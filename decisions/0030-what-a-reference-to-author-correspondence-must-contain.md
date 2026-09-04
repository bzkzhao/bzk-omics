# ADR-0030 — What a reference to author correspondence must contain, and why the enum's other four values do not need one yet

| | |
|---|---|
| Status | Proposed |
| Date | 2026-09-04 |
| Supersedes | — |
| Superseded by | — |

## Scope

Decides what a curation record must supply alongside `basis = 'author_correspondence'` for the
claim to be checkable by a reader who is not the recipient of the email, and rules on whether the
value's `authoritative` confidence is the defect instead.

**This record decides and does not build.** No `ONTOLOGY.md` amendment, no schema change, no field
added to any curation record, no edge emitted. **It uses the correspondence nowhere**: nothing here
quotes it, cites it, or treats anything it contains as established.

Every figure and line reference below was measured at `f345243`, and the instrument is stated
beside each.

## The state of the tree, measured before the question was framed

**`author_correspondence` is used by no curation record.** `grep -rn` over the repository
(excluding `.git` and `.venv`) returns **13 lines** mentioning the value, in **four files**:
`ROADMAP.md` (10), `ONTOLOGY.md` l.581 (1), `bzk/ontology/schema.py` l.32 (1) and ADR-0026 l.109
(1). Reading every `*.json` under `data/curation/` — **three files** — the only one carrying a
`basis` at all is `curation_PXD018299.json`, which carries `publication_methods` / `inferred`; both
fixtures under `tests/fixtures/` carry the same pair. **No record in the tree has ever carried
`author_correspondence`.**

**`basis` and `confidence` are identifying on `Analysis`; `rationale` is not.** Read from
`schema.IDENTITY["Analysis"].fields` at run time rather than from the §3 table: twelve fields,
including `basis` and `confidence`, excluding `rationale`. `bzk/curation/loader.py` states the
consequence at the point it validates: *"It is identifying on Analysis (§3), so a misspelling forks
an id rather than failing."* **So a change to l.581's Meaning cell is prose, and a change to a
record's `basis` value re-mints the curation `Analysis` id and everything anchored on it.**

**The reference to the source lives in `rationale` today, for the one value that has been used.**
`curation_PXD018299.json`'s `rationale` is 1,515 characters opening *"Design taken from the methods
section of Pinto-Fernandez et al., Br J Cancer 124:817-830 (2021), doi:10.1038/s41416-020-01167-y."*
`ONTOLOGY.md` l.93 places `rationale` in the excluded family *"descriptive free text (`label`,
`rationale`)"*. **So the DOI that warrants the shipped record is in a field nothing can check.**

**Two mechanisms for citing a source already exist on `Analysis`, and both are declared and
unemitted.** Read from `schema.REL_TABLES`:

| Relationship | Endpoints | Multiplicity | Emitted today |
|---|---|---|---|
| `CURATION_CITES` | `Analysis` → `Publication` | — | no |
| `WAS_ASSOCIATED_WITH` | `Analysis` → `Person` | `MANY_ONE` | no |

`CURATION_CITES` is in the shipped DDL at `ONTOLOGY.md` l.511 and at `bzk/ontology/schema.py`
l.596. **The repository has already diagnosed why it is unemitted, for `publication_methods` and in
a test**: `tests/test_curation_loader.py` records that the real record *"cites a DOI inside
free-text `rationale` and nowhere structured"*, that regex-extracting it *"would be inventing an
identifier from prose"*, and that *"the record format needs a structured `publication` field; until
it has one, `CURATION_CITES` is not emitted."*

`WAS_ASSOCIATED_WITH` is unemitted for a different reason. `curated_by` is `null` in all three
records that carry the key — the shipped record and both fixtures — and it is listed in
`bzk/curation/loader.py`'s `STRUCTURAL_KEYS`, so it never becomes a node field. `grep -rn` finds
`curated_by` in exactly seven places and **none of them is `ONTOLOGY.md` or `bzk/ontology/`**: it is
a record key the loader recognises and discards. `tests/test_curation_loader.py` records the
consequence: *"`Person` keys on `orcid` + `name`, and only `orcid`'s absence is classified
(`curated`, §3) — a nameless Person cannot be keyed, so none is emitted."*

