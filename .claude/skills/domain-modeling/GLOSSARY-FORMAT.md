# Glossary format

`GLOSSARY.md` at the repo root is the home for definitions. It already exists and already has a
format — match it rather than imposing one.

## Header block

Every document in this repo carries a header block. `GLOSSARY.md`'s declares it authoritative for
*"Definitions of terms used across all documents"*. **Update `Last reviewed` when you touch the
file**, per `CLAUDE.md` § Conventions.

## Entry format

Terms are grouped under `##` category headings — currently Biology, Mass spectrometry, and others.
One term per line:

```md
**Term** — Definition in one or two sentences. Real identifiers in backticks (`uniprot:P05161`).
```

Rules that bind:

- **Additive only.** Terms are added, not removed. A definition that turns out wrong is corrected
  in place; a term that falls out of use stays.
- **This file wins.** Where a definition here conflicts with usage elsewhere, the glossary is
  right and the other document is corrected.
- **Real external identifiers only.** Never invent a UniProt accession, PXD accession, or ontology
  term to fill an example. Mark it synthetic or leave it blank — `CLAUDE.md` § Working style.
- **No implementation details.** This is a glossary and nothing else. Not a spec, not a scratch
  pad, not a home for decisions. Field semantics and invariants belong in `ONTOLOGY.md`; decisions
  belong in `decisions/`.

## What does not go here

| Tempting to put here | Actual home |
|---|---|
| A term's type, fields, or invariants | `ONTOLOGY.md` §4–§8 |
| The CURIE prefix map | `ONTOLOGY.md` §3 |
| Why a modelling choice was made | `decisions/NNNN-*.md` |
| Whether a term is in scope at all | `VISION.md` |

Restating any of these here creates a second copy that diverges within weeks. `CLAUDE.md` calls
that a defect, not redundancy.

## Single context

This repo has one context. There is no `CONTEXT-MAP.md` and no per-package glossary. Do not
create either.
