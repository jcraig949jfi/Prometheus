"""RULERS: frozen calibration, multi-metric behavioural novelty, niche grids.

No scalar novelty score exists anywhere in Theseus. Every ruler is reported
separately; a candidate is flagged per ruler, and "agreement" is a count.

Calibration (Cal) is computed ONCE from the G0 population before any arm or
lane runs, written to disk, and never refitted during a run:
  desc_scales  per-descriptor response scales (battery.calibrate_scales)
  fp_mu, fp_sd z-scoring of fingerprints
  tau_rep      replicability gate: median nearest-neighbour distance among
               distinct viable G0 fingerprints (a replicate must be closer
               to itself than a typical distinct G0 neighbour)
  grids        three niche grids with bin edges at G0 quantiles plus open
               outer bins: "pca" (top-4 PCs of the full z-fingerprint),
               "desc" (4 named descriptors), "resp" (top-3 PCs of the
               intervention-response block)
  sparse_thr   per metric, the 90th percentile of G0 leave-one-out k-NN
               sparseness

Metrics: euclid_z (Euclidean on z), cosine (1 - cos on z), quantile_l1
(mean |dF| after mapping each dim through the G0 empirical CDF).
"""

from __future__ import annotations

import json

import numpy as np

from . import battery as bt

K_NN = 5
QS = [1, 20, 40, 60, 80, 99]  # 7 bins per axis
METRICS = ("euclid_z", "cosine", "quantile_l1")
GRIDS = ("pca", "desc", "resp")
DESC_AXES = ["mean_response", "log_temporal_std", "spectral_entropy", "value_entropy"]


class Cal:
    def __init__(self, d):
        self.d = d
        self.desc_scales = np.array(d["desc_scales"])
        self.mu = np.array(d["fp_mu"])
        self.sd = np.array(d["fp_sd"])
        self.tau_rep = d["tau_rep"]
        self.pca = np.array(d["pca_basis"])
        self.rpca = np.array(d["resp_pca_basis"])
        self.edges = {k: [np.array(e) for e in v] for k, v in d["edges"].items()}
        self.sorted_ref = np.array(d["sorted_ref"])  # [n_ref, D] per-dim sorted G0 z-values
        self.sparse_thr = d["sparse_thr"]

    def to_json(self):
        return self.d

    # ------------------------------------------------------------ transforms
    def z(self, F):
        return (np.atleast_2d(F) - self.mu) / self.sd

    def quant(self, F):
        Z = self.z(F)
        out = np.empty_like(Z)
        n = self.sorted_ref.shape[0]
        for j in range(Z.shape[1]):
            out[:, j] = np.searchsorted(self.sorted_ref[:, j], Z[:, j]) / n
        return out

    def axes(self, F, grid):
        Z = self.z(F)
        F = np.atleast_2d(F)
        if grid == "pca":
            return Z @ self.pca
        if grid == "resp":
            return Z[:, bt.N_DESC:] @ self.rpca
        if grid == "desc":
            names = bt.DESC_NAMES
            cols = [F[:, bt.N_DESC:].mean(1), F[:, names.index("log_temporal_std")],
                    F[:, names.index("spectral_entropy")], F[:, names.index("value_entropy")]]
            return np.stack(cols, 1)
        raise ValueError(grid)

    def cells(self, F, grid):
        A = self.axes(F, grid)
        E = self.edges[grid]
        idx = np.stack([np.searchsorted(E[j], A[:, j]) for j in range(A.shape[1])], 1)
        return [tuple(int(v) for v in row) for row in idx]


def dist_matrix(A, B, metric, cal):
    if metric == "euclid_z":
        ZA, ZB = cal.z(A), cal.z(B)
        return np.sqrt(np.maximum(((ZA[:, None, :] - ZB[None, :, :]) ** 2).sum(-1), 0))
    if metric == "cosine":
        ZA, ZB = cal.z(A), cal.z(B)
        na = np.linalg.norm(ZA, axis=1, keepdims=True) + 1e-12
        nb = np.linalg.norm(ZB, axis=1, keepdims=True) + 1e-12
        return 1.0 - (ZA / na) @ (ZB / nb).T
    if metric == "quantile_l1":
        QA, QB = cal.quant(A), cal.quant(B)
        return np.abs(QA[:, None, :] - QB[None, :, :]).mean(-1)
    raise ValueError(metric)


