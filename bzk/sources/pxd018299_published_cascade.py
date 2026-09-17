"""Write the committed per-row record of the PXD018299 published-claim cascade.

`python -m bzk.sources.pxd018299_published_cascade`, after `python -m bzk.sources.pride` and with
`SUPP_DATA_1` in the store. Writes `tests/fixtures/pxd018299_published_cascade.json`, which
`bzk/published_cascade.py` reads and nothing else writes. What the cascade means, and why it
measures recall only, is that module's docstring; this one records how the rows are produced.

**Three inputs, each taken from the code that already owns it, never re-implemented here.**

1. **The platform path's per-row outcome** comes from running `pxd018299_differential.main()`
   itself, unmodified, with its two write destinations pointed at a temporary directory: its
   fixture (`FIXTURE_PATH`) and its graph (`open_graph`). The adapter's refusals and ingested rows
   are captured from `MaxQuantSiteAdapter.parse`, and the per-row statistics from the `SiteResult`
   list `main()` hands to `site_change_set`. Re-deriving any of that here would be a second source
   of truth for the population the whole comparison rests on. **The run must reproduce the
   committed `pxd018299_platform_targets.json` byte for byte, or nothing is written**: a cascade
   computed over a platform run that no longer matches its own committed record would be a
   comparison against a moved target.
2. **The published side's keying** passes every S1 row through the same `MaxQuantSiteAdapter` the
   deposit path uses — `_promotions` (I17), `resolve_to_nodes`, `_site` — configured from the
   curation record by `rebuild._adapter_for`. `_site` is given no sample columns and a placeholder
   dataset id; neither reaches the site key or the refusal.
3. **The join** matches each S1 row to exactly one deposit row on `(Protein, Position)`, and is not
   widened: a row matching none, or several, is lost at the `join` stage.

**Network conditions are part of the record, and differ between the two sides on purpose.** The
published side resolves **online**: S1 names accessions the deposit path never attempts — its
low-localisation rows, its contaminants and their promotion candidates — and an uncached canonical
candidate makes `is_live_reviewed` return False, so an offline run silently declines promotions an
online one makes (measured: 190 offline against 192 online). The deposit side runs with **network
refused**: its committed record is what it is checked against, and its lookups are not the ones this
run was asked to make. Both conditions, the requests made or refused, the commit and the UTC time
are written into `generated_under`, which `pxd018299_refusals.json` does not carry and which is why
its run cannot be compared like for like.

**It reaches the network**, for the published side only. Nothing in the installed package imports
this module; like its siblings it is an entry point.
"""

from __future__ import annotations

import math
import platform
import statistics
import subprocess
import sys
import tempfile
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import patch

import numpy as np
import requests
import scipy

from bzk import published_cascade as cascade
from bzk.adapters import maxquant, maxquant_sites, spreadsheet
from bzk.adapters.base import ParsedObservations, Refusal
from bzk.adapters.maxquant_sites import MaxQuantSiteAdapter
from bzk.analysis import SiteResult, site_change_set
from bzk.curation.loader import load_path
from bzk.http import RestResponse
from bzk.provenance.raw_store import verify
from bzk.rebuild import _adapter_for, _deposit_for, create_graph
from bzk.resolve.nodes import Resolver, resolve_to_nodes
from bzk.resolve.uniprot import DEFAULT_CACHE_DIR, Resolution, resolve
from bzk.sources import pxd018299_differential as differential
from bzk.sources.pride import PXD018299_SITES
from bzk.sources.protein_groups import SUPP_DATA_1

REPO_ROOT = Path(__file__).resolve().parents[2]
CURATION = REPO_ROOT / "data" / "curation" / "curation_PXD018299.json"
HOME = Path.home() / ".bzk-omics"
GENERATED_BY = "python -m bzk.sources.pxd018299_published_cascade"

