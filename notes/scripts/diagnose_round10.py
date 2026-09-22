"""Round-10 descriptive, UNREGISTERED checks (adversarial review, 2026-09-22).

Usage, from the repository root:  .venv/bin/python notes/scripts/diagnose_round10.py

Not an independent path: the same instruments the registered runs use. Nothing registered changes.

M — IS THE F1 CEILING AN ARTEFACT OF THE AGGREGATION? The published list is ONE realisation; round
    9 scored a majority over 20 draws against it. For the 112 claims whose support the draw decides,
    a majority rule cannot include what a single realisation can. F1 is recomputed PER SEED.

N — THE s0 AXIS. Round 9 scanned one dimension (the scale on the null count) at s0 = 0.1. s0 does
    not slide the cut, it rotates the ranking, trading fold change against variance, so other s0
    values give selections nested in nothing already scanned. The ceiling is recomputed over the
    plane.

O — THE PRECISION SIDE, PARTITIONED. Round 9 partitioned the misses (6 supported in no draw:
    structural; 112 in 1-9 draws: the phenomenon). The same split is owed on the other side: of the
    claims called but not published, how many are supported in ALL draws?

P — THE FLOOR OVER THE WHOLE FAMILY, not over two points, and stated with the direction of its
    other bias: instability is monotone in the number of draws, so 20 draws undercounts.

Q — RANK MOVEMENT, which needs no rule, no s0 and no population argument. The log q measure failed
    on a clipping floor meeting zero q values; rank is immune.
"""

import json
import math

import numpy as np

from bzk.adapters import maxquant
from bzk.provenance.raw_store import verify
from bzk.sources.pxd018299_h10 import HOME, PXD018299_SITES, anchor_population
from bzk.stats.imputation import downshifted_normal
from bzk.stats.perseus_s0 import _relabellings, _statistic

SEEDS = range(20)
R = 250
ALPHA = 0.01
DEFAULT = {"downshift_sd": 1.8, "width_sd": 0.3, "scope": "per_sample"}
KO = ["Intensity KO_IFN_1", "Intensity KO_IFN_2", "Intensity KO_IFN_3"]
WT = ["Intensity WT_IFN_1", "Intensity WT_IFN_2", "Intensity WT_IFN_3"]
SCALES = (0.25, 0.4, 0.5, 0.6, 0.75, 1.0, 1.5, 2.0)
S0S = (0.0, 0.05, 0.1, 0.2, 0.5, 1.0)

rows, column = anchor_population(
    maxquant.read_table(verify(PXD018299_SITES.expected_content_hash,
                               filename=PXD018299_SITES.filename, home=HOME))
)


def cell(row: list[str], name: str) -> float:
    raw = row[column[name]].strip() if name in column else ""
    try:
        value = float(raw)
    except ValueError:
        return math.nan
    return math.log2(value) if value > 0 else math.nan


matrix = np.array([[cell(r, n) for n in KO + WT] for r in rows])
ids = [str(r[column["id"]]).strip() for r in rows]
measured = ~np.isnan(matrix)
keep = (measured[:, :3].sum(1) >= 1) | (measured[:, 3:].sum(1) >= 1)
kept, kept_measured = matrix[keep], measured[keep]
kept_ids = [i for i, k in zip(ids, keep, strict=True) if k]
with open("tests/fixtures/pxd018299_published_cascade.json") as handle:
    claim_ids = {str(c["deposit_id"]) for c in json.load(handle)["rows"]}
published = np.array([i in claim_ids for i in kept_ids])
imputed_count = 6 - kept_measured.sum(1)
blocks = [downshifted_normal(kept, seed=seed, **DEFAULT).values for seed in SEEDS]
print(f"rows {kept.shape[0]}, published claims {int(published.sum())}, draws {len(blocks)}")


def q_and_statistic(block: np.ndarray, seed: int, s0: float) -> tuple[np.ndarray, np.ndarray]:
    observed = _statistic(block[:, :3], block[:, 3:], s0)
    finite = np.isfinite(observed)
    magnitude = np.abs(observed[finite])
    thresholds = np.sort(magnitude)
    counts = []
    for assignment in _relabellings(3, 3, scheme="random_excluding_trivial",
                                    randomisations=R, seed=seed)[0]:
        mask = np.zeros(6, dtype=bool)
        mask[np.asarray(assignment[:3])] = True
        null = np.abs(_statistic(block[:, mask], block[:, ~mask], s0))[finite]
        null = np.sort(null[np.isfinite(null)])
        counts.append(null.size - np.searchsorted(null, thresholds, side="left"))
    null_count = np.array(counts, dtype=float).mean(axis=0)
    observed_count = magnitude.size - np.searchsorted(thresholds, thresholds, side="left")
    base = np.full(observed.shape, np.inf)
    base[finite] = np.minimum.accumulate(null_count / np.maximum(observed_count, 1))[
        np.searchsorted(thresholds, magnitude, side="right") - 1
    ]
    return base, observed


