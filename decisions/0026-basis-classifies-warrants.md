# ADR-0026 — `basis` classifies warrants, not containers; a composed mapping records its weakest link

| | |
|---|---|
| Status | Accepted |
| Date | 2026-08-18 |
| Reviewed | 2026-08-18 — five findings, three revisions made below |
| Supersedes | — |
| Superseded by | — |

## Review

Landed `Proposed` at `10d76f6` and reviewed in the following turn. Five findings; two required no
change, one was a reviewer's own error ruled on below, and two produced the revisions marked
**Added in review** further down. **No finding identified a defect in the decision itself**, which
is the ground for the status above rather than the absence of objections.

### The consequence went live in the same commit as the record, and it stands

§5.3's Meaning cells were widened at `10d76f6`, citing this record while it was `Proposed`. So the
normative ontology carried the consequence before the argument had been read. **The amendment
stands, and the round-trip means something narrower than it appears.**

**`decisions/README.md` already says so, about two of its own records.** Its status paragraph notes
that ADR-0008 and ADR-0012 *"record decisions that are already live and normative as I6 and I9: the
status is a property of **the record's** review state, not of the decision's settledness, which is
what the rule's own wording says."* A `Proposed` record whose consequence is fully binding in
`ONTOLOGY.md` is therefore not a new state in this repository; it is two-thirteenths of the
`Proposed` set.

**One asymmetry, named rather than waved past.** 0008 and 0012 documented decisions that predated
their records; this one's consequence went live simultaneously. That does not separate them for the
purpose the round-trip serves, which is review of the *reasoning*. Reverting the cells would leave
§5.3 asserting a reading this review has now examined and upheld, and would leave two Meaning cells
citing a record whose consequence had been withdrawn — worse than either stable state.

**What `Proposed` means for a record whose consequence is already binding.** It governs the **cost
of reversal**, not the permission to act. Under README's l.5 a `Proposed` record is corrected by an
ordinary edit; under l.7 an `Accepted` one is append-only and changes only by a superseding ADR. So
between landing and acceptance the widened cells were revertible in one commit, and from this turn
they are not.

## Which vocabulary this touches, and which it does not

**This record settles `ONTOLOGY.md` §5.3's `basis` enum only** — the one whose heading is at l.564,
declared closed at l.576, tabled at l.578–584, and carried on `Analysis` where `kind = 'curation'`.
Its confidence column holds exactly two values, and l.472's DDL comment scopes that pair as
*curation only*.

**`basis` is a field name used on five node types with five different closed sets.** The scoping is
stated here because miscategorising a value across two of them has already cost this project one
ADR: I17 at l.961 records that calling a keying rule an inference *"is what put it in the
`ProteinAssignment` basis enum and into conflict with I14"*, which ADR-0024 then had to unpick.

| Field | Declared | Vocabulary | Touched here |
|---|---|---|---|
| `Analysis.basis` | l.471 | §5.3's five values | **yes, and only the Meaning column** |
| `SiteObservation.keying_basis` | l.432 | `razor` \| `reviewed_preferred` | no |
| `ModifierAssignment.basis` | l.651 | includes `inferred_default` (l.680) | no |
| `EnzymeAssociation.basis` | l.698 | its own enum | no |
| `ProteinAssignment.basis` | l.732 | `unambiguous` \| `unique_peptide` \| `leading` \| `razor` \| `reviewed_preferred` \| `orthogonal_evidence` (l.1128) | no |

`EvidencedInference`'s contract at l.626 pairs its `basis` with a **different** confidence
vocabulary — `ambiguous` \| `probable` \| `confirmed` — and `schema.py` l.24–29 records that reusing
one for the other *"would be wrong rather than merely loose"*. **Nothing below applies to any row of
that table but the first.**

## Context

Three deposits have been ruled *present but insufficient* on both public bases. Every file listing
walked also carried files that would ordinarily hold the experiment-to-file assignment, named at
`ROADMAP.md` l.9721–9727: `readme.txt`, `UbiSite_summary.txt` and `UbiSite_parameters.txt` on
`PXD027163`; `mqpar.xml` and `mqpar_DP.xml` on `PXD027328`. The `PXD027328` walk separately left
nine Supplementary Datasets and a Source Data file unfetched.

