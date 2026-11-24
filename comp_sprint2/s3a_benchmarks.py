"""Phase 3 Track S3-A Fresh Sealed Benchmarks: 7-to-9 Input Hard Multi-Output XAG Circuits (80 tasks).

Designed specifically for **3-Generation Compounding (G1 -> G2 -> G3)** on expanding dev curricula
evaluated on ONE shared 40-task brand-new untouched holdout (ZERO overlap with Sprint 1 OR Sprint 2!).

Splits (80 tasks total, all 6..9 inputs, 64..512-bit exact truth tables):
  EXPANDING DEV CURRICULUM (40 tasks = 30 expanding train [10 G1 + 10 G2 + 10 G3] + 10 hidden dev_val):
    - s3a_dev_g1  (10): 6-7 input structured + procedural starter curriculum
    - s3a_dev_g2  (10): 7-8 input harder structured + procedural expansion
    - s3a_dev_g3  (10): 8-9 input hardest structured + procedural expansion
    - s3a_dev_val (10): hidden internal validation split (5 structured + 5 procedural, 7-9 inputs; NEVER shown in prompts!)
  SHARED UNTOUCHED FINAL HOLDOUT (40 brand-new tasks across 3 strata; evaluated by ALL frozen checkpoints A0..G3):
    - s3a_hold_struct      (14): brand-new 7-9 input arithmetic, GF(16), sorting, modulo, datapath, crypto
    - s3a_hold_proc_shared (14): 100% procedural 7-9 input uniform random shared-cone DAGs (disjoint seed)
    - s3a_hold_proc_comp   (12): 100% procedural 7-9 input deep alien-cell compositional DAGs (disjoint seed)
"""
from __future__ import annotations

import hashlib
import json
import random
from typing import Dict, List, Sequence, Tuple

from comp_sprint.benchmarks import BenchmarkTask, _bits, _from_fn, _gf16_inv, _gf16_mul_const, _popcount, _sort_bits
from comp_sprint.circuit import StrashBuilder, XAGCircuit, full_mask
from comp_sprint2.s2a_benchmarks import (
    _alu2_4op,
    _bcd_add_1dig,
    _keccak_chi_n,
    _sample_alien_cells_4to2,
    _sample_deep_comp_dag,
    _sample_hard_shared_dag,
)


def _sample_hard_shared_7to9(rng: random.Random, n_in: int, n_out: int) -> XAGCircuit:
    core = 22 if n_in == 7 else (26 if n_in == 8 else 30)
    return _sample_hard_shared_dag(rng, n_inputs=n_in, n_outputs=n_out, n_shared_core=core, n_head=5)


def _sample_deep_comp_7to9(rng: random.Random, cells: Sequence[XAGCircuit], n_in: int, n_out: int) -> XAGCircuit:
    if n_in <= 8:
        return _sample_deep_comp_dag(rng, cells, n_inputs=n_in, n_outputs=n_out)
    # 9-input deep 3-layer alien-cell DAG: two disjoint 4-in cells + leftover wire -> layer1 (5 wires) -> layer2 cell -> glue!
    b = StrashBuilder(n_in)
    wires: List[Tuple[int, bool]] = [(i, False) for i in range(n_in)]

    def apply_cell(cell: XAGCircuit, args: Sequence[Tuple[int, bool]]) -> List[Tuple[int, bool]]:
        cmap: Dict[int, Tuple[int, bool]] = {-1: (-1, False)}
        for idx, (wn, wi) in enumerate(args):
            cmap[idx] = (wn, wi ^ rng.choice((False, True)))
        for gi, g in enumerate(cell.gates):
            ln, li = cmap[g.left]
            rn, ri = cmap[g.right]
            cmap[cell.n_inputs + gi] = b.add_gate(g.op, ln, li ^ g.left_inv, rn, ri ^ g.right_inv)
        return [(cmap[on][0], cmap[on][1] ^ oi) for on, oi in cell.outputs]

    perm = list(range(n_in))
    rng.shuffle(perm)
    o1 = apply_cell(rng.choice(cells), [wires[perm[i]] for i in range(4)])
    o2 = apply_cell(rng.choice(cells), [wires[perm[i]] for i in range(4, 8)])
    l1 = o1 + o2 + [wires[perm[8]]]  # 5 wires
    rng.shuffle(l1)
    o3 = apply_cell(rng.choice(cells), l1[:4])
    pool = l1 + o3
    for _ in range(4):
        op = rng.choice(("XOR", "AND"))
        (u, ui), (v, vi) = rng.sample(pool, 2)
        pool.append(b.add_gate(op, u, ui ^ rng.choice((False, True)), v, vi ^ rng.choice((False, True))))
    chosen = rng.sample(pool[-max(n_out, 6):], n_out)
    return b.build([(n, inv ^ rng.choice((False, True))) for n, inv in chosen], prune_dead=True)


