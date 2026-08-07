"""Reference nodes that come from version control rather than from a file or an authority fetch.

Almost every reference node in this graph is resolved from outside — a `Protein` from UniProt, a
`Gene` from HGNC. The `Modifier` nodes are different: which modifiers a tryptic K-GG remnant cannot
distinguish is a **fact about biology that the project asserts**, and ADR-0021 requires it to live
in version control rather than in graph state, because `ModifierAssignment.candidate_modifiers` is
identifying and would otherwise make every assignment id a function of when the graph was seeded.

So the set has one home — `schema.GG_REMNANT_MODIFIERS`, guarded against `ONTOLOGY.md` §6.1 — and
this module is the only thing that turns it into nodes. It is also what keeps I9 true for them: the
seed is regenerable from the source tree, which is inside I9's input list.
"""

from __future__ import annotations

from bzk.adapters.base import Node
from bzk.ontology import schema
from bzk.ontology.invariants import NODE_TYPE_KEY


def modifier_nodes() -> list[Node]:
    """The `Modifier` nodes for the K-GG remnant set (§6.1, §4).

    `Modifier` is authority-assigned (§3), so the id *is* the UniProt CURIE and nothing is minted.
    `leaves_gg_remnant` is `true` for every member by construction — membership in this map is
    exactly the claim that column makes, which is why the set carries no members where it is false.
    """
    return [
        {
            NODE_TYPE_KEY: "Modifier",
            "id": accession,
            "name": modifier.name,
            "c_terminal_motif": modifier.c_terminal_motif,
            "leaves_gg_remnant": True,
        }
        for accession, modifier in sorted(schema.GG_REMNANT_MODIFIERS.items())
    ]


#: The value `ModifierAssignment.candidate_modifiers` takes at GlyGly grain, sorted so the field —
#: which is identifying — cannot fork an id on enumeration order (I7). `keys.canonical_value` sorts
#: `STRING[]` before hashing too; this is belt and braces, and it makes the emitted node readable.
CANDIDATE_MODIFIERS: list[str] = sorted(schema.GG_REMNANT_MODIFIERS)
