import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('collector', ROOT / 'scripts/collect_news.py')
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class FeedTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 9, 23, 4, tzinfo=timezone.utc)
        self.source = {'id': 'example', 'category': 'tech'}

    def feed(self, link='https://example.com/story?utm_source=rss', date='Wed, 23 Sep 2026 03:00:00 GMT'):
        return f'''<rss><channel><item><title><![CDATA[AI &amp; 科技 <script>alert(1)</script>]]></title>
          <link>{link}</link><pubDate>{date}</pubDate>
          <description><![CDATA[<p>正文摘要</p><script>bad()</script><img src="x" onerror="bad()"/>]]></description>
          </item></channel></rss>'''.encode()

    def test_feed_has_clean_text_and_canonical_link(self):
        items = collector.parse_feed(self.feed(), self.source, self.now)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['title'], 'AI & 科技')
        self.assertEqual(items[0]['excerpt'], '正文摘要')
        self.assertEqual(items[0]['url'], 'https://example.com/story')
        self.assertEqual(items[0]['category'], 'ai')

    def test_rejects_unsafe_links_undated_old_and_future_articles(self):
        self.assertFalse(collector.parse_feed(self.feed(link='javascript:alert(1)'), self.source, self.now))
        for date in ['', 'Wed, 23 Sep 2026 03:00:00', 'Wed, 23 Sep 2020 03:00:00 GMT', 'Wed, 30 Sep 2026 03:00:00 GMT']:
            self.assertFalse(collector.parse_feed(self.feed(date=date), self.source, self.now))

    def test_failed_source_history_is_retained_and_duplicate_is_replaced(self):
        old = collector.parse_feed(self.feed(), self.source, self.now)[0]
        revised = dict(old, title='AI 更新后的标题')
        retained = collector.merge_articles([old], [], self.now, {'example'})
        self.assertEqual(retained, [old])
        merged = collector.merge_articles([old], [revised], self.now, {'example'})
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]['title'], revised['title'])
        self.assertFalse(collector.merge_articles([old], [], self.now + timedelta(days=31), {'example'}))

    def test_limit_excerpt_and_keep_source_provenance(self):
        feed = self.feed().replace('正文摘要'.encode(), ('很长的内容' * 100).encode())
        item = collector.parse_feed(feed, self.source, self.now)[0]
        self.assertLessEqual(len(item['excerpt']), 90)
        self.assertEqual(item['sourceId'], 'example')

    def test_stable_id_and_unique_titles(self):
        item = collector.parse_feed(self.feed(), self.source, self.now)[0]
        same_title = dict(item, url='https://example.com/duplicate')
        self.assertEqual(len(collector.merge_articles([item], [same_title], self.now, {'example'})), 1)
        self.assertIsNone(collector.safe_url('https://user:password@example.com/'))


class ArchiveTests(unittest.TestCase):
    def test_build_preserves_blog_article_urls_and_assets(self):
        data = ROOT / 'news/data/news.json'
        existed = data.exists()
        original = data.read_bytes() if existed else None
        try:
            data.parent.mkdir(parents=True, exist_ok=True)
            data.write_text(json.dumps({'articles': []}))
            with tempfile.TemporaryDirectory() as tmp:
                legacy = Path(tmp) / 'old'
                legacy.mkdir()
                (legacy / 'index.html').write_text('<a href="/">Blog</a>')
                article = legacy / '2020/story'
                article.mkdir(parents=True)
                (article / 'index.html').write_text('<a href="/">首页</a><p>原文保留</p>')
                (legacy / 'asset.css').write_text('body{}')
                (legacy / 'CNAME').write_text('obsolete.example.com')
                output = Path(tmp) / 'out'
                subprocess.run([sys.executable, str(ROOT / 'scripts/build_news.py'), '--legacy', str(legacy), '--output', str(output)], check=True, capture_output=True)
                self.assertIn('id="news-content"', (output / 'index.html').read_text())
                self.assertIn('Blog', (output / 'blog/index.html').read_text())
                self.assertIn('href="/blog/"', (output / '2020/story/index.html').read_text())
                self.assertIn('原文保留', (output / '2020/story/index.html').read_text())
                self.assertTrue((output / 'asset.css').exists())
                self.assertFalse((output / 'CNAME').exists())
                # The document must not load an unversioned cached script or stylesheet.
                homepage = (output / 'index.html').read_text()
                for name, extension in [('app', 'js'), ('style', 'css'), ('favicon', 'svg')]:
                    match = re.search(r'/assets/news/' + name + r'\.[0-9a-f]{12}\.' + extension, homepage)
                    self.assertIsNotNone(match)
                    self.assertEqual((output / match.group(0).lstrip('/')).read_bytes(), (ROOT / 'news/assets' / f'{name}.{extension}').read_bytes())
        finally:
            if existed:
                data.write_bytes(original)
            elif data.exists():
                data.unlink()


if __name__ == '__main__':
    unittest.main()
