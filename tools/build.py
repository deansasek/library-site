#!/usr/bin/env python3
"""Writes the static site. Run from the repository root: python3 tools/build.py

Shared head, nav, and footer markup lives here, so every page stays in sync.
The landing page (index.html) keeps its own body, but its nav and footer are
rewritten from the same templates. Output is plain static HTML and CSS.
"""
import datetime, html as H, json, os, re, sys, urllib.request
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.date.today()
YEAR = TODAY.year
REVIEWED_LABEL = TODAY.strftime('%B %d, %Y').replace(' 0', ' ')
REPO_API = 'https://api.github.com/repos/deansasek/library/releases/latest'
# Docs pages in reading order (the guide's order: start, features, then the reference pages).
PAGER_ORDER = [('/install/', 'Install'), ('/guide/', 'Guide'), ('/smart-features/', 'Smart features'),
               ('/privacy/', 'Privacy'), ('/development/', 'Development')]
SEARCH_PAGES = {'/guide/': 'Guide', '/privacy/': 'Privacy', '/install/': 'Install', '/development/': 'Development', '/smart-features/': 'Smart features'}
SITE_PATHS = ['/', '/guide/', '/privacy/', '/install/', '/development/', '/smart-features/', '/releases/', '/whats-new/', '/accessibility/']
REPO = 'https://github.com/deansasek/library'
CHEV_R = '<svg class="icon chevron" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="m9 6 6 6-6 6"/></svg>'
CHEV_L = '<svg class="icon chevron" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="m15 6-6 6 6 6"/></svg>'

# ----------------------------------------------------------------------
# shared chrome: nav, footer, and document head
# ----------------------------------------------------------------------

def header():
    return ('<header class="nav"><div class="nav-inner">'
            '<a class="nav-brand" href="/"><img src="/assets/icon.png" width="22" height="22" alt="">Library</a>'
            '<nav aria-label="Main">'
            '<a href="/guide/">Guide</a>'
            f'<a class="nav-extra" href="/privacy/">Privacy</a>'
            '<a href="/install/">Install</a>'
            '<a class="nav-extra" href="/accessibility/">Accessibility</a>'
            '<a class="nav-extra" href="/whats-new/">What\'s new</a>'
            '<a class="nav-extra" href="/releases/">Releases</a>'
            f'<a class="nav-extra" href="{REPO}" rel="noopener noreferrer">GitHub</a>'
            '</nav></div></header>')


def footer():
    return ('<footer><nav class="footer-cols" aria-label="Footer">'
            f'<div><p class="ft">Project</p><a href="{REPO}" rel="noopener noreferrer">GitHub</a><a href="/development/">Development</a>'
            '<a href="https://buymeacoffee.com/deansasek" rel="noopener noreferrer">Support</a>'
            '</div>'
            '<div><p class="ft">Guide</p><a href="/guide/">Feature guide</a><a href="/smart-features/">Smart features</a></div>'
            '<div><p class="ft">Privacy</p><a href="/privacy/">Privacy guide</a></div>'
            '<div><p class="ft">Releases</p><a href="/whats-new/">What\'s new</a></div>'
            f'</nav><p class="legal">Library is open source. &copy; {YEAR}. Library is available under the <a href="https://github.com/deansasek/library/blob/main/LICENSE" rel="noopener noreferrer">MIT License</a>.</p></footer>')


def head(title, desc, path):
    url = 'https://deansasek.github.io/library-site' + path
    t = title if 'Library' in title else f'{title} · Library'
    return f'''<!doctype html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://deansasek.github.io/library-site/assets/icon.png">
<meta property="og:image:alt" content="Library app icon">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="https://deansasek.github.io/library-site/assets/icon.png">
<link rel="icon" type="image/png" sizes="256x256" href="/assets/icon.png">
<link rel="apple-touch-icon" href="/assets/icon.png">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="stylesheet" href="/assets/styles.css">
<script src="/assets/script.js" defer></script>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
'''


