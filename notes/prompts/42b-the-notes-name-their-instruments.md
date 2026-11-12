# Prompt 42b — `bzk.audit` stages 6 and 7: both `not_automated` notes, and a guarded receipt map (revision 10)

**Repository:** `main` at the commit adding this prompt. Line references were measured at `1e68e89`.
Since `f999bbd`, three commits have landed: `22ef594` and `1e68e89` modify
`notes/REVIEWER-MAP-findings-5-and-6.md` only, and `34041a5` adds `notes/REVIEWER-HANDOFF-2026-11-12.md`
only. §0 re-measures every reference.

**Why revision 10.** Revisions 2 to 9 each went through two independent adversarial reviews. From
revision 4 on, one review built the spec in a copy of the repository and ran it. Revisions 5 to 9
built clean: the suite passed, `PINNED` matched the forecast and every mutation fired. The account
of what each round found is in this prompt's commit message. Two lessons shape the design:

- The guard reads the instrument, not only the anchors.
- Assertions are written in their natural form and classified, never reshaped to escape `sweep()`
  (`tests/test_tautology_sweep.py:229-233`).

42a (`4779e40`) made stages 6 and 7 state which rule and population they computed. This prompt
corrects what their notes say about the figures they disclaim.

**The defect.** Stage 6's note attributes §5's changing-support count to
`notes/scripts/diagnose_round11.py` / `diagnose_round12.py`. The count §5 headlines is
`diagnose_round13.py`'s. §5 draws on four instruments and the note names one of them. §6 draws on
three, and stage 7's note names one. Both notes render verbatim into the report
(`bzk/audit.py:1228-1229`), so a reader of the audit is told the wrong attribution.

**Why a guarded constant and not just corrected prose.** Prompt 41 corrected stage 4's note by
hand, and this is the next instance of the same class. A second hand-correction closes one case and
leaves the class open.

- Moving the attribution into a constant is this prompt's own step.
- Once it is a constant, it is a mirror of facts whose homes are `walk/FINDINGS.md`, the CHECKS
  documents and the logs. `CLAUDE.md:98` requires every such mirror to be guarded by a test, and
  this prompt builds that guard.
- `:98`'s other sentence, about a note in `HANDOFF.md` §8, does not reach `not_automated` notes. The
  report does not cite it as reaching them.

---

## 0. Receipt check — answer, then stop and wait

Re-measure each item, report what you find and whether it matches, and **stop on any mismatch.**
Quote from the file or from git, never from this prompt or from memory.

**(a) The two notes.** `stage.not_automated = [` is at `bzk/audit.py:901` (stage 6, through `:909`)
and at `:952` (stage 7, through `:958`). Quote both in full. Both spans include the closing `]`, and
each is a one-element list.

Stage 6's note puts a phrase in quotation marks that `walk/FINDINGS.md` does not contain.
`:104-105` reads "Recomputed under Perseus's documented FDR rule, at the recovered imputation
parameters, over 20 paired draws". Confirm this; the rewrite drops the phrase.

**(b) Where they surface, and the contract they keep.** `bzk/audit.py:1228-1229` renders each
**list item** as its own `- _NOT_AUTOMATED_: {item}` bullet. Quote `bzk/audit.py:7-11`: "it does
not quote the figure" governs everything §1.2 writes. Quote `CLAUDE.md:40` (one home per fact).

**(c) Stage 6's attribution is false.** Its note names `diagnose_round11.py` /
`diagnose_round12.py` for the count `walk/FINDINGS.md:109` headlines. That figure is
`diagnose_round13.py`'s:

- `walk/CHECKS-collateral-and-pkm.md:3` names the script.
- `notes/logs/round13.txt:7` carries the figure.
- Round 11 (§S, §0g) supplies `:110` and the `4 at 100 draws` half of `:131`, not `:109`.

**(d) Stage 7's note is incomplete, not false.** It names `diagnose_round12.py` for the ATP1A1 range
at `walk/FINDINGS.md:137-138`, which is right: round 12's §Z produced it (§0g). §6's other
figures come from round 13 and round 14.

**(e) The roster.** `notes/REVIEWER-MAP-findings-5-and-6.md` §1 registers eleven figures: six in §5
and five in §6. Confirm the instruments:

- §5's are round9, round10, round11/12 and round13.
- §6's are round11/12, round13 and round14.
- round9 enters §5 through the `133 calls` cell at `walk/FINDINGS.md:120`, whose home is
  `walk/CHECKS-ceiling-and-floor.md:108`.

The constant in §1.1 has thirteen entries, not eleven, because two map rows each cover two
`walk/FINDINGS.md` phrases. The labels below are the reviewer map's, not `walk/FINDINGS.md`'s
wording:

- Map row 5 ("16 / 3, 118 / 6") becomes rows 5 and 6.
- Map row 6 ("9 of 791; 4 at 100") becomes rows 7 (round10) and 8 (round11/12). These two halves
  have different instruments.

**(f) Which logs and scripts exist.**
- `notes/logs/` holds exactly `round13.txt`, `round14.txt`, `round15.txt`, `round15b.txt`,
  `round15c.txt` and `round16.txt`.
- `notes/scripts/` holds `diagnose_round` scripts for 3, 4, 6–16, 15b and 15c. There is no round 5.
- `walk/CHECKS-collateral-and-pkm.md:5-6` starts the committed-log practice.

**(g) Each CHECKS home names exactly one script set.** Over the whole file,
`grep -oE 'diagnose_round[0-9]+[a-z]?\.py' | sort -u` returns these **basenames**:

