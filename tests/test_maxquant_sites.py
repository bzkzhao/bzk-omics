"""`bzk/adapters/maxquant_sites.py` — the first search-output adapter (Slice 2).

Entirely offline: the resolver is injected, which is the whole point of the seam `resolve/nodes.py`
opened. Fixtures are **synthetic twins** of the real file's shapes rather than the real file, per
`HANDOFF.md` §8 — a refusal path tested against whichever accession happens to be stale in UniProt
today stops testing the day UniProt changes, and stops *green*.

The three refusals are tested separately because they are three different findings, and only one of
them — `residue_mismatch` — is the sequence-drift measurement the slice exists to produce.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bzk.adapters.base import SampleMapping
from bzk.adapters.maxquant_sites import (
    GLYGLY,
    DeclaredSiteAnalysis,
    MaxQuantSiteAdapter,
    MaxQuantSiteError,
)
from bzk.ontology import invariants
from bzk.ontology.invariants import NODE_TYPE_KEY
from bzk.resolve.nodes import Resolver
from bzk.resolve.uniprot import Resolution

# Real accessions; the sequences are synthetic and marked as such — `CLAUDE.md` § Working style
# permits an invented sequence only where it is labelled, and a real 500-mer would obscure the test.
MX1 = "P20591"
IFIT1 = "P09914"
SYNTHETIC_SEQUENCE = "MAAKGGKLLKR"  # K at 4, 7, 10; R at 11


def _ok(accession: str, *, sv: int = 4, sequence: str = SYNTHETIC_SEQUENCE) -> Resolution:
    return Resolution(
        status="ok",
        requested=accession,
        canonical=accession.split("-")[0],
        isoform=None,
        is_isoform="-" in accession,
        reviewed=True,
        entry_type="UniProtKB reviewed (Swiss-Prot)",
        sequence=sequence,
        sequence_version=sv,
        last_seq_update="2019-12-11",
        gene=None,
        sequence_source="canonical",
    )


def _resolver(table: dict[str, Resolution]) -> Resolver:
    def _resolve(accession: str) -> Resolution:
        return table[accession]

    return _resolve


HEADER = [
    "Proteins",
    "Positions within proteins",
    "Leading proteins",
    "Protein",
    "Position",
    "Amino acid",
    "Localization prob",
    "Score",
    "Reverse",
    "Potential contaminant",
    "id",
]


def _write(tmp_path: Path, rows: list[list[str]], header: list[str] | None = None) -> Path:
    """A synthetic site table. CRLF deliberately: the deposit is CRLF throughout."""
    lines = ["\t".join(header if header is not None else HEADER)]
    lines += ["\t".join(row) for row in rows]
    path = tmp_path / "GlyGly (K)Sites.txt"
    path.write_bytes(("\r\n".join(lines) + "\r\n").encode("utf-8"))
    return path


def _row(
    *,
    proteins: str = MX1,
    positions: str = "4",
    pick: str = MX1,
    position: str = "4",
    residue: str = "K",
    loc: str = "0.99",
    score: str = "80.5",
    reverse: str = "",
    contaminant: str = "",
    row_id: str = "0",
) -> list[str]:
    return [
        proteins,
        positions,
        pick,
        pick,
        position,
        residue,
        loc,
        score,
        reverse,
        contaminant,
        row_id,
    ]


def _mapping() -> SampleMapping:
    return SampleMapping(
        curation_analysis_id="bzk:curation1",
        samples=[
            {
                NODE_TYPE_KEY: "Sample",
                "id": "bzk:sample1",
                "label": "WT_1",
                "source_type": "cell_line",
                "cell_line": "HAP1",
                "organism_taxid": "NCBITaxon:9606",
                "model_system": None,
                "genotype": "WT",
                "treatment": "none",
                "timepoint_h": None,
                "replicate": 1,
                "replicate_type": "biological",
                # Not a DDL column — the curation loader adds it, and it must not reach the graph.
                "mapping_key": "Intensity WT_1",
            }
        ],
    )


def _adapter(table: dict[str, Resolution] | None = None) -> MaxQuantSiteAdapter:
    return MaxQuantSiteAdapter(
        DeclaredSiteAnalysis(search_engine="maxquant", external_version="1.6.10.43"),
        resolver=_resolver(table if table is not None else {MX1: _ok(MX1)}),
    )


# ── The happy path, and that it is a valid change-set ───────────────────────────────────────────


def test_one_row_becomes_a_site_and_an_observation(tmp_path: Path) -> None:
    parsed = _adapter().parse(_write(tmp_path, [_row()]), _mapping())
    labels = {n[NODE_TYPE_KEY] for n in parsed.nodes}
    assert {"Protein", "ProteinSequence", "ModificationSite", "SiteObservation"} <= labels
    site = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "ModificationSite")
    assert site["id"] == f"uniprot:{MX1}#sv4#K4#{GLYGLY}"
    assert site["residue"] == "K"
    assert site["position"] == 4
    assert parsed.refusals == []


def test_the_output_is_a_valid_change_set(tmp_path: Path) -> None:
    """`parse` validates before returning, so this is a second, independent assertion of it."""
    parsed = _adapter().parse(_write(tmp_path, [_row()]), _mapping())
    invariants.validate(parsed.nodes, parsed.edges)


def test_each_fact_is_written_once(tmp_path: Path) -> None:
    """ADR-0023: `RESOLVES_TO_SITE` and `REPORTED_BY` were duplicates of the two below and are gone
    from the DDL, so emitting them is no longer merely redundant — it would fail structural
    validation. Kept as an explicit assertion anyway: the surviving *direction* of `REPORTS_SITE`
    is the thing most easily got wrong, since its predecessor pointed the other way.
    """
    parsed = _adapter().parse(_write(tmp_path, [_row()]), _mapping())
    types = {e["type"] for e in parsed.edges}
    assert {"REPORTS_SITE", "MEASURED_AT"} <= types
    assert not types & {"REPORTED_BY", "RESOLVES_TO_SITE"}
    reports = next(e for e in parsed.edges if e["type"] == "REPORTS_SITE")
    observation = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "SiteObservation")
    assert reports["to"] == observation["id"], "REPORTS_SITE runs Dataset -> SiteObservation"


def test_the_sample_descriptor_is_narrowed_to_its_columns(tmp_path: Path) -> None:
    """`SampleMapping.samples` holds descriptors, not nodes (`base.py`). `mapping_key` is the
    curation record's column header and is not a `Sample` column; passing it through would put a
    phantom field into the graph."""
    parsed = _adapter().parse(_write(tmp_path, [_row()]), _mapping())
    sample = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "Sample")
    assert "mapping_key" not in sample
    assert sample["cell_line"] == "HAP1"


def test_a_group_keeps_every_candidate_but_keys_on_the_pick(tmp_path: Path) -> None:
    """ADR-0022: the group is the observation's identity; the pick is only what the site keys on."""
    row = _row(proteins=f"{MX1};{IFIT1}", positions="4;7", pick=MX1, position="4")
    parsed = _adapter({MX1: _ok(MX1)}).parse(_write(tmp_path, [row]), _mapping())
    observation = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "SiteObservation")
    assert observation["candidate_proteins"] == [f"uniprot:{MX1}", f"uniprot:{IFIT1}"]
    # The candidate that keys nothing still gets a Protein node, and no ProteinSequence: the
    # accession was observed, but nothing here claims a sequence for it.
    assert {n["id"] for n in parsed.nodes if n[NODE_TYPE_KEY] == "Protein"} == {
        f"uniprot:{MX1}",
        f"uniprot:{IFIT1}",
    }
    assert [n["id"] for n in parsed.nodes if n[NODE_TYPE_KEY] == "ProteinSequence"] == [
        f"uniprot:{MX1}#sv4"
    ]


