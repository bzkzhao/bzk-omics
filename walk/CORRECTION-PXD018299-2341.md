# CORRECTION — the paper's 2,341 is the site table's row count (2026-11-24)

**This corrects five claims that the paper's stated 2,341 cannot be reproduced from
the PXD018299 deposit: four in `walk/CHECKS-collateral-and-pkm.md` §3,
`walk/CHECKS-census.md` §3 and §4, and `walk/CHECKS-gap-and-protein-grain.md` §3, and
their carrier in `walk/FINDINGS.md` §8.** No figure moves, and no registered rule,
threshold, estimand or verdict changes. The dated checks are not rewritten; each
carries a banner, and this document is the record. `walk/FINDINGS.md` is edited
directly. Three further corrections made in the same build, to
`walk/CHECKS-gap-and-protein-grain.md` §1 and §2, `walk/CHECKS-draws-and-threshold.md`
§6, `walk/CHECKS-ceiling-and-floor.md` §4 and `walk/CHECKS-ceiling-survives.md` §4,
are carried by their banners alone and are not recorded here. Each banner ends with an
*Other homes, not edited* run-in listing its claim's other homes and its execution
records; no earlier `walk/` banner has such a section, and these banners introduce it.

Vocabulary as fixed in `walk/CHECKS-membership-and-corrections.md:8-13`: **withdrawn**
= false as stated, because the instrument or the reasoning was defective; **superseded**
= a correct computation under a stated choice that later evidence disfavours.
"Retired" and "partial withdrawal" are not used (`:15`). All five claims below are
**withdrawn**.

---

## The measurement

The paper states 2,341. The deposited site table, `HAP1_USP18KO_GlyGlyKSites.txt`,
has **2,341 rows**. Four committed sources say so:

- `ROADMAP.md:152`, under a heading dated 2026-08-06 at `:148`: "Sites before
  filtering | 2,341 — matches the published figure";
- `ROADMAP.md:210`: "2,341 sites → **2,298** after decoys and contaminants";
- `ROADMAP.md:286`: "rows in file | 2,341 | 2,341", the platform route against the
  notebook;
- `tests/fixtures/pxd018299_platform_targets.json:14`: `"rows_in_file": 2341`, written
  by `bzk/sources/pxd018299_differential.py:371` (`rows_in_file=len(table.rows)`) — a
  measurement taken by the platform rather than by hand.

bzk measured it again on 2026-11-17, on bzk's machine, against the verified raw-store
bytes:

```
uv run python -c "
from bzk.adapters import maxquant
from bzk.provenance.raw_store import verify
from bzk.sources.pxd018299_h10 import HOME, PXD018299_SITES, anchor_population
t = maxquant.read_table(verify(PXD018299_SITES.expected_content_hash, filename=PXD018299_SITES.filename, home=HOME))
print('file rows:', len(t.rows), ' anchor_population:', len(anchor_population(t)[0]))
"
file rows: 2341  anchor_population: 2318
```

The command needs the raw store and is not re-runnable in a clean checkout. It is
quoted as bzk's measurement; the four sources above are the in-repository evidence.

2,341 − 23 reverse decoys = 2,318, the base rounds 13, 14 and 15 read; − 20
contaminants = 2,298, which matches round 13's own log (`notes/logs/round13.txt:26`),
`ROADMAP.md:210`, and `HANDOFF.md:617`'s "43 decoys and contaminants".

**Line numbers.** Every line reference in this record, including every row of the
closing table, is as the banners this correction added leave them. The banner moved
every line of `walk/CHECKS-gap-and-protein-grain.md` from `:3` on down by **65**, of
`walk/CHECKS-draws-and-threshold.md` from `:3` on down by **13**, of
`walk/CHECKS-ceiling-and-floor.md` from `:3` on down by **15**, and of
`walk/CHECKS-ceiling-survives.md` from `:3` on down by **25**. On
`walk/CHECKS-collateral-and-pkm.md` and `walk/CHECKS-census.md` the new banner follows
the 2026-11-15 one: it moved every line of the first from `:18` on down by **30**, and
every line of the second from `:16` on down by **38**, and nothing above those moves —
each title at `:1`, and the 2026-11-15 banner's own lines, keep their numbers. The first
line whose content moves is the run line; the key names the blank before it because
the blank is content-free and the same either way, which makes the statement simpler.
To map a reference measured before the 2026-11-15 banners, add those banners' 16 and
14 as well (`walk/CORRECTION-PXD018299-H10-headline.md:17-22`): 46 on collateral and 52
on census, for any line from `:3` on. References into `walk/FINDINGS.md` are by
section, and its withdrawn §8 text, which no longer exists, is quoted as at `32b6ead`.
A reference to part of a line gives the line and the words that bound the part.

