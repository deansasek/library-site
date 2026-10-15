#!/usr/bin/env python3
"""Writes content/releases.json from the Library app's published GitHub releases. Run from the repository root.

Every published release is listed, patch releases included. Drafts and pre-releases are left out. The build reads
this file, so it never needs the network. The sync workflow runs this and then the build.
"""
import datetime, json, os, re, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = 'https://api.github.com/repos/deansasek/library/releases?per_page=100'
OUT = os.path.join(ROOT, 'content', 'releases.json')


def notes(body):
    """The release's bullet points, with the author and pull request links GitHub adds removed."""
    items = []
    for line in (body or '').splitlines():
        m = re.match(r'^\s*[*-]\s+(.*)$', line)
        if not m:
            continue
        text = re.sub(r'\s+by @\S+\s+in\s+\S+$', '', m.group(1)).strip()
        text = re.sub(r'\s+in\s+https?://\S+$', '', text).strip()
        if text:
            items.append(text)
    return items


def main():
    req = urllib.request.Request(API, headers={'User-Agent': 'library-site-sync', 'Accept': 'application/vnd.github+json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        releases = json.load(r)
    out = []
    for r in releases:
        if r.get('draft') or r.get('prerelease'):
            continue
        tag = r['tag_name']
        published = datetime.datetime.strptime(r['published_at'], '%Y-%m-%dT%H:%M:%SZ').date()
        out.append({'tag': tag, 'version': tag.lstrip('v'), 'date': published.isoformat(),
                    'url': r['html_url'], 'notes': notes(r.get('body'))})
    out.sort(key=lambda x: [int(p) for p in x['version'].split('.')], reverse=True)
    with open(OUT, 'w') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f'wrote {len(out)} releases to {os.path.relpath(OUT, ROOT)}')


if __name__ == '__main__':
    main()
