"""Sprint 10 Core: Exact Binary Bilinear 3-Tensor Rank over F_2 (AlphaTensor / Strassen Domain).

Formal Substrate #5:
  - Target: A 3D binary tensor `T in F_2^{na x nb x nc}` (e.g., matrix multiplication `C = A * B`,
    polynomial multiplication, cyclic convolution, or procedural bilinear 3-tensors over F_2).
  - Solution: A bilinear rank-R decomposition `terms = [(u_r, v_r, w_r)]` (bitmasks `u_r in [1..2^na-1]`,
    `v_r in [1..2^nb-1]`, `w_r in [1..2^nc-1]`) such that:
        sum_{r=1}^{R} u_{r,i} * v_{r,j} * w_{r,k} == T_{i,j,k} (mod 2)  for ALL (i, j, k).
  - Primary Cost: Exact bilinear tensor rank `R = len(terms)` (ZERO macro discount!).
  - Exact Verifier: `verify_bilinear_decomp` computes exact tensor bitmask in O(R * wt(u)*wt(v)*wt(w)) (<0.1ms).
  - Published SOTA Baseline: `A1_FLIP_GRAPH` — Kauers & Moosbauer (2023) Flip-Graph Walk with
    exact Reduction (R -> R-1/-2), Flip (rank-preserving basis exchange on shared factor), and
    Plus (R -> R+1 escape split) transitions!
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from comp_sprint3.sandbox_s3 import CompositionalAlgoArtifact, LibModule, OpBudget
from comp_sprint6_compound.law4b_meter import run_compositional_law4b

DEFAULT_S10_V3_BUDGET = 1_800_000


@dataclass(frozen=True)
class BilinearTensorF2:
    """Exact 3D binary bilinear tensor `T in F_2^{na x nb x nc}` with an initial valid decomposition."""
    name: str
    na: int
    nb: int
    nc: int
    tensor_mask: int
    init_terms: Tuple[Tuple[int, int, int], ...]

    def base_rank(self) -> int:
        return len(self.init_terms)

    def sha256(self) -> str:
        payload = {"na": self.na, "nb": self.nb, "nc": self.nc, "mask": hex(self.tensor_mask)}
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


def _bits_of(x: int) -> List[int]:
    out: List[int] = []
    t = x
    while t:
        lb = t & -t
        out.append(lb.bit_length() - 1)
        t ^= lb
    return out


def tensor_mask_from_terms(na: int, nb: int, nc: int, terms: Sequence[Tuple[int, int, int]]) -> int:
    """Compute exact 3D binary tensor bitmask of `sum_r (u_r (x) v_r (x) w_r) mod 2`."""
    mask = 0
    for u, v, w in terms:
        if u <= 0 or v <= 0 or w <= 0:
            continue
        ub = _bits_of(u)
        vb = _bits_of(v)
        wb = _bits_of(w)
        # Pre-pack w into a nc-bit shift pattern once per term!
        for i in ub:
            base_i = i * nb
            for j in vb:
                mask ^= w << ((base_i + j) * nc)
    return mask


def verify_bilinear_decomp(target: BilinearTensorF2, terms: Sequence[Tuple[int, int, int]]) -> bool:
    """100% exact verification over all `na * nb * nc` tensor entries mod 2."""
    lim_a = 1 << target.na
    lim_b = 1 << target.nb
    lim_c = 1 << target.nc
    clean: List[Tuple[int, int, int]] = []
    for t in terms:
        if not isinstance(t, (tuple, list)) or len(t) != 3:
            return False
        u, v, w = int(t[0]), int(t[1]), int(t[2])
        if not (0 < u < lim_a and 0 < v < lim_b and 0 < w < lim_c):
            return False
        clean.append((u, v, w))
    return tensor_mask_from_terms(target.na, target.nb, target.nc, clean) == target.tensor_mask


def reduce_bilinear_terms(terms: Sequence[Tuple[int, int, int]]) -> List[Tuple[int, int, int]]:
    """Exact algebraic reduction loop: merges any pair of terms sharing 2 of 3 factors `(u,v)`, `(u,w)`, or `(v,w)`,
    canceling zero terms until fixed point (strictly preserves exact tensor mod 2!)."""
    cur = [(int(u), int(v), int(w)) for u, v, w in terms if u and v and w]
    changed = True
    while changed:
        changed = False
        # Merge on (u, v) -> xor w
        m_uv: Dict[Tuple[int, int], int] = {}
        for u, v, w in cur:
            k = (u, v)
            if k in m_uv:
                m_uv[k] ^= w
                changed = True
            else:
                m_uv[k] = w
        cur = [(u, v, w) for (u, v), w in m_uv.items() if w]
        # Merge on (u, w) -> xor v
        m_uw: Dict[Tuple[int, int], int] = {}
        for u, v, w in cur:
            k = (u, w)
            if k in m_uw:
                m_uw[k] ^= v
                changed = True
            else:
                m_uw[k] = v
        cur = [(u, v, w) for (u, w), v in m_uw.items() if v]
        # Merge on (v, w) -> xor u
        m_vw: Dict[Tuple[int, int], int] = {}
        for u, v, w in cur:
            k = (v, w)
            if k in m_vw:
                m_vw[k] ^= u
                changed = True
            else:
                m_vw[k] = u
        cur = [(u, v, w) for (v, w), u in m_vw.items() if u]
    return cur


def apply_flip(terms: List[Tuple[int, int, int]], i: int, j: int, shared_mode: int, twist: int = 0) -> Optional[List[Tuple[int, int, int]]]:
    """Exact Kauers-Moosbauer Flip move on two terms `(i, j)` sharing `shared_mode in {0, 1, 2}` (`u`, `v`, or `w`).
    `twist in {0, 1}` chooses which of the two non-shared modes is XORed into term i vs term j."""
    if i == j or not (0 <= i < len(terms) and 0 <= j < len(terms)):
        return None
    u1, v1, w1 = terms[i]
    u2, v2, w2 = terms[j]
    out = list(terms)
    if shared_mode == 0:
        if u1 != u2:
            return None
        if twist == 0:
            nt1, nt2 = (u1, v1, w1 ^ w2), (u2, v1 ^ v2, w2)
        else:
            nt1, nt2 = (u1, v1 ^ v2, w1), (u2, v2, w1 ^ w2)
    elif shared_mode == 1:
        if v1 != v2:
            return None
        if twist == 0:
            nt1, nt2 = (u1, v1, w1 ^ w2), (u1 ^ u2, v2, w2)
        else:
            nt1, nt2 = (u1 ^ u2, v1, w1), (u2, v2, w1 ^ w2)
    else:
        if w1 != w2:
            return None
        if twist == 0:
            nt1, nt2 = (u1, v1 ^ v2, w1), (u1 ^ u2, v2, w2)
        else:
            nt1, nt2 = (u1 ^ u2, v1, w1), (u2, v1 ^ v2, w2)
    out[i] = nt1
    out[j] = nt2
    return [t for t in out if t[0] and t[1] and t[2]]


def apply_plus(terms: List[Tuple[int, int, int]], i: int, mode: int, vec: int) -> Optional[List[Tuple[int, int, int]]]:
    """Exact Kauers-Moosbauer Plus move (`R -> R + 1`): splits term `i` along `mode in {0, 1, 2}` using `vec != 0`."""
    if not (0 <= i < len(terms)) or vec <= 0:
        return None
    u, v, w = terms[i]
    out = list(terms)
    if mode == 0:
        u2 = u ^ vec
        if u2 == 0:
            return None
        out[i] = (u2, v, w)
        out.append((vec, v, w))
    elif mode == 1:
        v2 = v ^ vec
        if v2 == 0:
            return None
        out[i] = (u, v2, w)
        out.append((u, vec, w))
    else:
        w2 = w ^ vec
        if w2 == 0:
            return None
        out[i] = (u, v, w2)
        out.append((u, v, vec))
    return out


# ---------------------------------------------------------------------------
# Published Baseline: Kauers-Moosbauer (2023) Flip-Graph Walk (`A1_FLIP_GRAPH`)
# ---------------------------------------------------------------------------
def build_s10_a1_flip_graph_artifact(name: str = "A1_FLIP_GRAPH") -> CompositionalAlgoArtifact:
    """Faithful published Kauers-Moosbauer (2023) Flip-Graph Random Walk + Reduction + Plus Transitions
    running under the EXACT SAME Law 4b+4c `OpBudget v3` as evolved arms!"""
    src = """
