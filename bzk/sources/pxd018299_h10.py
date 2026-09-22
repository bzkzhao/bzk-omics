"""Run `walk/PREREG-PXD018299-H10.md`: gate G, check A, and H10 on the anchor.

`python -m bzk.sources.pxd018299_h10`, after both deposits and both supplements are in the content
store. Writes `tests/fixtures/pxd018299_h10.json`.

**The pre-registration is the specification and this module implements it, in its order.** Gate G
on published Perseus output first (§4), then check A on the anchor's own matrix, then — only if a
variant survives both — the 360-member family and readouts A to D (§§5–6).

**Its §7 expectations are not inputs.** X1 to X8 appear nowhere in this module: no constant carries
them, no branch consults them, and nothing is compared against them. The registered *rules* are
implemented; the registered *guesses* are for the reviewer to score afterwards.

**Nothing here re-implements turn 16 or turn 18.** The shotgun pipeline, the sample axes, the
supplement readers, the imputation grid and `run_member` come from
`bzk/sources/pxd026748_reconstruction.py`; the test itself is `bzk/stats/perseus_s0.py`. What is
new here is the anchor's own population and matrix, the two checks that fix the unstated steps,
and the readouts.

**Two runs of the same test, at two parameter sets, and they are not interchangeable.** Gate G runs
at `s0 = 1`, FDR 0.05, 6 against 6, because those are the values `PXD026748`'s Supplementary Table
3 was produced under. The anchor runs at `s0 = 0.1`, FDR 0.01, 3 against 3, because those are the
values PMC7884788 names. Neither set is a default and neither is carried across.

## `walk/PXD018299-author-parameters.json`

The pre-registration's author-parameter rule enters through exactly one file, and this module
defines its schema:

```json
{
  "source": "who stated them, when, and in what form",
  "date_received": "2026-09-30",
  "width_sd": 0.3,
  "downshift_sd": 1.8,
  "scope": "per_sample",
  "seed": 0,
  "randomisations": 250,
  "scheme": "exhaustive_excluding_trivial"
}
```

`source` and `date_received` are required; every parameter key is optional and defaults to the
registered value. **Any other key refuses by name** — a file with a misspelled key would otherwise
silently run the registered configuration while claiming to be the authors'. An example with
placeholder values is at `notes/example-author-parameters.json`; this module never creates the real
file, and `walk/PXD018299-author-parameters.json` is not written here.

**Whether the file was *committed* decides what it is, not whether it exists.** §6 A makes the
author configuration readout A's primary only if it is committed before the run; an untracked file
on someone's disk is not a record. The run asks `git cat-file -e HEAD:<path>` and records the
answer either way. **H10's verdict never reads this file** — readout B stays on the registered
default cell, as v8's rule requires and §6 B repeats.

*(This paragraph said `git ls-files --error-unmatch` until 2026-09-22 and was stale by one turn:
`is_tracked` moved to `HEAD` when the staged-file loophole was closed, and the docstring did not
follow. A comment that describes a check the code stopped making is worse than no comment, because
it is the thing a reader trusts instead of reading the function.)*
"""

from __future__ import annotations

import collections
import json
import math
import platform
import subprocess
import sys
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from bzk.adapters import maxquant
from bzk.curation.loader import LoadedCuration
from bzk.ontology.invariants import NODE_TYPE_KEY
from bzk.provenance.raw_store import verify
from bzk.rebuild import _deposit_for
from bzk.sources.pride import PXD018299_SITES
from bzk.sources.protein_groups import SUPP_DATA_1, SupplementaryFile
from bzk.sources.pxd018299_published_cascade import S1_AS_DEPOSIT
from bzk.sources.pxd026748_ingest_figures import _parse_arm
from bzk.sources.pxd026748_published_cascade import SUPP_TABLE_1, _commit
from bzk.sources.pxd026748_reconstruction import (
    DEFAULT_DOWNSHIFT_SD,
    DEFAULT_SCOPE,
    DEFAULT_WIDTH_SD,
    SEEDS,
    TABLE_3_SHEET,
    Member,
    _fraction,
    family_members,
    first_accession,
    intensity_matrix,
    log2_zero_as_missing,
    pipeline,
    resolve_column,
    sample_axes,
    sheet_rows,
    shotgun_rows,
)
from bzk.stats import downshifted_normal
from bzk.stats.perseus_s0 import SCHEMES, perseus_s0

REPO_ROOT = Path(__file__).resolve().parents[2]
CURATION_DIR = REPO_ROOT / "data" / "curation"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"
HOME = Path.home() / ".bzk-omics"

ANCHOR_CURATION = CURATION_DIR / "curation_PXD018299.json"
SHOTGUN_CURATION = CURATION_DIR / "curation_PXD026748_shotgun.json"
CASCADE_FIXTURE = FIXTURES_DIR / "pxd018299_published_cascade.json"
TARGETS_FIXTURE = FIXTURES_DIR / "pxd018299_platform_targets.json"
AUTHOR_PARAMETERS = REPO_ROOT / "walk" / "PXD018299-author-parameters.json"
FIXTURE_NAME = "pxd018299_h10.json"
#: Attempt 2 writes its own file. §"What it supersedes": *"Attempt 1 is not replaced. Its result
#: stands, and this attempt is reported beside it."* Beside, not over.
FIXTURE_NAME_ATTEMPT_2 = "pxd018299_h10_attempt2.json"
#: Attempt 3 likewise. *"Attempts 1 and 2 stand and are reported beside this one."*
FIXTURE_NAME_ATTEMPT_3 = "pxd018299_h10_attempt3.json"

GENERATED_BY = "python -m bzk.sources.pxd018299_h10"

#: §1. The paper's own values, for the anchor run alone.
ANCHOR_S0 = 0.1
ANCHOR_ALPHA = 0.01

#: §4's gate values, which are `PXD026748`'s Supplementary Table 3's and not the anchor's.
GATE_S0 = 1.0
GATE_ALPHA = 0.05
GATE_MIN_PRECISION = 0.95
GATE_MIN_RECALL = 0.95
#: *"a protein counts as called if it is called in at least 10 of the 20 seeds"* (§4) — which is a
#: majority of the seeds, and is computed as one by `gate_majority` rather than written as a bare
#: 10. **The choice is for the tests and costs nothing at the registered size**: a test that runs
#: three seeds would otherwise need ten of three, and a threshold that cannot be met is not a
#: smaller version of §4's rule. At the registered twenty seeds the two readings are the same
#: number, which `test_the_gate_majority_is_ten_of_twenty` holds.
GATE_MAJORITY = 10
#: *"If it is below 30, G is flagged weakly informative but not failed"* (§4).
GATE_WEAKLY_INFORMATIVE_BELOW = 30

#: §4. *"This is the reviewer's understanding of Perseus's default, not verified."*
RANDOMISATIONS = 250

#: §2. The anchor's contrast, numerator first: KO + IFN against WT + IFN.
KO_ARM = "KO_IFN"
WT_ARM = "WT_IFN"
REPLICATES = (1, 2, 3)

#: §3's two column families. The summed columns are the platform's; the `___1` columns are the
#: per-multiplicity ones an expanded Perseus table would carry.
COLUMN_FAMILIES = ("summed", "multiplicity_1")

#: §3's normalisation candidates, in the order the rule tests them.
NORMALISATIONS = ("none", "median_subtracted")

#: §3. *"if S1's value equals log2 of the deposit value (|Δ| ≤ 1e-6) for at least 99% of those
#: cells"*.
MATCH_TOLERANCE = 1e-6
MATCH_CRITERION = 0.99

#: §3's valid-value candidates, strictest first.
VALID_VALUE_CANDIDATES = (3, 2, 1)

#: §6 B's registered directions, with the same slack turn 17 adopted for the same reason: these
#: shares are rationals over the claim counts, and a registered direction decided by binary
#: floating point at its own boundary is not the registered direction.
RECURS_AT_OR_ABOVE = 0.05
ABSENT_AT_OR_BELOW = 0.01
THRESHOLD_TOLERANCE = 1e-9

#: §6 A. *"the median over its 20 draws"*. At exactly 10 of 20 the median of the support indicator
#: is 0.5, and the rule includes it — the same majority §4 states for the gate, so the two readouts
#: do not disagree about what a median of twenty booleans means.
MEDIAN_SUPPORT = 0.5

#: The author file's schema — see the module docstring.
AUTHOR_PARAMETER_KEYS = ("width_sd", "downshift_sd", "scope", "seed", "randomisations", "scheme")
AUTHOR_REQUIRED_KEYS = ("source", "date_received")


class H10Error(ValueError):
    """An input cannot support the pre-registration as written. Never a warning (`CLAUDE.md`)."""


@dataclass(frozen=True)
class Variant:
    """One of §4's eight: a sidedness and a permutation scheme."""

    sidedness: str
    scheme: str

    @property
    def name(self) -> str:
        return f"{self.sidedness}+{self.scheme}"


#: Attempt 1's two sidedness values, pinned here rather than taken from `perseus_s0.SIDEDNESS`.
#: **That module gained a third, `joint_half`, on 2026-09-22 for attempt 2**, and attempt 1's
#: variant list is part of a registered and already-run gate: reading it off a constant that grows
#: would have silently made attempt 1 a twelve-variant run, and its committed result a description
#: of something else.
ATTEMPT_1_SIDEDNESS = ("joint", "per_side")

#: Attempt 2's four, in `walk/PREREG-PXD018299-H10-attempt2.md` §2's order: `joint_half` crossed
#: with the same four schemes, and *"no other convention is admitted"*. The order is load-bearing
#: for §3's tie-break, exactly as attempt 1's is.
ATTEMPT_2_SIDEDNESS = ("joint_half",)

#: §3's G2b bands, **inclusive at both ends**: Perseus called 72 higher in WT and 210 higher in
#: ISG15-/-, and the bands are those figures ±20%. They are read once, by `direction_split`, after
#: every count is formed.
G2B_WT_BAND = (58, 86)
G2B_KO_BAND = (168, 252)

#: The label every result block of attempt 2 carries. §1: the convention was fitted to Table 3, so
#: nothing measured under it is independent of the table it was fitted on, whatever else it passes.
ATTEMPT_2_VALIDATION = "in-sample; independent confirmation pending"

