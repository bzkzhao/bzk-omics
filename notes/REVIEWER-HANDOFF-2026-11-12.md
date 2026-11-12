# REVIEWER HANDOFF — 2026-11-12

**Starting point for the next session.** This file supersedes
`notes/REVIEWER-HANDOFF-2026-11-07b.md` as the starting point. That file stays as the record; its
§1 figures were measured at `f61f6fd` and eight commits have landed since.

**What is not restated here.** Items the earlier handoffs carry which this session did not touch
are not repeated. 11-07b §6(B)–(C) stands for the platform line; 11-07 (02:20) §3 stands for what
the third deposit found.

**One brief closed and one opened.** Prompt 42 split: **42a built and landed** (`4779e40`), and
**42b is drafted with eleven verified findings against it and nothing folded in**. ADR-0040
completed its review round trip and is `Accepted`.

**Line references** are to `main` at `22ef594` unless stated, and every one was measured there.
`4779e40` moved `bzk/audit.py` by 29 lines: both `not_automated` notes are now at **`:901-909`**
(stage 6) and **`:952-958`** (stage 7), not at the `:879`/`:927` the earlier prompts cite.

---

## 1. Starting point

| | |
|---|---|
| `main` | `22ef594`, clean and linear, no merges |
| suite | **1244 passed / 15 skipped** with `streamlit` present; 1228 without `tests/test_ui.py`, plus one environmental failure |
| `sweep()` | **60 modules / 2711 asserts**, `PINNED` 351, floor at `tests/test_tautology_sweep.py:2374` |
| checks | `ruff check` / `ruff format --check bzk tests` clean, `mypy bzk tests` clean, at the `pyproject.toml:27-28` pins |
| ADR statuses | `{Accepted: 27, Proposed: 9, Superseded: 3}`, 39 records |

**The environmental failure, so it is not mistaken for a defect.** Without `streamlit`,
`test_every_classified_instance_re_runs_its_recorded_evidence` fails because the sub-pytest it
spawns exits 2 collecting `tests/test_ui.py`. Any other failure is real.

**Tooling trap, cost two measurements this session.** `pip install 'ruff==0.16.1'` can leave a
different ruff first on `PATH`. Run the checks **by resolved path** and report the version each
actually executed; ruff 0.17.x reports a false `RUF100` at
`tests/test_pxd026748_published_cascade.py:508`, and 0.16.1 and 0.16.9 are both clean, so the
symptom does not identify the wrong binary.

---

## 2. Commits since `24a44da`, in order

| | |
|---|---|
| `191d036` | REVIEWER MAP: the homes behind FINDINGS §5 and §6, with the instrument roster |
| `7d67a5d` | PROMPT: 42a rev 2 |
| `091263f` | REVIEWER: three corrections found by 42a's receipt check |
| `4779e40` | **build:** audit stages 6 and 7 name the variant and the population; stage 7's counters renamed |
| `768d6d1` | REVIEWER MAP: the 21.2% row supersedes the level, not the 751 population |
| `838d9af` | **ADR-0040 (Accepted):** the review round trip |
| `f999bbd` | decisions/README: the round-trip count re-measured |
| `22ef594` | REVIEWER MAP: §5 draws on four instruments |

---

## 3. What 42a built

Stages 6 and 7 of `bzk.audit` reported figures numerically adjacent to `walk/FINDINGS.md` §5's and
§6's documented-rule figures without saying which FDR rule or population produced them. Eight live
figures in the repository sit between 20% and 33%, two pairs numerically identical across unrelated
quantities.

- **Both stages** carry `registered_variant` as their first finding, **read** from
  `readouts.primary.variant`, never written. The fixture has three homes for it and
  `readouts.secondary.primary_variant` differs, so the choice is guarded rather than assumed.
- **Stage 6** adds `over_all_claims` (159/791) and `conditional_on_imputation` (159/751), each with
  numerator, denominator and an **unrounded** share — bit-identical to the fixture's
  `readout_b`, which is what makes the mirror an exact equality.
