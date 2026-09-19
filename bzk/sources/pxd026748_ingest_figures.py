"""Write the committed record of what a PXD026748 ingestion produces, for both arms.

`python -m bzk.sources.pxd026748_ingest_figures`, after the two deposits are in the content store.
Parses each arm through the adapter its curation record selects — `rebuild._deposit_for` and
`rebuild._adapter_for`, the same two the replay uses — and writes
`tests/fixtures/pxd026748_digly_ingest.json` and `tests/fixtures/pxd026748_shotgun_ingest.json`.

**A generator, not a transcription, and that is the whole point.** PXD026748's ingest figures exist
only as prose — the GG arm's in `notes/reports/09-ingest-PXD026748-report.md`, the shotgun arm's in
`walk/RESULT-PXD026748-shotgun-ingest.md`. Writing a fixture by copying those numbers out would
repeat exactly what `tests/test_pxd018299_refusals.py`'s docstring names: a fixture written from the
documents it is supposed to check, which agrees with a sentence rather than with the bytes. The
anchor's fixtures are generated from the raw bytes by `bzk/sources/pxd018299_refusals.py` and these
follow it line for line.

**Record, don't judge.** This module writes figures. It does not compare them with any
registration, report or document, and it carries no expected values — not in an assertion, not in a
default, not in a docstring. A guard against what it writes is a different turn's work, and it needs
the fixtures to exist first.

**Neither fixture is written unless both arms parse.** Both deposits are located, both adapters are
selected and both parses run before anything touches disk. A run that fails on the second arm
leaves the first arm's fixture as it was, rather than committing half a measurement next to a stale
half — the two arms are one deposit and are read together.

**It reaches the network**, for the reason `pxd018299_refusals.py` gives: the GG arm's residue check
needs today's UniProt for every distinct razor pick. The shotgun arm resolves nothing. Nothing in
the installed package imports this module; like its siblings it is an entry point.

**The multi-protein and isoform methods are defined here and recorded in the fixture.** Neither
`walk/PREREG-PXD026748-ingest.md` nor report 09 states how those two shares were computed — the
PREREG names the quantities (*"share of sites whose `candidate_proteins` names more than one
protein"*, *"share of razor picks that are isoform accessions"*) and report 09 gives numerators and
denominators, and no document says which column was read, which rows were counted, or what makes an
accession an isoform. So the definitions below are this module's, written into each fixture as a
`method` string, and **they may differ from whatever turn 09 did.** That is a finding about the
report rather than a defect here: a share with no stated method cannot be reproduced, and the
fixture is the first place the method is written down.
"""

from __future__ import annotations

import collections
import json
import platform
import sys
from collections.abc import Mapping, Sequence
from dataclasses import asdict
from pathlib import Path
from typing import Any

from bzk.adapters import maxquant
from bzk.adapters.base import ParsedObservations
from bzk.adapters.maxquant_protein_groups import ProteinIngestReport
from bzk.adapters.maxquant_sites import SiteIngestReport
from bzk.curation.loader import LoadedCuration, load_path
from bzk.ontology.invariants import NODE_TYPE_KEY
from bzk.rebuild import _adapter_for, _deposit_for

REPO_ROOT = Path(__file__).resolve().parents[2]
CURATION_DIR = REPO_ROOT / "data" / "curation"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"
HOME = Path.home() / ".bzk-omics"

DIGLY_CURATION = CURATION_DIR / "curation_PXD026748.json"
SHOTGUN_CURATION = CURATION_DIR / "curation_PXD026748_shotgun.json"
DIGLY_FIXTURE = "pxd026748_digly_ingest.json"
SHOTGUN_FIXTURE = "pxd026748_shotgun_ingest.json"

GENERATED_BY = "python -m bzk.sources.pxd026748_ingest_figures"

#: MaxQuant's own flag for a group identified only by a modified peptide. The publication removed
#: these and the adapter does not, so the three counts below are what a comparison with the
#: publication has to subtract.
ONLY_BY_SITE_COLUMN = "Only identified by site"

#: What `candidate_proteins` naming more than one protein means, operationally. **Defined here, not
#: taken from a document** — see the module docstring.
MULTI_PROTEIN_METHOD = (
    "A row is multi-protein when its `Proteins` column, split on ';' with blanks dropped, names "
    "more than one accession; an emitted observation is multi-protein when its "
    "`candidate_proteins` list has more than one member. The row populations are the adapter's "
    "own, not re-derived: `after_decoy_or_contaminant` is "
    "`maxquant.drop_decoys_and_contaminants(table)` and `after_localisation` is the second value "
    "the adapter's `_filter` returns, so the denominators here are the same rows the ingestion "
    "counted. NEITHER walk/PREREG-PXD026748-ingest.md NOR notes/reports/09-ingest-PXD026748-"
    "report.md states the method behind their figures, so this definition is this module's and "
    "may differ from the one that produced them."
)

