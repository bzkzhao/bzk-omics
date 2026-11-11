# Prompt 42a — `bzk.audit` stages 6 and 7: the figures they report do not say which rule produced them (revision 2)

**Repository:** `main` at the commit adding this prompt. Every line reference was measured at
`24a44da`; §0 re-measures them.

**Why revision 2.** An independent audit **built** revision 1 end to end and returned four
blockers. It also confirmed, by building it, that the core is sound: §1.2's mirror matches
`readout_b` bit for bit, all four test groups are writable with no `approx` and no `round`, the
rename breaks no consumer, and the post-build counters land at `60 / 2685`, `PINNED` 351.

The four blockers were mine. Three were one failure — §1.4's synthetic case named neither the row
nor the column, and "flip that row's support **values**" (plural) is self-defeating: flipping all
twenty default columns gives `min == max == 0`, so the numerator stays 159 and the test fails as
written. The default columns are **indices 160–179**, not 0–19; an engineer flipping index 0 gets
159 and a red build that reads as a bug in their own §1.2.

The fourth is substantive. Revision 1 said which denominator the registration makes primary is a
live question. **It is not.** `walk/PREREG-PXD018299-H10-attempt3.md:81–82` — the pre-registration
that governs *this* fixture, which revision 1 never cited — states the shares are taken over
claims whose row carries at least one imputed value, and `walk/PREREG-PXD018299-H10.md:186–187`
puts the all-claims share under "Reported, never the headline". H10 has **three** PREREGs (base,
attempt 2, attempt 3); revision 1 cited only the base one and never checked whether a more
specific one existed. That is the fourth time in this sequence that the cause was an unenumerated
document class, and here it was a sibling of the file I did cite.

**The defect this prompt closes.** Stages 6 and 7 compute the registered attempt-3 family under
the variant the fixture names, and report figures numerically adjacent to `walk/FINDINGS.md` §5's
and §6's documented-rule figures **without the keys saying which rule produced them, or over which
population**. The fixture carries both denominators at `readouts.primary.readout_b`; the stages
discard that structure and emit a bare share. Stages 6 and 7 also have **no tests at all**.

---

## 0. Receipt check — answer, then stop and wait

Re-measure each. Report what you find and whether it matches. **Stop on any mismatch.**

**(a) The stage figures.** Run stage 6 and stage 7 against
`tests/fixtures/pxd018299_h10_attempt3.json` — `stage6_sensitivity(fixture, out)` takes an output
directory as its second positional argument — and report every key:

```
stage 6: claims 791 | changing_in_default_cell 159 | changing_in_default_cell_share 0.201
         family_members 360 | changing_somewhere_in_family 479
         supported_in_every_default_draw 631 | supported_in_no_default_draw 1
stage 7: fully_measured_claims 40 | moved_across_cut_in_family 3
         moved_across_cut_in_default_cell 0
         859 ALDOA 294/360 20/20 | 889 ATP1A1;ATP1A2;ATP1A3 184/360 20/20
         1623 HIST1H4A 347/360 20/20
```

**(b) The mirror this prompt pins.** `readouts.primary.readout_b` holds exactly six keys:
`conditional_on_imputation` (numerator 159, denominator 751, share 0.21171770972037285),
`over_all_claims` (159, 791, 0.20101137800252844), `verdict` (exactly three keys: `outcome`
"recurs", `share` 0.21171770972037285, `reason` null), `isolations`, `family_categories`
(`underdetermined` 479), `whole_table_supported_default_cell` 822.

**No key marks a primary** — in the JSON it is implied only by `verdict.share` duplicating
`conditional_on_imputation.share`. The *registration* does name one (§1.2); the fixture does not.

From `_per_claim_matrix`'s three returns `(rows, support, imputed)` and the default-cell columns:
`imputed.sum()` 751; `changed.sum()` 159; `(changed & imputed).sum()` 159;
`(changed & ~imputed).sum()` **0**. Confirm `159/751` and `159/791` are **bit-identical** to
`readout_b`'s two shares — compare `.hex()`, not `==` alone, and report both:

```
159/751 = 0x1.b1990df9dd3b0p-3      159/791 = 0x1.9babda7528748p-3
```

**(c) That zero is a hole in the mirror, not a convenience.** No fully measured claim changes
support in the default cell at this fixture, so **both numerators are 159 — and so are both of
`readout_b`'s**. A build computing the all-claims numerator over the imputed-only population
returns 159 over 791 with a bit-identical share, and is **indistinguishable** under §1.4 test 2.
§1.4 test 3 closes that with a synthetic fixture rather than by dropping the assertion.

