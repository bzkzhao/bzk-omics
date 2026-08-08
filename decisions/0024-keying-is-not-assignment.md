# ADR-0024 — Keying a site is not assigning a protein; `reviewed_preferred` leaves the basis enum

| | |
|---|---|
| Status | Accepted |
| Date | 2026-08-07 |
| Supersedes | — |
| Superseded by | — |

## Context

Implementing I17 (`bzk/adapters/maxquant_sites.py`, 2026-08-07) produced a conflict the documents
cannot both satisfy:

- **§6.3** lists `reviewed_preferred` in the `ProteinAssignment.basis` enum with permitted
  confidence **`probable`**.
- **I14** requires **`confirmed`** before a `ProteinAssignment` may reach `ASSIGNS_PROTEIN` from a
  multi-candidate set.
- Promotion is **always** multi-candidate: it happens precisely when the group holds both an
  unreviewed pick and a reviewed alternative.

So the schema can record that a promotion occurred and can never state its conclusion. The adapter
shipped an assignment with no `ASSIGNS_PROTEIN` edge, which satisfies both rules and satisfies
neither's intent.

**The conflict is a symptom; the cause is a category error.** A reviewed entry is better
*annotated*, not better *evidenced*. Swiss-Prot curation says nothing about which protein a shared
tryptic peptide actually came from — it says a human has reviewed the entry. So
`reviewed_preferred` cannot be a basis for an *evidential* claim, and raising its permitted
confidence to `confirmed` would buy the edge by over-claiming, which is what I14 exists to prevent.

What promotion actually decides is **which `ProteinSequence` the `ModificationSite` keys against**.
That is a different question from *which protein did this peptide come from*, and it is not an
inference at all: ADR-0023 narrowed `SITE_ON` to `MANY_ONE` because a `ModificationSite` key embeds
exactly one sequence and the position differs per protein. **A site must key against one sequence.
The choice is forced by the schema, and a forced choice is not a claim about the world.**

Three further defects sit in the same paragraph and are settled here rather than separately.

**(1) §6.3 says "the reviewed Swiss-Prot entry", singular. The data has several.** ADAR's candidate
group holds five reviewed accessions — `P55265` and four of its isoforms. OAS1's holds two distinct
*canonical* reviewed proteins, `F8VXY3` and `P00973`.

**(2) The tie-break was a decision made in code.** The adapter prefers a canonical accession over
an isoform and declines to promote where more than one distinct canonical reviewed protein remains.
That rule determined OAS1's outcome and existed only in a docstring and a report.

**(3) Promotion ignored whether it preserved validity.** TAP1's unreviewed razor pick
`A0A140T9T7` (808 aa) has K at 449 and 458; the reviewed `Q03518` it was promoted to is 748 aa today
with L and V there. Promotion moved a validated site onto a sequence that no longer matches, and
the residue check then refused it — turning a recovered published target into two refused rows.
Measured across the deposit: of 526 promotions, 522 validate, **4 fail where the original would
have validated**, and 0 fail both ways.

## Decision

**1. `reviewed_preferred` is removed from the `ProteinAssignment.basis` enum.** Promotion emits no
`ProteinAssignment`. With it gone the I14 conflict does not arise, because there is no longer an
assignment whose conclusion needs stating.

**2. The keying choice is recorded on the `SiteObservation`, in two columns.** I17's *"never
silently"* is the binding half of that invariant and survives this ADR intact; what changes is
where the record lives, not whether one exists. **Trading an over-claim for a silence would be a
worse outcome than the conflict.**

```cypher
keying_basis STRING,        -- 'razor' | 'reviewed_preferred'. Which rule chose the
                            -- ProteinSequence this site keys against (§6.3, ADR-0024).
                            -- Always set: 'razor' is the search engine's own pick.
displaced_protein STRING,   -- CURIE of the accession the search picked, where the
                            -- platform keyed against a different one. NULL when
                            -- keying_basis = 'razor', because nothing was displaced.
```

Both are **excluded from identity** (§3). They must be: the `ModificationSite` anchor already
encodes which sequence was chosen, so the observation's id differs between a promoted and an
unpromoted keying without their help. Including them would add nothing and would make the id a
function of a field that merely explains it.

Together they answer the question I17 asks — *this site keys against `P55265` rather than the razor
pick `H0YCK3`, because the razor pick is not a live reviewed entry* — without asserting that the
peptide came from `P55265`, which nobody knows.

**3. Validity is a precondition of promotion, not a consideration within it.** I2 makes a site keyed
at a non-matching residue meaningless; preference between accessions is a tiebreak among *valid*
options and cannot license an invalid one. So promotion applies only where the promoted entry's
residue at its own aligned position matches what the search reported. Where it does not, the
original keying stands and the reason is recorded. The current implementation applies the
preference first and lets I2 refuse afterwards, which has the two rules in the wrong order.

**4. The tie-break is normative, not an implementation detail.** Where several reviewed candidates
exist: prefer a **canonical** accession over an isoform; if more than one *distinct canonical
reviewed protein* remains, **do not promote**. Choosing between two genuinely different reviewed
proteins is a claim about peptide origin — the search engine's job, and exactly what I14 forbids
resolution from asserting. OAS1 is the case: `F8VXY3` and `P00973` are both canonical and both
reviewed, so its keying is left with the search engine's pick.

**5. I17 is reworded.** Its last sentence read *"The promotion is an inference and is recorded as
one."* That is the claim this ADR rejects. It becomes a keying rule with a recorded basis.

## Consequences

- `ONTOLOGY.md`: §5 gains the two columns; §3 lists both as excluded; §6.3 loses the
  `reviewed_preferred` row from the basis enum and gains the keying rules; I17 is reworded.
- `schema.py` gains `KEYING_BASIS`, guarded against §6.3 by `tests/test_schema.py` — the same
  mirror-plus-guard as `CURATION_BASIS` against §5.3.
- The adapter stops emitting `ProteinAssignment` for promotions. The 522 currently in the graph
  disappear on the next rebuild; nothing else references them.
- **`ProteinAssignment` becomes unpopulated by any adapter.** That is honest rather than a
  regression — the node type exists for genuine origin inferences (`unique_peptide`,
  `orthogonal_evidence`), and none is available from a MaxQuant site table.

## Not decided here

**The `Majority protein IDs` narrowing** (`HANDOFF.md` §8) is a separate question and this ADR does
not close it. §6.3's shape is a candidate set plus a concluded protein, and *"weighed six, kept
three, concluded none"* is still unrepresentable. That case is a genuine narrowing of an
**inference**; this one was never an inference, which is why removing it does not help there.

## Alternatives considered

**(a) Raise `reviewed_preferred` to permit `confirmed`.** Rejected: buys the edge by over-claiming.
Curation status is not evidence of peptide origin, and I14 exists to stop exactly this trade.

**(b) Exempt `reviewed_preferred` from I14.** Rejected for the same reason in a different form —
the exemption would have to be justified by the same false premise.

**(c) Make `ASSIGNS_PROTEIN` optional and let `candidate_proteins` mean *kept*.** Not rejected, but
not the fix here: it is the right shape for the `Majority protein IDs` narrowing and would still be
needed after this ADR. Applying it to promotion would preserve the category error while making it
representable.
