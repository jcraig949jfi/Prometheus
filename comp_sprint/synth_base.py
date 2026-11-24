"""Shared monotonic multi-output XAG synthesizer for arms A0, A2, A3, A4, A5 (v2).

Architecture (identical code across all arms; only `library: Sequence[Macro]` varies):
  1. Multi-order Shared Positive-Davio Initialization:
     Runs a small deterministic set of variable-split orderings with shared structural
     hashing (StrashBuilder) across all outputs, keeping the smallest exact verified DAG.
  2. Monotonic k-Cut Library Rewriting (k <= 4, single-output NPN-matched AND multi-output
     shared-cut matched):
     - Enumerates priority k-cuts (k in {2, 3, 4}) of the current verified DAG.
     - Matches single-output cuts modulo exact 4-input NPN equivalence against verified
       macros in `library`, and matches 2-output shared cuts against multi-output macros
       in `library` (modulo input permutation & polarity).
     - Every candidate macro substitution is flattened to primitive {AND, XOR} gates via
       StrashBuilder (ZERO artificial gate-count discount), dead-gate pruned, and
       ACCEPTED ONLY IF flattened primitive gate count STRICTLY DECREASES (`new < best`).
  3. Monotonic Local Algebraic / Structural Pass:
     Shared across all arms; runs within the exact same evaluation budget & WorkMeter.

Guarantees:
  - Strictly monotonic: adding a library can NEVER degrade gate count relative to
    the same initialization seed (within matched eval budget).
  - Exact per-trial eval charging to `WorkMeter`.
  - Every returned circuit passes exact full bitmask truth-table verification.
"""
from __future__ import annotations

import itertools
import random
import time
from typing import Dict, List, Optional, Sequence, Tuple

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


def _norm_tt(tt: int, mask: int) -> Tuple[int, bool]:
    if tt & 1:
        return (tt ^ mask, True)
    return (tt, False)


def _embed_to_4bit(tt: int, k_in: int) -> int:
    """Embed a k_in <= 4 truth table into canonical 16-bit (4-input) truth table."""
    if k_in == 4:
        return tt & 0xFFFF
    out = 0
    sub_mask = (1 << k_in) - 1
    for r in range(16):
        if (tt >> (r & sub_mask)) & 1:
            out |= 1 << r
    return out


def _davio_synthesize(
    n_inputs: int,
    targets: Sequence[int],
    var_order: Sequence[int],
    use_greedy_var: bool = True,
    lib_index: Optional["_LibraryIndex"] = None,
) -> Tuple[XAGCircuit, int]:
    """Build a shared multi-output XAG via Positive/Negative Davio + shared strash pool
    + optional exact NPN4 library leaf substitution (zero gate-count discount)."""
    mask = full_mask(n_inputs)
    in_tts = input_masks(n_inputs)
    clean_targets = tuple(t & mask for t in targets)

    builder = StrashBuilder(n_inputs)
    node_tt: Dict[int, int] = {-1: 0}
    tt_to_node: Dict[int, Tuple[int, bool]] = {0: (-1, False)}
    pool_ids: List[int] = []
    for i in range(n_inputs):
        node_tt[i] = in_tts[i]
        ntt, inv = _norm_tt(in_tts[i], mask)
        tt_to_node[ntt] = (i, inv)
        pool_ids.append(i)

    evals = 0

    def reg(nid: int, ninv: bool, tt: int) -> None:
        raw = (tt ^ mask) if ninv else tt
        if nid not in node_tt:
            node_tt[nid] = raw
            pool_ids.append(nid)
        ntt, ni = _norm_tt(raw, mask)
        if ntt not in tt_to_node:
            tt_to_node[ntt] = (nid, ni)

    def add_prim(op: str, l: int, li: bool, r: int, ri: bool) -> Tuple[int, bool, int]:
        lv = node_tt[l] ^ (mask if li else 0)
        rv = node_tt[r] ^ (mask if ri else 0)
        tt = (lv & rv) if op == "AND" else (lv ^ rv)
        nid, ninv = builder.add_gate(op, l, li, r, ri)
        reg(nid, ninv, tt)
        return nid, ninv, tt

    def cofactor(tt: int, v: int, val: int) -> int:
        m1 = in_tts[v]
        shift = 1 << v
        if val == 0:
            low = tt & (mask ^ m1)
            return low | (low << shift)
        high = tt & m1
        return high | (high >> shift)

    def project_to_4bit(tt: int, dep_vars: Sequence[int]) -> int:
        """Project `tt` (which depends only on `dep_vars`, len <= 4) into a 16-bit 4-var truth table."""
        k = len(dep_vars)
        sub_tt = 0
        for r in range(1 << k):
            full_r = 0
            for j, v in enumerate(dep_vars):
                if (r >> j) & 1:
                    full_r |= 1 << v
            if (tt >> full_r) & 1:
                sub_tt |= 1 << r
        return _embed_to_4bit(sub_tt, k)

    memo: Dict[int, Tuple[int, bool]] = {}

    def synth_one(tt: int, remaining_vars: Tuple[int, ...]) -> Tuple[int, bool]:
        nonlocal evals
        tt &= mask
        ntt, tinv = _norm_tt(tt, mask)
        if ntt in tt_to_node:
            nid, ninv = tt_to_node[ntt]
            return (nid, ninv ^ tinv)
        if ntt in memo:
            nid, ninv = memo[ntt]
            return (nid, ninv ^ tinv)

        # Exact 1-gate XOR hit against shared pool
        for u in pool_ids:
            evals += 1
            need = tt ^ node_tt[u]
            nneed, ni = _norm_tt(need, mask)
            if nneed in tt_to_node:
                v, vi = tt_to_node[nneed]
                nid, oinv, _ = add_prim("XOR", u, False, v, vi ^ ni)
                memo[ntt] = (nid, oinv ^ tinv)
                return (nid, oinv)

        dep = [v for v in remaining_vars if cofactor(tt, v, 0) != tt]
        if not dep:
            return (-1, bool(tt & 1))

        # Exact library leaf match when subfunction depends on 2..4 inputs (flattened into StrashBuilder!)
        if lib_index is not None and lib_index.single_by_npn4 and (2 <= len(dep) <= 4):
            tt4 = project_to_4bit(tt, dep)
            evals += 1
            c = npn4_canonical(tt4)
            cands = lib_index.single_by_npn4.get(c)
            if cands:
                macro, m_tt4 = cands[0]
                evals += len(macro.gates)
                mapping = compose_npn4_wire_map(tt4, m_tt4)
                if mapping is not None:
                    src_idx, src_inv, out_inv = mapping
                    m_map: Dict[int, Tuple[int, bool]] = {-1: (-1, False)}
                    for m_in in range(macro.n_inputs):
                        si = src_idx[m_in]
                        if si < len(dep):
                            m_map[m_in] = (dep[si], src_inv[m_in])
                        else:
                            m_map[m_in] = (-1, src_inv[m_in])
                    for mg_idx, mg in enumerate(macro.gates):
                        mln, mli = m_map[mg.left]
                        mrn, mri = m_map[mg.right]
                        gn, gi, _ = add_prim(mg.op, mln, mli ^ mg.left_inv, mrn, mri ^ mg.right_inv)
                        m_map[macro.n_inputs + mg_idx] = (gn, gi)
                    mo_n, mo_i = macro.outputs[0]
                    fn, fi = m_map[mo_n]
                    res = (fn, fi ^ mo_i ^ out_inv)
                    memo[ntt] = (res[0], res[1] ^ tinv)
                    return res

        if not use_greedy_var:
            best_v = dep[0]
            f0 = cofactor(tt, best_v, 0)
            f1 = cofactor(tt, best_v, 1)
            fd = f0 ^ f1
            pol = False
            if _norm_tt(f1, mask)[0] in tt_to_node and _norm_tt(f0, mask)[0] not in tt_to_node:
                pol = True
            evals += 2
            fbase = f1 if pol else f0
        else:
            best_v = dep[0]
            best_score = (10**9, 10**9, 10**9)
            best_choice = (0, 0, False)
            for pos_idx, v in enumerate(dep):
                evals += 2
                f0 = cofactor(tt, v, 0)
                f1 = cofactor(tt, v, 1)
                fd = f0 ^ f1
                nf0 = _norm_tt(f0, mask)[0]
                nf1 = _norm_tt(f1, mask)[0]
                nfd = _norm_tt(fd, mask)[0]
                for pol_c, fb_c, nfb_c in ((False, f0, nf0), (True, f1, nf1)):
                    miss = (0 if nfb_c in tt_to_node else 1) + (0 if nfd in tt_to_node else 1)
                    rem_d = sum(
                        1 for u in dep if u != v and cofactor(fb_c, u, 0) != fb_c
                    ) + sum(
                        1 for u in dep if u != v and cofactor(fd, u, 0) != fd
                    )
                    sc = (miss, rem_d, pos_idx)
                    if sc < best_score:
                        best_score = sc
                        best_v = v
                        best_choice = (fb_c, fd, pol_c)
            fbase, fd, pol = best_choice

        rest = tuple(u for u in dep if u != best_v)
        nbase, ibase = synth_one(fbase, rest)
        nd, id_ = synth_one(fd, rest)
        na, ia, _ = add_prim("AND", best_v, pol, nd, id_)
        nr, ir, _ = add_prim("XOR", nbase, ibase, na, ia)
        memo[ntt] = (nr, ir ^ tinv)
        return (nr, ir)

    order_tup = tuple(var_order)
    outs = [synth_one(t, order_tup) for t in clean_targets]
    return builder.build(outs, prune_dead=True), evals


