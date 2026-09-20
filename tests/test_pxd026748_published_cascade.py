"""`bzk/sources/pxd026748_published_cascade.py` — the arithmetic, on synthetic inputs.

**Entirely offline, and nothing here touches PXD026748.** The module reads a deposit and a journal
supplement that exist only on bzk's machine; what can be tested here is where it places a row once
both have been read, and that it refuses to write half a fixture. Every workbook is built in
`tmp_path` with `openpyxl`, as `tests/test_perseus.py` builds its own, and thrown away. No deposit,
no supplement and no generated fixture is committed.

**One test here guards a module this turn changed and does not own.** The `doi` field added to
`bzk.sources.protein_groups.SupplementaryFile` exists so a second article can declare a file; the
three anchor declarations must resolve to exactly the URLs they resolved to before, and
`test_the_anchor_declarations_keep_their_urls` is what says so.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from bzk.adapters import maxquant
from bzk.adapters.spreadsheet import SpreadsheetError
from bzk.sources import protein_groups
from bzk.sources import pxd026748_published_cascade as cascade_source

# Real accessions (`CLAUDE.md` § Working style); nothing here depends on what UniProt says of them.
MX1 = "P20591"
IFIT1 = "P09914"
ISG15 = "P05161"

#: The four mapping keys of one synthetic group, and the three groups that complete the four.
GROUPS: dict[str, list[str]] = {
    "WT | wt_plpro": ["Intensity A1", "Intensity A2", "Intensity A3"],
    "WT | mut_plpro": ["Intensity B1", "Intensity B2", "Intensity B3"],
    "KO | wt_plpro": ["Intensity C1", "Intensity C2", "Intensity C3"],
    "KO | mut_plpro": ["Intensity D1", "Intensity D2", "Intensity D3"],
}
SAMPLE_COLUMNS = [name for names in GROUPS.values() for name in names]

SITE_HEADER = [
    "Proteins",
    "Positions within proteins",
    "Protein",
    "Position",
    "Amino acid",
    "Localization prob",
    "Sequence window",
    "Reverse",
    "Potential contaminant",
    "id",
    *SAMPLE_COLUMNS,
    "Intensity A3___2",
]


def _site_row(
    *,
    protein: str,
    position: str,
    row_id: str,
    prob: str = "0.99",
    window: str = "AAAKAAA",
    reverse: str = "",
    contaminant: str = "",
    values: list[str] | None = None,
    mult_2: str = "",
) -> list[str]:
    return [
        protein,
        position,
        protein,
        position,
        "K",
        prob,
        window,
        reverse,
        contaminant,
        row_id,
        *(values if values is not None else ["100"] * len(SAMPLE_COLUMNS)),
        mult_2,
    ]


def _deposit(tmp_path: Path, rows: list[list[str]]) -> maxquant.MaxQuantTable:
    """A synthetic site table read back through the adapter's own reader."""
    lines = ["\t".join(SITE_HEADER)] + ["\t".join(r) for r in rows]
    path = tmp_path / "GlyGly (K)Sites.txt"
    path.write_bytes(("\r\n".join(lines) + "\r\n").encode("utf-8"))
    return maxquant.read_table(path)


def _published(**overrides: Any) -> dict[str, Any]:
    row = {
        "#": 1,
        "Cluster": "A",
        "Uniprot ID": MX1,
        "Gene name": "MX1",
        "Lysine position": 4,
        "Multiplicity": 1,
        "Sequence window": "AAAKAAA",
    }
    row.update(overrides)
    return row


def _build(published: list[dict[str, Any]], deposit: maxquant.MaxQuantTable, **kwargs: Any) -> Any:
    defaults: dict[str, Any] = {
        "emitted_rows": {"0", "1", "2", "3", "4", "5"},
        "refused_rows": {},
        "groups": GROUPS,
        "localization_threshold": 0.75,
    }
    defaults.update(kwargs)
    return cascade_source.build(published=published, deposit=deposit, **defaults)


def _placed(record: dict[str, Any]) -> tuple[Any, Any]:
    return record["lost_at"], record["loss_reason"]


# ── T1 · one row per stage ──────────────────────────────────────────────────────────────────────


