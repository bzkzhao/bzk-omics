"""Only `_compose` composes a MaxQuant site column (ADR-0038 D5; prompt 33 §2.1).

ADR-0038 D5 binds a column to a `Sample` in exactly one place per format *"by composing the header
from the sample's mapping key through the adapter's closed family table and requiring exact
membership in the file's header"*. In `bzk/adapters/maxquant_sites.py` that place is `_compose`.
Before prompt 30, `_site` composed `f"{prefix}{label}"` itself — twice, once for the membership
test and once for the read — and nothing noticed: prompt 30's build found it by reading. This
module is the tripwire that was missing.

**The rule, by shape and never by identifier names.** An f-string or `+` that joins a *prefix* to
a label, anywhere outside `_compose`, is refused. Inside `_site` the names are reversed against the
other callers (`column` is the header mapping there, `header` the composed name), so a guard keyed
on names would miss the very function that broke the rule.

- **A prefix** is any value derived from `QUANTITY_COLUMNS` — an expression mentioning it, or a
  name bound from one by assignment, walrus, `for` or comprehension target, or a parameter some
  call site in the module passes one to — or a string constant ending in one of its values
  (`"Intensity "`), which is the family table spelled by hand.
- **The discriminator between a binding and a message** is adjacency. A binding puts a bare prefix
  interpolation (no `!r`, no format spec), or a constant ending in a prefix, *immediately* before
  another bare interpolation — `f"{prefix}{label}"`, `f"Intensity {label}"`, or `prefix + label`.
  A refusal message *names* a prefix and a label — `{QUANTITY_COLUMNS[quantity]!r}` with prose
  around it — and never puts the two flush together: a column name is never a `repr`. A message
  that names a prefix is a candidate and is classified, not excluded by a list; the full candidate
  set is pinned below, printed rather than recited.

**What it does not catch — measured, not assumed (E4; `UNCAUGHT` below).** It sees syntax. A
composition built by `str.join`, `%`, `.format`, or through a helper function's *return value*,
or stored on an attribute, passes: the prefix's taint does not cross a return or an attribute, and
only `f`-strings and `+` are composition shapes here. A local variable does **not** defeat it —
taint follows assignments within a function. It is a tripwire for the shape the defect took and its
obvious neighbours, not a proof that no column is composed elsewhere.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from bzk.adapters.maxquant_sites import QUANTITY_COLUMNS

MODULE = Path(__file__).resolve().parent.parent / "bzk" / "adapters" / "maxquant_sites.py"
PREFIXES = tuple(QUANTITY_COLUMNS.values())
ALLOWED = "_compose"


def _mentions(node: ast.AST, tainted: set[str]) -> bool:
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and (n.id == "QUANTITY_COLUMNS" or n.id in tainted):
            return True
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value.endswith(PREFIXES):
            return True
    return False


def _names(target: ast.AST) -> set[str]:
    return {n.id for n in ast.walk(target) if isinstance(n, ast.Name)}


def _taint(tree: ast.Module) -> dict[str, set[str]]:
    """Each function's prefix-derived names, to a fixpoint across the module's call sites."""
    functions = {
        f.name: f for f in ast.walk(tree) if isinstance(f, ast.FunctionDef | ast.AsyncFunctionDef)
    }
    tainted: dict[str, set[str]] = {name: set() for name in functions}
    changed = True
    while changed:
        changed = False
        for name, func in functions.items():
            mine = tainted[name]
            before = len(mine)
            for node in ast.walk(func):
                if isinstance(node, ast.Assign | ast.AnnAssign | ast.AugAssign) and node.value:
                    if _mentions(node.value, mine):
                        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                        for t in targets:
                            mine |= _names(t)
                elif isinstance(node, ast.NamedExpr) and _mentions(node.value, mine):
                    mine |= _names(node.target)
                elif isinstance(node, ast.For | ast.AsyncFor | ast.comprehension):
                    if _mentions(node.iter, mine):
                        mine |= _names(node.target)
                elif isinstance(node, ast.Call):
                    callee_name = (
                        node.func.id
                        if isinstance(node.func, ast.Name)
                        else node.func.attr
                        if isinstance(node.func, ast.Attribute)
                        else None
                    )
                    callee = functions.get(callee_name or "")
                    if callee is None:
                        continue
                    params = [a.arg for a in callee.args.args]
                    if isinstance(node.func, ast.Attribute) and params[:1] in (["self"], ["cls"]):
                        params = params[1:]
                    hit = {
                        params[i]
                        for i, arg in enumerate(node.args)
                        if i < len(params) and _mentions(arg, mine)
                    }
                    hit |= {kw.arg for kw in node.keywords if kw.arg and _mentions(kw.value, mine)}
                    if not hit <= tainted[callee.name]:
                        tainted[callee.name] |= hit
                        changed = True
            if len(mine) != before:
                changed = True
    return tainted


def _bare(part: ast.AST) -> bool:
    return isinstance(part, ast.FormattedValue) and part.conversion == -1 and not part.format_spec


def _is_binding(node: ast.JoinedStr | ast.BinOp, tainted: set[str]) -> bool:
    if isinstance(node, ast.BinOp):
        right_is_text = isinstance(node.right, ast.Constant) and isinstance(node.right.value, str)
        return _mentions(node.left, tainted) and not right_is_text
    for part, after in zip(node.values, node.values[1:], strict=False):
        is_prefix = (
            isinstance(part, ast.Constant)
            and isinstance(part.value, str)
            and part.value.endswith(PREFIXES)
        ) or (_bare(part) and _mentions(part.value, tainted))  # type: ignore[attr-defined]
        if is_prefix and _bare(after):
            return True
    return False


def candidates(source: str) -> list[tuple[str, str, str]]:
    """Every f-string or outermost `+` that touches a prefix, as `(function, kind, source)`, where
    kind is `binding` or `message`. The printed match set — what the rule reaches."""
    tree = ast.parse(source)
    tainted = _taint(tree)
    parent: dict[int, ast.AST] = {}
    owner: dict[int, str] = {}

    def descend(node: ast.AST, function: str) -> None:
        for child in ast.iter_child_nodes(node):
            parent[id(child)] = node
            inner = (
                child.name if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef) else None
            )
            owner[id(child)] = inner or function
            descend(child, inner or function)

    descend(tree, "<module>")
    found: list[tuple[str, str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp):
            outer = parent.get(id(node))
            if not isinstance(node.op, ast.Add) or (
                isinstance(outer, ast.BinOp) and isinstance(outer.op, ast.Add)
            ):
                continue
        elif not isinstance(node, ast.JoinedStr):
            continue
        function = owner.get(id(node), "<module>")
        mine = tainted.get(function, set())
        if not _mentions(node, mine):
            continue
        kind = "binding" if _is_binding(node, mine) else "message"
        found.append((function, kind, ast.unparse(node)))
    return sorted(found)


def bindings_outside_compose(source: str) -> list[tuple[str, str]]:
    return [(f, src) for f, kind, src in candidates(source) if kind == "binding" and f != ALLOWED]


# --------------------------------------------------------------------------------------------
# The module as committed
# --------------------------------------------------------------------------------------------


def test_only_compose_composes_a_site_column() -> None:
    assert bindings_outside_compose(MODULE.read_text(encoding="utf-8")) == []


def test_the_guard_sees_the_composition_it_allows() -> None:
    """A guard that cannot see `_compose`'s own composition could not see a forbidden one."""
    found = candidates(MODULE.read_text(encoding="utf-8"))
    assert [k for f, k, _ in found if f == ALLOWED] == ["binding", "binding"]