def _enumerate_cuts(
    circ: XAGCircuit,
    max_k: int = 4,
    max_cuts_per_node: int = 24,
) -> Dict[int, List[Tuple[int, ...]]]:
    """Standard ABC-style k-feasible cut enumeration prioritizing high-volume 3- and 4-cuts."""
    n_in = circ.n_inputs
    cuts: Dict[int, List[Tuple[int, ...]]] = {i: [(i,)] for i in range(n_in)}
    for idx, g in enumerate(circ.gates):
        nid = n_in + idx
        c_left = cuts.get(g.left, [()]) if g.left >= 0 else [()]
        c_right = cuts.get(g.right, [()]) if g.right >= 0 else [()]
        merged: List[Tuple[int, ...]] = []
        seen = {(nid,)}
        for cl in c_left:
            for cr in c_right:
                u = tuple(sorted(set(cl) | set(cr)))
                if 2 <= len(u) <= max_k and u not in seen:
                    seen.add(u)
                    merged.append(u)
        # Prioritize deeper 4-cuts and 3-cuts (lower min/sum leaf id = deeper cone!), keep unit cut
        merged.sort(key=lambda c: (-len(c), sum(c), c))
        cuts[nid] = [(nid,)] + merged[: max_cuts_per_node - 1]
    return cuts


def _eval_cut_tt(
    circ: XAGCircuit,
    root_nid: int,
    leaves: Tuple[int, ...],
) -> Optional[int]:
    """Compute the exact 16-bit (4-input embedded) truth table of `root_nid` in terms of `leaves`.

    Returns None if `root_nid` depends on a primary input not covered by `leaves`.
    """
    n_in = circ.n_inputs
    k = len(leaves)
    assert 1 <= k <= 4
    leaf_masks = {lf: input_masks(4)[i] for i, lf in enumerate(leaves)}
    vals: Dict[int, int] = {-1: 0}
    vals.update(leaf_masks)

    def eval_node(nid: int) -> Optional[int]:
        if nid in vals:
            return vals[nid]
        if nid < n_in:
            # Uncovered primary input!
            return None
        g = circ.gates[nid - n_in]
        lv = eval_node(g.left)
        if lv is None:
            return None
        rv = eval_node(g.right)
        if rv is None:
            return None
        if g.left_inv:
            lv ^= 0xFFFF
        if g.right_inv:
            rv ^= 0xFFFF
        res = (lv & rv) if g.op == "AND" else (lv ^ rv)
        vals[nid] = res
        return res

    return eval_node(root_nid)


def _splice_single_node(
    circ: XAGCircuit,
    target_nid: int,
    leaves: Tuple[int, ...],
    macro: Macro,
    src_idx: Tuple[int, int, int, int],
    src_inv: Tuple[bool, bool, bool, bool],
    out_inv: bool,
) -> XAGCircuit:
    """Replace `target_nid` in `circ` with flattened `macro` bound to `leaves`, strash + prune."""
    n_in = circ.n_inputs
    builder = StrashBuilder(n_in)
    node_map: Dict[int, Tuple[int, bool]] = {-1: (-1, False)}
    for i in range(n_in):
        node_map[i] = (i, False)

    for idx, g in enumerate(circ.gates):
        nid = n_in + idx
        if nid == target_nid:
            # Instantiate macro flattened into builder!
            k_leaf = len(leaves)
            m_map: Dict[int, Tuple[int, bool]] = {-1: (-1, False)}
            for m_in in range(macro.n_inputs):
                si = src_idx[m_in]
                if si < k_leaf:
                    ln, li = node_map[leaves[si]]
                    m_map[m_in] = (ln, li ^ src_inv[m_in])
                else:
                    # Unused padded input slot -> bind to CONST0 ^ src_inv
                    m_map[m_in] = (-1, src_inv[m_in])
            for mg_idx, mg in enumerate(macro.gates):
                mln, mli = m_map[mg.left]
                mrn, mri = m_map[mg.right]
                m_map[macro.n_inputs + mg_idx] = builder.add_gate(
                    mg.op, mln, mli ^ mg.left_inv, mrn, mri ^ mg.right_inv
                )
            mo_node, mo_inv = macro.outputs[0]
            mn, mi = m_map[mo_node]
            node_map[nid] = (mn, mi ^ mo_inv ^ out_inv)
        else:
            ln, li = node_map[g.left]
            rn, ri = node_map[g.right]
            node_map[nid] = builder.add_gate(g.op, ln, li ^ g.left_inv, rn, ri ^ g.right_inv)

    new_outs = []
    for onode, oinv in circ.outputs:
        mn, mi = node_map[onode]
        new_outs.append((mn, mi ^ oinv))
    return builder.build(new_outs, prune_dead=True)


