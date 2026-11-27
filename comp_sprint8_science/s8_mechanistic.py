"""Study 1 (100% Offline Mechanistic Science, $0.00 LLM):
1. Five-Component Controlled Factorial Ablation of Sprint 7's Evolved `mod_g3_null_todd`
   on BOTH Sprint 7's 44-task `n=6..8` holdout AND Sprint 8's 80-task `n=8..11` holdout!
2. Zero-Shot Out-of-Distribution Scale Transfer (`S7_G3_TRANSFER` on unseen `n=8..11` qubits,
   including 20 real literature quantum circuits) vs Published `T-par (2014)`, `TODD (2018)`,
   `FastTODD (2022)`, and Full-Budget `A5_SHAM`!
3. Scientific Synthesis Test (`SYNTH_SPARSE_NULL_TODD`): Replacing S7 G3's `O(2^n)` cubic `sig`
   table with our exact `C(n-1, 2)` involutive `chi_z` nullspace while retaining all 4 evolved
   algorithmic mechanisms (`M2` shift-multiplicity branch-and-bound, `M3` Gray-code nullspace
   enumeration, `M4` plateau/uphill nullspace walk, `M5` `RM(n-4, n)` weight-15 `span_4` kicks).
"""
from __future__ import annotations

import json
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from comp_sprint3.sandbox_s3 import CompositionalAlgoArtifact, LibModule
from comp_sprint3.sprint3_runner import paired_wilcoxon_stats
from comp_sprint7_clifford_t.s7_benchmarks import build_s7_benchmarks
from comp_sprint7_clifford_t.s7_core import (
    CliffordTCircuit,
    DEFAULT_S7_V3_BUDGET,
    todd_baseline_optimize as todd_optimize,
    tpar_fold_baseline as tpar_optimize,
)
from comp_sprint8_science.s8_benchmarks import build_s8_benchmarks
from comp_sprint8_science.s8_core import (
    DEFAULT_S8_V3_BUDGET,
    fast_todd_2022_optimize,
    run_s8_artifact,
    todd_2018_optimize,
)


