"""Scheduled blog posts. Each goes live on its "date" (see build.py and the
publish-posts GitHub Action). Figures come from data/output/ (2023 values)."""

GDS_DATA = ('Gross Domestic Suffering. Country-year scores and methodology, 2000–2023.', 'https://github.com/ajbraus/gds')
HALE = ('World Health Organization. Healthy life expectancy (HALE) at birth. Global Health Observatory.', 'https://www.who.int/data/gho/data/indicators/indicator-details/GHO/gho-ghe-hale-healthy-life-expectancy-at-birth')
IMR = ('World Bank. Mortality rate, infant (per 1,000 live births). UN Inter-agency Group for Child Mortality Estimation.', 'https://data.worldbank.org/indicator/SP.DYN.IMRT.IN')
GII = ('UNDP. Gender Inequality Index. Human Development Report 2025.', 'https://hdr.undp.org/data-center/thematic-composite-indices/gender-inequality-index#/indicies/GII')
UNODC_DATA = ('UNODC. Intentional homicide victims. via Our World in Data.', 'https://ourworldindata.org/grapher/homicide-rate-unodc')
UCDP = ('Uppsala Conflict Data Program. Deaths in armed conflicts, by country where they occurred. via Our World in Data.', 'https://ourworldindata.org/grapher/death-rate-in-armed-conflicts')
WPB = ('Institute for Crime &amp; Justice Policy Research. World Prison Brief.', 'https://www.prisonstudies.org/')
GSI = ('Walk Free. Global Slavery Index 2023.', 'https://www.walkfree.org/global-slavery-index/')
FAO = ('UN Food and Agriculture Organization. Animals slaughtered for meat. via Our World in Data.', 'https://ourworldindata.org/grapher/animals-slaughtered-for-meat')
API = ('World Animal Protection. Animal Protection Index 2020.', 'https://api.worldanimalprotection.org/')
COBB = ('Cobb, C., Halstead, T., &amp; Rowe, J. (1995). If the GDP is up, why is America down? <em>The Atlantic</em>.', 'https://www.theatlantic.com/magazine/archive/1995/10/if-the-gdp-is-up-why-is-america-down/415807/')


def table(head, rows, highlight=None):
    th = "".join(f"<th scope=\"col\">{h}</th>" for h in head)
    body = []
    for r in rows:
        cls = ' class="highlight"' if highlight and r[1] == highlight else ""
        cells = f'<th scope="row">{r[0]}</th>' + "".join(f"<td>{c}</td>" for c in r[1:])
        body.append(f"                        <tr{cls}>{cells}</tr>")
    return f'''            <div class="table-wrap">
                <table class="compare">
                    <thead><tr>{th}</tr></thead>
                    <tbody>
{chr(10).join(body)}
                    </tbody>
                </table>
            </div>'''


def sup(n):
    return f'<sup><a href="#s{n}">{n}</a></sup>'