#: What an isoform razor pick is. **Defined here**, and deliberately the same test the resolver
#: applies at `bzk/resolve/uniprot.py:357` (`is_isoform = '-' in requested`) rather than a second
#: rule: two definitions of isoform in one repository would be a mirror with nothing holding them
#: equal, and the resolver's is the one that decides what gets fetched.
ISOFORM_METHOD = (
    "A razor pick is MaxQuant's `Protein` column for a row, stripped, BEFORE any I17 promotion — "
    "promotion replaces the pick with a reviewed entry, and 'razor pick' names what MaxQuant "
    "chose. It is an isoform accession when it contains '-', which is the test "
    "`bzk/resolve/uniprot.py:357` applies. `rows.denominator` counts every row after the "
    "localisation filter, including rows whose `Protein` is empty and which the adapter then "
    "refuses as `no_razor_pick`; those rows contribute to the denominator and never to the "
    "numerator. `distinct_picks` counts each non-empty pick once. As above, neither the PREREG "
    "nor report 09 states its method and this one may differ."
)


# ── The arithmetic, pure ────────────────────────────────────────────────────────────────────────


def _header(curation: LoadedCuration, fixture_note: str) -> dict[str, Any]:
    """Provenance, in the anchor fixture's key order.

    `dataset`, `file` and `content_hash` come off the loaded `Dataset` node rather than from a
    `pride.DepositFile`, as `pxd018299_refusals.py` takes them: there is no `DepositFile` for
    PXD026748, and the curation record is what named the bytes in the first place.
    """
    dataset = next(n for n in curation.nodes if n[NODE_TYPE_KEY] == "Dataset")
    return {
        "dataset": str(dataset["external_accession"]),
        "file": str(dataset["label"]),
        "content_hash": str(dataset["content_hash"]),
        "note": fixture_note,
        "generated_by": GENERATED_BY,
        # Python only, as the anchor records: nothing here computes a statistic, so neither numpy
        # nor scipy is in the path. What the GG arm's refusals depend on is what UniProt returned
        # on the day, which has no version number and is named inside each refusal's `detail`.
        "generated_under": {"python": platform.python_version()},
    }


def _cells_by_quantity(parsed: ParsedObservations) -> dict[str, int]:
    """One count per `quantity` across every batch. Sorted keys — a mapping has no order to keep."""
    counts = collections.Counter(c.quantity for _, batch in parsed.cells for c in batch)
    return dict(sorted(counts.items()))


def _positive_cells_by_quantity(parsed: ParsedObservations) -> dict[str, int]:
    """Cells whose value is strictly greater than zero, per quantity.

    Separate from the total because they answer different questions and MaxQuant writes both `0`
    and nothing: a reported zero is a measurement (I19, `maxquant.cell_value`) and stays in the
    total, so the gap between these two numbers and `_cells_by_quantity`'s is the zeros plus the
    nulls, which is what coverage means at this grain.
    """
    counts = collections.Counter(
        c.quantity
        for _, batch in parsed.cells
        for c in batch
        if c.value is not None and c.value > 0
    )
    return dict(sorted(counts.items()))


def _multi_protein_rows(rows: Sequence[Sequence[str]], column: Mapping[str, int]) -> int:
    index = column["Proteins"]
    return sum(1 for row in rows if len([a for a in row[index].split(";") if a.strip()]) > 1)


def _share(numerator: int, denominator: int) -> dict[str, int]:
    """A share as its two integers and nothing else — never a float.

    A percentage is a derivation, and `CLAUDE.md` § *Generated values are never displayed as
    measurements* is the same rule one layer down: the fixture records what was counted, and
    whoever wants a percentage divides.
    """
    return {"numerator": numerator, "denominator": denominator}


