# ADR-0016 — Embargoed dataset state

| | |
|---|---|
| Status | Accepted |
| Date | 2026-08-06 |
| Supersedes | — |
| Superseded by | — |

## Context

`Dataset.source` recognised two states: `local` for data the user generated, and `pride` for public deposits. Both are exportable without restriction.

A collaborator has offered an unpublished GlyGly dataset with substantially improved coverage. That data is neither. It must be fully ingestible, queryable and analysable, and must not leave the machine in any export, report or figure until released.

The situation is not exceptional. The platform's intended users are researchers working on unpublished data, and most of what they hold is in this state most of the time.

## Decision

A third state, `embargoed`, with three supporting fields: `embargo_holder` (who controls release), `embargo_reference` (manuscript or agreement), and `embargo_released_at` (NULL while embargoed).

Invariant I18 enforces it at the **export boundary**, not at query time. Within the local instance the data is unrestricted; nothing may cross the boundary into an export, report, figure file or shared artifact while the embargo stands.

Release is an event rather than an edit: setting `embargo_released_at` and changing `source` to `pride` records that the data became public, and the prior state remains inspectable.

## Consequences

**Positive.** The platform can hold collaborator data safely, which is a precondition for having a real user at all. Enforcing at the boundary rather than at query time means the restriction is invisible during normal work and impossible to circumvent accidentally at the point it matters.

**Negative.** Every export path must consult the check, so adding a new export route creates a new place to get it wrong. Mitigated by routing all exports through a single function.

**Note.** This is the point at which local-first stops being a design preference stated in `VISION.md` and becomes a condition of the collaboration. A cloud-dependent system could not accept this data at all.

## Alternatives considered

**Restrict at query time.** Rejected: it would make embargoed data awkward to work with, which defeats the purpose of ingesting it.

**A separate instance for embargoed data.** Rejected: it prevents cross-dataset queries between embargoed and public data, which is the platform's central capability.

**Rely on the user to remember.** Rejected for the reason every invariant exists — a rule that depends on recollection at 11pm is not a rule.