#: §4's three tiers of publication-named targets. The curated fourteen come from the committed
#: targets fixture (readout D's own source); these two lists are §4's own, and are the only place
#: this module carries a symbol list of its own.
DPRIME_NOT_CURATED = ("DDX3X", "DHX9")
DPRIME_DISCUSSION = (
    "TAP1",
    "GBP1",
    "STAT1",
    "IFIT1",
    "PSMB10",
    "PSMB9",
    "GBP2",
    "PARP14",
    "MAGE",
)

#: §4: *"MAGE is matched as any symbol beginning `MAGE`, and that rule is declared as such."*
DPRIME_PREFIX_SYMBOLS = ("MAGE",)

#: §4's eight, in the order the section lists them — sidedness outermost, scheme inner. The order
#: is load-bearing: *"Ties go to the earlier variant in the list above."*
VARIANTS = tuple(Variant(s, c) for s in ATTEMPT_1_SIDEDNESS for c in SCHEMES)

ATTEMPT_2_VARIANTS = tuple(Variant(s, c) for s in ATTEMPT_2_SIDEDNESS for c in SCHEMES)

#: `walk/PREREG-PXD018299-H10-attempt3.md` §2's two, **and the primary is the first of them by
#: fiat rather than by any score.** §2 fixes it *"by principle rather than by tie"*: it keeps both
#: of `HYPOTHESIS.md` v8's random steps — imputation and permutation, paired by seed — and is
#: closest to Perseus's documented practice of drawing a fixed number of randomisations. **No tie
#: rule applies to attempt 3**, and `primary_variant`'s F1 comparison is not reached on that path.
ATTEMPT_3_PRIMARY = Variant("joint_half", "random_excluding_trivial")
ATTEMPT_3_SECONDARY = Variant("joint_half", "exhaustive_excluding_trivial")
ATTEMPT_3_VARIANTS = (ATTEMPT_3_PRIMARY, ATTEMPT_3_SECONDARY)

#: §3's strengthened check A. Attempt 2 admitted a variant that reached `q <= 0.01` under **any**
#: seed, and `joint_half+random` did so on exactly one favourable draw and supported nothing in a
#: typical one — so its registered primary was degenerate and H10 went untested in substance.
#: The median over the twenty seeds is what a typical draw means, and 1 is the least it can be
#: and still be a claim.
CHECK_A_MEDIAN_MINIMUM = 1

#: §4's second flag, on every attempt-3 result block. Attempt 2 §4 measured it: about 2% of S1's
#: cells match log2 of the deposit, and 7 published claims carry six S1 values apiece while having
#: no measured value in any of the six deposit columns. The reconstruction therefore tests the
#: deposit, and every figure has to say so.
ATTEMPT_3_MATRIX_FLAG = "deposit, not the published S1"

#: §3's own words for the outcome where the primary is not admitted.
ATTEMPT_3_NOT_TESTED = "not tested (attempt 3)"


def variants_for(attempt: int) -> tuple[Variant, ...]:
    """The registered variant list for an attempt. Nothing else selects between the three."""
    if attempt == 1:
        return VARIANTS
    if attempt == 2:
        return ATTEMPT_2_VARIANTS
    if attempt == 3:
        return ATTEMPT_3_VARIANTS
    raise H10Error(f"attempt {attempt!r} is not 1, 2 or 3; there are three registrations")


# ── gate G ──────────────────────────────────────────────────────────────────────────────────────


def table_3_calls(
    source: Path | bytes, *, sheet: str = TABLE_3_SHEET, id_column: str | None = None
) -> tuple[set[str], dict[str, int]]:
    """Supplementary Table 3's `+` calls, by `Uniprot ID`, with every distinct cell value counted.

    A different column of the same sheet turn 16's `read_table_3` reads, located the same way. The
    `+` column is resolved by content — its spelling is in no document this repository holds — and
    a cell counts as a call when, stripped, it is exactly `+`. Reporting every value found is what
    makes that reading auditable rather than assumed.
    """
    rows = sheet_rows(source, sheet=sheet, markers=[id_column or "Uniprot ID"])
    if not rows:
        raise H10Error(f"sheet {sheet!r} has a header and no data rows")
    ids = id_column or resolve_column(
        list(rows[0]), required=["uniprot"], forbidden=[], what="Table 3's protein identifier"
    )
    call_column = resolve_column(
        list(rows[0]),
        required=["significant"],
        forbidden=[],
        what="Table 3's significance call column",
    )
    called: set[str] = set()
    seen: collections.Counter[str] = collections.Counter()
    for row in rows:
        value = row.get(call_column)
        seen["" if value is None else str(value)] += 1
        if value is not None and str(value).strip() == "+":
            called.add(str(row[ids]).strip())
    return called, dict(sorted(seen.items()))


def direction_split(up: np.ndarray, down: np.ndarray, *, majority: int) -> dict[str, Any]:
    """G2b: how many rows the majority of seeds called higher in WT, and how many in ISG15-/-.

    `walk/PREREG-PXD018299-H10-attempt2.md` §3 asks for the two counts *"over all 2,438 rows, with
    the majority-of-seeds call"*, against the bands [58, 86] and [168, 252] — Perseus's 72 and 210
    ±20%, **inclusive at both ends**, since §3 writes them as ranges and a count at an endpoint is
    inside a range.

    **The majority is applied per direction, not to significance and then to a direction.** A row
    counts as higher in WT when at least a majority of the seeds called it *and* put it there; a
    row called by many seeds in neither consistent direction is in neither count, which is the
    honest answer for it. The two can in principle both hold at an even seed count (ten up and ten
    down of twenty), so `both` is reported rather than assumed away.
    """
    in_wt = up >= majority
    in_ko = down >= majority
    wt, ko = int(in_wt.sum()), int(in_ko.sum())
    return {
        "higher_in_wt": wt,
        "higher_in_knockout": ko,
        "both": int((in_wt & in_ko).sum()),
        "bands": {"higher_in_wt": list(G2B_WT_BAND), "higher_in_knockout": list(G2B_KO_BAND)},
        "wt_in_band": G2B_WT_BAND[0] <= wt <= G2B_WT_BAND[1],
        "knockout_in_band": G2B_KO_BAND[0] <= ko <= G2B_KO_BAND[1],
        "passes": bool(
            G2B_WT_BAND[0] <= wt <= G2B_WT_BAND[1] and G2B_KO_BAND[0] <= ko <= G2B_KO_BAND[1]
        ),
    }


def orientation_holds(
    values: np.ndarray, wt_columns: Sequence[int], ko_columns: Sequence[int]
) -> bool:
    """Whether `direction > 0` means *higher in WT* under the argument order actually used.

    A probe rather than a comment: one synthetic row, higher in every WT column and zero in every
    ISG15-/- one, pushed through `perseus_s0` with the **same two arguments in the same order**
    `gate_block` uses. If that order were ever swapped, G2b's two bands would silently exchange
    places and both would still look plausible — 33 and 145 against 58-86 and 168-252 is a miss
    either way round, and a swap would be invisible in the figures.
    """
    probe = np.zeros((1, values.shape[1]))
    probe[0, list(wt_columns)] = 1.0
    outcome = perseus_s0(
        probe[:, list(wt_columns)],
        probe[:, list(ko_columns)],
        s0=GATE_S0,
        alpha=GATE_ALPHA,
        randomisations=2,
        seed=0,
        sidedness="joint",
        scheme="random",
    )
    return bool(outcome.direction[0] > 0)


def gate_majority(seeds: Sequence[int]) -> int:
    """§4's *"at least 10 of the 20 seeds"*, as a majority of however many seeds ran."""
    return math.ceil(len(seeds) / 2)


def gate_metrics(called: np.ndarray, target: np.ndarray) -> dict[str, Any]:
    """Precision and recall of `called` against `target`, plus F1. `None` where undefined.

    F1 is the harmonic mean §4 names, and it is `None` rather than 0 where either side is
    undefined: a variant that called nothing has no precision, and scoring it zero would rank it
    against variants whose precision exists.
    """
    hits = int(np.sum(called & target))
    precision = _fraction(hits, int(called.sum()))
    recall = _fraction(hits, int(target.sum()))
    f1 = (
        None
        if precision["share"] is None
        or recall["share"] is None
        or precision["share"] + recall["share"] == 0
        else 2 * precision["share"] * recall["share"] / (precision["share"] + recall["share"])
    )
    return {"precision": precision, "recall": recall, "f1": f1}


