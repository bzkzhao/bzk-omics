# ADR-0006 — Modifier identity is a defeasible assignment, not a site property

| | |
|---|---|
| Status | Proposed |
| Date | 2026-08-09 |
| Supersedes | — |
| Superseded by | — |

## Context

Ubiquitin, NEDD8 and ISG15 leave an identical K-ε-GG remnant on the acceptor lysine after tryptic
digestion (`ONTOLOGY.md` §6.1). Neither the precursor mass nor the MS² fragmentation distinguishes
them. The field's convention is to report a diGly site as ubiquitination, which holds at baseline
because ubiquitin conjugation dominates and fails under type I interferon stimulation — the exact
condition this project exists to study.

The schema question that follows is where the modifier lives. A column on the site is the obvious
shape and is what most tools do.

**Written 2026-08-09 from `ARCHITECTURE.md` §5's one-line seed and §6.1 as it stands.** No record of
the original deliberation survives; what is reconstructed here is the decision the schema embodies,
not a discussion that happened.

## Decision

The modifier is **not** a property of the site. `ModificationSite.modification_type` records the
**remnant** — `unimod:121` — which is what the instrument measured. Which UBL produced it is a
separate `ModifierAssignment` node carrying `basis`, `candidate_modifiers`, `confidence`,
`rationale` and an evidence edge to an `Analysis` or a `Publication`.

I3 makes the consequence enforceable: no view or export may render a K-GG site as "ubiquitination"
unless a live assignment has `confidence != 'ambiguous'`.

## Consequences

A site is storable with its modifier unknown, and unknown is a first-class state rather than a
default. The cost is that every consumer must handle a site with no live assignment; the benefit is
that the platform cannot silently assert the field's convention.

`ModificationSite`'s key composes the remnant CURIE, not the modifier, so a later assignment
changes no id — which is what makes the inference defeasible in practice and not only in name.

## Alternatives considered

**A `modifier` column defaulting to `ubiquitin`.** Rejected: it is the field's error expressed in
the schema, and it is unfalsifiable from inside the data — nothing distinguishes a defaulted value
from a measured one.

**A nullable `modifier` column, set only when known.** Rejected: it can hold a conclusion with no
basis, no confidence and no evidence edge, so a curator cannot tell a knockout-supported assignment
from a guess, and a retraction has nowhere to go.

**One `ModificationSite` per (site, modifier) pair.** Rejected: it makes the site's identity depend
on an inference, so re-assigning the modifier would re-key the site and every digest anchored on it
— the failure ADR-0005's key deliberately avoids.
