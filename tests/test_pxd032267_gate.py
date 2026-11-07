"""`bzk/sources/pxd032267_gate.py` — guarded against its registration, tested on synthetic twins.

**No deposit bytes are used here, and none exist in the build container.** Every branch of the
instrument is exercised on a synthetic site table written into `tmp_path` (`HANDOFF.md` §8's
synthetic twin), shaped like `GlyGly__K_Sites.txt` in the columns the module reads and nothing
else. The real run is on bzk's Mac.

**Every registered number is parsed from `walk/PREREG-PXD032267-gate.md` and compared to the module
constant**, in the pattern of `graph.I4_LABELS`' guard (`tests/test_query.py`). A pattern that
matches other than exactly once fails rather than picking one, so a number that cannot be parsed
unambiguously is reported by the failure instead of being hard-coded around.
"""

from __future__ import annotations

import ast
import collections
import copy
import csv
import inspect
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, cast

import numpy as np
import pytest

from bzk.sources import pxd032267_gate as gate
from bzk.sources.pride import PXD032267_PARAMETERS, PXD032267_SITES, DepositFile
from bzk.sources.pxd026748_reconstruction import SEEDS, Member
from bzk.stats.tukey import tukey

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRATION = (REPO_ROOT / "walk" / "PREREG-PXD032267-gate.md").read_text(encoding="utf-8")
WALK = json.loads((REPO_ROOT / "walk" / "walk_PXD032267.json").read_text(encoding="utf-8"))
WALK_JOIN = WALK["deposit_read"]["join_to_published_claims"]["rows"]

WORDS = {"one": 1, "two": 2, "three": 3}


# ── reading the registration ────────────────────────────────────────────────────────────────────


def _section(number: int) -> str:
    """The text of `## <number>.` up to the next `## ` heading."""
    match = re.search(rf"^## {number}\. .*?(?=^## |\Z)", REGISTRATION, re.DOTALL | re.MULTILINE)
    assert match is not None, f"registration has no section {number}"
    return match.group(0)


def _one(pattern: str, text: str) -> tuple[str, ...]:
    """The groups of the one match of `pattern` in `text`. Zero or two matches fail, naming them."""
    found = list(re.finditer(pattern, text, re.DOTALL))
    assert len(found) == 1, f"{pattern!r} matched {len(found)} times: {[m.group(0) for m in found]}"
    return found[0].groups()


NUMBER = r"([0-9]+(?:\.[0-9]+)?(?:e-[0-9]+)?)"


def test_the_input_tolerance_is_section_4s() -> None:
    (value,) = _one(rf"pinned file to \|Δ\| ≤ {NUMBER}", _section(4))
    assert float(value) == gate.INPUT_TOLERANCE


def test_the_p_tolerance_is_section_4s_in_both_places_it_is_used() -> None:
    section = _section(4)
    (passes,) = _one(rf"on every gate row, \|p − published `p_value`\| ≤ {NUMBER}", section)
    (separated,) = _one(rf"variants are within {NUMBER} of each other on every gate row", section)
    assert float(passes) == float(separated) == gate.P_TOLERANCE


def test_the_minimum_gate_rows_is_section_4s_in_both_places_it_is_stated() -> None:
    section = _section(4)
    (rule,) = _one(r"if there are fewer than (\w+), G is \*\*undeterminable\*\*", section)
    (why,) = _one(r"which is why §4 needs at least (\w+) gate rows", section)
    assert WORDS[rule] == WORDS[why] == gate.MIN_GATE_ROWS


def _variant_table() -> list[tuple[str, str]]:
    return re.findall(r"^\| \*{0,2}(T\d)\*{0,2} \| (.*?) \|$", _section(4), re.MULTILINE)


def test_the_variants_are_section_4s_table_in_its_order() -> None:
    assert tuple(v for v, _ in _variant_table()) == gate.GATE_VARIANTS


def test_the_registered_df_are_the_n_equals_3_instances_of_tukeys_formulas() -> None:
    """§4 states the df at the gate's own n = 3 (§1). They are guarded as that instance:
    `tukey` is run on a synthetic 2 × 2 at n = 3 and its df compared to the table's."""
    (n,) = _one(r"n = (\d+) per cell", _section(1))
    stated = {
        v: int(m.group(1)) for v, text in _variant_table() if (m := re.search(r"df = (\d+)", text))
    }
    assert set(stated) == {"T1", "T2", "T3", "T4"}, stated
    per_cell = int(n)
    values = np.arange(4 * per_cell, dtype=float).reshape(1, -1) ** 1.5
    result = tukey(
        values,
        np.array(["a"] * (2 * per_cell) + ["b"] * (2 * per_cell)),
        np.array((["x"] * per_cell + ["y"] * per_cell) * 2),
        variants=("T3",),
    )
    measured = {
        "T1": result.df_interaction,
        "T2": result.df_additive,
        "T3": result.df_interaction,
        "T4": result.df_student,
    }
    assert measured == stated


def _grid_line(name: str) -> str:
    (line,) = _one(rf"\n\s*- {name} (.+?);\n", _section(3))
    return line


def test_the_grid_and_its_default_cell_are_section_3s() -> None:
    widths = _grid_line("width")
    downshifts = _grid_line("downshift")
    scopes = _grid_line("scope")
    assert tuple(float(x) for x in re.findall(r"[0-9.]+", widths)) == gate.GRID_WIDTH_SDS
    assert tuple(float(x) for x in re.findall(r"[0-9.]+", downshifts)) == gate.GRID_DOWNSHIFT_SDS
    assert tuple(re.findall(r"`(\w+)`", scopes)) == gate.GRID_SCOPES
    bold = (
        float(_one(r"\*\*([0-9.]+)\*\*", widths)[0]),
        float(_one(r"\*\*([0-9.]+)\*\*", downshifts)[0]),
        _one(r"\*\*`(\w+)`\*\*", scopes)[0],
    )
    width, downshift, scope = _one(
        r"The \*\*default cell\*\* is \(([0-9.]+), ([0-9.]+), `(\w+)`\)", _section(3)
    )
    assert bold == (float(width), float(downshift), scope) == gate.DEFAULT_CELL


def test_twenty_draws_with_seed_k_are_seeds_0_to_19() -> None:
    """*"20 draws per cell, with draw k using seed k"*. The count is the registration's; the range
    0–19 is the build's reading, and is the house convention `pxd026748_reconstruction.SEEDS`."""
    (draws,) = _one(r"(\d+) draws per cell, with draw k using seed k", _section(3))
    assert len(gate.DRAW_SEEDS) == int(draws)
    assert gate.DRAW_SEEDS == tuple(range(int(draws)))
    assert gate.DRAW_SEEDS is SEEDS


def test_the_valid_value_candidates_are_section_3s_in_order() -> None:
    found = re.findall(r"at least (\d+) (?:valid values )?in at least one", _section(3))
    assert tuple(int(x) for x in found) == gate.VALID_VALUE_CANDIDATES


def test_support_is_both_halves_of_the_rule_everywhere_it_is_stated() -> None:
    """Up and down are each a p half and a Difference half. §1 states both directions, §5 B up,
    §5 C down; every statement must agree with the constant pair."""
    up_1, down_1, alpha_1 = _one(
        rf"Difference > {NUMBER} and downregulation at\s+Difference < −{NUMBER}, with P < {NUMBER}",
        _section(1),
    )
    alpha_b, up_b = _one(rf"Support means p < {NUMBER} and Difference > {NUMBER}", _section(5))
    alpha_c, down_c = _one(rf"\(p < {NUMBER}, Difference < −{NUMBER}\)", _section(5))
    assert {float(alpha_1), float(alpha_b), float(alpha_c)} == {gate.SUPPORT_ALPHA}
    assert {float(up_1), float(down_1), float(up_b), float(down_c)} == {gate.SUPPORT_DIFFERENCE}


def test_readout_a_near_is_measured_against_the_median_at_section_5s_fraction() -> None:
    (percent,) = _one(r"within ±(\d+)% of the median", _section(5))
    assert int(percent) / 100 == gate.NEAR_FRACTION


def test_readout_b_thresholds_are_section_5s() -> None:
    section = _section(5)
    (recurs,) = _one(r"\*\*Recurs:\*\* at least (\d+)%", section)
    (absent,) = _one(r"\*\*Absent:\*\* at most (\d+)%", section)
    assert int(recurs) / 100 == gate.RECURS_AT_OR_ABOVE_SHARE
    assert int(absent) / 100 == gate.ABSENT_AT_OR_BELOW_SHARE


def test_readout_c_targets_section_5s_named_site() -> None:
    name, position = _one(r"\*\*C\. The named target\.\*\* (\S+) K(\d+)'s", _section(5))
    assert (name, int(position)) == gate.READOUT_C_TARGET


# ── the published tables and the walk record ────────────────────────────────────────────────────


