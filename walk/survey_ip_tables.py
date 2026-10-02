"""Prompt 23 — survey of the public IP tables. Measurement only; prints a report, writes nothing.

    uv run python walk/survey_ip_tables.py FILE [FILE ...]

Every number in `walk/SURVEY-public-IP-tables.md` is reproduced by running this on the files named
there. Any subset of files may be given; a file this script does not recognise by digest is still
surveyed, under its own name.

**Blindness (prompt 23 §1).** Nothing per-row is printed: no identity column, no accession, no gene
name, no cell value. What leaves this script is column headers, title rows, sheet names, counts,
fractions and deciles. No row is filtered, sorted or looked up by protein.

**Type is decided by the repository's own reader.** `PerseusAdapter.sniff` is called unchanged, on
an instance built without `__init__` because `sniff` reads no instance state and its constructor
wants a declared analysis this survey has no business inventing. The header row is then the first
row within `HEADER_SCAN_ROWS` carrying a `_is_stamped` cell, or row 1 when none does — the same
scan, not a new heuristic.
"""

from __future__ import annotations

import hashlib
import math
import re
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from bzk.adapters import spreadsheet
from bzk.adapters.perseus import HEADER_SCAN_ROWS, PerseusAdapter, _is_stamped

#: Digests of the files prompt 23 names, so the report can say which file it is looking at. The
#: first four were fetched and checked on 2026-10-02; S3's is the reviewer-supplied digest at
#: `ROADMAP.md:11943–11944`, and no file with it was reachable from this container.
KNOWN = {
    "e2680e30fd6ea73a327f9e1736eab815245cd16fb1f0c4a8e8f517fa2b88a0db": "BJC Supplementary Data 1",
    "da870551116f00b4ea5a89ae930156e503283d2ee7a4eebe5c03acfb54651509": "BJC Supplementary Data 2",
    "9c9d9dfbd69078053caed1158752a14c31bdc5e4364e25d3401f3c691b3b9fca": "BJC Supplementary Data 3",
    "214a79cae8ae41143e896fca09d7ab3ee3b894e4dbb4d43f298b388d97fb8ab1": (
        "PXD018299 ISG15 interactome (HAP1_USP18KO_ISG15_interactome_proteinGroups.xlsx)"
    ),
    "2ea450f3a63721fa6e59898392e8d07d2e002abbb5cf16004340fe838d3f52e9": "PXD055843 Supplementary Data S3",
}
INTERACTOME = "PXD018299 ISG15 interactome"

#: Per-sample intensity columns in MaxQuant's own naming. Used only for a file with no type stamp,
#: where the header carries no Perseus `main`-column marker; in a stamped file the quantitative
#: block is the unprefixed columns, which is Perseus' own split.
MAXQUANT_QUANT = re.compile(r"^(LFQ intensity|Intensity) \S")

#: Column names that carry a test outcome in Perseus' naming. Matched case-insensitively against
#: the header with any type prefix removed. MaxQuant's protein `Q-value` is an *identification*
#: score and is deliberately not here (`ROADMAP.md:12545`).
STATISTIC = re.compile(
    r"(t-test|p-value|q-value .+|significant|difference|test statistic|fdr)", re.IGNORECASE
)

#: A trailing replicate index, `_1` or `-1`, for grouping sample headers as their names state.
REPLICATE = re.compile(r"^(?P<group>.+?)[-_](?P<rep>\d+)$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_perseus(path: Path) -> bool:
    """The repository's own decision, unchanged (`bzk/adapters/perseus.py` `sniff`)."""
    return PerseusAdapter.sniff(object.__new__(PerseusAdapter), path)


def header_index(text: list[list[str]]) -> int:
    for i, row in enumerate(text[:HEADER_SCAN_ROWS]):
        if any(_is_stamped(c) for c in row):
            return i
    return 0


def strip_prefix(name: str) -> str:
    return name[3:] if _is_stamped(name) else name


def as_float(v: Any) -> float | None:
    if isinstance(v, bool):
        return None
    if isinstance(v, int | float):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v)
        except ValueError:
            return None
    return None


def kind(v: Any) -> str:
    """One of empty / nan / zero / value / text for a quantitative cell."""
    if v is None or (isinstance(v, str) and v.strip() == ""):
        return "empty"
    f = as_float(v)
    if f is None:
        return "text"
    if math.isnan(f):
        return "nan"
    if f == 0:
        return "zero"
    return "value"


