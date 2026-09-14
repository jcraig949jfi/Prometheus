#!/usr/bin/env python3
"""
Cleric chance floor for the Pollux verdict on the REAL Mahler data
(Rhadamanthus trial, 2026-09-11). Answers the brief's pressure point (d):
T4 in pollux_instrument_null.py bracketed the PROMOTED chance floor with
assumed marginals (exponential, uniform); this computes it on the tree's
own subsets, through the daemon's own arithmetic, with three nulls that
each destroy a different thing the design might have meant by "shared
spacing profile":

  N1 own_marginals   A* ~ smoothed bootstrap of A, B* ~ smoothed bootstrap
                     of B, independent. Keeps both marginal shapes, destroys
                     any relation between the two SAMPLES. If PROMOTED is
                     common here, the verdict is a property of the two
                     densities, not of a coincidence between the sets.
  N2 same_density    A* and B* both drawn from A's smoothed marginal (and,
                     separately, both from B's). No pairing, no second
                     population: the PROMOTED rate here is the floor for
                     "two samples of one density".
  N3 pooled          A* and B* both drawn from the smoothed pooled marginal
                     (the smoothed analogue of the Necromancer's T3 label
                     permutation).

Also D: the T3 label-permutation null re-run with a SIGNED one-sided p
(fraction of null corr_norm >= observed), because PROMOTED can only be
reached from the positive side and the Necromancer reported |null| >= |obs|.

Smoothed bootstrap = interpolated empirical quantile function: u ~ U(0,1),
value = linear interpolation between the sorted sample's order statistics.
Every replicate is pushed through the exact run_tick arithmetic (sorted
n-smallest truncation, _mean_spacing_normalize, _spearman, _classify).

Output: cleric_chance_floor_result.json, written from Python and flushed
after every pair. No network, no database.
"""
import importlib.util
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
OUT = HERE / "cleric_chance_floor_result.json"
sys.path.insert(0, str(REPO_ROOT))
DAEMON = REPO_ROOT / "charon" / "agents" / "pollux" / "daemon.py"

N_NULL = 1000
SEED = 20260911


def load_daemon():
    spec = importlib.util.spec_from_file_location("pollux_daemon", DAEMON)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def pipeline(d, a_vals, b_vals):
    """Exact run_tick arithmetic (copied from daemon.run_tick)."""
    n = min(len(a_vals), len(b_vals))
    a_p = sorted(a_vals)[:n]
    b_p = sorted(b_vals)[:n]
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


def smoothed_sampler(values):
    s = sorted(values)
    m = len(s)

    def draw(rng, k):
        out = []
        for _ in range(k):
            u = rng.random() * (m - 1)
            i = int(u)
            f = u - i
            if i >= m - 1:
                out.append(s[-1])
            else:
                out.append(s[i] + f * (s[i + 1] - s[i]))
        return out
    return draw


def quantiles(xs, qs=(0.025, 0.5, 0.975)):
    s = sorted(x for x in xs if x is not None)
    if not s:
        return {}
    return {str(q): round(s[min(len(s) - 1, int(q * len(s)))], 4) for q in qs}


def run_null(d, rng, draw_a, draw_b, n_a, n_b, obs_norm):
    norms = []
    verdicts = {"PROMOTED": 0, "REJECTED": 0, "UNVERIFIED": 0}
    for _ in range(N_NULL):
        a = draw_a(rng, n_a)
        b = draw_b(rng, n_b)
        _, cn, kp = pipeline(d, a, b)
        norms.append(cn)
        verdicts[verdict_of(kp)] += 1
    valid = [x for x in norms if x is not None]
    out = {
        "verdict_fractions": {k: v / N_NULL for k, v in verdicts.items()},
        "corr_norm_quantiles": quantiles(valid),
        "corr_norm_mean": round(sum(valid) / len(valid), 4) if valid else None,
    }
    if obs_norm is not None and valid:
        out["p_one_sided_ge_obs"] = sum(1 for x in valid if x >= obs_norm) / len(valid)
        out["p_two_sided_abs"] = sum(1 for x in valid if abs(x) >= abs(obs_norm)) / len(valid)
    return out


def label_permutation_signed(d, rng, a_vals, b_vals, obs_norm):
    pool = list(a_vals) + list(b_vals)
    n_a, n_b = len(a_vals), len(b_vals)
    norms = []
    prom = 0
    for _ in range(N_NULL):
        rng.shuffle(pool)
        _, cn, kp = pipeline(d, pool[:n_a], pool[n_a:n_a + n_b])
        norms.append(cn)
        prom += verdict_of(kp) == "PROMOTED"
    valid = [x for x in norms if x is not None]
    return {
        "p_one_sided_ge_obs": sum(1 for x in valid if x >= obs_norm) / len(valid) if valid else None,
        "p_two_sided_abs": sum(1 for x in valid if abs(x) >= abs(obs_norm)) / len(valid) if valid else None,
        "PROMOTED_fraction": prom / N_NULL,
        "corr_norm_quantiles": quantiles(valid),
    }


