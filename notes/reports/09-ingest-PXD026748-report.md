# Report — complete the curation record for PXD026748 and ingest it

**Run at:** 2026-09-19 · **Opened at:** `c93e9f1` (one ahead of `origin/main`, the `.gitignore` fix) · **Record:** `data/curation/curation_PXD026748.json` · **Commits:** `624d10e`, and this report's own · **Pushed**

**Headline.** Ingested: 2,166 sites, 21 refused, all for residue mismatch, and 51,984 quantitative cells. **Three of the six registered figures held and three missed.** The multi-protein share came in at **9%** against a registered 70–90%, and isoform razor picks at **0%** against 20–40%. **The deposit's own protocol contradicts the split-lysate premise in ADR-0035**, so the record's `unresolved` states the contradiction rather than the premise. The suite is green, and turns 06 and 07 misread a failure in it; see *Correction to reports 06 and 07*.

---

## Receipt checks

### R1 — the site table

| | |
|---|---|
| path | `/Users/bzk/bzk-omics/GlyGly (K)Sites.txt`, git-ignored since `c93e9f1`; stored this turn at `~/.bzk-omics/raw/59000733…647f50/GlyGly (K)Sites.txt` |
| bytes | 3,767,240 |
| sha256 | `59000733f3b6b9fa8be31d4f8ae7e1868c0bb5099a8bbada580d28b3db647f50`. **Matches the reviewer's digest**, so no stop |
| data rows | **2,653**. All have a numeric `id`, and no row has the wrong width |
| columns | **195** |

### R2 — the shape of the existing records

| record | `basis` | `confidence` |
|---|---|---|
| `curation_PXD018299.json` | `publication_methods` | `inferred` |
| `curation_PXD055843.json` | `submitter_metadata` | `inferred` |

A mapping entry's full field list, from PXD018299's `Ratio mod/base WT_1`: `genotype`, `treatment`, `timepoint_h`, `replicate`, `replicate_type`, `source_type`, `cell_line`, `organism_taxid`. This turn's record uses exactly those eight.

### R3 — §5.3's `basis` enum

`sdrf` → `authoritative`; `author_correspondence` → `authoritative`; `submitter_metadata` → `inferred`; `publication_methods` → `inferred`; **`filename_inference` → `inferred`, *"Deduced from raw file naming conventions"***.

**Yes, there is a value for a design derived from filenames, and it is used.** I8 bears on it directly: *"Experimental design inferred from filenames is never presented as though it came from the submitters."*

### R4 — the `quantity` enum (`ONTOLOGY.md:474-483`)

`'intensity' | 'intensity_multiplicity_summed' | 'ratio_mod_base' | 'lfq' | 'ibaq'`, with the comment: *"Per-multiplicity consumption (the ___n split) is deferred — extend the enum when a per-multiplicity analysis is actually run."* **No value denotes a per-multiplicity quantity.**

### R5 — the ingest entry point, read from the repository

**`python -m bzk.rebuild`.** There is no console script; `pyproject.toml` has no `[project.scripts]`. It replays every `data/curation/curation_*.json` record. For each deposit whose `content_hash` is in `~/.bzk-omics/raw/`, which is located by digest and re-hashed, it runs `MaxQuantSiteAdapter`, configured from the record by `_adapter_for`: `search_engine`, `search_engine_version`, `acquisition_mode`. It sets no `localization_threshold` and no `quantity`, so the adapter defaults apply: **0.75** and **`intensity_multiplicity_summed`**.

`python -m bzk.sources.pxd018299_sites` is the older per-deposit, measure-only entry point. It is hard-wired to the anchor.

### R6 — the six registered figures, quoted

| # | quantity | registered |
|---|---|---|
| 1 | rows in `GlyGly (K)Sites.txt` before any filter | **2,143 to 2,400** |
| 2 | rows dropped by `drop_decoys_and_contaminants` | **25 to 70** |
| 3 | refusals at resolution | **17 to 55**, point estimate **30** |
| 4 | share of sites whose `candidate_proteins` names more than one protein | **70% to 90%** |
| 5 | share of razor picks that are isoform accessions | **20% to 40%** |
| 6 | of the 296 published claims, how many key to an ingested site | **285 to 296** |

---

## Expectations

These were measured directly from the file with a stand-alone reader, independent of the adapter, and the adapter later agreed on every one.

