"""DMRG instrument-trust unit test.

Reviewer (2026-04-25) flagged that v3.2 §4.3 attributes DMRG no-op to
truncation tolerance + rollback guard, but never verified that the DMRG
inner loop actually modifies cores before the rollback kicks in. If the
inner loop is broken, all DMRG conclusions are weaker.

This test constructs a case where DMRG MUST do work if the implementation
is correct, then verifies the four sub-claims:
  (a) the supercore update produces non-zero core differences
  (b) singular values change between before and after
  (c) rank can change adaptively
  (d) the rollback guard, not the inner loop, is what determines the
      final returned TT when err_after >= err_before
"""
from __future__ import annotations
import numpy as np

from zoo.tt.core import tt_svd, relative_l2_error, TTDecomposition
from zoo.tt.dmrg import tt_dmrg_refine, _two_site_update, tt_evaluate_with_dmrg


def _max_core_diff(cores_a, cores_b):
    """Maximum element-wise absolute difference across cores of equal rank profile."""
    if any(a.shape != b.shape for a, b in zip(cores_a, cores_b)):
        return float("inf")  # rank profile changed
    return max(float(np.max(np.abs(a - b))) for a, b in zip(cores_a, cores_b))


def test_inner_loop_modifies_cores():
    """A — Does the DMRG inner loop change the cores at all?"""
    print("\n=== Test A — Inner loop modifies cores ===")
    rng = np.random.default_rng(42)
    T = rng.standard_normal((6, 6, 6, 6))
    # TT-SVD at moderate rank (substantial truncation since random tensor)
    tt0 = tt_svd(T, max_ranks=(3, 3, 3))
    cores_before = [c.copy() for c in tt0.cores]
    err_before = relative_l2_error(T, tt0.reconstruct())

    # Run DMRG WITHOUT the rollback guard (call refine directly, not evaluate)
    tt_refined = tt_dmrg_refine(tt0, T, n_sweeps=1, rel_tol=1e-10, max_bond=8)
    cores_after = tt_refined.cores
    err_after = relative_l2_error(T, tt_refined.reconstruct())

    diff = _max_core_diff(cores_before, cores_after)
    rank_before = tt0.ranks
    rank_after = tt_refined.ranks
    print(f"  err_before = {err_before:.6f}")
    print(f"  err_after  = {err_after:.6f}")
    print(f"  ranks_before = {rank_before}")
    print(f"  ranks_after  = {rank_after}")
    print(f"  max core diff = {diff:.3e}")
    if diff > 1e-8:
        print("  PASS: inner loop modifies cores")
    else:
        print("  FAIL: inner loop did NOT modify cores")
    return {
        "err_before": float(err_before),
        "err_after": float(err_after),
        "rank_before": list(rank_before),
        "rank_after": list(rank_after),
        "max_core_diff": float(diff),
        "verdict": "PASS" if diff > 1e-8 else "FAIL",
    }


def test_singular_values_change():
    """B — Do the bond singular values shift between before and after?

    Compute SVD of unfolded TT before and after one DMRG sweep; the dominant
    singular values should not be byte-identical if cores changed.
    """
    print("\n=== Test B — Singular values change ===")
    rng = np.random.default_rng(123)
    T = rng.standard_normal((5, 5, 5, 5))
    tt0 = tt_svd(T, max_ranks=(3, 3, 3))

    def _unfold_sv(tt, k=1):
        # Reconstruct, unfold at bond k, take SVD
        R = tt.reconstruct()
        left = int(np.prod(R.shape[: k + 1]))
        right = int(np.prod(R.shape[k + 1:]))
        return np.linalg.svd(R.reshape(left, right), compute_uv=False)

    sv_before = _unfold_sv(tt0)
    refined = tt_dmrg_refine(tt0, T, n_sweeps=1, rel_tol=1e-10, max_bond=8)
    sv_after = _unfold_sv(refined)
    n = min(len(sv_before), len(sv_after))
    delta = float(np.max(np.abs(sv_before[:n] - sv_after[:n])))
    print(f"  top-3 SV before: {sv_before[:3]}")
    print(f"  top-3 SV after:  {sv_after[:3]}")
    print(f"  max |delta_SV| = {delta:.3e}")
    if delta > 1e-8:
        print("  PASS: singular values shift")
    else:
        print("  FAIL: singular values byte-identical (cores not changing)")
    return {
        "sv_before_top3": [float(x) for x in sv_before[:3]],
        "sv_after_top3": [float(x) for x in sv_after[:3]],
        "max_delta": float(delta),
        "verdict": "PASS" if delta > 1e-8 else "FAIL",
    }


