"""Measure H5c and H9p of `HYPOTHESIS.md` §5, both registered in v6 before measurement.

`python -m bzk.sources.pxd026748_h5c_h9p`, after both deposits and the supplement are in the
content store and `tests/fixtures/pxd026748_reconstruction.json` is committed. Writes
`tests/fixtures/pxd026748_h5c_h9p.json`.

**Two hypotheses, one run, because they share every input.** H5c asks whether the publication's own
citation flag tracks H9s's durability; H9p asks whether the imputation underdetermination H9s found
at site grain is smaller at protein grain. Both read the committed reconstruction fixture, the
pinned supplement and the two deposits, and H9p's site-grain half is H5c's durability read a
second way — running them together is what keeps the two from disagreeing about the same 288
claims.

**Nothing here re-implements turn 16.** `sheet_rows`, `resolve_column`, `sample_axes`,
`intensity_matrix`, `pipeline`, `shotgun_rows`, `first_accession`, `read_table_2_ids`,
`family_members` and `run_member` are imported from `bzk/sources/pxd026748_reconstruction.py`. A
second copy of any of them would be a second population wearing the same name, which is the failure
that module's own docstrings name.

**H5c never runs the family, and that is a property rather than an economy.** Its durability comes
from the committed fixture's per-claim `min_p`, recomputed into categories and **checked against
the counts the fixture stores** before anything downstream reads them. A rerun would sample new
draws from the same grid and give slightly different categories, so a rerun could not corroborate
the fixture — it would replace it, silently, inside a hypothesis about that fixture's contents.
`tests/test_pxd026748_h5c_h9p.py` holds a spy on `run_member` that fails if the H5c path calls it.

**The registered thresholds are read once each, at the point of verdict.** H5c's ±0.10 and H9p's
0.5 and 0.8 appear in `h5c_verdict` and `h9p_verdict` and nowhere else; every proportion above them
is computed without reference to them. The declared confound — how many of a claim's twelve values
were missing before imputation — is computed, reported by group, and **never read by either
verdict**; `HYPOTHESIS.md` §5 calls it descriptive and this module holds it to that.
"""

from __future__ import annotations

