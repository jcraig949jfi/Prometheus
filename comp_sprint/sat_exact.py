"""Exact Boolean circuit synthesis via CaDiCaL (PySAT) and independent exact BFS.

Uses Knuth/Haaswijk normal-gate 3-variable SAT encoding (f(0,0)=0, fixed output
polarity from target bit 0, no-reapplication C5 for XAG, co-lexicographic C4 for
single-output) for fast provable optimality.

Supports:
  - basis="XAG": {AND, XOR} + free wire inversions (exact match to Knuth B_2!)
  - basis="AIG": {AND} + free wire inversions (exact match to Berkeley ABC AIG nodes!)
"""
from __future__ import annotations

import time
from typing import Dict, List, Optional, Sequence, Tuple

from pysat.solvers import Solver

from comp_sprint.circuit import Gate, StrashBuilder, XAGCircuit, full_mask, input_masks
from comp_sprint.npn import npn4_table

# Map normal-gate triple (f01, f10, f11) with f00=0 to (op, left_inv, right_inv, out_inv)
_NORMAL_TRIPLE_TO_GATE = {
    (0, 0, 1): ("AND", False, False, False),  # a & b
    (1, 0, 0): ("AND", True, False, False),   # ~a & b
    (0, 1, 0): ("AND", False, True, False),   # a & ~b
    (1, 1, 1): ("AND", True, True, True),     # a | b == ~(~a & ~b)
    (1, 1, 0): ("XOR", False, False, False),  # a ^ b
}


