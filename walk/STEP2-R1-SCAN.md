# STEP2-R1-SCAN — requirement-1 scan across the §6 candidates

**2026-09-17. Against WALK-STANDARD v1. Working copy: `/Users/bzk/bzk-omics`.**

Publication sources only. No deposit was touched, nothing downloaded.

**Method of discovery, stated as the standard requires:** six search-engine
queries and one full-text retrieval of the Genome Biology article HTML
(`link.springer.com/article/10.1186/s13059-026-04034-w`). Supplementary items
were enumerated by following the in-text `MOESM` anchors in that retrieved full
text and reconciling them against the Results narrative. **The recorded term set
of WALK-STANDARD §4 source 1 was not applied** — this was reading, not a
systematic full-text search. Source 1 is therefore *not exhausted* for any
candidate.

**Grade: P throughout.** Deepest grain reached: **G1** (item), once.

**No FAIL is recorded below, and none is available from this pass.** Under §2, a
FAIL needs G4 on every listed item. Everything here is PASS-provisional or
UNRESOLVED.

---

## 1. Genome Biology 2026 — the strongest candidate

Eggermont et al., *Proteomics and tracer metabolomics link GAPDH ISGylation to
glycolytic control*, Genome Biology 27:135 (2026),
doi:10.1186/s13059-026-04034-w. Impens lab, Ghent. Open access.

**Supplementary listing, enumerated at G1:**

| item | contents as stated in text | bearing on R1 |
|---|---|---|
| Additional file 1 (MOESM1) | Figs S1–S10 | none |
| Additional file 2 (MOESM2) | Tables S1–S6 | **S1 is the candidate** |

Table S1 is cited in text as accompanying the significantly regulated GlyGly(K)
sites after unsupervised hierarchical clustering. S2 shotgun proteomics, S3
significantly regulated proteins, S4 metabolomics, S5 GAPDH sites across
studies, S6 plasmids.

- **R1 — PASS-provisional at G1.** Site-grain claims are asserted in the main
  text (counts of ISG15 sites on proteins, and of ubiquitin sites, per cluster),
  and a table is pointed at. Not confirmed: row unit, identifier column,
  position column. Under §2 a PASS needs G2+, so this is not yet a PASS.
- **R2 — UNRESOLVED.** The retrieved text truncated inside the LC–MS/MS methods,
  before data analysis. Source 5 not exhausted.
- **Deposit accession — UNRESOLVED.** Data availability not reached. Until it
  is, this candidate has no deposit, only a publication.

**Two things about this candidate that are more important than its R1 status.**

*Additional file 2 is one file holding six tables.* This is the multi-sheet
workbook case §4 source 3 flags. Whether S1–S6 are sheets of one workbook or
separate files inside an archive is unknown, and it changes what "opening the
item" means.

*The published claim set may not be gated on the stated statistic.* The claims
are membership of a cluster — a two-sample test, then unsupervised hierarchical
clustering, then a judgement that the sites are absent in the knockout arm. The
anchor's claim set is gated on a threshold; this one is gated on a partition.
See §5 below.

---

## 2. iScience 2024 — HERC5-dependent ISGylome

Zhao, Perez, Faull, Chan, Munting, Canadeo, Cenik, Huibregtse, *Cellular targets
and lysine selectivity of the HERC5 ISG15 ligase*, iScience 27:108820 (2024),
doi:10.1016/j.isci.2024.108820. UT Austin. Open access (CC BY-NC-ND).

- **R1 — UNDETERMINED.** Supplemental listing not retrieved. Site-grain claims
  are asserted in the abstract (thousands of modified lysines across over a
  thousand proteins), which is a strong prior and no evidence at all.
- **Two corrections to the §6 row.** The system is **A549 and A549-HERC5KO**,
  not unspecified human cells. And the study carries a **parallel mouse arm**
  (mHERC6 selectivity comparison). A mixed-species deposit raises the same keying
  problem flagged for Zhang 2019, inside a single candidate.
- **CC BY-NC-ND** is worth noting before any derived artefact is committed.

---

## 3. Zhang 2019 / Impens — species question answered

*The in vivo ISGylome links ISG15 to metabolic pathways and autophagy upon
Listeria monocytogenes infection*, Nat Commun 10:5383 (2019).

