"""Track S2-B Engine: Verified 8/16-Bit Bit-Vector Superoptimizer Base, Safe Domain API, A3 & A5_SHAM.

Every candidate `BVProgram` returned by ANY arm (A0, A1, A2, A3, A4, A5) is:
  - Measured strictly in live primitive BV ops (`op_count()`, ZERO artificial macro discount!).
  - Proven 100% mathematically equivalent to `spec` across ALL inputs via exact Z3 `UNSAT`!
  - Strictly bounded by identical per-task wall-clock budget (`time_budget_sec`).
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Sequence, Tuple

from comp_sprint2.s2b_bv import (
    ALL_BV_OPS,
    BINARY_OPS,
    BVBuilder,
    BVNode,
    BVProgram,
    UNARY_OPS,
    default_test_vectors,
    simplify_bv_with_z3_industry,
    verify_bv_equiv_z3,
)
from comp_sprint2.sandbox_exec import AlgoArtifact, AlgoPass, run_monotonic_pipeline


def bv_base_simplify(spec: BVProgram) -> BVProgram:
    """Arm A0_BASE: basic local constant folding, structural hashing, and trivial 1-op identities."""
    b = BVBuilder(spec.width, spec.n_inputs, fold_constants=True)
    nmap: Dict[int, int] = {}
    for idx, nd in enumerate(spec.nodes):
        if nd.op == "IN":
            nmap[idx] = b.inp(nd.args[0])
        elif nd.op == "CONST":
            nmap[idx] = b.const(nd.args[0])
        else:
            nmap[idx] = b.op(nd.op, *[nmap[a] for a in nd.args])
    cand = b.build(nmap[spec.out_id])
    if cand.op_count() < spec.op_count():
        ok, _ = verify_bv_equiv_z3(spec, cand)
        if ok:
            return cand
    return spec


def _safe_replace_node(prog: BVProgram, target_idx: int, repl: BVProgram, arg_map: Sequence[int]) -> Optional[BVProgram]:
    """Replace node `target_idx` in `prog` with `repl` wired to `arg_map` nodes (strictly sound DAG splice)."""
    if repl.width != prog.width or len(arg_map) != repl.n_inputs:
        return None
    b = BVBuilder(prog.width, prog.n_inputs, fold_constants=True)
    nmap: Dict[int, int] = {}
    for idx, nd in enumerate(prog.nodes):
        if idx == target_idx:
            rmap: Dict[int, int] = {}
            for r_idx, rnd in enumerate(repl.nodes):
                if rnd.op == "IN":
                    src = arg_map[rnd.args[0]]
                    if src not in nmap:
                        return None
                    rmap[r_idx] = nmap[src]
                elif rnd.op == "CONST":
                    rmap[r_idx] = b.const(rnd.args[0])
                else:
                    rmap[r_idx] = b.op(rnd.op, *[rmap[a] for a in rnd.args])
            nmap[idx] = rmap[repl.out_id]
        else:
            if nd.op == "IN":
                nmap[idx] = b.inp(nd.args[0])
            elif nd.op == "CONST":
                nmap[idx] = b.const(nd.args[0])
            else:
                nmap[idx] = b.op(nd.op, *[nmap[a] for a in nd.args])
    return b.build(nmap[prog.out_id])


def _safe_eval_all_nodes(prog: BVProgram, test_vectors: Sequence[Tuple[int, ...]]) -> List[Tuple[int, ...]]:
    """Compute concrete output tuple across `test_vectors` for EVERY node in `prog` simultaneously."""
    w = prog.width
    mask = (1 << w) - 1
    sign_bit = 1 << (w - 1)
    n_v = len(test_vectors)
    node_vecs: List[List[int]] = []
    for nd in prog.nodes:
        op = nd.op
        if op == "IN":
            i = nd.args[0]
            node_vecs.append([tv[i] & mask for tv in test_vectors])
        elif op == "CONST":
            c = nd.args[0] & mask
            node_vecs.append([c] * n_v)
        elif op == "NOT":
            a = node_vecs[nd.args[0]]
            node_vecs.append([(~v) & mask for v in a])
        elif op == "NEG":
            a = node_vecs[nd.args[0]]
            node_vecs.append([(-v) & mask for v in a])
        elif op == "AND":
            a, c = node_vecs[nd.args[0]], node_vecs[nd.args[1]]
            node_vecs.append([a[k] & c[k] for k in range(n_v)])
        elif op == "OR":
            a, c = node_vecs[nd.args[0]], node_vecs[nd.args[1]]
            node_vecs.append([a[k] | c[k] for k in range(n_v)])
        elif op == "XOR":
            a, c = node_vecs[nd.args[0]], node_vecs[nd.args[1]]
            node_vecs.append([a[k] ^ c[k] for k in range(n_v)])
        elif op == "ADD":
            a, c = node_vecs[nd.args[0]], node_vecs[nd.args[1]]
            node_vecs.append([(a[k] + c[k]) & mask for k in range(n_v)])
        elif op == "SUB":
            a, c = node_vecs[nd.args[0]], node_vecs[nd.args[1]]
            node_vecs.append([(a[k] - c[k]) & mask for k in range(n_v)])
        elif op == "MUL":
            a, c = node_vecs[nd.args[0]], node_vecs[nd.args[1]]
            node_vecs.append([(a[k] * c[k]) & mask for k in range(n_v)])
        elif op == "SHL":
            a, c = node_vecs[nd.args[0]], node_vecs[nd.args[1]]
            node_vecs.append([((a[k] << c[k]) & mask) if c[k] < w else 0 for k in range(n_v)])
        elif op == "LSHR":
            a, c = node_vecs[nd.args[0]], node_vecs[nd.args[1]]
            node_vecs.append([(a[k] >> c[k]) if c[k] < w else 0 for k in range(n_v)])
        elif op == "ASHR":
            a, c = node_vecs[nd.args[0]], node_vecs[nd.args[1]]
            out = []
            for k in range(n_v):
                sa = a[k] - (1 << w) if (a[k] & sign_bit) else a[k]
                out.append((mask if sa < 0 else 0) if c[k] >= w else ((sa >> c[k]) & mask))
            node_vecs.append(out)
        elif op == "ULT":
            a, c = node_vecs[nd.args[0]], node_vecs[nd.args[1]]
            node_vecs.append([1 if a[k] < c[k] else 0 for k in range(n_v)])
        elif op == "EQ":
            a, c = node_vecs[nd.args[0]], node_vecs[nd.args[1]]
            node_vecs.append([1 if a[k] == c[k] else 0 for k in range(n_v)])
        elif op == "ITE":
            cond, t_v, f_v = node_vecs[nd.args[0]], node_vecs[nd.args[1]], node_vecs[nd.args[2]]
            node_vecs.append([t_v[k] if cond[k] != 0 else f_v[k] for k in range(n_v)])
    return [tuple(v) for v in node_vecs]


def _safe_verify_equiv(spec: BVProgram, cand: BVProgram) -> Tuple[bool, Optional[Tuple[int, ...]]]:
    return verify_bv_equiv_z3(spec, cand, timeout_ms=800)


def build_bv_domain_api() -> Dict[str, Any]:
    """Whitelisted domain API injected into sandboxed Track S2-B `AlgoPass` functions."""
    return {
        "BVBuilder": BVBuilder,
        "BVNode": BVNode,
        "BVProgram": BVProgram,
        "UNARY_OPS": UNARY_OPS,
        "BINARY_OPS": BINARY_OPS,
        "ALL_BV_OPS": ALL_BV_OPS,
        "default_test_vectors": default_test_vectors,
        "eval_all_nodes": _safe_eval_all_nodes,
        "replace_node": _safe_replace_node,
        "verify_equiv_z3": _safe_verify_equiv,
    }


# ---------------- Deterministic Arm A3_ZERO_LLM & Matched-Compute Arm A5_SHAM ----------------

_A3_DET_CEGIS_PASS = """
def optimize(prog, spec, seed, deadline):
    # Deterministic zero-LLM bottom-up size-1..2 enumerative CEGIS superoptimizer (whole-program)
    w = prog.width
    n_in = prog.n_inputs
    mask = (1 << w) - 1
    tvs = list(default_test_vectors(w, n_in, seed=seed + 11, n_rand=20))
    target_sig = spec.eval_vectors(tvs)
    best = prog
    if best.op_count() <= 1:
        return best

    # Pool of (expr_prog, vec_tuple) ordered by op_count
    seen = {}
    pool_by_size = {0: [], 1: [], 2: []}

    def add_cand(p):
        oc = p.op_count()
        if oc >= best.op_count():
            return None
        sig = p.eval_vectors(tvs)
        if sig == target_sig:
            ok, ce = verify_equiv_z3(spec, p)
            if ok:
                return p
            if ce is not None:
                tvs.append(ce)
        if sig not in seen and oc <= 2:
            seen[sig] = p
            pool_by_size[oc].append((p, sig))
        return None

    # Size 0: inputs + tiny constants
    for i in range(n_in):
        b = BVBuilder(w, n_in)
        r = add_cand(b.build(b.inp(i)))
        if r is not None:
            return r
    for c in (0, 1, mask):
        b = BVBuilder(w, n_in)
        r = add_cand(b.build(b.const(c)))
        if r is not None:
            return r

    bin_ops = ("AND", "OR", "XOR", "ADD", "SUB")
    un_ops = ("NOT", "NEG")

    def build_u(op, p0):
        b = BVBuilder(w, n_in)
        nmap = {}
        for idx, nd in enumerate(p0.nodes):
            nmap[idx] = b.inp(nd.args[0]) if nd.op == "IN" else (b.const(nd.args[0]) if nd.op == "CONST" else b.op(nd.op, *[nmap[a] for a in nd.args]))
        return b.build(b.op(op, nmap[p0.out_id]))

    def build_b(op, p0, p1):
        b = BVBuilder(w, n_in)
        m0, m1 = {}, {}
        for idx, nd in enumerate(p0.nodes):
            m0[idx] = b.inp(nd.args[0]) if nd.op == "IN" else (b.const(nd.args[0]) if nd.op == "CONST" else b.op(nd.op, *[m0[a] for a in nd.args]))
        for idx, nd in enumerate(p1.nodes):
            m1[idx] = b.inp(nd.args[0]) if nd.op == "IN" else (b.const(nd.args[0]) if nd.op == "CONST" else b.op(nd.op, *[m1[a] for a in nd.args]))
        return b.build(b.op(op, m0[p0.out_id], m1[p1.out_id]))

    # Size 1
    for p0, _ in list(pool_by_size[0]):
        if time.perf_counter() >= deadline:
            return best
        for op in un_ops:
            r = add_cand(build_u(op, p0))
            if r is not None:
                best = r
                if best.op_count() <= 1:
                    return best
    for i, (p0, _) in enumerate(list(pool_by_size[0])):
        for j, (p1, _) in enumerate(list(pool_by_size[0])):
            if time.perf_counter() >= deadline:
                return best
            for op in bin_ops:
                if op in ("AND", "OR", "XOR", "ADD") and j < i:
                    continue
                r = add_cand(build_b(op, p0, p1))
                if r is not None:
                    best = r
                    if best.op_count() <= 1:
                        return best

    # Size 2 (1-op combined with 0-op)
    if best.op_count() > 2:
        for p1, _ in list(pool_by_size[1]):
            if time.perf_counter() >= deadline:
                return best
            for op in un_ops:
                r = add_cand(build_u(op, p1))
                if r is not None:
                    best = r
                    if best.op_count() <= 2:
                        return best
            for p0, _ in list(pool_by_size[0]):
                if time.perf_counter() >= deadline:
                    return best
                for op in bin_ops:
                    for a, c in ((p1, p0), (p0, p1)):
                        if op in ("AND", "OR", "XOR", "ADD") and a is p0:
                            continue
                        r = add_cand(build_b(op, a, c))
                        if r is not None:
                            best = r
                            if best.op_count() <= 2:
                                return best
    return best
