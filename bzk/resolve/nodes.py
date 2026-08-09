"""Accessions → the reference nodes a change-set needs (ADR-0005, `ONTOLOGY.md` §4).

This is the seam between the resolver and the graph, and it exists because **ADR-0005 splits one
accession into two nodes**. A protein's identity outlives any one version of its sequence, but a
*position* is meaningless without a specific sequence — so `Protein` is stable and
`ProteinSequence` is version-specific, and a `ModificationSite` keys against the second. An adapter
that wants to emit a site therefore needs `uniprot:P20591#sv4`, which it cannot construct without
asking UniProt what the current version is. Doing that lookup in one place, here, keeps it out of
every adapter.

**Injected, not called directly.** `resolve` is a parameter with a default, so an adapter takes it
on its constructor and `parse(file, mapping)` keeps the signature `ARCHITECTURE.md` §3 fixes. Tests
pass a stub and never touch the network; the two rejected alternatives were threading a session
through `parse` (which breaks the protocol) and resolving *after* the adapter (which leaves the
adapter unable to key a `ModificationSite`, so it could not emit a valid change-set at all).

**Failure is reported, not raised.** At the PXD018299 site table's 4,815 distinct accessions a dead
or renamed one is expected, and sinking a whole batch for it would be wrong. What to do about an
unresolved accession is the *adapter's* decision — it knows whether that accession was the only
candidate for a site or one of nine — so this returns them in `unresolved` and lets the caller
refuse. Nothing partial is emitted for them: an accession without a sequence version produces no
`ProteinSequence`, because I2 would reject the site keyed against it anyway.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path

from bzk.adapters.base import Edge, Node
from bzk.ontology.invariants import NODE_TYPE_KEY
from bzk.ontology.keys import protein_key, protein_sequence_key
from bzk.resolve.uniprot import DEFAULT_CACHE_DIR, Resolution, resolve

#: What an adapter injects. Narrower than `uniprot.resolve` on purpose — an adapter has no business
#: passing `refresh` or a session, and a stub in a test should not have to accept them.
Resolver = Callable[[str], Resolution]


@dataclass(frozen=True)
class ResolvedProteins:
    """The reference half of a change-set, plus the lookups an adapter keys sites with."""

    nodes: list[Node]
    edges: list[Edge]
    #: accession → `Protein.id`, for `RESOLVES_TO_PROTEIN` and `candidate_proteins`.
    protein_id: dict[str, str]
    #: accession → `ProteinSequence.id`, which is what a `ModificationSite` keys against (§4).
    #: An accession missing here has no usable sequence version; see `unresolved`.
    sequence_id: dict[str, str] = field(default_factory=dict)
    #: accession → why it produced no `ProteinSequence`. The caller decides what that means.
    unresolved: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        assert set(self.sequence_id).isdisjoint(self.unresolved), (
            "an accession is both resolved and unresolved"
        )


def default_resolver(cache_dir: Path = DEFAULT_CACHE_DIR) -> Resolver:
    """The real thing, bound to the two-tier cache. Reaches the network on a cache miss."""

    def _resolve(accession: str) -> Resolution:
        return resolve(accession, cache_dir=cache_dir)

    return _resolve


def resolve_to_nodes(
    accessions: Iterable[str], *, resolver: Resolver | None = None
) -> ResolvedProteins:
    """Resolve each accession once and project it onto `Protein` + `ProteinSequence` + `HAS_SEQUENCE`.

    Accessions are de-duplicated before resolving, so a site table naming one protein 400 times
    costs one lookup. Ids are content-derived (I7), so re-staging the same reference node in another
    change-set converges rather than colliding (`bzk/ontology/store.py`).
    """
    resolve_one = resolver if resolver is not None else default_resolver()
    nodes: list[Node] = []
    edges: list[Edge] = []
    protein_id: dict[str, str] = {}
    sequence_id: dict[str, str] = {}
    unresolved: dict[str, str] = {}

    for accession in sorted(set(accessions)):
        if not accession:
            continue
        result = resolve_one(accession)
        pid = protein_key(accession)
        protein_id[accession] = pid
        # `Protein` carries only its accession. **Withdrawn and replaced 2026-08-08 — the old
        # comment read "the resolver reports neither, and filling them from `gene` or an assumption
        # would be inventing", and its premise was half false.** The resolver does report one of
        # them: `Resolution.gene` exists (`uniprot.py`) and is populated on every `ok` path — 2,128
        # of 2,261 cached entries carry it. What was right is the conclusion for `name`, and for a
        # reason the comment did not give: `Resolution.gene` is a **gene symbol**, and `Protein.name`
        # holds UniProt's *protein* name (§4). Writing the symbol here would make `Gene.symbol`
        # redundant — two homes for one fact — so the symbol's route is `Gene`, which cannot be
        # minted because `Gene.id` is an `hgnc:` CURIE and the entry cache stores the parse rather
        # than the payload that carries the id (§11 Q12). `organism_taxid` genuinely is unreported.
        # So both columns stay null, and this is now a routing decision rather than an absence.
        nodes.append({NODE_TYPE_KEY: "Protein", "id": pid, "accession": accession})

        if result.status != "ok":
            unresolved[accession] = f"resolver status {result.status!r}"
            continue
        if result.sequence_version is None:
            # I2: a site on a sequence with no version has meaningless residue numbering.
            unresolved[accession] = "no sequence_version, so no ProteinSequence can be keyed (I2)"
            continue
        if result.sequence is None:
            # The resolver's own invariant: an isoform whose sequence could not be fetched returns
            # None rather than the canonical sequence standing in for it. Honour that here — a
            # ProteinSequence node without its sequence cannot validate a residue.
            unresolved[accession] = f"no sequence ({result.sequence_source})"
            continue

        sid = protein_sequence_key(pid, result.sequence_version)
        sequence_id[accession] = sid
        nodes.append(
            {
                NODE_TYPE_KEY: "ProteinSequence",
                "id": sid,
                "sequence_version": result.sequence_version,
                "sequence": result.sequence,
            }
        )
        edges.append({"type": "HAS_SEQUENCE", "from": pid, "to": sid})

    return ResolvedProteins(
        nodes=nodes,
        edges=edges,
        protein_id=protein_id,
        sequence_id=sequence_id,
        unresolved=unresolved,
    )


def residue_at(resolved: ResolvedProteins, accession: str, position: int) -> str | None:
    """The residue a site would sit on, or `None` if it cannot be checked.

    Position is 1-based, as UniProt and MaxQuant both report it. Returns `None` rather than raising
    for an out-of-range position: that is a *finding* about the data — the sequence has been amended
    since the search — and the adapter reports how many, which is the measurement `ROADMAP.md`
    § Measured findings sizes at ~114 of 2,298 sites at risk.
    """
    sid = resolved.sequence_id.get(accession)
    if sid is None:
        return None
    sequence = next(
        (n["sequence"] for n in resolved.nodes if n["id"] == sid and "sequence" in n), None
    )
    if not isinstance(sequence, str) or not 1 <= position <= len(sequence):
        return None
    return sequence[position - 1]
