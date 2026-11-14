#!/usr/bin/env python3
"""Nevada Information - data assembler.

Combines the raw downloads in build/sources/ (Census, Wikidata, Wikipedia, Commons)
into build/data/places.json and build/data/counties.json, which the site generator reads.

Raw sources (re-download with build/fetch_sources.py):
  census_raw.json   2020 Census redistricting counts (P1), 2010 Gazetteer counts, Vintage 2024 estimates,
                    2020 Gazetteer place list (land area, internal point)
  county_gaz.json   2020 Gazetteer counties
  wd.json           Wikidata per GNIS ID: Wikipedia article, image, official website, inception, elevation, seat
  wiki.json         Wikipedia lead text (REST API)
  images.json       Wikimedia Commons photos per place (author + license)
Run: python3 build/assemble.py
"""
import json, os, re
from urllib.parse import unquote

HERE = os.path.dirname(os.path.abspath(__file__))
SRC, DATA = os.path.join(HERE, 'sources'), os.path.join(HERE, 'data')


def load(name, default=None):
    p = os.path.join(SRC, name)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else default


raw = load('census_raw.json')
wd = load('wd.json', {})
wiki = load('wiki.json', {})
images = load('images.json', {})
cgaz = load('county_gaz.json', [])
geo = json.load(open(os.path.join(DATA, 'nevada_counties_geo.json')))['counties']

# Hand-checked corrections: values Wikidata gets wrong or lacks.
WEBSITE_FIX = {}
# Wikidata still lists retired Clark County town-advisory-board pages (all 404) and some mismatched ones; drop them.
DROP_SITE = ('clarkcountynv.gov/depts/', 'town-liaison')
TZ_OVERRIDE = {'West Wendover': ['America/Denver'], 'Jackpot': ['America/Denver']}  # both keep Mountain Time by local practice


def inside(lon, lat, ring):
    c = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]; xj, yj = ring[j]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi + 1e-12) + xi:
            c = not c
        j = i
    return c


def county_of(lon, lat):
    for k in geo:
        if any(inside(lon, lat, r) for r in k['rings']):
            return k['name']
    # fall back to the nearest ring vertex
    best = min(((x - lon) ** 2 + (y - lat) ** 2, k['name']) for k in geo for r in k['rings'] for x, y in r)
    return best[1]


def wiki_for(item):
    art = item.get('article')
    if not art: return {}, None
    t = unquote(art.split('/wiki/')[1])
    return wiki.get(t, {}), art


def commons_main(item):
    img = item.get('image')
    if not img: return None, None
    f = unquote(img.split('Special:FilePath/')[-1]).replace('_', ' ')
    from urllib.parse import quote
    return f'https://commons.wikimedia.org/wiki/Special:FilePath/{quote(f.replace(" ", "_"))}?width=960', f


def year(v):
    m = re.match(r'^-?(\d{4})', v or '')
    return m.group(1) if m else ''


def clean_name(n):
    return re.sub(r' (city|CDP)$', '', n)


places = []
for p in raw['places']:
    g = p['GEOID']; gn = str(int(p['ANSICODE']))
    item = wd.get(gn, {})
    name = clean_name(p['NAME'])
    lat, lon = float(p['INTPTLAT']), float(p['INTPTLONG'])
    w, art = wiki_for(item)
    img, imgfile = commons_main(item)
    pop20 = raw['pop20'].get(g, [0])[0]
    pop10 = raw['pop10'].get(g, [None])[0]
    est = raw['est'].get(g, [None])[0]
    change = ''
    if pop10:
        change = f'{(pop20 - pop10) / pop10 * 100:+.1f}%'
    places.append({
        'name': name, 'geoid': g, 'type': 'city' if p['LSAD'] in ('25', '00') else 'cdp',
        'county': county_of(lon, lat), 'pop2020': pop20, 'pop2010': pop10, 'change': change, 'est2024': est,
        'land_sqmi': float(p['ALAND_SQMI']), 'water_sqmi': float(p['AWATER_SQMI'] or 0), 'lat': lat, 'lon': lon,
        'incorporated': year(item.get('inception')) if p['LSAD'] in ('25', '00') else '',
        'elev_ft': round(float(item['elev']) * 3.28084) if item.get('elev') else None,
        'website': '' if any(d in item.get('website', '') for d in DROP_SITE) else WEBSITE_FIX.get(name, item.get('website', '')), 'wiki_url': art or '',
        'summary': w.get('extract') or w.get('summary') or '', 'image': img, 'image_file': imgfile,
        'photos': images.get(gn, []), 'tz_override': TZ_OVERRIDE.get(name),
    })

pops = {k: v for k, v in raw['pop20'].items() if len(k) == 5}
counties = []
for r in cgaz:
    g = r['GEOID']; gn = str(int(r['ANSICODE']))
    item = wd.get(gn, {})
    name = re.sub(r' County$', '', r['NAME'])
    w, art = wiki_for(item)
    img, imgfile = commons_main(item)
    counties.append({
        'name': name, 'geoid': g, 'pop2020': pops.get(g, [0])[0], 'est2024': raw['est'].get(g, [None])[0],
        'land_sqmi': float(r['ALAND_SQMI']), 'lat': float(r['INTPTLAT']), 'lon': float(r['INTPTLONG']),
        'est': year(item.get('inception')), 'seat': item.get('seatLabel', ''), 'website': item.get('website', ''),
        'wiki_url': art or '', 'summary': w.get('extract') or w.get('summary') or '', 'image': img, 'image_file': imgfile,
    })

json.dump(sorted(places, key=lambda x: x['name']), open(os.path.join(DATA, 'places.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
json.dump(sorted(counties, key=lambda x: x['name']), open(os.path.join(DATA, 'counties.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(f'{len(places)} places ({sum(p["type"] == "city" for p in places)} cities), {len(counties)} counties; '
      f'{sum(1 for p in places if p["summary"])} place summaries, {sum(1 for p in places if p["photos"])} with photo galleries')