SCHEDULED = [
# ---------------------------------------------------------------------------
{
"slug": "best-countries-to-live-in",
"date": "2026-12-03",
"title": "The Best Countries to Live In, Ranked by Least Suffering",
"seo_title": "Best Countries to Live In: Ranked by Least Suffering (2023)",
"description": "Which are the best countries to live in? We rank 185 countries by preventable suffering: illness, violence, unfreedom, deprivation, gender inequality and animal suffering.",
"tag": "Rankings",
"excerpt": "Most \"best countries\" lists rank wealth or reputation. We ranked 185 countries by how much preventable suffering their people and animals endure. Japan comes first.",
"image": "/images/hero-earth-night.webp", "image_w": 2400, "image_h": 1200,
"image_alt": "Satellite composite of the Earth's city lights at night",
"credit": 'Earth\'s city lights. NASA Goddard Space Flight Center, <a href="https://commons.wikimedia.org/wiki/File:Earth%27s_City_Lights_by_DMSP,_1994-1995_(large).jpg" target="_blank" rel="noopener">public domain</a>.',
"og": "/images/og-best-countries-to-live-in.jpg",
"read": "7 min read",
"body": f'''
            <div class="callout tldr">
                <strong>The short answer</strong>
                <p>Measured by the least preventable suffering, the best countries to live in are <strong>Japan, Switzerland, Germany, Norway and Sweden</strong>. The United States ranks <strong>82nd of 185</strong>, behind China, Cuba and Vietnam. South Sudan, Ukraine, Haiti, Somalia and Nigeria carry the heaviest burdens.</p>
            </div>

            <h2>A different way to rank countries</h2>
            <p>Most "best countries to live in" lists rank income, reputation or how a panel of survey respondents feels about a place. Those lists tell you where life looks good from the outside. We asked a harder question: where do people, and animals, suffer least?</p>
            <p>The Gross Domestic Suffering (GDS) index scores every country from 0 (least suffering) to 100 (most) across six pillars:{sup(1)}</p>
            <ul>
                <li><strong>Illness:</strong> healthy years of life lost to disease, despair and early death, plus infant mortality.{sup(2)}{sup(3)}</li>
                <li><strong>Gender inequality:</strong> the UN's Gender Inequality Index.{sup(4)}</li>
                <li><strong>Violence:</strong> homicides plus deaths in war, per 100,000 people.{sup(5)}{sup(6)}</li>
                <li><strong>Unfreedom:</strong> prisoners plus people in modern slavery, per 100,000.{sup(7)}{sup(8)}</li>
                <li><strong>Deprivation:</strong> hunger, extreme poverty and forced displacement.</li>
                <li><strong>Animal suffering:</strong> land animals slaughtered per person, adjusted for weak protection laws.{sup(9)}</li>
            </ul>
            <p>Every pillar counts equally, and the scale never moves between years. A lower score means less suffering.</p>

            <h2>The 10 best countries to live in (2023)</h2>
{table(["Rank", "Country", "GDS score", "Weakest pillar"], [
    ("1", "Japan", "11.5", "Animal suffering"),
    ("2", "Switzerland", "12.4", "Animal suffering"),
    ("3", "Germany", "14.5", "Animal suffering"),
    ("4", "Norway", "14.6", "Animal suffering"),
    ("5", "Sweden", "14.7", "Animal suffering"),
    ("6", "Luxembourg", "15.2", "Unfreedom"),
    ("7", "Denmark", "16.7", "Animal suffering"),
    ("8", "Finland", "18.5", "Animal suffering"),
    ("9", "Netherlands", "18.9", "Animal suffering"),
    ("10", "Singapore", "18.9", "Animal suffering"),
])}
            <p>Japan tops the list because it scores near zero on almost every human pillar. People there lose only about 2.8 years of healthy life against our benchmark, fewer than 2 babies in 1,000 die before their first birthday, and the violent death rate is 0.2 per 100,000, one of the lowest in the world.</p>
            <p>Notice the pattern in the last column. Even the best countries to live in score poorly on animal suffering. The Netherlands and Denmark slaughter enough animals per person to score 91 and 79 out of 100 on that pillar. No country has solved every kind of suffering.</p>

            <h2>Where the largest countries rank</h2>
{table(["Rank", "Country", "GDS score"], [
    ("1", "Japan", "11.5"),
    ("3", "Germany", "14.5"),
    ("17", "United Kingdom", "24.8"),
    ("28", "China", "28.6"),
    ("63", "Vietnam", "41.4"),
    ("82", "United States", "45.3"),
    ("83", "India", "45.7"),
    ("98", "Russia", "49.7"),
    ("145", "Mexico", "59.9"),
    ("149", "Brazil", "61.5"),
    ("181", "Nigeria", "70.7"),
], highlight="United States")}

            <h2>Why the United States ranks 82nd</h2>
            <p>The world's largest economy ranks just ahead of India. Three pillars pull it down:</p>
            <ul>
                <li><strong>Unfreedom.</strong> About 542 of every 100,000 Americans are in prison, one of the five highest rates in the world, and Walk Free estimates another 330 per 100,000 live in modern slavery.{sup(7)}{sup(8)}</li>
                <li><strong>Animal suffering.</strong> The US slaughters about 29 land animals per person each year, among the most in the world.{sup(9)}</li>
                <li><strong>Illness and violence.</strong> Americans lose 10.4 years of healthy life against our benchmark, nearly four times as many as the Japanese, and die violently at 5 times the rate of the United Kingdom.</li>
            </ul>
            <p>Wealth helps, but how a society uses its wealth matters more. Dozens of poorer countries suffer less than the United States.</p>

            <h2>The countries with the most suffering</h2>
            <p>At the other end, South Sudan (185th), Ukraine (184th), Haiti, Somalia and Nigeria score above 70. War drives Ukraine's score. In South Sudan, Somalia and Haiti, violence, hunger and illness compound one another.</p>

            <h2>The good news: suffering is falling</h2>
            <p>83% of countries suffered less in 2023 than in 2000, and the population-weighted world score fell from 52.6 to 45.4. Among countries with more than 20 million people, China (down 16.3 points), Uzbekistan (down 15.7), Tanzania (down 14.7) and India (down 13.5) improved most, mainly through less illness, hunger and poverty, and in India's case much less gender inequality. Animal suffering rose in all four. Ukraine, Egypt and Mexico got worse.</p>
            <p>Suffering is not fixed. Countries have already cut it dramatically, which means the rest can too.</p>
''',
"sources": [GDS_DATA, HALE, IMR, GII, UNODC_DATA, UCDP, WPB, GSI, FAO],
},
# ---------------------------------------------------------------------------
{
"slug": "genuine-progress-indicator",
"date": "2026-12-17",
"title": "What Is the Genuine Progress Indicator (GPI)? A Plain-Language Guide",
"seo_title": "Genuine Progress Indicator (GPI): What It Is and How It Works",
"description": "The Genuine Progress Indicator adjusts GDP for inequality, pollution, crime and unpaid work. Learn how GPI is calculated, what it shows, and what it still misses.",
"tag": "Beyond GDP",
"excerpt": "The Genuine Progress Indicator corrects GDP by adding the good it ignores and subtracting the harm it counts as growth. Here is how it works and what it still misses.",
"image": "/images/environment-smog.webp", "image_w": 2000, "image_h": 731,
"image_alt": "Panorama of São Paulo under a layer of air pollution",
"credit": 'Air pollution over São Paulo. Wilfredor, <a href="https://commons.wikimedia.org/wiki/File:Panoramic_view_of_air_pollution_in_S%C3%A3o_Paulo_city,_Brazil.jpg" target="_blank" rel="noopener">CC0</a>.',
"og": "/images/og-genuine-progress-indicator.jpg",
"read": "7 min read",
"body": f'''
            <div class="callout tldr">
                <strong>The short answer</strong>
                <p>The <strong>Genuine Progress Indicator (GPI)</strong> starts with consumer spending, the core of GDP, then adds the value of unpaid work and subtracts costs such as inequality, crime, pollution and resource depletion. Studies using it find that genuine progress per person stalled in the late 1970s even as GDP kept rising.</p>
            </div>

            <h2>Where the GPI came from</h2>
            <p>In 1989, economist Herman Daly and theologian John Cobb proposed an Index of Sustainable Economic Welfare in their book <em>For the Common Good</em>.{sup(1)} In 1995, researchers at the think tank Redefining Progress refined it into the Genuine Progress Indicator and published the results under a famous headline in <em>The Atlantic</em>: "If the GDP is up, why is America down?"{sup(2)}</p>
            <p>Their argument was simple. GDP counts every dollar spent as progress, including the cost of cleaning up oil spills, treating preventable disease and locking people up. A better measure should separate the spending that makes life better from the spending that only repairs damage.</p>

            <h2>How the GPI is calculated</h2>
            <p>The GPI is measured in dollars, which makes it directly comparable with GDP. A typical calculation works in four steps:</p>
            <ol>
                <li><strong>Start with personal consumption</strong>, the largest part of GDP.</li>
                <li><strong>Adjust for inequality.</strong> An extra dollar means more to a poor family than a rich one, so consumption is discounted as inequality rises.</li>
                <li><strong>Add what GDP misses:</strong> the value of housework, parenting, volunteering and public infrastructure.</li>
                <li><strong>Subtract the costs:</strong> crime, family breakdown, commuting, lost leisure, air and water pollution, lost farmland and wetlands, depletion of non-renewable resources and long-term environmental damage.</li>
            </ol>

            <h2>What the GPI shows</h2>
            <p>The headline finding is sobering. A 2013 study in <em>Ecological Economics</em> estimated the GPI for 17 countries home to over half the world's people. Global GPI per person peaked in 1978 and then stalled, while GDP per person kept climbing.{sup(3)} Beyond a certain point, growth stopped turning into genuine progress.</p>
            <p>The GPI has also reached government. Maryland became the first US state to calculate a GPI and still publishes one.{sup(4)} In 2012, Vermont passed Act 113, which established a GPI to measure the state's economic, environmental and social well-being alongside gross state product.{sup(5)}</p>

            <h2>Strengths and weaknesses</h2>
            <h4>Strengths</h4>
            <ul>
                <li>It speaks GDP's language, so policymakers and economists can compare the two directly.</li>
                <li>It makes visible the costs that GDP counts as gains.</li>
                <li>It credits unpaid care work, most of it done by women.</li>
            </ul>
            <h4>Weaknesses</h4>
            <ul>
                <li><strong>Putting a price on everything.</strong> What is the dollar cost of a divorce, or of a lost wetland? Different researchers choose different values, so GPI results vary.</li>
                <li><strong>No global annual dataset.</strong> Unlike GDP, no agency publishes a GPI for every country every year, which makes country comparisons hard.</li>
                <li><strong>It still measures consumption.</strong> The starting point is spending, so a country can only score well by consuming more, carefully.</li>
                <li><strong>Animals don't count.</strong> The suffering of the tens of billions of animals raised for food each year has no place in it.</li>
            </ul>

            <h2>GPI vs. Gross Domestic Suffering</h2>
{table(["", "Genuine Progress Indicator", "Gross Domestic Suffering"], [
    ("Unit", "Dollars", "Score from 0 to 100 (higher = more suffering)"),
    ("Starts from", "Consumer spending", "Outcomes people and animals experience"),
    ("Coverage", "Selected countries, states and years", "185 countries, every year 2000–2023"),
    ("Counts violence and imprisonment?", "As dollar costs of crime", "Directly: violent deaths, prisoners, modern slavery"),
    ("Counts animal suffering?", "No", "Yes"),
])}
            <p>We see the two as allies. The GPI asks whether growth is worth what it costs. <a href="/">Gross Domestic Suffering</a> skips the price tags and counts the suffering itself, in deaths, illness, imprisonment, hunger and animals killed. Both lead to the same conclusion: GDP alone is a poor guide to whether life is getting better.</p>
            <p>Read more in our guides to <a href="/blog/alternative-to-gdp/">the best alternatives to GDP</a> and <a href="/blog/limitations-of-gdp/">the limitations of GDP</a>.</p>
''',
"sources": [
    ('Daly, H. E., &amp; Cobb, J. B. (1989). <em>For the Common Good: Redirecting the Economy Toward Community, the Environment, and a Sustainable Future</em>. Beacon Press.', None),
    COBB,
    ('Kubiszewski, I., et al. (2013). Beyond GDP: Measuring and achieving global genuine progress. <em>Ecological Economics</em>, 93, 57–68.', 'https://doi.org/10.1016/j.ecolecon.2013.04.019'),
    ('Maryland Department of Natural Resources. Maryland Genuine Progress Indicator.', 'https://dnr.maryland.gov/mdgpi/Pages/default.aspx'),
    ('Vermont General Assembly. (2012). Act No. 113 (S.237): Genuine progress indicator.', 'https://legislature.vermont.gov/Documents/2012/Docs/BILLS/S-0237/ACT113%20Act%20Summary.htm'),
],
},
# ---------------------------------------------------------------------------
{
"slug": "most-dangerous-countries",
"date": "2026-12-31",
"title": "The Most Dangerous Countries in the World, by Violent Death Rate",
"seo_title": "Most Dangerous Countries in the World (2023): Violent Death Rates",
"description": "Which are the most dangerous countries in the world? We rank countries by violent deaths per 100,000 people, combining homicide and war deaths, with 2023 data.",
"tag": "Rankings",
"excerpt": "Most danger rankings mix perceptions, politics and military spending. We counted the people actually killed, by murder or by war, per 100,000 people.",
"image": "/images/violence-mariupol.webp", "image_w": 1000, "image_h": 563,
"image_alt": "Apartment buildings in Mariupol, Ukraine, destroyed in the war",
"credit": 'Destroyed buildings in Mariupol, Ukraine. Mariupol City Council, <a href="https://commons.wikimedia.org/wiki/File:Destroyed_buildings_in_mariupol.jpg" target="_blank" rel="noopener">public domain</a>.',
"og": "/images/og-most-dangerous-countries.jpg",
"read": "6 min read",
"body": f'''
            <div class="callout tldr">
                <strong>The short answer</strong>
                <p>Counting homicides and war deaths together, the most dangerous places in 2023 were <strong>the West Bank and Gaza, Ukraine, Jamaica, Ecuador and Haiti</strong>. The safest large countries were <strong>Japan, Indonesia, South Korea and China</strong>. The United States had 5.8 violent deaths per 100,000 people, five times the rate of the United Kingdom.</p>
            </div>

            <h2>How we measure danger</h2>
            <p>Many "most dangerous countries" lists rely on the Global Peace Index, which blends 23 indicators, including military spending, weapons exports and how dangerous people <em>believe</em> their country is. We wanted something simpler: how many people were killed.</p>
            <p>Our violence measure adds two counts, per 100,000 people:</p>
            <ul>
                <li><strong>Homicides</strong>, from the UN Office on Drugs and Crime, with World Health Organization estimates where UN data is missing.{sup(1)}</li>
                <li><strong>Deaths in armed conflict</strong>, counted where they occurred, from the Uppsala Conflict Data Program.{sup(2)}</li>
            </ul>
            <p>A murder and a death in war end a life just the same, so we count both.</p>

            <h2>The most dangerous countries in 2023</h2>
            <p>Countries and territories with more than one million people, ranked by violent deaths per 100,000:</p>
{table(["Rank", "Country", "Violent deaths per 100k", "From homicide", "From war"], [
    ("1", "West Bank and Gaza", "485.5", "0.6", "484.9"),
    ("2", "Ukraine", "206.4", "3.8", "202.7"),
    ("3", "Jamaica", "49.4", "49.4", "0"),
    ("4", "Ecuador", "48.7", "45.7", "3.0"),
    ("5", "Haiti", "44.7", "41.2", "3.6"),
    ("6", "South Africa", "43.7", "43.7", "0"),
    ("7", "Trinidad and Tobago", "40.4", "40.4", "0"),
    ("8", "Lesotho", "38.9", "38.9", "0"),
    ("9", "Burkina Faso", "36.9", "9.3", "27.6"),
    ("10", "Sudan", "34.7", "5.3", "29.3"),
    ("11", "Mexico", "33.2", "24.9", "8.3"),
    ("12", "Honduras", "32.6", "31.4", "1.2"),
    ("13", "Somalia", "27.7", "5.0", "22.7"),
    ("14", "Colombia", "25.9", "24.9", "1.0"),
    ("15", "Central African Republic", "25.7", "18.1", "7.6"),
])}
            <p>The figure for the West Bank and Gaza reflects the war that began in October 2023. Several small Caribbean nations, such as St. Kitts and Nevis, have even higher homicide rates but fewer than a million people, so they are left out of this table. Their figures are in our open dataset.{sup(3)}</p>

            <h2>Two kinds of danger</h2>
            <p>The list splits cleanly in two. In Ukraine, Sudan, Burkina Faso and Somalia, most violent deaths come from war. In Jamaica, Ecuador, South Africa, Honduras and Mexico, nearly all come from homicide, with no war at all. A ranking that counted only war would call those countries peaceful.</p>
            <p>Homicide is the larger killer worldwide. The UN estimates that about 458,000 people were murdered in 2021, more than were killed by armed conflict and terrorism combined.{sup(4)}</p>

            <h2>The safest countries, and how others compare</h2>
{table(["Country", "Violent deaths per 100k"], [
    ("Japan", "0.2"),
    ("Indonesia", "0.3"),
    ("South Korea", "0.5"),
    ("China", "0.5"),
    ("Italy", "0.6"),
    ("Germany", "0.9"),
    ("United Kingdom", "1.1"),
    ("Canada", "2.0"),
    ("United States", "5.8"),
    ("Russia", "7.6"),
    ("Brazil", "20.4"),
], highlight="United States")}
            <p>The United States stands out among rich countries. Its violent death rate is about three times Canada's and 25 times Japan's.</p>

            <h2>Violence in the Gross Domestic Suffering index</h2>
            <p>Violence is one of six pillars in the <a href="/">Gross Domestic Suffering index</a>. We score it on a log scale from 0 to 100, so the difference between 1 and 10 deaths per 100,000 counts as much as the difference between 10 and 100. That keeps a single catastrophic war from swamping every other kind of suffering, while still placing countries at war near the bottom.</p>
            <p>See how violence combines with illness, unfreedom, deprivation, gender inequality and animal suffering in our ranking of <a href="/blog/best-countries-to-live-in/">the best countries to live in</a>.</p>
''',
"sources": [
    UNODC_DATA, UCDP, GDS_DATA,
    ('UNODC. (2023). Fifty-two people lost their lives to homicide globally every hour in 2021, says new report from UNODC. Global Study on Homicide 2023.', 'https://unodc.org/unodc/press/releases/2023/December/fifty-two-people-lost-their-lives-to-homicide-globally-every-hour-in-2021--says-new-report-from-unodc.html'),
],
},
# ---------------------------------------------------------------------------
{
"slug": "incarceration-rates-by-country",
"date": "2027-01-14",
"title": "Incarceration Rates by Country: How the US Compares",
"seo_title": "Incarceration Rates by Country: How the US Compares (2026)",
"description": "Incarceration rates by country, from El Salvador and the US to Japan and India, plus modern slavery: how many people each country holds against their will.",
"tag": "Unfreedom",
"excerpt": "About 11.5 million people are in prison worldwide, and 50 million more live in modern slavery. Here is how countries compare, and where the United States stands.",
"image": "/images/justice-prison.webp", "image_w": 1000, "image_h": 714,
"image_alt": "Cell block corridor in Philadelphia's historic Moyamensing Prison",
"credit": 'Moyamensing Prison, Philadelphia. Historic American Buildings Survey, Library of Congress, <a href="https://commons.wikimedia.org/wiki/File:Philadelphia_County_Prison_(Moyamensing_Prison)_Philadelphia_PA_(7)_139920pu.jpg" target="_blank" rel="noopener">public domain</a>.',
"og": "/images/og-incarceration-rates-by-country.jpg",
"read": "6 min read",
"body": f'''
            <div class="callout tldr">
                <strong>The short answer</strong>
                <p>El Salvador imprisons more of its people than any other country, about 1,659 per 100,000. The <strong>United States, at 542 per 100,000, has one of the five highest incarceration rates in the world</strong>, roughly four times the UK's and 16 times Japan's. Counting modern slavery too, Mauritania, Saudi Arabia and El Salvador hold the most people against their will.</p>
            </div>

            <h2>The highest incarceration rates in the world</h2>
            <p>The World Prison Brief collects official prison counts for almost every country. Its latest list puts the world's prison population at about 11.5 million people.{sup(1)}{sup(2)} Rates per 100,000 people, for the most recent year available:</p>
{table(["Rank", "Country", "Prisoners per 100k", "Year"], [
    ("1", "El Salvador", "1,659", "2024"),
    ("2", "Cuba", "794", "2020"),
    ("3", "Rwanda", "620", "2024"),
    ("4", "Turkmenistan", "576", "2021"),
    ("5", "United States", "542", "2023"),
    ("6", "Panama", "533", "2025"),
    ("7", "Tonga", "516", "2022"),
    ("8", "Turkey", "468", "2026"),
    ("9", "Cape Verde", "467", "2024"),
    ("10", "Uruguay", "449", "2024"),
], highlight="United States")}
            <p>The list excludes US territories such as American Samoa and Guam, which also have very high rates. El Salvador's rate soared after the government declared a state of emergency against gangs in 2022 and began mass arrests.</p>

            <h2>How the US compares with its peers</h2>
{table(["Country", "Prisoners per 100k"], [
    ("United States", "542"),
    ("Brazil", "416"),
    ("Russia", "300"),
    ("Australia", "170"),
    ("United Kingdom", "139"),
    ("France", "126"),
    ("China (2018)", "119"),
    ("Canada", "90"),
    ("Germany", "71"),
    ("Norway", "54"),
    ("India", "37"),
    ("Japan", "33"),
], highlight="United States")}
            <p>The US rate has fallen from a peak of 755 per 100,000 in 2008, but it remains far above every other wealthy democracy.{sup(1)}</p>

            <h2>Modern slavery: the hidden prisoners</h2>
            <p>Prison counts tell only part of the story. The International Labour Organization, Walk Free and the International Organization for Migration estimate that 50 million people lived in modern slavery in 2021: about 28 million in forced labour and 22 million in forced marriage.{sup(3)}</p>
            <p>Walk Free's Global Slavery Index estimates how common modern slavery is in each country.{sup(4)} The highest rates per 1,000 people:</p>
{table(["Country", "People in modern slavery per 1,000"], [
    ("North Korea", "104.6"),
    ("Eritrea", "90.3"),
    ("Mauritania", "32.0"),
    ("Saudi Arabia", "21.3"),
    ("Tajikistan", "14.0"),
    ("United Arab Emirates", "13.4"),
    ("Russia", "13.0"),
    ("United States", "3.3"),
], highlight="United States")}
            <p>Even the United States, at 3.3 per 1,000, has an estimated 1.1 million people in modern slavery.</p>

            <h2>Unfreedom in the Gross Domestic Suffering index</h2>
            <p>Prison and slavery both hold people against their will, so the <a href="/">Gross Domestic Suffering index</a> adds them together into one <strong>Unfreedom</strong> pillar: prisoners plus enslaved people per 100,000. On that combined measure, Mauritania (3,257), Saudi Arabia (2,270), El Salvador (2,197), Turkmenistan and Russia rank worst among countries with both figures available. The United States, at 872, ranks 73rd of 209.</p>
            <p>Not every prisoner is a victim, of course. But mass incarceration causes enormous suffering for prisoners, their families and their communities, and countries such as Norway and Japan keep crime low while imprisoning a fraction as many people. That makes high incarceration a form of preventable suffering.</p>
            <p>See how unfreedom combines with the other five pillars in our ranking of <a href="/blog/best-countries-to-live-in/">the best countries to live in</a>.</p>
''',
"sources": [
    WPB,
    ('Institute for Crime &amp; Justice Policy Research. (2024). Prison populations continue to rise in many parts of the world, with 11.5 million held in prisons worldwide. World Prison Population List, 14th edition.', 'https://icpr.org.uk/node/379'),
    ('International Labour Organization. (2022). 50 million people worldwide in modern slavery. Global Estimates of Modern Slavery.', 'https://www.ilo.org/resource/news/50-million-people-worldwide-modern-slavery-0'),
    GSI,
],
},
# ---------------------------------------------------------------------------
{
"slug": "gender-inequality-index",
"date": "2027-01-28",
"title": "The Gender Inequality Index, Explained: What It Measures and Who Ranks Worst",
"seo_title": "Gender Inequality Index (GII): Explained, With Country Rankings",
"description": "The UN's Gender Inequality Index measures women's losses in health, empowerment and work. Learn how the GII works, which countries rank best and worst, and where the US stands.",
"tag": "Gender inequality",
"excerpt": "The UN's Gender Inequality Index measures how much women lose to inequality in health, power and work. Denmark ranks best, Yemen worst, and the US only 45th.",
"image": "/images/gender-field.webp", "image_w": 1000, "image_h": 678,
"image_alt": "A woman cultivating a field with a hoe in a village in Guinea-Bissau",
"credit": 'Village life in Guinea-Bissau, 1974. Roel Coutinho, ASC Leiden, <a href="https://commons.wikimedia.org/wiki/File:ASC_Leiden_-_Coutinho_Collection_-_5_18_-_Village_life_in_Guinea-Bissau_-_Woman_cultivating_the_field_-_1974.tif" target="_blank" rel="noopener">CC BY-SA 4.0</a>.',
"og": "/images/og-gender-inequality-index.jpg",
"read": "6 min read",
"body": f'''
            <div class="callout tldr">
                <strong>The short answer</strong>
                <p>The <strong>Gender Inequality Index (GII)</strong> is a UN measure, from 0 (equality) to 1 (extreme inequality), of the losses women suffer in reproductive health, empowerment and the labour market. In 2023, Denmark (0.003) ranked best and Yemen (0.838) worst. The United States ranked 45th of 172.</p>
            </div>

            <h2>What the Gender Inequality Index measures</h2>
            <p>The UN Development Programme introduced the GII in its 2010 Human Development Report and publishes it every year.{sup(1)} It combines five indicators in three dimensions:</p>
{table(["Dimension", "Indicator"], [
    ("Reproductive health", "Maternal deaths per 100,000 live births"),
    ("Reproductive health", "Births per 1,000 women aged 15–19"),
    ("Empowerment", "Share of parliamentary seats held by women"),
    ("Empowerment", "Women and men aged 25+ with at least some secondary education"),
    ("Labour market", "Labour force participation of women and men"),
])}
            <p>A score of 0 means women and men fare equally. The closer a country gets to 1, the more women lose.</p>

            <h2>The countries with the least gender inequality</h2>
{table(["Rank", "Country", "GII (2023)"], [
    ("1", "Denmark", "0.003"),
    ("2", "Norway", "0.004"),
    ("3", "Sweden", "0.007"),
    ("4", "Switzerland", "0.010"),
    ("5", "Netherlands", "0.013"),
    ("6", "Finland", "0.021"),
    ("7", "Iceland", "0.024"),
    ("8", "Singapore", "0.031"),
])}

            <h2>The countries with the most gender inequality</h2>
{table(["Rank", "Country", "GII (2023)", "Maternal deaths per 100k births"], [
    ("172", "Yemen", "0.838", "183"),
    ("171", "Nigeria", "0.677", "1,047"),
    ("170", "Somalia", "0.675", "621"),
    ("169", "Chad", "0.670", "1,063"),
    ("168", "Afghanistan", "0.661", "620"),
    ("167", "Liberia", "0.646", "652"),
])}
            <p>Yemen ranks last because women are almost entirely shut out of public life: they hold 0.3% of parliamentary seats, and only about 6% are in the labour force. In Nigeria and Chad, more than 1 in 100 births ends in the mother's death.</p>

            <h2>Where the United States ranks</h2>
            <p>The US ranks 45th, with a GII of 0.169, behind Japan (22nd), Canada (18th) and the United Kingdom (31st). Women in the US are as educated as men, but two indicators drag the score down:</p>
            <ul>
                <li><strong>Maternal mortality:</strong> 21 deaths per 100,000 births, compared with fewer than 2 in Norway.</li>
                <li><strong>Teen births:</strong> 13 per 1,000 women aged 15–19, compared with fewer than 1 in South Korea.</li>
            </ul>
            <p>Women also hold only 28% of seats in Congress.</p>

            <h2>Is gender inequality falling?</h2>
            <p>Yes, slowly. The world's GII fell from 0.557 in 2000 to 0.455 in 2023. India, at 0.403, has cut its score by more than 40% since 2000.{sup(1)} At this pace, though, equality is generations away.</p>

            <h2>Gender inequality in the Gross Domestic Suffering index</h2>
            <p>The GII is one of six pillars in the <a href="/">Gross Domestic Suffering index</a>. We use it because the losses it measures, from mothers dying in childbirth to women shut out of work and power, are suffering that societies can prevent. Some of it overlaps with our Illness pillar, since maternal deaths also shorten healthy lives, but most of what the GII captures, such as political and economic exclusion, appears nowhere else.</p>
            <p>See how gender inequality combines with the other pillars in our ranking of <a href="/blog/best-countries-to-live-in/">the best countries to live in</a>.</p>
''',
"sources": [GII, GDS_DATA],
},
# ---------------------------------------------------------------------------
{
"slug": "animals-killed-for-food",
"date": "2027-02-11",
"title": "How Many Animals Are Killed for Food Each Year?",
"seo_title": "How Many Animals Are Killed for Food Each Year? (2023 Data)",
"description": "About 85 billion land animals were slaughtered for meat in 2023. See the numbers by species and country, how they have grown since 1961, and how we measure animal suffering.",
"tag": "Animal suffering",
"excerpt": "About 85 billion land animals were slaughtered for meat in 2023, more than 2,600 every second. Here is the data by species and country.",
"image": "/images/animals-cages.webp", "image_w": 1000, "image_h": 666,
"image_alt": "Egg-laying hens crammed into wire battery cages",
"credit": 'Hens in battery cages. Lever Foundation, <a href="https://commons.wikimedia.org/wiki/File:Subway_egg_supplier_investigation_-_birds_crammed_in_cages.jpg" target="_blank" rel="noopener">CC0</a>.',
"og": "/images/og-animals-killed-for-food.jpg",
"read": "6 min read",
"body": f'''
            <div class="callout tldr">
                <strong>The short answer</strong>
                <p>Farmers slaughtered about <strong>85 billion land animals for meat in 2023</strong>, more than 2,600 every second and about 10 for every person on Earth. Over 90% were chickens. The number has grown more than tenfold since 1961.</p>
            </div>

            <h2>Land animals slaughtered for meat, 2023</h2>
            <p>The UN Food and Agriculture Organization (FAO) counts the animals slaughtered for meat in every country.{sup(1)} For the seven main species:</p>
{table(["Species", "Animals slaughtered (2023)"], [
    ("Chickens", "77.0 billion"),
    ("Ducks", "4.2 billion"),
    ("Pigs", "1.5 billion"),
    ("Sheep", "710 million"),
    ("Goats", "570 million"),
    ("Turkeys", "520 million"),
    ("Cattle", "300 million"),
    ("<strong>Total</strong>", "<strong>84.7 billion</strong>"),
])}
            <p>These figures leave out fish, which the FAO reports in tonnes rather than individual animals. Counting fish would multiply the total many times over.</p>

            <h2>A tenfold increase since 1961</h2>
            <p>In 1961, farmers slaughtered about 7.9 billion land animals for meat. By 2000 the number had reached 45 billion, and by 2023, 84.7 billion. The world's population grew about 2.6 times over the same period, so the number of animals killed per person roughly quadrupled. Nearly all of that growth came from chickens, raised in ever larger industrial farms.</p>

            <h2>Which countries kill the most animals?</h2>
{table(["Country", "Land animals slaughtered (2023)"], [
    ("China", "16.2 billion"),
    ("United States", "9.9 billion"),
    ("Brazil", "6.4 billion"),
    ("Indonesia", "4.9 billion"),
    ("India", "3.6 billion"),
    ("Russia", "2.7 billion"),
    ("Mexico", "2.2 billion"),
])}
            <p>Per person, the picture changes. Among countries with more than a million people, Belarus (52 animals per person), Mauritius (40), Poland (36), Israel (31) and Brazil (30) slaughter the most. The United States slaughters 29 per person; India slaughters fewer than 3.</p>
            <p>The FAO counts animals where they are slaughtered, so countries that export a lot of meat, such as Brazil and the Netherlands, score high even though some of the meat is eaten abroad.</p>

            <h2>Does protection law make a difference?</h2>
            <p>Numbers alone don't capture how animals live. World Animal Protection's Animal Protection Index grades 50 countries from A (strongest protection) to G (weakest) on their animal welfare laws and policies.{sup(2)} No country earned an A in the 2020 edition. Six earned a B: Austria, Denmark, the Netherlands, Sweden, Switzerland and the United Kingdom. Azerbaijan and Iran received a G.</p>

            <h2>Animal suffering in the Gross Domestic Suffering index</h2>
            <p>Animal suffering is one of the six pillars of the <a href="/">Gross Domestic Suffering index</a>, weighted the same as human illness, violence and deprivation. Suffering does not stop at the species line.</p>
            <p>We measure it as land animals slaughtered per person, then adjust for the Animal Protection Index: a country graded B gets 20% less weight per animal, and a country graded G gets 30% more. Better laws reduce suffering per animal, but they never cancel out the number of animals killed.</p>
            <p>This pillar changes the rankings. Wealthy countries that eat a lot of meat, such as the United States, Australia and the Netherlands, score near the bottom on animal suffering even when they score well on human suffering. See the full picture in our ranking of <a href="/blog/best-countries-to-live-in/">the best countries to live in</a>.</p>
''',
"sources": [FAO, API, GDS_DATA],
},
]