def test_one_protein_named_by_many_rows_is_resolved_once(tmp_path: Path) -> None:
    calls: list[str] = []

    def counting(accession: str) -> Resolution:
        calls.append(accession)
        return _ok(MX1)

    adapter = MaxQuantSiteAdapter(
        DeclaredSiteAnalysis(search_engine="maxquant", external_version="1.6.10.43"),
        resolver=counting,
    )
    rows = [_row(position=p, positions=p, row_id=str(i)) for i, p in enumerate(("4", "7", "10"))]
    parsed = adapter.parse(_write(tmp_path, rows), _mapping())
    assert calls == [MX1]
    assert len([n for n in parsed.nodes if n[NODE_TYPE_KEY] == "ModificationSite"]) == 3


# ── The three refusals ──────────────────────────────────────────────────────────────────────────


def test_a_residue_mismatch_is_refused_and_counted(tmp_path: Path) -> None:
    """**The measurement.** Position 5 of the synthetic sequence is G, not K: the sequence has been
    amended since the search, so the position no longer means what the search meant by it."""
    rows = [
        _row(position="4", positions="4", row_id="0"),
        _row(position="5", positions="5", row_id="1"),
    ]
    adapter = _adapter()
    parsed = adapter.parse(_write(tmp_path, rows), _mapping())
    assert adapter.report is not None
    assert adapter.report.refused_residue_mismatch == 1
    assert adapter.report.sites_emitted == 1
    refusal = next(r for r in parsed.refusals if r.reason == "residue_mismatch")
    assert refusal.row == "1"
    assert "'K'" in refusal.detail and "'G'" in refusal.detail
    # Refused, not merely flagged: nothing was emitted for it.
    assert all(n.get("position") != 5 for n in parsed.nodes)


