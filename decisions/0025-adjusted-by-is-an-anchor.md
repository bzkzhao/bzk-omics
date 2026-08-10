# ADR-0025 — `ADJUSTED_BY` is an anchor on `DifferentialResult`

| | |
|---|---|
| Status | Proposed |
| Date | 2026-08-10 |
| Supersedes | — |
| Superseded by | — |

## Context

`ONTOLOGY.md` §11 Q7 recorded a second cardinality defect alongside the XOR question that became
I20, and recorded it as **demonstrated rather than predicted** on 2026-08-07: for a
`protein_adjusted = 'applied'` result, `ADJUSTED_BY` names the protein-level result used as the
correction baseline, and that edge is absent from §3's anchor list. Two corrected results differing
*only* in which baseline they used therefore mint one id.

The demonstration was re-run against shipped code before this record was written, and it reproduces
digit for digit:

```
label=DifferentialResult
adjustment_method=residual_vs_protein_lfc
protein_adjusted=applied
@Analysis=bzk:an1
@Contrast=bzk:c1
@ProteinObservation= null
@SiteObservation=bzk:obs1
```

Both baselines mint `bzk:1529fff2e684983da8b8983e266cefb5`. The baseline appears nowhere in the
tuple, so the two are not merely hard to tell apart — they are the same node.

**It is reachable under a faithful implementation, not a contrived one.** At I14's measured 82%
multi-mapping, an honest correction of an ambiguous site is computed against *each* candidate
parent, and `ADJUSTED_BY` is `MANY_ONE`, so each correction needs its own `DifferentialResult`. What
would be lost is not a duplicate row; it is the ability to hold two corrections of one site at all.

## Decision

**`("DifferentialResult", "ADJUSTED_BY")` joins the anchor list for `DifferentialResult`** in §3's
identity table and in `schema.py`'s `IDENTITY`, in that order. Nothing else changes: no new
invariant, no DDL change, no multiplicity change.

## Consequences

**It is the first self-referential anchor in the identity table**, and that was checked rather than
assumed — no other `Identity` anchors on its own label. Three consequences follow, each probed
against the shipped validator before the amendment was written.

**1. The ordering obligation is on the producer, not on the change-set.** A baseline must be keyed
before the result that anchors on it. Structural validation is **order-blind** — the same batch
validates with the corrected result listed before its baseline and after it — so ADR-0019 gains no
new obligation. The producer's obligation is a topological order over a graph that `MANY_ONE` makes
a forest: each result has at most one baseline.

**2. A cycle becomes unkeyable, which is a strengthening rather than a hazard.** A two-cycle
(`R1 ADJUSTED_BY R2`, `R2 ADJUSTED_BY R1`) and a self-loop (`R ADJUSTED_BY R`) both **validate
today** and both still validate after this change; the amendment neither creates that hole nor
widens it. ~~What it adds is that `evidence_id` **cannot produce** either, because computing one id
needs the other's. A cycle therefore survives only where ids are hand-written, which is the fixture
route. **No acyclicity check is asserted anywhere**, before or after — stated because a reader
meeting the ordering obligation would reasonably look for one.~~

**Corrected 2026-08-10, before this record was Accepted.** *This edit is an ordinary one and not a
breach of the append-only rule.* `decisions/README.md` draws that line **by status rather than by
elapsed time** and says so in its own second sentence — *"Correcting a record during review is an
ordinary edit to a `Proposed` document — that is what the status is for"* — and this record is
`Proposed`. **That is the only reason it is an edit**: had this been `Accepted`, the correction
below would be ADR-0026 superseding this one, because a sentence inside the record that argued for
the amendment is exactly the kind of thing that must die visibly.

`evidence_id` **can** produce an id for a member of a cycle. It resolves nothing — `anchor_ids` is
an argument, and an absent anchor is permitted outright — so a caller who omits the self-anchor gets
a real id with `@DifferentialResult=␀null` in the tuple. What cannot be produced is the
**cyclically-determined** id, which is the *producer's* impossibility and is where consequence 1
already puts the ordering obligation.

