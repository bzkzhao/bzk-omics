"""A committed sweep for assertions compared against the expression that produced them.

**Why this exists as a test rather than a procedure.** The 2026-08-08 sweep was run by hand, and its
own report said the detector *"will not re-run"*. That is the defect one level out: a class found by
a procedure nobody repeats is a class rediscovered by the next audit. The passes below are the same
syntactic nets, committed, so a new assertion of the shape fails until someone has looked at it.

**What a syntactic net can and cannot do.** It cannot decide whether a call *is* the expression that
produced the other side — that needs the producer's body, and reading it is judgement. So the net
pins its **match set**, not a verdict: **every equality, in every assert, in every `.py` file under
`tests/`** must appear in `PINNED`, and a new one fails this module with instructions to classify
it. The four already classified as instances are listed separately in `INSTANCES`, and each carries
an `Evidence` the suite **re-runs** rather than a sentence it stores.

**That declaration is exact as of 2026-08-08 and was not before.** It read *"every matching
assertion in `tests/`"*, unqualified, while the net examined the first comparison of each assert and
no other, counted one assert twice, and could not reach an async function, a module-level assert or
a non-`test_*.py` module. `assert a == 0 and <a confirmed instance>` passed. Both the loop and the
counter were one decision about what "the surface" means and are converged together; the count the
floor is denominated in moved from 633 to 632 as a result.

**The demonstration that repair originally rested on was worthless, and is replaced — 2026-08-08.**
It planted `assert receipt.drifts == 0 and <a confirmed instance>`, whose second conjunct unparses
to a string already in `PINNED` for that module, so under a set key it added nothing and passed the
broken net and the repaired one alike. Confirmed against both. A **novel** expression in the same
second-conjunct position discriminates: `receipt.checked_at == drift.latest_stamp(home)` is green
under the restored `break` and red without it, naming the new match. That is what establishes the
loop repair, and the earlier plant established nothing.

**The record is a multiset, and neither a set nor a count would do.** A count is satisfied by
deleting one substantive assertion and adding one tautological assertion in the same module; a set
is satisfied by duplicating any pinned assertion, which was planted and confirmed. The module used
to state the first of those as though it settled the question, while the second went unmentioned —
two arguments each covering the other's hole. A multiset is one key rather than a pair, so its own
limit is stated below instead of inferred from the pair's.

**This module excludes itself from its own surface**, because its assertions compare a computed
match set against a pinned constant — the shape the net matches — and a module that swept itself
would have to pin its own pin. Stated rather than silently filtered.
"""

from __future__ import annotations

import ast
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass

TESTS = pathlib.Path(__file__).resolve().parent
SELF = pathlib.Path(__file__).name


def _has_call(node: ast.AST) -> bool:
    return any(isinstance(x, ast.Call) for x in ast.walk(node))


def _is_literalish(node: ast.AST) -> bool:
    """A literal, or a display built only from literals. Not a name — a name can hold anything."""
    if isinstance(node, ast.Constant):
        return True
    if isinstance(node, ast.UnaryOp):
        return _is_literalish(node.operand)
    if isinstance(node, ast.List | ast.Tuple | ast.Set):
        return all(_is_literalish(e) for e in node.elts)
    if isinstance(node, ast.Dict):
        return all(
            k is not None and _is_literalish(k) and _is_literalish(v)
            for k, v in zip(node.keys, node.values, strict=True)
        )
    return False


def _equalities(test: ast.expr) -> list[ast.Compare]:
    return [
        c
        for c in ast.walk(test)
        if isinstance(c, ast.Compare) and any(isinstance(o, ast.Eq) for o in c.ops)
    ]


def _enclosing_function(tree: ast.AST) -> dict[int, ast.AST]:
    """`id(assert node) -> the innermost function enclosing it`, or the module for a bare one.

    Built by descending rather than by `ast.walk` over every function, because walking every
    `FunctionDef` visits a nested one twice — once on its own and once inside its parent — and an
    assert in the nested body is then counted and examined twice. Measured before this was written:
    633 walked against 632 distinct, the duplicate being `test_rebuild.py:250`, in `_resolve` nested
    inside `_resolver_for`. One assert is one member of the surface, whatever it is nested in.
    """
    owner: dict[int, ast.AST] = {}

    def descend(node: ast.AST, scope: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef):
                descend(child, child)
            else:
                if isinstance(child, ast.Assert):
                    owner[id(child)] = scope
                descend(child, scope)

    descend(tree, tree)
    return owner


def sweep(directory: pathlib.Path | None = None) -> tuple[Counter[tuple[str, str]], int, int]:
    """Return `{(module, normalized source)}` plus the module and assert counts of the surface.

    **Pass C** — one side of an `==` contains a call and another side is not a literal display.
    Catches `receipt.archive_digest == drift.archive_digest(archived_sequences(home))`.

    **Pass D** — no call anywhere in the comparison, but one side is a bare name bound earlier in
    the same scope from an expression that did contain one. Catches the same shape laundered
    through a local variable, which Pass C cannot see. Pass D found no instances on 2026-08-08 and
    is committed anyway: a pass that has never fired is the one whose absence goes unnoticed.

    **The surface is every equality in every assert, each assert counted once — widened
    2026-08-08.** Three ways the examined surface was narrower than the declared one, all fixed
    here as one decision about what "the surface" means, because converging on part of it is the
    half-closure this module exists to catch:

      * **only the first `Compare` in each assert was examined.** A `break` sat outside the `if`,
        so `assert a == 0 and <a second matching comparison>` passed. Established by a plant that
        **discriminates** — a novel expression, green under the `break` and red without it. The
        plant first used here did not: its second conjunct was already in `PINNED`, so a set key
        could not have registered it either way.
      * **one assert was counted and examined twice**, per `_enclosing_function` above.
      * **three edges were unreachable by construction** — an `AsyncFunctionDef`, an assert outside
        any function, and a `.py` file in `tests/` that is not `test_*.py`. All three measure zero
        today, so covering them changes no count; they are covered because the declaration says
        *every assertion in `tests/`* and a surface that silently excludes a shape is this class
        whether or not the shape is currently present.
    """
    found: Counter[tuple[str, str]] = Counter()
    modules = 0
    asserts = 0
    directory = TESTS if directory is None else directory
    for path in sorted(directory.glob("*.py")):
        if path.name == SELF:
            continue
        modules += 1
        matched, counted = analyse(path.name, path.read_text(encoding="utf-8"))
        found.update(matched)
        asserts += counted
    return found, modules, asserts


def analyse(name: str, source: str) -> tuple[Counter[tuple[str, str]], int]:
    """The net over one module's source. Split out so it can be planted with synthetic input.

    That split is the point rather than tidiness: the three mutations offered as confirmation on
    2026-08-08 all acted at whole-assert or whole-module granularity, and the two defects repaired
    here live *below* an assert and *inside* the counter, where none of them could reach. A net
    whose reach is only ever exercised against the tree it reports on cannot show that its reach is
    what it claims — so `test_the_net_reaches_every_granularity_it_declares` runs this over source
    that contains each shape deliberately.
    """
    found: Counter[tuple[str, str]] = Counter()
    asserts = 0
    tree = ast.parse(source)
    owner = _enclosing_function(tree)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assert):
            continue
        asserts += 1
        scope = owner.get(id(node), tree)
        bound_from_call = {
            n.id
            for st in ast.walk(scope)
            if isinstance(st, ast.Assign) and _has_call(st.value)
            for tgt in st.targets
            for n in ast.walk(tgt)
            if isinstance(n, ast.Name)
        }
        for cmp_ in _equalities(node.test):
            sides = [cmp_.left, *cmp_.comparators]
            non_literal = [s for s in sides if not _is_literalish(s)]
            if any(_has_call(s) for s in sides):
                # Pass C: a call on one side, something non-literal on another.
                hit = any(
                    _has_call(s) and any(not _is_literalish(o) for o in sides if o is not s)
                    for s in sides
                )
            else:
                # Pass D: no call in the comparison at all.
                hit = any(isinstance(s, ast.Name) and s.id in bound_from_call for s in sides) and (
                    bool(non_literal)
                )
            if hit:
                found[name, ast.unparse(cmp_)] += 1
    return found, asserts


