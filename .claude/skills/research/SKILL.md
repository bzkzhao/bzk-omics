---
name: research
description: Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent.
---

Spin up a **background agent** to do the research, so you keep working while it reads.

Its job:

1. Investigate the question against **primary sources** — official docs, source code, specs, first-party APIs — not a secondary write-up of them. Follow every claim back to the source that owns it.
2. Write the findings to a single Markdown file, citing each claim's source.
3. Save it to `.scratch/research/<slug>.md` — gitignored working space, per
   `.claude/config/issue-tracker.md`. Tell the user the path.

**Nothing durable may live only in `.scratch/`.** When a finding settles, it belongs in the
document that owns that fact: `ROADMAP.md` for scope, `HANDOFF.md` §8 for an item with a trigger,
`GLOSSARY.md` for a definition, an `Open questions` section for a question that survives. Say which
one, and offer to make the edit — do not promote silently.

**Real external identifiers only.** Never invent a UniProt accession, PXD accession, or ontology
term to fill a gap in the findings; mark it synthetic or leave it blank. For this project's
domain, the primary sources are UniProt, PRIDE, and the published methods — not a secondary
write-up of them.
