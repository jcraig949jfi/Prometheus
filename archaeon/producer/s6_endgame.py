"""Fossil metabolism S6 -- the endgame: what G's one-step score discards, and cheap deterministic refinements.

G scores a probe q at evidence state s by ER(q) = sum_d n_d^2 / N, the expected number of feasible targets left
after observing q's outcome. That is a COLLISION statistic of the outcome partition {n_d}: many partitions share it.
S6 asks what identification-relevant information the compression to ER throws away, and whether a cheap
deterministic refinement of G's choice recovers a useful part of the exact optimum's advantage.

This module holds three things, kept apart on purpose:

  PARTITION STATISTICS (target-free, cheap): the outcome partition of a probe on the current feasible set and
  small summaries of it -- entropy, singleton mass, number of cells, largest cell, the sorted shape, and the
  one-step-ahead count value V2 (the expected best ER after the outcome; the most expensive cheap statistic).

  THE SEALED ORACLE: exact full-horizon values V*(s) and Q*(s, q) from the S5 DP (archaeon.producer.s5_producers),
  with its own work ledger. It is used ONLY by the evaluator and by the deliberately labelled positive control;
  no candidate takes it as input (tests assert the signatures), and its work is accounted separately
  (one-time oracle work vs amortised memo hits) so that O's cost never reads zero again (S5 accounting gap).

  CANDIDATE REFINEMENTS OF G: G's own pool, G's own objective, G's own seed; the refinement acts only inside an
  admissible window around G's best ER (window 0 = exact ties) and picks, deterministically, the member that
  maximises one partition statistic (ties by the lexicographic rule G already uses). Outside the window nothing
  changes; when the window holds one probe the refinement is inactive by construction. Work is charged per probe
  scored and per statistic evaluated.

The blind control is the EXACT uniform-random policy value R(s) (a DP averaging over every probe), not one seeded
draw: S5 run 2 showed a single fixed blind sequence can tie the optimum in a tiny symmetric state by chance.
"""
from __future__ import annotations

import hashlib
import math
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import acquisition as AQ
from . import fossil_inference as FI
from . import s5_producers as O5
from .s4_producers import Proposal, _base, exhausted
from .work_budget import BudgetExhausted, WorkBudget, charge as _charge

PRODUCER_VERSION = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16]
STATISTICS = ("entropy", "singleton_mass", "n_cells", "neg_max_cell", "shape", "v2", "v2w", "lb2")


# ------------------------------------------------------------------ partitions and statistics (target-free)
def feasible_ints(fossils: Sequence[FI.Fossil]) -> np.ndarray:
    return np.array(sorted(O5._as_int(t) for t in FI.enumerate_targets(list(fossils))), dtype=np.int64)


def partition_cells(L: int, S: np.ndarray, q_int: int) -> Tuple[int, ...]:
    """Sorted (descending) cell sizes of the outcome partition of probe q on feasible set S."""
    row = O5._dist_matrix(L)[q_int, S]
    _, counts = np.unique(row, return_counts=True)
    return tuple(sorted((int(c) for c in counts), reverse=True))


def er_num(cells: Sequence[int]) -> int:
    return sum(c * c for c in cells)


def entropy_bits(cells: Sequence[int]) -> float:
    N = sum(cells)
    return -sum((c / N) * math.log2(c / N) for c in cells if c)


def v2_num(L: int, S: np.ndarray, q_int: int, cache: Dict[bytes, int]) -> int:
    """One-step-ahead count value, exact: sum over outcome cells of min_q' sum n^2 within the cell (numerator over N).
    A cell of size 1 contributes 1 (nothing left to split)."""
    D = O5._dist_matrix(L); row = D[q_int, S]; tot = 0
    for e in np.unique(row):
        cell = S[row == e]
        if len(cell) == 1:
            tot += 1; continue
        k = cell.tobytes(); v = cache.get(k)
        if v is None:
            M = D[:, cell]; counts = np.stack([(M == d).sum(1) for d in range(L + 1)], axis=1)
            _charge(1 << L, "v2_cell_probes")
            v = int((counts.astype(np.int64) ** 2).sum(1).min()); cache[k] = v
        tot += v
    return tot


def lb2_num(L: int, S: np.ndarray, q_int: int, cache: Dict[bytes, float]) -> float:
    """Two-level PROBE-UNIT lower bound on the cost of probing q first (exact, cheap):
        LB2(q) = sum_e (n_e / N) * lb(cell_e),   lb(cell) = 0 if |cell| = 1,
        else 1 + min_{q'} sum_{e'} (n_e' / |cell|) * [n_e' >= 2]
    i.e. every non-singleton cell costs at least one more probe, and after the best next probe every cell still
    of size >= 2 costs at least one more. A cell that some probe SHATTERS into singletons costs exactly 1. This is
    the quantity ER discards: ER counts targets, cost counts probes. Lower is better; returned as-is (the caller
    negates it for the higher-is-preferred convention)."""
    D = O5._dist_matrix(L); row = D[q_int, S]; tot = 0.0; N = len(S)
    for e in np.unique(row):
        cell = S[row == e]; n = len(cell)
        if n == 1:
            continue
        k = cell.tobytes(); v = cache.get(k)
        if v is None:
            M = D[:, cell]
            best = None
            for qq in range(1 << L):
                _charge(1, "lb2_cell_probe")
                r2 = M[qq]; _, cnt = np.unique(r2, return_counts=True)
                m = float(cnt[cnt >= 2].sum()) / n
                if best is None or m < best:
                    best = m
                    if best == 0.0:
                        break
            v = 1.0 + best; cache[k] = v
        tot += (n / N) * v
    return tot