#: Every match, as `(module, normalized source, occurrences)` — a **multiset**, because a set
#: cannot see a pinned expression duplicated and a count cannot see one swapped for another.
#: Normalized source rather than a line number, so unrelated edits above it do not churn the pin.
#: Regenerate with `python -c "from tests.test_tautology_sweep import sweep;
#: print(sorted(sweep()[0]))"` **after** classifying whatever is new.
PINNED: frozenset[tuple[str, str, int]] = frozenset(
    {
        # ── tests/test_agent_config_references.py, classified individually 2026-08-18 ──────────
        # **One match, `PINNED` rather than `INSTANCES`, and the two sides have independent
        # origins.** `len(docs)` is read off the filesystem by `_agent_docs()`; the right side is
        # `EXPECTED_AGENT_DOCS`, a literal `47` written by hand at l.52 of that module. Neither
        # produced the other, which is the question the failure message poses — so it is not the
        # call-equals-its-own-expression class `INSTANCES` records, and there is no mutation to
        # keep green.
        #
        # **Measured rather than read, and to the stricter standard: the failure names *this*
        # assertion, not an earlier line in the same test.** Mutation: one `.md` file added under
        # `.claude/config/` carrying no code path, so `test_code_paths_resolve` cannot redden with
        # it and the demonstration is isolated to one assert. Result `F..` — the other two tests
        # pass — failing at `tests/test_agent_config_references.py:116` with
        # *".claude/ holds 48 Markdown files, not 47"* and `assert 48 == 47`. That test carries a
        # single assert, so reddening at an earlier line was not available to it anyway; the
        # mutation establishes the count reaches the message rather than merely that the test
        # fails.
        #
        # **Occurrences measured off `sweep()` rather than taken from the failure text**, since
        # this record is a multiset and a wrong count is a hole in the guard: one.
        #
        # **It could have been made to vanish in one character and was not.** Pass C excludes a
        # comparison against a literal display, so `len(docs) == 47` never matches while
        # `len(docs) == EXPECTED_AGENT_DOCS` does. Writing the literal would have bought a green
        # suite by removing the expression from review rather than by reviewing it — the turn that
        # wrote the guard stopped instead and recorded the block in `HANDOFF.md` §8.
        ("test_agent_config_references.py", "len(docs) == EXPECTED_AGENT_DOCS", 1),
        (
            "test_curation_content_hash.py",
            "_record(name)['content_hash'] == PXD018299_SITES.expected_content_hash",
            1,
        ),
        (
            "test_curation_content_hash.py",
            "_records_citing_the_deposit() == set(CITING_RECORDS)",
            1,
        ),
        ("test_curation_content_hash.py", "accession == PXD018299_SITES.accession", 1),
        # ── tests/test_command_blocks.py, classified individually 2026-08-11 ──────────────────
        # **One match, and it is not an instance — but it is the vacuity shape rather than the
        # tautology shape, so the classification took a measurement rather than a reading.** The
        # left side is parsed from the eleven documents; the right side is `[]`. Nothing re-derives
        # the left at assert time, so it is not the call-equals-its-own-expression class. What it
        # *is* exposed to is emptiness: if the block classifier stops recognising command blocks,
        # `gaps` is `[]` and this line is green over nothing — the omission failure
        # `tests/test_query_absence_coverage.py` was built against, one module along.
        #
        # **Measured rather than argued.** Mutation E on 2026-08-10's successor turn made
        # `_is_command_block` return `False` unconditionally: this assertion **passed**, and
        # `test_the_check_fires_on_the_defect_it_was_written_for` and
        # `test_the_known_command_blocks_are_all_covered` both failed. So the non-vacuity is
        # carried by those two, not by this line, and the three are a set of which none is
        # redundant. Pinned rather than rewritten, because `== []` is the honest statement of the
        # property; moving it to `not gaps` would hide the same exposure behind a truthiness test.
        ("test_command_blocks.py", "gaps == []", 1),
        # ── tests/test_deposit_survey.py, classified individually 2026-08-12 ──────────────────
        # **Nine matches, none an instance, and the classification turns on a distinction worth
        # stating.** Eight compare a computed `site_state` against `SITE_PRESENT` /
        # `SITE_CANDIDATE` / `SITE_ABSENT` — module constants, not literals, which is why Pass C
        # does not exclude them. That is *close* to the class: `site_state` returns those very
        # names, so if a constant's value drifted, both sides would drift together and the
        # assertion would hold. What it would not survive is a change to which **branch** runs,
        # which is the property each one is written for — and mutations C (candidate reported as
        # absent) and D (candidate promoted to present) fail exactly these, measured.
        #
        # The residual exposure — the vocabulary itself — is closed by
        # `test_the_three_state_values_are_what_they_say`, which pins the three strings against
        # literals in one place. So the pair is: eight assertions pinning branches, one pinning
        # values, and neither is redundant. **That vocabulary pin is not in this set**: its right
        # side is a tuple of string literals, which Pass C excludes by construction — so it
        # raises the surface by one assert and the match count by zero. Pinning it here was tried
        # and failed as a `gone` entry, which is this module refusing a pin for something it does
        # not match.
        #
        # The ninth is `skipped == ('raw_search_output.zip: beyond the limit of 0',)`: the left
        # side is `expand_archives`' return, the right a literal tuple written by hand. It is the
        # assertion that a name habit no longer skips an archive, and mutation H fails it.
        (
            "test_deposit_survey.py",
            "Candidate('x', '', '', files=tuple((f['fileName'] for f in plausible))).site_state == SITE_PRESENT",
            1,
        ),
        ("test_deposit_survey.py", "_c('20190520_phospho_run1.raw').site_state == SITE_ABSENT", 1),
        (
            "test_deposit_survey.py",
            "_c('HAP1_USP18KO_GlyGlyKSites.txt').site_state == SITE_PRESENT",
            1,
        ),
        ("test_deposit_survey.py", "_c('S1_1_site-enriched.mzML').site_state == SITE_ABSENT", 1),
        (
            "test_deposit_survey.py",
            "_c('Search.zip!Output/GlyGly (K)Sites.txt').site_state == SITE_PRESENT",
            1,
        ),
        (
            "test_deposit_survey.py",
            "_c('Search/GlyGly (K)Sites.txt.gz').site_state == SITE_PRESENT",
            1,
        ),
        ("test_deposit_survey.py", "_c('UbPTMs_PTMs_Summary.txt').site_state == SITE_CANDIDATE", 1),
        (
            "test_deposit_survey.py",
            "_c('proteinGroups.txt', 'run.raw').site_state == SITE_ABSENT",
            1,
        ),
        (
            "test_deposit_survey.py",
            "skipped == ('raw_search_output.zip: beyond the limit of 0',)",
            1,
        ),
        # ── tests/test_deposit_survey.py, the extractor's eleven, classified 2026-08-12 ────────
        # **Eleven expressions over thirteen occurrences, all `PINNED`, none an instance.** An
        # instance claim requires the assertion to stay **green** under a mutation of the code it
        # tests. Every one of these goes red, and the failure message names *that assertion* rather
        # than merely its test — which is a stricter check than the test reddening, because a test
        # can redden at an earlier line.
        #
        # Three mutations carry them, each aimed at what the assertion actually compares:
        #   (X) `extract_member` returns `raw[:-1] + b"X"` — length preserved, last byte changed,
        #       applied after every guard so nothing refuses. Reddens the six content comparisons
        #       and **not** `len(got) == len(content)`, which is how those two are separated.
        #   (Y) `extract_member` returns `raw[:-1]` — length changed. Reddens the length check.
        #   (Z) field mutations of `archive_members`: the zip64 write-back removed, the CRC read
        #       from bytes 12-16, the uncompressed size read from 20-24.
        #
        # 1. `_zip64_values(extra, 2) == [999, real]` (1) — the parser's read of a hand-built extra
        #    field against the two values packed into it; `999` and `real` are literals bound above
        #    and the call is on one side only. Made to fail by shortening the comprehension's range.
        # 2. `extract_member(...) == content` (2) — extracted bytes against the payload written into
        #    the archive. Twice, and the two are not redundant: one is a stored (method 0) member,
        #    the other the zip64-sentinel member, so one expression covers two paths. (X).
        # 3. `extract_member(...) == expected` (2) — `expected` is **`zipfile`'s own read** of the
        #    same archive, so this compares two implementations rather than two views of one. Twice:
        #    the zip64 local-extra member and the non-UTF-8 name member. (X).
        # 4. `extract_member(...bytes(blob)) == expected` (1) — the same shape against the patched
        #    copy, where the data-descriptor flag is set. Distinct expression because the session is
        #    built from `bytes(blob)`, not `blob`. (X).
        # 5. `got == b'body of GlyGly (K)Sites.txt'` (1) — the multi-member test: the right member's
        #    body against a literal. **Matched by Pass D, not Pass C** — the other side *is* a
        #    literal display, and Pass D does not exclude that. Kept as a match rather than argued
        #    away; the asymmetry with Pass C is recorded in `ROADMAP.md` § *Classifying the
        #    extractor's eleven sweep matches* and deliberately not fixed here. (X).
        # 6. `got == content` (1) — the large-member test's content check, after its length check.
        #    (X), which is chosen precisely because it leaves the length assertion green.
        # 7. `got == zf.read('combined/txt/GlyGly (K)Sites.txt')` (1) — the reference comparison the
        #    extractor turn declined to rewrite: both sides are calls, one ours and one `zipfile`'s,
        #    and replacing it with a literal would discard the second implementation. (X).
        # 8. `len(got) == len(content)` (1) — the same test's length check, and **not** a weaker copy
        #    of 6: (Y) reddens this and (X) does not, which is the measurement that separates them.
        # 9. `member.compressed_size == real` (1) — the parser's zip64-resolved size against
        #    `zipfile`'s `compress_size` for the same entry. Made to fail by removing the write-back.
        # 10. `member.crc32 == info.CRC == zlib.crc32(content) & 4294967295` (1) — **one expression,
        #    not two.** A chained comparison is a single `ast.Compare`, so `sides` is all three terms
        #    and `ast.unparse` records the whole chain. Conjunct one compares our parse against
        #    `zipfile`'s stored CRC; conjunct two recomputes it from the payload with `zlib`. Neither
        #    is independently trivial, but **only the first exercises `archive_members`** — the second
        #    checks the reference implementation, which is why it is kept rather than dropped. (Z).
        # 11. `member.uncompressed_size == info.file_size == len(content)` (1) — the same chain
        #    shape, and the same asymmetry: conjunct one is our parse against `zipfile`'s, conjunct
        #    two is `zipfile`'s record against the input length and tests the reference, not us. (Z).
        (
            "test_deposit_survey.py",
            "_zip64_values(extra, 2) == [999, real]",
            1,
        ),
        (
            "test_deposit_survey.py",
            "extract_member('http://x/a.zip', member, session=_RangedSession(blob)) == content",
            2,
        ),
        (
            "test_deposit_survey.py",
            "extract_member('http://x/a.zip', member, session=_RangedSession(blob)) == expected",
            2,
        ),
        (
            "test_deposit_survey.py",
            (
                "extract_member('http://x/a.zip', member, "
                "session=_RangedSession(bytes(blob))) == expected"
            ),
            1,
        ),
        ("test_deposit_survey.py", "got == b'body of GlyGly (K)Sites.txt'", 1),
        ("test_deposit_survey.py", "got == content", 1),
        (
            "test_deposit_survey.py",
            "got == zf.read('combined/txt/GlyGly (K)Sites.txt')",
            1,
        ),
        ("test_deposit_survey.py", "len(got) == len(content)", 1),
        ("test_deposit_survey.py", "member.compressed_size == real", 1),
        (
            "test_deposit_survey.py",
            "member.crc32 == info.CRC == zlib.crc32(content) & 4294967295",
            1,
        ),
        (
            "test_deposit_survey.py",
            "member.uncompressed_size == info.file_size == len(content)",
            1,
        ),
        # ── tests/test_curation_pxd026748_arms.py, classified 2026-09-19 ──────────────────────
        # **`PINNED`, not `INSTANCES`, and the two sides are two different files.** `shotgun` and
        # `gg` are each `sorted(tuple(...))` over the `Sample` nodes of one committed curation
        # record; neither call produced the other, and the records are written independently by
        # the review loop. The claim is that `curation_PXD026748.json` and
        # `curation_PXD026748_shotgun.json` describe the same twelve materials field-for-field —
        # which is a fact about two documents, the shape the block below calls safe.
        #
        # The assertion above it compares the same two as *sets* and names the symmetric
        # difference; this one adds multiplicity, and fails when one arm repeats a tuple the other
        # carries once. Made to fail by changing one shotgun sample's `treatment` in a copy under
        # `tmp_path`.
        ("test_curation_pxd026748_arms.py", "shotgun == gg", 1),
        # ── tests/test_decision_index.py, classified individually 2026-08-10 ──────────────────
        # Thirteen matches, none an instance, each made to fail by a mutation of the surface it
        # names. Every one is either a computed value against a **pinned literal** or two sets
        # parsed from **different documents** — the shape the tautology risk here would be is two
        # sets from one parse, and only `forward`/`backward` come from one call. That pair reads
        # two *different header fields*, and both directions were made to fail separately.
        #
        # Pinned counts. Each fails when its own surface is emptied or grown: a planted file (A),
        # a planted row (B), 0018 moved out of Queued (C), the Written table emptied (D), the seed
        # list emptied (E), a seed un-struck (F).
        ("test_decision_index.py", "len(_files()) == EXPECTED_FILES", 1),
        ("test_decision_index.py", "len(_written()) == EXPECTED_WRITTEN_ROWS", 1),
        ("test_decision_index.py", "len(_queued()) == EXPECTED_QUEUED_ROWS", 1),
        ("test_decision_index.py", "len(seeds) == EXPECTED_SEED_LINES", 1),
        # The one that caught a defect in its own guard before any mutation: the first draft read
        # `sum(1 for _, struck in seeds)` — no condition — and counted 18 against a pinned 17.
        (
            "test_decision_index.py",
            "sum((1 for _, struck in seeds if struck)) == EXPECTED_SEED_STRUCK",
            1,
        ),
        # Two independently parsed surfaces on each side: the filesystem against README's Written
        # table, in both directions. Fails on a planted file (A) and a planted row (B) respectively.
        ("test_decision_index.py", "written - files == set()", 1),
        ("test_decision_index.py", "files - written == set()", 1),
        # A computed list against a literal; `missing` is built from `Path.exists()`, so the
        # filesystem is the other side rather than the parse. Fails on a one-character link break.
        ("test_decision_index.py", "missing == []", 1),
        # `ARCHITECTURE.md` against `decisions/README.md` — two documents, two parsers. Fails on
        # 0018 moved to Written, on the seed list emptied, and on a seed un-struck.
        ("test_decision_index.py", "unstruck == set(_queued())", 1),
        # Three surfaces in one line: seeded numbers, the directory, and Queued.
        ("test_decision_index.py", "unwritten == set(_queued())", 1),
        # The two README tables against each other. Fails on 0018 appearing in both.
        (
            "test_decision_index.py",
            "{number for number, _ in _written()} & set(_queued()) == set()",
            1,
        ),
        # Status counts against a pinned literal, so a 25th record fails until it is classified.
        ("test_decision_index.py", "counted == EXPECTED_STATUSES", 1),
        # The only pair drawn from one parse, and it reads two different header fields. Made to
        # fail on its own: `0019 Supersedes ADR-0016` with 0016 silent gives
        # `{('0019', '0016')} == set()`. The reciprocal direction is pinned as an exception below
        # it and fails on a second one-sided pair.
        ("test_decision_index.py", "forward - backward == set()", 1),
        (
            "test_curation_loader.py",
            "len(set(loaded.sample_ids.values())) == len(loaded.sample_ids)",
            1,
        ),
        ("test_curation_loader.py", "load(changed).dataset_id == loaded.dataset_id", 1),
        (
            "test_curation_loader.py",
            "set(_record(MINTED_IDS)['samples']) == set(_record(REAL_RECORD)['mapping'])",
            1,
        ),
        (
            "test_curation_loader.py",
            "set(load(changed).sample_ids.values()) == set(loaded.sample_ids.values())",
            1,
        ),
        ("test_curation_loader.py", "sources == set(loaded.sample_ids.values())", 1),
        (
            "test_curation_loader.py",
            "{n['label'] for n in _nodes(loaded, 'Sample')} == set(loaded.sample_ids)",
            1,
        ),
        (
            "test_curation_loader.py",
            "{s['id'] for s in mapping.samples} == set(loaded.sample_ids.values())",
            1,
        ),
        ("test_drift.py", "drift.STALE_AFTER_DAYS == int(stated.group(1))", 1),
        ("test_drift.py", "drift.read_receipt(home) == receipt", 1),
        (
            "test_drift.py",
            "receipt.archive_digest == drift.archive_digest(drift.archived_sequences(home))",
            1,
        ),
        ("test_drift.py", "receipt.sequences_checked == len(drift.archived_sequences(home))", 1),
        (
            "test_keys.py",
            "canonical_parameters_json('{\"n\": 1e16}') == canonical_parameters_json('{\"n\": 10000000000000000}')",
            1,
        ),
        (
            "test_keys.py",
            "canonical_parameters_json('{\"n\": 1e22}') == canonical_parameters_json('{\"n\": 10000000000000000000000}')",
            1,
        ),
        (
            "test_keys.py",
            "canonical_value(8, 'DOUBLE') == canonical_value(8.0, 'DOUBLE') == '8.0'",
            1,
        ),
        # Classified individually 2026-08-09, with the local-part guard.
        #
        # Not an instance: the right side is the loop's *input*, not this call's output, so nothing
        # here compares a computation with itself. Its content is narrow and worth stating —
        # `check_curie_case` either returns its argument or raises, so `f(x) == x` can only fail
        # against an implementation that **repairs**. That is exactly the contract §4 fixes
        # (refuse, never normalize), and the assertion is the only thing pinning it at this call
        # site. Pinned rather than strengthened: a wider claim would need a second return path
        # that does not exist.
        ("test_keys.py", "check_curie_case(curie) == curie", 1),
        # Not an instance either, and a genuine partition: the enforced prefixes come from
        # `keys._LOCAL_PART_PREFIX` and the open ones are written out, so a prefix added to
        # `schema.CURIE_PREFIXES` without being classified fails here rather than being silently
        # unenforced. Neither side is derived from the other.
        (
            "test_keys.py",
            (
                "set(keys._LOCAL_PART_PREFIX) | {'uniprot'} | {'unimod', 'pmid', 'ensembl', "
                "'reactome', 'doi', 'mod'} == set(schema.CURIE_PREFIXES)"
            ),
            1,
        ),
        (
            "test_keys.py",
            "evidence_id('Analysis', SITE_ANALYSIS, child_values=a) == evidence_id('Analysis', SITE_ANALYSIS, child_values=b)",
            1,
        ),
        (
            "test_keys.py",
            "evidence_id('Analysis', SITE_ANALYSIS, child_values={'Imputation': [one, two]}) == evidence_id('Analysis', SITE_ANALYSIS, child_values={'Imputation': [two, one]})",
            1,
        ),
        ("test_keys.py", "evidence_id('Analysis', a) == evidence_id('Analysis', b)", 4),
        (
            "test_keys.py",
            "evidence_id('Analysis', dict(SITE_ANALYSIS, localization_threshold=0.75)) == evidence_id('Analysis', dict(SITE_ANALYSIS, localization_threshold=0.75))",
            1,
        ),
        (
            "test_keys.py",
            "evidence_id('Analysis', protein) == evidence_id('Analysis', dict(protein))",
            1,
        ),
        # ADR-0025's structural claim, classified 2026-08-10 and the turn's only new match. Not an
        # instance: the right side is a literal display and the left is computed from
        # `schema.IDENTITY`, which is not the expression that produced it. Made to fail by adding a
        # second self-anchor (`("ProteinAssignment", "SUPERSEDES")`) — one failure, this test alone.
        # Pass D catches it rather than Pass C, because the call is in the binding
        # (`schema.IDENTITY.items()`) and not in the comparison.
        (
            "test_keys.py",
            "self_anchored == {'DifferentialResult': ['DifferentialResult']}",
            1,
        ),
        ("test_keys.py", "protein == 'uniprot:P20591'", 1),
        ("test_keys.py", "sequence == 'uniprot:P20591#sv4'", 1),
        ("test_keys.py", "site == 'uniprot:P20591#sv4#K48#unimod:121'", 1),
        # I20's DDL-derivation check, classified 2026-08-10. **The closest call in `PINNED` and it
        # is not an instance, for a reason that had to be measured.** Both sides read
        # `schema.REL_TABLES`, so the right side looks like the expression that produced the left —
        # but they are two *different* filters over one source, and the property asserted is that
        # the source is the same. Made to fail: replacing the module's predicate with
        # `r.name == "RESULT_FOR_SITE"` gives `{'RESULT_FOR_SITE'} == {'RESULT_FOR_PROTEIN',
        # 'RESULT_FOR_SITE'}` **on this line**. What it cannot catch is a change made to both sides
        # at once, which is why the next line in that test pins `declared` against a literal pair —
        # the two assertions are a pair and neither is redundant.
        ("test_invariants.py", "set(_RESULT_EDGES) == declared", 1),
        ("test_maxquant.py", "accessions == ['P20591', 'P19525']", 1),
        # The coverage guard's two, classified 2026-08-10. Neither is an instance and each was made
        # to fail by a mutation of the thing it names rather than of something upstream.
        #
        # Left: a query's return over a DDL-only graph. Right: a value in `EXPECTED`, measured once
        # and then a literal — not a producer, and not re-derived at assert time. Removing
        # `gene_symbols`' empty-`Gene` check fails here and nowhere else.
        ("test_query_absence_coverage.py", "observed == expectation.expected", 1),
        # Left: the registry's keys. Right: computed from `bzk.query.__all__`. This is the whole
        # anti-omission mechanism, so it is the one assertion in that module that must not be
        # satisfiable by the registry alone. Adding an unclassified export fails it by name —
        # `Extra items in the right set: 'newly_added_query'`.
        ("test_query_absence_coverage.py", "set(EXPECTED) == _exported_queries()", 1),
        # The protein adapter's three, classified individually 2026-08-10. None is an instance, and
        # each was made to fail by a mutation of the adapter recorded in `ROADMAP.md`
        # § *Outcome: the MaxQuant protein adapter*.
        #
        # Two artefacts of one `parse`, not one artefact against its own producer: the left is the
        # set of `RESOLVES_TO_PROTEIN` **edges**, the right the observation **node**'s stored field.
        # They are built from one local list, which is why they agree.
        #
        # **The mutation that establishes it is `protein_ids[:0]`, and `[:1]` establishes nothing
        # here.** Narrowing the loop to one candidate does fail the test — but at
        # `invariants.validate` inside `parse`, raising I14 before the assertion is reached, so it
        # measures the invariant and not this line. Emptying the loop is the case I14 deliberately
        # permits (no edges is a node re-staged as a referent, ADR-0019), so `parse` returns and the
        # assertion fails on its own line: `assert set() == {…P20591, …P09914, …P05161}`. That gap
        # is exactly what this assertion covers and the invariant does not.
        (
            "test_maxquant_protein_groups.py",
            "reached == set(observation['candidate_proteins'])",
            1,
        ),
        # Against a literal display of three accessions the fixture names; the `set()` on the left
        # is deduplication, not the producer. Made to fail with
        # `candidate_nodes([*group, "Q9NRZ9"])` — an extra `Protein` no edge names is a valid
        # change-set, so it survives `parse` and reaches the assertion.
        (
            "test_maxquant_protein_groups.py",
            "set(protein_ids) == {f'uniprot:{MX1}', f'uniprot:{IFIT1}', f'uniprot:{ISG15}'}",
            1,
        ),
        # A third assertion in the same test, `sorted(protein_ids) == sorted(set(protein_ids))`, was
        # **withdrawn rather than pinned**: it cannot fail, because `parse` validates before
        # returning and structural validation refuses a duplicate `(label, id)`, so no `parsed`
        # carrying one ever reaches an assert. Removing the adapter's `staged_proteins` filter fails
        # the test inside `parse`, which establishes that guard and not the line.
        ("test_maxquant_sites.py", "set(modifiers) == set(schema.GG_REMNANT_MODIFIERS)", 1),
        # Classified individually 2026-08-09, with the identity pin. None is an instance; each is
        # recorded with what it would take to make it fail, and two were made to fail by the
        # mutations run on `_pin_put` and on `_Entry`'s default.
        #
        # A precondition, not a result: it establishes that `refresh=True` really did overwrite the
        # snapshot, without which the *next* assertion in that test — that `resolve` still returns
        # the archived sequence — would pass against a snapshot nothing had touched. The right side
        # is a test literal and the left is what came back off disk through `_fetch_entry` and
        # `json.dumps`, so the round trip is the content.
        (
            "test_pins.py",
            "json.loads((cache / 'entry' / 'P20591.json').read_text())['sequence'] == amended",
            1,
        ),
        # Two reads of one file with `_pin_put` and a `resolve` between them, so the comparison is
        # before-and-after and not a value against itself. Demonstrated rather than argued:
        # deleting the write-once check in `_pin_put` fails this and nothing else.
        ("test_pins.py", "pin.read_text() == before", 2),
        # The sentinel reaching disk, not just the return value: the right side is a module
        # constant and the left is a read of the file `_fetch_entry` wrote. Restoring the
        # pre-2026-08-09 first-match fails this and nothing else in the suite, which is how the
        # gap it covers was found.
        (
            "test_pins.py",
            (
                "json.loads((tmp_path / 'entry' / 'P20591.json').read_text())['hgnc_id'] "
                "== uniprot.AMBIGUOUS"
            ),
            1,
        ),
        # A change-detector on a declaration, which is the nearest of the three to a tautology and
        # is kept deliberately. It compares a field's default with the constant that default is
        # written as, so it can only fail if the declaration moves — which is exactly the failure
        # worth catching: defaulting `hgnc_id` to `None` silently stops `_load_entry`'s sentinel
        # check from ever firing, and every pre-widening snapshot then reads as *no HGNC id*.
        # Confirmed by mutation. The line beside it carries the content the pin rests on.
        ("test_pins.py", "uniprot._Entry(status='ok').hgnc_id == uniprot.NOT_CAPTURED", 1),
        # Classified individually 2026-08-09, with the read path. None is an instance — every right
        # side is either a literal or a value read from `schema`, and none is produced by the call
        # on the left — and none is unfailable, which is the other reason a row is withdrawn here
        # rather than pinned.
        #
        # The empty differential table, twice in the fixture module and once against the real
        # graph. It sits beside an `absence is ...` assertion and is not redundant with it: rows
        # non-empty under `NOT_STORED`, or empty under the wrong absence, are different bugs and
        # each assertion catches one.
        ("test_query.py", "rows == []", 2),
        ("test_query_real_graph.py", "rows == []", 1),
        # The `gene_absence` partition, computed from the graph against a literal. The real-graph
        # row carries the figures §4 records, so a divergence is a finding about the graph.
        (
            "test_query.py",
            "census == {'encoded': 1, 'unresolved': 1, 'no_cross_reference': 0, 'not_captured': 0}",
            1,
        ),
        # The same shape over the empty-`Gene` fixture, and pinned for the same reason: the literal
        # is written from what the fixture puts in the graph — one `Protein`, `unresolved` — and not
        # from what the census returns, so the two sides have independent origins. Its job there is
        # non-vacuity: it is what stops that fixture degenerating into an empty database, which
        # would make the `NOT_STORED` it exists to check true for the wrong reason.
        (
            "test_query.py",
            "census == {'encoded': 0, 'unresolved': 1, 'no_cross_reference': 0, 'not_captured': 0}",
            1,
        ),
        (
            "test_query_real_graph.py",
            (
                "census == {'encoded': 1054, 'unresolved': 3492, 'no_cross_reference': 15, "
                "'not_captured': 0}"
            ),
            1,
        ),
        # Code against code: the census must key **every** state including the zeroes, because an
        # omitted key and a zero read differently and only one of them is a measurement.
        ("test_query.py", "set(census) == set(schema.GENE_ABSENCE) | {'encoded'}", 1),
        # Which two of the fourteen are absent, not merely how many. `DDX58` is the one that
        # matters: absent under its own name while the gene is present as `RIGI`.
        ("test_query_real_graph.py", "absent == ['DDX58', 'OAS1']", 1),
        # Classified individually 2026-08-09, with the interface. Neither is an instance: the right
        # side of each is the `Absence` enum or a literal, and neither is produced by the left.
        # Both are the two halves of one contract that has to be asserted as two — a mapping can be
        # complete and still say the same thing twice, which is the blank-grid failure with extra
        # steps. Confirmed by mutation: making two absences share a headline fails the second and
        # not the first.
        ("test_ui.py", "set(ui_absence.RENDERING) == set(Absence)", 1),
        ("test_ui.py", "len(set(headlines)) == len(Absence) == 4", 1),
        ("test_perseus.py", "dataset['content_hash'] == content_hash(TABLE.read_bytes())", 1),
        (
            "test_perseus.py",
            "ids == {'uniprot:P20591', 'uniprot:P19525', 'uniprot:O43593', 'uniprot:P05161'}",
            1,
        ),
        ("test_perseus.py", "mx1['adj_p_value'] == pytest.approx(0.0012)", 1),
        ("test_perseus.py", "mx1['log2fc'] == pytest.approx(3.42)", 1),
        ("test_perseus.py", "p_values[0] == pytest.approx(10 ** (-5.02))", 1),
        ("test_perseus.py", "result['adj_p_value'] == pytest.approx(0.0012)", 1),
        ("test_perseus.py", "result['p_value'] == pytest.approx(3.0902e-05)", 1),
        ("test_perseus.py", "store.ids_by_label(conn) == before", 1),
        # ── tests/test_pxd026748_published_cascade.py, classified 2026-09-20 ──────────────────
        # **`PINNED`, not `INSTANCES`, and the two sides are two separate runs over two different
        # deposits.** `found` is `build(...)` over a deposit whose `Sequence window` cells carry
        # the published windows; `missed` is `build(...)` over one that does not. Neither call
        # produced the other — they share only their published rows — and the claim is that the
        # window diagnostic is **inert**: finding a lead must change no placement and no count.
        #
        # Asserted as whole objects on purpose. A handful of named numbers would leave whichever
        # count the test forgot to name as the place a recovery could hide, which is the defect
        # these two lines exist to rule out. Made to fail by letting a window match recover the
        # row, which moves `join` and `reaches_test` together.
        (
            "test_pxd026748_published_cascade.py",
            "[_placed(r) for r in found] == [_placed(r) for r in missed]",
            1,
        ),
        (
            "test_pxd026748_published_cascade.py",
            "cascade_source.summary(found) == cascade_source.summary(missed)",
            1,
        ),
        ("test_protein_groups.py", "[asdict(m) for m in measured] == _pinned()", 1),
        (
            "test_protein_groups.py",
            "m['multi_fraction'] == pytest.approx(m['multi_accession'] / m['rows'], abs=5e-05)",
            1,
        ),
        # ── the four added with the baseline's per-target candidate sites ─────────────────────
        # **None is an instance, and the reason is the same for all four: the fixture now carries
        # two records of one run — each entry's selected row, and the `sites` it was selected
        # from — and every one of these compares one against the other.** A call appears on one
        # side because counting or maximising is how the comparison is written, not because the
        # call re-derives the side it is compared to.
        #
        # **What each is exposed to, since "not an instance" is not "not vacuous":**
        #
        # `row['n_sites'] == len(row['sites'])` — the weakest of the four and pinned as such.
        # `derive()` sets both from the same `hits` frame, so it cannot fail while the generator
        # is correct; what it catches is a hand-edit to one record and not the other, or a write
        # that truncated `sites`. It is not load-bearing for the selection rule and is not
        # claimed to be.
        #
        # `row['log2fc'] == max(values)` — the strongest. The left side was chosen by
        # `hits.loc[hits['log2fc'].idxmax()]` when the fixture was written; the right re-runs
        # that rule at assert time over the *other* record. A candidate set that quietly dropped
        # the losers would still satisfy the membership check beside it and reddens here the
        # moment it drops a winner. Neither side is computed from the other.
        #
        # `len(row.sites) == len(want['sites'])` and
        # `value == pytest.approx(pinned, rel=FLOAT_RTOL)` — both inside the re-derivation test,
        # which the module's own docstring already classifies: the fixture was written by the
        # function being compared to it, so this half is a determinism and dependency-drift check
        # and not a regression check. The second is the same shape as the `getattr(...)` entry
        # directly above, one level down into `sites`.
        #
        # **Occurrences read off `sweep()` rather than counted by eye: one each.** The two inside
        # the re-derivation test were **not** exercised in the turn that wrote them — the deposit
        # is not in `raw/`, so that test skips — and no mutation confirms them here.
        (
            "test_pxd018299_baseline.py",
            "row['n_sites'] == len(row['sites'])",
            1,
        ),
        ("test_pxd018299_baseline.py", "row['log2fc'] == max(values)", 1),
        ("test_pxd018299_baseline.py", "len(row.sites) == len(want['sites'])", 1),
        (
            "test_pxd018299_baseline.py",
            "value == pytest.approx(pinned, rel=FLOAT_RTOL)",
            1,
        ),
        (
            "test_pxd018299_baseline.py",
            "getattr(row, field) == pytest.approx(want[field], rel=FLOAT_RTOL)",
            1,
        ),
        ("test_pxd018299_baseline.py", "len(_rows()) == _record()['n_expected_total']", 1),
        ("test_pxd018299_baseline.py", "recovered == _record()['n_expected_recovered']", 1),
        (
            "test_pxd018299_baseline.py",
            "tuple((row['gene'] for row in _rows() if not row['recovered'])) == NOT_RECOVERED",
            1,
        ),
        (
            "test_pxd018299_baseline.py",
            "tuple((row['gene'] for row in _rows())) == EXPECTED_TARGETS",
            1,
        ),
        (
            "test_pxd018299_baseline.py",
            "{row.gene for row in rederived.targets} == set(expected)",
            1,
        ),
        (
            "test_pxd018299_platform_targets.py",
            "{row['gene'] for row in _rows()} == set(EXPECTED_TARGETS)",
            1,
        ),
        # ── tests/test_pxd018299_refusals.py, classified individually 2026-09-14 ──────────────
        # **Two matches, neither an instance, and the distinction is which key of the file each
        # side reads.** `pxd018299_refusals.py` writes one JSON object holding `counts` and
        # `refusals`; `_counts()` reads the first off disk and the other side recomputes the same
        # summary from the second. Both sides come out of the same file, which is exactly why they
        # are worth comparing — `refusal_fixture` builds them from one list, so a file whose halves
        # disagree was not produced by a single run of it. Neither call re-derives the other side
        # at assert time, which is the call-equals-its-own-expression class `INSTANCES` records.
        #
        # **No mutation confirms either one here, and that is a property of the container rather
        # than of the assertions.** The fixture is generated from the deposit, `raw/` does not
        # survive a container (`HANDOFF.md` §3), and this run was explicitly forbidden from
        # hand-writing the file — so both assertions error on a missing fixture rather than
        # passing, and there is no green state to mutate away from. The same is already true of
        # the two `test_pxd018299_baseline.py` entries inside its re-derivation test, recorded
        # directly above in the same terms.
        #
        # **The residual exposure is emptiness, and it is accepted rather than closed.** A fixture
        # carrying `counts: {}` and `refusals: []` satisfies both. No guard forces a non-empty
        # record, deliberately: a deposit that refused nothing is a legitimate outcome
        # (`HANDOFF.md` §3 — report it even if it is zero), and a floor written today would be a
        # floor written from `ROADMAP.md`'s 27 rather than from a measurement, which is the one
        # thing the fixture exists to stop. The vocabulary and deposit-row checks in that module
        # are vacuous on an empty file for the same reason and say so.
        #
        # **Occurrences read off `sweep()`: one each.**
        ("test_pxd018299_refusals.py", "_counts() == recounted", 1),
        ("test_pxd018299_refusals.py", "len(_refusals()) == sum(_counts().values())", 1),
        # ── tests/test_pxd055843_depletion_ranking.py, classified individually 2026-09-15 ──────
        # **Ten expressions over eleven occurrences, all `PINNED`, none an instance.** The module
        # under test reports an ordering and pins no answer, so every assertion in it is a relation
        # between two things with separate origins: a value the module computed and either a
        # constant the test wrote into its own synthetic workbook or a different function of the
        # same output. Nothing here compares a call to the expression that produced it.
        #
        # **Nine were made to fail, each by a mutation chosen so the failure names *that* line and
        # not an earlier one in the same test.** Every mutation was confirmed applied by reading
        # the file back, and reverted with the suite green again afterwards.
        #
        # `differences == sorted(differences)` — `sorted` is a different function of the list, not
        # the expression that built it, and it fails exactly when the module stops ordering. Made
        # to fail by `found.sort(..., reverse=True)`: `l.258`, `[2.75, 1.25, ...] == [-3.1, ...]`.
        # **Count 2, and only one of the two was confirmed.** The other occurrence is inside the
        # artefact test, which skips in this container — the bytes are in no content store here and
        # are not to be put into the tree — so there is no green state to mutate away from, exactly
        # as recorded for the two `test_pxd018299_refusals.py` entries above.
        #
        # `[row.rank ...] == list(range(1, len(...) + 1))` — the ranks are a field the module
        # assigns; the range is built from the row count. Made to fail by `enumerate(found,
        # start=0)`, which leaves the sortedness assertion above it green: `l.259`,
        # `[0, 1, 2, 3, 4] == [1, 2, 3, 4, 5]`.
        #
        # `ranked.data_rows == len(DATA)` — a count the module accumulates against the length of
        # the list this test file writes into the workbook. Made to fail by deleting the
        # increment: `l.269`, `0 == 7`.
        #
        # `len(rows) + without_difference == data_rows` — the partition. Both sides are the
        # module's own bookkeeping, which is the point: it fails for a row that fell out of both
        # branches. Made to fail by deleting `without_difference += 1`, which leaves the count
        # above it green: `l.270`, `(5 + 0) == 7`.
        #
        # `without_difference == sum(...)` — the module's exclusion count against the test's own
        # recount over its own data. Made to fail by returning a NaN instead of `None`, which
        # keeps the partition above it green because the row merely moves from one side to the
        # other: `l.271`, `1 == 2`.
        #
        # `set(ranked.columns) == {the four marks}` — the module's discovery report against the
        # four constants imported from it. Made to fail by dropping `GENE_MARK` from `columns`:
        # `l.148`.
        #
        # The two `rank(_book(..., label_rows=N)).contrast == SUFFIX` — `SUFFIX` is written by this
        # test file *into* the workbook, so the right side is an input the test chose. They are two
        # entries rather than one because they are two files, and the mutation for each leaves the
        # other green. `label_rows=1`: `contrast_of` returning the whole column name — `l.227`,
        # `"Student's T-...FN_siCTRL_IFN" == 'siUSP24_IFN_siCTRL_IFN'`. `label_rows=0`:
        # `header_row` returning `max(index, 1)`, which reads a data row as the header — `l.228`
        # goes red on the `RankingError` raised inside the call on that line while `l.227` stays
        # green. **Recorded as it is and not dressed up: that line reddens by raising rather than
        # by comparing**, which is weaker than the others here and is the strongest available,
        # since a header row read off the wrong index cannot reach a comparison at all.
        #
        # `sheet.max_column == width` — the only one inside a helper rather than a test. It is the
        # builder checking `openpyxl`'s view of what it wrote against the width it meant to write,
        # and it guards every file below. Made to fail by appending one extra cell per data row:
        # `l.129` on all sixteen tests.
        #
        # **Occurrences read off `sweep()` rather than from the failure text: one each, except
        # `differences == sorted(differences)` at two.**
        (
            "test_pxd055843_depletion_ranking.py",
            "[row.rank for row in artefact.rows] == list(range(1, len(artefact.rows) + 1))",
            1,
        ),
        (
            "test_pxd055843_depletion_ranking.py",
            "[row.rank for row in ranked.rows] == list(range(1, len(ranked.rows) + 1))",
            1,
        ),
        ("test_pxd055843_depletion_ranking.py", "differences == sorted(differences)", 2),
        (
            "test_pxd055843_depletion_ranking.py",
            "len(artefact.rows) + artefact.without_difference == artefact.data_rows",
            1,
        ),
        (
            "test_pxd055843_depletion_ranking.py",
            "len(ranked.rows) + ranked.without_difference == ranked.data_rows",
            1,
        ),
        (
            "test_pxd055843_depletion_ranking.py",
            "rank(_book(tmp_path / 'no-label.xlsx', label_rows=0)).contrast == SUFFIX",
            1,
        ),
        (
            "test_pxd055843_depletion_ranking.py",
            "rank(_book(tmp_path / 'one-label.xlsx', label_rows=1)).contrast == SUFFIX",
            1,
        ),
        ("test_pxd055843_depletion_ranking.py", "ranked.data_rows == len(DATA)", 1),
        (
            "test_pxd055843_depletion_ranking.py",
            "ranked.without_difference == sum((1 for row in DATA if row[1] in (None, 'NaN')))",
            1,
        ),
        (
            "test_pxd055843_depletion_ranking.py",
            "set(ranked.columns) == {GENE_MARK, DIFFERENCE_MARK, Q_VALUE_MARK, MINUS_LOG_P_MARK}",
            1,
        ),
        ("test_pxd055843_depletion_ranking.py", "sheet.max_column == width", 1),
        ("test_raw_store.py", "again.path.read_bytes() == PAYLOAD", 1),
        ("test_raw_store.py", "content_hash(PAYLOAD) == f'sha256:{sha256_hex(PAYLOAD)}'", 1),
        (
            "test_raw_store.py",
            "fetch(pinned, home=tmp_path, session=_StubSession()).content_hash == content_hash(PAYLOAD)",
            1,
        ),
        (
            "test_raw_store.py",
            "store(PAYLOAD, 'sites.txt', home=tmp_path).content_hash == content_hash(PAYLOAD)",
            1,
        ),
        ("test_raw_store.py", "stored.content_hash == content_hash(PAYLOAD)", 1),
        ("test_raw_store.py", "stored.path.read_bytes() == PAYLOAD", 1),
        ("test_raw_store.py", "to_https(ftp) == https", 1),
        (
            "test_quant.py",
            (
                "back == [quant.Cell('bzk:obs1', 'bzk:s1', "
                "'intensity_multiplicity_summed', 150520.0), "
                "quant.Cell('bzk:obs1', 'bzk:s2', 'intensity_multiplicity_summed', 0.0), "
                "quant.Cell('bzk:obs1', 'bzk:s1', 'ratio_mod_base', None)]"
            ),
            1,
        ),
        ("test_quant.py", "never_ingested == []", 1),
        ("test_quant.py", "quant.count_cells(connection) == first == {'site_values': 4}", 1),
        ("test_quant.py", "quant.digest_rows(first) == quant.digest_rows(second)", 1),
        ("test_raw_store.py", "to_https(https) == https", 1),
        (
            "test_raw_store.py",
            "verify(stored.content_hash, filename='sites.txt', home=tmp_path) == stored.path",
            1,
        ),
        ("test_rebuild.py", "first == second", 1),
        ("test_rebuild.py", "store.count_edges(conn) == EXPECTED_EDGES", 1),
        ("test_rebuild.py", "store.count_nodes(conn) == EXPECTED_NODES", 2),
        ("test_rebuild.py", "store.ids_by_label(conn) == before", 1),
        (
            "test_rebuild.py",
            "store.ids_by_label(open_graph(home)) == {'Project': [pinned['project']], 'Experiment': [pinned['experiment']], 'Dataset': [pinned['dataset']], 'Analysis': [pinned['analysis']], 'Sample': sorted(pinned['samples'].values())}",
            1,
        ),
        # Classified individually 2026-08-09, with `Gene`. None is an instance; two of the six the
        # sweep first raised were withdrawn rather than pinned, because they asserted a partition on
        # a *returned* `ResolvedProteins` and `__post_init__` raises during construction — so they
        # could not fail. They are replaced by a test that exercises the guard, confirmed by
        # deleting each half of it.
        #
        # The replacement of the row this one supersedes: the emitted `Protein`'s key set, now four
        # columns rather than three. A literal on the right, the builder's output on the left.
        # ── tests/test_rebuild_report_mirror.py, classified 2026-09-19 ────────────────────────
        # **`PINNED`, not `INSTANCES`, and matched by Pass D rather than Pass C.** The right side
        # is a literal display, which Pass C excludes; what matches is Pass D — `extra` is a name
        # bound from a call, and Pass D does not exclude a literal on the other side.
        #
        # Neither side produced the other. The left is read off `RebuildReport`'s and
        # `ReplayReport`'s declarations at run time; the right is `{'tables_created'}`, typed by
        # hand, and it is the whole claim — that `RebuildReport` adds exactly one field to the
        # replay's, so a second one added there alone is noticed. Re-deriving it would assert
        # nothing, which is why it is a literal and why moving it is a deliberate edit.
        ("test_rebuild_report_mirror.py", "extra == {'tables_created'}", 1),
        (
            "test_resolve_nodes.py",
            "set(protein) == {NODE_TYPE_KEY, 'id', 'accession', 'gene_absence'}",
            1,
        ),
        # The fixture set is asserted to exercise **every** member of the enum. It fails if a value
        # is added to `GENE_ABSENCE` with no case behind it, or if the builder emits one the enum
        # does not name — which is the fall-through §4's column exists to make impossible.
        (
            "test_resolve_nodes.py",
            "set(resolved.gene_absence.values()) == set(schema.GENE_ABSENCE)",
            1,
        ),
        ("test_schema.py", "accession == accession.upper()", 1),
        ("test_schema.py", "built == schema.table_names()", 1),
        ("test_schema.py", "code_children == doc_children", 1),
        ("test_schema.py", "included == {'P0CG48', 'Q15843', 'P05161'}", 1),
        ("test_schema.py", "len(listed) == len(set(listed))", 1),
        ("test_schema.py", "named == {e for _, e in pairs}", 1),
        ("test_schema.py", "prefix == prefix.lower()", 1),
        ("test_schema.py", "schema.CURATION_BASIS == dict(rows)", 1),
        # A document mirror, the same shape as `CURATION_BASIS == dict(rows)` two rows down: the
        # left is the code's enum and the right is parsed out of §4. `NULL` is excluded because it
        # is the column's absence rather than a value it holds, and its presence in the document is
        # asserted separately so removing that row fails rather than shrinking the comparison.
        ("test_schema.py", "set(schema.GENE_ABSENCE) == set(named) - {'NULL'}", 1),
        ("test_schema.py", "schema.CURIE_PREFIXES == _curie_prefixes()", 1),
        ("test_schema.py", "schema_nodes == ontology_nodes", 1),
        ("test_schema.py", "schema_rels == ontology_rels", 1),
        ("test_schema.py", "set(authority) & set(composed) == set()", 1),
        ("test_schema.py", "set(authority) | set(composed) == _reference_node_tables()", 1),
        ("test_schema.py", "set(listed) == set(nodes)", 1),
        ("test_schema.py", "set(schema.IDENTITY) == {label for label, *_ in rows}", 1),
        ("test_schema.py", "set(spec.anchors) == doc_anchors", 1),
        ("test_schema.py", "set(spec.fields) == doc_fields", 1),
        ("test_stats.py", "benjamini_hochberg(np.array([0.031]))[0] == pytest.approx(0.031)", 1),
        (
            "test_stats.py",
            "drawn.mean() == pytest.approx(observed.mean() - 1.8 * observed.std(ddof=1), rel=0.02)",
            1,
        ),
        (
            "test_stats.py",
            "drawn.std(ddof=1) == pytest.approx(0.3 * observed.std(ddof=1), rel=0.05)",
            1,
        ),
        ("test_stats.py", "got.log2fc[0] == pytest.approx(0.0)", 1),
        ("test_stats.py", "got.p_value[0] == pytest.approx(1.0)", 1),
        ("test_stats.py", "welch_t(a, b).log2fc[0] == pytest.approx(2.0)", 1),
        ("test_store.py", "store.ids_by_label(conn) == {'Protein': sorted([MX1, USP18])}", 1),
        # ── tests/test_target_recovery_rules.py, classified individually 2026-09-14 ────────────
        # **Six expressions over six occurrences, all `PINNED`, none an instance — and the module
        # arrived with three more that were removed rather than pinned.** This is the second time
        # the net has caught new code in the turn that wrote it, and it did so three times in that
        # turn: `len(counts) == len(PATH_VALUES) * len(RULE_VALUES)` compared `totals()`' key count
        # against the two tuples `totals()` itself iterates to build those keys; `totals([empty])
        # == {(p, r): 0 for p in PATH_VALUES for r in RULE_VALUES}` restated the same construction
        # on its right-hand side; and `source_for(path).fixture == module.FIXTURE_PATH` compared
        # `source_for()`'s output against the very attribute its body reads. None could fail. The
        # first is now checked from the printed report, the second reads
        # `not any(totals([empty]).values())`, and the third was replaced by the provenance loop
        # whose two matches are pinned below — a moved constant rather than a restated one.
        #
        # `seen == expected`: `seen` is the gene order `bzk/target_recovery_rules.py`'s `compare()`
        # produced; `expected` is read straight out of the committed fixture by `load()`. Two
        # surfaces — a computation and a file on disk — so neither produced the other. Made to fail
        # by having `compare()` iterate `reversed(load(path)["targets"])`, and this is the first
        # assertion in its test, so the failure names it.
        #
        # `len(seen) == len(set(seen))`: the closest call in this group, because both sides derive
        # from `seen`. It is not the class `INSTANCES` records all the same — `set(seen)` is not
        # the expression that produced `seen`, it is a *different* function of it, and the
        # assertion fails exactly when that function loses an element.
        #
        # **Measured to the stricter standard: the failure names *this* assertion and not the line
        # above it.** The obvious mutation — `compare()` visiting each path's targets twice — does
        # not qualify: it reddens `seen == expected` first, and was confirmed doing exactly that,
        # which would have left this entry resting on an earlier line's failure. The mutation that
        # discriminates duplicates a target inside a *copy* of `pxd018299_welch_baseline.json`, so
        # `expected` carries the duplicate too, `seen == expected` stays green, and this line fires
        # on `15 == 14`. The committed fixture is not touched.
        #
        # `read(source_for(path)) == moved`: `moved` is a value **the test invents** — the module
        # constant plus one, or a renamed path — and is then written onto the owning module before
        # the call. So the right-hand side is an input the test chose, not an expression the call
        # produced, which is what distinguishes this from the third removal above. Made to fail by
        # binding the thresholds at import in `bzk/target_recovery_rules.py`, which leaves
        # `source_for()` returning the pre-move value.
        #
        # `set(MODULES) == set(PATH_VALUES)`: two module-level constants declared separately in
        # `bzk/target_recovery_rules.py`. Neither is built from the other — `MODULES` is a literal
        # keyed by the two path constants — so the pair can disagree, and does the moment a third
        # path is added to one and not the other. Made to fail by adding a key to `PATH_VALUES`.
        #
        # `source_for(other) == untouched`: the negative half of the provenance check. `untouched`
        # is read *before* any move, so this compares the same call across a state change rather
        # than against its own expression. Made to fail by pointing both `MODULES` entries at the
        # baseline module, so the untouched path follows the moved one.
        #
        # **This entry stood at a count of 2 and the second occurrence was worthless.** The same
        # assertion was repeated after the restore loop, where nothing between it and the in-loop
        # copy touches `other`'s module — so no mutation could redden one without the other, and
        # the attempt to find one is what surfaced it. It now reads `source_for(path) == before`,
        # which checks what that position can actually check: that the restore happened. Made to
        # fail by replacing the `finally` body with `pass`, which leaves the last attribute moved.
        ("test_target_recovery_rules.py", "seen == expected", 1),
        ("test_target_recovery_rules.py", "len(seen) == len(set(seen))", 1),
        ("test_target_recovery_rules.py", "read(source_for(path)) == moved", 1),
        ("test_target_recovery_rules.py", "set(MODULES) == set(PATH_VALUES)", 1),
        ("test_target_recovery_rules.py", "source_for(other) == untouched", 1),
        ("test_target_recovery_rules.py", "source_for(path) == before", 1),
        # ── tests/test_published_cascade.py, classified individually 2026-09-17 ─────────────────
        # **One match, `PINNED`, and it is the closest call in the module.** The fixture's
        # `summary` block was written by `bzk/sources/pxd018299_published_cascade.py` using the
        # same `bzk/published_cascade.py` functions the test's `derived` calls — so at generation
        # time the two sides were one computation. It is not the class `INSTANCES` records all the
        # same, because what the test compares is **two stored surfaces** of the committed fixture:
        # the `summary` a reader quotes and the `rows` the module re-reads. Either can be edited
        # without the other, and the module's stage definitions can move without the fixture being
        # regenerated; the call re-derives from the rows *now*, not from the run.
        #
        # **Measured to the stricter standard.** Mutation: a temporary copy of the fixture with
        # `summary.recovered` set to 513 and the rows untouched. This test is the **only** one in
        # the module that fails; every figure test stays green, because each reads the rows. The
        # converse mutation (one recovered row moved to `presence`, summary untouched) fails this
        # test and four figure tests together, so it establishes nothing about this line on its
        # own and is not the evidence. The committed fixture was not touched.
        #
        # Five further matches arrived with the module and were removed rather than pinned: four
        # compared against the name `PUBLISHED_ROWS`, which the net cannot tell from a computed
        # value, and one against `list(range(...))`. Each now compares against a literal.
        ("test_published_cascade.py", "fixture['summary'] == derived", 1),
        # ── tests/test_anova.py, classified individually 2026-09-20 ────────────────────────────
        # **Nineteen matches, all `PINNED`, and the classification turns on one question the
        # module poses: does the call produce the other side?** Here it never does, in three
        # shapes.
        #
        # Thirteen are `result.<term> == pytest.approx(<number>)` against R's printed `aov` table
        # for `ToothGrowth`. The net matches them only because `pytest.approx` is a call; what it
        # wraps is a literal someone else published, so the right side has an origin `two_way` had
        # no part in. Made to fail by dropping the `b` factor from `ss_a`
        # (`n * b * ((mean_a` -> `n * ((mean_a`): `factor_a.sum_squares[0]` reads 68.45 against
        # 205.35.
        #
        # Four are the symmetry check, `reversed_.<term> == pytest.approx(forward.<term>)`. Both
        # sides come from `two_way`, which is the shape `INSTANCES` exists for — but from **two
        # calls with the factors exchanged**, so neither produced the other, and a defect that
        # treats the two factor positions differently separates them. Made to fail by computing
        # `mean_b` from A's first level alone (`cell_means.mean(axis=1)` -> `cell_means[:, 0, :]`),
        # which reddens this assertion at 2426.43 against 3504.33.
        #
        # One is `result.min_p() == pytest.approx(np.minimum(np.minimum(...)))`, whose sides are
        # both functions of the same `result`. It is still not the class `INSTANCES` records, and
        # the distinguishing test is `Evidence`'s own: an instance is one whose **own scope stays
        # green** under the mutation. `np.nanmin` -> `np.nanmax` in `min_p` reddens this very
        # assertion (0.937 against 0.122), so its scope does see the defect and there is no
        # green-scope evidence to record.
        #
        # One is the fixture pin, `hashlib.sha256(FIXTURE.read_bytes()).hexdigest() ==
        # TOOTHGROWTH_SHA256`: the file's bytes now against a digest written by hand when it was
        # fetched. Made to fail by appending one newline to `tests/fixtures/toothgrowth.csv`; the
        # committed fixture was restored from a copy taken before the mutation.
        (
            "test_anova.py",
            "hashlib.sha256(FIXTURE.read_bytes()).hexdigest() == TOOTHGROWTH_SHA256",
            1,
        ),
        ("test_anova.py", "result.factor_a.sum_squares[0] == pytest.approx(205.35, abs=0.005)", 1),
        (
            "test_anova.py",
            "result.factor_b.sum_squares[0] == pytest.approx(2426.43434, abs=0.005)",
            1,
        ),
        (
            "test_anova.py",
            "result.interaction.sum_squares[0] == pytest.approx(108.319, abs=0.005)",
            1,
        ),
        ("test_anova.py", "result.residual_sum_squares[0] == pytest.approx(712.106, abs=0.005)", 1),
        ("test_anova.py", "result.factor_a.f[0] == pytest.approx(15.572, abs=0.0005)", 1),
        ("test_anova.py", "result.factor_b.f[0] == pytest.approx(92.0, abs=0.0005)", 1),
        ("test_anova.py", "result.interaction.f[0] == pytest.approx(4.107, abs=0.0005)", 1),
        ("test_anova.py", "result.factor_a.p_value[0] == pytest.approx(0.000231, abs=5e-07)", 1),
        ("test_anova.py", "result.interaction.p_value[0] == pytest.approx(0.0219, abs=5e-05)", 1),
        (
            "test_anova.py",
            "reversed_.factor_a.sum_squares[0] == pytest.approx(forward.factor_b.sum_squares[0])",
            1,
        ),
        (
            "test_anova.py",
            "reversed_.factor_b.sum_squares[0] == pytest.approx(forward.factor_a.sum_squares[0])",
            1,
        ),
        (
            "test_anova.py",
            "reversed_.interaction.sum_squares[0] == pytest.approx(forward.interaction.sum_squares[0])",
            1,
        ),
        (
            "test_anova.py",
            "reversed_.residual_sum_squares[0] == pytest.approx(forward.residual_sum_squares[0])",
            1,
        ),
        (
            "test_anova.py",
            "result.factor_a.f == pytest.approx(_lstsq_f(values, full, np.column_stack([intercept, db, dab])), rel=1e-09)",
            1,
        ),
        (
            "test_anova.py",
            "result.factor_b.f == pytest.approx(_lstsq_f(values, full, np.column_stack([intercept, da, dab])), rel=1e-09)",
            1,
        ),
        (
            "test_anova.py",
            "result.interaction.f == pytest.approx(_lstsq_f(values, full, np.column_stack([intercept, da, db])), rel=1e-09)",
            1,
        ),
        (
            "test_anova.py",
            "result.factor_a.sum_squares + result.factor_b.sum_squares + result.interaction.sum_squares + result.residual_sum_squares == pytest.approx(total, rel=1e-09)",
            1,
        ),
        (
            "test_anova.py",
            "result.min_p() == pytest.approx(np.minimum(np.minimum(result.factor_a.p_value, result.factor_b.p_value), result.interaction.p_value))",
            1,
        ),
        # ── tests/test_t_variants.py, classified individually 2026-09-20 ──────────────────────
        # **Five entries over eight occurrences, all `PINNED`.** The right side of every one is
        # arithmetic done by hand in the test's own docstring: `DIFFERENCE` is the literal -4.0,
        # and `_p(...)` reads `scipy.stats.t.sf` at a statistic and a df written out from the two
        # groups' means and variances. `bzk/stats/tests.py` had no part in producing either, which
        # is the question the failure message poses. Made to fail by weighting Welch's two
        # variances by the other group's n (`var1 / n1 + var2 / n2` -> `var1 / n2 + var2 / n1`):
        # the Welch P reads 0.0551 against 0.0458.
        #
        # **`result.log2fc[0] == pytest.approx(DIFFERENCE)` stands at a count of 4, and the
        # multiset cannot tell the four apart** — they are one expression in four test functions,
        # differing only in which variant bound `result`, which is the scope-blindness this
        # module's own docstring declares. It is recorded rather than worked around, because
        # nothing rests on it: the difference of means is the one quantity all four variants share
        # by construction, so a variant wired to the wrong helper is caught by the P assertion two
        # lines below it in the same test, never by this one. Made to fail as above, which reddens
        # the P line; `log2fc` is reddened instead by returning `mean2 - mean1`.
        ("test_t_variants.py", "result.log2fc[0] == pytest.approx(DIFFERENCE)", 4),
        (
            "test_t_variants.py",
            "result.p_value[0] == pytest.approx(_p(DIFFERENCE / WELCH_SE, WELCH_DF), rel=1e-12)",
            1,
        ),
        (
            "test_t_variants.py",
            "result.p_value[0] == pytest.approx(_p(DIFFERENCE / STUDENT_SE, STUDENT_DF), rel=1e-12)",
            1,
        ),
        (
            "test_t_variants.py",
            "result.p_value[0] == pytest.approx(_p(DIFFERENCE / (WELCH_SE + S0), WELCH_DF), rel=1e-12)",
            1,
        ),
        (
            "test_t_variants.py",
            "result.p_value[0] == pytest.approx(_p(DIFFERENCE / (STUDENT_SE + S0), STUDENT_DF), rel=1e-12)",
            1,
        ),
        # ── tests/test_pxd026748_reconstruction.py, classified individually 2026-09-20 ────────
        # **Ten matches, all `PINNED`, and none of them compares the module against itself.**
        # Six compare a figure the module produced against `len(CLAIM_IDS)` or `[360] *
        # len(CLAIM_IDS)`, where `CLAIM_IDS` is the list of deposit ids the *test* wrote into its
        # synthetic cascade fixture and 360 is the grid size `:110-124` registers — an input the
        # test chose and a published constant, neither produced by the code under test. Made to
        # fail by cutting the seed range from twenty to ten (`SEEDS = tuple(range(20))` ->
        # `range(10)`), which reads 180 against 360.
        #
        # Two are `code == 0` and `code == 1`, `main`'s exit status against a literal: matched
        # because Pass D sees a bare name bound from a call, not because either side derives from
        # the other. Made to fail by running the GG arm whatever the gate says (`if not
        # gate["verdict"]["passed"]:` -> `if gate["verdict"]["passed"] is None:`), which reads
        # 0 against 1.
        #
        # Two are `normalised[0, 0] == pytest.approx(8.0 - 12.0)` and its counterpart at `8.0 -
        # 11.0`: the two medians of one synthetic column, with and without the row the valid-value
        # filter drops, written out by hand in the test. **They are the pair that makes the
        # pipeline's order checkable**, and they are asserted against arithmetic rather than
        # against each other. Made to fail by normalising after filtering instead of before, which
        # reads -3.0 against -4.0.
        (
            "test_pxd026748_reconstruction.py",
            "[len(c['min_p']) for c in family['claims']] == [360] * len(CLAIM_IDS)",
            1,
        ),
        (
            "test_pxd026748_reconstruction.py",
            "a['family']['population_rows'] == len(CLAIM_IDS) + 1",
            1,
        ),
        ("test_pxd026748_reconstruction.py", "after[0, 0] == pytest.approx(8.0 - 11.0)", 1),
        ("test_pxd026748_reconstruction.py", "normalised[0, 0] == pytest.approx(8.0 - 12.0)", 1),
        ("test_pxd026748_reconstruction.py", "code == 0", 1),
        ("test_pxd026748_reconstruction.py", "code == 1", 1),
        ("test_pxd026748_reconstruction.py", "family['exposure'] == len(CLAIM_IDS)", 1),
        ("test_pxd026748_reconstruction.py", "family['verdict']['exposure'] == len(CLAIM_IDS)", 1),
        ("test_pxd026748_reconstruction.py", "len(family['claims']) == len(CLAIM_IDS)", 1),
        ("test_pxd026748_reconstruction.py", "sum(counts.values()) == len(CLAIM_IDS)", 1),
        # ── tests/test_pxd026748_h5c_h9p.py, classified individually 2026-09-21 ───────────────
        # **One match, `PINNED`.** `counts` is bound from `missing_counts(...)` and the right side
        # is the literal `[0, None]` the test wrote, so Pass D matched a name bound from a call and
        # not a call compared against its own expression. The whole module contributes one entry
        # because every other assertion compares against a literal display or a dict literal.
        #
        # **Measured to the stricter standard: the failure names *this* assertion and not the line
        # above it.** The obvious mutation — a `null` min(P) counted as support — does not qualify:
        # it reddens `categories[1] == {...}` one line earlier, and this line never runs. The
        # mutation that discriminates is `missing_counts` returning `0` rather than `None` for a
        # claim with no row in the filtered population, which is exactly the conflation the
        # assertion exists to forbid: it reads `[0, 0] == [0, None]`.
        ("test_pxd026748_h5c_h9p.py", "counts == [0, None]", 1),
        # Two more from the module's single end-to-end test, both `PINNED`. `code == 0` is
        # `main`'s exit status against a literal, matched because Pass D sees a name bound from a
        # call; made to fail by `main` returning 1, which reads `1 == 0`. `len(written['h9p']
        # ['sites']) == len(CLAIM_IDS)` compares a length of what was written against the length of
        # the claim list the *test* supplied — an input the test chose, imported from
        # `tests/test_pxd026748_reconstruction.py`; made to fail by writing `sites[:2]`, which
        # reads `2 == 5`.
        ("test_pxd026748_h5c_h9p.py", "code == 0", 1),
        (
            "test_pxd026748_h5c_h9p.py",
            "len(written['h9p']['sites']) == len(CLAIM_IDS)",
            1,
        ),
        # ── tests/test_perseus_s0.py, classified individually 2026-09-21 ──────────────────────
        # **Ten matches, all `PINNED`.** Every right side is arithmetic written out in the test's
        # own docstring — `3 / (sqrt(2/3) + 0.1)`, `1 / 0.1`, `1/19`, the pooled `−4 / (sqrt(56/15)
        # + 0.1)` — or a literal, or `scipy.stats.t.sf` at hand-computed arguments, which is a
        # special function and not arithmetic the module under test performs. None is a call
        # compared against its own expression, which is the question the failure message poses.
        #
        # **Measured line by line where a line could be reached on its own.**
        #  - `result.d[0] == …sqrt(2/3)…`: `s0` dropped from the denominator, reading 3.674 against
        #    3.274. `result.d[2] == 10.0` goes with it — it is the row whose spread is zero, so the
        #    same mutation takes it to infinity.
        #  - `result.d[1] == 0` and `result.d[5] == 0` are the rows whose two group means are
        #    equal, and no denominator mutation moves them. The one that does is a numerator
        #    "guard" — `np.where(difference == 0, 1.0, difference)` — which reddens d[1] at 1.091
        #    while leaving d[0] green, so both are reachable without the line above.
        #  - `result.d[0] == pytest.approx(pooled, …)`: `pooled=True` swapped for `pooled=False`,
        #    reading −2.458 against −1.968. **That test exists because this mutation left the
        #    3-against-3 case green**: at equal group sizes the pooled and Welch standard errors
        #    are the same number, so P1 cannot tell them apart and an unequal-n case had to be
        #    added.
        #  - `used == 'exhaustive'`: the scheme labelled `random` while still enumerating.
        #    `count == 19`: the identity relabelling kept, reading 20.
        #  - `unchanged.log2fc[0] == 3.0`: `welch_t`'s difference negated. `unchanged.p_value[0]`:
        #    Welch-Satterthwaite's df off by one. Both are in `bzk/stats/tests.py`, which this
        #    entry guards as unchanged.
        #
        # **One entry is documentary and is recorded as such rather than claimed as guarded.**
        # `result.q_value[2] == pytest.approx(1.0 / 19.0)` restates in closed form one element of
        # the `assert_allclose` on the line above, which checks every q against an independent
        # enumeration. Any mutation to the q arithmetic reddens that line first, so this one
        # cannot be reached on its own; what it adds is the reading — 1/19 is the smallest FDR a
        # 19-draw null can produce, so no alpha below it is attainable at 3 against 3 — and the
        # multiset records it as a restatement rather than as a second guard.
        ("test_perseus_s0.py", "count == 19", 1),
        (
            "test_perseus_s0.py",
            "result.d[0] == pytest.approx(3.0 / (np.sqrt(2.0 / 3.0) + 0.1), rel=1e-12)",
            1,
        ),
        ("test_perseus_s0.py", "result.d[0] == pytest.approx(pooled, rel=1e-12)", 1),
        ("test_perseus_s0.py", "result.d[1] == pytest.approx(0.0)", 1),
        ("test_perseus_s0.py", "result.d[2] == pytest.approx(10.0, rel=1e-12)", 1),
        ("test_perseus_s0.py", "result.d[5] == pytest.approx(0.0)", 1),
        ("test_perseus_s0.py", "result.q_value[2] == pytest.approx(1.0 / 19.0, rel=1e-12)", 1),
        ("test_perseus_s0.py", "unchanged.log2fc[0] == pytest.approx(3.0)", 1),
        (
            "test_perseus_s0.py",
            "unchanged.p_value[0] == pytest.approx(2.0 * scipy_stats.t.sf(3.0 / np.sqrt(2.0 / 3.0), 4), rel=1e-12)",
            1,
        ),
        # **1 -> 2 on 2026-09-22**, and the multiset is what made it visible: the new
        # exhaustive-excluding-trivial test asserts the same expression, in a different scope,
        # about a different scheme. The two are not separable by this pin — the module's own
        # docstring calls that its declared limit — so both are covered by the same evidence
        # shape, the exhaustive branch labelled `"random"`, which reddens whichever runs first.
        ("test_perseus_s0.py", "used == 'exhaustive'", 2),
        # ── tests/test_perseus_s0.py, the trivial-relabelling schemes, 2026-09-22 ─────────────
        # **Six further matches, all `PINNED`**, from the three tests that land the two
        # `_excluding_trivial` schemes. Every right side is a literal count or `1/19` written out
        # in the test, and none is a call compared against its own expression. Each was measured
        # line by line, since each test carries more than one of them.
        #  - `np.nanmin(with_mirror.q_value) == pytest.approx(1.0 / 19.0)`: the mirror dropped from
        #    the scheme that keeps it (`skip = trivial`), which reads 0.0 against 0.0526. It is
        #    the assertion that pins the floor to the mirror rather than to the draw count, which
        #    is the correction this turn also made to P1's comment.
        #  - `np.nanmin(without.q_value) == pytest.approx(0.0)`: the mirror kept in the excluding
        #    scheme (`mirror = None`), which reads 0.0526 against 0.
        #  - `count == 18`: the exhaustive branch skipping only the identity, reading 19.
        #  - `unequal == kept == 55`: the mirror misread as the **last** `n_a` columns rather than
        #    as B's columns — the same set at equal sizes, a real 3-combination at 3 against 5 —
        #    which drops one relabelling too many and reads 54.
        #  - `used == 'random_excluding_trivial'`: the drawing branch labelled `"random"`.
        #  - `count == 400`: the same branch returning one draw fewer, reading 399.
        ("test_perseus_s0.py", "count == 18", 1),
        ("test_perseus_s0.py", "count == 400", 1),
        (
            "test_perseus_s0.py",
            "np.nanmin(with_mirror.q_value) == pytest.approx(1.0 / 19.0, rel=1e-12)",
            1,
        ),
        ("test_perseus_s0.py", "np.nanmin(without.q_value) == pytest.approx(0.0)", 1),
        ("test_perseus_s0.py", "unequal == kept == 55", 1),
        ("test_perseus_s0.py", "used == 'random_excluding_trivial'", 1),
        # ── tests/test_perseus_s0.py, the `joint_half` sidedness, 2026-09-22 ──────────────────
        # **Six further matches, all `PINNED`.** Every right side is a literal: `1/19`, `1/38`, or
        # a list of q-values read off the implementation at `0a6892d` in a worktree of that commit
        # and typed in here. The two `.tolist()` entries are a regression pin against a run that
        # has already happened — attempt 1's committed result — so their values deliberately come
        # from the older code rather than from this one; a first draft of that test carried
        # invented numbers and failed on two of six, which is the whole reason it is worth having.
        #
        # Measured line by line where a line could be reached on its own:
        #  - `np.nanmin(half.q_value) == 1/38`: the halving dropped (`null_scale=1.0`), reading
        #    0.0526 against 0.0263.
        #  - `np.nanmin(whole.q_value) == 1/19` and `joint.q_value.tolist() == [...]`: `joint`
        #    quietly routed through the halving (`null_scale=0.5`), reading 0.0263 against 0.0526.
        #  - `per_side.q_value.tolist() == [...]`: `d >= 0` narrowed to `d > 0` on the positive
        #    side, which leaves the zero-difference rows with no q at all and reads `nan`.
        #
        # **Two are documentary and are recorded as such rather than claimed as guarded.**
        # `_fdr_at(whole, extreme, whole.d, null) == 1/19` is computed entirely inside the test,
        # from its own enumeration of the nineteen relabellings — it states a property of the hand
        # case (exactly one null value reaches the most extreme observed `|d|`), which is what
        # anchors the `1/38` beside it; no mutation to the module reaches it. And
        # `half.q_value[argmax] == 1/38` restates one element of the `assert_allclose` two lines
        # above, which any mutation to the q arithmetic reddens first.
        (
            "test_perseus_s0.py",
            "_fdr_at(whole, extreme, whole.d, null) == pytest.approx(1.0 / 19.0, rel=1e-12)",
            1,
        ),
        (
            "test_perseus_s0.py",
            "half.q_value[np.argmax(np.abs(half.d))] == pytest.approx(1.0 / 38.0, rel=1e-12)",
            1,
        ),
        (
            "test_perseus_s0.py",
            "joint.q_value.tolist() == pytest.approx([0.05263157894736842, 1.0, 0.05263157894736842, 1.0, 1.0, 1.0])",
            1,
        ),
        (
            "test_perseus_s0.py",
            "np.nanmin(half.q_value) == pytest.approx(1.0 / 38.0, rel=1e-12)",
            1,
        ),
        (
            "test_perseus_s0.py",
            "np.nanmin(whole.q_value) == pytest.approx(1.0 / 19.0, rel=1e-12)",
            1,
        ),
        (
            "test_perseus_s0.py",
            "per_side.q_value.tolist() == pytest.approx([0.0, 0.5789473684210527, 0.0, 0.5789473684210527, 0.5789473684210527, 0.5789473684210527])",
            1,
        ),
        # ── tests/test_pxd018299_h10.py, classified individually 2026-09-22 ───────────────────
        # **Seventeen matches, all `PINNED`, and none is a call compared against its own
        # expression.** Every right side is one of three things: a literal the test wrote
        # (`0`, `1`, `10`, `0.4`, `0.5`, `1/3`, `2/3`); a value the test *chose as input* and is
        # checking came back (`names[1]`, `first`/`second`/`earlier`, `Member(0.4, 2.0, …)`, the
        # variant-name set built from `h10.VARIANTS`); or a figure from a different part of the
        # same written fixture (`per_claim_support` rows against `anchor_matrix.exposure`), which
        # is two stored surfaces rather than a call and its own expression — the shape
        # `test_published_cascade.py`'s entry already records.
        #
        # Measured line by line, since most of these tests carry several:
        #  - the three `h10.primary_variant(...)` lines and `admitted_variants`: the lowest F1
        #    taken as primary (reads `joint+random` against `joint+random_excluding_trivial`), the
        #    tie broken alphabetically, an undefined F1 scored as zero, and admission ignoring
        #    check A.
        #  - `gate_majority(SEEDS) == GATE_MAJORITY == 10`: the majority floored rather than
        #    rounded up, which still gives 10 at twenty seeds and 1 at three — so this line stays
        #    green and the `(0, 1, 2)` line below it reddens, which is why both are asserted.
        #  - the `metrics` and `lopsided` lines: F1 as the arithmetic mean. **`lopsided` exists
        #    because that mutation left the symmetric case green** — at precision == recall the
        #    harmonic and arithmetic means are the same number.
        #  - `plain['readout_b'][…]['share'] == 0.5`: the stub's own design, and the line that
        #    makes the verdict comparison beside it non-vacuous.
        #  - `code == 0` / `code == 1`: `main`'s exit status, reddened by the reverse-decoy filter
        #    inverted and by the anchor run going ahead with no admitted variant.
        #  - `configuration.member() == Member(…)`: every author file reported as tracked leaves
        #    this line green and the one above it red, so its own evidence is the defaulting of an
        #    omitted `scope`, which reads `whole_matrix` against `per_sample`.
        ("test_pxd018299_h10.py", "code == 0", 4),
        ("test_pxd018299_h10.py", "code == 1", 3),
        (
            "test_pxd018299_h10.py",
            "configuration.member() == Member(width_sd=0.4, downshift_sd=2.0, scope='per_sample', seed=3)",
            1,
        ),
        ("test_pxd018299_h10.py", "h10.admitted_variants(gate, attainability) == [names[1]]", 1),
        ("test_pxd018299_h10.py", "h10.gate_majority(SEEDS) == h10.GATE_MAJORITY == 10", 1),
        (
            "test_pxd018299_h10.py",
            "h10.primary_variant([first, second, third], gate) == second",
            1,
        ),
        ("test_pxd018299_h10.py", "h10.primary_variant([first, second], gate) == second", 1),
        ("test_pxd018299_h10.py", "h10.primary_variant([later, earlier], gate) == earlier", 1),
        (
            "test_pxd018299_h10.py",
            "len(written['readouts']['per_claim_support']['rows']) == written['anchor_matrix']['exposure']",
            1,
        ),
        ("test_pxd018299_h10.py", "lopsided['f1'] == pytest.approx(0.4)", 1),
        ("test_pxd018299_h10.py", "lopsided['precision']['share'] == pytest.approx(0.5)", 1),
        ("test_pxd018299_h10.py", "lopsided['recall']['share'] == pytest.approx(1 / 3)", 1),
        ("test_pxd018299_h10.py", "metrics['f1'] == pytest.approx(2 / 3)", 1),
        (
            "test_pxd018299_h10.py",
            "metrics['precision'] == {'numerator': 2, 'denominator': 3, 'share': pytest.approx(2 / 3)}",
            1,
        ),
        (
            "test_pxd018299_h10.py",
            "metrics['recall'] == {'numerator': 2, 'denominator': 3, 'share': pytest.approx(2 / 3)}",
            1,
        ),
        (
            "test_pxd018299_h10.py",
            "plain['readout_b']['conditional_on_imputation']['share'] == pytest.approx(0.5)",
            1,
        ),
        (
            "test_pxd018299_h10.py",
            "set(written['gate_g']['variants']) == {v.name for v in h10.VARIANTS}",
            1,
        ),
        # ── tests/test_pxd018299_h10.py, attempt 2, 2026-09-22 ────────────────────────────────
        # **Eight further matches, all `PINNED`.** Each right side is a literal the test wrote, a
        # constant the module declares and the test is checking is still what it was, or a value
        # captured before the call (`before`, the attempt 1 file's bytes read a line earlier).
        # None is a call compared against its own expression.
        #
        # Measured line by line:
        #  - `h10.variants_for(1) == h10.VARIANTS` and its `(2)` sibling: the two attempts'
        #    variant lists swapped inside `variants_for`, which reads `joint_half+random` against
        #    `joint+random`.
        #  - `_digest(written) == ATTEMPT_1_DIGEST`: attempt 1's run given the direction split too
        #    (`direction=True` at the call), and separately S1's gene column reaching attempt 1's
        #    `anchor_matrix`. **That second mutation was not planted — it was a real defect this
        #    assertion caught**, which is why the digest is measured against a worktree of
        #    `36b344a` rather than against a second run of the live code.
        #  - `admitted == names[1:]` and `admitted_variants(…) == names`: G2b made unconditional,
        #    so attempt 1's admission rule reads the split it must not read.
        #  - `set(written['gate_g']['variants']) == ATTEMPT_2_VARIANTS` and
        #    `attempt_1_path.read_bytes() == before`: `registered` pinned to `VARIANTS`, so
        #    attempt 2 scores attempt 1's eight.
        #  - `adar['largest_site_intensity'] == 9.0`: the largest site taken as the weakest, which
        #    reads the other peptide's intensity.
        ("test_pxd018299_h10.py", "adar['largest_site_intensity'] == pytest.approx(9.0)", 1),
        ("test_pxd018299_h10.py", "admitted == names[1:]", 1),
        ("test_pxd018299_h10.py", "attempt_1_path.read_bytes() == before", 1),
        (
            "test_pxd018299_h10.py",
            "h10.admitted_variants(gate, attainability, variants=h10.ATTEMPT_2_VARIANTS) == names",
            1,
        ),
        ("test_pxd018299_h10.py", "h10.variants_for(1) == h10.VARIANTS", 1),
        ("test_pxd018299_h10.py", "h10.variants_for(2) == h10.ATTEMPT_2_VARIANTS", 1),
        (
            "test_pxd018299_h10.py",
            "set(written['gate_g']['variants']) == {v.name for v in h10.ATTEMPT_2_VARIANTS}",
            1,
        ),
        # ── tests/test_pxd018299_h10.py, attempt 3, 2026-09-22 ────────────────────────────────
        # **Eight entries, all `PINNED`, and one of them is an expression attempt 2's block
        # carried under another name** — `_digest(written) == ATTEMPT_1_DIGEST` became
        # `_digest(one)` beside a new `_digest(two)`, so the old entry is removed here rather
        # than left beside the two new ones: the `gone` half of the assertion below is what makes
        # a pin describing a suite that no longer exists a failure rather than a comment.
        # `attempt_1_path.read_bytes() == before` was removed with it on the first pass and put
        # back, because `gone` reported it and `new` then reported it again: attempt 2's own
        # single-fixture test still carries that line, and only the digest test's loop is new.
        #
        # Measured line by line, each against a mutation of `bzk/sources/pxd018299_h10.py`
        # confirmed applied by reading the file back and reverted afterwards:
        #  - `_digest(one) == ATTEMPT_1_DIGEST`: `family_block_for`'s `disclosed` defaulting to
        #    `True`, so attempt 3 §1's label reaches attempt 1's readout A.
        #  - `_digest(two) == ATTEMPT_2_DIGEST`: attempt 2's header gaining attempt 3's `matrix`
        #    flag. **This is the entry that makes turn 20's digest test cover two attempts rather
        #    than one** — under that mutation the attempt 1 digest above it stays green, which is
        #    exactly what a single pinned digest could not have told anyone.
        #  - `(fixtures / name).read_bytes() == bytes_`: attempt 3 writing its block a second time
        #    under `FIXTURE_NAME_ATTEMPT_2`. Reddened at the first index that differs; a mutation
        #    that merely renamed attempt 3's own output reddens the *open* of the file instead,
        #    which is a crash and not this line, so the clobbering one is the recorded evidence.
        #  - `code == 0`, 1 -> 4: `_attempt_3`'s closing `return 0` returned 1. Exactly the three
        #    new occurrences reddened and the attempt-1 one did not, which is what pins the count
        #    rather than the expression.
        #  - `code == 1`, 1 -> 3: `g2_rerun_consistency` reporting `consistent: True` regardless,
        #    and separately the unadmitted-primary branch writing a verdict and returning 0. One
        #    new occurrence each; the attempt-1 one keeps its own recorded evidence above.
        #  - `len(entry['counts_by_seed']) == len(GATE_SEEDS)`: `counts_by_seed` truncated to
        #    `seed_counts[:1]`.
        #  - `entry['median'] == float(np.median(entry['counts_by_seed']))`: the counts reported
        #    one higher than the counts summarised, so the two fields disagree. **The mutation
        #    this line looks written for — the median reported as the mean — left it green**, and
        #    is recorded rather than swapped out: at synthetic scale every seed returns the same
        #    count, and on a constant list the mean, the median and the maximum are one number.
        #    It is the same shape as the pooled-versus-Welch and harmonic-versus-arithmetic traps
        #    this suite has hit twice before. That mutation does redden
        #    `test_check_a_uses_the_median_over_seeds_and_not_any_seed`, whose counts are stubbed
        #    to `[0] * 20` with a single 1 — `assert 0.05 == 0.0` — so the median *is* guarded;
        #    it is guarded there and not here.
        #  - `set(written['check_a']) == {v.name for v in h10.ATTEMPT_3_VARIANTS}`: the reported
        #    `check_a` narrowed to the primary's entry. Narrowing the *call* instead raises inside
        #    admission before the assertion is reached, so the reported block is what is mutated.
        ("test_pxd018299_h10.py", "(fixtures / name).read_bytes() == bytes_", 1),
        ("test_pxd018299_h10.py", "_digest(one) == ATTEMPT_1_DIGEST", 1),
        ("test_pxd018299_h10.py", "_digest(two) == ATTEMPT_2_DIGEST", 1),
        (
            "test_pxd018299_h10.py",
            "entry['median'] == float(np.median(entry['counts_by_seed']))",
            1,
        ),
        ("test_pxd018299_h10.py", "len(entry['counts_by_seed']) == len(GATE_SEEDS)", 1),
        (
            "test_pxd018299_h10.py",
            "set(written['check_a']) == {v.name for v in h10.ATTEMPT_3_VARIANTS}",
            1,
        ),
    }
)


