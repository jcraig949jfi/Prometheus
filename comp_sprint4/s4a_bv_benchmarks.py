"""Track S4-A Fresh Sealed Benchmarks: 140-Task Hard 16-Bit Multi-Stage Z3 BV Suite.

Fixes all three compounding laws on a SECOND formal substrate (16-bit BV superoptimization):
  - s4a_train_g1 (12): 5 structured + 7 hard procedural (4..8 op cores obfuscated to 14..34 ops)
  - s4a_val_g1   (20): HIDDEN promotion gate for Gen 1 ONLY (8 struct + 12 proc)
  - s4a_train_g2 (12): 5 structured + 7 hard procedural
  - s4a_val_g2   (20): HIDDEN promotion gate for Gen 2 ONLY (8 struct + 12 proc)
  - s4a_train_g3 (12): 5 structured + 7 hard procedural
  - s4a_val_g3   (20): HIDDEN promotion gate for Gen 3 ONLY (8 struct + 12 proc)
  - s4a_hold_struct (18) + s4a_hold_proc (26) = 44 UNTOUCHED holdout tasks!

Strict invariant enforced at build time:
  - 100% deterministic generation (ZERO Z3 timeouts during manifest build).
  - ZERO duplicate task_ids and ZERO duplicate 32-vector output signatures across ALL 140 tasks!
"""
from __future__ import annotations

import hashlib
import json
import random
from typing import Any, Dict, List, Sequence, Tuple

from comp_sprint2.s2b_benchmarks import BVTask, _mk_task
from comp_sprint2.s2b_bv import BVBuilder, default_test_vectors
from comp_sprint2.s3b_benchmarks import _obf_chain, _obfuscate_hard_node, _sample_hard_proc_bv


def _obf2(b: BVBuilder, u: int, aux: int, m1: int, m2: int) -> int:
    return _obf_chain(b, _obf_chain(b, u, aux, m1), aux, m2)


def _gen_proc_bv(
    seed: int,
    split: str,
    prefix: str,
    count: int,
    core_range: Tuple[int, int],
    seen_sigs: set,
) -> List[BVTask]:
    rng = random.Random(seed)
    out: List[BVTask] = []
    idx = 0
    tvs = default_test_vectors(16, 3, seed=20261128, n_rand=28)
    while len(out) < count:
        n_in = 2 if (idx % 3 != 2) else 3
        n_core = rng.randint(core_range[0], core_range[1])
        tid = f"{prefix}_{idx:02d}_n{n_in}"
        t = _sample_hard_proc_bv(rng, tid, split, 16, n_in, n_core)
        if t is None:
            continue
        sub_tvs = tuple(tv[:n_in] for tv in tvs)
        sig = (n_in, t.spec.eval_vectors(sub_tvs))
        if sig in seen_sigs:
            continue
        seen_sigs.add(sig)
        out.append(t)
        idx += 1
    return out


def _make_struct_family(split: str, prefix: str, specs: Sequence[Tuple[str, int, Any, str]], seen_sigs: set) -> List[BVTask]:
    tvs = default_test_vectors(16, 3, seed=20261128, n_rand=28)
    out: List[BVTask] = []
    for name, n_in, fn, desc in specs:
        t = _mk_task(f"{prefix}_{name}", "structured", split, 16, n_in, fn, desc)
        sub_tvs = tuple(tv[:n_in] for tv in tvs)
        sig = (n_in, t.spec.eval_vectors(sub_tvs))
        assert sig not in seen_sigs, f"Duplicate BV signature for {t.task_id}"
        seen_sigs.add(sig)
        out.append(t)
    return out


