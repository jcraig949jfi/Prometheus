"""The height family's coefficient domain, in one place, so its members cannot disagree.

WHY. Cycle 060 enumerated the five scalar entry points of the height family against the full
non-finite input grid -- 45 calls, no sampling -- and found FOUR different postures toward the
same out-of-domain input:

    mahler_measure      returned `nan`/`inf` on 5 of 9, raised numpy's message on 4
    log_mahler_measure  identical, inherited
    is_cyclotomic       returned `False` on 5 of 9 -- a VERDICT about a non-polynomial
    polynomial_length   returned a number on 9 of 9 -- the most permissive of the family
    house               raised on 7 of 9, and returned **0.0** on 2

`house([inf, 1, -1]) == 0.0` is the one that matters. Zero is house's genuine value for a
MONOMIAL -- all roots at the origin -- so this is not an absurd number that announces itself. It
is a plausible, in-range, wrong answer, of exactly the kind cycles 049-059 established nothing
in this loop has ever caught. It arises because `np.roots` normalises by the leading
coefficient and `[1, -1] / inf` is `[0, 0]`.

The refusals were no better than the returns: six of the seven came from numpy's
`"Array must not contain infs or NaNs"`, which is an implementation detail leaking through a
mathematical interface, and `house([nan])` refused only INCIDENTALLY, via its no-roots-on-a-
constant branch, so any refactor of that branch would silently reopen the hole.

THE DECISION, against the criterion pre-registered before the data was seen: *the posture that
wins is the one under which a caller cannot confuse "no height exists for this input" with "the
height is small."*

    REFUSE. Non-finite coefficients are out of domain and every member says so identically.

Propagation loses that distinction irrecoverably, because NaN is not merely wrong, it is
UNORDERED: `mahler_measure([nan]) < 1.17628` is False, `> 1.17628` is False, and `== 1.0` is
False. A candidate whose measure failed to compute silently drops out of every Lehmer screen
without ever being counted as a failure. That is the campaign's target failure mode exactly.

AND STRINGS, WHICH THE SWEEP FOUND BY ACCIDENT. `mahler_measure(["1.0", "-2.0"])` returned
**2.0** -- the correct answer -- because numpy parses numeric strings on cast to complex128.
Cycle 059's double-encoding fault handed every function in a 128-call sweep a string, and this
function would have answered correctly throughout, concealing it. So str/bytes is rejected by
TYPE, both as a coefficient and as the coefficient sequence.

Kept dependency-free on purpose: `polynomial_length` advertises itself as the O(n) screen you
run before paying for root-finding, and importing numpy into it to check finiteness would tax
the one property it is for. The numpy fast path lives in `require_finite_array`, used only by
the batch entry points, which already hold arrays.
"""
from __future__ import annotations

import math
from typing import Iterable

__all__ = ["NonFiniteCoefficient", "require_finite_coefficients", "require_finite_array"]


class NonFiniteCoefficient(ValueError):
    """A coefficient was NaN or infinite, so no height is defined for this input.

    Subclasses `ValueError` deliberately: the family already raises `ValueError` for the zero
    polynomial, existing callers catch `ValueError`, and this must not become a new exception
    escaping through code that was written to handle out-of-domain input. Callers that need to
    tell "not a polynomial" from "not a number" catch this subclass; callers that only need
    "out of domain" keep working untouched.
    """


def _non_finite_reason(c) -> str | None:
    """The reason `c` is not a finite complex number, or None if it is one.

    Returns a REASON rather than a bool because the message has to name what was wrong; a
    guard whose message says only "invalid input" sends the caller back to the source.
    """
    if isinstance(c, (str, bytes, bytearray)):
        # Never reached via the public entry points (they reject str/bytes by type first);
        # kept so a direct caller of this helper cannot slip a numeric string past it.
        raise TypeError(
            f"coefficient {c!r} is a string. Numeric strings CAST SILENTLY to complex "
            f"(complex('1.0') == 1+0j), so a string-typed argument would produce a correct-"
            f"looking height and conceal an encoding fault upstream.")
    try:
        z = complex(c)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"coefficient {c!r} is not a number: {exc}") from None
    if not math.isfinite(z.real):
        return f"real part is {z.real}"
    if not math.isfinite(z.imag):
        return f"imaginary part is {z.imag}"
    return None


def require_finite_coefficients(coefficients: Iterable, *, function: str) -> list:
    """Return the coefficients unchanged, or refuse. A GUARD, never a transform.

    Raises
    ------
    TypeError
        If `coefficients` is a `str`/`bytes` (a string is not a coefficient sequence, and
        iterating it yields characters -- `polynomial_length("123")` returned 6.0), or if any
        coefficient is a string or a non-number.
    NonFiniteCoefficient
        If any coefficient has a non-finite real or imaginary part. The message names the
        INDEX and the value, because the pre-guard failure mode was position-dependent and a
        message without the index leaves the caller to re-find it.
    """
    if isinstance(coefficients, (str, bytes, bytearray)):
        raise TypeError(
            f"{function}: coefficients must be a sequence of numbers, not {type(coefficients).__name__}. "
            f"Iterating a string yields CHARACTERS -- polynomial_length('123') returned 6.0 "
            f"this way -- so a string argument is a caller error, not a degenerate polynomial.")
    out = list(coefficients)
    for i, c in enumerate(out):
        reason = _non_finite_reason(c)
        if reason is not None:
            raise NonFiniteCoefficient(
                f"{function}: coefficient at index {i} is {c!r} ({reason}). No height is "
                f"defined for a polynomial whose coefficients are not complex numbers. This "
                f"REFUSES rather than propagating NaN because NaN is unordered: a propagated "
                f"NaN measure is neither below nor above the Lehmer bound nor equal to 1, so "
                f"a failed computation would be indistinguishable from a candidate that simply "
                f"did not qualify.")
    return out


def require_finite_array(array, *, function: str):
    """The same refusal for a numpy array, vectorised, for the batch entry points.

    The scalar loop is O(n) in Python and the batch paths run over millions of rows, so this
    exists to keep the guard from becoming the cost of the thing it guards.

    THE CONTRACT THIS PRESERVES. `mahler_measure_padded` uses NaN in its OUTPUT as the in-band
    signal for an all-zero (degenerate) row. If non-finite INPUT were allowed to reach the
    output as NaN as well, one symbol would mean two different things -- "this row had no
    polynomial in it" and "this row's coefficients were garbage" -- and no caller could tell
    them apart. Refusing at the front door keeps `NaN out <=> degenerate row in` an invariant
    a caller can rely on.
    """
    import numpy as np

    a = np.asarray(array)
    if a.size == 0:
        return a
    if a.dtype.kind in "US":
        raise TypeError(
            f"{function}: coefficient array has string dtype {a.dtype!r}. Numeric strings cast "
            f"silently to complex, which would produce correct-looking heights from malformed "
            f"input.")
    if a.dtype.kind not in "fciub":
        return a                       # object/other dtype: leave it to the scalar path
    if a.dtype.kind in "iub":
        return a                       # integers are finite by construction
    if bool(np.all(np.isfinite(a))):
        return a
    bad = np.argwhere(~np.isfinite(a))
    first = tuple(int(x) for x in bad[0])
    raise NonFiniteCoefficient(
        f"{function}: {len(bad)} non-finite coefficient(s); first at index {first} with value "
        f"{a[first]!r}. Refused at the front door so that NaN in the OUTPUT keeps exactly one "
        f"meaning -- a degenerate (all-zero) row -- rather than also meaning 'the input was "
        f"malformed', which no caller could distinguish.")
