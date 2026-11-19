# Gross Domestic Suffering Index v2: data, formula and first results

*Updated 2026-11-19. Supersedes the indicator list in `docs/gds-index-plan.md`. Code: `pipeline/`. Outputs: `data/output/`.*

**Goal:** measure suffering itself, with apples-to-apples comparisons **across years for any one country** and **across countries**.

**Framing rule:** every pillar, indicator and label is framed as suffering. Higher always means worse: Illness, not health; Unfreedom, not freedom; Animal suffering, not animal welfare. Any source framed positively is inverted before it enters the index.

The result is **one number per country per year (2000–2023)**, from 0 (least suffering) to 100 (most), covering **185 countries** in 2023. It combines nine indicators in six equally weighted pillars.

---

## 1. Pillars and indicators

| Pillar (weight) | Indicator | What it counts | Source | Transform |
|---|---|---|---|---|
| **Illness** (1/6) | Healthy life years lost to illness and early death | 75 − healthy life expectancy at birth. This includes suicide, depression, alcohol and drug disorders | WHO Global Health Observatory, HALE (`WHOSIS_000002`), 2000–2023 | linear |
| | Infant mortality | Deaths before age 1 per 1,000 live births | World Bank `SP.DYN.IMRT.IN` (UN IGME) | log |
| **Gender inequality** (1/6) | Gender Inequality Index | Women's loss in reproductive health, empowerment and the labour market (0–1) | [UNDP Human Development Report 2025](https://hdr.undp.org/data-center/thematic-composite-indices/gender-inequality-index#/indicies/GII) | linear |
| **Violence** (1/6) | Violent deaths | Homicides + deaths in armed conflict, per 100,000 | UNODC homicide (WHO modelled estimates where missing); UCDP conflict deaths by location | log(1+x) |
| **Unfreedom** (1/6) | Unfree people | Prisoners + people in modern slavery, per 100,000 | ICPR World Prison Brief; Walk Free Global Slavery Index 2023 | log |
| **Deprivation** (1/6) | Undernourishment | % of people without enough food | FAO via World Bank `SN.ITK.DEFC.ZS` | log |
| | Extreme poverty | % living on under $3.00/day (2021 PPP) | World Bank `SI.POV.DDAY` | log(1+x) |
| | Forcibly displaced people | Refugees, asylum seekers and internally displaced people from the country, per 100,000 | UNHCR population statistics, by origin | log(1+x) |
| **Animal suffering** (1/6) | Animals slaughtered, welfare-adjusted | Land animals slaughtered per person × an Animal Protection Index factor | FAO via Our World in Data; World Animal Protection API 2020 | log(1+x) |

**Walk Free → Unfreedom:** the Global Slavery Index estimate is already a count of suffering (people in modern slavery per 1,000), so it goes straight into Unfreedom. Prisoners and enslaved people are added together because both are people held against their will.

**Animal Protection Index → Animal suffering:** the API is framed positively (A = best protection). It is inverted into a multiplier on animals slaughtered per person: A 0.7, B 0.8, C 0.9, **D 1.0** (the median grade, also used for unrated countries), E 1.1, F 1.2, G 1.3. Weaker protection means more suffering per animal killed.

### Choices behind the indicator list

- **Suicide, depression, alcoholism and drug deaths are not added separately.** All four are causes inside *healthy life years lost*, so adding them again would double count.
- **Infant mortality is kept, as you asked.** It overlaps with healthy life years lost (Spearman ρ = 0.91), so the two are **averaged inside the Illness pillar** and count once together.
- **Unemployment is dropped.** Its harm shows up through illness, deprivation and violence, all of which are measured directly.
- **Violence is homicide plus war deaths, not the inverted Global Peace Index.** The Global Peace Index mixes in military spending, weapons exports, nuclear capability and perceptions, and it already includes incarceration, which would double count Unfreedom. It also has no downloadable time series. Homicide appears only once in v2.
- **Deprivation was added** because famine and destitution were invisible to the first version. South Sudan was ranking better than Jamaica.
- **Burden of disease uses WHO HALE.** IHME's GBD DALYs can't be redistributed: Our World in Data blocks the download, and WHO's API carries all-cause DALYs only for 2000 and 2012. *Healthy life years lost* is the per-person counterpart to DALYs, combining years lost to early death and years lived with illness. With a free IHME account, the DALY export can replace it (put it in `data/raw/ihme/`).

