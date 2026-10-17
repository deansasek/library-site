#!/usr/bin/env python3
"""Writes the static site. Run from the repository root: python3 tools/build.py

Shared head, nav, and footer markup lives here, so every page stays in sync.
The landing page (index.html) keeps its own body, but its nav and footer are
rewritten from the same templates. Output is plain static HTML and CSS.
"""
import datetime, hashlib, html as H, json, os, re, sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.date.today()
YEAR = TODAY.year
REVIEWED_LABEL = TODAY.strftime('%B %d, %Y').replace(' 0', ' ')
# Docs pages in reading order (the guide's order: start, features, then the reference pages).
PAGER_ORDER = [('/install/', 'Install'), ('/guide/', 'Guide'), ('/smart-features/', 'Smart features'),
               ('/privacy/', 'Privacy'), ('/development/', 'Development')]
SEARCH_PAGES = {'/guide/': 'Guide', '/privacy/': 'Privacy', '/install/': 'Install', '/development/': 'Development', '/smart-features/': 'Smart features'}
SITE_PATHS = ['/', '/guide/', '/privacy/', '/install/', '/development/', '/smart-features/', '/releases/', '/whats-new/', '/accessibility/']
REPO = 'https://github.com/deansasek/library'
# The GitHub Pages project path. Links on /404.html must be written under it: the page is served at
# whatever address was missing, so a relative link would resolve under the missing path.
BASE_PATH = '/library-site'
CHEV_R = '<svg class="icon chevron" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="m9 6 6 6-6 6"/></svg>'
CHEV_L = '<svg class="icon chevron" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="m15 6-6 6 6 6"/></svg>'

# ----------------------------------------------------------------------
# shared chrome: nav, footer, and document head
# ----------------------------------------------------------------------

def search():
    """The site-wide search field that the header shows on every page. It starts hidden; script.js reveals it once the index loads."""
    return ('<div class="search" role="search" hidden><label class="visually-hidden" for="site-search">Search the docs</label>'
            '<div class="search-field"><svg class="icon search-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
            '<circle cx="11" cy="11" r="6.5"/><path d="m16 16 4 4"/></svg>'
            '<input id="site-search" type="search" placeholder="Search" autocomplete="off"></div>'
            '<div class="results" hidden></div></div>')


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
            '</nav>'
            + search() +
            '</div></header>')


