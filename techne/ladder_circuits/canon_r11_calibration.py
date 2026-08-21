"""CANON R11 — meta-reasoning / calibrated uncertainty. (Canon v2.0 §3.)

Canon: *"Kill: claims with long misleading streaks (n²+n+41's 40-term run of primes). Math:
report {solved / probable / under-constrained} and be right about it (Brier-scored). Artifact:
calibration state vs. ground truth."*

**The aliasing analysis came first this cycle, and it changed the design.** Applying cycle 018's
instrument before building anything produced a result I did not expect:

- At the FORECASTER level, aliasing is not a defect to repair — it is the environment the rung
  exists for. A claim that fails at n = 40 and a claim that never fails are identical to anyone
  who has checked n ≤ 39. No better projection is available from inside the situation, so the
  correct response to the witness is not a sharper instrument, it is **honest uncertainty**.
  Every prior rung treated an aliasing witness as something to design away. R11 is where you
  cannot, and calibration is what you do instead.

- At the SCORER level, R11 supplies the **first genuine counterexample to claim v11'**. Empirical
  calibration on a fixed record is *definitionally* a function of that record, so no two records
  can be aliased with respect to it — the scorer sees everything the target depends on. The
  aliasing returns the moment the target becomes calibration on the NEXT battery, which is what
  anyone actually wants. Both halves are measured in the test suite, on one constructed pair.

Circuits:
- ReferenceClassForecaster — the honest one. Checks a budget, reports 0.0 with a witness when it
  finds a counterexample, and otherwise reports the base rate of its declared reference class,
  fitted on a CALIBRATION battery it is then scored away from.
- OverconfidentAsserter (trap 1) — 0.99 on anything it has not personally refuted.
- HedgingForecaster (trap 2) — always the base rate. Perfect reliability, zero resolution, and
  it beats the honest circuit on ECE. The reason reliability is never the verdict.
- BatteryTunedForecaster (trap 3) — memorises outcomes by claim name. Brier 0, ECE 0, skill 1:
  a flawless scoreboard with no forecasting in it. Killed without needing name randomisation,
  because it issues refutations of claims whose counterexamples lie past its own search budget
  and cannot say where they fail.
- SelectiveReporter (trap 4) — honest forecasts, but silently drops the claims it got wrong.
  MEASURED: it improves Brier 0.125 -> 0.0375 and skill 0.500 -> 0.844 while its reliability
  DEGRADES (0.0 -> 0.0375), so a proper scoring rule rewards it and a reliability check happens
  to notice. That second half is a property of this particular drop rule, not a defence. The
  guaranteed catch is completeness, which is not a function of the published record at all.
- MimicForecaster — not a trap; the constructed half of the aliasing pair.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from prometheus_math.calibration import (
    MurphyPartition, brier_score, expected_calibration_error, murphy_decomposition,
)

#: How many terms a forecaster is allowed to check before it must commit.
DEFAULT_BUDGET = 10


@dataclass(frozen=True)
class Claim:
    """A universally quantified claim, its truth, and where it first fails (None if true)."""

    name: str
    truth: bool
    first_failure: Optional[int] = None

    def holds_at(self, n: int) -> bool:
        return self.first_failure is None or n != self.first_failure

    def survives(self, budget: int) -> bool:
        """Does the claim look true to someone who has checked n = 0..budget?"""
        return self.first_failure is None or self.first_failure > budget


def late_failure(k: int, tag: str = "") -> Claim:
    """A misleading streak of length k: holds for every n < k, fails at exactly k."""
    return Claim(f"fails_at_{k}{tag}", truth=False, first_failure=k)


def always_true(i: int, tag: str = "") -> Claim:
    return Claim(f"true_{i}{tag}", truth=True)


#: The battery the forecasters FIT their reference class on.
CALIBRATION_BATTERY: Tuple[Claim, ...] = (
    tuple(always_true(i, "_cal") for i in range(6))
    + tuple(late_failure(k, "_cal") for k in (2, 4, 6, 8))     # detectable within budget 10
    + (late_failure(15, "_cal"), late_failure(20, "_cal"))     # misleading streaks past it
)

#: The battery they are SCORED on. Same mix, disjoint claims — so a forecaster with a genuine
#: reference class transfers and one that memorised does not.
BATTERY: Tuple[Claim, ...] = (
    tuple(always_true(i, "_test") for i in range(6))
    + tuple(late_failure(k, "_test") for k in (3, 5, 7, 9))
    + (late_failure(14, "_test"), late_failure(19, "_test"))
)

#: A battery with a DIFFERENT mix — more misleading streaks past the budget. A reference class
#: fitted on CALIBRATION_BATTERY is wrong here, which is the honest limit of the honest circuit.
SHIFTED_BATTERY: Tuple[Claim, ...] = (
    tuple(always_true(i, "_shift") for i in range(2))
    + tuple(late_failure(k, "_shift") for k in (12, 13, 14, 16, 17, 18))
)


@dataclass(frozen=True)
class Assessment:
    """One forecast, and the artifact canon asks for: calibration state vs. ground truth."""

    claim: str
    confidence: float
    outcome: int                       # 1 if the claim is true
    state: str                         # "solved" | "probable" | "under-constrained" | "refuted"
    witness: Optional[str] = None      # required for a "refuted" state

    @property
    def is_supported(self) -> bool:
        """Evidence typing (claim v12): a REFUTED state asserts a counterexample exists, so it
        needs one. The other states assert only a degree of belief and carry no such debt."""
        return self.state != "refuted" or self.witness is not None


def classify(confidence: float) -> str:
    """The canon's three-way report, plus the refuted state that carries a witness."""
    if confidence <= 0.0:
        return "refuted"
    if confidence >= 0.95:
        return "solved"
    if confidence >= 0.5:
        return "probable"
    return "under-constrained"