def _sat_synthesize_fixed_k(
    n_inputs: int,
    targets: Sequence[int],
    k_gates: int,
    basis: str = "XAG",
    solver_name: str = "cadical195",
    meter: Optional[object] = None,
    phase: str = "sat_exact",
) -> Optional[XAGCircuit]:
    """Return an exact k_gates circuit realizing `targets`, or None if UNSAT."""
    if basis not in ("XAG", "AIG"):
        raise ValueError(f"Unsupported basis: {basis!r}")
    mask = full_mask(n_inputs)
    n_rows = 1 << n_inputs
    n_outs = len(targets)
    in_tts = input_masks(n_inputs)

    # Normalize every target so bit 0 is 0 (recording required final output inversion).
    raw_targets = [t & mask for t in targets]
    out_invs = [bool(t & 1) for t in raw_targets]
    norm_targets = [(t ^ mask) if inv else t for t, inv in zip(raw_targets, out_invs)]

    # Fast exact k=0 check (constants and primary inputs, all normalized to bit0 == 0)
    if k_gates == 0:
        zero_map: Dict[int, int] = {0: -1}
        for i, tt in enumerate(in_tts):
            zero_map[tt] = i  # input_masks always have bit 0 == 0
        outs = []
        for nt, oinv in zip(norm_targets, out_invs):
            if nt not in zero_map:
                return None
            outs.append((zero_map[nt], oinv))
        return XAGCircuit(n_inputs=n_inputs, gates=(), outputs=tuple(outs))

    nxt = 1

    def new_var() -> int:
        nonlocal nxt
        v = nxt
        nxt += 1
        return v

    # x[i][t] for t in 1..n_rows-1 (t=0 is identically 0 by normal-gate induction)
    x = [{t: new_var() for t in range(1, n_rows)} for _ in range(k_gates)]

    # Fanin pair selectors s[i][(j, l)] for 0 <= j < l < n_inputs + i
    s: List[Dict[Tuple[int, int], int]] = []
    for i in range(k_gates):
        d: Dict[Tuple[int, int], int] = {}
        limit = n_inputs + i
        for j in range(limit):
            for l in range(j + 1, limit):
                d[(j, l)] = new_var()
        s.append(d)

    # Normal gate function bits (f01, f10, f11) per gate (f00 = 0 fixed)
    f01 = [new_var() for _ in range(k_gates)]
    f10 = [new_var() for _ in range(k_gates)]
    f11 = [new_var() for _ in range(k_gates)]

    # Output selectors o[h][node] for node in {-1, 0..n_inputs+k-1}
    all_nodes = [-1] + list(range(n_inputs + k_gates))
    o = [{nd: new_var() for nd in all_nodes} for _ in range(n_outs)]

    clauses: List[List[int]] = []

    def exactly_one(vlist: Sequence[int]) -> None:
        clauses.append(list(vlist))
        for a_idx in range(len(vlist)):
            va = vlist[a_idx]
            for b_idx in range(a_idx + 1, len(vlist)):
                clauses.append([-va, -vlist[b_idx]])

    # 1. Each gate chooses exactly one fanin pair and a valid non-trivial normal function
    for i in range(k_gates):
        exactly_one(list(s[i].values()))
        # Forbid CONST0 (0,0,0), proj-a (0,1,1), proj-b (1,0,1)
        clauses.append([f01[i], f10[i], f11[i]])
        clauses.append([f01[i], -f10[i], -f11[i]])
        clauses.append([-f01[i], f10[i], -f11[i]])
        if basis == "AIG":
            # Also forbid XOR (1,1,0)
            clauses.append([-f01[i], -f10[i], f11[i]])

    # 2. Output matching
    for h, nt in enumerate(norm_targets):
        exactly_one([o[h][nd] for nd in all_nodes])
        for nd in all_nodes:
            ov = o[h][nd]
            if nd == -1:
                if nt != 0:
                    clauses.append([-ov])
            elif nd < n_inputs:
                if nt != in_tts[nd]:
                    clauses.append([-ov])
            else:
                gi = nd - n_inputs
                for t in range(1, n_rows):
                    want = (nt >> t) & 1
                    clauses.append([-ov, x[gi][t] if want else -x[gi][t]])

    # 3. Main simulation constraints (only rows t = 1..n_rows-1)
    for i in range(k_gates):
        v01, v10, v11 = f01[i], f10[i], f11[i]
        xi_map = x[i]
        for (j, l), svar in s[i].items():
            for t in range(1, n_rows):
                xi = xi_map[t]
                if j < n_inputs:
                    j_cases = [((t >> j) & 1, [])]
                else:
                    jv = x[j - n_inputs][t]
                    j_cases = [(0, [jv]), (1, [-jv])]

                if l < n_inputs:
                    l_cases = [((t >> l) & 1, [])]
                else:
                    lv = x[l - n_inputs][t]
                    l_cases = [(0, [lv]), (1, [-lv])]

                for a_bit, a_cl in j_cases:
                    for b_bit, b_cl in l_cases:
                        prefix = [-svar] + a_cl + b_cl
                        if a_bit == 0 and b_bit == 0:
                            # f(0,0) = 0 => xi = 0
                            clauses.append(prefix + [-xi])
                        else:
                            fvar = v01 if (a_bit == 0 and b_bit == 1) else (v10 if (a_bit == 1 and b_bit == 0) else v11)
                            clauses.append(prefix + [-fvar, xi])
                            clauses.append(prefix + [fvar, -xi])

    # 4. Sound symmetry breaking:
    # (C2) Every gate must be used by a later gate or an output.
    for i in range(k_gates):
        nid = n_inputs + i
        users: List[int] = [o[h][nid] for h in range(n_outs)]
        for i2 in range(i + 1, k_gates):
            for (j, l), svar in s[i2].items():
                if j == nid or l == nid:
                    users.append(svar)
        clauses.append(users)

    # (C5) No-reapplication (provably sound for XAG = B_2):
    # If gate i has fanins (j, l), no later gate i2 may take (j, nid_i) or (l, nid_i).
    if basis == "XAG":
        for i in range(k_gates):
            nid_i = n_inputs + i
            for (j, l), s_i in s[i].items():
                for i2 in range(i + 1, k_gates):
                    s_bad1 = s[i2].get((j, nid_i))
                    if s_bad1 is not None:
                        clauses.append([-s_i, -s_bad1])
                    s_bad2 = s[i2].get((l, nid_i))
                    if s_bad2 is not None:
                        clauses.append([-s_i, -s_bad2])

    # Single-output tightening: last gate is output + co-lexicographic ordering (C4)
    if n_outs == 1:
        clauses.append([o[0][n_inputs + k_gates - 1]])
        for i in range(k_gates - 1):
            nid_i = n_inputs + i
            for (j1, l1), s1 in s[i].items():
                for (j2, l2), s2 in s[i + 1].items():
                    if j2 == nid_i or l2 == nid_i:
                        continue
                    if (l2, j2) < (l1, j1):
                        clauses.append([-s1, -s2])

    t0 = time.perf_counter()
    with Solver(name=solver_name, bootstrap_with=clauses) as solver:
        sat = solver.solve()
        model = solver.get_model() if sat else None
    dt = time.perf_counter() - t0
    if meter is not None:
        meter.charge_sat_call(dt, phase=phase)

    if not sat or model is None:
        return None

    mset = set(v for v in model if v > 0)
    # Reconstruct primitive XAG circuit pushing any OR-gate (1,1,1) output inversion forward.
    builder = StrashBuilder(n_inputs)
    node_map: Dict[int, Tuple[int, bool]] = {-1: (-1, False)}
    for i in range(n_inputs):
        node_map[i] = (i, False)

    for i in range(k_gates):
        j, l = next(pair for pair, v in s[i].items() if v in mset)
        triple = (int(f01[i] in mset), int(f10[i] in mset), int(f11[i] in mset))
        op, li, ri, go_inv = _NORMAL_TRIPLE_TO_GATE[triple]
        ln, l_cur_inv = node_map[j]
        rn, r_cur_inv = node_map[l]
        gn, g_inv = builder.add_gate(op, ln, l_cur_inv ^ li, rn, r_cur_inv ^ ri)
        node_map[n_inputs + i] = (gn, g_inv ^ go_inv)

    outs_res: List[Tuple[int, bool]] = []
    for h in range(n_outs):
        chosen_nd = next(nd for nd, v in o[h].items() if v in mset)
        mn, m_inv = node_map[chosen_nd]
        outs_res.append((mn, m_inv ^ out_invs[h]))

    circ = builder.build(outs_res, prune_dead=True)
    assert circ.truth_tables() == tuple(raw_targets), "SAT model failed truth-table self-check!"
    assert circ.gate_count() <= k_gates
    return circ


