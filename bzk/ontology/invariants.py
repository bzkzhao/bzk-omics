"""Write-time invariant enforcement over a staged change-set.

The invariants of ONTOLOGY.md §8 are errors, not warnings (CLAUDE.md): a violation raises
`InvariantError`, which ingestion must let propagate rather than downgrade.

**Enforced here** (write-time, over the staged change-set):
  I2, I3, I4, I10, I14, I15, I16, I19, I20, I21 — one checker each — plus **change-set structural
  validation** (ADR-0019): every referent an edge names is present, every edge endpoint carries
  the node label `schema.py` declares for that relationship, every edge type is a relationship in
  the DDL, every relationship's multiplicity is respected (a MANY_ONE source or a ONE_MANY
  destination appears at most once in the change-set), and every node has a unique id and declares
  a node type the DDL knows. Structural
  failures raise ``STRUCTURE``, except a
  missing or mislabelled endpoint on a relationship a specific invariant owns (SITE_ON→I2,
  ASSIGNS→I3, ASSOCIATION_FOR→I10, ASSIGNS_PROTEIN→I14), which raises that invariant. Structural
  validation runs first and unconditionally, so the checks below never read a field off an absent
  or wrong-typed referent.

**Not enforced here** — where each lives, by class (CS = write-time change-set · WG = whole-graph
/query-time · EX = export boundary · LINT = source-tree lint, not a data check · CON = enforced by
construction · write-path · data = storage layer). Tracked in HANDOFF.md §8:
  - I1  (CS)         disjointness — not written
  - I5  (WG)         provenance reachability — flagged `unprovenanced` at query time (§7)
  - I6  (write-path) append-only assertions — reject in-place edits; retraction propagation (v0.2)
  - I7  (CON)        deterministic reference keys — holds once the key builder exists
  - I8  (CS + WG)    curated design — Sample→curation reachability + `inferred` labelling
  - I9  (OP)         reproducible rebuild — exercised by `rebuild.py`; non-vacuous since
                     2026-08-07, when the curation replay began writing real content
  - I11 (data)       quantitative retention — met 2026-08-08 by `bzk/quant/` for
                     `SiteObservation` ONLY (ADR-0004, ADR-0013). `ProteinObservation`
                     has a table and a `quant_ref` path and no adapter that writes
                     either: `maxquant_sites.py` is the sole `quant_ref` assignment in
                     `bzk/adapters/`, and `perseus.py` emits no cells at all. Not a
                     change-set check: a change-set is graph content by definition (§2),
                     and these values are one-per-entity-per-sample, so nothing here
                     can see them
  - I12 (LINT)       no tryptic assumptions — a source-tree lint, not a change-set check
  - I13 (LINT)       pipeline metadata is data — a source-tree lint, not a change-set check
  - I17 (CON)        reviewed preferred — recorded by the adapter / ProteinAssignment construction
  - I18 (EX)         embargo — the export-boundary check; must land with the first export path

A change-set is plain data, independent of Kùzu storage: a node is
``{NODE_TYPE_KEY, "id", **props}`` and an edge is ``{"type", "from", "to"}``. Relationship and label
expectations are derived from `schema.py` (the mirror of ONTOLOGY.md §4-7), never restated here —
domain logic stays out of code that consumes the contract (ONTOLOGY.md §10).

**The node-type key is ``__label__``, not ``label``** (ADR-0019, renamed 2026-08-07). ``label`` is a
real DDL column on six node tables — `Sample`, `Dataset`, `Analysis`, `Contrast`, `Disease`, `Drug`
— so while the discriminator owned that name those six columns could not be written through this
contract at all: ``{**props}`` would have overwritten the node type. Every column in §4-§7 matches
``[a-z][a-z0-9_]*``, so a dunder key cannot collide with one now or later.
"""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Callable, Iterable
from typing import Any

from bzk.ontology import keys, schema
from bzk.ontology.schema import (
    CONFIDENCE,
    PROTEIN_ADJUSTED,
    QUANTITY_VALUES,
    STOCHASTIC_IMPUTATION,
)

Node = dict[str, Any]
Edge = dict[str, Any]

# The node-type discriminator. Read it from here rather than writing the literal, so the next
# rename is one edit — the reason the last one was mechanical is that there were no adapters yet.
NODE_TYPE_KEY = "__label__"

