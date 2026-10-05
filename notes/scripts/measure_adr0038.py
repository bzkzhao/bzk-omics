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
from collections import Counter
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


def measure_store() -> None:
    """M11: what `quant_store.write_cells` does with one key twice in a batch, and across batches."""
    import tempfile

    from bzk.quant import store as quant_store
    from bzk.quant.store import Cell

    print("M11 retained-matrix writes under a repeated key")
    connection = quant_store.connect(Path(tempfile.mkdtemp()))
    q = "intensity_multiplicity_summed"
    first = Cell(observation_id="bzk:o1", sample_id="bzk:s1", quantity=q, value=1.0)
    second = Cell(observation_id="bzk:o1", sample_id="bzk:s1", quantity=q, value=2.0)
    try:
        staged = quant_store.write_cells(
            connection, "SiteObservation", [first, second]
        ).cells_staged
        kept = len(quant_store.read_cells(connection, "SiteObservation", "bzk:o1"))
        print(f"  one batch, key repeated: accepted; cells_staged {staged}, cells retained {kept}")
    except Exception as exc:  # noqa: BLE001 - the measurement is which branch runs
        print(f"  one batch, key repeated: refused ({type(exc).__name__})")
    fixture = json.loads((ROOT / "tests" / "fixtures" / "pxd026748_digly_ingest.json").read_text())
    print(
        f"  PXD026748 sites_emitted (tests/fixtures/pxd026748_digly_ingest.json): "
        f"{fixture['report']['sites_emitted']}"
    )
    connection.close()


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


#: PXD055843 Supplementary Data S3 - digest and name as walk/SURVEY-public-IP-tables.md section 7
#: records them. No curation record covers S3 (it waits on the PI and ADR-0032), so its arms are
#: declared here, by exact composed header, as the pre-registration's curator statement.
S3_DIGEST = "sha256:2ea450f3a63721fa6e59898392e8d07d2e002abbb5cf16004340fe838d3f52e9"
S3_FILE = "Supplementary_Data_S3_ISG15_IP.xlsx"
S3_SUFFIX = "siUSP24 (+IFN)_sic (+IFN)"
_S3_DIR = (
    "E:\\MS_Projects\\Rishov_USP24_SCP00004\\ISG15_IPs_Thermo_Ab\\"
    "SCP0013_MSQ2590_20230403_RishovMukhopadhyay_"
)
S3_IP_NUM = [
    f"Set 1 | siUSP24 (+IFN) | {_S3_DIR}ISG08_S1-H1_1_939.d",
    f"Set 2 | siUSP24 (+IFN) | {_S3_DIR}ISG12_S1-D2_1_944.d",
    f"Set 3 | siUSP24 (+IFN) | {_S3_DIR}ISG16_S1-H2_1_949.d",
]
S3_IP_DEN = [
    f"Set 1 | sic (+IFN) | {_S3_DIR}ISG07_S1-G1_1_938.d",
    f"Set 2 | sic (+IFN) | {_S3_DIR}ISG11_S1-C2_1_943.d",
    f"Set 3 | sic (+IFN) | {_S3_DIR}ISG15_S1-G2_1_948.d",
]
S3_BEADS_NUM = f"only beads _ no Ab | siUSP24 (+IFN) | {_S3_DIR}ISG04_S1-D1_1_934.d"
S3_BEADS_DEN = f"only beads _ no Ab | sic (+IFN) | {_S3_DIR}ISG03_S1-C1_1_933.d"


def untested(row, columns, diff: str, minus_log_p: str, statistic: str | None) -> bool:
    """D6-revised's placeholder rule, from the statistics columns alone: Difference 0, -log p 0
    (p = 1), and test statistic 0 where the file carries one. Reads no arm column."""
    from bzk.adapters.perseus import _cell_value

    d = _cell_value(row, columns, diff)
    lp = _cell_value(row, columns, minus_log_p)
    t = _cell_value(row, columns, statistic) if statistic else 0.0
    return d == 0 and lp == 0 and t == 0