import collections
import hashlib
import json
import platform
import sys
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
from bzk.sources.protein_groups import SupplementaryFile
from bzk.sources.pxd026748_ingest_figures import _parse_arm
from bzk.sources.pxd026748_published_cascade import (
    HEADER_MARKERS,
    SUPP_SHEET,
    SUPP_TABLE_1,
    _commit,
)
from bzk.sources.pxd026748_reconstruction import (
    PRIMARY_THRESHOLD,
    SampleAxes,
    _fraction,
    family_members,
    first_accession,
    intensity_matrix,
    pipeline,
    read_table_2_ids,
    resolve_column,
    run_member,
    sample_axes,
    sheet_rows,
    shotgun_rows,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
CURATION_DIR = REPO_ROOT / "data" / "curation"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"
HOME = Path.home() / ".bzk-omics"

DIGLY_CURATION = CURATION_DIR / "curation_PXD026748.json"
SHOTGUN_CURATION = CURATION_DIR / "curation_PXD026748_shotgun.json"
RECONSTRUCTION_FIXTURE = FIXTURES_DIR / "pxd026748_reconstruction.json"
FIXTURE_NAME = "pxd026748_h5c_h9p.json"

GENERATED_BY = "python -m bzk.sources.pxd026748_h5c_h9p"

#: H5c's population. *"Cluster 3's ubiquitin sites are excluded, because the flag concerns ISG15
#: targets"* — `HYPOTHESIS.md` §5, H5c. Named here so the exclusion is one edit rather than a
#: condition spelled at each use.
ISG15_CLUSTERS = ("Cluster 1a", "Cluster 1b", "Cluster 2")

#: H5c's registered directions, **inclusive at both ends**. §5 writes *"at least +0.10"* and *"at
#: most −0.10"*, with the middle band *"between −0.10 and +0.10, exclusive"*, so a difference of
#: exactly ±0.10 belongs to the outer verdicts. The three readings agree; this module states which
#: one it applies because a boundary case decides a registered hypothesis.
H5C_THRESHOLD = 0.10

#: H9p's registered directions. `U_p <= 0.5 * U_s` is particular to site data; `U_p >= 0.8 * U_s`
#: is general to the imputation step; between them, indeterminate.
H9P_PARTICULAR_FACTOR = 0.5
H9P_GENERAL_FACTOR = 0.8

#: The published column H5c's groups come from, and the value that means flagged. The column is
#: located by content (`resolve_column`) rather than by position; `x` is §5's own spelling.
FLAG_REQUIRED = ("invivo", "isg15")
FLAG_VALUE = "x"

#: Table 1's own row key, and H5c's join column. Named rather than spelled inline because
#: `_normalise` reduces it to the empty string, so it cannot be located by content the way every
#: other column here is — it is matched literally, and its absence is a named refusal.
ROW_NUMBER_COLUMN = "#"

#: How a published cell becomes a flag. **Chosen here — §5 says only that the column *is* `x`.**
#: Surrounding whitespace is stripped and case is ignored, and every distinct cell value found is
#: reported beside the counts, so a reader can see whether either allowance mattered. A cell that
#: is empty, `None` or anything else is not flagged.
FLAG_RULE = (
    "A claim is flagged when its Table 1 `In vivo ISG15 targets` cell, stripped of surrounding "
    "whitespace and lowercased, is exactly 'x'. HYPOTHESIS.md v6 states the value as `x` and "
    "states no normalisation, so the stripping and the case-folding are this module's and are "
    "auditable from `flag_values_as_found`, which counts every distinct cell value the column "
    "actually held. Anything else — empty, absent, or another mark — is not flagged; no cell is "
    "read as flagged by being non-empty."
)

#: The join H5c uses between the supplement and the reconstruction fixture. Published row number,
#: not the accession: `#` is unique per published row and a site accession is not.
JOIN_RULE = (
    "A committed claim joins the published row whose `#` equals the claim's `published_row`. The "
    "row number rather than the accession, because Supplementary Table 1 carries several rows per "
    "protein and `#` is its own row key. Both sides are compared as integers. A claim that joins "
    "no row, or more than one, stops the run: H5c's groups are defined by a published column, and "
    "a claim with no published row has no group."
)


class HypothesisError(ValueError):
    """An input cannot support the hypothesis as registered. Never downgraded to a warning."""


# ── reading the committed reconstruction ────────────────────────────────────────────────────────


def _row_number(value: object) -> int:
    """One published row number as an integer. `openpyxl` returns `1.0` where Excel stored a
    number, and `'1'` where it stored text; both are the same row."""
    if isinstance(value, bool):
        raise HypothesisError(f"row number {value!r} is a boolean, which names no row")
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError) as exc:
        raise HypothesisError(f"row number {value!r} is not an integer") from exc


def recomputed_categories(
    claims: Sequence[Mapping[str, Any]], *, member_count: int, threshold: float = PRIMARY_THRESHOLD
) -> list[dict[str, Any]]:
    """`{support, category}` per claim, recomputed from the stored per-member `min_p`.

    Durable is supported in **all** members, unsupported in none, underdetermined in between —
    `HYPOTHESIS.md` §5's own definition, applied to the fixture's numbers rather than to its
    conclusions. A `null` min(P), which the reconstruction writes for a claim with no row in the
    filtered population, clears no threshold and so counts as unsupported.
    """
    found: list[dict[str, Any]] = []
    for claim in claims:
        values = claim.get("min_p")
        if not isinstance(values, list) or len(values) != member_count:
            raise HypothesisError(
                f"claim {claim.get('deposit_id')!r} carries {0 if values is None else len(values)} "
                f"min(P) value(s) against {member_count} member(s); the fixture and its own member "
                "list disagree, and a support count over the wrong denominator is not a support "
                "count"
            )
        support = sum(1 for v in values if v is not None and v < threshold)
        category = (
            "durable"
            if support == member_count
            else ("unsupported" if support == 0 else "underdetermined")
        )
        found.append({"support": support, "category": category})
    return found


