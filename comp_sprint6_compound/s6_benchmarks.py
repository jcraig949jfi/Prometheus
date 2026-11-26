"""Sprint 6 Fresh Sealed Benchmarks: 172-Task 8-to-10 Input Multi-Stage XAG Suite (4 Expanding Lineages).

Reuses the proven 8..10 input sweet spot (256..1024-bit truth tables, fast under Law 4b word+container
metering, rich multi-level algebraic/decomp/netlist headroom) with 100% fresh disjoint RNG seeds:
  - s6_train_g1 (12, 8-9in)  -> gated on hidden s6_val_g1 (20, 8-10in)
  - s6_train_g2 (12, 8-10in) -> gated on hidden s6_val_g2 (20, 8-10in)
  - s6_train_g3 (12, 9-10in) -> gated on hidden s6_val_g3 (20, 8-10in)
  - s6_train_g4 (12, 9-10in) -> gated on hidden s6_val_g4 (20, 8-10in)
  - UNTOUCHED FINAL HOLDOUT (44 brand-new 8-10in tasks: 16 struct + 14 proc_shared + 14 proc_comp)
"""
from __future__ import annotations

import hashlib
import json
import random
from typing import Dict, List, Sequence

from comp_sprint.benchmarks import BenchmarkTask, _bits, _from_fn, _gf16_inv, _gf16_mul_const, _popcount, _sort_bits
from comp_sprint.circuit import full_mask
from comp_sprint2.s2a_benchmarks import _keccak_chi_n, _sample_alien_cells_4to2
from comp_sprint3.s3_benchmarks import _crc4_step, _gray_decode, _gray_encode, _sbox_gift, _sbox_present, _sbox_skinny
from comp_sprint4.s4b_xag_benchmarks import _sample_deep_comp_9to11, _sample_deep_shared_9to11


def _mk(tid: str, split: str, n_in: int, n_out: int, fn, desc: str) -> BenchmarkTask:
    return BenchmarkTask(tid, "structured", split, n_in, _from_fn(n_in, n_out, fn), desc)


