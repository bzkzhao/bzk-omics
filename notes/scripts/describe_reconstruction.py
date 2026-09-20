"""Descriptive, UNREGISTERED breakdown of the PXD026748 reconstruction fixture.

Usage, from the repository root:  .venv/bin/python notes/scripts/describe_reconstruction.py

Reads only tests/fixtures/pxd026748_reconstruction.json. Nothing here can change the registered
readouts or H9s's verdict, which were fixed in walk/PREREG-PXD026748-reconstruction.md before the
run. It answers one question the registered readouts do not: whether "underdetermined" claims fail
in extreme corners of the grid or flip with the seed.
"""

import collections
import json

import numpy as np

f = json.load(open("tests/fixtures/pxd026748_reconstruction.json"))
members = f["family"]["members"]
claims = f["family"]["claims"]
p = np.array([c["min_p"] for c in claims], dtype=float)
supported = p < 0.01
count = supported.sum(axis=1)
total = p.shape[1]
category = np.where(count == total, "durable", np.where(count == 0, "unsupported", "underdetermined"))
print("recomputed categories:", dict(collections.Counter(category.tolist())))

under = count[(count > 0) & (count < total)]
for floor in (342, 324, 288, 180):
    print(f"underdetermined claims supported in >= {floor}/{total} members: {int((under >= floor).sum())}")
print("underdetermined support, min / 25% / median / 75% / max:",
      [int(v) for v in np.percentile(under, [0, 25, 50, 75, 100])])

width = np.array([m["width_sd"] for m in members])
downshift = np.array([m["downshift_sd"] for m in members])
scope = np.array([m["scope"] for m in members])
cells = sorted(set(zip(width.tolist(), downshift.tolist(), scope.tolist())))
share = np.array([[supported[i][(width == w) & (downshift == d) & (scope == s)].mean()
                   for (w, d, s) in cells] for i in range(len(claims))])
under_idx = np.where(category == "underdetermined")[0]
seed_mixed = ((share[under_idx] > 0) & (share[under_idx] < 1)).sum(axis=1)
print("underdetermined claims with at least one cell where the seed decides:", int((seed_mixed > 0).sum()),
      "| failing only by whole cells:", int((seed_mixed == 0).sum()))

default = share[:, cells.index((0.3, 1.8, "per_sample"))]
print("default cell (0.3, 1.8, per_sample): supported in all 20 seeds:", int((default == 1).sum()),
      "| in some seeds only:", int(((default > 0) & (default < 1)).sum()),
      "| in none:", int((default == 0).sum()))

for name, axis in (("width_sd", width), ("downshift_sd", downshift), ("scope", scope)):
    print(f"support share by {name}, all claims:",
          {str(level): round(float(supported[:, axis == level].mean()), 4) for level in sorted(set(axis.tolist()))})