| # | expected | measured |
|---|---|---|
| **E1** | 66 dropped: 26 `Reverse`, 40 `Potential contaminant` | **Held**: 26 + 40, none carrying both flags, 66 in all. The file is the reviewer's file |
| **E2** | 2,653 → 2,587 → **2,187** | **Held exactly**. No kept row has a blank `Localization prob` |
| **E3** | 2,187 − 2,143 = **44** | **Held.** The PRIDE data-processing text states *"the discovery of 2143 GG-modification sites (listed in the GlyGly(K) site table)"*. **Reported, not reconciled.** No rule was tried to close it |
| **E4** | `___1`/`___2`/`___3` present, globally and per run | **Held**: `Intensity___1..3` globally, plus 36 per-run `Intensity … ___n` columns (12 runs × 3). `Intensity` is the only `___n` family, and the file has **no `Multiplicity` column** |

---

## The curation record

`data/curation/curation_PXD026748.json`. It loads through `bzk.curation.loader` to **16 nodes** (1 Project, 1 Experiment, 1 Dataset, 1 curation Analysis, 12 Sample) and **38 edges**, which is the anchor record's shape exactly. `invariants.validate` runs inside the loader.

### Fields that are a judgement rather than a reading

| field | value | why it is a judgement |
|---|---|---|
| `basis` | `filename_inference` | The column-to-condition mapping comes from the run names; the treatment parameters come from submitter-written PRIDE text. I chose the weaker, filename source, because the mapping is what curation fixes and I8 forbids presenting it as the submitters'. `submitter_metadata` was the alternative, and both carry `inferred` |
| `project.title` | *SARS-CoV-2 PLpro deISGylation of host proteins* | A new research question gets a new Project, under the anchor record's own scoping note |
| `experiment.title` | *HeLa ISG15 knockout diGly proteomics, IFN-alpha then lysate PLpro wild-type vs mutant* | Written to carry every discriminator the anchor's scoping note asks for |
| `genotype` | `WT` / `ISG15-/-` | The deposit writes `Isg15-/-`. I normalised to the HGNC symbol for the human gene. **`genotype` is identifying, so this choice fixes the Sample ids** |
| `treatment` | *IFN-alpha 500 U/mL 72 h; then lysate + recombinant SARS-CoV-2 PLpro {WT \| mutant} 1:50 w/w 30 min 37 C* | ADR-0035 R1 says to name the full sequence; the string format is mine |
| `timepoint_h` | `0.5` | From ADR-0035 R1, the governing record's judgement, applied as written |
| `replicate_type` | `unspecified` | The prompt's rule, and the anchor's practice. See `unresolved` |
| `contrasts_of_interest` | PLpro WT vs mutant within WT, and the same within ISG15-/- as a negative control | The curator's statement of interest. The publication ran a two-way ANOVA, not these contrasts, and each note says so |
| `curated_by` | `null` | As in both existing records |

**Read, not judged:**

- `accession`, `file` and `content_hash` (from R1);
- `search_engine` `maxquant` and `search_engine_version` `1.6.17.0`;
- `acquisition_mode` `dda` (*"operated in data-dependent mode"*);
- `instrument` `Q Exactive HF`;
- all twelve mapping keys, which are the actual `Intensity <run>` headers;
- `replicate` 1–3 from `_repN`;
- `cell_line` `HeLa` and `organism_taxid` 9606.

### `unresolved`, and one entry the governing record gets wrong

Each entry names its consequence.

1. **PAIRING: ADR-0035's premise is contradicted by the deposit, and the record says so rather than asserting the premise.** ADR-0035 and `WALK-STANDARD` v2's R5 row describe the PLpro axis as *"three cultures split two ways, not six independent replicates"*. The deposit's own sample-processing protocol, held in `data/frame/frame_raw.tsv`, says:
   > five millions cells of each genotype were seeded in triplicate for each condition (WT or mutant PLpro) in 12x150 mm2 culture dishes

   and *"7.2 mg total protein of each replicate was treated with recombinant WT or mutant PLpro"*. **That is twelve separately seeded dishes, one per sample, and no lysate split.** What survives is narrower: whether same-index replicates were processed as blocks is unstated, the schema could not record a block if one existed, and the publication does not say whether its ANOVA used one. The consequence stands either way: a reconstruction cannot choose its model from the deposit. **Writing "three cultures split two ways" into the record, as the prompt specified, would have asserted what the data contradicts.** The record states the contradiction instead and says that ADR-0035's Context and R2 should be re-examined at its review. **ADR-0035 was not edited.**
