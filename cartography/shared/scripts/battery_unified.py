#!/usr/bin/env python3
"""
Unified Battery Runner — F1-F23 in one interface.

Wraps falsification_battery.py (F1-F14) + battery_v2.py (F15-F23).
Produces structured JSONL logs via battery_logger.py.

Two modes:
  1. Correlation mode: test whether two series are correlated (F1-F14)
  2. Distribution mode: test a distribution's properties (F15-F23)
  3. Full mode: both, when applicable

Usage:
    from battery_unified import UnifiedBattery
    ub = UnifiedBattery()

    # Test a distribution property (e.g., M4/M2^2 of conductors)
    result = ub.test_distribution(
        finding_id="P1",
        claim="G2 conductor M4/M2^2 = USp(4) = 3.0",
        values=conductor_array,
        predicted_value=3.0,
        data_source="genus2 66K curves",
        domain_is_multiplicative=True,
    )

    # Test a correlation (e.g., config -> energy enrichment)
    result = ub.test_correlation(
        finding_id="P3",
        claim="electron config enrichment on energy levels",
        values_a=config_distances,
        values_b=energy_distances,
        data_source="NIST ASD 42K levels",
        confounds={"Z": atomic_numbers},
    )
"""

import sys
import os
import numpy as np
from pathlib import Path

# Ensure scripts dir is on path
_scripts_dir = str(Path(__file__).resolve().parent)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from battery_v2 import BatteryV2
from battery_logger import BatteryLogger


# Try to import F1-F14; graceful fallback if cycle_logger not available
try:
    import falsification_battery as fb
    HAS_F1_F14 = True
except ImportError:
    HAS_F1_F14 = False


def _m4_m2_sq(values):
    """Compute M4/M2^2 (excess kurtosis-adjacent statistic)."""
    v = np.array(values, dtype=float)
    v = v[np.isfinite(v)]
    if len(v) < 10:
        return float("nan")
    vn = v / np.mean(v) if np.mean(v) != 0 else v
    m2 = np.mean(vn ** 2)
    m4 = np.mean(vn ** 4)
    return m4 / m2 ** 2 if m2 > 0 else float("nan")