def test_table_7_in_the_published_tables_file_equals_the_registrations_table() -> None:
    """Two transcriptions of one supplement table: §5's and the sha256-pinned file's."""
    rows = re.findall(r"^\| ([^|]+?) \| (\d+) \| (\d+) \|$", _section(5), re.MULTILINE)
    assert len(rows) == 3, rows
    published = gate.load_published().table_7
    assert list(published) == [c.published_label for c in gate.COMPARISONS]
    assert [(int(u), int(d)) for _, u, d in rows] == [
        (v["up"], v["down"]) for v in published.values()
    ]


def test_table_8_differences_equal_the_walk_records() -> None:
    published = gate.load_published()
    assert [c.difference for c in published.claims] == [
        r["published_difference"] for r in WALK_JOIN
    ]


def test_the_two_p_values_quoted_in_y6_agree_with_the_published_tables_to_their_rounding() -> None:
    (row,) = [r for r in _section(6).splitlines() if r.startswith("| Y6 |")]
    quoted = dict(re.findall(r"(\w+ K\d+) \((0\.\d+)\)", row))
    assert set(quoted) == {"Ackr3 K362", "Adprhl1 K335"}, quoted
    claims = gate.load_published().claims
    by_label = {r["claim"]: claims[i] for i, r in enumerate(WALK_JOIN)}
    for label, text in quoted.items():
        decimals = len(text.split(".")[1])
        assert round(by_label[label].p_value, decimals) == float(text), label


def test_the_deposit_facts_are_the_receipts() -> None:
    facts = gate.load_deposit_facts()
    assert (facts.data_rows, facts.columns, facts.reverse) == (1440, 171, 14)
    assert facts.joined_ids == (57, 151, 281, 405, 553, 901, 1252, 1270, 1276, 1282)


def test_the_samples_are_the_deposits_own_labels() -> None:
    """`deposit_read.site_table.samples` reads `KOC1-3, KOTCA1-3, WtC1-3, WtTAC1-3`."""
    stated = WALK["deposit_read"]["site_table"]["samples"].split(" (")[0]
    expanded = [f"{stem}{i}" for stem in re.findall(r"(\w+?)1-3", stated) for i in (1, 2, 3)]
    assert tuple(expanded) == gate.SAMPLES


def test_the_deposit_declarations_carry_a_pinned_digest_and_the_publication_month() -> None:
    """Digests pinned from the Mac fetch (step A, 2026-11-07); the archive month from `frame_raw.tsv`."""
    frame = REPO_ROOT / "data" / "frame" / "frame_raw.tsv"
    with frame.open(encoding="utf-8", newline="") as handle:
        (row,) = [
            r for r in csv.DictReader(handle, delimiter="\t") if r["accession"] == "PXD032267"
        ]
    year, month, _ = row["publicationDate"].split("-")
    for deposit in (PXD032267_SITES, PXD032267_PARAMETERS):
        assert re.fullmatch(r"sha256:[0-9a-f]{64}", deposit.expected_content_hash or ""), deposit
        assert (deposit.year, deposit.month) == (int(year), int(month))
    assert PXD032267_SITES.filename == WALK["deposit_read"]["site_table"]["artefact"]


# ── the synthetic twin ──────────────────────────────────────────────────────────────────────────

HEADER = (
    ["Proteins", "Positions within proteins", "Protein names", "GlyGly (K) Probabilities"]
    + [gate.INTENSITY_PREFIX + s for s in gate.SAMPLES]
    + [gate.IDENTIFICATION_PREFIX + s for s in gate.SAMPLES]
    + ["Reverse", "id"]
)

#: The order of `gate.SAMPLES`: KO control, KO TAC, WT control, WT TAC, three each.
KO_C, KO_T, WT_C, WT_T = slice(0, 3), slice(3, 6), slice(6, 9), slice(9, 12)


def _row(
    ident: int,
    name: str,
    position: int,
    probabilities: str,
    log2: np.ndarray,
    *,
    reverse: bool = False,
    matched: tuple[int, ...] = (),
) -> list[str]:
    intensities = ["0" if np.isnan(v) else repr(float(2.0**v)) for v in log2]
    types = [
        "By matching" if i in matched else ("" if np.isnan(v) else "By MS/MS")
        for i, v in enumerate(log2)
    ]
    return [
        f"SYN{ident}",
        str(position),
        name,
        probabilities,
        *intensities,
        *types,
        "+" if reverse else "",
        str(ident),
    ]


def _claim_values(
    control: float, tac: float, spread: float, ko_spread: tuple[float, float, float]
) -> np.ndarray:
    """WT arms with equal spread (so Student and Welch coincide), KO arms deliberately unequal."""
    out = np.empty(12)
    out[WT_C] = control + np.array([-spread, 0.0, spread])
    out[WT_T] = tac + np.array([-spread, 0.0, spread])
    out[KO_C] = 23.0 + np.array(ko_spread)
    out[KO_T] = 23.5 + np.array(ko_spread[::-1]) * 1.7
    return out


def _twin(
    tmp_path: Path,
    *,
    complete_claims: int = 2,
    published_variant: str = "T4",
    difference_error: float = 0.0,
    matched_claim: bool = False,
) -> tuple[Path, Path, gate.Published, gate.DepositFacts]:
    """A site table, a parameters file, and the published tables and facts that describe it.

    Three claims: two complete in all twelve samples (gate rows) unless `complete_claims` says
    fewer, and filamin-C K2590 with one WT control value missing. Published `Difference` and
    `p_value` are this data's own, at the publication's six decimals, under `published_variant`.
    """
    rng = np.random.default_rng(7)
    lines = []
    for i in range(1, 31):
        values = rng.normal(24.0, 1.2, 12)
        values[rng.random(12) < 0.12] = np.nan
        lines.append(_row(i, f"Background protein {i}", 7 * i, f"PEPK(1)R{i}", values))
    for i in range(31, 34):
        lines.append(_row(i, "Decoy", 1, "DECOYK(1)", rng.normal(20.0, 1.0, 12), reverse=True))
    alpha = _claim_values(22.0, 24.0, 0.3, (-1.0, 0.1, 1.2))
    beta = _claim_values(21.0, 22.5, 0.5, (-0.8, 0.3, 0.9))
    if complete_claims < 2:
        beta[KO_C.start] = np.nan
    filamin = _claim_values(20.5, 22.0, 0.4, (-0.6, 0.2, 0.7))
    filamin[WT_C.start] = np.nan
    claims_data = [
        (101, "Alpha protein", 10, "AAAK(1)R", alpha),
        (102, "Beta protein", 20, "BBBK(1)R", beta),
        (103, "Filamin-C", 2590, "YGGK(0.997)AK(0.003)", filamin),
    ]
    for ident, name, position, probabilities, values in claims_data:
        matched = tuple(range(12)) if (matched_claim and name == "Filamin-C") else ()
        lines.append(_row(ident, name, position, probabilities, values, matched=matched))

    sites = tmp_path / "GlyGly__K_Sites.txt"
    with sites.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(HEADER)
        writer.writerows(lines)
    parameters = tmp_path / "parameters.txt"
    parameters.write_text("Version\t2.0.3.0\n", encoding="utf-8")

    published_claims = []
    for _, name, position, probabilities, values in claims_data:
        row = values.reshape(1, -1)
        difference = float(np.nanmean(row[0, WT_T]) - np.nanmean(row[0, WT_C]))
        p = 0.5
        if not np.isnan(row).any():
            p = float(
                tukey(row, gate.GENOTYPE, gate.SURGERY, variants=(published_variant,))
                .pair("WT:TAC", "WT:control")
                .p[published_variant][0]
            )
        published_claims.append(
            gate.PublishedClaim(
                protein_name=name,
                position=position,
                glygly_probabilities=probabilities,
                p_value=round(p, 6),
                difference=round(difference, 6)
                + (difference_error if name == "Alpha protein" else 0.0),
            )
        )
    published = gate.Published(
        claims=tuple(published_claims),
        table_7={c.published_label: {"up": 1, "down": 1} for c in gate.COMPARISONS},
        source_sha256="synthetic",
    )
    facts = gate.DepositFacts(
        data_rows=len(lines), columns=len(HEADER), reverse=3, joined_ids=(101, 102, 103)
    )
    return sites, parameters, published, facts


#: The default cell's twenty draws and one member off it — enough to exercise the family's
#: categories without running all 360 on a synthetic table.
FEW_MEMBERS = (*gate.default_cell_members(), Member(0.2, 1.6, "whole_matrix", 0))


#: The synthetic twins are not the deposit, so they are checked against unpinned copies of the
#: real declarations. The real declarations carry the digests pinned from the Mac fetch, and a
#: synthetic file against them must raise: `test_the_pinned_declaration_refuses_a_twin` says so.
UNPINNED_SITES = DepositFile("PXD032267", 2023, 5, "GlyGly__K_Sites.txt", None)
UNPINNED_PARAMETERS = DepositFile("PXD032267", 2023, 5, "parameters.txt", None)
UNPINNED: dict[str, Any] = {
    "sites_deposit": UNPINNED_SITES,
    "parameters_deposit": UNPINNED_PARAMETERS,
}


