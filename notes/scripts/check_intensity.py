"""Does proteinGroups.txt's `Intensity` include GlyGly-modified peptides?

Usage:  python3 check_intensity.py ~/Downloads/20210616_Shotgun_PRIDE

Read-only. Tests three hypotheses for each protein group and each run, against
the peptide-level intensities in modificationSpecificPeptides.txt:

  H1  Intensity = sum over the group's razor peptides, ALL modified forms
  H2  Intensity = the same sum, EXCLUDING every GlyGly-carrying form
  H3  H2, and also excluding the unmodified counterpart of any peptide that
      appears GlyGly-modified ("Discard unmodified counterpart peptides")

A CONTROL set (groups with no GlyGly form anywhere) is checked first. There all
three hypotheses give the same number, so if the control does not match, the
join is wrong and the H1/H2/H3 result means nothing.
"""

import sys
from pathlib import Path

TOL = 0.005  # relative


def read(path: Path) -> tuple[list[str], list[list[str]]]:
    lines = path.read_bytes().decode("utf-8", "replace").splitlines()
    return lines[0].split("\t"), [line.split("\t") for line in lines[1:] if line]


def need(header: list[str], names: list[str], where: str) -> dict[str, int]:
    missing = [n for n in names if n not in header]
    if missing:
        sys.exit(f"STOP: {where} lacks {missing}. Columns containing 'ID' or 'razor': "
                 f"{[c for c in header if 'ID' in c or 'razor' in c.lower()]}")
    return {n: header.index(n) for n in names}


def num(text: str) -> float:
    try:
        value = float(text)
    except ValueError:
        return 0.0
    return 0.0 if value != value else value  # NaN -> 0


d = Path(sys.argv[1]).expanduser()
pg_h, pg = read(d / "proteinGroups.txt")
msp_h, msp = read(d / "modificationSpecificPeptides.txt")

runs = [c[len("Intensity "):] for c in pg_h if c.startswith("Intensity ")]
print("runs:", len(runs))
pgi = need(pg_h, ["id", "Peptide IDs", "Peptide is razor", "Reverse", "Potential contaminant"]
           + [f"Intensity {r}" for r in runs], "proteinGroups.txt")
mi = need(msp_h, ["Peptide ID", "Modifications"] + [f"Intensity {r}" for r in runs],
          "modificationSpecificPeptides.txt")

# peptide id -> list of (is_glygly, is_unmodified, [intensity per run])
forms: dict[str, list[tuple[bool, bool, list[float]]]] = {}
for row in msp:
    if len(row) < len(msp_h):
        continue
    mods = row[mi["Modifications"]]
    forms.setdefault(row[mi["Peptide ID"]], []).append(
        ("GlyGly" in mods, mods == "Unmodified",
         [num(row[mi[f"Intensity {r}"]]) for r in runs])
    )
print("mod-specific peptide rows:", sum(len(v) for v in forms.values()),
      "| GlyGly forms:", sum(f[0] for v in forms.values() for f in v))

control = {"n": 0, "match": 0}
tested = {"n": 0, "H1": 0, "H2": 0, "H3": 0, "none": 0}
examples = []
for row in pg:
    if len(row) < len(pg_h) or not row[pgi["id"]].isdigit():
        continue
    if row[pgi["Reverse"]] == "+" or row[pgi["Potential contaminant"]] == "+":
        continue
    ids = row[pgi["Peptide IDs"]].split(";")
    razor = row[pgi["Peptide is razor"]].split(";")
    if len(ids) != len(razor):
        continue
    mine = [p for p, r in zip(ids, razor) if r == "True"]
    group_forms = [f for p in mine for f in forms.get(p, [])]
    gg_peptides = {p for p in mine if any(f[0] for f in forms.get(p, []))}
    for k, r in enumerate(runs):
        a = num(row[pgi[f"Intensity {r}"]])
        if a <= 0:
            continue
        h1 = sum(f[2][k] for f in group_forms)
        h2 = sum(f[2][k] for f in group_forms if not f[0])
        h3 = sum(f[2][k] for p in mine for f in forms.get(p, [])
                 if not f[0] and not (f[1] and p in gg_peptides))
        ok = {h: v > 0 and abs(a - v) / a <= TOL for h, v in (("H1", h1), ("H2", h2), ("H3", h3))}
        if not gg_peptides:
            control["n"] += 1
            control["match"] += ok["H1"]
            continue
        if h1 == h2:  # GlyGly forms present but zero in this run: not discriminating
            continue
        tested["n"] += 1
        for h in ("H1", "H2", "H3"):
            tested[h] += ok[h]
        tested["none"] += not any(ok.values())
        if len(examples) < 5:
            examples.append((row[pgi["id"]], r[:12], a, h1, h2, h3))

print("\n== CONTROL (no GlyGly form in the group) ==")
print(f"group-runs: {control['n']} | Intensity == razor-peptide sum (±{TOL:.1%}): "
      f"{control['match']}")
print("\n== TEST (GlyGly form with non-zero intensity in that run) ==")
print(f"group-runs: {tested['n']}")
for h in ("H1", "H2", "H3", "none"):
    print(f"  matches {h}: {tested[h]}")
print("\nexamples: group, run, proteinGroups Intensity, H1, H2, H3")
for e in examples:
    print(f"  {e[0]:>6} {e[1]:<12} {e[2]:>14.0f} {e[3]:>14.0f} {e[4]:>14.0f} {e[5]:>14.0f}")
