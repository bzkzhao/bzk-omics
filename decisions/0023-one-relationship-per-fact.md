# ADR-0023 — One relationship per fact: `SITE_ON` narrows, two duplicate names are dropped

| | |
|---|---|
| Status | Accepted |
| Date | 2026-08-07 |
| Supersedes | — |
| Superseded by | — |

## Context

Three relationship-level defects in `ONTOLOGY.md`, all found while building
`bzk/adapters/maxquant_sites.py` — the first search-output adapter, and the first code that had to
*choose* which edge to emit rather than read a diagram.

**(1) `SITE_ON` was `MANY_MANY` against a key composing one parent.** §4 keys a `ModificationSite`
as `{ProteinSequence.id}#{residue}{position}#{modification_type}` — exactly one sequence — while
the DDL permitted attachment to several. §4 and §6.3 both recorded the mismatch as unresolved and
deferred it, twice, to "the first search-output adapter (weeks 5–6)".

**(2) and (3) Two pairs of relationships modelled one fact each.**

| | endpoints | multiplicity |
|---|---|---|
| `RESOLVES_TO_SITE` | `SiteObservation → ModificationSite` | `MANY_ONE` |
| `MEASURED_AT` | `SiteObservation → ModificationSite` | `MANY_ONE` |
| `REPORTS_SITE` | `Dataset → SiteObservation` | `ONE_MANY` |
| `REPORTED_BY` | `SiteObservation → Dataset` | `MANY_ONE` |

The first pair is identical in every respect. The second is the same fact read in both directions.
The document used them inconsistently, and that inconsistency is how the defect surfaced: §1's
diagram and §9's worked example draw `MEASURED_AT`, while §3's identity table anchored on
`RESOLVES_TO_SITE`. A query written from the diagram and a query written from the identity table
would traverse different edges over the same graph, and nothing kept them in step.

Enumerated across all 35 relationship tables, these are the **only** two instances of either shape.
A third pair shares endpoints but differs in multiplicity — `RESULT_FOR_SITE` (§5) and
`WAS_DERIVED_FROM` (§7) — and is deliberately excluded; see *Not decided here*.

## Decision

**1. `SITE_ON` narrows from `MANY_MANY` to `MANY_ONE`.**

**2. `MEASURED_AT` survives; `RESOLVES_TO_SITE` is dropped.**

**3. `REPORTS_SITE` survives; `REPORTED_BY` is dropped.**

Neither dropped name is retained as an alias. Both are removed from the DDL.

## The grounds for narrowing `SITE_ON`, in order

**(a) The key composes exactly one parent.** `keys.modification_site_key` takes one
`ProteinSequence.id` and embeds it. A second `SITE_ON` would attach a node *whose own id names
sequence A* to sequence B. This is a property of §4's key template, not of any adapter, and no
producer can emit around it.

**(b) The same peptide sits at a different position in each protein it maps to.** Measured on
`HAP1_USP18KO_GlyGlyKSites.txt` at `Localization prob ≥ 0.75`:

| | rows | |
|---|---|---|
| single-protein | 363 | |
| multi-protein | 1,693 | |
| — all candidates at the **same** position | 422 | 24.9% of multi |
| — positions **differ** | **1,271** | **75.1% of multi** |

Spread within one row reaches 14 distinct positions. Row 2 (HDLBP) lists
`A0A024R4E5;Q00341-2;Q00341;H0Y394;H7BZC3;H7C2D1` at `672;639;672;481;181;60`.
`ModificationSite.position` is a single `INT64`; for three-quarters of multi-mapping rows it cannot
be true of two parents at once. This is a property of the data.

**(c) A shared position number is not a shared position.** The remaining 24.9% do not rescue the
wider declaration: residue and position are meaningful only *relative to a sequence*. `P20591`
position 48 is `K`; `P09914-2` position 48 is `E`. Same integer, different residue, different
protein, different site.

Corroboration predating the adapter: `tests/fixtures/valid_changeset.json` has carried the note
*"not a second `SITE_ON` to a protein where position 48 is a different residue"* since before
ADR-0005, and (c) shows that sentence is literally true of the two accessions it names. The one
time this repository held two `SITE_ON`s from one site, it was a defect, fixed in `056c5d4`.

### What is *not* among the grounds

**The count "1,967 of 1,967 sites carry exactly one `SITE_ON`" is not evidence and was withdrawn.**

