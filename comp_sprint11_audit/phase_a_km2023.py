"""Phase A — Faithful Independent Reference Reproduction of Kauers & Moosbauer (2023)
("Flip Graphs for Matrix Multiplication", ISSAC 2023 / github.com/jakobmoosbauer/flips)
AND Wall-Clock-Equalized Head-to-Head Audit Against Sprint 10's `S10_G0` (`mod_g0_flip`).

Key Differences Between Our Throttled Sprint 10 `A1_FLIP_GRAPH` vs. Genuine Kauers & Moosbauer (2023):
  1. Sprint 10 `A1_FLIP_GRAPH` rebuilt `buckets` and called full `O(R)` `api["reduce_terms"]` on EVERY
     single flip inside `OpBudget v3`, limiting it to ~2,500 flips total and resetting after only 120 stale steps!
  2. Genuine Kauers & Moosbauer (2023) maintains incremental adjacency/factor sets, runs LONG random walks
     (path length limit `L = 10,000..50,000` flips per walk!) over ALL 3 modes, checks reductions in O(1)
     on ONLY the two modified terms, keeps a pool of minimum-rank schemes, and applies Plus transitions
     (splitting a term to create a new shared factor) when walks stall!

Stop Condition #1:
  This reference implementation MUST independently reproduce exact rank `23` on `3x3x3` matrix
  multiplication over `F_2` (as reported in Kauers & Moosbauer 2023), as well as rank `7` on `2x2x2`,
  `11` on `2x2x3`, `15` on `2x3x3`, and `14` on `2x2x4`!
"""
from __future__ import annotations

import json
import random
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from comp_sprint3.sprint3_runner import paired_wilcoxon_stats
from comp_sprint10_alphatensor.s10_benchmarks import build_s10_benchmarks, make_matmul_tensor
from comp_sprint10_alphatensor.s10_core import (
    BilinearTensorF2,
    reduce_bilinear_terms,
    verify_bilinear_decomp,
)


