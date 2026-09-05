# ADR-0032 — What the Perseus adapter reads from an export it was not written for, and whether the platform converts

| | |
|---|---|
| Status | Proposed |
| Date | 2026-09-05 |
| Supersedes | — |
| Superseded by | — |

## Context

`ROADMAP.md`'s four-findings block, landed at `705ca35`, records that the deposit admitted by
ADR-0031 cannot be read by `bzk/adapters/perseus.py` as it stands. Each of its findings has a **code
half**, measured in this repository, and a **file half** about two `.xlsx` files that are not in the
tree. **Every file half cited below stays labelled as the block labels it: reviewer-supplied and not
re-derivable in this container.** Nothing here re-measures them and nothing here confirms them.

This record decides three questions and builds nothing. It changes no adapter, writes no converter,
ingests nothing, and writes no curation record.

### The order the three were taken, and why

**Q1 (which protein column), then Q2 (the annotation row), then Q3 (whether the platform converts) —
and Q2 was returned to after Q3 for its second half.** The order is not neutral and is stated rather
than left to be inferred. If Q2 were answered by changing `sniff` and Q1 by widening
`PROTEIN_COLUMNS`, the only conversion left would be spreadsheet to tab-separated text, and Q3's
*transport* disposition would be far easier to defend than it is on the conversion the four-findings
block describes. Ruling Q3 first would have fixed the amount of remaining conversion **by
assumption**; ruling Q1 and Q2 first fixes it **by decision**, and Q3 is then answered against a
remainder that is known rather than assumed.

**The ordering was chosen for that reason and did not produce the answer it favours.** Q1 and Q2 both
shrink the conversion, exactly as the interaction predicts, and Q3 still does not land on transport —
it lands on there being no conversion at all, for a reason neither Q1 nor Q2 supplies.

Q2's answer has two halves with different dependencies, so it is recorded as two. Its **negative**
half — that a converter must not manufacture the marker — is independent of Q3 and was settled
before it. Its **positive** half — what `sniff` reads instead — depends on what the adapter is handed,
which is Q3's question, and was settled after it. Reporting Q2 as one undivided answer taken before
Q3 would misdescribe how it was reached.

### What `HANDOFF.md` §8 already ruled, and what it did not

`bzk/rebuild.py` l.36 cites `HANDOFF.md` §8 in a parenthetical, and the row it reaches is
`HANDOFF.md` l.736. That row says:

> Three hazards are handled on the strength of the documented format rather than a real file: the
> `-Log Student's T-test p-value` column name, the `#!{...}` annotation rows, and `Majority protein
> IDs` as the accession column. All three are conventions, and a real export may spell any of them
> differently — the adapter refuses loudly on each (naming the columns it looked for) rather than
> guessing, so a mismatch is a clear error and not a silent empty result. **Trigger: the first real
> export.**

Two of the three hazards are Q1 and Q2. **What the row settles, constrains, and merely predicts is
different for each, and the row's own words decide it — not its resemblance to what this record
wants.**

**For Q1 it settles the failure mode and nothing else.** *"the adapter refuses loudly on each (naming
the columns it looked for) rather than guessing"* is in the present tense about the adapter's
behaviour **on meeting** a divergence: it says what happens, not what should then change. The only
forward-looking token in the row is *"**Trigger: the first real export.**"*, and a trigger names an
occasion on which an item becomes live. It does not name a remedy. **So the row is silent on which
column an adapter should read**, and Q1 is not answered by it. What it does constrain is negative and
binding: whatever the answer, it may not be reached by guessing, and a mismatch may not become a
silent empty result.

**For Q2 it predicts, and the prediction has been borne out.** *"a real export may spell any of them
differently"* is a prediction about files not yet seen; the four-findings block's file half records
that the deposit's files carry **zero** occurrences of the annotation prefix, which is that
prediction arriving in its strongest form — not a different spelling but no occurrence at all. The
row is again silent on the remedy. It is **not** silent on one thing: an adapter that accepts such a
file must still fail loudly on a file it cannot read, so any replacement test must still refuse
rather than half-read.

