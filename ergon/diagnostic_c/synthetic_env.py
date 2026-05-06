"""Synthetic ground-truth env for Ergon Learner v0.5 tire-kick (W3.1).

Clean env with a known linear latent rule on a polynomial-coefficient feature
space that is qualitatively similar to the 17-entry Lehmer boundary-layer
fixture (palindromic degree-14 polynomials, coefficients in [-5, 5], with
Mahler-style derived invariants).

Three locked acceptance criteria (Aporia 2026-05-05, locked into W3.1):

1. LSQ-baseline recoverability >85% on held-out clean data — closed-form
   numpy.linalg.lstsq on the same features used by the env recovers the
   binary latent label at >85% accuracy on the held-out split.

2. SNR in documented range — NOT at the modal-collapse boundary
   (modal_collapse_synthetic V3 used sigma=0.01, signal:noise ~ 10000:1
   yet REINFORCE/PPO collapsed). NOT trivially clean (the LSQ baseline
   should not be ~100%). Default SNR = 10 dB (signal_var / noise_var = 10),
   sitting on the elbow where >85% becomes achievable but actual learning
   is required (random-baseline = 50%).

3. Feature-space qualitative similarity to the 17-entry boundary-layer
   fixture — features are integer poly coefficients (palindromic deg-14,
   8 free coeffs) plus three Mahler-style invariants (height, nnz_free,
   mahler_proxy). The 17-entry fixture's `poly_coefficients`,
   `mahler_measure_dps*`, `n_irreducible_factors`,
   `cyclotomic_factor_indices` are real Lehmer invariants; this env's
   features are CHEAP polynomial-shape proxies designed to live in the
   same R^d neighborhood (integer-coefficient palindrome + scalar
   invariants), not to replicate the math. The latent rule predicts a
   scalar polynomial-property label given those features.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

import numpy as np


N_FREE_COEFFS: int = 8
DEGREE: int = 14
COEFF_RANGE: Tuple[int, int] = (-5, 5)
N_DERIVED: int = 3
N_FEATURES: int = N_FREE_COEFFS + N_DERIVED


@dataclass(frozen=True)
class SyntheticRecord:
    poly_coefficients: List[int]
    height: int
    nnz_free: int
    mahler_proxy: float
    label: int
    label_continuous: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "poly_coefficients": list(self.poly_coefficients),
            "height": int(self.height),
            "nnz_free": int(self.nnz_free),
            "mahler_proxy": float(self.mahler_proxy),
            "label": int(self.label),
            "label_continuous": float(self.label_continuous),
        }


@dataclass
class SyntheticCorpus:
    train: List[SyntheticRecord]
    heldout: List[SyntheticRecord]
    snr_db: float
    w_true: np.ndarray
    b_true: float
    feature_means: np.ndarray
    feature_stds: np.ndarray
    median_signal: float
    metadata: Dict[str, Any] = field(default_factory=dict)


def _build_palindrome(free_coeffs: np.ndarray) -> List[int]:
    full = np.empty(DEGREE + 1, dtype=int)
    for i in range(N_FREE_COEFFS):
        full[i] = int(free_coeffs[i])
        full[DEGREE - i] = int(free_coeffs[i])
    return full.tolist()


def _free_coeffs_block(rng: np.random.Generator, n: int) -> np.ndarray:
    lo, hi = COEFF_RANGE
    coeffs = rng.integers(lo, hi + 1, size=(n, N_FREE_COEFFS))
    bad = coeffs[:, 0] == 0
    while bad.any():
        coeffs[bad, 0] = rng.integers(lo, hi + 1, size=int(bad.sum()))
        bad = coeffs[:, 0] == 0
    return coeffs


def _features_from_free(coeffs_free: np.ndarray) -> np.ndarray:
    height = np.abs(coeffs_free).sum(axis=1).astype(float)
    nnz = (coeffs_free != 0).sum(axis=1).astype(float)
    mahler_proxy = np.log(1.0 + height / (1.0 + np.abs(coeffs_free[:, 0]).astype(float)))
    return np.column_stack([coeffs_free.astype(float), height, nnz, mahler_proxy])


def generate_synthetic_corpus(
    n_train: int = 1000,
    n_heldout: int = 200,
    snr_db: float = 10.0,
    seed: int = 42,
) -> Tuple[SyntheticCorpus, SyntheticCorpus]:
    if n_train < 20:
        raise ValueError(f"n_train must be >= 20; got {n_train}")
    if n_heldout < 10:
        raise ValueError(f"n_heldout must be >= 10; got {n_heldout}")

    rng = np.random.default_rng(seed)
    n_total = n_train + n_heldout
    coeffs_free = _free_coeffs_block(rng, n_total)
    X = _features_from_free(coeffs_free)

    mu = X.mean(axis=0)
    sd = X.std(axis=0) + 1e-12
    Xs = (X - mu) / sd

    truth_rng = np.random.default_rng(seed + 1)
    w_true = truth_rng.standard_normal(N_FEATURES)
    w_true /= np.linalg.norm(w_true)
    b_true = float(truth_rng.standard_normal())

    signal = Xs @ w_true + b_true
    signal_var = float(signal.var())
    snr_linear = 10.0 ** (snr_db / 10.0)
    noise_std = float(np.sqrt(signal_var / snr_linear))
    noise = rng.standard_normal(n_total) * noise_std
    y_cont = signal + noise
    median_signal = float(np.median(y_cont))
    label = (y_cont > median_signal).astype(int)

    records: List[SyntheticRecord] = []
    for i in range(n_total):
        records.append(SyntheticRecord(
            poly_coefficients=_build_palindrome(coeffs_free[i]),
            height=int(X[i, N_FREE_COEFFS]),
            nnz_free=int(X[i, N_FREE_COEFFS + 1]),
            mahler_proxy=float(X[i, N_FREE_COEFFS + 2]),
            label=int(label[i]),
            label_continuous=float(y_cont[i]),
        ))

    train_records = records[:n_train]
    heldout_records = records[n_train:]

    train_corpus = SyntheticCorpus(
        train=train_records,
        heldout=heldout_records,
        snr_db=float(snr_db),
        w_true=w_true,
        b_true=b_true,
        feature_means=mu,
        feature_stds=sd,
        median_signal=median_signal,
        metadata={
            "n_train": int(n_train),
            "n_heldout": int(n_heldout),
            "seed": int(seed),
            "n_features": int(N_FEATURES),
            "degree": int(DEGREE),
            "coeff_range": list(COEFF_RANGE),
            "palindromic": True,
        },
    )
    heldout_corpus = SyntheticCorpus(
        train=heldout_records,
        heldout=heldout_records,
        snr_db=float(snr_db),
        w_true=w_true,
        b_true=b_true,
        feature_means=mu,
        feature_stds=sd,
        median_signal=median_signal,
        metadata={"is_heldout_view": True},
    )
    return train_corpus, heldout_corpus


def _records_to_X_y(records: List[SyntheticRecord]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = len(records)
    coeffs_free = np.zeros((n, N_FREE_COEFFS), dtype=int)
    for i, r in enumerate(records):
        coeffs_free[i] = r.poly_coefficients[:N_FREE_COEFFS]
    X = _features_from_free(coeffs_free)
    y = np.array([r.label for r in records], dtype=int)
    y_cont = np.array([r.label_continuous for r in records], dtype=float)
    return X, y, y_cont


def _lsq_baseline_accuracy(corpus: SyntheticCorpus) -> float:
    Xtr, _, ytr_c = _records_to_X_y(corpus.train)
    Xte, yte, _ = _records_to_X_y(corpus.heldout)
    Xtr_s = (Xtr - corpus.feature_means) / corpus.feature_stds
    Xte_s = (Xte - corpus.feature_means) / corpus.feature_stds
    A_tr = np.column_stack([Xtr_s, np.ones(Xtr_s.shape[0])])
    sol, *_ = np.linalg.lstsq(A_tr, ytr_c - corpus.median_signal, rcond=None)
    A_te = np.column_stack([Xte_s, np.ones(Xte_s.shape[0])])
    pred = (A_te @ sol > 0).astype(int)
    return float((pred == yte).mean())


def _empirical_snr_db(corpus: SyntheticCorpus) -> float:
    Xtr, _, ytr_c = _records_to_X_y(corpus.train)
    Xtr_s = (Xtr - corpus.feature_means) / corpus.feature_stds
    signal = Xtr_s @ corpus.w_true + corpus.b_true
    residual = ytr_c - signal
    sig_var = float(signal.var())
    noise_var = float(residual.var()) + 1e-18
    return float(10.0 * np.log10(sig_var / noise_var))


_FEATURE_SPACE_CLAIM = (
    "Features are integer palindromic degree-14 polynomial coefficients "
    "(8 free in [-5,+5]) plus three Mahler-style derived invariants "
    "(height = sum |c_i|, nnz_free, mahler_proxy = log(1+height/(1+|c_0|))). "
    "Qualitatively similar to the 17-entry Lehmer boundary-layer fixture's "
    "poly_coefficients + mahler_measure_dps* + n_irreducible_factors shape, "
    "in the sense that the input is a polynomial-coefficient vector with "
    "scalar invariants (NOT arbitrary regression features). The latent "
    "rule is a linear functional of the standardized features thresholded "
    "at the empirical median, so a polynomial-property classifier."
)


def validate_acceptance_criteria(corpus: SyntheticCorpus) -> Dict[str, Any]:
    lsq_acc = _lsq_baseline_accuracy(corpus)
    emp_snr = _empirical_snr_db(corpus)
    return {
        "lsq_baseline_accuracy": float(lsq_acc),
        "snr_db": float(emp_snr),
        "snr_db_requested": float(corpus.snr_db),
        "feature_space_similarity": _FEATURE_SPACE_CLAIM,
        "criterion_1_pass": bool(lsq_acc > 0.85),
        "criterion_2_pass": bool(5.0 <= emp_snr <= 20.0),
        "criterion_3_pass": True,
        "all_pass": bool(lsq_acc > 0.85 and 5.0 <= emp_snr <= 20.0),
    }


__all__ = [
    "DEGREE",
    "COEFF_RANGE",
    "N_FREE_COEFFS",
    "N_FEATURES",
    "SyntheticRecord",
    "SyntheticCorpus",
    "generate_synthetic_corpus",
    "validate_acceptance_criteria",
]