Neither group is described by the enum as written. l.582's `submitter_metadata` names *"Locally
generated data, or structured PRIDE metadata"*, and a deposited `mqpar.xml` is neither — it is a file
the submitter uploaded, not a field PRIDE structures. l.584's `filename_inference` names deduction
from *"raw file naming conventions"*, and reading a parameter file's contents is not that. l.583's
`publication_methods` names the *"methods section"*, and a supplementary table is not that.

**The blocking question is therefore not what these files contain. It is what kind of thing the enum
is a list of.**

## The evidence that settled it, found in this repository rather than reasoned about

**One. MaxQuant's own documentation fixes what a parameter file can assert.** `ROADMAP.md`
l.7833–7834 quotes the Raw Files tab: *"The experiment is text that the user can choose and use
however convenient"*, and l.7845–7847 the one generated case: *"MaxQuant generates an value for the
experiment from the paths to the files"*. So the pairing an `mqpar.xml` or a `summary.txt` records is
**raw-file path ↔ experiment name**. The format has no field for a biological condition, and D2 was
stopped on exactly this ground at l.9315.

**Two. The anchor's own curation record already performs the composition this decision is about, and
labels it with the stronger source.** `data/curation/curation_PXD018299.json` carries
`basis = 'publication_methods'`, `confidence = 'inferred'`, and its `rationale` reads:

> *"Column names in the site table encode genotype (WT / KO), treatment (presence or absence of the
> _IFN token) and replicate index (1-3) unambiguously, so the mapping from column to condition is
> direct."*

**The methods gave the conditions; the column tokens assigned them to columns.** That is the move
three consecutive mapping walks refused as `filename_inference`, performed in the repository's only
curation record and recorded under `publication_methods`. `KO` ↔ *USP18-/- knockout* is not a
stronger match than `MG` ↔ *MG132*. **Either the record overstates its basis or the walks were too
strict, and this decision has to say which.**

**Three. Authorship does not predict confidence inside the existing table.** `sdrf` and
`author_correspondence` are both submitter-sourced and both `authoritative`; `submitter_metadata` is
submitter-sourced and `inferred`. So *the submitter authored it* — one of the two distinctions
offered as a discriminator — already fails to separate the rows that exist.

## Decision

**`basis` is a vocabulary of warrants, not of containers.** A source is classified by what it
*asserts about the design*, never by who wrote it, what format it is in, or where it is hosted.
Three rules follow, and they are the decision:

**R1 — A source that does not assert a sample-to-condition assignment is not a `basis`.** It may
still be useful: it converts one design question into another. A MaxQuant parameter file or
`summary.txt` asserts raw-file → experiment-name, which turns *which condition is column `MG1`* into
*which condition is raw file X*. The basis is then whatever answers the converted question, and the
parameter file is an intermediate that appears in `rationale`.

**R2 — Where a mapping composes several sources, `basis` records the weakest link.** A chain breaks
where it is thinnest, and I8 at l.888 makes `basis` a label carried into *"every view and export"*.
A mapping that would collapse if a token reading were wrong must not name the paper as its warrant,
because a reader told *basis: publication_methods* will go and check the paper, which is not where
the load is.

**R3 — A container is classified on reading, and only some containers can be classified in advance.**
This is where the two candidate sources part company, and **they are two decisions, not one.**

- **Machine-written processing configuration is categorically excluded**, decidable from the format
  before any fetch: `mqpar.xml`, `mqpar_DP.xml`, `UbiSite_summary.txt`, `UbiSite_parameters.txt`. By
  the documentation above their schema has no condition field, so no content could make one a design
  statement. Composed with raw filenames under R2, the result is `filename_inference` — l.584,
  already in the enum.
- **Human-written free-form documents cannot be classified in advance** — a deposited `readme.txt`, a
  supplementary dataset. Each resolves to an existing value when read, and to which one is fixed by
  R1 and R2, not by the container.

**The discriminator is whether the format fixes what the document can assert** — not that the
submitter authored one and the publisher hosts the other, which Evidence Three shows does not
separate the rows already present.

**Two Meaning cells widen; no value is added and no confidence changes.**