def gate_block(
    *,
    values: np.ndarray,
    wt_columns: Sequence[int],
    ko_columns: Sequence[int],
    complete: np.ndarray,
    accessions: Sequence[str],
    calls: set[str],
    call_values: Mapping[str, int],
    randomisations: int = RANDOMISATIONS,
    seeds: Sequence[int] = SEEDS,
    variants: Sequence[Variant] = VARIANTS,
    direction: bool = False,
    progress: bool = True,
) -> dict[str, Any]:
    """§4's gate, over the attempt's variants. Pure.

    **The imputation is computed once per seed and shared by the eight variants.** They differ in
    how the null is drawn, not in the matrix they see, and imputing eight times per seed would be
    eight different matrices wearing one seed's name as well as eight times the work.

    The complete-case restriction is the gate's whole point (§4): a protein with no missing value
    cannot be moved by the draw, so its call is comparable with a published one without choosing a
    seed.

    **`direction` adds attempt 2's G2b and changes nothing else.** It is off by default, so
    attempt 1's block is byte-for-byte what it was — attempt 1 has already run and its result is
    committed. The two counts it adds ride on the same twenty imputations and the same calls the
    gate already makes, because running them again would be a second twenty draws wearing the same
    seeds' names.
    """
    target = np.array([a in calls for a in accessions], dtype=bool)
    counts = {variant.name: np.zeros(values.shape[0], dtype=int) for variant in variants}
    up_counts = {variant.name: np.zeros(values.shape[0], dtype=int) for variant in variants}
    down_counts = {variant.name: np.zeros(values.shape[0], dtype=int) for variant in variants}
    for index, seed in enumerate(seeds):
        filled = downshifted_normal(
            values,
            downshift_sd=DEFAULT_DOWNSHIFT_SD,
            width_sd=DEFAULT_WIDTH_SD,
            seed=seed,
            scope=DEFAULT_SCOPE,
        ).values
        for variant in variants:
            outcome = perseus_s0(
                # **WT is the numerator**, which is turn 19's argument order and is what makes
                # `direction > 0` mean *higher in WT*. `_orientation_holds` below asserts it on a
                # probe rather than leaving it to this comment.
                filled[:, list(wt_columns)],
                filled[:, list(ko_columns)],
                s0=GATE_S0,
                alpha=GATE_ALPHA,
                randomisations=randomisations,
                seed=seed,
                sidedness=variant.sidedness,
                scheme=variant.scheme,
            )
            counts[variant.name] += outcome.significant.astype(int)
            up_counts[variant.name] += (outcome.significant & (outcome.direction > 0)).astype(int)
            down_counts[variant.name] += (outcome.significant & (outcome.direction < 0)).astype(int)
        if progress:
            print(f"[gate] seed {index + 1:>2}/{len(seeds)}", end="\r")
    if progress:
        print()

    scored: dict[str, Any] = {}
    for variant in variants:
        called = counts[variant.name] >= gate_majority(seeds)
        metrics = gate_metrics(called[complete], target[complete])
        passes = (
            metrics["precision"]["share"] is not None
            and metrics["recall"]["share"] is not None
            and metrics["precision"]["share"] >= GATE_MIN_PRECISION
            and metrics["recall"]["share"] >= GATE_MIN_RECALL
        )
        scored[variant.name] = {
            **metrics,
            "called_complete_case": int(called[complete].sum()),
            "passes": bool(passes),
        }
        if direction:
            scored[variant.name]["direction_split"] = direction_split(
                up_counts[variant.name], down_counts[variant.name], majority=gate_majority(seeds)
            )

    complete_positive = int(target[complete].sum())
    return {
        "parameters": {
            "s0": GATE_S0,
            "fdr": GATE_ALPHA,
            "randomisations": randomisations,
            "seeds": list(seeds),
            "majority_of_seeds": gate_majority(seeds),
            "cell": {
                "width_sd": DEFAULT_WIDTH_SD,
                "downshift_sd": DEFAULT_DOWNSHIFT_SD,
                "scope": DEFAULT_SCOPE,
            },
        },
        "complete_case_proteins": int(complete.sum()),
        "complete_case_published_calls": complete_positive,
        "table_3_call_values": dict(call_values),
        "weakly_informative": complete_positive < GATE_WEAKLY_INFORMATIVE_BELOW,
        "variants": scored,
        "passes": any(v["passes"] for v in scored.values()),
        "thresholds": {"precision": GATE_MIN_PRECISION, "recall": GATE_MIN_RECALL},
    }


# ── the anchor's population and matrix ──────────────────────────────────────────────────────────


def anchor_population(table: maxquant.MaxQuantTable) -> tuple[list[list[str]], dict[str, int]]:
    """§2's population: every row but the reverse decoys.

    **Contaminants and low-localisation rows are kept, and so are rows the platform refused.** §2
    gives the reason and it is a finding rather than a convenience: the paper's own table retains
    33 peptides below 0.75 and 3 flagged contaminants, so removing them would reproduce the D6
    error this run exists to replace. `maxquant.drop_decoys_and_contaminants` drops both, so it is
    **not** used here — this is the one place in the repository where the decoy filter is applied
    without the contaminant one, and it is spelled out rather than borrowed.
    """
    column = {name: i for i, name in enumerate(table.header)}
    reverse = column.get("Reverse")
    if reverse is None:
        return list(table.rows), column
    return [row for row in table.rows if row[reverse].strip() != "+"], column


def anchor_columns(column: Mapping[str, int], family: str) -> tuple[list[int], list[str]]:
    """The six intensity column indices for one family, KO first then WT, and their names."""
    suffix = "" if family == "summed" else "___1"
    names = [f"Intensity {arm}_{i}{suffix}" for arm in (KO_ARM, WT_ARM) for i in REPLICATES]
    missing = [n for n in names if n not in column]
    if missing:
        raise H10Error(
            f"the deposit has no column(s) {missing} for the {family!r} family; its header carries "
            f"{sorted(n for n in column if n.startswith('Intensity '))}"
        )
    return [column[n] for n in names], names


def s1_columns(header: Sequence[str]) -> list[str]:
    """S1's six published log2 intensity columns, KO first then WT, located by content.

    **Their spelling is in no document this repository holds**, and S1's header carries Perseus'
    type prefixes (`T:`, `N:`, `C:`), so each is resolved by the fragments that identify it —
    `intensity` plus the arm and replicate — rather than by a name this module would be guessing.
    `resolve_column` refuses by name with the whole header printed where a column does not resolve
    to exactly one, which is the stop §3 needs rather than a wrong join.
    """
    return [
        resolve_column(
            list(header),
            required=["intensity", f"{arm.lower().replace('_', '')}{i}"],
            forbidden=["___", "ratio"],
            what=f"S1's published intensity for {arm}_{i}",
        )
        for arm in (KO_ARM, WT_ARM)
        for i in REPLICATES
    ]


@dataclass(frozen=True)
class MatrixCheck:
    """§3's joint decision: which column family, and whether anything was normalised."""

    family: str
    normalisation: str
    #: `True` where the decision was forced by the fallback rather than met by the criterion.
    undetermined: bool
    fractions: dict[str, dict[str, Any]]


def _match_fraction(published: np.ndarray, deposit_log2: np.ndarray) -> dict[str, Any]:
    """The share of deposit-measured cells where S1 equals log2 of the deposit, within tolerance."""
    comparable = np.isfinite(published) & np.isfinite(deposit_log2)
    matching = comparable & (np.abs(published - deposit_log2) <= MATCH_TOLERANCE)
    return _fraction(int(matching.sum()), int(comparable.sum()))


def matrix_check(
    *,
    published: np.ndarray,
    deposit_by_family: Mapping[str, np.ndarray],
    population_by_family: Mapping[str, np.ndarray],
) -> MatrixCheck:
    """§3's column-family and normalisation check, in the order §3 states it.

    Four combinations are measured — two families crossed with two normalisations — and then the
    rule picks, never the outcome:

    1. a combination *meets the criterion* when at least 99% of the deposit-measured cells agree
       within 1e-6;
    2. among those that do, the **summed** family wins, *"since they are the platform's"*, and
       within a family **no normalisation** wins, since §3 tests it first;
    3. if none does, the summed family is used with no normalisation and the run is flagged
       `undetermined`, as §3's last clause requires.

    The medians for the normalised candidates are taken **over the population**, not over the 798
    published rows: §3 says *"with medians over the population"*, and a median over the claim set
    would be a median of the rows the paper selected rather than of the matrix it normalised.
    """
    fractions: dict[str, dict[str, Any]] = {}
    for family, deposit_log2 in deposit_by_family.items():
        medians = np.nanmedian(population_by_family[family], axis=0)
        for normalisation in NORMALISATIONS:
            candidate = deposit_log2 if normalisation == "none" else deposit_log2 - medians
            fractions[f"{family}+{normalisation}"] = _match_fraction(published, candidate)

    for family in COLUMN_FAMILIES:
        for normalisation in NORMALISATIONS:
            share = fractions[f"{family}+{normalisation}"]["share"]
            if share is not None and share >= MATCH_CRITERION:
                return MatrixCheck(family, normalisation, False, fractions)
    return MatrixCheck(COLUMN_FAMILIES[0], "undetermined", True, fractions)


def valid_value_choice(
    matrix: np.ndarray,
    *,
    claim_rows: Sequence[int],
    candidates: Sequence[int] = VALID_VALUE_CANDIDATES,
) -> dict[str, Any]:
    """§3's rule: the strictest candidate under which every published claim's row passes.

    Every candidate's count is reported whichever is taken. Where none retains all of them, the
    rule takes the one retaining the most and the run names the claims that fail — §3's own
    fallback, which is a measurement rather than a repair.
    """
    measured = ~np.isnan(matrix)
    half = matrix.shape[1] // 2
    reported: dict[str, Any] = {}
    for minimum in candidates:
        passes = (
            np.maximum(measured[:, :half].sum(axis=1), measured[:, half:].sum(axis=1)) >= minimum
        )
        retained = [i for i in claim_rows if bool(passes[i])]
        reported[str(minimum)] = {
            "rows_retained": int(passes.sum()),
            "claims_retained": len(retained),
            "retains_every_claim": len(retained) == len(claim_rows),
        }
    for minimum in candidates:
        if reported[str(minimum)]["retains_every_claim"]:
            return {"candidates": reported, "taken": minimum, "retains_every_claim": True}
    best = max(candidates, key=lambda m: (reported[str(m)]["claims_retained"], -m))
    return {"candidates": reported, "taken": best, "retains_every_claim": False}


def published_draw_estimates(
    *, published: np.ndarray, deposit_log2: np.ndarray, column_names: Sequence[str]
) -> dict[str, Any]:
    """§3's estimation readout, over the cells the **deposit** reports as missing.

    *"the imputed cells are identified by the deposit's missingness, not by a value cut-off"* — the
    whole answer to the circularity objection, so it is the only rule here. The implied downshift
    is how many measured standard deviations below the measured mean the published values sit; the
    implied width is their spread in the same units. Both are reported per column (per-sample
    scope) and once over the whole matrix, because §3 asks for both and they are different numbers.
    """
    missing = np.isnan(deposit_log2)
    filled = missing & np.isfinite(published)

    def estimate(values: np.ndarray, observed: np.ndarray) -> dict[str, Any]:
        if values.size == 0 or observed.size < 2:
            return {
                "n": int(values.size),
                "mean": None,
                "sd": None,
                "downshift": None,
                "width": None,
            }
        observed_mean, observed_sd = float(observed.mean()), float(observed.std(ddof=1))
        mean, sd = float(values.mean()), float(values.std(ddof=1)) if values.size > 1 else None
        return {
            "n": int(values.size),
            "mean": mean,
            "sd": sd,
            "observed_mean": observed_mean,
            "observed_sd": observed_sd,
            "downshift": None if not observed_sd else (observed_mean - mean) / observed_sd,
            "width": None if not observed_sd or sd is None else sd / observed_sd,
        }

    per_column = {
        name: estimate(published[filled[:, i], i], deposit_log2[~missing[:, i], i])
        for i, name in enumerate(column_names)
    }
    return {
        "rule": (
            "A cell is an imputed cell when the DEPOSIT reports no value for it, never when its "
            "published value falls below a cut-off. PREREG §3: identifying them by value would be "
            "the circularity this readout exists to avoid. Estimation only — it locates the "
            "published run and changes no family member and no primary readout."
        ),
        "per_sample": per_column,
        "whole_matrix": estimate(published[filled], deposit_log2[~missing]),
    }


