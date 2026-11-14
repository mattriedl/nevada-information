#!/usr/bin/env python3
"""Downloads Wikipedia lead text and Wikimedia Commons photos for every place and county listed in
build/sources/wd.json, into build/sources/wiki.json and build/sources/images.json.

Resumable: entries already downloaded are skipped, so re-running only fills gaps.
Runs in GitHub Actions (.github/workflows/refresh-sources.yml) because Wikimedia rate-limits shared
cloud IPs heavily. Run locally: python3 build/fetch_sources.py
"""
import html as H, json, os, re, sys, time, urllib.parse, urllib.request
from urllib.parse import quote, unquote

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sources')
UA = 'NevadaInformationBot/1.0 (https://nevadainformation.com; site build script)'
wd = json.load(open(os.path.join(SRC, 'wd.json')))
WIKI, IMGS = os.path.join(SRC, 'wiki.json'), os.path.join(SRC, 'images.json')
wiki = json.load(open(WIKI)) if os.path.exists(WIKI) else {}
imgs = json.load(open(IMGS)) if os.path.exists(IMGS) else {}
DEADLINE = time.time() + float(os.environ.get('FETCH_MINUTES', '300')) * 60


def get(url):
    for attempt in range(8):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60).read().decode()
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            wait = int(e.headers.get('Retry-After') or 0) or 20 * (attempt + 1)
            print(f'  HTTP {e.code}, waiting {wait}s', flush=True); time.sleep(min(wait, 300))
        except Exception as e:
            print(f'  {type(e).__name__}, retrying', flush=True); time.sleep(10)
    return None


def lead_text(doc):
    m = re.search(r'<section data-mw-section-id="0"[^>]*>(.*?)</section>', doc or '', re.S)
    if not m: return ''
    out = []
    for p in re.findall(r'<p[^>]*>(.*?)</p>', m.group(1), re.S):
        p = re.sub(r'<sup[^>]*>.*?</sup>|<style.*?</style>', '', p, flags=re.S)
        p = re.sub(r'<span[^>]*class="[^"]*(?:IPA|rt-commentedText)[^"]*"[^>]*>.*?</span>', '', p, flags=re.S)
        t = re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', '', p))).strip()
        t = re.sub(r'\[\d+\]|\[citation needed\]', '', t)
        if len(t) > 40: out.append(t)
    return '\n'.join(out)


def clean(s): return re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', '', s or ''))).strip()


titles = sorted({unquote(v['article'].split('/wiki/')[1]) for v in wd.values() if v.get('article')})
for t in titles:
    if time.time() > DEADLINE: break
    o = wiki.setdefault(t, {})
    if o.get('extract') is not None and 'summary' in o: continue
    s = get('https://en.wikipedia.org/api/rest_v1/page/summary/' + quote(t, safe=''))
    if s:
        s = json.loads(s); o['summary'] = s.get('extract', '')
    h = get('https://en.wikipedia.org/api/rest_v1/page/html/' + quote(t, safe=''))
    o['extract'] = lead_text(h)
    json.dump(wiki, open(WIKI, 'w'), ensure_ascii=False)
    print('wiki', t, len(o['extract']), flush=True); time.sleep(1)

for g, v in wd.items():
    if time.time() > DEADLINE: break
    cat = v.get('commons')
    if not cat or g in imgs: continue
    q = {'action': 'query', 'generator': 'categorymembers', 'gcmtitle': 'Category:' + cat, 'gcmtype': 'file', 'gcmlimit': 40,
         'prop': 'imageinfo', 'iiprop': 'url|extmetadata|size|mime', 'iiurlwidth': 960, 'format': 'json'}
    d = get('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(q))
    if d is None: continue
    out = []
    for p in (json.loads(d).get('query', {}).get('pages', {}) or {}).values():
        ii = (p.get('imageinfo') or [{}])[0]
        if ii.get('mime') not in ('image/jpeg', 'image/png') or (ii.get('width') or 0) < 800: continue
        m = ii.get('extmetadata', {})
        out.append({'src': ii.get('thumburl'), 'file': p['title'][5:], 'page': ii.get('descriptionurl'),
                    'artist': clean(m.get('Artist', {}).get('value'))[:80], 'license': m.get('LicenseShortName', {}).get('value', ''),
                    'caption': clean(m.get('ImageDescription', {}).get('value'))[:200], 'w': ii.get('width'), 'h': ii.get('height')})
    imgs[g] = out
    json.dump(imgs, open(IMGS, 'w'), ensure_ascii=False)
    print('commons', cat, len(out), flush=True); time.sleep(1)

done_w = sum(1 for t in titles if wiki.get(t, {}).get('extract') is not None)
done_i = sum(1 for g, v in wd.items() if v.get('commons') and g in imgs)
print(f'Wikipedia: {done_w}/{len(titles)}  Commons: {done_i}/{sum(1 for v in wd.values() if v.get("commons"))}')
