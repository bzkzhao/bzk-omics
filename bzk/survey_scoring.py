"""C1's five body-only components, scored from a candidate's site table.

**These procedures are transcribed from the registration in `ROADMAP.md` § *Pre-registration:
scoring the five body-only components* (l.8189-**8294** at `5c158ac`) and from nothing else.** The
figures the previous turn produced live in that document's result tables; this module was written
from the registration and run afterwards, so a divergence between the two is evidence about one of
them rather than a licence to tune this one.

The five are criteria **1** (multi-mapping rate, I14), **2** (isoform razor picks, I2), **9** (the
unrecorded-threshold yes/no, I16's unfired case), **6**'s median-and-scale component, and **5**'s
multiplicity component. **Criteria 3 and 4 are not here**: both need the UniProt resolver, which is
a different kind of cost and was held by a separate decision.

**Sample names are an argument, not something this module derives.** The corrected D1 (ROADMAP.md
§ *The corrected D1, stated in full*, l.7755) defines its vocabulary as the 67 templates *"extracted
programmatically from the fetched page rather than transcribed"*. Hard-coding those 67 strings here
would transcribe a list whose whole provenance claim is that it was not transcribed — the defect
that put two unfounded prefixes in D1's first draft — and fetching the page at call time would make
scoring depend on a network. The seam is left where the provenance question is, so D1 can be made
durable later without touching this file.

**No criterion, band or denominator is defined here.** They live in `ROADMAP.md`'s C1 band table;
this module computes the quantities the bands are read against and reports the third state,
`unscorable`, wherever a band's own sample floor is not met.
"""

from __future__ import annotations

import csv
import re
import statistics
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

#: Registered denominator (l.8189-8190): reverse hits and contaminants removed, no localisation cut.
REVERSE = "Reverse"
CONTAMINANT = "Potential contaminant"
LOCALISATION = "Localization prob"

#: Criterion 9's cut (l.8236-8238) and criterion 6's tolerance and scale ceiling (l.8257-8259).
LOCALISATION_CUT = 0.75
MEDIAN_TOLERANCE = 0.005
SCALE_CEILING = 1.0

#: Criterion 2's two readings of *"the `Protein` column where present"* (l.8218). `PER_TABLE` is
#: normative: *present* is a predicate on the column, and every pick in one artefact then comes from
#: one column, so the rate measures one quantity rather than a blend of two. See `score_site_table`.
PER_TABLE = "per_table"
PER_ROW = "per_row"

#: Criterion 2's sample floor is the band's own (l.3885); criterion 5's is the registration's.
MIN_PICK_SAMPLE = 20
MIN_MULTIPLICITY_COMPARISONS = 20

#: Criterion 5's verdict thresholds and tolerance (l.8280-8288); its differ-rule is l.8290.
SUMMED_AT = 0.99
NOT_SUMMED_AT = 0.01
ABSOLUTE_TOLERANCE = 1.0
RELATIVE_TOLERANCE = 1e-6

_NUMBER = re.compile(r"^-?\d+(\.\d+)?([eE][-+]?\d+)?$")
_MULTIPLICITY_SUFFIX = "___"


def _number(cell: str) -> float | None:
    """A cell's value, or `None` where it is empty, absent or unparseable.

    `NaN` is deliberately unparseable rather than a float: the registration reads it as a *missing*
    operand, and `float("nan")` would silently poison every comparison it entered.
    """
    text = cell.strip()
    return float(text) if _NUMBER.match(text) else None


@dataclass(frozen=True)
class MultiMapping:
    """Criterion 1 (l.8206-8207).

    **`column_present` is what keeps this criterion from degrading to a figure.** Without it a table
    lacking a `Proteins` column reports `0 / denominator`, which reads as *no site multi-maps* — a
    strong claim — where the truth is *this cannot be scored*. Criterion 2 in the same position
    already answers `unscorable` and criterion 6 answers `None`; criterion 1 was the odd one out.
    """

    multi: int
    total: int
    column_present: bool = True

    @property
    def rate(self) -> float | None:
        if not self.column_present or not self.total:
            return None
        return self.multi / self.total

    @property
    def scorable(self) -> bool:
        return self.column_present and self.total > 0


@dataclass(frozen=True)
class IsoformPicks:
    """Criterion 2 (l.8218-8220). `sample` is the parseable-pick count and is the band's sample."""

    isoform: int
    sample: int
    fallback: str = PER_TABLE

    @property
    def rate(self) -> float | None:
        return self.isoform / self.sample if self.sample else None

    @property
    def scorable(self) -> bool:
        """False is the third state — `unscorable`, never *does not differ* (l.8223-8225)."""
        return self.sample >= MIN_PICK_SAMPLE


