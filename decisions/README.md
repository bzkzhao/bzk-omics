# Architecture decision records

Numbered, immutable records of settled choices. Each captures one decision, its context, and what was rejected.

**An ADR lands as `Proposed`, is reviewed, and becomes `Accepted` only once that round-trip completes.** Correcting a record during review is an ordinary edit to a `Proposed` document — that is what the status is for.

**Once `Accepted`, a record is append-only.** It is never edited; a changed decision gets a new record that supersedes the old, and both remain readable — the same discipline the product applies to `ModifierAssignment` and `EnzymeAssociation`. A decision should die visibly.

The line is drawn by **status rather than by elapsed time**, because a status is checkable and "shortly after writing it" is not. ADR-0020 and ADR-0021 each carry a `Revised in place` row recording amendments made after they were marked `Accepted`, under the earlier reading of this rule. Those rows stay: they are the record of how the convention reached its current form, and reclassifying them retroactively would erase exactly the history this file exists to keep.

**What the round-trip means when the author and the reviewer are one loop — settled 2026-08-09, before eight records were landed rather than after.** The rule above was measured against the directory rather than assumed: ~~**ten records have a first commit git can read, nine of them first appear as `Accepted`**~~ — **re-measured 2026-08-10 at 24 records: 18 informative, of which 8 first appear as `Accepted`, 7 `Proposed` and 3 `Superseded`** — and ~~ADR-0022 is the only completed round-trip~~ — **ADR-0026 completed one on 2026-08-18, landed `Proposed` and accepted in the following turn on five reviewer findings, ~~so the count is two of twenty-five~~ — re-measured 2026-08-31 at `af331de`: *four of twenty-eight* — ADR-0022, ADR-0026, ADR-0027 and ADR-0028, against the 28 records `decisions/` now holds. Instrument: first status `Proposed` at `git log --diff-filter=A`, current status `Accepted`. Counting `| Reviewed |` header rows instead returns *three*, because ADR-0022's round-trip predates that row and its header carries none — the two instruments disagree by one, and the disagreement is in what got recorded, not in what happened. ADR-0029 is `Proposed` and is excluded; a round-trip is completed or it is not. The figure was supplied by the review half of the one loop this sentence already names, and is recorded here rather than derived here — the asymmetry the `Proposed` bullet below already licenses when it says a status holds *"until the reviewer has read them"*, the writing half stating a fact it does not itself establish. Cited by its content rather than by its line, because this write moved that line and a within-file line number in this file is a referent waiting to be lost. Form followed: the dated, instrument-naming one used twice earlier in this sentence, not the bare `~~Five~~ **six**` one that comes after it**. ~~Five~~ **six** arrived in a bulk *"Add files via upload"* commit and are uninformative in both directions — they are not counted as violations and not counted as compliance. Landing eight more as `Accepted` in one commit would take the informative count from nine of ten to seventeen of eighteen, and would do it by asserting a review that had not happened, which is the one thing this project refuses everywhere else.

**The sentence's other figures, established and deliberately not corrected — 2026-08-31 at `af331de`.** Correcting one figure inside a sentence leaves the rest reading as current, so each is stated here at what it is. **`24 records` is stale by four**: `decisions/` holds 28 files matching `NNNN-*.md`, the additions being 0026–0029. **The bulk-upload count cannot have drifted**, because a record written later cannot enter an earlier commit; checked rather than assumed, five records first appear in a commit titled *"Add files via upload"* — 0002, 0003, 0015, 0016, 0017 — and 0001 arrived through the same web editor under *"Create 0001-two-graph-model.md"*, so **six** is right if 0001 is the sixth and the loose part is describing them as one commit. **`18 informative, of which 8 / 7 / 3` is not established here, and not for cost**: its instrument is the first-appearance status read at `git log --diff-filter=A`, which is the first half of the instrument the four-of-twenty-eight figure was measured with — so re-deriving it would be taking the reserved measurement after all, one figure over. It is left standing and labelled unestablished, which is not the same as labelled current.

So the eight written on 2026-08-09 land as **`Proposed`**, except where a different status is a statement of fact rather than of review:

* **`Proposed`** — 0006, 0008, 0009, 0010, 0012. True at the moment of landing, and it stays true until the reviewer has read them. Note that 0008 and 0012 record decisions that are *already live and normative* as I6 and I9: the status is a property of **the record's** review state, not of the decision's settledness, which is what the rule's own wording says.
* **`Superseded`** — 0007, 0011, 0014. The round-trip does not apply: each records a decision that was made and then replaced, `Proposed` would be false of a decision nobody is proposing, and `Accepted` would assert the same missing review. The `Superseded by` row carries the successor.