def test_a_position_past_the_end_is_a_residue_mismatch(tmp_path: Path) -> None:
    """The other half of drift: the sequence was *shortened*. `residue_at` returns None and the
    refusal says so rather than reporting a residue it does not have."""
    adapter = _adapter()
    parsed = adapter.parse(_write(tmp_path, [_row(position="900", positions="900")]), _mapping())
    assert adapter.report is not None
    assert adapter.report.refused_residue_mismatch == 1
    assert "past the end" in parsed.refusals[0].detail


def test_a_row_with_no_razor_pick_is_refused(tmp_path: Path) -> None:
    """The real file's row 1319: seven proteins, two leading, and an empty `Protein`. MaxQuant
    declined to pick, and picking for it would invent the inference it withheld."""
    row = _row(proteins=f"{MX1};{IFIT1}", positions="4;7", pick="", position="")
    adapter = _adapter()
    parsed = adapter.parse(_write(tmp_path, [row]), _mapping())
    assert adapter.report is not None
    assert adapter.report.refused_no_razor_pick == 1
    assert adapter.report.sites_emitted == 0
    assert parsed.refusals[0].reason == "no_razor_pick"


def test_an_unresolvable_protein_is_refused_not_guessed(tmp_path: Path) -> None:
    """No sequence version means no `ProteinSequence` (I2), so the site cannot be keyed at all."""
    dead = Resolution(
        status="not_found",
        requested=MX1,
        canonical=MX1,
        isoform=None,
        is_isoform=False,
        reviewed=None,
        entry_type="",
        sequence=None,
        sequence_version=None,
        last_seq_update=None,
        gene=None,
        sequence_source="canonical",
    )
    adapter = _adapter({MX1: dead})
    parsed = adapter.parse(_write(tmp_path, [_row()]), _mapping())
    assert adapter.report is not None
    assert adapter.report.refused_unresolved_protein == 1
    assert "not_found" in parsed.refusals[0].detail
    # The Protein node survives — the accession was observed — but nothing is keyed against it.
    assert [n["id"] for n in parsed.nodes if n[NODE_TYPE_KEY] == "Protein"] == [f"uniprot:{MX1}"]
    assert not [n for n in parsed.nodes if n[NODE_TYPE_KEY] == "ModificationSite"]