def test_one_published_row_lands_at_each_stage(tmp_path: Path) -> None:
    """T1. Six published rows: one lost at each of the five stages, twice at `join` for its two
    reasons, and one reaching the test.

    The stages are ordered, so a row lost early must never be examined later — a decoy row whose
    localisation is also low belongs to `decoy_contaminant`, and the placement being *exactly one*
    stage is what `summary`'s sum rests on.
    """
    deposit = _deposit(
        tmp_path,
        [
            # 0: clean, emitted, three positives in one group -> reaches the test
            _site_row(protein=MX1, position="4", row_id="0"),
            # 1: decoy
            _site_row(protein=IFIT1, position="7", row_id="1", reverse="+"),
            # 2: below the localisation threshold
            _site_row(protein=ISG15, position="9", row_id="2", prob="0.10"),
            # 3: matched but not emitted, and refused by name
            _site_row(protein=MX1, position="11", row_id="3"),
            # 4: emitted, but no group has three positives
            _site_row(
                protein=IFIT1,
                position="13",
                row_id="4",
                values=(["100", "100", "0"] * 4),
            ),
            # 5 and 6: two rows sharing a key -> ambiguous
            _site_row(protein=ISG15, position="21", row_id="5"),
            _site_row(protein=ISG15, position="21", row_id="6"),
        ],
    )
    published = [
        _published(**{"#": 1, "Uniprot ID": MX1, "Lysine position": 4}),
        _published(**{"#": 2, "Uniprot ID": IFIT1, "Lysine position": 7}),
        _published(**{"#": 3, "Uniprot ID": ISG15, "Lysine position": 9}),
        _published(**{"#": 4, "Uniprot ID": MX1, "Lysine position": 11}),
        _published(**{"#": 5, "Uniprot ID": IFIT1, "Lysine position": 13}),
        _published(**{"#": 6, "Uniprot ID": MX1, "Lysine position": 999}),
        _published(**{"#": 7, "Uniprot ID": ISG15, "Lysine position": 21}),
    ]

    records = _build(
        published,
        deposit,
        emitted_rows={"0", "1", "2", "4", "5", "6"},
        refused_rows={"3": "residue_mismatch"},
    )

    assert _placed(records[0]) == (None, None)
    assert _placed(records[1]) == ("decoy_contaminant", "reverse")
    assert _placed(records[2]) == ("localisation", "localization_prob_below_threshold")
    assert _placed(records[3]) == ("ingestion", "residue_mismatch")
    assert _placed(records[4]) == ("presence", "presence_rule")
    assert _placed(records[5]) == ("join", "no_key_match")
    assert _placed(records[6]) == ("join", "ambiguous_key")
    assert records[6]["ambiguous_ids"] == ["5", "6"]

    counts = cascade_source.summary(records)
    assert counts["reaches_test"] == 1
    assert {s: counts["lost"][s]["count"] for s in cascade_source.STAGES_RUN} == {
        "join": 2,
        "decoy_contaminant": 1,
        "localisation": 1,
        "ingestion": 1,
        "presence": 1,
    }
    assert "significance" not in counts["lost"], "no significance stage ran, so none is reported"


def test_a_matched_row_that_is_neither_emitted_nor_refused_is_named_as_such(
    tmp_path: Path,
) -> None:
    """The third state at `ingestion`. Calling it refused would invent a reason the adapter never
    gave, which is the same defect as reading a contingent null as a determined one."""
    deposit = _deposit(tmp_path, [_site_row(protein=MX1, position="4", row_id="0")])
    records = _build([_published()], deposit, emitted_rows=set(), refused_rows={})

    assert _placed(records[0]) == ("ingestion", "not_emitted")


# ── T2 · the window diagnostic does not recover ─────────────────────────────────────────────────


def test_a_window_match_is_recorded_and_never_recovers_the_row(tmp_path: Path) -> None:
    """T2. A published row whose key misses but whose window matches a deposit row stays lost at
    `join`, and carries that row's id as a lead.

    Recovering on the window would key a published claim to a row the publication's own identifier
    does not name — a razor-pick inference where an observation belongs (§6.3).
    """
    deposit = _deposit(
        tmp_path,
        [_site_row(protein=MX1, position="4", row_id="0", window="QQQKQQQ")],
    )
    published = [_published(**{"Lysine position": 999, "Sequence window": "QQQKQQQ"})]

    records = _build(published, deposit)

    assert _placed(records[0]) == ("join", "no_key_match")
    assert records[0]["window_matches"] == ["0"], "the lead is recorded"
    assert records[0]["deposit_id"] is None, "and it is not a key"
    assert cascade_source.summary(records)["reaches_test"] == 0


def test_the_window_diagnostic_is_null_where_the_deposit_has_no_window_column(
    tmp_path: Path,
) -> None:
    """`None`, not `[]`. An empty list would assert that no deposit row shares the window, which a
    table without the column cannot support."""
    header = [c for c in SITE_HEADER if c != "Sequence window"]
    row = [
        v
        for i, v in enumerate(_site_row(protein=MX1, position="4", row_id="0"))
        if SITE_HEADER[i] != "Sequence window"
    ]
    path = tmp_path / "GlyGly (K)Sites.txt"
    path.write_bytes(("\r\n".join(["\t".join(header), "\t".join(row)]) + "\r\n").encode("utf-8"))

    records = _build([_published(**{"Lysine position": 999})], maxquant.read_table(path))

    assert records[0]["window_matches"] is None