# ── The reserved namespace (ADR-0019) ────────────────────────────────────────────────────────────
#
# A change-set dict mixes *structural* keys with *stored* ones. The distinction is what the `label`
# collision came down to, so it is declared rather than left implicit, and the two kinds are
# guarded in opposite directions by `tests/test_invariants.py`:
#
#   - **Reserved** keys carry information the DDL does not store under that name — a node's type is
#     the table it lives in, an edge's type is the relationship. They must therefore collide with
#     NO column or property, or a real field becomes unwritable. `label` was reserved while also
#     being a column on six node tables, so those six columns could not be written at all.
#   - **Column-backed** keys name a real column and mean exactly it. `id` is the only one. It must
#     therefore be present on EVERY node table, or structural validation reads a field the store
#     does not have.
#
# The rule is the general form of the 2026-08-07 rename, and the guard is what makes it hold for
# the next field rather than the last one.
RESERVED_NODE_KEYS: frozenset[str] = frozenset({NODE_TYPE_KEY})
RESERVED_EDGE_KEYS: frozenset[str] = frozenset({"type", "from", "to"})
COLUMN_BACKED_NODE_KEYS: frozenset[str] = frozenset({"id"})

# Endpoint labels, valid relationship names, and multiplicity per relationship — derived from the
# schema, so this module mirrors ONTOLOGY.md rather than becoming a second source of truth.
# Every declared (source, destination) pair per relationship. A relationship may have more
# than one (ADR-0022: PROTEIN_ASSIGNMENT_FOR reaches both observation grains), so an edge is
# well-formed when its endpoints match ANY declared pair.
_REL_ENDPOINTS: dict[str, tuple[tuple[str, str], ...]] = {
    t.name: t.pairs for t in schema.REL_TABLES
}
_REL_MULT: dict[str, str | None] = {t.name: t.multiplicity for t in schema.REL_TABLES}
_NODE_LABELS: frozenset[str] = frozenset(t.name for t in schema.NODE_TABLES)

# Relationships a write-time invariant consults; a structural failure on one is that invariant's.
_REL_INVARIANT: dict[str, str] = {
    "SITE_ON": "I2",
    "ASSIGNS": "I3",
    "ASSOCIATION_FOR": "I10",
    "ASSIGNS_PROTEIN": "I14",
}


class InvariantError(Exception):
    """A staged change violates an ONTOLOGY.md §8 invariant (or ADR-0019 structure). Carries the id."""

    def __init__(self, invariant: str, message: str) -> None:
        super().__init__(f"{invariant} — {message}")
        self.invariant = invariant


def _nodes(nodes: Iterable[Node], label: str) -> list[Node]:
    return [n for n in nodes if n.get(NODE_TYPE_KEY) == label]


def _edges(edges: Iterable[Edge], rel: str) -> list[Edge]:
    return [e for e in edges if e.get("type") == rel]


def _index(nodes: Iterable[Node], label: str) -> dict[Any, Node]:
    """`{id: node}` for one label.

    Label-scoped, not global. Two node tables may share an id — §3 keys both `Protein` and
    `Modifier` on `uniprot:`, so ISG15 is `uniprot:P05161` under both (ADR-0019, corrected
    2026-08-07) — and a global index would return whichever came last. The failure that causes is
    silent rather than loud: I2's `HAS_SEQUENCE` clause reads `.get("accession")` off the node it
    finds, and a `Modifier` has no `accession`, so the check would skip instead of raising. Every
    caller here knows the label from the relationship it is walking, so scoping costs nothing.
    """
    return {n["id"]: n for n in nodes if "id" in n and n.get(NODE_TYPE_KEY) == label}


