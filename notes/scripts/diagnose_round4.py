"""Round-4 descriptive, UNREGISTERED checks on PXD018299 (adversarial review, 2026-09-22).

Usage, from the repository root:  .venv/bin/python notes/scripts/diagnose_round4.py

NOT an independent path: the same instruments the registered run used, re-aggregated here. Nothing
below changes a registered verdict, a pre-registration or a committed fixture. Attempt 3 stands.

D — THE TWELVE-SAMPLE POPULATION.  The deposit holds four groups of three: KO, KO_IFN, WT, WT_IFN.
    Seven published claims have no measured value in the six IFN columns at all, so the paper's
    valid-value filter must have run across all twelve. This rebuilds the population that way,
    reruns the IFN contrast on it, and asks three things: which filter retains all 798 published
    claims; whether the seven then reach significance; and where the instability rate lands.
    Simulation in round 3 (part C) put the seven at 0 of 7 supported under our six-column
    population, against the paper publishing all seven as significant.

E — WHICH FDR CONVENTION RETURNS THE PUBLISHED COUNT?  Data Table S1 carries the authors' own
    post-imputation values for their 798 rows, measured and drawn. Using those values where they
    exist and our draws elsewhere, this asks which convention calls about 798 rows: `joint`
    (Perseus's documented q-value), `joint_half` (the convention attempt 2 fitted on the OTHER
    deposit), or `per_side`. It is the first evidence on `joint_half` that does not come from
    PXD026748. It is hybrid and approximate: the authors' draw is fixed for their rows only.
"""

import json
import math
import re

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

SEEDS = range(20)
CELL = {"downshift_sd": 1.8, "width_sd": 0.3, "scope": "per_sample"}
TEST = {"s0": 0.1, "alpha": 0.01, "randomisations": 250, "scheme": "random_excluding_trivial"}
SEVEN = ["124", "434", "562", "1070", "1140", "1233", "1903"]

deposit = maxquant.read_table(
    verify(PXD018299_SITES.expected_content_hash, filename=PXD018299_SITES.filename, home=HOME)
)
rows, column = anchor_population(deposit)
summed = [n for n in deposit.header if n.startswith("Intensity ") and "___" not in n and n != "Intensity"]
groups: dict[str, list[str]] = {"KO_IFN": [], "WT_IFN": [], "KO": [], "WT": []}
for name in summed:
    rest = name[len("Intensity "):]
    key = "KO_IFN" if rest.startswith("KO_IFN") else "WT_IFN" if rest.startswith("WT_IFN") else (
        "KO" if re.match(r"KO_\d", rest) else "WT" if re.match(r"WT_\d", rest) else None)
    if key:
        groups[key].append(name)
for key, names in groups.items():
    print(f"group {key:>7}: {names}")
order = groups["KO_IFN"] + groups["WT_IFN"] + groups["KO"] + groups["WT"]
assert len(order) == 12, f"expected twelve summed intensity columns, found {len(order)}"


def cell(row: list[str], name: str) -> float:
    raw = row[column[name]].strip() if name in column else ""
    try:
        value = float(raw)
    except ValueError:
        return math.nan
    return math.log2(value) if value > 0 else math.nan


full = np.array([[cell(r, name) for name in order] for r in rows])
ids = [str(r[column["id"]]).strip() for r in rows]
measured = ~np.isnan(full)
with open("tests/fixtures/pxd018299_published_cascade.json") as handle:
    cascade = json.load(handle)["rows"]
claim_ids = [str(c["deposit_id"]) for c in cascade]
claim_set = set(claim_ids)

print("\nD — the twelve-sample valid-value filter")
blocks = [slice(0, 3), slice(3, 6), slice(6, 9), slice(9, 12)]
chosen = None
for minimum in (3, 2, 1):
    keep = np.zeros(len(rows), dtype=bool)
    for block in blocks:
        keep |= measured[:, block].sum(1) >= minimum
    kept_claims = sum(1 for i, name in enumerate(ids) if keep[i] and name in claim_set)
    print(f"  at least {minimum} in one of the four groups: rows {int(keep.sum()):>5}, "
          f"published claims retained {kept_claims} of {len(claim_ids)}")
    if kept_claims == len(claim_ids) and chosen is None:
        chosen = (minimum, keep)
