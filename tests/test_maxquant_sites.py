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
from bzk.ontology import invariants, schema
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
    # The per-sample quantitative columns I11 retains. Added 2026-08-08 with `bzk/quant/`: the
    # adapter now refuses a mapping key whose run label names no column, so a fixture without
    # them is a mapping the adapter cannot place rather than a fixture with nothing to retain.
    "Intensity WT_1",
    "Ratio mod/base WT_1",
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
    intensity: str = "150520",
    ratio: str = "NaN",
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
        intensity,
        ratio,
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


# ── Slice 3: the ambiguous default on every site ────────────────────────────────────────────────


def test_every_site_gets_an_ambiguous_assignment(tmp_path: Path) -> None:
    """§6.1: the default is created automatically, `inferred_default` / `ambiguous`, naming the
    candidate set rather than a modifier. Enforced by I3, so this asserts the *content* the
    invariant cannot — that the candidate set is the three-member closed enum and not, say, empty.
    """
    parsed = _adapter().parse(_write(tmp_path, [_row()]), _mapping())
    assignment = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "ModifierAssignment")
    assert assignment["basis"] == "inferred_default"
    assert assignment["confidence"] == "ambiguous"
    assert assignment["candidate_modifiers"] == [
        "uniprot:P05161",
        "uniprot:P0CG48",
        "uniprot:Q15843",
    ]
    observation = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "SiteObservation")
    assert {"type": "ASSIGNMENT_FOR", "from": assignment["id"], "to": observation["id"]} in (
        parsed.edges
    )


def test_the_default_assignment_names_no_modifier(tmp_path: Path) -> None:
    """I3, and the product: a K-GG site is not reported as ubiquitination. `ASSIGNS` is what would
    name one, and an ambiguous assignment may not carry it — so its absence here is the claim."""
    parsed = _adapter().parse(_write(tmp_path, [_row()]), _mapping())
    assert not [e for e in parsed.edges if e["type"] == "ASSIGNS"]


def test_the_modifier_set_is_seeded_from_its_one_home(tmp_path: Path) -> None:
    """`candidate_modifiers` names ids, so the `Modifier` nodes must be in the change-set — the
    same treatment `candidate_proteins` gets. Seeded from `schema.GG_REMNANT_MODIFIERS` via
    `seed.modifier_nodes()`, never written out here, so the set has one home (ADR-0021)."""
    parsed = _adapter().parse(_write(tmp_path, [_row()]), _mapping())
    modifiers = {n["id"]: n for n in parsed.nodes if n[NODE_TYPE_KEY] == "Modifier"}
    assert set(modifiers) == set(schema.GG_REMNANT_MODIFIERS)
    assert modifiers["uniprot:P0CG48"]["name"] == "ubiquitin"
    assert modifiers["uniprot:P0CG48"]["c_terminal_motif"] == "LRLRGG"
    assert all(m["leaves_gg_remnant"] for m in modifiers.values())
    # Every id named by an assignment is a node in the same change-set.
    assignment = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "ModifierAssignment")
    assert set(assignment["candidate_modifiers"]) <= set(modifiers)


def test_re_ingesting_converges_on_one_assignment(tmp_path: Path) -> None:
    """`asserted_at` is excluded from identity (§3), so a second run of the same file produces the
    same assignment id rather than a new one per run — which is what makes I9's replay idempotent
    and I6's retraction meaningful (a superseding assignment must be a *different* node)."""
    path = _write(tmp_path, [_row()])
    first = _adapter().parse(path, _mapping())
    second = _adapter().parse(path, _mapping())
    ids = [
        {n["id"] for n in p.nodes if n[NODE_TYPE_KEY] == "ModifierAssignment"}
        for p in (first, second)
    ]
    assert ids[0] == ids[1]


