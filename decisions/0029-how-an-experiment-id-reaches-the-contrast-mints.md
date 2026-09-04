# ADR-0029 — How an `Experiment` id reaches the two `Contrast` mints, and why the two answers differ

| | |
|---|---|
| Status | Proposed |
| Date | 2026-08-31 |
| Reviewed | 2026-09-03 — four findings, two grounds struck, one defect in the decision; held `Proposed` |
| Supersedes | — |
| Superseded by | — |

## Review

Landed `Proposed` at `2028686` and reviewed at `c5dc140`. **The record is held, not accepted.**
Finding B struck the ground Q1 rejects option (b) on *and* the sentence that selects (a) over it,
and the argument for (b) that the correct field list makes available was never engaged — so Q1's
comparison has to be run again against a `DeclaredRun` described as it is. Q2, Q3 and the
measurement stand.

### A — the ordering is stated twice at two scopes, and the numerals in the operative sentence are unqualified. Defect in the decision

**Two texts.** l.119–121: *"So the three parts move together: implied change 4 first or alongside,
then Q1's parameter, then implied changes 1, 3 and 5."* l.197, closing the record's own numbered
list: *"**Then ADR-0027's implied changes 1, 3 and 5.** Not before the four above."*

**Which record each numeral belongs to.** In l.119 every numeral is **ADR-0027's** — *implied change
4* is ADR-0027's fourth (the loader materialising `Contrast`, per l.77 and l.191) and *implied
changes 1, 3 and 5* are ADR-0027's (per l.13 and l.197); only *"Q1's parameter"* names an item of
**this** record, and it names it by description. In the list at l.188–197 every numeral is **this
record's own**: item 1 is Q1's parameter, item 2 is ADR-0027's #4, item 3 is the adapter change,
item 4 is the I21 generalisation, item 5 is ADR-0027's #1, #3 and #5.

**The collision, ruled separately.** All four of l.119's unqualified numerals — 4, and 1/3/5 —
collide with items this record numbers 4, 1, 3 and 5, and two of them denote different things
under the two readings: ADR-0027's #4 is the loader change, this record's item 4 is the I21
generalisation. The sentence is *recoverable*, because reading the numerals as this record's own
makes item 1 appear twice and is incoherent — but recovery by detected incoherence is not
disambiguation. **The record qualifies its numerals at l.13, l.77, l.191 and l.197 and drops the
qualification in the one sentence a builder would work from.** That is a defect, and it is this
record's, not ADR-0027's.

**The orderings, ruled separately from the collision.** They are not two conflicting orderings.
Attributed correctly, l.119 states *item 2 ≤ item 1 < item 5*; the list states *{1, 2, 3, 4} < 5*,
with item 2 a prerequisite of ADR-0027's #3 and item 4 *"before or with the anchor landing"*. Each
carries a constraint the other omits, and neither contradicts the other. **The list governs**,
because it is the record's final statement and because it postdates §Q3 — l.119 closes the Q1/Q2
section and could not have covered a part Q3 had not yet introduced.