RELATED = {
    '/guide/': [('/install/', 'Install'), ('/privacy/', 'Privacy'), ('/smart-features/', 'Smart features'), ('/guide/#troubleshooting', 'Troubleshooting')],
    '/privacy/': [('/guide/#settings', 'Settings'), ('/guide/', 'Guide'), ('/install/', 'Install')],
    '/install/': [('/guide/', 'Guide'), ('/development/', 'Development'), ('/releases/', 'Releases')],
    '/development/': [('/install/', 'Install'), ('/releases/', 'Releases'), ('/guide/', 'Guide')],
    '/smart-features/': [('/guide/#clipboard', 'Clipboard'), ('/guide/', 'Guide'), ('/privacy/', 'Privacy')],
    '/releases/': [('/install/', 'Install'), ('/guide/', 'Guide'), ('/development/', 'Development')],
}


# ----------------------------------------------------------------------
# page templates and related links
# ----------------------------------------------------------------------

def search_box(path):
    if path not in SEARCH_PAGES and not path.startswith('/guide/'):
        return ''
    return ('<div class="search" hidden><label class="visually-hidden" for="docs-search">Search the docs</label>'
            '<div class="search-field"><svg class="icon search-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
            '<circle cx="11" cy="11" r="6.5"/><path d="m16 16 4 4"/></svg>'
            '<input id="docs-search" type="search" placeholder="Search" autocomplete="off"></div>'
            '<div class="results" hidden></div></div>')


def page(path, title, desc, lede, toc, sections, plain=False, extra='', released=None, nav=None):
    toc_items = nav or '<ol>' + ''.join(f'<li><a href="#{i}">{l}</a></li>' for i, l in toc) + '</ol>'
    body = ''.join(f'<section id="{i}"><h2>{h}</h2>{html}</section>'
                   for i, h, html in sections)
    default = [('/whats-new/', "What's new"), ('/install/', 'Install'), ('/guide/', 'Guide')] if path.startswith('/whats-new/') else []
    if path.startswith('/guide/') and path != '/guide/':
        default = [('/guide/', 'Guide overview'), ('/install/', 'Install'), ('/privacy/', 'Privacy'), ('/smart-features/', 'Smart features')]
    rel_items = RELATED.get(path, default)
    related = ''.join(f'<li><a href="{h}">{l}</a></li>' for h, l in rel_items)
    back = f'<p class="back"><a href="/">{CHEV_L}Back to Library</a></p>'
    if plain:
        return (head(title, desc, path) + header() +
                f'<main id="main" class="doc">{back}<h1>{title}</h1><p class="lede">{lede}</p>{extra}</main>'
                + footer() + '\n</body>\n</html>\n')
    return (head(title, desc, path) + header() +
            f'<main id="main" class="doc">{back}<h1>{title}</h1><p class="lede">{lede}</p>'
            f'<p class="updated">' + (f'Released {released}. ' if released else 'Applies to the current release of Library. ') + f'Last reviewed {REVIEWED_LABEL}.</p>'
            f'<div class="article"><nav class="toc" aria-label="On this page"><p class="toc-title">On this page</p>{search_box(path)}{toc_items}</nav>'
            f'<div class="content">{body}'
            f'<section class="related"><h2>Related</h2><ul>{related}</ul></section>'
            '</div></div></main>'
            + footer() + '\n</body>\n</html>\n')


# ----------------------------------------------------------------------
# text transforms: minify, relative links, code bars
# ----------------------------------------------------------------------

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
        path, sep, frag = value.partition('#')
        # Clean folder URLs: the home link is the folder root and folder links keep their trailing slash.
        if path.endswith('index.html'):
            path = path[:-len('index.html')]
        target = base + path[1:]
        if target == '':
            target = './'
        return f'{attr}="{target}{sep}{frag}"'
    return re.sub(r'\b(href|src)="(/[^"]*)"', fix, html)


def code_bars(html):
    """Give each code block a header bar. The label is static text; script.js adds the Copy button to the bar."""
    return re.sub(r'<div class="code-block">\s*<pre>',
                  '<div class="code-block"><div class="code-head"><span class="code-label">Terminal</span></div><pre>', html)


# ----------------------------------------------------------------------
# build checks
# ----------------------------------------------------------------------

EMPTY_CHECKED = {'li', 'p', 'div', 'section', 'td', 'dd'}
MEDIA_TAGS = {'img', 'svg', 'picture', 'video', 'audio', 'canvas', 'iframe', 'input', 'textarea',
              'select', 'button', 'object', 'embed', 'hr'}