# ── check A, and the choice of variant ──────────────────────────────────────────────────────────


def check_a(
    *,
    numerator: np.ndarray,
    denominator: np.ndarray,
    variants: Sequence[Variant],
    randomisations: int = RANDOMISATIONS,
    seeds: Sequence[int] = SEEDS,
    progress: bool = True,
) -> dict[str, Any]:
    """§4's attainability check: one claim reaching `q <= 0.01` and `d > 0`, under any seed.

    The matrices are already imputed per seed by the caller — `numerator`/`denominator` here are
    the *unfilled* ones and each seed's imputation is applied inside, because a variant's
    attainability is a property of the test at the default cell rather than of one draw.
    """
    combined = np.hstack([numerator, denominator])
    half = numerator.shape[1]
    reached: dict[str, Any] = {name.name: {"reached": False, "seed": None} for name in variants}
    for seed in seeds:
        filled = downshifted_normal(
            combined,
            downshift_sd=DEFAULT_DOWNSHIFT_SD,
            width_sd=DEFAULT_WIDTH_SD,
            seed=seed,
            scope=DEFAULT_SCOPE,
        ).values
        for variant in variants:
            if reached[variant.name]["reached"]:
                continue
            outcome = perseus_s0(
                filled[:, :half],
                filled[:, half:],
                s0=ANCHOR_S0,
                alpha=ANCHOR_ALPHA,
                randomisations=randomisations,
                seed=seed,
                sidedness=variant.sidedness,
                scheme=variant.scheme,
            )
            if bool((outcome.significant & (outcome.d > 0)).any()):
                reached[variant.name] = {"reached": True, "seed": int(seed)}
        if progress:
            print(f"[check A] seed {seed + 1:>2}/{len(seeds)}", end="\r")
    if progress:
        print()
    return reached


def check_a_typical(
    *,
    numerator: np.ndarray,
    denominator: np.ndarray,
    claim_rows: Sequence[int],
    variants: Sequence[Variant],
    randomisations: int = RANDOMISATIONS,
    seeds: Sequence[int] = SEEDS,
    progress: bool = True,
) -> dict[str, Any]:
    """Attempt 3 §3's check A: the **median over seeds** of the per-seed claim count, at least 1.

    **This is a different question from attempts 1 and 2's, and `check_a` above is left alone.**
    That one asks whether any seed reaches `q <= 0.01` with `d > 0` and short-circuits on the
    first that does. Attempt 2's result is what makes the difference matter: `joint_half+random`
    reached it at seed 4 and at no other, supported nothing in a typical draw, and was made the
    registered primary by a tie rule — so the registered verdict came from a variant that calls
    almost nothing, and H10 went untested in substance. The median is what a typical draw means.

    **It counts claims, not rows.** §3 says *"the per-seed count of claims with q ≤ 0.01 and
    d > 0"*; attempts 1 and 2's implementation asked `.any()` over every row of the matrix, which
    is a superset of the claims. The two agree on whether anything is reached and disagree on how
    much, and attempt 3 needs the amount.

    Every seed's count is reported, not only the median: a median of 1 over counts of
    `[0, 0, 1, 40, …]` and one over `[1, 1, 1, 1, …]` are different facts about a variant, and the
    figure that admits it should not hide which it was.
    """
    combined = np.hstack([numerator, denominator])
    half = numerator.shape[1]
    rows = list(claim_rows)
    counts: dict[str, list[int]] = {v.name: [] for v in variants}
    for index, seed in enumerate(seeds):
        filled = downshifted_normal(
            combined,
            downshift_sd=DEFAULT_DOWNSHIFT_SD,
            width_sd=DEFAULT_WIDTH_SD,
            seed=seed,
            scope=DEFAULT_SCOPE,
        ).values
        for variant in variants:
            outcome = perseus_s0(
                filled[:, :half],
                filled[:, half:],
                s0=ANCHOR_S0,
                alpha=ANCHOR_ALPHA,
                randomisations=randomisations,
                seed=seed,
                sidedness=variant.sidedness,
                scheme=variant.scheme,
            )
            supported = outcome.significant & (outcome.d > 0)
            counts[variant.name].append(int(sum(1 for row in rows if supported[row])))
        if progress:
            print(f"[check A] seed {index + 1:>2}/{len(seeds)}", end="\r")
    if progress:
        print()
    return {
        name: {
            "counts_by_seed": seed_counts,
            "median": float(np.median(seed_counts)),
            "minimum_required": CHECK_A_MEDIAN_MINIMUM,
            "reached": float(np.median(seed_counts)) >= CHECK_A_MEDIAN_MINIMUM,
            "reached_under_any_seed": any(c > 0 for c in seed_counts),
        }
        for name, seed_counts in counts.items()
    }


def g2_rerun_consistency(
    gate: Mapping[str, Any], earlier: Mapping[str, Any], *, variants: Sequence[Variant]
) -> dict[str, Any]:
    """§3: G2a and G2b recomputed must equal attempt 2's exactly, or the run stops.

    *"since they are deterministic given the seeds. A difference stops the run and is reported as
    an instrument fault."* Six integers per variant are compared — precision's numerator and
    denominator, recall's, and the two direction counts — rather than the shares and the `passes`
    flags: a share is a quotient, and two different pairs of counts can produce the same one.

    A variant that attempt 2 did not score at all is a mismatch too, and is named as one. Attempt
    2 ran four variants and attempt 3 runs two of them, so this should never fire; it fires if the
    committed fixture is not the run attempt 3 thinks it is.
    """
    #: `(name, path)` for each of the six integers compared, as a path through the block rather
    #: than a lambda so the field names and the places they come from are one list.
    fields: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("precision_numerator", ("precision", "numerator")),
        ("precision_denominator", ("precision", "denominator")),
        ("recall_numerator", ("recall", "numerator")),
        ("recall_denominator", ("recall", "denominator")),
        ("higher_in_wt", ("direction_split", "higher_in_wt")),
        ("higher_in_knockout", ("direction_split", "higher_in_knockout")),
    )

    def read(block: Mapping[str, Any], path: tuple[str, ...]) -> int:
        value: Any = block
        for key in path:
            value = value[key]
        return int(value)

    compared: dict[str, Any] = {}
    differences: list[dict[str, Any]] = []
    for variant in variants:
        recomputed = gate["variants"].get(variant.name)
        previous = earlier.get("gate_g", {}).get("variants", {}).get(variant.name)
        if recomputed is None or previous is None:
            differences.append({"variant": variant.name, "field": "variant", "reason": "absent"})
            compared[variant.name] = {"absent": True}
            continue
        entry: dict[str, Any] = {}
        for field, path in fields:
            now, before = read(recomputed, path), read(previous, path)
            entry[field] = {"attempt_3": now, "attempt_2": before, "equal": now == before}
            if now != before:
                differences.append(
                    {"variant": variant.name, "field": field, "attempt_3": now, "attempt_2": before}
                )
        compared[variant.name] = entry
    return {
        "source": FIXTURE_NAME_ATTEMPT_2,
        "compared": compared,
        "differences": differences,
        "consistent": not differences,
    }


def admitted_variants(
    gate: Mapping[str, Any],
    attainability: Mapping[str, Any],
    *,
    variants: Sequence[Variant] = VARIANTS,
    direction: bool = False,
) -> list[str]:
    """Attempt 1 §4: those passing both G and A. Attempt 2 §3: G2a **and G2b** and A.

    `direction` is what makes it attempt 2's rule. It defaults off, so attempt 1's admission is
    the function it always was — and a variant that passes G2a on precision and recall while
    calling 33 rows up against a band of [58, 86] is exactly what G2b exists to exclude.
    """
    return [
        v.name
        for v in variants
        if gate["variants"][v.name]["passes"]
        and attainability[v.name]["reached"]
        and (not direction or gate["variants"][v.name]["direction_split"]["passes"])
    ]


def primary_variant(
    names: Sequence[str], gate: Mapping[str, Any], *, variants: Sequence[Variant] = VARIANTS
) -> str | None:
    """§4: the admitted variant with the highest G F1, ties to the earlier one in `VARIANTS`.

    The tie-break is positional and not alphabetical, because §4 says *"the earlier variant in the
    list above"* and that list is `VARIANTS`' own order. An F1 of `None` — a variant that called
    nothing — cannot win; it is not scored zero, which would rank it against variants whose F1
    exists.
    """
    order = {v.name: i for i, v in enumerate(variants)}
    scored = [
        (n, gate["variants"][n]["f1"]) for n in names if gate["variants"][n]["f1"] is not None
    ]
    if not scored:
        return None
    best = max(f1 for _, f1 in scored)
    return min((n for n, f1 in scored if f1 == best), key=lambda n: order[n])


# ── the family and the readouts ─────────────────────────────────────────────────────────────────


def run_paired_member(
    matrix: np.ndarray,
    half: int,
    member: Member,
    variant: Variant,
    *,
    permutation_seed: int | None = None,
    randomisations: int = RANDOMISATIONS,
) -> np.ndarray:
    """One member's support per row: `q <= 0.01` **and** `d > 0`, as §1 defines support.

    §5 pairs the two random steps — *"Draw k uses imputation seed k and permutation seed k"* — so
    `permutation_seed` defaults to the member's own. Passing it explicitly is what the two
    isolations in §6 do, and it is a parameter rather than a second function so the paired and the
    isolated runs cannot drift apart.
    """
    filled = downshifted_normal(
        matrix,
        downshift_sd=member.downshift_sd,
        width_sd=member.width_sd,
        seed=member.seed,
        scope=member.scope,
    ).values
    outcome = perseus_s0(
        filled[:, :half],
        filled[:, half:],
        s0=ANCHOR_S0,
        alpha=ANCHOR_ALPHA,
        randomisations=randomisations,
        seed=member.seed if permutation_seed is None else permutation_seed,
        sidedness=variant.sidedness,
        scheme=variant.scheme,
    )
    return np.asarray(outcome.significant & (outcome.d > 0), dtype=bool)


def _default_cell_members(members: Sequence[Member]) -> list[Member]:
    return [m for m in members if m.is_default_cell]


def instability(support: np.ndarray) -> np.ndarray:
    """Which rows' support **differs** across the draws — §6 B's quantity, per row."""
    return np.asarray(support.any(axis=1) & ~support.all(axis=1), dtype=bool)