**`Publication` is an authority node and `Person` is not.** `schema.IDENTITY["Publication"]` has
empty `fields` and `authority=True`; `bzk/ontology/schema.py` l.215 defines that flag as marking
*"a reference node whose id is the external identifier itself."* `Person` keys on `orcid` and
`name` with `authority=False`. **This is the whole of why the two mechanisms are not
interchangeable here**, and it is measured rather than argued.

## The question

`ONTOLOGY.md` l.581 gives the value the meaning *"Design confirmed directly by the submitters"* and
the confidence `authoritative` — one of two values in the enum carrying it. I8 makes `basis` a label
carried into every view and export, and ADR-0026's R2 states the reason that matters: *"a reader
told* basis: publication_methods *will go and check the paper, which is not where the load is."*

**A reader told `basis: author_correspondence` can go and check nothing.** Private email has no
citable identifier, no public location, and no third party who can confirm it. So: what must the
record supply for the claim to be actionable by someone who is not the recipient — and if nothing
can make it so, is the confidence the defect rather than the missing rule?

## Decision

**R1 — The problem is general to the enum and its acute form is specific to this value, and the two
must not be conflated.** No basis value has a structured reference today; the shipped record's DOI
sits in free text and `CURATION_CITES` goes unemitted for exactly that reason, which the test suite
already records. **What is specific to `author_correspondence` is that the general fix has nothing
to name.** A structured `publication` field closes `publication_methods` because a DOI exists;
correspondence has no identifier for such a field to hold. **So this record does not propose a
reference field for the enum. It decides what the one value that cannot use it must supply
instead.**

**R2 — A reference to correspondence records attribution, because it cannot record verification,
and the record must say which of the two it is offering.** A third party cannot inspect a private
email. What a third party *can* do is address the person who made the claim. Those are different
acts, and the enum's other four values do not distinguish them because for all four the artefact is
public. **A record whose `basis` is `author_correspondence` and whose reference reads like a
citation is claiming the wrong one**, which is R2 of ADR-0026 read one level in: the label must not
promise a reader an act they cannot perform.

**R3 — The minimum content, and it is invented here rather than derived from an existing form.**
Four elements. **Named as an invention**: nothing in `ONTOLOGY.md`, ADR-0026 or the record format
states a reference form for any basis value, so there was no convention to follow and this one is
announced instead of slipped in.

1. **Who asserted it**, by name, sufficient to key a `Person` — which by `schema.IDENTITY` means at
   minimum `name`, `orcid` being classifiable absent under §3.
2. **When**, as a date, so that a later contradicting statement can be ordered against it.
3. **What was asked**, because a confirmation is only as good as the question it answers, and
   *"design confirmed"* does not say which design was put to the submitter.
4. **What was asserted**, in the submitter's terms rather than the curator's, so that the mapping
   step performed afterwards is visible as a separate act.

**Element 4 is what makes the rule falsifiable rather than decorative.** A record supplying 1–3 and
paraphrasing the answer into the curator's own vocabulary has hidden the mapping step, and under
ADR-0026's own widened `submitter_metadata` cell — *"Still `inferred`: it is prose about an
experiment, and the curator does the mapping"* — a hidden mapping step is the difference between
`authoritative` and `inferred`. **So a reference that fails element 4 is not a badly documented
`author_correspondence`; it is a record that has not shown it is one.**

**R4 — `authoritative` is correct and is not the defect.** The tempting ruling is that an
unverifiable warrant cannot be the highest confidence, and it is wrong on ADR-0026's own evidence.
Its Evidence Three establishes that *"Authorship does not predict confidence inside the existing
table"* — `sdrf` and `author_correspondence` are both submitter-sourced and `authoritative` while
`submitter_metadata` is submitter-sourced and `inferred`. The axis the enum actually runs on is
stated in ADR-0026's Decision: `inferred` is where *"the curator does the mapping."* **On that axis
`author_correspondence` is correctly `authoritative`** — the submitter states the assignment and the
curator performs no mapping step. **Public inspectability is a different property, and the enum
records it nowhere.** Four of five values happen to correlate with it; this one does not, and the
correlation is what makes the omission invisible.

## Options, each with its cost

