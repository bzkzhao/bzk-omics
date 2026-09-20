"""How far PXD026748's summed site intensities diverge from the per-multiplicity ones the paper analysed.

Usage, from the repository root:

    .venv/bin/python notes/scripts/measure_multiplicity.py

Registered against walk/PREREG-PXD026748-multiplicity.md, which is committed before this runs.
Read-only: it parses the GG site table offline, writes nothing, and never touches a graph. It locates
the deposit by the record's digest and filters rows with the adapter's own `_filter`, the same
population the ingestion used.

Optional: `--file PATH` reads a site table from PATH instead of the raw store. That exists only so the
script can be exercised on synthetic data; the registered run uses the raw store.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

from bzk.adapters import maxquant
from bzk.curation.loader import load_path
from bzk.rebuild import _adapter_for, _deposit_for

RECORD = Path("data/curation/curation_PXD026748.json")
PREFIX = "Intensity "
MULTIPLICITIES = (1, 2, 3)

parser = argparse.ArgumentParser()
parser.add_argument("--home", type=Path, default=Path.home() / ".bzk-omics")
parser.add_argument("--file", type=Path, default=None)
args = parser.parse_args()

loaded = load_path(RECORD)
deposit = args.file if args.file is not None else _deposit_for(loaded, args.home)
if deposit is None:
    raise SystemExit("STOP: the GG deposit is not in the raw store")
adapter = _adapter_for(loaded, deposit, None)
if adapter is None:
    raise SystemExit("STOP: no adapter claims the file")

table = maxquant.read_table(deposit)
column = {name: i for i, name in enumerate(table.header)}
kept, _, _ = adapter._filter(table, column)

mapping = json.loads(RECORD.read_text(encoding="utf-8"))["mapping"]
labels = [key[len(PREFIX):] for key in mapping]
group_of = {key[len(PREFIX):]: (v["genotype"], v["treatment"]) for key, v in mapping.items()}


def num(row: list[str], name: str) -> float:
    i = column.get(name)
    if i is None or i >= len(row):
        return 0.0
    try:
        value = float(row[i])
    except ValueError:
        return 0.0
    return 0.0 if math.isnan(value) else value


print("== Q1. per-multiplicity columns ==")
present = {m: sum(f"{PREFIX}{lab}___{m}" in column for lab in labels) for m in MULTIPLICITIES}
print("labels:", len(labels), "| columns present per multiplicity:", present)
if any(n != len(labels) for n in present.values()):
    raise SystemExit("STOP: not every label has all three multiplicity columns; the question is moot")

print("\n== population ==")
print("sites after decoy/contaminant and localisation (the adapter's _filter):", len(kept))

summed = [{lab: num(r, f"{PREFIX}{lab}") for lab in labels} for r in kept]
per_m = [{m: {lab: num(r, f"{PREFIX}{lab}___{m}") for lab in labels} for m in MULTIPLICITIES} for r in kept]

print("\n== sanity: summed == ___1 + ___2 + ___3, per cell ==")
cells = agree = 0
for s, pm in zip(summed, per_m):
    for lab in labels:
        cells += 1
        total = sum(pm[m][lab] for m in MULTIPLICITIES)
        if abs(s[lab] - total) <= 1e-6 * max(1.0, s[lab]):
            agree += 1
print(f"cells agreeing: {agree} of {cells}")

print("\n== Q2. expanded rows ==")
rows_by_m = {m: sum(any(pm[m][lab] > 0 for lab in labels) for pm in per_m) for m in MULTIPLICITIES}
print("rows with any positive value, by multiplicity:", rows_by_m, "| total:", sum(rows_by_m.values()))

print("\n== Q3. sites whose summed value differs from ___1 ==")
multi = sum(any(pm[2][lab] > 0 or pm[3][lab] > 0 for lab in labels) for pm in per_m)
only_multi = sum(
    (not any(pm[1][lab] > 0 for lab in labels)) and any(s[lab] > 0 for lab in labels)
    for s, pm in zip(summed, per_m)
)
print(f"sites with a positive ___2 or ___3 in any run: {multi} of {len(kept)}")
print(f"sites with no positive ___1 in any run but a positive summed value: {only_multi}")


def log2_median(values: list[float]) -> float:
    return statistics.median(math.log2(v) for v in values if v > 0)


print("\n== Q4. per-sample median of log2 intensity: expanded rows vs summed rows ==")
diffs = []
for lab in labels:
    expanded = [pm[m][lab] for pm in per_m for m in MULTIPLICITIES]
    plain = [s[lab] for s in summed]
    d = log2_median(expanded) - log2_median(plain)
    diffs.append(d)
    print(f"  {lab[:40]:<40} expanded - summed = {d:+.4f}")
print(f"difference: mean {statistics.mean(diffs):+.4f}, spread (max - min) {max(diffs) - min(diffs):.4f}, "
      f"sd {statistics.stdev(diffs):.4f}")

print("\n== Q5. the valid-value filter: summed rows vs ___1 rows ==")
groups: dict[tuple[str, str], list[str]] = defaultdict(list)
for lab in labels:
    groups[group_of[lab]].append(lab)


def passes(values: dict[str, float]) -> bool:
    return any(sum(values[lab] > 0 for lab in members) >= 3 for members in groups.values())


pass_summed = [passes(s) for s in summed]
pass_m1 = [passes(pm[1]) for pm in per_m]
print("groups:", {f"{g} / PLpro {'mutant' if 'mutant' in t else 'WT'}": len(v) for (g, t), v in groups.items()})
print(f"pass on summed: {sum(pass_summed)} | pass on ___1: {sum(pass_m1)}")
print(f"pass on summed but not ___1: {sum(a and not b for a, b in zip(pass_summed, pass_m1))} | "
      f"pass on ___1 but not summed: {sum(b and not a for a, b in zip(pass_summed, pass_m1))}")
print("\ndone; nothing written")