| document | scripts named |
|---|---|
| `walk/CHECKS-ceiling-and-floor.md` | `diagnose_round9.py` (at `:3`) |
| `walk/CHECKS-ceiling-survives.md` | `diagnose_round10.py` (at `:3`) |
| `walk/CHECKS-draws-and-threshold.md` | `diagnose_round11.py`, `diagnose_round12.py` (both at `:4`) |
| `walk/CHECKS-collateral-and-pkm.md` | `diagnose_round13.py` (at `:3`) |
| `walk/CHECKS-census.md` | `diagnose_round14.py` (at `:3`) |

The second script is written bare: `:4` reads "`notes/scripts/diagnose_round11.py` and
`diagnose_round12.py`". So the guard compares **basenames**, not paths.

**Within the one home naming two scripts, each entry names the script that produced its figure.**
Quote both docstring sections:
- `notes/scripts/diagnose_round11.py:10-11` (§S) produced the draw-count table, printed from `:111`.
  That gives rows 2 and 8.
- `notes/scripts/diagnose_round12.py:12-16` (§Z) produced id 889, ATP1A1 K605. Its header prints at
  `:64`, and its figures at `:131` and `:133`. That gives rows 9 and 10.

Each of those rows carries a **script anchor**: a phrase occurring in its own script and not in the
other script, which lets direction 3 check the choice (§1.4A). Measured:

| rows | script anchor | where it occurs |
|---|---|---|
| 2, 8 | `S and T — both headlines as functions of the draw count` | `diagnose_round11.py:111` only |
| 9, 10 | `id 889: measured in all six columns` | `diagnose_round12.py:64` only |

Row 7's figure is also derivable from round 11 §S (`walk/CHECKS-draws-and-threshold.md:17`, 6 + 3). The map
attributes it to round 10, whose home states it (reviewer map row 6). That is a choice, and the
report names it (§3.3).

Stage 7's current note names round 12 alone for the ATP1A1 range, and that is right.

**(h) The receipt map, measured.** Thirteen entries: §5 has rows 1–8 and §6 has rows 9–13.

- Every `walk/FINDINGS.md` anchor occurs there **exactly once**.
- Every home anchor occurs in its home.
- **Four** entries carry a committed log, rows 1, 11, 12 and 13. Each log anchor occurs in its log.
- **None of the nine log-less entries' `walk/FINDINGS.md` anchors occurs in any file in
  `notes/logs/`.** This is direction 6 of §1.4(A), measured here.

The anchor columns, and `script_anchor` (§0g), are guard data and never render. *describes* is what the notes print.
`walk/CHECKS-draws-and-threshold.md:21` requires the draw count for instability and structural
disagreement: "Neither number may be quoted without its draw count". This prompt extends that to
**every quantity computed across draws**, so every *describes* carries its draw count. Row 4 included: 133 is the
difference between the halved and documented rules' call counts (`walk/CHECKS-ceiling-and-floor.md:23`,
`:26`), each a call made in at least half of 20 draws (`notes/scripts/diagnose_round9.py:37`, `:104`).

| row | § | `walk/FINDINGS.md` anchor | describes (rendered) | scripts | home | home anchor | log | log anchor |
|---|---|---|---|---|---|---|---|---|
| 1 | 5 | `210 of 791` | share of all published claims whose support changes across draws, documented rule, 20 draws | round13 | collateral-and-pkm | `210 of 791` | `round13.txt` | `210 of 791` |
| 2 | 5 | `38.3%` | share of claims with an imputed value whose support changes, documented rule, 100 draws | round11 | draws-and-threshold | `38.3%` | — | — |
| 3 | 5 | `13.7%` | floor of support-change instability across the FDR rule family, over claims with an imputed value, 20 draws | round10 | ceiling-survives | `**13.7%** (103 of 751)` | — | — |
| 4 | 5 | `133 calls` | difference in calls between the halved and documented rules, 20 draws | round9 | ceiling-and-floor | `133 calls` | — | — |
| 5 | 5 | `3 are supported in every draw` | called-but-unpublished claims supported in every draw, 20 draws | round10 | ceiling-survives | `**3** (supported in all 20 draws)` | — | — |
| 6 | 5 | `6 are supported in none` | published-but-uncalled claims supported in no draw, 20 draws | round10 | ceiling-survives | `**6** (supported in no draw)` | — | — |
| 7 | 5 | `9 claims of 791` | structural disagreement with the published list, 20 draws | round10 | ceiling-survives | `9 of 791 claims` | — | — |
| 8 | 5 | `4 at 100 draws` | structural disagreement with the published list, 100 draws | round11 | draws-and-threshold | *(below)* | — | — |
| 9 | 6 | `+2.664` | ATP1A1 K605's statistic, frozen across 20 draws | round12 | draws-and-threshold | `+2.664 to +2.664` | — | — |
| 10 | 6 | `0.0144 and 0.0177` | ATP1A1 K605's q range, 20 draws | round12 | draws-and-threshold | `0.0144 to 0.0177` | — | — |
| 11 | 6 | `one is moved across the cut` | fully measured claims whose q range spans the cut, 20 draws | round13 | collateral-and-pkm | `of those, q range spans the 0.01 cut` | `round13.txt` | `their q ranges span the 0.01 cut: 1` |
| 12 | 6 | `median 0.0015` | median q range of the fully measured claims, 20 draws | round13 | collateral-and-pkm | `median 0.0015` | `round13.txt` | `median 0.0015` |
| 13 | 6 | `0.1% to 13%` | interval on the rate at which fully measured claims cross the cut, 20 draws | round14 | census | `0.1% to 13%` | `round14.txt` | `0.1% to 13%` |

