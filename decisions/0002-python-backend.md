# ADR-0002 — Python for the backend

| | |
|---|---|
| Status | Accepted |
| Date | 2026-08-06 |
| Supersedes | — |
| Superseded by | — |

## Context

The author's existing programming experience is in web development — HTML, CSS, JavaScript. Choosing TypeScript throughout would let one language cover both backend and frontend and would play to that strength.

The work, however, is proteomics: parsing search-engine output, resolving UniProt accessions, handling mzML and mzTab, computing moderated statistics over sparse matrices.

## Decision

Python 3.12 for the backend, packaged with `uv`, served by FastAPI. TypeScript for the frontend only.

## Consequences

**Positive.** `pyteomics` and `pyopenms` handle mass-spectrometry formats; `polars` handles wide quantitative tables with predictable memory; the empirical Bayes literature has reference implementations to check against. None of these has a mature TypeScript equivalent. FastAPI generates an OpenAPI schema, so the frontend gets typed clients without hand-written glue.

**Negative.** Two languages to maintain. The author must learn Python, which is a real cost against a compressed timeline.

**Accepted cost.** Reimplementing tested proteomics primitives in TypeScript would consume more time than learning Python, and would produce code with no community to check it against.

## Alternatives considered

**TypeScript throughout (Node or Bun).** Rejected on ecosystem grounds. The saving in language count does not offset reimplementing mzML parsing and statistical routines.

**R.** Strong for the statistics — `limma` is the reference implementation of the moderated *t*-test — but weak for building an application, and an R dependency breaks the one-afternoon install promise in `VISION.md`. Revisited and rejected again in ADR-0011.