def sat_exact_synthesize(
    n_inputs: int,
    targets: Sequence[int],
    basis: str = "XAG",
    max_gates: int = 8,
    min_gates: int = 0,
    solver_name: str = "cadical195",
    meter: Optional[object] = None,
    phase: str = "sat_exact",
) -> Optional[XAGCircuit]:
    """Iteratively search k = min_gates .. max_gates for a provably minimum-gate circuit."""
    for k in range(min_gates, max_gates + 1):
        circ = _sat_synthesize_fixed_k(
            n_inputs=n_inputs,
            targets=targets,
            k_gates=k,
            basis=basis,
            solver_name=solver_name,
            meter=meter,
            phase=phase,
        )
        if circ is not None:
            return circ
    return None


def exact_bfs_4input(basis: str = "XAG", max_gates: int = 4) -> Dict[int, int]:
    """Independent exact bottom-up DAG BFS over 4-input NPN classes up to `max_gates`."""
    if basis not in ("XAG", "AIG"):
        raise ValueError(f"Unsupported basis: {basis!r}")
    if max_gates > 4:
        raise ValueError("exact_bfs_4input is intended for max_gates <= 4 calibration")

    tbl = npn4_table()
    mask = 0xFFFF
    in_tts = input_masks(4)
    best: Dict[int, int] = {}

    def record(tt: int, k: int) -> None:
        c = int(tbl[tt & mask])
        if c not in best or k < best[c]:
            best[c] = k

    record(0, 0)
    for t in in_tts:
        record(t, 0)
    if max_gates == 0:
        return best

    def gate_outputs(a: int, b: int) -> Tuple[int, ...]:
        na = a ^ mask
        nb = b ^ mask
        if basis == "XAG":
            return (a & b, na & b, a & nb, na & nb, a ^ b)
        return (a & b, na & b, a & nb, na & nb)

    def norm_tt(tt: int) -> int:
        return (tt ^ mask) if (tt & 1) else tt

    base_nodes = tuple(norm_tt(t) for t in in_tts)
    base_set = set(base_nodes) | {0}

    first_gates = (
        (norm_tt(in_tts[0] & in_tts[1]), norm_tt(in_tts[0] ^ in_tts[1]))
        if basis == "XAG"
        else (norm_tt(in_tts[0] & in_tts[1]),)
    )
    states: List[Tuple[int, ...]] = [(g,) for g in first_gates]
    for g in first_gates:
        record(g, 1)

    for k in range(2, max_gates + 1):
        next_states_set = set()
        need_next = k < max_gates
        for st in states:
            nodes = base_nodes + st
            existing = base_set | set(st)
            m = len(nodes)
            for i in range(m):
                a = nodes[i]
                for j in range(i + 1, m):
                    b = nodes[j]
                    for out in gate_outputs(a, b):
                        nout = norm_tt(out)
                        if nout in existing:
                            continue
                        record(nout, k)
                        if need_next:
                            next_states_set.add(tuple(sorted(st + (nout,))))
        states = list(next_states_set)

    return best
