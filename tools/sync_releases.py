#!/usr/bin/env python3
"""Writes content/releases.json from the Library app's published GitHub releases. Run from the repository root.

Every published release is listed, patch releases included. Drafts and pre-releases are left out. The build reads
this file, so it never needs the network. The sync workflow runs this and then the build.
"""
import datetime, json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = 'https://api.github.com/repos/deansasek/library/releases?per_page=100'
OUT = os.path.join(ROOT, 'content', 'releases.json')
HEADERS = {'User-Agent': 'library-site-sync', 'Accept': 'application/vnd.github+json'}


def next_page(link):
    """The URL of the next page, from a GitHub Link header, or None on the last page."""
    for part in (link or '').split(','):
        m = re.match(r'\s*<([^>]+)>\s*;\s*rel="next"', part)
        if m:
            return m.group(1)
    return None


def fetch_releases():
    """Every page of the releases, following the Link header. GitHub returns at most 100 per page."""
    releases, url = [], API
    while url:
        with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=30) as r:
            releases.extend(json.load(r))
            url = next_page(r.headers.get('Link'))
    return releases


def version_key(version):
    """The numbers in a version, in order, so 1.10.0 sorts after 1.9.0. A version with no numbers sorts last."""
    return [int(p) for p in re.findall(r'\d+', version)]


def existing_releases():
    """The releases the current file lists, newest first. A missing or unreadable file counts as none."""
    try:
        with open(OUT) as f:
            return json.load(f)
    except (OSError, ValueError):
        return []


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
    out = []
    for r in fetch_releases():
        if r.get('draft') or r.get('prerelease'):
            continue
        tag = r['tag_name']
        published = datetime.datetime.strptime(r['published_at'], '%Y-%m-%dT%H:%M:%SZ').date()
        out.append({'tag': tag, 'version': tag.lstrip('v'), 'date': published.isoformat(),
                    'url': r['html_url'], 'notes': notes(r.get('body'))})
    # Compare by tag, not by count: a release published in the same window as one that was removed keeps the count
    # equal, and a short response is told apart from a real removal by how much of the known list is missing.
    existing = existing_releases()
    fetched = {r['tag'] for r in out}
    missing = [r for r in existing if r['tag'] not in fetched]
    newly_missing = [r for r in missing if not r.get('removed')]
    allow_removal = os.environ.get('SYNC_ALLOW_REMOVAL') == '1'
    if newly_missing and not allow_removal and len(newly_missing) > 2:
        tags = ', '.join(r['tag'] for r in newly_missing)
        sys.exit(f'refusing to write {len(out)} releases: {len(newly_missing)} of the {len(existing)} in '
                 f'{os.path.relpath(OUT, ROOT)} are missing from GitHub ({tags}). '
                 'Treating this as a partial response. Run the workflow by hand with allow_removal to drop them.')
    if missing:
        tags = ', '.join(r['tag'] for r in missing)
        if allow_removal:
            print(f'dropping {len(missing)} release(s) missing from GitHub: {tags}')
        else:
            # Keep a removed release in the file, flagged, so its date, notes, and URL are not lost. Once it is
            # flagged, later syncs carry it forward quietly instead of failing or flagging it again.
            out.extend({**r, 'removed': True} for r in missing)
            if newly_missing:
                print(f'keeping {len(newly_missing)} release(s) missing from GitHub, marked removed: '
                      f'{", ".join(r["tag"] for r in newly_missing)}')
    out.sort(key=lambda x: version_key(x['version']), reverse=True)
    with open(OUT, 'w') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f'wrote {len(out)} releases to {os.path.relpath(OUT, ROOT)}')


if __name__ == '__main__':
    main()