class EmptyCheck(HTMLParser):
    """Collects checked elements that hold no text and no media, and adjacent lists."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.problems = []

    def handle_starttag(self, tag, attrs):
        if tag in MEDIA_TAGS:
            for frame in self.stack:
                frame['media'] = True
            return
        self.stack.append({'tag': tag, 'attrs': dict(attrs), 'text': False, 'media': False, 'pos': self.getpos()})

    def handle_startendtag(self, tag, attrs):
        if tag in MEDIA_TAGS:
            for frame in self.stack:
                frame['media'] = True

    def handle_data(self, data):
        if data.replace('\u00a0', ' ').strip():
            for frame in self.stack:
                frame['text'] = True

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]['tag'] == tag:
                frame = self.stack.pop(i)
                if tag in EMPTY_CHECKED and not frame['text'] and not frame['media']:
                    # Intended exceptions: a spacer with a class, and a hidden container that a script fills later.
                    attrs = frame['attrs']
                    if 'spacer' not in attrs.get('class', '') and 'hidden' not in attrs:
                        self.problems.append('empty <%s> at line %d' % (tag, frame['pos'][0]))
                del self.stack[i:]
                return


def check_build_html(path, html):
    """Fail the build on empty list items, paragraphs, blocks, and table cells, and on back-to-back lists."""
    parser = EmptyCheck()
    parser.feed(html)
    parser.close()
    problems = list(parser.problems)
    for m in re.finditer(r'</(ul|ol)><(ul|ol)\b', html):
        problems.append('two lists in a row (merge them): ...' + html[max(0, m.start() - 40):m.end()] + '...')
    if problems:
        sys.exit('build check failed for %s:\n  %s' % (path, '\n  '.join(problems)))


# ----------------------------------------------------------------------
# file writers and generated files
# ----------------------------------------------------------------------

GUIDE_PATH_OF = {}  # guide section id -> its page, filled in by build_all


def point_guide_links(html):
    """Old links to a guide section, such as /guide/#clipboard, go to the group page that now holds it."""
    return re.sub(r'href="(?:/|\./)guide/#([a-z0-9-]+)"',
                  lambda m: f'href="{GUIDE_PATH_OF[m.group(1)]}#{m.group(1)}"' if m.group(1) in GUIDE_PATH_OF else m.group(0),
                  html)


def write(path, html):
    full = os.path.join(ROOT, path.lstrip('/'))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    out = code_bars(minify_html(relativize(point_guide_links(html), path)))
    check_build_html(path, out)
    with open(full, 'w') as f:
        f.write(out)


def update_landing():
    p = os.path.join(ROOT, 'index.html')
    s = open(p).read()
    s = re.sub(r'<header class="nav">.*?</header>', lambda m: header(), s, flags=re.S)
    s = re.sub(r'<footer>.*?</footer>', lambda m: footer(), s, flags=re.S)
    s = re.sub(r'\s*<meta name="color-scheme"[^>]*>', '', s)
    s = re.sub(r'\s*<meta property="og:site_name"[^>]*>', '', s)
    s = code_bars(minify_html(relativize(point_guide_links(s), '/index.html')))
    check_build_html('/index.html', s)
    open(p, 'w').write(s)


def guide_redirect(paths):
    """A small script for the guide index: a link with a section's anchor moves to that section's group page."""
    table = json.dumps(paths, separators=(',', ':'))
    return ('<script>(function(){var map=' + table + ';var id=location.hash.slice(1);'
            'if(id&&map[id]){location.replace(map[id]+"#"+id);}})();</script>')


def path_key(path):
    return path.replace('index.html', '')


def pager(path):
    """Previous and next links between the docs pages, in PAGER_ORDER."""
    keys = [k for k, _ in PAGER_ORDER]
    i = keys.index(path_key(path))
    parts = []
    if i > 0:
        parts.append(f'<a class="prev" href="{keys[i-1]}">Previous: {PAGER_ORDER[i-1][1]}</a>')
    if i < len(keys) - 1:
        parts.append(f'<a class="next" href="{keys[i+1]}">Next: {PAGER_ORDER[i+1][1]}</a>')
    return '<nav class="pager" aria-label="Previous and next pages">' + ''.join(parts) + '</nav>'


