"""Per-run quantification coverage of a MaxQuant proteinGroups.txt, by family.

Usage:  python3 coverage_shotgun.py path/to/proteinGroups.txt

Read-only. Run on 2026-09-19 over PXD026748's shotgun proteinGroups.txt
(sha256:b74a1797...f884); its output is quoted in
data/curation/curation_PXD026748_shotgun.json's RUN LAYOUT and QUANTITY
COVERAGE items.
"""

import sys

lines = open(sys.argv[1], encoding="utf-8", errors="replace").read().splitlines()
h = lines[0].split("\t")
rows = [line.split("\t") for line in lines[1:] if line]
ix = {c: i for i, c in enumerate(h)}
keep = [
    r
    for r in rows
    if r[ix["id"]].isdigit() and r[ix["Reverse"]] != "+" and r[ix["Potential contaminant"]] != "+"
]
runs = [c[len("LFQ intensity "):] for c in h if c.startswith("LFQ intensity ")]


def v(r, c):
    try:
        return float(r[ix[c]])
    except ValueError:
        return 0.0


print("groups after decoy/contaminant:", len(keep), "| runs:", len(runs))
print(f"{'run':<14}{'Intensity>0':>12}{'LFQ>0':>8}{'iBAQ>0':>8}{'Int>0,LFQ=0':>13}")
for r in runs:
    i = sum(v(x, "Intensity " + r) > 0 for x in keep)
    lfq = sum(v(x, "LFQ intensity " + r) > 0 for x in keep)
    b = sum(v(x, "iBAQ " + r) > 0 for x in keep)
    gap = sum(v(x, "Intensity " + r) > 0 and v(x, "LFQ intensity " + r) <= 0 for x in keep)
    lab = r[:2] + " " + r.split("shotgun-")[-1]
    print(f"{lab[:13]:<14}{i:>12}{lfq:>8}{b:>8}{gap:>13}")
any_i = sum(any(v(x, "Intensity " + r) > 0 for r in runs) for x in keep)
any_l = sum(any(v(x, "LFQ intensity " + r) > 0 for r in runs) for x in keep)
print("groups with Intensity>0 in any run:", any_i, "| LFQ>0 in any run:", any_l)
