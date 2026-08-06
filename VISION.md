# VISION.md

| Field | Value |
|---|---|
| Status | Draft |
| Version | 2.2 |
| Last reviewed | 2026-08-06 |
| Depends on | Nothing |
| Authoritative for | Positioning, target user, principles, non-goals |

This document answers *why* and *for whom*. It defines no schema — see `ONTOLOGY.md` — and no milestones — see `ROADMAP.md`.

---

## In one sentence

bzk Omics is a local-first, open-source knowledge graph for post-translational modification proteomics that treats modification identity as an evidenced inference rather than an assertion — a diGly site stays ambiguous between ubiquitin, NEDD8 and ISG15 until knockout, mutant or interactome evidence resolves it, and the enzyme that wrote or erased it is recorded only when a perturbation experiment supports the claim. It ingests search-engine output from a researcher's own experiments and from public PRIDE datasets on equal footing, resolving everything to versioned UniProt identities so that questions spanning years of accumulated work become single queries instead of weeks of scripting. Every result carries provenance back to the raw file, the search parameters, and the human judgement used to reconstruct the experimental design — so nothing is asserted beyond what the data supports, and nothing is lost when the pipeline changes.

---

## Who it is for

Independent researchers: graduate students, postdoctoral scientists, and small groups who generate genuinely complex multimodal data and have no access to enterprise data-integration software.

The people who most need semantic data infrastructure are the people least able to buy it. Foundry-class capability is gated behind six-figure contracts and forward-deployed integration teams. A PhD student with three diGly datasets, a matched proteome, an RNA-seq experiment, and eighteen months of accumulated context has exactly the problem that software solves, and none of the budget.

Four consequences follow directly, and every design decision should be checkable against them:

1. **Install-to-value in one afternoon.** No integration project, no consultant, no schema authoring. The ontology ships pre-built for the domain.
2. **Runs on a laptop.** No cluster, no cloud account, no institutional IT request.
3. **Own data and public data on equal footing.** Public reanalysis is how a single researcher achieves statistical power.
4. **Open source.** The user cannot be locked in, and the ontology improves by contribution rather than by consultancy.

---

## Problem

Laboratory knowledge is stored as files. The relationships between those files exist only in people's heads.

A project's evidence is scattered across raw instrument output, search-engine result tables, R and Python scripts, PowerPoint figures, notebook entries, and published supplementary material. Researchers routinely know a result exists but cannot retrieve, compare, or re-derive it. When a group member leaves, the interpretive layer leaves with them.

Existing tools solve adjacent problems and stop short of this one:

| Category | Examples | What they do | What they don't do |
|---|---|---|---|
| ELN | Benchling, LabArchives, eLabFTW | Capture protocols and narrative | Model relationships between results |
| LIMS | Sapio, Dotmatics, Revvity Signals | Track samples and inventory | Reason across analyses |
| Pipeline platforms | Nextflow Tower, DNAnexus, LatchBio | Execute and version workflows | Retain meaning after execution |
| PTM analysis | Perseus, FragPipe, MaxQuant | Process one dataset | Connect datasets to each other |
| Repositories | PRIDE, GEO, Zenodo | Archive terminal datasets | Serve day-to-day retrieval |
| Public knowledge graphs | Open Targets, SPOKE, Hetionet | Model published biology | Contain unpublished evidence |
| Enterprise integration | Palantir Foundry | All of the above, well | Exist at a price a student can pay |

---

## Core belief

Files are storage. Relationships are understanding.

The value of a research programme is not in any single dataset. It emerges from connections across time, technologies, biological systems, and literature — connections currently reconstructed by hand, repeatedly, by whoever happens to remember them.

---

## Positioning

bzk Omics **sits downstream** of the search engines and analysis tools a researcher already uses. Their outputs are its inputs.

bzk Omics **is not an analysis tool.** Perseus has been the standard in this field for over a decade, does the job well, and is free. Nothing here asks anyone to stop using it, and a platform that required them to would deserve to fail.

bzk Omics **is not** a pipeline executor, a visualisation suite, a notebook environment, an inventory LIMS, or a public repository either.

### What downstream means, precisely

The gap in this field is not analysis quality. It is that analysis is **terminal**: a volcano plot is produced, a figure is saved, and the reasoning that produced it evaporates. Nothing accumulates. Ask which sites recur across four years of experiments and the answer is a week of scripting, every time.

So the platform holds what those tools produce, connects it, resolves every entity to a versioned external identity, and records which claims were measured and which were inferred.

**Two ingestion paths, deliberately.** Analysis outputs are ingested with their parameters recorded as reported. Search-engine outputs are ingested with the underlying quantitative matrix retained, so results are recomputable and comparable. The two are distinguished rather than conflated — see `ONTOLOGY.md` §5.4 and invariant I19.

