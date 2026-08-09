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

**`Gene` and `ENCODES` are minted here, 2026-08-09.** They come off the same `Resolution` this
module already consumes, and `ARCHITECTURE.md` §2 declares this module *accession → `Protein` +
`ProteinSequence`*, so a third reference node UniProt asserts about an accession belongs on the
same seam. `bzk/ontology/seed.py` is explicitly **not** the precedent: `Modifier` lives in version
control because which modifiers a K-GG remnant cannot distinguish is a fact *the project asserts*
(ADR-0021), and that is what keeps I9 true for it. `Gene` is fetched, so its I9 input is the
UniProt cache — already the fourth input since 2026-08-07. **I9's input list does not change**, and
that is the test this placement had to pass: a `Gene` built from anything else would have added one.

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
from bzk.ontology.keys import check_curie_case, protein_key, protein_sequence_key
from bzk.resolve.uniprot import AMBIGUOUS, DEFAULT_CACHE_DIR, NOT_CAPTURED, Resolution, resolve

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
    #: accession → why it got no `Gene`, from `schema.GENE_ABSENCE`. An accession is in exactly one
    #: of this and `gene_id`; §4 tabulates the three values and why the distinction is load-bearing.
    gene_absence: dict[str, str] = field(default_factory=dict)
    #: accession → `Gene.id`, for callers that need the gene without walking `ENCODES`.
    gene_id: dict[str, str] = field(default_factory=dict)

    def candidate_nodes(self, accessions: Iterable[str]) -> list[Node]:
        """`Protein` nodes for candidate accessions this resolution did not cover.

        An adapter names far more accessions in a protein group than it resolves — only the razor
        picks need a sequence version — and mints an accession-only `Protein` for the rest. Those
        proteins were **never resolved against UniProt**, so their `gene_absence` is `unresolved`,
        and that is a fact about the adapter's resolution policy rather than about the protein
        (§4).

        **It lives here and not in the adapters because the store's write path is `MERGE … SET`,
        so a `Protein` staged twice is last-write-wins.** Minting an accession-only node for an
        accession that *was* resolved would overwrite its `gene_absence` with `unresolved`,
        depending on staging order — which is how the first build of `Gene` put 3,492 proteins in
        the graph with a NULL `gene_absence` and no `ENCODES` edge, the exact collapse §4's column
        exists to prevent. Excluding the resolved set is order-independent; ordering the writes
        would not have been.
        """
        return [
            {
                NODE_TYPE_KEY: "Protein",
                "id": protein_key(accession),
                "accession": accession,
                "gene_absence": "unresolved",
            }
            for accession in dict.fromkeys(accessions)
            if accession and accession not in self.protein_id
        ]

    def __post_init__(self) -> None:
        assert set(self.sequence_id).isdisjoint(self.unresolved), (
            "an accession is both resolved and unresolved"
        )
        assert set(self.gene_id).isdisjoint(self.gene_absence), (
            "an accession both has a Gene and carries a reason it has none"
        )
        assert set(self.gene_id) | set(self.gene_absence) == set(self.protein_id), (
            "every Protein must be in exactly one of gene_id and gene_absence — an absent ENCODES "
            "edge with no recorded reason is the collapse §4's gene_absence exists to prevent"
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
    gene_absence: dict[str, str] = {}
    gene_id: dict[str, str] = {}
    genes: dict[str, Node] = {}

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
        # redundant — two homes for one fact — so the symbol's route is `Gene`.
        #
        # **`Gene` was minted 2026-08-09 (§11 Q12, closed).** The symbol reaches the graph through
        # `Gene.symbol` below, so `Protein.name` still stays null — a routing decision, not an
        # absence. `organism_taxid` genuinely is unreported by the resolver.
        why = _gene_absence(result)
        if why is None:
            # `Gene.id` is authority-assigned: HGNC's own identifier, CURIE-prefixed, and §4 fixes
            # the local part at the authority's rendering — `hgnc:HGNC:7532`, never `hgnc:7532`.
            # Routed through `check_curie_case` so a malformed capture is refused here rather than
            # becoming a second node for one gene.
            gid = check_curie_case(f"hgnc:{result.hgnc_id}")
            gene_id[accession] = gid
            # One node per gene however many proteins reach it — `ENCODES` is ONE_MANY. Measured
            # on PXD018299 the maximum is 2 proteins on one gene, because only razor picks are
            # resolved; a cache-wide projection put it at 34, which is what the graph would show
            # if the adapter resolved every candidate.
            genes.setdefault(
                gid, {NODE_TYPE_KEY: "Gene", "id": gid, "symbol": result.gene, "name": None}
            )
            edges.append({"type": "ENCODES", "from": gid, "to": pid})
        else:
            gene_absence[accession] = why
        nodes.append(
            {
                NODE_TYPE_KEY: "Protein",
                "id": pid,
                "accession": accession,
                "gene_absence": why,
            }
        )

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

    # Appended last so a `Gene` is staged after every `Protein` it encodes. Order is not required
    # by the store — ADR-0019 makes a change-set self-contained — but a reader of the staged list
    # should not have to hold an edge whose endpoints appear later.
    nodes.extend(genes[gid] for gid in sorted(genes))
    return ResolvedProteins(
        nodes=nodes,
        edges=edges,
        protein_id=protein_id,
        sequence_id=sequence_id,
        unresolved=unresolved,
        gene_absence=gene_absence,
        gene_id=gene_id,
    )


def _gene_absence(result: Resolution) -> str | None:
    """Which of §4's three `gene_absence` values applies, or `None` when a `Gene` can be minted.

    Every branch returns a value from `schema.GENE_ABSENCE`; there is no fall-through, because a
    fall-through would be a fourth absence with no name, which is the state this column exists to
    make impossible. `AMBIGUOUS` folds into `no_cross_reference`: UniProt reported several HGNC
    ids and the platform will not pick one (`uniprot.AMBIGUOUS`), so from the graph's side there is
    no usable cross-reference — and the reason is recorded at the sentinel rather than lost, since
    a fourth enum value for a state measured 0 of 198 times would be a column nothing populates.
    """
    if result.status != "ok":
        return "unresolved"
    if result.hgnc_id == NOT_CAPTURED:
        return "not_captured"
    if result.hgnc_id in (None, AMBIGUOUS):
        return "no_cross_reference"
    return None


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