**The distinction matters because the two readings were both available.** *Refuses loudly rather than
guessing* can be read as a position on what the adapter does today, or as a standing prohibition on
ever changing the test. The row's grammar decides: every verb in the clause has the adapter as its
subject and the present as its tense, and the sentence's purpose — given by its own final clause,
*"so a mismatch is a clear error and not a silent empty result"* — is to say what a user sees, not
what a maintainer may do. It is the first reading. **Changing `sniff` is therefore not forbidden by
this row; shipping a `sniff` that guesses would be.**

### One claim in that row is false as written, and this record does not repair it

The same row states *"no Perseus export from the group exists."* **That is false against this
repository at `705ca35`**, and the finding is recorded here and carried to the turn's report as a
numbered defect. It is not repaired here: `HANDOFF.md` is not edited by this record, and the row's
home is `HANDOFF.md` §8.

Three sites in the tree contradict it, all measured here:

* `bzk/sources/protein_groups.py` l.9–10 names *"**BJC Supplementary Data 2** (`MOESM4`) — a Perseus
  protein-level export, 25 rows"* and *"**BJC Supplementary Data 3** (`MOESM5`) — the same, 323
  rows."*
* `ROADMAP.md` l.12076 records *"BJC supplementary Tables 1–3 | Perseus exports — Table 1 site grain,
  Tables 2–3 protein grain, all carrying `C:`/`N:`/`T:`/`M:` prefixes"*, with the consequence *"This
  is a real analysis-output (Perseus) adapter input"*.
* `ROADMAP.md` l.1356–1357 records that both *"already enter `raw/` through
  `provenance/raw_store.store`, the same content-addressing every other input gets, and both
  verify"*.

**The claim is elsewhere stated with the qualification that makes it true**, which is why this is a
defect in one sentence rather than a disagreement about a fact. `HANDOFF.md` l.522 reads *"no Perseus
export from the group exists and the two BJC supplementary tables are published *results* rather than
this laboratory's own file"* — conceding that the tables are Perseus exports and excluding them on a
stated ownership ground. **l.736 carries the clause without the ground**, and a claim that is true
only under a qualification it does not carry is false where it stands.

**Nothing about the deposit is needed to establish this and nothing imported is used for it.** The
file half's report that `Supplementary_Data_S1_TP.xlsx` carries a Perseus type prefix on 11 of its 29
columns is *not* offered as further evidence: it is reviewer-supplied, it concerns a partial stamp
against a criterion that says *every* column name, and the defect stands without it.

---

## Decision

### Q1 — the column an adapter reads is the row's identity, not the wider set

**The ground the module docstring gives assumes a relation, and the relation is named.**
`bzk/adapters/perseus.py` l.36–40 reads:

> The set read is **`Protein IDs`, not `Majority protein IDs`**, where both are present. §6.3:
> *"MaxQuant's `Leading proteins` and `Protein` columns are its own razor-rule inference, not
> ground truth"* — and `Majority protein IDs` is that inference, being the subset carrying at
> least half the peptides. An observation records what was observed, so it takes the wider column.
> The two differ on 52-72% of rows, so this is not a formality.