def forecasts_and_outcomes(assessments: Sequence[Assessment]) -> Tuple[List[float], List[int]]:
    return [a.confidence for a in assessments], [a.outcome for a in assessments]


def reference_class_prior(battery: Sequence[Claim], budget: int = DEFAULT_BUDGET) -> float:
    """Among claims that SURVIVE `budget` checks, what fraction are true?

    This is the whole content of being calibrated here: not a feeling about a claim, but a
    measured base rate over a declared reference class. On CALIBRATION_BATTERY at budget 10 it
    is 6 true / (6 true + 2 surviving false) = 0.75.
    """
    survivors = [c for c in battery if c.survives(budget)]
    if not survivors:
        return 0.0
    return sum(1 for c in survivors if c.truth) / len(survivors)


def base_rate(battery: Sequence[Claim]) -> float:
    return sum(1 for c in battery if c.truth) / len(battery) if battery else 0.0


class Forecaster:
    """Common machinery: check the budget, then defer to `confidence_for`."""

    budget: int = DEFAULT_BUDGET

    def counterexample(self, claim: Claim) -> Optional[int]:
        for n in range(self.budget + 1):
            if not claim.holds_at(n):
                return n
        return None

    def confidence_for(self, claim: Claim) -> float:      # pragma: no cover - abstract
        raise NotImplementedError

    def assess(self, claim: Claim) -> Assessment:
        n = self.counterexample(claim)
        if n is not None:
            return Assessment(claim.name, 0.0, int(claim.truth), "refuted",
                              witness=f"{claim.name} fails at n = {n}")
        p = self.confidence_for(claim)
        return Assessment(claim.name, p, int(claim.truth), classify(p))

    def assess_all(self, battery: Sequence[Claim]) -> List[Assessment]:
        return [self.assess(c) for c in battery]


@dataclass
class ReferenceClassForecaster(Forecaster):
    """THE HONEST CIRCUIT. Its confidence on an unrefuted claim is the measured base rate of the
    reference class it declares, fitted on a battery it is not scored on."""

    prior: float = field(default_factory=lambda: reference_class_prior(CALIBRATION_BATTERY))
    budget: int = DEFAULT_BUDGET

    def confidence_for(self, claim: Claim) -> float:
        return self.prior


@dataclass
class OverconfidentAsserter(Forecaster):
    """TRAP 1: 0.99 on anything it has not personally refuted. Every misleading streak past the
    budget becomes a confident error."""

    budget: int = DEFAULT_BUDGET

    def confidence_for(self, claim: Claim) -> float:
        return 0.99


@dataclass
class HedgingForecaster(Forecaster):
    """TRAP 2: reports the battery's base rate on EVERY claim, refuted or not — so it never
    even uses its budget. Perfect reliability, zero resolution, and it beats the honest circuit
    on ECE. The reason canon R11 says Brier-scored and not calibration-scored."""

    rate: Optional[float] = None
    budget: int = DEFAULT_BUDGET

    def assess(self, claim: Claim) -> Assessment:
        p = self.rate if self.rate is not None else base_rate(BATTERY)
        return Assessment(claim.name, p, int(claim.truth), classify(p))

    def confidence_for(self, claim: Claim) -> float:       # pragma: no cover - unused
        return self.rate if self.rate is not None else base_rate(BATTERY)


@dataclass
class BatteryTunedForecaster(Forecaster):
    """TRAP 3: a lookup table from claim NAME to outcome. Brier 0, ECE 0, skill 1 — a flawless
    scoreboard with no forecasting in it. Dies the moment the names are randomised."""

    table: Dict[str, bool] = field(
        default_factory=lambda: {c.name: c.truth for c in BATTERY})
    budget: int = DEFAULT_BUDGET

    def assess(self, claim: Claim) -> Assessment:
        if claim.name in self.table:
            p = 1.0 if self.table[claim.name] else 0.0
            state = classify(p)
            return Assessment(claim.name, p, int(claim.truth), state,
                              witness="memorised" if state == "refuted" else None)
        return super().assess(claim)

    def confidence_for(self, claim: Claim) -> float:
        return 0.5                                          # nothing memorised: no opinion


