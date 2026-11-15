# REVIEWER HANDOFF — 2026-11-15

**Starting point for the next session.** This file supersedes
`notes/REVIEWER-HANDOFF-2026-11-12.md` as the starting point. That file stays as the record.

**What is not restated here.** The defect list now has a committed home,
`notes/REVIEWER-DEFECTS.md`, and this handoff cites it by item number rather than copying it
(`CLAUDE.md:40`). Items the earlier handoffs carry that are neither in the register nor touched
this session are not repeated; 11-07b §6(B)–(C) still stands for the platform line.

**All four items the 11-12 handoff put first are done.** 42b built (`4ba12ff`); the defect list got
a home (`aec062e`); the registration conflict became ADR-0041, `Accepted` (`248dd6d`); and FINDINGS
§5's mixed denominators were fixed by ADR-0041's follow-on, prompt 44 (`cfb1aa7`), which closed W3.

**Line references** are to `main` at `1c68a4b` unless stated.

---

## 1. Starting point

| | |
|---|---|
| `main` | `1c68a4b`, clean and linear, no merges |
| suite | **1305 passed / 15 skipped** (reviewer re-run at `cfb1aa7`, with `PYTHONPATH=.` in `/tmp/reviewA/venv`) |
| `pytest tests/test_schema.py` | 20 passed |
| `sweep()` | **60 modules / 2726 asserts**, `PINNED` 353, floor at `tests/test_tautology_sweep.py:2409` |
| checks | `ruff check` 0.16.1, `ruff format --check` and `mypy` 2.3.0 clean on `bzk tests` |
| ADR statuses | `{Accepted: 28, Proposed: 9, Superseded: 3}`, 40 records |

