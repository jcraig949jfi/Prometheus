"""
Test 0.3 — Trivial Invariant Dominance

THE kill test for the coefficient representation.

Question: Can we predict "same isogeny class / same L-function" using only
trivial metadata (conductor, rank, torsion, cm, analytic_rank, fricke)?
If so, the coefficient vectors are a fancy conductor proxy, and the 100%
bridge recovery is explained by "same conductor = nearest neighbor."

Method:
  Model A: Gradient Boosting on full 25-dim coefficient vectors (both objects + distance)
  Model B: Gradient Boosting on trivial metadata only
  Model C: Logistic Regression on conductor-match alone (absolute baseline)

Failure condition: trivial model achieves >= 80% of coefficient model
performance (AUC or F1).

Binary outcome. No "promising." No "worth investigating."
"""

import duckdb
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

from charon.src.config import DB_PATH

np.random.seed(42)


def build_pair_dataset():
    """Build positive (true bridge) and negative (same conductor, not bridge) pairs."""
    duck = duckdb.connect(str(DB_PATH), read_only=True)

    # EC representatives (one per isogeny class)
    ecs_raw = duck.execute("""
        SELECT ec.lmfdb_iso, o.id, o.invariant_vector, o.conductor,
               ec.rank, ec.torsion, ec.cm, ec.analytic_rank
        FROM elliptic_curves ec
        JOIN objects o ON ec.object_id = o.id
        WHERE o.invariant_vector IS NOT NULL
        ORDER BY ec.lmfdb_iso
    """).fetchall()

    seen_iso = set()
    ec_data = []
    for iso, oid, vec, cond, rank, torsion, cm, arank in ecs_raw:
        if iso in seen_iso:
            continue
        seen_iso.add(iso)
        v25 = np.array([x if x is not None else 0.0 for x in vec[:25]])
        ec_data.append({
            'iso': iso, 'id': oid, 'vec': v25, 'conductor': int(cond),
            'rank': int(rank or 0), 'torsion': int(torsion or 0),
            'cm': int(cm or 0), 'analytic_rank': int(arank or 0)
        })

    # MFs: weight-2, dim-1, trivial character (the ones modularity connects to ECs)
    mfs_raw = duck.execute("""
        SELECT o.id, o.invariant_vector, o.conductor, mf.level,
               mf.weight, mf.fricke_eigenval, mf.is_cm
        FROM objects o
        JOIN modular_forms mf ON o.id = mf.object_id
        WHERE o.invariant_vector IS NOT NULL
          AND mf.weight = 2 AND mf.dim = 1 AND mf.char_order = 1
        ORDER BY o.conductor
    """).fetchall()

    mf_data = []
    for oid, vec, cond, level, weight, fricke, is_cm in mfs_raw:
        v25 = np.array([x if x is not None else 0.0 for x in vec[:25]])
        mf_data.append({
            'id': oid, 'vec': v25, 'conductor': int(cond),
            'level': int(level), 'weight': int(weight),
            'fricke': int(fricke or 0), 'is_cm': int(is_cm or 0)
        })

    # Known bridges
    bridges = duck.execute(
        "SELECT source_id, target_id FROM known_bridges WHERE bridge_type = 'modularity'"
    ).fetchall()
    bridge_set = set((s, t) for s, t in bridges)

    duck.close()

    print(f"EC representatives: {len(ec_data)}")
    print(f"MF dim-1 weight-2 trivial char: {len(mf_data)}")
    print(f"Known bridges: {len(bridge_set)}")

    # Index MFs by conductor
    mf_by_cond = defaultdict(list)
    for mf in mf_data:
        mf_by_cond[mf['conductor']].append(mf)

    # Build positive and negative pairs
    positive_pairs = []
    negative_pairs = []

    for ec in ec_data:
        cond = ec['conductor']
        cand_mfs = mf_by_cond.get(cond, [])

        for mf in cand_mfs:
            is_bridge = (ec['id'], mf['id']) in bridge_set

            # Coefficient features: distance + element-wise absolute difference
            coeff_dist = np.linalg.norm(ec['vec'] - mf['vec'])
            coeff_absdiff = np.abs(ec['vec'] - mf['vec'])
            coeff_features = np.concatenate([coeff_absdiff, [coeff_dist]])

            # Trivial features
            trivial_features = np.array([
                float(ec['conductor']),
                float(mf['conductor']),
                float(ec['conductor'] == mf['conductor']),
                float(ec['rank']),
                float(ec['torsion']),
                float(ec['cm']),
                float(ec['analytic_rank']),
                float(mf['fricke']),
                float(mf['is_cm']),
            ])

            if is_bridge:
                positive_pairs.append((coeff_features, trivial_features, 1))
            else:
                negative_pairs.append((coeff_features, trivial_features, 0))

    return positive_pairs, negative_pairs


