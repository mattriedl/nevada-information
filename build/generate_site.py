#!/usr/bin/env python3
"""Nevada Information - static site generator.

Reads build/data/*.json (made by build/assemble.py) and build/content.py, and writes the whole
site into public/: home, Nevada facts, moving and visiting guides, 6 region pages, 17 county pages,
a page for every incorporated city and census-designated place, the A-Z directory, ZIP code and
area code pages, about/contact/privacy/advertise, 404, sitemap.xml, robots.txt and server config.

Run from the repo root:  python3 build/generate_site.py
"""
import hashlib, html, json, math, os, re, shutil, sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'public')
sys.path.insert(0, HERE)
from content import REGIONS, REGION_OF, ELECTRIC_COUNTY, ELECTRIC_PLACE, NV_ENERGY, GAS_NORTH_NVE, SCHOOL_DISTRICTS, TRANSIT, L, STATE_LINKS, CUSTOM  # noqa: E402
import pages  # noqa: E402  hand-written long-form pages (home, moving, visiting, Nevada facts)

BASE_URL = 'https://nevadainformation.com'
SITE_NAME = 'Nevada Information'
CONTACT_EMAIL = 'contact@nevadainformation.com'
ANALYTICS_ID = ''          # set to the GA4 measurement ID (G-XXXXXXX) once the property exists
INDEXNOW_KEY = '7f3c2a9e5b1d4c8fa0e6b2d9c4f1a7e3'
YEAR = date.today().year
TODAY = date.today().isoformat()

D = lambda f: json.load(open(os.path.join(HERE, 'data', f), encoding='utf-8'))
PLACES = D('places.json')
COUNTIES = D('counties.json')
ZIPS = D('place_zips.json')
SCHOOLS = D('schools.json')
GEO = D('nevada_counties_geo.json')['counties']
for k in COUNTIES:
    if k['name'] == 'Carson City': k['seat'] = 'Carson City'
COUNTY = {k['name']: k for k in COUNTIES}
STATE_POP2020 = 3104614      # 2020 Census, Nevada (P1_001N)


# ================================================================ helpers
def e(t): return html.escape(str(t), quote=True)
def n(v):
    try: return f'{int(float(v)):,}'
    except (TypeError, ValueError): return ''
def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower().replace("'", '')).strip('-')
def host(u): return re.sub(r'^https?://(www\.)?', '', u or '').rstrip('/')
def ordinal(k): return f"{k}{'th' if 10 <= k % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(k % 10, 'th')}"
EXT = ' target="_blank" rel="noopener"'
def a_ext(url, text): return f'<a href="{e(url)}"{EXT}>{text}</a>'


def miles(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a['lat'], a['lon'], b['lat'], b['lon']))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 3958.8 * 2 * math.asin(math.sqrt(h))


FILLERS = ('Free, independent guide.', 'Sources cited.', 'Updated regularly.', 'Plan a move or a visit.', 'Free guide.', 'With FAQs.')


def fit_desc(*parts):
    """Meta description of 150-160 characters: add parts while they fit, then short fillers to reach 150."""
    out = ''
    for p in parts:
        if not p: continue
        if not out: out = p; continue
        if len(out) + 1 + len(p) <= 160: out += ' ' + p
    if len(out) > 160: out = out[:157].rsplit(' ', 1)[0].rstrip(',;:') + '...'
    for f in FILLERS:
        if len(out) >= 150: break
        if f not in out and len(out) + 1 + len(f) <= 160: out += ' ' + f
    return out


def summary_html(text, limit=1200):
    text = re.sub(r' \(\s*[^)]*?(?:listen|pronounced|;)\s*[^)]*\)', '', text or '')
    text = re.sub(r'\(\s*\)', '', text); text = re.sub(r'\s+([,.;])', r'\1', text)
    out, total = [], 0
    for para in [p.strip() for p in text.split('\n') if p.strip()]:
        if total + len(para) > limit and out: break
        if len(para) > limit:
            cut = para[:limit]; para = cut[:cut.rfind('. ') + 1] if '. ' in cut else cut
        out.append(para); total += len(para)
    return ''.join(f'<p>{e(p)}</p>' for p in out)


def wiki_credit(url):
    return (f'<p class="src">Background adapted from {a_ext(url, "Wikipedia")}, available under '
            f'{a_ext("https://creativecommons.org/licenses/by-sa/4.0/", "CC BY-SA 4.0")}.</p>') if url else ''


# ================================================================ visuals
def ridges(seed, layers=4, w=1200, h=150):
    """Basin-and-Range skyline seeded from the page name: steep, jagged ranges separated by flat basins,
    so each page gets its own set of ridges."""
    hsh = hashlib.sha256(seed.encode()).digest() * 4
    k = [0]
    def r():
        k[0] += 1
        return hsh[k[0] % len(hsh)] / 255
    fills = ['#343a57', '#45416b', '#5d4a86', '#6f8463']
    paths = []
    for L_ in range(layers):
        floor = h * (0.55 + 0.13 * L_)          # basin floor for this layer
        top = h * (0.04 + 0.16 * L_)            # highest summit this layer can reach
        pts, x = [(0, floor)], -60 * r()
        while x < w:
            span = w * (0.16 + 0.16 * r())      # width of one range
            gap = w * (0.02 + 0.06 * r())       # flat basin before it
            x += gap; pts.append((x, floor))
            crest = top + (floor - top) * (0.15 + 0.45 * r())
            n_ = 2 + int(r() * 3)
            for j in range(n_):
                px = x + span * (j + 0.5) / n_ + span * 0.08 * (r() - 0.5)
                py = crest + (floor - crest) * (0.0 if j == n_ // 2 else 0.12 + 0.3 * r())
                pts.append((px, py))
                if j < n_ - 1: pts.append((x + span * (j + 1) / n_, py + (floor - py) * (0.25 + 0.25 * r())))
            x += span; pts.append((x, floor))
        pts += [(w, floor), (w, h), (0, h)]
        paths.append(f'<path d="M{" L".join(f"{max(0, min(w, a)):.0f} {b:.0f}" for a, b in pts)}Z" fill="{fills[L_]}"/>')
    return f'<svg class="ridges" viewBox="0 0 {w} {h}" preserveAspectRatio="none" aria-hidden="true" focusable="false">{"".join(paths)}</svg>'


BBOX = (34.95, 42.05, -120.05, -113.98)


def _xy(lat, lon, w, h, pad=6):
    la0, la1, lo0, lo1 = BBOX
    kx = math.cos(math.radians(38.5))
    sx = (w - 2 * pad) / ((lo1 - lo0) * kx); sy = (h - 2 * pad) / (la1 - la0)
    s = min(sx, sy)
    ox = (w - (lo1 - lo0) * kx * s) / 2; oy = (h - (la1 - la0) * s) / 2
    return (lon - lo0) * kx * s + ox, (la1 - lat) * s + oy


def county_paths(w, h, highlight=(), link=True, up=''):
    out = []
    for k in GEO:
        d = ''.join('M' + ' L'.join('%.1f %.1f' % _xy(y, x, w, h) for x, y in r) + 'Z' for r in k['rings'])
        cls = 'cty on' if k['name'] in highlight else 'cty'
        p = f'<path class="{cls}" d="{d}"><title>{e(k["name"])}{"" if k["name"] == "Carson City" else " County"}</title></path>'
        out.append(f'<a href="/counties/{slug(k["name"])}/">{p}</a>' if link else p)
    return ''.join(out)


def locator_map(lat, lon, label, county):
    w, h = 220, 300
    x, y = _xy(lat, lon, w, h)
    return (f'<figure class="loc"><svg viewBox="0 0 {w} {h}" role="img" aria-label="Map of Nevada showing where {e(label)} is">'
            f'{county_paths(w, h, (county,), link=False)}<circle cx="{x:.1f}" cy="{y:.1f}" r="6" class="dot"/></svg>'
            f'<figcaption>{e(county)}{"" if county == "Carson City" else " County"} highlighted</figcaption></figure>')


def county_map(highlight=(), w=460, h=620, labels=True):
    lab = ''
    if labels:
        for k in COUNTIES:
            if k['name'] in ('Carson City', 'Storey'): continue
            x, y = _xy(k['lat'], k['lon'], w, h)
            lab += f'<text x="{x:.0f}" y="{y:.0f}" class="clab">{e(k["name"])}</text>'
    return (f'<figure class="cmap"><svg viewBox="0 0 {w} {h}" role="img" aria-label="Map of Nevada\'s 17 counties">'
            f'{county_paths(w, h, highlight)}{lab}</svg><figcaption>Select a county to open its guide.</figcaption></figure>')


# ================================================================ page chrome
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Overpass:wght@400;600;800&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap" rel="stylesheet">')
CSS = open(os.path.join(HERE, 'site.css'), encoding='utf-8').read()


def head(title, desc, path, og_type='website', image=None, ld_objs=(), noindex=False):
    url = BASE_URL + path
    ga = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={ANALYTICS_ID}"></script><script>window.dataLayer=window.dataLayer||[];'
          f'function gtag(){{dataLayer.push(arguments);}}gtag("js",new Date());gtag("config","{ANALYTICS_ID}");</script>') if ANALYTICS_ID else ''
    lds = ''.join(f'<script type="application/ld+json">{json.dumps(o, ensure_ascii=False)}</script>' for o in ld_objs)
    img = image or f'{BASE_URL}/assets/og-image.png'
    return (f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{e(title)}</title><meta name="description" content="{e(desc)}">'
            + ('<meta name="robots" content="noindex">' if noindex else '') +
            f'<link rel="canonical" href="{url}"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">'
            f'<meta name="theme-color" content="#1d2433">'
            f'<meta property="og:site_name" content="{SITE_NAME}"><meta property="og:locale" content="en_US"><meta property="og:type" content="{og_type}">'
            f'<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}">'
            f'<meta property="og:image" content="{e(img)}"><meta name="twitter:card" content="summary_large_image">'
            f'{FONTS}<link rel="stylesheet" href="/assets/site.css?v={hashlib.md5(CSS.encode()).hexdigest()[:8]}">{lds}{ga}</head><body>'
            '<a class="skip" href="#main">Skip to content</a>')