## The instrument defect

Rounds 13, 14 and 15 read the site table through `anchor_population`
(`bzk/sources/pxd018299_h10.py:515`), which drops the 23 reverse decoys and keeps the
contaminants. Round 13 labelled that base "rows in the table"
(`notes/scripts/diagnose_round13.py:164`, printed as 2318 at
`notes/logs/round13.txt:25`), and every later reading started from it. No reading in
the three rounds counted the file's own rows.

A second mislabelling sits in the same place. Round 13's CC docstring
(`notes/scripts/diagnose_round13.py:23`) gives "our candidates are 2,653 raw", but
2,653 is **PXD026748's** row count (`data/curation/curation_PXD026748.json:25`, "2,653
rows"), not this deposit's, whose raw count is 2,341.

Both labels are recorded here and neither is edited: execution records are not edited
(ADR-0041 item 8, `decisions/0041-a-registered-headline-moves-only-through-hypothesis.md:253`).

## The claims withdrawn

**Three grounds.** All five claims are withdrawn, with one successor, but the defect
differs, and each withdrawal and banner names its ground:

- **The misnamed reading.** *The instrument was defective.* The figure the claim relies
  on was misnamed: round 13 labelled the 2,318 rows left after the reverse decoys "rows
  in the table". Whether the claim coins that label — collateral §3's table is round
  13's own output — or inherits it, as census §4 does, it reasons correctly from it, so
  its arithmetic and inference stand or fall with the label, and the defect is the
  reading rather than an independent error of argument.
- **The unit inference.** *The reasoning was defective.* It took round 13's 2,318 as the
  file's row count and inferred that the paper's figure must live at a unit the
  deposited table does not carry. The successor falsifies the premise: the figure is
  the table's own row count.
- **The axis inference.** *The reasoning was defective.* It took round 13's 2,318 as the
  file's row count and inferred, from readings on the **distinct-modified-peptide-id**
  axis, that no reading of the file could be the paper's figure. Those readings are
  sound — census §3's three unions over `Mod. peptide IDs`, gap §3's 54-cell grid — and
  their axis is a different quantity from the file's rows, so what fails is the
  inference rather than the measurement.

The two reasoning grounds are kept apart because the documents differ in fact.
Collateral §3's table is seven **row-count** readings (`:113-121`, column header
"rows"), and its inference is about units. The distinct-modified-peptide-id axis
appears in census §3 (`:137-141`), gap §3 (`:146-147`) and `walk/FINDINGS.md` §8, and
**nowhere in collateral §3**, so a single ground naming that axis would be false of
collateral.

**1. That the 2,341 is at a unit the site table does not carry.**
`walk/CHECKS-collateral-and-pkm.md` §3, three parts on two grounds.

The table's label, `:115`:

> rows in the table | 2,318

- **Withdrawn: the misnamed reading.** The 2,318 is the rows left after the 23 reverse
  decoys, not the table's rows. The label is named here and in the banner, not changed.

The heading, `:111`, entire, and the paragraph `:123-126`. The paragraph's withdrawn
span ends on `:126` at "`modificationSpecificPeptides.txt`," and takes the comma:

> The paper's 2,341 cannot be reconstructed, because it is a different unit
>
> **None is 2,341.** The paper counts GlyGly **peptides**; this table is
> site-keyed, and a site carries several peptide forms, so the count is not
> recoverable from it at any filter or expansion. It would need
> `modificationSpecificPeptides.txt`,

- **Withdrawn: the unit inference.** Both clauses of the heading go: the successor
  falsifies "cannot be reconstructed" as well as "because it is a different unit".

The *Reading*, `:128-130`. The withdrawn span opens on `:128` after the label
"**Reading (judged).**", at "This is a clean negative", and closes on `:130` at "on the
other deposit,":

> This is a clean negative: the constraint is real, and it
> lives at a unit we do not have. It also bounds the same-kind success on the
> other deposit,

- **Withdrawn: the unit inference.** The rest of `:130` and `:131` — the PXD026748
  note, *where expanded rows reproduced its stated 2,143 exactly — that worked because
  the count there was quoted at site-and-multiplicity grain* — survives.