def fixture_consistency(fixture: Mapping[str, Any]) -> dict[str, Any]:
    """Recompute the fixture's categories and check them against the counts it stores.

    **This runs before anything reads durability, and a disagreement stops the run.** H5c is a
    statement about the committed fixture's contents; if the file's stored counts and its own
    per-claim numbers have parted company, then which of the two H5c is about is undecided, and
    measuring either would be choosing silently.
    """
    if not fixture.get("gg_run"):
        raise HypothesisError(
            "the reconstruction fixture records `gg_run: false`, so its gate failed and it carries "
            "no family. H5c's durability and H9p's site-grain half both come from that family."
        )
    family = fixture["family"]
    member_count = len(family["members"])
    recomputed = recomputed_categories(family["claims"], member_count=member_count)
    counts = collections.Counter(entry["category"] for entry in recomputed)
    stored = family["readouts"]["primary"]["counts"]
    recounted = {name: int(counts.get(name, 0)) for name in stored}
    if recounted != dict(stored):
        raise HypothesisError(
            f"recomputing the fixture's categories from its own per-claim min(P) gives {recounted}, "
            f"against the {dict(stored)} it stores. The file disagrees with itself, so which of the "
            "two H5c is about is undecided. Regenerate the fixture rather than reading either."
        )
    return {
        "members": member_count,
        "claims": len(family["claims"]),
        "recomputed_counts": recounted,
        "stored_counts": dict(stored),
        "agrees": True,
    }


# ── reading the published flag ──────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PublishedFlags:
    """The flag column, by published row number, with every value it actually held."""

    column: str
    flagged: dict[int, bool]
    values_as_found: dict[str, int]


def published_flags(
    source: Path | bytes, *, sheet: str = SUPP_SHEET, flag_column: str | None = None
) -> PublishedFlags:
    """Table 1's `In vivo ISG15 targets`, keyed by `#`. The header is located by content.

    A duplicated `#` raises: the join is on that column, and keeping one of two rows would decide
    silently which published row a claim's group came from.
    """
    rows = sheet_rows(source, sheet=sheet, markers=HEADER_MARKERS)
    if not rows:
        raise HypothesisError(f"sheet {sheet!r} has a header and no data rows")
    column = flag_column or resolve_column(
        list(rows[0]),
        required=list(FLAG_REQUIRED),
        forbidden=[],
        what="Table 1's in vivo ISG15 target flag",
    )
    if ROW_NUMBER_COLUMN not in rows[0]:
        raise HypothesisError(
            f"sheet {sheet!r} has no {ROW_NUMBER_COLUMN!r} column; its header reads "
            f"{list(rows[0])}. {JOIN_RULE}"
        )
    flagged: dict[int, bool] = {}
    values: collections.Counter[str] = collections.Counter()
    for row in rows:
        number = _row_number(row.get(ROW_NUMBER_COLUMN))
        if number in flagged:
            raise HypothesisError(
                f"Supplementary Table 1 carries row number {number} more than once; the join "
                "H5c uses is on that column and cannot choose between two rows"
            )
        cell = row.get(column)
        values["" if cell is None else str(cell)] += 1
        flagged[number] = str(cell).strip().lower() == FLAG_VALUE if cell is not None else False
    return PublishedFlags(
        column=column, flagged=flagged, values_as_found=dict(sorted(values.items()))
    )


# ── H5c ─────────────────────────────────────────────────────────────────────────────────────────


