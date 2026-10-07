# ADR-0039 — The shape guard admits pinned exceptions: ADR-0038 D4's two arm edges stand

| | |
|---|---|
| Status | Proposed |
| Date | 2026-10-07 |
| Supersedes | — |
| Superseded by | — |

**It supersedes nothing.** It amends the scope of a guard ADR-0023 wrote under *Consequences*, not
any of ADR-0023's three numbered decisions, and it leaves ADR-0038 D4 as accepted. The same shape
ADR-0038 took to ADR-0036: an amendment to a mechanism is not a supersession.

## Context

ADR-0038 D4 declares two relationships, both `Contrast → Sample`, `MANY_MANY`, non-identifying,
written only by the loader: `NUMERATOR_SAMPLE` and `DENOMINATOR_SAMPLE`. It cites ADR-0023 for the
rule it is following — one relationship per fact, two facts therefore two types — and does not
check the guard ADR-0023 wrote to enforce that rule.

**The conflict, measured.** With exactly those two DDL lines added after `ONTOLOGY.md` §5 l.521 in
a scratch clone at `a83a3f7`, `pytest tests/test_schema.py` gives **2 failed, 18 passed**. The
failures are `test_no_two_relationships_share_endpoints_and_multiplicity` (l.81–98), which is this
record's subject, and the §5↔`schema.py` mirror test, which is expected because `schema.py` was not
edited in that clone and is not evidence of anything here.

**The guard is a proxy, and it mis-fires in both directions.** It groups the parsed DDL by
`(endpoints, multiplicity)` and refuses any shape carried by more than one name. ADR-0023's
*Context* states the inference it is standing in for: the two pairs it found were *one fact under
two names*. D4's two edges are the opposite case — two facts that happen to share one shape — and
the proxy cannot tell them apart, because shape is all it sees.

That the proxy is inexact is not a new observation. **ADR-0023 records its under-inclusion itself**,
in *Not decided here*: `RESULT_FOR_SITE` (§5) and `WAS_DERIVED_FROM` (§7) have the same endpoints
and, in ADR-0023's own words, the same meaning, and survive the guard **only because their
multiplicities differ**. A known one-fact-two-names pair passes today. So the guard has never been
a decision procedure for the rule; it is a cheap net that catches the instances ADR-0023 enumerated,
and it was already accepted as letting one through unannounced.

**Neither the build nor a test edit can resolve this.** ADR-0023 and ADR-0038 are both `Accepted`,
and `decisions/README.md` l.7 makes an Accepted record append-only: a changed decision gets a new
record. Editing the guard without a record would leave the amendment's only justification in a test
docstring, which is the shape `CLAUDE.md` point 3 names — a class closed by prose a reader must
remember rather than by something checkable.

**ADR-0038's drafting defect.** *Implied changes* l.504–505 says `tests/test_schema.py` "moves with
§5". It does not: the guard refuses the DDL outright, and the landing verification never ran it.
Recorded here so a reader of ADR-0038 reaches the correction, per the same convention ADR-0023 used
for ADR-0022's three stale references.

## Decision

**1. The shape guard refuses a same-shape pair unless that pair is pinned as an exception, with the
record that decided the two names are distinct facts.**

**2. `NUMERATOR_SAMPLE` / `DENOMINATOR_SAMPLE` is the one entry, citing ADR-0038 D4.** ADR-0038
D4 stands unamended.

**3. The pin keys on the exact pair *and* its endpoints *and* its multiplicity.** A pinned pair
whose DDL later changes shape stops matching the pin and fails. Any other same-shape pair fails,
including a third `Contrast → Sample, MANY_MANY` edge arriving beside the two pinned ones.

**4. The reverse-relationship guard (`tests/test_schema.py` l.101–125) is untouched.** D4's edges
are not reverses of each other; nothing about this record bears on it.

## The grounds

**(a) Narrowing this guard changes no decision.** ADR-0023's *Decision* section has three numbered
items: `SITE_ON` narrows to `MANY_ONE`; `MEASURED_AT` survives and `RESOLVES_TO_SITE` is dropped;
`REPORTS_SITE` survives and `REPORTED_BY` is dropped. All three stand untouched. The shape guard
appears under *Consequences*, as one of two assertions added in the same commit to close the class
the three items emptied. Amending the reach of a consequence is consistent with `Supersedes —`.

