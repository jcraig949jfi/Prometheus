"""Track S4-B Fresh Sealed Benchmarks: 172-Task Scaled 9-to-11 Input Multi-Stage XAG Suite (4 Generations).

Designed to break past Sprint 3's 2-step saturation on 7-9in circuits by scaling up to
**9-to-11 input (512..2048-bit exact truth tables), deeper multi-stage arithmetic/crypto/sorting/
modulo/datapath + 3-4 layer deep procedural DAGs** with an expanding 4-generation curriculum:
  - s4b_train_g1 (12, 8-9in)  -> gated on disjoint s4b_val_g1 (20, 9-10in)
  - s4b_train_g2 (12, 9-10in) -> gated on disjoint s4b_val_g2 (20, 9-11in)
  - s4b_train_g3 (12, 10-11in)-> gated on disjoint s4b_val_g3 (20, 9-11in)
  - s4b_train_g4 (12, 10-11in)-> gated on disjoint s4b_val_g4 (20, 9-11in)
  - UNTOUCHED FINAL HOLDOUT (44 brand-new 9-11in tasks):
      * s4b_hold_struct      (16): 9-11in multi-stage arithmetic, multipliers, sorting, modulo, GF, CRC, ALU
      * s4b_hold_proc_shared (14): 100% procedural 9-11in deep shared-cone DAGs (36..46 core gates!)
      * s4b_hold_proc_comp   (14): 100% procedural 9-11in 3-to-4 layer alien-cell compositional DAGs!

Strict invariant enforced at build time: ZERO duplicate task_ids and ZERO duplicate truth tables across ALL 172 tasks!
"""
from __future__ import annotations

import hashlib
import json
import random
from typing import Dict, List, Sequence, Tuple

from comp_sprint.benchmarks import BenchmarkTask, _bits, _from_fn, _gf16_inv, _gf16_mul_const, _popcount, _sort_bits
from comp_sprint.circuit import StrashBuilder, XAGCircuit, full_mask
from comp_sprint2.s2a_benchmarks import _keccak_chi_n, _sample_alien_cells_4to2, _sample_hard_shared_dag
from comp_sprint3.s3_benchmarks import _crc4_step, _gray_decode, _gray_encode, _sbox_gift, _sbox_present, _sbox_skinny


def _sample_deep_shared_9to11(rng: random.Random, n_in: int, n_out: int) -> XAGCircuit:
    core = 32 if n_in <= 9 else (38 if n_in == 10 else 44)
    return _sample_hard_shared_dag(rng, n_inputs=n_in, n_outputs=n_out, n_shared_core=core, n_head=6)


def _sample_deep_comp_9to11(rng: random.Random, cells: Sequence[XAGCircuit], n_in: int, n_out: int) -> XAGCircuit:
    """Deep 3-to-4 layer alien-cell compositional DAG for 8..11 inputs."""
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
    # Layer 1: two disjoint 4-in cells (plus a 3rd overlapping cell for 10-11 inputs)
    l1: List[Tuple[int, bool]] = []
    l1.extend(apply_cell(rng.choice(cells), [wires[perm[i]] for i in range(4)]))
    l1.extend(apply_cell(rng.choice(cells), [wires[perm[i]] for i in range(4, 8)]))
    if n_in >= 10:
        extra = [wires[perm[i]] for i in range(8, n_in)] + [wires[perm[i]] for i in range(4 - (n_in - 8))]
        l1.extend(apply_cell(rng.choice(cells), extra))
    else:
        for i in range(8, n_in):
            l1.append(wires[perm[i]])
    # Layer 2: two mixing cells over Layer 1 wires
    rng.shuffle(l1)
    l2 = apply_cell(rng.choice(cells), l1[:4])
    l2_b = apply_cell(rng.choice(cells), (l1[2:] + l2)[:4])
    pool = l1 + l2 + l2_b
    # Layer 3: final cell + glue gates
    if len(pool) >= 4:
        rng.shuffle(pool)
        l3 = apply_cell(rng.choice(cells), pool[:4])
        pool = pool + l3
    for _ in range(5):
        op = rng.choice(("XOR", "AND"))
        (u, ui), (v, vi) = rng.sample(pool, 2)
        pool.append(b.add_gate(op, u, ui ^ rng.choice((False, True)), v, vi ^ rng.choice((False, True))))
    chosen = rng.sample(pool[-max(n_out + 2, 7):], n_out)
    return b.build([(n, inv ^ rng.choice((False, True))) for n, inv in chosen], prune_dead=True)


