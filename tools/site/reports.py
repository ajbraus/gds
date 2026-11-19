"""Reports: suffering in the United States and in the world, 2000–2023, each with a PDF.

Charts read data/output/report_data.json (written by tools/site/report_data.py). The text
quotes figures from the same file and from data/output/; re-check it after a rebuild.
PDFs are printed from the built pages by tools/site/make_pdfs.sh."""
import json, os
from layout import page, ORG, SITE, breadcrumbs_ld, breadcrumbs_html

UPDATED = "2026-11-19"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = json.load(open(f"{ROOT}/data/output/report_data.json", encoding="utf8"))
YEARS = DATA["years"]

# Categorical slots 1-3 of the reference chart palette, validated on white
BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#8a8f9c"
PILLAR_NAMES = {"illness": "Illness", "discrimination": "Gender and sexual discrimination", "violence": "Violence",
                "unfreedom": "Unfreedom", "deprivation": "Deprivation", "animal_suffering": "Animal suffering"}

US_PDF = "/reports/gds-report-united-states-2023.pdf"
WORLD_PDF = "/reports/gds-report-global-2023.pdf"


def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def a(url, text):
    return f'<a href="{url}" target="_blank" rel="noopener">{text}</a>'


def sup(n):
    return f'<sup><a href="#s{n}">{n}</a></sup>'


def line_chart(title, series, lo, hi, note):
    """series: [(label, color, values by YEARS)]. Native SVG tooltips on every point; data table below."""
    W, H, L, R, T, B = 720, 320, 44, 150, 16, 34
    x = lambda i: L + i * (W - L - R) / (len(YEARS) - 1)
    y = lambda v: T + (hi - v) * (H - T - B) / (hi - lo)
    grid = "".join(f'<line x1="{L}" x2="{W - R}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="#e2dccf" stroke-width="1"/>'
                   f'<text x="{L - 8}" y="{y(v) + 4:.1f}" text-anchor="end" class="ax">{v}</text>'
                   for v in range(lo, hi + 1, 10))
    ticks = "".join(f'<text x="{x(i):.1f}" y="{H - 10}" text-anchor="middle" class="ax">{yr}</text>'
                    for i, yr in enumerate(YEARS) if yr % 5 == 0 or yr == YEARS[-1])
    lines, labels, ends = [], [], []
    for label, color, vals in series:
        pts = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(vals))
        lines.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
        lines.append("".join(f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="7" fill="transparent"><title>{label}, {YEARS[i]}: {v:.1f}</title></circle>'
                             for i, v in enumerate(vals)))
        ends.append([y(vals[-1]), label, color, vals[-1]])
    ends.sort()
    for k in range(1, len(ends)):  # keep end labels at least 30px apart
        ends[k][0] = max(ends[k][0], ends[k - 1][0] + 30)
    for ly, label, color, v in ends:
        cy = y(v)
        labels.append(f'<circle cx="{x(len(YEARS) - 1):.1f}" cy="{cy:.1f}" r="4" fill="{color}" stroke="#fff" stroke-width="2"/>'
                      f'<text x="{W - R + 12}" y="{ly - 2:.1f}" class="lbl">{label}</text>'
                      f'<text x="{W - R + 12}" y="{ly + 13:.1f}" class="val">{v:.1f}</text>')
    legend = "".join(f'<span><i style="background:{c}"></i>{l}</span>' for l, c, _ in series)
    head = "".join(f"<th scope=\"col\">{l}</th>" for l, _, _ in series)
    rows = "".join(f"<tr><th scope=\"row\">{yr}</th>" + "".join(f"<td>{s[2][i]:.1f}</td>" for s in series) + "</tr>"
                   for i, yr in enumerate(YEARS))
    return f'''            <figure class="chart">
                <figcaption class="chart-title">{title}</figcaption>
                {'<div class="chart-legend">' + legend + '</div>' if len(series) > 1 else ''}
                <svg viewBox="0 0 {W} {H}" role="img" aria-label="{title}">{grid}{ticks}{"".join(lines)}{"".join(labels)}</svg>
                <figcaption>{note}</figcaption>
                <details class="chart-data"><summary>Show the data</summary>
                    <div class="table-wrap"><table class="compare"><thead><tr><th scope="col">Year</th>{head}</tr></thead><tbody>{rows}</tbody></table></div>
                </details>
            </figure>'''


