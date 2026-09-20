# HYPOTHESIS — claim durability in PTM site proteomics

**Version:** 7, superseding v6. It adds D7 (draw instability) as an
**exploratory** class, found after the fact on `PXD026748`. It registers H10 on
the anchor as D7's first registered test, before any anchor computation. It
records that the deposits are not independent, and it requires a comparability
criterion for H4 before anything is counted. H5c and H9p are unchanged.
**Status:** registered. Amendments are recorded with their trigger so the change
is auditable; v1 to v6 are superseded, not silently replaced. v3 was a working
draft and was never formally published (`notes/landing/LANDING-HYPOTHESIS-v4.md`).

**What this document is:** the hypotheses, the definitions they depend on, the
registered expectations and their directions, and the conditions under which the
thesis fails. It governs what data get generated and what counts as an instance.

**What this document is not:** a home for measured numbers. Under the
single-source rule, figures live in their dated homes. Where a figure below is
the *trigger* for a registered decision, it is named with its home so the
decision can be audited; it is not restated anywhere else.

---

## 0. Changelog from v6 *(this version)*

**Trigger.** A descriptive breakdown of H9s's family, computed from the committed
fixture after the verdict was recorded (`walk/RESULT-PXD026748-reconstruction.md`,
the unregistered section, and `notes/scripts/describe_reconstruction.py`). Seed
variation alone changes some claims' support **in every one of the 18 parameter
cells**, 53 to 162 of 288 claims per cell. An external review
(`notes/reports/REVIEW-seed-lability.md`, 2026-09-20, committed unchanged
beside this version) argued this is a class distinct from
D5.

1. **D7, draw instability, is added as an exploratory class** (§4). It was
   found after the fact, so `PXD026748` is its discovery deposit and **not a
   confirmation of it**.
2. **H10 is registered** (§5). It is D7's first registered test, on the anchor,
   before any anchor computation. It carries the primary-readout rule and the
   conditional denominator.
3. **The deposits are not independent** (§8 and §9). Both publications share
   authors. A third, unaffiliated deposit becomes the top gate.
4. **H4 gains a registered requirement** (§5): a comparability criterion,
   specified in a later amendment **before** any D3 instance is counted.
5. **Corrections to the review, recorded so they are not re-introduced:**
   - `PXD026748`'s publication states **no** imputation width, downshift, scope
     or seed. The default cell is the reviewer's assumption, not *"the
     publication's own settings"*.
   - D7 is therefore **not** *"measured at the publication's settings"* and
     **not** *"free of any reporting omission"*: the seed and the parameters were
     omitted.
   - D7's claim to distinctness rests on something else: lability in every
     cell, and the fact that recording a seed would make the claim set
     reproducible without making it stable.
   - The review's proposed v7 removed the full text of D1 to D6 and of H2, H3,
     H6, H7, H8, H9, H9s, H5c and H9p, and altered H5c's registered design. It
     was **not adopted**, and no registered text is removed here.
6. **The novelty of D7 is unverified.** Multiple imputation for proteomics
   differential analysis exists (e.g. mi4p). A literature check is required
   before any novelty claim is written (§11).

**What did not change.** Every other class, every registered hypothesis's text
(H5c and H9p included), every measured figure, and the kill conditions other
than the added one.

---

## 0-v6. Changelog from v5 *(carried, unchanged)*

**Two triggers.**
- **H9s was measured.** The verdict is *extends D5 to imputation alone*. Home:
  `walk/RESULT-PXD026748-reconstruction.md` and
  `tests/fixtures/pxd026748_reconstruction.json`.
- **Unused columns were found.** The publication's Supplementary Table 1 carries
  columns nothing has used yet. One of them flags each ISG15 claim that an
  independent *in vivo* ISGylome also reported. The reviewer counted that
  column's flags (128 of the 276 ISG15 claims) and **deliberately did not join
  them to the reconstruction's durability**, so that the join can be registered
  before anyone sees it.

1. **H9s's status is recorded,** with its home, under H9s in §5 and in §6.
2. **D5 gains a v6 note.** The anchor's *test-choice* mechanism did not recur on
   `PXD026748`. There the stated test reproduces the publication's own
   statistics exactly, measured on imputation-free proteins. The class holds
   through a different unstated step. See §4, D5.
3. **H5c is registered: corroboration by citation, against D5 durability.** It
   is **not C0**, and §4's C0 entry says why.
4. **H9p is registered: D5 at protein grain,** on the same deposit's shotgun arm.
   It tests whether imputation-underdetermination is particular to site data.
5. **§6 gains exposure rows** for H5c and H9p.

**What did not change.** Every class, every other hypothesis, the kill
conditions, and C0's vacancy.

---

## 0-bis. Changelog from v4 *(carried, unchanged)*

**One trigger.** The second deposit's methods were read in full on 2026-09-20
(`notes/reports/REVIEW-ADR-0035.md`, addendum). They state the software, the
model and the selection rule, and they leave only the imputation unstated. That
makes `PXD026748` close to the deposit v4 asked for under D5 and H9: *"a deposit
whose methods specify the test fully"*. Its reconstruction is about to be
registered, and v4 says the sharp form must be registered before it is measured.

1. **H9s is registered**, H9's sharp form, stated for `PXD026748`: the family,
   the durability criterion, and both directions. See §5.
2. **§9's second-deposit gate is clarified, not moved.** It concerns ingesting
   the *publication's* imputation. An internal reconstruction that declares its
   own parameters and seeds is a different act (ADR-0034, table row 3), and it
   does not pass that gate.
3. **§6 gains the second deposit's D5 exposure row.** It is unmeasured, and the
   cascade measures it.

**What did not change.** Every class, every measured figure, every other
hypothesis, and the kill conditions.

---

## 0a. Changelog from v3 *(carried, unchanged)*

All six amendments share one trigger: the cascade (task K-b). Denominator 798,
one path, **512 recovered, 286 lost, no residual**, against an arithmetic ceiling
of 516 platform significant-up rows — so recall reaches **64.2%, four claims
short of the maximum possible**. Home: `FINDINGS` §14.