"""

_A5_SHAM_RANDOM_BV_PASS = """
def optimize(prog, spec, seed, deadline):
    # Matched-compute SHAM baseline: spends the exact same wall-clock budget sampling
    # random short BV programs (1..3 ops) and checking against concrete test vectors + Z3.
    w = prog.width
    n_in = prog.n_inputs
    mask = (1 << w) - 1
    rng = random.Random(seed * 10007 + 91919)
    tvs = default_test_vectors(w, n_in, seed=seed + 3, n_rand=20)
    target_sig = spec.eval_vectors(tvs)
    best = prog
    ops = ("AND", "OR", "XOR", "ADD", "SUB", "NOT", "NEG", "SHL", "LSHR")
    iters = 0
    while time.perf_counter() < deadline and iters < 2500:
        iters += 1
        target_len = rng.randint(1, min(3, max(1, best.op_count() - 1)))
        b = BVBuilder(w, n_in)
        pool = [b.inp(i) for i in range(n_in)] + [b.const(0), b.const(1), b.const(mask)]
        for _ in range(target_len):
            op = rng.choice(ops)
            if op in ("NOT", "NEG"):
                nd = b.op(op, rng.choice(pool))
            else:
                nd = b.op(op, rng.choice(pool), rng.choice(pool))
            pool.append(nd)
        cand = b.build(pool[-1])
        if cand.op_count() < best.op_count() and cand.eval_vectors(tvs) == target_sig:
            ok, _ = verify_equiv_z3(spec, cand)
            if ok:
                best = cand
    return best
