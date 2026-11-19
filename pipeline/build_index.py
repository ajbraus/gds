"""Build the Gross Domestic Suffering (GDS) v2 index: one score per country per year.

Usage (repo root):
    bash pipeline/fetch.sh            # download raw data
    python3 -I pipeline/extract.py    # PDF/HTML tables -> data/interim/
    python3 -I pipeline/build_index.py

Method (see docs/gds-v2-plan.md):
  1. Assemble nine indicators per country-year, 2000-2023. Every indicator is framed
     as suffering: higher = worse.
  2. Fill gaps within each country: linear interpolation between observed years,
     held flat up to MAX_EXTEND years beyond the first/last observation.
  3. Transform (log for skewed rates) and rescale to 0-100 with FIXED goalposts
     (2.5th / 97.5th percentile of all observed country-years), so a country's
     score changes only when its own data changes.
  4. Average into six equally weighted pillars: Illness, Gender inequality, Violence,
     Unfreedom, Deprivation and Animal suffering. Illness averages two indicators
     because infant mortality is also inside healthy life expectancy.
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
MAX_EXTEND_BY = {"homicide": 10, "prison": 10, "poverty": 10}  # poverty surveys are also irregular
HALE_REFERENCE = 75.0   # healthy life years benchmark (close to the best observed national HALE)
GOALPOST_PCT = (2.5, 97.5)
MIN_PILLARS = 5

# Animal Protection Index grade -> multiplier on animals slaughtered per person.
# D (the median grade) is neutral; unrated countries get 1.0.
API_FACTOR = {"A": 0.70, "B": 0.80, "C": 0.90, "D": 1.00, "E": 1.10, "F": 1.20, "G": 1.30}

INDICATORS = {
    # key: (label, unit, transform)
    "illness_burden":    ("Healthy life years lost to illness and early death", f"years below {HALE_REFERENCE:g} (WHO HALE)", "linear"),
    "infant_mortality":  ("Infant mortality", "deaths per 1,000 live births", "log"),
    "gender_inequality": ("Gender Inequality Index", "0-1 (UNDP)", "linear"),
    "violence":          ("Violent deaths", "homicide (UNODC, WHO fallback) + conflict deaths (UCDP) per 100k", "log1p"),
    "unfreedom":         ("Unfree people", "prisoners + people in modern slavery per 100k", "log"),
    "undernourishment":  ("Undernourishment", "% of population (FAO)", "log"),
    "extreme_poverty":   ("Extreme poverty", "% below $3.00/day, 2021 PPP (World Bank)", "log1p"),
    "displacement":      ("Forcibly displaced people", "refugees, asylum seekers and IDPs by origin per 100k (UNHCR)", "log1p"),
    "animal_suffering":  ("Animal suffering", "welfare-adjusted land animals slaughtered per person", "log1p"),
}
PILLARS = {
    "illness":           ["illness_burden", "infant_mortality"],
    "gender_inequality": ["gender_inequality"],
    "violence":          ["violence"],
    "unfreedom":         ["unfreedom"],
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


def load_raw():
    out = {}
    hale = pd.DataFrame(json.load(open(f"{RAW}/who/WHOSIS_000002.json"))["value"])
    hale = hale[(hale.SpatialDimType == "COUNTRY") & (hale.Dim1 == "SEX_BTSX")]
    out["hale"] = hale.rename(columns={"SpatialDim": "iso3", "TimeDim": "year", "NumericValue": "value"})[["iso3", "year", "value"]]
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

    out["slavery"] = pd.read_csv(f"{INTERIM}/gsi2023_slavery.csv")
    out["api"] = pd.read_csv(f"{INTERIM}/api2020_grades.csv")
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

    hale, imp["illness_burden"] = fill(raw["hale"], isos)
    vals["illness_burden"] = (HALE_REFERENCE - hale).clip(lower=0)
    vals["infant_mortality"], imp["infant_mortality"] = fill(raw["imr"], isos)
    vals["gender_inequality"], imp["gender_inequality"] = fill(raw["gii"], isos)

    hom, hom_imp = fill(raw["homicide"], isos, MAX_EXTEND_BY["homicide"])
    # Fall back to WHO's modelled homicide estimates where UNODC has no usable figure
    who_hom, _ = fill(raw["homicide_who"], isos)
    hom_imp = hom_imp | (hom.isna() & who_hom.notna())
    hom = hom.fillna(who_hom)
    con, con_imp = fill(raw["conflict"], isos)
    con = con.fillna(0)  # UCDP records every conflict; no entry means no recorded conflict deaths
    vals["violence"] = hom + con
    imp["violence"] = hom_imp

    prison, prison_imp = fill(raw["prison"], isos, MAX_EXTEND_BY["prison"])
    sl = raw["slavery"].set_index("iso3").slavery_per_1000.reindex(isos)
    # Regional median for countries Walk Free does not estimate (mostly small states)
    regions = {r["id"]: r["region"]["value"] for r in json.load(open(f"{RAW}/worldbank/countries.json"))[1]}
    reg = pd.Series({i: regions.get(i) for i in isos})
    sl_filled = sl.fillna(sl.groupby(reg).transform("median"))
    slavery_100k = pd.DataFrame(np.repeat(sl_filled.values[:, None] * 100, len(YEARS), axis=1), index=isos, columns=YEARS)
    vals["unfreedom"] = prison + slavery_100k
    imp["unfreedom"] = prison_imp | pd.DataFrame(np.repeat(sl.isna().values[:, None], len(YEARS), axis=1), index=isos, columns=YEARS)

    pop, _ = fill(raw["pop"], isos)
    vals["undernourishment"], imp["undernourishment"] = fill(raw["undernourishment"], isos)
    vals["extreme_poverty"], imp["extreme_poverty"] = fill(raw["poverty"], isos, MAX_EXTEND_BY["poverty"])
    displaced, imp["displacement"] = fill(raw["displaced"], isos)
    # UNHCR lists origins with displaced people; a country it never lists has none recorded
    listed = raw["displaced"].iso3.unique()
    displaced.loc[~displaced.index.isin(listed)] = 0
    vals["displacement"] = displaced / pop * 1e5
    sla, sla_imp = fill(raw["slaughtered"], isos)
    factor = raw["api"].set_index("iso3").api_grade.map(API_FACTOR).reindex(isos).fillna(1.0)
    vals["animal_suffering"] = (sla / pop).mul(factor, axis=0)
    imp["animal_suffering"] = sla_imp

    long = []
    for k in INDICATORS:
        v = vals[k].stack(dropna=False).rename(k)
        i = imp[k].reindex_like(vals[k]).fillna(False).stack(dropna=False).rename(k + "_imputed")
        long += [v, i]
    df = pd.concat(long, axis=1).reset_index().rename(columns={"level_0": "iso3", "level_1": "year"})
    df.insert(1, "country", df.iso3.map(countries))
    df["population"] = pop.stack(dropna=False).reindex(pd.MultiIndex.from_frame(df[["iso3", "year"]])).values
    df["slavery_per_1000_gsi2023"] = df.iso3.map(sl)
    df["api_grade_2020"] = df.iso3.map(raw["api"].set_index("iso3").api_grade)
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
            goalposts[k] = tuple(np.percentile(t, GOALPOST_PCT))
    for k, (_, _, kind) in INDICATORS.items():
        lo, hi = goalposts[k]
        df[k + "_score"] = (100 * (transform(df[k], kind) - lo) / (hi - lo)).clip(0, 100)
    for p, ks in PILLARS.items():
        df["pillar_" + p] = df[[k + "_score" for k in ks]].mean(axis=1)
    P = df[["pillar_" + p for p in PILLARS]]
    W = pd.Series({"pillar_" + p: w for p, w in weights.items()})
    avail = P.notna()
    df["n_pillars"] = avail.sum(axis=1)
    df["gds"] = (P.fillna(0) * W).sum(axis=1) / (avail * W).sum(axis=1)
    ok = (df.n_pillars >= MIN_PILLARS) & df.pillar_illness.notna()
    df.loc[~ok, "gds"] = np.nan
    df["rank"] = df.groupby("year").gds.rank(method="min")
    df["n_ranked"] = df.groupby("year").gds.transform("count")
    imp_cols = [k + "_imputed" for k in INDICATORS]
    df["share_imputed"] = df[imp_cols].astype(float).mean(axis=1).round(2)
    return df, goalposts


def rank_ranges(df, year, n=1000, seed=7):
    """Rank uncertainty from random pillar weights (Dirichlet, alpha=4 → mostly within ±10 points of 20%)."""
    rng = np.random.default_rng(seed)
    d = df[df.year == year].set_index("iso3")
    P = d[["pillar_" + p for p in PILLARS]]
    ok = d.gds.notna()
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
    always = scored.groupby("iso3").gds.apply(lambda g: g.notna().all())
    panel_set = always[always].index
    in_panel = scored.iso3.isin(panel_set)
    scored.loc[in_panel, "rank_constant_set"] = scored[in_panel].groupby("year").gds.rank(method="min")
    print(f"Constant comparison set: {len(panel_set)} countries scored every year {YEARS[0]}-{YEARS[-1]}")

    latest = max(YEARS)
    rr = rank_ranges(scored, latest)
    scored = scored.merge(rr.reset_index().assign(year=latest), on=["iso3", "year"], how="left")

    cols = (["iso3", "country", "year", "gds", "rank", "n_ranked", "rank_constant_set", "rank_p5", "rank_p95", "gds_humans_only", "rank_humans_only"]
            + ["pillar_" + p for p in PILLARS] + [k + "_score" for k in INDICATORS] + list(INDICATORS)
            + ["slavery_per_1000_gsi2023", "api_grade_2020", "population", "n_pillars", "share_imputed"])
    out = scored[cols].sort_values(["year", "rank", "iso3"])
    num = out.select_dtypes("float").columns
    out[num] = out[num].round(3)
    out.to_csv(f"{OUT}/gds_v2_country_year.csv", index=False)
    out[out.year == latest].dropna(subset=["gds"]).to_csv(f"{OUT}/gds_v2_{latest}.csv", index=False)

    gp = pd.DataFrame([(k, *INDICATORS[k], *goalposts[k]) for k in INDICATORS],
                      columns=["indicator", "label", "unit", "transform", "best_goalpost", "worst_goalpost"])
    gp.to_csv(f"{OUT}/goalposts.csv", index=False)

    # World trend: population-weighted mean GDS across ranked countries
    w = scored.dropna(subset=["gds", "population"])
    world = w.groupby("year").apply(lambda g: np.average(g.gds, weights=g.population)).round(2).rename("world_gds_pop_weighted")
    world = pd.concat([world, w.groupby("year").gds.median().round(2).rename("median_country_gds"),
                       w.groupby("year").size().rename("countries_ranked")], axis=1)
    world.to_csv(f"{OUT}/gds_v2_world_trend.csv")

    print(f"Wrote {OUT}/gds_v2_country_year.csv ({out.gds.notna().sum()} scored country-years)")
    print(world.loc[[2000, 2005, 2010, 2015, 2020, 2023]].to_string())


if __name__ == "__main__":
    main()