def build_s3a_benchmarks() -> Dict[str, List[BenchmarkTask]]:
    """Build fresh sealed 80-task Phase 3 Track S3-A (7..9 input XAG) manifest."""
    alien_s3 = _sample_alien_cells_4to2(motif_seed=2026112490)

    def gen_sh(seed: int, split: str, prefix: str, count: int, arities: Sequence[int]) -> List[BenchmarkTask]:
        rng = random.Random(seed)
        out: List[BenchmarkTask] = []
        idx = 0
        while len(out) < count:
            n_in = arities[len(out) % len(arities)]
            n_out = 4
            c = _sample_hard_shared_7to9(rng, n_in, n_out)
            tts = c.truth_tables()
            mask = full_mask(n_in)
            nr = 1 << n_in
            if len(set(tts)) < n_out or any(t in (0, mask) for t in tts):
                continue
            if any(not (0.14 * nr <= t.bit_count() <= 0.86 * nr) for t in tts):
                continue
            if c.gate_count() < 24:
                continue
            out.append(BenchmarkTask(
                f"{prefix}_{idx:02d}_n{n_in}m{n_out}", "proc_shared", split, n_in, tts,
                f"Phase3 7-9in procedural shared-cone DAG (seed={seed})", hidden_witness_gates=c.gate_count(),
            ))
            idx += 1
        return out

    def gen_cp(seed: int, split: str, prefix: str, count: int, arities: Sequence[int]) -> List[BenchmarkTask]:
        rng = random.Random(seed)
        out: List[BenchmarkTask] = []
        idx = 0
        while len(out) < count:
            n_in = arities[len(out) % len(arities)]
            n_out = 4
            c = _sample_deep_comp_7to9(rng, alien_s3, n_in, n_out)
            tts = c.truth_tables()
            mask = full_mask(n_in)
            nr = 1 << n_in
            if len(set(tts)) < n_out or any(t in (0, mask) for t in tts):
                continue
            if any(not (0.12 * nr <= t.bit_count() <= 0.88 * nr) for t in tts):
                continue
            if c.gate_count() < 18:
                continue
            out.append(BenchmarkTask(
                f"{prefix}_{idx:02d}_n{n_in}m{n_out}", "proc_comp", split, n_in, tts,
                f"Phase3 7-9in procedural deep alien-cell DAG (seed={seed})", hidden_witness_gates=c.gate_count(),
            ))
            idx += 1
        return out

    # --- Expanding Dev Curriculum (G1: 6-7in, G2: 7-8in, G3: 8-9in) ---
    dev_g1_struct = [
        BenchmarkTask("s3a_g1_add3_cin", "structured", "dev", 7,
                      _from_fn(7, 4, lambda r: _bits((r & 7) + ((r >> 3) & 7) + ((r >> 6) & 1), 4)),
                      "3-bit adder with carry-in (7->4)"),
        BenchmarkTask("s3a_g1_mul3x3", "structured", "dev", 6,
                      _from_fn(6, 6, lambda r: _bits((r & 7) * ((r >> 3) & 7), 6)),
                      "3x3 multiplier (6->6)"),
        BenchmarkTask("s3a_g1_popcount7", "structured", "dev", 7,
                      _from_fn(7, 3, lambda r: _popcount(r, 7, 3)),
                      "7-bit population count (7->3)"),
        BenchmarkTask("s3a_g1_sort6", "structured", "dev", 6,
                      _from_fn(6, 6, lambda r: _sort_bits(r, 6)),
                      "6-bit sorting network (6->6)"),
        BenchmarkTask("s3a_g1_mod3_7bit", "structured", "dev", 7,
                      _from_fn(7, 2, lambda r: _bits(r % 3, 2)),
                      "7-bit integer modulo 3 (7->2)"),
    ]
    dev_g1 = dev_g1_struct + gen_sh(2026112501, "dev", "s3a_g1_sh", 3, (7,)) + gen_cp(2026112502, "dev", "s3a_g1_cp", 2, (7,))

    dev_g2_struct = [
        BenchmarkTask("s3a_g2_gf16_mul", "structured", "dev", 8,
                      _from_fn(8, 4, lambda r: _bits(_gf16_mul_const(r & 0xF, (r >> 4) & 0xF), 4)),
                      "GF(2^4) full 4x4 multiplier (8->4)"),
        BenchmarkTask("s3a_g2_bcd_add", "structured", "dev", 8,
                      _from_fn(8, 5, _bcd_add_1dig),
                      "1-digit BCD adder with decimal correction (8->5)"),
        BenchmarkTask("s3a_g2_prio_enc8", "structured", "dev", 8,
                      _from_fn(8, 4, lambda r: _bits(0 if r == 0 else r.bit_length(), 4)),
                      "8-bit priority encoder (8->4)"),
        BenchmarkTask("s3a_g2_rot4_bidir", "structured", "dev", 7,
                      _from_fn(7, 4, lambda r: _bits(
                          ((((r & 0xF) << ((r >> 4) & 3)) | ((r & 0xF) >> (4 - ((r >> 4) & 3)))) & 0xF)
                          if ((r >> 6) & 1) == 0 else
                          ((((r & 0xF) >> ((r >> 4) & 3)) | ((r & 0xF) << (4 - ((r >> 4) & 3)))) & 0xF), 4)),
                      "4-bit bidirectional barrel rotator (7->4)"),
        BenchmarkTask("s3a_g2_mod6_8bit", "structured", "dev", 8,
                      _from_fn(8, 3, lambda r: _bits(r % 6, 3)),
                      "8-bit integer modulo 6 (8->3)"),
    ]
    dev_g2 = dev_g2_struct + gen_sh(2026112503, "dev", "s3a_g2_sh", 3, (7, 8)) + gen_cp(2026112504, "dev", "s3a_g2_cp", 2, (8,))

    dev_g3_struct = [
        BenchmarkTask("s3a_g3_mul4x3_hi", "structured", "dev", 8,
                      _from_fn(8, 4, lambda r: _bits((((r & 0xF) * ((r >> 4) & 0xF)) >> 4) & 0xF, 4)),
                      "4x4 multiplier upper 4 bits (8->4)"),
        BenchmarkTask("s3a_g3_sort8_lo4", "structured", "dev", 8,
                      _from_fn(8, 4, lambda r: _sort_bits(r, 8)[:4]),
                      "8-bit sorting network lower 4 threshold bits (8->4)"),
        BenchmarkTask("s3a_g3_popcount8_mod3", "structured", "dev", 8,
                      _from_fn(8, 3, lambda r: _bits(r.bit_count() % 3, 2) + [int(r.bit_count() >= 5)]),
                      "8-bit popcount mod 3 + threshold >=5 (8->3)"),
        BenchmarkTask("s3a_g3_min4_lt", "structured", "dev", 8,
                      _from_fn(8, 5, lambda r: _bits(min(r & 0xF, (r >> 4) & 0xF), 4) + [int((r & 0xF) < ((r >> 4) & 0xF))]),
                      "4-bit min(a,b) plus (a<b) flag (8->5)"),
        BenchmarkTask("s3a_g3_mod5_9bit", "structured", "dev", 9,
                      _from_fn(9, 3, lambda r: _bits(r % 5, 3)),
                      "9-bit integer modulo 5 (9->3)"),
    ]
    dev_g3 = dev_g3_struct + gen_sh(2026112505, "dev", "s3a_g3_sh", 3, (8, 9)) + gen_cp(2026112506, "dev", "s3a_g3_cp", 2, (8, 9))

    # --- Internal Hidden dev_val (10 tasks: 5 structured + 3 proc_shared + 2 proc_comp; NEVER in prompts!) ---
    dev_val_struct = [
        BenchmarkTask("s3a_val_alu2_4op", "structured", "dev", 6, _from_fn(6, 3, _alu2_4op), "2-bit 4-op ALU (6->3)"),
        BenchmarkTask("s3a_val_mod7_7bit", "structured", "dev", 7, _from_fn(7, 3, lambda r: _bits(r % 7, 3)), "7-bit mod 7 (7->3)"),
        BenchmarkTask("s3a_val_hamming_4x2", "structured", "dev", 8,
                      _from_fn(8, 3, lambda r: _bits(((r & 0xF) ^ ((r >> 4) & 0xF)).bit_count(), 3)),
                      "Hamming distance between two 4-bit words (8->3)"),
        BenchmarkTask("s3a_val_div3_8bit", "structured", "dev", 8,
                      _from_fn(8, 4, lambda r: _bits((r // 3) & 0xF, 4)),
                      "8-bit integer floor(x/3) low 4 bits (8->4)"),
        BenchmarkTask("s3a_val_thresh9_ge3456", "structured", "dev", 9,
                      _from_fn(9, 4, lambda r: [int(r.bit_count() >= k) for k in (3, 4, 5, 6)]),
                      "9-bit multi-threshold (>=3,>=4,>=5,>=6) (9->4)"),
    ]
    dev_val = dev_val_struct + gen_sh(2026112507, "dev", "s3a_val_sh", 3, (7, 8, 9)) + gen_cp(2026112508, "dev", "s3a_val_cp", 2, (8, 9))

    # --- Shared Brand-New 40-Task Untouched Final Holdout (evaluated by ALL frozen checkpoints!) ---
    hold_struct = [
        BenchmarkTask("s3a_hold_add4_cin", "structured", "holdout", 9,
                      _from_fn(9, 5, lambda r: _bits((r & 0xF) + ((r >> 4) & 0xF) + ((r >> 8) & 1), 5)),
                      "4-bit unsigned adder with carry-in (9->5)"),
        BenchmarkTask("s3a_hold_sub4_bin", "structured", "holdout", 9,
                      _from_fn(9, 5, lambda r: _bits(((r & 0xF) - ((r >> 4) & 0xF) - ((r >> 8) & 1)) & 0x1F, 5)),
                      "4-bit unsigned subtractor with borrow-in (9->5)"),
        BenchmarkTask("s3a_hold_mul4x4_lo5", "structured", "holdout", 8,
                      _from_fn(8, 5, lambda r: _bits(((r & 0xF) * ((r >> 4) & 0xF)) & 0x1F, 5)),
                      "4x4 multiplier lower 5 bits (8->5)"),
        BenchmarkTask("s3a_hold_mul4x4_mid4", "structured", "holdout", 8,
                      _from_fn(8, 4, lambda r: _bits((((r & 0xF) * ((r >> 4) & 0xF)) >> 2) & 0xF, 4)),
                      "4x4 multiplier middle 4 bits [5:2] (8->4)"),
        BenchmarkTask("s3a_hold_popcount9", "structured", "holdout", 9,
                      _from_fn(9, 4, lambda r: _popcount(r, 9, 4)),
                      "9-bit population count (9->4)"),
        BenchmarkTask("s3a_hold_sort8_top4", "structured", "holdout", 8,
                      _from_fn(8, 4, lambda r: _sort_bits(r, 8)[4:]),
                      "8-bit sorting network top 4 threshold bits (8->4)"),
        BenchmarkTask("s3a_hold_absdiff4", "structured", "holdout", 8,
                      _from_fn(8, 4, lambda r: _bits(abs((r & 0xF) - ((r >> 4) & 0xF)), 4)),
                      "4-bit unsigned absolute difference |a-b| (8->4)"),
        BenchmarkTask("s3a_hold_max4", "structured", "holdout", 8,
                      _from_fn(8, 4, lambda r: _bits(max(r & 0xF, (r >> 4) & 0xF), 4)),
                      "4-bit unsigned maximum max(a,b) (8->4)"),
        BenchmarkTask("s3a_hold_add4_sat", "structured", "holdout", 8,
                      _from_fn(8, 4, lambda r: _bits(min(15, (r & 0xF) + ((r >> 4) & 0xF)), 4)),
                      "4-bit saturating unsigned adder min(15, a+b) (8->4)"),
        BenchmarkTask("s3a_hold_mod7_8bit", "structured", "holdout", 8,
                      _from_fn(8, 3, lambda r: _bits(r % 7, 3)),
                      "8-bit integer modulo 7 (8->3)"),
        BenchmarkTask("s3a_hold_mod3_9bit", "structured", "holdout", 9,
                      _from_fn(9, 2, lambda r: _bits(r % 3, 2)),
                      "9-bit integer modulo 3 (9->2)"),
        BenchmarkTask("s3a_hold_gf16_div", "structured", "holdout", 8,
                      _from_fn(8, 4, lambda r: _bits(_gf16_mul_const(_gf16_inv(r & 0xF), (r >> 4) & 0xF), 4)),
                      "GF(2^4) division b * inv(a) mod x^4+x+1 (8->4)"),
        BenchmarkTask("s3a_hold_keccak_chi9", "structured", "holdout", 9,
                      _from_fn(9, 9, lambda r: _keccak_chi_n(r, 9)),
                      "9-bit Keccak chi nonlinear layer (9->9)"),
        BenchmarkTask("s3a_hold_clz8", "structured", "holdout", 8,
                      _from_fn(8, 4, lambda r: _bits(8 if r == 0 else (8 - r.bit_length()), 4)),
                      "8-bit count-leading-zeros CLZ (8->4)"),
    ]
    hold_sh = gen_sh(2026112521, "holdout", "s3a_hold_sh", 14, (7, 8, 9))
    hold_cp = gen_cp(2026112523, "holdout", "s3a_hold_cp", 12, (7, 8, 9))

    return {
        "s3a_dev_g1": dev_g1,
        "s3a_dev_g2": dev_g2,
        "s3a_dev_g3": dev_g3,
        "s3a_dev_val": dev_val,
        "s3a_hold_struct": hold_struct,
        "s3a_hold_proc_shared": hold_sh,
        "s3a_hold_proc_comp": hold_cp,
    }


def s3a_manifest_sha256(suites: Dict[str, List[BenchmarkTask]]) -> str:
    payload = {k: [t.public_dict() for t in v] for k, v in sorted(suites.items())}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