def _validate_structure(nodes: list[Node], edges: list[Edge]) -> None:
    """ADR-0019 — a change-set must be self-contained and well-formed before any invariant is
    meaningful. Expectations come from `schema.py`, so this checks against ONTOLOGY.md's DDL."""
    seen: set[Any] = set()
    for node in nodes:
        node_id = node.get("id")
        if node_id is None:
            raise InvariantError(
                "STRUCTURE", f"node labelled {node.get(NODE_TYPE_KEY)!r} has no id"
            )
        # Keyed on (label, id), not id alone. Two node *tables* may legitimately share an id, and
        # the case is not exotic: `Modifier` and `Protein` both key on `uniprot:` (§3), so ISG15 is
        # `uniprot:P05161` under both — the protein that a diGly search reports as a razor pick, and
        # the modifier a K-GG remnant might have come from. That is the anchor domain of this
        # project, not an edge case, and it surfaced the first time a real file was ingested with
        # the modifier seed in the same change-set. Kùzu stores them in separate tables and is
        # untroubled; it was this format that was too narrow.
        if (node.get(NODE_TYPE_KEY), node_id) in seen:
            raise InvariantError(
                "STRUCTURE",
                f"duplicate node id {node_id!r} for label {node.get(NODE_TYPE_KEY)!r} in the "
                "change-set",
            )
        seen.add((node.get(NODE_TYPE_KEY), node_id))
        # Every node declares a node type the DDL knows. Until 2026-08-07 a node type was only ever
        # checked where an *edge* pointed at it, so a node no edge referenced could carry a typo'd
        # type or none at all and pass. The discriminator rename in the same ADR is what exposed
        # it: a producer still emitting the old `label` key yields nodes with no type, and the one
        # thing that must not do is validate. Checked after `id` so an id-less node still reports
        # as one.
        node_type = node.get(NODE_TYPE_KEY)
        if node_type not in _NODE_LABELS:
            raise InvariantError(
                "STRUCTURE",
                f"node {node_id!r} declares {NODE_TYPE_KEY}={node_type!r}, which is not a node "
                f"table in the schema. A node's type is carried by {NODE_TYPE_KEY!r}, not 'label' "
                "— 'label' is a DDL column on six node tables (ADR-0019, 2026-08-07).",
            )

    # id -> every label carrying it. An edge names its endpoints by bare id, so where two labels
    # share one the edge would be ambiguous — except that the *relationship* declares its endpoint
    # types, which disambiguates it: `HAS_SEQUENCE(FROM Protein TO ProteinSequence)` reaching
    # `uniprot:P05161` can only mean the `Protein`. So an endpoint is well-formed when SOME node
    # with that id carries a declared label, rather than when THE node with that id does.
    labels_by_id: dict[Any, set[str]] = defaultdict(set)
    for node in nodes:
        if "id" in node:
            labels_by_id[node["id"]].add(str(node.get(NODE_TYPE_KEY)))
    # MANY_ONE / ONE_ONE constrain the source side; ONE_MANY / ONE_ONE the destination side.
    seen_from: dict[str, set[Any]] = defaultdict(set)
    seen_to: dict[str, set[Any]] = defaultdict(set)
    for edge in edges:
        rel = edge.get("type")
        if rel not in _REL_ENDPOINTS:
            raise InvariantError(
                "STRUCTURE", f"edge type {rel!r} is not a relationship in the schema"
            )
        owner = _REL_INVARIANT.get(rel, "STRUCTURE")
        present = []
        for role in ("from", "to"):
            found = labels_by_id.get(edge.get(role))
            if not found:
                raise InvariantError(
                    owner, f"{rel} names {role} {edge.get(role)!r}, absent from the change-set"
                )
            present.append(found)
        if not any(src in present[0] and dst in present[1] for src, dst in _REL_ENDPOINTS[rel]):
            declared = " or ".join(f"{s} → {d}" for s, d in _REL_ENDPOINTS[rel])
            raise InvariantError(
                owner,
                f"{rel} runs {sorted(present[0])} → {sorted(present[1])} between "
                f"{edge.get('from')!r} and {edge.get('to')!r}; the schema declares {declared}",
            )

        # Multiplicity, from the same source as the endpoints (schema.RelTable.multiplicity).
        mult = _REL_MULT.get(rel)
        src, dst = edge.get("from"), edge.get("to")
        if mult in ("MANY_ONE", "ONE_ONE"):
            if src in seen_from[rel]:
                raise InvariantError(
                    "STRUCTURE", f"{rel} is {mult}: source {src!r} has more than one {rel} edge"
                )
            seen_from[rel].add(src)
        if mult in ("ONE_MANY", "ONE_ONE"):
            if dst in seen_to[rel]:
                raise InvariantError(
                    "STRUCTURE",
                    f"{rel} is {mult}: destination {dst!r} has more than one {rel} edge",
                )
            seen_to[rel].add(dst)


# ── One checker per invariant. Structural validation has already guaranteed that every edge
#    endpoint below is present and correctly labelled, so no referent-absence guard is needed. ──


def _check_confidence(nodes: list[Node], label: str, invariant: str) -> None:
    """Every EvidencedInference subtype draws `confidence` from the closed §6 enum.

    Attributed to the invariant that consults the field for that subtype, per ADR-0019's
    convention. Note this is the §6 vocabulary only: `Analysis.confidence` is curation's
    'authoritative' | 'inferred', a different set, and is deliberately not checked here.
    """
    for node in _nodes(nodes, label):
        value = node.get("confidence")
        if value is not None and value not in CONFIDENCE:
            raise InvariantError(
                invariant,
                f"{label} {node.get('id')} has confidence={value!r}, which is not in the closed "
                f"enum (ONTOLOGY.md §6): {sorted(CONFIDENCE)}.",
            )


