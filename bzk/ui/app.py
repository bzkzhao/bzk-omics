"""The minimal v0.1 interface: three panels over `bzk/query/` (`ARCHITECTURE.md` §3).

    streamlit run bzk/ui/app.py

**It imports `bzk.query` and nothing else from `bzk/`.** No `kuzu`, no Cypher, no schema. That is
the constraint that makes *"the UI derives nothing"* checkable rather than a habit: a panel needing
a value the read layer does not return is a **read-layer gap to report**, and the import rule is
what stops it being closed with a second query in the renderer.

**Three rules it inherits and one it adds.**

1. **No value is derived here.** Everything on screen is a field of a record `bzk/query/` returned.
   Where a field is `None` because the read layer could not determine it — `substantially_imputed`,
   whose denominator lives in `quant.duckdb` — the screen says *unknown* **with the reason**, never
   a blank cell. `graph.py` argues a `False` would assert I15's clause satisfied; a blank says the
   same thing more quietly and lets the reader supply the missing word.
2. **`ONTOLOGY.md` §8 I14's display half attaches here for the first time.** Where a number has a
   candidate set behind it, the set appears beside it.
3. **Four absences render as four things** (`bzk/ui/absence.py`). This is the panel-three point and
   the reason the empty panels stay visible rather than being hidden until they have rows.
4. **It does not resolve the `DDX58`/`RIGI` rename.** Both are shown; neither is joined to the
   other. `graph.py` returns encoded ids *so that a caller can compare*, and making the comparison
   for the reader is the platform asserting a synonymy the graph does not hold. Reported as a
   read-layer gap in `HANDOFF.md` §8 rather than closed here.

**Two operational facts, established rather than assumed (2026-08-09).** Kùzu takes a single writer
lock, so this **cannot read the graph while `bzk rebuild` holds it**; `query.connect` raises and
the app renders that state instead of a traceback. And a screen is a *view within the local
instance*, which §8 I18 declares unrestricted, so nothing here fires `HANDOFF.md` §8's EX trigger —
**there is no download button**, and adding one would fire it.

**The second of those carries a condition, and this docstring asserted it without one until
2026-08-09.** *Local instance* is not a property of the code: `streamlit run` binds `0.0.0.0` by
default and announces an External URL. The condition is met by `.streamlit/config.toml` at the
repository root, which sets `server.address = "localhost"` — read from the working directory, so it
governs the documented command and not an absolute-path invocation from elsewhere
(`OPERATIONS.md` §4.1). Cited rather than restated: `CLAUDE.md`'s normativity rule names
`ONTOLOGY.md` and does not reach a reading that lives in `HANDOFF.md` §3, so what settles this pair
is the single-source rule instead — the condition has one home and this is not it.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import streamlit as st

from bzk import query
from bzk.ui.absence import describe

#: The 14 published ISGylation substrates, as `bzk/sources/pxd018299_baseline.py` records them.
#: Duplicated as a default here rather than imported: importing it would make this module depend on
#: a `sources/` script, and the panel takes any symbol list — this is a starting value, not a fact.
DEFAULT_SYMBOLS = (
    "ADAR, EIF2AK2, DDX58, DDX60, DHX58, OAS1, OAS2, "
    "IFIH1, STAT1, PSMB9, PSMB10, PSMA7, PSME2, TAP1"
)

#: Which graph to read. Defaults to the one every other command uses; overridable because a
#: `streamlit run` takes no arguments of its own and the tests must point the app at a fixture.
#: An environment variable rather than a flag for that reason, and it is read once, here.
GRAPH_ENV = "BZK_GRAPH"


def _absence_notice(absence: Any) -> None:
    """Render one absence as its own claim. The whole of panel three's contract."""
    rendering = describe(absence)
    if rendering is None:
        return
    st.warning(f"**{rendering.headline}**\n\n{rendering.detail}")


def _unknown(reason: str) -> str:
    """A field whose truth value the read layer could not determine.

    Never `False`, never blank: `graph.py` records that a `False` for `substantially_imputed` would
    assert I15's clause satisfied, and a blank cell makes the same assertion without saying so.
    """
    return f"unknown — {reason}"


