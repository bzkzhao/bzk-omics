"""`bzk/rebuild.py`'s adapter dispatch — which adapter claims a file, and what it is told.

**Written because the replay could only ever have been right by accident.** `_adapter_for` could
return exactly one adapter class, and the report path read `sites_emitted` off whatever it got, so
a curation record naming a `proteinGroups.txt` either went un-ingested or crashed on an attribute
the protein report does not have. Dispatch and the report path are both widened, and the two
properties they now rest on are asserted here rather than argued in a docstring:

* the three `sniff`s are **pairwise disjoint**, which is what licenses `_adapter_for` to carry no
  "more than one adapter claims this" branch at all — a refusal for a case that cannot occur is an
  unreachable branch, and `rebuild.py` already records removing one for that reason;
* `QUANTITY_COLUMNS`' prefixes are **mutually non-prefixing**, which is what licenses
  `quantity_from_mapping_keys` to take the first family a key matches as *the* family.

Entirely offline and entirely synthetic, for `test_rebuild.py`'s reason. Nothing here reads the
real `~/.bzk-omics/`: every path is under `tmp_path` with an explicit `home`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from bzk.adapters.base import SampleMapping
from bzk.adapters.maxquant_protein_groups import (
    QUANTITY_COLUMNS,
    DeclaredProteinAnalysis,
    MaxQuantProteinGroupsAdapter,
    MaxQuantProteinGroupsError,
    quantity_from_mapping_keys,
)
from bzk.adapters.maxquant_sites import DeclaredSiteAnalysis, MaxQuantSiteAdapter
from bzk.adapters.perseus import DeclaredAnalysis, DeclaredContrast, PerseusAdapter
from bzk.ontology import store
from bzk.ontology.invariants import NODE_TYPE_KEY
from bzk.rebuild import _adapter_for, create_graph, replay_ingestion

FIXTURES = Path(__file__).parent / "fixtures"
SYNTHETIC_RECORD = FIXTURES / "curation_synthetic_loadable.json"

#: Real accessions (`CLAUDE.md` § Working style); nothing here depends on what UniProt says of them.
MX1 = "P20591"


def _site_adapter() -> MaxQuantSiteAdapter:
    return MaxQuantSiteAdapter(
        DeclaredSiteAnalysis(search_engine="maxquant", external_version="1.5.5.1")
    )


def _protein_adapter(quantity: str = "lfq") -> MaxQuantProteinGroupsAdapter:
    return MaxQuantProteinGroupsAdapter(
        DeclaredProteinAnalysis(
            search_engine="maxquant", external_version="1.5.5.1", quantity=quantity
        )
    )


def _perseus_adapter() -> PerseusAdapter:
    """Constructed as `tests/test_perseus.py:94` does: a declaration plus one contrast.

    That constructor signature is the whole reason `PerseusAdapter` is absent from `_adapter_for`
    — `contrasts` come from an analysis record, which the dispatch does not hold — so the fixture
    that builds one here is also the demonstration of why the dispatch cannot.
    """
    return PerseusAdapter(
        declared=DeclaredAnalysis(
            quantity="lfq",
            filters_applied=["reverse", "potential_contaminant"],
            test="welch_t",
            fdr_method="BH",
            external_version="1.6.15.0",
        ),
        contrasts=[
            DeclaredContrast(
                column_suffix="KO_IFN_WT_IFN", numerator="USP18-/- + IFN", denominator="WT + IFN"
            )
        ],
    )


# ── T1 · the three sniffs are pairwise disjoint ─────────────────────────────────────────────────


def _claims(path: Path) -> list[str]:
    """Which of the three adapters claims this file, by name."""
    return [
        name
        for name, adapter in (
            ("maxquant_sites", _site_adapter()),
            ("maxquant_protein_groups", _protein_adapter()),
            ("perseus", _perseus_adapter()),
        )
        if adapter.sniff(path)
    ]


def _every_txt_fixture() -> list[Path]:
    return sorted(FIXTURES.glob("*.txt"))


@pytest.mark.parametrize("path", _every_txt_fixture(), ids=lambda p: p.name)
def test_at_most_one_adapter_claims_any_file(path: Path) -> None:
    """The premise `_adapter_for` rests on, over every tab-separated fixture in the tree.

    `_adapter_for` tries the site adapter, then the protein one, and returns the first that claims
    the file. That is only a *dispatch* and not a coin toss because no file can be claimed twice;
    if this ever fails, the missing refusal branch in `_adapter_for` stops being unreachable and
    the order of the two `if`s silently becomes the decision.
    """
    assert len(_claims(path)) <= 1, f"{path.name} is claimed by more than one adapter"


def test_a_perseus_export_over_protein_groups_is_claimed_by_perseus_alone() -> None:
    """A Perseus tab-separated export keeps its source table's header, so column names alone put
    this file in the protein adapter's hands. Measured: before the annotation-row guard the
    protein `sniff` returned `True` here, which would have recorded a search output's grain over
    an analysis' values (I16)."""
    assert _claims(FIXTURES / "perseus_synthetic_over_protein_groups.txt") == ["perseus"]


