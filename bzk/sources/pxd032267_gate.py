"""Run `walk/PREREG-PXD032267-gate.md`: the pinning check, gate G, and readouts A to D.

`python -m bzk.sources.pxd032267_gate`, on bzk's Mac, after both deposit files can be fetched.
Writes `tests/fixtures/pxd032267_gate.json`. **Not run in the build turn**: no deposit bytes exist
in that container, and the registration's single attempt (§7) is not spent on a build.

**The registration is the specification and this module implements it, in its order.** The
pinning check (§2), the population (§2), the values and the valid-value rule (§3), gate G (§4),
then — only when G passes or is *not separated* — readouts A to D (§5). Its §6 expectations are
not inputs: Y1 to Y8 appear nowhere here, as X1 to X8 appear nowhere in
`bzk/sources/pxd018299_h10.py`. The registered *rules* are implemented; the registered *guesses*
are for the reviewer to score.

**The template is `bzk/sources/pxd018299_h10.py`, and its conventions are reused, not re-derived.**
The imputation grid, `Member` and `SEEDS` come from `pxd026748_reconstruction.py`, as H10 takes
them; *instability* and D7's verdict with its boundary slack are H10's own functions, because §5 B
is *"H10's definition, unchanged"*; the author-parameter rule is H10's, with this instrument's
key set (below); `generated_under` follows `pxd018299_published_cascade.py`. The test is
`bzk/stats/tukey.py`, validated against R before this module existed.

**Published values are read at run time from `walk/PXD032267-published-tables.json`**, the only
home of Tables 7 and 8, and never copied into this module. The deposit facts the pinning check and
the join compare against are read from `walk/walk_PXD032267.json` § `deposit_read` in the same way.

**Every reading this module takes where the registration is silent is marked `[reading]`** in the
docstring of the function that takes it, and the build turn's report lists them all.

## `walk/PXD032267-author-parameters.json`

Registration lines 21–25 adopt H10's author-parameter rule unchanged. The schema here is H10's
with **this instrument's keys**: the test is parametric, so H10's `randomisations` and `scheme`
have no meaning and are refused by name like any other unknown key.

```json
{
  "source": "who stated them, when, and in what form",
  "date_received": "2026-12-01",
  "width_sd": 0.3,
  "downshift_sd": 1.8,
  "scope": "per_sample",
  "seed": 0
}
```

Only a file **tracked in git at the run's commit** becomes readout A's primary, with the default
cell beside it; an untracked one is reported and ignored (`pxd018299_h10.is_tracked`, l.1050).
Readout B's verdict never reads it: the author configuration is an added readout B line.
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
from bzk.sources.pride import PXD032267_PARAMETERS, PXD032267_SITES, DepositFile
from bzk.sources.pxd018299_h10 import (
    ABSENT_AT_OR_BELOW,
    RECURS_AT_OR_ABOVE,
    AuthorConfiguration,
    h10_verdict,
    instability,
    is_tracked,
)
from bzk.sources.pxd026748_published_cascade import _commit
from bzk.sources.pxd026748_reconstruction import (
    DEFAULT_DOWNSHIFT_SD,
    DEFAULT_SCOPE,
    DEFAULT_WIDTH_SD,
    DOWNSHIFT_SDS,
    SCOPES,
    SEEDS,
    WIDTH_SDS,
    Member,
    _fraction,
    family_members,
    log2_zero_as_missing,
)
from bzk.stats import downshifted_normal
from bzk.stats.tukey import VARIANTS, cell_name, tukey

REPO_ROOT = Path(__file__).resolve().parents[2]
WALK_DIR = REPO_ROOT / "walk"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"
HOME = Path.home() / ".bzk-omics"

REGISTRATION = WALK_DIR / "PREREG-PXD032267-gate.md"
PUBLISHED_TABLES = WALK_DIR / "PXD032267-published-tables.json"
WALK_RECORD = WALK_DIR / "walk_PXD032267.json"
AUTHOR_PARAMETERS = WALK_DIR / "PXD032267-author-parameters.json"
FIXTURE_NAME = "pxd032267_gate.json"
GENERATED_BY = "python -m bzk.sources.pxd032267_gate"

# ── constants transcribed from the registration, each guarded against its text ──────────────────
# `tests/test_pxd032267_gate.py` parses every number below out of `REGISTRATION` and compares it to
# the constant, in the pattern of `graph.I4_LABELS`' guard. Full rules, not half-rules.

#: §4 *Input check*: *"to |Δ| ≤ 1e-5"*, on every gate row.
INPUT_TOLERANCE = 1e-5

#: §4 *The rule*: a variant passes if *"on every gate row, |p − published `p_value`| ≤ 1e-4"*. The
#: same 1e-4 decides *not separated*: two passing variants *"within 1e-4 of each other on every gate
#: row"*.
P_TOLERANCE = 1e-4

#: §4 *Too few gate rows*: *"if there are fewer than two, G is **undeterminable**"*.
MIN_GATE_ROWS = 2

#: §4's table, in its order; table order breaks exact ties in the primary. One home, in the test.
GATE_VARIANTS = VARIANTS

#: §3 *Imputation family: the H10 grid, unchanged*. Imported from where H10 takes them, so the two
#: instruments cannot drift; the guard checks the registration against these names.
GRID_WIDTH_SDS = WIDTH_SDS
GRID_DOWNSHIFT_SDS = DOWNSHIFT_SDS
GRID_SCOPES = SCOPES
DEFAULT_CELL = (DEFAULT_WIDTH_SD, DEFAULT_DOWNSHIFT_SD, DEFAULT_SCOPE)

#: §3 *"20 draws per cell, with draw k using seed k"*. **[reading]** seeds 0–19: the registration
#: gives no range, and `pxd026748_reconstruction.SEEDS` is the house convention H10 also used.
DRAW_SEEDS = SEEDS

#: §3's candidates, strictest first: at least 3, 2, then 1 valid values in at least one of the
#: four cells.
VALID_VALUE_CANDIDATES = (3, 2, 1)

#: §1 and §5 B/C: up is *p < 0.05 and Difference > 0.585*; down is *p < 0.05 and Difference <
#: −0.585*. Both halves of each rule are the constant pair; neither is ever applied alone.
SUPPORT_ALPHA = 0.05
SUPPORT_DIFFERENCE = 0.585

#: §5 A *near*: *"outside that range but within ±25% of the median"* — of the median of the 20
#: draws' counts, not of the range's ends or the mean.
NEAR_FRACTION = 0.25

#: §5 B: *recurs* at least 5%, *absent* at most 1%, *indeterminate* between. H10's own constants,
#: because §5 B is H10's definition unchanged; `h10_verdict` applies them with H10's slack.
RECURS_AT_OR_ABOVE_SHARE = RECURS_AT_OR_ABOVE
ABSENT_AT_OR_BELOW_SHARE = ABSENT_AT_OR_BELOW

#: §5 C: the named target, as Table 8 names it.
READOUT_C_TARGET = ("Filamin-C", 2590)

# ── the design ──────────────────────────────────────────────────────────────────────────────────

#: The twelve samples as deposited. `TCA` in the KO labels is the deposit's own spelling and is not
#: corrected (`deposit_read.site_table.samples`).
SAMPLES = (
    "KOC1",
    "KOC2",
    "KOC3",
    "KOTCA1",
    "KOTCA2",
    "KOTCA3",
    "WtC1",
    "WtC2",
    "WtC3",
    "WtTAC1",
    "WtTAC2",
    "WtTAC3",
)
GENOTYPE = np.array(["KO"] * 6 + ["WT"] * 6)
SURGERY = np.array((["control"] * 3 + ["TAC"] * 3) * 2)
CELLS = tuple(cell_name(g, s) for g in ("WT", "KO") for s in ("control", "TAC"))

INTENSITY_PREFIX = "Intensity "
IDENTIFICATION_PREFIX = "Identification type "
MATCHED = "By matching"


@dataclass(frozen=True)
class Comparison:
    """One of Table 7's three comparisons. Difference is mean(`first`) − mean(`second`)."""

    key: str
    published_label: str
    first: str
    second: str


