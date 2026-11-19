# Building the Gross Domestic Suffering Index: plan (v2)

*Drafted 2026-11-19. **The indicator set and formula are superseded by [gds-v2-plan.md](gds-v2-plan.md)**; the roadmap, governance and SEO sections still apply. Builds on the 2022 prototype in `gds-model-v1/` and the indicators proposed on grossdomesticsuffering.org.*

## 1. Goal

Publish an open, annually updated index that answers one question per country and year:

> **How much preventable suffering do the people and animals of this country experience?**

It should be credible enough that journalists, researchers and policymakers can cite it, and simple enough to explain in one sentence. Every number should trace back to a public primary source and a script in this repo.

Ship two headline numbers, mirroring GDP and GDP per capita:

| Product | What it is | Why |
|---|---|---|
| **GDS Score** (per capita, 0–100, lower is better) | Average suffering experienced by a person in the country | Fair comparison between countries; this is what the rankings use |
| **Gross Domestic Suffering** (total) | GDS Score × population | Lives up to the name: *where is most of the world's suffering?* India and China matter more here than Iceland |

A third, derived view, **suffering vs. GDP per capita** (scatter plot plus an "efficiency" residual), is the most quotable output. It shows which countries turn wealth into less suffering and which don't.

---

## 2. What we have today

### 2.1 Indicators proposed so far (combined)

| Source of proposal | Indicators |
|---|---|
| Website (11) | Gender Inequality Index, infant mortality, Global Burden of Disease, unemployment, violence (inverse Global Peace Index), suicide, incarceration, depression, alcoholism, drug fatalities, Animal Protection Index |
| Website, "under consideration" (7) | Air pollution (IQAir), Environmental Performance Index, unsafe drinking water, PISA, illiteracy, life expectancy, Fragile States Index |
| 2022 notebook (11) | Fragile States Index, Women Peace & Security Index, poverty rate, infant mortality, unemployment, violent crime, suicide, incarceration, depression, alcoholism, drug use |

### 2.2 What the 2022 prototype actually does

I re-ran `gds-model-v1/Gross Domestic Misery.ipynb` against `data.csv` (186 countries). It reproduces the website's headline: **the United States ranks 58th** (the site said 59th), and Norway, Iceland, the Netherlands, Ireland and Finland come out on top.

The prototype divides each column by a hand-picked constant (÷100, ÷10,000, and so on) and then adds the columns together. Those constants act as **hidden weights**. Here is each indicator's average share of the final score:

| Indicator | Share of score |
|---|---|
| Fragile States Index | **32.4%** |
| Poverty rate | 20.5% |
| Infant mortality | 15.3% |
| Women, Peace & Security Index | 10.6% |
| Suicide rate | 7.0% |
| Violent crime | 5.2% |
| Depression | 3.3% |
| Unemployment | 3.0% |
| Incarceration | **1.2%** |
| Alcoholism | 1.2% |
| Drug use | **0.5%** |

**Implication:** the website explains the US ranking with "healthcare failures, mental health crises, and mass incarceration," but in the model incarceration, drugs and depression together contribute about 5%. The ranking is driven mostly by the Fragile States Index and poverty. The redesigned site now states only the rank and leaves out the causes. v2 needs explicit, defensible weights.

Other issues to fix:

1. **Mean imputation.** Missing values are replaced with the global mean, and poverty alone is missing for 28 countries. A missing country gets an "average" score whatever its region or income.
2. **Arbitrary offsets.** Unemployment uses `x/100 − 0.04`, which goes negative (e.g. Cuba −0.023), so some countries get *credit* that reduces their suffering score.
3. **Mixed years.** Columns cover 2000–2020 averages, 2019 and 2022, so the score isn't a snapshot of any single year and can't show trends.
4. **Secondary sources.** Several figures come from World Population Review, an aggregator. Reviewers will expect the primary source (WHO, UNODC, IHME, and so on).
5. **Composite inside a composite.** The Fragile States Index and the Global Peace Index are themselves indices of *risk and inputs* (military spending, arms exports, factionalized elites, refugees). They double-count other indicators and measure things that aren't suffering.
6. **No uncertainty.** Ranks are reported as exact. Neighbouring countries are usually statistically tied.

---

## 3. Design principles for v2