- **`registered_primary`** marks `conditional_on_imputation`, citing
  `walk/PREREG-PXD018299-H10-attempt3.md:81-82` and `walk/PREREG-PXD018299-H10.md:186-187`. It is a
  *written* label because the fixture marks no primary, so it carries a mirror guard in the form of
  `bzk/audit.py:59-61`.
- **Stage 7's** two counters are renamed to name support change rather than cut crossing.
- **Five tests, where the stages had none.** The one that matters: a synthetic fixture copy flipping
  one default-cell column of row 274 (deposit 859, ALDOA) makes `over_all_claims.numerator` 160
  while the conditional stays 159. **A build computing the all-claims numerator over the
  imputed-only population passes the mirror test and fails this one** — reproduced independently
  under the `CLAUDE.md:97` bytecode discipline. At the committed fixture both numerators are 159,
  so nothing in the data discriminates them; this is the first receipt check either stage has had.

**The reviewer's own 42a figures that were wrong, corrected at `091263f`:** §0(c) named one
`KeyError` where the two fixtures raise different ones, and §0(e) claimed no file outside
`bzk/audit.py` reads the stage keys — **falsified by the reviewer's own commit** `191d036`, which
quotes them. Both were found by the build's receipt check.

---

## 4. ADR-0040 and the round-trip count

**ADR-0040 is `Accepted`** (`838d9af`), append-only from here. Two findings, neither touching the
decision: the record claimed `DeclaredContrast` refuses with "the same wording" as
`site_change_set` when only the *rule* is shared — the messages differ, each naming its own site's
mechanism, and the exception types differ too; and its eight-construction-site count is nine now,
the guard's own test being the ninth. The *Alternatives* argument was re-measured and holds:
`bzk/curation/loader.py:669-672` and `:685-698` build the D4 edges and the `ContrastArms` from one
`arms` dict, so where both reach a producer from one `LoadedCuration`, extension holds exactly when
identity holds.

**`decisions/README.md`'s completed-round-trip count was stale by eight, not one** (`f999bbd`).
Re-measured with the instrument the sentence names: **twelve of thirty-nine**. The interesting part
is not the number. **ADR-0030 completed a round trip on 2026-09-04 — five findings, `Reviewed` row
recorded — and was deliberately held `Proposed`.** So the two instruments now return twelve each
and the sets differ by one in *each* direction: the status instrument misses 0030, the
`| Reviewed |`-row instrument misses 0022. *Completed a round trip* and *accepted after review* are
not the same set, which the sentence's own rule ("a round-trip is completed or it is not") did not
say.

---

## 5. 42b — drafted, eleven findings, nothing folded in

**Scope.** Stage 6's note attributes §5's changing-support count to
`notes/scripts/diagnose_round11.py` / `diagnose_round12.py`; the count §5 headlines is
`diagnose_round13.py`'s. Stage 7's note names one of §6's three instruments. Both notes render
verbatim into the report (`bzk/audit.py:1228-1229`), so the wrong attribution is what a reader of
the audit is told. 42a deliberately left both alone because rewriting one needs the roster.

**The design is measured, and measuring changed it twice.**

1. **Each entry needs two anchors, not one.** `walk/FINDINGS.md:141` and `notes/logs/round13.txt:3`
   state the same figure and **share no phrase** — "one is moved across the cut" against "their q
   ranges span the 0.01 cut: 1". A one-string map cannot express that the log carries the figure.
2. **`40 fully measured claims` is a rejected anchor.** It occurs in `walk/FINDINGS.md:141` *and*
   `notes/logs/round14.txt:16`, so using it attributes a round-13 figure to round 14 — the defect
   class the prompt exists to close.

**The map, verified at `f999bbd`:** twelve entries, every `walk/FINDINGS.md` anchor occurring there
exactly once; **four** name a committed log (`210 of 791`, `one is moved across the cut`,
`median 0.0015` → `round13.txt`; `0.1% to 13%` → `round14.txt`) and **eight** name none.

**The eleven findings, in the order they bear on the rewrite.** Three are blockers.

1. **B** — the draft's prose says three entries carry a log; it is **four**. Direction 2 of the
   guard applies to four entries and direction 3 to eight.
