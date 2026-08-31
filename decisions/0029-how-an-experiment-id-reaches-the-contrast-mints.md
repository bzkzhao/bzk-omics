# ADR-0029 — How an `Experiment` id reaches the two `Contrast` mints, and why the two answers differ

| | |
|---|---|
| Status | Proposed |
| Date | 2026-08-31 |
| Supersedes | — |
| Superseded by | — |

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

**(b) is rejected on category, not on cost.** `DeclaredRun` holds the declaration of statistical
intent — `quantity`, `test`, `fdr_method`, `localization_threshold`, `filters_applied`,
`imputation`, `numerator`, `denominator`, `parameters_json`. **An `Experiment` id is a graph
reference, not a parameter of a test**, and the fact that it would cost the three callers nothing is
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

**(a) is chosen because it is the only option where forgetting is a `TypeError`.** Costing the three
test callers a line each is the point of it, not a price paid for it.

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
which is what the determination at `ROADMAP.md` l.11189 did. **So the class stays open, and it stays
open for a structural reason rather than for want of writing a guard.**

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
