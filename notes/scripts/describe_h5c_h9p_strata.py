"""Descriptive, UNREGISTERED stratified checks for H5c and H9p on PXD026748.

Usage, from the repository root:  .venv/bin/python notes/scripts/describe_h5c_h9p_strata.py

Reads only tests/fixtures/pxd026748_h5c_h9p.json. It was written after both verdicts were
recorded, at an adversarial reviewer's request, and it cannot change either verdict. It asks two
questions the registered readouts did not:
  1. Does H5c's corroboration gap survive stratification by missing values (its declared confound)?
  2. At equal missingness, are protein claims less or more imputation-dependent than site claims?
"""

import json

f = json.load(open("tests/fixtures/pxd026748_h5c_h9p.json"))

print("H5c — durable share, flagged minus unflagged, within missingness strata (clusters 1a, 1b, 2)")
claims = [c for c in f["h5c"]["claims"] if c["cluster"] != "Cluster 3"]


def h5c_band(m: int) -> str:
    return "0-5" if m <= 5 else ("6-8" if m <= 8 else "9")


weighted, total = 0.0, 0
for band in ("0-5", "6-8", "9"):
    group = [c for c in claims if h5c_band(c["missing_values"]) == band]
    flagged = [c for c in group if c["flagged"]]
    unflagged = [c for c in group if not c["flagged"]]
    share_f = sum(c["category"] == "durable" for c in flagged) / len(flagged)
    share_u = sum(c["category"] == "durable" for c in unflagged) / len(unflagged)
    difference = share_f - share_u
    weighted += difference * len(group)
    total += len(group)
    print(f"  {band:>4} missing: flagged {len(flagged)}, unflagged {len(unflagged)}, difference {difference:+.3f}")
print(f"  weighted by stratum size: {weighted / total:+.3f}")

print("H9p — underdetermined share within missingness strata, proteins against sites")


def h9p_band(m: int) -> str:
    if m == 0:
        return "0"
    return "1-2" if m <= 2 else ("3-5" if m <= 5 else ("6-8" if m <= 8 else "9+"))


for band in ("1-2", "3-5", "6-8", "9+"):
    rows = []
    for name, items in (("proteins", f["h9p"]["proteins"]), ("sites", f["h9p"]["sites"])):
        group = [r for r in items if h9p_band(r["missing_values"]) == band]
        under = sum(r["category"] == "underdetermined" for r in group)
        rows.append(f"{name} {under} of {len(group)} ({under / len(group):.0%})")
    print(f"  {band:>4} missing: " + " | ".join(rows))