@dataclass(frozen=True)
class UnrecordedThreshold:
    """Criterion 9 (l.8236-8238). The yes/no is the score; `rate` is measured and is not.

    **`values_seen` is what separates *nobody filtered below 0.75* from *nothing was readable*.**
    A table whose `Localization prob` column is absent, or present and unparseable on every row,
    counts zero rows below the cut and would otherwise answer `pre_filtered = True` — the same answer
    a genuinely pre-filtered deposit gives, from no evidence at all.
    """

    below_cut: int
    total: int
    values_seen: int = 0

    @property
    def pre_filtered(self) -> bool | None:
        return None if self.values_seen == 0 else self.below_cut == 0

    @property
    def rate_not_scored(self) -> float | None:
        return self.below_cut / self.total if self.total and self.values_seen else None


@dataclass(frozen=True)
class LocalisationDistribution:
    """Criterion 6's median-and-scale component (l.8257-8259).

    `minimum` is reported and is **not** part of the differ-test: the band names median, column name
    and scale, and the column-name third is scored elsewhere.
    """

    median: float | None
    minimum: float | None
    maximum: float | None

    @property
    def differs(self) -> bool | None:
        if self.median is None or self.maximum is None:
            return None
        return abs(self.median - 1.00) > MEDIAN_TOLERANCE or self.maximum > SCALE_CEILING


@dataclass(frozen=True)
class MultiplicityIdentity:
    """Criterion 5's component (l.8273-8294).

    `trivial` rows agree vacuously and are excluded from the verdict; `zero_base_nonzero_total` rows
    are neither trivial nor counted, because the registration computes the verdict over `base > 0`
    and a zero base with a non-zero total satisfies neither clause.

    **`negative_base` closes the accounting the sentence above claims to close.** A negative base
    satisfies neither `base == 0` nor `base > 0` either, and it was previously dropped into no
    counter at all — so `comparisons + trivial + zero_base_nonzero_total` could silently fail to
    account for every row with a parseable base. MaxQuant intensities are non-negative, so this is
    expected to be zero on every real table; a counter that is always zero still closes the books,
    and a docstring that promises closure and does not deliver it is the defect being fixed.
    """

    agree: int
    comparisons: int
    trivial: int
    zero_base_nonzero_total: int
    negative_base: int
    substituted_operands: int
    samples_without_multiplicity_columns: int

    @property
    def fraction(self) -> float | None:
        return self.agree / self.comparisons if self.comparisons else None

    @property
    def verdict(self) -> str:
        if self.comparisons < MIN_MULTIPLICITY_COMPARISONS:
            return "unscorable"
        fraction = self.agree / self.comparisons
        if fraction >= SUMMED_AT:
            return "summed"
        return "not summed" if fraction <= NOT_SUMMED_AT else "indeterminate"

    @property
    def differs(self) -> bool | None:
        """Criterion 5's registered differ-rule, l.8290: *differs iff the verdict is not `summed`*.

        **`unscorable` answers `None` rather than `True`, and that is a reading, not a transcription.**
        Taken literally, `unscorable != "summed"` and the rule would return *differs* — but the same
        registration insists at l.8223-8225 that the third state is *"never rounded to does not
        differ"*, and rounding it to *differs* collapses it just as completely in the other
        direction. A criterion that could not be evaluated has no differ-verdict.
        """
        verdict = self.verdict
        return None if verdict == "unscorable" else verdict != "summed"


@dataclass(frozen=True)
class Scores:
    """The five results, plus the three row counts the registration requires reporting.

    `rows_after_localisation_cut` is diagnostic (l.8197-8200): it is reported beside the denominator
    and **does not license** scoring against it instead.
    """

    rows_total: int
    rows_in_denominator: int
    rows_after_localisation_cut: int
    multi_mapping: MultiMapping
    isoform_picks: IsoformPicks
    unrecorded_threshold: UnrecordedThreshold
    localisation: LocalisationDistribution
    multiplicity: MultiplicityIdentity


def _multiplicity_columns(
    header: Sequence[str], samples: Iterable[str]
) -> tuple[list[tuple[int, list[int]]], int]:
    """`(base index, multiplicity indices)` per sample, and the count of samples that have none.

    A sample with no `___j` column carries no identity to test — *the multiplicity columns present
    for that sample* is empty — so it contributes nothing rather than contributing failures. A SILAC
    table reaches this: it splits multiplicity on the ratio family, not on per-sample intensity.
    """
    position = {name: index for index, name in enumerate(header)}
    pairs: list[tuple[int, list[int]]] = []
    without = 0
    for sample in samples:
        base = f"Intensity {sample}"
        if base not in position:
            continue
        prefix = base + _MULTIPLICITY_SUFFIX
        indices = [index for name, index in position.items() if name.startswith(prefix)]
        if indices:
            pairs.append((position[base], sorted(indices)))
        else:
            without += 1
    return pairs, without


