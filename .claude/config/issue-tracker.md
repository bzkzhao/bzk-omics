# Issue tracker

Where issues, specs and tickets live for this repo. `to-spec`, `to-tickets`, `triage`,
`wayfinder` and `code-review` read this file.

## This repo does not use GitHub Issues

The remote is `bzkzhao/bzk-omics` on GitHub, but the issue tracker is unused and single-developer
work is not tracked there. Do not open GitHub issues, and do not tell the user to. Do not run
`gh issue create`.

## Durable work is tracked in the documents

Three homes, each authoritative for one kind of thing. These are the real tracker:

| What | Home |
|---|---|
| Milestones, scope, deliberate deferrals | `ROADMAP.md` § Milestones, § Beyond v0.1 |
| Open items carried into implementation, each with a trigger | `HANDOFF.md` §8 |
| An unanswered question about one document's subject | a numbered `## Open questions` section at the end of that document |

`CLAUDE.md` § Working style states the rule directly: open questions live in a numbered
`Open questions` section at the end of the relevant file, **not in comments or issues**. Existing
sections are in `ARCHITECTURE.md`, `ONTOLOGY.md` §11, `OPERATIONS.md` and `ROADMAP.md`.

**A note in `HANDOFF.md` §8 does not close a machine-checkable class.** If the assertion can be
written, write it; the note then records a trigger a guard already enforces rather than one a
reader must remember. See `CLAUDE.md`, point 3 of the verification report.

## Ephemeral agent working files: `.scratch/`

Specs and tickets a skill generates mid-flow go under `.scratch/`, which is gitignored.

- One effort per directory: `.scratch/<slug>/`
- The spec is `.scratch/<slug>/spec.md`
- Tickets are one file per ticket at `.scratch/<slug>/issues/<NN>-<slug>.md`, numbered from `01` —
  never a single combined tickets file
- Triage state is a `Status:` line near the top of each ticket file (see `triage-labels.md`)
- Comments append at the bottom under a `## Comments` heading

**Nothing durable may live only in `.scratch/`.** It is uncommitted and the container it lives in
is reclaimed. When a spec settles into scope, it belongs in `ROADMAP.md`; when a ticket becomes an
item with a trigger, it belongs in `HANDOFF.md` §8; when a question survives the session, it
belongs in an `Open questions` section. `.scratch/` is where work is staged, not where it is kept.

This mirrors invariant I9 as applied to prose: the scratch directory is derived, and must be
regenerable from the committed documents plus the conversation.

## When a skill says "publish to the issue tracker"

Write the file under `.scratch/<slug>/`, then tell the user which durable document it should be
promoted into, and offer to make that edit. Do not promote silently — `ROADMAP.md` and
`HANDOFF.md` are hand-maintained.

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path directly. If they name
a milestone or an open item instead, read it from `ROADMAP.md` or `HANDOFF.md` §8.

## Wayfinding operations

Used by `wayfinder`. The **map** is a file with one **child** file per ticket.

- **Map**: `.scratch/<effort>/map.md` — the Notes / Decisions-so-far / Fog body.
- **Child ticket**: `.scratch/<effort>/issues/NN-<slug>.md`, numbered from `01`, with the question
  in the body. A `Type:` line records the ticket type (`research`/`prototype`/`grilling`/`task`);
  a `Status:` line records `claimed`/`resolved`.
- **Blocking**: a `Blocked by: NN, NN` line near the top. A ticket is unblocked when every file it
  lists is `resolved`.
- **Frontier**: scan `.scratch/<effort>/issues/` for files that are open, unblocked and unclaimed;
  first by number wins.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: append the answer under an `## Answer` heading, set `Status: resolved`, then append
  a context pointer to the map's Decisions-so-far in `map.md`.

## PRs as a request surface

Off. This is a single-developer repository; external PRs are not part of the triage queue.