def perseus_s3() -> None:
    from bzk.adapters.perseus import DIFFERENCE, MINUS_LOG_P, Q_VALUE, PerseusAdapter, _cell_value
    from bzk.provenance.raw_store import verify
    from bzk.sources import pxd055843_perseus as src

    path = verify(S3_DIGEST, filename=S3_FILE, home=Path.home() / ".bzk-omics")
    declaration, contrast = src.declared()  # only to construct an adapter; _read uses neither
    header, rows = PerseusAdapter(declaration, [contrast])._read(path.read_bytes(), path)
    columns = {name: i for i, name in enumerate(header)}
    diff = DIFFERENCE.format(suffix=S3_SUFFIX)
    minus_log_p = MINUS_LOG_P.format(suffix=S3_SUFFIX)
    q_value = Q_VALUE.format(suffix=S3_SUFFIX)
    statistic = f"Student's T-test Test statistic {S3_SUFFIX}"
    needed = [
        diff,
        minus_log_p,
        q_value,
        statistic,
        *S3_IP_NUM,
        *S3_IP_DEN,
        S3_BEADS_NUM,
        S3_BEADS_DEN,
    ]
    missing = absent_columns(columns, needed)
    if missing:
        raise SystemExit(f"T refused: {len(missing)} column(s) absent from the header: {missing}")
    flagged = [r for r in rows if untested(r[1], columns, diff, minus_log_p, statistic)]
    tested = [r for r in rows if not untested(r[1], columns, diff, minus_log_p, statistic)]
    q_of_flagged = sorted({_cell_value(r[1], columns, q_value) for r in flagged}, key=str)
    print(
        f"T0 rows {len(rows)}; untested by rule {len(flagged)}; tested {len(tested)}; "
        f"q among untested {q_of_flagged}"
    )
    print(f"T0 rows carrying a finite Difference: {difference_rows(rows, columns, diff)}")
    for label, n, d in (
        ("T1 IP 3 v 3, declared order", S3_IP_NUM, S3_IP_DEN),
        ("T2 IP + beads 4 v 4", [*S3_IP_NUM, S3_BEADS_NUM], [*S3_IP_DEN, S3_BEADS_DEN]),
        ("T3 IP 3 v 3, reversed", S3_IP_DEN, S3_IP_NUM),
    ):
        worst, checked = recompute(tested, columns, n, d, diff)
        devs = sorted(
            abs(
                _cell_value(r, columns, diff)
                - (
                    sum(_cell_value(r, columns, c) for c in n) / len(n)
                    - sum(_cell_value(r, columns, c) for c in d) / len(d)
                )
            )
            for _, r in tested
        )
        within = sum(v <= 1e-3 for v in devs)
        median = devs[len(devs) // 2] if devs else float("nan")
        print(
            f"{label}: max |dev| {worst:.3g} over {checked} tested rows; "
            f"within 1e-3 {within}; median {median:.3g}"
        )
    on_flagged = recompute(flagged, columns, S3_IP_NUM, S3_IP_DEN, diff)
    print(f"T4 untested rows, IP 3 v 3: max |dev| {on_flagged[0]:.3g} over {on_flagged[1]} rows")


def perseus_s1_origin() -> None:
    """ORIGIN: where S1's untested rows come from. Prints counts only, per row class."""
    from bzk.adapters.perseus import DIFFERENCE, MINUS_LOG_P, PerseusAdapter, _cell_value
    from bzk.sources import pxd055843_perseus as src

    path = src.locate()
    declaration, contrast = src.declared()
    header, rows = PerseusAdapter(declaration, [contrast])._read(path.read_bytes(), path)
    columns = {name: i for i, name in enumerate(header)}
    diff = DIFFERENCE.format(suffix=src.COLUMN_SUFFIX)
    minus_log_p = MINUS_LOG_P.format(suffix=src.COLUMN_SUFFIX)
    statistic = f"Student's T-test Test statistic {src.COLUMN_SUFFIX}"
    record = json.loads((CURATION / "curation_PXD055843.json").read_text())
    groups: dict[str, list[str]] = {}
    for key, sample in record["mapping"].items():
        groups.setdefault(f"{sample['genotype']} / {sample['treatment']}", []).append(key)
    num, den = declared_arms({p.name: _load(p) for p in RECS})[
        ("curation_PXD055843.json", "siUSP24_IFN_vs_siC_IFN")
    ]
    tested_cols = num + den
    missing = absent_columns(columns, [diff, minus_log_p, statistic, *record["mapping"]])
    if missing:
        raise SystemExit(f"ORIGIN refused: {len(missing)} column(s) absent: {missing}")
    # A column's lowest 10%: where a downshifted-normal draw lands. A proxy, not a mask.
    floor = {}
    for c in record["mapping"]:
        values = sorted(v for _, r in rows if (v := _cell_value(r, columns, c)) is not None)
        floor[c] = values[int(0.10 * len(values))]

    def profile(row: list[str]) -> tuple[int, int]:
        low = sum(_cell_value(row, columns, c) <= floor[c] for c in tested_cols)
        other_high = sum(
            all(_cell_value(row, columns, c) > floor[c] for c in keys)
            for keys in groups.values()
            if not set(keys) & set(tested_cols)
        )
        return low, other_high

    for label, flag in (("untested", True), ("tested", False)):
        selected = [
            r for _, r in rows if untested(r, columns, diff, minus_log_p, statistic) is flag
        ]
        profiles = [profile(r) for r in selected]
        lows = sorted(p[0] for p in profiles)
        print(
            f"ORIGIN {label}: rows {len(selected)}; tested-arm values in their column's lowest 10% "
            f"(of 6): median {lows[len(lows) // 2]}, distribution {dict(sorted(Counter(lows).items()))}; "
            f"rows with >=1 other group wholly above it: {sum(p[1] >= 1 for p in profiles)}"
        )


if __name__ == "__main__":
    if "--s1" in sys.argv:
        perseus_s1()
    elif "--s3" in sys.argv:
        perseus_s3()
    elif "--s1-origin" in sys.argv:
        perseus_s1_origin()
    else:
        measure()
        measure_store()
