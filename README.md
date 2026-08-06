# bzk Omics

A local-first knowledge graph for post-translational modification proteomics, which treats modification identity as an evidenced inference rather than an assertion.

A diGly site stays ambiguous between ubiquitin, NEDD8 and ISG15 until knockout, mutant or interactome evidence resolves it. The enzyme that wrote or erased it is recorded only where a perturbation experiment supports the claim. Every result traces back to the raw file, the search parameters, and the human judgement used to reconstruct the experimental design.

**Status:** early design and exploration. No working software yet.

---

## Why

Ubiquitin, NEDD8, ISG15 and FAT10 all leave an identical K-ε-GG remnant after tryptic digestion. The field's default assumption that a diGly site is ubiquitin holds at baseline and fails under interferon stimulation — the exact condition of interest in ISGylation biology. Existing tools either report the assumption as fact or leave it to prose in a discussion section.

The same pattern recurs elsewhere. Which protein a shared peptide came from, which enzyme placed the mark, whether a value was measured or imputed — all are inferences routinely presented as measurements. This project models them as inferences with an evidence chain.

## Repository layout

| File | Contents |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | **Start here.** Router and working conventions |
| [`VISION.md`](VISION.md) | Positioning, target user, principles, non-goals |
| [`ONTOLOGY.md`](ONTOLOGY.md) | Normative schema — node and edge types, sixteen invariants |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Stack, storage layout, module boundaries |
| [`ROADMAP.md`](ROADMAP.md) | Scope, milestones, measured findings, recorded assumptions |
| [`GLOSSARY.md`](GLOSSARY.md) | Terminology |

`ONTOLOGY.md` is normative: its DDL is a contract, and code that diverges from it is a defect. Everything else describes, decides, or defines.

## Exploratory work

`notebooks/` contains two Colab notebooks used to test the design against real data before writing any of it.

Working from PXD018299 (Pinto-Fernández et al., *Br J Cancer* 124:817–830, 2021 — the USP18-dependent ISGylome), they reproduce 12 of the 14 published ISGylation targets, and record what that reproduction required.

Findings that changed the schema:

- **82% of GlyGly sites map to more than one protein.** Expected to be an edge case; is the common case. Forced a cardinality change and a new inference type.
- **`Ratio mod/base` yields 23 testable sites; `Intensity` with imputation yields thousands.** The stoichiometrically correct quantity is unusable for a low-stoichiometry modification.
- **Imputation is load-bearing, not optional.** The published figure depends on it, and its parameters are not recoverable from the methods section.
- Three defensible analysis choices moved the outcome from 1 recovered target to 12. None is stated in the publication.

`data/curation/` holds the sample-to-condition mapping for that dataset, reconstructed from the publication's methods because no SDRF accompanies the deposit. Under the reproducibility invariant this is the only content that cannot be regenerated.

## Design principles

- **Observation and annotation are never conflated.** The graph separates what was measured from what the literature asserts.
- **The platform never asserts what the data cannot support.** Ambiguous modifiers, razor-picked proteins, imputed values and inferred experimental designs all carry their status wherever they appear.
- **Local-first.** Full functionality on a laptop; no cloud dependency.
- **Interoperability over invention.** Every reference entity resolves to an external authority, so the knowledge survives this platform.
- **Rebuild over migration.** The graph is derived from content-addressed source files and can be regenerated from scratch.

## Licence

To be decided before first release.