| Option | Cost | Why not chosen |
|---|---|---|
| **(a) a `rationale` convention with a stated minimum** | none | **rejected**: `ONTOLOGY.md` l.93 excludes `rationale` from identity as descriptive free text, so nothing can check the convention was followed, and `CLAUDE.md` states the standing preference — *"if the assertion can be written, it is written"* |
| **(b) a structured reference field on the curation record** | a record-format change and a loader change | **the shape R3 describes**, and the one an implied change would build |
| **(c) a `Publication` node via `CURATION_CITES`** | none beyond the loader | **rejected on the tree, not on cost**: `Publication` is `authority=True`, its id *is* the external identifier, and correspondence has none. Inventing one is the defect `tests/test_curation_loader.py` already refuses for the DOI |
| **(d) a `Person` node via `WAS_ASSOCIATED_WITH`** | a non-null `curated_by` and a keyable `Person` | **partial, and it collides**: the edge is `MANY_ONE`, so one `Person` per `Analysis`, while a correspondence-based curation has a curator *and* a correspondent in different roles |
| **(e) demote the confidence** | an `ONTOLOGY.md` amendment that re-mints ids | **rejected under R4** |
| **(f) defer — nothing uses the value** | none | **rejected under the immutability below** |

**(d) is the finding that changes what an implied change would look like.** The machinery to
attribute a curation `Analysis` to a named person is already in the shipped DDL and is unemitted
only because `curated_by` is null everywhere and discarded by the loader. But `MANY_ONE` admits one
`Person`, and R3's element 1 needs a *second* one in a different role. **Whether that is solved by a
property on the edge, a second relationship, or a role field is a schema question this record does
not decide.**

## Why deferring is the expensive option

`ONTOLOGY.md` l.588 states the immutability that governs this, and it is not I6's own sentence: I6
at l.886 names only *"`ModifierAssignment` and `DifferentialResult` nodes"*, and l.588 extends it by
cross-reference — *"Curation nodes are immutable under I6. A corrected mapping supersedes rather
than overwrites, and the retraction propagates to every derived result and figure."* **The reach to
curation nodes is stated at l.588 and nowhere else**, checked by reading I6 itself rather than
citing its number.

**So a curation record adopted before the rule exists cannot be retro-fitted.** Adding the reference
later is not an edit; it is a supersession, and because `basis` and `confidence` are identifying the
new `Analysis` carries a different id, with the retraction propagating to every derived result and
figure. **The cost of deferring is therefore not "write it later" but "supersede it later"**, and it
is paid in full the first time the value is used — which, measured above, has not yet happened.
**That is the argument for deciding now and the reason (f) is rejected**: the window in which this
is free is exactly the window in which no record carries the value.

## What the sources do not settle

**Whether public inspectability should be recorded at all, and if so where.** R4 establishes that
the enum's confidence column runs on whether the curator maps, not on whether a reader can inspect.
It does not follow that the second property belongs in the enum. ADR-0026 decided that `basis`
classifies warrants; it did not decide whether the confidence column is the only classification a
warrant carries, and neither §5.3 nor I8 says. **Three dispositions are open — a second column, a
property on the curation record, or nothing at all on the ground that R3's four elements already
tell the reader what they can do — and nothing in the repository selects one.** Named here with its
options rather than settled, because settling it is an `ONTOLOGY.md` amendment and this record does
not have one to make.

## Implied changes, described and not made

1. **A structured field on the curation record format** carrying R3's four elements, with the
   loader validating presence rather than content — presence being what a machine can check and
   content being what it cannot.
2. **`curated_by` stops being a `STRUCTURAL_KEY`** and becomes the source of a `Person`, which is
   what `WAS_ASSOCIATED_WITH` is declared for and has never carried.
3. **A resolution of the `MANY_ONE` collision** between curator and correspondent, in whichever
   form a schema decision takes.
4. **A separate decision on whether public inspectability is recorded**, per the section above.
5. **None of these before the first record adopts the value**, which is the only ordering this
   record fixes.

## Consequences

**No record changes and no id moves.** Measured: zero curation records carry the value, so the rule
binds the first one that does and disturbs nothing that exists.

**`publication_methods` is left exactly as it stands.** The shipped record's DOI stays in
`rationale` and `CURATION_CITES` stays unemitted; that defect is recorded in
`tests/test_curation_loader.py` and is not this record's to close.

**ADR-0028 is a live decision about the same record's `basis` and this record does not presuppose
its execution.** Nothing here depends on `curation_PXD018299.json` carrying one value rather than
another.

**What this record does not establish** is that the four elements are sufficient — only that they
are what a third party can act on. A reader supplied with all four still cannot read the email.
That is the honest limit of the decision and it is stated rather than left for a reviewer to find.
