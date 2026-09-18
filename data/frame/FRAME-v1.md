# FRAME v1 — the ISGylation deposit frame, built and judged

**2026-09-17.** Built to FRAME-SPEC v1 against the PRIDE v3 search API.
Counts below are measurements; the membership calls are judgements and are
labelled as such.

---

## Counts

| | n |
|---|---|
| unique projects returned by the term set | 95 |
| term-confirmed locally across the four fields | 73 |
| after the conditional-term rule (secondary enzymes need a modifier co-hit) | **53** |
| **Frame B — site-directed enrichment, judged** | **11** |
| undecided between A and B | 5 |

Frame A is not yet 53: the §5 membership test (ISG15 as subject, not mention)
has been applied only to the B candidates. The remaining rows are term-confirmed
and unjudged.

---

## Frame B — 11 deposits

| accession | files | title |
|---|---|---|
| `PXD011513` | 40 | Proteomics-based identification of ISG15 modification sites during Listeria monocytogene |
| `PXD018299` | 39 | Deep analysis of the USP18-dependent ISGylome and proteome unveils important roles for U |
| `PXD026748` | 27 | Proteome-wide identification of ISG15 sites targeted by SARS-CoV-2 PLpro |
| `PXD032078` | 77 | Proteomics-based identification of ISG15 modification sites in vivo upon Coxsackie virus |
| `PXD032267` | 27 | Proteome wide screening for ubiquitination, ISGylation and NEDDylation sites in wildtype |
| `PXD044834` | 60 | Cellular Targets and the Lysine Selectivity of the HERC5 ISG15 Ligase |
| `PXD055843` | 56 | USP24 is an ISG15 cross-reactive deubiquitinase that mediates IFN-I production by de-ISG |
| `PXD065158` | 39 | Proteome-wide identification of ISG15 sites in HeLa cells |
| `PXD068808` | 35 | Global ISGylome analysis to identify substrates of SARS-CoV-2 Nsp3-PLpro |
| `PXD071724` | 22 | Mapping ISG15 sites on GAPDH and PGK1 by AP-MS |
| `PXD075835` | 52 | Mapping ISG15 sites in HeLa cells during MPXV virus infection |

**Evidence class:** each carries an explicit remnant-enrichment statement — GlyGly or di-Gly peptidomics, diglycine-remnant enrichment, anti-K-ε-GG immunoaffinity, or PTMScan IAP — in the title, description or sample protocol. Not inferred from the modifier term.

**Relation to the handoff §6 candidate list.** §6 named six candidates. Frame B contains **eleven**, of which **six are new to it**: `PXD026748`, `PXD032267`, `PXD044834`, `PXD068808`, `PXD075835`, and `PXD011513` (§6 had this one as *Zhang 2019 / Impens*, unaccessioned). `PXD044834` is the iScience HERC5 deposit whose accession was recorded unknown in the M4 walk record — now closed.

---

## Undecided — 5

| accession | why undecided |
|---|---|
| `PXD001805` | GlyGly set as a **variable modification** in the search, 2 files. Searching for a remnant is not enriching for one. Radoshevich Listeria, SILAC pulldown. |
| `PXD053712` | GlyGly as a **dynamic modification**, 7 files, targeted HERC5/N-protein work rather than proteome-wide. |
| `PXD071548` | `ubiquitin remnant (K-gg; +114.043 Da)` named as a considered modification, 12 files. Could be enrichment; the protocol text does not say. |
| `PXD045154` | di-glycine among variable modifications; the study is replication-fork biology, so ISG15 subject-hood is also in question. |
| `PXD051575` | Matches on ISG15's **own C-terminal diGlycine motif** — the LRLRGG, not a remnant. Almost certainly not B; kept here because the call is mine. |

Each needs the full sample protocol read. None can be resolved from a pattern.

---

## Detector history — recorded because a passing control is not a passing detector

| version | B | fault |
|---|---|---|
| v1 | 5 | ran on title and a 300-character `dataProcessing` field; **missed the anchor**. The two text fields it needed were never written out. |
| v2 | 21 | all four controls passed. `modification site` matched MaxQuant's *only identified by site* filter column and generic search-parameter text. |
| v3 | 18 | `di.?gly` matched **"Accordingly"** — `di` + any char + `gly` inside the word. Two false positives. |
| v4 | 17 | word boundaries fixed; controls still pass. Remaining 6 separated by judgement, not by pattern. |

**The controls only ever tested sensitivity.** All four passed at v2, v3 and v4 while precision moved from bad to acceptable. A positive-control set cannot catch a detector that is too generous — the same asymmetry WALK-STANDARD §2 states for absences, arriving here from the other direction.

---

## What this does to the walk

The §5 countable's denominator is Frame B, not six. Curatability and requirement 1 now have to be determined across **eleven** deposits, of which two are already done — `PXD065158` passes R1, `PXD055843` fails it with curatability passing.

That is a materially larger job than the handoff's plan, and it is the job the handoff's own §5 asks for.
