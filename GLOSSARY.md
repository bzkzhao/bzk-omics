# GLOSSARY.md

| Field | Value |
|---|---|
| Status | Draft |
| Version | 0.2 |
| Last reviewed | 2026-08-06 |
| Depends on | Nothing |
| Authoritative for | Definitions of terms used across all documents |

Additive only — terms are added, not removed. Where a definition here conflicts with usage elsewhere, this file wins and the other document is corrected.

---

## Biology

**Ubiquitin-like modifier (UBL)** — A small protein covalently conjugated to substrate lysines by an E1–E2–E3 enzyme cascade. Includes ubiquitin, NEDD8, ISG15, FAT10, SUMO and others.

**Ubiquitination** — Conjugation of ubiquitin (`uniprot:P0CG48`, `P0CG47`) to a substrate lysine. Regulates degradation, trafficking, signalling and DNA repair.

**ISG15** — An interferon-stimulated ubiquitin-like modifier (`uniprot:P05161`), structurally a ubiquitin dimer. Strongly induced by type I interferon.

**ISGylation** — Conjugation of ISG15 to substrate lysines, via the E1 UBA7, E2 UBE2L6, and E3 ligases including HERC5. Reversed by the deISGylase USP18.

**UBA7 / UBE1L** — The ISG15-specific E1 activating enzyme (`uniprot:P41226`). Its knockout abolishes ISGylation and is the cleanest orthogonal test for modifier identity.

**UBE2L6 / UbcH8** — The E2 conjugating enzyme for ISG15 (`uniprot:O14933`).

**HERC5** — The principal human ISG15 E3 ligase (`uniprot:Q9UII4`).

**USP18** — The deISGylating protease (`uniprot:Q9UMW8`); also a negative regulator of type I interferon signalling independent of its catalytic activity.

**NEDD8** — A UBL (`uniprot:Q15843`) conjugated principally to cullin scaffolds. Pharmacologically inhibited at the E1 step by pevonedistat (MLN4924), which provides a means of excluding NEDD8 as a candidate modifier.

**FAT10 / UBD** — A UBL (`uniprot:O15205`) induced by interferon-γ and TNF; also leaves a diglycine remnant.

**Type I interferon** — IFN-α/β. Induces the ISG transcriptional programme, including *ISG15*, *UBA7*, *UBE2L6*, *HERC5* and *USP18* — which is why interferon-stimulated conditions maximise modifier ambiguity in diGly data.

**ISG** — Interferon-stimulated gene.

---

## Mass spectrometry

**diGly / K-ε-GG** — The diglycine remnant left on a modified lysine's ε-amino group after tryptic digestion of a UBL conjugate. Mass shift +114.0429 Da; `unimod:121`.

**Modifier ambiguity** — The central methodological problem of this platform. Ubiquitin, NEDD8, ISG15 and FAT10 all terminate in a diglycine motif, so all four leave an indistinguishable K-ε-GG remnant. Neither precursor mass nor MS² fragmentation resolves which was present. SUMO does not share this property with trypsin, as its C-terminal sequence leaves a longer remnant.

**diGly enrichment** — Immunoaffinity purification of K-ε-GG peptides using an anti-K-ε-GG antibody, necessary because modified peptides are a vanishing fraction of the tryptic pool.

**Localisation probability** — The confidence, from the search engine, that a modification sits on a specific residue rather than an adjacent one within the peptide. A site with low localisation probability is a site on the wrong lysine.

**PSM** — Peptide-spectrum match. One assignment of one MS² spectrum to one peptide sequence.

**DDA / DIA** — Data-dependent and data-independent acquisition. DDA selects precursors for fragmentation by intensity; DIA fragments all precursors in fixed windows, improving quantitative completeness across samples.

**Sequence version** — The UniProt release-specific version of a protein sequence. Residue positions are only meaningful relative to one. Sites silently shift between versions when sequences are amended.

