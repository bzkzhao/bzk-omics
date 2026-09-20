"""Place every row of PXD026748's Supplementary Table 1 at one stage of the platform path.

`python -m bzk.sources.pxd026748_published_cascade`, after the two files are in the content store.
Writes `tests/fixtures/pxd026748_published_cascade.json`: one record per published row, each lost
at exactly one stage or reaching the test, plus the counts.

**The stages are `bzk/published_cascade.py`'s, and this deposit reaches five of the six.** `join`,
`decoy_contaminant`, `localisation`, `ingestion`, `presence` — and then nothing. **There is no
significance stage here, and its absence is a fact about this turn rather than about the deposit.**
Significance belongs to the reconstruction, which needs a differential model this repository has
not run for `PXD026748`: which one it should run is `ADR-0035`'s open block question and
`ADR-0034`'s unstated imputation, both biting at that stage. So a row that clears `presence`
*reaches the test* — it is not *recovered*, and this module never says it was. The summary counts
the five stages it ran and does not report a sixth as having lost zero, because `significance: 0`
would read as a stage that ran and found nothing.

**A generator, not a transcription.** The figures this writes exist nowhere else; the point of
computing them from the bytes is `tests/test_pxd018299_refusals.py`'s, quoted in turn 13's module:
a fixture written from the documents it is supposed to check agrees with a sentence rather than
with the data. **This module reads no pre-registration and no report, carries no expected value in
an assertion, a default or a docstring, and compares its figures with nothing.** Scoring them
against `walk/PREREG-PXD026748-cascade.md` is the reviewer's, after the run.

**The populations are the ingestion's own.** The emitted observations, the refusals and the
declared localisation threshold all come from `pxd026748_ingest_figures._parse_arm`, which is
`replay_ingestion`'s own `_deposit_for` / `_adapter_for` pair. Its docstring gives the reason and it
holds here unchanged: an adapter configured from a different declaration is a second population
wearing the same name, and a cascade built over one would be measuring a path nobody runs.

**The window diagnostic never recovers a row.** For a row lost at `join` this records which deposit
rows carry the same `Sequence window`. That is a lead for a human, not a second key: recovering on
it would key a published claim to a row the publication's own identifier does not name, which is
the razor-pick inference §6.3 keeps out of an observation. `tests/test_pxd026748_published_cascade.py`
pins that the row stays lost.
"""

from __future__ import annotations

import collections
import json
import platform
import subprocess
import sys
from collections.abc import Mapping, Sequence
from datetime import UTC, date, datetime, time
from pathlib import Path
from typing import Any

from bzk import published_cascade as cascade
from bzk.adapters import maxquant, spreadsheet
from bzk.curation.loader import LoadedCuration
from bzk.provenance.raw_store import verify
from bzk.rebuild import _deposit_for
from bzk.sources.protein_groups import SupplementaryFile
from bzk.sources.pxd026748_ingest_figures import _parse_arm

REPO_ROOT = Path(__file__).resolve().parents[2]
CURATION_DIR = REPO_ROOT / "data" / "curation"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"
HOME = Path.home() / ".bzk-omics"

DIGLY_CURATION = CURATION_DIR / "curation_PXD026748.json"
FIXTURE_NAME = "pxd026748_published_cascade.json"

GENERATED_BY = "python -m bzk.sources.pxd026748_published_cascade"

#: Nature Immunology 22:1416-1427 (2021). A different article from the anchor's, which is why
#: `SupplementaryFile` carries a `doi` at all — see `bzk/sources/protein_groups.py`.
PXD026748_DOI = "10.1038/s41590-021-01035-8"

SUPP_TABLE_1 = SupplementaryFile(
    label="Nat Immunol Supplementary Table 1 (PLpro-sensitive ISGylation sites)",
    filename="41590_2021_1035_MOESM3_ESM.xlsx",
    expected_content_hash=(
        "sha256:872371eb9877c6aa1f85e82429e8354993cd4d10c643592ff8ee14012e36a870"
    ),
    doi=PXD026748_DOI,
)

#: The sheet the published table is on. The workbook has three (`walk/walk_PXD026748.json`), so the
#: reader is told which rather than taking the first.
SUPP_SHEET = "Table 1"

