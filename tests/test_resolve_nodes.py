"""`bzk/resolve/nodes.py` — the ADR-0005 two-node projection (Slice 1).

Entirely offline: every test injects a resolver, which is the point of the seam. The real
`uniprot.resolve` is already covered by `tests/test_resolve.py` and `tests/test_resolve_pxd018299.py`
(20/20 against recorded responses); what is new here is the projection from a `Resolution` onto
`Protein` + `ProteinSequence` + `HAS_SEQUENCE`, and that is a pure function of a `Resolution`.

The unresolved cases are tested against **constructed** `Resolution`s rather than against whichever
accession happens to be dead in UniProt today — `HANDOFF.md` §8's rule, since an error path pinned
to live external state stops testing the day that state changes.
"""

from __future__ import annotations

from bzk.ontology import invariants
from bzk.ontology.invariants import NODE_TYPE_KEY
from bzk.resolve.nodes import Resolver, residue_at, resolve_to_nodes
from bzk.resolve.uniprot import Resolution

# Real accessions, and the two the repository already uses elsewhere.
MX1 = "P20591"
IFIT1_2 = "P09914-2"


def _ok(accession: str, *, sv: int, sequence: str, isoform: bool = False) -> Resolution:
    return Resolution(
        status="ok",
        requested=accession,
        canonical=accession.split("-")[0],
        isoform=accession.split("-")[1] if isoform else None,
        is_isoform=isoform,
        reviewed=True,
        entry_type="UniProtKB reviewed (Swiss-Prot)",
        sequence=sequence,
        sequence_version=sv,
        last_seq_update="2019-12-11",
        gene="MX1",
        sequence_source="isoform" if isoform else "canonical",
    )


def _resolver(**by_accession: Resolution) -> Resolver:
    table = {k.replace("__", "-"): v for k, v in by_accession.items()}

    def _resolve(accession: str) -> Resolution:
        return table[accession]

    return _resolve


def test_one_accession_becomes_two_nodes_and_an_edge() -> None:
    """ADR-0005: stable identity and version-specific sequence are different nodes."""
    resolved = resolve_to_nodes([MX1], resolver=_resolver(P20591=_ok(MX1, sv=4, sequence="MVVSEK")))
    labels = [n[NODE_TYPE_KEY] for n in resolved.nodes]
    assert labels == ["Protein", "ProteinSequence"]
    assert resolved.protein_id[MX1] == "uniprot:P20591"
    assert resolved.sequence_id[MX1] == "uniprot:P20591#sv4"
    assert resolved.edges == [
        {"type": "HAS_SEQUENCE", "from": "uniprot:P20591", "to": "uniprot:P20591#sv4"}
    ]


def test_the_projection_is_a_valid_change_set_fragment() -> None:
    """What it emits must pass ADR-0019 on its own, since an adapter will merge it into a batch."""
    resolved = resolve_to_nodes(
        [MX1, IFIT1_2],
        resolver=_resolver(
            P20591=_ok(MX1, sv=4, sequence="MVVSEK"),
            P09914__2=_ok(IFIT1_2, sv=2, sequence="MPDLEK", isoform=True),
        ),
    )
    invariants.validate(resolved.nodes, resolved.edges)


def test_an_isoform_keeps_its_full_accession() -> None:
    """`HANDOFF.md` §6: stripping `-2` fetches a different protein of different length, and the
    position then resolves to the wrong residue without erroring. 30% of razor picks are isoforms."""
    resolved = resolve_to_nodes(
        [IFIT1_2], resolver=_resolver(P09914__2=_ok(IFIT1_2, sv=2, sequence="MPDLEK", isoform=True))
    )
    assert resolved.protein_id[IFIT1_2] == "uniprot:P09914-2"
    assert resolved.sequence_id[IFIT1_2] == "uniprot:P09914-2#sv2"


def test_accessions_are_resolved_once_each() -> None:
    """A site table names one protein hundreds of times; a lookup per row would be absurd."""
    calls: list[str] = []

    def counting(accession: str) -> Resolution:
        calls.append(accession)
        return _ok(MX1, sv=4, sequence="MVVSEK")

    resolved = resolve_to_nodes([MX1] * 400, resolver=counting)
    assert calls == [MX1]
    assert len(resolved.nodes) == 2


