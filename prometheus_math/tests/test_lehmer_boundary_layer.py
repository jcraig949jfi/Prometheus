"""Tests for prometheus_math.lehmer_boundary_layer.

Math-tdd skill rubric: >=3 tests in each of authority / property / edge /
composition. The full pipeline runs in milliseconds (only 17 entries on
already-cached JSONs), so composition tests can run end-to-end.

Honest framing: 17 entries is a small sample. These tests pin the shape
of the descriptive analysis, not predictive claims.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

from prometheus_math.lehmer_boundary_layer import (
    DEFAULT_BRUTE_FORCE_PATH,
    DEFAULT_PATH_A_PATH,
    DEFAULT_PATH_B_PATH,
    DEFAULT_PATH_C_PATH,
    FEATURE_KEYS,
    build_feature_matrix,
    characterize_clusters,
    cluster_features,
    extract_features,
    kill_vector_signature,
    load_all_paths,
    run_boundary_layer,
)


# ---------------------------------------------------------------------------
# Authority -- paper-anchored / data-anchored facts
# ---------------------------------------------------------------------------

def test_authority_three_paths_align_to_17_entries():
    """All four JSONs must align to exactly 17 entries by coeffs_ascending.

    The Charon brute-force run produced 17 NOT-in-Mossinghoff entries in
    the deg-14 +/- 5 palindromic Lehmer band. Paths A, B, C each
    classified the same 17. If alignment fails, the boundary-layer
    analysis is meaningless.
    """
    paths = load_all_paths()
    assert len(paths["brute_force"]) == 17
    assert len(paths["path_a"]) == 17
    assert len(paths["path_b"]) == 17
    assert len(paths["path_c"]) == 17
    # Coefficients must agree position-wise across paths.
    for i in range(17):
        bf_coeffs = paths["brute_force"][i]["coeffs_ascending"]
        a_coeffs = paths["path_a"][i]["coeffs_ascending"]
        b_coeffs = paths["path_b"][i]["coeffs_ascending"]
        c_coeffs = paths["path_c"][i]["coeffs_ascending"]
        assert bf_coeffs == a_coeffs == b_coeffs == c_coeffs, (
            f"alignment broken at index {i}"
        )


def test_authority_lehmer_phi_entries_share_one_cluster():
    """Entries 2 and 14 (0-indexed; the two C2 Lehmer x Phi_n^k entries)
    must end up together in a 2-element cluster -- they are x->-x
    reflection equivalents of one base polynomial.

    Reference: Path C classification, Lehmer x Phi_1^4 (orientation 'x')
    and Lehmer x Phi_2^4 (orientation '-x').
    """
    result = run_boundary_layer()
    labels = result["best_labels"]
    # Find the two C2 entries.
    c2_indices = [
        i for i, e in enumerate(result["entries"])
        if e["classification_c"] == "C2"
    ]
    assert len(c2_indices) == 2, (
        f"expected 2 C2 entries, got {len(c2_indices)}"
    )
    # They must share a cluster id.
    assert labels[c2_indices[0]] == labels[c2_indices[1]], (
        f"C2 entries split across clusters: "
        f"labels={labels[c2_indices[0]]}, {labels[c2_indices[1]]}"
    )
    # That cluster must have size exactly 2 (no C3 contamination).
    c2_cluster = labels[c2_indices[0]]
    cluster_size = sum(1 for lab in labels if lab == c2_cluster)
    assert cluster_size == 2, (
        f"C2 cluster has wrong size: {cluster_size} (expected 2)"
    )


def test_authority_best_k_in_expected_range():
    """At n=17 with one 15-class and one 2-class, the best k must land in
    {2, 3, 4}. This is the gross-structure check: clustering must NOT
    pick k=1 (collapse) and must NOT pick k>=5 (over-fragmentation).
    """
    result = run_boundary_layer(k_range=(2, 3, 4))
    assert result["best_k"] in {2, 3, 4}, (
        f"best_k={result['best_k']} not in {{2,3,4}}"
    )
    # Cluster sizes must sum to 17.
    sizes = [c["size"] for c in result["cluster_characterizations"]]
    assert sum(sizes) == 17, f"cluster sizes sum to {sum(sizes)}, expected 17"


# ---------------------------------------------------------------------------
# Property -- invariants
# ---------------------------------------------------------------------------

def test_property_determinism_with_fixed_seed():
    """Re-running with the same random_state yields identical labels.

    KMeans with n_init>=20 and a fixed seed is deterministic.
    """
    r1 = run_boundary_layer(random_state=42)
    r2 = run_boundary_layer(random_state=42)
    assert r1["best_k"] == r2["best_k"]
    assert r1["best_labels"] == r2["best_labels"]


def test_property_cluster_assignment_stable_across_inits():
    """Different random_states should agree on the dominant 15/2 split
    (modulo cluster id permutation). The 15-2 separation is a
    high-silhouette finding (sil > 0.8); it should not flip with seed.
    """
    seeds = [0, 1, 7, 42, 137]
    cluster_size_sets = []
    for s in seeds:
        r = run_boundary_layer(random_state=s, k_range=(2,))
        sizes = sorted(
            (c["size"] for c in r["cluster_characterizations"]),
            reverse=True,
        )
        cluster_size_sets.append(tuple(sizes))
    # All seeds must produce the same 15/2 size signature.
    assert all(s == (15, 2) for s in cluster_size_sets), (
        f"cluster sizes flipped across seeds: {cluster_size_sets}"
    )


def test_property_cluster_sizes_sum_to_n():
    """For every k in k_range, cluster sizes sum to the input n."""
    result = run_boundary_layer(k_range=(2, 3, 4))
    n = result["n_entries"]
    for per_k in result["per_k_clustering"]:
        total = sum(per_k["cluster_sizes"].values())
        assert total == n, (
            f"k={per_k['k']} sizes sum to {total}, expected {n}"
        )


def test_property_feature_keys_consistent():
    """The feature matrix has one column per FEATURE_KEYS entry."""
    result = run_boundary_layer()
    X = np.array(result["feature_matrix"])
    assert X.shape == (17, len(FEATURE_KEYS)), (
        f"feature matrix shape {X.shape} != (17, {len(FEATURE_KEYS)})"
    )


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_edge_too_few_samples_raises():
    """cluster_features must raise on too-few-samples (e.g. k=4 with n=3)."""
    X = np.array([[1.0, 2.0], [1.5, 2.5], [3.0, 4.0]])
    with pytest.raises(ValueError):
        cluster_features(X, k_range=(4,))


def test_edge_zero_variance_column_handled():
    """A constant column (zero variance, e.g. n_non_cyclotomic_factors=0
    everywhere in a sub-class) must not crash KMeans/silhouette.

    StandardScaler will produce NaNs on a zero-variance column; the
    driver must replace those with 0 so clustering proceeds.
    """
    # 6 points in 3D, where the 3rd column is constant.
    X = np.array([
        [1.0, 0.0, 5.0],
        [1.1, 0.1, 5.0],
        [0.9, -0.1, 5.0],
        [5.0, 5.0, 5.0],
        [5.1, 5.1, 5.0],
        [4.9, 4.9, 5.0],
    ])
    result = cluster_features(X, k_range=(2,), random_state=0)
    assert result["best_k"] == 2
    sizes = result["per_k"][0]["cluster_sizes"]
    assert sum(sizes.values()) == 6


def test_edge_single_member_cluster_kept_when_k_chosen_high():
    """If k=4 produces a singleton cluster, characterize_clusters must
    still return a well-formed entry for it (size=1 is valid).
    """
    # Synthesize 6 entries: 2 close pairs + 2 outliers.
    fake_entries = [
        {**{k: 0.0 for k in FEATURE_KEYS}, "classification_a": "A1",
         "classification_c": "C3", "verdict_a": "x", "failure_mode": "nan_return",
         "cyclotomic_n_indices": [1], "phi_factors_c": {}},
        {**{k: 0.1 for k in FEATURE_KEYS}, "classification_a": "A1",
         "classification_c": "C3", "verdict_a": "x", "failure_mode": "nan_return",
         "cyclotomic_n_indices": [1], "phi_factors_c": {}},
        {**{k: 5.0 for k in FEATURE_KEYS}, "classification_a": "A2",
         "classification_c": "C3", "verdict_a": "y", "failure_mode": "nan_return",
         "cyclotomic_n_indices": [2], "phi_factors_c": {}},
        {**{k: 5.1 for k in FEATURE_KEYS}, "classification_a": "A2",
         "classification_c": "C3", "verdict_a": "y", "failure_mode": "nan_return",
         "cyclotomic_n_indices": [2], "phi_factors_c": {}},
        {**{k: 10.0 for k in FEATURE_KEYS}, "classification_a": "A3",
         "classification_c": "C2", "verdict_a": "z", "failure_mode": "nan_return",
         "cyclotomic_n_indices": [3], "phi_factors_c": {}},
        {**{k: -10.0 for k in FEATURE_KEYS}, "classification_a": "A4",
         "classification_c": "C2", "verdict_a": "w", "failure_mode": "nan_return",
         "cyclotomic_n_indices": [4], "phi_factors_c": {}},
    ]
    # Add coeffs_ascending key required by characterize_clusters.
    for i, e in enumerate(fake_entries):
        e["coeffs_ascending"] = [i, 1, i]
    labels = [0, 0, 1, 1, 2, 3]
    chars = characterize_clusters(fake_entries, labels)
    assert len(chars) == 4
    sizes = sorted(c["size"] for c in chars)
    assert sizes == [1, 1, 2, 2]
    # Singleton clusters must have well-formed feature_stats (min == max).
    for c in chars:
        if c["size"] == 1:
            for key in FEATURE_KEYS:
                stats = c["feature_stats"][key]
                assert stats["min"] == stats["max"]


def test_edge_empty_entries_raises_or_handles():
    """build_feature_matrix on an empty list returns a (0, len(FEATURE_KEYS))
    or empty array; cluster_features on it must reject (need >= k+1 rows).
    """
    X_empty = build_feature_matrix([])
    # numpy on empty list -> shape (0,) or (0, n_features); both are
    # "no rows" and clustering should reject.
    with pytest.raises(ValueError):
        cluster_features(
            X_empty if X_empty.ndim == 2 else X_empty.reshape(0, len(FEATURE_KEYS)),
            k_range=(2,),
        )


# ---------------------------------------------------------------------------
# Composition -- end-to-end pipeline
# ---------------------------------------------------------------------------

def test_composition_full_pipeline_writes_well_formed_json(tmp_path: Path):
    """Running run_boundary_layer with output_path writes JSON with all
    required top-level keys.
    """
    out = tmp_path / "boundary_layer_test.json"
    result = run_boundary_layer(output_path=out)
    assert out.exists()
    with out.open("r", encoding="utf-8") as fh:
        loaded = json.load(fh)
    required_keys = {
        "n_entries", "feature_keys", "method", "k_range",
        "per_k_clustering", "best_k", "best_labels",
        "feature_matrix", "entries",
        "cluster_characterizations", "cluster_kill_vector_map",
        "metadata",
    }
    assert required_keys.issubset(loaded.keys()), (
        f"missing keys: {required_keys - set(loaded.keys())}"
    )
    assert loaded["n_entries"] == 17
    assert len(loaded["entries"]) == 17


def test_composition_cluster_characterization_includes_representatives():
    """Every cluster characterization must have a representative
    polynomial (coeffs_ascending) and structural feature stats.
    """
    result = run_boundary_layer()
    for cc in result["cluster_characterizations"]:
        rep = cc.get("representative_coeffs_ascending")
        assert rep is not None
        assert isinstance(rep, list)
        assert len(rep) == 15  # deg-14 polynomial has 15 coeffs
        # Feature stats must contain every FEATURE_KEY.
        for key in FEATURE_KEYS:
            assert key in cc["feature_stats"]
            stats = cc["feature_stats"][key]
            assert stats["min"] is not None
            assert stats["max"] is not None
            assert stats["mean"] is not None


def test_composition_kill_vector_signature_structurally_valid():
    """Every cluster's kill_vector signature has the required boolean
    fields, and the C2 (Lehmer x Phi_n) cluster has is_lehmer_product=True
    while the C3 (cyclotomic-noise) cluster has is_pure_cyclotomic=True.
    """
    result = run_boundary_layer()
    required_kv_keys = {
        "out_of_band", "has_cyclotomic_factor", "is_lehmer_product",
        "is_pure_cyclotomic", "verification_failed_at_dps30",
        "mossinghoff_proximity_match",
    }
    for cluster_kv in result["cluster_kill_vector_map"]:
        kv = cluster_kv["kill_vector_signature"]
        assert required_kv_keys.issubset(kv.keys())
        # Every kv must be uniform within its cluster (these are
        # structural booleans on the path-C classification).
        assert cluster_kv["uniform_within_cluster"] is True

    # Find the C2 and C3 clusters by their kv.
    has_lehmer_cluster = any(
        c["kill_vector_signature"]["is_lehmer_product"]
        for c in result["cluster_kill_vector_map"]
    )
    has_pure_cyc_cluster = any(
        c["kill_vector_signature"]["is_pure_cyclotomic"]
        for c in result["cluster_kill_vector_map"]
    )
    assert has_lehmer_cluster, "no cluster carries is_lehmer_product=True"
    assert has_pure_cyc_cluster, "no cluster carries is_pure_cyclotomic=True"


def test_composition_per_entry_kill_vector_consistent_with_path_c():
    """Per-entry kill_vector_signature must agree with path C
    classification: C2 -> is_lehmer_product, C3 -> is_pure_cyclotomic.
    """
    result = run_boundary_layer()
    for entry in result["entries"]:
        kv = entry["kill_vector_signature"]
        cls_c = entry["classification_c"]
        if cls_c == "C2":
            assert kv["is_lehmer_product"] is True
            assert kv["is_pure_cyclotomic"] is False
        elif cls_c == "C3":
            assert kv["is_pure_cyclotomic"] is True
            assert kv["is_lehmer_product"] is False
        # All 17 share these:
        assert kv["has_cyclotomic_factor"] is True
        assert kv["verification_failed_at_dps30"] is True


def test_composition_default_data_files_present():
    """The four input JSONs the driver depends on must exist on disk."""
    for p in (
        DEFAULT_BRUTE_FORCE_PATH,
        DEFAULT_PATH_A_PATH,
        DEFAULT_PATH_B_PATH,
        DEFAULT_PATH_C_PATH,
    ):
        assert Path(p).exists(), f"missing input: {p}"


# ---------------------------------------------------------------------------
# Misc unit tests for helper functions
# ---------------------------------------------------------------------------

def test_extract_features_emits_all_feature_keys():
    """extract_features on a real entry produces every FEATURE_KEYS entry."""
    paths = load_all_paths()
    feat = extract_features(
        paths["brute_force"][0], paths["path_a"][0],
        paths["path_b"][0], paths["path_c"][0],
    )
    for key in FEATURE_KEYS:
        assert key in feat, f"missing feature key: {key}"
        val = feat[key]
        # No NaNs in numeric features at this stage.
        assert isinstance(val, (int, float))
        assert not (isinstance(val, float) and math.isnan(val))


def test_kill_vector_signature_unit():
    """kill_vector_signature on a synthesised entry produces correct flags."""
    fake_c2 = {
        "M_path_a": 1.1762808182599175,
        "classification_c": "C2",
        "verdict_a": "rediscovery",
    }
    kv = kill_vector_signature(fake_c2)
    assert kv["is_lehmer_product"] is True
    assert kv["is_pure_cyclotomic"] is False
    assert kv["out_of_band"] is False  # M=1.176 is in band
    assert kv["mossinghoff_proximity_match"] is True

    fake_c3 = {
        "M_path_a": 1.0,
        "classification_c": "C3",
        "verdict_a": "cyclotomic_noise",
    }
    kv = kill_vector_signature(fake_c3)
    assert kv["is_pure_cyclotomic"] is True
    assert kv["is_lehmer_product"] is False
    assert kv["out_of_band"] is True  # M=1.0 is below band (true M)
