---
name: code-review
description: Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes — Standards (does the code follow this repo's documented coding standards?) and Spec (does the code match what the originating issue/spec asked for?). Runs both reviews in parallel sub-agents and reports them side by side. Use when the user wants to review a branch, a PR, work-in-progress changes, or asks to "review since X".
---

Two-axis review of the diff between `HEAD` and a fixed point the user supplies:

- **Standards** — does the code conform to this repo's documented coding standards?
- **Spec** — does the code faithfully implement the originating issue / spec?

Both axes run as **parallel sub-agents** so they don't pollute each other's context, then this skill aggregates their findings.

Where specs and tickets live is recorded in `.claude/config/issue-tracker.md`. Read it first.

## Process

### 1. Pin the fixed point

Whatever the user said is the fixed point — a commit SHA, branch name, tag, `main`, `HEAD~5`, etc. If they didn't specify one, ask for it.

Capture the diff command once: `git diff <fixed-point>...HEAD` (three-dot, so the comparison is against the merge-base). Also note the list of commits via `git log <fixed-point>..HEAD --oneline`.

Before going further, confirm the fixed point resolves (`git rev-parse <fixed-point>`) and the diff is non-empty. A bad ref or empty diff should fail here — not inside two parallel sub-agents.

### 2. Identify the spec source

Look for the originating spec, in this order:

1. Issue references in the commit messages (`#123`, `Closes #45`, GitLab `!67`, etc.) — fetch via the workflow in `.claude/config/issue-tracker.md`.
2. A path the user passed as an argument.
3. A spec file under `docs/`, `specs/`, or `.scratch/` matching the branch name or feature.
4. If nothing is found, ask the user where the spec is. If they say there isn't one, the **Spec** sub-agent will skip and report "no spec available".

### 3. Identify the standards sources

This repo documents how code should be written across several files. `CLAUDE.md` is the router
and names which one governs a given change. Pass the sub-agent whichever of these the diff touches:

| Source | Authoritative for |
|---|---|
| `CLAUDE.md` § Conventions | The working rules below, and the four-point verification report |
| `ONTOLOGY.md` | Node/edge types, field semantics, invariants (§8), CURIE prefixes (§3), storage boundary (§2) |
| `ARCHITECTURE.md` | Library and language choices, where data lives, module layout |
| `OPERATIONS.md` | Backup, cache policy, dependency pinning, testing |
| `decisions/NNNN-*.md` | Why a settled choice was made — read before flagging it as wrong |
| `VISION.md` | Positioning and non-goals |

**These are hard violations, not judgement calls.** Each is a documented rule in `CLAUDE.md`
§ Conventions, and each has a defect it was written in response to. Check the diff against every
one that applies:

- **Code diverging from `ONTOLOGY.md`'s DDL is wrong** — or the document is wrong and must be
  amended *before* the code changes. Silent reconciliation in the code is the violation.
- **An invariant downgraded to a warning to make a dataset load** (`ONTOLOGY.md` §8).
- **A K-GG site labelled "ubiquitination" without a live non-ambiguous `ModifierAssignment`**, or a
  site attributed to an enzyme without a live `EnzymeAssociation` — I3 and I10, the product's core
  honesty claim.
- **An `isinstance` branch on `Observation` or `EvidencedInference` outside a subtype module** —
  §10. Domain logic lives in subtypes.
- **A conditional on `search_engine`, `acquisition_mode`, `library_type` or `test` outside
  `adapters/` or the statistics registry** — I13. That metadata is recorded data, not a switch.
- **A generated value displayed as a measurement** — I15 and I16. Imputed points, razor-picked
  proteins and inferred designs carry their status.
- **The quantitative matrix discarded after computing a statistic** — I11.
- **Content that exists only inside `graph.kuzu/`** — I9. The graph is derived and must be
  regenerable from `raw/` plus the curation export.
- **A fact restated in a second document** rather than cross-referenced — § Single source of truth.
- **An `Accepted` ADR edited in place** rather than superseded by a new record.
- **An invented UniProt accession, PXD accession, or ontology term** in an example or fixture.
- **A new mirror between two sources with no test guarding it.** Every existing mirror here is
  guarded; prose in `HANDOFF.md` §8 does not close a machine-checkable class.
- **Copy positioning the platform as an alternative to Perseus or the search engines** — they are
  inputs, not competitors (`VISION.md` § Positioning).

A documented repo standard always wins over the smell baseline below.

On top of whatever the repo documents, the Standards axis always carries the **smell baseline** below — a fixed set of Fowler code smells (_Refactoring_, ch.3) that applies even when a repo documents nothing. Two rules bind it:

- **The repo overrides.** A documented repo standard always wins; where it endorses something the baseline would flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"), never a hard violation — and, like any standard here, skip anything tooling already enforces.

Each smell reads *what it is* → *how to fix*; match it against the diff:

- **Mysterious Name** — a function, variable, or type whose name doesn't reveal what it does or holds. → rename it; if no honest name comes, the design's murky.
- **Duplicated Code** — the same logic shape appears in more than one hunk or file in the change. → extract the shared shape, call it from both.
- **Feature Envy** — a method that reaches into another object's data more than its own. → move the method onto the data it envies.
- **Data Clumps** — the same few fields or params keep travelling together (a type wanting to be born). → bundle them into one type, pass that.
- **Primitive Obsession** — a primitive or string standing in for a domain concept that deserves its own type. → give the concept its own small type.
- **Repeated Switches** — the same `switch`/`if`-cascade on the same type recurs across the change. → replace with polymorphism, or one map both sites share.
- **Shotgun Surgery** — one logical change forces scattered edits across many files in the diff. → gather what changes together into one module.
- **Divergent Change** — one file or module is edited for several unrelated reasons. → split so each module changes for one reason.
- **Speculative Generality** — abstraction, parameters, or hooks added for needs the spec doesn't have. → delete it; inline back until a real need shows.
- **Message Chains** — long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the walk behind one method on the first object.
- **Middle Man** — a class or function that mostly just delegates onward. → cut it, call the real target direct.
- **Refused Bequest** — a subclass or implementer that ignores or overrides most of what it inherits. → drop the inheritance, use composition.

### 4. Spawn both sub-agents in parallel

**Standards sub-agent prompt** — include:

- The full diff command and commit list.
- The list of standards-source files you found in step 3, **plus the smell baseline from step 3** pasted in full — the sub-agent has no other access to it.
- The brief: "Report — per file/hunk where relevant — (a) every place the diff violates a documented standard: cite the standard (file + the rule); and (b) any baseline smell you spot: name it and quote the hunk. Distinguish hard violations from judgement calls — documented-standard breaches can be hard, but baseline smells are always judgement calls, and a documented repo standard overrides the baseline. Skip anything tooling enforces. Under 400 words."

**Spec sub-agent prompt** — include:

- The diff command and commit list.
- The path or fetched contents of the spec.
- The brief: "Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong. Quote the spec line for each finding. Under 400 words."

If the spec is missing, skip the Spec sub-agent and note this in the final report.

### 5. Aggregate

Present the two reports under `## Standards` and `## Spec` headings, verbatim or lightly cleaned. Do **not** merge or rerank findings — the two axes are deliberately separate (see _Why two axes_).

End with a one-line summary: total findings per axis, and the worst issue _within each axis_ (if any). Don't pick a single winner across axes — that's the reranking the separation exists to prevent.

## Why two axes

A change can pass one axis and fail the other:

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the issue asked but breaks the project's conventions → **Spec pass, Standards fail.**

Reporting them separately stops one axis from masking the other.

## Report the checks, don't infer them

Neither sub-agent runs the suite. Before presenting the two reports, run the checks yourself and
name each at its actual result with its target stated:

```bash
uv run pytest
uv run pytest tests/test_schema.py
uv run ruff check bzk tests
uv run ruff format --check bzk tests
uv run mypy bzk tests
```

A check not run is reported as not run — silence is not a pass, and "lint clean" without naming
which of the three it covered is the same defect one level in. `ruff check .` additionally covers
the three `colab_*.ipynb` notebooks, which are permanently out of scope: they are records of
experiments, not maintained source.

Green tests have twice been consistent with a real defect here — four invariant checks passing
vacuously (ADR-0019), and `test_rebuild` asserting a count against its own source. If the diff adds
a guard, say whether it has been made to fail and whether the mutation was confirmed to have
applied.

When the reviewed change touches a critical node, the turn closes with the full four-point report
in `CLAUDE.md` § Working style.