#: The two columns whose co-occurrence identifies the header row. **Which row is the header is not
#: recorded anywhere**, so it is found by content rather than by a position this module would be
#: guessing — the workbook is reported to carry a title row above it. These two are chosen because
#: they are the join key's own columns: a file that does not have both cannot be joined at all, so
#: failing to find them is a reason to stop rather than a reason to look harder.
HEADER_MARKERS = ("Uniprot ID", "Lysine position")

#: The published columns carried onto every record, verbatim and unparsed except where noted.
PUBLISHED_COLUMNS = (
    "#",
    "Cluster",
    "Uniprot ID",
    "Gene name",
    "Lysine position",
    "Multiplicity",
    "Sequence window",
)

#: The paper's valid-value rule, admitted as Route A in `walk/RESULT-PXD026748-multiplicity.md`:
#: at least this many positive values in at least one (genotype, treatment) group.
MIN_VALID_IN_A_GROUP = 3

#: The stages this deposit reaches, in order. Deliberately not `cascade.STAGES`, which ends with
#: `significance` — see the module docstring.
STAGES_RUN = (
    cascade.STAGE_JOIN,
    cascade.STAGE_DECOY_CONTAMINANT,
    cascade.STAGE_LOCALISATION,
    cascade.STAGE_INGESTION,
    cascade.STAGE_PRESENCE,
)

#: Where a row that clears all five ends up. Not `cascade.RECOVERED`: nothing here has been tested.
REACHES_TEST = "reaches_test"

REASON_NO_KEY_MATCH = "no_key_match"
REASON_AMBIGUOUS_KEY = "ambiguous_key"
REASON_COERCED_KEY = "coerced_key"
REASON_NOT_EMITTED = "not_emitted"
REASON_PRESENCE_RULE = "presence_rule"

#: The two published columns the join key is built from. Named so `REASON_COERCED_KEY` and the key
#: itself cannot come to disagree about which columns matter.
KEY_COLUMNS = ("Uniprot ID", "Lysine position")

#: The types `openpyxl` returns for a cell the spreadsheet stored as a date or a time, which JSON
#: cannot serialise. **This is not a hypothetical.** Run on the real supplement at `a33472f` the
#: generator computed every record and then died at `write_text` with `TypeError: Object of type
#: datetime is not JSON serializable`; nothing was written, so the no-partial-fixture property
#: held and the defect surfaced as a failure rather than as a fixture. Two cells are involved, both
#: in `Gene name` — the familiar case of spreadsheet software turning a gene symbol into a date.
#:
#: `datetime` is a subclass of `date`, so the type is reported as `type(value).__name__`: what
#: matters to a reader is which one `openpyxl` handed back, not which one it also is.
COERCED_TYPES = (datetime, date, time)

#: What a published cell may be once `_published_value` has run, and therefore what `json` will be
#: asked to serialise. A cell of any other type stops the run by name — see `_published_value`.
SERIALISABLE_TYPES = (str, int, float, bool, type(None))


class CascadeSourceError(ValueError):
    """The published table cannot be read as given. Never downgraded to a warning."""


# ── reading the published table ─────────────────────────────────────────────────────────────────


def header_row_index(rows: Sequence[Sequence[str]]) -> int:
    """The 0-based index of the one row carrying every `HEADER_MARKERS` column.

    Raises where there is not exactly one. **Zero and two are different defects and the message
    says which**: zero means this is not the sheet, or the columns were renamed; two means the
    table has a repeated header, and picking the first would silently drop or duplicate rows
    depending on which block the caller then read.
    """
    wanted = set(HEADER_MARKERS)
    matches = [i for i, row in enumerate(rows) if wanted <= {str(c).strip() for c in row}]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise CascadeSourceError(
            f"no row carries all of {list(HEADER_MARKERS)}, so the header cannot be located by "
            f"content and nothing can be joined. Read {len(rows)} row(s)."
        )
    raise CascadeSourceError(
        f"{len(matches)} rows carry all of {list(HEADER_MARKERS)} (0-based indices {matches}); "
        "the header must be unique, because choosing one of two would decide silently which block "
        "of rows is data."
    )


def published_rows(source: Path | bytes, *, sheet: str | None = SUPP_SHEET) -> list[dict[str, Any]]:
    """Every data row of the published table, keyed by its header, in file order."""
    cells = spreadsheet.rows(source, sheet=sheet)
    text = [["" if c is None else str(c) for c in row] for row in cells]
    index = header_row_index(text)
    header = [str(c).strip() for c in text[index]]
    return [
        {name: value for name, value in zip(header, row, strict=False) if name}
        for row in cells[index + 1 :]
        if any(c is not None and str(c).strip() for c in row)
    ]


