#!/usr/bin/env python3
"""Overlay the news portal on the original published blog without rebuilding old Hexo."""
import argparse
import hashlib
import json
import os
import shutil
from html import escape as html_escape
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import urlsplit
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--legacy', type=Path, required=True)
    p.add_argument('--output', type=Path, default=ROOT / '_site')
    args = p.parse_args()
    refresh_endpoint = os.environ.get('NEWS_REFRESH_ENDPOINT', '').strip() or 'https://zacai.fun/api/news-refresh'
    endpoint = urlsplit(refresh_endpoint)
    if (endpoint.scheme != 'https' or not endpoint.hostname or endpoint.username or endpoint.password
            or endpoint.query or endpoint.fragment or endpoint.path != '/api/news-refresh'):
        raise SystemExit('NEWS_REFRESH_ENDPOINT must be an HTTPS /api/news-refresh URL without credentials or query parameters')
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
        text = text.replace('http://yoursite.com', 'https://news.zacai.fun')
        page.write_text(text)
    for filename in ('atom.xml', 'sitemap.xml'):
        path = output / filename
        if path.exists():
            path.write_text(path.read_text().replace('http://yoursite.com', 'https://news.zacai.fun'))
    shutil.copy2(ROOT / 'news/index.html', output / 'index.html')
    shutil.copytree(ROOT / 'news/assets', output / 'assets/news', dirs_exist_ok=True)
    # New HTML always requests the matching assets, even with cached older releases.
    homepage = (output / 'index.html').read_text()
    homepage = homepage.replace('content="https://zacai.fun/api/news-refresh"',
                                f'content="{html_escape(refresh_endpoint, quote=True)}"')
    shell_files = ['/', '/manifest.webmanifest', '/assets/news/icon-180.png',
                   '/assets/news/icon-192.png', '/assets/news/icon-512.png']
    for filename in ('app.js', 'pwa.js', 'style.css', 'favicon.svg'):
        asset = output / 'assets/news' / filename
        digest = hashlib.sha256(asset.read_bytes()).hexdigest()[:12]
        versioned = asset.with_name(f'{asset.stem}.{digest}{asset.suffix}')
        shutil.copy2(asset, versioned)
        homepage = homepage.replace(f'"/assets/news/{filename}"', f'"/assets/news/{versioned.name}"')
        shell_files.append(f'/assets/news/{versioned.name}')
    (output / 'index.html').write_text(homepage)
    shutil.copy2(ROOT / 'news/manifest.webmanifest', output / 'manifest.webmanifest')
    worker = (ROOT / 'news/sw.js').read_text()
    shell_digest = hashlib.sha256(homepage.encode() + worker.encode())
    for path in shell_files[1:]:
        shell_digest.update((output / path.lstrip('/')).read_bytes())
    worker = worker.replace('__BUILD_ID__', shell_digest.hexdigest()[:16])
    worker = worker.replace('__SHELL_FILES__', json.dumps(shell_files))
    (output / 'sw.js').write_text(worker)
    shutil.copytree(ROOT / 'news/data', output / 'data', dirs_exist_ok=True)
    (output / '.nojekyll').touch()
    data = json.loads((output / 'data/news.json').read_text())
    # A tiny health file avoids downloading and parsing the entire archive in Workers.
    updated_at = data['updatedAt']
    if datetime.fromisoformat(updated_at.replace('Z', '+00:00')).tzinfo is None:
        raise SystemExit('News timestamp must include a timezone')
    (output / 'data/status.json').write_text(json.dumps({'updatedAt': updated_at}) + '\n')
    items = ''.join(f'<item><title>{escape(a["title"])}</title><link>{escape(a["url"])}</link><guid>{escape(a["url"])}</guid><pubDate>{format_datetime(datetime.fromisoformat(a["publishedAt"].replace("Z", "+00:00")))}</pubDate><description>{escape(a["excerpt"])}</description></item>' for a in data['articles'][:50])
    (output / 'news.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>资讯</title><link>https://news.zacai.fun/</link><description>综合热点与 AI 科技资讯。摘要来自原始资讯源。</description>' + items + '</channel></rss>')
    # A compact sitemap of the portal and preserved article URLs.
    urls = ['https://news.zacai.fun/', 'https://news.zacai.fun/blog/']
    urls += ['https://news.zacai.fun/' + str(f.relative_to(output).parent) + '/' for f in output.glob('20*/**/index.html')]
    (output / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{escape(u)}</loc></url>' for u in urls) + '</urlset>')
    (output / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://news.zacai.fun/sitemap.xml\n')
    print(f'Built {output}; {len(data["articles"])} news items; original blog preserved at /blog/.')


if __name__ == '__main__':
    main()
