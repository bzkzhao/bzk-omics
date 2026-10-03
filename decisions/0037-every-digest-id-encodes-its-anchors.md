# ADR-0037 — I21 generalised: a digest-shaped id encodes every anchor its change-set carries

| | |
|---|---|
| Status | Proposed |
| Date | 2026-10-03 |
| Supersedes | — (amends I21's statement, `ONTOLOGY.md` l.968; I21 keeps its number) |
| Superseded by | — |

Drafted against `f7f931c`. **Every number below was measured at `f7f931c` unless it is marked as a
prediction.**

## Context

**This is ADR-0029's implied change 4, and ADR-0029's correction to finding E puts it first.**

- ADR-0029 Q3 decided that `Contrast`'s anchor needs the null-anchor check I21 gives
  `ADJUSTED_BY`. It decided the check should be a generalisation of I21, not a new number.
- ADR-0029 left that generalisation to *"its own record, before or with the anchor landing"*.
- The correction to its finding E (2026-10-03) fixes the order that keeps the 1,362 results to one
  re-mint: this record first, then items 1–3, 5 and 6 as one build.
- ADR-0036 D4 makes that build a prerequisite of option 1's first IP contrast.

**Why I21 could not simply be widened before now.** `_check_I21` (`invariants.py` l.588) records
the measurement in its own docstring:

> *the general form — every digest-shaped id recomputes — … is refused by the real ingestion:
> 1,362 `SiteObservation`s and 36 `Sample`s are staged with no anchor edge in the change-set that
> stages them, because ADR-0019 permits a node to be re-staged as a referent.*

So the general form must keep I21's trigger, which is the presence of an anchor edge in the
change-set, not the presence of the node.

### The anchor inventory, measured

`schema.IDENTITY` and `schema.REL_TABLES` were enumerated at `f7f931c`.

- **24 labels carry an identity spec. 12 of them carry anchors, over 25 (label, anchor) pairs.**
  The 12-of-24 figure agrees with ADR-0029's finding C.
- **For 5 of the 25 pairs, the anchor is the edge's *source*, not the anchored node.** These are
  `HAS_SEQUENCE` (`Protein`→`ProteinSequence`), `CONTAINS` (`Project`→`Experiment`),
  `PERFORMED_ON` (`Experiment`→`Sample`), `REPORTS_SITE` (`Dataset`→`SiteObservation`) and
  `REPORTS_PROTEIN` (`Dataset`→`ProteinObservation`).
  - `_check_I21` reads each anchor as *"an edge whose source is the result"*, which is true of all
    five `DifferentialResult` anchors. A generalisation that kept that reading would count none of
    these five, and would never examine a `Sample` or an `Experiment`.
- **5 anchor rels declare no multiplicity:**
  - `USED` (`Analysis`→`Dataset`);
  - `ASSIGNMENT_SUPPORTED_BY` and `ASSIGNMENT_CITES`;
  - `ASSOCIATION_SUPPORTED_BY` and `ASSOCIATION_CITES`.

  §3 l.89 says *"An anchor must be single-valued, so widening a relationship removes it from
  identity"*. **Those five are anchors whose relationship is not declared single-valued.** That
  contradiction predates this record, and it is not repaired here (D4).
- **One label has identity children:** `Analysis`, from its `Imputation` through `IMPUTATION_FOR`.

## Decision

### D1. I21 is restated over every anchored label.

Proposed wording for `ONTOLOGY.md` l.968:

> **I21 — A digest-shaped id encodes the anchors its change-set carries.**
>
> - Applies wherever a change-set carries an anchor edge (§3) incident to a node of an anchored
>   label whose id claims to be a digest (`keys.is_digest_id`).
> - That node's id must equal `evidence_id` over three inputs: its identifying fields; the
>   counterpart of every anchor edge of its label in that change-set; and, for `Analysis`, its
>   identity children in that change-set.
> - The correction case is one instance: a `DifferentialResult` `ADJUSTED_BY` a baseline.

The number stays I21, on ADR-0029 Q3's ground: two node-specific invariants are where the general
one should be written instead.

**The existing clause's three stated limits all carry over unchanged:**

- hand-written ids are outside it;
- carrying one anchor edge obliges carrying the others;
- acyclicity is subsumed.

### D2. Edge-triggered, as I21 is.

A node staged with no anchor edge in its change-set is not examined. This is the ground the
docstring measured, kept and not re-argued: ADR-0019's re-staged referents.

### D3. Orientation is read from the declared pair, never assumed.

For each anchor `(A, R)` of label `L`:

- if `(L, A)` is one of `R`'s declared pairs, the anchored node is the edge's source;
- if `(A, L)` is one of them, it is the destination.

For a rel with several pairs (`PROTEIN_ASSIGNMENT_FOR`), the counterpart's label decides which
anchor the edge supplies. If that counterpart is not staged in the change-set, the node is refused
as unresolvable rather than guessed.

### D4. Two counterparts for one anchor in a change-set are refused.

An id renders one id per anchor label (`keys.identity_tuple`, l.334–341). So a node carrying two
distinct counterparts for one anchor cannot be keyed by any rule, and the check refuses it.

**Declaring the five rels `MANY_ONE` is not decided here, because one of them is about to be
tested by a real case.** ADR-0036's open question — how a concordance assignment cites the two
results it rests on — is likely to want an `Analysis` that `USED` two `Dataset`s. That question
and §3 l.89's contradiction should be settled together. This is recorded as `ONTOLOGY.md` §11 Q15.

### D5. What it does not catch, stated so a pass is not misread.

- **A node minted without its anchor whose edge is also omitted.** Nothing in the change-set names
  the anchor, so nothing can be recomputed. Closing that is a per-label *anchor presence* guard,
  which for `Contrast` is ADR-0027's implied change 5. It is not this invariant.
- **Hand-written ids**, which assert nothing, as before.
- **Cross-change-set consistency.** Each change-set is judged alone, per ADR-0019.

## Pre-registration — measured before enforcement, on real ingestion

**The rule is enforced only if real ingestion passes it.** A rule that refuses the shipped
ingestion is the general form the I21 docstring already rejected.

**The instrument is `walk/anchor_recompute_dryrun.py`.**

- It wraps `invariants.validate` report-only, so `store.write_change_set` validates exactly as
  before.
- It classifies every change-set under D1–D4. The outcomes are: `triggered`, `recompute_ok`,
  `null_door`, `mismatch`, `multi_valued_anchor` and `unresolved_counterpart`.
- `tests/test_anchor_recompute_dryrun.py` shows the instrument is not vacuous. A null-door
  `Sample`, a second `USED` edge and an anchor-less referent are each planted on the real
  PXD018299 record and counted as such.

**Measured in this container, curation layer only** (`curation` mode, four records, in memory):

| label | triggered | recompute_ok | any refusal |
|---|---|---|---|
| `Analysis` | 4 | 4 | 0 |
| `Experiment` | 4 | 4 | 0 |
| `Sample` | 54 | 54 | 0 |

**Predictions for `rebuild` and then `differential`, run on bzk's Mac.** They cannot run here: the
raw store and the UniProt cache are absent.

| # | Prediction | Direction wanted |
|---|---|---|
| P1 | `null_door` = 0, `mismatch` = 0 for every label | zero. Any non-zero means a producer mints an id that does not encode an edge it emits, a live defect of exactly the class this rule exists for |
| P2 | `multi_valued_anchor` = 0 | zero. Non-zero means D4 refuses real ingestion today, and Q15 must be settled before enforcement |
| P3 | `unresolved_counterpart` = 0 | zero. Non-zero means D3's refusal of an unstaged counterpart is too strict for real change-sets |
| P4 | `triggered` > 0 for `SiteObservation`, `ProteinObservation`, `ModifierAssignment`, `ProteinAssignment`, `DifferentialResult` and `Imputation` | non-zero. A zero here means the rule examines nothing for that label, and its pass is vacuous for it |

**Enforcement waits on P1–P3 holding.** If any fails, this record is revised before it is
accepted, not after.

## Pre-registration result — run on bzk's Mac at `856c3d1`, 2026-10-03

Two commands were run in order, `rebuild` then `differential`, with output pasted back verbatim.
The reviewer's reading follows.

**Rebuild context.**
- 4 curation records replayed and 3 deposits ingested.
- 4,195 site observations, 4,768 protein observations, 48 refusals.
- Exit **INCOMPLETE**: `Supplementary_Data_S1_TP.xlsx` has no adapter in the replay. That is
  known, and it is outside this record.

**Differential context.**
- 1,362 tested; 48.9% imputed; 516 significant up.
- 12 of 14 published targets recovered, with `OAS1` absent from the tested population. This is the
  shipped baseline.

### The instrument counts validations, not nodes. Corrected here, with no effect on P1–P3

The rebuild's adapter and curation change-sets are each validated twice:
- once by their producer: `maxquant_sites.py` l.408, `maxquant_protein_groups.py` l.442,
  `loader.py` l.411;
- once by `store.write_change_set` (`store.py` l.120).

The wrap sees both, which is why it printed *14* change-sets for 4 records and 3 deposits. The
differential's three change-sets are each validated once, so its counts are distinct as printed.
Zero doubled is zero, so P1–P3 read the same either way.

| label | rebuild, distinct (printed ÷ 2) | differential, distinct |
|---|---|---|
| `Analysis` | 7 triggered, 7 ok | 3 / 3 |
| `Experiment` | 4 / 4 | 1 / 1 |
| `Sample` | 90 staged, **54 triggered**, 54 ok | 24 staged, 12 triggered, 12 ok |
| `SiteObservation` | 4,195 / 4,195 | 3,391 staged, 2,029 triggered, 2,029 ok |
| `ProteinObservation` | 4,768 / 4,768 | — |
| `ModifierAssignment` | 4,195 / 4,195 | 3,391 / 3,391 |
| `DifferentialResult` | — | 1,362 / 1,362 |
| `Imputation` | — | 1 / 1 |

**36 `Sample`s staged without their anchor edge (90 − 54).** This is exactly the figure
`_check_I21`'s docstring gives for the re-staged referents that rejected the node-triggered form.
D2's ground is reproduced by an independent instrument. The differential's 1,362 re-staged
`SiteObservation`s (3,391 − 2,029) are the docstring's other figure, reproduced the same way.

### Verdicts

| # | Verdict | Evidence |
|---|---|---|
| P1 | **Holds** | `null_door` = 0 and `mismatch` = 0 for every label in both runs |
| P2 | **Holds** | `multi_valued_anchor` = 0. Q15 does not block enforcement |
| P3 | **Holds** | `unresolved_counterpart` = 0 |
| P4 | **Holds for 5 of 6. Fails for `ProteinAssignment`** | `SiteObservation`, `ProteinObservation`, `ModifierAssignment`, `DifferentialResult` and `Imputation` all trigger. `ProteinAssignment` does not appear at all, **because no producer in `bzk/` emits one**: `perseus.py` l.788 and `maxquant_sites.py` l.592 each say so, and a grep finds no mint. The prediction was wrong. For that label the rule is exercised only by constructed cases, as I21 has been for `ADJUSTED_BY` since it was written |

### Absences the run shows are designed, recorded so they are not mistaken for gaps

- **`ModifierAssignment`, all triggered nodes, lacking `Modifier`, `Analysis` and `Publication`.**
  These are the automatic `inferred_default` / `ambiguous` assignments (§6.1), which by
  construction name no single modifier, supporting analysis or citation.
  - They are D5's first limit at scale. For 4,195 nodes, three of four anchors are absent on
    purpose, and nothing in a change-set separates that from a producer that forgot them.
- **`DifferentialResult`, all 1,362, lacking `ProteinObservation` and `DifferentialResult`.**
  These are site-grain results (I20), all `not_applied` (I4).

### Not confirmed at the time of writing

The differential run rewrote `tests/fixtures/pxd018299_platform_targets.json`, as that command
always does. **Whether the rewrite produced a diff was not reported.** The fixture's own note says a
diff there is a finding, not a regeneration. This record's result does not depend on it, and it is
left open here rather than assumed clean.

## Review

**Reviewed 2026-10-03 at `856c3d1`, by the reviewer who drafted it, so this is not an independent
review.** Three findings, none a defect in the decision:

- **R1 — P4's `ProteinAssignment` prediction was wrong** (above). The rule stands. Implied
  change 4's tests carry a constructed `ProteinAssignment` case, because real ingestion will not
  exercise one.
- **R2 — the instrument's double count** (above). The instrument is not changed. Its
  docstring's word *"classifies every change-set"* is accurate, and the doubling is a fact about
  the callers.
- **R3 — enforcement cost.** The generalised check recomputes one digest per triggered node. In
  the rebuild that is 2 × 13,223 = 26,446 digests (the printed `triggered` column summed). `sha256` over a few hundred bytes makes this negligible
  next to the rebuild's measured 84–150 s warm. No ground to defer.

**Status stays `Proposed`. Acceptance is bzk's.**

## Consequences

- `_check_I21` is generalised in place, not replaced. Its two error readings — *no baseline at all*
  and *a different one* — become the general *no anchor* and *a different anchor*.
- I21 starts examining `Sample`, `Experiment`, `Analysis` and every other anchored label in
  real ingestion. P4 is the measurement that says how much.
- **No id moves.** This record changes a check, not an identity.

## Implied changes, described and not made

1. **`ONTOLOGY.md` l.968**: I21 restated per D1. The `ADJUSTED_BY` text becomes the worked
   instance, with its acyclicity and hand-written-id paragraphs kept.
2. **`ONTOLOGY.md` §11**: Q15 opened, per D4, cross-referenced to ADR-0036 *Consequences*.
3. **`bzk/ontology/invariants.py`**:
   - `_check_I21` generalised per D1–D4, with orientation read from `schema.REL_TABLES` pairs;
   - `_RESULT_ANCHORS` (l.585) and its docstring narrowed or removed.
4. **`tests/test_invariants.py`**: the existing I21 cases kept, plus one case per D3 orientation,
   one per D4 refusal and one for the `Analysis` child fold.
5. **Then ADR-0029 items 1–3, 5 and 6, as one build.**
