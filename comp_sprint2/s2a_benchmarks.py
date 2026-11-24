"""Track S2-A Fresh Sealed Benchmarks: Hard 6-to-8-Input Multi-Output XAG Circuits (52 tasks).

ZERO overlap with Sprint 1 (4..6-input tasks). Every target here has 6..8 inputs (64..256-bit
exhaustive truth tables -> microsecond exact verification, 30..250+ primitive XAG gates of headroom).

Splits (52 tasks):
  DEV (24 tasks; internal dev_train = [0..7] per suite [16], dev_val = [8..11] per suite [8]):
    - s2a_dev_struct (12): hard 6-8 input arithmetic, finite-field, crypto, and datapath circuits
    - s2a_dev_proc   (12): 100% procedural 6-8 input shared-cone & compositional alien-cell DAGs
  UNTOUCHED HOLDOUT (28 brand-new tasks across 3 strata):
    - s2a_hold_struct      (10): brand-new 6-8 input arithmetic, GF(16), sorting, modulo, crypto
    - s2a_hold_proc_shared (10): 100% procedural 7-8 input uniform random shared-cone DAGs
    - s2a_hold_proc_comp    (8): 100% procedural 7-8 input deep alien-cell compositional DAGs
"""
from __future__ import annotations

import hashlib
import json
import random
from typing import Dict, List, Sequence, Tuple

from comp_sprint.benchmarks import BenchmarkTask, _bits, _from_fn, _gf16_mul_const, _popcount, _sort_bits
from comp_sprint.circuit import StrashBuilder, XAGCircuit, full_mask


def _keccak_chi_n(x: int, n: int) -> List[int]:
    b = _bits(x, n)
    return [b[i] ^ ((1 - b[(i + 1) % n]) & b[(i + 2) % n]) for i in range(n)]


def _bcd_add_1dig(r: int) -> List[int]:
    # 8-in -> 5-out: 4-bit a (0..15) + 4-bit b (0..15) with BCD decimal correction (+6 if sum >= 10)
    a = r & 0xF
    b = (r >> 4) & 0xF
    s = a + b
    if s >= 10:
        s += 6
    return _bits(s & 0x1F, 5)


def _alu2_4op(r: int) -> List[int]:
    # 6-in -> 3-out: a(2), b(2), op(2) -> 0:a+b, 1:(a-b)&7, 2:a&b, 3:a^b
    a = r & 3
    b = (r >> 2) & 3
    op = (r >> 4) & 3
    if op == 0:
        v = a + b
    elif op == 1:
        v = (a - b) & 7
    elif op == 2:
        v = a & b
    else:
        v = a ^ b
    return _bits(v, 3)


def _sample_hard_shared_dag(
    rng: random.Random,
    n_inputs: int,
    n_outputs: int,
    n_shared_core: int,
    n_head: int,
) -> XAGCircuit:
    b = StrashBuilder(n_inputs)
    core: List[Tuple[int, bool]] = []
    pool: List[Tuple[int, bool]] = [(i, False) for i in range(n_inputs)]
    for _ in range(n_shared_core):
        op = rng.choice(("AND", "AND", "XOR"))
        (u, ui), (v, vi) = rng.sample(pool, 2)
        nd = b.add_gate(op, u, ui ^ rng.choice((False, True)), v, vi ^ rng.choice((False, True)))
        core.append(nd)
        pool.append(nd)
    outs: List[Tuple[int, bool]] = []
    for _ in range(n_outputs):
        lpool = list(pool)
        cur = rng.choice(core[-min(len(core), 10):])
        for _ in range(n_head):
            op = rng.choice(("AND", "AND", "XOR"))
            other = rng.choice([p for p in lpool if p[0] != cur[0]])
            cur = b.add_gate(op, cur[0], cur[1] ^ rng.choice((False, True)), other[0], other[1] ^ rng.choice((False, True)))
            lpool.append(cur)
        outs.append((cur[0], cur[1] ^ rng.choice((False, True))))
    return b.build(outs, prune_dead=True)