`tests/fixtures/` holds three H10 fixtures, and **only `_attempt3` has `readouts.primary`** — the
other two raise `KeyError` in `_per_claim_matrix` — `_attempt2` on `'primary'`, and the
base `pxd018299_h10.json` on `'readouts'`, having no readouts block at all. So nothing else in the committed data
can discriminate these two populations. Confirm that.

**(d) The variant, and where it lives.** `readouts.primary.variant`,
`readouts.primary.primary_variant` and top-level `primary_variant` all read
`joint_half+random_excluding_trivial` — but they are **not interchangeable**:
`readouts.secondary.primary_variant` is `joint_half+exhaustive_excluding_trivial`, so
`primary_variant` names *its block's* primary and coincides with `variant` only inside the primary
block. Confirm both values, and confirm `bzk/audit.py` reads none of the three —
`grep -n variant bzk/audit.py` exits 1 with no output.

**(e) Nothing consumes the keys.** `notes/REVIEWER-MAP-findings-5-and-6.md` (landed at
`191d036`, after this prompt's measurements) quotes several of these key names as a dated
record of what the stages emitted; it is prose, not a consumer, and §1.3's rename does not
break it. Setting that file aside, confirm no file outside `bzk/audit.py` reads
`changing_in_default_cell`, `moved_across_cut_in_family`, `moved_across_cut_in_default_cell`,
`changing_somewhere_in_family`, `supported_in_no_default_draw`,
`supported_in_every_default_draw` or `fully_measured_claims` — grep the whole tree, no
`--include` filter — and that `tests/test_audit.py` contains no reference to `stage6` or `stage7`.
`tests/test_audit_pxd032267.py:489` does call `audit.stage6_sensitivity(record)`, but its l.22 is
`from bzk import audit_pxd032267 as audit` — a different module, different signature
(`bzk/audit_pxd032267.py:496`), non-colliding keys. §1.3's rename breaks no consumer.

**(f) Stage 7's rename is warranted.** `bzk/audit.py:900` is `if s.min() != s.max():` — a
support-change test — and the counters built from it are at `:914` and `:915–920`. Stage 7's note
at `:929–931` states q-values are not stored in the fixture. Confirm both.

**(g) The default-cell columns.** `_members` and `_default_columns` (`bzk/audit.py:105–115`) select
the 20 family members matching `DEFAULT_CELL`; they are **indices 160–179** of the 360. Report the
first and last. `_per_claim_matrix` returns no column information, so this is the only source for
them — §1.4 test 3 depends on it.

**(h) Counters.** `sweep()` reads **60 modules / 2669 asserts**, `PINNED` **351**, new 0 / gone 0 —
exactly the floor at `tests/test_tautology_sweep.py:2370`, no lag. Report your reading before
changing anything.

**(i) Baselines, with the pinned tools.** `pyproject.toml:27–28` pins **`ruff==0.16.1`,
`mypy==2.3.0`**. Run them **by resolved path** and report the version each actually executed:
`pip install` can leave a different ruff first on `PATH`, so a bare `ruff --version` may disagree
with what pip reports. At `24a44da`, `ruff check bzk tests` is **clean** at both 0.16.1 and 0.16.9
and `ruff format --check` reports 127 files formatted; **0.17.x** reports a false `RUF100` at
`tests/test_pxd026748_published_cascade.py:508`. A report naming an error there is reporting its
own toolchain.

Report `pytest -q`'s passed/skipped before any change. One expected environmental failure: if
`streamlit` is absent, `test_every_classified_instance_re_runs_its_recorded_evidence` fails because
the sub-pytest it spawns exits 2 collecting `tests/test_ui.py`. **That is not a repo defect.** Any
other failure: stop.

---

## 1. Build

### 1.1 Both stages carry the variant, read from the fixture

Add `"registered_variant"` as the first key of stage 6's and stage 7's `findings`, with value
`fixture["readouts"]["primary"]["variant"]`. **Read it; do not write the string** — a hand-written
label is a second home for a fact the fixture owns (`CLAUDE.md:40`), and §1.4 test 1 is only a
guard if the stage derives the value.

Read `variant`, not `primary_variant`. The reason is §0(d): they are different fields that happen
to coincide in this block, and `primary_variant` is the block's own label for its primary — it
takes a different value in `readouts.secondary`. `variant` is the field that names the variant the
block *is*.

Add a test that all three homes agree **at this fixture**, so the coincidence is recorded rather
than assumed. `bzk/audit.py:59–61` is the precedent for that half only — the test that a duplicate
still agrees with its source. It is not a precedent for the read-never-write rule above; those
lines document an accepted duplicate, which is the opposite case.

### 1.2 Stage 6 reports both populations, and marks the registered one

Mirror `readout_b`'s two keys **by name** — `over_all_claims` and `conditional_on_imputation` —
each a mapping of `numerator`, `denominator` and `share`.

Compute both from `support` and `imputed`, plus the default columns from `_members` /
`_default_columns`: `changed` is `sub.min(axis=1) != sub.max(axis=1)` over `sub = support[:,
default]`, so the column selection is a required input and `_per_claim_matrix` does not supply it.
The all-claims denominator is `support.shape[0]`; the conditional one is `imputed.sum()`. Do not
read either figure from `readout_b` — the stage recomputes, and §1.4 pins the recomputation
against it.

**Store the share unrounded.** `159/751` and `159/791` are bit-identical to `readout_b`'s two
shares (§0b), so the mirror is an exact equality. The legacy `changing_in_default_cell_share`
rounds to four places (`bzk/audit.py:872`); a rounded new key could not equal the fixture's share
at all.

**Mark `conditional_on_imputation` as the registered primary.**
`walk/PREREG-PXD018299-H10-attempt3.md:81–82` states the shares are taken over claims whose row
carries at least one imputed value, and `walk/PREREG-PXD018299-H10.md:179–181` registers the same
estimand with `:186–187` putting the all-claims share under "Reported, never the headline". Two
committed pre-registrations, one answer.

**This marks the registered estimand, not a headline.** Whether
`walk/CHECKS-collateral-and-pkm.md:29–30` may overrule the registration *in* `walk/FINDINGS.md` is
item 3 of the list at `notes/prompts/22-walk-two-route-independence.md:149`, and §2 keeps it out.
Note for your own reading that those two figures — 209 of 751 and 210 of 791
(`notes/logs/round13.txt:6–7`) — differ by **numerator as well as denominator**, the extra claim
being the one fully measured claim that moves; they share the documented FDR rule. The stage's own
figures share a numerator and differ only by denominator, which is the opposite shape.

**Do not remove the existing keys.** Nothing consumes them (§0e), but a rename and a semantic
change in one turn leaves no way to tell which broke a figure.

### 1.3 Stage 7's two counters are renamed to what they measure

`moved_across_cut_in_family` and `moved_across_cut_in_default_cell` count **support changes**
(§0f). Stage 7 cannot perform a q-range reading — its own note says q-values are not stored — so
the names assert something the stage does not do. Rename both to name support change rather than
cut crossing. `fully_measured_claims` and the per-claim `supported_in_*` strings keep their names.

### 1.4 Tests

Stages 6 and 7 have no tests. Add, in `tests/test_audit.py`:

**1. The variant is read, not written.** Both stages' `registered_variant` equals the fixture's
`readouts.primary.variant`; the three homes agree at this fixture; and over a copy in which
**only `readouts.primary.variant` is changed** — leaving `primary_variant` and the top-level key
untouched — both stages report the changed value. The restriction to one home is what makes the
test discriminate: mutate all three and a build reading the wrong home still passes.

**2. The recomputation mirrors the registered readout.** Stage 6's `over_all_claims` and
`conditional_on_imputation` equal `readout_b`'s same-named mappings, and
`changing_somewhere_in_family` equals `family_categories.underdetermined` (479).

**3. The two populations are told apart — the case the committed fixture cannot make.** Build a
deep copy of the fixture and make **exactly one** change:

```
copy["readouts"]["primary"]["per_claim_support"]["rows"][274]["support"][160] = 0
```

Row index **274** is `deposit_id` 859, ALDOA — one of the three fully measured claims that already
change support somewhere in the 360-member family. Column **160** is the first default-cell column
(§0g). Exactly one column: flipping all twenty gives `min == max == 0`, so `changed` stays False
and the numerator stays 159.

Registered expectations over that copy, measured at `24a44da`:

| key | base | copy |
|---|---|---|
| `over_all_claims.numerator` | 159 | **160** |
| `conditional_on_imputation.numerator` | 159 | 159 |
| `changing_somewhere_in_family` | 479 | 479 |
| `supported_in_every_default_draw` | 631 | **630** |
| `supported_in_no_default_draw` | 1 | 1 |
| stage 7 support-changes-in-family | 3 | 3 |
| stage 7 support-changes-in-default-cell | 0 | **1** |
| `fully_measured_claims` | 40 | 40 |

Row 274 is chosen for the third line: it already changes somewhere in the family, so
`changing_somewhere_in_family` stays 479 and **test 2's invariant still holds on the copy**. Any of
the other 37 fully measured rows gives 480 and 4, and test 2 then appears to fail on the copy for
no stated reason.

Two notes on what this test does and does not do. `fully_measured_claims` is read from
`row_carries_an_imputed_cell` (`bzk/audit.py:101`), so **no support flip can move it** — assert it
as a regression guard, not as a discriminator. And the last line is worth more than the
discrimination: stage 7's default-cell counter is **0 at the only usable fixture**, so the
expression computing it (`bzk/audit.py:915–920`) has never produced a nonzero result in any test
or run. This copy is the first thing that exercises it.

A build that computed the all-claims numerator over the imputed-only population passes test 2 and
fails this one. That is the `CAUGHT` half of the pattern at
`tests/test_maxquant_sites_composition.py:265`: the guard ships the case the real data does not
contain, so its firing is re-established by the suite rather than argued from a coincidence.

**4. Ordering.** `registered_variant` is the first key of each `findings` dict.

Run a mutation against each of the four, and defeat the bytecode cache as `CLAUDE.md:97`
specifies — delete every `__pycache__`, then run with `PYTHONDONTWRITEBYTECODE=1`, in that
order — confirming each mutation applied by reading the file back, and reverting it before the
report.

### 1.5 Registered before the run

`sweep()`'s surface is asserted equalities. Measured against `analyse()` at `24a44da`, what
registers is **a call appearing in the compared expressions, or a bare `ast.Name` bound earlier
from an expression containing a call**, when some other side is not a literal display:

| shape | registers |
|---|---|
| `s = stage6_sensitivity(fx, tmp)` then `s.findings["x"] == fx["a"]["b"]` | **no** — a Subscript is not a Name |
| `got = stage6_sensitivity(...).findings["x"]` then `got == fx["a"]["b"]` | **yes** |
| `pytest.approx(x) == y`, `round(x, 4) == y`, `stage6_sensitivity(...).findings["x"] == rb["share"]` | **yes** |
| `check(m, d) == []`, `len(v) == 1`, `s.findings["x"] == "MUTANT"` | **no** — the other side is a literal display |
| `assert not v` | **no** — not a comparison at all |

So: **hoist the stage result and subscript through it; never bind a compared scalar to a bare name;
compare against a literal display where the expected value is one.** Under that discipline an
independent build of this prompt measured the floor moving **2669 → 2685** with `PINNED` unchanged
at **351**, and the suite at **1227 passed / 15 skipped** plus the one environmental failure.
Those are an independent measurement, not a registration you must hit: report your own, and
account for any difference.

If you find you need `approx` or `round` anywhere, **the registration is void** — say so, classify
the new entry, and report that the shape constraint failed rather than working around it.

Read `sweep()` before adding anything and report whether it lags; report it after.

---

## 2. Out of scope. Do not touch.

- **Both `not_automated` notes** (`bzk/audit.py:879–887` and `:927–933`). Stage 6's attribution is
  wrong — it names `diagnose_round11.py` / `diagnose_round12.py` for a count that is
  `diagnose_round13.py`'s (`walk/CHECKS-collateral-and-pkm.md:3`, `notes/logs/round13.txt:7`) —
  and that is **42b**, with the receipt map. Rewriting a note needs the full instrument roster for
  §5 and §6, which is not yet committed anywhere; §5 alone draws on rounds 10, 11/12 and 13.
- **FINDINGS §5's headline figure.** Item 3 of the list at `notes/prompts/22-…:149`: whether
  `walk/CHECKS-collateral-and-pkm.md:29–30` may overrule the registration in `walk/FINDINGS.md`.
  An ADR, not a build. Do not register either figure as an expected value; do not edit
  `walk/FINDINGS.md`, `HYPOTHESIS.md` or any `walk/CHECKS-*`.
- **§5's mixed denominators.** `:109` shows its denominator; `:110` and `:111` are over 751 and
  show none, and `:110` is labelled "the same at 100 draws" when the denominator differs. A
  separate `walk/FINDINGS.md` edit.
- **`bzk/audit_pxd032267.py`.** Same function names, different module.
- **The stage-3/stage-4 `[FIXTURE]`-under-`--live` labelling item**, and the eight unguarded
  source-readers deferred by prompt 39.

---

## 3. Report

The four-point close (`CLAUDE.md:95`), with the checks named at the versions they actually ran
(§0i), and:

1. Every §0 item at the value you measured, including both `.hex()` comparisons and the first and
   last default-cell column indices.
2. Test 3's copy: the numerator it produces, and every row of §1.4's expected-value table at what
   you measured — not just that the test passes.
3. `sweep()` before and after, whether it lagged, and whether the shape constraint held.
4. What this did **not** cover: both notes still carry their attributions, stage 6's still wrong;
   §5 and §6 remain unregenerable by `bzk.audit`; the stages still render `[FIXTURE]` under
   `--live`. This prompt makes the stages state which rule and which population they computed. It
   closes nothing else.