def footer():
    return ('<footer><nav class="footer-cols" aria-label="Footer">'
            f'<div><p class="ft">Project</p><a href="{REPO}" rel="noopener noreferrer">GitHub</a><a href="/development/">Development</a>'
            '<a href="https://buymeacoffee.com/deansasek" rel="noopener noreferrer">Support</a>'
            '</div>'
            '<div><p class="ft">Guide</p><a href="/guide/">Feature guide</a><a href="/smart-features/">Smart features</a>'
            '<a href="/install/">Install</a><a href="/accessibility/">Accessibility</a></div>'
            '<div><p class="ft">Privacy</p><a href="/privacy/">Privacy guide</a></div>'
            '<div><p class="ft">Releases</p><a href="/whats-new/">What\'s new</a><a href="/releases/">Releases</a></div>'
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
            f'<div class="article"><nav class="toc" aria-label="On this page"><p class="toc-title">On this page</p>{toc_items}</nav>'
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


def absolutize(html, base):
    """Point local href/src at the site's full base path, so the page works from any address.

    Used for /404.html, which GitHub Pages serves at the address that was missing. Absolute https URLs
    and fragments are left as they are.
    """
    return re.sub(r'\b(href|src)="(/[^"]*)"',
                  lambda m: m.group(0) if m.group(2).startswith('//') else f'{m.group(1)}="{base}{m.group(2)}"',
                  html)


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
    """Fail the build on empty list items, paragraphs, blocks, and table cells, on back-to-back lists,
    and on an executable inline <script>, which the CSP in _headers would block."""
    parser = EmptyCheck()
    parser.feed(html)
    parser.close()
    problems = list(parser.problems)
    for m in re.finditer(r'</(ul|ol)><(ul|ol)\b', html):
        problems.append('two lists in a row (merge them): ...' + html[max(0, m.start() - 40):m.end()] + '...')
    for m in re.finditer(r'<script\b([^>]*)>', html, re.I):
        attrs = m.group(1)
        # A script with a src is a file, and application/ld+json is data, so both are allowed.
        if re.search(r'\bsrc=', attrs, re.I) or re.search(r'\btype="application/ld\+json"', attrs, re.I):
            continue
        problems.append('executable inline <script> (the CSP in _headers blocks it; '
                        'move the code to a file): ' + html[m.start():m.end()][:80])
    if problems:
        sys.exit('build check failed for %s:\n  %s' % (path, '\n  '.join(problems)))


def check_pages_reachable():
    """Fail the build if a SITE_PATHS page is linked from neither the footer nor the narrow-screen header.

    Below 735px the stylesheet hides the header's .nav-extra links, so a link counts only when it is in the
    footer or in the part of the header that stays visible. This is what keeps Accessibility, Releases, and
    the other top-level pages reachable from a phone.
    """
    narrow_header = re.sub(r'<a class="nav-extra"[^>]*>.*?</a>', '', header())
    chrome = narrow_header + footer()
    missing = [p for p in SITE_PATHS if f'href="{p}"' not in chrome]
    if missing:
        sys.exit('build check failed: no footer or narrow-screen header link to ' + ', '.join(missing))
def _between(path, pattern):
    """The first capture group of pattern in a built file, or None."""
    with open(os.path.join(ROOT, path.lstrip('/'))) as f:
        m = re.search(pattern, f.read(), flags=re.S)
    return m.group(1) if m else None


def check_install_command(command):
    """Fail the build unless the landing page and the Install page show the same checksum-verified command.

    Both come from INSTALL_COMMAND in content/pages.py, so the two cannot drift apart, and the landing
    page must never send visitors to git clone the repository.
    """
    problems = []
    landing = _between('/index.html', r'id="download".*?<pre><code>(.*?)</code></pre>')
    install = _between('/install/index.html', r'id="install".*?<pre><code>(.*?)</code></pre>')
    if landing != command or install != command:
        problems.append('the landing page and the Install page must show the shared INSTALL_COMMAND')
    if 'shasum -a 256 -c' not in (command or ''):
        problems.append('the install command must verify the release checksum with shasum -a 256 -c')
    landing_tools = _between('/index.html', r'<dt>Developer tools</dt><dd>(.*?)</dd>')
    install_tools = _between('/install/index.html', r'<dt>Developer tools</dt><dd>(.*?)</dd>')
    if landing_tools != install_tools:
        problems.append('the landing page requirements must match the Install page')
    with open(os.path.join(ROOT, 'index.html')) as f:
        if 'git clone' in f.read():
            problems.append('the landing page must not tell visitors to git clone the repository')
    if problems:
        sys.exit('install check failed:\n  ' + '\n  '.join(problems))

# A fragment, an absolute path (such as /library-site/assets/styles.css), or a full URL. Anything else
# is relative and would resolve under the address that was missing.
ABSOLUTE_LINK = re.compile(r'^(?:/|#|[a-zA-Z][a-zA-Z0-9+.-]*:)')


def check_absolute_links(path, html):
    """Fail the build if any href or src on this page is a relative path.

    Paths are written with the leading `/`, so they carry the full base and work at any depth.
    """
    relative = [m.group(1) for m in re.finditer(r'\b(?:href|src)="([^"]*)"', html)
                if not ABSOLUTE_LINK.match(m.group(1))]
    if relative:
        sys.exit('build check failed for %s (links must not be relative):\n  %s'
                 % (path, '\n  '.join(relative)))


# ----------------------------------------------------------------------
# file writers and generated files
# ----------------------------------------------------------------------

GUIDE_PATH_OF = {}  # guide section id -> its page, filled in by build_all


def point_guide_links(html):
    """Old links to a guide section, such as /guide/#clipboard, go to the group page that now holds it."""
    return re.sub(r'href="(?:/|\./)guide/#([a-z0-9-]+)"',
                  lambda m: f'href="{GUIDE_PATH_OF[m.group(1)]}#{m.group(1)}"' if m.group(1) in GUIDE_PATH_OF else m.group(0),
                  html)


KEY_GLYPHS = '⌘⇧⌥⌃'


def _key_cap(m):
    caps = ''.join(f'<kbd>{c}</kbd>' for c in m.group(1))
    return caps + (f'<kbd>{m.group(2)}</kbd>' if m.group(2) else '')


# Copy writes shortcuts with Apple's key symbols, per the notation rule in content/pages.py, so most key caps come from
# the glyphs above. A key name written out in running text, such as "press Return", and any older word form such as
# Command-Z, are set as key caps too. "Option-click" is a key with a mouse action, so only the key becomes a key cap.
_KEY_COMBO = re.compile(r'\b(?:Command|Control|Option|Shift)(?:-(?:Command|Control|Option|Shift|Return|Escape|Tab|Space|Delete|[A-Z]|[0-9]+)\b)+')
_KEY_AFTER_VERB = re.compile(r'(?<=[Pp]ress )(Return|Escape|Tab|Space|Delete)\b|(?<=[Hh]old )(Option|Command|Control|Shift)\b')


def _combo_caps(m):
    return ''.join(f'<kbd>{part}</kbd>' for part in m.group(0).split('-'))


_KEY_CLICK = re.compile(r'\b(Command|Control|Option|Shift)-([Cc]lick)\b')


def _word_keys(text):
    text = _KEY_CLICK.sub(lambda m: f'<kbd>{m.group(1)}</kbd>-{m.group(2)}', text)
    text = _KEY_COMBO.sub(_combo_caps, text)
    return _KEY_AFTER_VERB.sub(lambda m: f'<kbd>{m.group(0)}</kbd>', text)


def key_caps(html):
    """Shortcut glyphs in running text become key caps. Code, preformatted text, and existing key caps are left alone."""
    parts = re.split(r'(<[^>]+>)', html)
    out, skip = [], 0
    for part in parts:
        if part.startswith('<'):
            if re.match(r'<(code|pre|kbd)[\s>]', part):
                skip += 1
            elif re.match(r'</(code|pre|kbd)>', part):
                skip = max(0, skip - 1)
            out.append(part)
        elif skip:
            out.append(part)
        else:
            out.append(_word_keys(re.sub(r'([⌘⇧⌥⌃]+)([A-Za-z0-9]+|[,./])?', _key_cap, part)))
    return ''.join(out)


def write(path, html):
    full = os.path.join(ROOT, path.lstrip('/'))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    html = key_caps(point_guide_links(html))
    # /404.html is served at whatever address was missing, so relative links would resolve under that
    # missing path. Its links are written under the site's full base path instead, so they work at any depth.
    html = absolutize(html, BASE_PATH) if path == '/404.html' else relativize(html, path)
    out = code_bars(minify_html(html))
    check_build_html(path, out)
    if path == '/404.html':
        check_absolute_links(path, out)
    with open(full, 'w') as f:
        f.write(out)


def update_landing(install_command):
    p = os.path.join(ROOT, 'index.html')
    s = open(p).read()
    # The Download command comes from the same constant as the Install page (content/pages.py), so the two
    # cannot drift apart: every build rewrites it. A stale git clone command fails the build instead of
    # being quietly replaced, so the original bug cannot come back unnoticed.
    stale = re.search(r'<section class="block band" id="download">.*?<pre><code>(.*?)</code></pre>', s, flags=re.S)
    if stale and 'git clone' in stale.group(1):
        sys.exit('install check failed:\n  the landing page must not tell visitors to git clone the repository')
    s = re.sub(r'<header class="nav">.*?</header>', lambda m: header(), s, flags=re.S)
    s = re.sub(r'<footer>.*?</footer>', lambda m: footer(), s, flags=re.S)
    s = re.sub(r'(<section class="block band" id="download">.*?<pre><code>).*?(</code></pre>)',
               lambda m: m.group(1) + install_command + m.group(2), s, flags=re.S)
    s = re.sub(r'\s*<meta name="color-scheme"[^>]*>', '', s)
    s = re.sub(r'\s*<meta property="og:site_name"[^>]*>', '', s)
    s = code_bars(minify_html(relativize(key_caps(point_guide_links(s)), '/index.html')))
    check_build_html('/index.html', s)
    open(p, 'w').write(s)


def script_json(data):
    """JSON that is safe inside a <script> element: <, >, and & are written as \\u escapes, so no value can end the element."""
    return json.dumps(data, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')


def write_guide_redirect(paths):
    """Writes assets/guide-redirect.js for the guide index: a link with a section's anchor moves to that
    section's group page. It is a file, not an inline script, because the CSP in _headers blocks inline scripts."""
    body = ('(function(){var map=' + script_json(paths) + ';var id=location.hash.slice(1);'
            'if(id&&map[id]){location.replace(map[id]+"#"+id);}})();\n')
    with open(os.path.join(ROOT, 'assets', 'guide-redirect.js'), 'w') as f:
        f.write(body)


def path_key(path):
    return path.replace('index.html', '')


def sitemap_lastmod(path, release_dates, reviewed):
    """The lastmod for one sitemap URL, or None to leave the optional element out.

    A release's What's new page uses its release date; every other page uses the date the docs were last
    reviewed. When neither is known the page has no real date, and a build date would wrongly tell search
    engines it changed today, and give the hourly sync a diff to commit.
    """
    release = path[len('/whats-new/'):].strip('/') if path.startswith('/whats-new/') else ''
    if release:
        return release_dates.get(release)
    return reviewed.isoformat() if reviewed else None


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


SEARCH_TEXT_LIMIT = 400
# Search queries that must find a known sub-section, so word-order matching cannot regress. Each pair is a query
# and the id of a section or sub-section it has to reach.
SEARCH_CHECKS = [('template', 'manager-templates'), ('bulk edit', 'manager-bulk-edit'),
                 ('queue paste', 'clipboard-paste-queue'), ('pin clipboard', 'clipboard-pin-an-item')]


def _search_text(html):
    """Plain text for the search index: tags dropped, entities decoded, whitespace collapsed."""
    text = ' '.join(H.unescape(re.sub(r'<[^>]+>', ' ', html)).split())
    return re.sub(r'\s+([.,;:!?])', r'\1', text)[:SEARCH_TEXT_LIMIT]


def check_search_index(items, indexed, expected):
    """Fail the build unless every <h3 id> is indexed and every word of a check query is found in any order."""
    missing = sorted(expected - indexed)
    if missing:
        sys.exit('build check failed: headings missing from the search index: ' + ', '.join(missing))
    for query, anchor in SEARCH_CHECKS:
        words = query.lower().split()
        if not any(it['u'].endswith('#' + anchor) and
                   all(w in (it['t'] + ' ' + it['p'] + ' ' + it['s']).lower() for w in words) for it in items):
            sys.exit(f'build check failed: searching for "{query}" does not find #{anchor}')


def write_search_index(rendered, guide_groups):
    """A JSON index of each docs heading and its text, for script.js.

    Guide sections are labeled with their navigation group, such as "Find and open", not just "Guide".
    Each <h3 id> is indexed as its own entry, so sub-sections such as Templates are searchable.
    """
    items, indexed, expected = [], set(), set()
    for path, page_html in rendered.items():
        pg = path.replace('index.html', '')
        if pg == '/guide/' or not (pg in SEARCH_PAGES or pg.startswith('/guide/')):
            continue
        # Relative to the script's folder (assets/), so the link works under any base path.
        url = '../' + pg.strip('/') + '/#'
        for id_ in re.findall(r'<h3 id="([^"]+)"', page_html):
            expected.add(url + id_)
        for m in re.finditer(r'<section id="([^"]+)"><h2>([^<]*)</h2>(.*?)</section>', page_html, re.S):
            sid, title, body = m.groups()
            label = guide_groups[sid] if pg.startswith('/guide/') else SEARCH_PAGES[pg]
            # The section's own text runs up to its first sub-heading; each sub-heading owns the text after it.
            items.append({'t': H.unescape(title), 'p': label, 'u': url + sid,
                          's': _search_text(re.split(r'<h3 id="', body)[0])})
            indexed.add(url + sid)
            for hm in re.finditer(r'<h3 id="([^"]+)"[^>]*>(.*?)(?=<h3 id="|$)', body, re.S):
                hid, inner = hm.groups()
                items.append({'t': _search_text(inner.split('</h3>', 1)[0]), 'p': label, 'u': url + hid,
                              's': _search_text(inner)})
                indexed.add(url + hid)
    check_search_index(items, indexed, expected)
    data = json.dumps(items, ensure_ascii=False, separators=(',', ':'))
    with open(os.path.join(ROOT, 'assets', 'search-index.json'), 'w') as f:
        f.write(data)


# ----------------------------------------------------------------------
# release check and build entry point
# ----------------------------------------------------------------------

def version_key(version):
    """The numbers in a version, in order, so 1.10.0 sorts after 1.9.0. Mirrors tools/sync_releases.py."""
    return [int(p) for p in re.findall(r'\d+', version)]


def latest_release():
    """The newest release in content/releases.json, or None when the file is missing or empty.

    The build reads the already-synced file, so the check needs no network.
    """
    path = os.path.join(ROOT, 'content', 'releases.json')
    try:
        with open(path) as f:
            releases = json.load(f)
    except (OSError, ValueError):
        return None
    return max(releases, key=lambda r: version_key(r['version']), default=None)


def check_release(reviewed):
    """Warn if the latest release is newer than the version the docs were reviewed against.

    The warning is repeated as a GitHub Actions annotation and step summary, so maintainers see it even though the
    workflow stays green. Never fails the build: a missing releases file only prints a note.
    """
    latest = latest_release()
    if latest is None:
        print('release check skipped: content/releases.json is missing or empty')
        return
    tag, version = latest['tag'], latest['version']
    if version == reviewed:
        print(f'release check: the docs were reviewed against {reviewed}, the latest release.')
        return
    message = (f'latest release is {tag}, but the docs were last reviewed against {reviewed}. '
               'Review the docs, then set REVIEWED_VERSION in content/pages.py.')
    if os.environ.get('GITHUB_ACTIONS'):
        print(f'::warning file=content/pages.py,title=Docs are out of date::{message}')
        summary = os.environ.get('GITHUB_STEP_SUMMARY')
        if summary:
            with open(summary, 'a') as f:
                f.write('## Docs are out of date\n\n'
                        f'The docs were last reviewed against **{reviewed}**, but the latest release is **{tag}**.\n\n'
                        'Review the docs, then set `REVIEWED_VERSION` in `content/pages.py`.\n')
    print(f'WARNING: {message}')


SW_SKIP_DIRS = {'.git', 'src', 'content', 'tools', 'assets'}
SW_PRECACHE_ASSETS = ['assets/styles.css', 'assets/script.js', 'assets/guide-redirect.js', 'assets/search-index.json',
                      'assets/icon.png', 'manifest.webmanifest']

SW_TEMPLATE = """// Generated by tools/build.py. Keeps the site readable offline. Pages are network first, so readers get the
// newest version while they are online. Everything else is served from the cache, and images load on first use.
var VERSION = "%(version)s";
var PRECACHE = %(precache)s;

self.addEventListener("install", function (event) {
  // Reload bypasses the browser's HTTP cache, so each new version precaches the files from the current deploy.
  event.waitUntil(caches.open(VERSION).then(function (cache) {
    return cache.addAll(PRECACHE.map(function (u) { return new Request(u, { cache: "reload" }); }));
  }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener("activate", function (event) {
  event.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== VERSION; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener("fetch", function (event) {
  var request = event.request;
  if (request.method !== "GET" || new URL(request.url).origin !== location.origin) { return; }
  if (request.mode === "navigate") {
    // Pages are cached without their query string, so the cache holds one entry per page, not per URL.
    var key = new URL(request.url);
    key.search = "";
    event.respondWith(fetch(request).then(function (response) {
      if (!response.ok) { return response; }
      var copy = response.clone();
      return caches.open(VERSION).then(function (cache) { return cache.put(key.href, copy); })
        .catch(function () {}).then(function () { return response; });
    }).catch(function () {
      return caches.open(VERSION).then(function (cache) {
        return cache.match(key.href).then(function (hit) {
          return hit || cache.match(new URL("404.html", self.registration.scope).href);
        });
      });
    }));
    return;
  }
  event.respondWith(caches.open(VERSION).then(function (cache) {
    return cache.match(request).then(function (hit) {
      if (hit) { return hit; }
      return fetch(request).then(function (response) {
        if (response.ok) { cache.put(request, response.clone()); }
        return response;
      });
    });
  }));
});
"""


def write_service_worker():
    """Writes sw.js at the site root. Its version is a hash of the files it precaches, so each build is a new version."""
    pages = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SW_SKIP_DIRS and not d.startswith('.')]
        for name in filenames:
            if name.endswith('.html'):
                rel = os.path.relpath(os.path.join(dirpath, name), ROOT).replace(os.sep, '/')
                pages.append(rel[:-len('index.html')] if rel.endswith('index.html') else rel)
    precache = sorted(set(pages) | set(SW_PRECACHE_ASSETS))
    digest = hashlib.sha256()
    for rel in precache:
        source = rel if rel and not rel.endswith('/') else rel + 'index.html'
        with open(os.path.join(ROOT, source), 'rb') as f:
            digest.update(rel.encode() + f.read())
    version = digest.hexdigest()[:12]
    urls = ['./' if r == '' else r for r in precache]
    body = SW_TEMPLATE % {'version': version, 'precache': json.dumps(urls)}
    if 'cache: "reload"' not in body:
        sys.exit('build check failed: sw.js must precache with cache: "reload" so a new version cannot pin '
                 'stale files from the HTTP cache')
    with open(os.path.join(ROOT, 'sw.js'), 'w') as f:
        f.write(body)


def build_all(check=False):
    global REVIEWED_LABEL
    check_pages_reachable()
    import importlib.util
    spec = importlib.util.spec_from_file_location('pages', os.path.join(ROOT, 'content', 'pages.py'))
    pages = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pages)
    reviewed_on = pages.REVIEWED_DATE or TODAY
    REVIEWED_LABEL = reviewed_on.strftime('%B %d, %Y').replace(' 0', ' ')
    rendered = pages.render(page)
    GUIDE_PATH_OF.update(pages.GUIDE_PATH_OF)
    write_search_index(rendered, pages.GUIDE_GROUP_OF)
    write_guide_redirect(pages.GUIDE_PATH_OF)
    for path, html in rendered.items():
        html = html.replace('__HEADER__', header()).replace('__FOOTER__', footer())
        if path.startswith('/guide/') and path != '/guide/index.html' and path.endswith('/index.html'):
            # Breadcrumbs for each guide group page, so search results show the path to it.
            crumbs = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Library', 'item': 'https://deansasek.github.io/library-site/'},
                {'@type': 'ListItem', 'position': 2, 'name': 'Guide', 'item': 'https://deansasek.github.io/library-site/guide/'},
                {'@type': 'ListItem', 'position': 3, 'name': H.unescape(re.search(r'<h1>(.*?)</h1>', html).group(1)).replace(': Library guide', ''),
                 'item': 'https://deansasek.github.io/library-site' + path.replace('index.html', '')}]}
            html = html.replace('</head>', '<script type="application/ld+json">' + script_json(crumbs) + '</script></head>', 1)
        if path == '/guide/index.html':
            # Old guide anchors, such as /guide/#clipboard-paste-queue, open the page that holds that section.
            html = html.replace('</body>', '<script src="/assets/guide-redirect.js" defer></script></body>', 1)
        html = html.replace('</main>', pager(path) + '</main>', 1) if path_key(path) in dict(PAGER_ORDER) else html
        write(path, html)
    update_landing(pages.INSTALL_COMMAND)
    check_install_command(pages.INSTALL_COMMAND)
    css = open(os.path.join(ROOT, 'src', 'styles.css')).read()
    open(os.path.join(ROOT, 'assets', 'styles.css'), 'w').write(minify_css(css))
    js = open(os.path.join(ROOT, 'src', 'script.js')).read()
    js = '\n'.join(l.strip() for l in js.splitlines() if l.strip() and not l.strip().startswith('//'))
    open(os.path.join(ROOT, 'assets', 'script.js'), 'w').write(js + '\n')
    release_paths = sorted(k.replace('index.html', '') for k in rendered if k.startswith('/whats-new/') and k != '/whats-new/index.html')
    # Each URL carries its own real date (a release's date on a What's new page, the review date elsewhere),
    # not the build date, so a rebuild that changes nothing writes the same sitemap.
    release_dates = {r['version'].replace('.', '-'): r['date'] for r in pages._release_records()}
    urls = ''
    for u in SITE_PATHS + sorted(set(pages.GUIDE_PATH_OF.values())) + release_paths:
        stamp = sitemap_lastmod(u, release_dates, pages.REVIEWED_DATE)
        lastmod = f'    <lastmod>{stamp}</lastmod>\n' if stamp else ''
        urls += f'  <url>\n    <loc>https://deansasek.github.io/library-site{u}</loc>\n{lastmod}  </url>\n'
    open(os.path.join(ROOT, 'sitemap.xml'), 'w').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '</urlset>\n')
    write_service_worker()
    if check:
        check_release(pages.REVIEWED_VERSION)


if __name__ == '__main__':
    build_all(check='--check-release' in sys.argv)
    print('built')