def _splice_multi_output_nodes(
    circ: XAGCircuit,
    target_nids: Tuple[int, ...],
    leaves: Tuple[int, ...],
    macro: Macro,
    perm: Tuple[int, ...],
    in_neg: int,
    out_perm: Tuple[int, ...],
    out_invs: Tuple[bool, ...],
) -> XAGCircuit:
    """Simultaneously replace multiple nodes sharing `leaves` with a multi-output `macro`."""
    n_in = circ.n_inputs
    builder = StrashBuilder(n_in)
    node_map: Dict[int, Tuple[int, bool]] = {-1: (-1, False)}
    for i in range(n_in):
        node_map[i] = (i, False)

    target_set = set(target_nids)
    # Instantiate the multi-output macro as soon as all `leaves` are available (i.e. at max(leaves))
    ready_after = max(leaves)
    macro_instantiated = False
    macro_out_wires: Dict[int, Tuple[int, bool]] = {}

    def emit_macro() -> None:
        nonlocal macro_instantiated
        m_map: Dict[int, Tuple[int, bool]] = {-1: (-1, False)}
        for m_in in range(macro.n_inputs):
            lf = leaves[perm[m_in]]
            ln, li = node_map[lf]
            m_map[m_in] = (ln, li ^ bool((in_neg >> m_in) & 1))
        for mg_idx, mg in enumerate(macro.gates):
            mln, mli = m_map[mg.left]
            mrn, mri = m_map[mg.right]
            m_map[macro.n_inputs + mg_idx] = builder.add_gate(
                mg.op, mln, mli ^ mg.left_inv, mrn, mri ^ mg.right_inv
            )
        for h_idx, tnid in enumerate(target_nids):
            mo_node, mo_inv = macro.outputs[out_perm[h_idx]]
            mn, mi = m_map[mo_node]
            macro_out_wires[tnid] = (mn, mi ^ mo_inv ^ out_invs[h_idx])
        macro_instantiated = True

    if ready_after < n_in:
        emit_macro()

    for idx, g in enumerate(circ.gates):
        nid = n_in + idx
        if nid in target_set:
            if not macro_instantiated:
                emit_macro()
            node_map[nid] = macro_out_wires[nid]
        else:
            ln, li = node_map[g.left]
            rn, ri = node_map[g.right]
            node_map[nid] = builder.add_gate(g.op, ln, li ^ g.left_inv, rn, ri ^ g.right_inv)
            if not macro_instantiated and nid == ready_after:
                emit_macro()

    new_outs = []
    for onode, oinv in circ.outputs:
        mn, mi = node_map[onode]
        new_outs.append((mn, mi ^ oinv))
    return builder.build(new_outs, prune_dead=True)


class _LibraryIndex:
    """Fast NPN4 index for single-output macros + permutation index for multi-output macros."""

    def __init__(self, library: Sequence[Macro]) -> None:
        self.single_by_npn4: Dict[int, List[Tuple[Macro, int]]] = {}
        # Multi-output macros (n_inputs <= 4, n_outputs == 2):
        # index by frozenset of canonical NPN4 classes of their outputs for instant pre-filtering!
        self.pair_by_npn4_pair: Dict[Tuple[int, int], List[Tuple[Macro, Tuple[int, int]]]] = {}

        for m in library:
            if not (2 <= m.n_inputs <= 4) or len(m.gates) == 0:
                continue
            if len(m.outputs) == 1:
                tt4 = _embed_to_4bit(m.truth_tables[0], m.n_inputs)
                c = npn4_canonical(tt4)
                self.single_by_npn4.setdefault(c, []).append((m, tt4))
            elif len(m.outputs) >= 2:
                # Also index each individual output as a single-output macro? No — keep multi-output
                # macros strictly for shared multi-output replacement (and also allow single-out if
                # caller explicitly included 1-out macros).
                for a in range(len(m.outputs)):
                    for b in range(a + 1, len(m.outputs)):
                        tta = _embed_to_4bit(m.truth_tables[a], m.n_inputs)
                        ttb = _embed_to_4bit(m.truth_tables[b], m.n_inputs)
                        ca, cb = npn4_canonical(tta), npn4_canonical(ttb)
                        key = (ca, cb) if ca <= cb else (cb, ca)
                        self.pair_by_npn4_pair.setdefault(key, []).append((m, (a, b)))

        # Sort each bucket smallest primitive gate count first
        for c in self.single_by_npn4:
            self.single_by_npn4[c].sort(key=lambda pair: len(pair[0].gates))
        for k in self.pair_by_npn4_pair:
            self.pair_by_npn4_pair[k].sort(key=lambda pair: len(pair[0].gates))


def _match_multi_output_pair(
    tt_u: int,
    tt_v: int,
    k_leaf: int,
    macro: Macro,
    out_pair: Tuple[int, int],
) -> Optional[Tuple[Tuple[int, ...], int, Tuple[int, int], Tuple[bool, bool]]]:
    """Check if `(tt_u, tt_v)` on `k_leaf` inputs matches `macro`'s outputs `out_pair`
    under input permutation + input negation + output negation (exact, k_leaf == macro.n_inputs <= 4)."""
    if k_leaf != macro.n_inputs:
        return None
    n_rows = 1 << k_leaf
    sub_mask = (1 << n_rows) - 1
    mu = tt_u & sub_mask
    mv = tt_v & sub_mask
    ma = macro.truth_tables[out_pair[0]] & sub_mask
    mb = macro.truth_tables[out_pair[1]] & sub_mask

    # Pre-check Hamming weights mod inversion (fast exact filter!)
    def w_mod(x: int) -> int:
        w = x.bit_count()
        return min(w, n_rows - w)

    w_u, w_v = w_mod(mu), w_mod(mv)
    w_a, w_b = w_mod(ma), w_mod(mb)
    if {w_u, w_v} != {w_a, w_b}:
        return None

    # Exhaustively check k! * 2^k transforms (for k=3: 48; for k=4: 384 — microseconds!)
    for perm in itertools.permutations(range(k_leaf)):
        for neg in range(1 << k_leaf):
            # Evaluate macro(x_{perm[0]}^neg0, ...) on each row r of leaves
            ta = 0
            tb = 0
            for r in range(n_rows):
                mr = 0
                for j in range(k_leaf):
                    bit = ((r >> perm[j]) & 1) ^ ((neg >> j) & 1)
                    mr |= bit << j
                if (ma >> mr) & 1:
                    ta |= 1 << r
                if (mb >> mr) & 1:
                    tb |= 1 << r
            # Match (mu, mv) to (ta, tb) or (tb, ta) modulo output inversions
            for (o_p, x0, x1) in ((out_pair, ta, tb), ((out_pair[1], out_pair[0]), tb, ta)):
                inv0 = None
                if x0 == mu:
                    inv0 = False
                elif (x0 ^ sub_mask) == mu:
                    inv0 = True
                if inv0 is None:
                    continue
                inv1 = None
                if x1 == mv:
                    inv1 = False
                elif (x1 ^ sub_mask) == mv:
                    inv1 = True
                if inv1 is not None:
                    return (perm, neg, o_p, (inv0, inv1))
    return None