Shorthand in the table:
- **scripts** means `notes/scripts/diagnose_roundN.py`.
- **home** means `walk/CHECKS-<name>.md`.
- **log** means `notes/logs/<name>`.

**Row 8's home anchor** is `| 100 | **38.3%** | **2** | **2** |`, the 100-draw row of
`walk/CHECKS-draws-and-threshold.md`'s §1 table, and it occurs once. The figure is that row's last
two cells summed (2 structural misses + 2 extras), so no phrase in the home states "4" by itself.
Say so in the constant's comment for that row.

**Why three anchor columns.** Row 11's figure is worded three ways:

| where | wording |
|---|---|
| `walk/FINDINGS.md:141` | "one is moved across the cut" |
| `walk/CHECKS-collateral-and-pkm.md:22` | "of those, q range spans the 0.01 cut" |
| `notes/logs/round13.txt:3` | "their q ranges span the 0.01 cut: 1" |

`walk/FINDINGS.md`'s wording occurs in neither the home nor the log.

Two anchors were rejected in measurement:
- `40 fully measured claims` occurs in `walk/FINDINGS.md:141` **and** `notes/logs/round14.txt:16`,
  so it would tie a round-13 figure to round 14.
- `1 in 40` at `:144` restates `:141`'s ratio.

**(i) Counters and environment.**

- **Sweep.** `sweep()` reads **60 / 2711**, `PINNED` **351**, new 0 / gone 0. That is exactly the
  floor at `tests/test_tautology_sweep.py:2374`, so there is no lag.
- **Suite.** Build the environment with `uv sync`. `streamlit` is a declared dependency
  (`pyproject.toml:14`), and without it `pytest` is **interrupted at collection** on
  `tests/test_ui.py`. On a synced environment, `pytest -q` reads **1244 passed / 15 skipped**. Any
  failure: stop.
- **Pinned tools.** Use `ruff==0.16.1` and `mypy==2.3.0` (`pyproject.toml:27-28`) **by resolved
  path**, and report the version each actually ran. The binaries first on `PATH` may differ: ruff
  0.16.9 and mypy 2.3.1 have been seen there. ruff 0.17.x reports a false `RUF100` at
  `tests/test_pxd026748_published_cascade.py:508`.

**(j) Correction vocabulary in `bzk/`.** Quote these:
- `bzk/audit.py:743`, which uses "superseded" in a findings note, landed by `24a44da`.
- `bzk/resolve/nodes.py:144`, a code comment: "Withdrawn and replaced 2026-08-08 —".
- `walk/CHECKS-membership-and-corrections.md:8-15`. `:8` reads "Vocabulary, fixed here and applied
  throughout."

**(k) `24a44da`, from git.** Quote its commit message, and confirm from the message and its diff:
- it deleted stage 4's `not_automated` block and put new text "in its place" in the
  `reference_distribution` and `two_routes` findings keys;
- it gives two reasons: the wrong attribution, and figures that `--live` now computes.

**(l) `CLAUDE.md:98`.** Quote the sentence about "a note in `HANDOFF.md` §8". Also quote the clause
"every mirror between two sources here is guarded by a test", which follows a colon mid-sentence.

**(m) `walk/CHECKS-ceiling-and-floor.md`.**
- `grep -c 791` returns **0**.
- `:86` heads the §4 table "claims with an imputed value (751)".
- `:88` is the documented rule's 209.
- `:89` is the halved rule's 159. This is stage 6's conditional figure, and the only stage figure
  in the file.
- `:90` is the round-9 20.8% floor, superseded by `walk/CHECKS-ceiling-survives.md:74-76` and
  unbannered.
- `:108` holds "133 calls".

**(n) The `median 0.0015` population.** Quote `notes/scripts/diagnose_round13.py:120` and
`diagnose_round14.py:150-151`. Confirm that `:120` and `:150` both define `fully = published & (imputed_count == 0)`,
so `round14.txt:12` restates round 13's figure over the same 40 claims. Confirm that `round14.txt:12`
reads `median q range 0.0015`, which does not contain `median 0.0015`. Row 12 has one home and one
log, and no caveat is written about it.

**(o) Populations and rules the prose will state.** Quote each of these:
- `walk/CHECKS-draws-and-threshold.md:15`, the table header "unstable, of claims with an imputed
  value". This is row 2's population.
- `walk/FINDINGS.md:104-105`, "Recomputed under Perseus's documented FDR rule". This is the source
  for "documented rule" in rows 1 and 2, and for §1.3's statement about §5's headline.
- Stage 6 run on the committed fixture: `over_all_claims` (159/791), `conditional_on_imputation`
  (159/751), `registered_variant` and `registered_primary`.
- **No §6 home states the FDR rule its figure was computed under.** This was measured; confirm it.
  - In `walk/CHECKS-draws-and-threshold.md`, "documented rule" occurs at `:82`, `:104` and `:112`.
    All three are outside its §3 (`:49-75`), the ATP1A1 section.
  - `walk/CHECKS-collateral-and-pkm.md` and `walk/CHECKS-census.md` state no rule.
  - `walk/FINDINGS.md` §6 (`:134-151`) states none either. §5 does, in its lead sentence
    (`:104-105`).

  So stage 7's prose names no rule for §6 (§1.2), and that stays open (§3.3). The reviewer map §1
  records "documented" for map rows 7–11 (constant rows 9–13): **raise that** under §2's raise-don't-edit rule. Rounds 11
  to 14 use the unscaled null count, which is round 9's documented scale
  (`walk/CHECKS-ceiling-and-floor.md:26`). A later prompt could close the rule question from the
  instruments.

---

## 1. Build