2. **B** — round9 was a three-way contradiction, **now resolved in the map at `22ef594`**: §5 draws
   on **four** instruments. `FINDINGS:120`'s 133-call figure sits inside §5 (`:102-132`) and its
   home is `walk/CHECKS-ceiling-and-floor.md:108` → `diagnose_round9.py`. Round9 has two roles —
   that condition cell, and the home of stage 6's own pair at `:88-89` — and the draft treated the
   second as excluding the first. **The prompt still says three; fix it there too.**
3. **B** — the claim that the withdrawn/superseded vocabulary "has no precedent in `bzk/**.py`" is
   **false in the module being edited**: `bzk/audit.py:743` uses "superseded" in a user-facing
   findings note, landed by `24a44da` — the commit cited as precedent — and
   `bzk/resolve/nodes.py:144` reads "**Withdrawn and replaced 2026-08-08**".
   `walk/CHECKS-membership-and-corrections.md:8` says "fixed here and applied **throughout**", not
   scoped to `walk/`. The instruction was backwards: the note may carry the word directly.
4. **D** — `walk/CHECKS-ceiling-and-floor.md` contains **no occurrence of `791`**. Its §4 table is
   headed "claims with an imputed value (751)", so it cannot be where stage 6's pair reads against
   §5's `210 of 791`; it supports only the 751 half.
5. **D** — and that section's culminating row, `:90`'s 20.8% floor, is one of the two unbannered
   supersessions §2 itself puts out of scope. A user-facing note should not point there.
6. **D** — the `stage.limitations` claim about `24a44da` is false. The text went into the
   `two_routes` findings key only. **This had already been corrected out of 42a and was written
   again in 42b from memory rather than from the corrected text.**
7. **D** — `24a44da`'s own commit message gives a *dual* reason (wrong attribution **and** figures
   `--live` now computes); the draft presents "became computable" as the sole differentiator.
8. **D** — the final assertion is vacuous. If the per-figure lines are generated from the map,
   "every entry appears in the rendered note" cannot fail without mutating the generator, which the
   draft never says. `CLAUDE.md:97`: a guard is not verified until it has been made to fail.
9. **D** — "the rendered note" is singular, but the entries split **7 to stage 6's note and 5 to
   stage 7's**. Asserting all twelve against either fails.
10. **D** — the `median 0.0015` constraint cannot be expressed by the structure. The draft requires
    the note not present it as one figure with one home (`round13.txt:5` over the 40 fully measured
    claims, `round14.txt:12` over rows whose own values never move) while giving each entry one log
    field. Either add a second-home field or move the caveat to hand-written prose and say so.
11. **D** — `CLAUDE.md:98` reads "A note in **`HANDOFF.md` §8**"; generalising it to a
    `not_automated` note is the draft's own step, and it is the whole justification for building a
    guard rather than correcting prose.

**One measurement correction that matters beyond 42b.** Literal displays are **not** always safe in
the tautology sweep. `v = check(...)` then `assert v == []` **registers** — Pass D catches a bound
name whatever it is compared to. Only the inline form and `len(v) == 1` escape:

```
inline  check(m, f, d) == []        -> no match
bound   v = check(...); v == []     -> REGISTERS
bound   v = check(...); len(v) == 1 -> no match
inline  len(check(...)) == 1        -> no match
```

Any prompt stating a shape constraint must say this, or a builder writes the natural parametrised
form and moves `PINNED` off 351.

---

## 6. Open, in priority order

1. **42b revision 2, then two adversarial rounds.** All eleven above are measured; the rewrite is
   mechanical. Scope unchanged: both notes, the map as a guarded constant, nothing in `walk/`.
2. **The registration conflict needs an ADR, not a build.** Item 3 of the list at
   `notes/prompts/22-walk-two-route-independence.md:149`. The question is **narrower than it was**:
   two pre-registrations settle the registered estimand at the 751 denominator
   (`PREREG-…-attempt3.md:81-82`, `PREREG-…-H10.md:179-181`, `:186-187`), so it is no longer "which
   figure is right" but *whether a later CHECKS document may move a headline the pre-registration
   fixed* (`walk/CHECKS-collateral-and-pkm.md:29-30` against those). A decision about the
   project's own discipline; the reviewer should frame the options, not pick.
