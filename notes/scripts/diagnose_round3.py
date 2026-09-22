"""Round-3 descriptive, UNREGISTERED follow-ups on PXD018299 (adversarial review, 2026-09-22).

Usage, from the repository root:  .venv/bin/python notes/scripts/diagnose_round3.py

NOT an independent path: this uses the same instruments the run used (`anchor_population`,
`downshifted_normal`, `perseus_s0`), re-aggregated by a separate script. A fault in those modules
would reproduce here.

A — WHICH drawn value moves a claim?  The 4-imputed class (WT arm drawn, one KO value missing) is
    where every unstable claim sits. Three candidates: the drawn KO value through the difference;
    the same value through the within-group spread (the statistic is d/(s + s0)); or the three drawn
    WT values through their mean. Per claim and per draw, this reports which of them tracks support.
    It also asks what the 46 unstable claims in the 3-imputed class share.

B — ARE THE KNOCKOUT COLUMNS SELECTED?  The authors' drawn KO values are visible only in rows S1
    published, i.e. significant ones, and a higher drawn KO value raises significance twice over
    (larger difference, smaller spread). Simulating a draw at the recovered WT parameters
    (downshift 1.77, width 0.29) and recovering the downshift from significant rows only says
    whether selection alone reproduces the observed 1.39-1.51.

C — THE SEVEN WHOLLY DRAWN CLAIMS.  With both arms drawn from the deposit's column statistics, do
    they clear the threshold? This replaces the extrapolation in
    `walk/CHECKS-PXD018299-imputation-effects.md`.
"""

import json
import math

import numpy as np
from bzk.adapters import maxquant
from bzk.provenance.raw_store import verify
from bzk.sources.pxd018299_h10 import (
    HOME,
    PXD018299_SITES,
    anchor_population,
)
from bzk.stats.imputation import downshifted_normal
from bzk.stats.perseus_s0 import perseus_s0

KO = ["Intensity KO_IFN_1", "Intensity KO_IFN_2", "Intensity KO_IFN_3"]
WT = ["Intensity WT_IFN_1", "Intensity WT_IFN_2", "Intensity WT_IFN_3"]
SEEDS = range(20)
CELL = {"downshift_sd": 1.8, "width_sd": 0.3, "scope": "per_sample"}
TEST = {"s0": 0.1, "alpha": 0.01, "randomisations": 250, "sidedness": "joint_half",
        "scheme": "random_excluding_trivial"}

deposit = maxquant.read_table(
    verify(PXD018299_SITES.expected_content_hash, filename=PXD018299_SITES.filename, home=HOME)
)
rows, column = anchor_population(deposit)


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
keep = (measured[:, :3].sum(1) >= 1) | (measured[:, 3:].sum(1) >= 1)
kept, kept_measured = matrix[keep], measured[keep]
kept_ids = [i for i, k in zip(ids, keep, strict=True) if k]
with open("tests/fixtures/pxd018299_published_cascade.json") as handle:
    claim_ids = {str(c["deposit_id"]) for c in json.load(handle)["rows"]}
is_claim = np.array([i in claim_ids for i in kept_ids])
imputed_count = 6 - kept_measured.sum(1)

support, ko_drawn_z, wt_drawn_mean_z, spread = [], [], [], []
column_mean = np.nanmean(kept, axis=0)
column_sd = np.nanstd(kept, axis=0, ddof=1)
for seed in SEEDS:
    filled = downshifted_normal(kept, seed=seed, **CELL).values
    outcome = perseus_s0(filled[:, :3], filled[:, 3:], seed=seed, **TEST)
    support.append(outcome.significant & (outcome.direction > 0))
    drawn_ko = np.where(~kept_measured[:, :3], (filled[:, :3] - column_mean[:3]) / column_sd[:3], np.nan)
    drawn_wt = np.where(~kept_measured[:, 3:], (filled[:, 3:] - column_mean[3:]) / column_sd[3:], np.nan)
    ko_drawn_z.append(np.nanmean(drawn_ko, axis=1))
    wt_drawn_mean_z.append(np.nanmean(drawn_wt, axis=1))
    spread.append(filled[:, :3].std(axis=1, ddof=1))
support = np.array(support)
ko_drawn_z, wt_drawn_mean_z, spread = np.array(ko_drawn_z), np.array(wt_drawn_mean_z), np.array(spread)

print("A — within the 4-imputed class, what tracks support across draws?")
four = np.where(is_claim & (imputed_count == 4))[0]
for name, quantity in (("drawn KO value (z)", ko_drawn_z), ("drawn WT mean (z)", wt_drawn_mean_z),
                       ("KO within-group spread", spread)):
    per_claim = []
    for i in four:
        s, q = support[:, i].astype(float), quantity[:, i]
        if s.std() == 0 or np.isnan(q).any() or np.std(q) == 0:
            continue
        per_claim.append(np.corrcoef(s, q)[0, 1])
    per_claim = np.array(per_claim)
    print(f"  {name:>24}: mean within-claim correlation with support {per_claim.mean():+.3f}"
          f"  (claims usable {len(per_claim)}; share positive {np.mean(per_claim > 0):.0%})")

print("\nA2 — the 46 unstable claims in the 3-imputed class, against the stable 552")
three = is_claim & (imputed_count == 3)
counts = support.sum(0)
unstable = three & (counts > 0) & (counts < 20)
stable = three & ~unstable
for name, mask in (("unstable", unstable), ("stable", stable)):
    ko = np.nanmean(kept[mask][:, :3], axis=1)
    print(f"  {name:>8}: n {int(mask.sum()):>3}, measured KO mean {ko.mean():.2f} (sd {ko.std():.2f}),"
          f" KO column mean {column_mean[:3].mean():.2f}")

print("\nB — do the knockout columns look low because only significant rows are visible?")
rng = np.random.default_rng(0)
sim = kept.copy()
for j in range(6):
    missing = np.isnan(sim[:, j])
    sim[missing, j] = rng.normal(column_mean[j] - 1.77 * column_sd[j], 0.29 * column_sd[j], int(missing.sum()))
outcome = perseus_s0(sim[:, :3], sim[:, 3:], seed=0, **TEST)
significant = outcome.significant & (outcome.direction > 0)
print(f"  simulated at downshift 1.77, width 0.29; significant rows: {int(significant.sum())}")
for j, name in enumerate(KO + WT):
    drawn = np.isnan(kept[:, j])
    for label, mask in (("all drawn", drawn), ("drawn in significant rows", drawn & significant)):
        values = sim[mask, j]
        if values.size < 5:
            continue
        down = (column_mean[j] - values.mean()) / column_sd[j]
        width = values.std(ddof=1) / column_sd[j]
        print(f"  {name:>22} {label:>26}: n {values.size:>5}  down {down:>5.2f}  width {width:>4.2f}")

print("\nC — the seven wholly drawn claims, simulated at the recovered parameters")
seven = np.array([[math.nan] * 6] * 7)
block = np.vstack([kept, seven])
hits = []
for seed in SEEDS:
    filled = downshifted_normal(block, seed=seed, **CELL).values
    out = perseus_s0(filled[:, :3], filled[:, 3:], seed=seed, **TEST)
    hit = out.significant & (out.direction > 0)
    hits.append(hit[-7:])
hits = np.array(hits)
print(f"  supported in a median draw: {int((hits.mean(0) >= 0.5).sum())} of 7;"
      f"  per-claim support counts over 20 draws: {hits.sum(0).tolist()}")
print("  (added to the matrix only for this check; it is not the registered population)")