def v2w_num(L: int, S: np.ndarray, q_int: int, cache: Dict[bytes, int]) -> float:
    """Cell-weighted next-step collision: sum_e (n_e/N) * min_q' sum n'^2 over the cell, singletons contributing 0.
    (Found by accident in the first characterization pass through a cache collision between v2 and lb2 -- recorded as
    its own statistic because it was the one actually measured there; it weights each cell's best next-step ER by
    the probability of landing in it and gives a resolved cell nothing.)"""
    D = O5._dist_matrix(L); row = D[q_int, S]; tot = 0.0; N = len(S)
    for e in np.unique(row):
        cell = S[row == e]; n = len(cell)
        if n == 1:
            continue
        k = cell.tobytes(); v = cache.get(k)
        if v is None:
            M = D[:, cell]; counts = np.stack([(M == d).sum(1) for d in range(L + 1)], axis=1)
            _charge(1 << L, "v2_cell_probes")
            v = int((counts.astype(np.int64) ** 2).sum(1).min()); cache[k] = v
        tot += (n / N) * v
    return tot


def statistic(name: str, L: int, S: np.ndarray, q_int: int, cells: Sequence[int], caches: Dict[str, Dict]) -> object:
    """Higher is preferred. Every statistic is a function of the outcome partition (and, for v2/v2w/lb2, of the cells'
    own partitions). `caches` holds ONE dict per statistic name (they store different quantities under the same keys)."""
    _charge(1, "statistic_" + name)
    if name == "entropy":
        return entropy_bits(cells)
    if name == "singleton_mass":
        return sum(1 for c in cells if c == 1) / sum(cells)
    if name == "n_cells":
        return len(cells)
    if name == "neg_max_cell":
        return -max(cells)
    if name == "shape":
        return tuple(-c for c in cells)                    # lexicographic: prefer smaller largest cell, then smaller second, ...
    if name == "v2":
        return -v2_num(L, S, q_int, caches.setdefault("v2", {}))
    if name == "v2w":
        return -v2w_num(L, S, q_int, caches.setdefault("v2w", {}))
    if name == "lb2":
        return -lb2_num(L, S, q_int, caches.setdefault("lb2", {}))
    raise ValueError(name)


# ------------------------------------------------------------------ the sealed oracle (evaluator only)
@dataclass
class OracleLedger:
    fresh_units: int = 0          # (subset, probe) DP evaluations paid for the first time in this process
    memo_hits: int = 0
    calls: int = 0
    seconds: float = 0.0


class SealedOracle:
    """Exact V*(s) and Q*(s, q). Wraps the S5 DP with its own work ledger. Never passed to a candidate."""

    def __init__(self, L: int):
        self.L = L; self.D = O5._dist_matrix(L); self.ledger = OracleLedger()

    def _dp(self, S: np.ndarray) -> Tuple[float, int]:
        stats = {"memo_hits": 0, "fresh_subsets": 0}; t0 = time.perf_counter()
        with WorkBudget(10 ** 12) as b:
            v, q = O5._dp(self.L, self.D, S, stats)
        self.ledger.fresh_units += b.units; self.ledger.memo_hits += stats["memo_hits"]; self.ledger.calls += 1; self.ledger.seconds += time.perf_counter() - t0
        return v, q

    def V(self, S: np.ndarray) -> float:
        return self._dp(S)[0]

    def Q(self, S: np.ndarray, q_int: int) -> float:
        row = self.D[q_int, S]
        if (row == row[0]).all():
            return float("inf")                                   # uninformative: never terminates by this probe alone
        c = 1.0
        for e in np.unique(row):
            cell = S[row == e]
            if len(cell) > 1:
                c += (len(cell) / len(S)) * self.V(cell)
        return c


def random_policy_value(L: int, S: np.ndarray, memo: Dict[bytes, float]) -> float:
    """Exact expected probes-to-identification of the BLIND uniform policy (every probe in {0,1}^L equally likely at
    every step, evidence ignored). Uninformative probes are wasted steps: R = (1 + (1/2^L) sum_informative sum_e
    (n_e/N) R(cell)) / (1 - u/2^L)."""
    if len(S) == 1:
        return 0.0
    k = S.tobytes(); v = memo.get(k)
    if v is not None:
        return v
    D = O5._dist_matrix(L); M = D[:, S]; n = len(S); P = 1 << L; acc = 0.0; uninformative = 0
    for q in range(P):
        row = M[q]
        if (row == row[0]).all():
            uninformative += 1; continue
        for e in np.unique(row):
            cell = S[row == e]
            if len(cell) > 1:
                acc += (len(cell) / n) * random_policy_value(L, cell, memo)
    v = (1.0 + acc / P) / (1.0 - uninformative / P); memo[k] = v
    return v