#: Matches classified as instances of the class: the call **is** the expression the producing code
#: used. Each was confirmed by mutating that code and observing what stayed green — the evidence is
#: the third element, and the trigger for all four is `HANDOFF.md` §8.
@dataclass(frozen=True)
class Evidence:
    """A mutation and its recorded outcome, in a form the suite re-runs.

    **This replaced a prose string on 2026-08-08, after establishing that re-running it is
    mechanically possible rather than asserting that it is not.** The string said things like
    *"archived_sequences -> found[:-1]: whole suite green"*, and `INSTANCES`'s consumer bound it to
    `_evidence` and never read it — so the record carried a mutation result that nothing checked and
    that would survive the code changing underneath it, which is this session's class inside the
    artefact built to close it.

    Measured cost of re-running it, since the decision had to rest on a number rather than a
    judgement: copying the repository minus `.venv`, `.git` and the caches is **0.08 s** with
    `__pycache__` carried over (1.22 s without, which is what a cold copy costs); one whole-suite
    run in the copy, self-deselected, is **12.4 s**; one module **1.3 s**; one test **0.3 s**. The
    five runs below total **~15 s**, taking the suite from roughly 9 s to roughly 24 s. That is the
    price of the record being true rather than asserted, and it is paid.

    One reduction was taken and is named: `content_hash`'s *"suite red elsewhere"* is checked
    against `tests/test_raw_store.py` rather than the whole suite. That is a 12 s saving and it
    makes the claim **more** precise, not less — it names where the mutation is caught instead of
    asserting that somewhere does.
    """

    target: str
    #: Exact text to replace, which must occur exactly once — a replacement that silently misses
    #: produces a green run indistinguishable from a guard that does not fire.
    old: str
    new: str
    #: `pytest` arguments whose run must stay **green** under the mutation. That greenness is what
    #: makes the assertion an instance: its own scope cannot see the defect.
    green_scope: tuple[str, ...]
    #: Optional scope that must go **red**, where the record claims the defect is caught elsewhere.
    #: `None` where the record claims nothing catches it, which is the stronger finding.
    red_scope: tuple[str, ...] | None


