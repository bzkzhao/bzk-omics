"""Every exported query, over a graph with the DDL and nothing in it.

**The class, and why it is a behavioural check rather than a syntactic one.** `gene_symbols` went
to its `MATCH` without consulting the `Gene` table, so over a graph built with no `raw/` every
symbol came back `UNATTRIBUTABLE` — asserting that the graph held what would answer the question,
of a graph holding nothing. It was found by driving the app in the cold-clone rehearsal, not by a
test, because both fixtures the read layer had were populated. `graph.py` records why the fix is
`Gene`-specific rather than *is the graph empty*: the condition being reported is about the table
that query reads. A syntactic guard — *every query consults a table before it matches* — was
rejected on that ground and the rejection stands. What generalises is the **behaviour**: run every
export against a DDL-only graph and require the answer it is supposed to give.

**The coverage problem is nine exports, not one, and a check that classified only the four
`Absence`-carrying ones would pass by omission for five.** So the classification below is keyed off
`bzk.query.__all__` itself and is self-checking in three directions:

* **An added export fails.** `EXPECTED` and the exported query callables are compared as sets, so a
  tenth function is unclassified and named in the failure rather than skipped.
* **A changed signature fails.** The recorded arguments are bound through `inspect.signature`
  before the call, so a recipe that has gone stale raises `TypeError` naming the function instead
  of silently testing a different call.
* **A misclassified group fails.** `group` is checked against what the return *actually is* —
  whether an `Absence` is reachable inside it — rather than taken as a declaration. Writing
  `container` on a query that carries an absence, or the reverse, fails.

The one escape hatch is `NOT_A_QUERY`, and it is loud by construction: a callable added to `__all__`
is forced into `EXPECTED` or into that set, and both are decisions someone has to write down.

**No export is silent over an empty graph today** — measured before this module was written, and it
corrects the premise it was written from. `gene_absence_census` does not return an empty dict: it
keys **all four** of §4's states at zero, the *an omitted key and a zero read differently*
convention `test_query.py` already asserts, and `unprovenanced` keys all three of §7's entity
labels at `(0, 0)`. So this freezes a property that holds rather than repairing one that does not,
which is the whole reason it can be written as an equality against measured values.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import kuzu
import pytest

import bzk.query as q
from bzk.ontology import schema
from bzk.query import Absence

#: Exported callables that are not queries. `connect` opens the database and answers nothing, so it
#: has no empty-graph behaviour to classify. Named rather than pattern-matched: the point of this
#: module is that leaving an export out is a written decision, and a pattern would make it an
#: accident of naming.
NOT_A_QUERY = frozenset({"connect"})


@dataclass(frozen=True)
class Expectation:
    """What one export must return over a DDL-only graph, and which group it belongs to.

    `args` are the arguments after `conn`. Ids that name nothing are deliberate — a DDL-only graph
    has no real id to pass, and *asked about something absent, over a store with nothing in it* is
    the state the class is about.

    `project` normalises a return that carries free text. Only `gene_symbols` needs it: its `detail`
    is prose written for a reader and pinning it here would make this module the second home for a
    sentence. What is pinned instead is the machine-readable part, and `detail` is asserted
    non-empty rather than verbatim.
    """

    group: str  # 'absence' | 'optional' | 'container'
    args: tuple[Any, ...]
    expected: Any
    why: str
    project: Callable[[Any], Any] | None = field(default=None, compare=False)


def _symbol_answers(answers: Any) -> Any:
    return [
        (a.symbol, a.present, a.absence, a.gene_id, a.protein_ids, bool(a.detail)) for a in answers
    ]


def _imputation(state: Any) -> Any:
    return (state.analysis_id, state.methods, state.seeds, state.absence, state.satisfies_i15)


def _refusal(answer: Any) -> Any:
    return (answer.dataset_id, answer.reasons, answer.absence, bool(answer.detail))


#: One row per exported query. Every value was measured against a DDL-only graph before being
#: written here; none was predicted from the source.
EXPECTED: dict[str, Expectation] = {
    "differential_table": Expectation(
        group="absence",
        args=("bzk:nosuch",),
        expected=([], Absence.NOT_STORED),
        why="no DifferentialResult exists, which is a claim about the store rather than about the "
        "analysis — NONE_FOUND is what an analysis that produced none returns",
    ),
    "imputation_state": Expectation(
        group="absence",
        args=("bzk:nosuch",),
        expected=("bzk:nosuch", (), (), Absence.NOT_STORED, False),
        why="I15 is unsatisfied rather than satisfied-vacuously: no Imputation was found, so the "
        "analysis cannot be said to have declared one",
        project=_imputation,
    ),
    "refusals": Expectation(
        group="absence",
        args=(),
        expected=(None, (), Absence.NOT_RETAINED, True),
        why="a refusal is not an entity and is never written, so an empty graph changes nothing — "
        "this is the one value that is the same over every graph",
        project=_refusal,
    ),
    "gene_symbols": Expectation(
        group="absence",
        args=(["MX1", "NOSUCHGENE"],),
        expected=[
            ("MX1", False, Absence.NOT_STORED, None, (), True),
            ("NOSUCHGENE", False, Absence.NOT_STORED, None, (), True),
        ],
        why="the branch the cold-clone rehearsal found: an empty Gene table is NOT_STORED, never "
        "UNATTRIBUTABLE, which would claim the graph holds what answers the question",
        project=_symbol_answers,
    ),
    "site_keying": Expectation(
        group="optional",
        args=("uniprot:P20591#sv4#K4#unimod:121",),
        expected=None,
        why="the site is absent, and None is the whole return type's absence — a SiteKeying with "
        "null fields would assert a site that is not there",
    ),
    "site_ids": Expectation(
        group="container",
        args=(),
        expected=[],
        why="an enumeration, where empty has one reading: the population is empty. There is no "
        "second state for an absence value to distinguish it from",
    ),
    "analysis_ids": Expectation(
        group="container",
        args=(),
        expected=[],
        why="an enumeration, as site_ids",
    ),
    "unprovenanced": Expectation(
        group="container",
        args=(),
        expected={"Dataset": (0, 0), "SiteObservation": (0, 0), "DifferentialResult": (0, 0)},
        why="every §7 entity label is keyed at (0, 0) rather than omitted, so 'none unprovenanced' "
        "and 'none of this label exists' are both readable and the denominator says which",
    ),
    "gene_absence_census": Expectation(
        group="container",
        args=(),
        expected={"unresolved": 0, "no_cross_reference": 0, "not_captured": 0, "encoded": 0},
        why="all four §4 states keyed at zero, the omitted-key-versus-zero convention test_query "
        "already asserts on a populated graph. An all-zero census says the Protein table is empty",
    ),
}


def _exported_queries() -> set[str]:
    """The names in `__all__` this module is responsible for: callables that are not types."""
    return {
        name
        for name in q.__all__
        if callable(getattr(q, name))
        and not inspect.isclass(getattr(q, name))
        and name not in NOT_A_QUERY
    }


def _absences(value: Any, depth: int = 0) -> list[Absence]:
    """Every `Absence` reachable in a return value, so `group` is decided rather than declared.

    Walks tuples, lists and dataclass fields to a bounded depth — every return shape in this layer
    is one of those, and a bound keeps a cyclic structure from hanging the suite rather than
    failing it.
    """
    if depth > 4:
        return []
    if isinstance(value, Absence):
        return [value]
    if isinstance(value, list | tuple):
        return [a for v in value for a in _absences(v, depth + 1)]
    if hasattr(value, "__dataclass_fields__"):
        return [
            a
            for name in value.__dataclass_fields__
            for a in _absences(getattr(value, name), depth + 1)
        ]
    return []


def _is_vacant(value: Any) -> bool:
    """True when a container says *nothing here* without needing an absence value.

    Empty, or every number in it zero. `{'Dataset': (0, 0)}` is vacant; `[]` is vacant; a list of
    rows is not. This is what the `container` group has to mean if it is to be a claim rather than
    a label — otherwise `container` would be satisfied by a query returning real content.
    """
    if isinstance(value, list | tuple | set):
        return all(_is_vacant(v) for v in value)
    if isinstance(value, dict):
        return all(_is_vacant(v) for v in value.values())
    if isinstance(value, int | float) and not isinstance(value, bool):
        return value == 0
    return False


@pytest.fixture
def ddl_only(tmp_path: Path) -> kuzu.Connection:
    """A graph with §4–§7's DDL applied and not one node.

    An established instrument rather than new ground: `ROADMAP.md` § *Measured findings* carries a
    registered prediction and a recorded outcome against a DDL-only graph from the cold-clone
    rehearsal, and `test_query.py` builds one for the `Gene` branch.
    """
    conn = kuzu.Connection(kuzu.Database(str(tmp_path / "ddl.kuzu")))
    for ddl in schema.ddl_statements():
        conn.execute(ddl)
    return conn


def test_every_exported_query_is_classified() -> None:
    """The check that makes the rest cover what it claims. Without it, adding an export adds a
    silent exemption — the failure mode the four-of-nine version of this module would have had."""
    assert set(EXPECTED) == _exported_queries()


def test_the_classification_recipes_still_bind() -> None:
    """A per-function argument list is a second enumeration; this is what makes it rot loudly.

    Set equality above catches a function added or removed. It cannot catch a **signature change**
    on one that stayed — `differential_table(conn, analysis_id, *, grain)` would leave `EXPECTED`
    intact and testing a call that no longer exists. Binding first turns that into a `TypeError`
    naming the function.
    """
    for name, expectation in sorted(EXPECTED.items()):
        signature = inspect.signature(getattr(q, name))
        signature.bind("<conn>", *expectation.args)


def test_every_exported_query_answers_an_empty_graph_as_classified(
    ddl_only: kuzu.Connection,
) -> None:
    """The behavioural half: nine calls, nine measured answers."""
    for name, expectation in sorted(EXPECTED.items()):
        function = getattr(q, name)
        inspect.signature(function).bind(ddl_only, *expectation.args)
        result = function(ddl_only, *expectation.args)
        observed = expectation.project(result) if expectation.project else result
        assert observed == expectation.expected, f"{name}: {expectation.why}"


def test_each_group_matches_what_the_return_actually_is(ddl_only: kuzu.Connection) -> None:
    """`group` is checked, not believed.

    A guard satisfied by something other than the field it names has passed three times on this
    project. Here the thing named is *this export carries an absence*, and the way to satisfy it
    without the property holding is to write the group down and never look. So the group is decided
    from the return: an `Absence` is reachable inside it, or it is `None`, or it is a vacant
    container carrying no `Absence` at all.
    """
    for name, expectation in sorted(EXPECTED.items()):
        result = getattr(q, name)(ddl_only, *expectation.args)
        found = _absences(result)
        if expectation.group == "absence":
            assert found, f"{name} is classified 'absence' and returned none over an empty graph"
        elif expectation.group == "optional":
            assert result is None, f"{name} is classified 'optional' and returned {result!r}"
            assert not found
        elif expectation.group == "container":
            assert not found, f"{name} is classified 'container' but carries {found}"
            assert _is_vacant(result), f"{name} is classified 'container' and returned content"
        else:
            raise AssertionError(f"{name}: unknown group {expectation.group!r}")


def test_the_three_groups_are_the_whole_classification() -> None:
    """A fourth group would be a state nobody decided what to do about — the shape §4's
    `gene_absence` column exists to prevent one level down."""
    assert {e.group for e in EXPECTED.values()} == {"absence", "optional", "container"}
    assert all(e.why.strip() for e in EXPECTED.values())
