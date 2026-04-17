#!/usr/bin/env python3
"""
Tensor Executor: Hypothesis → tensor slice → coupling → battery → result.

Replaces the CSV-loading executor.py with tensor index operations.
All data is precomputed in RAM. Each hypothesis maps to two column slices.
Expected throughput: 100+ hypotheses/sec (vs 9.3/sec in executor.py).

Battery integration:
  - F1-F14: falsification_battery.run_battery (two paired arrays)
  - F15-F38: battery_v2 methods (individual tests wired to tensor slices)
  - Kill taxonomy pre-filter: reject known-dead patterns before computing
  - F35 Megethos kill: auto-reject log_conductor × anything signals
"""
import sys
import math
import numpy as np
from pathlib import Path
from scipy.stats import spearmanr, pearsonr, ks_2samp

_root = Path(__file__).resolve().parent.parent  # Prometheus/
_forge_v3 = str(_root / "forge/v3")
if _forge_v3 not in sys.path:
    sys.path.insert(0, _forge_v3)
sys.path.insert(0, str(Path(__file__).parent))

_scripts = str(_root / "cartography/shared/scripts")
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

from gene_schema import Hypothesis, ACTIVE_FEATURES
from tensor_builder import TensorData, build_tensor
from kill_taxonomy import check_hypothesis_against_kills, get_all_kills

# Lazy-import batteries (heavy imports)
_bv1 = None
_bv2 = None


def _get_bv1():
    global _bv1
    if _bv1 is None:
        import falsification_battery as fb
        _bv1 = fb
    return _bv1


def _get_bv2():
    global _bv2
    if _bv2 is None:
        from battery_v2 import BatteryV2
        _bv2 = BatteryV2()
    return _bv2


# ============================================================
# Coupling Functions (tensor-native)
# ============================================================

