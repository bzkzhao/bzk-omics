# Prompt 25 — Land ADR-0036 (Proposed) and verify its claims against the repository

**Repository:** `main` at the commit adding this prompt and the draft, directly on top of `a74cf18`.
**Governing:** `notes/REVIEWER-HANDOFF-2026-10-02.md` §2.1 and §7.2; the draft
`notes/drafts/0036-ip-ms-as-role-tagged-observations.md`.

This prompt **lands a record and measures**. It makes **no change** to `ONTOLOGY.md`,
`bzk/ontology/schema.py`, anything under `bzk/`, `tests/`, `ROADMAP.md` or `HANDOFF.md`. The record's
*Implied changes* section stays described and not made. The prompt ends at the report.

---

## 0. Receipt check — answer all of these, then stop and wait

1. **Repository state.** Run `git log --oneline -2` and `git status --short`.
   - HEAD must be this prompt's commit, with `a74cf18` beneath it.
   - The only untracked path allowed is `notes/prompts/22-walk-two-route-independence.md`.
   - If either check fails, stop.
2. **Draft citations.** Quote these verbatim, each with its line number:
   - `ONTOLOGY.md` l.119 (the `Contrast` identity row);
   - `ONTOLOGY.md` l.670 (the `isg15_interactome_concordance` row);
   - the first sentence of `ONTOLOGY.md` l.684.
   If any of the three is not at that line, say where it is now.
3. **Schema.** Quote `bzk/ontology/schema.py` l.274 and l.329–341 verbatim.
4. **Cold rebuild.**
   - Name the command that performs a cold rebuild of the graph, and the file or output where it
     reports node counts by label.
   - Say whether that command can run in this container. The raw store `~/.bzk-omics/raw/` is not
     here.
   - If it cannot run here, say so. Do not attempt a partial build.

**Do not start §1 until bzk replies.**

---

## 1. Land the record

1. Copy the draft to `decisions/0036-ip-ms-as-role-tagged-observations.md`.
   - If 0036 is taken, use the next free number and change only the number. Record the change
     under a *Landing verification* heading.
2. Set Status to `Proposed`, per `decisions/README.md`.
3. Make no other edit to the decision text. Corrections go under *Landing verification* (§2),
   each one with the check that forced it. Struck rather than deleted, as in ADR-0035.

## 2. Landing verification — measure, do not inherit

Append a `## Landing verification` section to the landed record. It holds one entry per item
below. Each entry gives the command, the output (verbatim, or its tail where long) and a verdict:
**holds**, **corrected** (with the correction) or **not measurable here** (with the reason).

| # | Claim in the draft | Measure |
|---|---|---|
| V1 | Every `ONTOLOGY.md` / `schema.py` / `differential.py` / `perseus.py` / `query/graph.py` / `curation_PXD018299.json` / `ROADMAP.md` / `HANDOFF.md` / ADR-0013 line reference | Re-read each at HEAD. List any that moved |
| V2 | No node type anchors on `Sample` | Every `anchors=` entry in `schema.py`. Print the full list of (label, anchor label) pairs |
| V3 | `DifferentialResult` anchors on `Contrast`. `ModifierAssignment` anchors on neither `Sample` nor `Contrast` | From V2's list |
| V4 | Re-mint scope | Node counts for `Sample`, `Contrast`, `DifferentialResult` after a cold rebuild. **If §0.4 says it cannot run here, write the exact command for bzk's Mac and mark not measurable here.** Do not substitute counts from any document |
| V5 | Ids are cited by nothing outside the graph (ADR-0025's premise, re-measured) | Find every `bzk:` + 32-hex string in tracked files (`git grep -nE 'bzk:[0-9a-f]{32}'`). Report the count per file. For each, say whether it is a `Sample`, `Contrast` or `DifferentialResult` id where determinable without a rebuild. Otherwise say "type undetermined" |
| V6 | `n_imputed` consumers | `git grep -nw n_imputed`. Report the files and the count. Confirm that `row_carries_an_imputed_cell` is not matched |
| V7 | Nothing in `bzk/` or `tests/` names `isg15_interactome_concordance` | `git grep -n isg15_interactome_concordance -- bzk tests` |
| V8 | `EnrichmentObservation` homes: `ONTOLOGY.md` l.539, l.684, l.1061; `ROADMAP.md` l.117, l.139; `HANDOFF.md` l.1326; ADR-0013 l.18, l.72; the reviewer handoff | `git grep -n EnrichmentObservation`. Report any home the draft omits |
| V9 | `protein_adjusted` is already set on protein results | Quote `bzk/adapters/perseus.py` l.540–546 |
| V10 | PXD018299's matching proteome is not keyed to any `Sample` | Quote the sentence in `ROADMAP.md` l.68 that says so, with only the clause needed |

**Blindness.** No gene name, accession or per-row value is printed by any step.

## 3. Out of scope — carried, not touched

- **Defect:** `bzk/sources/protein_groups.py:117` mislabels SD3.
- **Defect:** `tests/test_tautology_sweep.py`'s minimum counts are stale.
- Walk line `b960c9a` and prompt 22.
- The PI's imputation question (PXD055843 S1_TP and S3).
- **The paper's 312 against SD3's 323 rows.** This is for the pre-registration step, not this one.
- Any `ONTOLOGY.md`, schema or code change implied by the record.

## 4. Report

Report the following, then stop:

1. The landed path and its commit.
2. V1–V10 as a table: claim, verdict, one line of evidence.
3. Every correction made under *Landing verification*.
4. Anything the draft asserts that §2 did not reach.
