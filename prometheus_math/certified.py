"""Certified ball arithmetic — Arb (FLINT 3) via python-flint.

The substrate's `precision_dps` fields record how much precision was REQUESTED. This module
records what the error actually IS: every value is a ball (midpoint ± radius) whose enclosure
is certified by Arb's rigorous ball arithmetic. A verdict built on a CertifiedValue can say
"decisively nonzero" and mean it — the trichotomy {yes, no, indeterminate} replaces float
optimism at exactly the resolution boundaries where INCONCLUSIVE verdicts live
(feedback: resolution-dependent truth, 2026-05-04).

Design note, learned RED->GREEN: the midpoint must be held at arbitrary precision (mpmath.mpf
parsed from Arb's decimal serialization, radius widened by the serialization error). The first
draft exported to Python float and silently capped every ball at ~1e-16 radius — the authority
tests (OEIS digits at 25-30 dps) caught it immediately, which is what they are for.

Wraps, does not rewrite (Standing Order #1): all rigor comes from flint.arb; this file only
gives it a stable, substrate-facing interface. Tests: prometheus_math/tests/test_certified.py.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from typing import Union

import mpmath
from flint import arb, ctx

__all__ = ["CertifiedValue", "certified_const", "certified_zeta", "KNOWN_CONSTANTS",
           "CONSTANT_AUTHORITIES"]

_GUARD_BITS = 16
_LOG2_10 = math.log2(10)
#: extra decimal digits carried through serialization so the export widening is negligible
_SER_EXTRA = 12

Number = Union[int, float, "CertifiedValue"]


def _bits(dps: int) -> int:
    if not isinstance(dps, int) or dps <= 0:
        raise ValueError(f"dps must be a positive integer, got {dps!r}")
    return int(math.ceil(dps * _LOG2_10)) + _GUARD_BITS


def _ensure_int_digits(n: int) -> None:
    """Python >= 3.11 caps int<->str conversion at 4300 digits; certified balls at high dps
    legitimately exceed that (documented edge: dps=5000). Raise the cap, never lower it."""
    if n + 100 > sys.get_int_max_str_digits():
        sys.set_int_max_str_digits(n + 200)


def _with_prec(bits: int, fn):
    """Run fn under a temporary Arb working precision; always restore."""
    old = ctx.prec
    ctx.prec = bits
    try:
        return fn()
    finally:
        ctx.prec = old


@dataclass(frozen=True)
class CertifiedValue:
    """A certified real ball: the true value lies within midpoint ± radius.

    midpoint and radius are mpmath.mpf at (dps + slack) working precision, built from Arb's
    own serialization with the serialization error folded INTO the radius — so `contains`
    stays sound end to end. Arithmetic re-enters Arb so enclosures stay rigorous THROUGH
    operations, not just at endpoints.
    """

    mid_str: str
    rad_str: str
    dps: int
    _wdps: int = field(init=False, repr=False, default=0)

    def __post_init__(self) -> None:
        object.__setattr__(self, "_wdps", self.dps + _SER_EXTRA + 10)

    # ---- construction ------------------------------------------------------------------

    @staticmethod
    def _from_arb(x: arb, dps: int) -> "CertifiedValue":
        ser_digits = dps + _SER_EXTRA
        # Store Arb's own decimal serialization VERBATIM. The first draft re-rounded it through
        # mpmath.nstr, which silently shortened the string below the width the radius widening
        # assumed — an unsound ball, caught by the OEIS authority tests. One serialization,
        # one accounted-for rounding.
        mid_s = x.mid().str(ser_digits, radius=False)
        _ensure_int_digits(ser_digits)
        with mpmath.workdps(ser_digits + 10):
            mid = mpmath.mpf(mid_s)
            # Serialization rounds to ser_digits significant digits: error <= one unit in the
            # last printed place, bounded by (|mid|+1) * 10^(1-ser_digits).
            ser_err = (abs(mid) + 1) * mpmath.mpf(10) ** (1 - ser_digits)
            rad = mpmath.mpf(float(x.rad())) + ser_err
            return CertifiedValue(mid_str=mid_s, rad_str=mpmath.nstr(rad, 20), dps=dps)

    # ---- numeric views -----------------------------------------------------------------

    @property
    def midpoint(self) -> mpmath.mpf:
        _ensure_int_digits(self._wdps)
        with mpmath.workdps(self._wdps):
            return mpmath.mpf(self.mid_str)

    @property
    def radius(self) -> mpmath.mpf:
        with mpmath.workdps(self._wdps):
            return mpmath.mpf(self.rad_str)

    def _to_arb(self) -> arb:
        return arb(arb(self.mid_str), float(self.radius))

    # ---- predicates --------------------------------------------------------------------

    def contains(self, x) -> bool:
        """True iff x lies inside the certified enclosure (sound: never excludes the truth)."""
        _ensure_int_digits(self._wdps)
        with mpmath.workdps(self._wdps):
            return abs(mpmath.mpf(x) - self.midpoint) <= self.radius

    def overlaps(self, other: "CertifiedValue") -> bool:
        with mpmath.workdps(max(self._wdps, other._wdps)):
            return abs(self.midpoint - other.midpoint) <= (self.radius + other.radius)

    def decisively_nonzero(self) -> bool:
        """True ONLY when 0 is excluded from the ball. Indeterminate is not a yes."""
        with mpmath.workdps(self._wdps):
            return abs(self.midpoint) > self.radius

    # ---- certified arithmetic (re-enters Arb) ------------------------------------------

    def _binop(self, other: Number, op) -> "CertifiedValue":
        dps = self.dps if not isinstance(other, CertifiedValue) else min(self.dps, other.dps)
        bits = _bits(dps)
        o = other._to_arb() if isinstance(other, CertifiedValue) else arb(other)
        return _with_prec(bits, lambda: CertifiedValue._from_arb(op(self._to_arb(), o), dps))

    def __add__(self, other: Number) -> "CertifiedValue":
        return self._binop(other, lambda a, b: a + b)

    def __sub__(self, other: Number) -> "CertifiedValue":
        return self._binop(other, lambda a, b: a - b)

    def __mul__(self, other: Number) -> "CertifiedValue":
        return self._binop(other, lambda a, b: a * b)

    def __truediv__(self, other: Number) -> "CertifiedValue":
        return self._binop(other, lambda a, b: a / b)

    def __pow__(self, k: int) -> "CertifiedValue":
        return self._binop(k, lambda a, b: a ** b)

    def __repr__(self) -> str:
        return f"CertifiedValue({self.mid_str[:24]}… ± {float(self.radius):.3e} @ {self.dps}dps)"


#: name -> zero-arg Arb constructor. Extend here; tests sample from this registry, so a new
#: entry is automatically covered by every property test (containment, monotone radius,
#: composition). Each carries its OEIS decimal-expansion A-number as the authority the
#: acceptance suite checks against.
KNOWN_CONSTANTS = {
    "pi": lambda: arb.pi(),                     # OEIS A000796
    "e": lambda: arb.const_e(),                 # OEIS A001113
    "catalan": lambda: arb.const_catalan(),     # OEIS A006752
    "euler_gamma": lambda: arb.const_euler(),   # OEIS A001620
    "log2": lambda: arb.const_log2(),           # OEIS A002162
    "glaisher": lambda: arb.const_glaisher(),   # OEIS A074962
    "khinchin": lambda: arb.const_khinchin(),   # OEIS A002210
}

#: Authority pointers, kept ON the module (provenance doctrine: the reference travels with
#: the value, not in a commit message).
CONSTANT_AUTHORITIES = {
    "pi": "OEIS A000796", "e": "OEIS A001113", "catalan": "OEIS A006752",
    "euler_gamma": "OEIS A001620", "log2": "OEIS A002162",
    "glaisher": "OEIS A074962", "khinchin": "OEIS A002210",
}


def certified_const(name: str, dps: int) -> CertifiedValue:
    """A certified ball for a named mathematical constant at >= dps decimal digits."""
    bits = _bits(dps)
    try:
        make = KNOWN_CONSTANTS[name]
    except KeyError:
        raise ValueError(
            f"unknown constant {name!r}; known: {sorted(KNOWN_CONSTANTS)}"
        ) from None
    return _with_prec(bits, lambda: CertifiedValue._from_arb(make(), dps))


def certified_zeta(s, dps: int) -> CertifiedValue:
    """A certified ball for the Riemann zeta function at real s != 1."""
    bits = _bits(dps)
    if s == 1:
        raise ValueError("zeta has a pole at s=1")
    return _with_prec(bits, lambda: CertifiedValue._from_arb(arb(s).zeta(), dps))
