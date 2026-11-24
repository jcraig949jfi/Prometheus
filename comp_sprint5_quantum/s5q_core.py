"""Track S5-Q Core IR, Exact Verifier, Published Patel-Markov-Hayes (PMH 2008) Baseline & Law-4 Metered Engine.

Formal Substrate #3: Exact Linear Reversible / Quantum CNOT Circuit Synthesis over GL(n, F_2) (n = 12..18 qubits).
  - Target: invertible binary n x n matrix `target_rows: Tuple[int, ...]` (bit c of row r is M[r, c]).
  - Primitive gate: `CNOT(ctrl, targ)` applies `row[targ] ^= row[ctrl]` (exact elementary matrix E_{targ, ctrl}).
  - Cost: exact primitive CNOT count `len(gates)` (ZERO discount!).
  - Exact Verifier: applies `gates` to I_n and checks `tuple(rows) == target_rows` (~2 us, 0.000 jitter).
  - Industry Baseline (`A1_PMH`): Published Patel-Markov-Hayes (2008) O(n^2 / log n) block-Gaussian compiler!
  - Metering: ALL FOUR LAWS native from Line 1 via `run_compositional_word_metered` (`OpBudget v2`).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from comp_sprint3.sandbox_s3 import CompositionalAlgoArtifact, LibModule, OpBudget
from comp_sprint4.law4_meter import run_compositional_word_metered


DEFAULT_S5Q_WORD_BUDGET = 140_000


@dataclass(frozen=True)
class CNOTCircuit:
    """Immutable exact linear reversible quantum CNOT circuit over n qubits."""
    n_qubits: int
    gates: Tuple[Tuple[int, int], ...]  # (ctrl, targ) applying row[targ] ^= row[ctrl]

    def gate_count(self) -> int:
        return len(self.gates)

    def sha256(self) -> str:
        payload = {"n_qubits": self.n_qubits, "gates": [list(g) for g in self.gates]}
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()

    def matrix_rows(self) -> Tuple[int, ...]:
        rows = [1 << i for i in range(self.n_qubits)]
        for c, t in self.gates:
            rows[t] ^= rows[c]
        return tuple(rows)


def apply_cnot_seq(n_qubits: int, gates: Sequence[Tuple[int, int]], init_rows: Optional[Sequence[int]] = None) -> Tuple[int, ...]:
    rows = [1 << i for i in range(n_qubits)] if init_rows is None else list(init_rows)
    for c, t in gates:
        rows[t] ^= rows[c]
    return tuple(rows)


def verify_cnot_circuit(target_rows: Sequence[int], circ: CNOTCircuit) -> bool:
    if not isinstance(circ, CNOTCircuit) or circ.n_qubits != len(target_rows):
        return False
    n = circ.n_qubits
    rows = [1 << i for i in range(n)]
    for g in circ.gates:
        if not isinstance(g, tuple) or len(g) != 2:
            return False
        c, t = g
        if not (0 <= c < n and 0 <= t < n and c != t):
            return False
        rows[t] ^= rows[c]
    return tuple(rows) == tuple(target_rows)


def is_invertible_gf2(rows: Sequence[int]) -> bool:
    n = len(rows)
    r = list(rows)
    for col in range(n):
        bit = 1 << col
        piv = -1
        for i in range(col, n):
            if r[i] & bit:
                piv = i
                break
        if piv < 0:
            return False
        if piv != col:
            r[col], r[piv] = r[piv], r[col]
        for i in range(col + 1, n):
            if r[i] & bit:
                r[i] ^= r[col]
    return True


def invert_gf2(rows: Sequence[int]) -> Tuple[int, ...]:
    """Exact GF(2) matrix inverse via Gauss-Jordan."""
    n = len(rows)
    a = list(rows)
    inv = [1 << i for i in range(n)]
    for col in range(n):
        bit = 1 << col
        piv = next(i for i in range(col, n) if a[i] & bit)
        if piv != col:
            a[col], a[piv] = a[piv], a[col]
            inv[col], inv[piv] = inv[piv], inv[col]
        for i in range(n):
            if i != col and (a[i] & bit):
                a[i] ^= a[col]
                inv[i] ^= inv[col]
    return tuple(inv)


def _reduce_to_identity_gauss(rows: Sequence[int]) -> List[Tuple[int, int]]:
    """Standard Gauss-Jordan elimination returning reduction ops (reverse them to synthesize `rows` from I_n!)."""
    n = len(rows)
    a = list(rows)
    ops: List[Tuple[int, int]] = []
    # Forward elimination to upper triangular (with diagonal 1s)
    for col in range(n):
        bit = 1 << col
        if not (a[col] & bit):
            piv = next(i for i in range(col + 1, n) if a[i] & bit)
            a[col] ^= a[piv]
            ops.append((piv, col))
        for i in range(col + 1, n):
            if a[i] & bit:
                a[i] ^= a[col]
                ops.append((col, i))
    # Backward elimination to identity
    for col in range(n - 1, -1, -1):
        bit = 1 << col
        for i in range(col - 1, -1, -1):
            if a[i] & bit:
                a[i] ^= a[col]
                ops.append((col, i))
    return ops


def gauss_elim_cnot(target_rows: Sequence[int]) -> CNOTCircuit:
    """Arm A0_BASE: standard Gauss-Jordan CNOT synthesizer."""
    ops = _reduce_to_identity_gauss(target_rows)
    circ = CNOTCircuit(len(target_rows), tuple(reversed(ops)))
    assert verify_cnot_circuit(target_rows, circ)
    return circ


def _pmh_lower_pass(a: List[int], m: int, ops: List[Tuple[int, int]]) -> None:
    """Patel-Markov-Hayes (2008) section-wise lower-triangular elimination with block size `m`."""
    n = len(a)
    for sec_start in range(0, n, m):
        sec_end = min(n, sec_start + m)
        sec_mask = ((1 << (sec_end - sec_start)) - 1) << sec_start
        # Step A: Eliminate duplicate non-zero sub-rows in this section (rows sec_start..n-1)
        patt: Dict[int, int] = {}
        for r in range(sec_start, n):
            sub = a[r] & sec_mask
            if sub == 0:
                continue
            if sub in patt:
                src = patt[sub]
                a[r] ^= a[src]
                ops.append((src, r))
            else:
                patt[sub] = r
        # Step B: Standard pivot elimination within columns sec_start..sec_end-1
        for col in range(sec_start, sec_end):
            bit = 1 << col
            if not (a[col] & bit):
                piv = next(i for i in range(col + 1, n) if a[i] & bit)
                a[col] ^= a[piv]
                ops.append((piv, col))
            for r in range(col + 1, n):
                if a[r] & bit:
                    a[r] ^= a[col]
                    ops.append((col, r))


def _transpose_gf2(rows: Sequence[int]) -> List[int]:
    n = len(rows)
    tr = [0] * n
    for r in range(n):
        v = rows[r]
        while v:
            lsb = v & -v
            c = lsb.bit_length() - 1
            tr[c] |= (1 << r)
            v ^= lsb
    return tr


def pmh_cnot_synth(target_rows: Sequence[int], block_sizes: Sequence[int] = (2, 3, 4)) -> CNOTCircuit:
    """Arm A1_PMH: Published Patel-Markov-Hayes (2008) O(n^2 / log n) quantum CNOT compiler!

    Runs PMH forward pass (lower-triangular) -> transpose -> PMH pass (upper-triangular)
    across block sizes `m in {2, 3, 4}` (and both M and M^-1^T) taking the shortest exact circuit.
    """
    n = len(target_rows)
    best: Optional[CNOTCircuit] = None

    def _run_pmh_once(rows: Sequence[int], m: int) -> CNOTCircuit:
        a = list(rows)
        ops1: List[Tuple[int, int]] = []
        _pmh_lower_pass(a, m, ops1)
        # Now `a` is upper-triangular with 1s on diagonal; transpose -> lower-triangular!
        at = _transpose_gf2(a)
        ops2: List[Tuple[int, int]] = []
        _pmh_lower_pass(at, m, ops2)
        # Transpose of E_{t,c} is E_{c,t} applied in reverse!
        # Since E_k ... E_1 * M = U and F_r ... F_1 * U^T = I => U = (F_1^T ... F_r^T)
        # So M = E_1 ... E_k * F_1^T ... F_r^T
        # Wait: verify cleanly: applying (c, t) in reversed(ops1) transforms U -> M,
        # and applying (t, c) in ops2 transforms I -> U!
        gates = tuple((t, c) for c, t in ops2) + tuple(reversed(ops1))
        return CNOTCircuit(n, gates)

    for m in block_sizes:
        cand = _run_pmh_once(target_rows, m)
        if verify_cnot_circuit(target_rows, cand):
            if best is None or cand.gate_count() < best.gate_count():
                best = cand
    # Also try reducing M^{-1} (reversed reduction ops of M^{-1} build M^{-1}, so forward ops build M!)
    inv_rows = invert_gf2(target_rows)
    for m in block_sizes:
        c_inv = _run_pmh_once(inv_rows, m)
        cand = CNOTCircuit(n, tuple(reversed(c_inv.gates)))
        if verify_cnot_circuit(target_rows, cand):
            if best is None or cand.gate_count() < best.gate_count():
                best = cand

    assert best is not None and verify_cnot_circuit(target_rows, best)
    return best


def make_metered_cnot_api_factory(
    target_rows: Tuple[int, ...],
) -> Callable[[OpBudget, Callable[[Any], bool]], Dict[str, Any]]:
    n = len(target_rows)

    def factory(budget: OpBudget, _report_best: Callable[[Any], bool]) -> Dict[str, Any]:
        def m_make_circ(gates: Sequence[Tuple[int, int]]) -> CNOTCircuit:
            budget.charge(max(2, len(gates)))
            return CNOTCircuit(n, tuple((int(c), int(t)) for c, t in gates))

        def m_apply(gates: Sequence[Tuple[int, int]], init_rows: Optional[Sequence[int]] = None) -> Tuple[int, ...]:
            budget.charge(max(2, len(gates)))
            return apply_cnot_seq(n, gates, init_rows)

        def m_verify(circ: CNOTCircuit) -> bool:
            budget.charge(max(4, len(circ.gates)))
            return verify_cnot_circuit(target_rows, circ)

        def m_gauss(rows: Sequence[int]) -> CNOTCircuit:
            budget.charge(n * n)
            return gauss_elim_cnot(rows)

        def m_pmh(rows: Sequence[int], m: int = 3) -> CNOTCircuit:
            budget.charge(n * n)
            return pmh_cnot_synth(rows, block_sizes=(max(2, min(5, int(m))),))

        def m_invert(rows: Sequence[int]) -> Tuple[int, ...]:
            budget.charge(n * n)
            return invert_gf2(rows)

        def m_transpose(rows: Sequence[int]) -> Tuple[int, ...]:
            budget.charge(n * 2)
            return tuple(_transpose_gf2(rows))

        def m_features(rows: Sequence[int]) -> Dict[str, Any]:
            budget.charge(n)
            hw = sum(int(r).bit_count() for r in rows)
            diag = sum(1 for i, r in enumerate(rows) if (r >> i) & 1)
            return {
                "n_qubits": len(rows),
                "hamming_weight": hw,
                "density": round(hw / max(1, len(rows) * len(rows)), 4),
                "diag_ones": diag,
            }

        return {
            "CNOTCircuit": CNOTCircuit,
            "make_circuit": m_make_circ,
            "apply_cnot_seq": m_apply,
            "verify_cnot_circuit": m_verify,
            "gauss_synth": m_gauss,
            "pmh_synth": m_pmh,
            "invert_gf2": m_invert,
            "transpose_gf2": m_transpose,
            "matrix_features": m_features,
        }

    return factory


# ---------------- Deterministic Baselines: A3_ZERO_LLM & A5_SHAM ----------------

_S5Q_A3_MOD = """
def greedy_hw_reduce(target_rows, seed):
    n = len(target_rows)
    a = list(target_rows)
    ops = []
    # Greedy Hamming-weight descent (steepest single-CNOT drop while preserving non-zero rows)
    while budget.remaining() > 500 and len(ops) < 3 * n * n:
        cur_hw = sum(r.bit_count() for r in a)
        if cur_hw == n and all(a[i] == (1 << i) for i in range(n)):
            break
        best_mv = None
        best_gain = 0
        for c in range(n):
            rc = a[c]
            for t in range(n):
                if c == t:
                    continue
                nw = (a[t] ^ rc).bit_count()
                gain = a[t].bit_count() - nw
                if gain > best_gain:
                    best_gain = gain
                    best_mv = (c, t)
        if best_mv is None:
            break
        c, t = best_mv
        a[t] ^= a[c]
        ops.append((c, t))
    # Finish residual matrix with exact Gauss elimination
    tail = gauss_synth(a)
    full = make_circuit(list(tail.gates) + list(reversed(ops)))
    report_best(full)
    return best_solution()