**2. That a 23-row gap separates the table from the paper's figure.**
`walk/CHECKS-census.md` §4. The withdrawn span is an interpolated clause of §4's one
sentence, between the em dashes on `:159` and `:161` and excluding both. It is a
relative clause whose antecedent is the surviving question, so it is quoted here only
inside that sentence: §4 asks whether the deposited table was regenerated after the
analysis — *"which would explain the 23-row gap between 2,318 rows and the stated
2,341, and would be a defeater instance of a kind this project has no example of"* —
and answers that this **cannot be answered from what is held**.

- **Withdrawn: the misnamed reading.** §4 ran no instrument and holds no table; it
  inherits round 13's mislabelled 2,318. There is no gap: the 23 are the reverse
  decoys, and once they are named as decoys both sides of the comparison are rows. The
  clause, and the defeater-instance claim resting on it, go. Its inferences — that a
  gap exists, that regeneration would explain it, that this would be a defeater
  instance of an unexampled kind — are correct given the label and fail with it.
- **Not withdrawn:** the sentence around the clause. Its subject, "Whether the
  deposited table was regenerated after the analysis" (`:159`), and its predicate,
  "**cannot be answered from what is held.** PRIDE's file listing for PXD018299 would
  say." (`:161-162`), stand; the question is open (see *What the successor does not
  settle*).

**3. That the paper's filter cannot be reproduced.** `walk/CHECKS-census.md` §3. The
heading clause on `:132`, which opens after the topic phrase "The 2,341: ", and the
paragraph `:146-149`:

> narrowed from "wrong unit" to "unreproducible filter"

> **`walk/CHECKS-collateral-and-pkm.md` §3 is superseded.** It concluded the count
> "lives at a unit the deposit's processed tables do not provide". The grain is
> available; **what cannot be reproduced is the filter**. No combination tried
> lands on 2,341.

- **Withdrawn: the axis inference.** Its premise is §3's arithmetic at `:143-144`,
  which places the paper's 2,341 between two peptide-id readings; the successor puts
  the figure on the row axis instead.
- Two further defects in the same paragraph, recorded with it. It classifies as
  *superseded* a claim that is now **withdrawn**. And it misquotes collateral §3, which
  says the count "lives at a unit we do not have" (`walk/CHECKS-collateral-and-pkm.md:129`),
  not "lives at a unit the deposit's processed tables do not provide".

**4. That the published record is exhausted on this axis.**
`walk/CHECKS-gap-and-protein-grain.md` §3. The heading clause on `:144`, which opens
after the topic phrase "The 2,341: ", and the claim `:156-158`. `:156` is shared: the
surviving insensitivity sentence ends on it at "missing axis.", and the withdrawn claim
begins on it at "**No filter":

> the published record is exhausted on this axis

> **No filter in this region reproduces the paper's stated
> identification count**, and the declaration that the published record is
> exhausted on this axis is now evidenced rather than assumed.

- **Withdrawn: the axis inference.**

**5. That the 2,341 is unreproducible, as `walk/FINDINGS.md` carried it.**
`walk/FINDINGS.md` §8, as at `32b6ead`:

> **The paper's stated count of 2,341 identified peptides cannot be reproduced.**
> Fifty-four filter combinations over localisation and score give 1,171 to 2,359
> distinct modified peptides, and none is 2,341. On this axis the published record
> is exhausted, which is now evidenced rather than assumed.

- **Withdrawn: the axis inference, carried forward from 3 and 4**, whose figures it
  reports. The withdrawn claims are the first sentence and "On this axis the published
  record is exhausted"; the middle sentence reports gap §3's scan, which survives. The
  paragraph is replaced by the successor, a limit and a pointer here; §8's heading
  changes with it.

**The sentences that are true on their own axis.** "No combination tried lands on
2,341" (census §3) and "No filter in this region reproduces the paper's stated
identification count" (gap §3) are **true of distinct modified-peptide ids**, the axis
their scans measured: no reading on that axis reached 2,341, and round 15's scan
dropped reverse and contaminant rows itself. They are withdrawn as statements about the
paper's 2,341, which is a row count.

**Successor**, to all five: the paper's stated 2,341 **equals** the deposited site
table's row count before any filter, reverse decoys and contaminants included.
`ROADMAP.md:152` recorded this on 2026-08-06.

