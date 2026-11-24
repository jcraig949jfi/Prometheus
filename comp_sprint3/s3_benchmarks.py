"""Sprint 3 Fresh Sealed Benchmarks: 170-Task 7-to-9 Input Multi-Output XAG Suite.

Fixes Law 2 (Zero Adaptive Goodharting) with 100% disjoint per-generation validation splits:
  - train_g1  (15): visible in Gen 1 prompt (7 structured + 4 proc_shared + 4 proc_comp)
  - val_g1    (25): HIDDEN promotion gate for Gen 1 ONLY (10 structured + 8 proc_shared + 7 proc_comp)
  - train_g2  (15): visible in Gen 2 prompt (7 structured + 4 proc_shared + 4 proc_comp)
  - val_g2    (25): HIDDEN promotion gate for Gen 2 ONLY (10 structured + 8 proc_shared + 7 proc_comp)
  - train_g3  (15): visible in Gen 3 prompt (7 structured + 4 proc_shared + 4 proc_comp)
  - val_g3    (25): HIDDEN promotion gate for Gen 3 ONLY (10 structured + 8 proc_shared + 7 proc_comp)
  - holdout   (50): UNTOUCHED final holdout evaluated ONCE across ALL frozen checkpoints:
      * s3_hold_struct      (18): 7-9 input structured arithmetic/crypto/datapath/threshold/GF/sort
      * s3_hold_proc_shared (16): 100% procedural 7-9in uniform random shared-cone DAGs
      * s3_hold_proc_comp   (16): 100% procedural 7-9in deep alien-cell compositional DAGs

Strict invariant enforced at build time: ZERO duplicate truth-table tuples across all 170 tasks!
"""
from __future__ import annotations

import hashlib
import json
import random
from typing import Dict, List, Sequence, Tuple

from comp_sprint.benchmarks import BenchmarkTask, _bits, _from_fn, _gf16_inv, _gf16_mul_const, _popcount, _sort_bits
from comp_sprint.circuit import full_mask
from comp_sprint2.s2a_benchmarks import _keccak_chi_n, _sample_alien_cells_4to2
from comp_sprint2.s3a_benchmarks import _sample_deep_comp_7to9, _sample_hard_shared_7to9


def _gf16_sq(x: int) -> int:
    return _gf16_mul_const(x & 0xF, x & 0xF)


def _crc4_step(val: int, width: int, poly: int = 0x3) -> List[int]:
    """Compute 4-bit CRC remainder of `width`-bit message with polynomial x^4 + poly."""
    reg = 0
    for i in range(width - 1, -1, -1):
        b = (val >> i) & 1
        top = (reg >> 3) & 1
        reg = ((reg << 1) & 0xF) ^ (poly if (top ^ b) else 0)
    return _bits(reg, 4)


def _gray_encode(x: int, w: int) -> int:
    return (x ^ (x >> 1)) & ((1 << w) - 1)


def _gray_decode(g: int, w: int) -> int:
    x = g
    sh = 1
    while sh < w:
        x ^= (x >> sh)
        sh <<= 1
    return x & ((1 << w) - 1)


def _sbox_present(x: int) -> int:
    t = (0xC, 5, 6, 0xB, 9, 0, 0xA, 0xD, 3, 0xE, 0xF, 8, 4, 7, 1, 2)
    return t[x & 0xF]


def _sbox_skinny(x: int) -> int:
    t = (0xC, 6, 9, 0, 1, 0xA, 2, 0xB, 3, 8, 5, 0xD, 4, 0xE, 7, 0xF)
    return t[x & 0xF]


def _sbox_gift(x: int) -> int:
    t = (1, 0xA, 4, 0xC, 6, 0xF, 3, 9, 2, 0xD, 0xB, 7, 5, 0, 8, 0xE)
    return t[x & 0xF]


def _make_struct_task(tid: str, split: str, n_in: int, n_out: int, fn, desc: str) -> BenchmarkTask:
    return BenchmarkTask(tid, "structured", split, n_in, _from_fn(n_in, n_out, fn), desc)


