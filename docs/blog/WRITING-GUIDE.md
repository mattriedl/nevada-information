# Nevada Information blog: writing and publishing guide

The rulebook for every article on the Nevada Information blog (`/blog/`). The scheduled blog task follows it
end to end; a human writer should too.

The site is an independent guide to Nevada for people **moving to, living in and visiting** the state.
Articles must be accurate, specific and useful, written for people rather than search engines. The bar is
Google's helpful-content and E-E-A-T standard: answer the search better than page one does.

---

## 1. Choose the topic and keywords (OpenSEO + web search)

OpenSEO project: **`b0a187c0-1e0d-40c4-90d3-ab449a316869`** (nevadainformation.com, US/English).
Budget about 150-400 credits per article. Never start a batch over 2,000 credits.

1. Read `docs/blog/topics.md` (backlog and published list) and the `keywords` of every article in
   `build/data/blog_articles.json`. Never reuse another article's primary keyword or search intent.
2. Check what is timely. Seasonal topics publish **2-6 weeks before** the season peaks (holiday events by
   mid-November, skiing and hot springs in December, spring wildflowers and Valley of Fire hiking in February,
   Lake Tahoe and summer road trips in April-May, Burning Man season in July). Use web search for current
   Nevada news and events.
3. Take the top backlog row (or a better timely idea) and confirm it:
   - `research_keywords` on 1-3 seeds (default 150 results). Keep Nevada-related rows only.
   - `get_keyword_metrics` on the shortlist (primary + 10-30 long tails).
   - `get_serp_results` for the primary keyword (depth 10): who ranks, what they cover, "People also ask".
   - Once Search Console is connected to the project, also use `get_search_console_performance`.
4. **One primary keyword**: real demand (ideally 500+/month or a cluster that adds up), difficulty preferably
   under 30, and a page one with blogs, forums or thin pages to outdo.
5. **4-9 secondary keywords**: long-tail variations and questions; they become H2/H3 headings and FAQs.
6. Record the choice in `docs/blog/topics.md` (move the row from Backlog to Published) and log it in OpenSEO with
   `update_project_context` → `appendResearchLog` (topic, primary keyword, volume/KD, credits used).
7. Save the primary and every secondary keyword to the project's saved keywords with OpenSEO `save_keywords`
   (no tags). `save_keywords` uses no credits. Pass `searchVolume` and `keywordDifficulty` only from the
   `get_keyword_metrics` / `research_keywords` results you already have from step 3; never make an extra paid call
   just to fill them in. A keyword without metrics is saved without them. Every keyword the site targets is kept
   there so rankings can be tracked later.

## 2. Research the facts

- Read primary sources with web search and WebFetch: nv.gov agencies (NDOT/NVRoads, Nevada State Parks,
  DMV, Department of Taxation), NPS, BLM, USFS, NOAA/NWS (weather.gov/vef and weather.gov/rev), county and city
  sites, LVCVA (visitlasvegas.com), Visit Reno Tahoe, Travel Nevada, and official event and business sites.
- Write down exact figures, dates, prices, hours, addresses and URLs as you go.
- **Never invent** statistics, quotes, prices, events, reviews or personal experiences. If a fact can't be
  verified, leave it out or tell the reader what to check.
- Give this season's dates only when an official source publishes them; otherwise "typically early December;
  check the official site".
- No photos of real people as the subject, and no private individuals' details.

## 3. Write the article

Files:
- Body: `build/blog_content/<slug>.html` (HTML fragment: no `<html>`, `<head>` or `<h1>`).
- Metadata: add an object to `build/data/blog_articles.json` (2-space indent, keep the list):

```json
{
  "slug": "christmas-in-las-vegas",
  "title": "Christmas in Las Vegas: Lights, Ice Skating, Events & What's Open",
  "seo_title": "Christmas in Las Vegas: Lights, Skating & Events",
  "h1": "Christmas in Las Vegas: Lights, Ice Skating, Events and What's Open",
  "description": "150-160 characters: primary keyword early, the concrete benefit, a reason to click.",
  "excerpt": "1-2 sentences for article lists.",
  "hero_sub": "1-2 sentences under the H1.",
  "date": "YYYY-MM-DD (today, America/Los_Angeles)",
  "dateModified": "same as date",
  "category": "Visiting Nevada | Living in Nevada | Moving to Nevada",
  "cta": "visiting | moving",
  "keywords": ["primary keyword", "secondary 1", "..."],
  "image": "https://thumb.wikimedia.org/... 960px thumbnail",
  "image_page": "https://commons.wikimedia.org/wiki/File:...",
  "image_credit": "Author / License",
  "image_alt": "Specific description of what the photo shows"
}
```

