"""Regularised multinomial logistic probe and cross-validated cross-entropy (bits).

Held-out cross-entropy of a probe gives a LOWER bound on the information the features carry about the
label: I(X; Y) >= H(Y) - CE_heldout(Y | X). Conditional version: CE(Y|O) - CE(Y|S,O) estimates the
information in S beyond O (a lower bound only if both probes are well specified; the permutation null
calibrates the estimator's own bias).
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize


class Logit:
    def __init__(self, n_classes: int, l2: float = 1e-2, maxiter: int = 300):
        self.K = n_classes
        self.l2 = l2
        self.maxiter = maxiter

    def _prep(self, X):
        Z = (X - self.mu) / self.sd
        return np.hstack([Z, np.ones((len(Z), 1))])

    def fit(self, X: np.ndarray, y: np.ndarray) -> "Logit":
        X = np.asarray(X, float)
        self.mu = X.mean(0)
        sd = X.std(0)
        self.sd = np.where(sd > 1e-12, sd, 1.0)
        Z = self._prep(X)
        n, d = Z.shape
        Y = np.zeros((n, self.K))
        Y[np.arange(n), y] = 1.0
        l2 = self.l2

        def f(w):
            W = w.reshape(d, self.K)
            A = Z @ W
            A -= A.max(1, keepdims=True)
            P = np.exp(A)
            P /= P.sum(1, keepdims=True)
            loss = -np.sum(Y * np.log(np.clip(P, 1e-12, None))) / n + 0.5 * l2 * np.sum(W[:-1] ** 2)
            G = Z.T @ (P - Y) / n
            G[:-1] += l2 * W[:-1]
            return loss, G.ravel()

        res = minimize(f, np.zeros(d * self.K), jac=True, method="L-BFGS-B", options={"maxiter": self.maxiter})
        self.W = res.x.reshape(d, self.K)
        return self

    def proba(self, X: np.ndarray) -> np.ndarray:
        A = self._prep(np.asarray(X, float)) @ self.W
        A -= A.max(1, keepdims=True)
        P = np.exp(A)
        return P / P.sum(1, keepdims=True)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.proba(X).argmax(1)


def cv_ce_bits(X: np.ndarray, y: np.ndarray, K: int, folds: int = 5, seed: int = 0, l2: float = 1e-2) -> float:
    """Mean held-out cross-entropy in bits (5-fold)."""
    n = len(y)
    idx = np.random.default_rng(seed).permutation(n)
    parts = np.array_split(idx, folds)
    ll = 0.0
    for i in range(folds):
        te = parts[i]
        tr = np.concatenate([parts[j] for j in range(folds) if j != i])
        m = Logit(K, l2=l2).fit(X[tr], y[tr])
        p = m.proba(X[te])[np.arange(len(te)), y[te]]
        ll += -np.log2(np.clip(p, 1e-12, None)).sum()
    return ll / n
