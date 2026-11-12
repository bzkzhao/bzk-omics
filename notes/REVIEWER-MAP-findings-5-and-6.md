# REVIEWER MAP — every home behind FINDINGS §5 and §6

**Measured 2026-11-10 against `main` at `24a44da`.** Method: enumerate what *does*
bear on each figure, one figure at a time, instead of reporting that a search came
back clean. Prompts 41 and 42 both failed on the second method.

Every line reference below was opened and read at `24a44da`.

---

## 1. The figure register

### FINDINGS §5 (l.102–132)

| # | figure | at | denom. | FDR rule | instrument | home | status |
|---|---|---|---|---|---|---|---|
| 1 | 210 of 791 = **26.5%** | :109 | 791 | documented | round13 | `CHECKS-collateral-and-pkm.md:25`; `round13.txt:7` | **conflicts with PREREG §6B — D1** |
| 2 | **38.3%** at 100 draws | :110 | **751** | documented | round11/12 | `CHECKS-draws-and-threshold.md:19` | live |
| 3 | **13.7%** family floor | :111 | **751** (103) | family floor | **round10** | `CHECKS-ceiling-survives.md:70` | live; supersedes 20.8% |
| 4 | 133 calls | :120 | — | — | **round9** | `CHECKS-ceiling-and-floor.md:108` | live |
| 5 | 16 / 3, 118 / 6 | :128–130 | — | documented | **round10** | `CHECKS-ceiling-survives.md:52–53` | live; phrasing rule attached (§4 below) |
| 6 | 9 of 791; 4 at 100 | :131 | 791 | documented | **round10** (20 draws, stated); round11/12 (100 draws) | `CHECKS-ceiling-survives.md:55`, `:69`; `draws-and-threshold.md:19` | live |

### FINDINGS §6 (l.134–151)

| # | figure | at | denom. | FDR rule | instrument | home | status |
|---|---|---|---|---|---|---|---|
| 7 | +2.664 frozen | :137 | — | documented | round11/12 | `CHECKS-draws-and-threshold.md:56` | live |
| 8 | q 0.0144 → 0.0177 | :138 | — | documented | round11/12 | `CHECKS-draws-and-threshold.md:57` | live |
| 9 | 1 of 40 across the cut | :141 | 40 | documented | round13 | `CHECKS-collateral-and-pkm.md:21–22`; `round13.txt:2–3` | live |
| 10 | median **0.0015** | :142 | 40 | documented | round13 | `CHECKS-collateral-and-pkm.md:23`; `round13.txt:5` | live; restated by round14 over the same 40 — §3 |
| 11 | 1 in 40, 0.1%–13% | :144 | 40 | documented | round14 | `round14.txt:16–17`; `CHECKS-census.md:68–69` | live |

**§5 draws on four instruments — round9, round10, round11/12, round13; §6 on
three — round11/12, round13, round14.** Round9 enters §5 only through the condition
cell at :120, the 133-call figure (`CHECKS-ceiling-and-floor.md:108`). Separately, its §4
carries the 751 half of the stage's conditional figure (`:89`, 159 of 751 under the halved rule)
beside the documented rule's 209 (`:88`); **that file contains no `791`, so it is not the home of
the stage's 791 figure, and `:88` is not a stage figure at all.** (Corrected 2026-11-12: this line
called `:88–89` "the home of the stage's own pair", which 42b's revision 2 copied into a §0 item
that a build would have stopped on.) Two roles for one round, not a conflict —
an earlier version of this line said §5 had three instruments and that round9 was not
among them, which contradicted row 4 of the register above. Between them: six rounds
(11, 12, 13, 14 and the ceiling-and-floor / ceiling-survives runs), five CHECKS
documents, two committed logs. **No single ported function regenerates either
section.** That is the premise prompt 42 got wrong twice.

---

## 2. The collision zone, measured

Stage 6 run against `tests/fixtures/pxd018299_h10_attempt3.json` at `24a44da`: **The key
names below are this commit's; prompt 42a renames stage 7's two counters, and a
dated record is not corrected when the code it recorded moves on.**

```
claims 791   family_members 360   default draws 20
changing_in_default_cell       159
changing_in_default_cell_share 0.201
changing_somewhere_in_family   479
supported_in_every_default     631
supported_in_no_default_draw     1
```