It was offered as the adapter's contribution to the deferred question. It is worthless for that
purpose: `maxquant_sites.py` emits one `SITE_ON` per site unconditionally, in a single line with no
branch, so the count is arithmetic on a constant. The measurement was reporting the adapter's own
design choice back as though it were a property of the data.

This is recorded rather than quietly replaced because the failure mode generalises and the
corrected conclusion alone would hide it. §6.3 deferred the question to "the first search-output
adapter" on the assumption that building one would *produce evidence*. It could not, and no adapter
could have: an adapter is the thing making the choice, so its output cannot arbitrate it. **Deferring
a modelling question to an implementation only works when the implementation is free to come out
either way.** Where it is not, the deferral has to name the measurement that would settle it — here,
the position spread across candidates, which is in the file and was answerable at any point.

`MANY_ONE`, not `ONE_ONE`: many sites on one sequence is the ordinary case and must stay many.

## Why these two names survive

**`MEASURED_AT` over `RESOLVES_TO_SITE`.** ADR-0022 broke the parallel the losing name asserts.
`RESOLVES_TO_PROTEIN` is now `MANY_MANY` and means *candidacy* — one of several proteins this might
be. This edge is `MANY_ONE` and means the opposite: the single thing the observation measured.
A shared `RESOLVES_TO_` prefix tells a reader they are the same kind of edge at two grains, and
since ADR-0022 they are not. `MEASURED_AT` says what the edge means, and §1 and §9 — the two places
a reader meets the model first — already used it.

**`REPORTS_SITE` over `REPORTED_BY`.** These are reverses, so the question is direction. The protein
grain had already answered it: `ProteinObservation` anchors on `REPORTS_PROTEIN`
(`Dataset → ProteinObservation`, `ONE_MANY`) with no reverse declared. Keeping `REPORTED_BY` would
have left the two grains anchoring **opposite directions of one fact**, which is the real
inconsistency here and worse than either name. Keeping `REPORTS_SITE` makes them one shape — this
follows an existing convention rather than inventing one. Separately, Cypher traversal is
bidirectional (`<-[:REPORTS_SITE]-`), so a reverse relationship buys no queryability in a graph
database; it is duplication with no upside.

**Dropped, not aliased.** An unpopulated relationship that means the same as a populated one is
worse than a removed name, because a removed name errors and an empty one lies: `MATCH
(d:Dataset)-[:REPORTS_SITE]->(o)` against a retained-but-unemitted `REPORTS_SITE` returns zero rows
and reads as "this dataset reported no sites". That is the runs-cleanly-and-is-wrong class this
repository exists to refuse. The dead names live here, which is where a reader of older prose
should look; ADRs are append-only, so this record does not decay.

**Renaming costs nothing in ids.** `keys.identity_tuple` folds `@AnchorType=<id>` and discards the
relationship name, so swapping both of `SiteObservation`'s anchors leaves every minted id
byte-identical. Verified by performing the swap and comparing, not by reading the function.

## Consequences

- `ONTOLOGY.md` v1.20: §3 identity anchors, §4 `SITE_ON` multiplicity and its prose, §5 DDL and
  contract table, §6.1 (loses the `MEASURED_AT` declaration, which moves to §5 beside the
  observation it attaches to), §6.3's two deferred paragraphs, I14. Schema goes 24 node + 35 rel =
  59 tables → 24 + 33 = **57**.
- **Two guards, added in the same commit as the change** (`tests/test_schema.py`): no two
  relationships may share endpoints *and* multiplicity, and none may be another's exact reverse.
  Both were unwritable before this ADR, because the DDL declared the violations. They pass
  immediately — which is the point: the class is closed by an assertion rather than by this turn
  having looked once.
- `SITE_ON` at `MANY_ONE` is now enforced by ADR-0019's structural multiplicity check, so a second
  parent is a write-time error rather than something merely unrepresentable in the id.
- ADR-0022's body refers to `RESOLVES_TO_SITE` in three places. ADRs are append-only and it is not
  edited; read those as `MEASURED_AT`.

## Not decided here

**`RESULT_FOR_SITE` (§5) vs `WAS_DERIVED_FROM` (§7)** — same endpoints, same meaning, surviving the
new guard only because their multiplicities differ. Excluded because the fix is not a rename: §7
opens *"Provenance is a PROV-O mapping, not a log"*, and a mapping materialised as a stored edge is
this defect one layer up. Whether §7 is stored or projected at export is wider than this ADR and is
recorded as `ONTOLOGY.md` §11 Q11, with *project, do not store* as the proposed resolution. Settle
with the first export path.
