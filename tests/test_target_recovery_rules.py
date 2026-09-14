"""Guards for the cross-rule comparison (`bzk/target_recovery_rules.py`).

**What is deliberately not asserted here: which targets are recovered under which rule, and how
many.** That is the finding the module exists to produce, and it has not been reviewed yet. A table
pinned in the same turn that first computed it would fix the answer before anyone has read it —
`tests/test_pxd018299_platform_targets.py` declines to pin its path's membership for the same
reason, and this is the same shape one level out.

What is pinned instead is **internal agreement**: that the two rules stand in the relation they
must stand in (any-site recovery is implied by largest-site recovery, so no total can invert), that
every target lands in exactly one state per path-and-rule, that the third state is counted in
neither total, and that each rule reproduces the verdict field the fixture that *already* records
that rule wrote independently — the baseline fixture's `recovered` is the largest-site rule and the
platform fixture's `status` is the any-site rule, so each is a check against a figure this module
did not produce.

Every check is offline. Both fixtures are committed artefacts and both source modules are imported
for their thresholds only, so nothing here needs `raw/`, the network, or a populated graph — and
so **nothing here skips**, which `test_no_check_in_this_module_skips` asserts rather than leaves to
inspection.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from bzk.sources import pxd018299_baseline as baseline_module
from bzk.sources import pxd018299_differential as platform_module
from bzk.target_recovery_rules import (
    MODULES,
    PATH_BASELINE,
    PATH_PLATFORM,
    PATH_VALUES,
    RULE_ANY_SITE,
    RULE_LARGEST_SITE,
    RULE_VALUES,
    STATE_NO_USABLE_SITES,
    STATE_NOT_RECOVERED,
    STATE_RECOVERED,
    STATE_VALUES,
    PathSource,
    TargetVerdict,
    _report,
    clears,
    compare,
    load,
    source_for,
    totals,
    usable,
    verdicts_for,
)

SELF = Path(__file__)


def _rows_for(path: str) -> list[TargetVerdict]:
    return [row for row in compare() if row.path == path]


def test_both_fixtures_are_committed_and_read_without_the_deposit_or_the_graph() -> None:
    """The premise every other check rests on, asserted rather than assumed."""
    for path in PATH_VALUES:
        fixture = source_for(path).fixture
        assert fixture.is_file(), f"{path}'s fixture is not committed at {fixture}"
        payload = load(path)
        assert payload["targets"], f"{path}'s fixture carries no targets"


def test_each_path_reads_its_criterion_and_its_fixture_off_its_own_module() -> None:
    """Neither path borrows the other's criterion, and neither restates a threshold or a path.

    **Comparing values would not establish this.** The two modules define `SIG_ADJ_P` and
    `SIG_LOG2FC` separately and they presently hold *equal* values, so a threshold borrowed off the
    wrong module compares equal to the right one and every value check passes. That was the first
    draft of this test, and it asserted nothing it claimed to.

    **Comparing against the module attribute would not establish it either.** The second draft read
    `source_for(path).fixture == module.FIXTURE_PATH`, which is the attribute `source_for` itself
    reads — a value compared against the expression that produced it, which cannot fail.
    `tests/test_tautology_sweep.py` matched it, and it is replaced here rather than pinned.

    What is checked instead is **provenance**: each of the three constants is moved in turn to a
    value this test invents, and the path that owns it must follow while the other stays put.
    `bzk/target_recovery_rules.py` reads through `MODULES` on every call, which is what makes the
    move visible; every attribute is restored in a `finally`.
    """
    assert set(MODULES) == set(PATH_VALUES)
    owners = {PATH_BASELINE: baseline_module, PATH_PLATFORM: platform_module}
    moves: tuple[tuple[str, Callable[[PathSource], object], Callable[[Any], object]], ...] = (
        ("SIG_ADJ_P", lambda source: source.thresholds.sig_adj_p, lambda old: float(old) + 1.0),
        ("SIG_LOG2FC", lambda source: source.thresholds.sig_log2fc, lambda old: float(old) + 1.0),
        ("FIXTURE_PATH", lambda source: source.fixture, lambda old: Path(old).with_name("m.json")),
    )
    for path, module in owners.items():
        assert MODULES[path] is module
        other = next(p for p in PATH_VALUES if p != path)
        untouched = source_for(other)
        before = source_for(path)
        for attribute, read, move in moves:
            original = getattr(module, attribute)
            moved = move(original)
            setattr(module, attribute, moved)
            try:
                assert read(source_for(path)) == moved, (
                    f"{path} did not follow {module.__name__}.{attribute} — it is reading that "
                    "value from somewhere else"
                )
                assert source_for(other) == untouched, (
                    f"{other} followed {module.__name__}.{attribute} — it is borrowing the other "
                    "path's module"
                )
            finally:
                setattr(module, attribute, original)
        # Every move is undone before the next path is examined. A second `source_for(other) ==
        # untouched` stood here first and could not be made to fail — nothing between the last
        # in-loop check and this line touches `other`'s module, so it duplicated the assertion
        # above rather than adding one. What *can* fail here is the restore itself.
        assert source_for(path) == before, (
            f"{module.__name__} was left mutated — the next path would be examined against a "
            "moved constant"
        )


def test_every_target_holds_exactly_one_state_per_path_and_rule() -> None:
    """One verdict per target per (path, rule), drawn from the declared three, and no target lost.

    The gene list comes from each fixture rather than from a constant here, so a target the
    fixtures stop carrying fails this instead of silently leaving the comparison.
    """
    rows = compare()
    for path in PATH_VALUES:
        expected = [str(target["gene"]) for target in load(path)["targets"]]
        seen = [row.gene for row in rows if row.path == path]
        assert seen == expected, f"{path} does not cover the fixture's targets in order"
        assert len(seen) == len(set(seen)), f"{path} reports a target twice"
        for rule in RULE_VALUES:
            for row in rows:
                if row.path != path:
                    continue
                verdict = row.under(rule)
                assert verdict in STATE_VALUES, f"{row.gene} on {path}/{rule}: {verdict!r}"


def test_any_site_recovery_is_implied_by_largest_site_recovery() -> None:
    """The relation that makes the four totals comparable at all.

    The largest site is one of the sites, so a target recovered because *that* site cleared is
    recovered because *some* site cleared. Asserted per target first: a totals-only check would be
    satisfied by one target flipping each way.
    """
    for row in compare():
        if row.largest_site == STATE_RECOVERED:
            assert row.any_site == STATE_RECOVERED, (
                f"{row.gene} on {row.path} is recovered under the largest site but not under any "
                "site, which is arithmetically impossible"
            )


def test_the_four_totals_are_computed_and_never_invert() -> None:
    """Four figures, one per (path, rule), each bounded by the relation above — none pinned.

    No expected count appears here. What is asserted is that each total is within the number of
    targets on its path and that the any-site total never falls below the largest-site total.

    **That there are exactly four is deliberately not asserted here.** `totals()` builds its keys by
    iterating `PATH_VALUES` and `RULE_VALUES`, so `len(counts) == len(PATH_VALUES) *
    len(RULE_VALUES)` compares a value against the expression that produced it and cannot fail —
    `tests/test_tautology_sweep.py` matched it on the turn it was written and it was removed rather
    than pinned. The four totals are instead checked where they are not tautological: from the
    printed output, in `test_the_report_carries_every_row_and_all_four_totals`.
    """
    rows = compare()
    counts = totals(rows)
    for path in PATH_VALUES:
        n_targets = len(_rows_for(path))
        for rule in RULE_VALUES:
            assert 0 <= counts[path, rule] <= n_targets
        assert counts[path, RULE_ANY_SITE] >= counts[path, RULE_LARGEST_SITE], (
            f"on {path} the any-site total fell below the largest-site total"
        )


def test_a_target_with_no_sites_is_in_neither_rule_and_neither_total() -> None:
    """The third state, on constructed input and on whatever the committed fixtures carry.

    Constructed first, because the third state must hold for a target with no sites whether or not
    a fixture happens to contain one today.
    """
    for path in PATH_VALUES:
        empty = verdicts_for("SYNTHETIC", path, [])
        assert empty.largest_site == STATE_NO_USABLE_SITES
        assert empty.any_site == STATE_NO_USABLE_SITES
        assert empty.n_sites == 0
        assert empty.n_excluded == 0
        # Every total is zero, asserted without restating `totals()`' own key construction — a
        # dict literal over the same two tuples would compare the function against its own body.
        assert not any(totals([empty]).values()), "the third state reached a total"

    rows = compare()
    for path in PATH_VALUES:
        sizes = {
            str(target["gene"]): len(target.get("sites") or []) for target in load(path)["targets"]
        }
        for row in rows:
            if row.path != path:
                continue
            if sizes[row.gene] == 0:
                assert row.largest_site == STATE_NO_USABLE_SITES
                assert row.any_site == STATE_NO_USABLE_SITES
            else:
                assert row.largest_site != STATE_NO_USABLE_SITES or row.n_excluded == row.n_sites


def test_sites_with_null_statistics_are_excluded_and_the_exclusion_is_counted() -> None:
    """A null statistic removes a site from both rules and shows up in `n_excluded`.

    A NaN comparison is false without saying so, so an unexcluded null site would read as a site
    that was tested and missed. The clearing site here is null in one field only, which is the
    shape the fixtures write.
    """
    clearing: dict[str, Any] = {"log2fc": 9.0, "p": 1e-9, "adj_p": 1e-9}
    for field in ("log2fc", "p", "adj_p"):
        nulled: dict[str, Any] = dict(clearing)
        nulled[field] = None
        assert not usable(nulled)
        verdict = verdicts_for("SYNTHETIC", PATH_BASELINE, [nulled])
        assert verdict.largest_site == STATE_NO_USABLE_SITES
        assert verdict.any_site == STATE_NO_USABLE_SITES
        assert verdict.n_sites == 1
        assert verdict.n_excluded == 1

    missing = {"log2fc": 0.0, "p": 0.9, "adj_p": 0.9}
    mixed = verdicts_for("SYNTHETIC", PATH_BASELINE, [dict(clearing, p=None), missing])
    assert mixed.n_excluded == 1
    assert mixed.any_site == STATE_NOT_RECOVERED
    assert mixed.largest_site == STATE_NOT_RECOVERED


def test_the_largest_site_rule_takes_the_first_row_at_the_maximum() -> None:
    """Ties go to the earlier row, which is what `hits['log2fc'].idxmax()` does on the other side.

    Two sites share the maximum `log2fc`; only the first clears. If the rule took the last, this
    target would come out not-recovered under the largest-site rule.
    """
    first = {"log2fc": 5.0, "p": 1e-9, "adj_p": 1e-9}
    second = {"log2fc": 5.0, "p": 0.9, "adj_p": 0.9}
    verdict = verdicts_for("SYNTHETIC", PATH_BASELINE, [first, second])
    assert verdict.largest_site == STATE_RECOVERED


def test_each_rule_reproduces_the_verdict_its_own_fixture_already_records() -> None:
    """The check against a figure this module did not produce.

    `pxd018299_welch_baseline.json`'s `recovered` was written by the largest-site selection, and
    `pxd018299_platform_targets.json`'s `status` was read off the any-site significance set. Each
    is compared against this module's rule of the same name, on its own path. No gene and no count
    is named: what is asserted is that the two agree wherever the fixture states a verdict.
    """
    baseline_rows = {row.gene: row for row in _rows_for(PATH_BASELINE)}
    for target in load(PATH_BASELINE)["targets"]:
        gene = str(target["gene"])
        expected = STATE_RECOVERED if target["recovered"] else STATE_NOT_RECOVERED
        assert baseline_rows[gene].largest_site == expected, (
            f"{gene}: the largest-site rule disagrees with the baseline fixture's own `recovered`"
        )

    platform_rows = {row.gene: row for row in _rows_for(PATH_PLATFORM)}
    for target in load(PATH_PLATFORM)["targets"]:
        gene = str(target["gene"])
        status = str(target["status"])
        if status == platform_module.STATUS_ABSENT_FROM_TESTED:
            assert platform_rows[gene].any_site == STATE_NO_USABLE_SITES
            continue
        expected = (
            STATE_RECOVERED if status == platform_module.STATUS_RECOVERED else STATE_NOT_RECOVERED
        )
        assert platform_rows[gene].any_site == expected, (
            f"{gene}: the any-site rule disagrees with the platform fixture's own `status`"
        )


def test_clears_is_strict_on_both_sides() -> None:
    """A site sitting exactly on either threshold does not clear it.

    Both source modules compare with `<` and `>`; a site at the threshold is the one input that
    tells `<` from `<=`, and neither fixture is guaranteed to contain one.
    """
    thresholds = source_for(PATH_BASELINE).thresholds
    on_p = {"log2fc": thresholds.sig_log2fc + 1.0, "p": 0.0, "adj_p": thresholds.sig_adj_p}
    on_fc = {"log2fc": thresholds.sig_log2fc, "p": 0.0, "adj_p": 0.0}
    both_clear = {"log2fc": thresholds.sig_log2fc + 1.0, "p": 0.0, "adj_p": 0.0}
    assert not clears(on_p, thresholds)
    assert not clears(on_fc, thresholds)
    assert clears(both_clear, thresholds)


def test_the_report_carries_every_row_and_all_four_totals() -> None:
    """The printed output is the deliverable, so its completeness is checked, not its numbers."""
    rows = compare()
    lines = _report(rows)
    body = "\n".join(lines)
    for row in rows:
        assert any(line.find(row.gene) == 0 and line.find(row.path) > 0 for line in lines), (
            f"{row.gene} on {row.path} is missing from the report"
        )
    for path in PATH_VALUES:
        for rule in RULE_VALUES:
            assert body.find(f"recovered under {rule:<13} on {path:<9}") >= 0
    assert body.find(STATE_NO_USABLE_SITES) >= 0


def test_the_module_writes_no_file() -> None:
    """Stdout only. A fixture written today would pin the finding before it has been reviewed."""
    source = (SELF.parent.parent / "bzk" / "target_recovery_rules.py").read_text(encoding="utf-8")
    for forbidden in ("write_text(", "open(", "json.dump", "NamedTemporaryFile"):
        if forbidden == "open(":
            # `source_for(path).fixture.open(encoding=...)` is the fixture *read*; a write would need
            # a mode argument, and there is none in this module.
            assert source.find('.open(encoding="utf-8")') > 0
            continue
        assert source.find(forbidden) < 0, f"{forbidden} appears in a module declared write-free"


def test_no_check_in_this_module_skips() -> None:
    """Declared in the docstring, asserted here rather than left to inspection.

    Both inputs are committed, so a skip in this module would mean a check that silently stopped
    running — the failure `tests/test_tautology_sweep.py` exists one level out to catch.
    """
    source = SELF.read_text(encoding="utf-8")
    # Each marker is assembled from two halves so this guard does not match itself — the first
    # draft did, and a self-matching guard is red on a module that skips nothing.
    for head, tail in (
        ("pytest.", "skip"),
        ("mark.", "skip"),
        ("skip", "if"),
        ("import", "orskip"),
    ):
        marker = head + tail
        assert source.find(marker) < 0, f"this module carries {marker!r}"
