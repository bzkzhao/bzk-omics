"""Exploratory, NOT pre-registered: how PV1's deviation is distributed. Read-only."""
import importlib.util, math, statistics, sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("m", "notes/scripts/measure_adr0038.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
from bzk.adapters.perseus import DIFFERENCE, PerseusAdapter, _cell_value


def devs(rows, columns, num, den, diff):
    out = []
    for _, row in rows:
        d = _cell_value(row, columns, diff)
        vals = [_cell_value(row, columns, c) for c in num + den]
        if d is None or any(v is None for v in vals):
            continue
        a, b = vals[: len(num)], vals[len(num):]
        out.append((abs(d - (sum(a) / len(a) - sum(b) / len(b))), d, vals))
    return out


def report(label, ds):
    x = sorted(v for v, _, _ in ds)
    q = lambda p: x[min(len(x) - 1, int(p * len(x)))]
    print(f"{label}: n {len(x)}; <=2e-5 {sum(v <= 2e-5 for v in x)}; <=1e-3 {sum(v <= 1e-3 for v in x)}; "
          f"<=0.1 {sum(v <= 0.1 for v in x)}; median {q(0.5):.3g}; p90 {q(0.9):.3g}; p99 {q(0.99):.3g}; max {x[-1]:.3g}")


def main():
    from bzk.sources import pxd055843_perseus as src
    path = src.locate()
    declaration, contrast = src.declared()
    header, rows = PerseusAdapter(declaration, [contrast])._read(path.read_bytes(), path)
    columns = {n: i for i, n in enumerate(header)}
    diff = DIFFERENCE.format(suffix=src.COLUMN_SUFFIX)
    loaded = {p.name: m._load(p) for p in m.RECS}
    num, den = m.declared_arms(loaded)[("curation_PXD055843.json", "siUSP24_IFN_vs_siC_IFN")]
    print("D1 numerator columns:", num)
    print("D1 denominator columns:", den)
    print("D2 other quantitative-looking columns:",
          [h for h in header if h.startswith("Set ") and h not in num + den][:20])
    ds = devs(rows, columns, num, den, diff)
    report("D3 declared order", ds)
    report("D3 reversed order", devs(rows, columns, den, num, diff))
    # Imputation proxy: a downshifted-normal draw sits low in its column.
    lows = {}
    for c in num + den:
        col = sorted(v for _, r in rows if (v := _cell_value(r, columns, c)) is not None)
        lows[c] = col[int(0.10 * len(col))]
    low_flags = []
    for _, row in rows:
        vals = [_cell_value(row, columns, c) for c in num + den]
        low_flags.append(any(v is not None and v <= lows[c] for v, c in zip(vals, num + den)))
    agree = [v <= 1e-3 for v, _, _ in ds]
    for flag in (True, False):
        sel = [a for a, f in zip(agree, low_flags) if f is flag]
        print(f"D4 rows with {'any' if flag else 'no'} arm value in its column's lowest 10%: "
              f"{len(sel)}, agreeing within 1e-3: {sum(sel)}")
    signed = [d - (sum(v[:3]) / 3 - sum(v[3:]) / 3) for _, d, v in ds]
    print(f"D5 signed deviation: mean {statistics.fmean(signed):.3g}, "
          f"median {statistics.median(signed):.3g}")
    worst = sorted(ds, key=lambda t: -t[0])[:3]
    for v, d, vals in worst:
        print(f"D6 worst: dev {v:.3g}; Difference {d:.4g}; arm values {[round(x, 3) for x in vals]}")


if __name__ == "__main__":
    main()
