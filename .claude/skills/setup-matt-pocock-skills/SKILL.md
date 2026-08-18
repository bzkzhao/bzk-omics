---
name: setup-matt-pocock-skills
description: Re-configure this repo's engineering-skill settings — issue tracker, triage label vocabulary, and domain doc layout. Setup has already been run; use this only to change a setting or re-derive the config from scratch.
disable-model-invocation: true
---

# Setup

**This repo is already configured.** The config the engineering skills read lives in
`.claude/config/`:

| File | Holds |
|---|---|
| `.claude/config/issue-tracker.md` | Where issues, specs and tickets live |
| `.claude/config/triage-labels.md` | The five canonical triage roles and the strings used here |
| `.claude/config/domain.md` | Which domain documents to read, and the ADR guard |

Read them before running this skill. Run this skill only to **change** a setting, or to re-derive
the config after the repo's conventions move.

## What was decided, and why

Upstream's setup writes `CONTEXT.md`, `docs/adr/` and `docs/agents/*.md`. None of those were
created here. Each already has an older, stricter home:

| Upstream default | Home in this repo |
|---|---|
| `CONTEXT.md` | `GLOSSARY.md` — definitions; additive only |
| `docs/adr/` | `decisions/NNNN-*.md` — append-only once `Accepted`, index test-guarded |
| `docs/agents/*.md` | `.claude/config/*.md` |
| GitHub Issues | unused — `ROADMAP.md`, `HANDOFF.md` §8, and per-file `Open questions` sections |
| `CONTEXT-MAP.md`, per-context layout | not applicable — single context |

Creating the upstream files would put a second copy of a fact next to the first.
`CLAUDE.md` § Single source of truth calls that a defect, not redundancy: the copies diverge within
weeks and there is then no way to tell which is authoritative.

**The config files cross-reference; they do not restate.** `.claude/config/domain.md` names
`ONTOLOGY.md` as normative rather than summarising it. Keep it that way when you edit.

## Changing a setting

Edit the file in `.claude/config/` directly. That is the whole procedure — no skill run is needed
for an ordinary change, and the skills read the files fresh each time.

Re-run this skill only when a change is structural: adopting an issue tracker, splitting the repo
into multiple contexts, or moving where ADRs live. In that case:

1. **Explore.** Read `CLAUDE.md` (the router), the three files in `.claude/config/`, and whatever
   the change touches. Read `decisions/README.md` if ADR handling is in scope.
2. **Confirm.** Show the user a diff of what each config file would become. Let them edit before
   you write.
3. **Write.** Update `.claude/config/`. If the structural change is itself hard to reverse and was
   a real trade-off, it wants an ADR — see `domain-modeling`'s
   [ADR-FORMAT.md](../domain-modeling/ADR-FORMAT.md), and note that writing one is a multi-file,
   test-guarded change.
4. **Check.** Run `pytest` and report the result. A structural change to where decisions live can
   move `tests/test_decision_index.py`.

## Do not add an `## Agent skills` block to CLAUDE.md

Upstream's setup appends one, summarising the three config files. Here that would restate
`.claude/config/` inside `CLAUDE.md` — the same duplication the config avoided. `CLAUDE.md` is the
router; it points at documents, and `.claude/config/` points at it. The direction is deliberate:
the config depends on the repo's documents, not the other way round.
