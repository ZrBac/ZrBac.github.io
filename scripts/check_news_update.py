#!/usr/bin/env python3
"""Check the published news timestamp and dispatch a bounded recovery run."""
import argparse
import fcntl
import json
import os
import subprocess
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = 'ZrBac/news'
WORKFLOW = 'news.yml'
SITE_DATA = 'https://news.zacai.fun/data/news.json'
STALE_SECONDS = 2 * 3600
COOLDOWN_SECONDS = 2 * 3600
MAX_ATTEMPTS = 3  # Per rolling 24 hours while the published timestamp stays unchanged.


def timestamp(value):
    date = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if date.tzinfo is None:
        raise ValueError('Timestamp must include timezone')
    return date.timestamp()


def log(event, **fields):
    print(json.dumps({'at': datetime.now(timezone.utc).isoformat(),
                      'event': event, **fields}, ensure_ascii=False), flush=True)


def gh(*args):
    result = subprocess.run(['gh', *args], capture_output=True, text=True, timeout=45)
    if result.returncode:
        # Do not put credential helper output or arbitrary command stderr in logs.
        raise RuntimeError(f'GitHub command failed (exit {result.returncode})')
    return result.stdout


def read_published():
    req = urllib.request.Request(SITE_DATA + '?health=' + str(int(time.time())), headers={
        'User-Agent': 'ZrBacNewsWatchdog/1.0', 'Cache-Control': 'no-cache',
    })
    with urllib.request.urlopen(req, timeout=25) as response:
        data = response.read(15_000_001)
    if len(data) > 15_000_000:
        raise ValueError('Published data exceeds size limit')
    return json.loads(data)['updatedAt']


def save_state(path, state):
    temporary = path.with_suffix('.tmp')
    with temporary.open('w') as out:
        json.dump(state, out)
        out.flush()
        os.fsync(out.fileno())
    temporary.replace(path)


def check(path, dry_run=False, now=None):
    now = time.time() if now is None else now
    updated_at = read_published()
    updated = timestamp(updated_at)
    if updated > now + 600:
        raise ValueError('Published timestamp is in the future')
    state = json.loads(path.read_text()) if path.exists() else {}
    baseline = state.get('baselineUpdatedAt')
    # A successful new publication resets the retry budget; a stale CDN response cannot.
    if baseline is None or updated > timestamp(baseline):
        state = {'baselineUpdatedAt': updated_at, 'attempts': []}
    attempts = state['attempts']
    if not isinstance(attempts, list) or any(type(t) not in (int, float) for t in attempts):
        raise ValueError('Invalid retry state')
    state['attempts'] = attempts = [t for t in attempts if t > now - 86400]
    if not dry_run:
        save_state(path, state)
    age = now - updated
    if age <= STALE_SECONDS:
        log('fresh', updatedAt=updated_at, ageMinutes=round(age / 60))
        return 'fresh'
    if baseline and updated < timestamp(baseline):
        log('older_cached_response', updatedAt=updated_at)
        return 'older_cached_response'
    runs = json.loads(gh('run', 'list', '--repo', REPO, '--workflow', WORKFLOW,
                         '--limit', '50', '--json', 'databaseId,status,createdAt'))
    active = [run['databaseId'] for run in runs if run['status'] != 'completed']
    if active:
        log('run_active', runs=active, updatedAt=updated_at)
        return 'run_active'
    # Allow a just-started manual/scheduled run time to publish and propagate, even if
    # it already completed or failed. Avoid following somebody else's retry immediately.
    if any(now - timestamp(run['createdAt']) < COOLDOWN_SECONDS for run in runs):
        log('recent_run', updatedAt=updated_at)
        return 'recent_run'
    if attempts and now - max(attempts) < COOLDOWN_SECONDS:
        log('cooldown', attempts=len(attempts))
        return 'cooldown'
    if len(attempts) >= MAX_ATTEMPTS:
        log('retry_limit', attempts=len(attempts), updatedAt=updated_at)
        return 'retry_limit'
    if dry_run:
        log('would_dispatch', updatedAt=updated_at, ageMinutes=round(age / 60))
        return 'would_dispatch'
    # Persist before dispatch, so API errors/timeouts also consume the retry budget.
    state['attempts'].append(now)
    save_state(path, state)
    gh('workflow', 'run', WORKFLOW, '--repo', REPO, '--ref', 'hexo')
    log('dispatched', updatedAt=updated_at, attempts=len(state['attempts']))
    return 'dispatched'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--state-dir', type=Path, default=Path('/var/lib/zrbac-news-watchdog'))
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    args.state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (args.state_dir / 'check.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            log('already_checking')
            return
        try:
            check(args.state_dir / 'state.json', args.dry_run)
        except Exception as exc:
            log('check_failed', errorType=type(exc).__name__)
            raise SystemExit(1) from None


if __name__ == '__main__':
    main()