def _check_I2(nodes: list[Node], edges: list[Edge]) -> None:
    """I2 — sequence pinning, in four clauses (ADR-0005; `HANDOFF.md` §8's three, plus the first).

    The first clause has always been here. The other three landed with the first search-output
    adapter, which is the trigger §8 recorded for them, and each closes a way for a position to
    assert against one sequence while attaching to another:

      2. the `sv` segment of the site key must equal the target's `sequence_version` — otherwise the
         key says sv3 and the graph says sv4;
      3. the residue at the site's position must be the residue the site claims, where the sequence
         is in the change-set — the write-time mirror of the adapter's own check, and the backstop
         for any future producer that skips it;
      4. a `ProteinSequence`'s id must agree with its own `sequence_version` and with the accession
         of the `Protein` it hangs from — a key and a column are two homes for one fact.

    Clause 3 is skipped where the change-set carries no `sequence`, which is legal: a site may be
    re-staged against a `ProteinSequence` already in the graph. It is a backstop, not the first line.
    """
    sites = _index(nodes, "ModificationSite")
    sequences = _index(nodes, "ProteinSequence")
    for edge in _edges(edges, "SITE_ON"):  # ModificationSite -> ProteinSequence
        site, protein_sequence = sites[edge["from"]], sequences[edge["to"]]
        version = protein_sequence.get("sequence_version")
        if version is None:
            raise InvariantError(
                "I2",
                f"ModificationSite {edge['from']} sits on ProteinSequence {edge['to']} "
                "which has no sequence_version; residue numbering is meaningless.",
            )
        keyed = _sv_segment(str(site.get("id", "")))
        if keyed is not None and keyed != int(version):
            raise InvariantError(
                "I2",
                f"ModificationSite {site.get('id')} is keyed against sv{keyed} but its SITE_ON "
                f"target {edge['to']} declares sequence_version {version}; the position would "
                "assert against one sequence while attaching to another.",
            )
        sequence = protein_sequence.get("sequence")
        position, residue = site.get("position"), site.get("residue")
        if isinstance(sequence, str) and isinstance(position, int) and isinstance(residue, str):
            actual = sequence[position - 1] if 1 <= position <= len(sequence) else None
            if actual != residue.upper():
                raise InvariantError(
                    "I2",
                    f"ModificationSite {site.get('id')} claims {residue!r} at position {position} "
                    f"but {edge['to']} has {actual or 'nothing (past the end)'!r} there.",
                )

    proteins = _index(nodes, "Protein")
    accession_of = {
        e["to"]: proteins[e["from"]].get("accession") for e in _edges(edges, "HAS_SEQUENCE")
    }
    for protein_sequence in _nodes(nodes, "ProteinSequence"):
        node_id = str(protein_sequence.get("id", ""))
        version = protein_sequence.get("sequence_version")
        keyed = _sv_segment(node_id)
        if version is not None and keyed is not None and keyed != int(version):
            raise InvariantError(
                "I2",
                f"ProteinSequence {node_id} declares sequence_version {version}; its id says "
                f"sv{keyed}. A key and a column are two homes for one fact.",
            )
        accession = accession_of.get(node_id)
        if accession is not None and node_id.split("#")[0] != f"uniprot:{accession}":
            raise InvariantError(
                "I2",
                f"ProteinSequence {node_id} is reached by HAS_SEQUENCE from a Protein with "
                f"accession {accession!r}; the id names a different protein. An isoform keyed "
                "against its canonical parent is exactly the substitution ADR-0005 forbids.",
            )


def _sv_segment(node_id: str) -> int | None:
    """The `n` of an `#sv{n}` segment anywhere in an id, or `None` if it carries none.

    `None` rather than an error: not every id passed here is a keyed one, and a caller that cannot
    find a version should skip the comparison rather than invent one.
    """
    match = re.search(r"#sv(\d+)", node_id)
    return int(match.group(1)) if match else None


def _check_I3(nodes: list[Node], edges: list[Edge]) -> None:
    """I3 — no bare modifier claim, in two directions.

    **No over-claiming:** an ambiguous `ModifierAssignment` may not `ASSIGNS` a modifier. This half
    has always been here — it stops a K-GG site being named "ubiquitination" without evidence.

    **No silent under-claiming:** every `SiteObservation` must carry a `ModifierAssignment`
    (§6.1). An observation with none is not a *cautious* site, it is a site whose modifier status is
    unstated, and nothing downstream can distinguish "no assignment yet" from "assignment is
    ambiguous" — the first reads as an omission and invites someone to supply the missing default by
    assuming ubiquitin, which is the assumption the whole §6.1 apparatus exists to refuse. §6.1
    creates the `inferred_default` / `ambiguous` assignment automatically for exactly this reason;
    this makes the automatic step non-optional instead of conventional.

    **Scoped to the change-set, which has a cost worth stating.** A producer re-staging a
    `SiteObservation` — because an edge it emits names one (ADR-0019) — must re-stage that
    observation's assignment too. That is stricter than I2's residue clause, which *skips* when the
    change-set does not carry the sequence, and the two differ for a reason: a `ProteinSequence` is
    immutable reference content that legitimately lives only in the graph, whereas an assignment is
    evidence tied one-to-one to the observation and travels with it.
    """
    _check_confidence(nodes, "ModifierAssignment", "I3")
    assignments = _index(nodes, "ModifierAssignment")
    for edge in _edges(edges, "ASSIGNS"):  # ModifierAssignment -> Modifier
        assignment = assignments[edge["from"]]
        if assignment.get("confidence") == "ambiguous":
            raise InvariantError(
                "I3",
                f"ModifierAssignment {edge['from']} asserts modifier {edge['to']} while "
                "confidence='ambiguous'; a K-GG site may not be named without a "
                "non-ambiguous assignment.",
            )

    assigned = {e["to"] for e in _edges(edges, "ASSIGNMENT_FOR")}  # -> SiteObservation
    for observation in _nodes(nodes, "SiteObservation"):
        if observation.get("id") not in assigned:
            raise InvariantError(
                "I3",
                f"SiteObservation {observation.get('id')} carries no ModifierAssignment. §6.1 "
                "requires one on every observation — created as basis='inferred_default', "
                "confidence='ambiguous' where nothing orthogonal is known. A site with no "
                "assignment states nothing about its modifier, which reads as an omission to be "
                "filled in rather than as the ambiguity it actually is.",
            )