def test_two_sites_get_two_distinct_assignments(tmp_path: Path) -> None:
    """The `SiteObservation` anchor is what separates them; the fields are identical across sites,
    so an id built from fields alone would collapse every site's assignment into one node."""
    rows = [_row(position=p, positions=p, row_id=str(i)) for i, p in enumerate(("4", "7"))]
    parsed = _adapter().parse(_write(tmp_path, rows), _mapping())
    assignments = [n for n in parsed.nodes if n[NODE_TYPE_KEY] == "ModifierAssignment"]
    assert len({a["id"] for a in assignments}) == 2


def test_a_refused_site_gets_no_assignment(tmp_path: Path) -> None:
    """A refused row produces no observation, so it must produce no assignment either — an
    assignment attached to nothing would be a dangling inference."""
    parsed = _adapter().parse(_write(tmp_path, [_row(position="5", positions="5")]), _mapping())
    assert not [n for n in parsed.nodes if n[NODE_TYPE_KEY] == "SiteObservation"]
    assert not [n for n in parsed.nodes if n[NODE_TYPE_KEY] == "ModifierAssignment"]


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


# ── ADR-0024: keying is recorded on the observation, not as a ProteinAssignment ──────────────────


def test_an_unpromoted_site_records_the_razor_keying(tmp_path: Path) -> None:
    """`keying_basis` is always set — a null-means-razor convention would make "not recorded" and
    "recorded as the search engine's pick" indistinguishable, which is the silence I17 forbids."""
    parsed = _adapter().parse(_write(tmp_path, [_row()]), _mapping())
    observation = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "SiteObservation")
    assert observation["keying_basis"] == "razor"
    assert observation["displaced_protein"] is None
    assert not [n for n in parsed.nodes if n[NODE_TYPE_KEY] == "ProteinAssignment"]


def test_a_promotion_is_recorded_on_the_observation_not_as_an_assignment(tmp_path: Path) -> None:
    """ADR-0024: `reviewed_preferred` left the `ProteinAssignment.basis` enum, because a reviewed
    entry is better annotated and not better evidenced. The override still has to be recorded —
    trading an over-claim for a silence would be worse than the conflict it resolved."""
    unreviewed = Resolution(
        status="ok",
        requested=IFIT1,
        canonical=IFIT1,
        isoform=None,
        is_isoform=False,
        reviewed=False,
        entry_type="UniProtKB unreviewed (TrEMBL)",
        sequence=SYNTHETIC_SEQUENCE,
        sequence_version=1,
        last_seq_update=None,
        gene=None,
        sequence_source="canonical",
    )
    row = _row(proteins=f"{IFIT1};{MX1}", positions="4;4", pick=IFIT1, position="4")
    adapter = _adapter({IFIT1: unreviewed, MX1: _ok(MX1)})
    parsed = adapter.parse(_write(tmp_path, [row]), _mapping())

    observation = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "SiteObservation")
    assert observation["keying_basis"] == "reviewed_preferred"
    assert observation["displaced_protein"] == f"uniprot:{IFIT1}"
    assert not [n for n in parsed.nodes if n[NODE_TYPE_KEY] == "ProteinAssignment"]
    site = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "ModificationSite")
    assert site["id"].startswith(f"uniprot:{MX1}#"), "the site keys against the promoted entry"


def test_promotion_is_refused_where_it_would_break_validity(tmp_path: Path) -> None:
    """**The TAP1 case.** ADR-0024 rule 1: I2 makes a site keyed at a non-matching residue
    meaningless, so preference cannot license an invalid keying. The unreviewed pick has K at 4;
    the reviewed alternative has G there, so the original keying stands and the site survives.

    Measured on the real deposit at 4 of 526 promotions — TAP1 twice, PTBP1 twice.
    """
    unreviewed = Resolution(
        status="ok",
        requested=IFIT1,
        canonical=IFIT1,
        isoform=None,
        is_isoform=False,
        reviewed=False,
        entry_type="UniProtKB unreviewed (TrEMBL)",
        sequence=SYNTHETIC_SEQUENCE,
        sequence_version=1,
        last_seq_update=None,
        gene=None,
        sequence_source="canonical",
    )
    # MX1's synthetic sequence has G at position 5, not K — promoting there would refuse the site.
    row = _row(proteins=f"{IFIT1};{MX1}", positions="4;5", pick=IFIT1, position="4")
    adapter = _adapter({IFIT1: unreviewed, MX1: _ok(MX1)})
    parsed = adapter.parse(_write(tmp_path, [row]), _mapping())

    assert parsed.refusals == [], "the site must survive rather than be refused"
    observation = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "SiteObservation")
    assert observation["keying_basis"] == "razor"
    site = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "ModificationSite")
    assert site["id"].startswith(f"uniprot:{IFIT1}#"), "the original keying stands"


