# ADR-0011 — Statistical tests are pluggable behind a registry; `moderated_t_ebayes` default

| | |
|---|---|
| Status | Superseded |
| Date | 2026-08-06 |
| Supersedes | ADR-0007 |
| Superseded by | ADR-0015 |

## Context

ADR-0007 fixed one test — a Perseus-compatible modified *t* with `s0` — as the platform's
statistical entry point, chosen to match the cutoffs in the collaborating group's 2020 work.

Two things were then read as evidence that the choice was dated. The group's 2025 preprint reports
GraphPad Prism for its functional assays and **states nothing about proteomic statistics**, which
was read as the workflow having moved on. And a single hard-coded test is a structural weakness
independent of which test it is: a platform that retains only log₂FC and adjusted *p* is married to
whichever test produced them.

**Written 2026-08-09, after both this record and its successor were already in force.** What it
decided is recovered from ADR-0015's Context and from `ARCHITECTURE.md` §4; the deliberation itself
is not recorded anywhere and is not invented here.

## Decision

Statistical tests sit behind a **registry**. A test is an entry with a declared name recorded on the
`Analysis` (`test`, per I16), FDR control is a separate pluggable step recorded in `fdr_method`, and
the quantitative matrix is retained so any entry can be recomputed over the same values.

`moderated_t_ebayes` becomes the default entry. `permutation_s0` is demoted to an optional entry,
kept for legacy reproduction of the group's published results.

R was revisited here as a way of getting `limma`'s reference implementation and rejected again, on
the install-cost grounds ADR-0002 first gave.

## Consequences

The registry is what makes the comparison capability possible at all: running a second test over a
retained matrix and reporting where the two diverge is a finding about analytical sensitivity, and
no existing tool reports it.

Making the default a test the collaborator does not use put the burden of matching their numbers on
them rather than on the platform.

## Why it was superseded

ADR-0015 reversed the default on author correspondence of 2026-08-06, which states the group's
workflow directly and confirms Perseus. **The registry architecture decided here is unchanged and
survives into ADR-0015; only which entry is default was wrong.** The error worth keeping is recorded
there and is not restated here: absence of a stated method in a publication was treated as evidence
of a changed method.

## Alternatives considered

**Keep one hard-coded test (ADR-0007's shape).** Rejected: it forecloses recomputation and
comparison, and it makes the choice of test invisible in the output — a `DifferentialResult` with no
recorded `test` cannot be reproduced or argued with.

**Depend on R for `limma`.** Rejected again, following ADR-0002: an R dependency breaks the
one-afternoon install promise in `VISION.md`, and the platform is an application before it is a
statistics package.

**Offer several tests with no default.** Rejected: a required choice at the point of first use is a
worse failure than a wrong default, because it stalls the user who has least context.