RUN_LABEL_MESSAGE = (
    "f'sample mapping key {key!r} names no column this adapter recognises; expected one "
    "of {sorted(QUANTITY_COLUMNS.values())} followed by the run label'"
)
NO_COLUMN_MESSAGE = (
    'f"Sample {sample_id!r} (run label {label!r}, from mapping key {key!r}) has no '
    "{quantity!r} column in the file, whose family prefix is "
    "{QUANTITY_COLUMNS[quantity]!r}; another family's column for the same run does not "
    'stand in for it (ADR-0038 D5)"'
)
UNKNOWN_QUANTITY_MESSAGE = (
    "f'quantity {quantity!r} has no column family in this adapter; expected one of "
    "{sorted(QUANTITY_COLUMNS)}'"
)


def test_the_match_set_is_printed_not_recited() -> None:
    """Everything the rule reaches in the committed module, classified. Three refusal messages name
    `QUANTITY_COLUMNS` and are messages by the adjacency rule; `_sample_columns`' message names no
    prefix and is not reached at all, so it needs no exclusion."""
    assert candidates(MODULE.read_text(encoding="utf-8")) == [
        ("_compose", "binding", "f'{p}{label}'"),
        ("_compose", "binding", "f'{p}{label}'"),
        ("_run_label", "message", RUN_LABEL_MESSAGE),
        ("bind_column", "message", NO_COLUMN_MESSAGE),
        ("bind_column", "message", UNKNOWN_QUANTITY_MESSAGE),
    ]