Rules:
- **Evergreen**: no years in the slug, title, seo_title, h1, description or keywords. Dates belong in the body.
- **seo_title** ≤ 60 characters, primary keyword first. **description** 150-160 characters.
- **Length** 1,800-3,000 words (1,500 minimum). Depth over padding.
- **Structure** (copy `build/blog_content/christmas-in-las-vegas.html`):
  1. `<p class="lede">` answers the search in 2-3 sentences, primary keyword bolded once in the first 100 words.
  2. `<div class="callout"><p>Quick answer</p><ul>...` with 4-6 bullet facts.
  3. 6-12 `<h2 id="...">` sections; `<h3 id="...">` for each place or item. The template builds the table of
     contents from the H2s, so **do not add your own TOC**. Phrase several H2s as the questions people search and
     answer each in a bolded first sentence.
  4. At least one comparison `<table class="tbl">`.
  5. For places, a `<div class="visit-card"><dl><dt>Address</dt><dd>...</dd>...</dl></div>`.
  6. `<h2 id="faq">` then `<div class="faq">` with 4-8 `<details><summary>Question?</summary><p>Answer</p></details>`
     (built into FAQPage schema). Use real "People also ask" questions.
  7. A closing paragraph with next steps and internal links, then `<p class="src">` on checking current details.
- **Internal links (6+)**: city names to `/cities/<slug>/` on first mention, plus `/counties/`, `/regions/`,
  `/visit-nevada/`, `/moving-to-nevada/`, `/nevada-zip-codes/`, and at least one related `/blog/<slug>/` once others
  exist. Root-relative, trailing slash. Unincorporated towns have pages too (Paradise, Spring Valley, Pahrump...).
- **External links (3+, 2+ official)**: cite inline where the fact appears, with `target="_blank" rel="noopener"`.
- **Photos**: the hero (metadata `image`) plus at least 2 in the body, Wikimedia Commons only, freely licensed.
  Confirm author and license on the file page. 960px thumbnail, `width`/`height`, `loading="lazy"`,
  `decoding="async"`, descriptive `alt`, and the credit:
  `<figure class="photo"><img ...><figcaption>Caption. <small>Photo: <a href="https://commons.wikimedia.org/wiki/File:..." target="_blank" rel="noopener">Author / License</a> via Wikimedia Commons</small></figcaption></figure>`.
  `build/data/places.json` lists verified Commons photos for most towns (`photos`: src, page, artist, license).
- **Voice**: plain, friendly US English. Short paragraphs, specific details (miles, prices, months), no hype or filler
  ("nestled", "bustling", "vibrant", "delve", "in conclusion"). Tell the reader what to do.
- **Safety**: heat, water and fuel warnings for desert trips; road and chain conditions for mountain trips; permits.
  No medical, legal or tax advice beyond summarizing official rules with a link.

## 4. Build and check (all must pass)

```bash
python3 build/generate_site.py                       # builds the whole site into public/, including the blog
python3 build/check_blog.py <slug>                   # must end "Problems: 0"
python3 build/check_blog.py --all | tail -1          # no new problems elsewhere
python3 build/check_site.py | tail -1                # internal links and every page's title/description: "OK"
```

Then view it like a reader: serve `public/` (`python3 -m http.server 8765` in `public/`) and load
`/blog/<slug>/` at 390px and 1280px wide (Playwright + Chrome). No sideways scrolling, photos load, FAQ opens.
Re-read the article once as an editor against your notes: every number, date, price and name.

## 5. Publish

- Commit with message `Blog: <title>`, a blank line, then the Co-Authored-By and Claude-Session trailers.
  Use `git -c user.name="Matt Riedl" -c user.email="mattriedl@users.noreply.github.com"`. Push to `main`
  (never a pull request). Pushing deploys the Cloudflare preview within a minute.
- Verify it is live: `https://nevada-information.mattriedl.workers.dev/blog/<slug>/` returns 200 with the new title.
  Once nevadainformation.com is live, check there too and submit the article URL, `/blog/` and linked city pages
  with OpenSEO `submit_indexnow_urls`.
- Never push an article that fails the checks. If you can't finish, leave it unpushed and report why.
