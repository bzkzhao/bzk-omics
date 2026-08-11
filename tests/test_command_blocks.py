"""Every command block in the documents produces what it uses.

**The class this closes, and it is narrow on purpose.** A fenced block that spends a shell variable
nothing in the block sets is not a command anyone can run — the reader has to supply the missing
half, and *what they supply is the defect*. `HANDOFF.md`'s command block carried
`--watch-pid $!` with no `&` above it for a day: `$!` expands to the pid of the last backgrounded
job and the block backgrounds nothing, so the pid came from nowhere. What a reader improvises there
is the backgrounding **and** the stopping, and improvising the stopping is where `pkill -f` gets
written — the one failure `bzk/fetch_progress.py` exists to make unnecessary, and which recurred
twice on 2026-08-10 after that module had landed.

**This is mechanically decidable, which is why it is a test and not a note.** A shell variable use
is `$NAME` / `${NAME}` / `$!`; a producer is an assignment, a `for`, a `read`, or — for `$!` alone —
a background operator earlier in the block. Nothing here parses shell; it is a lexical check over
text that is already fenced, and the one thing it must get right is that `cmd & NAME=$!` **is** a
producer for both. The first draft of this check did not treat `&` as an assignment separator and
reported the *corrected* block as broken, which is the shape of a guard that fires at the wrong
thing.

**What defeats a stronger version, stated so nobody reaches for it.** *Is this command runnable* is
not decidable from the text — a block may name a path that does not exist, a flag that was renamed,
or a working directory it never states (`OPERATIONS.md` §4.1's `streamlit run bzk/ui/app.py` only
works from the repository root, and that condition lives in the prose beside it, not in the block).
So this asserts the one property that *is* textual: a block does not spend what it never earns.

`tests/test_decision_index.py` is the precedent — a test that reads documents — and its lesson is
carried here: a classifier that quietly stops matching compares equal to anything else that matched
nothing, so the blocks this covers are named individually rather than counted.
"""

from __future__ import annotations

import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = sorted(ROOT.glob("*.md")) + sorted(ROOT.glob("decisions/*.md"))

_FENCE = re.compile(r"^```(\w*)\s*$")
_USE = re.compile(r"\$(\{)?([A-Za-z_][A-Za-z0-9_]*|[!?@#*0-9])(?(1)\})")
_SET = re.compile(r"(?:^|\||&&|&|;|\bexport\s+|\bfor\s+|\bread\s+)\s*([A-Za-z_][A-Za-z0-9_]*)=")
_FOR = re.compile(r"\bfor\s+([A-Za-z_][A-Za-z0-9_]*)\s+in\b")
#: `&&` is not a background operator and neither is a redirection (`2>&1`, `>&2`, `<&0`).
_NOT_BACKGROUND = re.compile(r"&&|\d*>&\d*|<&\d*")

#: A line that opens with one of these *may* be a command. The verb alone is not enough: the
#: `kuzu`/`duckdb`/`polars` listing in `HANDOFF.md` §2 has lines reading `pytest` and `streamlit`,
#: which are package names. A command also carries an argument or a path, and `_is_command` below
#: requires one — the first draft of this module did not, and classified that listing as commands.
_COMMAND = re.compile(
    r"^\s*(uv|python|\.venv/|streamlit|git|curl|pytest|ruff|mypy|du|time|pkill|wait|cd|ls|"
    r"export|kill|nohup|bash|sh)\b"
)
_COMMENT = re.compile(r"\s+#.*$")


def _blocks(path: Path) -> list[tuple[int, list[str]]]:
    """`(first line number, body lines)` for every fenced block in one document."""
    out: list[tuple[int, list[str]]] = []
    inside, start = False, 0
    buf: list[str] = []
    for i, line in enumerate(path.read_text().splitlines(), 1):
        if _FENCE.match(line) and not inside:
            inside, start, buf = True, i, []
        elif line.strip() == "```" and inside:
            out.append((start, buf))
            inside = False
        elif inside:
            buf.append(line)
    return out


def _is_command(line: str) -> bool:
    bare = _COMMENT.sub("", line).strip()
    if not bare or bare.startswith("#") or not _COMMAND.match(bare):
        return False
    return " " in bare or "/" in bare


def _commands(body: list[str]) -> list[str]:
    return [_COMMENT.sub("", ln).strip() for ln in body if _is_command(ln)]


def _is_command_block(body: list[str]) -> bool:
    return bool(_commands(body))


def _backgrounds(line: str) -> bool:
    return "&" in _NOT_BACKGROUND.sub("", line)


