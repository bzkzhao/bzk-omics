"""Retrieval of public deposits (`ARCHITECTURE.md` §3).

Separate from `adapters/`, which §3 defines as *one module per search engine* and whose contract is
`ObservationAdapter` — `sniff` / `parse` over a file already in hand. Fetching a deposit is neither:
it produces the file an adapter later reads. Separate from `provenance/` too, which owns the
content-addressed store and stays offline so it can be tested without a network.
"""
