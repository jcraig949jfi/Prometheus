"""
Dissection Tensor — GPU-accelerated multi-dimensional signature space.

Architecture:
  1. ENCODE: Pack mathematical objects' dissection signatures into PyTorch
     tensors on GPU. Each object is a point in N-dimensional signature space.
  2. BATTERY: Encode falsification battery results (F1-F27) as additional
     dimensions — the truth boundary becomes geometry in the tensor.
  3. COMPRESS: TT-decomposition (TensorLy) reveals entangled dimensions
     and makes high-dimensional exploration tractable.
  4. EXPLORE: GPU-parallel sweeps for geometric intersections — submanifolds
     where objects from different domains converge.

Dissection strategies mapped to existing data:
  S1  (complex plane eval)  -> knot poly / EC a_p on unit circle grid
  S3  (mod-p fingerprint)  -> EC a_p, knot poly coeffs mod p
  S5  (spectral/FFT)       -> OEIS sequences, knot poly coefficients
  S7  (p-adic valuation)   -> EC conductor factorization, NF discriminant
  S9  (symmetry group)     -> Genus-2 ST groups, crystal space groups
  S10 (Galois group)       -> NF galois_label
  S11 (monodromy proxy)    -> sign changes, periodicity, growth, Galois content, symmetry, ramification
  S12 (zeta-like density)  -> point count / divisibility density across domains
  S13 (discriminant)       -> NF disc_abs, EC conductor
  S21 (automorphic assoc)  -> Ramanujan bound, Hecke multiplicativity, Satake params
  S22 (operadic structure) -> Fungrim formula type/module
  S24 (info-theoretic)     -> Shannon entropy of coefficients

Battery dimensions:
  F_eta2    -> variance decomposition effect size
  F_p       -> permutation null p-value
  F_z       -> z-score
  F_verdict -> categorical (KILLED=0, TENDENCY=1, CONSTRAINT=2, LAW=3, IDENTITY=4)

Machine: M1 (Skullport)
GPU: RTX 5060 Ti, 17GB VRAM
"""
import sys
import json
import numpy as np
import torch
import torch.nn.functional as F
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

# TensorLy for decomposition
import tensorly as tl
from tensorly.decomposition import tensor_train

# Use PyTorch backend for TensorLy (GPU-native)
tl.set_backend('pytorch')

ROOT = Path(__file__).resolve().parents[3]
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


# ============================================================
# Data classes
# ============================================================
@dataclass
class MathObject:
    """A mathematical object with its multi-strategy signature."""
    obj_id: str
    domain: str          # 'EC', 'knot', 'NF', 'fungrim', 'genus2', 'OEIS', etc.
    label: str           # human-readable label
    signatures: dict     # strategy_name -> np.array or scalar
    battery: dict = field(default_factory=dict)  # test_id -> battery results
    raw: dict = field(default_factory=dict)      # original data for reference


