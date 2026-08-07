# CLAUDE.md

| Field | Value |
|---|---|
| Status | Active |
| Version | 1.5 |
| Last reviewed | 2026-08-07 |
| Authoritative for | Document routing, working conventions |

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
| `OPERATIONS.md` | Touching backup, the cache, a dependency version, or writing tests |
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
| Backup, cache policy, pinning, testing | `OPERATIONS.md` |
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

**Build for the anchor laboratory, not for a market.** When scope is ambiguous, the question is whether the Pinto-Fernández group needs it for their own data. Generality that costs nothing — contracts, registries, closed enums — is kept. Generality that costs weeks is deferred until someone asks.

**Tests before code, invariants before adapters.** The invariant suite is written first and fails first. An adapter that ingests data while violating I3 or I14 is worse than no adapter.

**The platform is downstream, not a replacement.** Perseus and the search engines are inputs. Never write code or copy that positions bzk Omics as an alternative to them — see `VISION.md` § Positioning.

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
- Commit to `main`. This is a single-developer repository with linear history; development lands directly on `main`, not on long-lived feature branches. A session handed a different working branch by its harness should fast-forward the change onto `main` when it is complete, and continue there.
- **Verify at every critical node — as the closing act of the turn that reaches it.** A critical node is any `ONTOLOGY.md` amendment, any new ADR, the key builder, each adapter, and anything touching the export boundary (I18). The four-point report **closes** such a turn; it cannot open one. A session starting a turn — and especially one resumed after a compaction — does not hold the previous turn's instructions, so point 4 is unrecoverable at the open; that is how the `RESULT_FOR_PROTEIN` fixture fix was lost. Points 1 and 2 are also cheapest while the context that produced the change is still fresh. Before ending the turn, report all four explicitly:
  1. Every check run and reported by name, at its actual result, **with its target stated**: `pytest` (full suite) and `pytest tests/test_schema.py`; `ruff check bzk tests`; `ruff format --check bzk tests`; `mypy bzk`. **A check not run is reported as not run** — silence is not a pass, and neither is "lint clean" without naming which of the three it covered. The targets are part of the rule because they are not the whole repository: `ruff check .` additionally covers the three notebooks and `mypy bzk tests` additionally covers `tests/`, and both were failing at the time this was written (18 and 36 respectively). A report saying "zero" against an unstated target is the same defect as saying nothing, one level in — so state the target or state the wider number. An earlier draft of this point named pytest and `tests/test_schema.py` only; `ruff` and `mypy` had been reported voluntarily until then, and stopped being reported the moment the protocol stopped asking. Eight commits of decay followed — six `FURB167`, five unformatted files and a real `mypy` error accrued without one report being false, because none of them mentioned lint at all. The narrow standard is what let it through, so the checks are enumerated here rather than left to judgement.
  2. The change did what it claimed, checked directly rather than inferred from a passing suite. Green tests have twice been consistent with a real defect here: four invariant checks passed vacuously while fully tested (ADR-0019), and `test_rebuild` asserted a table count against its own source.
  3. What the change did **not** cover, stated plainly. Most defects found on this project surfaced from that question, not from a test run.
  4. Any instruction from the turn that was dropped or partially done.

  A turn spent verifying is cheaper than an ADR that supersedes another.
- **At the open of a turn, verify only what the open can support:** that the suite is green on the state you inherited, and that any items left outstanding by the previous turn are picked up. The full four-point report — point 4 in particular — belongs at the close, where the turn's own instructions are still in hand.
