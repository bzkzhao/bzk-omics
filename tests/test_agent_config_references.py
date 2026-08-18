"""Every pointer from `.claude/` into this repository resolves.

**The class this closes.** The vendored skills under `.claude/skills/` and the config under
`.claude/config/` are written against this repository's normative documents. Twenty-six of those
files name a normative document; eight of them additionally *restated* something one owned — a
pinned constant's name, a record count, an enumeration of invariants, the check-command list — and
those eight were reduced to pointers rather than guarded as copies, because a pointer carries no
independent claim about content and so cannot disagree with its source.

That reduction closes the *content* half and opens a narrower one: **a pointer can still name a
document that no longer exists, or a section whose heading has been renamed.** Nothing in the suite
reads `.claude/`, so such a reference goes stale in silence — the same failure mode the
restatements had, one level in. This module asserts the property the reduction leaves outstanding:
not that the copies agree, but that the pointers land.

**Why this is a test and not a note in `HANDOFF.md` §8.** It is mechanically decidable. A section
pointer is `` `DOC.md` § ``  followed by text; whether it resolves is answered by reading `DOC.md`'s
own headings, which is the same shape as `tests/test_decision_index.py` comparing a record against
its referent. `CLAUDE.md`'s point 3 is explicit that a machine-checkable class gets the assertion
rather than the prose.

**The target document is the authority, not a list kept here.** `_headings` reads the real headings
out of each document at run time and a pointer must begin with one of them. Nothing enumerates the
sections, so a renamed heading fails here rather than being reconciled against a second copy —
writing that list into this module would recreate the defect the module exists to catch.

**Every parsed set carries a pinned count**, following `tests/test_decision_index.py`. A regex that
stops matching compares equal to anything else that matched nothing, and this module's whole job is
comparing extracted references against a referent — so an extractor that silently matched zero
would report clean while checking nothing. The counts move in the same commit as a legitimate
addition.

**Two reference kinds are checked, and a third deliberately is not.** Section pointers and code
paths are checked. Bare document mentions are not: `.claude/skills/setup-matt-pocock-skills/SKILL.md`
tabulates upstream defaults (`CONTEXT.md`, `docs/adr/`) precisely *because* they do not exist here,
so asserting that every backticked `.md` resolves would fire at the one file whose job is to say
they don't. That is the shape `tests/test_command_blocks.py` warns about — a guard that fires at
the wrong thing — and the narrower property is the one that is true.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENT_DIR = ROOT / ".claude"

#: The counts at the commit that introduced this module, pinned so an extractor that stops
#: matching fails loudly instead of checking an empty set. A legitimate addition moves these in
#: the same commit — the discipline `tests/test_decision_index.py` carries, for the same reason.
EXPECTED_AGENT_DOCS = 47
EXPECTED_SECTION_POINTERS = 44
EXPECTED_CODE_PATHS = 12

#: `` `DOC.md` `` immediately followed by a section mark. The document name is captured so the
#: pointer is resolved against the document it actually names, never against a default.
#:
#: Matched against whitespace-normalised text, because a pointer wraps: `.claude/skills/tdd/tests.md`
#: carries `` `CLAUDE.md` § Working `` with `style` on the next line. The first draft of this module
#: bounded the tail at the newline and reported that *correct* pointer as dangling — the shape
#: `tests/test_command_blocks.py` records as a guard firing at the wrong thing. The prose was left
#: alone and the extractor fixed, which is the right way round: reflowing a paragraph to satisfy a
#: regex is the document serving the test.
#:
#: The tail is captured through a **lookahead** so a match consumes nothing beyond the section
#: mark. A consuming tail swallows any second pointer inside its window, which both hides those
#: pointers from the check and makes the pinned count depend on line lengths — a mutation that
#: renamed a code path moved the section count by one, which is how this was found.
_SECTION_REF = re.compile(r"`([A-Za-z_]+\.md)`\s*§\s*(?=(.{0,60}))")

#: A repository-relative path into code. `<` excludes the placeholder forms the skills use for
#: paths a run creates (`.scratch/<slug>/…`), which are templates rather than references.
_CODE_PATH = re.compile(r"`((?:tests|bzk)/[A-Za-z0-9_/]+\.py)`")

_HEADING = re.compile(r"^#{2,4}\s+(.+?)\s*$", re.MULTILINE)


def _agent_docs() -> list[Path]:
    """Every Markdown file under `.claude/`, sorted."""
    return sorted(AGENT_DIR.rglob("*.md"))


def _flat(doc: Path) -> str:
    """One document as a single whitespace-normalised line, so a wrapped pointer still reads."""
    return re.sub(r"\s+", " ", doc.read_text(encoding="utf-8"))


def _headings(doc: Path) -> list[str]:
    """The `##`-and-deeper heading texts of one document, longest first.

    Longest first matters: `ONTOLOGY.md` has both `5. Evidence nodes` and `5.3 Curation as an
    activity`, and a pointer to `§5.3` must match the subsection rather than stopping at `5.`.
    """
    return sorted(_HEADING.findall(doc.read_text(encoding="utf-8")), key=len, reverse=True)


def _resolves(tail: str, headings: list[str]) -> bool:
    """Does the text after a `§` begin with one of the target document's headings?

    Numeric pointers are written `§8`, `§5.3`, `§4–§7` while the headings read `8. Invariants` and
    `5.3 Curation as an activity`, so a numeric tail matches on the number alone. Named pointers
    (`§ Working style`) must match the heading text.
    """
    tail = tail.lstrip()
    number = re.match(r"(\d+(?:\.\d+)?)", tail)
    if number:
        want = number.group(1)
        return any(re.match(rf"{re.escape(want)}[.\s]", h) or h == want for h in headings)
    return any(tail.startswith(h) for h in headings)


def test_agent_doc_count() -> None:
    """The corpus this module reads is non-empty and its size is pinned."""
    docs = _agent_docs()
    assert len(docs) == EXPECTED_AGENT_DOCS, (
        f".claude/ holds {len(docs)} Markdown files, not {EXPECTED_AGENT_DOCS} — move the pin in "
        "the same commit as the addition, so this module is known to have read them all"
    )


def test_section_pointers_resolve() -> None:
    """Every `` `DOC.md` § … `` pointer in `.claude/` names a section that document really has."""
    found = 0
    for doc in _agent_docs():
        for name, tail in _SECTION_REF.findall(_flat(doc)):
            found += 1
            target = ROOT / name
            assert target.exists(), (
                f"{doc.relative_to(ROOT)}: points into `{name}`, which does not exist"
            )
            assert _resolves(tail, _headings(target)), (
                f"{doc.relative_to(ROOT)}: `{name}` § {tail[:40]!r} does not resolve to any "
                f"heading in {name} — the section was renamed or the pointer was wrong when written"
            )
    assert found == EXPECTED_SECTION_POINTERS, (
        f"matched {found} section pointers, not {EXPECTED_SECTION_POINTERS} — a count that moves "
        "without the pin means the extractor stopped seeing a form it used to see"
    )


def test_code_paths_resolve() -> None:
    """Every `tests/…py` or `bzk/…py` path named in `.claude/` exists."""
    found = 0
    for doc in _agent_docs():
        for path in _CODE_PATH.findall(_flat(doc)):
            found += 1
            assert (ROOT / path).exists(), (
                f"{doc.relative_to(ROOT)}: names `{path}`, which does not exist — a module was "
                "renamed and the pointer was left behind"
            )
    assert found == EXPECTED_CODE_PATHS, (
        f"matched {found} code paths, not {EXPECTED_CODE_PATHS} — move the pin in the same commit "
        "as the addition"
    )