**Measured here, not imported.** The relation it assumes has three named parts: the narrower column
is a **subset** of the wider; the subset is fixed by a **stated derivation rule**, *"carrying at least
half the peptides"*; and the two **differ on a stated proportion**, 52–72% of rows.
`bzk/sources/protein_groups.py` l.27–29 states the same relation from the other side — *"`Protein
IDs` lists every protein in the group; `Majority protein IDs` lists the subset carrying at least half
the peptides, and its first entry is MaxQuant's leading pick"* — so this is the repository's account
of the pair in two places and not one sentence's phrasing. `ONTOLOGY.md` l.722 supplies the
classification the ground rests on: *"MaxQuant's `Leading proteins` and `Protein` columns are its own
razor-rule inference, not ground truth, and are recorded as such."*

**So the ground is not about width. It is about provenance, and width is its consequence for this
one pair**: the wider column is preferred because the narrower one is *the tool's inference*, and for
MaxQuant's pair the inference happens to be a narrowing.

**Whether the deposit's pair stands in that relation is not established — by this record or by the
reviewer.** The four-findings block's file half, reviewer-supplied and not re-derivable in this
container, records over `Supplementary_Data_S1_TP.xlsx`'s 7,610 data rows that *"the `Protein.Group`
column gives **7,610** distinct sets with none repeated; the `Protein.Ids` column gives **7,591**
distinct sets, with **19** appearing twice"*, and that *"none of the four spellings in
`PROTEIN_COLUMNS` appears in it"*. **Those are counts of distinct sets. They say nothing about
per-row containment and nothing about which column is wider on a row.** The docstring's rule takes
its input — width — from a measurement neither half of the block carries, so **the rule as written
has no input for this pair and cannot be applied to it at all.** That is the finding, and it is
stronger than *the ground does not transfer*: the ground cannot even be evaluated.

**What follows if the relation does not hold.** The preference for the wider column is derived
entirely from the narrower one being an inference. Where neither column is a tool-side narrowing of
the other, both are readings of what was reported, and *"An observation records what was observed"*
picks neither — the sentence stops discriminating. **A rule whose ground has evaporated is not a
default to fall back on; it is a rule with no case left.**

**The consequence of choosing wrong is not cosmetic.**
`decisions/0022-protein-group-ambiguity.md` l.67–69 decides:

> 1. **`ProteinObservation` gains `candidate_proteins STRING[]` as an identifying field**, and
>    `RESOLVES_TO_PROTEIN` becomes `MANY_MANY`, one edge per member. The observation is then keyable
>    without choosing, and what it asserts is what the search reported.

Measured here: `bzk/ontology/schema.py` l.588 reads `RelTable("REPORTS_PROTEIN", "Dataset",
"ProteinObservation", multiplicity="ONE_MANY")`. With `candidate_proteins` identifying, two rows
carrying the same set converge on one `ProteinObservation` (ADR-0020's content-derived ids), and that
one destination then takes two `REPORTS_PROTEIN` edges from one `Dataset` — which `ONE_MANY` forbids.
**On the imported figures, `Protein.Ids` has 19 sets appearing twice and `Protein.Group` has none.**

**Decided. The column an adapter reads is the one that identifies the entity the row's quantities
were computed for, and the operational test is one-to-one correspondence with the export's data
rows.** Stated so it decides a file this record has not seen:

1. **Never read a column that is another candidate's tool-side narrowing.** This is the docstring's
   ground, unchanged, and it survives because it was never about width. Where the narrowing relation
   is asserted, it is asserted from the engine's documented behaviour and recorded as such.
2. **Among the candidates clause 1 leaves, read the one whose value is distinct on every data row.**
   The module's stated grain is protein — l.7, *"the grain is **protein**, so a row becomes a
   `ProteinObservation` anchored on a `Protein`"* — so one row is one protein-grain entity, and a
   column that repeats across rows is not naming that entity.
3. **Where two surviving candidates are both distinct on every row, read the wider.** Clause 1's
   ground then applies in the form the docstring already gives it.
4. **Where the candidate clause 1 prefers is not distinct on every row, refuse and name what was
   found.** Do not fall through to another column. This is `HANDOFF.md` l.736's *"refuses loudly on
   each (naming the columns it looked for) rather than guessing"*, carried forward to a check on
   content rather than on a column name.

**What the rule decides about an export nobody here has seen.** It decides by measuring the file
rather than by recognising a name, so a FragPipe `combined_protein.tsv`, a Spectronaut report, and a
future DIA-NN release that renames its columns are all decided without this record or
`PROTEIN_COLUMNS` being rewritten: whichever candidate column is distinct on every data row is the
identity. Where **no** candidate is distinct on every row, the file's grain is not one row per
protein-grain entity, the module's stated grain does not hold for it, and the adapter refuses — which
is the right answer and not a gap. `PROTEIN_COLUMNS` survives as the list of **where to look**; it
stops being **what is chosen**.

**What the rule yields for the deposit's file, with its one unmeasured input named.** Clause 2 admits
`Protein.Group` (7,610 distinct over 7,610 rows) and refuses `Protein.Ids` (7,591 distinct, 19
repeated) — on imported figures, labelled. **Clause 1 cannot be evaluated**, because whether either
column is the other's narrowing is exactly what the file half does not record. So the admission of
`Protein.Group` is **conditional**, and the condition is a named measurement: per-row containment
between `Protein.Group` and `Protein.Ids` over the file's 7,610 rows, which would say whether either
is a subset of the other and in which direction. **Until that measurement exists, an adapter applying
this rule reads `Protein.Group` and an implied change records that clause 1 went unchecked.** Naming
the gap is not deferring the rule: clauses 2–4 decide the file today, and clause 1 can only overturn
that by showing `Protein.Group` to be a tool-side narrowing, in which case the adapter must refuse
rather than read either.

**This bears on ADR-0022 and does not amend it.** ADR-0022 made the observed group the identity; it
did not say which column supplies the group for an export it was not written from. That is the gap
this clause fills, and it fills it here rather than in that record, which is `Accepted`.

### Q2 — `sniff`'s test changes; the conversion does not supply the row

**The two options, and the first loses on a ground the repository already holds.**

`bzk/adapters/perseus.py` l.65–68 states what the marker is for:

> Perseus writes annotation rows between the header and the data, each prefixed `#!{...}`.
> Only the prefix is relied on. The rows' internal layout is not parsed — the adapter needs named
> columns, not column types, and depending on a format detail it does not need would be inventing
> precision it cannot check against a real export.

