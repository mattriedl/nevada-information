"""Hand-maintained Nevada content used by the generator: regions, utilities, school districts,
state-wide links and facts, and extra detail for the larger towns.

Keep facts here evergreen (no years in titles) and only add a figure when it has a source."""

# ---------------------------------------------------------------- regions
# Six regions built from whole counties. Order = display order.
REGIONS = {
    'Las Vegas & Southern Nevada': {
        'slug': 'las-vegas-southern-nevada', 'counties': ['Clark'],
        'desc': ('Clark County holds about three of every four Nevadans: the Las Vegas Valley cities of Las Vegas, Henderson and '
                 'North Las Vegas, the large unincorporated towns of Paradise, Spring Valley, Enterprise and Sunrise Manor that '
                 'surround the Strip, and outlying communities such as Boulder City, Mesquite, Laughlin and the Moapa Valley. '
                 'It is Mojave Desert country, with hot summers, mild winters, Lake Mead and Red Rock Canyon close to town.'),
        'living': 'The state\'s biggest job market (hospitality, gaming, construction, health care and logistics), the widest choice of housing, and RTC buses across the valley.',
        'visit': 'The Strip and downtown Fremont Street, Red Rock Canyon, Valley of Fire State Park, Hoover Dam and Lake Mead.',
    },
    'Reno-Tahoe': {
        'slug': 'reno-tahoe', 'counties': ['Washoe', 'Storey'],
        'desc': ('Reno and Sparks anchor the Truckee Meadows at the foot of the Sierra Nevada, with the Comstock mining town of '
                 'Virginia City in the hills above and the Nevada shore of Lake Tahoe at Incline Village. Washoe County runs north '
                 'past Pyramid Lake to the Black Rock Desert. Four distinct seasons, snow in the mountains and a fast-growing '
                 'industrial base along Interstate 80 east of Sparks.'),
        'living': 'A second big job market (logistics, manufacturing, the University of Nevada, Reno and tourism), and a quick drive to Lake Tahoe ski areas.',
        'visit': 'Downtown Reno and the Truckee River, Lake Tahoe\'s east shore, Pyramid Lake and Virginia City\'s boardwalks.',
    },
    'Carson City & Western Nevada': {
        'slug': 'carson-city-western-nevada', 'counties': ['Carson City', 'Douglas', 'Lyon'],
        'desc': ('The state capital, Carson City, sits between the Carson Range and the Pine Nut Mountains. South of it, the Carson '
                 'Valley towns of Minden and Gardnerville spread across ranch land, and Douglas County also takes in the Lake Tahoe '
                 'casinos at Stateline. Lyon County to the east covers Dayton, Fernley, Yerington and Silver Springs, one of the '
                 'faster-growing parts of the state.'),
        'living': 'Government and health-care jobs in Carson City, commuting distance to Reno, and more land per dollar than the Truckee Meadows.',
        'visit': 'The Nevada State Capitol and museums, Genoa (Nevada\'s first settlement), the Carson Valley and Lake Tahoe at Stateline.',
    },
    'Northeastern Nevada': {
        'slug': 'northeastern-nevada', 'counties': ['Elko', 'Humboldt', 'Pershing', 'Lander', 'Eureka'],
        'desc': ('Interstate 80 follows the Humboldt River across this high, open country of cattle ranches and gold mines. Elko is '
                 'the regional hub, with the Ruby Mountains rising behind it; Winnemucca, Battle Mountain, Lovelock and Eureka are '
                 'the county seats along the way, and West Wendover sits on the Utah line. Winters are cold and summers are dry and warm.'),
        'living': 'Well-paid mining jobs, a small-town pace and some of the most affordable housing in the state, with long drives between services.',
        'visit': 'Lamoille Canyon in the Ruby Mountains, the California Trail Interpretive Center, buckaroo heritage and hot springs.',
    },
    'Central Nevada': {
        'slug': 'central-nevada', 'counties': ['Churchill', 'Mineral', 'Nye', 'Esmeralda'],
        'desc': ('From the farm fields of Fallon to the old silver camps of Tonopah and Goldfield, central Nevada is a long stretch of '
                 'basins and ranges crossed by US 50 and US 95. Nye County, the third-largest county in the lower 48 by area, reaches '
                 'south to Pahrump, a fast-growing town an hour from Las Vegas. Hawthorne sits on Walker Lake in Mineral County.'),
        'living': 'Naval Air Station Fallon, mining and agriculture, low housing costs and wide-open space; Pahrump is a commuter town for Las Vegas.',
        'visit': 'Lahontan and Walker lakes, Tonopah\'s dark skies, the ghost towns of Esmeralda County and US 50 east of Fallon.',
    },
    'Eastern Nevada & Great Basin': {
        'slug': 'eastern-nevada-great-basin', 'counties': ['White Pine', 'Lincoln'],
        'desc': ('Ely, on US 50 and US 93, is the hub of White Pine County and the gateway to Great Basin National Park, home to '
                 'Wheeler Peak and ancient bristlecone pines. Lincoln County to the south is a land of small towns such as Pioche, '
                 'Caliente, Panaca and Alamo, with several state parks set in its canyons.'),
        'living': 'Small, close-knit communities, mining and ranching jobs, and hours of distance to the nearest big city.',
        'visit': 'Great Basin National Park, the Nevada Northern Railway in Ely, Cathedral Gorge State Park and Pioche\'s mining history.',
    },
}
REGION_OF = {c: r for r, v in REGIONS.items() for c in v['counties']}

