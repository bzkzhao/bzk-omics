# Vendored agent skills

| Field | Value |
|---|---|
| Status | Active |
| Version | 1.0 |
| Last reviewed | 2026-08-18 |
| Depends on | `CLAUDE.md`, `.claude/config/` |
| Authoritative for | Which skills are installed, what was changed from upstream, and why |

Twenty-six skills from [mattpocock/skills](https://github.com/mattpocock/skills), vendored and
adapted to this repository.

**Upstream:** `9c9f36ccd3995266cd675468af71639c8dde1ec5`, package version `1.2.3`, 2026-08-17.
**Licence:** MIT — `LICENSE.upstream`, copyright Matt Pocock. Adaptations inherit it.

---

## Why vendored rather than installed as a plugin

Upstream offers two routes. `claude plugins install mattpocock-skills` subscribes to a managed,
read-only bundle that updates when upstream ships. `npx skills@latest add mattpocock/skills` copies
editable files you own. **Installing both leaves every skill present twice** — pick one, and this
repo has picked vendoring.

Two reasons:

1. **The upstream defaults would break this repo.** `domain-modeling` writes ADRs into `docs/adr/`.
   Here ADRs live in `decisions/` and `tests/test_decision_index.py` pins exact counts across three
   enumerations. An unadapted skill writing a record turns the suite red. `setup-matt-pocock-skills`
   creates `CONTEXT.md` and `docs/agents/` beside the existing `GLOSSARY.md` and `ONTOLOGY.md` —
   a second copy of a fact, which `CLAUDE.md` § Single source of truth calls a defect.
2. **A read-only bundle cannot be corrected.** The adaptations below are not preferences; several
   are the difference between a skill that works here and one that files a false report.

The cost is real and is accepted: **these files do not update when upstream ships.** Re-vendoring
is a manual diff against the commit named above.

---

## Configuration

The skills read three files in `.claude/config/`, written for this repo:

| File | Holds |
|---|---|
| `issue-tracker.md` | GitHub Issues is unused; durable work lives in `ROADMAP.md`, `HANDOFF.md` §8, and per-file `Open questions` sections; `.scratch/` is ephemeral |
| `triage-labels.md` | The five canonical roles as `Status:` strings, plus the repo's `ready-for-agent` bar |
| `domain.md` | Which documents to read, and the ADR guard checklist |

They **cross-reference and do not restate**. `domain.md` names `ONTOLOGY.md` as normative rather
than summarising it. Keep it that way when editing: a summary is a second copy that diverges.

Setup has already been run. Change a setting by editing the file directly — no skill run needed.

---

## What was changed from upstream

**Paths, everywhere.** `CONTEXT.md` → `GLOSSARY.md`. `docs/adr/` → `decisions/`.
`docs/agents/` → `.claude/config/`. Multi-context branches (`CONTEXT-MAP.md`, per-package
glossaries, per-context ADR directories) removed — this repo is single-context.

**Toolchain, everywhere.** npm/pnpm, vitest/jest, `tsc`, Prettier and ESLint replaced with
`uv run pytest`, `uv run ruff check bzk tests`, `uv run ruff format --check bzk tests`,
`uv run mypy bzk tests`. All TypeScript examples rewritten in Python. The stated targets are part
of the instruction: `ruff check .` additionally covers the three `colab_*.ipynb` notebooks, which
are **deliberately and permanently out of scope** — records of experiments, not maintained source.

**Per skill:**

| Skill | Change |
|---|---|
| `setup-matt-pocock-skills` | Rewritten. Its five seed templates were deleted — `.claude/config/` is now the single home for that config, and keeping both would be the duplication the config exists to avoid. It no longer appends an `## Agent skills` block to `CLAUDE.md`, for the same reason. |
| `domain-modeling` | `CONTEXT-FORMAT.md` → `GLOSSARY-FORMAT.md`, rewritten for the repo's additive-only glossary. `ADR-FORMAT.md` rewritten for `decisions/`: `Proposed` → review → `Accepted`, append-only once accepted, and the five-surface checklist a new record must move in one commit. |
| `code-review` | Standards axis now names the repo's normative documents, and carries thirteen **hard** violations drawn from `CLAUDE.md` § Conventions and `ONTOLOGY.md` §8 — I3, I9, I10, I11, I13, I15/I16, subtype dispatch, silent DDL divergence, restated facts, edited ADRs, invented identifiers, unguarded mirrors, Perseus positioning. Closes by running and naming the checks. |
| `tdd` | Examples in pytest. Carries the repo's two recorded green-suite failures — the vacuous invariant checks of ADR-0019, and `test_rebuild` asserting a count against its own source — and the 2026-08-07 mutation that silently did not apply. `mocking.md` prefers real temporary Kùzu/DuckDB stores over mocks. |
| `implement` | Repo check commands; `ONTOLOGY.md` amended before code, never reconciled silently; closes with the four-point report. |
| `resolving-merge-conflicts` | Repo checks; regenerate `uv.lock` rather than hand-merge; run the mirror guards specifically after a conflict resolution. |
| `codebase-design`, `writing-for-agents`, `triage` | Examples and environment references converted to Python/uv. |
| `teach` | **Scoped away from the repo root.** It writes `MISSION.md`, `RESOURCES.md`, `GLOSSARY.md`, `NOTES.md`, `learning-records/` and `lessons/` into its workspace — run here unmodified it would overwrite this project's authoritative `GLOSSARY.md`. It now asks for a path outside the repo, or uses `.scratch/teach/`. |
| `research` | Output pinned to `.scratch/research/<slug>.md` instead of "somewhere sensible", with the promotion rule and the no-invented-identifiers rule. |
| `prototype` | Output pinned to `.scratch/prototypes/`; upstream's "locate it next to the module it prototypes for" would have put throwaway code into `bzk/`, where `ruff`, `mypy` and the suite pick it up. |

**The four-point verification report is referenced, never restated.** `CLAUDE.md` § Working style
is its only home. `implement`, `tdd` and `code-review` point at it.

---

## What was not taken, and why

Nine of the thirty-five upstream skills:

- **TypeScript/npm-specific, no meaning here** — `migrate-to-shoehorn` (`as` assertions →
  `@total-typescript/shoehorn`), `setup-ts-deep-modules` (dependency-cruiser),
  `setup-pre-commit` (Husky + lint-staged + Prettier).
- **Course authoring, unrelated to this project** — `scaffold-exercises`.
- **Marked in-progress upstream** — `claude-handoff`, `loop-me`, `writing-beats`,
  `writing-fragments`, `writing-shape`. `handoff` (the settled one) *was* taken.

The Codex `agents/openai.yaml` file was dropped from every skill — this repo drives Claude Code.

---

## Two things to know before using these

**`code-review` shadows a built-in.** Claude Code ships a `code-review` skill with `--fix` and
`--comment`; this project-level skill has the same name and takes precedence here. They are
genuinely different: the built-in hunts correctness bugs and cleanups, the vendored one runs
Standards and Spec as parallel sub-agents and refuses to rank findings across the two axes. To get
the built-in back, rename or delete this directory.

**`git-guardrails-claude-code` is vendored but not installed.** Running it writes a Claude Code
hook that blocks `git push`, `git reset --hard`, `git clean -f`, `git branch -D` and others before
they execute. That is the point of it — but it will also block an agent session that has been told
to push to a working branch. Install it deliberately, not incidentally.

---

## Where the repo's own rules still win

These skills are generic engineering advice. `CLAUDE.md` is not. Where they disagree, `CLAUDE.md`
governs — it is the router, and the skills are downstream of it. Three specific collisions are
already resolved in the adapted text:

- Upstream creates domain docs lazily when absent. Here they exist, and are older and stricter.
- Upstream treats an ADR as one file. Here it is a five-surface, test-guarded change.
- Upstream's `implement` commits to the current branch. `CLAUDE.md` § Working style lands
  development on `main`; the adapted skill asks before fast-forwarding, because a harness that
  pinned a branch may have its own reason.
