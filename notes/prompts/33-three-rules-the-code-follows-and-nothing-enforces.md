# Prompt 33 — Three rules the code follows and nothing enforces

**Repository:** `main` at the commit adding this revision. **Rev 11.**

***Rev 11 folds in the seven findings the build session's §0 receipt check returned at `d369216`,
all verified against an independent clone.*** Two change a build step (§2.1's mutation, §3's
`PINNED` regeneration, whose command is broken in the repository); one changes what §2.3's helper
must refuse; the rest are line references and an enumeration §3 was short by. **The receipt check
worked**: it found in one pass what nine prompt audits had not.

***Rev 10 is a figure refresh and nothing else.*** Rev 9 was committed at `d4084a3`, whose
parent `d35ea87` landed five commits after `8297e58` — prompt 36's build, a new `bzk/audit_pxd032267.py`
and a new `tests/test_audit_pxd032267.py`. **Every line reference in §2.1, §2.2, §2.3 and §3 was
re-verified at `d4084a3` and all of them still hold**, as do the six `ContrastArms` construction
sites, every `site_change_set` call site, and `tests/test_tautology_sweep.py`'s anchors. The new
module touches none of this prompt's subjects. What moved: the four check figures, the `ast.parse`
count and the commit distance, all corrected below and each now stated **with the commit it was
measured at**, so a mismatch tells you the tree moved rather than that this prompt is wrong.

`8d71ec4` wrote rev 1 on 2026-10-10 and its §0 was never run. Revs 2–9 were written 2026-11-07
against `8297e58`, **27 commits later** (`git rev-list --count 8d71ec4..8297e58`), under nine
independent audits. Rev 10 refreshes their figures at `d4084a3`, **33 commits** from `8d71ec4`.

**The three rules are unchanged across every revision; the shape of §2.2 is not** — rev 7
withdrew an option, and that section says why. Each revised passage carries a *rev N* mark in
place. This paragraph neither lists nor counts them: every revision that tried to was wrong.

Rev 2 fixed four stale figures and four falsified assertions. **Rev 3 fixes the four blockers
rev 2's audit found, two of them rev 2's own** (it also folded in that audit's minors, so more
passages carry a *rev 3* mark than four):
- §0.6's reason for `_literal_reads`' blind spot was wrong, and wrong in rev 1 too (*rev 3*);
- §5's Step A claim inverted the section it cited (*rev 3*, correcting rev 2);
- §2.2's mutation asked for a confirmation nothing in this container can run (*rev 3*);
- §2.1's widened-rule exclusion named a site the rule cannot reach — **the same
  exclusion-that-needs-none shape rev 2 faulted rev 1 for, committed in rev 2's fix** (*rev 3*).

Plus §0.5's mis-citation of D6-revised (c), carried unmarked through both earlier revisions.

**Rev 4 fixed §2.2 option (i)**, which could not be built as written: the minted `Contrast` node
carries nothing a stored record id could be compared against. A rev-1 clause that survived two
audits.

**Rev 5 fixes rev 4's own file-state paragraph**, which asserted that
`git diff --numstat 8d71ec4 8297e58` lists two paths. It lists **39**. Two is the count among the
paths this prompt cites, and rev 4 stated it of the command — so a builder running the check would
have found a falsified pre-condition on line one. Rev 5 also narrows rev 4's refutation of rev 1's
option (i), which was right about the conclusion and overstated on the ground.

**Read this before trusting any correction below.** Four audits, and **in each one the previous
revision's fixes were themselves a source of new defects, several reproducing the exact shape they
were repairing** — a wrong exclusion inside the fix for a wrong exclusion, a miscounted file list
inside the paragraph announcing it had stopped miscounting, a bare countable inside the sentence
arguing countables must be measured. No count of those is given here; counting them is how this
paragraph went wrong twice.

**So: a passage marked as a fix is the least settled line in this prompt, not the most.** Verify
every marked claim against the repository before building on it. Where a mark and the code
disagree, the code wins and the disagreement is a finding to report, not a discrepancy to
reconcile.

**No file-state summary is given here. Rev 6 deleted it** — and deleting it, rather than
correcting it a sixth time, is the finding.

Revs 2 through 6 each carried a paragraph summarising which cited files had moved since `8d71ec4`
— rev 1 carried none — and an audit falsified it every time: a list short by three, then by nine,
then a hedged total, then a count asserted of `git diff --numstat` that held only of cited paths,
then a list short by one again. The last omission was `tests/test_pxd032267_gate.py`, **created**
in the range at +1598/−0 and cited at §0.6. No count of the defects is given here; the counts are
what kept being wrong.

**It was the wrong instrument from the start.** `CLAUDE.md`'s single-source rule — *"Each fact has
exactly one home. Cross-reference; never restate"*, and *"Duplicating a fact into a second
document is a defect, not redundancy"* — covers this exactly: a hand-maintained file census in a
prompt header restates facts whose home is the repository. *(Rev 7: rev 6 attributed "measured
numbers live in dated homes" to `CLAUDE.md`. That phrasing is the handoffs' and does not appear
there — `grep -n dated CLAUDE.md` is empty. The restatement half is `CLAUDE.md`'s; the rest was
not.)* No step of this build reads a census, and §0 already makes the builder measure state from
the repository and compare it against stated expectations, which is what a receipt check is for.
So the census is gone and §0 carries the load alone.

