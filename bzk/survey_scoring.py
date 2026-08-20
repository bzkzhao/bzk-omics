"""C1's five body-only components, scored from a candidate's site table.

**These procedures are transcribed from the registration in `ROADMAP.md` § *Pre-registration:
scoring the five body-only components* (l.8189-8288 at `a720ec6`) and from nothing else.** The
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

#: Criterion 2's sample floor is the band's own (l.3885); criterion 5's is the registration's.
MIN_PICK_SAMPLE = 20
MIN_MULTIPLICITY_COMPARISONS = 20

#: Criterion 5's verdict thresholds and tolerance (l.8280-8288).
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
    """Criterion 1 (l.8206-8207)."""

    multi: int
    total: int

    @property
    def rate(self) -> float | None:
        return self.multi / self.total if self.total else None


@dataclass(frozen=True)
class IsoformPicks:
    """Criterion 2 (l.8218-8220). `sample` is the parseable-pick count and is the band's sample."""

    isoform: int
    sample: int

    @property
    def rate(self) -> float | None:
        return self.isoform / self.sample if self.sample else None

    @property
    def scorable(self) -> bool:
        """False is the third state — `unscorable`, never *does not differ* (l.8223-8225)."""
        return self.sample >= MIN_PICK_SAMPLE


@dataclass(frozen=True)
class UnrecordedThreshold:
    """Criterion 9 (l.8236-8238). The yes/no is the score; `rate` is measured and is not."""

    below_cut: int
    total: int

    @property
    def pre_filtered(self) -> bool:
        return self.below_cut == 0

    @property
    def rate_not_scored(self) -> float | None:
        return self.below_cut / self.total if self.total else None


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
    """Criterion 5's component (l.8273-8288).

    `trivial` rows agree vacuously and are excluded from the verdict; `zero_base_nonzero_total` rows
    are neither trivial nor counted, because the registration computes the verdict over `base > 0`
    and a zero base with a non-zero total satisfies neither clause. It is surfaced rather than
    folded into a neighbour so the accounting closes.
    """

    agree: int
    comparisons: int
    trivial: int
    zero_base_nonzero_total: int
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


def score_site_table(path: Path, samples: Sequence[str]) -> Scores:
    """Score one artefact's MaxQuant site table against C1's five body-only components.

    `samples` are the per-sample column suffixes the corrected D1 returns for this artefact; see the
    module docstring for why they are an argument.
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
        agree = comparisons = trivial = zero_base = substituted = 0

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
            elif leading is not None and row[leading].strip():
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
                    continue  # the verdict is computed over `base > 0`
                comparisons += 1
                if abs(base - total) <= max(ABSOLUTE_TOLERANCE, RELATIVE_TOLERANCE * base):
                    agree += 1

    return Scores(
        rows_total=rows_total,
        rows_in_denominator=rows_denominator,
        rows_after_localisation_cut=rows_denominator - below_cut,
        multi_mapping=MultiMapping(multi=multi, total=rows_denominator),
        isoform_picks=IsoformPicks(isoform=isoforms, sample=picks),
        unrecorded_threshold=UnrecordedThreshold(below_cut=below_cut, total=rows_denominator),
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
            substituted_operands=substituted,
            samples_without_multiplicity_columns=samples_without,
        ),
    )
