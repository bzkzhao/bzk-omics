"""`python -m bzk.published_cascade` — the published-claim cascade for PXD018299, from its fixture.

**What this answers.** Of the 798 site-level claims the anchor publication makes in its Supplementary
Data 1 (`SUPP_DATA_1`), how many survive the platform path, and which stage loses each of the rest.
Each S1 row is joined to exactly one row of the deposit's GlyGly site table and walked through the
platform's own stages — decoy/contaminant, localisation, ingestion, presence rule, significance —
and placed at exactly one of them. `tests/fixtures/pxd018299_published_cascade.json` holds the
per-row result; this module computes the cascade table, the significance split, the recall figure
and the fold-change control partitions **from that fixture alone**.

**The figure is one-directional by construction, and that bounds what every number here means.**
S1 lists the publication's *significant* peptides and nothing else; no published table lists what
the publication tested and did not call. So this measures **recall of published claims** through
the platform path. It does not and cannot measure the converse: a platform-significant site with no
S1 row may be non-significant in the publication, undetected there, or cut by a rule the
publication does not state, and nothing in the published record distinguishes those.

**Which figures a clone can re-derive, and which needed the store and the network.**

- *Re-derivable from a clone, by this module, with no deposit, no store, no graph and no network:*
  the cascade table, the significance split, the recall figure and the control partitions. Every
  one is a function of the committed per-row fields, and nothing here imports a reader for any
  other source.
- *Required the content-addressed store and UniProt to generate:* the per-row fields themselves.
  The join needs the deposit's bytes and S1's bytes from `raw/`; the stage each row reaches needs
  the platform path run over the deposit, which resolves against the UniProt cache; the published
  side's keying needs live UniProt lookups for accessions the deposit path never attempts. Those
  are produced by `python -m bzk.sources.pxd018299_published_cascade`, whose `generated_under`
  records when, at which commit, and under which network conditions.

**This module writes nothing** — stdout only, in the shape of `bzk/target_recovery_rules.py`.

**Precision.** The published log2 fold change is computed from S1's intensity cells as the
publication rounded them, to four decimal places, so a `published − platform` difference is only
meaningful to about 5e-5. The control partition is reported, not tested, to that precision.
"""

from __future__ import annotations

import json
import math
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "pxd018299_published_cascade.json"

#: The platform path's stages, in the order a row meets them. `join` is the first: a published row
#: that matches no single deposit row never enters the deposit path at all.
STAGE_JOIN = "join"
STAGE_DECOY_CONTAMINANT = "decoy_contaminant"
STAGE_LOCALISATION = "localisation"
STAGE_INGESTION = "ingestion"
STAGE_PRESENCE = "presence"
STAGE_SIGNIFICANCE = "significance"
STAGES = (
    STAGE_JOIN,
    STAGE_DECOY_CONTAMINANT,
    STAGE_LOCALISATION,
    STAGE_INGESTION,
    STAGE_PRESENCE,
    STAGE_SIGNIFICANCE,
)

#: Where a row that is lost at none of the stages ends up.
RECOVERED = "recovered"

#: The two halves of the significance criterion, and their conjunction. A row lost at significance
#: carries exactly one of these as its `loss_reason`.
FAILS_P_VALUE = "p_value"
FAILS_FOLD_CHANGE = "fold_change"
FAILS_BOTH = "both"
SIGNIFICANCE_REASONS = (FAILS_P_VALUE, FAILS_FOLD_CHANGE, FAILS_BOTH)

#: The published WT arm's cell count below this value is the control partition's key.
WT_LOW_CUTOFF = 21


class CascadeFixtureError(ValueError):
    """The fixture does not have the shape this module reads. Never downgraded to a warning."""


def load(path: Path | None = None) -> dict[str, Any]:
    """The committed fixture. Read-only; nothing here writes a fixture back."""
    with (path or FIXTURE_PATH).open(encoding="utf-8") as handle:
        loaded: dict[str, Any] = json.load(handle)
    return loaded


def outcome(row: dict[str, Any]) -> str:
    """The one place a row ends: the stage that lost it, or `recovered`.

    Refuses a row whose fields contradict each other rather than guessing, because a row placed at
    two stages — or at none — is exactly what the cascade's sum exists to rule out.
    """
    lost_at = row.get("lost_at")
    if lost_at is None:
        if row.get("loss_reason") is not None:
            raise CascadeFixtureError(f"row {row.get('row')} is not lost but carries a loss_reason")
        return RECOVERED
    if lost_at not in STAGES:
        raise CascadeFixtureError(f"row {row.get('row')} is lost at unknown stage {lost_at!r}")
    if lost_at == STAGE_SIGNIFICANCE and row.get("loss_reason") not in SIGNIFICANCE_REASONS:
        raise CascadeFixtureError(
            f"row {row.get('row')} is lost at significance with reason {row.get('loss_reason')!r}"
        )
    return str(lost_at)


