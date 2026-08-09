"""Change-sets for analyses the platform itself ran, over observations already in the graph.

**Why this is a fourth layer and not one of the three (`ARCHITECTURE.md` §3).** `sources/` retrieves
deposits, `adapters/` maps an external tool's output to `Observation` nodes, `stats/` computes
arithmetic and knows nothing about the graph, and `ontology/store.py` is the only module that
writes. What lives here is none of them: it takes values a computation produced and observations
that already exist, and emits the derived evidence — an `Analysis`, its `Imputation`, a `Contrast`
and the `DifferentialResult`s. There is no external file to parse and no observation to mint.

Putting it in `adapters/` would make *adapter* mean "anything that builds a change-set", which is
the one thing that layer's contract does not say — `ObservationAdapter` is defined by `sniff` and
`parse(file, mapping)`, and neither has an argument here. Putting it in `stats/` would make the
arithmetic layer depend on the schema, and its independence is precisely what makes I11's retained
matrix worth having: a test that cannot mint a node can be swapped without touching the graph.
Putting it in the dataset script that already computes the numbers would make one deposit's runner
the home of a contract every future computed analysis needs.

What this package must never do: arithmetic, I/O, or writing. It is a pure function from declared
parameters plus per-row statistics to `(nodes, edges)`, and `store.write_change_set` remains the
only thing that touches the store.
"""

from bzk.analysis.differential import DeclaredRun, SiteResult, site_change_set

__all__ = ["DeclaredRun", "SiteResult", "site_change_set"]
