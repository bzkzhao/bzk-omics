# REVIEWER CONVERSATION HANDOFF — 2026-11-07

**For the incoming reviewer agent.** This does **not** supersede
`notes/REVIEWER-HANDOFF-2026-11-07b.md`, which stays the starting point for
*state*. This file is for *role*: what the reviewer does, what it must not do,
and which two questions to open with.

**Read in this order, and stop after the second:**

1. `notes/REVIEWER-HANDOFF-2026-11-07b.md` in full — state, open list, and §6's
   conventions.
2. `CLAUDE.md` — the single-source rule (l.38–53) and the four-point close
   (l.95–99).

Everything else is cited where it is needed. Do not read the whole repository
first; §2 below says why.

---

## 1. State, as the delta only

- **`main` at `8654365`**, linear, no merges, **37 commits** from `8d71ec4`.
- Figures live in 11-07b §1 **with the commit each was measured at**. Do not
  restate them here or anywhere else; cite that section.
- Nothing is in flight. No prompt is open, no build session is running, no
  patch is awaiting application.
- Stale `claude/*` branches on the remote: 11-07b §5 carries the count and its
  caveat (a clone whose `origin` is another clone reports zero).

## 2. What the reviewer is for

The loop (11-07b §6; 10-10 conversation handoff §4): **Claude Code output
pasted → reviewer verifies against an independent clone and reports → reviewer
writes one prompt → an independent checker audits the prompt → reviewer folds
in valid corrections and reissues in full.**

Four things that are not obvious and cost real time when missed:

- **Verify, never accept.** Checker findings and build reports are both audited
  against the repository. On 2026-11-07 a checker reported a branch count of 0
  as a blocker; it had measured against a local clone whose `origin` was another
  clone, and the real figure was 19. A build report that session was right on
  all seven of its findings — and it was still checked.
- **Measure, do not recite.** Every countable in a prompt is measured at a named
  commit before it is written down. 11-07b §6 records the failure mode that ran
  through nine audit rounds: countables one level short, in the same direction,
  often inside the sentence claiming they had stopped being short.
- **Prompts land as bzk's commit first.** Send him the terminal commands; he
  commits and pushes; only then is a build session released. Shell sent to him
  must run as pasted — no `<placeholder>` angle brackets (zsh redirection), no
  trailing `# comments` (his zsh passes them as arguments), never `git add -A`,
  and a new patch filename for every revision.
- **§0 earns its weight.** Nine prompt audits found twenty-three blockers; the
  build's §0 receipt check then found seven more in one pass, one of which would
  have stopped the build. §0 executes against the repository where an audit only
  reads it. Keep §0 heavy; audit the prompt lightly by comparison.

## 3. What this conversation does first — two decisions, framed not taken

**Both are bzk's to make. The reviewer's job is to put each one in front of him
with the evidence attached and the consequences named, and then stop.** Neither
is a build. Do not write a prompt for either.

### 3.1 ROADMAP open questions 1 and 3 (11-07b §5.1)

`ROADMAP.md` l.12784–12789 holds five. Two are live:

- **Q1 (l.12786):** *does v0.1 ship publicly, or is it a private proof that the
  ontology holds?*
- **Q3 (l.12788):** *does a paper come out of this, and if so is the target the
  tool or the ISGylation biology it enables?*

**What to put in front of him, and it is already measured.** 11-07 (02:20) §3
bears directly on Q3's second half. **Read its readouts B, C and D from there
rather than from here** — that section is their home and this brief does not
restate figures. In shape: the third deposit's headline target survives only a
small minority of draws, D7 recurs across a majority of the exposed claims at
low `n`, the fully measured claims collapse entirely once match-between-runs is
withheld, and one registered expectation missed with no post-hoc mechanism
offered. Every one of those numbers carries *second attempt, after a
registration defect; test identified exploratorily*.

**The reviewer's framing, not its verdict:** that pattern is evidence *about
published claim durability*, which is a tool-and-method result. It is not
ISGylation biology. If Q3 resolves to *the biology*, the open list has nothing
on it that serves that paper; if it resolves to *the tool*, 11-07b §5.2 (the
four FINDINGS figures) becomes the critical path, because a paper needs those
from one command.

**Note what Q1 and Q3 do *not* gate.** `ROADMAP.md` l.12791–12793 is the
worked precedent, on Q4: an open question was read as blocking a dependency
redraw, the reading was tested by running both branches, and it moved nothing.
Its closing line is the standard — *"evaluating a decision already executed is
not the same as blocking one not yet taken, and conflating the two is what
turned an open question into a stop."* Apply that test before letting either
answer gate anything. Also live but not urgent: **Q2, the licence** (l.12787),
which bears on whether a commercial fork is acceptable and therefore on Q1.

### 3.2 Identity or extension — the question blocking `DeclaredContrast`

11-07b §5 carries this as reported-not-built. The facts, all at `8654365`:

- `DeclaredContrast` (`bzk/adapters/perseus.py` l.311–312) carries `contrast`
  and `arms` as independently chosen arguments, exactly as `site_change_set`
  did before `f61f6fd`. l.643 anchors every result on
  `str(declared.contrast["id"])` while `_prove` binds and recomputes over
  `declared.arms` (l.979). A mismatched pair attributes results to contrast A
  while proving the binding over B's arms.
