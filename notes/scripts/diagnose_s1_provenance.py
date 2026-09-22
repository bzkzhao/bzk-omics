"""Descriptive, UNREGISTERED check of where PXD018299's Data Table S1 intensities come from.

Usage, from the repository root:  .venv/bin/python notes/scripts/diagnose_s1_provenance.py

H10's attempts found only ~2% of S1's measured cells equal log2 of the deposited site table's values
exactly (within 1e-6), and 7 published claims with no site-table value. An adversarial review
(2026-09-22) proposed a cheaper explanation than a separate run: the paper counts GlyGly PEPTIDES,
so S1 may be quantified from the peptide-level table of the same search. An exact-equality test also
cannot rule out spreadsheet rounding or a per-column offset. This script reports, and changes nothing:

  1. S1's full header, so its identifying columns are visible.
  2. For cells where the site table has a value: the distribution of S1 - log2(site), the share
     within 0.01 / 0.1 / 0.5, the per-column median offset, and the correlation.
  3. Which files in the local raw store look like peptide-level MaxQuant tables, so they can be
     compared next.
"""

import json
import math

import numpy as np

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

header, s1 = _s1_rows(_supplement_path(SUPP_DATA_1, HOME))
print("S1 header:", header)
columns = s1_columns(header)
print("S1 intensity columns:", columns)

deposit_path = verify(PXD018299_SITES.expected_content_hash, filename=PXD018299_SITES.filename, home=HOME)
rows, column = anchor_population(maxquant.read_table(deposit_path))
row_of_id = {str(r[column["id"]]).strip(): r for r in rows}
with open("tests/fixtures/pxd018299_published_cascade.json") as handle:
    cascade = json.load(handle)

diffs = {name: [] for name in columns}
pairs = []
for claim in cascade["rows"]:
    site = row_of_id.get(str(claim["deposit_id"]))
    published = s1.get(int(claim["row"]))
    if site is None or published is None:
        continue
    for name in columns:
        raw = site[column[name]].strip() if name in column else ""
        try:
            value = float(raw)
        except ValueError:
            continue
        if value <= 0 or math.isnan(value):
            continue
        s1_value = _float_cell(published.get(name))
        if math.isnan(s1_value):
            continue
        d = s1_value - math.log2(value)
        diffs[name].append(d)
        pairs.append((math.log2(value), s1_value))

all_d = np.array([d for v in diffs.values() for d in v])
print(f"\nmeasured cells compared: {len(all_d)}")
for tol in (1e-6, 0.01, 0.1, 0.5, 1.0):
    print(f"  |S1 - log2(site)| <= {tol}: {int((np.abs(all_d) <= tol).sum())} ({(np.abs(all_d) <= tol).mean():.1%})")
print("  quantiles of S1 - log2(site), 1/5/25/50/75/95/99%:",
      [round(float(q), 3) for q in np.percentile(all_d, [1, 5, 25, 50, 75, 95, 99])])
print("  share with S1 < log2(site) (a site sums its peptides, so a single peptide would be lower):",
      f"{(all_d < -1e-6).mean():.1%}")
for name, values in diffs.items():
    v = np.array(values)
    print(f"  {name}: n {len(v)}, median offset {np.median(v):+.3f}, IQR {np.percentile(v, 25):+.3f} to {np.percentile(v, 75):+.3f}")
x, y = np.array(pairs).T
print(f"  correlation of S1 with log2(site): {np.corrcoef(x, y)[0, 1]:.4f}")

print("\npeptide-level candidates in the raw store (compare these next):")
for path in sorted((HOME / "raw").glob("*/*")):
    lower = path.name.lower()
    if "peptide" in lower or "evidence" in lower:
        print("  ", path.parent.name[:12], path.name)
