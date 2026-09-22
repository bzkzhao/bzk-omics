"""Round-11 descriptive, UNREGISTERED checks (adversarial review, 2026-09-22).

Usage, from the repository root:  .venv/bin/python notes/scripts/diagnose_round11.py

Not an independent path: the same instruments the registered runs use. Nothing registered changes.

R — READ THE NINE. Structural discordance was counted (3 called-not-published, 6 published-not-
    called) and never inspected. n = 9 is small enough to read: their identity may name the
    upstream difference.
S — THE DRAW COUNT MOVES BOTH HEADLINES, IN OPPOSITE DIRECTIONS. Instability rises with draws;
    "structural" (defined by unanimity across draws) falls. Both are reported at 20, 50 and 100.
T — INTERVALS ON THE STRUCTURAL COUNTS. "Supported in no draw" is not a property of a claim: at 20
    draws it is consistent with a true support probability up to about 14%. Clopper-Pearson bounds.
U — RANK, HONESTLY. The crossing share inherits the rule through its reference point, and the ranks
    were computed over |statistic| while the cut counted only positive-direction calls. Both fixed:
    the unconditional rank-spread distribution (rule-free), and crossing as a CURVE over cut
    position, with the documented rule's rate marked as one point on it.
V — THE UNIT. The paper counts GlyGly PEPTIDES (798 of 2,341). Our matrix is site-keyed on the
    summed columns. The per-multiplicity (`___1`) table is an untested axis, and on the other
    deposit that same axis reproduced its stated count exactly.
W — THE POPULATION, SEARCHED RATHER THAN FITTED. Every scan so far moved the threshold and held the
    population at a rule chosen to retain the published set. This scans the population instead.
X — THE DEPOSIT'S OWN METADATA. A Perseus session file or a processed matrix would settle the
    threshold and the population without a Windows machine. This lists what the raw store holds.
"""

import json
import math

import numpy as np
from bzk.adapters import maxquant
from bzk.provenance.raw_store import verify
from bzk.sources.pxd018299_h10 import HOME, PXD018299_SITES, anchor_population
from bzk.stats.imputation import downshifted_normal
from bzk.stats.perseus_s0 import _relabellings, _statistic
from scipy import stats

R_PERM = 250
ALPHA, S0 = 0.01, 0.1
DEFAULT = {"downshift_sd": 1.8, "width_sd": 0.3, "scope": "per_sample"}
KO = ["Intensity KO_IFN_1", "Intensity KO_IFN_2", "Intensity KO_IFN_3"]
WT = ["Intensity WT_IFN_1", "Intensity WT_IFN_2", "Intensity WT_IFN_3"]
KO1 = [f"{n}___1" for n in KO]
WT1 = [f"{n}___1" for n in WT]

table = maxquant.read_table(
    verify(PXD018299_SITES.expected_content_hash, filename=PXD018299_SITES.filename, home=HOME)
)
rows, column = anchor_population(table)


def cell(row: list[str], name: str) -> float:
    raw = row[column[name]].strip() if name in column else ""
    try:
        value = float(raw)
    except ValueError:
        return math.nan
    return math.log2(value) if value > 0 else math.nan


def build(names: list[str]) -> tuple[np.ndarray, np.ndarray]:
    block = np.array([[cell(r, n) for n in names] for r in rows])
    return block, ~np.isnan(block)


matrix, measured = build(KO + WT)
ids = [str(r[column["id"]]).strip() for r in rows]
with open("tests/fixtures/pxd018299_published_cascade.json") as handle:
    cascade = json.load(handle)["rows"]
claim_ids = {str(c["deposit_id"]) for c in cascade}
claim_row = {str(c["deposit_id"]): c for c in cascade}


