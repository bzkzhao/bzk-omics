"""Recompute H10 attempt 3's readout A at the default cell, from the committed fixture alone.

Usage, from the repository root:  .venv/bin/python notes/scripts/recompute_readout_a.py

Why this exists: `bzk/sources/pxd018299_h10.py` (l.1343 at `a5aeb00`) passes the whole family's
support — all 360 members — to `_readout_a`, and labels the result `default_cell`. The default cell
is 20 members (width 0.3, downshift 1.8, per_sample, seeds 0-19). Readouts B, D and D' already use
the default slice, and attempt 2's secondary readout A (l.1413) was computed over the default
members, so only readout A is affected. This script recomputes it both ways from
`readouts.*.per_claim_support` so the correction is reproducible without re-running anything.
"""

import json

import numpy as np

with open("tests/fixtures/pxd018299_h10_attempt3.json") as handle:
    fixture = json.load(handle)
for role in ("primary", "secondary"):
    block = fixture["readouts"][role]
    pcs = block["per_claim_support"]
    members = pcs["members"]
    support = np.array([[float(x) for x in row["support"]] for row in pcs["rows"]])
    default = [
        i
        for i, m in enumerate(members)
        if (m["width_sd"], m["downshift_sd"], m["scope"]) == (0.3, 1.8, "per_sample")
    ]
    at_default = int((np.median(support[:, default], axis=1) >= 0.5).sum())
    over_family = int((np.median(support, axis=1) >= 0.5).sum())
    print(
        f"{role} ({block['variant']}): default cell ({len(default)} members) {at_default} of {len(support)};"
        f" as the fixture computed it ({support.shape[1]} members) {over_family};"
        f" fixture's stored value {block['readout_a']['default_cell']['supported']}"
    )
