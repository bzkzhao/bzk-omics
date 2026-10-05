"""ADR-0038's instrument. Read-only over the repository; nothing is written anywhere.

Usage:
    uv run python notes/scripts/measure_adr0038.py            # M1-M10, container, no raw data
    uv run python notes/scripts/measure_adr0038.py --s1       # PV, bzk's Mac, needs PXD055843 S1

M1-M10 were run at `ebc0750` and their output is reproduced verbatim in ADR-0038. PV is that
record's pre-registration: it reads PXD055843's Supplementary Data S1 from the content store by the
digest in `data/curation/analysis_PXD055843_siUSP24_IFN_vs_siC_IFN.json`, and prints three lines.
It retains nothing and writes nothing.

**Every arm below is a curator's statement, selected once by sample fields and printed as the
mapping keys it resolves to.** Nothing here selects a column by a token or a substring, except M2
and PV's third line, which do it on purpose to show what that would catch.
"""

from __future__ import annotations

import copy
import json
import math
import re
import subprocess
import sys
from pathlib import Path

from bzk.adapters import maxquant_protein_groups as mpg
from bzk.adapters import maxquant_sites as mqs
from bzk.adapters.base import SampleMapping
from bzk.curation import loader
from bzk.ontology import keys, schema

ROOT = Path(__file__).resolve().parents[2]
CURATION = ROOT / "data" / "curation"
RECS = sorted(CURATION.glob("curation_*.json"))

#: (record, contrast id) -> (numerator spec, denominator spec), over `Sample` fields. A regex value
#: matches inside the field; every other value must equal it.
ARMS: dict[tuple[str, str], tuple[dict[str, object], dict[str, object]]] = {
    ("curation_PXD018299.json", "KO_IFN_vs_WT_IFN"): (
        {"genotype": "USP18-/-", "treatment": "IFN-alpha2b_1000U_per_mL"},
        {"genotype": "WT", "treatment": "IFN-alpha2b_1000U_per_mL"},
    ),
    ("curation_PXD018299.json", "KO_vs_WT_unstimulated"): (
        {"genotype": "USP18-/-", "treatment": "none"},
        {"genotype": "WT", "treatment": "none"},
    ),
    ("curation_PXD026748.json", "PLproWT_vs_PLproMut_in_WT"): (
        {"genotype": "WT", "treatment": re.compile(r"PLpro WT ")},
        {"genotype": "WT", "treatment": re.compile(r"PLpro mutant ")},
    ),
    ("curation_PXD026748.json", "PLproWT_vs_PLproMut_in_ISG15KO"): (
        {"genotype": "ISG15-/-", "treatment": re.compile(r"PLpro WT ")},
        {"genotype": "ISG15-/-", "treatment": re.compile(r"PLpro mutant ")},
    ),
    ("curation_PXD055843.json", "siUSP24_IFN_vs_siC_IFN"): (
        {"genotype": "siUSP24", "treatment": "IFN-B"},
        {"genotype": "siC", "treatment": "IFN-B"},
    ),
}


def _load(path: Path) -> tuple[dict, loader.LoadedCuration]:
    record = json.loads(path.read_text())
    return record, loader.load(record)


def _pick(mapping: dict, spec: dict) -> list[str]:
    out = []
    for key, sample in mapping.items():
        if all(
            bool(want.search(sample.get(f) or ""))
            if isinstance(want, re.Pattern)
            else sample.get(f) == want
            for f, want in spec.items()
        ):
            out.append(key)
    return out


def declared_arms(loaded: dict) -> dict[tuple[str, str], tuple[list[str], list[str]]]:
    return {
        k: (_pick(loaded[k[0]][0]["mapping"], num), _pick(loaded[k[0]][0]["mapping"], den))
        for k, (num, den) in ARMS.items()
    }