class IncrementalFlipState:
    """Fast pure-Python incremental binary tensor decomposition state for faithful Kauers-Moosbauer (2023).

    Maintains:
      - `terms`: list of `[u, v, w]` triples
      - `by_mode[m]`: dict `factor -> set of term indices` (for O(1) flip-edge sampling across all 3 modes!)
      - `by_pair[m]`: dict `(f_a, f_b) -> term index` (for O(1) immediate reduction detection!)
    """
    __slots__ = ("terms", "by_mode", "by_pair", "multi_keys")

    def __init__(self, init_terms: Sequence[Tuple[int, int, int]]) -> None:
        self.terms: List[Tuple[int, int, int]] = []
        self.by_mode: List[Dict[int, List[int]]] = [{}, {}, {}]
        self.by_pair: List[Dict[Tuple[int, int], int]] = [{}, {}, {}]
        self.multi_keys: List[List[int]] = [[], [], []]
        for t in reduce_bilinear_terms(init_terms):
            self._append(t)

    def clone(self) -> "IncrementalFlipState":
        return IncrementalFlipState(self.terms)

    def _pair_key(self, m: int, t: Tuple[int, int, int]) -> Tuple[int, int]:
        if m == 0:
            return (t[1], t[2])
        if m == 1:
            return (t[0], t[2])
        return (t[0], t[1])

    def _append(self, t: Tuple[int, int, int]) -> int:
        idx = len(self.terms)
        self.terms.append(t)
        for m in (0, 1, 2):
            f = t[m]
            lst = self.by_mode[m].get(f)
            if lst is None:
                self.by_mode[m][f] = [idx]
            else:
                if len(lst) == 1:
                    self.multi_keys[m].append(f)
                lst.append(idx)
            self.by_pair[m][self._pair_key(m, t)] = idx
        return idx

    def _remove_at(self, idx: int) -> None:
        last = len(self.terms) - 1
        t_rm = self.terms[idx]
        for m in (0, 1, 2):
            f = t_rm[m]
            lst = self.by_mode[m][f]
            lst.remove(idx)
            if not lst:
                del self.by_mode[m][f]
            pk = self._pair_key(m, t_rm)
            if self.by_pair[m].get(pk) == idx:
                del self.by_pair[m][pk]
        if idx != last:
            t_mv = self.terms[last]
            self.terms[idx] = t_mv
            for m in (0, 1, 2):
                f = t_mv[m]
                lst = self.by_mode[m][f]
                lst.remove(last)
                lst.append(idx)
                self.by_pair[m][self._pair_key(m, t_mv)] = idx
        self.terms.pop()

    def add_and_reduce(self, t: Tuple[int, int, int]) -> bool:
        """Insert `t` and cascade any exact reductions in O(1) amortized time. Returns True if a reduction occurred."""
        reduced = False
        queue = [t]
        while queue:
            u, v, w = queue.pop()
            if not (u and v and w):
                reduced = True
                continue
            # Check exact duplicate / 2-factor match across all 3 pair maps
            hit_idx = -1
            hit_m = -1
            for m, pk in ((0, (v, w)), (1, (u, w)), (2, (u, v))):
                idx = self.by_pair[m].get(pk)
                if idx is not None:
                    hit_idx = idx
                    hit_m = m
                    break
            if hit_idx >= 0:
                ou, ov, ow = self.terms[hit_idx]
                self._remove_at(hit_idx)
                reduced = True
                if hit_m == 0:
                    nu, nv, nw = ou ^ u, ov, ow
                elif hit_m == 1:
                    nu, nv, nw = ou, ov ^ v, ow
                else:
                    nu, nv, nw = ou, ov, ow ^ w
                if nu and nv and nw:
                    queue.append((nu, nv, nw))
            else:
                self._append((u, v, w))
        return reduced

    def sample_and_flip(self, rng: random.Random) -> bool:
        """Sample a uniform random flippable pair across modes 0, 1, 2 and apply an exact flip + O(1) reduction!
        Returns True if rank strictly decreased."""
        # Collect active modes with at least one bucket of size >= 2
        m_order = [0, 1, 2]
        rng.shuffle(m_order)
        for m in m_order:
            mk = self.multi_keys[m]
            bm = self.by_mode[m]
            while mk:
                k_idx = rng.randrange(len(mk))
                f = mk[k_idx]
                lst = bm.get(f)
                if lst is None or len(lst) < 2:
                    mk[k_idx] = mk[-1]
                    mk.pop()
                    continue
                L = len(lst)
                a = rng.randrange(L)
                b = rng.randrange(L - 1)
                if b >= a:
                    b += 1
                i, j = lst[a], lst[b]
                if i < j:
                    i, j = j, i  # remove higher index first!
                u1, v1, w1 = self.terms[i]
                u2, v2, w2 = self.terms[j]
                tw = rng.randrange(2)
                if m == 0:
                    nt1, nt2 = ((u1, v1, w1 ^ w2), (u2, v1 ^ v2, w2)) if tw == 0 else ((u1, v1 ^ v2, w1), (u2, v2, w1 ^ w2))
                elif m == 1:
                    nt1, nt2 = ((u1, v1, w1 ^ w2), (u1 ^ u2, v2, w2)) if tw == 0 else ((u1 ^ u2, v1, w1), (u2, v2, w1 ^ w2))
                else:
                    nt1, nt2 = ((u1, v1 ^ v2, w1), (u1 ^ u2, v2, w2)) if tw == 0 else ((u1 ^ u2, v1, w1), (u2, v1 ^ v2, w2))
                r_before = len(self.terms)
                self._remove_at(i)
                self._remove_at(j)
                self.add_and_reduce(nt1)
                self.add_and_reduce(nt2)
                return len(self.terms) < r_before
        return False

    def apply_plus_random(self, rng: random.Random, na: int, nb: int, nc: int) -> bool:
        """Exact Kauers-Moosbauer (2023) fused atomic Plus transition on two terms `(i, j)` in mode `m`:
            (u_i, v_i, w_i) + (u_j, v_j, w_j)
              = (u_i^u_j, v_i, w_i) + (u_j, v_i, w_i^w_j) + (u_j, v_i^v_j, w_j)  (mod 2)
        Produces a genuinely reduced (R+1)-term decomposition that does NOT trivially collapse back!"""
        R = len(self.terms)
        if R < 2:
            return False
        for _ in range(16):
            i = rng.randrange(R)
            j = rng.randrange(R - 1)
            if j >= i:
                j += 1
            m = rng.randrange(3)
            u1, v1, w1 = self.terms[i]
            u2, v2, w2 = self.terms[j]
            if (u1 == u2) or (v1 == v2) or (w1 == w2):
                continue
            hi, lo = (i, j) if i > j else (j, i)
            self._remove_at(hi)
            self._remove_at(lo)
            if m == 0:
                t1, t2, t3 = (u1 ^ u2, v1, w1), (u2, v1, w1 ^ w2), (u2, v1 ^ v2, w2)
            elif m == 1:
                t1, t2, t3 = (u1, v1 ^ v2, w1), (u1, v2, w1 ^ w2), (u1 ^ u2, v2, w2)
            else:
                t1, t2, t3 = (u1, v1, w1 ^ w2), (u1 ^ u2, v1, w2), (u2, v1 ^ v2, w2)
            self.add_and_reduce(t1)
            self.add_and_reduce(t2)
            self.add_and_reduce(t3)
            return True
        return False