def deciles(values: list[float]) -> str:
    if len(values) < 2:
        return "n<2"
    qs = statistics.quantiles(values, n=10, method="inclusive")
    return " ".join(f"{q:.4g}" for q in [min(values), *qs, max(values)])


def classify_unstamped(column: list[Any]) -> str:
    """Content type of a column in a file with no stamp: numeric, categorical or text.

    Not a type stamp and not presented as one. Numeric: every non-empty cell parses as a number.
    Categorical: none does and at most ten distinct values occur. Text otherwise.
    """
    filled = [v for v in column if kind(v) != "empty"]
    if filled and all(as_float(v) is not None for v in filled):
        return "numeric"
    if len({str(v) for v in filled}) <= 10:
        return "categorical"
    return "text"


def survey(path: Path) -> dict[str, Any]:
    digest = sha256(path)
    label = KNOWN.get(digest, f"(unrecognised) {path.name}")
    out: list[str] = [f"## {label}", "", f"- file: `{path.name}`", f"- SHA-256: `{digest}`"]
    raw = path.read_bytes()
    if not spreadsheet.looks_like_a_workbook(raw):
        out.append("- not a workbook; this survey reads `.xlsx` only")
        return {"label": label, "lines": out, "samples": []}

    import openpyxl

    wb = openpyxl.load_workbook(path, read_only=True)
    sheetnames = list(wb.sheetnames)
    wb.close()
    perseus = is_perseus(path)
    out.append(f"- sheets: {sheetnames}")
    out.append(
        f"- `PerseusAdapter.sniff` (first sheet): **{perseus}** "
        f"→ {'Perseus export' if perseus else 'not a Perseus export (no type-prefix stamp)'}"
    )

    samples: list[str] = []
    for sheet in sheetnames:
        values = spreadsheet.rows(raw, sheet=sheet)
        text = spreadsheet.text_rows(raw, sheet=sheet)
        h = header_index(text)
        header = text[h] if text else []
        width = max((len(r) for r in text), default=0)
        stamped = [c for c in header if _is_stamped(c)]
        out += ["", f"### sheet `{sheet}`", ""]
        out.append(f"- rows in sheet: {len(text)}; widest row: {width} cells")
        out.append(f"- header row: {h + 1}; type-prefix stamped cells in it: {len(stamped)}")
        for i in range(h):
            cells = [c for c in text[i] if c]
            out.append(f"- row {i + 1} above the header (title), verbatim: {cells}")
        named = [j for j, c in enumerate(header) if c]
        unnamed = [j for j, c in enumerate(header) if not c]
        body = values[h + 1 :]
        populated = [r for r in body if any(kind(r[j]) != "empty" for j in named if j < len(r))]
        stray = sum(
            1 for r in body for j in range(len(r)) if j not in named and kind(r[j]) != "empty"
        )
        out.append(f"- data rows (any non-empty cell under a named header): **{len(populated)}**")
        out.append(f"- columns with a named header: {len(named)}; unnamed: {len(unnamed)}")
        out.append(f"- non-empty cells under no named header (not printed): {stray}")
        if stray:
            where = Counter(
                (j + 1, "numeric" if as_float(r[j]) is not None else "text")
                for r in body
                for j in range(len(r))
                if j not in named and kind(r[j]) != "empty"
            )
            out.append(
                "  - by (1-based column, content type): "
                + ", ".join(f"col {c} {t}: {n}" for (c, t), n in sorted(where.items()))
            )

        def col(j: int, rows: list[tuple[Any, ...]] = populated) -> list[Any]:
            return [r[j] if j < len(r) else None for r in rows]

        groups: dict[str, list[str]] = {
            "quantitative": [],
            "categorical": [],
            "numeric": [],
            "text": [],
        }
        if stamped:
            prefix_kind = {"C: ": "categorical", "N: ": "numeric", "T: ": "text", "M: ": "numeric"}
            for j in named:
                c = header[j]
                groups[prefix_kind[c[:3]] if _is_stamped(c) else "quantitative"].append(c)
            basis = "Perseus type prefix (unprefixed = main/quantitative; M: listed as numeric)"
        else:
            for j in named:
                c = header[j]
                groups[
                    "quantitative" if MAXQUANT_QUANT.match(c) else classify_unstamped(col(j))
                ].append(c)
            basis = (
                "no stamp: quantitative = per-sample `Intensity`/`LFQ intensity`; others by "
                "content (all numeric / ≤10 distinct non-numeric / otherwise text)"
            )
        out += ["", f"Column groups — basis: {basis}", ""]
        for g, cs in groups.items():
            out.append(f"- **{g}** ({len(cs)}): {cs}")

        quant = [j for j in named if header[j] in groups["quantitative"]]
        sample_cols = [header[j] for j in quant if REPLICATE.match(header[j])]
        samples += sample_cols
        by_group: dict[str, list[str]] = {}
        for c in sample_cols:
            m = REPLICATE.match(c)
            assert m
            by_group.setdefault(m["group"], []).append(m["rep"])
        out += ["", "Sample groups as the headers name them (trailing `-n`/`_n` = replicate):", ""]
        for g, reps in by_group.items():
            out.append(f"- `{g}`: {len(reps)} replicates ({', '.join(reps)})")
        role_words = re.compile(
            r"\b(ip|iap|igg|control|ctrl|input|mock|bead|empty)\b", re.IGNORECASE
        )
        roles = [c for c in sample_cols if role_words.search(c)]
        out.append(
            f"- sample headers naming a role (IP / control / input / IgG / mock / beads): "
            f"{roles if roles else 'none'}"
        )

        stats = [header[j] for j in named if STATISTIC.search(strip_prefix(header[j]))]
        out += ["", f"Statistics columns (Perseus test naming): {stats if stats else 'none'}"]
        for j in named:
            c = header[j]
            if c not in stats:
                continue
            cells = col(j)
            if re.search("significant", c, re.IGNORECASE):
                counts = Counter("+" if str(v).strip() == "+" else "blank" for v in cells)
                out.append(f"- `{c}`: {dict(counts)}")
            else:
                fs = [f for v in cells if (f := as_float(v)) is not None and not math.isnan(f)]
                bins = Counter(
                    "<0.01" if f < 0.01 else "<0.05" if f < 0.05 else ">=0.05" for f in fs
                )
                out.append(
                    f"- `{c}`: {len(fs)} numeric of {len(cells)}; bins {dict(sorted(bins.items()))}"
                )
        flags = [
            header[j]
            for j in named
            if strip_prefix(header[j])
            in ("Reverse", "Potential contaminant", "Only identified by site")
        ]
        for c in flags:
            j = header.index(c)
            n = sum(1 for v in col(j) if str(v).strip() == "+")
            out.append(f"- `{c}` marked `+`: {n} of {len(populated)} rows")

        out += [
            "",
            "Missingness over the quantitative block (cells under quantitative headers):",
            "",
        ]
        total: Counter[str] = Counter()
        per: list[str] = []
        for j in quant:
            ks = Counter(kind(v) for v in col(j))
            total += ks
            fs = [f for v in col(j) if (f := as_float(v)) is not None and not math.isnan(f) and f]
            per.append(
                f"| `{header[j]}` | {ks['nan']} | {ks['empty']} | {ks['zero']} | "
                f"{ks['text']} | {ks['value']} | {deciles(fs)} |"
            )
        cells_total = sum(total.values())
        out.append(
            f"- total cells {cells_total}: NaN {total['nan']}, empty {total['empty']}, "
            f"zero {total['zero']}, non-numeric text {total['text']}, value {total['value']}"
        )
        missing = total["nan"] + total["empty"] + total["zero"]
        out.append(
            f"- any missing (NaN/empty/zero) in the quantitative block: **{missing > 0}** "
            f"({missing} of {cells_total})"
        )
        out += [
            "",
            "| column | NaN | empty | zero | text | value | min, deciles 10–90, max (non-zero finite) |",
            "|---|---|---|---|---|---|---|",
            *per,
        ]
        imput = [c for r in text[: h + 1] for c in r if "imput" in c.lower()]
        out += [
            "",
            (
                "Imputation markers (any header/title cell containing `imput`): "
                f"{imput if imput else 'none'}"
            ),
        ]
    return {"label": label, "lines": out, "samples": samples}


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    results = [survey(Path(p)) for p in argv]
    print("# Survey of public IP tables — measurement output\n")
    for r in results:
        print("\n".join(r["lines"]))
        print()
    ref = [r for r in results if r["label"].startswith(INTERACTOME)]
    bjc = [r for r in results if r["label"].startswith("BJC")]
    if ref and bjc:
        target = set(ref[0]["samples"])
        print("## Sample-header match against the interactome (verbatim, headers only)\n")
        for r in bjc:
            hit = [s for s in r["samples"] if s in target]
            print(f"- {r['label']}: {len(hit)} of {len(r['samples'])} sample headers match: {hit}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