@dataclass
class SelectiveReporter(Forecaster):
    """TRAP 4, and the one that motivates a constitution rather than a metric.

    It forecasts exactly as the honest circuit does, and then declines to report the claims it
    got wrong. The evidence it publishes is not falsified — it is incomplete, and **completeness
    is not a property any function of the record can see**, because the record does not contain
    what is absent from it.

    Measured on BATTERY: Brier 0.125 -> 0.0375, skill 0.500 -> 0.844, reliability 0.0 -> 0.0375.
    So the proper scoring rule rewards the omission, and reliability incidentally degrades —
    an artefact of dropping only confident-and-wrong claims, which leaves the survivor set
    systematically under-forecast. Do not read that as a defence.
    """

    inner: ReferenceClassForecaster = field(default_factory=ReferenceClassForecaster)
    threshold: float = 0.5
    budget: int = DEFAULT_BUDGET

    def confidence_for(self, claim: Claim) -> float:
        return self.inner.confidence_for(claim)

    def assess_all(self, battery: Sequence[Claim]) -> List[Assessment]:
        kept = []
        for c in battery:
            a = self.inner.assess(c)
            embarrassing = (a.confidence >= self.threshold) != bool(a.outcome)
            if not embarrassing:
                kept.append(a)
        return kept


@dataclass
class MimicForecaster(Forecaster):
    """Not a trap — the constructed half of the aliasing pair.

    Replays another forecaster's answers on a nominated battery and reports a fixed default
    everywhere else. On that battery its record is IDENTICAL to the one it mimics; off it, the
    two diverge. That is the pair the scorer-level aliasing analysis needs.
    """

    replay: Dict[str, Assessment] = field(default_factory=dict)
    default: float = 0.5
    budget: int = DEFAULT_BUDGET

    @classmethod
    def of(cls, target: Forecaster, battery: Sequence[Claim],
           default: float = 0.5) -> "MimicForecaster":
        return cls(replay={a.claim: a for a in target.assess_all(battery)}, default=default)

    def assess(self, claim: Claim) -> Assessment:
        if claim.name in self.replay:
            return dataclasses.replace(self.replay[claim.name])
        return Assessment(claim.name, self.default, int(claim.truth), classify(self.default))

    def confidence_for(self, claim: Claim) -> float:        # pragma: no cover - unused
        return self.default


# --------------------------------------------------------------------------------------------
# Scoring

def score(assessments: Sequence[Assessment], expected: int) -> Dict[str, float]:
    """Brier + Murphy + ECE, and the two things a scoreboard cannot supply for itself.

    `completeness` is the fraction of the battery actually reported on. It is NOT computable
    from the record — it needs `expected`, which must come from outside — and that is precisely
    the point of trap 4.
    """
    ps, ys = forecasts_and_outcomes(assessments)
    m = murphy_decomposition(ps, ys)
    return {
        "brier": m.brier,
        "reliability": m.reliability,
        "resolution": m.resolution,
        "skill": m.skill,
        "ece": expected_calibration_error(ps, ys),
        "completeness": len(assessments) / expected if expected else 0.0,
        "unsupported": float(sum(1 for a in assessments if not a.is_supported)),
    }


def audit_report(assessments: Sequence[Assessment], declared: Sequence[Claim]) -> Dict[str, object]:
    """EXTERNAL AUDIT (claim v12), against a PRE-DECLARED claim ledger rather than the record.

    Cycle 019 established that a check reading the circuit's own output is reading the
    attacker's testimony. Here that is sharper than at R10: the missing information is not a
    mislabelled field but an absence, and no function of the published record can recover it.
    The auditor must hold an independent list of what was asked.
    """
    reported = {a.claim for a in assessments}
    missing = [c.name for c in declared if c.name not in reported]
    return {
        "complete": not missing,
        "missing": tuple(missing),
        "unsupported": tuple(a.claim for a in assessments if not a.is_supported),
    }


def verify_refutations(assessments: Sequence[Assessment],
                       declared: Sequence[Claim]) -> Tuple[str, ...]:
    """Check that every REFUTED state carries a witness that actually witnesses.

    Evidence typing (claim v12) applied at R11: "refuted" asserts a counterexample exists, so
    the witness must name an n at which the claim genuinely fails, and an external check must be
    able to re-run it. A forecaster whose refutations come from a lookup table has the right
    verdict and the wrong evidence, and this is what notices.
    """
    by_name = {c.name: c for c in declared}
    bad = []
    for a in assessments:
        if a.state != "refuted":
            continue
        claim = by_name.get(a.claim)
        if claim is None or a.witness is None:
            bad.append(a.claim)
            continue
        try:
            n = int(a.witness.rsplit("=", 1)[1])
        except (IndexError, ValueError):
            bad.append(a.claim)                     # not of the form "... fails at n = k"
            continue
        if claim.holds_at(n):                       # re-run it: does it actually fail there?
            bad.append(a.claim)
    return tuple(bad)
