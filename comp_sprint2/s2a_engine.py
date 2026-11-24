"""Track S2-A Engine: Hard 6-to-8 Input XAG Base Synthesizer, Safe Domain API, A3 & Matched-Compute A5_SHAM.

Every candidate circuit returned by ANY arm (A0, A1, A2, A3, A4, A5) is:
  - Flattened to primitive {AND, XOR} gates with free inversions (ZERO macro-call discount!).
  - Verified 100% bit-exact by exhaustive 64..256-bit truth-table check (`verify_truth_tables`).
  - Strictly bounded by identical per-task wall-clock budget (`time_budget_sec`).
"""
from __future__ import annotations

import random
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple

from comp_sprint.circuit import (
    Gate,
    Macro,
    StrashBuilder,
    XAGCircuit,
    full_mask,
    input_masks,
    verify_truth_tables,
)
from comp_sprint.npn import compose_npn4_wire_map, npn4_canonical
from comp_sprint.sat_exact import sat_exact_synthesize
from comp_sprint.synth_base import (
    _davio_synthesize,
    _enumerate_cuts,
    _eval_cut_tt,
    _splice_single_node,
)
from comp_sprint2.sandbox_exec import AlgoArtifact, AlgoPass, run_monotonic_pipeline


def _fast_cofactor(tt: int, v: int, val: int, mask: int, m1: int) -> int:
    sh = 1 << v
    if val == 0:
        low = tt & (mask ^ m1)
        return low | (low << sh)
    high = tt & m1
    return high | (high >> sh)


def davio_base_6to8(
    n_inputs: int,
    targets: Sequence[int],
    seed: int = 0,
    n_random_orders: int = 2,
) -> XAGCircuit:
    """Arm A0_BASE for Track S2-A: fast deterministic multi-order Shared Davio (handles 6..8 inputs cleanly)."""
    mask = full_mask(n_inputs)
    clean_targets = tuple(t & mask for t in targets)
    rng = random.Random(seed)

    orders: List[Tuple[List[int], bool]] = [
        (list(range(n_inputs)), True),
        (list(reversed(range(n_inputs))), False),
    ]
    for _ in range(n_random_orders):
        o = list(range(n_inputs))
        rng.shuffle(o)
        orders.append((o, False))

    best: Optional[XAGCircuit] = None
    for var_ord, greedy in orders:
        cand, _ = _davio_synthesize(n_inputs, clean_targets, var_ord, use_greedy_var=greedy)
        if best is None or cand.gate_count() < best.gate_count():
            best = cand
    assert best is not None
    assert verify_truth_tables(best, clean_targets)
    return best


def _safe_sat_exact_4in(tt4: int, max_gates: int = 6) -> Optional[XAGCircuit]:
    """Bounded exact CaDiCaL 4-input XAG solver exposed safely to offline evolved passes."""
    tt4 = int(tt4) & 0xFFFF
    mg = max(1, min(6, int(max_gates)))
    return sat_exact_synthesize(4, (tt4,), basis="XAG", min_gates=1, max_gates=mg)


def _safe_sat_exact_multi(n_in: int, targets: Sequence[int], max_gates: int = 5) -> Optional[XAGCircuit]:
    """Bounded exact CaDiCaL multi-output XAG solver (n_in <= 4, n_out <= 2, max_gates <= 5)."""
    n_in = int(n_in)
    if not (2 <= n_in <= 4) or not (1 <= len(targets) <= 2):
        return None
    mg = max(1, min(5, int(max_gates)))
    m = full_mask(n_in)
    return sat_exact_synthesize(n_in, tuple(int(t) & m for t in targets), basis="XAG", min_gates=1, max_gates=mg)


def _safe_davio(n_inputs: int, targets: Sequence[int], var_order: Sequence[int], greedy: bool = False) -> XAGCircuit:
    n_inputs = int(n_inputs)
    m = full_mask(n_inputs)
    c, _ = _davio_synthesize(n_inputs, tuple(int(t) & m for t in targets), list(var_order), use_greedy_var=bool(greedy))
    return c