class UnifiedBattery:
    """F1-F23 unified runner with structured logging."""

    def __init__(self, log_dir=None, seed=42):
        self.bv2 = BatteryV2(rng_seed=seed)
        self.logger = BatteryLogger(log_dir=log_dir)
        self.seed = seed

    def test_distribution(self, finding_id: str, claim: str, values,
                          predicted_value: float = None,
                          data_source: str = "",
                          domain_is_multiplicative: bool = False,
                          synthetic_generator=None,
                          group_labels=None,
                          confound_values=None,
                          X_for_regression=None,
                          Y_for_regression=None,
                          notes: str = ""):
        """Run distribution-focused tests (F15-F23) on a set of values.

        Args:
            values: The distribution to test
            predicted_value: Theoretical prediction for M4/M2^2 (for F16)
            domain_is_multiplicative: True if values are naturally multiplicative (for F15)
            synthetic_generator: callable(n) -> array for F19
            group_labels: array of group labels for F17
            confound_values: array of confound values for F17
            X_for_regression, Y_for_regression: paired data for F21/F22/F23
        """
        values = np.array(values, dtype=float)
        values = values[np.isfinite(values)]
        n_samples = len(values)
        tests = {}

        # F15: Log-normal calibration
        verdict, result = self.bv2.F15_log_normal_calibration(
            values, domain_is_multiplicative=domain_is_multiplicative
        )
        tests["F15"] = {"verdict": verdict, **result}

        # F16: Equivalence test (if predicted value given)
        if predicted_value is not None:
            verdict, result = self.bv2.F16_equivalence_test(values, predicted_value)
            tests["F16"] = {"verdict": verdict, **result}

        # F17: Confound sensitivity (if group labels + confound given)
        if group_labels is not None and confound_values is not None:
            verdict, result = self.bv2.F17_confound_sensitivity(
                values, group_labels, confound_values
            )
            tests["F17"] = {"verdict": verdict, **result}

        # F18: Subset stability
        verdict, result = self.bv2.F18_subset_stability(values, _m4_m2_sq)
        tests["F18"] = {"verdict": verdict, **result}

        # F19: Generative replay (if synthetic generator given)
        if synthetic_generator is not None:
            verdict, result = self.bv2.F19_generative_replay(
                values, synthetic_generator, _m4_m2_sq
            )
            # Micro-refinement: variance ratio check
            if result.get("synthetic_std", 0) > 0:
                var_ratio = result["synthetic_std"] / abs(result.get("real_statistic", 1))
                result["variance_ratio"] = var_ratio
                if var_ratio > 10:
                    verdict = "MODEL_MISSPECIFIED"
                    result["note"] = "variance_ratio > 10: model too noisy to test"
            tests["F19"] = {"verdict": verdict, **result}

        # F20: Representation invariance
        verdict, result = self.bv2.F20_representation_invariance(values, _m4_m2_sq)
        tests["F20"] = {"verdict": verdict, **result}

        # F21: Trend robustness (if paired data given)
        if X_for_regression is not None and Y_for_regression is not None:
            verdict, result = self.bv2.F21_trend_robustness(
                X_for_regression, Y_for_regression
            )
            tests["F21"] = {"verdict": verdict, **result}

        # F22: Representation alignment (if paired data given)
        if X_for_regression is not None and Y_for_regression is not None:
            try:
                verdict, result = self.bv2.F22_representation_alignment(
                    X_for_regression, Y_for_regression
                )
                tests["F22"] = {"verdict": verdict, **result}
            except Exception as e:
                tests["F22"] = {"verdict": "ERROR", "error": str(e)}

        # F23: Latent confound discovery (if paired data given)
        if X_for_regression is not None and Y_for_regression is not None:
            try:
                verdict, result = self.bv2.F23_latent_confound_discovery(
                    X_for_regression, Y_for_regression
                )
                tests["F23"] = {"verdict": verdict, **result}
            except Exception as e:
                tests["F23"] = {"verdict": "ERROR", "error": str(e)}

        # F24: Variance decomposition (mandatory annotation, if groups given)
        if group_labels is not None:
            verdict, result = self.bv2.F24_variance_decomposition(values, group_labels)
            tests["F24"] = {"verdict": verdict, **result}

            # F24b: Metric consistency (tail-driven check)
            verdict, result = self.bv2.F24b_metric_consistency(values, group_labels)
            tests["F24b"] = {"verdict": verdict, **result}

        # Classify
        overall = self._classify_distribution(tests)

        # Log
        self.logger.log_run(
            finding_id=finding_id, claim=claim, data_source=data_source,
            n_samples=n_samples, tests_run=tests,
            overall_verdict=overall["verdict"], tier=overall["tier"],
            notes=notes,
            extra={"mode": "distribution", "predicted_value": predicted_value}
        )

        return {"tests": tests, "overall": overall, "n_samples": n_samples}

    def test_correlation(self, finding_id: str, claim: str,
                         values_a, values_b,
                         data_source: str = "",
                         confounds: dict = None,
                         dose_levels=None,
                         dose_labels=None,
                         subgroups=None,
                         n_hypotheses_tested: int = 3,
                         index_values=None,
                         notes: str = ""):
        """Run correlation-focused tests (F1-F14) on paired arrays.

        Falls back gracefully if falsification_battery.py is unavailable.
        """
        values_a = np.array(values_a, dtype=float)
        values_b = np.array(values_b, dtype=float)
        n_samples = min(len(values_a), len(values_b))
        tests = {}

        if HAS_F1_F14:
            verdict_f14, results_f14 = fb.run_battery(
                values_a, values_b,
                confounds=confounds,
                dose_levels=dose_levels,
                dose_labels=dose_labels,
                subgroups=subgroups,
                n_hypotheses_tested=n_hypotheses_tested,
                index_values=index_values,
                claim=claim,
            )
            # Convert F1-F14 results to dict keyed by test name
            for r in results_f14:
                test_name = r["test"].split("_")[0].upper()  # e.g. "F1"
                tests[test_name] = {k: v for k, v in r.items()}
        else:
            verdict_f14 = "SKIPPED"
            tests["F1-F14"] = {"verdict": "SKIPPED", "reason": "falsification_battery not importable"}

        # Also run F21 trend robustness on the correlation
        if n_samples >= 30:
            v21, r21 = self.bv2.F21_trend_robustness(values_a[:n_samples], values_b[:n_samples])
            tests["F21"] = {"verdict": v21, **r21}

        # F23 latent confound on the correlation
        if n_samples >= 100:
            try:
                v23, r23 = self.bv2.F23_latent_confound_discovery(
                    values_a[:n_samples], values_b[:n_samples]
                )
                tests["F23"] = {"verdict": v23, **r23}
            except Exception as e:
                tests["F23"] = {"verdict": "ERROR", "error": str(e)}

        overall = self._classify_correlation(tests, verdict_f14)

        self.logger.log_run(
            finding_id=finding_id, claim=claim, data_source=data_source,
            n_samples=n_samples, tests_run=tests,
            overall_verdict=overall["verdict"], tier=overall["tier"],
            notes=notes,
            extra={"mode": "correlation"}
        )

        return {"tests": tests, "overall": overall, "n_samples": n_samples}

    def test_full(self, finding_id: str, claim: str,
                  values, values_a=None, values_b=None,
                  predicted_value: float = None,
                  data_source: str = "",
                  domain_is_multiplicative: bool = False,
                  synthetic_generator=None,
                  confounds: dict = None,
                  group_labels=None, confound_values=None,
                  notes: str = ""):
        """Run both distribution (F15-F23) and correlation (F1-F14) tests."""
        results = {}

        # Distribution tests on values
        dist_result = self.test_distribution(
            finding_id=finding_id + "_dist", claim=claim + " [distribution]",
            values=values, predicted_value=predicted_value,
            data_source=data_source,
            domain_is_multiplicative=domain_is_multiplicative,
            synthetic_generator=synthetic_generator,
            group_labels=group_labels, confound_values=confound_values,
            notes=notes,
        )
        results["distribution"] = dist_result

        # Correlation tests if paired data given
        if values_a is not None and values_b is not None:
            corr_result = self.test_correlation(
                finding_id=finding_id + "_corr", claim=claim + " [correlation]",
                values_a=values_a, values_b=values_b,
                data_source=data_source,
                confounds=confounds,
                notes=notes,
            )
            results["correlation"] = corr_result

        return results

    def _classify_distribution(self, tests: dict) -> dict:
        """Classify a distribution finding based on test results."""
        # Count verdicts by tier
        tier_a_pass = False  # F18 is Tier A for distributions
        tier_b_pass = False  # F17, F21 are Tier B
        tier_c_info = {}     # F15, F16, F19, F20, F22 are Tier C (diagnostic)
        kills = []

        # F18 (Tier A): subset stability
        if "F18" in tests:
            v = tests["F18"]["verdict"]
            if v == "STABLE":
                tier_a_pass = True
            elif v == "UNSTABLE":
                kills.append("F18")

        # F17 (Tier B): confound sensitivity
        if "F17" in tests:
            v = tests["F17"]["verdict"]
            if v in ("CONFOUND_ROBUST",):
                tier_b_pass = True
            elif v == "CONFOUND_DOMINATED":
                kills.append("F17")

        # F21 (Tier B): trend robustness
        if "F21" in tests:
            v = tests["F21"]["verdict"]
            if v == "ROBUST":
                tier_b_pass = True
            elif v == "TREND_CONFOUND":
                kills.append("F21")

        # F23 (Tier B): latent confound
        if "F23" in tests:
            v = tests["F23"]["verdict"]
            if v == "NO_CONFOUND":
                tier_b_pass = True
            elif v == "LATENT_CONFOUND":
                kills.append("F23")

        # Tier C diagnostics (not gates)
        for t in ("F15", "F16", "F19", "F20", "F22"):
            if t in tests:
                tier_c_info[t] = tests[t]["verdict"]

        # F24/F24b: effect size annotation (mandatory, not a gate)
        effect_size = None
        tail_driven = False
        if "F24" in tests:
            effect_size = tests["F24"]["verdict"]
            tier_c_info["F24"] = effect_size
        if "F24b" in tests:
            td = tests["F24b"]["verdict"]
            tier_c_info["F24b"] = td
            tail_driven = ("TAIL_DRIVEN" in td)  # catches TAIL_DRIVEN and EXTREME_TAIL_DRIVEN

        if kills:
            return {"verdict": "KILLED", "tier": "KILLED", "kills": kills, "tier_c": tier_c_info}

        if tier_a_pass and tier_b_pass:
            # Classify finding type by effect geometry:
            #   LAW:        strong effect (eta² > 0.14), not tail-driven
            #   CONSTRAINT: tail-driven effect (any size)
            #   TENDENCY:   small/moderate effect, not tail-driven
            #   PROBABLE:   fallback when F24 didn't run
            if effect_size in ("STRONG_EFFECT",) and not tail_driven:
                finding_type = "LAW"
            elif tail_driven:
                finding_type = "CONSTRAINT"
            elif effect_size in ("MODERATE_EFFECT",):
                finding_type = "TENDENCY" if not tail_driven else "CONSTRAINT"
            elif effect_size in ("SMALL_EFFECT", "NEGLIGIBLE_EFFECT"):
                finding_type = "TENDENCY"
            else:
                finding_type = "PROBABLE"

            eta_sq = tests.get("F24", {}).get("eta_squared", None)
            eta_str = f", eta²={eta_sq:.3f}" if eta_sq is not None else ""
            return {
                "verdict": finding_type,
                "tier": f"B+ ({finding_type.lower()}{eta_str})",
                "tier_c": tier_c_info,
                "effect_size": effect_size,
                "tail_driven": tail_driven,
                "finding_type": finding_type,
            }
        elif tier_a_pass:
            return {"verdict": "POSSIBLE", "tier": "A", "tier_c": tier_c_info}
        else:
            return {"verdict": "CONJECTURE", "tier": "unclassified", "tier_c": tier_c_info}

    def _classify_correlation(self, tests: dict, verdict_f14: str) -> dict:
        """Classify a correlation finding based on F1-F14 + extended tests."""
        kills = []

        # F1-F14 verdict
        if verdict_f14 == "KILLED":
            # Find which tests failed
            for tname, tdata in tests.items():
                if isinstance(tdata, dict) and tdata.get("verdict") == "FAIL":
                    kills.append(tname)

        # F21 trend kill
        if "F21" in tests and tests["F21"]["verdict"] == "TREND_CONFOUND":
            kills.append("F21")

        # F23 latent confound kill
        if "F23" in tests and tests["F23"]["verdict"] == "LATENT_CONFOUND":
            kills.append("F23")

        if kills:
            return {"verdict": "KILLED", "tier": "KILLED", "kills": kills}

        if verdict_f14 == "SURVIVES":
            # Check if F21/F23 also survived
            extended_ok = True
            if "F21" in tests and tests["F21"]["verdict"] not in ("ROBUST", "NULL", "HIDDEN_STRUCTURE"):
                extended_ok = False
            if "F23" in tests and tests["F23"]["verdict"] == "POSSIBLE_CONFOUND":
                extended_ok = False

            if extended_ok:
                return {"verdict": "PROBABLE", "tier": "B+"}
            else:
                return {"verdict": "POSSIBLE", "tier": "A"}

        return {"verdict": "CONJECTURE", "tier": "unclassified"}


