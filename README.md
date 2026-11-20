# nevadainformation.com

Static guide to every Nevada city, census-designated town, county and region. Sister site to oregoninformation.com.

The deployable site is in **`public/`** (committed, so any host can serve it as-is). Everything that makes it is in `build/`.

## Build

```
python3 build/assemble.py       # build/sources/*.json  ->  build/data/places.json, counties.json
python3 build/generate_site.py  # build/data + content  ->  public/
python3 build/check_site.py     # internal links, title/description lengths (add --external to test outside links)
```

No dependencies beyond Python 3.

## Where things live

| File | What it holds |
|---|---|
| `build/content.py` | Regions, utilities, school districts, transit, statewide links, attractions and taglines for larger towns |
| `build/pages.py` | Hand-written pages: home, Nevada facts, moving guide, visiting guide |
| `build/generate_site.py` | Templates for city/town, county, region, A-Z, ZIP and area-code pages; sitemap, robots, `.htaccess`, `_headers` |
| `build/site.css` | All styles |
| `build/sources/` | Raw data: Census (2010/2020, Vintage 2024), Wikidata, Wikipedia text, Commons photos |
| `build/data/` | Assembled data, plus ZIP-to-place matches, NCES schools and county boundaries |

## Data refresh

Wikimedia throttles cloud IPs, so Wikipedia text and Commons photos are fetched by the
**Refresh Wikipedia and Commons data** GitHub Action (`.github/workflows/refresh-sources.yml`). It runs weekly,
on changes to the fetch/assemble scripts, or by hand from the Actions tab, then rebuilds `public/` and commits.

## Hosting

- **Cloudflare Pages:** no build command, output directory `public`.
- **Apache (VPS):** point the document root at `public/` (or rsync it to `public_html`). `public/.htaccess` handles
  https/www redirects and caching.

## To do before launch

- Create a GA4 property and set `ANALYTICS_ID` in `build/generate_site.py`.
- Set up email for `contact@nevadainformation.com`.
- Submit the sitemap to Search Console and Bing; IndexNow key file is `public/60953573236b4171a9f01357b86ed4ba.txt`.