# --------------------------------------------------------------------------------------------
# What it catches, and what it does not
# --------------------------------------------------------------------------------------------

_HEADER = "QUANTITY_COLUMNS = {}\n"

CAUGHT = {
    "the pre-prompt-30 membership test": (
        "def _site(column, labels):\n"
        "    return [q for label in labels\n"
        "            for q, prefix in sorted(QUANTITY_COLUMNS.items())\n"
        "            if f'{prefix}{label}' in column]\n"
    ),
    "the pre-prompt-30 read": (
        "def _site(column, labels):\n"
        "    return [cell(column, f'{prefix}{label}') for label in labels\n"
        "            for q, prefix in sorted(QUANTITY_COLUMNS.items())]\n"
    ),
    "concatenation": "def f(q, label):\n    return QUANTITY_COLUMNS[q] + label\n",
    "through a local variable": (
        "def f(q, label):\n    p = QUANTITY_COLUMNS[q]\n    return f'{p}{label}'\n"
    ),
    "a hand-spelled prefix": "def f(label):\n    return f'Intensity {label}'\n",
    "a hand-spelled prefix, concatenated": "def f(label):\n    return 'Intensity ' + label\n",
    "through a parameter a call site fills": (
        "def g(p, label):\n    return f'{p}{label}'\n"
        "def f(q, label):\n    return g(QUANTITY_COLUMNS[q], label)\n"
    ),
}

#: E4: compositions this guard does **not** catch, kept as its documented limit rather than widened
#: away. Source strings parsed here, never written into `bzk/adapters/maxquant_sites.py`, which
#: would break the rule this module enforces.
UNCAUGHT = {
    "str.join": "def f(q, label):\n    return ''.join((QUANTITY_COLUMNS[q], label))\n",
    "percent formatting": "def f(q, label):\n    return '%s%s' % (QUANTITY_COLUMNS[q], label)\n",
    "str.format": "def f(q, label):\n    return '{}{}'.format(QUANTITY_COLUMNS[q], label)\n",
    "a helper's return value": (
        "def prefix_of(q):\n    return QUANTITY_COLUMNS[q]\n"
        "def f(q, label):\n    return f'{prefix_of(q)}{label}'\n"
    ),
    "an attribute": (
        "class R:\n    def __init__(self, q):\n        self.p = QUANTITY_COLUMNS[q]\n"
        "    def f(self, label):\n        return f'{self.p}{label}'\n"
    ),
}


@pytest.mark.parametrize("source", list(CAUGHT.values()), ids=list(CAUGHT))
def test_the_guard_catches(source: str) -> None:
    assert len(bindings_outside_compose(_HEADER + source)) == 1


@pytest.mark.parametrize("source", list(UNCAUGHT.values()), ids=list(UNCAUGHT))
def test_the_guard_does_not_catch(source: str) -> None:
    assert bindings_outside_compose(_HEADER + source) == []


def test_a_message_naming_a_prefix_is_not_a_binding() -> None:
    source = _HEADER + (
        "def f(q, label):\n"
        "    raise ValueError(f'run {label!r} has no column {QUANTITY_COLUMNS[q]!r}')\n"
    )
    assert [k for _, k, _ in candidates(source)] == ["message"]