- **l.582 `submitter_metadata`** covers a design the submitter stated outside SDRF, whether as
  structured PRIDE metadata or in a document deposited beside the data. Still `inferred`: it is prose
  about an experiment, and the curator does the mapping.
- **l.583 `publication_methods`** reaches a supplementary file **only where the methods section cites
  it for the design**. The methods delegating to a table is still the methods speaking; a
  supplementary file the methods never point at is not reachable, and this does not widen the value
  to *anything the publisher hosts*.

## Options, each with its cost

**(i) These files are `submitter_metadata`, on the ground that the submitter produced and deposited
them. — Adopted in part.** Adopted for the deposited human-written document; **rejected for the
machine-written configuration**, which R1 excludes for a reason authorship cannot see. Cost as
adopted: l.582's definition widens, and `submitter_metadata` becomes a three-headed value —
locally generated data, PRIDE's structured fields, and now deposited documents. That is a real
looseness and it is accepted, because all three are the same warrant: the submitter describing an
experiment in prose, with the curator doing the mapping. **Cost had it been adopted whole:** an
`mqpar.xml` mapping would be labelled as though the submitter had stated a design they never stated,
which is the clause I8 exists to enforce.

**(ii) Add a value to §5.3's enum. — Rejected, on the merits and separately as not executable.**
On the merits: a new value would assert that *a file the submitter deposited* is a different kind of
warrant from *metadata the submitter supplied*, and it is not — both are prose, both need the same
mapping work, both are `inferred`. It would encode a **container** distinction into a **warrant**
vocabulary, which is the category error ADR-0024 records and I17 at l.961 names. A confidence would
also have to be chosen from a two-value column, and neither fits: `authoritative` is false, and
`inferred` makes it a synonym of the value it was added to distinguish itself from.

Separately, **it is not executable in this turn**, and this was measured rather than assumed:
`tests/test_schema.py::test_curation_basis_enum_matches_ontology_5_3` parses §5.3's table and
asserts `schema.CURATION_BASIS == dict(rows)`, and `bzk/curation/loader.py` l.232 rejects any record
whose `basis` is outside that set. **Adding a row turns the suite red unless `schema.py` changes in
the same commit.** The guard's regex captures the value and the confidence only, so the Meaning
column is prose and the value→confidence pairs are the validated vocabulary — which is why the two
widenings above are recordable now and a sixth row would not be.

**(iii) They fall outside the enum and are not a basis. — Rejected as a general answer, adopted for
one case.** Correct for machine configuration, where it is R1. Wrong for a `readme.txt`, because a
README in which a submitter writes *"column DMSO1 is the vehicle control"* is a submitter stating a
design, and no reading of the enum makes that unusable. Taken whole, this option would make a
mapping legible in a deposited document and nowhere else permanently unusable, which trades a real
mapping for a definitional tidiness.

**(iv) A classifying rule instead of a value. — Chosen**, as R1–R3 above.