def f1(called: np.ndarray) -> tuple[float, float, float]:
    hits = int((called & published).sum())
    precision = hits / max(int(called.sum()), 1)
    recall = hits / int(published.sum())
    return precision, recall, (0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall))


by_s0 = {s0: [q_and_statistic(block, seed, s0) for block, seed in zip(blocks, SEEDS, strict=True)]
         for s0 in S0S}

print("\nM — F1 per single draw against the published list, at s0 = 0.1")
for scale in (0.5, 1.0):
    per_seed = []
    for q, observed in by_s0[0.1]:
        per_seed.append(f1((q * scale <= ALPHA) & (observed > 0))[2])
    majority = np.array([(q * scale <= ALPHA) & (observed > 0) for q, observed in by_s0[0.1]])
    label = "documented" if scale == 1.0 else "halved"
    print(f"  {label:>11}: per-seed F1 mean {np.mean(per_seed):.3f}, range {min(per_seed):.3f}-{max(per_seed):.3f}"
          f"  |  majority-over-20 F1 {f1(majority.sum(0) >= len(SEEDS) / 2)[2]:.3f}")

print("\nN — the ceiling over the (s0, scale) plane, per-seed mean F1")
print(f"  {'s0':>6} " + " ".join(f"{scale:>6}" for scale in SCALES))
best = None
for s0 in S0S:
    line = f"  {s0:>6} "
    for scale in SCALES:
        values = [f1((q * scale <= ALPHA) & (observed > 0))[2] for q, observed in by_s0[s0]]
        mean = float(np.mean(values))
        line += f" {mean:>6.3f}"
        if best is None or mean > best[2]:
            best = (s0, scale, mean)
    print(line)
print(f"  ceiling over the plane: F1 {best[2]:.3f} at s0 {best[0]}, scale {best[1]}"
      f"  (the paper states s0 = 0.1)")

print("\nO — the precision side, partitioned (documented rule, s0 = 0.1)")
support = np.array([(q <= ALPHA) & (observed > 0) for q, observed in by_s0[0.1]])
counts = support.sum(0)
called = counts >= len(SEEDS) / 2
extra = called & ~published
missed = published & ~called
print(f"  called but not published: {int(extra.sum())}")
print(f"    supported in all {len(SEEDS)} draws (structural): {int((extra & (counts == len(SEEDS))).sum())}")
print(f"    supported in {len(SEEDS) // 2}-{len(SEEDS) - 1} draws (the phenomenon): "
      f"{int((extra & (counts >= len(SEEDS) / 2) & (counts < len(SEEDS))).sum())}")
print(f"  published but not called: {int(missed.sum())}")
print(f"    supported in no draw (structural): {int((missed & (counts == 0)).sum())}")
print(f"    supported in 1-{len(SEEDS) // 2 - 1} draws (the phenomenon): "
      f"{int((missed & (counts >= 1) & (counts < len(SEEDS) / 2)).sum())}")
structural = int((extra & (counts == len(SEEDS))).sum()) + int((missed & (counts == 0)).sum())
print(f"  structural discordance: {structural} of {int(published.sum())} ({structural / published.sum():.1%})")

print("\nP — the floor over the whole scale family, not two points (s0 = 0.1)")
with_imputed = published & (imputed_count > 0)
floor = np.ones(kept.shape[0], dtype=bool)
for scale in SCALES:
    c = np.array([(q * scale <= ALPHA) & (observed > 0) for q, observed in by_s0[0.1]]).sum(0)
    floor &= (c > 0) & (c < len(SEEDS))
for scale in (0.5, 1.0):
    c = np.array([(q * scale <= ALPHA) & (observed > 0) for q, observed in by_s0[0.1]]).sum(0)
    unstable = with_imputed & (c > 0) & (c < len(SEEDS))
    print(f"  unstable at scale {scale}: {int(unstable.sum())} ({unstable.sum() / with_imputed.sum():.1%})")
across = with_imputed & floor
print(f"  unstable across ALL scales {SCALES}: {int(across.sum())} ({across.sum() / with_imputed.sum():.1%})")
print("  Direction of the other bias: instability is monotone in the draw count, so 20 draws")
print("  understates it. This is a floor across FDR scalings AND an underestimate in draws.")

print("\nQ — rank movement, which needs no rule, no s0 threshold and no population argument")
ranks = np.array([np.argsort(np.argsort(-np.abs(observed))) for _, observed in by_s0[0.1]])
spread = ranks.max(0) - ranks.min(0)
print(f"  rank spread across draws, claims with an imputed value: median {int(np.median(spread[with_imputed]))}, "
      f"90th {int(np.percentile(spread[with_imputed], 90))} (of {kept.shape[0]} rows)")
cut = int(np.median([int(((q <= ALPHA) & (observed > 0)).sum()) for q, observed in by_s0[0.1]]))
crosses = with_imputed & (ranks.min(0) < cut) & (ranks.max(0) >= cut)
print(f"  rank range crosses the median call boundary (rank {cut}): {int(crosses.sum())} of "
      f"{int(with_imputed.sum())} ({crosses.sum() / with_imputed.sum():.1%})")