NAV = [('Moving', '/moving-to-nevada/'), ('Visiting', '/visit-nevada/'), ('Regions', '/regions/'),
       ('Counties', '/counties/'), ('Cities &amp; towns', '/cities/')]


def header(active=''):
    links = ''.join(f'<li><a href="{u}"{" aria-current=\"page\"" if u == active else ""}>{t}</a></li>' for t, u in NAV)
    return (f'<header class="hd"><div class="wrap hd-in"><a class="logo" href="/"><svg viewBox="0 0 26 32" aria-hidden="true">'
            f'<path d="M1 1h14l10 10v20H1z" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round"/></svg>'
            f'<span>Nevada Information</span></a><nav aria-label="Main"><ul>{links}</ul></nav></div></header>')


def footer(note=''):
    return (f'<footer class="ft"><div class="wrap"><nav aria-label="Footer"><a href="/nevada/">Nevada facts</a><a href="/regions/">Regions</a>'
            f'<a href="/counties/">Counties</a><a href="/cities/">Cities &amp; towns</a><a href="/nevada-zip-codes/">ZIP codes</a>'
            f'<a href="/nevada-area-codes/">Area codes</a><a href="/about/">About</a><a href="/contact/">Contact</a>'
            f'<a href="/privacy/">Privacy</a><a href="/advertise/">Advertise</a></nav>'
            f'<p>&copy; {YEAR} Nevada Information. An independent guide, not affiliated with the State of Nevada.{note}</p></div></footer>'
            + WX_JS + '</body></html>')


def hero(h1, sub='', pills='', seed='', crumbs=None):
    cr = ''
    if crumbs:
        cr = '<nav class="crumbs" aria-label="Breadcrumb">' + ' <span aria-hidden="true">/</span> '.join(
            f'<a href="{u}">{e(t)}</a>' if u else f'<span aria-current="page">{e(t)}</span>' for t, u in crumbs) + '</nav>'
    return (f'<div class="hero"><div class="wrap">{cr}<h1>{h1}</h1>' + (f'<p class="sub">{sub}</p>' if sub else '')
            + (f'<div class="pills">{pills}</div>' if pills else '') + f'</div>{ridges(seed or h1)}</div>')


def crumbs_ld(items):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i, 'name': t, 'item': BASE_URL + u} for i, (t, u) in enumerate(items, 1)]}


def faq_block(fq, title):
    det = ''.join(f'<details><summary>{e(q)}</summary><p>{h or e(a)}</p></details>' for q, a, h in fq)
    ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a, _ in fq]}
    return f'<h2 id="faq">{title}</h2><div class="faq">{det}</div>', ld


def gallery(item, name):
    photos = [p for p in item.get('photos') or [] if p.get('src')]
    skip = ('map', 'locator', 'seal', 'flag', 'logo', 'sign', 'diagram', 'chart', 'grave', 'cemetery')
    photos = [p for p in photos if not any(s in (p['file'] + ' ' + p.get('caption', '')).lower() for s in skip)]
    photos = [p for p in photos if p.get('w', 0) >= p.get('h', 0)][:6]   # landscape only
    if not photos: return ''
    figs = []
    for p in photos:
        cap = re.sub(r'\.(jpe?g|png)$', '', p.get('caption') or p['file'], flags=re.I).strip()
        if len(cap) > 110: cap = cap[:108].rsplit(' ', 1)[0].rstrip(',;:') + '...'
        if re.match(r'^[\w-]*\d{5,}', cap): cap = f'{name}, Nevada'
        credit = e(p.get('artist') or 'Wikimedia Commons') + (f', {e(p["license"])}' if p.get('license') else '')
        figs.append(f'<figure><img src="{e(p["src"])}" alt="{e(cap if name.lower() in cap.lower() else cap + " in " + name + ", Nevada")}" '
                    f'loading="lazy" width="960" height="640"><figcaption>{e(cap)}<small>Photo: {credit} &middot; {a_ext(p["page"], "source")}</small></figcaption></figure>')
    return f'<h2 id="photos">{e(name)} in pictures</h2><div class="gallery">{"".join(figs)}</div>'


