"""Track S5-Q Fresh Sealed Benchmarks: 140-Task Exact Quantum/Reversible GL(n, F_2) CNOT Suite (n = 12..18 qubits).

Disjoint 3-Generation Law 2 Splits:
  - s5q_train_g1 (12), s5q_val_g1 (20)
  - s5q_train_g2 (12), s5q_val_g2 (20)
  - s5q_train_g3 (12), s5q_val_g3 (20)
  - UNTOUCHED HOLDOUT (44 brand-new n=12..18 matrices):
      * s5q_hold_struct      (18): cryptographic circulant/MDS/Feistel/prefix-XOR/LFSR/Toeplitz linear diffusion layers
      * s5q_hold_proc_dense  (13): 100% procedural uniform random dense GL(n, F_2) matrices
      * s5q_hold_proc_circ   (13): 100% procedural random CNOT-circuit-generated invertible matrices

Enforces 100% invertibility (`is_invertible_gf2`) and ZERO duplicate matrices across ALL 140 tasks!
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Sequence, Tuple

from comp_sprint5_quantum.s5q_core import apply_cnot_seq, is_invertible_gf2


@dataclass(frozen=True)
class CNOTTask:
    task_id: str
    stratum: str
    split: str
    n_qubits: int
    target_rows: Tuple[int, ...]
    description: str

    def public_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "stratum": self.stratum,
            "split": self.split,
            "n_qubits": self.n_qubits,
            "target_rows": list(self.target_rows),
            "description": self.description,
        }

    def sha256(self) -> str:
        return hashlib.sha256(json.dumps(self.public_dict(), sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


def _circulant(n: int, shifts: Sequence[int]) -> Tuple[int, ...]:
    base = list(shifts)
    for bump in range(n * n):
        cur = list(base)
        if bump > 0:
            cur[-1] = (base[-1] + bump) % n
            if len(set(cur)) < len(cur) or len(cur) % 2 == 0:
                continue
        rows = []
        for r in range(n):
            v = 0
            for sh in cur:
                v |= 1 << ((r + sh) % n)
            rows.append(v)
        t = tuple(rows)
        if is_invertible_gf2(t):
            return t
    # Fallback: guaranteed invertible odd-weight circulant (0, 1, 2) or (0, 1, 3)
    for a in range(1, n):
        for b in range(a + 1, n):
            rows = tuple((1 << r) | (1 << ((r + a) % n)) | (1 << ((r + b) % n)) for r in range(n))
            if is_invertible_gf2(rows):
                return rows
    raise ValueError(f"No invertible circulant found for n={n}")


def _lfsr_power(n: int, taps: Sequence[int], power: int) -> Tuple[int, ...]:
    # Companion matrix C raised to `power` over GF(2)
    c_mat = [0] * n
    for i in range(n - 1):
        c_mat[i] = 1 << (i + 1)
    last = 0
    for t in taps:
        last |= 1 << t
    c_mat[n - 1] = last

    def mul(a: List[int], b: List[int]) -> List[int]:
        out = [0] * n
        for i in range(n):
            v = a[i]
            acc = 0
            while v:
                lsb = v & -v
                acc ^= b[lsb.bit_length() - 1]
                v ^= lsb
            out[i] = acc
        return out

    res = [1 << i for i in range(n)]
    base = list(c_mat)
    p = power
    while p > 0:
        if p & 1:
            res = mul(res, base)
        base = mul(base, base)
        p >>= 1
    return tuple(res)


def _feistel_linear(n: int, taps_a: Sequence[int], taps_b: Sequence[int], rounds: int) -> Tuple[int, ...]:
    half = n // 2
    rows = [1 << i for i in range(n)]
    for rd in range(rounds):
        taps = taps_a if rd % 2 == 0 else taps_b
        src_off = 0 if rd % 2 == 0 else half
        dst_off = half if rd % 2 == 0 else 0
        new_rows = list(rows)
        for i in range(half):
            acc = rows[dst_off + i]
            for sh in taps:
                acc ^= rows[src_off + ((i + sh) % half)]
            new_rows[dst_off + i] = acc
        rows = new_rows
    return tuple(rows)


def _block_mix_mds(n: int, word: int, rot_shifts: Sequence[int]) -> Tuple[int, ...]:
    # Word-wise MDS-like binary diffusion (AES/Midori/SKINNY inspired): each word XORs rotated neighbors
    k = n // word
    rows = [1 << i for i in range(n)]
    # Apply 2 mixing layers
    for layer in range(2):
        nxt = list(rows)
        for blk in range(k):
            for bit in range(word):
                r = blk * word + bit
                acc = rows[r]
                for db, sh in enumerate(rot_shifts):
                    if db == 0:
                        continue
                    nb = (blk + db + layer) % k
                    acc ^= rows[nb * word + ((bit + sh + layer) % word)]
                nxt[r] = acc
        if is_invertible_gf2(nxt):
            rows = nxt
    return tuple(rows)


def _prefix_triangular(n: int, stride: int, rev: bool = False) -> Tuple[int, ...]:
    rows = [0] * n
    for i in range(n):
        v = 1 << i
        j = i + stride
        while j < n:
            v |= 1 << j
            j += stride
        if rev:
            rows[n - 1 - i] = v
        else:
            rows[i] = v
    # Make strictly invertible (if rev flipped, fix diagonal)
    if not is_invertible_gf2(rows):
        rows = [rows[n - 1 - i] for i in range(n)]
    return tuple(rows)


def _sample_dense_gl2(rng: random.Random, n: int) -> Tuple[int, ...]:
    mask = (1 << n) - 1
    while True:
        rows = tuple(rng.randint(1, mask) for _ in range(n))
        if is_invertible_gf2(rows):
            return rows


def _sample_circ_gl2(rng: random.Random, n: int, depth: int) -> Tuple[int, ...]:
    gates = []
    for _ in range(depth):
        c = rng.randrange(n)
        t = rng.randrange(n - 1)
        if t >= c:
            t += 1
        gates.append((c, t))
    return apply_cnot_seq(n, gates)


def build_s5q_benchmarks() -> Dict[str, List[CNOTTask]]:
    seen = set()

    def reg(tid: str, strat: str, split: str, rows: Tuple[int, ...], desc: str) -> CNOTTask:
        assert is_invertible_gf2(rows), f"Non-invertible matrix for {tid}"
        key = (len(rows), rows)
        assert key not in seen, f"Duplicate matrix for {tid}"
        seen.add(key)
        return CNOTTask(tid, strat, split, len(rows), rows, desc)

    def gen_dense(seed: int, split: str, prefix: str, count: int, widths: Sequence[int]) -> List[CNOTTask]:
        rng = random.Random(seed)
        out = []
        idx = 0
        while len(out) < count:
            n = widths[len(out) % len(widths)]
            rows = _sample_dense_gl2(rng, n)
            if (n, rows) in seen:
                continue
            out.append(reg(f"{prefix}_{idx:02d}_q{n}", "proc_dense", split, rows, f"Uniform random dense GL({n},F2)"))
            idx += 1
        return out

    def gen_circ(seed: int, split: str, prefix: str, count: int, widths: Sequence[int]) -> List[CNOTTask]:
        rng = random.Random(seed)
        out = []
        idx = 0
        while len(out) < count:
            n = widths[len(out) % len(widths)]
            depth = rng.randint(3 * n, 5 * n)
            rows = _sample_circ_gl2(rng, n, depth)
            if (n, rows) in seen or sum(r.bit_count() for r in rows) < 2 * n:
                continue
            out.append(reg(f"{prefix}_{idx:02d}_q{n}", "proc_circ", split, rows, f"Random {depth}-CNOT GL({n},F2)"))
            idx += 1
        return out

    # Structured families parameterized cleanly with distinct n & parameters across splits
    def struct_pack(split: str, prefix: str, specs: Sequence[Tuple[str, Tuple[int, ...], str]]) -> List[CNOTTask]:
        return [reg(f"{prefix}_{nm}", "structured", split, m, d) for nm, m, d in specs]

    # Primitive polynomials (taps with tap 0 included for invertibility)
    tg1 = struct_pack("dev", "s5q_tg1", [
        ("circ12_015", _circulant(12, (0, 1, 5)), "12q circulant (0,1,5)"),
        ("lfsr12_p17", _lfsr_power(12, (0, 1, 4, 6), 17), "12q LFSR^17"),
        ("feis12_r3", _feistel_linear(12, (0, 1, 3), (0, 2, 4), 3), "12q 3-rd linear Feistel"),
        ("mds12_w3", _block_mix_mds(12, 3, (0, 1, 2)), "12q 4x3b MDS mix"),
    ]) + gen_dense(2026120501, "dev", "s5q_tg1_d", 4, (12, 14)) + gen_circ(2026120502, "dev", "s5q_tg1_c", 4, (12, 14))

    vg1 = struct_pack("val_g1", "s5q_vg1", [
        ("circ13_014", _circulant(13, (0, 1, 4)), "13q circulant (0,1,4)"),
        ("circ14_0135", _circulant(14, (0, 1, 3, 5, 8)), "14q 5-tap circulant"),
        ("lfsr13_p19", _lfsr_power(13, (0, 1, 3, 4), 19), "13q LFSR^19"),
        ("lfsr14_p23", _lfsr_power(14, (0, 1, 6, 10), 23), "14q LFSR^23"),
        ("feis14_r4", _feistel_linear(14, (0, 1, 2), (0, 3, 5), 4), "14q 4-rd Feistel"),
        ("mds16_w4a", _block_mix_mds(16, 4, (0, 1, 3)), "16q 4x4b MDS mix"),
        ("pref14_s1", _prefix_triangular(14, 1), "14q prefix-XOR"),
        ("pref15_s2", _prefix_triangular(15, 2), "15q stride-2 triangular"),
    ]) + gen_dense(2026120511, "val_g1", "s5q_vg1_d", 6, (12, 14, 16)) + gen_circ(2026120512, "val_g1", "s5q_vg1_c", 6, (12, 14, 16))

    tg2 = struct_pack("dev", "s5q_tg2", [
        ("circ15_0147", _circulant(15, (0, 1, 4, 7, 11)), "15q 5-tap circulant"),
        ("lfsr15_p27", _lfsr_power(15, (0, 1), 27), "15q LFSR^27"),
        ("feis16_r4", _feistel_linear(16, (0, 1, 4), (0, 2, 5), 4), "16q 4-rd Feistel"),
        ("mds15_w3", _block_mix_mds(15, 3, (0, 1, 2)), "15q 5x3b MDS mix"),
    ]) + gen_dense(2026120521, "dev", "s5q_tg2_d", 4, (14, 16)) + gen_circ(2026120522, "dev", "s5q_tg2_c", 4, (14, 16))

    vg2 = struct_pack("val_g2", "s5q_vg2", [
        ("circ16_01369", _circulant(16, (0, 1, 3, 6, 9)), "16q 5-tap circulant"),
        ("circ15_0258", _circulant(15, (0, 2, 5, 8, 12)), "15q 5-tap circulant B"),
        ("lfsr16_p29", _lfsr_power(16, (0, 2, 3, 5), 29), "16q LFSR^29"),
        ("lfsr15_p35", _lfsr_power(15, (0, 1, 4, 7), 35), "15q LFSR^35"),
        ("feis16_r5", _feistel_linear(16, (0, 2, 3), (0, 1, 6), 5), "16q 5-rd Feistel"),
        ("mds16_w4b", _block_mix_mds(16, 4, (0, 2, 1)), "16q 4x4b MDS mix B"),
        ("pref16_s1", _prefix_triangular(16, 1), "16q prefix-XOR"),
        ("feis14_r5", _feistel_linear(14, (0, 2, 4), (0, 1, 3), 5), "14q 5-rd Feistel"),
    ]) + gen_dense(2026120531, "val_g2", "s5q_vg2_d", 6, (14, 16, 18)) + gen_circ(2026120532, "val_g2", "s5q_vg2_c", 6, (14, 16, 18))

    tg3 = struct_pack("dev", "s5q_tg3", [
        ("circ17_0148", _circulant(17, (0, 1, 4, 8, 13)), "17q 5-tap circulant"),
        ("lfsr17_p31", _lfsr_power(17, (0, 3), 31), "17q LFSR^31"),
        ("feis18_r4", _feistel_linear(18, (0, 1, 4), (0, 2, 6), 4), "18q 4-rd Feistel"),
        ("mds18_w3", _block_mix_mds(18, 3, (0, 1, 2)), "18q 6x3b MDS mix"),
    ]) + gen_dense(2026120541, "dev", "s5q_tg3_d", 4, (16, 18)) + gen_circ(2026120542, "dev", "s5q_tg3_c", 4, (16, 18))

    vg3 = struct_pack("val_g3", "s5q_vg3", [
        ("circ18_013711", _circulant(18, (0, 1, 3, 7, 11)), "18q 5-tap circulant"),
        ("circ17_0259", _circulant(17, (0, 2, 5, 9, 14)), "17q 5-tap circulant B"),
        ("lfsr18_p33", _lfsr_power(18, (0, 7), 33), "18q LFSR^33"),
        ("lfsr16_p41", _lfsr_power(16, (0, 2, 3, 5), 41), "16q LFSR^41"),
        ("feis18_r5", _feistel_linear(18, (0, 1, 5), (0, 3, 7), 5), "18q 5-rd Feistel"),
        ("mds18_w6", _block_mix_mds(18, 6, (0, 1, 4)), "18q 3x6b MDS mix"),
        ("pref18_s1", _prefix_triangular(18, 1), "18q prefix-XOR"),
        ("pref17_s2", _prefix_triangular(17, 2), "17q stride-2 triangular"),
    ]) + gen_dense(2026120551, "val_g3", "s5q_vg3_d", 6, (14, 16, 18)) + gen_circ(2026120552, "val_g3", "s5q_vg3_c", 6, (14, 16, 18))

    # ==================== UNTOUCHED FINAL HOLDOUT (44 tasks: 18 struct + 13 dense + 13 circ) ====================
    hold_s = struct_pack("holdout", "s5q_hold", [
        ("circ12_025", _circulant(12, (0, 2, 5)), "12q circulant (0,2,5)"),
        ("circ14_0147", _circulant(14, (0, 1, 4, 7, 10)), "14q 5-tap circulant"),
        ("circ15_013610", _circulant(15, (0, 1, 3, 6, 10)), "15q 5-tap circulant"),
        ("circ16_01259", _circulant(16, (0, 1, 2, 5, 9)), "16q 5-tap circulant"),
        ("circ17_013611", _circulant(17, (0, 1, 3, 6, 11)), "17q 5-tap circulant"),
        ("circ18_014813", _circulant(18, (0, 1, 4, 8, 13)), "18q 5-tap circulant"),
        ("lfsr12_p25", _lfsr_power(12, (0, 1, 4, 6), 25), "12q LFSR^25"),
        ("lfsr14_p31", _lfsr_power(14, (0, 1, 6, 10), 31), "14q LFSR^31"),
        ("lfsr16_p37", _lfsr_power(16, (0, 2, 3, 5), 37), "16q LFSR^37"),
        ("lfsr17_p43", _lfsr_power(17, (0, 3), 43), "17q LFSR^43"),
        ("lfsr18_p47", _lfsr_power(18, (0, 7), 47), "18q LFSR^47"),
        ("feis12_r5", _feistel_linear(12, (0, 1, 2), (0, 2, 5), 5), "12q 5-rd Feistel"),
        ("feis16_r6", _feistel_linear(16, (0, 1, 3, 5), (0, 2, 4, 7), 6), "16q 6-rd Feistel"),
        ("feis18_r6", _feistel_linear(18, (0, 2, 5), (0, 1, 4, 8), 6), "18q 6-rd Feistel"),
        ("mds12_w4", _block_mix_mds(12, 4, (0, 1, 3)), "12q 3x4b MDS mix"),
        ("mds16_w4c", _block_mix_mds(16, 4, (0, 3, 2)), "16q 4x4b MDS mix C"),
        ("mds18_w6b", _block_mix_mds(18, 6, (0, 2, 5)), "18q 3x6b MDS mix B"),
        ("pref18_s3", _prefix_triangular(18, 3), "18q stride-3 triangular"),
    ])
    hold_d = gen_dense(2026120591, "holdout", "s5q_hold_d", 13, (12, 14, 16, 18))
    hold_c = gen_circ(2026120593, "holdout", "s5q_hold_c", 13, (12, 14, 16, 18))

    suites = {
        "s5q_train_g1": tg1, "s5q_val_g1": vg1,
        "s5q_train_g2": tg2, "s5q_val_g2": vg2,
        "s5q_train_g3": tg3, "s5q_val_g3": vg3,
        "s5q_hold_struct": hold_s,
        "s5q_hold_proc_dense": hold_d,
        "s5q_hold_proc_circ": hold_c,
    }
    assert sum(len(v) for v in suites.values()) == 140
    return suites


def s5q_manifest_sha256(suites: Dict[str, List[CNOTTask]]) -> str:
    payload = {k: [t.public_dict() for t in v] for k, v in sorted(suites.items())}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