- **Species — mouse, confirmed at G0.** Determined indirectly: the Genome
  Biology paper describes this work as modification of metabolic enzymes in the
  livers of infected mice. Indirect, and sufficient to act on.
- **Out of scope on species grounds, pending your call.** Per §7 of the brief,
  cross-species keying is worse than sequence-version drift. R1 is
  **NOT-REACHED**, gated on scope rather than on evidence.

---

## 4. Not reached this pass

| candidate | state |
|---|---|
| **PXD065158** | **SUPERSEDED 2026-09-17 by `walk_PXD065158.json`.** M1 closed: it is the Genome Biology deposit, and §1 above is the same candidate as this row. The file-count argument made here was wrong; the correction is recorded in that file. §1's R1 verdict of "PASS-provisional" is not in the standard's vocabulary and is superseded there too. |
| **PXD055843** | Not searched this pass. Its `S2_GG` sheet is the R1 candidate and is already in hand. Cheapest remaining check. |
| **Unpublished USP18 GlyGly set** | Open channel under I18. UNRESOLVED by construction until 21 September; can never carry a FAIL. |
| **The four already-walked deposits** | Not re-examined. `PXD074990`'s verdict is void under WALK-STANDARD §5 and needs re-determination, not inheritance. |

---

## 5. Proposed amendment to WALK-STANDARD, for decision

R2 as written asks only that a methods section state a statistical criterion.
The Genome Biology candidate shows that this is not the requirement the walk
actually needs. A paper can state a test, a correction and a threshold in full,
and still select its published claim set by something else — here, cluster
membership plus an absence judgement across a knockout arm.

A reconstruction that chooses BH on Welch has nothing to disagree with in that
case. It would not withdraw support from the claims; it would be measuring a
different selection step. That is D1, not D5.

**Proposed R2, v2:** *a methods section stating the statistical criterion that
selects the published claim set* — and a recorded judgement, at G2 or deeper, of
whether the stated criterion is the selecting one or merely an upstream filter.

This tightens the filter and will cost candidates. It also stops the walk from
producing a fraction that answers a question nobody asked. Your call — it
changes what R2 PASS means, so it is a version bump, not an edit.

---

## 6. Manual check sheet

In order. Each closes a named grain on a named requirement.

**M1 — Is PXD065158 the Genome Biology deposit?**
Open the Genome Biology article's Data availability section and record every
accession it names. Then open the PRIDE record for PXD065158 and compare title,
submitter, cell line, genotype arms and linked publication.
*Closes:* whether §6 has six candidates or five. *Grain:* G0. *Two minutes.*

**M2 — Open Additional file 2 of the Genome Biology paper.**
Record: whether it is one workbook or several files; the sheet count; for Table
S1, the header row, whether an accession or gene column is present, whether a
position column is present, and whether the row unit is the site.
*Closes:* R1 at G3/G4, PASS or not. *This is the single most valuable check on
the sheet.*

**M3 — Read the Genome Biology data-analysis methods in full.**
Record the test, the correction, the threshold, any s0, the software and version,
and — for the amendment above — whether the published claim set is selected by
that criterion or by the clustering.
*Closes:* R2, and the D5-vs-D1 question.

**M4 — Retrieve the iScience supplemental listing.**
From the Cell Press article page, enumerate every supplemental item and record
its stated contents. Open any item that could carry site-grain claims.
*Closes:* R1 for the iScience candidate at G1, then G2+.
*Also record:* whether human and mouse claims share a table, and how they are
distinguished.

**M5 — PXD055843: open the paper's supplementary listing.**
The `S2_GG` sheet is already curated. Record whether the *publication* presents
a site-grain significant table, and whether it is that sheet.
*Closes:* R1 for PXD055843, and with it whether clearing the I15 block is worth
it.

**M6 — Re-determine PXD074990.**
Under §5: record the original pointer verbatim, its failure mode, and walk the
recovery ladder rung by rung. Do not inherit the previous verdict.

M1 and M2 together decide most of this. M6 is the one that fixes the defect the
standard exists for.

---

## 7. What this pass licenses

One provisional R1 at G1. One species determination. Two corrections to the
candidate table. Zero FAILs, zero exhausted sources, zero deposits touched.

The §5 countable cannot be reported yet: no denominator exists until curatability
is determined for at least one R1-failing candidate, and no candidate has failed
R1.
