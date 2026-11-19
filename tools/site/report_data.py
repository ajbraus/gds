"""Summarize the index for the US and global reports into data/output/report_data.json.

Usage: python3 -I tools/site/report_data.py
Run after pipeline/build_index.py. The site build reads the JSON (no pandas needed there);
the report text in reports.py quotes these figures, so re-check it after a rebuild."""
import json, os
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = f"{ROOT}/data/output"
PILLARS = ["illness", "discrimination", "violence", "unfreedom", "deprivation", "animal_suffering"]
INDICATORS = ["premature_death", "infant_mortality", "ill_health_share", "substance_deaths", "gender_inequality",
              "lgbti_laws", "violence", "captivity", "overwork", "undernourishment", "extreme_poverty", "displacement"]
YEARS = list(range(2000, 2024))


def pw(g, col):
    """Population-weighted mean over countries with a value."""
    g = g.dropna(subset=[col, "population"])
    return round(float(np.average(g[col], weights=g.population)), 2) if len(g) else None


def main():
    d = pd.read_csv(f"{OUT}/gds_v2_country_year.csv")
    d = d[d["rank"].notna()].copy()
    meta = {r["id"]: (r["region"]["value"].strip(), r["incomeLevel"]["value"])
            for r in json.load(open(f"{ROOT}/data/raw/worldbank/countries.json"))[1]}
    d["region"] = d.iso3.map(lambda i: meta.get(i, ("?", "?"))[0])
    d["income"] = d.iso3.map(lambda i: meta.get(i, ("?", "?"))[1])
    by_year = {y: g for y, g in d.groupby("year")}
    rich = d[(d.income == "High income") & (d.iso3 != "USA")]  # other high-income countries
    rich_year = {y: g for y, g in rich.groupby("year")}

    us = d[d.iso3 == "USA"].set_index("year")
    out = {
        "years": YEARS,
        "world": {
            "gds": [pw(by_year[y], "gds") for y in YEARS],
            "pillars": {p: [pw(by_year[y], "pillar_" + p) for y in YEARS] for p in PILLARS},
            "indicators": {k: {str(y): pw(by_year[y], k) for y in (2000, 2010, 2019, 2023)} for k in INDICATORS},
            "regions": {r: {str(y): pw(g[g.year == y], "gds") for y in (2000, 2023)} for r, g in d.groupby("region")},
            "income": {r: {str(y): pw(g[g.year == y], "gds") for y in (2000, 2023)} for r, g in d.groupby("income")},
            "pop_high_suffering_bn": {str(y): round(by_year[y][by_year[y].gds >= 70].population.sum() / 1e9, 2) for y in (2000, 2023)},
            "n_high_suffering": {str(y): int((by_year[y].gds >= 70).sum()) for y in (2000, 2023)},
        },
        "rich": {
            "gds": [pw(rich_year[y], "gds") for y in YEARS],
            "pillars_2023": {p: pw(rich_year[2023], "pillar_" + p) for p in PILLARS},
            "indicators_2023_median": {k: round(float(rich_year[2023][k].median()), 2) for k in INDICATORS},
        },
        "us": {
            "gds": [round(float(us.gds[y]), 2) for y in YEARS],
            "rank": [int(us["rank"][y]) for y in YEARS],
            "n_ranked": [int(us.n_ranked[y]) for y in YEARS],
            "pillars": {p: [round(float(us["pillar_" + p][y]), 2) for y in YEARS] for p in PILLARS},
            "indicators": {k: {str(y): round(float(us[k][y]), 2) for y in (2000, 2010, 2019, 2023)} for k in INDICATORS},
        },
    }
    change = d[d.year.isin([2000, 2023])].pivot(index="iso3", columns="year", values="gds").dropna()
    change["delta"] = change[2023] - change[2000]
    names = d.drop_duplicates("iso3").set_index("iso3").country
    pop = by_year[2023].set_index("iso3").population
    big = change[pop.reindex(change.index) > 20e6].sort_values("delta")
    out["world"]["compared"] = int(len(change))
    out["world"]["improved"] = int((change.delta < 0).sum())
    out["world"]["big_improvers"] = [(names[i], round(float(v), 1)) for i, v in big.delta.head(6).items()]
    out["world"]["big_worse"] = [(names[i], round(float(v), 1)) for i, v in big.delta[big.delta > 0].sort_values(ascending=False).items()]
    json.dump(out, open(f"{OUT}/report_data.json", "w"), indent=1)
    print(f"Wrote {OUT}/report_data.json")


if __name__ == "__main__":
    main()