def _safe_splice_cut(circ: XAGCircuit, target_nid: int, leaves: Sequence[int], repl_circ: XAGCircuit) -> Optional[XAGCircuit]:
    """Replace `target_nid` (whose exact function on `leaves` equals `repl_circ`) cleanly via StrashBuilder."""
    k = len(leaves)
    if k != repl_circ.n_inputs or len(repl_circ.outputs) != 1:
        return None
    n_in = circ.n_inputs
    b = StrashBuilder(n_in)
    nmap: Dict[int, Tuple[int, bool]] = {-1: (-1, False)}
    for i in range(n_in):
        nmap[i] = (i, False)
    for gi, g in enumerate(circ.gates):
        nid = n_in + gi
        if nid == target_nid:
            rmap: Dict[int, Tuple[int, bool]] = {-1: (-1, False)}
            for j, lf in enumerate(leaves):
                rmap[j] = nmap[lf]
            for rgi, rg in enumerate(repl_circ.gates):
                ln, li = rmap[rg.left]
                rn, ri = rmap[rg.right]
                rmap[k + rgi] = b.add_gate(rg.op, ln, li ^ rg.left_inv, rn, ri ^ rg.right_inv)
            ro_n, ro_i = repl_circ.outputs[0]
            nmap[nid] = (rmap[ro_n][0], rmap[ro_n][1] ^ ro_i)
        else:
            ln, li = nmap[g.left]
            rn, ri = nmap[g.right]
            nmap[nid] = b.add_gate(g.op, ln, li ^ g.left_inv, rn, ri ^ g.right_inv)
    final_outs = [(nmap[on][0], nmap[on][1] ^ oi) for on, oi in circ.outputs]
    return b.build(final_outs, prune_dead=True)


def _safe_splice_npn4(
    circ: XAGCircuit,
    target_nid: int,
    leaves: Tuple[int, ...],
    canon_circ: XAGCircuit,
    cut_tt4: int,
) -> Optional[XAGCircuit]:
    """Replace `target_nid` on `leaves` (len 2..4) with NPN4-equivalent `canon_circ`."""
    if canon_circ.n_inputs != 4 or len(canon_circ.outputs) != 1:
        return None
    m_tt4 = canon_circ.truth_tables()[0] & 0xFFFF
    mapping = compose_npn4_wire_map(cut_tt4 & 0xFFFF, m_tt4)
    if mapping is None:
        return None
    src_idx, src_inv, out_inv = mapping
    macro = Macro.from_circuit("tmp", canon_circ)
    return _splice_single_node(circ, target_nid, tuple(leaves), macro, src_idx, src_inv, out_inv)


def _safe_cone_size(circ: XAGCircuit, root_nid: int, leaves: Sequence[int]) -> int:
    lset = set(leaves)
    seen = set()
    stack = [root_nid]
    n_in = circ.n_inputs
    while stack:
        u = stack.pop()
        if u in seen or u in lset or u < n_in:
            continue
        seen.add(u)
        g = circ.gates[u - n_in]
        stack.append(g.left)
        stack.append(g.right)
    return len(seen)


def _safe_node_tts(circ: XAGCircuit) -> Dict[int, int]:
    """Compute exact full truth-table bitmask for every node (-1, inputs, gates) in `circ`."""
    n_in = circ.n_inputs
    mask = full_mask(n_in)
    in_tts = input_masks(n_in)
    tts: Dict[int, int] = {-1: 0}
    for i in range(n_in):
        tts[i] = in_tts[i]
    for gi, g in enumerate(circ.gates):
        lv = tts[g.left] ^ (mask if g.left_inv else 0)
        rv = tts[g.right] ^ (mask if g.right_inv else 0)
        tts[n_in + gi] = (lv & rv) if g.op == "AND" else (lv ^ rv)
    return tts


def build_xag_domain_api() -> Dict[str, Any]:
    """Whitelisted domain API injected into sandboxed Track S2-A `AlgoPass` functions."""
    return {
        "Gate": Gate,
        "StrashBuilder": StrashBuilder,
        "XAGCircuit": XAGCircuit,
        "full_mask": full_mask,
        "input_masks": input_masks,
        "npn4_canonical": npn4_canonical,
        "sat_exact_4in": _safe_sat_exact_4in,
        "sat_exact_multi": _safe_sat_exact_multi,
        "davio_synth": _safe_davio,
        "enumerate_cuts": _enumerate_cuts,
        "eval_cut_tt": _eval_cut_tt,
        "splice_cut": _safe_splice_cut,
        "splice_npn4": _safe_splice_npn4,
        "cone_size": _safe_cone_size,
        "node_tts": _safe_node_tts,
        "verify_truth_tables": verify_truth_tables,
    }


# ---------------- Deterministic Arm A3_ZERO_LLM & Matched-Compute Arm A5_SHAM ----------------

