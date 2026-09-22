"""Two descriptive, UNREGISTERED checks on PXD018299, from an adversarial review of 2026-09-22.

Usage, from the repository root:  .venv/bin/python notes/scripts/diagnose_imputation_effects.py

Neither check touches a registered verdict, a pre-registration or a committed fixture.

CHECK 1 — does imputation decide the test?
  If a row's values are largely drawn, the comparison is between two columns' imputation centres
  rather than between measurements, so its P value should be set by column-level statistics: far
  from the threshold, and stable across draws. That would also explain why H10's instability rate
  is 21% rather than higher. The check reports support and instability by how many of a row's six
  values are imputed. NOTE: the seven wholly-imputed published claims are NOT in this matrix — the
  reconstruction's valid-value rule removes them — so the gradient is measured up to 5 of 6.

CHECK 2 — the authors' realised draw, with the reference distribution fixed.
  Data Table S1 is log2 of the deposit's site table, so S1's values at deposit-missing cells are the
  authors' own imputed draw. Readout C compared them against S1's 798 significant rows; the right
  reference is the deposit's own column distribution. Both are reported side by side.
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
from bzk.stats.imputation import downshifted_normal
from bzk.stats.perseus_s0 import perseus_s0

KO = ["Intensity KO_IFN_1", "Intensity KO_IFN_2", "Intensity KO_IFN_3"]
WT = ["Intensity WT_IFN_1", "Intensity WT_IFN_2", "Intensity WT_IFN_3"]
SEEDS = range(20)

deposit_path = verify(
    PXD018299_SITES.expected_content_hash, filename=PXD018299_SITES.filename, home=HOME
)
rows, column = anchor_population(maxquant.read_table(deposit_path))


def cell(row: list[str], name: str) -> float:
    raw = row[column[name]].strip() if name in column else ""
    try:
        value = float(raw)
    except ValueError:
        return math.nan
    return math.log2(value) if value > 0 else math.nan


matrix = np.array([[cell(r, name) for name in KO + WT] for r in rows])
ids = [str(r[column["id"]]).strip() for r in rows]
measured = ~np.isnan(matrix)
# The reconstruction's valid-value rule, as attempt 3 took it: at least 1 in at least one group.
keep = (measured[:, :3].sum(1) >= 1) | (measured[:, 3:].sum(1) >= 1)
print(f"population rows {len(rows)}, retained by 'at least 1 in a group' {int(keep.sum())}")

with open("tests/fixtures/pxd018299_published_cascade.json") as handle:
    cascade = json.load(handle)
claim_ids = {str(c["deposit_id"]) for c in cascade["rows"]}
kept_index = {name: i for i, name in enumerate([i for i, k in zip(ids, keep, strict=True) if k])}
kept = matrix[keep]
kept_measured = measured[keep]
is_claim = np.array([name in claim_ids for name, k in zip(ids, keep, strict=True) if k])
print(f"claims in the retained matrix: {int(is_claim.sum())}")

# --- CHECK 1 -------------------------------------------------------------------------------------
support = []
q_default = []
for seed in SEEDS:
    filled = downshifted_normal(kept, downshift_sd=1.8, width_sd=0.3, seed=seed, scope="per_sample").values
    outcome = perseus_s0(
        filled[:, :3], filled[:, 3:], s0=0.1, alpha=0.01, randomisations=250,
        seed=seed, sidedness="joint_half", scheme="random_excluding_trivial",
    )
    support.append(outcome.significant & (outcome.direction > 0))
    q_default.append(outcome.q_value)
support = np.array(support).T
q = np.median(np.array(q_default).T, axis=1)
imputed_count = 6 - kept_measured.sum(1)

print("\nCHECK 1 — support and instability by how many of the six values are imputed (claims only)")
print(f"{'imputed':>8} {'claims':>7} {'supported':>10} {'unstable':>9} {'median q':>10}")
for n in range(7):
    rows_n = is_claim & (imputed_count == n)
    if not rows_n.any():
        continue
    counts = support[rows_n].sum(1)
    supported = int((counts >= 10).sum())
    unstable = int(((counts > 0) & (counts < 20)).sum())
    print(f"{n:>8} {int(rows_n.sum()):>7} {supported:>10} {unstable:>9} {np.median(q[rows_n]):>10.2e}")

# --- CHECK 2 -------------------------------------------------------------------------------------
header, s1 = _s1_rows(_supplement_path(SUPP_DATA_1, HOME))
published_columns = s1_columns(header)
row_of_id = {name: i for i, name in enumerate(ids)}
drawn: dict[str, list[float]] = {name: [] for name in published_columns}
s1_measured: dict[str, list[float]] = {name: [] for name in published_columns}
for claim in cascade["rows"]:
    i = row_of_id.get(str(claim["deposit_id"]))
    published = s1.get(int(claim["row"]))
    if i is None or published is None:
        continue
    for j, name in enumerate(published_columns):
        value = _float_cell(published.get(name))
        if math.isnan(value):
            continue
        (drawn if math.isnan(matrix[i, j]) else s1_measured)[name].append(value)

print("\nCHECK 2 — the authors' realised draw, against two reference distributions")
print("  (downshift = (reference mean - drawn mean) / reference SD;  width = drawn SD / reference SD)")
print(f"{'column':>22} {'drawn':>6} {'ref: deposit column':>28} {'ref: S1 significant rows':>30}")
for j, name in enumerate(published_columns):
    values = np.array(drawn[name])
    if values.size == 0:
        continue
    deposit_column = kept[:, j][~np.isnan(kept[:, j])]
    s1_rows_column = np.array(s1_measured[name])
    out = []
    for reference in (deposit_column, s1_rows_column):
        if reference.size < 2:
            out.append("n/a")
            continue
        down = (reference.mean() - values.mean()) / reference.std(ddof=1)
        width = values.std(ddof=1) / reference.std(ddof=1)
        out.append(f"n {reference.size:>5}  down {down:>5.2f}  width {width:>4.2f}")
    print(f"{name:>22} {values.size:>6} {out[0]:>28} {out[1]:>30}")
print("  Perseus defaults: downshift 1.8, width 0.3")
