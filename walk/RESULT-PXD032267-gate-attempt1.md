# RESULT — PXD032267 under its named test, attempt 1: input not reproduced

**Run on bzk's machine after registration** (`walk/PREREG-PXD032267-gate.md`,
committed at `96da102`), at `c1f23e1`, from a clean tree, in 1.3 s. No
author-parameter file existed. Output: `tests/fixtures/pxd032267_gate.json`.

## The registered outcome

**Gate G stopped at the input check: *input not reproduced*.** As registered
(§4), no test variant was scored and readouts A–D did not run. **D7 is still
untested on a deposit with no shared authors.**

What ran before the gate, all as registered:
- **Pinning:** both digests matched the declarations pinned at `c1f23e1`, and
  the site table measured 1,440 rows, 171 columns and 14 reverse rows.
- **Join:** keys P and N found the same row for all ten Table 8 claims, and the
  ids equalled the walk record's.
- **Valid-value rule:** at least 3 valid values in at least one cell, retaining
  all ten claims.
- **Gate rows:** three — the Table 8 claims measured in all twelve samples.

**The input check, over those three rows** (tolerance 1e-5):

| gate row | published Difference | from the deposit | \|Δ\| | passes |
|---|---|---|---|---|
| Adprhl1 K335 | 1.319833 | 1.3198348 | 1.8e-6 | yes |
| Kmt2b K102 | 2.701133 | 2.7011220 | 1.1e-5 | **no** |
| Ackr3 K362 | 0.850433 | 0.8504034 | 3.0e-5 | **no** |

## Registered expectations, scored

| # | registered | outcome |
|---|---|---|
| Y1 | gate rows: reported, not predicted | 3 |
| Y2 | input check passes; G passes; primary T1 | **miss**: the input check failed, and G was not reached |
| Y3 | valid-value rule ≥ 3 in at least one cell | **hit** |
| Y4–Y8 | readouts A–D | not run |

**Why Y2 missed, and whose error it is.** The 1e-5 tolerance was the
reviewer's. Its basis, in §6, was that three rows *"already match to three
decimals"*. Agreement to three decimals is evidence at about 5e-4, so the basis
was a hundred times weaker than the threshold it was offered for. The
registration bounded the publication's rounding (5e-7) and never asked how the
authors' own pipeline produced its numbers. **A tolerance for an input check
has to come from a model of the authors' export, not only from the rounding
of the published table.** Next time, that model is registered first.

**What the registered outcome does and does not say.**
- It does not say the authors used different data. The deltas are at most
  3e-5. A different column family or a per-column normalisation would be
  expected to move differences by 1e-2 or more, two to three orders of
  magnitude larger. That is an expectation, not a measurement.
- It does not say the claims are unstable, or that the test is not the paper's:
  readouts and variants were never reached.
- It does say that, at the precision registered, this deposit does not reproduce
  its published differences, and that the registered attempt ends here.

---

## Diagnosis — EXPLORATORY, UNREGISTERED

Everything below was designed after the registered outcome was known. **It is
not a result of the registration and is never scored against it.**

Script: `notes/scripts/explore_pxd032267_gate_only.py` (sha256
`e98f9f3a629559e5…`, byte-identical to the copy run), run on bzk's Mac at
`c1f23e1` against the pinned files. It reruns the module's own steps up to the
gate, suspends the input check (its only departure from the registration), and
**computes no readout**, so A–D stay unseen. It writes nothing. Output,
verbatim:

```
EXPLORATORY — input check suspended; readouts not run
status: passed | primary: T1 | passing: ['T1']
  T1: p=['0.038957', '0.020353', '0.049864']  max|dp|=6.48e-06  passes=True
  T2: p=['0.024973', '0.012209', '0.038545']  max|dp|=1.40e-02  passes=False
  T3: p=['0.009637', '0.004869', '0.012531']  max|dp|=3.73e-02  passes=False
  T4: p=['0.022283', '0.018225', '0.001693']  max|dp|=4.82e-02  passes=False
  T5: p=['0.063524', '0.019006', '0.001872']  max|dp|=4.80e-02  passes=False
  published p: [0.038957, 0.020353, 0.049858]
  close pairs: [] | pairwise gaps: {}
rounding test (log2 rounded to k decimals, then mean difference, |delta| to published):
  k=3: 1.7e-04, 2.0e-04, 1.0e-04
  k=4: 3.3e-07, 3.3e-07, 3.3e-07
  k=5: 3.3e-07, 9.7e-06, 3.3e-05
```

**Reading 1: the test is identified.** T1, Tukey HSD over the four cells with
the interaction model's error, reproduces the published p-values to 6.5e-6. Two
of the three match to all six published decimals. Every other variant misses by
more than 1e-2, and no pair of variants is close. The paper ran the test it
names.

**Reading 2: the authors' log2 values were rounded to four decimals.** At k = 4,
all three differences reproduce to 3.3e-7, which is below the publication's
rounding floor. At k = 3 and k = 5 they do not. **The identical 3.3e-7 is a
fingerprint, not a coincidence.** A difference of two means of three
four-decimal numbers lies on a grid of steps of 1e-4 / 3, and rounding such a
value to six decimals leaves exactly ⅓ × 1e-6. Any four-decimal matrix lies
on that grid, so the grid alone does not identify the input. **What does is
that rounding this deposit's own values reproduces all three published
differences**, at k = 4 and at no other k tried. The input is the deposit,
rounded at export.

**What the diagnosis licenses.** On its own, nothing: it was designed after the
outcome. It does locate the registration's defect exactly. That is the ground
for `walk/PREREG-PXD032267-gate-attempt2.md`, which corrects that defect and
nothing else, and leaves readouts A–D as untouched as they are now.
