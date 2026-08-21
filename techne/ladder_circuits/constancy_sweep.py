"""STRUCTURAL-CONSTANCY SWEEP — cycle 029. READ-ONLY across the repo's kill batteries.

Cycle 028 found that a member which CANNOT fire and one which merely HAS NOT fired both read
0.000 bits, and that reading the source settles what more sampling cannot. This makes that
mechanical: two tiers with different logical force, and an honest middle for what neither settles.

    VARIES                 a flipping input was exhibited        — proof it CAN fire
    PARAMETER_INDEPENDENT  the body never reads its arguments    — proof it CANNOT
    UNSETTLED              reads them, nothing probed flipped it — honest

**A limitation I want stated before any result:** parameter-independence is *sufficient* for
verdict-constancy, not *necessary*. A member can read its argument for a purpose that never
reaches the verdict — `CredulousAsserter` reads the conjecture's name and then returns the same
verdict regardless — and the static tier will decline to call it constant. Those land in
UNSETTLED, correctly but unsatisfyingly. Closing that gap needs dataflow tracing from the
parameter to the returned verdict, not just a reference scan.

Batteries swept, all read-only:
  * `prometheus_math.discovery_pipeline` — the kill path (F1, F6, F9, F11) plus its
    reciprocity/irreducibility gates.
  * `prometheus_math.lehmer_brute_force` — the cyclotomic-factor and catalog-lookup checks.
  * `techne.ladder_circuits.canon_r6_falsification` — my own R6 circuits, self-audited, because
    a sweep that exempts its author is not a sweep.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Callable, Dict, List, Sequence, Tuple

import sympy as sp

from prometheus_math.battery import (
    INVALID_PROBE, PARAMETER_INDEPENDENT, UNSETTLED, VARIES, ConstancyVerdict,
    structural_constancy,
)

__all__ = ["polynomial_probes", "half_coeff_probes", "sweep_discovery_pipeline",
           "sweep_lehmer_brute_force", "sweep_r6_circuits", "sweep_all", "SweepRow"]

x = sp.Symbol("x")


def polynomial_probes(limit: int = 220) -> List[Tuple[Tuple[int, ...], float]]:
    """A deliberately HOSTILE input space, not a natural sample.

    Mutation testing wants inputs chosen to break a predicate, not inputs drawn from the
    distribution the pipeline usually sees — that was cycle 028's whole lesson. So: degenerate
    lengths, zero and huge coefficients, reciprocal and not, and Mahler values spanning far
    outside the search band including nonsense ones.
    """
    probes: List[Tuple[Tuple[int, ...], float]] = []
    shapes: List[List[int]] = [
        [], [1], [0], [1, 1], [1, -1, 1], [1, 0, 0, 0, 0, -1], [5, 3, -7, 2],
        [10 ** 6, -10 ** 6], [1, 2, 3, 4, 5, 6, 7, 8, 9], [-1, 0, 1],
        [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1],                       # Lehmer
        [1, 0, -1, 0, 1], [2, 0, 0, 1], [1, 2, 3],
    ]
    for triple in itertools.product([-2, -1, 0, 1, 2], repeat=3):
        shapes.append([1] + list(triple) + [1])
    for coeffs in shapes:
        for m in (0.0, 1.0, 1.0005, 1.05, 1.176281, 1.5, 9.6, -3.0, float("inf")):
            probes.append((tuple(coeffs), m))
            if len(probes) >= limit:
                return probes
    return probes


@dataclass(frozen=True)
class SweepRow:
    battery: str
    member: str
    status: str
    n_probed: int
    n_evaluated: int = 0

    @property
    def flag(self) -> str:
        return {VARIES: "ok", PARAMETER_INDEPENDENT: "CANNOT FIRE",
                UNSETTLED: "unsettled", INVALID_PROBE: "PROBE INVALID (my fault)"}[self.status]


def _row(battery: str, v: ConstancyVerdict) -> SweepRow:
    return SweepRow(battery, v.name, v.status, v.n_probed, v.n_evaluated)


def half_coeff_probes() -> List[Tuple[Tuple[int, ...], float]]:
    """Length-8 half-coefficient vectors — the shape `lehmer_brute_force` actually accepts.

    My first sweep passed full coefficient lists to functions that take HALF coefficients of a
    degree-14 palindrome and require exactly length 8. Every call raised, and the sweep reported
    UNSETTLED, which is how an instrument fault dresses itself as a finding about the code.
    """
    out: List[Tuple[Tuple[int, ...], float]] = []
    bases = [
        [1, 0, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1], [1, -1, 1, -1, 1, -1, 1, -1],
        [1, 1, 0, -1, -1, -1, 0, 0], [0] * 8, [2, 0, -1, 0, 1, 0, -1, 0],
        [1, 0, -1, 0, 0, 0, 1, 0], [1, 2, 3, 4, 5, 6, 7, 8],
    ]
    for triple in itertools.product([-1, 0, 1], repeat=3):
        bases.append([1] + list(triple) + [0, 0, 0, 0])
    for half in bases:
        for m in (1.0, 1.0005, 1.05, 1.176281, 1.5):
            out.append((tuple(half), m))
    return out


def sweep_discovery_pipeline() -> List[SweepRow]:
    from prometheus_math.discovery_pipeline import (
        _check_catalog_miss, _f1_permutation_null, _f6_base_rate, _f9_simpler_explanation,
        _f11_cross_validation, _is_irreducible, _is_reciprocal,
    )

    probes = polynomial_probes()
    members: List[Tuple[str, Callable, Callable]] = [
        ("F1", lambda p: _f1_permutation_null(list(p[0]), p[1])[0], _f1_permutation_null),
        ("F6", lambda p: _f6_base_rate(list(p[0]), p[1])[0], _f6_base_rate),
        ("F9", lambda p: _f9_simpler_explanation(list(p[0]))[0], _f9_simpler_explanation),
        ("F11", lambda p: _f11_cross_validation(list(p[0]), p[1])[0], _f11_cross_validation),
        ("reciprocity", lambda p: _is_reciprocal(list(p[0])), _is_reciprocal),
        ("irreducibility", lambda p: _is_irreducible(list(p[0]))[0], _is_irreducible),
        ("catalog_miss", lambda p: _check_catalog_miss(list(p[0]), p[1])[0], _check_catalog_miss),
    ]
    return [_row("discovery_pipeline",
                 structural_constancy(name, pred, probes, fn_for_source=src))
            for name, pred, src in members]


def sweep_lehmer_brute_force() -> List[SweepRow]:
    from prometheus_math.lehmer_brute_force import (
        is_reducible_to_cyclotomic_factor, lookup_in_mossinghoff_legacy,
    )

    probes = half_coeff_probes()
    members: List[Tuple[str, Callable, Callable]] = [
        ("cyclotomic_factor",
         lambda p: is_reducible_to_cyclotomic_factor(list(p[0]), p[1])[0],
         is_reducible_to_cyclotomic_factor),
        ("mossinghoff_lookup",
         lambda p: lookup_in_mossinghoff_legacy(list(p[0]), p[1])[0],
         lookup_in_mossinghoff_legacy),
    ]
    return [_row("lehmer_brute_force",
                 structural_constancy(name, pred, probes, fn_for_source=src))
            for name, pred, src in members]


def sweep_r6_circuits() -> List[SweepRow]:
    """Self-audit. A sweep that exempts its author is not a sweep."""
    from techne.ladder_circuits.canon_r6_falsification import (
        BoundedSearcher, CredulousAsserter, EagerFalsifier, euler_prime_conjecture,
        late_failure_conjecture, true_conjecture_square, true_conjecture_sum,
    )

    conjectures = [euler_prime_conjecture(), true_conjecture_sum(), true_conjecture_square(),
                   late_failure_conjecture(3), late_failure_conjecture(12),
                   late_failure_conjecture(60)]
    members = [
        ("BoundedSearcher.judge", lambda c: BoundedSearcher(horizon=100).judge(c).claimed_false,
         BoundedSearcher.judge),
        ("EagerFalsifier.judge", lambda c: EagerFalsifier(patience=3).judge(c).claimed_false,
         EagerFalsifier.judge),
        ("CredulousAsserter.judge", lambda c: CredulousAsserter().judge(c).claimed_false,
         CredulousAsserter.judge),
    ]
    return [_row("canon_r6_falsification",
                 structural_constancy(name, pred, conjectures, fn_for_source=src))
            for name, pred, src in members]


def sweep_all() -> List[SweepRow]:
    return sweep_discovery_pipeline() + sweep_lehmer_brute_force() + sweep_r6_circuits()
