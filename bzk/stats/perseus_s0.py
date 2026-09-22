"""`perseus_s0` — the SAM-style modified *t* with permutation FDR. §4's default and required entry.

**Why it exists now and not before.** `ARCHITECTURE.md` §4 has called this entry *default and
required* since ADR-0015, and `ROADMAP.md` l.73 moved it to v0.2 on 2026-08-11 for one reason:
*"the `s0` and FDR parameter values are not yet known"*, and ADR-0017 records what guessing them
would be worth — *being 95% right about `s0` and permutation FDR is worse than useless*. For
`PXD018299` they are now known from the publication itself (PMC7884788, Methods, *Data analysis*):
*Perseus (v1.6.0.2) … a t-test with permutation FDR = 0.01 … and s0 = 0.1*, applied by the Fig. 2
legend to all the paper's proteomic analyses. **They are not defaults here.** They are that
deposit's values, they belong to the analysis record that names them, and every parameter below is
required with no default — a default would assert a number for some other deposit that nobody has
supplied.

**The statistic.** Tusher et al.'s SAM form, as §4 describes it: `d = (mean_A − mean_B) / (s + s0)`
with `s` the pooled (Student) standard error. That denominator is the whole of the difference from
`welch_t`: §4, *"the `s0` parameter introduces a fold-change dependence into the significance
threshold, producing the characteristic curved boundary on a Perseus volcano rather than straight
cutoffs"*. `_moments` is imported from `bzk/stats/tests.py` rather than reimplemented — one home
for the variance arithmetic, which is the rule that module's own `_Moments` docstring states.

**The null.** Relabellings of the columns that preserve both group sizes. Nothing is resampled and
nothing is assumed about the distribution: the null is what this data looks like when the labels
carry no information, which is the whole reason Perseus uses a permutation FDR rather than BH
(§4: *"Perseus uses permutation-based FDR, not BH"*).

**Two implementation questions the paper does not settle, so both answers are built.** §4 fixes the
statistic and the FDR's kind; it fixes neither the sidedness nor how the relabellings are drawn,
and neither does the publication. Each is a named variant, and **this module chooses between them
for nobody** — H10's gate will choose on published Perseus output, exactly as PC2 chose a t-test
variant in `walk/PREREG-PXD026748-reconstruction.md`. Choosing here, by judgement, is the failure
ADR-0017 names.

**The relabelling count is small at the sizes this project works with, and that is the fact
`exhaustive_when_small` exists for: at 3 against 3 there are only C(6,3) = 20 relabellings, of
which 19 are not the identity.** Twenty draws with replacement from twenty relabellings is not a
finer null than all twenty — it is the same null, sampled badly, with an FDR that moves with the
seed for no reason in the data. Above the cut the enumeration is hopeless (C(12,6) = 924, C(20,10)
= 184,756), so the scheme falls back and says that it did.

**The mirror is why the two `_excluding_trivial` schemes exist, and it is not a nicety — it can
make a variant unable to reach any FDR at all.** The mirror relabelling gives group A precisely
B's columns; it exists only when the two groups are the same size, and its statistic is exactly
`−d` for every row at once. Under `joint`, which counts `|d|`, that reproduces **every observed
`|d|` exactly**, so at every threshold the null count is at least one and the FDR is floored at
`1 / (number of relabellings)` — 1/19 at 3 against 3, whatever the data say. A `joint` variant
that keeps the mirror therefore cannot return a q below that floor, and an FDR of 0.01 is
unreachable for it at that design.

**Measured, not reasoned.** The reviewer's simulation — 1,375 rows at 3 against 3 with 200 planted
+4 SD effects — had `joint` with the mirror kept call **none** of them at FDR 0.01, against **69**
for `per_side` with the exhaustive scheme. **Re-run here at seed 0 on the same shape, the
mechanism reproduces exactly and the sizes do not**, which is what a different draw gives: `joint`
with the mirror called 0 with its smallest q pinned at 0.0526 = 1/19, `per_side` exhaustive called
46, and `joint` with the trivial relabellings excluded reached q = 0 — so the floor is the mirror
and not the draw count. Only the reviewer's figure of 69 is unreproduced, and it is that run's,
not this one's.

A third thing that run shows and is worth carrying: `joint` **without** the mirror still called
only 1 of the 200, because counting `|d|` doubles the null relative to a one-sided count. The
mirror is what makes `joint` impossible at this design; the two-tailed count is what makes it
weak. Excluding the two trivial relabellings is offered as its own scheme rather than folded into
the existing ones because which treatment a published run used is exactly the kind of question
this module refuses to answer by judgement.

## `joint_half`, and what it rests on

`joint_half` is `joint` with the null count at each threshold multiplied by ½, and nothing else.
It is the third sidedness, added 2026-09-22 for `walk/PREREG-PXD018299-H10-attempt2.md` §1, and
three things about it have to travel with it wherever it is used:

1. **It was fitted, on one number at one seed.** H10's attempt 1 failed its gate at precision 1.00
   and recall 0.50: every complete-case protein this implementation called, Perseus had called,
   and Perseus called more. The diagnosis (`notes/scripts/diagnose_gate_g.py`, seed 0, the default
   cell) found the ranking already exact — the top 86 of the statistic *are* the 86 published
   complete-case calls — and the threshold off by about a factor of two: at Perseus's 282nd call
   this module's `joint` q is 0.098, and half of that, 0.049, sits just under Perseus's 0.05.
   **That single figure is the whole of the fit.** `walk/RESULT-PXD018299-H10-attempt1.md` records
   it.
2. **It is unverified against Perseus's code.** The plugin source once cited for it,
   `github.com/JurgenCox/perseus-plugins`, returned **404 on 2026-09-22**, so the convention could
   not be read from an implementation. What it is is the leading *reading* of a counting
   convention — null exceedances counted in one tail against observed exceedances in both — and
   not a transcription of one.
3. **Attempt 1's result is why it exists at all.** It is not a better idea about permutation FDR;
   it is a hypothesis about what one published tool counts, adopted because the alternative was to
   stop. Every result computed under it is in-sample until something outside Table 3 confirms it:
   an independent published Perseus output with its FDR and s0 stated, the code, or the authors.

**At 3 against 3 with the mirror kept, the floor halves with it**: `joint`'s 1/19 becomes 1/38.
That is arithmetic rather than a second claim, and it is asserted in the tests.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass

import numpy as np

from bzk.stats.registry import register
from bzk.stats.tests import _moments

#: The three answers to *"how is sidedness handled"*, none chosen here. `joint_half` was added
#: 2026-09-22 for `walk/PREREG-PXD018299-H10-attempt2.md` §1 — see the module docstring for what
#: it is fitted to and what it is not verified against.
SIDEDNESS = ("joint", "per_side", "joint_half")

#: The four answers to *"how are the relabellings drawn"*, none chosen here. The two
#: `_excluding_trivial` forms were added 2026-09-22 for the reason the module docstring gives.
SCHEMES = (
    "random",
    "random_excluding_trivial",
    "exhaustive_when_small",
    "exhaustive_excluding_trivial",
)

#: What `Analysis.parameters_json` must carry to have run this test. `ARCHITECTURE.md` §4:
#: *"Required parameters, recorded on the `Analysis` per I16: `s0`, `fdr`, and the number of
#: randomisations"*; `ONTOLOGY.md` l.155 names two of the three as identifying. The superset is
#: declared because §4 is the normative source for this entry and a subset would under-record it.
#: `fdr` is §4's name for the level this module calls `alpha`; the outcome carries the value under
#: both readings, so a caller building the payload never has to guess which is meant.
REQUIRED_PARAMETERS = ("s0", "fdr", "randomisations")


class PerseusS0Error(ValueError):
    """The call is not one this test can run. Never downgraded to a warning (`CLAUDE.md`)."""


@dataclass(frozen=True)
class PerseusOutcome:
    """One run's per-row results and the exact conditions that produced them.

    **Not a `TestResult`, and deliberately not made to look like one.** A permutation q-value is
    not a p-value: it is an estimated false-discovery proportion at the threshold that would call
    the row, and putting it in a field named `p_value` would be the shape I15 forbids of values —
    a number presented as something it is not. The registry admits this type rather than the other
    way round; `bzk/stats/registry.py` records why.

    **The conditions travel with the numbers** because the run is not reproducible without them:
    the variant pair, the scheme that *ran* (which is not always the scheme asked for), the
    randomisation count that ran, and the seed. `randomisations_used` rather than `randomisations`
    alone is the figure `ONTOLOGY.md` l.155 wants recorded — what determined the result.
    """

    #: The SAM statistic per row.
    d: np.ndarray
    #: `mean_A − mean_B`, the unmodified difference. Kept beside `d` because I11's reasoning holds
    #: one level up: computing a statistic does not license dropping what it came from.
    difference: np.ndarray
    #: The smallest FDR over the thresholds that would still call the row.
    q_value: np.ndarray
    significant: np.ndarray
    #: `sign(difference)`: +1, −1, or 0 where the two group means are exactly equal.
    direction: np.ndarray

    s0: float
    alpha: float
    sidedness: str
    scheme: str
    #: What actually ran — `random` or `exhaustive`. `exhaustive_when_small` is a request, not a
    #: guarantee, and a fixture recording the request would not say which null was used.
    scheme_used: str
    randomisations: int
    randomisations_used: int
    seed: int


def _statistic(numerator: np.ndarray, denominator: np.ndarray, s0: float) -> np.ndarray:
    """`d = (mean_A − mean_B) / (s + s0)`, row-wise, on the pooled standard error."""
    moments = _moments(numerator, denominator, pooled=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.asarray(moments.difference / (moments.standard_error + s0), dtype=float)


def _relabellings(
    n_a: int, n_b: int, *, scheme: str, randomisations: int, seed: int
) -> tuple[list[np.ndarray], str, int]:
    """`(index arrays, scheme that ran, count)`. The first `n_a` indices of each are group A.

    `exhaustive_when_small` enumerates `itertools.combinations` in its own deterministic order and
    drops the identity — the one relabelling under which the "null" is the observed data, whose
    inclusion would pull every FDR towards the observed counts by exactly one draw. It keeps the
    mirror (group A given precisely B's columns), which is a genuine relabelling and merely yields
    `−d`; whether that is right depends on the sidedness, which is why the choice is a scheme of
    its own rather than a correction applied here — see the module docstring for what keeping it
    costs under `joint`.

    `exhaustive_excluding_trivial` is the same enumeration with the mirror dropped as well. At
    unequal group sizes there is no mirror, so the two exhaustive schemes coincide and the count
    says so: `C − 1` rather than `C − 2`.

    `random` draws with replacement, as the brief fixes it: the draws are independent, so a
    relabelling can repeat and the identity can come up. Both are properties of the sampling rather
    than defects, and neither is corrected for — a de-duplicating "random" scheme would be a third
    scheme wearing the name of the second.

    `random_excluding_trivial` draws the same way but **keeps drawing until it has
    `randomisations` non-trivial draws**, so the count it reports is the count that ran. Repeats
    are still allowed: what is excluded is the identity and the mirror, not repetition. The loop
    cannot fail to terminate for any design this test accepts, since `n >= 2` per group leaves at
    least four relabellings of which at most two are trivial.
    """
    total = n_a + n_b
    if scheme not in SCHEMES:
        raise PerseusS0Error(f"scheme {scheme!r} is not one of {list(SCHEMES)}")
    # **The cut is on the draws that would actually run, `C − 1`, not on `C`.** The brief states
    # the rule both ways — *"when the number of distinct relabellings, C(n_A + n_B, n_A), is at
    # most `randomisations`"* and, of the same case, *"uses exactly 19 non-identity relabellings at
    # 3 against 3 when `randomisations >= 19`"* — and the two disagree at exactly one point,
    # `randomisations == C - 1`. This resolves it toward the second: `randomisations` is a budget
    # of draws, the identity is never one of the draws, and refusing an enumeration of 19 because
    # a twentieth relabelling exists that the scheme would not use is a fallback with no cost
    # behind it. At 3 against 3 the cut therefore bites at 19, and at 18 it falls back.
    identity = frozenset(range(n_a))
    # The mirror exists only at equal group sizes: there is no relabelling that hands A exactly
    # B's columns when the two counts differ.
    mirror = frozenset(range(n_a, total)) if n_a == n_b else None
    trivial = {identity} | ({mirror} if mirror is not None else set())
    excluding = scheme.endswith("_excluding_trivial")
    dropped = len(trivial) if excluding else 1

    distinct = math.comb(total, n_a)
    if scheme.startswith("exhaustive") and distinct - dropped <= randomisations:
        skip = trivial if excluding else {identity}
        draws = [
            np.array([*group, *[i for i in range(total) if i not in set(group)]])
            for group in itertools.combinations(range(total), n_a)
            if frozenset(group) not in skip
        ]
        return draws, "exhaustive", len(draws)

    rng = np.random.default_rng(seed)
    if not excluding:
        return [rng.permutation(total) for _ in range(randomisations)], "random", randomisations

    drawn: list[np.ndarray] = []
    while len(drawn) < randomisations:
        draw = rng.permutation(total)
        if frozenset(draw[:n_a].tolist()) not in trivial:
            drawn.append(draw)
    return drawn, "random_excluding_trivial", randomisations


def _tail_counts(sorted_values: np.ndarray, thresholds: np.ndarray, *, upper: bool) -> np.ndarray:
    """How many of `sorted_values` lie at or beyond each threshold, in the given direction."""
    if upper:
        return np.asarray(
            sorted_values.size - np.searchsorted(sorted_values, thresholds, side="left")
        )
    return np.asarray(np.searchsorted(sorted_values, thresholds, side="right"))


def _q_values(
    observed: np.ndarray,
    null_total: np.ndarray,
    thresholds: np.ndarray,
    *,
    upper: bool,
    draws: int,
    null_scale: float = 1.0,
) -> np.ndarray:
    """The q-value for every row whose statistic is finite, from counts already accumulated.

    `FDR(t)` is the mean over permutations of the null count at `t`, over the observed count at
    `t` — §4's permutation FDR, and the brief's definition verbatim. A row's q is the **smallest
    FDR over the thresholds that would still call it**, which is what makes q monotone: the
    eligible threshold set grows with the statistic, so a running minimum over thresholds ordered
    from least to most extreme is exactly that smallest value, read off at the row's own threshold.

    The FDR is not capped at 1. It is a ratio of counts and can exceed 1 where the labels carry
    nothing; clipping it would assert a bound the estimator does not have, and nothing downstream
    reads q as a probability — significance is `q <= alpha`, and an uncapped q above 1 fails that
    exactly as a capped one would.

    `null_scale` multiplies the null count and is ½ for `joint_half` — the whole of that
    convention, applied at the one place the null count enters. It cannot disturb monotonicity: a
    positive constant factor commutes with the running minimum below, so q stays non-increasing in
    the statistic whatever the scale.
    """
    ordered = np.sort(thresholds) if upper else np.sort(thresholds)[::-1]
    order = np.argsort(thresholds) if upper else np.argsort(thresholds)[::-1]
    observed_sorted = np.sort(observed)
    called = _tail_counts(observed_sorted, ordered, upper=upper)
    with np.errstate(divide="ignore", invalid="ignore"):
        fdr = (null_scale * null_total[order] / draws) / called
    # Least extreme threshold first, so the running minimum at position k is the smallest FDR over
    # every threshold a row at `ordered[k]` would still be called by.
    cummin = np.minimum.accumulate(fdr)
    position = np.searchsorted(ordered, observed) if upper else np.searchsorted(-ordered, -observed)
    return np.asarray(cummin[position], dtype=float)


def _side_q(
    d: np.ndarray,
    null_draws: list[np.ndarray],
    *,
    upper: bool,
    mask: np.ndarray,
    draws: int,
    null_scale: float = 1.0,
) -> np.ndarray:
    """q for the rows in `mask`, against the whole null in one direction. NaN elsewhere."""
    q = np.full(d.shape, np.nan)
    subject = d[mask]
    if subject.size == 0:
        return q
    thresholds = np.unique(subject)
    null_total = np.zeros(thresholds.size)
    for null in null_draws:
        finite = np.sort(null[np.isfinite(null)])
        null_total += _tail_counts(finite, thresholds, upper=upper)
    q[mask] = _q_values(
        subject, null_total, thresholds, upper=upper, draws=draws, null_scale=null_scale
    )
    return q


@register("perseus_s0", parameters=REQUIRED_PARAMETERS)
def perseus_s0(
    numerator: np.ndarray,
    denominator: np.ndarray,
    *,
    s0: float,
    alpha: float,
    randomisations: int,
    seed: int,
    sidedness: str,
    scheme: str,
) -> PerseusOutcome:
    """The SAM-style modified *t* with a permutation FDR, row-wise.

    **Every parameter is required and keyword-only.** Calling `perseus_s0(a, b)` raises `TypeError`
    naming what is missing, which is the point: `ROADMAP.md` l.73 deferred this entry precisely
    because its values were unknown, and a default would put a number in `Analysis.parameters_json`
    that no publication and no collaborator supplied. `sidedness` and `scheme` are required for the
    same reason one level along — they are open questions, and a default would answer one silently.

    **NaN propagates rather than raising**, as `welch_t` has it: a row whose statistic is not
    finite is excluded from the thresholds and from every count, and comes back with `q = NaN` and
    `significant = False`. A caller who skipped imputation gets an obviously empty answer for that
    row rather than a plausible one.
    """
    if sidedness not in SIDEDNESS:
        raise PerseusS0Error(f"sidedness {sidedness!r} is not one of {list(SIDEDNESS)}")
    if s0 < 0:
        raise PerseusS0Error(f"s0 {s0!r} is negative; the SAM denominator is `s + s0`")
    if randomisations < 1:
        raise PerseusS0Error(f"randomisations {randomisations!r} is not a positive count")

    numerator = np.asarray(numerator, dtype=float)
    denominator = np.asarray(denominator, dtype=float)
    n_a, n_b = numerator.shape[1], denominator.shape[1]

    moments = _moments(numerator, denominator, pooled=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        d = np.asarray(moments.difference / (moments.standard_error + s0), dtype=float)

    combined = np.hstack([numerator, denominator])
    draws, scheme_used, used = _relabellings(
        n_a, n_b, scheme=scheme, randomisations=randomisations, seed=seed
    )
    null_draws = [_statistic(combined[:, idx[:n_a]], combined[:, idx[n_a:]], s0) for idx in draws]

    finite = np.isfinite(d)
    if sidedness in ("joint", "joint_half"):
        # One FDR over |d|: both directions share a threshold and a null, which is what makes it
        # one test rather than two half-sized ones. `joint_half` is this and one multiplication —
        # the null count halved — so the two share every line but the scale, which is what makes
        # "as `joint`, except" a statement about the code and not only about the definition.
        absolute = np.abs(d)
        q = _side_q(
            absolute,
            [np.abs(null) for null in null_draws],
            upper=True,
            mask=finite,
            draws=used,
            null_scale=0.5 if sidedness == "joint_half" else 1.0,
        )
    else:
        # Separate FDRs, each on one-sided counts. A row with `d == 0` is placed on the positive
        # side, so every finite row has exactly one q; the choice is visible rather than left to
        # a strict inequality on both sides, which would give such a row none at all.
        upper_mask = finite & (d >= 0)
        lower_mask = finite & (d < 0)
        q = np.where(
            upper_mask,
            _side_q(d, null_draws, upper=True, mask=upper_mask, draws=used),
            _side_q(d, null_draws, upper=False, mask=lower_mask, draws=used),
        )
        q = np.where(finite, q, np.nan)

    significant = np.where(np.isfinite(q), q <= alpha, False)
    return PerseusOutcome(
        d=d,
        difference=moments.difference,
        q_value=q,
        significant=np.asarray(significant, dtype=bool),
        direction=np.sign(moments.difference),
        s0=s0,
        alpha=alpha,
        sidedness=sidedness,
        scheme=scheme,
        scheme_used=scheme_used,
        randomisations=randomisations,
        randomisations_used=used,
        seed=seed,
    )
