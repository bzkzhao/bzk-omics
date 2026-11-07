"""`bzk/stats/tukey.py` against R, before any real data passes through it.

`walk/PREREG-PXD032267-gate.md` §4, *Instrument validation*: the five variants are validated
against R on `ToothGrowth` (supp × dose, doses 0.5 and 1.0, so a balanced 2 × 2) to |Δp| ≤ 1e-6,
and *"a failure stops the build, not the gate."*

**The oracle was not produced here.** `tests/fixtures/r_tukey_reference.csv` was generated on bzk's
Mac under R 4.5.2 by `notes/scripts/tukey_reference.R`, and an independent R 4.3.3 run agreed on all
114 values to 1e-14. Its independence from the session that wrote `tukey.py` is the point: an
implementation and an oracle written together can share a misreading of which pair, which error
term or which df, and then agree perfectly.

**R's pair names are parsed, not hard-coded.** `VC:0.5-OJ:0.5` is split on its one `-` into the two
cells, and `TukeyResult.pair` is asked for that orientation, so a fixture row this module did not
anticipate is checked rather than skipped. The `environment` row carries no value and is the one
row skipped; the count of values checked is asserted, so a skip that grew would fail.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import numpy as np
import pytest
from scipy import stats

from bzk.stats.anova import AnovaError
from bzk.stats.tukey import VARIANTS, TukeyError, TukeyResult, tukey

FIXTURES = Path(__file__).parent / "fixtures"
ORACLE = FIXTURES / "r_tukey_reference.csv"
TOOTHGROWTH = FIXTURES / "toothgrowth.csv"

#: Registration §4: *"to |Δp| ≤ 1e-6"*. Applied to every numeric value in the oracle, the
#: differences and MSEs included, which are held to the same bound because they are the inputs
#: every p is formed from.
TOLERANCE = 1e-6

#: Numeric rows in the oracle: 39 per case and 36 in the grid. Asserted so that a parse which
#: silently dropped rows cannot pass by checking fewer.
ORACLE_VALUES = 114


def _oracle() -> list[dict[str, str]]:
    return list(csv.DictReader(ORACLE.read_text(encoding="utf-8").splitlines()))


def _cases() -> dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """The two designs `tukey_reference.R` builds, rebuilt from the committed `ToothGrowth`.

    `tg_n10` is every row at doses 0.5 and 1; `tg_n3` is the first three rows of each cell in
    dataset order, as the script's `d[1:3, ]` takes them.
    """
    rows = [
        r
        for r in csv.DictReader(TOOTHGROWTH.read_text(encoding="utf-8").splitlines())
        if r["dose"] in ("0.5", "1")
    ]
    first_three: list[dict[str, str]] = []
    seen: dict[tuple[str, str], int] = {}
    for r in rows:
        key = (r["supp"], r["dose"])
        if seen.get(key, 0) < 3:
            first_three.append(r)
            seen[key] = seen.get(key, 0) + 1

    def arrays(chosen: list[dict[str, str]]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        return (
            np.array([[float(r["len"]) for r in chosen]]),
            np.array([r["supp"] for r in chosen]),
            np.array([r["dose"] for r in chosen]),
        )

    return {"tg_n10": arrays(rows), "tg_n3": arrays(first_three)}


def _ours(case: str, quantity: str, pair: str, cache: dict[str, TukeyResult]) -> float:
    """This module's value for one oracle row, located by parsing R's labels."""
    if case == "ptukey_grid":
        fields = dict(part.split("=") for part in pair.split(";"))
        return float(
            stats.studentized_range.sf(float(fields["q"]), int(fields["nmeans"]), int(fields["df"]))
        )
    if case not in cache:
        cache[case] = tukey(*_cases()[case])
    result = cache[case]
    if quantity == "n":
        return float(result.n_per_cell * len(result.cells))
    if quantity in ("mse_interaction", "mse_additive"):
        return float(getattr(result, quantity)[0])
    first, second = pair.split("-")
    found = result.pair(first, second)
    if quantity == "diff":
        return float(found.diff[0])
    variant = quantity.removesuffix("_p")
    return float(found.p[variant][0])


def test_every_oracle_value_is_reproduced_to_1e_6() -> None:
    cache: dict[str, TukeyResult] = {}
    failures: list[str] = []
    checked = 0
    for row in _oracle():
        if row["value"] == "":
            assert row["case"] == "environment", row
            continue
        expected = float(row["value"])
        got = _ours(row["case"], row["quantity"], row["pair"], cache)
        checked += 1
        if not abs(got - expected) <= TOLERANCE:
            failures.append(
                f"{row['case']} {row['quantity']} {row['pair']}: {got!r} vs {expected!r}"
            )
    assert not failures, failures
    assert checked == ORACLE_VALUES


def test_the_tolerance_is_the_registrations() -> None:
    """§4 *Instrument validation*: *"to |Δp| ≤ 1e-6"*, parsed rather than restated."""
    text = (Path(__file__).resolve().parents[1] / "walk" / "PREREG-PXD032267-gate.md").read_text(
        encoding="utf-8"
    )
    found = re.findall(r"`ToothGrowth` \(supp × dose\), to \|Δp\| ≤ ([0-9]+e-[0-9]+)", text)
    assert len(found) == 1, found
    assert float(found[0]) == TOLERANCE


def test_the_oracle_is_the_one_committed_with_revision_1() -> None:
    """Its shape, as the receipt check read it: 115 rows, R 4.5.2, n = 40 and n = 12."""
    rows = _oracle()
    assert len(rows) == ORACLE_VALUES + 1
    environment = [r for r in rows if r["case"] == "environment"]
    assert [r["pair"] for r in environment] == ["R version 4.5.2 (2025-10-31)"]
    sizes = {r["case"]: r["value"] for r in rows if r["quantity"] == "n"}
    assert sizes == {"tg_n10": "40", "tg_n3": "12"}


def test_the_df_are_n_minus_four_n_minus_three_and_two_n_minus_two() -> None:
    """At ToothGrowth's two sizes. The registration's own n = 3 values are guarded in
    `tests/test_pxd032267_gate.py` against its text."""
    for case, (interaction, additive, student) in {
        "tg_n10": (36, 37, 18),
        "tg_n3": (8, 9, 4),
    }.items():
        result = tukey(*_cases()[case], variants=("T3",))
        assert (result.df_interaction, result.df_additive, result.df_student) == (
            interaction,
            additive,
            student,
        )


def test_pair_reverses_the_difference_and_keeps_every_p() -> None:
    values, supp, dose = _cases()["tg_n3"]
    result = tukey(values, supp, dose)
    forward = result.pair("VC:0.5", "OJ:0.5")
    backward = result.pair("OJ:0.5", "VC:0.5")
    assert float(backward.diff[0]) == -float(forward.diff[0])
    for variant in VARIANTS:
        assert float(backward.p[variant][0]) == float(forward.p[variant][0])


def test_rows_are_independent_so_a_restricted_call_agrees_with_a_full_one() -> None:
    """`pairs` and `variants` exist for speed; restricting them must change no value."""
    values, supp, dose = _cases()["tg_n10"]
    stacked = np.vstack([values, values[:, ::-1], values * 2.0])
    full = tukey(stacked, supp, dose)
    narrow = tukey(stacked[1:2], supp, dose, pairs=[("OJ:1", "VC:1")], variants=("T1", "T5"))
    wide = full.pair("OJ:1", "VC:1")
    one = narrow.pair("OJ:1", "VC:1")
    for variant in ("T1", "T5"):
        assert abs(float(one.p[variant][0]) - float(wide.p[variant][1])) <= 1e-15
    assert set(one.p) == {"T1", "T5"}


def test_missing_values_are_refused() -> None:
    values, supp, dose = _cases()["tg_n3"]
    broken = values.copy()
    broken[0, 0] = np.nan
    with pytest.raises(AnovaError, match="missing value"):
        tukey(broken, supp, dose)


def test_an_unbalanced_design_is_refused() -> None:
    values, supp, dose = _cases()["tg_n3"]
    with pytest.raises(AnovaError, match="unbalanced"):
        tukey(values[:, 1:], supp[1:], dose[1:])


def test_a_design_that_is_not_two_by_two_is_refused() -> None:
    rows = list(csv.DictReader(TOOTHGROWTH.read_text(encoding="utf-8").splitlines()))
    values = np.array([[float(r["len"]) for r in rows]])
    supp = np.array([r["supp"] for r in rows])
    dose = np.array([r["dose"] for r in rows])
    with pytest.raises(TukeyError, match="not 2x2"):
        tukey(values, supp, dose)


def test_an_unknown_variant_or_pair_is_refused() -> None:
    values, supp, dose = _cases()["tg_n3"]
    with pytest.raises(TukeyError, match="unknown variant"):
        tukey(values, supp, dose, variants=("T6",))
    with pytest.raises(TukeyError, match="not two distinct cells"):
        tukey(values, supp, dose, pairs=[("VC:0.5", "VC:0.5")])
    with pytest.raises(TukeyError, match="no pair"):
        tukey(values, supp, dose, pairs=[("VC:0.5", "OJ:0.5")]).pair("VC:1", "OJ:1")