def _check_I4(nodes: list[Node], edges: list[Edge]) -> None:
    """I4 — protein_adjusted is tri-state, and 'applied' requires an ADJUSTED_BY edge."""
    adjusted_from = {e["from"] for e in _edges(edges, "ADJUSTED_BY")}
    for dr in _nodes(nodes, "DifferentialResult"):
        state = dr.get("protein_adjusted")
        if state not in PROTEIN_ADJUSTED:
            raise InvariantError(
                "I4",
                f"DifferentialResult {dr.get('id')} has protein_adjusted={state!r}; "
                f"must be one of {sorted(PROTEIN_ADJUSTED)}.",
            )
        if state == "applied" and dr.get("id") not in adjusted_from:
            raise InvariantError(
                "I4",
                f"DifferentialResult {dr.get('id')} is protein_adjusted='applied' but has "
                "no ADJUSTED_BY edge to the protein-level result used to correct it.",
            )


def _check_I10(nodes: list[Node], edges: list[Edge]) -> None:
    """I10 — an enzyme may be attributed to a site only through a *live* EnzymeAssociation."""
    _check_confidence(nodes, "EnzymeAssociation", "I10")
    associations = _index(nodes, "EnzymeAssociation")
    for edge in _edges(edges, "ASSOCIATION_FOR"):  # EnzymeAssociation -> SiteObservation
        association = associations[edge["from"]]
        if association.get("retracted_at") is not None:
            raise InvariantError(
                "I10",
                f"SiteObservation {edge['to']} is attributed to an enzyme through "
                f"EnzymeAssociation {edge['from']}, which is retracted (not live).",
            )


def _check_I14(nodes: list[Node], edges: list[Edge]) -> None:
    """I14 — a multi-mapping *observation* is not rendered against one protein.

    Two enforceable halves since ADR-0022. The first is the original: an assignment concluding one
    protein out of several candidates must be `confirmed`. The second is new, and is the door the
    protein grain left open — an observation that *names* a group while resolving to one member of
    it asserts exactly what the first half forbids, through a different edge. `RESOLVES_TO_PROTEIN`
    is `MANY_MANY` precisely so it does not have to.

    Site grain is deliberately not covered here; see I14 in §8. A `ModificationSite` key carries a
    protein-specific position, so resolving to every candidate is not available, and rejecting the
    pick would refuse 82% of sites with nothing that would satisfy it.
    """
    _check_confidence(nodes, "ProteinAssignment", "I14")
    protein_assignments = _index(nodes, "ProteinAssignment")
    for edge in _edges(edges, "ASSIGNS_PROTEIN"):  # ProteinAssignment -> Protein
        assignment = protein_assignments[edge["from"]]
        candidates = assignment.get("candidate_proteins") or []
        if len(candidates) > 1 and assignment.get("confidence") != "confirmed":
            raise InvariantError(
                "I14",
                f"ProteinAssignment {edge['from']} renders an observation against one protein "
                f"({edge['to']}) out of {len(candidates)} candidates with "
                f"confidence={assignment.get('confidence')!r}; only 'confirmed' may.",
            )

    resolved: dict[Any, set[Any]] = defaultdict(set)
    for edge in _edges(edges, "RESOLVES_TO_PROTEIN"):  # ProteinObservation -> Protein
        resolved[edge["from"]].add(edge["to"])
    for observation in _nodes(nodes, "ProteinObservation"):
        candidates = set(observation.get("candidate_proteins") or [])
        pointed = resolved.get(observation.get("id"), set())
        # No edges in this batch is not a violation — the node may be re-staged as a referent
        # (ADR-0019). Pointing at *some* of what it names is.
        if len(candidates) > 1 and pointed and pointed != candidates:
            raise InvariantError(
                "I14",
                f"ProteinObservation {observation.get('id')} names {len(candidates)} candidate "
                f"proteins but RESOLVES_TO_PROTEIN reaches {sorted(pointed)}; an observation of a "
                "group resolves to every member, or it is rendering against a razor pick "
                "(ONTOLOGY.md §8 I14, ADR-0022).",
            )


