# FRAME-SPEC — the ISGylation deposit frame

**v1, 2026-09-17. Working copy: `/Users/bzk/bzk-omics`.**

Written **before** any query is run, so the frame is auditable and a later
re-draw is comparable rather than a replacement. Same discipline as
WALK-STANDARD, one level up: that fixes when a deposit's evidence is exhausted;
this fixes what the set of deposits *is*.

---

## 1. Why a frame, and why the existing one will not do

§5's countable is *how many curatable ISGylation deposits cannot support a
claim-grain comparison*. That is an **integer over a defined set**. A rate from a
sample does not convert to it, and a set that was never defined cannot produce
one.

`ROADMAP.md`'s sixty cannot serve, for three reasons that compound:

- **Wrong subject.** It is GlyGly-general. §2 of the brief scopes the walk to
  ISGylation and USP18, and states the cost of that narrowness deliberately.
- **Wrong query.** Its 450-deposit pool was built from *what a diGly deposit is
  titled* — the remnant by its chemistry. `PXD065158` is titled *Proteome-wide
  identification of ISG15 sites in HeLa cells*, with no GlyGly in the title. It
  is in the sixty by luck of the pool, not by construction. ROADMAP says as much
  of an earlier round: *what limited that draw was its query set, not its gate*.
- **Not a sample design.** Sixty of 450 because *60 is what fits without the
  draw becoming the turn* — a budget cut. Nothing in it licenses an inference to
  the pool, let alone to a different population.

---

## 2. Term set

Searched as substrings, case-insensitive, each recorded with its own hit count so
a term that contributes nothing is visible rather than assumed useful.

| group | terms |
|---|---|
| modifier | `ISG15`, `ISGylation`, `ISGylated`, `ISGylome`, `interferon-stimulated gene 15` |
| conjugation machinery | `UBA7`, `UBE1L`, `UBE2L6`, `UbcH8`, `HERC5`, `HERC6`, `TRIM25`, `ARIH1`, `HHARI` |
| removal | `USP18`, `UBP43`, `deISGylase`, `deISGylating`, `deISGylation` |
| cross-reactive DUBs, only in combination with a modifier term | `USP16`, `USP24`, `USP36` |

**Excluded deliberately, and why.** Bare `interferon` and `IFN` — they return the
whole type-I interferon literature and the precision cost is not repaid.
`GlyGly`, `diGly`, `K-ε-GG` — these are the chemistry terms that built the wrong
pool; including them here would rebuild it. `ubiquitin` for the same reason.

The cross-reactive DUB row is conditional because `USP24` alone returns
unrelated deubiquitinase work; `PXD055843` is in frame through `ISG15`, which its
title carries, and the DUB term is a redundancy check rather than a route.

---

## 3. Fields

**Title, description, keywords, and sample-processing protocol.** All four.

Title alone demonstrably misses: it would have missed `PXD065158` on the
chemistry route and would miss any ISG15 deposit titled by its biology rather
than its modifier. The sample-processing protocol is included because
`PXD074990`'s walk showed that field carrying the design where the title carried
nothing.

Record, per deposit, **which field matched** — a frame whose members all matched
on one field is a different object from one that needed four.

---

## 4. Scope boundaries

- **Species.** Any. Species is a *candidate* property, not a frame property —
  excluding mouse at frame time would hide how much of the field is mouse, which
  is itself a finding. Record it; do not filter on it.
- **Date.** No lower bound. An upper bound of the query date, recorded.
- **Repository.** PRIDE and ProteomeXchange. Others recorded as out of frame with
  the reason.
- **Embargo.** Embargoed deposits are **in frame and counted**, named only as
  permitted under I18. A frame that silently drops what it may not name
  understates itself.

---

## 5. What makes a deposit a member

**ISG15 must be a subject of the deposit, not a mention.** The test: does the
design contain an ISG15-directed perturbation or enrichment — an ISG15 or
machinery knockout, an ISG15 immunoprecipitation, a deISGylase perturbation, or
IFN stimulation read out against an ISG15-specific control?

A deposit that cites ISG15 in a discussion and perturbs something else is out.
Determined from the deposit description at G0 and **recorded with the sentence
that decided it**, so the judgement is reviewable rather than asserted.

---

## 6. Two frames, and the countable is reported against the narrower

| frame | membership | purpose |
|---|---|---|
| **A** | every deposit meeting §5 | the honest population of ISGylation proteomics |
| **B** | the subset with site-directed enrichment — anti-K-ε-GG, remnant-motif or equivalent | the set that *could* have published a site-grain claim table |

**The countable is reported against B, with A's size given alongside.**

The reason is that A includes interactome and pulldown deposits that fail
requirement 1 trivially, because they never attempted site-level work. Counting
those inflates the numerator with deposits that were never candidates, and the
finding *deposits that did site-level work and still published no keyable site
table* is the one worth having. Reporting A's size keeps the restriction visible
instead of silent.

---

## 7. Per-deposit record

Accession · title · matching term(s) · matching field(s) · membership verdict
with its deciding sentence · frame A or B · species · repository · embargo state
· search engine if stated · associated publication if any.

**Nothing else at frame time.** Curatability and requirement 1 are the walk's
questions, assessed afterwards against WALK-STANDARD. A frame that pre-judges
them is not a frame.

---

## 8. Positive controls — run these before trusting the query

Four deposits are known to be in frame. **A query that does not return all four
is wrong and must be fixed before the frame is used.**

| accession | expected route |
|---|---|
| `PXD018299` | title — *USP18-dependent ISGylome* |
| `PXD055843` | title — *ISG15 cross-reactive deubiquitinase* |
| `PXD065158` | title — *ISG15 sites in HeLa cells* |
| `PXD071724` | title — *ISG15 sites on GAPDH and PGK1* |

Two of these are in ROADMAP's sixty. If the frame recovers them **and** finds
deposits the sixty missed, that difference is itself measured evidence about the
chemistry-term query, and should be recorded rather than noted.

---

## 9. Pre-registration

Registered before running, per the project's standing convention.

- **Frame A size: 25 to 60.** Basis: the 2021 ISGylation-proteomics review
  (Thery, Eggermont and Impens) catalogues on the order of twenty MS studies to
  that date, and the field has grown since without becoming large. A result
  below 15 suggests the query is too narrow; above 100 suggests a term is
  admitting the interferon literature.
- **Frame B, as a share of A: 30–50%.** Most ISG15 proteomics before the
  remnant-motif era was pulldown-based.
- **Numerator — frame B members with curatability passing and requirement 1
  failing: at least 1.** `PXD055843` is already determined. There is no basis
  for a tighter prediction and one is not offered.

---

## 10. Limits

1. **This cannot be run from the reviewer container.** Egress does not reach
   `ebi.ac.uk`, and URL fetching is restricted to links already seen. The query
   runs on the Mac or not at all.
2. **A repository search index is not the repository.** Terms are matched against
   what submitters wrote; a deposit whose metadata names none of §2's terms is
   invisible to any query built this way, and no term set closes that.
3. **The frame is a claim about PRIDE, not about the field.** Work not deposited
   is outside it, permanently and undetectably.
4. Recording these here is what makes the resulting integer a measurement with
   stated limits rather than a number.
