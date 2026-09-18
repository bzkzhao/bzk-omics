# PRE-REGISTRATION — PXD026748 GlyGly ingest

**Registered 2026-09-17, before any run. Working copy: `/Users/bzk/bzk-omics`.**

Per the project's standing convention: expected outcomes are registered before a
run that produces a number to be compared against a recorded baseline. Each
figure below carries its basis and the direction it is expected to move relative
to the anchor, with what would falsify it.

**Anchor figures are quoted as BASIS only.** Their homes are `ROADMAP.md`
§ *Measured findings* and `ONTOLOGY.md` §8; nothing here re-homes them.

**Instrument:** `bzk/adapters/maxquant_sites.py` over
`20210616_GlyGly_PRIDE.zip → GlyGly (K)Sites.txt` (3.8 MB), with a curation
record for the 12 GG runs.

---

## The two facts that move every prediction

**1. The search database contained isoforms and unreviewed sequences.** The
paper's Data availability says so explicitly: *"human, including isoforms and
unreviewed sequences"*, UniProt January 2021, 20,621 sequences. That pushes
isoform and TrEMBL prevalence **up** relative to a reviewed-only search.

**2. The search is roughly two years less stale than the anchor's.** January
2021 against the anchor's late-2018 acquisition, so there is about two years
less UniProt drift for the residue check to catch. That pushes refusals **down**.

The two act in opposite directions and I do not know which dominates. The
intervals below are wide because of that, not despite it.

---

## Registered figures

| # | quantity | registered | basis |
|---|---|---|---|
| 1 | rows in `GlyGly (K)Sites.txt` before any filter | **2,143 to 2,400** | The methods state 2,143 GG-modification sites were discovered and listed in this table. MaxQuant site tables also carry reverse and contaminant rows, which that count probably excludes, so the raw row count should meet or exceed 2,143. |
| 2 | rows dropped by `drop_decoys_and_contaminants` | **25 to 70** | The anchor dropped 43 of 2,341, about 1.8%. Same tool, same conventions, comparable table size. |
| 3 | **refusals at resolution** | **17 to 55**, point estimate **30** | The anchor refused 27 on roughly 2,030 sites, about 1.3%. Applied to a similar table size, adjusted down for less drift and up for an isoform-bearing database. |
| 4 | share of sites whose `candidate_proteins` names more than one protein | **70% to 90%** | The anchor measured 82% at site grain. Same enrichment chemistry, same search engine family, comparable database. This is the prediction I expect to hold most firmly. |
| 5 | share of razor picks that are isoform accessions | **20% to 40%** | The anchor measured 30%. The isoform-bearing database pushes up; nothing pushes down. |
| 6 | of the 296 published claims, how many key to an ingested site | **285 to 296** | Supplementary Table 1 carries numeric positions, zero isoform hyphens and zero multi-accession cells, so losses should come only from refusals. |

---

## What each outcome would mean

**Refusals far below 17.** The drift effect dominates, and deposit age is a
stronger predictor of keying survival than anything else measured. That is worth
knowing before the countable is interpreted, because it would mean the fraction
partly tracks when a deposit was searched.

**Refusals far above 55.** The isoform-bearing database dominates, and I17 and I2
do more work here than on the anchor. Expect `reviewed_preferred` keying and
`displaced_protein` to be populated at a higher rate.

**Multi-protein share far below 70%.** The anchor's 82% is not a property of
GlyGly data but of that deposit's particular razor behaviour. That would be a
genuine finding and would weaken I14's justification, which cites the 82% as
evidence that ambiguity is the default path rather than an exception.

**Published claims keying below 285.** Something is wrong with either the
reconciliation or the assumption that the published table is a subset of the
search output. Stop and diagnose rather than record the number.

---

## Deliberately not predicted

**The imputation burden.** The anchor's generated fraction at site grain is
recorded in its dated home; PXD026748's Perseus stage cannot be reproduced
without the unstated imputation parameters, so any number here would be a
property of a choice I made rather than of the deposit. Registering a prediction
for it would be registering my own future decision.

**The D5 fraction itself.** It is the object of the study. Predicting it before
the instrument runs would invite fitting the instrument to the prediction.

---

## Track record disclosed, because it bears on how to read the intervals

Three predictions made earlier today and their outcomes:

| predicted | actual |
|---|---|
| frame A at 25 to 60 | 73 term-confirmed |
| Frame B, first detector | 5, then 21, then 11 after two fixes |
| PXD026748's file count reconciling to 27 | 26, unresolved |

The frame miss had a diagnosable cause — secondary enzyme terms placed in the
unconditional row — but it was still a miss. The intervals above are wider than
I would have set this morning, and that is deliberate rather than hedging: a
narrow interval that misses teaches less than a wide one that holds, and today
has provided evidence about which I produce.

---

## Committed before the run

This file is registered before the adapter is pointed at the deposit. If it is
amended after a number is known, the amendment is a defect and not a correction.