"""

_S5Q_A3_ORCH = """
def solve(circ, target_rows, seed, api, lib, budget):
    return lib.greedy_hw_reduce(target_rows, seed)
"""

_S5Q_A5_MOD = """
def sham_perm_pmh(target_rows, seed):
    rng = random.Random(seed * 10007 + 55555)
    n = len(target_rows)
    base = list(range(n))
    # Random qubit-permutation restarts of Gauss & PMH burning the EXACT same word budget!
    while budget.remaining() > n * n + 200:
        perm = list(base)
        rng.shuffle(perm)
        inv_p = [0] * n
        for i, p in enumerate(perm):
            inv_p[p] = i
        # Permuted matrix P M P^T
        pm = [0] * n
        for r in range(n):
            v = target_rows[perm[r]]
            nv = 0
            for c in range(n):
                if (v >> perm[c]) & 1:
                    nv |= (1 << c)
            pm[r] = nv
        sub = pmh_synth(pm, m=rng.choice((2, 3, 4)))
        mapped = [(perm[c], perm[t]) for c, t in sub.gates]
        report_best(make_circuit(mapped))
    return best_solution()
"""

_S5Q_A5_ORCH = """
def solve(circ, target_rows, seed, api, lib, budget):
    return lib.sham_perm_pmh(target_rows, seed)