def build_s3_benchmarks() -> Dict[str, List[BenchmarkTask]]:
    """Build fresh sealed 170-task Sprint 3 XAG benchmark suite with disjoint val_g1/g2/g3."""
    alien_s3 = _sample_alien_cells_4to2(motif_seed=2026112499)

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
                f"Sprint3 7-9in procedural shared-cone DAG (seed={seed})", hidden_witness_gates=c.gate_count(),
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
                f"Sprint3 7-9in procedural deep alien-cell DAG (seed={seed})", hidden_witness_gates=c.gate_count(),
            ))
            idx += 1
        return out

    # ==================== TRAIN G1 (15 tasks: 7 struct + 4 sh + 4 cp) ====================
    train_g1_struct = [
        _make_struct_task("s3_tg1_add3_cin", "dev", 7, 4,
                          lambda r: _bits((r & 7) + ((r >> 3) & 7) + ((r >> 6) & 1), 4),
                          "3-bit adder with carry-in (7->4)"),
        _make_struct_task("s3_tg1_popcount7", "dev", 7, 3,
                          lambda r: _popcount(r, 7, 3),
                          "7-bit population count (7->3)"),
        _make_struct_task("s3_tg1_sort7_lo4", "dev", 7, 4,
                          lambda r: _sort_bits(r, 7)[:4],
                          "7-bit sorting network lower 4 bits (7->4)"),
        _make_struct_task("s3_tg1_mod3_7b", "dev", 7, 2,
                          lambda r: _bits(r % 3, 2),
                          "7-bit mod 3 (7->2)"),
        _make_struct_task("s3_tg1_gf16_mul", "dev", 8, 4,
                          lambda r: _bits(_gf16_mul_const(r & 0xF, (r >> 4) & 0xF), 4),
                          "GF(16) full 4x4 multiplier (8->4)"),
        _make_struct_task("s3_tg1_absdiff4", "dev", 8, 4,
                          lambda r: _bits(abs((r & 0xF) - ((r >> 4) & 0xF)), 4),
                          "4-bit absolute difference |a-b| (8->4)"),
        _make_struct_task("s3_tg1_crc4_7b_p3", "dev", 7, 4,
                          lambda r: _crc4_step(r, 7, 0x3),
                          "7-bit CRC-4 poly=0x3 (7->4)"),
    ]
    train_g1 = train_g1_struct + gen_sh(2026112601, "dev", "s3_tg1_sh", 4, (7, 8)) + gen_cp(2026112602, "dev", "s3_tg1_cp", 4, (7, 8))

    # ==================== VAL G1 (25 tasks: 10 struct + 8 sh + 7 cp; HIDDEN!) ====================
    val_g1_struct = [
        _make_struct_task("s3_vg1_sub3_bin", "val_g1", 7, 4,
                          lambda r: _bits(((r & 7) - ((r >> 3) & 7) - ((r >> 6) & 1)) & 0xF, 4),
                          "3-bit subtractor with borrow-in (7->4)"),
        _make_struct_task("s3_vg1_mul4x3_lo4", "val_g1", 7, 4,
                          lambda r: _bits(((r & 0xF) * ((r >> 4) & 7)) & 0xF, 4),
                          "4x3 multiplier low 4 bits (7->4)"),
        _make_struct_task("s3_vg1_mul4x3_hi3", "val_g1", 7, 3,
                          lambda r: _bits((((r & 0xF) * ((r >> 4) & 7)) >> 4) & 7, 3),
                          "4x3 multiplier upper 3 bits (7->3)"),
        _make_struct_task("s3_vg1_mod5_7b", "val_g1", 7, 3,
                          lambda r: _bits(r % 5, 3),
                          "7-bit mod 5 (7->3)"),
        _make_struct_task("s3_vg1_prio7", "val_g1", 7, 3,
                          lambda r: _bits(0 if r == 0 else r.bit_length(), 3),
                          "7-bit priority encoder (7->3)"),
        _make_struct_task("s3_vg1_min4_eq", "val_g1", 8, 5,
                          lambda r: _bits(min(r & 0xF, (r >> 4) & 0xF), 4) + [int((r & 0xF) == ((r >> 4) & 0xF))],
                          "4-bit min(a,b) + (a==b) (8->5)"),
        _make_struct_task("s3_vg1_hamming4x2", "val_g1", 8, 3,
                          lambda r: _bits(((r & 0xF) ^ ((r >> 4) & 0xF)).bit_count(), 3),
                          "Hamming distance of two 4-bit words (8->3)"),
        _make_struct_task("s3_vg1_keccak7", "val_g1", 7, 7,
                          lambda r: _keccak_chi_n(r, 7),
                          "7-bit Keccak chi nonlinear layer (7->7)"),
        _make_struct_task("s3_vg1_thresh8_246", "val_g1", 8, 3,
                          lambda r: [int(r.bit_count() >= k) for k in (2, 4, 6)],
                          "8-bit thresholds >=2,>=4,>=6 (8->3)"),
        _make_struct_task("s3_vg1_add4_gray", "val_g1", 8, 5,
                          lambda r: _bits(_gray_encode((r & 0xF) + ((r >> 4) & 0xF), 5), 5),
                          "4-bit Gray-encoded sum (8->5)"),
    ]
    val_g1 = val_g1_struct + gen_sh(2026112611, "val_g1", "s3_vg1_sh", 8, (7, 8, 9)) + gen_cp(2026112612, "val_g1", "s3_vg1_cp", 7, (7, 8, 9))

    # ==================== TRAIN G2 (15 tasks: 7 struct + 4 sh + 4 cp) ====================
    train_g2_struct = [
        _make_struct_task("s3_tg2_add4_nosat", "dev", 8, 5,
                          lambda r: _bits((r & 0xF) + ((r >> 4) & 0xF), 5),
                          "4-bit unsigned adder (8->5)"),
        _make_struct_task("s3_tg2_mod6_8b", "dev", 8, 3,
                          lambda r: _bits(r % 6, 3),
                          "8-bit mod 6 (8->3)"),
        _make_struct_task("s3_tg2_div3_8b", "dev", 8, 4,
                          lambda r: _bits((r // 3) & 0xF, 4),
                          "8-bit floor(x/3) low 4 bits (8->4)"),
        _make_struct_task("s3_tg2_rot4_bidir", "dev", 7, 4,
                          lambda r: _bits(
                              ((((r & 0xF) << ((r >> 4) & 3)) | ((r & 0xF) >> (4 - ((r >> 4) & 3)))) & 0xF)
                              if ((r >> 6) & 1) == 0 else
                              ((((r & 0xF) >> ((r >> 4) & 3)) | ((r & 0xF) << (4 - ((r >> 4) & 3)))) & 0xF), 4),
                          "4-bit bidirectional barrel rotator (7->4)"),
        _make_struct_task("s3_tg2_sort8_lo4", "dev", 8, 4,
                          lambda r: _sort_bits(r, 8)[:4],
                          "8-bit sorting network low 4 bits (8->4)"),
        _make_struct_task("s3_tg2_gf16_sqmul", "dev", 8, 4,
                          lambda r: _bits(_gf16_mul_const(_gf16_sq(r & 0xF), (r >> 4) & 0xF), 4),
                          "GF(16) a^2 * b (8->4)"),
        _make_struct_task("s3_tg2_present_xor", "dev", 8, 4,
                          lambda r: _bits(_sbox_present((r & 0xF) ^ ((r >> 4) & 0xF)) ^ (r & 0xF), 4),
                          "PRESENT S-box(a^b)^a Feistel round (8->4)"),
    ]
    train_g2 = train_g2_struct + gen_sh(2026112621, "dev", "s3_tg2_sh", 4, (7, 8, 9)) + gen_cp(2026112622, "dev", "s3_tg2_cp", 4, (7, 8, 9))

    # ==================== VAL G2 (25 tasks: 10 struct + 8 sh + 7 cp; HIDDEN!) ====================
    val_g2_struct = [
        _make_struct_task("s3_vg2_sub4_nosat", "val_g2", 8, 5,
                          lambda r: _bits(((r & 0xF) - ((r >> 4) & 0xF)) & 0x1F, 5),
                          "4-bit unsigned subtractor (8->5)"),
        _make_struct_task("s3_vg2_mul4x4_hi4", "val_g2", 8, 4,
                          lambda r: _bits((((r & 0xF) * ((r >> 4) & 0xF)) >> 4) & 0xF, 4),
                          "4x4 multiplier upper 4 bits (8->4)"),
        _make_struct_task("s3_vg2_mod7_7b", "val_g2", 7, 3,
                          lambda r: _bits(r % 7, 3),
                          "7-bit mod 7 (7->3)"),
        _make_struct_task("s3_vg2_div5_8b", "val_g2", 8, 4,
                          lambda r: _bits((r // 5) & 0xF, 4),
                          "8-bit floor(x/5) low 4 bits (8->4)"),
        _make_struct_task("s3_vg2_popcount8", "val_g2", 8, 4,
                          lambda r: _popcount(r, 8, 4),
                          "8-bit population count (8->4)"),
        _make_struct_task("s3_vg2_clz7", "val_g2", 7, 3,
                          lambda r: _bits(7 if r == 0 else (7 - r.bit_length()), 3),
                          "7-bit count leading zeros (7->3)"),
        _make_struct_task("s3_vg2_max4_gt", "val_g2", 8, 5,
                          lambda r: _bits(max(r & 0xF, (r >> 4) & 0xF), 4) + [int((r & 0xF) > ((r >> 4) & 0xF))],
                          "4-bit max(a,b) + (a>b) (8->5)"),
        _make_struct_task("s3_vg2_alu3_addsub", "val_g2", 7, 4,
                          lambda r: _bits(((r & 7) + ((r >> 3) & 7)) if ((r >> 6) & 1) == 0 else (((r & 7) - ((r >> 3) & 7)) & 0xF), 4),
                          "3-bit add/sub ALU (7->4)"),
        _make_struct_task("s3_vg2_skinny_feistel", "val_g2", 8, 4,
                          lambda r: _bits(_sbox_skinny(r & 0xF) ^ ((r >> 4) & 0xF), 4),
                          "SKINNY S-box Feistel step (8->4)"),
        _make_struct_task("s3_vg2_thresh9_357", "val_g2", 9, 3,
                          lambda r: [int(r.bit_count() >= k) for k in (3, 5, 7)],
                          "9-bit thresholds >=3,>=5,>=7 (9->3)"),
    ]
    val_g2 = val_g2_struct + gen_sh(2026112631, "val_g2", "s3_vg2_sh", 8, (7, 8, 9)) + gen_cp(2026112632, "val_g2", "s3_vg2_cp", 7, (7, 8, 9))

    # ==================== TRAIN G3 (15 tasks: 7 struct + 4 sh + 4 cp) ====================
    train_g3_struct = [
        _make_struct_task("s3_tg3_mod5_9b", "dev", 9, 3,
                          lambda r: _bits(r % 5, 3),
                          "9-bit mod 5 (9->3)"),
        _make_struct_task("s3_tg3_pop8_mod3", "dev", 8, 3,
                          lambda r: _bits(r.bit_count() % 3, 2) + [int(r.bit_count() >= 5)],
                          "8-bit popcount mod 3 + >=5 (8->3)"),
        _make_struct_task("s3_tg3_add4_sat", "dev", 8, 4,
                          lambda r: _bits(min(15, (r & 0xF) + ((r >> 4) & 0xF)), 4),
                          "4-bit saturating adder (8->4)"),
        _make_struct_task("s3_tg3_gray_add4", "dev", 8, 4,
                          lambda r: _bits((_gray_decode(r & 0xF, 4) + _gray_decode((r >> 4) & 0xF, 4)) & 0xF, 4),
                          "4-bit Gray-decoded sum (8->4)"),
        _make_struct_task("s3_tg3_shift5_var", "dev", 8, 5,
                          lambda r: _bits(((r & 0x1F) << ((r >> 5) & 7)) & 0x1F, 5),
                          "5-bit variable logical left shifter (8->5)"),
        _make_struct_task("s3_tg3_gf16_affine", "dev", 8, 4,
                          lambda r: _bits(_gf16_mul_const(r & 0xF, ((r >> 4) & 0xF) ^ 0x9) ^ 0x5, 4),
                          "GF(16) affine multiply a*(b^9)^5 (8->4)"),
        _make_struct_task("s3_tg3_maj9_par", "dev", 9, 3,
                          lambda r: [int(r.bit_count() >= 5), int(r.bit_count() >= 3), r.bit_count() & 1],
                          "9-bit majority + >=3 + parity (9->3)"),
    ]
    train_g3 = train_g3_struct + gen_sh(2026112641, "dev", "s3_tg3_sh", 4, (8, 9)) + gen_cp(2026112642, "dev", "s3_tg3_cp", 4, (8, 9))

    # ==================== VAL G3 (25 tasks: 10 struct + 8 sh + 7 cp; HIDDEN!) ====================
    val_g3_struct = [
        _make_struct_task("s3_vg3_sub4_sat", "val_g3", 8, 4,
                          lambda r: _bits(max(0, (r & 0xF) - ((r >> 4) & 0xF)), 4),
                          "4-bit saturating subtractor max(0, a-b) (8->4)"),
        _make_struct_task("s3_vg3_mod9_8b", "val_g3", 8, 4,
                          lambda r: _bits(r % 9, 4),
                          "8-bit mod 9 (8->4)"),
        _make_struct_task("s3_vg3_mod6_9b", "val_g3", 9, 3,
                          lambda r: _bits(r % 6, 3),
                          "9-bit mod 6 (9->3)"),
        _make_struct_task("s3_vg3_sort8_mid4", "val_g3", 8, 4,
                          lambda r: _sort_bits(r, 8)[2:6],
                          "8-bit sorting network middle 4 bits (8->4)"),
        _make_struct_task("s3_vg3_avg4", "val_g3", 8, 4,
                          lambda r: _bits(((r & 0xF) + ((r >> 4) & 0xF)) >> 1, 4),
                          "4-bit unsigned average (a+b)>>1 (8->4)"),
        _make_struct_task("s3_vg3_ctz8", "val_g3", 8, 4,
                          lambda r: _bits(8 if r == 0 else ((r & -r).bit_length() - 1), 4),
                          "8-bit count trailing zeros CTZ (8->4)"),
        _make_struct_task("s3_vg3_mux4_2x4", "val_g3", 9, 4,
                          lambda r: _bits((r & 0xF) if ((r >> 8) & 1) == 0 else ((r >> 4) & 0xF), 4),
                          "4-bit 2-to-1 MUX (9->4)"),
        _make_struct_task("s3_vg3_gift_feistel", "val_g3", 8, 4,
                          lambda r: _bits(_sbox_gift((r & 0xF) ^ ((r >> 4) & 0xF)) ^ ((r >> 4) & 0xF), 4),
                          "GIFT S-box Feistel round (8->4)"),
        _make_struct_task("s3_vg3_crc4_8b_p9", "val_g3", 8, 4,
                          lambda r: _crc4_step(r, 8, 0x9),
                          "8-bit CRC-4 poly=0x9 (8->4)"),
        _make_struct_task("s3_vg3_keccak8", "val_g3", 8, 8,
                          lambda r: _keccak_chi_n(r, 8),
                          "8-bit Keccak chi nonlinear layer (8->8)"),
    ]
    val_g3 = val_g3_struct + gen_sh(2026112651, "val_g3", "s3_vg3_sh", 8, (7, 8, 9)) + gen_cp(2026112652, "val_g3", "s3_vg3_cp", 7, (7, 8, 9))

    # ==================== UNTOUCHED FINAL HOLDOUT (50 tasks: 18 struct + 16 sh + 16 cp) ====================
    hold_struct = [
        _make_struct_task("s3_hold_add4_cin", "holdout", 9, 5,
                          lambda r: _bits((r & 0xF) + ((r >> 4) & 0xF) + ((r >> 8) & 1), 5),
                          "4-bit adder with carry-in (9->5)"),
        _make_struct_task("s3_hold_sub4_bin", "holdout", 9, 5,
                          lambda r: _bits(((r & 0xF) - ((r >> 4) & 0xF) - ((r >> 8) & 1)) & 0x1F, 5),
                          "4-bit subtractor with borrow-in (9->5)"),
        _make_struct_task("s3_hold_mul4x4_lo5", "holdout", 8, 5,
                          lambda r: _bits(((r & 0xF) * ((r >> 4) & 0xF)) & 0x1F, 5),
                          "4x4 multiplier lower 5 bits (8->5)"),
        _make_struct_task("s3_hold_mul4x4_mid4", "holdout", 8, 4,
                          lambda r: _bits((((r & 0xF) * ((r >> 4) & 0xF)) >> 2) & 0xF, 4),
                          "4x4 multiplier middle 4 bits (8->4)"),
        _make_struct_task("s3_hold_popcount9", "holdout", 9, 4,
                          lambda r: _popcount(r, 9, 4),
                          "9-bit population count (9->4)"),
        _make_struct_task("s3_hold_sort8_top4", "holdout", 8, 4,
                          lambda r: _sort_bits(r, 8)[4:],
                          "8-bit sorting network top 4 bits (8->4)"),
        _make_struct_task("s3_hold_sort9_mid4", "holdout", 9, 4,
                          lambda r: _sort_bits(r, 9)[2:6],
                          "9-bit sorting network middle 4 bits (9->4)"),
        _make_struct_task("s3_hold_mod7_8b", "holdout", 8, 3,
                          lambda r: _bits(r % 7, 3),
                          "8-bit mod 7 (8->3)"),
        _make_struct_task("s3_hold_mod3_9b", "holdout", 9, 2,
                          lambda r: _bits(r % 3, 2),
                          "9-bit mod 3 (9->2)"),
        _make_struct_task("s3_hold_mod7_9b", "holdout", 9, 3,
                          lambda r: _bits(r % 7, 3),
                          "9-bit mod 7 (9->3)"),
        _make_struct_task("s3_hold_div6_8b", "holdout", 8, 4,
                          lambda r: _bits((r // 6) & 0xF, 4),
                          "8-bit floor(x/6) low 4 bits (8->4)"),
        _make_struct_task("s3_hold_gf16_div", "holdout", 8, 4,
                          lambda r: _bits(_gf16_mul_const(_gf16_inv(r & 0xF), (r >> 4) & 0xF), 4),
                          "GF(16) division b*inv(a) (8->4)"),
        _make_struct_task("s3_hold_keccak9", "holdout", 9, 9,
                          lambda r: _keccak_chi_n(r, 9),
                          "9-bit Keccak chi nonlinear layer (9->9)"),
        _make_struct_task("s3_hold_clz8", "holdout", 8, 4,
                          lambda r: _bits(8 if r == 0 else (8 - r.bit_length()), 4),
                          "8-bit count leading zeros CLZ (8->4)"),
        _make_struct_task("s3_hold_alu4_addsub", "holdout", 9, 5,
                          lambda r: _bits(((r & 0xF) + ((r >> 4) & 0xF)) if ((r >> 8) & 1) == 0 else (((r & 0xF) - ((r >> 4) & 0xF)) & 0x1F), 5),
                          "4-bit add/sub ALU (9->5)"),
        _make_struct_task("s3_hold_crc4_9b_p3", "holdout", 9, 4,
                          lambda r: _crc4_step(r, 9, 0x3),
                          "9-bit CRC-4 poly=0x3 (9->4)"),
        _make_struct_task("s3_hold_rshift5_var", "holdout", 8, 5,
                          lambda r: _bits(((r & 0x1F) >> ((r >> 5) & 7)) & 0x1F, 5),
                          "5-bit variable logical right shifter (8->5)"),
        _make_struct_task("s3_hold_mac3_add3", "holdout", 9, 4,
                          lambda r: _bits((((r & 7) * ((r >> 3) & 7)) + ((r >> 6) & 7)) & 0xF, 4),
                          "3-bit multiply-accumulate (a*b + c) mod 16 (9->4)"),
    ]
    hold_sh = gen_sh(2026112681, "holdout", "s3_hold_sh", 16, (7, 8, 9))
    hold_cp = gen_cp(2026112683, "holdout", "s3_hold_cp", 16, (7, 8, 9))

    suites: Dict[str, List[BenchmarkTask]] = {
        "s3_train_g1": train_g1,
        "s3_val_g1": val_g1,
        "s3_train_g2": train_g2,
        "s3_val_g2": val_g2,
        "s3_train_g3": train_g3,
        "s3_val_g3": val_g3,
        "s3_hold_struct": hold_struct,
        "s3_hold_proc_shared": hold_sh,
        "s3_hold_proc_comp": hold_cp,
    }

    # Strict anti-leakage assertion: ZERO duplicate task_ids and ZERO duplicate truth-table tuples!
    seen_ids = set()
    seen_tts = set()
    for sname, tasks in suites.items():
        for t in tasks:
            assert t.task_id not in seen_ids, f"Duplicate task_id {t.task_id}"
            seen_ids.add(t.task_id)
            key = (t.n_inputs, tuple(t.targets))
            assert key not in seen_tts, f"Duplicate truth table across splits: {t.task_id} in {sname}"
            seen_tts.add(key)

    return suites


def s3_manifest_sha256(suites: Dict[str, List[BenchmarkTask]]) -> str:
    payload = {k: [t.public_dict() for t in v] for k, v in sorted(suites.items())}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