if chosen is None:
    raise SystemExit("  no twelve-sample rule retains every published claim — stopping")
minimum, keep = chosen
print(f"  taking 'at least {minimum} in one of the four groups'")

ifn = full[keep][:, :6]
kept_ids = [name for name, k in zip(ids, keep, strict=True) if k]
is_claim = np.array([name in claim_set for name in kept_ids])
seven_rows = np.array([name in SEVEN for name in kept_ids])
imputed_count = 6 - (~np.isnan(ifn)).sum(1)

for sidedness in ("joint_half", "joint"):
    support = []
    for seed in SEEDS:
        filled = downshifted_normal(ifn, seed=seed, **CELL).values
        out = perseus_s0(filled[:, :3], filled[:, 3:], seed=seed, sidedness=sidedness, **TEST)
        support.append(out.significant & (out.direction > 0))
    support = np.array(support)
    counts = support.sum(0)
    supported = (counts >= 10) & is_claim
    with_imputed = is_claim & (imputed_count > 0)
    unstable = with_imputed & (counts > 0) & (counts < 20)
    print(f"\n  [{sidedness}] rows {ifn.shape[0]}, claims {int(is_claim.sum())}")
    print(f"    supported claims (median draw): {int(supported.sum())} of {int(is_claim.sum())}")
    print(f"    unstable among claims with an imputed value: {int(unstable.sum())} of "
          f"{int(with_imputed.sum())} ({unstable.sum() / max(with_imputed.sum(), 1):.1%})")
    print(f"    the seven wholly drawn claims: supported {int((supported & seven_rows).sum())} of 7,"
          f" support counts {counts[seven_rows].tolist()}")
    for n in range(7):
        mask = is_claim & (imputed_count == n)
        if not mask.any():
            continue
        u = mask & (counts > 0) & (counts < 20)
        print(f"    imputed {n}: claims {int(mask.sum()):>4}  supported {int(((counts >= 10) & mask).sum()):>4}"
              f"  unstable {int(u.sum()):>4}")

print("\nE — which FDR convention returns the published count, on the authors' own values?")
header, s1 = _s1_rows(_supplement_path(SUPP_DATA_1, HOME))
published_columns = s1_columns(header)
row_of_id = {name: i for i, name in enumerate(kept_ids)}
authors = np.full(ifn.shape, np.nan)
placed = 0
for claim in cascade:
    i = row_of_id.get(str(claim["deposit_id"]))
    published = s1.get(int(claim["row"]))
    if i is None or published is None:
        continue
    values = [_float_cell(published.get(name)) for name in published_columns]
    if any(math.isnan(v) for v in values):
        continue
    authors[i] = values
    placed += 1
print(f"  authors' rows placed: {placed} of {len(claim_ids)}")
for sidedness in ("joint", "joint_half", "per_side"):
    calls, claim_calls = [], []
    for seed in SEEDS:
        filled = downshifted_normal(ifn, seed=seed, **CELL).values
        hybrid = np.where(np.isnan(authors), filled, authors)
        out = perseus_s0(hybrid[:, :3], hybrid[:, 3:], seed=seed, sidedness=sidedness, **TEST)
        hit = out.significant & (out.direction > 0)
        calls.append(int(hit.sum()))
        claim_calls.append(int((hit & is_claim).sum()))
    print(f"  {sidedness:>10}: calls over the whole matrix, median {int(np.median(calls))} "
          f"(range {min(calls)}-{max(calls)}); of the published claims, median {int(np.median(claim_calls))}"
          f" of {len(claim_ids)}  [the paper called 798]")
