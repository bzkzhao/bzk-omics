# RESULT — PXD026748 multiplicity divergence (the quantity gate)

**Run 2026-09-20 on bzk's machine, after registration.** The registration is
`walk/PREREG-PXD026748-multiplicity.md` at `afdd942`, pushed 2026-09-20 02:02:59
+0100. The instrument is `notes/scripts/measure_multiplicity.py`, sha256
`8e37c292…29c4`, run once. The input is the GG site table,
`sha256:59000733…b647f50`, from the raw store.

---

## Output, verbatim

```
== Q1. per-multiplicity columns ==
labels: 12 | columns present per multiplicity: {1: 12, 2: 12, 3: 12}

== population ==
sites after decoy/contaminant and localisation (the adapter's _filter): 2187

== sanity: summed == ___1 + ___2 + ___3, per cell ==
cells agreeing: 26222 of 26244

== Q2. expanded rows ==
rows with any positive value, by multiplicity: {1: 2116, 2: 27, 3: 0} | total: 2143

== Q3. sites whose summed value differs from ___1 ==
sites with a positive ___2 or ___3 in any run: 27 of 2187
sites with no positive ___1 in any run but a positive summed value: 14

== Q4. per-sample median of log2 intensity: expanded rows vs summed rows ==
  01_Ap_WNE14_trap5_CMB-812_FRIMP_denzel_G expanded - summed = +0.0000
  03_Ap_WNE14_trap5_CMB-812_FRIMP_denzel_G expanded - summed = +0.0018
  05_Ap_WNE14_trap5_CMB-812_FRIMP_denzel_G expanded - summed = +0.0092
  07_Ap_WNE14_trap5_CMB-812_FRIMP_denzel_G expanded - summed = -0.0026
  09_Ap_WNE14_trap5_CMB-812_FRIMP_denzel_G expanded - summed = +0.0000
  11_Ap_WNE14_trap5_CMB-812_FRIMP_denzel_G expanded - summed = +0.0042
  13_Ap_WNE14_trap5_CMB-812_FRIMP_denzel_G expanded - summed = +0.0000
  15_Ap_WNE14_trap5_CMB-812_FRIMP_denzel_G expanded - summed = +0.0016
  17_Ap_WNE14_trap5_CMB-812_FRIMP_denzel_G expanded - summed = +0.0013
  19_Ap_WNE14_trap5_CMB-812_FRIMP_denzel_G expanded - summed = +0.0022
  21_Ap_WNE14_trap5_CMB-812_FRIMP_denzel_G expanded - summed = +0.0145
  23_Ap_WNE14_trap5_CMB-812_FRIMP_denzel_G expanded - summed = +0.0122
difference: mean +0.0037, spread (max - min) 0.0171, sd 0.0054

== Q5. the valid-value filter: summed rows vs ___1 rows ==
groups: {'ISG15-/- / PLpro WT': 3, 'ISG15-/- / PLpro mutant': 3, 'WT / PLpro WT': 3, 'WT / PLpro mutant': 3}
pass on summed: 877 | pass on ___1: 877
pass on summed but not ___1: 0 | pass on ___1 but not summed: 0

done; nothing written
```

---

## Scoring

| # | registered | measured | result |
|---|---|---|---|
| 0 | population 2,187 | 2,187 | held (MEASURED) |
| 1 | columns present | 12 / 12 / 12 | held |
| S | ≥ 99% of 26,244 cells | 26,222 (99.92%) | held; **22 cells disagree, unexplained** |
| 2 | 2,187 to 4,000 expanded rows; point ~2,600 | **2,143** | **missed, below** |
| 3a | 5% to 40% of sites; point ~15% | **27 (1.2%)** | **missed, below** |
| 3b | 0 to 5% | 14 (0.64%) | held |
| 4a | mean between −0.6 and 0; point −0.2 | **+0.0037** | **missed on sign; the magnitude is negligible** |
| 4b | spread 0 to 0.3; point < 0.1 | **0.0171** | held |
| 5a | 0 to 5%; point 1–2% | **0** | held, below the point |
| 5b | 0 | 0 | held (DERIVED) |

**Three misses of ten, all in the same direction: the table carries far less
multiplicity than the reviewer expected.**
- **#2** missed because the basis assumed every filtered site has a quantified
  `___1` row. In fact 71 of the 2,187 have none: 14 are seen only at
  multiplicity 2, and **57 have no positive intensity in any of the 12 runs**.
- **#3a** and **#4a** follow from the same fact: 27 multiplicity-2 rows, and
  none at multiplicity 3.

No rule, and no threshold, was moved.

---

## The decision rule, applied as registered

- **4b = 0.0171 ≤ 0.1.** Holds, by a factor of about six.
- **5a = 0 ≤ 21.** Holds.

**Route A is admissible:** reconstruct on the summed intensities, with the
divergence declared. Over the filtered sites, as measured here:
- values differ for 27 sites (1.2%);
- the valid-value filter is **unaffected** (877 pass either way);
- the per-sample normalisation shifts by at most 0.0171 log2 across samples.

**Not bounded here, carried to the reconstruction's registration:**
- **The imputation difference.** Perseus draws relative to each column's
  distribution. Expanded and summed columns differ by a handful of values, so
  the reviewer judges the difference negligible, but it was not measured.
- **The claim-level count.** How many of the 296 claims sit on the 27 sites is
  counted when the claims are keyed, in the cascade turn.

**Independent of the route: B-store stands.** #1 held, so the site adapter
discards quantities the deposit reports, namely `___1`, `___2` and `___3`. That
is the class 10d closed at protein grain, and an I11 question in its own right.
It is carried as a defect.

---

## An observation this run was not designed to make: the 44-row gap

`notes/reports/09-ingest-PXD026748-report.md` records 2,187 filtered sites
against the paper's stated 2,143, a gap of 44, reported and deliberately not
reconciled. **This run's Q2 total is 2,143.** That is 2,116 multiplicity-1 rows
plus 27 multiplicity-2 rows, taken over the same 2,187 filtered sites.

**The reading (judged, not established):** the paper's 2,143 counts the rows of
the expanded site table that carry any intensity, after the reverse,
contaminant and localisation filters. They are called "sites" in the text but
are really (site, multiplicity) rows. The arithmetic fits:
- 2,116 + 14 = 2,130 distinct sites carry intensity;
- 13 of them carry a second, multiplicity-2 row, giving 2,143 rows;
- 57 filtered sites carry no intensity at all.

**Why this is not the fishing that report 09 and the handoff forbade.**
- The instrument was registered for a different question, and the count fell out
  of it unchanged.
- No rule was sought to close the gap.

**Why it is still only a reading.**
- The methods attribute 2,143 to the minimum-score setting, not to expansion.
- The equality could be coincidence.
- It rests on the assumption that Perseus's expansion omits empty multiplicity
  rows, which is unverified.

**What would test it:** anything in the publication that counts the expanded
table after the valid-value filter, or Perseus's documented behaviour on
expansion. Recorded as a candidate explanation, and not written into any record
as fact.

**Unexplained and carried:** the 22 cells in S where summed ≠ `___1` + `___2` +
`___3`.