**One consequence worth stating, because §0.6 depends on it:** that count tracks file creation, so
it has moved twice. **Seven** at `8d71ec4` (before `tests/test_pxd032267_gate.py`), **eight** at
`8297e58`, **nine** at `d4084a3` (prompt 36's `tests/test_audit_pxd032267.py`). §0.6's expectation
is the figure at `d4084a3`; if you measure eight or seven, you are behind this prompt's commit.

**Re-verified at `d4084a3`:** every line reference, and every count stated as *Expected* in §0,
plus `tables_created` 60. The 1,362 figure was verified **as source text only** — see §2.2, which
records that nothing in this container can re-measure it. **Not re-measured here:** the `claude/*`
branch count, which rev 1 stated as seventeen. It has a home — handoff 10-10 §*Housekeeping*
l.185–188 — and what cannot be checked from this container is the live remote; see *Out of
scope*.

**Why these three together.** They are one shape, not three features: **a rule this repository
already obeys, relied on by a record or a build, and checked by nothing.** Each was found by the
turn that had to work around it, each was carried rather than built, and each would be broken the
same silent way — a green suite over a rule that stopped holding. None adds a capability. The
handoff of 2026-10-10 §6(A) lists them.

**Governing:**
- `notes/REVIEWER-HANDOFF-2026-10-10.md` §6(A), which names all three and why they share a prompt;
- for §2.1: ADR-0038 D5 **l.218–220** — *"a column is bound to a `Sample` in exactly one place per
  format — the adapter's `_sample_columns` — by composing the header from the sample's mapping key
  through the adapter's closed family table **and requiring exact membership in the file's
  header**"*. *Rev 3: rev 1 cited l.218–219 and quoted only the first conjunct; rev 2 widened the
  range to l.218–220 but left the quote half-length, which is the same defect one level in. The
  second conjunct is the one rev 1's quote dropped. `_compose` (l.202–209) implements **both of
  the halves that clause names of it** — composition and the exact-membership test, in one
  expression at l.209, as its docstring l.205 says. The mapping-key and family-table resolution
  the clause also describes sits in the **callers**: `_run_label` l.187–199 strips the key, and the
  `QUANTITY_COLUMNS` resolution happens at l.141, l.176 and l.710 (*rev 8: rev 7 listed two of
  the three*). **Those are not the three `_compose` call sites §0.2 names**, which are l.141,
  l.176 and **l.711** — in `_site` the resolution at l.710 feeds the call at l.711 (*rev 9: rev 8
  asserted the two sets were the same*). (Rev 6 said `_compose` implements "both"
  without that split, which overshot; rev 3 called the bolded clause "the half `_compose`
  implements", which undershot.)* And handoff 10-09 §2;
- for §2.2: ADR-0038 D7's *Where each refusal sits* (l.444–457) and handoff 10-09 §7;
- for §2.3: ADR-0038 D6-revised (a) and (b) (l.350–393), and handoff 10-10 §6(A) item 3;
- `CLAUDE.md` l.95–99, the four-point close.

**Settled ground.** **ADR-0038 is fully built** (handoff 10-10 §1). `ONTOLOGY.md` v1.48. This
prompt builds no decision and amends no record: every rule here is already decided and already
obeyed. It only makes each one checkable.

**This changes no behaviour on any committed input.** No DDL, no id moves, `tables_created` stays
**60** and `ONTOLOGY.md` is **not edited**. ***Rev 9 — but not "every existing test passes
unchanged", which revs 1–8 claimed here.*** §2.2's guard refuses in **seven** unmutated tests of
`tests/test_analysis_differential.py`; §3(b) pre-authorises exactly those edits and §2.2 says why
they are the guard working rather than collateral. Failures on the unmutated tree are those and
nothing else. The only other new
failures possible are the ones this prompt's own mutations produce. That is the claim §3 is built
to falsify.

**Edits are limited to** `bzk/adapters/maxquant_sites.py`, `bzk/analysis/differential.py`,
`bzk/adapters/perseus.py`, `tests/`, and — **for §2.2 only** — `bzk/curation/loader.py`. No ADR,
no `ONTOLOGY.md`, no curation record, no
`ROADMAP.md`, no `HANDOFF.md`, nothing under `notes/` other than this prompt.

***Why the set includes `loader.py`.*** Rev 1 limited edits to three modules and `tests/`, and
§2.2 cannot be built inside that: `ContrastArms` is defined in `bzk/curation/loader.py` l.186 and
constructed at l.679, so the new field lands there. **`site_change_set`'s signature does not
change**, so no caller moves — `bzk/sources/pxd018299_differential.py` is not opened. *(Rev 7:
revs 2–6 opened it for the withdrawn option (ii). §2.2 records why that option is gone.)*

The prompt ends at the report.

---

## 0. Receipt check — answer all of these, then stop and wait

1. **Repository state.**
   - `git log --oneline -3`, `git status --short`. HEAD is this revision's commit, tree clean.
   - Open-of-turn: `uv run pytest`, `uv run pytest tests/test_schema.py`, `uv run mypy bzk tests`,
     both `ruff` targets.
   - Expected **in a container, measured at `d4084a3`**: `1181 passed, 14 skipped`; 20 passed;
     `Success` over 126 files; clean / 126. *(Rev 10. At `8297e58` these were 1104 / 14, 124, 124;
     prompt 36 added `bzk/audit_pxd032267.py` and `tests/test_audit_pxd032267.py` between the two.
     Rev 1 carried 982 / 117 / 117.)*
   - bzk's Mac runs **six more passing and six fewer skipped** — the raw-store tests — so expect
     `1187 passed, 8 skipped`. **That is the relation applied to a measured container figure, not
     a measured Mac figure**; handoff 11-07 §1 records the same relation and marks its own Mac
     number inferred. If your run disagrees, report it rather than reconciling it.
   - **If any of these four disagrees, stop and report before §0.2.** The figures are anchored to
     `d4084a3`; a mismatch most likely means the tree has moved again, which is a finding about
     state, not a licence to adjust anything.
2. **Rule one, and its three obedient callers.**
   - Quote `bzk/adapters/maxquant_sites.py`'s `_compose` with its docstring.
   - List every call site by line, and say how each differs.
   - Expected: **three** — l.141 `_sample_columns` (any family), l.176 `bind_column` (the one
     asked for), l.711 `_site`'s I11 retention (each family in turn).
   - Say what happened the last time this rule was broken, and what caught it.
   - Expected: `_site` composed `f"{prefix}{label}"` itself and tested membership; **nothing
     caught it** — prompt 30's build found it by reading, and routed it through `_compose`.
3. **Rule two, and the field that cannot express it.**
   - Quote `site_change_set`'s signature and its `arms.kind` refusal.
   - Quote `ContrastArms`' field list from `bzk/curation/loader.py`.
   - State why a caller can pass arms belonging to a different contrast than the `contrast` node
     it also passes.
   - Expected: `ContrastArms` carries `numerator`, `denominator` and `kind` and **no contrast id**,
     so the two arguments are independent and nothing relates them.
4. **Rule three, and the five places it is broken.** *(Rev 2: rev 1's heading said four while its
   own Expected said five.)*
   - Run `grep -n "float(row\[" bzk/adapters/perseus.py` and list every line with the method it
     sits in.
   - Expected: **five**, in three methods — l.397 `difference_of`; l.400 and l.405 `result`;
     l.416 and l.421 `untested`. Report what you find; if it is not five, say so before going on.
   - State what each raises on a blank cell and what the message contains.
   - Expected: a bare `ValueError` from `float()`, naming **neither the row nor the column**.
5. **Why `_cell_value` is not the fix.**
   - Quote `_cell_value`'s docstring.
   - State what it returns for a blank cell, and say **why that is right for a quantitative column
     and wrong for a statistics column**.
   - Expected: it returns `None` — blank, unparseable and `NaN` are all absences. For a statistics
     column that would be a silent reclassification: rule (a) must distinguish `0` from *blank*
     (a blank Difference cannot be judged zero), and rule (b) cannot recompute against an absent
     Difference. **Routing the statistics reads through `_cell_value` would turn a malformed row
     into a quietly untested one.**
   - ***Rev 3 — and that is not D6-revised (c)'s shape.*** Rev 1 and rev 2 both said it was. (c)
     (l.394–398) prevents the **inverse**: an untested row minting a `DifferentialResult` with
     log2FC 0, p 1, q 1 *"indistinguishable from a measured null"*. A malformed row silently
     becoming untested is guarded by **nothing** — which is the reason to build §2.3, stated
     correctly.
6. **What an AST guard in this repository looks like.**
   - Count the test modules that call `ast.parse`, then quote what the two named below check.
   - Expected at `d4084a3`: **nine** call `ast.parse` — `test_analysis_differential.py`,
     `test_analysis_record.py`, `test_audit_pxd032267.py`, `test_curation_loader.py`,
     `test_published_cascade.py`, `test_pxd018299_refusals.py`, `test_pxd032267_gate.py`,
     `test_tautology_sweep.py`, `test_ui.py`. (A tenth, `test_curation_content_hash.py`, uses
     `ast.literal_eval` only.) *(Rev 10: eight at `8297e58`; prompt 36's
     `test_audit_pxd032267.py` is the ninth. Rev 1 said "among them", hedging the countable.)*
   - The two to quote: `tests/test_tautology_sweep.py` (every equality in every assert) and
     `tests/test_analysis_record.py` (`_literal_reads`, string keys read off a receiver).
   - Say what `_literal_reads`' known blind spot is. Handoff 10-09 §7 l.259 records **that** it
     is open and gives **no reason**, so read `_is_receiver` and state the reason yourself.
   - Expected: it cannot see a key read off `json.loads(...)`. ***Rev 3 — not for the reason rev 1
     and rev 2 gave.*** They said *"the receiver is a call and not a name"*; `_is_receiver`
     (`tests/test_analysis_record.py` l.142–147) **accepts a call** whose `func` is an `ast.Name`
     in `receivers`, and l.56 says so — `_record()["n_sites_tested"]` counts. The real reason is
     narrower: `json.loads` is an **`ast.Attribute`**, so `node.func` is not an `ast.Name` at all
     and fails the second test. **An AST guard sees syntax, not behaviour** — §2.1 must say what
     its own blind spot is, and must get the reason right, not just the symptom.

**Do not start §1 until bzk replies.**

---

## 1. What this prompt builds

Three guards. Each closes a class, none changes behaviour.

**The reading this prompt adds, and it applies to all three:** *a guard that cannot fail is worse
than no guard, because it reads as coverage.* Every one of these must be made to fail by a
mutation that is itself read back — and for §2.1, the mutation is the historical defect: restore
`_site`'s own composition and the guard must catch it.

---

## 2. The build

### 2.1 `maxquant_sites.py` — only `_compose` composes

- A test parsing `bzk/adapters/maxquant_sites.py` with `ast` and refusing any **f-string or
  concatenation that joins a `QUANTITY_COLUMNS` prefix to a label** outside `_compose`.
- ***Rev 2 — the exclusions rev 1 named were wrong, and it missed the real one.*** `_run_label`
  (l.187–199) performs **no join at all** — `key.startswith(p)` l.193, `key[len(prefix):]` l.199 —
  so prefix stripping is not reachable by the stated rule and needs no exclusion. The actual false
  positive is **`bind_column`'s refusal message, l.178–183**: four implicitly-concatenated
  adjacent string literals — **three f-strings and one plain literal** (l.182) — form one
  `JoinedStr` carrying both `{label!r}` (l.179) and `{QUANTITY_COLUMNS[quantity]!r}` (l.181). So
  rev 1's "the three existing callers pass unchanged" is **false for `bind_column`** under the rule
  as written. *(Rev 3: rev 2 called all four f-strings.)*
- Exclude refusal-message strings, and say in the test that they are excluded and why: a message
  that *names* a prefix and a label is not a composition that *binds* one. If you widen the rule
  to `QUANTITY_COLUMNS.values()`, **l.196–198** (`_run_label`'s message, `QUANTITY_COLUMNS` at
  l.197 in the same `JoinedStr` as `{key!r}`) comes into range too.
- ***Rev 3 — rev 2 also named l.143–144 here, and it is not reachable.*** `_sample_columns`'
  message references **no `QUANTITY_COLUMNS` at all** (only `{label!r}` and `{key!r}`), so no rule
  keyed on a `QUANTITY_COLUMNS` prefix can reach it, widened or not. **That is the same
  exclusion-that-needs-none defect rev 2 faulted rev 1 for, committed inside rev 2's own fix** —
  worth knowing before you trust any exclusion list here, this one included. Name only what your
  rule actually reaches, and show the match set.
- ***Rev 4 — a third message `JoinedStr` carries `QUANTITY_COLUMNS`, and no revision has named
  it.*** `bind_column`'s unknown-quantity refusal, l.163–166, puts `{quantity!r}` (l.164) and
  `sorted(QUANTITY_COLUMNS)` (l.165) in one implicitly-concatenated `JoinedStr`. It reads the
  dict's **keys**, not a prefix value, so a rule keyed strictly on prefixes misses it — but that
  is a fact to establish from your match set, not to inherit. **This is why §2.1 asks for the
  match set printed rather than an exclusion list recited:** three revisions of hand-maintained
  exclusions have been wrong in both directions.
- **Distinguishing a message from a binding is the guard's hard part, not an aside.** State the
  discriminator you used.
- **State the blind spot in the guard test's own docstring**, not `_compose`'s — §2.1 writes a
  test and leaves `bzk/adapters/maxquant_sites.py` **unedited at the commit**. Its mutation below
  does edit that module and is reverted before the report, as `CLAUDE.md` point 2 requires
  (*rev 8: "the docstring" was ambiguous through rev 7; rev 9 adds the at-the-commit qualifier
  here rather than only in §4*). An AST guard sees syntax. A caller that builds the
  same string by `str.join`, `%`, `.format`, or through a local variable, defeats it. The guard
  catches the shape the defect actually took (`f"{prefix}{label}"`) and the obvious neighbours, and
  it is a tripwire rather than a proof.
- **Mutation:** restore the pre-prompt-30 composition inside `_site` — the real historical defect —
  and show the guard fires. ***Rev 11: there were two, not one.*** At `402fce8^`, `_site` built
  `f"{prefix}{label}"` at **l.651** (inside `maxquant.cell_value(row, column, …)`) and again at
  **l.655** (the membership test `if f"{prefix}{label}" in column`). **Restore both lines**, and say
  whether your guard catches each.
- ***Rev 11 — key the guard on shape, never on parameter names.*** Inside `_site` the names are
  reversed against the other callers: `column` is the header-to-index mapping (l.568) and `header`
  is the **composed column name** bound by the walrus at l.711, whereas in `bind_column` `header` is
  the header collection. A guard keyed on identifier names would miss `_site` and is the shape
  §2.1's rule already avoids — confirm that from the match set rather than assuming it.

### 2.2 `differential.py` — arms must belong to the contrast

**This section was rewritten in rev 7, and the shape it builds is now specified rather than
delegated.** Revs 1–6 offered two shapes and told the builder to argue for one; six audits later,
two of the three blockers in rev 6 were in that delegation. The reason is below, under *What rev 7
removed*. Build what this section says and nothing else.

- `site_change_set` **refuses** when its `arms` do not belong to its `contrast`.
- **The relation is established by the minted `Contrast` node id.** `ContrastArms` gains that id,
  and the check compares it against `contrast["id"]`.
  - It is in hand at `bzk/curation/loader.py` **l.683** as `contrast_nodes[handle]["id"]`, in the
    `contrast_arms` comprehension (l.678–690) that builds every `ContrastArms`.
  - `site_change_set` already reads `contrast["id"]` (`bzk/analysis/differential.py` l.157), so
    **the contrast side needs no new plumbing**; the arms side is the field this builds. *(Rev 9:
    rev 8 said "both sides of the comparison exist today", which is true of the value at loader
    l.683 and not of the field.)*
  - **Not the record handle.** The handle *is* `entry["id"]`, the record's declared contrast id —
    `arms[entry["id"]]` at loader **l.410** (in `_resolve_arms`), `contrast_nodes[entry["id"]]` at
    **l.643** — but the minted node's properties are `numerator`, `denominator`, `label` plus the
    digest `id` (l.641–647) and **carry no handle**, so a stored handle would have nothing on the
    `Contrast` to compare against. Rev 1 specified the handle against the node; that was the one
    unbuildable thing in this section and it survived two audits.
- **This must not make `ContrastArms`' id identifying or reach any node's properties.** The arms
  are non-identifying (D4) and nothing here changes that. The new field is read by the check and
  by nothing else.
- **Where the check sits: after the `Contrast`-shape refusal at l.152**, so `contrast["id"]` is
  known good before it is compared, and **before the `Contrast` is staged at l.158** — not before
  the body stages anything, since the `Analysis` (l.145), `USED` (l.146), `Imputation` (l.149) and
  `IMPUTATION_FOR` (l.150) are already appended by then (*rev 9: rev 8 said "anything"*).
  *(Rev 8: placement was
  unspecified through rev 7. It matters — `tests/test_analysis_differential.py` l.289–300 passes
  `contrast=dataset` and expects l.152's message, so a check placed earlier changes which refusal
  fires.)*
- **Mutation:** `data/curation/curation_PXD018299.json` declares two contrasts
  (`KO_IFN_vs_WT_IFN` and `KO_vs_WT_unstimulated`), both of kind
  `condition`, so the existing l.111 refusal pre-empts nothing in either direction. Construct the
  mismatched pair from the loader, call, and read the refusal back. One mutation, a runtime
  failure, read back — as §1 and `CLAUDE.md` point 2 require of every guard here.

***Rev 8 — this guard breaks seven existing tests, and that is the guard working.***
`tests/test_analysis_differential.py` pairs a **synthetic** `Contrast` with **real** arms:
`CONTRAST = _anchored_contrast(…)` at l.51 is anchored on `"bzk:experiment-test"` (l.42–48), while
`CONDITION_ARMS` at l.57 is `load_path(REAL_RECORD).contrast_arms["KO_IFN_vs_WT_IFN"]`, whose node
is anchored on the real record's `Experiment`. **Measured, 2026-11-07:**

```
synthetic CONTRAST id: bzk:07d797bc191de20d9f0ef71c5726bbe8
real loader node id  : bzk:8f9a06344675831a26dd59b2bf8c4393
```

So every unmutated call in that module pairing the two **refuses** once this check exists:
**four calls — l.110, l.188, l.228, l.274 — driving seven tests** (l.130, 145, 157 and 204 through
`_write` at l.110; l.175, l.218, l.270).

*Rev 9: rev 8 also listed l.292 and still said seven. It does not pair them — l.289–300 passes
`contrast=dataset`, so with the check placed after l.152 as specified above, l.152 refuses first
and the new check never runs. §3 makes an unlisted site touched **or** a listed site untouched a
finding either way, so that entry would have forced one or the other.*

That is not collateral damage: those four calls exercise precisely the state the guard forbids,
arms resolved from record R against a contrast that is not R's. **The tests are the mismatch.**

**So they change, and the change is pre-authorised** (§3 E1 lists it): `CONTRAST` becomes the
loader's node for the same handle `CONDITION_ARMS` comes from —
`load_path(REAL_RECORD).contrast("KO_IFN_vs_WT_IFN")` — and `_anchored_contrast` goes if nothing
else uses it. **One consequence to report rather than smooth over:** l.284's
`assert staged == [CONTRAST]` pins ADR-0029 E, that this function mints no `Contrast`. It still
pins it — staged must equal the node passed in — but the node is no longer *recognisably*
un-mintable here, which is what made the synthetic one load-bearing. Say in point 3 whether that
test is weaker for it, and do not strengthen it by inventing a second contrast the record does not
declare.
- **The same pair exists in `perseus.py` and is NOT guarded here. Report the class as open**
  (*rev 9*). `DeclaredContrast` (**l.265**–283; l.264 is its `@dataclass` decorator) carries
  `contrast: Mapping` (l.282) and
  `arms: ContrastArms` (l.283) just as independently: l.609 anchors every result on
  `str(declared.contrast["id"])` while `_prove` binds and recomputes over `declared.arms` (l.941).
  A mismatched `DeclaredContrast` attributes results to contrast A while proving the binding over
  B's arms — the identical defect in a second producer.

  **Rev 8 required guarding it here, citing `CLAUDE.md` point 3. Rev 9 withdraws that, because the
  guard has a design question in it that a build prompt cannot settle:** what "belong" means.
  - The check specified above enforces **identity** — these arms were minted for this contrast.
  - `tests/test_perseus.py` l.1312 `test_the_count_is_per_contrast` **deliberately** pairs a second
    contrast (`other_node`, l.1315) with the module's existing `ARMS` (l.1316), because its subject
    is one row untested under one contrast and tested under the other. It relies on **extension** —
    these samples are this contrast's arms — and an identity check breaks it.
  - `tests/test_perseus.py` **l.468** pairs `_anchored_contrast("KO", "WT")` with `ARMS` **outside** its
    `pytest.raises` block at l.472, so a construction-time refusal makes that test **error** rather
    than fail, while it is testing an unrelated refusal. *(Rev 11: revs 9–10 cited l.461, which is
    the `def`. The substance holds — the pairing precedes the `raises`.)*
  - `DeclaredContrast` is a frozen dataclass with **no `__post_init__`** today, so this is a new
    method, not the one-line comparison rev 8 called it.

  **Identity or extension is a decision**, and on `CLAUDE.md`'s own terms point 3 is satisfied by
  reporting the class **open** with its instance and its blocking question named — which is what
  this prompt does. It is not closed by this build. Say so in point 3, name
  `DeclaredContrast`, and name the identity-versus-extension question. Do not guard it here.
  *(Five of §3(a)'s six construction sites are `DeclaredContrast` arms — rev 8 said three — so
  they move for the field regardless; none of them needs a new check.)*
- **Say what this does not catch.** Both checks relate `arms` to `contrast`; neither relates
  either to `dataset`. A caller can still pass a `dataset` node from one record with a
  contrast/arms pair from another, and that stays representable and unguarded. Report it; do not
  build it — it needs a `dataset`-side relation that neither type carries.

***What rev 7 removed, and why it is a finding rather than a simplification.*** Revs 1–6 also
offered **(ii)**: `site_change_set` takes the arms keyed, or takes the handle and looks them up,
"so the mismatch is unrepresentable rather than refused" — and called it the stronger shape. Two
things went wrong with that, both caught at the sixth audit:

- **(ii) named two different designs.** Under *keyed arms* the caller still supplies an arms map
  and a `contrast` node independently, so the mismatch stays fully representable; only the
  *handle-lookup* form, where the function derives both the node and the arms from one key, makes
  it unrepresentable. Rev 6 told the builder there was no refusal to show under (ii) — so a builder
  taking the keyed form would have shipped `site_change_set` **with no check at all**, strictly
  worse than today.
- **Rev 6's claim that (ii) has no runtime mutation was false.** `arms` is used in
  `site_change_set` for exactly one thing — its `kind`, tested at l.111 and echoed in the refusal
  message at l.114. Under the handle-lookup form the mutation is the lookup itself — resolve the
  arms under a different handle than the contrast — which is a one-line change to the new code,
  catchable at runtime and readable back. Rev 6 dropped E2's count to four on the strength of that false claim, which would
  have left this guard verified by nothing.

**(ii) may still be the better design, and that is a decision, not a build step.** It belongs in an
ADR or in bzk's hands, not improvised inside a build prompt — this prompt amends no decision
(header). If it is taken later it is a follow-up on top of (i), with its own pre-registration.

- ***Rev 3 — what the unmutated confirmation can and cannot be.*** Rev 1 and rev 2 asked you to
  *"confirm the unmutated tree still writes the 1,362-result change-set"*. **Nothing in this
  container can run that.** Both assertions of 1,362 are in `tests/test_query_real_graph.py` —
  l.88 and l.242 (*rev 4: rev 3 said "every assertion … is in l.88", naming one of two*) — and all
  eight of that module's tests skip here for a missing graph at `~/.bzk-omics`; the
  deposit-dependent
  paths skip for a missing raw store; and `pxd018299_differential.py`'s `main()` needs the deposit
  and writes. §3 is headed *this container* and §5 is *Nothing*, so there was no home for it.
  **Confirm the change-set's shape on fixtures instead** — that the unmutated call still returns
  one `Analysis` plus one `DifferentialResult` per result with its arms accepted — and say plainly
  that the 1,362 figure is not re-measured by this build.

### 2.3 `perseus.py` — a statistics cell that is not a number

- Every statistics read names the row and the column when the cell is not a finite number.
- ***Rev 11 — "not finite" is wider than "unparseable", and the gap is live.*** `float()` accepts
  `NaN`, `inf` and `-Infinity` without raising (measured at `d369216`). So the helper must refuse
  **non-finite values as well as unparseable text** — the wording above already covers this and
  the implementation must not narrow it to a `try/except ValueError`.
  - **Report the consequence the build's §0 surfaced**, which is a pre-existing defect and not
    this prompt's to fix: a `NaN` Difference fails `untested`'s `== 0.0` test (because
    `NaN == 0.0` is `False`), so such a row reads as **tested** and mints a `DifferentialResult`
    with `log2fc` `NaN`. Name it in point 3; do not build it.
  **Do not route through `_cell_value`** (§0.5): a malformed statistics cell is a refusal, not an
  absence.
- One helper, used by all five sites §0.4 found, so the message is one sentence in one place.
- ***Rev 3 — the signature change this forces, and its blast radius.*** The message must carry the
  file line number, and `_ContrastColumns.difference_of`, `result` and `untested` (l.396–422) take
  only `row`. `line_no` is in scope at all three **loop-level** call sites, under **two different
  loops** both spelled `for line_no, row in rows:` — `result` at l.662 under the loop at **l.612**
  (in `parse`), and `untested` at l.960 with `difference_of` at l.978 under the loop at **l.957**
  (in `_prove`). **Two further calls are internal**, `difference_of` from `result` at l.402 and
  from `untested` at l.419, so both of those gain `line_no` themselves (*rev 8*). So **all three method signatures change.** *(Rev 5: rev 4 put all three under l.957.
  Rev 3 had listed l.957 and l.660 as call sites, when l.957 is a loop header and l.660 reads
  `untested_lines`. The substance has held throughout — `line_no` is in scope at all three.)* Every caller is inside `bzk/adapters/perseus.py` — none in `tests/`,
  none in `bzk/sources/pxd055843_perseus.py` — so this stays inside the edit set, and
  `PerseusError(ValueError)` (l.260) keeps the change compatible with every handler that catches
  `ValueError`, in bare or tuple form. *(Rev 4: rev 3 said "the seven `except ValueError` sites".
  Seven is the count of the bare literal across `bzk/` and `tests/`, only one of which is in
  `perseus.py`, and none of which can catch these raises — a vacuous countable. The subclassing
  claim is the real basis; the count was not.)* Confirm both the caller locality and the
  subclassing from the repository rather than taking them from here.
- The message carries: the file line number, the column name, and the raw cell as it appeared.
- ***Rev 2 — rev 1 said prompt 31's four refusals "already name line and column". Three do not.***
  Measured in `bzk/adapters/perseus.py`: l.944–950 (unplaced arm sample) names the contrast suffix
  and sample ids, **neither line nor column**; **l.968–973 (non-finite arm value) names line and
  column — the only one that does**; l.981–986 (deviation) names the line and the arm
  **column-name** lists (`numerator` / `denominator`, built at l.951–952 as `column_of[s]`) without
  singling out an offending column — *rev 3: rev 2 called these value lists*; l.990–993 (nothing
  left to test) names **neither**. Follow **l.968–973** for form.
- **The absence/refusal line must be stated where the helper lives**: a quantitative column's blank
  is an absence (I19, `_cell_value`), a statistics column's blank is a malformed row. Both rules
  are correct and they are not interchangeable.
- **Mutation:** a fixture row with a blank Difference, one with a blank q, and one with a
  non-numeric statistic — each refused, each naming its own column.

---

## 3. Pre-registration — this container

**Not rehearsed.**

**E1 — nothing changes on committed input.** `uv run pytest` passes with **no existing test
edited** except where a new refusal needs a case. State any test you did edit and why.
`tests/fixtures/` unchanged except for fixtures §2.3's mutations need; name them.

***The test edits §2.2 forces, pre-authorised — two sets, not one.*** Both are part of the build,
not exceptions to E1:

**(a) `ContrastArms` gains a field, so every construction site moves. Repo-wide, exhaustively** —
`tests/test_perseus.py` l.80 and l.1267, `tests/test_query.py` l.650, `tests/test_ui.py` l.501,
`tests/test_adapter_dispatch.py` l.88, and `bzk/curation/loader.py` l.679, the only production
site. Six, no others.

**(b) The new refusal breaks tests that pair a synthetic contrast with real arms** — see §2.2's
measured ids. In `tests/test_analysis_differential.py` only: `CONTRAST` l.51, `_anchored_contrast`
l.42–48 if nothing else uses it, and the four calls at **l.110, 188, 228, 274**.

**The module holds six `site_change_set` calls; two are correctly untouched, and both are named
here so the unlisted-site rule below is not misread** (*rev 11 — revs 9–10 named only the first*):
- **l.292** passes `contrast=dataset`, so l.152's shape refusal fires before the new check.
- **l.325** (`test_D7_an_ip_kind_is_refused_at_the_producer`) passes the loader's **matched**
  contrast and arms for one handle, so the new check passes and l.111's kind refusal fires as that
  test intends. **Nothing in `tests/test_perseus.py` moves for a check**, since rev 9 guards only
`site_change_set`; those arms move for the new field alone, under (a).

*(Rev 8: rev 7 listed only (a) and called it exhaustive, while the next clause makes an unlisted
site a finding — so every site in (b) read as a defect. Rev 7's own note faults rev 3 for that
shape with the roles reversed. Rev 9 drops l.292 and the `perseus.py` entry rev 8 added.)*

Report the sites you actually touched against this list; a site here you did not touch, or one you
touched that is not here, is a finding either way.

***One further edit the suite will force, pre-authorised — and its tooling is broken.***
`tests/test_tautology_sweep.py` requires every equality in every assert in every `.py` under
`tests/` **that Pass C or Pass D matches** to appear in `PINNED` (`PINNED` l.203), so any new guard
or mutation test of that shape fails that module until classified. Regenerating `PINNED` and
writing the classification comment **is part of this build**, not an exception to E1 — after
classifying what is new, never before.

***Rev 11 — two corrections here, both from the build's §0.*** Revs 2–10 said the module requires
**every** equality to be pinned, repeating the claim its own docstring (l.10–11) makes. `sweep()`
walks every equality but increments `found` **only when `hit` is true** (`if hit:` l.193, `found[…] += 1` l.194), so a
comparison against a literal display is never pinned — the floor comments say as much. The code
wins; the docstring's over-claim is a finding to report, not something to fix here.

**And the regenerate command at l.201–202 does not reproduce `PINNED`'s shape.** It prints
`sorted(sweep()[0])`, and `sweep()[0]` is a `Counter` keyed by `(module, source)`, so `sorted` of it
yields **2-tuples**; `PINNED` holds `(module, source, count)` **3-tuples**. Measured at `d369216`:
sorted width 2, `PINNED` element width 3. **Fixing that comment is in scope** — the file is already
authorised and the build cannot regenerate `PINNED` without a working command. Use
`sorted(sweep()[0].items())` or equivalent, state what you changed it to, and report the old
command as a defect that would have silently produced the wrong shape.

**E2 — each guard fails under its own mutation, and the mutation is read back.** **Five, and five
is the count:** §2.1's historical restoration; §2.2's wrong-contrast arms; §2.3's three malformed
cells. *(Rev 6 made it four on a false claim that §2.2's then-preferred shape had no runtime
mutation; rev 7 restored five but hedged it as "at least"; rev 8 made it six by adding a
`DeclaredContrast` guard that rev 9 withdraws. Five.)*

**E3 — `tables_created` stays 60, no id moves, `ONTOLOGY.md` is not edited.**

**E4 — the AST guard's blind spot is demonstrated, not just described.** Write the composition a
way the guard does **not** catch, show it passes, and keep that as a documented limit rather than
widening the guard until it catches everything. A guard whose limits are measured is worth more
than one whose limits are assumed.

***Rev 2 — where that demonstration lives.*** **Not in `bzk/adapters/maxquant_sites.py`**: a real
uncaught composition written into the module would violate §2.1's own rule and E1/E3's
no-behaviour-change claim. Put it in a source string the test parses, or a test-local fixture
module under `tests/`. Say which.

| Check (target) | Before | After, predicted |
|---|---|---|
| `uv run pytest` (full) | 1181 passed, 14 skipped (`d4084a3`) | all pass; state the counts |
| `uv run pytest tests/test_schema.py` | 20 passed | 20 passed, file unedited |
| `uv run mypy bzk tests` | Success, 126 files (`d4084a3`) | Success; state the count |
| `ruff check bzk tests` / `ruff format --check bzk tests` | clean / 126 (`d4084a3`) | clean; state the count |

**If any prediction fails, stop and report. Do not adjust code, fixtures or pins to match.**

---

## 4. Commit and report

**One commit**, fast-forwarded onto `main`, single subject line naming the three guards and that
no behaviour changes.

**Files expected at the commit:** `bzk/analysis/differential.py`, `bzk/adapters/perseus.py`,
`bzk/curation/loader.py`, `tests/`. Any file beyond those needs a reason.

**`bzk/adapters/maxquant_sites.py` is edited during the build and not at the commit** (*rev 8*):
§2.1 writes a test, its mutation restores the historical composition in that module and is then
reverted, and E4's uncaught composition lives in a test-local source string. If it appears in
`git diff --stat`, say why. *(Rev 4: rev 2 widened the edit set for §2.2 and left this list
unwidened, so a file the build requires read as an exception needing justification. Rev 7: one
shape, so `loader.py` is required rather than one-of.)*

**Report:** the commit hash; §0's answers; E1–E4 as measured; §3's table with "After" measured;
each new refusal's message on the unmutated tree; the mutation evidence; `git diff --stat`; the
four-point close. **In point 3, say for each guard what it does not catch** — §2.1's blind spot
measured, §2.2's `dataset` gap as that section states it, §2.3's reads that are not statistics
columns.

Then stop.

---

## 5. For bzk's Mac

**Nothing.** No behaviour changes on any committed input, so there is nothing to re-measure.

***Rev 2 — rev 1's reassurance was misattributed, and it was a write.*** Rev 1 credited "the
`differential_table` query from prompt 32 §5" and `platform_targets.json` byte-identity to that
section. Prompt 32 §5 is headed *"a read-only query, no write"*, says **"Nothing is written"**, and
contains neither string. Re-running `bzk/sources/pxd018299_differential.py` calls
`store.write_change_set` at **l.525**, so the check is a write.

**The byte-identity check has two homes, not one** (*rev 3*): handoff 10-09 **§4.3** (l.143–152),
and the implementation at `bzk/sources/pxd018299_published_cascade.py` l.194–198, declared in that
module's docstring l.15–16 — *"must reproduce the committed `pxd018299_platform_targets.json` byte
for byte, or nothing is written"*.

***Rev 3 — and rev 2 inverted §4.3 in the same breath as correcting rev 1.*** Rev 2 said the check
*"needs its own Step A snapshot before the pull (handoff 10-09 §4.3)"*. §4.3 says the opposite: the
2026-10-08 cold rebuild left **no prior state**, which is precisely why byte-identity *became* the
id check — **the committed fixture is the before-state, so no snapshot is needed.** The
Step-A-before-the-pull rule in that same section is for a **graph-level id sweep**, because
`rebuild` drops the stores (`bzk/rebuild.py` l.154). Rev 2 also cited "§4.3 (l.83, l.147)": l.147
is in §4.3, **l.83 is in §3** (*Dated home*, l.75–95).

So: **there is no read-only reassurance to offer here**, and if the byte-identity check is ever
wanted it belongs in its own prompt as a write that needs no snapshot — not under a §5 headed
*Nothing*. What prompt 32 §5 does support, read-only, is that all 1,362 `DifferentialResult`s map
to *stoichiometry-uncorrected*.

---

## Out of scope

- **Order item 3** (PXD018299's `ISG15_interactome`, the first real IP ingestion) — handoff
  10-10 §6(B). The protein-groups binding and M8's silently dropped family belong there.
- **The untested derivation's one-external-analysis-per-`Dataset` assumption** (handoff 10-10 §7).
  Unguarded, and a fourth item of this same shape — but it needs a second external analysis to
  exist before a guard means anything.
- **`_literal_reads`' blindness to `json.loads(...)["contrast"]`** — a fifth, and the same shape
  again. Its own prompt.
- **ADR-0032 taking D6-revised (c) into its review** (ADR-0038 l.399). Overdue; not a build.
- `write_cells` over-reporting; the drift checker; the stale tautology floor; F-b; F-d; R6's
  prefix-only check; the D2/D3 invariant-level check; I22's reliance on a single `Contrast`
  minter; `pxd055843_perseus.py`'s stale module docstring; the stale `claude/*` branches on the
  remote.

***No branch figure is stated here, and after several revisions that is the point.*** Rev 1
printed one; it went stale. Rev 2 explained why printing one was wrong and then printed one. Rev 3
dropped it and mis-described the figure's history. Rev 4 corrected that history by printing two
further figures inside the paragraph arguing against printing them. **So this paragraph gives no
branch figure** — the measured count already has a home, handoff 10-10 §*Housekeeping* l.185–188,
and this out-of-scope pointer is not it.

**For whoever re-measures it into that home:** `git ls-remote --heads origin | grep -c
'refs/heads/claude/'`, run against the GitHub remote. A clone whose `origin` is another local clone
reports zero, because the `claude/*` refs exist only on GitHub — three audits of this prompt hit
that, and one reported the zero as a finding. Read 10-10 §*Housekeeping* before recording anything:
it already documents one correction to this count, and what the correction was.
