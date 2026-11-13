# REVIEWER DEFECTS — the register

**This file is the home of the reviewer's defect list.** Until now the list lived only inside
prompt 22's "Out of scope. Do not touch." section (`notes/prompts/22-walk-two-route-independence.md:145-181`).
That prompt reviewed commit `3a165a4` (2026-09-22). The prompt file itself entered the repository in
`4c88e9a` (2026-11-06). Items 3 and 12 both land on FINDINGS §5, and two consecutive prompts missed
them because the list sat in a section that tells the reader not to look. The handoff of
2026-11-12 (§6 item 4) names this as the proximate cause of three failures in one session.

**Rules for this file.**
- A prompt's out-of-scope section cites items **by number and points here**. It does not copy them.
  A copy is a second home (`CLAUDE.md:40`).
- The reviewer edits this file. A build session that finds an entry wrong **raises it and does not
  edit it**. That is the rule prompt 42b set for the reviewer map
  (`notes/prompts/42b-the-notes-name-their-instruments.md:673-674`), applied here.
- Closing an item records the closing commit. Items are never renumbered or deleted.
- Each status below was measured at `74acd53` on 2026-11-13. "Unchanged" means the cited file has no
  commit since `3a165a4`, so the item's original line references still hold.

**Numbering.** W*n* is prompt 22's `walk/` item *n*. P1–P9 and D30 keep prompt 22's numbers. Items
in §4 are new here. The reviewer map's D1 heading and prompt 42b:671 cite the old form, "item 3 of
prompt 22:149", which is W3.

**Item 1 is not missing.** The handoff of 2026-11-12 noted that the `walk/` list starts at 2.
Prompt 22 *is* item 1: its title reads "walk/ item 1. Withdraw 'two routes sharing no inputs'".

---

## 1. The `walk/` list (W1–W12)

Each item's text is prompt 22's, verbatim, except W1, which prompt 22 states as its own subject.

