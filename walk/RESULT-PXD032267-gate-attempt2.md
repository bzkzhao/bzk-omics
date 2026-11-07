# RESULT — PXD032267 under its named test, attempt 2 (final)

> **Every figure in this document carries the label** *second attempt, after a
> registration defect; test identified exploratorily* (attempt 2 §4). Attempt 1
> stands beside it unrevised (`walk/RESULT-PXD032267-gate-attempt1.md`).

**Run on bzk's machine after registration** (`walk/PREREG-PXD032267-gate-attempt2.md`,
committed at `02251d0`, built under prompt 35 at `d85c9a1` and `f22e8c9`),
at `f22e8c9`, in 8 min 26 s. No author-parameter file existed.

**Output:**
- `tests/fixtures/pxd032267_gate_attempt2.json`, the record;
- `tests/fixtures/pxd032267_gate_attempt2.started.json`, the §5 marker,
  state `completed`;

both committed at `63ca92b`. Attempt 1's `main --attempt 1` was refused
before the run, as built, because its fixture exists.

**Provenance note.** The fixture's `generated_under.working_tree_clean` reads
`false`. The marker's own `generated_under`, written when the licence was
minted and before any readout, reads `true` at `f22e8c9`. When the fixture was
written, the only change to the tree was the run's own untracked marker.
`_commit()` counts untracked files, so the run marked itself dirty. This is the
same effect prompt 35's audit found for the faults file (its B6), uncaught for
the marker. It changes no figure. **It is an open instrument item:** an
attempt-2-style run should exclude its own marker from the cleanliness check.

## §3 consistency checks — all passed

| check | result |
|---|---|
| 1. attempt 1's digests, ids, rule taken and rows reproduced | passed |
| 2. input check on attempt 1's three gate rows at 5e-7 + 1e-9 | passed |
| 3. G passes with T1 the only passing variant | passed |

Gate G: **passed, primary T1, passing set {T1}.** Y2 was disclosed in advance
and is not scored.

## Readout A — the stated pipeline reproduces every published count

At the default cell (width 0.3, downshift 1.8, `per_sample`), over draws 0–19:

| Table 7 cell | published | median | range | verdict |
|---|---|---|---|---|
| WT TAC vs WT control, up (**headline**) | 10 | 11.5 | 10–14 | **reproduced** |
| WT TAC vs WT control, down | 48 | 47 | 44–54 | reproduced |
| *Isg15*−/− TAC vs control, up | 74 | 73.5 | 67–79 | reproduced |
| *Isg15*−/− TAC vs control, down | 18 | 18 | 14–20 | reproduced |
| *Isg15*−/− TAC vs WT TAC, up | 31 | 29.5 | 24–36 | reproduced |
| *Isg15*−/− TAC vs WT TAC, down | 5 | 5 | 3–7 | reproduced |

Readout A rests on no single draw. Four inputs reproduce all six counts the
paper published:
- the paper's stated pipeline;
- the paper's named test, identified as T1;
- the deposit's values rounded to four decimals;
- the registered default imputation cell.

The headline's published 10 sits at the minimum of its draw range.

## Readout B — draw instability (D7) recurs, n ≤ 10

**Exposure:** the 7 Table 8 claims whose row carries an imputed value. The
other 3 (Adprhl1 K335, Kmt2b K102, Ackr3 K362) are measured in all twelve
samples, so a draw cannot move them.

**Verdict: recurs.** 4 of 7 exposed claims (57%) change support across the 20
draws: Titin K12993, Synpo2l K433, Filamin-C K2590 and Myh7 K1279.
`power_flag: n ≤ 10`: one changing claim would already read *recurs*, so the
verdict is close to binary and does not carry the weight of the anchor's.

**Secondaries** (reported, never the headline):

| claim | support at the default cell, of 20 | family, 360 members |
|---|---|---|
| Adprhl1 K335 | 20 | durable |
| Kmt2b K102 | 20 | durable |
| Ackr3 K362 | 20 | durable |
| Myh7 K1305 | 20 | durable |
| Myh7 K34 | 20 | durable |
| Filamin-C K2590 | 19 | underdetermined |
| Titin K12993 | 17 | underdetermined |
| Synpo2l K433 | 17 | underdetermined |
| Myh7 K1279 | 17 | underdetermined |
| **Xirp2 K1054** | **0** | underdetermined |

- **Xirp2 K1054 is a published claim supported in none of the 20 default-cell
  draws.** It does not count as changing support, since it is consistently
  unsupported, so it is not in B's numerator. It is supported elsewhere in the
  family.
- **Family:** 5 durable, 5 underdetermined, 0 unsupported. Half of the
  published claim set depends on the imputation choice, which the paper does
  not state.
