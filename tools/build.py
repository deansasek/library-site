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
REVIEWED_VERSION = ''
REVIEWED_ISO = TODAY.isoformat()
# Docs pages in reading order (the guide's order: start, features, then the reference pages).
PAGER_ORDER = [('/install/', 'Install'), ('/guide/', 'Guide'), ('/smart-features/', 'Smart features'),
               ('/privacy/', 'Privacy'), ('/development/', 'Development')]
SEARCH_PAGES = {'/guide/': 'Guide', '/privacy/': 'Privacy', '/install/': 'Install', '/development/': 'Development', '/smart-features/': 'Smart features'}
SITE_PATHS = ['/', '/guide/', '/privacy/', '/install/', '/development/', '/smart-features/', '/releases/', '/whats-new/', '/accessibility/']
REPO = 'https://github.com/deansasek/library'
# The GitHub Pages project path. Links on /404.html must be written under it: the page is served at
# whatever address was missing, so a relative link would resolve under the missing path.
BASE_PATH = '/library-site'
# Crawlers read robots.txt only from the host root, which a GitHub Pages project site does not own. Every page
# therefore declares the sitemap in its head, so search engines can find it without a root robots.txt.
SITEMAP_LINK = ('<link rel="sitemap" type="application/xml" title="Sitemap" '
                'href="https://deansasek.github.io/library-site/sitemap.xml">')
CHEV_R = '<svg class="icon chevron" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="m9 6 6 6-6 6"/></svg>'
CHEV_L = '<svg class="icon chevron" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="m15 6-6 6 6 6"/></svg>'

# ----------------------------------------------------------------------
# the app's own docs: a pinned copy, so the site says what the app says
# ----------------------------------------------------------------------

APP_REPO = 'https://github.com/deansasek/library.git'
# A sibling checkout, used by --update-app-docs before it falls back to a clone.
SIBLING_APP = os.path.join(os.path.dirname(ROOT), 'library')
APP_DOCS = os.path.join(ROOT, 'content', 'appdocs')
APP_DOC_NAMES = ['guide.md', 'privacy.md', 'development.md']


def app_doc_ref():
    """The app commit the vendored docs came from, or exit when the pin is missing.

    The docs are committed, so a build needs no network and always renders the same text. A build without the pin
    would silently fall back to the site's own copy, which is the drift this replaces, so a missing one fails.
    """
    path = os.path.join(APP_DOCS, 'REF')
    if not os.path.isfile(path):
        sys.exit('missing %s. Run python3 tools/build.py --update-app-docs to vendor the app docs.' % path)
    ref = open(path).read().strip()
    if not re.fullmatch(r'[0-9a-f]{40}', ref):
        sys.exit('%s holds %r, which is not a full commit id.' % (path, ref))
    return ref


def app_doc(name):
    """The app's doc at the pinned commit, as text."""
    path = os.path.join(APP_DOCS, name)
    if not os.path.isfile(path):
        sys.exit('missing %s. Run python3 tools/build.py --update-app-docs to vendor the app docs.' % path)
    return open(path).read()


def _git_out(args, cwd=None):
    import subprocess
    return subprocess.run(args, cwd=cwd, check=True, stdout=subprocess.PIPE).stdout


def app_doc_references(text):
    """Every path a doc points at: Markdown links and images, and the src of an HTML <img>."""
    refs = [m.group(1) for m in re.finditer(r'!?\[[^\]]*\]\(\s*([^)\s]+)', text)]
    refs += [m.group(1) for m in re.finditer(r'<img[^>]*\bsrc="([^"]+)"', text)]
    return [r for r in refs if not re.match(r'(https?:|mailto:|#)', r)]


def update_app_docs(ref=None):
    """Copy the app's docs, and the images they show, from the app repo at `ref` into content/appdocs.

    Uses a sibling checkout when it has that commit, and clones otherwise. The commit is recorded in REF, so the
    site is built from one known version of the app's words.
    """
    import subprocess
    repo = None
    if os.path.isdir(os.path.join(SIBLING_APP, '.git')):
        try:
            resolved = _git_out(['git', 'rev-parse', '--verify', (ref or 'HEAD') + '^{commit}'],
                                cwd=SIBLING_APP).decode().strip()
            repo, ref = SIBLING_APP, resolved
        except subprocess.CalledProcessError:
            repo = None
    if repo is None:
        import tempfile
        repo = tempfile.mkdtemp(prefix='library-app-')
        subprocess.run(['git', 'clone', '--quiet', APP_REPO, repo], check=True)
        ref = _git_out(['git', 'rev-parse', '--verify', (ref or 'HEAD') + '^{commit}'], cwd=repo).decode().strip()
    os.makedirs(APP_DOCS, exist_ok=True)
    for name in APP_DOC_NAMES:
        open(os.path.join(APP_DOCS, name), 'wb').write(_git_out(['git', 'show', ref + ':docs/' + name], cwd=repo))
    # Only the images the docs show, so the vendored copy stays small enough to commit.
    for name in APP_DOC_NAMES:
        for target in app_doc_references(app_doc(name)):
            if not target.startswith('docs/media/'):
                continue
            open(os.path.join(APP_DOCS, os.path.basename(target)), 'wb').write(
                _git_out(['git', 'show', ref + ':' + target], cwd=repo))
    open(os.path.join(APP_DOCS, 'REF'), 'w').write(ref + '\n')
    print('vendored the app docs at %s' % ref)