3. **`walk/FINDINGS.md` §5's mixed denominators.** `:109` shows its denominator; `:110` and `:111`
   are over **751** and show none; `:110` is labelled "the same at 100 draws" when the denominator
   differs. A `walk/FINDINGS.md` edit, independent of (2) for rows 2 and 3 and **entangled with it
   for row 1**, whose figure is what (2) disputes.
4. **The reviewer defect list has no home.** **Twenty items** — eleven `walk/` defects numbered
   **2 to 12** (there is no item 1, so the list may itself be short by one at the top) and nine
   platform items P1 to P9 — living only inside prompt 22's "Out of scope. Do not touch." section.
   Items 3 and 12 both land on §5 and were invisible to two consecutive prompts because of it. The
   reviewer map covers those two; **the other eighteen are still homeless.** This is the single
   highest-leverage item on this list: it was the proximate cause of three separate failures this
   session. *(The reviewer said "twenty-one" and "nineteen" repeatedly before counting; the count
   above was measured at `22ef594`.)*
5. **The two unbannered supersessions.** `walk/CHECKS-ceiling-and-floor.md:90` (the round-9 20.8%
   floor, superseded by `ceiling-survives.md:74-76`) and `walk/CHECKS-ceiling-survives.md:72` (the
   round-10 32.9% rank crossing, superseded by `draws-and-threshold.md:108-109` — and carrying the
   justification that supersession refuted).
6. **The eight unguarded source-readers**, deferred by prompt 39 and still unlisted anywhere in the
   repository; prompt 39's §3 point 3 only ordered the list produced in a build report.
7. **The unguarded producer class.** No test asserts that *every* producer taking a contrast and
   arms separately refuses a mismatch — ADR-0040 closes two sites, not the class.
8. **Stages 3 and 4 render `[FIXTURE]` under `--live`** though some keys are computed live.
9. **The prose mirror.** Line references inside strings emitted by `bzk/audit.py` will go stale;
   42b adds a guarded map for `walk/FINDINGS.md` anchors and does not address the rest.
10. **Q2's institutional check** — whether Oxford or the CAMS Oxford Institute holds a claim on the
    code. Recorded in `ROADMAP.md` as blocking the licence commit, not the answer.

---

## 7. How this session ran

Four rounds of review on 42a and one on 42b, and **every round found something**. The failures moved
in a direction worth recording, because the classes are different and need different guards:

- **Revision 1–2 (prompt 42):** claims about the repository never opened — a missed document
  *class*, then a missed document *within* a class already searched. The fix was to enumerate what
  bears on each figure one figure at a time, which produced the reviewer map.
- **Revision 3:** internal contradictions between paragraphs written in one sitting, and behaviour
  reasoned about rather than measured. Both were caught by running `analyse()` instead of thinking
  about it.
- **42a revision 1:** compression. The roster was correct in the map and lost compressing it into
  the prompt. The fix was splitting the prompt and committing the map.
- **42b revision 1:** generalising a repository rule past its stated scope (twice), and **rewriting
  a claim already corrected in 42a from memory instead of from the corrected text**.

**The committed map was corrected three times in six hours**, by three routes — the 42a build's
receipt check, the reviewer re-reading it, and 42b's round 1. Every correction was a real error, and
none of them would have surfaced while the document sat outside the repository. That is the argument
for item 6(4) above, and it is the same lesson three times over.

**What the build sessions caught that the reviewer did not.** The 42a build found both of the
reviewer's §0 errors, including one the reviewer had created himself between writing the prompt and
the build reading it. It also reconciled a suite count the reviewer had got wrong by double-counting
`tests/test_ui.py`, and raised a map contradiction rather than editing a reviewer document — the
right call, and worth stating as a rule rather than leaving to judgement: **a build that finds a
`notes/` document contradicting the code raises it; the reviewer corrects it.**
