"""Extract country tables that are only published as PDF/HTML into data/interim/.

- Walk Free Global Slavery Index 2023: prevalence of modern slavery per 1,000 people
- World Animal Protection Animal Protection Index 2020: overall grade A-G, and the
  farm-animal grade from each country profile

Usage (repo root): python3 -I pipeline/extract.py
Requires pdftotext (poppler).
"""
import html
import os
import re
import subprocess
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from countries import lookup, norm  # noqa: E402

RAW, INTERIM = "data/raw", "data/interim"
os.makedirs(INTERIM, exist_ok=True)
table = lookup()


def slavery():
    pdf = f"{RAW}/walkfree/Global-Slavery-Index-2023.pdf"
    text = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, check=True).stdout.decode("utf8")
    # Rows look like: "[rank]  Country name   prevalence  number  population"
    pat = re.compile(r"(?:\d{1,3}\s+)?([A-Z][A-Za-zôéç’'.()\- ]{1,48}?)\s{2,}(\d{1,3}\.\d)\s+([\d,]{3,})\s+([\d,]{5,})(?=\s|$)")
    found = {}
    for line in text.splitlines():
        for m in pat.finditer(line):
            iso = table.get(norm(m.group(1)))
            if iso:
                prev, number, pop = float(m.group(2)), int(m.group(3).replace(",", "")), int(m.group(4).replace(",", ""))
                # sanity check: prevalence ≈ number / population * 1000
                if abs(number / pop * 1000 - prev) <= max(0.6, prev * 0.1):
                    found.setdefault(iso, (m.group(1).strip(), prev, number, pop))
    df = pd.DataFrame([(k, *v) for k, v in found.items()],
                      columns=["iso3", "name_in_source", "slavery_per_1000", "people_in_slavery", "population"])
    df.sort_values("iso3").to_csv(f"{INTERIM}/gsi2023_slavery.csv", index=False)
    print(f"Global Slavery Index 2023: {len(df)} countries")


def animal_protection():
    s = open(f"{RAW}/wap/rankings.html", encoding="utf8").read()
    s = re.sub(r"<script.*?</script>|<style.*?</style>", "", s, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", "|", s))
    t = re.sub(r"\s*\|[\s|]*", "|", t)
    rows = {}
    for grade, name in re.findall(r"\|([A-G])\|([A-Z][A-Za-z .]+?)\|Compare\|Profile", t):
        iso = table.get(norm(name))
        if not iso:
            print("  unmatched API country:", name)
            continue
        rows[iso] = (name, grade)
    df = pd.DataFrame([(k, *v) for k, v in rows.items()], columns=["iso3", "name_in_source", "api_grade"])
    df.sort_values("iso3").to_csv(f"{INTERIM}/api2020_grades.csv", index=False)
    print(f"Animal Protection Index 2020: {len(df)} countries")


def animal_protection_farm():
    """Grade for 'Protecting animals used in farming' from each API 2020 country profile."""
    grades = pd.read_csv(f"{INTERIM}/api2020_grades.csv")
    rows = []
    for iso, name, overall in grades.itertuples(index=False):
        s = open(f"{RAW}/wap/countries/{name.lower().replace(' ', '-')}.html", encoding="utf8").read()
        t = html.unescape(re.sub(r"<[^>]+>", "|", re.sub(r"<script.*?</script>|<style.*?</style>", "", s, flags=re.S)))
        m = re.search(r"\|([A-G])\|Protecting animals used in farming\|", re.sub(r"\s*\|[\s|]*", "|", t))
        # The Netherlands profile has no farming section; fall back to its overall grade
        rows.append((iso, name, m.group(1) if m else overall, "farming" if m else "overall (no farming section)"))
    df = pd.DataFrame(rows, columns=["iso3", "name_in_source", "farm_grade", "grade_basis"])
    df.to_csv(f"{INTERIM}/api2020_farm_grades.csv", index=False)
    print(f"Animal Protection Index 2020 farm-animal grades: {len(df)} countries")


if __name__ == "__main__":
    slavery()
    animal_protection()
    animal_protection_farm()