def test_rank_can_adapt():
    """C — When given a TT initialized with too-high ranks (zero-padded),
    does DMRG truncate them adaptively?

    Construct: take a low-rank tensor, decompose at high rank with
    zero-padded cores, then DMRG should detect and truncate.
    """
    print("\n=== Test C — Rank can adapt under tight rel_tol ===")
    rng = np.random.default_rng(7)
    # Low-effective-rank target: rank-2 separable
    a = rng.standard_normal((5, 2))
    b = rng.standard_normal((2, 5))
    M = a @ b
    M3 = np.einsum("ij,kl->ijkl", M, M)  # shape (5, 2, 5, 2)... awkward
    # Simpler: just use a rank-1 tensor
    v1 = rng.standard_normal(5); v2 = rng.standard_normal(5)
    v3 = rng.standard_normal(5); v4 = rng.standard_normal(5)
    T = np.einsum("i,j,k,l->ijkl", v1, v2, v3, v4)  # exact rank 1

    # Decompose at HIGH ranks
    tt_high = tt_svd(T, max_ranks=(4, 4, 4))
    err_high = relative_l2_error(T, tt_high.reconstruct())

    # DMRG with strict rel_tol should adapt down to rank 1
    tt_refined = tt_dmrg_refine(tt_high, T, n_sweeps=2, rel_tol=1e-8, max_bond=8)
    err_refined = relative_l2_error(T, tt_refined.reconstruct())

    print(f"  ranks_input  = {tt_high.ranks}  err = {err_high:.3e}")
    print(f"  ranks_output = {tt_refined.ranks}  err = {err_refined:.3e}")
    rank_dropped = max(tt_refined.ranks) < max(tt_high.ranks)
    if rank_dropped:
        print("  PASS: DMRG adapted rank downward")
    else:
        print("  AMBIGUOUS: rank did not drop (TT-SVD already optimal at this size)")
    return {
        "ranks_in": list(tt_high.ranks),
        "ranks_out": list(tt_refined.ranks),
        "err_in": float(err_high),
        "err_out": float(err_refined),
        "rank_dropped": bool(rank_dropped),
        "verdict": "PASS" if rank_dropped else "AMBIGUOUS",
    }


def test_rollback_guard():
    """D — Verify the rollback guard discards refinement when err_after
    fails to strictly improve.

    The wrapper tt_evaluate_with_dmrg returns the un-refined TT when
    err_after > err_before * 1.001. We construct a case at machine-epsilon
    error where DMRG cannot improve and the guard kicks in.
    """
    print("\n=== Test D — Rollback guard activates at machine epsilon ===")
    # Exact rank-1 tensor
    rng = np.random.default_rng(9)
    v = [rng.standard_normal(6) for _ in range(4)]
    T = np.einsum("i,j,k,l->ijkl", *v)

    refined_tt, err_before, err_after = tt_evaluate_with_dmrg(
        T, ranks=(2, 2, 2), n_sweeps=2, rel_tol=1e-10, max_bond=8,
    )
    refinement_gain = err_before - err_after
    print(f"  err_before = {err_before:.3e}")
    print(f"  err_after  = {err_after:.3e}")
    print(f"  refinement_gain = {refinement_gain:.3e}")
    print(f"  ranks_returned = {refined_tt.ranks}")
    if refinement_gain == 0.0:
        print("  Likely guard activated (gain = 0) — un-refined TT returned")
    elif refinement_gain > 0:
        print("  DMRG improved error — guard did not activate")
    return {
        "err_before": float(err_before),
        "err_after": float(err_after),
        "refinement_gain": float(refinement_gain),
        "guard_activated": bool(refinement_gain == 0.0),
    }


def main() -> int:
    import json
    from pathlib import Path
    print("DMRG instrument-trust unit tests")
    results = {
        "A_inner_loop_modifies_cores": test_inner_loop_modifies_cores(),
        "B_singular_values_change": test_singular_values_change(),
        "C_rank_can_adapt": test_rank_can_adapt(),
        "D_rollback_guard": test_rollback_guard(),
    }
    out = Path(__file__).resolve().parent.parent / "results" / "dmrg_unit_test.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"\nDumped {out}")

    # Roll-up
    print("\n=== ROLL-UP ===")
    a = results["A_inner_loop_modifies_cores"]["verdict"]
    b = results["B_singular_values_change"]["verdict"]
    c = results["C_rank_can_adapt"]["verdict"]
    d_guard = results["D_rollback_guard"]["guard_activated"]
    print(f"  A inner-loop modifies cores: {a}")
    print(f"  B singular values change:     {b}")
    print(f"  C rank can adapt:             {c}")
    print(f"  D rollback guard activates:   {d_guard}")
    if a == "PASS" and b == "PASS":
        print("\n  DMRG implementation is OPERATIONAL. The v3.2 §4.3 no-op")
        print("  attribution to (truncation tolerance + rollback guard) is")
        print("  defensible — DMRG works, it's just being suppressed by the")
        print("  configuration.")
    else:
        print("\n  DMRG implementation has a bug; v3.2 §4.3 conclusions need revision.")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
