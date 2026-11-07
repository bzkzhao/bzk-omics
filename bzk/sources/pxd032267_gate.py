"""Run `walk/PREREG-PXD032267-gate.md`: the pinning check, gate G, and readouts A to D.

`python -m bzk.sources.pxd032267_gate --attempt {1,2}`, on bzk's Mac, after both deposit files can
be fetched. `--attempt` is required and has no default. **Not run in a build turn**: no deposit
bytes exist in that container, and no attempt is spent on a build.

## Two attempts, one instrument

- **Attempt 1** (`walk/PREREG-PXD032267-gate.md`) ran at `c1f23e1` and is on the record in
  `tests/fixtures/pxd032267_gate.json`. `--attempt 1` refuses while that file exists, so it is
  never re-written. Its path through `run()` is unchanged: no rounding, `INPUT_TOLERANCE`, and
  readouts only when G passes or is *not separated*.
- **Attempt 2** (`walk/PREREG-PXD032267-gate-attempt2.md`, final) changes exactly two things
  (its §2): measured log2 values are rounded with `np.round` to `ATTEMPT_ROUNDING_DECIMALS[2]`
  decimals before anything uses them, and the input check's tolerance is
  `ATTEMPT_INPUT_TOLERANCE[2]`. Its §3 consistency checks run inside `run()` **before any
  readout**, and the order is structural (its §6): every readout entry point takes a
  `ReadoutLicence` as its first argument, and the only licence attempt 2 can obtain is minted by
  `consistency_checks` after all three checks pass. It writes
  `tests/fixtures/pxd032267_gate_attempt2.json`, never attempt 1's fixture; a
  `.started.json` marker written the moment a licence exists blocks every repeat once a readout
  can have been computed (its §5).

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

import argparse
import collections
import hashlib
import json
import platform
import re
import sys
import traceback
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from types import MappingProxyType
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

#: Attempt 2's registration, which governs only where it replaces `REGISTRATION` (its l.6–9).
REGISTRATION_ATTEMPT2 = WALK_DIR / "PREREG-PXD032267-gate-attempt2.md"
#: Attempt 1's result; its exploratory block is read for §3 check 3's *"beside"* values.
ATTEMPT1_RESULT = WALK_DIR / "RESULT-PXD032267-gate-attempt1.md"
#: Attempt 1's committed fixture: §3 check 1's and check 2's reference. Never written here.
REFERENCE_FIXTURE = FIXTURES_DIR / FIXTURE_NAME
FIXTURE_NAME_ATTEMPT2 = "pxd032267_gate_attempt2.json"
STARTED_NAME_ATTEMPT2 = "pxd032267_gate_attempt2.started.json"
FAULTS_NAME_ATTEMPT2 = "pxd032267_gate_attempt2_faults.json"

# ── constants transcribed from the registration, each guarded against its text ──────────────────
# `tests/test_pxd032267_gate.py` parses every number below out of `REGISTRATION` and compares it to
# the constant, in the pattern of `graph.I4_LABELS`' guard. Full rules, not half-rules.

#: §4 *Input check*: *"to |Δ| ≤ 1e-5"*, on every gate row. Attempt 1's, and only attempt 1's:
#: `gate_g` takes the tolerance as an argument and never reads this name.
INPUT_TOLERANCE = 1e-5

# ── the attempt switch: attempt 2's two changes, each guarded against its text ─────────────────
# `MappingProxyType`, so item assignment raises. Rebinding the module name does not — that route is
# open, and the build report lists it.

#: Attempt 2 §2 *Change 1* (l.54–55, *"rounded to **four decimals** … (numpy's `round`)"*) and §6
#: (l.148–150, *"`None` for attempt 1 … and `4` for attempt 2"*).
ATTEMPT_ROUNDING_DECIMALS: Mapping[int, int | None] = MappingProxyType({1: None, 2: 4})

#: Attempt 2 §2 *Change 2* (l.64, *"5e-7 + 1e-9"*): written as that sum, which is not the float
#: `5.01e-7`. Attempt 1's entry **is** `INPUT_TOLERANCE`, not a second literal.
ATTEMPT_INPUT_TOLERANCE: Mapping[int, float] = MappingProxyType(
    {1: INPUT_TOLERANCE, 2: 5e-7 + 1e-9}
)

#: Attempt 2 §3 check 2 (l.86): *"on all three gate rows"*.
ATTEMPT2_GATE_ROWS = 3

#: Attempt 2 §3 check 3 (l.87): *"with **T1 the only passing variant**"*.
ATTEMPT2_SOLE_VARIANT = "T1"

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


class InstrumentFault(RuntimeError):
    """Attempt 2 §3 (l.97–101): *"A failure in §3 is an instrument fault, not an attempt."*

    Also raised when a readout is handed a licence that does not match its data. `consistency`
    carries the full §3 block — every check, its inputs, result and reason — when §3 failed.
    """

    def __init__(self, message: str, *, consistency: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.consistency = consistency


# ── readout licences (attempt 2 §6: the order is structural, not incidental) ────────────────────


class _Licence:
    """Permission to compute readouts. **Minted, never constructed.**

    Every readout entry point — `readouts_for`, `readout_a`, `readout_b`, `readout_c`,
    `readout_d` — takes one as its first, positional argument, so mypy refuses a readout called
    without one. `__init__` raises, attributes cannot be set after minting, and `copy`/`pickle`
    fail on the same `__setattr__`, so a licence exists only where `_mint_licence` made it.

    What a licence records at minting: the attempt, the rounding decimals it was minted for (which
    `readouts_for` and `readout_d` compare to their data's, raising `InstrumentFault` on a
    mismatch), the label the readouts must carry (`None` under attempt 1), and who issued it.
    """

    __slots__ = ("attempt", "decimals", "issued_by", "label")
    attempt: int
    decimals: int | None
    label: str | None
    issued_by: str

    def __init__(self) -> None:
        raise TypeError(f"{type(self).__name__} is minted by run(), never constructed")

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError(f"a readout licence is immutable: {name} cannot be set")

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(attempt={self.attempt}, decimals={self.decimals}, "
            f"issued_by={self.issued_by!r})"
        )


class Attempt1Status(_Licence):
    """Attempt 1's existing path: G passed or is *not separated*, with no rounding."""

    __slots__ = ("gate_status",)
    gate_status: str


