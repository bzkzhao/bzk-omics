"""The protein-grain group measurement (`bzk/sources/protein_groups.py`).

The numbers this produces are a **measured finding** in `ROADMAP.md`, and an ADR is written against
them, so a silent change in the measurement code would move a recorded finding without anyone
noticing. `tests/fixtures/pxd018299_protein_groups.json` pins what the code produced on 2026-08-07.

Same shape as the 12-of-14 baseline fixture, and the same caveat: this checks **change, not
correctness**, since the fixture came out of the code it guards. A failure means the measurement
moved or an artefact was revised — both need explaining, neither is fixed by regenerating.

**On mutation-testing these guards** (`CLAUDE.md` point 2): the offline half is deliberately not
mutation-tested, and that is a decision rather than an omission. Its subject is a fixture of derived
numbers, and the assertions are arithmetic over them — `multi_fraction == multi / rows`,
`isoform_only + distinct_gene == multi`. Mutating the fixture to break one of those demonstrates
only that `==` works. What *is* mutation-tested is the code the numbers come from: dropping the
spill-line guard in `bzk/adapters/maxquant.py` fails `test_re_measuring_reproduces_the_pinned_
numbers` here, because the measurement then reads six spill lines as protein groups. That is the
failure worth catching, and it is caught.

The three inputs live in `raw/`, which does not survive a container (`HANDOFF.md` §3), so the
re-measurement skips when they are absent. The fixture's own shape is checked either way, because a
guard whose subject matter is a fetched file must still say something on a cold container.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import pytest

from bzk.sources.protein_groups import (
    SUPP_DATA_2,
    SUPP_DATA_3,
    _base,
    measure_all,
    summarise,
)

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "pxd018299_protein_groups.json"


def _pinned() -> list[dict[str, Any]]:
    loaded = json.loads(FIXTURE.read_text())["measurements"]
    return cast("list[dict[str, Any]]", loaded)


# ── Offline ─────────────────────────────────────────────────────────────────────────────────────


def test_the_fixture_covers_both_columns_of_all_three_artefacts() -> None:
    """Six rows: three artefacts x `Majority protein IDs` and `Protein IDs`.

    Both columns matter because which one an adapter reads decides how often it refuses, so a
    fixture that quietly lost one would understate the finding.
    """
    pinned = _pinned()
    assert len(pinned) == 6
    assert len({m["artefact"] for m in pinned}) == 3
    for measurement in pinned:
        assert "Majority protein IDs" in measurement["column"] or (
            measurement["column"].endswith("Protein IDs")
        )


def test_every_pinned_measurement_is_internally_consistent() -> None:
    """The derived fields must follow from the counts, or a hand-edit has drifted from the data."""
    for m in _pinned():
        assert 0 < m["multi_accession"] <= m["rows"]
        assert m["multi_fraction"] == pytest.approx(m["multi_accession"] / m["rows"], abs=5e-5)
        assert m["isoform_only"] + m["distinct_gene_multi"] == m["multi_accession"]
        assert m["max_size"] >= m["median_size"] >= 1


def test_the_finding_is_that_most_rows_are_groups() -> None:
    """The headline, asserted so it cannot erode quietly.

    §6.3 settled the site grain at 82% multi-mapping. If this ever drops below half, the premise
    `bzk/adapters/perseus.py` refuses on — and the ADR written against it — needs revisiting rather
    than the threshold being lowered.
    """
    majority = [m for m in _pinned() if m["column"].endswith("Majority protein IDs")]
    assert len(majority) == 3
    assert all(m["multi_fraction"] > 0.5 for m in majority), majority


def test_isoform_only_groups_are_the_minority() -> None:
    """The split that decides whether a fallback exists.

    An isoform-only group names one gene with the isoform unresolved; a distinct-gene group names
    different proteins and has no fallback at all. If most multi-accession rows were isoform-only,
    "resolve to the gene" would be a cheap answer — they are not, so it is not.
    """
    for m in _pinned():
        # `>=` not `>`: Supplementary Data 2 splits exactly 9/9 on `Majority protein IDs`, its
        # smallest artefact at 25 rows. Writing `>` and exempting that one number would be fitting
        # the assertion to the data rather than stating the claim.
        assert m["distinct_gene_multi"] >= m["isoform_only"], m


def test_base_accession_strips_only_the_isoform_suffix() -> None:
    assert _base("P09914-2") == "P09914"
    assert _base("P09914") == "P09914"
    assert _base("A0A087WXQ8") == "A0A087WXQ8"


def test_summarise_counts_a_single_accession_row_as_unambiguous() -> None:
    stats = summarise(
        "synthetic", "col", [["P20591"], ["P19525", "O43593"], ["P09914", "P09914-2"]]
    )
    assert stats.rows == 3
    assert stats.multi_accession == 2
    assert stats.isoform_only == 1  # P09914 / P09914-2 is one gene
    assert stats.distinct_gene_multi == 1  # P19525 / O43593 is two


# ── Re-measurement: needs the three artefacts in raw/ ───────────────────────────────────────────


def test_re_measuring_reproduces_the_pinned_numbers() -> None:
    """Determinism and drift, against the artefacts themselves.

    Skips rather than fails on a cold container: `raw/` does not persist, and a test that went red
    every fresh session is one sessions learn to ignore (`HANDOFF.md` §3).
    """
    try:
        measured = measure_all()
    except (FileNotFoundError, ValueError) as exc:
        pytest.skip(f"artefacts not in raw/ — run `python -m bzk.sources.protein_groups` ({exc})")
    from dataclasses import asdict

    assert [asdict(m) for m in measured] == _pinned()


def test_the_supplementary_digests_are_well_formed() -> None:
    """A truncated paste would compare equal to nothing and the fetch would raise on every run."""
    import re

    for supp in (SUPP_DATA_2, SUPP_DATA_3):
        assert re.fullmatch(r"sha256:[0-9a-f]{64}", supp.expected_content_hash), supp.filename
        assert supp.url.startswith("https://static-content.springer.com/")
