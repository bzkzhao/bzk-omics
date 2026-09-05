"""The Perseus analysis-output adapter (`ARCHITECTURE.md` §3, ADR-0017, `ONTOLOGY.md` §5.4).

Written before the adapter and failing first (`CLAUDE.md` § Working style).

Every fixture here is **synthetic**, and deliberately so — `HANDOFF.md` §8 records the hazard this
session found: a test whose fixture is live project data stops guarding when the data changes, and
the error-path half goes green rather than red. No Perseus output from the collaborating group
exists yet, so there is nothing real to test against in any case; when one arrives it becomes an
*additional* fixture, not a replacement for these.

The accessions are real (`CLAUDE.md`: real external identifiers only) and are ones this repository
already carries elsewhere — P20591, P19525, O43593, P05161.

What the adapter must get right, and why each is a test rather than a comment:

- **`parameters_observed = false` means the parameters are STATED, not observed** (I19, §5.4). A
  result table does not record which quantity it consumed or which test produced it, so the adapter
  takes them declared and refuses without them. That is the whole difference between this class of
  adapter and a search-output one.
- **`-Log` p-values.** Perseus writes `-Log Student's T-test p-value` by default. Reading that
  column as a p-value gives 4.51 where 3.09e-05 is meant — the "wrong column, no error" class in
  `HANDOFF.md` §6, and the reason both spellings are handled explicitly and tested apart.
- **CRLF.** `ARCHITECTURE.md` §3 records the PXD018299 deposit as CRLF throughout and what a manual
  split leaves on the last column. One fixture is CRLF for that reason.
- **Protein groups.** A row naming two accessions measured the *group*, and 72-77% of real rows do.
  The adapter refused every one until ADR-0022 made `candidate_proteins` identifying; it now names
  the whole group and picks none of it. Read from `Protein IDs` rather than `Majority protein IDs`
  where both exist, because the majority subset is MaxQuant's own inference (§6.3).
"""

from __future__ import annotations

from pathlib import Path
from typing import cast

import kuzu
import pytest

from bzk.adapters.base import ObservationAdapter, SampleMapping
from bzk.adapters.perseus import (
    DeclaredAnalysis,
    DeclaredContrast,
    PerseusAdapter,
    PerseusError,
)
from bzk.ontology import invariants
from bzk.ontology.invariants import NODE_TYPE_KEY

FIXTURES = Path(__file__).resolve().parent / "fixtures"
TABLE = FIXTURES / "perseus_synthetic_proteins.txt"
GROUPS = FIXTURES / "perseus_synthetic_groups.txt"
PLAIN_P = FIXTURES / "perseus_synthetic_plain_pvalue.txt"
NOT_PERSEUS = FIXTURES / "perseus_synthetic_not_perseus.txt"

CONTRAST = DeclaredContrast(
    column_suffix="KO_IFN_WT_IFN", numerator="USP18-/- + IFN", denominator="WT + IFN"
)

# What the user states about a run the platform did not witness (§5.4). `lfq` because a protein-
# grain Perseus table is conventionally built on LFQ intensities; it is declared, not detected.
DECLARED = DeclaredAnalysis(
    quantity="lfq",
    filters_applied=["reverse", "potential_contaminant", "only_identified_by_site"],
    test="welch_t",
    fdr_method="BH",
    external_version="1.6.15.0",
)


@pytest.fixture
def mapping() -> SampleMapping:
    """Two Samples as **change-set nodes, already narrowed**. Ids are the shape `keys.py` mints.

    **Corrected 2026-09-05: this read *"as the curation loader hands them over"*, and that was
    false.** `bzk/curation/loader.py`'s `sample_mapping` builds each descriptor as
    `{**by_id[sample_id], "mapping_key": key}`, so one the loader hands over carries `mapping_key`
    — not a DDL column — and these carry none. **What the fixture returns is unchanged; only the
    claim about it is.** The loader's shape is exercised by
    `test_a_loader_shaped_descriptor_does_not_put_mapping_key_in_the_change_set`, which no fixture
    of this shape could reach.
    """
    return SampleMapping(
        curation_analysis_id="bzk:bc90e3eb515d6edd1351ce25ecd33209",
        samples=[
            {NODE_TYPE_KEY: "Sample", "id": "bzk:9924d6d24941af0f1b64171e0b550e76", "replicate": 1},
            {NODE_TYPE_KEY: "Sample", "id": "bzk:7b2ed3b2751c3364da982151935c9845", "replicate": 2},
        ],
    )


@pytest.fixture
def adapter() -> PerseusAdapter:
    return PerseusAdapter(declared=DECLARED, contrasts=[CONTRAST])


