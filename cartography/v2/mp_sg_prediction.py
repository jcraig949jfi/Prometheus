"""
Materials Project: Predict Space Group from Physical Properties
===============================================================
Can a random forest predict spacegroup_number (230 classes, 96 observed)
and crystal_system (7 classes) from band_gap, density, volume, nsites,
formation_energy_per_atom?

Approach:
  1. Load MP 10K sample
  2. Features: [band_gap, density, volume, nsites, formation_energy_per_atom, crystal_system_encoded]
  3. Target A: spacegroup_number (multi-class, many rare)
  4. Target B: crystal_system (7 classes — should be easier)
  5. Random forest with 5-fold stratified CV
  6. Accuracy vs majority baseline
  7. Feature importance
  8. Confusion matrix highlights (top confused pairs)
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold

DATA_PATH = Path(__file__).parent.parent / "physics" / "data" / "materials_project_10k.json"
OUT_PATH = Path(__file__).parent / "mp_sg_prediction_results.json"


def main():
    print("Loading data...")
    with open(DATA_PATH) as f:
        raw = json.load(f)
    print(f"  {len(raw)} records loaded")

    # Encode crystal system
    cs_list = sorted(set(r['crystal_system'] for r in raw))
    cs_map = {c: i for i, c in enumerate(cs_list)}
    print(f"  Crystal systems ({len(cs_list)}): {cs_list}")

    # Build feature matrix and targets
    feature_names = ['band_gap', 'density', 'volume', 'nsites', 'formation_energy_per_atom', 'crystal_system_enc']
    X_rows, sg_labels, cs_labels = [], [], []
    for r in raw:
        X_rows.append([
            r['band_gap'], r['density'], r['volume'],
            r['nsites'], r['formation_energy_per_atom'],
            cs_map[r['crystal_system']]
        ])
        sg_labels.append(r['spacegroup_number'])
        cs_labels.append(cs_map[r['crystal_system']])

    X = np.array(X_rows, dtype=np.float64)
    y_cs = np.array(cs_labels)

    # Remap spacegroup numbers to contiguous 0..N-1
    sg_uniq = sorted(set(sg_labels))
    sg_remap = {s: i for i, s in enumerate(sg_uniq)}
    sg_inv = {i: s for s, i in sg_remap.items()}
    y_sg = np.array([sg_remap[s] for s in sg_labels])

    n_sg_classes = len(sg_uniq)
    n_cs_classes = len(cs_list)
    print(f"  {n_sg_classes} unique space groups, {n_cs_classes} crystal systems")

    sg_counts = Counter(sg_labels)
    cs_counts = Counter(r['crystal_system'] for r in raw)
    majority_sg = sg_counts.most_common(1)[0]
    majority_cs = cs_counts.most_common(1)[0]
    print(f"  Majority SG: {majority_sg[0]} ({majority_sg[1]} / {len(raw)} = {majority_sg[1]/len(raw):.3f})")
    print(f"  Majority CS: {majority_cs[0]} ({majority_cs[1]} / {len(raw)} = {majority_cs[1]/len(raw):.3f})")

    results = {
        'experiment': 'mp_sg_prediction',
        'description': 'Random forest prediction of spacegroup_number and crystal_system from physical properties',
        'n_records': len(raw),
        'features': feature_names,
        'n_spacegroups': n_sg_classes,
        'n_crystal_systems': n_cs_classes,
        'majority_sg': {'sg': majority_sg[0], 'count': majority_sg[1], 'baseline_acc': round(majority_sg[1] / len(raw), 4)},
        'majority_cs': {'cs': majority_cs[0], 'count': majority_cs[1], 'baseline_acc': round(majority_cs[1] / len(raw), 4)},
        'sg_distribution_top20': [{'sg': sg, 'count': c} for sg, c in sg_counts.most_common(20)],
        'cs_distribution': [{'cs': cs, 'count': cs_counts[cs]} for cs in cs_list],
    }

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # -----------------------------------------------------------------------
    # Task 1: Crystal system prediction (7 classes, no crystal_system feature)
    # -----------------------------------------------------------------------
    print("\n=== Task 1: Crystal System Prediction (7 classes) ===")
    X_cs = X[:, :5]
    cs_feature_names = feature_names[:5]

    fold_accs_cs = []
    all_preds_cs = np.zeros(len(y_cs), dtype=int)
    importances_cs = np.zeros(5)

    for fold_i, (train_idx, test_idx) in enumerate(skf.split(X_cs, y_cs)):
        rf = RandomForestClassifier(n_estimators=200, max_depth=25, min_samples_leaf=3,
                                     random_state=42, n_jobs=-1)
        rf.fit(X_cs[train_idx], y_cs[train_idx])
        preds = rf.predict(X_cs[test_idx])
        all_preds_cs[test_idx] = preds
        acc = (preds == y_cs[test_idx]).mean()
        fold_accs_cs.append(acc)
        importances_cs += rf.feature_importances_
        print(f"  Fold {fold_i+1}: acc={acc:.4f}")

    importances_cs /= 5
    mean_acc_cs = np.mean(fold_accs_cs)
    std_acc_cs = np.std(fold_accs_cs)
    print(f"  Mean accuracy: {mean_acc_cs:.4f} +/- {std_acc_cs:.4f}")
    print(f"  Majority baseline: {majority_cs[1]/len(raw):.4f}")
    print(f"  Lift over baseline: {mean_acc_cs / (majority_cs[1]/len(raw)):.2f}x")

    # Confusion matrix for CS
    cs_confusion = np.zeros((n_cs_classes, n_cs_classes), dtype=int)
    for true, pred in zip(y_cs, all_preds_cs):
        cs_confusion[true, pred] += 1

    cs_confused = []
    for i in range(n_cs_classes):
        for j in range(n_cs_classes):
            if i != j and cs_confusion[i, j] > 0:
                cs_confused.append({
                    'true': cs_list[i], 'predicted': cs_list[j],
                    'count': int(cs_confusion[i, j]),
                    'pct_of_true': round(cs_confusion[i, j] / max(1, cs_confusion[i].sum()), 4)
                })
    cs_confused.sort(key=lambda x: -x['count'])

    cs_per_class = []
    for i in range(n_cs_classes):
        total = cs_confusion[i].sum()
        correct = cs_confusion[i, i]
        cs_per_class.append({
            'class': cs_list[i],
            'total': int(total),
            'correct': int(correct),
            'accuracy': round(correct / max(1, total), 4)
        })

    cs_feat_imp = sorted(
        [{'feature': cs_feature_names[i], 'importance': round(float(importances_cs[i]), 4)} for i in range(5)],
        key=lambda x: -x['importance']
    )

    results['crystal_system_prediction'] = {
        'task': 'predict crystal_system from [band_gap, density, volume, nsites, formation_energy]',
        'n_folds': 5,
        'fold_accuracies': [round(a, 4) for a in fold_accs_cs],
        'mean_accuracy': round(mean_acc_cs, 4),
        'std_accuracy': round(std_acc_cs, 4),
        'majority_baseline': round(majority_cs[1] / len(raw), 4),
        'lift_over_baseline': round(mean_acc_cs / (majority_cs[1] / len(raw)), 2),
        'feature_importance': cs_feat_imp,
        'per_class_accuracy': cs_per_class,
        'top_confused_pairs': cs_confused[:15],
        'confusion_matrix': cs_confusion.tolist(),
        'class_labels': cs_list,
    }

    # -----------------------------------------------------------------------
    # Task 2: Space group prediction (96 classes, include crystal_system)
    # -----------------------------------------------------------------------
    print("\n=== Task 2: Space Group Prediction (96 classes) ===")
    fold_accs_sg = []
    all_preds_sg = np.zeros(len(y_sg), dtype=int)
    all_proba_sg = np.zeros((len(y_sg), n_sg_classes))
    importances_sg = np.zeros(6)

    for fold_i, (train_idx, test_idx) in enumerate(skf.split(X, y_sg)):
        rf = RandomForestClassifier(n_estimators=200, max_depth=30, min_samples_leaf=2,
                                     random_state=42, n_jobs=-1)
        rf.fit(X[train_idx], y_sg[train_idx])
        preds = rf.predict(X[test_idx])
        proba = rf.predict_proba(X[test_idx])
        all_preds_sg[test_idx] = preds
        # Map probabilities to full class array (RF may not see all classes in each fold)
        for ci, cls in enumerate(rf.classes_):
            all_proba_sg[test_idx, cls] = proba[:, ci]
        acc = (preds == y_sg[test_idx]).mean()
        fold_accs_sg.append(acc)
        importances_sg += rf.feature_importances_
        print(f"  Fold {fold_i+1}: acc={acc:.4f}")

    importances_sg /= 5
    mean_acc_sg = np.mean(fold_accs_sg)
    std_acc_sg = np.std(fold_accs_sg)
    print(f"  Mean accuracy: {mean_acc_sg:.4f} +/- {std_acc_sg:.4f}")
    print(f"  Majority baseline: {majority_sg[1]/len(raw):.4f}")
    print(f"  Lift over baseline: {mean_acc_sg / (majority_sg[1]/len(raw)):.2f}x")

    # Top-5 accuracy from stored probabilities
    top5_correct = 0
    for i in range(len(y_sg)):
        top5 = np.argsort(all_proba_sg[i])[-5:]
        if y_sg[i] in top5:
            top5_correct += 1
    top5_acc = top5_correct / len(y_sg)
    print(f"  Top-5 accuracy: {top5_acc:.4f}")

    # Confusion highlights for SG
    sg_confusion = np.zeros((n_sg_classes, n_sg_classes), dtype=int)
    for true, pred in zip(y_sg, all_preds_sg):
        sg_confusion[true, pred] += 1

    sg_confused = []
    for i in range(n_sg_classes):
        for j in range(n_sg_classes):
            if i != j and sg_confusion[i, j] > 0:
                sg_confused.append({
                    'true_sg': int(sg_inv[i]), 'predicted_sg': int(sg_inv[j]),
                    'count': int(sg_confusion[i, j]),
                    'pct_of_true': round(sg_confusion[i, j] / max(1, sg_confusion[i].sum()), 4)
                })
    sg_confused.sort(key=lambda x: -x['count'])

    sg_per_class = []
    for sg_num, cnt in sg_counts.most_common(20):
        i = sg_remap[sg_num]
        total = sg_confusion[i].sum()
        correct = sg_confusion[i, i]
        sg_per_class.append({
            'spacegroup': sg_num,
            'total': int(total),
            'correct': int(correct),
            'accuracy': round(correct / max(1, total), 4)
        })

    sg_feat_imp = sorted(
        [{'feature': feature_names[i], 'importance': round(float(importances_sg[i]), 4)} for i in range(6)],
        key=lambda x: -x['importance']
    )

    results['spacegroup_prediction'] = {
        'task': 'predict spacegroup_number from [band_gap, density, volume, nsites, formation_energy, crystal_system_enc]',
        'n_classes': n_sg_classes,
        'n_folds': 5,
        'fold_accuracies': [round(a, 4) for a in fold_accs_sg],
        'mean_accuracy': round(mean_acc_sg, 4),
        'std_accuracy': round(std_acc_sg, 4),
        'top5_accuracy': round(top5_acc, 4),
        'majority_baseline': round(majority_sg[1] / len(raw), 4),
        'lift_over_baseline': round(mean_acc_sg / (majority_sg[1] / len(raw)), 2),
        'feature_importance': sg_feat_imp,
        'per_class_accuracy_top20': sg_per_class,
        'top_confused_pairs': sg_confused[:20],
    }

    # -----------------------------------------------------------------------
    # Task 3: Space group prediction WITHOUT crystal_system (pure physics)
    # -----------------------------------------------------------------------
    print("\n=== Task 3: Space Group from Pure Physics (no crystal_system) ===")
    X_pure = X[:, :5]
    fold_accs_pure = []
    for fold_i, (train_idx, test_idx) in enumerate(skf.split(X_pure, y_sg)):
        rf = RandomForestClassifier(n_estimators=200, max_depth=30, min_samples_leaf=2,
                                     random_state=42, n_jobs=-1)
        rf.fit(X_pure[train_idx], y_sg[train_idx])
        preds = rf.predict(X_pure[test_idx])
        acc = (preds == y_sg[test_idx]).mean()
        fold_accs_pure.append(acc)
        print(f"  Fold {fold_i+1}: acc={acc:.4f}")

    mean_acc_pure = np.mean(fold_accs_pure)
    std_acc_pure = np.std(fold_accs_pure)
    print(f"  Mean accuracy: {mean_acc_pure:.4f} +/- {std_acc_pure:.4f}")
    print(f"  Crystal system feature adds: {mean_acc_sg - mean_acc_pure:+.4f}")

    results['spacegroup_pure_physics'] = {
        'task': 'predict spacegroup_number from [band_gap, density, volume, nsites, formation_energy] only',
        'fold_accuracies': [round(a, 4) for a in fold_accs_pure],
        'mean_accuracy': round(mean_acc_pure, 4),
        'std_accuracy': round(std_acc_pure, 4),
        'crystal_system_feature_lift': round(mean_acc_sg - mean_acc_pure, 4),
    }

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    results['summary'] = {
        'crystal_system_accuracy': round(mean_acc_cs, 4),
        'crystal_system_baseline': round(majority_cs[1] / len(raw), 4),
        'spacegroup_accuracy': round(mean_acc_sg, 4),
        'spacegroup_top5_accuracy': round(top5_acc, 4),
        'spacegroup_baseline': round(majority_sg[1] / len(raw), 4),
        'spacegroup_pure_accuracy': round(mean_acc_pure, 4),
        'conclusion': (
            f"Crystal system: {mean_acc_cs:.1%} vs {majority_cs[1]/len(raw):.1%} baseline ({mean_acc_cs/(majority_cs[1]/len(raw)):.1f}x lift). "
            f"Space group: {mean_acc_sg:.1%} top-1 / {top5_acc:.1%} top-5 vs {majority_sg[1]/len(raw):.1%} baseline. "
            f"Crystal system encoding adds {mean_acc_sg - mean_acc_pure:+.1%} to SG prediction. "
            f"Physical properties carry substantial but incomplete symmetry information."
        )
    }

    print(f"\n=== Summary ===")
    print(results['summary']['conclusion'])

    with open(OUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == '__main__':
    main()
