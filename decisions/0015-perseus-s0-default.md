# ADR-0015 — Perseus `s0` test as the default statistical entry

| | |
|---|---|
| Status | Accepted |
| Date | 2026-08-06 |
| Supersedes | ADR-0011 |
| Superseded by | — |

## Context

ADR-0007 proposed implementing a Perseus-compatible modified *t*-test with the `s0` parameter, to reproduce the cutoffs used in the collaborating group's published work.

ADR-0011 superseded it. The reasoning was that the group's 2020 study used Perseus while its 2025 preprint reported GraphPad Prism for functional assays and stated nothing about proteomic statistics — read as evidence that the workflow had moved on. `moderated_t_ebayes` was made the default and `permutation_s0` was demoted to an optional entry for legacy reproduction.

**That reading was wrong.** Author correspondence, 2026-08-06, states the workflow directly: log₂ transformation of intensity values, filtering of missing values, imputation based on a normal distribution, and a dedicated two-sample statistical test, with volcano plots built on the difference in intensities. Perseus remains the group's workflow and is described as the field's long-standing standard.

## Decision

`perseus_s0` becomes the **default and required** entry in the statistics registry.

`moderated_t_ebayes` is retained as a secondary entry — better calibrated at *n* = 3 than a plain *t*-test, and useful for detecting when the choice of test is load-bearing. `welch_t` is retained as a sanity check.

The registry architecture established by ADR-0011 is unchanged. Only which entry is default was wrong.

## Consequences

**Positive.** The platform can reproduce the group's published and internal results, which is a precondition for adoption by the intended first user. The distinction between `perseus_s0` and `welch_t` with Benjamini–Hochberg is now explicit: `s0` introduces a fold-change dependence into the significance threshold, producing a curved boundary rather than straight cutoffs, and Perseus uses permutation-based FDR rather than BH. A reproduction ignoring this will not match their numbers even where it recovers the same proteins.

**Negative.** More implementation work than a plain moderated *t*-test, and the `s0` and FDR parameter values are not yet known — to be obtained at the meeting.

## The error worth recording

Absence of a stated method in a publication was treated as evidence of a changed method. It is not. It is absence of a stated method.

This is precisely the failure mode the platform exists to prevent — an inference presented, and acted upon, as though it were a measurement. That it occurred in the project's own reasoning rather than in its data is worth keeping visible.

## Alternatives considered

**Retain `moderated_t_ebayes` as default and offer Perseus compatibility as an option.** Rejected: it puts the burden of matching the collaborator's numbers on the collaborator rather than on the platform, which inverts the relationship the project depends on.

**Wrap Perseus itself.** Rejected: Perseus is a desktop GUI application, not a library. Implementing the test is more tractable than automating the tool.