# ------------------------------------------------------------------ candidate refinements of G
def g_pool_and_values(fossils: Sequence[FI.Fossil], seed_inputs: Dict[str, object]):
    """Exactly G's pool (same seed suffix ':G') and G's exact one-step values."""
    st = AQ.feasible(fossils)
    rng = random.Random(repr(sorted(seed_inputs.items())) + ":G")
    pool = AQ.probe_pool(st, fossils, rng, n_random=32)
    vals = []
    for q in pool:
        _charge(1, "probe_scored"); vals.append(AQ.value(st, q))
    return st, pool, vals


def produce_refined(fossils: Sequence[FI.Fossil], seed_inputs: Dict[str, object], stat: str, window: float = 0.0, max_units: int = 2_000_000) -> Proposal:
    """G with its choice refined inside the admissible window: members whose exact ER numerator is <= (1 + window) x the
    pool minimum are re-ranked by `stat` (higher preferred), ties by G's lexicographic rule. window 0 = exact ties only.
    Signature carries no target, no oracle."""
    t0 = time.perf_counter(); pool = None
    try:
        with WorkBudget(max_units):
            st, pool, vals = g_pool_and_values(fossils, seed_inputs)
            best_num = min(v.er_numerator for v in vals)
            adm = [v for v in vals if v.er_numerator <= best_num * (1.0 + window) + 1e-9]
            if len(adm) == 1:
                choice = adm[0]; ranked = [(None, choice)]
            else:
                L = st.length; S = feasible_ints(fossils); caches: Dict[str, Dict] = {}
                scored = []
                for v in adm:
                    cells = partition_cells(L, S, O5._as_int(v.probe))
                    scored.append((statistic(stat, L, S, O5._as_int(v.probe), cells, caches), v))
                scored.sort(key=lambda x: (x[1].er_numerator, tuple(-y for y in x[0]) if isinstance(x[0], tuple) else -x[0], x[1].probe))
                # order: G's objective first (exact ties only re-ranked when window == 0), then the statistic, then lex
                if window > 0:
                    scored.sort(key=lambda x: (tuple(-y for y in x[0]) if isinstance(x[0], tuple) else -x[0], x[1].er_numerator, x[1].probe))
                ranked = scored; choice = scored[0][1]
            ties = [v.probe for s_, v in ranked if s_ == ranked[0][0] and v.er_numerator == choice.er_numerator] if len(adm) > 1 else [choice.probe]
    except BudgetExhausted as exc:
        return exhausted("G+" + stat, "PEW_CONSUMING", fossils, seed_inputs, t0, exc, len(pool) if pool else None)
    p = _base("G+" + stat + ("" if window == 0 else "@%g" % window), "PEW_CONSUMING", fossils, choice.probe, dict(seed_inputs),
              "G's objective; admissible window %g re-ranked by %s" % (window, stat), choice.expected_remaining, ties,
              {"fossils_consumed": sorted({(f.bits, f.score) for f in fossils}), "pool_size": len(pool), "rank": 0, "n_feasible": st.feasible_targets, "admissible": len(adm), "active": len(adm) > 1}, t0,
              {"partition": choice.partition, "entropy_bits": choice.outcome_entropy_bits})
    p.producer_version = PRODUCER_VERSION
    return p


def produce_oracle_control(fossils: Sequence[FI.Fossil], seed_inputs: Dict[str, object], oracle: SealedOracle, window: float = 0.0, max_units: int = 2_000_000) -> Proposal:
    """POSITIVE CONTROL, NOT A CANDIDATE: G's pool and window, re-ranked by the sealed oracle's Q*. It bounds what any
    refinement confined to that window could achieve. It takes the oracle explicitly so that no candidate can be
    confused with it."""
    t0 = time.perf_counter(); pool = None
    try:
        with WorkBudget(max_units):
            st, pool, vals = g_pool_and_values(fossils, seed_inputs)
            best_num = min(v.er_numerator for v in vals)
            adm = [v for v in vals if v.er_numerator <= best_num * (1.0 + window) + 1e-9]
    except BudgetExhausted as exc:
        return exhausted("CTRL", "PEW_CONSUMING", fossils, seed_inputs, t0, exc, len(pool) if pool else None)
    S = feasible_ints(fossils)
    scored = sorted(((oracle.Q(S, O5._as_int(v.probe)), v.er_numerator, v.probe, v) for v in adm), key=lambda x: (x[0], x[1], x[2]))
    choice = scored[0][3]
    p = _base("CTRL@%g" % window, "ORACLE_ASSISTED", fossils, choice.probe, dict(seed_inputs), "positive control: window re-ranked by sealed Q*", choice.expected_remaining, [choice.probe],
              {"fossils_consumed": sorted({(f.bits, f.score) for f in fossils}), "pool_size": len(pool), "rank": 0, "n_feasible": st.feasible_targets, "admissible": len(adm), "active": len(adm) > 1}, t0, {"oracle_assisted": True})
    p.producer_version = PRODUCER_VERSION
    return p
