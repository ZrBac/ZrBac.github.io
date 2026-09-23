#!/usr/bin/env python3
"""Overlay the news portal on the original published blog without rebuilding old Hexo."""
import argparse
import json
import shutil
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--legacy', type=Path, required=True)
    p.add_argument('--output', type=Path, default=ROOT / '_site')
    args = p.parse_args()
    legacy = args.legacy.resolve()
    output = args.output.resolve()
    if not (legacy / 'index.html').is_file():
        raise SystemExit('Published blog snapshot missing. Refusing to drop the existing blog.')
    if output == ROOT or output == legacy or output in legacy.parents or output in ROOT.parents:
        raise SystemExit('Unsafe output directory')
    if output.exists():
        shutil.rmtree(output)
    shutil.copytree(legacy, output, ignore=shutil.ignore_patterns('.git', '.github', 'CNAME'))
    # Original article URLs and assets stay in place; move only the old home page.
    (output / 'blog').mkdir(exist_ok=True)
    shutil.copy2(output / 'index.html', output / 'blog/index.html')
    for page in output.rglob('*.html'):
        text = page.read_text(errors='replace')
        text = text.replace('href="/"', 'href="/blog/"')
        text = text.replace('http://yoursite.com', 'https://zrbac.github.io')
        page.write_text(text)
    for filename in ('atom.xml', 'sitemap.xml'):
        path = output / filename
        if path.exists():
            path.write_text(path.read_text().replace('http://yoursite.com', 'https://zrbac.github.io'))
    shutil.copy2(ROOT / 'news/index.html', output / 'index.html')
    shutil.copytree(ROOT / 'news/assets', output / 'assets/news', dirs_exist_ok=True)
    shutil.copytree(ROOT / 'news/data', output / 'data', dirs_exist_ok=True)
    (output / '.nojekyll').touch()
    data = json.loads((output / 'data/news.json').read_text())
    items = ''.join(f'<item><title>{escape(a["title"])}</title><link>{escape(a["url"])}</link><guid>{escape(a["url"])}</guid><pubDate>{format_datetime(datetime.fromisoformat(a["publishedAt"].replace("Z", "+00:00")))}</pubDate><description>{escape(a["excerpt"])}</description></item>' for a in data['articles'][:50])
    (output / 'news.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>今日知闻 · ZrBac</title><link>https://zrbac.github.io/</link><description>综合热点与 AI 科技资讯。摘要来自原始资讯源。</description>' + items + '</channel></rss>')
    # A compact sitemap of the portal and preserved article URLs.
    urls = ['https://zrbac.github.io/', 'https://zrbac.github.io/blog/']
    urls += ['https://zrbac.github.io/' + str(f.relative_to(output).parent) + '/' for f in output.glob('20*/**/index.html')]
    (output / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{escape(u)}</loc></url>' for u in urls) + '</urlset>')
    (output / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://zrbac.github.io/sitemap.xml\n')
    print(f'Built {output}; {len(data["articles"])} news items; original blog preserved at /blog/.')


if __name__ == '__main__':
    main()
