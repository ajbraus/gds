"""Build the Gross Domestic Suffering (GDS) v2 index: one score per country per year.

Usage (repo root):
    bash pipeline/fetch.sh            # download raw data
    python3 -I pipeline/extract.py    # PDF/HTML tables -> data/interim/
    python3 -I pipeline/build_index.py

Method (see docs/gds-v2-plan.md):
  1. Assemble eleven indicators per country-year, 2000-2023. Every indicator is
     framed as suffering (higher = worse) and measures suffering within a life, not
     how long the life is.
  2. Fill gaps within each country: linear interpolation between observed years,
     held flat up to MAX_EXTEND years beyond the first/last observation.
  3. Transform (log for skewed rates) and rescale to 0-100 with FIXED goalposts
     (2.5th / 97.5th percentile of all observed country-years), so a country's
     score changes only when its own data changes.
  4. Average into six equally weighted pillars: Illness, Gender inequality, Violence,
     Unfreedom, Deprivation and Animal suffering. Violence counts every violent death
     equally: homicide, war and suicide (self-directed violence, as the WHO classifies it).
     Only large, reliable, global datasets are used (see /methods/).
  5. GDS = weighted mean of pillars (0 = least suffering, 100 = most).
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from countries import universe  # noqa: E402

RAW, INTERIM, OUT = "data/raw", "data/interim", "data/output"
YEARS = list(range(2000, 2024))
MAX_EXTEND = 5          # years a value may be carried beyond its last observation
# Homicide and prison counts are published irregularly, so they may be carried further.
MAX_EXTEND_BY = {"homicide": 10, "prison": 10, "poverty": 10, "overwork": 10}  # irregular surveys
GOALPOST_PCT = (2.5, 97.5)
MIN_PILLARS = 5

NORDIC = ["NOR", "SWE", "DNK", "FIN"]
SLAVERY_PEERS = {
    "ISL": NORDIC, "FRO": NORDIC, "GRL": NORDIC,
    "LUX": ["BEL", "NLD", "DEU", "FRA"], "LIE": ["CHE", "AUT"], "MCO": ["FRA", "ITA"],
    "AND": ["ESP", "FRA"], "SMR": ["ITA"], "MLT": ["ITA", "CYP"], "GIB": ["GBR", "ESP"],
    "CHI": ["GBR", "IRL"], "IMN": ["GBR", "IRL"],
}

# Animal suffering measures treatment, not numbers: the Animal Protection Index farm-animal
# grade (50 countries, 88% of land animals eaten), A = 0 to G = 100. Unrated countries get the
# median grade of rated countries in their World Bank region.
API_SCORE = {g: round(100 * i / 6, 1) for i, g in enumerate("ABCDEFG")}
FIXED_GOALPOSTS = {"animal_suffering": (0, 100)}  # the grade scale is already 0-100
# Within Discrimination, weight by people affected: women are about half of people,
# LGBTQ+ adults about 9% (Ipsos LGBT+ Pride 2023, 26 countries), so 50:9, roughly 85:15
INDICATOR_WEIGHTS = {"gender_inequality": 0.85, "lgbti_laws": 0.15}
MIN_POP = 0  # every scored country is ranked, whatever its size

INDICATORS = {
    # key: (label, unit, transform)
    "premature_death":   ("Premature adult death", "probability of dying between 15 and 60, per 1,000 (WHO)", "log"),
    "ill_health_share":  ("Share of life lived in ill health", "% of life expectancy, (LE - HALE) / LE (WHO)", "linear"),
    "infant_mortality":  ("Infant mortality", "deaths per 1,000 live births", "log"),
    "substance_deaths":  ("Alcohol and drug deaths", "deaths from alcohol and drug use disorders per 100k (WHO GHE)", "log"),
    "gender_inequality": ("Gender Inequality Index", "0-1 (UNDP)", "linear"),
    "lgbti_laws":        ("Anti-LGBTI laws", "LGBTI Composite Policy Index, sign reversed (Velasco, via OWID)", "linear"),
    "violence":          ("Violent deaths", "homicide (UNODC, WHO fallback) + conflict deaths (UCDP) + suicide (WHO) per 100k", "log1p"),
    "captivity":         ("People held captive", "prisoners + people in modern slavery per 100k", "log"),
    "overwork":          ("Overwork", "% of employed working 49+ hours a week (ILO)", "log"),
    "undernourishment":  ("Undernourishment", "% of population (FAO)", "log"),
    "extreme_poverty":   ("Extreme poverty", "% below $3.00/day, 2021 PPP (World Bank)", "log1p"),
    "displacement":      ("Forcibly displaced people", "refugees, asylum seekers and IDPs by origin per 100k (UNHCR)", "log1p"),
    "animal_suffering":  ("Farm-animal mistreatment", "Animal Protection Index 2020 farm-animal grade, A = 0 to G = 100", "linear"),
}
PILLARS = {
    "illness":           ["premature_death", "infant_mortality", "ill_health_share", "substance_deaths"],
    "discrimination":    ["gender_inequality", "lgbti_laws"],
    "violence":          ["violence"],
    "unfreedom":         ["captivity", "overwork"],
    "deprivation":       ["undernourishment", "extreme_poverty", "displacement"],
    "animal_suffering":  ["animal_suffering"],
}
WEIGHTS = {p: 1 / len(PILLARS) for p in PILLARS}


# ----------------------------------------------------------------------------- loaders
def owid(slug):
    d = pd.read_csv(f"{RAW}/owid/{slug}.csv")
    d = d[d.code.notna() & (d.code.str.len() == 3)]
    return d.rename(columns={"code": "iso3"})


def worldbank(indicator):
    _, rows = json.load(open(f"{RAW}/worldbank/{indicator}.json"))
    d = pd.DataFrame([(r["countryiso3code"], int(r["date"]), r["value"]) for r in rows],
                     columns=["iso3", "year", "value"]).dropna()
    return d[d.iso3.str.len() == 3]


def series(df, value_col):
    return df[["iso3", "year", value_col]].rename(columns={value_col: "value"}).dropna()


def who(code):
    d = pd.DataFrame(json.load(open(f"{RAW}/who/{code}.json"))["value"])
    d = d[(d.SpatialDimType == "COUNTRY") & (d.Dim1 == "SEX_BTSX")].copy()
    # Some series (suicide, 2021) add rows for single age groups; keep the all-ages figure
    if "Dim2" in d:
        d = d[d.Dim2.isna() | (d.Dim2 == "AGEGROUP_YEARSALL")]
    # A few WHO series publish the number only as text in "Value"
    d["NumericValue"] = d.NumericValue.fillna(pd.to_numeric(d.Value, errors="coerce"))
    return d.rename(columns={"SpatialDim": "iso3", "TimeDim": "year", "NumericValue": "value"})[["iso3", "year", "value"]]


def load_raw():
    out = {}
    out["hale"] = who("WHOSIS_000002")
    out["life_expectancy"] = who("WHOSIS_000001")
    out["adult_mortality"] = who("WHOSIS_000004")
    out["suicide"] = who("SDGSUICIDE")
    subs = owid("death-rates-substance-disorders-who")
    out["substance_deaths"] = series(subs, [c for c in subs.columns if c.startswith("death_rate")][0])

    ilo = pd.read_csv(f"{RAW}/ilo/EMP_TEMP_SEX_HOW_NB_A.csv.gz")
    ilo = ilo[ilo.sex == "SEX_T"].pivot_table(index=["ref_area", "time"], columns="classif1", values="obs_value", aggfunc="first")
    ilo = (100 * ilo["HOW_BANDS_HGE49"] / ilo["HOW_BANDS_TOTAL"]).rename("value").reset_index()
    ilo = ilo.rename(columns={"ref_area": "iso3", "time": "year"}).dropna()
    # Japan is missing from ILO's hours breakdown; use its own Labour Force Survey (via JILPT)
    sup = pd.read_csv(f"{INTERIM}/overwork_supplement.csv").rename(columns={"overwork_pct": "value"})
    out["overwork"] = pd.concat([ilo[~ilo.iso3.isin(sup.iso3)], sup[["iso3", "year", "value"]]])
    who_hom = pd.DataFrame(json.load(open(f"{RAW}/who/VIOLENCE_HOMICIDERATE.json"))["value"])
    who_hom = who_hom[(who_hom.SpatialDimType == "COUNTRY") & (who_hom.Dim1 == "SEX_BTSX")]
    out["homicide_who"] = who_hom.rename(columns={"SpatialDim": "iso3", "TimeDim": "year", "NumericValue": "value"})[["iso3", "year", "value"]]
    out["imr"] = worldbank("SP.DYN.IMRT.IN")
    out["pop"] = worldbank("SP.POP.TOTL")
    out["undernourishment"] = worldbank("SN.ITK.DEFC.ZS")
    out["poverty"] = worldbank("SI.POV.DDAY")
    unhcr = pd.DataFrame(json.load(open(f"{RAW}/unhcr/population_by_origin.json"))["items"])
    kinds = ["refugees", "asylum_seekers", "idps", "oip"]
    unhcr[kinds] = unhcr[kinds].apply(pd.to_numeric, errors="coerce").fillna(0)
    unhcr["value"] = unhcr[kinds].sum(axis=1)
    out["displaced"] = unhcr.rename(columns={"coo_iso": "iso3"})[["iso3", "year", "value"]]

    undp = pd.read_csv(f"{RAW}/undp/HDR25_Composite_indices_complete_time_series.csv", encoding="latin-1")
    gii = undp[["iso3"] + [c for c in undp.columns if c.startswith("gii_") and c[4:].isdigit()]]
    gii = gii.melt(id_vars="iso3", var_name="year", value_name="value").dropna()
    gii["year"] = gii.year.str[4:].astype(int)
    out["gii"] = gii[gii.iso3.str.len() == 3]
    lgbti = series(owid("lgbt-rights-index"), "composite_index")
    out["lgbti"] = lgbti.assign(value=-lgbti.value)  # higher = more discriminatory law

    hom = owid("homicide-rate-unodc")
    out["homicide"] = series(hom, [c for c in hom.columns if c.startswith("value__")][0])
    con = owid("death-rate-in-armed-conflicts")
    out["conflict"] = series(con, con.columns[3])
    out["prison"] = series(owid("prison-population-rate"), "prison_population_rate")

    ani = owid("animals-slaughtered-for-meat")
    cols = [c for c in ani.columns if c.startswith("meat")]
    chicken = [c for c in cols if c.startswith("meat__chicken")][0]
    # Chickens are ~90% of land animals slaughtered; a row without them is not usable.
    ani["value"] = ani[cols].sum(axis=1).where(ani[chicken].notna())
    out["slaughtered"] = ani[["iso3", "year", "value"]].dropna()

    # Animals eaten: kg of each meat type available per person / world average kg per animal
    # of that type (FAO production / FAO heads slaughtered), so importers count the animals
    # they eat and exporters are not charged for animals eaten abroad.
    prod = pd.read_csv(f"{RAW}/owid/global-meat-production-by-livestock-type.csv")
    prod = prod[prod.entity == "World"].set_index("year")
    heads = ani_world = pd.read_csv(f"{RAW}/owid/animals-slaughtered-for-meat.csv")
    ani_world = ani_world[ani_world.entity == "World"].set_index("year")
    pick = lambda df, *names: df[[c for c in df.columns if any(c.startswith(f"meat__{n}") or c.startswith(f"meat_of_{n}") for n in names)]].sum(axis=1)
    kg_per_animal = pd.DataFrame({
        "poultry": pick(prod, "poultry") * 1000 / pick(ani_world, "chicken", "turkey", "duck"),
        "pig": pick(prod, "pig") * 1000 / pick(ani_world, "pig"),
        "beef_and_buffalo": pick(prod, "beef_and_buffalo") * 1000 / pick(ani_world, "cattle"),
        "sheep_and_goat": pick(prod, "sheep_and_goat") * 1000 / pick(ani_world, "goat", "lamb"),
    }).dropna()
    sup = owid("per-capita-meat-type")
    eaten = 0
    for t in kg_per_animal.columns:
        col = [c for c in sup.columns if c.startswith(f"meat__{t}__")][0]
        eaten = eaten + sup[col].fillna(0) / sup.year.map(kg_per_animal[t])
    poultry_col = [c for c in sup.columns if c.startswith("meat__poultry__")][0]
    sup["value"] = eaten.where(sup[poultry_col].notna())
    out["eaten_per_person"] = sup[["iso3", "year", "value"]].dropna()

    out["slavery"] = pd.read_csv(f"{INTERIM}/gsi2023_slavery.csv")
    out["api"] = pd.read_csv(f"{INTERIM}/api2020_farm_grades.csv").rename(columns={"farm_grade": "api_grade"})
    return out


# ----------------------------------------------------------------------------- gap filling
def fill(df, isos, extend=MAX_EXTEND):
    """Country x year panel with interpolation and limited flat extension. Returns (values, imputed_mask)."""
    wide = df.pivot_table(index="iso3", columns="year", values="value", aggfunc="mean")
    wide = wide.reindex(index=isos, columns=sorted(set(wide.columns) | set(YEARS)))
    observed = wide.notna()
    filled = wide.interpolate(axis=1, limit_area="inside")
    filled = filled.ffill(axis=1, limit=extend).bfill(axis=1, limit=extend)
    return filled[YEARS], ~observed.reindex(columns=filled.columns)[YEARS] & filled[YEARS].notna()


def panel(raw):
    countries = universe()
    isos = sorted(countries)
    vals, imp = {}, {}

    hale, hale_imp = fill(raw["hale"], isos)
    le, le_imp = fill(raw["life_expectancy"], isos)
    vals["ill_health_share"] = (100 * (le - hale) / le).clip(lower=0)
    imp["ill_health_share"] = hale_imp | le_imp
    vals["substance_deaths"], imp["substance_deaths"] = fill(raw["substance_deaths"], isos)
    vals["overwork"], imp["overwork"] = fill(raw["overwork"], isos, MAX_EXTEND_BY["overwork"])
    vals["infant_mortality"], imp["infant_mortality"] = fill(raw["imr"], isos)
    vals["premature_death"], imp["premature_death"] = fill(raw["adult_mortality"], isos)
    vals["gender_inequality"], imp["gender_inequality"] = fill(raw["gii"], isos)
    vals["lgbti_laws"], imp["lgbti_laws"] = fill(raw["lgbti"], isos)

    hom, hom_imp = fill(raw["homicide"], isos, MAX_EXTEND_BY["homicide"])
    # Fall back to WHO's modelled homicide estimates where UNODC has no usable figure
    who_hom, _ = fill(raw["homicide_who"], isos)
    hom_imp = hom_imp | (hom.isna() & who_hom.notna())
    hom = hom.fillna(who_hom)
    con, con_imp = fill(raw["conflict"], isos)
    con = con.fillna(0)  # UCDP records every conflict; no entry means no recorded conflict deaths
    sui, sui_imp = fill(raw["suicide"], isos)
    # WHO publishes no suicide rate for some very small states: use the median of the same
    # World Bank region and income group, flagged as imputed
    wb = {r["id"]: (r["region"]["value"], r["incomeLevel"]["value"]) for r in json.load(open(f"{RAW}/worldbank/countries.json"))[1]}
    peer = pd.Series({i: " / ".join(wb.get(i, ("?", "?"))) for i in isos})
    sui_imp = sui_imp | sui.isna()
    sui = sui.fillna(sui.groupby(peer).transform("median"))
    vals["violence"] = hom + con + sui
    imp["violence"] = hom_imp | sui_imp

    prison, prison_imp = fill(raw["prison"], isos, MAX_EXTEND_BY["prison"])
    sl = raw["slavery"].set_index("iso3").slavery_per_1000.reindex(isos)
    # Countries Walk Free does not estimate (mostly small states) get the median of
    # countries in the same region AND income group, e.g. Iceland ~ high-income Europe,
    # not a Europe & Central Asia median that includes Russia and Turkmenistan.
    wb = {r["id"]: (r["region"]["value"], r["incomeLevel"]["value"]) for r in json.load(open(f"{RAW}/worldbank/countries.json"))[1]}
    peer = pd.Series({i: " / ".join(wb.get(i, ("?", "?"))) for i in isos})
    region = pd.Series({i: wb.get(i, ("?", "?"))[0] for i in isos})
    # Small Western European states: closest neighbours, since high-income Europe also spans
    # Eastern Europe and Russia, where Walk Free's estimates run 3-13 per 1,000.
    for iso, peers in SLAVERY_PEERS.items():
        if iso in sl.index and pd.isna(sl[iso]):
            sl[iso] = sl.reindex(peers).median()
    sl_filled = sl.fillna(sl.groupby(peer).transform("median")).fillna(sl.groupby(region).transform("median"))
    slavery_100k = pd.DataFrame(np.repeat(sl_filled.values[:, None] * 100, len(YEARS), axis=1), index=isos, columns=YEARS)
    vals["captivity"] = prison + slavery_100k
    imp["captivity"] = prison_imp | pd.DataFrame(np.repeat(sl.isna().values[:, None], len(YEARS), axis=1), index=isos, columns=YEARS)

    pop, _ = fill(raw["pop"], isos)
    vals["undernourishment"], imp["undernourishment"] = fill(raw["undernourishment"], isos)
    vals["extreme_poverty"], imp["extreme_poverty"] = fill(raw["poverty"], isos, MAX_EXTEND_BY["poverty"])
    displaced, imp["displacement"] = fill(raw["displaced"], isos)
    # UNHCR lists origins with displaced people; a country it never lists has none recorded
    listed = raw["displaced"].iso3.unique()
    displaced.loc[~displaced.index.isin(listed)] = 0
    vals["displacement"] = displaced / pop * 1e5
    order = "ABCDEFG"
    grade = raw["api"].set_index("iso3").api_grade.reindex(isos)
    rank = grade.map({g: i for i, g in enumerate(order)})
    filled = rank.fillna(rank.groupby(region).transform("median").round()).fillna(rank.median())
    a = filled.map(lambda i: API_SCORE[order[int(i)]])
    vals["animal_suffering"] = pd.DataFrame({y: a for y in YEARS})
    imp["animal_suffering"] = pd.DataFrame({y: grade.isna() for y in YEARS})

    long = []
    for k in INDICATORS:
        v = vals[k].stack(dropna=False).rename(k)
        i = imp[k].reindex_like(vals[k]).fillna(False).stack(dropna=False).rename(k + "_imputed")
        long += [v, i]
    df = pd.concat(long, axis=1).reset_index().rename(columns={"level_0": "iso3", "level_1": "year"})
    df.insert(1, "country", df.iso3.map(countries))
    df["population"] = pop.stack(dropna=False).reindex(pd.MultiIndex.from_frame(df[["iso3", "year"]])).values
    df["slavery_per_1000_gsi2023"] = df.iso3.map(sl)
    df["api_farm_grade_2020"] = df.iso3.map(raw["api"].set_index("iso3").api_grade)
    return df


# ----------------------------------------------------------------------------- scoring
def transform(x, kind):
    if kind == "log":
        return np.log(x.clip(lower=1e-6))
    if kind == "log1p":
        return np.log1p(x.clip(lower=0))
    return x


def score(df, weights=WEIGHTS, goalposts=None):
    df = df.copy()
    if goalposts is None:
        goalposts = {}
        for k, (_, _, kind) in INDICATORS.items():
            t = transform(df.loc[~df[k + "_imputed"].astype(bool), k].dropna(), kind)
            goalposts[k] = FIXED_GOALPOSTS.get(k) or tuple(np.percentile(t, GOALPOST_PCT))
    for k, (_, _, kind) in INDICATORS.items():
        lo, hi = goalposts[k]
        df[k + "_score"] = (100 * (transform(df[k], kind) - lo) / (hi - lo)).clip(0, 100)
    for p, ks in PILLARS.items():
        S = df[[k + "_score" for k in ks]]
        w = pd.Series([INDICATOR_WEIGHTS.get(k, 1) for k in ks], index=S.columns)
        df["pillar_" + p] = (S.fillna(0) * w).sum(axis=1) / (S.notna() * w).sum(axis=1)
    # The LGBTI index carries 15% of the pillar, too little to stand in for missing gender data
    df.loc[df.gender_inequality_score.isna(), "pillar_discrimination"] = np.nan
    P = df[["pillar_" + p for p in PILLARS]]
    W = pd.Series({"pillar_" + p: w for p, w in weights.items()})
    avail = P.notna()
    df["n_pillars"] = avail.sum(axis=1)
    df["gds"] = (P.fillna(0) * W).sum(axis=1) / (avail * W).sum(axis=1)
    # Illness and Animal suffering are required: no country gets a pass on either
    ok = (df.n_pillars >= MIN_PILLARS) & df.pillar_illness.notna() & df.pillar_animal_suffering.notna()
    df.loc[~ok, "gds"] = np.nan
    big = df.gds.where(df.population >= MIN_POP)
    df["rank"] = big.groupby(df.year).rank(method="min")
    df["n_ranked"] = big.groupby(df.year).transform("count")
    imp_cols = [k + "_imputed" for k in INDICATORS]
    df["share_imputed"] = df[imp_cols].astype(float).mean(axis=1).round(2)
    return df, goalposts


def rank_ranges(df, year, n=1000, seed=7):
    """Rank uncertainty from random pillar weights (Dirichlet, alpha=4 → mostly within ±10 points of 20%)."""
    rng = np.random.default_rng(seed)
    d = df[df.year == year].set_index("iso3")
    P = d[["pillar_" + p for p in PILLARS]]
    ok = d["rank"].notna()
    ranks = []
    for w in rng.dirichlet([4] * len(PILLARS), n):
        avail = P[ok].notna()
        g = (P[ok].fillna(0) * w).sum(axis=1) / (avail * w).sum(axis=1)
        ranks.append(g.rank(method="min"))
    R = pd.concat(ranks, axis=1)
    return pd.DataFrame({"rank_p5": R.quantile(0.05, axis=1), "rank_p95": R.quantile(0.95, axis=1)}).astype(int)


def main():
    os.makedirs(OUT, exist_ok=True)
    raw = load_raw()
    df = panel(raw)
    scored, goalposts = score(df)

    # Sensitivity variant: humans only (no animal pillar)
    human_w = {p: (0 if p == "animal_suffering" else 1 / (len(PILLARS) - 1)) for p in PILLARS}
    human, _ = score(df, human_w, goalposts)
    scored["gds_humans_only"] = human.gds
    scored["rank_humans_only"] = human["rank"]

    # Ranks comparable over time: rank only among countries scored in every year
    always = scored.groupby("iso3")["rank"].apply(lambda g: g.notna().all())
    panel_set = always[always].index
    in_panel = scored.iso3.isin(panel_set)
    scored.loc[in_panel, "rank_constant_set"] = scored[in_panel].groupby("year").gds.rank(method="min")
    print(f"Constant comparison set: {len(panel_set)} countries scored every year {YEARS[0]}-{YEARS[-1]}")

    latest = max(YEARS)
    rr = rank_ranges(scored, latest)
    scored = scored.merge(rr.reset_index().assign(year=latest), on=["iso3", "year"], how="left")

    cols = (["iso3", "country", "year", "gds", "rank", "n_ranked", "rank_constant_set", "rank_p5", "rank_p95", "gds_humans_only", "rank_humans_only"]
            + ["pillar_" + p for p in PILLARS] + [k + "_score" for k in INDICATORS] + list(INDICATORS)
            + ["slavery_per_1000_gsi2023", "api_farm_grade_2020", "population", "n_pillars", "share_imputed"])
    out = scored[cols].sort_values(["year", "rank", "iso3"])
    num = out.select_dtypes("float").columns
    out[num] = out[num].round(3)
    out.to_csv(f"{OUT}/gds_v2_country_year.csv", index=False)
    out[out.year == latest].dropna(subset=["gds"]).to_csv(f"{OUT}/gds_v2_{latest}.csv", index=False)

    gp = pd.DataFrame([(k, *INDICATORS[k], *goalposts[k]) for k in INDICATORS],
                      columns=["indicator", "label", "unit", "transform", "best_goalpost", "worst_goalpost"])
    gp.to_csv(f"{OUT}/goalposts.csv", index=False)

    # World trend: population-weighted mean GDS across ranked countries
    w = scored.dropna(subset=["rank", "population"])
    world = w.groupby("year").apply(lambda g: np.average(g.gds, weights=g.population)).round(2).rename("world_gds_pop_weighted")
    world = pd.concat([world, w.groupby("year").gds.median().round(2).rename("median_country_gds"),
                       w.groupby("year").size().rename("countries_ranked")], axis=1)
    world.to_csv(f"{OUT}/gds_v2_world_trend.csv")

    print(f"Wrote {OUT}/gds_v2_country_year.csv ({out.gds.notna().sum()} scored country-years)")
    print(world.loc[[2000, 2005, 2010, 2015, 2020, 2023]].to_string())


if __name__ == "__main__":
    main()
