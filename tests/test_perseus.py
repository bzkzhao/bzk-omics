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
    """Two Samples, as the curation loader hands them over. Ids are the shape `keys.py` mints."""
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

    assert report.nodes_written == len(parsed.nodes)
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
