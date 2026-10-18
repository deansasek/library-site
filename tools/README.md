# Building the site

`build.py` writes the site from the sources in `src/` and `content/`. Run it from the repository root.

```sh
python3 tools/build.py
```

It writes the HTML pages, `assets/styles.css`, `assets/script.js`, `assets/search-index.json`, `sitemap.xml`, and `sw.js`. Run it again after every change to the sources.

`robots.txt` is edited by hand; the build does not write it.

To check the latest release against the version the docs were reviewed for, add `--check-release`. It prints a warning if they differ. A network failure only prints a note.

## The app's docs

Some of the site's words come from the app's own documentation rather than from `content/pages.py`, so the two cannot drift. The privacy page's file table is built from `docs/privacy.md` in [the app repository](https://github.com/deansasek/library).

`content/appdocs/` holds a copy of those documents, the images they show, and `REF`, the full app commit they came from. The copy is committed, so a build needs no network and always renders the same text. To refresh it after the app's docs change:

```sh
python3 tools/build.py --update-app-docs          # the app's current main
python3 tools/build.py --update-app-docs v1.6.8   # or one tag
```

It reads from a sibling checkout of the app repository when there is one, and clones otherwise. Commit whatever changes, so the pin and the text move together.

The build fails when `content/appdocs/REF` is missing, when a document points at an image or another document that is not vendored beside it, or when the app's privacy document has no file table to build from.

## Previewing locally

```sh
python3 -m http.server 8000
```

Then open http://localhost:8000. The server serves each folder's `index.html`, so links such as `guide/` work as clean URLs. Preview through the server; opening the files directly from disk is not supported.