def test_the_three_refusals_are_counted_apart(tmp_path: Path) -> None:
    """They are three findings, not one 'bad rows' number, and only one measures sequence drift."""
    rows = [
        _row(row_id="0"),  # fine
        _row(row_id="1", position="5", positions="5"),  # residue mismatch
        _row(row_id="2", pick="", position=""),  # no pick
        _row(row_id="3", proteins=IFIT1, pick=IFIT1, position="4", positions="4"),  # unresolvable
    ]
    unresolvable = Resolution(
        status="ok",
        requested=IFIT1,
        canonical=IFIT1,
        isoform=None,
        is_isoform=False,
        reviewed=True,
        entry_type="UniProtKB reviewed (Swiss-Prot)",
        sequence=None,
        sequence_version=2,
        last_seq_update=None,
        gene=None,
        sequence_source="isoform_fetch_failed",
    )
    adapter = _adapter({MX1: _ok(MX1), IFIT1: unresolvable})
    adapter.parse(_write(tmp_path, rows), _mapping())
    report = adapter.report
    assert report is not None
    assert (report.refused_residue_mismatch, report.refused_no_razor_pick) == (1, 1)
    assert report.refused_unresolved_protein == 1
    assert report.sites_emitted == 1


# ── Filtering, counted rather than merely applied ───────────────────────────────────────────────


def test_decoys_contaminants_and_poor_localization_are_dropped_and_counted(tmp_path: Path) -> None:
    rows = [
        _row(row_id="0"),
        _row(row_id="1", reverse="+"),
        _row(row_id="2", contaminant="+"),
        _row(row_id="3", loc="0.50"),
    ]
    adapter = _adapter()
    adapter.parse(_write(tmp_path, rows), _mapping())
    report = adapter.report
    assert report is not None
    assert report.rows_read == 4
    assert report.dropped_decoy_or_contaminant == 2
    assert report.dropped_below_localization == 1
    assert report.sites_emitted == 1


def test_the_localization_threshold_is_the_declared_one(tmp_path: Path) -> None:
    """I16: the threshold is a filter the adapter applies, so it is the caller's to declare and
    not a constant. A row at 0.80 passes 0.75 and fails 0.90."""
    rows = [_row(loc="0.80")]
    for threshold, expected in ((0.75, 1), (0.90, 0)):
        adapter = MaxQuantSiteAdapter(
            DeclaredSiteAnalysis(
                search_engine="maxquant",
                external_version="1.6.10.43",
                localization_threshold=threshold,
            ),
            resolver=_resolver({MX1: _ok(MX1)}),
        )
        adapter.parse(_write(tmp_path, rows), _mapping())
        assert adapter.report is not None
        assert adapter.report.sites_emitted == expected


# ── Refusing the file rather than half-reading it ───────────────────────────────────────────────


def test_a_missing_column_is_named_not_crashed_on(tmp_path: Path) -> None:
    header = [c for c in HEADER if c != "Position"]
    rows = [[v for i, v in enumerate(_row()) if HEADER[i] != "Position"]]
    path = _write(tmp_path, rows, header=header)
    with pytest.raises(MaxQuantSiteError, match="Position"):
        _adapter().parse(path, _mapping())


def test_an_empty_sample_mapping_is_refused(tmp_path: Path) -> None:
    """I5: results with no curation activity behind them would be permanently `unprovenanced`."""
    path = _write(tmp_path, [_row()])
    with pytest.raises(MaxQuantSiteError, match="unprovenanced"):
        _adapter().parse(path, SampleMapping(curation_analysis_id="bzk:c", samples=[]))


def test_a_declared_quantity_outside_the_enum_is_refused() -> None:
    """It is identifying on `Analysis` (§3), so a misspelling forks an id rather than failing."""
    with pytest.raises(MaxQuantSiteError, match="closed enum"):
        MaxQuantSiteAdapter(
            DeclaredSiteAnalysis(
                search_engine="maxquant", external_version="1", quantity="intensity_but_wrong"
            )
        )


def test_sniff_rejects_a_protein_groups_table(tmp_path: Path) -> None:
    """Content, not name: `proteinGroups.txt` is tab-separated `.txt` in this same deposit. What
    distinguishes a site table is a per-site residue and a position within the protein."""
    groups = tmp_path / "proteinGroups.txt"
    groups.write_bytes(b"Protein IDs\tMajority protein IDs\tid\r\nP20591\tP20591\t0\r\n")
    assert not _adapter().sniff(groups)
    assert _adapter().sniff(_write(tmp_path, [_row()]))
