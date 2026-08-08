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

**Pinning the match set rather than a count is deliberate.** A count is satisfied by deleting one
substantive assertion and adding one tautological assertion in the same module, which is precisely
the drift this exists to catch.

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


def sweep(directory: pathlib.Path | None = None) -> tuple[set[tuple[str, str]], int, int]:
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
        so `assert a == 0 and <a confirmed instance>` passed. Planted and confirmed: the module
        stayed green over an instance of the class it exists to catch.
      * **one assert was counted and examined twice**, per `_enclosing_function` above.
      * **three edges were unreachable by construction** — an `AsyncFunctionDef`, an assert outside
        any function, and a `.py` file in `tests/` that is not `test_*.py`. All three measure zero
        today, so covering them changes no count; they are covered because the declaration says
        *every assertion in `tests/`* and a surface that silently excludes a shape is this class
        whether or not the shape is currently present.
    """
    found: set[tuple[str, str]] = set()
    modules = 0
    asserts = 0
    directory = TESTS if directory is None else directory
    for path in sorted(directory.glob("*.py")):
        if path.name == SELF:
            continue
        modules += 1
        matched, counted = analyse(path.name, path.read_text(encoding="utf-8"))
        found |= matched
        asserts += counted
    return found, modules, asserts


def analyse(name: str, source: str) -> tuple[set[tuple[str, str]], int]:
    """The net over one module's source. Split out so it can be planted with synthetic input.

    That split is the point rather than tidiness: the three mutations offered as confirmation on
    2026-08-08 all acted at whole-assert or whole-module granularity, and the two defects repaired
    here live *below* an assert and *inside* the counter, where none of them could reach. A net
    whose reach is only ever exercised against the tree it reports on cannot show that its reach is
    what it claims — so `test_the_net_reaches_every_granularity_it_declares` runs this over source
    that contains each shape deliberately.
    """
    found: set[tuple[str, str]] = set()
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
                found.add((name, ast.unparse(cmp_)))
    return found, asserts


#: Every assertion in `tests/` matching Pass C or Pass D, as `(module, normalized source)`.
#: Normalized source rather than a line number, so unrelated edits above it do not churn the pin.
#: Regenerate with `python -c "from tests.test_tautology_sweep import sweep;
#: print(sorted(sweep()[0]))"` **after** classifying whatever is new.
PINNED: frozenset[tuple[str, str]] = frozenset(
    {
        (
            "test_curation_content_hash.py",
            "_record(name)['content_hash'] == PXD018299_SITES.expected_content_hash",
        ),
        ("test_curation_content_hash.py", "_records_citing_the_deposit() == set(CITING_RECORDS)"),
        ("test_curation_content_hash.py", "accession == PXD018299_SITES.accession"),
        (
            "test_curation_loader.py",
            "len(set(loaded.sample_ids.values())) == len(loaded.sample_ids)",
        ),
        ("test_curation_loader.py", "load(changed).dataset_id == loaded.dataset_id"),
        (
            "test_curation_loader.py",
            "set(_record(MINTED_IDS)['samples']) == set(_record(REAL_RECORD)['mapping'])",
        ),
        (
            "test_curation_loader.py",
            "set(load(changed).sample_ids.values()) == set(loaded.sample_ids.values())",
        ),
        ("test_curation_loader.py", "sources == set(loaded.sample_ids.values())"),
        (
            "test_curation_loader.py",
            "{n['label'] for n in _nodes(loaded, 'Sample')} == set(loaded.sample_ids)",
        ),
        (
            "test_curation_loader.py",
            "{s['id'] for s in mapping.samples} == set(loaded.sample_ids.values())",
        ),
        ("test_drift.py", "drift.STALE_AFTER_DAYS == int(stated.group(1))"),
        ("test_drift.py", "drift.read_receipt(home) == receipt"),
        (
            "test_drift.py",
            "receipt.archive_digest == drift.archive_digest(drift.archived_sequences(home))",
        ),
        ("test_drift.py", "receipt.sequences_checked == len(drift.archived_sequences(home))"),
        (
            "test_keys.py",
            "canonical_parameters_json('{\"n\": 1e16}') == canonical_parameters_json('{\"n\": 10000000000000000}')",
        ),
        (
            "test_keys.py",
            "canonical_parameters_json('{\"n\": 1e22}') == canonical_parameters_json('{\"n\": 10000000000000000000000}')",
        ),
        ("test_keys.py", "canonical_value(8, 'DOUBLE') == canonical_value(8.0, 'DOUBLE') == '8.0'"),
        (
            "test_keys.py",
            "evidence_id('Analysis', SITE_ANALYSIS, child_values=a) == evidence_id('Analysis', SITE_ANALYSIS, child_values=b)",
        ),
        (
            "test_keys.py",
            "evidence_id('Analysis', SITE_ANALYSIS, child_values={'Imputation': [one, two]}) == evidence_id('Analysis', SITE_ANALYSIS, child_values={'Imputation': [two, one]})",
        ),
        ("test_keys.py", "evidence_id('Analysis', a) == evidence_id('Analysis', b)"),
        (
            "test_keys.py",
            "evidence_id('Analysis', dict(SITE_ANALYSIS, localization_threshold=0.75)) == evidence_id('Analysis', dict(SITE_ANALYSIS, localization_threshold=0.75))",
        ),
        (
            "test_keys.py",
            "evidence_id('Analysis', protein) == evidence_id('Analysis', dict(protein))",
        ),
        ("test_keys.py", "protein == 'uniprot:P20591'"),
        ("test_keys.py", "sequence == 'uniprot:P20591#sv4'"),
        ("test_keys.py", "site == 'uniprot:P20591#sv4#K48#unimod:121'"),
        ("test_maxquant.py", "accessions == ['P20591', 'P19525']"),
        ("test_maxquant_sites.py", "set(modifiers) == set(schema.GG_REMNANT_MODIFIERS)"),
        ("test_perseus.py", "dataset['content_hash'] == content_hash(TABLE.read_bytes())"),
        (
            "test_perseus.py",
            "ids == {'uniprot:P20591', 'uniprot:P19525', 'uniprot:O43593', 'uniprot:P05161'}",
        ),
        ("test_perseus.py", "mx1['adj_p_value'] == pytest.approx(0.0012)"),
        ("test_perseus.py", "mx1['log2fc'] == pytest.approx(3.42)"),
        ("test_perseus.py", "p_values[0] == pytest.approx(10 ** (-5.02))"),
        ("test_perseus.py", "result['adj_p_value'] == pytest.approx(0.0012)"),
        ("test_perseus.py", "result['p_value'] == pytest.approx(3.0902e-05)"),
        ("test_perseus.py", "store.ids_by_label(conn) == before"),
        ("test_protein_groups.py", "[asdict(m) for m in measured] == _pinned()"),
        (
            "test_protein_groups.py",
            "m['multi_fraction'] == pytest.approx(m['multi_accession'] / m['rows'], abs=5e-05)",
        ),
        (
            "test_pxd018299_baseline.py",
            "getattr(row, field) == pytest.approx(want[field], rel=FLOAT_RTOL)",
        ),
        ("test_pxd018299_baseline.py", "len(_rows()) == _record()['n_expected_total']"),
        ("test_pxd018299_baseline.py", "recovered == _record()['n_expected_recovered']"),
        (
            "test_pxd018299_baseline.py",
            "tuple((row['gene'] for row in _rows() if not row['recovered'])) == NOT_RECOVERED",
        ),
        (
            "test_pxd018299_baseline.py",
            "tuple((row['gene'] for row in _rows())) == EXPECTED_TARGETS",
        ),
        ("test_pxd018299_baseline.py", "{row.gene for row in rederived.targets} == set(expected)"),
        ("test_raw_store.py", "again.path.read_bytes() == PAYLOAD"),
        ("test_raw_store.py", "content_hash(PAYLOAD) == f'sha256:{sha256_hex(PAYLOAD)}'"),
        (
            "test_raw_store.py",
            "fetch(pinned, home=tmp_path, session=_StubSession()).content_hash == content_hash(PAYLOAD)",
        ),
        (
            "test_raw_store.py",
            "store(PAYLOAD, 'sites.txt', home=tmp_path).content_hash == content_hash(PAYLOAD)",
        ),
        ("test_raw_store.py", "stored.content_hash == content_hash(PAYLOAD)"),
        ("test_raw_store.py", "stored.path.read_bytes() == PAYLOAD"),
        ("test_raw_store.py", "to_https(ftp) == https"),
        ("test_raw_store.py", "to_https(https) == https"),
        (
            "test_raw_store.py",
            "verify(stored.content_hash, filename='sites.txt', home=tmp_path) == stored.path",
        ),
        ("test_rebuild.py", "first == second"),
        ("test_rebuild.py", "store.count_edges(conn) == EXPECTED_EDGES"),
        ("test_rebuild.py", "store.count_nodes(conn) == EXPECTED_NODES"),
        ("test_rebuild.py", "store.ids_by_label(conn) == before"),
        (
            "test_rebuild.py",
            "store.ids_by_label(open_graph(home)) == {'Project': [pinned['project']], 'Experiment': [pinned['experiment']], 'Dataset': [pinned['dataset']], 'Analysis': [pinned['analysis']], 'Sample': sorted(pinned['samples'].values())}",
        ),
        ("test_resolve_nodes.py", "set(protein) == {NODE_TYPE_KEY, 'id', 'accession'}"),
        ("test_schema.py", "accession == accession.upper()"),
        ("test_schema.py", "built == schema.table_names()"),
        ("test_schema.py", "code_children == doc_children"),
        ("test_schema.py", "included == {'P0CG48', 'Q15843', 'P05161'}"),
        ("test_schema.py", "len(listed) == len(set(listed))"),
        ("test_schema.py", "named == {e for _, e in pairs}"),
        ("test_schema.py", "prefix == prefix.lower()"),
        ("test_schema.py", "schema.CURATION_BASIS == dict(rows)"),
        ("test_schema.py", "schema.CURIE_PREFIXES == _curie_prefixes()"),
        ("test_schema.py", "schema_nodes == ontology_nodes"),
        ("test_schema.py", "schema_rels == ontology_rels"),
        ("test_schema.py", "set(authority) & set(composed) == set()"),
        ("test_schema.py", "set(authority) | set(composed) == _reference_node_tables()"),
        ("test_schema.py", "set(listed) == set(nodes)"),
        ("test_schema.py", "set(schema.IDENTITY) == {label for label, *_ in rows}"),
        ("test_schema.py", "set(spec.anchors) == doc_anchors"),
        ("test_schema.py", "set(spec.fields) == doc_fields"),
        ("test_stats.py", "benjamini_hochberg(np.array([0.031]))[0] == pytest.approx(0.031)"),
        (
            "test_stats.py",
            "drawn.mean() == pytest.approx(observed.mean() - 1.8 * observed.std(ddof=1), rel=0.02)",
        ),
        (
            "test_stats.py",
            "drawn.std(ddof=1) == pytest.approx(0.3 * observed.std(ddof=1), rel=0.05)",
        ),
        ("test_stats.py", "got.log2fc[0] == pytest.approx(0.0)"),
        ("test_stats.py", "got.p_value[0] == pytest.approx(1.0)"),
        ("test_stats.py", "welch_t(a, b).log2fc[0] == pytest.approx(2.0)"),
        ("test_store.py", "store.ids_by_label(conn) == {'Protein': sorted([MX1, USP18])}"),
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

_DRIFT_EVIDENCE = Evidence(
    target="bzk/drift.py",
    old="    return found\n",
    new="    return found[:-1]\n",
    green_scope=("-q",),
    red_scope=None,
)

INSTANCES: frozenset[tuple[str, str, Evidence]] = frozenset(
    {
        (
            "test_drift.py",
            "receipt.sequences_checked == len(drift.archived_sequences(home))",
            _DRIFT_EVIDENCE,
        ),
        (
            "test_drift.py",
            "receipt.archive_digest == drift.archive_digest(drift.archived_sequences(home))",
            _DRIFT_EVIDENCE,
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
    """
    root = TESTS.parent
    ignore = shutil.ignore_patterns(".venv", ".git", ".pytest_cache", ".ruff_cache")
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