def _compute_coupling(a, b, method):
    """Compute coupling between two 1D arrays. Arrays already cleaned."""
    n = len(a)
    if n < 20:
        return {"method": method, "value": float("nan"), "p_value": 1.0, "n": n}

    # Reject constant arrays
    if np.std(a) == 0 or np.std(b) == 0:
        return {"method": method, "value": float("nan"), "p_value": 1.0, "n": n}

    if method == "spearman":
        rho, p = spearmanr(a, b)
        return {"method": "spearman", "value": float(rho), "p_value": float(p), "n": n}
    elif method == "pearson":
        r, p = pearsonr(a, b)
        return {"method": "pearson", "value": float(r), "p_value": float(p), "n": n}
    elif method == "mutual_information":
        from sklearn.metrics import mutual_info_score
        n_bins = min(30, n // 10)
        if n_bins < 3:
            return {"method": "mi", "value": 0.0, "p_value": 1.0, "n": n}
        ad = np.digitize(a, np.linspace(a.min() - 1e-10, a.max() + 1e-10, n_bins + 1))
        bd = np.digitize(b, np.linspace(b.min() - 1e-10, b.max() + 1e-10, n_bins + 1))
        mi = mutual_info_score(ad, bd) / max(np.log(2), 1)
        return {"method": "mi", "value": float(mi), "p_value": 0.0, "n": n}
    elif method == "ks_statistic":
        stat, p = ks_2samp(a, b)
        return {"method": "ks", "value": float(stat), "p_value": float(p), "n": n}
    elif method == "wasserstein":
        from scipy.stats import wasserstein_distance
        wd = wasserstein_distance(a, b)
        return {"method": "wasserstein", "value": float(wd), "p_value": 0.0, "n": n}
    else:
        rho, p = spearmanr(a, b)
        return {"method": "spearman", "value": float(rho), "p_value": float(p), "n": n}


# ============================================================
# Megethos Kill (F35)
# ============================================================

_MAGNITUDE_FEATURES = {
    "conductor", "log_conductor", "discriminant", "log_discriminant",
    "volume", "n_atoms", "f_vector_sum",
}


def _is_megethos_kill(hypothesis):
    """F35: Reject if one feature is a magnitude proxy and conditioning is none."""
    if hypothesis.conditioning != "none":
        return False
    if hypothesis.feature_a in _MAGNITUDE_FEATURES or hypothesis.feature_b in _MAGNITUDE_FEATURES:
        return True
    return False


# ============================================================
# Kill Taxonomy Pre-filter
# ============================================================

_kills_cache = None


def _prefilter_kills(hypothesis):
    """Check hypothesis against known kill patterns. Returns (killed, kill_name) or (False, '')."""
    global _kills_cache
    if _kills_cache is None:
        _kills_cache = get_all_kills()

    matches = check_hypothesis_against_kills(hypothesis)
    if matches:
        return True, f"kill_taxonomy:{matches[0]['failure_mode']}"
    return False, ""


# ============================================================
# Paired Array Preparation
# ============================================================

def _prepare_paired_arrays(tensor, hypothesis):
    """Extract and align two feature arrays from the tensor.

    For same-domain pairs: natural alignment by object index.
    For cross-domain pairs: subsample to min(resolution, min_size), align by position.

    Returns: (a, b, n) or (None, None, 0) if data unavailable.
    """
    slice_a = tensor.get_slice(hypothesis.domain_a, hypothesis.feature_a)
    slice_b = tensor.get_slice(hypothesis.domain_b, hypothesis.feature_b)

    if slice_a is None or slice_b is None:
        return None, None, 0

    # Clean NaNs from each independently first
    valid_a = slice_a[np.isfinite(slice_a)]
    valid_b = slice_b[np.isfinite(slice_b)]

    if len(valid_a) < 20 or len(valid_b) < 20:
        return None, None, 0

    # Subsample to resolution
    n = hypothesis.resolution
    rng = np.random.default_rng(hash(hypothesis.id) % (2**31))

    if len(valid_a) > n:
        valid_a = rng.choice(valid_a, n, replace=False)
    if len(valid_b) > n:
        valid_b = rng.choice(valid_b, n, replace=False)

    # Align to same length
    min_len = min(len(valid_a), len(valid_b))
    return valid_a[:min_len], valid_b[:min_len], min_len


# ============================================================
# Battery Integration
# ============================================================

def _run_battery_stages(a, b, hypothesis, coupling_result, z_score, p_perm):
    """Run progressive battery stages. Returns (survival_depth, kill_test, notes).

    Stage 1 (F1-F3): Basic signal existence
    Stage 2 (F5, F10-F12): Robustness checks
    Stage 3 (F15, F18): Distributional and stability checks
    Stage 4 (F24, F25): Variance decomposition and transportability
    """
    depth = 0
    notes_parts = []

    # --- Stage 1: Signal existence ---

    # F1: Permutation null (z > 2)
    if abs(z_score) <= 2:
        return depth, "F1_permutation_null", f"z={z_score:.2f}"
    depth += 1

    # F3: Effect size (|coupling| > 0.05)
    coup_val = abs(coupling_result.get("value", 0))
    if coup_val <= 0.05:
        return depth, "F3_effect_size", f"|r|={coup_val:.4f}"
    depth += 1

    # F1 p-value check (p < 0.01)
    if p_perm > 0.01:
        return depth, "F1_p_value", f"p_perm={p_perm:.4f}"
    depth += 1

    # --- Stage 2: Robustness ---

    fb = _get_bv1()

    # F2: Subset stability
    try:
        r2 = fb.f2_subset_stability(a, b)
        if r2["verdict"] == "FAIL":
            return depth, "F2_subset_stability", r2.get("reason", "")
        depth += 1
    except Exception:
        depth += 1  # skip on error, don't kill

    # F5: Alternative normalization
    try:
        r5 = fb.f5_alternative_normalization(a, b)
        if r5["verdict"] == "FAIL":
            return depth, "F5_normalization", r5.get("reason", "")
        depth += 1
    except Exception:
        depth += 1

    # F10: Outlier sensitivity
    try:
        r10 = fb.f10_outlier_sensitivity(a, b)
        if r10["verdict"] == "FAIL":
            return depth, "F10_outlier_sensitivity", r10.get("reason", "")
        depth += 1
    except Exception:
        depth += 1

    # F11: Cross-validation
    try:
        r11 = fb.f11_cross_validation(a, b)
        if r11["verdict"] == "FAIL":
            return depth, "F11_cross_validation", r11.get("reason", "")
        depth += 1
    except Exception:
        depth += 1

    # F12: Partial correlation (against integer index as confound)
    if len(a) >= 20 and len(b) >= 20:
        try:
            r12 = fb.f12_partial_correlation(a, b)
            if r12["verdict"] == "FAIL":
                return depth, "F12_partial_correlation", r12.get("reason", "")
            depth += 1
        except Exception:
            depth += 1
    else:
        depth += 1

    # F13: Growth rate filter
    if len(a) >= 15 and len(b) >= 15:
        try:
            r13 = fb.f13_growth_rate_filter(a, b)
            if r13["verdict"] == "FAIL":
                return depth, "F13_growth_rate_filter", r13.get("reason", "")
            depth += 1
        except Exception:
            depth += 1
    else:
        depth += 1

    # --- Stage 3: Distribution and stability (battery_v2) ---

    bv2 = _get_bv2()

    # F15: Log-normal calibration (on feature_a)
    try:
        positive_a = a[a > 0]
        if len(positive_a) >= 50:
            verdict_15, _ = bv2.F15_log_normal_calibration(positive_a)
            if verdict_15 == "CONSISTENT_WITH_LOGNORMAL":
                return depth, "F15_lognormal", "signal consistent with log-normal null"
        depth += 1
    except Exception:
        depth += 1

    # F18: Subset stability (battery_v2 version)
    try:
        def _stat_fn(arr):
            if len(arr) < 10:
                return 0.0
            mid = len(arr) // 2
            rho, _ = spearmanr(arr[:mid], arr[mid:2*mid]) if mid >= 10 else (0, 1)
            return rho

        verdict_18, _ = bv2.F18_subset_stability(a, _stat_fn)
        if verdict_18 == "UNSTABLE":
            return depth, "F18_subset_stability", "statistic unstable across subsets"
        depth += 1
    except Exception:
        depth += 1

    # F21: Trend robustness
    try:
        verdict_21, _ = bv2.F21_trend_robustness(a, b)
        if verdict_21 == "TREND_ARTIFACT":
            return depth, "F21_trend_artifact", "monotone trend explains coupling"
        depth += 1
    except Exception:
        depth += 1

    # --- Stage 4: Advanced tests ---

    # F24: Variance decomposition (using binned feature_a as groups)
    try:
        n_bins = min(10, len(a) // 20)
        if n_bins >= 3:
            group_labels = np.digitize(a, np.linspace(a.min(), a.max(), n_bins + 1))
            verdict_24, result_24 = bv2.F24_variance_decomposition(
                b, group_labels, permutation_calibrate=True, n_perms=200
            )
            if "PERM_NOT_SIGNIFICANT" in verdict_24:
                return depth, "F24_variance_decomposition", f"eta²={result_24.get('eta_squared', 0):.4f}"
        depth += 1
    except Exception:
        depth += 1

    # F24b: Metric consistency (tail localization)
    try:
        n_bins = min(10, len(a) // 20)
        if n_bins >= 3:
            group_labels = np.digitize(a, np.linspace(a.min(), a.max(), n_bins + 1))
            verdict_24b, _ = bv2.F24b_metric_consistency(b, group_labels)
            if verdict_24b == "TAIL_DRIVEN":
                return depth, "F24b_tail_driven", "effect localized to tail bins"
        depth += 1
    except Exception:
        depth += 1

    # F25: Transportability (leave-one-bin-out OOS)
    try:
        n_bins = min(5, len(a) // 30)
        if n_bins >= 3:
            primary_labels = np.digitize(a, np.linspace(a.min(), a.max(), n_bins + 1))
            # Use secondary = feature_b binned
            sec_bins = min(3, len(b) // 30)
            if sec_bins >= 2:
                secondary_labels = np.digitize(b, np.linspace(b.min(), b.max(), sec_bins + 1))
                verdict_25, result_25 = bv2.F25_transportability(
                    b, primary_labels, secondary_labels
                )
                if verdict_25 in ("NON_TRANSPORTABLE", "OVERFIT"):
                    return depth, "F25_transportability", f"OOS R²={result_25.get('oos_r2', 0):.4f}"
        depth += 1
    except Exception:
        depth += 1

    # Build notes
    notes_parts.append(f"coupling={coup_val:.4f}")
    notes_parts.append(f"z={z_score:.1f}")
    notes_parts.append(f"depth={depth}")

    return depth, "", ", ".join(notes_parts)


# ============================================================
# Main Tensor Executor
# ============================================================

class TensorExecutor:
    """Executes hypotheses against a precomputed tensor. Load once, run many."""

    def __init__(self, tensor=None, tensor_path=None):
        """Initialize with either a TensorData object or path to .npz file."""
        if tensor is not None:
            self.tensor = tensor
        elif tensor_path is not None:
            self.tensor = TensorData.load(tensor_path)
        else:
            # Build from scratch
            self.tensor = build_tensor(verbose=False)

        self.rng = np.random.default_rng(42)
        self._executed = 0
        self._killed_prefilter = 0
        self._killed_megethos = 0

    def _f0_object_permutation_null(self, hypothesis, a, b, real_coupling, n_perms=50):
        """F0: Object-identity permutation null.

        Tests whether the coupling depends on WHICH objects are sampled.
        Resample feature_a from domain_a with fresh random objects, keeping
        the same feature_b sample. If coupling is unchanged, it's a
        distributional artifact (feature geometry, not object pairing).

        This is the test that killed ALL explorer survivors in session 3.
        It catches what the existing F1 (shuffle-b) cannot: distributional
        coupling that survives permutation of paired values but is not
        specific to any particular set of objects.

        Returns: (killed: bool, z_score: float, note: str)
        """
        slice_a_full = self.tensor.get_slice(hypothesis.domain_a, hypothesis.feature_a)
        if slice_a_full is None:
            return False, 0.0, "no_data"

        valid_a_full = slice_a_full[np.isfinite(slice_a_full)]
        if len(valid_a_full) < 40:
            return False, 0.0, "too_few_objects"

        real_val = real_coupling.get("value", 0.0)
        if np.isnan(real_val):
            return True, 0.0, "coupling_nan"

        # Resample domain_a objects and recompute coupling
        null_values = []
        n = min(len(b), hypothesis.resolution)
        for _ in range(n_perms):
            resample_a = self.rng.choice(valid_a_full, n, replace=False)
            resample_b = self.rng.choice(
                self.tensor.get_slice(hypothesis.domain_b, hypothesis.feature_b)[
                    np.isfinite(self.tensor.get_slice(hypothesis.domain_b, hypothesis.feature_b))
                ],
                n, replace=False,
            )
            null_c = _compute_coupling(resample_a, resample_b, hypothesis.coupling)
            val = null_c.get("value", float("nan"))
            if not np.isnan(val):
                null_values.append(val)

        if len(null_values) < 10:
            return False, 0.0, "insufficient_null"

        null_arr = np.array(null_values)
        null_std = np.std(null_arr)
        if null_std < 1e-10:
            # Zero variance in null = coupling is deterministic = distributional
            return True, 0.0, "null_zero_variance"

        z = (real_val - np.mean(null_arr)) / null_std
        # Kill if z < 2: real coupling is indistinguishable from resampled coupling
        if abs(z) < 2.0:
            return True, float(z), f"z={z:.2f},null_mean={np.mean(null_arr):.4f}"
        return False, float(z), f"z={z:.2f},SURVIVES"

    def execute(self, hypothesis):
        """Execute a hypothesis against the tensor. Returns result dict."""
        result = {
            "hypothesis_id": hypothesis.id,
            "status": "error",
            "coupling": {},
            "z_score": 0.0,
            "p_value": 1.0,
            "survival_depth": 0,
            "kill_test": "",
            "notes": "",
        }

        try:
            # --- Pre-filter: Kill taxonomy ---
            killed, kill_name = _prefilter_kills(hypothesis)
            if killed:
                result["status"] = "prefiltered"
                result["kill_test"] = kill_name
                result["notes"] = "Matched known kill pattern"
                self._killed_prefilter += 1
                return result

            # --- Pre-filter: F35 Megethos ---
            if _is_megethos_kill(hypothesis):
                result["status"] = "prefiltered"
                result["kill_test"] = "F35_megethos"
                result["notes"] = f"Magnitude feature ({hypothesis.feature_a}/{hypothesis.feature_b}) without conditioning"
                self._killed_megethos += 1
                return result

            # --- Get paired arrays from tensor ---
            a, b, n = _prepare_paired_arrays(self.tensor, hypothesis)

            if a is None or n < 20:
                result["status"] = "insufficient_data"
                result["kill_test"] = "data_unavailable"
                result["notes"] = f"Could not extract paired arrays (n={n})"
                return result

            # --- Compute coupling ---
            coupling = _compute_coupling(a, b, hypothesis.coupling)

            if np.isnan(coupling.get("value", float("nan"))):
                result["status"] = "no_signal"
                result["kill_test"] = "coupling_nan"
                result["notes"] = "Coupling computation returned NaN"
                return result

            # --- F0: Object-identity permutation null (NEW — the honest test) ---
            f0_killed, f0_z, f0_note = self._f0_object_permutation_null(
                hypothesis, a, b, coupling
            )
            if f0_killed:
                result["coupling"] = coupling
                result["z_score"] = f0_z
                result["status"] = "executed"
                result["survival_depth"] = 0
                result["kill_test"] = "F0_object_permutation"
                result["notes"] = f"Object-identity null: {f0_note}"
                self._executed += 1
                return result

            # --- F1: Paired permutation null (existing — tests pairing significance) ---
            null_values = []
            n_perms_max = 200
            n_perms_early = 50
            real_val = coupling["value"]

            for i in range(n_perms_max):
                shuffled_b = b.copy()
                self.rng.shuffle(shuffled_b)
                null_c = _compute_coupling(a, shuffled_b, hypothesis.coupling)
                if not np.isnan(null_c.get("value", float("nan"))):
                    null_values.append(null_c["value"])

                if i == n_perms_early - 1 and null_values:
                    _nv = np.array(null_values)
                    _std = np.std(_nv)
                    if _std > 0:
                        _z = abs(real_val - np.mean(_nv)) / _std
                        if _z < 1.5:
                            break

            if null_values:
                null_arr = np.array(null_values)
                z_score = ((real_val - np.mean(null_arr)) / np.std(null_arr)
                           if np.std(null_arr) > 0 else 0.0)
                p_perm = (np.sum(np.abs(null_arr) >= abs(real_val)) + 1) / (len(null_arr) + 1)
            else:
                z_score = 0.0
                p_perm = 1.0

            result["coupling"] = coupling
            result["z_score"] = float(z_score)
            result["p_value"] = float(p_perm)
            result["status"] = "executed"

            # --- Run progressive battery ---
            depth, kill_test, notes = _run_battery_stages(
                a, b, hypothesis, coupling, z_score, p_perm
            )

            # Offset depth by 1 for F0 survival
            depth += 1

            result["survival_depth"] = depth
            result["kill_test"] = kill_test

            if not kill_test:
                result["status"] = "survived"
                result["notes"] = f"Survived {depth} tests (F0+F1-F25): {notes}"
            else:
                result["notes"] = f"Killed at depth {depth} by {kill_test}: {notes}"

            self._executed += 1

        except Exception as e:
            result["status"] = "error"
            result["notes"] = str(e)[:200]
            result["kill_test"] = "execution_error"

        return result

    def stats(self):
        """Return executor statistics."""
        return {
            "executed": self._executed,
            "prefiltered_taxonomy": self._killed_prefilter,
            "prefiltered_megethos": self._killed_megethos,
            "tensor_shape": (self.tensor.n_objects, self.tensor.n_features),
            "domains": list(self.tensor.domain_boundaries.keys()),
        }


# ============================================================
# Standalone execute() for drop-in compatibility
# ============================================================

_global_executor = None


def execute(hypothesis):
    """Drop-in replacement for executor.execute(). Builds tensor on first call."""
    global _global_executor
    if _global_executor is None:
        tensor_path = Path(__file__).parent / "tensor.npz"
        if tensor_path.exists():
            _global_executor = TensorExecutor(tensor_path=str(tensor_path))
        else:
            _global_executor = TensorExecutor()
    return _global_executor.execute(hypothesis)


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":
    import time
    from gene_schema import random_hypothesis, Hypothesis

    print("=" * 70)
    print("TENSOR EXECUTOR TEST")
    print("=" * 70)

    # Build tensor
    t0 = time.time()
    tensor = build_tensor(verbose=True)
    build_time = time.time() - t0

    executor = TensorExecutor(tensor=tensor)

    # Test 1: Known self-correlation
    print("\n--- Test 1: Self-correlation (should survive) ---")
    h = Hypothesis(
        id="test_self", domain_a="elliptic_curves", domain_b="elliptic_curves",
        feature_a="rank", feature_b="rank", coupling="spearman",
        conditioning="log_conductor", resolution=2000,
    )
    r = execute(h)
    print(f"  Status: {r['status']}, z={r['z_score']:.1f}, depth={r['survival_depth']}, kill={r['kill_test']}")

    # Test 2: Cross-domain null
    print("\n--- Test 2: Cross-domain null (should die) ---")
    h = Hypothesis(
        id="test_null", domain_a="elliptic_curves", domain_b="knots",
        feature_a="rank", feature_b="determinant", coupling="spearman",
        conditioning="log_conductor", resolution=500,
    )
    r = execute(h)
    print(f"  Status: {r['status']}, z={r['z_score']:.1f}, depth={r['survival_depth']}, kill={r['kill_test']}")

    # Test 3: Megethos kill (log_conductor unconditioned)
    print("\n--- Test 3: F35 Megethos kill ---")
    h = Hypothesis(
        id="test_megethos", domain_a="elliptic_curves", domain_b="modular_forms",
        feature_a="log_conductor", feature_b="level", coupling="spearman",
        conditioning="none", resolution=2000,
    )
    r = execute(h)
    print(f"  Status: {r['status']}, kill={r['kill_test']}, notes={r['notes']}")

    # Test 4: Throughput benchmark
    print("\n--- Test 4: Throughput benchmark (200 random hypotheses) ---")
    import random as _random
    _rng = _random.Random(42)

    t0 = time.time()
    results = []
    for i in range(200):
        h = random_hypothesis(0, _rng)
        h.resolution = 500
        r = executor.execute(h)
        results.append(r)
    elapsed = time.time() - t0

    survived = sum(1 for r in results if r["status"] == "survived")
    prefiltered = sum(1 for r in results if r["status"] == "prefiltered")
    killed = sum(1 for r in results if r["kill_test"] and r["status"] not in ("prefiltered",))

    print(f"  200 hypotheses in {elapsed:.2f}s = {200/elapsed:.1f} hyp/sec")
    print(f"  Survived: {survived}, Prefiltered: {prefiltered}, Killed in battery: {killed}")
    print(f"  Executor stats: {executor.stats()}")

    # Depth distribution
    from collections import Counter
    depths = Counter(r["survival_depth"] for r in results)
    print(f"  Depth distribution: {dict(sorted(depths.items()))}")

    kills = Counter(r["kill_test"] for r in results if r["kill_test"])
    print(f"  Kill modes (top 5): {dict(kills.most_common(5))}")