# ---------------------------------------------------------------- utilities (confirm by address)
NV_ENERGY = ('NV Energy', 'https://www.nvenergy.com/')
ELECTRIC_COUNTY = {
    'Clark': [NV_ENERGY], 'Washoe': [NV_ENERGY], 'Storey': [NV_ENERGY], 'Carson City': [NV_ENERGY],
    'Douglas': [NV_ENERGY], 'Lyon': [NV_ENERGY], 'Churchill': [NV_ENERGY], 'Mineral': [NV_ENERGY],
    'Pershing': [NV_ENERGY], 'Humboldt': [NV_ENERGY], 'Lander': [NV_ENERGY],
    'Elko': [NV_ENERGY, ('Wells Rural Electric Company', 'https://www.wrec.coop/')],
    'Eureka': [('Mt. Wheeler Power', 'https://www.mwpower.net/'), NV_ENERGY],
    'White Pine': [('Mt. Wheeler Power', 'https://www.mwpower.net/')],
    'Lincoln': [('Lincoln County Power District No. 1', 'https://www.lcpd1.com/')],
    'Nye': [('Valley Electric Association', 'https://www.vea.coop/'), NV_ENERGY],
    'Esmeralda': [NV_ENERGY, ('Valley Electric Association', 'https://www.vea.coop/')],
}
ELECTRIC_PLACE = {
    'Boulder City': [('City of Boulder City Utilities', 'https://www.bcnv.org/')],
    'Mesquite': [('Overton Power District No. 5', 'https://www.opd5.com/')],
    'Bunkerville': [('Overton Power District No. 5', 'https://www.opd5.com/')],
    'Moapa Valley': [('Overton Power District No. 5', 'https://www.opd5.com/')],
    'Moapa Town': [('Overton Power District No. 5', 'https://www.opd5.com/')],
    'Logandale': [('Overton Power District No. 5', 'https://www.opd5.com/')],
    'Overton': [('Overton Power District No. 5', 'https://www.opd5.com/')],
    'Pahrump': [('Valley Electric Association', 'https://www.vea.coop/')],
    'Amargosa Valley': [('Valley Electric Association', 'https://www.vea.coop/')],
    'Elko': [NV_ENERGY], 'Carlin': [NV_ENERGY], 'Spring Creek': [NV_ENERGY],
    'Wells': [('Wells Rural Electric Company', 'https://www.wrec.coop/')],
    'West Wendover': [('Wells Rural Electric Company', 'https://www.wrec.coop/')],
}
GAS_NORTH_NVE = {'Washoe'}

# ---------------------------------------------------------------- schools: Nevada runs one district per county
SCHOOL_DISTRICTS = {
    'Carson City': ('Carson City School District', 'https://www.carsoncityschools.com/'),
    'Churchill': ('Churchill County School District', 'https://www.churchillcsd.com/'),
    'Clark': ('Clark County School District', 'https://www.ccsd.net/'),
    'Douglas': ('Douglas County School District', 'https://www.dcsd.k12.nv.us/'),
    'Elko': ('Elko County School District', 'https://www.ecsdnv.net/'),
    'Esmeralda': ('Esmeralda County School District', 'https://www.esmeraldacountyschools.com/'),
    'Eureka': ('Eureka County School District', 'https://www.eureka.k12.nv.us/'),
    'Humboldt': ('Humboldt County School District', 'https://www.hcsdnv.com/'),
    'Lander': ('Lander County School District', 'https://www.lander.k12.nv.us/'),
    'Lincoln': ('Lincoln County School District', 'https://www.lcsdnv.com/'),
    'Lyon': ('Lyon County School District', 'https://www.lyoncsd.org/'),
    'Mineral': ('Mineral County School District', 'https://nces.ed.gov/ccd/districtsearch/district_detail.asp?ID2=3200330'),
    'Nye': ('Nye County School District', 'https://www.nye.k12.nv.us/'),
    'Pershing': ('Pershing County School District', 'https://nces.ed.gov/ccd/districtsearch/district_detail.asp?ID2=3200420'),
    'Storey': ('Storey County School District', 'https://nces.ed.gov/ccd/districtsearch/district_detail.asp?ID2=3200450'),
    'Washoe': ('Washoe County School District', 'https://www.washoeschools.net/'),
    'White Pine': ('White Pine County School District', 'https://www.whitepine.k12.nv.us/'),
}