def build_ablation_artifact(
    name: str,
    *,
    use_bnb: bool = True,       # M2: shift-multiplicity bucket sort + 2c+2 branch-and-bound
    use_gray_null: bool = True, # M3: Gray-code full-nullspace enumeration (vs 1st basis vec only)
    use_plateau: bool = True,   # M4: g==0 / g>=-2 nullspace plateau/uphill moves
    use_rm_span4: bool = True,  # M5: RM(n-4, n) weight-15 4D-subspace codeword kicks
    use_sparse_chiz: bool = False,  # Scientific synthesis: exact C(n-1,2) sparse chi_z (no 2^n table!)
) -> CompositionalAlgoArtifact:
    """Build an exact, AST-sandboxed Law 4b/4c artifact isolating each mathematical mechanism."""
    if not use_sparse_chiz:
        # Exact S7 `mod_g3_null_todd` family (with configurable switches for M2/M3/M4/M5)
        mod_src = f"""
def ab_reduce(P):
    cnt = {{}}
    for y in P:
        if y:
            cnt[y] = cnt.get(y, 0) ^ 1
    return [y for y in cnt if cnt[y]]

def ab_rand(st, m):
    st[0] = (st[0] * 1103515245 + 12345) & 0x7FFFFFFF
    return (st[0] >> 8) % m if m > 0 else 0

def ab_sigtab(n):
    tri = {{}}
    k = 0
    for a in range(n):
        for b in range(a + 1, n):
            for c in range(b + 1, n):
                tri[(a * n + b) * n + c] = k
                k += 1
    N = 1 << n
    sig = [0] * N
    for y in range(1, N):
        h = y.bit_length() - 1
        r = y ^ (1 << h)
        s = sig[r]
        bits = []
        t = r
        i = 0
        while t:
            if t & 1:
                bits.append(i)
            t >>= 1
            i += 1
        L = len(bits)
        for p in range(L):
            bp = bits[p] * n
            for q in range(p + 1, L):
                s ^= 1 << tri[(bp + bits[q]) * n + h]
        sig[y] = s
    return sig

def ab_null(cols):
    piv = {{}}
    out = []
    bit = 1
    for c in cols:
        v = c
        cm = bit
        while v:
            lb = v & -v
            if lb in piv:
                e = piv[lb]
                v ^= e[0]
                cm ^= e[1]
            else:
                piv[lb] = (v, cm)
                break
        if v == 0:
            out.append(cm)
        bit <<= 1
    return out

def ab_newsize(P, par, r0, y, z):
    tog = {{}}
    cnt = 0
    j = 0
    yy = y
    while yy:
        if yy & 1:
            a = P[j]
            tog[a] = tog.get(a, 0) ^ 1
            b = a ^ z
            tog[b] = tog.get(b, 0) ^ 1
            cnt += 1
        yy >>= 1
        j += 1
    if cnt & 1:
        tog[z] = tog.get(z, 0) ^ 1
    s = r0
    for k in tog:
        if k and tog[k]:
            if par.get(k, 0):
                s -= 1
            else:
                s += 1
    return s

def ab_apply(P, y, z):
    Q = []
    cnt = 0
    for j in range(len(P)):
        a = P[j]
        if (y >> j) & 1:
            Q.append(a ^ z)
            cnt += 1
        else:
            Q.append(a)
    if cnt & 1:
        Q.append(z)
    return ab_reduce(Q)

def ab_scan(P, n, sig, budget, floor, st, collect, window, maxd):
    m = len(P)
    par = {{}}
    for a in P:
        par[a] = par.get(a, 0) ^ 1
    r0 = 0
    for k in par:
        if par[k]:
            r0 += 1
    lim = 1 << n
    pc = [0] * lim
    for i in range(m):
        ai = P[i]
        for j in range(i + 1, m):
            pc[ai ^ P[j]] += 1
        pc[ai] += 1
    pc[0] = 0
    mx = 0
    for z in range(1, lim):
        if pc[z] > mx:
            mx = pc[z]
    off = ab_rand(st, lim)
    if {use_bnb}:
        buckets = [[] for q in range(mx + 1)]
        for t in range(1, lim):
            z = ((t + off) % (lim - 1)) + 1
            c = pc[z]
            if c:
                buckets[c].append(z)
    else:
        buckets = [[], []]
        for t in range(1, lim):
            z = ((t + off) % (lim - 1)) + 1
            if pc[z]:
                buckets[1].append(z)
        mx = 1
    sP = [sig[a] for a in P]
    best_gain = 0
    best = None
    zero = []
    nz = 0
    hit = -1
    cnt = 0
    stop = False
    for c in range(mx, 0, -1):
        if {use_bnb} and 2 * c + 2 <= best_gain:
            break
        for z in buckets[c]:
            cnt += 1
            if (cnt & 7) == 0 and (budget.limit - budget.spent) <= floor:
                stop = True
                break
            if hit >= 0 and cnt - hit > window:
                stop = True
                break
            sz = sig[z]
            cols = []
            for j in range(m):
                a = P[j]
                cols.append(a | ((sig[a ^ z] ^ sP[j] ^ sz) << n))
            nl = ab_null(cols)
            d = len(nl)
            if d == 0:
                continue
            if {use_gray_null}:
                dd = d if d <= maxd else maxd
                tt = 1 << dd
                y = 0
                for t in range(1, tt + d - dd):
                    if t < tt:
                        idx = (t & -t).bit_length() - 1
                        y ^= nl[idx]
                        yv = y
                    else:
                        yv = nl[dd + t - tt]
                    s = ab_newsize(P, par, r0, yv, z)
                    g = r0 - s
                    if g > best_gain:
                        best_gain = g
                        best = (z, yv)
                        if hit < 0:
                            hit = cnt
                    elif collect and best is None and g >= -2:
                        nz += 1
                        if len(zero) < 16:
                            zero.append((g, z, yv))
                        else:
                            k = ab_rand(st, nz)
                            if k < 16:
                                zero[k] = (g, z, yv)
            else:
                yv = nl[0]
                s = ab_newsize(P, par, r0, yv, z)
                g = r0 - s
                if g > best_gain:
                    best_gain = g
                    best = (z, yv)
                    if hit < 0:
                        hit = cnt
                elif collect and best is None and g >= -2:
                    nz += 1
                    if len(zero) < 16:
                        zero.append((g, z, yv))
        if stop:
            break
    return (best_gain, best, zero)

def ab_descent(P, n, sig, budget, floor, st, window, maxd):
    P = list(P)
    while len(P) > 1 and (budget.limit - budget.spent) > floor:
        res = ab_scan(P, n, sig, budget, floor, st, False, window, maxd)
        mv = res[1]
        if mv is None:
            break
        P = ab_apply(P, mv[1], mv[0])
    return ab_reduce(P)

def ab_solve(P0, n, seed, budget, on_improve):
    floor = max(40000, budget.limit // 20)
    if n > 10:
        # O(2^n) sig table still runs for n=11 if budget allows, demonstrating scaling cost honestly
        pass
    sig = ab_sigtab(n)
    st = [(seed * 7 + 3) & 0x7FFFFFFF]
    best = ab_descent(ab_reduce(P0), n, sig, budget, floor, st, 24, 6)
    if on_improve is not None:
        on_improve(best)
    cur = list(best)
    lim = (1 << n) - 1
    stale = 0
    guard = 0
    while len(best) > 1 and (budget.limit - budget.spent) > floor:
        guard += 1
        if guard > 100000:
            break
        m = len(cur)
        if m < 2:
            break
        kind = ab_rand(st, 10)
        Q = None
        up = False
        if kind < 4 and {use_plateau}:
            res = ab_scan(cur, n, sig, budget, floor, st, True, 1000000, 6)
            if res[1] is not None:
                Q = ab_apply(cur, res[1][1], res[1][0])
            else:
                zl = res[2]
                if zl:
                    z0 = [e for e in zl if e[0] == 0]
                    pool = zl
                    if z0 and ab_rand(st, 4) != 0:
                        pool = z0
                    e = pool[ab_rand(st, len(pool))]
                    Q = ab_apply(cur, e[2], e[1])
                    up = True
        elif kind >= 8 and {use_rm_span4}:
            basis = [cur[ab_rand(st, m)], cur[ab_rand(st, m)], 1 + ab_rand(st, lim), 1 + ab_rand(st, lim)]
            span = []
            for mask in range(1, 16):
                v = 0
                for t in range(4):
                    if (mask >> t) & 1:
                        v ^= basis[t]
                if v:
                    span.append(v)
            Q = ab_reduce(cur + span)
        else:
            w = cur[ab_rand(st, m)] ^ cur[ab_rand(st, m)]
            if kind >= 6:
                w ^= cur[ab_rand(st, m)]
            if w == 0:
                w = 1 + ab_rand(st, lim)
            Q = cur + [w, w]
        if Q is None:
            stale += 1
            if stale > 30:
                cur = list(best)
                stale = 0
            continue
        R = ab_descent(Q, n, sig, budget, floor, st, 24, 6)
        if len(R) < len(best):
            best = list(R)
            cur = list(R)
            stale = 0
            if on_improve is not None:
                on_improve(best)
        else:
            if len(R) <= len(cur) or (up and len(R) <= len(cur) + 2 and ab_rand(st, 3) == 0):
                cur = R
            stale += 1
        if stale > 30:
            cur = list(best)
            stale = 0
    return best
"""
    else:
        # Scientific Synthesis: Scale-Free O(m^2) Sparse Pairwise-XOR + Exact C(n-1, 2) Involutive chi_z
        # + ALL 4 Evolved S7 Mechanisms (M2 BnB + M3 Gray Nullspace + M4 Plateau Walk + M5 RM(n-4,n) span_4!)
        mod_src = """
def ab_reduce(P):
    cnt = {}
    for y in P:
        if y:
            cnt[y] = cnt.get(y, 0) ^ 1
    return [y for y in cnt if cnt[y]]

def ab_rand(st, m):
    st[0] = (st[0] * 1103515245 + 12345) & 0x7FFFFFFF
    return (st[0] >> 8) % m if m > 0 else 0

def ab_newsize(P, par, r0, y, z):
    tog = {}
    cnt = 0
    j = 0
    yy = y
    while yy:
        if yy & 1:
            a = P[j]
            tog[a] = tog.get(a, 0) ^ 1
            b = a ^ z
            tog[b] = tog.get(b, 0) ^ 1
            cnt += 1
        yy >>= 1
        j += 1
    if cnt & 1:
        tog[z] = tog.get(z, 0) ^ 1
    s = r0
    for k in tog:
        if k and tog[k]:
            if par.get(k, 0):
                s -= 1
            else:
                s += 1
    return s

def ab_apply(P, y, z):
    Q = []
    cnt = 0
    for j in range(len(P)):
        a = P[j]
        if (y >> j) & 1:
            Q.append(a ^ z)
            cnt += 1
        else:
            Q.append(a)
    if cnt & 1:
        Q.append(z)
    return ab_reduce(Q)

def ab_scan_sparse(P, n, api, budget, floor, st, collect, window, maxd):
    m = len(P)
    par = {}
    for a in P:
        par[a] = par.get(a, 0) ^ 1
    r0 = len(par)
    # Sparse O(m^2) shift multiplicity map — ZERO O(2^n) scan!
    pc = {}
    for i in range(m):
        ai = P[i]
        pc[ai] = pc.get(ai, 0) + 1
        for j in range(i + 1, m):
            z = ai ^ P[j]
            if z:
                pc[z] = pc.get(z, 0) + 1
    mx = 0
    for c in pc.values():
        if c > mx:
            mx = c
    buckets = [[] for _ in range(mx + 1)]
    for z, c in pc.items():
        buckets[c].append(z)
    # Light deterministic shuffle per bucket
    for c in range(1, mx + 1):
        bk = buckets[c]
        L = len(bk)
        if L > 1:
            off = ab_rand(st, L)
            buckets[c] = bk[off:] + bk[:off]
    best_gain = 0
    best = None
    zero = []
    nz = 0
    hit = -1
    cnt = 0
    stop = False
    chi_fn = api["chi_z_cols"]
    null_fn = api["nullspace_gf2"]
    for c in range(mx, 0, -1):
        if 2 * c + 2 <= best_gain:
            break
        for z in buckets[c]:
            cnt += 1
            if (cnt & 3) == 0 and (budget.limit - budget.spent) <= floor:
                stop = True
                break
            if hit >= 0 and cnt - hit > window:
                stop = True
                break
            cols = chi_fn(P, z)
            nl = null_fn(cols)
            d = len(nl)
            if d == 0:
                continue
            dd = d if d <= maxd else maxd
            tt = 1 << dd
            y = 0
            for t in range(1, tt + d - dd):
                if t < tt:
                    idx = (t & -t).bit_length() - 1
                    y ^= nl[idx]
                    yv = y
                else:
                    yv = nl[dd + t - tt]
                s = ab_newsize(P, par, r0, yv, z)
                g = r0 - s
                if g > best_gain:
                    best_gain = g
                    best = (z, yv)
                    if hit < 0:
                        hit = cnt
                elif collect and best is None and g >= -2:
                    nz += 1
                    if len(zero) < 16:
                        zero.append((g, z, yv))
                    else:
                        k = ab_rand(st, nz)
                        if k < 16:
                            zero[k] = (g, z, yv)
        if stop:
            break
    return (best_gain, best, zero)

def ab_descent_sparse(P, n, api, budget, floor, st, window, maxd):
    P = list(P)
    while len(P) > 1 and (budget.limit - budget.spent) > floor:
        res = ab_scan_sparse(P, n, api, budget, floor, st, False, window, maxd)
        mv = res[1]
        if mv is None:
            break
        P = ab_apply(P, mv[1], mv[0])
    return ab_reduce(P)

def ab_solve_sparse(P0, n, api, seed, budget, on_improve):
    floor = max(60000, budget.limit // 20)
    st = [(seed * 7 + 3) & 0x7FFFFFFF]
    best = ab_descent_sparse(ab_reduce(P0), n, api, budget, floor, st, 24, 6)
    if on_improve is not None:
        on_improve(best)
    cur = list(best)
    lim = (1 << n) - 1
    stale = 0
    guard = 0
    while len(best) > 1 and (budget.limit - budget.spent) > floor:
        guard += 1
        if guard > 100000:
            break
        m = len(cur)
        if m < 2:
            break
        kind = ab_rand(st, 10)
        Q = None
        up = False
        if kind < 4:
            res = ab_scan_sparse(cur, n, api, budget, floor, st, True, 200, 6)
            if res[1] is not None:
                Q = ab_apply(cur, res[1][1], res[1][0])
            else:
                zl = res[2]
                if zl:
                    z0 = [e for e in zl if e[0] == 0]
                    pool = zl
                    if z0 and ab_rand(st, 4) != 0:
                        pool = z0
                    e = pool[ab_rand(st, len(pool))]
                    Q = ab_apply(cur, e[2], e[1])
                    up = True
        elif kind < 8:
            w = cur[ab_rand(st, m)] ^ cur[ab_rand(st, m)]
            if kind >= 6:
                w ^= cur[ab_rand(st, m)]
            if w == 0:
                w = 1 + ab_rand(st, lim)
            Q = cur + [w, w]
        else:
            basis = [cur[ab_rand(st, m)], cur[ab_rand(st, m)], 1 + ab_rand(st, lim), 1 + ab_rand(st, lim)]
            span = []
            for mask in range(1, 16):
                v = 0
                for t in range(4):
                    if (mask >> t) & 1:
                        v ^= basis[t]
                if v:
                    span.append(v)
            Q = ab_reduce(cur + span)
        if Q is None:
            stale += 1
            if stale > 30:
                cur = list(best)
                stale = 0
            continue
        R = ab_descent_sparse(Q, n, api, budget, floor, st, 24, 6)
        if len(R) < len(best):
            best = list(R)
            cur = list(R)
            stale = 0
            if on_improve is not None:
                on_improve(best)
        else:
            if len(R) <= len(cur) or (up and len(R) <= len(cur) + 2 and ab_rand(st, 3) == 0):
                cur = R
            stale += 1
        if stale > 30:
            cur = list(best)
            stale = 0
    return best
"""

    if not use_sparse_chiz:
        orch_src = """
def solve(api, lib, budget):
    P0 = list(api["init_parities"])
    n = api["n_qubits"]
    seed = api.get("seed", 0)
    sub = api.get("submit_best")
    def on_imp(P):
        if sub is not None:
            sub(P, "ablation")
    return lib.ab_solve(P0, n, seed, budget, on_imp)
"""
    else:
        orch_src = """
def solve(api, lib, budget):
    P0 = list(api["init_parities"])
    n = api["n_qubits"]
    seed = api.get("seed", 0)
    sub = api.get("submit_best")
    def on_imp(P):
        if sub is not None:
            sub(P, "synth_sparse")
    return lib.ab_solve_sparse(P0, n, api, seed, budget, on_imp)
"""

    mod = LibModule.from_source(
        name=f"mod_{name.lower()}",
        generation=0,
        source=mod_src,
        origin="mechanistic_ablation",
        rationale=name,
    )
    orch = LibModule.from_source(
        name="orchestrator",
        generation=0,
        source=orch_src,
        required_fn="solve",
        origin="mechanistic_ablation",
        rationale=name,
    )
    return CompositionalAlgoArtifact(
        arm=name,
        track="S8_MECHANISTIC",
        generation=0,
        modules=(mod,),
        orchestrator=orch,
    )