def q_of(block: np.ndarray, seed: int) -> tuple[np.ndarray, np.ndarray]:
    observed = _statistic(block[:, :3], block[:, 3:], S0)
    finite = np.isfinite(observed)
    magnitude = np.abs(observed[finite])
    thresholds = np.sort(magnitude)
    counts = []
    for assignment in _relabellings(3, 3, scheme="random_excluding_trivial",
                                    randomisations=R_PERM, seed=seed)[0]:
        mask = np.zeros(6, dtype=bool)
        mask[np.asarray(assignment[:3])] = True
        null = np.abs(_statistic(block[:, mask], block[:, ~mask], S0))[finite]
        null = np.sort(null[np.isfinite(null)])
        counts.append(null.size - np.searchsorted(null, thresholds, side="left"))
    null_count = np.array(counts, dtype=float).mean(axis=0)
    observed_count = magnitude.size - np.searchsorted(thresholds, thresholds, side="left")
    q = np.full(observed.shape, np.inf)
    q[finite] = np.minimum.accumulate(null_count / np.maximum(observed_count, 1))[
        np.searchsorted(thresholds, magnitude, side="right") - 1
    ]
    return q, observed


def run(block: np.ndarray, keep: np.ndarray, draws: int) -> tuple[np.ndarray, np.ndarray]:
    support, statistics = [], []
    for seed in range(draws):
        filled = downshifted_normal(block[keep], seed=seed, **DEFAULT).values
        q, observed = q_of(filled, seed)
        support.append((q <= ALPHA) & (observed > 0))
        statistics.append(observed)
    return np.array(support), np.array(statistics)


keep = (measured[:, :3].sum(1) >= 1) | (measured[:, 3:].sum(1) >= 1)
kept_ids = [i for i, k in zip(ids, keep, strict=True) if k]
published = np.array([i in claim_ids for i in kept_ids])
imputed_count = 6 - measured[keep].sum(1)

print("S and T — both headlines as functions of the draw count")
print(f"  {'draws':>6} {'unstable':>20} {'structural, missed':>20} {'structural, extra':>19}")
support_by_draws = {}
for draws in (20, 50, 100):
    support, _ = run(matrix, keep, draws)
    support_by_draws[draws] = support
    counts = support.sum(0)
    called = counts >= draws / 2
    with_imputed = published & (imputed_count > 0)
    unstable = with_imputed & (counts > 0) & (counts < draws)
    missed_structural = published & ~called & (counts == 0)
    extra_structural = called & ~published & (counts == draws)
    print(f"  {draws:>6} {unstable.sum() / with_imputed.sum():>19.1%} "
          f"{int(missed_structural.sum()):>20} {int(extra_structural.sum()):>19}")

support = support_by_draws[20]
counts = support.sum(0)
called = counts >= 10
missed_structural = published & ~called & (counts == 0)
extra_structural = called & ~published & (counts == 20)
for label, n in (("no support in 20 draws", int(missed_structural.sum())),
                 ("support in all 20 draws", int(extra_structural.sum()))):
    if label.startswith("no"):
        # Clopper-Pearson: 0 successes in 20 draws bounds the per-claim support probability above.
        print(f"  {n} claims with '{label}': each consistent with a support probability up to "
              f"{stats.beta.ppf(0.975, 1, 20):.1%}")
    else:
        print(f"  {n} claims with '{label}': each consistent with a support probability down to "
              f"{stats.beta.ppf(0.05, 20, 1):.1%}")

print("\nR — the nine, read rather than counted")
for label, mask in (("published, never supported", missed_structural),
                    ("called in every draw, not published", extra_structural)):
    print(f"  {label}:")
    for position in np.where(mask)[0]:
        deposit_id = kept_ids[position]
        claim = claim_row.get(deposit_id, {})
        row = rows[ids.index(deposit_id)]
        fields = {name: row[column[name]] for name in
                  ("Localization prob", "Score", "Reverse", "Potential contaminant")
                  if name in column}
        multiplicity = [n for n in (KO1 + WT1) if n in column and row[column[n]].strip() not in ("", "0")]
        print(f"    id {deposit_id:>6}  imputed {int(imputed_count[position])}/6  "
              f"published row {claim.get('row', '?')}  loc {fields.get('Localization prob', '?')}  "
              f"score {fields.get('Score', '?')}  rev {fields.get('Reverse', '')!r}  "
              f"con {fields.get('Potential contaminant', '')!r}  ___1 columns with values: {len(multiplicity)}")