class ConsistencyPassed(_Licence):
    """Attempt 2: all three §3 consistency checks held, and nothing else mints this."""

    __slots__ = ()


ReadoutLicence = Attempt1Status | ConsistencyPassed

#: Every licence minted in this process, by kind, in order. Read through `licences_issued()`, so a
#: test can show that a failing §3 minted none without naming a private symbol.
_ISSUED: list[str] = []


def _mint_licence[L: (Attempt1Status, ConsistencyPassed)](
    kind: type[L], *, attempt: int, issued_by: str, **fields: object
) -> L:
    """The one place a licence comes into being. Callers: the two mints and the test factory."""
    licence = object.__new__(kind)
    for name, value in {
        "attempt": attempt,
        "decimals": ATTEMPT_ROUNDING_DECIMALS[attempt],
        "issued_by": issued_by,
        "label": None,
        **fields,
    }.items():
        object.__setattr__(licence, name, value)
    _ISSUED.append(kind.__name__)
    return licence


def _mint_attempt1(*, decimals: int | None, gate_status: str) -> Attempt1Status:
    """Attempt 1's licence. Called only from `run()`'s attempt-1 branch, and refuses unless the
    data is unrounded and G passed or is *not separated* — attempt 1's existing condition."""
    if decimals is not None:
        raise InstrumentFault(f"attempt 1 is never rounded; asked to license decimals={decimals}")
    if gate_status not in ("passed", "not_separated"):
        raise InstrumentFault(f"attempt 1 licenses readouts only when G passes; G is {gate_status}")
    return _mint_licence(Attempt1Status, attempt=1, issued_by="run", gate_status=gate_status)


def _mint_consistency(
    *, attempt: int, decimals: int | None, consistency: Mapping[str, Any], label: str
) -> ConsistencyPassed:
    """Attempt 2's licence. Called only from `consistency_checks`, and refuses unless the block it
    is handed records all three checks as passed — a second look, not the only one."""
    if attempt != 2 or decimals != ATTEMPT_ROUNDING_DECIMALS[2]:
        raise InstrumentFault(f"ConsistencyPassed is attempt 2's, at its decimals; not {attempt}")
    checks = consistency.get("checks", {})
    if (
        consistency.get("passed") is not True
        or set(checks) != {"1", "2", "3"}
        or not all(c.get("passed") is True for c in checks.values())
    ):
        raise InstrumentFault("§3 has not passed; no licence", consistency=dict(consistency))
    return _mint_licence(ConsistencyPassed, attempt=2, issued_by="run", label=label)


def licence_for_tests(attempt: int) -> ReadoutLicence:
    """**Test-only.** A licence for calling one readout function directly on synthetic data.

    Never used by `run()` or by any `run()`-level test; `tests/test_pxd032267_gate.py` enforces
    both. It records `issued_by="tests"`, and `main` refuses such a licence if one ever reaches it.
    """
    if attempt == 1:
        return _mint_licence(Attempt1Status, attempt=1, issued_by="tests", gate_status="tests")
    if attempt == 2:
        return _mint_licence(
            ConsistencyPassed, attempt=2, issued_by="tests", label=attempt2_label()
        )
    raise GateError(f"no attempt {attempt}")


def licences_issued() -> int:
    """How many licences this process has minted, of either kind."""
    return len(_ISSUED)


def _require(licence: ReadoutLicence, *, decimals: int | None, where: str) -> None:
    """The runtime match check: the licence's recorded decimals must be the data's. Never inferred
    from the values; `decimals` is what the caller declared the data was rounded to."""
    if not isinstance(licence, Attempt1Status | ConsistencyPassed):
        raise InstrumentFault(f"{where} needs a ReadoutLicence, not {type(licence).__name__}")
    if licence.decimals != decimals:
        raise InstrumentFault(
            f"{where}: licence minted for attempt {licence.attempt} at decimals="
            f"{licence.decimals}, handed data at decimals={decimals}"
        )


def _label(licence: ReadoutLicence, block: dict[str, Any]) -> dict[str, Any]:
    """Attempt 2 §4 (l.123–124): every attempt-2 readout block carries the label. Attempt 1's
    licence has none, so attempt 1's output is unchanged."""
    if licence.label is not None:
        block["label"] = licence.label
    return block


# ── text read from attempt 2's registration and attempt 1's result ─────────────────────────────


def attempt2_label(path: Path = REGISTRATION_ATTEMPT2) -> str:
    """Attempt 2 §4's label, read from its text: italic there, and wrapped across a line break, so
    whitespace is normalised. Exactly one match, or `GateError`."""
    found = re.findall(
        r"\*\*Every attempt-2 readout carries the label\*\*\s+\*([^*]+)\*",
        path.read_text(encoding="utf-8"),
    )
    if len(found) != 1:
        raise GateError(f"{path.name}: the §4 label matched {len(found)} times, not once")
    return " ".join(found[0].split())