def digly_fixture(
    *,
    curation: LoadedCuration,
    report: SiteIngestReport,
    parsed: ParsedObservations,
    rows_after_decoys: Sequence[Sequence[str]],
    rows_after_localisation: Sequence[Sequence[str]],
    column: Mapping[str, int],
) -> dict[str, Any]:
    """The GG arm's figures. Pure: every number here is counted from an argument."""
    observations = [n for n in parsed.nodes if n[NODE_TYPE_KEY] == "SiteObservation"]
    multi_emitted = sum(1 for n in observations if len(list(n["candidate_proteins"])) > 1)

    picks = [str(row[column["Protein"]]).strip() for row in rows_after_localisation]
    named = [p for p in picks if p]
    distinct = sorted(set(named))

    return {
        **_header(
            curation,
            "What ingesting PXD026748's GG-enriched site table produces: every count on the "
            "adapter's SiteIngestReport, the quantitative cells it retains, the membership of its "
            "refusals, and the two shares walk/PREREG-PXD026748-ingest.md registered. Generated "
            "from the deposit's bytes through the adapter the curation record selects, never "
            "transcribed from a report — see this module's docstring for why. The two shares "
            "carry their own `method` string because no document states the method behind the "
            f"figures they are comparable to. Regenerate with `{GENERATED_BY}`.",
        ),
        "report": {
            "rows_read": report.rows_read,
            "dropped_decoy_or_contaminant": report.dropped_decoy_or_contaminant,
            "dropped_below_localization": report.dropped_below_localization,
            "sites_emitted": report.sites_emitted,
            "refused_no_razor_pick": report.refused_no_razor_pick,
            "refused_unresolved_protein": report.refused_unresolved_protein,
            "refused_residue_mismatch": report.refused_residue_mismatch,
            "promoted_reviewed": report.promoted_reviewed,
        },
        "cells": {
            "total": sum(len(batch) for _, batch in parsed.cells),
            "by_quantity": _cells_by_quantity(parsed),
        },
        "refusals": [asdict(r) for r in parsed.refusals],
        "multi_protein": {
            "method": MULTI_PROTEIN_METHOD,
            "after_decoy_or_contaminant": _share(
                _multi_protein_rows(rows_after_decoys, column), len(rows_after_decoys)
            ),
            "after_localisation": _share(
                _multi_protein_rows(rows_after_localisation, column), len(rows_after_localisation)
            ),
            "emitted_observations": _share(multi_emitted, len(observations)),
        },
        "isoform_razor_picks": {
            "method": ISOFORM_METHOD,
            "rows": _share(sum(1 for p in named if "-" in p), len(picks)),
            "distinct_picks": _share(sum(1 for p in distinct if "-" in p), len(distinct)),
        },
    }


def _only_identified_by_site(
    table: maxquant.MaxQuantTable, column: Mapping[str, int], report: ProteinIngestReport
) -> dict[str, Any]:
    """The three counts a comparison with the publication needs, or nulls if the column is absent.

    The publication removed proteins only identified by site; the adapter filters `Reverse` and
    `Potential contaminant` only, so some of these rows reach the graph and some are dropped for a
    different reason entirely. The record's FILTERS item was corrected 2026-09-19 for exactly that
    overlap, having first assumed there was none.

    **Nulls rather than zeros where the column is absent.** `Only identified by site` is a MaxQuant
    output option, so a file without it has no such rows *recorded* — which is not the same as
    having none, and writing `0` would state a measurement the file cannot support (I15's shape at
    fixture grain). `column_present` says which case this is.
    """
    if ONLY_BY_SITE_COLUMN not in column:
        return {
            "column_present": False,
            "in_file": None,
            "emitted": None,
            "dropped_as_decoy_or_contaminant": None,
        }

    index = column[ONLY_BY_SITE_COLUMN]
    reverse = column.get("Reverse")
    contaminant = column.get("Potential contaminant")
    id_index = column["id"]
    emitted_rows = set(report.observation_of_row)

    in_file = [row for row in table.rows if row[index] == "+"]
    dropped = [
        row
        for row in in_file
        if (reverse is not None and row[reverse] == "+")
        or (contaminant is not None and row[contaminant] == "+")
    ]
    return {
        "column_present": True,
        "in_file": len(in_file),
        # Counted through the adapter's own `observation_of_row` rather than as `in_file - dropped`:
        # a row can also fail to be emitted by being refused, and a subtraction would fold that
        # into the decoy count and report a row as dropped for a reason it was not.
        "emitted": sum(1 for row in in_file if row[id_index] in emitted_rows),
        "dropped_as_decoy_or_contaminant": len(dropped),
    }


def shotgun_fixture(
    *,
    curation: LoadedCuration,
    report: ProteinIngestReport,
    parsed: ParsedObservations,
    table: maxquant.MaxQuantTable,
    column: Mapping[str, int],
) -> dict[str, Any]:
    """The shotgun arm's figures. Pure: every number here is counted from an argument."""
    analysis = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "Analysis" and "quantity" in n)

    return {
        **_header(
            curation,
            "What ingesting PXD026748's shotgun protein-groups table produces: every field on the "
            "adapter's ProteinIngestReport but `observation_of_row`, the quantitative cells it "
            "retains by family, the membership of its refusals, the quantity its ingestion "
            "Analysis declares, and the only-identified-by-site rows the publication removed and "
            "this adapter does not. Generated from the deposit's bytes through the adapter the "
            f"curation record selects, never transcribed from a report. Regenerate with "
            f"`{GENERATED_BY}`.",
        ),
        "report": {
            "rows_read": report.rows_read,
            "spill_lines": report.spill_lines,
            "dropped_decoy_or_contaminant": report.dropped_decoy_or_contaminant,
            "groups_emitted": report.groups_emitted,
            "refused_empty_group": report.refused_empty_group,
            "distinct_accessions": report.distinct_accessions,
            "cells": report.cells,
        },
        "cells": {
            "by_quantity": _cells_by_quantity(parsed),
            "positive_by_quantity": _positive_cells_by_quantity(parsed),
        },
        "refusals": [asdict(r) for r in parsed.refusals],
        "analysis_quantity": str(analysis["quantity"]),
        "only_identified_by_site": _only_identified_by_site(table, column, report),
    }


