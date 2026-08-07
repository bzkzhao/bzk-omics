# ADR-0019 — Change-sets are self-contained; structural validation precedes invariants

| | |
|---|---|
| Status | Accepted |
| Date | 2026-08-07 |
| Supersedes | — |
| Superseded by | — |

## Context

Write-time invariant checks (`bzk/ontology/invariants.py`) run over a *change-set* — a batch of
node and edge dicts staged for a write. An audit found four of the eight checks passing vacuously:
I2, I3, I10 and I14 look up a node by an edge endpoint and guard with `if referent is not None`, so
when the referent is absent from the batch the check enforces nothing and reports nothing. Because a
change-set is a batch, an adapter that stages proteins in one batch and sites in another would get a
clean I2 on the site batch — the invariant silent precisely where it matters.

Three further structural assumptions were unstated and unchecked, so a malformed change-set could
reach a check and be read as valid:

- an edge endpoint's node label was never verified against what the schema declares for that
  relationship — `_check_I2` read `sequence_version` off whatever sat at `edge["to"]`, and
  `_check_I15` inferred "produced differential results" from the edge type alone, sound only because
  the DDL restricts `WAS_GENERATED_BY`, which the validator never consulted;
- an edge type outside the DDL was silently ignored;
- the node index dropped nodes lacking an `id` and let a duplicate `id` last-win.

The question is what a dangling or malformed reference *means*. Three options.

## Decision

**(a) A change-set must be self-contained. A dangling or malformed reference is an
`InvariantError`.** Structural validation runs first and unconditionally, before any invariant
check, and enforces four things, with expectations derived from `schema.py` (never restated, so this
stays a mirror of ONTOLOGY.md §4-7):

1. **Referent presence.** Every node an edge names by `from`/`to` is present in the change-set.
2. **Endpoint labels.** Each endpoint carries the node label the schema declares as that
   relationship's source/target.
3. **Known relationships.** Every edge `type` is a `REL TABLE` in the DDL.
4. **Node identity.** Every node has an `id`; ids are unique within the change-set.

Attribution: a failure of (1) or (2) on a relationship a specific invariant consults
(`SITE_ON`→I2, `ASSIGNS`→I3, `ASSOCIATION_FOR`→I10, `ASSIGNS_PROTEIN`→I14) raises **that
invariant**, so the error names the relationship at fault. Every other structural failure raises
**`STRUCTURE`**.

## Consequences

**Positive.** The four vacuous checks now enforce. The label check makes the invariant checks sound
rather than accidentally sound: a check that reads a field off an endpoint is now guaranteed the
endpoint is the type it assumes. Deriving expectations from `schema.py` means a schema change
propagates to the validator with no second edit, preserving the mirror the consistency test
(`test_schema.py`) already guards.

**Negative.** Adapters must stage a coherent unit: a `SiteObservation` with its resolved `Protein`
(I2) and its mandatory `ModifierAssignment` (§6.1) in the same change-set. A referent already in the
graph must be re-staged into any change-set that references it. This is redundant but cheap and
safe, because reference keys are content-derived (I7), so re-staging is idempotent — the cost of
keeping the validator pure.

**Fifth hole (multiplicity), added 2026-08-07.** The `RelTable.multiplicity` in `schema.py` — the
same source as the endpoints — was initially unchecked, so two `MEASURED_AT` edges from one
`SiteObservation` (declared `MANY_ONE`) passed. Structural validation now also enforces
multiplicity within the change-set: for `MANY_ONE` a source id appears at most once for that
relationship, for `ONE_MANY` a destination id at most once, for `ONE_ONE` both. Failures raise
`STRUCTURE`. This is change-set-scoped — Kùzu enforces the same bound at write time across
change-sets — but catches the malformed batch before it reaches the store.

**Sixth hole (node type declared at all), added 2026-08-07.** Point 4 above required every node to
have a unique `id` but never that it declare a node type — a type was checked only where an *edge*
pointed at the node, so a change-set of nodes no edge referenced validated clean whatever they
claimed to be, or claimed nothing. Structural validation now also requires each node's
`__label__` to be a node table in the DDL. Found while checking the rename below for silent-failure
modes: it has exactly one, a producer still emitting the old key, and that produces nodes with no
type — which was the case that passed.

**Discriminator key renamed to `__label__`, 2026-08-07.** This ADR governs the change-set format,
and the format named its node-type discriminator `label`. `label` is *also* a real `STRING` column
on six node tables — `Sample`, `Dataset`, `Analysis`, `Contrast`, `Disease`, `Drug` — so
`{"label": <node type>, "id", **columns}` could never carry those six columns: writing one
overwrote the node type. Six real columns were unreachable through the only documented ingestion
path.

Nothing had hit it. The nodes in `tests/fixtures/valid_changeset.json` that own a `label` column
never set one, so the format's own fixture passed while a whole column was unwritable. The curation
loader was the first writer to meet it, and its first draft declined to emit the column, which
kept the change-set well-formed and left the defect in place — a workaround, not a fix.

The key is now **`__label__`**. Every column in ONTOLOGY.md §4-§7 matches `[a-z][a-z0-9_]*` — a
convention `tests/test_schema.py` already relies on when it parses §3 — so a dunder key cannot
collide with a column now or later, which a bare rename to `_label` or `node_type` would only make
unlikely. It is read from `invariants.NODE_TYPE_KEY` rather than written as a literal, so a further
change is one edit. `id` is left alone: no node table has a column called `id` other than the
primary key it already is.

