"""Round-16 descriptive, UNREGISTERED checks (adversarial review, 2026-09-22).

Usage, from the repository root:
    .venv/bin/python notes/scripts/diagnose_round16.py 2>&1 | tee notes/logs/round16.txt

Not an independent path: the same instruments the registered runs use. Nothing registered changes.

LL — THE DOWNSHIFT BAND. Round 15 found the observed gap between published and measured-only fold
     changes (+1.055) matches a simulation at the recovered downshift (+1.047). That agreement is
     only informative if the prediction MOVES with the downshift. A drawn cell in a three-value arm
     shifts that arm's mean by about a third of the distance between the measured values and the
     draw, so the predicted gap should move by roughly (change in downshift) x (column SD) / 3 —
     about 0.1 log2 units per 0.17 of downshift, ten times the observed agreement. Scanned here:
     the band of downshifts consistent with +1.055 is a SECOND, independent recovery of the
     parameter, from published fold changes rather than from cell values.
     What it cannot identify: the realisation, or any distribution with the same first moment.

MM — MOESM5, BY ARGMAX RATHER THAN ASSUMPTION. Round 15c compared MOESM5 against the six IFN
     columns only and found no reading. But the deposit also carries KO_P_* and WT_P_* (untreated),
     and a correlation of 0.707 on raw log2 is too high for unrelated data and too low for the same
     samples — which is what different conditions in the same cell lines look like. This correlates
     every published column against every deposited LFQ column and reads the mapping off the
     argmax. It subsumes the untreated-columns hypothesis: if the values live there, the argmax
     points there.
"""

import json
import math
import warnings

import numpy as np
from bzk.adapters import maxquant
from bzk.provenance.raw_store import raw_root, verify
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
from openpyxl import load_workbook

warnings.filterwarnings("ignore")
KO = ["Intensity KO_IFN_1", "Intensity KO_IFN_2", "Intensity KO_IFN_3"]
WT = ["Intensity WT_IFN_1", "Intensity WT_IFN_2", "Intensity WT_IFN_3"]
WIDTH = 0.29

table = maxquant.read_table(
    verify(PXD018299_SITES.expected_content_hash, filename=PXD018299_SITES.filename, home=HOME)
)
rows, column = anchor_population(table)
ids = [str(r[column["id"]]).strip() for r in rows]
index_of = {name: i for i, name in enumerate(ids)}


def raw_value(row: list[str], name: str) -> float:
    text = row[column[name]].strip() if name in column else ""
    try:
        return float(text)
    except ValueError:
        return 0.0


def provided(row: list[str], name: str) -> bool:
    return raw_value(row, name) > 0 or any(
        raw_value(row, f"{name}{suffix}") > 0 for suffix in ("___1", "___2", "___3")
    )


with open("tests/fixtures/pxd018299_published_cascade.json") as handle:
    cascade = json.load(handle)["rows"]
header, s1 = _s1_rows(_supplement_path(SUPP_DATA_1, HOME))
published_columns = s1_columns(header)

column_values = {name: [] for name in KO + WT}
for row in rows:
    for name in KO + WT:
        value = raw_value(row, name)
        if value > 0:
            column_values[name].append(math.log2(value))
column_mean = {name: float(np.mean(v)) for name, v in column_values.items()}
column_sd = {name: float(np.std(v, ddof=1)) for name, v in column_values.items()}
print("LL — the downshift band, from published fold changes")
print(f"  column SDs: {[round(column_sd[n], 2) for n in KO + WT]}")

records, observed_gaps = [], []
for claim in cascade:
    row = rows[index_of[str(claim["deposit_id"])]]
    values = [_float_cell(s1[int(claim["row"])].get(name)) for name in published_columns]
    drawn = [not provided(row, name) for name in KO + WT]
    if not any(drawn) or all(drawn[:3]) or all(drawn[3:]):
        continue
    ko_measured = [v for v, d in zip(values[:3], drawn[:3], strict=True) if not d]
    wt_measured = [v for v, d in zip(values[3:], drawn[3:], strict=True) if not d]
    measured_fc = np.mean(ko_measured) - np.mean(wt_measured)
    records.append((drawn, values, measured_fc))
    observed_gaps.append((np.mean(values[:3]) - np.mean(values[3:])) - measured_fc)
