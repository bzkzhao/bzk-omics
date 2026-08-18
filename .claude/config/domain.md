# Domain docs

How the vendored engineering skills consume this repo's domain documentation.

This repo does **not** use `CONTEXT.md` / `CONTEXT-MAP.md` / `docs/adr/`. Those are the upstream
defaults. The equivalents here already exist and are older and stricter than anything a skill
should invent.

## Before exploring, read these

`CLAUDE.md` is the router — it names which document governs a given change. Read it first, then:

- **`ONTOLOGY.md`** — node types, edge types, field semantics, invariants, the CURIE prefix map
  (§3), and the storage boundary (§2). **Normative.** Its DDL is not illustrative: code that
  diverges from it is wrong, or the document is wrong and must be amended *before* the code
  changes. Never reconcile silently in the code.
- **`GLOSSARY.md`** — definitions. This is the repo's glossary; it plays the role upstream assigns
  to `CONTEXT.md`.
- **`ARCHITECTURE.md`** — library and language choices, where data lives, module layout.
- **`decisions/`** — ADRs touching the area you are about to work in. Read
  `decisions/README.md` first; it carries the status convention and corrections that could not be
  made in place.
- **`VISION.md`** — scope and non-goals, when the question is whether something belongs at all.

All of these exist. If a skill's instructions tell you to proceed silently when a domain doc is
absent, that branch is dead here.

## Single context

This repo is single-context. Every upstream multi-context branch — `CONTEXT-MAP.md`, per-package
`CONTEXT.md`, `src/<context>/docs/adr/` — does not apply. Do not create them.

## Use the glossary's vocabulary

When your output names a domain concept, use the term as defined in `GLOSSARY.md` and typed in
`ONTOLOGY.md`. If the concept is not there, that is a signal: either you are inventing language the
project does not use, or there is a real gap. A real gap is recorded in a numbered `Open questions`
section in the file that should have contained the answer — see `.claude/config/issue-tracker.md`.

## Writing an ADR is a guarded operation

ADRs live in `decisions/NNNN-slug.md`, sequentially numbered. Read `decisions/README.md` before
writing one. Two rules bind:

- **An ADR lands as `Proposed`** and becomes `Accepted` only after a review round-trip completes.
  Do not land a record as `Accepted` to save a step; that asserts a review that did not happen.
- **Once `Accepted`, a record is append-only.** It is never edited. A changed decision gets a new
  record that supersedes the old, and both stay readable.

**Adding, removing, or restatusing an ADR is a test-guarded change.** `tests/test_decision_index.py`
checks three enumerations of ADR numbers against each other and against the directory, and pins
exact counts so a parser that stops matching fails loudly instead of comparing two empty sets. A new
ADR must move, in the same commit:

- the file in `decisions/`
- the **Written** table in `decisions/README.md`
- the **Queued** table in `decisions/README.md`, if the number was reserved there
- `ARCHITECTURE.md` §5's seed list, if the number is within its range
- the pinned constants in `tests/test_decision_index.py` — `EXPECTED_FILES`,
  `EXPECTED_WRITTEN_ROWS`, `EXPECTED_QUEUED_ROWS`, `EXPECTED_STATUSES`

Skip any of these and the suite goes red. Run `pytest tests/test_decision_index.py` before
claiming the ADR is written.

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0012 (the graph is derived, not authoritative) — but worth reopening because…_

Relitigating a settled choice without reading its ADR first is the failure `decisions/` exists to
prevent.

## Do not duplicate a fact

`CLAUDE.md` § Single source of truth assigns each fact exactly one home. Cross-reference; never
restate. Duplicating a fact into a second document is a defect, not redundancy — the copies diverge
within weeks and there is then no way to tell which is authoritative. This binds skill output as
much as hand-written prose.
