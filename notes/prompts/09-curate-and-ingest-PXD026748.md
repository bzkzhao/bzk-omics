# PROMPT — complete the curation record for PXD026748 and ingest it

Working copy: /Users/bzk/bzk-omics
Runs only after 07 and 08 have landed. ADR-0035 is the governing record.

The site table has been copied in by hand before this prompt runs. Expected
sha256, computed by the reviewer on a separate copy:
`59000733f3b6b9fa8be31d4f8ae7e1868c0bb5099a8bbada580d28b3db647f50`
RECOMPUTE IT HERE. If it differs, the files differ — report and stop.


## Receipt checks

R1. Locate `GlyGly (K)Sites.txt`. Report path, bytes, sha256, data-row count and
    column count. If absent, STOP.

R2. `data/curation/curation_PXD018299.json` and `curation_PXD055843.json` —
    quote each one's `basis` and `confidence`, and the full field list of one
    mapping entry. This turn's record matches that shape.

R3. ONTOLOGY.md §5.3 — quote the `basis` enum's admitted values. Is there one
    for design derived from filenames? ADR-0035 and I8 both bear on this.

R4. ONTOLOGY.md §5 — quote the `quantity` enum in full, and say whether any
    value denotes a PER-MULTIPLICITY quantity.

R5. The ingest entry point for a MaxQuant sites deposit. Report the command,
    read from the repository, not from memory.

R6. `walk/PREREG-PXD026748-ingest.md` — quote its six registered figures with
    their intervals. This turn is measured against them.


## Registered expectations, and one the reviewer already measured

E1. Decoy/contaminant drop is 66 rows — 26 `Reverse`, 40 `Potential
    contaminant` — against PREREG's registered 25-70. Already measured by the
    reviewer on the separate copy; re-derive it here as a file-identity check.
E2. 2,653 data rows; after decoy/contaminant 2,587; after `Localization prob`
    < 0.75, **2,187**.
E3. The paper states **2,143** GG sites discovered. 2,187 - 2,143 = **44**.
    Neither the methods nor the deposit explains the gap. REPORT IT; do not
    reconcile it by trying rules until one fits — that is the error turn 07
    corrected.
E4. `___1`, `___2`, `___3` columns are present, global and per-run.


## The multiplicity question — carried from ADR-0034 and turn 08

The publication analysed the **expanded** site table. The adapter reads
`intensity_multiplicity_summed` by default. `quantity` is IDENTIFYING, so
declaring the wrong one mints a wrong `Analysis` id rather than failing.

**What this turn must do:** declare the quantity the PLATFORM's analysis
consumes, measured from the adapter rather than assumed; and record in the
curation record's `unresolved` that no enum value denotes the publication's
per-multiplicity quantity, so the published analysis cannot yet be declared
honestly. Do NOT extend the enum — that is a schema change with its own record.


## Task

1. Run R1-R6 and E1-E4. Report both. Stop conditions: R1 absent, or sha256
   mismatch.
2. Write `data/curation/curation_PXD026748.json`. Twelve GlyGly runs, two
   genotypes x two PLpro treatments x three replicates, conditions legible in
   every `Intensity` column name and every raw filename.
   Under ADR-0035: `Sample` is the material measured, so twelve samples;
   `treatment` names the full sequence; `timepoint_h` is 0.5.
   `basis` per R3. `content_hash` from R1 — never invented.
   `unresolved` MUST carry, each naming its consequence:
     - the pairing gap (ADR-0035 R4) — three cultures split two ways, not six
       independent replicates; unrecordable; a reconstruction cannot choose
       paired or unpaired;
     - the per-multiplicity `quantity` gap;
     - the 44-row gap between 2,187 and the paper's 2,143;
     - `replicate_type` — state what the deposit supports, and if it does not
       state biological vs technical, record `unspecified` as PXD018299 does
       rather than asserting.
3. Ingest. Report the refusal count with reasons, the multi-protein share at
   site grain, the isoform share among razor picks, and the decoy/contaminant
   drop.
4. **Compare every figure to R6's registered intervals.** For each: held, or
   missed by how much and in which direction. A miss is a result. Do not adjust
   a rule to bring a figure inside its interval.
5. Key the 296 published claims from Nature Immunology Supplementary Table 1
   against the ingested sites IF that file is on disk. If not, say so and skip.
   Do not fetch it.
6. Commit the curation record and any fixture separately from the report. Push.
7. Write the report to `notes/reports/09-ingest-PXD026748-report.md`; commit it.


## Out of scope

Any reconstruction of the Perseus analysis — blocked by ADR-0034's imputation
question and ADR-0035's pairing gap, both at the same stage. Extending the
`quantity` enum. Adding any field to `Sample`. Any FragPipe work. PXD065158.
Screening against C0. Amending ONTOLOGY.md, schema.py or any invariant.
The four off-repo documents — turn 10. The standing defect list: the tautology
sweep's stale floor; `resolve` not caching errors; `resolve` splitting
accessions on a hyphen; `Resolution` collapsing deleted and gene-less active
entries; the snapshot cache storing no synonyms; `Reverse` / `Potential
contaminant` absent from `REQUIRED_COLUMNS`; `pxd018299_refusals.json` carrying
no date; `SUPP_DATA_3`'s label; `distinct_gene_multi`.


## Report

R1-R6 quoted. E1-E4 measured. The curation record's path, and every field whose
value was a judgement rather than a reading. Every measured figure against its
registered interval. Everything refused, with reasons. Commit SHAs and push.
Anything you could not verify either way.