1. **The taxonomy gains an axis: locus.** Every class is now marked **latent** —
   present in the published record, needing no reanalyst — or **introduced** —
   generated by the act of reconstruction. Four of v3's instances move to
   *introduced*, which makes them weaker as claims about decay and stronger as
   claims about reconstruction. The axis is the finding; see §4.
2. **D5 — analytical underdetermination, new, and it is the strongest latent
   class after D2.** The publication states permutation FDR 0.01 with s0 0.1 and
   no implementation. A reconstruction that reads the methods and picks a
   standard test (BH on Welch) finds **223 of 749 published claims fail the
   p-value, 179 of them on the p-value alone**. Both tests are defensible. The
   claim's support is a property of the test, and the test is not recoverable
   from what was published.
3. **D6 — specification divergence, new, introduced.** Rules the reconstruction
   applies and the publication did not: the 0.75 localisation cut and the
   contaminant drop, costing **36 published claims** (33 + 3).
4. **D4b relocates to latent.** The published WT arm is imputed — established by
   the cascade's control, §4 — so the generated-arm concentration is inherited
   from the published derivation path rather than introduced. This is what H6
   needed and could not previously assert.
5. **H2 amended again; H9 registered.** See §5.
6. **One kill condition partially fired.** §8's "defeat rates are low enough that
   derivation paths mostly hold" is half-true and must be stated: against
   *capacity*, the paths hold — 512 of a possible 516. The losses are real and
   concentrated in one identified mechanism. That is the smaller, better paper
   §8 anticipated, and it is the one to write.

**What did not change.** D2, D2c, H3, H7, C0's vacancy, and every measured figure
in v3. D2 is now the strongest class in the taxonomy by some distance: it is the
only one where the data changed under a published claim with no reanalyst
involved.

---

## 0b. Changelog from v2 *(carried, unchanged)*

All five amendments share one trigger: the anchor publication was read at figure
and supplementary grain for the first time. v1 and v2 reasoned from its methods
section, which is silent on both points below; its figures are not.

1. **D1's locus corrected. The paper's recovery rule is any-site.** Trigger: the
   publication retains all seven ADAR ISGylation sites (K433, K637, K763, K781,
   K798, K895, K996) in its Fig. 4c intensity plot and its Fig. 4d domain table,
   and its Fig. 2f volcano is at GlyGly-peptide grain — 2,341 peptides across
   2,172 protein groups, with the USP18-dependent set reported as 476 proteins.
   Peptides are tested; proteins are derived by mapping significant peptides
   upward. No step selects a representative site, so no representative rule
   exists to be undocumented. Grade B: inferred from published artefacts, not
   stated. **Consequence:** the largest-site rule is the *notebook's*, not the
   publication's. ADAR remains a named D1 instance, but of selection introduced
   by reanalysis rather than inherited from the published claim. The
   publication-facing form of D1 is restated in §4.
2. **D1 split into two routes, and D1b is new.** The undocumented selection that
   matters most on this deposit is not which site represents a target but which
   targets constitute the published set. See §4.
3. **The fourteen is a reconstruction, and the twelve has no published source.**
   Trigger: the publication names its ISGylome targets in prose across two
   categories — ADAR, DDX58, DDX60, DHX58, OAS1/2, EIF2AK2, IFIH1, DDX3X, DHX9,
   STAT1 for dsRNA binding and innate immunity, then PSMA7, PSMB9, PSMB10,
   PSME2, TAP1 for antigen presentation — and the first list ends *"and others"*.
   That is sixteen named with OAS1/2 split, against an explicitly open set. The
   curated fourteen is that list minus DDX3X and DHX9. No count of recovered
   targets appears anywhere in the publication. `n_expected_recovered: 12` and
   `n_expected_total: 14` therefore record a reconstruction, and the
   reconstruction step is unrecorded. Home: write-up §3.
4. **New hypothesis H8** (claim-set membership), §5. **New denominator** for
   D1b, §6.
5. **New gate: threshold parity.** The publication states permutation FDR 0.01
   with s0 0.1 for all its proteomic analyses. Both reproduction paths apply
   `adj p < 0.05` and `log₂FC > 1.0`. Those are different criteria for the same
   operation, so *recovered* on either path is not *would have been named in the
   paper*. This is grade A on the publication's side and must be settled before
   any recovery count is compared to it. See §9.

**What did not change.** D2, D3, D4, C0, and every measured figure. The four-cell
table is unaffected — it is a statement about what two pipelines do under two
rules, and every cell in it stands. What changed is which cell corresponds to the
publication, and what the fourteen in its denominator is.

---

## 0c. Changelog from v1 *(carried, unchanged)*

1. **D4 Construction reinstated as a class.** v1 demoted analytical state to a
   mechanism acting only through selection, with a reinstatement test. The test
   fired. Trigger: write-up §3 — twenty of the twenty-one significant-up rows
   producing the platform's twelve test a measured arm against a generated one,
   with no selection rule in that path. Home: `tests/fixtures/pxd018299_platform_targets.json`.
2. **The class has two routes, not one.** DDX58 confirms v1's demotion (defeat
   only via the largest-site rule; under any-site both paths recover). The
   generated-arm finding confirms the reinstatement. Both are true; the class is
   defined by route, below.
3. **H5 amended.** The negative control must rest on measured evidence. Trigger:
   EIF2AK2 K426's WT_IFN arm is wholly generated (write-up §6), so it cannot
   serve. C0 is now recorded as **vacant**.
4. **H1 moved to open gates.** Its denominator needs the 2019 search FASTA; if
   the deposit does not carry one, H1 is not measurable here.
5. **New required output:** the claim-grain reference-identity table (§7).
6. **D2c upgraded** from single instance to measured behaviour with two proteins.
7. **D3 recorded as unevidenced,** with the decision it forces stated in §7.

---

## 1. Core thesis

A published PTM site claim is the terminal output of a derivation path. Its
apparent stability is a property of that path rather than of the biology.

**Amended (v4).** The path fails in two distinguishable ways, and the cascade
measures both:

- **Latent** — the published record changes under the claim, or never determined
  it. Reference drift needs nobody; analytical underdetermination needs only that
  the methods section be read honestly. Neither requires an error by anyone.
