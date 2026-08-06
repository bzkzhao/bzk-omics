# CLAUDE.md

Router and working conventions for the bzk Omics repository. Read this first; it tells you which document governs the change you are making.

---

## What this project is

An open-source, local-first semantic layer that turns a researcher's experimental output into a queryable evidence graph. Anchor domain: cancer ubiquitinomics and ISGylation. Target user: independent researchers without enterprise software budgets.

Full rationale in `VISION.md`. Do not restate it elsewhere.

---

## Document map

| Read this | When you are |
|---|---|
| `VISION.md` | Deciding whether something is in scope, or why a design serves the user |
| `ONTOLOGY.md` | Adding or changing node types, edge types, fields, or invariants; writing ingestion, query, or export code |
| `ARCHITECTURE.md` | Choosing libraries, deciding where data lives, adding a module |
| `ROADMAP.md` | Asking what is being built now and what is deliberately deferred |
| `GLOSSARY.md` | Encountering an unfamiliar term |
| `decisions/NNNN-*.md` | Wondering why a settled choice was made, before relitigating it |

If a question is not answered by any of these, the answer does not yet exist. Ask rather than invent, and record the answer in the file that should have contained it.

---

## Single source of truth

Each fact has exactly one home. Cross-reference; never restate.

| Fact type | Home |
|---|---|
| Node types, edge types, field semantics, invariants | `ONTOLOGY.md` |
| CURIE prefix map | `ONTOLOGY.md` §3 |
| Storage boundary (graph vs columnar) | `ONTOLOGY.md` §2, elaborated in `ARCHITECTURE.md` |
| Library and language choices | `ARCHITECTURE.md` |
| Milestones, scope, deferrals | `ROADMAP.md` |
| Definitions | `GLOSSARY.md` |
| Positioning, user, non-goals | `VISION.md` |

Duplicating a fact into a second document is a defect, not redundancy. The copies diverge within weeks and there is then no way to tell which is authoritative.

---

## Conventions

**Documents carry a header block** — status, version, last reviewed, depends on, authoritative for. Update `last reviewed` when you touch a file.

**`ONTOLOGY.md` is normative.** Its DDL is not illustrative. Code that diverges from it is wrong, or the document is wrong and must be amended *before* the code changes. Never reconcile silently in the code.

**Decisions are append-only.** `decisions/0003-kuzu-over-neo4j.md` is superseded by a later ADR, never edited. This mirrors the product's own retraction model: a decision should die visibly.

**Invariants are errors, not warnings.** The invariants in `ONTOLOGY.md` §8 fail ingestion. Do not downgrade one to make a dataset load.

**Never assert what the data cannot support.** Invariants I3 and I10 are the product's core honesty claim, not niceties. If you find yourself writing code or copy that labels a K-GG site "ubiquitination" without a live non-ambiguous `ModifierAssignment`, or attributes a site to an enzyme without a live `EnzymeAssociation`, stop.

**Domain logic lives in subtypes.** Any code consuming the `Observation` or `EvidencedInference` contract must work for every subtype. An `isinstance` branch outside a subtype module is a defect — see `ONTOLOGY.md` §10.

**Generated values are never displayed as measurements.** Invariants I15 and I16. Imputed points, razor-picked proteins, and inferred experimental designs all carry their status. If a volcano plot cannot distinguish a measured point from an imputed one, it is wrong.

**Never discard the quantitative matrix.** Invariant I11. Computing a statistic does not license dropping the values it came from. This is what keeps the statistical layer pluggable.

**Never branch on pipeline metadata.** Invariant I13. `search_engine`, `acquisition_mode`, `library_type` and `test` are recorded data. A conditional on their value outside `adapters/` or the statistics registry is a defect.

**The graph is derived, not authoritative.** Invariant I9. Never create content that exists only inside `graph.kuzu/`; it must be regenerable from `raw/` plus the curation export. This is what keeps schema change cheap.

**Flag rather than hide.** Unprovenanced results, stoichiometry-uncorrected results, and ambiguous modifiers are displayed with their status, never suppressed and never silently promoted.

---

## Working style

- Prefer amending a document over adding one. The document set is deliberately small.
- Open questions live in a numbered `Open questions` section at the end of the relevant file, not in comments or issues.
- Real external identifiers only. Never invent a UniProt accession, PXD accession, or ontology term to fill an example — mark it synthetic or leave it blank.