observed = float(np.median(observed_gaps))
print(f"  observed median gap over {len(records)} claims: {observed:+.3f}")

rng = np.random.default_rng(0)
print(f"  {'downshift':>10} {'predicted median gap':>22} {'consistent with observed?':>26}")
band = []
for downshift in (1.0, 1.2, 1.4, 1.6, 1.7, 1.77, 1.8, 1.9, 2.0, 2.2, 2.5):
    gaps = []
    for _ in range(200):
        for drawn, values, measured_fc in records:
            simulated = list(values)
            for position, name in enumerate(KO + WT):
                if drawn[position]:
                    simulated[position] = rng.normal(
                        column_mean[name] - downshift * column_sd[name], WIDTH * column_sd[name]
                    )
            gaps.append((np.mean(simulated[:3]) - np.mean(simulated[3:])) - measured_fc)
    predicted = float(np.median(gaps))
    # the sampling interval on the observed median, from the same simulation's spread
    spread = float(np.std([np.median(rng.choice(observed_gaps, size=len(observed_gaps))) for _ in range(400)]))
    consistent = abs(predicted - observed) <= 2 * spread
    if consistent:
        band.append(downshift)
    print(f"  {downshift:>10} {predicted:>+22.3f} {'yes' if consistent else 'no':>26}")
print(f"  bootstrap standard error on the observed median: {spread:.3f}")
print(f"  downshifts consistent with the observed gap: {band}")
print("  Readout C recovered 1.76-1.78 from the cell values; this recovers it from the published")
print("  fold changes. It identifies a first moment near that value, not the realisation.")

print("\nMM — MOESM5 by argmax: every published column against every deposited LFQ column")
moesm5 = next(iter(raw_root(HOME).glob("*/41416_2020_1167_MOESM5_ESM.xlsx")), None)
groups_path = next(iter(raw_root(HOME).glob("*/HAP1_USP18KO_proteinGroups.txt")), None)
book = load_workbook(moesm5, read_only=True, data_only=True)
body = [r for r in book.worksheets[0].iter_rows(values_only=True) if any(c is not None for c in r)]
head_index = next(i for i, r in enumerate(body) if any("LFQ intensity" in str(c) for c in r if c))
head = [str(c).strip() if c is not None else "" for c in body[head_index]]
published_rows = body[head_index + 1:]
groups = maxquant.read_table(groups_path)
group_column = {n: i for i, n in enumerate(groups.header)}
deposit_lfq = [n for n in groups.header if n.startswith("LFQ intensity")]
lookup: dict[str, list[str]] = {}
for row in groups.rows:
    for part in row[group_column["Protein IDs"]].split(";"):
        lookup.setdefault(part.strip(), row)
key_index = head.index("T: Protein IDs")
published_lfq = [n for n in head if n.startswith("LFQ intensity")]

paired = []
for row in published_rows:
    key = str(row[key_index]).split(";")[0].strip() if row[key_index] else ""
    group = lookup.get(key)
    if group is not None:
        paired.append((row, group))
print(f"  matched {len(paired)} of {len(published_rows)} claims")
print(f"  {'published column':>26} {'best deposited match':>34} {'r':>7} {'second best':>34} {'r':>7}")
for name in published_lfq:
    scores = []
    for deposit_name in deposit_lfq:
        pairs = []
        for row, group in paired:
            try:
                published = float(row[head.index(name)])
            except (TypeError, ValueError):
                continue
            text = group[group_column[deposit_name]].strip()
            try:
                value = float(text)
            except ValueError:
                continue
            if value > 0:
                pairs.append((published, math.log2(value)))
        if len(pairs) > 30:
            a, b = np.array(pairs).T
            scores.append((float(np.corrcoef(a, b)[0, 1]), deposit_name, len(pairs)))
    scores.sort(reverse=True)
    if scores:
        best, second = scores[0], scores[1] if len(scores) > 1 else (float("nan"), "-", 0)
        print(f"  {name:>26} {best[1]:>34} {best[0]:>7.3f} {second[1]:>34} {second[0]:>7.3f}")
print("  If the argmax is the identity mapping, the values are IFN-column intensities after some")
print("  transform. If it points at the untreated columns, the header names the wrong samples.")
print("  If no column stands out, the numbers match nothing deposited.")