def _run(tmp_path: Path, **kwargs: Any) -> dict[str, Any]:
    author_path = kwargs.pop("author_path", tmp_path / "no-author.json")
    repo_root = kwargs.pop("repo_root", tmp_path)
    sites, parameters, published, facts = _twin(tmp_path, **kwargs)
    return gate.run(
        attempt=1,
        sites_path=sites,
        parameters_path=parameters,
        published=published,
        facts=facts,
        author_path=author_path,
        repo_root=repo_root,
        members=FEW_MEMBERS,
        **UNPINNED,
    )


# ── 1. pinning ──────────────────────────────────────────────────────────────────────────────────


def test_pinning_records_both_digests_and_says_it_compared_nothing(tmp_path: Path) -> None:
    sites, parameters, _, facts = _twin(tmp_path)
    _, record = gate.pinning_check(sites, parameters, facts=facts, **UNPINNED)
    assert record["sites"]["compared"] is False
    assert record["parameters"]["compared"] is False
    assert record["sites"]["content_hash"].startswith("sha256:")
    assert "recorded, not compared" in record["sites"]["comparison"]
    assert record["measured"] == {"data_rows": 33 + 3, "columns": 30, "reverse": 3}
    assert record["raw_newlines"] == 37


def test_pinning_fails_on_a_wrong_row_count(tmp_path: Path) -> None:
    sites, parameters, _, facts = _twin(tmp_path)
    wrong = gate.DepositFacts(facts.data_rows + 1, facts.columns, facts.reverse, facts.joined_ids)
    with pytest.raises(gate.GateError, match="not the file deposit_read counted"):
        gate.pinning_check(sites, parameters, facts=wrong, **UNPINNED)


def test_pinning_fails_on_a_wrong_reverse_count(tmp_path: Path) -> None:
    sites, parameters, _, facts = _twin(tmp_path)
    wrong = gate.DepositFacts(facts.data_rows, facts.columns, facts.reverse + 1, facts.joined_ids)
    with pytest.raises(gate.GateError, match="'reverse': 3"):
        gate.pinning_check(sites, parameters, facts=wrong, **UNPINNED)


def test_pinning_fails_on_a_declared_digest_that_differs(tmp_path: Path) -> None:
    sites, parameters, _, facts = _twin(tmp_path)
    declared = DepositFile("PXD032267", 2023, 5, "GlyGly__K_Sites.txt", "sha256:" + "0" * 64)
    with pytest.raises(gate.GateError, match="not the declared"):
        gate.pinning_check(
            sites,
            parameters,
            facts=facts,
            sites_deposit=declared,
            parameters_deposit=UNPINNED_PARAMETERS,
        )


def test_the_pinned_declaration_refuses_a_twin(tmp_path: Path) -> None:
    """With the real, pinned declarations as defaults, a file that is not the deposit raises."""
    sites, parameters, _, facts = _twin(tmp_path)
    with pytest.raises(gate.GateError, match="not the declared sha256:61c8fef0"):
        gate.pinning_check(sites, parameters, facts=facts)


# ── 4. the join ─────────────────────────────────────────────────────────────────────────────────


def _join(
    tmp_path: Path, extra: list[list[str]], claim: gate.PublishedClaim, ids: tuple[int, ...]
) -> Any:
    sites, _, _, _ = _twin(tmp_path)
    with sites.open("a", encoding="utf-8", newline="") as handle:
        csv.writer(handle, delimiter="\t", lineterminator="\n").writerows(extra)
    from bzk.adapters import maxquant

    table = maxquant.read_table(sites)
    return gate.join(table, gate.population(table), [claim], expected_ids=ids)


def _claim(
    name: str = "Gamma protein", probabilities: str = "GGGK(1)R", position: int = 40
) -> gate.PublishedClaim:
    return gate.PublishedClaim(name, position, probabilities, 0.01, 1.0)


FULL = np.full(12, 24.0)


def test_the_join_raises_on_zero_matches(tmp_path: Path) -> None:
    with pytest.raises(gate.GateError, match="neither key P nor key N"):
        _join(tmp_path, [], _claim(), (201,))


def test_the_join_raises_when_both_keys_find_two_rows(tmp_path: Path) -> None:
    twins = [
        _row(201, "Gamma protein", 40, "GGGK(1)R", FULL),
        _row(202, "Gamma protein", 40, "GGGK(1)R", FULL),
    ]
    with pytest.raises(gate.GateError, match="do not agree on one row"):
        _join(tmp_path, twins, _claim(), (201,))


def test_the_join_raises_on_an_id_mismatch(tmp_path: Path) -> None:
    with pytest.raises(gate.GateError, match="not deposit_read's"):
        _join(tmp_path, [_row(201, "Gamma protein", 40, "GGGK(1)R", FULL)], _claim(), (999,))


def test_the_join_raises_when_key_p_and_key_n_disagree(tmp_path: Path) -> None:
    rows = [
        _row(201, "Gamma protein", 40, "OTHERK(1)R", FULL),
        _row(202, "Delta protein", 40, "GGGK(1)R", FULL),
    ]
    with pytest.raises(gate.GateError, match="do not agree on one row"):
        _join(tmp_path, rows, _claim(), (201,))


def test_the_join_succeeds_when_only_one_key_matches(tmp_path: Path) -> None:
    """Key P misses on formatting (a probability written differently); key N alone is unique."""
    rows = [_row(201, "Gamma protein", 40, "GGGK(1.0)R", FULL)]
    _, record = _join(tmp_path, rows, _claim(), (201,))
    assert record[0]["key_p_ids"] == []
    assert record[0]["decided_by"] == ["N"]


def test_key_n_over_matching_beside_a_unique_key_p_joins_on_key_p(tmp_path: Path) -> None:
    """`Gamma protein` is contained in `Gamma protein-like 2`, so key N finds two rows."""
    rows = [
        _row(201, "Gamma protein", 40, "GGGK(1)R", FULL),
        _row(202, "Gamma protein-like 2", 40, "HHHK(1)R", FULL),
    ]
    _, record = _join(tmp_path, rows, _claim(), (201,))
    assert record[0]["key_n_ids"] == [201, 202]
    assert record[0]["joined_id"] == 201
    assert record[0]["decided_by"] == ["P"]


# ── 5. the valid-value rule ─────────────────────────────────────────────────────────────────────


def _claims(n: int) -> list[gate.PublishedClaim]:
    return [_claim(f"Claim {i}", f"C{i}K(1)", i) for i in range(n)]


def test_the_valid_value_rule_takes_the_strictest_candidate_retaining_every_claim() -> None:
    matrix = np.full((4, 12), 24.0)
    matrix[0, [0, 3, 6, 9]] = np.nan  # best cell holds 2: fails 3, passes 2
    matrix[1, :] = np.nan
    matrix[1, 0] = 24.0  # a non-claim row with one value: retained only at 1
    rule = gate.valid_value_choice(matrix, claim_rows=[0, 2], claims=_claims(2))
    assert rule["taken"] == 2
    assert rule["retains_every_claim"] is True
    assert rule["claims_lost"] == []
    assert [rule["candidates"][k]["rows_retained"] for k in ("3", "2", "1")] == [2, 3, 4]


def test_under_readout_d_a_claim_losing_every_value_takes_the_fallback_and_is_named() -> None:
    matrix = np.full((40, 12), np.nan)
    rng = np.random.default_rng(3)
    matrix[:, :] = rng.normal(24.0, 1.0, (40, 12))
    matched = np.zeros_like(matrix, dtype=bool)
    matched[5, :] = True  # every value of claim 1 came from matching
    claims = _claims(2)
    out = gate.readout_d(
        gate.licence_for_tests(1),
        matrix,
        matched,
        [3, 5],
        decimals=None,
        claims=claims,
        table_7={c.published_label: {"up": 0, "down": 0} for c in gate.COMPARISONS},
        members=FEW_MEMBERS,
        primary="T4",
        taken_before=3,
    )
    rule = out["valid_value_rule"]
    assert rule["retains_every_claim"] is False
    assert rule["claims_lost"] == [claims[1].label]
    assert out["valid_value_rule_changed"] is True
    assert out["cells_masked"] == 12
    assert out["readout_b"]["exposure"] == []


# ── 7. gate G ───────────────────────────────────────────────────────────────────────────────────


def test_one_gate_row_is_undeterminable_and_its_failing_input_check_is_recorded(
    tmp_path: Path,
) -> None:
    out = _run(tmp_path, complete_claims=1, difference_error=2e-5)
    g = out["gate_g"]
    assert g["status"] == "undeterminable"
    assert g["gate_rows"] == ["Alpha protein K10"]
    assert g["input_check"]["rows_checked"] == 1
    assert g["input_check"]["passed"] is False
    assert "variants" not in g
    assert out["readouts"] is None