# ================================================================ weather (Open-Meteo, no key)
WX_JS = ("<script>(function(){var c={0:'Clear',1:'Mostly clear',2:'Partly cloudy',3:'Overcast',45:'Fog',48:'Freezing fog',51:'Light drizzle',53:'Drizzle',55:'Heavy drizzle',"
         "61:'Light rain',63:'Rain',65:'Heavy rain',71:'Light snow',73:'Snow',75:'Heavy snow',77:'Snow grains',80:'Showers',81:'Heavy showers',82:'Violent showers',"
         "85:'Snow showers',86:'Heavy snow showers',95:'Thunderstorm',96:'Thunderstorm, hail',99:'Thunderstorm, hail'};"
         "document.querySelectorAll('[data-wx]').forEach(function(el){var p=el.dataset.wx.split(',');"
         "fetch('https://api.open-meteo.com/v1/forecast?latitude='+p[0]+'&longitude='+p[1]+'&current=temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m"
         "&daily=temperature_2m_max,temperature_2m_min,weather_code&temperature_unit=fahrenheit&wind_speed_unit=mph&timezone='+encodeURIComponent(p[2])+'&forecast_days=7')"
         ".then(function(r){return r.json()}).then(function(d){var k=d.current,y=d.daily,days=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];"
         "var h='<p class=\"wx-now\"><b>'+Math.round(k.temperature_2m)+'&deg;F</b> '+(c[k.weather_code]||'')+'<span>Wind '+Math.round(k.wind_speed_10m)+' mph &middot; Humidity '+Math.round(k.relative_humidity_2m)+'%</span></p><ol class=\"wx-days\">';"
         "for(var i=1;i<7;i++){var t=new Date(y.time[i]+'T12:00:00');h+='<li><b>'+days[t.getDay()]+'</b><span>'+Math.round(y.temperature_2m_max[i])+'&deg; / '+Math.round(y.temperature_2m_min[i])+'&deg;</span><small>'+(c[y.weather_code[i]]||'')+'</small></li>'}"
         "el.innerHTML=h+'</ol><p class=\"src\">Forecast from <a href=\"https://open-meteo.com/\" target=\"_blank\" rel=\"noopener\">Open-Meteo</a>, loaded when you open this page.</p>'})"
         ".catch(function(){el.innerHTML='<p>Forecast unavailable right now. Try <a href=\"https://forecast.weather.gov/\">weather.gov</a>.</p>'})})})();</script>")


def weather(name, lat, lon, tz):
    return (f'<h2 id="weather">Weather in {e(name)}</h2><div class="wx" data-wx="{lat:.4f},{lon:.4f},{tz}">'
            f'<p>Loading the 7-day forecast&hellip;</p></div>')


# ================================================================ place data helpers
TZ_NAME = {'America/Los_Angeles': 'Pacific Time', 'America/Denver': 'Mountain Time'}


def zips_for(p):
    z = ZIPS.get(p['geoid'], {})
    return z.get('zips', []), (p.get('tz_override') or z.get('timezones') or ['America/Los_Angeles'])


def area_codes(county): return ['702', '725'] if county == 'Clark' else ['775']


def electric(p):
    return ELECTRIC_PLACE.get(p['name']) or ELECTRIC_COUNTY.get(p['county'], [NV_ENERGY])


def gas(county):
    if county in GAS_NORTH_NVE:
        return f'{a_ext(L["nve_gas"], "NV Energy")} in the Reno&ndash;Sparks area, or propane in outlying areas'
    return f'{a_ext(L["southwest_gas"], "Southwest Gas")} where lines reach, otherwise propane'


def place_kind(p):
    if p['name'] == 'Carson City': return 'consolidated city and state capital'
    return 'incorporated city' if p['type'] == 'city' else 'unincorporated town (census-designated place)'


def nearby_high_schools(p, k=4):
    hs = [s for s in SCHOOLS if s['school_level'] == 3 and s.get('school_type') == 1 and not s.get('virtual') and s.get('latitude')
          and (s.get('enrollment') or 0) > 40 and 'CORRECTIONAL' not in (s.get('lea_name') or '')]
    ranked = sorted(((miles(p, {'lat': s['latitude'], 'lon': s['longitude']}), s) for s in hs), key=lambda t: t[0])
    return [(d, s) for d, s in ranked[:k] if d < 40]


def title_case_school(s):
    s = s.title()
    for a, b in ((' J-Shs', ' Jr./Sr. High School'), (' Hs', ' High School'), ("'S", "'s"), (' Jr/Sr', ' Jr./Sr.'), (' Of ', ' of ')): s = s.replace(a, b)
    return s


def county_label(c): return c if c == 'Carson City' else f'{c} County'


def county_link(c): return f'<a href="/counties/{slug(c)}/">{e(county_label(c))}</a>'


def region_link(r): return f'<a href="/regions/{REGIONS[r]["slug"]}/">{e(r)}</a>'


# ================================================================ city / town pages
RANKED = sorted(PLACES, key=lambda x: -x['pop2020'])
RANK = {p['geoid']: i for i, p in enumerate(RANKED, 1)}


def place_title(p, nz):
    nm = p['name']
    z = 'ZIP Code' if nz == 1 else 'ZIP Codes'
    for t in (f'{nm}, Nevada: Population, {z}, Schools & Weather', f'{nm}, Nevada: Population, {z} & Weather',
              f'{nm}, NV: Population, {z} & Weather', f'{nm}, NV: Population & {z}', f'{nm}, Nevada Guide'):
        if len(t) <= 60: return t
    return t


def place_faq(p, near):
    nm, cty = p['name'], p['county']; reg = REGION_OF[cty]; fq = []
    pop = n(p['pop2020'])
    a = f"{nm} had {pop} residents at the 2020 U.S. Census"
    if p.get('pop2010'): a += f" ({'up' if p['pop2020'] >= p['pop2010'] else 'down'} from {n(p['pop2010'])} in 2010)"
    a += '.'
    if p.get('est2024'): a += f" The Census Bureau estimated {n(p['est2024'])} residents in mid-2024."
    fq.append((f'What is the population of {nm}, Nevada?', a, None))
    rk = RANK[p['geoid']]
    a = f"{nm} covers about {p['land_sqmi']:,.1f} square miles of land"
    if p['land_sqmi'] > 0 and p['pop2020']: a += f", about {p['pop2020'] / p['land_sqmi']:,.0f} people per square mile"
    a += '. ' + ('It is the largest place in Nevada by population.' if rk == 1 else
                 f"By 2020 population it ranks {ordinal(rk)} of the {len(PLACES)} cities and census-designated towns in Nevada.")
    fq.append((f'How big is {nm}, Nevada?', a, None))
    a = (f"{nm} is in {county_label(cty)}, in the {reg} region." if cty != 'Carson City'
         else "Carson City is an independent, consolidated city: it is its own county-equivalent and is not part of any county.")
    if p['type'] == 'cdp':
        a += f" It is an unincorporated town, so {county_label(cty)} provides local government services."
    seat = COUNTY[cty]['seat']
    if seat and seat != nm and cty != 'Carson City': a += f" The county seat is {seat}."
    elif seat == nm and cty != 'Carson City': a += f" {nm} is the county seat."
    fq.append((f'What county is {nm}, Nevada in?', a, None))
    zl, tzs = zips_for(p)
    if zl:
        a = (f"The ZIP code covering {nm} is {zl[0]}." if len(zl) == 1 else
             f"ZIP codes that cover part of {nm} include {', '.join(zl[:12])}" + (f" and {len(zl) - 12} more." if len(zl) > 12 else '.'))
        a += ' Mailing addresses do not always match town boundaries, so confirm a specific address with USPS.'
        fq.append((f'What is the ZIP code for {nm}, Nevada?', a, None))
    fq.append((f'What area code does {nm} use?', (
        f"{nm} uses area codes 702 and 725, which overlay each other across Clark County, so local calls need all ten digits." if cty == 'Clark'
        else f"{nm} uses area code 775, which covers all of Nevada outside Clark County."), None))
    if tzs != ['America/Los_Angeles']:
        fq.append((f'What time zone is {nm} in?', f"{nm} keeps {' / '.join(TZ_NAME.get(t, t) for t in tzs)}, unlike most of Nevada, which is on Pacific Time.", None))
    for hub in ('Las Vegas', 'Reno'):
        if nm == hub: continue
        h = next(x for x in PLACES if x['name'] == hub)
        d = miles(p, h)
        if d < 450:
            fq.append((f'How far is {nm} from {hub}?', f"{nm} is about {d:.0f} miles from {hub} in a straight line. Driving distance is longer and depends on the route.", None))
            break
    if near:
        d, o = near[0]
        fq.append((f'What towns are near {nm}?', f"The closest is {o['name']}, about {d:.0f} miles away. Others nearby include {', '.join(x['name'] for _, x in near[1:4])}.", None))
    dist = SCHOOL_DISTRICTS[cty]
    fq.append((f'What school district serves {nm}?', f"Public schools in {nm} are run by the {dist[0]}; Nevada has one school district per county. The school a student attends depends on the home address.",
               f"Public schools in {e(nm)} are run by the {a_ext(dist[1], e(dist[0]))}; Nevada has one school district per county. The school a student attends depends on the home address."))
    a = ("Nevada has no state personal income tax. Sales tax is 6.85% at minimum statewide and higher in some counties (8.375% in Clark County). "
         "Housing is the biggest cost difference between towns.")
    fq.append((f'What is the cost of living in {nm}, Nevada?', a + ' See our moving guide for more on taxes and costs.',
               e(a) + ' See our <a href="/moving-to-nevada/#costs">Nevada moving guide</a> for more on taxes and costs.'))
    fq.append((f'How soon do I need a Nevada license and plates after moving to {nm}?',
               "New residents must get a Nevada driver's license and register their vehicles within 30 days of moving to the state.", None))
    return fq