def check_app_docs():
    """Fail when a doc points at an image or another doc that is not vendored beside it.

    A missing reference would otherwise reach the page as a dead link or a broken image, and the build would pass.
    """
    ref = app_doc_ref()
    problems = []
    for name in APP_DOC_NAMES:
        for target in app_doc_references(app_doc(name)):
            if target.startswith('docs/media/') or target.startswith('docs/'):
                if not os.path.isfile(os.path.join(APP_DOCS, os.path.basename(target))):
                    problems.append('%s points at %s, which is not vendored' % (name, target))
    if problems:
        sys.exit('app docs check failed at %s:\n  %s' % (ref[:12], '\n  '.join(sorted(set(problems)))))


def markdown(text, row_headers=False):
    """Converts the app's Markdown to the HTML the site uses.

    Only what the app's docs contain: headings, paragraphs, bullet lists, pipe tables, images, and the inline
    **bold**, *italic*, `code` and [link] forms. A block that is already HTML is passed through, since the docs use
    that for a centred image with its alt text. With `row_headers`, the first cell of each table row becomes a row
    header, which is what the site's tables use.
    """
    out = []
    for block in re.split(r'\n\s*\n', text.strip()):
        block = block.strip()
        if not block:
            continue
        if block.startswith('|'):
            out.append(_markdown_table(block, row_headers))
            continue
        heading = re.match(r'(#{1,6})\s+(.*)', block)
        if heading:
            level = len(heading.group(1))
            out.append(f'<h{level}>{inline(heading.group(2))}</h{level}>')
            continue
        if re.match(r'^\s*[-*]\s+', block):
            items = ''.join(f'<li>{inline(re.sub(r"^\s*[-*]\s+", "", line).strip())}</li>'
                            for line in block.splitlines() if re.match(r'^\s*[-*]\s+', line))
            out.append('<ul>' + items + '</ul>')
            continue
        if block.startswith('<'):
            out.append(block)
            continue
        out.append('<p>' + inline(' '.join(l.strip() for l in block.splitlines())) + '</p>')
    return '\n'.join(out)


def _markdown_table(block, row_headers):
    """One pipe table as the site's table markup, without a caption: the page supplies its own."""
    rows = [[c.strip() for c in line.strip().strip('|').split('|')]
            for line in block.splitlines() if line.strip().startswith('|')]
    head = rows[0]
    body = [r for r in rows[2:] if not set(''.join(r)) <= set('-: ')]
    thead = '<tr>' + ''.join(f'<th scope="col">{inline(c)}</th>' for c in head) + '</tr>'
    rows_html = ''
    for row in body:
        cells = (f'<th scope="row">{inline(row[0])}</th>' if row_headers and row else '') \
            + ''.join(f'<td>{inline(c)}</td>' for c in row[1:])
        rows_html += f'<tr>{cells}</tr>'
    return f'<table><thead>{thead}</thead><tbody>{rows_html}</tbody></table>'


def inline(text):
    """The inline Markdown forms the docs use, with every piece HTML-escaped first."""
    text = H.escape(text)
    text = re.sub(r'!\[([^\]]*)\]\(([^)\s]+)\)',
                  lambda m: f'<img src="{m.group(2)}" alt="{m.group(1)}">', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<![\w*])\*([^*\n]+)\*(?![\w*])', r'<em>\1</em>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text

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
            '<a class="nav-brand" href="/"><img src="/assets/icon-44.png" width="22" height="22" alt="">Library</a>'
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
{SITEMAP_LINK}
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

def reviewed_line(version, verb, label, iso):
    """One metadata line under the page title, like the quiet date line on an Apple page."""
    date = f'<time datetime="{iso}">{label}</time>' if iso else label
    return f'<p class="updated">Version {version} · {verb} {date}</p>'