**Why that is nonetheless a defect in the decision rather than presentation.** l.119 says *"the
three parts"*, which reads as exhaustive, and it is not: item 4, the I21 generalisation, is the
fourth part, and Q3 makes it a prerequisite of the anchor landing. **A builder following l.119
alone lands the anchor with no null-anchor guard** — precisely the hazard Q3 exists to close. An
ordering is what this record contributes over ADR-0027 (*"ADR-0027 states no ordering among its six
items"*), so an ordering stated once incompletely and once completely, without either deferring to
the other, is a defect in the thing decided. **Ruling (a).** Q1's, Q2's and Q3's answers are
untouched by it.

### B — `DeclaredRun` is not what Q1 says it is, and (a) is not the only loud option. Two grounds struck

**The field list.** `DeclaredRun` has **ten** fields at `bzk/analysis/differential.py` ~~l.33–42~~
**l.33–43 — range corrected 2026-09-04: l.33–41 are the nine fields through `parameters_json`, l.42
is the comment, and the line the short range omitted is l.43, which carries `label` — the field
this finding turns on**:
`quantity`, `test`, `fdr_method`, `localization_threshold`, `filters_applied`, `imputation`,
`numerator`, `denominator`, `parameters_json`, **`label`**. l.55–56 enumerates **nine** and omits
`label` — whose own comment reads *"Free-text, excluded from identity (§3). Never load-bearing."*
**The omitted field is the one that refutes the category**: a free-text display name is not a
parameter of a statistical test, and it is passed at both construction sites (l.304, l.29).

**What the ten fields actually are.** Six key an `Analysis` (`quantity`, `test`, `fdr_method`,
`localization_threshold`, `filters_applied`, `parameters_json` are all in
`schema.IDENTITY["Analysis"].fields`); `imputation` supplies the `Imputation` child fold on that
same identity; **`numerator` and `denominator` are `schema.IDENTITY["Contrast"].fields` entire**,
and l.119–120 mints the `Contrast` id from exactly them; `label` is excluded from identity
altogether. Classified as the finding asks: `localization_threshold` is a **filter** threshold,
`filters_applied` is a **filter** record, and `numerator` and `denominator` are **references to
graph content** — the complete key of the node this record is about. **At most five of ten are
parameters of a test.**

**So the category ground is struck.** `DeclaredRun` is not *"the declaration of statistical
intent"*; it is the identity material for three evidence nodes plus one display label. **An
`Experiment` id is a graph reference — and so are two fields already on it**, which is the argument
*for* (b) that the nine-field list made invisible: the anchor would sit beside the rest of the key
it anchors.

**The selecting sentence is struck too.** l.71: *"(a) is chosen because it is the only option where
forgetting is a `TypeError`."* **False, demonstrated**: a field with no default on a frozen
dataclass raises `TypeError: __init__() missing 1 required positional argument` when omitted. (b)
with a required field is exactly as loud as (a); only (d) is quiet.

**Whether the second ground carries (b)'s rejection alone. As stated, no.** *"The obligation would
be discharged once, invisibly, at a module-level constant"* is contingent on the test file's shape
— the production site constructs `DeclaredRun` at l.304 and calls at l.322, in one function, with
no module-level constant — and it argues from **cost**, in a paragraph that opens *"rejected on
category, not on cost."* Its structural core does carry, restated: **a `DeclaredRun` is 1:N with
`site_change_set` calls** (the test's `RUN` at l.29 serves all three), so an `experiment_id` on it
is asserted once for calls that need not share an experiment. That restatement is not in the
record.

**The two call-site figures describe different populations and do not contradict each other.**
Measured: `site_change_set` has **four** call sites — `bzk/sources/pxd018299_differential.py` l.322
and `tests/test_analysis_differential.py` l.84, l.138, l.176 — of which **three are tests**
(l.62 is the definition, not a call), and **two** `DeclaredRun` constructions (l.304, l.29). *"The
three callers"* is the table's own column head, *"the four call sites"* is l.188. Both correct.
**What the table under-reports is (b)'s real cost**: *"none change"* is true of call sites and
false of construction sites, both of which would change, visibly.

**Ruling (b) — two grounds struck. The decision does not survive on the grounds that remain, and
that is why the record is held.** What remains is sound but insufficient: (c) and (d) are rejected
soundly and independently (a label search that returns nothing; a default that always succeeds), so
two of four options are eliminated. The choice between (a) and (b) rested entirely on the two
struck grounds. It may well come out (a) again on the arity ground above — but that is a comparison
this record has not made.

**Made 2026-09-04, and not on the arity ground.** See *Q1 re-run* below: the arity ground was
established not to carry, and (a) stands on a different one. This ruling is unchanged — both
grounds named here are still struck — and the record is still held, acceptance being the
reviewer's half of the round-trip rather than a consequence of the comparison landing.

### C — a guard of the named shape is writable, and the claim is narrowed. Ground struck

l.180–184 rules the class *"is real and is not machine-checkable"* and stays open *"for a
structural reason rather than for want of writing a guard."*

**The named check is writable, and it is not vacuous.** Measured over `bzk/` by AST walk —
**matching both bare and attribute call forms, and excluding `bzk/ontology/invariants.py`, whose
two calls recompute an already-minted digest for comparison rather than mint an id that is
written**: **22** `evidence_id` minting call sites, **all 22 with a string-literal label** and none
computed; **12 of `schema.IDENTITY`'s 24 labels carry non-empty `anchors`**; ~~**14 call sites**~~
**15 call sites** name an anchored label and every one of them passes an anchor argument. So *for
every anchored label, every `evidence_id` call for it passes anchor ids* has ~~fourteen~~
**fifteen** live subjects today, passes today, and **turns red the moment `schema.py` gains
`Contrast`'s anchor without `differential.py` l.120 and `perseus.py` l.226 being threaded** — which
is the hazard l.112–117 describes.

**Both figures were corrected 2026-09-04 at `b031825`, and they are two different defects.** The
count of anchored sites was a plain miscount with no instrument behind it: the walk that produced
this paragraph printed 22 rows, of which **seven** name an unanchored label — four `Dataset`, two
`Contrast`, one `Project` — leaving **15**, and *fourteen* was written twice, once in figures and
once in words. **The 22 is not wrong, but its instrument was unstated.** Run as this paragraph
originally described it — an unrestricted *"AST walk over `bzk/`"* — the number is **24**, because
`bzk/ontology/invariants.py` l.646 and l.652 call `keys.evidence_id` in the attribute form and the
original walk matched bare-name calls only. **So the original 22 was reached by two errors that
cancelled**, and a reader re-deriving it from the stated instrument would not have got it. **The
exclusion is stated and kept rather than the figure changed**: the figure counts *minting* sites,
and the guard this finding describes is about whether a mint supplies its anchors — a
recomputation that deliberately reproduces an existing id in order to compare against it is not a
site where an anchor can be forgotten. Pre-registered at `ed1f6db`, alone and before any measuring
code existed, with all six expected figures — 22, 15, 24, 2, 12 and 0 non-literal labels —
returned exactly. **Finding C's ruling is untouched by either correction**: the guard is
non-vacuous at 14, 15 or 17 subjects, and *"it does not catch the class"* stands as written.

**What it would not catch.** It is syntactic: an anchor argument present but resolving to `None`,
or a dict missing a key, still renders `␀null` and passes. It reads only `bzk/`. It needs a literal
label. And it does not catch **the class** — a record describing an implied change whose
reachability was never established leaves nothing in the tree to assert over, because the change
is not in the tree.

**Does that distinction rescue the claim? Half of it.** *The class is not machine-checkable* stands,
and it stands for the reason the record gives: reachability of an unwritten change is answered by
reading call sites. *It stays open for want of a structural reason rather than a guard* does not
stand, because it reads as *no guard was available* and one is — a mirror between `schema.IDENTITY`
and the call sites, of exactly the kind this repository guards everywhere else. **Ruling (b).** The
decision — that this record closes one instance and no class — survives on the surviving half.

### D — the measurement reproduces exactly. No defect

Reproduced in memory, writing nothing, with the identity spec substituted and restored and the
restoration asserted. `Experiment` id `bzk:222c1d19e977939d440f321823de5b94`, taken from
`load_path` rather than invented.

| Contrast | current | anchored | null-anchor |
|---|---|---|---|
| `KO_IFN_vs_WT_IFN` | `bzk:f7c41f45886d3cf7c5c5ce8d59b0e267` | `bzk:8f9a06344675831a26dd59b2bf8c4393` | `bzk:03ccd33e0d41b99f61407b9b30462df9` |
| `KO_vs_WT_unstimulated` | `bzk:852326f345b67bc266845f675d1d63da` | `bzk:d78903eeb3746b372e2100d3b6e52906` | `bzk:7fa11302cf15805ef6cd325546b6be38` |

**All six match the record**, across all three sets, and the three are mutually distinct per
contrast. The anchor relationship name does not enter the digest — `keys.py` l.335 discards it —
so the anchored figures do not depend on what the edge is eventually called.

**The closing claim holds, checked rather than taken.** `graph.kuzu/` is absent and no DuckDB file
exists; `bzk/curation/loader.py` contains no `evidence_id("Contrast", …)` call — the only two in
`bzk/` are `differential.py` l.120 and `perseus.py` l.226 — and l.357–359 hands
`contrasts_of_interest` on as a tuple without materialising. **Ruling (c).**

### Q1 re-run — (a) stands, on a ground read off the tree, 2026-09-04

Finding B struck both grounds the (a)-versus-(b) choice rested on and left the comparison unmade.
This makes it. **(b) was written out at full strength first, before either option was chosen**, and
what follows immediately below is the case for the option this section does not take.

#### (b) at its strongest

`site_change_set` computes nothing — the module docstring says *"Nothing here computes anything:
the caller passes the statistics it already has."* So `DeclaredRun` is not a declaration of intent
that the function acts on. **It is the caller's supply of the material three evidence nodes are
keyed from**, and that is measurable rather than interpretive: six of its ten fields are in
`schema.IDENTITY["Analysis"].fields`, `imputation` supplies the `Imputation` child fold on that
same identity, and `numerator` and `denominator` are `schema.IDENTITY["Contrast"].fields` entire —
with `bzk/analysis/differential.py` l.119–120 building the contrast dict from exactly those two and
minting the id from it.

**On that description an `Experiment` id is not a foreign object smuggled into a statistics
declaration. It is the one missing component of the `Contrast` key, and the other two components
are already on the object.** Putting it anywhere else splits a single node's key across two
parameters — `numerator` and `denominator` arriving on `run`, the anchor arriving as a sibling
keyword — and an id whose components are assembled from scattered sources is an id no one site can
be held responsible for, which is the concern ADR-0020 and I21 both exist for. **And this record's
own Q2 decides the symmetric thing one layer over**: the adapter is to receive contrast ids
*pre-keyed* rather than assemble them. Under (b) the analysis layer likewise receives the whole key
in one object, and the two layers are treated alike.

This is a stronger form of (b) than Finding B sketched, because it rests on what `site_change_set`
does rather than on what `DeclaredRun` is named.

#### The arity ground does not carry, and that is established rather than asserted

Finding B offered a restatement of the second ground: a `DeclaredRun` is 1:N with `site_change_set`
calls, so an `experiment_id` on it would be asserted once for calls that need not share an
experiment. **The 1:N holds and is uninformative.** Re-measured at `b031825` by AST walk over
`bzk/` and `tests/` matching `ast.Call` with a bare `ast.Name` callee — which excludes the `def` at
l.62 by construction rather than by hand: **four** call sites
(`bzk/sources/pxd018299_differential.py` l.322; `tests/test_analysis_differential.py` l.84, l.138,
l.176) and **two** constructions (l.304, l.29). Production is 1:1; the test file is 1:3 from its
module-level `RUN`. **But all three test callers take their `dataset` from the same `_attached()`
helper**, so the tree holds no case of one `DeclaredRun` spanning two experiments, and nothing in
it establishes whether that would be legitimate.

**On its own the arity ground would therefore leave Q1 undecidable**, and it is not the ground
taken.

#### The ground that carries: no anchor in this function arrives on `DeclaredRun`

Read off `site_change_set` whole — every node it mints, every anchor, and where each anchor comes
from:

| Node minted | Anchors supplied | Source of each anchor |
|---|---|---|
| `Analysis`, l.109 | `Dataset` | **the `dataset` keyword parameter** |
| `Imputation`, l.115 | `Analysis` | an id minted six lines earlier |
| `Contrast`, l.120 | none today | — |
| `DifferentialResult`, l.145 | `Analysis`, `SiteObservation`, `Contrast` | two ids minted earlier in the call; one from `SiteResult.observation_id` |

**The rule is exceptionless and it is already in the code: `DeclaredRun` supplies identifying
fields and supplies no anchor.** Every anchor here is the `dataset` keyword parameter, an id minted
earlier in the same call, or a value carried on `SiteResult`.

**That answers (b) at its strongest on (b)'s own terms.** (b) says the anchor belongs beside the
rest of the key it anchors — but no anchor in this function sits beside its fields. `Analysis`'s
**twelve** identifying fields arrive on `run` while its anchor arrives as a keyword parameter, and
`DifferentialResult`'s three anchors sit nowhere near its fields either. **Putting `experiment_id`
on `DeclaredRun` would make `Contrast` the only node in this function whose anchor travels with its
fields**, and it would do so in the one function where the separation is uniform across four node
types.

**Decision: (a) stands** — a required keyword-only `experiment_id: str` on `site_change_set` — **on
the ground that an `Experiment` id is an anchor, and anchors do not travel on `DeclaredRun`.** The
ground is read off the function under discussion rather than argued from what the dataclass is
called, which is what Finding B struck the old one for. The four sites outcome (b) would have
required rewriting — implied change 1, the options table, the ordering list and the *"under-reports
(b)'s real cost"* sentence — are untouched, because (b) was not chosen.

**This does not accept the record.** The record stays `Proposed`; acceptance is the reviewer's half
of the round-trip. The three struck or narrowed grounds stay struck and narrowed.

## Scope

Decides how an `Experiment` id reaches `bzk/analysis/differential.py` l.120 and
`bzk/adapters/perseus.py` l.226, so that ADR-0027's implied changes 1, 3 and 5 become buildable.
**This record decides and does not build:** no `Contrast` is anchored, no signature changes, no
`RelTable` is added, no invariant is written.

**The determination this rests on** is `ROADMAP.md` l.11189–11289 — 101 lines under six `####`
subsections — which ruled verdict **(c)**, an `Experiment` id reachable at neither site, and landed
nothing.

## ADR-0027's implied-changes list reads as buildable and is not

Said plainly, because it is the reason this record exists. ADR-0027's six implied changes are
written as a list of consequences, each describable and each apparently independent. **Implied
change 3 is not buildable at all as the code stands**, and the record does not say so — it names
the anchor, the `RelTable` and the §3 cell, and never asks whether anything can supply the anchor.

**This record is the change ADR-0027 never named.** ADR-0027 is `Accepted` and is not amended.

## Q1 — how `site_change_set` gets an `Experiment` id

**Decision: a required keyword-only `experiment_id: str` parameter on `site_change_set`.**

**The id exists in the caller, and this was verified rather than assumed.**
`bzk/sources/pxd018299_differential.py` calls `load_path(CURATION)` at l.143 and `site_change_set` at
l.322 in the same function, and `LoadedCuration` carries `experiment_id: str` at
`bzk/curation/loader.py` l.153. **So the value is in scope at the only non-test call site, twelve
lines of local flow apart.**

### The options, and what each costs the callers

There are **four** `site_change_set` call sites — `pxd018299_differential.py` l.322 and
`tests/test_analysis_differential.py` l.84, l.138 and l.176 — and **two** `DeclaredRun`
constructions, at `pxd018299_differential.py` l.304 and `tests/test_analysis_differential.py` l.29.
Both counts are measured, not estimated.

| Option | Cost at the three test callers | Verdict |
|---|---|---|
| **(a) required keyword parameter** | **all three change**, each gaining one argument; the module-level `RUN` is untouched | **chosen** |
| (b) field on `DeclaredRun` | **none change** — the test's module-level `RUN` at l.29 gains the field and all three callers inherit it | rejected |
| (c) entry in `attached_nodes` | none change syntactically; each would have to be checked for an `Experiment` node | rejected |
| (d) defaulted keyword parameter | none change | rejected |

~~**(b) is rejected on category, not on cost.** `DeclaredRun` holds the declaration of statistical
intent — `quantity`, `test`, `fdr_method`, `localization_threshold`, `filters_applied`,
`imputation`, `numerator`, `denominator`, `parameters_json`. **An `Experiment` id is a graph
reference, not a parameter of a test**~~ — **ground struck by Review finding B, 2026-09-03: the list
is nine fields of ten, the omitted `label` is not a parameter of a test, and `numerator` and
`denominator` are `Contrast`'s complete identity.** The remainder of the sentence stands as written:
the fact that it would cost the three callers nothing is
precisely what makes it dangerous: the obligation would be discharged once, invisibly, at a
module-level constant.

**(c) is rejected because it cannot fail loudly.** `attached_nodes` is *"the slice of the ingestion
change-set the results attach to, passed in whole, as the adapter minted them"* — and **no adapter
mints an `Experiment`**; the only `evidence_id("Experiment", …)` call in `bzk/` is the curation
loader's at l.320. So the node would have to be injected by the caller and then found by a
label search, which returns nothing when the caller forgets. **A lookup that silently returns
nothing renders `␀null`**, which is the hazard this record exists to avoid.

**(d) is rejected for the same reason in its purest form.** A default is a lookup that always
succeeds and always returns the wrong thing.

~~**(a) is chosen because it is the only option where forgetting is a `TypeError`.**~~ — **struck by
Review finding B, 2026-09-03: a field with no default on a frozen dataclass raises `TypeError` on
omission, so (b) with a required field is exactly as loud. Only (d) is quiet.** Costing the three
test callers a line each is the point of it, not a price paid for it.

**Ground supplied 2026-09-04 by the Q1 re-run in the Review, after (b) was argued at full
strength: an `Experiment` id is an anchor, and in this function no anchor arrives on
`DeclaredRun`** — `Analysis`'s comes from the `dataset` keyword parameter, `Imputation`'s and
`DifferentialResult`'s from ids minted earlier in the same call. **(a) stands on that, not on the
struck sentence above and not on the arity ground, which was established not to carry.**

## Q2 — whether `SampleMapping` widens

**Decision: it does not. The loader materialises `Contrast` and hands the adapter pre-keyed ids, as
it already does for samples.** That is ADR-0027's implied change 4, which this record makes a
**prerequisite** of implied change 3.

**This is a contract question and it needed its own ground, which is what `SampleMapping`'s own
docstring supplies.** l.38–44 defines it as *"The sample-to-condition mapping, already written to the
graph as a curation `Analysis`"*, consumed by the adapter *"never a configuration file"*.

**The decisive fact is what the adapter is already not allowed to do.** Measured: **no adapter mints
a `Sample` id**. The only `evidence_id("Sample", …)` call anywhere in `bzk/` is
`bzk/curation/loader.py` l.324, which supplies `{"Experiment": experiment_id}`. Adapters *emit*
`Sample` nodes — `bzk/adapters/base.py` l.69 builds them from the descriptors — but the ids come in
with the descriptors, already keyed.

**So the adapter has been kept out of identity work over experiment scope, deliberately and
completely, with exactly one exception: `Contrast`.** `perseus.py` l.226 is the only place an
adapter mints an id for a node type it does not receive pre-keyed — and it is the only one whose
identity spec has no anchor.

**Adding `experiment_id` to `SampleMapping` would not widen a mapping; it would grant the adapter a
capability the design has withheld from it everywhere else.** The cheaper reading — that an
`Experiment` id is just one more field beside two others — is available and is wrong, because the
two fields it would join are a *curation analysis id* and *pre-keyed descriptors*, neither of which
lets the adapter key anything.

**The alternative is already in ADR-0027's own list.** The loader reads `contrasts_of_interest` and
hands them on without materialising — `loader.py` l.357–359 — and it holds `experiment_id`. Once it
mints the `Contrast` nodes, the adapter receives contrast ids the way it receives sample ids, and
**the contract is unchanged rather than widened.**

## Q1 and Q2 got different answers, and what follows

**They did, and the difference is not a compromise.** The analysis layer legitimately mints ids and
is given the anchor to mint them with; the adapter layer does not mint ids anchored on `Experiment`
and is not given the means to start.

**A build that anchors one minting site and not the other is not coherent, and the reason is
mechanical.** `keys.py` l.334–341 renders the anchor for **every** `Contrast` mint the moment
`schema.py` carries it. So a build that threads the id into `site_change_set` and leaves
`perseus.py` alone produces two disjoint id spaces for the same contrast: the analysis path mints
`@Experiment=<real>` and the adapter mints `@Experiment=␀null`. **A `RESULT_IN_CONTRAST` edge from a
differential result would then point at a `Contrast` id no adapter ever emits.**

**So the three parts move together: implied change 4 first or alongside, then Q1's parameter, then
implied changes 1, 3 and 5.** ADR-0027 states no ordering among its six items, and this is the
second ordering constraint its list omits.

**Review finding A, 2026-09-03 — this sentence is local and does not govern.** Every numeral in it
is **ADR-0027's**, and all four collide with items this record's own list numbers 1, 3, 4 and 5,
where item 4 is a different thing. It also closes the Q1/Q2 section and so omits the fourth part
§Q3 adds — *"the three parts"* is not exhaustive. **The list at the end of this record governs.**

## Q3 — where the null-anchor check lives

**Decision: the check is needed, and its correct form is a generalisation of I21 rather than a new
invariant. That generalisation is a separate decision and is not made here.**

`keys.py` l.303–311 states the position exactly: *"Nothing here can refuse it: this function is
handed the anchors and resolves none… The obligation therefore sits at write time."* I21 is that
obligation discharged for one anchor — stated at `ONTOLOGY.md` l.966, implemented at
`bzk/ontology/invariants.py` l.588 as `_check_I21`, registered at l.710.

**`Contrast` needs the analogue, for the same reason and with the same shape**: an id that claims to
be a content digest must encode the anchor its edges name, or the anchor is decorative.

**Why a generalisation and not a new number.** I21's statement is
*"A correction's id names the baseline it was computed against"* — a claim about `ADJUSTED_BY`
semantics, not about anchors in general. A `Contrast` check would be the same structure with a
different node type, and adding one would start a per-node series where the general rule is
**every anchored node's id encodes its anchors**. Two node-specific invariants are the point at
which the general one should be written instead.

**The next free invariant number was verified rather than assumed**, in case a new one were the
answer: `ONTOLOGY.md`'s invariant list runs to **I21**, and `invariants.py` registers checks for
I2, I3, I4, I10, I14, I15, I16, I19, I20 and I21. **So a new invariant would be I22.** It is not
taken, because a new invariant is not the decision.

**Generalising I21 is an `ONTOLOGY.md` amendment to an `Accepted` invariant**, so it needs its own
record. **Named here with its ground rather than left implicit.**

## How many `Contrast` ids would change — measured

**Two, of the two the repository declares.** Measured un-populated, in memory, writing nothing: the
two entries of `curation_PXD018299.json`'s `contrasts_of_interest` keyed through
`keys.evidence_id` before and after substituting an anchored identity spec, with the spec restored
afterwards and the restoration asserted.

| Contrast | before | after, anchored |
|---|---|---|
| `KO_IFN_vs_WT_IFN` | `bzk:f7c41f45886d3cf7c5c5ce8d59b0e267` | `bzk:8f9a06344675831a26dd59b2bf8c4393` |
| `KO_vs_WT_unstimulated` | `bzk:852326f345b67bc266845f675d1d63da` | `bzk:d78903eeb3746b372e2100d3b6e52906` |

**It is measurable un-populated because ids are content-derived (ADR-0020)**: `evidence_id` is a
function of the props, the identity spec and the anchor ids, and consults nothing on disk.

**A third id set exists and is the one to avoid.** Under a null-anchor build the same two contrasts
mint `bzk:03ccd33e0d41b99f61407b9b30462df9` and `bzk:7fa11302cf15805ef6cd325546b6be38` — **distinct
from both the current ids and the anchored ones**. So a build that lands the anchor without the
threading does not leave ids where they are; it moves them to a third place that closes nothing.

**And the count of ids that change in any store is zero**, because no store exists: `graph.kuzu/`
is absent and the loader materialises no `Contrast`. **The figure above is a count over what the
committed record would mint, not over anything currently held.**

## The class

**This record closes no class.** It closes one instance: ADR-0027's implied change 3 had no
supplier for its anchor, and this supplies one.

**The class it belongs to — a record whose implied changes are described without their reachability
established — is real and is not machine-checkable.** Whether a described-but-unbuilt change can be
built is not expressible as an assertion over the tree; it is answered by reading the call sites,
which is what the determination at `ROADMAP.md` l.11189 did. ~~**So the class stays open, and it stays
open for a structural reason rather than for want of writing a guard.**~~ — **narrowed by Review
finding C, 2026-09-03: the class does stay open for a structural reason, but a guard over
`schema.IDENTITY`'s anchored labels and the 22 `evidence_id` **minting** call sites — 22 under the
exclusion the Review states, 24 without it — is writable and non-vacuous, and it would catch the
shape this instance took. It does not catch the class.**

## Implied changes, described and not made

1. **`site_change_set` gains a required keyword-only `experiment_id: str`**, and the four call sites
   supply it — `pxd018299_differential.py` l.322 from `curation.experiment_id`, and the three test
   callers each with a value of their own.
2. **`bzk/curation/loader.py` materialises `Contrast`** — ADR-0027's implied change 4, promoted here
   from a peer of implied change 3 to its prerequisite.
3. **The adapter receives contrast ids rather than minting them**, which removes `perseus.py` l.226
   as a minting site and leaves `SampleMapping`'s two fields untouched.
4. **A generalisation of I21 to every anchored node**, with its own record, before or with the
   anchor landing.
5. **Then ADR-0027's implied changes 1, 3 and 5.** Not before the four above.
