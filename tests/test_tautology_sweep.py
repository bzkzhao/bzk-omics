"""A committed sweep for assertions compared against the expression that produced them.

**Why this exists as a test rather than a procedure.** The 2026-08-08 sweep was run by hand, and its
own report said the detector *"will not re-run"*. That is the defect one level out: a class found by
a procedure nobody repeats is a class rediscovered by the next audit. The passes below are the same
syntactic nets, committed, so a new assertion of the shape fails until someone has looked at it.

**What a syntactic net can and cannot do.** It cannot decide whether a call *is* the expression that
produced the other side — that needs the producer's body, and reading it is judgement. So the net
pins its **match set**, not a verdict: every matching assertion in `tests/` must appear in `PINNED`,
and a new one fails this module with instructions to classify it. The four already classified as
instances are listed separately in `INSTANCES`, and each carries its evidence.

**Pinning the match set rather than a count is deliberate.** A count is satisfied by deleting one
substantive assertion and adding one tautological assertion in the same module, which is precisely
the drift this exists to catch.

**This module excludes itself from its own surface**, because its assertions compare a computed
match set against a pinned constant — the shape the net matches — and a module that swept itself
would have to pin its own pin. Stated rather than silently filtered.
"""

from __future__ import annotations

import ast
import pathlib

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


def sweep() -> tuple[set[tuple[str, str]], int, int]:
    """Return `{(module, normalized source)}` plus the module and assert counts of the surface.

    **Pass C** — one side of an `==` contains a call and another side is not a literal display.
    Catches `receipt.archive_digest == drift.archive_digest(archived_sequences(home))`.

    **Pass D** — no call anywhere in the comparison, but one side is a bare name bound earlier in
    the same function from an expression that did contain one. Catches the same shape laundered
    through a local variable, which Pass C cannot see. Pass D found no instances on 2026-08-08, and
    it is committed anyway: a pass that has never fired is the one whose absence goes unnoticed.
    """
    found: set[tuple[str, str]] = set()
    modules = 0
    asserts = 0
    for path in sorted(TESTS.glob("test_*.py")):
        if path.name == SELF:
            continue
        modules += 1
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for func in ast.walk(tree):
            if not isinstance(func, ast.FunctionDef):
                continue
            bound_from_call = {
                name.id
                for st in ast.walk(func)
                if isinstance(st, ast.Assign) and _has_call(st.value)
                for tgt in st.targets
                for name in ast.walk(tgt)
                if isinstance(name, ast.Name)
            }
            for node in ast.walk(func):
                if not isinstance(node, ast.Assert):
                    continue
                asserts += 1
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
                        hit = any(
                            isinstance(s, ast.Name) and s.id in bound_from_call for s in sides
                        ) and bool(non_literal)
                    if hit:
                        found.add((path.name, ast.unparse(cmp_)))
                    break
    return found, modules, asserts


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
INSTANCES: frozenset[tuple[str, str, str]] = frozenset(
    {
        (
            "test_drift.py",
            "receipt.sequences_checked == len(drift.archived_sequences(home))",
            "archived_sequences -> found[:-1]: whole suite green",
        ),
        (
            "test_drift.py",
            "receipt.archive_digest == drift.archive_digest(drift.archived_sequences(home))",
            "archived_sequences -> found[:-1]: whole suite green",
        ),
        (
            "test_perseus.py",
            "dataset['content_hash'] == content_hash(TABLE.read_bytes())",
            "content_hash -> hash(data+X): all 21 perseus tests green, suite red elsewhere",
        ),
        (
            "test_curation_loader.py",
            "{s['id'] for s in mapping.samples} == set(loaded.sample_ids.values())",
            "Sample id minting -> id + 'X': this test green, module red via a sibling",
        ),
    }
)


def test_the_match_set_has_not_grown_unreviewed() -> None:
    """A new assertion of the shape must be classified before it lands.

    Pinning the *set* rather than a count is what makes this bite: a count is satisfied by deleting
    one substantive assertion and adding one tautological assertion in the same module.
    """
    found, modules, asserts = sweep()
    assert modules >= 19 and asserts >= 600, (
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


def test_every_classified_instance_is_still_present() -> None:
    """An instance must not leave the record by being deleted or edited without a decision."""
    found, _, _ = sweep()
    for module, source, _evidence in sorted(INSTANCES):
        assert (module, source) in found, (
            f"{module} no longer contains {source!r}. If it was fixed, remove it from INSTANCES "
            "and say so where the trigger is recorded (HANDOFF.md §8)."
        )
        assert (module, source) in PINNED, f"{module}: {source!r} is an instance but not pinned"
