"""`bzk/sources/pxd026748_ingest_figures.py` — the arithmetic, on synthetic inputs.

**Entirely offline, and nothing here touches PXD026748.** The module's whole job is to read two
real deposits that exist only on bzk's machine; what can be tested here is the arithmetic it
applies once a parse has happened, so these tests build small tables under `tmp_path`, parse them
through the same adapters, and check the numbers the pure functions return. No deposit and no
generated fixture is committed.

**The GG arm's resolver is injected**, as `tests/test_rebuild.py` injects one: the real path
reaches UniProt for every distinct razor pick, and a test that did so would be slow, would depend
on the network, and would stop testing the day a sequence was amended — stopping *green*.

**`main`'s failure path is tested against a temporary `home`, never the real one.**
`rebuild.replay_ingestion`'s docstring records what the alternative cost: a default that pointed at
`~/.bzk-omics/raw/` once made a test ingest the actual 2.8 MB deposit, 78 seconds a run, with
counts that depended on whether the developer had fetched it.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

import pytest

from bzk.adapters import maxquant
from bzk.adapters.base import SampleMapping
from bzk.adapters.maxquant_protein_groups import (
    DeclaredProteinAnalysis,
    MaxQuantProteinGroupsAdapter,
)
from bzk.adapters.maxquant_sites import DeclaredSiteAnalysis, MaxQuantSiteAdapter
from bzk.ontology.invariants import NODE_TYPE_KEY
from bzk.sources import pxd026748_ingest_figures as figures

# Real accessions (`CLAUDE.md` § Working style); nothing here depends on what UniProt says of them.
MX1 = "P20591"
IFIT1 = "P09914"

#: Synthetic, and labelled as such — K at 4, 7 and 10.
SYNTHETIC_SEQUENCE = "MAAKGGKLLKR"


def _write(tmp_path: Path, name: str, header: list[str], rows: list[list[str]]) -> Path:
    """A synthetic MaxQuant table. CRLF, as both real deposits are."""
    lines = ["\t".join(header)] + ["\t".join(r) for r in rows]
    path = tmp_path / name
    path.write_bytes(("\r\n".join(lines) + "\r\n").encode("utf-8"))
    return path


def _sample(sample_id: str, key: str) -> dict[str, object]:
    return {
        NODE_TYPE_KEY: "Sample",
        "id": sample_id,
        "label": key.split()[-1],
        "source_type": "cell_line",
        "cell_line": "HeLa",
        "organism_taxid": "NCBITaxon:9606",
        "model_system": None,
        "genotype": "WT",
        "treatment": "none",
        "timepoint_h": None,
        "replicate": 1,
        "replicate_type": "biological",
        "mapping_key": key,
    }


def _resolver(*accessions: str) -> Any:
    from bzk.resolve.uniprot import Resolution

    allowed = set(accessions)

    def _resolve(requested: str) -> Resolution:
        assert requested in allowed, requested
        return Resolution(
            status="ok",
            requested=requested,
            canonical=requested,
            isoform=None,
            is_isoform=False,
            reviewed=True,
            entry_type="UniProtKB reviewed (Swiss-Prot)",
            sequence=SYNTHETIC_SEQUENCE,
            sequence_version=4,
            last_seq_update="2019-12-11",
            gene=None,
            sequence_source="canonical",
        )

    return _resolve


# ── T1 · the shotgun arm's arithmetic ───────────────────────────────────────────────────────────

SHOTGUN_HEADER = [
    "Protein IDs",
    "Majority protein IDs",
    "Peptides",
    "Razor + unique peptides",
    "Reverse",
    "Potential contaminant",
    "Only identified by site",
    "id",
    "LFQ intensity A",
    "LFQ intensity B",
    "Intensity A",
    "Intensity B",
]


def _shotgun_mapping() -> SampleMapping:
    return SampleMapping(
        curation_analysis_id="bzk:curation1",
        samples=[
            _sample("bzk:sampleA", "LFQ intensity A"),
            _sample("bzk:sampleB", "LFQ intensity B"),
        ],
    )


def _shotgun_parse(tmp_path: Path) -> tuple[Any, Any, maxquant.MaxQuantTable, dict[str, int]]:
    """Three rows: a decoy that is also site-only, a site-only row that is kept, an ordinary row.

    The first is the overlap the shotgun record's FILTERS item was corrected for on 2026-09-19,
    having first assumed there was none — so it is the case this fixture field exists to measure.
    """
    rows = [
        # only-identified-by-site AND Reverse: in_file, dropped, never emitted
        [MX1, MX1, "3", "2", "+", "", "+", "0", "10", "20", "11", "21"],
        # only-identified-by-site and kept: in_file, emitted
        [IFIT1, IFIT1, "4", "3", "", "", "+", "1", "0", "40", "31", "41"],
        # ordinary
        [MX1, MX1, "7", "5", "", "", "", "2", "50", "", "51", "61"],
    ]
    path = _write(tmp_path, "proteinGroups.txt", SHOTGUN_HEADER, rows)
    adapter = MaxQuantProteinGroupsAdapter(
        DeclaredProteinAnalysis(search_engine="maxquant", external_version="1.6.17.0")
    )
    parsed = adapter.parse(path, _shotgun_mapping())
    assert adapter.report is not None, "`parse` sets the report; a None here is a broken adapter"
    table = maxquant.read_table(path)
    return adapter, parsed, table, {n: i for i, n in enumerate(table.header)}


def test_only_identified_by_site_separates_dropped_from_emitted(tmp_path: Path) -> None:
    """T1. Two rows carry the flag; one of them is also a decoy and never reaches the graph.

    `emitted` is counted through the adapter's `observation_of_row`, not as `in_file - dropped`.
    The subtraction is right here and wrong in general: a row can also fail to be emitted by being
    refused, and the difference would then report it as dropped for a reason it was not.
    """
    adapter, parsed, table, column = _shotgun_parse(tmp_path)
    fixture = figures.shotgun_fixture(
        curation=_stub_curation("PXD026748", "proteinGroups.txt"),
        report=adapter.report,
        parsed=parsed,
        table=table,
        column=column,
    )

    assert fixture["only_identified_by_site"] == {
        "column_present": True,
        "in_file": 2,
        "emitted": 1,
        "dropped_as_decoy_or_contaminant": 1,
    }


def test_shotgun_cells_are_counted_by_quantity_and_by_positivity(tmp_path: Path) -> None:
    """T1's second half. Two groups survive the decoy filter, two samples, two families present:
    eight cells. A reported `0` is a measurement and stays in the total (I19), so it is the gap
    between the two mappings — as is the blank, which is an absence."""
    adapter, parsed, table, column = _shotgun_parse(tmp_path)
    fixture = figures.shotgun_fixture(
        curation=_stub_curation("PXD026748", "proteinGroups.txt"),
        report=adapter.report,
        parsed=parsed,
        table=table,
        column=column,
    )

    assert fixture["cells"]["by_quantity"] == {"intensity": 4, "lfq": 4}
    # lfq: row 1 has 0 and 40 (one positive), row 2 has 50 and blank (one positive).
    assert fixture["cells"]["positive_by_quantity"] == {"intensity": 4, "lfq": 2}
    assert fixture["analysis_quantity"] == "lfq"


# ── T2 · the GG arm's arithmetic ────────────────────────────────────────────────────────────────

SITE_HEADER = [
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
    "Intensity A",
    "Intensity B",
]


def _site_mapping() -> SampleMapping:
    return SampleMapping(
        curation_analysis_id="bzk:curation1",
        samples=[_sample("bzk:sampleA", "Intensity A"), _sample("bzk:sampleB", "Intensity B")],
    )


def _digly_figures(tmp_path: Path, rows: list[list[str]], *, picks: tuple[str, ...]) -> Any:
    path = _write(tmp_path, "GlyGly (K)Sites.txt", SITE_HEADER, rows)
    adapter = MaxQuantSiteAdapter(
        DeclaredSiteAnalysis(search_engine="maxquant", external_version="1.6.17.0"),
        resolver=_resolver(*picks),
    )
    parsed = adapter.parse(path, _site_mapping())
    assert adapter.report is not None, "`parse` sets the report; a None here is a broken adapter"
    table = maxquant.read_table(path)
    column = {n: i for i, n in enumerate(table.header)}
    after_decoys = maxquant.drop_decoys_and_contaminants(table)
    after_localisation, _, _ = adapter._filter(table, column)
    return figures.digly_fixture(
        curation=_stub_curation("PXD026748", "GlyGly (K)Sites.txt"),
        report=adapter.report,
        parsed=parsed,
        rows_after_decoys=after_decoys,
        rows_after_localisation=after_localisation,
        column=column,
    )


def test_the_three_multi_protein_denominators_are_three_different_populations(
    tmp_path: Path,
) -> None:
    """T2. One multi-protein row kept, one single-protein row kept, one multi-protein row dropped
    below the localisation threshold.

    The three pairs disagree on purpose: the dropped row is multi-protein and counts in the first
    denominator and in no other, which is what makes *"the multi-protein share"* ambiguous until a
    denominator is named. Report 09 gives all three; nothing in it says which one the registered
    70–90% was meant to be compared against.
    """
    rows = [
        # multi-protein, kept
        [f"{MX1};{IFIT1}", "4;4", MX1, MX1, "4", "K", "0.99", "80", "", "", "0", "100", "200"],
        # single-protein, kept
        [MX1, "7", MX1, MX1, "7", "K", "0.98", "70", "", "", "1", "300", "400"],
        # multi-protein, below threshold
        [f"{MX1};{IFIT1}", "10;10", MX1, MX1, "10", "K", "0.10", "60", "", "", "2", "500", "600"],
    ]
    fixture = _digly_figures(tmp_path, rows, picks=(MX1,))

    assert fixture["multi_protein"]["after_decoy_or_contaminant"] == {
        "numerator": 2,
        "denominator": 3,
    }
    assert fixture["multi_protein"]["after_localisation"] == {"numerator": 1, "denominator": 2}
    assert fixture["multi_protein"]["emitted_observations"] == {"numerator": 1, "denominator": 2}


def test_an_isoform_razor_pick_counts_once_per_row_and_once_per_distinct_pick(
    tmp_path: Path,
) -> None:
    """The isoform pair, on the same shape. Two rows share one isoform pick and a third names a
    canonical one, so `rows` and `distinct_picks` give different numerators over different
    denominators — which is why the fixture records both rather than a single share."""
    isoform = f"{MX1}-2"
    rows = [
        [isoform, "4", isoform, isoform, "4", "K", "0.99", "80", "", "", "0", "100", "200"],
        [isoform, "7", isoform, isoform, "7", "K", "0.98", "70", "", "", "1", "300", "400"],
        [IFIT1, "10", IFIT1, IFIT1, "10", "K", "0.97", "60", "", "", "2", "500", "600"],
    ]
    fixture = _digly_figures(tmp_path, rows, picks=(isoform, IFIT1))

    assert fixture["isoform_razor_picks"]["rows"] == {"numerator": 2, "denominator": 3}
    assert fixture["isoform_razor_picks"]["distinct_picks"] == {"numerator": 1, "denominator": 2}


# ── T3 · no partial fixture ─────────────────────────────────────────────────────────────────────


def test_main_writes_neither_fixture_when_a_deposit_is_absent(tmp_path: Path) -> None:
    """T3. An empty `home` has neither deposit, so the first arm exits and nothing is written.

    The assertion that `fixtures_dir` is still empty is the one that matters: the failure mode this
    guards is a run that writes one arm's fixture and then dies, leaving a committed pair one turn
    out of step with each other.
    """
    home = tmp_path / "home"
    home.mkdir()
    fixtures_dir = tmp_path / "fixtures"
    fixtures_dir.mkdir()

    with pytest.raises(SystemExit) as caught:
        figures.main(home=home, fixtures_dir=fixtures_dir)

    message = str(caught.value)
    assert "curation_PXD026748.json" in message
    assert "No fixture was written" in message
    assert list(fixtures_dir.iterdir()) == []


# ── A stub loaded curation, so the pure functions can be called without the real records ────────


def _stub_curation(accession: str, filename: str) -> Any:
    """Just enough of a `LoadedCuration` for `_header`: one `Dataset` node.

    Built rather than loaded because these tests are about the arithmetic, and loading a real
    record here would tie every arithmetic assertion to a curation judgement that the review loop
    owns and that `tests/test_curation_pxd026748_arms.py` already covers.
    """

    dataset = {
        NODE_TYPE_KEY: "Dataset",
        "external_accession": accession,
        "label": filename,
        "content_hash": "sha256:" + "0" * 64,
    }

    class _Stub:
        nodes: ClassVar[list[dict[str, Any]]] = [dataset]

    return _Stub()