def test_protein_carries_only_what_the_resolver_reports() -> None:
    """`name` and `organism_taxid` are real columns the `Resolution` does not supply.

    Filling them from `gene`, or from an assumption that everything here is human, would be
    inventing — and `Protein.accession` is the only identifying one anyway (§3).
    """
    resolved = resolve_to_nodes([MX1], resolver=_resolver(P20591=_ok(MX1, sv=4, sequence="MVVSEK")))
    protein = resolved.nodes[0]
    assert set(protein) == {NODE_TYPE_KEY, "id", "accession"}


# ── Unresolved: reported, never partially emitted ───────────────────────────────────────────────


def test_a_dead_accession_yields_a_protein_but_no_sequence() -> None:
    """The `Protein` is still real — the accession was observed — but nothing can key a site on it."""
    dead = Resolution(
        status="not_found",
        requested="Q00000",
        canonical="Q00000",
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
    resolved = resolve_to_nodes(["Q00000"], resolver=_resolver(Q00000=dead))
    assert [n[NODE_TYPE_KEY] for n in resolved.nodes] == ["Protein"]
    assert resolved.sequence_id == {}
    assert "not_found" in resolved.unresolved["Q00000"]
    assert resolved.edges == []


def test_an_isoform_whose_sequence_is_unavailable_is_unresolved_not_substituted() -> None:
    """The resolver's own invariant, honoured here: never the canonical sequence standing in.

    This is the isoform-stripping failure of `HANDOFF.md` §6 in its second form — the sequence would
    validate as a lysine and be silently the wrong protein's.
    """
    unavailable = Resolution(
        status="ok",
        requested=IFIT1_2,
        canonical="P09914",
        isoform="2",
        is_isoform=True,
        reviewed=True,
        entry_type="UniProtKB reviewed (Swiss-Prot)",
        sequence=None,
        sequence_version=2,
        last_seq_update=None,
        gene="IFIT1",
        sequence_source="isoform_fetch_failed",
    )
    resolved = resolve_to_nodes([IFIT1_2], resolver=_resolver(P09914__2=unavailable))
    assert resolved.sequence_id == {}
    assert "isoform_fetch_failed" in resolved.unresolved[IFIT1_2]


def test_resolved_and_unresolved_are_disjoint() -> None:
    """Asserted in `__post_init__`, so a future edit cannot report an accession as both."""
    resolved = resolve_to_nodes([MX1], resolver=_resolver(P20591=_ok(MX1, sv=4, sequence="MVVSEK")))
    assert set(resolved.sequence_id).isdisjoint(resolved.unresolved)


# ── residue_at: the hook Slice 2's measurement needs ────────────────────────────────────────────


def test_residue_at_reads_the_pinned_sequence() -> None:
    """1-based, as UniProt and MaxQuant both report. K at 6 of MVVSEK."""
    resolved = resolve_to_nodes([MX1], resolver=_resolver(P20591=_ok(MX1, sv=4, sequence="MVVSEK")))
    assert residue_at(resolved, MX1, 6) == "K"
    assert residue_at(resolved, MX1, 1) == "M"


def test_residue_at_returns_none_past_the_end_rather_than_raising() -> None:
    """A position beyond the sequence is a *finding* — the sequence was amended since the search —
    and the adapter counts them. ROADMAP sizes it at ~114 of 2,298 sites at risk."""
    resolved = resolve_to_nodes([MX1], resolver=_resolver(P20591=_ok(MX1, sv=4, sequence="MVVSEK")))
    assert residue_at(resolved, MX1, 99) is None
    assert residue_at(resolved, MX1, 0) is None


def test_residue_at_returns_none_for_an_unresolved_accession() -> None:
    dead = Resolution(
        status="http_500",
        requested="Q00000",
        canonical="Q00000",
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
    resolved = resolve_to_nodes(["Q00000"], resolver=_resolver(Q00000=dead))
    assert residue_at(resolved, "Q00000", 1) is None