def place_page(p):
    nm, cty = p['name'], p['county']; reg = REGION_OF[cty]; x = CUSTOM.get(nm, {})
    path = f'/cities/{slug(nm)}/'
    zl, tzs = zips_for(p)
    near = sorted(((miles(p, o), o) for o in PLACES if o is not p), key=lambda t: t[0])[:8]
    pop = n(p['pop2020'])
    rows = [('County', county_link(cty) if cty != 'Carson City' else 'Independent city (county-equivalent)'),
            ('Region', region_link(reg)), ('Type', e(place_kind(p)).capitalize()), ('Population (2020 Census)', pop)]
    if p.get('est2024'): rows.append(('Population estimate (2024)', n(p['est2024'])))
    if p.get('pop2010'): rows.append(('Population (2010 Census)', f"{n(p['pop2010'])} ({e(p['change'])} by 2020)"))
    rows.append(('Land area', f"{p['land_sqmi']:,.1f} sq mi"))
    if p['land_sqmi'] > 0: rows.append(('Density', f"{p['pop2020'] / p['land_sqmi']:,.0f} people per sq mi"))
    if p.get('elev_ft'): rows.append(('Elevation', f"{n(p['elev_ft'])} ft"))
    if p.get('incorporated'): rows.append(('Incorporated', e(p['incorporated'])))
    if zl: rows.append(('ZIP code' if len(zl) == 1 else 'ZIP codes', ', '.join(zl[:14]) + (f' and {len(zl) - 14} more' if len(zl) > 14 else '')))
    rows.append(('Area code' if cty != 'Clark' else 'Area codes', ' and '.join(area_codes(cty)) + ' (<a href="/nevada-area-codes/">Nevada area codes</a>)'))
    rows.append(('Time zone', ' / '.join(TZ_NAME.get(t, t) for t in tzs)))
    if p.get('website'): rows.append(('Official website', a_ext(p['website'], e(host(p['website'])))))
    if TRANSIT.get(cty): rows.append(('Public transit', a_ext(TRANSIT[cty][1], e(TRANSIT[cty][0]))))
    facts = ''.join(f'<tr><th scope="row">{a}</th><td>{b}</td></tr>' for a, b in rows)

    lead = (f'{e(nm)} is an {e(place_kind(p))} in {county_link(cty) if cty != "Carson City" else "western Nevada"}, in the {region_link(reg)} region, '
            f'with {pop} residents at the 2020 Census.' if nm != 'Carson City' else
            f'Carson City is Nevada\'s capital and an independent consolidated city in the {region_link(reg)} region, with {pop} residents at the 2020 Census.')
    if p['type'] == 'cdp' and nm != 'Carson City':
        lead += f' Because it is not incorporated, {e(county_label(cty))} runs local services such as roads, policing and planning.'
    about = f'<p>{lead}</p>' + summary_html(p['summary']) + wiki_credit(p['wiki_url'] if p['summary'] else '')

    el = electric(p)
    el_html = ' or '.join(a_ext(u, e(t)) for t, u in el)
    dist = SCHOOL_DISTRICTS[cty]
    hs = nearby_high_schools(p)
    hs_html = ''.join(f'<li>{a_ext("https://nces.ed.gov/ccd/schoolsearch/school_detail.asp?ID=" + s["ncessch"], e(title_case_school(s["school_name"])))}'
                      f' <span class="m">{d:.1f} mi{", charter" if s.get("charter") == 1 else ""}</span></li>' for d, s in hs)
    attractions = ''
    if x.get('attractions'):
        attractions = (f'<h2 id="things-to-do">Things to do in {e(nm)}</h2><ul class="list">' + ''.join(
            f'<li>{a_ext(u, e(t)) if u else "<strong>" + e(t) + "</strong>"}<span>{e(dsc)}</span></li>' for t, u, dsc in x['attractions']) + '</ul>')
    employers = x.get('employers')
    moving = (f'<h2 id="moving">Moving to {e(nm)}</h2><div class="ledger">'
              f'<section><h3>Utilities</h3><ul><li>Electricity: {el_html} (confirm by address)</li><li>Natural gas: {gas(cty)}</li>'
              f'<li>Water, sewer and trash: {"the City of " + e(nm) if p["type"] == "city" else e(county_label(cty)) + " or a local water district"}</li>'
              f'<li>Internet: compare providers on the {a_ext(L["fcc"], "FCC broadband map")}</li></ul></section>'
              f'<section><h3>Schools</h3><ul><li>District: {a_ext(dist[1], e(dist[0]))}</li>'
              + (f'<li>Nearest public high schools:<ul class="sub">{hs_html}</ul></li>' if hs_html else '')
              + f'<li>{a_ext(L["nces"], "Look up the schools for an address (NCES)")}</li></ul></section>'
              f'<section><h3>Car and license</h3><ul><li>Nevada license and registration within <strong>30 days</strong> of moving</li>'
              f'<li>{a_ext(L["dmv_new"], "DMV new resident guide")}</li><li>Most vehicles need a smog check in the Las Vegas and Reno areas</li></ul></section>'
              f'<section><h3>Jobs</h3><ul>' + (f'<li>Major employers: {e(employers)}</li>' if employers else '')
              + f'<li>{a_ext(L["employnv"], "EmployNV job board")}</li><li>{a_ext(L["detr"], "Nevada DETR")} (unemployment and job training)</li></ul></section>'
              f'<section><h3>Voting</h3><ul><li>{a_ext(L["register"], "Register to vote online")}</li>'
              f'<li>Active registered voters are mailed a ballot unless they opt out</li>'
              + (f'<li>{a_ext(COUNTY[cty]["website"], e(county_label(cty)) + " website")} (clerk and elections)</li>' if COUNTY[cty].get('website') else '')
              + f'</ul></section>'
              f'<section><h3>Help and health care</h3><ul><li>{a_ext(L["access_nv"], "Access Nevada")} for SNAP and Medicaid</li>'
              f'<li>{a_ext(L["healthlink"], "Nevada Health Link")} for health insurance</li><li>{a_ext(L["nv211"], "Nevada 211")}, or dial 211</li></ul></section></div>')
    near_html = ''.join(f'<li><a href="/cities/{slug(o["name"])}/">{e(o["name"])}</a><span>{d:.0f} mi, pop. {n(o["pop2020"])}</span></li>' for d, o in near[:6])
    fq = place_faq(p, near)
    faq_html, faq_ld = faq_block(fq, f'{e(nm)}, Nevada: common questions')
    local = []
    if p.get('website'): local.append(a_ext(p['website'], f'{"City" if p["type"] == "city" else "Town"} of {e(nm)} official website'))
    if COUNTY[cty].get('website') and cty != 'Carson City': local.append(a_ext(COUNTY[cty]['website'], f'{e(county_label(cty))} official website'))
    if p.get('wiki_url'): local.append(a_ext(p['wiki_url'], f'{e(nm)} on Wikipedia'))
    links = '<ul class="links">' + ''.join(f'<li>{x_}</li>' for x_ in local + [a_ext(u, t) for t, u in STATE_LINKS]) + '</ul>'

    tagline = x.get('tagline') or f'{place_kind(p).capitalize()} in {county_label(cty)}'
    pills = (f'<span>Pop. {pop}</span><span>{e(county_label(cty))}</span>' +
             ('<span>State capital</span>' if nm == 'Carson City' else '<span>County seat</span>' if COUNTY[cty]['seat'] == nm else ''))
    nz = len(zl)
    title = place_title(p, nz)
    desc = fit_desc(f'{nm}, Nevada: {pop} residents (2020 Census), {county_label(cty)}.',
                    f'ZIP code{"s" if nz != 1 else ""}, schools, weather,' if nz else 'Schools, weather,',
                    'things to do,' if x.get('attractions') else '', 'nearby towns and moving tips.', f'Updated guide to {nm}, NV.')
    crumbs = [('Home', '/'), ('Cities & towns', '/cities/'), (county_label(cty), f'/counties/{slug(cty)}/'), (nm, path)]
    ld_city = {'@context': 'https://schema.org', '@type': 'City' if p['type'] == 'city' else 'Place', 'name': f'{nm}, Nevada', 'url': BASE_URL + path,
               'geo': {'@type': 'GeoCoordinates', 'latitude': p['lat'], 'longitude': p['lon']},
               'containedInPlace': {'@type': 'AdministrativeArea', 'name': f'{county_label(cty)}, Nevada'}}
    same = [u for u in (p.get('wiki_url'), p.get('website')) if u]
    if same: ld_city['sameAs'] = same
    toc = [('About', 'about'), ('Quick facts', 'facts'), ('Weather', 'weather')] + ([('Photos', 'photos')] if gallery(p, nm) else []) \
        + ([('Things to do', 'things-to-do')] if attractions else []) + [('Moving', 'moving'), ('Nearby', 'nearby'), ('FAQ', 'faq')]
    return (head(title, desc, path, 'article', p.get('image'), (ld_city, crumbs_ld(crumbs), faq_ld))
            + header('/cities/') + hero(f'{e(nm)}, Nevada', e(tagline), pills, nm, crumbs)
            + '<main id="main" class="wrap page">' + toc_html(toc)
            + f'<div class="body"><h2 id="about">About {e(nm)}</h2><div class="prose">{about}</div>'
            + f'<h2 id="facts">Quick facts</h2><div class="facts"><table>{facts}</table>{locator_map(p["lat"], p["lon"], nm, cty)}</div>'
            + weather(nm, p['lat'], p['lon'], tzs[0]) + gallery(p, nm) + attractions + moving
            + f'<h2 id="nearby">Towns near {e(nm)}</h2><ul class="near">{near_html}</ul>'
            + faq_html + f'<h2 id="links">Official links</h2>{links}</div></main>'
            + footer(' Population: U.S. Census Bureau. Schools: NCES Common Core of Data.'))