- **The guard `f61f6fd` built for `site_change_set` enforces identity**: these
  arms were minted for this contrast, compared by the minted node id.
- **`tests/test_perseus.py` l.1383 `test_the_count_is_per_contrast` relies on
  extension**: it deliberately pairs a second contrast with the module's
  existing `ARMS`, because its subject is one row untested under one contrast
  and tested under the other. An identity check breaks a test whose whole
  purpose is that scenario.
- `DeclaredContrast` is a frozen dataclass with **no `__post_init__`**, so the
  check is a new method rather than a line.

**The question for bzk:** does *belong* mean the arms object was minted for this
contrast (identity), or that these samples are this contrast's arms
(extension)? They differ wherever two contrasts legitimately share arm samples.

**Why this is an ADR and not a prompt.** `f61f6fd` already answered it one way
for one producer without the question being asked. A second producer answering
it the other way, or the same way at the cost of a test built on the opposite
reading, is a decision about the ontology's vocabulary. `CLAUDE.md`'s
single-source rule applies to the *answer*: it needs one home, and that home is
a decision record. ADR-0032 is the adjacent one and is already `Proposed` and
owed two inputs (§4.1 below) — whether this belongs inside it or in a new ADR
is itself worth asking.

**Do not resolve it by widening the existing guard.** On 2026-11-07 a prompt
revision tried to specify this for `DeclaredContrast` as a bolt-on; it was
withdrawn at the sixth audit precisely because the design question surfaced.
11-07b §6's third convention — distrust passages marked as fixes — came from
that.

## 4. Then, in the handoff's own order

11-07b §5 is the list. Notes the reviewer needs that are not in it:

### 4.1 ADR-0032, and why it moved

Still `Proposed` (`decisions/0032-…md` l.5), overdue since 10-10. It is titled
*what the Perseus adapter reads and whether the platform converts*, and
`f61f6fd` changed exactly that: every statistics read now goes through
`_statistic` (l.264) and refuses a non-finite cell. **So it owes two inputs —
D6-revised (c), and §2.3 of prompt 33.** This is the oldest open item and the
one whose subject has moved most since it was written.

### 4.2 The four FINDINGS figures (11-07b §5.2)

**Measure before scoping.** Prompt 36 added `bzk/audit_pxd032267.py` as a
*separate* ten-stage audit. Whether it moved any of §1 census, §2 two-route
downshift, §5 changing-support count or §6 q-ranges is **unmeasured** — it was
deliberately left so rather than guessed. Settle that first; it decides whether
this is one prompt or several.

### 4.3 Instrument items, each a one-line fix with a measured home

- `walk/FINDINGS.md` l.3 opens *"Two deposits"* — **wrong by one** since
  PXD032267, whose audit prompt 36 then built. It sits in the document a paper
  would draw from.
- `bzk/sources/pxd018299_h10.py` l.164 `MATCH_TOLERANCE = 1e-6`, the defect
  behind the withdrawn S1 finding.
- `tests/test_tautology_sweep.py` l.2301: the floor still moves **only by
  hand** — `f61f6fd` moved it manually; 11-07b §5.5 carries the figures.
- `tests/test_tautology_sweep.py` l.10–11 **over-claims**, saying every equality
  is pinned where only Pass C/D matches are (`if hit:` l.193). It is the source
  prompt 33 inherited its own wrong wording from. Unfixed.

### 4.4 Blocked on the PI

- **PXD055843's block is the imputation *seed*, not whether imputation ran.**
  `data/curation/curation_PXD055843.json` states the method from the paper's
  methods and puts only the seed and the "Perseus defaults" values in
  `unresolved`. Earlier handoffs frame it as the broader question; the record
  does not.
- Order item 3 (PXD018299's `ISG15_interactome`, the first real IP ingestion)
  and the three PI questions: 10-10 §6(B)–(C).

### 4.5 Closed — do not reopen

- **10-10 §6(A), in full.** All three guards, `f61f6fd`. E3 was verified on the
  loader-minted ids in an independent clone, not inferred from a green suite.
- **The non-finite statistics question, for the two files that exist.** S1 and
  S3 came back clean. **11-07b §4 is its dated home and carries the figures,
  the three cross-checks that the probe read S1 as the adapter does, and the
  reachability bound — read them there; they are not restated here.**
  `notes/scripts/probe_nonfinite_statistics.py` is the instrument, committed. **S2_GG and S4 are not in the content store and are
  named nowhere in the repository** — if either is added, re-run the probe.

## 5. Where everything else lives

- **State and figures:** `notes/REVIEWER-HANDOFF-2026-11-07b.md`.
- **The third deposit's result:** `notes/REVIEWER-HANDOFF-2026-11-07.md` §3,
  and `walk/RESULT-PXD032267-gate-attempt2.md`.
- **Invariants:** `ONTOLOGY.md` v1.48, 21 invariants. **Decisions:**
  `decisions/`, ADR-0038 fully built, ADR-0032 `Proposed`.
- **The loop's conventions:** 11-07b §6, and the 10-10 conversation handoff §4
  for the ones that predate it.
- **Prompts:** `notes/prompts/`, through 36. Prompt 33 is at rev 11 and built.
