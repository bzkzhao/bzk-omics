# PRE-REGISTRATION — PXD026748 shotgun (protein-groups) ingest

**Registered 2026-09-19, before any run, at the commit that adds this file.
Working copy: `/Users/bzk/bzk-omics`.**

Per the project's convention, expected outcomes are registered before a run that
produces a number to be compared against a recorded one. **Each figure is marked
by where its expectation comes from**, because the last pre-registration of this
deposit (`walk/PREREG-PXD026748-ingest.md`) missed three of six figures, two of
them because the basis was wrong, not because the deposit surprised anyone:

- **MEASURED** — already counted on 2026-09-19 by a reviewer script over the same
  file (`notes/scripts/`). The ingest re-derives it with a different instrument,
  the adapter, so agreement is a **cross-instrument check**, not a prediction
  confirmed. A mismatch means the two instruments count differently, and that is
  a finding about one of them.
- **DERIVED** — computed from code behaviour plus a MEASURED figure. It is exact
  if both hold. Flagged as derived from instruments rather than from data.
- **JUDGED** — the reviewer's expectation, with a stated basis and an interval as
  wide as that basis deserves.

**Instrument:** `notes/scripts/measure_shotgun_ingest.py`, run once. Step 3
drives `MaxQuantProteinGroupsAdapter` offline, dispatched by
`bzk/rebuild.py:_adapter_for`. Step 4 is `rebuild()` in the scratch home
`/tmp/bzk-e3`, never the live home. **Input:** `proteinGroups.txt`,
`sha256:b74a1797…f884`, 11,174,233 bytes, named by
`data/curation/curation_PXD026748_shotgun.json`.

---

## Registered figures

| # | quantity | registered | kind | basis |
|---|---|---|---|---|
| 1 | `rows_read`; `spill_lines` | **4,916**; **0** | MEASURED | `inspect_shotgun.py`: 4,916 rows whose `id` is digits, 0 other lines. The adapter's `read_table` applies the same rule. |
| 2 | `dropped_decoy_or_contaminant` | **148** | MEASURED | `coverage_shotgun.py`: 4,916 → 4,768, which is 62 `Reverse` + 86 `Potential contaminant` with none both. |
| 3 | `refused_empty_group` | **0** | JUDGED | MaxQuant writes `Protein IDs` for every group. Unmeasured. Any other value is a finding about the file. |
| 4 | `groups_emitted` | **4,768 − #3**, so **4,768** | DERIVED | #2 and #3. |
| 5 | `cells` | **171,648** = #4 × 12 samples × 3 families | DERIVED | Turn 10d keeps every family. The record's rationale (4) gives three families of twelve per-run columns. |
| 6 | cells per quantity | **57,216** each for `lfq`, `intensity`, `ibaq` | DERIVED | #5 split evenly. Every family covers all twelve labels. |
| 7 | cells with value > 0 | **`lfq` 28,396; `intensity` 41,951; `ibaq` 41,951** | MEASURED | The per-run sums of `coverage_shotgun.py`'s LFQ>0, Intensity>0 and iBAQ>0 columns over the same 4,768 groups. This is the sharpest cross-instrument check here. |
| 8 | ingestion `Analysis.quantity` | **`lfq`** | DERIVED | Turn 11 R5: `quantity_from_mapping_keys` on the record. |
| 9 | `distinct_accessions` | **4,768 to 9,536**, point estimate **~5,700** | JUDGED | The anchor's 23,807 accessions over 4,797 groups (≈5.0 per group) **does not transfer**: that search carried isoforms. This deposit searched canonical Swiss-Prot. The deposit and the methods both give 20,621 sequences, and the GG arm measured 0 isoform razor picks and a 9.0% multi-protein share at site grain. Expected 1.0 to 2.0 accessions per group. The basis is thin: it is site grain in the other arm, not group grain in this one. |
| 10 | `Only identified by site` rows among emitted observations | **0 to 93**, point estimate **31 to 93** | JUDGED | 93 over all 4,916 rows (`inspect_shotgun.py`). How many of those were dropped as `Reverse` or `Potential contaminant` is **unmeasured**. Arithmetic bounds it only at 0 to 93, because 148 rows were dropped. The narrower estimate assumes contaminants are rarely site-only, which is a judgement, and leaves the 62 decoys as the most that can overlap. |
| 11 | duplicate-group error | **not raised** | JUDGED | MaxQuant's groups are disjoint, and `PXD018299` measured 0 duplicates. If it is raised, the rebuild stops, and that is a finding. |
| 12 | scratch rebuild | `deposits_ingested` **3**; `site_observations` **4,195**; `protein_observations` **= #4**; `cells_staged` **100,680 + #5 = 272,328**; refusals **48 + #3**; `ingestions_skipped` **1** (`PXD055843` only) | DERIVED | The 10b re-run gave 4,195 sites, 48 refusals and 100,680 cells. The shotgun ingest adds only protein-grain figures, and no protein refusal other than #3 exists. |

---

## What a miss would mean

**#1, #2 or #7 missing.** The two instruments disagree about the same bytes.
`read_table`'s spill rule, the decoy rule, and `cell_value`'s zero/blank
convention are where they could differ. Find which one before trusting either.

**#9 above 9,536.** The search carried more multi-member groups than a canonical
Swiss-Prot search should. That contradicts the database reading two sources
agree on, and a correction to it would outrank the prediction.

**#10 below 93.** The record's `FILTERS` item says the ingested observations
"include those 93". That assumed no overlap with the dropped rows, so a miss
below 93 means **the record's figure is wrong** and needs a dated correction.
The reviewer wrote that item without measuring the overlap.

**#12 missing on the site figures.** The shotgun ingest disturbed another
deposit's replay. That cannot happen by design, since datasets are keyed by
digest, so it would be a defect to stop on.

**No rule is adjusted to move a figure into its interval.**