def page(path, title, desc, lede, toc, sections, plain=False, extra='', released=None, released_version=None, released_iso=None, nav=None):
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
    line = (reviewed_line(released_version, 'Released', released, released_iso) if released
            else reviewed_line(REVIEWED_VERSION, 'Updated', REVIEWED_LABEL, REVIEWED_ISO))
    return (head(title, desc, path) + header() +
            f'<main id="main" class="doc">{back}<h1>{title}</h1>{line}<p class="lede">{lede}</p>'
            f'<p class="updated">' + (f'Released {released}. ' if released else 'Applies to the current release of Library. ') + f'Last reviewed {REVIEWED_LABEL}.</p>'
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
    on an executable inline <script>, which the CSP in _headers would block, and on markup that shows as
    literal text because it was escaped twice."""
    parser = EmptyCheck()
    parser.feed(html)
    parser.close()
    problems = list(parser.problems)
    for m in re.finditer(r'</(ul|ol)><(ul|ol)\b', html):
        problems.append('two lists in a row (merge them): ...' + html[max(0, m.start() - 40):m.end()] + '...')
    for m in re.finditer(r'&lt;(strong|code)&gt;', html):
        problems.append('markup escaped twice (shows as literal text): ...'
                        + html[max(0, m.start() - 40):m.end() + 40] + '...')
    for m in re.finditer(r'<script\b([^>]*)>', html, re.I):
        attrs = m.group(1)
        # A script with a src is a file, and application/ld+json is data, so both are allowed.
        if re.search(r'\bsrc=', attrs, re.I) or re.search(r'\btype="application/ld\+json"', attrs, re.I):
            continue
        problems.append('executable inline <script> (the CSP in _headers blocks it; '
                        'move the code to a file): ' + html[m.start():m.end()][:80])
    # A noindex page must not point a canonical or og:url at itself: noindex says drop the page, while a
    # canonical would claim the page (or, on 404.html, any missing address) is a copy of that URL.
    if re.search(r'<meta name="robots" content="[^"]*\bnoindex\b', html):
        for tag in ('<link rel="canonical"', '<meta property="og:url"'):
            if tag in html:
                problems.append('a noindex page must not declare %s' % tag)
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


def check_sitemap_declared(paths):
    """Fail the build unless every indexable page declares the sitemap in its head.

    A GitHub Pages project site cannot serve robots.txt from the host root, where crawlers look for it, so
    the pages themselves point crawlers at the sitemap. /404.html is noindex, so it is left out.
    """
    missing = [p for p in paths
               if SITEMAP_LINK not in open(os.path.join(ROOT, p.lstrip('/'))).read()]
    if missing:
        sys.exit('build check failed: no sitemap link in ' + ', '.join(missing))


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


def check_landing_privacy():
    """Fail the build unless the landing privacy section agrees with the privacy page.

    The landing heading must name the iCloud Drive exception, because Keep Library in iCloud Drive moves
    the library into iCloud Drive and to the user's other Macs. Its internet list must include Update in
    Terminal, which the privacy page's What is sent list names. The claims are checked against the built
    files, so the landing page cannot drift back to the older wording unnoticed.
    """
    heading = _between('/index.html', r'id="privacy".*?<h2>(.*?)</h2>')
    facts = _between('/index.html', r'id="privacy".*?<ul class="facts">(.*?)</ul>')
    sent = _between('/privacy/index.html', r'id="what-is-sent".*?<ul>(.*?)</ul>')
    problems = []
    if not heading or 'iCloud Drive' not in heading:
        problems.append('the landing privacy heading must name the iCloud Drive exception')
    if not facts or 'Update in Terminal' not in facts:
        problems.append('the landing internet list must include Update in Terminal')
    if not sent or 'Update in Terminal' not in sent:
        problems.append('the privacy page What is sent list must include Update in Terminal')
    if problems:
        sys.exit('landing privacy check failed:\n  ' + '\n  '.join(problems))


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


# The landing page demos, which replaced the two GIFs. The issue sets a 200 KB budget for the pair
# of clips and a 400 KB budget for the first screen's images, so the build fails if either is missed.
DEMO_CLIPS = {'menu_bar': (479, 462), 'quick_open': (558, 316)}
CLIP_BUDGET = 200 * 1024
FIRST_VIEW_BUDGET = 400 * 1024


def _asset_bytes(ref, problems):
    """The size of a local asset referenced from the landing page, or 0 with a problem if it is missing."""
    if not ref or ref.startswith(('data:', 'http:', 'https:', '//')):
        return 0
    rel = ref[2:] if ref.startswith('./') else ref.lstrip('/')
    path = os.path.join(ROOT, rel)
    if not os.path.isfile(path):
        problems.append('landing page asset is missing: ' + ref)
        return 0
    return os.path.getsize(path)


def _has_attr(attrs, name):
    return re.search(r'(?:^|\s)%s(?:[\s=]|$)' % name, attrs) is not None


def check_landing_media():
    """Fail the build unless the landing demos are small, looping videos that still work without script.

    Each demo is a <video> with its original width and height, a poster, and native autoplay (muted,
    looping, playsinline), with MP4 and WebM sources. A GIF may not come back. The pair must fit the
    200 KB clip budget, counting every source and poster, and the first screen's media must fit the
    400 KB image budget. script.js must pause the clips under prefers-reduced-motion: reduce.
    """
    with open(os.path.join(ROOT, 'index.html')) as f:
        html = f.read()
    problems = []
    if re.search(r'\bsrc="[^"]*\.gif"', html):
        problems.append('the landing page must not load a GIF; use the video demos instead')
    videos = re.findall(r'<video\b([^>]*)>(.*?)</video>', html, re.S)
    if len(videos) != len(DEMO_CLIPS):
        problems.append('the landing page needs the %d demo <video> elements' % len(DEMO_CLIPS))
    clip_bytes = 0
    for attrs, inner in videos:
        stem = next((s for s in DEMO_CLIPS if s in attrs or s in inner), '')
        if not stem:
            problems.append('unrecognized demo <video>: ' + attrs[:80])
            continue
        width, height = DEMO_CLIPS[stem]
        if not re.search(r'\bwidth="%d"' % width, attrs) or not re.search(r'\bheight="%d"' % height, attrs):
            problems.append('%s demo must keep its %dx%d size' % (stem, width, height))
        for name in ('autoplay', 'muted', 'loop', 'playsinline'):
            if not _has_attr(attrs, name):
                problems.append('%s demo must have the %s attribute so it loops without script' % (stem, name))
        poster = re.search(r'\bposter="([^"]*)"', attrs)
        if not poster:
            problems.append('%s demo must have a poster image' % stem)
        else:
            clip_bytes += _asset_bytes(poster.group(1), problems)
        sources = {}
        for tag in re.findall(r'<source\b([^>]*)>', inner):
            src = re.search(r'\bsrc="([^"]*)"', tag)
            kind = re.search(r'\btype="video/([a-z0-9]+)"', tag)
            if src and kind:
                sources[kind.group(1)] = src.group(1)
        for kind in ('mp4', 'webm'):
            if kind not in sources:
                problems.append('%s demo needs a %s source' % (stem, kind))
            else:
                clip_bytes += _asset_bytes(sources[kind], problems)
    if clip_bytes > CLIP_BUDGET:
        problems.append('the demo clips are %d bytes, over the %d byte budget' % (clip_bytes, CLIP_BUDGET))
    # The first screen: images that are not deferred, plus each autoplaying clip and its poster.
    first_view = 0
    for attrs in re.findall(r'<img\b([^>]*)>', html):
        if 'loading="lazy"' in attrs:
            continue
        src = re.search(r'\bsrc="([^"]*)"', attrs)
        if src:
            first_view += _asset_bytes(src.group(1), problems)
    for attrs, inner in videos:
        for src in re.findall(r'<source\b[^>]*\bsrc="([^"]*)"[^>]*\btype="video/mp4"', inner):
            first_view += _asset_bytes(src, problems)
        poster = re.search(r'\bposter="([^"]*)"', attrs)
        if poster:
            first_view += _asset_bytes(poster.group(1), problems)
    if first_view > FIRST_VIEW_BUDGET:
        problems.append('the first screen loads %d bytes of images, over the %d byte budget'
                        % (first_view, FIRST_VIEW_BUDGET))
    with open(os.path.join(ROOT, 'assets', 'script.js')) as f:
        script = f.read()
    if ('video.demo-video' not in script or '.pause()' not in script
            or 'prefers-reduced-motion: reduce' not in script):
        problems.append('assets/script.js must pause video.demo-video under prefers-reduced-motion: reduce')
    if problems:
        sys.exit('landing media check failed:\n  ' + '\n  '.join(problems))


# A root-absolute URL path such as "/guide/find-and-open/" resolves against the host root, not the
# deployed base path, so the site stops working under /library-site/. The lookahead keeps full URLs
# and protocol-relative addresses (//host) out, and the charset skips markup inside string literals
# such as an inline SVG's d="M5.5 15.5...".
SCRIPT_ABS_PATH = re.compile(r'(["\'])(/(?!/)[^\s"\'<>\\]*)\1')


def check_script_paths(path, script):
    """Fail the build if a generated page script contains a root-absolute URL path.

    Scripts must use paths relative to their page (or full https URLs), so old guide links such as
    /guide/#quick-open stay under the deployed base path instead of leaving it for a 404. The service
    worker is not checked: it stores root-absolute page URLs and rebases them against its scope itself.
    """
    absolute = [m.group(2) for m in SCRIPT_ABS_PATH.finditer(script)]
    if absolute:
        sys.exit('build check failed for %s (scripts must not use root-absolute paths):\n  %s'
                 % (path, '\n  '.join(absolute)))


# The accent colors a Mac user can pick in System Settings > Appearance. Button labels follow
# AccentColorText, which is white or black, so each accent must reach 4.5:1 with one of them.
MACOS_ACCENTS = [('Red', '#ff5257'), ('Orange', '#ff9f0a'), ('Yellow', '#ffd60a'), ('Green', '#30d158'),
                 ('Blue', '#0a84ff'), ('Purple', '#bf5af2'), ('Pink', '#ff375f'), ('Graphite', '#8e8e93')]


def luminance(color):
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
              for c in (int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(a, b):
    lighter, darker = sorted((luminance(a), luminance(b)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def check_accent_contrast(css):
    """Fail the build if the accent cannot keep button labels at 4.5:1 contrast.

    The accent follows AccentColor where the browser supports it, and its label follows
    AccentColorText, so a Mac user can pick any accent and still get a legible label. Each fallback
    accent/on-accent pair in src/styles.css must reach 4.5:1 on its own, and --accent must stay wired
    to AccentColor so the accent follows the system.
    """
    problems = []
    for name, accent in MACOS_ACCENTS:
        best = max(contrast_ratio(accent, '#ffffff'), contrast_ratio(accent, '#000000'))
        if best < 4.5:
            problems.append('%s accent %s: the best label contrast is %.2f:1' % (name, accent, best))
    if not re.search(r'--accent\s*:\s*AccentColor', css) or not re.search(r'--on-accent\s*:\s*AccentColorText', css):
        problems.append('--accent must follow AccentColor and --on-accent must follow AccentColorText')
    for block in re.findall(r'\{([^{}]*)\}', css, re.S):
        tokens = dict(re.findall(r'--([a-z0-9-]+)\s*:\s*([^;}]+)', block))
        accent, on_accent = tokens.get('accent', '').strip(), tokens.get('on-accent', '').strip()
        if accent.startswith('#') and on_accent.startswith('#'):
            ratio = contrast_ratio(accent, on_accent)
            if ratio < 4.5:
                problems.append('accent %s with label %s is %.2f:1' % (accent, on_accent, ratio))
    if problems:
        sys.exit('accent contrast check failed:\n  ' + '\n  '.join(problems))


# The header draws its icon at 22x22 on every page, so a 44x44 copy covers a 2x display. icon.png stays at 256x256
# for the favicon, the apple-touch icon, and the social cards. The landing support badge draws at 217x60.
HEADER_ICON = 'assets/icon-44.png'
HEADER_ICON_MAX_BYTES = 4 * 1024
SUPPORT_BADGE = 'assets/buy_me_a_coffee.webp'
SUPPORT_BADGE_MAX_BYTES = 10 * 1024


def check_image_sizes():
    """Fail the build if the header icon or the landing support badge grows past the size the page draws.

    Both ship at several times their drawn size otherwise. The header icon is a 44x44 copy of icon.png, so it
    stays sharp on a 2x display at 22x22, and the badge is a 434x120 copy of the 1090x306 art, for 217x60.
    """
    problems = []
    for path, limit in ((HEADER_ICON, HEADER_ICON_MAX_BYTES), (SUPPORT_BADGE, SUPPORT_BADGE_MAX_BYTES)):
        size = os.path.getsize(os.path.join(ROOT, path))
        if size > limit:
            problems.append('%s is %d bytes, over the %d byte limit' % (path, size, limit))
    if problems:
        sys.exit('image size check failed:\n  ' + '\n  '.join(problems))


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


# Generated pages live at the site root and in folders such as guide/ and whats-new/. These folders hold
# sources, assets, and tooling instead, so an .html file in them is not a page.
SITE_SKIP_DIRS = {'.git', 'src', 'content', 'tools', 'assets'}


def remove_orphan_pages(rendered):
    """Delete generated .html files that the sources no longer render.

    Pages are only ever added, so a renamed guide group or a removed release page used to stay on disk and
    stay published even though the sitemap left it out. The generated set is every rendered page plus the
    hand-maintained index.html; any other .html outside the source folders is an orphan. Only .html files
    are touched, so hand-maintained top-level files such as CNAME, _headers, and .nojekyll stay put.
    """
    keep = {'index.html'} | {p.lstrip('/') for p in rendered}
    orphans = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SITE_SKIP_DIRS and not d.startswith('.')]
        for name in filenames:
            if not name.endswith('.html'):
                continue
            rel = os.path.relpath(os.path.join(dirpath, name), ROOT).replace(os.sep, '/')
            if rel not in keep:
                orphans.append(rel)
    for rel in sorted(orphans):
        os.remove(os.path.join(ROOT, rel))
    return orphans


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


# The guide index page. Its redirect script's map is written relative to this page's folder.
GUIDE_INDEX_PATH = '/guide/index.html'


def write_guide_redirect(paths):
    """Writes assets/guide-redirect.js for the guide index: a link with a section's anchor moves to that
    section's group page. It is a file, not an inline script, because the CSP in _headers blocks inline scripts.

    The map's paths are relative to the guide index, so /guide/#quick-open replaces to
    find-and-open/#quick-open and stays under the deployed base path instead of the host root.
    """
    base = GUIDE_INDEX_PATH.rsplit('/', 1)[0] + '/'
    relative = {sid: url[len(base):] if url.startswith(base) else url for sid, url in paths.items()}
    body = ('(function(){var map=' + script_json(relative) + ';var id=location.hash.slice(1);'
            'if(id&&Object.prototype.hasOwnProperty.call(map,id)){location.replace(map[id]+"#"+id);}})();\n')
    with open(os.path.join(ROOT, 'assets', 'guide-redirect.js'), 'w') as f:
        f.write(body)
    check_script_paths('/assets/guide-redirect.js', body)


def path_key(path):
    return path.replace('index.html', '')


def page_urls(rendered):
    """Every page URL in the built site, apart from 404.html, in sitemap order.

    The rendered pages are the source of truth, plus the hand-maintained landing page. The fixed top-level
    pages keep the order in SITE_PATHS; the guide group and release pages follow, sorted. Both sitemap.xml
    and the service worker's page list come from here, so they cannot drift apart or keep a removed page.
    """
    urls = {path_key(p) for p in rendered if p != '/404.html'}
    urls.add('/')
    return [p for p in SITE_PATHS if p in urls] + sorted(urls - set(SITE_PATHS))


def check_sitemap_matches_service_worker():
    """Fail the build unless sw.js lists the same pages as sitemap.xml, apart from 404.html.

    The service worker keeps a PAGES list so activate can drop cached pages that the sources no longer
    render. A page that is in one list but not the other would stay published or stay cached.
    """
    with open(os.path.join(ROOT, 'sitemap.xml')) as f:
        sitemap = set(re.findall(r'<loc>https://deansasek\.github\.io/library-site(/[^<]*)</loc>', f.read()))
    with open(os.path.join(ROOT, 'sw.js')) as f:
        match = re.search(r'^var PAGES = (\[.*?\]);$', f.read(), re.M)
    if not match:
        sys.exit('build check failed: sw.js must list the site pages in PAGES')
    pages = set(json.loads(match.group(1)))
    if pages != sitemap:
        problems = []
        if pages - sitemap:
            problems.append('in sw.js but not sitemap.xml: ' + ', '.join(sorted(pages - sitemap)))
        if sitemap - pages:
            problems.append('in sitemap.xml but not sw.js: ' + ', '.join(sorted(sitemap - pages)))
        sys.exit('build check failed: sw.js and sitemap.xml list different pages:\n  ' + '\n  '.join(problems))


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


# The precache is the shell only: the assets, the home page, and the 404 fallback. Guide pages are left out
# because the fetch handler caches each page on first navigation. The search index is left out too: at ~52 KB
# it is larger than the headroom under the first-install budget, and script.js fetches it when search is used.
SW_PRECACHE_ASSETS = ['assets/styles.css', 'assets/script.js', 'assets/guide-redirect.js', 'assets/icon.png',
                      'assets/icon-44.png', 'manifest.webmanifest']
SW_PRECACHE_PAGES = ['', '404.html']
# The first install must stay under 100 KB, and changing one page must not make a returning visitor download
# more than 50 KB (the page itself, plus the page cache when the page is precached).
SW_INSTALL_BUDGET = 100 * 1024
SW_PAGE_BUDGET = 50 * 1024

SW_TEMPLATE = """// Generated by tools/build.py. Keeps the shell readable offline. Pages are network first with a short timeout,
// so readers get the newest version while they are online, and the cached copy when the network stalls.
// The shell assets are precached; the search index and images are fetched on first use and kept for offline
// reading. The asset and page caches are versioned separately, so a page edit does not download the asset set again.
var ASSET_CACHE = "assets-%(asset_version)s";
var PAGE_CACHE = "pages-%(page_version)s";
var RUNTIME_CACHE = "runtime";
var PRECACHE_ASSETS = %(assets)s;
var PRECACHE_PAGES = %(pages)s;
var PAGES = %(page_list)s;
var SHELL_ASSETS = PRECACHE_ASSETS.map(function (u) { return new URL(u, location.href).pathname; });
// How long a navigation waits on the network before the cached page is served instead. Kept under the 1.5 second
// budget the issue sets for showing a cached page, so the wait is the timeout and not however long the network takes.
var NETWORK_TIMEOUT = 1200;

function precache(name, urls) {
  return caches.open(name).then(function (cache) {
    // The cache name is a hash of its files, so a cache that already holds every entry is complete. Skipping
    // the copy keeps a page edit from downloading assets whose cache did not change.
    return Promise.all(urls.map(function (u) { return cache.match(u); })).then(function (hits) {
      if (hits.every(Boolean)) { return; }
      return cache.addAll(urls.map(function (u) { return new Request(u, { cache: "reload" }); }));
    });
  });
}

function prunePageCache() {
  // A page the build no longer renders must not stay in the page cache and be served offline. PAGES is the
  // same page set as sitemap.xml, apart from 404.html, which is precached as the offline fallback.
  var keep = PAGES.map(function (p) { return new URL("." + p, self.registration.scope).href; })
    .concat(PRECACHE_PAGES.map(function (p) { return new URL(p || "./", self.registration.scope).href; }));
  return caches.open(PAGE_CACHE).then(function (cache) {
    return cache.keys().then(function (requests) {
      return Promise.all(requests.filter(function (request) {
        var url = new URL(request.url);
        url.search = "";
        return keep.indexOf(url.href) === -1;
      }).map(function (request) { return cache.delete(request); }));
    });
  });
}

self.addEventListener("install", function (event) {
  // Reload bypasses the browser's HTTP cache, so each new version precaches the files from the current deploy.
  event.waitUntil(Promise.all([
    precache(ASSET_CACHE, PRECACHE_ASSETS),
    precache(PAGE_CACHE, PRECACHE_PAGES)
  ]).then(function () { return self.skipWaiting(); }));
});

self.addEventListener("activate", function (event) {
  var keep = [ASSET_CACHE, PAGE_CACHE, RUNTIME_CACHE];
  event.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return keep.indexOf(k) === -1; }).map(function (k) { return caches.delete(k); }));
  }).then(prunePageCache).then(function () { return self.clients.claim(); }));
});