def build_s6_benchmarks() -> Dict[str, List[BenchmarkTask]]:
    alien_s6 = _sample_alien_cells_4to2(motif_seed=2026120600)
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
            if c.gate_count() < 28:
                continue
            key = (n_in, tuple(tts))
            if key in seen_tts:
                continue
            seen_tts.add(key)
            out.append(BenchmarkTask(f"{prefix}_{idx:02d}_n{n_in}m{n_out}", "proc_shared", split, n_in, tts, f"S6 {n_in}in shared DAG", hidden_witness_gates=c.gate_count()))
            idx += 1
        return out

    def gen_cp(seed: int, split: str, prefix: str, count: int, arities: Sequence[int]) -> List[BenchmarkTask]:
        rng = random.Random(seed)
        out: List[BenchmarkTask] = []
        idx = 0
        while len(out) < count:
            n_in = arities[len(out) % len(arities)]
            n_out = 4 if n_in <= 9 else 5
            c = _sample_deep_comp_9to11(rng, alien_s6, n_in, n_out)
            tts = c.truth_tables()
            mask = full_mask(n_in)
            nr = 1 << n_in
            if len(set(tts)) < n_out or any(t in (0, mask) for t in tts):
                continue
            if any(not (0.10 * nr <= t.bit_count() <= 0.90 * nr) for t in tts):
                continue
            if c.gate_count() < 22:
                continue
            key = (n_in, tuple(tts))
            if key in seen_tts:
                continue
            seen_tts.add(key)
            out.append(BenchmarkTask(f"{prefix}_{idx:02d}_n{n_in}m{n_out}", "proc_comp", split, n_in, tts, f"S6 {n_in}in alien-cell DAG", hidden_witness_gates=c.gate_count()))
            idx += 1
        return out

    def reg(tasks: List[BenchmarkTask]) -> List[BenchmarkTask]:
        for t in tasks:
            key = (t.n_inputs, tuple(t.targets))
            assert key not in seen_tts, f"Duplicate truth table in {t.task_id}"
            seen_tts.add(key)
        return tasks

    tg1 = reg([
        _mk("s6_tg1_add4_cin", "dev", 9, 5, lambda r: _bits((r & 0xF) + ((r >> 4) & 0xF) + ((r >> 8) & 1), 5), "4-bit adder+cin"),
        _mk("s6_tg1_pop8", "dev", 8, 4, lambda r: _popcount(r, 8, 4), "8-bit popcount"),
        _mk("s6_tg1_mod5_9b", "dev", 9, 3, lambda r: _bits(r % 5, 3), "9-bit mod 5"),
        _mk("s6_tg1_sort8_lo4", "dev", 8, 4, lambda r: _sort_bits(r, 8)[:4], "8-bit sort lo4"),
        _mk("s6_tg1_gf16_mul", "dev", 8, 4, lambda r: _bits(_gf16_mul_const(r & 0xF, (r >> 4) & 0xF), 4), "GF16 mul"),
        _mk("s6_tg1_crc4_8b_p3", "dev", 8, 4, lambda r: _crc4_step(r, 8, 0x3), "8-bit CRC4 p3"),
    ]) + gen_sh(2026120601, "dev", "s6_tg1_sh", 3, (8, 9)) + gen_cp(2026120602, "dev", "s6_tg1_cp", 3, (8, 9))

    vg1 = reg([
        _mk("s6_vg1_add5_lo5", "val_g1", 10, 5, lambda r: _bits(((r & 0x1F) + ((r >> 5) & 0x1F)) & 0x1F, 5), "5-bit add lo5"),
        _mk("s6_vg1_sub4_bin", "val_g1", 9, 5, lambda r: _bits(((r & 0xF) - ((r >> 4) & 0xF) - ((r >> 8) & 1)) & 0x1F, 5), "4-bit sub+bin"),
        _mk("s6_vg1_pop9", "val_g1", 9, 4, lambda r: _popcount(r, 9, 4), "9-bit popcount"),
        _mk("s6_vg1_mod7_9b", "val_g1", 9, 3, lambda r: _bits(r % 7, 3), "9-bit mod 7"),
        _mk("s6_vg1_sort9_lo4", "val_g1", 9, 4, lambda r: _sort_bits(r, 9)[:4], "9-bit sort lo4"),
        _mk("s6_vg1_max5", "val_g1", 10, 5, lambda r: _bits(max(r & 0x1F, (r >> 5) & 0x1F), 5), "5-bit max"),
        _mk("s6_vg1_hamm5x2", "val_g1", 10, 3, lambda r: _bits(((r & 0x1F) ^ ((r >> 5) & 0x1F)).bit_count(), 3), "5-bit Hamming dist"),
        _mk("s6_vg1_keccak8", "val_g1", 8, 8, lambda r: _keccak_chi_n(r, 8), "8-bit Keccak chi"),
    ]) + gen_sh(2026120611, "val_g1", "s6_vg1_sh", 6, (8, 9, 10)) + gen_cp(2026120612, "val_g1", "s6_vg1_cp", 6, (8, 9, 10))

    tg2 = reg([
        _mk("s6_tg2_sub5_nosat", "dev", 10, 6, lambda r: _bits(((r & 0x1F) - ((r >> 5) & 0x1F)) & 0x3F, 6), "5-bit sub"),
        _mk("s6_tg2_absdiff5", "dev", 10, 5, lambda r: _bits(abs((r & 0x1F) - ((r >> 5) & 0x1F)), 5), "5-bit |a-b|"),
        _mk("s6_tg2_mod9_9b", "dev", 9, 4, lambda r: _bits(r % 9, 4), "9-bit mod 9"),
        _mk("s6_tg2_div5_9b", "dev", 9, 4, lambda r: _bits((r // 5) & 0xF, 4), "9-bit floor(x/5)"),
        _mk("s6_tg2_present_f9", "dev", 9, 4, lambda r: _bits(_sbox_present((r & 0xF) ^ ((r >> 4) & 0xF)) ^ (0xF if (r >> 8) else 0), 4), "PRESENT Feistel-9"),
        _mk("s6_tg2_sort10_lo4", "dev", 10, 4, lambda r: _sort_bits(r, 10)[:4], "10-bit sort lo4"),
    ]) + gen_sh(2026120621, "dev", "s6_tg2_sh", 3, (8, 9, 10)) + gen_cp(2026120622, "dev", "s6_tg2_cp", 3, (8, 9, 10))

    vg2 = reg([
        _mk("s6_vg2_add5_sat", "val_g2", 10, 5, lambda r: _bits(min(31, (r & 0x1F) + ((r >> 5) & 0x1F)), 5), "5-bit sat add"),
        _mk("s6_vg2_min5_lt", "val_g2", 10, 6, lambda r: _bits(min(r & 0x1F, (r >> 5) & 0x1F), 5) + [int((r & 0x1F) < ((r >> 5) & 0x1F))], "5-bit min+(a<b)"),
        _mk("s6_vg2_mod6_10b", "val_g2", 10, 3, lambda r: _bits(r % 6, 3), "10-bit mod 6"),
        _mk("s6_vg2_mod3_10b", "val_g2", 10, 2, lambda r: _bits(r % 3, 2), "10-bit mod 3"),
        _mk("s6_vg2_sort10_top4", "val_g2", 10, 4, lambda r: _sort_bits(r, 10)[6:], "10-bit sort top4"),
        _mk("s6_vg2_mul4x4_lo5", "val_g2", 8, 5, lambda r: _bits(((r & 0xF) * ((r >> 4) & 0xF)) & 0x1F, 5), "4x4 mul lo5"),
        _mk("s6_vg2_clz9", "val_g2", 9, 4, lambda r: _bits(9 if r == 0 else (9 - r.bit_length()), 4), "9-bit CLZ"),
        _mk("s6_vg2_skinny_f10", "val_g2", 10, 4, lambda r: _bits(_sbox_skinny((r & 0xF) ^ ((r >> 6) & 0xF)) ^ ((r >> 4) & 0xF), 4), "SKINNY Feistel-10"),
    ]) + gen_sh(2026120631, "val_g2", "s6_vg2_sh", 6, (8, 9, 10)) + gen_cp(2026120632, "val_g2", "s6_vg2_cp", 6, (8, 9, 10))

    tg3 = reg([
        _mk("s6_tg3_pop10", "dev", 10, 4, lambda r: _popcount(r, 10, 4), "10-bit popcount"),
        _mk("s6_tg3_mod7_10b", "dev", 10, 3, lambda r: _bits(r % 7, 3), "10-bit mod 7"),
        _mk("s6_tg3_mul5x4_lo5", "dev", 9, 5, lambda r: _bits(((r & 0x1F) * ((r >> 5) & 0xF)) & 0x1F, 5), "5x4 mul lo5"),
        _mk("s6_tg3_div3_10b", "dev", 10, 4, lambda r: _bits((r // 3) & 0xF, 4), "10-bit floor(x/3)"),
        _mk("s6_tg3_avg5", "dev", 10, 5, lambda r: _bits(((r & 0x1F) + ((r >> 5) & 0x1F)) >> 1, 5), "5-bit avg"),
        _mk("s6_tg3_crc4_10b_p3", "dev", 10, 4, lambda r: _crc4_step(r, 10, 0x3), "10-bit CRC4 p3"),
    ]) + gen_sh(2026120641, "dev", "s6_tg3_sh", 3, (9, 10)) + gen_cp(2026120642, "dev", "s6_tg3_cp", 3, (9, 10))

    vg3 = reg([
        _mk("s6_vg3_sub5_sat", "val_g3", 10, 5, lambda r: _bits(max(0, (r & 0x1F) - ((r >> 5) & 0x1F)), 5), "5-bit sat sub"),
        _mk("s6_vg3_mod9_10b", "val_g3", 10, 4, lambda r: _bits(r % 9, 4), "10-bit mod 9"),
        _mk("s6_vg3_gray_add5", "val_g3", 10, 5, lambda r: _bits((_gray_decode(r & 0x1F, 5) + _gray_decode((r >> 5) & 0x1F, 5)) & 0x1F, 5), "5-bit Gray-dec sum"),
        _mk("s6_vg3_prio10", "val_g3", 10, 4, lambda r: _bits(0 if r == 0 else r.bit_length(), 4), "10-bit priority enc"),
        _mk("s6_vg3_gift_f10", "val_g3", 10, 4, lambda r: _bits(_sbox_gift((r & 0xF) ^ ((r >> 6) & 0xF)) ^ ((r >> 4) & 0xF), 4), "GIFT Feistel-10"),
        _mk("s6_vg3_mul4x4_mid4", "val_g3", 8, 4, lambda r: _bits((((r & 0xF) * ((r >> 4) & 0xF)) >> 2) & 0xF, 4), "4x4 mul mid4"),
        _mk("s6_vg3_sort9_mid4", "val_g3", 9, 4, lambda r: _sort_bits(r, 9)[2:6], "9-bit sort mid4"),
        _mk("s6_vg3_keccak9", "val_g3", 9, 9, lambda r: _keccak_chi_n(r, 9), "9-bit Keccak chi"),
    ]) + gen_sh(2026120651, "val_g3", "s6_vg3_sh", 6, (8, 9, 10)) + gen_cp(2026120652, "val_g3", "s6_vg3_cp", 6, (8, 9, 10))

    tg4 = reg([
        _mk("s6_tg4_alu4_4op", "dev", 10, 4, lambda r: _bits((
            ((r & 0xF) + ((r >> 4) & 0xF)) if ((r >> 8) & 3) == 0 else
            ((r & 0xF) - ((r >> 4) & 0xF)) if ((r >> 8) & 3) == 1 else
            ((r & 0xF) ^ ((r >> 4) & 0xF)) if ((r >> 8) & 3) == 2 else
            ((r & 0xF) & ((r >> 4) & 0xF))
        ) & 0xF, 4), "4-bit 4-op ALU"),
        _mk("s6_tg4_mod11_10b", "dev", 10, 4, lambda r: _bits(r % 11, 4), "10-bit mod 11"),
        _mk("s6_tg4_pop10_mod3", "dev", 10, 4, lambda r: _bits(r.bit_count() % 3, 2) + [int(r.bit_count() >= 4), int(r.bit_count() >= 7)], "10-bit pop%3+thr"),
        _mk("s6_tg4_mul5x5_lo5", "dev", 10, 5, lambda r: _bits(((r & 0x1F) * ((r >> 5) & 0x1F)) & 0x1F, 5), "5x5 mul lo5"),
        _mk("s6_tg4_mux4_2x4", "dev", 9, 4, lambda r: _bits((r & 0xF) if ((r >> 8) & 1) == 0 else ((r >> 4) & 0xF), 4), "4-bit 2:1 MUX"),
        _mk("s6_tg4_keccak10_lo5", "dev", 10, 5, lambda r: _keccak_chi_n(r, 10)[:5], "10-bit Keccak lo5"),
    ]) + gen_sh(2026120661, "dev", "s6_tg4_sh", 3, (9, 10)) + gen_cp(2026120662, "dev", "s6_tg4_cp", 3, (9, 10))

    vg4 = reg([
        _mk("s6_vg4_div7_10b", "val_g4", 10, 4, lambda r: _bits((r // 7) & 0xF, 4), "10-bit floor(x/7)"),
        _mk("s6_vg4_ctz10", "val_g4", 10, 4, lambda r: _bits(10 if r == 0 else ((r & -r).bit_length() - 1), 4), "10-bit CTZ"),
        _mk("s6_vg4_mul5x4_mid4", "val_g4", 9, 4, lambda r: _bits((((r & 0x1F) * ((r >> 5) & 0xF)) >> 3) & 0xF, 4), "5x4 mul mid4"),
        _mk("s6_vg4_add5_gray", "val_g4", 10, 6, lambda r: _bits(_gray_encode((r & 0x1F) + ((r >> 5) & 0x1F), 6), 6), "5-bit Gray-enc sum"),
        _mk("s6_vg4_gf16_div_x", "val_g4", 9, 4, lambda r: _bits(_gf16_mul_const(_gf16_inv(r & 0xF), (r >> 4) & 0xF) ^ (0xA if (r >> 8) else 0), 4), "GF16 div cond-xor"),
        _mk("s6_vg4_mod5_10b", "val_g4", 10, 3, lambda r: _bits(r % 5, 3), "10-bit mod 5"),
        _mk("s6_vg4_sort8_top4", "val_g4", 8, 4, lambda r: _sort_bits(r, 8)[4:], "8-bit sort top4"),
        _mk("s6_vg4_mac3_add3", "val_g4", 9, 4, lambda r: _bits((((r & 7) * ((r >> 3) & 7)) + ((r >> 6) & 7)) & 0xF, 4), "3-bit MAC + 3b"),
    ]) + gen_sh(2026120671, "val_g4", "s6_vg4_sh", 6, (8, 9, 10)) + gen_cp(2026120672, "val_g4", "s6_vg4_cp", 6, (8, 9, 10))

    # ==================== UNTOUCHED FINAL HOLDOUT (44 brand-new 8..10in tasks) ====================
    hold_s = reg([
        _mk("s6_hold_add5_full", "holdout", 10, 6, lambda r: _bits((r & 0x1F) + ((r >> 5) & 0x1F), 6), "5-bit full adder (10->6)"),
        _mk("s6_hold_sub5_lo5", "holdout", 10, 5, lambda r: _bits(((r & 0x1F) - ((r >> 5) & 0x1F)) & 0x1F, 5), "5-bit sub lo5 (10->5)"),
        _mk("s6_hold_mul5x5_mid4", "holdout", 10, 4, lambda r: _bits((((r & 0x1F) * ((r >> 5) & 0x1F)) >> 3) & 0xF, 4), "5x5 mul mid4 (10->4)"),
        _mk("s6_hold_mul5x5_hi4", "holdout", 10, 4, lambda r: _bits((((r & 0x1F) * ((r >> 5) & 0x1F)) >> 6) & 0xF, 4), "5x5 mul hi4 (10->4)"),
        _mk("s6_hold_mac4x3_add3", "holdout", 10, 5, lambda r: _bits((((r & 0xF) * ((r >> 4) & 7)) + ((r >> 7) & 7)) & 0x1F, 5), "4x3 MAC+3b (10->5)"),
        _mk("s6_hold_sort10_mid4", "holdout", 10, 4, lambda r: _sort_bits(r, 10)[3:7], "10-bit sort mid4 (10->4)"),
        _mk("s6_hold_sort9_top4", "holdout", 9, 4, lambda r: _sort_bits(r, 9)[5:], "9-bit sort top4 (9->4)"),
        _mk("s6_hold_pop9_mod5", "holdout", 9, 4, lambda r: _bits(r.bit_count() % 5, 3) + [int(r.bit_count() >= 5)], "9-bit pop%5+maj (9->4)"),
        _mk("s6_hold_mod10_10b", "holdout", 10, 4, lambda r: _bits(r % 10, 4), "10-bit mod 10 (10->4)"),
        _mk("s6_hold_mod13_10b", "holdout", 10, 4, lambda r: _bits(r % 13, 4), "10-bit mod 13 (10->4)"),
        _mk("s6_hold_div6_10b", "holdout", 10, 4, lambda r: _bits((r // 6) & 0xF, 4), "10-bit floor(x/6) (10->4)"),
        _mk("s6_hold_absdiff5_eq", "holdout", 10, 5, lambda r: _bits(abs((r & 0x1F) - ((r >> 5) & 0x1F)), 4) + [int((r & 0x1F) == ((r >> 5) & 0x1F))], "5-bit |a-b|+eq (10->5)"),
        _mk("s6_hold_alu4_addsub", "holdout", 9, 5, lambda r: _bits(((r & 0xF) + ((r >> 4) & 0xF)) if ((r >> 8) & 1) == 0 else (((r & 0xF) - ((r >> 4) & 0xF)) & 0x1F), 5), "4-bit add/sub ALU (9->5)"),
        _mk("s6_hold_clz10", "holdout", 10, 4, lambda r: _bits(10 if r == 0 else (10 - r.bit_length()), 4), "10-bit CLZ (10->4)"),
        _mk("s6_hold_crc4_10b_p9", "holdout", 10, 4, lambda r: _crc4_step(r, 10, 0x9), "10-bit CRC4 p9 (10->4)"),
        _mk("s6_hold_gf16_div", "holdout", 8, 4, lambda r: _bits(_gf16_mul_const(_gf16_inv(r & 0xF), (r >> 4) & 0xF), 4), "GF16 division (8->4)"),
    ])
    hold_sh = gen_sh(2026120691, "holdout", "s6_hold_sh", 14, (8, 9, 10))
    hold_cp = gen_cp(2026120693, "holdout", "s6_hold_cp", 14, (8, 9, 10))

    suites = {
        "s6_train_g1": tg1, "s6_val_g1": vg1,
        "s6_train_g2": tg2, "s6_val_g2": vg2,
        "s6_train_g3": tg3, "s6_val_g3": vg3,
        "s6_train_g4": tg4, "s6_val_g4": vg4,
        "s6_hold_struct": hold_s,
        "s6_hold_proc_shared": hold_sh,
        "s6_hold_proc_comp": hold_cp,
    }
    assert sum(len(v) for v in suites.values()) == 172
    return suites


def s6_manifest_sha256(suites: Dict[str, List[BenchmarkTask]]) -> str:
    payload = {k: [t.public_dict() for t in v] for k, v in sorted(suites.items())}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