def toc_html(items):
    return '<nav class="toc" aria-label="On this page"><p>On this page</p><ol>' + ''.join(f'<li><a href="#{a}">{t}</a></li>' for t, a in items) + '</ol></nav>'


# ================================================================ county pages
def county_page(k):
    nm = k['name']; lab = county_label(nm); reg = REGION_OF[nm]
    path = f'/counties/{slug(nm)}/'
    members = sorted([p for p in PLACES if p['county'] == nm], key=lambda x: -x['pop2020'])
    in_places = sum(p['pop2020'] for p in members)
    dist = SCHOOL_DISTRICTS[nm]
    rows = [('Region', region_link(reg)), ('County seat', (f'<a href="/cities/{slug(k["seat"])}/">{e(k["seat"])}</a>' if any(p['name'] == k['seat'] for p in PLACES) else e(k['seat'])) or 'n/a'),
            ('Established', e(k['est']) or 'n/a'), ('Population (2020 Census)', n(k['pop2020']))]
    if k.get('est2024'): rows.append(('Population estimate (2024)', n(k['est2024'])))
    rows += [('Share of Nevada', f"{k['pop2020'] / STATE_POP2020 * 100:.1f}%"), ('Land area', f"{n(k['land_sqmi'])} sq mi"),
             ('Density', f"{k['pop2020'] / k['land_sqmi']:,.1f} people per sq mi"),
             ('Cities and towns', f'{len(members)} ({sum(p["type"] == "city" for p in members)} incorporated)'),
             ('School district', a_ext(dist[1], e(dist[0]))), ('Area code' if nm != 'Clark' else 'Area codes', ' and '.join(area_codes(nm)))]
    if k.get('website'): rows.append(('Official website', a_ext(k['website'], e(host(k['website'])))))
    facts = ''.join(f'<tr><th scope="row">{a}</th><td>{b}</td></tr>' for a, b in rows)
    lst = ''.join(f'<li><a href="/cities/{slug(p["name"])}/">{e(p["name"])}</a><span>{"city" if p["type"] == "city" else "town"}, pop. {n(p["pop2020"])}</span></li>' for p in members)
    rank = sorted(COUNTIES, key=lambda c: -c['pop2020']).index(k) + 1
    area_rank = sorted(COUNTIES, key=lambda c: -c['land_sqmi']).index(k) + 1
    fq = [(f'What is the population of {lab}, Nevada?', f"{lab} had {n(k['pop2020'])} residents at the 2020 Census, the {ordinal(rank)} most of Nevada's 17 counties."
           + (f" The 2024 estimate is {n(k['est2024'])}." if k.get('est2024') else ''), None),
          (f'What is the county seat of {lab}?', 'Carson City is an independent city and serves as its own seat of government.' if nm == 'Carson City'
           else f"The county seat is {k['seat']}.", None),
          (f'How big is {lab}?', f"{lab} covers about {n(k['land_sqmi'])} square miles of land, the {ordinal(area_rank)} largest of Nevada's counties.", None),
          (f'What cities and towns are in {lab}?', (f"{lab} includes {', '.join(p['name'] for p in members[:8])}" + (f" and {len(members) - 8} other communities." if len(members) > 8 else '.')) if members else 'None are listed.', None),
          (f'What school district serves {lab}?', f"The {dist[0]} runs public schools across the whole county.", None)]
    if members:
        fq.append((f'How many people in {lab} live in a city or town?', f"About {in_places / k['pop2020'] * 100:.0f}% of residents live inside a city or census-designated town; the rest live in rural areas outside them.", None))
    faq_html, faq_ld = faq_block(fq, f'{e(lab)}: common questions')
    about = f'<p>{e(lab)} is in Nevada\'s {region_link(reg)} region.</p>' + summary_html(k['summary']) + wiki_credit(k['wiki_url'] if k['summary'] else '')
    title = f'{lab}, Nevada: Towns, Population, Schools & Map' if len(f'{lab}, Nevada: Towns, Population, Schools & Map') <= 60 else f'{lab}, NV: Towns, Population & Map'
    desc = fit_desc(f'{lab}, Nevada guide: {n(k["pop2020"])} residents at the 2020 Census' + (f', county seat {k["seat"]}.' if nm != 'Carson City' else '.'),
                    f'All {len(members)} cities and towns, schools, map, facts and FAQs.', 'Plan a move or a visit.')
    crumbs = [('Home', '/'), ('Counties', '/counties/'), (lab, path)]
    others = ''.join(f'<li><a href="/counties/{slug(c)}/">{e(county_label(c))}</a></li>' for c in REGIONS[reg]['counties'] if c != nm)
    return (head(title, desc, path, 'article', k.get('image'), ({'@context': 'https://schema.org', '@type': 'AdministrativeArea', 'name': f'{lab}, Nevada', 'url': BASE_URL + path}, crumbs_ld(crumbs), faq_ld))
            + header('/counties/') + hero(e(lab), f'{e(n(k["pop2020"]))} residents, {e(reg)}', '', nm + ' county', crumbs)
            + '<main id="main" class="wrap page">' + toc_html([('About', 'about'), ('Facts', 'facts'), ('Towns', 'towns'), ('FAQ', 'faq')])
            + f'<div class="body"><h2 id="about">About {e(lab)}</h2><div class="prose">{about}</div>'
            + f'<h2 id="facts">Quick facts</h2><div class="facts"><table>{facts}</table>{locator_map(k["lat"], k["lon"], lab, nm)}</div>'
            + f'<h2 id="towns">Cities and towns in {e(lab)}</h2>' + (f'<ul class="near">{lst}</ul>' if lst else '<p>No incorporated cities or census-designated towns.</p>')
            + faq_html + (f'<h2>Other counties in the {e(reg)} region</h2><ul class="links">{others}</ul>' if others else '') + '</div></main>'
            + footer(' Population and area: U.S. Census Bureau.'))


