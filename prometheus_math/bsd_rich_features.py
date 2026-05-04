"""prometheus_math.bsd_rich_features — vectorizer for the rich BSD corpus.

Turns a ``RichBSDEntry`` into a fixed-length numpy feature vector
suitable for both linear REINFORCE and the MLP backend. The layout
combines:

  - Raw a_p (n_ap entries; default 20)            -> n_ap floats
  - Numerical features                             -> 9 floats
        log10(conductor)
        log10(max(1, conductor_radical))
        log_regulator               = log10(max(reg, 1e-9))
        log_real_period             = log10(max(omega, 1e-9))
        log_L1                      = log10(max(L1, 1e-9))
        log_sha_an                  = log10(max(sha_an, 1e-9))
        faltings_height (already log-scale per LMFDB convention)
        abc_quality
        szpiro_ratio
  - Tamagawa one-hot (Cp in {1,2,3,4,5,6,7,8,>=9}) -> 9 bits
  - Torsion-order one-hot (T in {1,2,3,4,5,6,7,8,9,10,12,>=12}) -> 12 bits
  - Torsion-structure shape one-hot                -> 6 bits
        () | (n,) | (2,) | (2, 2n) | (2, 2) | other
  - CM flag (1 bit if CM, else 0)                  -> 1 bit
  - Semistable flag                                -> 1 bit
  - signD signed indicator (-1, 0, +1)             -> 3 bits
  - Conductor-radical class (small-N bucket)       -> 5 bits

Total feature dimension = n_ap + 9 + 9 + 12 + 6 + 1 + 1 + 3 + 5
                       = n_ap + 46
With the default n_ap = 20 -> 66 features.

Why these choices (and what we explicitly skipped)
--------------------------------------------------
- Sato-Tate group: NOT a column on LMFDB ``ec_curvedata`` (verified
  2026-05-04). We could compute it from the CM discriminant + isogeny
  class structure, but for the modal-class ceiling test the existing
  CM flag captures the binary CM-vs-not signal that matters.
- ``ainvs``: already encoded by a_p (Cremona's aplist starts from
  ainvs).  Including raw ainvs would over-fit the Weierstrass form
  rather than the curve.
- ``isogeny_degrees``: structural but rare; deferred.
- ``sha_primes``: would dominate at the n=1000 scale; deferred.

The vectorizer is deterministic (no RNG) and pure: same input ->
same output, every time.
"""
from __future__ import annotations

import math
from typing import Sequence

import numpy as np

from ._bsd_rich_features import RichBSDEntry, RichFeatures


# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------


_TAMAGAWA_BUCKETS = (1, 2, 3, 4, 5, 6, 7, 8)  # plus a >=9 bucket
_TORSION_BUCKETS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12)  # plus >12 bucket
_TS_SHAPES = (
    "trivial",        # ()
    "cyclic",         # (n,) for n > 1
    "Z2",             # (2,)
    "Z2_x_Z2k",       # (2, 2k) for k >= 1
    "Z2_x_Z2",        # (2, 2)
    "other",
)
_RAD_BUCKETS = (1, 10, 100, 1000, 10000)  # 5 buckets, log-scaled boundaries


def _onehot(idx: int, n: int) -> np.ndarray:
    """Return an (n,) one-hot vector with a 1 at ``idx`` (clamped to [0, n))."""
    v = np.zeros(n, dtype=np.float64)
    if idx < 0:
        idx = 0
    if idx >= n:
        idx = n - 1
    v[idx] = 1.0
    return v


def _bucket_idx(value: int, buckets: Sequence[int]) -> int:
    """Bucket index for an integer ``value`` w.r.t. an exact-match list,
    with an implicit "above" bucket = ``len(buckets)``."""
    for i, b in enumerate(buckets):
        if value == b:
            return i
    return len(buckets)


def _tamagawa_idx(cp: int) -> int:
    return _bucket_idx(cp, _TAMAGAWA_BUCKETS)  # 0..8 (>=9 -> 8)


def _torsion_idx(t: int) -> int:
    return _bucket_idx(t, _TORSION_BUCKETS)  # 0..11 (>12 -> 11)


def _torsion_structure_idx(ts: Sequence[int]) -> int:
    n = len(ts)
    if n == 0:
        return 0
    if n == 1:
        if int(ts[0]) == 2:
            return 2
        return 1
    if n == 2:
        a, b = int(ts[0]), int(ts[1])
        if a == 2 and b == 2:
            return 4
        if a == 2 and b % 2 == 0 and b > 2:
            return 3
    return 5


def _signD_idx(sd: int) -> int:
    if sd > 0:
        return 0
    if sd == 0:
        return 1
    return 2


def _radical_idx(rad: int) -> int:
    """5-bin log-scaled bucket for the conductor radical."""
    rad = max(int(rad), 1)
    log_rad = math.log10(rad)
    if log_rad < 1.0:
        return 0
    if log_rad < 2.0:
        return 1
    if log_rad < 3.0:
        return 2
    if log_rad < 4.0:
        return 3
    return 4


