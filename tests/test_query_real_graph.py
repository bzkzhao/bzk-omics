"""The five queries against the graph a real ingestion built. Skips when there is none.

**Why this exists beside `test_query.py` rather than instead of it.** A fixture proves a query is
correct about a shape; it cannot prove the query is correct about the *population*. That gap is
what the projection which missed by a factor of three fell into — it counted cached entries where
the builder counts resolved accessions — so the recorded figures get an assertion against the real
thing.

**Why it is one module and not five tests spread through the suite.** Adding a skipping test per
query would have made coverage a function of who runs the suite, which is the thing being avoided.
The two costs are stated rather than absorbed, and both were measured on 2026-08-09 rather than
estimated — neither had a figure in the tree before that, only the mechanism:

* **Coverage.** With no `~/.bzk-omics` at all, **10 of 383 tests skip**: seven here, two in
  `test_pxd018299_baseline.py`, one in `test_protein_groups.py`. **Ten tests, not four gate sites**
  — the gate is per-fixture and per-test, and counting modules understates it by more than half.
* **Wall clock.** This module alone runs in **46.9 s** (*n* = 1), because `site_keying` is called
  2,029 times to check a property only meaningful over all of them. The full suite is
  **107–302 s (n = 5)** with a graph present and **77–89 s (n = 2)** without one. The upper range
  read *233–302 s (n = 3)* until 2026-08-09, when a cold clone ran the same suite against the same
  graph in **107.2 s** and this checkout ran it in **188.8 s** — so the spread is now 3× rather than
  1.3×, and the paragraph below was already the right conclusion two revisions before it had this
  much evidence.

**The wall-clock figures were narrower here on 2026-08-09 and the narrowing was wrong.** This block
read *"37.3 s"* and *"168.7 s … 55.7 s"*, each from a single run, and the next session's
measurements were 46.9 s and 233/238/302 s against a suite that had grown by five seconds of new
tests. So the movement is the machine, not the code, and the same mistake was made here as with
`bzk rebuild`'s wall clock two entries running: **a figure from one session is not a baseline.**
The range is stated with its *n* and nothing finer than *three to five minutes with a graph, about
a minute without* is available from this instrument.

Both costs were accepted deliberately, and the coverage one is the one to watch: a suite that is
three times slower where the data exists is a suite people run where it does not.

Everything asserted here is a figure recorded in `ROADMAP.md` or `ONTOLOGY.md`, so a divergence is a
finding about the graph rather than about this file.
"""

from __future__ import annotations

from pathlib import Path

import kuzu
import pytest

from bzk.query import graph as gq

GRAPH = Path.home() / ".bzk-omics" / "graph.kuzu"
TARGETS = (
    "ADAR", "EIF2AK2", "DDX58", "DDX60", "DHX58", "OAS1", "OAS2",
    "IFIH1", "STAT1", "PSMB9", "PSMB10", "PSMA7", "PSME2", "TAP1",
)  # fmt: skip


@pytest.fixture(scope="module")
def conn() -> kuzu.Connection:
    if not GRAPH.exists():
        pytest.skip("no graph at ~/.bzk-omics/graph.kuzu — run `python -m bzk.rebuild` first")
    connection = gq.connect(GRAPH)
    sites = gq._rows(connection, "MATCH (o:SiteObservation) RETURN count(o)")[0][0]
    if sites != 2029:
        pytest.skip(f"graph holds {sites} SiteObservations, not the recorded 2,029")
    return connection


def test_the_welch_run_is_stored_and_every_row_carries_the_test_that_produced_it(
    conn: kuzu.Connection,
) -> None:
    """**This assertion read the opposite until 2026-08-09** and the reversal is the finding.

    It said `DifferentialResult` was empty and `differential_table` returned `NOT_STORED`, which
    was true while `pxd018299_differential.py` computed results and wrote none. It now writes them,
    so the assertion is on what landed: **1,362** rows under `welch_t` with BH, one per tested
    observation.

    **Both halves of the pair are asserted on every row, not just the test.** ADR-0015's
    Consequences turn on `s0` curvature *and* permutation FDR together, so a row carrying
    `welch_t` and no `fdr_method` is still misreadable as Perseus-comparable. The `all(...)` runs
    over all 1,362 rather than over the first, because a per-row field read off the `Analysis`
    (I16) is exactly the kind that is right on the row someone spot-checks.
    """
    welch = gq._rows(conn, "MATCH (a:Analysis) WHERE a.test = 'welch_t' RETURN a.id")
    assert len(welch) == 1
    rows, absence = gq.differential_table(conn, str(welch[0][0]))
    assert len(rows) == 1362
    assert absence is None
    assert all(r.test == "welch_t" and r.fdr_method == "BH" for r in rows)
    assert all(r.quantity == "intensity_multiplicity_summed" for r in rows)
    # I4: uncorrected by construction on this route, and stated rather than left null.
    assert all(r.protein_adjusted == "not_applied" and r.adjustment_method is None for r in rows)
    # I15's display half is still not derivable from the graph — the denominator is per-sample in
    # `quant.duckdb`, and writing rows did not move it.
    assert all(r.substantially_imputed is None for r in rows)


