# Prompt 45 — the paper's 2,341 reproduces; W6, W7, R1 and R9 corrected in `walk/`

**Repository:** `main` at the commit adding this prompt. Line references were measured at
`32b6ead`.

**What this is.** Six items from `notes/REVIEWER-DEFECTS.md`, all in `walk/`, no code:

| item | what | form |
|---|---|---|
| W11, W5, and four further claims of this project's own | the paper's 2,341 is the site table's row count, so five claims resting on the contrary are withdrawn; W5's assumption is stated rather than settled | a CORRECTION record, banners, FINDINGS §8 |
| W6 | "selection adds almost nothing" was tested only for selection on a fold-change floor | banner |
| W7 | "MOESM5's values are log2 ratios" was never confirmed | banners |
| R1 | two supersessions with no banner on the superseded document | banners |
| R9 | FINDINGS opens "Two deposits"; §10a is a third | FINDINGS lead |

**The finding behind the first row.** Rounds 13, 14 and 15 read the PXD018299 site table through
`anchor_population` (`bzk/sources/pxd018299_h10.py:515`), which drops the 23 reverse decoys and
keeps the contaminants. Round 13 printed that base as "rows in the table: 2318"
(`notes/logs/round13.txt:25`; `notes/scripts/diagnose_round13.py:164`), and every later reading
started from it. No reading in the three rounds counted the file's own rows. The file has **2,341
rows**, the paper's stated figure. Four committed sources agree:

- `ROADMAP.md:152`, under a heading dated 2026-08-06 at `:148`: "Sites before filtering | 2,341 —
  matches the published figure";
- `ROADMAP.md:210`: "2,341 sites → **2,298** after decoys and contaminants", mid-line;
- `ROADMAP.md:286`: "| rows in file | 2,341 | 2,341 |", the platform route against the notebook;
- `tests/fixtures/pxd018299_platform_targets.json:14`: `"rows_in_file": 2341`, written by
  `bzk/sources/pxd018299_differential.py:371` (`rows_in_file=len(table.rows)`) — a measurement
  taken by the platform rather than by hand.

And **measured by bzk on 2026-11-17**, on his machine against the verified raw-store bytes:

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

2,341 − 23 reverse = 2,318; − 20 contaminants = 2,298, which matches round 13's log,
`ROADMAP.md:210`, and `HANDOFF.md:617`'s "43 decoys and contaminants". **The command needs the raw
store and is not re-runnable in a clean checkout**; the record quotes it as bzk's measurement, with
the four committed sources standing as the in-repository evidence.

**The house form** is the one `b960c9a` set and `cfb1aa7` followed:
- a dated CHECKS document is **not rewritten**; it carries a dated banner at the top;
- a `walk/CORRECTION-*.md` document records a withdrawal that spans documents;
- `walk/FINDINGS.md` is edited directly.

Follow `walk/CHECKS-two-route-recovery.md:3-14` (banner; `:1` is the title) and
`walk/CORRECTION-PXD018299-H10-headline.md` (record: its *Line numbers* paragraph at `:17-22`, its
*The claims withdrawn* / *What survives* / *What does not change* sections, its part-line notation
at `:44-45`, and its single flat closing table at `:156` onward). Vocabulary:
`walk/CHECKS-membership-and-corrections.md:8-13` — **withdrawn** = false as stated, because the
instrument **or the reasoning** was defective; **superseded** = a correct computation under a stated
choice that later evidence disfavours. "Retired" and "partial withdrawal" are not used (`:15`).

**Header blocks.** `CLAUDE.md:59` asks documents to carry a status/version header. No `walk/CHECKS-*`,
`walk/CORRECTION-*` or `walk/FINDINGS.md` carries one; they carry a dated run line or a dated title
instead. The new record follows its neighbours: **no header block**, and the date in the title, as
`walk/CORRECTION-PXD018299-H10-headline.md:1` does. Note this in the report as a convention
followed, not a rule broken.

**Dates.** The record and every banner carry the build day, as `> **Correction (<date>).**`. The
build day is after 2026-11-15, so the second banners on collateral and census differ from the first
by date; no other marker is needed.

---

## 0. Receipt check — answer, then stop and wait

Quote from the file or from git, never from this prompt. **Stop on any mismatch.**

**(a) State.**
- `git log --oneline -2` shows this prompt's commit with `32b6ead` beneath it; `git status --short`
  is empty.
- `pytest -q` reads 1305 passed / 15 skipped.
- `sweep()` reads 60 modules / 2726 asserts, **353 `PINNED` entries** (`len(PINNED)`; the multiset
  total is 373), new 0 / gone 0.

**(b) The lines this prompt changes, quotes or classifies.** Quote each:

| # | where | expected |
|---|---|---|
| R1 | `walk/FINDINGS.md:3-10` | "**Two deposits, reconstructed …" through "…what the published numbers themselves are made of." |
| R2 | `walk/FINDINGS.md:171`, `:180-183` | "## 8. Two negatives that cost real tests"; "The paper's stated count of 2,341 identified peptides cannot be reproduced." through "…evidenced rather than assumed." |
| R3 | `walk/FINDINGS.md:219`, `:225` | "## 10a." and its heading; "**The deposit.** `PXD032267`: Yerra et al., *J Clin Invest* 2023." |
| R4 | `walk/CHECKS-collateral-and-pkm.md:1`, `:3`, `:17-19`, `:81`, `:83-91`, `:93-96`, `:98-101`, `:131-135`, `:137-140` | the title ("…and 2,341 ruled out"); the existing 2026-11-15 banner's first line; its **last** line, the blank after it, and the run line; §3's heading; §3's table, whose column header reads "rows" and whose first row is "rows in the table \| 2,318"; "**None is 2,341.** …" through `:96`, which reads "`modificationSpecificPeptides.txt`, which the raw store does not hold." — one line carrying the end of the claim and a surviving clause; the *Reading*, through "…site-and-multiplicity grain."; §5's remaining-routes list; §5's "Tested and exhausted: … the paper's own peptide-count constraint." |
| R5 | `walk/CHECKS-census.md:3`, `:15-17`, `:94`, `:96-97`, `:99-103`, `:105-106`, `:108-111`, `:113-116`, `:118-124` | the existing banner's first line; its **last** line, the blank after it, and the run line; §3's heading; §3's lead-in sentence, "The union of the site table's `Mod. peptide IDs` … count the table can provide:"; §3's table, whose column header reads "distinct modified-peptide ids" and whose first row is "all rows \| 2,377"; "The paper states **2,341**, which sits between the last two: 18 below one, 70 above the other."; "**`walk/CHECKS-collateral-and-pkm.md` §3 is superseded.** … lands on 2,341."; "**Also narrowed:** … recorded as such."; §4 entire |
| R6 | `walk/CHECKS-gap-and-protein-grain.md:1-7`, `:21-25`, `:29-37`, `:72-77`, `:79`, `:81-82`, `:84-88`, `:90-93` | the title and run line; §1's table rows (observed +1.055; unconditional +1.007; "conditioned on clearing the weakest published fold change" +1.047); the *Readings*, including "Observation and prediction agree to about 0.01 log2 units" and "**Selection adds almost nothing**" through "…turns out not to bite"; §2's MOESM5 paragraph, whose claim begins "Its values" on `:72` and continues "are log2 ratios despite an 'LFQ intensity' header" on `:73`, with the three readings' 0.0%, 0.3% and 0.1% and "remains unknown"; §3's heading; §3's statement that the scan is "for an exact match on distinct modified-peptide ids"; §3's scan table, including "\| exact hits on 2,341 \| **0** \|" and "range covered \| 1,171 to 2,359"; and `:90-93`, where the insensitivity sentence ends with "missing axis." on `:91` and the withdrawn claim begins on the same line with "**No filter in this region reproduces the paper's stated" |
| R7 | `walk/CHECKS-draws-and-threshold.md:1-6`, `:97`, `:108-112`, `:119`, `:123-124` | the title and run line, whose last sentence breaks across `:5-6` ("**Attempt 3's" / "registered verdict stands.**"); §5's heading; "Round 10's 32.9% inherited the rule through its reference point and used a ranking over both directions while the cut counted only one. **Superseded.**" through "…at the documented rule's calling rate"; the MOESM5 row, "values are log2 ratios, not intensities"; "MOESM5's header disagrees with its" on `:123` continuing "content" on `:124` |
| R8 | `walk/CHECKS-ceiling-and-floor.md:1-6`, `:86-93`, `:111-114` | the title and run line, which continues to `:6` ("One further claim of this project's / own is withdrawn below."); §4's table including its header row at `:86-87`, with "**156 (20.8%)**" at `:90` and "**20.8% is a floor no choice of convention removes.** It should be quoted beside the documented rule's 27.8%." at `:92-93`; §5's "**So the claim the evidence supports is:** … with a floor of 20.8%." |
| R9 | `walk/CHECKS-ceiling-survives.md:1-5` (its run line does end at `:5`), `:55`, `:67-72`, `:74-78`, `:80-81` | the title and run line; "**Structural discordance: 9 of 791 claims, 1.1%.**"; §4's table including its header row at `:67-68` and its four data rows at `:69-72`; "**The floor is 13.7%, not the 20.8% reported in round 9.** That figure was an intersection over two points of the family rather than the whole of it, and is **superseded**." through "…20 is few."; "Rank movement is the measure that survives every unresolved question about the convention, and it is the largest of the three." |
| R10 | `notes/logs/round13.txt:24-25`; `notes/logs/round14.txt:21`; `notes/logs/round15.txt:9`, `:20`, `:30-32`; `notes/logs/round15c.txt` | the execution records. `round15.txt:9` must read "median +1.047 over 8296 of 8600 draws"; `round15c.txt` must give the three readings (0.0% at median −26.609 over 1556 cells; 0.3%; 0.1%) and "remains open"; `round14.txt:21` must read "all rows: 2377 distinct modified-peptide ids" |
| R11 | `bzk/sources/pxd018299_h10.py:515-529` | `anchor_population`: "§2's population: every row but the reverse decoys" at `:516`, and `:518-523`'s statement that contaminants and low-localisation rows are kept |
| R12 | `walk/CHECKS-two-route-recovery.md:3-14`, `:25-47`; `walk/CORRECTION-PXD018299-H10-headline.md:1-30`, `:44-45`, `:156-158` | the banner form; the record form, its part-line notation, and its closing table's preamble; and two-route §1's downshift-band table, whose simulation at `notes/scripts/diagnose_round16.py:107-124` applies no conditioning |
| R13 | `bzk/audit.py`, `RECEIPT_MAP` | **Read the live map, not this prompt.** Report the entry count, and for each of the six CHECKS documents: whether it is the `home` of any entry; every `home_anchor` of its entries; the set of `diagnose_round*.py` names the document's own text contains (the guard's pattern is at `tests/test_audit.py:930`); and whether its entries carry a `script_anchor`. Rule 1 and rule 2 both turn on these, so they are measured here rather than taken from this prompt. Also quote the four guard sites the rules and §1.4 cite: `tests/test_audit.py:930` (`_SCRIPT`), `:951-968` (`_misattributed`, with 3b at `:956` and 3c at `:958`), `:1006` (direction 2's occurrence test) and `:1590-1598` (`mislabels_791`'s two triggers) |
| R14 | `data/curation/curation_PXD026748.json:25` | "2,653 rows" — PXD026748's row count |
| R15 | the execution-record lines §1.2 lists | each exists and carries the wording given there: `diagnose_round11.py:18`; `diagnose_round13.py:22-26`, `:157`, `:164`, `:184`; `diagnose_round14.py:22-25`, `:165`, `:174`; `diagnose_round15.py:21-24`, `:181`, `:199`, `:202`, `:210`; `diagnose_round15c.py:8`; `diagnose_round10.py:23`, `:165`; `diagnose_s1_provenance.py:7`. **Report any whose wording differs from the quote this prompt or a banner gives.** Three are known to differ and must be quoted from the file: `diagnose_round10.py:165` reads "no s0 **threshold**", `:23` reads "no rule, no s0 **and** no population argument" (against ceiling-survives `:72`'s "no rule, no s0, no population argument"), and `diagnose_round15c.py:8` reads "log2 **RATIOS**" in capitals |
| R16 | the context and supporting lines §1.2 relies on | each exists and reads as stated: `ROADMAP.md:148`, `:152`, `:210`, `:286`, `:3736`, `:3756`, `:6085`, `:8610`; `HANDOFF.md:616-617`; `decisions/0038-contrast-arms-are-declared-and-bound-at-the-loader.md:255`; `decisions/0041-a-registered-headline-moves-only-through-hypothesis.md:253` (item 8, execution records are not edited); `walk/PREREG-PXD026748-ingest.md:40`; `bzk/adapters/maxquant.py:153`; `bzk/adapters/maxquant_sites.py:23`, `:491`; `bzk/sources/pxd018299_differential.py:371`; `tests/fixtures/pxd018299_platform_targets.json:14`; `walk/CHECKS-membership-and-corrections.md:8-13`, `:15`; `HYPOTHESIS.md:310-311` |

**(c) Absences.**
- `walk/CORRECTION-PXD018299-2341.md` does not exist.
- `git grep -n "2,341" -- walk/FINDINGS.md` returns `:180` **and** `:182`, and nothing else.

**Do not start §1 until bzk replies.**

---

## 1. Build

### 1.1 Order

1. The banners (§1.3).
2. `walk/FINDINGS.md` (§1.4) — **§8 before the lead**, which §1.4 explains.
3. The record (§1.2), last, so its post-banner line numbers are read off the files rather than
   computed.

### 1.2 The CORRECTION record: `walk/CORRECTION-PXD018299-2341.md`

It records the 2,341 withdrawals only. W6, W7 and R1 are carried entirely by their banners (§1.3).

**They are not one claim in one document, and the banners say so.** W7's claim has a second home
(`walk/CHECKS-draws-and-threshold.md:119`, banner 4); R1's 20.8% has a second home in the same
document as the first (`walk/CHECKS-ceiling-and-floor.md:114`, §5); R1 moves a figure, twice, which
is why both are classified; and W6's defect reaches a second document,
`walk/CHECKS-two-route-recovery.md` §1 and through it FINDINGS §2's second route, which this prompt
records as an unexamined limitation and does **not** re-run. Each banner therefore ends with an
*Other homes, not edited* run-in listing its claim's other homes and its execution records. No
existing `walk/` banner has such a section; this prompt introduces it, and the record says so in
one sentence.

**Sections.** The record carries, in this order: *The measurement*; *Line numbers*; *The instrument
defect*; *The claims withdrawn* (with *Three grounds*, *The sentences that are true on their own
axis*, *Successor* and *Why not "superseded"* as run-ins inside it, as the house record runs in its
own successor paragraphs at `:58-63`); *What survives*; *What the successor does not settle*; *What
does not change*; the closing table; *Completeness*. Use `##` headings for all of them except
*Line numbers*, *Three grounds*, *The sentences that are true on their own axis*, *Successor*,
*Why not "superseded"* and *Completeness*, which are bold run-ins — *Completeness* is a run-in in
the house record too (`walk/CORRECTION-PXD018299-H10-headline.md:218`). **Line numbers comes
second**, as the closing run-in of *The measurement* rather than as a preamble above
the first heading, because every reference in every later section is post-banner and that paragraph
is the key to them. (The house record puts its own *Line numbers* in a
preamble above its first heading at `:17-22`, before *The claims withdrawn* at `:26`; this record
puts it inside *The measurement* instead. Either way it precedes every section that uses it, which
is the point. *Completeness* follows the closing table in both.) This is the house record's order plus three sections
this correction needs (*The measurement*, *The instrument defect*, *What the successor does not
settle*) and minus one it does not (*The label error, a separate class*).

**Line numbers.** Every line reference in this record, including every row of the closing table, is
**post-banner** — as the banners this build wrote leave them. State the shift of **all six**
banner-receiving documents once in this paragraph, not only the three the record happens to cite, so
that the paragraph is a complete key; §3 item 5 asks for all six in the report too. Use the form `walk/CORRECTION-PXD018299-H10-headline.md:17-22` uses, but **naming the
first line that moved**: "the banner moved every line of X from `:F` on down by **N**".
- On the four documents receiving a **first** banner — gap, draws, ceiling-and-floor,
  ceiling-survives — the banner goes after the title at `:1` and the blank at `:2`, so `:F` is `:3`.
- On `walk/CHECKS-collateral-and-pkm.md` and `walk/CHECKS-census.md` the new banner follows the
  existing one with a blank line between, so `:F` is the blank that preceded the run line — `:18`
  and `:16` at `32b6ead` — **and nothing above that moves.** Say so: the existing banners' own
  lines, and each title at `:1`, keep their numbers. The closing table's collateral `:1` row is one
  of those; it is not shifted. The first line whose *content* moves is the run line (`:19` and
  `:17`); the key names the blank instead because the blank is content-free and identical either
  way, so `:18` and `:16` on down is the simpler statement. Say that in one clause.

References into `walk/FINDINGS.md` are given by section, and the withdrawn §8 text — which no longer
exists after §1.4's edit — is labelled "as at `32b6ead`". Part-line references use the house
record's notation at `walk/CORRECTION-PXD018299-H10-headline.md:44-45` — **and are stricter than
it.** That precedent gives the line number plus a description ("The sentence starts at `:135`; the
withdrawn phrase is on `:136`"); this record gives the line number plus **the words that bound the
part**, because the closing table's preamble requires every boundary to be in the table. Do not
reproduce the looser house form. **No letter suffixes on line numbers.** The numbers given **below in this
prompt** are pre-banner, measured at `32b6ead`; they are locators for the build and must each be
shifted before being written into the record.

**The instrument defect.** Round 13 labelled `anchor_population`'s output "rows in the table"
(`notes/scripts/diagnose_round13.py:164`, printed at `notes/logs/round13.txt:25`). That base had
already dropped the 23 reverse decoys. Rounds 14 and 15 read the same base. A second mislabelling
sits in the same place: round 13's CC docstring (`notes/scripts/diagnose_round13.py:23`) gives "our
candidates are 2,653 raw", but 2,653 is **PXD026748's** row count
(`data/curation/curation_PXD026748.json:25`, "2,653 rows"), not this deposit's, whose raw count is
2,341. Both labels are recorded and neither is edited.

**Three grounds.** All five claims below are **withdrawn**, with the same successor, but the defect
differs. Name the grounds as they are named here — not by letter — and state each once, as a
*Three grounds* run-in opening *The claims withdrawn*, then refer to each by name in every
withdrawal and in every banner:

- **The misnamed reading.** *The instrument was defective.* The figure the claim relies on was
  misnamed: round 13 labelled the 2,318 rows left after the reverse decoys "rows in the table".
  Whether the claim coins that label — collateral §3's table is round 13's own output — or inherits
  it, as census §4 does, it reasons correctly from it, so its own arithmetic and inference stand or
  fall with the label, and the defect is the reading rather than an independent error of argument.
- **The unit inference.** *The reasoning was defective.* It took round 13's 2,318 as the file's row
  count and inferred that the paper's figure must live at a unit the deposited table does not
  carry. The successor falsifies the premise: the figure is the table's own row count.
- **The axis inference.** *The reasoning was defective.* It took round 13's 2,318 as the file's row
  count and inferred from a reading on the **distinct-modified-peptide-id** axis that no reading of
  the file could be the paper's figure. Those readings are sound — census §3's three unions over
  `Mod. peptide IDs`, gap §3's 54-cell grid — and their axis is a different quantity from the file's
  rows, so what fails is the inference rather than the measurement.

The two reasoning grounds are kept distinct because the documents differ in fact: collateral §3's
table is seven **row-count** readings (`:83-91`, column header "rows") and its inference is about
units; the distinct-modified-peptide-id axis appears in census §3 (`:99-103`), gap §3 (`:81-82`) and
`walk/FINDINGS.md` §8, and **nowhere in collateral §3**. A single ground naming that axis would be
false of collateral, which is why there are two reasoning grounds rather than one.

**What is withdrawn**, each quoted as a blockquote, as
`walk/CORRECTION-PXD018299-H10-headline.md:26-64` does.

1. `walk/CHECKS-collateral-and-pkm.md` §3 — three parts, two grounds, quoted as **three**
   blockquotes:
   - `:85`, the §3 table's "rows in the table | 2,318" label — **the misnamed reading**. The label
     is named, not changed (see *What survives*).
   - `:81`, the heading **entire** — both "The paper's 2,341 cannot be reconstructed" and "because
     it is a different unit", since the successor falsifies the first clause as well as the second —
     and `:93-96`, "**None is 2,341.** … the count is not recoverable from it at any filter or
     expansion. It would need `modificationSpecificPeptides.txt`" — **the unit inference**. `:96` is
     a part-line: the withdrawn span ends at "`modificationSpecificPeptides.txt`" and takes the comma
     after it, and the clause
     that follows it on the same line, "which the raw store does not hold", is **true and
     survives** — the same fact the record keeps as census `:120-121`. Bound this span by those
     words, not by the line.
   - `:98-100`, the *Reading*, as one continuous withdrawn span: from "This is a clean negative"
     through "on the other deposit," — **the unit inference**. Everything from "where expanded rows
     reproduced its stated 2,143 exactly" to the end of `:101` **survives**, so the span is bounded
     by those words and not by line alone. The surviving clause is a relative clause whose
     antecedent sits inside the withdrawn span: quote it only inside a sentence that supplies the
     antecedent — "the PXD026748 note, *where expanded rows reproduced its stated 2,143 exactly …*"
     — never as a standalone blockquote.
2. `walk/CHECKS-census.md` §4, the **interpolated clause** of its one sentence, which runs
   `:121-123`: "which would explain the 23-row gap between 2,318 rows and the stated 2,341, and
   would be a defeater instance of a kind this project has no example of". There is no gap: the 23
   are the reverse decoys, so the clause and the defeater-instance claim resting on it both go.
   **The sentence around it survives and is not withdrawn**: its subject, "Whether the deposited
   table was regenerated after the analysis" (`:121`), and its predicate, "**cannot be answered from
   what is held.** PRIDE's file listing for PXD018299 would say." (`:123-124`). That question is
   what W5 rests on. Bound the withdrawn clause from "which would explain" to "no example of",
   inside the interpolating em dashes on `:121` and `:123` and excluding both. It is a relative
   clause whose antecedent sits in the surviving span, so — as with collateral `:96` and `:100-101`
   — quote it only inside a sentence that supplies the antecedent ("the possibility that the table
   was regenerated, *which would explain the 23-row gap …*"), never as a standalone blockquote, and
   never in a way that implies the question itself is withdrawn.
   **The misnamed reading** — §4 ran no instrument and holds no table; it inherits round 13's
   mislabelled figure, and its inferences from that figure (that a gap exists, that regeneration
   would explain it, that this would be a defeater instance of an unexampled kind) are correct given
   the label and fail with it. This is **W11**, the rows-against-peptides unit slip, at its root:
   once the 23 are named as decoys, both sides of the comparison are rows.
3. `walk/CHECKS-census.md` §3 (`:94`, `:108-111`): the heading, "narrowed from 'wrong unit' to
   'unreproducible filter'"; and "**`walk/CHECKS-collateral-and-pkm.md` §3 is superseded.** … The
   grain is available; **what cannot be reproduced is the filter**. No combination tried lands on
   2,341." **The axis inference.** Two further defects in the same passage, recorded with it: it
   classifies as *superseded* a claim that is now **withdrawn**, and it misquotes collateral §3,
   which says the count "lives at a unit we do not have", not "lives at a unit the deposit's
   processed tables do not provide".
4. `walk/CHECKS-gap-and-protein-grain.md` §3 (`:79`, `:91-93`): the heading, "the published record
   is exhausted on this axis"; and the claim beginning on `:91` with "**No filter in this region
   reproduces the paper's stated identification count**" through "…is now evidenced rather than
   assumed." **The axis inference.** `:91` is a shared line: the surviving insensitivity sentence
   ends on it with "missing axis.", and the withdrawn claim begins on it. Bound this withdrawal by
   those words, exactly as withdrawal 1 bounds collateral `:100`.
5. `walk/FINDINGS.md` §8 as at `32b6ead` (`:180-183`): "The paper's stated count of 2,341
   identified peptides cannot be reproduced", and "On this axis the published record is exhausted".
   **The axis inference, carried forward from 3 and 4**, whose figures it reports.

**The sentences that are true on their own axis.** Say plainly, once: "No combination tried lands on
2,341" (census §3) and "No filter in this region reproduces the paper's stated identification
count" (gap §3) are **true of distinct modified-peptide ids**, the axis their scans measured — no
reading on that axis reached 2,341, and round 15's scan dropped reverse and contaminant rows itself.
They are withdrawn as statements about the paper's 2,341, which is a row count.

**Successor.** The paper's stated 2,341 **equals** the deposited site table's row count before any
filter, reverse decoys and contaminants included. `ROADMAP.md:152` recorded this on 2026-08-06.

**What the successor does not settle.** Two limits, stated as limits, not as findings:
- **(W5) It does not establish that the deposited table is the one the paper analysed.** The
  row-count match is consistent with that and does not show it; the deposit may have been
  regenerated after the analysis, which census §4 raised and which nothing held can answer. **What
  this build changes about W5 is that the assumption is now stated explicitly, as a named limit of
  the successor, instead of sitting implicit in census §4. The assumption itself stays open.**
- **It does not settle what the paper's word "peptides" denotes.** The figure is reproduced **as a
  row count**. Census §3's reading — that the paper's prose calls site-level rows "peptides" — is
  *consistent with* the successor and is **not confirmed** by it; nothing here reads the paper's
  intent, and `HYPOTHESIS.md:310` records the opposite inference. Everywhere the record or a banner
  touches the paper's unit word, write "as a row count" and do not assert the peptide reading.

**Why not "superseded".** The word classifies a correct computation under a stated choice that
later evidence disfavours. The base these readings used was a deliberate population —
`anchor_population`'s, every row but the reverse decoys, argued in its docstring at
`bzk/sources/pxd018299_h10.py:516-523` — so a choice was made; what failed is the **label** on it.
A reading misnamed as something it is not is a defective instrument, and an inference drawn from
the misnamed figure is defective reasoning. Neither is a disfavoured choice.

**What survives.**
- **Every count in the three documents**, as a count of what it counted. Two labels are wrong and
  are named, not changed: collateral §3's "rows in the table | 2,318" (`:85`), and census §3's
  "all rows | 2,377" (`:101`), are over the 2,318 rows left after the reverse decoys.
- **Census §3's *Also narrowed* paragraph** (`:113-116`): that the claim set is site-keyed, with
  798 published rows mapping one-to-one onto 798 distinct site rows so that only the identification
  count is affected; and, in its last two lines, that the paper's prose calls site-level rows
  "peptides", "which is loose usage rather than a different table". Take the paragraph whole — the
  loose-usage sentence begins part-way along `:115`, and a row that claims a whole paragraph claims
  its bold run-in label with it — which is why this row is on whole lines while collateral `:98`'s,
  claiming part of a paragraph rather than the whole of it, is not. The site-keyed mapping is
  simply unaffected; the loose-usage reading is the one the successor is **consistent with and does
  not confirm**.
- **Census §3's arithmetic** (`:105-106`), that the paper's 2,341 sits 18 below 2,359 and 70 above
  2,271. True as arithmetic on the peptide-id axis. It is also the premise of withdrawal 3 — it
  places the paper's figure on that axis, which the successor denies — so it is **named in the
  banner** and not edited.
- **Collateral §3's closing clause** (`:96`, from "which the raw store does not hold"), which the
  withdrawn span at `:93-96` stops short of. Its antecedent, `modificationSpecificPeptides.txt`, is
  the last word of the withdrawn span, so — as with `:100-101` — quote it only inside a sentence
  that names the file, never as a standalone blockquote.
- **Census §4's raw-store statement** (`:120` through the word "only." on `:121`): the store holds
  the site tables, the protein groups and the supplements only.
- **Census §4's question and its answer** — the subject on `:121`, "Whether the deposited table was
  regenerated after the analysis", together with the predicate at `:123-124`, "**cannot be answered
  from what is held.** PRIDE's file listing for PXD018299 would say." The withdrawn clause sits
  between them, so quote the two together as one surviving statement with the clause elided, never
  the predicate alone — on its own it is a subjectless fragment, and it is what W5 rests on.
- **Gap §3's scan figures** (`:84-88`: 54 cells scanned, 0 exact hits on 2,341, range 1,171 to
  2,359) **and its insensitivity finding** (`:90` through "missing axis." on `:91`), as counts and
  properties of distinct modified-peptide ids, and its sentences read on that axis.
- **Collateral §3's note on PXD026748** (`:100-101`, from "where expanded rows reproduced its
  stated 2,143 exactly"), that its stated 2,143 reproduced at site-and-multiplicity grain. That is
  about the other deposit and stands.
- **Collateral §5's remaining-routes list** (`:131-135`).

**What does not change.** No figure moves. No registered rule, threshold, estimand or verdict
changes. H10's headline, FINDINGS §5 and §6, and `bzk/audit.py` are untouched. The suite and
`sweep()` read as before.

**A closing table**, in the house form at `walk/CORRECTION-PXD018299-H10-headline.md:156` onward: a
single flat table, three columns — `home` | `wording` | `handled` — at post-banner numbers, with a
preamble stating:
- which kinds a `handled` cell can name: **withdrawn claim**; **named label**; **named claim, not
  withdrawn** — a claim this correction shows to be false that no withdrawal covers, named in a
  banner and not edited, which is collateral `:1` and `:137-140` and nothing else; **surviving
  figure or statement** — a figure, clause, sentence or paragraph the correction leaves standing,
  which is why this kind is named *figure or statement*: four of its rows carry no
  figure at all (census's raw-store statement and its question-and-answer, collateral `:96`'s clause
  and §5's routes list); **execution record**; **context**. Six kinds, and no seventh: a row that
  fits none of them is reported under §3 item 4, not given a kind of its own;
- that a row may name more than one kind, and that where a line carries more than one kind the row
  names each;
- that **every row's `wording` cell quotes the text that row claims, first word to last** — a row's
  *span* is that quoted text, not the line range it cites. This holds for every row without
  exception, so a context row quoting part of a line satisfies it the same way a withdrawn row does.
  **Four conventions fix how much a row quotes, so that the list below is a property of the
  documents and not of the builder's taste.** (i) A row quotes the **minimum text that carries what the row
  claims**, and never more: for an execution record that is the printed or docstring wording the row
  is named by, not the source line carrying it — round 13's script line 164 claims the label
  `"rows in the table"`, not `    "rows in the table": len(rows),`; for a context row it is the
  figure or sentence cited, not the whole line. (ii) A line's **leading indentation is not
  content**, so a quote opening after or closing before leading or trailing whitespace does not
  begin or end part-way along the line. (iii) **Line furniture is not content either**: a Markdown
  table's `|` delimiters and its separator row, a list's `- ` marker, a heading's `## n. ` prefix, a
  blockquote's `> `, and a data file's structural punctuation (a JSON key's quotes, its colon, its
  trailing comma) are read like indentation. Emphasis markers **inside** a quoted span are content
  and are quoted. (iv) **A bold run-in label follows its paragraph**: a row claiming a whole
  paragraph claims the label with it, and a row claiming part of a paragraph claims the label only
  where the label carries part of what the row claims. So census `:113-116` takes "**Also
  narrowed:**" and is whole at both ends; collateral `:98-100` does **not** take
  "**Reading (judged).**", so `:98` is part-way; and collateral `:93-96` does take
  "**None is 2,341.**", which is itself the withdrawn assertion. Without (iv), convention (i) alone
  would make census `:113` part-way and the list thirty-three. One pair worth distinguishing, because they look alike:
  `tests/fixtures/pxd018299_platform_targets.json:14` is `    "rows_in_file": 2341,` and is **whole**
  — everything after the figure is structural punctuation — so the context lines number thirteen, not
  fourteen; round 13's script line 164 is `    "rows in the table": len(rows),` and is **part-way**,
  because what follows the claimed label is a value, not punctuation. A code line is whole only where **no content the row does not claim
  precedes or follows the quoted span on it**. Round 15's script line 199 is
  `        if len(union) == 2341:` and its row is named by that comparison: `if` and the colon are
  the statement's own syntax rather than content beside it, and the row claims the statement, so the
  line is whole. Round 13's script line 164 and round 14's script line 165 are
  part-way, because each of those rows claims a sub-expression — a dict key, a tuple — and content
  the row does not claim lies before or after it on the line: the dict's value after `:164`'s key,
  the loop header before `:165`'s tuple. **The criterion is convention (i), not
  whether the line prints**; an earlier draft said bare code was "never part-way", which would have
  deleted those two members. Without these four a compliant build can quote whole lines, come up
  short on the list below, and be impossible to mark wrong — which is what an earlier revision did;
- that the report additionally **lists every line where a row's quoted text begins or ends part-way
  along it, naming what claims the rest of that line — another row, or nothing.** These are the
  places a reader could misattribute text, and they are what the `wording` quotes exist to settle.
  **Derive this list; do not copy one from this prompt.** Three earlier drafts enumerated it and
  came up short or named a non-member each time; the test is mechanical, so the build applies it
  rather than trusting a count, and reports what it finds. Known in advance, as a floor and as the
  shapes to look for:
  - **two rows meeting on one line** — collateral `:96` (withdrawn row `:93-96` ends at
    "`modificationSpecificPeptides.txt`", the comma falling on the **withdrawn** side; the surviving
    row begins at "which the raw store"); collateral `:100`; census `:121` (three rows meet: the
    raw-store row ends after "only.", the withdrawn clause begins at "which", the question-and-answer
    row begins at "Whether"); census `:123` (the withdrawn clause ends at "no example of", the
    question-and-answer row resumes at "**cannot be"); gap `:91`. Census `:121` and `:123` belong to
    both shapes: the interpolating em dashes that withdrawal 2 excludes are claimed by no row, so
    each of those two lines has a *nothing* as well as two or three rows meeting;
  - **one row, with the rest of the line claimed by nothing** — census `:94` and gap `:79`, where
    §3's withdrawn heading clause opens after the topic phrase "The 2,341: ", which is content and
    which no row claims; collateral `:98`, where the *Reading*'s span opens **after** the bold label
    "**Reading (judged).**", because that row claims part of the paragraph rather than the
    paragraph itself; collateral `:1`, whose row quotes only "2,341 ruled out" out of the
    title; **thirteen context lines**, whose quotes sit
    inside a longer line — `HYPOTHESIS.md:310` (the quote opens after "and ") and `:311` (it closes
    before ", with the USP18-dependent set"), `ROADMAP.md:152`, `:210`, `:6085`, `:8610`,
    `HANDOFF.md:616` (claiming "it is not the notebook's 1,375 nor the
    file's 2,341", not the 2,029 ingested-population clause that opens the line) and `:617`
    (claiming "2,341 rows → 43 decoys and contaminants"), `decisions/0038-*:255`, `walk/PREREG-PXD026748-ingest.md:40`,
    `bzk/adapters/maxquant.py:153`, `bzk/adapters/maxquant_sites.py:23` and `:491`; **and most of
    the execution-record rows**, whose quotes are printed or docstring wording rather than the source
    line carrying it — round 13's script lines 157, 164 and 184, round 14's script lines 165 and
    174, round 15's script lines 181, 202 and 210, round 11's script line 18, and the S1 provenance
    script line 7. Context and execution-record rows together make up most of this list; give both
    groups and say which lines, not that there are none;
  - **not in this list:** a whole line carrying two *kinds*, such as collateral `:85`, which is the
    preamble's multiple-kinds bullet's case, not this one, and which convention (iii) keeps whole
    because its outer `|` delimiters are furniture **and its row claims the whole of the row's
    content** — the same reasoning covers census `:101`, `ROADMAP.md:286`, `:3736` and `:3756`,
    whose third cells are empty so there is no cell to go unclaimed. (The JSON row is whole for the
    separate reason given above, its structural punctuation.) **Delimiters alone never make a row
    part-way; a cell the row does not claim does** — which is why `ROADMAP.md:152` (a third cell
    unclaimed), `:6085` (the cell runs on past the figure chain) and
    `walk/PREREG-PXD026748-ingest.md:40` (three cells precede the quote) are in the list above while
    those four table rows are not; census `:124`, which the
    question-and-answer row claims from its first word to its last; the three docstring rows — round
    13's `:22-26`, round 14's `:22-25`, round 15's `:21-24` — each of which opens on its first word
    and closes on its last; round 15's script line 199, whose row claims the whole statement —
    whole by convention (i), **not** (iii): the line carries no furniture but its indentation;
    `notes/logs/round15.txt:30`, whose trailing space convention (ii) discounts; and `walk/FINDINGS.md` §8, which is keyed by section, since a
    section-keyed row contributes no line to this list;
- that *What survives*' blanket clause, "every count in the three documents", is carried by the
  preamble rather than by a row each: only the two mislabelled readings get rows, and the preamble
  says in one sentence that **every count in the three documents** survives as a count of what it
  counted — collateral §3's other six readings and census §3's other two named explicitly, and gap
  §1's and §2's figures, which banner 3 touches, and of which §2 is also what banner 4 points
  to, and which neither banner moves — all unrowed and unedited;
- that the context rows come last.

Rows:

*Withdrawn claims.* collateral `:85`, `:81`, `:93-96`, `:98-100`; census `:121-123` (the
interpolated clause only); census `:94`, `:108-111`; gap `:79`, `:91-93`; `walk/FINDINGS.md` §8 —
**edited**, the only one.

*Named, not edited.* collateral `:1` (the title's "2,341 ruled out" — **unshifted**); collateral
`:85` (also a withdrawn claim, as the preamble allows); collateral `:137-140` (§5's "Tested and
exhausted … the paper's own peptide-count constraint" — the peptide-count constraint is not
exhausted: the figure is reproduced **as a row count**, and whether the paper's "peptides" denotes
these site rows is not settled here); census `:101` (a named label; unlike collateral `:85` this
one is **not** also a withdrawn claim — census §3's table itself is not withdrawn, and its readings
are sound); census `:105-106` (a *surviving figure or statement*: true
arithmetic on the peptide-id axis, listed in this group because it is also the premise of
withdrawal 3, named in the banner and not edited).

*Surviving figures and statements inside a banner-corrected section.* gap `:84-88`; gap `:90-91`;
census `:113-116` (§3's *Also narrowed* paragraph, which carries the site-keyed mapping and the
loose-usage reading; *What survives* keeps it and banner 2 names it);
census `:120-121`; census `:121` + `:123-124` (§4's question and its answer, one row, the withdrawn
clause elided); collateral `:96`; collateral `:100-101`; collateral `:131-135`. **Every bullet of
*What survives* has a row here or under *Named, not edited*; check that correspondence both ways
before writing the table.**

*Execution records, listed and not edited* (ADR-0041 item 8, `decisions/0041-*:253`).
- `notes/scripts/diagnose_round11.py:18`.
- `notes/scripts/diagnose_round13.py:22-26` (the CC docstring, including `:23`'s "2,653 raw"),
  `:157`, `:164` (the "rows in the table" label) and `:184`.
- `notes/logs/round13.txt:24-25`.
- `notes/scripts/diagnose_round14.py:22-25` (the GG docstring), `:165` (the `("all rows", rows)`
  reading) and `:174`.
- `notes/logs/round14.txt:21`.
- `notes/scripts/diagnose_round15.py:21-24` (the KK docstring), `:181`, `:199`, `:202` and `:210`.
- `notes/logs/round15.txt:20`, `:30`, `:31-32`.
- `notes/scripts/diagnose_s1_provenance.py:7`.

*Context.* `ROADMAP.md:152`, `:210`, `:286`, `:3736`, `:3756`, `:6085`, `:8610`;
`HANDOFF.md:616-617`; `decisions/0038-contrast-arms-are-declared-and-bound-at-the-loader.md:255`;
`walk/PREREG-PXD026748-ingest.md:40`; `bzk/adapters/maxquant.py:153`;
`bzk/adapters/maxquant_sites.py:23`, `:491`; `tests/fixtures/pxd018299_platform_targets.json:14`;
and `HYPOTHESIS.md:310-311` — the quoted wording spans the line break, ending "2,341 peptides
across" on `:310` and "2,172 protein groups" on `:311`, and `:311` continues ", with the
USP18-dependent set reported as 476 proteins", which the row does not claim. Its row reads: it is
**not** the paper's own words but this repository's own grade-B inference, "its Fig. 2f volcano is
at GlyGly-peptide grain — 2,341 peptides across 2,172 protein groups"; it carries the paper's unit
word as an inference; out of scope for this record, listed, not edited.

**Completeness.** State the search the build ran, before any edit:

```
git grep -n -i -e "2,341" -e "2341" -e "different unit" -e "unreproducible filter" \
  -e "exhausted on this axis" -e "record is exhausted" -e "23-row" -e "peptide-count" \
  -- . ':(exclude)notes/prompts' ':(exclude)notes/REVIEWER-*'
```

The pathspec implements the scope, which is the whole repository except `notes/prompts/` and
`notes/REVIEWER-*`; both exclusions are live — without the pathspec the search also returns
`notes/prompts/30-*.md` and four `notes/REVIEWER-HANDOFF-*` files. **At `32b6ead` it returns 185
hits**; report the number it actually returns and reconcile any difference. Classify every hit
against the classes above. Two classes are excluded wholesale, and both are live:
- **digits inside hashes**: `uv.lock`'s package-URL hashes, 3 hits;
- **digits inside floats** in `tests/fixtures/`: `pxd018299_h10.json`,
  `pxd018299_h10_attempt2.json`, `pxd018299_h10_attempt3.json`,
  `pxd018299_published_cascade.json` and `pxd026748_reconstruction.json`, 135 hits.

Give each excluded class as a count, not a line list. `tests/fixtures/pxd018299_platform_targets.json:14`
is **not** in the float class: it is an integer target and a context row. 185 − 138 leaves **47**
hits to classify.

**Do not claim any class the search cannot return.** Earlier drafts excluded "PXD026748's 2,143"
and "unrelated uses of 'ruled out'"; neither term is in the search, and no line it returns carries
either. A class that cannot be reached is not an exclusion.

**Listed, not found.** The search's eight terms do not reach every line this record lists, so the
record must not present its rows as search-found. **Derive this rather than copying it**: test each
closing-table row's own span against the eight terms, and report (i) the count the search returns,
(ii) the rows it cannot reach, by group, and (iii) the further lines the banners and this record
cite that it cannot reach. Reconcile all three.

The reviewer measured the following at `32b6ead` against the row list as §1.2 now gives it; treat
it as a cross-check and **report any difference rather than matching it**. **Fourteen closing-table
rows are unreachable**, in two groups:
- **`walk/` rows whose own wording carries no search term (10)** — collateral `:85`, `:96`,
  `:98-100`, `:100-101`, `:131-135`; census `:101`, `:113-116`, `:120-121`, `:121`+`:123-124`; gap
  `:90-91`.
- **execution-record rows (4)** — round 13's script line 164; round 14's script line 165; round
  14's log line 21; the S1 provenance script line 7.

**Further lines the record or a banner cites that the search cannot reach are named too, not
counted as rows — and this set is derived, not copied.** Test every line this record or a banner
cites, not only the closing-table rows. Known in advance, as a floor: round 15c's script line 8;
round 10's script lines 23 and 165; round 15's log line 9; round 16's script lines 107-124;
`data/curation/curation_PXD026748.json:25`; `decisions/0041-*:253`;
`bzk/sources/pxd018299_h10.py:516-523`, which *Why not "superseded"* cites;
`walk/CHECKS-membership-and-corrections.md:8-13` and `:15`, the vocabulary;
`walk/CORRECTION-PXD018299-H10-headline.md:17-22` and `:44-45`, the forms this record follows;
`ROADMAP.md:148`; `bzk/sources/pxd018299_differential.py:371`; and `notes/logs/round15c.txt`.

Say the consequence plainly, in the record: the search reaches **no line** of collateral §3's
*Reading*, **neither** mislabelled table row, and neither line of gap §3's insensitivity finding —
so withdrawal 1's *Reading* part, both named labels and **seven of the eight surviving rows** are
listed from this record rather than found by the search. In census §4 the search reaches **only**
`:122`, the interpolated clause's own line, which carries both `23-row` and `2,341`: so withdrawal 2
is search-found, while the surviving question, its answer and the raw-store statement are not.

Three sentences not to write, each false and each written in an earlier draft:
- that two of the five withdrawals are unreachable — only withdrawal 1 has an unreachable part, and
  its `:81` and `:93` the search returns;
- that gap §3's surviving lines are unreachable — the scan-figures row `:84-88` contains `:87`,
  which the search does return;
- that no part of census §4 is reachable — `:122` is.

A line the search cannot reach is listed, never claimed as found.

### 1.3 Banners

**Form.** One `> ` blockquote per banner, placed after the title and **before the run line**,
opening `> **Correction (<date>).**`. A document that already carries a banner gets a second
blockquote after the first, **separated by one blank line** — without it Markdown merges the two
into a single blockquote. Where a banner carries more than one correction, give a one-line preamble
naming how many and on what, then open each with its label on its own line (`> **2,341.**`,
`> **W6.**`, `> **W7.**`), separate the labelled blocks with a bare `>` line, use `> - ` for
sub-points, and close with *Other homes, not edited* as an italic run-in on its own `> ` line.
Follow `walk/CHECKS-two-route-recovery.md:3-14` for voice and length.

**Two rules for every banner.** Read R13's answer off `bzk/audit.py` and off the documents
themselves before writing any banner; the rules are written to hold for all six documents, so no
per-document exception is needed.

- **Rule 1 — no banner writes the string `diagnose_round<N>.py` at all**, with or without a
  directory, anywhere, including in *Other homes, not edited*. Cite such a script as "round N's
  script, line L"; a committed log as "round N's log, line L"; and
  `notes/scripts/diagnose_s1_provenance.py` as "the S1 provenance script, line 7".
  *The mechanism, stated correctly:* the guard's pattern is
  `_SCRIPT = re.compile(r"diagnose_round\d+[a-z]?\.py")` (`tests/test_audit.py:930`), which matches
  the **filename**, path or not — so "by path" is not the test and a bare filename trips it just as
  well. `_misattributed` (`tests/test_audit.py:951-968`) does **not** compare the home's scripts
  against the entries' in the direction a reader expects: 3b tests `named <= home_set`, the
  entries' scripts being a subset of the document's, so adding a name to a banner only grows
  `home_set` and 3b never fires. The live trigger is **3c**:
  `len(home_set) > 1 and entry.script_anchor is None`. A banner that introduces a second script
  name into a **single-script home** makes `len(home_set) > 1` while its entries carry no
  `script_anchor`, and every entry of that home fails as `attribution`. Four of the six are
  single-script homes and the rule bites on each: collateral, census, ceiling-and-floor and
  ceiling-survives. On draws-and-threshold the test would **not** fire — it already names two
  scripts and its entries carry `script_anchor`s, so 3d and 3e are reached and pass for every
  script now in `notes/scripts/` — and on gap-and-protein-grain it cannot fire at all, because that
  document is the home of no entry. The rule is kept across all six, and extended to
  `diagnose_s1_provenance.py`, which the pattern does not match, so that there is one form
  everywhere and no builder has to compute `home_set`. **A corollary: re-naming a document's own
  script in its own banner would also be harmless, since `home_set` is a set — and is still not
  done.**
- **Rule 2 — no banner contains a `home_anchor` of its own document, quoted or not, bolded or
  bare.** The reason is that direction 2 checks only that `home_anchor` **occurs** in the home text
  (`tests/test_audit.py:1006`, `entry.home_anchor not in home_text`): a banner repeating an anchor
  keeps the check green after the body's own occurrence is deleted or reflowed, so it **masks** real
  drift rather than failing. **Rule 2 is unguarded by construction** — its purpose is to stop a
  check from passing, so no test can fire either way and only reading catches a violation.
  Extract each document's anchors from the live map — do not work from a list in this prompt — and
  check the banner against them as raw substrings. **Four of the fourteen anchors carry bold and ten
  are bare**, so "give figures without their bold" is not sufficient protection. Two traps in
  particular:
  - **`9 of 791 claims`** is a ceiling-survives anchor, occurring once in the body at `:55`. Banner
    6 is told below to call §4's structural-discordance row unaffected. §4's row reads
    "**1.1%** (9 of 791)", which is not the anchor — but a banner that names the row by the figure
    "9 of 791 claims" lands on it. **Name that row by description only.**
  - **`**13.7%** (103 of 751)`** is also a ceiling-survives anchor. Banner 6 is told to call the
    two-sense caveat on the family-wide floor unaffected, while banner 5 — on a different
    document — writes "reports 103 of 751". **Banner 6 must name the family-wide floor by
    description, never by its figure-and-fraction**, and must not reproduce ceiling-survives' two
    support-count cells either.

**What each banner says.** Name each claim by its wording, not by line. Give the successor and the
ground, by the ground's name. Point to the record where one exists.

1. **`walk/CHECKS-collateral-and-pkm.md`** (second banner): withdrawal 1, with its three parts on
   their two grounds as §1.2 assigns them — the table's label on *the misnamed reading*; the
   heading's "different unit" and the not-recoverable inference on *the unit inference*; the
   *Reading*, through "on the other deposit,", on *the unit inference* — and the title's "2,341
   ruled out". The §3 table's "rows in the table" label is over the 2,318 rows left after the
   reverse decoys. §5's "the paper's own peptide-count constraint" is listed among things tested and
   exhausted, and the constraint is in fact met **as a row count**. The PXD026748 note from "where
   expanded rows reproduced its stated 2,143 exactly", §5's remaining-routes list, and every count
   are unaffected. Pointer to `walk/CORRECTION-PXD018299-2341.md`.
   *Other homes, not edited.* The execution records §1.2 lists — rounds 11, 13, 14 and 15's scripts
   and logs, and the S1 provenance script — in the citation forms rule 1 gives; and FINDINGS §8,
   which is edited.
2. **`walk/CHECKS-census.md`** (second banner): withdrawal 3 on *the axis inference* — with its two
   further defects, the *superseded* misclassification and the misquote of collateral §3 — and
   withdrawal 2 on *the misnamed reading*, which is W11 at its root. §3's "all rows" label is over
   the same 2,318. §3's arithmetic placing the paper's 2,341 between two peptide-id readings is true
   as arithmetic and is the premise of withdrawal 3; it is named here and not edited. §3's *Also narrowed*
   paragraph stands whole — the site-keyed mapping unaffected, and the loose-usage reading one the
   successor is **consistent with** rather than confirming.
   §4's raw-store statement is unaffected, and matters more now: the row-count match does not
   establish that the deposited table is the one analysed. Pointer to the record.
   *Other homes, not edited.* As banner 1; and FINDINGS §8.
3. **`walk/CHECKS-gap-and-protein-grain.md`** (its first banner), three corrections in one banner:
   - **2,341.** Withdrawal 4 on *the axis inference*, bounded on `:91` as §1.2 specifies. The scan's
     figures and its insensitivity finding stand as counts and properties of distinct
     modified-peptide ids, and so do its sentences read on that axis; what is withdrawn is the
     inference about the paper's stated count. Pointer to the record.
   - **W6.** Two sentences of §1's *Readings* go, and one is qualified.
     - "**Selection adds almost nothing**", and "The concern that the 43 are a selected class …
       turns out not to bite", are **withdrawn: false as stated, because the reasoning was
       defective** — they report as found what was not tested. The simulation conditioned on
       clearing the weakest published fold change; the published claims were selected by being
       called, on q, which was not simulated.
     - **What remains true on the axis simulated**, stated as explicitly as the 2,341 correction
       states its axis: under the conditioning that *was* run — a fold-change floor — the shift
       from +1.007 to +1.047 log2 is indeed small, and that measurement stands. What does not
       follow is the unqualified claim about selection, or the conclusion that the gap is downshift
       arithmetic rather than a selection artefact.
     - **Successor:** under selection on a fold-change floor, selection moves the simulated median
       gap from +1.007 to +1.047 log2; selection on q was not simulated.
     - **§1's first reading is qualified, not unaffected.** "Observation and prediction agree to
       about 0.01 log2 units" compares the observed +1.055 with the fold-change-conditioned
       +1.047 — a conditioning that 8,296 of 8,600 simulated draws cleared (round 15's log, line
       9). Against the unconditional +1.007 the difference is 0.048. It stands as a comparison
       with that simulation only.
   - **W7.** §2's claim that MOESM5's values "are log2 ratios despite an 'LFQ intensity' header" —
     which begins "Its values" on `:72` and continues on `:73`, so quote it across the break — is
     **withdrawn**, not because a ratio reading has been disproved but because the sentence states
     as found what the same paragraph calls unknown, and a claim asserted at a confidence its
     measurement had not reached is false as stated. The ground is **the reasoning was defective**.
     **Successor:** unknown. What was measured: MOESM5's values lie a median 26.6 below log2 of the
     deposited `proteinGroups` **LFQ** intensities, over 1,556 cells (round 15c's log), so they are
     not the deposit's log2 LFQ intensities; and the two ratio-shaped readings tested, minus the
     row mean and minus the column median, put only 0.3% and 0.1% of cells within 0.01. A ratio to
     a reference the raw store does not hold remains untested. The 17 unmatched claims and the
     protein census's own figures are unaffected.
   - *Other homes, not edited.* For W6: round 16's downshift band
     (`walk/CHECKS-two-route-recovery.md` §1, and through it FINDINGS §2's second route) compares
     the same selected observation with unconditional simulations — round 16's script, lines
     107-124, apply no conditioning. **It is recorded here as the same unexamined limitation and
     is not re-examined**: no figure of that document or of FINDINGS §2 moves in this prompt.
     For W7: the MOESM5 row of `walk/CHECKS-draws-and-threshold.md` §6 (banner 4) — **name it by
     description, not by line**: its `32b6ead` key `:119` goes stale the moment banner 4 lands, and
     §1.3 asks banners to name claims by wording. And round 15c's script, line 8, whose wording is
     "log2 RATIOS" in capitals. For 2,341: the execution records as in banner 1.
4. **`walk/CHECKS-draws-and-threshold.md`** (its first banner): **W7**, the §6 table's MOESM5 row,
   "values are log2 ratios, not intensities", withdrawn on the same ground with the same successor.
   **Do not restate the measurement here** (`CLAUDE.md:40`): point to
   `walk/CHECKS-gap-and-protein-grain.md` §2, which holds it. **Do not point to the record for it**
   — the record covers the 2,341 withdrawals only and does not carry W7's measurement. §6's own incidental
   observation that "MOESM5's header disagrees with its content" — which runs across `:123-124` — is
   **unaffected, and is now supported** by that measurement. Neither the two unopened supplements'
   contents nor the threshold-and-population conclusion changes.
   *Other homes, not edited.* `walk/CHECKS-gap-and-protein-grain.md` §2, and round 15c's script,
   line 8.
5. **`walk/CHECKS-ceiling-and-floor.md`** (its first banner): **R1**, two classifications on one
   figure.
   - The figure, 156 of 751 claims unstable under both rules, is **superseded** by
     `walk/CHECKS-ceiling-survives.md` §4, which takes the floor across the whole rule family and
     reports 103 of 751. The reason is given there, not in this document's own words: §4 states the
     round-9 figure "was an intersection over two points of the family rather than the whole of
     it". The computation was correct under that two-point choice.
   - The claim built on it, "**20.8% is a floor no choice of convention removes**", is
     **withdrawn: false as stated, because the reasoning was defective**: a choice of convention
     does remove it — taking the whole family rather than two of its points lowers the floor.
     Successor: the family-wide floor as `walk/CHECKS-ceiling-survives.md` §4 gives it, with its
     two-sense caveat.
   - *Other homes, not edited.* §5's sentence stating what the evidence supports, which ends "with
     a floor of 20.8%" — below this banner, named here, not edited.
6. **`walk/CHECKS-ceiling-survives.md`** (its first banner): **R1.**
   - The rank-crossing figure, 247 of 751 claims, is **superseded** by
     `walk/CHECKS-draws-and-threshold.md` §5, which gives two reasons: the figure inherited the
     rule through its reference point, **and** it used a ranking over both directions while the cut
     counted only one. Successor: the rank-spread distribution itself, as that §5 gives it, with
     the crossing share quotable only at the documented rule's calling rate.
     **The label is the source's, kept knowingly.** Draws §5 writes "**Superseded.**" The second
     reason — a ranking over both directions against a one-directional cut — would support
     **withdrawn** under the vocabulary, since it is a defect in the instrument rather than a
     disfavoured choice. This banner keeps draws §5's own classification rather than reclassifying
     a figure in a document it does not edit, and says so in one sentence.
   - Its justification, "needs no rule, no s0, no population argument", and the reading "Rank
     movement is the measure that survives every unresolved question about the convention", are
     **withdrawn: false as stated, because the reasoning was defective**: the figure inherited the
     rule through its reference point, so it was not rule-free. Successor: the rank-spread
     distribution, as `walk/CHECKS-draws-and-threshold.md` §5 gives it.
   - §4's structural-discordance row and its documented-rule row are unaffected, and so is the
     two-sense caveat on the family-wide floor. **Name all three by description only**, never by
     figure — rule 2's two traps are both in this document.
   - *Other homes, not edited.* Round 10's script, lines 23 and 165, which carry the same
     justification as an execution record. Quote each from the file, not from this banner: line 165
     reads "no s0 **threshold**", and line 23 reads "no rule, no s0 **and** no population argument".

**Do not edit any of the six CHECKS documents below its banners.** `walk/FINDINGS.md` has no banner
and is edited at §1.4.

### 1.4 `walk/FINDINGS.md`

**Apply §8 first, then the lead.** Both ranges below are measured at `32b6ead`. The lead
replacement is 9 lines for 8, so applying it first would shift §8 down by one and the `:180-183`
replacement would consume the blank line plus the first three lines of the paragraph, orphaning its
last line — while the suite stayed green, because nothing tests §8's prose (no `RECEIPT_MAP` entry
has `section` 8; all are 5 or 6). Bottom-up avoids the hazard. Net shift: `walk/FINDINGS.md` **+2**,
one line at each edit.

**§8 (`:171`, `:180-183`).**
- The heading at `:171` becomes `## 8. A negative that cost a real test, and a count that reproduces`.
- The first paragraph (the MOESM5 table) is unchanged.
- Replace `:180-183` with:

```
**The paper's stated count of 2,341 equals the deposited site table's row
count**, before any filter, reverse decoys and contaminants included. Whether
the paper's word "peptides" denotes these site rows is not settled here. An
earlier version of this section reported the count as unreproducible
(`walk/CORRECTION-PXD018299-2341.md`).
```

The narration of the withdrawn claim stays out: result, limit, pointer — as `cfb1aa7` did for §5,
and as this document's own "What goes in this document" requires.

**The lead, `:3-10` (R9).** Replace `:3-10` with exactly:

```
**Three deposits, reconstructed from their raw data: PXD018299 (Pinto-Fernández
et al., *Br J Cancer* 2021), PXD026748 (Munnur et al., *Nat Immunol* 2021) and,
in §10a, PXD032267 (Yerra et al., *J Clin Invest* 2023).**

Neither of the first two papers states how it imputed its missing values. On
both, a substantial minority of published claims sit close enough to the
significance line that the imputation's random draw decides them. On the first
— the only one of the two that published its post-imputation matrix — something
stronger can be measured: what the published numbers themselves are made of.
```

These replace `:3-10` exactly. Change nothing else in the lead.

**Check before committing**, against the live sources rather than this prompt:
- the new text adds **no** `RECEIPT_MAP` `findings_anchor`, and duplicates none — direction 1
  requires each anchor to occur exactly once in FINDINGS, in its entry's section;
- `mislabels_791` (`tests/test_audit.py:1590-1598`) returns `[]`. It has **two** triggers: a line
  containing "all published claims", **and** a line with "published claim(s)" beside the number
  791. The new text must trip neither;
- `check_receipts(RECEIPT_MAP, REPO_ROOT)` returns `[]`;
- `git grep -n "2,341" -- walk/FINDINGS.md` now returns one line.

### 1.5 No code, no tests

This prompt changes no file under `bzk/` or `tests/`. The suite and `sweep()` must read as in
§0(a) after the build.

---

## 2. Out of scope. Do not touch.

- Every document not named in §1, and the six CHECKS documents below their banners.
- `HYPOTHESIS.md` — including `:310`, whose peptide-grain inference this prompt lists and does not
  revise — every PREREG and RESULT document, `ROADMAP.md`, `HANDOFF.md`, `decisions/`.
- `walk/CHECKS-two-route-recovery.md` and FINDINGS §2. W6's limitation reaches them and is
  **recorded** in banner 3; nothing there is re-run or edited in this prompt.
- `walk/CORRECTION-PXD018299-H10-headline.md`.
- `notes/logs/`, `notes/scripts/`, and every `notes/` reviewer record.
- `notes/REVIEWER-DEFECTS.md`: the reviewer closes **W6, W7, W11, R1 and R9**. **W5 is not closed
  by this build**: its assumption moves from implicit in census §4 to explicitly stated as a named
  limit of the successor, and stays open. The closure table (§3 item 6) states exactly that for W5
  and no more; whether an item worded as "the census's *implicit* … assumption" closes when the
  assumption stops being implicit is the reviewer's call, not the build's.
- W12 and every other register item.

**Stale line keys to raise, not to edit.** Every banner shifts the lines below it, and FINDINGS'
two edits shift it by `+2`, so every line-keyed reference into the seven touched documents goes
stale. All of it is register item R5, the prose mirror; most of it this build creates. **This is not
a closed list — find them with a search and report whatever it returns**, because an enumeration
here would be short the same way ADR-0041's V8 was:

```
grep -rnoE "(CHECKS-(collateral-and-pkm|census|gap-and-protein-grain|draws-and-threshold|ceiling-and-floor|ceiling-survives)|FINDINGS)(\.md)?:[0-9]+([-–][0-9]+)?" \
  notes/ walk/ decisions/ *.md
```

Note the **en dash**: `notes/REVIEWER-DEFECTS.md` writes ranges as `:107–108`, which a hyphen
pattern misses. Exclude this prompt's own file and the hits inside the documents being edited where
they point at themselves. For each hit, give the old line and the new one.

Five are known in advance and must appear in the report whatever the search returns:
1. **`notes/REVIEWER-DEFECTS.md`'s W5 and W11** cite `CHECKS-census.md:107–108` and record the file
   as unchanged, under the rule at `:17-18` that "unchanged" means the original references still
   hold. The 2026-11-15 banner inserted 14 lines, so those lines are at `:121-122` at `32b6ead` —
   census §4, which carries both items, as this prompt reads them. **After this build's banner they
   move again**; give the `32b6ead` pair and the post-banner pair in the report, and the post-banner
   pair in the closure table.
2. **`walk/CORRECTION-PXD018299-H10-headline.md:17-22`** states the collateral and census shifts as
   16 and 14 and instructs its reader to subtract those. The banners this build adds make those the
   first banner's shift only, so that key and every line-keyed row of its closing table go stale.
   The record is out of scope here; report the new totals.
3. **`notes/REVIEWER-DEFECTS.md`'s W12** cites both `CHECKS-draws-and-threshold.md:17–19` **and**
   `FINDINGS:102` "now at `:110`" (`:46`); the first shifts when banner 4 lands and the second by
   FINDINGS' `+1` at the lead. W12 is out of scope, so nothing else will raise it. Note also that
   W2's `:118` and W8's `:184` were already one short at `32b6ead` — the live lines are `:119` and
   `:185`, moved by `cfb1aa7` — and shift again.
4. **`notes/REVIEWER-MAP-findings-5-and-6.md:89` and `:152`** both cite `FINDINGS.md:109`, the
   209-of-751 row, which becomes `:110`. That file is `RECEIPT_MAP`'s own derivation record
   (`bzk/audit.py:93-97`), so a stale key there is worse than in a handoff.

5. **R1's own register row** (`notes/REVIEWER-DEFECTS.md:86`) carries four keys into documents this
   build shifts — `CHECKS-ceiling-and-floor.md:90`, `CHECKS-ceiling-survives.md:72` and `:74-76`,
   and `CHECKS-draws-and-threshold.md:108-109`. R1 is an item being closed and §3 item 6 wants
   post-edit lines, so give all four.

`notes/REVIEWER-HANDOFF-2026-11-12.md` and `-11-15.md` carry further keys into these documents; the
search finds them.

**Two limits of the search, to state rather than work around.** It is prefixed by filename, so it
does not reach a **bare** line key — `notes/REVIEWER-DEFECTS.md`'s W2 (`:118`) and W8 (`:184`), or
the "from `:3` … by **16**" form in `walk/CORRECTION-PXD018299-H10-headline.md:17-22`. All of those
are in the known-in-advance list above, so nothing is lost; say so rather than widening the pattern
into noise. And it returns ~40 hits inside `notes/prompts/` — prompts 22, 42a, 42b, 43 and 44 —
which are historical records nobody will re-point — about 60 occurrences across those five files,
or roughly 40 distinct keys, so report the number the search prints rather than either figure:
**report them as historical and propose no fix.**
One referent to flag while reporting: `notes/REVIEWER-MAP-findings-5-and-6.md:89` cites
`FINDINGS.md:109` but its subject is the 26.5% / 210-of-791 row, which `cfb1aa7` moved to `:112`,
so the key was already pointing three lines off before this build touched anything — `:109` is
row 1, 209 of 751, and the 210-of-791 row is `:112`. The same mis-referent applies to MAP `:152`,
which follows `:151`'s 791 sentence; item 4 above describes both as citing the 209-of-751 row, which
is the key's target rather than its subject. Give each key's shift and that fact.

---

## 3. Report

Give the four-point close (`CLAUDE.md:95`). Name each check at the version it ran, with its target,
including `pytest tests/test_schema.py` run separately. Also report `check_receipts` and
`mislabels_791` on the new FINDINGS, and the `findings_anchor` uniqueness check. Then:

1. §0 as a table, every row quoted — including R13's answer, read off the live map and the
   documents: the entry count, each document's homes and anchors, each document's own
   `diagnose_round*.py` set, and whether its entries carry a `script_anchor`.
2. The new FINDINGS text and the record's *The claims withdrawn*, *What survives*, *What the
   successor does not settle* and *Completeness* sections, quoted in full. For the banners and the
   closing table: quote banners 3, 5 and 6 in full, quote the closing table in full, and summarise
   banners 1, 2 and 4 to their claims, grounds, successors, pointers and *Other homes* lists. (An earlier draft made this conditional on a 200-line budget; review builds measured the
   six banners at 179, 194 and 204 lines on successive revisions, so the branch was not worth
   leaving in.)
3. Each banner checked by reading against the two rules in §1.3: no `diagnose_round<N>.py` string;
   no `home_anchor` of its own document. State the anchors checked for, per document, as read off
   the live map. Note the header-block convention followed for the new record.
4. The completeness search: the hit count, every hit classified, the two excluded classes as counts,
   and the count of listed rows the search cannot reach, reconciled. Name any hit that fits none of
   the classes — do not invent a class for it; report it. **The same for a closing-table row that
   fits none of the six `handled` kinds: report it here rather than giving it a kind of its own.** **Also give the two derived lists the
   closing table's preamble asks for**, at post-banner numbers as the record's rows are: every line
   where a row's quoted text begins or ends part-way along it, with what claims the rest; and the
   further cited lines the search cannot reach.
5. Each of the six documents' line shift, with the first line that moved, and `walk/FINDINGS.md`'s
   two edits and its net `+2`.
6. **A closure table**: one row per register item (W6, W7, W11, R1, R9, and W5 as *recorded, open*),
   giving the register's wording, what this build produced for it, and at what post-edit line. This
   is what the reviewer closes the items against; the reviewer adds the closing commit.
7. Point 3 of the close states what this prompt leaves uncovered: W6's limitation in
   `walk/CHECKS-two-route-recovery.md` §1 and FINDINGS §2's second route, recorded and not
   re-examined — **and ask the reviewer to open a numbered register item for it, since W6 closes
   while the limitation survives in a second document with no home**; the deposit-is-the-analysed-table
   assumption (W5), recorded and open; what the paper's "peptides" denotes, unsettled;
   `HYPOTHESIS.md:310`, listed and not revised; and every stale line key the §2 search returns. None is
   machine-checkable, so none is guarded — and rule 2 is unguarded by construction. Say so.