# ---------------------------------------------------------------------------
# Public surface
# ---------------------------------------------------------------------------


def feature_dim(n_ap: int) -> int:
    """Return the total dimension of the vectorize_rich output."""
    n_tam = len(_TAMAGAWA_BUCKETS) + 1
    n_tor = len(_TORSION_BUCKETS) + 1
    n_ts = len(_TS_SHAPES)
    n_sd = 3
    n_rad = len(_RAD_BUCKETS)
    return int(n_ap + 9 + n_tam + n_tor + n_ts + 1 + 1 + n_sd + n_rad)


def vectorize_rich(entry: RichBSDEntry, n_ap: int = 20) -> np.ndarray:
    """Convert a ``RichBSDEntry`` to a fixed-length feature vector.

    The output is finite by construction: every transformation is
    log10(max(., eps)) or one-hot. Missing LMFDB fields fall back to
    their RichFeatures defaults (zeros / empty tuples) and produce
    zero blocks in the corresponding one-hot slots.
    """
    rich: RichFeatures = entry.rich

    # Block 1: raw a_p
    ap = list(entry.a_p)
    if len(ap) >= n_ap:
        ap = ap[:n_ap]
    else:
        ap = ap + [0] * (n_ap - len(ap))
    ap_arr = np.asarray(ap, dtype=np.float64)

    # Block 2: numerical features
    eps = 1e-9
    log_n = math.log10(max(1, int(entry.conductor)))
    log_rad = math.log10(max(1, int(rich.conductor_radical)))
    log_reg = math.log10(max(rich.regulator, eps))
    log_omega = math.log10(max(rich.real_period, eps))
    log_L1 = math.log10(max(rich.L1, eps))
    log_sha = math.log10(max(rich.sha_an, eps))
    fh = float(rich.faltings_height)
    abcq = float(rich.abc_quality)
    szp = float(rich.szpiro_ratio)
    nums = np.asarray(
        [log_n, log_rad, log_reg, log_omega, log_L1, log_sha, fh, abcq, szp],
        dtype=np.float64,
    )

    # Block 3: tamagawa one-hot
    tam = _onehot(
        _tamagawa_idx(int(rich.tamagawa_product)),
        len(_TAMAGAWA_BUCKETS) + 1,
    )

    # Block 4: torsion one-hot
    tor = _onehot(
        _torsion_idx(int(rich.torsion)),
        len(_TORSION_BUCKETS) + 1,
    )

    # Block 5: torsion structure shape one-hot
    ts = _onehot(
        _torsion_structure_idx(rich.torsion_structure),
        len(_TS_SHAPES),
    )

    # Block 6: CM flag
    cm = np.asarray([1.0 if int(rich.cm) != 0 else 0.0], dtype=np.float64)

    # Block 7: semistable flag
    ss = np.asarray([1.0 if rich.semistable else 0.0], dtype=np.float64)

    # Block 8: signD one-hot
    sd = _onehot(_signD_idx(int(rich.signD)), 3)

    # Block 9: radical bucket
    rad = _onehot(_radical_idx(int(rich.conductor_radical)), len(_RAD_BUCKETS))

    out = np.concatenate([ap_arr, nums, tam, tor, ts, cm, ss, sd, rad])
    # Belt-and-suspenders: replace any NaN/Inf with 0.
    np.nan_to_num(out, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
    expected = feature_dim(n_ap)
    assert out.shape == (expected,), (
        f"vectorize_rich produced shape {out.shape}, expected ({expected},)"
    )
    return out


def feature_block_layout(n_ap: int = 20) -> dict[str, tuple[int, int]]:
    """Return ``{block_name: (start, end_exclusive)}`` slices into the vector.

    Used by tests + diagnostics; mirrors the docstring layout above.
    """
    layout: dict[str, tuple[int, int]] = {}
    cur = 0

    layout["a_p"] = (cur, cur + n_ap)
    cur += n_ap

    layout["numerical"] = (cur, cur + 9)
    cur += 9

    nt = len(_TAMAGAWA_BUCKETS) + 1
    layout["tamagawa_onehot"] = (cur, cur + nt)
    cur += nt

    nt2 = len(_TORSION_BUCKETS) + 1
    layout["torsion_onehot"] = (cur, cur + nt2)
    cur += nt2

    nts = len(_TS_SHAPES)
    layout["torsion_structure_onehot"] = (cur, cur + nts)
    cur += nts

    layout["cm_flag"] = (cur, cur + 1)
    cur += 1
    layout["semistable_flag"] = (cur, cur + 1)
    cur += 1
    layout["signD_onehot"] = (cur, cur + 3)
    cur += 3

    nrad = len(_RAD_BUCKETS)
    layout["radical_onehot"] = (cur, cur + nrad)
    cur += nrad

    assert cur == feature_dim(n_ap), (
        f"layout end {cur} != feature_dim {feature_dim(n_ap)}"
    )
    return layout


__all__ = [
    "feature_dim",
    "feature_block_layout",
    "vectorize_rich",
]
