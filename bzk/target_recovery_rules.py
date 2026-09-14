"""`python -m bzk.target_recovery_rules` — the two recovery rules, on both paths, side by side.

**What this answers, and why it had to become code.** Each path's fixture already records a verdict
per published target, but each records the verdict of *one* rule: `pxd018299_welch_baseline.json`'s
`recovered` is the notebook's best-site-by-log2FC selection, and
`pxd018299_platform_targets.json`'s `status` is `recovered` if *any* tested site for the target
came out significant. Those are different rules, so the two membership lists are not comparable as
they stand — and the comparison that *would* make them comparable, running both rules on both
paths, has until now been done by reading numbers off a terminal. A figure produced that way cannot
be re-derived, and this one is going into a write-up.

Both fixtures now carry **every** candidate site per target, which is the change that makes the
cross-rule comparison computable at all. Before that, only the baseline's selected site survived.

**It lives in `bzk/` beside `drift.py` and `fetch_progress.py`, which is the stated precedent** —
an operational instrument the platform itself never imports, run as `python -m`. `bzk/sources/` is
"retrieval of public deposits" (its `__init__`), and this retrieves nothing; `bzk/analysis/` is
change-sets for the graph, and this writes no node. `bzk/survey_scoring.py` is the closer sibling
in shape: a reporting module that computes quantities from a committed table and reports a third
state where a verdict is not available.

**This module writes nothing.** No fixture, no file, stdout only. That is deliberate and not an
omission: which targets are recovered under which rule is the *finding*, and a fixture written in
the same turn that first computes it would pin the answer before anyone has reviewed it. The tests
beside this module assert internal relations for the same reason and pin no verdict.

**Thresholds are read from each path's own module, never restated here.** `SIG_ADJ_P` and
`SIG_LOG2FC` are defined separately in `bzk/sources/pxd018299_baseline.py` and
`bzk/sources/pxd018299_differential.py` — two definitions, presently of equal value. They are
imported separately rather than collapsed to one, because the two paths are allowed to diverge and
a single borrowed constant would hide the day one of them moved.

**The third state is an answer.** A target with no usable site on a path is neither recovered nor
not-recovered *there*: no rule has anything to evaluate. It is reported as `no_usable_sites` and
counted in neither total, rather than collapsed into a miss — collapsing it would make a target
that was never tested indistinguishable from one that was tested and failed, which is the
distinction `pxd018299_differential.py` already spends a third status on.

**Null statistics are excluded, and the exclusion is printed.** A site's `log2fc`, `p` or `adj_p`
is `null` where the arithmetic produced NaN (both fixtures say so). A NaN comparison is silently
false, so an unexcluded null site would read as "tested, did not clear" — a miss the data does not
support. The per-target rows carry the excluded count beside the site count so a target that fell
into the third state *because* of exclusions is visible as such.

**The largest-site rule breaks ties the way the baseline does.** `hits.loc[hits['log2fc'].idxmax()]`
takes the first row at the maximum; `max()` over a list returns the first maximal element. Stated
because it is a coincidence of two libraries agreeing, not a property either one documents here.

**What this does not settle.** Whether either rule is the right one. `pxd018299_differential.py`
records that as an open question and declines to answer it inside a fixture; this module computes
both and declines in the same way. It also does not reconcile the two paths' site keying — the
baseline records positions in the coordinate frame of the row's own razor accession and the
platform keys against the sequence it resolved to, so the per-target site *counts* here are
comparable but the individual sites are not paired.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

from bzk.sources import pxd018299_baseline as baseline_path
from bzk.sources import pxd018299_differential as platform_path

#: The verdict a rule returns for one target on one path. `NO_USABLE_SITES` is the third state and
#: is not a failure: it says the rule had nothing to evaluate, not that the target missed.
STATE_RECOVERED = "recovered"
STATE_NOT_RECOVERED = "not_recovered"
STATE_NO_USABLE_SITES = "no_usable_sites"
STATE_VALUES = (STATE_RECOVERED, STATE_NOT_RECOVERED, STATE_NO_USABLE_SITES)

#: The two rules under comparison. `LARGEST_SITE` is the notebook's selection rule; `ANY_SITE` is
#: the platform path's. Each is run on both paths here, which is the whole point of the module.
RULE_LARGEST_SITE = "largest_site"
RULE_ANY_SITE = "any_site"
RULE_VALUES = (RULE_LARGEST_SITE, RULE_ANY_SITE)

#: The two paths, named as their fixtures name themselves.
PATH_BASELINE = "baseline"
PATH_PLATFORM = "platform"
PATH_VALUES = (PATH_BASELINE, PATH_PLATFORM)


@dataclass(frozen=True)
class Thresholds:
    """One path's significance criterion, as that path's own module defines it."""

    sig_adj_p: float
    sig_log2fc: float


@dataclass(frozen=True)
class PathSource:
    """Where one path's per-target record and criterion come from. Both are read, never restated."""

    fixture: Path
    thresholds: Thresholds