**(b) The rule survives the amendment; only the proxy moves.** One relationship per fact is
untouched — ADR-0038 D4 obeys it, and says so. What changes is that a pair claiming to be two facts
must now name the record that decided it, instead of being refused for a resemblance.

**(c) The pin is a documented exception where the status quo is a silent one.** The guard already
passes a pair ADR-0023 itself calls one fact. After this record, the one same-shape pair in the DDL
carries a citation to the record that adjudicated it, and the untreated case stays exactly as
ADR-0023 left it (below). That is a net gain in what the suite can tell a reader, not a loss.

### The objection this has to answer

ADR-0023's *Consequences* say of both guards: *they pass immediately — which is the point: the
class is closed by an assertion rather than by this turn having looked once.* A pinned exception
reopens that class by exactly one entry, and the obvious failure mode is a pin list that grows
whenever the guard is inconvenient.

Three things hold it closed:

- **The pin is a whitelist of one, keyed on a triple.** Nothing generalises from it. A second
  same-shape pair fails loudly, and so does a pinned pair whose shape drifts.
- **The precedent is in this repository and has held.** `ONE_SIDED_SUPERSESSION` in
  `tests/test_decision_index.py` (l.73–82) pins exactly one pair, `("0017", "0014")`, with the
  reason it is permitted, and every other one-sided supersession still fails.
- **Entry requires a record, not a judgement.** A pin cites the ADR that decided the two names are
  distinct facts. Adding one without writing that record is itself the thing the guard now refuses.

### What is not among the grounds

**"The test is wrong" is not a ground, and was not available.** The guard does what ADR-0023 says
it does. Had the two DDL lines been added and the guard edited in the same prompt — which is what
ADR-0038 l.504–505 anticipated — the suite would have gone green and nothing would have recorded
that ADR-0023's assertion had been narrowed. The failure is the mechanism working.

**The count "2 failed, 18 passed" is not evidence for the decision.** It establishes that the
conflict is real and was not resolved by the acceptance of ADR-0038. It says nothing about which
option is right; (a) and (b) both make it green.

## Option (b), not chosen

ADR-0039 could instead amend ADR-0038 D4 to one edge, `ARM_SAMPLE`, carrying a `side` property.
The guard would be untouched and no exception machinery would exist.

Rejected on D4's own stated ground, which this record does not reopen: every reader must then filter
on `side`, and a reader who forgets silently merges the two arms. That is the conflation one
relationship per fact exists to prevent, so (b) satisfies the proxy by breaking the rule it proxies
for. It also reverses a decision accepted the same day, on no new evidence.

## Consequences

- **The guard's edit does not land here.** It lands in prompt 29, in the same commit as the DDL it
  permits, so the exception and the pair it admits arrive together and neither exists alone. This
  record only decides it.
- **This record's own landing moves three pins**, in the commit that adds the file:
  - `tests/test_decision_index.py` `EXPECTED_FILES` 37 → **38**;
  - `EXPECTED_WRITTEN_ROWS` 37 → **38**, with the matching row added to `decisions/README.md`'s
    **Written** table;
  - `EXPECTED_STATUSES` `Proposed` 9 → **10** while this record is `Proposed`, and on acceptance
    `Accepted` 25 → 26 with `Proposed` back to 9.
- **`ARCHITECTURE.md` §5 does not move.** Its seed list stops at `0018` and reserves no number for
  this record, so there is no strike to make and `test_a_queued_number_is_not_also_written` is
  unaffected.
- `ONTOLOGY.md` is not amended by this record. Its §5 DDL gains the two edges in prompt 29 under
  ADR-0038 D4, which is where that change was always going to live.
- A reader of ADR-0038 *Implied changes* l.504–505 should read "moves with §5" as corrected here.

## Not decided here

**`RESULT_FOR_SITE` (§5) vs `WAS_DERIVED_FROM` (§7)** stays exactly as ADR-0023 left it: excluded,
surviving on a multiplicity difference, recorded as `ONTOLOGY.md` §11 Q11 with *project, do not
store* proposed, and settled with the first export path. This record cites that pair as evidence
that the guard is inexact; it does not resolve it, and the pin introduced here is not a route to
resolving it — a pin asserts two facts, and Q11's question is whether there is one.

**Whether I22 and D2/D3 belong at invariant level** is the build plan's P1 and handoff 10-05 §7,
not this record.

**Whether any second pair should ever be pinned.** No second entry is contemplated. If one is
proposed, it needs its own record, and that record should say why the pair is two facts before it
says anything about the guard.
