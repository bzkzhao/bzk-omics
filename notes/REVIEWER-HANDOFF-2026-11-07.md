# REVIEWER HANDOFF — 2026-11-07

**Public version.** This file supersedes `notes/REVIEWER-HANDOFF-2026-10-10.md`
as the starting point. That file stays as the record.

**The top gate in `HYPOTHESIS.md` §9 is met, as a second attempt.** The third,
unaffiliated deposit (`PXD032267`) was selected, read, registered, built twice,
run twice and written up in one session, 2026-11-06 22:00 to 2026-11-07 02:20.
§3 says what it found. §5 says what is still open.

**What is not restated here.** Items the earlier handoffs carry, which this
session did not touch, are not repeated. 2026-10-10 §6–§7 still stands for the
platform line: order item 3 (the first real IP ingestion), the three PI
questions, ADR-0032's overdue review, and the unchanged open list there.

**Line references** are to `main` at `06c5dbe` unless stated.

---

## 1. Starting point

- **`main` at `06c5dbe`**, linear, no merges.
- **Suite:** container `1104 passed, 14 skipped`, measured at `06c5dbe`. bzk's
  Mac is expected at `1110 passed, 8 skipped` (the usual six raw-store tests
  run there). That figure is inferred, not yet measured at this commit. `mypy bzk tests`: Success over
  124 files. ruff clean on `bzk tests`.
- **bzk's Mac content store** now holds both PXD032267 files, pinned in
  `bzk/sources/pride.py`.

## 2. Commits this session, in order

| commit | what |
|---|---|
| `4c88e9a` | keying dates recorded by the cascade; refusals fixture stamped. **Also swept in 34 untracked audit-output files by `git add -A`** |
| `ab1652d` | untracks them; `.gitignore` gains `audit-out*/`, `audit-*.log` |
| `31d540a` | §9 deposit-side keying dated and **closed**. The cascade re-run came out row-identical to the 09-17 one |
| `aa55b4b` | third deposit **selected** under the v8 rule: `PXD032267`, attrition 26/5/1 over 32 rows (`walk/SELECTION-third-deposit.md`) |
| `801cb83` | the deposit read at G4 (`walk/walk_PXD032267.json` § `deposit_read`) |
| `96da102` | `walk/PREREG-PXD032267-gate.md`, attempt 1 |
| `a7da073` | prompt 34, plus the R Tukey oracle generated on bzk's Mac (`tests/fixtures/r_tukey_reference.csv`) |
| `2b1866e` | prompt 34 rev 3, plus `walk/PXD032267-published-tables.json` (Tables 7 and 8, sha256-pinned PDF) |
| `18e6e41` | build: `bzk/stats/tukey.py`, `bzk/sources/pxd032267_gate.py` |
| `c1f23e1` | both PXD032267 digests pinned from the Mac fetch |
| `02251d0` | attempt 1 **result** (input not reproduced), the exploratory script, attempt 2 **registered as final** |
| `39cc2d9` | prompt 35 |
| `d85c9a1`, `f22e8c9` | attempt-2 build: rounding switch, licence-gated readouts, §3 checks, started marker |
| `63ca92b` | attempt-2 fixture and marker (the record) |
| `06c5dbe` | attempt-2 result, the §9 update, FINDINGS §10a and the §11 limitation |

## 3. What the third deposit found

**Every attempt-2 figure carries:** *second attempt, after a registration
defect; test identified exploratorily.*

- **Attempt 1 (registered result): input not reproduced.**
  - The 1e-5 input tolerance had a basis a hundred times too weak. That basis
    was the reviewer's.
  - **Exploratory diagnosis:**
    - the paper's test is **T1**, Tukey HSD on the interaction-model error. It
      matches the published p to 6.5e-6, and every other variant misses by
      more than 1e-2;
    - the authors' log2 values were **rounded to four decimals** at export.
      Rounding this deposit's own values reproduces all three published
      differences to 3.3e-7.