def test_two_distinct_canonical_reviewed_proteins_block_promotion(tmp_path: Path) -> None:
    """ADR-0024 rule 3, and OAS1's case: `F8VXY3` and `P00973` are both canonical and both
    reviewed. Choosing between two genuinely different reviewed proteins is a claim about peptide
    origin — the search engine's job, and what I14 forbids resolution from asserting."""
    unreviewed = Resolution(
        status="ok",
        requested="Q00000",
        canonical="Q00000",
        isoform=None,
        is_isoform=False,
        reviewed=False,
        entry_type="UniProtKB unreviewed (TrEMBL)",
        sequence=SYNTHETIC_SEQUENCE,
        sequence_version=1,
        last_seq_update=None,
        gene=None,
        sequence_source="canonical",
    )
    row = _row(proteins=f"Q00000;{MX1};{IFIT1}", positions="4;4;4", pick="Q00000", position="4")
    adapter = _adapter({"Q00000": unreviewed, MX1: _ok(MX1), IFIT1: _ok(IFIT1)})
    parsed = adapter.parse(_write(tmp_path, [row]), _mapping())
    observation = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "SiteObservation")
    assert observation["keying_basis"] == "razor", "two canonical reviewed candidates: no promotion"


# ── I11: the per-sample values the adapter retains (ADR-0004, ADR-0013) ─────────────────────────


def test_every_observation_carries_its_quant_ref_and_its_cells(tmp_path: Path) -> None:
    """I11's positive obligation at this grain, both halves: the witness on the node and the cells.

    `quant_ref` names the table, not a join key — the join is on `id` (§2, ADR-0004) — and a `None`
    there would mean no values retained, which is the violation state.
    """
    parsed = _adapter().parse(_write(tmp_path, [_row()]), _mapping())
    observations = [n for n in parsed.nodes if n[NODE_TYPE_KEY] == "SiteObservation"]
    assert observations and all(o["quant_ref"] == "site_values" for o in observations)

    assert [label for label, _ in parsed.cells] == ["SiteObservation"]
    cells = parsed.cells[0][1]
    assert {(c.observation_id, c.quantity) for c in cells} == {
        (observations[0]["id"], "intensity_multiplicity_summed"),
        (observations[0]["id"], "ratio_mod_base"),
    }
    assert all(c.sample_id == "bzk:sample1" for c in cells)


def test_maxquant_s_literal_nan_becomes_a_null_and_a_zero_does_not(tmp_path: Path) -> None:
    """Measured on PXD018299: `Ratio mod/base` is the text `NaN` for 196 of the first 200 rows, and
    `float()` accepts it — so without this the store would hold a NaN *value* where the deposit
    means no value. A reported `0` is a different thing and stays (I19)."""
    parsed = _adapter().parse(_write(tmp_path, [_row(intensity="0", ratio="NaN")]), _mapping())
    by_quantity = {c.quantity: c.value for c in parsed.cells[0][1]}
    assert by_quantity["ratio_mod_base"] is None, "NaN is an absence"
    assert by_quantity["intensity_multiplicity_summed"] == 0.0, "a reported zero is a measurement"


def test_a_refused_row_contributes_no_cells(tmp_path: Path) -> None:
    """The matrix must not outlive the observation it belongs to: a row the adapter refuses has no
    `SiteObservation` id to key cells against, so orphan rows would be unreachable by construction."""
    parsed = _adapter().parse(_write(tmp_path, [_row(residue="R")]), _mapping())
    assert [r.reason for r in parsed.refusals] == ["residue_mismatch"]
    assert parsed.cells == []