**Why not "superseded".** That word classifies a correct computation under a stated
choice that later evidence disfavours. The base these readings used was a deliberate
population — `anchor_population`'s, every row but the reverse decoys, argued in its
docstring at `bzk/sources/pxd018299_h10.py:516-523` — so a choice was made; what failed
is the **label** on it. A reading misnamed as something it is not is a defective
instrument, and an inference drawn from the misnamed figure is defective reasoning.
Neither is a disfavoured choice.

## What survives

- **Every count in the three documents**, as a count of what it counted. Two labels are
  wrong and are named, not changed: collateral §3's "rows in the table | 2,318"
  (`walk/CHECKS-collateral-and-pkm.md:115`) and census §3's "all rows | 2,377"
  (`walk/CHECKS-census.md:139`) are over the 2,318 rows left after the reverse decoys.
- **Census §3's *Also narrowed* paragraph** (`walk/CHECKS-census.md:151-154`), whole:
  that the claim set is site-keyed, with 798 published rows mapping one-to-one onto 798
  distinct site rows, so that only the identification count is affected; and that the
  paper's prose calls site-level rows "peptides", "which is loose usage rather than a
  different table". The site-keyed mapping is unaffected. The loose-usage reading is
  one the successor is **consistent with and does not confirm**.
- **Census §3's arithmetic** (`walk/CHECKS-census.md:143-144`): the paper's 2,341 sits
  18 below 2,359 and 70 above 2,271. True as arithmetic on the peptide-id axis. It is
  also the premise of withdrawal 3, since it places the paper's figure on that axis, so
  it is named in the banner and not edited.
- **Collateral §3's closing clause** (`walk/CHECKS-collateral-and-pkm.md:126`, from
  "which the raw store does not hold"), which the withdrawn span stops short of: the
  paragraph names `modificationSpecificPeptides.txt`, *which the raw store does not
  hold*.
- **Census §4's raw-store statement** (`walk/CHECKS-census.md:158` through "only." on
  `:159`): the store holds the site tables, the protein groups and the supplements only.
- **Census §4's question and its answer**, quoted together with the withdrawn clause
  elided: "Whether the deposited table was regenerated after the analysis […]
  **cannot be answered from what is held.** PRIDE's file listing for PXD018299 would
  say." (`walk/CHECKS-census.md:159`, `:161-162`). It is what the first limit below
  rests on.
- **Gap §3's scan figures** (`walk/CHECKS-gap-and-protein-grain.md:149-153`: 54 cells
  scanned, 0 exact hits on 2,341, range 1,171 to 2,359) **and its insensitivity
  finding** (`:155` through "missing axis." on `:156`), as counts and properties of
  distinct modified-peptide ids, and its sentences read on that axis.
- **Collateral §3's note on PXD026748**, the rest of the sentence whose opening is
  withdrawn: it bounds the success on the other deposit, *where expanded rows
  reproduced its stated 2,143 exactly — that worked because the count there was quoted
  at site-and-multiplicity grain* (`walk/CHECKS-collateral-and-pkm.md:130-131`). It is
  about the other deposit and stands.
- **Collateral §5's remaining-routes list** (`walk/CHECKS-collateral-and-pkm.md:161-165`).

## What the successor does not settle

Two limits, stated as limits, not as findings.

- **It does not establish that the deposited table is the one the paper analysed.** The
  row-count match is consistent with that and does not show it. The deposit may have
  been regenerated after the analysis, which census §4 raised and which nothing held
  can answer. What this correction changes is that the assumption is now stated
  explicitly, as a named limit of the successor, instead of sitting implicit in census
  §4. **The assumption itself stays open.**
- **It does not settle what the paper's word "peptides" denotes.** The figure is
  reproduced **as a row count**. Census §3's reading, that the paper's prose calls
  site-level rows "peptides", is consistent with the successor and is **not confirmed**
  by it; nothing here reads the paper's intent, and `HYPOTHESIS.md:310-311` records the
  opposite inference.

## What does not change

No figure moves. No registered rule, threshold, estimand or verdict changes. H10's
headline, `walk/FINDINGS.md` §5 and §6, and `bzk/audit.py` are untouched. The suite and
the tautology sweep read as before.

## Every home of the withdrawn claims, the named labels and claims, what survives beside them, and the execution records, and how each was handled

