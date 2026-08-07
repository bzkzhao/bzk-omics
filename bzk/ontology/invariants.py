"""Write-time invariant enforcement over a staged change-set.

The invariants of ONTOLOGY.md §8 are errors, not warnings (CLAUDE.md): a violation raises
`InvariantError`, which ingestion must let propagate rather than downgrade.

**Enforced here** (write-time, over the staged change-set):
  I2, I3, I4, I10, I14, I15, I16, I19 — one checker each — plus **change-set structural
  validation** (ADR-0019): every referent an edge names is present, every edge endpoint carries
  the node label `schema.py` declares for that relationship, every edge type is a relationship in
  the DDL, and every node has a unique id. Structural failures raise ``STRUCTURE``, except a
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
  - I9  (OP)         reproducible rebuild — partly exercised by `rebuild.py`
  - I11 (data)       quantitative retention — needs the DuckDB layer
  - I12 (LINT)       no tryptic assumptions — a source-tree lint, not a change-set check
  - I13 (LINT)       pipeline metadata is data — a source-tree lint, not a change-set check
  - I17 (CON)        reviewed preferred — recorded by the adapter / ProteinAssignment construction
  - I18 (EX)         embargo — the export-boundary check; must land with the first export path

A change-set is plain data, independent of Kùzu storage: a node is ``{"label", "id", **props}`` and
an edge is ``{"type", "from", "to"}``. Relationship and label expectations are derived from
`schema.py` (the mirror of ONTOLOGY.md §4-7), never restated here — domain logic stays out of code
that consumes the contract (ONTOLOGY.md §10).
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from bzk.ontology import schema
from bzk.ontology.schema import PROTEIN_ADJUSTED, STOCHASTIC_IMPUTATION

Node = dict[str, Any]
Edge = dict[str, Any]

# Endpoint labels per relationship, and valid relationship names — derived from the schema, so
# this module mirrors ONTOLOGY.md rather than becoming a second source of truth.
_REL_ENDPOINTS: dict[str, tuple[str, str]] = {t.name: (t.src, t.dst) for t in schema.REL_TABLES}

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
    return [n for n in nodes if n.get("label") == label]


def _edges(edges: Iterable[Edge], rel: str) -> list[Edge]:
    return [e for e in edges if e.get("type") == rel]


def _index(nodes: Iterable[Node]) -> dict[Any, Node]:
    return {n["id"]: n for n in nodes if "id" in n}


def _validate_structure(nodes: list[Node], edges: list[Edge]) -> None:
    """ADR-0019 — a change-set must be self-contained and well-formed before any invariant is
    meaningful. Expectations come from `schema.py`, so this checks against ONTOLOGY.md's DDL."""
    seen: set[Any] = set()
    for node in nodes:
        node_id = node.get("id")
        if node_id is None:
            raise InvariantError("STRUCTURE", f"node labelled {node.get('label')!r} has no id")
        if node_id in seen:
            raise InvariantError("STRUCTURE", f"duplicate node id {node_id!r} in the change-set")
        seen.add(node_id)

    by_id = {node["id"]: node for node in nodes if "id" in node}
    for edge in edges:
        rel = edge.get("type")
        if rel not in _REL_ENDPOINTS:
            raise InvariantError(
                "STRUCTURE", f"edge type {rel!r} is not a relationship in the schema"
            )
        owner = _REL_INVARIANT.get(rel, "STRUCTURE")
        src_label, dst_label = _REL_ENDPOINTS[rel]
        for role, expected in (("from", src_label), ("to", dst_label)):
            referent = by_id.get(edge.get(role))
            if referent is None:
                raise InvariantError(
                    owner, f"{rel} names {role} {edge.get(role)!r}, absent from the change-set"
                )
            if referent.get("label") != expected:
                raise InvariantError(
                    owner,
                    f"{rel} {role} {edge.get(role)!r} is labelled {referent.get('label')!r}, "
                    f"not {expected!r} as the schema declares",
                )


# ── One checker per invariant. Structural validation has already guaranteed that every edge
#    endpoint below is present and correctly labelled, so no referent-absence guard is needed. ──


def _check_I2(nodes: list[Node], edges: list[Edge]) -> None:
    """I2 — a ModificationSite's parent Protein must carry a sequence_version."""
    by_id = _index(nodes)
    for edge in _edges(edges, "SITE_ON"):  # ModificationSite -> Protein
        protein = by_id[edge["to"]]
        if protein.get("sequence_version") is None:
            raise InvariantError(
                "I2",
                f"ModificationSite {edge['from']} sits on Protein {edge['to']} "
                "which has no sequence_version; residue numbering is meaningless.",
            )


def _check_I3(nodes: list[Node], edges: list[Edge]) -> None:
    """I3 — no bare modifier claim: an ambiguous ModifierAssignment may not ASSIGNS a modifier."""
    by_id = _index(nodes)
    for edge in _edges(edges, "ASSIGNS"):  # ModifierAssignment -> Modifier
        assignment = by_id[edge["from"]]
        if assignment.get("confidence") == "ambiguous":
            raise InvariantError(
                "I3",
                f"ModifierAssignment {edge['from']} asserts modifier {edge['to']} while "
                "confidence='ambiguous'; a K-GG site may not be named without a "
                "non-ambiguous assignment.",
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
    by_id = _index(nodes)
    for edge in _edges(edges, "ASSOCIATION_FOR"):  # EnzymeAssociation -> SiteObservation
        association = by_id[edge["from"]]
        if association.get("retracted_at") is not None:
            raise InvariantError(
                "I10",
                f"SiteObservation {edge['to']} is attributed to an enzyme through "
                f"EnzymeAssociation {edge['from']}, which is retracted (not live).",
            )


def _check_I14(nodes: list[Node], edges: list[Edge]) -> None:
    """I14 — a multi-mapping peptide is not rendered against one protein without a
    ProteinAssignment of confidence='confirmed'."""
    by_id = _index(nodes)
    for edge in _edges(edges, "ASSIGNS_PROTEIN"):  # ProteinAssignment -> Protein
        assignment = by_id[edge["from"]]
        candidates = assignment.get("candidate_proteins") or []
        if len(candidates) > 1 and assignment.get("confidence") != "confirmed":
            raise InvariantError(
                "I14",
                f"ProteinAssignment {edge['from']} renders a site against one protein "
                f"({edge['to']}) out of {len(candidates)} candidates with "
                f"confidence={assignment.get('confidence')!r}; only 'confirmed' may.",
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


_CHECKS: dict[str, Callable[[list[Node], list[Edge]], None]] = {
    "I2": _check_I2,
    "I3": _check_I3,
    "I4": _check_I4,
    "I10": _check_I10,
    "I14": _check_I14,
    "I15": _check_I15,
    "I16": _check_I16,
    "I19": _check_I19,
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