_LOADER_TEST = (
    "tests/test_curation_loader.py::test_sample_mapping_hands_the_adapter_the_analysis_id"
)

#: **Split into two on 2026-08-08, after establishing the rows are separable.** One shared
#: `Evidence` made the reported row an artefact of alphabetical order: the consumer sorted by
#: `(module, source)` and skipped an `Evidence` already seen, `archive_digest` sorts before
#: `sequences_checked`, and so a change to the *`sequences_checked`* row's property failed naming
#: the *`archive_digest`* row — correct verdict, wrong row, and an instruction that was wrong for
#: the row it named. Separability was established by running, not argued: `archive_digest` is
#: called by the second assertion and not the first, and mutating it leaves the whole suite green.
_SEQUENCES_CHECKED_EVIDENCE = Evidence(
    target="bzk/drift.py",
    old="    return found\n",
    new="    return found[:-1]\n",
    green_scope=("-q",),
    red_scope=None,
)

_ARCHIVE_DIGEST_EVIDENCE = Evidence(
    target="bzk/drift.py",
    old='    return "sha256:" + hashlib.sha256(joined.encode("utf-8")).hexdigest()[:32]',
    new='    return "sha256:" + hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]',
    green_scope=("-q",),
    red_scope=None,
)

INSTANCES: frozenset[tuple[str, str, Evidence]] = frozenset(
    {
        (
            "test_drift.py",
            "receipt.sequences_checked == len(drift.archived_sequences(home))",
            _SEQUENCES_CHECKED_EVIDENCE,
        ),
        (
            "test_drift.py",
            "receipt.archive_digest == drift.archive_digest(drift.archived_sequences(home))",
            _ARCHIVE_DIGEST_EVIDENCE,
        ),
        (
            "test_perseus.py",
            "dataset['content_hash'] == content_hash(TABLE.read_bytes())",
            Evidence(
                target="bzk/provenance/raw_store.py",
                old='    return f"sha256:{sha256_hex(data)}"',
                new='    return "sha256:" + sha256_hex(data + b"X")',
                green_scope=("tests/test_perseus.py", "-q"),
                red_scope=("tests/test_raw_store.py", "-q"),
            ),
        ),
        (
            "test_curation_loader.py",
            "{s['id'] for s in mapping.samples} == set(loaded.sample_ids.values())",
            Evidence(
                target="bzk/curation/loader.py",
                old='        key: evidence_id("Sample", props, {"Experiment": experiment_id})',
                new='        key: evidence_id("Sample", props, {"Experiment": experiment_id}) + "X"',
                green_scope=(
                    _LOADER_TEST,
                    "-q",
                ),
                red_scope=("tests/test_curation_loader.py", "-q"),
            ),
        ),
    }
)