# ── The IO ──────────────────────────────────────────────────────────────────────────────────────


def _parse_arm(curation_path: Path, home: Path) -> tuple[LoadedCuration, Any, ParsedObservations]:
    """`(curation, adapter, parsed)` for one arm, or `SystemExit` naming the record.

    Located and configured exactly as `replay_ingestion` does it, rather than by constructing an
    adapter from constants here. `pxd018299_refusals.py` gives the reason and it holds unchanged:
    the figures this file records must be the figures an ingestion produces, and an adapter
    configured from a different declaration is a second population wearing the same name.
    """
    curation = load_path(curation_path)
    deposit = _deposit_for(curation, home)
    if deposit is None:
        raise SystemExit(
            f"{curation_path.name} names a deposit that is not in the content store under {home}; "
            "fetch it and re-run. No fixture was written."
        )
    adapter = _adapter_for(curation, deposit, None)
    if adapter is None:
        raise SystemExit(
            f"no adapter recognises {deposit.name}, named by {curation_path.name}. "
            "No fixture was written."
        )
    parsed = adapter.parse(deposit, curation.sample_mapping())
    return curation, adapter, parsed


def main(*, home: Path = HOME, fixtures_dir: Path = FIXTURES_DIR) -> int:
    """Parse both arms, then write both fixtures. Never one without the other.

    **`home` and `fixtures_dir` are parameters with real defaults, and the tests pass their own.**
    `rebuild.replay_ingestion`'s docstring records what a default pointing at the real store cost
    once — 78 seconds a run and counts that depended on whether the developer had fetched the
    deposit. This module is an entry point rather than a library, so the defaults stay; what the
    tests need is a way past them, and that is what these are.
    """
    digly_curation, digly_adapter, digly_parsed = _parse_arm(DIGLY_CURATION, home)
    shotgun_curation, shotgun_adapter, shotgun_parsed = _parse_arm(SHOTGUN_CURATION, home)

    digly_deposit = _deposit_for(digly_curation, home)
    shotgun_deposit = _deposit_for(shotgun_curation, home)
    assert digly_deposit is not None and shotgun_deposit is not None  # `_parse_arm` raised if not

    digly_table = maxquant.read_table(digly_deposit)
    digly_column = {name: i for i, name in enumerate(digly_table.header)}
    # The adapter's own two row populations, taken from the adapter rather than re-derived here:
    # `drop_decoys_and_contaminants` is the function `_filter` calls first, and `_filter` is the
    # function the ingestion applied. A second implementation of either would be a second
    # population wearing the same name, which is the failure `_parse_arm`'s docstring names.
    rows_after_decoys = maxquant.drop_decoys_and_contaminants(digly_table)
    rows_after_localisation, _, _ = digly_adapter._filter(digly_table, digly_column)

    shotgun_table = maxquant.read_table(shotgun_deposit)
    shotgun_column = {name: i for i, name in enumerate(shotgun_table.header)}

    digly = digly_fixture(
        curation=digly_curation,
        report=digly_adapter.report,
        parsed=digly_parsed,
        rows_after_decoys=rows_after_decoys,
        rows_after_localisation=rows_after_localisation,
        column=digly_column,
    )
    shotgun = shotgun_fixture(
        curation=shotgun_curation,
        report=shotgun_adapter.report,
        parsed=shotgun_parsed,
        table=shotgun_table,
        column=shotgun_column,
    )

    # Both dicts are built before either is written, so a failure in the second arm's arithmetic
    # leaves the first arm's committed fixture untouched rather than one turn ahead of it.
    for name, fixture in ((DIGLY_FIXTURE, digly), (SHOTGUN_FIXTURE, shotgun)):
        (fixtures_dir / name).write_text(json.dumps(fixture, indent=2) + "\n")
        print(f"[figures] wrote {fixtures_dir / name}")

    print(
        f"[figures] GG      {digly['report']['sites_emitted']:,} site(s) emitted, "
        f"{len(digly['refusals']):,} refused, {digly['cells']['total']:,} cell(s)"
    )
    print(
        f"[figures] shotgun {shotgun['report']['groups_emitted']:,} group(s) emitted, "
        f"{len(shotgun['refusals']):,} refused, {shotgun['report']['cells']:,} cell(s)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