# Reusable parameterized 16-bit multi-stage structured builders (5..10 op cores -> 16..34 op bloated specs)
def _fn_sat_add(b: BVBuilder, bias: int = 0) -> int:
    a = _obf_chain(b, 0, 1, 0)
    c = _obf_chain(b, 1, 0, 1)
    s = b.op("ADD", a, c)
    if bias:
        s = b.op("ADD", s, b.const(bias))
    ov = b.op("ULT", s, a)
    return _obf_chain(b, b.op("ITE", ov, b.const(0xFFFF), s), 0, 2)


def _fn_sat_sub(b: BVBuilder, bias: int = 0) -> int:
    a = _obf_chain(b, 0, 1, 1)
    c = _obf_chain(b, 1, 0, 2)
    d = b.op("SUB", a, c)
    if bias:
        d = b.op("XOR", d, b.const(bias))
    uf = b.op("ULT", a, c)
    return _obf_chain(b, b.op("ITE", uf, b.const(0), d), 1, 0)


def _fn_rot_mix(b: BVBuilder, sh: int, mul_c: int) -> int:
    x = _obf_chain(b, 0, 1, 0)
    y = _obf_chain(b, 1, 0, 2)
    rot = b.op("OR", b.op("SHL", x, b.const(sh)), b.op("LSHR", x, b.const(16 - sh)))
    res = b.op("XOR", b.op("MUL", rot, b.const(mul_c)), y)
    return _obf_chain(b, res, 0, 1)


def _fn_avg_floor(b: BVBuilder, xor_out: int = 0) -> int:
    a = _obf_chain(b, 0, 1, 2)
    c = _obf_chain(b, 1, 0, 0)
    avg = b.op("ADD", b.op("AND", a, c), b.op("LSHR", b.op("XOR", a, c), b.const(1)))
    if xor_out:
        avg = b.op("XOR", avg, b.const(xor_out))
    return _obf_chain(b, avg, 1, 1)


def _fn_avg_ceil(b: BVBuilder, add_out: int = 0) -> int:
    a = _obf_chain(b, 0, 1, 0)
    c = _obf_chain(b, 1, 0, 2)
    avg = b.op("SUB", b.op("OR", a, c), b.op("LSHR", b.op("XOR", a, c), b.const(1)))
    if add_out:
        avg = b.op("ADD", avg, b.const(add_out))
    return _obf_chain(b, avg, 0, 1)


def _fn_clamp3(b: BVBuilder, invert: bool = False) -> int:
    x = _obf_chain(b, 0, 1, 0)
    lo = _obf_chain(b, 1, 2, 1)
    hi = _obf_chain(b, 2, 0, 2)
    t1 = b.op("ITE", b.op("ULT", x, lo), lo, x)
    t2 = b.op("ITE", b.op("ULT", hi, t1), hi, t1)
    if invert:
        t2 = b.op("NOT", t2)
    return _obf_chain(b, t2, 0, 1)


def _fn_absdiff(b: BVBuilder, shift_r: int = 0) -> int:
    a = _obf_chain(b, 0, 1, 0)
    c = _obf_chain(b, 1, 0, 1)
    ad = b.op("ITE", b.op("ULT", a, c), b.op("SUB", c, a), b.op("SUB", a, c))
    if shift_r:
        ad = b.op("LSHR", ad, b.const(shift_r))
    return _obf_chain(b, ad, 1, 2)


def _fn_byte_swap_mix(b: BVBuilder, op2: str, c2: int) -> int:
    x = _obf_chain(b, 0, 1, 1)
    y = _obf_chain(b, 1, 0, 0)
    sw = b.op("OR", b.op("SHL", x, b.const(8)), b.op("LSHR", x, b.const(8)))
    res = b.op(op2, sw, b.op("XOR", y, b.const(c2)))
    return _obf_chain(b, res, 0, 2)


def _fn_nibble_pack(b: BVBuilder, mask1: int, sh1: int) -> int:
    a = _obf_chain(b, 0, 1, 0)
    c = _obf_chain(b, 1, 0, 2)
    p = b.op("OR", b.op("AND", a, b.const(mask1)), b.op("SHL", b.op("AND", c, b.const(mask1)), b.const(sh1)))
    return _obf_chain(b, p, 0, 1)


