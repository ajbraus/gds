#!/usr/bin/env bash
# Download raw inputs for the GDS v2 index into data/raw/<source>/.
# Usage: bash pipeline/fetch.sh   (run from the repo root)
set -euo pipefail
RAW="data/raw"
UA="Mozilla/5.0 (Macintosh) gds-index-pipeline"
get() { mkdir -p "$(dirname "$2")"; curl -sSfL -m 300 -A "$UA" -o "$2" "$1"; echo "  $2"; }

echo "OWID (UNODC, UCDP, ICPR, FAO)"
# Note: IHME GBD DALYs are not redistributable via OWID; see docs/gds-v2-plan.md for the optional IHME swap-in.
owid() { get "https://ourworldindata.org/grapher/$1.csv?v=1&csvType=full&useColumnShortNames=true" "$RAW/owid/$1.csv"; }
owid homicide-rate-unodc                 # UNODC: intentional homicides per 100k
owid death-rate-in-armed-conflicts       # UCDP: conflict deaths per 100k, where they occurred
owid prison-population-rate              # ICPR World Prison Brief: prisoners per 100k
owid animals-slaughtered-for-meat        # FAO: land animals slaughtered, by species

echo "UNDP Human Development Report (Gender Inequality Index)"
get "https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Composite_indices_complete_time_series.csv" \
    "$RAW/undp/HDR25_Composite_indices_complete_time_series.csv"

echo "WHO Global Health Observatory (healthy life expectancy, homicide estimates)"
get "https://ghoapi.azureedge.net/api/WHOSIS_000002" "$RAW/who/WHOSIS_000002.json"
get "https://ghoapi.azureedge.net/api/VIOLENCE_HOMICIDERATE" "$RAW/who/VIOLENCE_HOMICIDERATE.json"  # modelled homicide rates (fallback)

echo "World Bank (infant mortality, population, country list)"
get "https://api.worldbank.org/v2/country?format=json&per_page=400" "$RAW/worldbank/countries.json"
wb() { get "https://api.worldbank.org/v2/country/all/indicator/$1?format=json&per_page=20000&date=1990:2025" "$RAW/worldbank/$1.json"; }
wb SP.DYN.IMRT.IN
wb SP.POP.TOTL
wb SN.ITK.DEFC.ZS   # FAO prevalence of undernourishment
wb SI.POV.DDAY      # extreme poverty, $3.00/day (2021 PPP)

echo "UNHCR (refugees, asylum seekers and IDPs by country of origin)"
get "https://api.unhcr.org/population/v1/population/?limit=10000&yearFrom=2000&yearTo=2025&coo_all=true" "$RAW/unhcr/population_by_origin.json"

echo "World Animal Protection (Animal Protection Index 2020 rankings page)"
get "https://api.worldanimalprotection.org/rankings" "$RAW/wap/rankings.html"

echo "Walk Free (Global Slavery Index 2023 report; country table is parsed from the PDF)"
[ -f "$RAW/walkfree/Global-Slavery-Index-2023.pdf" ] || \
  get "https://cdn.walkfree.org/content/uploads/2023/05/17114737/Global-Slavery-Index-2023.pdf" "$RAW/walkfree/Global-Slavery-Index-2023.pdf"
echo "done"
