# ADR-0008 — Append-only assertions with explicit retraction

| | |
|---|---|
| Status | Proposed |
| Date | 2026-08-09 |
| Supersedes | — |
| Superseded by | — |

## Context

Every inference this platform records can turn out to be wrong: a modifier assigned from
concordance, an enzyme attributed from a perturbation, a protein picked from a shared peptide. In a
mutable store the correction is destructive — the row is edited, downstream figures silently
change, and nothing records that the claim was ever made or ever different. A reader cannot
distinguish "this was always the conclusion" from "this replaced something else last Tuesday".

**Written 2026-08-09 from `ARCHITECTURE.md` §5's one-line seed.** The decision itself is not new
and is not made here: it is already normative as the `EvidencedInference` contract at
`ONTOLOGY.md` §6 and as invariant I6. This record exists so the reasoning has a home in
`decisions/`; where it and the normative text differ, `CLAUDE.md` § Conventions makes
`ONTOLOGY.md` right.

## Decision

Assertion nodes are **immutable**. Every `EvidencedInference` subtype carries `asserted_at` and
`retracted_at`; revision creates a **new** node and sets `retracted_at` on the old, and both remain
readable. Retraction propagates to every downstream figure and report (I6).

`retracted_at` is deliberately outside evidence-node identity (ADR-0020), so retracting a claim does
not re-key it.

## Consequences

The graph accumulates superseded nodes, which is the intended cost: a query for live assertions
filters on `retracted_at IS NULL`, and the history remains queryable rather than lost.

Because `retracted_at` is outside identity and nothing in `raw/` supplies it, a rebuild reconstructs
the node but **not** the fact that it was retracted. `OPERATIONS.md` §2 carries the consequence: the
curation export must ship a retraction record per retracted assertion, and without it every
retraction is lost on the next rebuild — I6 failing exactly where I9 is meant to make regeneration
cheap.

The convention `decisions/README.md` applies to its own records is borrowed from this decision, and
its ADR-0013 note is the recorded cost of applying it to prose as well as to data.

## Alternatives considered

**Mutable assertions with an audit log.** Rejected: the log is a second store that can disagree with
the first, and the thing a reader needs — *what did the graph say when this figure was made* — is
answerable only by replaying it.

**Soft delete with no supersession link.** Rejected: it records that a claim died and not what
replaced it, so a reader sees a gap rather than a revision.

**Versioned rows with a monotonic revision number.** Rejected: it makes identity depend on how many
times a claim has been revised, which is a fact about the project's editing history rather than
about the claim — and it conflicts with ADR-0020's content-derived ids.