def _monotonic_rewrite_pass(
    circ: XAGCircuit,
    clean_targets: Tuple[int, ...],
    lib_index: _LibraryIndex,
    budget_left: int,
) -> Tuple[XAGCircuit, int, int]:
    """Run monotonic k-cut substitution using `lib_index`. Returns (best_circ, evals_used, n_accepted)."""
    best = circ
    evals = 0
    accepted = 0
    if not lib_index.single_by_npn4 and not lib_index.pair_by_npn4_pair:
        return best, 0, 0

    for _round in range(6):
        if evals >= budget_left:
            break
        improved_this_round = False
        cuts = _enumerate_cuts(best, max_k=4, max_cuts_per_node=16)
        n_in = best.n_inputs
        n_g = best.gate_count()

        # 1. Single-output NPN4 k-cut substitution
        if lib_index.single_by_npn4:
            for g_idx in range(n_g - 1, -1, -1):
                if evals >= budget_left:
                    break
                nid = n_in + g_idx
                for leaves in cuts.get(nid, ()):
                    if len(leaves) < 2:
                        continue
                    if evals >= budget_left:
                        break
                    tt4 = _eval_cut_tt(best, nid, leaves)
                    evals += 1
                    if tt4 is None:
                        continue
                    c = npn4_canonical(tt4)
                    cands = lib_index.single_by_npn4.get(c)
                    if not cands:
                        continue
                    for macro, m_tt4 in cands[:3]:
                        evals += len(macro.gates)
                        mapping = compose_npn4_wire_map(tt4, m_tt4)
                        if mapping is None:
                            continue
                        src_idx, src_inv, out_inv = mapping
                        cand = _splice_single_node(best, nid, leaves, macro, src_idx, src_inv, out_inv)
                        if cand.gate_count() < best.gate_count():
                            if cand.truth_tables() == clean_targets:
                                best = cand
                                accepted += 1
                                improved_this_round = True
                                break
                    if improved_this_round:
                        break
                if improved_this_round:
                    break

        if improved_this_round:
            continue

        # 2. Multi-output shared k-cut substitution (captures full-adder / S-box / shared-cone savings!)
        if lib_index.pair_by_npn4_pair and evals < budget_left:
            # Group nodes sharing the EXACT same k-leaf cut (k in {2, 3, 4})
            by_leaves: Dict[Tuple[int, ...], List[Tuple[int, int, int]]] = {}
            for g_idx in range(n_g):
                nid = n_in + g_idx
                for leaves in cuts.get(nid, ()):
                    if len(leaves) < 2:
                        continue
                    tt4 = _eval_cut_tt(best, nid, leaves)
                    evals += 1
                    if tt4 is None:
                        continue
                    by_leaves.setdefault(leaves, []).append((nid, tt4, npn4_canonical(tt4)))

            for leaves, entries in by_leaves.items():
                if len(entries) < 2 or evals >= budget_left:
                    continue
                k_leaf = len(leaves)
                for i in range(len(entries)):
                    nid_u, ttu, cu = entries[i]
                    for j in range(i + 1, len(entries)):
                        if evals >= budget_left:
                            break
                        nid_v, ttv, cv = entries[j]
                        if ttu == ttv or (ttu ^ 0xFFFF) == ttv:
                            continue
                        pkey = (cu, cv) if cu <= cv else (cv, cu)
                        cands = lib_index.pair_by_npn4_pair.get(pkey)
                        if not cands:
                            continue
                        for macro, opair in cands[:3]:
                            evals += len(macro.gates) * 2
                            match = _match_multi_output_pair(ttu, ttv, k_leaf, macro, opair)
                            if match is None:
                                continue
                            perm, neg, matched_opair, o_invs = match
                            cand = _splice_multi_output_nodes(
                                best, (nid_u, nid_v), leaves, macro, perm, neg, matched_opair, o_invs
                            )
                            if cand.gate_count() < best.gate_count():
                                if cand.truth_tables() == clean_targets:
                                    best = cand
                                    accepted += 1
                                    improved_this_round = True
                                    break
                        if improved_this_round:
                            break
                    if improved_this_round:
                        break
                if improved_this_round:
                    break

        if not improved_this_round:
            break

    return best, evals, accepted


def _eval_macro_on_wire_tts(
    macro: Macro,
    arg_tts: Sequence[int],
    mask: int,
) -> Tuple[int, ...]:
    """Evaluate a macro's outputs on wire truth-table bitmasks."""
    vals: List[int] = list(arg_tts)
    for g in macro.gates:
        lv = 0 if g.left == -1 else vals[g.left]
        if g.left_inv:
            lv ^= mask
        rv = 0 if g.right == -1 else vals[g.right]
        if g.right_inv:
            rv ^= mask
        vals.append((lv & rv) if g.op == "AND" else (lv ^ rv))
    outs: List[int] = []
    for onode, oinv in macro.outputs:
        v = 0 if onode == -1 else vals[onode]
        if oinv:
            v ^= mask
        outs.append(v)
    return tuple(outs)


def _check_exact_factorization(
    wire_tts: Sequence[int],
    clean_targets: Sequence[int],
    n_rows: int,
) -> Optional[Tuple[int, Dict[int, int]]]:
    """Check if `clean_targets` is a 100% exact function of `wire_tts` across all `n_rows`.

    Returns `(n_distinct_states, state_to_out_pack)` if lossless, else None.
    """
    n_w = len(wire_tts)
    n_o = len(clean_targets)
    mapping: Dict[int, int] = {}
    for r in range(n_rows):
        st = 0
        for j in range(n_w):
            if (wire_tts[j] >> r) & 1:
                st |= 1 << j
        out_pack = 0
        for h in range(n_o):
            if (clean_targets[h] >> r) & 1:
                out_pack |= 1 << h
        prev = mapping.get(st)
        if prev is None:
            mapping[st] = out_pack
        elif prev != out_pack:
            return None
    return len(mapping), mapping