**The wording mattered because it concealed a live hole, not because it was loose.** The same
omission that keys a cycle also **re-mints this ADR's own collision**: two corrections against
different baselines, both minted with a null self-anchor, are one node again —
`bzk:3473130e9cb7f1198196ee40b0e30727`, measured against shipped code. I4 accepts it (it reads the
edge, never the id), I20 is silent (it counts `RESULT_FOR_*`), and structural validation recomputes
no ids. So the amendment above closed the collision only for producers that choose to supply the
anchor it added.

**Closed by I21** (`ONTOLOGY.md` §8, 2026-08-10): a digest-shaped id carrying an `ADJUSTED_BY` edge
must encode that edge's target. **Acyclicity is subsumed by it** — a cycle needs `sha256` to
determine its own input, and a cycle assembled from ids minted against *third* baselines is refused
at both ends. A cycle among **hand-written** ids still validates, exactly as this consequence
originally said: I21 governs ids that claim to be digests, and the fixture route is untouched.

**3. `ADJUSTED_BY`'s `MANY_ONE` multiplicity is now load-bearing.** §3's rule is that an anchor must
be single-valued, and this anchor satisfies it only because §7 declares the relationship `MANY_ONE`
— confirmed by probe: a result naming two baselines is refused with
`STRUCTURE — ADJUSTED_BY is MANY_ONE`. Before this record that multiplicity was a modelling choice;
now widening it would remove this anchor by §3's own rule, exactly as that rule describes for
`RESOLVES_TO_PROTEIN` under ADR-0022. **Do not widen `ADJUSTED_BY` without reading this paragraph.**

**Every existing `DifferentialResult` id moved: 1,362 of 1,362.** An absent anchor still renders —
the `@ProteinObservation= null` line above is the evidence — so results that will never carry the
edge move too. Measured before deciding: **0** of the 1,362 carry an `ADJUSTED_BY` edge and all are
`not_applied`, so every one of them moved for a field none of them uses.

**§11 Q7 said the amendment was *free today and will not stay free*, and that stopped being true on
2026-08-09** when the differential writer landed the 1,362. It was done anyway, because the cost was
established rather than assumed: **nothing outside the graph cites a live `DifferentialResult` id.**
No test contains one, the valid fixture's are hand-written and recomputed by nothing, the only
complete id in the document set is the collision demonstration's, `bzk rebuild` drops all 1,362 and
`python -m bzk.sources.pxd018299_differential` regenerates them. That is why *ids move* is cheap
here and would not be for `ModificationSite`, whose keys are cited by position downstream — the
difference is what references them, not how many there are.

**The guard covers a case nothing produces, and that is stated so a pass cannot be misread.**
`perseus.py` records protein-grain results as uncorrected by construction, the 1,362 are all
`not_applied`, and no writer in this repository emits `applied` at all. `tests/test_keys.py`
exercises the separation with a constructed pair. A green test is evidence the key builder
distinguishes two baselines — not evidence that anything here produces two.

## Alternatives rejected

**Leave it and rely on `adjustment_method`.** It is already identifying and does not help: two
corrections against different parents share a method. The recorded tuple shows exactly this.

**Make `ADJUSTED_BY` `MANY_MANY` and carry the baselines as a list field** (the ADR-0022 shape,
where `candidate_proteins` replaced a single-`Protein` anchor). Rejected because the two cases are
opposites. ADR-0022 widened because a razor pick was being forced and the *group* was the observed
fact; here each correction genuinely has exactly one baseline, and a list would model a set that
does not exist. It would also lose the per-correction result the 82% argument needs.

**Defer again until `perseus.py` emits corrected results.** That is the circular shape ADR-0023
names, and §11 Q7 already refused it once: the writer chooses how many results to emit, so waiting
for it means asking the thing under test what the answer is. The deferral is also what turned a free
amendment into a 1,362-id one.