def _check_I15(nodes: list[Node], edges: list[Edge]) -> None:
    """I15 — an Analysis producing differential results declares an Imputation (incl. 'none'),
    and a stochastic method records a seed."""
    imputed_analyses = {e["to"] for e in _edges(edges, "IMPUTATION_FOR")}
    produced_by = {e["to"] for e in _edges(edges, "WAS_GENERATED_BY")}
    for analysis_id in produced_by:
        if analysis_id not in imputed_analyses:
            raise InvariantError(
                "I15",
                f"Analysis {analysis_id} produces differential results but declares no "
                "Imputation (use method='none' when nothing was imputed).",
            )
    for imp in _nodes(nodes, "Imputation"):
        if imp.get("method") in STOCHASTIC_IMPUTATION and imp.get("seed") is None:
            raise InvariantError(
                "I15",
                f"Imputation {imp.get('id')} uses stochastic method "
                f"{imp.get('method')!r} without a seed; the result is irreproducible.",
            )


def _check_I16(nodes: list[Node], edges: list[Edge]) -> None:
    """I16 — every data-consuming Analysis declares the quantity and the filters applied."""
    for an in _nodes(nodes, "Analysis"):
        if an.get("kind") == "curation":  # curation consumes no quantity
            continue
        if an.get("quantity") is None:
            raise InvariantError(
                "I16", f"Analysis {an.get('id')} does not declare which quantity it consumed."
            )
        if an["quantity"] not in QUANTITY_VALUES:
            raise InvariantError(
                "I16",
                f"Analysis {an.get('id')} declares quantity {an['quantity']!r}, which is not in "
                f"the closed enum (ONTOLOGY.md §5): {sorted(QUANTITY_VALUES)}.",
            )
        if an.get("filters_applied") is None:
            raise InvariantError(
                "I16", f"Analysis {an.get('id')} does not declare the filters applied."
            )


def _check_I19(nodes: list[Node], edges: list[Edge]) -> None:
    """I19 — every Analysis sets parameters_observed (observed vs reported provenance)."""
    for an in _nodes(nodes, "Analysis"):
        if an.get("parameters_observed") is None:
            raise InvariantError(
                "I19",
                f"Analysis {an.get('id')} does not set parameters_observed; observed and "
                "reported provenance must be distinguished.",
            )


#: The two ways a `DifferentialResult` names what it measures (§7). Read from `schema.REL_TABLES`
#: rather than listed, so a third grain's result edge is caught here by the DDL that declares it
#: instead of by someone remembering to widen a tuple — which is the shape of omission I20's own
#: `neither` case was.
_RESULT_EDGES: tuple[str, ...] = tuple(
    sorted(
        r.name
        for r in schema.REL_TABLES
        if r.src == "DifferentialResult" and r.name.startswith("RESULT_FOR_")
    )
)