#: How far off a registered threshold still counts as on it, for both hypotheses. **Chosen here, and it is not a
#: loosening of the threshold.** The difference is a subtraction of two rationals in binary
#: floating point, where `0.5 - 0.4` is `0.09999999999999998`: a boundary case that is exactly
#: +0.10 in arithmetic can arrive here 2e-17 below it, and a registered direction decided by the
#: representation rather than by the data is not the registered direction. The slack is safe
#: because the differences are rationals over group sizes: with at most 288 claims per group, two
#: distinct achievable differences are at least 1/(288 x 288) ~ 1.2e-5 apart, four orders of
#: magnitude above this, so no pair of genuinely different results can be merged by it. H9p's two
#: factors are compared with the same slack for the same reason — see `h9p_verdict`.
THRESHOLD_TOLERANCE = 1e-9


def h5c_verdict(difference: float) -> str:
    """H5c's registered directions, inclusive at ±0.10. The **only** reader of `H5C_THRESHOLD`."""
    if difference >= H5C_THRESHOLD - THRESHOLD_TOLERANCE:
        return "discriminates"
    if difference <= -H5C_THRESHOLD + THRESHOLD_TOLERANCE:
        return "inverted"
    return "does_not_discriminate"


def missing_counts(
    claims: Sequence[Mapping[str, Any]], values: np.ndarray, row_of_id: Mapping[str, int]
) -> list[int | None]:
    """Each claim's missing values out of twelve, after log2 and before imputation.

    The declared confound. `None` where the claim's deposit row is not in the filtered population,
    which is not the same as zero — the reconstruction records that case separately and so does
    this.
    """
    found: list[int | None] = []
    for claim in claims:
        index = row_of_id.get(str(claim["deposit_id"]))
        found.append(None if index is None else int(np.isnan(values[index]).sum()))
    return found


def h5c_block(
    *,
    claims: Sequence[Mapping[str, Any]],
    categories: Sequence[Mapping[str, Any]],
    flags: PublishedFlags,
    values: np.ndarray,
    axes: SampleAxes,
    row_of_id: Mapping[str, int],
) -> dict[str, Any]:
    """H5c, end to end over already-read inputs. Pure, and it never runs a family member.

    `values` and `axes` are here for the confound alone — the count of missing values in each
    claim's GG row. They are deliberately the same matrix turn 16 imputed, so "missing before
    imputation" means the same thing in both places; and `run_member` is in this module's namespace
    precisely so a test can prove it is not called from here.
    """
    joined = []
    for claim, category in zip(claims, categories, strict=True):
        number = _row_number(claim["published_row"])
        if number not in flags.flagged:
            raise HypothesisError(
                f"claim {claim['deposit_id']!r} names published row {number}, which Supplementary "
                f"Table 1 does not carry. {JOIN_RULE}"
            )
        # Named fields rather than `**dict(claim)`: a committed claim carries its 360 `min_p`
        # values, and copying them here would duplicate the reconstruction fixture's whole matrix
        # inside this one. What the figures were computed from is the support count and the
        # category, both recomputed above, and the source matrix is pinned by
        # `reconstruction_fixture_hash`.
        joined.append(
            {
                "deposit_id": str(claim["deposit_id"]),
                "published_row": number,
                "cluster": claim.get("cluster"),
                "uniprot_id": claim.get("uniprot_id"),
                "lysine_position": claim.get("lysine_position"),
                **dict(category),
                "flagged": flags.flagged[number],
            }
        )

    missing = missing_counts(claims, values, row_of_id)
    for entry, count in zip(joined, missing, strict=True):
        entry["missing_values"] = count

    population = [e for e in joined if str(e["cluster"]) in ISG15_CLUSTERS]
    groups: dict[str, list[dict[str, Any]]] = {
        "flagged": [e for e in population if e["flagged"]],
        "unflagged": [e for e in population if not e["flagged"]],
    }
    proportions = {
        name: _fraction(sum(1 for e in members if e["category"] == "durable"), len(members))
        for name, members in groups.items()
    }
    flagged_share = proportions["flagged"]["share"]
    unflagged_share = proportions["unflagged"]["share"]
    difference = (
        None
        if flagged_share is None or unflagged_share is None
        else flagged_share - unflagged_share
    )
    return {
        "population": {
            "clusters": list(ISG15_CLUSTERS),
            "excluded_cluster": "Cluster 3",
            "claims": len(population),
            "excluded_claims": len(joined) - len(population),
            "by_cluster": dict(
                sorted(collections.Counter(str(e["cluster"]) for e in population).items())
            ),
        },
        "flag": {
            "rule": FLAG_RULE,
            "column": flags.column,
            "join_rule": JOIN_RULE,
            "values_as_found": flags.values_as_found,
        },
        "group_sizes": {name: len(members) for name, members in groups.items()},
        "durable_proportion": proportions,
        "difference": difference,
        "verdict": ("undefined" if difference is None else h5c_verdict(difference)),
        "undefined_reason": (
            None
            if difference is not None
            else "one of the two groups is empty, so it has no durable proportion to difference"
        ),
        # Descriptive, and read by no verdict: HYPOTHESIS.md §5 declares the confound and declares
        # it descriptive in the same sentence.
        "confound_missing_values": {
            "note": (
                "Each claim's count of missing values in its GG row out of twelve, after log2 and "
                "before imputation. Declared in HYPOTHESIS.md v6 as descriptive; it enters no "
                "verdict here, and `tests/test_pxd026748_h5c_h9p.py` holds that two runs with the "
                "same durability and different missing counts give the same verdict."
            ),
            "by_group": {
                name: dict(
                    sorted(
                        collections.Counter(
                            "absent" if e["missing_values"] is None else str(e["missing_values"])
                            for e in members
                        ).items()
                    )
                )
                for name, members in groups.items()
            },
        },
        "claims": joined,
    }