# ================================================================ index pages
def cities_index():
    letters = sorted({p['name'][0] for p in PLACES})
    groups = ''.join(f'<h2 id="l-{c}">{c}</h2><ul class="near az">' + ''.join(
        f'<li data-n="{e(p["name"].lower())}"><a href="/cities/{slug(p["name"])}/">{e(p["name"])}</a><span>{e(county_label(p["county"]))}, pop. {n(p["pop2020"])}</span></li>'
        for p in PLACES if p['name'][0] == c) + '</ul>' for c in letters)
    alpha = ''.join(f'<a href="#l-{c}">{c}</a>' for c in letters)
    top = ''.join(f'<tr><td>{i}</td><td><a href="/cities/{slug(p["name"])}/">{e(p["name"])}</a></td><td>{e(county_label(p["county"]))}</td><td>{"City" if p["type"] == "city" else "Town (CDP)"}</td><td class="r">{n(p["pop2020"])}</td></tr>'
                  for i, p in enumerate(RANKED[:25], 1))
    js = ("<script>(function(){var q=document.getElementById('q');q.addEventListener('input',function(){var v=q.value.trim().toLowerCase();"
          "document.querySelectorAll('.az li').forEach(function(li){li.hidden=v&&li.dataset.n.indexOf(v)<0});"
          "document.querySelectorAll('.az').forEach(function(u){var h=u.previousElementSibling;var any=[].some.call(u.children,function(l){return !l.hidden});u.hidden=!any;h.hidden=!any})})})();</script>")
    nc = sum(p['type'] == 'city' for p in PLACES)
    title = 'Nevada Cities and Towns A-Z: All 133 Places'
    desc = fit_desc(f'Every Nevada city and town: the {nc} incorporated cities and {len(PLACES) - nc} census-designated towns, with population, county and a guide to each one.', 'Search by name.')
    crumbs = [('Home', '/'), ('Cities & towns', '/cities/')]
    body = (f'<div class="prose"><p>Nevada has only {nc} incorporated cities, counting Carson City. Many of its biggest communities, including '
            f'Paradise, Spring Valley, Enterprise and Sunrise Manor around the Las Vegas Strip, are unincorporated towns that the Census Bureau '
            f'counts as census-designated places (CDPs). This directory covers all {len(PLACES)} of them.</p></div>'
            f'<label class="search"><span>Find a city or town</span><input id="q" type="search" autocomplete="off" placeholder="Type a name, e.g. Pahrump"></label>'
            f'<nav class="alpha" aria-label="Jump to letter">{alpha}</nav>{groups}'
            f'<h2 id="largest">The 25 largest places in Nevada</h2><div class="tbl-wrap"><table class="tbl"><thead><tr><th>#</th><th>Name</th><th>County</th><th>Type</th><th class="r">Population (2020)</th></tr></thead><tbody>{top}</tbody></table></div>')
    return (head(title.replace('133', str(len(PLACES))), desc, '/cities/', ld_objs=(crumbs_ld(crumbs),)) + header('/cities/')
            + hero('Nevada cities and towns', f'{len(PLACES)} places, from Las Vegas to Jarbidge', '', 'cities index', crumbs)
            + f'<main id="main" class="wrap narrow">{body}</main>' + js + footer(' Population: U.S. Census Bureau, 2020 Census.'))


def counties_index():
    rows = ''.join(f'<tr><td><a href="/counties/{slug(k["name"])}/">{e(county_label(k["name"]))}</a></td><td>{e(k["seat"])}</td><td>{e(REGION_OF[k["name"]])}</td>'
                   f'<td class="r">{n(k["pop2020"])}</td><td class="r">{n(k["land_sqmi"])}</td></tr>' for k in sorted(COUNTIES, key=lambda c: -c['pop2020']))
    title = "Nevada Counties: Map and Guide to All 17"
    desc = fit_desc("Map and guide to Nevada's 16 counties and the independent city of Carson City: county seats, population, land area, towns and school districts.", 'Pick one to start.')
    crumbs = [('Home', '/'), ('Counties', '/counties/')]
    body = (f'<div class="split">{county_map()}<div class="prose"><p>Nevada is divided into 16 counties plus Carson City, an independent city '
            f'that serves as its own county. Clark County alone holds {COUNTY["Clark"]["pop2020"] / STATE_POP2020 * 100:.0f}% of the state\'s people; '
            f'Esmeralda County, the least populous, had {n(COUNTY["Esmeralda"]["pop2020"])} residents at the 2020 Census.</p>'
            f'<p>Each county also runs its own school district, so the county you live in decides which district your children attend.</p></div></div>'
            f'<div class="tbl-wrap"><table class="tbl"><thead><tr><th>County</th><th>Seat</th><th>Region</th><th class="r">Population (2020)</th><th class="r">Land (sq mi)</th></tr></thead><tbody>{rows}</tbody></table></div>')
    return (head(title, desc, '/counties/', ld_objs=(crumbs_ld(crumbs),)) + header('/counties/')
            + hero("Nevada's counties", '16 counties and one independent city', '', 'counties index', crumbs)
            + f'<main id="main" class="wrap">{body}</main>' + footer(' Population and area: U.S. Census Bureau.'))