and l.145–150 states why the test is on content:

> True for a tab-separated file carrying at least one Perseus annotation row.
>
> Content, not name (`ARCHITECTURE.md` §3): the MaxQuant site table this group also produces
> is `.txt` and tab-separated too, so a suffix distinguishes nothing.

**What the marker asserts:** that this file carries Perseus's inter-header annotation rows — which is
a claim about **who wrote the file**, since nothing but Perseus writes them. That is the whole
content of the assertion, because *"Only the prefix is relied on"*.

**Whether asserting it would be true, for a file the platform produced from a deposit that carries
none: no.** The file half records **zero** occurrences of the prefix in either `.xlsx`. A converter
writing the line would be writing a false statement about the file's origin, and the adapter would
then be reading back a marker the platform itself had written — the marker stops being evidence and
becomes a token the platform passes to itself. That is `CLAUDE.md`'s *generated values are never
displayed as measurements* one level in, and it is the shape this repository keeps meeting: a check
reporting clean because it never ran. **The four-findings block's scratch conversion did exactly this
and labelled the line INVENTED at the point it wrote it.** So the first option loses, and it loses on
the marker's own docstring rather than on preference.

**Decided: `sniff`'s test changes.** The negative half above is independent of Q3. The positive half
— what the test reads instead — is settled by Q3 below, and is recorded there and restated here once
Q3 has been taken.

**Measured here, and it moves the question:** `sniff` does not currently reach its annotation-row
test on a spreadsheet at all. Instrument: a two-row workbook written by `openpyxl` in the scratchpad
and handed to `PerseusAdapter.sniff`, which returned `False`; the same bytes raised
`UnicodeDecodeError` under `read_text(encoding="utf-8", errors="strict")`. Nothing was written to the
tree and the probe file was deleted. So the refusal happens at l.152–154, the decode gate, **before**
l.157's annotation test runs. **The annotation row is the second thing that has to change about
`sniff`, not the first** — which the four-findings block could not see, because it framed the
question over a file already converted to text.

**Q2's positive half, taken after Q3.** `sniff` reads the **column-name type prefix**, which is the
marker the repository already calls decisive and the marker a Perseus **Excel** export actually
carries. Two sites in the tree, both measured here:

