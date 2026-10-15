#!/usr/bin/env python3
"""Writes the static site. Run: python3 build.py

Shared head, nav, and footer markup lives here, so every page stays in sync.
The landing page (index.html) keeps its own body, but its nav and footer are
rewritten from the same templates. Output is plain static HTML and CSS.
"""
import os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = 'https://github.com/deansasek/library'
CHEV_R = '<svg class="icon chevron" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="m9 6 6 6-6 6"/></svg>'
CHEV_L = '<svg class="icon chevron" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="m15 6-6 6 6 6"/></svg>'


def header():
    return ('<header class="nav"><div class="nav-inner">'
            '<a class="nav-brand" href="/"><img src="/assets/icon.png" width="22" height="22" alt="">Library</a>'
            '<nav aria-label="Main">'
            '<a href="/guide/">Guide</a>'
            f'<a class="nav-extra" href="/privacy/">Privacy</a>'
            '<a href="/install/">Install</a>'
            '<a class="nav-extra" href="/releases/">Releases</a>'
            f'<a class="nav-extra" href="{REPO}" rel="noopener noreferrer">GitHub</a>'
            '</nav></div></header>')


def footer():
    return ('<footer><nav class="footer-cols" aria-label="Footer">'
            '<div><p class="ft">Project</p>'
            f'<a href="{REPO}" rel="noopener noreferrer">GitHub</a><a href="/install/">Install</a></div>'
            '<div><p class="ft">Guide</p>'
            '<a href="/guide/">Feature guide</a><a href="/smart-features/">Smart features</a></div>'
            '<div><p class="ft">Privacy</p><a href="/privacy/">Privacy</a></div>'
            '<div><p class="ft">Releases</p>'
            f'<a href="/releases/">Latest version</a><a href="{REPO}/releases" rel="noopener noreferrer">All releases</a></div>'
            '</nav><p class="legal">Library is open source. &copy; 2026</p></footer>')


def head(title, desc, path):
    url = 'https://getlibrary.app' + path
    t = 'Library' if title == 'Library' else f'{title} · Library'
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://getlibrary.app/assets/icon.png">
<meta name="twitter:card" content="summary">
<link rel="icon" type="image/png" sizes="256x256" href="/assets/icon.png">
<link rel="apple-touch-icon" href="/assets/icon.png">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="stylesheet" href="/styles.css">
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
'''


RELATED = {
    '/guide/': [('/install/', 'Install'), ('/privacy/', 'Privacy'), ('/smart-features/', 'Smart features')],
    '/privacy/': [('/guide/#settings', 'Settings'), ('/guide/', 'Guide'), ('/install/', 'Install')],
    '/install/': [('/guide/', 'Guide'), ('/development/', 'Development'), ('/releases/', 'Releases')],
    '/development/': [('/install/', 'Install'), ('/releases/', 'Releases'), ('/guide/', 'Guide')],
    '/smart-features/': [('/guide/#keep-what-you-copy', 'Keep what you copy'), ('/guide/', 'Guide'), ('/privacy/', 'Privacy')],
    '/releases/': [('/install/', 'Install'), ('/guide/', 'Guide'), ('/development/', 'Development')],
}
RELEASE = ('October 14, 2026', 'v1.5.0')


def page(path, title, desc, lede, toc, sections):
    toc_items = ''.join(f'<li><a href="#{i}">{l}</a></li>' for i, l in toc)
    body = ''.join(f'<section id="{i}"><h2>{h}</h2>{html}</section>'
                   for i, h, html in sections)
    related = ''.join(f'<li><a href="{h}">{l}</a></li>' for h, l in RELATED.get(path, []))
    back = f'<p class="back"><a href="/">{CHEV_L}Back to Library</a></p>'
    date, version = RELEASE
    return (head(title, desc, path) + header() +
            f'<main id="main" class="doc">{back}<h1>{title}</h1><p class="lede">{lede}</p>'
            f'<p class="updated">Last updated {date} for Library {version}.</p>'
            f'<div class="article"><nav class="toc" aria-label="On this page"><p class="toc-title">On this page</p><ol>{toc_items}</ol></nav>'
            f'<div class="content">{body}'
            f'<section class="related"><h2>Related</h2><ul>{related}</ul></section>'
            '</div></div></main>'
            + footer() + '\n</body>\n</html>\n')


def minify_html(s):
    pre = []
    s = re.sub(r'<pre>.*?</pre>', lambda m: (pre.append(m.group(0)), f'\x00PRE{len(pre)-1}\x00')[1], s, flags=re.S)
    s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
    s = re.sub(r'\n\s*', '\n', s)
    s = re.sub(r'>\s*\n\s*<', '><', s)
    s = re.sub(r'\n{2,}', '\n', s)
    s = s.strip() + '\n'
    for i, p in enumerate(pre):
        s = s.replace(f'\x00PRE{i}\x00', p)
    return s


def minify_css(s):
    s = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
    s = re.sub(r'\s*\n\s*', '', s)
    s = re.sub(r'\s*([{};,>])\s*', r'\1', s)
    s = re.sub(r':\s+', ':', s)
    return s.strip() + '\n'


def relativize(html, path):
    """Make local href/src relative to the page's folder, so the site also works from disk (file://).

    path is the page's URL path, such as '/guide/index.html' or '/404.html'. Absolute https URLs and
    fragments (#...) are left as they are.
    """
    depth = path.strip('/').count('/')
    base = '../' * depth

    def fix(m):
        attr, value = m.group(1), m.group(2)
        if value.startswith('//'):
            return m.group(0)
        if value == '/':
            return f'{attr}="{base or "./"}"'
        return f'{attr}="{base}{value[1:]}"'
    return re.sub(r'\b(href|src)="(/[^"]*)"', fix, html)


def write(path, html):
    full = os.path.join(ROOT, path.lstrip('/'))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w') as f:
        f.write(minify_html(relativize(html, path)))


def update_landing():
    p = os.path.join(ROOT, 'index.html')
    s = open(p).read()
    s = re.sub(r'<header class="nav">.*?</header>', lambda m: header(), s, flags=re.S)
    s = re.sub(r'<footer>.*?</footer>', lambda m: footer(), s, flags=re.S)
    s = re.sub(r'\s*<meta name="color-scheme"[^>]*>', '', s)
    s = re.sub(r'\s*<meta property="og:site_name"[^>]*>', '', s)
    s = re.sub(r'\s*<meta property="og:image:(?:width|height|alt)"[^>]*>', '', s)
    s = re.sub(r'\s*<meta name="twitter:(?:title|description|image)"[^>]*>', '', s)
    s = minify_html(relativize(s, '/index.html'))
    open(p, 'w').write(s)


def build_all():
    import importlib.util
    spec = importlib.util.spec_from_file_location('pages', os.path.join(ROOT, 'content', 'pages.py'))
    pages = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pages)
    for path, html in pages.render(page).items():
        html = html.replace('__HEADER__', header()).replace('__FOOTER__', footer())
        write(path, html)
    update_landing()
    css = open(os.path.join(ROOT, 'styles.css')).read()
    open(os.path.join(ROOT, 'styles.css'), 'w').write(minify_css(css))


if __name__ == '__main__':
    build_all()
    print('built')
