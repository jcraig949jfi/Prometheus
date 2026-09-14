"""Fossil metabolism S3 -- information-seeking probe selection (exact).

The world is the evaluate_bitstring landscape: hidden target t in {0,1}^L,
a probe q returns the EXACT score s = (L - d_H(q, t)) / L. Given fossils E
the feasible set is T(E) = { t : d_H(x_i, t) = m_i for every (x_i, s_i) }
(archaeon.producer.fossil_inference gives it as weighted block solutions).

A probe's possible outcomes d = d_H(q, t) PARTITION T(E): n_d = number of
feasible targets at distance d from q. Observing the outcome leaves exactly
the cell the true target sits in.

PRIMARY ACQUISITION OBJECTIVE (chosen before any production result was
looked at, S3 phase 1):

    ER(q | E) = expected remaining feasible targets after observing q
             = sum_d (n_d / N) * n_d  =  sum_d n_d^2 / N,     N = |T(E)|

ASSUMPTION, named: the expectation is under a UNIFORM prior over T(E). It
is an assumption of indifference among targets the evidence cannot tell
apart, not a fact about the landscape generator. Lower ER is better; the
best conceivable probe has n_d in {0, 1} (ER = 1); a probe whose outcome
is the same for every feasible target has ER = N (it teaches nothing).
Reported beside it, never used to choose: worst-case remaining max_d n_d,
expected eliminated N - ER, and the outcome entropy.

TIE SEMANTICS: two probes with equal ER (exact integers over a common
denominator) are TIED and reported as one equivalence class; a
deterministic tie-break (lexicographically smallest bitstring) is applied
only to name a single row to emit, and the class is recorded beside it.
Probes inducing the same partition have the same ER by construction.

EXACT COMPUTATION without enumeration. In block B (pattern p, size n_B)
the target has u_B ones among n_B positions, placed uniformly across the
C(n_B, u_B) placements of a given block solution. If q has q1_B ones in B,
the number j of target-ones landing on q-ones is hypergeometric
(n_B, q1_B, u_B) and the block's mismatch count is u_B + q1_B - 2j. The
total distance is the sum over blocks; its distribution is the convolution
of the per-block hypergeometric mismatch distributions, weighted by the
block solution's placement count. `outcome_partition` does exactly that;
`brute_partition` enumerates targets for small L and the tests require
agreement.

The selector never sees the hidden target: the only inputs are fossils
(bits, score) and candidate probes. A cheating selector is provided in the
tests to show what reading the target would look like, and the legitimate
functions are asserted never to receive it.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from math import comb
from typing import Dict, List, Optional, Sequence, Tuple

from . import fossil_inference as FI
from .work_budget import charge as _charge


@dataclass
class ProbeValue:
    probe: str
    expected_remaining: float          # ER, exact rational as float (n_d^2 sums / N)
    er_numerator: int                  # sum n_d^2 (exact integer)
    n_feasible: int                    # N
    worst_case_remaining: int          # max_d n_d
    expected_eliminated: float         # N - ER
    outcome_entropy_bits: float        # H(d) under the uniform prior
    partition: Dict[int, int]          # distance -> n_d
    expected_score: float              # immediate task quality under the same prior
    n_outcomes: int


def feasible(fossils: Sequence[FI.Fossil]) -> FI.Inference:
    """The evidence state. Raises FI.Contradiction: an inconsistent set has no
    feasible targets and no probe may be chosen from it (fail closed)."""
    return FI.infer(fossils)


def _block_mismatch_dist(n: int, q1: int, u: int) -> Dict[int, int]:
    """Number of placements (out of C(n,u)) giving each mismatch count in one
    block: j target-ones on q-ones ~ hypergeometric; mismatches = u + q1 - 2j."""
    out: Dict[int, int] = {}
    for j in range(max(0, u - (n - q1)), min(q1, u) + 1):
        ways = comb(q1, j) * comb(n - q1, u - j)
        if ways:
            m = u + q1 - 2 * j
            out[m] = out.get(m, 0) + ways
    return out


def outcome_partition(state: FI.Inference, q: str) -> Dict[int, int]:
    """n_d for every distance d: how many feasible targets sit at Hamming
    distance d from q. Exact; sums to state.feasible_targets."""
    if len(q) != state.length or any(c not in "01" for c in q):
        raise ValueError("probe must be a 0/1 string of the landscape length")
    total: Dict[int, int] = {}
    for sol in state.solutions:
        dist: Dict[int, int] = {0: 1}
        _charge(len(state.blocks), "partition_solution_blocks")
        for b, u in zip(state.blocks, sol):
            n = len(b.positions); q1 = sum(1 for j in b.positions if q[j] == "1")
            bd = _block_mismatch_dist(n, q1, u)
            nxt: Dict[int, int] = {}
            for d0, w0 in dist.items():
                for m, w in bd.items():
                    nxt[d0 + m] = nxt.get(d0 + m, 0) + w0 * w
            dist = nxt
        for d, w in dist.items():
            total[d] = total.get(d, 0) + w
    assert sum(total.values()) == state.feasible_targets
    return total


def value(state: FI.Inference, q: str) -> ProbeValue:
    part = outcome_partition(state, q)
    N = state.feasible_targets
    num = sum(n * n for n in part.values())
    ent = -sum((n / N) * math.log2(n / N) for n in part.values() if n)
    L = state.length
    es = sum(((L - d) / L) * n for d, n in part.items()) / N
    return ProbeValue(probe=q, expected_remaining=num / N, er_numerator=num, n_feasible=N, worst_case_remaining=max(part.values()),
                      expected_eliminated=N - num / N, outcome_entropy_bits=ent, partition=dict(sorted(part.items())), expected_score=es, n_outcomes=len(part))


def brute_partition(fossils: Sequence[FI.Fossil], q: str) -> Dict[int, int]:
    """Enumeration baseline (small L)."""
    out: Dict[int, int] = {}
    for t in FI.enumerate_targets(fossils):
        d = sum(a != b for a, b in zip(q, t)); out[d] = out.get(d, 0) + 1
    return dict(sorted(out.items()))


def _flip(x: str, j: int) -> str:
    return x[:j] + ("1" if x[j] == "0" else "0") + x[j + 1:]


def probe_pool(state: FI.Inference, fossils: Sequence[FI.Fossil], rng: random.Random, n_random: int = 32, max_pool: int = 512) -> List[str]:
    """The scalable candidate set the selector scores (all of 2^L is not
    admissible above small L): every fossil, its complement, every single-bit
    flip of every fossil, the posterior mode and its single-bit flips, and
    n_random uniform probes. Deterministic given rng. Nothing here is a
    preference: every member is scored by ER alone."""
    L = state.length
    pool: List[str] = []
    seen = set()
    def add(x):
        if x not in seen:
            seen.add(x); pool.append(x)
    best = max(fossils, key=lambda f: (f.score, f.bits))
    mode = FI.posterior_mode(state, tie_break=best.bits)
    add(mode)
    for f in sorted(set(fossils), key=lambda f: f.bits):
        add(f.bits); add("".join("1" if c == "0" else "0" for c in f.bits))
        for j in range(L):
            add(_flip(f.bits, j))
    for j in range(L):
        add(_flip(mode, j))
    for _ in range(n_random):
        add("".join(rng.choice("01") for _ in range(L)))
    return pool[:max_pool]


@dataclass
class Selection:
    probe: str
    value: ProbeValue
    tie_class: List[str]               # every pool member with the same exact ER
    ranked: List[ProbeValue]           # the whole pool, best first (ER, then probe)


def select(state: FI.Inference, pool: Sequence[str]) -> Selection:
    """Minimum expected remaining feasible targets; ties reported as a class,
    named by the lexicographically smallest probe."""
    vals = []
    for q in pool:
        _charge(1, "probe_scored")
        vals.append(value(state, q))
    vals.sort(key=lambda v: (v.er_numerator, v.probe))
    best = vals[0]
    ties = [v.probe for v in vals if v.er_numerator == best.er_numerator]
    return Selection(probe=best.probe, value=best, tie_class=ties, ranked=vals)


def optimum_by_enumeration(fossils: Sequence[FI.Fossil]) -> Tuple[int, List[str]]:
    """Oracle: over ALL 2^L probes (small L), the minimum sum n_d^2 and the
    full equivalence class attaining it."""
    L = fossils[0].length
    if L > 12:
        raise ValueError("oracle is for L <= 12")
    state = feasible(fossils)
    best = None; cls: List[str] = []
    for n in range(2 ** L):
        q = format(n, "0{}b".format(L)); num = sum(v * v for v in outcome_partition(state, q).values())
        if best is None or num < best:
            best, cls = num, [q]
        elif num == best:
            cls.append(q)
    return best, cls


def uniform_probe(L: int, rng: random.Random) -> str:
    return "".join(rng.choice("01") for _ in range(L))


def hamming(a: str, b: str) -> int:
    return sum(x != y for x, y in zip(a, b))
