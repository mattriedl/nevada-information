"""Nevada Information blog: article pages, the /blog/ index, and the blocks that link articles from
the home page, guides and city pages. Called by generate_site.py; not run on its own.

Articles: metadata in build/data/blog_articles.json, body HTML fragment in build/blog_content/<slug>.html.
See docs/blog/WRITING-GUIDE.md for the rules every article follows."""
import json, os, re
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ARTS_JSON = os.path.join(HERE, 'data', 'blog_articles.json')
CONTENT = os.path.join(HERE, 'blog_content')
CATEGORIES = ('Moving to Nevada', 'Living in Nevada', 'Visiting Nevada')


def load():
    if not os.path.exists(ARTS_JSON): return []
    arts = json.load(open(ARTS_JSON, encoding='utf-8'))
    arts = [a for a in arts if os.path.exists(os.path.join(CONTENT, a['slug'] + '.html'))]
    return sorted(arts, key=lambda a: (a['date'], a['slug']), reverse=True)


def body_of(a): return open(os.path.join(CONTENT, a['slug'] + '.html'), encoding='utf-8').read().strip()
def nice_date(iso): return date.fromisoformat(iso).strftime('%B %-d, %Y')
def words(html_): return len(re.sub(r'<[^>]+>', ' ', html_).split())
def text(h): return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', h)).replace('&amp;', '&').replace('&nbsp;', ' ').strip()


def city_posts(arts):
    """slug of each city page -> articles that link to it (for 'In our guides' blocks on city pages)."""
    out = {}
    for a in arts:
        for s in sorted(set(re.findall(r'href="/cities/([a-z0-9-]+)/"', body_of(a)))):
            out.setdefault(s, []).append(a)
    return out


def cards(arts, e):
    return '<ul class="posts">' + ''.join(
        f'<li><a href="/blog/{a["slug"]}/"><b>{e(a["title"])}</b></a><span class="m">{e(a["category"])}, {nice_date(a["date"])}</span>'
        f'<p>{e(a.get("excerpt") or a["description"])}</p></li>' for a in arts) + '</ul>'


def article_page(a, arts, c):
    e = c['e']; body = re.sub(r'(<table class="tbl">.*?</table>)', r'<div class="tbl-wrap">\1</div>', body_of(a), flags=re.S); path = f'/blog/{a["slug"]}/'; url = c['BASE_URL'] + path
    mod = a.get('dateModified') or a['date']; wc = words(body)
    heads = [(text(t), i) for i, t in re.findall(r'<h2 id="([^"]+)"[^>]*>(.*?)</h2>', body, re.S)]
    toc = c['toc_html']([(t if len(t) < 42 else t[:40].rsplit(' ', 1)[0] + '...', i) for t, i in heads])
    qa = [(text(q), text(ans)) for q, ans in re.findall(r'<details>\s*<summary>(.*?)</summary>(.*?)</details>', body, re.S)]
    imgs = [a['image']] + [u for u in re.findall(r'<img[^>]+src="(https?://[^"]+)"', body) if u != a.get('image')]
    pub = {'@type': 'Organization', 'name': 'Nevada Information', 'url': c['BASE_URL'] + '/',
           'logo': {'@type': 'ImageObject', 'url': c['BASE_URL'] + '/assets/og-image.png'}}
    lds = [{'@context': 'https://schema.org', '@type': 'Article', 'headline': a['title'], 'description': a['description'],
            'datePublished': a['date'], 'dateModified': mod, 'image': imgs, 'wordCount': wc, 'articleSection': a['category'],
            'keywords': ', '.join(a['keywords']), 'inLanguage': 'en-US', 'mainEntityOfPage': {'@type': 'WebPage', '@id': url},
            'author': {'@type': 'Organization', 'name': 'Nevada Information Editorial Team', 'url': c['BASE_URL'] + '/about/'}, 'publisher': pub},
           c['crumbs_ld']([('Home', '/'), ('Blog', '/blog/'), (a['title'], path)])]
    if qa:
        lds.append({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': ans}} for q, ans in qa]})
    hero_fig = (f'<figure class="photo lead"><img src="{e(a["image"])}" alt="{e(a["image_alt"])}" width="960" height="540" fetchpriority="high" decoding="async">'
                f'<figcaption><small>Photo: <a href="{e(a["image_page"])}" target="_blank" rel="noopener">{e(a["image_credit"])}</a> via Wikimedia Commons</small></figcaption></figure>')
    guide = ('/moving-to-nevada/', 'Read the moving to Nevada guide') if a['cta'] == 'moving' else ('/visit-nevada/', 'Plan a trip with the visiting Nevada guide')
    related = sorted([x for x in arts if x['slug'] != a['slug']], key=lambda x: (x['category'] != a['category'], x['date']), reverse=False)[:3]
    meta = f'{nice_date(a["date"])}' + (f', updated {nice_date(mod)}' if mod != a['date'] else '') + f'. {max(1, round(wc / 230))} min read'
    crumbs = [('Home', '/'), ('Blog', '/blog/'), (a['title'], path)]
    return (c['head'](a['seo_title'], a['description'], path, 'article', a['image'], lds) + c['header']('/blog/')
            + c['hero'](e(a.get('h1') or a['title']), e(a['hero_sub']), f'<span>{e(a["category"])}</span><span>{meta}</span>', a['slug'], crumbs)
            + f'<main id="main" class="wrap page">{toc}<article class="body prose post">{hero_fig}{body}'
            + f'<aside class="next"><p>{a_int(guide)} or browse <a href="/cities/">all {len(c["PLACES"])} Nevada cities and towns</a>.</p></aside>'
            + (f'<h2>More from the blog</h2>{cards(related, e)}' if related else '') + '</article></main>'
            + c['footer'](' Articles are general guidance; confirm details with the official source before you go.'))


def a_int(g): return f'<a href="{g[0]}">{g[1]}</a>'


def index_page(arts, c):
    e = c['e']; crumbs = [('Home', '/'), ('Blog', '/blog/')]
    body = cards(arts, e) if arts else '<p>The first articles are on the way.</p>'
    ld = {'@context': 'https://schema.org', '@type': 'Blog', 'name': 'Nevada Information Blog', 'url': c['BASE_URL'] + '/blog/',
          'blogPost': [{'@type': 'BlogPosting', 'headline': a['title'], 'url': f'{c["BASE_URL"]}/blog/{a["slug"]}/', 'datePublished': a['date']} for a in arts]}
    desc = c['fit_desc']('Researched guides to moving to, living in and visiting Nevada: Las Vegas and Reno neighborhoods, costs, seasonal events, hot springs and road trips.')
    return (c['head']('Nevada Information Blog: Moving, Living & Visiting', desc, '/blog/', ld_objs=(ld, c['crumbs_ld'](crumbs)))
            + c['header']('/blog/') + c['hero']('The Nevada Information blog', 'Researched guides for moving to, living in and visiting the Silver State', '', 'blog', crumbs)
            + f'<main id="main" class="wrap narrow">{body}</main>' + c['footer']())


def block(arts, title, e, n=4):
    if not arts: return ''
    return f'<h2>{title}</h2>{cards(arts[:n], e)}<p><a href="/blog/">All blog articles</a></p>'