def _nodes(parsed: object, label: str) -> list[dict[str, object]]:
    return [n for n in parsed.nodes if n[NODE_TYPE_KEY] == label]  # type: ignore[attr-defined]


# ── The spreadsheet shape ───────────────────────────────────────────────────────────────────────
#
# **The shape modelled below is reviewer-supplied and not re-derivable in this container.** The
# deposit's export is a one-sheet workbook with three header rows and no `#!{` annotation row
# anywhere: rows 1 and 2 carry a set label and a condition string for the quantitative columns, and
# row 3 carries a raw acquisition path for those columns and the Perseus type-stamped names for the
# statistics and identifier columns, whose protein spellings are `Protein.Group` and `Protein.Ids`.
# No such file is in the tree and none is fetched — every workbook here is built in `tmp_path` by
# `openpyxl` and thrown away, which is the synthetic twin `HANDOFF.md` §8 requires.


def _sheet(path: Path, sheet_rows: list[list[object]], merges: list[str] | None = None) -> Path:
    import openpyxl

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    for row in sheet_rows:
        sheet.append(row)
    for span in merges or []:
        sheet.merge_cells(span)
    workbook.save(path)
    return path


#: Row 3's stamped names, in column order. The two protein spellings are the deposit's.
_STAMPED = [
    "T: Protein.Group",
    "T: Protein.Ids",
    "N: Peptides",
    "N: Student's T-test Difference KO_IFN_WT_IFN",
    "N: -Log Student's T-test p-value KO_IFN_WT_IFN",
    "N: Student's T-test q-value KO_IFN_WT_IFN",
]


def _deposit_shaped(path: Path) -> Path:
    """Three header rows, a stamp on the third, and `Protein.Ids` repeating where `Protein.Group`
    does not — which is the pair's behaviour the reviewer measured on the deposit's own file."""
    return _sheet(
        path,
        [
            [None, None, None, None, None, None, "1", "2"],
            [None, None, None, None, None, None, "siC (-IFN-B)", "siUSP24 (+ IFN-B)"],
            [*_STAMPED, "/raw/2024_A.d", "/raw/2024_B.d"],
            ["P20591", "P20591;Q9NRZ9", 7, 3.42, 4.51, 0.0012, 100.0, 200.0],
            ["P19525", "P20591;Q9NRZ9", 12, 4.95, 5.02, 0.0009, 110.0, 210.0],
            ["O43593", "O43593", 4, -1.87, 2.30, 0.0210, 120.0, 220.0],
        ],
    )


# ── The contract ────────────────────────────────────────────────────────────────────────────────


def test_satisfies_the_observation_adapter_protocol(adapter: PerseusAdapter) -> None:
    """`ARCHITECTURE.md` §3: `(file, SampleMapping) -> ParsedObservations`, never a directory."""
    assert isinstance(adapter, ObservationAdapter)
    assert adapter.name == "perseus"


def test_sniffs_on_content_not_on_a_name(adapter: PerseusAdapter) -> None:
    """A Perseus matrix carries `#!{...}` annotation rows; a bare TSV does not.

    The contract requires sniffing content because "search engines differ in output layout more
    than in output content". A `.txt` suffix says nothing — the deposit's MaxQuant table is `.txt`
    too.
    """
    assert adapter.sniff(TABLE)
    assert adapter.sniff(PLAIN_P)
    assert not adapter.sniff(NOT_PERSEUS)


# ── The change-set ──────────────────────────────────────────────────────────────────────────────


def test_change_set_satisfies_the_invariant_layer(
    adapter: PerseusAdapter, mapping: SampleMapping
) -> None:
    """ADR-0019: self-contained, every referent present, multiplicity respected."""
    parsed = adapter.parse(TABLE, mapping)
    invariants.validate(parsed.nodes, parsed.edges)


def test_emits_one_observation_and_one_result_per_protein(
    adapter: PerseusAdapter, mapping: SampleMapping
) -> None:
    """Four data rows, one declared contrast: four proteins, four observations, four results."""
    parsed = adapter.parse(TABLE, mapping)
    assert len(_nodes(parsed, "Protein")) == 4
    assert len(_nodes(parsed, "ProteinObservation")) == 4
    assert len(_nodes(parsed, "DifferentialResult")) == 4
    assert len(_nodes(parsed, "Contrast")) == 1
    assert len(_nodes(parsed, "Analysis")) == 1
    assert len(_nodes(parsed, "Imputation")) == 1
    assert len(_nodes(parsed, "Dataset")) == 1


