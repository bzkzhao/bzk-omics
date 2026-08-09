# ADR-0010 — `Observation` and `EvidencedInference` are contracts, not tables

| | |
|---|---|
| Status | Proposed |
| Date | 2026-08-09 |
| Supersedes | — |
| Superseded by | — |

## Context

Two families of node recur across the schema. Observations are things an instrument reported —
sites, proteins, enrichments. Evidenced inferences are things the platform concluded — which
modifier, which enzyme, which protein a shared peptide came from. Each family shares structure
across its members, and Kùzu has no inheritance, so there is no supertype table to hang it on.

**Written 2026-08-09 from `ARCHITECTURE.md` §5's one-line seed.** No record of the original
deliberation survives; the substance below is read off `ONTOLOGY.md` §5.1, §6 and §10 as they stand.

## Decision

Both supertypes are **contracts every subtype must satisfy**, enumerated in the document and
enforced by review rather than by a base table.

`Observation` (§5.1): a content-derived `id`, a `quant_ref` naming the columnar table holding its
per-sample values, a `REPORTS_SITE` edge from a `Dataset`, a `RESOLVES_TO` edge to a reference node,
and provenance reachability to an `Analysis` (I5).

`EvidencedInference` (§6): `basis` from a closed enum, `confidence`, `rationale`,
`asserted_at` / `retracted_at`, and an evidence edge to an `Analysis` or a `Publication`.

The binding half is the consumer rule, which `CLAUDE.md` § Conventions states as a working
convention: code consuming either contract must work for every subtype, and an `isinstance` branch
outside a subtype module is a defect.

## Consequences

A new subtype is additive — `ONTOLOGY.md` §10 prices an `Observation` subtype at days and an
`EvidencedInference` subtype at days plus an enum value and a target node — and nothing that
consumes the contract changes. This is what makes the schema generalisable past PTM proteomics
without the generality having cost anything up front.

What a contract cannot do is fail at write time. There is no table to constrain, so a subtype that
omits `quant_ref` or ships an open `basis` is caught by review or by an invariant written for it,
not by the store. That is the price of Kùzu having no inheritance, and it is why §5.1 and §6
enumerate the members explicitly rather than describing them.

## The seed's framing still holds; the membership rule is what has moved

The seed line has been reworded twice, and neither rewording touched the contract mechanism — both
narrowed **what qualifies as an `EvidencedInference` at all**, which is a different question and is
recorded here because the two are easy to conflate.

* **ADR-0024** rejected *"the promotion is an inference and is recorded as one"*. Choosing which
  `ProteinSequence` a site keys against is forced by the schema, and a forced choice is not a claim
  about the world. The cost of having had it the other way was a spurious `ProteinAssignment` basis
  row and a conflict with I14.
* **`ONTOLOGY.md` §6.3.4** settled that a name copied from UniProt is a plain property, not an
  inference: the platform chooses nothing and derives nothing in copying it, and reaching for the
  inference machinery because a fact came from outside is the same error one level along.

So the rule the contract needs beside it: **an `EvidencedInference` is a claim the platform makes
that the primary measurement does not support.** Copying is not one, and neither is a choice the
schema forces. Nothing here changes §6's contract; it names the test that keeps the contract's
membership honest.

## Alternatives considered

**One wide table per family with a discriminator column.** Rejected: every subtype's fields would
have to be nullable on every row, so the schema could no longer state which fields a given subtype
requires — the thing the contract exists to state.

**Duplicate the shared fields into each subtype with no contract recorded.** Rejected: it is what
the schema physically does anyway, and leaving it unstated means the shared shape survives only as
a coincidence that the next subtype is free to break.

**Enforce the contract in code with an abstract base class.** Not rejected as wrong, but it does not
reach the graph: the store holds rows, not objects, and a change-set assembled from a dict would
bypass it. The invariant suite is where enforcement that must survive the write path lives.
