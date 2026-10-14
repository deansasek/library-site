# getlibrary.app

Static landing page for Library, a macOS app. One HTML page, one stylesheet, no build step and no JavaScript.

## Preview locally

```sh
cd ~/src/library-site
python3 -m http.server 8000
```

Then open http://localhost:8000.

## Deploy

Any static host works. Upload the folder contents (`index.html`, `styles.css`, `assets/`, `CNAME`) to the host's web root.

The `CNAME` file contains `getlibrary.app`, so hosts that support custom domains (GitHub Pages, Netlify, Cloudflare Pages) will bind the domain to the site. Point the domain's DNS at the host as that host documents.
