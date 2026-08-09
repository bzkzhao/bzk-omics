"""`bzk/ui/` — the absence mapping, and what the three panels actually render.

**Why this module has tests at all.** `app.py` holds no derivation: every value on screen is a
field of a record `bzk/query/` returned. But it holds one real decision — the mapping from each
`Absence` to what a reader sees — and that decision is the whole point of the third panel. A test
that only imported the module would be the shape this project has been caught by twice: *a guard
that cannot see the objects it governs*. So the app is run headlessly through
`streamlit.testing.v1.AppTest` against a graph written by the real write path, and the assertions
are on rendered text.

**What that costs, stated rather than absorbed.** `AppTest` executes the script in-process, so a
Streamlit version bump can break these without breaking the app and the reverse; and asserting on
substrings of rendered markdown is a weaker contract than asserting a return value. Both accepted —
the alternative is asserting nothing about the only decision the module makes.

**These do not skip.** The fixture graph is built in `tmp_path`, so the UI is covered on a fresh
container where `~/.bzk-omics` does not exist and the ten graph-dependent tests skip.
"""

from __future__ import annotations

import ast
from pathlib import Path

import kuzu
import pytest
from streamlit.testing.v1 import AppTest

from bzk.ontology import schema, store
from bzk.ontology.invariants import NODE_TYPE_KEY
from bzk.query import Absence
from bzk.ui import absence as ui_absence
from bzk.ui import app as ui_app

APP = Path(ui_app.__file__)
MX1 = "uniprot:P20591"
IFIT1_2 = "uniprot:P09914-2"
SEQ = f"{MX1}#sv4"
SITE = f"{MX1}#sv4#K48#unimod:121"
GENE = "hgnc:HGNC:7532"
ANALYSIS = "bzk:analysis1"
DATASET = "bzk:dataset1"
OBS = "bzk:obs1"


def _n(label: str, node_id: str, **props: object) -> dict[str, object]:
    return {NODE_TYPE_KEY: label, "id": node_id, **props}


def _e(rel: str, frm: str, to: str) -> dict[str, object]:
    return {"type": rel, "from": frm, "to": to}