def region_page(r):
    v = REGIONS[r]; path = f'/regions/{v["slug"]}/'
    members = sorted([p for p in PLACES if REGION_OF[p['county']] == r], key=lambda x: -x['pop2020'])
    pop = sum(COUNTY[c]['pop2020'] for c in v['counties'])
    lst = ''.join(f'<li><a href="/cities/{slug(p["name"])}/">{e(p["name"])}</a><span>{e(county_label(p["county"]))}, pop. {n(p["pop2020"])}</span></li>' for p in members)
    cts = ''.join(f'<li><a href="/counties/{slug(c)}/">{e(county_label(c))}</a><span>pop. {n(COUNTY[c]["pop2020"])}</span></li>' for c in v['counties'])
    title = f'{r}: Cities, Counties & Travel Guide' if len(f'{r}: Cities, Counties & Travel Guide') <= 60 else f'{r}, Nevada: Region Guide'
    desc = fit_desc(f'{r} region of Nevada: {n(pop)} residents across {len(v["counties"])} {"county" if len(v["counties"]) == 1 else "counties"} and {len(members)} cities and towns.',
                    'What living here is like, what to see and a guide to every town.')
    crumbs = [('Home', '/'), ('Regions', '/regions/'), (r, path)]
    return (head(title, desc, path, ld_objs=(crumbs_ld(crumbs),)) + header('/regions/')
            + hero(e(r), f'{n(pop)} residents, {len(members)} cities and towns', '', r, crumbs)
            + f'<main id="main" class="wrap"><div class="split">{county_map(v["counties"], labels=False)}<div class="prose"><p>{e(v["desc"])}</p>'
            + f'<h2>Living here</h2><p>{e(v["living"])}</p><h2>Visiting</h2><p>{e(v["visit"])}</p></div></div>'
            + f'<h2>Counties</h2><ul class="near">{cts}</ul><h2>Cities and towns</h2><ul class="near">{lst}</ul></main>'
            + footer(' Population: U.S. Census Bureau, 2020 Census.'))


def regions_index():
    cards = ''
    for r, v in REGIONS.items():
        pop = sum(COUNTY[c]['pop2020'] for c in v['counties'])
        cards += (f'<li><a href="/regions/{v["slug"]}/"><b>{e(r)}</b></a><span>{n(pop)} residents, '
                  f'{", ".join(county_label(c) for c in v["counties"])}</span><p>{e(v["desc"].split(". ")[0])}.</p></li>')
    crumbs = [('Home', '/'), ('Regions', '/regions/')]
    return (head('Regions of Nevada: Six Areas to Live and Explore', fit_desc('The six regions of Nevada, from Las Vegas and the Mojave to Reno-Tahoe, the Ruby Mountains and Great Basin National Park.', 'Cities, counties and what each area is like.'),
                 '/regions/', ld_objs=(crumbs_ld(crumbs),)) + header('/regions/')
            + hero('Regions of Nevada', 'Six regions, each built from whole counties', '', 'regions', crumbs)
            + f'<main id="main" class="wrap"><div class="split">{county_map()}<ul class="regions">{cards}</ul></div></main>' + footer())


def zip_page():
    rows = ''
    for p in PLACES:
        zl, _ = zips_for(p)
        if zl: rows += f'<tr><td><a href="/cities/{slug(p["name"])}/">{e(p["name"])}</a></td><td>{e(county_label(p["county"]))}</td><td>{", ".join(zl)}</td></tr>'
    allz = sorted({z for v in ZIPS.values() for z in v['zips']})
    fq = [('How many ZIP codes does Nevada have?', 'Nevada ZIP codes run from 889 to 898. Las Vegas Valley codes start with 890 and 891, Reno-area codes with 894 and 895, and rural northern Nevada with 893, 894 and 898.', None),
          ('Why does my ZIP code say Las Vegas when I live in Paradise or Spring Valley?', 'The Postal Service uses "Las Vegas" as the mailing city for most of the unincorporated valley, even though Paradise, Spring Valley, Enterprise and similar towns are separate communities governed by Clark County.', None),
          ('How were these ZIP codes matched to towns?', 'We used the Census Bureau\'s 2020 relationship file between ZIP Code Tabulation Areas and places, listing a ZIP code when a meaningful share of it falls inside the town. Always confirm an address with USPS.', None)]
    faq_html, faq_ld = faq_block(fq, 'Nevada ZIP code questions')
    crumbs = [('Home', '/'), ('ZIP codes', '/nevada-zip-codes/')]
    return (head('Nevada ZIP Codes by City and Town', fit_desc('Nevada ZIP codes for every city and census-designated town, from Las Vegas and Henderson to Reno, Pahrump and Elko.', 'Look up a town to see the ZIP codes inside it.'),
                 '/nevada-zip-codes/', ld_objs=(crumbs_ld(crumbs), faq_ld)) + header()
            + hero('Nevada ZIP codes', f'{len(allz)} ZIP codes across {sum(1 for p in PLACES if zips_for(p)[0])} cities and towns', '', 'zip', crumbs)
            + f'<main id="main" class="wrap narrow"><div class="tbl-wrap"><table class="tbl"><thead><tr><th>City or town</th><th>County</th><th>ZIP codes</th></tr></thead><tbody>{rows}</tbody></table></div>{faq_html}</main>'
            + footer(' ZIP-to-place matching: U.S. Census Bureau 2020 ZCTA relationship file.'))


def area_code_page():
    big775 = [p['name'] for p in RANKED if p['county'] != 'Clark'][:10]
    big702 = [p['name'] for p in RANKED if p['county'] == 'Clark'][:10]
    fq = [('What are the area codes in Nevada?', 'Nevada has three: 702 and 725, which overlay each other in Clark County, and 775 for the rest of the state.', None),
          ('Do I need to dial 10 digits in Las Vegas?', 'Yes. Because 702 and 725 share the same area, local calls in Clark County need the area code plus the seven-digit number.', None),
          ('Which area code is Reno?', 'Reno, Sparks, Carson City, Elko, Pahrump and every other place outside Clark County use 775.', None),
          ('When did 775 start?', 'Area code 775 was split from 702 in 1998. Before that, 702 covered all of Nevada.', None)]
    faq_html, faq_ld = faq_block(fq, 'Nevada area code questions')
    crumbs = [('Home', '/'), ('Area codes', '/nevada-area-codes/')]
    lnk = lambda names: ', '.join(f'<a href="/cities/{slug(x)}/">{e(x)}</a>' for x in names)
    return (head('Nevada Area Codes: 702, 725 and 775 Map & Cities', fit_desc('Nevada area codes explained: 702 and 725 for Las Vegas and Clark County, 775 for Reno, Carson City and the rest of the state.', 'See which code each town uses.'),
                 '/nevada-area-codes/', ld_objs=(crumbs_ld(crumbs), faq_ld)) + header()
            + hero('Nevada area codes', '702 and 725 in Clark County, 775 everywhere else', '', 'area codes', crumbs)
            + f'<main id="main" class="wrap"><div class="split">{county_map(("Clark",), labels=True)}<div class="prose">'
            + f'<h2>702 and 725: Clark County</h2><p>Area code 702 serves Las Vegas and the rest of Clark County. Area code 725 was added in 2014 as an overlay, so new numbers in the same area can get either code and every local call needs ten digits. Largest places: {lnk(big702)}.</p>'
            + f'<h2>775: the rest of Nevada</h2><p>Area code 775 covers all 16 other county areas, from Reno and Lake Tahoe to Elko, Ely and Pahrump. Largest places: {lnk(big775)}.</p></div></div>{faq_html}</main>'
            + footer())


def simple_page(path, title, desc, h1, sub, body, typ='WebPage'):
    crumbs = [('Home', '/'), (h1, path)]
    return (head(title, desc, path, ld_objs=({'@context': 'https://schema.org', '@type': typ, 'name': title, 'url': BASE_URL + path}, crumbs_ld(crumbs)))
            + header() + hero(e(h1), sub, '', h1, crumbs) + f'<main id="main" class="wrap narrow prose">{body}</main>' + footer())


