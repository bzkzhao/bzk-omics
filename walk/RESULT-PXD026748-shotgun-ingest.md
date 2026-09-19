# RESULT — PXD026748 shotgun (protein-groups) ingest

**Run 2026-09-19 on bzk's machine, after the registration was committed.** The
registration is `walk/PREREG-PXD026748-shotgun-ingest.md` at `cae91c6`, pushed
2026-09-19 20:08:49 +0100. The instrument is
`notes/scripts/measure_shotgun_ingest.py`, sha256 `406ab661…2fd1`, run once. The
scratch home was `/tmp/bzk-e3`; the live home's graph and quant stores were not
touched. The file now sits in the live raw store at
`raw/b74a1797…f884/proteinGroups.txt`.

**This document is the run's transcript and its scoring. It is not the figures'
machine-readable home.** That is the fixture the generator in turn 13 writes
from the raw bytes. A fixture transcribed from this page would be written from
the document it is meant to check (`tests/test_pxd018299_refusals.py`, module
docstring).

---

## Output, verbatim

```
== 1. store ==
digest sha256:b74a1797b49b85ff3ba88e2739e47dad242583eedd58945417c239ba9fd7f884 | matches record: True
stored and re-verified at /Users/bzk/.bzk-omics/raw/b74a1797b49b85ff3ba88e2739e47dad242583eedd58945417c239ba9fd7f884/proteinGroups.txt

== 2. dispatch ==
adapter: MaxQuantProteinGroupsAdapter | declared quantity: lfq

== 3. parse (offline, no graph) ==
rows_read: 4916
spill_lines: 0
dropped_decoy_or_contaminant: 148
groups_emitted: 4768
refused_empty_group: 0
distinct_accessions: 5408
cells: 171648
refusals by reason: {}
cells by quantity: {'ibaq': 57216, 'intensity': 57216, 'lfq': 57216}
cells with value > 0 by quantity: {'ibaq': 41951, 'intensity': 41951, 'lfq': 28396}
ingestion Analysis quantity: lfq
'Only identified by site' rows in file: 93 | among emitted observations: 73 | among rows dropped as decoy/contaminant: 20

== 4. rebuild in the scratch home ==
[rebuild] dropping derived stores (graph.kuzu, quant.duckdb)
[rebuild] recreating schema from ONTOLOGY.md §4-7
[rebuild]   no adapter recognises Supplementary_Data_S1_TP.xlsx; not ingested
[rebuild] ingestion replay: 4 curation record(s), 3 deposit(s), 4195 site observation(s), 4768 protein observation(s), 48 refusal(s), 32788 node statement(s), 31344 edge statement(s), 272,328 quantitative cell(s), 1 ingestion(s) skipped
[rebuild] sequence archive last drift-checked 5 day(s) ago over a DIFFERENT set (3,013 then, 3,579 now) — run `python -m bzk.drift`
[rebuild] done: 57 tables, 4 curation record(s), 3 deposit(s), 4195 site observation(s), 4768 protein observation(s), 48 refused, 32788 node statement(s), 31344 edge statement(s), 272,328 quantitative cell(s)
[rebuild] INCOMPLETE: 1 curation record(s) named a deposit that was not ingested. The stores are written and are a subset of the export — run `python -m bzk.sources.pride` and rebuild (OPERATIONS.md §5)
deposits_ingested: 3
site_observations: 4195
protein_observations: 4768
cells_staged: 272328
ingestions_skipped: 1
refusals: 48 {'residue_mismatch': 36, 'unresolved_protein': 11, 'no_razor_pick': 1}

done; the live home's graph and quant stores were not touched
```

The command's `grep -v` filtered out the per-record `replayed` lines and the
per-deposit `ingested` lines. Nothing else was removed.

---

## Scoring

| # | registered | measured | result |
|---|---|---|---|
| 1 | 4,916 rows; 0 spill | 4,916; 0 | held (MEASURED) |
| 2 | 148 dropped | 148 | held (MEASURED) |
| 3 | 0 empty groups | 0 | held (JUDGED) |
| 4 | 4,768 emitted | 4,768 | held (DERIVED) |
| 5 | 171,648 cells | 171,648 | held (DERIVED) |
| 6 | 57,216 per family | 57,216 × 3 | held (DERIVED) |
| 7 | positive cells: `lfq` 28,396; `intensity` 41,951; `ibaq` 41,951 | the same | held (MEASURED) |
| 8 | `lfq` | `lfq` | held (DERIVED) |
| 9 | 4,768 to 9,536; point ~5,700 | **5,408** | held; point estimate 292 high |
| 10 | 0 to 93; point 31 to 93 | **73** | held; the record's figure was wrong |
| 11 | no duplicate-group error | none | held (JUDGED) |
| 12 | 3 deposits; 4,195 sites; 4,768 protein obs.; 272,328 cells; 48 refusals; 1 skipped | the same | held (DERIVED) |

**Read as twelve of twelve only with its composition stated.**
- **Eight figures were instrument checks:** #1, #2 and #7 MEASURED, and #4, #5,
  #6, #8 and #12 DERIVED. They show that the adapter and the reviewer's scripts
  count the same bytes the same way, and that the code behaves as read. #7 is
  the strongest of them, because it agrees to the unit across three families.
- **Four were predictions: #3, #9, #10 and #11.** All four held. #9's 5,408 is
  1.13 accessions per group, which is consistent with the canonical Swiss-Prot
  reading of the search database. The anchor's ≈5.0 per group would have been
  wrong by a factor of about four.

**#10 corrects the curation record.** 20 of the file's 93 site-only rows are
also decoy or contaminant rows and are dropped with them. The record's FILTERS
item said the ingested observations "include those 93", which was written
without measuring the overlap. That item is corrected, dated, in the commit
that adds this document.

**A consistency check that was not registered, reported as such.**
- **Nodes:** node statements rose by 10,206 over the 10b run (22,582 →
  32,788). That equals the shotgun record's 16 plus the adapter's 12 Samples,
  1 Dataset, 1 Analysis, 4,768 observations and 5,408 proteins, which is exact.
- **Edges:** edge statements rose by 10,227. Take off 38 curation edges, 12
  `PRODUCED`, 1 `USED` and 4,768 `REPORTS_PROTEIN`, and 5,408 remain for
  `RESOLVES_TO_PROTEIN`. That would mean no accession sits in two groups.
- **The 38 is assumed, not measured.** It is the GG record's curation edge
  count, and the edge argument holds only if the shotgun record stages the
  same number. So the second half is an inference, not a measurement.

**Carried, unchanged:** the drift line (3,013 sequences checked then, 3,579
now). It was not caused by this run.
