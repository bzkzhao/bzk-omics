# ADR-0019 — Change-sets are self-contained; structural validation precedes invariants

| | |
|---|---|
| Status | Accepted |
| Date | 2026-08-07 |
| Supersedes | — |
| Superseded by | — |

## Context

Write-time invariant checks (`bzk/ontology/invariants.py`) run over a *change-set* — a batch of
node and edge dicts staged for a write. An audit found four of the eight checks passing vacuously:
I2, I3, I10 and I14 look up a node by an edge endpoint and guard with `if referent is not None`, so
when the referent is absent from the batch the check enforces nothing and reports nothing. Because a
change-set is a batch, an adapter that stages proteins in one batch and sites in another would get a
clean I2 on the site batch — the invariant silent precisely where it matters.

Three further structural assumptions were unstated and unchecked, so a malformed change-set could
reach a check and be read as valid:

- an edge endpoint's node label was never verified against what the schema declares for that
  relationship — `_check_I2` read `sequence_version` off whatever sat at `edge["to"]`, and
  `_check_I15` inferred "produced differential results" from the edge type alone, sound only because
  the DDL restricts `WAS_GENERATED_BY`, which the validator never consulted;
- an edge type outside the DDL was silently ignored;
- the node index dropped nodes lacking an `id` and let a duplicate `id` last-win.

The question is what a dangling or malformed reference *means*. Three options.

## Decision

**(a) A change-set must be self-contained. A dangling or malformed reference is an
`InvariantError`.** Structural validation runs first and unconditionally, before any invariant
check, and enforces four things, with expectations derived from `schema.py` (never restated, so this
stays a mirror of ONTOLOGY.md §4-7):

1. **Referent presence.** Every node an edge names by `from`/`to` is present in the change-set.
2. **Endpoint labels.** Each endpoint carries the node label the schema declares as that
   relationship's source/target.
3. **Known relationships.** Every edge `type` is a `REL TABLE` in the DDL.
4. **Node identity.** Every node has an `id`; ids are unique within the change-set.

Attribution: a failure of (1) or (2) on a relationship a specific invariant consults
(`SITE_ON`→I2, `ASSIGNS`→I3, `ASSOCIATION_FOR`→I10, `ASSIGNS_PROTEIN`→I14) raises **that
invariant**, so the error names the relationship at fault. Every other structural failure raises
**`STRUCTURE`**.

## Consequences

**Positive.** The four vacuous checks now enforce. The label check makes the invariant checks sound
rather than accidentally sound: a check that reads a field off an endpoint is now guaranteed the
endpoint is the type it assumes. Deriving expectations from `schema.py` means a schema change
propagates to the validator with no second edit, preserving the mirror the consistency test
(`test_schema.py`) already guards.

**Negative.** Adapters must stage a coherent unit: a `SiteObservation` with its resolved `Protein`
(I2) and its mandatory `ModifierAssignment` (§6.1) in the same change-set. A referent already in the
graph must be re-staged into any change-set that references it. This is redundant but cheap and
safe, because reference keys are content-derived (I7), so re-staging is idempotent — the cost of
keeping the validator pure.

**Fifth hole (multiplicity), added 2026-08-07.** The `RelTable.multiplicity` in `schema.py` — the
same source as the endpoints — was initially unchecked, so two `MEASURED_AT` edges from one
`SiteObservation` (declared `MANY_ONE`) passed. Structural validation now also enforces
multiplicity within the change-set: for `MANY_ONE` a source id appears at most once for that
relationship, for `ONE_MANY` a destination id at most once, for `ONE_ONE` both. Failures raise
`STRUCTURE`. This is change-set-scoped — Kùzu enforces the same bound at write time across
change-sets — but catches the malformed batch before it reaches the store.

**Note.** This is the shape of the ingestion contract for the adapters (weeks 3-6): batch by a
complete fact, not by node type.

## Alternatives considered

**(b) Resolve missing referents against the graph before checking.** Rejected: it threads a live
Kùzu handle into every checker, breaking the one architectural bet this module makes — that
invariants are a pure function over a change-set, independent of storage and unit-testable without a
graph (ONTOLOGY.md §10). It also invites a check-then-write race.

**(c) Record missing referents as unchecked and re-verify at a whole-graph level.** Rejected: it
demotes a write-time guarantee to a deferred warning, re-checked by a whole-graph pass that does not
exist, and "errors, not warnings" (CLAUDE.md) is the discipline that makes the design worth having.
A rule enforced later is a rule that fails to fire under deadline.
