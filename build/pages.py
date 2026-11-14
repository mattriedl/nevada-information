"""Hand-written long-form pages: home, Nevada facts, moving guide, visiting guide.
Each function takes the generator's context dict (helpers + data) and returns HTML.
Figures here are evergreen or cited; update the sources list when a number changes."""
import json

STATE_EST_2024 = 3267467      # Census Vintage 2024 estimate, July 1, 2024
STATE_AREA_SQMI = 110571      # 2020 Gazetteer, land + water


def _src(c, items):
    return '<h2 id="sources">Sources</h2><ul class="links">' + ''.join(f'<li>{c["a_ext"](u, t)}</li>' for t, u in items) + '</ul>'


def home(c):
    e, n, slug = c['e'], c['n'], c['slug']
    names = [{'n': p['name'], 's': slug(p['name']), 'c': c['county_label'](p['county']), 'p': p['pop2020']} for p in c['RANKED']]
    regions = ''.join(f'<li><a href="/regions/{v["slug"]}/"><b>{e(r)}</b></a><span>{", ".join(c["county_label"](x) for x in v["counties"])}</span>'
                      f'<p>{e(v["desc"].split(". ")[0])}.</p></li>' for r, v in c['REGIONS'].items())
    big = ''.join(f'<li><a href="/cities/{slug(p["name"])}/">{e(p["name"])}</a><span>{e(c["county_label"](p["county"]))}, pop. {n(p["pop2020"])}</span></li>' for p in c['RANKED'][:12])
    cities = sum(p['type'] == 'city' for p in c['PLACES'])
    js = ("<script>(function(){var D=" + json.dumps(names, separators=(',', ':')) + ",q=document.getElementById('hq'),o=document.getElementById('hr');"
          "q.addEventListener('input',function(){var v=q.value.trim().toLowerCase();o.innerHTML='';if(!v)return;"
          "D.filter(function(x){return x.n.toLowerCase().indexOf(v)===0}).concat(D.filter(function(x){var i=x.n.toLowerCase().indexOf(v);return i>0}))"
          ".slice(0,8).forEach(function(x){var li=document.createElement('li'),a=document.createElement('a');a.href='/cities/'+x.s+'/';a.textContent=x.n;"
          "var s=document.createElement('span');s.textContent=x.c+', pop. '+x.p.toLocaleString();li.appendChild(a);li.appendChild(s);o.appendChild(li)});"
          "if(!o.children.length){o.innerHTML='<li>No town by that name. Try the <a href=\"/cities/\">full list</a>.</li>'}});"
          "q.form.addEventListener('submit',function(ev){ev.preventDefault();var f=o.querySelector('a');if(f)location.href=f.href})})();</script>")
    desc = c['fit_desc'](f'A guide to every Nevada city, town and county: population, ZIP codes, schools, weather and moving tips for {len(c["PLACES"])} places from Las Vegas to Elko.', 'Free and independent.')
    ld = {'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'Nevada Information', 'url': c['BASE_URL'] + '/'}
    return (c['head']('Nevada Information: Cities, Counties & Moving Guide', desc, '/', ld_objs=(ld,)) + c['header']()
            + c['hero']('Nevada, town by town', f'Population, ZIP codes, schools, weather and moving help for all {len(c["PLACES"])} cities and towns in the Silver State.', '', 'Nevada home')
            + '<main id="main" class="wrap">'
            + '<form class="search" role="search" style="max-width:560px"><label for="hq">Find a city or town</label><input id="hq" type="search" autocomplete="off" placeholder="Henderson, Pahrump, Elko&hellip;"></form>'
            + '<ul id="hr" class="near" aria-live="polite" style="max-width:760px"></ul>'
            + f'<p class="home-lede">Nevada had {n(c["STATE_POP2020"])} residents at the 2020 Census and an estimated {n(STATE_EST_2024)} by 2024. '
            + f'Only {cities} of its communities are incorporated cities; most people outside Las Vegas, Henderson, North Las Vegas, Reno and Sparks live in unincorporated towns run by their county. '
            + 'This site covers both.</p>'
            + '<div class="paths"><section><h3><a href="/moving-to-nevada/">Moving to Nevada</a></h3><p>Taxes, the 30-day DMV deadline, utilities, schools and how to choose a town.</p></section>'
            + '<section><h3><a href="/visit-nevada/">Visiting Nevada</a></h3><p>Red Rock and Valley of Fire, Lake Tahoe, Great Basin National Park and the long roads between them.</p></section>'
            + '<section><h3><a href="/nevada/">Nevada facts</a></h3><p>Statehood, geography, population, state symbols, time zones and area codes.</p></section></div>'
            + f'<h2>Six regions</h2><div class="split">{c["county_map"]()}<ul class="regions">{regions}</ul></div>'
            + c['blog_block'](c['ARTS'], 'Latest from the blog', 3)
            + f'<h2>Largest cities and towns</h2><ul class="near">{big}</ul><p><a href="/cities/">See all {len(c["PLACES"])} cities and towns</a> or <a href="/counties/">browse by county</a>.</p>'
            + '</main>' + js + c['footer'](' Population: U.S. Census Bureau.'))


def nevada(c):
    e, n = c['e'], c['n']
    rows = [('Statehood', 'October 31, 1864 (36th state)'), ('Capital', '<a href="/cities/carson-city/">Carson City</a>'),
            ('Largest city', '<a href="/cities/las-vegas/">Las Vegas</a>'), ('Population (2020 Census)', n(c['STATE_POP2020'])),
            ('Population estimate (2024)', n(STATE_EST_2024)), ('Total area', f'{n(STATE_AREA_SQMI)} sq mi (7th-largest state)'),
            ('Counties', '<a href="/counties/">16, plus the independent city of Carson City</a>'),
            ('Nicknames', 'The Silver State; Battle Born State'), ('Motto', 'All For Our Country'),
            ('Highest point', 'Boundary Peak, 13,147 ft'), ('Lowest point', 'Colorado River below Laughlin, about 480 ft'),
            ('Time zones', 'Pacific Time; West Wendover keeps Mountain Time'), ('Area codes', '<a href="/nevada-area-codes/">702, 725, 775</a>')]
    facts = ''.join(f'<tr><th scope="row">{a}</th><td>{b}</td></tr>' for a, b in rows)
    sym = [('State bird', 'Mountain bluebird'), ('State flower', 'Sagebrush'), ('State trees', 'Single-leaf piñon and bristlecone pine'),
           ('State animal', 'Desert bighorn sheep'), ('State reptile', 'Desert tortoise'), ('State fish', 'Lahontan cutthroat trout'), ('State metal', 'Silver')]
    symt = ''.join(f'<tr><th scope="row">{a}</th><td>{b}</td></tr>' for a, b in sym)
    clark = c['COUNTY']['Clark']['pop2020'] / c['STATE_POP2020'] * 100
    wash = c['COUNTY']['Washoe']['pop2020'] / c['STATE_POP2020'] * 100
    fq = [('When did Nevada become a state?', 'Nevada was admitted to the Union on October 31, 1864, during the Civil War, which is why its state flag and nickname say "Battle Born." Nevada Day is still a state holiday.', None),
          ('What is the capital of Nevada?', 'Carson City is the capital. Las Vegas is by far the largest city, and Reno is the largest in northern Nevada.', None),
          ('How many people live in Nevada?', f'Nevada had {n(c["STATE_POP2020"])} residents at the 2020 Census. The Census Bureau estimated {n(STATE_EST_2024)} in mid-2024. About {clark:.0f}% live in Clark County and {wash:.0f}% in Washoe County.', None),
          ('What time zone is Nevada in?', 'Nevada is on Pacific Time. The exception is West Wendover on the Utah line, which observes Mountain Time, as does the border town of Jackpot by local practice.', None),
          ('Why is Nevada called the Silver State?', 'The Comstock Lode silver strike near Virginia City in 1859 set off a mining rush that led to statehood five years later.', None)]
    faq_html, faq_ld = c['faq_block'](fq, 'Nevada facts: common questions')
    crumbs = [('Home', '/'), ('Nevada facts', '/nevada/')]
    body = (c['toc_html']([('Overview', 'overview'), ('Quick facts', 'facts'), ('People', 'people'), ('Land', 'land'), ('Symbols', 'symbols'), ('FAQ', 'faq')])
            + '<div class="body prose"><h2 id="overview">Overview</h2>'
            + '<p>Nevada sits almost entirely within the Great Basin, a region where rivers drain inward rather than to the sea, and the state is crossed by more than 300 north-south mountain ranges separated by flat valleys. '
            + 'The far south is Mojave Desert, home to Las Vegas, and the far west climbs into the Sierra Nevada at Lake Tahoe.</p>'
            + '<p>Mining built the state, starting with the Comstock Lode in 1859, and gold mining remains a major industry in northern Nevada. Legalized casino gambling in 1931 set Las Vegas and Reno on course to become resort cities.</p>'
            + f'<h2 id="facts">Quick facts</h2><div class="facts" style="grid-template-columns:1fr"><table>{facts}</table></div>'
            + f'<h2 id="people">People</h2><p>Nevada is one of the most urban states in the country despite its empty map: Clark County holds about {clark:.0f}% of residents, and Washoe County, centered on Reno, holds about {wash:.0f}%. '
            + 'The other 15 county areas share the remaining population across most of the state\'s land. See the <a href="/cities/">full list of cities and towns</a>.</p>'
            + '<h2 id="land">Land</h2><p>About 80 percent of Nevada is managed by federal agencies, chiefly the Bureau of Land Management, along with national forests, military ranges and national parks. '
            + 'That public land is why so much of the state is open for hiking, off-roading, hunting and camping, and also why towns rarely sprawl beyond their valleys.</p>'
            + f'<h2 id="symbols">State symbols</h2><div class="facts" style="grid-template-columns:1fr"><table>{symt}</table></div>'
            + faq_html + _src(c, [('U.S. Census Bureau: 2020 Census and Vintage 2024 estimates', 'https://www.census.gov/'),
                                  ('Nevada State Library: Nevada state symbols', 'https://nsla.nv.gov/'),
                                  ('Bureau of Land Management: Nevada', 'https://www.blm.gov/nevada')]) + '</div>')
    desc = c['fit_desc']('Nevada facts: statehood in 1864, capital Carson City, population, counties, geography, time zones, area codes and state symbols, with sources.', 'A quick reference.')
    return (c['head']('Nevada Facts: Capital, Population, Geography & Symbols', desc, '/nevada/', 'article', ld_objs=(c['crumbs_ld'](crumbs), faq_ld))
            + c['header']() + c['hero']('Nevada facts', 'The Silver State in figures', '', 'Nevada facts', crumbs)
            + f'<main id="main" class="wrap page">{body}</main>' + c['footer']())


def moving(c):
    e, n, slug = c['e'], c['n'], c['slug']
    big = ''.join(f'<li><a href="/cities/{slug(p["name"])}/">{e(p["name"])}</a><span>{e(c["county_label"](p["county"]))}, pop. {n(p["pop2020"])}</span></li>'
                  for p in c['RANKED'] if p['county'] != 'Clark' and p['pop2020'] > 15000)
    fq = [('Does Nevada have a state income tax?', 'No. Nevada does not tax personal income, including wages, pensions and Social Security benefits.', None),
          ('How long do I have to get a Nevada driver\'s license after moving?', 'New residents must get a Nevada driver\'s license and register their vehicles within 30 days of moving to the state.', None),
          ('What is the sales tax in Nevada?', 'The statewide minimum is 6.85%, and counties can add more. Clark County\'s combined rate is 8.375%, the highest in the state.', None),
          ('Do I need a smog check to register a car in Nevada?', 'Most gasoline and diesel vehicles registered in the urban parts of Clark and Washoe counties need an emissions test. Rural counties do not require one.', None),
          ('Can I register to vote online in Nevada?', 'Yes, with a current Nevada driver\'s license or ID card. Nevada also offers same-day registration in person during early voting and on Election Day.', None),
          ('Is Las Vegas or Reno cheaper to live in?', 'It depends on the neighborhood and the year, so compare current listings. Both are much more expensive than rural towns such as Elko, Fallon or Winnemucca, where housing is the biggest savings.', None)]
    faq_html, faq_ld = c['faq_block'](fq, 'Moving to Nevada: common questions')
    crumbs = [('Home', '/'), ('Moving to Nevada', '/moving-to-nevada/')]
    a = c['a_ext']; L = c['L']
    body = (c['toc_html']([('Checklist', 'checklist'), ('Taxes and costs', 'costs'), ('Choosing a town', 'towns'), ('Climate', 'climate'), ('Utilities', 'utilities'), ('Schools', 'schools'), ('FAQ', 'faq')])
            + '<div class="body prose">'
            + '<p>Nevada draws newcomers for its lack of a state income tax, its job markets in Las Vegas and Reno, and the open land in between. This guide covers the deadlines and costs that catch people out, and how to pick a town.</p>'
            + '<h2 id="checklist">First 30 days checklist</h2><ol>'
            + f'<li><strong>Driver\'s license:</strong> get a Nevada license within 30 days of becoming a resident ({a(L["dmv_new"], "DMV new resident guide")}). Book an appointment early; urban DMV offices are busy.</li>'
            + f'<li><strong>Vehicle registration:</strong> register your vehicles within the same 30 days. You will need Nevada insurance, and in the Las Vegas and Reno areas most vehicles need an emissions (smog) test first ({a(L["dmv_reg"], "registration requirements")}).</li>'
            + f'<li><strong>Voter registration:</strong> update it online once you have your Nevada license ({a(L["register"], "registertovotenv.gov")}). Active voters are mailed a ballot for each election unless they opt out.</li>'
            + '<li><strong>Utilities:</strong> set up electricity, gas, water and trash before move-in day; see below for who provides what.</li>'
            + '<li><strong>Schools:</strong> enroll children with the county school district, which assigns schools by address.</li></ol>'
            + '<h2 id="costs">Taxes and costs</h2>'
            + '<p><strong>No state income tax.</strong> Nevada does not tax wages, retirement income or Social Security. The state relies instead on sales tax and taxes on gaming and tourism.</p>'
            + '<p><strong>Sales tax</strong> is at least 6.85% everywhere in the state and reaches 8.375% in Clark County, which includes Las Vegas and Henderson.</p>'
            + '<p><strong>Property tax</strong> is limited by a partial abatement: for an owner-occupied primary home, the tax bill generally cannot rise more than 3% a year, regardless of how fast the assessed value climbs. Rental and second homes have a higher cap.</p>'
            + '<p><strong>Vehicle registration</strong> includes the Governmental Services Tax, based on the vehicle\'s original price and age, so the first registration of a newer car can cost more than newcomers expect.</p>'
            + f'<p>Check rates with the {a(L["tax"], "Nevada Department of Taxation")} and your county assessor before you buy.</p>'
            + '<h2 id="towns">Choosing a town</h2>'
            + '<p><strong>The Las Vegas Valley</strong> has most of the state\'s jobs and housing. Henderson and Summerlin South (west of the city) are popular with families; Paradise and Winchester are close to the Strip; North Las Vegas and Enterprise have much of the newer construction. See the <a href="/regions/las-vegas-southern-nevada/">Las Vegas &amp; Southern Nevada</a> region.</p>'
            + '<p><strong>Reno and Sparks</strong> offer four seasons and quick access to Lake Tahoe, with a job base in logistics, manufacturing and the university. Nearby Fernley, Dayton and Spanish Springs are lower-cost commuter options. See <a href="/regions/reno-tahoe/">Reno-Tahoe</a>.</p>'
            + '<p><strong>Carson City and the Carson Valley</strong> (Minden, Gardnerville) are quieter, with government and health-care jobs. <strong>Rural Nevada</strong> towns such as Elko, Winnemucca, Fallon and Ely have lower housing costs and mining or military jobs, but long drives to specialists and big-box shopping.</p>'
            + f'<p>Largest towns outside Clark County:</p><ul class="near">{big}</ul>'
            + '<h2 id="climate">Climate</h2><p>Southern Nevada is hot desert: summer highs above 100&deg;F are normal in Las Vegas, winters are mild, and rain is rare. Northern Nevada is high desert, at 4,000 feet and above, with cold winters, snow in the mountains, big day-night temperature swings and dry, warm summers. '
            + 'Wildfire smoke can affect air quality in summer statewide; check the <a href="https://fire.airnow.gov/" target="_blank" rel="noopener">AirNow fire and smoke map</a>.</p>'
            + '<h2 id="utilities">Utilities</h2><p>NV Energy provides electricity to most of the state, including Las Vegas, Reno and Carson City. Some areas are served by local cooperatives or districts instead, such as Valley Electric Association around Pahrump, Overton Power District No. 5 in the Moapa Valley and Mesquite, Mt. Wheeler Power around Ely and Wells Rural Electric in parts of Elko County. '
            + 'Natural gas comes from Southwest Gas in most of the state and NV Energy in the Reno area; many rural homes use propane. Each <a href="/cities/">city and town page</a> lists the providers for that area.</p>'
            + '<p>Southern Nevada gets about 90 percent of its water from the Colorado River through Lake Mead, and outdoor watering is restricted by season. Ask your water provider about landscaping rules before you plant a lawn.</p>'
            + f'<h2 id="schools">Schools</h2><p>Nevada has one public school district per county, so the Clark County School District serves all of the Las Vegas Valley and the Washoe County School District serves Reno, Sparks and Incline Village. Charter schools, many sponsored by the State Public Charter School Authority, are another option. Search schools by address with the {a(L["nces"], "NCES school search")} or the {a(L["nde"], "Nevada Department of Education")}.</p>'
            + c['blog_block']([x for x in c['ARTS'] if x['cta'] == 'moving'], 'More guides for moving to Nevada')
            + faq_html + _src(c, [('Nevada DMV: new residents', L['dmv_new']), ('Nevada Department of Taxation', L['tax']), ('Nevada Secretary of State: elections', L['sos_elections']),
                                  ('Southern Nevada Water Authority: water resources', 'https://www.snwa.com/'), ('U.S. Census Bureau: 2020 Census', 'https://www.census.gov/')]) + '</div>')
    desc = c['fit_desc']('Moving to Nevada: the 30-day DMV deadline, no state income tax, sales and property tax, utilities, schools, climate and how to choose a town.', 'A practical checklist.')
    return (c['head']('Moving to Nevada: Taxes, DMV, Utilities & Best Towns', desc, '/moving-to-nevada/', 'article', ld_objs=(c['crumbs_ld'](crumbs), faq_ld))
            + c['header']('/moving-to-nevada/') + c['hero']('Moving to Nevada', 'Deadlines, taxes, utilities and how to pick a town', '', 'moving', crumbs)
            + f'<main id="main" class="wrap page">{body}</main>' + c['footer']())


def visiting(c):
    a = c['a_ext']; L = c['L']
    spots = [
        ('Red Rock Canyon National Conservation Area', 'https://www.redrockcanyonlv.org/', 'las-vegas', 'Las Vegas', 'Sandstone cliffs and a 13-mile scenic drive about 20 minutes west of the Strip. Timed entry reservations are required for the drive in the busy season.'),
        ('Valley of Fire State Park', 'https://parks.nv.gov/parks/valley-of-fire', 'moapa-valley', 'Moapa Valley', 'Nevada\'s oldest state park, with red Aztec sandstone, petroglyphs and the Fire Wave hike, about an hour northeast of Las Vegas.'),
        ('Hoover Dam and Lake Mead', 'https://www.nps.gov/lake/', 'boulder-city', 'Boulder City', 'Tour the dam, then swim, boat or walk the Historic Railroad Trail in the national recreation area.'),
        ('Lake Tahoe\'s Nevada shore', 'https://parks.nv.gov/parks/sand-harbor', 'incline-village', 'Incline Village', 'Sand Harbor\'s clear water and boulders, the Tahoe East Shore Trail and ski areas above Incline Village and Stateline.'),
        ('Virginia City', 'https://www.virginiatruckee.com/', 'virginia-city', 'Virginia City', 'The Comstock boomtown, with wooden boardwalks, saloons, mine tours and steam train rides, 35 minutes from Reno.'),
        ('Great Basin National Park', 'https://www.nps.gov/grba/', 'ely', 'Ely', 'Wheeler Peak, Lehman Caves tours and 4,000-year-old bristlecone pines on the Utah line. Some of the darkest night skies in the country.'),
        ('Ruby Mountains and Lamoille Canyon', None, 'elko', 'Elko', 'An alpine canyon of glacier-carved walls and lakes above Elko, often called the Swiss Alps of Nevada.'),
        ('Pyramid Lake', None, 'reno', 'Reno', 'A desert lake on the Pyramid Lake Paiute Reservation, 40 minutes north of Reno; buy a tribal permit before fishing or camping.'),
        ('US 50, "The Loneliest Road"', None, 'fallon', 'Fallon', 'Fallon to Ely by way of Austin and Eureka: hundreds of miles of basins, ranges and historic mining towns.'),
    ]
    items = ''.join(f'<li>{a(u, c["e"](t)) if u else "<strong>" + c["e"](t) + "</strong>"}<span>{c["e"](d)} Nearest town: <a href="/cities/{s}/">{c["e"](tn)}</a>.</span></li>' for t, u, s, tn, d in spots)
    fq = [('When is the best time to visit Nevada?', 'Spring (March to May) and fall (September to November) are best for most of the state. Summer is ideal for Lake Tahoe and the high country but very hot in southern Nevada, and winter brings skiing near Reno and snow-closed roads in the mountains.', None),
          ('How do I check road conditions in Nevada?', 'Use NVRoads.com or dial 511 for closures, chain controls and construction from the Nevada Department of Transportation.', None),
          ('Do I need a reservation for Red Rock Canyon?', 'Timed-entry reservations are required for the Red Rock Canyon Scenic Drive during the busy season. Check the Bureau of Land Management\'s current rules before you go.', None),
          ('Is it safe to drive across rural Nevada?', 'Yes, with preparation. Gas stations can be 100 miles or more apart, cell service drops out between towns, and summer heat is dangerous, so fill up often and carry water.', None)]
    faq_html, faq_ld = c['faq_block'](fq, 'Visiting Nevada: common questions')
    crumbs = [('Home', '/'), ('Visiting Nevada', '/visit-nevada/')]
    body = (c['toc_html']([('Where to go', 'where'), ('When to go', 'when'), ('Driving', 'driving'), ('FAQ', 'faq')])
            + '<div class="body prose"><p>Most visitors see Las Vegas and Lake Tahoe. The rest of Nevada rewards a road trip: red-rock parks, alpine lakes, mining towns and national parks, separated by long empty highways.</p>'
            + f'<h2 id="where">Where to go</h2><ul class="list">{items}</ul>'
            + '<h2 id="when">When to go</h2><p>Spring and fall are the best seasons for hiking in southern Nevada; summer highs in Las Vegas regularly pass 100&deg;F. Northern Nevada and Lake Tahoe are at their best in summer and early fall, and the Reno-Tahoe area becomes a ski destination from December into spring.</p>'
            + f'<h2 id="driving">Driving tips</h2><ul><li>Check {a(L["nvroads"], "NVRoads")} or dial 511 before mountain drives, especially in winter.</li>'
            + '<li>Fill up whenever you can on rural highways; stretches of US 50, US 6 and US 95 run 100 miles or more without services.</li>'
            + '<li>Carry extra water, and do not rely on phone navigation alone in areas with no cell signal.</li>'
            + f'<li>Watch for open-range cattle and wildlife at night. Find more ideas at {a(L["travel"], "Travel Nevada")} and {a(L["parks"], "Nevada State Parks")}.</li></ul>'
            + c['blog_block']([x for x in c['ARTS'] if x['cta'] == 'visiting'], 'Nevada travel guides from our blog')
            + faq_html + _src(c, [('Nevada State Parks', L['parks']), ('National Park Service: Great Basin', 'https://www.nps.gov/grba/'), ('Bureau of Land Management: Red Rock Canyon', 'https://www.blm.gov/programs/national-conservation-lands/nevada/red-rock-canyon'),
                                  ('Nevada Department of Transportation: NVRoads', L['nvroads'])]) + '</div>')
    desc = c['fit_desc']('Visiting Nevada: Red Rock Canyon, Valley of Fire, Lake Tahoe, Virginia City, Great Basin National Park and US 50, plus when to go and road-trip tips.', 'Plan your trip.')
    return (c['head']('Visit Nevada: Best Places to Go & Road Trip Tips', desc, '/visit-nevada/', 'article', ld_objs=(c['crumbs_ld'](crumbs), faq_ld))
            + c['header']('/visit-nevada/') + c['hero']('Visiting Nevada', 'Beyond the Strip: parks, lakes and the long roads between them', '', 'visiting', crumbs)
            + f'<main id="main" class="wrap page">{body}</main>' + c['footer']())
