"""Country universe and name -> ISO3 lookup shared by the pipeline."""
import json
import re
import unicodedata

import pandas as pd

RAW = "data/raw"

# Names used by Walk Free, World Animal Protection and others that don't match
# World Bank / OWID spellings.
OVERRIDES = {
    "usa": "USA", "united states": "USA", "korea": "KOR", "south korea": "KOR",
    "north korea": "PRK", "iran": "IRN", "russia": "RUS", "vietnam": "VNM",
    "viet nam": "VNM", "lao pdr": "LAO", "laos": "LAO", "democratic republic": "COD",
    "democratic republic of the congo": "COD", "republic of the congo": "COG",
    "congo": "COG", "cote d'ivoire": "CIV", "ivory coast": "CIV", "hong kong": "HKG",
    "taiwan": "TWN", "kosovo": "XKX", "czechia": "CZE", "czech republic": "CZE",
    "syria": "SYR", "turkey": "TUR", "turkiye": "TUR", "egypt": "EGY",
    "venezuela": "VEN", "gambia": "GMB", "kyrgyzstan": "KGZ", "slovakia": "SVK",
    "yemen": "YEM", "bolivia": "BOL", "moldova": "MDA", "tanzania": "TZA",
    "eswatini": "SWZ", "brunei": "BRN", "palestine": "PSE", "micronesia": "FSM",
    "cape verde": "CPV", "macedonia": "MKD", "east timor": "TLS",
}


def norm(name):
    s = str(name).replace("’", "'")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().strip()
    return re.sub(r"\s+", " ", s)


def universe():
    """Sovereign countries/territories from the World Bank list (excludes aggregates)."""
    meta, rows = json.load(open(f"{RAW}/worldbank/countries.json"))
    out = {r["id"]: r["name"] for r in rows if r["region"]["value"] != "Aggregates"}
    out["TWN"] = "Taiwan"  # not in the World Bank list, but in several sources
    return out


def lookup():
    table = {norm(v): k for k, v in universe().items()}
    for f in ["homicide-rate-unodc", "prison-population-rate"]:
        d = pd.read_csv(f"{RAW}/owid/{f}.csv", usecols=["entity", "code"]).dropna()
        for e, c in d.drop_duplicates().itertuples(index=False):
            if len(c) == 3:
                table.setdefault(norm(e), c)
    table.update(OVERRIDES)
    return table


def to_iso3(name, table=None):
    table = table or lookup()
    return table.get(norm(name))