# ── the arithmetic, pure ────────────────────────────────────────────────────────────────────────


def _text(value: object) -> str:
    """One cell as the text a key is built from.

    An integral float becomes its integer: `openpyxl` returns `90.0` for a position typed as a
    number, and `'90.0'` would match no deposit row while looking like a key. Recorded here rather
    than at each call site so the published side and the deposit side cannot normalise differently.
    """
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return "" if value is None else str(value).strip()


def _coerced_type(value: object) -> str | None:
    """The type name where a published cell came back as a date or a time, else `None`."""
    return type(value).__name__ if isinstance(value, COERCED_TYPES) else None


def _published_value(column: str, value: object) -> Any:
    """One published cell as it goes into the record: ISO-8601 for a date or time, else unchanged.

    **Converted, not interpreted.** The ISO string is the cell *as found*, in a form JSON can hold;
    it says what the spreadsheet contains and makes no claim about what it was before the
    spreadsheet changed it. Mapping `2021-09-09` back to the gene symbol it replaced is an
    inference, and writing an inference where the source belongs is what `ONTOLOGY.md` §6.3 keeps
    out of an observation. The record flags the cell instead, and a reader with the paper can do
    the rest.

    **Anything else stops the run by name.** `openpyxl` can also return a `timedelta` for a
    duration-formatted cell, which has no `isoformat` and which JSON cannot hold either. Rather
    than stringify an unknown type — inventing a representation nobody chose — this raises with
    the column and the type, so the next such cell is a named refusal at build time instead of the
    opaque `TypeError` at `write_text` that this turn exists to fix.
    """
    if isinstance(value, COERCED_TYPES):
        return value.isoformat()
    if not isinstance(value, SERIALISABLE_TYPES):
        raise CascadeSourceError(
            f"published column {column!r} holds a {type(value).__name__}, which JSON cannot "
            f"serialise and this module does not know how to record as found. Value: {value!r}. "
            "Add its type to COERCED_TYPES with the form it should take, rather than letting a "
            "representation be chosen for it."
        )
    return value


def sample_groups(curation: LoadedCuration) -> dict[str, list[str]]:
    """`(genotype, treatment)` → the mapping keys in it, which are the deposit's column names.

    Read off the curation record, never off the run labels: the record is what states which run is
    which condition, and parsing a condition back out of a filename is the inference its `basis`
    already declares (`filename_inference`, I8).
    """
    groups: dict[str, list[str]] = collections.defaultdict(list)
    for sample in curation.sample_mapping().samples:
        label = f"{sample.get('genotype')} | {sample.get('treatment')}"
        groups[label].append(str(sample.get("mapping_key", "")))
    return {k: sorted(v) for k, v in sorted(groups.items())}


def _positive(row: Sequence[str], column: Mapping[str, int], name: str) -> bool:
    value = maxquant.cell_value(row, column, name)
    return value is not None and value > 0


def _clears_presence(
    row: Sequence[str], column: Mapping[str, int], groups: Mapping[str, Sequence[str]]
) -> bool:
    """The paper's valid-value rule on the **summed** intensities.

    Summed and not per-multiplicity: the mapping key names the summed column, and the rule the
    paper states is about a site's values, not about one multiplicity of it. The per-multiplicity
    columns are recorded per record as a flag and are never counted here.
    """
    return any(
        sum(1 for name in names if _positive(row, column, name)) >= MIN_VALID_IN_A_GROUP
        for names in groups.values()
    )


def _multiplicity_flag(
    row: Sequence[str], column: Mapping[str, int], groups: Mapping[str, Sequence[str]]
) -> bool:
    """Whether the matched deposit row carries any positive `…___2` or `…___3` value."""
    return any(
        _positive(row, column, f"{name}___{n}")
        for names in groups.values()
        for name in names
        for n in (2, 3)
    )


