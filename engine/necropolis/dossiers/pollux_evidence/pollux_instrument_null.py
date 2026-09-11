"""Pollux instrument nulls: the tests that were prescribed twice and never run.

pivot/COMPONENT_DOSSIERS_2026-06-24.md (### Pollux, "Suggested settle
condition") and charon/CHARON_SESSION_2026-08-12.md ("write the script that
computes Pollux's statistic on sorted and on shuffled inputs and print both")
both prescribe executable checks on the instrument. Neither was ever recorded
as executed. This script executes them, offline, with the daemon's own
functions, and writes pollux_instrument_null_result.json.

  T1  Identity: Spearman(sorted(a), sorted(b)) == 1.0 for ANY a, b (random
      draws), so the daemon's corr_raw cannot observe the data.
  T2  The 08-12 prescription: the daemon's statistic on the real pairs with
      inputs in DB order, shuffled order, and reversed order. Because
      run_tick sorts internally, all orders give corr_raw = 1.0. The
      non-sorted "raw" Spearman (pairing by DB index) is reported as what a
      non-tautological raw leg would have looked like.
  T3  Label-permutation null for corr_norm on each real pair: pool A u B,
      shuffle labels, split to (n_a, n_b), run the exact pipeline. Fraction
      of null draws landing in PROMOTED / REJECTED / UNVERIFIED and a
      two-sided p for the observed corr_norm. (The random-pairing null the
      06-24 dossier asked for.)
  T4  Independent-samples null: two INDEPENDENT samples of sizes (n_a, n_b)
      from one smooth density (exponential, shifted to start at 1) and from
      the uniform. If independent draws routinely produce PROMOTED, the
      "survives" pattern measures a shared monotone density trend, not a
      coincidence between the two subsets.
  T5  Truncation sensitivity: the daemon keeps the n SMALLEST values of the
      larger subset. Replace that with a random size-n subsample of the
      larger subset and see whether the verdict is stable.
"""
from __future__ import annotations

import importlib.util
import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
DAEMON = REPO_ROOT / "charon" / "agents" / "pollux" / "daemon.py"
OUT = HERE / "pollux_instrument_null_result.json"
sys.path.insert(0, str(REPO_ROOT))

N_NULL = 1000
SEED = 20260911


def load_daemon():
    spec = importlib.util.spec_from_file_location("pollux_daemon", DAEMON)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def pipeline(d, a_vals, b_vals, truncate="smallest", rng=None):
    """The exact run_tick arithmetic. truncate='smallest' is the daemon's
    rule; 'random' is the T5 alternative."""
    n = min(len(a_vals), len(b_vals))
    if truncate == "smallest":
        a_p = sorted(a_vals)[:n]
        b_p = sorted(b_vals)[:n]
    else:
        a_p = sorted(rng.sample(a_vals, n)) if len(a_vals) > n else sorted(a_vals)
        b_p = sorted(rng.sample(b_vals, n)) if len(b_vals) > n else sorted(b_vals)
    corr_raw = d._spearman(a_p, b_p)
    a_n = d._mean_spacing_normalize(a_p)
    b_n = d._mean_spacing_normalize(b_p)
    m = min(len(a_n), len(b_n))
    corr_norm = d._spearman(a_n[:m], b_n[:m]) if m >= 10 else None
    kp = d._classify(corr_raw, corr_norm)
    return corr_raw, corr_norm, kp


def verdict_of(kp):
    if kp == "pollux_correlation_survives_normalization":
        return "PROMOTED"
    if kp in ("pollux_sign_flips_under_normalization", "pollux_no_correlation_observed"):
        return "REJECTED"
    return "UNVERIFIED"


def quantiles(xs, qs=(0.025, 0.5, 0.975)):
    s = sorted(x for x in xs if x is not None)
    if not s:
        return {}
    return {str(q): s[min(len(s) - 1, int(q * len(s)))] for q in qs}


def t1_identity(d, rng):
    max_dev = 0.0
    shuffled_corrs = []
    for _ in range(N_NULL):
        n = rng.randint(10, 120)
        a = [rng.lognormvariate(0, 1) for _ in range(n)]
        b = [rng.expovariate(1.0) for _ in range(n)]
        c = d._spearman(sorted(a), sorted(b))
        max_dev = max(max_dev, abs(c - 1.0))
        shuffled_corrs.append(d._spearman(a, b))
    return {
        "draws": N_NULL,
        "spearman_sorted_sorted_max_abs_dev_from_1": max_dev,
        "spearman_unsorted_independent_mean": sum(shuffled_corrs) / len(shuffled_corrs),
        "spearman_unsorted_independent_quantiles": quantiles(shuffled_corrs),
        "conclusion": "corr_raw is a function of the sort, not of the data",
    }


