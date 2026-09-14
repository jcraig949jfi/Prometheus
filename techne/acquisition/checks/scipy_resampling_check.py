"""Does scipy.stats.permutation_test reproduce the tree's hand-rolled permutation null?

    python -m techne.acquisition.checks.scipy_resampling_check

WHY THIS CHECK EXISTS (donor-foundry criterion 2: home-grown code duplicating mature
machinery). A census on 2026-09-11 (`git grep`) finds 124 hand-rolled permutation /
bootstrap / shuffle-null definitions across 111 tracked files, against 22 files that call
scipy's `permutation_test` or `bootstrap` -- with scipy 1.17.1 already installed. The
reference home-grown implementation is cartography/shared/scripts/falsification_battery.py
`f1_permutation_null` (two-sample mean difference, label shuffle, p = (k+1)/(n+1)).

WHAT THIS ESTABLISHES, and only this: on the SAME fixtures, scipy's independent-sample
permutation test and the home-grown F1 return p-values that agree within Monte-Carlo error,
both detect a planted effect (POSITIVE), neither hallucinates one on exchangeable data
(NEGATIVE), and the harness itself notices an implementation that ignores its labels
(CHEAT). It does NOT say any null in the tree should be replaced -- which null a campaign
uses is the campaign's scientific logic and belongs to its owner; the receipt is the
evidence a seat can cite instead of rewriting a resampling loop.

Stage: ADAPTER_QUALIFICATION (no adapter is written; the donor is called directly, which is
the point -- the tree already consumes scipy directly and needs no Techne wrapper here).
"""
from __future__ import annotations

import sys

import numpy as np
from scipy import stats

from .. import receipt


def f1_home(values_a, values_b, n_perm=2000, seed=42) -> float:
    """Verbatim logic of cartography/shared/scripts/falsification_battery.f1_permutation_null,
    reduced to its p-value; kept here rather than imported so the check does not depend on
    a cartography module's import side effects."""
    observed = abs(np.mean(values_a) - np.mean(values_b))
    combined = np.concatenate([values_a, values_b])
    n_a = len(values_a)
    rng = np.random.RandomState(seed)
    k = 0
    for _ in range(n_perm):
        rng.shuffle(combined)
        if abs(np.mean(combined[:n_a]) - np.mean(combined[n_a:])) >= observed:
            k += 1
    return (k + 1) / (n_perm + 1)


def f1_scipy(values_a, values_b, n_perm=2000, seed=42) -> float:
    res = stats.permutation_test(
        (values_a, values_b), lambda a, b, axis=0: np.abs(np.mean(a, axis=axis) - np.mean(b, axis=axis)),
        permutation_type="independent", vectorized=True, n_resamples=n_perm,
        alternative="greater", random_state=seed)
    return float(res.pvalue)


def cheat_ignores_labels(values_a, values_b, n_perm=2000, seed=42) -> float:
    """A wrong implementation: the statistic never looks at the split, so the observed value
    equals every permuted value and p is always ~1. The harness must flag it."""
    return 1.0


def mc_se(p, n):
    return float(np.sqrt(max(p * (1 - p), 1e-12) / n))