**DDA / DIA** — data-dependent and data-independent acquisition. DDA selects precursors for fragmentation by intensity; DIA fragments all precursors within fixed *m/z* windows, improving quantitative completeness across samples. The Pinto-Fernández group moved to DIA around 2022.

**Library-free DIA** — DIA analysis using a spectral library predicted computationally from the FASTA sequence database rather than built from separate DDA runs. Results are not directly comparable with experimental-library analyses, so `Dataset.library_type` records which was used.

**PAC** — protein aggregation capture. Bead-based sample preparation used for tissue lysates, typically automated on a KingFisher platform.

**mzML / mzTab** — HUPO-PSI standard formats for raw spectra and for reported identification and quantification results.

**SDRF-Proteomics** — Sample and Data Relationship Format; a tabular standard mapping raw files to samples and experimental factors. Rarely present on public submissions, which is why sample-to-condition mapping is often manual.

**MaxQuant / FragPipe / DIA-NN** — Search engines producing the site-level tables this platform ingests.

---

## Statistics

**Contrast** — A defined comparison between two groups of samples, e.g. IFN-β 8 h versus mock.

**log₂ fold change (log₂FC)** — Effect size for a contrast on a log₂ scale.

**Moderated *t*-test / empirical Bayes** — The standard test for small-*n* omics data, shrinking per-feature variance estimates toward a pooled prior (Smyth, 2004). Substantially better calibrated than a per-feature *t*-test at *n* = 3.

**Benjamini–Hochberg (BH)** — Procedure controlling the false discovery rate across many simultaneous tests.

**Stoichiometry** — The fraction of a protein's copies bearing the modification at a given site. Distinct from site abundance.

**Stoichiometry-uncorrected** — A site-level result not adjusted for its parent protein's abundance. Such a site may appear regulated purely because the protein is regulated, with no change in modification stoichiometry. The platform labels these explicitly rather than reporting them as modification changes.

**Protein-level adjustment** — Correcting a site-level log₂FC by the matched protein-level log₂FC, requiring a paired proteome dataset from the same samples.

---

## Platform

**Reference graph** — Nodes describing entities that exist independently of measurement, imported from external authorities and never authored locally.

**Evidence graph** — Nodes describing what this laboratory did and observed, authored locally and carrying provenance.

**Observation** — A node joining the two graphs: a measured claim about a reference entity within a stated experimental context.

**ModifierAssignment** — A defeasible inference about which UBL produced an observed diGly remnant, carrying its own basis and evidence chain. Immutable; superseded rather than edited.

**Sample-to-condition mapping** — The assignment of raw files to experimental conditions, replicates, and timepoints. Machine-readable where SDRF-Proteomics accompanies a submission; inferred from filenames, submitter metadata, or the publication's methods section where it does not. Without it there is no contrast, and therefore no statistics.

**Curation** — An `Analysis` with `kind = 'curation'`: a recorded act of asserting experimental design rather than measuring it. Carries a `basis` naming the source of the assertion and a `confidence` of `authoritative` or `inferred`. Immutable and superseded rather than edited, on the same footing as a modifier assignment.

**Inferred design** — A sample-to-condition mapping reconstructed from indirect evidence rather than supplied by the submitters. Labelled in every derived view and export, never presented as authoritative.

**Imputation** — Replacing a missing quantitative value with a generated one. Standard practice in proteomics because absence is ambiguous: the analyte may be genuinely absent or below detection. Perseus' default draws from a normal distribution downshifted 1.8 SD below the observed mean with width 0.3 SD. An imputed value is an inference, not a measurement, and is recorded as such (I15).

**Substantially imputed** — A result whose underlying values are more than half generated rather than measured. Labelled wherever it appears.

**Downshift** — The number of standard deviations below the observed mean at which imputed values are drawn. Encodes the assumption that missing means "present but below detection".

**Isoform** — An alternative sequence for a gene product, denoted by a suffix (`P09914-2`). Isoforms differ in length and residue numbering, so a position is only meaningful once the isoform is specified. Part of the `ModificationSite` key, not a property of it.

