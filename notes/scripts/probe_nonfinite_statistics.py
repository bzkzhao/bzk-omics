"""Read-only probe: does any Perseus statistics cell hold a non-finite value?

Run on bzk's Mac, from the repo root. Reads only. Writes nothing. Ingests
nothing. Mints nothing.

    uv run python notes/scripts/probe_nonfinite_statistics.py

Why: prompt 33 §2.3 (f61f6fd) made every Perseus statistics read refuse a
non-finite cell. float() previously accepted NaN/inf, so such a cell used to
pass through as a number. Perseus writes the NEGATED log, -log10(p), and
-log10(0) is inf -- so an underflowed p is a plausible Inf in a real table.
PerseusError is never downgraded, so ONE such cell now refuses the whole file.
No committed table carries one; S1/S3 had never been measured for it.

**This version reads through the adapter's own `_read`**, which dispatches between the
tab-separated and spreadsheet containers and composes the multi-row header.
A first version scanned two raw rows for literal column names and found zero
statistics columns in S1 -- a vacuous pass. The deposit's export carries THREE
header rows, merged qualifier spans that must be filled before composition, and
`#!{...}` annotation rows between header and data. Reimplementing any of that
is how the first version produced a false negative, so none of it is
reimplemented here.
"""

import dataclasses
import math
import sys
from pathlib import Path

from bzk.adapters.perseus import (
    DeclaredContrast,
    PerseusAdapter,
    DeclaredAnalysis,
)
from bzk.curation.loader import ContrastArms
from bzk.ontology.invariants import NODE_TYPE_KEY

STAT_MARKERS = ("Difference", "q-value", "p-value", "Test statistic")

#: A declaration good enough to construct the adapter. Never used to ingest: this probe only
#: calls `_read_workbook`, which composes the header and splits the data rows.
def _probe_arms() -> ContrastArms:
    """A `ContrastArms` built from whatever fields this checkout's dataclass declares.

    `contrast_id` exists only from `f61f6fd` onward. Constructing it by name would make this
    probe refuse to run on an older tree, and comparing the two trees is exactly what the
    probe is for, so the field list is read rather than assumed.
    """
    names = {f.name for f in dataclasses.fields(ContrastArms)}
    kwargs: dict[str, object] = {
        "numerator": ("bzk:s1",),
        "denominator": ("bzk:s2",),
        "kind": "condition",
    }
    if "contrast_id" in names:
        kwargs["contrast_id"] = "bzk:probe"
    unknown = names - set(kwargs) - {"numerator", "denominator", "kind"}
    if unknown:
        print(f"# note: ContrastArms also declares {sorted(unknown)}; left at their defaults")
    return ContrastArms(**kwargs)  # type: ignore[arg-type]


_PROBE_CONTRAST = DeclaredContrast(
    column_suffix="__probe__",
    contrast={NODE_TYPE_KEY: "Contrast", "id": "bzk:probe", "numerator": "a", "denominator": "b"},
    arms=_probe_arms(),
)


def _adapter() -> PerseusAdapter:
    return PerseusAdapter(
        DeclaredAnalysis(
            quantity="lfq",
            filters_applied=[],
            test="welch_t",
            fdr_method="BH",
            external_version="probe",
        ),
        [_PROBE_CONTRAST],
    )


def probe(path: Path, adapter: PerseusAdapter) -> tuple[int, int]:
    """(non-finite cells, statistics columns scanned) for one file."""
    header, data = adapter._read(path.read_bytes(), path)
    stat_cols = [(i, h) for i, h in enumerate(header) if any(m in h for m in STAT_MARKERS)]
    print(f"  {len(data)} data rows, {len(header)} columns, "
          f"{len(stat_cols)} statistics columns")
    for i, h in stat_cols:
        print(f"    scanning: {h!r}")
    bad = 0
    for line_no, row in data:
        for i, name in stat_cols:
            if i >= len(row):
                continue
            text = row[i].strip()
            if not text:
                continue
            try:
                v = float(text)
            except ValueError:
                continue  # unparseable: refused before this build too
            if not math.isfinite(v):
                bad += 1
                print(f"    NON-FINITE line {line_no} col {name!r}: {text!r}")
    return bad, len(stat_cols)


def _targets(args: list[str]) -> tuple[list[Path], list[str]]:
    if args:
        return [Path(a) for a in args], []
    found: list[Path] = []
    notes: list[str] = []
    try:
        from bzk.sources import pxd055843_perseus as s1

        p = s1.locate()
        found.append(p)
        notes.append(f"S1 located by digest via pxd055843_perseus.locate(): {p}")
    except BaseException as exc:
        notes.append(f"S1 NOT located by digest ({type(exc).__name__}): {exc}")
    raw = Path.home() / ".bzk-omics" / "raw"
    if raw.is_dir():
        others = sorted(
            q for q in raw.rglob("*")
            if q.is_file()
            and q.suffix.lower() in {".xlsx", ".xlsm", ".txt", ".tsv"}
            and q not in found
        )
        found += others
        notes.append(f"{len(others)} further candidate(s) under {raw} (.xlsx and .txt)")
    else:
        notes.append(f"no content store at {raw}")
    return found, notes


if __name__ == "__main__":
    targets, notes = _targets(sys.argv[1:])
    for n in notes:
        print(f"# {n}")
    print()
    if not targets:
        print("INCONCLUSIVE: nothing to read.")
        raise SystemExit(2)
    adapter = _adapter()
    total = 0
    scanned: list[tuple[Path, int]] = []
    refused: list[str] = []
    for q in targets:
        print(f"{q}:")
        if not q.exists():
            print("  MISSING")
            refused.append(f"{q.name}: missing")
            continue
        try:
            bad, ncols = probe(q, adapter)
            total += bad
            scanned.append((q, ncols))
        except Exception as exc:
            print(f"  NOT READ ({type(exc).__name__}: {exc})")
            refused.append(f"{q.name}: {type(exc).__name__}")
    print()
    with_stats = [(q, n) for q, n in scanned if n]
    without = [q for q, n in scanned if not n]
    print(f"Read {len(scanned)} file(s); {len(with_stats)} carried statistics columns.")
    for q, n in with_stats:
        print(f"  {n} statistics column(s): {q}")
    for q in without:
        print(f"  NO statistics columns (nothing scanned): {q}")
    for r in refused:
        print(f"  not read: {r}")
    print()
    if not with_stats:
        print("INCONCLUSIVE: no file yielded a single statistics column, so nothing was")
        print("actually scanned. A clean result here would be vacuous. Do not treat this")
        print("as evidence that f61f6fd changes nothing.")
        raise SystemExit(2)
    if total:
        print(f"VERDICT: {total} non-finite statistics cell(s).")
        print("f61f6fd WOULD refuse the file(s) named above. Report before PXD055843 unblocks.")
    else:
        print("VERDICT: no non-finite statistics cell, across the statistics columns listed")
        print("above. f61f6fd changes nothing for those files. Files listed as carrying no")
        print("statistics columns are NOT covered by this result.")