Each `handled` cell names which kind of home the row is, from six kinds:
**withdrawn claim**; **named label**; **named claim, not withdrawn** — a claim this
correction shows to be false that no withdrawal covers, named in a banner and not
edited, which is collateral `:1` and `:167-170` and nothing else; **surviving figure or
statement** — a figure, clause, sentence or paragraph the correction leaves standing,
named *figure or statement* because four of its rows carry no figure at all;
**execution record**; **context**. There is no seventh. A row may name more than one
kind, and where a line carries more than one kind the row names each.

Every row's `wording` cell quotes the text that row claims, first word to last; a row's
span is that quoted text, not the line range it cites. Four conventions fix how much a
row quotes. (i) A row quotes the minimum text that carries what it claims: for an
execution record, the printed or docstring wording it is named by, not the source line
carrying it; for a context row, the figure or sentence cited. (ii) A line's leading
and trailing whitespace is not content. (iii) Line furniture is not content either: a
Markdown table's `|` delimiters and separator row, a list's `- ` marker, a heading's
`## n. ` prefix, a blockquote's `> `, and a data file's structural punctuation. Here a
table row's inner delimiters are written `\|`, and lines of one span are joined by
" / " where furniture separates them. Emphasis markers inside a span are content.
(iv) A bold run-in label follows its paragraph: a row claiming a whole paragraph claims
the label with it, and a row claiming part of a paragraph claims the label only where
the label carries part of what the row claims. Where a span is a relative clause, the
`handled` cell names its antecedent.

**Every count in the three documents** survives as a count of what it counted, and
only the two mislabelled readings get rows: collateral §3's other six readings, census
§3's other two, and gap §1's and §2's figures — which the gap banner touches, of which
§2 is also what the draws banner points to, and which neither banner moves — are
unrowed and unedited. The **context** rows come last.