def site_panel(conn: Any, site_ids: Sequence[str]) -> None:
    st.header("1 · Site provenance")
    st.caption(
        "What one `ModificationSite` was keyed against, and on what basis (I2, I17, ADR-0024)."
    )
    if not site_ids:
        st.warning("**No sites are stored.** Nothing to key.")
        return
    site_id = st.selectbox("ModificationSite", site_ids, index=0)
    keying = query.site_keying(conn, str(site_id))
    if keying is None:
        st.warning("**No such site.** The id is not in the graph.")
        return

    left, right = st.columns(2)
    with left:
        st.subheader("Keyed against")
        st.markdown(
            f"- `ProteinSequence` **{keying.sequence_id}** (sv{keying.sequence_version})\n"
            f"- `Protein` **{keying.protein_id}** — accession `{keying.accession}`\n"
            f"- residue **{keying.residue}{keying.position}**, "
            f"modification `{keying.modification_type}`"
        )
        st.subheader("Provenance (I5)")
        st.markdown(
            f"- **{'provenanced' if keying.provenance.provenanced else 'UNPROVENANCED'}**\n"
            f"- reached by `{keying.provenance.path or '(no declared path)'}`\n"
            f"- `Analysis`: {', '.join(keying.provenance.analysis_ids) or '—'}"
        )
    with right:
        st.subheader("On what basis")
        promoted = "reviewed_preferred" in keying.keying_basis
        st.markdown(
            f"- `keying_basis`: **{', '.join(keying.keying_basis) or '—'}**\n"
            f"- `displaced_protein`: "
            + (
                f"**{', '.join(keying.displaced_protein)}**"
                if keying.displaced_protein
                else "none — this site was not promoted"
            )
            + (
                "\n- I17 promoted this site over the search engine's razor pick, and names what "
                "it displaced."
                if promoted
                else "\n- The search engine's razor pick was kept."
            )
        )
        st.subheader(f"Candidate set — {len(keying.candidate_proteins)} protein(s)")
        # I14's display half: the set the observation named, never narrowed here.
        st.markdown("\n".join(f"- `{p}`" for p in keying.candidate_proteins) or "—")
        st.caption(
            "The observation named every one of these. I14: a result is never rendered against "
            "one of them without a `confirmed` assignment."
        )
        st.markdown(
            f"- modifier basis: `{', '.join(keying.modifier_basis) or '—'}`, "
            f"confidence: `{', '.join(keying.modifier_confidence) or '—'}`"
        )


def gene_panel(conn: Any) -> None:
    st.header("2 · Gene symbols")
    st.caption(
        "Which symbols are present in stored content. **Identifiability, not recovery** — a count "
        "here says how many symbols are answerable from stored `Gene.symbol`, and nothing about "
        "how many published targets an analysis recovered."
    )
    raw = st.text_area("Symbols (comma-separated)", value=DEFAULT_SYMBOLS, height=68)
    symbols = [s.strip() for s in raw.split(",") if s.strip()]
    if not symbols:
        st.info("No symbols requested.")
        return
    answers = query.gene_symbols(conn, symbols)
    present = [a for a in answers if a.present]
    absent = [a for a in answers if not a.present]
    st.markdown(
        f"**{len(present)} of {len(answers)} requested symbols are present** "
        f"as a `Gene` node with that symbol."
    )
    st.dataframe(
        [
            {
                "symbol": a.symbol,
                "present": a.present,
                "Gene.id": a.gene_id or "—",
                "proteins encoded": len(a.protein_ids),
                "absence": a.absence.value if a.absence else "—",
            }
            for a in answers
        ],
        hide_index=True,
    )
    for a in absent:
        st.markdown(f"**{a.symbol}**")
        _absence_notice(a.absence)
        st.caption(a.detail)
    st.caption(
        "This panel does not join a renamed symbol to its current one. Where an absent symbol and "
        "a present one are the same locus, both appear and neither is linked to the other — the "
        "read layer returns encoded ids so a caller can compare, and making the comparison here "
        "would assert a synonymy the graph does not hold."
    )


