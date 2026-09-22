# PROMPT 20 — H10 attempt 2: the `joint_half` convention, its checks, and D′

Working copy: this container's clone of `bzkzhao/bzk-omics`. Report its path.

**Base.** Fetch, then fast-forward to `origin/main`. It must be a fast-forward
of `20e3185` whose only changes are:
- `walk/PREREG-PXD018299-H10-attempt2.md`, added, with sha256
  `16759b7f2992b629b889f2f6ae5e4191e340f66cf9252deb956a1eb613ff3166`;
- anything under `notes/prompts/`.

Verify with `git diff --stat 20e3185..origin/main` and the hash. Otherwise report
and stop.

Build the environment with `uv sync`. Run every Python command under
`.venv/bin/python`. **Never force-push, and never amend or rebase a pushed
commit. Do not write, retype or commit any file under `notes/prompts/`.** This
container has no raw store. **You build and test; bzk runs it.**

**Read these in full before writing anything:**
- `walk/PREREG-PXD018299-H10-attempt2.md`, which is the specification;
- `walk/PREREG-PXD018299-H10.md`, which still governs everything attempt 2
  does not replace;
- `walk/RESULT-PXD018299-H10-attempt1.md` and
  `notes/scripts/diagnose_gate_g.py`, for why attempt 2 exists.

**The expectations Y1–Y4 are not inputs,** and nothing in the code may read or
depend on them. Where the specification is silent, choose, record the choice in
the module and the report, and never choose by outcome.


## Part A — the `joint_half` sidedness in `perseus_s0`

Add the sidedness `joint_half` exactly as the specification's §1 defines it: the
`joint` null count at each threshold, multiplied by ½, and nothing else. Leave
`joint` and `per_side` untouched, and keep q monotone.

The docstring must say three things:
- the convention was **fitted on Table 3**, from one number at one seed;
- it is **unverified** against Perseus's code, since the source returned 404;
- attempt 1's result is why it exists.

**Tests:**
- **(i)** On a hand-computable case, `joint_half`'s FDR is exactly half of
  `joint`'s at every threshold. Mutation: halve the observed count instead.
- **(ii)** Under `joint_half` at 3 against 3 with the mirror kept, the floor is
  1/38. Mutation: drop the halving, which gives 1/19.
- **(iii)** `joint` and `per_side` give identical outputs to before, on a fixed
  input.


## Part B — attempt 2 in `bzk/sources/pxd018299_h10.py`

Attempt 2 is a mode of the existing module, and **attempt 1's behaviour must be
reproducible unchanged**. Add a registered `attempt` parameter (1 or 2) to
`main`, and a command-line flag `--attempt 2`. The default stays 1.

**Under attempt 2:**
- **The variants** are `joint_half` × the four schemes, in the specification's
  §2 order, and nothing else.
- **G2a:** attempt 1's gate G, with the same metric and thresholds, run over the
  four `joint_half` variants.
- **G2b, the direction split,** computed over **all rows** with the
  majority-of-seeds call.
  - Count the proteins called higher in WT and those called higher in
    *ISG15*−/−, and check them against the bands [58, 86] and [168, 252].
  - Take WT and *ISG15*−/− from the curation record's genotype labels, and
    **assert** that `direction > 0` means higher in WT. Under the argument order
    turn 19 used, WT is the numerator. State that in a comment beside the
    assertion.
- **Check A:** unchanged.
- **Admission and the primary variant:** as the specification's §3 says.
- **If a variant is admitted:** attempt 1's §§2–6 anchor path unchanged, plus
  readout **D′** from the specification's §4:
  - match targets against S1's gene-name column exactly, except MAGE, which
    matches by prefix;
  - report both grains;
  - report *absent from S1* where a symbol matches nothing.
- **Output:** `tests/fixtures/pxd018299_h10_attempt2.json`. **Never overwrite
  attempt 1's fixture.** Every result block carries
  `validation: "in-sample; independent confirmation pending"`.

**The staged-file loophole.** Replace `is_tracked`'s
`git ls-files --error-unmatch` with `git cat-file -e HEAD:<path>`. The rule is
*committed before the run*, and the old check also passes for a staged file.
Add a test for a staged but uncommitted file, which must count as **not**
committed. Mutation: revert to `ls-files`.


## Tests — added to `tests/test_pxd018299_h10.py`

Each test must be seen to fail before it passes. The report gives each mutation
and its failure message.

- **Attempt 1 is unchanged.** On the existing synthetic end-to-end run,
  attempt 1's fixture is byte-identical to before, apart from the
  `generated_under` timestamp.
- **Attempt 2 admits only variants passing G2a, G2b and A.** Build a synthetic
  case where G2a passes and G2b fails. Mutation: skip G2b.
- **G2b's bands are inclusive.** Counts of exactly 58, 86, 168 and 252 pass;
  57 and 253 fail.
- **The direction orientation.** A synthetic protein higher in WT is counted
  in the WT band. Mutation: flip the sign.
- **D′:**
  - the tiers are reported separately;
  - MAGE matches by prefix, and nothing else does;
  - an absent symbol is reported as absent, not as unrecovered.
- **Attempt 2 never writes attempt 1's fixture path.**


## Registered expectations for this turn

E1. The suite is 833 passed and 14 skipped at base, plus the new tests.
E2. No existing test changes, beyond classifications in the tautology sweep
    (named). The floor is untouched.


## Task

1. Verify the base, and read the documents.
2. Write Parts A and B and their tests.
3. Run E1–E2 and every `CLAUDE.md` point-1 check with its target:
   - `pytest` (full suite) and `pytest tests/test_schema.py`;
   - `ruff check bzk tests`;
   - `ruff format --check bzk tests`;
   - `mypy bzk tests`.
4. Commit Part A (`stats:`), then Part B (`sources:`). Push, fast-forward only.
5. Write `notes/reports/20-h10-attempt2-build-report.md`, with the report's run
   date taken from the commit date, and commit it alone. Push.


## Out of scope

- Any real-data run.
- Changing either pre-registration.
- Any variant beyond `joint_half`.
- The third deposit.
- The tautology floor.
- `notes/prompts/`.


## Report

- The base check.
- Every choice made where the specification was silent, with its reason.
- Each test, with its mutation and failure message.
- E1–E2, each held or missed.
- Every `CLAUDE.md` point-1 check at its actual result, with its target.
- What this turn does NOT cover.
- Commit SHAs and the push range, stating every push was a fast-forward.
