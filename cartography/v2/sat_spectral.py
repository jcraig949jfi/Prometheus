#!/usr/bin/env python3
"""
SAT Spectral Experiment -- Charon
================================
Generate 1,000 random 3-SAT instances near the phase transition (alpha ~ 4.27, n=50).
Build variable interaction graphs, compute eigenvalue spectra, separate SAT/UNSAT,
and test whether spectral signatures differ measurably.

Key questions:
  1. Do SAT and UNSAT instances have different spectral signatures?
  2. Does SVD on (instance x spectral features) reveal low-rank structure?
  3. Is the spectral gap (lambda1 - lambda2) measurably different between SAT and UNSAT?
"""

import json
import time
import numpy as np
from pathlib import Path

# --Parameters --------------------------------------------------------------
N_VARS = 50
ALPHA = 4.27
N_CLAUSES = round(ALPHA * N_VARS)  # 214
N_INSTANCES = 1000
SEED = 42
MAX_DPLL_CALLS = 500_000  # budget per instance to keep runtime bounded

rng = np.random.default_rng(SEED)


# --1. Random 3-SAT generation ---------------------------------------------
def generate_3sat(n_vars, n_clauses, rng):
    """Generate a random 3-SAT instance. Returns list of clauses.
    Each clause is a tuple of 3 signed literals (1-indexed, negative = negated)."""
    clauses = []
    for _ in range(n_clauses):
        # Pick 3 distinct variables
        vars_ = rng.choice(n_vars, size=3, replace=False) + 1
        # Random signs
        signs = rng.choice([-1, 1], size=3)
        clause = tuple(int(v * s) for v, s in zip(vars_, signs))
        clauses.append(clause)
    return clauses


# --2. DPLL solver (simple, with unit propagation) -------------------------
def solve_dpll(clauses, n_vars, max_calls=MAX_DPLL_CALLS):
    """Simple DPLL solver. Returns True (SAT) or False (UNSAT/timeout)."""
    call_count = [0]

    def _solve(assignment, clauses):
        call_count[0] += 1
        if call_count[0] > max_calls:
            return None  # timeout -- treat as unknown

        # Unit propagation
        changed = True
        while changed:
            changed = False
            for clause in clauses:
                unset = []
                satisfied = False
                for lit in clause:
                    var = abs(lit)
                    if var in assignment:
                        if (lit > 0) == assignment[var]:
                            satisfied = True
                            break
                    else:
                        unset.append(lit)
                if satisfied:
                    continue
                if len(unset) == 0:
                    return False  # conflict
                if len(unset) == 1:
                    # Unit clause -- force assignment
                    lit = unset[0]
                    var = abs(lit)
                    assignment[var] = (lit > 0)
                    changed = True

        # Check all clauses
        all_satisfied = True
        for clause in clauses:
            satisfied = False
            has_unset = False
            for lit in clause:
                var = abs(lit)
                if var in assignment:
                    if (lit > 0) == assignment[var]:
                        satisfied = True
                        break
                else:
                    has_unset = True
            if not satisfied:
                if not has_unset:
                    return False  # unsatisfied, no unset vars
                all_satisfied = False

        if all_satisfied:
            return True

        # Pick an unset variable (first unset)
        for v in range(1, n_vars + 1):
            if v not in assignment:
                for val in [True, False]:
                    new_assign = dict(assignment)
                    new_assign[v] = val
                    result = _solve(new_assign, clauses)
                    if result is True:
                        return True
                    if result is None:
                        return None
                return False
        return True

    return _solve({}, clauses)


# --3. Build variable interaction graph ------------------------------------
def build_adjacency(clauses, n_vars):
    """Build weighted adjacency matrix. Edge weight = number of shared clauses."""
    adj = np.zeros((n_vars, n_vars), dtype=np.float64)
    for clause in clauses:
        vars_ = [abs(lit) - 1 for lit in clause]  # 0-indexed
        for i in range(len(vars_)):
            for j in range(i + 1, len(vars_)):
                adj[vars_[i], vars_[j]] += 1
                adj[vars_[j], vars_[i]] += 1
    return adj