def test_an_analysis_that_stored_no_results_now_says_none_found_not_not_stored(
    conn: kuzu.Connection,
) -> None:
    """The same empty list, meaning the other thing — which is the whole point of the signature.

    The ingestion and curation analyses produced no `DifferentialResult` and never will. While the
    table was empty that read `NOT_STORED`; now that it holds 1,362 rows belonging to a different
    analysis, the honest answer for these two is `NONE_FOUND`. Asserted because the transition is
    invisible at the call site: both return `[]`.
    """
    others = gq._rows(conn, "MATCH (a:Analysis) WHERE a.test IS NULL RETURN a.id ORDER BY a.id")
    assert len(others) == 2
    for (analysis_id,) in [(str(r[0]),) for r in others]:
        rows, absence = gq.differential_table(conn, analysis_id)
        assert rows == []
        assert absence is gq.Absence.NONE_FOUND


def test_every_site_carries_a_keying_basis_and_only_the_promoted_ones_a_displaced_accession(
    conn: kuzu.Connection,
) -> None:
    """§6.3 and I17, over all 2,029 rather than over one.

    The 522 is `ROADMAP.md`'s recorded promotion count, and it has to be *exactly* the set with a
    non-null `displaced_protein`: a promotion that displaced nothing, or a displacement without a
    promotion, is I17's *never silently* failing in one direction or the other.
    """
    sites = sorted({str(r[0]) for r in gq._rows(conn, "MATCH (s:ModificationSite) RETURN s.id")})
    assert len(sites) == 2029
    with_basis = with_displaced = promoted = 0
    for site_id in sites:
        keying = gq.site_keying(conn, site_id)
        assert keying is not None
        if keying.keying_basis:
            with_basis += 1
        if keying.displaced_protein:
            with_displaced += 1
        if "reviewed_preferred" in keying.keying_basis:
            promoted += 1
    assert with_basis == 2029
    assert with_displaced == 522
    assert promoted == 522, "a promotion and a displacement must be the same set (I17)"


def test_only_the_analysis_that_imputed_satisfies_i15(conn: kuzu.Connection) -> None:
    """**Read *no analysis has one* until 2026-08-09.** One does now, and two still do not.

    I15 requires an `Analysis` that produced results to declare its imputation — *including*
    `method = 'none'`. The `welch_t` run declares `downshifted_normal` with its seed, which is what
    makes the imputation mask reconstructible rather than lost to a count. The ingestion and
    curation analyses produced no results, so their violation is the harmless kind and is still
    reported rather than excused.
    """
    analyses = [str(r[0]) for r in gq._rows(conn, "MATCH (a:Analysis) RETURN a.id ORDER BY a.id")]
    assert len(analyses) == 3
    satisfied = [a for a in analyses if gq.imputation_state(conn, a).satisfies_i15]
    assert len(satisfied) == 1
    state = gq.imputation_state(conn, satisfied[0])
    assert state.methods == ("downshifted_normal",)
    assert state.seeds == (0,)
    assert state.absence is None
    for analysis_id in [a for a in analyses if a != satisfied[0]]:
        other = gq.imputation_state(conn, analysis_id)
        assert other.methods == () and other.seeds == ()
        # Not `NOT_STORED`: `Imputation` is no longer empty, so an absence here is about this
        # analysis rather than about the table.
        assert other.absence is gq.Absence.NONE_FOUND
        assert not other.satisfies_i15


def test_the_refusals_are_not_recoverable_from_the_graph(conn: kuzu.Connection) -> None:
    # 27 refusals are reported at ingestion and 0 are recoverable. The gap is the finding.
    answer = gq.refusals(conn)
    assert answer.reasons == ()
    assert answer.absence is gq.Absence.NOT_RETAINED


def test_twelve_of_the_fourteen_symbols_are_present_and_both_absences_are_unattributable(
    conn: kuzu.Connection,
) -> None:
    """**Identifiability, not recovery.** `ROADMAP.md` fixes what this 12 means and this asserts it.

    Twelve published symbols are answerable from stored `Gene.symbol`. No differential is run here
    and no comparison to a recovery figure is made — the assertion below is on which symbols are
    stored, and the `RIGI` line is why the count is not the whole answer: `DDX58` is absent under
    its own name while the gene is present under the one HGNC renamed it to.
    """
    answers = gq.gene_symbols(conn, TARGETS)
    present = sorted(a.symbol for a in answers if a.present)
    absent = sorted(a.symbol for a in answers if not a.present)
    assert len(present) == 12
    assert absent == ["DDX58", "OAS1"]
    for answer in answers:
        if not answer.present:
            assert answer.absence is gq.Absence.UNATTRIBUTABLE

    [rigi] = gq.gene_symbols(conn, ["RIGI"])
    assert rigi.present and rigi.gene_id == "hgnc:HGNC:19102"


def test_nothing_in_the_real_graph_is_unprovenanced(conn: kuzu.Connection) -> None:
    # I5, and the totals matter: `DifferentialResult: (0, 0)` is 0 of 0, which the bare count
    # would have shown as a pass.
    assert gq.unprovenanced(conn) == {
        "Dataset": (0, 1),
        "SiteObservation": (0, 2029),
        # Was `(0, 0)` until 2026-08-09 — 0 of 0, which the bare count would have shown as a pass
        # and which the totals exist to distinguish. It is now 0 of 1,362, and the same first
        # number means something.
        "DifferentialResult": (0, 1362),
    }


def test_the_gene_absence_census_matches_the_recorded_partition(conn: kuzu.Connection) -> None:
    census = gq.gene_absence_census(conn)
    assert census == {
        "encoded": 1054,
        "unresolved": 3492,
        "no_cross_reference": 15,
        "not_captured": 0,
    }
    assert sum(census.values()) == 4561