def t2_prescription(d, pairs, rng):
    rows = []
    for p in pairs:
        a_vals, _ = d._load_subset(p["a"])
        b_vals, _ = d._load_subset(p["b"])
        if not a_vals or not b_vals:
            rows.append({"pair": p["name"], "error": "subset_load_failed"})
            continue
        n = min(len(a_vals), len(b_vals))
        as_db = list(a_vals)
        bs_db = list(b_vals)
        a_sh = list(a_vals); rng.shuffle(a_sh)
        b_sh = list(b_vals); rng.shuffle(b_sh)
        out = {"pair": p["name"], "n_paired": n}
        # What run_tick does (sorts internally) on each input ordering:
        out["daemon_corr_raw_db_order"] = round(pipeline(d, as_db, bs_db)[0], 6)
        out["daemon_corr_raw_shuffled"] = round(pipeline(d, a_sh, b_sh)[0], 6)
        out["daemon_corr_raw_reversed"] = round(pipeline(d, as_db[::-1], bs_db[::-1])[0], 6)
        # What a non-sorting raw leg would have said (pair by DB index):
        out["nonsorted_spearman_db_index_pairing"] = d._spearman(as_db[:n], bs_db[:n])
        out["nonsorted_spearman_shuffled_pairing"] = d._spearman(a_sh[:n], b_sh[:n])
        rows.append(out)
    return rows


def t3_label_permutation(d, pairs, rng):
    rows = []
    for p in pairs:
        a_vals, _ = d._load_subset(p["a"])
        b_vals, _ = d._load_subset(p["b"])
        if not a_vals or not b_vals:
            rows.append({"pair": p["name"], "error": "subset_load_failed"})
            continue
        obs_raw, obs_norm, obs_kp = pipeline(d, a_vals, b_vals)
        pool = list(a_vals) + list(b_vals)
        na = len(a_vals)
        # Cap the pool size for the two pairs with 8k-element subsets:
        # the daemon itself only ever looks at the n smallest of the big
        # set, but a label-permutation null must permute the whole pool.
        null_norm = []
        null_v = {"PROMOTED": 0, "REJECTED": 0, "UNVERIFIED": 0}
        for _ in range(N_NULL):
            rng.shuffle(pool)
            a_n, b_n = pool[:na], pool[na:]
            _, cn, kp = pipeline(d, a_n, b_n)
            null_norm.append(cn)
            null_v[verdict_of(kp)] += 1
        valid = [x for x in null_norm if x is not None]
        p_two = None
        if obs_norm is not None and valid:
            p_two = sum(1 for x in valid if abs(x) >= abs(obs_norm)) / len(valid)
        rows.append({
            "pair": p["name"], "n_a": na, "n_b": len(b_vals),
            "observed_corr_norm": obs_norm, "observed_verdict": verdict_of(obs_kp),
            "null_draws": N_NULL,
            "null_corr_norm_quantiles": quantiles(null_norm),
            "null_verdict_fractions": {k: v / N_NULL for k, v in null_v.items()},
            "p_two_sided_abs": p_two,
            "observed_survives_null_at_0.05": (p_two is not None and p_two < 0.05),
        })
    return rows


def t4_independent_samples(d, sizes, rng):
    rows = []
    for (na, nb) in sizes:
        for dist in ("exponential_shift1", "uniform_1_2"):
            v = {"PROMOTED": 0, "REJECTED": 0, "UNVERIFIED": 0}
            norms = []
            for _ in range(N_NULL):
                if dist == "exponential_shift1":
                    a = [1.0 + rng.expovariate(1.0) for _ in range(na)]
                    b = [1.0 + rng.expovariate(1.0) for _ in range(nb)]
                else:
                    a = [rng.uniform(1.0, 2.0) for _ in range(na)]
                    b = [rng.uniform(1.0, 2.0) for _ in range(nb)]
                _, cn, kp = pipeline(d, a, b)
                norms.append(cn)
                v[verdict_of(kp)] += 1
            rows.append({
                "n_a": na, "n_b": nb, "distribution": dist,
                "independent_draws": N_NULL,
                "corr_norm_quantiles": quantiles(norms),
                "verdict_fractions": {k: x / N_NULL for k, x in v.items()},
            })
    return rows