# --4. Spectral features --------------------------------------------------
def compute_spectral_features(adj):
    """Compute eigenvalue spectrum and derived features."""
    eigenvalues = np.linalg.eigvalsh(adj)  # sorted ascending
    eigenvalues = eigenvalues[::-1]  # now descending

    # Features
    lambda1 = eigenvalues[0]
    lambda2 = eigenvalues[1]
    spectral_gap = lambda1 - lambda2
    spectral_radius = lambda1
    trace = np.sum(eigenvalues)  # should be 0 for adjacency matrix
    algebraic_connectivity = eigenvalues[-2]  # second smallest (Fiedler value)

    # Spectral entropy (normalized eigenvalues as distribution)
    abs_eigs = np.abs(eigenvalues)
    if abs_eigs.sum() > 0:
        p = abs_eigs / abs_eigs.sum()
        p = p[p > 0]
        spectral_entropy = -np.sum(p * np.log(p))
    else:
        spectral_entropy = 0.0

    # Energy (sum of absolute eigenvalues)
    energy = np.sum(abs_eigs)

    return {
        "eigenvalues": eigenvalues,
        "lambda1": lambda1,
        "lambda2": lambda2,
        "spectral_gap": spectral_gap,
        "spectral_radius": spectral_radius,
        "algebraic_connectivity": algebraic_connectivity,
        "spectral_entropy": spectral_entropy,
        "energy": energy,
    }


