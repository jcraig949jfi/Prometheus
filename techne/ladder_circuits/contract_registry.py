"""CONTRACT REGISTRY — every instrument in the arsenal, certified or refused. (Cycle 037.)

Cycle 036 built the contract; this points it at everything already shipped. Fixtures are
FACTORIES with per-call randomness and certification runs with `draws > 1`, because cycle 036
demonstrated that frozen fixtures let a pure memoriser pass.

**Refusals are the point.** An instrument that cannot produce one of the four fixtures has told
us something about itself, and the response is to record it — never to weaken the contract until
it passes.
"""
from __future__ import annotations

import random
from typing import Callable, Dict, List, Tuple

from prometheus_math.instrument_contract import (
    CertificationReport, InstrumentContract, certify,
)

__all__ = ["build_registry", "certify_all", "REGISTRY_NOTES"]

_R = random.Random(20260821)


# `structural_constancy` reads its target's SOURCE, so its fixtures must be module-level
# functions with retrievable source. A lambda built inside an expression — or any function
# defined in an exec'd string — hits the instrument's conservative "cannot analyse" path and
# reports UNSETTLED. That is honest behaviour, and it is also a real REACH LIMIT: the instrument
# is unusable wherever source is unavailable. Cycle 037 found this by certifying it.

def _ignores_its_argument(n):
    return True


def _reads_its_argument(n):
    return n > 2


def _always_raises(n):
    raise ValueError("out of domain")


def _blocks(labels):
    out: Dict[object, list] = {}
    for i, lab in enumerate(labels):
        out.setdefault(lab, []).append(i)
    return tuple(frozenset(v) for v in out.values())


# --------------------------------------------------------------------------------------------
# One contract per instrument. `is_signal` = "the thing this instrument claims to detect".