def test_protein_ids_are_uniprot_curies(adapter: PerseusAdapter, mapping: SampleMapping) -> None:
    """§4's reference key template, built by `keys.protein_key` rather than string-formatted here."""
    ids = {n["id"] for n in _nodes(adapter.parse(TABLE, mapping), "Protein")}
    assert ids == {"uniprot:P20591", "uniprot:P19525", "uniprot:O43593", "uniprot:P05161"}


def test_the_analysis_is_external_and_its_parameters_are_reported_not_observed(
    adapter: PerseusAdapter, mapping: SampleMapping
) -> None:
    """ADR-0017 and I19. `parameters_observed = false` propagates to every result generated here.

    This is the single most consequential field the adapter sets: it is what stops a Perseus number
    acquiring the same provenance standing as one the platform computed.
    """
    analysis = _nodes(adapter.parse(TABLE, mapping), "Analysis")[0]
    assert analysis["kind"] == "external"
    assert analysis["parameters_observed"] is False
    assert analysis["external_tool"] == "perseus"
    assert analysis["external_version"] == "1.6.15.0"
    assert analysis["quantity"] == "lfq"
    assert analysis["test"] == "welch_t"
    assert analysis["basis"] is None and analysis["confidence"] is None


def test_results_carry_the_numbers_from_the_row(
    adapter: PerseusAdapter, mapping: SampleMapping
) -> None:
    parsed = adapter.parse(TABLE, mapping)
    by_protein = {}
    obs = {n["id"]: n for n in _nodes(parsed, "ProteinObservation")}
    resolves = {e["from"]: e["to"] for e in parsed.edges if e["type"] == "RESOLVES_TO_PROTEIN"}
    for edge in (e for e in parsed.edges if e["type"] == "RESULT_FOR_PROTEIN"):
        by_protein[resolves[obs[edge["to"]]["id"]]] = edge["from"]
    results = {n["id"]: n for n in _nodes(parsed, "DifferentialResult")}
    mx1 = results[by_protein["uniprot:P20591"]]
    assert mx1["log2fc"] == pytest.approx(3.42)
    assert mx1["adj_p_value"] == pytest.approx(0.0012)
    assert mx1["protein_adjusted"] == "not_applied"


def test_minus_log_p_values_are_converted(adapter: PerseusAdapter, mapping: SampleMapping) -> None:
    """Perseus writes `-Log Student's T-test p-value` by default; 4.51 means 3.09e-05.

    Reading that column as a p-value is the "wrong column, no error" failure of `HANDOFF.md` §6 in
    its purest form — every row would look wildly non-significant and nothing would raise.
    """
    parsed = adapter.parse(TABLE, mapping)
    p_values = sorted(
        float(cast("float", n["p_value"])) for n in _nodes(parsed, "DifferentialResult")
    )
    assert p_values[0] == pytest.approx(10**-5.02)
    assert all(0.0 < p <= 1.0 for p in p_values)


def test_a_plain_p_value_column_is_read_as_is_and_crlf_survives(
    adapter: PerseusAdapter, mapping: SampleMapping
) -> None:
    """The other spelling, in a CRLF file — both hazards in one fixture.

    `ARCHITECTURE.md` §3 measured the PXD018299 deposit as CRLF throughout and recorded what a
    manual split leaves behind: a trailing `\\r` on the last field of every row, so a lookup on the
    last column silently returns nothing.
    """
    assert PLAIN_P.read_bytes().count(b"\r\n") > 0, "fixture is meant to be CRLF"
    parsed = adapter.parse(PLAIN_P, mapping)
    result = _nodes(parsed, "DifferentialResult")[0]
    assert result["p_value"] == pytest.approx(3.0902e-05)
    assert result["adj_p_value"] == pytest.approx(0.0012)  # the LAST column: no stray \r


def test_samples_are_restaged_and_linked_to_the_dataset(
    adapter: PerseusAdapter, mapping: SampleMapping
) -> None:
    """ADR-0019 requires referents in the batch; the Samples come from the curation `Analysis`."""
    parsed = adapter.parse(TABLE, mapping)
    assert len(_nodes(parsed, "Sample")) == 2
    produced = {e["from"] for e in parsed.edges if e["type"] == "PRODUCED"}
    assert produced == {s["id"] for s in mapping.samples}


