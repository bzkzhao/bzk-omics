"""Read-only inspection of PXD026748's shotgun zip, for piece 2's curation record.

Usage:  .venv/bin/python inspect_shotgun.py /path/to/20210616_Shotgun_PRIDE.zip

Writes nothing to the repository or the raw store. One temporary copy of
proteinGroups.txt is written to a temp directory so the real adapters can sniff
it, and that copy is deleted on exit.
"""

import hashlib
import sys
import tempfile
import zipfile
from pathlib import Path

FAMILIES = ("Intensity ", "LFQ intensity ", "iBAQ ")


def section(title: str) -> None:
    print(f"\n== {title} ==")


zpath = Path(sys.argv[1]).expanduser()
section("zip")
print(zpath, zpath.stat().st_size, "bytes")
digest = hashlib.sha256()
with zpath.open("rb") as handle:
    for block in iter(lambda: handle.read(1 << 20), b""):
        digest.update(block)
print("sha256(zip)", digest.hexdigest())

with zipfile.ZipFile(zpath) as z:
    section("members")
    for info in z.infolist():
        print(f"{info.file_size:>12}  {info.filename}")

    pg_names = [n for n in z.namelist() if n.rsplit("/", 1)[-1] == "proteinGroups.txt"]
    print("\nproteinGroups.txt members:", pg_names)
    if len(pg_names) != 1:
        sys.exit("STOP: expected exactly one proteinGroups.txt")
    raw = z.read(pg_names[0])

    def show_member(basename: str, keep=lambda line: True, limit: int = 40) -> None:
        names = [n for n in z.namelist() if n.rsplit("/", 1)[-1] == basename]
        section(basename)
        if not names:
            print("absent")
            return
        lines = z.read(names[0]).decode("utf-8", "replace").splitlines()
        kept = [line for line in lines if keep(line)]
        for line in kept[:limit]:
            print(line[:200])
        if len(kept) > limit:
            print(f"... {len(kept) - limit} more")

    show_member(
        "parameters.txt",
        keep=lambda line: line.split("\t")[0].strip().lower()
        in {"version", "fasta file", "label-free quantification", "lfq min. ratio count",
            "match between runs", "ibaq", "decoy mode", "include contaminants"},
    )
    show_member("experimentalDesignTemplate.txt")
    show_member("summary.txt", keep=lambda line: not line.startswith("Total"), limit=20)

section("proteinGroups.txt")
print("bytes", len(raw))
print("sha256", "sha256:" + hashlib.sha256(raw).hexdigest())
lines = raw.decode("utf-8", "replace").splitlines()
header = lines[0].split("\t")
print("columns", len(header))
print("has 'Protein IDs':", "Protein IDs" in header, "| has 'id':", "id" in header)
print("lines starting '#!{':", sum(line.startswith("#!{") for line in lines[1:]))
print("CRLF line endings:", b"\r\n" in raw[:10000])

idx = header.index("id") if "id" in header else None
rows = [line.split("\t") for line in lines[1:]]
data = [r for r in rows if idx is not None and len(r) > idx and r[idx].isdigit()]
print("data rows (id is digits):", len(data), "| other lines:", len(rows) - len(data))
for flag in ("Reverse", "Potential contaminant", "Only identified by site"):
    if flag in header:
        i = header.index(flag)
        print(f"{flag} '+':", sum(1 for r in data if len(r) > i and r[i] == "+"))
    else:
        print(f"{flag}: column absent")

section("quantity families (exact headers)")
for prefix in FAMILIES:
    cols = [c for c in header if c.startswith(prefix)]
    print(f"{prefix.strip()!r}: {len(cols)}")
    for c in cols:
        print("   ", repr(c))

section("sniff on the real bytes")
sys.path.insert(0, str(Path.cwd()))
from bzk.adapters.maxquant_protein_groups import (  # noqa: E402
    DeclaredProteinAnalysis,
    MaxQuantProteinGroupsAdapter,
)
from bzk.adapters.maxquant_sites import DeclaredSiteAnalysis, MaxQuantSiteAdapter  # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    copy = Path(tmp) / "proteinGroups.txt"
    copy.write_bytes(raw)
    site = MaxQuantSiteAdapter(DeclaredSiteAnalysis(search_engine="maxquant", external_version="x"))
    prot = MaxQuantProteinGroupsAdapter(
        DeclaredProteinAnalysis(search_engine="maxquant", external_version="x")
    )
    print("site sniff:", site.sniff(copy))
    print("protein-groups sniff:", prot.sniff(copy))
print("\ndone; nothing written outside a deleted temp directory")