---

## 2. The formula

For country *c*, year *t* and indicator *k* (all oriented so that higher = more suffering):

1. **Fill gaps within each country.** Interpolate linearly between observed years, and hold a value flat for up to 5 years beyond the first or last observation (10 years for homicide, prison and poverty data, which are published irregularly). Every filled cell is flagged; the median country-year has 22% of its indicator values filled.

2. **Rescale to 0–100 with fixed goalposts:**

   *s<sub>kct</sub>* = 100 × clip( ( f<sub>k</sub>(*x<sub>kct</sub>*) − L<sub>k</sub> ) / ( U<sub>k</sub> − L<sub>k</sub> ), 0, 1 )

   f<sub>k</sub> is a log for skewed rates. L<sub>k</sub> and U<sub>k</sub> are the 2.5th and 97.5th percentiles of all observed country-years from 2000 to 2023, saved in `data/output/goalposts.csv`. **The goalposts never move between releases**, so a score changes only when that country's own data changes. This is what makes comparisons across years apples-to-apples.

3. **Pillar score** = the mean of the pillar's indicator scores.

4. **GDS score** = the mean of the available pillar scores, each weighted 1/6:

   **GDS<sub>ct</sub>** = Σ<sub>p</sub> w<sub>p</sub> · P<sub>pct</sub> / Σ<sub>p available</sub> w<sub>p</sub>

   A country is scored only if it has the Illness pillar and at least 5 of the 6 pillars.

5. **Ranks.**
   - `rank`: rank among all countries scored that year (174 in 2000, 185 in 2023).
   - `rank_constant_set`: rank among the **174 countries scored in every year from 2000 to 2023**. Use this one to compare a country's rank across years.
   - `rank_p5`–`rank_p95` (2023): the rank range across 1,000 random weightings (Dirichlet, α = 4), showing how much the rank depends on the weights.
   - `gds_humans_only`, `rank_humans_only`: the same index without the Animal suffering pillar, as a transparency check. The headline score always includes animals.

### How the pillars relate (Spearman ρ across countries, 2023)

- Illness, gender inequality and deprivation move together (ρ ≈ 0.8–0.9). Poor countries suffer on all three, but each measures a different harm.
- Unfreedom is nearly independent of the others (ρ ≈ 0–0.2, apart from displacement at 0.36), so it adds information the other pillars miss.
- **Animal suffering runs opposite to human suffering (ρ ≈ −0.5):** richer countries kill more animals per person. That is why rich meat producers such as the US, Brazil and the Netherlands score worse than human-only measures would suggest.

---

## 3. First results (2023)

\* *Rank range* = 5th–95th percentile across 1,000 random weightings. *Humans-only rank* is shown for transparency only.

**Least suffering**

