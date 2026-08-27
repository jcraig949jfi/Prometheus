"""Frozen mutation-source identifiability classifier (PRIV-1).

Deterministic multinomial softmax regression (numpy, full-batch GD, fixed
hyperparameters, fixed seed). Train/test split grouped by parent so the
classifier cannot memorize a parent's neighborhood.

Protocol frozen before any real-substrate run:
- rows: NON-IDENTITY transitions (child pkey != parent pkey) from viable
  parents, single-parent menu operators only (crossover excluded: different
  parent structure)
- features: substrate disp_features (behavioral displacement only)
- split: 70/30 by hash of parent index
- report: accuracy, Wilson 95% CI, chance level (majority class share in
  test), full confusion matrix, per-class recall
"""
from __future__ import annotations

import numpy as np

EPOCHS = 300
LR = 0.5
L2 = 1e-4
SEED = 7700


def wilson_ci(k: int, n: int, z: float = 1.96):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (float(center - half), float(center + half))


def fit_softmax(X: np.ndarray, y: np.ndarray, n_classes: int) -> np.ndarray:
    rng = np.random.default_rng(SEED)
    n, d = X.shape
    W = rng.normal(0, 0.01, size=(d, n_classes))
    Y = np.zeros((n, n_classes))
    Y[np.arange(n), y] = 1.0
    for _ in range(EPOCHS):
        logits = X @ W
        logits -= logits.max(axis=1, keepdims=True)
        P = np.exp(logits)
        P /= P.sum(axis=1, keepdims=True)
        grad = X.T @ (P - Y) / n + L2 * W
        W -= LR * grad
    return W


def identifiability(features: np.ndarray, ops: np.ndarray, parent_idx: np.ndarray,
                    n_classes: int, min_test: int = 300) -> dict:
    """features: (n, d) displacement features; ops: (n,) labels;
    parent_idx: (n,) grouping key."""
    n = features.shape[0]
    if n < 4 * min_test:
        return {"status": "INSUFFICIENT_DATA", "n": int(n)}
    # grouped split: deterministic hash of parent index
    grp = (parent_idx * 2654435761 % 2**32) % 10
    test_mask = grp >= 7
    Xtr, ytr = features[~test_mask], ops[~test_mask]
    Xte, yte = features[test_mask], ops[test_mask]
    if len(yte) < min_test or len(np.unique(ytr)) < 2:
        return {"status": "INSUFFICIENT_DATA", "n": int(n), "n_test": int(len(yte))}
    mu, sd = Xtr.mean(axis=0), Xtr.std(axis=0)
    sd[sd < 1e-12] = 1.0
    Xtr = np.hstack([(Xtr - mu) / sd, np.ones((len(Xtr), 1))])
    Xte = np.hstack([(Xte - mu) / sd, np.ones((len(Xte), 1))])
    W = fit_softmax(Xtr, ytr, n_classes)
    pred = np.argmax(Xte @ W, axis=1)
    acc = float(np.mean(pred == yte))
    lo, hi = wilson_ci(int(np.sum(pred == yte)), len(yte))
    conf = np.zeros((n_classes, n_classes), dtype=int)
    for t, p in zip(yte, pred):
        conf[t, p] += 1
    class_counts = np.bincount(yte, minlength=n_classes)
    chance = float(class_counts.max() / class_counts.sum())
    recalls = [float(conf[c, c] / class_counts[c]) if class_counts[c] else None
               for c in range(n_classes)]
    return {
        "status": "OK", "n_train": int(len(ytr)), "n_test": int(len(yte)),
        "accuracy": acc, "ci95": [lo, hi], "chance": chance,
        "confusion": conf.tolist(), "per_class_recall": recalls,
    }