def bar_chart(title, groups, series, note):
    """Paired horizontal bars, 0-100. groups: [label]; series: [(label, color, [values])]."""
    W, L, R, row, bar = 720, 230, 56, 54, 14
    H = 20 + row * len(groups)
    x = lambda v: L + v * (W - L - R) / 100
    out = [f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="10" y2="{H - 6}" stroke="#e2dccf"/>'
           f'<text x="{x(v):.1f}" y="{H + 10}" text-anchor="middle" class="ax">{v}</text>' for v in range(0, 101, 25)]
    for gi, g in enumerate(groups):
        top = 16 + gi * row
        out.append(f'<text x="{L - 12}" y="{top + bar + 4}" text-anchor="end" class="lbl">{g}</text>')
        for si, (label, color, vals) in enumerate(series):
            v, by = vals[gi], top + si * (bar + 2)
            out.append(f'<rect x="{L}" y="{by}" width="{max(x(v) - L, 1):.1f}" height="{bar}" rx="4" fill="{color}"><title>{g}, {label}: {v:.0f}</title></rect>'
                       f'<text x="{x(v) + 6:.1f}" y="{by + bar - 3}" class="val">{v:.0f}</text>')
    legend = "".join(f'<span><i style="background:{c}"></i>{l}</span>' for l, c, _ in series)
    head = "".join(f"<th scope=\"col\">{l}</th>" for l, _, _ in series)
    rows = "".join(f"<tr><th scope=\"row\">{g}</th>" + "".join(f"<td>{s[2][i]:.1f}</td>" for s in series) + "</tr>"
                   for i, g in enumerate(groups))
    return f'''            <figure class="chart">
                <figcaption class="chart-title">{title}</figcaption>
                <div class="chart-legend">{legend}</div>
                <svg viewBox="0 0 {W} {H + 18}" role="img" aria-label="{title}">{"".join(out)}</svg>
                <figcaption>{note}</figcaption>
                <details class="chart-data"><summary>Show the data</summary>
                    <div class="table-wrap"><table class="compare"><thead><tr><th scope="col">Pillar</th>{head}</tr></thead><tbody>{rows}</tbody></table></div>
                </details>
            </figure>'''