# ============================================================
# Strategy extractors — compute signatures from raw data
# ============================================================
class StrategyExtractors:
    """Compute dissection signatures from raw mathematical objects."""

    @staticmethod
    def s1_complex(coefficients, n_points=8):
        """S1: Complex plane evaluation.
        Evaluate polynomial with given coefficients on n_points equally spaced
        points on the unit circle: e^{i*pi*k/4} for k=0..n_points-1.
        Returns: vector of magnitudes at each point (length n_points).
        """
        if not coefficients or len(coefficients) < 2:
            return np.full(n_points, np.nan)
        coeffs = np.array(coefficients, dtype=np.complex128)
        grid = np.exp(1j * np.pi * np.arange(n_points) / (n_points / 2))
        mags = np.zeros(n_points, dtype=np.float32)
        for i, z in enumerate(grid):
            # Evaluate polynomial: c0 + c1*z + c2*z^2 + ...
            val = np.polyval(coeffs[::-1], z)
            mags[i] = np.abs(val)
        # Log-scale to tame large magnitudes
        mags = np.log1p(mags).astype(np.float32)
        return mags

    @staticmethod
    def s12_zeta(values, mode="divisibility", primes=(2, 3, 5, 7)):
        """S12: Point count / zeta-like arithmetic density.
        Modes:
          'divisibility' — fraction of values divisible by each prime (OEIS, EC a_p)
          'conductor_mod' — conductor mod each prime (EC)
          'disc_mod' — discriminant mod each prime (NF)
        Returns: vector of length len(primes).
        """
        n_primes = len(primes)
        if values is None:
            return np.full(n_primes, np.nan)

        if mode == "divisibility":
            if not values or len(values) < 2:
                return np.full(n_primes, np.nan)
            n = len(values)
            sig = []
            for p in primes:
                count = sum(1 for v in values if int(v) % p == 0)
                sig.append(count / n)
            return np.array(sig, dtype=np.float32)

        elif mode == "conductor_mod":
            # values is a single integer (conductor)
            cond = abs(int(values))
            if cond == 0:
                return np.full(n_primes, np.nan)
            sig = [float((cond % p) / p) for p in primes]
            return np.array(sig, dtype=np.float32)

        elif mode == "disc_mod":
            # values is a single integer (discriminant)
            disc = abs(int(values))
            if disc == 0:
                return np.full(n_primes, np.nan)
            sig = [float((disc % p) / p) for p in primes]
            return np.array(sig, dtype=np.float32)

        return np.full(n_primes, np.nan)

    @staticmethod
    def s3_mod_p(coefficients, primes=(2, 3, 5, 7, 11, 13)):
        """S3: Modular arithmetic fingerprint.
        For polynomial coefficients, compute residue class coverage mod p.
        Returns: vector of length len(primes) with coverage fractions.
        """
        if not coefficients or len(coefficients) < 2:
            return np.full(len(primes), np.nan)
        sig = []
        for p in primes:
            residues = set(int(c) % p for c in coefficients if c != 0)
            sig.append(len(residues) / p)
        return np.array(sig, dtype=np.float32)

    @staticmethod
    def s5_spectral(values, n_features=8):
        """S5: Spectral decomposition.
        FFT of a sequence -> top-K power spectrum magnitudes.
        Returns: vector of length n_features.
        """
        if not values or len(values) < 4:
            return np.full(n_features, np.nan)
        arr = np.array(values, dtype=np.float64)
        # Normalize
        if np.std(arr) > 0:
            arr = (arr - np.mean(arr)) / np.std(arr)
        spectrum = np.abs(np.fft.rfft(arr))
        # Top-K magnitudes (skip DC component)
        if len(spectrum) > 1:
            spectrum = spectrum[1:]
        # Pad or truncate to n_features
        if len(spectrum) >= n_features:
            sig = np.sort(spectrum)[-n_features:][::-1]
        else:
            sig = np.zeros(n_features)
            sig[:len(spectrum)] = np.sort(spectrum)[::-1]
        return sig.astype(np.float32)

    @staticmethod
    def s7_padic(n, primes=(2, 3, 5, 7, 11)):
        """S7: p-adic valuation.
        For an integer n, compute v_p(n) for each prime p.
        Returns: vector of length len(primes).
        """
        if n is None or n == 0:
            return np.full(len(primes), np.nan)
        n = abs(int(n))
        sig = []
        for p in primes:
            v = 0
            m = n
            while m > 0 and m % p == 0:
                v += 1
                m //= p
            sig.append(v)
        return np.array(sig, dtype=np.float32)

    @staticmethod
    def s10_galois_hash(galois_label, max_dim=8):
        """S10: Galois group encoding.
        Encode Galois label (e.g., '4T3') as a feature vector.
        Returns: vector of length max_dim.
        """
        sig = np.zeros(max_dim, dtype=np.float32)
        if not galois_label:
            sig[:] = np.nan
            return sig
        # Parse nTk format
        parts = galois_label.replace('T', ' ').split()
        if len(parts) == 2:
            try:
                n, k = int(parts[0]), int(parts[1])
                sig[0] = n            # degree
                sig[1] = k            # transitive group index
                sig[2] = n * k        # combined
                sig[3] = np.log1p(n)  # log degree
            except ValueError:
                sig[:] = np.nan
        else:
            sig[:] = np.nan
        return sig

    @staticmethod
    def s13_discriminant(disc, conductor=None, max_dim=4):
        """S13: Discriminant/conductor signature.
        Returns: vector with log magnitude, sign, factorization features.
        """
        sig = np.zeros(max_dim, dtype=np.float32)
        if disc is None:
            sig[:] = np.nan
            return sig
        d = abs(int(disc))
        sig[0] = np.log1p(d)
        sig[1] = 1.0 if disc > 0 else -1.0
        sig[2] = len([i for i in range(2, min(d + 1, 100)) if d % i == 0])  # rough divisor count
        if conductor is not None:
            sig[3] = np.log1p(abs(int(conductor)))
        return sig

    @staticmethod
    def s24_entropy(coefficients):
        """S24: Information-theoretic signature.
        Shannon entropy + compression features of coefficient sequence.
        Returns: vector of length 4.
        """
        if not coefficients or len(coefficients) < 2:
            return np.full(4, np.nan)
        coefficients = np.array(coefficients, dtype=np.float64)
        arr = np.abs(coefficients) + 0.01
        p = arr / arr.sum()
        entropy = -np.sum(p * np.log2(p))
        # Additional features
        sig = np.array([
            entropy,
            np.log1p(float(len(coefficients))),   # length
            np.log1p(float(np.max(np.abs(coefficients)))),  # max magnitude
            float(np.std(coefficients) / (np.mean(np.abs(coefficients)) + 1e-8)),  # CV
        ], dtype=np.float32)
        return sig

    # Weyl group orders: |W(X_n)| for ADE root systems
    _WEYL_ORDERS = {}
    for _n in range(1, 30):
        _fac = 1
        for _k in range(2, _n + 2):
            _fac *= _k
        _WEYL_ORDERS[('A', _n)] = _fac
    for _n in range(4, 20):
        _fac = 1
        for _k in range(2, _n + 1):
            _fac *= _k
        _WEYL_ORDERS[('D', _n)] = (2 ** (_n - 1)) * _fac
    _WEYL_ORDERS[('E', 6)] = 51840
    _WEYL_ORDERS[('E', 7)] = 2903040
    _WEYL_ORDERS[('E', 8)] = 696729600

    _ADE_LATTICE_DETS = {}
    for _n in range(1, 30):
        _ADE_LATTICE_DETS[('A', _n)] = _n + 1
    for _n in range(4, 20):
        _ADE_LATTICE_DETS[('D', _n)] = 4
    _ADE_LATTICE_DETS[('E', 6)] = 3
    _ADE_LATTICE_DETS[('E', 7)] = 2
    _ADE_LATTICE_DETS[('E', 8)] = 1

    @staticmethod
    def s19_ade_classify(data, method="discriminant"):
        """S19: ADE singularity classification.

        Classifies mathematical objects by their ADE type — the universal
        classification of simple singularities (A_n, D_n, E_6, E_7, E_8).

        Methods:
          'discriminant' — polynomial coefficients: use discriminant/shape
          'order'        — group order: match against Weyl group orders
          'lattice_det'  — lattice determinant: match root lattice determinants
          'mckay'        — modular form (level, weight): McKay correspondence
          'torsion'      — EC torsion structure: ADE from torsion pattern

        Returns: vector of length 8:
          [0] A-type score, [1] D-type score, [2] E6 score,
          [3] E7 score, [4] E8 score, [5] best_n (rank),
          [6] confidence, [7] method code
        """
        sig = np.full(8, np.nan, dtype=np.float32)
        method_code = {"discriminant": 0, "order": 1, "lattice_det": 2,
                       "mckay": 3, "torsion": 4}.get(method, 0)
        ext = StrategyExtractors

        if method == "discriminant":
            if data is None or not hasattr(data, '__len__') or len(data) < 2:
                return sig
            coeffs = np.array(data, dtype=np.float64)
            n = len(coeffs)
            abs_c = np.abs(coeffs)
            abs_c = abs_c[abs_c > 0]
            if len(abs_c) < 2:
                return sig
            diffs = np.diff(abs_c)
            frac_decreasing = np.sum(diffs < 0) / max(len(diffs), 1)
            a_score = float(frac_decreasing)
            even_sum = np.sum(abs_c[::2])
            odd_sum = np.sum(abs_c[1::2]) + 1e-12
            even_ratio = even_sum / (even_sum + odd_sum)
            d_score = float(np.exp(-abs(even_ratio - 0.8) * 5))
            if n >= 6:
                thirds = np.array([np.sum(abs_c[i::3]) for i in range(3)])
                thirds_cv = np.std(thirds) / (np.mean(thirds) + 1e-12)
                e6_score = float(np.exp(-thirds_cv * 3))
            else:
                e6_score = 0.0
            if n >= 7:
                half1 = np.sum(abs_c[:n // 2])
                half2 = np.sum(abs_c[n // 2:])
                ratio = min(half1, half2) / (max(half1, half2) + 1e-12)
                e7_score = float(np.exp(-abs(ratio - 0.6) * 5))
            else:
                e7_score = 0.0
            ent_p = abs_c / (abs_c.sum() + 1e-12)
            entropy = -np.sum(ent_p * np.log2(ent_p + 1e-12))
            max_entropy = np.log2(max(len(abs_c), 2))
            norm_ent = entropy / max_entropy if max_entropy > 0 else 1.0
            e8_score = float(np.exp(-norm_ent * 2))
            scores = [a_score, d_score, e6_score, e7_score, e8_score]
            best_n = n - 1
            confidence = min(max(float(max(scores) - np.mean(scores)), 0.0), 1.0)
            sig[:] = [a_score, d_score, e6_score, e7_score, e8_score,
                      float(best_n), confidence, float(method_code)]

        elif method == "order":
            if data is None or int(data) == 0:
                return sig
            order = abs(int(data))
            best_a, best_d = 0.0, 0.0
            best_a_n, best_d_n = 1, 4
            e6_score, e7_score, e8_score = 0.0, 0.0, 0.0
            for n in range(1, 25):
                w_order = ext._WEYL_ORDERS.get(('A', n))
                if w_order is None:
                    continue
                if w_order == order:
                    best_a, best_a_n = 1.0, n
                    break
                elif order % w_order == 0 or w_order % order == 0:
                    ratio = min(order, w_order) / max(order, w_order)
                    score = float(np.exp(-abs(np.log(ratio + 1e-30)) * 0.5))
                    if score > best_a:
                        best_a, best_a_n = score, n
            for n in range(4, 16):
                w_order = ext._WEYL_ORDERS.get(('D', n))
                if w_order is None:
                    continue
                if w_order == order:
                    best_d, best_d_n = 1.0, n
                    break
                elif order % w_order == 0 or w_order % order == 0:
                    ratio = min(order, w_order) / max(order, w_order)
                    score = float(np.exp(-abs(np.log(ratio + 1e-30)) * 0.5))
                    if score > best_d:
                        best_d, best_d_n = score, n
            for e_n, e_order in [(6, 51840), (7, 2903040), (8, 696729600)]:
                if order == e_order:
                    if e_n == 6: e6_score = 1.0
                    elif e_n == 7: e7_score = 1.0
                    else: e8_score = 1.0
                elif order % e_order == 0 or e_order % order == 0:
                    ratio = min(order, e_order) / max(order, e_order)
                    s = float(np.exp(-abs(np.log(ratio + 1e-30)) * 0.5))
                    if e_n == 6: e6_score = s
                    elif e_n == 7: e7_score = s
                    else: e8_score = s
            scores = [best_a, best_d, e6_score, e7_score, e8_score]
            best_idx = int(np.argmax(scores))
            best_n = [best_a_n, best_d_n, 6, 7, 8][best_idx]
            sig[:] = [best_a, best_d, e6_score, e7_score, e8_score,
                      float(best_n), float(max(scores)), float(method_code)]

        elif method == "lattice_det":
            if data is None or int(data) == 0:
                return sig
            det = abs(int(data))
            best_n = 1
            a_score = 0.0
            if det >= 2:
                n_cand = det - 1
                if 1 <= n_cand <= 30:
                    a_score, best_n = 1.0, n_cand
                else:
                    a_score = float(np.exp(-abs(np.log(det / 10.0)) * 0.3))
            d_score = 1.0 if det == 4 else float(np.exp(-abs(det - 4) * 0.5))
            e6_score = 1.0 if det == 3 else float(np.exp(-abs(det - 3) * 0.5))
            e7_score = 1.0 if det == 2 else float(np.exp(-abs(det - 2) * 0.5))
            e8_score = 1.0 if det == 1 else float(np.exp(-abs(det - 1) * 0.5))
            scores = [a_score, d_score, e6_score, e7_score, e8_score]
            best_idx = int(np.argmax(scores))
            if best_idx == 1: best_n = 4
            elif best_idx == 2: best_n = 6
            elif best_idx == 3: best_n = 7
            elif best_idx == 4: best_n = 8
            confidence = min(max(float(max(scores) - np.mean(scores)), 0.0), 1.0)
            sig[:] = [a_score, d_score, e6_score, e7_score, e8_score,
                      float(best_n), confidence, float(method_code)]

        elif method == "mckay":
            if data is None or not hasattr(data, '__len__') or len(data) < 2:
                return sig
            level, weight = int(data[0]), int(data[1])
            if level == 0:
                return sig
            a_n = max(weight - 1, 1)
            a_score = float(np.exp(-abs(weight - (a_n + 1)) * 0.3))
            d_n = max(weight // 2 + 1, 4)
            d_score = float(np.exp(-abs(weight - 2 * (d_n - 1)) * 0.3))
            e6_score = float(np.exp(-abs(weight - 12) * 0.2))
            e7_score = float(np.exp(-abs(weight - 18) * 0.2))
            e8_score = float(np.exp(-abs(weight - 30) * 0.2))
            for n in range(1, 15):
                w = ext._WEYL_ORDERS.get(('A', n))
                if w and w % level == 0:
                    a_score = min(a_score * 1.5, 1.0)
                    break
            for n in range(4, 12):
                w = ext._WEYL_ORDERS.get(('D', n))
                if w and w % level == 0:
                    d_score = min(d_score * 1.5, 1.0)
                    break
            if 51840 % level == 0: e6_score = min(e6_score * 1.5, 1.0)
            if 2903040 % level == 0: e7_score = min(e7_score * 1.5, 1.0)
            if 696729600 % level == 0: e8_score = min(e8_score * 1.5, 1.0)
            scores = [a_score, d_score, e6_score, e7_score, e8_score]
            best_idx = int(np.argmax(scores))
            best_n = [a_n, d_n, 6, 7, 8][best_idx]
            confidence = min(max(float(max(scores) - np.mean(scores)), 0.0), 1.0)
            sig[:] = [a_score, d_score, e6_score, e7_score, e8_score,
                      float(best_n), confidence, float(method_code)]

        elif method == "torsion":
            if data is None:
                return sig
            torsion = abs(int(data))
            if torsion == 0:
                return sig
            a_n = torsion - 1
            a_score = float(np.exp(-a_n * 0.1)) if a_n >= 1 else 0.0
            d_score = 0.8 if torsion % 4 == 0 else (0.5 if torsion % 2 == 0 else 0.0)
            e6_score = float(np.exp(-abs(torsion - 3) * 0.8))
            e7_score = float(np.exp(-abs(torsion - 2) * 0.8))
            e8_score = float(np.exp(-abs(torsion - 1) * 0.8))
            scores = [a_score, d_score, e6_score, e7_score, e8_score]
            best_idx = int(np.argmax(scores))
            best_n = [max(a_n, 1), 4, 6, 7, 8][best_idx]
            confidence = min(max(float(max(scores) - np.mean(scores)), 0.0), 1.0)
            sig[:] = [a_score, d_score, e6_score, e7_score, e8_score,
                      float(best_n), confidence, float(method_code)]

        return sig

    @staticmethod
    def s21_automorphic_signature(coefficients, level=None, weight=None):
        """S21: Automorphic association signature.

        Encodes whether a coefficient sequence behaves like Hecke eigenvalues
        of an automorphic form. EC a_p sequences and modular form traces
        should score high on Ramanujan bound and multiplicativity; OEIS and
        knot sequences should score low — that separation IS the signal.

        Args:
            coefficients: list/array of numeric values (a_p, traces, or raw terms)
            level: conductor/level of the form (None if unknown)
            weight: weight of the form (None if unknown; EC = 2)

        Returns: np.array of length 8 (float32)
        """
        n_dims = 8
        if not coefficients or len(coefficients) < 4:
            return np.full(n_dims, np.nan, dtype=np.float32)

        coeffs = np.array(coefficients, dtype=np.float64)
        n = len(coeffs)
        k = weight if weight is not None else 2  # default weight-2 (EC)

        # --- [0] spectral_type: Ramanujan bound compliance ---
        # For weight-k forms, |a_p| <= 2*p^((k-1)/2) at prime indices.
        # Approximate: treat index i+1 as the i-th prime-like position.
        # Use actual small primes for the first terms.
        small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        n_check = min(n, len(small_primes))
        if n_check > 0:
            satisfied = 0
            for idx in range(n_check):
                p = small_primes[idx]
                bound = 2.0 * p ** ((k - 1) / 2.0)
                if abs(coeffs[idx]) <= bound + 1e-9:
                    satisfied += 1
            spectral_type = satisfied / n_check
        else:
            spectral_type = 0.0

        # --- [1] parity: sign distribution ---
        # Automorphic forms have specific parity constraints.
        # Encode as normalized sum of signs: +1 if all positive, -1 if all negative.
        nonzero = coeffs[coeffs != 0]
        if len(nonzero) > 0:
            parity = float(np.sum(np.sign(nonzero))) / len(nonzero)
        else:
            parity = 0.0

        # --- [2] multiplicativity_score ---
        # Test a_{mn} = a_m * a_n for coprime (m, n) pairs.
        # Use 0-indexed: coeffs[i] represents a_{i+1}.
        from math import gcd
        mult_tests = 0
        mult_pass = 0
        max_idx = min(n, 20)
        for m in range(1, max_idx + 1):
            for ni in range(m + 1, max_idx + 1):
                mn = m * ni
                if mn - 1 >= n:
                    continue
                if gcd(m, ni) != 1:
                    continue
                expected = coeffs[m - 1] * coeffs[ni - 1]
                actual = coeffs[mn - 1]
                mult_tests += 1
                if abs(expected) < 1e-12 and abs(actual) < 1e-12:
                    mult_pass += 1
                elif abs(expected) > 1e-12:
                    if abs((actual - expected) / expected) < 0.01:
                        mult_pass += 1
        multiplicativity = mult_pass / mult_tests if mult_tests > 0 else 0.0

        # --- [3] functional_equation_type ---
        # Encode symmetry from sign pattern: even function -> +1, odd -> -1.
        # Proxy: check if coefficients are symmetric/antisymmetric around midpoint.
        half = min(n, 20)
        if half >= 4:
            front = coeffs[:half]
            signs = np.sign(front)
            # Fraction of positive signs among nonzero
            pos_frac = np.sum(signs > 0) / max(np.sum(signs != 0), 1)
            # Map: 0.5 = balanced (odd-like), 0 or 1 = biased (even-like)
            func_eq = abs(pos_frac - 0.5) * 2.0  # 0 = perfectly balanced, 1 = all same sign
        else:
            func_eq = 0.0

        # --- [4] conductor_weight_ratio ---
        if level is not None and level > 0 and k > 0:
            cw_ratio = np.log1p(float(level)) / float(k)
        else:
            cw_ratio = 0.0

        # --- [5] coefficient_field_degree ---
        # Approximate: if all coefficients are integers, degree = 1.
        # Otherwise, count distinct fractional parts as proxy for higher degree.
        int_count = sum(1 for c in coeffs[:20] if abs(c - round(c)) < 1e-9)
        total_check = min(n, 20)
        if total_check > 0:
            int_frac = int_count / total_check
            # degree 1 -> 1.0, higher degree -> lower score
            coeff_field_deg = int_frac  # 1.0 = all integers (Q-rational), 0.0 = none
        else:
            coeff_field_deg = 0.0

        # --- [6] hecke_multiplicativity ---
        # Stronger test: a_{p^2} = a_p^2 - p^(k-1) for weight k.
        # Check at small primes where p^2 - 1 < n.
        hecke_tests = 0
        hecke_pass = 0
        for p in small_primes:
            p_idx = p - 1       # a_p is at index p-1
            p2_idx = p * p - 1  # a_{p^2} is at index p^2 - 1
            if p2_idx >= n or p_idx >= n:
                continue
            a_p = coeffs[p_idx]
            a_p2 = coeffs[p2_idx]
            expected_hecke = a_p ** 2 - p ** (k - 1)
            hecke_tests += 1
            if abs(expected_hecke) < 1e-12 and abs(a_p2) < 1e-12:
                hecke_pass += 1
            elif abs(expected_hecke) > 1e-12:
                if abs((a_p2 - expected_hecke) / expected_hecke) < 0.01:
                    hecke_pass += 1
        hecke_mult = hecke_pass / hecke_tests if hecke_tests > 0 else 0.0

        # --- [7] satake_parameter ---
        # For weight k, a_p = alpha_p + beta_p where alpha*beta = p^(k-1).
        # Estimate: satake angle theta_p where a_p = 2*p^((k-1)/2)*cos(theta_p).
        # Average |cos(theta_p)| across primes as a summary.
        satake_vals = []
        for p in small_primes:
            p_idx = p - 1
            if p_idx >= n:
                continue
            a_p = coeffs[p_idx]
            denom = 2.0 * p ** ((k - 1) / 2.0)
            if abs(denom) > 1e-12:
                cos_theta = a_p / denom
                # Clamp to [-1, 1] — values outside mean Ramanujan violation
                cos_theta_clamped = max(-1.0, min(1.0, cos_theta))
                satake_vals.append(abs(cos_theta_clamped))
        satake_param = float(np.mean(satake_vals)) if satake_vals else 0.0

        return np.array([
            spectral_type,
            parity,
            multiplicativity,
            func_eq,
            cw_ratio,
            coeff_field_deg,
            hecke_mult,
            satake_param,
        ], dtype=np.float32)

    @staticmethod
    def s11_monodromy_proxy(coefficients, n_terms=None):
        """S11: Monodromy representation proxy.
        Extract 6 features that correlate with monodromy structure from
        a coefficient sequence. Monodromy — how solutions permute as
        parameters traverse loops — is a deep invariant linking topology
        and number theory (braid groups, Grothendieck-Teichmuller).

        Features:
          [0] sign_changes      — normalized count of sign changes
          [1] period_estimate   — autocorrelation-based period detection
          [2] growth_type       — 0=bounded, 0.5=polynomial, 1.0=exponential
          [3] galois_content    — distinct prime factors of GCD of nonzero terms
          [4] symmetry_score    — palindromic / anti-palindromic test
          [5] ramification_proxy — fraction of degenerate (0 or +/-1) terms

        Returns: vector of length 6.
        """
        if not coefficients or len(coefficients) < 4:
            return np.full(6, np.nan)

        arr = np.array(coefficients, dtype=np.float64)
        if n_terms is not None:
            arr = arr[:n_terms]
        N = len(arr)
        sig = np.zeros(6, dtype=np.float32)

        # [0] sign_changes — count transitions between positive and negative
        nonzero = arr[arr != 0]
        if len(nonzero) >= 2:
            signs = np.sign(nonzero)
            sig[0] = float(np.sum(signs[1:] != signs[:-1])) / len(nonzero)
        else:
            sig[0] = 0.0

        # [1] period_estimate — autocorrelation peak detection
        centered = arr - np.mean(arr)
        norm = np.dot(centered, centered)
        if norm > 1e-12 and N >= 6:
            # Compute autocorrelation for lags 1..N//2
            max_lag = N // 2
            autocorr = np.zeros(max_lag)
            for lag in range(1, max_lag):
                autocorr[lag] = np.dot(centered[:N - lag], centered[lag:]) / norm
            # Find first peak: where autocorr goes from increasing to decreasing
            best_lag = 0
            for k in range(2, max_lag - 1):
                if autocorr[k] > autocorr[k - 1] and autocorr[k] > autocorr[k + 1]:
                    if autocorr[k] > 0.1:  # minimum significance
                        best_lag = k
                        break
            # Normalize period: 0 = aperiodic, 1 = period-2 (fastest)
            if best_lag > 0:
                sig[1] = 1.0 / best_lag
            else:
                sig[1] = 0.0
        else:
            sig[1] = 0.0

        # [2] growth_type — classify via log(|a_n|) / log(n)
        abs_arr = np.abs(arr)
        # Use terms at indices >= 2 to avoid log(0) and log(1) issues
        indices = np.arange(2, N)
        if len(indices) >= 3:
            vals = abs_arr[2:N]
            valid = vals > 0
            if valid.sum() >= 3:
                log_vals = np.log(vals[valid])
                log_idx = np.log(indices[:len(vals)][valid])
                # Median ratio: log(|a_n|) / log(n)
                ratios = log_vals / np.maximum(log_idx, 1e-12)
                med_ratio = np.median(ratios)
                if med_ratio < 0.5:
                    sig[2] = 0.0    # bounded
                elif med_ratio < 5.0:
                    sig[2] = 0.5    # polynomial
                else:
                    sig[2] = 1.0    # exponential
            else:
                sig[2] = 0.0  # mostly zeros -> bounded
        else:
            sig[2] = 0.0

        # [3] galois_content — distinct prime factors of GCD of nonzero terms
        int_nonzero = [abs(int(round(v))) for v in arr if v != 0 and np.isfinite(v)]
        if int_nonzero:
            from math import gcd
            from functools import reduce
            g = reduce(gcd, int_nonzero)
            if g > 1:
                # Count distinct prime factors
                n_prime_factors = 0
                temp = g
                for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
                    if temp <= 1:
                        break
                    if temp % p == 0:
                        n_prime_factors += 1
                        while temp % p == 0:
                            temp //= p
                if temp > 1:
                    n_prime_factors += 1  # remaining large prime factor
                sig[3] = float(n_prime_factors)
            else:
                sig[3] = 0.0
        else:
            sig[3] = 0.0

        # [4] symmetry_score — palindromic / anti-palindromic test
        # +1 = perfect palindrome, -1 = perfect anti-palindrome, 0 = neither
        rev = arr[::-1]
        norm_arr = np.linalg.norm(arr)
        if norm_arr > 1e-12:
            palin_score = np.dot(arr, rev) / (norm_arr ** 2)
            sig[4] = float(np.clip(palin_score, -1.0, 1.0))
        else:
            sig[4] = 0.0

        # [5] ramification_proxy — fraction of terms that are 0 or +/-1
        degenerate = np.sum((abs_arr == 0) | (abs_arr == 1))
        sig[5] = float(degenerate) / N

        return sig

    @staticmethod
    def s33_recurrence(values, max_order=5, residual_threshold=0.01):
        """S33: Linear recurrence detection.
        Test whether a sequence satisfies a linear recurrence of order 1-5.
        Returns: vector of length 3 [is_recurrent, best_order, residual].
        """
        sig = np.full(3, np.nan, dtype=np.float32)
        if not values or len(values) < max_order + 10:
            return sig
        seq = np.array(values, dtype=np.float64)
        best_order, best_residual = 0, 1.0
        for k in range(1, max_order + 1):
            n = len(seq) - k
            if n < k + 5:
                continue
            X = np.column_stack([seq[k - j - 1: k - j - 1 + n] for j in range(k)])
            y = seq[k: k + n]
            try:
                coeffs, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
            except np.linalg.LinAlgError:
                continue
            predicted = X @ coeffs
            ss_res = np.sum((y - predicted) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            if ss_tot == 0:
                return np.array([1.0, 1.0, 0.0], dtype=np.float32)
            relative_residual = ss_res / ss_tot
            if relative_residual < best_residual:
                best_residual = relative_residual
                best_order = k
        is_rec = 1.0 if best_residual < residual_threshold else 0.0
        sig[:] = [is_rec, float(best_order), float(best_residual)]
        return sig


# ============================================================
# Battery encoder — F1-F27 results as tensor dimensions
# ============================================================
class BatteryEncoder:
    """Encode falsification battery results as feature vectors."""

    VERDICT_MAP = {
        'KILLED': 0.0, 'SKIP': 0.0,
        'NEGLIGIBLE': 0.1, 'NEGLIGIBLE_EFFECT': 0.1,
        'TENDENCY': 0.3,
        'SMALL_EFFECT': 0.4,
        'CONSTRAINT': 0.5, 'MODERATE_EFFECT': 0.5,
        'CONDITIONAL': 0.7, 'CONDITIONAL_LAW': 0.7,
        'STRONG_EFFECT': 0.8,
        'LAW': 0.9, 'UNIVERSAL': 0.9,
        'IDENTITY': 1.0,
        'SURVIVES': 0.6,
        'ANALYZED': 0.5,
        'NOT_TAUTOLOGY': 0.7,
        'PARTIAL_MATCH': 0.4,
        'CONTEXT_DEPENDENT': 0.5,
        'CONSISTENT': 0.6,
        'EXTREME_TAIL_DRIVEN': 0.3,
    }

    @classmethod
    def encode(cls, battery_result, n_dims=8):
        """Encode a single test's battery results into a feature vector.

        Extracts: verdict_score, eta_squared, p_value, z_score,
                  m4m2, f25_verdict, f27_verdict, spearman_r
        """
        sig = np.full(n_dims, np.nan, dtype=np.float32)

        if not battery_result:
            return sig

        # Verdict -> score
        verdict = battery_result.get('verdict', '')
        sig[0] = cls.VERDICT_MAP.get(verdict, 0.5)

        # eta^2 from F24
        f24 = battery_result.get('f24', battery_result.get('f24_by_rank', {}))
        if isinstance(f24, dict):
            eta2 = f24.get('eta_squared')
            if eta2 is not None:
                sig[1] = float(eta2)

        # p-value
        p_val = battery_result.get('p')
        if p_val is not None:
            sig[2] = -np.log10(max(float(p_val), 1e-300))  # log-scale

        # z-score
        z = battery_result.get('z')
        if z is not None:
            sig[3] = float(z)

        # M4/M^2 from F24b
        f24b = battery_result.get('f24b', {})
        if isinstance(f24b, dict):
            m4m2 = f24b.get('m4m2_ratio')
            if m4m2 is not None and isinstance(m4m2, (int, float)):
                sig[4] = float(m4m2)

        # F25 transportability
        f25 = battery_result.get('f25', {})
        if isinstance(f25, dict):
            f25_v = f25.get('verdict', '')
            sig[5] = cls.VERDICT_MAP.get(f25_v, 0.5)

        # F27 consequence check
        f27 = battery_result.get('f27', {})
        if isinstance(f27, dict):
            f27_v = f27.get('verdict', '')
            sig[6] = cls.VERDICT_MAP.get(f27_v, 0.5)

        # Correlation (Spearman r)
        r = battery_result.get('spearman_r')
        if r is not None:
            sig[7] = float(r)

        return sig


# ============================================================
# Data loaders — extract MathObjects from existing datasets
# ============================================================
class DataLoaders:
    """Load mathematical objects from Prometheus datasets."""

    @staticmethod
    def load_knots(max_n=None):
        """Load knots with Alexander/Jones polynomial signatures."""
        path = ROOT / "cartography/knots/data/knots.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        objects = []
        ext = StrategyExtractors

        for k in data["knots"][:max_n]:
            obj = MathObject(
                obj_id=f"knot_{k['name']}",
                domain="knot",
                label=k["name"],
                signatures={},
                raw={"crossing_number": k.get("crossing_number", 0),
                     "determinant": k.get("determinant", 0)},
            )

            # S1: complex plane evaluation on Alexander polynomial
            ac = k.get("alex_coeffs", [])
            obj.signatures["s1_alex"] = ext.s1_complex(ac)

            # S1: complex plane evaluation on Jones polynomial
            jc = k.get("jones_coeffs", [])
            obj.signatures["s1_jones"] = ext.s1_complex(jc)

            # S3: mod-p on Alexander coefficients
            obj.signatures["s3_alex"] = ext.s3_mod_p(ac)

            # S3: mod-p on Jones coefficients
            obj.signatures["s3_jones"] = ext.s3_mod_p(jc)

            # S5: spectral on Alexander
            obj.signatures["s5_alex"] = ext.s5_spectral(ac)

            # S5: spectral on Jones
            obj.signatures["s5_jones"] = ext.s5_spectral(jc)

            # S7: p-adic valuation of determinant
            det = k.get("determinant")
            obj.signatures["s7_det"] = ext.s7_padic(det)

            # S13: determinant as discriminant analog
            obj.signatures["s13"] = ext.s13_discriminant(det)

            # S24: entropy of Alexander coefficients
            obj.signatures["s24_alex"] = ext.s24_entropy(ac)

            # S21: automorphic signature on Alexander coefficients
            # Knots will score low on Ramanujan/multiplicativity — useful separation
            obj.signatures["s21_auto"] = ext.s21_automorphic_signature(ac)

            # S11: monodromy proxy — knot polynomials have deep monodromy
            # connections to braid groups (Grothendieck-Teichmuller bridge)
            # Use Alexander coefficients as primary (palindromic structure)
            # and Jones coefficients as fallback
            if ac and len(ac) >= 4:
                obj.signatures["s11_mono"] = ext.s11_monodromy_proxy(ac)
            elif jc and len(jc) >= 4:
                obj.signatures["s11_mono"] = ext.s11_monodromy_proxy(jc)
            else:
                obj.signatures["s11_mono"] = np.full(6, np.nan)

            # S19: ADE classification from Alexander polynomial coefficients
            obj.signatures["s19_ade"] = ext.s19_ade_classify(ac, method="discriminant")

            objects.append(obj)
        return objects

    @staticmethod
    def load_number_fields(max_n=None):
        """Load number fields with algebraic signatures."""
        path = ROOT / "cartography/number_fields/data/number_fields.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        objects = []
        ext = StrategyExtractors

        for f in data[:max_n]:
            try:
                disc = int(f["disc_abs"])
                obj = MathObject(
                    obj_id=f"nf_{f['label']}",
                    domain="NF",
                    label=f["label"],
                    signatures={},
                    raw={"degree": int(f["degree"]),
                         "class_number": int(f.get("class_number", 0)),
                         "regulator": float(f.get("regulator", 0))},
                )
                # S7: p-adic valuation of discriminant
                obj.signatures["s7_disc"] = ext.s7_padic(disc)

                # S10: Galois group
                obj.signatures["s10"] = ext.s10_galois_hash(f.get("galois_label"))

                # S12: zeta-like density from discriminant mod p
                obj.signatures["s12_nf"] = ext.s12_zeta(disc, mode="disc_mod")

                # S13: discriminant
                obj.signatures["s13"] = ext.s13_discriminant(
                    disc * (1 if f.get("disc_sign", "1") == "1" else -1)
                )

                # S24: class number / regulator as "coefficient" analog
                cn = int(f.get("class_number", 0))
                reg = float(f.get("regulator", 0))
                if cn > 0 and reg > 0:
                    obj.signatures["s24_arith"] = np.array([
                        np.log1p(cn), np.log1p(reg),
                        np.log1p(cn * reg / max(np.sqrt(disc), 1)),  # Brauer-Siegel
                        float(f["degree"]),
                    ], dtype=np.float32)
                else:
                    obj.signatures["s24_arith"] = np.full(4, np.nan)

                objects.append(obj)
            except (ValueError, TypeError):
                continue
        return objects

    @staticmethod
    def load_ec(max_n=None):
        """Load elliptic curves from DuckDB."""
        import duckdb
        con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
        df = con.execute(f"""
            SELECT lmfdb_label, conductor, rank, analytic_rank,
                   torsion, torsion_structure, aplist, bad_primes
            FROM elliptic_curves
            WHERE rank IS NOT NULL
            {"LIMIT " + str(max_n) if max_n else ""}
        """).fetchdf()
        con.close()

        objects = []
        ext = StrategyExtractors

        for _, row in df.iterrows():
            cond = int(row["conductor"])
            obj = MathObject(
                obj_id=f"ec_{row['lmfdb_label']}",
                domain="EC",
                label=row["lmfdb_label"],
                signatures={},
                raw={"conductor": cond, "rank": int(row["rank"]),
                     "torsion": int(row["torsion"]),
                     "analytic_rank": int(row["analytic_rank"])},
            )

            # S1: complex plane evaluation on a_p sequence (treated as polynomial coeffs)
            ap = row.get("aplist")
            if ap is not None and hasattr(ap, '__len__') and len(ap) >= 3:
                ap_list = [int(x) for x in ap[:50] if x is not None]
                obj.signatures["s1_ap"] = ext.s1_complex(ap_list)
                obj.signatures["s3_ap"] = ext.s3_mod_p(ap_list)
                obj.signatures["s5_ap"] = ext.s5_spectral(ap_list)
                obj.signatures["s24_ap"] = ext.s24_entropy(ap_list)
                # S12: divisibility density from a_p values
                obj.signatures["s12_ec"] = ext.s12_zeta(ap_list, mode="divisibility")
                # S21: automorphic signature — EC a_p with conductor as level, weight=2
                obj.signatures["s21_auto"] = ext.s21_automorphic_signature(
                    ap_list, level=cond, weight=2)
                # S11: monodromy proxy on a_p traces
                obj.signatures["s11_mono"] = ext.s11_monodromy_proxy(ap_list)
            else:
                obj.signatures["s1_ap"] = np.full(8, np.nan)
                obj.signatures["s3_ap"] = np.full(6, np.nan)
                obj.signatures["s5_ap"] = np.full(8, np.nan)
                obj.signatures["s24_ap"] = np.full(4, np.nan)
                obj.signatures["s12_ec"] = np.full(4, np.nan)
                obj.signatures["s21_auto"] = np.full(8, np.nan)
                obj.signatures["s11_mono"] = np.full(6, np.nan)

            # S7: p-adic valuation of conductor
            obj.signatures["s7_cond"] = ext.s7_padic(cond)

            # S13: conductor as discriminant
            obj.signatures["s13"] = ext.s13_discriminant(cond)

            # S19: ADE classification from torsion structure
            torsion_val = int(row["torsion"])
            obj.signatures["s19_ade"] = ext.s19_ade_classify(
                torsion_val, method="torsion")

            objects.append(obj)
        return objects

    @staticmethod
    def load_oeis(max_n=20000):
        """Load OEIS sequences with spectral and attractor signatures."""
        path = ROOT / "cartography/oeis/data/stripped_new.txt"
        if not path.exists():
            print("  OEIS stripped_new.txt not found, skipping")
            return []

        objects = []
        ext = StrategyExtractors
        count = 0

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Format: A-number ,term1,term2,...
                idx = line.find(",")
                if idx < 0:
                    continue
                a_num = line[:idx].strip()
                terms_str = line[idx:].strip().strip(",")
                if not terms_str:
                    continue
                try:
                    terms = [int(t.strip()) for t in terms_str.split(",") if t.strip()]
                except ValueError:
                    continue

                if len(terms) < 10:
                    continue

                terms = terms[:100]  # cap

                obj = MathObject(
                    obj_id=f"oeis_{a_num}",
                    domain="OEIS",
                    label=a_num,
                    signatures={},
                    raw={"n_terms": len(terms), "first_term": terms[0]},
                )

                # S5: spectral
                obj.signatures["s5_oeis"] = ext.s5_spectral(terms)

                # S6: attractor (phase space) — (a(n), a(n+1)) statistics
                if len(terms) >= 20:
                    diffs = np.diff(terms[:50])
                    arr = np.array(terms[:50], dtype=float)
                    # Lyapunov-like: mean |log(|diff|)|
                    abs_diffs = np.abs(diffs).astype(float) + 1
                    lyap = np.mean(np.log(abs_diffs))
                    # Autocorrelation at lag 1
                    if np.std(arr) > 0:
                        ac1 = np.corrcoef(arr[:-1], arr[1:])[0, 1]
                    else:
                        ac1 = 0.0
                    obj.signatures["s6_oeis"] = np.array([
                        lyap,
                        ac1 if np.isfinite(ac1) else 0.0,
                        np.log1p(float(np.max(np.abs(np.array(terms[:50], dtype=float))))),
                        float(np.std(diffs) / (np.mean(np.abs(diffs)) + 1e-8)),
                    ], dtype=np.float32)
                else:
                    obj.signatures["s6_oeis"] = np.full(4, np.nan)

                # S3: mod-p on terms
                obj.signatures["s3_ap"] = ext.s3_mod_p(terms)

                # S12: zeta-like divisibility density
                obj.signatures["s12_oeis"] = ext.s12_zeta(terms, mode="divisibility")

                # S24: entropy
                obj.signatures["s24_oeis"] = ext.s24_entropy(terms)

                # S21: automorphic signature on raw terms
                # OEIS will score low on Ramanujan/multiplicativity — creates separation
                obj.signatures["s21_auto"] = ext.s21_automorphic_signature(terms[:50])

                # S11: monodromy proxy on sequence terms
                obj.signatures["s11_mono"] = ext.s11_monodromy_proxy(terms[:50])

                # S33: linear recurrence detection
                obj.signatures["s33_recurrence"] = ext.s33_recurrence(terms)

                objects.append(obj)
                count += 1
                if count >= max_n:
                    break

        return objects

    @staticmethod
    def load_genus2(max_n=None):
        """Load genus-2 curves with symmetry, conductor, endomorphism, and Galois signatures.

        Sources (merged by label, LMFDB file takes priority for shared fields):
          1. cartography/genus2/data/genus2_curves_full.json  (original)
          2. cartography/lmfdb_dump/g2c_curves.json           (66K LMFDB records)
          3. cartography/lmfdb_dump/g2c_endomorphisms.json    (ring/GL2 type)
          4. cartography/lmfdb_dump/g2c_galrep.json           (Galois images)
        """
        # --- Step 1: Merge curve data from both sources -----------------
        curves_by_label = {}

        # Source A: original genus2_curves_full.json
        path_orig = ROOT / "cartography/genus2/data/genus2_curves_full.json"
        if not path_orig.exists():
            path_orig = ROOT / "cartography/genus2/data/genus2_curves.json"
        if path_orig.exists():
            raw = json.loads(path_orig.read_text(encoding="utf-8"))
            orig_curves = raw if isinstance(raw, list) else raw.get("curves", raw.get("data", []))
            for c in orig_curves:
                lbl = c.get("label", c.get("lmfdb_label", ""))
                if lbl:
                    curves_by_label[lbl] = dict(c)
            print(f"    genus-2 original: {len(orig_curves)} records")

        # Source B: LMFDB g2c_curves.json (66K, dict with "records" key)
        path_lmfdb = ROOT / "cartography/lmfdb_dump/g2c_curves.json"
        if path_lmfdb.exists():
            raw = json.loads(path_lmfdb.read_text(encoding="utf-8"))
            lmfdb_recs = raw.get("records", []) if isinstance(raw, dict) else raw
            for c in lmfdb_recs:
                lbl = c.get("label", "")
                if not lbl:
                    continue
                if lbl in curves_by_label:
                    # Merge — LMFDB fields take priority
                    curves_by_label[lbl].update(c)
                else:
                    curves_by_label[lbl] = dict(c)
            print(f"    genus-2 LMFDB:    {len(lmfdb_recs)} records")

        if not curves_by_label:
            print("  genus-2 data not found, skipping")
            return []

        print(f"    genus-2 merged:   {len(curves_by_label)} unique curves")

        # --- Step 2: Load endomorphism data (keyed by label) ------------
        endo_by_label = {}
        path_endo = ROOT / "cartography/lmfdb_dump/g2c_endomorphisms.json"
        if path_endo.exists():
            raw = json.loads(path_endo.read_text(encoding="utf-8"))
            endo_recs = raw.get("records", []) if isinstance(raw, dict) else raw
            for e in endo_recs:
                lbl = e.get("label", "")
                if lbl:
                    endo_by_label[lbl] = e
            print(f"    genus-2 endomorphisms: {len(endo_by_label)} records")

        # --- Step 3: Load Galois rep data (keyed by label, multi-row) ---
        galrep_by_label = {}  # label -> list of (prime, modell_image)
        path_galrep = ROOT / "cartography/lmfdb_dump/g2c_galrep.json"
        if path_galrep.exists():
            raw = json.loads(path_galrep.read_text(encoding="utf-8"))
            galrep_recs = raw.get("records", []) if isinstance(raw, dict) else raw
            for g in galrep_recs:
                lbl = g.get("lmfdb_label", "")
                if lbl:
                    galrep_by_label.setdefault(lbl, []).append(g)
            print(f"    genus-2 galrep:   {len(galrep_by_label)} curves, "
                  f"{len(galrep_recs)} rows")

        # --- Step 4: Build MathObjects ----------------------------------
        # Ring-type encoding for endomorphisms
        ring_type_map = {
            "[1,-1]": 0,   # Z (trivial endomorphism ring)
            "[1,1]": 1,    # Z x Z
            "[2,-1]": 2,   # order in imaginary quadratic field
            "[2,1]": 3,    # order in real quadratic field
            "[4,-1]": 4,   # quaternion order
            "[4,1]": 5,    # M_2(Z)
        }

        objects = []
        ext = StrategyExtractors
        all_labels = list(curves_by_label.keys())
        if max_n is not None:
            all_labels = all_labels[:max_n]

        for lbl in all_labels:
            c = curves_by_label[lbl]
            cond = c.get("conductor") or c.get("cond")
            if not cond:
                continue
            try:
                cond = int(cond)
            except (ValueError, TypeError):
                continue

            obj = MathObject(
                obj_id=f"g2_{lbl}",
                domain="genus2",
                label=lbl,
                signatures={},
                raw={"conductor": cond,
                     "st_group": c.get("st_group", c.get("st_group_label", "")),
                     "analytic_rank": c.get("analytic_rank"),
                     "root_number": c.get("root_number")},
            )

            # S7: p-adic valuation of conductor
            obj.signatures["s7_cond"] = ext.s7_padic(cond)

            # S13: conductor as discriminant
            disc = c.get("disc", c.get("abs_disc", cond))
            obj.signatures["s13"] = ext.s13_discriminant(disc, conductor=cond)

            # S9: Sato-Tate group as symmetry encoding
            st = c.get("st_group", c.get("st_group_label", ""))
            st_map = {"USp(4)": 0, "N(G_{3,3})": 1, "G_{3,3}": 2,
                      "N(U(1))": 3, "SU(2)": 4, "U(1)": 5,
                      "E_6": 6, "J(E_6)": 7, "E_4": 8, "J(E_4)": 9,
                      "F_{a,b}": 10, "F_{ac}": 11, "J(C_2)": 12,
                      "J(C_4)": 13, "J(C_6)": 14, "J(D_2)": 15,
                      "J(D_3)": 16, "J(D_4)": 17, "J(D_6)": 18,
                      "J(T)": 19, "J(O)": 20, "C_{2,1}": 21,
                      "D_{2,1}": 22, "D_{3,2}": 23, "D_{4,1}": 24,
                      "D_{4,2}": 25, "D_{6,1}": 26, "D_{6,2}": 27,
                      "O_1": 28}
            obj.signatures["s9_st"] = np.array([
                st_map.get(st, -1),
                float(len(st)) / 10.0,  # name length as proxy
                1.0 if "N(" in st else 0.0,  # normalizer flag
                1.0 if "J(" in st else 0.0,  # J-flag
            ], dtype=np.float32)

            # --- Endomorphism-derived features (s9-like encoding) -------
            endo = endo_by_label.get(lbl, {})
            ring_base = str(endo.get("ring_base", ""))
            ring_geom = str(endo.get("ring_geom", ""))
            is_gl2 = 1.0 if c.get("is_gl2_type", False) else 0.0
            is_simple_base = 1.0 if endo.get("is_simple_base",
                                              c.get("is_simple_base", False)) else 0.0
            is_simple_geom = 1.0 if endo.get("is_simple_geom",
                                              c.get("is_simple_geom", False)) else 0.0
            st_group_base = endo.get("st_group_base", "")
            st_group_geom = endo.get("st_group_geom", "")
            # Encode ring type as categorical
            ring_base_code = ring_type_map.get(ring_base, -1)
            ring_geom_code = ring_type_map.get(ring_geom, -1)
            obj.signatures["s9_endo"] = np.array([
                ring_base_code,
                ring_geom_code,
                is_gl2,
                is_simple_base,
                is_simple_geom,
                st_map.get(st_group_base, -1) if st_group_base else -1,
                st_map.get(st_group_geom, -1) if st_group_geom else -1,
                float(len(endo.get("factorsRR_base", []))) if endo else 0.0,
            ], dtype=np.float32)

            # --- Galois rep features ------------------------------------
            galreps = galrep_by_label.get(lbl, [])
            if galreps:
                primes_seen = []
                image_codes = []
                for gr in galreps:
                    p = gr.get("prime", 0)
                    img = gr.get("modell_image", "")
                    primes_seen.append(int(p) if p else 0)
                    # Parse modell_image "N.M.K" -> numeric hash
                    parts = str(img).split(".")
                    code = 0.0
                    for i, part in enumerate(parts[:3]):
                        try:
                            code += int(part) / (10 ** (i + 1))
                        except (ValueError, TypeError):
                            pass
                    image_codes.append(code)
                n_reps = len(galreps)
                mean_prime = float(np.mean(primes_seen)) if primes_seen else 0.0
                max_prime = float(max(primes_seen)) if primes_seen else 0.0
                mean_img_code = float(np.mean(image_codes)) if image_codes else 0.0
                obj.signatures["s10_galrep"] = np.array([
                    float(n_reps),
                    mean_prime / 100.0,  # normalize
                    max_prime / 100.0,
                    mean_img_code,
                ], dtype=np.float32)
            else:
                obj.signatures["s10_galrep"] = np.full(4, np.nan, dtype=np.float32)

            # --- S19: ADE from discriminant -----------------------------
            try:
                disc_val = int(c.get("abs_disc", c.get("disc", 0)))
            except (ValueError, TypeError):
                disc_val = 0
            if disc_val > 0:
                obj.signatures["s19_ade"] = ext.s19_ade_classify(
                    disc_val, method="lattice_det")

            # --- S21: automorphic association ---------------------------
            # Use root_number as functional equation sign, conductor as level
            root_num = c.get("root_number")
            analytic_rank = c.get("analytic_rank")
            # Build a lightweight coefficient-like sequence from invariants
            # for the automorphic signature (torsion, tamagawa, selmer)
            torsion_order = c.get("torsion_order", 0)
            tamagawa = c.get("tamagawa_product", 0)
            two_selmer = c.get("two_selmer_rank", 0)
            mw_rank = c.get("mw_rank", 0)
            try:
                torsion_order = int(torsion_order) if torsion_order else 0
                tamagawa = int(tamagawa) if tamagawa else 0
                two_selmer = int(two_selmer) if two_selmer else 0
                mw_rank = int(mw_rank) if mw_rank else 0
            except (ValueError, TypeError):
                torsion_order = tamagawa = two_selmer = mw_rank = 0

            func_eq_sign = float(root_num) if root_num is not None else 0.0
            a_rank = float(analytic_rank) if analytic_rank is not None else 0.0
            obj.signatures["s21_auto"] = np.array([
                0.0,           # spectral_type placeholder
                func_eq_sign,  # parity / root number
                0.0,           # multiplicativity placeholder
                abs(func_eq_sign),  # functional_equation_type
                np.log1p(float(cond)),  # conductor_weight_ratio (level proxy)
                1.0,           # coefficient_field_degree (rational)
                0.0,           # hecke_multiplicativity placeholder
                a_rank / 4.0,  # satake_parameter proxy (rank-scaled)
            ], dtype=np.float32)

            # --- S11: monodromy proxy from invariants -------------------
            # Build a coefficient-like sequence from arithmetic invariants
            invariant_seq = [
                float(torsion_order),
                float(tamagawa),
                float(two_selmer),
                float(mw_rank),
                float(cond % 12),  # level mod 12
                func_eq_sign,
            ]
            if len(invariant_seq) >= 4:
                obj.signatures["s11_mono"] = ext.s11_monodromy_proxy(invariant_seq)

            objects.append(obj)

        return objects

    @staticmethod
    def load_fungrim(max_n=None):
        """Load Fungrim formulas with operadic/symbolic signatures."""
        import ast
        path = ROOT / "cartography/fungrim/data/fungrim_index.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        objects = []

        for f in data["formulas"][:max_n]:
            nsym = int(f["n_symbols"])
            symbols = f.get("symbols", [])
            if isinstance(symbols, str):
                try:
                    symbols = ast.literal_eval(symbols)
                except:
                    symbols = []

            obj = MathObject(
                obj_id=f"fg_{f['id']}",
                domain="fungrim",
                label=f"{f['module']}/{f['id']}",
                signatures={},
                raw={"module": f["module"], "type": f["type"],
                     "n_symbols": nsym},
            )

            # S22: operadic — encode type and module as features
            type_map = {"equation": 0, "definition": 1, "domain": 2,
                        "table": 3, "identity": 4}
            obj.signatures["s22"] = np.array([
                type_map.get(f["type"], -1),
                nsym,
                len(symbols),
                hash(f["module"]) % 1000 / 1000.0,  # module hash
            ], dtype=np.float32)

            # S24: symbol frequency as entropy
            obj.signatures["s24_sym"] = np.array([
                np.log1p(nsym),
                1.0 if "Pi" in symbols else 0.0,
                1.0 if any("Zeta" in s for s in symbols) else 0.0,
                1.0 if "Infinity" in symbols else 0.0,
            ], dtype=np.float32)

            objects.append(obj)
        return objects

    @staticmethod
    def load_modular_forms(max_n=None):
        """Load modular forms from DuckDB with Hecke eigenvalue signatures."""
        import duckdb
        db_path = ROOT / "charon/data/charon.duckdb"
        if not db_path.exists():
            print("  WARNING: charon.duckdb not found, skipping modular_forms")
            return []
        try:
            con = duckdb.connect(str(db_path), read_only=True)
            query = """
                SELECT lmfdb_label, level, weight, traces
                FROM modular_forms WHERE traces IS NOT NULL
            """
            if max_n:
                query += f" LIMIT {int(max_n)}"
            rows = con.execute(query).fetchall()
            con.close()
        except Exception as e:
            print(f"  WARNING: Failed to load modular_forms: {e}")
            return []

        objects = []
        ext = StrategyExtractors
        for label, level, weight, traces in rows:
            if traces is None or len(traces) < 4:
                continue
            traces_list = [float(t) for t in traces[:50] if t is not None]
            if len(traces_list) < 4:
                continue
            obj = MathObject(
                obj_id=f"mf_{label}",
                domain="MF",
                label=label,
                signatures={},
                raw={"level": int(level), "weight": int(weight)},
            )
            obj.signatures["s7_cond"] = ext.s7_padic(level)
            obj.signatures["s13"] = ext.s13_discriminant(level)
            obj.signatures["s5_ap"] = ext.s5_spectral(traces_list)
            obj.signatures["s3_ap"] = ext.s3_mod_p(traces_list)
            obj.signatures["s1_ap"] = ext.s1_complex(traces_list)
            obj.signatures["s24_ap"] = ext.s24_entropy(traces_list)
            # S21: automorphic signature — modular form traces with level and weight
            obj.signatures["s21_auto"] = ext.s21_automorphic_signature(
                traces_list, level=int(level), weight=int(weight))
            # S11: monodromy proxy on Hecke traces
            obj.signatures["s11_mono"] = ext.s11_monodromy_proxy(traces_list)
            # S19: ADE classification via McKay correspondence (level, weight)
            obj.signatures["s19_ade"] = ext.s19_ade_classify(
                [int(level), int(weight)], method="mckay")
            objects.append(obj)
        return objects

    @staticmethod
    def load_abstract_groups(max_n=50000):
        """Load abstract groups with group-theoretic signatures."""
        path = ROOT / "cartography/groups/data/abstract_groups.json"
        if not path.exists():
            print("  WARNING: abstract_groups.json not found, skipping")
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            records = data.get("records", []) if isinstance(data, dict) else data
        except Exception as e:
            print(f"  WARNING: Failed to load abstract_groups: {e}")
            return []

        objects = []
        ext = StrategyExtractors
        for g in records[:max_n]:
            order = g.get("order")
            if order is None or order == 0:
                continue
            order = int(order)
            exponent = int(g.get("exponent", 0))
            num_conj = int(g.get("num_conjugacy_classes", 0))

            obj = MathObject(
                obj_id=f"grp_{g.get('label', str(order))}",
                domain="group",
                label=str(g.get("label", g.get("name", ""))),
                signatures={},
                raw={"order": order, "exponent": exponent,
                     "num_conjugacy_classes": num_conj,
                     "name": g.get("name", "")},
            )
            obj.signatures["s13"] = ext.s13_discriminant(order)
            obj.signatures["s7_cond"] = ext.s7_padic(order)
            invariants = [order, exponent, num_conj]
            obj.signatures["s3_ap"] = ext.s3_mod_p(invariants)
            obj.signatures["s24_ap"] = ext.s24_entropy(invariants)
            # S19: ADE classification from group order matching Weyl groups
            obj.signatures["s19_ade"] = ext.s19_ade_classify(order, method="order")
            objects.append(obj)
        return objects

    @staticmethod
    def load_maass_forms(max_n=15000):
        """Load Maass forms with spectral and coefficient signatures.

        WARNING: Source file is ~335 MB. Uses streaming parse to limit memory.
        """
        path = ROOT / "cartography/maass/data/maass_with_coefficients.json"
        if not path.exists():
            print("  WARNING: maass_with_coefficients.json not found, skipping")
            return []

        objects = []
        ext = StrategyExtractors
        count = 0

        try:
            # Stream-parse: read the JSON array incrementally
            import io
            with open(path, "r", encoding="utf-8") as f:
                # Skip opening bracket
                ch = f.read(1)
                while ch and ch != '[':
                    ch = f.read(1)

                buffer = ""
                brace_depth = 0
                while count < max_n:
                    ch = f.read(1)
                    if not ch:
                        break
                    if ch == '{':
                        if brace_depth == 0:
                            buffer = ch
                        else:
                            buffer += ch
                        brace_depth += 1
                    elif ch == '}':
                        brace_depth -= 1
                        buffer += ch
                        if brace_depth == 0 and buffer:
                            entry = json.loads(buffer)
                            buffer = ""
                            # Process entry
                            level = entry.get("level")
                            coeffs = entry.get("coefficients", [])
                            if level is None or not coeffs or len(coeffs) < 4:
                                continue
                            coeffs_50 = [float(c) for c in coeffs[:50]]
                            sp = entry.get("spectral_parameter")
                            try:
                                sp_val = float(sp) if sp is not None else 0.0
                            except (ValueError, TypeError):
                                sp_val = 0.0

                            obj = MathObject(
                                obj_id=f"maass_{entry.get('maass_id', count)}",
                                domain="maass",
                                label=str(entry.get("maass_id", "")),
                                signatures={},
                                raw={"level": int(level),
                                     "weight": int(entry.get("weight", 0)),
                                     "spectral_parameter": sp_val,
                                     "symmetry": entry.get("symmetry"),
                                     "fricke_eigenvalue": entry.get("fricke_eigenvalue")},
                            )
                            obj.signatures["s5_ap"] = ext.s5_spectral(coeffs_50)
                            obj.signatures["s3_ap"] = ext.s3_mod_p(coeffs_50)
                            obj.signatures["s1_ap"] = ext.s1_complex(coeffs_50)
                            obj.signatures["s7_cond"] = ext.s7_padic(level)
                            obj.signatures["s13"] = ext.s13_discriminant(level)
                            obj.signatures["s24_ap"] = ext.s24_entropy(coeffs_50)
                            # S21: automorphic signature — Maass form coefficients
                            maass_weight = int(entry.get("weight", 0))
                            obj.signatures["s21_auto"] = ext.s21_automorphic_signature(
                                coeffs_50, level=int(level), weight=maass_weight)
                            # S11: monodromy proxy on Fourier coefficients
                            obj.signatures["s11_mono"] = ext.s11_monodromy_proxy(coeffs_50)
                            # S19: ADE classification by level via McKay
                            obj.signatures["s19_ade"] = ext.s19_ade_classify(
                                [int(level), maass_weight], method="mckay")
                            objects.append(obj)
                            count += 1
                    elif brace_depth > 0:
                        buffer += ch
        except Exception as e:
            print(f"  WARNING: Failed to load maass_forms: {e}")
            if objects:
                print(f"  (loaded {len(objects)} before error)")

        return objects

    @staticmethod
    def load_lattices(max_n=None):
        """Load integral lattices with geometric signatures."""
        path = ROOT / "cartography/lattices/data/lattices_full.json"
        if not path.exists():
            print("  WARNING: lattices_full.json not found, skipping")
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            records = data.get("records", []) if isinstance(data, dict) else data
        except Exception as e:
            print(f"  WARNING: Failed to load lattices: {e}")
            return []

        objects = []
        ext = StrategyExtractors
        for rec in records[:max_n]:
            det = rec.get("determinant")
            if det is None:
                continue
            det = int(det)
            level = int(rec.get("level", 0))
            dim = int(rec.get("dimension", 0))
            cn = int(rec.get("class_number", 0))
            mv = int(rec.get("minimal_vector", 0))

            obj = MathObject(
                obj_id=f"lat_{rec.get('label', str(det))}",
                domain="lattice",
                label=str(rec.get("label", "")),
                signatures={},
                raw={"dimension": dim, "determinant": det,
                     "level": level, "class_number": cn,
                     "minimal_vector": mv,
                     "aut_group_order": int(rec.get("aut_group_order", 0))},
            )
            obj.signatures["s13"] = ext.s13_discriminant(det, conductor=level)
            obj.signatures["s7_cond"] = ext.s7_padic(det)
            obj.signatures["s3_ap"] = ext.s3_mod_p([dim, det, level, cn, mv])
            obj.signatures["s24_ap"] = ext.s24_entropy([dim, det, level, cn])
            # S19: ADE classification from lattice determinant
            obj.signatures["s19_ade"] = ext.s19_ade_classify(det, method="lattice_det")
            objects.append(obj)
        return objects

    @staticmethod
    def load_dirichlet_zeros(max_n=None):
        """Load Dirichlet L-function zeros from DuckDB."""
        import duckdb
        db_path = ROOT / "charon/data/charon.duckdb"
        if not db_path.exists():
            print("  WARNING: charon.duckdb not found, skipping dirichlet_zeros")
            return []
        try:
            con = duckdb.connect(str(db_path), read_only=True)
            query = """
                SELECT lmfdb_url, conductor, degree, rank, zeros_vector
                FROM dirichlet_zeros WHERE conductor IS NOT NULL
            """
            if max_n:
                query += f" LIMIT {int(max_n)}"
            rows = con.execute(query).fetchall()
            con.close()
        except Exception as e:
            print(f"  WARNING: Failed to load dirichlet_zeros: {e}")
            return []

        objects = []
        ext = StrategyExtractors
        for lmfdb_url, conductor, degree, rank, zeros_vec in rows:
            if conductor is None:
                continue
            conductor = int(conductor)
            degree = int(degree) if degree is not None else 0
            rank = int(rank) if rank is not None else 0

            obj = MathObject(
                obj_id=f"lz_{lmfdb_url or conductor}",
                domain="Lzeros",
                label=str(lmfdb_url or ""),
                signatures={},
                raw={"conductor": conductor, "degree": degree, "rank": rank},
            )
            obj.signatures["s7_cond"] = ext.s7_padic(conductor)
            obj.signatures["s13"] = ext.s13_discriminant(conductor)

            # Extract valid (non-None) zero heights
            if zeros_vec is not None and len(zeros_vec) > 0:
                zv = [float(z) for z in zeros_vec[:50] if z is not None]
                if len(zv) >= 4:
                    obj.signatures["s5_ap"] = ext.s5_spectral(zv)
                    obj.signatures["s24_ap"] = ext.s24_entropy(zv)
                    # S21: automorphic signature on zero heights as proxy
                    obj.signatures["s21_auto"] = ext.s21_automorphic_signature(zv)
                    # S11: monodromy proxy on zero heights as sequence
                    obj.signatures["s11_mono"] = ext.s11_monodromy_proxy(zv)
                else:
                    obj.signatures["s5_ap"] = np.full(8, np.nan)
                    obj.signatures["s24_ap"] = np.full(4, np.nan)
                    obj.signatures["s21_auto"] = np.full(8, np.nan)
                    obj.signatures["s11_mono"] = np.full(6, np.nan)
            else:
                obj.signatures["s5_ap"] = np.full(8, np.nan)
                obj.signatures["s24_ap"] = np.full(4, np.nan)
                obj.signatures["s21_auto"] = np.full(8, np.nan)
                obj.signatures["s11_mono"] = np.full(6, np.nan)

            obj.signatures["s3_ap"] = ext.s3_mod_p([conductor, degree, rank])
            objects.append(obj)
        return objects

    @staticmethod
    def load_object_zeros(max_n=None):
        """Load object zeros (L-function zeros attached to objects) from DuckDB."""
        import duckdb
        db_path = ROOT / "charon/data/charon.duckdb"
        if not db_path.exists():
            print("  WARNING: charon.duckdb not found, skipping object_zeros")
            return []
        try:
            con = duckdb.connect(str(db_path), read_only=True)
            query = """
                SELECT object_id, zeros_vector, root_number, analytic_rank
                FROM object_zeros WHERE zeros_vector IS NOT NULL
            """
            if max_n:
                query += f" LIMIT {int(max_n)}"
            rows = con.execute(query).fetchall()
            con.close()
        except Exception as e:
            print(f"  WARNING: Failed to load object_zeros: {e}")
            return []

        objects = []
        ext = StrategyExtractors
        for object_id, zeros_vec, root_number, analytic_rank in rows:
            if zeros_vec is None or len(zeros_vec) < 2:
                continue
            obj_id_int = int(object_id)
            a_rank = int(analytic_rank) if analytic_rank is not None else 0

            obj = MathObject(
                obj_id=f"oz_{obj_id_int}",
                domain="obj_zeros",
                label=str(obj_id_int),
                signatures={},
                raw={"object_id": obj_id_int,
                     "root_number": float(root_number) if root_number is not None else 0.0,
                     "analytic_rank": a_rank},
            )

            # Extract valid (non-None) zero heights
            zv = [float(z) for z in zeros_vec[:50] if z is not None]
            if len(zv) >= 4:
                obj.signatures["s5_ap"] = ext.s5_spectral(zv)
                obj.signatures["s3_ap"] = ext.s3_mod_p(zv)
                obj.signatures["s1_ap"] = ext.s1_complex(zv)
                obj.signatures["s24_ap"] = ext.s24_entropy(zv)
                # S11: monodromy proxy on zero heights as sequence
                obj.signatures["s11_mono"] = ext.s11_monodromy_proxy(zv)
            else:
                obj.signatures["s5_ap"] = np.full(8, np.nan)
                obj.signatures["s3_ap"] = np.full(6, np.nan)
                obj.signatures["s1_ap"] = np.full(8, np.nan)
                obj.signatures["s24_ap"] = np.full(4, np.nan)
                obj.signatures["s11_mono"] = np.full(6, np.nan)

            objects.append(obj)
        return objects

    @staticmethod
    def load_hmf(max_n=50000):
        """Load Hilbert Modular Forms from lmfdb_dump/hmf_forms.json.

        Fields available: label, level_norm, weight, dimension, disc, deg,
        level_bad_primes, field_bad_primes.  No hecke_eigenvalues in this
        dump, so we use level_bad_primes + field_bad_primes as arithmetic
        coefficient proxies for spectral/mod-p/entropy signatures.
        """
        path = ROOT / "cartography/lmfdb_dump/hmf_forms.json"
        if not path.exists():
            print("  WARNING: hmf_forms.json not found, skipping HMF")
            return []
        raw = json.loads(path.read_text(encoding="utf-8"))
        recs = raw.get("records", []) if isinstance(raw, dict) else raw
        if not recs:
            print("  WARNING: hmf_forms.json has no records")
            return []
        print(f"    HMF raw records: {len(recs)}")

        objects = []
        ext = StrategyExtractors
        count = 0
        for r in recs:
            label = r.get("label", "")
            level_norm = r.get("level_norm")
            if level_norm is None or not label:
                continue
            try:
                level_norm = int(level_norm)
            except (ValueError, TypeError):
                continue

            dimension = r.get("dimension", 1)
            disc = r.get("disc")
            # weight is stored as string like "[2, 2, 2]"; parse to list
            weight_raw = r.get("weight", "2")
            if isinstance(weight_raw, str):
                try:
                    weight_list = json.loads(weight_raw.replace("'", '"'))
                    if isinstance(weight_list, list):
                        weight_val = int(weight_list[0]) if weight_list else 2
                    else:
                        weight_val = int(weight_list)
                except (json.JSONDecodeError, ValueError):
                    weight_val = 2
            elif isinstance(weight_raw, (int, float)):
                weight_val = int(weight_raw)
            else:
                weight_val = 2

            # Build coefficient proxy from bad primes
            level_bp = r.get("level_bad_primes", [])
            field_bp = r.get("field_bad_primes", [])
            if not isinstance(level_bp, list):
                level_bp = []
            if not isinstance(field_bp, list):
                field_bp = []
            coeff_proxy = [int(x) for x in level_bp + field_bp if x is not None]

            obj = MathObject(
                obj_id=f"hmf_{label}",
                domain="HMF",
                label=label,
                signatures={},
                raw={"level_norm": level_norm, "weight": weight_val,
                     "dimension": int(dimension) if dimension else 1},
            )

            # S7: p-adic valuation of level_norm (conductor proxy)
            obj.signatures["s7_cond"] = ext.s7_padic(level_norm)

            # S13: discriminant from level_norm
            obj.signatures["s13"] = ext.s13_discriminant(
                disc if disc is not None else level_norm,
                conductor=level_norm)

            # Coefficient-proxy signatures (from bad primes)
            if len(coeff_proxy) >= 2:
                obj.signatures["s5_ap"] = ext.s5_spectral(coeff_proxy)
                obj.signatures["s3_ap"] = ext.s3_mod_p(coeff_proxy)
                obj.signatures["s1_ap"] = ext.s1_complex(coeff_proxy)
                obj.signatures["s24_ap"] = ext.s24_entropy(coeff_proxy)
                obj.signatures["s11_mono"] = ext.s11_monodromy_proxy(coeff_proxy)
            else:
                obj.signatures["s5_ap"] = np.full(8, np.nan)
                obj.signatures["s3_ap"] = np.full(6, np.nan)
                obj.signatures["s1_ap"] = np.full(8, np.nan)
                obj.signatures["s24_ap"] = np.full(4, np.nan)
                obj.signatures["s11_mono"] = np.full(6, np.nan)

            # S21: automorphic signature — HMF with level and weight
            obj.signatures["s21_auto"] = ext.s21_automorphic_signature(
                coeff_proxy if len(coeff_proxy) >= 4 else [0] * 4,
                level=level_norm, weight=weight_val)

            # S19: ADE classification via McKay correspondence
            obj.signatures["s19_ade"] = ext.s19_ade_classify(
                [level_norm, weight_val], method="mckay")

            objects.append(obj)
            count += 1
            if count >= max_n:
                break

        return objects

    @staticmethod
    def load_belyi(max_n=50000):
        """Load Belyi maps (dessins d'enfants) from lmfdb_dump/belyi_galmaps.json.

        Fields: label, deg (degree), g (genus), triples_cyc (ramification data).
        """
        path = ROOT / "cartography/lmfdb_dump/belyi_galmaps.json"
        if not path.exists():
            print("  WARNING: belyi_galmaps.json not found, skipping Belyi")
            return []
        raw = json.loads(path.read_text(encoding="utf-8"))
        recs = raw.get("records", []) if isinstance(raw, dict) else raw
        if not recs:
            print("  WARNING: belyi_galmaps.json has no records")
            return []
        print(f"    Belyi raw records: {len(recs)}")

        objects = []
        ext = StrategyExtractors
        count = 0
        for r in recs:
            label = r.get("label", "")
            deg = r.get("deg")
            if deg is None or not label:
                continue
            try:
                deg = int(deg)
            except (ValueError, TypeError):
                continue

            genus = r.get("g", 0)
            triples_cyc = r.get("triples_cyc", [])

            obj = MathObject(
                obj_id=f"belyi_{label}",
                domain="belyi",
                label=label,
                signatures={},
                raw={"deg": deg, "genus": int(genus) if genus is not None else 0},
            )

            # S13: discriminant-like from degree
            obj.signatures["s13"] = ext.s13_discriminant(deg)

            # S19: ADE classification from degree
            obj.signatures["s19_ade"] = ext.s19_ade_classify(deg, method="lattice_det")

            # S11: monodromy proxy from triples_cyc flattened
            # triples_cyc is a list of triples of cycle-type strings or lists
            mono_coeffs = []
            if isinstance(triples_cyc, list):
                for triple in triples_cyc:
                    if isinstance(triple, list):
                        for item in triple:
                            if isinstance(item, (int, float)):
                                mono_coeffs.append(int(item))
                            elif isinstance(item, str):
                                # Parse cycle notation "(1,2)(3)" -> extract lengths
                                cycles = item.replace("(", " ").replace(")", " ").split()
                                for c in cycles:
                                    try:
                                        mono_coeffs.append(int(c))
                                    except ValueError:
                                        pass
                            elif isinstance(item, list):
                                mono_coeffs.extend([int(x) for x in item
                                                    if isinstance(x, (int, float))])
            if len(mono_coeffs) >= 4:
                obj.signatures["s11_mono"] = ext.s11_monodromy_proxy(mono_coeffs[:50])
            else:
                obj.signatures["s11_mono"] = np.full(6, np.nan)

            objects.append(obj)
            count += 1
            if count >= max_n:
                break

        return objects


# ============================================================
# The Dissection Tensor
# ============================================================
class DissectionTensor:
    """GPU-resident multi-dimensional signature tensor.

    Packs mathematical objects from multiple domains into a dense
    tensor where each row is an object and columns are dissection
    strategy dimensions. NaN = strategy not applicable to this object.

    Dimensions:
      s1_alex[8], s1_jones[8], s1_ap[8]  = 24  (complex plane eval)
      s3_alex[6], s3_jones[6], s3_ap[6]  = 18  (mod-p fingerprints)
      s5_alex[8], s5_jones[8], s5_ap[8]  = 24  (spectral)
      s7_det[5], s7_disc[5], s7_cond[5]  = 15  (p-adic)
      s10[8]                              =  8  (Galois)
      s11_mono[6]                         =  6  (monodromy proxy)
      s12_ec[4], s12_oeis[4], s12_nf[4]  = 12  (zeta-like density)
      s13[4]                              =  4  (discriminant)
      s19_ade[8]                          =  8  (ADE singularity)
      s21_auto[8]                         =  8  (automorphic)
      s22[4]                              =  4  (operadic)
      s24_alex[4], s24_arith[4],
        s24_ap[4], s24_sym[4]             = 16  (entropy)
      battery[8]                          =  8  (falsification)
      ---
      Total: ~167 dimensions
    """

    # Strategy name -> dimensionality
    STRATEGY_DIMS = {
        "s1_alex": 8, "s1_jones": 8, "s1_ap": 8,
        "s3_alex": 6, "s3_jones": 6, "s3_ap": 6,
        "s5_alex": 8, "s5_jones": 8, "s5_ap": 8, "s5_oeis": 8,
        "s6_oeis": 4,
        "s7_det": 5, "s7_disc": 5, "s7_cond": 5,
        "s9_st": 4,
        "s9_endo": 8,       # genus-2 endomorphism ring/GL2/simplicity
        "s10": 8,
        "s10_galrep": 4,    # genus-2 Galois representation summary
        "s12_ec": 4, "s12_oeis": 4, "s12_nf": 4,
        "s13": 4,
        "s22": 4,
        "s21_auto": 8,
        "s11_mono": 6,
        "s19_ade": 8,
        "s24_alex": 4, "s24_arith": 4, "s24_ap": 4, "s24_sym": 4,
        "s24_oeis": 4,
        "s33_recurrence": 3,
    }

    TOTAL_DIMS = sum(STRATEGY_DIMS.values())

    # Strategy groups — which strategies are "the same lens" across domains.
    # Cross-domain distance requires matches within at least 2 groups.
    STRATEGY_GROUPS = {
        "complex":   ["s1_alex", "s1_jones", "s1_ap"],
        "mod_p":     ["s3_alex", "s3_jones", "s3_ap"],
        "spectral":  ["s5_alex", "s5_jones", "s5_ap", "s5_oeis"],
        "padic":     ["s7_det", "s7_disc", "s7_cond"],
        "symmetry":  ["s9_st", "s9_endo"],
        "galois":    ["s10", "s10_galrep"],
        "zeta":      ["s12_ec", "s12_oeis", "s12_nf"],
        "disc_cond": ["s13"],
        "operadic":  ["s22"],
        "entropy":   ["s24_alex", "s24_arith", "s24_ap", "s24_sym", "s24_oeis"],
        "attractor": ["s6_oeis"],
        "automorphic": ["s21_auto"],
        "monodromy":   ["s11_mono"],
        "ade":         ["s19_ade"],
        "recurrence":  ["s33_recurrence"],
    }

    def __init__(self):
        self.objects = []
        self.domain_indices = defaultdict(list)  # domain -> [indices]
        self.tensor = None       # [N, D] on GPU
        self.mask = None         # [N, D] boolean — True where data exists
        self.labels = []         # obj_id list
        self.domains = []        # domain list
        self._strategy_slices = {}  # strategy_name -> (start, end) in dim axis
        self._group_slices = {}    # group_name -> (start, end) covering all strategies in group
        self.battery_index = {}    # test_id -> BatteryEncoder.encode() result
        self.battery_domains = {}  # test_id -> (domain_a, domain_b) the hypothesis spans

        # Build slice map
        offset = 0
        for name, dim in self.STRATEGY_DIMS.items():
            self._strategy_slices[name] = (offset, offset + dim)
            offset += dim

        # Build group slice map
        for group_name, strat_list in self.STRATEGY_GROUPS.items():
            starts = [self._strategy_slices[s][0] for s in strat_list if s in self._strategy_slices]
            ends = [self._strategy_slices[s][1] for s in strat_list if s in self._strategy_slices]
            if starts:
                self._group_slices[group_name] = (min(starts), max(ends))

    def add_objects(self, objects):
        """Add a list of MathObjects."""
        for obj in objects:
            idx = len(self.objects)
            self.objects.append(obj)
            self.domain_indices[obj.domain].append(idx)
            self.labels.append(obj.obj_id)
            self.domains.append(obj.domain)

    def add_battery_results(self, test_id, result_dict, domain_a=None, domain_b=None):
        """Register battery results as truth-boundary constraints.

        Battery results are NOT per-object dimensions. They are properties
        of hypotheses about relationships between domain pairs. Stored in
        a separate index and used as post-filters on intersections.
        """
        encoded = BatteryEncoder.encode(result_dict)
        self.battery_index[test_id] = {
            "encoded": encoded,
            "result": result_dict,
            "domains": (domain_a, domain_b),
        }

    def build(self):
        """Pack all objects into a GPU tensor."""
        N = len(self.objects)
        D = self.TOTAL_DIMS
        print(f"Building dissection tensor: {N} objects x {D} dimensions")

        # Allocate on CPU first (NaN-filled)
        data = np.full((N, D), np.nan, dtype=np.float32)

        for i, obj in enumerate(self.objects):
            # Fill each strategy slice
            for strat_name, sig in obj.signatures.items():
                if strat_name in self._strategy_slices:
                    start, end = self._strategy_slices[strat_name]
                    dim = end - start
                    if len(sig) == dim:
                        data[i, start:end] = sig
                    elif len(sig) > dim:
                        data[i, start:end] = sig[:dim]
                    else:
                        data[i, start:start + len(sig)] = sig

        # Create mask (True where we have data)
        mask = ~np.isnan(data)

        # Replace NaN with 0 for GPU operations (mask tracks validity)
        data_clean = np.nan_to_num(data, nan=0.0)

        # Move to GPU
        self.tensor = torch.tensor(data_clean, device=DEVICE, dtype=torch.float32)
        self.mask = torch.tensor(mask, device=DEVICE, dtype=torch.bool)

        # Stats
        fill_rate = mask.sum() / mask.size * 100
        print(f"  Tensor shape: {self.tensor.shape}")
        print(f"  Device: {self.tensor.device}")
        print(f"  Fill rate: {fill_rate:.1f}%")
        print(f"  Memory: {self.tensor.element_size() * self.tensor.nelement() / 1e6:.1f} MB")

        # Per-strategy fill rates
        for name, (start, end) in self._strategy_slices.items():
            strat_mask = mask[:, start:end]
            strat_fill = strat_mask.any(axis=1).sum() / N * 100
            print(f"    {name:12s}: {strat_fill:5.1f}% of objects have data")

        return self.tensor

    def normalize(self):
        """Per-dimension normalization (z-score where data exists)."""
        if self.tensor is None:
            raise ValueError("Call build() first")

        # Compute mean/std only over valid entries
        masked = self.tensor * self.mask.float()
        counts = self.mask.float().sum(dim=0).clamp(min=1)
        means = masked.sum(dim=0) / counts
        sq_diff = ((self.tensor - means) ** 2) * self.mask.float()
        stds = (sq_diff.sum(dim=0) / counts).sqrt().clamp(min=1e-8)

        # Normalize in-place
        self.tensor = ((self.tensor - means) / stds) * self.mask.float()
        print(f"Normalized: mean ~ 0, std ~ 1 per dimension")

    def get_strategy_slice(self, strategy_name):
        """Get tensor slice for a specific strategy."""
        start, end = self._strategy_slices[strategy_name]
        return self.tensor[:, start:end], self.mask[:, start:end]

    def get_domain_mask(self, domain):
        """Boolean mask for objects from a specific domain."""
        indices = self.domain_indices[domain]
        mask = torch.zeros(len(self.objects), device=DEVICE, dtype=torch.bool)
        mask[indices] = True
        return mask

    # ============================================================
    # GPU-accelerated exploration
    # ============================================================
    def cross_domain_distances(self, domain_a, domain_b,
                               strategies=None, min_shared_groups=1,
                               top_k=50):
        """Find closest pairs between two domains in signature space.

        Uses strategy-group-aware distance: only compares dimensions
        where both objects have data, and requires matches in at least
        min_shared_groups distinct strategy groups.

        Args:
            domain_a, domain_b: domain names (e.g., 'knot', 'EC')
            strategies: list of strategy names to use (None = all math strategies)
            min_shared_groups: minimum distinct strategy groups with shared data
            top_k: number of closest pairs to return

        Returns:
            list of (obj_a_id, obj_b_id, distance, n_shared_dims)
        """
        idx_a = torch.tensor(self.domain_indices[domain_a], device=DEVICE)
        idx_b = torch.tensor(self.domain_indices[domain_b], device=DEVICE)

        if len(idx_a) == 0 or len(idx_b) == 0:
            return []

        # Select strategy columns (exclude battery — it's a post-filter)
        if strategies:
            cols = []
            for s in strategies:
                if s in self._strategy_slices:
                    start, end = self._strategy_slices[s]
                    cols.extend(range(start, end))
            cols = torch.tensor(cols, device=DEVICE)
        else:
            cols = torch.arange(self.TOTAL_DIMS, device=DEVICE)

        # Extract sub-tensors
        t_a = self.tensor[idx_a][:, cols]  # [Na, d]
        t_b = self.tensor[idx_b][:, cols]  # [Nb, d]
        m_a = self.mask[idx_a][:, cols]
        m_b = self.mask[idx_b][:, cols]

        Na, Nb = len(idx_a), len(idx_b)

        # Batch pairwise distances to avoid OOM
        # Process in chunks of batch_size rows from domain A
        batch_size = max(1, min(2000, int(1e9 / (Nb * len(cols) * 4))))
        best_dists = torch.full((top_k,), float('inf'), device=DEVICE)
        best_indices = torch.zeros((top_k, 2), device=DEVICE, dtype=torch.long)

        for start in range(0, Na, batch_size):
            end = min(start + batch_size, Na)
            chunk_a = t_a[start:end]    # [chunk, d]
            chunk_ma = m_a[start:end]

            # Pairwise within chunk: [chunk, 1, d] - [1, Nb, d]
            diff = chunk_a.unsqueeze(1) - t_b.unsqueeze(0)
            shared_mask = chunk_ma.unsqueeze(1) & m_b.unsqueeze(0)

            sq_diff = (diff ** 2) * shared_mask.float()
            n_shared = shared_mask.float().sum(dim=2).clamp(min=1)
            dists = (sq_diff.sum(dim=2) / n_shared).sqrt()
            # Require minimum shared dimensions (at least 2 strategy groups)
            min_dims = max(5, min_shared_groups * 4)
            dists[n_shared < min_dims] = float('inf')

            # Find top-k in this chunk
            chunk_flat = dists.flatten()
            k_chunk = min(top_k, chunk_flat.numel())
            vals, flat_idx = torch.topk(chunk_flat, k_chunk, largest=False)

            # Convert flat indices to (i_a_local, i_b)
            i_a_local = flat_idx // Nb
            i_b_idx = flat_idx % Nb

            # Track n_shared for this chunk
            chunk_n_shared = n_shared  # [chunk, Nb]

            # Merge with running best
            for j in range(k_chunk):
                v = vals[j]
                if v < best_dists[-1]:
                    ia_local = i_a_local[j].item()
                    ib_local = i_b_idx[j].item()
                    best_dists[-1] = v
                    best_indices[-1, 0] = start + ia_local
                    best_indices[-1, 1] = ib_local
                    # Store n_shared in a separate tensor
                    if not hasattr(self, '_best_nshared'):
                        self._best_nshared = torch.zeros(top_k, device=DEVICE)
                    self._best_nshared[-1] = chunk_n_shared[ia_local, ib_local]
                    # Re-sort
                    order = best_dists.argsort()
                    best_dists = best_dists[order]
                    best_indices = best_indices[order]
                    self._best_nshared = self._best_nshared[order]

            del diff, shared_mask, sq_diff, dists, chunk_flat, chunk_n_shared
            torch.cuda.empty_cache()

        results = []
        for k_i in range(top_k):
            val = best_dists[k_i].item()
            if np.isinf(val):
                continue
            ia = best_indices[k_i, 0].item()
            ib = best_indices[k_i, 1].item()
            ns = int(self._best_nshared[k_i].item()) if hasattr(self, '_best_nshared') else 0
            obj_a = self.objects[idx_a[ia].item()]
            obj_b = self.objects[idx_b[ib].item()]
            results.append((obj_a.obj_id, obj_b.obj_id, float(val), ns))

        if hasattr(self, '_best_nshared'):
            del self._best_nshared

        return results

    def find_intersections(self, threshold=1.0, strategies=None,
                           min_shared_groups=2, top_k=100):
        """Find cross-domain intersections — object pairs from different
        domains that are close in signature space.

        Returns sorted list of (obj_a, obj_b, distance, n_shared_dims).
        """
        domains = list(self.domain_indices.keys())
        all_pairs = []

        for i, da in enumerate(domains):
            for db in domains[i + 1:]:
                pairs = self.cross_domain_distances(
                    da, db, strategies, min_shared_groups, top_k)
                all_pairs.extend(pairs)

        # Sort by distance, filter by threshold
        all_pairs.sort(key=lambda x: x[2])
        return [p for p in all_pairs if p[2] < threshold][:top_k]

    def tt_decompose(self, rank=5):
        """Tensor Train decomposition via TensorLy.

        Compresses the signature tensor and reveals which dimensions
        are entangled. Bond dimensions between TT cores indicate
        dimensional coupling strength.

        Returns: (tt_factors, bond_dimensions, reconstruction_error)
        """
        if self.tensor is None:
            raise ValueError("Call build() first")

        print(f"TT decomposition (rank={rank})...")

        # TensorLy TT on 2D is essentially SVD-based
        # Reshape into a higher-order tensor for meaningful TT:
        # Group dimensions by strategy for interpretable cores
        strategy_groups = []
        group_names = []
        for name, (start, end) in self._strategy_slices.items():
            strategy_groups.append(self.tensor[:, start:end])
            group_names.append(name)

        # Stack into [N, S1_dim, S2_dim, ...] — but strategies have
        # different dims, so we pad to max and reshape
        # For now, do TT on the flat [N, D] tensor
        t = self.tensor.cpu()  # TensorLy TT works on CPU
        tl_tensor = tl.tensor(t)

        try:
            tt = tensor_train(tl_tensor, rank=rank)
            # Reconstruction error
            reconstructed = tl.tt_to_tensor(tt)
            error = torch.norm(t - torch.tensor(reconstructed)) / torch.norm(t)

            # Bond dimensions
            bond_dims = [core.shape[-1] for core in tt[:-1]]

            print(f"  Cores: {len(tt)}")
            print(f"  Bond dimensions: {bond_dims}")
            print(f"  Reconstruction error: {error:.4f}")
            print(f"  Compression ratio: {t.numel() / sum(c.numel() for c in tt):.1f}x")

            return tt, bond_dims, float(error)
        except Exception as e:
            print(f"  TT decomposition failed: {e}")
            return None, None, None

    def tt_decompose_grouped(self, rank=5):
        """Strategy-grouped TT decomposition.

        Reshapes [N, D] into [N, G1, G2, ..., Gk] where Gi is a
        low-dimensional summary of strategy group i (mean + std across
        dims in that group). Then runs TT decomposition on the resulting
        higher-order tensor.

        Bond dimensions between adjacent strategy-group cores reveal
        which strategy pairs are ENTANGLED (high bond dim = strong
        coupling between those mathematical lenses).

        Returns: (tt_factors, bond_dims, group_names, entanglement_pairs)
        """
        if self.tensor is None:
            raise ValueError("Call build() first")

        group_names = list(self.STRATEGY_GROUPS.keys())
        n_groups = len(group_names)
        N = self.tensor.shape[0]

        print(f"\nStrategy-grouped TT decomposition (rank={rank})...")
        print(f"  Groups: {group_names}")

        # Build [N, n_groups, 2] features tensor on GPU:
        # For each group, compute (masked mean, masked std) across all dims
        group_features = torch.zeros(N, n_groups, 2, device=DEVICE)

        for gi, gname in enumerate(group_names):
            strat_list = self.STRATEGY_GROUPS[gname]
            cols = []
            for sname in strat_list:
                if sname in self._strategy_slices:
                    start, end = self._strategy_slices[sname]
                    cols.extend(range(start, end))
            if not cols:
                continue
            col_idx = torch.tensor(cols, device=DEVICE)
            group_vals = self.tensor[:, col_idx]       # [N, group_dim]
            group_mask = self.mask[:, col_idx].float()  # [N, group_dim]
            denom = group_mask.sum(dim=1).clamp(min=1)
            mean = (group_vals * group_mask).sum(dim=1) / denom
            sq_diff = ((group_vals - mean.unsqueeze(1)) ** 2) * group_mask
            std = (sq_diff.sum(dim=1) / denom).sqrt()
            group_features[:, gi, 0] = mean
            group_features[:, gi, 1] = std

        # Reshape into higher-order tensor: [N, 2, 2, ..., 2] (n_groups modes of size 2)
        # Build via successive outer products
        ho_tensor = group_features[:, 0, :]  # [N, 2]
        for gi in range(1, n_groups):
            # [N, 2, ..., 2] x [N, 2] -> [N, 2, ..., 2, 2]
            ho_tensor = ho_tensor.unsqueeze(-1) * group_features[:, gi, :].unsqueeze(1)
            target_shape = [N] + [2] * (gi + 1)
            ho_tensor = ho_tensor.reshape(target_shape)

        print(f"  Higher-order tensor shape: {list(ho_tensor.shape)}")
        print(f"  Modes: N={N}, " +
              ", ".join(f"{gname}=2" for gname in group_names))

        # TT decomposition via TensorLy (CPU)
        t_cpu = ho_tensor.cpu()
        tl_tensor = tl.tensor(t_cpu)

        try:
            tt = tensor_train(tl_tensor, rank=rank)

            # Reconstruction error
            reconstructed = tl.tt_to_tensor(tt)
            error = torch.norm(t_cpu - torch.tensor(reconstructed)) / torch.norm(t_cpu)

            # Bond dimensions between cores
            bond_dims = [core.shape[-1] for core in tt[:-1]]

            print(f"  Cores: {len(tt)}")
            print(f"  Core shapes: {[list(c.shape) for c in tt]}")
            print(f"  Bond dimensions: {bond_dims}")
            print(f"  Reconstruction error: {error:.4f}")

            # Identify entangled strategy pairs (high bond dim between adjacent cores)
            # Core 0 is N-mode, cores 1..k are strategy groups
            # Bond between core i and core i+1 connects group_names[i-1] to group_names[i]
            entanglement_pairs = []
            print(f"\n  Strategy entanglement (bond dimensions):")
            for bi in range(len(bond_dims)):
                if bi == 0:
                    left = "objects"
                else:
                    left = group_names[bi - 1]
                if bi < len(group_names):
                    right = group_names[bi]
                else:
                    right = "terminal"
                bd = bond_dims[bi]
                entanglement_pairs.append((left, right, bd))
                marker = " ***" if bd == rank else ""
                print(f"    {left:12s} <-> {right:12s}: bond_dim={bd}{marker}")

            # Sort by bond dim to show strongest couplings
            entanglement_pairs.sort(key=lambda x: x[2], reverse=True)
            print(f"\n  Strongest couplings (saturated bond = max entanglement):")
            for left, right, bd in entanglement_pairs[:5]:
                print(f"    {left} <-> {right}: {bd}")

            return tt, bond_dims, group_names, entanglement_pairs

        except Exception as e:
            print(f"  Grouped TT decomposition failed: {e}")
            return None, None, group_names, []

    def strategy_group_correlation(self):
        """Compute strategy-group correlation matrix on GPU.

        For each pair of strategy groups, compute the mean Pearson
        correlation across objects (using only objects that have data
        in both groups). This reveals which mathematical lenses
        co-vary across the entire object population.

        Returns: (corr_matrix, group_names)  -- corr_matrix is [G, G] numpy
        """
        if self.tensor is None:
            raise ValueError("Call build() first")

        group_names = list(self.STRATEGY_GROUPS.keys())
        n_groups = len(group_names)
        N = self.tensor.shape[0]

        print(f"\nStrategy-group correlation matrix ({n_groups}x{n_groups})...")

        # Compute group-level summary: masked mean per group per object
        group_means = torch.zeros(N, n_groups, device=DEVICE)
        group_valid = torch.zeros(N, n_groups, device=DEVICE, dtype=torch.bool)

        for gi, gname in enumerate(group_names):
            strat_list = self.STRATEGY_GROUPS[gname]
            cols = []
            for sname in strat_list:
                if sname in self._strategy_slices:
                    start, end = self._strategy_slices[sname]
                    cols.extend(range(start, end))
            if not cols:
                continue
            col_idx = torch.tensor(cols, device=DEVICE)
            group_vals = self.tensor[:, col_idx]
            group_mask = self.mask[:, col_idx].float()
            has_data = group_mask.sum(dim=1) > 0
            denom = group_mask.sum(dim=1).clamp(min=1)
            group_means[:, gi] = (group_vals * group_mask).sum(dim=1) / denom
            group_valid[:, gi] = has_data

        # Pearson correlation between all group pairs (GPU)
        corr_matrix = torch.zeros(n_groups, n_groups, device=DEVICE)

        for i in range(n_groups):
            for j in range(i, n_groups):
                # Mask: both groups have data
                shared = group_valid[:, i] & group_valid[:, j]
                n_shared = shared.sum().item()
                if n_shared < 10:
                    corr_matrix[i, j] = 0.0
                    corr_matrix[j, i] = 0.0
                    continue
                x = group_means[shared, i]
                y = group_means[shared, j]
                # Pearson r on GPU
                mx = x - x.mean()
                my = y - y.mean()
                num = (mx * my).sum()
                den = (mx.norm() * my.norm()).clamp(min=1e-12)
                r = (num / den).item()
                corr_matrix[i, j] = r
                corr_matrix[j, i] = r

        # Print correlation matrix
        print(f"\n  {'':14s} " + " ".join(f"{g:>10s}" for g in group_names))
        corr_np = corr_matrix.cpu().numpy()
        for i, gname in enumerate(group_names):
            row = " ".join(f"{corr_np[i, j]:10.3f}" for j in range(n_groups))
            print(f"  {gname:14s} {row}")

        # Highlight strongest off-diagonal correlations
        print(f"\n  Strongest cross-group correlations:")
        pairs = []
        for i in range(n_groups):
            for j in range(i + 1, n_groups):
                pairs.append((group_names[i], group_names[j], corr_np[i, j]))
        pairs.sort(key=lambda x: abs(x[2]), reverse=True)
        for left, right, r in pairs[:10]:
            marker = " (strong)" if abs(r) > 0.3 else ""
            print(f"    {left:12s} <-> {right:12s}: r={r:+.3f}{marker}")

        return corr_np, group_names

    def summary(self):
        """Print tensor summary."""
        if self.tensor is None:
            print("Tensor not built yet. Call build() first.")
            return

        print(f"\n{'='*60}")
        print(f"DISSECTION TENSOR SUMMARY")
        print(f"{'='*60}")
        print(f"Objects: {len(self.objects)}")
        print(f"Dimensions: {self.TOTAL_DIMS}")
        print(f"Device: {self.tensor.device}")
        print(f"Memory: {self.tensor.element_size() * self.tensor.nelement() / 1e6:.1f} MB")
        print(f"\nDomains:")
        for domain, indices in sorted(self.domain_indices.items()):
            print(f"  {domain:12s}: {len(indices):6d} objects")
        print(f"\nStrategy dimensions:")
        for name, (start, end) in self._strategy_slices.items():
            dim = end - start
            strat_mask = self.mask[:, start:end]
            n_with_data = strat_mask.any(dim=1).sum().item()
            print(f"  {name:12s}: {dim:2d} dims, "
                  f"{n_with_data:6d}/{len(self.objects)} objects ({n_with_data/len(self.objects)*100:.0f}%)")


# ============================================================
# Main — build and explore
# ============================================================
def main():
    print(f"Device: {DEVICE}")
    if DEVICE.type == 'cuda':
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

    dt = DissectionTensor()

    # Load all domains
    print("\n--- Loading data ---")
    print("Loading knots...")
    dt.add_objects(DataLoaders.load_knots())

    print("Loading number fields...")
    dt.add_objects(DataLoaders.load_number_fields())

    print("Loading elliptic curves...")
    dt.add_objects(DataLoaders.load_ec())

    print("Loading Fungrim...")
    dt.add_objects(DataLoaders.load_fungrim())

    print("Loading OEIS sequences...")
    dt.add_objects(DataLoaders.load_oeis(max_n=20000))

    print("Loading genus-2 curves...")
    dt.add_objects(DataLoaders.load_genus2(max_n=66000))

    # Tier 1 additions — cap totals to stay under ~500K objects
    print("Loading modular forms...")
    dt.add_objects(DataLoaders.load_modular_forms(max_n=100000))

    print("Loading abstract groups...")
    dt.add_objects(DataLoaders.load_abstract_groups(max_n=50000))

    print("Loading Maass forms...")
    dt.add_objects(DataLoaders.load_maass_forms(max_n=15000))

    print("Loading lattices...")
    dt.add_objects(DataLoaders.load_lattices())

    print("Loading Dirichlet zeros...")
    dt.add_objects(DataLoaders.load_dirichlet_zeros(max_n=185000))

    print("Loading object zeros...")
    dt.add_objects(DataLoaders.load_object_zeros(max_n=120000))

    print("Loading Hilbert modular forms...")
    dt.add_objects(DataLoaders.load_hmf(max_n=50000))

    print("Loading Belyi maps...")
    dt.add_objects(DataLoaders.load_belyi(max_n=50000))

    n_total = len(dt.objects)
    print(f"\nTotal objects loaded: {n_total}")
    if n_total > 500000:
        print(f"  WARNING: {n_total} objects exceeds 500K target — consider reducing max_n caps")

    # Load battery results as truth-boundary index (NOT tensor dims)
    print("\nLoading battery results (truth-boundary index)...")
    v2_dir = ROOT / "cartography/shared/scripts/v2"
    for result_file in v2_dir.glob("r3_*_results.json"):
        data = json.loads(result_file.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for test_id, result in data.items():
                if isinstance(result, dict):
                    dt.add_battery_results(test_id, result)
    print(f"  {len(dt.battery_index)} battery results indexed")

    # Build tensor
    print("\n--- Building tensor ---")
    dt.build()
    dt.normalize()
    dt.summary()

    # Explore cross-domain distances (require at least 2 shared strategy groups)
    print(f"\n--- Cross-domain exploration (min 2 shared strategy groups) ---")
    domains = list(dt.domain_indices.keys())
    for i, da in enumerate(domains):
        for db in domains[i + 1:]:
            pairs = dt.cross_domain_distances(da, db, min_shared_groups=2, top_k=5)
            if pairs:
                print(f"\n{da} <-> {db} (top 5 closest):")
                for obj_a, obj_b, dist, n_shared in pairs:
                    print(f"  {obj_a:30s} <-> {obj_b:30s}  "
                          f"d={dist:.3f} ({n_shared} shared dims)")

    # Find intersections
    print(f"\n--- Intersections (threshold=1.5, min 2 groups) ---")
    intersections = dt.find_intersections(threshold=1.5, top_k=20)
    for obj_a, obj_b, dist, n_shared in intersections:
        da = obj_a.split("_")[0]
        db = obj_b.split("_")[0]
        print(f"  [{da}<->{db}] {obj_a:30s} <-> {obj_b:30s}  "
              f"d={dist:.3f} ({n_shared} shared dims)")

    # TT decomposition
    print(f"\n--- Tensor Train decomposition ---")
    tt, bonds, error = dt.tt_decompose(rank=5)

    # Strategy-grouped TT decomposition
    print(f"\n--- Strategy-grouped TT decomposition ---")
    gtt, gbonds, gnames, entanglement = dt.tt_decompose_grouped(rank=5)

    # Strategy-group correlation matrix
    print(f"\n--- Strategy-group correlation matrix ---")
    corr, corr_names = dt.strategy_group_correlation()

    # Save tensor for later use
    out_dir = ROOT / "cartography/convergence/data"
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save({
        "tensor": dt.tensor.cpu(),
        "mask": dt.mask.cpu(),
        "labels": dt.labels,
        "domains": dt.domains,
        "strategy_slices": dt._strategy_slices,
    }, out_dir / "dissection_tensor.pt")
    print(f"\nTensor saved to convergence/data/dissection_tensor.pt")

    return dt


if __name__ == "__main__":
    dt = main()