#: S1's column for each field the adapter reads, so an S1 row can be handed to `_site` unchanged.
S1_AS_DEPOSIT = {
    "Proteins": "T: Proteins",
    "Positions within proteins": "T: Positions within proteins",
    "Protein": "T: Protein",
    "Position": "N: Position",
    "Amino acid": "C: Amino acid",
    "Localization prob": "N: Localization prob",
    "Score": "N: Score",
}
KO_COLUMNS = tuple(f"Intensity {differential.CONTRAST[0]}_{i}" for i in (1, 2, 3))
WT_COLUMNS = tuple(f"Intensity {differential.CONTRAST[1]}_{i}" for i in (1, 2, 3))


@dataclass
class PlatformRun:
    """What the platform path's own run produced, captured rather than recomputed."""

    parsed: ParsedObservations
    observation_of_row: dict[str, str]
    results: list[SiteResult]
    refused_requests: list[str]
    #: The threshold the adapter itself applied, read off the adapter rather than restated.
    localization_threshold: float

    @property
    def refused(self) -> dict[str, str]:
        return {r.row: r.reason for r in self.parsed.refusals}

    @property
    def result_of_observation(self) -> dict[str, SiteResult]:
        return {r.observation_id: r for r in self.results}

    @property
    def site_of_observation(self) -> dict[str, str]:
        return {
            str(e["from"]): str(e["to"]) for e in self.parsed.edges if e["type"] == "MEASURED_AT"
        }


class _RefusingSession:
    """A UniProt session that records each request and makes none."""

    def __init__(self) -> None:
        self.urls: list[str] = []

    def get(self, url: str, *, timeout: int = 0) -> RestResponse:
        self.urls.append(url)
        raise requests.ConnectionError("network refused for the deposit side of this run")


class _LoggingSession:
    """A UniProt session that performs each request and records it with its outcome."""

    def __init__(self) -> None:
        self._session = requests.Session()
        self.requests: list[dict[str, Any]] = []

    def get(self, url: str, *, timeout: int = 0) -> RestResponse:
        entry: dict[str, Any] = {"url": url, "at": datetime.now(UTC).isoformat()}
        try:
            response = self._session.get(url, timeout=timeout)
            entry["status"] = response.status_code
            return response
        except requests.RequestException as exc:
            entry["status"] = type(exc).__name__
            raise
        finally:
            self.requests.append(entry)


def run_platform_path() -> PlatformRun:
    """`pxd018299_differential.main()`, unmodified, with its writes redirected. See the docstring."""
    refusing = _RefusingSession()
    captured: dict[str, Any] = {}
    real_parse = MaxQuantSiteAdapter.parse
    real_change_set = site_change_set
    committed = Path(differential.FIXTURE_PATH).read_bytes()

    def offline_resolver(cache_dir: Path = DEFAULT_CACHE_DIR) -> Resolver:
        return lambda accession: resolve(accession, cache_dir=cache_dir, session=refusing)

    def parse(self: MaxQuantSiteAdapter, *args: Any, **kwargs: Any) -> ParsedObservations:
        parsed = real_parse(self, *args, **kwargs)
        captured["parsed"], captured["adapter"] = parsed, self
        return parsed

    def change_set(run: Any, results: list[SiteResult], **kwargs: Any) -> Any:
        captured["results"] = list(results)
        return real_change_set(run, results, **kwargs)

    with tempfile.TemporaryDirectory(prefix="bzk_published_cascade_") as scratch:
        fixture = Path(scratch) / "platform_targets.json"
        with (
            patch.object(differential, "FIXTURE_PATH", fixture),
            patch.object(differential, "open_graph", lambda _: create_graph(Path(scratch))),
            patch.object(differential, "site_change_set", change_set),
            patch.object(maxquant_sites, "default_resolver", offline_resolver),
            patch.object(MaxQuantSiteAdapter, "parse", parse),
        ):
            differential.main()
        if fixture.read_bytes() != committed:
            raise SystemExit(
                "the platform path no longer reproduces tests/fixtures/"
                "pxd018299_platform_targets.json byte for byte; the cascade is not written"
            )
    adapter: MaxQuantSiteAdapter = captured["adapter"]
    assert adapter.report is not None
    return PlatformRun(
        parsed=captured["parsed"],
        observation_of_row=dict(adapter.report.observation_of_row),
        results=captured["results"],
        refused_requests=refusing.urls,
        localization_threshold=float(adapter.declared.localization_threshold),
    )