* `bzk/sources/protein_groups.py` l.13–14: *"The first two are the exact artefact in question:
  Perseus exports, identifiable by the `C:` / `N:` / `T:` column-type prefixes it writes into an
  Excel export."*
* `ROADMAP.md` l.12078: *"the type-prefix stamp is decisive; a bare statistics-column search gave a
  false positive (a `Q-value` column occurs in raw MaxQuant output too)"*, with the consequence
  *"Classify Perseus by the prefix stamp, never by the presence of a statistics column"*.

**The second of those forecloses the obvious alternative and is quoted rather than stepped around.**
Testing for the declared contrast's `Student's T-test Difference` column would be classifying Perseus
by a statistics column, which that row forbids by name and for a measured reason.

**What `sniff` then distinguishes, and whether its stated reason survives.** Its reason is that the
MaxQuant site table this group also produces is `.txt` and tab-separated, so a suffix distinguishes
nothing. The type prefix distinguishes them for the same reason the annotation row did — MaxQuant
writes no `C:` / `N:` / `T:` / `M:` stamp on a column name — so the test stays on content and the
docstring's ground is untouched. **What it distinguishes is weaker than what it distinguished
before, and this record says so rather than letting the word *decisive* carry it**: the survey's
criterion is that Perseus *"stamps a type prefix on **every** column name"*, and a test that accepts
**at least one** stamped column name admits a file that some Perseus step wrote part of the header
of, rather than a file Perseus wrote. That is a real widening. It is taken deliberately, because the
alternative criterion — every column name — is refuted for the deposit's files by the file half's
report of 11 of 29 and 11 of 27, and a test nothing real can pass is not a test.

**What the rule decides about an export nobody here has seen.** A tab-separated or spreadsheet file
carrying no `#!{` row and no type-prefixed column name does **not** sniff as a Perseus matrix and is
refused — including a DIA-NN, FragPipe or Spectronaut report that has been through no Perseus step at
all. **The widened test does not open this adapter to search-engine output**, which is the property
that matters: `ARCHITECTURE.md` §3's split between the two adapter classes survives it, and a file
that has genuinely never met Perseus still cannot enter through the analysis-output path.

### Q3 — the platform does not convert; the bytes go to `raw/` and the reading is code

**This is the question the other two rest on, and the repository has already answered it once — for
this file type, from this laboratory.** So this record applies an existing ruling and does not make a
new one.

**I9, read whole and answered against its own words.** `ONTOLOGY.md` l.889:

> **I9 — Reproducible rebuild.** The graph is a derived artifact, never authoritative. Given `raw/`
> (content-addressed), the curation export, **the UniProt sequence cache**, and this DDL, the entire
> graph must be regenerable from scratch. Curation records and manual inferences are the only
> non-derivable content; they serialise to a plain JSON export alongside the graph and are versioned
> independently. This is what converts schema change from a migration problem into a compute-time
> problem — see §10.

**On its face I9 does not distinguish transport from processing.** It constrains what the graph must
be regenerable *from*; it says nothing about who produced the bytes sitting in `raw/`. Read no
further, and the question is genuinely open — which is why the third disposition was real when this
turn began.

**It is settled by I9's own recorded generalisation, at `ONTOLOGY.md` l.911–916**, written after the
first cold rebuild failed on one label:

> **The generalisation is the part to keep:** for a derived-store guarantee, an input being
> *unmodified* is a weaker property than it appears — what I9 needs is that the input be
> **re-derivable by the code that reads it**, and a parse frozen in a snapshot is neither raw capture
> nor current derivation. `raw/` has this property because it stores bytes; the sequence tier has it
> because it stores bytes; the entry tier does not, because it stores a parse.

**A converted file in `raw/` is a parse frozen in a snapshot.** It is the entry tier's failure one
level out: the entry tier stored a parse of UniProt's JSON, the parsing code was corrected an hour
later, and five `Gene` nodes could not be regenerated because the correction could not reach a cache
hit. A converted tab-separated file stores a parse of the deposit's spreadsheet, and a correction to
the converter would not reach it either. **`raw/` stores bytes. That sentence is the ruling, and it
was written about a different tier for the same reason.**