**Build order:**
1. §1.1, the constant.
2. §1.4(A), the receipt checker, its synthetic cases and its real-repository test.
3. §1.2 and §1.3, the notes.
4. §1.4(B), the note checker, its synthetic cases and its real-note test.
5. §1.5, the registration and the mutations.

### 1.1 The receipt map, as a module constant

Add `RECEIPT_MAP` to `bzk/audit.py`, after `DEFAULT_CELL` (`:59-62`). It is a
`tuple[ReceiptEntry, ...]`, where `ReceiptEntry` is a frozen dataclass or `NamedTuple` with these
fields:

| field | type | notes |
|---|---|---|
| `section` | `int` | |
| `findings_anchor` | `str` | |
| `describes` | `str` | |
| `scripts` | `tuple[str, ...]` | repository-relative paths, e.g. `notes/scripts/diagnose_round13.py` |
| `script_anchor` | `str \| None` | required where the home names more than one script (§0g); `None` otherwise |
| `home` | `str` | repository-relative path |
| `home_anchor` | `str` | |
| `log` | `tuple[str, str] \| None` | the log's repository-relative path (`notes/logs/round13.txt`) and its anchor, so "no log" is one `None` and cannot be half-filled |

It holds §0(h)'s thirteen rows in that order.

**It is the only maintained copy of the figure → home → log pairing, and a guarded mirror of facts
whose homes are elsewhere.** The reviewer map holds the same pairing as a dated record, and says it
is "not corrected when the code it recorded moves on" (its §2). So the reviewer map is not a home. This prompt's own reading is that
the `CLAUDE.md:98` mirror rule therefore does not reach it; `:98` does not say so itself. The comment above it follows `:59-61`'s form for a kept duplicate and says
four things:

- **Why the anchors live here.** A note must identify the figures it disclaims, and the figures
  live in prose that cannot be imported.
- **The anchors are guard data and never render.**
- **Which tests keep them agreeing with their sources:** the receipt checker in
  `tests/test_audit.py`.
- **What it was derived from:** `notes/REVIEWER-MAP-findings-5-and-6.md`, a dated measurement
  record.

**Amend the module docstring** by one sentence after `:7-11`. It says that `RECEIPT_MAP` holds
phrases from `walk/FINDINGS.md`, its CHECKS homes, the logs and the scripts as guard data for stages
6 and 7's notes, and that the note checker in `tests/test_audit.py` asserts no such phrase reaches
either note. It also says that the draw counts and section numbers those notes carry are stated
conditions, as are the marker's date and the round numbers inside paths, not derived figures,
because `:7` says every number in the report is derived at run
time.

The anchor fields never enter the JSON report or `render()`. Only the generated items do.

### 1.2 Both notes, rewritten

**Both notes stay in `not_automated` and are rewritten in place.** Prompt 41 handled stage 4 the
other way: it deleted the note and put new text in its place in two findings keys (§0k). Its message
gave two reasons, and only the second, that the figure became computable, differs here. §5's and §6's
figures do not become computable, so these notes keep their channel.

**Shape.** Stage 6's note has **nine** items and stage 7's has **six**:

1. **One hand-written item.**
   - **Stage 6:** it starts with the correction marker, `Withdrawn and replaced <YYYY-MM-DD>: `.
     The date is **a string literal of the build day**, not computed at run time. The marker is
     followed by the **withdrawn clause**, one sentence ending `. ` and containing no other `. `
     (so no "e.g. "), naming what the withdrawn note
     attributed the figure to. That sentence is the only place in item 0 that may name an
     instrument (§1.4B, `hand_instruments`). Then comes the §1.3 prose.
     - The form follows `bzk/resolve/nodes.py:144`, with a colon for its em dash. The word is
       "withdrawn" because the attribution was false as stated
       (`walk/CHECKS-membership-and-corrections.md:8-15`).
   - **Stage 7:** no marker, because its note was incomplete, not false (§0d). It says why the
     fixture cannot produce §6's figures: support is kept as binary and no q-values are stored. That
     is the subject of the current note and what `:937-938` calls "the note below".
     - It names no FDR rule for §6's figures, because no §6 home states one (§0o). No stage-7
       item contains the words `documented` or `halved` (§1.4B, `rule`).
     - It points at the `registered_variant` key for what the stage computes, without restating
       the key's value.
2. **One generated item per entry of the stage's section**, from `RECEIPT_MAP`, in map order. Stage
   6 gets §5's eight entries and stage 7 gets §6's five. Each item names these:
   - `walk/FINDINGS.md section N`, the form the current notes use;
   - the entry's `describes`;
   - every path in `scripts`;
   - `home`;
   - the log path, or `no committed log`.

   For example:

   ```
   walk/FINDINGS.md section 6, median q range of the fully measured claims, 20 draws: script
   notes/scripts/diagnose_round13.py; home walk/CHECKS-collateral-and-pkm.md; log
   notes/logs/round13.txt.
   ```

   The punctuation and the order within the line are yours. The content is not.

**What the prose may contain.** The note checker (§1.4B) enforces all of this:

- **No figure.** Name populations ("all published claims", "claims with an imputed value", "fully
  measured claims"), never their sizes. Write "binary", not "0/1", and "the cut", not "the 0.01
  cut".
- **Digits only where these patterns match, in any item.** The list is exhaustive: rephrase
  anything else, such as "attempt 3", "stage 6", "§5", "0/1", "20 paired draws" or "the 0.01 cut".

  - repository paths: `(?:walk|notes|bzk|tests)/[\w./-]*\w\.(?:md|py|txt|json)(?!:\d)`
  - bare script basenames: `diagnose_round\d+[a-z]?\.py`. A bare log name is **not** allowed: name a
    log by its full `notes/logs/` path.
  - draw counts: `(?:20|100) draws`
  - sections: `[Ss]ections? [56](?: and [56])?`
  - the marker date: `\d{4}-\d{2}-\d{2}`, in stage 6's item 0 only, whether or not the marker is
    well formed
  - the site: `ATP1A1 K605`

  Draw counts are conditions, not figures. `walk/CHECKS-draws-and-threshold.md:21` requires them.

  The path pattern refuses a line suffix, so `walk/FINDINGS.md:109` leaves digits behind and fails.
  That is what guards "never by line". It also ends at the extension, so a sentence-final period
  is not captured.
- **Cite `walk/FINDINGS.md` by section and description, never by line.** Its §5 has a pending edit
  (§2). CHECKS homes are cited by path. This is not a repository-wide rule: `decisions/README.md:11`
  scopes its own version to that file.
- **No item points at `notes/REVIEWER-MAP-findings-5-and-6.md`.**
- **File-level home citations are not pointers to the supersessions §2 lists.** Rows 3 and 5–7 name
  `walk/CHECKS-ceiling-survives.md`, and row 4 names `walk/CHECKS-ceiling-and-floor.md`. Neither is a
  pointer to `:72` or `:90`.

### 1.3 Stage 6's prose: its own figures are not §5's

Stage 6 reports `over_all_claims` and `conditional_on_imputation` (42a). Its hand-written item says
**neither is a §5 figure**, and says what separates each from §5's headline:

- **`over_all_claims`** is over all published claims, the same population as §5's headline. Only
  the **rule** separates them. §5's headline is under Perseus's documented FDR rule
  (`walk/FINDINGS.md:104-105`, §0o), and the stage computes the registered variant. Reviewer map §2 says the same: "The denominator cannot separate
  them. Only the rule can."
- **`conditional_on_imputation`** is over claims with an imputed value, a different population from
  the headline's. It is also under the registered variant.

Name the `registered_variant` and `registered_primary` keys; that is required (§1.4B, `keys`).
"Without restating their values" means not quoting the variant string or any figure. Naming
`conditional_on_imputation` as a quantity is fine.

Not all of §5 is under the documented rule. Rows 3 and 4 concern the rule family itself, so the
prose speaks of the **headline**, not of "§5's figures".

Do not point at `walk/CHECKS-ceiling-and-floor.md` §4 (§0m).

### 1.4 The guards

Both guards live in `tests/test_audit.py`. Their **structure** follows
`tests/test_maxquant_sites_composition.py:169` (definition) and `:265` (parametrised cases calling
the same function the real check calls). Their **assertion form** follows §1.5, not that file.
Neither is called by `run()`.

Each returns a list of `Violation(kind: str, subject: str)` `NamedTuple`s. Both re-establish their
own firing on every run through synthetic cases (`CLAUDE.md:97`). Neither rests on a one-off
mutation alone.

#### (A) The receipt checker

`check_receipts(entries, root)` returns violations. All paths in `ReceiptEntry` are relative to
`root`, and `subject` is the entry's `findings_anchor`.

| # | kind | applies to | the violation |
|---|---|---|---|
| 1 | `findings_not_unique` | all | the anchor does not occur **exactly once in the whole file, with that occurrence inside its section**: between the line starting `## {section}. ` and the next `## ` |
| 2 | `home_drift` | all | `home` is missing, or lacks `home_anchor` |
| 3 | `attribution` | all | any of clauses 3a–3f below |
| 4 | `missing_script` | all | a path in `scripts` does not exist |
| 5 | `log_drift` | with a log | the log is missing; or it lacks its anchor; or its round is not among the scripts' rounds |
| 6 | `absence_false` | without a log | a top-level file in `notes/logs/` contains the `walk/FINDINGS.md` anchor |

Direction 3's clauses. Let *named* be `{Path(s).name for s in scripts}` and *home set* be
`set(re.findall(r"diagnose_round\d+[a-z]?\.py", home_text))`:

- **3a.** *named* is empty.
- **3b.** *named* is not a subset of *home set*.
- **3c–3e** apply only when *home set* has more than one script:
  - **3c.** `script_anchor` is `None`.
  - **3d.** `script_anchor` is missing from one of the entry's own scripts. 3d and 3e run only
    when `script_anchor` is not `None`.
  - **3e.** `script_anchor` occurs in a script of *home set* that the entry does not name.
- **3f.** *home set* has exactly one script and `script_anchor` is not `None`. The anchor is
  required exactly when the home names more than one script.

Rules:

- Anchors match as **raw substrings**, without whitespace normalisation. A reflowed line fails
  loudly, and that is intended.
- A **round** is the text between `round` and the extension, so `diagnose_round13.py` and
  `round13.txt` both give `13`.
- **Each kind is reported at most once per entry.** Violations are ordered by direction.
- The home's other scripts resolve to `root / "notes" / "scripts" / <basename>`.
- Direction 3 reads no script file that does not exist, whether the entry's own or another. An
  entry's own missing script is reported by direction 4 alone.
- Read every file with `encoding="utf-8"`: round 11's script anchor contains an em dash.
- In the synthetic cases, the base entry names **one** script and its home names only that script.
  Only the one-of-two cases use a two-script home.
- A **missing home** reports `home_drift` for direction 2, and direction 3 is skipped. Directions
  1 and 4–6 run as usual. A home that exists but
  lacks its anchor still runs direction 3.
- A **missing log** reports one `log_drift`; its anchor and round are not checked.
- With **no `notes/logs/`**, direction 6 scans nothing.

Direction 3 catches an instrument that disagrees with its stated home. Within a home naming two
scripts, the script anchor checks which one. Its limits go in the docstring and the report (§3.3):

- It checks the instrument against the **home document**, not whether the home is right.
- **A coherent re-attribution passes.** `home_anchor` is chosen by the map and is not tied to
  `findings_anchor`. Moving a log-less row's `scripts`, `home` and `home_anchor` together to another
  home where the new anchor occurs satisfies every direction.
- Direction 6 establishes absence only **in `walk/FINDINGS.md`'s own words**.
- Removing row 11's log goes undetected, because its `walk/FINDINGS.md` wording occurs in no log.
  Direction 3 still guards its attribution.

**Synthetic cases**, over a root built in `tmp_path`.

Each fixture is consistent **except in the one property its case names**:
- the `walk/FINDINGS.md` copy has `## 5. ` and `## 6. ` headings and carries the anchor once, in the
  entry's section;
- the home carries its anchor and names exactly the scripts, except in the one-of-two cases;
- the scripts exist;
- `notes/logs/` exists.

A case that differs in more than one property returns more than one kind, and must not be written.

| case | direction | entry and fixture | expected kinds |
|---|---|---|---|
| true, with log | — | log carries its anchor | `[]` |
| true, without log | — | no log carries the anchor | `[]` |
| no logs directory | — | entry without log; `notes/logs/` absent | `[]` |
| anchor not unique | 1 | anchor twice | `["findings_not_unique"]` |
| anchor absent | 1 | anchor zero times | `["findings_not_unique"]` |
| home drift | 2 | home lacks its anchor | `["home_drift"]` |
| home absent | 2 | home file missing | `["home_drift"]` |
| wrong instrument | 3 | entry without log names round11/12; home names round13 | `["attribution"]` |
| no scripts | 3 | entry without log, `scripts=()` | `["attribution"]` |
| one of two, right | — | home names two scripts; entry names one, with its script anchor | `[]` |
| one of two, anchor in neither | 3 | as above, but the script anchor occurs in neither script | `["attribution"]` |
| one of two, anchor in both | 3 | as above, but the script anchor occurs in both scripts | `["attribution"]` |
| one of two, no anchor | 3 | as above, `script_anchor=None` | `["attribution"]` |
| one script, stray anchor | 3 | one-script home; `script_anchor` set | `["attribution"]` |
| wrong section | 1 | anchor present once, but under the other section's heading | `["findings_not_unique"]` |
| missing script | 4 | one named script absent | `["missing_script"]` |
| content drift | 5 | log lacks its anchor | `["log_drift"]` |
| wrong log | 5 | scripts round13; log `round14.txt` carrying the anchor | `["log_drift"]` |
| log absent | 5 | named log file missing | `["log_drift"]` |
| absence false | 6 | entry without log; a log carries its anchor | `["absence_false"]` |

**The real-repository test** asserts:

- `check_receipts(audit.RECEIPT_MAP, audit.REPO_ROOT) == []`. `audit.REPO_ROOT` is
  `bzk/audit.py:49`.
- `sorted(p.name for p in (audit.REPO_ROOT / "notes" / "logs").iterdir())` equals the six names of
  §0(f), written as a literal. Direction 6 passes vacuously if it scans nothing, and this pin makes
  a new committed log a deliberate edit here.

#### (B) The note checker

`check_note(items, entries, stage, anchors)` takes four arguments:
- the stage's `not_automated` list;
- that stage's entries, in map order;
- `6` or `7`;
- every anchor to keep out of the note.

The real test passes every anchor of every `RECEIPT_MAP` entry, `script_anchor` included (its `None`s filtered out), so the
function reads no global. Indices are 0-based, and `subject` holds them as `str`.

**Each kind is reported at most once per list.** `subject` is the first offending item's index,
or the stage for `count`. Cascades are cut as follows, so each synthetic case's single defect returns a single kind. Outside
those cases, one defect can return two: for example `notes/logs/round13.txt:3` gives `log` and
`figure`.
- a `count` violation returns `["count"]` alone, and the per-item kinds are not run;
- an item failing `order` is not checked for `scripts`, `section`, `home` or `log`.

**Extraction**, shared by `home`, `log` and `hand_instruments`:
- **CHECKS documents:** `CHECKS-[\w-]+\.md`, with or without the `walk/` prefix, normalised to
  `walk/CHECKS-….md`.
- **Logs:** §1.2's path pattern, filtered by the `notes/logs/` prefix.
- **Scripts:** `diagnose_round\d+[a-z]?\.py` basenames, plus any `notes/scripts/` path, by its
  basename.

§1.2's path pattern ends at the extension, so a sentence-final period is not captured.

| kind | the violation |
|---|---|
| `count` | `len(items)` ≠ `1 + len(entries)` |
| `order` | item `1 + k` does not contain entry `k`'s `describes` |
| `scripts` | in item `1 + k` only: `set(re.findall(r"diagnose_round\d+[a-z]?\.py", item))` ≠ `{Path(s).name for s in scripts}`. Item 0 may name the withdrawn scripts. |
| `section` | the set of every number captured by `[Ss]ections? ([56])(?: and ([56]))?` in item `1 + k` ≠ `{entry.section}` |
| `home` | the set of `walk/CHECKS-*.md` paths in item `1 + k` ≠ `{home}` |
| `log` | the `notes/logs/` paths in item `1 + k` ≠ `{log path}`, or ≠ `∅` without a log; or `no committed log` is present when the entry has a log, or absent when it has none |
| `figure` | any item contains any of `anchors`; or, after removing every match of §1.2's patterns, any digit remains |
| `reviewer_pointer` | any item contains `REVIEWER-MAP` |
| `marker` | stage 6's item 0 does not match `^Withdrawn and replaced \d{4}-\d{2}-\d{2}: ` (exact case); or any stage-7 item contains `withdrawn`, case-insensitively |
| `rule` | any stage-7 item contains `documented` or `halved`, case-insensitively (§0o: no §6 source states a rule) |
| `hand_instruments` | item 0 names an instrument (by the extraction above) outside its allowance. **Stage 6:** the *withdrawn clause* runs from the start of item 0 to its first `. `, or to its end if it has none. The marker names no instrument, so this is the same clause whether or not the marker is well formed. Script basenames ⊆ {`diagnose_round11.py`, `diagnose_round12.py`} and CHECKS documents ⊆ {`walk/CHECKS-draws-and-threshold.md`} are allowed **inside that clause only**, and no instrument anywhere else in item 0. **Stage 7:** no instrument anywhere in item 0 |
| `keys` | stage 6's item 0 lacks `registered_variant` or `registered_primary`; or stage 7's item 0 lacks `registered_variant` |

**Synthetic cases** use two or three **synthetic** entries and hand-written items. They are not
built from `RECEIPT_MAP` or by the generator under test, so a mutation of either cannot redden the
checker's own cases. Nothing in them depends on a real row at import.

- **Correct lists.** One correct list for each stage, expecting `[]`.
- **One list per kind.** Each is correct except in that kind, and expects exactly `[kind]`.
  - The `count` list has one item **too many, appended at the end**. With `count` disabled, the
    per-item checks still run, and the case fails on its kinds, not on an `IndexError`.
  - The `order` list swaps two generated items whose synthetic entries differ in `describes`,
    scripts and home.
  - The `reviewer_pointer` list writes the full path or the bare token `REVIEWER-MAP`.
  - `hand_instruments` gets three lists:
    - `diagnose_round13.py` in stage 6's withdrawn clause;
    - `diagnose_round11.py` in stage 6's item 0 **after** the withdrawn clause;
    - `CHECKS-census.md`, without `walk/`, in stage 7's item 0.
  - `rule` gets a second list, with `Documented` capitalised; `marker` gets a third, with stage 7
    containing lowercase `withdrawn`. These pin case-insensitivity.
  - `section` gets a second list: a generated item citing "sections 5 and 6".
- **`figure` gets four lists**, one for each of:
  - an anchor **containing no digit**, so that only the anchor clause can catch it;
  - a population size (`791`) in the hand-written item;
  - `0/1`;
  - `walk/FINDINGS.md:109`.
- **`log` gets two lists:**
  - a logged entry's item naming another log;
  - a logged entry's item also saying `no committed log`.
- **`marker` gets two lists:**
  - stage 6 with an em dash in place of the colon;
  - stage 7 containing the word `Withdrawn` and no digit.

**The real-note test**, for both stages run on the committed fixture:
- `check_note(...) == []`, written inline;
- `len(six.not_automated) == 9` and `len(seven.not_automated) == 6`, as literals. A literal is
  independent of the map, so it is the stronger guard on the count.
- **The anchors stay out of the whole report.** Run
  `audit.run(tmp_path, live=False, home=tmp_path / "none")`, as existing tests do (`:134`). Read
  `audit_PXD018299.md`, and `audit_PXD018299.json` re-serialised with `ensure_ascii=False`. The
  writer escapes non-ASCII, and round 11's script anchor contains an em dash. Assert that no anchor
  occurs in either. Use `not any(...)`, which is not an equality.

### 1.5 Registration and mutations

**Write each assertion in its natural form. Never reshape one to escape Pass C or D.**
`tests/test_tautology_sweep.py:229-233` records that reshaping "would have bought a green suite by
removing the expression from review rather than by reviewing it".

**Forecast.** `PINNED` moves from 351 to **353**: two new entries, **one occurrence each**. They
come from exactly these two forms, written inline, each in **one** parametrised test per checker:
- `assert [v.kind for v in check_receipts(...)] == expected`
- `assert [v.kind for v in check_note(...)] == expected`

`PINNED` is a multiset (`:198-200`). Measure occurrences off `sweep()` and state them in each
classification comment, as `:226-227` does.

Two other forms would change the count without changing what is checked:
- Binding the list first (`kinds = [...]; assert kinds == expected`) in both tests gives one entry
  with count 2.
- Binding the call (`got = check(...); assert [v.kind for v in got] == expected`) hides both from
  the sweep, which is the reshaping `:229-233` forbids.

Use the inline forms above. Every other new assert is one of three things, and none registers:
- an inline call against a literal display;
- a `len(...)` against a literal;
- not an equality.

A call result bound to a name and then compared, even against `[]`, **registers**
(`v = check(...); assert v == []`, measured in the handoff §5). Write such checks inline.

Classify each new entry in `PINNED` with a comment in the form of `:209-233`, giving:
- the two sides' independent origins: a function over synthetic input, against a hand-written
  literal in the case table;
- the mutation that reddens it, quoted with its failure message.

**A registration outside the forecast** is classified in the same way and reported as a deviation
from the forecast, with why the forecast missed it. It is never reshaped away.

**Floor.** Bump `tests/test_tautology_sweep.py:2374` to the asserts count **read off `sweep()`**,
not incremented. Add the dated comment in the form of `:2370-2373`, stating whether the module count
stayed at 60.

**Mutations**, each confirmed by reading the file back and each reverted before the report.
"Disable" means suppressing **every** append of that kind, not the existence check that guards a
read.
- each receipt-checker direction disabled in turn, failing that direction's synthetic cases;
- direction 3's empty-set clause alone disabled, failing "no scripts";
- clause 3b alone disabled, failing "wrong instrument";
- clause 3c alone disabled, failing "one of two, no anchor";
- clause 3d alone disabled, failing "one of two, anchor in neither";
- clause 3e alone disabled, failing "one of two, anchor in both";
- clause 3f alone disabled, failing "one script, stray anchor";
- each note-checker kind disabled in turn, failing that kind's synthetic case;
- `figure`'s anchor clause alone disabled, failing the digit-free anchor list;
- `hand_instruments`' position rule alone disabled (allowance applied to all of item 0), failing
  the "after the withdrawn clause" list;
- **two row-1 mutations** in `RECEIPT_MAP`, each failing the real-repository test. The `== []`
  failure message truncates the list, so read the kinds off a direct call:
  - scripts → round11, round12 gives `attribution` and `log_drift` on `210 of 791`;
  - scripts → round11, round12 **and** home → `walk/CHECKS-draws-and-threshold.md`, the withdrawn
    note's own pairing, gives `home_drift`, `attribution` and `log_drift`. Each fires for a
    different reason:
    - `home_drift`, because the home lacks the anchor;
    - `attribution` (3c), because the home names two scripts and row 1 carries no script anchor.
      Scripts and home agree here, so this is not an instrument disagreement;
    - `log_drift`, because of the round.
- **six generator mutations**, each failing the real-note test:
  - drop one entry;
  - pair each entry with its neighbour's `scripts`;
  - name every script in every item;
  - pair each entry with its neighbour's `home`;
  - render each entry's `findings_anchor` into its line;
  - cite the other section in every generated item.

Defeat the bytecode cache as `CLAUDE.md:97` specifies, in this order:
1. Delete every `__pycache__`.
2. Run with `PYTHONDONTWRITEBYTECODE=1`.

---

## 2. Out of scope. Do not touch.

- **`walk/FINDINGS.md`, `HYPOTHESIS.md`, and every `walk/CHECKS-*`.** In particular §5's mixed
  denominators: `:109` shows its denominator, `:110` and `:111` are over 751 and show none, and
  `:110` is labelled "the same at 100 draws" when the denominator differs. That is a separate,
  pending edit.
- **FINDINGS §5's headline figure.** `walk/PREREG-PXD018299-H10-attempt3.md:81-82` and
  `walk/PREREG-PXD018299-H10.md:179-181`, `:186-187` stand against
  `walk/CHECKS-collateral-and-pkm.md:29-30`. This is item 3 of
  `notes/prompts/22-walk-two-route-independence.md:149`, and it needs an ADR, not a build.
- **`notes/REVIEWER-MAP-findings-5-and-6.md`.** If the build finds it contradicting the code or the
  sources, **raise it; do not edit it.** The reviewer corrects it.
- **The two unbannered supersessions**, `walk/CHECKS-ceiling-and-floor.md:90` and
  `walk/CHECKS-ceiling-survives.md:72`.
- **The findings-key prose that names instruments**, e.g. stage 4's `reference_distribution` and
  `two_routes` (`bzk/audit.py:739-744`, `:755-764`). It is the same class through a different
  channel, and §3.3 names it.
- **`bzk/audit_pxd032267.py`.** It uses the same function names in a different module.
- **The stage-3/stage-4 `[FIXTURE]`-under-`--live` item**, and the eight unguarded source-readers
  deferred by prompt 39.

---

## 3. Report

Give the four-point close (`CLAUDE.md:95`), with each check named at the version it actually ran and
its target stated, and:

1. **Every §0 item at the value you measured.** Include §0(h)'s table cell by cell, direction 6's
   absence over the nine, §0(g)'s script sets, and each quotation §0 asks for.
2. **Both notes quoted in full as they now stand**, item by item.
3. **The wrong-attribution class**, framed across **all prose `bzk/audit.py` emits that names an
   instrument for a `walk/FINDINGS.md` figure**. State what is closed, and by what. Then state what
   is not closed:
   - direction 3 trusts the home document;
   - row 7's attribution to round 10 where round 11 also prints the figure (§0g);
   - a coherent re-attribution of `scripts`, `home` and `home_anchor` together passes;
   - direction 6's limit;
   - row 11's log;
   - the **claims** in the two hand-written items: their attributions and rule statements are
     unguarded. The checks are digit- and anchor-absence, the reviewer pointer, the marker's form, stage 7's
     rule-word absence, the key pointers and item 0's instrument allowance. Digits pass
     unchecked in path-shaped tokens, date-shaped strings in stage 6's item 0, draw counts, section
     numbers and `ATP1A1 K605`. So a wrong draw count, for example 20 for 100, is unguarded. A figure spelled out in words is
     unguarded;
   - stage 7's note names no FDR rule for §6, because neither `walk/FINDINGS.md` §6 nor any §6
     home states one (§0o). The reviewer map §6's "stage 7's note names no rule" stays open. Name
     the instrument route to closing it, and report the map's §1 rule column as raised;
   - the `describes` strings' rule and population claims, which no guard checks;
   - the findings-key channel (§2);
   - the mirror between `RECEIPT_MAP` and the reviewer map. It is unguarded by design: the constant
     is checked against the primary sources, and the map is a dated record.
4. **`sweep()` before and after.**
   - Report whether it lagged.
   - Report the `PINNED` delta against the forecast of 351 → 353, with each new entry's
     classification comment quoted.
   - Quote the floor comment you added.
   - Give each mutation with its failure message.
   - Give the suite before and after.
5. **What this did not cover.** §5 and §6 remain unregenerable by `bzk.audit`, and this prompt does
   not change that. It makes the notes name the right instruments and puts a guard under them.
