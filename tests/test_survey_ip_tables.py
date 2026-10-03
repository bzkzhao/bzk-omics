"""`walk/survey_ip_tables.py`'s statistics-column classification (prompt 24).

Loaded by path because `walk/` is not a package. Every column is synthetic, and every expectation is
a literal written out here, never recomputed from the function under test.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
from types import ModuleType

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "walk" / "survey_ip_tables.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("survey_ip_tables", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


survey = _load()


def test_minus_log_p_is_converted_before_binning_and_negatives_are_invalid() -> None:
    assert survey.describe_statistic(
        "N: -Log Student's T-test p-value A_B", [0.5, 2.0, 3.0, -0.1]
    ) == (
        "- `N: -Log Student's T-test p-value A_B`: -log10 p → p; 4 numeric of 4; "
        "bins {'<0.01': 1, '<0.05': 1, '>=0.05': 1}; invalid (<0): 1"
    )


def test_p_value_is_binned_as_is_and_values_outside_the_unit_interval_are_counted() -> None:
    assert survey.describe_statistic(
        "N: Student's T-test p-value A_B", [0.001, 0.03, 0.2, 1.5]
    ) == (
        "- `N: Student's T-test p-value A_B`: p/q; 4 numeric of 4; "
        "bins {'<0.01': 1, '<0.05': 1, '>=0.05': 1}; out of [0, 1]: 1"
    )


def test_difference_reports_signs_only() -> None:
    assert survey.describe_statistic("N: Student's T-test Difference A_B", [1.2, -0.4, 0.0]) == (
        "- `N: Student's T-test Difference A_B`: difference; 3 numeric of 3; "
        "signs {'>0': 1, '<0': 1, '=0': 1}"
    )


def test_significant_counts_plus_against_blank_even_though_the_header_names_a_t_test() -> None:
    assert survey.describe_statistic("C: Student's T-test Significant A_B", ["+", "", "+"]) == (
        "- `C: Student's T-test Significant A_B`: significance marker; {'+': 2, 'blank': 1}"
    )


def test_a_statistic_none_of_the_rows_name_is_unclassified() -> None:
    assert (
        survey.describe_statistic("N: Student's T-test A_B", [0.4, 2.0])
        == "- `N: Student's T-test A_B`: unclassified statistic; 2 numeric of 2"
    )


def test_minus_log_q_value_is_unclassified_and_not_converted() -> None:
    assert survey.describe_statistic("N: -Log Student's T-test q-value A_B", [0.5, 2.0, 3.0]) == (
        "- `N: -Log Student's T-test q-value A_B`: unclassified statistic; 3 numeric of 3"
    )


def test_every_synthetic_header_is_one_the_survey_would_route_here() -> None:
    headers = [
        "-Log Student's T-test p-value A_B",
        "Student's T-test p-value A_B",
        "Student's T-test Difference A_B",
        "Student's T-test Significant A_B",
        "Student's T-test A_B",
        "-Log Student's T-test q-value A_B",
    ]
    assert all(survey.STATISTIC.search(h) for h in headers)
    assert not survey.STATISTIC.search("Q-value")