def fg_rand(st, m):
    st[0] = (st[0] * 1103515245 + 12345) & 0x7FFFFFFF
    return (st[0] >> 8) % m if m > 0 else 0

def fg_solve(api, budget):
    reduce_fn = api["reduce_terms"]
    flip_fn = api["flip_pair"]
    plus_fn = api["plus_split"]
    sub_fn = api["submit_best"]
    na = api["na"]
    nb = api["nb"]
    nc = api["nc"]
    best = reduce_fn(api["init_terms"])
    sub_fn(best, "a1_fg")
    cur = list(best)
    st = [(api["seed"] * 2654435761 + 17) & 0x7FFFFFFF]
    floor = max(40000, budget.limit // 25)
    stale = 0
    steps = 0
    while (budget.limit - budget.spent) > floor:
        steps += 1
        m = len(cur)
        if m <= 1:
            break
        # Find all flippable pairs sharing a factor in mode 0, 1, or 2
        mode = fg_rand(st, 3)
        buckets = {}
        for idx in range(m):
            key = cur[idx][mode]
            if key in buckets:
                buckets[key].append(idx)
            else:
                buckets[key] = [idx]
        cands = []
        for k in buckets:
            b = buckets[k]
            if len(b) >= 2:
                cands.append(b)
        if cands:
            b = cands[fg_rand(st, len(cands))]
            i1 = b[fg_rand(st, len(b))]
            i2 = b[fg_rand(st, len(b))]
            if i1 != i2:
                tw = fg_rand(st, 2)
                nxt = flip_fn(cur, i1, i2, mode, tw)
                if nxt is not None:
                    nxt = reduce_fn(nxt)
                    cur = nxt
                    if len(cur) < len(best):
                        best = list(cur)
                        sub_fn(best, "a1_fg")
                        stale = 0
                    else:
                        stale += 1
        else:
            stale += 1
        # Standard Kauers-Moosbauer Plus transition every ~120 stale steps (or restart from best)
        if stale > 120:
            if len(cur) <= len(best) + 1 and fg_rand(st, 2) == 0:
                idx = fg_rand(st, len(cur))
                pm = fg_rand(st, 3)
                # Split using another term's factor in same mode (encourages immediate flips!)
                jdx = fg_rand(st, len(cur))
                vec = cur[jdx][pm]
                if vec == cur[idx][pm]:
                    lim = (1 << (na if pm == 0 else (nb if pm == 1 else nc))) - 1
                    vec = 1 + fg_rand(st, lim)
                p_nxt = plus_fn(cur, idx, pm, vec)
                if p_nxt is not None:
                    cur = p_nxt
                stale = 0
            else:
                cur = list(best)
                stale = 0
    return best
"""
    mod = LibModule.from_source(
        name=f"mod_{name.lower()}",
        generation=0,
        source=src,
        origin="published_baseline",
        rationale="Published Kauers-Moosbauer (2023) Flip-Graph + Reduction + Plus Walk",
    )
    orch = LibModule.from_source(
        name="orchestrator",
        generation=0,
        source="def solve(api, lib, budget):\n    return lib.fg_solve(api, budget)\n",
        required_fn="solve",
        origin="published_baseline",
        rationale="Published Kauers-Moosbauer Flip-Graph",
    )
    return CompositionalAlgoArtifact(arm=name, track="S10_ALPHATENSOR_F2", generation=0, modules=(mod,), orchestrator=orch)


# ---------------------------------------------------------------------------
# Law 4b+4c Metered Execution Runtime (`run_s10_artifact`)
# ---------------------------------------------------------------------------
def run_s10_artifact(
    artifact: CompositionalAlgoArtifact,
    target: BilinearTensorF2,
    *,
    seed: int = 0,
    v3_budget: int = DEFAULT_S10_V3_BUDGET,
) -> Tuple[List[Tuple[int, int, int]], Dict[str, Any]]:
    """Run an S10 bilinear tensor rank artifact under strict Law 4b+4c metering and exact verification."""
    init_reduced = reduce_bilinear_terms(target.init_terms)

    def _verify(cand: Any) -> bool:
        if not isinstance(cand, (list, tuple)):
            return False
        return verify_bilinear_decomp(target, cand)

    def _cost(cand: Any) -> int:
        if not isinstance(cand, (list, tuple)):
            return 10**9
        return len(cand)

    def _api_factory(budget: OpBudget, report_best: Callable[[Any], bool]) -> Dict[str, Any]:
        def api_reduce(terms: Sequence[Tuple[int, int, int]]) -> List[Tuple[int, int, int]]:
            budget.charge(6 * len(terms) + 8)
            return reduce_bilinear_terms(terms)

        def api_flip(terms: List[Tuple[int, int, int]], i: int, j: int, shared_mode: int, twist: int = 0) -> Optional[List[Tuple[int, int, int]]]:
            budget.charge(len(terms) + 12)
            return apply_flip(terms, int(i), int(j), int(shared_mode), int(twist))

        def api_plus(terms: List[Tuple[int, int, int]], i: int, mode: int, vec: int) -> Optional[List[Tuple[int, int, int]]]:
            budget.charge(len(terms) + 12)
            return apply_plus(terms, int(i), int(mode), int(vec))

        def api_submit(terms: Sequence[Tuple[int, int, int]], tag: str = "algo") -> bool:
            budget.charge(6 * len(terms) + 20)
            red = reduce_bilinear_terms(terms)
            return report_best(red)

        return {
            "na": target.na,
            "nb": target.nb,
            "nc": target.nc,
            "init_terms": list(init_reduced),
            "seed": seed,
            "v3_budget": v3_budget,
            "reduce_terms": api_reduce,
            "flip_pair": api_flip,
            "plus_split": api_plus,
            "submit_best": api_submit,
            "rem_budget": lambda: max(0, budget.limit - budget.spent),
        }

    best_raw, tel = run_compositional_law4b(
        initial_solution=list(init_reduced),
        artifact=artifact,
        domain_api_factory=_api_factory,
        call_args_fn=lambda init_sol, api, lib, budget: (api, lib, budget),
        verify_fn=_verify,
        cost_fn=_cost,
        v3_budget=v3_budget,
    )
    best_clean = reduce_bilinear_terms(best_raw)
    if not verify_bilinear_decomp(target, best_clean):
        best_clean = list(init_reduced)
        tel["verifier_fallback"] = True
    else:
        tel["verifier_fallback"] = False
    return best_clean, tel
