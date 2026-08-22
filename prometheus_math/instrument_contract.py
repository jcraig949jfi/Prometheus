"""INSTRUMENT CONTRACT — no instrument is admissible until it kills a constructed anti-case.

Four cycles running, an instrument shipped blind in the direction it was pointed:

    029  the constancy probe read an all-raising probe space as constancy
    032  a convergence claim rested on a chain that could not have falsified it
    033  the monotonicity classifier ordered unordered values and returned UNIVERSAL
    034  the "raw syntax" control turned out to normalise six ways

Three were found by accident. The fourth was caught before the measurement only because the habit
was applied deliberately — and a habit is not a mechanism. External review (round 10) supplied
the mechanism, and it is stricter than "test it against an honest case":

> **No instrument is admissible until it has killed a deliberately constructed anti-case.**

Every instrument must ship four things, and the certification refuses to run without them:

    POSITIVE     a case that MUST trigger the claimed signal
    NEGATIVE     the answer-you-do-not-want case, built so the instrument must refuse,
                 report zero, or flip class
    INVALID      malformed or out-of-domain input that must produce NEITHER — only an error
                 or an explicit UNSETTLED
    SENSITIVITY  a pair (x, x') differing ONLY in the property the instrument claims to
                 measure, with M(x) != M(x')

The sensitivity witness is the measurement analogue of an aliasing witness. Without one, the
instrument has never demonstrated it is sensitive to its advertised target at all — it may be
responding to something correlated with it on the cases tried.

**What this does not do, stated up front because the contract deserves its own anti-case.** An
instrument that special-cases the four fixtures and returns garbage everywhere else passes
cleanly. That is fixture memorisation — canon R0's lookup-table trap one level up — and the
defence is the same: fixtures must be GENERATED per run rather than fixed, so that passing
requires the behaviour rather than the answers. `certify` therefore accepts fixture FACTORIES,
and `memorisation_is_still_possible` demonstrates the hole for anyone tempted to trust a clean
report on frozen fixtures.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Sequence, Tuple

__all__ = ["InstrumentContract", "CertificationReport", "certify", "ContractError",
           "memorisation_is_still_possible"]


class ContractError(ValueError):
    """Raised when an instrument is submitted without the fixtures the contract requires."""


@dataclass(frozen=True)
class InstrumentContract:
    """The four fixtures. Factories, not values, so a run can draw fresh ones.

    `positive` / `negative` / `invalid` each return an input for the instrument.
    `sensitivity` returns a pair differing only in the measured property.
    `accepts` classifies a returned verdict as signal / no-signal / neither.
    """

    name: str
    positive: Callable[[], Any]
    negative: Callable[[], Any]
    invalid: Callable[[], Any]
    sensitivity: Callable[[], Tuple[Any, Any]]
    is_signal: Callable[[Any], bool]
    is_no_signal: Callable[[Any], bool]

    def __post_init__(self) -> None:
        missing = [f for f in ("positive", "negative", "invalid", "sensitivity")
                   if getattr(self, f) is None]
        if missing:
            raise ContractError(
                f"{self.name!r} submitted without {missing}. An instrument with no anti-case has "
                "not been tested against the answer you do not want, which is the only failure "
                "mode that has actually bitten this loop")


@dataclass(frozen=True)
class CertificationReport:
    """Per-fixture outcome. `admissible` requires all four."""

    name: str
    positive_ok: bool
    negative_ok: bool
    invalid_ok: bool
    sensitive: bool
    notes: Tuple[str, ...] = ()

    @property
    def admissible(self) -> bool:
        return all((self.positive_ok, self.negative_ok, self.invalid_ok, self.sensitive))

    @property
    def failures(self) -> Tuple[str, ...]:
        out = []
        if not self.positive_ok:
            out.append("POSITIVE: did not trigger on a case that must")
        if not self.negative_ok:
            out.append("NEGATIVE: did not refuse the answer-you-do-not-want case")
        if not self.invalid_ok:
            out.append("INVALID: returned a verdict on out-of-domain input")
        if not self.sensitive:
            out.append("SENSITIVITY: no pair differing only in the measured property separates")
        return tuple(out)

    def report(self) -> str:  # pragma: no cover - reporting only
        state = "ADMISSIBLE" if self.admissible else "REFUSED: " + "; ".join(self.failures)
        return f"{self.name}: {state}"


def certify(instrument: Callable[[Any], Any], contract: InstrumentContract,
            draws: int = 1) -> CertificationReport:
    """Run the contract. `draws > 1` re-draws every fixture, which is what defeats memorisation
    when the factories are genuinely generative."""
    pos_ok = neg_ok = inv_ok = sens = True
    notes: list = []

    for _ in range(max(1, draws)):
        try:
            v = instrument(contract.positive())
            if not contract.is_signal(v):
                pos_ok = False
        except Exception as exc:
            pos_ok = False
            notes.append(f"positive raised {type(exc).__name__}")

        try:
            v = instrument(contract.negative())
            if not contract.is_no_signal(v):
                neg_ok = False
        except Exception as exc:
            neg_ok = False
            notes.append(f"negative raised {type(exc).__name__}")

        try:
            v = instrument(contract.invalid())
            if contract.is_signal(v) or contract.is_no_signal(v):
                inv_ok = False          # must be NEITHER — an error or an explicit UNSETTLED
        except Exception:
            pass                        # raising is a legitimate way to report out-of-domain

        try:
            a, b = contract.sensitivity()
            if instrument(a) == instrument(b):
                sens = False
        except Exception as exc:
            sens = False
            notes.append(f"sensitivity raised {type(exc).__name__}")

    return CertificationReport(contract.name, pos_ok, neg_ok, inv_ok, sens, tuple(notes))


def memorisation_is_still_possible(contract: InstrumentContract) -> bool:
    """THE CONTRACT'S OWN ANTI-CASE, because it would be absurd not to build one.

    An instrument that recognises the four fixtures and returns whatever each one needs — while
    being wholly blind elsewhere — passes cleanly. Demonstrated rather than asserted: this builds
    exactly that instrument and certifies it.

    So the contract is NECESSARY and NOT SUFFICIENT. What closes the hole is generative fixture
    factories plus `draws > 1`, which is canon R0's fresh-seed rule applied one level up. A clean
    report on FROZEN fixtures means only that the instrument handled those four inputs.
    """
    pos, neg, inv = contract.positive(), contract.negative(), contract.invalid()
    a, b = contract.sensitivity()

    def memoriser(x: Any) -> Any:
        if x == pos:
            return "SIGNAL"
        if x == neg:
            return "NO_SIGNAL"
        if x == a:
            return "SIGNAL"
        if x == b:
            return "NO_SIGNAL"
        if x == inv:
            raise ValueError("out of domain")
        return "SIGNAL"                 # blind everywhere else, and confidently so

    frozen = InstrumentContract(
        name=contract.name + "/frozen",
        positive=lambda: pos, negative=lambda: neg, invalid=lambda: inv,
        sensitivity=lambda: (a, b),
        is_signal=lambda v: v == "SIGNAL",
        is_no_signal=lambda v: v == "NO_SIGNAL",
    )
    return certify(memoriser, frozen).admissible
