"""Guards for the refusal-membership fixture (`tests/fixtures/pxd018299_refusals.json`).

`bzk/sources/pxd018299_refusals.py` writes it. Until it existed, an ingestion kept three integers —
`refused_residue_mismatch`, `refused_unresolved_protein`, `refused_no_razor_pick` on
`maxquant_sites.SiteIngestReport` — and threw the membership away: the `Refusal` objects reach
`rebuild.replay_ingestion`, are logged as a length, and are dropped with the report. A refusal is
not an entity, so `query.refusals` answers `NOT_RETAINED` and nothing can be read back. Three
integers cannot tell fifteen drifted sites from a different fifteen, which is the `HANDOFF.md` §6
failure one grain along.

**What is deliberately not asserted here: the total, the breakdown, and which accessions.** The
recorded numbers are 27 / 15 / 11 / 1 today and pinning them from this module would pin them from
prose — the only place those figures exist right now is `ROADMAP.md`, `adapters/base.py`'s docstring
and this sentence, none of which measured anything. Membership is being recorded for the first
time; a list written today would be written from the documents it is supposed to check.
`tests/test_pxd018299_baseline.py` states the same rule for its own candidate sites.

What is pinned instead is **internal agreement and vocabulary**: the counts follow from the rows
recorded under them, every row carries all three fields the adapter gives it, and every reason slug
is one the adapter actually constructs — read out of `bzk/adapters/maxquant_sites.py` by parsing
it, never restated as literals here. A slug renamed in the adapter and not regenerated into the
fixture then fails, which a list of strings copied into this module could not do.

Every check but the last is offline, the way `tests/test_pxd018299_platform_targets.py` reads its
own fixture: it is a committed artefact and needs neither `raw/` nor the graph. The last one is the
anti-fabrication guard — that each recorded `row` is a real `id` in the deposit's bytes — and that
one needs the deposit, so it skips in its absence exactly as the re-derivation in
`tests/test_pxd018299_baseline.py` does. `raw/` does not survive a container (`HANDOFF.md` §3), and
a test that went red on every fresh session would teach sessions to ignore it.
"""

from __future__ import annotations

import ast
import collections
import json
from pathlib import Path
from typing import Any, cast

import pytest

from bzk.adapters import maxquant, maxquant_sites
from bzk.adapters.base import Refusal
from bzk.sources.pride import PXD018299_SITES
from bzk.sources.pxd018299_baseline import deposit_path

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "pxd018299_refusals.json"

#: The three fields `adapters.base.Refusal` carries, read off the dataclass rather than listed, so
#: a field added there is a field this module starts requiring rather than one it silently ignores.
REFUSAL_FIELDS = tuple(Refusal.__dataclass_fields__)


def _fixture() -> dict[str, Any]:
    return cast("dict[str, Any]", json.loads(FIXTURE.read_text()))


def _refusals() -> list[dict[str, Any]]:
    return cast("list[dict[str, Any]]", _fixture()["refusals"])


def _counts() -> dict[str, int]:
    return cast("dict[str, int]", _fixture()["counts"])


def constructed_slugs() -> set[str]:
    """Every `reason` the site adapter constructs a `Refusal` with, read out of its source.

    Parsed rather than imported because the slugs are not named anywhere — they are string literals
    at the three `Refusal(...)` call sites in `maxquant_sites._site`, and the report's
    `refused_*` field names are a second spelling of them rather than their home. Restating them
    here as literals would make this check agree with this module instead of with the adapter,
    which is the shape `CLAUDE.md` point 2 names: a guard that cannot fail on the change it exists
    to catch. `tests/test_analysis_record.py` and `tests/test_curation_loader.py` read their
    subjects the same way.

    Deliberately the *site* adapter alone. `maxquant_protein_groups.py` constructs
    `empty_protein_group`, which is a protein-grain kind; a row in this fixture carrying it would
    mean the fixture was generated through the wrong adapter and must fail rather than pass.
    """
    source = Path(maxquant_sites.__file__).read_text(encoding="utf-8")
    return {
        keyword.value.value
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "Refusal"
        for keyword in node.keywords
        if keyword.arg == "reason"
        and isinstance(keyword.value, ast.Constant)
        and isinstance(keyword.value.value, str)
    }


def test_the_slug_extractor_finds_the_adapters_reasons() -> None:
    """The non-vacuity guard for `constructed_slugs`, and it has to come first.

    Every check below that uses it is a subset assertion, and a subset of the empty set is refused
    only while the fixture has rows — so an extractor that silently stopped matching (the call
    renamed, `reason` passed positionally) would take the vocabulary check down with it and leave
    no failure behind. That is the vacuous-pass shape `CLAUDE.md` point 2 records twice over.
    """
    assert constructed_slugs(), (
        f"no `Refusal(reason=...)` literal was found in {Path(maxquant_sites.__file__).name}; "
        "the extractor has stopped matching and every vocabulary check below is now vacuous"
    )


def test_counts_are_a_recount_of_the_recorded_refusals() -> None:
    """The counts against the rows under them — the one thing a summary can get wrong silently.

    The fixture's `counts` and its `refusals` are written from the same list by
    `refusal_fixture`, so agreement is expected; what this catches is the file being edited,
    truncated, or regenerated in halves, and a `counts` restated from `ROADMAP.md` or from
    `SiteIngestReport` rather than computed — which is the entire reason the module computes it.
    """
    recounted = dict(sorted(collections.Counter(r["reason"] for r in _refusals()).items()))
    assert _counts() == recounted, (
        "`counts` does not match a recount of `refusals` by reason — the two halves of the file "
        "disagree, so one of them was not produced by the run that wrote the other"
    )