def _contrast_ids(loaded: dict, arms: dict, variant: str) -> dict[str, str]:
    """Every existing contrast's id under one identity option, with `schema.IDENTITY` patched in
    memory and restored in `finally`."""
    out = {}
    spec = schema.IDENTITY["Contrast"]
    for (rname, cid), (num, den) in arms.items():
        _, lc = loaded[rname]
        node = lc.contrast_nodes[cid]
        props: dict[str, object] = {
            "numerator": node["numerator"],
            "denominator": node["denominator"],
        }
        anchors = {"Experiment": lc.experiment_id}
        children = None
        if variant == "a_roles":
            patched = schema.Identity(
                spec.fields + ("numerator_role", "denominator_role"), spec.anchors
            )
            props |= {"numerator_role": None, "denominator_role": None}
        elif variant == "b1_member_ids":
            patched = schema.Identity(
                spec.fields + ("numerator_samples", "denominator_samples"), spec.anchors
            )
            props |= {
                "numerator_samples": sorted(lc.sample_ids[x] for x in num),
                "denominator_samples": sorted(lc.sample_ids[x] for x in den),
            }
        elif variant == "b2_member_values":
            patched = schema.Identity(
                spec.fields,
                spec.anchors,
                (("Sample", "NUMERATOR_SAMPLE", tuple(schema.IDENTITY["Sample"].fields)),),
            )
            by_id = {n["id"]: n for n in lc.nodes}
            children = {"Sample": [by_id[lc.sample_ids[x]] for x in num + den]}
        else:  # c_labels: identity unchanged
            patched = spec
        schema.IDENTITY["Contrast"] = patched
        try:
            out[cid] = keys.evidence_id("Contrast", props, anchors, children)
        finally:
            schema.IDENTITY["Contrast"] = spec
    return out