def build(
    *,
    published: Sequence[Mapping[str, Any]],
    deposit: maxquant.MaxQuantTable,
    emitted_rows: frozenset[str] | set[str],
    refused_rows: Mapping[str, str],
    groups: Mapping[str, Sequence[str]],
    localization_threshold: float,
) -> list[dict[str, Any]]:
    """One record per published row, placed at exactly one stage. Pure.

    Every argument is a population someone else measured: `deposit` is the table the adapter read,
    `emitted_rows` and `refused_rows` come off the adapter's own report, and `groups` comes off the
    curation record. Nothing here re-derives any of them.
    """
    column = {name: i for i, name in enumerate(deposit.header)}
    by_key: dict[tuple[str, str], list[Sequence[str]]] = collections.defaultdict(list)
    for row in deposit.rows:
        by_key[_text(row[column["Protein"]]), _text(row[column["Position"]])].append(row)

    window_column = column.get("Sequence window")
    by_window: dict[str, list[str]] | None = None
    if window_column is not None:
        by_window = collections.defaultdict(list)
        for row in deposit.rows:
            by_window[_text(row[window_column])].append(_text(row[column["id"]]))

    records: list[dict[str, Any]] = []
    for cells in published:
        raw = {name: cells.get(name) for name in PUBLISHED_COLUMNS}
        coerced = [
            {"column": name, "as_found": _published_value(name, value), "type": kind}
            for name, value in raw.items()
            if (kind := _coerced_type(value)) is not None
        ]
        record: dict[str, Any] = {
            "published": {name: _published_value(name, value) for name, value in raw.items()},
            # Empty for almost every row, and present on all of them: a key that appears only where
            # something went wrong is a key a reader has to know to look for.
            "coerced_cells": coerced,
            "deposit_id": None,
            "lost_at": None,
            "loss_reason": None,
            "has_positive_multiplicity_column": None,
        }
        records.append(record)

        # A lead, never a key. `None` where the deposit has no `Sequence window` column at all,
        # because an empty list there would assert that no row shares the window. Computed here
        # rather than in a closure over `cells`: a function defined inside the loop that reads the
        # loop's variable is the late-binding trap, and it is one dict lookup.
        window_lead = (
            None if by_window is None else by_window.get(_text(cells.get("Sequence window")), [])
        )

        # **A coerced key is refused by name, before `_text` ever sees it.** `_text` would return
        # `'2021-09-09 00:00:00'` for a date — a non-empty string that looks like a key, matches no
        # deposit row, and loses the row as an ordinary `no_key_match`. The coercion would then be
        # invisible in the one place it changed an outcome. Nothing in the supplement hits this:
        # both of its coerced cells are in `Gene name`. This exists so that if it ever happened it
        # would be named rather than absorbed.
        if any(entry["column"] in KEY_COLUMNS for entry in coerced):
            record["lost_at"] = cascade.STAGE_JOIN
            record["loss_reason"] = REASON_COERCED_KEY
            record["window_matches"] = window_lead
            continue

        hits = by_key.get((_text(cells.get("Uniprot ID")), _text(cells.get("Lysine position"))), [])
        if len(hits) != 1:
            record["lost_at"] = cascade.STAGE_JOIN
            record["loss_reason"] = REASON_NO_KEY_MATCH if not hits else REASON_AMBIGUOUS_KEY
            record["window_matches"] = window_lead
            if len(hits) > 1:
                record["ambiguous_ids"] = [_text(r[column["id"]]) for r in hits]
            continue

        # `matched` rather than reusing `row`: the index loops above bind `row` to a deposit row
        # and this is the one that survived the join. One name for two populations in one function
        # is how a later edit reads the wrong one.
        matched = hits[0]
        row_id = _text(matched[column["id"]])
        record["deposit_id"] = row_id
        record["has_positive_multiplicity_column"] = _multiplicity_flag(matched, column, groups)

        reverse = column.get("Reverse")
        contaminant = column.get("Potential contaminant")
        if reverse is not None and matched[reverse] == "+":
            record["lost_at"] = cascade.STAGE_DECOY_CONTAMINANT
            record["loss_reason"] = "reverse"
            continue
        if contaminant is not None and matched[contaminant] == "+":
            record["lost_at"] = cascade.STAGE_DECOY_CONTAMINANT
            record["loss_reason"] = "potential_contaminant"
            continue

        prob = _text(matched[column["Localization prob"]])
        if not prob or float(prob) < localization_threshold:
            record["lost_at"] = cascade.STAGE_LOCALISATION
            record["loss_reason"] = "localization_prob_below_threshold"
            continue

        if row_id not in emitted_rows:
            record["lost_at"] = cascade.STAGE_INGESTION
            # The adapter's own reason where it refused the row, and a distinct slug where it did
            # not: a row that is neither emitted nor refused is a third state, and calling it
            # refused would invent a reason the adapter never gave.
            record["loss_reason"] = refused_rows.get(row_id, REASON_NOT_EMITTED)
            continue

        if not _clears_presence(matched, column, groups):
            record["lost_at"] = cascade.STAGE_PRESENCE
            record["loss_reason"] = REASON_PRESENCE_RULE
    return records