def test_the_input_check_fails_on_a_2e_5_difference_error(tmp_path: Path) -> None:
    out = _run(tmp_path, difference_error=2e-5)
    assert out["gate_g"]["status"] == "input_not_reproduced"
    assert [r["passes"] for r in out["gate_g"]["input_check"]["rows"]] == [False, True]
    assert out["readouts"] is None


def test_two_variants_within_1e_4_are_not_separated_and_readouts_run_under_both(
    tmp_path: Path,
) -> None:
    """Equal WT spreads make Student's and Welch's t one number, so T4 and T5 both pass and sit
    within 1e-4 of each other on both gate rows. The tie is exact and table order takes T4."""
    out = _run(tmp_path)
    g = out["gate_g"]
    assert g["status"] == "not_separated"
    assert g["passing"] == ["T4", "T5"]
    assert g["primary"] == "T4"
    assert g["close_pairs"] == [["T4", "T5"]]
    assert list(out["readouts"]) == ["T4", "T5"]
    for variant in ("T4", "T5"):
        readouts = out["readouts"][variant]
        assert set(readouts) == {"variant", "readout_a", "readout_b", "readout_c"}
        assert readouts["readout_c"]["of"] == 20
    assert out["readout_d"]["variant"] == "T4"
    # `main()` writes this dict and is not run in the build turn: strict JSON, or this raises.
    json.dumps(out, allow_nan=False)


def test_a_close_pair_excluding_the_primary_is_still_not_separated() -> None:
    published = np.array([0.03, 0.02])
    p = {
        "T1": published + 2e-5,
        "T4": published - 9e-5,
        "T5": published - 9.5e-5,
    }
    scored = gate.score_variants(p, published)
    assert scored["primary"] == "T1"
    assert scored["close_pairs"] == [["T4", "T5"]]
    assert scored["status"] == "not_separated"
    assert scored["readout_variants"] == ["T1", "T4", "T5"]


def test_the_closest_fit_beats_table_order() -> None:
    published = np.array([0.03, 0.02])
    p = {"T1": published + 8e-5, "T2": published - 3e-5}
    scored = gate.score_variants(p, published)
    assert scored["passing"] == ["T1", "T2"]
    assert scored["primary"] == "T2"
    assert scored["status"] == "passed"
    assert scored["readout_variants"] == ["T2"]


def test_no_passing_variant_is_not_reproduced() -> None:
    published = np.array([0.03, 0.02])
    scored = gate.score_variants({"T1": published + 2e-4}, published)
    assert scored["status"] == "not_reproduced"
    assert scored["primary"] is None


# ── 8. readouts ─────────────────────────────────────────────────────────────────────────────────


def test_readout_a_reaches_each_verdict_and_near_is_measured_against_the_median() -> None:
    assert gate.readout_a_verdict(11, [10] * 10 + [12] * 10)["verdict"] == "reproduced"
    # Median 10, mean 19: 8 is within 25% of the median and far outside 25% of the mean.
    near = gate.readout_a_verdict(8, [10] * 11 + [30] * 9)
    assert (near["median"], near["verdict"]) == (10.0, "near")
    # Median 20, maximum 40: 42 is within 25% of the maximum and not of the median.
    assert gate.readout_a_verdict(42, [4] * 9 + [20] * 10 + [40])["verdict"] == "not reproduced"


def _supported(rows: int, unstable: int) -> dict[tuple[str, str], np.ndarray]:
    stable = np.zeros((rows, 20), dtype=bool)
    out = {(c.key, d): stable.copy() for c in gate.COMPARISONS for d in gate.DIRECTIONS}
    out[("wt_tac_vs_wt_control", "up")][:unstable, 0] = True
    return out


@pytest.mark.parametrize(
    ("exposure", "unstable", "outcome"),
    [(20, 1, "recurs"), (100, 1, "absent"), (100, 2, "indeterminate")],
)
def test_readout_b_sits_on_its_boundaries_at_exactly_5_and_1_percent(
    exposure: int, unstable: int, outcome: str
) -> None:
    claims = _claims(exposure)
    out = gate.readout_b(
        gate.licence_for_tests(1),
        supported=_supported(exposure, unstable),
        imputed=np.ones(exposure, dtype=bool),
        claim_rows=list(range(exposure)),
        claims=claims,
        family=None,
    )
    assert out["share"]["numerator"] == unstable
    assert out["share"]["denominator"] == exposure
    assert out["verdict"]["outcome"] == outcome
    assert out["power_flag"] == "n ≤ 10"


# ── the author configuration ────────────────────────────────────────────────────────────────────

AUTHOR = {"source": "synthetic", "date_received": "2026-11-07", "width_sd": 0.4, "seed": 3}


@pytest.mark.parametrize("key", ["randomisations", "scheme", "downshfit_sd"])
def test_an_unknown_author_parameter_key_is_refused_by_name(tmp_path: Path, key: str) -> None:
    path = tmp_path / "author.json"
    path.write_text(json.dumps({**AUTHOR, key: 1}), encoding="utf-8")
    with pytest.raises(gate.GateError, match=key):
        gate.read_author_parameters(path, repo_root=tmp_path)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "commit.gpgsign=false", *args], cwd=repo, check=True, capture_output=True
    )


