# `walk/PXD018299-author-parameters.json` — the schema, with an example

**This is an example and a schema, not a record.** `notes/example-author-parameters.json` beside it
carries placeholder values. The real file, if it ever exists, is
`walk/PXD018299-author-parameters.json`, and **this turn deliberately did not create it**: its
presence is a claim that the anchor paper's authors stated these parameters, and nobody has.

## Why the file exists at all

`walk/PREREG-PXD018299-H10.md`'s opening section admits author-stated parameters only through a
committed file: *"Received and before the run are established by the record, not by memory."* The
file is the record. `bzk/sources/pxd018299_h10.py` reads it, validates it, and records whether git
tracked it at the run's commit.

## The schema

| key | required | meaning |
|---|---|---|
| `source` | **yes** | who stated the values, when, and in what form |
| `date_received` | **yes** | the date the statement was received |
| `width_sd` | no | the imputation's width, in observed SD units |
| `downshift_sd` | no | the imputation's downshift, in observed SD units |
| `scope` | no | `per_sample` or `whole_matrix` |
| `seed` | no | the imputation seed |
| `randomisations` | no | the permutation count |
| `scheme` | no | one of `perseus_s0`'s four permutation schemes |

Any key that is not in this table **refuses by name**. That is the one failure mode this file has:
a misspelled key would otherwise be dropped silently and the registered default run in its place,
under a record claiming the authors' value. Any parameter the file omits takes the registered
default, which is the pre-registration's own rule.

## What it changes, and what it cannot

- It becomes **readout A's primary** if — and only if — the file is *committed* before the run.
  An untracked file on someone's disk is not a record, and the run reports `tracked_in_git` either
  way.
- **It never reaches H10's verdict.** Readout B stays on the registered default cell, as
  `HYPOTHESIS.md` v8's rule requires and §6 B repeats. `tests/test_pxd018299_h10.py` holds that
  the verdict is identical with and without the file.