#: Table 7's rows, in its order. **[reading]** for the two KO comparisons: Table 8's positive
#: values fix *"X vs Y" = mean(X) − mean(Y)* for WT TAC vs WT control only; the same convention is
#: applied to the other two.
COMPARISONS = (
    Comparison("wt_tac_vs_wt_control", "Wildtype TAC vs. wildtype control", "WT:TAC", "WT:control"),
    Comparison("ko_tac_vs_ko_control", "Isg15-/- TAC vs. Isg15-/- control", "KO:TAC", "KO:control"),
    Comparison("ko_tac_vs_wt_tac", "Isg15-/- TAC vs. wildtype TAC", "KO:TAC", "WT:TAC"),
)
GATE_COMPARISON = COMPARISONS[0]
READOUT_C_COMPARISON = COMPARISONS[2]
DIRECTIONS = ("up", "down")

#: The author-parameter keys this instrument accepts. **Not H10's set**: `randomisations` and
#: `scheme` have no meaning for a parametric test and are refused by name.
AUTHOR_PARAMETER_KEYS = ("width_sd", "downshift_sd", "scope", "seed")
AUTHOR_REQUIRED_KEYS = ("source", "date_received")


class GateError(ValueError):
    """The inputs cannot be read as the registration describes. Never a warning (`CLAUDE.md`)."""


# ── the inputs this module reads but does not own ───────────────────────────────────────────────


@dataclass(frozen=True)
class PublishedClaim:
    """One Table 8 row, as `walk/PXD032267-published-tables.json` transcribes it."""

    protein_name: str
    position: int
    glygly_probabilities: str
    p_value: float
    difference: float

    @property
    def label(self) -> str:
        return f"{self.protein_name} K{self.position}"


@dataclass(frozen=True)
class Published:
    """Tables 7 and 8, plus the supplement's digest they were transcribed from."""

    claims: tuple[PublishedClaim, ...]
    table_7: dict[str, dict[str, int]]
    source_sha256: str


@dataclass(frozen=True)
class DepositFacts:
    """What `deposit_read` counted, which the pinning check and the join compare against."""

    data_rows: int
    columns: int
    reverse: int
    joined_ids: tuple[int, ...]


def load_published(path: Path = PUBLISHED_TABLES) -> Published:
    payload = json.loads(path.read_text(encoding="utf-8"))
    claims = tuple(
        PublishedClaim(
            protein_name=str(r["protein_name"]),
            position=int(r["position"]),
            glygly_probabilities=str(r["glygly_probabilities"]),
            p_value=float(r["p_value"]),
            difference=float(r["difference"]),
        )
        for r in payload["table_8"]["rows"]
    )
    table_7 = {
        str(r["comparison"]): {"up": int(r["up"]), "down": int(r["down"])}
        for r in payload["table_7"]["rows"]
    }
    return Published(claims=claims, table_7=table_7, source_sha256=str(payload["source"]["sha256"]))


def load_deposit_facts(path: Path = WALK_RECORD) -> DepositFacts:
    read = json.loads(path.read_text(encoding="utf-8"))["deposit_read"]
    site = read["site_table"]
    return DepositFacts(
        data_rows=int(site["data_rows"]),
        columns=int(site["columns"]),
        reverse=int(site["population"]["reverse"]),
        joined_ids=tuple(int(r["id"]) for r in read["join_to_published_claims"]["rows"]),
    )