- **Attempt 2 (final):**
  - §3 checks passed; gate passed with T1 alone.
  - **Readout A:** all six Table 7 counts reproduced.
  - **Readout B:** D7 **recurs**, 4 of 7 exposed claims, `n ≤ 10`.
    - Xirp2 K1054 is supported in 0 of 20 draws.
    - Family: 5 durable, 5 underdetermined.
  - **Readout C:** the headline target, filamin-C K2590 *down* in KO TAC vs WT
    TAC, holds in **2 of 20** draws.
  - **Readout D:** without match-between-runs, which the paper does not state:
    - 3 of 6 counts are not reproduced;
    - the 3 fully measured claims fall to 0 of 20.
  - **Expectations:** Y4 hit, Y6 hit, **Y6b miss** (Titin 17 of 20, not 20 of
    20). No post-hoc mechanism was offered.
- **What it does not establish:**
  - B and C are conditional on the registered default imputation cell; the
    authors' settings are unstated.
  - n = 7.
  - The provider (Creative Proteomics) may share tooling conventions with the
    earlier deposits.
- **§5 of the attempt-2 registration now applies.** No further attempt on
  PXD032267. Author or provider parameters, if they ever arrive, enter only as
  an added configuration.

## 4. Working conventions learned or confirmed this session

- **Patch delivery:** one patch per step, a **new filename for every
  revision**, and the apply command always included.
  - A reused name led bzk to apply a stale patch once (`patch-38` vs `38b`).
  - Where a patch sits on one bzk may already have committed, send it combined
    or check his state first.
- **Never `git add -A` in commands for bzk.** Name every file. `4c88e9a` swept
  34 files.
- **No trailing `# comments` in shell commands for bzk.** In his zsh they were
  passed to `git status` as arguments.
- **Independent checker on every build prompt.** Prompt 34 took 4 passes;
  prompt 35 took 4.
  - The checker caught a blocker each time: the missing Table 8 p-values; the
    attempt-1 licence path; a post-licence crash leaving no record.
  - Use a fresh agent with the repo read-only and no reviewer reasoning, and
    re-audit after every revision.
- **Oracle independence.** Reference values are produced outside the build
  session: R on bzk's Mac, cross-checked by a second R version.
- **Writes that appeared without a visible origin.** Twice this session,
  files in the reviewer's clone were already written when a request arrived:
  `HYPOTHESIS.md` §9, and the attempt-1 result, attempt-2 registration and §9
  line. They came from an earlier part of the same session after a restart.
  - Rule kept: **read before keeping.** One overclaiming sentence was corrected
    on that read.
- **Mutation runs need `PYTHONDONTWRITEBYTECODE=1`.** A same-size edit restored
  within the same second reused a stale `.pyc` and produced a false red (prompt
  34's report).

## 5. Open, in priority order

1. **ROADMAP open questions 1 and 3:** public or private v0.1; a paper on the
   tool or on the biology. bzk's decision. §3's result bears on the second.
2. **The four FINDINGS figures `bzk.audit` cannot regenerate:** §1 census, §2
   two-route downshift, §5 changing-support count, §6 q-ranges. A paper needs
   them from one command.
3. **The S1 item's remaining half:** were Fig. 2f's labelled points chosen by
   hand? (§9.)
4. **Instrument items:**
   - attempt 2 marked its own tree dirty, because its untracked marker existed
     when the fixture was written (attempt-2 result, provenance note);
   - the H10 `MATCH_TOLERANCE` 1e-6 defect behind the withdrawn S1 finding
     (`bzk/sources/pxd018299_h10.py` l.164);
   - FINDINGS' opening line still says "two deposits";
   - the tautology-sweep floor still moves only by hand.
5. **ADR-0032's review**, overdue since 10-10.
6. **Platform line**, unchanged from 10-10 §6: order item 3, and the PI
   questions (PXD055843's imputation answer still blocks its ingestion).

## 6. The pivot, for orientation only

bzk is considering a pivot to provenance-aware **dataset weighting** for public
proteomics (immunopeptidomics, cryptic antigens). It would use the curation and
attrition measures this platform already produces as inputs.

§5 items 1–2 are the reviewer's recommended finish line before it. Nothing in
the repository has been started for it.