TRANSIT = {
    'Clark': ('RTC of Southern Nevada', 'https://www.rtcsnv.com/'),
    'Washoe': ('RTC Washoe', 'https://www.rtcwashoe.com/'),
    'Carson City': ('Jump Around Carson (JAC)', 'https://www.carson.org/'),
}

# ---------------------------------------------------------------- statewide links (checked by tools/check_links.py)
L = {
    'dmv': 'https://dmv.nv.gov/',
    'dmv_new': 'https://dmv.nv.gov/newresident.htm',
    'dmv_reg': 'https://dmv.nv.gov/newresident.htm',
    'sos_elections': 'https://www.nvsos.gov/sos/elections',
    'register': 'https://www.registertovotenv.gov/',
    'vote411': 'https://www.vote411.org/',
    'employnv': 'https://www.employnv.gov/',
    'detr': 'https://detr.nv.gov/',
    'access_nv': 'https://accessnevada.dwss.nv.gov/',
    'nv211': 'https://www.nevada211.org/',
    'healthlink': 'https://www.nevadahealthlink.com/',
    'three_square': 'https://www.threesquare.org/',
    'fbnn': 'https://fbnn.org/',
    'housing': 'https://housing.nv.gov/',
    'zillow': 'https://www.zillow.com/nv/',
    'apartments': 'https://www.apartments.com/nevada/',
    'nde': 'https://doe.nv.gov/',
    'nces': 'https://nces.ed.gov/ccd/schoolsearch/',
    'fcc': 'https://broadbandmap.fcc.gov/',
    'nvroads': 'https://www.nvroads.com/',
    'airnow': 'https://fire.airnow.gov/',
    'travel': 'https://travelnevada.com/',
    'parks': 'https://parks.nv.gov/',
    'tax': 'https://tax.nv.gov/',
    'nv_gov': 'https://nv.gov/',
    'southwest_gas': 'https://www.swgas.com/',
    'nve_gas': 'https://www.nvenergy.com/',
    'weather': 'https://forecast.weather.gov/',
}

STATE_LINKS = [
    ('Nevada DMV &mdash; new resident guide', L['dmv_new']),
    ('Register to vote in Nevada', L['register']),
    ('EmployNV &mdash; state job board', L['employnv']),
    ('Access Nevada &mdash; SNAP, Medicaid and cash assistance', L['access_nv']),
    ('Nevada 211 &mdash; local help by phone or online', L['nv211']),
    ('NVRoads &mdash; road conditions and closures', L['nvroads']),
    ('Nevada State Parks', L['parks']),
    ('Travel Nevada', L['travel']),
]