def absences_panel(conn: Any, analysis_ids: Sequence[str]) -> None:
    st.header("3 · Differential results, refusals, imputation")
    st.caption(
        "Three questions the graph currently answers with nothing — and it is three different "
        "nothings. This panel stays visible when empty; that is the point of it."
    )

    st.subheader("Differential table")
    if not analysis_ids:
        st.warning("**No `Analysis` is stored.** Nothing to tabulate.")
    else:
        analysis_id = st.selectbox("Analysis", analysis_ids, index=0)
        rows, absence = query.differential_table(conn, str(analysis_id))
        _absence_notice(absence)
        if rows:
            st.dataframe(
                [
                    {
                        "result": r.result_id,
                        "site": r.site_id or "—",
                        "genes": ", ".join(r.gene_symbols) or "—",
                        "quantity": r.quantity or "—",
                        "test": r.test or "—",
                        "log2FC": r.log2fc,
                        "adj p": r.adj_p_value,
                        "protein_adjusted": r.protein_adjusted or "—",
                        # Never False and never blank — see `_unknown`.
                        "substantially imputed": (
                            _unknown(
                                "denominator is in quant.duckdb, which the read layer does "
                                "not reach"
                            )
                            if r.substantially_imputed is None
                            else r.substantially_imputed
                        ),
                        "n_imputed": r.n_imputed,
                        # I14's display half, on every row that carries a number.
                        "candidate proteins": ", ".join(r.candidate_proteins) or "—",
                        "assignment confidence": r.assignment_confidence or "—",
                        "provenance": (
                            "provenanced" if r.provenance.provenanced else "UNPROVENANCED"
                        ),
                    }
                    for r in rows
                ],
                hide_index=True,
            )

    st.subheader("Refusals")
    answer = query.refusals(conn)
    _absence_notice(answer.absence)
    st.caption(answer.detail)
    if answer.reasons:
        st.dataframe([{"reason": k, "rows": n} for k, n in answer.reasons], hide_index=True)

    st.subheader("Imputation state")
    if not analysis_ids:
        st.warning("**No `Analysis` is stored.** Nothing to report an imputation state for.")
    else:
        for analysis_id in analysis_ids:
            state = query.imputation_state(conn, str(analysis_id))
            st.markdown(f"`{analysis_id}` — I15 satisfied: **{state.satisfies_i15}**")
            _absence_notice(state.absence)
            if state.methods:
                st.dataframe(
                    [
                        {"method": m, "seed": s if s is not None else "—"}
                        for m, s in zip(state.methods, state.seeds, strict=True)
                    ],
                    hide_index=True,
                )
    st.caption(
        "An imputation state is a **set**: `IMPUTATION_FOR` is `MANY_ONE`, so several may attach "
        "to one `Analysis`."
    )


def graph_path() -> Path:
    """The graph this run reads. `$BZK_GRAPH` if set, else the standard location."""
    override = os.environ.get(GRAPH_ENV)
    return Path(override) if override else query.DEFAULT_GRAPH


def main(graph: Path | None = None) -> None:
    st.set_page_config(page_title="bzk Omics", layout="wide")
    st.title("bzk Omics — v0.1")
    st.caption(
        "Read-only over the evidence graph. Nothing on this screen is computed here: every value "
        "is returned by `bzk/query/`."
    )
    graph = graph_path() if graph is None else graph
    try:
        conn = query.connect(graph)
    except RuntimeError as exc:
        # Kùzu takes a single writer lock, so a running `bzk rebuild` holds the database. Rendered
        # rather than raised, and *not* retried: a silent retry would hang for the length of a
        # two-minute rebuild with nothing on screen.
        st.error(
            "**The graph is not readable.** Kùzu allows one writer, so a running "
            "`python -m bzk.rebuild` holds the database and a read-only connection is refused. "
            f"Wait for the rebuild to finish and reload.\n\n```\n{exc}\n```"
        )
        return

    # `query.site_ids` and `query.analysis_ids` exist because this line needed them. The first
    # draft wrote the `MATCH` here, which is the leak the import rule exists to catch — see
    # `bzk/query/graph.py::analysis_ids`.
    site_panel(conn, query.site_ids(conn))
    gene_panel(conn)
    absences_panel(conn, query.analysis_ids(conn))


# Streamlit executes the script top to bottom with `__name__ == "__main__"`, so the guard is what
# runs the app; a bare call beside it would render everything twice.
if __name__ == "__main__":
    main()