The rule is not weakened for a single-developer project. It is applied literally, and the cost of applying it literally is that most of this directory's history does not meet it — which is recorded here rather than resolved by relabelling.

**ADR-0013's `Consequences` overstates its own `Context`, and is left standing — 2026-08-08.**
Its Context sets the discharge condition (*"the obligation is discharged when those two persist
their values"*) and its Consequences declares it met (*"I11 moves from unmet to met for both live
observation subtypes"*). Only `SiteObservation` retains anything; `ProteinObservation` has a table
and a `quant_ref` path and no adapter that writes either. The decision the record makes — retain
permanently, pre-imputation, two grains, two tables — is unaffected and correct; one factual
sentence in it is not.

Three routes were considered against the rule above, and the rule leaves none inside the record.
**Editing in place** is what *"never edited"* forecloses, and the `Revised in place` rows on
ADR-0020 and ADR-0021 are not licence — this file labels them as the earlier reading. **A
superseding record** is what the rule offers, and it does not fit: supersession is for *"a changed
decision"*, no decision changed, and a record correcting one sentence and deciding nothing is not
an ADR by the definition three lines above. **A note inside the ADR** is the in-place edit again.

So the correction lives here, in the one file in this directory the append-only rule does not bind
and which already carries statements *about* records, and in `HANDOFF.md` §8 where the project keeps
corrections of fact. What this leaves standing is a wrong sentence in a durable record with a
pointer to it only from outside — recorded as the cost of the rule rather than worked around.

**Two correction forms were invented rather than followed, and this is where they are recorded — 2026-08-31.** The three routes above settle where a correction *lives*. Neither they nor the strike-and-replace marks used throughout this file say what shape a correction takes when no existing shape fits it, and twice one did not. Both are outside this directory, and each is named as an invention in its own text rather than slipped in as though a precedent existed.

* **A row struck because it went false, not because it was resolved** — `HANDOFF.md` l.762, the *ADRs 0004–0014 unwritten* row. Every other struck row in that table records something that was **fixed**; this one records something that stopped being true on 2026-08-09 and stayed listed for three weeks. The strike is the same mark doing a different job, so the row states which job in the cell beside it. **What the form is for:** the case where a table's own convention would make a correction read as a resolution, and striking silently would claim work that was never done.
* **A reference repaired after losing its referent** — `ROADMAP.md` l.10678, which announces the form for the repair made two lines above it, where *this turn's mutation* was resolved to *`b8a0c5a`'s*. That document's corrections strike a figure found wrong, a decision superseded, or an inference restated; none of them repairs a phrase that was true when written and became unreadable because the document kept growing around it. **What the form is for:** the case where nothing about the claim changed and only the phrase pointing at it stopped pointing — where an ordinary correction would misdescribe a still-correct statement as an error.

**These are two instances and are recorded as two.** Whether either becomes a convention is not settled here — one occurrence of each is not a pattern — and neither licenses a third form going unannounced: an invented correction form that is not named as invented is an in-place edit with better manners, which is what the three routes above refuse.

This exists because a project with one developer and a compressed timeline will otherwise relitigate settled questions every few months, and because an AI agent given the repository has no other way to know why a choice was made.

## Written

| # | Decision |
|---|---|
| [0001](0001-two-graph-model.md) | Reference and evidence graphs are disjoint |
| [0002](0002-python-backend.md) | Python for the backend |
| [0003](0003-kuzu-over-neo4j.md) | Kùzu for the graph store |
| [0004](0004-split-storage.md) | Split storage: graph identity in Kùzu, quantitative matrices in DuckDB |
| [0005](0005-modificationsite-and-protein-keys.md) | Sequence version and isoform as part of the `ModificationSite` and `Protein` keys |
| [0006](0006-modifier-as-defeasible-assignment.md) | Modifier identity is a defeasible assignment, not a site property |
| [0007](0007-perseus-s0-test.md) | Perseus-compatible modified *t*-test with `s0`, implemented locally — **superseded by 0011** |
| [0008](0008-append-only-assertions.md) | Append-only assertions with explicit retraction |
| [0009](0009-curation-as-activity.md) | Sample-to-condition mapping is a curation activity, not configuration |
| [0010](0010-contracts-not-tables.md) | `Observation` and `EvidencedInference` are contracts, not tables |
| [0011](0011-pluggable-statistics-registry.md) | Statistical tests pluggable behind a registry — supersedes 0007, **superseded by 0015** |
| [0012](0012-graph-is-derived.md) | The graph is derived, not authoritative; rebuild over migration |
| [0013](0013-matrices-retained-permanently.md) | Quantitative matrices retained permanently, never only derived statistics |
| [0014](0014-adapter-order.md) | Adapter order under pipeline uncertainty: DIA-NN, MaxQuant, FragPipe — **superseded by 0017** |
| [0015](0015-perseus-s0-default.md) | Perseus `s0` test as the default statistical entry — supersedes 0011 |
| [0016](0016-embargoed-datasets.md) | Embargoed dataset state for unpublished collaborator data |
| [0017](0017-downstream-positioning.md) | Downstream positioning, with both ingestion paths |
| [0019](0019-changeset-structural-validation.md) | Change-sets are self-contained; structural validation precedes invariants |
| [0020](0020-deterministic-evidence-ids.md) | Deterministic, content-derived ids for evidence nodes (not ULIDs) |
| [0021](0021-no-contingent-identifying-fields.md) | An identifying field may be absent only when its absence is determined — no fallback keys |
| [0022](0022-protein-group-ambiguity.md) | Multi-mapping is carried by the observation, at both grains |
| [0023](0023-one-relationship-per-fact.md) | One relationship per fact: `SITE_ON` narrows to `MANY_ONE`; two duplicate names dropped |
| [0024](0024-keying-is-not-assignment.md) | Keying a site is not assigning a protein; `reviewed_preferred` leaves the basis enum |
| [0025](0025-adjusted-by-is-an-anchor.md) | `ADJUSTED_BY` is an anchor on `DifferentialResult`; the first self-referential one |
| [0026](0026-basis-classifies-warrants.md) | §5.3's `basis` classifies warrants, not containers; a composed mapping records its weakest link |
| [0027](0027-contrast-stays-evidence-with-an-experiment-anchor.md) | `Contrast` stays an evidence node and is scoped by an `Experiment` anchor (§11 Q1) |
| [0028](0028-the-anchor-curation-record-is-one-supersession.md) | The anchor's curation record is one supersession; two of its four defects are not defects |
| [0029](0029-how-an-experiment-id-reaches-the-contrast-mints.md) | How an `Experiment` id reaches the two `Contrast` mints; the two sites get different answers |
| [0030](0030-what-a-reference-to-author-correspondence-must-contain.md) | What a reference to author correspondence must contain; attribution where verification is impossible |
| [0031](0031-selection-outside-the-surveys-route.md) | Selection outside the survey's route; C0's gates range over the site-grain table only |

## Queued

Seeded in [`../ARCHITECTURE.md`](../ARCHITECTURE.md) § Seed ADRs, not yet written up. Listed here so the numbering is reserved.

| # | Decision |
|---|---|
| 0018 | Typed API routes only; the front end never queries the graph directly |

Numbers 0015 and 0016 were written ahead of 0004–0014 because they arose from author correspondence rather than from design. Writing them out of sequence is correct — the numbering reserves identity, not chronology.

**Both tables were stale and the two documents disagreed about the reserved set — corrected 2026-08-09.** 0004 and 0013 had been written, marked `Accepted`, and left listed as Queued while absent from Written; 0006–0012 and 0014 were written that day. And this table omitted **0018**, which `ARCHITECTURE.md` § Seed ADRs reserves, so the two enumerations of reserved numbers disagreed by one. Reconciled in this direction because the Queued table's stated job is reserving numbers, and 0018 is reserved and unwritten; the seed list is the source and this is the index of it. Nothing else is queued.

**Which is the enumeration that can rot.** A number is reserved in two places and written in one, and ~~nothing checks the three against each other — no test reads `decisions/`~~ — **`tests/test_decision_index.py` does, since 2026-08-10.** Nine assertions over the three records and the directory: Written against the directory in both directions, every Written link resolving on disk, `ARCHITECTURE.md` §5's unstruck set against Queued, Queued disjoint from Written, and §5's header count claim. Every parsed set carries a **pinned count**, because a regex that matches nothing compares equal to another that matched nothing — and that was not hypothetical: the first row-regex written for it found **zero** Written rows against a table of 24, and the first strike counter counted all 18 seeds instead of the 17 struck. Eight mutations, each read back off disk first. **What §5 cannot support is asserted nowhere**: it holds `0001`–`0018`, so *every Written entry appears in §5* is false by construction for `0019`–`0025`. The staleness above is what the gap cost, and the first green run is evidence that the 2026-08-09 hand reconciliation was complete rather than evidence about the class.

## Format

Keep them short — context, decision, consequences, alternatives rejected. The value is in recording what was considered and discarded, not in length.

```markdown
# ADR-NNNN — Title

| | |
|---|---|
| Status | Proposed / Accepted / Superseded |
| Date | YYYY-MM-DD |
| Supersedes | — |
| Superseded by | — |

## Context
## Decision
## Consequences
## Alternatives considered
```