| # | item, as written at `3a165a4` | status at `74acd53` |
|---|---|---|
| W1 | (prompt 22's subject) Withdraw "two routes sharing no inputs". | **Closed** by `b960c9a` (2026-09-27): correction and banner. Its subject reads "FINDINGS §2 and :110 restated". |
| W2 | Check 2's knockout columns (down 1.39–1.51) and the "noisy" reading at imputation-effects.md:78–80. Do not add knockout figures, conditionality or reference-population caveats to FINDINGS §2 or :110. Do not change :110's "yes". | **Open.** `imputation-effects.md` is unchanged, and `:78-80` still reads "The knockout columns are noisy and are not read into". **FINDINGS line moved:** ":110's 'yes'" is the "imputation model \| **yes**" row, at `:110` at `3a165a4` and at **`:118`** now. `b960c9a` (W1) restated that row's "why" cell from "twice" to "(§2)". The "yes" stands. |
| W3 | The headline estimand: 27.8% (registered, PREREG-PXD018299-H10.md §6B) against 26.5% (CHECKS-collateral-and-pkm.md §1). | **Open. Needs an ADR, not a build.** It has narrowed since: two pre-registrations settle the registered estimand at the 751 denominator (`walk/PREREG-PXD018299-H10-attempt3.md:81-82`; `walk/PREREG-PXD018299-H10.md:179-181`, `:186-187`). The question is now whether a later CHECKS document may move a headline the pre-registration fixed (`walk/CHECKS-collateral-and-pkm.md:29-30`). Reviewer map D1. **Decided by bzk 2026-11-13:** a CHECKS document may propose, only a versioned HYPOTHESIS restatement moves; H10's headline stays at 27.8% (209 of 751). Recorded in ADR-0041 (`notes/drafts/0041-…`, landed by prompt 43). Closes when the record's Consequences items 2–4 and 7 land. |
| W4 | FINDINGS §3 "seven claims": the missing base rate and the unreconciled "stable and comfortably significant" prediction. | **Open.** FINDINGS §3 still opens "Seven published claims…" (`:70`), and FINDINGS carries no base rate. The prediction is at `walk/CHECKS-PXD018299-imputation-effects.md:47-48`, wrapped across two lines (file unchanged). It is still unreconciled with FINDINGS `:76-77` (1–8 of 20 draws) and `walk/CHECKS-PXD018299-population-and-convention.md:28` (0 of 7). |
| W5 | The census's implicit "deposit = analysed table" assumption (CHECKS-census.md:107–108). | **Open.** `CHECKS-census.md` unchanged. |
| W6 | "Selection adds almost nothing" conditions on a fold-change floor, not on q (CHECKS-gap-and-protein-grain.md:34). | **Open.** File unchanged. |
| W7 | MOESM5 "log2 ratios" against "unknown" (CHECKS-gap-and-protein-grain.md:73/:76; CHECKS-draws-and-threshold.md:119). | **Open.** Both files unchanged. |
| W8 | The join-mapping defeater class (CHECKS-two-route-recovery.md §4; FINDINGS §9). | **Open.** FINDINGS §9 is at `:184`, unchanged. `b960c9a` added only a 13-line banner to `CHECKS-two-route-recovery.md`. Its §4 is byte-identical, moved from `:95` to `:108`. |
| W9 | Check E's direction: 918 against 798 (CHECKS-PXD018299-population-and-convention.md:54, :68; CHECK-PXD026748-grouping.md:56). | **Open.** Both files unchanged. |
| W10 | MATCH_TOLERANCE = 1e-6 at bzk/sources/pxd018299_h10.py:164. | **Open.** File unchanged; `:164` still reads `MATCH_TOLERANCE = 1e-6`. |
| W11 | The rows-against-peptides unit slip (CHECKS-census.md:107–108). | **Open.** File unchanged. Shares its lines with W5. |
| W12 | The instability estimand grows with draw count (CHECKS-draws-and-threshold.md:17–19; FINDINGS:102). | **Open.** `draws-and-threshold.md` unchanged. **FINDINGS line moved:** `:102` at `3a165a4` was "the same at 100 draws \| 38.3%", now at **`:110`**. Overlaps reviewer map D2, §5's mixed denominators (handoff 2026-11-12 §6 item 3; map §7 item 3). |

## 2. The platform list (P1–P9)

| # | item, as written at `3a165a4` | status at `74acd53` |
|---|---|---|
| P1 | The seed-0 whole_matrix + Welch baseline (bzk/sources/pxd018299_differential.py:108–113). | **Open; lines moved.** The file changed three times since (`767e6e4`, `265beac`, `402fce8`). `IMPUTE`, with `"seed": 0` and `"scope": "whole_matrix"`, is now at `:116-121`. Welch is still the test (`welch_t`, `:354`). |
| P2 | bzk/stats/imputation.py: defaults, docstring, and row-order dependence of draws. | **Open, unchanged in substance.** `265beac` changed docstrings only. `downshift_sd`, `width_sd` and `scope="whole_matrix"` are still defaulted (`:65-68`). The module docstring says the defaults match Perseus (`:10`), while `:78` says `per_sample` is Perseus's own default. **Row-order dependence was measured on 2026-11-13:** permuting rows changes the output under both scopes, because draws are assigned in C-order of missing cells (`:103-104`, `:114-116`). |
| P3 | bzk/rebuild.py _adapter_for: hard-coded quantity and localization_threshold, and the literal "unknown" search_engine. | **Open.** File unchanged. `_adapter_for` is at `:201`. Its docstring records the site branch's `quantity` as a constant default (`:207-209`), and `"unknown"` is the fallback at `:230-231`. `:212` cites `maxquant_sites.py:171` for that default, but it is now at `:227` (`402fce8` moved it), an instance of R5's class. `localization_threshold` defaults to 0.75 at `maxquant_sites.py:224`. |
| P4 | The "nothing fitted" population claim (HYPOTHESIS v10; CHECKS-convention-resolved.md). | **Open.** `walk/CHECKS-membership-and-corrections.md:43-64` (`783138a`, 2026-09-22 22:23) withdrew "within 2% … with nothing fitted — a validation on the deposit under test". It also withdrew the 781-against-798 comparison: the comparable figure is 689. `HYPOTHESIS.md` v10 (`1019744`, sixteen minutes earlier) still states both, at `:5`, `:47-49`, `:638` and `:1203`, and cites the withdrawal nowhere. `:1203` was re-added in `4c88e9a`, after the withdrawal. The origin, `walk/CHECKS-convention-resolved.md:24-26`, carries no banner. |
| P5 | Invariant enforcement gaps I1/I6/I18; missing I12/I13 lints. | **Open (lint half).** The I13 tests (`tests/test_curation_loader.py:336`, `tests/test_maxquant_protein_groups.py:347`) assert that the fields are *recorded*. No test scans source for conditionals on `search_engine`, `acquisition_mode`, `library_type` or `test`, and no test names I12. I1, I6 and I18 were not re-measured. |
| P6 | PXD055843 unreachable by rebuild. | **Open.** `bzk/rebuild.py` unchanged; `:218` notes that `bzk/sources/pxd055843_perseus.py` routes around the replay. |
| P7 | Research code inside bzk/. | **Open, grown.** Since `3a165a4`, `bzk/` has gained `audit.py`, `audit_pxd032267.py`, `stats/tukey.py` and `sources/pxd032267_gate.py`. |
| P8 | The "12 of 14" propagation. | **Open.** It is in `ARCHITECTURE.md:269`, `ONTOLOGY.md:855`, `ROADMAP.md` (39 occurrences, e.g. `:200` "Reproduction status: 12 of 14 … recovered") and `HANDOFF.md` (6, including `:144` "do not quote 12 of 14 as a reproduction"), with these counts unchanged since `3a165a4`. New homes since: decisions/0037, four reviewer handoffs, prompt 30. `ROADMAP.md:200` against `HANDOFF.md:144` is a live contradiction. |
| P9 | Repo exposure and licence; HANDOFF.md staleness; "Last reviewed" headers; ROADMAP size; the Kùzu risk line. | **Partly addressed.** **Licence:** answered as Apache 2.0, pending an institutional check (`c57aeb9`; `ROADMAP.md:12796-12808`, see R6). There is no `LICENSE` file and no licence field in `pyproject.toml`. **Other parts, all open:** `HANDOFF.md` has had no commit since 2026-09-17. "Last reviewed" lags the last commit in `CLAUDE.md`, `ROADMAP.md`, `ARCHITECTURE.md`, `GLOSSARY.md` and `HANDOFF.md`. `ROADMAP.md` is 12,827 lines (12,794 at `3a165a4`). The Kùzu risk line (`ROADMAP.md:12770`) is unchanged. |

## 3. Environment

| # | item | status at `74acd53` |
|---|---|---|
| D30 | ATTEMPT_1_DIGEST at tests/test_pxd018299_h10.py:804 fails in some environments at 3a165a4, with the tautology-sweep failure as its knock-on. It passes on a fresh pinned install at the same commit. | **Closed by `fe06ca8`** (2026-10-07). Its message names both halves of D30: the cause (the interpreter and numpy versions inside the hashed `generated_under`) and the sweep knock-on. Re-run passing on 2026-11-13 under python 3.12.3 / numpy 2.5.1; the original failing environment was not re-run. The constant is now at `:812`. |

---

## 4. Raised since `3a165a4`, until now held only in handoffs

Each of these lived only in a reviewer handoff's prose or in a build report. They are numbered here
so a prompt can cite them. **This section is not yet complete.** It folds in handoff 2026-11-12 §6,
the 42b build, and three items confirmed open from handoff 2026-11-07b §5. The remaining open items
of handoffs 2026-10-10 §6–§7 and 2026-11-07b §5 are not yet folded in. These include the stale
`claude/*` branches, the `pxd055843_perseus.py` docstring, no export printing `protein_adjusted`,
and "the sweep floor moves only by hand".

| # | item | source |
|---|---|---|
| R1 | The two unbannered supersessions. `walk/CHECKS-ceiling-and-floor.md:90` is the round-9 20.8% floor, superseded by `walk/CHECKS-ceiling-survives.md:74-76`. `walk/CHECKS-ceiling-survives.md:72` is the round-10 32.9% rank crossing, superseded by `walk/CHECKS-draws-and-threshold.md:108-109`, and it still carries the justification that supersession refuted. | handoff 11-12 §6 item 5 |
| R2 | The unguarded source-readers deferred by prompt 39: eight by its count. Prompt 39's §3 point 3 only ordered them listed in a build report, so they are listed nowhere in the repository. `tests/` now has 15 `ast.parse` sites; prompt 39 counted 13. | handoff 11-12 §6 item 6 |
| R3 | The unguarded producer class. No test asserts that *every* producer taking a contrast and arms separately refuses a mismatch; ADR-0040 closes two sites, not the class. | handoff 11-12 §6 item 7 |
| R4 | Stages 3 and 4 of `bzk.audit` render `[FIXTURE]` under `--live`, though some keys are computed live. | handoff 11-12 §6 item 8 |
| R5 | The prose mirror. Line references inside prose the code carries go stale. 42b guards the stage 6 and 7 notes only. P3's `bzk/rebuild.py:212` is an instance. | handoff 11-12 §6 item 9 |
| R6 | Q2's institutional check: whether Oxford or the CAMS Oxford Institute holds a claim on the code. It blocks the licence commit (P9). | handoff 11-12 §6 item 10 |
| R7 | The wrong-attribution class through stage 4's findings keys: `reference_distribution` (`bzk/audit.py:927`) and `two_routes` (`:943`), whose file references sit at `:931`, `:947` and `:950`. Same class as 42b, different channel, unguarded. | 42b build report (not committed); verified against the code |
| R8 | Two branches of 42b's note checker have no synthetic case. `rule`'s `halved` alternative is untested: the cases use only "documented" and "Documented". `log`'s branch for a log-less entry (`tests/test_audit.py:1301`) is untested: both log cases hit the logged-entry branch (`:1299`). | 42b build report (not committed); verified against the code |
| R9 | `walk/FINDINGS.md:3` still says "**Two deposits**", though §10a is a third. | handoff 11-07b §5 item 5; confirmed open |
| R10 | `tests/test_tautology_sweep.py:10-11` claims "every equality, in every assert, in every `.py` file" must appear in `PINNED`. Literal displays, bound subscripts and non-equality comparisons do not register, so the docstring over-claims. | handoff 11-07b §5; confirmed open |
| R11 | ADR-0032 is still `Proposed` (`decisions/0032-*.md:5`). | handoff 11-07b §5 item 4; 10-10 §6(C); confirmed open |

## 5. Not here

The reviewer map's defects D1–D3 (`notes/REVIEWER-MAP-findings-5-and-6.md` §5) are FINDINGS §5 and
§6 specifics. D1 is W3, D2 overlaps W12, and D3 was closed by 42b (`4ba12ff`). They stay in the map,
which is their measurement record, and are cross-referenced here rather than copied.
