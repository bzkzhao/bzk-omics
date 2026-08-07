"""Ingest the PXD018299 GlyGly site table and report what the run measured.

Run as `python -m bzk.sources.pxd018299_sites` after `python -m bzk.sources.pride`. Reads the
deposit out of the content-addressed store by the digest `bzk.sources.pride.PXD018299_SITES` holds,
so it cannot silently run against different bytes, and takes its `SampleMapping` from the real
curation record rather than a synthetic one.

**This exists to produce a number, not to demonstrate the adapter.** The residue check in
`bzk/adapters/maxquant_sites.py` refuses any site whose reported residue disagrees with today's
UniProt at that position, and how many it refuses is the first direct measurement of what sequence
drift costs this deposit — the search ran in 2019, the resolver returns 2026. `ROADMAP.md`
§ Measured findings carries the result. `HANDOFF.md` §3: report it even if it is zero, especially
if it is zero.

**It reaches the network.** Resolving the distinct razor picks is ~1,000 UniProt lookups on a cold
cache, served from `~/.bzk-omics/cache/uniprot` afterwards (`OPERATIONS.md` §3). Nothing in the
installed package imports this module — like `pxd018299_baseline.py` it is an entry point, kept
beside `pride.py` because that is the fetch path for the input it reads.
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path

from bzk.adapters.maxquant_sites import DeclaredSiteAnalysis, MaxQuantSiteAdapter
from bzk.curation.loader import load_path
from bzk.ontology.invariants import NODE_TYPE_KEY
from bzk.provenance.raw_store import verify
from bzk.sources.pride import PXD018299_SITES

REPO_ROOT = Path(__file__).resolve().parents[2]
CURATION = REPO_ROOT / "data" / "curation" / "curation_PXD018299.json"

# Transcribed from `colab_reproducefigure.ipynb` cell 2 and the curation record, not read from them:
# the record is what this run is checked against, so taking its parameters as input would make the
# comparison circular — the same reasoning as `pxd018299_baseline.py`.
LOC_THRESHOLD = 0.75
SEARCH_ENGINE = "maxquant"
SEARCH_ENGINE_VERSION = "1.6.10.43"


def main() -> int:
    assert PXD018299_SITES.expected_content_hash is not None
    path = verify(PXD018299_SITES.expected_content_hash, filename=PXD018299_SITES.filename)
    curation = load_path(CURATION)
    mapping = curation.sample_mapping()
    if not mapping.samples:
        raise SystemExit(f"{CURATION} carries no Sample nodes; the mapping would be empty")

    adapter = MaxQuantSiteAdapter(
        DeclaredSiteAnalysis(
            search_engine=SEARCH_ENGINE,
            external_version=SEARCH_ENGINE_VERSION,
            localization_threshold=LOC_THRESHOLD,
        )
    )
    parsed = adapter.parse(path, mapping)
    report = adapter.report
    assert report is not None  # set by parse; asserted so a refactor cannot quietly drop it

    print(f"[sites] {path.name}")
    print(f"[sites] rows read                     {report.rows_read:>6,}")
    print(f"[sites]   - decoy / contaminant       {report.dropped_decoy_or_contaminant:>6,}")
    print(
        f"[sites]   - localization prob < {LOC_THRESHOLD}  {report.dropped_below_localization:>6,}"
    )
    print(
        f"[sites] considered                    {report.rows_read - report.dropped_decoy_or_contaminant - report.dropped_below_localization:>6,}"
    )
    print(f"[sites]   - no razor pick             {report.refused_no_razor_pick:>6,}")
    print(f"[sites]   - protein unresolved        {report.refused_unresolved_protein:>6,}")
    print(f"[sites]   - RESIDUE MISMATCH          {report.refused_residue_mismatch:>6,}")
    print(f"[sites] sites emitted                 {report.sites_emitted:>6,}")

    labels = collections.Counter(n[NODE_TYPE_KEY] for n in parsed.nodes)
    edge_types = collections.Counter(e["type"] for e in parsed.edges)
    print(f"[sites] nodes {dict(sorted(labels.items()))}")
    print(f"[sites] edges {dict(sorted(edge_types.items()))}")

    if report.unresolved:
        print(f"[sites] {len(report.unresolved)} accession(s) without a usable sequence:")
        for accession, why in sorted(report.unresolved.items()):
            print(f"[sites]     {accession}: {why}")

    by_reason = collections.Counter(r.reason for r in parsed.refusals)
    for reason in sorted(by_reason):
        print(f"[sites] --- {reason} ({by_reason[reason]}) ---")
        for refusal in [r for r in parsed.refusals if r.reason == reason][:20]:
            print(f"[sites]     row {refusal.row}: {refusal.detail}")
        if by_reason[reason] > 20:
            print(f"[sites]     … and {by_reason[reason] - 20} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
