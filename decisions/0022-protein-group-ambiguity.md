# ADR-0022 — Multi-mapping is carried by the observation, at both grains

| | |
|---|---|
| Status | Accepted |
| Date | 2026-08-07 |
| Supersedes | — |
| Superseded by | — |

## Context

`bzk/adapters/perseus.py` refuses any row naming more than one accession. It has to: a
`ProteinObservation`'s identity is its two anchors — `Dataset` (`REPORTS_PROTEIN`) and `Protein`
(`RESOLVES_TO_PROTEIN`) — with no identifying fields of its own, so **the id *is* the pick**. The
node cannot be minted without choosing one protein, and choosing one is the razor pick §6.3 exists
to forbid. There is also nowhere to record the ambiguity: `PROTEIN_ASSIGNMENT_FOR` is
`FROM ProteinAssignment TO SiteObservation` only.

I14 did not catch this because it is phrased about peptides — *"a multi-mapping peptide is not
rendered against one protein"* — and at protein grain there is no peptide.

### The measurement

`ROADMAP.md` § Protein-group ambiguity at protein grain, 2026-08-07. Three real artefacts: the two
BJC supplementary tables, which are genuine Perseus protein-level exports of the paper this
reproduction is anchored to, and `HAP1_USP18KO_proteinGroups.txt` upstream of Perseus.

| | rows | multi-accession (`Majority protein IDs`) | of which distinct-gene |
|---|---|---|---|
| Supp Data 2 (Perseus) | 25 | 72.0% | 9 of 18 |
| Supp Data 3 (Perseus) | 323 | **77.4%** | 166 of 250 — **51.4% of all rows** |
| MaxQuant proteinGroups | 4,797 | **77.1%** | 2,707 of 3,698 — **56.4% of all rows** |

Three things follow.

**This is not an edge case.** 77% is the same order as §6.3's 82% for sites, which is the number
that settled the site grain. The adapter currently refuses roughly three rows in four of every
protein-level table this group produces, so it is unusable on real input until this is settled.

**There is no cheap fallback.** Only a quarter to a half of the multi-accession rows are
isoform-only — one gene, isoform unresolved, where "resolve to the gene" would at least be
available. The rest name genuinely different genes: **over half of all rows** in both larger
artefacts. Resolving to the gene answers a minority of the problem.

**It is not a Perseus quirk.** Perseus' selection barely moves the figure — 77.4% against MaxQuant's
77.1%. The protein grain was modelled less completely than the site grain, and Perseus is merely the
first thing to use it. This is the same shape as the missing `RESULT_FOR_PROTEIN` edge.

### This is §6.3's open question, one grain up

§6.3 already records the identical tension for sites and defers it:

> **The `SITE_ON` declaration is wider than the key can express.** … Recorded rather than resolved:
> either the key gains a way to name several parents, or the relationship narrows to `MANY_ONE` and
> multi-mapping stays entirely within `ProteinAssignment`. Settle when the first search-output
> adapter constructs both (weeks 5–6).

`SITE_ON` is `MANY_MANY` while the `ModificationSite` key composes exactly one parent. That is the
same mismatch between what a relationship permits and what an identity can express. Settling the two
grains separately would answer one question twice, six weeks apart, and probably differently.

## Decision

**Multi-mapping is carried by the observation's identity, and the pick — where one is made — is a
separate, evidenced inference.** Both grains, one shape.

1. **`ProteinObservation` gains `candidate_proteins STRING[]` as an identifying field**, and
   `RESOLVES_TO_PROTEIN` becomes `MANY_MANY`, one edge per member. The observation is then keyable
   without choosing, and what it asserts is what the search reported.
2. **`PROTEIN_ASSIGNMENT_FOR` accepts `ProteinObservation` as well as `SiteObservation`**, as a
   two-pair `REL TABLE`. Verified available on the pinned Kùzu 0.11.3, writes included.