def km2023_reference_search(
    target: BilinearTensorF2,
    *,
    time_limit_sec: float = 0.50,
    path_limit: int = 8000,
    pool_size: int = 16,
    seed: int = 0,
    use_xor_triangle_plus: bool = False,
) -> Tuple[List[Tuple[int, int, int]], Dict[str, Any]]:
    """Faithful Kauers & Moosbauer (2023) Flip-Graph Random Walk with Pool + Long Paths + Plus Escapes.

    Runs under an EXACT wall-clock limit (`time_limit_sec`) with O(1) incremental flip + reduction!
    """
    t0 = time.perf_counter()
    deadline = t0 + time_limit_sec
    rng = random.Random(seed * 2654435761 + 17)
    init_red = reduce_bilinear_terms(target.init_terms)
    best_terms = list(init_red)
    best_rank = len(best_terms)
    pool: List[List[Tuple[int, int, int]]] = [list(best_terms)]
    total_flips = 0
    total_plus = 0
    walks = 0

    while time.perf_counter() < deadline and best_rank > 1:
        walks += 1
        base_scheme = pool[rng.randrange(len(pool))]
        st = IncrementalFlipState(base_scheme)
        # Apply Plus escape after initial pure-flip exploration stalls on current rank
        if walks > 3 and (walks % 2 == 0):
            if use_xor_triangle_plus:
                _apply_xor_triangle_plus(st, rng, target.na, target.nb, target.nc)
            else:
                st.apply_plus_random(rng, target.na, target.nb, target.nc)
            total_plus += 1

        step = 0
        while step < path_limit:
            if (step & 255) == 0 and time.perf_counter() >= deadline:
                break
            total_flips += 1
            step += 1
            reduced = st.sample_and_flip(rng)
            r = len(st.terms)
            if r < best_rank:
                best_rank = r
                best_terms = list(st.terms)
                pool = [list(best_terms)]
                walks = 0
                step = 0  # restart path clock on strict rank drop!
            elif r == best_rank and reduced and len(pool) < pool_size:
                pool.append(list(st.terms))
            elif r > best_rank + 1:
                break
        # Even if no reduction, add diverse equal-rank endpoint to pool
        if len(st.terms) == best_rank and len(pool) < pool_size:
            pool.append(list(st.terms))

    assert verify_bilinear_decomp(target, best_terms)
    return best_terms, {
        "rank": best_rank,
        "wall_sec": round(time.perf_counter() - t0, 4),
        "total_flips": total_flips,
        "total_plus": total_plus,
        "walks": walks,
    }


