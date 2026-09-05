"""`data/curation/analysis_*.json` — the format's vocabulary, and who actually reads it.

`bzk/curation/analysis_record.py` gives the format a runtime refusal: a key it does not define is
refused when a record is opened. That refusal is the weaker half of what is needed here, and the
module docstring says why — its vocabulary is the union of two dialects, so it recognises a key in
a record whose readers would never look for it.

**This module is the stronger half.** It derives, per committed record, which of that record's keys
its own readers read, and holds the remainder to `UNREAD` — a declared list with a ground for each
entry. A key added to a record must therefore be classified at the moment it is added: something
reads it, or it is named here with the reason it is carried anyway. That is the moment the defect
this pair closes actually occurs.

**The reads are derived from source, not asserted from memory.** `READERS` names each reader and
the expression its record is bound to; `_literal_reads` then takes the string subscripts and
`.get()` calls on that expression. Matching on the receiver rather than on the string is what keeps
`owned_by_the_record = {"n_sites_tested", ...}` in `tests/test_pxd018299_baseline.py` — a set that
names keys and reads none — from counting as four reads.

Offline: reads committed files only, and the one bad record it needs is built in `tmp_path` from a
copy of a good one.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any, NamedTuple

import pytest

from bzk.curation.analysis_record import (
    CORE_KEYS,
    CURATOR_KEYS,
    DERIVED_COUNT_KEYS,
    EXTERNAL_TOOL_KEYS,
    KNOWN_KEYS,
    AnalysisRecordInvalid,
    check_keys,
    read_record,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
CURATION_DIR = REPO_ROOT / "data" / "curation"
SEARCHED_DIRS = (REPO_ROOT / "bzk", REPO_ROOT / "tests")

PXD018299 = "analysis_PXD018299_KOIFN_vs_WTIFN.json"
PXD055843 = "analysis_PXD055843_siUSP24_IFN_vs_siC_IFN.json"


class _Reader(NamedTuple):
    """A module that reads keys out of an analysis record.

    `receivers` are the names the record is bound to in that file — a bare name, or the name of the
    helper that returns it, so `_record()["n_sites_tested"]` counts. `extra` is for a read this
    derivation cannot see, declared with the line that performs it. `records` are the records the
    file's keyed reads actually run over, which is not always every record it opens.
    """

    path: str
    receivers: tuple[str, ...]
    extra: tuple[str, ...]
    records: tuple[str, ...]


READERS = (
    # The one shipped reader. `declared()` and `locate()` both bind `_analysis_record()` to
    # `record`; the curation record it also opens is bound to nothing, so it cannot be confused
    # with this one.
    _Reader("bzk/sources/pxd055843_perseus.py", ("record",), (), (PXD055843,)),
    _Reader("tests/test_pxd055843_perseus.py", ("analysis",), (), (PXD055843,)),
    _Reader("tests/test_pxd018299_baseline.py", ("record", "_record"), (), (PXD018299,)),
    # Attributed to PXD018299 alone on purpose. Its keyed reads run over `CITING_RECORDS`, which
    # names that record and not the other; its discovery pass does read `file` off every JSON in
    # `data/curation/`, but through `json.loads(...).get("file")` — and attributing that here would
    # also attribute `dataset`, which nothing reads off the PXD055843 record.
    _Reader("tests/test_curation_content_hash.py", ("record", "_record"), (), (PXD018299,)),
    # `test_pending_markers_resolve_to_nulls` binds each record to `record` and reads `pending`;
    # `test_quantity_values_are_in_enum` walks every value looking for the key `quantity` by name,
    # which is a comparison rather than a subscript, so it is declared rather than derived.
    _Reader("tests/test_schema.py", ("record",), ("quantity",), (PXD018299, PXD055843)),
)

#: Files that name a committed record without reading a key out of it. Declared so the discovery
#: check below can insist that every file naming a record is one or the other.
MENTIONS = {
    # Transcribes the record's parameters into module constants and gives the reason: the record is
    # what its run is checked against, so consuming it would make the comparison circular.
    "bzk/sources/pxd018299_differential.py": "transcribes, and says why",
    # Writes a note into the baseline fixture pointing at the record for the three counts.
    "bzk/sources/pxd018299_baseline.py": "cites the record in a fixture note",
    # The format module: its docstring names PXD055843's record as the example of a record for an
    # analysis nobody here has repeated.
    "bzk/curation/analysis_record.py": "names a record in prose",
    "tests/test_analysis_record.py": "this module — it classifies both records' keys",
}

#: Per record, every key that record carries which no reader **of that record** reads, and why it is
#: carried anyway. Nothing here is repaired by deleting it: a record is a statement about an
#: analysis and a human reads it. What is refused is a key that is neither read nor declared, which
#: is the state every one of these was in before this list existed.
UNREAD: dict[str, dict[str, str]] = {
    PXD018299: {
        # These four are read — by `bzk/sources/pxd055843_perseus.py`, off the *other* record.
        # Nothing that opens this one looks at them, and `pxd018299_differential.py` holds the
        # executable form of all four as module constants rather than reading them here.
        "contrast": "read off the other record only; transcribed as CONTRAST in pxd018299_differential",
        "test": "read off the other record only; this run's test is chosen by the stats registry",
        "fdr_method": "read off the other record only; the run applies benjamini_hochberg by name",
        "filters_applied": "read off the other record only; the run's filters are its own constants",
        "localization_threshold": "no reader; the adapter writes its own from MaxQuantSiteAdapter",
        "presence_rule": "prose for a human; the executable form is PRESENCE_MIN / PRESENCE_EITHER",
        "protein_adjusted": "restates what the adapter writes on every row (I4 not_applied)",
    },
    PXD055843: {
        "dataset": "read only from records citing the PXD018299 deposit; nothing reads it here",
        "external_tool": "the adapter writes its own name; only external_version beside it is read",
        "localization_threshold": "no reader; the adapter writes null at protein grain for itself",
        "presence_rule": "prose restating filters_applied for a human",
        "protein_adjusted": "restates what the adapter writes on every row (I4 not_applied)",
        "rationale": "curator prose; the curation format's rationale reaches Analysis, this has no loader",
        "unresolved": "curator prose recording what could not be determined",
    },
}


def _committed() -> dict[str, dict[str, Any]]:
    """Every `analysis_*.json` in `data/curation/`, discovered rather than listed."""
    return {
        path.name: json.loads(path.read_text()) for path in CURATION_DIR.glob("analysis_*.json")
    }


def _is_receiver(node: ast.AST, receivers: tuple[str, ...]) -> bool:
    if isinstance(node, ast.Name):
        return node.id in receivers
    return (
        isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in receivers
    )


def _literal_reads(source: str, receivers: tuple[str, ...]) -> set[str]:
    """String keys read off `receivers` by subscript or `.get()`.

    A nested subscript — `record["imputation"]["n_values_total"]` — yields the outer key only; the
    inner receiver is a `Subscript`, not a name in `receivers`, which is right because this module
    classifies top-level keys.
    """
    keys: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Subscript) and _is_receiver(node.value, receivers):
            if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
                keys.add(node.slice.value)
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "get"
            and _is_receiver(node.func.value, receivers)
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            keys.add(node.args[0].value)
    return keys


def _reads_by_record() -> dict[str, set[str]]:
    """Per record name, the union of what its declared readers read out of it."""
    reads: dict[str, set[str]] = {name: set() for name in _committed()}
    for reader in READERS:
        found = _literal_reads((REPO_ROOT / reader.path).read_text(), reader.receivers)
        found |= set(reader.extra)
        for record in reader.records:
            reads[record] |= found & KNOWN_KEYS
    return reads


# ------------------------------------------------------------------------------------------------
# The vocabulary against the records on disk


def test_the_committed_records_are_found_and_accepted() -> None:
    """Both records pass the refusal, and the guard is not vacuous for want of a record."""
    paths = sorted(CURATION_DIR.glob("analysis_*.json"))
    assert paths, "data/curation/ holds no analysis record, so everything below asserts nothing"
    for path in paths:
        read_record(path)


def test_every_key_on_disk_is_defined_by_the_format() -> None:
    """The direction the refusal enforces, asserted against the committed records directly."""
    carried: set[str] = set()
    for keys in _committed().values():
        carried |= set(keys)
    undefined = sorted(carried - KNOWN_KEYS)
    assert not undefined, f"records carry {undefined}, which analysis_record.py does not define"


def test_every_defined_key_appears_in_a_record() -> None:
    """The converse, so the vocabulary cannot rot into fiction.

    The same reason `tests/test_curation_loader.py` asserts each declared structural key appears in
    a record on disk: a key nothing carries is a guess about a format, and a guess in a closed
    vocabulary is indistinguishable from a definition.
    """
    carried: set[str] = set()
    for keys in _committed().values():
        carried |= set(keys)
    invented = sorted(KNOWN_KEYS - carried)
    assert not invented, f"analysis_record.py defines {invented}, which no committed record carries"


def test_the_four_groups_partition_the_vocabulary() -> None:
    """`KNOWN_KEYS` is composed, so a key added to one group must not also sit in another."""
    groups = (CORE_KEYS, DERIVED_COUNT_KEYS, EXTERNAL_TOOL_KEYS, CURATOR_KEYS)
    total = sum(len(group) for group in groups)
    assert not total - len(KNOWN_KEYS), (
        f"the four groups overlap: {total} keys make {len(KNOWN_KEYS)}"
    )


# ------------------------------------------------------------------------------------------------
# The refusal


def test_an_undefined_key_is_refused_and_named(tmp_path: Path) -> None:
    """A copy of a good record with one key added — the shape a curator actually produces."""
    good = json.loads((CURATION_DIR / PXD055843).read_text())
    bad = tmp_path / PXD055843
    bad.write_text(json.dumps({**good, "n_sites_tested_": 1375}))
    with pytest.raises(AnalysisRecordInvalid) as exc:
        read_record(bad)
    message = str(exc.value)
    assert "n_sites_tested_" in message
    assert PXD055843 in message


def test_the_refusal_states_what_it_expected() -> None:
    """Naming the key alone leaves a curator unable to tell a typo from a key with no home."""
    with pytest.raises(AnalysisRecordInvalid) as exc:
        check_keys({"fdr_methd": "BH"}, source="somewhere.json")
    message = str(exc.value)
    assert "fdr_method" in message
    assert "unresolved" in message
    assert "tests/test_analysis_record.py" in message


def test_a_record_that_is_not_an_object_is_refused(tmp_path: Path) -> None:
    """`set(record)` over a list would be a set of its elements, which could pass by accident."""
    bad = tmp_path / "analysis_list.json"
    bad.write_text(json.dumps(["dataset", "file"]))
    with pytest.raises(AnalysisRecordInvalid) as exc:
        read_record(bad)
    assert "not an object" in str(exc.value)


# ------------------------------------------------------------------------------------------------
# What each record's own readers read


def test_the_declared_readers_exist_and_read_something() -> None:
    """A reader whose receiver name was renamed derives nothing, and would silently widen UNREAD."""
    for reader in READERS:
        path = REPO_ROOT / reader.path
        assert path.exists(), f"{reader.path} is declared a reader and is not in the tree"
        found = _literal_reads(path.read_text(), reader.receivers) | set(reader.extra)
        assert found & KNOWN_KEYS, (
            f"{reader.path} reads no analysis-record key through {reader.receivers} — the "
            "expression the record is bound to has been renamed, or the file stopped reading it"
        )


def test_each_records_unread_keys_are_exactly_the_declared_ones() -> None:
    """The check the runtime refusal cannot make: a key that is defined and still reaches nobody.

    Both directions. A key that stops being read must be classified rather than drift into being
    tolerated, and a key that starts being read must leave `UNREAD` rather than stay as a claim
    that is no longer true.
    """
    reads = _reads_by_record()
    for name, record in _committed().items():
        declared = UNREAD.get(name, {})
        carried = set(record)
        stale = sorted(set(declared) - carried)
        assert not stale, f"{name}: UNREAD names {stale}, which the record does not carry"
        now_read = sorted(set(declared) & reads[name])
        assert not now_read, f"{name}: UNREAD names {now_read}, which a reader now reads"
        unclassified = sorted(carried - reads[name] - set(declared))
        assert not unclassified, (
            f"{name}: {unclassified} reach no reader of this record and are not in UNREAD. Either "
            "a reader reads them — then declare it in READERS — or they are carried for a human, "
            "and then name them in UNREAD with the reason."
        )


def test_a_file_naming_a_record_is_a_declared_reader_or_a_declared_mention() -> None:
    """Otherwise the guard is self-limiting: it covers the readers it already knows about.

    The same argument as `test_the_citing_records_are_exactly_these`, one directory out. Discovery
    is by filename and so cannot find a reader that globs — `tests/test_schema.py` is one, and is
    declared rather than discovered — which is why this asserts containment and not equality.
    """
    declared = {reader.path for reader in READERS} | set(MENTIONS)
    found: set[str] = set()
    for directory in SEARCHED_DIRS:
        for path in directory.rglob("*.py"):
            source = path.read_text()
            if any(name in source for name in _committed()):
                found.add(path.relative_to(REPO_ROOT).as_posix())
    assert found, "no file names a committed analysis record — discovery has stopped working"
    unclassified = sorted(found - declared)
    assert not unclassified, (
        f"{unclassified} name an analysis record and are neither in READERS nor in MENTIONS. If "
        "one reads keys out of a record, declaring it changes what UNREAD must contain."
    )
