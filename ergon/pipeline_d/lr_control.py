"""W4.7 — logistic-regression trivial-feature control (third R14 defense).

Per Aporia 2026-05-05 review. Trains logistic regression on raw
poly_coefficients only — no LoRA, no embedding, no derived features —
on the same train/held-out split as W4.1. If LoRA accuracy ≈ LR accuracy,
LoRA learned only the trivial polynomial-coefficient feature.

Substrate-grade equivalent of W4.0's null gate at a different layer:
  W4.0 catches "did it learn anything?" (label-shuffle)
  W4.7 catches "did it learn more than the trivial feature?"

Outputs: ergon/pipeline_d/runs/lr_control/lr_control_results.json
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder

from ergon.pipeline_d.boundary_layer_fixture import (
    load_17_entry_fixture,
    load_heldout_fixture,
)


def run_lr_control() -> Dict[str, Any]:
    train = load_17_entry_fixture()
    heldout, _ = load_heldout_fixture()

    X_train = np.array([r.poly_coefficients for r in train], dtype=np.float64)
    X_eval = np.array([r.poly_coefficients for r in heldout], dtype=np.float64)

    results: Dict[str, Any] = {}

    for label_field in ("cls_post_fold", "cls"):
        y_train_raw = [getattr(r, label_field) for r in train]
        y_eval_raw = [getattr(r, label_field) for r in heldout]

        le = LabelEncoder()
        y_train = le.fit_transform(y_train_raw)
        try:
            y_eval = le.transform(y_eval_raw)
        except ValueError:
            unseen = set(y_eval_raw) - set(le.classes_)
            le2 = LabelEncoder()
            le2.fit(list(le.classes_) + list(unseen))
            y_train = le2.transform(y_train_raw)
            y_eval = le2.transform(y_eval_raw)
            le = le2

        clf = LogisticRegression(
            penalty="l2",
            C=1.0,
            solver="lbfgs",
            max_iter=2000,
            random_state=42,
        )
        clf.fit(X_train, y_train)

        train_acc = float(clf.score(X_train, y_train))
        eval_acc = float(clf.score(X_eval, y_eval))

        n_total = len(y_eval)
        n_correct = int(round(eval_acc * n_total))

        majority_class = max(set(y_eval_raw), key=y_eval_raw.count)
        majority_count = sum(1 for y in y_eval_raw if y == majority_class)
        majority_rate = majority_count / n_total if n_total > 0 else 0.0

        per_class = {}
        for c in sorted(set(y_eval_raw)):
            idx = [i for i, y in enumerate(y_eval_raw) if y == c]
            if idx:
                preds = clf.predict(X_eval[idx])
                gold = le.transform([c] * len(idx))
                per_class[c] = float(np.mean(preds == gold))

        results[label_field] = {
            "train_accuracy": train_acc,
            "heldout_accuracy": eval_acc,
            "n_correct": n_correct,
            "n_total": n_total,
            "per_class_heldout_accuracy": per_class,
            "majority_class": str(majority_class),
            "majority_class_rate": majority_rate,
            "n_features": int(X_train.shape[1]),
            "n_train": int(X_train.shape[0]),
            "classes_seen": le.classes_.tolist(),
        }

    out_path = Path("ergon/pipeline_d/runs/lr_control/lr_control_results.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)

    return results


def _print_summary(results: Dict[str, Any]) -> None:
    print("\n=== W4.7 LOGISTIC-REGRESSION TRIVIAL-FEATURE CONTROL ===")
    for label_field, block in results.items():
        print(f"\n[{label_field}]")
        print(f"  train_acc = {block['train_accuracy']:.3f}")
        print(f"  heldout_acc = {block['heldout_accuracy']:.3f} ({block['n_correct']}/{block['n_total']})")
        print(f"  majority_class = '{block['majority_class']}' @ {block['majority_class_rate']:.3f}")
        print(f"  per_class_heldout = {block['per_class_heldout_accuracy']}")
        print(f"  n_features={block['n_features']}, n_train={block['n_train']}")


if __name__ == "__main__":
    res = run_lr_control()
    _print_summary(res)
    print(f"\nWrote: ergon/pipeline_d/runs/lr_control/lr_control_results.json")