@dataclass
class PublishedKeying:
    """The published side's keying, per S1 row, and the live requests it took."""

    by_row: dict[int, dict[str, Any]]
    requests: list[dict[str, Any]]
    started: str
    finished: str
    promotions: int = field(default=0)


def _text(value: object) -> str:
    return "" if value is None else str(value)


def key_published(s1_rows: list[tuple[int, dict[str, Any]]]) -> PublishedKeying:
    """Every S1 row through the deposit path's adapter, online. See the docstring."""
    session = _LoggingSession()
    seen: dict[str, Resolution] = {}

    def resolve_one(accession: str) -> Resolution:
        if accession not in seen:
            seen[accession] = resolve(accession, session=session)
        return seen[accession]

    curation = load_path(CURATION)
    deposit = _deposit_for(curation, HOME)
    if deposit is None:
        raise SystemExit("deposit not in the content store; run `python -m bzk.sources.pride`")
    adapter = _adapter_for(curation, deposit, resolve_one)
    if not isinstance(adapter, MaxQuantSiteAdapter):
        raise SystemExit(f"no site adapter recognises {deposit.name}")
    column = {name: i for i, name in enumerate([*S1_AS_DEPOSIT, "id"])}
    rows = [
        [_text(cells[s1]) for s1 in S1_AS_DEPOSIT.values()] + [str(number)]
        for number, cells in s1_rows
    ]

    started = datetime.now(UTC).isoformat()
    promotions = adapter._promotions(rows, column, resolve_one)
    keyed = {
        promotions[r[column["id"]]].promoted_to
        if r[column["id"]] in promotions
        else r[column["Protein"]]
        for r in rows
        if r[column["Protein"]] or r[column["id"]] in promotions
    }
    resolved = resolve_to_nodes(keyed, resolver=resolve_one)
    by_row: dict[int, dict[str, Any]] = {}
    for r in rows:
        outcome = adapter._site(
            r, column, resolved, "s1:placeholder", promotions.get(r[column["id"]]), []
        )
        if isinstance(outcome, Refusal):
            record: dict[str, Any] = {"outcome": "refused", "reason": outcome.reason, "site": None}
        else:
            site = next(e["to"] for e in outcome[1] if e["type"] == "MEASURED_AT")
            record = {"outcome": "keyed", "reason": None, "site": str(site)}
        promotion = promotions.get(r[column["id"]])
        record["promoted_to"] = promotion.promoted_to if promotion else None
        by_row[int(r[column["id"]])] = record
    finished = datetime.now(UTC).isoformat()
    return PublishedKeying(by_row, session.requests, started, finished, len(promotions))


def _float(value: float | None) -> float | None:
    return None if value is None or math.isnan(value) else float(value)


def _gene_cell(value: object) -> tuple[str | None, str]:
    """`T: Gene names` as it stands, and what kind of cell it was.

    One S1 cell is an Excel date (`Septin-7`'s symbol, converted by the spreadsheet), which JSON
    cannot hold as a date; it is written as its ISO text and marked, rather than repaired.
    """
    if value is None:
        return None, "empty"
    if isinstance(value, datetime):
        return value.isoformat(), "date"
    return str(value), "text"


