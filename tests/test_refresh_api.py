import importlib.util
import json
import sys
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import news_refresh_api as api


class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.controller = api.RefreshController(root, root / 'check.lock')
        self.now = api.timestamp('2026-09-24T06:00:00Z')
        patch.object(api.time, 'time', return_value=self.now).start()
        self.gh = patch.object(api, 'gh', return_value='[]').start()
        self.published = patch.object(api, 'read_published', return_value='2026-09-24T05:00:00Z').start()
        self.addCleanup(patch.stopall)

    def test_dispatch_is_fixed_and_repeated_clicks_are_limited(self):
        self.gh.side_effect = ['[]', 'https://github.com/ZrBac/news/actions/runs/123']
        self.assertEqual(self.controller.trigger()['status'], 'running')
        self.gh.assert_called_with('workflow', 'run', 'news.yml', '--repo', 'ZrBac/news', '--ref', 'hexo')
        self.gh.side_effect = None
        # Restart the controller: the budget must survive a process restart.
        self.controller = api.RefreshController(self.controller.directory, self.controller.lockfile)
        self.assertEqual(self.controller.trigger()['status'], 'cooldown')

    def test_active_and_recent_workflows_are_not_duplicated(self):
        for status in ('queued', 'in_progress', 'waiting'):
            self.controller.cached_runs = None
            self.gh.return_value = json.dumps([{'databaseId': 2, 'status': status, 'createdAt': '2026-09-24T05:00:00Z'}])
            self.assertEqual(self.controller.trigger()['status'], 'running')
        self.controller.cached_runs = None
        self.gh.return_value = json.dumps([{'databaseId': 2, 'status': 'completed', 'createdAt': '2026-09-24T05:55:00Z'}])
        self.assertEqual(self.controller.trigger()['status'], 'cooldown')
        self.published.assert_not_called()

    def test_fresh_publication_skips_dispatch(self):
        self.published.return_value = '2026-09-24T05:55:00Z'
        self.assertEqual(self.controller.trigger()['status'], 'fresh')
        self.assertEqual(self.gh.call_count, 1)

    def test_dispatch_timeout_still_consumes_cooldown(self):
        self.gh.side_effect = ['[]', TimeoutError()]
        with self.assertRaises(TimeoutError):
            self.controller.trigger()
        self.gh.side_effect = None
        self.assertEqual(self.controller.trigger()['status'], 'cooldown')

    def test_status_and_status_cache_never_dispatch(self):
        self.assertEqual(self.controller.status()['status'], 'idle')
        self.assertEqual(self.controller.status()['status'], 'idle')
        self.assertEqual(self.gh.call_count, 1)
        api.save_state(self.controller.directory / 'request.json', {'requestedAt': self.now - 30, 'runId': 3})
        self.controller.cached_runs = [{'databaseId': 3, 'status': 'completed', 'conclusion': 'failure', 'createdAt': '2026-09-24T05:59:30Z'}]
        self.assertEqual(self.controller.status()['status'], 'failed')
        self.controller.cached_runs[0]['conclusion'] = 'success'
        self.assertEqual(self.controller.status()['status'], 'ready')


class HttpTests(unittest.TestCase):
    def test_cors_and_fixed_request_shape(self):
        with patch.object(api.controller, 'trigger', return_value={'status': 'fresh'}) as trigger:
            server = api.ThreadingHTTPServer(('127.0.0.1', 0), api.Handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                def request(origin, body=b'{}', header=True, method='POST'):
                    headers = {'Origin': origin}
                    if header:
                        headers['X-News-Refresh'] = '1'
                    req = urllib.request.Request(f'http://127.0.0.1:{server.server_port}/api/news-refresh',
                          data=body if method == 'POST' else None, headers=headers, method=method)
                    try:
                        return urllib.request.urlopen(req)
                    except urllib.error.HTTPError as response:
                        return response
                for origin in ('https://evil.example', 'null'):
                    with request(origin) as r:
                        self.assertEqual(r.status, 403)
                with request('https://news.zacai.fun', header=False) as r:
                    self.assertEqual(r.status, 403)
                with request('https://news.zacai.fun', b'{"repo":"other"}') as r:
                    self.assertEqual(r.status, 400)
                trigger.assert_not_called()
                with request('https://news.zacai.fun', method='OPTIONS') as r:
                    self.assertEqual(r.status, 200)
                    self.assertEqual(r.headers['Access-Control-Allow-Origin'], 'https://news.zacai.fun')
                with request('https://news.zacai.fun') as r:
                    self.assertEqual(json.load(r)['status'], 'fresh')
                trigger.assert_called_once_with()
            finally:
                server.shutdown()
                server.server_close()
                thread.join()
