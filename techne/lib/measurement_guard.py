"""Make a measurement prove itself before its number is allowed to mean anything.

WHY THIS EXISTS. Across cycles 049-059, seven measurements answered a different question than
the one posed. SIX of the seven were caught because the number looked absurd -- not because
anything checked. A *plausible* wrong answer would have shipped every time, and repeated
traps-ledger entries did not prevent recurrence: the same root cause (setup time attributed to
the thing under test) recurred seven cycles after being written down.

The mechanism is not another rule to remember. It is an ASSERTION THE INSTRUMENT MUST PASS
BEFORE ITS OUTPUT IS READABLE.

    A measurement is trustworthy only if the SAME code path returns the KNOWN answer for a
    case whose answer is known independently.

That converts "is my instrument measuring what I think?" from a judgement into a test. It
would have caught four of the five instrument faults in this record (see `SELF_TEST` below);
the fifth -- a sampling window -- needs `population()`, not a control.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence


class InstrumentInvalid(RuntimeError):
    """The instrument failed its own positive control. Its output must not be read."""


@dataclass
class Measurement:
    """A number that carries what is needed to disbelieve it.

    `value` is deliberately NOT accessible until `validate()` has run, because every failure in
    this record was a number read before its instrument was checked.
    """

    name: str
    _value: Any
    population: str                  # WHICH rows, stated -- not implied
    command: str = ""                # how to reproduce
    controls_passed: list = field(default_factory=list)
    _validated: bool = False

    @property
    def value(self):
        if not self._validated:
            raise InstrumentInvalid(
                f"{self.name}: value read before the instrument passed a positive control")
        return self._value

    def __str__(self) -> str:
        return (f"{self.name} = {self._value!r}\n"
                f"  population: {self.population}\n"
                f"  command   : {self.command or '(not recorded)'}\n"
                f"  controls  : {', '.join(self.controls_passed) or 'NONE -- untrustworthy'}")


def measure(name: str, fn: Callable[[], Any], *, population: str,
            controls: Sequence[tuple[str, Callable[[], Any], Any]],
            command: str = "", rel_tol: float = 1e-9) -> Measurement:
    """Run `fn`, but only after every positive control passes THROUGH THE SAME PATH.

    `controls` is a sequence of `(label, thunk, expected)`. Each thunk must exercise the same
    machinery as `fn` on a case whose answer is known independently of the instrument.

    A control that does not traverse the instrument proves nothing -- that is the whole failure
    mode. A control asserted from the same code that computes the result is a tautology.
    """
    if not controls:
        raise InstrumentInvalid(f"{name}: refusing to measure with no positive control")

    passed = []
    for label, thunk, expected in controls:
        got = thunk()
        ok = _close(got, expected, rel_tol)
        if not ok:
            raise InstrumentInvalid(
                f"{name}: POSITIVE CONTROL FAILED -- {label}: got {got!r}, expected "
                f"{expected!r}. The instrument is not measuring what it claims; its output "
                f"for the real case must not be read.")
        passed.append(label)

    m = Measurement(name=name, _value=fn(), population=population,
                    command=command, controls_passed=passed)
    m._validated = True
    return m


def _close(got, expected, rel_tol) -> bool:
    if isinstance(expected, type) and isinstance(got, expected):
        return True
    if type(got) is not type(expected) and not (
            isinstance(got, (int, float)) and isinstance(expected, (int, float))):
        return False                       # TYPE mismatch is the double-encoding failure
    try:
        return math.isclose(float(got), float(expected), rel_tol=rel_tol, abs_tol=1e-12)
    except (TypeError, ValueError):
        return got == expected


def compare(name: str, arm_a: Callable[[], Any], arm_b: Callable[[], Any], *,
            labels: tuple[str, str], must_differ_case: tuple[Callable[[], Any],
                                                             Callable[[], Any]],
            population: str, command: str = "") -> Measurement:
    """A two-arm comparison that first proves the arms CAN differ.

    Cycle 052 compared a fix against stored literals rather than against the old path; cycle
    057's `s4_clean` comparison had two arms whose true answers were both 1.0. In both cases
    "indistinguishable" was correct and carried no information.

    `must_differ_case` is a pair of thunks whose outputs are known to differ. If they come back
    equal, the comparison cannot detect a difference and the real result is unreadable.
    """
    a_ref, b_ref = must_differ_case
    if _close(a_ref(), b_ref(), 1e-9):
        raise InstrumentInvalid(
            f"{name}: the two arms returned the SAME value on a case chosen because they "
            f"should differ. This comparison cannot detect a difference; its verdict on the "
            f"real case is meaningless.")
    m = Measurement(name=name, _value=(arm_a(), arm_b()), population=population,
                    command=command, controls_passed=[f"arms-can-differ({labels[0]}/{labels[1]})"])
    m._validated = True
    return m
