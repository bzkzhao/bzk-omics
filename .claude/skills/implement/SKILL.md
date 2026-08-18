---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

Read `.claude/config/issue-tracker.md` for where the spec or tickets live, and
`.claude/config/domain.md` for which documents govern the change before you start.

Use `tdd` where possible, at pre-agreed seams.

Once done, use `code-review` to review the work.

## Before you write code

**`ONTOLOGY.md` is normative.** Its DDL is not illustrative. If the change needs the schema to
differ, amend `ONTOLOGY.md` *first*, in its own step, and never reconcile silently in the code.

**Invariants are errors, not warnings.** The invariants in `ONTOLOGY.md` §8 fail ingestion. Do not
downgrade one to make a dataset load.

**Tests before code, invariants before adapters.** The invariant suite is written first and fails
first. An adapter that ingests data while violating I3 or I14 is worse than no adapter.

## Checks

Run `mypy` and a single test file regularly, and the full suite once at the end.

`CLAUDE.md` § Working style, point 1, enumerates the checks and the target each runs against,
and says why the targets are narrower than the repository. Run them from there rather than
from a copy — a copied command list goes stale the moment a target moves, and this file has
no way to notice.

Report each by name at its actual result, with its target stated. A check not run is reported
as not run — silence is not a pass.

## Closing the turn

An implementation turn that touches a critical node — any `ONTOLOGY.md` amendment, any new ADR,
the key builder, any adapter, or anything touching the export boundary (I18) — **closes** with the
four-point verification report in `CLAUDE.md` § Working style. Report it in full, in your own
words, from the source; it is not restated here because a second copy would diverge.

Two points carry the most weight and are the easiest to skip:

- **A new guard is not verified until it has been made to fail**, and the mutation that fails it is
  itself confirmed to have applied. Read the mutated file back or read the failure message; never
  take the exit status alone. Revert each mutation and confirm the suite is green before reporting.
- **State what the change did not cover.** Most defects found on this project surfaced from that
  question, not from a test run. If the fix is an instance of a class, say whether the class is
  closed and by what.

The report cannot open a turn — point 4 asks what the turn's own instructions dropped, and a
session does not hold them at the open.

## Committing

Commit your work to the current branch.

`CLAUDE.md` § Working style says development lands directly on `main`: this is a single-developer
repository with linear history and no long-lived feature branches. A session handed a different
working branch by its harness should fast-forward the change onto `main` when it is complete.
**Confirm with the user before doing that** — a harness that pinned the branch may have its own
reason, and the two instructions can genuinely conflict.