1. **Measure outcomes, not inputs or policies.** Count suffering that happened (deaths, illness, violence, deprivation, imprisonment), not laws, spending or "risk." This rules out most composite indices as inputs.
2. **Preventable.** Every indicator should be something some countries have clearly reduced, which proves it can be reduced.
3. **One source, one fact.** No indicator should be counted twice through overlapping composites.
4. **Per capita, same year, primary sources, open licenses where possible.**
5. **Coverage ≥ 150 countries** and annual (or at least regular) updates.
6. **Transparent and reproducible.** One command rebuilds the index from raw downloads.
7. **Follow the OECD/JRC *Handbook on Constructing Composite Indicators*.** It is the standard reviewers will judge against, and it gives us a ready-made checklist.

---

## 4. Recommended framework: 7 pillars, about 18 indicators

Each pillar is a kind of suffering. Indicators are listed with recommended sources; ★ marks changes from the current proposal.

### Pillar 1. Premature death & illness
| Indicator | Source | Notes |
|---|---|---|
| Under-5 mortality per 1,000 ★ | UN IGME / World Bank `SH.DYN.MORT` | Replaces infant mortality: same data, covers more child deaths |
| Maternal mortality ratio ★ | WHO / UN MMEIG | Moved here from inside the Gender Inequality Index |
| Age-standardized DALYs per 100k, **excluding** causes counted in other pillars | IHME Global Burden of Disease | Keeps "burden of disease" without double-counting suicide, drugs, violence and so on |

### Pillar 2. Mental suffering & despair
| Indicator | Source | Notes |
|---|---|---|
| Suicide rate (age-standardized) | WHO Global Health Estimates | Primary source instead of World Population Review |
| Depressive and anxiety disorders, prevalence ★ | IHME GBD | Fills the website's missing "depression" source; adds anxiety |
| Alcohol and drug use disorders, deaths and prevalence ★ | IHME GBD | Fills the missing "alcoholism" and "drug fatality" sources from one consistent dataset |

### Pillar 3. Material deprivation ★ (new pillar)
| Indicator | Source | Notes |
|---|---|---|
| Extreme poverty rate (<$3.00/day, 2021 PPP) | World Bank Poverty & Inequality Platform | Was in the notebook but missing from the website |
| Prevalence of undernourishment | FAO | Hunger is suffering in the most literal sense |
| No access to safely managed water and sanitation | WHO/UNICEF JMP | Moves "unsafe drinking water" from "considering" to "in" |
| **Replace** unemployment with labour underutilization (unemployment + time-related underemployment + potential labour force) | ILO | Headline unemployment is low in poor countries with large informal sectors, which makes them look *better* |

### Pillar 4. Violence & insecurity
| Indicator | Source | Notes |
|---|---|---|
| Intentional homicide rate ★ | UNODC | Replaces the inverse Global Peace Index |
| Conflict deaths per 100k ★ | Uppsala Conflict Data Program (UCDP) | Captures war without counting military budgets |
| Forcibly displaced people (refugees + IDPs) by country of origin, per capita ★ | UNHCR / IDMC | Replaces the displacement part of the Fragile States Index |

### Pillar 5. Injustice & unfreedom
| Indicator | Source | Notes |
|---|---|---|
| Incarceration rate per 100k | World Prison Brief (ICPR, Birkbeck) | Primary source; check licensing before redistributing |
| Political Terror Scale (torture, political imprisonment, killings) ★ | politicalterrorscale.org | Outcome measure of state violence, replacing Fragile States Index elements |

### Pillar 6. Gender-based suffering
| Indicator | Source | Notes |
|---|---|---|
| Intimate-partner violence, past 12 months ★ | WHO Violence Against Women estimates | A direct suffering measure, versus the Gender Inequality Index's mix of parliament seats and education |
| Child marriage before 18 ★ | UNICEF | Clear harm, wide coverage |
| *(Optional)* Women, Peace & Security Index | Georgetown GIWPS | Keep as a robustness check rather than a core input; it overlaps with the two above |

### Pillar 7. Animal suffering ★ (rebuilt)
The World Animal Protection API scores **laws** and was last published in 2020, so it doesn't measure how many animals actually suffer. Recommendation:

| Indicator | Source | Notes |
|---|---|---|
| Land animals slaughtered per capita, weighted by species and production system | FAOSTAT (slaughter counts by species) | Broilers, laying hens in cages, pigs in crates and so on, weighted by a welfare score |
| Farmed fish production per capita | FAO FishStat | The largest numbers by far; weight carefully |
| Animal Protection Index | World Animal Protection | Keep as a minor policy modifier or in a sensitivity test |