**`bzk/rebuild.py` l.36–38 rules on the narrower half and is quoted so its reach is not overstated:**

> `perseus.py` still stays out: it has no real input (`HANDOFF.md` §8) and inventing one to make the
> replay look fuller would put content in the graph that `raw/` cannot regenerate, which is the one
> thing I9 forbids. The MaxQuant site table is the opposite case — it *is* in `raw/`, by digest.

**What it decides:** that content the graph holds must be regenerable from `raw/`, and that
fabricating an input to populate the replay violates that. Its subject is *"inventing one"* — a file
conjured where none exists.

**What it leaves open, stated plainly.** It rules on the **absence** of an input, not on any
platform-produced input in general: a conversion of bytes that do exist is not the case its sentence
describes. **It does reach Q2's first option**, and squarely: a converter supplying an `#!{` line
would be inventing content the deposit does not carry, so that option is forbidden by this passage as
well as by the marker's own docstring. **It does not by itself make disposition 1 unavailable** — a
genuinely lossless re-encoding invents nothing, and this passage would not catch it. **What closes
disposition 1 is l.911–916, not l.36–38**, and the two are not the same ruling.

**And l.30–34 says what the regenerable-from-`raw/` clause means in practice**, which fixes what
compliance looks like rather than leaving it to reading:

> **Search-output ingestion joined the replay 2026-08-07.** Each curation record names a deposit by
> `content_hash`; where those bytes are in the content-addressed store, the record's
> `SampleMapping` and the file go through the adapter that recognises it, and the sites are written
> alongside the curation. This is what I9's *"regenerable from `raw/` plus the curation export"*
> actually means — before it, the clause was discharged against curation content only.

**The precedent, read rather than assumed.** The anchor's curation record at
`data/curation/curation_PXD018299.json` l.3 names `"file": "HAP1_USP18KO_GlyGlyKSites.txt"` and l.13
`"search_engine": "maxquant"` — a processed artefact, produced by a tool that is not in this
repository. **What that establishes is exactly one thing: ingesting something downstream of the
instrument is already normal.** It establishes nothing about who may perform the processing, because
in that case the processing was performed by the submitter and published, and the record cites the
bytes the submitter published.

**Is a step performed by the platform different in kind from a step performed by the submitter? Yes,
and the difference is which side of I9's boundary it falls on.** The submitter's MaxQuant run is
**captured external state**: it happened once, outside this repository, and `raw/` holds its output
as bytes with a digest that a third party can check against PRIDE. I9 does not claim that output is
regenerable and never did — `ONTOLOGY.md` l.1086 says so directly, that *"`raw/` is not
reconstructible either and has always been an input"*. A step performed by the platform is **inside**
the regenerability claim: its output is derived content, and derived content that is stored rather
than recomputed is the frozen parse l.911–916 rules out. **So the same operation changes standing
depending on who performs it, and the reason is not authorship but which of I9's two categories the
result lands in.**

**The repository has already done this, for `.xlsx`, from this laboratory.** Measured here:

* `bzk/sources/protein_groups.py` l.176 reads `stored = store(response.content, supp.filename)` — the
  supplementary `.xlsx` enters the content-addressed store as **the bytes that were fetched**.
* l.185 reads `path = verify(supp.expected_content_hash, filename=supp.filename)` — it is read back
  by digest.
* l.142–143 declares `def measure_perseus_export(path: Path, artefact: str) -> list[GroupStats]:`
  with the docstring *"A Perseus Excel export: title in row 1, `C:`/`N:`/`T:`-prefixed header in row
  2, data after."* — the spreadsheet is parsed **in code**, at read time, with `openpyxl` (l.52), and
  its columns are matched with their type prefix intact (`"T: Protein IDs"`, l.149).
* `ROADMAP.md` l.1356–1357 and l.1366 record the same arrangement in prose and its consequence for
  the invariant: *"they already enter `raw/` through `provenance/raw_store.store`, the same
  content-addressing every other input gets"*, and *"**I9's input list does not change**: `raw/` is
  already its first input and these are already in it."*