print("\nU — rank, without the rule in the reference point")
_, statistics = run(matrix, keep, 20)
positive = statistics > 0
ranks = np.array([np.argsort(np.argsort(-np.where(p, s, -np.inf))) for s, p in zip(statistics, positive, strict=True)])
with_imputed = published & (imputed_count > 0)
spread = ranks.max(0) - ranks.min(0)
quartiles = np.percentile(spread[with_imputed], [25, 50, 75])
print(f"  rank spread (positive-direction ranking), claims with an imputed value: "
      f"quartiles {int(quartiles[0])} / {int(quartiles[1])} / {int(quartiles[2])} of {int(keep.sum())} rows")
print("  crossing share as a curve over the cut position:")
documented = int(np.median(support.sum(1)))
for cut in (200, 400, 600, documented, 800, 1000, 1400):
    crosses = with_imputed & (ranks.min(0) < cut) & (ranks.max(0) >= cut)
    mark = "  <- the documented rule's calling rate" if cut == documented else ""
    print(f"    cut at rank {cut:>5}: {crosses.sum() / with_imputed.sum():>6.1%}{mark}")

print("\nV — the unit: the per-multiplicity (___1) columns instead of the summed ones")
if all(n in column for n in KO1 + WT1):
    expanded, expanded_measured = build(KO1 + WT1)
    keep_expanded = (expanded_measured[:, :3].sum(1) >= 1) | (expanded_measured[:, 3:].sum(1) >= 1)
    support_e, _ = run(expanded, keep_expanded, 20)
    ids_e = [i for i, k in zip(ids, keep_expanded, strict=True) if k]
    published_e = np.array([i in claim_ids for i in ids_e])
    called_e = support_e.sum(0) >= 10
    hits = int((called_e & published_e).sum())
    print(f"  rows {int(keep_expanded.sum())}, calls {int(called_e.sum())}, "
          f"precision {hits / max(int(called_e.sum()), 1):.3f}, recall {hits / int(published_e.sum()):.3f} "
          f"(summed columns: 689 calls, 0.977, 0.851)")
else:
    print("  the ___1 columns are not all present in this table")

print("\nW — the population, searched under the documented rule")
print(f"  {'population rule':>34} {'rows':>6} {'calls':>7} {'precision':>10} {'recall':>8}")
for label, rule in (
    ("at least 1 in a group (the one used)", keep),
    ("at least 2 in a group", (measured[:, :3].sum(1) >= 2) | (measured[:, 3:].sum(1) >= 2)),
    ("at least 3 in a group", (measured[:, :3].sum(1) >= 3) | (measured[:, 3:].sum(1) >= 3)),
    ("at least 1 in both groups", (measured[:, :3].sum(1) >= 1) & (measured[:, 3:].sum(1) >= 1)),
    ("at least 3 in the knockout arm", measured[:, :3].sum(1) >= 3),
    ("every row with any value", measured.any(1)),
):
    support_p, _ = run(matrix, rule, 20)
    ids_p = [i for i, k in zip(ids, rule, strict=True) if k]
    published_p = np.array([i in claim_ids for i in ids_p])
    called_p = support_p.sum(0) >= 10
    hits = int((called_p & published_p).sum())
    precision = hits / max(int(called_p.sum()), 1)
    recall = hits / max(int(published_p.sum()), 1)
    print(f"  {label:>34} {int(rule.sum()):>6} {int(called_p.sum()):>7} {precision:>10.3f} {recall:>8.3f}")
print("  (the paper called 798; a population landing there under the documented rule would be the answer)")

print("\nX — what the raw store holds for this deposit")
root = HOME / "raw"
for path in sorted(root.glob("*/*")):
    name = path.name.lower()
    if any(word in name for word in ("perseus", "session", "summary", "parameters", "glygly", "txt", "xlsx", "zip")):
        print(f"  {path.parent.name[:12]}  {path.name}  ({path.stat().st_size:,} bytes)")
print("  A Perseus session file, a processed matrix or a summary would settle the threshold and")
print("  the population without a Windows machine. Check PRIDE's file listing too.")