def t5_truncation(d, pairs, rng):
    rows = []
    for p in pairs:
        a_vals, _ = d._load_subset(p["a"])
        b_vals, _ = d._load_subset(p["b"])
        if not a_vals or not b_vals or len(a_vals) == len(b_vals):
            continue
        _, obs_norm, obs_kp = pipeline(d, a_vals, b_vals)
        v = {"PROMOTED": 0, "REJECTED": 0, "UNVERIFIED": 0}
        norms = []
        for _ in range(200):
            _, cn, kp = pipeline(d, a_vals, b_vals, truncate="random", rng=rng)
            norms.append(cn)
            v[verdict_of(kp)] += 1
        rows.append({
            "pair": p["name"], "n_a": len(a_vals), "n_b": len(b_vals),
            "daemon_rule_smallest_n": {"corr_norm": obs_norm, "verdict": verdict_of(obs_kp)},
            "random_subsample_n_draws": 200,
            "random_subsample_verdict_fractions": {k: x / 200 for k, x in v.items()},
            "random_subsample_corr_norm_quantiles": quantiles(norms),
            "verdict_stable_under_subsample_rule": v[verdict_of(obs_kp)] / 200,
        })
    return rows


def main():
    rng = random.Random(SEED)
    result = {"script": "pollux_instrument_null.py", "seed": SEED, "n_null": N_NULL}
    try:
        d = load_daemon()
    except Exception as e:
        result["daemon_import"] = "FAILED: %s: %s" % (type(e).__name__, e)
        OUT.write_text(json.dumps(result, indent=1) + "\n", encoding="ascii")
        print(json.dumps(result, indent=1))
        return
    pairs = list(d.SEED_PAIRS) + list(d.CANDIDATE_POOL)
    result["T1_identity"] = t1_identity(d, rng)
    result["T2_prescription_sorted_vs_shuffled"] = t2_prescription(d, pairs, rng)
    result["T3_label_permutation_null"] = t3_label_permutation(d, pairs, rng)
    sizes = sorted({(min(r["n_a"], r["n_b"]), max(r["n_a"], r["n_b"]))
                    for r in result["T3_label_permutation_null"] if "n_a" in r})
    # cap the giant subsets for T4: the daemon only ever sees min(n) values anyway
    sizes = [(a, min(b, 2 * a)) for (a, b) in sizes]
    result["T4_independent_samples_null"] = t4_independent_samples(d, sizes, rng)
    result["T5_truncation_sensitivity"] = t5_truncation(d, pairs, rng)
    # Summary lines the dossier cites verbatim
    t3 = [r for r in result["T3_label_permutation_null"] if "p_two_sided_abs" in r]
    result["summary"] = {
        "T1_sorted_sorted_is_identically_1": result["T1_identity"]["spearman_sorted_sorted_max_abs_dev_from_1"] < 1e-9,
        "T2_all_orderings_give_corr_raw_1": all(
            r.get("daemon_corr_raw_db_order") == 1.0 and r.get("daemon_corr_raw_shuffled") == 1.0
            for r in result["T2_prescription_sorted_vs_shuffled"] if "error" not in r),
        "T3_pairs_surviving_label_permutation_at_0.05": [r["pair"] for r in t3 if r["observed_survives_null_at_0.05"]],
        "T3_pairs_not_surviving": [r["pair"] for r in t3 if not r["observed_survives_null_at_0.05"]],
        "T3_PROMOTED_pairs_and_their_p": {r["pair"]: r["p_two_sided_abs"] for r in t3 if r["observed_verdict"] == "PROMOTED"},
        "T4_max_PROMOTED_fraction_under_independence": max(
            r["verdict_fractions"]["PROMOTED"] for r in result["T4_independent_samples_null"]),
        "T4_PROMOTED_fraction_by_case": {
            "%d_%d_%s" % (r["n_a"], r["n_b"], r["distribution"]): r["verdict_fractions"]["PROMOTED"]
            for r in result["T4_independent_samples_null"]},
        "T5_min_verdict_stability": min(
            (r["verdict_stable_under_subsample_rule"] for r in result["T5_truncation_sensitivity"]), default=None),
    }
    OUT.write_text(json.dumps(result, indent=1) + "\n", encoding="ascii")
    print(json.dumps(result["summary"], indent=1))
    print(json.dumps(result["T1_identity"], indent=1))


if __name__ == "__main__":
    main()