A user can begin by handing over a Perseus table and later hand over search output, without migration. Retaining the matrix is what keeps the platform from being a filing cabinet.

**The known limitation.** Where only an analysis output is ingested, provenance starts where that output starts. A changed threshold upstream produces a new result the platform cannot explain. This is a real cost of the downstream position and is accepted knowingly, not overlooked.

### On the moat

There is no technical moat, and pursuing one would be a mistake. Foundry's defensibility rests on forward-deployed engineers constructing a bespoke ontology per customer — a labour moat that cannot be replicated by a single developer and that open source deliberately dissolves.

The substitute is a **pre-built, opinionated ontology for one domain**, so the researcher gets value on install rather than after an integration project. What accrues is the curated ubiquitin/UBL ontology and the ingestion adapters — both of which improve through contribution rather than eroding through disclosure.

Correctness in a domain nobody has modelled properly is a stronger position than novelty.

---

## Principles

### Observation and annotation are never conflated

The graph separates what was measured from what the literature asserts, joined only through observation nodes. Collapsing the two is the standard failure mode of biological knowledge graphs: once *"we measured this"* and *"someone published this"* share an edge type, the system can distinguish neither. Implemented in `ONTOLOGY.md` §1.

### Identity is inference, not measurement

Three claims routinely reported as fact are not measured by mass spectrometry at all: which ubiquitin-like modifier produced a diGly remnant, which enzyme wrote or erased it, and what the modification does. Each is modelled as a defeasible inference carrying a basis, a confidence and a supersession path. Implemented in `ONTOLOGY.md` §6.

The anchor case: ubiquitin, NEDD8, ISG15 and FAT10 all leave an identical tryptic K-ε-GG remnant. The field's default assumption that a diGly site is ubiquitin holds at baseline and fails precisely under interferon stimulation, which is the condition this platform exists to analyse. Modifier identity is therefore modelled as a defeasible inference with its own evidence chain, and sites lacking orthogonal evidence are reported as ambiguous rather than resolved. Implemented in `ONTOLOGY.md` §6.

The same discipline applies elsewhere: results without traceable provenance are flagged unprovenanced; site-level changes without matched protein-level correction are labelled stoichiometry-uncorrected. Flag rather than hide, and never silently promote.

### From retrieval to decision

Retrieval alone produces a better filing cabinet. Leverage comes from operations that change graph state and are recorded against it: promoting an observation to a validated finding, assigning a modifier with cited evidence, superseding a dataset, retracting a claim and propagating the retraction to every derived figure.

The last is the one nobody offers, and the one that most directly serves reproducibility. A conclusion should be able to die properly.

### Interoperability over invention

A locally invented ontology is a locally invented dead end. Every reference entity resolves to an external authority, and every export uses a community standard, so that a researcher's knowledge survives this platform. Authorities listed in `ONTOLOGY.md` §3.

### AI is the interface, not the oracle

The model holds no biology. It translates questions into structured graph queries, retrieves subgraphs rather than documents, answers only from retrieved nodes with citable identifiers, and returns an explicit *no supporting evidence in this graph* when retrieval is empty. Local-first implies local inference by default; external APIs are opt-in per project.

### Domain choice is a schema stress test

Ubiquitomics and ISGylation is the anchor, not the definition. It was chosen because it is the hardest case: site-level identity against a versioned sequence, genuine modifier ambiguity, enzyme attribution requiring perturbation, and a stoichiometry confound. A schema that handles it correctly extends to phospho, acetyl, glyco and SUMO almost for free — see `ONTOLOGY.md` §10.

The specialisation is the wedge, and the order matters: generality built before anyone uses the specialised version is a broader claim backed by less working software.

---

## Success metrics

- ≥ 90% of ingested datasets resolved to typed entities with at least one external identifier.
- Median time from question to cited answer under 60 seconds for cross-dataset queries.
- 100% of figures in a submitted manuscript regenerable from their provenance chain.
- No K-GG site presented as a ubiquitination site without an evidence chain supporting that assignment.
- Zero unattributed AI claims in exported reports, auditable by construction.

---

## Non-goals

Sample and inventory management. Wet-lab scheduling. Pipeline authoring. Multi-institution federation. GxP / 21 CFR Part 11 compliance.

Each is a legitimate product. None is this one.

---

## Long-term vision

A researcher starting a new project should immediately inherit every relevant experiment their group has performed, with its evidence and its caveats intact. The platform should become an active research partner rather than a passive repository — continuously organising, connecting, contextualising, and explaining.

---

## Final statement

The future of biological research is not defined by producing more data. It is defined by understanding the relationships within it.

Every experiment strengthens the graph. Every analysis extends it. Every discovery becomes permanent.
