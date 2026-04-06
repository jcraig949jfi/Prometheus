"""
Direction 2: Relationship Type Classification
================================================
Can we predict the relationship type between two LMFDB objects from their
arithmetic invariants? Unpredictable relationships encode deep structure.
"""

import duckdb
import numpy as np
import json
import logging
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder

DB = Path(__file__).parents[3] / "charon" / "data" / "charon.duckdb"
REPORT_DIR = Path(__file__).parent.parent / "reports"
REPORT_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout),
              logging.FileHandler(REPORT_DIR / f"relationship_classification_{date.today()}.log",
                                  mode="w", encoding="utf-8")])
log = logging.getLogger("cart.classify")


def main():
    log.info("=" * 70)
    log.info("DIRECTION 2: RELATIONSHIP TYPE CLASSIFICATION")
    log.info(f"Date: {date.today()}")
    log.info("=" * 70)

    duck = duckdb.connect(str(DB), read_only=True)

    # ================================================================
    # 1. Build feature vectors for edges
    # ================================================================
    log.info("\n--- 1. BUILDING EDGE FEATURES ---")

    # Get edges with source/target invariant vectors and metadata
    edges = duck.execute("""
        SELECT ge.edge_type,
               o1.object_type as src_type, o2.object_type as tgt_type,
               o1.conductor as src_cond, o2.conductor as tgt_cond,
               o1.invariant_vector as src_inv, o2.invariant_vector as tgt_inv,
               o1.zeros_vector as src_zeros, o2.zeros_vector as tgt_zeros
        FROM graph_edges ge
        JOIN objects o1 ON ge.source_id = o1.id
        JOIN objects o2 ON ge.target_id = o2.id
        WHERE o1.invariant_vector IS NOT NULL
          AND o2.invariant_vector IS NOT NULL
        LIMIT 50000
    """).fetchall()

    log.info(f"Edges with invariant vectors: {len(edges)}")

    # Build features for each edge
    X = []
    y = []
    edge_info = []

    for (btype, st, tt, sc, tc, sinv, tinv, szeros, tzeros) in edges:
        # Pairwise features from invariant vectors
        if sinv is None or tinv is None:
            continue

        sv = np.array([float(v) if v is not None else 0.0 for v in sinv[:20]])
        tv = np.array([float(v) if v is not None else 0.0 for v in tinv[:20]])

        # Feature vector: concatenate, difference, product
        diff = sv - tv
        l2_dist = np.sqrt(np.sum(diff**2))
        cos_sim = np.dot(sv, tv) / (np.linalg.norm(sv) * np.linalg.norm(tv) + 1e-10)

        # Conductor features
        cond_ratio = np.log(max(sc, 1)) / np.log(max(tc, 1)) if tc and sc else 1.0
        cond_diff = abs(int(sc or 0) - int(tc or 0))
        same_cond = 1.0 if sc == tc else 0.0

        # Type features
        same_type = 1.0 if st == tt else 0.0

        # Zero similarity (if available)
        zero_dist = 0.0
        if szeros is not None and tzeros is not None:
            sz = np.array([float(v) if v is not None else 0.0 for v in szeros[:20]])
            tz = np.array([float(v) if v is not None else 0.0 for v in tzeros[:20]])
            zero_dist = np.sqrt(np.sum((sz - tz)**2))

        features = list(diff[:10]) + [
            l2_dist, cos_sim, cond_ratio, np.log1p(cond_diff),
            same_cond, same_type, zero_dist,
        ]

        X.append(features)
        y.append(btype)
        edge_info.append((st, tt, sc, tc))

    X = np.array(X)
    log.info(f"Feature matrix: {X.shape}")
    log.info(f"Edge type distribution: {dict(sorted(defaultdict(int, [(label, 1) for label in y]).items(), key=lambda x: -x[1]))}")

    # ================================================================
    # 2. Classification: can we predict edge type?
    # ================================================================
    log.info("\n--- 2. CLASSIFICATION ---")

    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    classes = le.classes_

    log.info(f"Classes: {list(classes)}")
    log.info(f"Class distribution: {dict(zip(classes, np.bincount(y_enc)))}")

    # Random Forest
    rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    rf_scores = cross_val_score(rf, X, y_enc, cv=5, scoring='accuracy')
    log.info(f"\nRandom Forest accuracy: {rf_scores.mean():.4f} +/- {rf_scores.std():.4f}")

    # Baseline: predict most common class
    most_common = np.bincount(y_enc).max() / len(y_enc)
    log.info(f"Baseline (majority class): {most_common:.4f}")
    log.info(f"Lift over baseline: {rf_scores.mean() / most_common:.2f}x")

    # ================================================================
    # 3. Feature importance: which invariants predict relationships?
    # ================================================================
    log.info("\n--- 3. FEATURE IMPORTANCE ---")

    rf.fit(X, y_enc)
    feature_names = [f"diff_{i}" for i in range(10)] + [
        "l2_dist", "cos_sim", "cond_ratio", "log_cond_diff",
        "same_cond", "same_type", "zero_dist",
    ]

    importances = sorted(zip(feature_names, rf.feature_importances_), key=lambda x: -x[1])
    log.info("Top features:")
    for name, imp in importances[:10]:
        log.info(f"  {name:>15}: {imp:.4f}")

    # ================================================================
    # 4. Per-class accuracy: which types are predictable?
    # ================================================================
    log.info("\n--- 4. PER-CLASS PREDICTABILITY ---")

    from sklearn.model_selection import cross_val_predict
    y_pred = cross_val_predict(rf, X, y_enc, cv=5)

    from sklearn.metrics import classification_report
    report = classification_report(y_enc, y_pred, target_names=classes, output_dict=True)

    log.info(f"  {'Type':>15}  {'Precision':>9}  {'Recall':>6}  {'F1':>6}  {'N':>6}")
    for cls in classes:
        r = report[cls]
        log.info(f"  {cls:>15}  {r['precision']:>9.3f}  {r['recall']:>6.3f}  {r['f1-score']:>6.3f}  {r['support']:>6.0f}")

    # ================================================================
    # 5. Residual analysis: which edges are HARDEST to predict?
    # ================================================================
    log.info("\n--- 5. HARDEST-TO-PREDICT EDGES ---")

    # Get prediction probabilities
    from sklearn.model_selection import cross_val_predict
    y_proba = cross_val_predict(rf, X, y_enc, cv=5, method='predict_proba')

    # For each edge, compute the confidence of the correct prediction
    confidences = y_proba[np.arange(len(y_enc)), y_enc]
    hardest_idx = np.argsort(confidences)[:20]

    log.info("20 hardest-to-classify edges (lowest correct-class probability):")
    for idx in hardest_idx:
        pred_class = classes[np.argmax(y_proba[idx])]
        true_class = y[idx]
        conf = confidences[idx]
        st, tt, sc, tc = edge_info[idx]
        log.info(f"  true={true_class}, pred={pred_class}, conf={conf:.3f}, "
                 f"{st}->{tt}, N={sc}->{tc}")

    # How many edges are "surprising" (correct class probability < 0.3)?
    n_surprising = np.sum(confidences < 0.3)
    log.info(f"\nEdges with confidence < 0.3: {n_surprising} ({100*n_surprising/len(confidences):.1f}%)")
    log.info("These are relationships that CANNOT be predicted from invariants.")
    log.info("They may encode deep mathematical structure.")

    duck.close()

    log.info(f"\n{'='*70}")
    log.info("CLASSIFICATION COMPLETE")
    log.info(f"{'='*70}")


if __name__ == "__main__":
    main()