Report animal suffering as a **separate sub-index** and show the rankings **with and without** it. It will be the most debated pillar, and the human-only index shouldn't be dismissed because of it.

### Dropped or moved to an annex
| Indicator | Decision | Reason |
|---|---|---|
| Fragile States Index | Drop | Risk and governance composite; its outcome parts are covered by pillars 4–5 |
| Global Peace Index | Drop | Includes military spending and arms exports, which are not suffering in the country itself |
| Environmental Performance Index | Drop | Mostly policy and biodiversity; human harm is captured below |
| Air pollution (IQAir) | Replace | Sensor coverage is city-biased. Use PM2.5-attributable deaths from IHME / State of Global Air, already inside Pillar 1 DALYs as a risk factor, so report it in the annex as "share of suffering due to pollution" |
| Life expectancy | Drop | Already captured by DALYs, since years of life lost are part of them |
| PISA, illiteracy | Annex | These measure capability and future risk rather than suffering now. Show them on country pages but not in the score |
| Gallup "suffering" share (life rating ≤4 now and in 5 years) | **Validation, or add later** | It's literally a direct measure of suffering. The data is licensed, so start by using published aggregates to validate the index |

---

## 5. Methodology

1. **Data window.** Use the latest year available for each indicator, but no more than 5 years old. Record the year for each value and carry it into the output.
2. **Coverage rule.** Score a country only if it has ≥ 70% of indicators and ≥ 1 in every pillar. In v1 that is probably 165–175 countries.
3. **Imputation.** Replace mean-fill with, in order: the country's own nearest year, then a regression on region + income group + correlated indicators, then the regional median. Flag every imputed cell and show a coverage badge on each country page.
4. **Transform.** Log-transform heavily skewed rates (homicide, conflict deaths, incarceration, displacement), then winsorize at the 2.5th and 97.5th percentiles so a single outlier like a war year doesn't flatten everyone else.
5. **Normalize with fixed goalposts** (as HDI does). Map each indicator to 0–100, where 0 is a "best achieved" floor (for example, the 5th percentile in a base year) and 100 is a "worst plausible" ceiling. Fixed goalposts let scores be compared across years, so the index can show whether suffering is falling. Min–max on each year's data cannot do that.
6. **Weighting.** Equal weights across the 7 pillars and equal weights within each pillar. This is easy to explain and to defend. Publish an interactive "adjust the weights" tool so critics can test their own.
7. **Aggregation.** Use the arithmetic mean within pillars. Across pillars, publish the arithmetic mean (suffering adds up) as the headline. Also compute the geometric mean as a check, because it penalizes countries that hide one catastrophic pillar behind good averages.
8. **Gross total.** Multiply the score by population to get total Gross Domestic Suffering, and report each country's share of the world total.
9. **Uncertainty.** Run a Monte Carlo of about 1,000 iterations that varies weights (±50%), the imputation method, the normalization choice, and whether animals are included. Publish a **rank range** for every country (for example "US: 52–63, median 58"). This is the most effective defense against "you chose the weights to get that answer."
10. **Statistical checks.** Check correlations within each pillar (indicators should be positively correlated, and if r > 0.9 one is redundant), run PCA to see whether the data supports the 7 pillars, and test sensitivity by dropping one indicator at a time.
11. **Validation.** The index should correlate negatively with Gallup life evaluations and the World Happiness Report, and positively with Gallup's "suffering" share, but not perfectly. Wherever GDS and happiness disagree is a story worth telling. Also sanity-check the 2022 prototype's results against v2.
12. **Optional external audit.** The European Commission's JRC Competence Centre on Composite Indicators audits indices for free on request. It is a strong credibility signal.

### Possible v3: "suffering-years"
Instead of a 0–100 score, convert every indicator into a common unit, **suffering-adjusted life years per 1,000 people**. GBD already does this for disease. Extend it with severity weights for imprisonment, violence, poverty and animal suffering. It is harder and more contestable, but it would make GDS directly additive, and it would be a real contribution to the field.

---

## 6. Technical plan

