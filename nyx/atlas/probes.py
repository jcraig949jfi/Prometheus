"""Behavioral probe battery for the ASAL low-score region (operator directive 2026-09-19b s2).

TWO CHANNELS.

DECLARED CHANNEL -- the 14 preregistered probes named in the 2026-09-19 directive s5. Each is a pure,
deterministic function of a frame stack; none of them consults a foundation model, so every probe is
OBSERVER-INDEPENDENT by construction. That is the point: the probes must be able to separate organisms
that the observer's representation maps to the same score.

OPEN CHANNEL -- representation-light descriptors intended to expose structure the declared probes did
NOT anticipate (trajectory descriptors, temporal signatures, spectral summaries). Downstream these feed
clustering and nearest-neighbour anomaly detection. ANYTHING the open channel finds is a NOMINATION,
never evidence: it must earn confirmation on untouched data or by intervention/transplant. This keeps
our own taxonomy from becoming the walls of the search.

FROZEN BEFORE RESULTS. This module is frozen by source hash (probes.FREEZE beside it) BEFORE any
replication data is seen, and is exercised only on SYNTHETIC or UNRELATED fixtures (nyx/tests/
test_probes.py). Re-freezing requires a recorded reason.

Input contract: frames, an array of shape (T, H, W), float or uint8, non-negative intensities.
Output contract: a float per declared probe (NaN is never returned; degenerate input yields 0.0).
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict

import numpy as np

SCHEMA = "nyx.probe_battery/1"
_SRC = Path(__file__).resolve()
FREEZE = _SRC.parent / "probes.FREEZE"

_EPS = 1e-12


# ----------------------------------------------------------------- helpers (not probes)
def _prep(frames) -> np.ndarray:
    a = np.asarray(frames, dtype=np.float64)
    if a.ndim != 3:
        raise ValueError(f"frames must be (T,H,W), got {a.shape}")
    if a.size == 0 or a.shape[0] == 0:
        raise ValueError("empty frame stack")
    m = a.max()
    return a / m if m > 0 else a


def _mass(a):                      # per-frame total intensity
    return a.reshape(a.shape[0], -1).sum(axis=1)


def _centroid(a):
    T, H, W = a.shape
    ys, xs = np.arange(H)[None, :, None], np.arange(W)[None, None, :]
    m = _mass(a)[:, None]
    m = np.where(m > _EPS, m, 1.0)
    cy = (a * ys).reshape(T, -1).sum(axis=1)[:, None] / m
    cx = (a * xs).reshape(T, -1).sum(axis=1)[:, None] / m
    return np.concatenate([cy, cx], axis=1)          # (T,2)


def _flat_unit(a):
    v = a.reshape(a.shape[0], -1)
    n = np.linalg.norm(v, axis=1, keepdims=True)
    return v / np.where(n > _EPS, n, 1.0)


def _radial_spectrum(a, nbins=16):
    T, H, W = a.shape
    f = np.abs(np.fft.fftshift(np.fft.fft2(a, axes=(1, 2)), axes=(1, 2)))
    cy, cx = H / 2.0, W / 2.0
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
    r = (r / (r.max() + _EPS) * (nbins - 1)).astype(int)
    out = np.zeros((T, nbins))
    for b in range(nbins):
        msk = r == b
        if msk.any():
            out[:, b] = f[:, msk].mean(axis=1)
    s = out.sum(axis=1, keepdims=True)
    return out / np.where(s > _EPS, s, 1.0)


def _autocorr_profile(a):
    """Pearson correlation of frame pairs at each lag (mean over start positions).

    The frames are MEAN-CENTERED first: raw intensities are non-negative, so an uncentered cosine is
    high (~0.75) even between independent random fields and cannot distinguish identity from noise.
    """
    v = a.reshape(a.shape[0], -1)
    v = v - v.mean(axis=1, keepdims=True)
    n = np.linalg.norm(v, axis=1, keepdims=True)
    v = v / np.where(n > _EPS, n, 1.0)
    T = v.shape[0]
    return np.array([float((v[: T - L] * v[L:]).sum(axis=1).mean()) if T - L > 0 else 0.0 for L in range(T)])


# ----------------------------------------------------------------- DECLARED CHANNEL (14 probes)
def p01_coherence(frames) -> float:
    """coherent persistent morphology vs turbulent texture: mean cosine of consecutive frames."""
    a = _prep(frames); v = _flat_unit(a)
    return float((v[:-1] * v[1:]).sum(axis=1).mean()) if a.shape[0] > 1 else 1.0


def p02_locomotion_vs_deformation(frames) -> float:
    """ratio of centroid travel to shape change; high = moves without changing, low = deforms in place."""
    a = _prep(frames)
    if a.shape[0] < 2:
        return 0.0
    c = _centroid(a)
    travel = float(np.linalg.norm(np.diff(c, axis=0), axis=1).mean())
    v = _flat_unit(a)
    change = float(1.0 - (v[:-1] * v[1:]).sum(axis=1).mean())
    return travel / (change + _EPS)


def p03_identity_halflife(frames) -> float:
    """stable identity vs rapid turnover: first lag (normalised) where autocorrelation drops below 0.5."""
    a = _prep(frames); ac = _autocorr_profile(a); T = a.shape[0]
    below = np.where(ac < 0.5)[0]
    return float(below[0] / T) if below.size else 1.0


def p04_spatial_frequency(frames) -> float:
    """spatial frequency content: mean normalised radial centroid of the power spectrum."""
    rs = _radial_spectrum(_prep(frames))
    bins = np.arange(rs.shape[1]) / max(rs.shape[1] - 1, 1)
    return float((rs * bins[None, :]).sum(axis=1).mean())


def p05_occupancy_edge_density(frames) -> float:
    """occupancy and edge density: mean gradient magnitude per occupied cell."""
    a = _prep(frames)
    gy = np.abs(np.diff(a, axis=1)).sum(axis=(1, 2))
    gx = np.abs(np.diff(a, axis=2)).sum(axis=(1, 2))
    occ = (a > 0.1).reshape(a.shape[0], -1).sum(axis=1).astype(float)
    return float(((gy + gx) / np.where(occ > 0, occ, 1.0)).mean())


def p06_temporal_novelty_pixelspace(frames) -> float:
    """temporal novelty, in PIXEL space: mean over t of max cosine to any STRICTLY EARLIER frame.

    Deliberately the same functional form as the ASAL score but with no learned representation, so a
    difference between this and the ASAL scalar localises the effect IN the observer, not the dynamics.
    """
    a = _prep(frames); v = _flat_unit(a); T = v.shape[0]
    if T < 2:
        return 0.0
    k = np.tril(v @ v.T, k=-1)
    k[0, :] = 0.0
    return float(k.max(axis=1)[1:].mean())


def p07_frame_displacement(frames) -> float:
    """frame-to-frame displacement of the centre of mass, in field widths."""
    a = _prep(frames)
    if a.shape[0] < 2:
        return 0.0
    c = _centroid(a)
    return float(np.linalg.norm(np.diff(c, axis=0), axis=1).mean() / max(a.shape[1], a.shape[2]))


def p08_persistence(frames) -> float:
    """fraction of frames retaining at least 10% of the peak mass (does the thing survive)."""
    m = _mass(_prep(frames))
    return float((m >= 0.1 * m.max()).mean()) if m.max() > _EPS else 0.0


def p09_periodicity(frames) -> float:
    """strongest autocorrelation peak at lag >= 1 (a 2-cycle scores high)."""
    ac = _autocorr_profile(_prep(frames))
    return float(ac[1:].max()) if ac.size > 1 else 0.0


def p10_spectral_change(frames) -> float:
    """mean total-variation of the radial spectrum between consecutive frames."""
    rs = _radial_spectrum(_prep(frames))
    return float(np.abs(np.diff(rs, axis=0)).sum(axis=1).mean()) if rs.shape[0] > 1 else 0.0


def p11_object_background_separability(frames) -> float:
    """Otsu between-class variance, normalised: high = a clear object on a clean background."""
    a = _prep(frames); out = []
    for fr in a:
        x = fr.ravel()
        tot = x.var()
        if tot <= _EPS:
            out.append(0.0); continue
        best = 0.0
        for t in np.linspace(0.05, 0.95, 19):
            lo, hi = x[x <= t], x[x > t]
            if lo.size == 0 or hi.size == 0:
                continue
            w0, w1 = lo.size / x.size, hi.size / x.size
            best = max(best, w0 * w1 * (lo.mean() - hi.mean()) ** 2)
        out.append(best / tot)
    return float(np.mean(out))


def p12_morphology_preserving_motion(frames) -> float:
    """fraction of frame-to-frame change explained by pure translation (roll-registered cosine gain)."""
    a = _prep(frames)
    if a.shape[0] < 2:
        return 1.0
    c = _centroid(a); v = _flat_unit(a)
    raw = (v[:-1] * v[1:]).sum(axis=1)
    reg = []
    for t in range(a.shape[0] - 1):
        dy, dx = np.rint(c[t + 1] - c[t]).astype(int)
        shifted = np.roll(np.roll(a[t], dy, axis=0), dx, axis=1)
        s = shifted.ravel(); n = np.linalg.norm(s)
        s = s / (n if n > _EPS else 1.0)
        reg.append(float(s @ v[t + 1]))
    reg = np.array(reg)
    gain = (reg - raw) / (1.0 - raw + _EPS)
    return float(np.clip(gain, 0.0, 1.0).mean())


def p13_catastrophic_change(frames) -> float:
    """max absolute log mass ratio between consecutive frames (explosion or collapse)."""
    m = _mass(_prep(frames))
    m = np.where(m > _EPS, m, _EPS)
    return float(np.abs(np.diff(np.log(m))).max()) if m.size > 1 else 0.0


def p14_scene_scale_texture(frames) -> float:
    """radius of gyration normalised by field size: compact organism (low) vs scene-scale texture (high)."""
    a = _prep(frames); c = _centroid(a); T, H, W = a.shape
    yy, xx = np.mgrid[0:H, 0:W]
    out = []
    for t in range(T):
        m = a[t].sum()
        if m <= _EPS:
            out.append(0.0); continue
        d2 = (yy - c[t, 0]) ** 2 + (xx - c[t, 1]) ** 2
        out.append(float(np.sqrt((a[t] * d2).sum() / m) / max(H, W)))
    return float(np.mean(out))


DECLARED = {
    "p01_coherence": p01_coherence,
    "p02_locomotion_vs_deformation": p02_locomotion_vs_deformation,
    "p03_identity_halflife": p03_identity_halflife,
    "p04_spatial_frequency": p04_spatial_frequency,
    "p05_occupancy_edge_density": p05_occupancy_edge_density,
    "p06_temporal_novelty_pixelspace": p06_temporal_novelty_pixelspace,
    "p07_frame_displacement": p07_frame_displacement,
    "p08_persistence": p08_persistence,
    "p09_periodicity": p09_periodicity,
    "p10_spectral_change": p10_spectral_change,
    "p11_object_background_separability": p11_object_background_separability,
    "p12_morphology_preserving_motion": p12_morphology_preserving_motion,
    "p13_catastrophic_change": p13_catastrophic_change,
    "p14_scene_scale_texture": p14_scene_scale_texture,
}


def declared(frames) -> Dict[str, float]:
    """Run the whole declared battery. Deterministic; same input -> same output."""
    return {k: float(fn(frames)) for k, fn in DECLARED.items()}


# ----------------------------------------------------------------- OPEN CHANNEL (nominations only)
def open_descriptor(frames) -> np.ndarray:
    """A representation-light descriptor vector: per-frame series summarised, plus temporal and
    spectral signatures. Intended for clustering / nearest-neighbour anomaly search DOWNSTREAM.

    Nothing here is a finding. Whatever structure emerges is a NOMINATION that must be confirmed on
    untouched data or by intervention/transplant before it becomes evidence.
    """
    a = _prep(frames)
    m, c = _mass(a), _centroid(a)
    T, H, W = a.shape
    yy, xx = np.mgrid[0:H, 0:W]
    rg = np.array([np.sqrt((a[t] * ((yy - c[t, 0]) ** 2 + (xx - c[t, 1]) ** 2)).sum() / (m[t] + _EPS)) for t in range(T)])
    series = np.vstack([m / (m.max() + _EPS), c[:, 0] / H, c[:, 1] / W, rg / max(H, W)])
    summ = np.concatenate([series.mean(axis=1), series.std(axis=1),
                           (series[:, -1] - series[:, 0])])                      # level, variability, drift
    return np.concatenate([summ, _autocorr_profile(a), _radial_spectrum(a).mean(axis=0)]).astype(np.float64)


OPEN_CHANNEL_NOTE = ("open-channel output is a NOMINATION, not evidence; it must earn confirmation on untouched "
                     "data or by intervention/transplant (operator directive 2026-09-19b s2)")


# ----------------------------------------------------------------- freeze
def source_hash() -> str:
    return hashlib.sha256(_SRC.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def frozen_hash() -> str:
    if not FREEZE.exists():
        return ""
    return FREEZE.read_text(encoding="utf-8").split()[0]


def is_frozen_intact() -> bool:
    return bool(frozen_hash()) and frozen_hash() == source_hash()


if __name__ == "__main__":
    print(SCHEMA, "declared probes:", len(DECLARED))
    print("source_hash", source_hash())
    print("frozen_hash", frozen_hash() or "(not frozen)")
    print("intact     ", is_frozen_intact())
