# ADR-0005 — Sequence version and isoform as part of the ModificationSite and Protein keys

| | |
|---|---|
| Status | Accepted |
| Date | 2026-08-07 |
| Supersedes | — |
| Superseded by | — |

Written ahead of 0004 and 0006–0014. The numbering reserves identity, not chronology
(`decisions/README.md`), and this decision is upstream of the resolver, every observation, and the
key builder, so it could not wait for its turn.

## Context

`ONTOLOGY.md` §4 argued once, correctly, that **position numbering is only meaningful relative to a
specific sequence**: `P05161#sv1#K42` and `P05161#sv2#K42` may be different lysines because the
sequence was amended, and `P09914#K376` and `P09914-2#K376` are different lysines because the
isoforms differ in length. Measured on PXD018299: `P09914-2` position 376 returns threonine against
the canonical IFIT1 sequence and lysine against isoform 2.

That argument was applied to the `ModificationSite` key and not to the `Protein` whose sequence it
is. Three gaps followed, none of them decided:

1. **`sequence_version` was absent from the `Protein` key.** `Protein.id` was `uniprot:ACCESSION`
   alone, with `sequence_version` a mutable column.
2. **`isoform` was a column** — `-- e.g. 'P05161-1'; NULL means canonical` — in the same section
   whose prose states that a schema treating isoform as a property rather than part of the key
   "would silently merge these with their canonical counterparts and place modifications on the
   wrong residues". The DDL said what the prose forbade; under the DDL's reading, `uniprot:P09914`
   with `isoform='P09914-2'` merges both isoforms into one node.
3. **The key template wrote `[-{isoform}]`**, which only composes if `isoform` holds `'2'`. Three
   readings of one field. Practice (the fixture, the resolver's cache path
   `seq/{accession}#sv{n}.txt`, "full accession, never collapsed to canonical") followed a fourth.

## Decision

**(A) The full UniProt accession, including any isoform suffix, is the identifier.** `P09914-2` *is*
an accession, not a canonical accession plus a property. The `isoform` column is dropped; it is
`'-' in accession`. This makes the DDL agree with §4's prose, with the resolver, and with UniProt.

**(B) `Protein` and `ProteinSequence` are separate nodes.**

```
Protein          uniprot:{accession}                       stable identity; no sequence
ProteinSequence  uniprot:{accession}#sv{sequence_version}  carries sequence_version + sequence
```

`SITE_ON` targets a `ProteinSequence`. Everything whose meaning is version-independent —
`ENCODES`, `ANNOTATED_IN`, `ASSOCIATION_ENZYME`, `ASSIGNS_PROTEIN`, `RESOLVES_TO_PROTEIN` — targets
the stable `Protein`. `RESOLVES_TO_PROTEIN` in particular: a `ProteinObservation` quantifies a gene
product, carries no residue positions, and its `Dataset` anchor already records which search
produced it, so putting `sv` into observation identity would buy nothing.

I2 is reworded accordingly: the sequence-version claim moves to `ProteinSequence`, and a new clause
requires the version embedded in a site key to equal its `SITE_ON` target's `sequence_version`.

## The argument, honestly

**This is not a near-term need, and the case should not be made as one.** The resolver pins to the
*current* sequence version at resolution time, so two datasets ingested in the same week resolve
identically no matter which FASTA release they were originally searched against. Two versions of one
protein in one graph require an amendment to land *between* two ingestions.

The argument is **accumulation**, and the inability to represent the case once it arrives:

- Sequence amendment is ongoing, not historical. Measured on PXD018299: 1 of 20 sampled sequences
  amended since the ~2019 search (`H7BZW7`, amended 2026-06-10), extrapolating to ~114 of 2,298
  sites. Over a multi-year graph the probability that *some* protein is ingested at two versions
  approaches certainty.
- When it arrives, the pre-split schema **cannot represent it at all**. A single `Protein` node
  cannot carry two `sequence_version`s, yet sites legitimately pinned at both attach to it. That is
  a contradiction, not merely a lossy merge — and under I9 replay from a cache that holds both
  versions, nothing in the id determines which sequence the node should get.
- The failure is silent in the way this project keeps paying for: a site pinned at sv4 attached to a
  node carrying sv5's sequence validates its position against the wrong residue, which is the
  isoform-bug arithmetic in a new guise.

**Honest caveat:** a laboratory that ingests everything against one FASTA release will feel nothing
from this change, ever. It buys correctness against an accumulating risk, not a present pain. It is
taken now because nothing is ingested and no key builder exists, so it costs documentation, a schema
mirror and a fixture — and it will never be this cheap again.

## Consequences

**Positive.** Every edge sits at the grain its meaning requires. An enzyme attribution
(`ASSOCIATION_ENZYME` → USP18) no longer needs a sequence version at all, so it is unaffected when
UniProt edits a sequence record. The deferred residue-agreement check becomes sound by construction:
it reads the sequence off the `SITE_ON` target rather than consulting the cache. The graph keys the
same way the resolver's immutable cache already does (`{accession}#sv{n}`), which matters because
`rebuild.py` treats that cache as an input.

**Negative.** A new node type in a deliberately small schema (24 node + 35 rel tables, from 23 + 34),
and a permanent extra hop in site → protein → gene queries. I2's rewording is a normative change to
an invariant. The new "site key sv must equal target sv" clause is **not yet enforced** — it is
recorded with the other unenforced checks in `HANDOFF.md` §8 and lands with the first adapter.

**Not resolved by this ADR.** `ProteinSequence.sequence` is derivable from none of I9's stated inputs
(`raw/`, the curation export, the DDL) — sequences come from UniProt, which is mutable, and a
superseded version may not be refetchable. The split makes the pinned sequence *addressable*, not
*reconstructible*. Recorded as `ONTOLOGY.md` §11 Q6.

## Alternatives considered

**Keep `uniprot:{accession}` and read the pinned sequence from the cache.** Rejected. It cannot
represent two versions of one protein at all, so it fails on the case that motivates the decision.
It also leaves `Protein.sequence` in the graph as a column that looks authoritative and must never be
trusted for validation, and makes I9 replay undetermined when the cache holds two versions.

**Put `sv` in the `Protein` key: `uniprot:{accession}#sv{n}`.** Rejected, though it fixes I2 as
cleanly as the split does. Every `Protein` node would then carry a version *in its identity*,
including proteins named by curation rather than by a search — the enzymes behind
`ASSOCIATION_ENZYME` and the razor picks behind `ASSIGNS_PROTEIN`. Their version is not in the data;
it must be looked up at ingest time. So the node's id, and therefore the id of every
`EnzymeAssociation` anchored on it, would depend on *when* it was ingested: a biological assertion
would change identity because a sequence database was edited. That is the non-determinism ADR-0020
exists to prevent, striking I10, which is the product's core claim. It would also make `Modifier`
(itself a protein, keyed bare) inconsistent with `Protein`, and duplicate `ENCODES` and
`ANNOTATED_IN` across version nodes.

**Version by I6-style supersession.** Not distinct: a superseding node needs a distinct id, which
requires the version in the key, which is the rejected alternative above.