def build(
    s1_rows: list[tuple[int, dict[str, Any]]],
    deposit: maxquant.MaxQuantTable,
    platform_run: PlatformRun,
    keying: PublishedKeying,
) -> list[dict[str, Any]]:
    """One record per S1 row, placed at exactly one stage."""
    col = {name: i for i, name in enumerate(deposit.header)}
    index: dict[tuple[str, str], list[list[str]]] = defaultdict(list)
    for row in deposit.rows:
        index[row[col["Protein"]].strip(), row[col["Position"]].strip()].append(row)
    refused = platform_run.refused
    results = platform_run.result_of_observation
    sites = platform_run.site_of_observation
    threshold = differential.SIG_ADJ_P, differential.SIG_LOG2FC

    records: list[dict[str, Any]] = []
    for number, cells in s1_rows:
        gene, gene_cell = _gene_cell(cells["T: Gene names"])
        published = statistics.fmean(cells[c] for c in KO_COLUMNS) - statistics.fmean(
            cells[c] for c in WT_COLUMNS
        )
        hits = index.get((_text(cells["T: Protein"]), _text(cells["N: Position"])), [])
        record: dict[str, Any] = {
            "row": number,
            "gene_names": gene,
            "gene_names_cell": gene_cell,
            "protein": cells["T: Protein"],
            "position": cells["N: Position"],
            "localization_prob": cells["N: Localization prob"],
            "wt_cells_below_21": sum(1 for c in WT_COLUMNS if cells[c] < cascade.WT_LOW_CUTOFF),
            "deposit_id": None,
            "lost_at": None,
            "loss_reason": None,
            "published_log2fc": published,
            "platform_log2fc": None,
            "platform_p": None,
            "platform_adj_p": None,
            "platform_site": None,
            "published_keying": keying.by_row[number],
        }
        records.append(record)
        if len(hits) != 1:
            record["lost_at"] = cascade.STAGE_JOIN
            record["loss_reason"] = "absent" if not hits else f"ambiguous ({len(hits)} rows)"
            continue
        row = hits[0]
        row_id = row[col["id"]]
        record["deposit_id"] = row_id
        loc = row[col["Localization prob"]].strip()
        if row[col["Reverse"]] == "+" or row[col["Potential contaminant"]] == "+":
            record["lost_at"] = cascade.STAGE_DECOY_CONTAMINANT
            record["loss_reason"] = (
                "reverse" if row[col["Reverse"]] == "+" else "potential_contaminant"
            )
            continue
        if not loc or float(loc) < platform_run.localization_threshold:
            record["lost_at"] = cascade.STAGE_LOCALISATION
            record["loss_reason"] = "localization_prob_below_threshold"
            continue
        if row_id in refused:
            record["lost_at"] = cascade.STAGE_INGESTION
            record["loss_reason"] = refused[row_id]
            continue
        observation = platform_run.observation_of_row[row_id]
        record["platform_site"] = sites.get(observation)
        result = results.get(observation)
        if result is None:
            record["lost_at"] = cascade.STAGE_PRESENCE
            record["loss_reason"] = "presence_rule"
            continue
        record["platform_log2fc"] = _float(result.log2fc)
        record["platform_p"] = _float(result.p_value)
        record["platform_adj_p"] = _float(result.adj_p_value)
        p_ok = not math.isnan(result.adj_p_value) and result.adj_p_value < threshold[0]
        fc_ok = not math.isnan(result.log2fc) and result.log2fc > threshold[1]
        if not (p_ok and fc_ok):
            record["lost_at"] = cascade.STAGE_SIGNIFICANCE
            record["loss_reason"] = (
                cascade.FAILS_BOTH
                if not (p_ok or fc_ok)
                else cascade.FAILS_P_VALUE
                if not p_ok
                else cascade.FAILS_FOLD_CHANGE
            )
    return records


def summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    """The stage counts, the significance split and the recall figure, from the records above.

    Computed by `bzk/published_cascade.py`'s own functions, so the summary and the module that
    re-derives it from the rows cannot hold two definitions of a stage.
    """
    steps = cascade.cascade(records)
    got = cascade.recovered(records)
    return {
        "published_rows": len(records),
        "lost": {step.stage: step.lost for step in steps},
        "significance_split": cascade.significance_split(records),
        "recovered": got,
        "recall": got / len(records),
    }