ABOUT = f'''<p>Nevada Information is an independent guide to the State of Nevada. It has a page for every incorporated city and census-designated town in the state, each of the 17 counties, and six regions, plus guides for people moving to or visiting Nevada.</p>
<h2>Where the information comes from</h2><p>Population, land area and ZIP code boundaries come from the U.S. Census Bureau (2010 and 2020 Censuses and the Vintage 2024 estimates). School data comes from the National Center for Education Statistics. Background text is adapted from Wikipedia under the CC BY-SA 4.0 license, and photos come from Wikimedia Commons with the photographer and license shown under each one. Weather forecasts load live from Open-Meteo.</p>
<h2>What we are not</h2><p>We are not part of, or endorsed by, the State of Nevada or any city or county government. For official business, follow the government links on each page.</p>
<h2>Corrections</h2><p>If something is out of date or wrong, <a href="/contact/">tell us</a> and we will fix it.</p>'''
CONTACT = f'''<p>Questions, corrections and suggestions about any Nevada city, county or guide are welcome.</p>
<p>Email: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
<p>When reporting a correction, include the page address and, if you can, a source for the right information.</p>'''
ADVERTISE = f'''<p>Nevada Information reaches people researching a move to Nevada or planning a trip, town by town. Banner placements and sponsorships are available on city, county, region and guide pages.</p>
<p>Email <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> with the area and audience you want to reach.</p>'''
PRIVACY = f'''<p><em>Last updated: November 14, 2026</em></p>
<h2>Information we collect</h2><p>This site has no accounts or sign-up forms. If you email us, we keep your message and address only to reply.</p>
<h2>Weather and fonts</h2><p>City pages request a forecast from Open-Meteo using the town's coordinates, not your location. Fonts load from Google Fonts, which receives your IP address as part of the request.</p>
<h2>Analytics</h2><p>We may use Google Analytics to count visits and see which pages are useful. It sets cookies and collects data such as your browser, approximate location and the pages you view. You can opt out with the <a href="https://tools.google.com/dlpage/gaoptout" target="_blank" rel="noopener">Google Analytics opt-out add-on</a> or by blocking cookies.</p>
<h2>Advertising</h2><p>If we show ads, advertisers or ad networks may use cookies to measure them. We do not sell personal information.</p>
<h2>Children</h2><p>This site is not directed at children under 13, and we do not knowingly collect their information.</p>
<h2>Contact</h2><p>Questions about this policy: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>'''


def not_found():
    big = ''.join(f'<li><a href="/cities/{slug(p["name"])}/">{e(p["name"])}</a></li>' for p in RANKED[:8])
    return (head('Page Not Found | Nevada Information', 'This page does not exist. Find a Nevada city, town or county from the directory.', '/404.html', noindex=True)
            + header() + hero('That page isn\'t here', 'The address may be mistyped, or the page may have moved.', '', '404')
            + f'<main id="main" class="wrap narrow prose"><p>Try the <a href="/cities/">cities and towns directory</a> or the <a href="/counties/">county list</a>. Popular towns:</p><ul class="links">{big}</ul></main>' + footer())


# ================================================================ server config
HTACCESS = r'''# Nevada Information - Apache config (for the VPS). Cloudflare Pages uses _headers / _redirects instead.
Options -Indexes
ErrorDocument 404 /404.html
<IfModule mod_rewrite.c>
RewriteEngine On
# one hop to https://nevadainformation.com/...
RewriteCond %{HTTP_HOST} ^www\. [NC,OR]
RewriteCond %{HTTP:X-Forwarded-Proto} !https
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://nevadainformation.com/$1 [R=301,L]
RewriteCond %{THE_REQUEST} \s/+(.*?/)?index\.html[\s?]
RewriteRule ^ /%1 [R=301,L,NE]
</IfModule>
<IfModule mod_headers.c>
Header set Cache-Control "public, max-age=600, no-transform"
<FilesMatch "\.(css|svg|png|jpg|ico|woff2)$">
Header set Cache-Control "public, max-age=2592000"
</FilesMatch>
Header set X-Content-Type-Options "nosniff"
Header set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>
'''
HEADERS = '''/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Cache-Control: public, max-age=600, no-transform
/assets/*
  Cache-Control: public, max-age=2592000
'''


# ================================================================ build
def write(rel, content):
    p = os.path.join(OUT, rel.lstrip('/'))
    if p.endswith('/'): p += 'index.html'
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(content)


def main():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    shutil.copytree(os.path.join(HERE, 'static'), OUT)
    os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)
    open(os.path.join(OUT, 'assets', 'site.css'), 'w').write(CSS)
    urls = []
    def put(path, html_):
        write(path, html_); urls.append(path)
    ctx = dict(PLACES=PLACES, COUNTIES=COUNTIES, COUNTY=COUNTY, RANKED=RANKED, REGIONS=REGIONS, REGION_OF=REGION_OF, STATE_POP2020=STATE_POP2020,
               head=head, header=header, footer=footer, hero=hero, crumbs_ld=crumbs_ld, faq_block=faq_block, toc_html=toc_html, county_map=county_map,
               fit_desc=fit_desc, e=e, n=n, slug=slug, a_ext=a_ext, county_label=county_label, L=L, BASE_URL=BASE_URL)
    put('/', pages.home(ctx))
    put('/nevada/', pages.nevada(ctx))
    put('/moving-to-nevada/', pages.moving(ctx))
    put('/visit-nevada/', pages.visiting(ctx))
    put('/regions/', regions_index())
    for r in REGIONS: put(f'/regions/{REGIONS[r]["slug"]}/', region_page(r))
    put('/counties/', counties_index())
    for k in COUNTIES: put(f'/counties/{slug(k["name"])}/', county_page(k))
    put('/cities/', cities_index())
    for p in PLACES: put(f'/cities/{slug(p["name"])}/', place_page(p))
    put('/nevada-zip-codes/', zip_page())
    put('/nevada-area-codes/', area_code_page())
    put('/about/', simple_page('/about/', 'About Nevada Information | Independent Nevada Guide', fit_desc('About Nevada Information: an independent, free guide to every Nevada city, town and county, with sources for every figure.', 'Who we are and how the site works.'), 'About Nevada Information', 'An independent, plain-language guide to Nevada.', ABOUT, 'AboutPage'))
    put('/contact/', simple_page('/contact/', 'Contact Nevada Information', fit_desc('Contact Nevada Information with questions, corrections or suggestions about any Nevada city, town, county or guide.', 'We read every message.'), 'Contact us', 'Questions and corrections are welcome.', CONTACT, 'ContactPage'))
    put('/privacy/', simple_page('/privacy/', 'Privacy Policy | Nevada Information', fit_desc('Privacy policy for nevadainformation.com: what information we collect, how cookies, analytics and third-party services are used, and your choices.'), 'Privacy policy', 'How nevadainformation.com handles information.', PRIVACY))
    put('/advertise/', simple_page('/advertise/', 'Advertise on Nevada Information', fit_desc('Advertise on Nevada Information and reach people researching a move to Nevada or planning a trip, with placements on city, county and region pages.'), 'Advertise with us', 'Reach people planning a Nevada move or trip.', ADVERTISE))
    write('/404.html', not_found())
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
        f'  <url><loc>{BASE_URL}{u}</loc><lastmod>{TODAY}</lastmod></url>\n' for u in urls) + '</urlset>\n'
    write('/sitemap.xml', sm)
    write('/robots.txt', f'User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n')
    write('/.htaccess', HTACCESS)
    write('/_headers', HEADERS)
    write(f'/{INDEXNOW_KEY}.txt', INDEXNOW_KEY)
    print(f'Built {len(urls)} pages into public/ ({len(PLACES)} cities and towns, {len(COUNTIES)} counties, {len(REGIONS)} regions).')


if __name__ == '__main__':
    main()
