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
on someone's disk is not a record. The run asks `git ls-files --error-unmatch` and records the
answer either way. **H10's verdict never reads this file** — readout B stays on the registered
default cell, as v8's rule requires and §6 B repeats.
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
from bzk.stats.perseus_s0 import SCHEMES, SIDEDNESS, perseus_s0

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


#: §4's eight, in the order the section lists them — sidedness outermost, scheme inner. The order
#: is load-bearing: *"Ties go to the earlier variant in the list above."*
VARIANTS = tuple(Variant(s, c) for s in SIDEDNESS for c in SCHEMES)


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
    progress: bool = True,
) -> dict[str, Any]:
    """§4's gate, over all eight variants. Pure.

    **The imputation is computed once per seed and shared by the eight variants.** They differ in
    how the null is drawn, not in the matrix they see, and imputing eight times per seed would be
    eight different matrices wearing one seed's name as well as eight times the work.

    The complete-case restriction is the gate's whole point (§4): a protein with no missing value
    cannot be moved by the draw, so its call is comparable with a published one without choosing a
    seed.
    """
    target = np.array([a in calls for a in accessions], dtype=bool)
    counts = {variant.name: np.zeros(values.shape[0], dtype=int) for variant in VARIANTS}
    for index, seed in enumerate(seeds):
        filled = downshifted_normal(
            values,
            downshift_sd=DEFAULT_DOWNSHIFT_SD,
            width_sd=DEFAULT_WIDTH_SD,
            seed=seed,
            scope=DEFAULT_SCOPE,
        ).values
        for variant in VARIANTS:
            outcome = perseus_s0(
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
        if progress:
            print(f"[gate] seed {index + 1:>2}/{len(seeds)}", end="\r")
    if progress:
        print()

    variants: dict[str, Any] = {}
    for variant in VARIANTS:
        called = counts[variant.name] >= gate_majority(seeds)
        metrics = gate_metrics(called[complete], target[complete])
        passes = (
            metrics["precision"]["share"] is not None
            and metrics["recall"]["share"] is not None
            and metrics["precision"]["share"] >= GATE_MIN_PRECISION
            and metrics["recall"]["share"] >= GATE_MIN_RECALL
        )
        variants[variant.name] = {
            **metrics,
            "called_complete_case": int(called[complete].sum()),
            "passes": bool(passes),
        }

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
        "variants": variants,
        "passes": any(v["passes"] for v in variants.values()),
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


def admitted_variants(gate: Mapping[str, Any], attainability: Mapping[str, Any]) -> list[str]:
    """§4: those passing both G and A, in the list's own order."""
    return [
        v.name
        for v in VARIANTS
        if gate["variants"][v.name]["passes"] and attainability[v.name]["reached"]
    ]


def primary_variant(names: Sequence[str], gate: Mapping[str, Any]) -> str | None:
    """§4: the admitted variant with the highest G F1, ties to the earlier one in `VARIANTS`.

    The tie-break is positional and not alphabetical, because §4 says *"the earlier variant in the
    list above"* and that list is `VARIANTS`' own order. An F1 of `None` — a variant that called
    nothing — cannot win; it is not scored zero, which would rank it against variants whose F1
    exists.
    """
    order = {v.name: i for i, v in enumerate(VARIANTS)}
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
    """
    try:
        done = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(path)],
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


def _write(fixtures_dir: Path, fixture: Mapping[str, Any]) -> Path:
    path = fixtures_dir / FIXTURE_NAME
    path.write_text(json.dumps(fixture, indent=2) + "\n")
    return path


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
    progress: bool = True,
) -> dict[str, Any]:
    """§6's readouts A to D, plus H10's verdict. The family runs here."""
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

    readout_a = {
        "default_cell": _readout_a(support, claim_rows),
        "primary": "default_cell",
        "compared_with": {"welch_based_recovery": 512, "significance_losses": 237},
    }
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
    progress: bool = True,
) -> int:
    """Gate G, check A, then the anchor family if a variant survives both.

    Every path and both supplements are parameters with real defaults, as turns 13, 15, 16 and 17
    have it, so the tests drive this end to end over synthetic bytes. `members` is injectable for
    the same reason and for one more: the registered family is 360 members and a test does not
    need 360 to establish that the readouts read them.
    """
    started = time.monotonic()
    generated_at = datetime.now(UTC).isoformat()

    shotgun_curation, _, _ = _parse_arm(shotgun_curation_path, home)
    shotgun_deposit = _deposit_for(shotgun_curation, home)
    assert shotgun_deposit is not None  # `_parse_arm` raised if it were not
    gate_path = _supplement_path(gate_supplement, home)
    values, wt_columns, ko_columns, complete, accessions, calls, call_values = _gate_inputs(
        shotgun_curation, shotgun_deposit, gate_path
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
        progress=progress,
    )
    print(
        f"[gate] {sum(1 for v in gate['variants'].values() if v['passes'])} of {len(VARIANTS)} "
        f"variant(s) pass; {gate['complete_case_published_calls']:,} complete-case published call(s)"
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
    passing = [v for v in VARIANTS if gate["variants"][v.name]["passes"]]
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
        v.name: attainability.get(v.name, {"reached": False, "seed": None}) for v in VARIANTS
    }
    admitted = admitted_variants(gate, attainability)
    primary = primary_variant(admitted, gate)

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
    block = {
        **header,
        "gate_g": gate,
        "check_a": attainability,
        "admitted_variants": admitted,
        "primary_variant": primary,
        "anchor_matrix": {k: v for k, v in anchor.items() if k not in ("matrix", "claim_rows")},
    }

    if primary is None:
        path = _write(fixtures_dir, {**block, "result": "named test not reproduced"})
        print(f"[h10] no variant admitted; the anchor readouts did not run. Wrote {path}")
        return 1

    family = family_block_for(
        anchor=anchor,
        variants=[v for v in VARIANTS if v.name in admitted],
        primary=next(v for v in VARIANTS if v.name == primary),
        members=list(members) if members is not None else list(family_members()),
        targets=_named_targets(targets_fixture_path),
        author=author,
        randomisations=randomisations,
        progress=progress,
    )
    elapsed = time.monotonic() - started
    path = _write(fixtures_dir, {**block, "readouts": family, "runtime_seconds": elapsed})
    print(
        f"[h10] readout A {family['readout_a']['default_cell']['supported']:,} of {anchor['exposure']:,}"
    )
    print(f"[h10] readout B {family['readout_b']['verdict']}")
    print(f"[h10] wrote {path} in {elapsed:.1f}s")
    return 0


if __name__ == "__main__":  # pragma: no cover - the entry point
    sys.exit(main())