- **Introduced** — a reconstruction supplies what the record does not, and the
  supplied rule moves the verdict. The reconstruction is not wrong; it is
  under-constrained, and a different reconstructor would supply differently.

The first is a claim about decay. The second is a claim about consumption, which
is where the timeliness argument lives: a machine reading that methods section
gets two parameters and no implementation, and must choose.

Where the modifier is inferred from a remnant rather than measured, the path
contains a failure mode with no analogue in abundance proteomics or in
metabolomics feature selection: two orthogonal experiments can assign different
modifiers to the same residue, and neither is wrong.

---

## 2. Unit of analysis

A **claim** is the tuple:

    (target accession + sequence version, residue position, modifier identity,
     perturbation contrast, source publication)

Deliberately not the **identifier** (Griss et al., MCP 2011 — accession deletion
across PRIDE over time) and not the **annotation** (ProtMapper — site positions
not matching the reference sequence across databases and text miners). Both are
upstream of the claim; neither tells you whether the sentence in the paper still
holds.

**Enforcement:** every recorded instance carries all five fields. A record
missing the sequence version or the perturbation contrast is a note, not an
instance. Enforce at ingest.

---

## 3. Definitions

- **Derivation path** — design reconstruction, search parameters and database
  version, protein assignment, site selection, analytical construction
  (filtering, imputation, test), modifier attribution.
- **Defeat** — a claim that can no longer be keyed, or whose support is
  withdrawn, when the current record is applied to the unchanged data.
- **Exposure** — a claim having been subject to the conditions under which a
  given defeater can operate. Exposure, not claim count, is the denominator.
- **Promotion** — moving a modifier identity or a reference keying from
  candidate to asserted on the basis of evidence.
- **Precondition** — a schema-level requirement that must hold before promotion
  is permitted. A precondition that blocks promotion is a *design* outcome, not
  a measurement outcome.
- **Hollow recovery** — a verdict that passes its stated thresholds while the
  statistic supporting it is constructed rather than measured. Hollow recovery
  is defeat under D4, not survival.

---

## 4. Taxonomy (v4)

Six defeater classes and one control. **Every class carries a locus — latent or
introduced (§1)** — and an instance must name both its class and, where the class
has routes, which route.

| class | subject | locus | status |
|---|---|---|---|
| D1a | site representation | **introduced** | confirmed, ADAR |
| D1b | claim-set membership | **latent** | confirmed hard |
| D2 | reference identity | **latent** | measured, strongest |
| D3 | attribution | — | **unevidenced** |
| D4a | construction via selection | **introduced** | confirmed, DDX58 |
| D4b | construction, direct | **latent** *(relocated v4)* | confirmed |
| D5 | analytical underdetermination | **latent** *(new v4)* | measured |
| D6 | specification divergence | **introduced** *(new v4)* | measured |
| D7 | draw instability | **latent** *(new v7)* | **exploratory**: one discovery deposit, no registered test yet |
| C0 | corroboration control | — | **vacant** |

### D1 — Selection
An undocumented selection determines what the claim is about. Two routes, and an
instance must name which.

- **D1a, site representation.** A rule picks one site to represent a target.
  Named instance: ADAR, significant at 793, never consulted because 965 is
  larger. Measured shape: the four-cell table, two paths by two rules, four
  different answers, the curated count reproduced by two diagonally opposite
  pairings.
  **Locus, corrected (v3).** The publication applies no such rule — it retains
  all seven ADAR sites and tests at peptide grain. So this instance is
  *reanalyst-introduced*, not inherited, and must not be presented as a
  published claim losing support. The publication-facing claim is narrower and
  survives: the rule is recoverable only from the figures and the supplementary
  structure, never from the methods prose. A human reanalyst can reach it by
  reading Fig. 4d. A machine consuming the methods section cannot, will pick a
  rule, and the rule it picks moves the verdict on every multi-site target. That
  is a defeat generated at the point of automated consumption, which is where
  this thesis's timeliness argument lives.

- **D1b, claim-set membership.** An undocumented selection determines which
  targets constitute *the published set*, and therefore the denominator of every
  recovery count computed against it. Named instance: the anchor's fourteen —
  the publication's two prose lists total sixteen with OAS1/2 split, the first
  ends *"and others"*, and the curated set drops DDX3X and DHX9 by an unrecorded
  criterion. The publication states no count of recovered targets at all.
  This route is the more consequential of the two: D1a moves a verdict, D1b
  moves the denominator every verdict is scored against, and it operates at the
  curation boundary rather than the analysis boundary. It is also the cleanest
  instance in the project, because both the ambiguity and its source are on the
  public record and neither depends on the construction problem.

### D2 — Reference identity
The sequence under the position changed. Three outcomes:

- **D2a coordinate remapping** — position moves, claim survives. ADAR, offsets
  non-uniform, so resolution is performing alignment rather than a shift.
  PSMB9 at a constant offset.
- **D2b residue invalidation** — the claim is unkeyable. OAS1: one position
  where the reported residue is no longer lysine, one past the end of the
  current sequence.
- **D2c defeat averted by precondition** — promotion declined to preserve
  validity. **TAP1 and PTBP1**, two instances each, against a measured
  denominator of promotions attempted. Home: `ONTOLOGY.md` l.793 and
  `bzk/adapters/maxquant_sites.py`.

D2a and D2b are ProtMapper's and Griss's territory; position against them, not
around them. D2c is not theirs and cannot be.

### D3 — Attribution
Orthogonal experiments assign different modifiers to the same residue. Named
instance: PSMB10 K31. Not a discrepancy to be resolved statistically — evidence
disagreement about identity. **Currently unevidenced** (see §7).

### D4 — Construction *(reinstated)*
The analytical construction manufactures the evidence the claim rests on. Two
routes, and an instance must name which:

- **D4a, through selection.** A different constructed population reorders a
  target's sites, so the selection rule returns a different representative.
  Named instance: DDX58 — imputed matrices of different sizes from separately
  constructed generators; recovered on one path under largest-site and not the
  other; no defeat under any-site.