def test_a_tracked_author_file_is_readout_as_primary_and_leaves_readout_bs_verdict(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    author = repo / "author.json"
    author.write_text(json.dumps(AUTHOR), encoding="utf-8")
    _git(repo, "add", "author.json")
    _git(repo, "commit", "-qm", "author")

    data = tmp_path / "data"
    data.mkdir()
    plain = _run(data)
    tracked = _run(data, author_path=author, repo_root=repo)
    assert tracked["author_parameters"]["used"] is True
    for variant in ("T4", "T5"):
        a = tracked["readouts"][variant]["readout_a"]
        b = tracked["readouts"][variant]["readout_b"]
        assert a["primary"] == "author_configuration"
        assert a["author_configuration"]["member"]["width_sd"] == 0.4
        assert "default_cell" in a
        assert "author_configuration_line" in b
        assert b["verdict"] == plain["readouts"][variant]["readout_b"]["verdict"]


def test_an_untracked_author_file_is_reported_and_ignored(tmp_path: Path) -> None:
    author = tmp_path / "author.json"
    author.write_text(json.dumps(AUTHOR), encoding="utf-8")
    out = _run(tmp_path, author_path=author)
    assert out["author_parameters"]["tracked_in_git"] is False
    assert out["author_parameters"]["used"] is False
    for variant in ("T4", "T5"):
        assert out["readouts"][variant]["readout_a"]["primary"] == "default_cell"
        assert "author_configuration" not in out["readouts"][variant]["readout_a"]
        assert "author_configuration_line" not in out["readouts"][variant]["readout_b"]


# ══ attempt 2 (walk/PREREG-PXD032267-gate-attempt2.md) ═════════════════════════════════════════
#
# Everything below is synthetic. No readout has ever been computed on the deposit, and nothing here
# computes one: the twins are written into `tmp_path`, and `main` runs only against a temporary
# fixtures directory or refuses before computing anything.

REGISTRATION_2 = (REPO_ROOT / "walk" / "PREREG-PXD032267-gate-attempt2.md").read_text(
    encoding="utf-8"
)
RESULT_1 = (REPO_ROOT / "walk" / "RESULT-PXD032267-gate-attempt1.md").read_text(encoding="utf-8")
LABEL = "second attempt, after a registration defect; test identified exploratorily"
WORDS_2 = {"three": 3, "four": 4}


def _section_2(number: int) -> str:
    match = re.search(rf"^## {number}\. .*?(?=^## |\Z)", REGISTRATION_2, re.DOTALL | re.MULTILINE)
    assert match is not None, f"attempt 2 has no section {number}"
    return match.group(0)


# ── the attempt switch, guarded against attempt 2's text ────────────────────────────────────────


def test_the_rounding_decimals_are_change_1s_and_section_6s() -> None:
    (change_1,) = _one(r"is rounded to \*\*(\w+) decimals\*\*, half to even", _section_2(2))
    attempt_1, attempt_2 = _one(
        r"It is `(\w+)` for attempt 1, so attempt 1's run reproduces\s+unchanged, and `(\d+)` for "
        r"attempt 2",
        _section_2(6),
    )
    assert attempt_1 == "None"
    assert WORDS_2[change_1] == int(attempt_2)
    assert dict(gate.ATTEMPT_ROUNDING_DECIMALS) == {1: None, 2: int(attempt_2)}


def test_the_attempt_2_tolerance_is_change_2s_sum_and_attempt_1s_is_input_tolerance() -> None:
    """The two terms are parsed separately and **summed**: `5e-7 + 1e-9` is not the float
    `5.01e-7`, and a constant written as the latter would fail here."""
    first, second = _one(
        rf"\*\*Change 2: the input-check tolerance is {NUMBER} \+ {NUMBER}\.\*\*", _section_2(2)
    )
    assert gate.ATTEMPT_INPUT_TOLERANCE[2] == float(first) + float(second)
    assert float(first) + float(second) != 5.01e-7
    assert gate.ATTEMPT_INPUT_TOLERANCE[1] is gate.INPUT_TOLERANCE


def test_check_2s_row_count_and_check_3s_sole_variant_are_section_3s() -> None:
    (rows,) = _one(r"The input check passes on all (\w+) gate rows", _section_2(3))
    (variant,) = _one(r"Gate G passes, with \*\*(T\d) the only passing variant\*\*", _section_2(3))
    assert WORDS_2[rows] == gate.ATTEMPT2_GATE_ROWS
    assert variant == gate.ATTEMPT2_SOLE_VARIANT
    assert variant in gate.GATE_VARIANTS


def test_the_label_is_section_4s_read_across_its_line_break() -> None:
    """Italic in §4 and wrapped across a line break: a literal single-line search finds nothing,
    which is why the module normalises whitespace."""
    assert gate.attempt2_label() == LABEL
    assert LABEL not in REGISTRATION_2
    assert LABEL in " ".join(_section_2(4).split())


def test_the_exploratory_values_are_read_from_attempt_1s_verbatim_block() -> None:
    """Read, never retyped. Each value is found again on its own variant's line of the block."""
    values = gate.exploratory_max_abs_delta_p()
    assert tuple(values) == gate.GATE_VARIANTS
    (block,) = re.findall(r"Output,\s+verbatim:\s*\n```\n(.*?)\n```", RESULT_1, re.DOTALL)
    for variant, value in values.items():
        (line,) = [x for x in block.splitlines() if x.strip().startswith(f"{variant}: ")]
        assert f"max|dp|={value:.2e}" in line


def test_the_attempt_constants_refuse_assignment() -> None:
    for constant in (gate.ATTEMPT_ROUNDING_DECIMALS, gate.ATTEMPT_INPUT_TOLERANCE):
        with pytest.raises(TypeError):
            cast(Any, constant)[2] = 0
    assert gate.ATTEMPT_ROUNDING_DECIMALS[2] == 4


# ── licences ────────────────────────────────────────────────────────────────────────────────────

LICENSED = ("readouts_for", "readout_a", "readout_b", "readout_c", "readout_d")


def test_every_readout_entry_point_takes_a_licence_first_and_no_helper_does() -> None:
    for name in LICENSED:
        first = next(iter(inspect.signature(getattr(gate, name)).parameters.values()))
        assert (first.name, first.kind) == ("licence", inspect.Parameter.POSITIONAL_OR_KEYWORD)
        assert first.default is inspect.Parameter.empty
    for name in ("support", "run_members", "readout_a_verdict"):
        assert "licence" not in inspect.signature(getattr(gate, name)).parameters
        assert "takes no licence" in (getattr(gate, name).__doc__ or "")


def test_a_licence_cannot_be_constructed_altered_or_copied() -> None:
    for kind in (gate.Attempt1Status, gate.ConsistencyPassed):
        with pytest.raises(TypeError, match="minted"):
            kind()
    licence = gate.licence_for_tests(2)
    with pytest.raises(AttributeError, match="immutable"):
        cast(Any, licence).decimals = None
    with pytest.raises(AttributeError, match="immutable"):
        copy.copy(licence)
    assert (licence.attempt, licence.decimals, licence.issued_by) == (2, 4, "tests")
    assert licence.label == LABEL


def _readout_d_inputs() -> dict[str, Any]:
    rng = np.random.default_rng(3)
    return {
        "matrix": np.round(rng.normal(24.0, 1.0, (40, 12)), 4),
        "matched": np.zeros((40, 12), dtype=bool),
        "claim_rows": [3, 5],
        "claims": _claims(2),
        "table_7": {c.published_label: {"up": 0, "down": 0} for c in gate.COMPARISONS},
        "members": FEW_MEMBERS,
        "primary": "T1",
        "taken_before": 3,
    }


@pytest.mark.parametrize(("attempt", "decimals"), [(1, 4), (2, None)])
def test_readout_d_given_a_licence_for_other_decimals_raises(
    attempt: int, decimals: int | None
) -> None:
    inputs = _readout_d_inputs()
    with pytest.raises(gate.InstrumentFault, match=f"handed data at decimals={decimals}"):
        gate.readout_d(
            gate.licence_for_tests(attempt),
            inputs.pop("matrix"),
            inputs.pop("matched"),
            inputs.pop("claim_rows"),
            decimals=decimals,
            **inputs,
        )


@pytest.mark.parametrize(("attempt", "decimals"), [(1, 4), (2, None)])
def test_readouts_for_given_a_licence_for_other_decimals_raises(
    attempt: int, decimals: int | None
) -> None:
    inputs = _readout_d_inputs()
    prepared = gate.prepare(
        inputs["matrix"], inputs["claim_rows"], inputs["claims"], decimals=decimals
    )
    with pytest.raises(gate.InstrumentFault, match=f"handed data at decimals={decimals}"):
        gate.readouts_for(
            gate.licence_for_tests(attempt),
            prepared,
            "T1",
            claims=inputs["claims"],
            table_7=inputs["table_7"],
            members=FEW_MEMBERS,
            author=None,
        )


# The private mint names are built from parts, so this file's own source never matches them.
MINT = "_" + "mint" + "_"
CONSISTENCY_CALL = "consistency" + "_checks("
ALLOWED_MINT_SITES = {
    MINT + "attempt1": {"run"},
    MINT + "consistency": {"consistency" + "_checks"},
    MINT + "licence": {MINT + "attempt1", MINT + "consistency", "licence_for_tests"},
    "consistency" + "_checks": {"run"},
}
GUARDED_ROOTS = ("bzk", "tests", "notes/scripts")
GATE_MODULE = "bzk/sources/pxd032267_gate.py"
#: The test factory mints real licences, so it is allowed in this file alone — where
#: `test_the_test_factory_is_used_only_by_direct_readout_tests` limits it further.
FACTORY = "licence_for" + "_tests"
FACTORY_ALLOWED = {GATE_MODULE, "tests/test_pxd032267_gate.py"}


def _licence_site_violations(module_source: str, others: dict[str, str]) -> list[str]:
    """Every use of a mint name, or a call of §3's checks, outside the sites allowed for it.

    In the module, by AST: each reference's innermost enclosing function must be one allowed for
    that name; definitions are allowed. Everywhere else, by text: any occurrence is a violation.
    """
    found: list[str] = []

    def visit(node: ast.AST, scope: str | None) -> None:
        for child in ast.iter_child_nodes(node):
            inner = scope
            if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef):
                inner = child.name
            names = []
            if isinstance(child, ast.Name):
                names.append(child.id)
            elif isinstance(child, ast.Attribute):
                names.append(child.attr)
            for name in names:
                if name.startswith(MINT) and name not in ALLOWED_MINT_SITES:
                    found.append(f"{GATE_MODULE}: unknown mint {name} in {scope}")
                elif name in ALLOWED_MINT_SITES and scope not in ALLOWED_MINT_SITES[name]:
                    found.append(f"{GATE_MODULE}: {name} referenced in {scope}")
            visit(child, inner)

    visit(ast.parse(module_source), None)
    for path, text in sorted(others.items()):
        if MINT in text:
            found.append(f"{path}: names a private mint")
        if CONSISTENCY_CALL in text:
            found.append(f"{path}: calls §3's checks")
        if FACTORY in text and path not in FACTORY_ALLOWED:
            found.append(f"{path}: uses the test factory")
    return found


def _guarded_texts() -> dict[str, str]:
    """Every file under the guarded roots except the module itself. `notes/prompts/` is not a
    guarded root: it names the mints in prose."""
    texts: dict[str, str] = {}
    for root in GUARDED_ROOTS:
        for directory, subdirectories, files in os.walk(REPO_ROOT / root):
            subdirectories[:] = [d for d in subdirectories if d != "__pycache__"]
            for name in files:
                path = Path(directory) / name
                relative = path.relative_to(REPO_ROOT).as_posix()
                if relative != GATE_MODULE:
                    texts[relative] = path.read_bytes().decode("utf-8", errors="replace")
    return texts


def test_the_mints_are_used_only_at_their_allowed_sites() -> None:
    module = (REPO_ROOT / GATE_MODULE).read_text(encoding="utf-8")
    assert _licence_site_violations(module, _guarded_texts()) == []


def test_the_licence_site_guard_fails_on_planted_uses() -> None:
    planted_module = (
        f"def {MINT}attempt1(): pass\n"
        f"def run(): {MINT}attempt1()\n"
        f"def readout_d(): {MINT}attempt1()\n"
        f"def readout_a(): object.__new__({MINT}forged)\n"
    )
    planted_other = {
        "notes/scripts/planted.py": f"licence = gate.{MINT}consistency()\n",
        "notes/scripts/readouts_on_real_data.py": f"licence = gate.{FACTORY}(2)\n",
    }
    assert _licence_site_violations(planted_module, planted_other) == [
        f"{GATE_MODULE}: {MINT}attempt1 referenced in readout_d",
        f"{GATE_MODULE}: unknown mint {MINT}forged in readout_a",
        "notes/scripts/planted.py: names a private mint",
        "notes/scripts/readouts_on_real_data.py: uses the test factory",
    ]