def build_registry() -> List[Tuple[str, Callable, InstrumentContract]]:
    from prometheus_math.battery import (
        PARAMETER_INDEPENDENT, member_resolution, structural_constancy,
    )
    from prometheus_math.calibration import brier_score, murphy_decomposition
    from prometheus_math.partition import (
        chain_direction, conditional_entropy, refinement_multiplicity,
    )
    from prometheus_math.relative_claim import AGGREGATE, Domain, probe_monotonicity
    from techne.ladder_circuits.aliasing import find_aliasing_witness, fiber_search
    from techne.ladder_circuits.preprocessing_audit import python_ast_key
    from techne.ladder_circuits.stage_taxonomy import INCOMPARABLE, partition_motion

    reg: List[Tuple[str, Callable, InstrumentContract]] = []

    # 1. structural_constancy — detects a member that CANNOT fire
    reg.append((
        "battery.structural_constancy",
        lambda spec: structural_constancy("m", spec[0], spec[1]).status,
        InstrumentContract(
            "structural_constancy",
            positive=lambda: (_ignores_its_argument, list(range(_R.randrange(4, 9)))),
            negative=lambda: (_reads_its_argument, list(range(_R.randrange(5, 10)))),
            invalid=lambda: (_always_raises, list(range(_R.randrange(4, 9)))),
            sensitivity=lambda: ((_ignores_its_argument, [1, 2, 3]),
                                 (_reads_its_argument, [1, 2, 3])),
            is_signal=lambda v: v == PARAMETER_INDEPENDENT,
            is_no_signal=lambda v: v == "VARIES",
        )))

    # 2. member_resolution — detects a member that discriminates
    reg.append((
        "battery.member_resolution",
        lambda col: member_resolution({"m": col})["m"],
        InstrumentContract(
            "member_resolution",
            positive=lambda: [_R.choice([True, False]) for _ in range(8)] + [True, False],
            negative=lambda: [True] * _R.randrange(4, 9),
            invalid=lambda: [],
            sensitivity=lambda: ([True, False, True, False], [True, True, True, True]),
            is_signal=lambda v: isinstance(v, float) and v > 1e-9,
            is_no_signal=lambda v: isinstance(v, float) and v <= 1e-9,
        )))

    # 3. refinement_multiplicity — detects worst-case fragmentation
    def _mult(spec):
        proj, truth, n = spec
        return refinement_multiplicity(proj, truth, n)

    def _shattered():
        k = _R.randrange(3, 6)
        return (tuple(frozenset([i]) for i in range(k)), (frozenset(range(k)),), k)

    reg.append((
        "partition.refinement_multiplicity", _mult,
        InstrumentContract(
            "refinement_multiplicity",
            positive=_shattered,
            negative=lambda: ((frozenset(range(4)),), (frozenset(range(4)),), 4),
            invalid=lambda: ((frozenset([0, 1]), frozenset([1, 2])), (frozenset(range(3)),), 3),
            sensitivity=lambda: ((tuple(frozenset([i]) for i in range(4)),
                                  (frozenset(range(4)),), 4),
                                 ((frozenset(range(4)),), (frozenset(range(4)),), 4)),
            is_signal=lambda v: isinstance(v, int) and v > 1,
            is_no_signal=lambda v: isinstance(v, int) and v == 1,
        )))

    # 4. conditional_entropy as DEFICIT — detects truth-relevant information loss
    def _deficit(spec):
        truth, proj, n = spec
        return conditional_entropy(truth, proj, n)

    reg.append((
        "partition.deficit", _deficit,
        InstrumentContract(
            "deficit",
            positive=lambda: (_blocks([0, 1, 0, 1]), (frozenset(range(4)),), 4),
            negative=lambda: (_blocks([0, 1, 0, 1]), _blocks([0, 1, 0, 1]), 4),
            invalid=lambda: (_blocks([0, 1]), (frozenset([0, 1, 2]),), 2),
            sensitivity=lambda: ((_blocks([0, 1, 0, 1]), (frozenset(range(4)),), 4),
                                 (_blocks([0, 1, 0, 1]), _blocks([0, 1, 0, 1]), 4)),
            is_signal=lambda v: isinstance(v, float) and v > 1e-9,
            is_no_signal=lambda v: isinstance(v, float) and abs(v) <= 1e-9,
        )))

    # 5. chain_direction — detects an ACCUMULATING chain
    def _dir(spec):
        chain, n = spec
        return chain_direction(chain, n)

    fine4 = tuple(frozenset([i]) for i in range(4))
    pairs4 = _blocks([0, 0, 1, 1])
    whole4 = (frozenset(range(4)),)
    reg.append((
        "partition.chain_direction", _dir,
        InstrumentContract(
            "chain_direction",
            positive=lambda: ([whole4, pairs4, fine4], 4),
            negative=lambda: ([fine4, pairs4, whole4], 4),
            invalid=lambda: ([pairs4, _blocks([0, 1, 0, 1])], 4),
            sensitivity=lambda: (([whole4, pairs4, fine4], 4), ([fine4, pairs4, whole4], 4)),
            is_signal=lambda v: v == "ACCUMULATING",
            is_no_signal=lambda v: v == "DESTROYING",
        )))

    # 6. probe_monotonicity — detects a NON-monotone (AGGREGATE) claim
    ch = [Domain(f"d{k}", tuple(range(m))) for k, m in enumerate((2, 4, 6, 8))]
    reg.append((
        "relative_claim.probe_monotonicity",
        lambda f: probe_monotonicity(f, ch),
        InstrumentContract(
            "probe_monotonicity",
            positive=lambda: (lambda d: len(d) % 3),
            negative=lambda: (lambda d: len(d)),
            invalid=lambda: (lambda d: (min(d.members), max(d.members))),
            sensitivity=lambda: ((lambda d: len(d) % 3), (lambda d: len(d))),
            is_signal=lambda v: v == AGGREGATE,
            is_no_signal=lambda v: v in ("EXISTENTIAL", "UNIVERSAL", "INVARIANT"),
        )))

    # 7. brier_score — detects a poorly-scoring forecaster
    reg.append((
        "calibration.brier_score",
        lambda spec: brier_score(spec[0], spec[1]),
        InstrumentContract(
            "brier_score",
            positive=lambda: ([0.0] * 4, [1] * 4),
            negative=lambda: ([1.0] * 4, [1] * 4),
            invalid=lambda: ([], []),
            # a pair differing ONLY in calibration, holding resolution fixed
            sensitivity=lambda: (([0.5, 0.5, 0.5, 0.5], [1, 1, 0, 0]),
                                 ([0.9, 0.9, 0.1, 0.1], [1, 1, 0, 0])),
            is_signal=lambda v: isinstance(v, float) and v > 0.25,
            is_no_signal=lambda v: isinstance(v, float) and v <= 0.25,
        )))

    # 8. murphy_decomposition reliability — detects MIScalibration specifically
    reg.append((
        "calibration.murphy_reliability",
        lambda spec: murphy_decomposition(spec[0], spec[1]).reliability,
        InstrumentContract(
            "murphy_reliability",
            positive=lambda: ([0.9, 0.9, 0.9, 0.9], [1, 0, 0, 0]),
            negative=lambda: ([0.5, 0.5, 0.5, 0.5], [1, 1, 0, 0]),
            invalid=lambda: ([], []),
            sensitivity=lambda: (([0.9, 0.9, 0.9, 0.9], [1, 0, 0, 0]),
                                 ([0.25, 0.25, 0.25, 0.25], [1, 0, 0, 0])),
            is_signal=lambda v: isinstance(v, float) and v > 1e-9,
            is_no_signal=lambda v: isinstance(v, float) and abs(v) <= 1e-9,
        )))

    # 9. find_aliasing_witness — detects an aliased pair
    reg.append((
        "aliasing.find_aliasing_witness",
        lambda spec: find_aliasing_witness(spec[0], spec[1], spec[2]),
        InstrumentContract(
            "find_aliasing_witness",
            positive=lambda: ([1, 3], (lambda n: n % 2), (lambda n: n > 2)),
            negative=lambda: ([1, 2, 3], (lambda n: n), (lambda n: n > 2)),
            invalid=lambda: ([1], (lambda n: n % 2), (lambda n: n > 2)),
            sensitivity=lambda: (([1, 3], (lambda n: n % 2), (lambda n: n > 2)),
                                 ([1, 3], (lambda n: n), (lambda n: n > 2))),
            is_signal=lambda v: v is not None,
            is_no_signal=lambda v: v is None,
        )))

    # 10. fiber_search — synthesises an aliasing witness
    reg.append((
        "aliasing.fiber_search",
        lambda spec: fiber_search(spec[0], spec[1], spec[2], spec[3]),
        InstrumentContract(
            "fiber_search",
            positive=lambda: (1, (lambda s: [3, 5, 7]), (lambda n: n % 2), (lambda n: n > 4)),
            negative=lambda: (1, (lambda s: [3, 5]), (lambda n: n % 2), (lambda n: True)),
            invalid=lambda: (1, (lambda s: []), (lambda n: n % 2), (lambda n: n > 4)),
            sensitivity=lambda: ((1, (lambda s: [3, 5, 7]), (lambda n: n % 2),
                                  (lambda n: n > 4)),
                                 (1, (lambda s: [3, 5, 7]), (lambda n: n % 2),
                                  (lambda n: True))),
            is_signal=lambda v: v is not None,
            is_no_signal=lambda v: v is None,
        )))

    # 11. partition_motion — detects INCOMPARABLE motion
    reg.append((
        "stage_taxonomy.partition_motion",
        lambda spec: partition_motion(spec[0], spec[1], spec[2]),
        InstrumentContract(
            "partition_motion",
            positive=lambda: (_blocks([0, 0, 1, 1]), _blocks([0, 1, 0, 1]), 4),
            negative=lambda: (fine4, whole4, 4),
            invalid=lambda: ((frozenset([0, 1]), frozenset([1, 2])), whole4, 3),
            sensitivity=lambda: ((_blocks([0, 0, 1, 1]), _blocks([0, 1, 0, 1]), 4),
                                 (_blocks([0, 0, 1, 1]), whole4, 4)),
            is_signal=lambda v: v == INCOMPARABLE,
            is_no_signal=lambda v: v in ("COARSENING", "REFINEMENT", "PRESERVING"),
        )))

    # 12. python_ast_key — detects lexical equivalence
    reg.append((
        "preprocessing_audit.python_ast_key",
        lambda pair: python_ast_key(pair[0]) == python_ast_key(pair[1]),
        InstrumentContract(
            "python_ast_key",
            positive=lambda: ("(x)+y", "x  +  y"),
            negative=lambda: ("x+y", "x+z"),
            invalid=lambda: ("x +", "y"),
            sensitivity=lambda: (("(x)+y", "x+y"), ("x+y", "x+z")),
            is_signal=lambda v: v is True,
            is_no_signal=lambda v: v is False,
        )))

    return reg


def certify_all(draws: int = 4) -> List[Tuple[str, CertificationReport]]:
    return [(name, certify(fn, contract, draws=draws)) for name, fn, contract in build_registry()]


#: Filled in by cycle 037 after the first run — see the cycle doc for the discussion.
REGISTRY_NOTES: Dict[str, str] = {}