- **D4b, direct. Locus: latent, relocated in v4.** The verdict's supporting
  statistic is constructed, with no selection rule in the path. **And the
  publication's statistic is constructed too**: the cascade's control shows 39
  rows where both sides hold measured values agreeing to five decimal places,
  against a mean offset of +0.711 where the published WT arm is wholly generated.
  The published analysis imputed. The concentration is therefore inherited from
  the published derivation path, not introduced by reanalysis — which is what H6
  required and could not assert before. Named instance: the published-target rows, whose
  generated arm is displaced by the downshift (inflating the numerator) and
  drawn at the width (shrinking the denominator), with BH passing the
  manufactured small p-values through. This is defeat by §3's definition:
  support withdrawn, data unchanged.

**Required citation.** Downshifted-normal MNAR imputation inflating significance
is documented in the proteomics methods literature. Cite it. The contribution is
not the statistics; it is (i) the concentration at the published targets and
(ii) that an invariant written to catch exactly this is silent because it
thresholds on the matrix rather than on the rows carrying the claims.

### D5 — Analytical underdetermination *(new, v4)* — **latent**
The published record does not determine the analysis, so a faithful
reconstruction produces different support for the same claim without anyone
erring.

**Named instance and measured shape.** The anchor's methods state permutation
FDR 0.01 with s0 0.1, and no implementation. A reconstruction reading the methods
and choosing a standard test — BH on Welch — finds, of 749 published claims
reaching the test, **223 failing the p-value (179 on the p-value alone)** and 58
failing a fold-change threshold the publication does not impose at all, since s0
is a curvature parameter rather than a cut. Exposure 749, defeat 223.

**Why this is the class the thesis needed.** It requires no reanalyst error, no
reference change and no selection rule. It is a property of what publication
records, measured at claim grain with a denominator, and it is precisely what a
machine consuming the methods section encounters. D2 is decay; D5 is
under-determination. They are the two latent classes with evidence.

**v6 note — the second deposit.** On `PXD026748` the stated test is fully
specified and **reproduces the publication's own statistics exactly** wherever
imputation cannot enter: 1,512 of 1,512 proteins
(`walk/RESULT-PXD026748-reconstruction.md`, the gate). So the *test-choice*
mechanism named above did not recur, and that is v4's weakening condition met
**for that mechanism**. The class held through a different unstated step,
imputation, measured under H9s. **The class generalises across two deposits and
two mechanisms. The anchor's fraction is not a rate, and it is not compared with
the second deposit's.**

**What would weaken it.** A second deposit whose methods fully specify the test,
where the reconstruction's support matches. Look for one.

### D6 — Specification divergence *(new, v4)* — **introduced**
The reconstruction applies a rule the publication did not, and the rule removes
published claims.

**Measured instance.** Two filters, applied by both reconstruction paths before
any statistic and absent from the publication's own output: the **0.75
localisation cut**, which removes 33 of the 798, and the **contaminant drop**,
which removes 3. Total **36**. Both are defensible field conventions; both are
documented in `ONTOLOGY.md`; neither is what the paper did — S1 retains 33
peptides below 0.75, down to 0.499996, and 3 flagged as potential contaminants.

**Distinguish from D5.** D5 is *the record does not say*. D6 is *we did something
additional*. The first is the publication's property; the second is ours. An
instance that conflates them is not an instance.

### D7 — Draw instability *(new, v7)* — **latent**, **exploratory**
The published claim set is one realisation of a stochastic step, and other
realisations of the same procedure give a different claim set.
- **Recording the seed makes the claims reproducible, not stable.** That is what
  separates D7 from D5. D5 says the record does not determine the analysis. D7
  says that even a fully determined procedure leaves the claims dependent on the
  draw.

**Discovery instance, which is not a confirmation.** On `PXD026748`, H9s's
family was re-read descriptively after its verdict. Seed variation alone changes
some claims' support in **every one of the 18 parameter cells**, 53 to 162 of
288 claims per cell. No underdetermined claim fails on the choice of cell alone.
Home: `walk/RESULT-PXD026748-reconstruction.md` and the committed fixture.

**What the discovery deposit does not show.**
- **It does not show that D7 holds at the publication's settings.** Those are
  unstated, and so is its seed.
- **It does not show a rate for the literature.**
- **It does not show that any claim is false.** No claim is unsupported in
  every member. *Support varies* must never be written as *the site is not
  modified*.

**Status.** Exploratory until a registered test on data not yet examined
confirms it. H10 is the first such test; the third deposit is the independent
one.

**Relation to prior work.** Draw variability in single imputation is known, and
multiple imputation is its standard remedy. Any novelty claim is limited to a
measured rate of **claim-set** instability against a publication's own claim
set. It is **unverified** until the literature check in §11 is done.

### C0 — Corroboration (negative control) — **VACANT**
Independent perturbational designs converge and the claim survives D1–D4. Not a
failure mode; the internal validity check.

**Vacancy recorded.** EIF2AK2 K426 was the designated control and cannot serve:
its WT_IFN arm is wholly generated, so its supporting statistic is constructed
and it is a hollow recovery. The only candidate on this deposit is the one
target row that is partly measured (OAS2 K425, two of three), which is thin.
**Until a control exists, no claim may be made that the instrument distinguishes
defeat from noise.**

**Amended (v6) — a weaker candidate exists, and it is still not C0.**
`PXD026748`'s Supplementary Table 1 flags each ISG15 claim that an independent
*in vivo* ISGylome also reported (Zhang et al. 2019). The flag is **the
publication's citation of another study**. The other study's measured values are
not in the tree, and the publication's own mouse-to-human mapping has not been
checked. C0 requires the corroborating evidence to be measured on both sides, so
this does not fill C0. It is registered as **H5c** (§5): a test of whether the
instrument's D5 durability tracks citation-level corroboration. If it does not,
that is a warning about the instrument, recorded as such.

**Amended (v4) — a partial validity check now exists, and it is not C0.** The
cascade's measured-WT partition is 39 rows where both the publication and the
platform hold measured values; their log₂FC agree to within ±4.9 × 10⁻⁵ on 38 of
39, mean −0.0075. That establishes the instrument computes the publication's own
number where both sides have data, which is something C0 was standing in for. It
does **not** establish corroboration across independent perturbational designs,
which is what C0 is. Record it as an instrument check, cite it as one, and leave
C0 vacant.

