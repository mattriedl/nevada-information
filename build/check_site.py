#!/usr/bin/env python3
"""Checks the built site in public/: every internal link resolves, titles are under 70 characters,
meta descriptions are 150-160 characters, and (with --external) every outside link answers.
Run: python3 build/check_site.py [--external]"""
import glob, os, re, sys, html, urllib.request, concurrent.futures

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'public')
pages = sorted(glob.glob(f'{ROOT}/**/*.html', recursive=True))
bad, ext = [], {}
for f in pages:
    s = open(f, encoding='utf-8').read()
    rel = '/' + os.path.relpath(f, ROOT).replace('index.html', '')
    t = html.unescape(re.search(r'<title>(.*?)</title>', s).group(1))
    d = html.unescape(re.search(r'<meta name="description" content="(.*?)"', s).group(1))
    if len(t) > 70: bad.append(f'{rel}: title {len(t)} chars: {t}')
    if not f.endswith('404.html') and not 150 <= len(d) <= 160: bad.append(f'{rel}: description {len(d)} chars: {d}')
    if len(re.findall(r'<h1', s)) != 1: bad.append(f'{rel}: {len(re.findall("<h1", s))} h1 tags')
    for href in re.findall(r'href="([^"]+)"', s):
        href = html.unescape(href)
        if href.startswith(('http://', 'https://')):
            if 'nevadainformation.com' not in href and 'fonts.g' not in href: ext.setdefault(href, rel)
        elif href.startswith('/'):
            p = href.split('#')[0].split('?')[0]
            target = os.path.join(ROOT, p.lstrip('/'))
            if not (os.path.isfile(target) or os.path.isfile(os.path.join(target, 'index.html'))):
                bad.append(f'{rel}: broken internal link {href}')
print(f'{len(pages)} pages, {len(ext)} distinct external links')

if '--external' in sys.argv:
    def check(u):
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (compatible; NevadaInformationLinkCheck/1.0)'})
        try:
            with urllib.request.urlopen(req, timeout=25) as r: return u, r.status
        except urllib.error.HTTPError as e: return u, e.code
        except Exception as e: return u, type(e).__name__
    skip = ('nces.ed.gov/ccd/schoolsearch/school_detail', 'upload.wikimedia.org', 'commons.wikimedia.org', 'wikipedia.org')
    todo = [u for u in ext if not any(k in u for k in skip)]
    with concurrent.futures.ThreadPoolExecutor(12) as ex:
        for u, st in ex.map(check, todo):
            if st != 200 and st not in (401, 403, 405, 429):   # bot-blocking sites answer 403/429 but work in a browser
                bad.append(f'external {st}: {u} (first seen on {ext[u]})')
            elif st in (403, 429): print(f'  note {st} (likely bot-blocking): {u}')
for b in bad: print('FAIL', b)
print('OK' if not bad else f'{len(bad)} problems')