def _build_residual_on_reduced_wires(
    n_orig_inputs: int,
    wire_nodes: Sequence[Tuple[int, bool]],
    wire_tts: Sequence[int],
    clean_targets: Sequence[int],
    builder: StrashBuilder,
    lib_index: Optional["_LibraryIndex"] = None,
) -> XAGCircuit:
    """Synthesize residual function on compressed `wire_nodes` (len <= 6) using care-set aware Davio."""
    k = len(wire_nodes)
    n_outs = len(clean_targets)
    n_rows_orig = 1 << n_orig_inputs
    # Map each reachable k-bit wire state -> target output bits; unreachable states are don't-cares!
    state_map: Dict[int, int] = {}
    for r in range(n_rows_orig):
        st = 0
        for j in range(k):
            if (wire_tts[j] >> r) & 1:
                st |= 1 << j
        if st not in state_map:
            out_pack = 0
            for h in range(n_outs):
                if (clean_targets[h] >> r) & 1:
                    out_pack |= 1 << h
            state_map[st] = out_pack

    # Build care-set mask + truth tables in the k-wire space (filling don't-cares with 0 cleanly,
    # or checking exact 0/1/projection/1-gate hits over the care set first!)
    n_rows_k = 1 << k
    care_mask = 0
    sub_tts = [0] * n_outs
    for st, opack in state_map.items():
        care_mask |= 1 << st
        for h in range(n_outs):
            if (opack >> h) & 1:
                sub_tts[h] |= 1 << st

    # Try multiple Davio orderings on the reduced k-wire space (using don't-care-aware cofactoring!)
    in_k = input_masks(k)
    full_k = full_mask(k)

    def synth_care(order: Sequence[int]) -> XAGCircuit:
        b = StrashBuilder(k)
        ntt_map: Dict[int, Tuple[int, bool]] = {0: (-1, False)}
        n_tt: Dict[int, int] = {-1: 0}
        pool = []
        for i in range(k):
            n_tt[i] = in_k[i]
            pool.append(i)
            # Register on care_mask!
            c_tt = in_k[i] & care_mask
            ntt_map[c_tt] = (i, False)
            ntt_map[c_tt ^ care_mask] = (i, True)

        def add_g(op: str, l: int, li: bool, r: int, ri: bool) -> Tuple[int, bool]:
            lv = n_tt[l] ^ (full_k if li else 0)
            rv = n_tt[r] ^ (full_k if ri else 0)
            tt = (lv & rv) if op == "AND" else (lv ^ rv)
            nid, ninv = b.add_gate(op, l, li, r, ri)
            raw = (tt ^ full_k) if ninv else tt
            if nid not in n_tt:
                n_tt[nid] = raw
                pool.append(nid)
                c_tt = raw & care_mask
                if c_tt not in ntt_map:
                    ntt_map[c_tt] = (nid, False)
                if (c_tt ^ care_mask) not in ntt_map:
                    ntt_map[c_tt ^ care_mask] = (nid, True)
            return nid, ninv

        def cof_care(tt: int, cm: int, v: int, val: int) -> Tuple[int, int]:
            m1 = in_k[v]
            shift = 1 << v
            if val == 0:
                m0 = full_k ^ m1
                t0 = tt & m0
                c0 = cm & m0
                return (t0 | (t0 << shift), c0 | (c0 << shift))
            t1 = tt & m1
            c1 = cm & m1
            return (t1 | (t1 >> shift), c1 | (c1 >> shift))

        def rec(tt: int, cm: int, rem: Tuple[int, ...]) -> Tuple[int, bool]:
            tt &= cm
            if cm == 0 or tt == 0:
                return (-1, False)
            if tt == cm:
                return (-1, True)
            # Check exact match on current care-set `cm` against existing pool!
            for u in pool:
                ut = n_tt[u] & cm
                if ut == tt:
                    return (u, False)
                if (ut ^ cm) == tt:
                    return (u, True)
            # Check 1-gate XOR match on current care-set `cm`
            for idx_u in range(len(pool)):
                u = pool[idx_u]
                ut = n_tt[u] & cm
                for idx_v in range(idx_u + 1, len(pool)):
                    vt = n_tt[pool[idx_v]] & cm
                    xr = ut ^ vt
                    if xr == tt:
                        return add_g("XOR", u, False, pool[idx_v], False)
                    if (xr ^ cm) == tt:
                        n, inv = add_g("XOR", u, False, pool[idx_v], False)
                        return (n, not inv)
            # Filter variables where f0 and f1 actually disagree on overlapping care-set
            dep = []
            for v in rem:
                t0, c0 = cof_care(tt, cm, v, 0)
                t1, c1 = cof_care(tt, cm, v, 1)
                both = c0 & c1
                if (t0 & both) != (t1 & both):
                    dep.append(v)
            if not dep:
                # Independent of all remaining variables on care set: merge care sets!
                # Pick any cared bit
                return (-1, bool(tt != 0))
            v = dep[0]
            t0, c0 = cof_care(tt, cm, v, 0)
            t1, c1 = cof_care(tt, cm, v, 1)
            # Don't-care-aware Positive Davio: where only c0 or only c1 is cared, set fd=0!
            both = c0 & c1
            fd_t = (t0 ^ t1) & both
            # f_base equals t0 on c0 and t1 on (c1 \ c0)
            fb_c = c0 | c1
            fb_t = (t0 & c0) | (t1 & (c1 & ~c0))
            rest = tuple(u for u in dep if u != v)
            nb, ib = rec(fb_t, fb_c, rest)
            nd, id_ = rec(fd_t, both, rest)
            na, ia = add_g("AND", v, False, nd, id_)
            return add_g("XOR", nb, ib, na, ia)

        outs_k = [rec(sub_tts[h], care_mask, tuple(order)) for h in range(n_outs)]
        return b.build(outs_k, prune_dead=True)

    # Try identity order + reverse order on reduced k-wire space, pick smaller
    best_sub = synth_care(list(range(k)))
    if k >= 2:
        alt_sub = synth_care(list(reversed(range(k))))
        if alt_sub.gate_count() < best_sub.gate_count():
            best_sub = alt_sub

    # Stitch `best_sub` onto `builder`'s concrete `wire_nodes`!
    stitched = StrashBuilder(n_orig_inputs)
    # Copy existing gates from `builder`
    old_map: Dict[int, Tuple[int, bool]] = {-1: (-1, False)}
    for i in range(n_orig_inputs):
        old_map[i] = (i, False)
    for idx, g in enumerate(builder.gates):
        ln, li = old_map[g.left]
        rn, ri = old_map[g.right]
        old_map[n_orig_inputs + idx] = stitched.add_gate(g.op, ln, li ^ g.left_inv, rn, ri ^ g.right_inv)

    sub_map: Dict[int, Tuple[int, bool]] = {-1: (-1, False)}
    for j, (wn, wi) in enumerate(wire_nodes):
        mn, mi = old_map[wn]
        sub_map[j] = (mn, mi ^ wi)
    for idx, g in enumerate(best_sub.gates):
        ln, li = sub_map[g.left]
        rn, ri = sub_map[g.right]
        sub_map[k + idx] = stitched.add_gate(g.op, ln, li ^ g.left_inv, rn, ri ^ g.right_inv)

    final_outs = []
    for onode, oinv in best_sub.outputs:
        mn, mi = sub_map[onode]
        final_outs.append((mn, mi ^ oinv))
    return stitched.build(final_outs, prune_dead=True)