# ── 1. the pinning check (§2) ───────────────────────────────────────────────────────────────────


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _digest_record(path: Path, deposit: DepositFile) -> dict[str, Any]:
    """The digest, and what it was compared against — which, while the declaration is `None`, is
    nothing. Said in the output rather than implied by an absent field."""
    digest = _sha256(path)
    expected = deposit.expected_content_hash
    if expected is not None and digest != expected:
        raise GateError(
            f"{deposit.accession}/{deposit.filename} hashes to {digest}, not the declared "
            f"{expected}. §2: the run must establish that its file is the one read; it is not."
        )
    return {
        "file": deposit.filename,
        "content_hash": digest,
        "declared_content_hash": expected,
        "compared": expected is not None,
        "comparison": (
            "matches the declared digest"
            if expected is not None
            else "no digest is declared (bzk/sources/pride.py: None, deliberately): this digest is "
            "recorded, not compared. Pin it from this report."
        ),
    }


def pinning_check(
    sites_path: Path,
    parameters_path: Path,
    *,
    facts: DepositFacts,
    sites_deposit: DepositFile = PXD032267_SITES,
    parameters_deposit: DepositFile = PXD032267_PARAMETERS,
) -> tuple[maxquant.MaxQuantTable, dict[str, Any]]:
    """§2: hash both files, and require 1,440 data rows, 171 columns and 14 reverse rows.

    The three counts are `maxquant.read_table`'s, compared to `deposit_read`'s. **[reading]** the
    raw newline count is recorded beside them: `deposit_read` counted non-empty lines in a
    browser, and `read_table` drops spill lines, so if the two ever differ the record shows by
    how much without the check having to choose between them. A mismatch raises.
    """
    digests = {
        "sites": _digest_record(sites_path, sites_deposit),
        "parameters": _digest_record(parameters_path, parameters_deposit),
    }
    table = maxquant.read_table(sites_path)
    reverse_column = table.column("Reverse")
    reverse = sum(1 for r in table.rows if r[reverse_column].strip() == "+")
    measured = {"data_rows": len(table.rows), "columns": len(table.header), "reverse": reverse}
    expected = {"data_rows": facts.data_rows, "columns": facts.columns, "reverse": facts.reverse}
    if measured != expected:
        raise GateError(
            f"the site table is not the file deposit_read counted: measured {measured}, expected "
            f"{expected}. §2: a mismatch stops the run."
        )
    return table, {
        **digests,
        "measured": measured,
        "expected_from_deposit_read": expected,
        "raw_newlines": sites_path.read_bytes().count(b"\n"),
        "spill_lines": table.spill_lines,
    }


# ── 2–3. population and values (§2, §3) ─────────────────────────────────────────────────────────


def population(table: maxquant.MaxQuantTable) -> list[list[str]]:
    """§2: every row except reverse decoys. Contaminants and low-localisation rows are kept."""
    reverse_column = table.column("Reverse")
    return [r for r in table.rows if r[reverse_column].strip() != "+"]


def values_matrix(table: maxquant.MaxQuantTable, rows: Sequence[Sequence[str]]) -> np.ndarray:
    """§3: log2 of the twelve `Intensity <sample>` columns, zero as missing."""
    column = {name: i for i, name in enumerate(table.header)}
    for sample in SAMPLES:
        table.column(INTENSITY_PREFIX + sample)
    raw = np.array(
        [
            [maxquant.cell_value(r, column, INTENSITY_PREFIX + sample) or 0.0 for sample in SAMPLES]
            for r in rows
        ],
        dtype=float,
    ).reshape(len(rows), len(SAMPLES))
    return log2_zero_as_missing(raw)


def matched_mask(table: maxquant.MaxQuantTable, rows: Sequence[Sequence[str]]) -> np.ndarray:
    """Readout D's mask: cells whose `Identification type <sample>` is `By matching`."""
    indices = [table.column(IDENTIFICATION_PREFIX + s) for s in SAMPLES]
    return np.array([[r[i].strip() == MATCHED for i in indices] for r in rows], dtype=bool).reshape(
        len(rows), len(SAMPLES)
    )


# ── 4. the join (Table 8 to the deposit) ────────────────────────────────────────────────────────


def _positions(cell: str) -> set[str]:
    return {p.strip() for p in cell.split(";") if p.strip()}


def join(
    table: maxquant.MaxQuantTable,
    rows: Sequence[Sequence[str]],
    claims: Sequence[PublishedClaim],
    *,
    expected_ids: Sequence[int],
) -> tuple[list[int], list[dict[str, Any]]]:
    """Each Table 8 claim to one population row, by two keys computed independently. **[reading]**

    - **Key P (peptide):** `GlyGly (K) Probabilities` equals the published string, and the
      published position is in `Positions within proteins`.
    - **Key N (name)**, the walk record's rule: the published protein name is contained in
      `Protein names`, and the position is present as for key P.

    **The join takes a row R when every key that matched finds R, and at least one of them finds
    only R. Otherwise it raises.** One key alone finding exactly one row is enough; key N is
    substring containment and may over-match, and then key P decides. Both exist because an
    exact-string key can fail on formatting, and a raise here ends the registered attempt — §7
    allows a second only for faults caught by §2 or §4. The joined `id`s must then equal the walk
    record's, in order, or it raises: the guard either key passes through.
    """
    probabilities = table.column("GlyGly (K) Probabilities")
    names = table.column("Protein names")
    positions = table.column("Positions within proteins")
    ids = table.column("id")
    joined: list[int] = []
    record: list[dict[str, Any]] = []
    for claim in claims:
        position = str(claim.position)
        at_position = [i for i, r in enumerate(rows) if position in _positions(r[positions])]
        key_p = [i for i in at_position if rows[i][probabilities] == claim.glygly_probabilities]
        key_n = [i for i in at_position if claim.protein_name in rows[i][names]]
        matched = [k for k in (key_p, key_n) if k]
        found = {
            "claim": claim.label,
            "key_p_ids": [int(rows[i][ids]) for i in key_p],
            "key_n_ids": [int(rows[i][ids]) for i in key_n],
        }
        if not matched:
            raise GateError(f"{claim.label}: neither key P nor key N finds a row. {found}")
        common = set.intersection(*(set(k) for k in matched))
        taken = {k[0] for k in matched if len(k) == 1} & common
        if len(taken) != 1:
            raise GateError(
                f"{claim.label}: the keys do not agree on one row — every key that matched must "
                f"find it, and one must find only it. {found}"
            )
        row = taken.pop()
        joined.append(row)
        record.append(
            {
                **found,
                "joined_id": int(rows[row][ids]),
                "decided_by": [n for n, k in (("P", key_p), ("N", key_n)) if k == [row]],
            }
        )
    joined_ids = [int(rows[i][ids]) for i in joined]
    if joined_ids != list(expected_ids):
        raise GateError(
            f"the join found ids {joined_ids}, not deposit_read's {list(expected_ids)} in Table 8 "
            "order. The claims are not the rows the registration was written against."
        )
    return joined, record


