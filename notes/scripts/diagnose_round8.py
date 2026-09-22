"""Round-8 descriptive, UNREGISTERED checks (adversarial review, 2026-09-22).

Usage, from the repository root:  .venv/bin/python notes/scripts/diagnose_round8.py

Not an independent path: the same instruments the registered runs use. Nothing registered changes.

The review made three points that this measures:

F — EVERY DERIVED FIGURE MOVES WITH THE LEVEL. The class-conditional table (112 of 112 unstable at
    4 imputed, 46 of 598 at 3) was computed under the superseded halved rule. The documented rule
    is stricter, so the boundary moves down into the 3-imputed class. Recomputed here, with the
    supported counts.

G — SCORE MEMBERSHIP, NOT COUNTS. "781 against 798" and "278 against 282" are one-number matches.
    The published lists are hundreds of constraints. This reports precision and recall against the
    published membership on both deposits.

H — RECONSTRUCT MUNNUR'S INPUTS, NOT PERSEUS'S RULE. With the documented rule validated on the
    anchor, the parsimonious reading of the other deposit's factor of two is that our reconstruction
    of ITS inputs is wrong. This grids the things we inferred rather than read — the valid-value
    filter, the normalisation, the population — and scores each on membership under the documented
    rule. If a cell reaches Table 3's list, nothing anomalous remains.

Note on what is NOT here: running Perseus itself. It is a Windows desktop application and this
environment is Linux without a VM. It is the direct test and it is out of reach here.
"""

import json
import math

import numpy as np

from bzk.adapters import maxquant
from bzk.provenance.raw_store import verify
from bzk.sources.pxd018299_h10 import (
    GATE_ALPHA,
    GATE_S0,
    HOME,
    PXD018299_SITES,
    SHOTGUN_CURATION,
    SUPP_TABLE_1,
    _deposit_for,
    _gate_inputs,
    _parse_arm,
    _supplement_path,
    anchor_population,
)
from bzk.stats.imputation import downshifted_normal
from bzk.stats.perseus_s0 import perseus_s0

SEEDS = range(20)
R = 250
DEFAULT = {"downshift_sd": 1.8, "width_sd": 0.3, "scope": "per_sample"}
KO = ["Intensity KO_IFN_1", "Intensity KO_IFN_2", "Intensity KO_IFN_3"]
WT = ["Intensity WT_IFN_1", "Intensity WT_IFN_2", "Intensity WT_IFN_3"]


def membership(called: np.ndarray, published: np.ndarray) -> tuple[float, float]:
    hits = int((called & published).sum())
    return hits / max(int(called.sum()), 1), hits / max(int(published.sum()), 1)


# ---- the anchor ---------------------------------------------------------------------------------
rows, column = anchor_population(
    maxquant.read_table(verify(PXD018299_SITES.expected_content_hash,
                               filename=PXD018299_SITES.filename, home=HOME))
)


def anchor_cell(row: list[str], name: str) -> float:
    raw = row[column[name]].strip() if name in column else ""
    try:
        value = float(raw)
    except ValueError:
        return math.nan
    return math.log2(value) if value > 0 else math.nan


matrix = np.array([[anchor_cell(r, n) for n in KO + WT] for r in rows])
ids = [str(r[column["id"]]).strip() for r in rows]
measured = ~np.isnan(matrix)
keep = (measured[:, :3].sum(1) >= 1) | (measured[:, 3:].sum(1) >= 1)
kept, kept_measured = matrix[keep], measured[keep]
kept_ids = [i for i, k in zip(ids, keep, strict=True) if k]
with open("tests/fixtures/pxd018299_published_cascade.json") as handle:
    claim_ids = {str(c["deposit_id"]) for c in json.load(handle)["rows"]}
is_claim = np.array([i in claim_ids for i in kept_ids])
imputed_count = 6 - kept_measured.sum(1)

