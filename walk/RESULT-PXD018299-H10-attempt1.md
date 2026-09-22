# RESULT — PXD018299 under its named test, attempt 1: gate G failed

**Run on bzk's machine after registration** (`walk/PREREG-PXD018299-H10.md`,
committed at `0e4dc6b`), at `a4b2d9d`, in 9.4 s. No author-parameter file existed.
Output: `tests/fixtures/pxd018299_h10.json`.

## The registered outcome

**Gate G failed. No variant was admitted, and the anchor readouts did not run.**
As registered (§4), the result is: **named test not reproduced** by our
implementation. Check A and readouts A to D were not computed.

| variant | precision | recall | F1 |
|---|---|---|---|
| joint, all four schemes | 43 / 43 = 1.00 | 43 / 86 = 0.50 | 0.67 |
| per-side, all four schemes | 57 / 57 = 1.00 | 57 / 86 = 0.66 | 0.80 |

Both thresholds were 0.95. There were 86 complete-case proteins with published
calls (at least 30 were needed for the gate to be informative), among 1,512
complete-case proteins; Table 3 marks 282 `+` in all. The four permutation
schemes are identical within each sidedness. At 6 against 6 there are 924
relabellings, more than the 250 randomisations, so the exhaustive schemes fall
back to random draws and trivial relabellings almost never occur. **This gate
cannot distinguish the schemes.**

## Diagnosis — DESCRIPTIVE, UNREGISTERED

Script: `notes/scripts/diagnose_gate_g.py`, run at seed 0 in the default cell.
Output, verbatim:

```
rows 2438, complete-case 1512, published calls 282 (complete-case 86)
[SE + s0 (as implemented)] top-86 of complete cases by |d| contains 86 of the 86 published calls; unpublished complete cases ranked above the weakest published call: 0
[SD + s0 (alternative)] top-86 of complete cases by |d| contains 85 of the 86 published calls; unpublished complete cases ranked above the weakest published call: 11
[joint] called 178 of 2438 (Perseus: 282; 72 up, 210 down in WT/KO); ours up 33, down 145; the 282nd-smallest q = 0.0982 (Perseus's 282nd call sits at <= 0.05)
[per_side] called 183 of 2438 (Perseus: 282; 72 up, 210 down in WT/KO); ours up 8, down 175; the 282nd-smallest q = 0.1022 (Perseus's 282nd call sits at <= 0.05)
|d| at Perseus's 282nd rank under our statistic: 0.761
published calls among our top-282 by |d| (all rows): 255 of 282
```

**Readings (judged).**

1. **The statistic is right.** With s0 added to the pooled standard error, the 86
   published complete-case calls are exactly the top 86 of our ranking, with no
   unpublished protein above the weakest of them. The standard-deviation form
   does worse. So precision 1.0 is not luck: we rank as Perseus does.
2. **The FDR calibration is off by about a factor of 2.** Our joint q at
   Perseus's 282nd rank is 0.098, and half of that, 0.049, sits just under
   Perseus's 0.05.
   - A π₀ correction is unlikely to give exactly 2: with about 12% of proteins
     significant, π₀ would be near 0.8 to 0.9.
   - The leading hypothesis is a **counting convention**: null exceedances
     counted in one tail against observed exceedances in both, or an
     equivalent halving.
   - **Not verified.** The public source repository once cited for Perseus's
     plugins (`github.com/JurgenCox/perseus-plugins`) returned 404 on
     2026-09-22, so the convention could not be read from code.
3. **Per-side is not Perseus's convention,** despite its higher recall. It calls
   8 proteins up against Perseus's 72.
4. **The remainder is draw dependence.** Across all rows, 255 of Perseus's 282
   are in our top 282. The other 27 rows carry imputed values.

## What this means

- **The anchor is not yet recomputed under its named test.** The Welch-based
  figures (237 significance losses) remain D6 and are not the paper's.
- **A repaired implementation is a new attempt,** to be registered before it
  runs. **Gate G can no longer validate it independently,** because the
  factor-of-2 hypothesis was read off Table 3. Attempt 2 needs one of:
  - an independent published Perseus output, with FDR and s0 stated;
  - the code or documentation stating the convention;
  - the authors confirming it.

  Check A and the anchor's own claim count stay available as further
  constraints.
- **Attempt 1 is reported as it stands.** No threshold or variant is changed
  after the fact.