# ── H9p ─────────────────────────────────────────────────────────────────────────────────────────


def _category(support: int, member_count: int) -> str:
    if support == member_count:
        return "durable"
    return "unsupported" if support == 0 else "underdetermined"


def h9p_verdict(u_p: Mapping[str, Any], u_s: Mapping[str, Any]) -> dict[str, Any]:
    """H9p's registered directions. The **only** reader of the two factors.

    `undefined` where either denominator is zero, with the reason named: a proportion over no
    claims is not a small proportion, and comparing one would be a division rather than a finding.
    """
    if not u_p["denominator"] or not u_s["denominator"]:
        empty = [
            name for name, figures in (("U_p", u_p), ("U_s", u_s)) if not figures["denominator"]
        ]
        return {
            "outcome": "undefined",
            "reason": (
                f"{' and '.join(empty)} has no claims with a missing value, so the conditional "
                "proportion it names does not exist. H9p's comparison is conditional on "
                "missingness (HYPOTHESIS.md v6), and an unconditional substitute would be a "
                "different hypothesis."
            ),
            "particular_at_or_below": None,
            "general_at_or_above": None,
        }
    particular = H9P_PARTICULAR_FACTOR * u_s["share"]
    general = H9P_GENERAL_FACTOR * u_s["share"]
    # The same slack, for the same reason, and **this boundary was not hypothetical**: the test
    # that asserts the registered factors failed first on `U_p = 0.64` against `0.8 * 0.8`, which
    # is `0.6400000000000001`. Both figures are rationals over the two group sizes, so distinct
    # achievable comparisons are at least 1/(5 * 600 * 288) ~ 1.2e-6 apart — three orders of
    # magnitude above this — and nothing genuinely different can be merged by it.
    if u_p["share"] <= particular + THRESHOLD_TOLERANCE:
        outcome = "particular_to_site_data"
    elif u_p["share"] >= general - THRESHOLD_TOLERANCE:
        outcome = "general_to_imputation"
    else:
        outcome = "indeterminate"
    return {
        "outcome": outcome,
        "reason": None,
        "particular_at_or_below": particular,
        "general_at_or_above": general,
    }