**Environment trap, new this session.** Running `pytest` from the repository without `PYTHONPATH=.`
in the reviewer venv fails collection with 57 errors (`No module named 'kuzu'` resolves to the system
Python's path). That is environmental, not a defect. The 11-12 traps (`streamlit`, ruff on `PATH`)
still apply.

---

## 2. Commits since `22ef594`, in order

| | |
|---|---|
| `34041a5` | REVIEWER HANDOFF 2026-11-12 |
| `1e68e89` | REVIEWER MAP: median 0.0015 is one population; round9's file is not the home of the pair |
| `e853079` | PROMPT 42b rev 10 |
| `4ba12ff` | **build:** stages 6 and 7's notes name their instruments; a guarded `RECEIPT_MAP` |
| `74acd53` | REVIEWER MAP: §6's FDR-rule cells are unstated, not "documented" |
| `aec062e` | **REVIEWER DEFECTS:** the register — W1–W12, P1–P9, D30 from prompt 22, plus R1–R11 |
| `b8b8cf2` | PROMPT 43 rev 4 + ADR-0041 draft |
| `0a0e3d5` | **build:** ADR-0041 landed `Proposed`, with its Landing verification |
| `258c096` | REVIEWER DEFECTS: W3's pointer to ADR-0041's landed path |
| `248dd6d` | **ADR-0041 `Accepted`** (bzk's decision): review findings A–I, V1 and V9 corrected in place |
| `15baed0` | PROMPT 44, after ten adversarial rounds |
| `cfb1aa7` | **build:** H10's headline restored to 209 of 751 — CORRECTION record, two banners, FINDINGS §5, stage 6, label guard |
| `1c68a4b` | REVIEWER DEFECTS: W3 closed; R12, R13 added |

---

## 3. What landed

**ADR-0041** (`decisions/0041-a-registered-headline-moves-only-through-hypothesis.md`). bzk's
decision, verbatim at the time: "For (a): propose it with a versions hypothesis restatement. And A
for (b)", then "Accept".
- **(a):** a CHECKS document may propose moving a registered headline; only a versioned HYPOTHESIS
  restatement moves one.
- **(b):** H10's headline stays at 27.8% (209 of 751). 26.5% (210 of 791) is reported over all
  testable claims, never as the headline.

**Prompt 44's build** (`cfb1aa7`) made the ADR's Consequences items 2–7:
- `walk/CORRECTION-PXD018299-H10-headline.md`, in the house form `b960c9a` set;
- dated banners on `walk/CHECKS-collateral-and-pkm.md` (+16 lines) and `walk/CHECKS-census.md`
  (+14), bodies untouched;
- FINDINGS §5 rows: row 1 is 209 of 751 (27.8%), rows 2 and 3 show their 751, row 4 is 210 of 791
  over all testable claims;
- `bzk/audit.py`: a new first `RECEIPT_MAP` entry, the 210-of-791 entry moved and relabelled, the
  comment above `registered_primary`, and stage 6's note;
- `tests/test_audit.py`: the note count 9 → 10, and a "published claims" label guard
  (`PUBLISHED_CLAIMS`, `mislabels_791`, `CAUGHT_791` / `UNCAUGHT_791`, three real-repository tests).

The reviewer re-ran the suite, the schema tests, the lint and type checks, and mutations M3 and M5,
and checked the banners and every post-banner line number by reading.

---

## 4. Leftover tasks, in priority order

**Needs bzk (decisions, not builds):**

1. **R12 — ADR-0041 item 6 is wrong.** It says "The enumeration is complete at `aec062e`"; prompt
   44's review found two more `walk/` instances (`RESULT-PXD018299-H10-attempt3.md:126-127`,
   `-attempt2.md:91`) and four execution-record lines. The ADR is append-only. The options are: leave
   it as recorded, since the CORRECTION record already lists them; or supersede item 6's sentence with
   a later ADR. A small decision.
2. **ADR-0041's two Open questions.** (1) Does (a) cover a withdrawal, not only a moved headline?
   Reviewer defect P4 is the live case: HYPOTHESIS v10 still says "nothing fitted", which a CHECKS
   document withdrew. (2) May a RESULT document or FINDINGS *propose* a move? (1) decides how P4 gets
   fixed, so it comes before P4.
3. **R11 — ADR-0032 is still `Proposed`.** Accept, supersede or withdraw.
4. **R6 — Q2's institutional check** (Oxford / CAMS Oxford Institute and the code). External; it
   blocks the licence commit (P9).

**Reviewer work, then builds:**

5. **Finish the register. Done the same day:** R14–R32 fold in every open item of handoffs
   2026-10-10 §6–§7 and 2026-11-07b §5, and §4a records six found closed. Eleven of the new items are
   marked "Carried", not re-measured; a prompt that touches one measures it first. R31 (ROADMAP
   questions) and R32 (the PI's questions) join items 1–4 above as decisions outside the reviewer.
6. **Cheap `walk/` corrections, batched by file.** Each is a banner or a FINDINGS line, in the house
   form:
   - R1: the two unbannered supersessions (`CHECKS-ceiling-and-floor.md:90`,
     `CHECKS-ceiling-survives.md:72`);
   - R9: FINDINGS `:3` still says "Two deposits";
   - W5 and W11 share `CHECKS-census.md:107-108` (now `:121-122` after the banner): one correction;
   - W6 and W7 share `CHECKS-gap-and-protein-grain.md`: one correction.
7. **The other `walk/` items:** W2, W4, W8, W9, W12. W12 (the estimand grows with draw count) now
   bears on FINDINGS §5 row 2, which prompt 44 relabelled but did not reconcile. W10 is code
   (`MATCH_TOLERANCE`).
8. **Guard gaps (tests):** R13 (the label class is guarded in four places, not across `walk/`), R2
   (eight unguarded source-readers), R3 (the producer class), R7 (stage 4's attribution channel), R8
   (two untested branches of 42b's note checker), R5 (the prose mirror), R10 (a sweep docstring that
   over-claims; a one-line fix).
9. **R4:** stages 3 and 4 render `[FIXTURE]` under `--live`.
10. **The platform list, P1–P9.** P4 waits on item 2 above; P8 ("12 of 14") is a sweep across four
    documents; P9 waits partly on R6.

---

## 5. How far along

Counted from `notes/REVIEWER-DEFECTS.md` at `1c68a4b`:

| list | items | closed | open |
|---|---|---|---|
| `walk/` (W1–W12) | 12 | 2 (W1, W3) | 10 |
| platform (P1–P9) | 9 | 0 (P9 partly) | 9 |
| environment (D30) | 1 | 1 | 0 |
| raised since (R1–R32) | 32 | 0 | 32 |
| **total** | **54** | **3** | **51** |

Six further items from the old handoffs were found already closed (register §4a) and are not
counted. **The register is now complete** as far as the handoffs record; anything not in it was
never written down. The figure that matters more: the item the project's
central H10 result depended on, W3, is closed, and FINDINGS §5 is now consistent with the
registration. Most of what remains is either a banner, a test, or a bzk decision; very little of it
moves a published figure.

---

## 6. How this session ran

**Prompt 44 took ten adversarial rounds, the most of any prompt so far.** The code side was right by
round 3 — every later build passed the suite and fired all seven mutations. Every defect after that
was in the **correction record's wording**: which lines to list, how to classify each, whether its
completeness claims were true. Three lessons:

- **A rule the record must apply needs worked cases on both sides.** The membership rule for the
  "published claims" error was revised four times. Each revision was tested against the cases at
  hand and broke on the next line a reviewer applied it to (subsets; shares with no 791; a
  qualifier; a count printed from the 791). The fix that held was listing included and excluded
  examples by their wording.
- **"Complete" is a claim that needs its search named.** ADR-0041's V8 asserted completeness and was
  wrong; the prompt's own first completeness sentence was wrong the same way. What held was naming
  the searches, the state they run on, and limiting the claim to what they cover.
- **Delta rounds work late.** Rounds 9 and 10 reviewed only the changed text, which was proportionate
  once full builds were clean, and each still found one real defect.

**What the build caught that the reviewer did not.** Its §0 noticed `bzk/audit.py:1209` would match
the new guard's pattern, and correctly placed it in stage 8, outside the guard. It also fast-forwarded
`main` from a harness branch, as `CLAUDE.md` requires, without being told.