# ── 5–6. the valid-value rule and the matrix that is imputed (§3) ───────────────────────────────


def _cell_columns(cell: str) -> np.ndarray:
    genotype, surgery = cell.split(":")
    return np.flatnonzero((GENOTYPE == genotype) & (SURGERY == surgery))


def valid_value_choice(
    matrix: np.ndarray,
    *,
    claim_rows: Sequence[int],
    claims: Sequence[PublishedClaim],
    candidates: Sequence[int] = VALID_VALUE_CANDIDATES,
) -> dict[str, Any]:
    """§3: the strictest candidate retaining all ten claims, over the four cells.

    Every candidate's retained count is recorded whichever is taken. **[reading]** where no
    candidate retains all of them, the one retaining the most is taken and the claims it loses are
    named — `pxd018299_h10.valid_value_choice`'s fallback (l.649–650), **including its tie-break**:
    among candidates retaining equally many, the least strict. §2 says claims that fail leave the
    exposure and are reported. The case arises under readout D's masking.
    """
    measured = ~np.isnan(matrix)
    best_cell = np.max(
        np.stack([measured[:, _cell_columns(c)].sum(axis=1) for c in CELLS], axis=1), axis=1
    )
    reported: dict[str, Any] = {}
    keeps: dict[int, np.ndarray] = {}
    for minimum in candidates:
        keep = best_cell >= minimum
        keeps[minimum] = keep
        retained = [i for i, row in enumerate(claim_rows) if bool(keep[row])]
        reported[str(minimum)] = {
            "rows_retained": int(keep.sum()),
            "claims_retained": len(retained),
            "retains_every_claim": len(retained) == len(claim_rows),
        }
    taken = next(
        (m for m in candidates if reported[str(m)]["retains_every_claim"]),
        max(candidates, key=lambda m: (reported[str(m)]["claims_retained"], -m)),
    )
    keep = keeps[taken]
    return {
        "candidates": reported,
        "taken": taken,
        "retains_every_claim": bool(reported[str(taken)]["retains_every_claim"]),
        "claims_lost": [
            c.label for c, row in zip(claims, claim_rows, strict=True) if not keep[row]
        ],
        "_keep": keep,
    }


def filtered(
    matrix: np.ndarray, keep: np.ndarray, claim_rows: Sequence[int]
) -> tuple[np.ndarray, list[int | None]]:
    """The rows that reach imputation, and each claim's row in them (`None` where lost).

    **[reading, following the H10 convention]** imputation runs over the filtered rows only, so
    `per_sample` statistics are over the filtered matrix: `pxd018299_h10.py` applies the
    valid-value filter (l.1219–1229, `matrix = normalised[keep]` at l.1229) before `run_paired_member`
    imputes it (l.942).
    """
    position = np.cumsum(keep) - 1
    return matrix[keep], [int(position[r]) if keep[r] else None for r in claim_rows]


# ── 7. gate G (§4) ──────────────────────────────────────────────────────────────────────────────


def _float(x: float) -> float | None:
    return None if not np.isfinite(x) else float(x)


def differences(matrix: np.ndarray, comparison: Comparison) -> np.ndarray:
    """Difference for *"X vs Y"*: mean(X) − mean(Y), per row, over log2 values."""
    first, second = _cell_columns(comparison.first), _cell_columns(comparison.second)
    return np.asarray(matrix[:, first].mean(axis=1) - matrix[:, second].mean(axis=1))


def score_variants(
    p_by_variant: Mapping[str, np.ndarray], published_p: np.ndarray
) -> dict[str, Any]:
    """§4 *The rule*, over p-values already computed. Pure, so every branch is reachable.

    - A variant passes if |Δp| ≤ 1e-4 on every gate row.
    - The **primary** is the passing variant with the smallest maximum |Δp|, table order breaking
      exact ties only.
    - Every pair of passing variants is reported with its largest gap over the gate rows.
    - **The trigger is the registration's:** `not_separated` when **any** two passing variants are
      within 1e-4 of each other on every gate row, whether or not the primary is one of them.
    - **[reading]** the set the readouts run under is the primary plus every variant in any such
      close pair, so under `not_separated` they always run under more than one, as the
      registration's *"under both"* requires.
    """
    published_p = np.asarray(published_p, dtype=float)
    per_variant: dict[str, Any] = {}
    passing: list[str] = []
    worst: dict[str, float] = {}
    for variant in GATE_VARIANTS:
        if variant not in p_by_variant:
            continue
        p = np.asarray(p_by_variant[variant], dtype=float)
        delta = np.abs(p - published_p)
        passes = bool(np.all(delta <= P_TOLERANCE))
        worst[variant] = float(np.max(delta)) if delta.size else float("nan")
        per_variant[variant] = {
            "p": [_float(x) for x in p],
            "abs_delta_p": [_float(x) for x in delta],
            "max_abs_delta_p": _float(worst[variant]),
            "passes": passes,
        }
        if passes:
            passing.append(variant)
    gaps: dict[str, float | None] = {}
    close: list[tuple[str, str]] = []
    for i, v in enumerate(passing):
        for w in passing[i + 1 :]:
            gap = np.abs(
                np.asarray(p_by_variant[v], dtype=float) - np.asarray(p_by_variant[w], dtype=float)
            )
            largest = float(np.max(gap))
            gaps[f"{v}-{w}"] = _float(largest)
            if bool(np.all(gap <= P_TOLERANCE)):
                close.append((v, w))
    if not passing:
        return {
            "variants": per_variant,
            "passing": [],
            "primary": None,
            "pairwise_max_gap": {},
            "close_pairs": [],
            "readout_variants": [],
            "status": "not_reproduced",
        }
    primary = min(passing, key=lambda v: (worst[v], GATE_VARIANTS.index(v)))
    in_close = {v for pair in close for v in pair}
    readout_variants = [primary] + [v for v in GATE_VARIANTS if v in in_close and v != primary]
    return {
        "variants": per_variant,
        "passing": passing,
        "primary": primary,
        "pairwise_max_gap": gaps,
        "close_pairs": [list(pair) for pair in close],
        "readout_variants": readout_variants,
        "status": "not_separated" if close else "passed",
    }