# --5. Main experiment ----------------------------------------------------
def run_experiment():
    print(f"SAT Spectral Experiment: n={N_VARS}, m={N_CLAUSES}, alpha={ALPHA}, instances={N_INSTANCES}")
    print(f"Seed: {SEED}")
    print()

    sat_spectra = []
    unsat_spectra = []
    unknown_spectra = []
    all_features = []
    all_labels = []  # 1=SAT, 0=UNSAT, -1=unknown

    t0 = time.time()

    for i in range(N_INSTANCES):
        if (i + 1) % 100 == 0:
            elapsed = time.time() - t0
            print(f"  Instance {i+1}/{N_INSTANCES}  ({elapsed:.1f}s elapsed)")

        clauses = generate_3sat(N_VARS, N_CLAUSES, rng)
        adj = build_adjacency(clauses, N_VARS)
        feats = compute_spectral_features(adj)

        result = solve_dpll(clauses, N_VARS)

        feature_vec = [
            feats["lambda1"],
            feats["lambda2"],
            feats["spectral_gap"],
            feats["spectral_radius"],
            feats["algebraic_connectivity"],
            feats["spectral_entropy"],
            feats["energy"],
        ]
        # Also store top-10 eigenvalues as features
        top_eigs = feats["eigenvalues"][:10].tolist()
        feature_vec.extend(top_eigs)

        all_features.append(feature_vec)

        if result is True:
            sat_spectra.append(feats)
            all_labels.append(1)
        elif result is False:
            unsat_spectra.append(feats)
            all_labels.append(0)
        else:
            unknown_spectra.append(feats)
            all_labels.append(-1)

    elapsed = time.time() - t0
    print(f"\nCompleted in {elapsed:.1f}s")
    print(f"  SAT:     {len(sat_spectra)}")
    print(f"  UNSAT:   {len(unsat_spectra)}")
    print(f"  Unknown: {len(unknown_spectra)}")
    print()

    # --6. Compare SAT vs UNSAT spectra ----------------------------------
    results = {}
    results["parameters"] = {
        "n_vars": N_VARS,
        "n_clauses": N_CLAUSES,
        "alpha": ALPHA,
        "n_instances": N_INSTANCES,
        "seed": SEED,
    }
    results["counts"] = {
        "sat": len(sat_spectra),
        "unsat": len(unsat_spectra),
        "unknown": len(unknown_spectra),
    }

    if len(sat_spectra) > 0 and len(unsat_spectra) > 0:
        # Spectral gap comparison
        sat_gaps = [f["spectral_gap"] for f in sat_spectra]
        unsat_gaps = [f["spectral_gap"] for f in unsat_spectra]

        sat_gap_mean = float(np.mean(sat_gaps))
        sat_gap_std = float(np.std(sat_gaps))
        unsat_gap_mean = float(np.mean(unsat_gaps))
        unsat_gap_std = float(np.std(unsat_gaps))

        # Effect size (Cohen's d)
        pooled_std = np.sqrt((np.var(sat_gaps) + np.var(unsat_gaps)) / 2)
        cohens_d = (sat_gap_mean - unsat_gap_mean) / pooled_std if pooled_std > 0 else 0.0

        # Welch's t-test (manual)
        n1, n2 = len(sat_gaps), len(unsat_gaps)
        se = np.sqrt(np.var(sat_gaps)/n1 + np.var(unsat_gaps)/n2)
        t_stat = (sat_gap_mean - unsat_gap_mean) / se if se > 0 else 0.0

        print("-- Spectral Gap (L1 - L2) ---------------------------")
        print(f"  SAT:   mean={sat_gap_mean:.4f}  std={sat_gap_std:.4f}  (n={n1})")
        print(f"  UNSAT: mean={unsat_gap_mean:.4f}  std={unsat_gap_std:.4f}  (n={n2})")
        print(f"  Cohen's d = {cohens_d:.4f}")
        print(f"  Welch's t = {t_stat:.4f}")
        print()

        results["spectral_gap"] = {
            "sat_mean": sat_gap_mean,
            "sat_std": sat_gap_std,
            "unsat_mean": unsat_gap_mean,
            "unsat_std": unsat_gap_std,
            "cohens_d": float(cohens_d),
            "welch_t": float(t_stat),
        }

        # Compare all scalar features
        feature_names = ["lambda1", "lambda2", "spectral_gap", "spectral_radius",
                         "algebraic_connectivity", "spectral_entropy", "energy"]
        feature_comparison = {}
        print("-- Feature Comparison (SAT vs UNSAT) ---------------")
        for fname in feature_names:
            sat_vals = [f[fname] for f in sat_spectra]
            unsat_vals = [f[fname] for f in unsat_spectra]
            sm, ss = float(np.mean(sat_vals)), float(np.std(sat_vals))
            um, us = float(np.mean(unsat_vals)), float(np.std(unsat_vals))
            ps = np.sqrt((np.var(sat_vals) + np.var(unsat_vals)) / 2)
            cd = (sm - um) / ps if ps > 0 else 0.0
            print(f"  {fname:30s}  SAT={sm:.4f}+-{ss:.4f}  UNSAT={um:.4f}+-{us:.4f}  d={cd:.4f}")
            feature_comparison[fname] = {
                "sat_mean": sm, "sat_std": ss,
                "unsat_mean": um, "unsat_std": us,
                "cohens_d": float(cd),
            }
        print()
        results["feature_comparison"] = feature_comparison

        # --7. SVD / Rank-3 decomposition --------------------------------
        # Only use SAT+UNSAT instances (exclude unknown)
        known_mask = [l >= 0 for l in all_labels]
        X = np.array([f for f, m in zip(all_features, known_mask) if m])
        labels_known = np.array([l for l, m in zip(all_labels, known_mask) if m])

        # Center and normalize
        X_centered = X - X.mean(axis=0)
        col_std = X_centered.std(axis=0)
        col_std[col_std == 0] = 1
        X_normed = X_centered / col_std

        U, S, Vt = np.linalg.svd(X_normed, full_matrices=False)
        total_var = np.sum(S**2)
        cumulative_var = np.cumsum(S**2) / total_var

        print("--SVD Rank Decomposition --------------------------")
        for k in range(min(10, len(S))):
            print(f"  Component {k+1}: sigma={S[k]:.4f}  cumulative variance={cumulative_var[k]*100:.2f}%")

        rank_90 = int(np.searchsorted(cumulative_var, 0.90)) + 1
        rank_95 = int(np.searchsorted(cumulative_var, 0.95)) + 1
        rank_99 = int(np.searchsorted(cumulative_var, 0.99)) + 1
        print(f"\n  Rank for 90% variance: {rank_90}")
        print(f"  Rank for 95% variance: {rank_95}")
        print(f"  Rank for 99% variance: {rank_99}")

        # Is rank 2-3 sufficient? (>90% = low-rank shortcut)
        var_at_rank3 = float(cumulative_var[min(2, len(cumulative_var)-1)])
        low_rank_shortcut = var_at_rank3 > 0.90
        print(f"  Variance at rank 3: {var_at_rank3*100:.2f}%")
        print(f"  Low-rank shortcut (rank 3 > 90%): {low_rank_shortcut}")
        print()

        results["svd"] = {
            "singular_values": S[:10].tolist(),
            "cumulative_variance": cumulative_var[:10].tolist(),
            "rank_90": rank_90,
            "rank_95": rank_95,
            "rank_99": rank_99,
            "variance_at_rank3": float(var_at_rank3),
            "low_rank_shortcut": low_rank_shortcut,
        }

        # --8. Spectral gap as separator ---------------------------------
        # Can spectral gap alone classify SAT vs UNSAT?
        all_gaps = np.array(sat_gaps + unsat_gaps)
        all_gap_labels = np.array([1]*len(sat_gaps) + [0]*len(unsat_gaps))

        # Simple threshold classifier: sweep thresholds
        best_acc = 0.0
        best_thresh = 0.0
        thresholds = np.linspace(all_gaps.min(), all_gaps.max(), 1000)
        for thresh in thresholds:
            preds = (all_gaps >= thresh).astype(int)
            acc = np.mean(preds == all_gap_labels)
            if acc > best_acc:
                best_acc = acc
                best_thresh = thresh
            # Also check inverted
            acc_inv = np.mean((1 - preds) == all_gap_labels)
            if acc_inv > best_acc:
                best_acc = acc_inv
                best_thresh = thresh

        print(f"--Spectral Gap as Classifier ----------------------")
        print(f"  Best threshold accuracy: {best_acc*100:.2f}%")
        print(f"  Best threshold value:    {best_thresh:.4f}")
        print(f"  (Chance level: {max(len(sat_gaps), len(unsat_gaps))/len(all_gaps)*100:.1f}%)")
        print()

        results["gap_classifier"] = {
            "best_accuracy": float(best_acc),
            "best_threshold": float(best_thresh),
            "chance_level": float(max(len(sat_gaps), len(unsat_gaps)) / len(all_gaps)),
        }

        # --9. Full eigenvalue distribution comparison -------------------
        sat_eig_matrix = np.array([f["eigenvalues"] for f in sat_spectra])
        unsat_eig_matrix = np.array([f["eigenvalues"] for f in unsat_spectra])

        sat_eig_mean = sat_eig_matrix.mean(axis=0)
        unsat_eig_mean = unsat_eig_matrix.mean(axis=0)
        eig_diff = sat_eig_mean - unsat_eig_mean
        max_eig_diff_idx = int(np.argmax(np.abs(eig_diff)))
        max_eig_diff_val = float(eig_diff[max_eig_diff_idx])

        print(f"--Eigenvalue Distribution -------------------------")
        print(f"  Max mean difference at eigenvalue index {max_eig_diff_idx}: {max_eig_diff_val:.6f}")
        print(f"  Mean |difference| across spectrum: {float(np.mean(np.abs(eig_diff))):.6f}")
        print()

        results["eigenvalue_distribution"] = {
            "max_diff_index": max_eig_diff_idx,
            "max_diff_value": max_eig_diff_val,
            "mean_abs_diff": float(np.mean(np.abs(eig_diff))),
            "sat_mean_top5": sat_eig_mean[:5].tolist(),
            "unsat_mean_top5": unsat_eig_mean[:5].tolist(),
        }

    else:
        print("WARNING: Not enough SAT or UNSAT instances for comparison.")
        results["error"] = "insufficient_instances"

    # --10. Interpretation ------------------------------------------------
    interpretation = []
    if "spectral_gap" in results:
        sg = results["spectral_gap"]
        d = abs(sg["cohens_d"])
        if d < 0.2:
            interpretation.append(f"Spectral gap effect size is negligible (d={d:.3f}). No measurable constant separates SAT/UNSAT.")
        elif d < 0.5:
            interpretation.append(f"Spectral gap effect size is small (d={d:.3f}). Weak but detectable spectral difference.")
        elif d < 0.8:
            interpretation.append(f"Spectral gap effect size is medium (d={d:.3f}). Meaningful spectral difference exists.")
        else:
            interpretation.append(f"Spectral gap effect size is large (d={d:.3f}). Strong spectral signature separates SAT/UNSAT.")

    if "svd" in results:
        svd = results["svd"]
        if svd["low_rank_shortcut"]:
            interpretation.append(f"SVD reveals low-rank structure: rank 3 captures {svd['variance_at_rank3']*100:.1f}% of variance. Hidden shortcut exists in spectral space.")
        else:
            interpretation.append(f"SVD shows high-rank structure: rank 3 captures only {svd['variance_at_rank3']*100:.1f}% of variance. No low-rank shortcut -- this is a hard wall.")

    if "gap_classifier" in results:
        gc = results["gap_classifier"]
        if gc["best_accuracy"] > gc["chance_level"] + 0.05:
            interpretation.append(f"Spectral gap achieves {gc['best_accuracy']*100:.1f}% classification (chance={gc['chance_level']*100:.1f}%). Above chance but likely insufficient for practical separation.")
        else:
            interpretation.append(f"Spectral gap classification ({gc['best_accuracy']*100:.1f}%) is at chance level ({gc['chance_level']*100:.1f}%). Spectral gap alone cannot separate SAT/UNSAT.")

    results["interpretation"] = interpretation

    print("--Interpretation ----------------------------------")
    for line in interpretation:
        print(f"  {line}")
    print()

    # --Save results ------------------------------------------------------
    out_path = Path(__file__).parent / "sat_spectral_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {out_path}")

    return results


if __name__ == "__main__":
    run_experiment()