def sparseness(F, ref, metric, cal, k=K_NN, exclude_self=False):
    F = np.atleast_2d(F)
    ref = np.atleast_2d(ref)
    if ref.shape[0] == 0:
        return np.full(F.shape[0], np.inf)
    D = dist_matrix(F, ref, metric, cal)
    if exclude_self:
        D = D + np.where(D < 1e-12, np.inf, 0.0)
    kk = min(k, D.shape[1])
    return np.sort(D, axis=1)[:, :kk].mean(1)


def build_cal(fps, rep_pairs, desc_scales):
    """fps: [n, D] viable G0 fingerprints; rep_pairs: list of (fp0, fp1)."""
    F = np.asarray(fps)
    mu = F.mean(0)
    sd = F.std(0)
    sd = np.where(sd > 1e-3, sd, 1e-3)
    Z = (F - mu) / sd
    U, S, Vt = np.linalg.svd(Z - Z.mean(0), full_matrices=False)
    pca = Vt[:4].T
    Ur, Sr, Vtr = np.linalg.svd(Z[:, bt.N_DESC:] - Z[:, bt.N_DESC:].mean(0), full_matrices=False)
    rpca = Vtr[:3].T
    d = {"desc_scales": np.asarray(desc_scales).tolist(), "fp_mu": mu.tolist(), "fp_sd": sd.tolist(),
         "pca_basis": pca.tolist(), "resp_pca_basis": rpca.tolist(),
         "sorted_ref": np.sort(Z, axis=0).tolist(), "edges": {}, "sparse_thr": {}, "tau_rep": None}
    cal = Cal({**d, "edges": {g: [[0.0]] for g in GRIDS}, "sparse_thr": {}, "tau_rep": 0})
    for g in GRIDS:
        A = cal.axes(F, g)
        d["edges"][g] = [np.percentile(A[:, j], QS).tolist() for j in range(A.shape[1])]
    Dz = dist_matrix(F, F, "euclid_z", cal) + np.eye(len(F)) * 1e9
    d["tau_rep"] = float(np.median(Dz.min(1)))
    cal = Cal(d)
    for m in METRICS:
        s = sparseness(F, F, m, cal, exclude_self=True)
        d["sparse_thr"][m] = float(np.percentile(s, 90))
    rep = [float(np.linalg.norm((np.asarray(a) - np.asarray(b)) / sd)) for a, b in rep_pairs]
    d["g0_rep_dist_pct"] = np.percentile(rep, [10, 50, 90]).tolist() if rep else None
    return Cal(d)


class Archive:
    """Quality-diversity archive: per-grid cell elites + the full viable fp list.

    Quality for elites is REPRODUCIBILITY (smaller replicate distance), never
    novelty, so the archive does not reward weirdness for its own sake."""

    def __init__(self, cal):
        self.cal = cal
        self.ids = []
        self.F = np.zeros((0, bt.FP_DIM))
        self.elites = {g: {} for g in GRIDS}
        self.first = {g: {} for g in GRIDS}

    def assess(self, fp):
        fp = np.asarray(fp)
        out = {"new_cell": {}, "sparse": {}, "sparse_flag": {}}
        for g in GRIDS:
            c = self.cal.cells(fp, g)[0]
            out.setdefault("cell", {})[g] = list(c)
            out["new_cell"][g] = c not in self.first[g]
        for m in METRICS:
            s = float(sparseness(fp, self.F, m, self.cal)[0]) if len(self.ids) else float("inf")
            out["sparse"][m] = s
            out["sparse_flag"][m] = bool(s > self.cal.sparse_thr[m])
        out["n_rulers_novel"] = int(sum(out["new_cell"].values()) + sum(out["sparse_flag"].values()))
        return out

    def insert(self, eid, fp, quality):
        a = self.assess(fp)
        for g in GRIDS:
            c = tuple(a["cell"][g])
            if c not in self.first[g]:
                self.first[g][c] = eid
            cur = self.elites[g].get(c)
            if cur is None or quality > cur[1]:
                self.elites[g][c] = (eid, quality)
        self.ids.append(eid)
        self.F = np.vstack([self.F, np.asarray(fp)[None]])
        return a

    def occupancy(self):
        return {g: len(self.first[g]) for g in GRIDS}

    def elite_ids(self, grids=GRIDS):
        return {e for g in grids for (e, _) in self.elites[g].values()}


def save_cal(cal, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cal.to_json(), f)