def main():
    rng = random.Random(SEED)
    result = {"script": "cleric_chance_floor.py", "seed": SEED, "n_null": N_NULL, "pairs": []}
    try:
        d = load_daemon()
    except Exception as e:
        result["daemon_import"] = "FAILED: %s: %s" % (type(e).__name__, e)
        OUT.write_text(json.dumps(result, indent=1) + "\n", encoding="ascii")
        return
    pairs = list(d.SEED_PAIRS) + list(d.CANDIDATE_POOL)
    for p in pairs:
        a_vals, a_desc = d._load_subset(p["a"])
        b_vals, b_desc = d._load_subset(p["b"])
        row = {"pair": p["name"], "n_a": len(a_vals), "n_b": len(b_vals)}
        if not a_vals or not b_vals:
            row["error"] = "subset_load_failed"
            result["pairs"].append(row)
            OUT.write_text(json.dumps(result, indent=1) + "\n", encoding="ascii")
            continue
        _, obs_norm, kp = pipeline(d, a_vals, b_vals)
        row["observed"] = {"corr_norm": round(obs_norm, 4) if obs_norm is not None else None,
                           "kill_pattern": kp, "verdict": verdict_of(kp)}
        draw_a = smoothed_sampler(a_vals)
        draw_b = smoothed_sampler(b_vals)
        draw_pool = smoothed_sampler(list(a_vals) + list(b_vals))
        row["N1_own_marginals_independent"] = run_null(d, rng, draw_a, draw_b, len(a_vals), len(b_vals), obs_norm)
        row["N2_same_density_A"] = run_null(d, rng, draw_a, draw_a, len(a_vals), len(b_vals), obs_norm)
        row["N2_same_density_B"] = run_null(d, rng, draw_b, draw_b, len(a_vals), len(b_vals), obs_norm)
        row["N3_pooled_smoothed"] = run_null(d, rng, draw_pool, draw_pool, len(a_vals), len(b_vals), obs_norm)
        row["D_label_permutation_signed"] = label_permutation_signed(d, rng, a_vals, b_vals, obs_norm)
        result["pairs"].append(row)
        OUT.write_text(json.dumps(result, indent=1) + "\n", encoding="ascii")
        print(json.dumps({"pair": p["name"], "obs": row["observed"],
                          "N1_PROMOTED": row["N1_own_marginals_independent"]["verdict_fractions"]["PROMOTED"],
                          "N1_p_ge": row["N1_own_marginals_independent"].get("p_one_sided_ge_obs"),
                          "N2A_PROMOTED": row["N2_same_density_A"]["verdict_fractions"]["PROMOTED"],
                          "N2B_PROMOTED": row["N2_same_density_B"]["verdict_fractions"]["PROMOTED"],
                          "N3_PROMOTED": row["N3_pooled_smoothed"]["verdict_fractions"]["PROMOTED"],
                          "D_p_signed": row["D_label_permutation_signed"]["p_one_sided_ge_obs"]}))
    ok = [r for r in result["pairs"] if "observed" in r]
    result["summary"] = {
        "PROMOTED_chance_floor_N1_by_pair": {r["pair"]: r["N1_own_marginals_independent"]["verdict_fractions"]["PROMOTED"] for r in ok},
        "PROMOTED_chance_floor_N2_max_by_pair": {r["pair"]: max(r["N2_same_density_A"]["verdict_fractions"]["PROMOTED"],
                                                                 r["N2_same_density_B"]["verdict_fractions"]["PROMOTED"]) for r in ok},
        "PROMOTED_chance_floor_N3_by_pair": {r["pair"]: r["N3_pooled_smoothed"]["verdict_fractions"]["PROMOTED"] for r in ok},
        "observed_PROMOTED_pairs": [r["pair"] for r in ok if r["observed"]["verdict"] == "PROMOTED"],
        "N1_p_one_sided_for_PROMOTED_pairs": {r["pair"]: r["N1_own_marginals_independent"].get("p_one_sided_ge_obs")
                                              for r in ok if r["observed"]["verdict"] == "PROMOTED"},
        "D_signed_p_for_PROMOTED_pairs": {r["pair"]: r["D_label_permutation_signed"]["p_one_sided_ge_obs"]
                                          for r in ok if r["observed"]["verdict"] == "PROMOTED"},
        "max_PROMOTED_floor_any_null_any_pair": max(
            [r["N1_own_marginals_independent"]["verdict_fractions"]["PROMOTED"] for r in ok] +
            [r["N2_same_density_A"]["verdict_fractions"]["PROMOTED"] for r in ok] +
            [r["N2_same_density_B"]["verdict_fractions"]["PROMOTED"] for r in ok] +
            [r["N3_pooled_smoothed"]["verdict_fractions"]["PROMOTED"] for r in ok]),
    }
    OUT.write_text(json.dumps(result, indent=1) + "\n", encoding="ascii")
    print(json.dumps(result["summary"], indent=1))


if __name__ == "__main__":
    main()
