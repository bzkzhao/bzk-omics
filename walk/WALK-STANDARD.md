# WALK-STANDARD — completion standard for the ISGylation deposit walk

**v2, 2026-09-18.** Working copy: `/Users/bzk/bzk-omics`.
Supersedes v1 (2026-09-17). Changelog at the end names every change.

This standard governs **assessment**, not ingestion. It fixes when the search for
evidence about a candidate may stop, and what verdict the stopping licenses.

**Why it exists — restated in v2, because v1's stated motivation was wrong.**
v1 cited `PXD074990` as an absence recorded without a documented stopping rule.
The recorded walk of 2026-08-18 has a documented source set, measured fetch
accounting and a listing reconciled before scanning; the defect is not there
(see `walk_PXD074990_m6.json`). The standard stands on its own evidence instead:
in one session its rules caught three determinations that were about to be made
from a name, a count or a container listing rather than from an opened artefact.
**A standard whose motivating instance was itself asserted from a shallow read is
exactly the failure it exists to prevent, and saying so is cheaper than leaving
it.**

**Single-source note:** this document restates no measured figure.

---

## 1. What is being determined

| # | requirement | tier |
|---|---|---|
| R1 | a published site-grain claim set, pinnable and keyable — accession or gene, plus position | record |
| R2 | a methods section stating a statistical criterion | record |
| R3 | a column-to-condition mapping, in any grain | record |
| R4 | a processed file an existing adapter can read | **platform** |
| R5 | **a design the schema can represent without asserting something false** | **platform** |

R1's template is the anchor's `SUPP_DATA_1` **in kind**: one row per site, an
identifier column, a position column. Comparable in kind, not in size.

### 1.1 The two tiers, and why the distinction is load-bearing (new in v2)

**R1 to R3 are properties of the record.** They are true or false of the
publication and the deposit, and no amount of work on this platform changes them.

**R4 and R5 are properties of this platform's current reach.** R4 fails when no
adapter reads the format; R5 fails when the schema cannot hold the design. Both
can be cleared by building or by deciding, and neither is a deficiency of the
deposit.

Three consequences:

- A platform-tier FAIL is recorded as **what it would take to clear it**, not as
  a verdict on the deposit.
- The §5 countable — curatable deposits that cannot support a claim-grain
  comparison — is about the **record**, so a platform-tier failure must not enter
  its numerator.
- **R4's own wording wobbles between the tiers and v2 does not fix it.** *"An
  existing adapter can read it"* is platform-relative; *"a processed file exists
  in a documented format"* would be a record property. The denominator of §6
  currently uses R4, so it inherits the wobble. Named here rather than
  silently resolved; it needs a decision, not an edit.

---

## 2. Verdict vocabulary

Four verdicts. Three of them are not the same thing.

- **PASS** — positively exhibited by a named source at a named grain.
- **FAIL** — positively determined absent, every source in the applicable order
  having met its exhaustion criterion (§4).
- **UNRESOLVED** — the search stopped before exhaustion: a dead pointer survived
  its ladder, a source could only be opened and not exhausted, or budget ran out.
  **Not a FAIL, and it never rolls into one.**
- **NOT-REACHED** — gated off by §6 and never assessed.

**The asymmetry rule.** A PASS may be recorded from the shallowest grain that
positively exhibits the requirement. A FAIL requires the deepest applicable grain
on **every** listed item. Absence costs more evidence than presence, because
absences do not fail tests and nothing else will catch a wrong one.

**Titles are never sufficient for a FAIL.**

**R1 qualifier, new in v2 — `recoverable_only`.** A claim set whose key
*determines* a position without *carrying* one is not a PASS: the position is a
function of the sequence version resolved against, and where no version is stated
the published position is underdetermined. Record R1 FAIL with the qualifier
`recoverable_only` and the recovery route, rather than a bare FAIL. The instance
is `PXD044834`, whose sites are 15-mer windows with no position column.

**A positive-control set tests sensitivity only (new in v2).** It cannot catch a
detector or a criterion that is too generous. Where a determination is made by a
pattern or a query, its precision must be checked separately, by inspecting what
it admits — not only by confirming it admits what it should.

---

## 3. Grain ladder

Every verdict names the deepest grain reached.

0. **G0 metadata** — repository record, article abstract, item titles
1. **G1 item** — a listing as a set of named items
1c. **G1c container (new in v2)** — an archive, zip or folder that appears in a
   listing but has not been expanded. **No absence may be determined from G1c.**
   A listing that stops at a container is not exhausted, and a determination made
   there is the defect this standard exists to prevent.
2. **G2 document** — an item opened; its sheets, tabs or sections enumerated
3. **G3 column** — headers read and classified
4. **G4 row** — rows inspected for keying and one-row-per-site structure