def test_a_loader_shaped_descriptor_does_not_put_mapping_key_in_the_change_set(
    adapter: PerseusAdapter,
) -> None:
    """`base.py`'s narrowing is owed by every adapter emitting `Sample` nodes from a mapping.

    **The `mapping` fixture above cannot reach this and no test using it could.** It hands over
    change-set nodes that are already narrowed, so the divergence between this adapter and the two
    MaxQuant ones is invisible to it. The descriptor here is built the way
    `bzk/curation/loader.py`'s `sample_mapping` builds one — the `Sample` node's own keys plus
    `mapping_key`, the column header the curation was written against.

    **Synthetic rather than loaded from `data/curation/`**: a path tested against real data being
    in a particular state stops guarding the day that data changes, and does it by going green
    (`HANDOFF.md` §8).

    **Asserted on the key that must not appear, never on a column count.** A count would pass for
    the wrong reason the day `Sample` gains a column.
    """
    loader_shaped = SampleMapping(
        curation_analysis_id="bzk:bc90e3eb515d6edd1351ce25ecd33209",
        samples=[
            {
                NODE_TYPE_KEY: "Sample",
                "id": "bzk:9924d6d24941af0f1b64171e0b550e76",
                "replicate": 1,
                "mapping_key": "Ratio mod/base KO_IFN_1",
            },
            {
                NODE_TYPE_KEY: "Sample",
                "id": "bzk:7b2ed3b2751c3364da982151935c9845",
                "replicate": 2,
                "mapping_key": "Ratio mod/base KO_IFN_2",
            },
        ],
    )
    samples = _nodes(adapter.parse(TABLE, loader_shaped), "Sample")
    assert samples, "no Sample node reached the change-set, so the check below asserts nothing"
    for node in samples:
        assert "mapping_key" not in node


def test_the_dataset_is_keyed_on_the_files_own_digest(
    adapter: PerseusAdapter, mapping: SampleMapping
) -> None:
    """A Perseus result table is its own artefact with its own hash — not the deposit's.

    `Dataset` keys on `content_hash` (§3), so re-ingesting the same file converges on one node and
    an edited export is a different `Dataset` rather than a silent overwrite.
    """
    from bzk.provenance.raw_store import content_hash

    dataset = _nodes(adapter.parse(TABLE, mapping), "Dataset")[0]
    assert dataset["content_hash"] == content_hash(TABLE.read_bytes())


def test_parse_is_deterministic(adapter: PerseusAdapter, mapping: SampleMapping) -> None:
    """I9: the same file and mapping yield the same ids, run to run."""
    first, second = adapter.parse(TABLE, mapping), adapter.parse(TABLE, mapping)
    assert [n["id"] for n in first.nodes] == [n["id"] for n in second.nodes]


# ── Refusals ────────────────────────────────────────────────────────────────────────────────────


def test_a_protein_group_is_ingested_as_a_group(mapping: SampleMapping) -> None:
    """The ADR-0022 payoff: the row that used to be refused now becomes one observation of two.

    `candidate_proteins` is identifying and `RESOLVES_TO_PROTEIN` is `MANY_MANY`, so the observation
    names both members and asserts a pick among neither. Two `Protein` nodes, one observation, two
    resolves edges — and crucially one `DifferentialResult`, because the row is one measurement of
    a group, not two measurements.
    """
    adapter = PerseusAdapter(declared=DECLARED, contrasts=[CONTRAST])
    parsed = adapter.parse(GROUPS, mapping)
    invariants.validate(parsed.nodes, parsed.edges)
    assert len(_nodes(parsed, "Protein")) == 3  # P20591 alone, plus P19525 and O43593 as a group
    assert len(_nodes(parsed, "ProteinObservation")) == 2
    assert len(_nodes(parsed, "DifferentialResult")) == 2
    grouped = next(
        n
        for n in _nodes(parsed, "ProteinObservation")
        if len(cast("list[str]", n["candidate_proteins"])) > 1
    )
    members = cast("list[str]", grouped["candidate_proteins"])
    assert set(members) == {"uniprot:P19525", "uniprot:O43593"}
    resolves = [
        e for e in parsed.edges if e["type"] == "RESOLVES_TO_PROTEIN" and e["from"] == grouped["id"]
    ]
    assert len(resolves) == 2


def test_no_protein_assignment_is_invented_for_the_group(mapping: SampleMapping) -> None:
    """A group is not a pick, so nothing here records one.

    MaxQuant's narrowing to `Majority protein IDs` IS an inference worth recording, but §6.3's shape
    is a candidate set plus a concluded protein, and a narrowing to a smaller *subset* is neither.
    Deciding that is a modelling question, not an adapter's — `HANDOFF.md` §8.
    """
    parsed = PerseusAdapter(declared=DECLARED, contrasts=[CONTRAST]).parse(GROUPS, mapping)
    assert _nodes(parsed, "ProteinAssignment") == []
    assert not [e for e in parsed.edges if e["type"] == "ASSIGNS_PROTEIN"]