def _linear_precond_davio(
    n_inputs: int,
    clean_targets: Tuple[int, ...],
    lib_index: Optional["_LibraryIndex"],
    budget_left: int,
) -> Tuple[Optional[XAGCircuit], int]:
    """Invertible GF(2) linear-basis preconditioning (1-XOR and 2-XOR basis changes).

    Replaces input wire x_j with (x_j ^ x_i) before Davio synthesis (1 primitive XOR gate),
    then maps outputs back via exact bit-substitution. Preserves |image| = 2^n (bijective)
    while frequently collapsing S-box / GF(16) / XOR-heavy multi-output ANF complexity!
    Strictly monotonic: returns best flattened XAG circuit or None.
    """
    if n_inputs < 3 or n_inputs > 6 or budget_left < 200:
        return None, 0

    mask = full_mask(n_inputs)
    n_rows = 1 << n_inputs
    evals = 0
    best_circ: Optional[XAGCircuit] = None

    def transform_targets(xor_steps: Sequence[Tuple[int, int]]) -> Tuple[int, ...]:
        # Forward map y = A x (where each step (i, j) sets y_j ^= y_i).
        # Then F(x) = G(y) => G(y) = F(A^{-1} y).
        # Since each step (i, j) is self-inverse, A^{-1} applies steps in reverse order!
        inv_map = [0] * n_rows
        for y_row in range(n_rows):
            x_row = y_row
            for i, j in reversed(xor_steps):
                if (x_row >> i) & 1:
                    x_row ^= 1 << j
            inv_map[y_row] = x_row
        new_t = []
        for t in clean_targets:
            nt = 0
            for y_row in range(n_rows):
                if (t >> inv_map[y_row]) & 1:
                    nt |= 1 << y_row
            new_t.append(nt)
        return tuple(new_t)

    def stitch_linear(xor_steps: Sequence[Tuple[int, int]], inner: XAGCircuit) -> XAGCircuit:
        b = StrashBuilder(n_inputs)
        wires: List[Tuple[int, bool]] = [(k, False) for k in range(n_inputs)]
        for i, j in xor_steps:
            li_n, li_inv = wires[i]
            lj_n, lj_inv = wires[j]
            wires[j] = b.add_gate("XOR", li_n, li_inv, lj_n, lj_inv)
        nmap: Dict[int, Tuple[int, bool]] = {-1: (-1, False)}
        for k in range(n_inputs):
            nmap[k] = wires[k]
        for idx, g in enumerate(inner.gates):
            ln, li = nmap[g.left]
            rn, ri = nmap[g.right]
            nmap[n_inputs + idx] = b.add_gate(g.op, ln, li ^ g.left_inv, rn, ri ^ g.right_inv)
        final_outs = [(nmap[on][0], nmap[on][1] ^ oi) for on, oi in inner.outputs]
        return b.build(final_outs, prune_dead=True)

    # 1. Single-XOR basis steps: pick top promising pairs by reduced cofactor activity
    order_base = list(range(n_inputs))
    top_step1: List[Tuple[int, Tuple[int, int]]] = []
    for i in range(n_inputs):
        for j in range(n_inputs):
            if i == j or evals >= budget_left:
                continue
            steps = ((i, j),)
            t_prime = transform_targets(steps)
            inner, ev = _davio_synthesize(n_inputs, t_prime, order_base, use_greedy_var=True, lib_index=lib_index)
            evals += ev + 1
            cand = stitch_linear(steps, inner)
            gc = cand.gate_count()
            top_step1.append((gc, (i, j)))
            if best_circ is None or gc < best_circ.gate_count():
                if cand.truth_tables() == clean_targets:
                    best_circ = cand

    # 2. Second-XOR step from the top-4 best 1-XOR bases (bounded, fast, huge win on 4-bit S-boxes!)
    top_step1.sort(key=lambda x: x[0])
    for _gc1, s1 in top_step1[:4]:
        if evals >= budget_left:
            break
        for i in range(n_inputs):
            for j in range(n_inputs):
                if i == j or (i, j) == s1 or evals >= budget_left:
                    continue
                steps = (s1, (i, j))
                t_prime = transform_targets(steps)
                inner, ev = _davio_synthesize(n_inputs, t_prime, order_base, use_greedy_var=True, lib_index=lib_index)
                evals += ev + 1
                cand = stitch_linear(steps, inner)
                if best_circ is None or cand.gate_count() < best_circ.gate_count():
                    if cand.truth_tables() == clean_targets:
                        best_circ = cand

    return best_circ, evals


