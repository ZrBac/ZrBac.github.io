#!/usr/bin/env python3
"""A rate-limited public trigger for one fixed news publishing workflow."""
import fcntl
import json
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from check_news_update import gh, read_published, timestamp, save_state, REPO, WORKFLOW

ALLOWED_ORIGINS = {'https://news.zacai.fun', 'http://news.zacai.fun'}
INTERVAL = 15 * 60


class RefreshController:
    def __init__(self, directory=Path('/var/lib/zrbac-news-refresh'),
                 lockfile=Path('/var/lib/zrbac-news-watchdog/check.lock')):
        self.directory = directory
        self.lockfile = lockfile
        self.lock = threading.Lock()
        self.cached_runs = None
        self.runs_checked = 0

    def runs(self):
        if self.cached_runs is None or time.time() - self.runs_checked > 10:
            self.cached_runs = json.loads(gh('run', 'list', '--repo', REPO,
                '--workflow', WORKFLOW, '--limit', '20', '--json',
                'databaseId,status,conclusion,createdAt'))
            self.runs_checked = time.time()
        return self.cached_runs

    def state(self):
        path = self.directory / 'request.json'
        return json.loads(path.read_text()) if path.exists() else {}

    def status(self):
        with self.lock:
            state = self.state()
            runs = self.runs()
            active = next((r for r in runs if r['status'] != 'completed'), None)
            if active:
                return {'status': 'running', 'runId': active['databaseId'],
                        'baselineAt': state.get('baselineAt')}
            if not state:
                return {'status': 'idle'}
            run = next((r for r in runs if r['databaseId'] == state.get('runId') or
                        timestamp(r['createdAt']) >= state['requestedAt'] - 5), None)
            if run:
                return {'status': 'ready' if run['conclusion'] == 'success' else 'failed',
                        'baselineAt': state.get('baselineAt'), 'runId': run['databaseId']}
            return {'status': 'running' if time.time() - state['requestedAt'] < 120 else 'failed',
                    'baselineAt': state.get('baselineAt')}

    def trigger(self):
        with self.lock:
            self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
            # Share the watchdog's local lock; never race its dispatch operation.
            with self.lockfile.open('a') as lock:
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    return {'status': 'busy', 'retryAfter': 30}
                now = time.time()
                runs = self.runs()
                active = next((r for r in runs if r['status'] != 'completed'), None)
                if active:
                    return {'status': 'running', 'runId': active['databaseId']}
                state = self.state()
                recent = max([state.get('requestedAt', 0)] +
                             [timestamp(r['createdAt']) for r in runs])
                if now - recent < INTERVAL:
                    return {'status': 'cooldown', 'retryAfter': int(INTERVAL - (now - recent)) + 1}
                updated_at = read_published()
                if now - timestamp(updated_at) < INTERVAL:
                    return {'status': 'fresh', 'updatedAt': updated_at}
                state = {'requestedAt': now, 'baselineAt': updated_at}
                # Dispatch errors/timeouts consume the cooldown, even across restarts.
                path = self.directory / 'request.json'
                save_state(path, state)
                output = gh('workflow', 'run', WORKFLOW, '--repo', REPO, '--ref', 'hexo')
                match = re.search(r'/actions/runs/(\d+)', output)
                if match:
                    state['runId'] = int(match.group(1))
                    save_state(path, state)
                self.cached_runs = None
                return {'status': 'running', 'baselineAt': updated_at,
                        'runId': state.get('runId')}


controller = RefreshController()


class Handler(BaseHTTPRequestHandler):
    def reply(self, code, body):
        payload = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        origin = self.headers.get('Origin')
        if origin in ALLOWED_ORIGINS:
            self.send_header('Access-Control-Allow-Origin', origin)
        self.send_header('Vary', 'Origin')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-News-Refresh, Content-Type')
        self.send_header('Access-Control-Max-Age', '600')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def handle_api(self):
        path = urlsplit(self.path).path
        if path not in ('/api/news-refresh', '/api/news-refresh/status'):
            return self.reply(404, {'status': 'not_found'})
        if self.headers.get('Origin') not in ALLOWED_ORIGINS:
            return self.reply(403, {'status': 'forbidden'})
        if self.command == 'OPTIONS':
            return self.reply(200, {'status': 'ok'})
        try:
            if self.command == 'POST' and path == '/api/news-refresh':
                if self.headers.get('X-News-Refresh') != '1':
                    return self.reply(403, {'status': 'forbidden'})
                length = int(self.headers.get('Content-Length', '0'))
                if length < 0 or length > 128:
                    return self.reply(413, {'status': 'invalid_request'})
                if self.rfile.read(length).strip() not in (b'', b'{}'):
                    return self.reply(400, {'status': 'invalid_request'})
                return self.reply(200, controller.trigger())
            if self.command == 'GET' and path == '/api/news-refresh/status':
                return self.reply(200, controller.status())
            return self.reply(405, {'status': 'method_not_allowed'})
        except Exception as exc:
            print(json.dumps({'event': 'refresh_api_failed', 'errorType': type(exc).__name__}), flush=True)
            return self.reply(503, {'status': 'unavailable'})

    do_GET = handle_api
    do_POST = handle_api
    do_OPTIONS = handle_api


if __name__ == '__main__':
    ThreadingHTTPServer(('127.0.0.1', 8001), Handler).serve_forever()