// Stores a fresh page under its query-free URL, but only when the body differs from what is already cached,
// so a repeat navigation to an unchanged page performs no cache write.
function store(cache, key, cachedBody, response) {
  if (!response || !response.ok) { return Promise.resolve(); }
  return response.clone().text().then(function (fresh) {
    var unchanged = cachedBody ? cachedBody.then(function (old) { return old === fresh; }) : Promise.resolve(false);
    return unchanged.then(function (same) { if (!same) { return cache.put(key, response.clone()); } });
  }).catch(function () {});
}

self.addEventListener("fetch", function (event) {
  var request = event.request;
  if (request.method !== "GET" || new URL(request.url).origin !== location.origin) { return; }
  if (request.mode === "navigate") {
    // Pages are cached without their query string, so the cache holds one entry per page, not per URL.
    var key = new URL(request.url);
    key.search = "";
    event.respondWith(caches.open(PAGE_CACHE).then(function (cache) {
      return cache.match(key.href).then(function (hit) {
        // The cached body is read up front, so it can still be compared once the copy has been handed to the page.
        var cachedBody = hit ? hit.clone().text() : null;
        var timer;
        var network = fetch(request).then(function (response) { clearTimeout(timer); return response; },
                                       function () { clearTimeout(timer); return null; });
        // Race the network against a short timeout, so a stalled connection cannot hold up a cached page.
        var stalled = new Promise(function (resolve) {
          timer = setTimeout(function () { resolve(null); }, NETWORK_TIMEOUT);
        });
        return Promise.race([network, stalled]).then(function (response) {
          if (response) {
            // The network answered in time: refresh the cache only if the page changed, then show it.
            return store(cache, key.href, cachedBody, response).then(function () { return response; });
          }
          if (!hit) {
            // Nothing is cached, so the reader waits for the network rather than getting the 404 page early.
            return network.then(function (slow) {
              if (!slow) { return cache.match(new URL("404.html", self.registration.scope).href); }
              return store(cache, key.href, cachedBody, slow).then(function () { return slow; });
            });
          }
          // The network is slow: serve the cached page now and keep the worker alive to refresh the cache when a
          // late answer arrives.
          event.waitUntil(network.then(function (slow) { return store(cache, key.href, cachedBody, slow); }));
          return hit;
        });
      });
    }));
    return;
  }
  if (SHELL_ASSETS.indexOf(new URL(request.url).pathname) !== -1) {
    event.respondWith(caches.open(ASSET_CACHE).then(function (cache) {
      return cache.match(request).then(function (hit) { return hit || fetch(request); });
    }));
    return;
  }
  // The search index and images are not in the install set. Fetch them fresh when online, and keep a copy so
  // they are still available offline after the first use.
  event.respondWith(caches.open(RUNTIME_CACHE).then(function (cache) {
    return fetch(request).then(function (response) {
      if (response.ok) { cache.put(request, response.clone()); }
      return response;
    }).catch(function () { return cache.match(request); });
  }));
});
"""


def sw_source_path(rel):
    """The file on disk for one precache entry: a directory URL (or the home page) maps to its index.html."""
    rel = rel.lstrip('/')
    return rel + 'index.html' if rel == '' or rel.endswith('/') else rel


def sw_digest(entries):
    """A short hash of the named files, so an unchanged set keeps its version and its cache is not reinstalled."""
    digest = hashlib.sha256()
    for rel in entries:
        with open(os.path.join(ROOT, sw_source_path(rel)), 'rb') as f:
            digest.update(rel.encode() + f.read())
    return digest.hexdigest()[:12]


def sw_urls(entries):
    """The precache URLs, with the home page written as ./ so it resolves to the site root."""
    return json.dumps(['./' if r == '' else r for r in entries])


def write_service_worker(urls):
    """Writes sw.js at the site root.

    The shell is precached in two caches with separate versions, so a page edit installs a new page cache
    without reinstalling the asset cache. The build fails when the first install would exceed the install
    budget, or when changing one page would make a returning visitor download more than the per-edit budget.
    The page set comes from the rendered pages, not a disk scan, so a page that the sources drop cannot
    linger in the worker.
    """
    precache = SW_PRECACHE_ASSETS + SW_PRECACHE_PAGES
    total = sum(os.path.getsize(os.path.join(ROOT, sw_source_path(r))) for r in precache)
    if total > SW_INSTALL_BUDGET:
        sys.exit('build check failed: the service worker precaches %d bytes, over the %d KB first-install budget'
                 % (total, SW_INSTALL_BUDGET // 1024))
    # A page that is not precached is fetched on its own when a reader opens it. Changing a precached page
    # also installs the other precached pages, because the page cache gets a new version. Check both.
    page_cache = sum(os.path.getsize(os.path.join(ROOT, sw_source_path(r))) for r in SW_PRECACHE_PAGES)
    precached = {sw_source_path(r) for r in SW_PRECACHE_PAGES}
    for url in urls:
        rel = sw_source_path(url)
        cost = os.path.getsize(os.path.join(ROOT, rel)) + (page_cache if rel in precached else 0)
        if cost > SW_PAGE_BUDGET:
            sys.exit('build check failed: changing %s would make a returning visitor download %d bytes, '
                     'over the %d KB page-edit budget' % (rel, cost, SW_PAGE_BUDGET // 1024))
    body = SW_TEMPLATE % {'asset_version': sw_digest(SW_PRECACHE_ASSETS),
                          'page_version': sw_digest(SW_PRECACHE_PAGES),
                          'assets': sw_urls(SW_PRECACHE_ASSETS),
                          'pages': sw_urls(SW_PRECACHE_PAGES),
                          'page_list': json.dumps(urls)}
    if 'cache: "reload"' not in body:
        sys.exit('build check failed: sw.js must precache with cache: "reload" so a new version cannot pin '
                 'stale files from the HTTP cache')
    with open(os.path.join(ROOT, 'sw.js'), 'w') as f:
        f.write(body)


def build_all(check=False):
    global REVIEWED_LABEL, REVIEWED_VERSION, REVIEWED_ISO
    check_pages_reachable()
    check_app_docs()
    check_accent_contrast(open(os.path.join(ROOT, 'src', 'styles.css')).read())
    check_image_sizes()
    import importlib.util
    spec = importlib.util.spec_from_file_location('pages', os.path.join(ROOT, 'content', 'pages.py'))
    pages = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pages)
    # The app's docs at the pinned commit, and the Markdown converter: so a page can be written from the app's own
    # words instead of a second copy that drifts.
    pages.to_html = markdown
    pages.app_doc = app_doc
    pages.app_doc_ref = app_doc_ref
    reviewed_on = pages.REVIEWED_DATE or TODAY
    REVIEWED_LABEL = reviewed_on.strftime('%B %d, %Y').replace(' 0', ' ')
    REVIEWED_VERSION = pages.REVIEWED_VERSION
    REVIEWED_ISO = reviewed_on.isoformat()
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
    check_sitemap_declared(['/index.html'] + [p for p in rendered if p != '/404.html'])
    for rel in remove_orphan_pages(rendered):
        print('removed orphan page: ' + rel)
    check_install_command(pages.INSTALL_COMMAND)
    check_landing_privacy()
    css = open(os.path.join(ROOT, 'src', 'styles.css')).read()
    open(os.path.join(ROOT, 'assets', 'styles.css'), 'w').write(minify_css(css))
    js = open(os.path.join(ROOT, 'src', 'script.js')).read()
    js = '\n'.join(l.strip() for l in js.splitlines() if l.strip() and not l.strip().startswith('//'))
    open(os.path.join(ROOT, 'assets', 'script.js'), 'w').write(js + '\n')
    check_landing_media()
    check_script_paths('/assets/script.js', js)
    urls = page_urls(rendered)
    # Each URL carries its own real date (a release's date on a What's new page, the review date elsewhere),
    # not the build date, so a rebuild that changes nothing writes the same sitemap.
    release_dates = {r['version'].replace('.', '-'): r['date'] for r in pages._release_records()}
    sitemap = ''
    for u in urls:
        stamp = sitemap_lastmod(u, release_dates, pages.REVIEWED_DATE)
        lastmod = f'    <lastmod>{stamp}</lastmod>\n' if stamp else ''
        sitemap += f'  <url>\n    <loc>https://deansasek.github.io/library-site{u}</loc>\n{lastmod}  </url>\n'
    open(os.path.join(ROOT, 'sitemap.xml'), 'w').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + sitemap + '</urlset>\n')
    write_service_worker(urls)
    check_sitemap_matches_service_worker()
    if check:
        check_release(pages.REVIEWED_VERSION)


if __name__ == '__main__':
    if '--update-app-docs' in sys.argv:
        rest = [a for a in sys.argv[1:] if a != '--update-app-docs']
        update_app_docs(rest[0] if rest else None)
    else:
        build_all(check='--check-release' in sys.argv)
        print('built')