def gate_g(
    matrix: np.ndarray, claim_rows: Sequence[int], claims: Sequence[PublishedClaim]
) -> dict[str, Any]:
    """§4, in this order. **[reading on the order]**

    1. **Gate rows:** Table 8 claims measured (non-zero) in all twelve samples. Fewer than two
       gives `undeterminable` and the variants are not scored — but **the input check still runs
       on whatever gate rows exist, and its result is recorded beside the status**, against §4's
       *"Nothing downstream runs"*: if the authors' matrix is not the deposit's, that matters more
       than the row count, and a new registration written without knowing it would be wasted.
    2. **Input check:** the published Difference to |Δ| ≤ 1e-5 on every gate row; a failure is
       `input_not_reproduced`.
    3. **The variants**, scored by `score_variants`.
    """
    complete = [i for i, row in enumerate(claim_rows) if not np.isnan(matrix[row]).any()]
    gate_matrix = matrix[[claim_rows[i] for i in complete]]
    computed = differences(gate_matrix, GATE_COMPARISON)
    rows = []
    for k, i in enumerate(complete):
        delta = abs(float(computed[k]) - claims[i].difference)
        rows.append(
            {
                "claim": claims[i].label,
                "published_difference": claims[i].difference,
                "computed_difference": float(computed[k]),
                "abs_delta": delta,
                "passes": delta <= INPUT_TOLERANCE,
            }
        )
    input_check = {
        "rows_checked": len(rows),
        "tolerance": INPUT_TOLERANCE,
        "rows": rows,
        "passed": all(r["passes"] for r in rows) if rows else None,
    }
    block: dict[str, Any] = {
        "gate_rows": [claims[i].label for i in complete],
        "gate_row_count": len(complete),
        "minimum_gate_rows": MIN_GATE_ROWS,
        "input_check": input_check,
    }
    if len(complete) < MIN_GATE_ROWS:
        return {
            **block,
            "status": "undeterminable",
            "result": "gate rows insufficient",
            "primary": None,
            "readout_variants": [],
        }
    if not input_check["passed"]:
        return {
            **block,
            "status": "input_not_reproduced",
            "result": "input not reproduced",
            "primary": None,
            "readout_variants": [],
        }
    result = tukey(
        gate_matrix,
        GENOTYPE,
        SURGERY,
        pairs=[(GATE_COMPARISON.first, GATE_COMPARISON.second)],
    ).pair(GATE_COMPARISON.first, GATE_COMPARISON.second)
    scored = score_variants(
        {v: result.p[v] for v in GATE_VARIANTS},
        np.array([claims[i].p_value for i in complete]),
    )
    labels = {
        "passed": "G passes",
        "not_separated": "G passes, not separated",
        "not_reproduced": "named test not reproduced",
    }
    return {**block, **scored, "result": labels[scored["status"]]}


# ── 8. the readouts (§5) ────────────────────────────────────────────────────────────────────────


def support(
    filled: np.ndarray,
    variant: str,
    *,
    comparisons: Sequence[Comparison] = COMPARISONS,
) -> dict[tuple[str, str], np.ndarray]:
    """Per row, whether each comparison × direction is supported under `variant`.

    Up is p < 0.05 **and** Difference > 0.585; down is p < 0.05 **and** Difference < −0.585. The
    p-value is computed only for rows whose |Difference| clears 0.585 in some comparison, because
    no other row can be supported and `studentized_range.sf` costs milliseconds per value; each
    row's p is independent of every other row's, so the restriction changes no outcome.
    """
    diffs = {c.key: differences(filled, c) for c in comparisons}
    candidate = np.zeros(filled.shape[0], dtype=bool)
    for d in diffs.values():
        candidate |= np.abs(d) > SUPPORT_DIFFERENCE
    p_values = {c.key: np.full(filled.shape[0], np.nan) for c in comparisons}
    if candidate.any():
        result = tukey(
            filled[candidate],
            GENOTYPE,
            SURGERY,
            pairs=[(c.first, c.second) for c in comparisons],
            variants=(variant,),
        )
        for c in comparisons:
            p_values[c.key][candidate] = result.pair(c.first, c.second).p[variant]
    out: dict[tuple[str, str], np.ndarray] = {}
    with np.errstate(invalid="ignore"):
        for c in comparisons:
            significant = p_values[c.key] < SUPPORT_ALPHA
            out[(c.key, "up")] = significant & (diffs[c.key] > SUPPORT_DIFFERENCE)
            out[(c.key, "down")] = significant & (diffs[c.key] < -SUPPORT_DIFFERENCE)
    return out


