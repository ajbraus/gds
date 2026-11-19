"""Methods page: how the GDS index is built, and every adjustment we make to source data.
Keep in sync with pipeline/build_index.py."""
from layout import page, ORG, SITE, breadcrumbs_ld, breadcrumbs_html

UPDATED = "2026-11-19"


def _table(head, rows):
    th = "".join(f'<th scope="col">{h}</th>' for h in head)
    tr = "\n".join("                        <tr>" + "".join(
        (f'<th scope="row">{c}</th>' if i == 0 else f"<td>{c}</td>") for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'''            <div class="table-wrap">
                <table class="compare">
                    <thead><tr>{th}</tr></thead>
                    <tbody>
{tr}
                    </tbody>
                </table>
            </div>'''


def a(url, text):
    return f'<a href="{url}" target="_blank" rel="noopener">{text}</a>'


PILLARS = _table(["Pillar", "Indicator", "What it counts", "Source"], [
    ("Illness", "Premature adult death", "Probability of dying between ages 15 and 60, per 1,000", a("https://www.who.int/data/gho/data/indicators/indicator-details/GHO/adult-mortality-rate-(probability-of-dying-between-15-and-60-years-per-1000-population)", "WHO")),
    ("", "Infant mortality", "Deaths before age 1 per 1,000 live births", a("https://data.worldbank.org/indicator/SP.DYN.IMRT.IN", "World Bank / UN IGME")),
    ("", "Share of life lived in ill health", "(Life expectancy − healthy life expectancy) ÷ life expectancy", a("https://www.who.int/data/gho/data/themes/mortality-and-global-health-estimates/ghe-life-expectancy-and-healthy-life-expectancy", "WHO")),
    ("", "Alcohol and drug deaths", "Deaths from alcohol and drug use disorders, per 100,000", a("https://ourworldindata.org/grapher/death-rates-substance-disorders-who", "WHO Global Health Estimates")),
    ("Gender and sexual discrimination", "Gender Inequality Index (85%)", "Women's losses in reproductive health, empowerment and work (0–1)", a("https://hdr.undp.org/data-center/thematic-composite-indices/gender-inequality-index#/indicies/GII", "UNDP")),
    ("", "Anti-LGBTI laws (15%)", "Laws that criminalize or exclude LGBTI people, net of laws that protect them", a("https://ourworldindata.org/grapher/lgbt-rights-index", "Velasco, via Our World in Data")),
    ("Violence", "Violent deaths", "Homicides, deaths in armed conflict and suicides, per 100,000", a("https://dataunodc.un.org/", "UNODC") + ", " + a("https://ucdp.uu.se/", "UCDP") + ", " + a("https://www.who.int/data/gho/data/indicators/indicator-details/GHO/age-standardized-suicide-rates-(per-100-000-population)", "WHO")),
    ("Unfreedom", "People held captive", "Prisoners plus people in modern slavery, per 100,000", a("https://www.prisonstudies.org/", "World Prison Brief") + ", " + a("https://www.walkfree.org/global-slavery-index/", "Walk Free")),
    ("", "Overwork", "Share of workers working 49 or more hours a week", a("https://ilostat.ilo.org/", "ILO")),
    ("Deprivation", "Undernourishment", "Share of people without enough food", a("https://data.worldbank.org/indicator/SN.ITK.DEFC.ZS", "FAO")),
    ("", "Extreme poverty", "Share living on under $3.00 a day (2021 PPP)", a("https://data.worldbank.org/indicator/SI.POV.DDAY", "World Bank")),
    ("", "Forced displacement", "Refugees, asylum seekers and internally displaced people from the country, per 100,000", a("https://www.unhcr.org/refugee-statistics/", "UNHCR")),
    ("Animal suffering", "Farm-animal mistreatment", "Grade for laws protecting farm animals, A (strongest) = 0 to G (weakest) = 100", a("https://api.worldanimalprotection.org/", "World Animal Protection")),
])

GRADES = _table(["Farm-animal grade", "A", "B", "C", "D", "E", "F", "G"], [
    ("Animal suffering score", "0", "17", "33", "50", "67", "83", "100"),
])

ADJUSTMENTS = [
    ("Japan's overwork figure comes from Japan's own Labour Force Survey.",
     f'The ILO publishes no breakdown of working hours for Japan. We use the share of workers working 49+ hours a week from Japan\'s Labour Force Survey, as published by the Japan Institute for Labour Policy and Training ({a("https://www.jil.go.jp/english/jli/documents/2025/054-05.pdf", "JILPT")}): 23.1% in 2010, falling to 15.2% in 2023. JILPT\'s figures for other countries match the ILO\'s, so the two sources are comparable. China is also missing from the ILO data and, for now, has no overwork figure.'),
    ("Modern slavery is a single estimate, applied to every year.",
     "Walk Free's Global Slavery Index 2023 is the only edition with comparable country estimates, so the same figure is used for 2000–2023. Changes in the Unfreedom pillar over time therefore come from prison populations and working hours, not slavery."),
    ("Missing slavery estimates are filled from comparable neighbours.",
     "Walk Free does not estimate some small countries. For small Western European states we use the median of close neighbours: Iceland, the Faroe Islands and Greenland get the Nordic median; Luxembourg gets the median of Belgium, the Netherlands, Germany and France; Liechtenstein, Monaco, Andorra, San Marino, Malta, Gibraltar, the Channel Islands and the Isle of Man get their nearest neighbours. Other missing countries get the median of countries in the same World Bank region and income group. These countries are flagged as imputed."),
    ("Treatment of farm animals comes from 50 countries, with regional medians for the rest.",
     "World Animal Protection's Animal Protection Index (2020) grades the farm-animal laws of 50 countries from A (strongest) to G (weakest). Those countries eat 88% of the world's land animals. Every other country gets the median grade of rated countries in its World Bank region, flagged as imputed. The 2020 grades apply to every year, so this pillar does not change a country's trend over time. The Netherlands profile has no farm-animal section, so we use its overall grade, B."),
    ("The LGBTI index never stands in for missing gender data.",
     "It carries only 15% of its pillar, so where the Gender Inequality Index is missing the whole pillar counts as missing."),
    ("Missing suicide rates are filled from comparable countries.",
     "The WHO publishes no suicide rate for some very small states. They get the median of countries in the same World Bank region and income group, flagged as imputed."),
    ("Alcohol and drug deaths end in 2021.",
     "The WHO Global Health Estimates run from 2000 to 2021, so 2022 and 2023 carry the 2021 figure forward, flagged as imputed."),
    ("Homicide data uses WHO estimates where UN data is missing.",
     "Our first source is the UN Office on Drugs and Crime. Where it has no usable figure, we use the WHO's modelled homicide rate, flagged as imputed."),
    ("No record means zero for war deaths and displacement.",
     "The Uppsala Conflict Data Program records every armed conflict, so a country with no entry has no recorded conflict deaths. Likewise, a country UNHCR never lists as a place of origin has no recorded refugees or displaced people. War deaths are counted in the country where they occur."),
    ("Gaps between survey years are filled within each country.",
     "We interpolate linearly between observed years, and carry the first or last observation flat for up to 5 years (10 years for homicide, prison, poverty and working-hours data, which are published irregularly). We never borrow another country's data to fill a time gap. Every filled value is flagged, and each country-year reports its share of imputed values."),
    ("Very low hunger is reported as 2.5%.",
     "The FAO does not estimate undernourishment below 2.5%, so all countries under that threshold share the same best score."),
]


def build(write):
    path = "/methods/"
    trail = [("Home", "/"), ("Methods", path)]
    graph = [
        ORG,
        {"@type": "WebPage", "@id": SITE + path + "#page", "url": SITE + path,
         "name": "How the Gross Domestic Suffering index is built", "dateModified": UPDATED,
         "about": {"@id": SITE + "/#org"}},
        breadcrumbs_ld(trail),
    ]
    adj = "\n".join(f'''                <li><strong>{t}</strong> {d}</li>''' for t, d in ADJUSTMENTS)
    body = f'''        <section class="page-hero">
            <div class="container">
                {breadcrumbs_html(trail)}
                <p class="eyebrow">Methods</p>
                <h1>How the Gross Domestic Suffering index is built</h1>
                <p class="page-lead">Every data source, formula and adjustment behind the index, so anyone can check our work, challenge it, or rebuild it from the open code.</p>
            </div>
        </section>
        <div class="prose">
            <div class="callout tldr">
                <strong>In brief</strong>
                <p>We score 12 indicators of suffering for every country and every year from 2000 to 2023, scale each from 0 (least suffering) to 100 (most) against fixed goalposts, average them into six equally weighted pillars, and average the pillars into one score. Every indicator counts suffering, so higher is always worse.</p>
            </div>

            <h2>What we measure</h2>
            <p>The index measures the amount of suffering in people's lives, and in animals' lives, rather than how long lives last. Early death enters for a different reason: it causes some of the deepest suffering there is for the people left behind, from parents burying children to children losing a parent.</p>
{PILLARS}

            <h2>The formula</h2>
            <ol>
                <li><strong>Orient.</strong> Every indicator is framed so that a higher value means more suffering.</li>
                <li><strong>Transform.</strong> Rates that span orders of magnitude (deaths, prisoners, displaced people) are put on a log scale, so a change from 1 to 10 counts as much as a change from 10 to 100.</li>
                <li><strong>Scale with fixed goalposts.</strong> Each indicator is scaled from 0 to 100 between the 2.5th and 97.5th percentiles of all observed country-years, 2000–2023, and capped at 0 and 100. The farm-animal grade is already on a 0–100 scale. The goalposts never move between years, so a country's score changes only when its own data changes. This is what lets us compare a country with its own past, as well as with other countries.</li>
                <li><strong>Average into pillars.</strong> Each pillar is the average of its indicator scores. The one exception is Gender and sexual discrimination, weighted by the people each indicator covers: women are about half of people, and LGBTQ+ adults about 9% (<a href="https://www.ipsos.com/en/pride-month-2023-9-percent-of-adults-identify-as-lgbt">Ipsos, 2023</a>), so the Gender Inequality Index counts 85% and anti-LGBTI laws 15%.</li>
                <li><strong>Average into one score.</strong> The GDS score is the average of the six pillars, each weighted equally.</li>
            </ol>
            <p>A country is scored only when it has data for at least five of the six pillars, including Illness and Animal suffering.</p>

            <h2>Uncertainty</h2>
            <p>Equal weights are a judgment, not a fact. To show how much each rank depends on them, we recompute every country's rank under 1,000 random sets of pillar weights and publish the range covering 90% of results. A narrow range means the rank holds whatever weights you choose.</p>

            <h2>Deliberate choices</h2>
            <ul>
                <li><strong>Every violent death counts the same.</strong> Violence adds homicides, war deaths and suicides, which the WHO classifies as self-directed violence. Counting suicide this way, one death for one death, avoids giving a single cause of death the weight of a whole pillar. Deaths from alcohol and drug use disorders count in Illness.</li>
                <li><strong>Overwork is a form of unfreedom.</strong> Very long working hours take away people's control over their own time, so overwork sits in the Unfreedom pillar beside imprisonment and slavery. Captivity and overwork each make up half of the pillar.</li>
                <li><strong>Violence means people killed.</strong> We count homicides and war deaths directly rather than using the Global Peace Index, which mixes in military spending and perceptions and already includes incarceration.</li>
                <li><strong>Animals count, and what counts is how they are treated.</strong> Animal suffering carries the same weight as every human pillar. We measure treatment, not the amount of meat eaten: an animal raised well and slaughtered humanely suffers little.</li>
                <li><strong>Large, reliable datasets only.</strong> We use sources that cover nearly every country, year after year, from institutions such as the WHO, World Bank, UN agencies and FAO. We patch a gap only when another reliable source fills it cleanly, as with Japan's working hours. We accept a coarser picture rather than rely on thin or patchy data.</li>
            </ul>

            <h2>What we leave out, and why</h2>
            <ul>
                <li><strong>Loneliness, stress and daily negative emotions.</strong> Survey measures of feelings are not comparable with deaths, imprisonment or hunger, so we do not add them to the score.</li>
                <li><strong>Length of life itself.</strong> A long life is not less suffering in itself. We count early death for the grief it causes, and illness for the suffering it brings while people are alive.</li>
                <li><strong>Unemployment.</strong> Its harm shows up through poverty, illness and crime, which we measure directly.</li>
                <li><strong>Pollution and unsafe water.</strong> Their harm shows up as illness and early death, which we already count.</li>
                <li><strong>Loneliness and low-grade despair.</strong> The only global surveys of loneliness are proprietary and cover only recent years, so they cannot show trends since 2000.</li>
                <li><strong>Depression and anxiety.</strong> The only country-by-year estimates come from the Institute for Health Metrics and Evaluation, whose license forbids redistribution, so we cannot publish them in an open index.</li>
            </ul>

            <h2>Adjustments to source data</h2>
            <p>We use public sources as published, with the following exceptions. Each one is also documented in the code.</p>
            <ol>
{adj}
            </ol>


            <h3>Farm-animal grades</h3>
{GRADES}

            <h2>Known limitations</h2>
            <ul>
                <li><strong>Under-reported suicide.</strong> Some countries record far fewer suicides than occur, which makes their Violence score look better than it is.</li>
                <li><strong>Laws, not practice.</strong> The Animal Protection Index and the LGBTI policy index measure laws, not how animals are actually treated or how LGBTQ+ people are treated day to day.</li>
                <li><strong>Coarse animal data.</strong> Animal treatment rests on one set of grades, from 2020, for 50 countries. Other countries share their region's median grade, and the grades do not change over time.</li>
                <li><strong>Close scores.</strong> The leading countries are separated by a point or two, well within their rank ranges. Small differences in rank near the top should not be read as meaningful.</li>
                <li><strong>Small countries swing.</strong> Rates are per person, but in a state of 50,000 people a few extra murders move the rate a lot, so small countries' scores jump more from year to year.</li>
                <li><strong>Stale data.</strong> Some prison, homicide, poverty and working-hours figures are several years old and carried forward.</li>
            </ul>

            <h2>Open data and code</h2>
            <p>The full dataset (every country, every year, every indicator, raw and scaled, with imputation flags), the fixed goalposts and the code that builds them are on {a("https://github.com/ajbraus/gds", "GitHub")}. We welcome corrections and better data.</p>
            <p class="meta">Last updated {UPDATED}.</p>
        </div>'''
    write("methods/index.html", page("Methods: How the GDS Index Is Built | GDS",
          "Every data source, formula and adjustment behind the Gross Domestic Suffering index: six pillars, 12 indicators, fixed goalposts and open code.",
          path, graph, body, "methods"))