RUN_LEVEL = {"_run", "_run2", "_main2", "run", "main"}


def test_the_test_factory_is_used_only_by_direct_readout_tests() -> None:
    """A test that calls `licence_for_tests` must not reach `run()` or `main()`, directly or
    through this file's helpers, and no helper here may use the factory."""
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    offenders = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        called = {
            c.func.attr if isinstance(c.func, ast.Attribute) else getattr(c.func, "id", "")
            for c in ast.walk(node)
            if isinstance(c, ast.Call)
        }
        if "licence_for_tests" in called and (
            called & RUN_LEVEL or not node.name.startswith("test_")
        ):
            offenders.append(node.name)
    assert offenders == []


# ── the attempt-2 twin: three gate rows, values with more than four decimals ────────────────────


def _twin3(
    tmp_path: Path,
    *,
    published_variant: str = "T1",
    difference_error: float = 0.0,
) -> tuple[Path, Path, gate.Published, gate.DepositFacts, dict[str, np.ndarray]]:
    """A site table whose published Table 8 was computed **from four-decimal log2 values**.

    Attempt 2's export model, made physical: every claim's log2 values carry many decimals, the
    published `Difference` and `p_value` are computed from them rounded with `np.round(_, 4)` and
    then printed to six decimals, under `published_variant`. Three claims are complete in all
    twelve samples — three gate rows, as the deposit has — and filamin-C K2590 lacks one WT
    control value. `_twin` (two gate rows) is left as it was.
    """
    tmp_path.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(11)
    lines = []
    for i in range(1, 13):
        values = rng.normal(24.0, 0.3, 12)
        values[rng.random(12) < 0.12] = np.nan
        lines.append(_row(i, f"Background protein {i}", 7 * i, f"PEPK(1)R{i}", values))
    for i in range(31, 34):
        lines.append(_row(i, "Decoy", 1, "DECOYK(1)", rng.normal(20.0, 1.0, 12), reverse=True))

    def claim(control: float, tac: float, spread: float, ko: tuple[float, ...]) -> np.ndarray:
        out = np.empty(12)
        out[WT_C] = control + np.array([-spread, 0.0, spread * 1.3])
        out[WT_T] = tac + np.array([-spread * 0.7, 0.0, spread])
        out[KO_C] = 23.0 + np.array(ko)
        out[KO_T] = 23.5 + np.array(ko[::-1]) * 1.7
        return out + rng.uniform(-0.01, 0.01, 12)

    values_by_claim = {
        "Alpha protein": claim(22.0, 24.0, 0.3, (-1.0, 0.1, 1.2)),
        "Beta protein": claim(21.0, 22.5, 0.5, (-0.8, 0.3, 0.9)),
        "Gamma protein": claim(20.0, 21.6, 0.45, (-0.5, 0.2, 0.6)),
        "Filamin-C": claim(20.5, 22.0, 0.4, (-0.6, 0.2, 0.7)),
    }
    values_by_claim["Filamin-C"][WT_C.start] = np.nan
    claims_data = [
        (101, "Alpha protein", 10, "AAAK(1)R"),
        (102, "Beta protein", 20, "BBBK(1)R"),
        (103, "Gamma protein", 30, "CCCK(1)R"),
        (104, "Filamin-C", 2590, "YGGK(0.997)AK(0.003)"),
    ]
    for ident, name, position, probabilities in claims_data:
        lines.append(_row(ident, name, position, probabilities, values_by_claim[name]))

    sites = tmp_path / "GlyGly__K_Sites.txt"
    with sites.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(HEADER)
        writer.writerows(lines)
    parameters = tmp_path / "parameters.txt"
    parameters.write_text("Version\t2.0.3.0\n", encoding="utf-8")

    published_claims = []
    for _, name, position, probabilities in claims_data:
        row = np.round(values_by_claim[name], 4).reshape(1, -1)
        difference = float(np.nanmean(row[0, WT_T]) - np.nanmean(row[0, WT_C]))
        p = 0.5
        if not np.isnan(row).any():
            p = float(
                tukey(row, gate.GENOTYPE, gate.SURGERY, variants=(published_variant,))
                .pair("WT:TAC", "WT:control")
                .p[published_variant][0]
            )
        published_claims.append(
            gate.PublishedClaim(
                protein_name=name,
                position=position,
                glygly_probabilities=probabilities,
                p_value=round(p, 6),
                difference=round(difference, 6)
                + (difference_error if name == "Alpha protein" else 0.0),
            )
        )
    published = gate.Published(
        claims=tuple(published_claims),
        table_7={c.published_label: {"up": 1, "down": 1} for c in gate.COMPARISONS},
        source_sha256="synthetic",
    )
    facts = gate.DepositFacts(
        data_rows=len(lines), columns=len(HEADER), reverse=3, joined_ids=(101, 102, 103, 104)
    )
    return sites, parameters, published, facts, values_by_claim


#: The family for the three-row twin: one member off the default cell. T1's p is costly, and the
#: default cell's twenty draws run regardless.
ONE_MEMBER = (Member(0.2, 1.6, "whole_matrix", 0),)


def _inputs3(tmp_path: Path, **kwargs: Any) -> dict[str, Any]:
    """`run()`'s keyword arguments for the three-row twin, its reference included."""
    reference = kwargs.pop("reference", None)
    sites, parameters, published, facts, _ = _twin3(tmp_path, **kwargs)
    common = {
        "sites_path": sites,
        "parameters_path": parameters,
        "published": published,
        "facts": facts,
        "author_path": tmp_path / "no-author.json",
        "repo_root": tmp_path,
        "members": ONE_MEMBER,
        **UNPINNED,
    }
    if reference is None:
        reference = _reference(tmp_path, common)
    return {**common, "reference_fixture": reference}


def _reference(tmp_path: Path, common: dict[str, Any], **changes: Any) -> Path:
    """Attempt 1's fixture for a twin, written as `main` wrote the real one: an attempt-1 run of
    the same files, unrounded — which, like the deposit, does not reproduce its input."""
    out = gate.run(attempt=1, **common)
    reference = {
        "sites_content_hash": out["pinning"]["sites"]["content_hash"],
        "parameters_content_hash": out["pinning"]["parameters"]["content_hash"],
        **out,
    }
    for dotted, value in changes.items():
        *parents, leaf = dotted.split(".")
        target = reference
        for key in parents:
            target = target[key]
        target[leaf] = value
    path = tmp_path / "reference.json"
    path.write_text(json.dumps(reference), encoding="utf-8")
    return path


def _run2(tmp_path: Path, **kwargs: Any) -> dict[str, Any]:
    on_licence = kwargs.pop("on_licence", None)
    output = kwargs.pop("output", None)
    return gate.run(attempt=2, **_inputs3(tmp_path, **kwargs), on_licence=on_licence, output=output)


def _counting(calls: collections.Counter[str], name: str, real: Any) -> Any:
    def counted(*args: Any, **kw: Any) -> Any:
        calls[name] += 1
        return real(*args, **kw)

    return counted


def _spy(monkeypatch: pytest.MonkeyPatch) -> collections.Counter[str]:
    """A counting spy on every licence-taking function."""
    calls: collections.Counter[str] = collections.Counter()
    for name in LICENSED:
        monkeypatch.setattr(gate, name, _counting(calls, name, getattr(gate, name)))
    return calls


def test_the_twins_reference_is_attempt_1s_shape_input_not_reproduced(tmp_path: Path) -> None:
    """The attempt-1 run of the three-row twin fails its input check, as the deposit's did, and
    computes no readout — so the reference costs nothing and mirrors the real one."""
    inputs = _inputs3(tmp_path)
    reference = json.loads(inputs["reference_fixture"].read_text(encoding="utf-8"))
    assert reference["gate_g"]["status"] == "input_not_reproduced"
    assert reference["gate_g"]["gate_row_count"] == 3
    assert reference["readouts"] is None
    assert "consistency" not in reference


