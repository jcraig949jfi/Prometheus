"""prometheus_math.encodings.maass_form_hecke — minimal Maass form Hecke
eigenvalue encoding via :class:`OperatorOutputSequence`.

Per inbox ticket T-2026-05-07-T023 (P1, calibration anchor density in
under-explored harmonic-analysis territory per HARD-4).

Design doc: ``prometheus_math/encodings/maass_form_hecke_GAP.md``.

Per HARD-5: this module's primitive is :class:`OperatorOutputSequence`,
NOT a "MaassForm" class. Maass forms are one INSTANCE of the more general
"object that produces a sequence of values under a parameterized
operator" pattern; modular form q-expansion coefficients, L-function
values at integer arguments, and other harmonic-analysis-flavored objects
are sister instances. The discipline label "Maass form" lives in
``notes`` / docstring metadata, never in chart coordinates.

Per HARD-5 + T-2026-05-07-T029 (multi-precision audit): the module uses
string-encoded high-precision values (mpmath.mpf serialization via str())
to sidestep the float-precision contract gap. When the v2 multi-precision
contract change lands, this primitive's ``output_values`` field can be
type-widened additively without breaking existing serializations.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, NewType, Tuple


SerializedMpf = NewType("SerializedMpf", str)
"""Type alias documenting that a string-encoded value is intended to be
parsed back via mpmath.mpf(...). Documentation-only — Python does not
enforce NewType at runtime."""


@dataclass(frozen=True)
class OperatorOutputSequence:
    """Typed operator-output sequence indexed by a discrete parameter.

    Substrate-grade primitive for "object that produces a sequence of
    values under a parameterized operator." Maass forms are one
    instance (operator = Hecke at prime p; index = primes); modular
    forms' q-expansion coefficients are another (operator = nth Fourier
    coefficient; index = positive integers); L-function values at
    integer arguments are a third (operator = L-evaluation at s; index
    = integers).

    Per HARD-5: discipline label lives in ``notes``, NOT in coordinates.
    The substrate's coordinate is the (operator_id, index_values,
    output_values) shape.

    Per T-2026-05-07-T029 multi-precision audit: ``output_values`` are
    string-encoded (typically ``str(mpmath.mpf(...))`` results) to
    preserve high-precision values that double cannot hold. The explicit
    ``output_precision_dps`` field documents the precision so consumers
    can deserialize at the right precision via ``mpmath.mp.dps`` setup.
    """

    operator_id: str
    index_parameter_name: str
    index_values: Tuple[int, ...]
    output_values: Tuple[SerializedMpf, ...]
    output_precision_dps: int
    output_unit: str
    object_canonical_form: Mapping[str, Any]
    chart_id: str
    notes: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.operator_id, str) or not self.operator_id:
            raise ValueError(
                f"operator_id must be a non-empty string; got {self.operator_id!r}"
            )
        if not isinstance(self.index_parameter_name, str) or not self.index_parameter_name:
            raise ValueError(
                f"index_parameter_name must be a non-empty string; got "
                f"{self.index_parameter_name!r}"
            )
        if not isinstance(self.index_values, tuple):
            raise TypeError(
                f"index_values must be a tuple; got {type(self.index_values).__name__}"
            )
        if not isinstance(self.output_values, tuple):
            raise TypeError(
                f"output_values must be a tuple; got {type(self.output_values).__name__}"
            )
        if len(self.index_values) != len(self.output_values):
            raise ValueError(
                f"index_values and output_values must have the same length; "
                f"got {len(self.index_values)} indices vs "
                f"{len(self.output_values)} outputs"
            )
        if not isinstance(self.output_precision_dps, int) or self.output_precision_dps <= 0:
            raise ValueError(
                f"output_precision_dps must be a positive int; got "
                f"{self.output_precision_dps!r}"
            )
        if not isinstance(self.output_unit, str) or not self.output_unit:
            raise ValueError(
                f"output_unit must be a non-empty string; got {self.output_unit!r}"
            )
        if not isinstance(self.chart_id, str) or not self.chart_id:
            raise ValueError(
                f"chart_id must be a non-empty string; got {self.chart_id!r}"
            )
        if not isinstance(self.object_canonical_form, Mapping):
            raise TypeError(
                f"object_canonical_form must be a mapping; got "
                f"{type(self.object_canonical_form).__name__}"
            )
        if not all(isinstance(s, str) for s in self.output_values):
            raise TypeError(
                "output_values entries must all be strings (typically "
                "str(mpmath.mpf(...)) results); got non-string entry"
            )
        if not all(isinstance(i, int) for i in self.index_values):
            raise TypeError("index_values entries must all be ints")

    def __len__(self) -> int:
        return len(self.index_values)

    def lookup(self, index_value: int) -> SerializedMpf:
        """Return the (string-encoded) operator output at the given index value.

        Raises ``KeyError`` if the index is not in :attr:`index_values`
        (per the 2026-05-07 contract-change window's loud-fail-on-typo
        discipline; T-2026-05-06-ST003 + T-2026-05-07-T018 sister
        pattern). Use :meth:`has_index` for an Optional-style check.
        """
        try:
            i = self.index_values.index(index_value)
        except ValueError:
            raise KeyError(
                f"index_value {index_value!r} not in sequence; available indices: "
                f"{self.index_values}"
            ) from None
        return self.output_values[i]

    def has_index(self, index_value: int) -> bool:
        """True iff ``index_value`` is in this sequence's index set."""
        return index_value in self.index_values


__all__ = [
    "OperatorOutputSequence",
    "SerializedMpf",
]