---

## 5. Registered hypotheses, with direction

**H2 (selection, D1a) — amended.** Where more than one site was quantified for a
target, the represented site is not always the one with the strongest evidence
under the criteria in force.
*Direction:* at least one instance; no expectation of a high rate.
*Status:* **confirmed**, ADAR, on both paths — **locus: introduced** (§4). The publication selects no representative
(§0.1). State it as a property of reanalysis under an unstated rule, not as a
published claim that lost support, or the instance is refutable from the
anchor's own Fig. 4d.
*Not yet counted:* the exposure denominator — targets for which more than one
site was quantified — has been available since the four-cell table was
committed and is still uncomputed. This is §12's first failure shape, live, in
the oldest class.

**H8 (claim-set membership, D1b) — new.** The set of targets a publication is
read as claiming is not fully determined by the publication, and the
reconstruction step is not recorded.
*Direction:* at least one instance; the reconstruction identifiable and its
criterion absent.
*Status:* **confirmed**, anchor, from the publication itself. Sixteen named
against an open set, fourteen curated, two dropped without a recorded criterion,
no published recovered-count at all.
*What would strengthen it:* a second deposit whose curated target set can be
checked against its publication's own naming. Cheap — it needs a publication and
a curation record, not an ingestion.
*What would weaken it:* the anchor's supplementary Data Tables carrying an
explicit target list that yields fourteen. Check before writing (§9).

**H3 (construction through selection, D4a).** Where imputed matrices differ, the
identity of the representative site changes.
*Direction:* site identity less stable than target verdict.
*Status:* **confirmed with a correction** — in the observed instance the verdict
moved too, because it follows the representative. Verdict stability is therefore
not independent of site stability under a largest-site rule. Amend any claim
that separates them.

**H6 (construction, direct, D4b) — new.** Among rows producing published-target
verdicts, the share resting on a wholly constructed arm exceeds the share in the
tested population as a whole, and effect size rises monotonically with
construction burden.
*Direction:* concentration at targets; monotonic rise.
*Status:* **confirmed on this deposit**, at both grains and on both
protein-grain quantities, **and strengthened in v4: the concentration is
inherited.** The publication imputed too (§4, D4b), so this is a property of the
published derivation path rather than of the reanalysis. Home: write-up §6, and
`FINDINGS` §14.3 for the control.
*What would weaken it:* a deposit where the burden is uniform across tested and
target rows. Look for one; do not assume the concentration generalises.

**H7 (invariant blindness) — new.** A matrix-wide construction threshold does
not fire on a distribution concentrated at the rows carrying published claims.
*Direction:* silent where a label would change the reading.
*Status:* **confirmed**, measured from within the graph.
*Consequence for the ontology, not yet decided:* whether the invariant should
carry a per-result or per-target clause.

**H9 (analytical underdetermination, D5) — new, v4.** Where a publication states
statistical parameters without an implementation, a faithful reconstruction
choosing a standard test withdraws support from a measurable fraction of the
published claims.
*Direction:* nonzero, and larger than any single upstream filter's cost.
*Status:* **confirmed on this deposit.** 223 of 749 fail the p-value, 179 on it
alone, against 36 for the two divergent filters combined and 33 for the largest
single one. Home: `FINDINGS` §14.
*What would weaken it:* a deposit whose methods specify the test fully, where the
reconstruction's support matches.
~~*The sharp form, not yet registered as a hypothesis:*~~ **Registered in v5 as
H9s, below.** The methods admit a **family** of defensible reconstructions, not
one. Claims surviving every member of that family are durable in a sense that
means something; claims surviving only some are not. That intersection is
computable from a single deposit and is the direction most worth pursuing.
Register it before measuring it.

**H9s (the family form of D5) — new, v5, registered on `PXD026748` before
measurement.** Where a publication fixes everything but a stochastic step, the
published claims divide into those supported by every defensible completion of
that step, the durable ones, and those supported by only some, the
underdetermined ones.

*Everything the publication fixes is held constant.* This is its stated
pipeline:
- remove reverse sequences, contaminants, and localisation below 0.75;
- the per-multiplicity table, reconstructed on summed intensities with the
  divergence declared. Route A was admitted by a registered rule:
  `walk/RESULT-PXD026748-multiplicity.md`;
- log2 transformation, then per-sample median subtraction;
- at least three valid values in at least one group;
- a two-way ANOVA of treatment × genotype with interaction;
- retention at P < 0.01 on any of the three terms.

*The family varies only what the publication leaves unstated:* the imputation's
width, its downshift, and its scope (per column or the whole matrix), each
crossed with repeated seeds. The grid's values are fixed in the reconstruction's
pre-registration, before it runs. This document fixes the axes and the
criterion, not the values.

*Exposure:* the P-selected published claims, Supplementary Table 1's 296
(276 ISG15 + 20 ubiquitin sites), that reach the test. The 118 PLpro targets are
selected by clustering and are D1, not D5.

*Support:* the reconstruction retains the claim at P < 0.01 on at least one of
the three terms, as the publication did.

*Durable:* supported in every member and every seed. Reported together with the
fraction supported under each member alone, and the fraction supported in none.

*Directions, both registered:*
- **Weakens D5:** the durable fraction is **≥ 95% of exposure**. The test was
  specified, and the support matches, which is the condition v4 registered under
  D5 and H9.
- **Extends D5 to imputation alone:** the underdetermined fraction, supported in
  some members but not all, is **≥ 5% of exposure**.
- **The reviewer's expectation:** nonzero, and well below the anchor's
  test-choice figure, because only one step varies here.

The two thresholds are judgement, fixed here. They are not moved after
measurement.

*What it cannot show:* whether the published run used any particular member.
The seed is unrecorded, so matching one member is not evidence that the
publication used it.

*Status (v6):* **measured.** 111 durable and 177 underdetermined of 288, so the
verdict is **extends D5 to imputation alone**. The registered expectation
(*"extends, narrowly"*) held in direction and missed in size. Home:
`walk/RESULT-PXD026748-reconstruction.md`.