R1 FAIL requires G4 on every item that could plausibly carry claims, and G2 on
every item that could not — plausibility judged after opening, not before.

**The ladder is defined for tabular supplementary material.** A candidate whose
claims live in a figure has no defined deepest grain and is UNRESOLVED until the
ladder is extended. Instance: `PXD071724`.

---

## 4. Source order and exhaustion

R1, R2 and R5 are determined from sources 1–5 alone; no deposit is touched until
R1 passes (§6). Every source record carries its **method of discovery** and, for
a set, a **retrieved count**.

**1. Publication main text.** Exhausted when Results and Methods are read in full
**and** every in-text pointer is enumerated by full-text search over a recorded
term set (at minimum *Supplementary*, *Supplemental*, *Table S*, *Data S*,
*Fig. S*, *Additional file*, *source data*) and each pointer followed to its
target or recorded dead (§5).

**2. Supplementary listing.** Exhausted when every listed item carries a type
judgement made at G2 or deeper, with the item count reconciled against source 1's
pointers in both directions.

**3. Supplementary tables.** Per item: every sheet or tab enumerated, headers
read at G3, item classified for identifier column, position column, row unit and
significance column. R1 PASS requires G4 confirmation that the row unit is the
site.

**4. Figure legends.** Exhausted when every legend is read for site-grain claims
and for pointers to underlying data, source-data files included.

**5. Supplementary methods.** Exhausted for R2 when the criterion is recorded
with its parameters, or its absence determined after reading the full methods and
any separate methods supplement.

**5a. Peer-review file, where the journal publishes one (new in v2).** Exhausted
when read for parameter values and reviewer-prompted clarifications. Peer-review
files routinely carry method detail that never reaches the paper, which is
exactly the material a reconstruction needs.

**6. Repository project metadata.** Exhausted when description, sample protocol,
data-processing protocol, instrument, software, modifications, submission type
and linked publication have each been read.

**7. File listing.** Exhausted when the complete listing has been retrieved
programmatically, its count reconciled against the repository's stated count,
every processed file classified by producing software, **and every container
expanded** (§3, G1c).

**8. SDRF.** Exhausted when present and parsed for characteristics and
factor-value columns, or positively absent from the **fully expanded** listing of
source 7. **An SDRF may state search parameters and no experimental design, and
may misreport those parameters** — instance recorded in `walk_PXD065158.json`.

**9. Repository-adjacent records.** ProteomeXchange, the data-availability
statement, secondary hosts, reanalysis deposits, author correspondence.

**Correspondence is an open channel.** It can be opened, never exhausted, and can
never carry a FAIL. The same holds for embargoed material under I18.

---

## 5. Dead pointers

A pointer is dead when following it does not reach the named target. **A dead
pointer is not evidence of absence.** Record it verbatim with its source location
and failure mode, then work the ladder — publisher page, alternate host,
repository record, item searched by name, ProteomeXchange record, submitting
author — recording each rung. If the ladder is exhausted without reaching the
target, the requirement is **UNRESOLVED** and the deposit leaves the §6
denominator.

---

## 6. Gating, and the denominator of the negative result

**Gating.** Where R1 FAILs or is UNRESOLVED, the deposit is not walked at G2 or
deeper for R3, and R4 is determined from the file listing alone.

The countable is reported as three numbers, never one:

- **numerator** — deposits with R1 = FAIL and R3, R4 both PASS;
- **denominator** — deposits whose R3 and R4 are both determined;
- **excluded** — deposits whose R3 or R4 is UNRESOLVED or NOT-REACHED.

**R5 does not enter the countable** (§1.1). A deposit that fails R5 has a
comparable claim set that this platform cannot currently hold, which is a
statement about the platform.

Each class carries an exposure count and a defeat count.

---

## 7. R5 — representability (new in v2)

**The requirement.** Every axis of the deposit's design must be expressible in
the schema **without asserting something the data does not support, and without
losing a relation the analysis depends on.**

**Determined at G0 or G1**, from the deposit's sample-processing protocol or the
publication's design statement. It is cheap, and that is the point: R5 is placed
alongside R1 so a representability failure is found at screening rather than at
curation.

### The two tests, in order

**(a) Expressible.** Does a slot exist? Each axis must map onto a `Sample` field
— `genotype`, `treatment`, `timepoint_h`, `source_type`, `cell_line`,
`model_system`, `replicate`, `replicate_type` — or onto `Dataset` or `Analysis`
where the axis is not a sample property.

**(b) True.** Does the mapping assert only what the data supports? Two ways it
fails:

- **False multiplication.** Expressing an axis as a `Sample` property when the
  material was split after the biological sample ceased to exist asserts more
  biological samples than were prepared.
- **Lost relation.** A relation the analysis depends on — pairing, blocking,
  nesting, shared source — that the schema cannot record. The graph is then
  silent about something a reconstruction must know.