def _factor_with_library(
    n_inputs: int,
    clean_targets: Tuple[int, ...],
    library: Sequence[Macro],
    budget_left: int,
    allow_bijective: bool = False,
    max_depth: int = 6,
) -> Tuple[Optional[XAGCircuit], int]:
    """Exact Macro Functional Factorization (State-Compressing + Optional Bijective Peeling).

    Iteratively applies verified multi-output macros M(subset) -> Z that:
      1. Preserve 100% of target output distinctions (exact lossless factorization), AND
      2. Either strictly compress reachable states |image(W')| < |image(W)|, OR (when
         `allow_bijective=True`) keep |image(W')| == |image(W)| while strictly lowering
         the realized flattened gate count (enables S-box / Feistel multi-layer peeling!).
    """
    mask = full_mask(n_inputs)
    n_rows = 1 << n_inputs
    in_tts = input_masks(n_inputs)
    # Only multi-output macros (len(m.outputs) >= 2) can preserve multi-output distinctions
    # while compressing wires/states; single-output macros belong strictly to NPN4 cut rewriting!
    cand_macros = [
        m for m in library
        if 2 <= m.n_inputs <= min(4, n_inputs) and len(m.outputs) >= 2 and len(m.gates) > 0
    ]
    if not cand_macros:
        return None, 0

    evals = 0
    best_circ: Optional[XAGCircuit] = None

    # Compute baseline gate count on raw primary inputs for bijective acceptance threshold
    base_res = _build_residual_on_reduced_wires(
        n_inputs, [(i, False) for i in range(n_inputs)], list(in_tts), clean_targets, StrashBuilder(n_inputs)
    )
    base_ref_gates = base_res.gate_count() if base_res.truth_tables() == clean_targets else 10**9

    # Beam search over compressed wire bases: each state is (n_states, cur_gates, builder, wire_nodes, wire_tts)
    init_builder = StrashBuilder(n_inputs)
    init_nodes = [(i, False) for i in range(n_inputs)]
    init_tts = list(in_tts)
    beam = [(n_rows, 0, init_builder, init_nodes, init_tts)]

    # Precompute non-redundant (perm, input_neg_mask) transforms per macro so both
    # symmetric cells (HA/FA/CAS) AND NPN-canonicalized alien cells match arbitrary polarities!
    macro_transforms: Dict[str, List[Tuple[Tuple[int, ...], int]]] = {}
    for m in cand_macros:
        k = m.n_inputs
        sub_in = input_masks(k)
        sub_mask = full_mask(k)
        seen_out_sigs = set()
        unique_pn: List[Tuple[Tuple[int, ...], int]] = []
        # Try neg == 0 first (preserves fast path), then non-zero input polarities up to 24 unique
        neg_order = [0] + list(range(1, 1 << k))
        for neg in neg_order:
            for p in itertools.permutations(range(k)):
                args_p = [
                    sub_in[p[j]] ^ (sub_mask if ((neg >> j) & 1) else 0)
                    for j in range(k)
                ]
                ot = _eval_macro_on_wire_tts(m, args_p, sub_mask)
                sig = tuple(sorted(min(t, t ^ sub_mask) for t in ot))
                if sig not in seen_out_sigs:
                    seen_out_sigs.add(sig)
                    unique_pn.append((p, neg))
                    if len(unique_pn) >= (48 if k <= 3 else 16):
                        break
            if len(unique_pn) >= (48 if k <= 3 else 16):
                break
        macro_transforms[m.sha256] = unique_pn

    for _depth in range(max_depth):
        if evals >= budget_left or not beam:
            break
        next_beam = []
        seen_sigs = set()

        for cur_states, cur_g, b_cur, w_nodes, w_tts in beam:
            k_w = len(w_nodes)
            if k_w < 2:
                continue
            for m in cand_macros:
                if m.n_inputs > k_w or evals >= budget_left:
                    continue
                transforms_m = macro_transforms[m.sha256]
                combos = list(itertools.combinations(range(k_w), m.n_inputs))
                for comb in combos:
                    if evals >= budget_left:
                        break
                    for p, neg in transforms_m:
                        order = tuple(comb[i] for i in p)
                        if evals >= budget_left:
                            break
                        arg_tts = [
                            w_tts[order[j]] ^ (mask if ((neg >> j) & 1) else 0)
                            for j in range(m.n_inputs)
                        ]
                        out_tts = _eval_macro_on_wire_tts(m, arg_tts, mask)
                        evals += len(m.gates)

                        consumed = set(order)
                        rem_idx = [i for i in range(k_w) if i not in consumed]
                        new_tts = [w_tts[i] for i in rem_idx] + list(out_tts)
                        res = _check_exact_factorization(new_tts, clean_targets, n_rows)
                        evals += 1
                        if res is None:
                            continue
                        new_states, _ = res
                        is_compressive = new_states < cur_states
                        is_bijective_cand = (
                            allow_bijective
                            and (new_states == cur_states)
                            and (len(new_tts) == k_w)
                            and (len(m.outputs) >= 2)
                            and (_depth < 2)
                        )
                        if not is_compressive and not is_bijective_cand:
                            continue

                        sig = tuple(sorted(new_tts))
                        if sig in seen_sigs:
                            continue
                        seen_sigs.add(sig)

                        b_new = StrashBuilder(n_inputs)
                        omap: Dict[int, Tuple[int, bool]] = {-1: (-1, False)}
                        for i in range(n_inputs):
                            omap[i] = (i, False)
                        for gi, g in enumerate(b_cur.gates):
                            ln, li = omap[g.left]
                            rn, ri = omap[g.right]
                            omap[n_inputs + gi] = b_new.add_gate(g.op, ln, li ^ g.left_inv, rn, ri ^ g.right_inv)

                        mmap: Dict[int, Tuple[int, bool]] = {-1: (-1, False)}
                        for mi, wi_idx in enumerate(order):
                            wn, wi = w_nodes[wi_idx]
                            mn, m_inv = omap[wn]
                            mmap[mi] = (mn, m_inv ^ wi ^ bool((neg >> mi) & 1))
                        for gi, g in enumerate(m.gates):
                            ln, li = mmap[g.left]
                            rn, ri = mmap[g.right]
                            mmap[m.n_inputs + gi] = b_new.add_gate(g.op, ln, li ^ g.left_inv, rn, ri ^ g.right_inv)

                        new_nodes = [
                            (omap[w_nodes[i][0]][0], omap[w_nodes[i][0]][1] ^ w_nodes[i][1])
                            for i in rem_idx
                        ]
                        for onode, oinv in m.outputs:
                            mn, mi = mmap[onode]
                            new_nodes.append((mn, mi ^ oinv))

                        cand_gates = 10**9
                        if len(new_nodes) <= 6:
                            cand_c = _build_residual_on_reduced_wires(
                                n_inputs, new_nodes, new_tts, clean_targets, b_new
                            )
                            if cand_c.truth_tables() == clean_targets:
                                cand_gates = cand_c.gate_count()
                                if best_circ is None or cand_gates < best_circ.gate_count():
                                    best_circ = cand_c

                        # Reject non-compressive bijective candidates unless they actually improve realized gates!
                        if not is_compressive and cand_gates >= min(base_ref_gates, best_circ.gate_count() if best_circ else 10**9):
                            continue

                        next_beam.append((cand_gates, new_states, len(b_new.gates), m.sha256, b_new, new_nodes, new_tts))
                        break

        by_macro: Dict[str, List] = {}
        for item in next_beam:
            by_macro.setdefault(item[3], []).append(item)
        picked = []
        for items in by_macro.values():
            items.sort(key=lambda it: (it[1], it[0], it[2]))
            picked.extend(items[:2])
        by_states = sorted(next_beam, key=lambda it: (it[1], it[0], it[2]))[:6]
        by_gates = sorted(next_beam, key=lambda it: (it[0], it[1], it[2]))[:6]
        merged_beam = []
        seen_b = set()
        for it in picked + by_states + by_gates:
            sig = tuple(sorted(it[6]))
            if sig not in seen_b:
                seen_b.add(sig)
                merged_beam.append((it[1], it[2], it[4], it[5], it[6]))
        beam = merged_beam[:14]

    return best_circ, evals