def _fn_poly_mba(b: BVBuilder, c1: int, c2: int, c3: int) -> int:
    a = _obf_chain(b, 0, 1, 2)
    c = _obf_chain(b, 1, 0, 0)
    t1 = b.op("MUL", b.op("XOR", a, c), b.const(c1))
    t2 = b.op("MUL", b.op("AND", a, c), b.const(c2))
    t3 = b.op("ADD", b.op("ADD", t1, t2), b.const(c3))
    return _obf_chain(b, t3, 1, 1)


def _fn_arx_round(b: BVBuilder, sh: int, k: int) -> int:
    a = _obf_chain(b, 0, 1, 0)
    c = _obf_chain(b, 1, 2, 1)
    d = _obf_chain(b, 2, 0, 2)
    s1 = b.op("ADD", a, c)
    s2 = b.op("XOR", s1, d)
    r = b.op("OR", b.op("SHL", s2, b.const(sh)), b.op("LSHR", s2, b.const(16 - sh)))
    return _obf_chain(b, b.op("ADD", r, b.const(k)), 0, 1)


def _fn_median3(b: BVBuilder, xor_k: int = 0) -> int:
    a = _obf_chain(b, 0, 1, 0)
    c = _obf_chain(b, 1, 2, 1)
    d = _obf_chain(b, 2, 0, 2)
    mn_ac = b.op("ITE", b.op("ULT", a, c), a, c)
    mx_ac = b.op("ITE", b.op("ULT", a, c), c, a)
    mx_lo = b.op("ITE", b.op("ULT", mn_ac, d), d, mn_ac)
    med = b.op("ITE", b.op("ULT", mx_lo, mx_ac), mx_lo, mx_ac)
    if xor_k:
        med = b.op("XOR", med, b.const(xor_k))
    return _obf_chain(b, med, 0, 1)


def _fn_bit_blend(b: BVBuilder, mask_c: int, op_post: str) -> int:
    a = _obf_chain(b, 0, 1, 1)
    c = _obf_chain(b, 1, 2, 2)
    m = b.op("AND", _obf_chain(b, 2, 0, 0), b.const(mask_c))
    bl = b.op("XOR", a, b.op("AND", b.op("XOR", a, c), m))
    return _obf_chain(b, b.op(op_post, bl, b.const(3)), 1, 0)


def _fn_gray_arith(b: BVBuilder, op2: str, k: int) -> int:
    x = _obf_chain(b, 0, 1, 0)
    y = _obf_chain(b, 1, 0, 2)
    gx = b.op("XOR", x, b.op("LSHR", x, b.const(1)))
    gy = b.op("XOR", y, b.op("LSHR", y, b.const(1)))
    return _obf_chain(b, b.op("ADD", b.op(op2, gx, gy), b.const(k)), 0, 1)


def _fn_parity_fold(b: BVBuilder, k_mul: int) -> int:
    x = _obf_chain(b, 0, 1, 2)
    y = _obf_chain(b, 1, 0, 1)
    p = b.op("XOR", x, b.op("LSHR", x, b.const(8)))
    p = b.op("XOR", p, b.op("LSHR", p, b.const(4)))
    p = b.op("AND", p, b.const(0xF))
    return _obf_chain(b, b.op("ADD", b.op("MUL", p, b.const(k_mul)), y), 0, 0)


def _fn_sign_extend_mix(b: BVBuilder, sh: int, add_c: int) -> int:
    x = _obf_chain(b, 0, 1, 0)
    y = _obf_chain(b, 1, 0, 1)
    se = b.op("ASHR", b.op("SHL", x, b.const(sh)), b.const(sh))
    return _obf_chain(b, b.op("ADD", b.op("XOR", se, y), b.const(add_c)), 1, 2)


