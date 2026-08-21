"""REAL SUBSTRATE III — a falsification battery is a chain running the OTHER WAY. (Cycle 027.)

**READ-ONLY audit of `prometheus_math.discovery_pipeline`.** No pipeline code modified.

## Target chosen first, stage type verified before measuring

Cycle 025's failure was choosing the instrument before the target. So, in order:

1. **Target:** the discovery pipeline's kill-path battery — F1 (permutation null), F6 (base
   rate), F9 (simpler explanation), F11 (cross-validation) — run over polynomial candidates.
2. **Stage type:** each check is a FILTER. Filtering partitions the candidate set into survivors
   and killed, which is an inter-record operation, so cycle 026's scope statement says the
   partition instruments should apply.
3. **And then a direction check, which is where it got interesting.**

## The finding — the chain accumulates instead of destroying

Cycle 024 built the profile for a TRANSFORM pipeline, where stage k+1 sees only stage k's output.
Such a chain coarsens: `chain[k]` refines `chain[k+1]`, deficit rises, excess falls.

A falsification battery does the opposite. Each check ADDS a verdict bit to a running record and
none is discarded, so the state after k checks REFINES the state after k−1. Consequences,
measured below:

- `is_refinement_chain` returns **False** on a perfectly healthy battery, because the chain runs
  in the reverse direction. Read naively that says *"this is not a pipeline"*, and it is one.
- deficit against the terminal verdict **decreases** to zero; excess **increases**. Cycle 024's
  `ChainReport.deficit_monotone` flags a healthy battery as broken.

So the instruments are not blind here, as they were on the rewrite stages in cycle 025 — they
are **inverted**. That is a third stage-type category, and it is the one most likely to produce a
confidently wrong reading rather than an empty one.

    transform / rewrite   content changes, records stay distinct   instruments BLIND
    select / reorder      records chosen and ordered               instruments WORK   (cycle 026)
    filter / accumulate   verdict bits added, nothing discarded    instruments INVERTED

## Second finding — two of the four checks are constant on this battery

F9 and F11 return True for every candidate measured. In the sweep's vocabulary they carry zero
resolution: they cannot separate any pair, so they contribute no bits to the terminal verdict.
That is canon R11's hedging forecaster appearing inside a real falsification battery — a member
that never fires is indistinguishable from a member that is not there, and both are perfectly
"sound".

Reported, not judged: a check that never fires on the candidates it has seen may still be the one
that catches the next thing. What is worth knowing is that the battery's discriminating power on
this evidence comes entirely from F1 and F6.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import sympy as sp

from prometheus_math.discovery_pipeline import (
    _f1_permutation_null, _f6_base_rate, _f9_simpler_explanation, _f11_cross_validation,
)
from prometheus_math.partition import (
    conditional_entropy, entropy, induced_partition, is_refinement_chain,
)

__all__ = ["CHECKS", "real_candidates", "verdict_chain", "BatteryChainReport",
           "analyse_battery_chain", "check_resolution"]

x = sp.Symbol("x")

#: The battery, in the order `process_candidate` evaluates it.
CHECKS: Tuple[Tuple[str, Callable[[List[int], float], Tuple[bool, str]]], ...] = (
    ("F1", _f1_permutation_null),
    ("F6", _f6_base_rate),
    ("F9", lambda coeffs, m: _f9_simpler_explanation(coeffs)),
    ("F11", _f11_cross_validation),
)


def real_candidates() -> List[Tuple[Tuple[int, ...], float]]:
    """Reciprocal integer polynomials with Mahler measures computed at high precision.

    Palindromic by construction (the band the pipeline searches is reciprocal), small
    coefficients, plus Lehmer's polynomial itself. These are real objects with real measures,
    not fixtures — `mahler_measure_high_precision` is doing the work.
    """
    from prometheus_math._lehmer_brute_force_path_b import mahler_measure_high_precision as MM

    out: List[Tuple[Tuple[int, ...], float]] = []
    for mid in itertools.product([-1, 0, 1], repeat=3):
        coeffs = [1] + list(mid) + [1]
        try:
            out.append((tuple(coeffs), MM(sp.Poly(coeffs, x))))
        except Exception:
            continue
    for mid in itertools.product([-1, 0, 1], repeat=2):
        coeffs = [1] + list(mid) + list(mid)[::-1] + [1]
        try:
            out.append((tuple(coeffs), MM(sp.Poly(coeffs, x))))
        except Exception:
            continue
    out.append(((1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1), 1.176281))   # Lehmer
    return out


def verdict_chain(coeffs: Sequence[int], m: float) -> List[Tuple[Optional[bool], ...]]:
    """The running state after each check: a growing tuple of verdict bits.

    This is the pipeline's own shape — `process_candidate` evaluates every check and collects
    the results into one `check_results` dict before routing. Nothing is discarded, so the state
    only ever gains information.
    """
    states: List[Tuple[Optional[bool], ...]] = [()]
    acc: List[Optional[bool]] = []
    for _name, fn in CHECKS:
        try:
            acc.append(bool(fn(list(coeffs), m)[0]))
        except Exception:
            acc.append(None)
        states.append(tuple(acc))
    return states


@dataclass
class BatteryChainReport:
    """Profile of an ACCUMULATING chain, plus the direction diagnosis."""

    n_candidates: int
    deficits: List[float]
    excesses: List[float]
    terminal_entropy: float
    forward_is_refinement_chain: bool
    reversed_is_refinement_chain: bool
    stage_names: Tuple[str, ...]

    @property
    def deficit_decreases(self) -> bool:
        return all(self.deficits[k] >= self.deficits[k + 1] - 1e-12
                   for k in range(len(self.deficits) - 1))

    @property
    def matches_cycle024_assumption(self) -> bool:
        """Cycle 024 asserts deficit is non-DECREASING. A battery violates that by design."""
        return all(self.deficits[k] <= self.deficits[k + 1] + 1e-12
                   for k in range(len(self.deficits) - 1))

    @property
    def direction(self) -> str:
        if self.reversed_is_refinement_chain and not self.forward_is_refinement_chain:
            return "ACCUMULATING — refines forward; cycle-024 monotonicity runs backwards"
        if self.forward_is_refinement_chain:
            return "DESTROYING — coarsens forward; cycle-024 monotonicity applies"
        return "NEITHER — stages are incomparable; no chain argument available"


def analyse_battery_chain(candidates: Optional[Sequence[Tuple[Sequence[int], float]]] = None
                          ) -> BatteryChainReport:
    """Measure the battery as a chain, against its own terminal verdict."""
    cands = list(candidates if candidates is not None else real_candidates())
    n = len(cands)
    chains = [verdict_chain(c, m) for c, m in cands]
    depth = len(chains[0])

    stages = [induced_partition(list(range(n)), lambda i, k=k: chains[i][k])
              for k in range(depth)]
    terminal = induced_partition(list(range(n)), lambda i: chains[i][-1])

    return BatteryChainReport(
        n_candidates=n,
        deficits=[conditional_entropy(terminal, p, n) for p in stages],
        excesses=[conditional_entropy(p, terminal, n) for p in stages],
        terminal_entropy=entropy(terminal, n),
        forward_is_refinement_chain=is_refinement_chain(stages, n),
        reversed_is_refinement_chain=is_refinement_chain(list(reversed(stages)), n),
        stage_names=tuple(name for name, _fn in CHECKS),
    )


def check_resolution(candidates: Optional[Sequence[Tuple[Sequence[int], float]]] = None
                     ) -> Dict[str, float]:
    """Bits each check contributes on its own — its resolution over the candidate set.

    A check that returns the same verdict for every candidate contributes 0.000 bits. That is
    canon R11's hedger inside a falsification battery: a member that never fires is
    observationally identical to a member that is absent.
    """
    cands = list(candidates if candidates is not None else real_candidates())
    n = len(cands)
    out: Dict[str, float] = {}
    for name, fn in CHECKS:
        def verdict(i: int, fn=fn) -> Optional[bool]:
            try:
                return bool(fn(list(cands[i][0]), cands[i][1])[0])
            except Exception:
                return None
        out[name] = entropy(induced_partition(list(range(n)), verdict), n)
    return out
