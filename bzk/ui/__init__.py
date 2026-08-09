"""The v0.1 interface. `streamlit run bzk/ui/app.py`.

A package rather than a bare module for the reason `quant/` and `query/` are: `ruff` and `mypy`
walk `bzk`, and a directory without an `__init__.py` is a namespace package that some tools treat
differently from the rest of the tree. Nothing is re-exported here — `app.py` is run, not imported,
and `absence.py` is imported by its own name so the one decision this package makes has a findable
home.
"""
