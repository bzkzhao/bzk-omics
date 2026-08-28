"""The three enumerations of ADR numbers, checked against each other and against the directory.

**The class this closes.** `decisions/README.md` records it: *a number is reserved in two places and
written in one, and nothing checks the three against each other — no test reads `decisions/`.* It
bit on 2026-08-09 with both tables stale at once — `0004` and `0013` written, `Accepted`, and still
listed as Queued; `0018` reserved by `ARCHITECTURE.md` §5 and missing from the Queued table. Both
were reconciled **by hand**, which is why a green first run is evidence about that reconciliation
rather than about the class.

**Four surfaces, three of them records.** `ARCHITECTURE.md` §5's seed list, README's **Written**
table and README's **Queued** table each *record* numbers; `decisions/` is the **referent** they are
about. A directory cannot disagree with itself, so every assertion below compares a record against
the directory or against another record.

**One tempting relationship is not an invariant and is not asserted.** §5 holds `0001`–`0018` and
nothing beyond, so *every Written entry appears in §5* is false by construction — `0019`–`0025` were
never seeded. What §5 supports is its unstruck set (which must equal Queued) and its header's count
claim (*all but one are written*), and both are asserted.

**A struck number means written; a struck description does not.** `0007`'s seed line strikes the
number *and* its wording, because the seed was wrong. `_seed_numbers` reads the strike on the number
only, so a correction mark inside the prose carries no membership meaning.

**Every parsed set carries a pinned count, and that is the load-bearing half.** A Markdown table
drifts, and a regex that matches nothing compares equal to anything else that matched nothing — the
tautology shape, and the omission failure `tests/test_query_absence_coverage.py` was built against.
This was not hypothetical here: the first row-regex written for this module matched **zero** Written
rows against a table holding 24, and every set comparison would have been green. So the counts below
are asserted before the sets are compared, and emptying a table is one of the recorded mutations.

**No assertion here reads git.** The round-trip the status convention describes (`Proposed` →
review → `Accepted`) *is* readable from history in a working tree, but
`tests/test_tautology_sweep.py` runs the whole suite inside a copy that excludes `.git`, where
`git log` returns *fatal: not a git repository* — so a git-dependent assertion would turn that
module red for a reason unrelated to what it checks. The measurement lives in `decisions/README.md`
instead.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECISIONS = ROOT / "decisions"
README = DECISIONS / "README.md"
ARCHITECTURE = ROOT / "ARCHITECTURE.md"

#: The counts at `fdc8ef3`, pinned so a parser that stops matching fails loudly instead of
#: comparing two empty sets. A legitimate addition moves these in the same commit — the same
#: discipline `tests/test_tautology_sweep.py`'s floor carries, and for the same reason.
EXPECTED_FILES = 26
EXPECTED_WRITTEN_ROWS = 26
EXPECTED_QUEUED_ROWS = 1
EXPECTED_SEED_LINES = 18
EXPECTED_SEED_STRUCK = 17

#: The three status values `decisions/README.md` names, and their counts here.
EXPECTED_STATUSES = {"Accepted": 17, "Proposed": 6, "Superseded": 3}

#: Supersessions recorded on one side only, with the reason each is permitted.
#:
#: `0014` carries `Superseded by | ADR-0017` and `0017` carries `Supersedes | —`. The fact is
#: recorded in three other places — `0014`'s own header, README's Written row for `0014`, and
#: `ARCHITECTURE.md` §5's *reversed by `0017`* — so what is missing is the reciprocal row and not
#: the decision. **It is not fixed by editing `0017`**: that record is `Accepted`, and README's
#: convention has held strictly since 2026-08-07 that an Accepted ADR is amended only by a
#: superseding ADR. Pinned as an exception rather than worked around, so a **second** one-sided
#: pair fails — the `NOT_A_QUERY` shape, loud by construction.
ONE_SIDED_SUPERSESSION: frozenset[tuple[str, str]] = frozenset({("0017", "0014")})


def _section(text: str, heading: str) -> str:
    """The body under one Markdown heading, to the next heading of any level."""
    out: list[str] = []
    inside = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == heading:
            inside = True
            continue
        if inside and stripped.startswith("#"):
            break
        if inside:
            out.append(line)
    return "\n".join(out)


def _written() -> list[tuple[str, str]]:
    """`(number, link target)` per Written row."""
    body = _section(README.read_text(), "## Written")
    return re.findall(r"^\|\s*\[(\d{4})\]\(([^)]+)\)\s*\|", body, re.MULTILINE)


def _queued() -> list[str]:
    body = _section(README.read_text(), "## Queued")
    return re.findall(r"^\|\s*(\d{4})\s*\|", body, re.MULTILINE)


def _seed_lines() -> list[tuple[str, bool]]:
    """`(number, is struck)` per seed line. The strike read is the **number's**, not the prose's."""
    body = _section(ARCHITECTURE.read_text(), "## 5. Seed ADRs")
    return [
        (number, bool(open_mark and close_mark))
        for open_mark, number, close_mark in re.findall(
            r"^- (~~)?`(\d{4})`(~~)?", body, re.MULTILINE
        )
    ]


def _files() -> list[str]:
    return sorted(p.name[:4] for p in DECISIONS.glob("[0-9][0-9][0-9][0-9]-*.md"))


def _header(text: str, field: str) -> str | None:
    match = re.search(rf"^\|\s*{field}\s*\|\s*(.*?)\s*\|\s*$", text, re.MULTILINE)
    return match.group(1) if match else None


def _records() -> dict[str, tuple[str | None, str | None, str | None]]:
    """`number -> (Status, Supersedes, Superseded by)` for every record on disk."""
    out = {}
    for path in sorted(DECISIONS.glob("[0-9][0-9][0-9][0-9]-*.md")):
        text = path.read_text()
        out[path.name[:4]] = (
            _header(text, "Status"),
            _header(text, "Supersedes"),
            _header(text, "Superseded by"),
        )
    return out


# ── Non-vacuity: the parsers find what they claim to parse ──────────────────────────────────────


def test_every_parser_finds_its_table() -> None:
    """**The half without which none of the rest means anything.**

    Each comparison below is between two parsed sets, and two failed parses compare equal. The
    counts are therefore asserted first, against integers that a legitimate addition moves in the
    same commit. Written before the comparisons for the reason the module docstring records: the
    first regex tried here matched zero rows against a table of 24.
    """
    assert len(_files()) == EXPECTED_FILES
    assert len(_written()) == EXPECTED_WRITTEN_ROWS
    assert len(_queued()) == EXPECTED_QUEUED_ROWS
    seeds = _seed_lines()
    assert len(seeds) == EXPECTED_SEED_LINES
    # `if struck` is the whole point of the line and was missing in the first draft, which
    # counted all 18 seeds and compared them against 17. Caught by the pinned count rather
    # than by review — the assertion named a field it did not read.
    assert sum(1 for _, struck in seeds if struck) == EXPECTED_SEED_STRUCK


# ── The three enumerations against the directory and each other ─────────────────────────────────


def test_the_written_table_and_the_directory_agree_in_both_directions() -> None:
    """A file with no row is invisible to a reader of the index; a row with no file is a broken
    link. Both directions, because the 2026-08-09 staleness was one of each."""
    written = {number for number, _ in _written()}
    files = set(_files())
    assert written - files == set(), "Written rows naming no file"
    assert files - written == set(), "files with no Written row"


def test_every_written_link_resolves() -> None:
    """The number agreeing is not the link agreeing: a row may name `0022` and point at the wrong
    file. Checked against the filesystem rather than against the number parsed beside it."""
    missing = [link for _, link in _written() if not (DECISIONS / link).exists()]
    assert missing == []


def test_the_queued_table_and_the_unstruck_seeds_agree() -> None:
    """The disagreement of 2026-08-09, in the form it took: §5 reserved `0018` and Queued did not.

    §5's *struck* set is deliberately not compared against Written — `0019`–`0025` were never
    seeded, so that relationship is false by construction and asserting it would fail on seven
    records that are in no way wrong.
    """
    unstruck = {number for number, struck in _seed_lines() if not struck}
    assert unstruck == set(_queued())


def test_a_queued_number_is_not_also_written() -> None:
    """The other half of 2026-08-09: `0004` and `0013` were written and still listed as Queued.
    Queued's stated job is reserving numbers, so a number in both tables is a reservation for
    something that exists."""
    assert {number for number, _ in _written()} & set(_queued()) == set()


def test_the_seed_lists_header_claim_is_true() -> None:
    """§5's header says *all but one are written*, which is a count claim about the directory and
    goes stale silently. It was wrong once already — only `0005` and `0017` were struck while
    eleven more had been written."""
    seeded = {number for number, _ in _seed_lines()}
    unwritten = seeded - set(_files())
    assert unwritten == set(_queued())
    assert len(unwritten) == 1, "the header says all but one"


# ── The status convention (decisions/README.md) ─────────────────────────────────────────────────


def test_every_status_is_one_of_the_three_named_values() -> None:
    """A fourth value would be a state nobody decided what to do about — and `Draft` or `Active`
    would read as a status while meaning nothing the convention defines."""
    # `_header` returns `None` for a record with no Status row, and that must reach the assertion
    # rather than being filtered out — a record without the field is exactly what this refuses.
    statuses = [status or "MISSING" for status, _, _ in _records().values()]
    assert set(statuses) <= {"Accepted", "Proposed", "Superseded"}
    counted = {value: statuses.count(value) for value in sorted(set(statuses))}
    assert counted == EXPECTED_STATUSES


def test_every_superseded_record_names_a_successor_that_exists() -> None:
    """`Superseded` without a live successor is a record that says it is obsolete and cannot say
    what replaced it — the retraction shape this project refuses everywhere else."""
    records = _records()
    for number, (status, _, superseded_by) in sorted(records.items()):
        if status != "Superseded":
            continue
        named = re.findall(r"(\d{4})", superseded_by or "")
        assert named, f"{number} is Superseded and names no successor"
        assert all(target in records for target in named), f"{number} names a missing successor"


def test_supersession_is_reciprocal_except_where_recorded() -> None:
    """**Found by writing this guard: one pair is one-sided, and it is `0017`/`0014`.**

    Asserted in both directions, with the known asymmetry pinned rather than tolerated. `0017` is
    `Accepted` and README's convention has held strictly since 2026-08-07 that an Accepted ADR is
    amended only by a superseding ADR — so completing its `Supersedes` row would breach the rule
    this directory exists to keep, and the fact it would record is already in three other places.
    A second one-sided pair fails here.
    """
    records = _records()
    forward = {
        (number, target)
        for number, (_, supersedes, _) in records.items()
        for target in re.findall(r"(\d{4})", supersedes or "")
    }
    backward = {
        (target, number)
        for number, (_, _, superseded_by) in records.items()
        for target in re.findall(r"(\d{4})", superseded_by or "")
    }
    assert forward - backward == set(), "a Supersedes with no matching Superseded by"
    assert backward - forward == ONE_SIDED_SUPERSESSION
