# PRE-REGISTRATION — PXD026748 multiplicity divergence (the quantity gate)

**Registered 2026-09-20, before any run, at the commit that adds this file.**

## The question

The publication analysed the **expanded**, per-multiplicity GG site table. Its
own methods say the site table was expanded before log2 transformation. The
platform stores only the summed `Intensity {label}` column, and the closed
`quantity` enum has no per-multiplicity value (`ONTOLOGY.md`, `Analysis.quantity`
comment).

A reconstruction on the summed values (route A) diverges from the paper's input
in three ways:
1. through values;
2. through per-sample median normalisation;
3. through the valid-value filter.

This run **bounds those divergences**. It does not choose the route. The route
is chosen afterwards, by the rule registered below.

**Instrument:** `notes/scripts/measure_multiplicity.py`, run once from the
repository root. **Input:** the GG site table named by
`data/curation/curation_PXD026748.json` (`sha256:59000733…b647f50`), located by
digest in the raw store. **Population:** the adapter's own `_filter`, meaning
decoys, contaminants and localisation below 0.75 are removed, which is the rows
the ingestion used.

**Out of reach this run:** the same counts restricted to the 296 published
claims. Keying claims needs `MOESM3`, which is not yet pinned. That count
belongs to the cascade turn, and the measurement here covers all filtered sites.

Kinds follow `walk/PREREG-PXD026748-shotgun-ingest.md`: **MEASURED** (already
counted elsewhere), **DERIVED** (from code or construction plus a measured
figure), **JUDGED** (the reviewer's expectation, with its basis).

---

## Registered figures

| # | quantity | registered | kind | basis |
|---|---|---|---|---|
| 0 | the population | **2,187** | MEASURED | `tests/fixtures/pxd026748_digly_ingest.json`, the multi-protein `after_localisation` denominator |
| 1 | `___1`/`___2`/`___3` columns present for all 12 labels | **yes** | JUDGED | MaxQuant 1.6 site tables report per-experiment multiplicity columns. If absent, the question is moot and the script stops |
| S | cells where summed = `___1` + `___2` + `___3` | **≥ 99%** of 26,244 | JUDGED | the reviewer's model of MaxQuant's columns. **Below 99%, that model is wrong, and nothing after it is interpreted until the columns are re-read** |
| 2 | expanded rows (any positive value), total | **2,187 to 4,000**, point ~2,600 | JUDGED | ≤ 2,187 per multiplicity by construction; the `___2`/`___3` share is unknown. The interval is wide because the basis is only a chemical expectation |
| 3a | sites with a positive `___2` or `___3` in any run | **5% to 40%** of 2,187, point ~15% | JUDGED | doubly-modified GG peptides should be a minority. Thin basis |
| 3b | sites with no positive `___1` but a positive summed value | **0 to 5%** | JUDGED | sites seen only on multiply-modified peptides |
| 4a | per-sample median difference, expanded − summed, log2 | **mean between −0.6 and 0**, point −0.2 | JUDGED | expanded rows add lower-intensity multiplicity-2/3 values, and `___1` ≤ summed |
| 4b | spread of 4a across the 12 samples (max − min) | **0 to 0.3**, point < 0.1 | JUDGED | the multiplicity mix should be similar across runs. The `ko_mut` block's hardware difference is the main way it might not be |
| 5a | sites passing the valid-value filter on summed but not on `___1` | **0 to 5%** of 2,187, point 1–2% | JUDGED | sites whose `___1` is missing in a run where `___2`/`___3` is present |
| 5b | sites passing on `___1` but not on summed | **0** | DERIVED | if S holds, a positive `___1` implies a positive summed value |

The filter in #5 is Perseus's usual rule, at least three valid values in at
least one of the four groups. That is the reading of the methods sentence
recorded in `notes/reports/REVIEW-ADR-0035.md`'s addendum.

---

## The decision rule, registered before the data

Route A (reconstruct on the summed values, divergence declared) is
**admissible only if both** of these hold:

- **4b ≤ 0.1 log2.** A shift that is equal across samples cancels in the ANOVA
  and a large spread does not.
- **5a ≤ 21 sites**, which is 1% of 2,187. More than that changes which sites
  are tested at all.

**If either fails, route B**: extending the enum, with B1 or B2 decided by ADR.
3a is reported and informs the ADR, but it does not decide the route, because
the claim-level version of it waits for the cascade.

**The thresholds are the reviewer's judgement.** They are fixed here so they
cannot be fitted to the result. **No threshold is moved after the run.**

**Independently of the rule:** if #1 holds, the site adapter currently discards
quantities the deposit reports. That is the class turn 10d closed at protein
grain, and it is an I11 question whichever route is chosen.
