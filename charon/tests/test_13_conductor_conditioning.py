"""
Test 1.3 — Conductor Conditioning

The kill shot for conductor-as-proxy.

Within a fixed conductor stratum, is there residual clustering structure?
Take all objects within conductor bins. Cluster by coefficient vector.
Do the clusters correspond to anything mathematically meaningful?

Method:
  - Group EC representatives by conductor
  - Only consider conductors with >= 5 EC isogeny classes
  - Within each conductor bin, cluster the coefficient vectors (k-means)
  - Measure adjusted Rand index (ARI) against known invariants:
    * Analytic rank
    * Torsion structure
    * CM discriminant
    * Isogeny class (must be 1.0 by definition — sanity check)

Failure condition: mean ARI < 0.6 for ALL known invariants across strata.
(If no invariant achieves ARI > 0.6, clusters are noise after conditioning.)
"""

import duckdb
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
from collections import defaultdict
from charon.src.config import DB_PATH

np.random.seed(42)


def run_test():
    duck = duckdb.connect(str(DB_PATH), read_only=True)

    # Get all EC reps with metadata
    ecs_raw = duck.execute("""
        SELECT ec.lmfdb_iso, o.id, o.invariant_vector, o.conductor,
               ec.rank, ec.analytic_rank, ec.torsion, ec.torsion_structure,
               ec.cm, ec.class_size
        FROM elliptic_curves ec
        JOIN objects o ON ec.object_id = o.id
        WHERE o.invariant_vector IS NOT NULL
        ORDER BY ec.lmfdb_iso
    """).fetchall()

    seen = set()
    ec_data = []
    for iso, oid, vec, cond, rank, arank, torsion, tor_struct, cm, cls_size in ecs_raw:
        if iso in seen:
            continue
        seen.add(iso)
        v25 = np.array([x if x is not None else 0.0 for x in vec[:25]])
        ec_data.append({
            'iso': iso, 'vec': v25, 'conductor': int(cond),
            'rank': int(rank or 0), 'analytic_rank': int(arank or 0),
            'torsion': int(torsion or 0), 'cm': int(cm or 0),
            'class_size': int(cls_size or 1),
        })

    # Group by conductor
    by_cond = defaultdict(list)
    for ec in ec_data:
        by_cond[ec['conductor']].append(ec)

    # Only conductors with >= 5 EC isogeny classes
    eligible = {c: ecs for c, ecs in by_cond.items() if len(ecs) >= 5}

    print("=" * 60)
    print("TEST 1.3: CONDUCTOR CONDITIONING")
    print("=" * 60)
    print()
    print(f"Total conductors: {len(by_cond)}")
    print(f"Conductors with >= 5 EC iso classes: {len(eligible)}")
    print()

    # For each conductor stratum, cluster and measure ARI
    ari_by_invariant = defaultdict(list)
    nmi_by_invariant = defaultdict(list)
    strata_results = []

    for cond, ecs in sorted(eligible.items()):
        n = len(ecs)
        X = np.array([ec['vec'] for ec in ecs])

        # Determine k (at most n//2, at least 2)
        # Heuristic: number of unique values of the most varied invariant
        n_unique_rank = len(set(ec['rank'] for ec in ecs))
        n_unique_torsion = len(set(ec['torsion'] for ec in ecs))
        k = max(2, min(n // 2, max(n_unique_rank, n_unique_torsion, 3)))

        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        cluster_labels = km.fit_predict(X)

        # Measure ARI against each known invariant
        for invariant_name in ['rank', 'analytic_rank', 'torsion', 'cm']:
            true_labels = [ec[invariant_name] for ec in ecs]

            # Skip if invariant is constant in this stratum
            if len(set(true_labels)) < 2:
                continue

            ari = adjusted_rand_score(true_labels, cluster_labels)
            nmi = normalized_mutual_info_score(true_labels, cluster_labels)
            ari_by_invariant[invariant_name].append(ari)
            nmi_by_invariant[invariant_name].append(nmi)

        strata_results.append({
            'conductor': cond, 'n_classes': n, 'k': k,
        })

    # Report
    print(f"Strata analyzed: {len(strata_results)}")
    print()

    print("Mean Adjusted Rand Index (ARI) by invariant:")
    print("  (ARI=1.0: perfect agreement, ARI=0.0: random, ARI<0: worse than random)")
    print()

    best_ari = 0.0
    best_invariant = None
    for inv in ['rank', 'analytic_rank', 'torsion', 'cm']:
        vals = ari_by_invariant[inv]
        if vals:
            mean_ari = np.mean(vals)
            median_ari = np.median(vals)
            frac_above_06 = np.mean(np.array(vals) > 0.6)
            print(f"  {inv:15s}: mean ARI = {mean_ari:.4f}, median = {median_ari:.4f}, "
                  f"fraction > 0.6: {frac_above_06:.1%} ({len(vals)} strata)")
            if mean_ari > best_ari:
                best_ari = mean_ari
                best_invariant = inv
        else:
            print(f"  {inv:15s}: no strata with variation")

    print()
    print("Mean Normalized Mutual Information (NMI):")
    for inv in ['rank', 'analytic_rank', 'torsion', 'cm']:
        vals = nmi_by_invariant[inv]
        if vals:
            print(f"  {inv:15s}: mean NMI = {np.mean(vals):.4f}")

    # Also check: within a single conductor, do coefficient distances
    # separate different-rank curves from same-rank curves?
    print()
    print("--- Intra-conductor distance analysis ---")
    same_rank_dists = []
    diff_rank_dists = []
    for cond, ecs in eligible.items():
        for i in range(len(ecs)):
            for j in range(i + 1, len(ecs)):
                d = np.linalg.norm(ecs[i]['vec'] - ecs[j]['vec'])
                if ecs[i]['rank'] == ecs[j]['rank']:
                    same_rank_dists.append(d)
                else:
                    diff_rank_dists.append(d)

    same_rank_dists = np.array(same_rank_dists)
    diff_rank_dists = np.array(diff_rank_dists)
    print(f"  Same-rank pairs: {len(same_rank_dists)}, mean dist = {same_rank_dists.mean():.4f}")
    print(f"  Diff-rank pairs: {len(diff_rank_dists)}, mean dist = {diff_rank_dists.mean():.4f}")
    if len(diff_rank_dists) > 0 and len(same_rank_dists) > 0:
        from scipy.stats import mannwhitneyu
        u_stat, u_p = mannwhitneyu(same_rank_dists, diff_rank_dists, alternative='less')
        print(f"  Mann-Whitney U: p = {u_p:.2e} (same-rank < diff-rank?)")

    # Verdict
    print()
    print("=" * 60)
    print("VERDICT")
    print("=" * 60)
    print()
    print(f"Best invariant: {best_invariant} (mean ARI = {best_ari:.4f})")
    print(f"Failure condition: no invariant achieves mean ARI > 0.6")

    if best_ari > 0.6:
        print(f"TEST 1.3: PASSED — Residual structure exists after conductor conditioning.")
        print(f"  Clusters align with '{best_invariant}' at ARI = {best_ari:.4f}")
        return True
    else:
        print(f"TEST 1.3: FAILED — Clusters dissolve into noise after conditioning on conductor.")
        print(f"  Best ARI = {best_ari:.4f} < 0.6")
        print(f"  The metric is a conductor proxy.")
        return False


if __name__ == "__main__":
    run_test()