def run_members(
    matrix: np.ndarray,
    members: Sequence[Member],
    variant: str,
    *,
    rows: Sequence[int] | None = None,
    comparisons: Sequence[Comparison] = COMPARISONS,
) -> dict[tuple[str, str], np.ndarray]:
    """Support for every member, as rows × members per comparison × direction.

    Each member imputes the **whole** matrix with `downshifted_normal` — the imputation's own
    statistics are over every row — and `rows`, if given, restricts only which rows are then
    tested.
    """
    columns: dict[tuple[str, str], list[np.ndarray]] = collections.defaultdict(list)
    for member in members:
        filled = downshifted_normal(
            matrix,
            downshift_sd=member.downshift_sd,
            width_sd=member.width_sd,
            seed=member.seed,
            scope=member.scope,
        ).values
        chosen = filled if rows is None else filled[list(rows)]
        for key, value in support(chosen, variant, comparisons=comparisons).items():
            columns[key].append(value)
    return {key: np.stack(value, axis=1) for key, value in columns.items()}


def default_cell_members() -> list[Member]:
    width, downshift, scope = DEFAULT_CELL
    return [Member(width, downshift, scope, seed) for seed in DRAW_SEEDS]


def readout_a_verdict(published: int, counts: Sequence[int]) -> dict[str, Any]:
    """§5 A, per cell: *reproduced* within [min, max] of the draws' counts; *near* outside it but
    within ±25% of **the median** of those counts; *not reproduced* otherwise."""
    median = float(np.median(counts))
    low, high = int(min(counts)), int(max(counts))
    if low <= published <= high:
        verdict = "reproduced"
    elif abs(published - median) <= NEAR_FRACTION * median:
        verdict = "near"
    else:
        verdict = "not reproduced"
    return {
        "counts_by_draw": [int(c) for c in counts],
        "median": median,
        "minimum": low,
        "maximum": high,
        "published": published,
        "verdict": verdict,
    }


def readout_a(
    supported: Mapping[tuple[str, str], np.ndarray], table_7: Mapping[str, Mapping[str, int]]
) -> dict[str, Any]:
    """§5 A over rows × draws support: the six cells, each with its verdict, and the headline."""
    cells: dict[str, Any] = {}
    for c in COMPARISONS:
        cells[c.key] = {
            direction: readout_a_verdict(
                int(table_7[c.published_label][direction]),
                [int(x) for x in supported[(c.key, direction)].sum(axis=0)],
            )
            for direction in DIRECTIONS
        }
    return {
        "cells": cells,
        "headline": {
            "cell": f"{GATE_COMPARISON.key}, up",
            "verdict": cells[GATE_COMPARISON.key]["up"]["verdict"],
        },
    }


def readout_b(
    *,
    supported: Mapping[tuple[str, str], np.ndarray],
    imputed: np.ndarray,
    claim_rows: Sequence[int | None],
    claims: Sequence[PublishedClaim],
    family: np.ndarray | None,
) -> dict[str, Any]:
    """§5 B at the default cell, with its three reported secondaries.

    - **Exposure:** the claims §3 retained whose row carries at least one imputed value in any of
      the twelve samples. **Share:** those whose WT TAC vs WT control *up* support differs across
      the 20 draws (`pxd018299_h10.instability`). The verdict is `pxd018299_h10.h10_verdict`'s,
      flagged `n ≤ 10`.
    - **Secondary 1, the whole population.** **[reading]** *"across all six cells"* is ambiguous
      between per-cell shares and any-cell instability; the share is computed for each of the six
      cells, and the any-cell figure is reported beside them.
    - **Secondary 2, family categories** over the 360 members, with `pxd018299_h10.py`'s
      definitions (l.1329–1333): *durable* supported in every member, *unsupported* in none,
      *underdetermined* otherwise. `family` is claims × members, or `None` where not computed.
    - **Secondary 3:** each claim's support count out of 20 at the default cell.
    """
    headline = supported[(GATE_COMPARISON.key, "up")]
    retained = [(c, r) for c, r in zip(claims, claim_rows, strict=True) if r is not None]
    exposure = [(c, r) for c, r in retained if bool(imputed[r])]
    moved = [c.label for c, r in exposure if bool(instability(headline[[r]])[0])]
    share = _fraction(len(moved), len(exposure))
    any_unstable = np.zeros(imputed.shape[0], dtype=bool)
    per_cell: dict[str, Any] = {}
    for c in COMPARISONS:
        for direction in DIRECTIONS:
            unstable = instability(supported[(c.key, direction)])
            any_unstable |= unstable
            per_cell[f"{c.key}, {direction}"] = _fraction(
                int((unstable & imputed).sum()), int(imputed.sum())
            )
    categories: dict[str, Any] | None = None
    if family is not None:
        counts = family.sum(axis=1).tolist()
        width = family.shape[1]
        tally = collections.Counter(
            "durable" if n == width else ("unsupported" if n == 0 else "underdetermined")
            for n in counts
        )
        categories = {
            "members": width,
            "counts": {
                k: int(tally.get(k, 0)) for k in ("durable", "underdetermined", "unsupported")
            },
            "by_claim": {
                c.label: (
                    "durable" if n == width else ("unsupported" if n == 0 else "underdetermined")
                )
                for (c, _), n in zip(retained, counts, strict=True)
            },
        }
    return {
        "exposure": [c.label for c, _ in exposure],
        "exposure_size": len(exposure),
        "claims_whose_support_differs": moved,
        "share": share,
        "verdict": h10_verdict(share["share"]),
        "power_flag": "n ≤ 10",
        "secondary": {
            "whole_population_per_cell": per_cell,
            "whole_population_any_cell": _fraction(
                int((any_unstable & imputed).sum()), int(imputed.sum())
            ),
            "family_categories": categories,
            "support_out_of_20_at_default_cell": {
                c.label: int(headline[r].sum()) for c, r in retained
            },
        },
    }