**There is no converted intermediate anywhere in that path, and none was needed.**

**Decided — disposition 2, in its sharper form.** The conversion is processing, so it must be code in
this repository under I9; and once it is code it is not a conversion but a **reader**, because there
is no reason to write its output to disk. The deposit's bytes go to `raw/` by digest, unmodified, and
the spreadsheet is parsed at read time by code that ships with the platform. **The platform does not
convert.**

**Disposition 1 is rejected, and the reason is named rather than left as a preference.** A converted
file in `raw/` freezes a parse; correcting the reader would not move it; and the digest a curation
record cited would be the digest of a file that exists nowhere outside this platform, so a third
party could check it against nothing. `bzk/rebuild.py` l.152–157 makes the point about digests from
the other direction — the deposit is *"Located by **digest, not filename**"*, so that *"a replay
cannot silently run against a re-downloaded or revised deposit that happens to share a name"* — and a
digest over platform-produced bytes gives that guarantee against nothing external.

**Disposition 3 is rejected, and it was live until l.911–916 was read.** I9's headline sentence does
not settle the question; its generalisation does. Recording that is the point: the answer is in the
invariant, one paragraph past where the question would naturally stop reading.

**A converted file can therefore not be a `Dataset`, and the reason is worth stating in the form the
code already carries it.** `bzk/adapters/perseus.py` l.174–175 and l.186 hash and parse the same
bytes — `raw = path.read_bytes()`, then `header, rows = self._read(raw, path)`, then
`"content_hash": content_hash(raw)` — and `_read`'s docstring at l.289–291 states the property that
buys: *"The caller passes the bytes it hashed, so the `Dataset` digest and the parsed content are the
same read of the same file."* A converter between the hash and the parse breaks that sentence. Under
this decision it is never inserted.

---

## Consequences

**Positive — the deposit becomes readable without anything being invented.** Every step the
four-findings block's scratch conversion had to invent is removed by a decision here rather than
worked around: the invented `#!{` line is refused by Q2, the `Protein.Ids` → `Protein IDs` rename is
unnecessary once the identity is chosen by content (Q1), and the whole spreadsheet-to-text step is
refused by Q3. What remains is a reader.

**Positive — three name-list hazards become content checks.** `HANDOFF.md` l.736's three hazards are
handled today by matching literal column names. Q1 clause 2 and Q2's replacement test both decide by
reading the file, so an export that spells things differently is decided rather than refused for
spelling.

**Negative — the multi-row header is not solved by any of this, and it is the hard part.** The
four-findings block records, imported, that in both files the quantitative columns' identity spans
**three** rows while the identifier and statistics columns are named on the third alone, so *"no
single row of either file is a complete header"*. Measured here: `bzk/adapters/perseus.py` l.293
reads `header = lines[0].split("\t")` and takes its header from one line and no other. **Deciding the
identity column and the sniff test does not tell a reader how to compose a header from three rows**,
and this record does not decide it. It is named as an implied change and as an open question.

**Negative — one home becomes two unless something moves.** `bzk/sources/protein_groups.py` already
carries an `openpyxl` reader for a Perseus Excel export. An adapter growing its own would be two
homes for one rule, which is what that module itself refused when the spill-line guard went to
`bzk/adapters/maxquant.py` instead — l.159–160, *"any MaxQuant reader hits it, and a copy in each
would be two homes for one rule."*

**Negative — `Dataset.content_hash` has a fork this record does not close, and closing it is
forbidden here.** `content_hash` is identifying under §3. `bzk/rebuild.py` l.213–216 records that the
loader and the adapter converge on the `Dataset` *"because both key it on `content_hash` — the loader
from the record, the adapter by hashing the bytes"*. With a spreadsheet reader in the adapter the
convergence holds — both name the deposit's bytes — but the adapter must hash the file it was handed
and parse it through the reader, not hash a derived text. **This record states the requirement and
chooses no `content_hash`**, which it is forbidden to do.