### Verdicts

- **PASS** — every axis passes (a) and (b).
- **FAIL** — an axis fails (b), and record **what it would take to clear it**:
  the schema change, the ADR, or the convention, named.
- **UNRESOLVED** — the design statement does not say enough to determine it.

**R5 is not a licence to reject awkward deposits.** A compound `treatment` string
is ugly and passes. A dose series passes. R5 fails only where representation
requires a false assertion or discards a load-bearing relation. If a FAIL cannot
name the specific false assertion or the specific lost relation, it is not a
FAIL.

### Recorded instances

| candidate | R5 | why |
|---|---|---|
| `PXD018299` (anchor) | PASS | genotype and cell treatment, both properties of living cells |
| `PXD065158` | PASS | genotype and cell treatment; the ISG15-machinery transfection is a cell treatment |
| `PXD026748` | **FAIL** | the PLpro axis is applied to **lysate**, after the biological sample ends. Expressing it as `Sample.treatment` multiplies samples falsely; not expressing it breaks I11's `Cell` key; and the pairing — three cultures split two ways, not six independent replicates — is unrecordable either way. **To clear:** an ADR on post-preparation perturbation. |

**The `PXD026748` instance is why R5 exists.** It passes R1 through R4 and may
still be unusable, and nothing in v1 would have surfaced that before a curation
record was being written.

### What R5 gives the thesis, not only the walk

A design that cannot be represented is a design a reconstruction cannot faithfully
reproduce. `PXD026748`'s paired PLpro axis is **not stated as paired in the
methods**, so a reconstruction choosing an unpaired two-way ANOVA and one choosing
a paired one will disagree, and nothing says which was run. That is a defeater
arising from an **unrepresentable design** rather than an omitted parameter, and
the taxonomy has no class for it. R5 is how such cases get found.

---

## 8. When the walk is complete

**Per candidate:** every requirement carries a verdict; every verdict names a
grain and a source; every FAIL has its exhaustion criterion met at the grain §2
requires; every dead pointer has a closed ladder; the record is written.

**Overall:** every candidate in the frame has a record; the §6 countable is
reported as its three numbers; and either one deposit carries the D5 replication
or the absence of one is recorded at this standard.

Running out of budget is a legitimate stop. It produces UNRESOLVED and a recorded
remaining-source list — never a FAIL.

---

## 9. Known limits

1. Stopping rules only; nothing about how a replication is then run.
2. Source 9's channel list will need extending on contact with real candidates.
3. The G-ladder is defined for tabular material; figure-borne claims have no
   defined deepest grain.
4. **R4's tier is ambiguous** (§1.1) and the §6 denominator inherits it.
5. R5's test (b) is a judgement. The guard is that a FAIL must name the specific
   false assertion or lost relation; nothing mechanical checks that it is right.

---

## Changelog

**v2, 2026-09-18**
- **R5 added** (§7) — representability, with the two tests, the three verdicts,
  the not-a-licence clause and three recorded instances.
- **Two-tier distinction added** (§1.1) — R1–R3 are record properties, R4–R5 are
  platform properties; platform failures stay out of the §5 countable.
- **G1c container rung added** (§3) — no absence may be determined from an
  unexpanded container. This is the rung whose absence let an SDRF be recorded
  absent from a listing holding two unopened archives.
- **Source 5a added** (§4) — peer-review files.
- **Source 7 and 8 strengthened** (§4) — containers must be expanded; an SDRF may
  carry parameters and no design, and may misreport them.
- **R1 qualifier `recoverable_only` added** (§2).
- **Precision clause added** (§2) — positive controls test sensitivity only.
- **Motivating instance replaced** (preamble) — the `PXD074990` claim is
  withdrawn; the standard now stands on the errors its own rules caught.
- **R4 tier ambiguity named** (§1.1, §9) and deliberately not resolved.

**v1, 2026-09-17** — first version, written before any candidate was walked.

**v1's text is lost, and this changelog is all that survives of it.** v2 was
written by overwriting v1 in place rather than by keeping the prior version, so
v1 is not recoverable — not from this repository, not from the working directory
it was written in. **Every walk artefact in this repository names v1** — all five
records (`walk_PXD026748.json`, `walk_PXD065158.json`, `walk_PXD071724.json`,
`walk_PXD074990_m6.json`, `walk_M4_M5.json`) carry `"standard_version":
"WALK-STANDARD v1"`, and `STEP2-R1-SCAN.md` is headed *against WALK-STANDARD v1*.
Their verdicts were measured against a text no reader can now read, and the
entries above are the only account of how that text differed from this one. **v1 is deliberately not reconstructed from this changelog.** Reversing
the entries out would produce a document that had never governed anything, and
committing it as v1 would be worse than the gap it filled.
