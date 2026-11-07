"""EXPLORATORY, UNREGISTERED. PXD032267 gate variants with the input check suspended.

Readouts A-D are NOT computed, so a later registered attempt can still test them fresh.
Writes nothing. Run from the repository root:  .venv/bin/python <this file>
"""
import math

import numpy as np

from bzk.sources import pxd032267_gate as g
from bzk.sources.pride import PXD032267_PARAMETERS, PXD032267_SITES
from bzk.provenance.raw_store import verify

sites = verify(PXD032267_SITES.expected_content_hash, filename=PXD032267_SITES.filename, home=g.HOME)
params = verify(PXD032267_PARAMETERS.expected_content_hash, filename=PXD032267_PARAMETERS.filename, home=g.HOME)
published = g.load_published()
facts = g.load_deposit_facts()
table, _ = g.pinning_check(sites, params, facts=facts)
rows = g.population(table)
matrix = g.values_matrix(table, rows)
claim_rows, _ = g.join(table, rows, published.claims, expected_ids=facts.joined_ids)

g.INPUT_TOLERANCE = math.inf  # the one departure from the registration, and the reason this is exploratory
gate = g.gate_g(matrix, claim_rows, published.claims)
print("EXPLORATORY — input check suspended; readouts not run")
print("status:", gate["status"], "| primary:", gate["primary"], "| passing:", gate["passing"])
for v, rec in gate["variants"].items():
    print(f"  {v}: p={['%.6f' % x for x in rec['p']]}  max|dp|={rec['max_abs_delta_p']:.2e}  passes={rec['passes']}")
print("  published p:", [c.p_value for i, c in enumerate(published.claims) if c.label in gate["gate_rows"]])
print("  close pairs:", gate["close_pairs"], "| pairwise gaps:", gate["pairwise_max_gap"])

# Post-hoc idea, tested once: were the authors' log2 values rounded to 4 decimals before the difference?
print("rounding test (log2 rounded to k decimals, then mean difference, |delta| to published):")
complete = [i for i, r in enumerate(claim_rows) if not np.isnan(matrix[r]).any()]
for k in (3, 4, 5):
    deltas = []
    for i in complete:
        x = np.round(matrix[claim_rows[i]], k)
        d = x[9:12].mean() - x[6:9].mean()  # WtTAC - WtC, in g.SAMPLES order
        deltas.append(abs(d - published.claims[i].difference))
    print(f"  k={k}: " + ", ".join(f"{d:.1e}" for d in deltas))