def exploratory_max_abs_delta_p(path: Path = ATTEMPT1_RESULT) -> dict[str, float]:
    """Each variant's max |Δp| from attempt 1's exploratory output, read from its verbatim block.

    Attempt 2 §3 check 3 reports these *beside* the run's values and **never tests against them**;
    nothing here compares them to anything. Each variant must appear exactly once in the block.
    """
    text = path.read_text(encoding="utf-8")
    blocks = re.findall(r"Output,\s+verbatim:\s*\n```\n(.*?)\n```", text, re.DOTALL)
    if len(blocks) != 1:
        raise GateError(f"{path.name}: the verbatim exploratory block matched {len(blocks)} times")
    lines = re.findall(r"^\s+(T\d): p=.*?max\|dp\|=(\S+)\s", blocks[0], re.MULTILINE)
    variants = [v for v, _ in lines]
    if variants != list(GATE_VARIANTS):
        raise GateError(f"{path.name}: the block names {variants}, not {list(GATE_VARIANTS)}")
    return {v: float(x) for v, x in lines}


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


def gate_row_indices(matrix: np.ndarray, claim_rows: Sequence[int]) -> list[int]:
    """§4 *Gate rows*: the claims measured (non-zero) in all twelve samples, as claim indices."""
    return [i for i, row in enumerate(claim_rows) if not np.isnan(matrix[row]).any()]


def gate_scores(gate_matrix: np.ndarray, published_p: np.ndarray) -> dict[str, Any]:
    """Tukey on the gate rows, then `score_variants`. Pure, and the **only** route to G's scores.

    `gate_g` calls it once the input check passes; attempt 2's `consistency_checks` calls it
    whether or not the input check passed (the decision on prompt 35's receipt, option b), so §3's
    check 3 has a result to record even when check 2 fails. Where both ran, `consistency_checks`
    requires the two results to be equal and raises `InstrumentFault` otherwise.
    """
    result = tukey(
        gate_matrix,
        GENOTYPE,
        SURGERY,
        pairs=[(GATE_COMPARISON.first, GATE_COMPARISON.second)],
    ).pair(GATE_COMPARISON.first, GATE_COMPARISON.second)
    return score_variants({v: result.p[v] for v in GATE_VARIANTS}, published_p)


