"""Exact inference over scored bitstring fossils (fossil metabolism S2, phase 1).

A fossil on an evaluate_bitstring landscape is a pair (x, s): a candidate
bitstring x of length L and its EXACT score s = (L - d_H(x, t)) / L against
the hidden target t. So each fossil is the constraint

    d_H(x_i, t) = m_i,   m_i = L * (1 - s_i)   (must be an integer in 0..L)

THE MATHEMATICS, stated so it can be checked rather than believed.

One fossil (x, m): the feasible targets are every t at Hamming distance
exactly m from x -- C(L, m) of them. No single bit is fixed unless m = 0
(t = x) or m = L (t = complement of x).

Two fossils x1, x2 differing on the position set D (|D| = k) and agreeing on
A (|A| = L - k). Write a = mismatches of t against x1 on A (equal to its
mismatches against x2 on A, since x1 = x2 there), b1 = mismatches against x1
on D, b2 = mismatches against x2 on D. On D every t_j equals exactly one of
x1_j, x2_j, so b1 + b2 = k. Then m1 = a + b1 and m2 = a + b2, hence

    b1 = (k + m1 - m2) / 2,   b2 = k - b1,   a = m1 - b1.

The SCORE DIFFERENCE identifies b1 exactly (how many of the differing
positions the target takes from x1) and a; it does NOT say which positions.
If (k + m1 - m2) is odd, or b1 is outside 0..k, or a outside 0..L-k, the
fossils are CONTRADICTORY. Bits are fully identified on D only when b1 = 0
(t = x1 on all of D) or b1 = k (t = x2 on D); on A only when a = 0 or
a = L - k. Otherwise D and A are PARTIALLY CONSTRAINED: the count is known,
the positions are not. Feasible targets: C(k, b1) * C(L - k, a).

N fossils, generally. Partition the positions into BLOCKS by the column
pattern p = (x_1j, ..., x_Nj) in {0,1}^N. Inside a block of size n_B every
position looks the same to every fossil, so only u_B = number of positions
in B where t_j = 1 matters. Mismatches of t against fossil i are

    m_i = sum over blocks B of ( n_B - u_B  if p_B[i] = 1  else  u_B ).

This is an integer linear system in the u_B with 0 <= u_B <= n_B. Every
solution vector u corresponds to prod_B C(n_B, u_B) targets. The feasible
set is the union over solutions; its size is the sum of those products.
A block is FIXED (all bits known) when every solution has u_B = 0 (all zeros)
or u_B = n_B (all ones); it is COUNT-KNOWN when every solution has the same
u_B strictly between 0 and n_B; otherwise it is AMBIGUOUS. Per position, the
uniform-prior probability P(t_j = 1) inside block B is
sum_u w(u) * u_B / n_B  /  sum_u w(u), with w(u) = prod C(n_B, u_B).

Everything here is exact combinatorics: no heuristic is ever labelled
determined. `enumerate_targets` is the brute-force baseline for small L and
the tests require the block solver to agree with it.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from math import comb
from typing import Dict, List, Optional, Sequence, Tuple


class Contradiction(ValueError):
    """The fossils admit no target (a tampered or misattributed score)."""


@dataclass(frozen=True)
class Fossil:
    bits: str
    score: float

    @property
    def length(self) -> int:
        return len(self.bits)

    def mismatches(self) -> int:
        """m = L(1 - s), exact; a non-integer m is a contradiction in itself."""
        m = self.length * (1.0 - self.score)
        r = round(m)
        if abs(m - r) > 1e-9 or r < 0 or r > self.length:
            raise Contradiction("score {} on length {} is not an integer Hamming distance".format(self.score, self.length))
        return int(r)


@dataclass
class Block:
    pattern: Tuple[int, ...]          # the column of fossil bits at these positions
    positions: Tuple[int, ...]


@dataclass
class Inference:
    length: int
    n_fossils: int
    blocks: List[Block]
    solutions: List[Tuple[int, ...]]                  # feasible u vectors, one per block
    weights: List[int]                                # targets per solution
    feasible_targets: int
    fixed_bits: Dict[int, int]                        # position -> bit, for FIXED blocks
    count_known_blocks: List[Dict]                    # blocks with a single u strictly inside
    ambiguous_blocks: List[Dict]
    p_one: Dict[int, float]                           # uniform-prior P(t_j = 1) per position
    order_key: Tuple = field(default_factory=tuple)   # canonical fossil set, order-free

    @property
    def n_fixed(self) -> int:
        return len(self.fixed_bits)

    def status(self) -> str:
        if self.feasible_targets == 1:
            return "FULLY_IDENTIFIED"
        if self.fixed_bits:
            return "PARTIALLY_IDENTIFIED"
        if self.count_known_blocks:
            return "COUNT_CONSTRAINED_ONLY"
        return "AMBIGUOUS"


def _validate(fossils: Sequence[Fossil]) -> int:
    if not fossils:
        raise ValueError("no fossils")
    L = fossils[0].length
    if any(f.length != L for f in fossils):
        raise ValueError("fossils of different lengths cannot share a target")
    if any(c not in "01" for f in fossils for c in f.bits):
        raise ValueError("bits must be 0/1")
    return L


def blocks_of(fossils: Sequence[Fossil]) -> List[Block]:
    """Positions grouped by their column pattern across the fossils (order of
    fossils fixed by the caller; the block STRUCTURE is order-invariant up to
    relabelling, which `infer` normalises by sorting fossils first)."""
    L = _validate(fossils)
    groups: Dict[Tuple[int, ...], List[int]] = {}
    for j in range(L):
        pat = tuple(int(f.bits[j]) for f in fossils)
        groups.setdefault(pat, []).append(j)
    return [Block(pat, tuple(pos)) for pat, pos in sorted(groups.items())]


def infer(fossils: Sequence[Fossil]) -> Inference:
    """The exact feasible set of targets, by blocks. Raises Contradiction when
    empty. Fossils are canonicalised (deduplicated, sorted) first, so the
    result cannot depend on insertion order."""
    canon = sorted(set(fossils), key=lambda f: (f.bits, f.score))
    L = _validate(canon)
    ms = [f.mismatches() for f in canon]
    blocks = blocks_of(canon)
    sols: List[Tuple[int, ...]] = []
    weights: List[int] = []
    # Depth-first over blocks with exact bound pruning: after choosing u for the
    # first k blocks, fossil i's mismatch count so far must leave a deficit that
    # the remaining blocks can still supply (each remaining block B contributes
    # between 0 and n_B mismatches to every fossil). Exhaustive and exact; the
    # itertools.product form (S2) was exponential in the block count.
    N = len(ms); K = len(blocks); sizes = [len(b.positions) for b in blocks]
    suffix = [0] * (K + 1)
    for k in range(K - 1, -1, -1):
        suffix[k] = suffix[k + 1] + sizes[k]
    def dfs(k: int, partial: List[int], u: List[int], w: int):
        if k == K:
            if all(partial[i] == ms[i] for i in range(N)):
                sols.append(tuple(u)); weights.append(w)
            return
        n = sizes[k]; pat = blocks[k].pattern
        for ub in range(n + 1):
            ok = True
            for i in range(N):
                add = (n - ub) if pat[i] == 1 else ub
                deficit = ms[i] - (partial[i] + add)
                if deficit < 0 or deficit > suffix[k + 1]:
                    ok = False; break
            if not ok:
                continue
            for i in range(N):
                partial[i] += (n - ub) if pat[i] == 1 else ub
            u.append(ub)
            dfs(k + 1, partial, u, w * comb(n, ub))
            u.pop()
            for i in range(N):
                partial[i] -= (n - ub) if pat[i] == 1 else ub
    dfs(0, [0] * N, [], 1)
    if not sols:
        raise Contradiction("no target satisfies all {} fossils (mismatch counts {})".format(len(canon), ms))
    total = sum(weights)
    fixed: Dict[int, int] = {}
    count_known: List[Dict] = []
    ambiguous: List[Dict] = []
    p_one: Dict[int, float] = {}
    for bi, b in enumerate(blocks):
        n = len(b.positions)
        us = {s[bi] for s in sols}
        exp_u = sum(w * s[bi] for w, s in zip(weights, sols)) / total
        for j in b.positions:
            p_one[j] = exp_u / n
        if us == {0}:
            for j in b.positions:
                fixed[j] = 0
        elif us == {n}:
            for j in b.positions:
                fixed[j] = 1
        elif len(us) == 1:
            count_known.append({"positions": list(b.positions), "ones": next(iter(us)), "size": n})
        else:
            ambiguous.append({"positions": list(b.positions), "ones_possible": sorted(us), "size": n})
    return Inference(length=L, n_fossils=len(canon), blocks=blocks, solutions=sols, weights=weights,
                     feasible_targets=total, fixed_bits=fixed, count_known_blocks=count_known,
                     ambiguous_blocks=ambiguous, p_one=p_one, order_key=tuple((f.bits, f.score) for f in canon))


def enumerate_targets(fossils: Sequence[Fossil]) -> List[str]:
    """Brute force over all 2^L targets (baseline; small L only)."""
    L = _validate(fossils)
    if L > 20:
        raise ValueError("enumeration baseline is for L <= 20")
    ms = [f.mismatches() for f in fossils]
    out = []
    for n in range(2 ** L):
        t = format(n, "0{}b".format(L))
        if all(sum(a != b for a, b in zip(t, f.bits)) == m for f, m in zip(fossils, ms)):
            out.append(t)
    return out


def two_fossil_closed_form(f1: Fossil, f2: Fossil) -> Dict[str, object]:
    """The closed form in the docstring, for checking the block solver."""
    L = _validate([f1, f2]); m1, m2 = f1.mismatches(), f2.mismatches()
    D = [j for j in range(L) if f1.bits[j] != f2.bits[j]]; k = len(D)
    num = k + m1 - m2
    if num % 2 or not (0 <= num // 2 <= k) or not (0 <= m1 - num // 2 <= L - k):
        return {"consistent": False, "k": k, "reason": "b1 = (k + m1 - m2)/2 is not an integer in 0..k, or a is out of range"}
    b1 = num // 2; a = m1 - b1
    return {"consistent": True, "k": k, "b1": b1, "b2": k - b1, "a": a,
            "feasible_targets": comb(k, b1) * comb(L - k, a),
            "D_fixed": b1 in (0, k), "A_fixed": a in (0, L - k)}


def posterior_mode(inf: Inference, tie_break: Optional[str] = None) -> str:
    """The bitstring maximising the expected score under a UNIFORM prior over
    the feasible set: bit j = 1 iff P(t_j = 1) > 1/2; ties (exactly 1/2) take
    the tie_break string's bit, else 0. This is exact given the feasible set;
    it is a decision rule, not a claim that the mode is the target."""
    out = []
    for j in range(inf.length):
        p = inf.p_one[j]
        if abs(p - 0.5) < 1e-12:
            out.append(tie_break[j] if tie_break else "0")
        else:
            out.append("1" if p > 0.5 else "0")
    return "".join(out)


def expected_score(inf: Inference, candidate: str) -> float:
    """Exact expected score of `candidate` under the uniform prior over the
    feasible set: mean over positions of P(t_j = candidate_j)."""
    return sum((inf.p_one[j] if candidate[j] == "1" else 1.0 - inf.p_one[j]) for j in range(inf.length)) / inf.length