def synthesize_with_artifact(
    n_inputs: int,
    targets: Sequence[int],
    artifact: Optional[object] = None,
    budget: int = 8000,
    seed: int = 0,
    meter: Optional[object] = None,
    phase: str = "synth",
) -> XAGCircuit:
    """Unified monotonic offline interpreter for full `(L, T, S)` Artifacts (identical across ALL arms!).

    Stages (strictly non-degrading; every trial charged to `WorkMeter`):
      1. Multi-order Shared Davio Initialization (identical base floor A0).
      2a. (if S.enable_linear_precond) Invertible GF(2) 1-XOR / 2-XOR basis preconditioning.
      2b. Exact Macro Functional Factorization over `L` (state-compressing + optional bijective).
      2c. Library-accelerated Davio leaves over `L U rhs(T)`.
      2d. Monotonic k-cut NPN4 + multi-output + verified RewriteRule (`T`) DAG rewriting
          (accepts equal-gate algebraic bridges whenever global strashed gate count strictly drops!).
    """
    t0 = time.perf_counter()
    rng = random.Random(seed)
    mask = full_mask(n_inputs)
    clean_targets = tuple(t & mask for t in targets)

    macros: Sequence[Macro] = ()
    rewrites: Sequence[object] = ()
    enable_linear_precond = False
    enable_bijective_factor = False
    enable_bridge_rewrites = False
    max_factor_depth = 6

    if artifact is not None:
        macros = tuple(getattr(artifact, "macros", ()))
        rewrites = tuple(getattr(artifact, "rewrites", ()))
        strat = getattr(artifact, "strategy", None)
        if strat is not None:
            enable_linear_precond = bool(getattr(strat, "enable_linear_precond", False))
            enable_bijective_factor = bool(getattr(strat, "enable_bijective_factor", False))
            enable_bridge_rewrites = bool(getattr(strat, "enable_bridge_rewrites", False))
            max_factor_depth = int(getattr(strat, "max_factor_depth", 6))

    evals_used = 0
    # Stage 1: Deterministic multi-order Shared Davio initialization (identical across all arms!)
    orders: List[Tuple[List[int], bool]] = [(list(range(n_inputs)), True)]
    for _ in range(3):
        ord_i = list(range(n_inputs))
        rng.shuffle(ord_i)
        orders.append((ord_i, False))

    best: Optional[XAGCircuit] = None
    for var_ord, greedy in orders:
        cand, ev = _davio_synthesize(n_inputs, clean_targets, var_ord, use_greedy_var=greedy)
        evals_used += ev
        if best is None or cand.gate_count() < best.gate_count():
            best = cand
    assert best is not None

    # Build unified cut-rewrite index from L plus verified RHS patterns of T
    rw_macros: List[Macro] = [rw.rhs_as_macro() for rw in rewrites] if rewrites else []
    all_rw_pool: List[Macro] = list(macros) + rw_macros
    lib_index = _LibraryIndex(all_rw_pool) if all_rw_pool else None

    # Stage 2a: Invertible GF(2) Linear-Basis Preconditioning (if enabled in strategy S)
    if enable_linear_precond and evals_used < budget:
        lp_c, lp_ev = _linear_precond_davio(
            n_inputs, clean_targets, lib_index=lib_index, budget_left=(budget - evals_used) // 3
        )
        evals_used += lp_ev
        if lp_c is not None and lp_c.gate_count() < best.gate_count():
            best = lp_c

    # Stage 2b: Exact Macro Functional Factorization over L
    if macros and evals_used < budget:
        fac_c, fac_ev = _factor_with_library(
            n_inputs, clean_targets, macros,
            budget_left=(budget - evals_used) // 2,
            allow_bijective=enable_bijective_factor,
            max_depth=max_factor_depth,
        )
        evals_used += fac_ev
        if fac_c is not None and fac_c.gate_count() < best.gate_count():
            best = fac_c

    # Stage 2c: Library-accelerated Davio leaves
    if lib_index is not None and evals_used < budget:
        for var_ord, greedy in orders:
            if evals_used >= budget:
                break
            cand, ev = _davio_synthesize(
                n_inputs, clean_targets, var_ord, use_greedy_var=greedy, lib_index=lib_index
            )
            evals_used += ev
            if cand.gate_count() < best.gate_count():
                best = cand

    # Stage 2d: Monotonic k-cut NPN4 / multi-output + global-strash RewriteRule (`T`) pass
    if lib_index is not None and evals_used < budget:
        # When bridge rewrites are enabled, include BOTH lhs and rhs of equal-gate rules in `T`
        # so algebraic factoring can fire in either direction whenever global StrashBuilder shrinks!
        if enable_bridge_rewrites and rewrites:
            bridge_pool = list(all_rw_pool)
            for rw in rewrites:
                lhs_c = XAGCircuit(n_inputs=rw.n_inputs, gates=rw.lhs_gates, outputs=rw.lhs_outputs)
                bridge_pool.append(Macro.from_circuit(f"rwl_{rw.name}", lhs_c, origin=rw.origin))
            rw_index = _LibraryIndex(bridge_pool)
        else:
            rw_index = lib_index
        best, rw_evals, _n_acc = _monotonic_rewrite_pass(
            best, clean_targets, rw_index, budget_left=budget - evals_used
        )
        evals_used += rw_evals

    dt = time.perf_counter() - t0
    if meter is not None:
        meter.charge_evals(evals_used, phase=phase)
        meter.charge_cpu(dt, phase=phase)
    assert verify_truth_tables(best, clean_targets, meter=meter, phase=f"{phase}_verify"), (
        "Synthesized circuit failed exact truth-table verification!"
    )
    return best


def synthesize_with_library(
    n_inputs: int,
    targets: Sequence[int],
    library: Sequence[Macro] = (),
    budget: int = 8000,
    seed: int = 0,
    meter: Optional[object] = None,
    phase: str = "synth",
) -> XAGCircuit:
    """Backward-compatible wrapper: monotonic synthesis using a plain Macro library (default strategy)."""
    if not library:
        return synthesize_with_artifact(
            n_inputs, targets, artifact=None, budget=budget, seed=seed, meter=meter, phase=phase
        )

    class _LibShim:
        def __init__(self, m: Sequence[Macro]) -> None:
            self.macros = tuple(m)
            self.rewrites = ()
            self.strategy = None

    return synthesize_with_artifact(
        n_inputs, targets, artifact=_LibShim(library), budget=budget, seed=seed, meter=meter, phase=phase
    )