def _sample_alien_cells_4to2(motif_seed: int = 2026112400) -> List[XAGCircuit]:
    """Sample 3 PRNG 4-in 2-out non-human XAG cells (5..7 primitive gates, ZERO LLM)."""
    rng = random.Random(motif_seed)
    cells: List[XAGCircuit] = []
    seen = set()
    while len(cells) < 3:
        b = StrashBuilder(4)
        pool: List[Tuple[int, bool]] = [(i, False) for i in range(4)]
        for step in range(6):
            op = "AND" if (step in (0, 2, 4) or rng.random() < 0.6) else "XOR"
            (u, ui), (v, vi) = rng.sample(pool, 2)
            pool.append(b.add_gate(op, u, ui ^ rng.choice((False, True)), v, vi ^ rng.choice((False, True))))
        g_nodes = [p for p in pool if p[0] >= 4]
        if len(g_nodes) < 3:
            continue
        outs = [(n, inv ^ rng.choice((False, True))) for n, inv in rng.sample(g_nodes[-4:], 2)]
        c = b.build(outs, prune_dead=True)
        if not (4 <= c.gate_count() <= 7) or c.and_count() < 2:
            continue
        tts = c.truth_tables()
        if len(set(tts)) < 2 or any(not (4 <= t.bit_count() <= 12) for t in tts):
            continue
        sig = tuple(sorted(min(t, t ^ 0xFFFF) for t in tts))
        if sig in seen:
            continue
        seen.add(sig)
        cells.append(c)
    return cells


def _sample_deep_comp_dag(
    rng: random.Random,
    cells: Sequence[XAGCircuit],
    n_inputs: int,
    n_outputs: int,
) -> XAGCircuit:
    """Wire 3..4 instances of 4-in/2-out PRNG alien cells across 2..3 layers (7..8 inputs)."""
    b = StrashBuilder(n_inputs)
    wires: List[Tuple[int, bool]] = [(i, False) for i in range(n_inputs)]

    def apply_cell(cell: XAGCircuit, args: Sequence[Tuple[int, bool]]) -> List[Tuple[int, bool]]:
        cmap: Dict[int, Tuple[int, bool]] = {-1: (-1, False)}
        for idx, (wn, wi) in enumerate(args):
            cmap[idx] = (wn, wi ^ rng.choice((False, True)))
        for gi, g in enumerate(cell.gates):
            ln, li = cmap[g.left]
            rn, ri = cmap[g.right]
            cmap[cell.n_inputs + gi] = b.add_gate(g.op, ln, li ^ g.left_inv, rn, ri ^ g.right_inv)
        return [(cmap[on][0], cmap[on][1] ^ oi) for on, oi in cell.outputs]

    # Layer 1: two cell applications over shuffled inputs (reduces 7->5 or 8->4 wires!)
    perm = list(range(n_inputs))
    rng.shuffle(perm)
    out1 = apply_cell(rng.choice(cells), [wires[perm[i]] for i in range(4)])
    rem1 = [wires[perm[i]] for i in range(4, n_inputs)]
    if len(rem1) >= 4:
        out2 = apply_cell(rng.choice(cells), rem1[:4])
        layer1 = out1 + out2 + rem1[4:]
    else:
        # Overlap 1 wire from perm[0..3] if n_inputs == 7
        out2 = apply_cell(rng.choice(cells), rem1 + [wires[perm[0]]])
        layer1 = out1 + out2

    # Layer 2: mix layer1 wires with a 3rd cell + light glue
    rng.shuffle(layer1)
    out3 = apply_cell(rng.choice(cells), layer1[:4])
    pool = layer1 + out3
    for _ in range(3):
        op = rng.choice(("XOR", "AND"))
        (u, ui), (v, vi) = rng.sample(pool, 2)
        pool.append(b.add_gate(op, u, ui ^ rng.choice((False, True)), v, vi ^ rng.choice((False, True))))
    chosen = rng.sample(pool[-max(n_outputs, 5):], n_outputs)
    return b.build([(n, inv ^ rng.choice((False, True))) for n, inv in chosen], prune_dead=True)