def _commit() -> dict[str, Any]:
    def git(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()

    return {
        "commit": git("rev-parse", "HEAD"),
        "working_tree_clean": not git("status", "--porcelain"),
    }


def fixture_for(
    records: list[dict[str, Any]],
    *,
    generated_at: str,
    platform_run: PlatformRun,
    keying: PublishedKeying,
) -> dict[str, Any]:
    return {
        "dataset": PXD018299_SITES.accession,
        "published_file": SUPP_DATA_1.filename,
        "published_content_hash": SUPP_DATA_1.expected_content_hash,
        "deposit_file": PXD018299_SITES.filename,
        "deposit_content_hash": PXD018299_SITES.expected_content_hash,
        "path": "platform",
        "note": (
            "Every row of Supplementary Data 1 (the publication's significant GlyGly peptides) "
            "joined to the deposit's site table and walked through the PLATFORM path, placed at "
            "exactly one stage: `lost_at` names the stage that lost it, or is null where it was "
            "recovered, and `loss_reason` says why. The stages are those of "
            "bzk/published_cascade.py, which re-derives the summary from the rows. Recall only: S1 "
            "is the significant set, so a platform-significant site absent from it is not a "
            "disagreement this record can score. `published_log2fc` is the mean of S1's three "
            "Intensity KO_IFN cells minus the mean of its three Intensity WT_IFN cells as the "
            "publication rounded them (four decimals), so differences below about 5e-5 are "
            "rounding. `platform_*` are the platform run's own statistics where the row reached "
            "the test. `published_keying` is the S1 row keyed ONLINE through the deposit path's "
            "adapter; `platform_site` is the deposit row's own key. `gene_names_cell` marks the one "
            "S1 cell the spreadsheet holds as a date. A change in these rows means an input moved "
            "— UniProt, the platform path, or a store's bytes — and needs explaining, not "
            f"regenerating. Regenerate with `{GENERATED_BY}`."
        ),
        "generated_by": GENERATED_BY,
        "generated_under": {
            "generated_at": generated_at,
            **_commit(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "published_side_keying": {
                "online": True,
                "started": keying.started,
                "finished": keying.finished,
                "live_uniprot_requests": len(keying.requests),
                "requests": keying.requests,
                "promotions": keying.promotions,
            },
            "deposit_side_run": {
                "online": False,
                "refused_uniprot_requests": platform_run.refused_requests,
                "reproduced_committed_fixture": "tests/fixtures/pxd018299_platform_targets.json",
            },
        },
        "summary": summary(records),
        "rows": records,
    }


def main() -> int:  # pragma: no cover - reaches the store and the network
    import json

    generated_at = datetime.now(UTC).isoformat()
    s1_table = spreadsheet.rows(
        verify(SUPP_DATA_1.expected_content_hash, filename=SUPP_DATA_1.filename)
    )
    header = [str(h) for h in s1_table[1]]
    s1_rows = [
        (number, dict(zip(header, cells, strict=True)))
        for number, cells in enumerate(s1_table[2:], start=3)
    ]
    assert PXD018299_SITES.expected_content_hash is not None
    deposit = maxquant.read_table(
        verify(PXD018299_SITES.expected_content_hash, filename=PXD018299_SITES.filename)
    )

    platform_run = run_platform_path()
    keying = key_published(s1_rows)
    records = build(s1_rows, deposit, platform_run, keying)
    fixture = fixture_for(
        records, generated_at=generated_at, platform_run=platform_run, keying=keying
    )
    cascade.FIXTURE_PATH.write_text(json.dumps(fixture, indent=2) + "\n")

    for line in cascade._report(fixture):
        print(f"[cascade] {line}")
    print(f"[cascade] {len(keying.requests)} live UniProt request(s) for the published side")
    print(f"[cascade] wrote {cascade.FIXTURE_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