2. **QUANTITY.** No enum value denotes the publication's per-multiplicity quantity. The PRIDE text says *"the site table was expanded"*. The platform's analysis consumes `intensity_multiplicity_summed`. I measured that from the adapter, not assumed it: `DeclaredSiteAnalysis`'s default, which `rebuild._adapter_for` does not override, printed as `quantity='intensity_multiplicity_summed'` by the measurement run. Declaring the published analysis with the summed quantity would mint a wrong `Analysis` id. **The enum was not extended.**
3. **SITE COUNT.** 2,187 filtered against the stated 2,143, a gap of 44, unexplained. Consequence: published claims are keyed individually rather than by assuming the populations match.
4. **REPLICATE TYPE.** Recorded as `unspecified`. The protocol supports separately seeded dishes, which rules out repeated injection of one sample, but it never says "biological" or "technical".
5. **PLpro MUTANT.** The deposit says only *"mutant PLpro"*. The walk record's *"catalytically-dead"* is not in the deposit and is not written into `treatment`.

---

## The ingest

The ingest ran twice, and the two runs agree on every figure:

- **a measure-only parse** through `rebuild._adapter_for`'s exact configuration, with nothing written, which printed every figure below;
- **the real ingest**, `python -m bzk.rebuild`, which wrote the graph.

I copied the derived stores (`graph.kuzu` 82 MB, `quant.duckdb` 5.8 MB) to job scratch before the rebuild.

```
[rebuild]   ingested HAP1_USP18KO_GlyGlyKSites.txt via maxquant: 2029 site(s), 27 refused, … 48,696 quantitative cell(s)
[rebuild]   ingested GlyGly (K)Sites.txt via maxquant: 2166 site(s), 21 refused, 9762 node statement(s), 10740 edge statement(s), 51,984 quantitative cell(s)
[rebuild]   no adapter recognises Supplementary_Data_S1_TP.xlsx; sites not ingested
[rebuild] INCOMPLETE: 1 curation record(s) named a deposit that was not ingested.
```

**The anchor is unchanged** at 2,029 sites and 27 refused, matching `pxd018299_refusals.json`'s 27. **The `INCOMPLETE` line predates this turn.** PXD055843's record names a supplementary spreadsheet that no site adapter reads, and nothing in this turn touched it. I did not trust the exit status I captured, because `time` wrapped around the pipeline scrambles zsh's `pipestatus`. `main()` exits 1 on that condition.

| stage | count |
|---|---|
| rows read | 2,653 |
| − decoy / contaminant | 66 |
| − localisation < 0.75 | 400 |
| considered | 2,187 |
| − no razor pick | **0** |
| − protein unresolved | **0** |
| − **residue mismatch** | **21** |
| sites emitted | **2,166** |
| I17 promotions | 0 |

**Nodes:** Analysis 1, Dataset 1, Gene 1,030, ModificationSite 2,166, Modifier 3, ModifierAssignment 2,166, Protein 1,184, ProteinSequence 1,033, Sample 12, SiteObservation 2,166. **Cells:** 51,984, which is 2,166 × 12 × 2.

### Everything refused, with reasons

All 21 are `residue_mismatch`: the search reported K, and today's UniProt sequence has something else at that position. They fall on **9 proteins**, in clusters, which is the shape of a sequence amended since the search rather than of scattered error:

| accession | version | rows | today's residue at the reported positions |
|---|---|---|---|
| P08195 | sv4 | 475–479 | V, A, N, L, L (K171, K122, K166, K147, K160) |
| P49411 | sv3 | 1201–1203, 1206–1207 | D, L, S, G, A (K256, K234, K238, K347, K79) |
| Q9NVI7 | sv3 | 2433, 2436, 2438 | H, M, L (K472, K553, K549) |
| Q03518 | sv3 | 1684–1685 | L, L (K422, K449) |
| Q9BYK8 | sv7 | 2327–2328 | T, V (K2550, K2491) |
| Q16850 | sv4 | 1924 | N (K436) |
| Q66PJ3 | sv3 | 1985 | **past the end** (K370) |
| Q8NI36 | sv2 | 2109 | T (K159) |
| Q9UP83 | sv4 | 2553 | A (K724) |

9 proteins, 21 rows. A first draft of this report said *11 proteins*; that was a miscount, corrected against the refusal list before commit.

**Network:** the measurement parse resolved razor picks through the repository's own resolver. `~/.bzk-omics/cache/uniprot` went from **7,499 to 9,149 files (+1,650)** over 5 min 26 s, and the rebuild then ran from cache. The rebuild reports that the sequence archive is now **3,579 sequences against the 3,013 last drift-checked**. `python -m bzk.drift` was **not run**; it was not asked for.

---

## Every figure against its registered interval