_A3_DET_SAT_CUT_PASS = """
def optimize(circ, n_inputs, targets, seed, deadline):
    # Deterministic zero-LLM exact 4-cut CaDiCaL resynthesis pass (with NPN4 cache)
    best = circ
    npn_cache = {}
    for _round in range(4):
        if time.perf_counter() >= deadline:
            break
        improved = False
        cuts = enumerate_cuts(best, max_k=4, max_cuts_per_node=16)
        n_in = best.n_inputs
        # Inspect highest-volume bloated 4-cuts first
        cands = []
        for gi in range(best.gate_count() - 1, -1, -1):
            nid = n_in + gi
            for lf in cuts.get(nid, ()):
                if len(lf) < 3:
                    continue
                cs = cone_size(best, nid, lf)
                if cs >= 4:
                    cands.append((cs, nid, lf))
        cands.sort(key=lambda x: x[0], reverse=True)
        for cs, nid, lf in cands[:40]:
            if time.perf_counter() >= deadline:
                break
            tt4 = eval_cut_tt(best, nid, lf)
            if tt4 is None:
                continue
            c = npn4_canonical(tt4)
            if c in (0x0000, 0x00FF, 0x000F, 0x0FF0):
                continue
            if c not in npn_cache:
                npn_cache[c] = sat_exact_4in(c, max_gates=min(cs - 1, 5))
            opt = npn_cache[c]
            if opt is None or opt.gate_count() >= cs:
                continue
            cand = splice_npn4(best, nid, lf, opt, tt4)
            if cand is not None and cand.gate_count() < best.gate_count():
                if verify_truth_tables(cand, targets):
                    best = cand
                    improved = True
                    break
        if not improved:
            break
    return best
"""

_A5_SHAM_RANDOM_COMPUTE_PASS = """
def optimize(circ, n_inputs, targets, seed, deadline):
    # True full-budget matched-compute SHAM baseline: burns the ENTIRE wall-clock
    # deadline doing unguided random Davio variable-order restarts (zero domain evolution).
    rng = random.Random(seed * 10007 + 31337)
    best = circ
    base_ord = list(range(n_inputs))
    iters = 0
    while time.perf_counter() < deadline:
        iters += 1
        ord_i = list(base_ord)
        rng.shuffle(ord_i)
        cand = davio_synth(n_inputs, targets, ord_i, greedy=(iters % 5 == 0))
        if cand.gate_count() < best.gate_count():
            best = cand
    return best
"""


def build_s2a_a3_artifact() -> AlgoArtifact:
    p = AlgoPass.from_source(
        name="det_npn4_sat_cut_rewrite",
        track="S2A_XAG",
        source=_A3_DET_SAT_CUT_PASS,
        origin="zero_llm_baseline",
        rationale="Deterministic zero-LLM exact 4-cut CaDiCaL resynthesis baseline.",
    )
    return AlgoArtifact(arm="A3_ZERO_LLM", track="S2A_XAG", generation=1, passes=(p,))


def build_s2a_a5_sham_artifact() -> AlgoArtifact:
    p = AlgoPass.from_source(
        name="sham_random_davio_restarts",
        track="S2A_XAG",
        source=_A5_SHAM_RANDOM_COMPUTE_PASS,
        origin="sham_matched_compute",
        rationale="Matched-compute random Davio restarts baseline.",
    )
    return AlgoArtifact(arm="A5_SHAM", track="S2A_XAG", generation=1, passes=(p,))


def synthesize_s2a_with_artifact(
    n_inputs: int,
    targets: Sequence[int],
    artifact: Optional[AlgoArtifact],
    seed: int = 0,
    time_budget_sec: float = 0.60,
) -> Tuple[XAGCircuit, Dict[str, Any]]:
    """Unified strictly-monotonic Track S2-A evaluator (identical across ALL arms!)."""
    mask = full_mask(n_inputs)
    clean_targets = tuple(t & mask for t in targets)
    base = davio_base_6to8(n_inputs, clean_targets, seed=seed)
    if artifact is None or not artifact.passes:
        return base, {"final_cost": base.gate_count(), "elapsed_sec": 0.0, "pass_stats": []}

    api = build_xag_domain_api()
    best, meta = run_monotonic_pipeline(
        initial_solution=base,
        passes=artifact.passes,
        domain_api=api,
        call_args_fn=lambda cur, dl: (cur, n_inputs, clean_targets, seed, dl),
        verify_fn=lambda c: isinstance(c, XAGCircuit) and c.n_inputs == n_inputs and verify_truth_tables(c, clean_targets),
        cost_fn=lambda c: int(c.gate_count()),
        time_budget_sec=time_budget_sec,
    )
    assert verify_truth_tables(best, clean_targets)
    return best, meta
