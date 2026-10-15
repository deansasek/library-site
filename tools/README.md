# Building the site

`build.py` writes the site from the sources in `src/` and `content/`. Run it from the repository root.

```sh
python3 tools/build.py
```

It writes the HTML pages, `assets/styles.css`, `assets/script.js`, `assets/search-index.json`, `sitemap.xml`, and `robots.txt`. Run it again after every change to the sources.

To check the latest release against the version the docs were reviewed for, add `--check-release`. It prints a warning if they differ. A network failure only prints a note.

## Previewing locally

```sh
python3 -m http.server 8000
```

Then open http://localhost:8000. Because every internal link is relative, the site also works when you open `index.html` directly from disk.
