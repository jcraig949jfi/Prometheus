"""Boundary-layer clustering of the 17 Lehmer brute-force unverified entries.

Mission
-------
Three independent paths (A: high-precision mpmath; B: symbolic factorisation;
C: tighter Mossinghoff + Lehmer x Phi_n product matching) all agreed on a
coarse 15 / 2 split for the 17 ``verification_failed=True`` entries from the
deg-14 +/- 5 palindromic Lehmer brute-force run:

* 15 cyclotomic-noise entries (true M = 1, numpy float-noise put them in band).
* 2 Lehmer x Phi_n^k entries (entries 2 and 14, 0-indexed; Lehmer x Phi_1^4 and
  Lehmer x Phi_2^4 -- these are x -> -x reflection equivalents of one base).

This module clusters the 17 entries WITHIN those classes by a richer feature
signature, to expose the finer boundary-layer structure ChatGPT named. The
output is a labeled descriptive dataset that future near-miss classifiers
(e.g. the kill-space gradient field idea, Aporia G3) can train against.

Honest framing
--------------
17 entries is much too small to claim statistical significance. Silhouette
scores at this scale are noisy. This is a *descriptive* structural analysis,
not a *predictive* model. The value is exposing the discrete structural
strata in the cyclotomic-noise class -- which Phi_n indices appear, what
multiplicities, how many distinct factors -- so that downstream tooling has
a labeled training set when it is needed.

Read-only on the existing JSON files. No new pilots, no new mpmath calls.

Forged: 2026-05-04 by Techne (toolsmith) for Charon's boundary-layer pass.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Optional, Sequence

import numpy as np
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


__all__ = [
    "DEFAULT_BRUTE_FORCE_PATH",
    "DEFAULT_PATH_A_PATH",
    "DEFAULT_PATH_B_PATH",
    "DEFAULT_PATH_C_PATH",
    "FEATURE_KEYS",
    "build_feature_matrix",
    "characterize_clusters",
    "cluster_features",
    "extract_features",
    "kill_vector_signature",
    "load_all_paths",
    "run_boundary_layer",
]


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_HERE = Path(__file__).parent

DEFAULT_BRUTE_FORCE_PATH = _HERE / "_lehmer_brute_force_results.json"
DEFAULT_PATH_A_PATH = _HERE / "_lehmer_brute_force_path_a_results.json"
DEFAULT_PATH_B_PATH = _HERE / "_lehmer_brute_force_path_b_results.json"
DEFAULT_PATH_C_PATH = _HERE / "_lehmer_brute_force_path_c_results.json"

# Lehmer-band finishing line. Entries above are Lehmer-depth (Class 2);
# entries near 1.0 (within 0.01) are cyclotomic-noise (Class 1).
_LEHMER_M_REFERENCE: float = 1.1762808182599175
_NOISE_M_THRESHOLD: float = 1.01

# Numerical features used for clustering. Order matters for matrix layout.
FEATURE_KEYS: tuple[str, ...] = (
    "log10_M_minus_1_clamped",     # log10(M_numpy - 1), clamped at -8
    "residual_M_after_cyc",        # original brute-force residual_M
    "n_distinct_factors",          # number of distinct irreducible factors
    "n_distinct_cyclotomic_idx",   # number of distinct Phi_n indices
    "max_multiplicity",            # max multiplicity across factors
    "max_factor_degree",           # largest single-factor degree
    "min_factor_degree",           # smallest single-factor degree (always 1)
    "n_non_cyclotomic_factors",    # 0 for class 1, 1 for class 2
)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_all_paths(
    brute_force_path: str | Path = DEFAULT_BRUTE_FORCE_PATH,
    path_a_path: str | Path = DEFAULT_PATH_A_PATH,
    path_b_path: str | Path = DEFAULT_PATH_B_PATH,
    path_c_path: str | Path = DEFAULT_PATH_C_PATH,
) -> dict:
    """Read all four JSONs and align them to a list of 17 unverified entries.

    Alignment is by ``coeffs_ascending`` -- the canonical key shared by all
    four files. Returns a dict with keys ``brute_force``, ``path_a``,
    ``path_b``, ``path_c`` whose values are lists of 17 dicts indexed in the
    original brute-force order.
    """
    with Path(brute_force_path).open("r", encoding="utf-8") as fh:
        bf_data = json.load(fh)
    with Path(path_a_path).open("r", encoding="utf-8") as fh:
        pa_data = json.load(fh)
    with Path(path_b_path).open("r", encoding="utf-8") as fh:
        pb_data = json.load(fh)
    with Path(path_c_path).open("r", encoding="utf-8") as fh:
        pc_data = json.load(fh)

    # The 17 unverified brute-force entries (= NOT in mossinghoff).
    band = bf_data.get("in_lehmer_band", [])
    bf_unverified = [e for e in band if not e.get("in_mossinghoff", True)]

    pa_entries = pa_data.get("per_entry_results", [])
    pb_entries = pb_data.get("results", [])
    pc_entries = pc_data.get("classifications", [])

    if not (len(bf_unverified) == len(pa_entries) == len(pb_entries) == len(pc_entries)):
        raise ValueError(
            "path-length mismatch across JSONs: "
            f"bf={len(bf_unverified)} a={len(pa_entries)} "
            f"b={len(pb_entries)} c={len(pc_entries)}"
        )

    # Validate alignment by coeffs_ascending.
    aligned_bf = []
    aligned_a = []
    aligned_b = []
    aligned_c = []
    for i, bf in enumerate(bf_unverified):
        key = tuple(bf["coeffs_ascending"])
        # Find each path's entry with matching coeffs.
        a = next((e for e in pa_entries if tuple(e["coeffs_ascending"]) == key), None)
        b = next((e for e in pb_entries if tuple(e["coeffs_ascending"]) == key), None)
        c = next((e for e in pc_entries if tuple(e["coeffs_ascending"]) == key), None)
        if a is None or b is None or c is None:
            raise ValueError(
                f"alignment failed for entry {i} coeffs={list(key)[:5]}..."
            )
        aligned_bf.append(bf)
        aligned_a.append(a)
        aligned_b.append(b)
        aligned_c.append(c)

    return {
        "brute_force": aligned_bf,
        "path_a": aligned_a,
        "path_b": aligned_b,
        "path_c": aligned_c,
    }


# ---------------------------------------------------------------------------
# Per-entry feature extraction
# ---------------------------------------------------------------------------

def extract_features(
    bf_entry: dict,
    path_a_entry: dict,
    path_b_entry: dict,
    path_c_entry: dict,
) -> dict:
    """Build the per-entry feature row from the four aligned dicts.

    Numeric features (used for clustering) are emitted under their
    ``FEATURE_KEYS`` names. Categorical fields (factorisation, kill_vector
    signature) ride alongside for human inspection but are NOT clustered
    on directly.
    """
    M_numpy = float(bf_entry.get("M_numpy", float("nan")))
    residual = float(bf_entry.get("residual_M_after_cyclotomic_factor", float("nan")))

    # log10(M - 1) clamped at -8 (well below float-noise floor) so a true
    # M=1 doesn't blow up.
    excess = M_numpy - 1.0
    if excess <= 1e-8:
        log10_excess = -8.0
    else:
        log10_excess = math.log10(excess)

    # Path B factor list: the symbolic ground truth.
    factors = path_b_entry.get("factor_list", [])
    n_distinct_factors = len(factors)
    cyc_idx_list = sorted({
        f["cyclotomic_n"] for f in factors
        if f.get("is_cyclotomic") and f.get("cyclotomic_n") is not None
    })
    n_distinct_cyc_idx = len(cyc_idx_list)
    n_noncyc = path_b_entry.get("n_non_cyclotomic_factors", 0)
    multiplicities = [int(f.get("multiplicity", 1)) for f in factors]
    max_mult = max(multiplicities) if multiplicities else 0
    degrees = [int(f.get("degree", 0)) for f in factors]
    max_deg = max(degrees) if degrees else 0
    min_deg = min(degrees) if degrees else 0

    # Path A: high-precision M, convergence_dps.
    M_path_a = float(path_a_entry.get("M_path_a", float("nan")))
    conv_dps = path_a_entry.get("convergence_precision_digits")
    classification_a = path_a_entry.get("classification")
    verdict_a = path_a_entry.get("verdict_per_entry")

    # Path C: cyclotomic n indices with multiplicities + decomposition class.
    classification_c = path_c_entry.get("classification")
    phi_factors_c = path_c_entry.get("details", {}).get("phi_factors", {})
    lehmer_orientation = path_c_entry.get("details", {}).get("lehmer_orientation")

    # Failure-mode signature: NaN return, and the dps=30 numpy delta.
    M_mpmath_orig = bf_entry.get("M_mpmath")
    if M_mpmath_orig is None:
        failure_mode = "absent"
    else:
        try:
            mp_val = float(M_mpmath_orig)
            if math.isnan(mp_val):
                failure_mode = "nan_return"
            else:
                failure_mode = "out_of_band_at_dps30"
        except (TypeError, ValueError):
            failure_mode = "non_numeric"

    # Numerical-conditioning signature: how far did M_numpy land from M_path_a?
    if math.isnan(M_path_a):
        delta_M = float("nan")
    else:
        delta_M = M_numpy - M_path_a

    return {
        "coeffs_ascending": list(bf_entry["coeffs_ascending"]),
        # Numeric features (used for clustering).
        "log10_M_minus_1_clamped": log10_excess,
        "residual_M_after_cyc": residual,
        "n_distinct_factors": n_distinct_factors,
        "n_distinct_cyclotomic_idx": n_distinct_cyc_idx,
        "max_multiplicity": max_mult,
        "max_factor_degree": max_deg,
        "min_factor_degree": min_deg,
        "n_non_cyclotomic_factors": n_noncyc,
        # Categorical / metadata.
        "M_numpy": M_numpy,
        "M_path_a": M_path_a,
        "delta_M_numpy_vs_path_a": delta_M,
        "convergence_precision_digits": conv_dps,
        "classification_a": classification_a,
        "verdict_a": verdict_a,
        "classification_c": classification_c,
        "cyclotomic_n_indices": cyc_idx_list,
        "phi_factors_c": phi_factors_c,
        "lehmer_orientation": lehmer_orientation,
        "failure_mode": failure_mode,
    }


def build_feature_matrix(
    entries: Sequence[dict],
    feature_keys: Sequence[str] = FEATURE_KEYS,
) -> np.ndarray:
    """Stack per-entry feature dicts into a (n_entries, n_features) matrix."""
    rows = []
    for entry in entries:
        row = []
        for key in feature_keys:
            val = entry.get(key)
            if val is None or (isinstance(val, float) and math.isnan(val)):
                # NaN guard: replace with 0.0 so clustering doesn't blow up.
                # In practice this should not fire on the 17 entries.
                row.append(0.0)
            else:
                row.append(float(val))
        rows.append(row)
    return np.array(rows, dtype=float)


# ---------------------------------------------------------------------------
# Clustering
# ---------------------------------------------------------------------------

def cluster_features(
    X: np.ndarray,
    k_range: Sequence[int] = (2, 3, 4),
    method: str = "kmeans",
    random_state: int = 0,
    n_init: int = 20,
) -> dict:
    """Cluster the rows of X with k in k_range; return per-k results.

    Returns a dict with:
    * ``per_k``: list of dicts with ``k``, ``labels``, ``silhouette``,
      ``cluster_sizes``.
    * ``best_k``: the k that maximises silhouette (with deterministic
      tie-breaks toward the smaller k for parsimony).
    * ``best_labels``: labels at best_k.
    * ``method``: clustering method used.
    * ``X_scaled``: standardised feature matrix used.
    """
    if X.shape[0] < max(k_range) + 1:
        raise ValueError(
            f"too few samples ({X.shape[0]}) for max k={max(k_range)}"
        )

    # Standardise columns (z-score). KMeans is scale-sensitive; without
    # this, residual_M (~1.0) would dominate over n_distinct_factors (~3-4).
    scaler = StandardScaler()
    # If a column has zero variance, StandardScaler will divide by zero;
    # set scale_=1 in that case so the column stays at the constant mean.
    X_scaled = scaler.fit_transform(X)
    # Replace any NaNs that arose from zero-variance columns (will be 0/0).
    X_scaled = np.nan_to_num(X_scaled, nan=0.0, posinf=0.0, neginf=0.0)

    per_k = []
    for k in k_range:
        if k < 2:
            continue
        if k >= X.shape[0]:
            continue
        if method == "kmeans":
            model = KMeans(
                n_clusters=k, random_state=random_state, n_init=n_init,
            )
            labels = model.fit_predict(X_scaled)
        elif method == "agglomerative":
            model = AgglomerativeClustering(n_clusters=k, linkage="ward")
            labels = model.fit_predict(X_scaled)
        else:
            raise ValueError(f"unknown method: {method!r}")

        # Silhouette only defined when more than one cluster has samples.
        unique_labels = set(int(x) for x in labels)
        if len(unique_labels) < 2:
            sil = float("nan")
        else:
            try:
                sil = float(silhouette_score(X_scaled, labels))
            except Exception:
                sil = float("nan")
        sizes = {int(c): int((labels == c).sum()) for c in unique_labels}
        per_k.append({
            "k": int(k),
            "labels": [int(x) for x in labels],
            "silhouette": sil,
            "cluster_sizes": sizes,
        })

    # Choose best_k: max silhouette; ties broken toward smaller k (parsimony).
    valid = [r for r in per_k if not math.isnan(r["silhouette"])]
    if valid:
        best = max(valid, key=lambda r: (r["silhouette"], -r["k"]))
        best_k = best["k"]
        best_labels = best["labels"]
    else:
        best_k = per_k[0]["k"] if per_k else None
        best_labels = per_k[0]["labels"] if per_k else []

    return {
        "method": method,
        "per_k": per_k,
        "best_k": best_k,
        "best_labels": list(best_labels),
        "X_scaled": X_scaled.tolist(),
        "feature_keys": list(FEATURE_KEYS),
    }


# ---------------------------------------------------------------------------
# Cluster characterisation
# ---------------------------------------------------------------------------

def characterize_clusters(
    entries: Sequence[dict],
    labels: Sequence[int],
) -> list[dict]:
    """For each cluster, summarise the feature distribution + representatives."""
    cluster_ids = sorted({int(x) for x in labels})
    out = []
    for cid in cluster_ids:
        members = [e for e, lab in zip(entries, labels) if int(lab) == cid]
        n = len(members)
        # Numeric feature stats.
        stats = {}
        for key in FEATURE_KEYS:
            vals = [float(m.get(key, 0.0)) for m in members]
            if vals:
                stats[key] = {
                    "min": float(min(vals)),
                    "max": float(max(vals)),
                    "mean": float(sum(vals) / len(vals)),
                }
            else:
                stats[key] = {"min": None, "max": None, "mean": None}
        # Categorical fields: collect unique values.
        classifications_a = sorted({m.get("classification_a") for m in members})
        classifications_c = sorted({m.get("classification_c") for m in members})
        verdicts_a = sorted({m.get("verdict_a") for m in members})
        failure_modes = sorted({m.get("failure_mode") for m in members})
        # cyclotomic_n_indices: union of all
        all_cyc_ns: set[int] = set()
        for m in members:
            all_cyc_ns.update(m.get("cyclotomic_n_indices", []))
        # Representative: the entry closest to the cluster mean in n_distinct_cyc_idx.
        rep = members[0] if members else None
        out.append({
            "cluster_id": int(cid),
            "size": int(n),
            "feature_stats": stats,
            "classifications_a": [c for c in classifications_a if c is not None],
            "classifications_c": [c for c in classifications_c if c is not None],
            "verdicts_a": [v for v in verdicts_a if v is not None],
            "failure_modes": [f for f in failure_modes if f is not None],
            "cyclotomic_n_index_union": sorted(all_cyc_ns),
            "representative_coeffs_ascending": (
                rep.get("coeffs_ascending") if rep else None
            ),
            "representative_phi_factors_c": (
                rep.get("phi_factors_c") if rep else None
            ),
        })
    return out


# ---------------------------------------------------------------------------
# Kill-vector signature mapping
# ---------------------------------------------------------------------------

def kill_vector_signature(entry: dict) -> dict:
    """Best-effort kill-vector signature for a single entry.

    The full KillComponent / kill-space gradient field is in Aporia G3 and
    Charon's gauntlet. Here we emit a structurally-valid mock signature
    using ONLY the fields available in the four JSONs -- this is the seed
    that downstream tooling can lift to the real kill-vector.

    Boolean components (True = component fired against this entry):
    * out_of_band: True if M_path_a is outside the Lehmer-band (1.0001, 1.20).
      For class 1 this fires (true M = 1, below band); for class 2 it does not.
    * has_cyclotomic_factor: always True for these 17 (they all do).
    * is_lehmer_product: True iff Path C says C2 (Lehmer x Phi).
    * is_pure_cyclotomic: True iff Path C says C3 (all-cyclotomic).
    * verification_failed_at_dps30: True (definitional for the 17).
    * mossinghoff_proximity_match: True iff Path A's mossinghoff_match
      flagged in_catalog (M_proximity).
    """
    M_path_a = float(entry.get("M_path_a", float("nan")))
    if math.isnan(M_path_a):
        out_of_band = True
    else:
        out_of_band = not (1.0001 < M_path_a < 1.20)
    cls_c = entry.get("classification_c")
    is_lehmer_product = cls_c == "C2"
    is_pure_cyclotomic = cls_c == "C3"
    return {
        "out_of_band": bool(out_of_band),
        "has_cyclotomic_factor": True,
        "is_lehmer_product": bool(is_lehmer_product),
        "is_pure_cyclotomic": bool(is_pure_cyclotomic),
        "verification_failed_at_dps30": True,
        "mossinghoff_proximity_match": entry.get("verdict_a") == "rediscovery",
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def run_boundary_layer(
    output_path: Optional[str | Path] = None,
    brute_force_path: str | Path = DEFAULT_BRUTE_FORCE_PATH,
    path_a_path: str | Path = DEFAULT_PATH_A_PATH,
    path_b_path: str | Path = DEFAULT_PATH_B_PATH,
    path_c_path: str | Path = DEFAULT_PATH_C_PATH,
    k_range: Sequence[int] = (2, 3, 4),
    method: str = "kmeans",
    random_state: int = 0,
) -> dict:
    """Run the full boundary-layer pipeline and (optionally) write JSON."""
    paths = load_all_paths(
        brute_force_path, path_a_path, path_b_path, path_c_path,
    )
    n = len(paths["brute_force"])

    entries: list[dict] = []
    for i in range(n):
        feat = extract_features(
            paths["brute_force"][i],
            paths["path_a"][i],
            paths["path_b"][i],
            paths["path_c"][i],
        )
        feat["entry_index"] = i
        feat["kill_vector_signature"] = kill_vector_signature(feat)
        entries.append(feat)

    X = build_feature_matrix(entries)
    cluster_result = cluster_features(
        X, k_range=k_range, method=method, random_state=random_state,
    )

    # Attach cluster label to each entry under the chosen best_k.
    best_labels = cluster_result["best_labels"]
    for entry, lab in zip(entries, best_labels):
        entry["cluster_id_best_k"] = int(lab)

    cluster_chars = characterize_clusters(entries, best_labels)

    # Within-class sub-clustering: re-cluster the dominant cluster (size > 4)
    # to expose any second-level boundary-layer structure. At n=17 with one
    # 15-member class and one 2-member class, this only fires on the 15 C3
    # entries.
    sub_clustering = None
    largest = max(cluster_chars, key=lambda c: c["size"])
    if largest["size"] >= 5:
        members_idx = [
            i for i, lab in enumerate(best_labels)
            if int(lab) == largest["cluster_id"]
        ]
        sub_entries = [entries[i] for i in members_idx]
        X_sub = build_feature_matrix(sub_entries)
        # Drop zero-variance columns (e.g. n_non_cyclotomic_factors == 0
        # everywhere in the C3 sub-class).
        keep_cols = [
            j for j in range(X_sub.shape[1]) if X_sub[:, j].std() > 0
        ]
        X_sub_kept = X_sub[:, keep_cols] if keep_cols else X_sub
        sub_keys = [FEATURE_KEYS[j] for j in keep_cols]
        try:
            sub_result = cluster_features(
                X_sub_kept,
                k_range=(2, 3, 4, 5),
                method=method,
                random_state=random_state,
            )
            # Map sub-labels back onto the original entry indices.
            sub_labels_full = [None] * n
            for src_i, lab in zip(members_idx, sub_result["best_labels"]):
                sub_labels_full[src_i] = int(lab)
            sub_chars = characterize_clusters(
                sub_entries, sub_result["best_labels"],
            )
            sub_clustering = {
                "parent_cluster_id": int(largest["cluster_id"]),
                "n_members": len(sub_entries),
                "feature_keys_used": sub_keys,
                "per_k_clustering": sub_result["per_k"],
                "best_k": sub_result["best_k"],
                "best_labels": sub_result["best_labels"],
                "labels_full_indexing": sub_labels_full,
                "cluster_characterizations": sub_chars,
            }
        except ValueError as exc:
            sub_clustering = {
                "parent_cluster_id": int(largest["cluster_id"]),
                "n_members": len(sub_entries),
                "error": str(exc),
            }

    # Map each cluster to its dominant kill_vector signature.
    cluster_kill_vectors = []
    for cid in sorted({e["cluster_id_best_k"] for e in entries}):
        members = [e for e in entries if e["cluster_id_best_k"] == cid]
        # Take the kill_vector of any member (within a cluster they should
        # be uniform on these structural booleans).
        kv = members[0]["kill_vector_signature"]
        # Verify uniformity; record any disagreement.
        uniform = all(m["kill_vector_signature"] == kv for m in members)
        cluster_kill_vectors.append({
            "cluster_id": int(cid),
            "kill_vector_signature": kv,
            "uniform_within_cluster": bool(uniform),
            "size": len(members),
        })

    result = {
        "n_entries": n,
        "feature_keys": list(FEATURE_KEYS),
        "method": method,
        "k_range": list(k_range),
        "random_state": random_state,
        "per_k_clustering": cluster_result["per_k"],
        "best_k": cluster_result["best_k"],
        "best_labels": cluster_result["best_labels"],
        "feature_matrix": X.tolist(),
        "feature_matrix_scaled": cluster_result["X_scaled"],
        "entries": entries,
        "cluster_characterizations": cluster_chars,
        "cluster_kill_vector_map": cluster_kill_vectors,
        "sub_clustering_within_largest_class": sub_clustering,
        "metadata": {
            "honest_framing": (
                "17 entries is too small to claim statistical "
                "significance; this is descriptive structural analysis "
                "of the boundary layer, not a predictive classifier."
            ),
            "forged_by": "Techne (toolsmith)",
            "forged_for": "Charon kill-space gradient field seed",
            "read_only_inputs": [
                str(brute_force_path),
                str(path_a_path),
                str(path_b_path),
                str(path_c_path),
            ],
        },
    }

    if output_path is not None:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, default=_json_default)

    return result


def _json_default(o):
    """JSON encoder fallback for numpy scalars."""
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(f"Object of type {type(o).__name__} is not JSON serialisable")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:  # pragma: no cover -- CLI wrapper
    out = _HERE / "_lehmer_boundary_layer_results.json"
    result = run_boundary_layer(output_path=out)
    n = result["n_entries"]
    best_k = result["best_k"]
    sil = next(
        (r["silhouette"] for r in result["per_k_clustering"] if r["k"] == best_k),
        float("nan"),
    )
    print(f"[lehmer_boundary_layer] n={n}  best_k={best_k}  silhouette={sil:.4f}")
    for cc in result["cluster_characterizations"]:
        print(
            f"  cluster {cc['cluster_id']}: size={cc['size']}  "
            f"path_c={cc['classifications_c']}  "
            f"cyc_n_union={cc['cyclotomic_n_index_union']}"
        )
    print(f"[lehmer_boundary_layer] wrote {out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