# ── T3 · presence uses summed intensities and the four groups ───────────────────────────────────


def test_presence_passes_on_three_positives_in_exactly_one_group(tmp_path: Path) -> None:
    """T3, first half. Three positives in one group and fewer in every other is a pass: the rule is
    *at least one* group, not every group."""
    values = ["100", "100", "100"] + ["100", "0", "0"] * 3
    deposit = _deposit(tmp_path, [_site_row(protein=MX1, position="4", row_id="0", values=values)])

    records = _build([_published()], deposit)

    assert _placed(records[0]) == (None, None)


def test_presence_fails_on_two_positives_in_every_group(tmp_path: Path) -> None:
    """T3, second half. Eight positives overall and no group of three is a fail — which is the
    whole point of grouping, and what a bare count over all twelve columns would get wrong."""
    values = ["100", "100", "0"] * 4
    deposit = _deposit(tmp_path, [_site_row(protein=MX1, position="4", row_id="0", values=values)])

    records = _build([_published()], deposit)

    assert _placed(records[0]) == ("presence", "presence_rule")


def test_the_multiplicity_flag_reads_the_split_columns_and_presence_does_not(
    tmp_path: Path,
) -> None:
    """The `…___2` column is recorded per record and never counted by the presence rule. A row
    whose summed values fail stays lost however large its per-multiplicity values are.

    **The `___2` value sits on `Intensity A3`, whose summed value is the zero of its group.** On
    any other column the fixture would be inert: a rule that wrongly counted the split column
    would reach the same verdict, and this test would pass without exercising its own claim.
    Measured — the mutation that counts `…___2` leaves the first fixture green.
    """
    values = ["100", "100", "0"] * 4
    deposit = _deposit(
        tmp_path,
        [_site_row(protein=MX1, position="4", row_id="0", values=values, mult_2="99999")],
    )

    records = _build([_published()], deposit)

    assert records[0]["has_positive_multiplicity_column"] is True
    assert _placed(records[0]) == ("presence", "presence_rule")


# ── T4 · the header row is found by content ─────────────────────────────────────────────────────


def _workbook(path: Path, sheet_rows: list[list[Any]], *, name: str = "Table 1") -> Path:
    import openpyxl

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = name
    for row in sheet_rows:
        sheet.append(row)
    workbook.save(path)
    return path


HEADER_CELLS = ["#", "Cluster", "Uniprot ID", "Gene name", "Lysine position"]


def test_a_title_row_above_the_header_is_skipped(tmp_path: Path) -> None:
    """T4, first half. The header's position is not recorded anywhere, so it is found by the two
    join-key columns rather than by a row number this module would be guessing."""
    path = _workbook(
        tmp_path / "supp.xlsx",
        [
            ["Supplementary Table 1", None, None, None, None],
            HEADER_CELLS,
            [1, "A", MX1, "MX1", 4],
            [2, "B", IFIT1, "IFIT1", 7],
        ],
    )

    rows = cascade_source.published_rows(path)

    assert [r["#"] for r in rows] == [1, 2]
    assert rows[0]["Uniprot ID"] == MX1
    assert rows[1]["Cluster"] == "B"


def test_a_duplicated_header_row_stops_with_a_message(tmp_path: Path) -> None:
    """T4, second half. Two candidate headers is not a thing to resolve by taking the first:
    choosing one would decide silently which block of rows is data."""
    path = _workbook(
        tmp_path / "supp.xlsx",
        [HEADER_CELLS, [1, "A", MX1, "MX1", 4], HEADER_CELLS, [2, "B", IFIT1, "IFIT1", 7]],
    )

    with pytest.raises(cascade_source.CascadeSourceError) as caught:
        cascade_source.published_rows(path)

    assert "2 rows carry" in str(caught.value)
    assert "[0, 2]" in str(caught.value)


def test_a_sheet_without_the_marker_columns_stops_with_a_message(tmp_path: Path) -> None:
    """Zero candidates is a different defect from two, and the message says which."""
    path = _workbook(tmp_path / "supp.xlsx", [["a", "b"], [1, 2]])

    with pytest.raises(cascade_source.CascadeSourceError, match="no row carries all of"):
        cascade_source.published_rows(path)