def print_result(result: dict, verbose: bool = True):
    """Pretty-print a battery result."""
    overall = result["overall"]
    print(f"\n{'='*60}")
    print(f"VERDICT: {overall['verdict']}  (tier: {overall.get('tier', '?')})")
    print(f"Samples: {result['n_samples']}")
    if overall.get("kills"):
        print(f"KILLED BY: {overall['kills']}")
    if overall.get("tier_c"):
        print(f"Diagnostics: {overall['tier_c']}")
    print(f"{'='*60}")

    if verbose:
        for tname, tdata in sorted(result["tests"].items()):
            if isinstance(tdata, dict):
                v = tdata.get("verdict", "?")
                # Compact one-liner per test
                detail_keys = [k for k in tdata if k not in ("verdict", "test")]
                details = ", ".join(f"{k}={_fmt(tdata[k])}" for k in detail_keys[:4])
                print(f"  {tname:6s}: {v:30s} {details}")


def _fmt(v):
    """Format a value compactly."""
    if isinstance(v, float):
        if abs(v) < 0.001 and v != 0:
            return f"{v:.2e}"
        return f"{v:.4f}"
    if isinstance(v, dict):
        return "{...}"
    if isinstance(v, (list, tuple)) and len(v) > 3:
        return f"[{len(v)} items]"
    return str(v)


if __name__ == "__main__":
    print("=== Unified Battery Self-Test ===\n")

    ub = UnifiedBattery()
    rng = np.random.default_rng(42)

    # Test 1: Distribution with known structure (log-normal)
    print("--- Test 1: Log-normal distribution (should detect log-normality) ---")
    lognormal_vals = rng.lognormal(mean=5, sigma=1.5, size=1000)
    r = ub.test_distribution(
        finding_id="SELF_TEST_1",
        claim="log-normal self-test",
        values=lognormal_vals,
        predicted_value=3.0,
        data_source="synthetic",
        domain_is_multiplicative=True,
    )
    print_result(r)

    # Test 2: Uniform distribution (should NOT be log-normal)
    print("\n--- Test 2: Uniform distribution (should deviate from log-normal) ---")
    uniform_vals = rng.uniform(1, 100, size=1000)
    r = ub.test_distribution(
        finding_id="SELF_TEST_2",
        claim="uniform self-test",
        values=uniform_vals,
        predicted_value=1.8,
        data_source="synthetic",
    )
    print_result(r)

    print("\n--- Self-test complete ---")
    ub.logger.summary()
