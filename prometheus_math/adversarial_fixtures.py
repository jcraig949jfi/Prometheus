"""ADVERSARIAL FIXTURES — anti-cases sourced from the domain, not from the author. (Cycle 038.)

Cycle 037 certified twelve instruments and nine passed first time. I wrote both the instruments
and their anti-cases, and cycle 036 had already shown fixtures are gameable — so those nine
passes have two readings I could not tell apart:

    (a) the arsenal was sound
    (b) my anti-cases were too easy

The difference is who chose the input. A hand-written anti-case tests the failure its author
imagined; that is exactly the blind spot the whole contract exists for, relocated one level up.

So: state an INVARIANT that follows from what the instrument ADVERTISES, then let a property
search over the input domain hunt for a violation. The invariant comes from the instrument's
claim; the input comes from the domain. Neither comes from my intuition about which cases are
tricky.

**What this does not fix.** I still write the invariant, so an instrument whose advertised
semantics I have mis-stated will be tested against the wrong property and pass. That is a
strictly smaller hole than hand-picked inputs — an invariant is a universal claim over the whole
domain, while a fixture is one point — but it is not zero, and closing it needs a second author
rather than a cleverer generator.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional, Sequence, Tuple

__all__ = ["Violation", "search_for_violation", "InvariantSpec"]


@dataclass(frozen=True)
class Violation:
    """A domain-sourced anti-case: an input on which the instrument breaks its own advertisement."""

    instrument: str
    invariant: str
    counterexample: Any
    detail: str = ""

    def __str__(self) -> str:  # pragma: no cover - reporting only
        return (f"{self.instrument} violates {self.invariant!r} at {self.counterexample!r}"
                + (f" ({self.detail})" if self.detail else ""))


@dataclass(frozen=True)
class InvariantSpec:
    """One instrument, one advertised property, and a way to draw inputs for it."""

    instrument: str
    invariant: str
    check: Callable[[Any], bool]      # True == the invariant held on this input
    draw: Callable[[Any], Any]        # a Hypothesis data() draw -> an input


def search_for_violation(spec: InvariantSpec, max_examples: int = 300) -> Optional[Violation]:
    """Hunt the input domain for a case where the instrument breaks its advertised invariant.

    Returns the first `Violation` found, or None. **None is not proof** — it is the same bounded
    search the constancy probe reports honestly, and the same caveat applies: a search that finds
    nothing has established nothing about inputs it did not draw.
    """
    from hypothesis import HealthCheck, given, settings, strategies as st

    found: list = []

    @settings(max_examples=max_examples, deadline=None,
              suppress_health_check=list(HealthCheck))
    @given(st.data())
    def _run(data):
        if found:
            return
        try:
            case = spec.draw(data)
        except Exception:
            return
        try:
            ok = spec.check(case)
        except Exception as exc:
            found.append(Violation(spec.instrument, spec.invariant, case,
                                   f"raised {type(exc).__name__}: {exc}"))
            return
        if not ok:
            found.append(Violation(spec.instrument, spec.invariant, case))

    try:
        _run()
    except Exception:
        pass                          # a falsifying example surfaces via `found`
    return found[0] if found else None