#: Which module owns each path. The single place the association is written down.
MODULES: dict[str, ModuleType] = {
    PATH_BASELINE: baseline_path,
    PATH_PLATFORM: platform_path,
}


def source_for(path: str) -> PathSource:
    """One path's fixture and criterion, read from that path's own module.

    The fixture path is the module's own `FIXTURE_PATH` for the same reason the thresholds are its
    own `SIG_*`: a second spelling of either could disagree with the module that writes the file.

    **Read at call time rather than bound at import**, because that is what makes the provenance
    checkable. The two paths presently define equal thresholds, so a test comparing *values* cannot
    tell a constant read from this path's module from one borrowed off the other's — both would
    pass. Reading through `MODULES` on every call lets a test move one module's constant and
    observe that only that path follows, which is the property actually worth guarding.
    """
    module = MODULES[path]
    return PathSource(
        fixture=Path(module.FIXTURE_PATH),
        thresholds=Thresholds(float(module.SIG_ADJ_P), float(module.SIG_LOG2FC)),
    )


#: The three statistics both fixtures' site records share. The rest of each site record differs
#: between them — the baseline carries `protein`/`position`/`loc_prob`, the platform carries
#: `site`/`observation` — and nothing here touches those, so the two shapes need no reconciling.
STAT_FIELDS = ("log2fc", "p", "adj_p")


@dataclass(frozen=True)
class TargetVerdict:
    """One target, on one path, under both rules."""

    gene: str
    path: str
    n_sites: int
    n_excluded: int
    largest_site: str
    any_site: str

    def under(self, rule: str) -> str:
        """The verdict under `rule`. A mapping rather than a branch, so an unknown rule is loud."""
        return {RULE_LARGEST_SITE: self.largest_site, RULE_ANY_SITE: self.any_site}[rule]


def usable(site: dict[str, Any]) -> bool:
    """Whether a site carries all three statistics a rule needs.

    A site is excluded when any of them is `null`. Both fixtures write `null` where the arithmetic
    produced NaN, and a comparison against NaN is false without saying so — which would turn an
    uncomputable site into a silent miss.
    """
    return all(site.get(field) is not None for field in STAT_FIELDS)


def clears(site: dict[str, Any], thresholds: Thresholds) -> bool:
    """Whether one usable site clears both of its path's thresholds.

    The operators are the ones both source modules use — `adj_p <` and `log2fc >`, strict on each
    side — rather than a reading of what the thresholds "mean".
    """
    return (
        float(site["adj_p"]) < thresholds.sig_adj_p
        and float(site["log2fc"]) > thresholds.sig_log2fc
    )


def verdicts_for(gene: str, path: str, sites: list[dict[str, Any]]) -> TargetVerdict:
    """Both rules' verdicts for one target on one path, plus the counts behind them."""
    thresholds = source_for(path).thresholds
    testable = [site for site in sites if usable(site)]
    n_excluded = len(sites) - len(testable)
    if not testable:
        return TargetVerdict(
            gene=gene,
            path=path,
            n_sites=len(sites),
            n_excluded=n_excluded,
            largest_site=STATE_NO_USABLE_SITES,
            any_site=STATE_NO_USABLE_SITES,
        )
    largest = max(testable, key=lambda site: float(site["log2fc"]))
    return TargetVerdict(
        gene=gene,
        path=path,
        n_sites=len(sites),
        n_excluded=n_excluded,
        largest_site=STATE_RECOVERED if clears(largest, thresholds) else STATE_NOT_RECOVERED,
        any_site=(
            STATE_RECOVERED
            if any(clears(site, thresholds) for site in testable)
            else STATE_NOT_RECOVERED
        ),
    )