3. **I14 is rephrased from "a multi-mapping peptide" to "a multi-mapping observation"**, so it
   reaches a grain with no peptide in it, and gains a second write-time check: a
   `ProteinObservation` naming several candidates must carry `RESOLVES_TO_PROTEIN` to *every* one,
   never a subset. Without it the claim I14 blocks on `ASSIGNS_PROTEIN` walks in through a
   different edge.

   *Corrected during review.* An earlier draft also extended it to `SITE_ON`. That is not
   enforceable as a write-time error: `RESOLVES_TO_SITE` is `MANY_ONE`, so resolving to every
   candidate is unavailable at site grain, and rejecting the single site it names would refuse 82%
   of sites with nothing that would satisfy the check — `razor` is `ambiguous` by §6.3's own table.
   The site half stays what *rendered* has always meant: a display and export obligation.
4. **The site grain takes the same shape**: `SiteObservation` gains the same identifying
   `candidate_proteins`. The observation names every candidate; `RESOLVES_TO_SITE` stays `MANY_ONE`.

   *Corrected during review.* An earlier draft said the site half implements §6.3's *"the key gains
   a way to name several parents"* branch, and that overstated it twice. First, a `ModificationSite`
   key is `{ProteinSequence.id}#{residue}{position}#{modification_type}` and **the position differs
   per protein** — a peptide shared between two proteins sits at different absolute positions in
   each — so one site cannot honestly span two parents whatever `SITE_ON` permits. That argues for
   the *narrowing* branch, which this ADR does not take either: it is still for the first
   search-output adapter. Second, widening `RESOLVES_TO_SITE` would have to drop the
   `ModificationSite` anchor from `SiteObservation`'s identity, and two GlyGly sites on one peptide
   share a peptide sequence, a candidate set and a dataset — they would collide. That is
   `ONTOLOGY.md` §11 Q3, unsettled. So the site half here records the observed candidate set and
   nothing more, which is real (two different candidate sets no longer produce one id) and is not
   the whole of §6.3's question.

### The two candidate sets are different facts, and the data says so loudly

`ProteinObservation.candidate_proteins` is **observed** — what the search reported for that row.
`ProteinAssignment.candidate_proteins` is **inferential** — what the assignment weighed, which may
be narrower after contaminant filtering or a reviewed-over-TrEMBL preference. This is I19's
observed-versus-reported distinction one level down, and it is the reason **no guard asserts the two
agree**. A guard would forbid recording exactly the narrowing `basis = 'leading'` exists to name.

It survives contact with both sections, and with the data:

- **§3** already describes `candidate_modifiers` as *"the surviving candidate set, which diverges
  from the conclusion whenever more than one candidate remains"* — "surviving" is post-inference.
- **§6.3**'s DDL comment describes the same shape as *"every accession the peptide could derive
  from"* — which is pre-inference. The two documents have been describing one field in two ways;
  splitting the roles across two nodes resolves that rather than adding to it.
- **§6.3** also states that *"MaxQuant's `Leading proteins` and `Protein` columns are its own
  razor-rule inference, not ground truth, and are recorded as such"*. `Majority protein IDs` is that
  inference; `Protein IDs` is closer to the observation.
- **§5.1** is unaffected: the contract requires `RESOLVES_TO → <reference node>`, and every member
  of a group is a `Protein`. Widening the edge to `MANY_MANY` does not change what it points at.

**Measured, not assumed:** the two columns disagree on **72.0%, 66.9% and 51.7%** of rows in the
three artefacts. "Usually identical" is false — they differ on the majority of rows, and a guard
asserting agreement would fail on more than half of every real table. Two DDL comments, then, and
no guard.

### Not chosen

**A separate `ProteinGroup` node.** Conceptually the cleanest and the most expensive. §5.1 requires
an observation to resolve to a *reference* node, and no authority mints protein groups — a group is
this search's inference, so it is evidence, and a `ProteinGroupObservation` resolving to it breaks
the contract as written. Keying forks badly too: on members alone it is dataset-independent but
asserts that one accession set is one group across searches, which is not true; anchored on
`Dataset` it is honest and cross-queryable by nothing. And it buys no expressiveness over
`candidate_proteins`, while adding a node table, two relationships and an `Observation` subtype that
§10 then obliges every consumer to handle.