Timing was the whole argument for doing it now. There are no adapters and no graph content, so this
was a mechanical rename across two modules (`invariants.py`, `curation/loader.py`), one fixture
and three test files, plus a clarifying comment in two more; after `perseus.py` it would have been
a migration.

Two things deliberately did **not** follow the rename. The identity tuple in
`bzk/ontology/keys.py` still opens `label={type}`: those bytes are hash input, so renaming the
prefix would re-mint every evidence id in the graph, and no collision exists there — a node's
columns never enter the tuple except through `spec.fields`, and `label` is excluded from identity
(§3) on all six. And the **edge** keys `type` / `from` / `to` are unchanged: the same argument
applies in principle, since an edge dict carries relationship properties alongside them, but the
DDL declares only two rel properties in total (`source`, `evidence_code`) and neither collides.
That is a latent risk recorded in `HANDOFF.md` §8, not a second rename — the node case was a live
defect with six instances, this one has none.

**Reserved namespace — an invariant of the format, added 2026-08-07.** The rename above fixed one
collision. This is the rule it is an instance of, stated so the next one fails at the test suite
rather than at whichever writer first wants the field.

A change-set dict mixes two kinds of key, and the difference is what the `label` collision came
down to:

- **Reserved keys** carry information the DDL does not store under that name — a node's type is the
  *table* it lives in, an edge's type is the *relationship*. Nodes: `__label__`. Edges: `type`,
  `from`, `to`.
- **Column-backed keys** name a real column and mean exactly it. `id` is the only one.

The rule, in both directions:

5. **Reserved keys may not name a column or property.** No reserved node key may be a column on any
   node table; no reserved edge key may be a property on any rel table. A collision makes that
   column unwritable through the ingestion contract, silently — `{**columns}` overwrites the
   structural key.
6. **Column-backed keys must name a column, on every table.** `id` must be a column of every node
   table and its primary key, or structural validation reads a field the store does not have.
7. **A reserved key must be *unable* to become a column, not merely happen not to be one.** Every
   column in ONTOLOGY.md §4-§7 matches `[a-z][a-z0-9_]*`, so a reserved key must fall outside that
   shape. This is the difference between `__label__` and `node_type`: the second is a fix that
   works until someone adds the column.

Guarded by `tests/test_invariants.py`, one test per direction, derived from `schema.py` so the
check follows the DDL rather than restating it. Rule 5 currently has nothing to catch on the edge
side — the DDL declares two rel properties in total, `source` and `evidence_code`, and neither
collides — which is exactly why it is a guard and not a note: it passes today and fires the day a
relationship gains a property called `type`, `from` or `to`, without anyone remembering to look.
That automatic trigger is what makes leaving the edge keys un-renamed a decision rather than a
deferral.

Why this is written as a format invariant and not as a fifth structural check: it is a property of
the *schema against the format*, fixed at author time, not of any particular change-set. Putting it
in `_validate_structure` would re-derive a static fact on every write and, worse, report it only
once data flowed through the collision — which is how `label` survived this ADR and its first two
addenda in the first place.

**A node is identified by (label, id), not by id alone — corrected 2026-08-07.** Point 4 above said
"every node has a unique id", and the implementation read that as unique across the whole
change-set. That is wrong, and real data proved it on the first run that seeded `Modifier` nodes
alongside `Protein`s: **§3 keys both on `uniprot:`**, so ISG15 is `uniprot:P05161` under both
labels — the protein a diGly search reports as a razor pick, *and* the modifier the K-GG remnant
might have come from. Kùzu stores the two in separate tables and is untroubled; it was this format
that was too narrow, and the collision is the project's anchor domain rather than an edge case.

Three consequences, all in `_validate_structure` and its callers:

1. Uniqueness is per `(label, id)`. Two labels sharing an id is legal.
2. An edge names endpoints by **bare id**, so where two labels share one the reference is ambiguous
   in isolation. It is disambiguated by the *relationship*, which declares its endpoint types:
   `HAS_SEQUENCE(FROM Protein TO ProteinSequence)` reaching `uniprot:P05161` can only mean the
   `Protein`. So an endpoint is well-formed when **some** node with that id carries a declared
   label, rather than when **the** node with that id does.
3. Any producer collapsing duplicates by id must key the same way, or it silently drops one of the
   two nodes — which is precisely what happened before the check caught it.

What this does **not** do is give edges a way to name a label explicitly. Under the current schema
they never need one: no relationship declares an endpoint pair that both readings of a shared id
would satisfy. That is a property of today's DDL rather than a guarantee of the format, and it is
recorded in `HANDOFF.md` §8 with the guard that would detect the day it stops being true.

**Note.** This is the shape of the ingestion contract for the adapters (weeks 3-6): batch by a
complete fact, not by node type.

## Alternatives considered

**(b) Resolve missing referents against the graph before checking.** Rejected: it threads a live
Kùzu handle into every checker, breaking the one architectural bet this module makes — that
invariants are a pure function over a change-set, independent of storage and unit-testable without a
graph (ONTOLOGY.md §10). It also invites a check-then-write race.

**(c) Record missing referents as unchecked and re-verify at a whole-graph level.** Rejected: it
demotes a write-time guarantee to a deferred warning, re-checked by a whole-graph pass that does not
exist, and "errors, not warnings" (CLAUDE.md) is the discipline that makes the design worth having.
A rule enforced later is a rule that fails to fire under deadline.