**H5c (corroboration by citation, against D5) — new, v6, registered on
`PXD026748` before measurement.** Among the publication's ISG15 claims, those it
flags as also reported by an independent *in vivo* ISGylome are more often
durable under H9s's family than those it does not flag.
- *Population:* ISG15 claims (clusters 1a, 1b and 2) among H9s's 288 that reach
  the test. Cluster 3's ubiquitin sites are excluded, because the flag concerns
  ISG15 targets.
- *Groups:* flagged (Table 1's `In vivo ISG15 targets` column is `x`) and not
  flagged. The column is read from the pinned supplement, never re-derived.
- *Measure:* the durable proportion in each group at the primary threshold,
  taken from the committed reconstruction fixture, which is not re-run.
- *Directions, both registered:*
  - **Discriminates:** flagged minus unflagged durable proportion is at least
    **+0.10**. This supports the instrument's defeats not being noise.
  - **Does not discriminate:** the difference lies between −0.10 and +0.10,
    exclusive. This is recorded as a warning: D5 durability does not track
    citation-level corroboration.
  - **Inverted:** the difference is at most **−0.10**. It is reported as found,
    and the reviewer has no mechanism for it.
- *Declared confound:* corroborated sites may be more abundant, and so less
  often imputed, which would make them durable for reasons other than being
  true. Each claim's count of imputed values in its row is reported by group,
  **descriptively**. It is not used to adjust the verdict.
- *What it cannot show:* that a flagged claim is true. It can show only that
  durability and citation agree or disagree.
- The thresholds are judgement, fixed here, and not moved after measurement.

**H9p (D5 at protein grain) — new, v6, registered on `PXD026748` before
measurement.** The imputation-underdetermination measured under H9s at site grain
is smaller at protein grain, in the same deposit, pipeline and family.
- *Exposure:* Supplementary Table 2's proteins, the publication's two-way ANOVA
  set at P < 0.01 on any term. Only those that join to the reconstruction's
  shotgun matrix by the rule turn 16 recorded, and that reach the test, count.
- *Pipeline and family:* the shotgun arm as registered and gated in
  `walk/PREREG-PXD026748-reconstruction.md`, with the same 360 members and the
  same support rule.
- *Primary comparison:* **conditional on missingness.** A claim whose row has no
  missing value cannot be underdetermined by imputation. The protein arm has far
  more complete rows (the gate's 1,512 complete cases), so an unconditional
  comparison would be settled by missingness alone. The comparison is therefore
  the underdetermined proportion **among claims whose row carries at least one
  missing value**, protein grain (U_p) against site grain (U_s). U_s takes its support
  counts from the committed site fixture and its missingness from the GG
  deposit's rows, with nothing re-run.
- *Directions, both registered:*
  - **Particular to site data:** U_p ≤ 0.5 × U_s.
  - **General to the imputation step:** U_p ≥ 0.8 × U_s.
  - Between the two: **indeterminate**, reported as found, deciding nothing.
- *Disclosed before registration:* the gate's figures, including 1,512
  complete-case proteins and 415 complete-case ANOVA members, were seen when
  this was written. That knowledge is why the comparison is conditional. It sets
  no threshold.
- *What it cannot show:* that site data are more fragile *because* they are PTM
  data. Absence-defined claims exist at protein grain too. It can show only
  whether this deposit's two grains differ.
- The thresholds are judgement, fixed here, and not moved after measurement.

**H10 (D7 on the anchor) — new, v7, registered before any anchor computation.**
The anchor's published claims that reach its reconstruction's test are
draw-unstable under an imputation family built on the same axes as H9s's.
- *Test held fixed:* the anchor's D5 reconstruction's test, as recorded for its
  223. The family varies the imputation only.
- *Primary readout, fixed by this rule:* at the anchor's **default cell** (width
  0.3, downshift 1.8, per-sample, 20 seeds), the share of claims whose support
  differs across seeds, **over claims whose row carries at least one imputed
  value**.
- *Reported, and never the headline:* the same share over all claims reaching
  the test; the full-family underdetermined fraction; the single median draw.
- *Directions:*
  - **D7 recurs:** the primary readout is at least **5%**.
  - **D7 is absent on the anchor:** at most **1%**. That is a reportable
    outcome, and D7 would then be stated as deposit-specific.
  - Between the two: **indeterminate**.
- *Declared limitation:* the anchor shares authors with `PXD026748`, so a
  recurrence tests the group's practice, **not the literature's**. Only the third
  deposit (§9) is an independent test.
- *Before measurement,* the anchor's reconstruction pre-registration fixes the
  grid values, the population, and the exact test.
- The thresholds are judgement, fixed here, and not moved after measurement.

**H4 (attribution, D3).** For sites with orthogonal modifier evidence, some
fraction carries evidence supporting more than one modifier identity, and that
fraction is higher under interferon stimulation than at baseline.
*Direction:* nonzero, and higher under IFN.
*Status:* **unmeasured.**
*Registered requirement (v7):* **co-annotation across studies is not
disagreement.** A residue reported as ubiquitinated in one study and ISGylated in
another is not in conflict when the conditions differ. Before any D3 instance
is counted, a later amendment must specify a comparability criterion: same
residue, same sequence version, a comparable perturbation state, and two
assignments that cannot both hold. `PXD026748`'s co-annotation count is a
candidate pool, not an exposure set, until that criterion exists.
*Standing counter-position:* the field's settled answer is Kim et al.'s
baseline-derived majority-ubiquitin conclusion and the under-6% figure repeated
since. Argue the conditional-on-stimulation claim with own numbers or it is
closed with a 2011 citation.

**H5 (control, C0) — amended.** Corroborated claims survive D1–D4, **and the
corroborating evidence is itself measured rather than constructed.**
*Direction:* survival.
*Status:* **cannot be evaluated** — control vacant. Run this first once a
candidate exists; if the instrument defeats a valid control it is detecting
noise.

**H1 (exposure, D2) — moved to gates.** See §9.

---

## 6. Denominators

One per class. None is "all sites". Record the exposure count before the defeat
count, in the same run; a defeat count without its exposure count is not a
result.

| Class | Exposure set |
|---|---|
| D1a | Targets for which more than one site was quantified — **available since the four-cell table, uncomputed** |
| D1b | Targets named by the publication, against the targets carried in the curation record |
| D2 | Claims whose accession changed sequence version between publication and current release — **blocked, see §9** |
| D2c | Promotions attempted (measured) |
| D3 | Sites with orthogonal modifier evidence present in the tree |
| D4a | Targets whose sites reorder between constructed populations |
| D4b | Rows producing a published-target verdict, against the tested population |
| D5 | Published claims reaching the reconstruction's test (measured: 749) |
| D5, second deposit (H9s) | `PXD026748`'s P-selected published claims reaching the reconstruction's test — **measured: 288 of 296** (`tests/fixtures/pxd026748_published_cascade.json`) |
| H5c | ISG15 claims among H9s's 288, split by the publication's in vivo flag — **unmeasured** |
| H9p | Supplementary Table 2's proteins reaching the shotgun reconstruction's test, and within them those with at least one missing value — **unmeasured** |
| D6 | Published claims entering the reconstruction (measured: 798) |
| D7 (H10, anchor) | Anchor claims reaching the reconstruction's test whose row carries at least one imputed value — **unmeasured** |
| C0 | Targets appearing in two or more independent perturbational designs **with a measured arm on both sides** |

**Amended (v4).** D5 and D6 share a denominator the earlier classes lacked: the
**published claim set itself**, pinned as `SUPP_DATA_1`. Every class above can
now in principle be stated against it rather than against the platform's tested
population, and where it can, it should be.

---

## 7. Contribution, and the decision the write-up forces

Not a proportion. An instrument, a taxonomy grounded in named instances, and
behaviours nothing else has.

1. **Refusal (D2c)** — promotion declined by precondition. Now measured, two
   proteins, against a real denominator. This is the only result in the project
   untouched by the construction problem, because declining promotion consumes
   no statistic. Thickest where the thesis is thinnest.
2. **Adjudication (D3)** — modifier identity held as an evidenced state two
   experiments can disagree about. **No evidence yet.**
3. **Invariant blindness (H7)** — the instrument detecting a failure of its own
   rule. Novel as a demonstration, not as statistics.

**Required output, not yet assembled.** The claim-grain reference-identity
table: the fourteen curated claims against their D2 outcome — survived with
position moved, unkeyable, averted, unaffected. Every part is in committed
fixtures and distributed across write-up §4, §5 and §7. This is the one table in
the thesis that neither ProtMapper nor Griss produces, because it is at claim
grain. Assemble it as a single artefact.

**Amended (v3):** the table's rows are the *curated* fourteen, and the header
must say so. Add two rows for DDX3X and DHX9 — named by the publication, absent
from the curation record — so the artefact carries D1b as well as D2. That makes
one table do the work of two classes, and it makes the reconstruction visible in
the same place the keying outcomes are.

**The decision, resolved (v4).** v3 posed a choice: D3 acquires evidence, or the
contribution narrows to refusal plus invariant blindness. **It narrowed
differently, and to more.** D3 is still unevidenced. What arrived instead is the
cascade, and with it two things v3 did not have:

4. **A measured recall of published site-level claims** — 512 of 798 against a
   ceiling of 516, with all 286 losses attributed to named stages. No existing
   tool produces this, because it requires the published claim set pinned as an
   artefact and both sides keyed to accession-with-sequence-version. That is
   D2's machinery doing work D2 was not built for.
5. **D5, the 179.** Published claims that hold under the publication's stated
   criterion and fail under an honest reconstruction of it. This is claim
   durability with an exposure denominator, and it is the result the thesis was
   reaching for by a different route.

**What the paper is now.** Not *published claims decay*. Narrower and better
evidenced: **the derivation path behind a published PTM claim is underdetermined
by what is published, and the gap is measurable at claim grain.** Two latent
mechanisms with numbers — reference drift (D2), which needs nobody, and
analytical underdetermination (D5), which needs only an honest reconstruction —
plus the refusal census, D2c, and invariant blindness, all untouched.

The timeliness argument survives whole and is now demonstrated rather than
asserted.

**The open question that would make it a claim rather than a case study:** does
D5's fraction hold on a second deposit reconstructed honestly from its methods?
One number, one more dataset.

---

## 8. Kill conditions

- Every named instance turns out reproducible by an existing tool.
- The attribution disagreements resolve to one experiment simply being worse.
- ~~Defeat rates are low enough that derivation paths mostly hold.~~ **PARTIALLY
  FIRED (v4).** Against *capacity* the paths hold: 512 of a possible 516, four
  short of the arithmetic ceiling. The reconstruction is not leaking claims
  through its own filters — those cost 36 of 798. But 286 published claims do not
  survive, and 223 of those fail on a test the publication did not specify. So
  the rates are not low; they are **concentrated in one identified mechanism**,
  which is a sharper result than a diffuse one. This is the smaller and better
  paper the condition anticipated. Write that one.
- The instrument defeats a valid control (H5), once one exists.
- **New:** the construction findings prove to be a property of this deposit
  rather than of published claims. At n=1 this is currently unanswerable, and
  the write-up must say so rather than generalising.
- **New (v7):** every instance comes from one group's practice. The two deposits
  share authors, so agreement between them may reflect shared conventions, not
  the literature. Until an unaffiliated deposit is measured, the write-up must
  say so, and must not present the two deposits as independent samples.

---

## 9. Open gates

- **A third, unaffiliated deposit — the top gate (v7).** It is the only
  independent test of D5's and D7's generality, since the first two deposits
  share authors.
- **H1 blocked** on the 2019 search FASTA. The refusal fixture carries sequence
  versions only for refused rows; the drift receipt measures cache-against-
  UniProt over one day, a different relation. If the deposit carries no search
  database, H1 is not measurable here — record that, do not leave it open.
- **D3 blocked** on resolving both sides to accession-with-sequence-version and
  on the Impens data not being in the tree.
- **C0 blocked** on a deposit with a detected WT arm. *(Note: the cascade's
  measured-WT partition is an instrument check, not a corroboration control —
  §4.)*
- **D5's generalisation blocked** on a second deposit whose methods can be
  reconstructed honestly. This is now the single most valuable gate in the
  document, and it is a smaller ask than any other: one deposit, one
  reconstruction, one fraction.
- **Dating the deposit-side keying, open and cheap.**
  `tests/fixtures/pxd018299_refusals.json` records a Python version and no date.
  The cascade keys the published side today against a deposit side keyed at an
  unknown time, so it is not yet a like-for-like comparison. This stopped being
  housekeeping the moment both sides entered one measurement.
- **Threshold parity, open and answerable today.** The publication states
  permutation FDR 0.01 with s0 0.1 across its proteomic analyses; both paths
  apply `adj p < 0.05` and `log₂FC > 1.0`. s0 is a curvature parameter, not a
  fold-change cut-off, so this is a different test and not only a different
  threshold. Until it is settled, *recovered* is a property of the reproduction's
  criteria and not a comparison to the publication's. Grade A on the
  publication's side; needs no correspondence.
- **Data Table S1 grain, open and answerable today.** If the anchor's
  supplementary site table is summarised per protein rather than per peptide, a
  per-target selection exists at the reporting step even though Fig. 2f has
  none — which would supersede §0.1. Check before D1a's corrected locus is
  written up. Adjacent possibility to check at the same time: if Fig. 2f's
  labelled points were labelled by hand, the target list has no rule at all,
  which strengthens H8 and weakens nothing.
- **Second deposit blocked** at the imputation record; a stochastic imputation
  without a recorded seed and scope cannot be ingested, and "Perseus defaults"
  names a convention rather than a downshift and a width. **Clarified (v5):**
  this gate concerns ingesting the *publication's* imputation, and it stays
  closed. An internal reconstruction that declares its own parameters and seeds
  (ADR-0034, table row 3) is a different act. H9s measures that act, and it does
  not pass this gate.
- **Embargoed dataset** under the embargo invariant: instances countable, not
  nameable until release.
- **Sequencing:** none of this precedes v0.1. If a gate starts pulling platform
  scope forward, the gate is wrong.

---

## 10. Scope boundaries

- **Not an AI paper.** Machine consumption is why this is timely, not why it is
  true.
- **Not a formalism.** Assertion, evidence and provenance ontologies already
  specify how support and challenge can be represented; this measures instances.
- **Not a pipeline.** The platform stays downstream of Perseus.
- **Not a biology claim.** No assertion about ISGylation biology beyond what the
  sources assert.
- **Not "data integrity."** The data are intact throughout. Use *claim
  durability* or *derivation integrity*.
- **Not an imputation-methods paper.** D4 is a defeater class, not a
  recommendation about estimators.

---

## 11. Must-read before writing the relevant section

- Bachman, Gyori & Sorger — ProtMapper (D2 positioning).
- Griss et al., MCP 2011, "Published and Perished?" (D2 temporal positioning).
- Kim et al., Mol Cell 2011 (standing quantitative counter to H4).
- The 2025 survey of assertion, evidence and provenance ontologies.
- The September 2026 Frontiers in Immunology review on organelle-centred ISG15
  biology — evidence-strength framework in this exact biology. Read before
  defining D3 tiers; cite and extend.
- **New:** the MNAR / downshifted-normal imputation literature, for D4.
- **New (v7), required before any D7 novelty claim:** the multiple-imputation
  literature for proteomics differential analysis (for example mi4p), and
  studies of run-to-run variability from single imputation. D7's claim to
  novelty is limited to claim-set instability against a publication's own claim
  set, and even that stays unverified until this is read.
- **New, and first:** the anchor publication itself — Pinto-Fernández et al.,
  *Br J Cancer* 124:817–830 (2021) — read at **figure, table and supplementary
  grain**. Two of this version's five amendments came from figures that had been
  in reach the whole time. A derivation path is not reconstructible from a
  methods section, which is the thesis's own claim; reading only the methods
  section was the same error committed inward.

---

## 12. Writing discipline (own failure shapes)

- **Countables.** Each class needs an exposure count and a defeat count.
  Currently one level short on: the claim-grain D2 table, the D2 exposure
  denominator, the second path's target-site census, and **D1a's denominator,
  which has been derivable from a committed fixture for weeks while the class
  was carried on a named instance.** The oldest class is the one still short.
- **Absences do not fail tests.** The reviewer loop caught every error of
  commission across eleven audit runs — a wrong fixture cited, a figure inherited
  without its derivation, a module named that the repository rejects. It caught
  none of the real ones, because there was no wrong claim to catch: only an
  unasked question. Verification is structurally blind to the comparison nobody
  made. Where a claim rests on something not compared, say so in the claim.
- **The pipeline was right and the prose was wrong, repeatedly.** A target list
  typed into a module; a measurement stored under a field named `n_expected`;
  twelve-of-fourteen restated across six documents including the normative one;
  two filters presented as inherited. Rigour pointed entirely at inputs and
  nothing checked the descriptions. Before asserting anything about the platform,
  check whether the assertion is about the code or about a sentence describing
  it.
- **Read the artefact, not the prose about the artefact.** v1 and v2 reasoned
  about the anchor's derivation path from its methods section. The rule was in
  Fig. 4d and the target set was in the Fig. 2f prose, both public throughout.
  Before asserting that a path is unrecoverable, record which grains of the
  source were actually read.
- **Evidence grade must match prominence.** The strongest claim in the write-up
  is asserted from a grade-C re-derivation with no committed module. Either
  commit the module or demote the claim; do not leave a load-bearing figure as
  the least verifiable thing in the document.
- **Parallelism.** Selection and construction are not sequential — the
  construction produces the values the selection ranks. Section order must not
  contradict what the instances say. Check every "then" for "meanwhile".
- **Compression.** Facts must survive the short version. PTBP1 was compressed to
  a subordinate clause; it is a second instance of the only cell nothing else
  can produce.
- **Do not disclaim your own results.** A committed, re-derivable measurement no
  other tool produces is a finding, whatever section it sits in.
- **Closings.** No section ends on a negation or a restatement.