def test_the_widest_accession_column_wins(mapping: SampleMapping) -> None:
    """`Protein IDs` over `Majority protein IDs`: the observation records what was observed.

    The majority subset is MaxQuant's razor-rule inference (§6.3) and the two differ on 52-72% of
    real rows, so reading the narrower column would quietly record an inference as a measurement.
    """
    from bzk.adapters.perseus import PROTEIN_COLUMNS

    assert PROTEIN_COLUMNS.index("Protein IDs") < PROTEIN_COLUMNS.index("Majority protein IDs")


def test_refuses_an_undeclared_quantity(mapping: SampleMapping) -> None:
    """`quantity` is identifying on `Analysis` and drawn from a closed enum (I16, §5).

    A result table cannot state it, so it is declared — and a misspelling forks an id rather than
    failing, which is why it is checked against the enum and not merely required.
    """
    with pytest.raises(PerseusError) as exc:
        PerseusAdapter(
            declared=DeclaredAnalysis(
                quantity="LFQ",  # right family, wrong spelling
                filters_applied=[],
                test="welch_t",
                fdr_method="BH",
                external_version="1.6.15.0",
            ),
            contrasts=[CONTRAST],
        )
    assert "LFQ" in str(exc.value)


def test_refuses_when_a_declared_contrast_has_no_columns(mapping: SampleMapping) -> None:
    """A contrast the caller states but the file does not contain is a mismatch, not an empty
    result — silently emitting nothing would read as "Perseus found nothing significant"."""
    adapter = PerseusAdapter(
        declared=DECLARED,
        contrasts=[DeclaredContrast(column_suffix="KO_WT", numerator="KO", denominator="WT")],
    )
    with pytest.raises(PerseusError) as exc:
        adapter.parse(TABLE, mapping)
    assert "KO_WT" in str(exc.value)


def test_refuses_a_file_it_cannot_sniff(adapter: PerseusAdapter, mapping: SampleMapping) -> None:
    """`parse` does not assume `sniff` was called; a bare TSV is refused rather than half-read."""
    with pytest.raises(PerseusError):
        adapter.parse(NOT_PERSEUS, mapping)


def test_refuses_an_empty_sample_mapping(adapter: PerseusAdapter) -> None:
    """Without Samples the results reach no curation activity, so I5 would flag every one of them
    `unprovenanced` — a state to refuse at ingest, not to write and label afterwards."""
    with pytest.raises(PerseusError):
        adapter.parse(TABLE, SampleMapping(curation_analysis_id="bzk:x", samples=[]))


# ── The write path ──────────────────────────────────────────────────────────────────────────────


def test_the_change_set_stores(
    adapter: PerseusAdapter, mapping: SampleMapping, tmp_path: Path
) -> None:
    """The adapter's output through `store.write_change_set`, into the real DDL.

    `invariants.validate` is plain data and never touches Kùzu, so a type or column mistake passes
    it — and the loader's own column check was removed on 2026-08-07 precisely because the store
    now guards that for every producer. That left this adapter's output guarded by nothing, since
    no test stored it. This is that gap closed: the same end-to-end path the curation loader gets
    from `tests/test_rebuild.py`.
    """
    from bzk.ontology import schema, store

    parsed = adapter.parse(TABLE, mapping)
    conn = kuzu.Connection(kuzu.Database(str(tmp_path / "g.kuzu")))
    schema.create_schema(conn)
    report = store.write_change_set(conn, parsed.nodes, parsed.edges)

    # Was `report.nodes_written == len(parsed.nodes)`, which `store.WriteReport` computes by that
    # exact expression — a tautology that could not fail under any change to the code it appeared
    # to test. Replaced 2026-08-08, and what the replacement does and does not establish is worth
    # stating, because overclaiming it would be the same defect one turn on.
    #
    # The `sum(...)` terms were deleted on 2026-08-08 and the reason is worth keeping. They replaced
    # a tautology (`report.nodes_written == len(parsed.nodes)`), and were offered as catching a
    # silent write failure that the per-label dicts below do not. They do not: `sum(...) == 18` is
    # entailed by a dict of literals summing to 18, so no state fails the sum while the dict passes,
    # and the silent-skip mutation that "confirmed" the reach fails the dict too — which additionally
    # names the missing label. What survived deletion is the one conjunct the dicts do not entail:
    # the *staged* count against a literal. Its reach is this adapter's change-set size and nothing
    # more; the divergence the rename is about needs two change-sets and lives in test_store.py.
    assert report.nodes_staged == 18
    assert report.edges_staged == 24
    assert store.count_nodes(conn) == {
        "Protein": 4,
        "ProteinObservation": 4,
        "DifferentialResult": 4,
        "Contrast": 1,
        "Analysis": 1,
        "Imputation": 1,
        "Dataset": 1,
        "Sample": 2,
    }
    assert store.count_edges(conn) == {
        "PRODUCED": 2,
        "USED": 1,
        "IMPUTATION_FOR": 1,
        "REPORTS_PROTEIN": 4,
        "RESOLVES_TO_PROTEIN": 4,
        "WAS_GENERATED_BY": 4,
        "RESULT_FOR_PROTEIN": 4,
        "RESULT_IN_CONTRAST": 4,
    }