def _check_I20(nodes: list[Node], edges: list[Edge]) -> None:
    """I20 — every `DifferentialResult` attaches to exactly one of §7's `RESULT_FOR_*` edges.

    **Closes §11 Q7, answered 2026-08-07 and outstanding only for its number and this function.**
    The deferral it replaced — *once `perseus.py` emits results at both grains* — is the circular
    shape ADR-0023 names: the adapter chooses how many result edges to emit, so counting its output
    reports its own choice back. The evidence was never in the adapter.

    **The two halves rest on different evidence, and that is why the message distinguishes them.**
    *At least one* is empirical: before `aefd4e9`, the valid fixture's `bzk:dr2` carried
    `WAS_GENERATED_BY` and nothing else — a result attached to no observation it measures, sitting
    in the seed every invariant test validated against, passing. *At most one* is by construction:
    `bzk/analysis/differential.py` emits `RESULT_FOR_SITE` alone and `bzk/adapters/perseus.py`
    emits `RESULT_FOR_PROTEIN` alone, so nothing here can produce a result with both and the case
    is reachable only from a hand-written change-set.

    **Neither case is caught by ADR-0019's structural validation**, measured before this was written
    rather than assumed: a change-set whose result carries no `RESULT_FOR_*` edge validates, and so
    does one carrying both. That matters because a guard whose failure arrives from somewhere else
    establishes the somewhere else — the reason an assertion was withdrawn on 2026-08-10.

    **Not §3's *a single site-level `Analysis` emits both*.** That is a different axis: two results
    over one observation, corrected and uncorrected, **both site-grain and both attaching by
    `RESULT_FOR_SITE`** — so exactly-one holds per result and the two clauses never meet.
    Correspondingly this counts edges *per result*, never per analysis or per observation.
    """
    reached: dict[Any, set[str]] = defaultdict(set)
    for rel in _RESULT_EDGES:
        for edge in _edges(edges, rel):
            reached[edge["from"]].add(rel)
    for result in _nodes(nodes, "DifferentialResult"):
        rid = result.get("id")
        named = sorted(reached.get(rid, set()))
        if len(named) == 1:
            continue
        raise InvariantError(
            "I20",
            f"DifferentialResult {rid!r} attaches to {named or 'none'} of "
            f"{list(_RESULT_EDGES)}; a result measures exactly one thing. "
            + (
                "A result measuring nothing is an orphan statistic — a number with no observation "
                "behind it (ONTOLOGY.md §8 I20, §11 Q7)."
                if not named
                else "A result carrying both would claim one computation over two grains; §3's "
                "*a single site-level Analysis emits both* is two results, both site-grain "
                "(ONTOLOGY.md §8 I20, §11 Q7)."
            ),
        )


#: `DifferentialResult`'s anchors, read from `schema.IDENTITY` — the §3 table the key builder
#: mirrors — rather than listed here, so a sixth anchor is recomputed against without an edit. This
#: reads each as an edge whose *source* is the result, which is true of all five and is asserted in
#: `tests/test_invariants.py` rather than here: an anchor declared in the other direction would
#: contribute `null` to the recomputation and refuse every correction, and that is a red test rather
#: than a package that will not import.
_RESULT_ANCHORS: tuple[tuple[str, str], ...] = schema.IDENTITY["DifferentialResult"].anchors


def _check_I21(nodes: list[Node], edges: list[Edge]) -> None:
    """I21 — a correction's id names the baseline it was computed against (ADR-0025's null door).

    **What ADR-0025 left open, and it is not the acyclicity gap that record contemplated.** That ADR
    made `ADJUSTED_BY` an anchor so two corrections of one site against different parents stop
    minting one id. Nothing obliged a producer to *supply* it: `keys.identity_tuple` permits an
    absent anchor outright, because not every anchor applies to every instance. Omit it and the
    tuple carries `@DifferentialResult=␀null` — indistinguishable from a genuinely inapplicable
    anchor — and the two corrections are one node again, at
    `bzk:3473130e9cb7f1198196ee40b0e30727`, measured against shipped code before this was written.

    **Nothing else sees it.** `_check_I4` reads the `ADJUSTED_BY` edge and never the id, so a result
    minted through the null door with the edge present validates. `_check_I20` counts `RESULT_FOR_*`.
    ADR-0019's structural validation recomputes no ids at all — measured, because a guard whose
    failure arrives from somewhere else establishes the somewhere else, and one was withdrawn here
    for exactly that on 2026-08-10. So this fires at its own line.

    **Acyclicity is subsumed rather than asserted.** A cycle needs each id to encode the other's,
    which needs `sha256` to determine its own input — no fixed point in 12 iterations, and
    unsatisfiable by construction rather than merely unreached. The weaker rule *the id must differ
    from its no-baseline form* would close the null door and **not** this: two ids each minted
    honestly against some third baseline, then cross-linked, pass it and are refused here at both
    ends. That measurement is why this recomputes rather than compares against a null form.

    **Digest-shaped ids only, and that is a real limit.** `bzk:dr1` claims no digest and is left
    alone, so the valid fixture's four `bzk:dr*` results and the six hand-built change-sets in
    `tests/test_invariants.py` that mint one did not have to be re-keyed — and a hand-written cycle
    survives exactly as ADR-0025 already records. **Nothing in this repository produces the case**:
    no writer emits `protein_adjusted='applied'`, all 1,362 shipped results are `not_applied` and
    none carries the edge, so this is exercised only by constructed cases, as I20's and ADR-0025's
    own guard are.

    **The trigger is the edge, not the node, and that is what makes it writable at all.** The
    general form — *every digest-shaped id recomputes* — was measured over `bzk rebuild` and the
    differential before this scope was settled, and it is refused by the real ingestion: 1,362
    `SiteObservation`s and 36 `Sample`s are staged with **no** anchor edge in the change-set that
    stages them, because ADR-0019 permits a node to be re-staged as a referent (see `_check_I14`).
    A change-set that emits `ADJUSTED_BY` is producing the relationship rather than re-staging a
    referent, which is the one moment the baseline is known to be present.
    """
    adjusted = _edges(edges, "ADJUSTED_BY")
    if not adjusted:  # the shape all 1,362 shipped results have; nothing to recompute
        return

    anchors_of: dict[Any, dict[str, str]] = defaultdict(dict)
    for label, rel in _RESULT_ANCHORS:
        for edge in _edges(edges, rel):
            anchors_of[edge["from"]][label] = edge["to"]
    results = _index(nodes, "DifferentialResult")

    for edge in adjusted:
        rid = edge["from"]
        result = results.get(rid)
        if result is None or not keys.is_digest_id(rid):
            # A referent re-staged without its node is structural validation's business; a
            # hand-written id asserts nothing about its own content and cannot be held to it.
            continue
        anchors = anchors_of[rid]
        expected = keys.evidence_id("DifferentialResult", result, anchors)
        if expected == rid:
            continue
        # Which of the two failures this is, since they read very differently to whoever has to
        # fix it: a producer that never passed the anchor, or one that passed the wrong node.
        without = {k: v for k, v in anchors.items() if k != "DifferentialResult"}
        null_door = rid == keys.evidence_id("DifferentialResult", result, without)
        raise InvariantError(
            "I21",
            f"DifferentialResult {rid!r} is ADJUSTED_BY {edge['to']!r} but its id encodes "
            + ("no baseline at all" if null_door else "a different one")
            + f"; the id naming this baseline is {expected!r}. Since ADR-0025 the baseline is "
            "part of identity (§3), so a correction whose id omits it cannot be told from a "
            "correction of the same site against a different parent (ONTOLOGY.md §8 I21).",
        )