def summary(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """The stage counts, their reasons, and the breakdowns — all from the records above.

    Placement is read through `cascade.outcome`, which refuses a record that is lost at two stages
    or at none, so the sum below cannot be made to balance by a record that contradicts itself.
    """
    ends = [cascade.outcome(dict(r)) for r in records]
    reaching = [r for r, end in zip(records, ends, strict=True) if end == cascade.RECOVERED]

    lost: dict[str, Any] = {}
    for stage in STAGES_RUN:
        at_stage = [r for r, end in zip(records, ends, strict=True) if end == stage]
        reasons = collections.Counter(str(r["loss_reason"]) for r in at_stage)
        lost[stage] = {"count": len(at_stage), "reasons": dict(sorted(reasons.items()))}

    clusters = collections.Counter(str(r["published"].get("Cluster")) for r in reaching)
    # Over **every** record, not only the ones that reached the test: a coerced cell is a fact
    # about the supplement, and counting it only where it survived would report a property of the
    # cascade as a property of the file.
    by_column = collections.Counter(
        str(entry["column"]) for r in records for entry in r.get("coerced_cells", ())
    )
    coerced_rows = [r["published"].get("#") for r in records if r.get("coerced_cells")]
    return {
        "published_rows": len(records),
        "stages_run": list(STAGES_RUN),
        # What the spreadsheet turned into a date or a time, by column, and which rows. No symbol
        # is inferred for any of them — see `_published_value`.
        "coerced_cells": {"by_column": dict(sorted(by_column.items())), "rows": coerced_rows},
        # Named rather than `recovered`: these rows reached a test this repository has not run.
        REACHES_TEST: len(reaching),
        "lost": lost,
        "reaches_test_by_cluster": dict(sorted(clusters.items())),
        # Two counts, because "flagged multiplicity-2" has two readings and neither is the other.
        # The first is what the publication wrote in its `Multiplicity` column; the second is what
        # the deposit row carries in its `…___2` / `…___3` columns. They are different measurements
        # of different files and are reported as such.
        "reaches_test_published_multiplicity_2": sum(
            1 for r in reaching if _text(r["published"].get("Multiplicity")) == "2"
        ),
        "reaches_test_with_positive_multiplicity_column": sum(
            1 for r in reaching if r["has_positive_multiplicity_column"]
        ),
    }


# ── the IO ──────────────────────────────────────────────────────────────────────────────────────


def _commit() -> dict[str, Any]:
    """`HEAD` and whether the tree is clean, or `null`s where git cannot answer.

    **Tolerant of not being in a work tree, which the anchor's equivalent is not.** This was found
    by a test rather than reasoned: `tests/test_tautology_sweep.py` re-runs a recorded mutation in
    a copy of the repository made *without* `.git`, and the moment a test here called `main()`
    end to end, `git rev-parse HEAD` exited 128 and took the whole evidence run red — a module
    unrelated to this one failing because provenance was mandatory.

    `null` rather than a placeholder string: a fixture whose `commit` reads `"unknown"` asserts a
    commit by that name, and one whose `working_tree_clean` reads `false` asserts a dirty tree
    that was never looked at. The generator's real run happens inside the work tree, where both
    fields are populated; a run from anywhere else says so.
    """

    def git(*args: str) -> str | None:
        try:
            done = subprocess.run(
                ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True
            )
        except (OSError, subprocess.CalledProcessError):
            return None
        return done.stdout.strip()

    status = git("status", "--porcelain")
    return {
        "commit": git("rev-parse", "HEAD"),
        "working_tree_clean": None if status is None else not status,
    }


def fixture_for(
    records: Sequence[Mapping[str, Any]],
    *,
    curation: LoadedCuration,
    groups: Mapping[str, Sequence[str]],
    generated_at: str,
) -> dict[str, Any]:
    """The committed record: provenance, both files by name and hash, the summary, then the rows."""
    from bzk.ontology.invariants import NODE_TYPE_KEY

    dataset = next(n for n in curation.nodes if n[NODE_TYPE_KEY] == "Dataset")
    return {
        "dataset": str(dataset["external_accession"]),
        "published_file": SUPP_TABLE_1.filename,
        "published_content_hash": SUPP_TABLE_1.expected_content_hash,
        "published_sheet": SUPP_SHEET,
        "deposit_file": str(dataset["label"]),
        "deposit_content_hash": str(dataset["content_hash"]),
        "path": "platform",
        "note": (
            "Every row of PXD026748's Supplementary Table 1, joined to the deposit's site table on "
            "(Uniprot ID, Lysine position) against (Protein, Position) and walked through the "
            "PLATFORM path: join, decoy/contaminant, localisation, ingestion, presence. A row "
            "clearing all five REACHES THE TEST; it is not recovered, and no significance stage "
            "ran — that is the reconstruction, which this repository has not performed for this "
            "deposit. Rows lost at `join` carry `window_matches`, the ids of deposit rows sharing "
            "their Sequence window: a lead for a reader, never a second key, and the generator "
            "never recovers a row on it. Cells the spreadsheet stored as a date or a time are "
            "recorded AS FOUND, as ISO-8601 strings, and listed per row in `coerced_cells` and "
            "per column in the summary; no symbol is inferred for any of them, because writing an "
            "inference where the source belongs is not this file's job. Generated from both "
            "files' bytes through the adapter the "
            "curation record selects, never transcribed, and compared here with no registration "
            f"or report. Regenerate with `{GENERATED_BY}`."
        ),
        "generated_by": GENERATED_BY,
        "generated_under": {
            "generated_at": generated_at,
            **_commit(),
            "python": platform.python_version(),
            "presence_rule": (
                f"at least {MIN_VALID_IN_A_GROUP} positive summed intensities in at least one of "
                f"{len(groups)} (genotype, treatment) groups, from the curation record's mapping"
            ),
            "sample_groups": {k: list(v) for k, v in groups.items()},
        },
        "summary": summary(records),
        "rows": [dict(r) for r in records],
    }


def main(
    *,
    home: Path = HOME,
    fixtures_dir: Path = FIXTURES_DIR,
    curation_path: Path = DIGLY_CURATION,
    supplement: SupplementaryFile = SUPP_TABLE_1,
) -> int:
    """Read both files, build the records, then write. Nothing is written unless both are read.

    **`home`, `fixtures_dir`, `curation_path` and `supplement` are parameters with real defaults.**
    Turn 13's module parameterised the first two and its *"writes no partial fixture"* test could
    only reach the first guard, because no synthetic bytes can hash to a committed record's digest.
    Making the record and the supplement injectable closes that: a test can give `main` a record
    whose deposit is present and a supplement that is absent, and see the second guard fire.
    """
    generated_at = datetime.now(UTC).isoformat()

    curation, adapter, parsed = _parse_arm(curation_path, home)
    deposit_path = _deposit_for(curation, home)
    assert deposit_path is not None  # `_parse_arm` raised if it were not

    try:
        supplement_path = verify(
            supplement.expected_content_hash, filename=supplement.filename, home=home
        )
    except FileNotFoundError as exc:
        raise SystemExit(
            f"{supplement.filename} is not in the content store under {home}; fetch it from "
            f"{supplement.url} and re-run. No fixture was written."
        ) from exc

    published = published_rows(supplement_path)
    deposit = maxquant.read_table(deposit_path)
    groups = sample_groups(curation)
    records = build(
        published=published,
        deposit=deposit,
        emitted_rows=set(adapter.report.observation_of_row),
        refused_rows={r.row: r.reason for r in parsed.refusals},
        groups=groups,
        localization_threshold=adapter.declared.localization_threshold,
    )

    fixture = fixture_for(records, curation=curation, groups=groups, generated_at=generated_at)
    (fixtures_dir / FIXTURE_NAME).write_text(json.dumps(fixture, indent=2) + "\n")

    counts = fixture["summary"]
    print(f"[cascade] {counts['published_rows']:,} published row(s)")
    for stage in STAGES_RUN:
        print(f"[cascade]   lost at {stage:<19} {counts['lost'][stage]['count']:>5,}")
    print(f"[cascade]   reaching the test   {counts[REACHES_TEST]:>5,}")
    print(f"[cascade] wrote {fixtures_dir / FIXTURE_NAME}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