def test_re_ingesting_the_same_export_converges(
    adapter: PerseusAdapter, mapping: SampleMapping, tmp_path: Path
) -> None:
    """Idempotent replay (I9, ADR-0020): the same file twice is one graph, not two.

    The `Dataset` keys on the file's digest and every downstream id anchors on it, so nothing here
    depends on the store being empty — which is what makes a re-run of an ingestion safe.
    """
    from bzk.ontology import schema, store

    parsed = adapter.parse(TABLE, mapping)
    conn = kuzu.Connection(kuzu.Database(str(tmp_path / "g.kuzu")))
    schema.create_schema(conn)
    store.write_change_set(conn, parsed.nodes, parsed.edges)
    before = store.ids_by_label(conn)
    store.write_change_set(conn, adapter.parse(TABLE, mapping).nodes, parsed.edges)
    assert store.ids_by_label(conn) == before


# ── The spreadsheet path ────────────────────────────────────────────────────────────────────────


def test_a_spreadsheet_sniffs_on_the_type_stamp(adapter: PerseusAdapter, tmp_path: Path) -> None:
    """The marker for a workbook is the Perseus column-type stamp, not the `#!{` annotation row.

    `ROADMAP.md` § *Classification uses the established method and not a new one* states the rule
    and forbids the alternative in the same sentence: *"Perseus versus raw search-engine output is
    decided by the type-prefix stamp (`C:`/`N:`/`T:`/`M:`), **never** by the presence of a
    statistics column"* — the alternative having produced a recorded false positive on a `Q-value`
    column that raw MaxQuant also carries.

    Before this, a workbook could not reach the annotation test at all: `sniff` read the file with
    `errors="strict"` and a `.xlsx` is a ZIP container, so it returned `False` at the decode gate.
    """
    assert adapter.sniff(_deposit_shaped(tmp_path / "deposit.xlsx"))


def test_a_spreadsheet_with_no_type_stamp_does_not_sniff(
    adapter: PerseusAdapter, tmp_path: Path
) -> None:
    """A workbook of raw search-engine output carries no stamp, and the stamp is the whole test.

    Same columns, same data, stamps removed — so what separates the two files is the marker and not
    their content, which is what keeps this adapter off search-engine output.
    """
    book = _sheet(
        tmp_path / "unstamped.xlsx",
        [
            [name.split(": ", 1)[1] for name in _STAMPED],
            ["P20591", "P20591;Q9NRZ9", 7, 3.42, 4.51, 0.0012],
        ],
    )
    assert not adapter.sniff(book)


def test_the_tab_separated_annotation_row_path_still_sniffs(adapter: PerseusAdapter) -> None:
    """The spreadsheet path is additive: `#!{` keeps deciding a tab-separated export."""
    assert adapter.sniff(TABLE)
    assert not adapter.sniff(NOT_PERSEUS)


def test_the_composed_header_names_every_column(tmp_path: Path) -> None:
    """A column identified across three rows gets one name, and a stamped cell is that name.

    The rule: the **named row** is the first of the leading rows carrying a type-stamped cell. A
    column whose cell in that row is stamped takes it, stripped. Any other column takes every
    non-empty header cell above it, joined — so the quantitative columns, whose row-3 cell is an
    acquisition path rather than a stamped name, keep the set label and the condition string that
    identify them.
    """
    adapter = PerseusAdapter(declared=DECLARED, contrasts=[CONTRAST])
    header, _ = adapter._read(
        _deposit_shaped(tmp_path / "d.xlsx").read_bytes(), tmp_path / "d.xlsx"
    )
    assert header[0] == "Protein.Group"
    assert header[3] == "Student's T-test Difference KO_IFN_WT_IFN"
    assert header[6] == "1 | siC (-IFN-B) | /raw/2024_A.d"
    assert "" not in header