def load(path: str) -> dict[str, Any]:
    """One path's committed fixture. Read-only; nothing here writes a fixture back."""
    with source_for(path).fixture.open(encoding="utf-8") as handle:
        loaded: dict[str, Any] = json.load(handle)
    return loaded


def compare() -> list[TargetVerdict]:
    """Every target on every path, under both rules.

    Ordered path-major then by the fixture's own target order, which both fixtures share because
    both iterate `EXPECTED_TARGETS`. No gene list is written here: taking it from the fixtures
    means a target the fixtures stop carrying disappears from this report rather than being
    reported against nothing.
    """
    rows: list[TargetVerdict] = []
    for path in PATH_VALUES:
        for target in load(path)["targets"]:
            rows.append(verdicts_for(str(target["gene"]), path, list(target.get("sites") or [])))
    return rows


def totals(rows: list[TargetVerdict]) -> dict[tuple[str, str], int]:
    """The four figures: recoveries per (path, rule). The third state is counted in none of them."""
    return {
        (path, rule): sum(
            1 for row in rows if row.path == path and row.under(rule) == STATE_RECOVERED
        )
        for path in PATH_VALUES
        for rule in RULE_VALUES
    }


def _report(rows: list[TargetVerdict]) -> list[str]:
    """The printed report, built as lines so a test can read it without capturing stdout."""
    lines: list[str] = []
    lines.append("Published ISGylation targets under two recovery rules, on both paths.")
    lines.append("")
    for path in PATH_VALUES:
        source = source_for(path)
        lines.append(
            f"[{path}] adj p < {source.thresholds.sig_adj_p}, "
            f"log2FC > {source.thresholds.sig_log2fc}   ({source.fixture.name})"
        )
    criteria = {
        (source_for(path).thresholds.sig_adj_p, source_for(path).thresholds.sig_log2fc)
        for path in PATH_VALUES
    }
    agree = len(criteria) == 1
    lines.append(
        "        the two paths define these separately; the values presently "
        + ("agree." if agree else "DIFFER — each path is judged against its own.")
    )
    lines.append("")
    header = f"{'gene':<10}{'path':<10}{'sites':>6}{'excluded':>10}  {'largest site':<18}any site"
    lines.append(header)
    lines.append("-" * len(header))
    for row in rows:
        lines.append(
            f"{row.gene:<10}{row.path:<10}{row.n_sites:>6}{row.n_excluded:>10}  "
            f"{row.largest_site:<18}{row.any_site}"
        )
    lines.append("")
    counts = totals(rows)
    per_path = {path: sum(1 for row in rows if row.path == path) for path in PATH_VALUES}
    for path in PATH_VALUES:
        for rule in RULE_VALUES:
            lines.append(
                f"recovered under {rule:<13} on {path:<9} "
                f"{counts[path, rule]:>3} of {per_path[path]}"
            )
    lines.append("")
    for path in PATH_VALUES:
        third = sum(
            1 for row in rows if row.path == path and row.largest_site == STATE_NO_USABLE_SITES
        )
        excluded = sum(row.n_excluded for row in rows if row.path == path)
        genes = sorted(
            row.gene
            for row in rows
            if row.path == path and row.largest_site == STATE_NO_USABLE_SITES
        )
        lines.append(
            f"[{path}] {third} target(s) in the third state ({STATE_NO_USABLE_SITES}), "
            f"counted in neither total{': ' + ', '.join(genes) if genes else ''}"
        )
        lines.append(f"[{path}] {excluded} site(s) excluded for null statistics")
    return lines


def main() -> None:
    """Print the comparison. Writes no file — see the module docstring."""
    for line in _report(compare()):
        print(line)


if __name__ == "__main__":
    main()
