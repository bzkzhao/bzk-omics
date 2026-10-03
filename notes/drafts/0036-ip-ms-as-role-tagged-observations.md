# ADR-0036 — IP-MS enters as role-tagged observations; concordance is defined on an IP-vs-IP contrast; imputation is counted on the result

| | |
|---|---|
| Status | Proposed |
| Date | 2026-10-03 |
| Supersedes | `ONTOLOGY.md` §5.1's `EnrichmentObservation` headroom row (l.539) and §6.1's deferral paragraph (l.684) |
| Superseded by | — |

Drafted by the reviewer against `a74cf18`. Numbered 0036 on landing if nothing lands first.
**Every line reference below is to `a74cf18`.** `git diff 3a165a4 a74cf18 -- ONTOLOGY.md bzk/ decisions/`
is empty, so the handoff's references and these agree. Re-derive them at landing.

This record decides representation and invariants only. **It makes no `ONTOLOGY.md`, `schema.py` or
code change.** The amendments are listed under *Implied changes, described and not made*. The
concordance computation, its "measured well" rule and its predictions are a separate
pre-registration (handoff §7.3) and are not decided here.

---

## Context

**Option B was decided on 2026-10-02 (handoff §2.1) with a definition that no public deposit
instantiates.** It defined "enriched" as a `DifferentialResult` on an IP-vs-control `Contrast`. The
survey (`walk/SURVEY-public-IP-tables.md`, `a74cf18`) found:

- PXD018299's interactome has no control. It has 4 conditions × 3 IPs (§2).
- PXD055843 S3 has one no-antibody bead control per condition. Its quantitative block is fully
  populated, so measured and imputed values cannot be told apart (§7).

**Both papers define concordance on IP against IP across conditions. Neither compares IP against a
control.** Read for this record. The citations are to the papers, and the wording below is a
paraphrase:

- **PXD018299** (Pinto-Fernández et al., *Br J Cancer* 2021, doi:10.1038/s41416-020-01167-y).
  - The methods describe the ISG15 IP as anti-ISG15 on protein G, with no IgG or bead-only arm.
  - The results report 312 proteins interacting with ISG15 in a USP18-dependent manner (KO+IFN vs
    WT+IFN, Data Table S3). 110 of them overlap with the GlyGly result.
  - The paper notes that ISGylated proteins barely accumulate in WT cells under IFN. That makes
    WT+IFN a comparator with few conjugates. It is a biological comparator, not a technical control.
- **PXD055843** (Mukhopadhyay et al., preprint doi:10.1101/2024.09.06.611391; published as
  doi:10.1038/s41467-026-74490-2).
  - The methods state that no-antibody samples were the negative control. No reported analysis
    uses them.
  - Concordance is siUSP24+IFN vs siC+IFN in both the ISG15 IP and the GG-peptidome. 11 proteins
    pass a fold threshold in both, and 7 of the 11 are significant.
  - The paper calls all 4,410 S3 proteins "enriched in the ISG15 interactome", meaning recovered
    by the IP.

So `isg15_interactome_concordance` (l.670) is marked † as drawn from a strategy that is IP-vs-IP.
§2.1's definition would make the platform unable to reproduce the source of its own basis.

---

## Decisions

### D1. IP-MS data are `ProteinObservation`s. No new observation type.