@pytest.fixture(scope="module")
def passing2(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[dict[str, Any], list[gate.ReadoutLicence]]:
    """One passing attempt-2 run of the three-row twin, shared by the tests that only read it:
    T1's studentised-range p costs milliseconds a value, and the readouts need many."""
    licences: list[gate.ReadoutLicence] = []
    out = _run2(tmp_path_factory.mktemp("passing2"), on_licence=licences.append)
    return out, licences


def test_attempt_2_passes_section_3_on_its_twin_and_runs_under_t1_alone(
    passing2: tuple[dict[str, Any], list[gate.ReadoutLicence]],
) -> None:
    out, licences = passing2
    consistency = out["consistency"]
    assert consistency["passed"] is True
    assert [c["passed"] for c in consistency["checks"].values()] == [True, True, True]
    assert consistency["checks"]["3"]["inputs"]["passing"] == ["T1"]
    assert out["gate_g"]["status"] == "passed"
    assert out["gate_g"]["input_check"]["tolerance"] == gate.ATTEMPT_INPUT_TOLERANCE[2]
    assert list(out["readouts"]) == ["T1"]
    assert out["readout_d"]["variant"] == "T1"
    (licence,) = licences
    assert isinstance(licence, gate.ConsistencyPassed)
    assert (licence.attempt, licence.decimals, licence.issued_by) == (2, 4, "run")
    json.dumps(out, allow_nan=False)


def test_check_3_reports_every_variant_beside_its_exploratory_value(
    passing2: tuple[dict[str, Any], list[gate.ReadoutLicence]],
) -> None:
    variants = passing2[0]["consistency"]["checks"]["3"]["inputs"]["variants"]
    exploratory = gate.exploratory_max_abs_delta_p()
    assert tuple(variants) == gate.GATE_VARIANTS
    for variant, record in variants.items():
        assert record["exploratory_max_abs_delta_p"] == exploratory[variant]
        assert record["max_abs_delta_p"] is not None


def _on_grid(values: np.ndarray) -> bool:
    finite = values[~np.isnan(values)]
    return finite.size > 0 and bool(np.array_equal(finite, np.round(finite, 4)))


def test_rounding_reaches_every_use_of_the_values_and_never_the_draws(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Under attempt 2: the input check, the valid-value rule, imputation's input and readout D's
    masked matrix all see four-decimal values; imputed draws carry more than four decimals."""
    seen: dict[str, list[Any]] = collections.defaultdict(list)

    def recording(name: str, real: Any) -> Any:
        def recorded(*args: Any, **kw: Any) -> Any:
            result = real(*args, **kw)
            seen[name].append((args[0], result))
            return result

        return recorded

    _, _, _, _, values = _twin3(tmp_path / "raw")
    raw = np.array(list(values.values()))
    assert not _on_grid(raw)  # the twin is not already on the grid, or this test proves nothing
    inputs = _inputs3(tmp_path)  # writes the reference, an attempt-1 run, before the spies
    for name in ("valid_value_choice", "prepare", "downshifted_normal"):
        monkeypatch.setattr(gate, name, recording(name, getattr(gate, name)))

    out = gate.run(attempt=2, **inputs)

    alpha = np.round(values["Alpha protein"], 4)
    expected = float(alpha[WT_T].mean() - alpha[WT_C].mean())
    unrounded = float(values["Alpha protein"][WT_T].mean() - values["Alpha protein"][WT_C].mean())
    computed = out["gate_g"]["input_check"]["rows"][0]["computed_difference"]
    assert abs(computed - expected) < 1e-12
    assert abs(computed - unrounded) > 1e-7

    assert [_on_grid(m) for m, _ in seen["valid_value_choice"]] == [True, True]
    (run_prepare, d_prepare) = seen["prepare"]
    assert _on_grid(run_prepare[0]) and _on_grid(d_prepare[0])
    assert d_prepare[1].decimals == 4
    assert seen["downshifted_normal"]
    for matrix, filled in seen["downshifted_normal"]:
        assert _on_grid(matrix)
        drawn = filled.values[np.isnan(matrix)]
        assert drawn.size > 0
        assert bool(np.all(drawn != np.round(drawn, 4)))


def test_attempt_1_on_the_same_twin_does_not_round(tmp_path: Path) -> None:
    inputs = _inputs3(tmp_path)
    inputs.pop("reference_fixture")
    _, _, _, _, values = _twin3(tmp_path / "raw")
    out = gate.run(attempt=1, **inputs)
    alpha = values["Alpha protein"]
    computed = out["gate_g"]["input_check"]["rows"][0]["computed_difference"]
    assert abs(computed - float(alpha[WT_T].mean() - alpha[WT_C].mean())) < 1e-9
    assert out["gate_g"]["input_check"]["tolerance"] == gate.INPUT_TOLERANCE
    assert "consistency" not in out


# ── §3 failures: recorded, every check, and no licence ──────────────────────────────────────────


def _tampered_reference(tmp_path: Path, **changes: Any) -> Path:
    inputs = _inputs3(tmp_path / "base")
    common = {k: v for k, v in inputs.items() if k != "reference_fixture"}
    return _reference(tmp_path / "base", common, **changes)


FAILING_TWINS: dict[str, dict[str, Any]] = {
    "1": {"reference_changes": {"valid_value_rule.rows_reaching_imputation": 0}},
    "2": {"difference_error": 1e-6},
    "3": {"published_variant": "T4"},
}


def _failing_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, checks: str
) -> tuple[gate.InstrumentFault, dict[str, Any], collections.Counter[str], list[Any], int]:
    kwargs: dict[str, Any] = {}
    for check in checks:
        twin = dict(FAILING_TWINS[check])
        changes = twin.pop("reference_changes", None)
        if changes is not None:
            kwargs["reference"] = _tampered_reference(tmp_path, **changes)
        kwargs.update(twin)
    calls = _spy(monkeypatch)
    licences: list[Any] = []
    output: dict[str, Any] = {}
    issued = gate.licences_issued()
    with pytest.raises(gate.InstrumentFault) as raised:
        _run2(tmp_path, on_licence=licences.append, output=output, **kwargs)
    return raised.value, output, calls, licences, gate.licences_issued() - issued


@pytest.mark.parametrize("check", ["1", "2", "3"])
def test_each_check_fails_on_its_own_twin_and_no_readout_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, check: str
) -> None:
    fault, output, calls, licences, minted = _failing_run(tmp_path, monkeypatch, check)
    block = fault.consistency
    assert block is not None
    assert block["failed"] == [check]
    assert set(block["checks"]) == {"1", "2", "3"}
    assert output["consistency"] is block
    assert output["readouts"] is None and output["readout_d"] is None
    assert sum(calls.values()) == 0
    assert licences == []
    assert minted == 0


def test_all_three_checks_fail_together_and_all_three_are_recorded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fault, _, calls, licences, minted = _failing_run(tmp_path, monkeypatch, "123")
    block = fault.consistency
    assert block is not None
    assert block["failed"] == ["1", "2", "3"]
    checks = block["checks"]
    assert checks["1"]["reason"] == "differ from the reference: rows_reaching_imputation"
    assert checks["2"]["conditions"]["every_gate_row_passes"] is False
    # Check 3 still has scores of its own although gate_g, failing its input check, made none.
    assert checks["3"]["inputs"]["gate_g_scored"] is False
    assert checks["3"]["inputs"]["scored_here"] is True
    assert checks["3"]["inputs"]["passing"] == ["T4"]
    assert checks["3"]["conditions"]["t1_the_only_passing_variant"] is False
    assert sum(calls.values()) == 0
    assert licences == []
    assert minted == 0


def test_checks_1_and_2_read_the_committed_attempt_1_fixture() -> None:
    """The real reference, read by the same code, against sources independent of it: the digests
    pinned in `bzk/sources/pride.py`, the walk record's ids, and the attempt-1 result's counts
    (taken 3, 1,131 rows). Reads a committed file; computes nothing on the deposit."""
    reference = json.loads(gate.REFERENCE_FIXTURE.read_text(encoding="utf-8"))
    pinning = {
        "sites": {"content_hash": PXD032267_SITES.expected_content_hash},
        "parameters": {"content_hash": PXD032267_PARAMETERS.expected_content_hash},
    }
    joined = [{"joined_id": i} for i in gate.load_deposit_facts().joined_ids]
    check = gate._check_reproduced(
        reference, pinning, joined, {"taken": 3, "rows_reaching_imputation": 1131}
    )
    assert check["passed"] is True, check["reason"]
    check_2 = gate._check_input(reference, reference["gate_g"])
    assert len(check_2["inputs"]["reference_gate_rows"]) == gate.ATTEMPT2_GATE_ROWS
    # Attempt 1's own gate block, at attempt 1's tolerance, fails check 2 on both counts it should.
    assert check_2["conditions"]["tolerance_is_change_2s"] is False
    assert check_2["conditions"]["every_gate_row_passes"] is False
    assert check_2["conditions"]["gate_rows_equal_the_reference"] is True


def test_check_2_fails_when_the_gate_rows_differ_from_the_references_although_all_pass(
    tmp_path: Path,
) -> None:
    reference = _tampered_reference(
        tmp_path,
        **{"gate_g.gate_rows": ["Alpha protein K10", "Beta protein K20", "Filamin-C K2590"]},
    )
    with pytest.raises(gate.InstrumentFault) as raised:
        _run2(tmp_path, reference=reference)
    block = raised.value.consistency
    assert block is not None
    assert block["failed"] == ["2"]
    conditions = block["checks"]["2"]["conditions"]
    assert conditions["gate_rows_equal_the_reference"] is False
    assert conditions["every_gate_row_passes"] is True
    assert conditions["three_gate_rows"] is True


def _scores_with(monkeypatch: pytest.MonkeyPatch, change: Any, *, on_call: int | None) -> None:
    real = gate.gate_scores
    count = [0]

    def changed(gate_matrix: np.ndarray, published_p: np.ndarray) -> dict[str, Any]:
        count[0] += 1
        scores = real(gate_matrix, published_p)
        return change(scores) if on_call in (None, count[0]) else scores

    monkeypatch.setattr(gate, "gate_scores", changed)


def test_the_t1_only_check_fails_when_a_second_variant_also_passes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """T2 is made to pass beside T1 without a close pair, so G's status is still `passed`: only
    the sole-variant condition can fail it."""

    def second(scores: dict[str, Any]) -> dict[str, Any]:
        scores["variants"]["T2"]["passes"] = True
        scores["passing"] = ["T1", "T2"]
        return scores

    _scores_with(monkeypatch, second, on_call=None)
    with pytest.raises(gate.InstrumentFault) as raised:
        _run2(tmp_path)
    block = raised.value.consistency
    assert block is not None
    assert block["failed"] == ["3"]
    conditions = block["checks"]["3"]["conditions"]
    assert conditions == {
        "g_passes_on_these_scores": True,
        "t1_the_only_passing_variant": False,
        "scores_equal_gate_gs": True,
    }


def test_a_mismatch_between_gate_g_and_check_3s_scores_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The second call of `gate_scores` — check 3's — is perturbed; gate_g's is not."""

    def perturbed(scores: dict[str, Any]) -> dict[str, Any]:
        scores["variants"]["T1"]["max_abs_delta_p"] += 1e-12
        return scores

    _scores_with(monkeypatch, perturbed, on_call=2)
    calls = _spy(monkeypatch)
    with pytest.raises(gate.InstrumentFault, match="check\\(s\\) 3 failed") as raised:
        _run2(tmp_path)
    block = raised.value.consistency
    assert block is not None
    assert block["checks"]["3"]["conditions"]["scores_equal_gate_gs"] is False
    assert "disagrees with itself" in block["checks"]["3"]["reason"]
    assert sum(calls.values()) == 0


# ── labels ──────────────────────────────────────────────────────────────────────────────────────


def _readout_blocks(out: dict[str, Any]) -> dict[str, dict[str, Any]]:
    blocks: dict[str, dict[str, Any]] = {"consistency": out["consistency"]}
    for variant, under in out["readouts"].items():
        blocks[f"{variant}"] = under
        blocks[f"{variant} A"] = under["readout_a"]
        blocks[f"{variant} A default cell"] = under["readout_a"]["default_cell"]
        blocks[f"{variant} B"] = under["readout_b"]
        blocks[f"{variant} B secondaries"] = under["readout_b"]["secondary"]
        blocks[f"{variant} C"] = under["readout_c"]
    d = out["readout_d"]
    blocks["D"] = d
    blocks["D A"] = d["readout_a"]
    blocks["D A default cell"] = d["readout_a"]["default_cell"]
    blocks["D B"] = d["readout_b"]
    blocks["D B secondaries"] = d["readout_b"]["secondary"]
    return blocks


def test_the_label_is_on_every_attempt_2_block(
    passing2: tuple[dict[str, Any], list[gate.ReadoutLicence]],
) -> None:
    blocks = _readout_blocks(passing2[0])
    assert len(blocks) == 12
    assert {name: block.get("label") for name, block in blocks.items()} == dict.fromkeys(
        blocks, LABEL
    )


def test_attempt_1_carries_no_label(tmp_path: Path) -> None:
    out = _run(tmp_path)
    assert "consistency" not in out
    assert "label" not in json.dumps(out)


# ── main: refusals, faults and the started marker ───────────────────────────────────────────────


def _never() -> dict[str, Any]:
    raise AssertionError("main computed or fetched something before refusing")


def test_main_requires_attempt() -> None:
    with pytest.raises(SystemExit):
        gate.main([], inputs=_never)


def test_main_attempt_1_refuses_because_its_fixture_exists(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert (gate.FIXTURES_DIR / gate.FIXTURE_NAME).exists()
    assert gate.main(["--attempt", "1"], inputs=_never) == 2
    assert "attempt 1 is on the record" in capsys.readouterr().err


@pytest.mark.parametrize(
    "existing", ["pxd032267_gate_attempt2.json", "pxd032267_gate_attempt2.started.json"]
)
def test_main_attempt_2_refuses_when_its_fixture_or_its_marker_exists(
    tmp_path: Path, existing: str
) -> None:
    (tmp_path / existing).write_text("{}\n", encoding="utf-8")
    assert gate.main(["--attempt", "2"], fixtures_dir=tmp_path, inputs=_never) == 2


def _main2(tmp_path: Path, fixtures: Path, **kwargs: Any) -> int:
    inputs = _inputs3(tmp_path, **kwargs)
    return gate.main(["--attempt", "2"], fixtures_dir=fixtures, inputs=lambda: dict(inputs))


def test_main_attempt_2_writes_its_fixture_once_and_then_refuses(tmp_path: Path) -> None:
    fixtures = tmp_path / "fixtures"
    assert _main2(tmp_path, fixtures) == 0
    fixture = json.loads((fixtures / gate.FIXTURE_NAME_ATTEMPT2).read_text(encoding="utf-8"))
    assert fixture["registration"] == "walk/PREREG-PXD032267-gate-attempt2.md"
    assert fixture["governing_registration"] == "walk/PREREG-PXD032267-gate.md"
    assert (fixture["attempt"], fixture["rounding_decimals"]) == (2, 4)
    assert fixture["input_tolerance"] == 5e-7 + 1e-9
    assert fixture["label"] == LABEL
    assert fixture["reference_fixture_sha256"].startswith("sha256:")
    assert fixture["consistency"]["passed"] is True
    assert _readout_blocks(fixture)["D B secondaries"]["label"] == LABEL
    marker = json.loads((fixtures / gate.STARTED_NAME_ATTEMPT2).read_text(encoding="utf-8"))
    assert marker["state"] == "completed"
    assert marker["sites_content_hash"] == fixture["sites_content_hash"]
    assert not (fixtures / gate.FAULTS_NAME_ATTEMPT2).exists()
    assert gate.main(["--attempt", "2"], fixtures_dir=fixtures, inputs=_never) == 2


def test_main_attempt_2_records_section_3_failures_as_faults_and_writes_no_fixture(
    tmp_path: Path,
) -> None:
    fixtures = tmp_path / "fixtures"
    for _ in range(2):
        assert _main2(tmp_path, fixtures, published_variant="T4") == 1
    faults = json.loads((fixtures / gate.FAULTS_NAME_ATTEMPT2).read_text(encoding="utf-8"))
    assert len(faults) == 2
    for fault in faults:
        assert fault["stage"] == "attempt 2 §3: the consistency checks"
        assert fault["consistency"]["failed"] == ["3"]
        assert fault["readouts_computed"] is False
        assert fault["fixed_by_commit"] is None
    assert not (fixtures / gate.FIXTURE_NAME_ATTEMPT2).exists()
    assert not (fixtures / gate.STARTED_NAME_ATTEMPT2).exists()


def test_main_attempt_2_records_a_pinning_failure_before_section_3_as_a_fault(
    tmp_path: Path,
) -> None:
    fixtures = tmp_path / "fixtures"
    inputs = _inputs3(tmp_path)
    facts = inputs["facts"]
    inputs["facts"] = gate.DepositFacts(
        facts.data_rows + 1, facts.columns, facts.reverse, facts.joined_ids
    )
    assert gate.main(["--attempt", "2"], fixtures_dir=fixtures, inputs=lambda: inputs) == 1
    (fault,) = json.loads((fixtures / gate.FAULTS_NAME_ATTEMPT2).read_text(encoding="utf-8"))
    assert fault["stage"] == "before §3: pinning, the join, or reading the inputs"
    assert fault["exception"]["type"] == "GateError"
    assert fault["consistency"] is None


def test_an_exception_in_readout_d_is_written_into_the_marker_and_blocks_a_repeat(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def broken(*args: Any, **kwargs: Any) -> dict[str, Any]:
        raise RuntimeError("planted inside readout D")

    monkeypatch.setattr(gate, "readout_d", broken)
    fixtures = tmp_path / "fixtures"
    assert _main2(tmp_path, fixtures) == 1
    marker = json.loads((fixtures / gate.STARTED_NAME_ATTEMPT2).read_text(encoding="utf-8"))
    assert marker["state"] == "ended by an exception after readouts started"
    assert marker["exception"]["type"] == "RuntimeError"
    assert marker["exception"]["message"] == "planted inside readout D"
    completed = marker["completed"]["readouts"]
    assert list(completed) == ["T1"]
    assert {"readout_a", "readout_b", "readout_c"} <= set(completed["T1"])
    assert completed["T1"]["readout_c"]["of"] == 20
    assert marker["completed"]["readout_d"] == {}
    assert not (fixtures / gate.FIXTURE_NAME_ATTEMPT2).exists()
    assert not (fixtures / gate.FAULTS_NAME_ATTEMPT2).exists()
    assert gate.main(["--attempt", "2"], fixtures_dir=fixtures, inputs=_never) == 2
