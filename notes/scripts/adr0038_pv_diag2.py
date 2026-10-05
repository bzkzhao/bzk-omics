"""Exploratory, NOT pre-registered: the rows PV1 refuses, and what the file's other test columns say
about them. Read-only; prints numbers only."""
import importlib.util
from collections import Counter

spec = importlib.util.spec_from_file_location("m", "notes/scripts/measure_adr0038.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
from bzk.adapters.perseus import (DIFFERENCE, MINUS_LOG_P, P_VALUE, Q_VALUE, PerseusAdapter,
                                  _cell_value)


def raw(row, columns, name):
    i = columns.get(name)
    return None if i is None else row[i]


def main():
    from bzk.sources import pxd055843_perseus as src
    path = src.locate()
    declaration, contrast = src.declared()
    header, rows = PerseusAdapter(declaration, [contrast])._read(path.read_bytes(), path)
    columns = {n: i for i, n in enumerate(header)}
    sfx = src.COLUMN_SUFFIX
    diff = DIFFERENCE.format(suffix=sfx)
    stats = [c for c in (MINUS_LOG_P.format(suffix=sfx), P_VALUE.format(suffix=sfx),
                         Q_VALUE.format(suffix=sfx)) if c in columns]
    other = sorted(h for h in header if sfx in h and h != diff and h not in stats)
    print("E1 statistics columns present:", stats, "| other columns carrying the suffix:", other)
    loaded = {p.name: m._load(p) for p in m.RECS}
    num, den = m.declared_arms(loaded)[("curation_PXD055843.json", "siUSP24_IFN_vs_siC_IFN")]
    fail, zero_d = [], 0
    for _, row in rows:
        d = _cell_value(row, columns, diff)
        vals = [_cell_value(row, columns, c) for c in num + den]
        dev = abs(d - (sum(vals[:3]) / 3 - sum(vals[3:]) / 3))
        zero_d += d == 0
        if dev > 1e-3:
            fail.append((dev, d, row))
    print(f"E2 rows: {len(rows)}; Difference exactly 0: {zero_d}; refused at 1e-3: {len(fail)}; "
          f"refused with Difference exactly 0: {sum(d == 0 for _, d, _ in fail)}")
    print("E3 raw Difference cells among refused rows:",
          Counter(raw(r, columns, diff) for _, _, r in fail).most_common(5))
    for c in stats + other:
        print(f"E4 {c!r} among refused rows:",
              Counter(raw(r, columns, c) for _, _, r in fail).most_common(5))
        passed = [r for _, r in rows if all(r is not f for _, _, f in fail)]
        cells = Counter(raw(r, columns, c) == "" or raw(r, columns, c) is None for r in passed)
        print(f"   among the {len(passed)} agreeing rows, blank cells: {cells.get(True, 0)}")
    print("E5 refused deviations, sorted:", [round(v, 3) for v, _, _ in sorted(fail, key=lambda t: -t[0])])


if __name__ == "__main__":
    main()