# ---------------------------------------------------------------- extra detail for larger towns
# Attractions only where the official site is known; tools/check_links.py drops links that stop working.
CUSTOM = {
    'Las Vegas': {
        'tagline': 'The neon capital of the Mojave and Nevada\'s largest city',
        'employers': 'MGM Resorts, Caesars Entertainment, Clark County School District, University Medical Center, Nellis Air Force Base',
        'attractions': [
            ('Fremont Street Experience', 'https://vegasexperience.com/', 'Downtown\'s covered pedestrian mall with a block-long LED canopy and free shows'),
            ('The Neon Museum', 'https://www.neonmuseum.org/', 'Guided walks through a boneyard of restored casino signs'),
            ('The Mob Museum', 'https://themobmuseum.org/', 'National museum of organized crime and law enforcement in a 1933 federal courthouse'),
            ('Springs Preserve', 'https://www.springspreserve.org/', '180 acres of gardens, trails and museums on the site of the valley\'s original springs'),
            ('Red Rock Canyon National Conservation Area', 'https://www.redrockcanyonlv.org/', 'A 13-mile scenic drive and sandstone hiking about 20 minutes west of town'),
        ],
    },
    'Henderson': {
        'tagline': 'Nevada\'s second-largest city, on the southeast edge of the Las Vegas Valley',
        'employers': 'Henderson Hospital, St. Rose Dominican hospitals, Green Valley Ranch, city of Henderson, logistics and distribution centers',
        'attractions': [
            ('Ethel M Chocolates Botanical Cactus Garden', 'https://www.ethelm.com/', 'A free cactus garden and chocolate factory viewing aisle'),
            ('Henderson Bird Viewing Preserve', 'https://www.cityofhenderson.com/', 'Ponds and trails popular with birders, run by the city'),
            ('Lake Las Vegas', None, 'A private lake ringed by resorts, a village center and golf courses'),
            ('Water Street District', None, 'Henderson\'s historic downtown with restaurants, events and the Water Street Plaza'),
        ],
    },
    'Reno': {
        'tagline': 'The Biggest Little City in the World, on the Truckee River',
        'employers': 'University of Nevada, Reno, Renown Health, Washoe County School District, Tesla and the Tahoe-Reno Industrial Center, casino resorts',
        'attractions': [
            ('National Automobile Museum', 'https://www.automuseum.org/', 'About 200 cars, many from the Harrah collection, set in period street scenes'),
            ('Nevada Museum of Art', 'https://www.nevadaart.org/', 'Nevada\'s largest art museum, in a building modeled on the Black Rock Desert'),
            ('Truckee River Whitewater Park', None, 'Kayak and tubing runs right through downtown at Wingfield Park'),
            ('The Reno Arch', None, 'The Virginia Street sign that has welcomed visitors since 1926 in one form or another'),
            ('Animal Ark Wildlife Sanctuary', 'https://www.animalark.org/', 'A nonprofit sanctuary for non-releasable predators north of Reno'),
        ],
    },
    'Sparks': {
        'tagline': 'A railroad town turned Reno\'s fast-growing neighbor',
        'employers': 'Tahoe-Reno Industrial Center employers, Northern Nevada Medical Center, Nugget Casino Resort, distribution centers',
        'attractions': [
            ('Sparks Marina Park', None, 'A man-made lake with a walking path, beach and fishing'),
            ('Victorian Square', None, 'Downtown plaza for events such as the Best in the West Nugget Rib Cook-off'),
            ('Wild Island Family Adventure Park', 'https://www.wildisland.com/', 'Water park, bowling and go-karts'),
        ],
    },
    'Carson City': {
        'tagline': 'Nevada\'s state capital, between the Sierra and the Pine Nut Mountains',
        'employers': 'State of Nevada, Carson Tahoe Health, Carson City School District, manufacturers along the US 50 corridor',
        'attractions': [
            ('Nevada State Museum', 'https://carsonnvmuseum.org/', 'Housed in the old Carson City Mint, with a walk-through mine replica'),
            ('Nevada State Railroad Museum', 'https://carsonrailroadmuseum.org/', 'Restored Virginia & Truckee Railroad locomotives and cars'),
            ('Nevada State Capitol', None, 'The 1871 silver-domed capitol, open for self-guided visits on weekdays'),
            ('Kit Carson Trail', None, 'A painted-line walking tour of historic homes and buildings'),
        ],
    },
    'Boulder City': {
        'tagline': 'The town that built Hoover Dam, and still has no casinos',
        'attractions': [
            ('Hoover Dam', 'https://www.usbr.gov/lc/hooverdam/', 'Tours of the 726-foot concrete arch-gravity dam on the Colorado River'),
            ('Lake Mead National Recreation Area', 'https://www.nps.gov/lake/', 'Boating, swimming and the Historic Railroad Trail through dam-era tunnels'),
            ('Boulder City/Hoover Dam Museum', None, 'Exhibits on the people who built the dam, in the historic Boulder Dam Hotel'),
        ],
    },
    'Elko': {
        'tagline': 'Hub of northeastern Nevada, under the Ruby Mountains',
        'employers': 'Nevada Gold Mines, Northeastern Nevada Regional Hospital, Elko County School District, Great Basin College',
        'attractions': [
            ('California Trail Interpretive Center', None, 'Exhibits and trails about the 1840s overland emigrants'),
            ('Northeastern Nevada Museum', 'https://museumelko.org/', 'Regional history, wildlife and art'),
            ('Western Folklife Center', 'https://www.westernfolklife.org/', 'Home of the National Cowboy Poetry Gathering'),
            ('Lamoille Canyon', None, 'A glacier-carved canyon in the Ruby Mountains, about 30 minutes southeast'),
        ],
    },
    'Ely': {
        'tagline': 'Copper-mining hub on US 50 and the gateway to Great Basin National Park',
        'attractions': [
            ('Nevada Northern Railway Museum', 'https://www.nnry.com/', 'A working railroad yard with steam excursions'),
            ('Great Basin National Park', 'https://www.nps.gov/grba/', 'Wheeler Peak, Lehman Caves and bristlecone pines, about 70 miles southeast'),
            ('Ward Charcoal Ovens State Historic Park', 'https://parks.nv.gov/parks/ward-charcoal-ovens', 'Six beehive-shaped 1870s charcoal kilns south of town'),
        ],
    },
    'Pahrump': {
        'tagline': 'A fast-growing valley town an hour west of Las Vegas',
        'attractions': [
            ('Pahrump Valley Winery', 'https://www.pahrumpwinery.com/', 'One of a handful of wineries in southern Nevada'),
            ('Death Valley National Park', 'https://www.nps.gov/deva/', 'The park\'s eastern entrances are about an hour from town'),
        ],
    },
    'Virginia City': {
        'tagline': 'The Comstock Lode boomtown, preserved on the side of Mount Davidson',
        'attractions': [
            ('Virginia & Truckee Railroad', 'https://www.virginiatruckee.com/', 'Steam and diesel excursions between Virginia City and Gold Hill'),
            ('Comstock History Center', None, 'Exhibits on the mines and railroad that made the Comstock'),
            ('Piper\'s Opera House', None, 'An 1885 opera house still used for performances'),
        ],
    },
    'Fallon': {
        'tagline': 'The Oasis of Nevada, farm town and home of Naval Air Station Fallon',
        'employers': 'Naval Air Station Fallon, Banner Churchill Community Hospital, agriculture, Churchill County School District',
        'attractions': [
            ('Churchill County Museum', 'https://www.ccmuseum.org/', 'Local history from Lahontan Valley settlers to the Navy'),
            ('Lahontan State Recreation Area', 'https://parks.nv.gov/parks/lahontan', 'A reservoir for boating, fishing and camping'),
            ('Grimes Point Archaeological Area', None, 'Petroglyph boulders along a short trail east of town'),
        ],
    },
    'Winnemucca': {
        'tagline': 'Humboldt County seat and a buckaroo town on Interstate 80',
        'attractions': [
            ('Humboldt Museum', None, 'Regional history in a restored church and annex buildings'),
            ('Buckaroo Hall of Fame', None, 'Saddles and stories of Great Basin cowboys, in the convention center'),
        ],
    },
    'Mesquite': {
        'tagline': 'A golf and retirement town on the Virgin River at the Arizona line',
        'attractions': [
            ('Virgin Valley Heritage Museum', None, 'Pioneer history of the Mesquite and Bunkerville area'),
        ],
    },
    'Laughlin': {
        'tagline': 'A Colorado River resort town at Nevada\'s southern tip',
        'attractions': [
            ('Laughlin Riverwalk', None, 'A walkway along the Colorado River past the casino resorts'),
            ('Grapevine Canyon', None, 'Hundreds of petroglyphs a short hike from the trailhead off State Route 163'),
        ],
    },
    'Tonopah': {
        'tagline': 'A silver-boom town at the crossroads of US 6 and US 95',
        'attractions': [
            ('Tonopah Historic Mining Park', 'https://www.tonopahminingpark.org/', 'Mine headframes, buildings and a walk-out over a stope'),
            ('Tonopah Stargazing Park', None, 'Some of the darkest skies in the continental US'),
        ],
    },
    'Incline Village': {
        'tagline': 'A forested Lake Tahoe community on Nevada\'s north shore',
        'attractions': [
            ('Lake Tahoe Nevada State Park (Sand Harbor)', 'https://parks.nv.gov/parks/sand-harbor', 'Clear water, granite boulders and the summer Shakespeare festival'),
            ('Diamond Peak Ski Resort', 'https://www.diamondpeak.com/', 'A community-owned ski area above town'),
        ],
    },
    'Stateline': {
        'tagline': 'Casino resorts on the Nevada side of South Lake Tahoe',
        'attractions': [
            ('Heavenly Mountain Resort', None, 'Ski runs that cross the California-Nevada line'),
            ('Zephyr Cove', None, 'Beach, marina and paddlewheeler cruises just north of town'),
        ],
    },
}