| Rank | Country | GDS | Rank range* | Humans-only rank | Illness | Gender inequality | Violence | Unfreedom | Deprivation | Animal suffering |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Japan | 11.5 | 1–2 | 1 | 0 | 2 | 0 | 4 | 7 | 56 |
| 2 | Switzerland | 12.4 | 1–3 | 3 | 6 | 0 | 7 | 0 | 2 | 59 |
| 3 | Germany | 14.5 | 3–7 | 7 | 8 | 2 | 12 | 0 | 7 | 57 |
| 4 | Norway | 14.6 | 3–8 | 2 | 1 | 0 | 9 | 0 | 3 | 74 |
| 5 | Sweden | 14.7 | 4–7 | 6 | 0 | 0 | 15 | 5 | 8 | 59 |
| 6 | Luxembourg | 15.2 | 1–18 | 25 | 0 | 0 | 20 | 68 | 3 | 0 |
| 7 | Denmark | 16.7 | 5–14 | 4 | 7 | 0 | 11 | 0 | 3 | 79 |
| 8 | Finland | 18.5 | 8–15 | 8 | 3 | 0 | 13 | 16 | 4 | 76 |
| 9 | Netherlands | 18.9 | 7–22 | 5 | 10 | 0 | 9 | 0 | 4 | 91 |
| 10 | Singapore | 18.9 | 4–13 | 13 | 0 | 0 | 0 | 43 | 18 | 52 |

**Most suffering**

| Rank | Country | GDS | Rank range* | Humans-only rank | Illness | Gender inequality | Violence | Unfreedom | Deprivation | Animal suffering |
|---|---|---|---|---|---|---|---|---|---|---|
| 176 | Honduras | 68.5 | 157–182 | 164 | 41 | 60 | 90 | 76 | 74 | 70 |
| 177 | Guatemala | 68.6 | 162–181 | 159 | 48 | 67 | 81 | 77 | 64 | 75 |
| 178 | Yemen | 69.1 | 155–184 | 177 | 62 | 100 | 54 | 61 | 91 | 46 |
| 179 | Burkina Faso | 70.0 | 157–183 | 174 | 70 | 79 | 93 | 45 | 81 | 52 |
| 180 | Central African Republic | 70.7 | 142–184 | 183 | 94 | – | 83 | 59 | 97 | 21 |
| 181 | Nigeria | 70.7 | 156–183 | 181 | 78 | 97 | 74 | 73 | 81 | 21 |
| 182 | Somalia | 72.6 | 148–185 | 185 | 88 | 97 | 85 | 63 | 100 | 2 |
| 183 | Haiti | 72.7 | 155–185 | 184 | 69 | 88 | 98 | 77 | 96 | 9 |
| 184 | Ukraine | 72.8 | 155–185 | 165 | 34 | – | 100 | 94 | 49 | 87 |
| 185 | South Sudan | 73.8 | 168–185 | 182 | 81 | – | 75 | 84 | 92 | 37 |

**Selected countries**

| Rank | Country | GDS | Rank range* | Humans-only rank | Illness | Gender inequality | Violence | Unfreedom | Deprivation | Animal suffering |
|---|---|---|---|---|---|---|---|---|---|---|
| 17 | United Kingdom | 24.8 | 16–28 | 19 | 13 | 6 | 15 | 35 | 5 | 75 |
| 28 | China | 28.6 | 25–34 | 27 | 15 | 14 | 6 | 55 | 11 | 72 |
| 82 | **United States** | 45.3 | 58–132 | 55 | 24 | 19 | 46 | 75 | 9 | 98 |
| 83 | India | 45.7 | 60–94 | 98 | 52 | 55 | 31 | 74 | 38 | 25 |
| 98 | Russia | 49.7 | 72–147 | 77 | 25 | 19 | 53 | 99 | 18 | 83 |
| 149 | Brazil | 61.5 | 114–176 | 114 | 37 | 53 | 77 | 77 | 26 | 99 |
| 167 | Belize | 65.7 | 129–183 | 125 | 39 | 59 | 86 | 78 | 32 | 100 |
| 172 | Jamaica | 67.5 | 136–184 | 137 | 43 | 48 | 100 | 75 | 42 | 98 |

Adding the Deprivation pillar moved South Sudan, Somalia, Haiti, Central African Republic and Nigeria to the bottom. Jamaica and Belize remain low because of very high murder rates, mass incarceration and high animal slaughter per person.