def write_search_index(rendered, guide_groups):
    """A small JSON index of each docs section's heading and first sentence, for script.js.

    Guide sections are labeled with their navigation group, such as "Find and open", not just "Guide".
    """
    items = []
    for path, page_html in rendered.items():
        pg = path.replace('index.html', '')
        if pg == '/guide/' or not (pg in SEARCH_PAGES or pg.startswith('/guide/')):
            continue
        for m in re.finditer(r'<section id="([^"]+)"><h2>([^<]*)</h2>(.*?)</section>', page_html, re.S):
            sid, title, body = m.groups()
            text = ' '.join(H.unescape(re.sub(r'<[^>]+>', ' ', body)).split())
            text = re.sub(r'\s+([.,;:!?])', r'\1', text)
            first = re.split(r'(?<=[.!?])\s', text)[0][:100]
            label = guide_groups[sid] if pg.startswith('/guide/') else SEARCH_PAGES[pg]
            items.append({'t': H.unescape(title), 'p': label,
                          'u': pg.strip('/') + '/index.html#' + sid, 's': first})
    data = json.dumps(items, ensure_ascii=False, separators=(',', ':'))
    with open(os.path.join(ROOT, 'assets', 'search-index.json'), 'w') as f:
        f.write(data)


# ----------------------------------------------------------------------
# release check and build entry point
# ----------------------------------------------------------------------

def check_release(reviewed):
    """Warn if the latest GitHub release is newer than the version the docs were reviewed against.

    Never fails the build: a network error or timeout only prints a note.
    """
    req = urllib.request.Request(REPO_API, headers={'User-Agent': 'library-site-build',
                                                    'Accept': 'application/vnd.github+json'})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            tag = json.load(r).get('tag_name', '')
    except Exception as e:  # network down, rate limited, or no release yet
        print(f'release check skipped: {e}')
        return
    if tag.lstrip('v') != reviewed:
        print(f'WARNING: latest release is {tag}, but the docs were last reviewed against {reviewed}. '
              'Review the docs, then set REVIEWED_VERSION in content/pages.py.')
    else:
        print(f'release check: the docs were reviewed against {reviewed}, the latest release.')


def build_all(check=False):
    global REVIEWED_LABEL
    import importlib.util
    spec = importlib.util.spec_from_file_location('pages', os.path.join(ROOT, 'content', 'pages.py'))
    pages = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pages)
    reviewed_on = pages.REVIEWED_DATE or TODAY
    REVIEWED_LABEL = reviewed_on.strftime('%B %d, %Y').replace(' 0', ' ')
    rendered = pages.render(page)
    GUIDE_PATH_OF.update(pages.GUIDE_PATH_OF)
    write_search_index(rendered, pages.GUIDE_GROUP_OF)
    for path, html in rendered.items():
        html = html.replace('__HEADER__', header()).replace('__FOOTER__', footer())
        if path == '/guide/index.html':
            # Old guide anchors, such as /guide/#clipboard-paste-queue, open the page that holds that section.
            html = html.replace('</body>', guide_redirect(pages.GUIDE_PATH_OF) + '</body>', 1)
        html = html.replace('</main>', pager(path) + '</main>', 1) if path_key(path) in dict(PAGER_ORDER) else html
        write(path, html)
    update_landing()
    css = open(os.path.join(ROOT, 'src', 'styles.css')).read()
    open(os.path.join(ROOT, 'assets', 'styles.css'), 'w').write(minify_css(css))
    js = open(os.path.join(ROOT, 'src', 'script.js')).read()
    js = '\n'.join(l.strip() for l in js.splitlines() if l.strip() and not l.strip().startswith('//'))
    open(os.path.join(ROOT, 'assets', 'script.js'), 'w').write(js + '\n')
    release_paths = sorted(k.replace('index.html', '') for k in rendered if k.startswith('/whats-new/') and k != '/whats-new/index.html')
    urls = ''.join(f'  <url>\n    <loc>https://deansasek.github.io/library-site{u}</loc>\n    <lastmod>{TODAY.isoformat()}</lastmod>\n  </url>\n'
                   for u in SITE_PATHS + sorted(set(pages.GUIDE_PATH_OF.values())) + release_paths)
    open(os.path.join(ROOT, 'sitemap.xml'), 'w').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '</urlset>\n')
    if check:
        check_release(pages.REVIEWED_VERSION)


if __name__ == '__main__':
    build_all(check='--check-release' in sys.argv)
    print('built')