def _check_gene_absence(nodes: list[Node], edges: list[Edge]) -> None:
    """Every `Protein` names an `ENCODES` edge **or** a reason it has none — never neither (§4).

    Not a numbered invariant: it enforces a column's contract rather than one of §8's clauses, and
    it runs in the same place for the same reason — a change-set is self-contained (ADR-0019), so
    both halves are present or the change-set is malformed.

    **Written because the graph was wrong while the suite was green.** The first build of `Gene`
    put **3,492** proteins in the graph with a NULL `gene_absence` and no `ENCODES` edge: the two
    adapters mint an accession-only `Protein` for every candidate in a protein group, that path
    never went through `ResolvedProteins`, and its `__post_init__` partition check therefore never
    saw them. A guard that lives on the object the resolver returns cannot cover nodes minted
    beside it, which is why this one is at the change-set instead.
    """
    encoded = {e["to"] for e in _edges(edges, "ENCODES")}
    for protein in _nodes(nodes, "Protein"):
        pid = protein.get("id")
        absence = protein.get("gene_absence")
        if (pid in encoded) == (absence is not None):
            state = f"gene_absence={absence!r}" if absence is not None else "gene_absence NULL"
            raise InvariantError(
                "GENE_ABSENCE",
                f"Protein {pid!r} has {state} and "
                f"{'an' if pid in encoded else 'no'} ENCODES edge. §4: the column is NULL exactly "
                "when an edge reaches the protein, so an absent edge always names which of the "
                "three absences it is — an unexplained one reads as 'this protein has no gene' "
                "and is the collapse the column exists to prevent",
            )
        if absence is not None and absence not in schema.GENE_ABSENCE:
            raise InvariantError(
                "GENE_ABSENCE",
                f"Protein {pid!r} has gene_absence {absence!r}, which is not one of §4's "
                f"{sorted(schema.GENE_ABSENCE)}. A fourth absence with no name is the same defect "
                "one level in",
            )


_CHECKS: dict[str, Callable[[list[Node], list[Edge]], None]] = {
    "I2": _check_I2,
    "I3": _check_I3,
    "I4": _check_I4,
    "I10": _check_I10,
    "I14": _check_I14,
    "I15": _check_I15,
    "I16": _check_I16,
    "I19": _check_I19,
    "I20": _check_I20,
    "I21": _check_I21,
    "GENE_ABSENCE": _check_gene_absence,
}


def validate(nodes: list[Node], edges: list[Edge], only: str | None = None) -> None:
    """Run structural validation (ADR-0019) then write-time invariant checks over a change-set.

    Structural validation always runs first — a malformed change-set cannot be meaningfully checked
    for any invariant. With ``only`` set to an invariant id, run just that check afterwards (for
    targeted tests); otherwise run all. Raises `InvariantError` on the first violation; returns None
    if clean.
    """
    _validate_structure(nodes, edges)
    if only is not None:
        if only not in _CHECKS:
            raise ValueError(f"unknown or non-write-time invariant: {only!r}")
        _CHECKS[only](nodes, edges)
        return
    for check in _CHECKS.values():
        check(nodes, edges)