def test_a_perseus_export_over_sites_is_claimed_by_perseus_alone() -> None:
    """The same, and this one was a live defect rather than a guard for a new branch: the site
    `sniff` returned `True` on this file in shipped code, and its docstring claimed the Perseus
    export in the deposit carries no residue or position column. A Perseus export of a *site*
    table carries both."""
    assert _claims(FIXTURES / "perseus_synthetic_over_sites.txt") == ["perseus"]


# ── T2 · the prefixes are mutually non-prefixing ────────────────────────────────────────────────


def test_no_quantity_prefix_is_a_prefix_of_another() -> None:
    """`quantity_from_mapping_keys` takes the first family whose prefix a key starts with, and that
    is only well defined while no prefix extends another — `Intensity ` and `Intensity L ` would
    make a SILAC key place in whichever family `QUANTITY_COLUMNS` happened to list first.

    Asserted rather than assumed because the derivation *depends* on it and a fourth row added to
    that dict is exactly the edit that would break it without touching this file.
    """
    prefixes = sorted(QUANTITY_COLUMNS.values())
    for a in prefixes:
        for b in prefixes:
            if a != b:
                assert not b.startswith(a), (
                    f"{b!r} extends {a!r}, so a key matching both is ambiguous"
                )


# ── T3 · quantity derived from the record's mapping keys ────────────────────────────────────────


def _mapping(*keys: str) -> SampleMapping:
    return SampleMapping(
        curation_analysis_id="bzk:curation1",
        samples=[
            {NODE_TYPE_KEY: "Sample", "id": f"bzk:sample{i}", "mapping_key": key}
            for i, key in enumerate(keys)
        ],
    )


def test_uniform_lfq_keys_derive_lfq() -> None:
    assert quantity_from_mapping_keys(_mapping("LFQ intensity A", "LFQ intensity B")) == "lfq"


def test_uniform_intensity_keys_derive_intensity() -> None:
    assert quantity_from_mapping_keys(_mapping("Intensity A", "Intensity B")) == "intensity"


def test_mixed_families_raise_and_name_the_keys() -> None:
    """Never a fallback to the dataclass default. A mapping the adapter cannot place in one family
    is a curation problem — the class `_sample_columns` already raises on — and `lfq` guessed here
    would put a quantity on the `Analysis` that nothing in the record supports (I16)."""
    with pytest.raises(MaxQuantProteinGroupsError) as caught:
        quantity_from_mapping_keys(_mapping("LFQ intensity A", "Intensity B"))
    message = str(caught.value)
    assert "LFQ intensity A" in message
    assert "Intensity B" in message


def test_ratio_keys_raise_and_name_the_keys() -> None:
    """PXD018299's own keys, and the reason the derivation runs *after* the protein `sniff` rather
    than before it: deriving first would raise on the record that replays today."""
    with pytest.raises(MaxQuantProteinGroupsError) as caught:
        quantity_from_mapping_keys(_mapping("Ratio mod/base WT_1", "Ratio mod/base WT_2"))
    message = str(caught.value)
    assert "Ratio mod/base WT_1" in message
    assert "Ratio mod/base WT_2" in message


# ── T4/T5 · dispatch, and a replay over a protein-groups deposit ────────────────────────────────


def _record(curation_dir: Path, filename: str, content_hash: str) -> Any:
    """The synthetic curation record, pointed at a file, written into `curation_dir` and loaded.

    Never a real record and never the real export directory: `curation_synthetic_loadable.json`
    carries a deliberately non-PXD accession so it can never be mistaken for one.
    """
    from bzk.curation.loader import load_path

    record = json.loads(SYNTHETIC_RECORD.read_text())
    record["file"] = filename
    record["content_hash"] = content_hash
    curation_dir.mkdir(parents=True, exist_ok=True)
    path = curation_dir / "curation_SYNTHETIC.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    return load_path(path)


#: The four columns `curation_synthetic_loadable.json` maps, so the derived family is `intensity`.
SYNTHETIC_KEYS = ("Intensity CTRL_1", "Intensity CTRL_2", "Intensity TREAT_1", "Intensity TREAT_2")


def _synthetic_protein_groups() -> bytes:
    """A one-row MaxQuant `proteinGroups.txt` over the synthetic record's four samples. CRLF as the
    deposit is."""
    header = [
        "Protein IDs",
        "Majority protein IDs",
        "Peptides",
        "Razor + unique peptides",
        "Reverse",
        "Potential contaminant",
        "id",
        *SYNTHETIC_KEYS,
    ]
    row = [MX1, MX1, "7", "5", "", "", "0", "150520", "162200", "210300", "198450"]
    return ("\r\n".join(["\t".join(header), "\t".join(row)]) + "\r\n").encode("utf-8")


