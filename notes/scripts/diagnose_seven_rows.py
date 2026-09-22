"""Descriptive, UNREGISTERED look at the seven published claims with no measured deposit value.

Usage, from the repository root:  .venv/bin/python notes/scripts/diagnose_seven_rows.py

`diagnose_s1_provenance.py` showed Data Table S1 IS log2 of the deposited site table: all 2,437
measured cells agree within 0.01, correlation 1.0000, and the ~2% exact-match rate was a rounding
artefact of a 1e-6 tolerance. That leaves one thing unexplained: attempt 3 found 7 published claims
(deposit ids 124, 434, 562, 1070, 1140, 1233, 1903) whose six summed intensities are all absent in
the deposit, though S1 carries six values for them.

This prints, for each of those rows and for a summary of the rest: the deposit's six summed values,
any per-multiplicity (___1/2/3) values, S1's six values, and the row's localisation probability and
score. If the summed columns are empty while `___n` columns carry values, the paper analysed the
expanded table. If the deposit is empty either way, the rows were published as significant on
entirely imputed values.
"""

import json
import math

from bzk.adapters import maxquant
from bzk.provenance.raw_store import verify
from bzk.sources.pxd018299_h10 import (
    HOME,
    PXD018299_SITES,
    SUPP_DATA_1,
    _float_cell,
    _s1_rows,
    _supplement_path,
    anchor_population,
    s1_columns,
)

SEVEN = {"124", "434", "562", "1070", "1140", "1233", "1903"}

header, s1 = _s1_rows(_supplement_path(SUPP_DATA_1, HOME))
columns = s1_columns(header)
deposit_path = verify(
    PXD018299_SITES.expected_content_hash, filename=PXD018299_SITES.filename, home=HOME
)
table = maxquant.read_table(deposit_path)
rows, column = anchor_population(table)
row_of_id = {str(r[column["id"]]).strip(): r for r in rows}
multiplicity = [name for name in table.header if name.startswith("Intensity ") and "___" in name]
print("per-multiplicity intensity columns in the deposit:", multiplicity or "none")

with open("tests/fixtures/pxd018299_published_cascade.json") as handle:
    cascade = json.load(handle)

fully_imputed = 0
for claim in cascade["rows"]:
    site = row_of_id.get(str(claim["deposit_id"]))
    published = s1.get(int(claim["row"]))
    if site is None or published is None:
        continue

    def value(name: str, row: list[str] = site) -> float:
        raw = row[column[name]].strip() if name in column else ""
        try:
            return float(raw)
        except ValueError:
            return 0.0

    summed = [value(name) for name in columns]
    if max(summed) > 0:
        continue
    fully_imputed += 1
    if str(claim["deposit_id"]) not in SEVEN:
        continue
    expanded = {name: value(name) for name in multiplicity if value(name) > 0}
    s1_values = [_float_cell(published.get(name)) for name in columns]
    print(f"\ndeposit id {claim['deposit_id']} (S1 row {claim['row']}):")
    print("  deposit summed:", summed)
    print("  deposit per-multiplicity, non-zero:", expanded or "none")
    print("  S1 values:", [round(v, 3) if not math.isnan(v) else None for v in s1_values])
    for field in ("Localization prob", "Score", "PEP", "Reverse", "Potential contaminant"):
        if field in column:
            print(f"  deposit {field}: {site[column[field]]!r}")

print(f"\npublished claims with no measured summed value anywhere: {fully_imputed}")