def test_the_total_refused_is_the_sum_of_the_counts() -> None:
    """A second arithmetic tie, and not the same one: the recount above compares *per reason*.

    A refusal carrying a reason absent from `counts` fails the recount; a `counts` carrying a
    reason with no rows fails it too. What this adds is the length — a file whose `refusals` list
    was truncated at a reason boundary could satisfy neither, but one truncated after `counts` was
    computed over the full list fails here first and says so in the clearer terms.
    """
    assert len(_refusals()) == sum(_counts().values()), (
        f"{len(_refusals())} refusal(s) recorded against counts summing to "
        f"{sum(_counts().values())}"
    )


def test_every_refusal_carries_every_field_non_empty() -> None:
    """`row`, `reason` and `detail`, all three present and none blank, on every row.

    Fields read off `Refusal` rather than named, so widening the dataclass makes this fail until
    the fixture is regenerated — which is the correct outcome, since a fixture missing a field the
    adapter now records is a record of a run that no longer happens.
    """
    incomplete = [
        r for r in _refusals() if any(not str(r.get(field, "")).strip() for field in REFUSAL_FIELDS)
    ]
    assert not incomplete, (
        f"{len(incomplete)} refusal(s) are missing one of {list(REFUSAL_FIELDS)} or carry it "
        f"blank: {incomplete[:5]}"
    )


def test_every_recorded_reason_is_a_slug_the_adapter_constructs() -> None:
    """The vocabulary, against the adapter's source rather than against a list written here.

    A subset rather than an equality in both directions: a reason the adapter can construct and
    this deposit never triggers is not a defect — `no_razor_pick` fires on one row of 2,056 and a
    deposit without that row would carry none — while a reason in the file that the adapter cannot
    construct means the file came from somewhere other than a parse.
    """
    recorded = {r["reason"] for r in _refusals()}
    assert recorded <= constructed_slugs(), (
        f"{sorted(recorded - constructed_slugs())} appear(s) in the fixture and is constructed "
        f"nowhere in {Path(maxquant_sites.__file__).name}; the file did not come from this adapter"
    )


def test_the_counts_vocabulary_is_the_same_vocabulary() -> None:
    """`counts` keys too, not just the rows — the summary can name a kind the adapter cannot."""
    assert set(_counts()) <= constructed_slugs(), (
        f"{sorted(set(_counts()) - constructed_slugs())} is counted in the fixture and is "
        "constructed nowhere in the adapter"
    )


def test_the_fixture_names_the_deposit_it_was_generated_from() -> None:
    """Provenance against `pride.PXD018299_SITES`, which is where the digest lives.

    Without this the file is a list of row numbers against no particular bytes, and row `1319`
    means nothing outside the file that contains it. Pinned against the descriptor rather than
    against a literal digest for the reason `tests/test_curation_content_hash.py` gives: the digest
    has one home.
    """
    fixture = _fixture()
    assert fixture["content_hash"] == PXD018299_SITES.expected_content_hash, (
        f"the fixture records {fixture['content_hash']!r}, which is not the deposit "
        f"{PXD018299_SITES.filename} that pride.py holds a digest for"
    )
    assert fixture["dataset"] == PXD018299_SITES.accession
    assert fixture["file"] == PXD018299_SITES.filename


def test_the_note_says_what_is_not_retained() -> None:
    """The note is the file's only defence against being read as a graph export.

    Checked for the two words that carry it — the state `query.refusals` answers, and the
    regeneration command — rather than for its prose, so rewording it does not fail here while
    dropping the claim does.
    """
    note = str(_fixture()["note"])
    assert "NOT_RETAINED" in note
    assert "python -m bzk.sources.pxd018299_refusals" in note


# --------------------------------------------------------------------------------------------
# Anti-fabrication: needs the deposit in raw/
# --------------------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def deposit_row_ids() -> set[str]:
    """Every `id` in the deposit's bytes. Skips where `raw/` has not been fetched.

    The same gate `tests/test_pxd018299_baseline.py` puts on its re-derivation, and the same
    helper: `deposit_path` re-hashes the file it finds, so this cannot pass against different
    bytes than the fixture's `content_hash` names. No resolver and no network — the row ids are
    read straight out of the table, which is all this check needs.
    """
    try:
        path = deposit_path()
    except (FileNotFoundError, ValueError) as exc:
        pytest.skip(f"deposit not in raw/ — run `python -m bzk.sources.pride` first ({exc})")
    table = maxquant.read_table(path)
    id_column = table.header.index("id")
    return {row[id_column] for row in table.rows}


def test_every_recorded_row_is_a_row_in_the_deposit(deposit_row_ids: set[str]) -> None:
    """The one check here that reaches outside the fixture, and the reason it is worth having.

    Everything above is internal agreement: a hand-written file with a consistent `counts` would
    pass all of it. This one cannot be satisfied by writing plausible rows, because the `id`s have
    to be `id`s of these bytes. It is not a proof the fixture came from a parse — a fabricator with
    the file could copy real ids — but it is the check that fails on a fixture invented from the
    documents, which is the way this file would actually go wrong.
    """
    unknown = [r["row"] for r in _refusals() if r["row"] not in deposit_row_ids]
    assert not unknown, (
        f"{len(unknown)} recorded row id(s) are not `id`s in {PXD018299_SITES.filename}: "
        f"{unknown[:10]}"
    )