def _synthetic_site_table() -> bytes:
    """A one-row MaxQuant site table over the same four samples, for the site half of T4."""
    header = (
        "Proteins\tPositions within proteins\tLeading proteins\tProtein\tPosition\t"
        "Amino acid\tLocalization prob\tScore\tReverse\tPotential contaminant\tid\t"
        + "\t".join(SYNTHETIC_KEYS)
    )
    row = f"{MX1}\t4\t{MX1}\t{MX1}\t4\tK\t0.99\t80.5\t\t\t0\t150520\t162200\t210300\t198450"
    return f"{header}\r\n{row}\r\n".encode()


def _stored(tmp_path: Path, home: Path, payload: bytes, name: str) -> tuple[Any, Path]:
    """`(LoadedCuration, path in the content store)` for synthetic bytes under an explicit `home`.

    The record lands in `tmp_path / "curation"`, so a caller that wants a whole replay can pass
    that directory straight to `replay_ingestion`.

    Built rather than committed, as `test_rebuild.py` builds its site deposit: the record's
    `content_hash` must equal the digest of the bytes, so writing the two independently would let
    them drift apart.
    """
    from bzk.provenance import raw_store

    stored = raw_store.store(payload, name, home=home)
    loaded = _record(tmp_path / "curation", name, stored.content_hash)
    return loaded, raw_store.verify(stored.content_hash, filename=name, home=home)


def test_dispatch_returns_the_site_adapter_for_a_site_table(tmp_path: Any) -> None:
    home = tmp_path / "home"
    loaded, path = _stored(tmp_path, home, _synthetic_site_table(), "SYNTHETIC_Sites.txt")

    adapter = _adapter_for(loaded, path, None)
    assert isinstance(adapter, MaxQuantSiteAdapter)


def test_dispatch_returns_the_protein_adapter_with_the_derived_quantity(tmp_path: Any) -> None:
    """The half that is now true of `_adapter_for`'s docstring: this branch's `quantity` comes from
    the record. The record maps `Intensity …` columns, so the declaration reads `intensity` — not
    `DeclaredProteinAnalysis`' `lfq` default, which is what a constant here would have recorded."""
    home = tmp_path / "home"
    loaded, path = _stored(
        tmp_path, home, _synthetic_protein_groups(), "SYNTHETIC_proteinGroups.txt"
    )

    adapter = _adapter_for(loaded, path, None)
    assert isinstance(adapter, MaxQuantProteinGroupsAdapter)
    assert adapter.declared.quantity == "intensity"


def test_dispatch_returns_none_for_a_perseus_export(tmp_path: Any) -> None:
    """`PerseusAdapter` is not in the dispatch — its constructor needs `contrasts`, which come from
    an analysis record rather than the curation record `_adapter_for` holds. So a Perseus export
    leaves this function as `None`, which the caller reports as a skipped ingestion."""
    home = tmp_path / "home"
    payload = (FIXTURES / "perseus_synthetic_over_protein_groups.txt").read_bytes()
    loaded, path = _stored(tmp_path, home, payload, "SYNTHETIC_perseus.txt")

    assert _adapter_for(loaded, path, None) is None


def test_replay_over_a_protein_groups_deposit_counts_protein_observations(tmp_path: Any) -> None:
    """The crash this turn removes. `replay_ingestion` read `report.sites_emitted` unconditionally,
    and `ProteinIngestReport` carries `groups_emitted` instead — so the first protein-grain deposit
    to reach the replay raised `AttributeError` after the change-set had already been written.

    The counts are kept apart rather than summed: `site_observations` means what it always did, and
    a protein-groups deposit adds nothing to it.
    """
    home = tmp_path / "home"
    loaded, path = _stored(
        tmp_path, home, _synthetic_protein_groups(), "SYNTHETIC_proteinGroups.txt"
    )
    conn = create_graph(home)

    report = replay_ingestion(conn, tmp_path / "curation", home=home)

    # The adapter's own figure, parsed separately rather than restated as a literal: the claim is
    # that the replay reports *what the adapter emitted*, and a hard-coded 1 on both sides would be
    # `test_rebuild`'s old defect — an assertion checking a number against itself.
    adapter = _adapter_for(loaded, path, None)
    assert adapter is not None
    adapter.parse(path, loaded.sample_mapping())
    assert report.protein_observations == adapter.report.groups_emitted
    assert report.deposits_ingested == 1
    assert report.site_observations == 0
    # And they reached the graph, not only the report. Against the literal one row
    # `_synthetic_protein_groups` writes rather than against `groups_emitted` again: the previous
    # line already ties the report to the adapter, so repeating that term here would check the
    # graph against nothing.
    assert store.count_nodes(conn)["ProteinObservation"] == 1


def test_replay_ingestion_still_records_the_seventy_eight_second_hazard() -> None:
    """`home` has no default for a measured reason, and the reason is the docstring's to keep.
    Pinned because this file's whole offline claim rests on every caller passing `home` — and the
    one revision where a default existed cost 78 seconds a run and counts that depended on whether
    the developer had fetched the deposit."""
    assert replay_ingestion.__doc__ is not None
    assert "78 seconds" in replay_ingestion.__doc__