def measure() -> None:
    loaded = {p.name: _load(p) for p in RECS}

    print("M1 anchors and relationships")
    on = {
        a: [(lab, rel) for lab, s in schema.IDENTITY.items() for anc, rel in s.anchors if anc == a]
        for a in ("Contrast", "Sample")
    }
    print("  anchors on Contrast:", on["Contrast"])
    print("  anchors on Sample:", on["Sample"])
    print(
        "  rel tables touching Contrast:",
        [(t.name, t.src, t.dst) for t in schema.REL_TABLES if "Contrast" in (t.src, t.dst)],
    )
    base = {}
    for name, (_, lc) in loaded.items():
        for cid, node in lc.contrast_nodes.items():
            base[cid] = node["id"]
            print(
                f"  {name} {cid}: {node['numerator']!r} / {node['denominator']!r} -> {node['id']}"
            )
    print("  contrasts minted by the loader:", len(base))
    experiments = {lc.experiment_id for _, lc in loaded.values()}
    print(f"  records {len(loaded)}, distinct Experiment ids {len(experiments)}")

    print("M2 do arm strings compose from samples, or substring-match mapping keys?")
    for name, (record, _) in loaded.items():
        for entry in record.get("contrasts_of_interest") or ():
            for side in ("numerator", "denominator"):
                s = entry[side]
                eq = sum(
                    1
                    for v in record["mapping"].values()
                    if s in (v.get("genotype"), v.get("treatment"))
                    or s == f"{v.get('genotype')} + {v.get('treatment')}"
                )
                sub = sum(1 for k in record["mapping"] if s in k)
                print(f"  {entry['id']} {side} {s!r}: field-equal {eq}, key-substring {sub}")

    print("M3 an unknown key inside a contrasts_of_interest entry")
    record = copy.deepcopy(loaded["curation_PXD018299.json"][0])
    record["contrasts_of_interest"][0]["numerator_sampels"] = ["Ratio mod/base KO_IFN_1"]
    try:
        lc2 = loader.load(record)
        same = lc2.contrast_nodes == loaded["curation_PXD018299.json"][1].contrast_nodes
        print("  loaded, not refused; contrast nodes identical to the unmodified record:", same)
    except Exception as exc:  # noqa: BLE001 - the measurement is which branch runs
        print("  refused:", type(exc).__name__)

    print("M4 declared arms (mapping keys)")
    arms = declared_arms(loaded)
    ident = [f for f in schema.IDENTITY["Sample"].fields if f != "replicate"]
    for (rname, cid), (num, den) in arms.items():
        mapping = loaded[rname][0]["mapping"]
        homo = all(
            len({json.dumps(mapping[x].get(f)) for x in arm}) == 1
            for arm in (num, den)
            for f in ident
        )
        print(
            f"  {cid}: n {len(num)}/{len(den)}, overlap {len(set(num) & set(den))}, "
            f"one value per identifying field but replicate: {homo}"
        )
        print(f"    numerator {num}")
        print(f"    denominator {den}")
    print("  Contrast-Sample edges implied:", sum(len(a) + len(b) for a, b in arms.values()))

    print("M5 re-mint cost of each identity option")
    for variant in ("a_roles", "b1_member_ids", "b2_member_values", "c_labels"):
        ids = _contrast_ids(loaded, arms, variant)
        moved = [c for c in base if ids[c] != base[c]]
        print(f"  {variant}: Contrast ids moved {len(moved)} of {len(base)}")
    row = {"protein_adjusted": "not_applied", "adjustment_method": None}
    anch = {"Analysis": "bzk:" + "0" * 32, "SiteObservation": "bzk:" + "1" * 32}
    moved_contrast = _contrast_ids(loaded, arms, "a_roles")["KO_IFN_vs_WT_IFN"]
    r0 = keys.evidence_id("DifferentialResult", row, anch | {"Contrast": base["KO_IFN_vs_WT_IFN"]})
    r1 = keys.evidence_id("DifferentialResult", row, anch | {"Contrast": moved_contrast})
    print("  a representative DifferentialResult id follows its Contrast:", r0 != r1)
    writers = subprocess.run(
        ["git", "grep", "-l", "site_change_set(\\|PerseusAdapter(", "--", "bzk/sources"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    ).stdout.split()
    print("  result-writing source modules:", writers)

    print("M6 option b's coupling: would 190e696's Sample re-mint have moved a Contrast?")
    spec_s = schema.IDENTITY["Sample"]
    schema.IDENTITY["Sample"] = schema.Identity(
        tuple(f for f in spec_s.fields if f not in ("role", "bait")), spec_s.anchors
    )
    try:
        before = {p.name: _load(p) for p in RECS}
        b_pre = _contrast_ids(before, arms, "b1_member_ids")
    finally:
        schema.IDENTITY["Sample"] = spec_s
    b_now = _contrast_ids(loaded, arms, "b1_member_ids")
    print(
        f"  b1 Contrast ids moved by the Sample re-mint: {sum(b_pre[c] != b_now[c] for c in b_now)}"
    )
    print("  c  Contrast ids moved by the Sample re-mint: 0 by construction (no Sample input)")

    print("M7 the Intensity-vs-Ratio binding on PXD018299's real sites header")
    roadmap = (ROOT / "ROADMAP.md").read_text().splitlines()
    at = next(
        i
        for i, x in enumerate(roadmap)
        if x.startswith("**`PXD018299` / `HAP1_USP18KO_GlyGlyKSites.txt`")
    )
    line_no, line = next(
        (i, x) for i, x in enumerate(roadmap[at + 1 :], at + 2) if x.startswith(">")
    )
    header = re.findall(r"`([^`]+)`", line)
    column = {h: i for i, h in enumerate(header)}
    print(f"  header read from ROADMAP.md l.{line_no}: {len(header)} columns")
    mapping = loaded["curation_PXD018299.json"][1].sample_mapping()
    label_of = dict(mqs._sample_columns(mapping, column))
    by_key = {s["mapping_key"]: s["id"] for s in mapping.samples}
    num, den = arms[("curation_PXD018299.json", "KO_IFN_vs_WT_IFN")]
    for side, arm, token in (("numerator", num, "KO_IFN"), ("denominator", den, "WT_IFN")):
        bound = [f"Intensity {label_of[by_key[k]]}" for k in arm]
        by_token = [f"Intensity {token}_{i}" for i in (1, 2, 3)]
        print(
            f"  {side}: bound {bound}; present {all(b in column for b in bound)}; "
            f"equals the token's pick {bound == by_token}"
        )
    for h in ("Intensity KO_IFN_1", "Intensity KO_1"):
        print(
            f"  a startswith({h!r}) scan would catch {sum(c.startswith(h) for c in header)} columns"
        )

    print("M8 the interactome's two families (walk/SURVEY-public-IP-tables.md §6)")
    survey = (ROOT / "walk" / "SURVEY-public-IP-tables.md").read_text().splitlines()
    qline = next(x for x in survey if x.startswith("- **quantitative** (24)"))
    iheader = re.findall(r"'([^']+)'", qline)
    icol = {h: i for i, h in enumerate(iheader)}
    lfq = [h for h in iheader if h.startswith("LFQ intensity ")]
    reach = [k for k in lfq if f"Intensity {k[len('LFQ intensity ') :]}" in icol]
    fake = SampleMapping(
        curation_analysis_id="bzk:x",
        samples=[{"id": f"s{i}", "mapping_key": k} for i, k in enumerate(lfq)],
    )
    print(
        f"  LFQ columns {len(lfq)}, Intensity columns "
        f"{sum(h.startswith('Intensity ') for h in iheader)}; Intensity columns reachable from "
        f"an LFQ label {len(reach)}; LFQ keys the protein-groups binding places "
        f"{len(mpg._sample_columns(fake, icol, 'LFQ intensity '))}"
    )

    print("M9 I4's display labels and grain scope in code")
    for term in ("stoichiometry-uncorrected", "abundance-uncorrected"):
        hits = subprocess.run(
            ["git", "grep", "-n", term, "--", "bzk"],
            capture_output=True,
            text=True,
            cwd=ROOT,
            check=False,
        ).stdout.splitlines()
        print(f"  {term!r} in bzk/: {len(hits)} line(s) {hits}")
    src = (ROOT / "bzk" / "ontology" / "invariants.py").read_text()
    body = src[src.index("def _check_I4") : src.index("def _check_I10")]
    print("  _check_I4 reads a grain edge:", "RESULT_FOR" in body)

    print("M10 grain of every applied/native result in the committed fixtures")
    fixture = json.loads((ROOT / "tests" / "fixtures" / "valid_changeset.json").read_text())
    drs = {n["id"]: n for n in fixture["nodes"] if n["__label__"] == "DifferentialResult"}
    for e in fixture["edges"]:
        if e["type"] in ("RESULT_FOR_SITE", "RESULT_FOR_PROTEIN") and e["from"] in drs:
            print(
                f"  valid_changeset {e['from']}: {e['type']} {drs[e['from']]['protein_adjusted']}"
            )


def recompute(rows, columns, num: list[str], den: list[str], diff: str, f=lambda v: v):
    """Max |Difference - (mean(num) - mean(den))| over rows where every value is finite."""
    from bzk.adapters.perseus import _cell_value

    worst, checked = 0.0, 0
    for _, row in rows:
        d = _cell_value(row, columns, diff)
        vals = [_cell_value(row, columns, c) for c in num + den]
        if d is None or any(v is None for v in vals):
            continue
        vals = [f(v) for v in vals]  # type: ignore[arg-type]
        if any(not math.isfinite(v) for v in vals):
            continue
        a, b = vals[: len(num)], vals[len(num) :]
        worst = max(worst, abs(d - (sum(a) / len(a) - sum(b) / len(b))))
        checked += 1
    return worst, checked


def absent_columns(columns: dict[str, int], names: list[str]) -> list[str]:
    """Every name PV reads that the composed header does not carry."""
    return [name for name in names if name not in columns]


def difference_rows(rows, columns, diff: str) -> int:
    """PV5's denominator: rows whose Difference is a finite number."""
    from bzk.adapters.perseus import _cell_value

    return sum(1 for _, row in rows if _cell_value(row, columns, diff) is not None)


def perseus_s1() -> None:
    from bzk.adapters.perseus import DIFFERENCE, PerseusAdapter
    from bzk.sources import pxd055843_perseus as src

    path = src.locate()
    declaration, contrast = src.declared()
    adapter = PerseusAdapter(declaration, [contrast])
    header, rows = adapter._read(path.read_bytes(), path)
    columns = {name: i for i, name in enumerate(header)}
    diff = DIFFERENCE.format(suffix=src.COLUMN_SUFFIX)
    loaded = {p.name: _load(p) for p in RECS}
    num, den = declared_arms(loaded)[("curation_PXD055843.json", "siUSP24_IFN_vs_siC_IFN")]
    sub = [k for k in loaded["curation_PXD055843.json"][0]["mapping"] if "siUSP24 (+ IFN-B)" in k]
    print(f"PV rows {len(rows)}; arms {len(num)}/{len(den)}; substring numerator {len(sub)}")
    # A missing column makes every `_cell_value` None, so `recompute` would skip every row and
    # report `max |dev| 0 over 0 rows` - a pass that never ran. Refused before any PV line prints.
    missing = absent_columns(columns, [diff, *num, *den, *sub])
    if missing:
        raise SystemExit(f"PV refused: {len(missing)} column(s) absent from the header: {missing}")
    print(f"PV0 rows carrying a finite Difference: {difference_rows(rows, columns, diff)}")
    for label, n, d, f in (
        ("PV1 declared order, values as stored", num, den, lambda v: v),
        ("PV2 reversed order, values as stored", den, num, lambda v: v),
        ("PV3 substring numerator, as stored", sub, den, lambda v: v),
        (
            "PV4 declared order, log2 of stored",
            num,
            den,
            lambda v: math.log2(v) if v > 0 else math.nan,
        ),
    ):
        worst, checked = recompute(rows, columns, n, d, diff, f)
        print(f"{label}: max |dev| {worst:.3g} over {checked} rows")


if __name__ == "__main__":
    perseus_s1() if "--s1" in sys.argv else measure()