| # | registered | measured | verdict |
|---|---|---|---|
| 1 | raw rows **2,143–2,400** | **2,653** | **Missed, above, by 253.** The basis assumed the stated 2,143 was the table's post-filter size, with raw ≥ 2,143, and was right in direction. After filters it is 2,187; raw includes 66 decoy/contaminant rows and 400 below-threshold rows the basis did not size |
| 2 | decoy/contaminant **25–70** | **66** | **Held**, 4 inside the upper bound |
| 3 | refusals **17–55**, point **30** | **21** | **Held**, 9 below the point estimate. 21 / 2,187 = 0.96%, against the anchor's 27 on about 2,030 (1.3%) |
| 4 | multi-protein share **70–90%** | **9.0%** (232 / 2,587, the anchor's denominator: rows after decoy/contaminant). 9.4% after the localisation filter (205 / 2,187); 9.4% of emitted observations (203 / 2,166) | **Missed, below, by 61 points.** The interval was missed entirely, on the figure the PREREG said it *"expect[ed] to hold most firmly"* |
| 5 | isoform razor picks **20–40%** | **0 / 2,187 rows = 0%**; 0 / 1,033 distinct picks. **No isoform accession appears among any of the 1,185 candidates** | **Missed, below, by 20 points.** The interval was missed entirely |
| 6 | claims keyed **285–296** | **288 / 296** | **Held**, 3 inside the lower bound |

**Held 3, missed 3.** No rule was adjusted to move a figure. The two filters the adapter applies are the ones the publication states.

**What the PREREG itself says a miss on #4 would mean**, quoted rather than interpreted: *"The anchor's 82% is not a property of GlyGly data but of that deposit's particular razor behaviour. That would be a genuine finding and would weaken I14's justification, which cites the 82% as evidence that ambiguity is the default path rather than an exception."*

**A candidate explanation for #4 and #5, recorded as untested.** The PREREG's first "fact that moves every prediction" was that the search database contained *"human, including isoforms and unreviewed sequences"*, from the paper's Data availability. **The deposit's own data-processing text says otherwise:** *"spectra were searched against the human protein sequences in the Swiss-Prot database (database release version of January 2021), containing 20,621 sequences"*. 20,621 is about the size of reviewed human canonical-only. Zero isoform candidates in the whole table is what that text predicts. The anchor's record says it was searched *"against UniProtKB human"*. Whether that database difference drives 82% → 9% is **not tested here**. The anchor's 30% isoform figure was also **6 of 20**, a sample of twenty (`ROADMAP.md:168`), not a population share.

### Figure 6 in detail — the 296 published claims

`41590_2021_1035_MOESM3_ESM.xlsx` is **on disk**, in `~/Downloads`; 41590 is the Nature Immunology code. It was **not fetched**. I confirmed it as Supplementary Table 1 by shape against the walk record's R1: sheet `Table 1`, 296 data rows, and the walk's twelve columns in order. The walk records no digest, so the file's sha256 is `872371eb…a870`, recorded here for the first time. All 296 claims are `Multiplicity` 1.

I keyed on (`Uniprot ID`, `Lysine position`) against the ingested site key (razor pick, `Position`):

- **288** key to an emitted site.
- **2** key to a razor-pick row this run refused for residue mismatch: #122 ATAD3A Q9NVI7 K549 and #136 WDR36 Q8NI36 K159.
- **6** are absent: the pair appears nowhere in the table, as razor pick or as any candidate.

**The six absent claims, diagnosed and not re-counted.** All six are found **by sequence window**. Each is on a row whose razor pick *is* the published accession, but at a different position. In every case the published **position and gene name belong to the first-listed candidate protein in that row**, not to the razor pick:

| # | published | row's razor pick | first-listed candidate |
|---|---|---|---|
| 106 | P21333 FLNB K16 | P21333 K43 (id 200) | O75369, K16 |
| 141 | P60842 EIF4A3 K60 | P60842 K54 (id 1065) | P38919, K60 |
| 148 | P08238 HSP90AA1 K112 | P08238 K107 (id 456) | P07900, K112 |
| 169 | Q9BXB5 OSBPL11 K395 | Q9BXB5 K425 (id 2320) | Q9BXB4, K395 |
| 176 | P08238 HSP90AA1 K283 | P08238 K275 (id 459) | P07900, K283 |
| 215 | Q92973 TNPO2 K56 | Q92973 K66 (id 84) | O14787, K56 |

So **six published rows pair one protein's accession with another protein's position and gene name.** This probably also explains the walk record's open discrepancy, in which *"HSP90AA1 spans P07900 and P08238"* was read as paralogue collapse. Rows 148 and 176 carry P08238's accession with P07900's gene and position. That is a reading, **not verified further**.

The PREREG's basis for #6 said *"losses should come only from refusals"*. **That held for 2 of the 8 losses, not all of them.** The count stays 288, inside the interval.

**Also noticed, and left alone:** the table's caption says the sites were ranked *"after stringent filtering (p≤0.001)"*, while the PRIDE data-processing text says *"p-value less than 0,01"*.

---

## Checks

| check | target | result |
|---|---|---|
| `pytest` (full suite) | `tests/` via `.venv/bin/python` | **686 passed, 8 skipped** |
| `pytest tests/test_schema.py` | | **20 passed** |
| `ruff check` | `bzk tests` | **All checks passed** |
| `ruff format --check` | `bzk tests` | **97 files already formatted** |
| `mypy` | `bzk tests` | **no issues in 97 source files** |

**The one failure the new record caused, and its fix.** The first full run had two failures:

- `test_curation_loader.py::test_every_record_and_fixture_on_disk_still_loads` pinned **four** files on disk: two records and two synthetic twins. The new record made five. I moved the pin 4→5 and re-measured the docstring's key-set claim: no key set is shared by more than two files. **The guard was seen to fail before it moved**; the first run's message named all five files. This is a mirror of the kind `CLAUDE.md` point 3 describes, a count of `data/curation/` against a literal. It is closed by the test itself, now at five, and the next record will trip it in the same way.
- `test_tautology_sweep.py::test_every_classified_instance_re_runs_its_recorded_evidence` failed as a **knock-on**. The `test_drift.py` evidence's green scope is the *whole suite* (`("-q",)`) in a mutated copy, and that run included the failing pin. After the pin moved, it passed with no change of its own.

### Correction to reports 06 and 07

Those reports called the sweep's failure *"pre-existing"*, and 06 verified that by running it at `775ef51` in a worktree. **Both runs used `python3`, which here is `/Users/bzk/anaconda3/bin/python3`, and it cannot import `kuzu`.** The sweep re-runs the suite in a subprocess, which failed to collect (exit 4). That is pytest's usage-error code, and it was in the failure message I quoted without reading it.

Measured this turn: the same test **fails under `python3` and passes under `.venv/bin/python`** (1 passed, 56.5 s). So the failure pre-existed only in the wrong interpreter. **The repository was green in its own environment throughout.** The 34-pass and 29-pass figures in those reports ran under `python3` as well; they did not exercise anything that needs `kuzu`. Reports 06 and 07 are dated records and are not edited. This entry is the correction.

---

## Commits and push

| commit | contents |
|---|---|
| `c93e9f1` | `.gitignore`: `*GlyGly*Sites.txt` (the previous turn's, pushed with this one) |
| **`624d10e`** | `data/curation/curation_PXD026748.json`, and the record-count pin 4→5 in `tests/test_curation_loader.py` |
| this report | `notes/reports/09-ingest-PXD026748-report.md` and `notes/prompts/09-…` |

The push went `8fa187e..624d10e`. **No fixture was created.** The prompt allowed one but did not require it. `ROADMAP.md`'s *Measured findings* was **not** updated; this report is the only committed home for these figures.

**Nothing out of scope was touched:**

- no Perseus reconstruction;
- the `quantity` enum not extended;
- no field added to `Sample`;
- no FragPipe work, nothing on PXD065158, no C0 screening;
- `ONTOLOGY.md`, `schema.py` and the invariants not edited;
- **ADR-0035 not edited, although this turn contradicts its premise.**

**Left on disk:**

- the repository-root copy of `GlyGly (K)Sites.txt`, now ignored and a duplicate of the raw-store copy;
- the derived-store backups in job scratch.

---

## Could not verify either way

- **Whether same-index replicates were processed as blocks.** The protocol settles that the lysate was not split; it does not settle batching.
- **Why 2,187 ≠ 2,143.** The filters are the stated ones, and the gap of 44 is not explained by anything in the deposit.
- **Whether the database difference explains 9% against 82%** multi-protein, and 0% against 30% isoform. The paper's Data availability, which the PREREG quotes, and the deposit's PRIDE text disagree about what was searched. The paper is not on disk.
- **Whether the first-listed-candidate pattern in the six published rows is systematic** in how the table was built. It holds in 6 of 6 here, and explains the walk's HSP90AA1 discrepancy by reading; it was not tested further.
- **The Supplementary Table 1 file's provenance.** It is identified by name and shape. No digest was recorded before this turn.