def _fn_feistel_step(b: BVBuilder, sh1: int, sh2: int, k: int) -> int:
    l = _obf_chain(b, 0, 1, 1)
    r = _obf_chain(b, 1, 0, 2)
    f = b.op("XOR", b.op("ADD", b.op("SHL", r, b.const(sh1)), b.op("LSHR", r, b.const(sh2))), b.const(k))
    return _obf_chain(b, b.op("XOR", l, f), 0, 0)


def _fn_bit_extract_add(b: BVBuilder, sh: int, m: int) -> int:
    x = _obf_chain(b, 0, 1, 2)
    y = _obf_chain(b, 1, 0, 0)
    f1 = b.op("AND", b.op("LSHR", x, b.const(sh)), b.const(m))
    f2 = b.op("AND", b.op("LSHR", y, b.const(sh)), b.const(m))
    return _obf_chain(b, b.op("ADD", b.op("MUL", f1, b.const(3)), f2), 1, 1)


def _fn_cond_inc_dec(b: BVBuilder, step: int) -> int:
    x = _obf_chain(b, 0, 1, 0)
    y = _obf_chain(b, 1, 2, 1)
    z = _obf_chain(b, 2, 0, 2)
    cnd = b.op("EQ", b.op("AND", x, b.const(1)), b.const(0))
    res = b.op("ITE", cnd, b.op("ADD", y, b.const(step)), b.op("SUB", z, b.const(step)))
    return _obf_chain(b, res, 0, 1)