**The share stage 6 reports is 159 of 791 = 20.1%; FINDINGS §5's headline is
210 of 791 = 26.5%.** Same denominator, same nominal quantity, differing only by
FDR rule — the registered halved variant against the documented rule. The
*registered* share is the 751 one (D1); 20.1% is what the stage emits, not what
any document registers. **The denominator cannot
separate them. Only the rule can.** Any key registering either figure must name
the rule.

Eight live figures sit between 20% and 33%:

| value | quantity | denom. | rule | home |
|---|---|---|---|---|
| **20.1%** | support changes, default cell | 159/791 | halved | stage 6; `RESULT-…-attempt3.md:47` |
| **20.1%** | rank-range crossing at rank 1,000 | /751 | — | `draws-and-threshold.md:105` |
| 20.8% | family floor (round 9) | 156/751 | — | `ceiling-and-floor.md:90` — **superseded, unbannered** |
| 21.2% | support changes, pre-specified | 159/751 | halved | `HYPOTHESIS.md:81`; `attempt3.md:46` — the **level** is superseded (restated at 27.8% under the documented rule, `HYPOTHESIS.md:84–85`) and kept visible; the **751 population is not** — it is the registered estimand (D1) |
| 26.5% | support changes | 210/791 | documented | `collateral-and-pkm.md:25`; `FINDINGS.md:109` |
| **27.6%** | support changes, twelve-sample population | — | documented | `HYPOTHESIS.md:56` |
| **27.6%** | rank crossing at the documented calling rate | /751 | documented | `draws-and-threshold.md:104` |
| 27.8% | support changes | 209/751 | documented | `collateral-and-pkm.md:24` + 5 further homes |
| 32.9% | rank crossing (round 10) | 247/751 | — | `ceiling-survives.md:72` — **superseded, unbannered** |

**Two exact duplicates across unrelated quantities** (20.1%, 27.6%). **Two
unbannered supersessions.** `ceiling-survives.md:72` is the worse of the two: it
carries 32.9% described as needing "no rule, no s0, no population argument" —
which is precisely the justification `draws-and-threshold.md:108–109` refuted
when it superseded the figure eight minutes later.

---

## 3. Figure 10: one value, one population — corrected 2026-11-12

**This section said the two readings below were over different populations. They are not.**
Both scripts compute the figure with the same expression over the same rows:
`diagnose_round13.py:120` and `diagnose_round14.py:150` both read
`fully = published & (imputed_count == 0)`, under the same `anchor_population`, `DRAWS` and
`DEFAULT`, and round14's own header (`diagnose_round14.py:16-18`) introduces the figure as round
13's. Found by 42b revision 2's adversarial review reading the scripts; the scripts were not run.

| reading | population | home |
|---|---|---|
| median q range 0.0015 | the **40 fully measured published claims** | `round13.txt:5`; `collateral-and-pkm.md:23` |
| median q range 0.0015 | the same 40, restated as round 14's jitter band | `round14.txt:12`; `CHECKS-census.md:59–60` |

`round14.txt:12`'s label, "rows whose own values never move", describes the same rows: a fully
measured row's own values are never drawn. FINDINGS §6:142's figure is round13's; round14 restates
it, in different words (`median q range 0.0015` does not contain `median 0.0015`).

---

## 4. Rules already attached to these figures

- **Draw count is mandatory.** `draws-and-threshold.md:21` — "Neither number may
  be quoted without its draw count." FINDINGS §5 complies.
- **Phrasing.** `draws-and-threshold.md:27–30` — counts are observations, not
  properties; "supported in no draw" is correct, "structurally absent" is not.
  FINDINGS §5:130 complies.
- **Crossing share.** `draws-and-threshold.md:112` — quotable only "at the
  documented rule's calling rate".
- **Vocabulary.** `CHECKS-membership-and-corrections.md` — withdrawn = false as
  stated; superseded = correct under a disfavoured choice.

---

## 5. Three defects

### D1 — The registration conflict (open; item 3 of the reviewer defect list)