def score_site_table(path: Path, samples: Sequence[str], *, fallback: str = PER_TABLE) -> Scores:
    """Score one artefact's MaxQuant site table against C1's five body-only components.

    `samples` are the per-sample column suffixes the corrected D1 returns for this artefact; see the
    module docstring for why they are an argument.

    `fallback` selects between the two readings of criterion 2's *"the `Protein` column where
    present, else the first entry of `Leading proteins`"* (l.8218):

    - **`PER_TABLE`, normative.** *Present* is a predicate on the **column**. If the header carries
      `Protein`, every pick comes from it and a blank cell yields no pick; only a table without the
      column falls back to `Leading proteins`.
    - **`PER_ROW`.** *Present* is a predicate on the **cell**, so the fallback fires row by row.

    **`PER_TABLE` is normative on two grounds and neither is line count.** *Present* is what one says
    of a column and *empty* is what one says of a cell, so it is the more literal reading of the
    registered words. And it keeps the rate homogeneous: under `PER_ROW` a single artefact's rate
    blends picks drawn from two different columns, and criterion 2 exists to compare that rate across
    artefacts. Where `PER_TABLE` costs picks it costs them into the `unscorable` floor, which is the
    third state doing its job rather than a loss.

    The two readings differ only for a table whose `Protein` column exists and is empty on some row.
    """
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader, None)
        if header is None:
            raise ValueError(f"{path}: no header line")
        position = {name: index for index, name in enumerate(header)}
        multiplicity, samples_without = _multiplicity_columns(header, samples)

        reverse = position.get(REVERSE)
        contaminant = position.get(CONTAMINANT)
        proteins = position.get("Proteins")
        protein = position.get("Protein")
        leading = position.get("Leading proteins")
        localisation = position.get(LOCALISATION)

        rows_total = rows_denominator = 0
        multi = 0
        picks = isoforms = 0
        probabilities: list[float] = []
        below_cut = 0
        agree = comparisons = trivial = zero_base = negative_base = substituted = 0

        for raw in reader:
            if not any(cell.strip() for cell in raw):
                continue
            row = raw if len(raw) >= len(header) else [*raw, *[""] * (len(header) - len(raw))]
            rows_total += 1

            flagged = (reverse is not None and row[reverse].strip()) or (
                contaminant is not None and row[contaminant].strip()
            )
            if flagged:
                continue
            rows_denominator += 1

            if proteins is not None and len([p for p in row[proteins].split(";") if p.strip()]) > 1:
                multi += 1

            pick = ""
            if protein is not None and row[protein].strip():
                pick = row[protein].strip()
            elif (
                (protein is None or fallback == PER_ROW)
                and leading is not None
                and row[leading].strip()
            ):
                pick = row[leading].split(";")[0].strip()
            if pick:
                picks += 1
                if "-" in pick:
                    isoforms += 1

            if localisation is not None:
                value = _number(row[localisation])
                if value is not None:
                    probabilities.append(value)
                    if value < LOCALISATION_CUT:
                        below_cut += 1

            for base_index, indices in multiplicity:
                base = _number(row[base_index])
                if base is None:
                    continue  # an unparseable base excludes the row rather than zeroing it
                total = 0.0
                for index in indices:
                    operand = _number(row[index])
                    if operand is None:
                        substituted += 1
                    else:
                        total += operand
                if base == 0:
                    if total == 0:
                        trivial += 1
                    else:
                        zero_base += 1
                    continue
                if base < 0:
                    negative_base += 1  # neither clause covers it; counted so the books close
                    continue
                comparisons += 1
                if abs(base - total) <= max(ABSOLUTE_TOLERANCE, RELATIVE_TOLERANCE * base):
                    agree += 1

    return Scores(
        rows_total=rows_total,
        rows_in_denominator=rows_denominator,
        rows_after_localisation_cut=rows_denominator - below_cut,
        multi_mapping=MultiMapping(
            multi=multi, total=rows_denominator, column_present=proteins is not None
        ),
        isoform_picks=IsoformPicks(isoform=isoforms, sample=picks, fallback=fallback),
        unrecorded_threshold=UnrecordedThreshold(
            below_cut=below_cut, total=rows_denominator, values_seen=len(probabilities)
        ),
        localisation=LocalisationDistribution(
            median=statistics.median(probabilities) if probabilities else None,
            minimum=min(probabilities) if probabilities else None,
            maximum=max(probabilities) if probabilities else None,
        ),
        multiplicity=MultiplicityIdentity(
            agree=agree,
            comparisons=comparisons,
            trivial=trivial,
            zero_base_nonzero_total=zero_base,
            negative_base=negative_base,
            substituted_operands=substituted,
            samples_without_multiplicity_columns=samples_without,
        ),
    )