def _conditional(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """The underdetermined proportion among rows carrying at least one missing value."""
    with_missing = [r for r in rows if (r["missing_values"] or 0) > 0]
    return _fraction(
        sum(1 for r in with_missing if r["category"] == "underdetermined"), len(with_missing)
    )


def h9p_block(
    *,
    proteins: Sequence[Mapping[str, Any]],
    sites: Sequence[Mapping[str, Any]],
    join: Mapping[str, Any],
) -> dict[str, Any]:
    """H9p, over per-protein and per-site rows that each carry `category` and `missing_values`.

    Pure, and conditional by construction: `_conditional` is the only thing the verdict reads.
    The unconditional proportions are computed and reported beside it, as §5 requires, and are
    never compared with each other by anything here.
    """
    u_p, u_s = _conditional(proteins), _conditional(sites)
    return {
        "join": dict(join),
        "exposure": len(proteins),
        "site_claims": len(sites),
        "conditional": {"u_p": u_p, "u_s": u_s},
        "verdict": h9p_verdict(u_p, u_s),
        # Reported and never read: §5 lists these as descriptive, and an unconditional comparison
        # would be settled by the protein arm's complete rows alone, which is the reason H9p was
        # registered conditional.
        "descriptive": {
            "unconditional_underdetermined": {
                "protein": _fraction(
                    sum(1 for r in proteins if r["category"] == "underdetermined"), len(proteins)
                ),
                "site": _fraction(
                    sum(1 for r in sites if r["category"] == "underdetermined"), len(sites)
                ),
            },
            "complete_rows": {
                "protein": sum(1 for r in proteins if (r["missing_values"] or 0) == 0),
                "site": sum(1 for r in sites if (r["missing_values"] or 0) == 0),
            },
        },
        "proteins": [dict(r) for r in proteins],
    }


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


def gg_matrix(
    curation: LoadedCuration, adapter: Any, deposit: Path
) -> tuple[np.ndarray, dict[str, int], SampleAxes, int]:
    """`(values, row_of_id, axes, population_rows)` — turn 16's GG path, step for step.

    The population is the site adapter's own `_filter` output, including rows the platform refused
    at ingestion; the matrix is that population's summed intensities through `pipeline`, and
    `values` is the surviving rows. Written as one function because H5c's confound and H9p's U_s
    both need it and must not be able to disagree about it.
    """
    table = maxquant.read_table(deposit)
    column = {name: i for i, name in enumerate(table.header)}
    population, _, _ = adapter._filter(table, column)
    axes = sample_axes(curation)
    normalised, keep = pipeline(intensity_matrix(population, column, axes.labels), axes)
    kept_ids = [
        str(row[column["id"]]).strip() for row, k in zip(population, keep, strict=True) if k
    ]
    return normalised[keep], {row_id: i for i, row_id in enumerate(kept_ids)}, axes, len(population)


def shotgun_family(
    curation: LoadedCuration,
    deposit: Path,
    table_2_ids: Sequence[str],
    *,
    progress: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """H9p's exposure and its 360-member support counts, over the shotgun arm.

    The family runs over the **whole** filtered matrix and the exposure is read off it, not over
    the exposure alone: `whole_matrix` scope draws from the population's own mean and standard
    deviation, so imputing a subset would impute from a different distribution than the
    reconstruction did.
    """
    table = maxquant.read_table(deposit)
    rows, column = shotgun_rows(table)
    axes = sample_axes(curation)
    normalised, keep = pipeline(intensity_matrix(rows, column, axes.labels), axes)
    values = normalised[keep]

    accessions = [first_accession(row, column) for row in rows]
    leading = collections.Counter(accessions)
    kept_accessions = [a for a, k in zip(accessions, keep, strict=True) if k]
    index_of = {a: i for i, a in enumerate(kept_accessions)}

    exposure: list[dict[str, Any]] = []
    unmatched: list[str] = []
    ambiguous: list[str] = []
    not_reaching: list[str] = []
    for accession in table_2_ids:
        if leading[accession] > 1:
            ambiguous.append(accession)
        elif accession not in leading:
            unmatched.append(accession)
        elif accession not in index_of:
            not_reaching.append(accession)
        else:
            exposure.append({"accession": accession, "row": index_of[accession]})

    members = family_members()
    support = np.zeros(len(exposure), dtype=int)
    positions = [e["row"] for e in exposure]
    for i, member in enumerate(members):
        min_p = run_member(values, axes, member)
        support += (min_p[positions] < PRIMARY_THRESHOLD).astype(int)
        if progress:
            print(f"[h9p] member {i + 1:>3}/{len(members)}", end="\r")
    if progress:
        print()

    proteins = [
        {
            "accession": entry["accession"],
            "support": int(count),
            "category": _category(int(count), len(members)),
            "missing_values": int(np.isnan(values[entry["row"]]).sum()),
        }
        for entry, count in zip(exposure, support.tolist(), strict=True)
    ]
    join = {
        "table_2_ids_read": len(table_2_ids),
        "exposure": len(exposure),
        "unmatched": len(unmatched),
        "ambiguous": len(ambiguous),
        "not_reaching_the_test": len(not_reaching),
        "unmatched_ids": unmatched,
        "ambiguous_ids": ambiguous,
        "not_reaching_ids": not_reaching,
        "members": len(members),
        "rows_after_filters": len(rows),
        "rows_reaching_the_test": int(keep.sum()),
    }
    return proteins, join


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main(
    *,
    home: Path = HOME,
    fixtures_dir: Path = FIXTURES_DIR,
    digly_curation_path: Path = DIGLY_CURATION,
    shotgun_curation_path: Path = SHOTGUN_CURATION,
    reconstruction_fixture_path: Path = RECONSTRUCTION_FIXTURE,
    supplement: SupplementaryFile = SUPP_TABLE_1,
    table_1_flag_column: str | None = None,
    table_2_id_column: str | None = None,
    progress: bool = True,
) -> int:
    """H5c and H9p over the real inputs, written as one fixture.

    Every path is a parameter with a real default, as turns 13, 15 and 16 have it, so the tests
    drive this end to end over synthetic bytes. The two column overrides exist for the same reason
    turn 16's do: the published sheets' header spellings are in no document this repository holds,
    and `resolve_column` refuses by name rather than guessing.
    """
    generated_at = datetime.now(UTC).isoformat()

    fixture = json.loads(reconstruction_fixture_path.read_text(encoding="utf-8"))
    consistency = fixture_consistency(fixture)
    family = fixture["family"]
    claims = family["claims"]
    categories = recomputed_categories(claims, member_count=consistency["members"])

    digly_curation, digly_adapter, _ = _parse_arm(digly_curation_path, home)
    shotgun_curation, _, _ = _parse_arm(shotgun_curation_path, home)
    digly_deposit = _deposit_for(digly_curation, home)
    shotgun_deposit = _deposit_for(shotgun_curation, home)
    assert digly_deposit is not None and shotgun_deposit is not None  # `_parse_arm` raised if not

    supplement_path = _supplement_path(supplement, home)
    flags = published_flags(supplement_path, flag_column=table_1_flag_column)
    table_2_ids = read_table_2_ids(supplement_path, id_column=table_2_id_column)

    values, row_of_id, axes, population_rows = gg_matrix(
        digly_curation, digly_adapter, digly_deposit
    )
    h5c = h5c_block(
        claims=claims,
        categories=categories,
        flags=flags,
        values=values,
        axes=axes,
        row_of_id=row_of_id,
    )

    proteins, join = shotgun_family(
        shotgun_curation, shotgun_deposit, table_2_ids, progress=progress
    )
    sites = [
        {
            "deposit_id": str(c["deposit_id"]),
            "cluster": c["cluster"],
            "support": entry["support"],
            "category": entry["category"],
            "missing_values": missing,
        }
        for c, entry, missing in zip(
            claims, categories, missing_counts(claims, values, row_of_id), strict=True
        )
    ]
    h9p = h9p_block(proteins=proteins, sites=sites, join=join)

    digly_dataset, shotgun_dataset = _dataset(digly_curation), _dataset(shotgun_curation)
    written = {
        "dataset": str(digly_dataset["external_accession"]),
        "registration": "HYPOTHESIS.md §5, H5c and H9p (registered v6, unchanged in v7)",
        "published_file": supplement.filename,
        "published_content_hash": supplement.expected_content_hash,
        "published_sheets": [SUPP_SHEET, "Table 2"],
        "digly_file": str(digly_dataset["label"]),
        "digly_content_hash": str(digly_dataset["content_hash"]),
        "shotgun_file": str(shotgun_dataset["label"]),
        "shotgun_content_hash": str(shotgun_dataset["content_hash"]),
        "reconstruction_fixture": reconstruction_fixture_path.name,
        "reconstruction_fixture_hash": _digest(reconstruction_fixture_path),
        "note": (
            "H5c and H9p of HYPOTHESIS.md §5, both registered in v6 before measurement. H5c's "
            "durability is recomputed from the committed reconstruction fixture's per-claim "
            "min(P) and checked against the counts that fixture stores; the family is never "
            "re-run for it. H9p runs the same 360 members over the shotgun arm's filtered, "
            "normalised LFQ matrix and compares underdetermination at the two grains, "
            "conditional on missingness as registered. Each claim and each exposure protein "
            "carries the support count and the missing-value count every figure was computed "
            f"from. Regenerate with `{GENERATED_BY}`."
        ),
        "generated_by": GENERATED_BY,
        "generated_under": {
            "generated_at": generated_at,
            **_commit(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "primary_threshold": PRIMARY_THRESHOLD,
            "gg_population_rows": population_rows,
            "fixture_consistency": consistency,
        },
        "h5c": h5c,
        "h9p": {**h9p, "sites": sites},
    }
    path = fixtures_dir / FIXTURE_NAME
    path.write_text(json.dumps(written, indent=2) + "\n")

    print(
        f"[h5c] flagged {h5c['group_sizes']['flagged']:,} / unflagged "
        f"{h5c['group_sizes']['unflagged']:,} of {h5c['population']['claims']:,} ISG15 claim(s)"
    )
    print(
        f"[h5c] durable {h5c['durable_proportion']['flagged']['numerator']}/"
        f"{h5c['durable_proportion']['flagged']['denominator']} flagged, "
        f"{h5c['durable_proportion']['unflagged']['numerator']}/"
        f"{h5c['durable_proportion']['unflagged']['denominator']} unflagged; "
        f"difference {h5c['difference']}"
    )
    print(f"[h5c] verdict {h5c['verdict']}")
    print(
        f"[h9p] exposure {join['exposure']:,} protein(s); unmatched {join['unmatched']:,}, "
        f"not reaching the test {join['not_reaching_the_test']:,}, ambiguous {join['ambiguous']:,}"
    )
    print(
        f"[h9p] U_p {h9p['conditional']['u_p']['numerator']}/"
        f"{h9p['conditional']['u_p']['denominator']}, U_s "
        f"{h9p['conditional']['u_s']['numerator']}/{h9p['conditional']['u_s']['denominator']}"
    )
    print(f"[h9p] verdict {h9p['verdict']['outcome']}")
    print(f"[hypotheses] wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