**The United States** has these 2023 values:
- 10.4 healthy years lost
- infant mortality of 5.5 per 1,000
- Gender Inequality Index of 0.169
- 5.8 violent deaths per 100,000
- **872 unfree people per 100,000** (542 prisoners + 330 people in modern slavery)
- 2.5% undernourished, 1.2% in extreme poverty
- 29 land animals slaughtered per person (API grade D)

**Trends**
- The population-weighted world score fell from **52.6 in 2000 to 45.4 in 2023**, and 83% of countries suffered less in 2023 than in 2000.
- The US fell from 49.2 to 45.3. But among the constant set of 174 countries, its rank slipped from 63rd to 76th, because others reduced suffering faster.
- Suffering rose most in Dominica, Ukraine, Yemen, Syria, St. Kitts and Nevis, and Haiti.

---

## 4. Apples-to-apples: what holds and what doesn't

| Comparison | Holds? | Why |
|---|---|---|
| One country's score, year to year | **Yes**, for indicators that are updated annually | Fixed goalposts; same sources and methods every year |
| Countries in the same year | **Yes** | Same indicators, transforms and weights for every country |
| Ranks across years | Use `rank_constant_set` | The number of countries scored grows from 174 to 185 |
| Modern slavery over time | **No**, it's a constant | One Walk Free estimate (2023 report) applied to every year. The 2016 and 2018 editions used different methods |
| Animal Protection Index over time | **No**, it's a constant | The 2020 grades apply to every year. The 2014 grades could be used for earlier years |
| Stale data | Partly | Some prison, homicide and poverty figures are carried flat for up to 10 years, so a country's trend can lag reality. `share_imputed` shows how much |

---

## 5. Open decisions

1. **Weight of Animal suffering.** It now counts 1/6, like every other pillar. It always stays in; the question is only whether 1/6 is right.
2. **IHME DALYs instead of WHO healthy life years?** This needs your free IHME account.
3. **Slavery trend:** model a back-cast from Walk Free's risk factors, or keep the estimate constant and say so on the website (recommended for now).
4. **Animal counting:** weight species by days lived in farming (a broiler chicken lives about 6 weeks; a dairy cow, years) and add farmed fish. This is the biggest remaining improvement to Animal suffering.

## 6. Next steps

- Validate against Gallup's "suffering" share and run leave-one-pillar-out tests.
- Website: add a rankings table, a world map, a trend chart per country, and country pages, all built from `data/output/gds_v2_country_year.csv`.

## 7. Reproduce

```sh
bash pipeline/fetch.sh             # downloads raw data into data/raw/ (the Global Slavery Index PDF is about 36 MB)
python3 -I pipeline/extract.py     # Global Slavery Index PDF table and API grades → data/interim/
python3 -I pipeline/build_index.py # → data/output/
```

| Output | Contents |
|---|---|
| `gds_v2_country_year.csv` | Every country-year: score, ranks, rank range (2023), humans-only check, pillar and indicator scores, raw values, imputation share |
| `gds_v2_2023.csv` | 2023 ranking |
| `gds_v2_world_trend.csv` | Population-weighted world score and median by year |
| `goalposts.csv` | Fixed scaling goalposts (keep these fixed across releases) |

Sources: [WHO GHO](https://www.who.int/data/gho) · [World Bank](https://data.worldbank.org/indicator/SP.DYN.IMRT.IN) · [UNDP Gender Inequality Index](https://hdr.undp.org/data-center/thematic-composite-indices/gender-inequality-index#/indicies/GII) · [UNODC](https://dataunodc.un.org/) · [UCDP](https://ucdp.uu.se/) · [World Prison Brief](https://www.prisonstudies.org/) · [Walk Free Global Slavery Index](https://www.walkfree.org/global-slavery-index/downloads/) · [FAO](https://www.fao.org/faostat/) · [UNHCR](https://www.unhcr.org/refugee-statistics/) · [Animal Protection Index](https://api.worldanimalprotection.org/rankings)