def gate_g(
    matrix: np.ndarray,
    claim_rows: Sequence[int],
    claims: Sequence[PublishedClaim],
    *,
    input_tolerance: float,
) -> dict[str, Any]:
    """§4, in this order. **[reading on the order]**

    1. **Gate rows:** Table 8 claims measured (non-zero) in all twelve samples. Fewer than two
       gives `undeterminable` and the variants are not scored — but **the input check still runs
       on whatever gate rows exist, and its result is recorded beside the status**, against §4's
       *"Nothing downstream runs"*: if the authors' matrix is not the deposit's, that matters more
       than the row count, and a new registration written without knowing it would be wasted.
    2. **Input check:** the published Difference to |Δ| ≤ `input_tolerance` on every gate row; a
       failure is `input_not_reproduced`. The tolerance is the caller's, **required**, and no
       module global is read: `ATTEMPT_INPUT_TOLERANCE[attempt]`, which is `INPUT_TOLERANCE`
       (1e-5) for attempt 1 and 5e-7 + 1e-9 for attempt 2.
    3. **The variants**, scored by `gate_scores`.
    """
    complete = gate_row_indices(matrix, claim_rows)
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
                "passes": delta <= input_tolerance,
            }
        )
    input_check = {
        "rows_checked": len(rows),
        "tolerance": input_tolerance,
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
    scored = gate_scores(gate_matrix, np.array([claims[i].p_value for i in complete]))
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

    A helper that computes no readout on its own, so it takes no licence: it is reached only
    through a licensed entry point (`readouts_for`, `readout_d`) or a direct test of itself.

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

    Computes no readout on its own, so it takes no licence; the entry points that call it do.
    Imputed draws are made here, after any rounding, and are **not** rounded (attempt 2 §2).

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
    within ±25% of **the median** of those counts; *not reproduced* otherwise.

    A pure verdict on counts it is handed, computing no readout on its own: it takes no licence.
    """
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
    licence: ReadoutLicence,
    supported: Mapping[tuple[str, str], np.ndarray],
    table_7: Mapping[str, Mapping[str, int]],
) -> dict[str, Any]:
    """§5 A over rows × draws support: the six cells, each with its verdict, and the headline.

    `licence` is for mypy's sake only, with **no runtime check**: this receives support arrays,
    not a matrix, so there are no decimals to compare. It supplies the attempt-2 label.
    """
    cells: dict[str, Any] = {}
    for c in COMPARISONS:
        cells[c.key] = {
            direction: readout_a_verdict(
                int(table_7[c.published_label][direction]),
                [int(x) for x in supported[(c.key, direction)].sum(axis=0)],
            )
            for direction in DIRECTIONS
        }
    return _label(
        licence,
        {
            "cells": cells,
            "headline": {
                "cell": f"{GATE_COMPARISON.key}, up",
                "verdict": cells[GATE_COMPARISON.key]["up"]["verdict"],
            },
        },
    )


def readout_b(
    licence: ReadoutLicence,
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

    `licence` is for mypy's sake only, with **no runtime check**: this receives support arrays,
    not a matrix. It supplies the attempt-2 label, on the readout and on its secondaries.
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
    return _label(
        licence,
        {
            "exposure": [c.label for c, _ in exposure],
            "exposure_size": len(exposure),
            "claims_whose_support_differs": moved,
            "share": share,
            "verdict": h10_verdict(share["share"]),
            "power_flag": "n ≤ 10",
            "secondary": _label(
                licence,
                {
                    "whole_population_per_cell": per_cell,
                    "whole_population_any_cell": _fraction(
                        int((any_unstable & imputed).sum()), int(imputed.sum())
                    ),
                    "family_categories": categories,
                    "support_out_of_20_at_default_cell": {
                        c.label: int(headline[r].sum()) for c, r in retained
                    },
                },
            ),
        },
    )


def readout_c(
    licence: ReadoutLicence,
    supported: Mapping[tuple[str, str], np.ndarray],
    claim_rows: Sequence[int | None],
    claims: Sequence[PublishedClaim],
) -> dict[str, Any]:
    """§5 C: filamin-C K2590's *down* support in *Isg15*−/− TAC vs WT TAC, out of 20.

    `licence` is for mypy's sake only, with **no runtime check**: this receives support arrays,
    not a matrix. It supplies the attempt-2 label, on every outcome.
    """
    name, position = READOUT_C_TARGET
    found = [
        r
        for c, r in zip(claims, claim_rows, strict=True)
        if (c.protein_name, c.position) == (name, position)
    ]
    if not found:
        return _label(
            licence, {"target": f"{name} K{position}", "status": "not among the published claims"}
        )
    row = found[0]
    if row is None:
        return _label(
            licence, {"target": f"{name} K{position}", "status": "lost to the valid-value rule"}
        )
    down = supported[(READOUT_C_COMPARISON.key, "down")][row]
    return _label(
        licence,
        {
            "target": f"{name} K{position}",
            "comparison": READOUT_C_COMPARISON.key,
            "direction": "down",
            "supported_draws": int(down.sum()),
            "of": int(down.size),
        },
    )


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
    """The matrix that is imputed, and where each claim sits in it.

    `decimals` is what the caller **declared** the matrix was rounded to (`None` for unrounded). It
    is recorded, never inferred from the values; `readouts_for` compares it to its licence's.
    """

    matrix: np.ndarray
    claim_rows: list[int | None]
    imputed: np.ndarray
    valid_value_rule: dict[str, Any]
    decimals: int | None


def prepare(
    matrix: np.ndarray,
    claim_rows: Sequence[int],
    claims: Sequence[PublishedClaim],
    *,
    decimals: int | None,
) -> Prepared:
    """Steps 5 and 6: the valid-value rule, then the filtered matrix imputation runs over.

    `decimals` is required and only recorded: rounding happens once, in `run()`, before this.
    """
    rule = valid_value_choice(matrix, claim_rows=claim_rows, claims=claims)
    keep = rule.pop("_keep")
    reduced, rows = filtered(matrix, keep, claim_rows)
    return Prepared(
        matrix=reduced,
        claim_rows=rows,
        imputed=np.isnan(reduced).any(axis=1),
        valid_value_rule={**rule, "rows_reaching_imputation": int(reduced.shape[0])},
        decimals=decimals,
    )


def readouts_for(
    licence: ReadoutLicence,
    prepared: Prepared,
    variant: str,
    *,
    claims: Sequence[PublishedClaim],
    table_7: Mapping[str, Mapping[str, int]],
    members: Sequence[Member],
    author: AuthorConfiguration | None,
    into: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Readouts A, B and C under one variant.

    `author` is passed only when the file is tracked at the run's commit (`run` decides), so here
    it always becomes readout A's primary, with the default cell beside it, and adds a readout B
    line. Readout B's verdict is the default cell's whatever `author` is.

    **Licensed and checked:** raises `InstrumentFault` unless `licence` was minted for
    `prepared.decimals`. Each block is written into `into` (when given) the moment it is complete,
    so a caller holding `into` keeps every readout computed before an exception (attempt 2 §5).
    """
    _require(licence, decimals=prepared.decimals, where="readouts_for")
    out: dict[str, Any] = {} if into is None else into
    out["variant"] = variant
    _label(licence, out)
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
    a: dict[str, Any] = _label(
        licence,
        {"default_cell": readout_a(licence, supported, table_7), "primary": "default_cell"},
    )
    out["readout_a"] = a
    b = readout_b(
        licence,
        supported=supported,
        imputed=prepared.imputed,
        claim_rows=prepared.claim_rows,
        claims=claims,
        family=family,
    )
    out["readout_b"] = b
    if author is not None:
        member = author.member()
        a["author_configuration"] = {
            **_author_block(author),
            "member": member.as_dict(),
            **readout_a(licence, run_members(prepared.matrix, [member], variant), table_7),
        }
        a["primary"] = "author_configuration"
        # **[reading]** readout B's author line is D7 at the author's (width, downshift, scope)
        # over seeds 0–19: B measures instability across draws, which one seed cannot show. It is
        # a line, never the verdict — that stays on the default cell above.
        cell = [
            Member(member.width_sd, member.downshift_sd, member.scope, seed) for seed in DRAW_SEEDS
        ]
        line = readout_b(
            licence,
            supported=run_members(prepared.matrix, cell, variant),
            imputed=prepared.imputed,
            claim_rows=prepared.claim_rows,
            claims=claims,
            family=None,
        )
        b["author_configuration_line"] = _label(
            licence,
            {
                **_author_block(author),
                "cell": {k: v for k, v in member.as_dict().items() if k != "seed"},
                "share": line["share"],
                "outcome_not_the_verdict": line["verdict"]["outcome"],
            },
        )
    out["readout_c"] = readout_c(licence, supported, prepared.claim_rows, claims)
    return out


def readout_d(
    licence: ReadoutLicence,
    matrix: np.ndarray,
    matched: np.ndarray,
    claim_rows: Sequence[int],
    *,
    decimals: int | None,
    claims: Sequence[PublishedClaim],
    table_7: Mapping[str, Mapping[str, int]],
    members: Sequence[Member],
    primary: str,
    taken_before: int,
    into: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """§5 D under the primary only. **[reading on the masking point]**

    Cells whose `Identification type` is `By matching` are set to missing **before** steps 5 and 6
    — the registration says only *before imputation* — so the valid-value rule is chosen again,
    with step 5's fallback, and whether it changes is reported. **[reading]** D runs under the
    primary only: §4's *"readouts A–C … under both"* is read as not passing on to D.

    **Licensed and checked:** `decimals` is required, compared to the licence's before anything
    is computed, and passed on to the internal `prepare`. `matrix` is `run()`'s, already rounded
    under attempt 2, so the masked re-preparation sees rounded values. Blocks are written into
    `into` as they complete, as in `readouts_for`.
    """
    _require(licence, decimals=decimals, where="readout_d")
    out: dict[str, Any] = {} if into is None else into
    out["variant"] = primary
    _label(licence, out)
    masked = np.where(matched, np.nan, matrix)
    out["cells_masked"] = int((matched & ~np.isnan(matrix)).sum())
    prepared = prepare(masked, claim_rows, claims, decimals=decimals)
    out["valid_value_rule"] = prepared.valid_value_rule
    out["valid_value_rule_changed"] = prepared.valid_value_rule["taken"] != taken_before
    under: dict[str, Any] = {}
    try:
        readouts_for(
            licence,
            prepared,
            primary,
            claims=claims,
            table_7=table_7,
            members=members,
            author=None,
            into=under,
        )
    finally:
        for key in ("readout_a", "readout_b"):
            if key in under:
                out[key] = under[key]
    return out


# ── attempt 2 §3: the consistency checks, before any readout ────────────────────────────────────


def _display(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def _reference_item(read: Callable[[], Any], this_run: Any, what: str) -> dict[str, Any]:
    """One compared value. A reference that lacks it fails the comparison, with the reason."""
    try:
        reference = read()
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        return {
            "reference": None,
            "this_run": this_run,
            "equal": False,
            "reason": f"the reference fixture has no {what}: {exc!r}",
        }
    return {"reference": reference, "this_run": this_run, "equal": reference == this_run}


def _check_reproduced(
    reference: Mapping[str, Any],
    pinning: Mapping[str, Any],
    join_record: Sequence[Mapping[str, Any]],
    valid_value_rule: Mapping[str, Any],
) -> dict[str, Any]:
    """Check 1: the same digests, ids, rule taken and rows retained as the reference — read from
    the reference fixture, never copied into this module."""
    items = {
        "sites_content_hash": _reference_item(
            lambda: str(reference["sites_content_hash"]),
            str(pinning["sites"]["content_hash"]),
            "sites_content_hash",
        ),
        "parameters_content_hash": _reference_item(
            lambda: str(reference["parameters_content_hash"]),
            str(pinning["parameters"]["content_hash"]),
            "parameters_content_hash",
        ),
        "joined_ids": _reference_item(
            lambda: [int(r["joined_id"]) for r in reference["join"]],
            [int(r["joined_id"]) for r in join_record],
            "join",
        ),
        "valid_value_rule_taken": _reference_item(
            lambda: int(reference["valid_value_rule"]["taken"]),
            int(valid_value_rule["taken"]),
            "valid_value_rule.taken",
        ),
        "rows_reaching_imputation": _reference_item(
            lambda: int(reference["valid_value_rule"]["rows_reaching_imputation"]),
            int(valid_value_rule["rows_reaching_imputation"]),
            "valid_value_rule.rows_reaching_imputation",
        ),
    }
    differing = [k for k, item in items.items() if not item["equal"]]
    return {
        "check": "attempt 1's pinning, join and valid-value results are reproduced exactly",
        "registration": "attempt 2 §3 check 1 (l.83–85)",
        "inputs": items,
        "passed": not differing,
        "reason": (
            "all five equal the reference"
            if not differing
            else f"differ from the reference: {', '.join(differing)}"
        ),
    }


def _check_input(reference: Mapping[str, Any], gate: Mapping[str, Any]) -> dict[str, Any]:
    """Check 2: the gate rows are the reference's three, and each passes at change 2's tolerance."""
    try:
        reference_rows: list[str] | None = [str(x) for x in reference["gate_g"]["gate_rows"]]
    except (KeyError, TypeError):
        reference_rows = None
    rows = [str(x) for x in gate["gate_rows"]]
    input_check = gate["input_check"]
    conditions = {
        "gate_rows_equal_the_reference": reference_rows == rows,
        "three_gate_rows": len(rows) == ATTEMPT2_GATE_ROWS,
        "tolerance_is_change_2s": input_check["tolerance"] == ATTEMPT_INPUT_TOLERANCE[2],
        "every_gate_row_passes": bool(input_check["rows"])
        and all(r["passes"] for r in input_check["rows"]),
    }
    failing = [k for k, v in conditions.items() if not v]
    return {
        "check": "the input check passes on all three gate rows at the change-2 tolerance",
        "registration": "attempt 2 §3 check 2 (l.86)",
        "inputs": {
            "reference_gate_rows": reference_rows,
            "gate_rows": rows,
            "tolerance": input_check["tolerance"],
            "rows": [
                {"claim": r["claim"], "abs_delta": r["abs_delta"], "passes": r["passes"]}
                for r in input_check["rows"]
            ],
        },
        "conditions": conditions,
        "passed": not failing,
        "reason": "every condition holds" if not failing else f"fails: {', '.join(failing)}",
    }


def _check_sole_variant(
    matrix: np.ndarray,
    claim_rows: Sequence[int],
    claims: Sequence[PublishedClaim],
    gate: Mapping[str, Any],
) -> dict[str, Any]:
    """Check 3: G passes, with T1 the only passing variant.

    The variants are scored here by `gate_scores` **whether or not check 2 passed**, so this check
    always has a result to record. **[reading]** *"G passes"* is judged on these scores — status
    `passed` under §4's rule — and not on `gate_g`'s status, which reads `input_not_reproduced`
    whenever check 2 fails and would make check 3 fail with it. Where `gate_g` also scored the
    variants (always, once check 2 passes), the two must be equal; a mismatch fails this check,
    and so raises `InstrumentFault`. Each variant's max |Δp| is reported beside attempt 1's
    exploratory value, **never tested against it** (l.87–89).
    """
    complete = gate_row_indices(matrix, claim_rows)
    scores = (
        gate_scores(
            matrix[[claim_rows[i] for i in complete]],
            np.array([claims[i].p_value for i in complete]),
        )
        if complete
        else None
    )
    gate_scored = "variants" in gate
    matches: bool | None = None
    if gate_scored:
        matches = scores is not None and {k: gate.get(k) for k in scores} == scores
    exploratory = exploratory_max_abs_delta_p()
    conditions = {
        "g_passes_on_these_scores": scores is not None and scores["status"] == "passed",
        "t1_the_only_passing_variant": scores is not None
        and scores["passing"] == [ATTEMPT2_SOLE_VARIANT],
        "scores_equal_gate_gs": matches is not False,
    }
    failing = [k for k, v in conditions.items() if not v]
    reason = "every condition holds" if not failing else f"fails: {', '.join(failing)}"
    if matches is False:
        reason += (
            " — gate_g's scores and this check's differ although both came from gate_scores: "
            "the instrument disagrees with itself"
        )
    return {
        "check": "Gate G passes, with T1 the only passing variant",
        "registration": "attempt 2 §3 check 3 (l.87–92)",
        "inputs": {
            "gate_g_status": gate["status"],
            "status": None if scores is None else scores["status"],
            "gate_g_scored": gate_scored,
            "scored_here": scores is not None,
            "passing": None if scores is None else scores["passing"],
            "variants": {
                v: {
                    "max_abs_delta_p": (
                        None if scores is None else scores["variants"][v]["max_abs_delta_p"]
                    ),
                    "passes": None if scores is None else scores["variants"][v]["passes"],
                    "exploratory_max_abs_delta_p": exploratory[v],
                }
                for v in GATE_VARIANTS
            },
            "exploratory_values": (
                f"{_display(ATTEMPT1_RESULT)}, the verbatim exploratory block: reported beside, "
                "never tested against (attempt 2 §3 check 3)"
            ),
        },
        "conditions": conditions,
        "passed": not failing,
        "reason": reason,
    }


def consistency_checks(
    matrix: np.ndarray,
    claim_rows: Sequence[int],
    claims: Sequence[PublishedClaim],
    *,
    attempt: int,
    decimals: int | None,
    reference_fixture: Path,
    pinning: Mapping[str, Any],
    join_record: Sequence[Mapping[str, Any]],
    valid_value_rule: Mapping[str, Any],
    gate: Mapping[str, Any],
    label: str,
) -> tuple[ConsistencyPassed, dict[str, Any]]:
    """Attempt 2 §3, all three checks, **every one evaluated and recorded even after one fails**.

    Called only by `run()`, only under attempt 2, after the gate and before any readout. On any
    failure it raises `InstrumentFault` carrying the whole block, and no licence exists; on success
    it returns the only `ConsistencyPassed` attempt 2 can obtain, beside the block.
    """
    if attempt != 2:
        raise InstrumentFault(f"§3's consistency checks are attempt 2's, not attempt {attempt}'s")
    reference = json.loads(reference_fixture.read_text(encoding="utf-8"))
    checks = {
        "1": _check_reproduced(reference, pinning, join_record, valid_value_rule),
        "2": _check_input(reference, gate),
        "3": _check_sole_variant(matrix, claim_rows, claims, gate),
    }
    failed = [k for k, check in checks.items() if not check["passed"]]
    block: dict[str, Any] = {
        "label": label,
        "registration": "attempt 2 §3 (l.80–101)",
        "reference_fixture": _display(reference_fixture),
        "reference_fixture_sha256": _sha256(reference_fixture),
        "checks": checks,
        "failed": failed,
        "passed": not failed,
    }
    if failed:
        raise InstrumentFault(
            f"attempt 2 §3: check(s) {', '.join(failed)} failed. An instrument fault, not an "
            "attempt: no licence was minted and no readout computed.",
            consistency=block,
        )
    licence = _mint_consistency(attempt=attempt, decimals=decimals, consistency=block, label=label)
    return licence, block


# ── the run ─────────────────────────────────────────────────────────────────────────────────────


def run(
    *,
    attempt: int,
    sites_path: Path,
    parameters_path: Path,
    published: Published,
    facts: DepositFacts,
    author_path: Path = AUTHOR_PARAMETERS,
    repo_root: Path = REPO_ROOT,
    members: Sequence[Member] | None = None,
    sites_deposit: DepositFile = PXD032267_SITES,
    parameters_deposit: DepositFile = PXD032267_PARAMETERS,
    reference_fixture: Path = REFERENCE_FIXTURE,
    on_licence: Callable[[ReadoutLicence], None] | None = None,
    output: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Every step, in the registrations' order, from two files on disk. Pure apart from reading.

    - `attempt` is required. It selects `ATTEMPT_ROUNDING_DECIMALS` and `ATTEMPT_INPUT_TOLERANCE`
      and nothing else, except that attempt 2 runs §3's consistency checks where attempt 1 tests
      G's status.
    - Measured log2 values are rounded **once**, immediately after `values_matrix`, by rebinding
      `matrix`; everything after reads the rebound name — the input check, the gate, the
      valid-value rule, imputation's input and every readout, readout D's masking included.
      Imputed draws are made later and never rounded.
    - `reference_fixture` defaults to attempt 1's committed fixture. It is injectable so a
      synthetic test can supply its own — a route around check 1 that the build report lists.
    - `on_licence` is called once, with the licence, after it is minted and before the first
      readout. `output`, if given, must be empty; every block is written into it as it completes,
      so a caller keeps whatever was computed before an exception.
    - `members` defaults to the 360 of `family_members()`; it is a parameter so a synthetic test
      can run the family over fewer.
    """
    if attempt not in ATTEMPT_ROUNDING_DECIMALS:
        raise GateError(f"no attempt {attempt} is registered: {sorted(ATTEMPT_ROUNDING_DECIMALS)}")
    decimals = ATTEMPT_ROUNDING_DECIMALS[attempt]
    out: dict[str, Any] = {} if output is None else output
    if out:
        raise GateError("run(output=...) must be handed an empty dict")
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
    if decimals is not None:
        matrix = np.round(matrix, decimals)
    claim_rows, join_record = join(table, rows, published.claims, expected_ids=facts.joined_ids)
    prepared = prepare(matrix, claim_rows, published.claims, decimals=decimals)
    gate = gate_g(
        matrix, claim_rows, published.claims, input_tolerance=ATTEMPT_INPUT_TOLERANCE[attempt]
    )

    record: dict[str, Any] = {
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
    }
    if attempt == 2:
        record["consistency"] = None
    record["readouts"] = None
    record["readout_d"] = None
    out.update(record)

    licence: ReadoutLicence
    if attempt == 1:
        if gate["status"] not in ("passed", "not_separated"):
            return out
        licence = _mint_attempt1(decimals=decimals, gate_status=str(gate["status"]))
    else:
        try:
            licence, out["consistency"] = consistency_checks(
                matrix,
                claim_rows,
                published.claims,
                attempt=attempt,
                decimals=decimals,
                reference_fixture=reference_fixture,
                pinning=pinning,
                join_record=join_record,
                valid_value_rule=prepared.valid_value_rule,
                gate=gate,
                label=attempt2_label(),
            )
        except InstrumentFault as fault:
            out["consistency"] = fault.consistency
            raise
    if on_licence is not None:
        on_licence(licence)

    readouts: dict[str, Any] = {}
    out["readouts"] = readouts
    for variant in gate["readout_variants"]:
        readouts[variant] = {}
        readouts_for(
            licence,
            prepared,
            variant,
            claims=published.claims,
            table_7=published.table_7,
            members=members,
            author=author if author is not None and author.tracked else None,
            into=readouts[variant],
        )
    out["readout_d"] = {}
    readout_d(
        licence,
        matrix,
        matched_mask(table, rows),
        claim_rows,
        decimals=decimals,
        claims=published.claims,
        table_7=published.table_7,
        members=members,
        primary=str(gate["primary"]),
        taken_before=int(prepared.valid_value_rule["taken"]),
        into=out["readout_d"],
    )
    return out


# ── main: refusals, the started marker, the faults file ─────────────────────────────────────────


def refusal(attempt: int, *, fixtures_dir: Path = FIXTURES_DIR) -> str | None:
    """Why `main --attempt <attempt>` must not run, or `None`. Checked before any computation."""
    if attempt == 1:
        path = fixtures_dir / FIXTURE_NAME
        if path.exists():
            return f"{path} exists: attempt 1 is on the record and is never re-written"
        return None
    if attempt == 2:
        for name, why in (
            (FIXTURE_NAME_ATTEMPT2, "a completed attempt-2 fixture is never overwritten (§5)"),
            (
                STARTED_NAME_ATTEMPT2,
                (
                    "readouts were started under attempt 2, and once a readout may have been "
                    "computed no repeat is allowed (§5)"
                ),
            ),
        ):
            if (fixtures_dir / name).exists():
                return f"{fixtures_dir / name} exists: {why}"
        return None
    return f"no attempt {attempt} is registered"


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _generated_under() -> dict[str, Any]:
    import scipy

    return {
        "generated_at": _now(),
        **_commit(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
    }


def _write_json(path: Path, payload: Any, *, exclusive: bool = False, safe: bool = False) -> None:
    """Serialise first, then write, so a payload that cannot be written leaves nothing behind.
    `exclusive` refuses an existing file; `safe` writes what JSON cannot hold as its `repr`."""
    text = json.dumps(payload, indent=1, ensure_ascii=False, default=repr if safe else None) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x" if exclusive else "w", encoding="utf-8") as handle:
        handle.write(text)


def _exception_record(exc: BaseException) -> dict[str, Any]:
    return {
        "type": type(exc).__name__,
        "message": str(exc),
        "traceback": traceback.format_exception(exc),
    }


def _append_fault(path: Path, exc: BaseException, out: Mapping[str, Any]) -> None:
    """Attempt 2 §3: *"the run's output records every §3 failure and fix"*. **[reading]** the
    failure is recorded here, and its fix by the commit that makes it, which fills in
    `fixed_by_commit`. **[reading]** pinning and join failures come before §3, when no readout
    exists either, and are recorded the same way."""
    entries = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    if isinstance(exc, InstrumentFault):
        stage = "attempt 2 §3: the consistency checks"
    elif isinstance(exc, GateError):
        stage = "before §3: pinning, the join, or reading the inputs"
    else:
        stage = "before any licence: an unexpected error"
    entries.append(
        {
            "recorded_at": _now(),
            "attempt": 2,
            "stage": stage,
            "exception": _exception_record(exc),
            "consistency": exc.consistency if isinstance(exc, InstrumentFault) else None,
            "pinning": out.get("pinning"),
            "readouts_computed": False,
            "generated_under": _generated_under(),
            "fixed_by_commit": None,
        }
    )
    _write_json(path, entries, safe=True)


def _fetch_inputs() -> dict[str, Any]:  # pragma: no cover - the real fetch, on the Mac
    from bzk.sources.pride import fetch

    sites = fetch(PXD032267_SITES, home=HOME)
    parameters = fetch(PXD032267_PARAMETERS, home=HOME)
    return {
        "sites_path": sites.path,
        "parameters_path": parameters.path,
        "published": load_published(),
        "facts": load_deposit_facts(),
    }


def _attempt1(kwargs: dict[str, Any], fixtures_dir: Path) -> int:  # pragma: no cover - refused
    """Attempt 1's write, unchanged. Unreachable while its fixture exists: `refusal` says no."""
    import scipy

    published = kwargs["published"]
    result = run(attempt=1, **kwargs)
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
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    path = fixtures_dir / FIXTURE_NAME
    path.write_text(json.dumps(fixture, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[pxd032267_gate] G: {result['gate_g']['status']}; wrote {path}")
    return 0


def _attempt2(kwargs: dict[str, Any], fixtures_dir: Path) -> int:
    """Attempt 2, with its §3 faults and its §5 marker.

    - Before a licence exists, a failure — §3's `InstrumentFault`, or an earlier `GateError` — is
      appended to the faults file, and no attempt-2 fixture is written.
    - The moment a licence exists, the started marker is written: timestamp, commit, digests. Any
      exception after that point is written **into the marker**, with every readout block computed
      before it, and the run ends. The marker blocks every repeat (`refusal`).
    - On success the fixture is written exclusively (an existing file is never overwritten), and
      the marker records that it completed.
    """
    published: Published = kwargs["published"]
    label = attempt2_label()
    started = fixtures_dir / STARTED_NAME_ATTEMPT2
    fixture_path = fixtures_dir / FIXTURE_NAME_ATTEMPT2
    out: dict[str, Any] = {}
    licensed: list[ReadoutLicence] = []

    def on_licence(licence: ReadoutLicence) -> None:
        if not isinstance(licence, ConsistencyPassed) or licence.issued_by != "run":
            raise InstrumentFault(f"main was handed {licence!r}, not a licence run() minted")
        _write_json(
            started,
            {
                "state": "readouts started",
                "label": label,
                "attempt": 2,
                "started_at": _now(),
                "generated_under": _generated_under(),
                "sites_content_hash": out["pinning"]["sites"]["content_hash"],
                "parameters_content_hash": out["pinning"]["parameters"]["content_hash"],
                "licence": repr(licence),
                "note": "attempt 2 §5: from here a defect is reported, never corrected; this "
                "file blocks every repeat",
            },
            exclusive=True,
        )
        licensed.append(licence)

    try:
        result = run(attempt=2, **kwargs, on_licence=on_licence, output=out)
        fixture = {
            "dataset": "PXD032267",
            "registration": REGISTRATION_ATTEMPT2.relative_to(REPO_ROOT).as_posix(),
            "governing_registration": REGISTRATION.relative_to(REPO_ROOT).as_posix(),
            "attempt": 2,
            "rounding_decimals": ATTEMPT_ROUNDING_DECIMALS[2],
            "input_tolerance": ATTEMPT_INPUT_TOLERANCE[2],
            "label": label,
            "reference_fixture": result["consistency"]["reference_fixture"],
            "reference_fixture_sha256": result["consistency"]["reference_fixture_sha256"],
            "published_tables": PUBLISHED_TABLES.relative_to(REPO_ROOT).as_posix(),
            "published_tables_source_sha256": published.source_sha256,
            "sites_content_hash": result["pinning"]["sites"]["content_hash"],
            "parameters_content_hash": result["pinning"]["parameters"]["content_hash"],
            "author_parameters_present": result["author_parameters"] is not None,
            **result,
            "generated_by": f"{GENERATED_BY} --attempt 2",
            "generated_under": _generated_under(),
        }
        _write_json(fixture_path, fixture, exclusive=True)
    except BaseException as exc:
        if licensed:
            record = json.loads(started.read_text(encoding="utf-8"))
            record.update(
                {
                    "state": "ended by an exception after readouts started",
                    "ended_at": _now(),
                    "exception": _exception_record(exc),
                    "completed": {
                        "consistency": out.get("consistency"),
                        "readouts": out.get("readouts"),
                        "readout_d": out.get("readout_d"),
                        "note": "every block written before the exception; a block missing its "
                        "later keys is the one the exception interrupted",
                    },
                }
            )
            _write_json(started, record, safe=True)
            where = started
        elif isinstance(exc, Exception):
            _append_fault(fixtures_dir / FAULTS_NAME_ATTEMPT2, exc, out)
            where = fixtures_dir / FAULTS_NAME_ATTEMPT2
        if not isinstance(exc, Exception):
            raise
        print(f"[pxd032267_gate] attempt 2 ended: {exc}; recorded in {where}", file=sys.stderr)
        return 1
    record = json.loads(started.read_text(encoding="utf-8"))
    record.update(
        {
            "state": "completed",
            "ended_at": _now(),
            "fixture": fixture_path.name,
            "fixture_sha256": _sha256(fixture_path),
        }
    )
    _write_json(started, record)
    print(f"[pxd032267_gate] attempt 2: §3 passed; wrote {fixture_path}")
    return 0


def main(
    argv: Sequence[str] | None = None,
    *,
    fixtures_dir: Path = FIXTURES_DIR,
    inputs: Callable[[], dict[str, Any]] | None = None,
) -> int:
    """`--attempt {1,2}`, required. Refuses before fetching or computing anything when the
    attempt's record already exists (`refusal`). `fixtures_dir` and `inputs` exist so a synthetic
    test can run it; the real run uses neither."""
    parser = argparse.ArgumentParser(prog=GENERATED_BY)
    parser.add_argument(
        "--attempt",
        type=int,
        choices=sorted(ATTEMPT_ROUNDING_DECIMALS),
        required=True,
        help="1: walk/PREREG-PXD032267-gate.md; 2: walk/PREREG-PXD032267-gate-attempt2.md",
    )
    attempt = int(parser.parse_args(argv).attempt)
    reason = refusal(attempt, fixtures_dir=fixtures_dir)
    if reason is not None:
        print(f"[pxd032267_gate] refused: {reason}", file=sys.stderr)
        return 2
    kwargs = (_fetch_inputs if inputs is None else inputs)()
    if attempt == 1:
        return _attempt1(
            kwargs, fixtures_dir
        )  # pragma: no cover - refused while its fixture exists
    return _attempt2(kwargs, fixtures_dir)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv[1:]))
