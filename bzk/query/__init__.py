"""The read path over Kùzu. Five questions, and no bare numbers (`ARCHITECTURE.md` §3).

Everything before this module writes. This is the first thing that reads, and the hazard specific
to a first read path is that its output *looks like an answer*: a list of rows is quotable the
moment it exists, and whatever status the ontology requires to travel with a number has to travel
with it from here, because a renderer is not the only consumer.

**Three rules, each traceable to a clause rather than to taste.**

1. **No bare number leaves this module.** `ONTOLOGY.md` §8 I14's display half — *"where assignment
   is `razor` or `leading`, views and exports name the candidate set"* — and `ROADMAP.md`
   § *Weeks 7–8*'s *"ambiguity and correction status visible everywhere a number appears"*. So a
   site row carries the candidate set and the confidence of the assignment that named it, and a
   differential row carries the `Analysis`'s declared quantity and test (I16).

2. **This module is I5's enforcement point.** `HANDOFF.md` §8 classifies **I5** and **I8**'s
   reachability half as *WG — whole-graph / query-time, not written*, and names I5's mechanism as a
   per-entity `unprovenanced` flag. Saying *not here* would leave the invariant homeless in the
   layer its own classification points at. It is scoped to what `ONTOLOGY.md` §7 calls a
   `prov:Entity` — `Dataset`, `SiteObservation`, `DifferentialResult`, `Figure` — because I5 says
   *entity node* and §7 is where that word is defined. Reference nodes are not entities and carry
   no such flag; claiming one for them would be a wider assertion than the invariant makes.

3. **An absent answer is a value, never an empty container.** The precedent is `quant_ref = NULL`
   (§5.1): the node carries the reason its neighbour is missing. Measured on 2026-08-09, two of the
   five questions came back empty from the real graph and meant different things by it —
   `differential_table` had no `DifferentialResult` to return, `imputation_state` had no
   `Imputation` — and `refusals` cannot be answered at all, because a refusal is never written
   anywhere. An `[]` for all three would be one object standing for four different facts.

   **Writing the `welch_t` run the same day left one of those three empty and changed what the
   other two mean.** `differential_table` returns 1,362 rows for that analysis and `NONE_FOUND` for
   the two that produced none; `imputation_state` answers for it and returns `NONE_FOUND` for the
   others. Neither of those two call sites changed — the *answer* did, from a claim about the store
   to a claim about the analysis, which is exactly what an absence value buys and a bare `[]` would
   have hidden. `refusals` still cannot be answered at all — **and after the question was taken up
   and answered on 2026-08-09, it is the one that stays that way**: a refusal is not an entity, so
   there is nothing for this module to read. It is the only live case `NOT_RETAINED` has, which is
   what keeps the fourth value from being a member with no instance.

**What this module does not do.** It writes no file, so `ONTOLOGY.md` §8 **I18**'s embargo check
does not land here and is not weakened here — `HANDOFF.md` §8's EX class puts it at the first
export, report or figure-writing path. It renders nothing, opens no HTTP port, and imports no
plotting library; `api/` is its consumer.
"""

from bzk.query.graph import (
    ABSENT,
    DEFAULT_GRAPH,
    Absence,
    DifferentialRow,
    GeneSymbolAnswer,
    ImputationState,
    Provenance,
    RefusalAnswer,
    SiteKeying,
    analysis_ids,
    connect,
    differential_table,
    gene_absence_census,
    gene_symbols,
    imputation_state,
    refusals,
    site_ids,
    site_keying,
    unprovenanced,
)

__all__ = [
    "ABSENT",
    "DEFAULT_GRAPH",
    "Absence",
    "DifferentialRow",
    "GeneSymbolAnswer",
    "ImputationState",
    "Provenance",
    "RefusalAnswer",
    "SiteKeying",
    "analysis_ids",
    "connect",
    "differential_table",
    "gene_absence_census",
    "gene_symbols",
    "imputation_state",
    "refusals",
    "site_ids",
    "site_keying",
    "unprovenanced",
]