def test_the_match_set_has_not_grown_unreviewed() -> None:
    """A new assertion of the shape must be classified before it lands.

    Pinning the *set* rather than a count is what makes this bite: a count is satisfied by deleting
    one substantive assertion and adding one tautological assertion in the same module.
    """
    found, modules, asserts = sweep()
    # Denominated at the exact current surface, 2026-08-08. It read `asserts >= 600` against
    # 633, which tolerated deleting a twentieth of the suite's assertions — the case its own
    # failure message names. A legitimate reduction lowers these numbers in the same change,
    # the same discipline PINNED already carries; additions never trip it.
    assert modules >= 19 and asserts >= 632, (
        f"the surface shrank to {modules} modules / {asserts} asserts — a sweep over a surface "
        "that quietly stopped covering the tests is the defect this module exists to catch"
    )
    new = found - PINNED
    gone = PINNED - found
    assert not new, (
        f"{len(new)} assertion(s) match the tautology sweep and are not classified: {sorted(new)}. "
        "Read each one: if its call is the expression that produced the other side it is an "
        "instance and belongs in INSTANCES with its mutation evidence; otherwise add it to PINNED."
    )
    assert not gone, (
        f"{len(gone)} pinned assertion(s) no longer exist: {sorted(gone)}. Remove them from PINNED "
        "(and from INSTANCES) in the same change that removed the assertion, so the pin cannot "
        "drift into describing a suite that no longer exists."
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
    """An instance must not leave the record by being deleted or edited without a decision."""
    found, _, _ = sweep()
    for module, source, _evidence in sorted(INSTANCES, key=lambda i: (i[0], i[1])):
        assert (module, source) in found, (
            f"{module} no longer contains {source!r}. If it was fixed, remove it from INSTANCES "
            "and say so where the trigger is recorded (HANDOFF.md §8)."
        )
        assert (module, source) in PINNED, f"{module}: {source!r} is an instance but not pinned"


def test_every_classified_instance_re_runs_its_recorded_evidence() -> None:
    """The evidence is re-run, not read. See `Evidence` for the measured cost of doing so.

    Until 2026-08-08 the third element of each `INSTANCES` row was prose bound to `_evidence` and
    never read, while two artefacts said the evidence was carried and a third said the trigger was
    "enforced rather than remembered". Changing `drift.run` to compute `sequences_checked`
    independently would have left the prose intact, the module green, and the record describing a
    mutation result that no longer held.
    """
    seen: set[Evidence] = set()
    for module, source, evidence in sorted(INSTANCES, key=lambda i: (i[0], i[1])):
        if evidence in seen:  # two `test_drift.py` rows share one mutation
            continue
        seen.add(evidence)
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