| home | wording | handled |
|---|---|---|
| `walk/CHECKS-collateral-and-pkm.md:115` | *"rows in the table \| 2,318"* | withdrawn claim (the misnamed reading) and named label: banner; body not edited |
| `walk/CHECKS-collateral-and-pkm.md:111` | *"The paper's 2,341 cannot be reconstructed, because it is a different unit"* | withdrawn claim (the unit inference), the heading entire: banner; body not edited |
| `walk/CHECKS-collateral-and-pkm.md:123-126` | *"**None is 2,341.** The paper counts GlyGly **peptides**; this table is site-keyed, and a site carries several peptide forms, so the count is not recoverable from it at any filter or expansion. It would need `modificationSpecificPeptides.txt`,"* | withdrawn claim (the unit inference): banner; body not edited |
| `walk/CHECKS-collateral-and-pkm.md:128-130` | *"This is a clean negative: the constraint is real, and it lives at a unit we do not have. It also bounds the same-kind success on the other deposit,"* | withdrawn claim (the unit inference): banner; body not edited |
| `walk/CHECKS-census.md:159-161` | *"which would explain the 23-row gap between 2,318 rows and the stated 2,341, and would be a defeater instance of a kind this project has no example of"* | withdrawn claim (the misnamed reading), the interpolated clause only; its antecedent is the surviving question on `:159`: banner; body not edited |
| `walk/CHECKS-census.md:132` | *"narrowed from "wrong unit" to "unreproducible filter""* | withdrawn claim (the axis inference): banner; body not edited |
| `walk/CHECKS-census.md:146-149` | *"**`walk/CHECKS-collateral-and-pkm.md` §3 is superseded.** It concluded the count "lives at a unit the deposit's processed tables do not provide". The grain is available; **what cannot be reproduced is the filter**. No combination tried lands on 2,341."* | withdrawn claim (the axis inference), with its misclassification and its misquote: banner; body not edited |
| `walk/CHECKS-gap-and-protein-grain.md:144` | *"the published record is exhausted on this axis"* | withdrawn claim (the axis inference): banner; body not edited |
| `walk/CHECKS-gap-and-protein-grain.md:156-158` | *"**No filter in this region reproduces the paper's stated identification count**, and the declaration that the published record is exhausted on this axis is now evidenced rather than assumed."* | withdrawn claim (the axis inference): banner; body not edited |
| `walk/FINDINGS.md` §8, as at `32b6ead` | *"**The paper's stated count of 2,341 identified peptides cannot be reproduced.** Fifty-four filter combinations over localisation and score give 1,171 to 2,359 distinct modified peptides, and none is 2,341. On this axis the published record is exhausted, which is now evidenced rather than assumed."* | withdrawn claim (the axis inference, carried forward): **edited**, the only one. Replaced by the successor, the unit limit and a pointer here; heading changed with it |
| `walk/CHECKS-collateral-and-pkm.md:1` | *"2,341 ruled out"* | named claim, not withdrawn: named in the banner; title not edited. Unshifted |
| `walk/CHECKS-collateral-and-pkm.md:167-170` | *"Tested and exhausted: the FDR rule family, the s0 axis, the imputation grid, the permutation scheme, the estimator, the unit (aggregate and row level), the population (searched, not fitted), the supplements, and the paper's own peptide-count constraint."* | named claim, not withdrawn: the peptide-count constraint is met **as a row count**, and whether the paper's "peptides" denotes these site rows is not settled here. Named in the banner; body not edited |
| `walk/CHECKS-census.md:139` | *"all rows \| 2,377"* | named label: over the 2,318 rows left after the reverse decoys. Not a withdrawn claim: census §3's table is sound. Named in the banner; body not edited |
| `walk/CHECKS-census.md:143-144` | *"The paper states **2,341**, which sits between the last two: 18 below one, 70 above the other."* | surviving figure or statement: true arithmetic on the peptide-id axis, and the premise of withdrawal 3. Named in the banner; body not edited |
| `walk/CHECKS-gap-and-protein-grain.md:149-153` | *"cells scanned \| 54 / exact hits on 2,341 \| **0** / range covered \| 1,171 to 2,359"* | surviving figure or statement: counts of distinct modified-peptide ids. Unaffected; banner says so |
| `walk/CHECKS-gap-and-protein-grain.md:155-156` | *"The counts are also **insensitive to score below 40**, so score is not the missing axis."* | surviving figure or statement: a property of distinct modified-peptide ids. Unaffected; banner says so |
| `walk/CHECKS-census.md:151-154` | *"**Also narrowed:** the claim set itself is site-keyed. The 798 published rows map one-to-one onto 798 distinct site rows, so only the identification count is affected. The paper's prose calls site-level rows "peptides", which is loose usage rather than a different table, and is recorded as such."* | surviving figure or statement: the site-keyed mapping unaffected; the loose-usage reading consistent with the successor, not confirmed. Banner says so |
| `walk/CHECKS-census.md:158-159` | *"The raw store holds the site tables, the protein groups and the supplements only."* | surviving figure or statement. Unaffected; banner says so |
| `walk/CHECKS-census.md:159`, `:161-162` | *"Whether the deposited table was regenerated after the analysis"* […] *"**cannot be answered from what is held.** PRIDE's file listing for PXD018299 would say."* | surviving figure or statement: §4's question and its answer, one row, the withdrawn clause elided. The first limit of the successor rests on it. Banner says so |
| `walk/CHECKS-collateral-and-pkm.md:126` | *"which the raw store does not hold."* | surviving figure or statement: its antecedent is `modificationSpecificPeptides.txt`, the withdrawn span's last word. Banner says so |
| `walk/CHECKS-collateral-and-pkm.md:130-131` | *"where expanded rows reproduced its stated 2,143 exactly — that worked because the count there was quoted at site-and-multiplicity grain."* | surviving figure or statement: its antecedent is "the other deposit", the withdrawn span's last words. Banner says so |
| `walk/CHECKS-collateral-and-pkm.md:161-165` | *"**Figure 2f**, the published volcano, is the last route to the threshold that needs neither Perseus nor the authors. Its curve and its coloured-point count would bound the cut-off in (difference, p) space. Not attempted here. / **Running Perseus** on the deposited matrix at the published settings. / **The authors**, for the threshold, the randomisation count and the population."* | surviving figure or statement. Unaffected; banner says so |
| `notes/scripts/diagnose_round11.py:18` | *"The paper counts GlyGly PEPTIDES (798 of 2,341)."* | execution record: listed, not edited |
| `notes/scripts/diagnose_round13.py:22-26` | *"CC — THE PAPER'S OWN 2,341. The publication states 2,341 GlyGly peptides identified and 798 enriched. 2,341 is an unused constraint on the population: our candidates are 2,653 raw, 2,318 after the population rule and 2,101 reaching the test. This searches readings of the site table for one that gives 2,341 exactly, as the same kind of constraint did on the other deposit (where expanded rows carrying intensity reproduced its stated 2,143)."* | execution record, carrying the second mislabelling (`:23`'s "2,653 raw", PXD026748's count): listed, not edited |
| `notes/scripts/diagnose_round13.py:157` | *"CC — readings of the site table, against the paper's stated 2,341 GlyGly peptides"* | execution record: listed, not edited |
| `notes/scripts/diagnose_round13.py:164` | *"rows in the table"* | execution record, the label the misnamed reading names: listed, not edited |
| `notes/scripts/diagnose_round13.py:184` | *"<- matches the paper's 2,341"* | execution record: listed, not edited |
| `notes/logs/round13.txt:24-25` | *"CC — readings of the site table, against the paper's stated 2,341 GlyGly peptides / rows in the table:   2318"* | execution record, the label as printed: listed, not edited |
| `notes/scripts/diagnose_round14.py:22-25` | *"GG — THE PEPTIDE-LEVEL COUNT. The paper states 2,341 GlyGly peptides; no reading of the site table gave it. MaxQuant's sites table carries `Mod. peptide IDs` as semicolon lists, whose union is the peptide-level count the site table CAN provide. If it lands on 2,341 the unit question closes."* | execution record: listed, not edited |
| `notes/scripts/diagnose_round14.py:165` | *`("all rows", rows)`* | execution record, census §3's "all rows" reading over the 2,318: listed, not edited |
| `notes/scripts/diagnose_round14.py:174` | *"<- matches the paper's 2,341"* | execution record: listed, not edited |
| `notes/logs/round14.txt:21` | *"all rows:   2377 distinct modified-peptide ids"* | execution record: listed, not edited |
| `notes/scripts/diagnose_round15.py:21-24` | *"KK — THE 2,341 SCAN, BOUNDED AND GUARDED. The target sits between the localisation-filtered 2,271 and the contaminant-filtered 2,359, so the paper's filter lies in a small region with two monotone axes. Scanned for an EXACT match on distinct modified-peptide ids, reporting how many cells hit it and whether any hit is defensible on its face."* | execution record: listed, not edited |
| `notes/scripts/diagnose_round15.py:181` | *"KK — a bounded scan for the paper's 2,341 modified peptides"* | execution record: listed, not edited |
| `notes/scripts/diagnose_round15.py:199` | *`if len(union) == 2341:`* | execution record: listed, not edited |
| `notes/scripts/diagnose_round15.py:202` | *"exact hits on 2,341:"* | execution record: listed, not edited |
| `notes/scripts/diagnose_round15.py:210` | *"no cell reaches 2,341: on this axis the published record is exhausted, evidenced rather"* | execution record: listed, not edited |
| `notes/logs/round15.txt:20` | *"KK — a bounded scan for the paper's 2,341 modified peptides"* | execution record: listed, not edited |
| `notes/logs/round15.txt:30` | *"exact hits on 2,341: 0"* | execution record: listed, not edited |
| `notes/logs/round15.txt:31-32` | *"no cell reaches 2,341: on this axis the published record is exhausted, evidenced rather than assumed."* | execution record: listed, not edited |
| `notes/scripts/diagnose_s1_provenance.py:7` | *"the paper counts GlyGly PEPTIDES,"* | execution record: listed, not edited |
| `ROADMAP.md:152` | *"Sites before filtering \| 2,341 — matches the published figure"* | context: the successor, recorded 2026-08-06 |
| `ROADMAP.md:210` | *"2,341 sites → **2,298** after decoys and contaminants"* | context: unchanged, correct as it stands |
| `ROADMAP.md:286` | *"rows in file \| 2,341 \| 2,341"* | context: unchanged, correct as it stands |
| `ROADMAP.md:3736` | *"`HAP1_USP18KO_GlyGlyKSites.txt` \| 2,341"* | context: unchanged, correct as it stands |
| `ROADMAP.md:3756` | *"`HAP1_USP18KO_GlyGlyKSites.txt` \| 2,341"* | context: unchanged, correct as it stands |
| `ROADMAP.md:6085` | *"2,341 sites → 2,298 after decoys and contaminants → 2,056 after localisation → 1,375 tested"* | context: unchanged, correct as it stands |
| `ROADMAP.md:8610` | *"2,341 rows, 2,298 in the denominator"* | context: unchanged, correct as it stands |
| `HANDOFF.md:616-617` | `:616` *"it is not the notebook's 1,375 nor the file's 2,341"*; `:617` *"2,341 rows → 43 decoys and contaminants"* | context: unchanged, correct as it stands |
| `decisions/0038-contrast-arms-are-declared-and-bound-at-the-loader.md:255` | *"`2,341 → 2,298 → 2,056 → 2,029 → 1,362`"* | context: unchanged, append-only |
| `walk/PREREG-PXD026748-ingest.md:40` | *"The anchor dropped 43 of 2,341, about 1.8%."* | context: unchanged, correct as it stands |
| `bzk/adapters/maxquant.py:153` | *"records the 2,341 → 2,298 it makes on the site table."* | context: unchanged, correct as it stands |
| `bzk/adapters/maxquant_sites.py:23` | *"2,341 rows → 2,298 after"* | context: unchanged, correct as it stands |
| `bzk/adapters/maxquant_sites.py:491` | *"records 2,341 → 2,298"* | context: unchanged, correct as it stands |
| `tests/fixtures/pxd018299_platform_targets.json:14` | *`"rows_in_file": 2341`* | context: the platform's own measurement of the successor; unchanged |
| `HYPOTHESIS.md:310-311` | *"its Fig. 2f volcano is at GlyGly-peptide grain — 2,341 peptides across 2,172 protein groups"* | context: not the paper's own words but this repository's own grade-B inference, carrying the paper's unit word as an inference. Out of scope for this record; listed, not edited |