def readout_c(
    supported: Mapping[tuple[str, str], np.ndarray],
    claim_rows: Sequence[int | None],
    claims: Sequence[PublishedClaim],
) -> dict[str, Any]:
    """§5 C: filamin-C K2590's *down* support in *Isg15*−/− TAC vs WT TAC, out of 20."""
    name, position = READOUT_C_TARGET
    found = [
        r
        for c, r in zip(claims, claim_rows, strict=True)
        if (c.protein_name, c.position) == (name, position)
    ]
    if not found:
        return {"target": f"{name} K{position}", "status": "not among the published claims"}
    row = found[0]
    if row is None:
        return {"target": f"{name} K{position}", "status": "lost to the valid-value rule"}
    down = supported[(READOUT_C_COMPARISON.key, "down")][row]
    return {
        "target": f"{name} K{position}",
        "comparison": READOUT_C_COMPARISON.key,
        "direction": "down",
        "supported_draws": int(down.sum()),
        "of": int(down.size),
    }


# ── the author configuration ────────────────────────────────────────────────────────────────────


def read_author_parameters(
    path: Path, *, repo_root: Path = REPO_ROOT
) -> AuthorConfiguration | None:
    """The author file, validated, or `None` where it does not exist.

    H10's rule (`pxd018299_h10.read_author_parameters`, l.1010) with this instrument's keys.
    **Any key outside them refuses by name**, `randomisations` and `scheme` included: a key this
    module does not use would be dropped, and the registered default run under a record claiming
    the authors' values. Whether it is tracked at the run's commit is `is_tracked`'s answer, as
    H10 records `author.tracked` (`pxd018299_h10.py` l.1372–1376).
    """
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    unknown = [k for k in payload if k not in (*AUTHOR_PARAMETER_KEYS, *AUTHOR_REQUIRED_KEYS)]
    if unknown:
        raise GateError(
            f"{path.name} carries unknown key(s) {sorted(unknown)}. Accepted: "
            f"{sorted(AUTHOR_PARAMETER_KEYS)}, plus the required {sorted(AUTHOR_REQUIRED_KEYS)}. "
            "H10's `randomisations` and `scheme` have no meaning for a parametric test."
        )
    missing = [k for k in AUTHOR_REQUIRED_KEYS if k not in payload]
    if missing:
        raise GateError(f"{path.name} is missing {sorted(missing)}: who stated them, and when.")
    if "scope" in payload and payload["scope"] not in GRID_SCOPES:
        raise GateError(f"{path.name} names scope {payload['scope']!r}, not one of {GRID_SCOPES}")
    return AuthorConfiguration(
        parameters={k: payload[k] for k in AUTHOR_PARAMETER_KEYS if k in payload},
        source=str(payload["source"]),
        date_received=str(payload["date_received"]),
        tracked=is_tracked(path, repo_root=repo_root),
    )


def _author_block(author: AuthorConfiguration) -> dict[str, Any]:
    return {
        "parameters": dict(author.parameters),
        "source": author.source,
        "date_received": author.date_received,
        "tracked_in_git": author.tracked,
    }


# ── one variant's readouts, and readout D ───────────────────────────────────────────────────────


@dataclass(frozen=True)
class Prepared:
    """The matrix that is imputed, and where each claim sits in it."""

    matrix: np.ndarray
    claim_rows: list[int | None]
    imputed: np.ndarray
    valid_value_rule: dict[str, Any]


def prepare(
    matrix: np.ndarray, claim_rows: Sequence[int], claims: Sequence[PublishedClaim]
) -> Prepared:
    """Steps 5 and 6: the valid-value rule, then the filtered matrix imputation runs over."""
    rule = valid_value_choice(matrix, claim_rows=claim_rows, claims=claims)
    keep = rule.pop("_keep")
    reduced, rows = filtered(matrix, keep, claim_rows)
    return Prepared(
        matrix=reduced,
        claim_rows=rows,
        imputed=np.isnan(reduced).any(axis=1),
        valid_value_rule={**rule, "rows_reaching_imputation": int(reduced.shape[0])},
    )


def readouts_for(
    prepared: Prepared,
    variant: str,
    *,
    claims: Sequence[PublishedClaim],
    table_7: Mapping[str, Mapping[str, int]],
    members: Sequence[Member],
    author: AuthorConfiguration | None,
) -> dict[str, Any]:
    """Readouts A, B and C under one variant.

    `author` is passed only when the file is tracked at the run's commit (`run` decides), so here
    it always becomes readout A's primary, with the default cell beside it, and adds a readout B
    line. Readout B's verdict is the default cell's whatever `author` is.
    """
    default = default_cell_members()
    supported = run_members(prepared.matrix, default, variant)
    claim_positions = [r for r in prepared.claim_rows if r is not None]
    family = (
        run_members(
            prepared.matrix,
            members,
            variant,
            rows=claim_positions,
            comparisons=(GATE_COMPARISON,),
        )[(GATE_COMPARISON.key, "up")]
        if claim_positions
        else None
    )
    a: dict[str, Any] = {"default_cell": readout_a(supported, table_7), "primary": "default_cell"}
    b = readout_b(
        supported=supported,
        imputed=prepared.imputed,
        claim_rows=prepared.claim_rows,
        claims=claims,
        family=family,
    )
    if author is not None:
        member = author.member()
        a["author_configuration"] = {
            **_author_block(author),
            "member": member.as_dict(),
            **readout_a(run_members(prepared.matrix, [member], variant), table_7),
        }
        a["primary"] = "author_configuration"
        # **[reading]** readout B's author line is D7 at the author's (width, downshift, scope)
        # over seeds 0–19: B measures instability across draws, which one seed cannot show. It is
        # a line, never the verdict — that stays on the default cell above.
        cell = [
            Member(member.width_sd, member.downshift_sd, member.scope, seed) for seed in DRAW_SEEDS
        ]
        line = readout_b(
            supported=run_members(prepared.matrix, cell, variant),
            imputed=prepared.imputed,
            claim_rows=prepared.claim_rows,
            claims=claims,
            family=None,
        )
        b["author_configuration_line"] = {
            **_author_block(author),
            "cell": {k: v for k, v in member.as_dict().items() if k != "seed"},
            "share": line["share"],
            "outcome_not_the_verdict": line["verdict"]["outcome"],
        }
    return {
        "variant": variant,
        "readout_a": a,
        "readout_b": b,
        "readout_c": readout_c(supported, prepared.claim_rows, claims),
    }


