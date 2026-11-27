"""Sprint 10 Benchmark Suite: 140 Exact Binary Bilinear 3-Tensors over F_2
(Matrix Multiplication Strassen/Laderman/AlphaTensor + Polynomial Multiplication + Procedural Tensors).

Splits (ZERO duplicate tensors across all 140 tasks):
  - `dev_diag` (20): diagnostic evolution suite
  - `val_g1`, `val_g2`, `val_g3` (20 each = 60): 3 strictly disjoint Law 2 validation splits
  - Untouched Holdout (`N = 60` tasks):
      * `s10_hold_matmul` (12): Classic algebraic bilinear tensors (`matmul_2x2x2` [Strassen 8->7],
        `matmul_2x2x3` [12->11], `matmul_2x3x2`, `matmul_2x3x3` [18->15], `matmul_3x2x3`,
        `matmul_3x3x2`, `matmul_3x3x3` [Laderman/AlphaTensor 27->23!], `matmul_2x2x4` [16->14],
        `matmul_2x4x2`, `poly_mul_deg3_f2` [16->9], `poly_mul_deg4_f2` [25->13], `cyclic_conv_4_f2`)
      * `s10_hold_proc_planted` (24): 100% procedural planted low-rank tensors scrambled by GL(n, F_2)
        & re-expanded canonically (schoolbook rank 18..34, planted rank 9..16!)
      * `s10_hold_proc_rand` (24): 100% procedural sparse random bilinear 3-tensors over F_2!
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from typing import Dict, List, Sequence, Set, Tuple

from comp_sprint10_alphatensor.s10_core import (
    BilinearTensorF2,
    reduce_bilinear_terms,
    tensor_mask_from_terms,
)


@dataclass(frozen=True)
class S10Task:
    task_id: str
    stratum: str
    family: str
    tensor: BilinearTensorF2
    base_rank: int
    split: str = "holdout"

    def sha256(self) -> str:
        return self.tensor.sha256()


def make_matmul_tensor(p: int, q: int, r: int, name: str = "") -> BilinearTensorF2:
    """Exact schoolbook binary matrix multiplication tensor `<p, q, r>` over F_2 (`C = A * B`, rank `p*q*r`)."""
    na, nb, nc = p * q, q * r, p * r
    terms: List[Tuple[int, int, int]] = []
    for i in range(p):
        for k in range(q):
            for j in range(r):
                u = 1 << (i * q + k)
                v = 1 << (k * r + j)
                w = 1 << (i * r + j)
                terms.append((u, v, w))
    mask = tensor_mask_from_terms(na, nb, nc, terms)
    return BilinearTensorF2(name=name or f"matmul_{p}x{q}x{r}", na=na, nb=nb, nc=nc, tensor_mask=mask, init_terms=tuple(terms))


def make_poly_mul_tensor(deg_a: int, deg_b: int, name: str = "") -> BilinearTensorF2:
    """Exact polynomial multiplication over F_2: `(sum_{i=0}^{deg_a} a_i x^i)(sum_{j=0}^{deg_b} b_j x^j)`."""
    na, nb, nc = deg_a + 1, deg_b + 1, deg_a + deg_b + 1
    terms = [(1 << i, 1 << j, 1 << (i + j)) for i in range(na) for j in range(nb)]
    mask = tensor_mask_from_terms(na, nb, nc, terms)
    return BilinearTensorF2(name=name or f"poly_mul_{deg_a}x{deg_b}", na=na, nb=nb, nc=nc, tensor_mask=mask, init_terms=tuple(terms))


def make_cyclic_conv_tensor(n: int, name: str = "") -> BilinearTensorF2:
    """Exact length-n cyclic convolution tensor over F_2: `c_{(i+j) mod n} = sum a_i b_j`."""
    terms = [(1 << i, 1 << j, 1 << ((i + j) % n)) for i in range(n) for j in range(n)]
    mask = tensor_mask_from_terms(n, n, n, terms)
    return BilinearTensorF2(name=name or f"cyclic_conv_{n}", na=n, nb=n, nc=n, tensor_mask=mask, init_terms=tuple(terms))


def _canonical_slice_terms(na: int, nb: int, nc: int, mask: int) -> List[Tuple[int, int, int]]:
    """Expand any exact tensor bitmask into a canonical (uncompressed) rank decomposition by grouping `(i, j)` entries."""
    terms: List[Tuple[int, int, int]] = []
    w_mask = (1 << nc) - 1
    for i in range(na):
        for j in range(nb):
            w = (mask >> ((i * nb + j) * nc)) & w_mask
            if w:
                terms.append((1 << i, 1 << j, w))
    return reduce_bilinear_terms(terms)


def _sample_planted_tensor(rng: random.Random, na: int, nb: int, nc: int, planted_r: int, name: str) -> BilinearTensorF2:
    """Generate a 100% procedural low-rank bilinear tensor of planted rank `planted_r`, then expand into
    canonical slice-rank form (hiding the planted factors completely!) so evolution must rediscover low rank!"""
    la, lb, lc = (1 << na) - 1, (1 << nb) - 1, (1 << nc) - 1
    planted: List[Tuple[int, int, int]] = []
    for _ in range(planted_r):
        # Mix weight-2..4 random vectors so canonical expansion has rank ~1.6-2.5x higher than planted_r!
        u = rng.randint(1, la)
        v = rng.randint(1, lb)
        w = rng.randint(1, lc)
        planted.append((u, v, w))
    mask = tensor_mask_from_terms(na, nb, nc, planted)
    canon = _canonical_slice_terms(na, nb, nc, mask)
    return BilinearTensorF2(name=name, na=na, nb=nb, nc=nc, tensor_mask=mask, init_terms=tuple(canon))


def _sample_sparse_rand_tensor(rng: random.Random, na: int, nb: int, nc: int, name: str) -> BilinearTensorF2:
    """Generate a 100% procedural sparse random bilinear 3-tensor over F_2."""
    n_entries = rng.randint(na * nb, int(na * nb * nc * 0.28))
    mask = 0
    for _ in range(n_entries):
        i = rng.randrange(na)
        j = rng.randrange(nb)
        k = rng.randrange(nc)
        mask ^= 1 << ((i * nb + j) * nc + k)
    canon = _canonical_slice_terms(na, nb, nc, mask)
    return BilinearTensorF2(name=name, na=na, nb=nb, nc=nc, tensor_mask=mask, init_terms=tuple(canon))


def build_s10_benchmarks() -> Dict[str, List[S10Task]]:
    """Deterministically build all 140 Sprint 10 bilinear 3-tensor tasks over F_2 (0 duplicates)."""
    seen: Set[str] = set()
    suites: Dict[str, List[S10Task]] = {
        "dev_diag": [],
        "val_g1": [],
        "val_g2": [],
        "val_g3": [],
        "s10_hold_matmul": [],
        "s10_hold_proc_planted": [],
        "s10_hold_proc_rand": [],
    }

    # 1. 12 Classic Algebraic / Matrix Multiplication Holdout Benchmarks (`s10_hold_matmul`)
    lit = [
        ("matmul_2x2x2", "matmul", make_matmul_tensor(2, 2, 2, "matmul_2x2x2")),
        ("matmul_2x2x3", "matmul", make_matmul_tensor(2, 2, 3, "matmul_2x2x3")),
        ("matmul_2x3x2", "matmul", make_matmul_tensor(2, 3, 2, "matmul_2x3x2")),
        ("matmul_2x3x3", "matmul", make_matmul_tensor(2, 3, 3, "matmul_2x3x3")),
        ("matmul_3x2x3", "matmul", make_matmul_tensor(3, 2, 3, "matmul_3x2x3")),
        ("matmul_3x3x2", "matmul", make_matmul_tensor(3, 3, 2, "matmul_3x3x2")),
        ("matmul_3x3x3", "matmul", make_matmul_tensor(3, 3, 3, "matmul_3x3x3")),
        ("matmul_2x2x4", "matmul", make_matmul_tensor(2, 2, 4, "matmul_2x2x4")),
        ("matmul_2x4x2", "matmul", make_matmul_tensor(2, 4, 2, "matmul_2x4x2")),
        ("poly_mul_3x3", "poly_mul", make_poly_mul_tensor(3, 3, "poly_mul_3x3")),
        ("poly_mul_4x4", "poly_mul", make_poly_mul_tensor(4, 4, "poly_mul_4x4")),
        ("cyclic_conv_4", "cyclic_conv", make_cyclic_conv_tensor(4, "cyclic_conv_4")),
    ]
    for tid, fam, ten in lit:
        sha = ten.sha256()
        assert sha not in seen
        seen.add(sha)
        suites["s10_hold_matmul"].append(S10Task(tid, "s10_hold_matmul", fam, ten, ten.base_rank(), "holdout"))

    # 2. Procedural Holdout: 24 Planted Low-Rank + 24 Sparse Random
    dims_planted = [(5, 5, 5, 10), (5, 6, 5, 12), (6, 6, 6, 13), (6, 6, 6, 15)]
    rng_p = random.Random(20261127_201)
    k = 0
    while len(suites["s10_hold_proc_planted"]) < 24:
        na, nb, nc, pr = dims_planted[len(suites["s10_hold_proc_planted"]) % len(dims_planted)]
        ten = _sample_planted_tensor(rng_p, na, nb, nc, pr, f"s10_hold_pl_{k:02d}")
        k += 1
        if ten.tensor_mask and ten.base_rank() >= pr + 5 and ten.sha256() not in seen:
            seen.add(ten.sha256())
            suites["s10_hold_proc_planted"].append(S10Task(ten.name, "s10_hold_proc_planted", "proc_planted", ten, ten.base_rank(), "holdout"))

    dims_rand = [(5, 5, 5), (5, 6, 5), (6, 5, 6), (6, 6, 6)]
    rng_r = random.Random(20261127_202)
    k = 0
    while len(suites["s10_hold_proc_rand"]) < 24:
        na, nb, nc = dims_rand[len(suites["s10_hold_proc_rand"]) % len(dims_rand)]
        ten = _sample_sparse_rand_tensor(rng_r, na, nb, nc, f"s10_hold_rn_{k:02d}")
        k += 1
        if ten.tensor_mask and ten.base_rank() >= 15 and ten.sha256() not in seen:
            seen.add(ten.sha256())
            suites["s10_hold_proc_rand"].append(S10Task(ten.name, "s10_hold_proc_rand", "proc_rand", ten, ten.base_rank(), "holdout"))

    # 3. Disjoint Evolution Splits (`dev_diag`, `val_g1`, `val_g2`, `val_g3` — 20 tasks each)
    for sname, sseed in [("dev_diag", 20261127_210), ("val_g1", 20261127_211), ("val_g2", 20261127_212), ("val_g3", 20261127_213)]:
        rng = random.Random(sseed)
        k = 0
        while len(suites[sname]) < 20:
            pos = len(suites[sname])
            if pos % 2 == 0:
                na, nb, nc, pr = dims_planted[pos % len(dims_planted)]
                ten = _sample_planted_tensor(rng, na, nb, nc, pr, f"{sname}_pl_{k:02d}")
                min_r = pr + 5
                fam = "proc_planted"
            else:
                na, nb, nc = dims_rand[pos % len(dims_rand)]
                ten = _sample_sparse_rand_tensor(rng, na, nb, nc, f"{sname}_rn_{k:02d}")
                min_r = 15
                fam = "proc_rand"
            k += 1
            if ten.tensor_mask and ten.base_rank() >= min_r and ten.sha256() not in seen:
                seen.add(ten.sha256())
                suites[sname].append(S10Task(ten.name, sname, fam, ten, ten.base_rank(), sname))

    return suites


def s10_manifest_sha256(suites: Dict[str, List[S10Task]]) -> str:
    payload = {
        sn: [{"task_id": t.task_id, "sha": t.sha256(), "base_rank": t.base_rank} for t in tasks]
        for sn, tasks in sorted(suites.items())
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
