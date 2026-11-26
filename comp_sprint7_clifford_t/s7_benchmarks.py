"""Track S7-CT Fresh Sealed Benchmarks: 140-Task Fault-Tolerant Quantum Clifford+T T-Count Suite (n = 6..8 qubits).

Combines real structured quantum algorithms (Toffoli/CCZ networks, ripple-carry quantum adders,
quantum multipliers, Fredkin/CSWAP networks, Grover diffusion/oracle gadgets, QROM multiplexers)
with 100% procedural overlapping CCZ/Toffoli DAGs and 100% procedural random cubic phase polynomials!

Splits (140 tasks, ZERO duplicate cubic tensors across ALL 140 tasks!):
  - s7_train_g1 (12), s7_val_g1 (20)
  - s7_train_g2 (12), s7_val_g2 (20)
  - s7_train_g3 (12), s7_val_g3 (20)
  - UNTOUCHED HOLDOUT (44 brand-new n=6..8 qubit circuits):
      * s7_hold_struct    (18): structured quantum arithmetic/Toffoli/CCZ/Grover/Fredkin/QROM benchmarks
      * s7_hold_proc_ccz  (13): 100% procedural random overlapping CCZ/CNOT phase-polynomial circuits
      * s7_hold_proc_rand (13): 100% procedural uniform random cubic-tensor phase polynomials (Claim 4 hardness!)
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Sequence, Tuple

from comp_sprint7_clifford_t.s7_core import (
    CliffordTCircuit,
    _emit_parity_phase_gates,
    cubic_tensor_bitmask,
    extract_phase_poly,
)


@dataclass(frozen=True)
class CliffordTTask:
    task_id: str
    stratum: str
    split: str
    n_qubits: int
    circuit: CliffordTCircuit
    description: str

    def public_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "stratum": self.stratum,
            "split": self.split,
            "n_qubits": self.n_qubits,
            "gates": [list(g) for g in self.circuit.gates],
            "description": self.description,
        }

    def sha256(self) -> str:
        return hashlib.sha256(json.dumps(self.public_dict(), sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


def _ccz_gates(a: int, b: int, c: int) -> List[Tuple[Any, ...]]:
    """Standard exact 7-T-gate Clifford+T decomposition of CCZ(a, b, c) (phase = 4*x_a*x_b*x_c mod 8)."""
    return [
        ("T", a), ("T", b), ("T", c),
        ("CNOT", a, b), ("Tdg", b), ("CNOT", a, b),
        ("CNOT", a, c), ("Tdg", c), ("CNOT", a, c),
        ("CNOT", b, c), ("Tdg", c), ("CNOT", b, c),
        ("CNOT", a, b), ("CNOT", b, c), ("T", c), ("CNOT", b, c), ("CNOT", a, b),
    ]


def _build_ccz_network(n: int, triples: Sequence[Tuple[int, int, int]], pre_cnots: Sequence[Tuple[int, int]] = ()) -> CliffordTCircuit:
    gates: List[Tuple[Any, ...]] = [("CNOT", c, t) for c, t in pre_cnots]
    for a, b, c in triples:
        gates.extend(_ccz_gates(a, b, c))
    return CliffordTCircuit(n, tuple(gates))


def _build_from_cubic_triples(n: int, triples: Sequence[Tuple[int, int, int]], post_cnots: Sequence[Tuple[int, int]] = ()) -> CliffordTCircuit:
    """Build exact Clifford+T circuit implementing sum_{(i,j,k) in triples} 4*x_i*x_j*x_k (mod 8) + post CNOTs."""
    gates: List[Tuple[Any, ...]] = []
    for a, b, c in triples:
        gates.extend(_ccz_gates(a, b, c))
    for c, t in post_cnots:
        gates.append(("CNOT", c, t))
    return CliffordTCircuit(n, tuple(gates))


def _sample_proc_ccz(rng: random.Random, n: int, n_ccz: int, n_mix: int) -> CliffordTCircuit:
    gates: List[Tuple[Any, ...]] = []
    for step in range(n_ccz):
        # Interleave CNOT linear mixing with CCZ gadgets (realistic quantum circuit!)
        for _ in range(n_mix):
            c = rng.randrange(n)
            t = rng.randrange(n - 1)
            if t >= c:
                t += 1
            gates.append(("CNOT", c, t))
        a, b, c = sorted(rng.sample(range(n), 3))
        gates.extend(_ccz_gates(a, b, c))
    return CliffordTCircuit(n, tuple(gates))


def _sample_proc_rand_cubic(rng: random.Random, n: int, n_triples: int) -> CliffordTCircuit:
    all_t = [(i, j, k) for i in range(n) for j in range(i + 1, n) for k in range(j + 1, n)]
    chosen = rng.sample(all_t, min(n_triples, len(all_t)))
    return _build_from_cubic_triples(n, chosen)


def _struct_quantum_circuit(kind: str, n: int, variant: int) -> Tuple[CliffordTCircuit, str]:
    """Structured quantum benchmarks: arithmetic carry/multiplier/QROM/Grover/star/clique/ladder CCZ networks."""
    if kind == "star":
        # Shared-control Toffoli fan (e.g. QROM / controlled-adder): CCZ(hub, i, j)
        hub = variant % n
        others = [q for q in range(n) if q != hub]
        tset = set()
        for i in range(len(others)):
            tset.add(tuple(sorted((hub, others[i], others[(i + 1) % len(others)]))))
        for i in range(0, len(others), 2):
            tset.add(tuple(sorted((hub, others[i], others[(i + 2) % len(others)]))))
        # Add 2 non-hub cross-triples parametrized by variant for strict uniqueness
        tset.add(tuple(sorted((others[variant % len(others)], others[(variant + 1) % len(others)], others[(variant + 3) % len(others)]))))
        pre = [(others[variant % len(others)], hub)] if variant >= 2 else []
        return _build_ccz_network(n, sorted(tset), pre_cnots=pre), f"{n}q QROM star-CCZ v{variant}"
    if kind == "adder_carry":
        # Ripple-carry MAJ/UMA cubic terms with CNOT mixing
        gates: List[Tuple[Any, ...]] = []
        for i in range(0, n - 2):
            gates.extend(_ccz_gates(i, i + 1, i + 2))
            gates.append(("CNOT", i, i + 2))
            if i + 3 < n:
                gates.extend(_ccz_gates(i, i + 2, i + 3))
        if variant % 2 == 1:
            gates.append(("CNOT", n - 1, 0))
            gates.extend(_ccz_gates(0, 1, n - 1))
        return CliffordTCircuit(n, tuple(gates)), f"{n}q quantum adder-carry v{variant}"
    if kind == "mult_pp":
        # Quantum multiplier partial-product CCZ array: a_i * b_j * c_k
        h = n // 2
        triples = []
        for i in range(h):
            for j in range(h, n - 1):
                k = (i + j + variant) % n
                if k != i and k != j:
                    triples.append(tuple(sorted((i, j, k))))
        triples = sorted(set(triples))
        return _build_ccz_network(n, triples, pre_cnots=[(0, h), (1, n - 1)]), f"{n}q multiplier CCZ v{variant}"
    if kind == "grover_clique":
        # Dense overlapping 4-qubit multi-controlled-Z phase oracle gadgets (deduplicated + cross-links)
        tset = set()
        s0 = variant % (n - 3)
        sub = [(s0 + d) % n for d in range(4)]
        for a in range(4):
            for b in range(a + 1, 4):
                for c in range(b + 1, 4):
                    tset.add(tuple(sorted((sub[a], sub[b], sub[c]))))
        s1 = (s0 + 1 + (variant % 2)) % n
        sub2 = [(s1 + d) % n for d in range(4)]
        for a in range(4):
            for b in range(a + 1, 4):
                for c in range(b + 1, 4):
                    tset.add(tuple(sorted((sub2[a], sub2[b], sub2[c]))))
        # Add 2 cross-gadget triples coupling remaining qubits
        for d in range(2):
            q1, q2, q3 = (s0 + d) % n, (s0 + d + 2) % n, (s0 + d + 4) % n
            if len({q1, q2, q3}) == 3:
                tset.add(tuple(sorted((q1, q2, q3))))
        return _build_ccz_network(n, sorted(tset), pre_cnots=[(sub[0], sub2[-1]) if sub[0] != sub2[-1] else (0, 1)]), f"{n}q overlapping Grover-clique v{variant}"
    # kind == "fredkin_chain": CSWAP/Fredkin network with CNOT conjugation
    gates = []
    for i in range(n - 2):
        c = (i + variant) % n
        a = (i + 1 + variant) % n
        b = (i + 2 + variant) % n
        gates.append(("CNOT", b, a))
        gates.extend(_ccz_gates(c, a, b))
        gates.append(("CNOT", b, a))
    return CliffordTCircuit(n, tuple(gates)), f"{n}q Fredkin-CSWAP chain v{variant}"


def build_s7_benchmarks() -> Dict[str, List[CliffordTTask]]:
    seen_tensors = set()

    def reg(tid: str, strat: str, split: str, circ: CliffordTCircuit, desc: str) -> Optional[CliffordTTask]:
        poly, _ = extract_phase_poly(circ)
        t_par = [m for m, c in poly.items() if (c & 1) == 1]
        if len(t_par) < 10:
            return None
        key = (circ.n_qubits, cubic_tensor_bitmask(circ.n_qubits, t_par))
        if key[1] == 0 or key in seen_tensors:
            return None
        seen_tensors.add(key)
        return CliffordTTask(tid, strat, split, circ.n_qubits, circ, desc)

    def gen_struct(split: str, prefix: str, specs: Sequence[Tuple[str, int, int]]) -> List[CliffordTTask]:
        out = []
        for idx, (kind, n, var) in enumerate(specs):
            c, desc = _struct_quantum_circuit(kind, n, var)
            t = reg(f"{prefix}_{kind}_{idx:02d}_q{n}", "structured", split, c, desc)
            assert t is not None, f"Duplicate/trivial structured quantum task {prefix}_{kind}_{idx}"
            out.append(t)
        return out

    def gen_ccz(seed: int, split: str, prefix: str, count: int, widths: Sequence[int]) -> List[CliffordTTask]:
        rng = random.Random(seed)
        out, idx = [], 0
        while len(out) < count:
            n = widths[len(out) % len(widths)]
            c = _sample_proc_ccz(rng, n, n_ccz=rng.randint(5, 9), n_mix=rng.randint(1, 3))
            t = reg(f"{prefix}_{idx:02d}_q{n}", "proc_ccz", split, c, f"Random mixed CCZ network ({n}q)")
            if t is not None:
                out.append(t)
                idx += 1
        return out

    def gen_rand(seed: int, split: str, prefix: str, count: int, widths: Sequence[int]) -> List[CliffordTTask]:
        rng = random.Random(seed)
        out, idx = [], 0
        while len(out) < count:
            n = widths[len(out) % len(widths)]
            n_tr = rng.randint(6, 12) if n == 6 else rng.randint(8, 16)
            c = _sample_proc_rand_cubic(rng, n, n_tr)
            t = reg(f"{prefix}_{idx:02d}_q{n}", "proc_rand", split, c, f"Uniform random cubic tensor ({n}q, {n_tr} terms)")
            if t is not None:
                out.append(t)
                idx += 1
        return out

    tg1 = gen_struct("dev", "s7_tg1", [("star", 6, 0), ("adder_carry", 6, 0), ("mult_pp", 6, 0), ("grover_clique", 6, 0)]) + gen_ccz(2026120701, "dev", "s7_tg1_c", 4, (6, 7)) + gen_rand(2026120702, "dev", "s7_tg1_r", 4, (6, 7))
    vg1 = gen_struct("val_g1", "s7_vg1", [("star", 6, 1), ("star", 7, 0), ("adder_carry", 7, 0), ("mult_pp", 6, 1), ("mult_pp", 7, 0), ("grover_clique", 7, 0), ("fredkin_chain", 6, 0), ("fredkin_chain", 7, 0)]) + gen_ccz(2026120711, "val_g1", "s7_vg1_c", 6, (6, 7, 8)) + gen_rand(2026120712, "val_g1", "s7_vg1_r", 6, (6, 7, 8))

    tg2 = gen_struct("dev", "s7_tg2", [("star", 7, 1), ("adder_carry", 7, 1), ("mult_pp", 7, 1), ("grover_clique", 7, 1)]) + gen_ccz(2026120721, "dev", "s7_tg2_c", 4, (7, 8)) + gen_rand(2026120722, "dev", "s7_tg2_r", 4, (7, 8))
    vg2 = gen_struct("val_g2", "s7_vg2", [("star", 6, 2), ("star", 8, 0), ("adder_carry", 6, 1), ("adder_carry", 8, 0), ("mult_pp", 8, 0), ("grover_clique", 6, 1), ("grover_clique", 8, 0), ("fredkin_chain", 8, 0)]) + gen_ccz(2026120731, "val_g2", "s7_vg2_c", 6, (6, 7, 8)) + gen_rand(2026120732, "val_g2", "s7_vg2_r", 6, (6, 7, 8))

    tg3 = gen_struct("dev", "s7_tg3", [("star", 8, 1), ("adder_carry", 8, 1), ("mult_pp", 8, 1), ("grover_clique", 8, 1)]) + gen_ccz(2026120741, "dev", "s7_tg3_c", 4, (7, 8)) + gen_rand(2026120742, "dev", "s7_tg3_r", 4, (7, 8))
    vg3 = gen_struct("val_g3", "s7_vg3", [("star", 7, 2), ("star", 8, 2), ("mult_pp", 6, 2), ("mult_pp", 7, 2), ("mult_pp", 8, 2), ("grover_clique", 7, 2), ("fredkin_chain", 6, 1), ("fredkin_chain", 7, 1)]) + gen_ccz(2026120751, "val_g3", "s7_vg3_c", 6, (6, 7, 8)) + gen_rand(2026120752, "val_g3", "s7_vg3_r", 6, (6, 7, 8))

    # ==================== UNTOUCHED FINAL HOLDOUT (44 tasks: 18 struct + 13 proc_ccz + 13 proc_rand) ====================
    hold_s = gen_struct("holdout", "s7_hold", [
        ("star", 6, 3), ("star", 7, 3), ("star", 8, 3), ("star", 8, 4),
        ("mult_pp", 6, 3), ("mult_pp", 7, 3), ("mult_pp", 8, 3), ("mult_pp", 8, 4),
        ("grover_clique", 6, 2), ("grover_clique", 7, 3), ("grover_clique", 8, 2), ("grover_clique", 8, 3), ("grover_clique", 8, 4),
        ("fredkin_chain", 6, 2), ("fredkin_chain", 7, 2), ("fredkin_chain", 8, 1), ("fredkin_chain", 8, 2), ("fredkin_chain", 8, 3),
    ])
    hold_c = gen_ccz(2026120791, "holdout", "s7_hold_c", 13, (6, 7, 8))
    hold_r = gen_rand(2026120793, "holdout", "s7_hold_r", 13, (6, 7, 8))

    suites = {
        "s7_train_g1": tg1, "s7_val_g1": vg1,
        "s7_train_g2": tg2, "s7_val_g2": vg2,
        "s7_train_g3": tg3, "s7_val_g3": vg3,
        "s7_hold_struct": hold_s,
        "s7_hold_proc_ccz": hold_c,
        "s7_hold_proc_rand": hold_r,
    }
    assert sum(len(v) for v in suites.values()) == 140
    return suites


def s7_manifest_sha256(suites: Dict[str, List[CliffordTTask]]) -> str:
    payload = {k: [t.public_dict() for t in v] for k, v in sorted(suites.items())}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