def table(head, rows):
    th = "".join(f'<th scope="col">{h}</th>' for h in head)
    tr = "".join("<tr>" + "".join((f'<th scope="row">{c}</th>' if i == 0 else f"<td>{c}</td>") for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'''            <div class="table-wrap"><table class="compare"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'''


def sources(items):
    li = "\n".join(f'                <li id="s{i}">{t} {a(u, u.replace("https://", ""))}</li>' for i, (t, u) in enumerate(items, 1))
    return f'''            <section class="sources" aria-labelledby="sources-title">
                <h2 id="sources-title">Sources</h2>
                <ol>
{li}
                </ol>
            </section>'''


def report_page(write, slug, title, seo_title, description, eyebrow, lead, pdf, body):
    path = f"/reports/{slug}/"
    trail = [("Home", "/"), ("Reports", "/reports/"), (eyebrow, path)]
    graph = [
        ORG,
        {"@type": "Report", "@id": SITE + path + "#report", "url": SITE + path, "name": title,
         "description": description, "datePublished": UPDATED, "dateModified": UPDATED,
         "publisher": {"@id": SITE + "/#org"}, "inLanguage": "en",
         "encoding": {"@type": "MediaObject", "contentUrl": SITE + pdf, "encodingFormat": "application/pdf"}},
        breadcrumbs_ld(trail),
    ]
    html = f'''        <section class="page-hero report-hero">
            <div class="container">
                {breadcrumbs_html(trail)}
                <p class="eyebrow">Report · {eyebrow}</p>
                <h1>{title}</h1>
                <p class="page-lead">{lead}</p>
                <p class="report-actions"><a class="btn btn-primary" href="{pdf}" download>Download the PDF report</a></p>
            </div>
        </section>
        <article class="prose report">
            <p class="print-only report-print-head">Gross Domestic Suffering · Elton University · grossdomesticsuffering.org{path}</p>
{body}
            <p class="meta">Published {UPDATED} by the Gross Domestic Suffering team at Elton University. Data: 2000–2023. <a href="/methods/">How the index is built</a>.</p>
        </article>'''
    write(f"reports/{slug}/index.html", page(seo_title, description, path, graph, html, "reports"))


def us_report(write):
    us, rich, world = DATA["us"], DATA["rich"], DATA["world"]
    i0, i19 = 0, YEARS.index(2019)
    ui, ri = us["indicators"], rich["indicators_2023_median"]
    gap0, gap1 = us["gds"][0] - rich["gds"][0], us["gds"][-1] - rich["gds"][-1]
    trend = line_chart("GDS score, 2000–2023 (0 = least suffering, 100 = most)", [
        ("United States", BLUE, us["gds"]),
        ("Other rich countries", ORANGE, rich["gds"]),
        ("World", GRAY, world["gds"]),
    ], 30, 70, "“Other rich countries” and “World” are population-weighted averages. Rich countries are the World Bank’s high-income group, excluding the United States.")
    P = list(PILLAR_NAMES)
    pillars = bar_chart("Pillar scores, 2023 (higher = more suffering)", [PILLAR_NAMES[p] for p in P], [
        ("United States", BLUE, [us["pillars"][p][-1] for p in P]),
        ("Other rich countries", ORANGE, [rich["pillars_2023"][p] for p in P]),
    ], "Each pillar is scored from 0 to 100 against fixed goalposts. Other rich countries: population-weighted average.")
    ind = table(["Indicator", "US 2000", "US 2023", "Other rich countries, 2023 (median)"], [
        ("Deaths from alcohol and drug use disorders, per 100,000", f'{ui["substance_deaths"]["2000"]:.1f}', f'{ui["substance_deaths"]["2023"]:.1f}*', f'{ri["substance_deaths"]:.1f}'),
        ("Chance of dying between 15 and 60, per 1,000", f'{ui["premature_death"]["2000"]:.0f}', f'{ui["premature_death"]["2023"]:.0f}', f'{ri["premature_death"]:.0f}'),
        ("Share of life lived in ill health", f'{ui["ill_health_share"]["2000"]:.1f}%', f'{ui["ill_health_share"]["2023"]:.1f}%', f'{ri["ill_health_share"]:.1f}%'),
        ("Infant deaths per 1,000 live births", f'{ui["infant_mortality"]["2000"]:.1f}', f'{ui["infant_mortality"]["2023"]:.1f}', f'{ri["infant_mortality"]:.1f}'),
        ("Violent deaths (homicide, war, suicide) per 100,000", f'{ui["violence"]["2000"]:.1f}', f'{ui["violence"]["2023"]:.1f}', f'{ri["violence"]:.1f}'),
        ("Prisoners and people in modern slavery, per 100,000", f'{ui["captivity"]["2000"]:,.0f}', f'{ui["captivity"]["2023"]:,.0f}', f'{ri["captivity"]:,.0f}'),
        ("Workers putting in 49+ hours a week", f'{ui["overwork"]["2000"]:.1f}%', f'{ui["overwork"]["2023"]:.1f}%', f'{ri["overwork"]:.1f}%'),
        ("Gender Inequality Index (0–1)", f'{ui["gender_inequality"]["2000"]:.2f}', f'{ui["gender_inequality"]["2023"]:.2f}', f'{ri["gender_inequality"]:.2f}'),
    ])
    src = [
        ("Gross Domestic Suffering. Country-year scores, 2000–2023, and methods.", "https://grossdomesticsuffering.org/methods/"),
        ("World Health Organization. Global Health Estimates: deaths from alcohol and drug use disorders. via Our World in Data.", "https://ourworldindata.org/grapher/death-rates-substance-disorders-who"),
        ("World Health Organization. Adult mortality rate (probability of dying between 15 and 60 years per 1,000).", "https://www.who.int/data/gho/data/indicators/indicator-details/GHO/adult-mortality-rate-(probability-of-dying-between-15-and-60-years-per-1000-population)"),
        ("World Health Organization. Age-standardized suicide rates.", "https://www.who.int/data/gho/data/indicators/indicator-details/GHO/age-standardized-suicide-rates-(per-100-000-population)"),
        ("UNODC. Intentional homicide victims. via Our World in Data.", "https://ourworldindata.org/grapher/homicide-rate-unodc"),
        ("Centers for Disease Control and Prevention. Firearm injury and death: facts and statistics.", "https://www.cdc.gov/firearm-violence/data-research/facts-stats/index.html"),
        ("Institute for Crime &amp; Justice Policy Research. World Prison Brief.", "https://www.prisonstudies.org/"),
        ("Walk Free. Global Slavery Index 2023.", "https://www.walkfree.org/global-slavery-index/"),
        ("Sordo, L., et al. (2017). Mortality risk during and after opioid substitution treatment: systematic review and meta-analysis of cohort studies. <em>BMJ</em>, 357, j1550.", "https://doi.org/10.1136/bmj.j1550"),
        ("US Food and Drug Administration. (2023). FDA approves first over-the-counter naloxone nasal spray.", "https://www.fda.gov/news-events/press-announcements/fda-approves-first-over-counter-naloxone-nasal-spray"),
        ("World Health Organization. LIVE LIFE: limit access to the means of suicide.", "https://www.who.int/initiatives/live-life-initiative-for-suicide-prevention/limit-access-to-means-of-suicide"),
        ("Gunja, M. Z., et al. (2024). Insights into the U.S. maternal mortality crisis: an international comparison. Commonwealth Fund.", "https://www.commonwealthfund.org/publications/issue-briefs/2024/jun/insights-us-maternal-mortality-crisis-international-comparison"),
        ("Center for Economic and Policy Research. (2019). No-Vacation Nation, revised.", "https://cepr.net/no-vacation-nation-revised"),
        ("USDA National Agricultural Library. Humane Methods of Slaughter Act.", "https://www.nal.usda.gov/animal-health-and-welfare/humane-methods-slaughter-act"),
        ("World Animal Protection. Animal Protection Index 2020: United States of America.", "https://api.worldanimalprotection.org/country/usa"),
    ]
    body = f'''            <div class="callout tldr">
                <strong>Key findings</strong>
                <ul>
                    <li>Suffering in the United States fell only slightly, from a GDS score of {us["gds"][0]:.1f} in 2000 to {us["gds"][-1]:.1f} in 2023. The rest of the world improved faster, so the US slipped from <strong>{ordinal(us["rank"][0])} to {ordinal(us["rank"][-1])} of {us["n_ranked"][-1]} countries</strong>.{sup(1)}</li>
                    <li>The gap between the US and other rich countries widened from {gap0:.1f} to {gap1:.1f} points.</li>
                    <li>Deaths from alcohol and drug use disorders rose <strong>fivefold</strong>, from {ui["substance_deaths"]["2000"]:.1f} to {ui["substance_deaths"]["2023"]:.1f} per 100,000, about ten times the typical rich country.{sup(2)}</li>
                    <li>An American aged 15 is no more likely to reach 60 than in 2000, and violent deaths, mostly suicides, rose from {ui["violence"]["2000"]:.1f} to {ui["violence"]["2023"]:.1f} per 100,000.{sup(3)}{sup(4)}</li>
                    <li>The US made real progress on discrimination, incarceration and overwork, which shows that suffering responds to policy.</li>
                </ul>
            </div>

            <h2>The United States is falling behind</h2>
            <p>The Gross Domestic Suffering (GDS) index scores every country from 0 (least suffering) to 100 (most) across six equally weighted pillars: illness, gender and sexual discrimination, violence, unfreedom, deprivation and animal suffering. The goalposts never move, so a score can be compared across countries and over time.{sup(1)}</p>
            <p>In 2000 the United States scored {us["gds"][0]:.1f} and ranked {ordinal(us["rank"][0])}. By 2023 its score had improved to {us["gds"][-1]:.1f}, but its rank had fallen to {ordinal(us["rank"][-1])}. Other rich countries cut their average score from {rich["gds"][0]:.1f} to {rich["gds"][-1]:.1f}, more than twice the US improvement, and the world average fell from {world["gds"][0]:.1f} to {world["gds"][-1]:.1f}.</p>
{trend}
            <p>Of 36 high-income countries with more than 5 million people, only Saudi Arabia, Costa Rica and Russia suffered more than the United States in 2023. The country with the world's largest economy now ranks behind China, Albania, Kazakhstan and Türkiye.</p>

            <h2>Where Americans suffer most</h2>
{pillars}
            <p>The United States is worse than other rich countries on illness, violence and unfreedom, about level on animal suffering and deprivation, and slightly worse on discrimination. The table shows the indicators behind those pillars.</p>
{ind}
            <p class="table-note">* Deaths from alcohol and drug use disorders are published to 2021; 2023 carries the 2021 figure forward.</p>

            <h3>1. Addiction deaths have exploded</h3>
            <p>In 2000, {ui["substance_deaths"]["2000"]:.1f} Americans per 100,000 died of alcohol and drug use disorders. By 2021 the figure was {ui["substance_deaths"]["2023"]:.1f}, the highest of any high-income country and about ten times the median of other rich countries.{sup(2)} The rise accelerated after 2019, when the rate stood at {ui["substance_deaths"]["2019"]:.1f}.</p>

            <h3>2. Adults die young</h3>
            <p>An American aged 15 has an {ui["premature_death"]["2023"] / 10:.0f}% chance of dying before 60, the same as in 2000 and nearly twice the risk in other rich countries.{sup(3)} The risk spiked to 14% in 2021, during the COVID-19 pandemic. Americans also spend a growing share of their lives in ill health: {ui["ill_health_share"]["2023"]:.1f}% in 2023, up from {ui["ill_health_share"]["2000"]:.1f}% in 2000. Infant mortality improved, from {ui["infant_mortality"]["2000"]:.1f} to {ui["infant_mortality"]["2023"]:.1f} deaths per 1,000 births, but remains about 50% above the rich-country median.</p>

            <h3>3. Violent deaths are rising, driven by suicide</h3>
            <p>Homicides, war deaths and suicides together killed {ui["violence"]["2023"]:.1f} Americans per 100,000 in 2023, up from {ui["violence"]["2000"]:.1f} in 2000. Most of the rise came from suicide, which climbed from 10.9 to 14.0 per 100,000.{sup(4)} The homicide rate, 5.8 per 100,000 in 2023, is more than five times the median of other rich countries.{sup(5)} Guns tie the two together: more than half of the 44,000 firearm deaths in the United States in 2024 were suicides, and about a third were homicides.{sup(6)}</p>

            <h3>4. Mass incarceration is falling, but slowly</h3>
            <p>The share of Americans held in prison or modern slavery fell from {ui["captivity"]["2000"]:,.0f} to {ui["captivity"]["2023"]:,.0f} per 100,000. The prison rate fell from 683 to 542 per 100,000, still one of the five highest in the world, and Walk Free estimates another 330 per 100,000 live in modern slavery.{sup(7)}{sup(8)} The rich-country median is {ri["captivity"]:,.0f}.</p>

            <h3>5. Real progress on discrimination and overwork</h3>
            <p>The US Gender Inequality Index fell from {ui["gender_inequality"]["2000"]:.2f} to {ui["gender_inequality"]["2023"]:.2f}, and protections for LGBTI people grew stronger, including marriage equality in 2015. Together they cut the discrimination pillar from {us["pillars"]["discrimination"][0]:.0f} to {us["pillars"]["discrimination"][-1]:.0f}, the largest improvement of any US pillar. The share of workers putting in 49 or more hours a week fell from {ui["overwork"]["2000"]:.1f}% to {ui["overwork"]["2023"]:.1f}%, though it remains above the rich-country median of {ri["overwork"]:.1f}%.</p>

            <h3>6. Farm animals have weak protection</h3>
            <p>World Animal Protection gives US farm-animal law an E on its A-to-G scale.{sup(15)} The federal Humane Methods of Slaughter Act covers cattle, pigs, sheep and other livestock, but not chickens and turkeys, which are the great majority of animals slaughtered for food.{sup(14)}</p>

            <h2>Policy recommendations</h2>
            <p>Each recommendation targets a pillar where the United States trails other rich countries, and each rests on evidence that the policy reduces suffering.</p>
            <ol class="recs">
                <li><strong>Treat addiction as the health emergency it is.</strong> Make methadone and buprenorphine available to everyone with opioid use disorder. In a review of cohorts covering more than 120,000 people, those on methadone died at less than a third of the rate of those who had left treatment (11.3 versus 36.1 deaths per 1,000 people a year).{sup(9)} Distribute naloxone, now sold over the counter, wherever overdoses happen,{sup(10)} and use alcohol taxes and limits on sales to cut alcohol deaths.</li>
                <li><strong>Limit access to the means of suicide.</strong> The World Health Organization ranks limiting access to lethal means among the most effective ways to prevent suicide.{sup(11)} In the United States that means firearms: safe-storage laws, extreme risk protection orders and waiting periods, alongside the 988 crisis line.</li>
                <li><strong>Reduce violence where it concentrates.</strong> Fund community violence intervention and hospital-based programs in the neighborhoods with the highest homicide rates, and close gaps in background checks for gun sales.</li>
                <li><strong>Keep cutting incarceration.</strong> Prison rates have already fallen by a fifth since 2000. Sentencing reform, alternatives to prison for drug and low-level offenses, and parole reform can bring the US toward the rich-country median, without the crime rises critics fear: rich countries with far fewer prisoners also have far fewer homicides.</li>
                <li><strong>Protect mothers and babies.</strong> The United States has the highest maternal mortality of any high-income country, more than twice the rate of most.{sup(12)} Guarantee continuous health coverage through pregnancy and the first year after birth, and expand the midwife and obstetric workforce.</li>
                <li><strong>Guarantee paid leave.</strong> The United States is the only advanced economy that does not guarantee workers paid vacation or holidays.{sup(13)} A legal minimum of paid vacation, sick leave and parental leave would reduce overwork and the illness that comes with it.</li>
                <li><strong>Protect farm animals.</strong> Bring poultry under the Humane Methods of Slaughter Act, and set national standards to end extreme confinement such as battery cages and gestation crates.{sup(14)}</li>
                <li><strong>Measure what matters.</strong> Publish a national suffering report alongside GDP each year, so that progress against addiction, early death, violence and incarceration is tracked as closely as growth.</li>
            </ol>

            <h2>About this report</h2>
            <p>This report uses the Gross Domestic Suffering index, 2023 edition. Pillar scores, ranks and trends come from the open dataset; outside figures are cited. Equal pillar weights are a judgment: under 1,000 random weightings, the US ranks between 48th and 85th in 2023. Read <a href="/methods/">how the index is built</a>, or see <a href="/reports/global/">the global report</a>.</p>
{sources(src)}'''
    report_page(write, "united-states", "Suffering in the United States, 2000–2023",
                "Suffering in the United States, 2000–2023: Report | GDS",
                "The US has fallen from 43rd to 61st of 188 countries on the Gross Domestic Suffering index. Findings, trends and policy recommendations, with a downloadable PDF.",
                "United States",
                "The world’s largest economy has made little progress against suffering since 2000, and has fallen behind most rich countries. Here is where Americans suffer most, how that has changed, and what would reduce it.",
                US_PDF, body)


def world_report(write):
    w = DATA["world"]
    wi, P = w["indicators"], list(PILLAR_NAMES)
    g = w["gds"]
    i10, i19 = YEARS.index(2010), YEARS.index(2019)
    trend = line_chart("World GDS score, 2000–2023 (0 = least suffering, 100 = most)", [("World", BLUE, g)], 40, 70,
                       "Population-weighted average of all ranked countries.")
    pillars = bar_chart("World pillar scores, 2000 and 2023 (higher = more suffering)", [PILLAR_NAMES[p] for p in P], [
        ("2000", GRAY, [w["pillars"][p][0] for p in P]),
        ("2023", BLUE, [w["pillars"][p][-1] for p in P]),
    ], "Population-weighted averages. Farm-animal grades are from 2020 and apply to every year, so the animal pillar changes only as populations shift.")
    reg = sorted(w["regions"].items(), key=lambda kv: kv[1]["2023"])
    regions = table(["Region", "2000", "2023", "Change"], [
        (r.replace(", Afghanistan & Pakistan", ", Afghanistan and Pakistan").replace("&", "and"), f'{v["2000"]:.1f}', f'{v["2023"]:.1f}', f'{v["2023"] - v["2000"]:+.1f}') for r, v in reg])
    inc_order = ["High income", "Upper middle income", "Lower middle income", "Low income"]
    income = table(["Income group", "2000", "2023", "Change"], [
        (k.capitalize(), f'{w["income"][k]["2000"]:.1f}', f'{w["income"][k]["2023"]:.1f}', f'{w["income"][k]["2023"] - w["income"][k]["2000"]:+.1f}') for k in inc_order])
    ind = table(["Indicator (population-weighted)", "2000", "2019", "2023"], [
        ("Extreme poverty (% under $3 a day)", f'{wi["extreme_poverty"]["2000"]:.1f}%', f'{wi["extreme_poverty"]["2019"]:.1f}%', f'{wi["extreme_poverty"]["2023"]:.1f}%'),
        ("Undernourishment (% of people)", f'{wi["undernourishment"]["2000"]:.1f}%', f'{wi["undernourishment"]["2019"]:.1f}%', f'{wi["undernourishment"]["2023"]:.1f}%'),
        ("Infant deaths per 1,000 live births", f'{wi["infant_mortality"]["2000"]:.1f}', f'{wi["infant_mortality"]["2019"]:.1f}', f'{wi["infant_mortality"]["2023"]:.1f}'),
        ("Chance of dying between 15 and 60, per 1,000", f'{wi["premature_death"]["2000"]:.0f}', f'{wi["premature_death"]["2019"]:.0f}', f'{wi["premature_death"]["2023"]:.0f}'),
        ("Gender Inequality Index (0–1)", f'{wi["gender_inequality"]["2000"]:.2f}', f'{wi["gender_inequality"]["2019"]:.2f}', f'{wi["gender_inequality"]["2023"]:.2f}'),
        ("Violent deaths (homicide, war, suicide) per 100,000", f'{wi["violence"]["2000"]:.1f}', f'{wi["violence"]["2019"]:.1f}', f'{wi["violence"]["2023"]:.1f}'),
        ("Forcibly displaced people per 100,000", f'{wi["displacement"]["2000"]:,.0f}', f'{wi["displacement"]["2019"]:,.0f}', f'{wi["displacement"]["2023"]:,.0f}'),
        ("Prisoners and people in modern slavery, per 100,000", f'{wi["captivity"]["2000"]:,.0f}', f'{wi["captivity"]["2019"]:,.0f}', f'{wi["captivity"]["2023"]:,.0f}'),
    ])
    nm = lambda n: {"Russian Federation": "Russia", "Turkiye": "Türkiye", "Syrian Arab Republic": "Syria", "Yemen, Rep.": "Yemen"}.get(n, n)
    best = ", ".join(f"{nm(n)} ({v:+.1f})" for n, v in w["big_improvers"][:4])
    worst = ", ".join(f"{nm(n)} ({v:+.1f})" for n, v in w["big_worse"][:6])
    src = [
        ("Gross Domestic Suffering. Country-year scores, 2000–2023, and methods.", "https://grossdomesticsuffering.org/methods/"),
        ("FAO, IFAD, UNICEF, WFP and WHO. (2024). Hunger numbers stubbornly high for three consecutive years as global crises deepen. The State of Food Security and Nutrition in the World 2024.", "https://www.fao.org/newsroom/detail/hunger-numbers-stubbornly-high-for-three-consecutive-years-as-global-crises-deepen--un-report/en"),
        ("UNHCR. (2024). Global Trends: Forced Displacement in 2023.", "https://www.unhcr.org/publications/global-trends-2023"),
        ("Walk Free. Global Slavery Index 2023.", "https://www.walkfree.org/global-slavery-index/"),
        ("Egger, D., Haushofer, J., Miguel, E., Niehaus, P., &amp; Walker, M. (2022). General equilibrium effects of cash transfers: experimental evidence from Kenya. <em>Econometrica</em>, 90(6), 2603–2643.", "https://doi.org/10.3982/ECTA17945"),
        ("World Health Organization. LIVE LIFE: limit access to the means of suicide.", "https://www.who.int/initiatives/live-life-initiative-for-suicide-prevention/limit-access-to-means-of-suicide"),
        ("Our World in Data. How pesticide bans can prevent suicides: lessons from Sri Lanka.", "https://ourworldindata.org/pesticide-bans-suicide-prevention"),
        ("Human Dignity Trust. Map of countries that criminalise LGBT people.", "https://www.humandignitytrust.org/lgbt-the-law/map-of-criminalisation/"),
        ("World Animal Protection. Animal Protection Index 2020.", "https://api.worldanimalprotection.org/"),
    ]
    body = f'''            <div class="callout tldr">
                <strong>Key findings</strong>
                <ul>
                    <li>The world suffers less than it did in 2000. The population-weighted GDS score fell from {g[0]:.1f} to {g[-1]:.1f}, and <strong>{w["improved"]} of {w["compared"]} countries</strong> improved.{sup(1)}</li>
                    <li>The number of people living in the highest-suffering countries (a score of 70 or more) fell from {w["pop_high_suffering_bn"]["2000"]:.1f} billion to {w["pop_high_suffering_bn"]["2023"]:.1f} billion, even as the world's population grew by nearly 2 billion.</li>
                    <li>Progress has stalled. The world score fell {g[0] - g[i19]:.1f} points from 2000 to 2019, but only {g[i19] - g[-1]:.1f} from 2019 to 2023, as hunger, war and displacement rose.</li>
                    <li>The poorest countries are being left behind: low-income countries improved by less than 1 point, while upper-middle-income countries improved by 12.</li>
                    <li>Forced displacement has multiplied more than fivefold since 2000, and unfreedom, from prisons to modern slavery to overwork, has not improved at all.</li>
                </ul>
            </div>

            <h2>A generation of progress</h2>
            <p>The Gross Domestic Suffering (GDS) index scores every country from 0 (least suffering) to 100 (most) across six equally weighted pillars: illness, gender and sexual discrimination, violence, unfreedom, deprivation and animal suffering. Fixed goalposts make scores comparable across countries and years.{sup(1)}</p>
            <p>Measured this way, the 21st century has brought a large fall in human suffering. The world score fell from {g[0]:.1f} in 2000 to {g[i10]:.1f} in 2010 and {g[i19]:.1f} in 2019.</p>
{trend}
            <p>Most of the gain came from three changes. Extreme poverty fell from {wi["extreme_poverty"]["2000"]:.0f}% to {wi["extreme_poverty"]["2023"]:.0f}% of people in the countries we score. Infant mortality more than halved, from {wi["infant_mortality"]["2000"]:.0f} to {wi["infant_mortality"]["2023"]:.0f} deaths per 1,000 births. And the chance of dying between 15 and 60 fell by a quarter, from {wi["premature_death"]["2000"]:.0f} to {wi["premature_death"]["2023"]:.0f} per 1,000.</p>
{ind}

            <h2>Which kinds of suffering fell, and which did not</h2>
{pillars}
            <ul>
                <li><strong>Deprivation fell most</strong>, from {w["pillars"]["deprivation"][0]:.0f} to {w["pillars"]["deprivation"][-1]:.0f}, driven by falling poverty and hunger. But hunger has risen since 2019: the UN estimates that 733 million people faced hunger in 2023, about 152 million more than in 2019.{sup(2)}</li>
                <li><strong>Discrimination fell sharply</strong>, from {w["pillars"]["discrimination"][0]:.0f} to {w["pillars"]["discrimination"][-1]:.0f}, as the Gender Inequality Index fell from {wi["gender_inequality"]["2000"]:.2f} to {wi["gender_inequality"]["2023"]:.2f} and more countries protected LGBTI people.</li>
                <li><strong>Illness and violence fell</strong>, but progress has stopped since 2019: illness rose with the COVID-19 pandemic, and the violent death rate climbed from {wi["violence"]["2019"]:.1f} to {wi["violence"]["2023"]:.1f} per 100,000 with new wars in Ukraine, Sudan and Gaza.</li>
                <li><strong>Unfreedom did not improve.</strong> Prisoners and people in modern slavery hold steady at about {wi["captivity"]["2023"]:,.0f} per 100,000. Walk Free estimates that 50 million people lived in modern slavery on any given day in 2021, 10 million more than in 2016.{sup(4)}</li>
                <li><strong>Forced displacement exploded</strong>, from {wi["displacement"]["2000"]:,.0f} to {wi["displacement"]["2023"]:,.0f} people per 100,000. UNHCR counted 117.3 million people forcibly displaced at the end of 2023, one in every 69 people on Earth.{sup(3)}</li>
                <li><strong>Animal suffering is the highest pillar of all</strong>, at {w["pillars"]["animal_suffering"][-1]:.0f}. Of the 50 countries graded by World Animal Protection, 17 received the lowest grade, G, for protecting farm animals.{sup(9)}</li>
            </ul>

            <h2>Where suffering is falling, and where it is not</h2>
            <p>Every region improved, but at very different speeds. East Asia and South Asia cut suffering by more than 10 points. Sub-Saharan Africa improved by less than 2 and now suffers most of any region.</p>
{regions}
            <p>The same split runs by income. Upper-middle-income countries such as China, Kazakhstan and Türkiye improved fastest. Low-income countries barely moved, so the gap between the poorest countries and everyone else has widened.</p>
{income}
            <p>Among countries with more than 20 million people, the largest improvements came in {best}. The large countries that got worse the most were all at war or in deep security crises: {worst}.</p>

            <h2>Policy recommendations</h2>
            <p>Each recommendation addresses a finding above, and each rests on evidence that the policy reduces suffering.</p>
            <ol class="recs">
                <li><strong>Prevent and end wars, and protect the people they uproot.</strong> War drives every large reversal in the index, and displacement is the fastest-growing kind of suffering we measure. Fund diplomacy, peacekeeping and humanitarian response, and give refugees and displaced people the right to work, study and move.{sup(3)}</li>
                <li><strong>Put the poorest countries first.</strong> Low-income countries have gained almost nothing since 2000. Direct aid to them, and give cash where it can reach people: in rural Kenya, cash transfers of about $1,000 raised local economic activity by about 2.5 times the amount given, with minimal inflation.{sup(5)}</li>
                <li><strong>Restart the fight against hunger.</strong> The progress of 2000–2019 has reversed. Protect food supplies in conflicts, fund emergency nutrition and invest in smallholder farming.{sup(2)}</li>
                <li><strong>Prevent suicide by limiting access to lethal means.</strong> The World Health Organization advises national bans on highly hazardous pesticides.{sup(6)} Sri Lanka banned the most lethal pesticides and has cut its suicide rate by almost two-thirds since 2000.{sup(7)} It is also one of the five most improved large countries in the index.</li>
                <li><strong>Decriminalize LGBT people.</strong> 65 jurisdictions still criminalise private, consensual same-sex activity.{sup(8)} Repealing these laws costs nothing and removes a direct source of fear, violence and imprisonment.</li>
                <li><strong>Free the captive.</strong> Enforce laws against forced labour and forced marriage, require companies to remove modern slavery from their supply chains, and cut the use of prison for low-level and drug offences.{sup(4)}</li>
                <li><strong>Protect farm animals.</strong> Adopt and enforce farm-animal welfare laws, beginning with bans on extreme confinement, so that the animals raised for food live without severe suffering.{sup(9)}</li>
                <li><strong>Measure suffering, not just growth.</strong> Governments and international agencies should report suffering alongside GDP, and invest in the death registration, surveys and prison statistics that make it measurable everywhere.</li>
            </ol>

            <h2>About this report</h2>
            <p>This report uses the Gross Domestic Suffering index, 2023 edition, covering {DATA["us"]["n_ranked"][-1]} countries. World and regional figures are population-weighted averages of ranked countries. Equal pillar weights are a judgment; we publish rank ranges under 1,000 random weightings. Read <a href="/methods/">how the index is built</a>, or see <a href="/reports/united-states/">the United States report</a>.</p>
{sources(src)}'''
    report_page(write, "global", "Suffering in the World, 2000–2023",
                "Global Suffering Report, 2000–2023: Findings and Trends | GDS",
                "How much has suffering fallen worldwide since 2000? Findings, trends by region and pillar, and policy recommendations from the Gross Domestic Suffering index, with a PDF.",
                "Global",
                "Since 2000 the world has cut poverty, hunger and early death, and suffering has fallen in four of every five countries. But progress has stalled since 2019, and the poorest countries are being left behind.",
                WORLD_PDF, body)


def hub(write):
    path = "/reports/"
    trail = [("Home", "/"), ("Reports", path)]
    graph = [ORG, {"@type": "CollectionPage", "@id": SITE + path + "#page", "url": SITE + path, "name": "Gross Domestic Suffering reports"},
             breadcrumbs_ld(trail)]
    cards = "".join(f'''
                <article class="report-card">
                    <h2><a href="{href}">{t}</a></h2>
                    <p>{d}</p>
                    <p class="report-card-links"><a href="{href}">Read the report</a> · <a href="{pdf}" download>Download PDF</a></p>
                </article>''' for t, d, href, pdf in [
        ("Suffering in the United States, 2000–2023", "The US has fallen from 43rd to 61st of 188 countries. Addiction deaths have risen fivefold, and adults die young. Findings, trends and eight policy recommendations.", "/reports/united-states/", US_PDF),
        ("Suffering in the World, 2000–2023", "Suffering has fallen in four of every five countries since 2000, but progress has stalled since 2019 and the poorest countries are being left behind.", "/reports/global/", WORLD_PDF),
    ])
    html = f'''        <section class="page-hero">
            <div class="container">
                {breadcrumbs_html(trail)}
                <p class="eyebrow">Reports</p>
                <h1>Reports</h1>
                <p class="page-lead">Findings, trends and policy recommendations from the Gross Domestic Suffering index, each with a downloadable PDF.</p>
            </div>
        </section>
        <div class="prose report-hub">{cards}
        </div>'''
    write("reports/index.html", page("Reports: Suffering in the US and the World | GDS",
          "Findings, trends and policy recommendations from the Gross Domestic Suffering index, for the United States and the world, with downloadable PDFs.",
          path, graph, html, "reports"))


def build(write):
    hub(write)
    us_report(write)
    world_report(write)