def test_the_identity_column_is_the_one_distinct_on_every_row(
    mapping: SampleMapping, tmp_path: Path
) -> None:
    """`candidate_proteins` is identifying (ADR-0022) and `REPORTS_PROTEIN` is `ONE_MANY`, so a set
    repeating across rows collides into one observation taking two edges.

    `Protein.Ids` repeats here and `Protein.Group` does not, so the accession sets that reach the
    graph are the ones `Protein.Group` names — asserted on the sets themselves, not on a count of
    them.
    """
    adapter = PerseusAdapter(declared=DECLARED, contrasts=[CONTRAST])
    parsed = adapter.parse(_deposit_shaped(tmp_path / "d.xlsx"), mapping)
    observed = [n["candidate_proteins"] for n in _nodes(parsed, "ProteinObservation")]
    assert ["uniprot:P20591"] in observed
    assert ["uniprot:P19525"] in observed
    assert ["uniprot:O43593"] in observed
    # The set `Protein.Ids` carries on two of the three rows never becomes an identity, which is
    # the half that would have gone unnoticed: it collides rather than raising.
    assert ["uniprot:P20591", "uniprot:Q9NRZ9"] not in observed


def test_a_file_whose_only_protein_column_repeats_is_refused_by_name(
    mapping: SampleMapping, tmp_path: Path
) -> None:
    """Refuse rather than guess, and name what was found (`HANDOFF.md` §8).

    Falling through to no column, or silently letting two rows converge, would produce a graph
    quietly missing a protein — the `ran cleanly and was wrong` class this adapter refuses.
    """
    book = _sheet(
        tmp_path / "repeats.xlsx",
        [
            [_STAMPED[1], *_STAMPED[2:]],
            ["P20591;Q9NRZ9", 7, 3.42, 4.51, 0.0012],
            ["P20591;Q9NRZ9", 12, 4.95, 5.02, 0.0009],
        ],
    )
    adapter = PerseusAdapter(declared=DECLARED, contrasts=[CONTRAST])
    with pytest.raises(PerseusError) as exc:
        adapter.parse(book, mapping)
    assert "Protein.Ids" in str(exc.value)
    assert "1 distinct over 2 rows" in str(exc.value)


def test_a_column_the_header_rows_do_not_name_is_refused_by_position(
    mapping: SampleMapping, tmp_path: Path
) -> None:
    """A column that composes to nothing is an error naming what it found, never a blank name.

    A blank would become a dictionary key, collide with the next blank, and silently shift which
    column a later lookup reads.
    """
    book = _sheet(
        tmp_path / "orphan.xlsx",
        [
            [None, None, None, None, None, None],
            [*_STAMPED[:5], None],
            ["P20591", "P20591", 7, 3.42, 4.51, "orphan"],
        ],
    )
    adapter = PerseusAdapter(declared=DECLARED, contrasts=[CONTRAST])
    with pytest.raises(PerseusError) as exc:
        adapter.parse(book, mapping)
    assert "column 6" in str(exc.value)


# ── Merged header cells ─────────────────────────────────────────────────────────────────────────
#
# **Reviewer-supplied and not re-derivable in this container.** The deposit's `S1_TP`, at
# `a6e12e555709612590d1a1d2f499bcd416d2ee69d6e28cb2e167a162fe5c95c2`, carries three merged ranges in
# its first header row — `A1:D1`, `E1:H1`, `I1:L1`, holding `Set 1`, `Set 2`, `Set 3` — so that row
# reads as nine non-empty cells of 29 and nine of the eighteen quantitative columns compose without
# the set they are displayed under. The fixtures below carry that shape; the file does not enter the
# tree and none of its own figures is re-measured here.


def _merged_shaped(path: Path) -> Path:
    """One merged qualifier spanning four columns, above a condition row and a stamped row."""
    return _sheet(
        path,
        [
            ["Set 1", None, None, None, None, None],
            ["siC (-IFN-B)", "siUSP24 (-IFN-B)", "siC (+IFN-B)", "siUSP24 (+ IFN-B)", None, None],
            [
                "/raw/A.d",
                "/raw/B.d",
                "/raw/C.d",
                "/raw/D.d",
                "T: Protein.Group",
                "N: Student's T-test Difference X",
            ],
            ["100.0", "110.0", "120.0", "130.0", "P20591", "3.42"],
        ],
        merges=["A1:D1"],
    )