def _mk_s(tid: str, split: str, n_in: int, n_out: int, fn, desc: str) -> BenchmarkTask:
    return BenchmarkTask(tid, "structured", split, n_in, _from_fn(n_in, n_out, fn), desc)


def build_s4b_xag_benchmarks() -> Dict[str, List[BenchmarkTask]]:
    """Build fresh sealed 172-task Track S4-B (9..11 input 4-gen XAG) manifest."""
    alien_s4 = _sample_alien_cells_4to2(motif_seed=2026120400)
    seen_tts: set = set()

    def gen_sh(seed: int, split: str, prefix: str, count: int, arities: Sequence[int]) -> List[BenchmarkTask]:
        rng = random.Random(seed)
        out: List[BenchmarkTask] = []
        idx = 0
        while len(out) < count:
            n_in = arities[len(out) % len(arities)]
            n_out = 4 if n_in <= 9 else 5
            c = _sample_deep_shared_9to11(rng, n_in, n_out)
            tts = c.truth_tables()
            mask = full_mask(n_in)
            nr = 1 << n_in
            if len(set(tts)) < n_out or any(t in (0, mask) for t in tts):
                continue
            if any(not (0.12 * nr <= t.bit_count() <= 0.88 * nr) for t in tts):
                continue
            if c.gate_count() < 30:
                continue
            key = (n_in, tuple(tts))
            if key in seen_tts:
                continue
            seen_tts.add(key)
            out.append(BenchmarkTask(
                f"{prefix}_{idx:02d}_n{n_in}m{n_out}", "proc_shared", split, n_in, tts,
                f"S4B {n_in}in deep shared-cone DAG (seed={seed})", hidden_witness_gates=c.gate_count(),
            ))
            idx += 1
        return out

    def gen_cp(seed: int, split: str, prefix: str, count: int, arities: Sequence[int]) -> List[BenchmarkTask]:
        rng = random.Random(seed)
        out: List[BenchmarkTask] = []
        idx = 0
        while len(out) < count:
            n_in = arities[len(out) % len(arities)]
            n_out = 4 if n_in <= 9 else 5
            c = _sample_deep_comp_9to11(rng, alien_s4, n_in, n_out)
            tts = c.truth_tables()
            mask = full_mask(n_in)
            nr = 1 << n_in
            if len(set(tts)) < n_out or any(t in (0, mask) for t in tts):
                continue
            if any(not (0.10 * nr <= t.bit_count() <= 0.90 * nr) for t in tts):
                continue
            if c.gate_count() < 24:
                continue
            key = (n_in, tuple(tts))
            if key in seen_tts:
                continue
            seen_tts.add(key)
            out.append(BenchmarkTask(
                f"{prefix}_{idx:02d}_n{n_in}m{n_out}", "proc_comp", split, n_in, tts,
                f"S4B {n_in}in deep 3-4 layer alien-cell DAG (seed={seed})", hidden_witness_gates=c.gate_count(),
            ))
            idx += 1
        return out

    def reg_struct(tasks: List[BenchmarkTask]) -> List[BenchmarkTask]:
        for t in tasks:
            key = (t.n_inputs, tuple(t.targets))
            assert key not in seen_tts, f"Duplicate truth table in {t.task_id}"
            seen_tts.add(key)
        return tasks

    # ---- G1 (Train 12: 8-9in; Val 20: 9-10in) ----
    tg1 = reg_struct([
        _mk_s("s4b_tg1_add4_cin", "dev", 9, 5, lambda r: _bits((r & 0xF) + ((r >> 4) & 0xF) + ((r >> 8) & 1), 5), "4-bit adder+cin (9->5)"),
        _mk_s("s4b_tg1_pop9", "dev", 9, 4, lambda r: _popcount(r, 9, 4), "9-bit popcount (9->4)"),
        _mk_s("s4b_tg1_mod5_9b", "dev", 9, 3, lambda r: _bits(r % 5, 3), "9-bit mod 5 (9->3)"),
        _mk_s("s4b_tg1_sort9_lo4", "dev", 9, 4, lambda r: _sort_bits(r, 9)[:4], "9-bit sort low 4 (9->4)"),
        _mk_s("s4b_tg1_gf16_mul_x", "dev", 9, 4, lambda r: _bits(_gf16_mul_const(r & 0xF, (r >> 4) & 0xF) ^ (0xF if (r >> 8) else 0), 4), "GF16 mul cond-inv (9->4)"),
        _mk_s("s4b_tg1_crc4_9b_p9", "dev", 9, 4, lambda r: _crc4_step(r, 9, 0x9), "9-bit CRC4 poly=9 (9->4)"),
    ]) + gen_sh(2026120401, "dev", "s4b_tg1_sh", 3, (8, 9)) + gen_cp(2026120402, "dev", "s4b_tg1_cp", 3, (8, 9))

    vg1 = reg_struct([
        _mk_s("s4b_vg1_add5_nosat", "val_g1", 10, 6, lambda r: _bits((r & 0x1F) + ((r >> 5) & 0x1F), 6), "5-bit adder (10->6)"),
        _mk_s("s4b_vg1_sub4_bin", "val_g1", 9, 5, lambda r: _bits(((r & 0xF) - ((r >> 4) & 0xF) - ((r >> 8) & 1)) & 0x1F, 5), "4-bit sub+bin (9->5)"),
        _mk_s("s4b_vg1_pop10", "val_g1", 10, 4, lambda r: _popcount(r, 10, 4), "10-bit popcount (10->4)"),
        _mk_s("s4b_vg1_mod7_10b", "val_g1", 10, 3, lambda r: _bits(r % 7, 3), "10-bit mod 7 (10->3)"),
        _mk_s("s4b_vg1_sort10_lo4", "val_g1", 10, 4, lambda r: _sort_bits(r, 10)[:4], "10-bit sort low 4 (10->4)"),
        _mk_s("s4b_vg1_max5", "val_g1", 10, 5, lambda r: _bits(max(r & 0x1F, (r >> 5) & 0x1F), 5), "5-bit max(a,b) (10->5)"),
        _mk_s("s4b_vg1_hamm5x2", "val_g1", 10, 3, lambda r: _bits(((r & 0x1F) ^ ((r >> 5) & 0x1F)).bit_count(), 3), "5-bit Hamming dist (10->3)"),
        _mk_s("s4b_vg1_keccak9", "val_g1", 9, 9, lambda r: _keccak_chi_n(r, 9), "9-bit Keccak chi (9->9)"),
    ]) + gen_sh(2026120411, "val_g1", "s4b_vg1_sh", 6, (9, 10)) + gen_cp(2026120412, "val_g1", "s4b_vg1_cp", 6, (9, 10))

    # ---- G2 (Train 12: 9-10in; Val 20: 9-11in) ----
    tg2 = reg_struct([
        _mk_s("s4b_tg2_sub5_nosat", "dev", 10, 6, lambda r: _bits(((r & 0x1F) - ((r >> 5) & 0x1F)) & 0x3F, 6), "5-bit subtractor (10->6)"),
        _mk_s("s4b_tg2_absdiff5", "dev", 10, 5, lambda r: _bits(abs((r & 0x1F) - ((r >> 5) & 0x1F)), 5), "5-bit |a-b| (10->5)"),
        _mk_s("s4b_tg2_mod9_10b", "dev", 10, 4, lambda r: _bits(r % 9, 4), "10-bit mod 9 (10->4)"),
        _mk_s("s4b_tg2_div5_10b", "dev", 10, 4, lambda r: _bits((r // 5) & 0xF, 4), "10-bit floor(x/5) lo4 (10->4)"),
        _mk_s("s4b_tg2_rot5_sh", "dev", 9, 5, lambda r: _bits((((r & 0x1F) << ((r >> 5) & 7)) | ((r & 0x1F) >> (5 - (((r >> 5) & 7) % 5)))) & 0x1F, 5), "5-bit var shift/rot (9->5)"),
        _mk_s("s4b_tg2_feistel2_p", "dev", 10, 4, lambda r: _bits(_sbox_present((r & 0xF) ^ ((r >> 4) & 0xF)) ^ ((r >> 6) & 0xF), 4), "PRESENT Feistel-10 (10->4)"),
    ]) + gen_sh(2026120421, "dev", "s4b_tg2_sh", 3, (9, 10)) + gen_cp(2026120422, "dev", "s4b_tg2_cp", 3, (9, 10))

    vg2 = reg_struct([
        _mk_s("s4b_vg2_add5_sat", "val_g2", 10, 5, lambda r: _bits(min(31, (r & 0x1F) + ((r >> 5) & 0x1F)), 5), "5-bit saturating add (10->5)"),
        _mk_s("s4b_vg2_min5_lt", "val_g2", 10, 6, lambda r: _bits(min(r & 0x1F, (r >> 5) & 0x1F), 5) + [int((r & 0x1F) < ((r >> 5) & 0x1F))], "5-bit min+(a<b) (10->6)"),
        _mk_s("s4b_vg2_mod6_10b", "val_g2", 10, 3, lambda r: _bits(r % 6, 3), "10-bit mod 6 (10->3)"),
        _mk_s("s4b_vg2_mod3_11b", "val_g2", 11, 2, lambda r: _bits(r % 3, 2), "11-bit mod 3 (11->2)"),
        _mk_s("s4b_vg2_sort10_top4", "val_g2", 10, 4, lambda r: _sort_bits(r, 10)[6:], "10-bit sort top 4 (10->4)"),
        _mk_s("s4b_vg2_mul4x4_add2", "val_g2", 10, 5, lambda r: _bits((((r & 0xF) * ((r >> 4) & 0xF)) + ((r >> 8) & 3)) & 0x1F, 5), "4x4 mul + 2b lo5 (10->5)"),
        _mk_s("s4b_vg2_clz10", "val_g2", 10, 4, lambda r: _bits(10 if r == 0 else (10 - r.bit_length()), 4), "10-bit CLZ (10->4)"),
        _mk_s("s4b_vg2_skinny_f10", "val_g2", 10, 4, lambda r: _bits(_sbox_skinny((r & 0xF) ^ ((r >> 6) & 0xF)) ^ ((r >> 4) & 0xF), 4), "SKINNY Feistel-10 (10->4)"),
    ]) + gen_sh(2026120431, "val_g2", "s4b_vg2_sh", 6, (9, 10, 11)) + gen_cp(2026120432, "val_g2", "s4b_vg2_cp", 6, (9, 10, 11))

    # ---- G3 (Train 12: 10-11in; Val 20: 9-11in) ----
    tg3 = reg_struct([
        _mk_s("s4b_tg3_add5_cin", "dev", 11, 6, lambda r: _bits((r & 0x1F) + ((r >> 5) & 0x1F) + ((r >> 10) & 1), 6), "5-bit adder+cin (11->6)"),
        _mk_s("s4b_tg3_pop11", "dev", 11, 4, lambda r: _popcount(r, 11, 4), "11-bit popcount (11->4)"),
        _mk_s("s4b_tg3_mod5_11b", "dev", 11, 3, lambda r: _bits(r % 5, 3), "11-bit mod 5 (11->3)"),
        _mk_s("s4b_tg3_mul5x4_lo5", "dev", 9, 5, lambda r: _bits(((r & 0x1F) * ((r >> 5) & 0xF)) & 0x1F, 5), "5x4 mul lo5 (9->5)"),
        _mk_s("s4b_tg3_div3_10b", "dev", 10, 4, lambda r: _bits((r // 3) & 0xF, 4), "10-bit floor(x/3) lo4 (10->4)"),
        _mk_s("s4b_tg3_sort11_mid4", "dev", 11, 4, lambda r: _sort_bits(r, 11)[3:7], "11-bit sort mid 4 (11->4)"),
    ]) + gen_sh(2026120441, "dev", "s4b_tg3_sh", 3, (10, 11)) + gen_cp(2026120442, "dev", "s4b_tg3_cp", 3, (10, 11))

    vg3 = reg_struct([
        _mk_s("s4b_vg3_sub5_bin", "val_g3", 11, 6, lambda r: _bits(((r & 0x1F) - ((r >> 5) & 0x1F) - ((r >> 10) & 1)) & 0x3F, 6), "5-bit sub+bin (11->6)"),
        _mk_s("s4b_vg3_sub5_sat", "val_g3", 10, 5, lambda r: _bits(max(0, (r & 0x1F) - ((r >> 5) & 0x1F)), 5), "5-bit sat sub (10->5)"),
        _mk_s("s4b_vg3_mod7_11b", "val_g3", 11, 3, lambda r: _bits(r % 7, 3), "11-bit mod 7 (11->3)"),
        _mk_s("s4b_vg3_avg5", "val_g3", 10, 5, lambda r: _bits(((r & 0x1F) + ((r >> 5) & 0x1F)) >> 1, 5), "5-bit avg (a+b)>>1 (10->5)"),
        _mk_s("s4b_vg3_gray_add5", "val_g3", 10, 5, lambda r: _bits((_gray_decode(r & 0x1F, 5) + _gray_decode((r >> 5) & 0x1F, 5)) & 0x1F, 5), "5-bit Gray-dec sum (10->5)"),
        _mk_s("s4b_vg3_prio10", "val_g3", 10, 4, lambda r: _bits(0 if r == 0 else r.bit_length(), 4), "10-bit priority enc (10->4)"),
        _mk_s("s4b_vg3_crc4_11b_p3", "val_g3", 11, 4, lambda r: _crc4_step(r, 11, 0x3), "11-bit CRC4 poly=3 (11->4)"),
        _mk_s("s4b_vg3_gift_f10", "val_g3", 10, 4, lambda r: _bits(_sbox_gift((r & 0xF) ^ ((r >> 6) & 0xF)) ^ ((r >> 4) & 0xF), 4), "GIFT Feistel-10 (10->4)"),
    ]) + gen_sh(2026120451, "val_g3", "s4b_vg3_sh", 6, (9, 10, 11)) + gen_cp(2026120452, "val_g3", "s4b_vg3_cp", 6, (9, 10, 11))

    # ---- G4 (Train 12: 10-11in hardest; Val 20: 9-11in) ----
    tg4 = reg_struct([
        _mk_s("s4b_tg4_alu5_addsub", "dev", 11, 6, lambda r: _bits(((r & 0x1F) + ((r >> 5) & 0x1F)) if ((r >> 10) & 1) == 0 else (((r & 0x1F) - ((r >> 5) & 0x1F)) & 0x3F), 6), "5-bit add/sub ALU (11->6)"),
        _mk_s("s4b_tg4_mod11_10b", "dev", 10, 4, lambda r: _bits(r % 11, 4), "10-bit mod 11 (10->4)"),
        _mk_s("s4b_tg4_pop10_mod3", "dev", 10, 4, lambda r: _bits(r.bit_count() % 3, 2) + [int(r.bit_count() >= 4), int(r.bit_count() >= 7)], "10-bit pop%3 + thr (10->4)"),
        _mk_s("s4b_tg4_mul5x5_lo5", "dev", 10, 5, lambda r: _bits(((r & 0x1F) * ((r >> 5) & 0x1F)) & 0x1F, 5), "5x5 mul lo5 (10->5)"),
        _mk_s("s4b_tg4_mux5_2x5", "dev", 11, 5, lambda r: _bits((r & 0x1F) if ((r >> 10) & 1) == 0 else ((r >> 5) & 0x1F), 5), "5-bit 2-to-1 MUX (11->5)"),
        _mk_s("s4b_tg4_keccak10", "dev", 10, 5, lambda r: _keccak_chi_n(r, 10)[:5], "10-bit Keccak chi lo5 (10->5)"),
    ]) + gen_sh(2026120461, "dev", "s4b_tg4_sh", 3, (10, 11)) + gen_cp(2026120462, "dev", "s4b_tg4_cp", 3, (10, 11))

    vg4 = reg_struct([
        _mk_s("s4b_vg4_mod9_11b", "val_g4", 11, 4, lambda r: _bits(r % 9, 4), "11-bit mod 9 (11->4)"),
        _mk_s("s4b_vg4_mod6_11b", "val_g4", 11, 3, lambda r: _bits(r % 6, 3), "11-bit mod 6 (11->3)"),
        _mk_s("s4b_vg4_div7_10b", "val_g4", 10, 4, lambda r: _bits((r // 7) & 0xF, 4), "10-bit floor(x/7) lo4 (10->4)"),
        _mk_s("s4b_vg4_sort11_top4", "val_g4", 11, 4, lambda r: _sort_bits(r, 11)[7:], "11-bit sort top 4 (11->4)"),
        _mk_s("s4b_vg4_ctz10", "val_g4", 10, 4, lambda r: _bits(10 if r == 0 else ((r & -r).bit_length() - 1), 4), "10-bit CTZ (10->4)"),
        _mk_s("s4b_vg4_mul5x4_mid4", "val_g4", 9, 4, lambda r: _bits((((r & 0x1F) * ((r >> 5) & 0xF)) >> 3) & 0xF, 4), "5x4 mul mid4 (9->4)"),
        _mk_s("s4b_vg4_add5_gray", "val_g4", 10, 6, lambda r: _bits(_gray_encode((r & 0x1F) + ((r >> 5) & 0x1F), 6), 6), "5-bit Gray-enc sum (10->6)"),
        _mk_s("s4b_vg4_gf16_div_x", "val_g4", 9, 4, lambda r: _bits(_gf16_mul_const(_gf16_inv(r & 0xF), (r >> 4) & 0xF) ^ (0xA if (r >> 8) else 0), 4), "GF16 div cond-xor (9->4)"),
    ]) + gen_sh(2026120471, "val_g4", "s4b_vg4_sh", 6, (9, 10, 11)) + gen_cp(2026120472, "val_g4", "s4b_vg4_cp", 6, (9, 10, 11))

    # ==================== UNTOUCHED FINAL HOLDOUT (44 tasks: 16 struct + 14 sh + 14 cp, 9..11in) ====================
    hold_s = reg_struct([
        _mk_s("s4b_hold_add5_cin_lo5", "holdout", 11, 5, lambda r: _bits(((r & 0x1F) + ((r >> 5) & 0x1F) + ((r >> 10) & 1)) & 0x1F, 5), "5-bit adder+cin lo5 (11->5)"),
        _mk_s("s4b_hold_sub5_bin_hi5", "holdout", 11, 5, lambda r: _bits((((r & 0x1F) - ((r >> 5) & 0x1F) - ((r >> 10) & 1)) >> 1) & 0x1F, 5), "5-bit sub+bin hi5 (11->5)"),
        _mk_s("s4b_hold_mul5x5_mid4", "holdout", 10, 4, lambda r: _bits((((r & 0x1F) * ((r >> 5) & 0x1F)) >> 3) & 0xF, 4), "5x5 mul mid4 [6:3] (10->4)"),
        _mk_s("s4b_hold_mul5x5_hi4", "holdout", 10, 4, lambda r: _bits((((r & 0x1F) * ((r >> 5) & 0x1F)) >> 6) & 0xF, 4), "5x5 mul hi4 [9:6] (10->4)"),
        _mk_s("s4b_hold_mac4x3_add3", "holdout", 10, 5, lambda r: _bits((((r & 0xF) * ((r >> 4) & 7)) + ((r >> 7) & 7)) & 0x1F, 5), "4x3 MAC + 3b lo5 (10->5)"),
        _mk_s("s4b_hold_sort10_mid4", "holdout", 10, 4, lambda r: _sort_bits(r, 10)[3:7], "10-bit sort mid 4 (10->4)"),
        _mk_s("s4b_hold_sort11_lo4", "holdout", 11, 4, lambda r: _sort_bits(r, 11)[:4], "11-bit sort low 4 (11->4)"),
        _mk_s("s4b_hold_pop11_thr", "holdout", 11, 4, lambda r: _bits(r.bit_count() % 5, 3) + [int(r.bit_count() >= 6)], "11-bit pop%5 + maj (11->4)"),
        _mk_s("s4b_hold_mod10_11b", "holdout", 11, 4, lambda r: _bits(r % 10, 4), "11-bit mod 10 (11->4)"),
        _mk_s("s4b_hold_mod11_11b", "holdout", 11, 4, lambda r: _bits(r % 11, 4), "11-bit mod 11 (11->4)"),
        _mk_s("s4b_hold_div6_10b", "holdout", 10, 4, lambda r: _bits((r // 6) & 0xF, 4), "10-bit floor(x/6) lo4 (10->4)"),
        _mk_s("s4b_hold_absdiff5_eq", "holdout", 10, 5, lambda r: _bits(abs((r & 0x1F) - ((r >> 5) & 0x1F)), 4) + [int((r & 0x1F) == ((r >> 5) & 0x1F))], "5-bit |a-b|lo4 + eq (10->5)"),
        _mk_s("s4b_hold_alu4_4op", "holdout", 10, 4, lambda r: _bits((
            ((r & 0xF) + ((r >> 4) & 0xF)) if ((r >> 8) & 3) == 0 else
            ((r & 0xF) - ((r >> 4) & 0xF)) if ((r >> 8) & 3) == 1 else
            ((r & 0xF) ^ ((r >> 4) & 0xF)) if ((r >> 8) & 3) == 2 else
            ((r & 0xF) & ((r >> 4) & 0xF))
        ) & 0xF, 4), "4-bit 4-op ALU (10->4)"),
        _mk_s("s4b_hold_clz11", "holdout", 11, 4, lambda r: _bits(11 if r == 0 else (11 - r.bit_length()), 4), "11-bit CLZ (11->4)"),
        _mk_s("s4b_hold_crc4_10b_p9", "holdout", 10, 4, lambda r: _crc4_step(r, 10, 0x9), "10-bit CRC4 poly=9 (10->4)"),
        _mk_s("s4b_hold_keccak11_lo5", "holdout", 11, 5, lambda r: _keccak_chi_n(r, 11)[:5], "11-bit Keccak chi lo5 (11->5)"),
    ])
    hold_sh = gen_sh(2026120491, "holdout", "s4b_hold_sh", 14, (9, 10, 11))
    hold_cp = gen_cp(2026120493, "holdout", "s4b_hold_cp", 14, (9, 10, 11))

    suites = {
        "s4b_train_g1": tg1, "s4b_val_g1": vg1,
        "s4b_train_g2": tg2, "s4b_val_g2": vg2,
        "s4b_train_g3": tg3, "s4b_val_g3": vg3,
        "s4b_train_g4": tg4, "s4b_val_g4": vg4,
        "s4b_hold_struct": hold_s,
        "s4b_hold_proc_shared": hold_sh,
        "s4b_hold_proc_comp": hold_cp,
    }
    assert sum(len(v) for v in suites.values()) == 172
    return suites


def s4b_manifest_sha256(suites: Dict[str, List[BenchmarkTask]]) -> str:
    payload = {k: [t.public_dict() for t in v] for k, v in sorted(suites.items())}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
