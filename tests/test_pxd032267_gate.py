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

import csv
import json
import re
import subprocess
from pathlib import Path
from typing import Any

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


def test_the_deposit_declarations_carry_no_digest_and_the_publication_month() -> None:
    """`None` until the Mac fetch records one; the archive month from `frame_raw.tsv`."""
    frame = REPO_ROOT / "data" / "frame" / "frame_raw.tsv"
    with frame.open(encoding="utf-8", newline="") as handle:
        (row,) = [
            r for r in csv.DictReader(handle, delimiter="\t") if r["accession"] == "PXD032267"
        ]
    year, month, _ = row["publicationDate"].split("-")
    for deposit in (PXD032267_SITES, PXD032267_PARAMETERS):
        assert deposit.expected_content_hash is None
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


def _run(tmp_path: Path, **kwargs: Any) -> dict[str, Any]:
    author_path = kwargs.pop("author_path", tmp_path / "no-author.json")
    repo_root = kwargs.pop("repo_root", tmp_path)
    sites, parameters, published, facts = _twin(tmp_path, **kwargs)
    return gate.run(
        sites_path=sites,
        parameters_path=parameters,
        published=published,
        facts=facts,
        author_path=author_path,
        repo_root=repo_root,
        members=FEW_MEMBERS,
    )


# ── 1. pinning ──────────────────────────────────────────────────────────────────────────────────


def test_pinning_records_both_digests_and_says_it_compared_nothing(tmp_path: Path) -> None:
    sites, parameters, _, facts = _twin(tmp_path)
    _, record = gate.pinning_check(sites, parameters, facts=facts)
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
        gate.pinning_check(sites, parameters, facts=wrong)


def test_pinning_fails_on_a_wrong_reverse_count(tmp_path: Path) -> None:
    sites, parameters, _, facts = _twin(tmp_path)
    wrong = gate.DepositFacts(facts.data_rows, facts.columns, facts.reverse + 1, facts.joined_ids)
    with pytest.raises(gate.GateError, match="'reverse': 3"):
        gate.pinning_check(sites, parameters, facts=wrong)


def test_pinning_fails_on_a_declared_digest_that_differs(tmp_path: Path) -> None:
    sites, parameters, _, facts = _twin(tmp_path)
    declared = DepositFile("PXD032267", 2023, 5, "GlyGly__K_Sites.txt", "sha256:" + "0" * 64)
    with pytest.raises(gate.GateError, match="not the declared"):
        gate.pinning_check(sites, parameters, facts=facts, sites_deposit=declared)


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
        matrix,
        matched,
        [3, 5],
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