def run_test():
    positive_pairs, negative_pairs = build_pair_dataset()

    print(f"Positive pairs (true bridges): {len(positive_pairs)}")
    print(f"Negative pairs (same conductor, not corresponding): {len(negative_pairs)}")

    # Balance: sample negatives to 3x positives
    if len(negative_pairs) > len(positive_pairs) * 3:
        idx = np.random.choice(len(negative_pairs), len(positive_pairs) * 3, replace=False)
        negative_pairs = [negative_pairs[i] for i in idx]
        print(f"Downsampled negatives to: {len(negative_pairs)}")

    all_pairs = positive_pairs + negative_pairs
    np.random.shuffle(all_pairs)

    X_coeff = np.array([p[0] for p in all_pairs])
    X_trivial = np.array([p[1] for p in all_pairs])
    y = np.array([p[2] for p in all_pairs])

    print(f"Total samples: {len(y)}, positive rate: {y.mean():.1%}")
    print()

    # ============================================================
    print("=" * 60)
    print("TEST 0.3: TRIVIAL INVARIANT DOMINANCE")
    print("=" * 60)
    print()

    # Model A: Coefficient features
    print("Model A: GradientBoosting on coefficient |diff| + distance (26 features)")
    clf_coeff = GradientBoostingClassifier(n_estimators=200, max_depth=5, random_state=42)
    auc_coeff_scores = cross_val_score(clf_coeff, X_coeff, y, cv=5, scoring='roc_auc')
    f1_coeff_scores = cross_val_score(clf_coeff, X_coeff, y, cv=5, scoring='f1')
    auc_coeff = auc_coeff_scores.mean()
    f1_coeff = f1_coeff_scores.mean()
    print(f"  AUC: {auc_coeff:.4f} (+/- {auc_coeff_scores.std():.4f})")
    print(f"  F1:  {f1_coeff:.4f} (+/- {f1_coeff_scores.std():.4f})")

    # Model B: Trivial metadata
    print()
    print("Model B: GradientBoosting on trivial metadata (9 features)")
    print("  [conductor_ec, conductor_mf, cond_match, rank, torsion, cm, analytic_rank, fricke, is_cm]")
    clf_trivial = GradientBoostingClassifier(n_estimators=200, max_depth=5, random_state=42)
    auc_triv_scores = cross_val_score(clf_trivial, X_trivial, y, cv=5, scoring='roc_auc')
    f1_triv_scores = cross_val_score(clf_trivial, X_trivial, y, cv=5, scoring='f1')
    auc_trivial = auc_triv_scores.mean()
    f1_trivial = f1_triv_scores.mean()
    print(f"  AUC: {auc_trivial:.4f} (+/- {auc_triv_scores.std():.4f})")
    print(f"  F1:  {f1_trivial:.4f} (+/- {f1_triv_scores.std():.4f})")

    # Model C: Conductor match alone
    print()
    print("Model C: LogisticRegression on conductor-match alone (1 feature)")
    X_cond_only = X_trivial[:, 2:3]
    clf_cond = LogisticRegression(random_state=42)
    auc_cond_scores = cross_val_score(clf_cond, X_cond_only, y, cv=5, scoring='roc_auc')
    auc_cond = auc_cond_scores.mean()
    print(f"  AUC: {auc_cond:.4f}")

    # ============================================================
    print()
    print("=" * 60)
    print("VERDICT")
    print("=" * 60)
    print()

    ratio_auc = auc_trivial / auc_coeff if auc_coeff > 0 else float('inf')
    ratio_f1 = f1_trivial / f1_coeff if f1_coeff > 0 else float('inf')

    print(f"Coefficient model AUC:     {auc_coeff:.4f}")
    print(f"Trivial model AUC:         {auc_trivial:.4f}")
    print(f"Conductor-only AUC:        {auc_cond:.4f}")
    print()
    print(f"Trivial/Coefficient AUC ratio: {ratio_auc:.4f}")
    print(f"Trivial/Coefficient F1 ratio:  {ratio_f1:.4f}")
    print()
    print(f"Failure condition: trivial model >= 80% of coefficient model")
    print(f"  AUC ratio >= 0.80? {'YES -> FAIL' if ratio_auc >= 0.80 else 'NO -> PASS'} ({ratio_auc:.4f})")
    print(f"  F1  ratio >= 0.80? {'YES -> FAIL' if ratio_f1 >= 0.80 else 'NO -> PASS'} ({ratio_f1:.4f})")
    print()

    if ratio_auc >= 0.80 or ratio_f1 >= 0.80:
        print("TEST 0.3: *** FAILED ***")
        print("Trivial invariants explain most of what coefficients explain.")
        print("The coefficient vectors are primarily encoding conductor.")
        print("The 100% bridge recovery is a conductor proximity artifact.")
        print()
        print("DO NOT scale to conductor 50K. DO NOT ingest L-functions.")
        print("Pivot to Direction 2 (low-lying zeros) or Direction 3 (relationship graph).")
        return False
    else:
        print("TEST 0.3: PASSED")
        print(f"Coefficient vectors carry significant signal beyond trivial invariants.")
        print(f"Trivial model captures only {ratio_auc:.0%} of coefficient AUC.")
        return True


if __name__ == "__main__":
    result = run_test()