def run(n_fixtures=40, n_perm=2000, n=30):
    rec = receipt.new("ADAPTER_QUALIFICATION", "scipy_resampling", tool="scipy")
    rec["design_version"] = "1.0"
    rec["observations"]["scipy_version"] = __import__("scipy").__version__
    rec["observations"]["reference_implementation"] = (
        "cartography/shared/scripts/falsification_battery.py::f1_permutation_null (verbatim p-value logic)")
    rec["observations"]["census_2026-09-11"] = {
        "hand_rolled_permutation_bootstrap_defs": 124, "files": 111,
        "files_calling_scipy_permutation_test_or_bootstrap": 22,
        "method": "git grep -c -P 'def\\s+\\w*(permut|bootstrap|shuffle_null|null_dist)\\w*\\s*\\(' -- '*.py' (non-test)"}
    rng = np.random.default_rng(20260911)

    # POSITIVE: planted shift of 1.5 sd, n=30 per arm -- power at alpha 0.01 is ~0.999, so
    # the attainable count is n_fixtures and the gate is reachable. FIRST RUN (receipt
    # ...20260912T010316Z) planted 1.0 sd, where power at 0.01 is ~0.8: both implementations
    # rejected on the same 32 of 40 and the check read NOT_QUALIFIED against a gate that no
    # correct implementation could have reached. The deviation is recorded below; the gate
    # was moved to the attainable range, not the data to the gate.
    pos = []
    for i in range(n_fixtures):
        a = rng.standard_normal(n)
        b = rng.standard_normal(n) + 1.5
        pos.append({"home": f1_home(a, b, n_perm, seed=i), "scipy": f1_scipy(a, b, n_perm, seed=i)})
    pos_home = sum(1 for r in pos if r["home"] < 0.01)
    pos_scipy = sum(1 for r in pos if r["scipy"] < 0.01)
    pos_concordant = sum(1 for r in pos if (r["home"] < 0.01) == (r["scipy"] < 0.01))
    rec["deviations"].append(
        "run 1 (adapter_qualification-scipy_resampling-20260912T010316Z): positive control planted 1.0 sd "
        "(power ~0.8 at alpha 0.01); both implementations rejected on the same 32/40 and the 40/40 gate was "
        "unattainable. Shift raised to 1.5 sd BEFORE this run; per-fixture concordance added as the parity "
        "measure that does not depend on power.")

    # NEGATIVE: exchangeable arms -- rejection rate at alpha 0.05 must be near 0.05 for both,
    # and the two p-values must agree within Monte-Carlo error on every fixture
    neg = []
    for i in range(n_fixtures):
        a = rng.standard_normal(n)
        b = rng.standard_normal(n)
        ph, ps = f1_home(a, b, n_perm, seed=i), f1_scipy(a, b, n_perm, seed=i)
        neg.append({"home": ph, "scipy": ps, "abs_diff": abs(ph - ps),
                    "within_3se": abs(ph - ps) <= 3 * (mc_se(ph, n_perm) + mc_se(ps, n_perm))})
    neg_home = sum(1 for r in neg if r["home"] < 0.05)
    neg_scipy = sum(1 for r in neg if r["scipy"] < 0.05)
    agree = sum(1 for r in neg if r["within_3se"])

    # CHEAT: the label-blind implementation must be caught by the positive control
    cheat_detect = sum(1 for _ in range(n_fixtures)
                       if cheat_ignores_labels(rng.standard_normal(n), rng.standard_normal(n) + 1.0) < 0.01)

    obs = rec["observations"]
    obs["positive_control"] = {"n_fixtures": n_fixtures, "planted_shift_sd": 1.5, "n_per_arm": n,
                               "home_rejects_at_0.01": pos_home, "scipy_rejects_at_0.01": pos_scipy,
                               "per_fixture_concordance": "%d/%d" % (pos_concordant, n_fixtures)}
    obs["negative_control"] = {"n_fixtures": n_fixtures, "home_rejects_at_0.05": neg_home,
                               "scipy_rejects_at_0.05": neg_scipy,
                               "expected_rejects_at_0.05": round(0.05 * n_fixtures, 1),
                               "pvalue_agreement_within_3_mc_se": "%d/%d" % (agree, n_fixtures),
                               "max_abs_pvalue_diff": max(r["abs_diff"] for r in neg)}
    obs["cheat_control"] = {"label_blind_implementation_rejects_at_0.01": cheat_detect,
                            "reading": "0 of %d means the harness sees a wrong implementation as wrong" % n_fixtures}
    obs["rows"] = {"positive": pos, "negative": neg}

    ok = (pos_home >= n_fixtures - 1 and pos_scipy >= n_fixtures - 1 and pos_concordant == n_fixtures
          and cheat_detect == 0
          and agree >= n_fixtures - 2 and neg_home <= 0.15 * n_fixtures and neg_scipy <= 0.15 * n_fixtures)
    rec["status"] = "QUALIFIED" if ok else "NOT_QUALIFIED"
    rec["verdict"] = ("scipy.stats.permutation_test(permutation_type='independent') reproduces the tree's "
                      "F1 permutation null within Monte-Carlo error on every fixture; a seat writing a new "
                      "two-sample label-shuffle null can cite this receipt instead of a loop. This says "
                      "nothing about which null any campaign should use." if ok else
                      "DISAGREEMENT recorded; see observations")
    rec["consumers_named"] = ["Nemesis (chance floors, cheat controls)", "Rhadamanthus (forensic re-tests)",
                              "any seat about to write a permutation loop"]
    p = receipt.write(rec)
    print(rec["status"], p)
    print("positive  home %d/%d  scipy %d/%d  concordant %d/%d" % (pos_home, n_fixtures, pos_scipy, n_fixtures, pos_concordant, n_fixtures))
    print("negative  home %d  scipy %d  (expect ~%.1f)  agree %d/%d  max|dp| %.4f" % (
        neg_home, neg_scipy, 0.05 * n_fixtures, agree, n_fixtures, obs["negative_control"]["max_abs_pvalue_diff"]))
    print("cheat     label-blind rejects %d/%d" % (cheat_detect, n_fixtures))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(run())