print("F and G — the anchor under each rule (registered population, default cell, 20 draws)")
for sidedness in ("joint", "joint_half"):
    support = []
    for seed in SEEDS:
        filled = downshifted_normal(kept, seed=seed, **DEFAULT).values
        out = perseus_s0(filled[:, :3], filled[:, 3:], s0=0.1, alpha=0.01, randomisations=R,
                         seed=seed, sidedness=sidedness, scheme="random_excluding_trivial")
        support.append(out.significant & (out.direction > 0))
    support = np.array(support)
    counts = support.sum(0)
    called = counts >= len(SEEDS) / 2
    precision, recall = membership(called, is_claim)
    with_imputed = is_claim & (imputed_count > 0)
    unstable = with_imputed & (counts > 0) & (counts < len(SEEDS))
    print(f"\n  [{sidedness}] calls {int(called.sum())} (the paper called 798); "
          f"membership against the published list: precision {precision:.3f}, recall {recall:.3f}")
    print(f"    claims supported {int((called & is_claim).sum())} of {int(is_claim.sum())}; "
          f"unstable {int(unstable.sum())} of {int(with_imputed.sum())} "
          f"({unstable.sum() / max(with_imputed.sum(), 1):.1%})")
    print(f"    {'imputed':>8} {'claims':>7} {'supported':>10} {'unstable':>9} {'median q':>10}")
    for n in range(7):
        mask = is_claim & (imputed_count == n)
        if not mask.any():
            continue
        u = mask & (counts > 0) & (counts < len(SEEDS))
        print(f"    {n:>8} {int(mask.sum()):>7} {int((called & mask).sum()):>10} {int(u.sum()):>9}")

# ---- Munnur's inputs ----------------------------------------------------------------------------
print("\nH — a grid over what we inferred about the other deposit's inputs, documented rule")
curation, _, _ = _parse_arm(SHOTGUN_CURATION, HOME)
shotgun, wt, ko, complete, accessions, calls, _ = _gate_inputs(
    curation, _deposit_for(curation, HOME), _supplement_path(SUPP_TABLE_1, HOME)
)
target = np.array([a in calls for a in accessions])
present = ~np.isnan(shotgun)
print(f"  base matrix {shotgun.shape[0]} proteins, Table 3 calls {int(target.sum())}")
print(f"  {'filter':>22} {'normalisation':>14} {'rows':>6} {'calls':>7} {'precision':>10} {'recall':>8}")
for filter_label, mask in (
    ("at least 1 in a group", (present[:, wt].sum(1) >= 1) | (present[:, ko].sum(1) >= 1)),
    ("at least 2 in a group", (present[:, wt].sum(1) >= 2) | (present[:, ko].sum(1) >= 2)),
    ("at least 3 in a group", (present[:, wt].sum(1) >= 3) | (present[:, ko].sum(1) >= 3)),
    ("at least 3 in both", (present[:, wt].sum(1) >= 3) & (present[:, ko].sum(1) >= 3)),
    ("complete rows only", present.all(1)),
):
    for norm_label, normalise in (("none", False), ("median-subtracted", True)):
        block = shotgun[mask]
        published_here = target[mask]
        if normalise:
            block = block - np.nanmedian(block, axis=0)
        called_counts = np.zeros(block.shape[0])
        for seed in SEEDS:
            filled = downshifted_normal(block, seed=seed, **DEFAULT).values
            out = perseus_s0(filled[:, wt], filled[:, ko], s0=GATE_S0, alpha=GATE_ALPHA,
                             randomisations=R, seed=seed, sidedness="joint",
                             scheme="random_excluding_trivial")
            called_counts += out.significant.astype(float)
        called = called_counts >= len(SEEDS) / 2
        precision, recall = membership(called, published_here)
        print(f"  {filter_label:>22} {norm_label:>14} {block.shape[0]:>6} {int(called.sum()):>7} "
              f"{precision:>10.3f} {recall:>8.3f}")
print("  A cell reaching Table 3's list under the documented rule would dissolve the factor of two.")
print("  π0 note: the estimator used throughout is Storey's 2 * mean(p > 0.5) on Student t p-values;")
print("  with most rows moving, π0 estimates are unstable and estimator-dependent.")
