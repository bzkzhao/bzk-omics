"""Write the committed record of which PXD018299 rows ingestion refuses, and why.

`python -m bzk.sources.pxd018299_refusals`, after `python -m bzk.sources.pride`. Parses the anchor
deposit through the adapter the curation record selects — `rebuild._deposit_for` and
`rebuild._adapter_for`, the same two the replay uses — and writes every `Refusal` the parse returns
to `tests/fixtures/pxd018299_refusals.json`.

**The counts already survive an ingestion and the membership does not, and that asymmetry is what
this module closes.** `maxquant_sites.SiteIngestReport` carries `refused_residue_mismatch`,
`refused_unresolved_protein` and `refused_no_razor_pick`; `rebuild.replay_ingestion` accumulates the
`Refusal` objects themselves, logs `len(...)` and carries the list on its `ReplayReport`, which the
CLI then drops when it returns. Nothing writes them anywhere, and nothing can read them back: a
refusal is not an entity (`adapters/base.py`, `ROADMAP.md` § *Measured findings*), so
`query.refusals` answers `NOT_RETAINED` and — decided the same day — stays that way. Three integers
cannot say *which* fifteen rows drifted, which is the `HANDOFF.md` §6 shape one grain along: a
number that reads the same whichever fifteen they were.

**This writes a fixture and not a node table.** Nothing here touches the DDL, the invariants or
`query`; the sentence in `adapters/base.py` that a refusal has no id by construction is unchanged,
and so is `NOT_RETAINED`. What changes is that the membership now has a home outside a terminal
buffer, in the same shape as `pxd018299_platform_targets.json` and `pxd018299_welch_baseline.json`.

**No accession field, and that is a finding rather than an omission.** `Refusal` carries `row`,
`reason` and `detail` and nothing else. The accession is a live local at two of the three
construction sites in `maxquant_sites._site` — `pick`, which the `unresolved_protein` and
`residue_mismatch` details both name — and at the third (`no_razor_pick`) there is no accession to
carry, because an empty `Protein` column is the whole reason for that refusal. It is not a field on
the object this module receives, so recording it as its own key would mean either widening the
adapter contract or parsing it back out of `detail`; the second would turn a human sentence into an
apparently structured measurement. It stays inside `detail`. A gene symbol is not available at any
of the three sites: `Gene names` is not in `REQUIRED_COLUMNS` and the adapter never reads it.

**It reaches the network**, for the reason `pxd018299_sites.py` gives — the residue check needs
today's UniProt for every distinct razor pick, ~1,000 lookups on a cold cache. Nothing in the
installed package imports this module; like its two siblings it is an entry point.
"""

from __future__ import annotations

import collections
import json
import platform
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from bzk.adapters.base import Refusal
from bzk.curation.loader import load_path
from bzk.rebuild import _adapter_for, _deposit_for
from bzk.sources.pride import PXD018299_SITES

REPO_ROOT = Path(__file__).resolve().parents[2]
CURATION = REPO_ROOT / "data" / "curation" / "curation_PXD018299.json"
HOME = Path.home() / ".bzk-omics"
FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "pxd018299_refusals.json"

GENERATED_BY = "python -m bzk.sources.pxd018299_refusals"


def refusal_fixture(refusals: list[Refusal]) -> dict[str, Any]:
    """The committed record: provenance, the counts, then every refusal in the order `parse` returned it.

    **`counts` is computed from `refusals` here and read from nowhere else.** The same three numbers
    exist on `SiteIngestReport` and are quoted in `adapters/base.py`'s docstring and in
    `ROADMAP.md`; taking them from any of those would make this file agree with a sentence rather
    than with its own list, which is the failure the `counts`-against-recount guard in
    `tests/test_pxd018299_refusals.py` is written for.

    Nothing is summarised, grouped or re-ordered. `counts` has sorted keys because a mapping has no
    order to preserve; `refusals` keeps the parse order, which is the file's row order through the
    adapter's filters and is part of what is being recorded.
    """
    counts = collections.Counter(r.reason for r in refusals)
    return {
        "dataset": PXD018299_SITES.accession,
        "file": PXD018299_SITES.filename,
        "content_hash": PXD018299_SITES.expected_content_hash,
        "note": (
            "Every row the PXD018299 ingestion refused, individually: its MaxQuant `id`, the "
            "reason slug, and the detail the adapter constructed. This is the only record of "
            "refusal MEMBERSHIP anywhere — a refusal is not an entity, nothing is written to the "
            "graph, and query.refusals answers NOT_RETAINED, so after an ingestion the counts "
            "survive on the adapter's report and which rows they were does not. The accession "
            "sits inside `detail` and is deliberately not lifted into a field of its own: it is "
            "not a field on adapters.base.Refusal, and parsing it back out of a sentence written "
            "for a human would record a derivation as a measurement. No gene symbol is recorded "
            "because none is available where a Refusal is constructed. `counts` is computed from "
            "`refusals` below, never restated from the adapter's report or from any document. The "
            "refusals are in the order the parse returned them and are not grouped or sorted. A "
            "change in these rows means the reference data moved — UniProt amended a sequence, or "
            "the deposit's bytes changed — and needs explaining, not regenerating: which rows "
            "drifted is the finding, so a diff here is the result rather than noise. Regenerate "
            f"with `python -m bzk.sources.pride && {GENERATED_BY}`."
        ),
        "generated_by": GENERATED_BY,
        # Python only. The siblings record numpy and scipy because their numbers come out of them;
        # nothing here computes a statistic. What these rows actually depend on is what UniProt
        # returned on the day, which has no single version number — the per-sequence version is
        # named inside each `residue_mismatch` detail, which is where it can be checked.
        "generated_under": {"python": platform.python_version()},
        "counts": dict(sorted(counts.items())),
        "refusals": [asdict(r) for r in refusals],
    }


def main() -> int:
    # Located and configured exactly as `replay_ingestion` does it, rather than by constructing a
    # `MaxQuantSiteAdapter` from constants here as `pxd018299_sites.py` does. The refusals this
    # file records must be the refusals an ingestion produces, and an adapter configured from a
    # different declaration is a second population wearing the same name.
    curation = load_path(CURATION)
    deposit = _deposit_for(curation, HOME)
    if deposit is None:
        raise SystemExit("deposit not in the content store; run `python -m bzk.sources.pride`")
    adapter = _adapter_for(curation, deposit, None)
    if adapter is None:
        raise SystemExit(f"no adapter recognises {deposit.name}; nothing to refuse")

    parsed = adapter.parse(deposit, curation.sample_mapping())
    fixture = refusal_fixture(parsed.refusals)
    FIXTURE_PATH.write_text(json.dumps(fixture, indent=2) + "\n")

    counts: dict[str, int] = fixture["counts"]
    print(f"[refusals] {deposit.name} via {adapter.name}")
    print(f"[refusals] refused {len(parsed.refusals):,} row(s)")
    for reason in sorted(counts):
        print(f"[refusals]   {reason:<24} {counts[reason]:>6,}")
    print(f"[refusals] wrote {FIXTURE_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