**Completeness.** The search, run before any edit, at `37846f5` (identical to
`32b6ead` outside `notes/prompts/`):

```
git grep -n -i -e "2,341" -e "2341" -e "different unit" -e "unreproducible filter" \
  -e "exhausted on this axis" -e "record is exhausted" -e "23-row" -e "peptide-count" \
  -- . ':(exclude)notes/prompts' ':(exclude)notes/REVIEWER-*'
```

Its scope is the whole repository except `notes/prompts/` and `notes/REVIEWER-*`,
which quote the claims as dated records. It returned **185** hits. Two classes are
excluded wholesale: digits inside hashes, `uv.lock`'s package-URL hashes, **3** hits;
and digits inside floats in five `tests/fixtures/` files — `pxd018299_h10.json`,
`pxd018299_h10_attempt2.json`, `pxd018299_h10_attempt3.json`,
`pxd018299_published_cascade.json` and `pxd026748_reconstruction.json` — **135** hits.
`tests/fixtures/pxd018299_platform_targets.json:14` is not a float; it is an integer
target and a context row. That leaves **47** hits, and every one falls inside a row of
the table above. Run after the edits, the search would also hit the banners', this
record's and `walk/FINDINGS.md` §8's own quotations.

**Listed, not found.** The search's eight terms do not reach every row, so the rows are
not presented as search-found. Fourteen rows carry no search term in their own span:

- ten `walk/` rows: collateral `:115`, `:126`, `:128-130`, `:130-131` and `:161-165`;
  census `:139`, `:151-154`, `:158-159`, and `:159` with `:161-162`; gap `:155-156`;
- four execution-record rows: round 13's script line 164, round 14's script line 165,
  round 14's log line 21, and the S1 provenance script line 7.

So the search reaches **no line** of collateral §3's *Reading*, **neither** mislabelled
table row, and neither line of gap §3's insensitivity finding: withdrawal 1's *Reading*
part, both named labels and **seven of the eight surviving rows** are listed from this
record rather than found by the search. The eighth, gap's scan figures, contains a hit
on `:152`. Withdrawal 1's heading and its `:123-126` paragraph are search-found. In
census §4 the search reaches **only** `:160`, the interpolated clause's own line, which
carries both "23-row" and "2,341": withdrawal 2 is search-found, while the surviving
question, its answer and the raw-store statement are not.

Further lines this record or a banner cites, which the search cannot reach and which
are not rows: `walk/CHECKS-collateral-and-pkm.md:113-121` and `:129`;
`walk/CHECKS-census.md:137-141`; `walk/CHECKS-gap-and-protein-grain.md:146-147`;
round 15's log line 9; round
15c's script line 8 and its log; round 10's script lines 23 and 165; round 16's script
lines 107-124; `notes/logs/round13.txt:26`; `data/curation/curation_PXD026748.json:25`;
`decisions/0041-a-registered-headline-moves-only-through-hypothesis.md:253`;
`bzk/sources/pxd018299_h10.py:515` and `:516-523`; `bzk/sources/pxd018299_differential.py:371`;
`ROADMAP.md:148`; `walk/CHECKS-membership-and-corrections.md:8-13` and `:15`; and
`walk/CORRECTION-PXD018299-H10-headline.md:17-22`. A line the search cannot reach is
listed, never claimed as found.
