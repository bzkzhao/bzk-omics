"""Turn 12: store PXD026748's shotgun proteinGroups.txt, parse it, and rebuild in a scratch home.

Usage, from the repository root:

    .venv/bin/python notes/scripts/measure_shotgun_ingest.py \
        ~/Downloads/20210616_Shotgun_PRIDE/proteinGroups.txt

Registered against walk/PREREG-PXD026748-shotgun-ingest.md, which is committed before this runs.

What it writes: the file into the raw store under its digest (idempotent; the raw store is an
input, not a derived store), and a scratch graph under the scratch home. It never rebuilds the
live home. Optional flags: --home (raw store home, default ~/.bzk-omics) and --scratch (default
/tmp/bzk-e3, whose raw/ and cache/ are linked to the home's).
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from bzk.adapters.maxquant import read_table
from bzk.adapters.maxquant_protein_groups import MaxQuantProteinGroupsAdapter
from bzk.curation.loader import load_path
from bzk.provenance import raw_store
from bzk.rebuild import _adapter_for, rebuild

EXPECTED = "sha256:b74a1797b49b85ff3ba88e2739e47dad242583eedd58945417c239ba9fd7f884"
RECORD = Path("data/curation/curation_PXD026748_shotgun.json")

parser = argparse.ArgumentParser()
parser.add_argument("file", type=Path)
parser.add_argument("--home", type=Path, default=Path.home() / ".bzk-omics")
parser.add_argument("--scratch", type=Path, default=Path("/tmp/bzk-e3"))
args = parser.parse_args()

print("== 1. store ==")
data = args.file.expanduser().read_bytes()
digest = raw_store.content_hash(data)
print("digest", digest, "| matches record:", digest == EXPECTED)
if digest != EXPECTED:
    raise SystemExit("STOP: the file is not the one the record names")
raw_store.store(data, "proteinGroups.txt", home=args.home)
stored = raw_store.verify(EXPECTED, filename="proteinGroups.txt", home=args.home)
print("stored and re-verified at", stored)

print("\n== 2. dispatch ==")
loaded = load_path(RECORD)
adapter = _adapter_for(loaded, stored, None)
print("adapter:", type(adapter).__name__, "| declared quantity:",
      getattr(getattr(adapter, "declared", None), "quantity", None))
if not isinstance(adapter, MaxQuantProteinGroupsAdapter):
    raise SystemExit("STOP: the protein-groups adapter did not claim the file")

print("\n== 3. parse (offline, no graph) ==")
parsed = adapter.parse(stored, loaded.sample_mapping())
report = adapter.report
assert report is not None
for name in ("rows_read", "spill_lines", "dropped_decoy_or_contaminant", "groups_emitted",
             "refused_empty_group", "distinct_accessions", "cells"):
    print(f"{name}: {getattr(report, name)}")
print("refusals by reason:", dict(Counter(r.reason for r in parsed.refusals)))
cells = [c for _, batch in parsed.cells for c in batch]
print("cells by quantity:", dict(sorted(Counter(c.quantity for c in cells).items())))
print("cells with value > 0 by quantity:",
      dict(sorted(Counter(c.quantity for c in cells if c.value is not None and c.value > 0).items())))
analysis = next(n for n in parsed.nodes if n.get("kind") == "processing")
print("ingestion Analysis quantity:", analysis["quantity"])

table = read_table(stored)
col = {c: i for i, c in enumerate(table.header)}
site_only = {r[col["id"]] for r in table.rows if r[col["Only identified by site"]] == "+"}
emitted = set(report.observation_of_row)
print("'Only identified by site' rows in file:", len(site_only),
      "| among emitted observations:", len(site_only & emitted),
      "| among rows dropped as decoy/contaminant:", len(site_only - emitted))

print("\n== 4. rebuild in the scratch home ==")
args.scratch.mkdir(parents=True, exist_ok=True)
for sub in ("raw", "cache"):
    link = args.scratch / sub
    if not link.exists():
        link.symlink_to(args.home / sub)
rb = rebuild(home=args.scratch)
for name in ("deposits_ingested", "site_observations", "protein_observations", "cells_staged",
             "ingestions_skipped"):
    print(f"{name}: {getattr(rb, name)}")
print("refusals:", len(rb.refusals), dict(Counter(r.reason for r in rb.refusals)))
print("\ndone; the live home's graph and quant stores were not touched")
