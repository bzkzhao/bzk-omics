"""`ReplayReport` ↔ `RebuildReport` — the mirror between the two report dataclasses.

**The class this closes.** `rebuild()` returns a `RebuildReport` built from a `ReplayReport`, and
until `bzk/rebuild.py` was changed it did so with one `field=replay.field` line per field. That is
a mirror between two sources with nothing holding them equal, and it failed exactly as such a
mirror fails: `protein_observations` was added to `ReplayReport` and not to `RebuildReport`, and
nothing said so — no import error, no failing test, no runtime error. The omission surfaced only
because a rebuild over the real store printed the count in the replay summary and not on the
`done:` line, which is luck rather than a guard.

**Two things now hold it, at two different moments.** `rebuild()` splats
`fields(ReplayReport)` into the constructor, so a field on one class and not the other raises
`TypeError` on every rebuild — loud, but only once something rebuilds. This module asserts the same
property against the *declarations*, so it fails before any rebuild runs and names which field and
which direction.

**Why the exclusion set exists and why it is empty.** Every `ReplayReport` field is carried today,
and the honest way to say "all of them" is a named, empty set rather than a comprehension that
silently tolerates a gap. A future field that genuinely should not reach `RebuildReport` goes in
`NOT_CARRIED` *with its reason*, in the same commit, and the reader then sees an exception that was
decided rather than one that was never noticed. This is the shape `CLAUDE.md` § Single source of
truth asks for: the pair is guarded, and a deliberate divergence is a written one.

**Types are compared, not only names.** A field carried across under the same name but a different
annotation is the same defect wearing a disguise: `site_observations: int` against
`site_observations: int | None` would pass a name-only check and change what a caller may assume.
`fields()` is read rather than `__annotations__` so inherited and defaulted fields read the same
way, and the string form is compared because `from __future__ import annotations` is on in
`bzk/rebuild.py` — every annotation there is already a string, and resolving them would add an
evaluation step this assertion does not need.
"""

from __future__ import annotations

from dataclasses import fields

from bzk.rebuild import RebuildReport, ReplayReport

#: `ReplayReport` fields deliberately not carried into `RebuildReport`, each with its reason.
#: **Empty today, and that is the claim** — not an oversight. See the module docstring.
NOT_CARRIED: dict[str, str] = {}


def _annotations(cls: type) -> dict[str, str]:
    return {f.name: str(f.type) for f in fields(cls)}


def test_every_replay_field_is_carried_into_the_rebuild_report() -> None:
    """The direction the defect actually travelled: a field added to `ReplayReport` alone."""
    replay = set(_annotations(ReplayReport))
    rebuild = set(_annotations(RebuildReport))
    missing = replay - rebuild - set(NOT_CARRIED)

    assert not missing, (
        f"{sorted(missing)} is/are declared on ReplayReport and not on RebuildReport, so a "
        "rebuild would drop the figure. Add the field to RebuildReport, or add it to NOT_CARRIED "
        "with the reason it should not reach a caller"
    )


def test_the_shared_fields_agree_on_their_types() -> None:
    """A field carried across under a different annotation is the same defect in disguise."""
    replay = _annotations(ReplayReport)
    rebuild = _annotations(RebuildReport)
    disagreeing = {
        name: (replay[name], rebuild[name])
        for name in set(replay) & set(rebuild)
        if replay[name] != rebuild[name]
    }

    assert not disagreeing, (
        f"{disagreeing} — each entry is (ReplayReport, RebuildReport). A shared field must carry "
        "the same annotation on both, or a caller reading the rebuild's report may assume "
        "something the replay never promised"
    )


def test_the_rebuild_report_adds_exactly_the_fields_it_declares() -> None:
    """The other direction. A field added to `RebuildReport` alone is never populated by
    `rebuild()` — the constructor splats the replay's fields and passes `tables_created` — so it
    would sit at its default for ever while reading as a figure the rebuild measured."""
    extra = set(_annotations(RebuildReport)) - set(_annotations(ReplayReport))

    # A literal display rather than a named constant, so the claim reads where it is made:
    # `tables_created` is the only field `RebuildReport` adds, being the DDL step's own figure,
    # and `replay_ingestion` neither creates tables nor has a field for them. Re-deriving it would
    # assert nothing, so the literal is the pin and moving it is a deliberate edit. The comparison
    # is classified in `tests/test_tautology_sweep.py`'s `PINNED` — it is matched by that module's
    # Pass D, which a literal on one side does not exclude.
    assert extra == {"tables_created"}, (
        f"RebuildReport declares {sorted(extra)} beyond ReplayReport, not ['tables_created']. "
        "A field here that rebuild() does not pass stays at its default and reports a measurement "
        "that was never taken; move the pin in the same commit as a deliberate addition"
    )
