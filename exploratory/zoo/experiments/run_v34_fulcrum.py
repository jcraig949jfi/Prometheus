"""v3.4 fulcrum experiment — three sub-tests in one driver.

Reviewer-2026-04-26: "Before claiming the audit detects geometry, prove it
is not first detecting combinatorics."

Three sub-experiments, each producing single-number stacks against the
Phase 5b reference of MI ~ 1.6-1.9 nats on (log_params, rank_entropy).

  (1) LATTICE BASELINE — MI on a uniform random sample of valid rank
      profiles, with no MAP-Elites, no TT-SVD, no DMRG. Pure combinatorics.
      The irreducible "the lattice itself has structure" baseline.

  (2) ARCHIVE-HISTORY DECOMPOSITION — same Phase 5b data, split into:
      all probes (history, n=400), archive elites (cells), Pareto front.
      If MI structure survives all subsets, intrinsic. If concentrated in
      elites, that is a selection artifact (extreme-order statistics).

  (3) SYNTHETIC IDENTIFIABILITY — Question K from review questions doc.
      Construct 5 synthetic descriptor pairs with KNOWN relationships:
        INDEPENDENT, LINEAR, NONLINEAR, DISCRETIZATION_ONLY, SELECTION_COUPLED.
      Verify the audit classifies each correctly. Audit alone passes only if
      it discriminates these — a different standard than "catches something."
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np

from zoo.descriptors.rank_profile import rank_entropy, rank_concentration
from zoo.diagnostics.nonlinear import distance_correlation, knn_mutual_information


def n_params_from_profile(profile, shape):
    """profile = (r_1, ..., r_{d-1}); shape = (n_1, ..., n_d)."""
    d = len(shape)
    assert len(profile) == d - 1, f"profile length {len(profile)} != d-1 = {d-1}"
    total = 0
    for k in range(d):
        r_prev = 1 if k == 0 else profile[k - 1]
        r_next = 1 if k == d - 1 else profile[k]
        total += r_prev * shape[k] * r_next
    return total


def _audit_pair(x: np.ndarray, y: np.ndarray, n_shuffles: int = 100,
                k: int = 3, subsample: int = 200, seed: int = 42) -> dict:
    """Pearson, dCor, KSG MI, shuffled null on (x, y)."""
    rng = np.random.default_rng(seed)
    n = len(x)
    if n > subsample:
        idx = rng.choice(n, size=subsample, replace=False)
        x, y = x[idx], y[idx]
    if x.std() == 0 or y.std() == 0:
        return {"n": int(len(x)), "pearson": 0.0, "dcor": 0.0, "mi": 0.0,
                "null_mean": 0.0, "obs_over_null": 0.0, "p_value": 1.0}
    xn = (x - x.mean()) / x.std()
    yn = (y - y.mean()) / y.std()
    pearson = float(np.corrcoef(xn, yn)[0, 1])
    dc = distance_correlation(xn, yn)
    mi = knn_mutual_information(xn, yn, k=k)
    nulls = []
    for _ in range(n_shuffles):
        yp = yn[rng.permutation(len(yn))]
        nulls.append(knn_mutual_information(xn, yp, k=k))
    nulls = np.array(nulls)
    return {
        "n": int(len(x)), "pearson": pearson, "dcor": float(dc), "mi": float(mi),
        "null_mean": float(nulls.mean()),
        "null_p99": float(np.percentile(nulls, 99)),
        "obs_over_null": float(mi / max(nulls.mean(), 1e-12)),
        "p_value": float((nulls >= mi).mean()),
    }


# =============================================================================
# Sub-experiment 1: lattice baseline
# =============================================================================

def sub1_lattice_baseline(shape=(12,) * 6, max_bond=16, n_samples=10000,
                          seed=20260426) -> dict:
    """Uniform random sample of valid rank profiles. NO MAP-Elites, NO TT-SVD."""
    print("\n=== SUB 1 — LATTICE BASELINE ===")
    rng = np.random.default_rng(seed)
    d = len(shape)
    # Per-bond cap from achievable size
    caps = []
    for k in range(d - 1):
        left = int(np.prod(shape[:k + 1]))
        right = int(np.prod(shape[k + 1:]))
        caps.append(min(max_bond, left, right))
    print(f"  shape={shape} max_bond={max_bond} per-bond caps={caps}")

    profiles = [
        tuple(int(rng.integers(1, c + 1)) for c in caps)
        for _ in range(n_samples)
    ]
    log_params = np.array([
        np.log10(max(1, n_params_from_profile(p, shape))) for p in profiles
    ])
    rank_entropies = np.array([rank_entropy(p) for p in profiles])
    rank_concs = np.array([rank_concentration(p) for p in profiles])
    avg_ranks = np.array([float(np.mean(p)) for p in profiles])

    # Coverage of achievable entropy range
    min_ent = rank_entropy(tuple([max_bond] + [1] * (d - 2)))  # most peaked
    max_ent = float(np.log(d - 1))                              # uniform
    print(f"  achievable entropy range: [{min_ent:.3f}, {max_ent:.3f}]")
    print(f"  observed entropy range:   [{rank_entropies.min():.3f}, {rank_entropies.max():.3f}]")

    audit_lp_re = _audit_pair(log_params, rank_entropies, n_shuffles=100, subsample=300)
    audit_lp_rc = _audit_pair(log_params, rank_concs, n_shuffles=100, subsample=300)
    audit_re_rc = _audit_pair(rank_entropies, rank_concs, n_shuffles=100, subsample=300)

    print(f"  AUDIT (log_params, rank_entropy):")
    print(f"    pearson={audit_lp_re['pearson']:+.3f}  dcor={audit_lp_re['dcor']:.3f}  "
          f"mi={audit_lp_re['mi']:.3f} nats  obs/null={audit_lp_re['obs_over_null']:.1f}")
    print(f"  AUDIT (log_params, rank_concentration):")
    print(f"    pearson={audit_lp_rc['pearson']:+.3f}  dcor={audit_lp_rc['dcor']:.3f}  "
          f"mi={audit_lp_rc['mi']:.3f} nats  obs/null={audit_lp_rc['obs_over_null']:.1f}")
    print(f"  AUDIT (rank_entropy, rank_concentration):")
    print(f"    pearson={audit_re_rc['pearson']:+.3f}  dcor={audit_re_rc['dcor']:.3f}  "
          f"mi={audit_re_rc['mi']:.3f} nats  obs/null={audit_re_rc['obs_over_null']:.1f}")

    return {
        "n_samples": n_samples,
        "shape": list(shape),
        "max_bond": max_bond,
        "caps": list(caps),
        "achievable_entropy_range": [min_ent, max_ent],
        "observed_entropy_range": [float(rank_entropies.min()),
                                   float(rank_entropies.max())],
        "audit_log_params_rank_entropy": audit_lp_re,
        "audit_log_params_rank_concentration": audit_lp_rc,
        "audit_rank_entropy_rank_concentration": audit_re_rc,
    }


# =============================================================================
# Sub-experiment 2: archive-history decomposition
# =============================================================================

def sub2_archive_history_decomposition(phase5b_path: Path) -> dict:
    """Compare audit verdict across data subsets of the same Phase 5b run."""
    print("\n=== SUB 2 — ARCHIVE-HISTORY DECOMPOSITION ===")
    with phase5b_path.open() as f:
        p5b = json.load(f)
    out: dict = {}
    for label in ["pairwise_tanh", "runge_dim", "heat_smoothed"]:
        print(f"  [{label}]")
        # All probes (pooled history)
        history = p5b["pooled_history"][label]
        lp_h = np.array([np.log10(max(1, e["n_params"])) for e in history])
        re_h = np.array([(e["extras"] or {}).get("rank_entropy", 0.0) for e in history])
        # Archive elites (cells from each seed; pooled across seeds)
        # phase5b dump structure: archives_seed_0 only has seed 0 cells; multi_seed_summaries has per-seed counts.
        # For archive-elite analysis across seeds we need per-seed cells. Reconstruct by extracting
        # the cell elites from seed 0 explicitly + read other seeds from multi_seed if available.
        # phase5b_no_dmrg dump structure stores pooled_history + archives_seed_0 only;
        # we rebuild archive elites by taking the per-seed (cell -> best elite) reduction
        # from history using the same try_place logic.
        # Simpler proxy: use the pooled_history directly and extract distinct cells.
        # Each elite already carries .cell so we group by (seed_idx_via_generation, cell).
        # We approximate "archive elites" as the unique (cell, lowest_rel_error) per seed.
        # Phase 5b runs n_initial=12 + n_generations=80; each seed produces 80 evaluations.
        # Pooled history is 5*80 = 400 entries.
        # We use cell field: for each generation grouping (seeds split by index 0:80, 80:160, ...).
        seed_size = len(history) // 5
        archive_elites = []
        for s in range(5):
            seed_history = history[s * seed_size:(s + 1) * seed_size]
            best_per_cell: dict[tuple, dict] = {}
            for e in seed_history:
                c = tuple(e["cell"])
                cur = best_per_cell.get(c)
                if cur is None or e["rel_error"] < cur["rel_error"]:
                    best_per_cell[c] = e
            archive_elites.extend(best_per_cell.values())
        lp_a = np.array([np.log10(max(1, e["n_params"])) for e in archive_elites])
        re_a = np.array([(e["extras"] or {}).get("rank_entropy", 0.0) for e in archive_elites])
        # Pareto front (per-seed, pooled)
        pareto_pool = []
        for s in range(5):
            seed_history = history[s * seed_size:(s + 1) * seed_size]
            # Reconstruct Pareto front from cells
            best_per_cell = {}
            for e in seed_history:
                c = tuple(e["cell"])
                cur = best_per_cell.get(c)
                if cur is None or e["rel_error"] < cur["rel_error"]:
                    best_per_cell[c] = e
            elites = list(best_per_cell.values())
            front = []
            for a in elites:
                dominated = False
                for b in elites:
                    if b is a:
                        continue
                    if (b["n_params"] <= a["n_params"]
                        and b["rel_error"] <= a["rel_error"]
                        and (b["n_params"] < a["n_params"] or b["rel_error"] < a["rel_error"])):
                        dominated = True
                        break
                if not dominated:
                    front.append(a)
            pareto_pool.extend(front)
        lp_p = np.array([np.log10(max(1, e["n_params"])) for e in pareto_pool])
        re_p = np.array([(e["extras"] or {}).get("rank_entropy", 0.0) for e in pareto_pool])

        results = {}
        for subset_name, lp, re in [("history", lp_h, re_h),
                                    ("archive_elites", lp_a, re_a),
                                    ("pareto_front", lp_p, re_p)]:
            audit = _audit_pair(lp, re, n_shuffles=100,
                                subsample=min(200, len(lp)), seed=42)
            results[subset_name] = audit
            print(f"    {subset_name}: n={audit['n']}  "
                  f"pearson={audit['pearson']:+.3f}  dcor={audit['dcor']:.3f}  "
                  f"mi={audit['mi']:.3f} nats  obs/null={audit['obs_over_null']:.1f}")
        out[label] = results
    return out


# =============================================================================
# Sub-experiment 3: synthetic identifiability (Question K)
# =============================================================================

def sub3_synthetic_identifiability(n=300, seed=20260426) -> dict:
    """Five synthetic descriptor pairs with KNOWN relationships.

    Verify the audit classifies each correctly:
      - INDEPENDENT: should return MI ~ 0, dcor ~ 0
      - LINEAR: high pearson, high dcor, high mi
      - NONLINEAR: low pearson, high dcor, high mi
      - DISCRETIZATION: high mi but driven by lattice structure, not 'real' coupling
      - SELECTION_COUPLED: mimics MAP-Elites elite selection on independent data
    """
    print("\n=== SUB 3 — SYNTHETIC IDENTIFIABILITY ===")
    rng = np.random.default_rng(seed)
    out: dict = {}

    # 1. INDEPENDENT
    x = rng.standard_normal(n)
    y = rng.standard_normal(n)
    out["INDEPENDENT"] = {
        "expected": "MI ~ 0, dcor ~ 0",
        "audit": _audit_pair(x, y, seed=seed),
    }

    # 2. LINEAR
    x = rng.standard_normal(n)
    z = rng.standard_normal(n)
    rho = 0.7
    y = rho * x + np.sqrt(1 - rho ** 2) * z
    out["LINEAR"] = {
        "expected": "pearson ~ 0.7, dcor ~ 0.7, mi ~ 0.6 nats",
        "audit": _audit_pair(x, y, seed=seed),
    }

    # 3. NONLINEAR (sinusoidal) — Pearson should be low, MI high
    x = rng.uniform(-2, 2, size=n)
    z = rng.standard_normal(n) * 0.1
    y = np.sin(2 * np.pi * x) + z
    out["NONLINEAR"] = {
        "expected": "pearson ~ 0, dcor moderate-high, mi high",
        "audit": _audit_pair(x, y, seed=seed),
    }

    # 4. DISCRETIZATION — lattice-induced coupling on independent draws
    # x = uniform integer in [0, 19]; y = (x mod 5) + small noise
    # Pure lattice/discretization structure; no continuous geometry.
    x = rng.integers(0, 20, size=n).astype(float)
    y = (x % 5).astype(float) + rng.standard_normal(n) * 0.05
    out["DISCRETIZATION"] = {
        "expected": "mi nontrivial despite no continuous coupling — lattice baseline",
        "audit": _audit_pair(x, y, seed=seed),
    }

    # 5. SELECTION_COUPLED — independent (x, y), but kept only the MIN y per x-bin
    # Simulates MAP-Elites cell-elite selection on truly independent variables.
    # Should produce APPARENT coupling from extreme-order-statistic effects alone.
    x_full = rng.uniform(0, 1, size=n * 5)  # 5x more samples to select from
    y_full = rng.standard_normal(n * 5)
    bins = np.linspace(0, 1, n + 1)
    x_sel: list[float] = []
    y_sel: list[float] = []
    for i in range(n):
        mask = (x_full >= bins[i]) & (x_full < bins[i + 1])
        if mask.sum() == 0:
            continue
        idx = np.where(mask)[0][np.argmin(y_full[mask])]
        x_sel.append(x_full[idx])
        y_sel.append(y_full[idx])
    x_sel_arr = np.array(x_sel)
    y_sel_arr = np.array(y_sel)
    out["SELECTION_COUPLED"] = {
        "expected": "apparent coupling from elite selection on independent data — danger zone",
        "audit": _audit_pair(x_sel_arr, y_sel_arr, seed=seed),
        "note": "if mi >> 0, the audit cannot distinguish elite-selection from real coupling",
    }

    for k, v in out.items():
        a = v["audit"]
        print(f"  [{k}] expected: {v['expected']}")
        print(f"    pearson={a['pearson']:+.3f}  dcor={a['dcor']:.3f}  "
              f"mi={a['mi']:.3f}  obs/null={a['obs_over_null']:.1f}  p={a['p_value']:.3f}")

    return out


# =============================================================================
# Driver
# =============================================================================

def main() -> int:
    t0 = time.time()
    phase5b_path = (Path(__file__).resolve().parent.parent / "results"
                    / "phase5b_no_dmrg_20260425T033645.json")
    if not phase5b_path.exists():
        print(f"FATAL: Phase 5b dump not found at {phase5b_path}")
        return 2

    print("v3.4 fulcrum experiment — three sub-tests")
    print("=" * 70)

    sub1 = sub1_lattice_baseline()
    sub2 = sub2_archive_history_decomposition(phase5b_path)
    sub3 = sub3_synthetic_identifiability()

    # Save dump
    out_dir = Path(__file__).resolve().parent.parent / "results"
    ts = time.strftime("%Y%m%dT%H%M%S")
    out_path = out_dir / f"v34_fulcrum_{ts}.json"
    payload = {
        "experiment": "v34_fulcrum",
        "timestamp": ts,
        "sub1_lattice_baseline": sub1,
        "sub2_archive_history_decomposition": sub2,
        "sub3_synthetic_identifiability": sub3,
        "elapsed_s": time.time() - t0,
    }
    out_path.write_text(json.dumps(payload, indent=2, default=str))
    print(f"\nDumped {out_path}")
    print(f"Total elapsed: {time.time() - t0:.1f}s")

    # Summary verdict
    print("\n" + "=" * 70)
    print("VERDICT SCAFFOLD (for paper integration)")
    print("=" * 70)
    lat_mi = sub1["audit_log_params_rank_entropy"]["mi"]
    print(f"\nLattice baseline MI (log_params, rank_entropy) = {lat_mi:.3f} nats")
    print("Phase 5b reference MI (frontier functions) = 1.6-1.9 nats")
    if lat_mi > 1.0:
        print(f"  -> WARNING: lattice baseline alone produces MI ~ {lat_mi:.2f} nats.")
        print(f"     Phase 5b's claim of 'TT geometry signal' overclaims by a wide margin.")
        print(f"     The bulk of the measured coupling is COMBINATORIAL, not GEOMETRIC.")
        print(f"     Headline must hedge from 'TT geometry' to 'descriptor design obstruction'.")
    elif lat_mi > 0.5:
        print(f"  -> CAVEAT: lattice baseline at {lat_mi:.2f} nats explains a substantial fraction")
        print(f"     of Phase 5b's MI. The TT-specific contribution is the residual ~{1.7 - lat_mi:.2f} nats.")
    else:
        print(f"  -> OK: lattice baseline is small ({lat_mi:.2f} nats).")
        print(f"     The Phase 5b coupling is predominantly TT-search-specific.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