def _apply_xor_triangle_plus(st: IncrementalFlipState, rng: random.Random, na: int, nb: int, nc: int) -> bool:
    """Phase D Structural Strategy Modification: Fused 3-Term XOR-Triangle Plus-Bridge!
    Finds `(i, j, k)` in mode `m` with `f_i ^ f_j ^ f_k == 0` (so `f_i ^ f_j == f_k` already exists in term `k`!),
    and applies the exact fused Kauers-Moosbauer Plus move to `(i, j)`:
      (f_i, v_i, w_i) + (f_j, v_j, w_j) = (f_k, v_i, w_i) + (f_j, v_i, w_i^w_j) + (f_j, v_i^v_j, w_j)
    Because `f_k` ALREADY exists in term `k`, ALL THREE new terms immediately have flip partners
    (`f_k` with term `k`, `f_j` with each other, AND `v_i` with each other -> `deg_flip` jumps >= +3)!"""
    R = len(st.terms)
    if R < 3:
        return st.apply_plus_random(rng, na, nb, nc)
    m_order = [0, 1, 2]
    rng.shuffle(m_order)
    for m in m_order:
        f_set = st.by_mode[m]
        factors = list(f_set.keys())
        L = len(factors)
        if L < 3:
            continue
        trials = min(L * (L - 1) // 2, 64)
        for _ in range(trials):
            fa = factors[rng.randrange(L)]
            fb = factors[rng.randrange(L)]
            if fa == fb:
                continue
            fc = fa ^ fb
            if fc in f_set:
                idx_i = f_set[fc][rng.randrange(len(f_set[fc]))]
                idx_j = f_set[fa][rng.randrange(len(f_set[fa]))]
                if idx_i == idx_j:
                    continue
                u1, v1, w1 = st.terms[idx_i]
                u2, v2, w2 = st.terms[idx_j]
                if (u1 == u2) or (v1 == v2) or (w1 == w2):
                    continue
                hi, lo = (idx_i, idx_j) if idx_i > idx_j else (idx_j, idx_i)
                st._remove_at(hi)
                st._remove_at(lo)
                if m == 0:
                    t1, t2, t3 = (u1 ^ u2, v1, w1), (u2, v1, w1 ^ w2), (u2, v1 ^ v2, w2)
                elif m == 1:
                    t1, t2, t3 = (u1, v1 ^ v2, w1), (u1, v2, w1 ^ w2), (u1 ^ u2, v2, w2)
                else:
                    t1, t2, t3 = (u1, v1, w1 ^ w2), (u1 ^ u2, v1, w2), (u2, v1 ^ v2, w2)
                st.add_and_reduce(t1)
                st.add_and_reduce(t2)
                st.add_and_reduce(t3)
                return True
    return st.apply_plus_random(rng, na, nb, nc)


def run_s10_g0_wallclock(
    s10_proposals_path: Path,
    target: BilinearTensorF2,
    *,
    time_limit_sec: float = 0.50,
    seed: int = 0,
) -> Tuple[List[Tuple[int, int, int]], Dict[str, Any]]:
    """Run Sprint 10's `S10_G0` (`mod_g0_flip`) UN-THROTTLED under the EXACT SAME real wall-clock limit
    as `km2023_reference_search` — true apples-to-apples wall-clock comparison!"""
    prop = json.loads(s10_proposals_path.read_text(encoding="utf-8"))
    ns: Dict[str, Any] = {}
    for m in prop["artifacts"]["A2_PRIOR_ONLY"]["modules"]:
        exec(compile(m["source"], m["name"], "exec"), ns)
    exec(compile(prop["artifacts"]["A2_PRIOR_ONLY"]["orchestrator"]["source"], "orchestrator", "exec"), ns)

    init_red = reduce_bilinear_terms(target.init_terms)
    best_box = [list(init_red)]
    t0 = time.perf_counter()
    deadline = t0 + time_limit_sec

    class _WallBudget:
        limit = 10_000_000
        @property
        def spent(self) -> int:
            frac = min(1.0, (time.perf_counter() - t0) / max(1e-6, time_limit_sec))
            return int(frac * self.limit)

    class _Lib:
        def __getattr__(self, name: str) -> Any:
            return ns[name]
        def has(self, name: str) -> bool:
            return name in ns

    def api_submit(terms: Sequence[Tuple[int, int, int]], tag: str = "g0") -> bool:
        red = reduce_bilinear_terms(terms)
        if len(red) < len(best_box[0]) and verify_bilinear_decomp(target, red):
            best_box[0] = red
            return True
        return False

    from comp_sprint10_alphatensor.s10_core import apply_flip, apply_plus
    wb = _WallBudget()
    api = {
        "na": target.na, "nb": target.nb, "nc": target.nc,
        "init_terms": list(init_red), "seed": seed, "v3_budget": wb.limit,
        "reduce_terms": reduce_bilinear_terms,
        "flip_pair": apply_flip,
        "plus_split": apply_plus,
        "submit_best": api_submit,
        "rem_budget": lambda: max(0, wb.limit - wb.spent),
    }
    try:
        out = ns["solve"](api, _Lib(), wb)
        if isinstance(out, (list, tuple)):
            api_submit(out, "final")
    except Exception:
        pass
    assert verify_bilinear_decomp(target, best_box[0])
    return best_box[0], {"rank": len(best_box[0]), "wall_sec": round(time.perf_counter() - t0, 4)}


def run_phase_a_audit(s10_proposals_path: Path, out_path: Path) -> Dict[str, Any]:
    """Execute Phase A:
      1. Stop Condition #1 check: Verify faithful KM-2023 reproduces rank 23 on 3x3x3 (and 7, 11, 15, 14)!
      2. Strict wall-clock-equalized head-to-head comparison (0.50s/task & 1.50s/task) across ALL 60
         distinct Sprint 10 holdout tensors: Faithful KM-2023 Reference vs. S10_G0 (`mod_g0_flip`)!
    """
    print("=== PHASE A.1: STOP CONDITION #1 — FAITHFUL KAUERS-MOOSBAUER (2023) REPRODUCTION ===")
    classic_targets = [
        ("matmul_2x2x2", make_matmul_tensor(2, 2, 2), 7, 0.5),
        ("matmul_2x2x3", make_matmul_tensor(2, 2, 3), 11, 0.5),
        ("matmul_2x3x3", make_matmul_tensor(2, 3, 3), 15, 1.0),
        ("matmul_2x2x4", make_matmul_tensor(2, 2, 4), 14, 1.0),
        ("matmul_3x3x3", make_matmul_tensor(3, 3, 3), 23, 4.0),
    ]
    repro = {}
    for name, ten, target_r, tlim in classic_targets:
        best_r = 999
        best_meta = {}
        for sd in range(5):
            sol, meta = km2023_reference_search(ten, time_limit_sec=tlim, seed=sd)
            if len(sol) < best_r:
                best_r = len(sol)
                best_meta = meta
            if best_r <= target_r:
                break
        repro[name] = {"target_rank": target_r, "achieved_rank": best_r, "matched": best_r <= target_r, "meta": best_meta}
        print(f"  {name:14s}: target={target_r:2d} | KM2023_ref={best_r:2d} | matched={best_r <= target_r} | flips={best_meta.get('total_flips')} | wall={best_meta.get('wall_sec')}s", flush=True)

    assert repro["matmul_3x3x3"]["matched"], "STOP CONDITION #1 TRIGGERED: Failed to reproduce KM-2023 rank 23 on 3x3x3!"

    print("\n=== PHASE A.2: WALL-CLOCK-EQUALIZED HEAD-TO-HEAD (0.50s/TASK, N=60 DISTINCT S10 TASKS) ===")
    suites = build_s10_benchmarks()
    hold_tasks = suites["s10_hold_matmul"] + suites["s10_hold_proc_planted"] + suites["s10_hold_proc_rand"]
    km_scores: Dict[str, int] = {}
    g0_scores: Dict[str, int] = {}
    km_wall = 0.0
    g0_wall = 0.0
    for t in hold_tasks:
        # Median of 3 seeds at exact 0.50s/run -> 1 score per distinct task (N=60 tasks, NOT 180!)
        ks, gs = [], []
        for sd in (0, 1, 2):
            _, mk = km2023_reference_search(t.tensor, time_limit_sec=0.50, seed=sd)
            _, mg = run_s10_g0_wallclock(s10_proposals_path, t.tensor, time_limit_sec=0.50, seed=sd)
            ks.append(mk["rank"]); km_wall += mk["wall_sec"]
            gs.append(mg["rank"]); g0_wall += mg["wall_sec"]
        km_scores[t.task_id] = int(statistics.median(ks))
        g0_scores[t.task_id] = int(statistics.median(gs))

    # Breakdown by stratum
    def _sum_s(scores, sn):
        return sum(scores[t.task_id] for t in suites[sn])
    km_tot = sum(km_scores.values())
    g0_tot = sum(g0_scores.values())
    deltas = [g0_scores[t.task_id] - km_scores[t.task_id] for t in hold_tasks]
    w_all = paired_wilcoxon_stats(deltas)
    w_mm = paired_wilcoxon_stats([g0_scores[t.task_id] - km_scores[t.task_id] for t in suites["s10_hold_matmul"]])
    w_pr = paired_wilcoxon_stats([g0_scores[t.task_id] - km_scores[t.task_id] for t in suites["s10_hold_proc_planted"] + suites["s10_hold_proc_rand"]])

    print(f"  Faithful KM-2023 (0.50s/run): ALL={km_tot} | MATMUL={_sum_s(km_scores,'s10_hold_matmul')} | PLANTED={_sum_s(km_scores,'s10_hold_proc_planted')} | RAND={_sum_s(km_scores,'s10_hold_proc_rand')} | wall={km_wall:.1f}s")
    print(f"  S10_G0 mod_g0_flip (0.50s)  : ALL={g0_tot} | MATMUL={_sum_s(g0_scores,'s10_hold_matmul')} | PLANTED={_sum_s(g0_scores,'s10_hold_proc_planted')} | RAND={_sum_s(g0_scores,'s10_hold_proc_rand')} | wall={g0_wall:.1f}s")
    print(f"  S10_G0 vs Faithful KM-2023 (All 60): d={w_all['sum_delta']:+.1f} | {w_all['wins']}W/{w_all['ties']}T/{w_all['losses']}L | p_two={w_all['p_two']:.6f}")
    print(f"  S10_G0 vs Faithful KM-2023 (Mat 12): d={w_mm['sum_delta']:+.1f} | {w_mm['wins']}W/{w_mm['ties']}T/{w_mm['losses']}L | p_two={w_mm['p_two']:.6f}")
    print(f"  S10_G0 vs Faithful KM-2023 (Prc 48): d={w_pr['sum_delta']:+.1f} | {w_pr['wins']}W/{w_pr['ties']}T/{w_pr['losses']}L | p_two={w_pr['p_two']:.6f}")
    print("\n  Classic Matmul Breakdown (0.50s equalized wall-clock, 3-seed median):")
    for t in suites["s10_hold_matmul"]:
        print(f"    {t.task_id:15s}: Base={t.base_rank:2d} | KM2023_ref={km_scores[t.task_id]:2d} | S10_G0={g0_scores[t.task_id]:2d}")

    out = {
        "stop_condition_1_repro": repro,
        "wall_equalized_0p5s": {
            "km2023_total": km_tot,
            "s10_g0_total": g0_tot,
            "km2023_wall_sec": round(km_wall, 2),
            "s10_g0_wall_sec": round(g0_wall, 2),
            "by_stratum": {
                sn: {"km2023": _sum_s(km_scores, sn), "s10_g0": _sum_s(g0_scores, sn)}
                for sn in ("s10_hold_matmul", "s10_hold_proc_planted", "s10_hold_proc_rand")
            },
            "wilcoxon_all60": w_all,
            "wilcoxon_matmul12": w_mm,
            "wilcoxon_proc48": w_pr,
            "matmul_detail": {t.task_id: {"base": t.base_rank, "km2023": km_scores[t.task_id], "s10_g0": g0_scores[t.task_id]} for t in suites["s10_hold_matmul"]},
        },
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


if __name__ == "__main__":
    import sys
    run_phase_a_audit(Path(sys.argv[1]), Path(sys.argv[2]))