**Neutral — nothing about whether this deposit is ingested.** ADR-0031, the criteria and every survey
verdict are untouched. This record says only what an adapter would have to read.

---

## Alternatives considered

**Widen `PROTEIN_COLUMNS` with the DIA-NN spellings and stop there.** Cheapest, and it does not
decide. The tuple is an ordered name preference; adding `"Protein.Ids"` and `"Protein.Group"` to it
would put them in some order, and that order would be the decision — made silently, by position in a
literal, on no ground. It also decides exactly one file: the next export spelling its columns a third
way needs the tuple edited again, which is the thing `CLAUDE.md` calls a rule that decides one case.

**Keep the annotation-row test and require the deposit to supply one.** Refused above on the marker's
own docstring. Recorded here as well because it is the option that costs nothing to implement, which
is what makes it dangerous: it would leave `sniff` reading a token the platform wrote.

**Test `sniff` on the declared contrast's statistics columns.** Forbidden by `ROADMAP.md` l.12078 by
name — *"Classify Perseus by the prefix stamp, never by the presence of a statistics column"* — on a
measured false positive.

**Convert the spreadsheet to tab-separated text outside the repository and record the deposit as the
source.** The four-findings block's scratch reproduction is this option, executed. It is rejected by
`ONTOLOGY.md` l.911–916 and not by its results.

**Convert inside the repository and store the converted file in `raw/`.** The nearest miss, and it
fails on the same paragraph for the same reason: what is stored is a parse, and a correction to the
converter does not reach it. Storing the bytes and parsing at read time costs nothing more and has
the property I9 needs.

---

## Implied changes — described, not made

**None of these is made by this record. It decides and does not build.**

1. **`sniff` learns two things**: that a Perseus export may be a spreadsheet, and that its marker is
   the column-name type prefix. Both change `bzk/adapters/perseus.py` l.145–157. The docstring's
   *content, not name* ground is unchanged and must be restated against the new test.
2. **`_one_of`'s selection stops being a name-order preference.** `PROTEIN_COLUMNS` stays a candidate
   list; the choice among candidates becomes Q1's four clauses, which need the parsed rows and
   therefore run after `_read` rather than at l.177.
3. **A spreadsheet reader gets one home.** Whatever it is, `bzk/sources/protein_groups.py` calls it
   instead of carrying its own `openpyxl` block, on the precedent that module set for itself.
4. **A multi-row header composition is decided and written.** Not decided here. `_read` takes
   `lines[0]` and nothing else; a file whose column identity spans three rows needs a rule for
   composing them, and that rule must not invent a column name that is in no row.
5. **Clause 1 of Q1 is checked for the deposit's pair.** The named measurement is per-row containment
   between `Protein.Group` and `Protein.Ids` over the file's 7,610 rows. Until it exists, an adapter
   applying this rule reads `Protein.Group` with clause 1 unevaluated, and that is recorded rather
   than hidden.
6. **`HANDOFF.md` l.736's `no Perseus export from the group exists` is repaired to the qualified
   claim l.522 already carries.** Its home is `HANDOFF.md` §8 and this record does not touch it.
7. **No `ONTOLOGY.md` amendment is implied.** I9 is applied, not changed. Had one been needed it
   would be recorded here with its own record named as a prerequisite; none is.

---

## Open

1. **How a three-row header composes into one, and what a composed column name is.** Consequence 3
   above. It is the only part of reading this deposit that no decision here reaches.
2. **Whether *at least one type-prefixed column name* is the right threshold.** Q2 takes it knowingly
   weaker than the survey's *every column name*, on the ground that the stricter criterion is refuted
   for the deposit's files by imported figures. A dated re-measurement of those files would settle
   whether the partial stamp is the norm for this pipeline or an artefact of these two.
3. **Whether the deposit's archive holds a tab-separated export.** Recorded in the four-findings
   block as reviewer-supplied, undated and unchecked. If it does, Q3's reader is unnecessary for this
   file and the decision is unaffected — nothing here rests on the file being a spreadsheet, only on
   the platform not manufacturing one.