def build_s4a_bv_benchmarks() -> Dict[str, List[BVTask]]:
    """Build fresh sealed 140-task Track S4-A (16-bit deterministic Z3 BV) manifest."""
    seen_sigs: set = set()

    tg1_s = _make_struct_family("dev", "s4a_tg1", [
        ("sat_add", 2, lambda b: _fn_sat_add(b, 0), "16-bit saturating add"),
        ("rot5_m3", 2, lambda b: _fn_rot_mix(b, 5, 3), "rotl5(x)*3 ^ y"),
        ("avg_fl", 2, lambda b: _fn_avg_floor(b, 0), "overflow-free floor avg"),
        ("bswap_xor", 2, lambda b: _fn_byte_swap_mix(b, "XOR", 0x5A5A), "byteswap(x)^(y^0x5A5A)"),
        ("poly_3_5", 2, lambda b: _fn_poly_mba(b, 3, 5, 7), "poly MBA 3*(x^y)+5*(x&y)+7"),
    ], seen_sigs)
    tg1 = tg1_s + _gen_proc_bv(2026120101, "dev", "s4a_tg1_p", 7, (4, 7), seen_sigs)

    vg1_s = _make_struct_family("val_g1", "s4a_vg1", [
        ("sat_sub", 2, lambda b: _fn_sat_sub(b, 0), "16-bit saturating sub"),
        ("rot3_m5", 2, lambda b: _fn_rot_mix(b, 3, 5), "rotl3(x)*5 ^ y"),
        ("avg_cl", 2, lambda b: _fn_avg_ceil(b, 0), "overflow-free ceil avg"),
        ("absdiff", 2, lambda b: _fn_absdiff(b, 0), "16-bit |x-y|"),
        ("bswap_add", 2, lambda b: _fn_byte_swap_mix(b, "ADD", 0x1234), "byteswap(x)+(y^0x1234)"),
        ("clamp3", 3, lambda b: _fn_clamp3(b, False), "clamp(x, y, z)"),
        ("gray_add", 2, lambda b: _fn_gray_arith(b, "ADD", 5), "gray(x)+gray(y)+5"),
        ("feistel_2_3", 2, lambda b: _fn_feistel_step(b, 2, 3, 0x3C3C), "Feistel round (2,3)"),
    ], seen_sigs)
    vg1 = vg1_s + _gen_proc_bv(2026120111, "val_g1", "s4a_vg1_p", 12, (4, 8), seen_sigs)

    tg2_s = _make_struct_family("dev", "s4a_tg2", [
        ("arx_4", 3, lambda b: _fn_arx_round(b, 4, 0x9E37), "3-input ARX rot4"),
        ("nib_0f", 2, lambda b: _fn_nibble_pack(b, 0x00FF, 8), "byte pack"),
        ("blend_add", 3, lambda b: _fn_bit_blend(b, 0x0F0F, "ADD"), "masked bit blend + 3"),
        ("sext_4", 2, lambda b: _fn_sign_extend_mix(b, 4, 11), "12-bit sign-ext mix"),
        ("bext_3", 2, lambda b: _fn_bit_extract_add(b, 3, 0x1F), "bitfield extract MAC"),
    ], seen_sigs)
    tg2 = tg2_s + _gen_proc_bv(2026120121, "dev", "s4a_tg2_p", 7, (5, 8), seen_sigs)

    vg2_s = _make_struct_family("val_g2", "s4a_vg2", [
        ("arx_7", 3, lambda b: _fn_arx_round(b, 7, 0x45D9), "3-input ARX rot7"),
        ("median3", 3, lambda b: _fn_median3(b, 0), "3-input unsigned median"),
        ("nib_f0", 2, lambda b: _fn_nibble_pack(b, 0x0F0F, 4), "nibble interleave"),
        ("blend_xor", 3, lambda b: _fn_bit_blend(b, 0x5555, "XOR"), "odd/even bit blend ^ 3"),
        ("poly_7_2", 2, lambda b: _fn_poly_mba(b, 7, 2, 13), "poly MBA 7*(x^y)+2*(x&y)+13"),
        ("parfold_5", 2, lambda b: _fn_parity_fold(b, 5), "nibble parity fold *5 + y"),
        ("sext_8", 2, lambda b: _fn_sign_extend_mix(b, 8, 29), "8-bit sign-ext mix"),
        ("cond_inc5", 3, lambda b: _fn_cond_inc_dec(b, 5), "parity-gated y+5 / z-5"),
    ], seen_sigs)
    vg2 = vg2_s + _gen_proc_bv(2026120131, "val_g2", "s4a_vg2_p", 12, (5, 8), seen_sigs)

    tg3_s = _make_struct_family("dev", "s4a_tg3", [
        ("sat_add_b9", 2, lambda b: _fn_sat_add(b, 9), "sat add + bias 9"),
        ("absdiff_sr2", 2, lambda b: _fn_absdiff(b, 2), "|x-y| >> 2"),
        ("gray_xor", 2, lambda b: _fn_gray_arith(b, "XOR", 17), "gray(x)^gray(y)+17"),
        ("feistel_5_2", 2, lambda b: _fn_feistel_step(b, 5, 2, 0xA5A5), "Feistel round (5,2)"),
        ("cond_inc11", 3, lambda b: _fn_cond_inc_dec(b, 11), "parity-gated y+11 / z-11"),
    ], seen_sigs)
    tg3 = tg3_s + _gen_proc_bv(2026120141, "dev", "s4a_tg3_p", 7, (5, 8), seen_sigs)

    vg3_s = _make_struct_family("val_g3", "s4a_vg3", [
        ("sat_sub_x7", 2, lambda b: _fn_sat_sub(b, 7), "sat sub ^ 7"),
        ("rot9_m7", 2, lambda b: _fn_rot_mix(b, 9, 7), "rotl9(x)*7 ^ y"),
        ("avg_fl_x33", 2, lambda b: _fn_avg_floor(b, 0x33), "floor avg ^ 0x33"),
        ("clamp3_inv", 3, lambda b: _fn_clamp3(b, True), "~clamp(x,y,z)"),
        ("bswap_sub", 2, lambda b: _fn_byte_swap_mix(b, "SUB", 0xCAFE), "byteswap(x)-(y^0xCAFE)"),
        ("parfold_9", 2, lambda b: _fn_parity_fold(b, 9), "nibble parity fold *9 + y"),
        ("bext_5", 2, lambda b: _fn_bit_extract_add(b, 5, 0x3F), "6-bit field extract MAC"),
        ("median3_x5", 3, lambda b: _fn_median3(b, 5), "median3 ^ 5"),
    ], seen_sigs)
    vg3 = vg3_s + _gen_proc_bv(2026120151, "val_g3", "s4a_vg3_p", 12, (5, 8), seen_sigs)

    # ==================== UNTOUCHED FINAL HOLDOUT (44 tasks: 18 struct + 26 proc) ====================
    hold_s = _make_struct_family("holdout", "s4a_hold", [
        ("sat_add_b3", 2, lambda b: _fn_sat_add(b, 3), "sat add + bias 3"),
        ("sat_sub_x15", 2, lambda b: _fn_sat_sub(b, 15), "sat sub ^ 15"),
        ("rot6_m5", 2, lambda b: _fn_rot_mix(b, 6, 5), "rotl6(x)*5 ^ y"),
        ("rot11_m3", 2, lambda b: _fn_rot_mix(b, 11, 3), "rotl11(x)*3 ^ y"),
        ("avg_fl_x99", 2, lambda b: _fn_avg_floor(b, 0x99), "floor avg ^ 0x99"),
        ("avg_cl_a7", 2, lambda b: _fn_avg_ceil(b, 7), "ceil avg + 7"),
        ("absdiff_sr1", 2, lambda b: _fn_absdiff(b, 1), "|x-y| >> 1"),
        ("bswap_or", 2, lambda b: _fn_byte_swap_mix(b, "OR", 0x0F0F), "byteswap(x)|(y^0x0F0F)"),
        ("nib_3333", 2, lambda b: _fn_nibble_pack(b, 0x3333, 2), "2-bit stripe interleave"),
        ("poly_5_3", 2, lambda b: _fn_poly_mba(b, 5, 3, 19), "poly MBA 5*(x^y)+3*(x&y)+19"),
        ("arx_5", 3, lambda b: _fn_arx_round(b, 5, 0xBEEF), "3-input ARX rot5"),
        ("arx_11", 3, lambda b: _fn_arx_round(b, 11, 0x1357), "3-input ARX rot11"),
        ("median3_x2a", 3, lambda b: _fn_median3(b, 0x2A), "median3 ^ 0x2A"),
        ("blend_sub", 3, lambda b: _fn_bit_blend(b, 0x00FF, "SUB"), "low-byte blend - 3"),
        ("gray_sub", 2, lambda b: _fn_gray_arith(b, "SUB", 31), "gray(x)-gray(y)+31"),
        ("parfold_7", 2, lambda b: _fn_parity_fold(b, 7), "nibble parity fold *7 + y"),
        ("sext_6", 2, lambda b: _fn_sign_extend_mix(b, 6, 43), "10-bit sign-ext mix"),
        ("feistel_3_5", 2, lambda b: _fn_feistel_step(b, 3, 5, 0x7171), "Feistel round (3,5)"),
    ], seen_sigs)
    hold_p = _gen_proc_bv(2026120191, "holdout", "s4a_hold_p", 26, (5, 8), seen_sigs)

    suites = {
        "s4a_train_g1": tg1,
        "s4a_val_g1": vg1,
        "s4a_train_g2": tg2,
        "s4a_val_g2": vg2,
        "s4a_train_g3": tg3,
        "s4a_val_g3": vg3,
        "s4a_hold_struct": hold_s,
        "s4a_hold_proc": hold_p,
    }
    assert sum(len(v) for v in suites.values()) == 140
    return suites


def s4a_manifest_sha256(suites: Dict[str, List[BVTask]]) -> str:
    payload = {k: [t.public_dict() for t in v] for k, v in sorted(suites.items())}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