**Swiss-Prot / TrEMBL** — The reviewed and unreviewed sections of UniProtKB. Swiss-Prot entries are manually curated; TrEMBL entries are automatic. Search engines frequently select TrEMBL accessions as razor picks even when a reviewed entry is available.

**Position drift** — The silent failure where a residue position remains valid but refers to a different residue, because the underlying sequence was amended after the search. Invisible without a recorded sequence version.

**Razor peptide** — A peptide matching several proteins, which the search engine assigns to one of them by rule rather than by evidence. In PXD018299, 82% of GlyGly sites derive from peptides that could come from more than one protein — so the razor pick is an inference, not a fact.

**Protein assignment** — The inference about which protein a shared peptide actually derives from. The third `EvidencedInference` subtype, alongside modifier and enzyme.

**Ratio mod/base** — MaxQuant's modified-peptide intensity divided by unmodified protein signal: stoichiometry measured directly rather than inferred by protein-level adjustment. Recorded as `protein_adjusted = 'native'`. Not produced by DIA-NN.

**Class I site** — Field convention for a modification site with localisation probability ≥ 0.75.

**Evidenced inference** — A defeasible claim the measurement does not directly support, carrying a basis, a confidence, and a supersession path. `ModifierAssignment`, `EnzymeAssociation` and pathway annotation are the three instances. The abstraction that lets a fourth inference layer be added in days.

**Enzyme association** — An inference about which enzyme conjugated or deconjugated a modification at a site. Not measurable by mass spectrometry; requires perturbation of the enzyme. A site without one is *unattributed*, never assumed to belong to the canonical writer or eraser.

**Unattributed** — A site whose modifier may be assigned but whose responsible enzyme is not established. Displayed as such rather than defaulted.

**Observation contract** — The five things every observation subtype must provide (id, quant_ref, dataset edge, reference-entity edge, provenance reachability). Code operating on the contract works across every modality.

**Rebuild over migration** — The property, required by invariant I9, that the graph is derived from content-addressed raw files plus a curation export and can be regenerated from scratch. Converts most schema changes from migration scripts into re-ingestion.

**Recorded assumption** — A design decision taken under uncertainty, written down with a confidence and an explicit falsification trigger, so that being wrong is detectable rather than silent. See `ROADMAP.md`.

**Quantitative retention** — Invariant I11. Per-sample values persist permanently in the columnar store, so any statistical test is recomputable without re-ingestion. The cheapest hedge against pipeline change.

**Action** — An operation that changes graph state and is recorded against it: validating a finding, assigning a modifier, superseding a dataset, retracting a claim.

**Provenance** — The chain from a result back to its source data, workflow, parameters, software, operator and time, expressed in PROV-O rather than as free text.

**Unprovenanced** — A result with no traceable path to an analysis activity. Flagged visibly rather than hidden or silently trusted.

**PROV-O** — W3C provenance ontology. Models `Entity`, `Activity` and `Agent`, and the relations between them.

**RO-Crate** — A packaging standard bundling data with machine-readable metadata and provenance for export or archiving.

**CURIE** — Compact URI: `prefix:local_id`, e.g. `uniprot:P05161`. The identifier form used throughout the graph.

**Local-first** — Full functionality on the researcher's own hardware, with no cloud dependency; external services opt-in per project.

**ADR** — Architecture Decision Record. A numbered, immutable note capturing one decision and its rationale. Superseded by later ADRs, never edited.

---

## Comparable systems

**Palantir Foundry** — Enterprise data integration platform. Its Ontology layer (object types, links, and write-back Actions) is the structural reference for this project. Its defensibility rests on forward-deployed engineers building bespoke ontologies per customer — a model this project deliberately does not follow.

**Perseus** — Downstream statistical environment for MaxQuant output. Operates per-dataset; retains no cross-dataset model.

**PRIDE / ProteomeXchange** — Public repositories for proteomics data. The bootstrap source for public datasets.

**Open Targets, SPOKE, Hetionet** — Public biological knowledge graphs. Model published biology; contain no unpublished laboratory evidence.
