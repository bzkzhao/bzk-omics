"""How each `Absence` appears on screen — the one decision `bzk/ui/` actually makes.

Separated from `app.py` so it can be asserted without a Streamlit runtime, and because it is the
only thing in this package that is not layout. `ROADMAP.md` § *Weeks 7–8* requires ambiguity and
correction status visible everywhere a number appears; `bzk/query/` distinguishes four reasons a
query can come back with nothing, and a renderer that draws them as one blank grid discards that
distinction at the last step — the step where a reader actually forms a belief.

**Exhaustive by construction, and asserted so.** `RENDERING` is keyed by every member of
`query.Absence`; `tests/test_ui.py` fails if a member is added without a rendering, and fails again
if two renderings share a headline. Four distinct absences that render as four distinct strings is
the whole contract, and neither half of it is safe alone: a mapping can be complete and still say
the same thing twice.
"""

from __future__ import annotations

from dataclasses import dataclass

from bzk.query import Absence


@dataclass(frozen=True)
class Rendering:
    """What one absence says on screen. `headline` is the claim; `detail` is why it is that claim."""

    headline: str
    detail: str


#: Every `Absence`, and what it must not be confused with. The *must not* clauses are the reason
#: these are four strings and not one: each names the sibling a blank grid would collapse it onto.
RENDERING: dict[Absence, Rendering] = {
    Absence.NONE_FOUND: Rendering(
        headline="Nothing matched — the question was answered",
        detail=(
            "The graph holds this kind of thing and none of it matched. This is a real answer, "
            "not a gap: it is **not** the same as nothing being stored."
        ),
    ),
    Absence.NOT_STORED: Rendering(
        headline="Nothing is stored — the question was not answered",
        detail=(
            "The node type this reads is empty, so no query could have found anything. This is "
            "**not** a finding about the data: it does not mean nothing matched."
        ),
    ),
    Absence.NOT_RETAINED: Rendering(
        headline="Not retained — no query can answer this",
        detail=(
            "The fact exists at ingestion and the graph keeps no record of it, so it is not "
            "recoverable from stored content at all. **Not** the same as there being none."
        ),
    ),
    Absence.UNATTRIBUTABLE: Rendering(
        headline="Present but unattributable — the key given is not enough",
        detail=(
            "The graph holds what would answer this and cannot reach it from the key supplied. "
            "**Not** the same as the answer being absent."
        ),
    ),
}


def describe(absence: Absence | None) -> Rendering | None:
    """The rendering for one absence, or `None` when there is no absence to render.

    `None` in, `None` out — deliberately, rather than a *"no absence"* rendering. A caller with a
    real answer must show the answer; giving it a string here would let a panel display an absence
    notice above a populated table without noticing.
    """
    return None if absence is None else RENDERING[absence]