def h10_verdict(share: float | None) -> dict[str, Any]:
    """§6 B's registered directions, with the boundary slack turn 17 established."""
    if share is None:
        return {"outcome": "undefined", "share": None, "reason": "no claim carries an imputed cell"}
    if share >= RECURS_AT_OR_ABOVE - THRESHOLD_TOLERANCE:
        outcome = "recurs"
    elif share <= ABSENT_AT_OR_BELOW + THRESHOLD_TOLERANCE:
        outcome = "absent"
    else:
        outcome = "indeterminate"
    return {"outcome": outcome, "share": share, "reason": None}


def _median_supported(support: np.ndarray) -> np.ndarray:
    """Rows supported by the median over draws — see `MEDIAN_SUPPORT`."""
    return np.asarray(np.median(support.astype(float), axis=1) >= MEDIAN_SUPPORT, dtype=bool)


# ── the author configuration ────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class AuthorConfiguration:
    """The author-stated parameters, their provenance, and whether the file was committed."""

    parameters: dict[str, Any]
    source: str
    date_received: str
    tracked: bool

    def member(self) -> Member:
        return Member(
            width_sd=float(self.parameters.get("width_sd", DEFAULT_WIDTH_SD)),
            downshift_sd=float(self.parameters.get("downshift_sd", DEFAULT_DOWNSHIFT_SD)),
            scope=str(self.parameters.get("scope", DEFAULT_SCOPE)),
            seed=int(self.parameters.get("seed", 0)),
        )


def read_author_parameters(
    path: Path, *, repo_root: Path = REPO_ROOT
) -> AuthorConfiguration | None:
    """The author file, validated, or `None` where it does not exist.

    **An unknown key refuses by name.** A misspelled `downshfit_sd` would otherwise be dropped and
    the registered default run in its place, under a record claiming the authors' values — the one
    failure mode this file has, since nothing downstream can tell a defaulted parameter from a
    stated one.
    """
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    unknown = [k for k in payload if k not in (*AUTHOR_PARAMETER_KEYS, *AUTHOR_REQUIRED_KEYS)]
    if unknown:
        raise H10Error(
            f"{path.name} carries unknown key(s) {sorted(unknown)}. Accepted: "
            f"{sorted(AUTHOR_PARAMETER_KEYS)}, plus the required {sorted(AUTHOR_REQUIRED_KEYS)}. "
            "A key this module does not know would be dropped, and the registered default would "
            "run under a record claiming the authors' value."
        )
    missing = [k for k in AUTHOR_REQUIRED_KEYS if k not in payload]
    if missing:
        raise H10Error(
            f"{path.name} is missing {sorted(missing)}. PREREG's author-parameter rule admits "
            "values only with who stated them, when, and in what form: 'received' is established "
            "by the record, not by memory."
        )
    if "scheme" in payload and payload["scheme"] not in SCHEMES:
        raise H10Error(
            f"{path.name} names scheme {payload['scheme']!r}, not one of {list(SCHEMES)}"
        )
    return AuthorConfiguration(
        parameters={k: payload[k] for k in AUTHOR_PARAMETER_KEYS if k in payload},
        source=str(payload["source"]),
        date_received=str(payload["date_received"]),
        tracked=is_tracked(path, repo_root=repo_root),
    )


