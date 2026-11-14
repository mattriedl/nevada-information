#!/usr/bin/env python3
"""SEO and quality gate for Nevada Information blog articles.

  python3 build/check_blog.py <slug>   check one article (metadata, body and built page)
  python3 build/check_blog.py --all    check every article

Run after building (python3 build/generate_site.py). The last line is "Problems: N";
an article may only be published when N is 0. Warnings are advice.
"""
import html, json, os, re, sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PUB = os.path.join(ROOT, 'public')
ARTS = os.path.join(HERE, 'data', 'blog_articles.json')
CONTENT = os.path.join(HERE, 'blog_content')
TRUSTED = ('.gov', '.us', '.edu', 'nps.gov', 'blm.gov', 'fs.usda.gov', 'noaa.gov', 'weather.gov', 'travelnevada.com',
           'visitlasvegas.com', 'visitrenotahoe.com', 'lvcva.com', 'census.gov', 'nvroads.com', 'rtcsnv.com', 'rtcwashoe.com')
CATS = ('Moving to Nevada', 'Living in Nevada', 'Visiting Nevada')


def text_of(h): return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h))).strip()


def check(slug, strict=True):
    probs, warns = [], []
    P, W = probs.append, warns.append
    arts = json.load(open(ARTS, encoding='utf-8'))
    a = next((x for x in arts if x['slug'] == slug), None)
    if not a: return [f'{slug} is not in build/data/blog_articles.json'], []
    src = os.path.join(CONTENT, slug + '.html')
    if not os.path.exists(src): return [f'missing build/blog_content/{slug}.html'], []
    body = open(src, encoding='utf-8').read(); words = len(text_of(body).split())

    # metadata
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug): P('slug must be lowercase words joined by hyphens')
    for k in ('title', 'seo_title', 'description', 'excerpt', 'hero_sub', 'date', 'category', 'cta', 'keywords', 'image', 'image_page', 'image_credit', 'image_alt'):
        if not a.get(k): P(f'metadata "{k}" is missing')
    st, d = a.get('seo_title', ''), a.get('description', '')
    if len(st) > 60: P(f'seo_title is {len(st)} chars (max 60): {st}')
    if not 150 <= len(d) <= 160: P(f'description is {len(d)} chars (must be 150-160)')
    for k in ('title', 'seo_title', 'h1', 'description'):
        if re.search(r'\b20\d\d\b', a.get(k) or ''): P(f'{k} contains a year; keep titles and descriptions evergreen')
    if any(re.search(r'\b20\d\d\b', k) for k in a.get('keywords', [])): P('keywords contain a year; keep them evergreen')
    kws = a.get('keywords') or []
    if not 4 <= len(kws) <= 10: P(f'keywords: need 4-10 (primary first), found {len(kws)}')
    primary = (kws[0] if kws else '').lower()
    if a.get('category') not in CATS: P(f'category must be one of {CATS}')
    if a.get('cta') not in ('moving', 'visiting'): P('cta must be "moving" or "visiting"')
    try:
        if date.fromisoformat(a['date']) > date.today(): P('date is in the future')
    except Exception: P('date must be YYYY-MM-DD')
    for o in arts:
        if o['slug'] != slug and o.get('keywords') and o['keywords'][0].lower() == primary:
            P(f'primary keyword "{primary}" already belongs to /blog/{o["slug"]}/')
    if a.get('image') and 'wikimedia.org' not in a['image']: P('hero image must come from Wikimedia Commons')

    # keyword placement
    if primary:
        pk = re.escape(primary)
        if not all(w in st.lower() for w in primary.split()[:3]): W('primary keyword (or its main words) should be in seo_title')
        if primary.split()[0] not in d.lower(): W('primary keyword should be in the description')
        if not re.search(pk, ' '.join(text_of(body).split()[:120]).lower()): P('primary keyword must appear in the first 120 words')
        h2s = [text_of(h).lower() for h in re.findall(r'<h2[^>]*>(.*?)</h2>', body, re.S)]
        if not any(all(w in h for w in primary.split() if len(w) > 2) for h in h2s): W('primary keyword should appear in at least one <h2>')
        cnt = len(re.findall(pk, text_of(body).lower()))
        if cnt < 3: W(f'primary keyword appears only {cnt} times')
        if cnt * len(primary.split()) / max(words, 1) * 100 > 2.5: P('primary keyword density over 2.5% (keyword stuffing)')

    # structure
    if strict and words < 1500: P(f'only {words} words (minimum 1,500)')
    if words > 4000: W(f'{words} words; consider tightening')
    if '<h1' in body: P('no <h1> in the body; the template adds it')
    if not body.lstrip().startswith('<p class="lede">'): P('body must start with <p class="lede">')
    if 'class="callout"' not in body: P('add a quick-answer <div class="callout"> near the top')
    if len(re.findall(r'<h2', body)) < 6: P('need at least 6 <h2> sections (they become the table of contents)')
    if re.search(r'<h2(?! id=")', body): P('every <h2> needs an id="" for the table of contents')
    lv = [int(x) for x in re.findall(r'<h([2-4])', body)]
    if any(y > x + 1 for x, y in zip([2] + lv, lv)): P('heading levels skip (e.g. h2 to h4)')
    if 'class="tbl"' not in body: W('add a comparison <table class="tbl"> where the topic allows')

    # FAQ
    faq = re.search(r'<h2 id="faq"[^>]*>.*?<div class="faq">(.*?)</div>', body, re.S)
    qs = re.findall(r'<details>\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>\s*</details>', faq.group(1) if faq else '', re.S)
    if not faq: P('missing <h2 id="faq"> followed by <div class="faq">')
    elif not 4 <= len(qs) <= 8: P(f'FAQ needs 4-8 questions, found {len(qs)}')
    for q, ans in qs:
        if not text_of(q).endswith('?'): P(f'FAQ question should end with "?": {text_of(q)[:60]}')
        if len(text_of(ans).split()) < 15: W(f'FAQ answer is short: {text_of(q)[:50]}')

    # links
    links = re.findall(r'href="([^"]+)"', body)
    internal = {u for u in links if u.startswith('/')}
    external = {u for u in links if u.startswith('http')}
    if len(internal) < 6: P(f'need 6+ distinct internal links, found {len(internal)}')
    if not any(u.startswith('/cities/') for u in internal): P('link at least one /cities/ page')
    if len(arts) > 1 and not any(u.startswith('/blog/') for u in internal): W('link at least one related blog article')
    for u in internal:
        p = u.split('#')[0]
        f = os.path.join(PUB, p.lstrip('/'), 'index.html') if p.endswith('/') else os.path.join(PUB, p.lstrip('/'))
        if not os.path.exists(f): P(f'internal link {u} points to a page that does not exist')
        if not p.endswith('/') and '.' not in p.rsplit('/', 1)[-1]: W(f'internal link {u} should end with a slash')
    if len(external) < 3: P(f'cite 3+ external sources, found {len(external)}')
    if len({u for u in external if any(t in u for t in TRUSTED)}) < 2: P('2+ external links must be official sources (.gov, NPS, BLM, LVCVA, Travel Nevada...)')
    for tag in re.findall(r'<a [^>]*href="http[^"]*"[^>]*>', body):
        if 'target="_blank"' not in tag or 'rel="noopener"' not in tag: P('external links need target="_blank" rel="noopener"'); break

    # photos
    figs = re.findall(r'<figure class="photo">(.*?)</figure>', body, re.S)
    if len(figs) < 2: P(f'need 2+ in-article photos (<figure class="photo">), found {len(figs)}')
    for fg in figs:
        img = re.search(r'<img [^>]*>', fg)
        if not img: P('figure without <img>'); continue
        t = img.group(0)
        if 'wikimedia.org' not in t: P('photos must come from Wikimedia Commons')
        if not re.search(r'alt="[^"]{15,}"', t): P('every photo needs descriptive alt text (15+ characters)')
        if 'loading="lazy"' not in t: W('in-article photos should use loading="lazy"')
        if not re.search(r'width="\d+" height="\d+"', t): W('add width and height to photos')
        if 'commons.wikimedia.org/wiki/File:' not in fg: P('every photo needs a credit linking to its Commons file page')

    # writing
    for bad in ('as an ai', 'lorem ipsum', 'in conclusion', 'delve', 'tapestry', 'nestled', 'bustling', 'vibrant', "in today's"):
        if bad in text_of(body).lower(): W(f'avoid filler phrase "{bad}"')
    if re.search(r'\bTODO\b|\[citation needed\]|XXX', body): P('remove TODO or placeholder text')

    # built page
    page = os.path.join(PUB, 'blog', slug, 'index.html')
    if not os.path.exists(page): P('built page missing; run python3 build/generate_site.py')
    else:
        h = open(page, encoding='utf-8').read()
        types = [json.loads(j).get('@type') for j in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)]
        for t in ('Article', 'BreadcrumbList', 'FAQPage'):
            if t not in types: P(f'built page is missing {t} structured data')
        if f'<link rel="canonical" href="https://nevadainformation.com/blog/{slug}/">' not in h: P('canonical tag missing or wrong')
        if len(re.findall(r'<h1', h)) != 1: P('built page must have exactly one <h1>')
        if f'/blog/{slug}/' not in open(os.path.join(PUB, 'sitemap.xml')).read(): P('article missing from sitemap.xml')
        if f'/blog/{slug}/' not in open(os.path.join(PUB, 'blog', 'index.html')).read(): P('article missing from /blog/')
    return probs, warns


def main():
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
    arts = json.load(open(ARTS, encoding='utf-8'))
    slugs = [a['slug'] for a in arts] if sys.argv[1] == '--all' else [sys.argv[1]]
    total = 0
    for s in slugs:
        probs, warns = check(s, strict=sys.argv[1] != '--all')
        print(f'== {s}: {len(probs)} problem(s), {len(warns)} warning(s)')
        for p in probs: print('  PROBLEM:', p)
        for w in warns: print('  warning:', w)
        total += len(probs)
    print(f'Problems: {total}')
    sys.exit(1 if total else 0)


if __name__ == '__main__':
    main()
