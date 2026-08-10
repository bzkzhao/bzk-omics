"""`bzk/adapters/maxquant_protein_groups.py` — the protein-grain search-output adapter.

Entirely offline and entirely synthetic, for `test_maxquant_sites.py`'s reason: a path tested
against whichever accession happens to be stale in UniProt today stops testing the day UniProt
changes, and stops *green*. No resolver is injected because this grain resolves nothing — a
protein-level quantification measures a gene product, not a sequence version (§3), so every
candidate is an accession-only `Protein`.

**The write path guards almost nothing here, so these tests are the guard.** One invariant fires at
protein grain — I14's second half, and only on a strict non-empty subset of the named group — and
it is exercised below by mutating the adapter's own output rather than by trusting `parse` to have
called `invariants.validate`. Everything else this module claims (which accession column is read,
that a reported zero survives, that two rows cannot fold into one observation) is unenforced by the
schema and asserted here or nowhere.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bzk.adapters.base import SampleMapping
from bzk.adapters.maxquant_protein_groups import (
    DeclaredProteinAnalysis,
    MaxQuantProteinGroupsAdapter,
    MaxQuantProteinGroupsError,
)
from bzk.ontology import invariants
from bzk.ontology.invariants import NODE_TYPE_KEY

# Real accessions (`CLAUDE.md` § Working style); nothing here depends on what UniProt says of them.
MX1 = "P20591"
IFIT1 = "P09914"
ISG15 = "P05161"

HEADER = [
    "Protein IDs",
    "Majority protein IDs",
    "Peptides",
    "Razor + unique peptides",
    "Reverse",
    "Potential contaminant",
    "id",
    "LFQ intensity WT_P_1",
    "LFQ intensity KO_P_1",
    "Intensity WT_P_1",
    "Intensity KO_P_1",
]


def _write(tmp_path: Path, rows: list[list[str]], header: list[str] | None = None) -> Path:
    """A synthetic protein-groups table. CRLF deliberately: the deposit is CRLF throughout."""
    lines = ["\t".join(header if header is not None else HEADER)]
    lines += ["\t".join(row) for row in rows]
    path = tmp_path / "proteinGroups.txt"
    path.write_bytes(("\r\n".join(lines) + "\r\n").encode("utf-8"))
    return path


def _row(
    *,
    proteins: str = MX1,
    majority: str | None = None,
    peptides: str = "7",
    razor: str = "5",
    reverse: str = "",
    contaminant: str = "",
    row_id: str = "0",
    lfq_wt: str = "1500000",
    lfq_ko: str = "2500000",
    intensity_wt: str = "1600000",
    intensity_ko: str = "2600000",
) -> list[str]:
    return [
        proteins,
        proteins if majority is None else majority,
        peptides,
        razor,
        reverse,
        contaminant,
        row_id,
        lfq_wt,
        lfq_ko,
        intensity_wt,
        intensity_ko,
    ]


def _sample(sample_id: str, label: str, key: str, genotype: str) -> dict[str, object]:
    return {
        NODE_TYPE_KEY: "Sample",
        "id": sample_id,
        "label": label,
        "source_type": "cell_line",
        "cell_line": "HAP1",
        "organism_taxid": "NCBITaxon:9606",
        "model_system": None,
        "genotype": genotype,
        "treatment": "none",
        "timepoint_h": None,
        "replicate": 1,
        "replicate_type": "biological",
        # Not a DDL column — the curation loader adds it, and it must not reach the graph.
        "mapping_key": key,
    }


def _mapping(quantity: str = "lfq") -> SampleMapping:
    prefix = {"lfq": "LFQ intensity ", "intensity": "Intensity "}[quantity]
    return SampleMapping(
        curation_analysis_id="bzk:curation1",
        samples=[
            _sample("bzk:sampleWT", "WT_P_1", f"{prefix}WT_P_1", "WT"),
            _sample("bzk:sampleKO", "KO_P_1", f"{prefix}KO_P_1", "USP18_KO"),
        ],
    )


def _adapter(quantity: str = "lfq") -> MaxQuantProteinGroupsAdapter:
    return MaxQuantProteinGroupsAdapter(
        DeclaredProteinAnalysis(
            search_engine="maxquant", external_version="1.6.10.43", quantity=quantity
        )
    )


# ── The happy path, and that it is a valid change-set ───────────────────────────────────────────


def test_one_row_becomes_a_protein_observation(tmp_path: Path) -> None:
    parsed = _adapter().parse(_write(tmp_path, [_row()]), _mapping())
    labels = {n[NODE_TYPE_KEY] for n in parsed.nodes}
    assert {"Dataset", "Analysis", "Sample", "Protein", "ProteinObservation"} <= labels
    observation = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "ProteinObservation")
    assert observation["candidate_proteins"] == [f"uniprot:{MX1}"]
    assert observation["n_peptides"] == 7
    assert parsed.refusals == []


def test_the_output_is_a_valid_change_set(tmp_path: Path) -> None:
    """`parse` validates before returning, so this is a second, independent assertion of it."""
    parsed = _adapter().parse(_write(tmp_path, [_row()]), _mapping())
    invariants.validate(parsed.nodes, parsed.edges)


def test_no_modification_site_or_sequence_is_minted(tmp_path: Path) -> None:
    """The claim that separates this adapter from `maxquant_sites.py`. A protein-level quantity has
    no position, so nothing here needs a `ProteinSequence` — and minting one would assert a
    sequence version the file never named."""
    parsed = _adapter().parse(_write(tmp_path, [_row()]), _mapping())
    labels = {n[NODE_TYPE_KEY] for n in parsed.nodes}
    assert not labels & {"ModificationSite", "ProteinSequence", "SiteObservation"}
    assert not [n for n in parsed.nodes if n[NODE_TYPE_KEY] == "ModifierAssignment"]


def test_the_edges_run_the_declared_way(tmp_path: Path) -> None:
    """`REPORTS_PROTEIN` is `Dataset -> ProteinObservation` (§7) and `RESOLVES_TO_PROTEIN` is
    `ProteinObservation -> Protein`. Direction is the thing most easily got wrong and the DDL is
    the only place it is stated."""
    parsed = _adapter().parse(_write(tmp_path, [_row()]), _mapping())
    dataset = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "Dataset")
    observation = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "ProteinObservation")
    reports = next(e for e in parsed.edges if e["type"] == "REPORTS_PROTEIN")
    assert (reports["from"], reports["to"]) == (dataset["id"], observation["id"])
    resolves = next(e for e in parsed.edges if e["type"] == "RESOLVES_TO_PROTEIN")
    assert (resolves["from"], resolves["to"]) == (observation["id"], f"uniprot:{MX1}")


def test_the_sample_descriptor_is_narrowed_to_its_columns(tmp_path: Path) -> None:
    """`mapping_key` is the curation record's column header, not a `Sample` column; passing it
    through would put a phantom field into the graph."""
    parsed = _adapter().parse(_write(tmp_path, [_row()]), _mapping())
    sample = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "Sample")
    assert "mapping_key" not in sample


# ── ADR-0022: the observed group, and the column it is read from ────────────────────────────────


def test_the_whole_group_is_the_identity_and_every_member_is_reached(tmp_path: Path) -> None:
    """ADR-0022 and I14's second half together: the group is `candidate_proteins`, and an
    observation that names a group resolves to **every** member or it is rendering against a razor
    pick through an edge."""
    row = _row(proteins=f"{MX1};{IFIT1};{ISG15}")
    parsed = _adapter().parse(_write(tmp_path, [row]), _mapping())
    observation = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "ProteinObservation")
    assert observation["candidate_proteins"] == [
        f"uniprot:{MX1}",
        f"uniprot:{IFIT1}",
        f"uniprot:{ISG15}",
    ]
    reached = {e["to"] for e in parsed.edges if e["type"] == "RESOLVES_TO_PROTEIN"}
    assert reached == set(observation["candidate_proteins"])
    assert {n["id"] for n in parsed.nodes if n[NODE_TYPE_KEY] == "Protein"} == reached


def test_resolving_to_a_subset_of_the_group_is_refused_by_i14(tmp_path: Path) -> None:
    """**The one invariant that fires at this grain, made to fire.** The pre-registration recorded
    *no invariant fires at protein grain*, measured by removing `RESOLVES_TO_PROTEIN` entirely —
    which is the shape I14 permits, since a node re-staged as a referent carries no edges
    (ADR-0019). Dropping *one* edge is the shape it refuses, and the probe never tried it.
    """
    row = _row(proteins=f"{MX1};{IFIT1};{ISG15}")
    parsed = _adapter().parse(_write(tmp_path, [row]), _mapping())

    # None of them: legal, and this is what the pre-registration measured.
    invariants.validate(
        parsed.nodes, [e for e in parsed.edges if e["type"] != "RESOLVES_TO_PROTEIN"]
    )

    # One of the three removed: the observation now names three and reaches two.
    dropped = next(e for e in parsed.edges if e["type"] == "RESOLVES_TO_PROTEIN")
    with pytest.raises(invariants.InvariantError, match="I14"):
        invariants.validate(parsed.nodes, [e for e in parsed.edges if e is not dropped])


def test_the_observed_group_is_read_not_maxquant_s_narrowing(tmp_path: Path) -> None:
    """`Protein IDs`, never `Majority protein IDs`. §3 calls `candidate_proteins` the group *as the
    search reported it*; the majority column is MaxQuant's narrowing to the subset carrying half
    the peptides, which §6.3 classifies as its own razor-rule inference. The two differ on 52–72%
    of real rows, so reading the wrong one is not a rounding error."""
    row = _row(proteins=f"{MX1};{IFIT1};{ISG15}", majority=MX1)
    parsed = _adapter().parse(_write(tmp_path, [row]), _mapping())
    observation = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "ProteinObservation")
    assert len(observation["candidate_proteins"]) == 3, "the narrowing was not substituted"


def test_the_group_is_stored_in_the_order_the_search_reported(tmp_path: Path) -> None:
    """§3: `candidate_proteins` is the group *as the search reported it*, and MaxQuant's ordering
    within the group is its ranking. Preserved rather than sorted — sorting would discard which
    member MaxQuant led with, which is the same class of loss as reading `Majority protein IDs`."""
    parsed = _adapter().parse(_write(tmp_path, [_row(proteins=f"{ISG15};{MX1}")]), _mapping())
    observation = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "ProteinObservation")
    assert observation["candidate_proteins"] == [f"uniprot:{ISG15}", f"uniprot:{MX1}"]


def test_two_rows_naming_one_group_are_refused_however_it_is_ordered(tmp_path: Path) -> None:
    """Two claims in one, and the second is why the rows are written reversed.

    Protein groups are disjoint by construction — 4,797 rows, 4,797 distinct sorted groups on
    PXD018299 — so two identical ones contradict the identity ADR-0022 fixed, and folding them
    would overwrite one row's cells with the other's under `INSERT OR REPLACE`, invisibly. That
    these two *are* one group is `keys.canonical_value`'s doing: it sorts a `STRING[]` before
    hashing, so the stored order (above) is not the keyed order and MaxQuant's ranking cannot fork
    an id.

    A first draft asserted the second half by parsing two one-row files and comparing observation
    ids. It failed, and not because sorting was absent: the two files differ in bytes, so they are
    two `Dataset`s by `content_hash`, and the anchor moved the id underneath the claim. Holding the
    dataset fixed is what makes the group the only thing varying.
    """
    rows = [
        _row(row_id="0", proteins=f"{MX1};{IFIT1}"),
        _row(row_id="1", proteins=f"{IFIT1};{MX1}"),
    ]
    with pytest.raises(MaxQuantProteinGroupsError, match="same protein group"):
        _adapter().parse(_write(tmp_path, rows), _mapping())


def test_one_protein_named_by_two_groups_is_staged_once(tmp_path: Path) -> None:
    """ADR-0019 refuses a duplicate id in a batch, and a candidate recurring across groups is the
    normal case — 23,807 accessions over 4,797 groups. Real MaxQuant groups are disjoint, so this
    is a synthetic overlap; the batch must still be well-formed rather than depend on it.

    **`sorted(protein_ids) == sorted(set(protein_ids))` was written here and is withdrawn.** It
    cannot fail: `parse` runs `invariants.validate` before returning, and a duplicate `(label, id)`
    is refused by structural validation, so `parsed.nodes` never reaches an assertion carrying one.
    Removing the adapter's `staged_proteins` filter does fail this test — with
    `STRUCTURE — duplicate node id 'uniprot:P09914' for label 'Protein'`, raised inside `parse` —
    which establishes the write path's guard and not the line. The set comparison below is the one
    that discriminates, demonstrated with `candidate_nodes([*group, "Q9NRZ9"])`: an extra node no
    edge names is a valid change-set, so it reaches the assertion and fails it.
    """
    rows = [
        _row(row_id="0", proteins=f"{MX1};{IFIT1}"),
        _row(row_id="1", proteins=f"{IFIT1};{ISG15}", lfq_wt="42"),
    ]
    parsed = _adapter().parse(_write(tmp_path, rows), _mapping())
    protein_ids = [n["id"] for n in parsed.nodes if n[NODE_TYPE_KEY] == "Protein"]
    assert set(protein_ids) == {f"uniprot:{MX1}", f"uniprot:{IFIT1}", f"uniprot:{ISG15}"}


def test_an_empty_group_is_refused_and_counted(tmp_path: Path) -> None:
    """The one refusal kind at this grain, and it is a counted kind and nothing more (`base.py`).
    Measured **0** instances on the real file, so it is tested against a synthetic row."""
    rows = [_row(row_id="0"), _row(row_id="1", proteins="")]
    adapter = _adapter()
    parsed = adapter.parse(_write(tmp_path, rows), _mapping())
    assert [r.reason for r in parsed.refusals] == ["empty_protein_group"]
    assert parsed.refusals[0].row == "1"
    assert adapter.report is not None
    assert (adapter.report.groups_emitted, adapter.report.refused_empty_group) == (1, 1)
    # Refused, not merely flagged: no observation and no cells for it.
    assert len([n for n in parsed.nodes if n[NODE_TYPE_KEY] == "ProteinObservation"]) == 1
    assert len(parsed.cells[0][1]) == 2, "two samples for the one surviving row, none for the other"


def test_the_site_refusal_slugs_do_not_transfer(tmp_path: Path) -> None:
    """`no_razor_pick`, `unresolved_protein` and `residue_mismatch` are site-grain kinds and none
    can arise here: nothing is picked, no sequence is needed, and there is no residue. Asserted so
    a later edit cannot quietly reintroduce a pick at this grain under a familiar name."""
    rows = [_row(row_id="0", proteins=f"{MX1};{IFIT1}"), _row(row_id="1", proteins="")]
    parsed = _adapter().parse(_write(tmp_path, rows), _mapping())
    assert {r.reason for r in parsed.refusals} == {"empty_protein_group"}


# ── Filtering, counted rather than merely applied ───────────────────────────────────────────────


def test_decoys_and_contaminants_are_dropped_and_counted(tmp_path: Path) -> None:
    rows = [
        _row(row_id="0"),
        _row(row_id="1", proteins=IFIT1, reverse="+"),
        _row(row_id="2", proteins=ISG15, contaminant="+"),
    ]
    adapter = _adapter()
    adapter.parse(_write(tmp_path, rows), _mapping())
    report = adapter.report
    assert report is not None
    assert (report.rows_read, report.dropped_decoy_or_contaminant) == (3, 2)
    assert report.groups_emitted == 1


def test_the_filters_reach_the_analysis(tmp_path: Path) -> None:
    """I16: a filter the platform applied and did not record is the invisible analytical choice
    `ROADMAP.md` names. `filters_applied` is identifying on `Analysis` (§3), so it is not cosmetic.
    """
    parsed = _adapter().parse(_write(tmp_path, [_row()]), _mapping())
    analysis = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "Analysis")
    assert analysis["filters_applied"] == ["potential_contaminant", "reverse"]
    assert analysis["kind"] == "processing"
    assert analysis["parameters_observed"] is True
    assert analysis["quantity"] == "lfq"
    assert analysis["localization_threshold"] is None, "no residue to localise at this grain"
    assert analysis["test"] is None and analysis["fdr_method"] is None


def test_the_pipeline_metadata_is_recorded_on_the_dataset(tmp_path: Path) -> None:
    """I13: `search_engine` and its version are data, recorded once on the `Dataset` and never
    branched on downstream. The file does not state them, so they are declared."""
    parsed = _adapter().parse(_write(tmp_path, [_row()]), _mapping())
    dataset = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "Dataset")
    assert dataset["search_engine"] == "maxquant"
    assert dataset["search_engine_version"] == "1.6.10.43"
    assert dataset["content_hash"].startswith("sha256:")


# ── I11: the per-sample values the adapter retains (ADR-0004, ADR-0013) ─────────────────────────


def test_every_observation_carries_its_quant_ref_and_its_cells(tmp_path: Path) -> None:
    """I11's positive obligation at this grain, both halves: the witness on the node and the cells.

    `quant_ref` names the table, not a join key — the join is on `id` (§2, ADR-0004) — and a `None`
    there is the violation state the DDL column exists to make readable from the graph alone.
    """
    parsed = _adapter().parse(_write(tmp_path, [_row()]), _mapping())
    observation = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "ProteinObservation")
    assert observation["quant_ref"] == "protein_values"

    assert [label for label, _ in parsed.cells] == ["ProteinObservation"]
    cells = parsed.cells[0][1]
    assert {(c.sample_id, c.quantity, c.value) for c in cells} == {
        ("bzk:sampleWT", "lfq", 1500000.0),
        ("bzk:sampleKO", "lfq", 2500000.0),
    }
    assert all(c.observation_id == observation["id"] for c in cells)


def test_the_declared_quantity_chooses_the_column_family(tmp_path: Path) -> None:
    """I16's record and the numbers cannot disagree, because the declaration is what is read. The
    same row read as `lfq` and as `intensity` yields different values from different columns."""
    row = _row(lfq_wt="10", intensity_wt="20")
    by_quantity = {}
    for quantity in ("lfq", "intensity"):
        parsed = _adapter(quantity).parse(_write(tmp_path, [row]), _mapping(quantity))
        cells = {c.sample_id: c for c in parsed.cells[0][1]}
        by_quantity[quantity] = cells["bzk:sampleWT"]
    assert by_quantity["lfq"].value == 10.0
    assert by_quantity["intensity"].value == 20.0
    assert by_quantity["lfq"].quantity == "lfq"
    assert by_quantity["intensity"].quantity == "intensity"


def test_a_reported_zero_stays_a_zero(tmp_path: Path) -> None:
    """`maxquant.cell_value`'s decision, asserted at this grain because it is where it bites:
    **26,744 of the 67,158 `LFQ intensity` cells on the real file are `0` (39.8%)**. Folding them
    to null would be the adapter interpreting MaxQuant's convention, which I19 leaves to the
    statistics layer — and it would silently disagree with `maxquant_sites.py`."""
    parsed = _adapter().parse(_write(tmp_path, [_row(lfq_wt="0", lfq_ko="")]), _mapping())
    by_sample = {c.sample_id: c.value for c in parsed.cells[0][1]}
    assert by_sample["bzk:sampleWT"] == 0.0, "a reported zero is a measurement"
    assert by_sample["bzk:sampleKO"] is None, "a blank is an absence"


def test_a_refused_row_contributes_no_cells(tmp_path: Path) -> None:
    """The matrix must not outlive the observation it belongs to: a refused row has no observation
    id to key cells against, so orphan rows would be unreachable by construction."""
    adapter = _adapter()
    parsed = adapter.parse(_write(tmp_path, [_row(proteins="")]), _mapping())
    assert [r.reason for r in parsed.refusals] == ["empty_protein_group"]
    assert parsed.cells == []
    assert adapter.report is not None
    assert adapter.report.cells == 0


def test_the_peptide_count_is_optional_and_not_invented(tmp_path: Path) -> None:
    """`n_peptides` is non-identifying (§3) and absent rather than zero where the file is blank:
    zero peptides would be a claim the file did not make."""
    header = [c for c in HEADER if c not in {"Peptides", "Razor + unique peptides"}]
    row = [
        v for i, v in enumerate(_row()) if HEADER[i] not in {"Peptides", "Razor + unique peptides"}
    ]
    parsed = _adapter().parse(_write(tmp_path, [row], header=header), _mapping())
    observation = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "ProteinObservation")
    assert "n_peptides" not in observation


# ── Refusing the file rather than half-reading it ───────────────────────────────────────────────


def test_a_mapping_key_naming_no_column_is_refused(tmp_path: Path) -> None:
    """Skipping the sample would drop it from the matrix while leaving its `Sample` node in the
    graph — I11 unmet in a shape nothing would notice."""
    mapping = SampleMapping(
        curation_analysis_id="bzk:c",
        samples=[_sample("bzk:s", "WT_1", "LFQ intensity Ratio mod/base WT_1", "WT")],
    )
    with pytest.raises(MaxQuantProteinGroupsError, match="names no column"):
        _adapter().parse(_write(tmp_path, [_row()]), mapping)


def test_a_mapping_key_from_another_family_is_refused(tmp_path: Path) -> None:
    """The declared quantity chooses the columns, so a key naming another family would record one
    quantity on the `Analysis` and store another (I16). The column exists; it is the wrong one."""
    mapping = SampleMapping(
        curation_analysis_id="bzk:c",
        samples=[_sample("bzk:s", "WT_P_1", "Intensity WT_P_1", "WT")],
    )
    with pytest.raises(MaxQuantProteinGroupsError, match="declared quantity's family"):
        _adapter("lfq").parse(_write(tmp_path, [_row()]), mapping)


def test_an_empty_sample_mapping_is_refused(tmp_path: Path) -> None:
    """A protein group with no sample has no values to retain, so `quant_ref` would be set over an
    empty matrix — worse than the null the DDL calls the violation state."""
    with pytest.raises(MaxQuantProteinGroupsError, match="no sample mapping"):
        _adapter().parse(
            _write(tmp_path, [_row()]), SampleMapping(curation_analysis_id="bzk:c", samples=[])
        )


def test_a_missing_accession_column_is_named_not_crashed_on(tmp_path: Path) -> None:
    header = [c for c in HEADER if c != "Protein IDs"]
    row = [v for i, v in enumerate(_row()) if HEADER[i] != "Protein IDs"]
    with pytest.raises(MaxQuantProteinGroupsError, match="Protein IDs"):
        _adapter().parse(_write(tmp_path, [row], header=header), _mapping())


def test_a_declared_quantity_with_no_column_family_is_refused() -> None:
    """It is identifying on `Analysis` (§3), so a misspelling forks an id rather than failing."""
    with pytest.raises(MaxQuantProteinGroupsError, match="names no column family"):
        MaxQuantProteinGroupsAdapter(
            DeclaredProteinAnalysis(
                search_engine="maxquant", external_version="1", quantity="ratio_mod_base"
            )
        )


def test_sniff_tells_the_two_maxquant_tables_apart(tmp_path: Path) -> None:
    """Content, not name (`ARCHITECTURE.md` §3): both are tab-separated `.txt` in one deposit. The
    site table's own `sniff` keys on the residue and position columns, so the two are mutually
    exclusive rather than merely different."""
    from bzk.adapters.maxquant_sites import DeclaredSiteAnalysis, MaxQuantSiteAdapter

    groups = _write(tmp_path, [_row()])
    sites = tmp_path / "GlyGly (K)Sites.txt"
    sites.write_bytes(
        b"Proteins\tPositions within proteins\tProtein\tPosition\tAmino acid\t"
        b"Localization prob\tid\r\n"
        b"P20591\t4\tP20591\t4\tK\t0.99\t0\r\n"
    )
    site_adapter = MaxQuantSiteAdapter(
        DeclaredSiteAnalysis(search_engine="maxquant", external_version="1.6.10.43")
    )
    assert _adapter().sniff(groups)
    assert not _adapter().sniff(sites)
    assert site_adapter.sniff(sites)
    assert not site_adapter.sniff(groups)