@pytest.fixture(scope="module")
def graph(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A graph with one promoted site, one gene, and no results — the real graph's shape.

    Written through `store.write_change_set`, which validates first, for `test_query.py`'s reason:
    a renderer proved correct against rows no producer makes is correct about nothing. `Analysis`
    carries no `Imputation` and there is no `DifferentialResult`, so panel three renders the two
    `NOT_STORED` absences the live graph actually shows.
    """
    path = tmp_path_factory.mktemp("ui") / "g.kuzu"
    conn = kuzu.Connection(kuzu.Database(str(path)))
    for ddl in schema.ddl_statements():
        conn.execute(ddl)
    nodes: list[dict[str, object]] = [
        _n("Gene", GENE, symbol="MX1"),
        _n("Protein", MX1, accession="P20591", gene_absence=None),
        _n("Protein", IFIT1_2, accession="P09914-2", gene_absence="unresolved"),
        _n("ProteinSequence", SEQ, sequence_version=4, sequence="M" * 47 + "K" + "MM"),
        _n("ModificationSite", SITE, residue="K", position=48, modification_type="unimod:121"),
        _n(
            "SiteObservation",
            OBS,
            peptide_sequence="LLQFIDKELVR",
            candidate_proteins=[MX1, IFIT1_2],
            keying_basis="reviewed_preferred",
            displaced_protein=IFIT1_2,
            is_decoy=False,
        ),
        _n(
            "ModifierAssignment",
            "bzk:ma1",
            candidate_modifiers=["uniprot:P05161"],
            basis="inferred_default",
            confidence="ambiguous",
            retracted_at=None,
        ),
        _n("Dataset", DATASET, source="local", search_engine="maxquant"),
        _n(
            "Analysis",
            ANALYSIS,
            kind="processing",
            quantity="intensity_multiplicity_summed",
            localization_threshold=0.75,
            filters_applied=["localization_prob>=0.75"],
            test="welch_t",
            fdr_method="benjamini_hochberg",
            parameters_observed=False,
        ),
    ]
    edges = [
        _e("ENCODES", GENE, MX1),
        _e("HAS_SEQUENCE", MX1, SEQ),
        _e("SITE_ON", SITE, SEQ),
        _e("MEASURED_AT", OBS, SITE),
        _e("REPORTS_SITE", DATASET, OBS),
        _e("USED", ANALYSIS, DATASET),
        _e("ASSIGNMENT_FOR", "bzk:ma1", OBS),
    ]
    store.write_change_set(conn, nodes, edges)
    return path


def _run(graph: Path, monkeypatch: pytest.MonkeyPatch) -> AppTest:
    """Point the app at a fixture graph through the one surface it exposes.

    `streamlit run` takes no arguments of its own, so `app.graph_path` reads `$BZK_GRAPH`. Setting
    it here rather than reaching into the module is the point: the tests drive the app through the
    same surface a user would.
    """
    monkeypatch.setenv(ui_app.GRAPH_ENV, str(graph))
    return AppTest.from_file(str(APP), default_timeout=120)


def _elements(at: AppTest) -> list[str]:
    """Every rendered element, separately — so a claim about *one* element can be made."""
    out: list[str] = []
    for block in (at.title, at.header, at.subheader, at.markdown, at.caption, at.warning, at.error):
        out += [str(e.value) for e in block]
    return out


def _text(at: AppTest) -> str:
    """Everything the app rendered, as one string. Substring assertions run against this."""
    return "\n".join(_elements(at))


# ── The one decision: four absences, four renderings ────────────────────────────────────────────


def test_every_absence_has_a_rendering_and_no_two_are_the_same() -> None:
    """Exhaustive **and** distinct. Neither half is safe alone.

    A mapping can be complete and still say the same thing twice, which is the blank-grid failure
    with extra steps. Adding a fifth `Absence` fails the first assertion; copy-pasting a rendering
    fails the second.
    """
    assert set(ui_absence.RENDERING) == set(Absence)
    headlines = [r.headline for r in ui_absence.RENDERING.values()]
    assert len(set(headlines)) == len(Absence) == 4
    details = [r.detail for r in ui_absence.RENDERING.values()]
    assert len(set(details)) == 4
    # Each rendering names the sibling it must not be confused with, which is why they are four
    # strings rather than one: the distinction is the content.
    for rendering in ui_absence.RENDERING.values():
        assert "not" in rendering.detail.lower()


def test_no_absence_renders_as_nothing() -> None:
    for member in Absence:
        rendering = ui_absence.describe(member)
        assert rendering is not None
        assert rendering.headline.strip() and rendering.detail.strip()
    # `None` in, `None` out — a caller with a real answer must show the answer, and a "no absence"
    # string here would let a panel print an absence notice above a populated table.
    assert ui_absence.describe(None) is None


# ── What the panels render ──────────────────────────────────────────────────────────────────────


def test_the_app_runs_against_a_real_graph_without_raising(
    graph: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    at = _run(graph, monkeypatch).run()
    assert at.exception == [], [str(e.value) for e in at.exception]


def test_panel_one_shows_the_basis_and_what_it_displaced(
    graph: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    text = _text(_run(graph, monkeypatch).run())
    # **Asserted against the composed line, not the bare id.** The first version asserted
    # `IFIT1_2 in text`, and replacing the displaced accession with the word "(promoted)" left it
    # green — because the same accession is in the candidate list two lines below. The assertion
    # was satisfied by a different element than the one it names, which is the failure this suite
    # has now been caught by three times.
    assert "`keying_basis`: **reviewed_preferred**" in text
    assert f"`displaced_protein`: **{IFIT1_2}**" in text
    assert "I17 promoted this site" in text
    assert "sv4" in text and "K48" in text
    # I14's display half: the candidate set beside the number, never narrowed by the renderer.
    assert "Candidate set — 2 protein(s)" in text
    assert f"- `{MX1}`" in text and f"- `{IFIT1_2}`" in text


def test_panel_two_shows_twelve_present_and_does_not_join_the_rename(
    graph: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The fixture holds only `MX1`, so the counted figure here is 1 of 14, not 12.

    **That is deliberate.** The 12 is a property of the real graph and is asserted in
    `test_query_real_graph.py`, where a divergence is a finding about the data. What this asserts
    is what the *panel* does with whatever it is given: names what it counted, and does not join a
    renamed symbol to its current one.
    """
    text = _text(_run(graph, monkeypatch).run())
    assert "of 14 requested symbols are present" in text
    assert "Identifiability, not recovery" in text
    assert "DDX58" in text
    assert "does not join a renamed symbol" in text
    for forbidden in ("DDX58 → RIGI", "DDX58 (RIGI)", "RIGI (DDX58)", "formerly DDX58"):
        assert forbidden not in text, f"the UI resolved the rename: {forbidden!r}"


def test_entering_both_names_of_a_renamed_gene_shows_both_and_joins_neither(
    graph: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The rename, driven through the widget a caller would use.

    `RIGI` is deliberately **not** in the default list: that list is the fourteen published
    targets, a documented set, and adding a fifteenth symbol chosen to make a point would be the
    UI suggesting the comparison — which is the join by another route. So the comparison is the
    caller's to make, and this test makes it the way a caller would, then asserts the panel renders
    both sides and links neither.
    """
    at = _run(graph, monkeypatch).run()
    at.text_area[0].set_value("MX1, NOSUCHGENE").run()
    text = _text(at)
    assert "**1 of 2 requested symbols are present**" in text
    assert "NOSUCHGENE" in text
    assert ui_absence.RENDERING[Absence.UNATTRIBUTABLE].headline in text
    # Present and absent side by side, and no edge drawn between them. Asserted two ways, because
    # the first version banned bare arrows across the whole page and tripped on panel one's
    # provenance path — `Analysis -USED-> Dataset` — which is a legitimate arrow about something
    # else. The claim is narrower than "no arrows": **no rendered element mentions both symbols**,
    # which is what a join would have to look like.
    for element in _elements(at):
        assert not ("MX1" in element and "NOSUCHGENE" in element), (
            f"one element names both symbols, which is the join this panel must not make: "
            f"{element[:120]!r}"
        )
    for forbidden in ("formerly", "renamed to", "same locus as", "aka "):
        assert forbidden not in text, f"the panel implied a join: {forbidden!r}"


def test_panel_three_renders_two_different_nothings_and_names_both(
    graph: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The panel this turn exists for. Two `NOT_STORED` and one `NOT_RETAINED`, told apart.

    The fixture has no `DifferentialResult` and no `Imputation`, which is the real graph's state,
    and refusals are never retained — so all three notices appear at once and a reader must be able
    to tell which is which.
    """
    text = _text(_run(graph, monkeypatch).run())
    assert ui_absence.RENDERING[Absence.NOT_STORED].headline in text
    assert ui_absence.RENDERING[Absence.NOT_RETAINED].headline in text
    assert "not reconstructible from stored content" in text
    assert "an imputation state is a **set**" in text.lower()


def test_an_empty_panel_is_still_on_screen(graph: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # The empty panels stay visible. A renderer that hides a panel until it has rows makes an
    # absence invisible, which is the blank grid by another route.
    text = _text(_run(graph, monkeypatch).run())
    for heading in ("1 · Site provenance", "2 · Gene symbols", "3 · Differential results"):
        assert heading in text


# ── The rules the module claims about itself ────────────────────────────────────────────────────


def test_the_ui_imports_nothing_from_bzk_but_query() -> None:
    """The constraint that makes *"the UI derives nothing"* checkable rather than a habit.

    Asserted on the source of every module in the package, not just `app.py`: a helper importing
    `kuzu` would satisfy a check scoped to the entry point and leak just as far.
    """
    allowed = {"bzk.query", "bzk.ui"}
    for path in sorted(Path(ui_app.__file__).parent.glob("*.py")):
        source = path.read_text()
        # Parsed rather than string-matched: `from bzk import query` and `import bzk.query` are the
        # same import and a substring check gets one of them wrong, which it did on the first run.
        for node in ast.walk(ast.parse(source)):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module] + [f"{node.module}.{a.name}" for a in node.names]
            for name in names:
                assert not name.startswith("kuzu"), f"{path.name} imports {name}"
                if name == "bzk" or name.startswith("bzk."):
                    assert any(
                        name == a or name.startswith(f"{a}.") or a.startswith(f"{name}.")
                        for a in allowed
                    ), f"{path.name} imports {name}, which is not bzk.query or bzk.ui"
        assert "MATCH (" not in source, f"{path.name} contains Cypher"


def test_the_ui_writes_no_file_so_i18s_export_trigger_does_not_fire() -> None:
    """`HANDOFF.md` §8's EX class fires at the first path that can write a file. Not this one.

    §8 I18's own sentence is what settles it — *"queries and views within the local instance are
    unrestricted"* — and a download button is the thing that would change the answer, so its
    absence is asserted rather than assumed.
    """
    for path in sorted(Path(ui_app.__file__).parent.glob("*.py")):
        source = path.read_text()
        for forbidden in ("download_button", "write_text(", "open(", "to_csv", "savefig"):
            assert forbidden not in source, f"{path.name} can write a file: {forbidden!r}"


def test_an_unknown_truth_value_is_never_rendered_as_false_or_blank() -> None:
    # `graph.py` argues a `False` for `substantially_imputed` would assert I15's clause satisfied.
    # A blank cell says the same thing more quietly, so the renderer produces neither.
    rendered = ui_app._unknown("denominator is in quant.duckdb")
    assert rendered.startswith("unknown — ")
    assert rendered.strip() not in {"", "False", "false", "—"}