This restates handoff §2.1, which stands. IP intensities attach to `ProteinObservation`s reported
by an IP dataset. **Supersedes l.539** (the headroom row) and **l.684** (the deferral paragraph,
replaced by D7's lift conditions).

### D2. `Sample` gains `role` (identifying, required) and `bait` (identifying, determined by `role`).

**`role` records what was done to the material, not what the sample means in a comparison.**

| `role` | Meaning | In public data |
|---|---|---|
| `lysate` | Material measured as drawn from the lysate, including peptide-level enrichment that belongs to the modality (anti-K-ε-GG) | Every existing `Sample` |
| `ip` | Protein-level affinity purification against `bait` | PXD018299 interactome (12), PXD055843 S3 Sets 1–3 (12) |
| `no_antibody_control` | Beads processed as an `ip` with the antibody omitted | PXD055843 S3 (4) |

The enum is closed. Input and isotype-IgG controls are absent from the public data and are not
added here. Adding one later is a visible commit.

**Why "control" is not a role value.** WT+IFN in PXD018299 is an `ip` sample that serves as the
comparator in one contrast and as an ordinary arm in another. Only a technical control is a control
by construction. Comparative meaning is derived from the contrast (D4).

**Why `role` is identifying.** PXD055843 S3's bead column and its Set-*n* IP for the same condition
would otherwise differ only in `replicate`. That is a fragile separator, and it fails outright if
`replicate` is ever curated identically.

**`bait`** is the CURIE of the protein the antibody targets (`uniprot:P05161` for ISG15).

- Its absence is **determined by `role`**: NULL unless `role = 'ip'`.
- The antibody (clone or catalogue number) is recorded as a non-identifying `antibody` field. The
  methods state it in both papers (Boston Biochem A-380; Invitrogen 7H29L24). But it is
  conditionally reported in general, and ADR-0021 forbids a contingent null on an identifying field.

**Re-mint cost.** Making `role` identifying re-mints every `Sample` id. Existing samples take
`role = 'lysate'` explicitly, never a null default. **No node anchors on `Sample`** (`schema.py`
anchors, l.230–341), so nothing downstream moves. The count is measured at landing.

### D3. `Experiment.modality` gains `ip_ms`.

Each IP run is its own `Experiment`. Its samples are therefore separated from a same-condition
lysate sample by the existing `PERFORMED_ON` anchor (`schema.py:258`).

`role ∈ {ip, no_antibody_control}` if and only if `modality = 'ip_ms'`. An input control would
break this, and that is the visible commit that relaxes it.

### D4. `Contrast` gains `numerator_role` and `denominator_role` (identifying, required).

**This closes a collision that option 1 would otherwise create on its first write.**

- `Contrast` identity is `(numerator, denominator)` with no anchor (`schema.py:274`; ONTOLOGY l.119).
- PXD018299's diGly contrast is `'USP18-/- + IFN'` / `'WT + IFN'` (`curation_PXD018299.json:34–35`).
- An IP-vs-IP contrast curated in the same convention would mint the same id. `RESULT_IN_CONTRAST`
  could then no longer separate IP results from site results.

**Why role fields, not ADR-0027's `Experiment` anchor.**

- Role fields fix this collision directly.
- They also admit an IP-vs-control contrast whose arms share a condition string. The anchor
  cannot: both arms would sit in one `ip_ms` experiment with identical strings.
- The anchor stays the answer to §11 Q1's cross-cell-line collision. That is a separate question,
  not taken up here.

**Contrast kinds**, derived from the role pair and never stored:

| Pair | Kind | Permitted |
|---|---|---|
| (`lysate`, `lysate`) | abundance or site | yes (every existing contrast) |
| (`ip`, `ip`) | differential association | yes, both arms the same `bait` |
| (`ip`, `no_antibody_control`) | background enrichment | yes |
| any other | — | no |

**Re-mint cost.** `DifferentialResult` anchors on `Contrast` (`schema.py:335`), so every result id
moves, as under ADR-0025. That was affordable because ids are derived on demand and cited by
nothing outside the graph. Both premises are re-measured at landing, not inherited.

### D5. New invariant I22 — a contrast's arms are role-consistent.

Every sample whose values enter an arm of a contrast has that arm's declared role. The pair is in
D4's permitted set. Both `ip` arms share one `bait`.

**Enforced at the producer, not in the graph, and this is stated so a pass is not misread.**
`Contrast` has no edge to `Sample`. Arms are bound to columns upstream: `differential.py` takes
condition strings at l.39–40 and builds the node at l.119. So the check runs where columns are bound:

- the differential writer;
- the Perseus adapter.

A graph-checkable form waits on a `Contrast`–`Sample` linkage. That is named here and not built.

**This is the "machine-checkable guard" handoff §2.1 accepted as option B's cost.**

### D6. `isg15_interactome_concordance` is defined on a differential-association contrast, within one deposit.

l.670's meaning changes from *"parent protein also enriched in anti-ISG15 IP-MS"* to:

> the parent protein's ISG15-IP recovery rises in an (`ip`, `ip`) contrast whose condition strings
> match the (`lysate`, `lysate`) contrast in which the site rises, with both experiments under one
> `Project`.

- Permitted confidence stays `probable`.
- **Cross-deposit pairing is not this basis.** The voided R1 join is the reason (handoff §2.3).
- **Handoff §2.3 is corrected here.** It treats PXD055843 as cross-deposit only. Its S2 GG-peptidome
  makes a within-deposit pairing available, and that is the pairing the paper itself reports.

**Background enrichment is a different claim** (the protein is recovered above a no-antibody
background at all). If a deposit supports it with replicated controls, it gets its own basis value.
It does not get a widened meaning of this one, because a widened meaning would silently change what
existing assignments assert.

### D7. I4 is widened to (`ip`, `ip`) results; both public deposits enter `not_applied`.

I4 (l.886) is scoped to site results.

**The abundance confound is named by the anchor paper itself.** It attributes part of the
accumulation of modified ISGs to USP18's role in suppressing late IFN signalling. An IP-vs-IP
difference for ISG-encoded proteins inherits that confound.

So every `DifferentialResult` in an (`ip`, `ip`) contrast declares `protein_adjusted`, exactly as a
site result does.

- `not_applied` is labelled *abundance-uncorrected* in every view and export.
- The id cost is nil. `ADJUSTED_BY` has been an anchor on every result since ADR-0025, and
  `protein_adjusted` is already set on protein results (`perseus.py:545`).

**Neither public deposit can be corrected today.**

- PXD018299's matching proteome has 14 columns that no curation record keys to a `Sample`
  (`ROADMAP.md` l.68).
- PXD055843's S1 is not ingested.

**Concordance between two `not_applied` legs is permitted at `probable`, with a mandatory label.**
The assignment's rationale names both legs' adjustment states. Views say *both legs
abundance-uncorrected*. Both papers drew their concordance this way, and refusing it would refuse
every public instance.

**This is the decision in this record most open to challenge.** Where abundance rises, two
uncorrected legs share one confound, so for those proteins agreement is partly the confound counted
twice.

### D8. Imputation is counted on the result, per arm (G2), and whole-arm imputation is flagged (G1).

**G2.** `SiteObservation.n_imputed` (l.428, l.849) counts on the observation. But imputation belongs
to the `Analysis` (§6.5). So one observation imputed differently by two analyses cannot be
represented, and `ProteinObservation` has no count at all.

`DifferentialResult` gains four non-identifying `INT64` fields:

- `n_values_numerator`
- `n_values_denominator`
- `n_imputed_numerator`
- `n_imputed_denominator`

**The fields are absent when the mask is unrecoverable.** That absence is **determined by the
`Analysis`'s `parameters_observed`**: NULL where `false` and the export carries no mask.

- ADR-0034 (Proposed) reached the same reading for `Imputation`'s parameters. This record stands on
  §3's own test for `determined`, not on ADR-0034's acceptance.
- **Where the counts are NULL, the flag below is undeterminable. It is shown as such and never as
  `false`.** That is `query/graph.py:75–80`'s convention, kept.

`SiteObservation.n_imputed` is superseded. It is removed in the code step, not here.

**G1.** *Substantially imputed* (l.853, l.962) is flagged when **either** condition holds:

- (a) more than half of the result's values are generated; or
- (b) **either arm is entirely generated.**

(b) catches the cases (a) misses:

- the handoff's 2-vs-2 case (2 of 4);
- PXD018299's likely IP pattern, where a protein ISGylated only in KO is absent from every WT+IFN
  IP (3 of 6);
- a single imputed bead arm (1 of 4).

**The flag is not evaluated anywhere today** (`query/graph.py:75–80`). This decision gives it a
denominator for the first time.

---

## Lift conditions for the concordance basis (replacing l.684)

l.684 is prose. Nothing in `bzk/` or `tests/` names `isg15_interactome_concordance` (grep, `a74cf18`),
so the block was never machine-enforced. **It lifts only when all four hold**:

1. I22 is enforced at both producers.
2. D8's per-arm counts are written by every producer of (`ip`, `ip`) results.
3. A guard refuses the basis on any pairing that fails D6, the same-`Project` matched-strings rule.
4. The pre-registration of handoff §7.3 is committed.

---

## Consequences

- **Two within-deposit concordance cases instead of none.**
  - PXD018299: platform-imputed, so the mask is known and all four of handoff §5's outcome rows are
    available.
  - PXD055843: external results, mask unknown, so only the agreement row is available, and the
    result says so.
- **Ids move for `Sample` (D2) and for `Contrast` and every `DifferentialResult` (D4).**
  `ModifierAssignment` does not anchor on either (`schema.py:303–311`).
- **I4 gains a display obligation**: *abundance-uncorrected*, beside the existing
  *stoichiometry-uncorrected*.
- **Representation open question, settled before the concordance writer and not here:** how a
  `ModifierAssignment` cites the two results it rests on. `ASSIGNMENT_SUPPORTED_BY` names an
  `Analysis`, not a result. And a site can match more than one IP protein group, given the 72–77%
  multi-candidate rate at protein grain (l.961). So the citation may need to be identifying, and the
  single-valued anchor rule (§3) constrains that.

---

## Implied changes, described and not made

Line numbers are at `a74cf18`.

**`ONTOLOGY.md`**

- l.115 — `Sample` identity row: add `role`, `bait`.
- §3 absence table, after l.146 — `Sample.bait`, determined by `role`. `Sample.antibody` is
  non-identifying; classify its absence per §3.
- l.117 — `SiteObservation` non-identifying list: drop `n_imputed`, marked superseded.
- l.119 — `Contrast` identity row: add `numerator_role`, `denominator_role`.
- l.125 — `DifferentialResult` non-identifying list: add the four counts. Absence row as D8.
- l.380 — modality comment: add `'ip_ms'`.
- l.384–398 — `Sample` DDL: add `role`, `bait`, `antibody`.
- l.428 — `SiteObservation.n_imputed`: superseded.
- l.450–453 — `Contrast` DDL: add the two role columns.
- l.455–464 — `DifferentialResult` DDL: add the four counts.
- l.539 — strike the headroom row and point to this record.
- l.670 — the basis row's meaning, per D6.
- l.684 — replace with the lift conditions above.
- l.849, l.853 — §6.5: the count moves to the result; rule (b) is added.
- l.886 — I4 widened (D7).
- l.962 — I15's flag, rule (b) added.
- §8 — mint I22 (D5).
- l.1061 — the extension-cost table names `EnrichmentObservation` as its example. Keep the
  illustration, but change the example to `PeptideObservation`, so the table does not name a type
  this record declines to build.

**Other homes naming `EnrichmentObservation`.** The handoff named two homes. There are six, plus a
historical ADR:

- `ROADMAP.md` l.117 and l.139;
- `HANDOFF.md` l.1326;
- ADR-0013 l.18 and l.72. This one is accepted and historical, so it is not edited. A pointer to
  this record is the most that changes.

**`bzk/ontology/schema.py`**

- `Sample` identity (l.246–259): add `role`, `bait`.
- `Contrast` identity (l.274): add the two role fields.
- `ABSENCE`: add the new determined row(s).
- DDL columns, including l.450's `n_imputed`, which is removed.
- `tests/test_schema.py` compares `ABSENCE` with §3, so both homes move together.

**`n_imputed` consumers.** A plain grep over-reports, because `row_carries_an_imputed_cell`
contains the substring. Enumerate with a word boundary at landing.

---

## Alternatives considered

- **Option 2 — "enriched" means IP-vs-control only.** Rejected.
  - It yields no concordance on any public deposit.
  - It cannot reproduce the † source.
  - Its only instance is a single bead arm that is probably imputed.
  - Extending it later would widen the meaning of an existing basis value.
- **Option 3 — defer enrichment and do G2 and G3 first.** Adopted as sequencing, not as an
  alternative. D2–D5 and D8 land before any IP result is written.
- **`Experiment` anchor on `Contrast` instead of role fields.** Rejected for this purpose (D4). It
  remains the candidate for §11 Q1.
- **A `control` role value.** Rejected (D2). A biological comparator is a contrast-level meaning.