def _run_in_a_mutated_copy(evidence: Evidence, scope: tuple[str, ...]) -> int:
    """Copy the repository, apply the mutation, run `pytest` over `scope`, return its exit code.

    A copy rather than the working tree, for two reasons: a crash mid-run would otherwise leave the
    tree mutated, and an in-place whole-suite run would re-enter this module.

    **`__pycache__` is excluded, and it was not until 2026-08-09.** `copytree` uses `copy2`, so a
    copied `.pyc` arrives with the mtime bookkeeping that made it valid where it came from, and the
    interpreter in the copy then loads **the working tree's last compiled bytecode** in preference
    to the source beside it. Observed rather than reasoned: with `__pycache__` copied, this helper
    reported a failure in `/home/user/…/tests/test_query_real_graph.py` — the *original* path,
    embedded in the stale code object — asserting a figure the source in the copy no longer
    contained; excluding it, the same run is 378 passed. That makes the omission the sharpest
    version of the defect this module exists to find: **the instrument that classifies every other
    assertion could report a result it had not computed**, in either direction, because the mutation
    it applied to the source need never have been executed. Every recorded classification here rests
    on this function, so it is the one place a stale read is not merely a flake.
    """
    root = TESTS.parent
    ignore = shutil.ignore_patterns(
        ".venv", ".git", ".pytest_cache", ".ruff_cache", ".mypy_cache", "__pycache__"
    )
    with tempfile.TemporaryDirectory() as tmp:
        copy = pathlib.Path(tmp) / "repo"
        shutil.copytree(root, copy, ignore=ignore, symlinks=True)
        target = copy / evidence.target
        source = target.read_text(encoding="utf-8")
        assert source.count(evidence.old) == 1, (
            f"{evidence.target}: the recorded mutation's `old` text occurs "
            f"{source.count(evidence.old)} times, not once — the evidence names code that has "
            "moved, so the recorded outcome describes a mutation that can no longer be applied"
        )
        target.write_text(source.replace(evidence.old, evidence.new, 1), encoding="utf-8")
        assert evidence.new in target.read_text(encoding="utf-8"), "mutation did not apply"
        env = dict(os.environ, PYTHONPATH=str(copy))
        result = subprocess.run(
            [sys.executable, "-m", "pytest", *scope, f"--ignore=tests/{SELF}"],
            cwd=copy,
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        return result.returncode


def test_the_pinned_multiset_has_not_changed_unreviewed() -> None:
    """A new matching expression, **or a new occurrence of one**, must be classified before it lands.

    **Re-keyed from a set to a multiset, 2026-08-08.** The record was `(module, normalized source)`,
    and the module argued that pinning the set rather than a count was deliberate because *"a count
    is satisfied by deleting one substantive assertion and adding one tautological assertion in the
    same module"*. That is true and its converse is equally true: **a set is satisfied by
    duplicating any pinned assertion.** Planted and confirmed before the re-key — a second copy of
    `test_drift.py`'s confirmed instance, as its own standalone assert, left the module green with
    `sweep()` reporting 633 asserts, 82 matches, 0 new. The two arguments each covered the other's
    hole and neither covered its own, and the module stated one of them as though it settled the
    question.

    A multiset is one key rather than two guards, so its own limit can be stated instead of inferred
    from a pair: **it is scope-blind.** It records how many times an expression text occurs in a
    module, never where, so two occurrences that differ only in what their names are bound to are
    one entry with a count of two. Where that matters — Pass D's shape depends on the enclosing
    scope's assignments — a non-matching occurrence simply is not counted, so the count still moves;
    what it cannot separate is two *matching* occurrences whose classifications would differ.

    The re-key also surfaced four occurrences the set had been collapsing silently: 86 occurrences
    across 82 expressions, `evidence_id('Analysis', a) == evidence_id('Analysis', b)` appearing four
    times in `test_keys.py` and `store.count_nodes(conn) == EXPECTED_NODES` twice in
    `test_rebuild.py`.
    """
    found, modules, asserts = sweep()
    # Denominated at the exact current surface, re-denominated three times on 2026-08-09: 655 ->
    # 662 for the local-part guard, 662 -> 687 for `tests/test_pins.py` (also the twenty-first
    # module), 687 -> 714 for `Gene` and its change-set check, 714 -> 786 for the read path (also
    # the twenty-second and twenty-third modules), and 786 -> 821 for the interface (the
    # twenty-fourth). It read `asserts >= 600` against 633, which
    # tolerated deleting a twentieth of the suite's assertions — the case its own failure message
    # names. A legitimate reduction lowers these numbers in the same change, the same discipline
    # the multiset carries; additions never trip it, because an added *match* is caught by the
    # multiset rather than by this floor — but leaving the floor behind the surface reintroduces
    # exactly the slack the re-denomination removed, so it moves with every addition too.
    #
    # **And it did not move, twice, which is the slack arriving by the route that sentence names.**
    # 821 -> 926 and 24 -> 26 on 2026-08-10, covering `tests/test_analysis_differential.py` (the
    # twenty-fifth, landed at `91ba011` on 2026-08-09) as well as this turn's protein adapter (the
    # twenty-sixth). The differential turn added a module and its assertions without
    # re-denominating, and nothing failed — because nothing can: `>=` is silent about a surface
    # that grew. A floor that moves only when someone remembers is the shape of check this module
    # exists to replace, so the number is re-read from `sweep()` rather than incremented.
    #
    # 926 -> 942 and 26 -> 27 on 2026-08-10, for I20's cases and
    # `tests/test_query_absence_coverage.py` (the twenty-seventh); then 942 -> 949 the same day for
    # ADR-0025's five guards, no new module; then 949 -> 967 and 27 -> 28 for
    # `tests/test_decision_index.py` (the twenty-eighth). Checked rather than assumed each time:
    # the floor is read off `sweep()` again, and the `>=` did not fail on the additions — it
    # cannot, which is the standing reason this line moves by hand. Then 967 -> 986 and 28 -> 29
    # for `tests/test_fetch_progress.py` — **which added no match at all**: every one of its
    # equalities compares against a literal display, which Pass C excludes by construction. A
    # turn that grows the surface and the match set by zero is exactly the case this floor exists
    # to keep visible, since the multiset alone would have said nothing.
    #
    # 1007 -> 1039 and 30 -> 31 on 2026-08-12 for `tests/test_deposit_survey.py` (the
    # thirty-first), which added **nine** matches — the site/skip assertions; the
    # vocabulary pin written to close their one residual exposure adds an assert and no match,
    # because its right side is a literal display. Classified above, one at
    # a time, with the mutation that fails each named. Read off `sweep()`.
    #
    # 993 -> 1007 and 29 -> 30 on 2026-08-11 for `tests/test_command_blocks.py` (the thirtieth),
    # which added **one** match — `gaps == []`, classified above with the mutation that establishes
    # it is carried by two siblings rather than by itself. Read off `sweep()`.
    #
    # 986 -> 993 on 2026-08-10 for I21's eight cases, module count unchanged at 29 — they live in
    # `tests/test_invariants.py`. The new equalities were classified one at a time rather than in
    # aggregate: two are `ei.value.invariant == "I21"` and one is `len(_RESULT_ANCHORS) == 5`, all
    # comparisons against a literal display, which Pass C excludes exactly as it excludes the same
    # shape for I2 through I20; one is `declared[rel] == ("DifferentialResult", label)`, a
    # comparison against a value the test derives from `schema.REL_TABLES`, which Pass C also
    # excludes as a literal display. The remaining additions are `in str(...)` membership
    # assertions, which this pass never matched.
    #
    # **The match set moved by one and then back to zero, and the one was real.** The direction
    # test was written with `set(_RESULT_ANCHORS) == set(schema.IDENTITY['DifferentialResult']
    # .anchors)` in it, and this module matched it immediately: `_RESULT_ANCHORS` *is* that
    # expression, so the assertion compared a value to itself. It was removed rather than pinned.
    # That is this module catching a tautology in the same turn it was written, which is the first
    # time it has done so on new code rather than on the audit that created it.
    # 1039 -> 1123 on 2026-08-12, no new module: the extractor's tests in
    # `tests/test_deposit_survey.py` (the thirty-first module already counted). Read off
    # `sweep()` rather than incremented, and moved for those tests alone — the `>=` did not
    # fail on the additions, which is the standing reason this line moves by hand.
    # 1123 -> 1129 on 2026-08-18, and **31 -> 32 — the module count moves this time**. The
    # previous move left it at 31 because the new tests landed in `tests/test_deposit_survey.py`,
    # a module the sweep already counted; `tests/test_agent_config_references.py` is a module that
    # did not exist, so both figures move together as they did at 993 -> 1007 / 29 -> 30. Read off
    # `sweep()` — 32 modules, 1129 asserts — rather than incremented, and moved for that module's
    # three tests alone.
    # 1129 -> 1641 and 32 -> 47 on 2026-09-20, with `tests/test_anova.py` (the forty-seventh).
    # **Fifteen modules and five hundred assertions accrued behind this line without it moving**,
    # which is the slack the two re-denominations above already named and then took again: `>=` is
    # silent about a surface that grew, so it moves only when someone remembers, and between
    # 2026-08-18 and today nobody did. It is read off `sweep()` rather than incremented, and the
    # gap is recorded here rather than closed quietly — a floor that lags the surface by a third
    # tolerates deleting a third of the suite's assertions, which is the case its own failure
    # message describes.
    # 1641 -> 1653 and 47 -> 48 the same day for `tests/test_t_variants.py` (the
    # forty-eighth), read off `sweep()` in the same way.
    # 1653 -> 1693 and 48 -> 49 the same day for `tests/test_pxd026748_reconstruction.py`
    # (the forty-ninth), read off `sweep()` in the same way.
    assert modules >= 49 and asserts >= 1693, (
        f"the surface shrank to {modules} modules / {asserts} asserts — a sweep over a surface "
        "that quietly stopped covering the tests is the defect this module exists to catch"
    )
    observed = {(module, source, count) for (module, source), count in found.items()}
    new = observed - PINNED
    gone = PINNED - observed
    assert not new, (
        f"{len(new)} matching expression(s) or occurrence count(s) are not classified: "
        f"{sorted(new)}. Each entry is (module, expression, occurrences). Read each one: if its "
        "call is the expression that produced the other side it is an instance and belongs in "
        "INSTANCES with its Evidence; otherwise add it to PINNED with its count."
    )
    assert not gone, (
        f"{len(gone)} pinned entr(ies) no longer match the tree: {sorted(gone)}. A count that fell "
        "means an occurrence was removed; an entry that vanished means the expression was. Update "
        "PINNED (and INSTANCES) in the same change, so the pin cannot drift into describing a "
        "suite that no longer exists."
    )


#: One synthetic module carrying every shape the net declares it reaches, so the net's *reach* is
#: exercised against source written to contain each rather than against the tree it reports on.
#: Eight asserts, six of them matching, seven matching comparisons. Every match is a Pass C shape except the last, which is
#: Pass D. Kept as source text rather than a fixture file so the shapes and the expectations are
#: readable together.
PLANTED = """
import mod

TOP = mod.produce()
assert TOP == mod.produce()                        # 1 module-level assert, matches

async def test_async() -> None:
    got = mod.produce()
    assert got == mod.produce()                    # 2 inside an AsyncFunctionDef, matches

def test_outer() -> None:
    def inner() -> None:
        assert mod.value() == mod.value()          # 3 inside a nested function, matches, counted 1x
    inner()
    assert 1 == 1                                  # 4 no match
    assert True and mod.a() == mod.b()             # 5 SECOND comparison in the assert, matches
    assert mod.left(p) == q and r == mod.right(s)  # 6 ONE assert, TWO matching comparisons
    held = mod.derive()
    assert held == OTHER                           # 7 Pass D: bare name bound from a call
    assert [1, 2] == [1, 2]                        # 8 no match, literal displays
"""

#: What `analyse` must return for `PLANTED`. Written from the shapes, not from a run — a expected
#: value read off the implementation is the defect this module is about.
PLANTED_MATCHES = {
    "TOP == mod.produce()",
    "got == mod.produce()",
    "mod.value() == mod.value()",
    "mod.a() == mod.b()",
    "mod.left(p) == q",
    "r == mod.right(s)",
    "held == OTHER",
}
PLANTED_ASSERTS = 8


def test_the_net_reaches_every_granularity_it_declares() -> None:
    """Planting, at each granularity at which the examined surface can shrink below the declared one.

    Enumerated before the widened net was written, because the previous round's three mutations all
    acted at whole-assert or whole-module granularity and neither repaired defect could have shown
    up there. Each shape below fails this test if the net stops reaching it:

      * a second (and third) comparison inside one assert — the `break` defect, planted directly;
      * an assert inside a nested function, which must be found **and counted once**;
      * an assert inside an `AsyncFunctionDef`;
      * an assert at module level, outside any function;
      * a call on either side of the comparison, not only the right;
      * Pass D's bare-name shape, in a scope that is not a `FunctionDef` body.

    The remaining granularity — a whole module dropped from the surface — is not plantable here,
    since `analyse` takes one module; it is covered by `test_a_non_test_module_is_still_swept` and
    by the module floor.
    """
    matched, asserts = analyse("planted.py", PLANTED)
    assert asserts == PLANTED_ASSERTS, (
        f"counted {asserts} asserts in the planted module, expected {PLANTED_ASSERTS} — a nested "
        "function counted twice inflates this, and the floor below is denominated in it"
    )
    assert {src for _, src in matched} == PLANTED_MATCHES, (
        f"the net's reach changed. missing: {sorted(PLANTED_MATCHES - {s for _, s in matched})}; "
        f"unexpected: {sorted({s for _, s in matched} - PLANTED_MATCHES)}"
    )


def test_a_non_test_module_is_still_swept(tmp_path: pathlib.Path) -> None:
    """The surface is `tests/`, not `tests/test_*.py`. Zero such modules exist today, which is why
    this is planted rather than measured: a helper or a `conftest.py` added later would otherwise
    join the suite outside the net without anything saying so."""
    (tmp_path / "helper.py").write_text("def f():\n    assert x == g(y)\n", encoding="utf-8")
    (tmp_path / "test_real.py").write_text("def test_a():\n    assert 1 == 1\n", encoding="utf-8")
    found, modules, asserts = sweep(tmp_path)
    assert modules == 2 and asserts == 2
    assert ("helper.py", "x == g(y)") in found


def test_every_classified_instance_is_still_present() -> None:
    """An instance must not leave the record by being deleted or edited without a decision.

    **This check is keyed on the expression, not on an occurrence of it, and the failure message
    was corrected on 2026-08-08 to stop describing a state the key cannot see.** It said *"if it was
    fixed, remove it from INSTANCES"*, which reads as though presence-or-absence tracked whether the
    instance had been repaired. It does not: an instance whose producing code is fixed keeps its
    text and stays present here. What catches a fixed instance is
    `test_every_classified_instance_re_runs_its_recorded_evidence`, whose mutation stops leaving the
    named scope green. And duplication of an instance is caught by `PINNED`'s multiset, which counts
    occurrences. So this check has exactly one job — the text is gone, or it is not — and no second
    guard is added for either state, because both already have one.
    """
    found, _, _ = sweep()
    pinned_pairs = {(module, source) for module, source, _count in PINNED}
    for module, source, _evidence in sorted(INSTANCES, key=lambda i: (i[0], i[1])):
        assert (module, source) in found, (
            f"{module} no longer contains {source!r} at all — the text was deleted or edited. This "
            "says nothing about whether the instance was *fixed*: a repaired instance keeps its "
            "text, and the evidence re-run is what notices that. Remove the row and say so where "
            "the trigger is recorded (HANDOFF.md §8)."
        )
        assert (module, source) in pinned_pairs, (
            f"{module}: {source!r} is an instance but not pinned"
        )


def test_every_classified_instance_re_runs_its_recorded_evidence() -> None:
    """The evidence is re-run, not read. See `Evidence` for the measured cost of doing so.

    Until 2026-08-08 the third element of each `INSTANCES` row was prose bound to `_evidence` and
    never read, while two artefacts said the evidence was carried and a third said the trigger was
    "enforced rather than remembered". Changing `drift.run` to compute `sequences_checked`
    independently would have left the prose intact, the module green, and the record describing a
    mutation result that no longer held.
    """
    for module, source, evidence in sorted(INSTANCES, key=lambda i: (i[0], i[1])):
        # No de-duplication by `Evidence` any more. It existed because the two `test_drift.py` rows
        # shared one mutation, and it made the row named in a failure a function of sort order
        # rather than of which row the mutation bears on. Every row now carries a mutation of the
        # code *its own* value depends on, so the row named is the row at fault.
        green = _run_in_a_mutated_copy(evidence, evidence.green_scope)
        assert green == 0, (
            f"{module}: {source!r} is recorded as an instance because {evidence.green_scope} stays "
            f"green under {evidence.target}'s mutation, and it did not (exit {green}). Either the "
            "assertion now catches the defect — in which case it is no longer an instance and the "
            "row comes out — or the mutation no longer targets the code the record names."
        )
        if evidence.red_scope is not None:
            red = _run_in_a_mutated_copy(evidence, evidence.red_scope)
            assert red != 0, (
                f"{module}: the record says {evidence.red_scope} catches this mutation elsewhere, "
                "and it passed. Nothing catches it, which makes this a stronger finding than the "
                "record states, not a weaker one — set red_scope to None and say so in §8."
            )


def test_no_repository_copy_carries_compiled_bytecode() -> None:
    """Every `shutil.copytree` in the tree excludes `__pycache__`. One instance, asserted anyway.

    **Written the day the one instance was wrong, and written because it was the only one.** The
    repository's standing rule is that a property true of zero or one site is exactly the property
    to assert rather than to note, because prose that is true today is indistinguishable from prose
    that stopped being true — the same argument that turned the reserved-namespace sweep from a
    `HANDOFF.md` §8 row into a test. `_run_in_a_mutated_copy` above is the site; what it copies is
    what every recorded classification in this module is computed from, so a second copier added
    later without the exclusion would silently widen a defect rather than introduce a new one.

    Asserted over the *source* rather than by calling the helper, since the failure being guarded is
    a copy that runs the wrong bytes — which a runtime check would be subject to as well.
    """
    roots = [TESTS, TESTS.parent / "bzk"]
    copies = 0
    for path in sorted(p for root in roots for p in root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        # `ignore=` is usually a local bound to `ignore_patterns(...)` one line above, so a name is
        # resolved to the call it was assigned rather than reported as unreadable — the readable
        # form is the common one and a guard that only accepted the inline form would be dodged by
        # the ordinary way of writing it. Resolved **per enclosing scope**, not per module: this
        # very function assigns `ignore` twice for its own purposes, and a module-wide map bound the
        # name to the last of them and reported a false positive against the code above.
        # Innermost scope first, module last, so a `copytree` inside a function resolves against
        # that function's own bindings. `ast.walk` yields a nested function after its parent, so
        # reversing the function list is what puts the nearest enclosing scope first.
        functions = [
            n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)
        ]
        scopes: list[ast.AST] = [*reversed(functions), tree]
        seen: set[int] = set()
        for scope in scopes:
            bound: dict[str, ast.Call] = {
                target.id: n.value
                for n in ast.walk(scope)
                if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call)
                for target in n.targets
                if isinstance(target, ast.Name)
            }
            for node in ast.walk(scope):
                if not isinstance(node, ast.Call) or id(node) in seen:
                    continue
                if not (isinstance(node.func, ast.Attribute) and node.func.attr == "copytree"):
                    continue
                seen.add(id(node))
                copies += 1
                where = f"{path.name}:{node.lineno}"
                ignore = next((k.value for k in node.keywords if k.arg == "ignore"), None)
                assert ignore is not None, (
                    f"{where}: copytree with no `ignore` copies `__pycache__`"
                )
                if isinstance(ignore, ast.Name):
                    ignore = bound.get(ignore.id, ignore)
                assert isinstance(ignore, ast.Call), (
                    f"{where}: `ignore` is not a call this guard can read, so whether `__pycache__` is "
                    "excluded cannot be established — inline the `ignore_patterns(...)` or bind it once"
                )
                patterns = {
                    arg.value
                    for arg in ignore.args
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str)
                }
                assert "__pycache__" in patterns, (
                    f"{where}: copytree's ignore patterns are {sorted(patterns)} and omit "
                    "`__pycache__` — the copy will load the source tree's compiled bytecode in "
                    "preference to the sources beside it, and Python's size-and-mtime invalidation "
                    "does not catch a same-size edit made within one second"
                )
    assert copies, (
        "no `copytree` call found — this guard has nothing to check and would pass anyway"
    )