def test_a_merged_qualifier_reaches_every_column_it_covers(tmp_path: Path) -> None:
    """A merged span is header information the file states, so every column it covers carries it.

    Read as a streaming reader reads it, a merged range yields its value in the top-left cell and
    nothing in the rest, so three of these four columns would compose without the set they are
    displayed under — unique, because the acquisition path differs, and wrong.
    """
    adapter = PerseusAdapter(declared=DECLARED, contrasts=[CONTRAST])
    book = _merged_shaped(tmp_path / "merged.xlsx")
    header, _ = adapter._read(book.read_bytes(), book)
    assert header[0] == "Set 1 | siC (-IFN-B) | /raw/A.d"
    assert header[1] == "Set 1 | siUSP24 (-IFN-B) | /raw/B.d"
    assert header[2] == "Set 1 | siC (+IFN-B) | /raw/C.d"
    assert header[3] == "Set 1 | siUSP24 (+ IFN-B) | /raw/D.d"
    assert header[4] == "Protein.Group"


def test_an_unmerged_blank_does_not_inherit_its_neighbour(tmp_path: Path) -> None:
    """A blank cell is not evidence of a span, and forward-filling would treat it as one.

    Same visual shape as the merged fixture and no merge recorded, so a reader that carried the last
    non-empty value rightwards would produce the merged answer here too — by accident, and wrong the
    day a header row has a genuinely empty column.
    """
    adapter = PerseusAdapter(declared=DECLARED, contrasts=[CONTRAST])
    book = _sheet(
        tmp_path / "unmerged.xlsx",
        [
            ["Set 1", None, None],
            ["siC (-IFN-B)", "siUSP24 (-IFN-B)", None],
            ["/raw/A.d", "/raw/B.d", "T: Protein.Group"],
            ["100.0", "110.0", "P20591"],
        ],
    )
    header, _ = adapter._read(book.read_bytes(), book)
    assert header[0] == "Set 1 | siC (-IFN-B) | /raw/A.d"
    assert header[1] == "siUSP24 (-IFN-B) | /raw/B.d"


def test_a_span_that_makes_two_names_identical_is_still_refused(tmp_path: Path) -> None:
    """Recovering a span must not turn a refusal into a silent pass.

    Both columns here are named by the span and by nothing else, so they compose to one name. Before
    the span was read the second column was named by nothing and refused for that; after it, the two
    collide and refuse for that. Either way the file does not load, and the message says which.
    """
    adapter = PerseusAdapter(declared=DECLARED, contrasts=[CONTRAST])
    book = _sheet(
        tmp_path / "collide.xlsx",
        [
            ["Set 1", None, None],
            [None, None, None],
            [None, None, "T: Protein.Group"],
            ["100.0", "110.0", "P20591"],
        ],
        merges=["A1:B1"],
    )
    with pytest.raises(PerseusError) as exc:
        adapter._read(book.read_bytes(), book)
    assert "compose to one name" in str(exc.value)
    assert "Set 1" in str(exc.value)


def test_a_column_no_span_reaches_is_still_refused(tmp_path: Path) -> None:
    """The other refusal, unchanged: a span covering some columns does not name the rest."""
    adapter = PerseusAdapter(declared=DECLARED, contrasts=[CONTRAST])
    book = _sheet(
        tmp_path / "orphan_span.xlsx",
        [
            ["Set 1", None, None, None],
            [None, None, None, None],
            [None, None, "T: Protein.Group", None],
            ["100.0", "110.0", "P20591", "x"],
        ],
        merges=["A1:B1"],
    )
    with pytest.raises(PerseusError) as exc:
        adapter._read(book.read_bytes(), book)
    assert "column 4" in str(exc.value)
    assert "named by no header row" in str(exc.value)


def test_the_unmerged_fixture_composes_exactly_as_before(tmp_path: Path) -> None:
    """Reading spans changes nothing about a sheet that records none — every name, verbatim.

    Asserted column by column rather than as one list comparison: a whole-list equality names only
    that the list moved, where these name which column did, and the width is asserted beside them so
    the enumeration cannot be short by one.
    """
    adapter = PerseusAdapter(declared=DECLARED, contrasts=[CONTRAST])
    book = _deposit_shaped(tmp_path / "d.xlsx")
    header, _ = adapter._read(book.read_bytes(), book)
    assert len(header) == 8
    assert header[0] == "Protein.Group"
    assert header[1] == "Protein.Ids"
    assert header[2] == "Peptides"
    assert header[3] == "Student's T-test Difference KO_IFN_WT_IFN"
    assert header[4] == "-Log Student's T-test p-value KO_IFN_WT_IFN"
    assert header[5] == "Student's T-test q-value KO_IFN_WT_IFN"
    assert header[6] == "1 | siC (-IFN-B) | /raw/2024_A.d"
    assert header[7] == "2 | siUSP24 (+ IFN-B) | /raw/2024_B.d"
