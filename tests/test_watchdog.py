import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('watchdog', Path(__file__).resolve().parents[1] / 'scripts/check_news_update.py')
watchdog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watchdog)


class WatchdogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'state.json'
        self.now = watchdog.timestamp('2026-09-23T14:00:00Z')
        self.published = patch.object(watchdog, 'read_published', return_value='2026-09-23T09:00:00Z').start()
        self.gh = patch.object(watchdog, 'gh', return_value='[]').start()
        patch.object(watchdog, 'log').start()
        self.addCleanup(patch.stopall)

    def check(self, **kwargs):
        return watchdog.check(self.path, now=self.now, **kwargs)

    def test_fresh_data_never_calls_github(self):
        self.published.return_value = '2026-09-23T12:00:00Z'
        self.assertEqual(self.check(), 'fresh')
        self.gh.assert_not_called()

    def test_overdue_dispatch_and_restart_cooldown(self):
        self.assertEqual(self.check(), 'dispatched')
        self.gh.assert_called_with('workflow', 'run', 'news.yml', '--repo', watchdog.REPO, '--ref', 'hexo')
        self.gh.reset_mock()
        self.assertEqual(self.check(), 'cooldown')
        self.assertEqual(self.gh.call_count, 1)  # List only; never dispatch twice.

    def test_active_and_recent_runs_are_not_duplicated(self):
        for status in ['queued', 'in_progress', 'waiting', 'requested']:
            self.gh.return_value = json.dumps([{'databaseId': 1, 'status': status, 'createdAt': '2026-09-23T09:00:00Z'}])
            self.assertEqual(self.check(), 'run_active')
        self.gh.return_value = json.dumps([{'databaseId': 1, 'status': 'completed', 'createdAt': '2026-09-23T13:55:00Z'}])
        self.assertEqual(self.check(), 'recent_run')

    def test_dispatch_failure_consumes_retry_budget(self):
        self.gh.side_effect = ['[]', RuntimeError('API unavailable')]
        with self.assertRaises(RuntimeError):
            self.check()
        self.gh.side_effect = None
        self.assertEqual(self.check(), 'cooldown')
        self.assertEqual(len(json.loads(self.path.read_text())['attempts']), 1)

    def test_daily_limit_expires_and_success_resets_budget(self):
        state = {'baselineUpdatedAt': '2026-09-23T09:00:00Z',
                 'attempts': [self.now - n * 3600 for n in [8, 5, 3]]}
        self.path.write_text(json.dumps(state))
        self.assertEqual(self.check(), 'retry_limit')
        self.published.return_value = '2026-09-23T13:30:00Z'
        self.assertEqual(self.check(), 'fresh')
        self.assertEqual(json.loads(self.path.read_text())['attempts'], [])
        state['attempts'] = [self.now - 25 * 3600]
        self.path.write_text(json.dumps(state))
        self.published.return_value = state['baselineUpdatedAt']
        self.assertEqual(self.check(), 'dispatched')

    def test_fetch_and_github_errors_do_not_dispatch(self):
        self.published.side_effect = OSError('DNS unavailable')
        with self.assertRaises(OSError):
            self.check()
        self.gh.assert_not_called()
        self.published.side_effect = None
        self.gh.side_effect = RuntimeError('API unavailable')
        with self.assertRaises(RuntimeError):
            self.check()
        self.assertEqual(json.loads(self.path.read_text())['attempts'], [])

    def test_dry_run_does_not_write_retry_state_or_dispatch(self):
        self.assertEqual(self.check(dry_run=True), 'would_dispatch')
        self.assertFalse(self.path.exists())
        self.assertEqual(self.gh.call_count, 1)

    def test_bad_timestamp_or_state_fails_closed(self):
        for value in ['not-a-date', '2026-09-23T09:00:00', '2026-09-24T09:00:00Z']:
            self.published.return_value = value
            with self.assertRaises(ValueError):
                self.check()
        self.published.return_value = '2026-09-23T09:00:00Z'
        self.path.write_text('broken')
        with self.assertRaises(ValueError):
            self.check()
        self.gh.assert_not_called()

    def test_older_cdn_response_does_not_reset_budget(self):
        self.path.write_text(json.dumps({'baselineUpdatedAt': '2026-09-23T10:00:00Z', 'attempts': [self.now - 60]}))
        self.assertEqual(self.check(), 'older_cached_response')
        self.gh.assert_not_called()
        self.assertEqual(len(json.loads(self.path.read_text())['attempts']), 1)


if __name__ == '__main__':
    unittest.main()