"""


def build_s2b_a3_artifact() -> AlgoArtifact:
    p = AlgoPass.from_source(
        name="det_cegis_size2_enumerator",
        track="S2B_BV",
        source=_A3_DET_CEGIS_PASS,
        origin="zero_llm_baseline",
        rationale="Deterministic zero-LLM bottom-up CEGIS enumerator up to size 2.",
    )
    return AlgoArtifact(arm="A3_ZERO_LLM", track="S2B_BV", generation=1, passes=(p,))


def build_s2b_a5_sham_artifact() -> AlgoArtifact:
    p = AlgoPass.from_source(
        name="sham_random_bv_sampler",
        track="S2B_BV",
        source=_A5_SHAM_RANDOM_BV_PASS,
        origin="sham_matched_compute",
        rationale="Matched-compute random BV expression sampler baseline.",
    )
    return AlgoArtifact(arm="A5_SHAM", track="S2B_BV", generation=1, passes=(p,))


def optimize_s2b_with_artifact(
    spec: BVProgram,
    artifact: Optional[AlgoArtifact],
    seed: int = 0,
    time_budget_sec: float = 0.80,
) -> Tuple[BVProgram, Dict[str, Any]]:
    """Unified strictly-monotonic Track S2-B evaluator (identical across ALL arms!)."""
    base = bv_base_simplify(spec)
    if artifact is None or not artifact.passes:
        return base, {"final_cost": base.op_count(), "elapsed_sec": 0.0, "pass_stats": []}

    api = build_bv_domain_api()
    best, meta = run_monotonic_pipeline(
        initial_solution=base,
        passes=artifact.passes,
        domain_api=api,
        call_args_fn=lambda cur, dl: (cur, spec, seed, dl),
        verify_fn=lambda p: isinstance(p, BVProgram) and verify_bv_equiv_z3(spec, p, timeout_ms=2000)[0],
        cost_fn=lambda p: int(p.op_count()),
        time_budget_sec=time_budget_sec,
    )
    if best.sha256() != base.sha256():
        ok, _ = verify_bv_equiv_z3(spec, best, timeout_ms=5000)
        if not ok:
            # Strict fail-closed on transient Z3 unknown/timeout: fall back monotonically to proven `base`
            best = base
    return best, meta