def test_the_named_sheet_is_read_and_a_missing_one_is_refused(tmp_path: Path) -> None:
    """The workbook has three sheets, so the reader is told which. A reader that fell back to the
    first would answer a question about `Table 1` with another sheet's rows."""
    import openpyxl

    workbook = openpyxl.Workbook()
    first = workbook.active
    first.title = "Legend"
    first.append(["this is not the table"])
    table = workbook.create_sheet("Table 1")
    for row in [HEADER_CELLS, [1, "A", MX1, "MX1", 4]]:
        table.append(row)
    path = tmp_path / "supp.xlsx"
    workbook.save(path)

    assert [r["#"] for r in cascade_source.published_rows(path)] == [1]

    with pytest.raises(SpreadsheetError, match="no sheet named 'Table 9'"):
        cascade_source.published_rows(path, sheet="Table 9")


# ── T5 · no partial fixture ─────────────────────────────────────────────────────────────────────


def test_main_writes_nothing_when_the_supplement_is_absent(tmp_path: Path) -> None:
    """T5. An empty `home` has neither file, so `main` exits before writing.

    **This reaches the supplement's own guard, which turn 13's equivalent could not.** There the
    deposit and the fixture directory were injectable and the record was not, so no test could put
    the run past the first guard. Here the supplement is a parameter, so a declaration whose hash
    nothing in the store matches is reachable without a deposit at all.
    """
    home = tmp_path / "home"
    home.mkdir()
    fixtures_dir = tmp_path / "fixtures"
    fixtures_dir.mkdir()

    with pytest.raises(SystemExit) as caught:
        cascade_source.main(home=home, fixtures_dir=fixtures_dir)

    assert "curation_PXD026748.json" in str(caught.value)
    assert "No fixture was written" in str(caught.value)
    assert list(fixtures_dir.iterdir()) == []


def test_main_names_the_supplement_when_only_it_is_missing(tmp_path: Path) -> None:
    """The second guard, reached with a record whose deposit *is* in the store.

    The deposit is synthetic and the curation record is built around its digest, so the run gets
    past `_parse_arm` and stops at the supplement — the case turn 13's module could not construct.
    """
    import json

    from bzk.provenance import raw_store

    home = tmp_path / "home"
    fixtures_dir = tmp_path / "fixtures"
    fixtures_dir.mkdir()

    lines = ["\t".join(SITE_HEADER), "\t".join(_site_row(protein=MX1, position="4", row_id="0"))]
    payload = ("\r\n".join(lines) + "\r\n").encode("utf-8")
    stored = raw_store.store(payload, "GlyGly (K)Sites.txt", home=home)

    record = json.loads(
        (Path(__file__).parent / "fixtures" / "curation_synthetic_loadable.json").read_text()
    )
    record["file"] = "GlyGly (K)Sites.txt"
    record["content_hash"] = stored.content_hash
    record["mapping"] = {
        name: dict(next(iter(record["mapping"].values())), replicate=i + 1)
        for i, name in enumerate(SAMPLE_COLUMNS[:4])
    }
    curation_path = tmp_path / "curation_SYNTHETIC.json"
    curation_path.write_text(json.dumps(record), encoding="utf-8")

    absent = protein_groups.SupplementaryFile(
        label="absent",
        filename="not_in_the_store.xlsx",
        expected_content_hash="sha256:" + "0" * 64,
        doi=cascade_source.PXD026748_DOI,
    )

    with pytest.raises(SystemExit) as caught:
        cascade_source.main(
            home=home,
            fixtures_dir=fixtures_dir,
            curation_path=curation_path,
            supplement=absent,
        )

    message = str(caught.value)
    assert "not_in_the_store.xlsx" in message
    assert "No fixture was written" in message
    assert list(fixtures_dir.iterdir()) == []


# ── the declaration this turn changed and does not own ──────────────────────────────────────────


def test_the_anchor_declarations_keep_their_urls() -> None:
    """The `doi` field added for this deposit must leave the anchor's three URLs byte-identical.

    Pinned as literals rather than re-derived from `SPRINGER_ESM`: re-deriving them would compare
    the new code with itself, which is what `tests/test_tautology_sweep.py` exists to catch.
    """
    base = (
        "https://static-content.springer.com/esm/art%3A10.1038%2Fs41416-020-01167-y/MediaObjects/"
    )
    assert protein_groups.SUPP_DATA_1.url == base + "41416_2020_1167_MOESM3_ESM.xlsx"
    assert protein_groups.SUPP_DATA_2.url == base + "41416_2020_1167_MOESM4_ESM.xlsx"
    assert protein_groups.SUPP_DATA_3.url == base + "41416_2020_1167_MOESM5_ESM.xlsx"

    assert cascade_source.SUPP_TABLE_1.url == (
        "https://static-content.springer.com/esm/art%3A10.1038%2Fs41590-021-01035-8/"
        "MediaObjects/41590_2021_1035_MOESM3_ESM.xlsx"
    )