def readout_d(
    matrix: np.ndarray,
    matched: np.ndarray,
    claim_rows: Sequence[int],
    *,
    claims: Sequence[PublishedClaim],
    table_7: Mapping[str, Mapping[str, int]],
    members: Sequence[Member],
    primary: str,
    taken_before: int,
) -> dict[str, Any]:
    """§5 D under the primary only. **[reading on the masking point]**

    Cells whose `Identification type` is `By matching` are set to missing **before** steps 5 and 6
    — the registration says only *before imputation* — so the valid-value rule is chosen again,
    with step 5's fallback, and whether it changes is reported. **[reading]** D runs under the
    primary only: §4's *"readouts A–C … under both"* is read as not passing on to D.
    """
    masked = np.where(matched, np.nan, matrix)
    prepared = prepare(masked, claim_rows, claims)
    under = readouts_for(
        prepared, primary, claims=claims, table_7=table_7, members=members, author=None
    )
    return {
        "variant": primary,
        "cells_masked": int((matched & ~np.isnan(matrix)).sum()),
        "valid_value_rule": prepared.valid_value_rule,
        "valid_value_rule_changed": prepared.valid_value_rule["taken"] != taken_before,
        "readout_a": under["readout_a"],
        "readout_b": under["readout_b"],
    }


# ── the run ─────────────────────────────────────────────────────────────────────────────────────


def run(
    *,
    sites_path: Path,
    parameters_path: Path,
    published: Published,
    facts: DepositFacts,
    author_path: Path = AUTHOR_PARAMETERS,
    repo_root: Path = REPO_ROOT,
    members: Sequence[Member] | None = None,
    sites_deposit: DepositFile = PXD032267_SITES,
    parameters_deposit: DepositFile = PXD032267_PARAMETERS,
) -> dict[str, Any]:
    """Every step, in the registration's order, from two files on disk. Pure apart from reading.

    `members` defaults to the 360 of `family_members()`; it is a parameter so a synthetic test can
    run the family over fewer.
    """
    members = family_members() if members is None else members
    author = read_author_parameters(author_path, repo_root=repo_root)
    table, pinning = pinning_check(
        sites_path,
        parameters_path,
        facts=facts,
        sites_deposit=sites_deposit,
        parameters_deposit=parameters_deposit,
    )
    rows = population(table)
    matrix = values_matrix(table, rows)
    claim_rows, join_record = join(table, rows, published.claims, expected_ids=facts.joined_ids)
    prepared = prepare(matrix, claim_rows, published.claims)
    gate = gate_g(matrix, claim_rows, published.claims)

    out: dict[str, Any] = {
        "pinning": pinning,
        "population": {
            "rule": "every row of GlyGly__K_Sites.txt except reverse decoys (§2)",
            "rows": len(rows),
        },
        "join": join_record,
        "valid_value_rule": prepared.valid_value_rule,
        "gate_g": gate,
        "author_parameters": (
            None
            if author is None
            else {
                **_author_block(author),
                "used": author.tracked,
                "note": (
                    "tracked at the run's commit: readout A's primary, with the default cell "
                    "beside it, and an added readout B line"
                    if author.tracked
                    else "not tracked at the run's commit: reported and ignored, because "
                    "registration lines 22-23 admit only a committed file"
                ),
            }
        ),
        "readouts": None,
        "readout_d": None,
    }
    if gate["status"] not in ("passed", "not_separated"):
        return out
    out["readouts"] = {
        variant: readouts_for(
            prepared,
            variant,
            claims=published.claims,
            table_7=published.table_7,
            members=members,
            author=author if author is not None and author.tracked else None,
        )
        for variant in gate["readout_variants"]
    }
    out["readout_d"] = readout_d(
        matrix,
        matched_mask(table, rows),
        claim_rows,
        claims=published.claims,
        table_7=published.table_7,
        members=members,
        primary=str(gate["primary"]),
        taken_before=int(prepared.valid_value_rule["taken"]),
    )
    return out


def main(argv: Sequence[str] | None = None) -> int:  # pragma: no cover - the real run, on the Mac
    """Fetch both files into the content store, run, and write the fixture."""
    import scipy

    from bzk.sources.pride import fetch

    del argv
    sites = fetch(PXD032267_SITES, home=HOME)
    parameters = fetch(PXD032267_PARAMETERS, home=HOME)
    published = load_published()
    result = run(
        sites_path=sites.path,
        parameters_path=parameters.path,
        published=published,
        facts=load_deposit_facts(),
    )
    fixture = {
        "dataset": "PXD032267",
        "registration": REGISTRATION.relative_to(REPO_ROOT).as_posix(),
        "published_tables": PUBLISHED_TABLES.relative_to(REPO_ROOT).as_posix(),
        "published_tables_source_sha256": published.source_sha256,
        "sites_content_hash": result["pinning"]["sites"]["content_hash"],
        "parameters_content_hash": result["pinning"]["parameters"]["content_hash"],
        "author_parameters_present": result["author_parameters"] is not None,
        **result,
        "generated_by": GENERATED_BY,
        "generated_under": {
            "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
            **_commit(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
    }
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIXTURES_DIR / FIXTURE_NAME
    path.write_text(json.dumps(fixture, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[pxd032267_gate] G: {result['gate_g']['status']}; wrote {path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv[1:]))