```
gds/
├── index.html, styles.css, images/      # public site (GitHub Pages)
├── data/
│   ├── raw/            # untouched downloads, one folder per source, with fetch date
│   ├── processed/      # tidy country-year-indicator table (CSV + Parquet)
│   └── output/         # gds_scores_{year}.csv, gds.json for the site
├── pipeline/
│   ├── fetch/          # one script per source (World Bank API, WHO GHO OData, UNODC,
│   │                   #   IHME GBD export, UNHCR API, FAOSTAT API, ILOSTAT, UCDP, PTS…)
│   ├── harmonize.py    # ISO3 codes, years, units, per-capita conversion
│   ├── score.py        # transform → normalize → weight → aggregate
│   ├── uncertainty.py  # Monte Carlo rank ranges
│   └── config.yaml     # indicators, directions, goalposts, weights (single source of truth)
├── tests/              # unit tests + "golden" checks (e.g. Norway in top 10, no NaNs)
└── docs/methodology.md
```

- **Python** (pandas, `wbgapi`, `requests`) with all parameters in `config.yaml`, so a weight change is a one-line diff with a visible history.
- A **GitHub Action** rebuilds the index whenever the config changes and on a quarterly schedule, then commits `data/output/`.
- The **site** reads `gds.json` and adds a world choropleth map, a sortable ranking table, a GDS-vs-GDP scatter plot, a weight sliders tool, and one page per country. Use Observable Plot or D3 with no build step, so it stays on GitHub Pages.
- **Licensing:** IHME GBD is free for non-commercial use with attribution. Check the World Prison Brief and Gallup terms before redistributing raw values; if needed, publish only derived scores. Release our own code under MIT and our data under CC BY 4.0.

---

## 7. Roadmap

| Phase | Weeks | Deliverables |
|---|---|---|
| **0. Framework** | 1–2 | Lock the pillars and indicators (this doc → `docs/methodology.md`); decide the open questions below |
| **1. Data pipeline** | 3–7 | Fetch scripts for every source, a harmonized table, a coverage report by country |
| **2. Scoring** | 8–10 | `score.py`, imputation, goalposts, first v2 rankings, comparison against v1 |
| **3. Robustness** | 11–12 | Monte Carlo rank ranges, correlation/PCA report, validation against happiness data |
| **4. Expert review** | 13–16 | Send to 5–10 reviewers (health economists, welfare economists, an animal-welfare researcher); optional JRC audit; revise |
| **5. Launch** | 17–20 | Rankings page, map, country pages, methodology PDF, downloadable CSV, press release |
| **6. Annual cycle** | ongoing | Re-run each year; add time series back to ~2010 so trends become the story |

---

## 8. Launch & SEO tie-in

Keyword research (OpenSEO, US market, Nov 2026) shows the domain doesn't yet rank even for its own name. It also shows demand that a real index can capture:

| Query | Monthly searches | Difficulty | Page that should target it |
|---|---|---|---|
| genuine progress indicator | 18,100 | 30 | `/alternatives-to-gdp/` guide |
| best countries to live in | 14,800 | 7 | Rankings page ("countries with the least suffering") |
| gender inequality index | 2,900 | 19 | Pillar 6 explainer |
| gross national happiness | 2,400 | 40 | Comparison guide |
| misery index | 2,400 | 37 | "GDS vs. the misery index" explainer |
| quality of life by country | 880 | 29 | Rankings page |
| limitations of gdp | 720 | 0 | `/limitations-of-gdp/` explainer |
| happy planet index | 720 | 0 | Comparison guide |
| social progress index | 480 | 18 | Comparison guide |

Country pages (`/country/united-states/`, …) create about 170 indexable pages with unique data. Each one is a natural answer to "[country] quality of life / suicide rate / incarceration rate" searches, and something journalists can link to. Releasing the dataset with a press release and a methodology paper (an SSRN preprint) is how the site earns the backlinks it currently lacks.

---

## 9. Open decisions for you

1. **Animals in the headline score, or a separate sub-index?** I recommend separate, plus a combined view.
2. **Equal pillar weights, or a deliberate value judgment** (for example, double weight for premature death)? I recommend equal weights plus the weight-sliders tool.
3. **Gallup data:** license it (cost) to add a direct "subjective suffering" pillar, or use it only to validate? I recommend validation only for v2.
4. **Name of the per-capita number:** "GDS Score" vs. "GDS per capita". Pick one and use it everywhere.
5. **Governance:** who signs the methodology (you alone, an advisory board, a university partner)? This matters for press credibility. Until it's settled, the site should avoid claims like "developed by economists and social scientists."
