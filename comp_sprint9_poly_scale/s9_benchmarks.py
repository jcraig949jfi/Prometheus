"""Sprint 9 Benchmark Suite: 320 Fresh `n = 12..16` Qubit Fault-Tolerant Quantum `Clifford+T` Circuits
(Up to 65,536-Dimensional Hilbert Space — Polynomial Exact Verification!).

Splits (ZERO duplicate `(n, L, Q, T)` tensors across all 320 tasks):
  - `dev_diag` (20): 4 each for `n = 12, 13, 14, 15, 16`
  - `val_g1`, `val_g2`, `val_g3`, `val_g4` (25 each = 100): 4 strictly disjoint Law 2 validation splits
  - Untouched Holdout (`N = 200` tasks — 2.5x Sprint 8, 4.5x Sprint 7!):
      * `s9_hold_lit` (40): Real fault-tolerant quantum literature circuits on `n = 12..16` qubits
        (`gf2^4_mult` [12q], `gf2^5_mult` [15q], Cuccaro adders [12..16q], VBE adders [12..16q],
         Barenco multi-control Toffolis [12..16q], QCLA carry trees [12..16q], CSUM-MUX [12..16q],
         Grover 3-SAT/clique phase oracles [12..16q])
      * `s9_hold_proc_ccz` (80): 100% procedural zero-LLM random `CCZ` networks (`n = 12..16`)
      * `s9_hold_proc_rand` (80): 100% procedural zero-LLM random symmetric 3-tensors (`n = 12..16`)
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from typing import Dict, List, Sequence, Set, Tuple

from comp_sprint7_clifford_t.s7_core import CliffordTCircuit, extract_phase_poly
from comp_sprint8_science.s8_benchmarks import (
    _build_from_cubic_triples,
    _exact_ccz_network,
    _lit_barenco_tof,
    _lit_csum_mux,
    _lit_cuccaro_adder,
    _lit_gf2_multiplier,
    _lit_grover_oracle,
    _lit_qcla_carry,
    _lit_vbe_adder,
)
from comp_sprint8_science.s8_core import odd_t_parities
from comp_sprint9_poly_scale.s9_poly_core import (
    fast_lin_quad_cubic_parity,
    tpar_poly_optimize,
)


@dataclass(frozen=True)
class S9Task:
    task_id: str
    stratum: str
    n_qubits: int
    circuit: CliffordTCircuit
    tensor_sha: str
    base_t: int
    tpar_t: int
    family: str
    split: str = "holdout"

    def sha256(self) -> str:
        return self.tensor_sha


def _sample_s9_proc_ccz(rng: random.Random, n_qubits: int) -> CliffordTCircuit:
    """100% procedural zero-LLM `CCZ` network on `n = 12..16` qubits (rich overlapping parity structure)."""
    n_blocks = rng.randint(2, 3)
    gates: List[Tuple] = []
    for _ in range(n_blocks):
        for _ in range(rng.randint(3, n_qubits // 2 + 1)):
            c, t = rng.sample(range(n_qubits), 2)
            gates.append(("CNOT", c, t))
        # Keep odd-T count in the realistic sweet spot (~30..65 T-gates after T-par!)
        n_ccz = rng.randint(max(5, n_qubits // 2), n_qubits)
        triples = [tuple(sorted(rng.sample(range(n_qubits), 3))) for _ in range(n_ccz)]
        gates.extend(_exact_ccz_network(n_qubits, triples).gates)
    return CliffordTCircuit(n_qubits=n_qubits, gates=tuple(gates))


def _sample_s9_proc_rand(rng: random.Random, n_qubits: int) -> CliffordTCircuit:
    """100% procedural zero-LLM random symmetric 3-tensor / `RM(n-4, n)` coset instance on `n = 12..16`."""
    # Clustered around 3-5 hub qubits + uniform random triples so non-trivial RM cancellations exist!
    n_triples = rng.randint(n_qubits + 4, 2 * n_qubits + 2)
    triples: List[Tuple[int, int, int]] = []
    hubs = rng.sample(range(n_qubits), min(4, n_qubits))
    while len(triples) < n_triples:
        if len(triples) % 2 == 0:
            h = rng.choice(hubs)
            a, b = rng.sample([q for q in range(n_qubits) if q != h], 2)
            t = tuple(sorted((h, a, b)))
        else:
            t = tuple(sorted(rng.sample(range(n_qubits), 3)))
        if t not in triples:
            triples.append(t)
    pre = []
    for _ in range(rng.randint(n_qubits // 2, n_qubits)):
        c, t = rng.sample(range(n_qubits), 2)
        pre.append((c, t))
    return _build_from_cubic_triples(n_qubits, triples, extra_cnots=pre)


def _make_s9_task(
    task_id: str,
    stratum: str,
    family: str,
    circ: CliffordTCircuit,
    seen: Set[Tuple[int, int]],
    split: str = "holdout",
) -> S9Task | None:
    poly, _ = extract_phase_poly(circ)
    par = odd_t_parities(poly)
    if len(par) < 16:
        return None
    _, _, cmask = fast_lin_quad_cubic_parity(circ.n_qubits, par)
    if cmask == 0 or (circ.n_qubits, cmask) in seen:
        return None
    seen.add((circ.n_qubits, cmask))
    tp = tpar_poly_optimize(circ)
    tsha = hashlib.sha256(f"s9:{circ.n_qubits}:{cmask}".encode("ascii")).hexdigest()
    return S9Task(
        task_id=task_id,
        stratum=stratum,
        n_qubits=circ.n_qubits,
        circuit=circ,
        tensor_sha=tsha,
        base_t=circ.t_count(),
        tpar_t=tp.t_count(),
        family=family,
        split=split,
    )


def build_s9_benchmarks() -> Dict[str, List[S9Task]]:
    """Deterministically build all 320 Sprint 9 tasks across `n = 12..16` qubits (0 duplicate cubic tensors)."""
    seen: Set[Tuple[int, int]] = set()
    suites: Dict[str, List[S9Task]] = {
        "dev_diag": [],
        "val_g1": [],
        "val_g2": [],
        "val_g3": [],
        "val_g4": [],
        "s9_hold_lit": [],
        "s9_hold_proc_ccz": [],
        "s9_hold_proc_rand": [],
    }

    # 1. 40 Real Literature Fault-Tolerant Quantum Circuits across n = 12, 13, 14, 15, 16!
    lit_specs = [
        # Cuccaro ripple-carry adders (12..16q)
        ("s9_lit_cuccaro_12a", "cuccaro_adder", _lit_cuccaro_adder(12, 0)),
        ("s9_lit_cuccaro_13a", "cuccaro_adder", _lit_cuccaro_adder(13, 1)),
        ("s9_lit_cuccaro_14a", "cuccaro_adder", _lit_cuccaro_adder(14, 0)),
        ("s9_lit_cuccaro_15a", "cuccaro_adder", _lit_cuccaro_adder(15, 1)),
        ("s9_lit_cuccaro_16a", "cuccaro_adder", _lit_cuccaro_adder(16, 0)),
        # VBE ripple-carry adders (12..16q)
        ("s9_lit_vbe_12a", "vbe_adder", _lit_vbe_adder(12, 0)),
        ("s9_lit_vbe_13a", "vbe_adder", _lit_vbe_adder(13, 1)),
        ("s9_lit_vbe_14a", "vbe_adder", _lit_vbe_adder(14, 0)),
        ("s9_lit_vbe_15a", "vbe_adder", _lit_vbe_adder(15, 1)),
        ("s9_lit_vbe_16a", "vbe_adder", _lit_vbe_adder(16, 0)),
        # GF(2^4) & GF(2^5) quantum multipliers (12..16q — famous hard T-count benchmarks!)
        ("s9_lit_gf2_4_mult_12a", "gf2_mult", _lit_gf2_multiplier(12, 4, 0)),
        ("s9_lit_gf2_4_mult_12b", "gf2_mult", _lit_gf2_multiplier(12, 4, 2)),
        ("s9_lit_gf2_4_mult_13a", "gf2_mult", _lit_gf2_multiplier(13, 4, 1)),
        ("s9_lit_gf2_4_mult_14a", "gf2_mult", _lit_gf2_multiplier(14, 4, 0)),
        ("s9_lit_gf2_5_mult_15a", "gf2_mult", _lit_gf2_multiplier(15, 5, 0)),
        ("s9_lit_gf2_5_mult_15b", "gf2_mult", _lit_gf2_multiplier(15, 5, 2)),
        ("s9_lit_gf2_5_mult_16a", "gf2_mult", _lit_gf2_multiplier(16, 5, 1)),
        # Barenco multi-controlled Toffolis (12..16q)
        ("s9_lit_barenco_12a", "barenco_tof", _lit_barenco_tof(12, 7, 0)),
        ("s9_lit_barenco_13a", "barenco_tof", _lit_barenco_tof(13, 8, 1)),
        ("s9_lit_barenco_14a", "barenco_tof", _lit_barenco_tof(14, 8, 0)),
        ("s9_lit_barenco_15a", "barenco_tof", _lit_barenco_tof(15, 9, 1)),
        ("s9_lit_barenco_16a", "barenco_tof", _lit_barenco_tof(16, 10, 0)),
        # Draper QCLA carry-lookahead prefix trees (12..16q)
        ("s9_lit_qcla_12a", "qcla_carry", _lit_qcla_carry(12, 0)),
        ("s9_lit_qcla_13a", "qcla_carry", _lit_qcla_carry(13, 1)),
        ("s9_lit_qcla_14a", "qcla_carry", _lit_qcla_carry(14, 0)),
        ("s9_lit_qcla_15a", "qcla_carry", _lit_qcla_carry(15, 1)),
        ("s9_lit_qcla_16a", "qcla_carry", _lit_qcla_carry(16, 0)),
        # Conditional-sum multiplexers (12..16q)
        ("s9_lit_csum_12a", "csum_mux", _lit_csum_mux(12, 0)),
        ("s9_lit_csum_13a", "csum_mux", _lit_csum_mux(13, 1)),
        ("s9_lit_csum_14a", "csum_mux", _lit_csum_mux(14, 0)),
        ("s9_lit_csum_15a", "csum_mux", _lit_csum_mux(15, 1)),
        ("s9_lit_csum_16a", "csum_mux", _lit_csum_mux(16, 0)),
        # Structured 3-SAT / Clique Grover Oracles (12..16q)
        ("s9_lit_grover_12a", "grover_oracle", _lit_grover_oracle(12, 11)),
        ("s9_lit_grover_12b", "grover_oracle", _lit_grover_oracle(12, 23)),
        ("s9_lit_grover_13a", "grover_oracle", _lit_grover_oracle(13, 17)),
        ("s9_lit_grover_14a", "grover_oracle", _lit_grover_oracle(14, 19)),
        ("s9_lit_grover_14b", "grover_oracle", _lit_grover_oracle(14, 31)),
        ("s9_lit_grover_15a", "grover_oracle", _lit_grover_oracle(15, 29)),
        ("s9_lit_grover_16a", "grover_oracle", _lit_grover_oracle(16, 37)),
        ("s9_lit_grover_16b", "grover_oracle", _lit_grover_oracle(16, 41)),
    ]
    for tid, fam, circ in lit_specs:
        t = _make_s9_task(tid, "s9_hold_lit", fam, circ, seen, split="holdout")
        assert t is not None, f"S9 literature circuit {tid} failed uniqueness/min-T check!"
        suites["s9_hold_lit"].append(t)

    # 2. Procedural Holdout Strata (`s9_hold_proc_ccz` 80 + `s9_hold_proc_rand` 80 across n = 12..16!)
    q_cycle = [12, 13, 14, 15, 16]
    rng_ccz = random.Random(20261127_101)
    idx = 0
    while len(suites["s9_hold_proc_ccz"]) < 80:
        n = q_cycle[len(suites["s9_hold_proc_ccz"]) % 5]
        t = _make_s9_task(f"s9_hold_pccz_{idx:03d}_q{n}", "s9_hold_proc_ccz", "proc_ccz", _sample_s9_proc_ccz(rng_ccz, n), seen)
        idx += 1
        if t is not None:
            suites["s9_hold_proc_ccz"].append(t)

    rng_rand = random.Random(20261127_102)
    idx = 0
    while len(suites["s9_hold_proc_rand"]) < 80:
        n = q_cycle[len(suites["s9_hold_proc_rand"]) % 5]
        t = _make_s9_task(f"s9_hold_prand_{idx:03d}_q{n}", "s9_hold_proc_rand", "proc_rand", _sample_s9_proc_rand(rng_rand, n), seen)
        idx += 1
        if t is not None:
            suites["s9_hold_proc_rand"].append(t)

    # 3. Disjoint Evolution Splits (`dev_diag` 20, `val_g1..g4` 25 each)
    for sname, target_n, sseed in [
        ("dev_diag", 20, 20261127_110),
        ("val_g1", 25, 20261127_111),
        ("val_g2", 25, 20261127_112),
        ("val_g3", 25, 20261127_113),
        ("val_g4", 25, 20261127_114),
    ]:
        rng = random.Random(sseed)
        k = 0
        while len(suites[sname]) < target_n:
            pos = len(suites[sname])
            n = q_cycle[pos % 5]
            kind = pos % 3
            if kind == 0:
                circ = _lit_grover_oracle(n, (sseed % 1000) + 100 + k)
                fam = "struct_oracle"
            elif kind == 1:
                circ = _sample_s9_proc_ccz(rng, n)
                fam = "proc_ccz"
            else:
                circ = _sample_s9_proc_rand(rng, n)
                fam = "proc_rand"
            t = _make_s9_task(f"{sname}_{k:02d}_q{n}", sname, fam, circ, seen, split=sname)
            k += 1
            if t is not None:
                suites[sname].append(t)

    return suites


def s9_manifest_sha256(suites: Dict[str, List[S9Task]]) -> str:
    payload = {
        sname: [
            {
                "task_id": t.task_id,
                "n_qubits": t.n_qubits,
                "tensor_sha": t.tensor_sha,
                "base_t": t.base_t,
                "tpar_t": t.tpar_t,
                "circ_sha": t.circuit.sha256(),
            }
            for t in tasks
        ]
        for sname, tasks in sorted(suites.items())
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
