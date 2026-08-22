"""MEASUREMENT — a three-valued result that makes one recurring bug unrepresentable.

Seven times now, across four modules, a measure has answered on input outside its own domain
instead of saying so:

    029  structural_constancy          all-raising probe space read as constancy
    037  find_aliasing_witness         None for "nothing to compare" and for "found nothing"
    037  fiber_search                  None for "empty fiber" and for "no flip"
    038  refinement_multiplicity       0 for "does not refine" and for "no fragmentation"
    039  murphy skill                  0.0 for "no skill" and for "skill undefined"
    039  verify_factorization          True for "factors through" and for "nothing to check"
    039  uniform_adversary.survived    True for "schema holds" and for "schema never ran"

Every one was found by a *different* instrument and none by reading the code. Detection works;
prevention does not. So this is the prevention attempt: a result type in which the conflation
cannot be written down.

**The three guarantees, and each exists because a specific past bug needed it:**

1. `.value` RAISES on `OUT_OF_DOMAIN`. You cannot get a number out without having handled the
   third case, so "there was nothing to look at" can never be arithmetic'd as though it were
   zero. (refinement_multiplicity, murphy skill.)
2. `__bool__` RAISES ALWAYS. `if result:` is the single most likely way to silently treat
   OUT_OF_DOMAIN as falsy — the same shape as `if not witness:`. Forcing an explicit status
   comparison is the point. (find_aliasing_witness, fiber_search.)
3. `OUT_OF_DOMAIN` without a `reason` RAISES at construction. An unexplained refusal is only
   marginally better than a wrong answer. (verify_factorization, uniform_adversary.)

**What the type buys, and what it does not.** It makes the conflation *inexpressible*: a measure
using `Measurement` cannot accidentally return a value that means both things, because the two
live in different constructors and the third refuses to be read as a value.

It does **not** make measures *correct*. A measure can still return `signal(...)` where it should
have returned `out_of_domain(...)` — that is a judgement about the domain, and no type checks
judgements. The type converts a silent-by-default failure into one that requires an explicit
wrong decision, which is a smaller target but not an empty one. `mistyped_domain_is_still_possible`
demonstrates exactly that, because a type shipped without its own anti-case would be the
fourth-cycle-running mistake.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

__all__ = ["Measurement", "SIGNAL", "NO_SIGNAL", "OUT_OF_DOMAIN", "signal", "no_signal",
           "out_of_domain", "MeasurementError", "measured", "mistyped_domain_is_still_possible"]

SIGNAL = "SIGNAL"
NO_SIGNAL = "NO_SIGNAL"
OUT_OF_DOMAIN = "OUT_OF_DOMAIN"


class MeasurementError(ValueError):
    """Raised on an ill-formed measurement, or on reading a value that does not exist."""


@dataclass(frozen=True)
class Measurement:
    """A measure's verdict, with the third case impossible to mistake for the other two."""

    status: str
    _value: Any = None
    reason: str = ""

    def __post_init__(self) -> None:
        if self.status not in (SIGNAL, NO_SIGNAL, OUT_OF_DOMAIN):
            raise MeasurementError(f"unknown status {self.status!r}")
        if self.status == OUT_OF_DOMAIN and not self.reason:
            raise MeasurementError(
                "OUT_OF_DOMAIN requires a reason. An unexplained refusal is only marginally "
                "better than a wrong answer — the caller still cannot tell what to fix")

    # -- guarantee 1 ---------------------------------------------------------------------------
    @property
    def value(self) -> Any:
        if self.status == OUT_OF_DOMAIN:
            raise MeasurementError(
                f"no value: the measure was not applicable ({self.reason}). Reading a value here "
                "is exactly the conflation this type exists to prevent")
        return self._value

    # -- guarantee 2 ---------------------------------------------------------------------------
    def __bool__(self) -> bool:
        raise MeasurementError(
            "a Measurement has no truth value — `if result:` would silently treat "
            "OUT_OF_DOMAIN as falsy, which is the shape of four of the seven past bugs. "
            "Compare the status explicitly: `result.status is SIGNAL`")

    # -- convenience that does NOT reintroduce the hole ------------------------------------------
    @property
    def is_signal(self) -> bool:
        return self.status == SIGNAL

    @property
    def is_no_signal(self) -> bool:
        return self.status == NO_SIGNAL

    @property
    def is_applicable(self) -> bool:
        return self.status != OUT_OF_DOMAIN

    def value_or(self, default: Any) -> Any:
        """Explicit opt-in to a default. Fine — the caller has said so in writing."""
        return default if self.status == OUT_OF_DOMAIN else self._value

    def render(self) -> str:  # pragma: no cover - reporting only
        if self.status == OUT_OF_DOMAIN:
            return f"OUT_OF_DOMAIN ({self.reason})"
        return f"{self.status} = {self._value!r}"


def signal(value: Any = True) -> Measurement:
    return Measurement(SIGNAL, value)


def no_signal(value: Any = False) -> Measurement:
    return Measurement(NO_SIGNAL, value)


def out_of_domain(reason: str) -> Measurement:
    return Measurement(OUT_OF_DOMAIN, None, reason)


def measured(fn: Callable, applicable: Callable[..., Optional[str]],
             is_signal: Callable[[Any], bool]) -> Callable[..., Measurement]:
    """Adapt an existing bare-value measure without changing its signature.

    `applicable(*args)` returns None when the input is in-domain, or a REASON string when it is
    not. This lets the four already-repaired sites express their repair in the type rather than
    remembering it, without a breaking change to their callers.
    """
    def wrapped(*args, **kwargs) -> Measurement:
        why = applicable(*args, **kwargs)
        if why is not None:
            return out_of_domain(why)
        try:
            v = fn(*args, **kwargs)
        except Exception as exc:
            return out_of_domain(f"{type(exc).__name__}: {exc}")
        return signal(v) if is_signal(v) else no_signal(v)
    return wrapped


def mistyped_domain_is_still_possible() -> bool:
    """THE TYPE'S OWN ANTI-CASE — the answer I do not want, constructed deliberately.

    A measure that decides wrongly whether its input is in-domain returns a perfectly well-formed
    `SIGNAL` where `OUT_OF_DOMAIN` was correct. The type cannot see that: it enforces the SHAPE of
    the answer, not the judgement behind it.

    Returns True, and it should. Reported honestly rather than left for someone to discover.
    """
    lies = measured(lambda xs: len(xs),
                    applicable=lambda xs: None,          # claims everything is in-domain
                    is_signal=lambda v: v > 0)
    m = lies([])                                          # empty input: genuinely out of domain
    return m.status == NO_SIGNAL                          # ...and it answered anyway