**Extending `PROTEIN_ASSIGNMENT_FOR` alone.** It gives the ambiguity somewhere to live but leaves
the observation keyed on one protein, so `RESOLVES_TO_PROTEIN` still asserts "this is a measurement
of P19525" while the assignment beside it says the candidates were `{P19525, O43593}` at
`confidence = 'ambiguous'`. I14 blocks that claim on `ASSIGNS_PROTEIN` and says nothing about
`RESOLVES_TO_PROTEIN`, so the identical assertion enters through an unguarded door. Point 2 above is
kept — but as half of the decision, not as the whole of it.

**Requiring resolution upstream** — the current behaviour: refuse, and ask for one accession per
row. Rejected because it moves the razor pick outside the platform where nothing records it, which
is the gap `VISION.md` says the product exists to close. It also fails on the measurement: it
discards 77% of every table.

## Consequences

**Positive.** The graph stops asserting a protein identity the data does not support at protein
grain, and records the observed candidate set at both. §6.3's open question is **narrowed, not
closed** — corrected during review; see point 4 — because multi-mapping is no longer visible only
through a razor pick, while `SITE_ON` still permits more than the `ModificationSite` key expresses. `perseus.py` becomes usable
on a real export. The observed/inferential split makes MaxQuant's own narrowing recordable as what
it is — `Protein IDs` to the observation, `Majority protein IDs` to a `ProteinAssignment` with
`basis = 'leading'` — which is §6.3's *"recorded as such"* actually implemented. The canonicalization
already exists: `keys.canonical_value` sorts `STRING[]` before hashing, so ordering cannot fork an
id (I7).

**Negative — every `ProteinObservation` and `SiteObservation` id moves.** Today that costs nothing:
no observation of either kind has ever been stored. The graph holds 16 curation nodes and no
observations, `perseus.py` refuses the rows that would create any, and the MaxQuant adapter is not
written. After either lands, this is a migration. **The cost of this decision is zero now and rises
the moment the next adapter runs** — the same argument that made the ADR-0019 discriminator rename
mechanical rather than a migration.

**Negative — a wider blast radius than a DDL edit.** `RelTable` models a single `src`/`dst` pair, so
a two-pair relationship touches `schema.py`'s dataclass and `_rel_ddl`, `invariants._REL_ENDPOINTS`,
`store._REL_ENDPOINTS`, `test_schema`'s DDL parser and §3's anchor-direction guard. Six sites, all
mechanical, all guarded by existing tests.

**Consequence beyond the schema: two records to revisit.** `HANDOFF.md` §8 states that *"the Perseus
(analysis-output) adapter has no candidate sets or razor picks, so I17 does not apply there"*, and
`ARCHITECTURE.md` §3 describes a Perseus result table as having *"no localisation or razor-pick
complexity"*. Both were correct about localisation and wrong about razor picks: `Majority protein
IDs` is a candidate set and it is MaxQuant's own pick. **This is a correction to a decision recorded
on 2026-08-07, not the discovery of an oversight** — the reasoning was sound and the premise was
false, and the measurement above is what falsified it. I17 does reach the analysis-output adapter.

## Open

**The reviewed-over-TrEMBL frequency at protein grain is unmeasured.** §6.3 measured it for sites —
in 4 of 8 sampled, the razor pick was TrEMBL while a reviewed entry sat in the same candidate set —
and I17 exists because of that. The protein-grain equivalent needs a UniProt review-status lookup
per member across 4,797 groups, which is a resolver run rather than a file read, so it is not in
this measurement. It does not change the decision; it changes how often `basis = 'reviewed_preferred'`
will be the right label once the pick is recordable.