- **Whole population:** 136 of the 668 retained rows carrying an imputed value
  (20.4%) change support in at least one of the six cells. Per cell the share is
  2.7% to 8.2%.

## Readout C — the paper's headline target, in the direction the text claims

Filamin-C K2590, *down* in *Isg15*−/− TAC vs WT TAC: **supported in 2 of 20
draws** at the default cell. The paper states this site was the only one of its
ten candidates also significantly downregulated in *Isg15*−/− TAC hearts. Under
the paper's own test and pipeline, with re-drawn imputation, that claim holds
in a tenth of draws. The same site's *up* claim in WT TAC vs WT control
(Table 8) holds in 19 of 20.

## Readout D — the published set depends on match-between-runs

Readout D masked the 3,201 cells identified `By matching`, which the paper
does not state was enabled.

**The valid-value rule changes.** No candidate stricter than *at least 1 in
at least one cell* now retains all ten claims, so 1,384 rows reach imputation.

| Table 7 cell | published | median | range | verdict |
|---|---|---|---|---|
| WT TAC vs WT control, up | 10 | 14 | 9–18 | reproduced |
| WT TAC vs WT control, down | 48 | 34 | 30–42 | **not reproduced** |
| *Isg15*−/− TAC vs control, up | 74 | 61 | 54–72 | near |
| *Isg15*−/− TAC vs control, down | 18 | 26 | 21–33 | **not reproduced** |
| *Isg15*−/− TAC vs WT TAC, up | 31 | 16 | 12–18 | **not reproduced** |
| *Isg15*−/− TAC vs WT TAC, down | 5 | 7 | 5–12 | reproduced |

**Table 8 under masking.** Exposure is 10, verdict *recurs* (7 of 10).
Support at the default cell, of 20:

| claim | support |
|---|---|
| Adprhl1 K335 | **0** |
| Kmt2b K102 | **0** |
| Ackr3 K362 | **0** |
| Xirp2 K1054 | 11 |
| Titin K12993 | 19 |
| Synpo2l K433 | 6 |
| Filamin-C K2590 | 3 |
| Myh7 K1279 | 4 |
| Myh7 K1305 | 1 |
| Myh7 K34 | 1 |

**The three claims measured in all twelve samples lose all support.** Their
"measured" values include match-between-runs transfers.

## Registered expectations, scored

| # | registered | outcome |
|---|---|---|
| Y2 | input check passes; G passes; primary T1 | disclosed, not scored; occurred |
| Y3 | ≥ 3 in at least one cell | scored in attempt 1 (hit); taken again here |
| Y4 | WT up: reproduced or near; median 4–40, point ~12 | **hit**: reproduced, median 11.5 |
| Y5 | other five cells: reported | all five reproduced |
| Y6 | readout B: recurs | **hit**: recurs, 4/7, n ≤ 10 |
| Y6b | Titin K12993: 20 of 20, durable | **miss**: 17 of 20, underdetermined |
| Y7 | readout C: reported | 2 of 20 |
| Y8 | readout D: reported | three of six cells not reproduced; ~~seven~~ **eight** of ten claims at or below 6 of 20. *Corrected 2026-11-07: the reviewer miscounted. The fixture's readout-D supports, and this file's own table above, give eight. Found by prompt 36's build report.* |

**Y6b's mechanism was wrong.** It held that a wholly drawn control arm gives a
large difference that is stable under re-drawing. Titin's support moves in 3 of
20 draws and across the family. No replacement mechanism is offered here; one
written after the result would be the error this project records in FINDINGS
§11.

## What this does and does not establish

- **Readout A** is the firmest result. The paper's pipeline, as stated and
  identified, reproduces its published counts.
- **Readouts B and C** are conditional on the registered default imputation
  cell, because the authors' parameters are unstated. The family shows that
  half the claims' support turns on that choice. *Fragile* here means fragile
  to unstated choices, not shown to be false.
- **Readout D** shows the published set depends on a search setting the paper
  does not state, match-between-runs. It does not show MBR was misused.
- **Independence.** This is the first deposit with no author shared with the
  earlier two. The proteomics was done by a contract provider, so a shared
  convention through tooling (MaxQuant with a Perseus-style downshifted normal)
  is not excluded (`walk/SELECTION-third-deposit.md`).
- **All of it is a second attempt.** It follows attempt 1's registration
  defect, and its test was identified exploratorily. The label is on every
  figure for that reason.

## Status

**`HYPOTHESIS.md` §9's top gate is met, as a second attempt.** D7 recurs on a
deposit with no shared authors, with n ≤ 10.

**§5 of the attempt-2 registration now applies.** There is no further attempt
on PXD032267. Author or provider parameters, if they arrive, enter only as an
added configuration.
