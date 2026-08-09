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
        ("test_keys.py", "protein == 'uniprot:P20591'", 1),
        ("test_keys.py", "sequence == 'uniprot:P20591#sv4'", 1),
        ("test_keys.py", "site == 'uniprot:P20591#sv4#K48#unimod:121'", 1),
        ("test_maxquant.py", "accessions == ['P20591', 'P19525']", 1),
        ("test_maxquant_sites.py", "set(modifiers) == set(schema.GG_REMNANT_MODIFIERS)", 1),
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
        ("test_protein_groups.py", "[asdict(m) for m in measured] == _pinned()", 1),
        (
            "test_protein_groups.py",
            "m['multi_fraction'] == pytest.approx(m['multi_accession'] / m['rows'], abs=5e-05)",
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
        ("test_resolve_nodes.py", "set(protein) == {NODE_TYPE_KEY, 'id', 'accession'}", 1),
        ("test_schema.py", "accession == accession.upper()", 1),
        ("test_schema.py", "built == schema.table_names()", 1),
        ("test_schema.py", "code_children == doc_children", 1),
        ("test_schema.py", "included == {'P0CG48', 'Q15843', 'P05161'}", 1),
        ("test_schema.py", "len(listed) == len(set(listed))", 1),
        ("test_schema.py", "named == {e for _, e in pairs}", 1),
        ("test_schema.py", "prefix == prefix.lower()", 1),
        ("test_schema.py", "schema.CURATION_BASIS == dict(rows)", 1),
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
    # Denominated at the exact current surface, re-denominated 2026-08-09 (655 -> 660, the five
    # assertions the `hgnc` local-part guard added). It read `asserts >= 600` against 633, which
    # tolerated deleting a twentieth of the suite's assertions — the case its own failure message
    # names. A legitimate reduction lowers these numbers in the same change, the same discipline
    # the multiset carries; additions never trip it, because an added *match* is caught by the
    # multiset rather than by this floor — but leaving the floor behind the surface reintroduces
    # exactly the slack the re-denomination removed, so it moves with every addition too.
    assert modules >= 20 and asserts >= 660, (
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