**H10 has three pre-registrations** — `PREREG-PXD018299-H10.md`, `-attempt2.md`,
`-attempt3.md` — and the attempt-3 one governs the fixture `bzk.audit` reads.
`PREREG-PXD018299-H10-attempt3.md:81–82` states the shares are taken over claims
whose row carries at least one imputed value. So the **registered estimand is
settled at the 751 denominator**; what is disputed is only whether a CHECKS
document may overrule it as FINDINGS' headline.

`PREREG-PXD018299-H10.md:179–187` registers H10's primary as the share **over
claims carrying an imputed value** (751), and lists "the same share over all
claims" under **"Reported, never the headline"**.
`CHECKS-collateral-and-pkm.md:29` makes the 791 figure the headline.
`FINDINGS.md:109` leads with it.

`HYPOTHESIS.md` — last touched 2026-11-07, the most recent of any home here —
keeps 27.8% as H10's level and **contains no occurrence of 26.5%** (grep count
0). So HYPOTHESIS is consistent with the registration and FINDINGS has departed
from it. **Neither chain cites the other on this point.**

Named in exactly one place in the repository: `notes/prompts/22-…:149`, inside a
section headed "Out of scope. Do not touch."

*Direction, which matters for how this is judged:* the correction moves the
headline **down**, 27.8% → 26.5%, so it is not outcome-fitted, and round 12's
mechanism — fully measured claims are exposed through the shared threshold —
is a substantive reason the 751 denominator understates the exposed population.
That argues the correction is **right**, and that it should have been recorded as
a registered deviation rather than taken silently.

### D2 — FINDINGS §5's table mixes denominators and calls them "the same"

:109 is of **791**; :110 is of **751** (`draws-and-threshold.md:15` header);
:111 is **103 of 751**. :109 shows its denominator; **:110 and :111 show none**, and :110 is labelled
"the same at 100 draws" when it is the same quantity over a *different*
denominator.

### D3 — Stage 6's note carries a wrong attribution

`bzk/audit.py:879–886` attributes FINDINGS §5's changing-support count to
`diagnose_round11.py` / `diagnose_round12.py` (`CHECKS-draws-and-threshold.md`).
§5's headline count — 210 of 791 — is **round13's**, in
`CHECKS-collateral-and-pkm.md` §1 / `round13.txt` block AA. Round11/12 supply
:110 and :131, not :109. Same defect class as stage 4's note, corrected by
prompt 41.

---

## 6. Stage 7, measured — the id-889 item is **not** a contradiction

```
fully_measured_claims            40
moved_across_cut_in_family        3
moved_across_cut_in_default_cell  0
  859  ALDOA      family 294/360   default 20/20
  889  ATP1A1…    family 184/360   default 20/20
  1623 HIST1H4A   family 347/360   default 20/20
```

id 889 is supported in **every** default draw under the registered halved rule,
against `draws-and-threshold.md:52`'s "called in **no** draw" under the
documented rule. **Two rules, not a contradiction** — which is what stage 6's
note exists to warn about. The defect is subtler: **stage 7's note names no
rule**, so nothing on the record lets a reader tell the two apart. Likewise
stage 7's `moved_across_cut_in_default_cell` is **0** against FINDINGS §6:141's
**1** — same nominal quantity, different rule.

Separately: the keys are named `moved_across_cut_*` while the measurement is
"support changes". Stage 7's own note states q-values are not stored in the
fixture, so the key name asserts a q-range reading the fixture cannot support.

---

## 7. Consequences for the prompt queue

1. **26.5% cannot be registered as an expected value until D1 is settled**, and
   D1 is a question about whether that figure may be the headline at all. That
   is a decision, not a build — an ADR.
2. **What is left is mechanical and safe**: correct stage 6's note (D3), add the
   FDR-rule label to stages 6 and 7's keys and notes, rename stage 7's
   `moved_across_cut_*` keys to what they measure.
3. **D2 is a FINDINGS edit**, independent of both.
4. **The 21-item reviewer defect list has no home in the repository.** It exists
   only inside prompt 22's out-of-scope section. That is why items 3 and 12 —
   both of which land on §5 — were invisible to the last two prompts.

Suggested order: (2) as the prompt that replaces 42; then (3); then (1) as an
ADR; and the defect list given a home of its own.