def is_tracked(path: Path, *, repo_root: Path = REPO_ROOT) -> bool:
    """Whether git tracks the file at this run's commit. `False` where git cannot answer.

    §6 A turns on *committed*, not on *present*: an untracked file on someone's disk is not a
    record, and a run that treated it as one would make readout A's primary depend on a file
    nobody else can see.

    **`git cat-file -e HEAD:<path>` since 2026-09-22, and the change closes a loophole.** This
    asked `git ls-files --error-unmatch`, which answers *is this path in the index* — and a file
    that has been `git add`ed and not committed is in the index. So a staged file passed a check
    whose whole purpose is that the values were **committed before the run**, which is the one
    thing the pre-registration will not take on trust. Asking `HEAD` asks the commit.
    """
    try:
        relative = path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        relative = path
    try:
        done = subprocess.run(
            ["git", "cat-file", "-e", f"HEAD:{relative.as_posix()}"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return False
    return done.returncode == 0


# ── the IO ──────────────────────────────────────────────────────────────────────────────────────


def _dataset(curation: LoadedCuration) -> Mapping[str, Any]:
    return next(n for n in curation.nodes if n[NODE_TYPE_KEY] == "Dataset")


def _supplement_path(supplement: SupplementaryFile, home: Path) -> Path:
    try:
        return verify(supplement.expected_content_hash, filename=supplement.filename, home=home)
    except FileNotFoundError as exc:
        raise SystemExit(
            f"{supplement.filename} is not in the content store under {home}; fetch it from "
            f"{supplement.url} and re-run. No fixture was written."
        ) from exc


def _write(fixtures_dir: Path, fixture: Mapping[str, Any], *, name: str = FIXTURE_NAME) -> Path:
    path = fixtures_dir / name
    path.write_text(json.dumps(fixture, indent=2) + "\n")
    return path


def fixture_name_for(attempt: int) -> str:
    """Which file an attempt writes. **Attempt 2 never writes attempt 1's**, which is asserted
    here rather than left to the call site: attempt 1's result is committed and stands."""
    if attempt == 1:
        return FIXTURE_NAME
    if attempt == 2:
        assert FIXTURE_NAME_ATTEMPT_2 != FIXTURE_NAME
        return FIXTURE_NAME_ATTEMPT_2
    if attempt == 3:
        assert FIXTURE_NAME_ATTEMPT_3 not in (FIXTURE_NAME, FIXTURE_NAME_ATTEMPT_2)
        return FIXTURE_NAME_ATTEMPT_3
    raise H10Error(f"attempt {attempt!r} is not 1, 2 or 3; there are three registrations")


def _load_anchor(path: Path) -> LoadedCuration:
    from bzk.curation.loader import load_path

    return load_path(path)


def _named_targets(path: Path) -> list[str]:
    """The 14 published targets, from the committed targets fixture's own symbol list.

    Read rather than retyped: `bzk/sources/pxd018299_differential.py` carries the same fourteen as
    `EXPECTED_TARGETS`, and a third copy here would be a mirror between two sources with nothing
    holding them equal. The fixture is the one this repository regenerates.
    """
    fixture = json.loads(path.read_text(encoding="utf-8"))
    return [str(t["gene"]) for t in fixture["targets"]]


def _s1_rows(supplement_path: Path) -> tuple[list[str], dict[int, dict[str, Any]]]:
    """S1's header and its rows by published row number, with the header located by content.

    The row numbers are `bzk/sources/pxd018299_published_cascade.py`'s own — it enumerates from 3,
    one past the header — so the cascade fixture's `row` field keys straight into this mapping. The
    two markers are that module's `S1_AS_DEPOSIT` entries rather than names retyped here.
    """
    from bzk.adapters import spreadsheet
    from bzk.sources.pxd026748_reconstruction import header_index

    cells = spreadsheet.rows(supplement_path)
    index = header_index(cells, [S1_AS_DEPOSIT["Protein"], S1_AS_DEPOSIT["Position"]])
    header = [str(c).strip() if c is not None else "" for c in cells[index]]
    rows = {
        number: dict(zip(header, row, strict=False))
        for number, row in enumerate(cells[index + 1 :], start=index + 2)
    }
    return header, rows


def _float_cell(value: object) -> float:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return float("nan")


def anchor_block(
    *,
    deposit: maxquant.MaxQuantTable,
    supplement_path: Path,
    cascade: Mapping[str, Any],
) -> dict[str, Any]:
    """§§2–3: the population, the two checks, the matrix, and the published-draw estimates.

    Returns the retained matrix (KO's three columns then WT's three) and the claim indices into
    it, beside every figure the fixture reports. Pure but for the two files it is handed.
    """
    rows, column = anchor_population(deposit)
    row_of_id = {str(r[column["id"]]).strip(): i for i, r in enumerate(rows)}

    claims = [dict(r) for r in cascade["rows"]]
    missing_ids = [c["deposit_id"] for c in claims if str(c["deposit_id"]) not in row_of_id]
    if missing_ids:
        raise H10Error(
            f"{len(missing_ids)} published claim(s) name a deposit row this population does not "
            f"carry ({missing_ids[:5]}). §2 records the join as measured: 798 rows, 798 distinct "
            "ids, none missing."
        )
    claim_index = [row_of_id[str(c["deposit_id"])] for c in claims]

    header, s1 = _s1_rows(supplement_path)
    published_columns = s1_columns(header)
    published = np.array(
        [[_float_cell(s1[int(c["row"])].get(name)) for name in published_columns] for c in claims],
        dtype=float,
    ).reshape(len(claims), len(published_columns))
    #: S1's own gene-name column, located by content, and the mean of each row's six published
    #: log2 intensities. Both are for readout D′ alone (attempt 2, §4) and are dropped from the
    #: written block; they are read here because this is the one place S1 is open.
    gene_column = resolve_column(
        list(header), required=["gene"], forbidden=[], what="S1's gene-name column"
    )
    gene_names = [str(s1[int(c["row"])].get(gene_column) or "") for c in claims]
    with np.errstate(invalid="ignore"):
        intensity = np.nanmean(np.where(np.isfinite(published), published, np.nan), axis=1)

    families: dict[str, tuple[np.ndarray, list[str]]] = {}
    for family in COLUMN_FAMILIES:
        indices, names = anchor_columns(column, family)
        raw = np.array([[_float_cell(r[i]) for i in indices] for r in rows], dtype=float)
        families[family] = (log2_zero_as_missing(raw), names)

    check = matrix_check(
        published=published,
        deposit_by_family={f: families[f][0][claim_index] for f in COLUMN_FAMILIES},
        population_by_family={f: families[f][0] for f in COLUMN_FAMILIES},
    )
    chosen = families[check.family][0]
    normalised = (
        chosen - np.nanmedian(chosen, axis=0)
        if check.normalisation == "median_subtracted"
        else chosen
    )

    valid = valid_value_choice(normalised, claim_rows=claim_index)
    measured = ~np.isnan(normalised)
    half = normalised.shape[1] // 2
    keep = (
        np.maximum(measured[:, :half].sum(axis=1), measured[:, half:].sum(axis=1)) >= valid["taken"]
    )
    position = np.cumsum(keep) - 1
    retained = [i for i, c in enumerate(claims) if keep[claim_index[i]]]
    lost = [claims[i]["deposit_id"] for i in range(len(claims)) if not keep[claim_index[i]]]

    matrix = normalised[keep]
    claim_rows = [int(position[claim_index[i]]) for i in retained]
    return {
        "matrix": matrix,
        "claim_rows": claim_rows,
        "s1_gene_names": [gene_names[i] for i in retained],
        "s1_intensity": [float(intensity[i]) for i in retained],
        "s1_gene_column": gene_column,
        "claims": [claims[i] for i in retained],
        "population_rows": len(rows),
        "rows_reaching_the_test": int(keep.sum()),
        "published_rows": len(claims),
        "exposure": len(retained),
        "claims_lost_to_the_valid_value_rule": lost,
        "column_family": check.family,
        "column_names": families[check.family][1],
        "normalisation": check.normalisation,
        "normalisation_undetermined": check.undetermined,
        "match_fractions": check.fractions,
        "valid_value_rule": valid,
        "published_draw": published_draw_estimates(
            published=published,
            deposit_log2=families[check.family][0][claim_index],
            column_names=families[check.family][1],
        ),
    }


def _readout_a(support: np.ndarray, claim_rows: Sequence[int]) -> dict[str, Any]:
    supported = _median_supported(support)[list(claim_rows)]
    return {"supported": int(supported.sum()), "of": len(claim_rows)}


def family_block_for(
    *,
    anchor: Mapping[str, Any],
    variants: Sequence[Variant],
    primary: Variant,
    members: Sequence[Member],
    targets: Sequence[str],
    author: AuthorConfiguration | None,
    randomisations: int = RANDOMISATIONS,
    disclosed: bool = False,
    progress: bool = True,
) -> dict[str, Any]:
    """§6's readouts A to D, plus H10's verdict. The family runs here.

    **`disclosed` labels readout A and changes nothing else.** Attempt 3 §1 discloses readout A
    for both its variants — 725 and 724 of 791, measured in attempt 2 — so it *"is reported for
    completeness and is not scored as a prediction"*. The flag is off by default, so attempts 1
    and 2's blocks are byte-for-byte what they were, and it is a field rather than a footnote
    because a figure that was known before the run is a different kind of claim from one that was
    not, and only the file will be read later.
    """
    matrix = np.asarray(anchor["matrix"])
    half = matrix.shape[1] // 2
    claim_rows = list(anchor["claim_rows"])
    claims = list(anchor["claims"])
    default = _default_cell_members(members)

    support = np.stack(
        [
            run_paired_member(matrix, half, m, primary, randomisations=randomisations)
            for m in members
        ],
        axis=1,
    )
    if progress:
        print(f"[family] {len(members)} member(s) under {primary.name}")
    default_support = support[:, [members.index(m) for m in default]]

    #: §3's rule, one level along: a claim's row carries an imputed cell where the DEPOSIT reports
    #: none, never where a value looks low.
    imputed_row = np.isnan(matrix).any(axis=1)
    claim_imputed = imputed_row[claim_rows]
    unstable = instability(default_support)[claim_rows]

    conditional = _fraction(int((unstable & claim_imputed).sum()), int(claim_imputed.sum()))
    isolations = {}
    for label, permutation_seed, imputation_fixed in (
        ("permutation_fixed", 0, False),
        ("imputation_fixed", None, True),
    ):
        drawn = np.stack(
            [
                run_paired_member(
                    matrix,
                    half,
                    Member(m.width_sd, m.downshift_sd, m.scope, 0 if imputation_fixed else m.seed),
                    primary,
                    permutation_seed=m.seed if imputation_fixed else permutation_seed,
                    randomisations=randomisations,
                )
                for m in default
            ],
            axis=1,
        )
        moved = instability(drawn)[claim_rows]
        isolations[label] = _fraction(int((moved & claim_imputed).sum()), int(claim_imputed.sum()))

    counts = support[claim_rows].sum(axis=1)
    categories = collections.Counter(
        "durable" if c == len(members) else ("unsupported" if c == 0 else "underdetermined")
        for c in counts.tolist()
    )

    supported_default = _median_supported(default_support)
    by_symbol: dict[str, list[int]] = collections.defaultdict(list)
    for position, claim in enumerate(claims):
        for symbol in str(claim.get("gene_names") or "").split(";"):
            if symbol.strip():
                by_symbol[symbol.strip()].append(position)

    readout_a: dict[str, Any] = {
        "default_cell": _readout_a(support, claim_rows),
        "primary": "default_cell",
        "compared_with": {"welch_based_recovery": 512, "significance_losses": 237},
    }
    if disclosed:
        readout_a["disclosed_before_run"] = True
    if author is not None:
        member = author.member()
        author_support = np.stack(
            [
                run_paired_member(
                    matrix,
                    half,
                    member,
                    next(
                        (v for v in VARIANTS if v.name.endswith(str(author.parameters["scheme"]))),
                        primary,
                    )
                    if "scheme" in author.parameters
                    else primary,
                    randomisations=int(author.parameters.get("randomisations", randomisations)),
                )
            ],
            axis=1,
        )
        readout_a["author_configuration"] = {
            "parameters": dict(author.parameters),
            "source": author.source,
            "date_received": author.date_received,
            "tracked_in_git": author.tracked,
            **_readout_a(author_support, claim_rows),
        }
        if author.tracked:
            readout_a["primary"] = "author_configuration"

    return {
        # **Not written to the fixture** — `main` pops it before writing, so attempt 1's file is
        # byte-for-byte what it was. It is here because readout D′ (attempt 2, §4) needs exactly
        # the default cell's support, per matrix row, and recomputing it there would be a second
        # median over the same draws that could differ from this one.
        "_default_cell_supported": supported_default,
        "primary_variant": primary.name,
        "members": len(members),
        "default_cell_members": len(default),
        "readout_a": readout_a,
        "readout_b": {
            "conditional_on_imputation": conditional,
            "verdict": h10_verdict(conditional["share"]),
            "over_all_claims": _fraction(int(unstable.sum()), len(claim_rows)),
            "isolations": isolations,
            "family_categories": {
                k: int(categories.get(k, 0)) for k in ("durable", "underdetermined", "unsupported")
            },
            "whole_table_supported_default_cell": int(supported_default.sum()),
        },
        "readout_c": anchor["published_draw"],
        "readout_d": {
            symbol: {
                "claims": len(by_symbol.get(symbol, [])),
                "supported": int(
                    sum(
                        1
                        for position in by_symbol.get(symbol, [])
                        if supported_default[claim_rows[position]]
                    )
                ),
            }
            for symbol in targets
        },
        "secondary_variants": {
            v.name: _readout_a(
                np.stack(
                    [
                        run_paired_member(matrix, half, m, v, randomisations=randomisations)
                        for m in default
                    ],
                    axis=1,
                ),
                claim_rows,
            )
            for v in variants
            if v.name != primary.name
        },
        "per_claim_support": {
            "note": (
                "One row per claim, in the exposure's order, holding the primary variant's "
                "support for every member of `members` as 0 or 1 — the raw data, not a summary, "
                "so every readout above is recomputable from this file without re-running."
            ),
            "members": [m.as_dict() for m in members],
            "rows": [
                {
                    "deposit_id": str(claims[i]["deposit_id"]),
                    "published_row": claims[i]["row"],
                    "gene_names": claims[i].get("gene_names"),
                    "row_carries_an_imputed_cell": bool(claim_imputed[i]),
                    "support": [int(x) for x in support[claim_rows[i]]],
                }
                for i in range(len(claim_rows))
            ],
        },
    }


def _symbols_in(cell: str) -> list[str]:
    """S1's gene-name cell as the symbols it names. `;`-separated, as MaxQuant and Perseus write it."""
    return [part.strip() for part in str(cell).split(";") if part.strip()]


def matches_symbol(target: str, cell: str) -> bool:
    """Whether an S1 gene-name cell names `target`. Exact, except for §4's declared prefix rule.

    §4: *"MAGE is matched as any symbol beginning `MAGE`, and that rule is declared as such."* It
    is one symbol and it is named in `DPRIME_PREFIX_SYMBOLS`, so a reader can see that `MAGE` is
    the exception rather than that matching is loose. Everything else is exact after splitting on
    `;` — `pxd018299_differential.py`'s own recorded reason holds here: substring matching lets
    OAS1 hit OASL.
    """
    symbols = _symbols_in(cell)
    if target in DPRIME_PREFIX_SYMBOLS:
        return any(symbol.startswith(target) for symbol in symbols)
    return target in symbols


def dprime_block(
    *,
    targets: Mapping[str, Sequence[str]],
    gene_names: Sequence[str],
    intensity: Sequence[float],
    gene_column: str = "",
    claim_rows: Sequence[int],
    supported: np.ndarray,
) -> dict[str, Any]:
    """Readout D′ (attempt 2, §4): the publication's own named targets, at two grains.

    Three tiers, reported separately because §4 lists them separately and they are different kinds
    of claim — a target in the paper's Results is not the same evidence as one in its Discussion.

    Two grains per target: **any site**, at least one of its S1 peptides supported by the median
    over the default cell's draws, and **largest site**, whether its highest-intensity S1 peptide
    is the supported one. "Highest intensity" is the mean of that peptide's six published log2
    values — §4 says *"highest-intensity"* and not which summary, and the mean over the six is the
    one that uses every column the table publishes.

    **A symbol matching nothing in S1 is `absent_from_s1`, never `not recovered`.** §4 requires
    it, and the distinction is the same one `ONTOLOGY.md` draws everywhere else: a claim the file
    does not carry has no recovery figure, and reporting one as unrecovered would assert a
    measurement over an empty set.

    **D′ decides nothing.** §4 gives it no registered expectation, and no verdict in this module
    reads it.
    """
    tiers: dict[str, Any] = {}
    for tier, symbols in targets.items():
        entries: dict[str, Any] = {}
        for symbol in symbols:
            matched = [i for i, cell in enumerate(gene_names) if matches_symbol(symbol, cell)]
            if not matched:
                entries[symbol] = {"absent_from_s1": True, "sites": 0}
                continue
            calls = [bool(supported[claim_rows[i]]) for i in matched]
            largest = max(
                matched,
                key=lambda i: intensity[i] if intensity[i] == intensity[i] else float("-inf"),
            )
            entries[symbol] = {
                "absent_from_s1": False,
                "sites": len(matched),
                "any_site": any(calls),
                "largest_site": bool(supported[claim_rows[largest]]),
                "largest_site_intensity": float(intensity[largest]),
            }
        tiers[tier] = entries
    return {
        "rule": (
            "Gene symbols matched against S1's own gene-name column, split on ';' and compared "
            "exactly — except MAGE, matched as any symbol beginning 'MAGE', which PREREG attempt "
            "2 §4 declares as such. `any_site` is at least one of the target's S1 peptides "
            "supported by the median over the default cell's draws; `largest_site` is its "
            "highest-intensity S1 peptide, by the mean of that peptide's six published log2 "
            "values. A symbol matching nothing is `absent_from_s1`, never `not recovered`. D′ is "
            "descriptive and decides nothing."
        ),
        "gene_column": gene_column,
        "prefix_matched_symbols": list(DPRIME_PREFIX_SYMBOLS),
        "tiers": tiers,
    }


def _header(
    *,
    anchor_curation: LoadedCuration,
    shotgun_curation: LoadedCuration,
    anchor_supplement: SupplementaryFile,
    gate_supplement: SupplementaryFile,
    generated_at: str,
    anchor_run: bool,
    author: AuthorConfiguration | None,
) -> dict[str, Any]:
    anchor_dataset, shotgun_dataset = _dataset(anchor_curation), _dataset(shotgun_curation)
    return {
        "dataset": str(anchor_dataset["external_accession"]),
        "registration": "walk/PREREG-PXD018299-H10.md",
        "anchor_run": anchor_run,
        "anchor_file": str(anchor_dataset["label"]),
        "anchor_content_hash": str(anchor_dataset["content_hash"]),
        "anchor_published_file": anchor_supplement.filename,
        "anchor_published_content_hash": anchor_supplement.expected_content_hash,
        "gate_file": str(shotgun_dataset["label"]),
        "gate_content_hash": str(shotgun_dataset["content_hash"]),
        "gate_published_file": gate_supplement.filename,
        "gate_published_content_hash": gate_supplement.expected_content_hash,
        "author_parameters_present": author is not None,
        "author_parameters_tracked": None if author is None else author.tracked,
        "note": (
            "PXD018299 under its own named test, as walk/PREREG-PXD018299-H10.md registers it. "
            "Gate G runs first on PXD026748's published Perseus output at s0 = 1 and FDR 0.05; "
            "check A then asks which surviving variant can reach FDR 0.01 on the anchor's 3 "
            "against 3 at all; only then does the family run. Support means q <= 0.01 AND d > 0. "
            "Every claim's support for every member of the primary variant is kept in "
            "`readouts.per_claim_support`, so each readout is recomputable from this file. "
            f"Regenerate with `{GENERATED_BY}`."
        ),
        "generated_by": GENERATED_BY,
        "generated_under": {
            "generated_at": generated_at,
            **_commit(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "anchor_s0": ANCHOR_S0,
            "anchor_fdr": ANCHOR_ALPHA,
            "randomisations": RANDOMISATIONS,
        },
    }


def _attempt_3(
    *,
    gate: Mapping[str, Any],
    anchor: Mapping[str, Any],
    numerator: np.ndarray,
    denominator: np.ndarray,
    anchor_curation: LoadedCuration,
    shotgun_curation: LoadedCuration,
    anchor_supplement: SupplementaryFile,
    gate_supplement: SupplementaryFile,
    generated_at: str,
    started: float,
    fixtures_dir: Path,
    attempt_2_fixture_path: Path,
    targets_fixture_path: Path,
    author: AuthorConfiguration | None,
    members: Sequence[Member],
    randomisations: int = RANDOMISATIONS,
    seeds: Sequence[int] = SEEDS,
    progress: bool = True,
) -> int:
    """`walk/PREREG-PXD018299-H10-attempt3.md` §§2–4, after the gate has run.

    Three things separate it from attempt 2, and they are the three the registration corrects:
    the primary is fixed by §2 rather than chosen by a score, check A is §3's typical draw rather
    than any seed, and §3's rerun consistency compares this run's G2a and G2b against the
    committed attempt-2 fixture before anything else is computed.
    """
    flags = {"validation": ATTEMPT_2_VALIDATION, "matrix": ATTEMPT_3_MATRIX_FLAG}
    header = {
        **_header(
            anchor_curation=anchor_curation,
            shotgun_curation=shotgun_curation,
            anchor_supplement=anchor_supplement,
            gate_supplement=gate_supplement,
            generated_at=generated_at,
            anchor_run=False,
            author=author,
        ),
        "attempt": 3,
        **flags,
    }
    dropped = ("matrix", "claim_rows", "s1_gene_names", "s1_intensity", "s1_gene_column")
    block: dict[str, Any] = {
        **header,
        "gate_g": gate,
        "anchor_matrix": {k: v for k, v in anchor.items() if k not in dropped},
    }
    name = fixture_name_for(3)

    # **§3's rerun consistency, before anything else is computed.** G2a and G2b are deterministic
    # given the seeds, so a difference is not a finding about the anchor — it is the instrument
    # having changed under a registration that assumes it did not.
    earlier = json.loads(attempt_2_fixture_path.read_text(encoding="utf-8"))
    consistency = g2_rerun_consistency(gate, earlier, variants=ATTEMPT_3_VARIANTS)
    if not consistency["consistent"]:
        path = _write(
            fixtures_dir,
            {**block, "g2_rerun_consistency": consistency, "instrument_fault": True},
            name=name,
        )
        print(f"[attempt 3] G2 differs from attempt 2's committed values; stopped. Wrote {path}")
        return 1

    attainability = check_a_typical(
        numerator=numerator,
        denominator=denominator,
        claim_rows=anchor["claim_rows"],
        variants=ATTEMPT_3_VARIANTS,
        randomisations=randomisations,
        seeds=seeds,
        progress=progress,
    )
    admitted = [
        v.name
        for v in ATTEMPT_3_VARIANTS
        if gate["variants"][v.name]["passes"]
        and gate["variants"][v.name]["direction_split"]["passes"]
        and attainability[v.name]["reached"]
    ]
    block = {
        **block,
        "g2_rerun_consistency": consistency,
        "instrument_fault": False,
        "check_a": attainability,
        "admitted_variants": admitted,
        # §2: the primary is named by the registration, so it is recorded whether or not it was
        # admitted. A field that appears only on success would make its absence ambiguous.
        "primary_variant": ATTEMPT_3_PRIMARY.name,
        "primary_admitted": ATTEMPT_3_PRIMARY.name in admitted,
        "secondary_variant": ATTEMPT_3_SECONDARY.name,
    }

    if ATTEMPT_3_PRIMARY.name not in admitted:
        # §3: *"If the primary is not admitted, no readout is reported as primary, and the result
        # is H10 not tested (attempt 3)."* The family does not run at all — the same place
        # attempts 1 and 2 put *"the anchor readouts do not run"*, and a secondary readout with no
        # primary beside it is not something §4 describes.
        path = _write(fixtures_dir, {**block, "h10": ATTEMPT_3_NOT_TESTED}, name=name)
        print(f"[attempt 3] the primary was not admitted; {ATTEMPT_3_NOT_TESTED}. Wrote {path}")
        return 1

    # §4: *"computed for both variants in full"*. Each is run as its own primary, so each gets the
    # whole block rather than readout A alone — which is what attempt 2's secondaries got, and is
    # why its readouts B, D and D′ for these two variants were never seen.
    readouts: dict[str, Any] = {}
    for role, variant in (("primary", ATTEMPT_3_PRIMARY), ("secondary", ATTEMPT_3_SECONDARY)):
        if variant.name not in admitted:
            readouts[role] = {"variant": variant.name, "admitted": False, **flags}
            continue
        family = family_block_for(
            anchor=anchor,
            variants=[variant],
            primary=variant,
            members=list(members),
            targets=_named_targets(targets_fixture_path),
            author=author,
            randomisations=randomisations,
            disclosed=True,
            progress=progress,
        )
        # The default cell's support, taken from the block that just computed it rather than
        # recomputed for D′: the draws are seeded and would agree, but one computation cannot
        # disagree with itself and two can.
        supported = family.pop("_default_cell_supported")
        # `family_block_for` reports every *other* admitted variant's readout A under this key,
        # which for attempt 3 is always empty: each variant is run as its own primary, and the two
        # are siblings at the top level rather than a primary and its secondaries. An empty map
        # here would read as "no secondary was admitted", which is a different statement.
        family.pop("secondary_variants", None)
        family["readout_d_prime"] = dprime_block(
            targets={
                "results_curated": _named_targets(targets_fixture_path),
                "results_not_curated": list(DPRIME_NOT_CURATED),
                "discussion": list(DPRIME_DISCUSSION),
            },
            gene_names=anchor["s1_gene_names"],
            gene_column=anchor["s1_gene_column"],
            intensity=anchor["s1_intensity"],
            claim_rows=anchor["claim_rows"],
            supported=supported,
        )
        readouts[role] = {"variant": variant.name, "admitted": True, **flags, **family}

    # §4: *"H10's verdict is read from the primary only."* The secondary carries its own readout B
    # — that is what makes its imputation-only isolation readable — and it is not the run's
    # verdict.
    verdict = readouts["primary"]["readout_b"]["verdict"]
    elapsed = time.monotonic() - started
    path = _write(
        fixtures_dir,
        {
            **block,
            "anchor_run": True,
            "readouts": readouts,
            "h10": verdict,
            "verdict_read_from": "primary",
            "runtime_seconds": elapsed,
        },
        name=name,
    )
    print(f"[attempt 3] readout A primary {readouts['primary']['readout_a']['default_cell']}")
    print(f"[attempt 3] H10 {verdict['outcome']} (from the primary alone)")
    print(f"[attempt 3] wrote {path} in {elapsed:.1f}s")
    return 0


def _gate_inputs(
    curation: LoadedCuration, deposit: Path, supplement_path: Path
) -> tuple[np.ndarray, list[int], list[int], np.ndarray, list[str], set[str], dict[str, int]]:
    """The shotgun arm through turn 16's pipeline, plus Table 3's calls. IO, no arithmetic of its own."""
    table = maxquant.read_table(deposit)
    rows, column = shotgun_rows(table)
    axes = sample_axes(curation)
    normalised, keep = pipeline(intensity_matrix(rows, column, axes.labels), axes)
    values = normalised[keep]
    accessions = [
        a for a, k in zip((first_accession(r, column) for r in rows), keep, strict=True) if k
    ]

    genotypes = sorted(set(axes.genotype))
    knockout = next((g for g in genotypes if g != "WT"), genotypes[-1])
    wild_type = next(g for g in genotypes if g != knockout)
    calls, call_values = table_3_calls(supplement_path)
    return (
        values,
        list(axes.columns_where(wild_type)),
        list(axes.columns_where(knockout)),
        ~np.isnan(values).any(axis=1),
        accessions,
        calls,
        call_values,
    )


def main(
    *,
    home: Path = HOME,
    fixtures_dir: Path = FIXTURES_DIR,
    anchor_curation_path: Path = ANCHOR_CURATION,
    shotgun_curation_path: Path = SHOTGUN_CURATION,
    cascade_fixture_path: Path = CASCADE_FIXTURE,
    targets_fixture_path: Path = TARGETS_FIXTURE,
    author_parameters_path: Path = AUTHOR_PARAMETERS,
    anchor_supplement: SupplementaryFile = SUPP_DATA_1,
    gate_supplement: SupplementaryFile = SUPP_TABLE_1,
    anchor_deposit_file: Any | None = None,
    randomisations: int = RANDOMISATIONS,
    seeds: Sequence[int] = SEEDS,
    members: Sequence[Member] | None = None,
    repo_root: Path = REPO_ROOT,
    attempt: int = 1,
    progress: bool = True,
) -> int:
    """Gate G, check A, then the anchor family if a variant survives both.

    Every path and both supplements are parameters with real defaults, as turns 13, 15, 16 and 17
    have it, so the tests drive this end to end over synthetic bytes. `members` is injectable for
    the same reason and for one more: the registered family is 360 members and a test does not
    need 360 to establish that the readouts read them.

    **`attempt` selects a registration, and 1 is the default.** Attempt 1 is
    `walk/PREREG-PXD018299-H10.md`, which has already run; attempt 2 is
    `walk/PREREG-PXD018299-H10-attempt2.md`, which replaces only its §1–§3 — the variants, the
    checks and the admission — and adds readout D′. Everything else, including the whole anchor
    path, is attempt 1's and is not re-specified here. The two write different files and attempt 2
    labels every result block `in-sample`, because §1's convention was fitted on the table its
    gate is scored against.

    **Attempt 3** is `walk/PREREG-PXD018299-H10-attempt3.md`, and it corrects exactly one thing:
    attempt 2's registered primary was degenerate. Its check A admitted a variant that reached the
    threshold under *one* favourable seed and supported nothing in a typical draw, and its tie
    rule then made that variant primary — so H10's registered verdict came from a claim set with
    almost nothing in it. Attempt 3 names its primary by principle, strengthens check A to the
    median over the twenty seeds, computes every readout for both its variants, and checks its own
    G2a and G2b against attempt 2's committed figures before it computes anything. All three
    attempts write different files, and none overwrites another's.
    """
    registered = variants_for(attempt)
    attempt_2 = attempt == 2
    attempt_3 = attempt == 3
    #: Attempt 3 keeps attempt 2's convention and its two checks, so everything `attempt_2` gates
    #: — the direction split, the orientation probe, the `in-sample` label — is on for it too.
    directional = attempt_2 or attempt_3
    started = time.monotonic()
    generated_at = datetime.now(UTC).isoformat()

    shotgun_curation, _, _ = _parse_arm(shotgun_curation_path, home)
    shotgun_deposit = _deposit_for(shotgun_curation, home)
    assert shotgun_deposit is not None  # `_parse_arm` raised if it were not
    gate_path = _supplement_path(gate_supplement, home)
    values, wt_columns, ko_columns, complete, accessions, calls, call_values = _gate_inputs(
        shotgun_curation, shotgun_deposit, gate_path
    )
    if directional and not orientation_holds(values, wt_columns, ko_columns):
        raise H10Error(
            "the probe says `direction > 0` is not `higher in WT` under the argument order this "
            "module uses. G2b's two bands would silently exchange places, so the run stops."
        )
    gate = gate_block(
        values=values,
        wt_columns=wt_columns,
        ko_columns=ko_columns,
        complete=complete,
        accessions=accessions,
        calls=calls,
        call_values=call_values,
        randomisations=randomisations,
        seeds=seeds,
        variants=registered,
        direction=directional,
        progress=progress,
    )
    print(
        f"[gate] {sum(1 for v in gate['variants'].values() if v['passes'])} of "
        f"{len(registered)} variant(s) pass; "
        f"{gate['complete_case_published_calls']:,} complete-case published call(s)"
    )

    anchor_curation = _load_anchor(anchor_curation_path)
    deposit_declaration = anchor_deposit_file or PXD018299_SITES
    assert deposit_declaration.expected_content_hash is not None
    anchor_deposit = verify(
        deposit_declaration.expected_content_hash,
        filename=deposit_declaration.filename,
        home=home,
    )
    anchor = anchor_block(
        deposit=maxquant.read_table(anchor_deposit),
        supplement_path=_supplement_path(anchor_supplement, home),
        cascade=json.loads(cascade_fixture_path.read_text(encoding="utf-8")),
    )

    numerator = anchor["matrix"][:, :3]
    denominator = anchor["matrix"][:, 3:]

    if attempt_3:
        return _attempt_3(
            gate=gate,
            anchor=anchor,
            numerator=numerator,
            denominator=denominator,
            anchor_curation=anchor_curation,
            shotgun_curation=shotgun_curation,
            anchor_supplement=anchor_supplement,
            gate_supplement=gate_supplement,
            generated_at=generated_at,
            started=started,
            fixtures_dir=fixtures_dir,
            attempt_2_fixture_path=fixtures_dir / FIXTURE_NAME_ATTEMPT_2,
            targets_fixture_path=targets_fixture_path,
            author=read_author_parameters(author_parameters_path, repo_root=repo_root),
            members=list(members) if members is not None else list(family_members()),
            randomisations=randomisations,
            seeds=seeds,
            progress=progress,
        )

    passing = [v for v in registered if gate["variants"][v.name]["passes"]]
    attainability = (
        check_a(
            numerator=numerator,
            denominator=denominator,
            variants=passing,
            randomisations=randomisations,
            seeds=seeds,
            progress=progress,
        )
        if passing
        else {}
    )
    attainability = {
        v.name: attainability.get(v.name, {"reached": False, "seed": None}) for v in registered
    }
    admitted = admitted_variants(gate, attainability, variants=registered, direction=attempt_2)
    primary = primary_variant(admitted, gate, variants=registered)

    author = read_author_parameters(author_parameters_path, repo_root=repo_root)
    header = _header(
        anchor_curation=anchor_curation,
        shotgun_curation=shotgun_curation,
        anchor_supplement=anchor_supplement,
        gate_supplement=gate_supplement,
        generated_at=generated_at,
        anchor_run=primary is not None,
        author=author,
    )
    # **Dropped from the written block**, all four for the same reason: they are inputs to readout
    # D′ (attempt 2) or to the family, not figures. `s1_gene_column` is among them because adding
    # it would have put a key in attempt 1's `anchor_matrix` that attempt 1 never had — caught by
    # the byte-identity test, which is what that test is for. D′ reports it instead.
    dropped = ("matrix", "claim_rows", "s1_gene_names", "s1_intensity", "s1_gene_column")
    block: dict[str, Any] = {
        **header,
        "gate_g": gate,
        "check_a": attainability,
        "admitted_variants": admitted,
        "primary_variant": primary,
        "anchor_matrix": {k: v for k, v in anchor.items() if k not in dropped},
    }
    if attempt_2:
        block = {**block, "attempt": 2, "validation": ATTEMPT_2_VALIDATION}

    name = fixture_name_for(attempt)
    if primary is None:
        result = f"named test not reproduced{' (attempt 2)' if attempt_2 else ''}"
        path = _write(fixtures_dir, {**block, "result": result}, name=name)
        print(f"[h10] no variant admitted; the anchor readouts did not run. Wrote {path}")
        return 1

    family = family_block_for(
        anchor=anchor,
        variants=[v for v in registered if v.name in admitted],
        primary=next(v for v in registered if v.name == primary),
        members=list(members) if members is not None else list(family_members()),
        targets=_named_targets(targets_fixture_path),
        author=author,
        randomisations=randomisations,
        progress=progress,
    )
    if attempt_2:
        family = {
            **family,
            "validation": ATTEMPT_2_VALIDATION,
            "readout_d_prime": dprime_block(
                targets={
                    "results_curated": _named_targets(targets_fixture_path),
                    "results_not_curated": list(DPRIME_NOT_CURATED),
                    "discussion": list(DPRIME_DISCUSSION),
                },
                gene_names=anchor["s1_gene_names"],
                gene_column=anchor["s1_gene_column"],
                intensity=anchor["s1_intensity"],
                claim_rows=anchor["claim_rows"],
                supported=family["_default_cell_supported"],
            ),
        }
    family.pop("_default_cell_supported", None)
    elapsed = time.monotonic() - started
    path = _write(
        fixtures_dir, {**block, "readouts": family, "runtime_seconds": elapsed}, name=name
    )
    print(
        f"[h10] readout A {family['readout_a']['default_cell']['supported']:,} of {anchor['exposure']:,}"
    )
    print(f"[h10] readout B {family['readout_b']['verdict']}")
    print(f"[h10] wrote {path} in {elapsed:.1f}s")
    return 0


def _attempt_from_argv(argv: Sequence[str]) -> int:
    """`--attempt N` off the command line, defaulting to 1.

    A hand-rolled read rather than `argparse`: this entry point takes exactly one flag, and the
    default has to be attempt 1 so that `python -m bzk.sources.pxd018299_h10` keeps meaning what
    it meant when attempt 1 ran.
    """
    for index, token in enumerate(argv):
        if token == "--attempt" and index + 1 < len(argv):
            return int(argv[index + 1])
        if token.startswith("--attempt="):
            return int(token.split("=", 1)[1])
    return 1


if __name__ == "__main__":  # pragma: no cover - the entry point
    sys.exit(main(attempt=_attempt_from_argv(sys.argv[1:])))
