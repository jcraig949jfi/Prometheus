"""
Per-domain π₀ (false-conjecture base rate) estimation from the substrate's
existing pilot data.

Method: beta-binomial estimation (Storey q-value path requires per-claim
p-values which the current substrate does not yet expose at the rediscovery-
env level). Two priors reported: Uniform Beta(1,1) and Jeffreys Beta(0.5,0.5).
Bootstrap CIs over per-seed means + Wilson 95% CI on aggregated counts.

Charon canon:
- Caveat-as-metadata: every estimate ships with CI + n + interpretation tag.
- Calibrated negatives preferred: thin domains say so loudly.
- Falsification-first: distributional assumptions named with alternative-prior
  estimates.

Author: Charon, 2026-05-05
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from scipy import stats

REPO = Path("F:/Prometheus")
PILOTS = REPO / "prometheus_math"
OUT_DIR = REPO / "charon" / "diagnostics"


def wilson_ci(k: int, n: int, alpha: float = 0.05) -> Tuple[float, float]:
    """Wilson score interval for a binomial proportion."""
    if n == 0:
        return (0.0, 1.0)
    z = stats.norm.ppf(1 - alpha / 2)
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def beta_posterior(k: int, n: int, prior_a: float, prior_b: float) -> Tuple[float, Tuple[float, float]]:
    """Posterior mean + central 95% CI for a beta-binomial."""
    a = prior_a + k
    b = prior_b + (n - k)
    mean = a / (a + b)
    lo = stats.beta.ppf(0.025, a, b)
    hi = stats.beta.ppf(0.975, a, b)
    return mean, (lo, hi)


def bootstrap_ci_from_seed_means(
    seed_accuracies: List[float], n_per_seed: int, n_boot: int = 10000, rng_seed: int = 0
) -> Tuple[float, Tuple[float, float]]:
    """
    Bootstrap a 95% CI for π₀ from per-seed accuracies.

    Treats each seed's accuracy as the binomial p, samples n_per_seed Bernoulli
    trials from each (parametric bootstrap), aggregates seeds, returns
    (1 - mean_accuracy, percentile CI).
    """
    rng = np.random.default_rng(rng_seed)
    pi0_samples = np.empty(n_boot)
    for i in range(n_boot):
        # Resample seeds with replacement, then parametric bootstrap each
        sampled = rng.choice(seed_accuracies, size=len(seed_accuracies), replace=True)
        # Parametric Bernoulli draw per seed
        per_seed_p = np.array([rng.binomial(n_per_seed, s) / n_per_seed for s in sampled])
        pi0_samples[i] = 1 - per_seed_p.mean()
    mean = float(pi0_samples.mean())
    lo = float(np.percentile(pi0_samples, 2.5))
    hi = float(np.percentile(pi0_samples, 97.5))
    return mean, (lo, hi)


def interpret(pi0: float, ci_width: float, thin: bool, special: str = "") -> str:
    if special:
        return special
    if thin:
        return "thin_data"
    if ci_width > 0.5:
        return "undefined_thin_data"
    if pi0 >= 0.9:
        return "high"
    if pi0 >= 0.5:
        return "moderate"
    return "low"


# ---------------------------------------------------------------------------
# Per-domain raw inputs (extracted from pilot JSONs in earlier inspection step)
# ---------------------------------------------------------------------------


def load_pilot(filename: str) -> dict:
    return json.loads((PILOTS / filename).read_text())


def domain_from_binary_pilot(name: str, pilot_filename: str, train_size: int, test_size: int) -> dict:
    """
    Compute π₀ for a binary-reward (HIT=100/MISS=0) rediscovery domain from
    its pilot file. Uses the random arm to estimate the null-model error rate.
    """
    d = load_pilot(pilot_filename)
    n_seeds = d["n_seeds"]
    n_episodes = d["n_episodes"]
    random_means = d["random_means"]  # per-seed mean reward across n_episodes train

    # Convert per-seed mean reward to per-seed accuracy (HIT=100, MISS=0)
    per_seed_acc_train = [m / 100.0 for m in random_means]
    n_total_train = n_seeds * n_episodes

    # BSD pilot uses test_eval_random_means; modular/knot/genus2/OEIS/mock_theta use test_random_means
    test_random_means = d.get("test_random_means") or d.get("test_eval_random_means")
    per_seed_acc_test = None
    n_total_test = None
    if test_random_means is not None:
        per_seed_acc_test = [m / 100.0 for m in test_random_means]
        n_total_test = n_seeds * test_size

    # Aggregate counts (train, primary)
    k_correct_train = sum(int(round(a * n_episodes)) for a in per_seed_acc_train)
    k_wrong_train = n_total_train - k_correct_train

    # Aggregate counts (test, sanity)
    k_correct_test = None
    k_wrong_test = None
    if per_seed_acc_test is not None:
        k_correct_test = sum(int(round(a * test_size)) for a in per_seed_acc_test)
        k_wrong_test = n_total_test - k_correct_test

    # π₀ = wrong/total under null
    # Beta-binomial under two priors
    pi0_uniform_mean, pi0_uniform_ci = beta_posterior(k_wrong_train, n_total_train, 1.0, 1.0)
    pi0_jeffreys_mean, pi0_jeffreys_ci = beta_posterior(k_wrong_train, n_total_train, 0.5, 0.5)
    wilson_ci_train = wilson_ci(k_wrong_train, n_total_train)

    # Bootstrap CI from per-seed
    boot_mean, boot_ci = bootstrap_ci_from_seed_means(per_seed_acc_train, n_episodes)

    # Sanity check on test
    test_block = None
    if k_wrong_test is not None and n_total_test is not None:
        test_pi0_mean, test_pi0_ci = beta_posterior(k_wrong_test, n_total_test, 0.5, 0.5)
        test_block = {
            "n_records": n_total_test,
            "k_wrong": k_wrong_test,
            "pi0_jeffreys_mean": test_pi0_mean,
            "pi0_jeffreys_ci": list(test_pi0_ci),
        }

    ci_width = pi0_jeffreys_ci[1] - pi0_jeffreys_ci[0]
    thin = n_total_train < 200 or (n_total_test is not None and n_total_test < 50)
    interp = interpret(pi0_jeffreys_mean, ci_width, thin)

    return {
        "name": name,
        "data_source": str((PILOTS / pilot_filename).as_posix()),
        "method_arm": "random_uniform_policy",
        "scoring": "binary_HIT100_MISS0",
        "n_records_train": n_total_train,
        "n_records_test": n_total_test,
        "k_wrong_train": k_wrong_train,
        "k_correct_train": k_correct_train,
        "per_seed_accuracy_train": per_seed_acc_train,
        "per_seed_accuracy_test": per_seed_acc_test,
        "pi0_mean": pi0_jeffreys_mean,
        "pi0_ci": list(pi0_jeffreys_ci),
        "pi0_ci_width": ci_width,
        "pi0_uniform_prior_mean": pi0_uniform_mean,
        "pi0_uniform_prior_ci": list(pi0_uniform_ci),
        "pi0_wilson_ci": list(wilson_ci_train),
        "pi0_bootstrap_mean": boot_mean,
        "pi0_bootstrap_ci": list(boot_ci),
        "test_split_check": test_block,
        "interpretation": interp,
    }


def domain_oeis_sleeping() -> dict:
    """
    OEIS Sleeping has 3-valued reward (HIT=100, NEAR=25, MISS=0). Mean reward
    alone gives bounds, not a point estimate. Compute π₀ as fraction with
    pure MISS = 0, derived as a bound from mean reward.

    From mean_reward = 100·p_hit + 25·p_near + 0·p_miss with p_hit + p_near + p_miss = 1:
      max p_miss (= pi0_upper): set p_near=0; p_hit = mean/100; p_miss = 1 - mean/100
        (each unit of HIT gives most reward per unit of probability budget,
         so concentrating reward in HITs leaves most room for MISS)
      min p_miss (= pi0_lower): set p_hit=0; p_near = mean/25; p_miss = 1 - mean/25
        (concentrating reward in NEARs uses up the most probability budget,
         leaving least room for MISS)
    Both bounds are achievable point distributions; the true (p_hit, p_near, p_miss)
    lies somewhere on the line segment between them (parameterized by p_hit).
    """
    d = load_pilot("_oeis_sleeping_pilot.json")
    n_seeds = d["n_seeds"]
    n_episodes = d["n_episodes"]
    random_means = d["random_means"]
    test_random_means = d.get("test_random_means")
    train_size = d["train_size"]
    test_size = d["test_size"]

    n_total_train = n_seeds * n_episodes
    mean_random_reward_train = float(np.mean(random_means))

    # Bounds on p_miss (= π₀)
    pi0_upper_bound = 1.0 - mean_random_reward_train / 100.0  # max HITs, no NEAR
    pi0_lower_bound = max(0.0, 1.0 - mean_random_reward_train / 25.0)   # no HITs, all NEAR

    # On test split (sanity)
    test_block = None
    if test_random_means is not None:
        n_total_test = n_seeds * test_size
        mean_test = float(np.mean(test_random_means))
        test_pi0_hi = 1.0 - mean_test / 100.0
        test_pi0_lo = max(0.0, 1.0 - mean_test / 25.0)
        test_block = {
            "n_records": n_total_test,
            "mean_reward": mean_test,
            "pi0_lower_bound": test_pi0_lo,
            "pi0_upper_bound": test_pi0_hi,
        }

    return {
        "name": "OEIS_sleeping",
        "data_source": str((PILOTS / "_oeis_sleeping_pilot.json").as_posix()),
        "method_arm": "random_uniform_policy",
        "scoring": "ternary_HIT100_NEAR25_MISS0",
        "n_records_train": n_total_train,
        "n_records_test": n_seeds * test_size if test_random_means else None,
        "mean_random_reward_train": mean_random_reward_train,
        "pi0_lower_bound": pi0_lower_bound,
        "pi0_upper_bound": pi0_upper_bound,
        "pi0_mean": (pi0_lower_bound + pi0_upper_bound) / 2,
        "pi0_ci": [pi0_lower_bound, pi0_upper_bound],
        "pi0_ci_width": pi0_upper_bound - pi0_lower_bound,
        "test_split_check": test_block,
        "interpretation": "high_with_bounds",
        "honesty_note": (
            "Ternary reward: cannot derive a point estimate of π₀ from mean "
            "reward alone. Bounds reported. To convert to a point estimate, "
            "the env would need to log per-prediction outcome (HIT|NEAR|MISS) "
            "rather than aggregate mean reward."
        ),
    }


def domain_lehmer_discovery() -> dict:
    """
    Lehmer/Mahler discovery domain. Direct π₀ estimate from four-counts pilot
    using the random_null arm: # promotes / # episodes.

    This is the only domain where the substrate currently exposes a proper
    kill stream (per-episode kill_pattern + promote/reject).
    """
    d = json.load(open(PILOTS / "four_counts_pilot_run_10k.json"))
    arm = d["per_condition"]["random_null"]
    n_episodes_total = sum(10000 for _ in arm["per_seed_counts"])
    n_promote = sum(s["promote"] for s in arm["per_seed_counts"])
    n_rejected = sum(s["rejected"] for s in arm["per_seed_counts"])
    n_catalog_hit = sum(s["catalog_hit"] for s in arm["per_seed_counts"])
    by_kill_pattern = arm["by_kill_pattern"]

    # π₀ = fraction of CLAIMs (= proposed polynomials) that are killed
    # 0 promotes from 30000 random episodes
    k_kill = n_rejected
    n = n_episodes_total

    pi0_uniform, ci_uniform = beta_posterior(k_kill, n, 1.0, 1.0)
    pi0_jeff, ci_jeff = beta_posterior(k_kill, n, 0.5, 0.5)
    wilson = wilson_ci(k_kill, n)

    # Promote rate — confidence we're not missing something
    p_promote_uniform, ci_p_uniform = beta_posterior(n_promote, n, 1.0, 1.0)
    p_promote_jeff, ci_p_jeff = beta_posterior(n_promote, n, 0.5, 0.5)

    # Rule-of-three upper bound (one-sided 95%)
    rule_of_three_upper = 3 / n if n_promote == 0 else None

    # Compare against REINFORCE arm
    arm_r = d["per_condition"]["reinforce_agent"]
    n_eps_r = sum(10000 for _ in arm_r["per_seed_counts"])
    n_promote_r = sum(s["promote"] for s in arm_r["per_seed_counts"])
    n_rejected_r = sum(s["rejected"] for s in arm_r["per_seed_counts"])
    pi0_jeff_r, ci_jeff_r = beta_posterior(n_rejected_r, n_eps_r, 0.5, 0.5)

    return {
        "name": "Lehmer_Mahler_discovery",
        "data_source": str((PILOTS / "four_counts_pilot_run_10k.json").as_posix()),
        "method_arm": "random_null",
        "scoring": "promote_vs_reject_via_battery",
        "n_records": n,
        "n_promote": n_promote,
        "n_rejected": n_rejected,
        "n_catalog_hit": n_catalog_hit,
        "by_kill_pattern": by_kill_pattern,
        "pi0_mean": pi0_jeff,
        "pi0_ci": list(ci_jeff),
        "pi0_ci_width": ci_jeff[1] - ci_jeff[0],
        "pi0_uniform_prior_mean": pi0_uniform,
        "pi0_uniform_prior_ci": list(ci_uniform),
        "pi0_wilson_ci": list(wilson),
        "promote_rate_mean": p_promote_jeff,
        "promote_rate_ci": list(ci_p_jeff),
        "promote_rate_rule_of_three_upper_95": rule_of_three_upper,
        "reinforce_arm_pi0_mean": pi0_jeff_r,
        "reinforce_arm_pi0_ci": list(ci_jeff_r),
        "reinforce_arm_n_promote": n_promote_r,
        "reinforce_arm_n_episodes": n_eps_r,
        "interpretation": "near_unity",
        "operational_note": (
            "0 promotes in 60000 episodes (random + REINFORCE). π₀ is "
            "essentially 1.0 with very tight CI. Consistent with Lehmer's "
            "conjecture: the domain may genuinely contain no sub-Lehmer "
            "non-cyclotomic polynomials, in which case π₀=1 is a structural "
            "property, not a finding about substrate competence."
        ),
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    domains = [
        domain_from_binary_pilot("BSD_rank", "_bsd_rank_pilot_run.json", 700, 300),
        domain_from_binary_pilot("modular_form", "_modular_form_pilot.json", 700, 300),
        domain_from_binary_pilot("knot_trace_field", "_knot_pilot.json", 34, 14),
        domain_from_binary_pilot("genus2", "_genus2_pilot.json", 1400, 600),
        domain_oeis_sleeping(),
        domain_from_binary_pilot("mock_theta", "_mock_theta_pilot.json", 31, 13),
        domain_lehmer_discovery(),
    ]
    out = {
        "computed_date": "2026-05-05",
        "computed_by": "Charon (instantiated for π₀ calibration task)",
        "data_sources": [d.get("data_source") for d in domains],
        "method": "beta_binomial",
        "method_rationale": (
            "Per-claim p-values are not exposed by the current cross-domain "
            "rediscovery envs (each pilot reports one experiment-level p-value, "
            "not per-prediction p-values). Storey's q-value approach therefore "
            "cannot be applied. Beta-binomial estimation per domain on the "
            "random_null arm gives the proportion of test items that fail the "
            "ground-truth check under a no-signal generator — the substrate-"
            "relevant proxy for π₀."
        ),
        "priors": {
            "primary": "Jeffreys Beta(0.5, 0.5)",
            "alternative": "Uniform Beta(1, 1)",
        },
        "ci_methods": ["beta_posterior_central_95", "wilson_score", "parametric_bootstrap"],
        "per_domain": {d["name"]: d for d in domains},
        "operational_implications": (
            "π₀ acts as the per-domain weight on PROMOTE confidence: "
            "PROMOTE in a high-π₀ domain (most candidates would be wrong "
            "under null) is strong evidence; PROMOTE in a low-π₀ domain "
            "is weaker. From these estimates: knot_trace_field and "
            "mock_theta have very high π₀ (>0.95) but THIN test sets — "
            "promotes there are individually noisy. modular_form and "
            "Lehmer_Mahler_discovery have π₀ near unity with dense data — "
            "any PROMOTE survivor is high-evidence. BSD_rank and genus2 "
            "have moderate π₀ (~0.7-0.8); a PROMOTE there is meaningful "
            "but weaker than in the harder domains. OEIS_sleeping reports "
            "bounds only (ternary reward); resolution requires logging "
            "per-prediction outcome rather than mean reward."
        ),
        "honesty_notes": [
            "The π₀ computed here is NOT Storey's strict null-proportion "
            "in a multi-test family. It is the population error rate of "
            "the random null model per domain — an upper bound on substrate "
            "claim-stream π₀ under the assumption that every wrong-under-null "
            "prediction maps to a substrate CLAIM.",
            "The substrate's actual CLAIM stream is filtered (the substrate "
            "does not promote every prediction); true substrate π₀ is "
            "therefore ≤ these estimates. The estimates here are best read "
            "as 'what π₀ would be if the substrate claimed indiscriminately.'",
            "All cross-domain rediscovery pilots use n_seeds=3. Bootstrap "
            "CIs over only 3 seeds are loose. Wilson and beta-posterior CIs "
            "on aggregated counts are tighter but assume i.i.d. predictions, "
            "which holds within a seed but not strictly across seeds.",
            "OEIS_sleeping ternary reward (HIT/NEAR/MISS) prevents point "
            "estimation from mean reward alone. Bounds reported. To convert "
            "to a point estimate, the env must log per-prediction outcome.",
            "Lehmer_Mahler_discovery has 0 promotes in 60000 episodes. "
            "π₀≈1.0 may be a substrate competence claim OR a structural "
            "property of Lehmer's conjecture. Cannot distinguish from the "
            "current data; flagged in operational_note for that domain.",
            "Thin domains (knot=42 test, mock_theta=39 test, oeis_sleeping=150 test): "
            "Wilson CIs are wide. Reported ci_width to be visible.",
            "Method choice (beta-binomial vs Storey) is data-availability "
            "driven, not preference. If/when the substrate begins logging "
            "per-claim p-values from F1/F6/F9/F11 battery tests, recompute "
            "with Storey for tighter and more interpretable estimates.",
        ],
    }
    out_path = OUT_DIR / "per_domain_pi0.json"
    out_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"Wrote {out_path}")

    # Print summary table (ASCII-safe for cp1252 Windows consoles)
    print("\n=== Per-domain pi0 summary ===")
    print(f"{'domain':30s} {'n':>6s} {'pi0':>8s} {'ci_width':>10s} {'interp':>20s}")
    for name, d in out["per_domain"].items():
        n = d.get("n_records") or d.get("n_records_train") or "?"
        pi0 = d.get("pi0_mean", "?")
        cw = d.get("pi0_ci_width", "?")
        interp = d.get("interpretation", "?")
        if isinstance(pi0, float):
            pi0_s = f"{pi0:.4f}"
        else:
            pi0_s = str(pi0)
        if isinstance(cw, float):
            cw_s = f"{cw:.4f}"
        else:
            cw_s = str(cw)
        print(f"{name:30s} {str(n):>6s} {pi0_s:>8s} {cw_s:>10s} {interp:>20s}")


if __name__ == "__main__":
    main()