def run_study1_mechanistic_and_transfer(out_path: Path) -> Dict[str, Any]:
    """Run 100% offline Study 1:
    Part A: 5-Factor Mechanistic Ablation on S7 Holdout (`N = 44`, `n = 6..8`, 3 seeds)
    Part B: Zero-Shot OOD Scale Transfer + Scientific Synthesis on S8 Holdout (`N = 80`, `n = 8..11`, seed=0 + Lit breakdown)
    """
    t0 = time.perf_counter()
    # --- Part A: Mechanistic Ablation on S7 Holdout (N=44, n=6..8, 3 seeds) ---
    s7_suites = build_s7_benchmarks()
    s7_hold = s7_suites["s7_hold_struct"] + s7_suites["s7_hold_proc_ccz"] + s7_suites["s7_hold_proc_rand"]

    ab_arms = {
        "S7_G3_FULL": build_ablation_artifact("S7_G3_FULL"),
        "NO_M2_BNB": build_ablation_artifact("NO_M2_BNB", use_bnb=False),
        "NO_M3_GRAY_NULL": build_ablation_artifact("NO_M3_GRAY_NULL", use_gray_null=False),
        "NO_M4_PLATEAU": build_ablation_artifact("NO_M4_PLATEAU", use_plateau=False),
        "NO_M5_RM_SPAN4": build_ablation_artifact("NO_M5_RM_SPAN4", use_rm_span4=False),
    }

    part_a_scores: Dict[str, Dict[str, float]] = {k: {} for k in ab_arms}
    part_a_wall: Dict[str, float] = {}
    part_a_ops: Dict[str, int] = {}

    for aname, art in ab_arms.items():
        w0 = time.perf_counter()
        tot_ops = 0
        for task in s7_hold:
            cs = []
            for sd in (0, 1, 2):
                circ, tel = run_s8_artifact(art, task.circuit, seed=sd, v3_budget=DEFAULT_S7_V3_BUDGET)
                cs.append(circ.t_count())
                tot_ops += tel.get("ops_spent", 0)
            part_a_scores[aname][task.task_id] = float(statistics.median(cs))
        part_a_wall[aname] = round(time.perf_counter() - w0, 2)
        part_a_ops[aname] = tot_ops
        tot = sum(part_a_scores[aname].values())
        print(f"[STUDY 1A S7 n=6..8] {aname:18s}: TOT={tot:6.1f} | wall={part_a_wall[aname]:6.2f}s | v3={tot_ops}")

    # Paired Wilcoxon vs S7_G3_FULL
    part_a_stats = {}
    base_vec = [part_a_scores["S7_G3_FULL"][t.task_id] for t in s7_hold]
    for aname in ab_arms:
        if aname == "S7_G3_FULL":
            continue
        vec = [part_a_scores[aname][t.task_id] for t in s7_hold]
        # Positive delta means ablating mechanism HURT (increased T-count)!
        w = paired_wilcoxon_stats([v - b for v, b in zip(vec, base_vec)])
        part_a_stats[aname] = w
        print(f"  Ablation delta ({aname} - FULL): {w['sum_delta']:+6.1f} T-gates | {w['losses']} worse / {w['ties']} tie / {w['wins']} better | p_two={w['p_two']:.6f}")

    # --- Part B: Zero-Shot OOD Scale Transfer + Scientific Synthesis on S8 Holdout (N=80, n=8..11) ---
    s8_suites = build_s8_benchmarks()
    s8_hold = s8_suites["s8_hold_lit"] + s8_suites["s8_hold_proc_ccz"] + s8_suites["s8_hold_proc_rand"]

    part_b_arms = {
        "A0_BASE": None,
        "A1_TPAR": None,
        "A1_TODD_2018": None,
        "A1_FAST_TODD_2022": None,
        "S7_G3_ZERO_SHOT": ab_arms["S7_G3_FULL"],
        "SYNTH_SPARSE_NULL_TODD": build_ablation_artifact("SYNTH_SPARSE_NULL_TODD", use_sparse_chiz=True),
    }

    part_b_scores: Dict[str, Dict[str, int]] = {k: {} for k in part_b_arms}
    part_b_wall: Dict[str, float] = {}
    part_b_ops: Dict[str, int] = {}

    for aname, art in part_b_arms.items():
        w0 = time.perf_counter()
        tot_ops = 0
        for task in s8_hold:
            if aname == "A0_BASE":
                c = task.circuit.t_count()
            elif aname == "A1_TPAR":
                c = tpar_optimize(task.circuit).t_count()
            elif aname == "A1_TODD_2018":
                c = todd_2018_optimize(task.circuit).t_count()
            elif aname == "A1_FAST_TODD_2022":
                c = fast_todd_2022_optimize(task.circuit).t_count()
            else:
                circ, tel = run_s8_artifact(art, task.circuit, seed=0, v3_budget=DEFAULT_S8_V3_BUDGET)
                c = circ.t_count()
                tot_ops += tel.get("ops_spent", 0)
            part_b_scores[aname][task.task_id] = int(c)
        part_b_wall[aname] = round(time.perf_counter() - w0, 2)
        part_b_ops[aname] = tot_ops
        tot = sum(part_b_scores[aname].values())
        lit_tot = sum(part_b_scores[aname][t.task_id] for t in s8_suites["s8_hold_lit"])
        by_q = {
            q: sum(part_b_scores[aname][t.task_id] for t in s8_hold if t.n_qubits == q)
            for q in (8, 9, 10, 11)
        }
        print(f"[STUDY 1B S8 n=8..11] {aname:24s}: TOT={tot:5d} | LIT={lit_tot:4d} | by_q={by_q} | wall={part_b_wall[aname]:6.2f}s | v3={tot_ops}")

    # Paired Wilcoxon for Study 1B
    part_b_stats = {}
    for a, b in [
        ("S7_G3_ZERO_SHOT", "A1_TODD_2018"),
        ("S7_G3_ZERO_SHOT", "A1_FAST_TODD_2022"),
        ("SYNTH_SPARSE_NULL_TODD", "A1_TODD_2018"),
        ("SYNTH_SPARSE_NULL_TODD", "A1_FAST_TODD_2022"),
        ("SYNTH_SPARSE_NULL_TODD", "S7_G3_ZERO_SHOT"),
    ]:
        ds = [part_b_scores[a][t.task_id] - part_b_scores[b][t.task_id] for t in s8_hold]
        w = paired_wilcoxon_stats(ds)
        part_b_stats[f"{a} vs {b}"] = w
        print(f"  [1B] {a} vs {b}: d={w['sum_delta']:+6.1f} | {w['wins']}W/{w['ties']}T/{w['losses']}L | p_two={w['p_two']:.6f}")

    # Per-literature-circuit breakdown
    lit_table = []
    for t in s8_suites["s8_hold_lit"]:
        row = {"task_id": t.task_id, "family": t.family, "n": t.n_qubits}
        for aname in part_b_arms:
            row[aname] = part_b_scores[aname][t.task_id]
        lit_table.append(row)

    out = {
        "elapsed_sec": round(time.perf_counter() - t0, 2),
        "part_a_s7_ablation": {
            "totals": {k: sum(v.values()) for k, v in part_a_scores.items()},
            "wall_sec": part_a_wall,
            "v3_ops": part_a_ops,
            "wilcoxon_vs_full": part_a_stats,
        },
        "part_b_s8_ood_transfer_and_synthesis": {
            "totals": {k: sum(v.values()) for k, v in part_b_scores.items()},
            "lit_totals": {k: sum(part_b_scores[k][t.task_id] for t in s8_suites["s8_hold_lit"]) for k in part_b_arms},
            "by_qubits": {
                k: {str(q): sum(part_b_scores[k][t.task_id] for t in s8_hold if t.n_qubits == q) for q in (8, 9, 10, 11)}
                for k in part_b_arms
            },
            "wall_sec": part_b_wall,
            "v3_ops": part_b_ops,
            "wilcoxon": part_b_stats,
            "lit_table": lit_table,
        },
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


if __name__ == "__main__":
    import sys
    dst = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("S8_STUDY1_MECHANISTIC.json")
    run_study1_mechanistic_and_transfer(dst)