"""


def build_s5q_a3_artifact() -> CompositionalAlgoArtifact:
    m = LibModule.from_source("s5q_a3_greedy", 0, _S5Q_A3_MOD, origin="zero_llm_baseline")
    o = LibModule.from_source("s5q_a3_orch", 0, _S5Q_A3_ORCH, required_fn="solve", origin="zero_llm_baseline")
    return CompositionalAlgoArtifact("A3_ZERO_LLM", "S5Q_CNOT_COMP", 0, (m,), o)


def build_s5q_a5_sham_artifact() -> CompositionalAlgoArtifact:
    m = LibModule.from_source("s5q_a5_sham", 0, _S5Q_A5_MOD, origin="sham_matched_compute")
    o = LibModule.from_source("s5q_a5_orch", 0, _S5Q_A5_ORCH, required_fn="solve", origin="sham_matched_compute")
    return CompositionalAlgoArtifact("A5_SHAM", "S5Q_CNOT_COMP", 0, (m,), o)


def synthesize_s5q_with_artifact(
    target_rows: Sequence[int],
    artifact: Optional[CompositionalAlgoArtifact],
    seed: int = 0,
    word_budget: int = DEFAULT_S5Q_WORD_BUDGET,
    fallback_artifact: Optional[CompositionalAlgoArtifact] = None,
) -> Tuple[CNOTCircuit, Dict[str, Any]]:
    """Unified 100%-deterministic Law-4-metered Track S5-Q evaluator."""
    t_rows = tuple(int(r) for r in target_rows)
    base = gauss_elim_cnot(t_rows)
    if artifact is None:
        return base, {
            "final_cost": base.gate_count(),
            "ops_spent": 0,
            "ops_limit": word_budget,
            "status": "base_only",
            "module_calls": {},
            "cross_gen_calls": {},
            "gen_gate_drops": {},
            "mod_gate_drops": {},
            "fn_errors": {},
            "fn_error_msgs": {},
        }

    api_factory = make_metered_cnot_api_factory(t_rows)
    verify_fn = lambda c: verify_cnot_circuit(t_rows, c)
    cost_fn = lambda c: int(c.gate_count())
    call_args_fn = lambda cur, api, lib, bud: (cur, t_rows, seed, api, lib, bud)

    best, meta1 = run_compositional_word_metered(
        initial_solution=base,
        artifact=artifact,
        domain_api_factory=api_factory,
        call_args_fn=call_args_fn,
        verify_fn=verify_fn,
        cost_fn=cost_fn,
        word_budget=word_budget,
    )
    if fallback_artifact is not None:
        rem = word_budget - int(meta1.get("ops_spent", 0))
        if rem >= 2500:
            best2, meta2 = run_compositional_word_metered(
                initial_solution=best,
                artifact=fallback_artifact,
                domain_api_factory=api_factory,
                call_args_fn=call_args_fn,
                verify_fn=verify_fn,
                cost_fn=cost_fn,
                word_budget=rem,
            )
            if cost_fn(best2) < cost_fn(best) and verify_fn(best2):
                best = best2
            meta1["ops_spent"] = min(word_budget, int(meta1.get("ops_spent", 0)) + int(meta2.get("ops_spent", 0)))
            meta1["final_cost"] = cost_fn(best)
    assert verify_cnot_circuit(t_rows, best)
    return best, meta1
