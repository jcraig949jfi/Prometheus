"""Fossil metabolism S5 -- the deeper reference policy.

S5 asks whether the STATE of the evidence predicts where one-step G is
myopic. That needs a producer that is not myopic at any horizon on the
worlds where the question is posed. O is that producer:

    O  optimal identification, PEW_CONSUMING: the exact adaptive policy
       minimising the expected number of further probes until the feasible
       set is a single target (uniform prior over the feasible set), by
       dynamic programming over the reachable feasible subsets with every
       probe in {0,1}^L as a candidate at every node. It is exact and
       therefore only defined on small worlds: the feasible set is
       enumerated explicitly and the DP is refused (outcome SCOPE_EXCEEDED,
       probe None) above `max_targets` feasible targets or above
       `max_length` bits. Under the S5 work budget every (subset, probe)
       evaluation is one unit; exhaustion returns BUDGET_EXHAUSTED exactly
       as for G, W and M (archaeon.producer.work_budget).

DECLARED SEMANTICS (recorded so the compute accounting can be read):
  * probes inducing the same set-partition of the current feasible subset
    are equivalent for every continuation; one representative (the
    smallest bitstring) is evaluated per class. This changes nothing about
    the optimum; it is an exactness-preserving reduction.
  * the DP value of a feasible SUBSET depends only on that subset, never on
    the fossils that produced it, so values are memoised per process across
    calls (`_MEMO`, keyed by L and the subset). A memo hit is reported in
    the ancestry (`memo_hits`, `fresh_subsets`) and costs no work units:
    the compute accounting of a season must sum FRESH work, and the tests
    show a memo hit returns the identical probe. `clear_memo()` resets it.
  * ties at the root (several probes with the same minimal expected cost,
    to 1e-12) form the tie class; the smallest bitstring is emitted.

Nothing here can receive the hidden target: the signature is (fossils,
seed_inputs, budget/scope limits) and the tests assert it, as in S4.
"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import fossil_inference as FI
from .s4_producers import Proposal, snapshot_id
from .work_budget import BudgetExhausted, WorkBudget, charge as _charge

PRODUCER_VERSION = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16]
DEFAULT_MAX_UNITS = 50_000_000
DEFAULT_MAX_TARGETS = 64
DEFAULT_MAX_LENGTH = 12

_MEMO: Dict[Tuple[int, bytes], Tuple[float, int]] = {}
_DIST: Dict[int, np.ndarray] = {}


def clear_memo() -> None:
    _MEMO.clear()


def _dist_matrix(L: int) -> np.ndarray:
    D = _DIST.get(L)
    if D is None:
        n = 1 << L
        xs = np.arange(n, dtype=np.int64)
        X = ((xs[:, None] >> np.arange(L)) & 1).astype(np.uint8)
        D = np.zeros((n, n), dtype=np.uint8)
        for j in range(L):
            D += (X[:, j][:, None] != X[:, j][None, :])
        _DIST[L] = D
    return D


def _as_int(bits: str) -> int:
    """bit j of the string is position j (the S4 convention); integer bit j = position j."""
    return int(bits[::-1], 2)


def _as_bits(x: int, L: int) -> str:
    return format(x, "0{}b".format(L))[::-1]


def _dp(L: int, D: np.ndarray, S: np.ndarray, stats: Dict[str, int]) -> Tuple[float, int]:
    """(expected further probes, best probe) for feasible subset S (ints, sorted). Exact."""
    if len(S) == 1:
        return 0.0, -1
    key = (L, S.tobytes())
    hit = _MEMO.get(key)
    if hit is not None:
        stats["memo_hits"] += 1
        return hit
    stats["fresh_subsets"] += 1
    M = D[:, S]                                                    # 2^L x |S| distances
    counts = np.stack([(M == e).sum(1) for e in range(L + 1)], axis=1)
    er = (counts.astype(np.int64) ** 2).sum(1)
    lab = M.astype(np.int64)
    first = np.zeros_like(lab)
    for i in range(lab.shape[0]):
        _, inv = np.unique(lab[i], return_inverse=True)
        first[i] = inv
    _, reps = np.unique(first, axis=0, return_index=True)
    order = [int(q) for q in reps if counts[q].max() != len(S)]
    order.sort(key=lambda q: (int(er[q]), q))
    best: Tuple[Optional[float], int] = (None, -1)
    n = len(S)
    for q in order:
        _charge(1, "dp_subset_probe")
        c = 1.0
        for e in range(L + 1):
            if counts[q, e] > 1:
                c += (counts[q, e] / n) * _dp(L, D, S[M[q] == e], stats)[0]
                if best[0] is not None and c >= best[0] - 1e-12:
                    break
        if best[0] is None or c < best[0] - 1e-12:
            best = (c, q)
    _MEMO[key] = (best[0], best[1])
    return best[0], best[1]


def _root_ties(L: int, D: np.ndarray, S: np.ndarray, value: float, stats: Dict[str, int]) -> List[int]:
    """Every probe whose expected cost at the root equals the optimum (exact continuation values from the memo)."""
    M = D[:, S]; n = len(S); ties = []
    for q in range(1 << L):
        row = M[q]
        if (row == row[0]).all():
            continue
        c = 1.0
        for e in np.unique(row):
            cell = S[row == e]
            if len(cell) > 1:
                c += (len(cell) / n) * _dp(L, D, cell, stats)[0]
        if abs(c - value) <= 1e-9:
            ties.append(q)
    return ties


def produce_O(fossils: Sequence[FI.Fossil], seed_inputs: Dict[str, object], max_units: int = DEFAULT_MAX_UNITS,
              max_targets: int = DEFAULT_MAX_TARGETS, max_length: int = DEFAULT_MAX_LENGTH) -> Proposal:
    t0 = time.perf_counter()
    canon = sorted({(f.bits, f.score) for f in fossils})
    ancestry = {"fossils_consumed": canon, "pool_size": None, "rank": None}
    L = fossils[0].length
    if L > max_length:
        return Proposal("O", PRODUCER_VERSION, "PEW_CONSUMING", snapshot_id(fossils), None, dict(seed_inputs), "SCOPE_EXCEEDED before a probe was chosen", None, [],
                        ancestry, time.perf_counter() - t0, {"outcome": "SCOPE_EXCEEDED", "reason": "length", "L": L, "max_length": max_length})
    st = FI.infer(fossils)                                         # raises Contradiction: fail closed, as every producer
    if st.feasible_targets > max_targets:
        ancestry["n_feasible"] = st.feasible_targets
        return Proposal("O", PRODUCER_VERSION, "PEW_CONSUMING", snapshot_id(fossils), None, dict(seed_inputs), "SCOPE_EXCEEDED before a probe was chosen", None, [],
                        ancestry, time.perf_counter() - t0, {"outcome": "SCOPE_EXCEEDED", "reason": "feasible_targets", "n_feasible": st.feasible_targets, "max_targets": max_targets})
    stats = {"memo_hits": 0, "fresh_subsets": 0}
    try:
        with WorkBudget(max_units) as b:
            D = _dist_matrix(L)
            S = np.array(sorted(_as_int(t) for t in FI.enumerate_targets(list(fossils))), dtype=np.int64)
            assert len(S) == st.feasible_targets
            value, q = _dp(L, D, S, stats)
            ties = _root_ties(L, D, S, value, stats)
            units = b.units
    except BudgetExhausted as exc:
        ancestry.update({"n_feasible": st.feasible_targets, "pool_size": 1 << L, "memo_hits": stats["memo_hits"], "fresh_subsets": stats["fresh_subsets"]})
        return Proposal("O", PRODUCER_VERSION, "PEW_CONSUMING", snapshot_id(fossils), None, dict(seed_inputs), "BUDGET_EXHAUSTED before a probe was chosen", None, [],
                        ancestry, time.perf_counter() - t0, {"outcome": "BUDGET_EXHAUSTED", "work": exc.provenance})
    probe = _as_bits(min(ties), L) if ties else _as_bits(q, L)
    ancestry.update({"n_feasible": st.feasible_targets, "pool_size": 1 << L, "rank": 0, "memo_hits": stats["memo_hits"], "fresh_subsets": stats["fresh_subsets"], "work_units": units})
    return Proposal("O", PRODUCER_VERSION, "PEW_CONSUMING", snapshot_id(fossils), probe, dict(seed_inputs),
                    "min expected further probes to identification (exact adaptive DP, uniform prior)", value, sorted(_as_bits(t, L) for t in ties),
                    ancestry, time.perf_counter() - t0, {"outcome": "OK", "expected_probes_to_identify": value})


# ---------------------------------------------------------------- GH: G with the entropy tie-break (the cheap refinement)
def produce_GH(fossils: Sequence[FI.Fossil], seed_inputs: Dict[str, object], max_units: int = 2_000_000) -> Proposal:
    """S4's G unchanged in pool and objective (min one-step ER over the fossil-centred
    pool), with ONE change: ties on the exact ER numerator are broken by the
    larger outcome entropy H(d) before the lexicographic rule. This is the
    minimal cheap consumer that acts on the S5 mechanism (the ER objective is a
    collision statistic and is indifferent between partitions whose
    identification futures differ; entropy is the identification-relevant
    refinement). Same signature, same budget contract, no target."""
    from . import acquisition as AQ
    from .s4_producers import _base
    t0 = time.perf_counter(); pool = None
    try:
        with WorkBudget(max_units):
            st = AQ.feasible(fossils)
            import random
            rng = random.Random(repr(sorted(seed_inputs.items())) + ":G")          # G's pool exactly (same seed suffix)
            pool = AQ.probe_pool(st, fossils, rng, n_random=32)
            vals = []
            for q in pool:
                _charge(1, "probe_scored"); vals.append(AQ.value(st, q))
            vals.sort(key=lambda v: (v.er_numerator, -v.outcome_entropy_bits, v.probe))
            best = vals[0]
            ties = [v.probe for v in vals if v.er_numerator == best.er_numerator and abs(v.outcome_entropy_bits - best.outcome_entropy_bits) < 1e-12]
    except BudgetExhausted as exc:
        from .s4_producers import exhausted
        return exhausted("GH", "PEW_CONSUMING", fossils, seed_inputs, t0, exc, len(pool) if pool else None)
    p = _base("GH", "PEW_CONSUMING", fossils, best.probe, dict(seed_inputs), "min expected remaining feasible targets (one step, uniform prior); ties by max outcome entropy", best.expected_remaining, ties,
              {"fossils_consumed": sorted({(f.bits, f.score) for f in fossils}), "pool_size": len(pool), "rank": 0, "n_feasible": st.feasible_targets}, t0,
              {"partition": best.partition, "expected_score": best.expected_score, "entropy_bits": best.outcome_entropy_bits})
    p.producer_version = PRODUCER_VERSION
    return p