def build_s2a_benchmarks() -> Dict[str, List[BenchmarkTask]]:
    """Build fresh sealed 52-task Track S2-A (6-to-8 input hard XAG) benchmark manifest."""
    dev_struct = [
        BenchmarkTask("s2a_dev_add3_cin", "structured", "dev", 7,
                      _from_fn(7, 4, lambda r: _bits((r & 7) + ((r >> 3) & 7) + ((r >> 6) & 1), 4)),
                      "3-bit unsigned adder with carry-in (7->4)"),
        BenchmarkTask("s2a_dev_mul3x3", "structured", "dev", 6,
                      _from_fn(6, 6, lambda r: _bits((r & 7) * ((r >> 3) & 7), 6)),
                      "3x3-bit unsigned multiplier (6->6)"),
        BenchmarkTask("s2a_dev_popcount7", "structured", "dev", 7,
                      _from_fn(7, 3, lambda r: _popcount(r, 7, 3)),
                      "7-bit population count (7->3)"),
        BenchmarkTask("s2a_dev_sort6", "structured", "dev", 6,
                      _from_fn(6, 6, lambda r: _sort_bits(r, 6)),
                      "6-bit sorting network / unary popcount (6->6)"),
        BenchmarkTask("s2a_dev_keccak_chi7", "structured", "dev", 7,
                      _from_fn(7, 7, lambda r: _keccak_chi_n(r, 7)),
                      "7-bit Keccak chi nonlinear layer (7->7)"),
        BenchmarkTask("s2a_dev_min3_lt", "structured", "dev", 6,
                      _from_fn(6, 4, lambda r: _bits(min(r & 7, (r >> 3) & 7), 3) + [int((r & 7) < ((r >> 3) & 7))]),
                      "3-bit min(a,b) plus (a<b) flag (6->4)"),
        BenchmarkTask("s2a_dev_mod3_7bit", "structured", "dev", 7,
                      _from_fn(7, 2, lambda r: _bits(r % 3, 2)),
                      "7-bit integer modulo 3 (7->2)"),
        BenchmarkTask("s2a_dev_gf16_mul", "structured", "dev", 8,
                      _from_fn(8, 4, lambda r: _bits(_gf16_mul_const(r & 0xF, (r >> 4) & 0xF), 4)),
                      "GF(2^4) full 4x4 multiplier mod x^4+x+1 (8->4)"),
        # Internal dev_val slice [8..11] (mixed arithmetic + datapath + crypto!)
        BenchmarkTask("s2a_dev_bcd_add", "structured", "dev", 8,
                      _from_fn(8, 5, _bcd_add_1dig),
                      "1-digit BCD adder with decimal correction (8->5)"),
        BenchmarkTask("s2a_dev_prio_enc8", "structured", "dev", 8,
                      _from_fn(8, 4, lambda r: _bits(0 if r == 0 else r.bit_length(), 4)),
                      "8-bit priority encoder (8->4)"),
        BenchmarkTask("s2a_dev_alu2_4op", "structured", "dev", 6,
                      _from_fn(6, 3, _alu2_4op),
                      "2-bit 4-operation ALU: add/sub/and/xor (6->3)"),
        BenchmarkTask("s2a_dev_rot4_bidir", "structured", "dev", 7,
                      _from_fn(7, 4, lambda r: _bits(
                          ((((r & 0xF) << ((r >> 4) & 3)) | ((r & 0xF) >> (4 - ((r >> 4) & 3)))) & 0xF)
                          if ((r >> 6) & 1) == 0 else
                          ((((r & 0xF) >> ((r >> 4) & 3)) | ((r & 0xF) << (4 - ((r >> 4) & 3)))) & 0xF), 4)),
                      "4-bit bidirectional barrel rotator (7->4)"),
    ]

    hold_struct = [
        BenchmarkTask("s2a_hold_add4", "structured", "holdout", 8,
                      _from_fn(8, 5, lambda r: _bits((r & 0xF) + ((r >> 4) & 0xF), 5)),
                      "4-bit unsigned adder a+b (8->5)"),
        BenchmarkTask("s2a_hold_sub4", "structured", "holdout", 8,
                      _from_fn(8, 5, lambda r: _bits(((r & 0xF) - ((r >> 4) & 0xF)) & 0x1F, 5)),
                      "4-bit unsigned subtractor a-b with borrow (8->5)"),
        BenchmarkTask("s2a_hold_mul4x2", "structured", "holdout", 6,
                      _from_fn(6, 6, lambda r: _bits((r & 0xF) * ((r >> 4) & 3), 6)),
                      "4x2-bit unsigned multiplier (6->6)"),
        BenchmarkTask("s2a_hold_mul4x3", "structured", "holdout", 7,
                      _from_fn(7, 7, lambda r: _bits((r & 0xF) * ((r >> 4) & 7), 7)),
                      "4x3-bit unsigned multiplier (7->7)"),
        BenchmarkTask("s2a_hold_popcount8", "structured", "holdout", 8,
                      _from_fn(8, 4, lambda r: _popcount(r, 8, 4)),
                      "8-bit population count (8->4)"),
        BenchmarkTask("s2a_hold_sort7", "structured", "holdout", 7,
                      _from_fn(7, 7, lambda r: _sort_bits(r, 7)),
                      "7-bit sorting network / unary popcount (7->7)"),
        BenchmarkTask("s2a_hold_cmp4", "structured", "holdout", 8,
                      _from_fn(8, 3, lambda r: [int((r & 0xF) < ((r >> 4) & 0xF)), int((r & 0xF) == ((r >> 4) & 0xF)), int((r & 0xF) > ((r >> 4) & 0xF))]),
                      "4-bit magnitude comparator <,=,> (8->3)"),
        BenchmarkTask("s2a_hold_gf16_mul_sq", "structured", "holdout", 8,
                      _from_fn(8, 4, lambda r: _bits(_gf16_mul_const(r & 0xF, (r >> 4) & 0xF) ^ _gf16_mul_const(r & 0xF, r & 0xF), 4)),
                      "GF(2^4) fused a*b + a^2 mod x^4+x+1 (8->4)"),
        BenchmarkTask("s2a_hold_keccak_chi8", "structured", "holdout", 8,
                      _from_fn(8, 8, lambda r: _keccak_chi_n(r, 8)),
                      "8-bit Keccak chi nonlinear layer (8->8)"),
        BenchmarkTask("s2a_hold_mod5_8bit", "structured", "holdout", 8,
                      _from_fn(8, 3, lambda r: _bits(r % 5, 3)),
                      "8-bit integer modulo 5 (8->3)"),
    ]

    def gen_shared(seed: int, split: str, prefix: str, count: int) -> List[BenchmarkTask]:
        rng = random.Random(seed)
        tasks: List[BenchmarkTask] = []
        idx = 0
        while len(tasks) < count:
            n_in = 7 if (len(tasks) % 2 == 0) else 8
            n_out = 4 if n_in == 7 else 4
            circ = _sample_hard_shared_dag(rng, n_inputs=n_in, n_outputs=n_out, n_shared_core=18, n_head=5)
            tts = circ.truth_tables()
            mask = full_mask(n_in)
            n_rows = 1 << n_in
            if len(set(tts)) < n_out or any(t in (0, mask) for t in tts):
                continue
            if any(not (0.15 * n_rows <= t.bit_count() <= 0.85 * n_rows) for t in tts):
                continue
            if circ.gate_count() < 22:
                continue
            tasks.append(BenchmarkTask(
                task_id=f"{prefix}_{idx:02d}_n{n_in}m{n_out}",
                stratum="proc_shared", split=split, n_inputs=n_in, targets=tts,
                description=f"Hard 7-8in procedural shared-cone DAG (seed={seed})",
                hidden_witness_gates=circ.gate_count(),
            ))
            idx += 1
        return tasks

    alien4 = _sample_alien_cells_4to2(motif_seed=2026112400)

    def gen_comp(seed: int, split: str, prefix: str, count: int) -> List[BenchmarkTask]:
        rng = random.Random(seed)
        tasks: List[BenchmarkTask] = []
        idx = 0
        while len(tasks) < count:
            n_in = 7 if (len(tasks) % 2 == 0) else 8
            n_out = 4
            circ = _sample_deep_comp_dag(rng, alien4, n_inputs=n_in, n_outputs=n_out)
            tts = circ.truth_tables()
            mask = full_mask(n_in)
            n_rows = 1 << n_in
            if len(set(tts)) < n_out or any(t in (0, mask) for t in tts):
                continue
            if any(not (0.12 * n_rows <= t.bit_count() <= 0.88 * n_rows) for t in tts):
                continue
            if circ.gate_count() < 16:
                continue
            tasks.append(BenchmarkTask(
                task_id=f"{prefix}_{idx:02d}_n{n_in}m{n_out}",
                stratum="proc_comp", split=split, n_inputs=n_in, targets=tts,
                description=f"Hard 7-8in procedural alien-cell compositional DAG (seed={seed})",
                hidden_witness_gates=circ.gate_count(),
            ))
            idx += 1
        return tasks

    # Dev procedural = 6 shared + 6 comp interleaved so dev_train[:8] & dev_val[8:] both have both!
    dev_sh = gen_shared(2026112411, "dev", "s2a_dev_sh", 6)
    dev_cp = gen_comp(2026112413, "dev", "s2a_dev_cp", 6)
    dev_proc: List[BenchmarkTask] = []
    for a, b in zip(dev_sh, dev_cp):
        dev_proc.append(a)
        dev_proc.append(b)

    hold_sh = gen_shared(2026112421, "holdout", "s2a_hold_sh", 10)
    hold_cp = gen_comp(2026112423, "holdout", "s2a_hold_cp", 8)

    return {
        "s2a_dev_struct": dev_struct,
        "s2a_dev_proc": dev_proc,
        "s2a_hold_struct": hold_struct,
        "s2a_hold_proc_shared": hold_sh,
        "s2a_hold_proc_comp": hold_cp,
    }


def s2a_manifest_sha256(suites: Dict[str, List[BenchmarkTask]]) -> str:
    payload = {k: [t.public_dict() for t in v] for k, v in sorted(suites.items())}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