**(v) Make `basis` multi-valued so a composition records every source it used. — Rejected.** It is
the honest shape and it cannot be had at this price: `basis` is identifying on `Analysis` (§3;
`schema.py`'s `ABSENCE` records `("Analysis", "basis"): "determined"`), so a list makes the id a
function of order unless canonicalised, and changing the field's type is a DDL change that forks
every existing id. R2 buys most of what it offers for none of that.

**(vi) Keep `basis` single-valued and add a sibling field naming the source document. — Rejected as
a decision, named as an implied change.** Insufficient alone: I8's labelling obligation names
`basis`, so a free-text sibling carries no obligation and would be invisible in exactly the views
where the warrant matters. It is the natural companion to R2 and is described below rather than
made.

**(vii) Record the strongest source and disclose the composition in `rationale`, rather than R2's
weakest link. — Rejected. Added in review**, because it is the rule the anchor record actually
applied and the record rejected it without stating it as an option. It is the strongest case against
R2: `basis` is one field, `rationale` is free text beside it, and a record that names
`publication_methods` and then says in its own prose that the column tokens did the assignment has
concealed nothing from a reader of the record.

**Rejected because the two do not travel together.** I8 propagates `basis` into *"every view and
export"*; **it propagates no `rationale`**. So the disclosure sits where a curator looks and the
attribution goes where a reader looks, and the one that travels is the one that overstates. That
asymmetry is the whole of the argument for R2, and it is why the anchor record is judged overstated
rather than merely terse.

**No option was chosen for unblocking the survey.** Under this settlement `PXD027328`'s mapping is
available at `filename_inference` — which is a worse basis than the walks were looking for, not a
better one — and `PXD027163`'s remains unestablished.

## What this does to the three completed walks

**Two of the three rulings stand, one becomes provisional, and two earlier deposits are
unestablished on this axis.** None is amended here; the ruling about their status is the output.

| Deposit | Unfetched source | Status under this settlement |
|---|---|---|
| `PXD027328` | `mqpar.xml`, `mqpar_DP.xml` | **Stands.** R1 excludes them categorically; they could not have changed the ruling |
| `PXD027328` | nine Supplementary Datasets, Source Data | **Stands.** The walk measured that no methods sentence cites one for the design, so R3's gate is not met |
| `PXD027163` | `UbiSite_summary.txt`, `UbiSite_parameters.txt` | **Stands**, by R1 |
| `PXD027163` | `readme.txt` | **Provisional.** Free-form, unread, and within R3's second class |
| `PXD019152` | its paper's supplementary files | **Unestablished.** Whether its methods cite one for the design was never measured |
| `PXD075538` | the single `OTHER` file in its listing | **Unestablished.** The record counts it and does not name it |

**And a correction to what those rulings were taken to mean.** Each walk answered *are the two
public bases sufficient?* and each answered correctly. It does not follow that no basis was
available. **`filename_inference` is in the closed enum, carries `inferred`, and is permitted by I8
with labelling** — three walks put it out of scope by instruction, which is a scope rule and not an
ontological bar. **The survey's route was never blocked by this vocabulary.** Whether the operator
wants a second deposit ingested at the enum's weakest basis is a decision, and it is not this one.

## What this does to the anchor's curation record

**Both stated facts confirmed by reading.** `data/curation/` holds three records, all `PXD018299`;
only `curation_PXD018299.json` carries a `basis`, and its value is `publication_methods` with
`confidence = 'inferred'`.

**The widenings do not unsettle it, and the question was answered rather than assumed.** Widening
l.582 touches a sibling value the record does not use. Widening l.583 extends the record's own value
to cover more sources without changing what a mapping made from the methods section proper asserts.
`basis` is identifying, so what would move an id is the **string**, and neither widening changes a
string.

**R2 does bear on it, and this is the sharpest consequence in the record.** The rationale composes
the methods section with a reading of the column tokens, and records the stronger source.
**Under R2 the correct value is `filename_inference`.** The record is not wrong about what it did —
it states the composition in its own text — but its `basis` names the half that was not
load-bearing.

**It is not amended here, and it could not be amended in place if it were.** `basis` is identifying,
so a changed value mints a different `Analysis` id. That makes the change a supersession rather than
an edit — under §5.3's own sentence *"Curation nodes are immutable under I6"*, which is where
curation nodes acquire that property: **I6's own text names `ModifierAssignment` and
`DifferentialResult` only**, so the obligation reaches `Analysis` through §5.3 and not directly.

### The extent of that supersession — Added in review

Measured by loading `data/curation/curation_PXD018299.json` through `bzk/curation/loader.py` twice,
once as committed and once with `basis` substituted, and diffing the two node and edge sets. **Held
in memory; nothing was written and no supersession was made.**

| | As committed | Under R2 |
|---|---|---|
| curation `Analysis` id | `bzk:bc90e3eb515d6edd1351ce25ecd33209` | `bzk:33b8991446168c8b25d2405b341729ab` |

**Exactly one node id moves, of sixteen.** The other fifteen are unchanged: 12 `Sample`, 1
`Project`, 1 `Experiment`, 1 `Dataset`. `Sample` is anchored on `("Experiment", "PERFORMED_ON")`,
not on the curation `Analysis`, so no sample id is a function of the basis.

**Thirteen edges of thirty-eight are re-keyed**, all on the moved endpoint — 12 `SAMPLE_GENERATED_BY`
(target) and 1 `USED` (source). Unchanged: 12 `PRODUCED`, 12 `PERFORMED_ON`, 1 `CONTAINS`.

**Nothing further is downstream in the id sense.** The two identity specs anchored on `Analysis` are
`DifferentialResult` (`WAS_GENERATED_BY`) and `Imputation` (`IMPUTATION_FOR`), and **neither node
type is constructed anywhere in shipped code**; the two adapters' `Analysis` nodes are their own,
each anchored on `Dataset`. `SampleMapping.curation_analysis_id` changes value and **is read by no
adapter** — declared at `bzk/adapters/base.py` l.46, constructed at `loader.py` l.170, consumed
nowhere.

**Three committed literals pin the moved id** and would have to move in the same commit:
`tests/fixtures/pxd018299_curation_ids.json`, `tests/test_perseus.py` l.74, and `HANDOFF.md`'s
minted-id table. The fixture's own note calls itself a *"re-mint tripwire"* and requires that it
never be regenerated to make a red test green without the move being explained — which is what this
section exists to supply in advance.

**The other two curation records are not downstream in the id sense.** Neither
`resolution_PXD018299.json` nor `analysis_PXD018299_KOIFN_vs_WTIFN.json` is loaded into the graph by
any shipped path; both hold counts rather than ids, and `bzk/sources/pxd018299_differential.py`
deliberately transcribes the second's parameters rather than reading it, to keep the comparison from
being circular. **They are downstream in I8's labelling sense**, being computed from the mapping the
curation record supplies.

**`12 of 14` is unaffected, and this is established rather than estimated.** The differential run
consumes `curation.sample_mapping()`'s samples, not its `basis`; the mapping itself does not change;
and `tests/fixtures/pxd018299_welch_baseline.json` — the fixture pinning which twelve — contains no
`basis` field and no node id at all, 14 target rows with 12 flagged recovered. **Both values are
`inferred`**, so I8's labelling obligation and its strength are identical before and after; what
changes is the string naming the basis, not the warning a reader sees.

## Implied changes, described and not made

1. **`ONTOLOGY.md` §5.3 gains a paragraph stating R1–R3** so the rules sit beside the table rather
   than only in this record. Not made: a `Proposed` ADR does not write normative text into a
   normative document.
2. **The `curation_PXD018299.json` supersession** above, with its I6 propagation.
3. **A `basis_sources` or `rationale`-adjacent field** recording every source a composed mapping
   used, per option (vi) — a DDL change, and out of scope by two rules.
4. **A guard for R2 — restated in review, because the reason it was deferred has now expired.**
   It was deferred at landing on the ground that writing it would enforce a decision ahead of its
   acceptance. **That reason stopped applying with the status change above**, so it is replaced by a
   narrower one rather than repeated.

   **What it would assert:** for every record under `data/curation/`, if `rationale` names a reading
   of the table's own column names as evidence for the mapping, then `basis` is `filename_inference`.
   The anchor record is the only instance, so the guard would go red on the tree as it stands.

   **Why it is not written in the same turn as the acceptance:** it would fail on a record this
   record explicitly declines to amend, and a guard that is red from birth is indistinguishable
   from a broken guard. The two must land together or in that order.

   **What makes it writable:** the supersession described above. Once the anchor record carries
   `filename_inference`, the guard passes on a true state rather than pinning a known violation,
   and the three literals in the extent table have moved with it. **Named as open, with its trigger
   stated, rather than left as a note a reader must remember.**
5. **No amendment to I8 at l.888.** R2 changes which value gets named under I8's obligation; it does
   not change the obligation, and I8's filename clause is satisfied either way — a composed mapping
   recorded as `filename_inference` is not presented as coming from the submitters.

## Consequences

- **Deciding a basis no longer needs a fetch in the excluded case.** R1 is readable from the file
  format, so a `mqpar.xml` in any future listing is settled before it is downloaded.
- **A `readme.txt` remains a live route** for `PXD027163`, at `submitter_metadata`, and requires a
  fetch to resolve.
- **The enum stays at five values**, so `schema.py`, the loader's closed-set check and every existing
  id are untouched by this record.
- **One repository inconsistency is now recorded rather than latent**: the anchor record and three
  walk rulings applied opposite rules to the same composition, and R2 says which is right.
