"""Sprint 9 Core: Polynomial-Time Exact Quantum `Clifford+T` Verification & Clifford Completion (`n = 6..20+` Qubits).

Exact Algebraic Identity over Z/8Z (Proof for ALL n >= 1, ALL x in {0, 1}^n):
    (y . x) = sum_{r=1}^{k} (-2)^{r-1} C(k, r)
            == sum_i y_i x_i  -  2 sum_{i<j} y_i y_j x_i x_j  +  4 sum_{i<j<k} y_i y_j y_k x_i x_j x_k  (mod 8)
  because for r >= 4, (-2)^{r-1} = (-8)*(-2)^{r-4} == 0 (mod 8)!

Consequences (Zero O(2^n) Simulation Required!):
  1. `phase_poly_z8_signature(n, poly)` computes the EXACT polynomial representation `(L_mod8, Q_mod8, T_mod2)`
     in O(m * n^3) time — 100% mathematically equivalent to exhaustive 2^n state-vector phase equality up to
     global phase! (Cross-verified identically against 2^n simulation for n <= 12 in unit tests.)
  2. `synthesize_poly_clifford_t(n, target_poly, final_mat, t_parities)` constructs the EXACT zero-T Clifford
     `{CNOT, S, Sdg, Z}` completion circuit in O(m * n^2) polynomial time for ANY `n`!
  3. Scale-adaptive Law 4b+4c budget `s9_budget_for_n(n) = 35_000 * C(n, 2)` keeps exact compute-proportional
     parity as `n` scales from 12 to 16+ qubits (`C(12,2)=66 -> 2.31M`, `C(16,2)=120 -> 4.20M`).
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from comp_sprint3.sandbox_s3 import CompositionalAlgoArtifact, OpBudget
from comp_sprint6_compound.law4b_meter import run_compositional_law4b
from comp_sprint7_clifford_t.s7_core import (
    CliffordTCircuit,
    _emit_parity_phase_gates,
    extract_phase_poly,
)
from comp_sprint8_science.s8_core import (
    _reduce_parities_xor,
    apply_todd_shift,
    build_chi_z_columns,
    nullspace_gf2_columns,
    odd_t_parities,
)


def s9_budget_for_n(n_qubits: int) -> int:
    """Scale-adaptive Law 4b+4c budget proportional to `C(n, 2)` (`2.31M` at n=12, `4.20M` at n=16)."""
    return 35_000 * (n_qubits * (n_qubits - 1) // 2)


def fast_lin_quad_cubic_parity(n_qubits: int, parities: Sequence[int]) -> Tuple[int, int, int]:
    """Compute exact `(L_mod2, Q_mod2, T_mod2)` bitmasks in O(m * wt^3) — FAST even for n = 16..20!"""
    # Extract set bit indices per parity (typically weight 1..6!) instead of looping C(n,3) over every parity!
    lin = 0
    quad_bits: Dict[Tuple[int, int], int] = {}
    cub_bits: Dict[Tuple[int, int, int], int] = {}
    for y in parities:
        if not y:
            continue
        lin ^= y
        bits: List[int] = []
        t = y
        while t:
            lb = t & -t
            bits.append(lb.bit_length() - 1)
            t ^= lb
        L = len(bits)
        for i in range(L):
            bi = bits[i]
            for j in range(i + 1, L):
                bj = bits[j]
                pk = (bi, bj)
                quad_bits[pk] = quad_bits.get(pk, 0) ^ 1
                for k in range(j + 1, L):
                    tk = (bi, bj, bits[k])
                    cub_bits[tk] = cub_bits.get(tk, 0) ^ 1
    qmask = 0
    for (i, j), v in quad_bits.items():
        if v:
            # Canonical index for pair (i, j)
            qmask |= 1 << (i * n_qubits + j)
    cmask = 0
    for (i, j, k), v in cub_bits.items():
        if v:
            cmask |= 1 << ((i * n_qubits + j) * n_qubits + k)
    return lin, qmask, cmask


def phase_poly_z8_signature(
    n_qubits: int, poly: Dict[int, int]
) -> Tuple[Tuple[int, ...], Tuple[Tuple[int, int, int], ...], Tuple[Tuple[int, int, int], ...]]:
    """Exact polynomial Z/8Z signature `(L_mod8, sparse Q_mod8, sparse T_mod2)` of `sum c_y (y.x) mod 8`.
    100% mathematically equivalent to exhaustive `2^n` phase equality (up to global phase) for ALL `n`!"""
    L = [0] * n_qubits
    Q: Dict[Tuple[int, int], int] = {}
    T: Dict[Tuple[int, int, int], int] = {}
    for y, coeff in poly.items():
        c = coeff & 7
        if c == 0 or y == 0:
            continue
        bits: List[int] = []
        t = y
        while t:
            lb = t & -t
            bits.append(lb.bit_length() - 1)
            t ^= lb
        ln = len(bits)
        c_quad = (-2 * c) & 7
        c_cub = (4 * c) & 7  # 4 if c odd, 0 if c even
        for i in range(ln):
            bi = bits[i]
            L[bi] = (L[bi] + c) & 7
            for j in range(i + 1, ln):
                bj = bits[j]
                pk = (bi, bj)
                Q[pk] = (Q.get(pk, 0) + c_quad) & 7
                if c_cub:
                    for k in range(j + 1, ln):
                        tk = (bi, bj, bits[k])
                        T[tk] = T.get(tk, 0) ^ 1
    q_sparse = tuple(sorted((i, j, v) for (i, j), v in Q.items() if v != 0))
    t_sparse = tuple(sorted(k for k, v in T.items() if v != 0))
    return tuple(L), q_sparse, t_sparse


def verify_poly_exact(
    target_poly: Dict[int, int],
    target_mat: Tuple[int, ...],
    cand: CliffordTCircuit,
) -> bool:
    """100% exact polynomial-time quantum unitary verification (valid for ANY `n` qubits!)."""
    if not isinstance(cand, CliffordTCircuit) or cand.n_qubits != len(target_mat):
        return False
    n = cand.n_qubits
    for g in cand.gates:
        if not isinstance(g, tuple) or len(g) < 2:
            return False
        if g[0] == "CNOT":
            if len(g) != 3 or not (0 <= g[1] < n and 0 <= g[2] < n and g[1] != g[2]):
                return False
        elif g[0] in ("T", "Tdg", "S", "Sdg", "Z"):
            if len(g) != 2 or not (0 <= g[1] < n):
                return False
        else:
            return False
    c_poly, c_mat = extract_phase_poly(cand)
    if c_mat != target_mat:
        return False
    return phase_poly_z8_signature(n, c_poly) == phase_poly_z8_signature(n, target_poly)


def synthesize_poly_clifford_t(
    n_qubits: int,
    target_poly: Dict[int, int],
    final_mat: Sequence[int],
    t_parities: Sequence[int],
) -> Optional[CliffordTCircuit]:
    """Exact polynomial-time `O(m * n^2)` zero-T Clifford completion for ANY `n` qubits!
    Given `t_parities` matching target `(L mod 2, Q mod 2, T mod 2)`, solves for exact
    Clifford `{S, Sdg, Z, CZ}` residual in Z/8Z without touching 2^n states."""
    clean_t = _reduce_parities_xor(t_parities)
    # Build difference poly: target_poly - sum_{y in clean_t} 1 * (y . x) (mod 8)
    diff: Dict[int, int] = dict(target_poly)
    for y in clean_t:
        diff[y] = (diff.get(y, 0) - 1) & 7
    L, Q_sparse, T_sparse = phase_poly_z8_signature(n_qubits, diff)
    # Exact Clifford-completability check: T must vanish, all L must be even, all Q must be 0 or 4 (mod 8)!
    if T_sparse:
        return None
    if any(v & 1 for v in L):
        return None
    out_poly: Dict[int, int] = {y: 1 for y in clean_t}
    for i, lv in enumerate(L):
        if lv:
            out_poly[1 << i] = (out_poly.get(1 << i, 0) + lv) & 7
    for i, j, qv in Q_sparse:
        if qv not in (0, 4):
            return None
        if qv == 4:
            # Exact identity: 4 * x_i * x_j == 2*x_i + 2*x_j + 6*(x_i ^ x_j) (mod 8) -> pure S/Sdg (0 T-gates!)
            out_poly[1 << i] = (out_poly.get(1 << i, 0) + 2) & 7
            out_poly[1 << j] = (out_poly.get(1 << j, 0) + 2) & 7
            ij = (1 << i) | (1 << j)
            out_poly[ij] = (out_poly.get(ij, 0) + 6) & 7
    out_poly = {m: c for m, c in out_poly.items() if m and (c & 7)}
    return _emit_parity_phase_gates(n_qubits, out_poly, final_mat)


# ---------------------------------------------------------------------------
# Polynomial-Time Published Baselines (`n = 12..18+` Qubits!)
# ---------------------------------------------------------------------------
def tpar_poly_optimize(circ: CliffordTCircuit) -> CliffordTCircuit:
    """Published Amy-Maslov-Mosca-Roetteler (2014) T-par phase-polynomial folding (polynomial time!)."""
    poly, final_mat = extract_phase_poly(circ)
    return _emit_parity_phase_gates(circ.n_qubits, poly, final_mat)


def todd_2018_poly_optimize(circ: CliffordTCircuit, max_passes: int = 250) -> CliffordTCircuit:
    """Published Heyfron-Campbell (2018) TODD baseline (polynomial completion, works for any `n`)."""
    n = circ.n_qubits
    poly, final_mat = extract_phase_poly(circ)
    P = odd_t_parities(poly)
    for _ in range(max_passes):
        m = len(P)
        improved = False
        seen_z = set()
        for i in range(m):
            ai = P[i]
            for j in range(i + 1, m):
                z = ai ^ P[j]
                if z == 0 or z in seen_z:
                    continue
                seen_z.add(z)
                cols = build_chi_z_columns(n, P, z)
                nl = nullspace_gf2_columns(cols)
                for yv in nl:
                    if (((yv >> i) ^ (yv >> j)) & 1) == 1:
                        Q = apply_todd_shift(P, yv, z)
                        if len(Q) < m:
                            P = Q
                            improved = True
                            break
                if improved:
                    break
            if improved:
                break
        if not improved:
            break
    out = synthesize_poly_clifford_t(n, poly, final_mat, P)
    return out if out is not None else tpar_poly_optimize(circ)


def fast_todd_2022_poly_optimize(circ: CliffordTCircuit, max_passes: int = 350) -> CliffordTCircuit:
    """Published Vandaele-Martiel-de Brugiere (2022) FastTODD baseline (polynomial completion, any `n`)."""
    n = circ.n_qubits
    poly, final_mat = extract_phase_poly(circ)
    P = odd_t_parities(poly)
    for _ in range(max_passes):
        m = len(P)
        if m <= 1:
            break
        counts: Dict[int, int] = {}
        for i in range(m):
            ai = P[i]
            counts[ai] = counts.get(ai, 0) + 1
            for j in range(i + 1, m):
                z = ai ^ P[j]
                if z:
                    counts[z] = counts.get(z, 0) + 1
        cand_z = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        best_Q: Optional[List[int]] = None
        best_gain = 0
        for z, mult in cand_z:
            if 2 * mult + 2 <= best_gain:
                break
            cols = build_chi_z_columns(n, P, z)
            nl = nullspace_gf2_columns(cols)
            if not nl:
                continue
            cands = list(nl)
            lim_b = min(len(nl), 4)
            for a_idx in range(lim_b):
                for b_idx in range(a_idx + 1, lim_b):
                    cands.append(nl[a_idx] ^ nl[b_idx])
            for yv in cands:
                Q = apply_todd_shift(P, yv, z)
                gain = m - len(Q)
                if gain > best_gain:
                    best_gain = gain
                    best_Q = Q
        if best_Q is None:
            break
        P = best_Q
    out = synthesize_poly_clifford_t(n, poly, final_mat, P)
    return out if out is not None else tpar_poly_optimize(circ)


# ---------------------------------------------------------------------------
# Scale-Adaptive Law 4b+4c Metered Runtime (`n = 12..18+` Qubits, Zero O(2^n)!)
# ---------------------------------------------------------------------------
def run_s9_artifact(
    artifact: CompositionalAlgoArtifact,
    circ: CliffordTCircuit,
    *,
    seed: int = 0,
    v3_budget: Optional[int] = None,
) -> Tuple[CliffordTCircuit, Dict[str, Any]]:
    """Run an evolved compositional artifact at `n = 12..18+` under scale-adaptive Law 4b+4c metering
    and 100% exact polynomial `O(m * n^3)` algebraic verification!"""
    n = circ.n_qubits
    eff_budget = s9_budget_for_n(n) if v3_budget is None else int(v3_budget)
    poly, final_mat = extract_phase_poly(circ)
    init_parities = odd_t_parities(poly)
    target_lqt = fast_lin_quad_cubic_parity(n, init_parities)

    def _verify_parities(cand: Any) -> bool:
        if not isinstance(cand, (list, tuple)):
            return False
        red = _reduce_parities_xor([int(x) for x in cand if isinstance(x, int)])
        return fast_lin_quad_cubic_parity(n, red) == target_lqt

    def _cost_parities(cand: Any) -> int:
        if not isinstance(cand, (list, tuple)):
            return 10**9
        return len(_reduce_parities_xor([int(x) for x in cand if isinstance(x, int)]))

    def _domain_api_factory(budget: OpBudget, report_best: Callable[[Any], bool]) -> Dict[str, Any]:
        c_n2 = max(1, n * (n - 1) // 2)
        words = max(1, (c_n2 + 63) // 64)

        def api_reduce(P: Sequence[int]) -> List[int]:
            budget.charge(3 * len(P) + 4)
            return _reduce_parities_xor(P)

        def api_chi_z_cols(P: Sequence[int], z: int) -> List[int]:
            # Law 4c: exact compute-proportional O(m * C(n, 2)) charge
            budget.charge(len(P) * (c_n2 + 4) + 12)
            if not z or z < 0 or z >= (1 << n):
                return []
            return build_chi_z_columns(n, P, int(z))

        def api_nullspace(cols: Sequence[int]) -> List[int]:
            # Law 4c: exact compute-proportional O(m * C(n, 2) * words) charge
            budget.charge(len(cols) * (c_n2 + 8 * words) + 16)
            return nullspace_gf2_columns(cols)

        def api_apply_shift(P: Sequence[int], y_mask: int, z: int) -> List[int]:
            budget.charge(4 * len(P) + 8)
            if not z or z < 0 or z >= (1 << n):
                return _reduce_parities_xor(P)
            return apply_todd_shift(P, int(y_mask), int(z))

        def api_submit(P: Sequence[int], tag: str = "algo") -> bool:
            budget.charge(4 * len(P) + 16)
            return report_best(_reduce_parities_xor(P))

        return {
            "n_qubits": n,
            "init_parities": list(init_parities),
            "seed": seed,
            "v3_budget": eff_budget,
            "reduce_parities": api_reduce,
            "chi_z_cols": api_chi_z_cols,
            "nullspace_gf2": api_nullspace,
            "apply_shift": api_apply_shift,
            "submit_best": api_submit,
            "rem_budget": lambda: max(0, budget.limit - budget.spent),
        }

    best_raw, tel = run_compositional_law4b(
        initial_solution=list(init_parities),
        artifact=artifact,
        domain_api_factory=_domain_api_factory,
        call_args_fn=lambda init_sol, api, lib, budget: (api, lib, budget),
        verify_fn=_verify_parities,
        cost_fn=_cost_parities,
        v3_budget=eff_budget,
    )
    best_parities = _reduce_parities_xor(best_raw)

    cand_circ = synthesize_poly_clifford_t(n, poly, final_mat, best_parities)
    if cand_circ is None or not verify_poly_exact(poly, final_mat, cand_circ):
        cand_circ = tpar_poly_optimize(circ)
        tel["verifier_fallback"] = True
    else:
        tel["verifier_fallback"] = False
    return cand_circ, tel
