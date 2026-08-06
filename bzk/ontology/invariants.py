"""Write-time invariant enforcement over a staged change-set.

The invariants of ONTOLOGY.md §8 are errors, not warnings (CLAUDE.md): a violation raises
`InvariantError`, which ingestion must let propagate rather than downgrade. This module
covers the subset checkable when a change is written — I2, I3, I4, I10, I14, I15, I16, I19.
Export-boundary (I18) and whole-graph (I5, I9) invariants live elsewhere.

A change-set is plain data, independent of Kùzu storage: a node is ``{"label", **props}`` and
an edge is ``{"type", "from", "to"}``, mirroring the DDL in `schema.py`. This keeps the
honesty guarantees in one pure, testable place rather than scattered through adapters —
domain logic stays out of code that consumes the contract (ONTOLOGY.md §10).
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from bzk.ontology.schema import PROTEIN_ADJUSTED, STOCHASTIC_IMPUTATION

Node = dict[str, Any]
Edge = dict[str, Any]


class InvariantError(Exception):
    """A staged change violates an ONTOLOGY.md §8 invariant. Carries the invariant id."""

    def __init__(self, invariant: str, message: str) -> None:
        super().__init__(f"{invariant} — {message}")
        self.invariant = invariant


def _nodes(nodes: Iterable[Node], label: str) -> list[Node]:
    return [n for n in nodes if n.get("label") == label]


def _edges(edges: Iterable[Edge], rel: str) -> list[Edge]:
    return [e for e in edges if e.get("type") == rel]


def _index(nodes: Iterable[Node]) -> dict[str, Node]:
    return {n["id"]: n for n in nodes if "id" in n}


# ── One checker per invariant. Each raises InvariantError on the first violation it finds. ──


def _check_I2(nodes: list[Node], edges: list[Edge]) -> None:
    """I2 — a ModificationSite's parent Protein must carry a sequence_version."""
    by_id = _index(nodes)
    for edge in _edges(edges, "SITE_ON"):  # ModificationSite -> Protein
        protein = by_id.get(edge["to"])
        if protein is not None and protein.get("sequence_version") is None:
            raise InvariantError(
                "I2",
                f"ModificationSite {edge['from']} sits on Protein {edge['to']} "
                "which has no sequence_version; residue numbering is meaningless.",
            )


def _check_I3(nodes: list[Node], edges: list[Edge]) -> None:
    """I3 — no bare modifier claim: an ambiguous ModifierAssignment may not ASSIGNS a modifier."""
    by_id = _index(nodes)
    for edge in _edges(edges, "ASSIGNS"):  # ModifierAssignment -> Modifier
        assignment = by_id.get(edge["from"])
        if assignment is not None and assignment.get("confidence") == "ambiguous":
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
        association = by_id.get(edge["from"])
        if association is not None and association.get("retracted_at") is not None:
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
        assignment = by_id.get(edge["from"])
        if assignment is None:
            continue
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


_CHECKS = {
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
    """Run write-time invariant checks over a staged change-set.

    With ``only`` set to an invariant id, run just that one (for targeted tests); otherwise run
    every write-time check. Raises `InvariantError` on the first violation; returns None if clean.
    """
    if only is not None:
        if only not in _CHECKS:
            raise ValueError(f"unknown or non-write-time invariant: {only!r}")
        checkers = [_CHECKS[only]]
    else:
        checkers = list(_CHECKS.values())
    for check in checkers:
        check(nodes, edges)