@dataclass(frozen=True)
class CascadeStep:
    """One stage: how many rows it lost, and how many survive past it."""

    stage: str
    lost: int
    surviving: int


def cascade(rows: list[dict[str, Any]]) -> list[CascadeStep]:
    """The cascade table, in stage order, starting from every row in the fixture."""
    ends = [outcome(row) for row in rows]
    surviving = len(rows)
    steps: list[CascadeStep] = []
    for stage in STAGES:
        lost = ends.count(stage)
        surviving -= lost
        steps.append(CascadeStep(stage, lost, surviving))
    return steps


def recovered(rows: list[dict[str, Any]]) -> int:
    """Rows lost at no stage."""
    return sum(1 for row in rows if outcome(row) == RECOVERED)


def significance_split(rows: list[dict[str, Any]]) -> dict[str, int]:
    """Rows lost at significance, by which half of the criterion they fail."""
    reasons = [row["loss_reason"] for row in rows if outcome(row) == STAGE_SIGNIFICANCE]
    return {reason: reasons.count(reason) for reason in SIGNIFICANCE_REASONS}


@dataclass(frozen=True)
class Distribution:
    """`published − platform` log2 fold change over a set of rows."""

    n: int
    mean: float
    sd: float
    minimum: float
    maximum: float
    median: float
    mean_abs: float


def distribution(values: list[float]) -> Distribution:
    if not values:
        nan = math.nan
        return Distribution(0, nan, nan, nan, nan, nan, nan)
    return Distribution(
        n=len(values),
        mean=statistics.fmean(values),
        sd=statistics.stdev(values) if len(values) > 1 else math.nan,
        minimum=min(values),
        maximum=max(values),
        median=statistics.median(values),
        mean_abs=statistics.fmean(abs(v) for v in values),
    )


def tested(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rows that reached the significance test with a platform fold change to compare against."""
    return [
        row
        for row in rows
        if outcome(row) in (RECOVERED, STAGE_SIGNIFICANCE) and row["platform_log2fc"] is not None
    ]


def differences(rows: list[dict[str, Any]]) -> list[float]:
    return [float(row["published_log2fc"]) - float(row["platform_log2fc"]) for row in rows]


def control_partitions(rows: list[dict[str, Any]]) -> dict[int, Distribution]:
    """The tested rows' fold-change differences, partitioned by published WT cells below 21.

    Reported, not explained: the partition is the measurement, and what it implies is the reader's.
    """
    reached = tested(rows)
    return {
        k: distribution(differences([row for row in reached if row["wt_cells_below_21"] == k]))
        for k in (0, 1, 2, 3)
    }


def _report(fixture: dict[str, Any]) -> list[str]:
    """The printed report, built as lines so a test can read it without capturing stdout."""
    rows: list[dict[str, Any]] = fixture["rows"]
    lines = [
        (
            f"Published-claim cascade: {fixture['dataset']} / Supplementary Data 1, "
            f"{len(rows)} published site-level claims through the platform path."
        ),
        "Recall only: S1 lists the significant set, so the converse is not measurable.",
        "",
        f"{'stage':<20}{'lost':>6}{'surviving':>11}",
        f"{'(published rows)':<20}{'':>6}{len(rows):>11}",
    ]
    for step in cascade(rows):
        lines.append(f"{step.stage:<20}{step.lost:>6}{step.surviving:>11}")
    split = significance_split(rows)
    lines.append(
        "  significance fails: "
        + ", ".join(f"{reason} only {split[reason]}" for reason in SIGNIFICANCE_REASONS[:2])
        + f", both {split[FAILS_BOTH]}"
    )
    got = recovered(rows)
    lines.append(f"recovered {got} of {len(rows)} ({100 * got / len(rows):.1f}%)")
    lines.append("")
    lines.append("published - platform log2FC, by published WT cells below 21:")
    lines.append(f"{'cells':>6}{'n':>6}{'mean':>10}{'sd':>9}{'min':>10}{'max':>9}{'mean|d|':>10}")
    everything = distribution(differences(tested(rows)))
    for label, d in [*control_partitions(rows).items(), ("all", everything)]:
        lines.append(
            f"{label!s:>6}{d.n:>6}{d.mean:>+10.4f}{d.sd:>9.4f}{d.minimum:>+10.4f}"
            f"{d.maximum:>+9.4f}{d.mean_abs:>10.4f}"
        )
    return lines


def main() -> None:
    """Print the cascade. Writes no file — see the module docstring."""
    for line in _report(load()):
        print(line)


if __name__ == "__main__":
    main()