def unsatisfied(body: list[str]) -> list[tuple[str, str]]:
    """`(variable, line)` for every variable the block spends and never earns."""
    out: list[tuple[str, str]] = []
    assigned: set[str] = set()
    forked = False
    for line in body:
        # A line's own assignments count for its own uses: `cmd & NAME=$!` earns and spends at once.
        assigned |= set(_SET.findall(line)) | set(_FOR.findall(line))
        forked = forked or _backgrounds(line)
        for _, name in _USE.findall(line):
            if (not forked) if name == "!" else (name not in assigned):
                out.append((name, line.strip()))
    return out


def command_blocks() -> list[tuple[str, int, list[str]]]:
    return [
        (path.name, start, body)
        for path in DOCS
        for start, body in _blocks(path)
        if _is_command_block(body)
    ]


def test_every_command_block_produces_what_it_uses() -> None:
    gaps = [
        (name, start, bad) for name, start, body in command_blocks() if (bad := unsatisfied(body))
    ]
    assert gaps == [], (
        f"{len(gaps)} command block(s) spend a shell variable nothing in the block sets: {gaps}. "
        "A reader who meets one improvises the missing half, and what they improvise is the defect"
    )


def test_the_check_fires_on_the_defect_it_was_written_for() -> None:
    """Non-vacuity, and the block below is the one that was committed rather than an analogue.

    Without this, a classifier that stopped recognising command blocks would pass the assertion
    above by covering nothing — the omission shape `tests/test_decision_index.py` records, where a
    regex matching zero rows compared equal to a table of 24.
    """
    broken = [
        ".venv/bin/python -m bzk.rebuild                         # graph from the four I9 inputs",
        ".venv/bin/python -m bzk.fetch_progress --watch-pid $!   # beside a cold rebuild",
    ]
    assert _is_command_block(broken)
    assert [var for var, _ in unsatisfied(broken)] == ["!"]

    fixed = [
        ".venv/bin/python -m bzk.rebuild & REBUILD=$!",
        ".venv/bin/python -m bzk.fetch_progress --watch-pid $REBUILD --interval 60",
        "wait $REBUILD",
    ]
    assert _is_command_block(fixed)
    assert unsatisfied(fixed) == []

    # `&&` is not a background operator, so it does not earn `$!`. Asserted because treating it as
    # one would make the broken block above pass anywhere a `&&` appeared earlier.
    assert not _backgrounds("ruff check bzk tests && mypy bzk tests")
    assert not _backgrounds("python -m bzk.rebuild > log 2>&1")
    assert _backgrounds("python -m bzk.rebuild &")


def test_the_poller_invocation_matches_the_module_that_documents_it() -> None:
    """`HANDOFF.md` and `bzk/fetch_progress.py` now carry the same three lines — a mirror, and every
    mirror between two sources in this repository is guarded rather than trusted."""
    import bzk.fetch_progress as fp

    lines = textwrap.dedent(fp.__doc__ or "").splitlines()
    opener = next(i for i, ln in enumerate(lines) if ln.rstrip().endswith("cold rebuild::"))
    module_form: list[str] = []
    for line in lines[opener + 1 :]:  # the reST literal block: indented, ends at the first outdent
        if not line.strip():
            if module_form:
                break
            continue
        if not line.startswith("    "):
            break
        module_form.append(line.strip())

    handoff = [
        [ln.strip() for ln in body]
        for _, body in _blocks(ROOT / "HANDOFF.md")
        if any("--watch-pid" in ln for ln in body)
    ]
    assert len(module_form) == 3, f"the module's usage block is {module_form}"
    assert len(handoff) == 1, "HANDOFF.md must carry the poller invocation exactly once"
    assert handoff[0] == module_form


_STREAMLIT = (
    "streamlit run bzk/ui/app.py --server.address localhost --browser.gatherUsageStats false"
)


def test_the_known_command_blocks_are_all_covered() -> None:
    """Named rather than counted, so a classifier that drops one fails here instead of passing the
    main assertion by covering less."""
    found = {(name, cmd) for name, _, body in command_blocks() for cmd in _commands(body)}
    for expected in (
        ("HANDOFF.md", "git clone <your repo>"),
        ("HANDOFF.md", "uv sync --frozen"),
        ("HANDOFF.md", ".venv/bin/python -m bzk.rebuild & REBUILD=$!"),
        ("HANDOFF.md", "wait $REBUILD"),
        ("OPERATIONS.md", "uv sync --frozen"),
        ("OPERATIONS.md", ".venv/bin/python -m bzk.drift"),
        ("OPERATIONS.md", _STREAMLIT),
    ):
        assert expected in found, f"{expected} is no longer recognised as a command"

    # The dependency listing in `HANDOFF.md` §2 has lines reading `pytest` and `streamlit`. It is
    # package names, and classifying it as commands is what the argument-or-path rule prevents.
    assert ("HANDOFF.md", "pytest") not in found
    assert ("HANDOFF.md", "streamlit") not in found
