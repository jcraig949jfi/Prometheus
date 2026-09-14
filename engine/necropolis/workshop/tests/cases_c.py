"""Necropolis workshop control cases, batch C (NECROPOLIS VALIDATION layer).

Wave-2 Keeper-authored controls for instruments the scouts surfaced.  Same
verdict vocabulary as run_controls: PASS = instrument behaved as a working
instrument must; FAIL = it did not (CHEAT FAIL = cheat succeeded); INFO =
observation only; ERROR = the case could not run (dependency), which is a
finding about the host, not the tool.

Every case here manufactures its own inputs.  None reads a grave.
"""
from __future__ import annotations

import importlib
import json
import math
import random
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def register(case):

    # ------------------------------------------------------------------ bswcd_null (harmonia/nulls/block_shuffle.py)
    def _bswcd_frame(n=400, seed=0, signal=True):
        import numpy as np
        import pandas as pd
        rng = np.random.default_rng(seed)
        strat = rng.integers(1, 10_000, size=n).astype(float)
        noise = rng.normal(size=n)
        # signal: value depends on stratifier AND on a within-stratum covariate x
        x = rng.normal(size=n)
        value = 0.3 * np.log(strat) + (0.8 * x if signal else 0.0) + noise
        return pd.DataFrame({"conductor": strat, "x": x, "value": value})

    def _slope(df):
        import numpy as np
        return float(np.corrcoef(df["x"].to_numpy(), df["value"].to_numpy())[0, 1])

    @case("bswcd_null.SYNTHETIC_SIGNAL.within_stratum_dependence_is_durable", "bswcd_null", "SYNTHETIC_SIGNAL")
    def _():
        B = importlib.import_module("harmonia.nulls.block_shuffle")
        r = B.bswcd_null(_bswcd_frame(signal=True), stratifier="conductor", n_bins=10, n_perms=200, seed=1, statistic=_slope)
        return r["verdict"] == "DURABLE" and r["z_score"] > 4, {k: r[k] for k in ("verdict", "z_score", "observed", "null_mean", "null_std", "n_strata_used")}

    @case("bswcd_null.SYNTHETIC_NULL.stratifier_only_dependence_collapses", "bswcd_null", "SYNTHETIC_NULL")
    def _():
        """value depends only on the stratifier; the within-stratum shuffle must
        NOT report the marginal stratifier trend as durable.  Statistic here is
        the marginal corr(value, log conductor), which a naive shuffle would call
        signal and a stratified shuffle preserves under the null."""
        import numpy as np
        B = importlib.import_module("harmonia.nulls.block_shuffle")
        df = _bswcd_frame(signal=False)
        stat = lambda d: float(np.corrcoef(np.log(d["conductor"].to_numpy()), d["value"].to_numpy())[0, 1])  # noqa: E731
        r = B.bswcd_null(df, stratifier="conductor", n_bins=10, n_perms=200, seed=1, statistic=stat)
        return r["verdict"] == "COLLAPSES", {k: r[k] for k in ("verdict", "z_score", "observed", "null_mean", "null_std")}

    @case("bswcd_null.REPETITION.same_seed_same_null", "bswcd_null", "REPETITION")
    def _():
        B = importlib.import_module("harmonia.nulls.block_shuffle")
        a = B.bswcd_null(_bswcd_frame(), n_perms=100, seed=5, statistic=_slope)
        b = B.bswcd_null(_bswcd_frame(), n_perms=100, seed=5, statistic=_slope)
        same = (a["null_mean"], a["null_std"], a["z_score"]) == (b["null_mean"], b["null_std"], b["z_score"])
        return same, {"a": a["z_score"], "b": b["z_score"]}

    # ------------------------------------------------------------------ bootstrap family (prometheus_math/research/bootstrap.py)
    @case("pm_bootstrap.SYNTHETIC_SIGNAL.permutation_test_separates_shifted_samples", "pm_bootstrap", "SYNTHETIC_SIGNAL")
    def _():
        PB = importlib.import_module("prometheus_math.research.bootstrap")
        rng = random.Random(0)
        a = [rng.gauss(0, 1) for _ in range(60)]
        b = [rng.gauss(1.0, 1) for _ in range(60)]
        r = PB.permutation_test(a, b, n=2000, seed=0)
        p = r.get("p_value", r.get("p"))
        return p is not None and p < 0.01, {"p": p, "observed": r.get("observed", r.get("statistic"))}

    @case("pm_bootstrap.SYNTHETIC_NULL.permutation_test_uniform_p_under_null", "pm_bootstrap", "SYNTHETIC_NULL")
    def _():
        """50 null replicates; fraction with p<0.05 must sit near 0.05 (binomial 95% band [0, 0.14])."""
        PB = importlib.import_module("prometheus_math.research.bootstrap")
        rng = random.Random(1)
        hits = 0
        for i in range(50):
            a = [rng.gauss(0, 1) for _ in range(30)]
            b = [rng.gauss(0, 1) for _ in range(30)]
            r = PB.permutation_test(a, b, n=500, seed=i)
            hits += (r.get("p_value", r.get("p")) < 0.05)
        return hits <= 7, {"false_positive_rate": hits / 50, "n": 50}

    @case("pm_bootstrap.ACCEPT.bootstrap_ci_covers_true_mean", "pm_bootstrap", "ACCEPT")
    def _():
        PB = importlib.import_module("prometheus_math.research.bootstrap")
        rng = random.Random(2)
        cover = 0
        for i in range(40):
            xs = [rng.gauss(3.0, 2.0) for _ in range(50)]
            r = PB.bootstrap_ci(xs, n_resamples=500, seed=i)
            lo, hi = r["ci_lower"], r["ci_upper"]
            cover += (lo <= 3.0 <= hi)
        return cover >= 32, {"coverage_of_true_mean": cover / 40, "nominal": 0.95}

    @case("pm_bootstrap.REJECT.matched_null_p_floor_is_one_over_n_plus_1", "pm_bootstrap", "REJECT")
    def _():
        """An observation far outside the null must NOT report p=0.  Measured:
        the code regularises each tail as (count+1)/(n+1) and doubles, so the
        floor is 2/(n+1); the docstring says 1/(n+1).  Behaviour is the more
        conservative of the two; the docstring is wrong by a factor of 2."""
        PB = importlib.import_module("prometheus_math.research.bootstrap")
        rng = random.Random(3)
        r = PB.matched_null_test(50.0, lambda: rng.gauss(0, 1), n=999, seed=0)
        p = r.get("p_value")
        return p is not None and 0 < p <= 2 / 1000 + 1e-12, {"p": p, "code_floor": 2 / 1000, "docstring_floor": 1 / 1000}

    @case("pm_bootstrap.PARITY.holm_bonferroni_matches_hand_computation", "pm_bootstrap", "PARITY")
    def _():
        PB = importlib.import_module("prometheus_math.research.bootstrap")
        ps = [0.01, 0.04, 0.03, 0.20]
        adj = list(map(float, PB.holm_bonferroni(ps)))
        # Holm: sort 0.01,0.03,0.04,0.20 -> x4,x3,x2,x1 = 0.04,0.09,0.08->monotone 0.09,0.20
        expected = [0.04, 0.09, 0.09, 0.20]
        ok = all(abs(x - y) < 1e-9 for x, y in zip(adj, expected))
        return ok, {"adjusted": adj, "expected": expected}

    # ------------------------------------------------------------------ kill_resurrection_audit (harmonia/diagnostics)
    @case("kill_resurrection.ACCEPT.relation_evaluator_truth_table", "kill_resurrection", "ACCEPT")
    def _():
        KR = importlib.import_module("harmonia.diagnostics.kill_resurrection_audit")
        checks = {
            "equal_t": KR.evaluate("equal", 3, 3.0) is True,
            "equal_f": KR.evaluate("equal", 3, 4) is False,
            "mod2": KR.evaluate("equal_mod_2", 7, 9) is True,
            "abs_diff": KR.evaluate("abs_diff_le_2", 1, 3) is True and KR.evaluate("abs_diff_le_2", 1, 4) is False,
            "divides": KR.evaluate("divides", 3, 9) is True and KR.evaluate("divides", 0, 0) is True,
            "unknown_relation_is_None": KR.evaluate("bogus", 1, 1) is None,
            "non_numeric_is_None": KR.evaluate("equal", "x", 1) is None,
        }
        return all(checks.values()), checks

    @case("kill_resurrection.REJECT.equal_mod_0_is_not_true", "kill_resurrection", "REJECT")
    def _():
        KR = importlib.import_module("harmonia.diagnostics.kill_resurrection_audit")
        return KR.evaluate("equal_mod_0", 4, 4) is False, {"equal_mod_0(4,4)": KR.evaluate("equal_mod_0", 4, 4)}

    @case("kill_resurrection.ACCEPT.rule_of_three", "kill_resurrection", "ACCEPT")
    def _():
        KR = importlib.import_module("harmonia.diagnostics.kill_resurrection_audit")
        return abs(KR.rule_of_three(92) - 3 / 92) < 1e-12 and math.isnan(KR.rule_of_three(0)), {"92": KR.rule_of_three(92)}

    # ------------------------------------------------------------------ fossil_inference (archaeon/producer)
    @case("fossil_inference.ACCEPT.two_fossils_pin_target_set_equal_to_bruteforce", "fossil_inference", "ACCEPT")
    def _():
        F = importlib.import_module("archaeon.producer.fossil_inference")
        rng = random.Random(0)
        agree = 0
        for _ in range(25):
            L = 8
            target = "".join(rng.choice("01") for _ in range(L))
            fossils = []
            for _ in range(3):
                bits = "".join(rng.choice("01") for _ in range(L))
                ham = sum(a != b for a, b in zip(bits, target))
                fossils.append(F.Fossil(bits, 1 - ham / L))
            inf = F.infer(fossils)
            brute = F.enumerate_targets(fossils)
            agree += (inf.feasible_targets == len(brute) and target in brute)
        return agree == 25, {"agree": agree, "of": 25}

    @case("fossil_inference.CHEAT.tampered_score_raises_contradiction", "fossil_inference", "CHEAT")
    def _():
        """Cheat: forge a fossil set whose scores are jointly impossible.  A working
        oracle must raise Contradiction rather than return a target set."""
        F = importlib.import_module("archaeon.producer.fossil_inference")
        # identical probes, different scores -> no target can satisfy both
        fossils = [F.Fossil("0000", 0.5), F.Fossil("0000", 0.75)]
        try:
            inf = F.infer(fossils)
            return False, {"returned": inf.status(), "feasible": inf.feasible_targets}
        except F.Contradiction as e:
            return True, {"raised": "Contradiction", "msg": str(e)[:80]}

    @case("fossil_inference.CORRUPT_INPUT.non_integer_hamming_score_rejected", "fossil_inference", "CORRUPT_INPUT")
    def _():
        F = importlib.import_module("archaeon.producer.fossil_inference")
        try:
            F.infer([F.Fossil("0000", 0.3)])
            return False, {"note": "accepted score 0.3 on L=4 (m=2.8 not integer)"}
        except F.Contradiction as e:
            return True, {"raised": "Contradiction", "msg": str(e)[:80]}

    # ------------------------------------------------------------------ baseline_costume (harmonia/primitives)
    def _costume_rows(n_keys=30, per_key=6, seed=0):
        rng = random.Random(seed)
        rows = []
        for k in range(n_keys):
            maj = rng.choice("AB")
            for _ in range(per_key):
                rows.append({"key": k, "label": maj if rng.random() < 0.85 else ("A" if maj == "B" else "B")})
        return rows

    @case("baseline_costume.REJECT.claim_that_is_marginal_majority_is_called_costume", "baseline_costume", "REJECT")
    def _():
        BC = importlib.import_module("harmonia.primitives.baseline_costume")
        rows = _costume_rows()
        claim = BC.marginal_majority(rows, key_fn=lambda r: r["key"], label_fn=lambda r: r["label"])
        v = BC.costume_check(claim, rows, key_fn=lambda r: r["key"], label_fn=lambda r: r["label"], n_null_trials=20, seed=0)
        verdict = getattr(v, "verdict", None)
        return str(verdict).startswith("COSTUME_OF:marginal_majority"), {"verdict": verdict, "z_vs_null": v.z_vs_null}

    @case("baseline_costume.ACCEPT.claim_beating_every_baseline_is_not_costume", "baseline_costume", "ACCEPT")
    def _():
        BC = importlib.import_module("harmonia.primitives.baseline_costume")
        rng = random.Random(1)
        rows = []
        truth = {}
        for k in range(30):
            truth[k] = rng.choice("AB")
            for _ in range(6):
                rows.append({"key": k, "label": truth[k] if rng.random() < 0.55 else ("A" if truth[k] == "B" else "B")})
        # the claim knows the hidden generator: it beats the noisy marginal majority
        claim = {k: truth[k] for k in truth}
        v = BC.costume_check(claim, rows, key_fn=lambda r: r["key"], label_fn=lambda r: r["label"], n_null_trials=20, seed=0)
        verdict = getattr(v, "verdict", None)
        return not str(verdict).startswith("COSTUME"), {"verdict": verdict, "z_vs_null": v.z_vs_null}

    @case("baseline_costume.CHEAT.unique_key_identity_tie_is_marked_vacuous", "baseline_costume", "CHEAT")
    def _():
        """Cheat from Harmonia D's a3 control: one row per key makes aggregating
        baselines identity-copiers that tie ANY claim.  The guard must mark the
        tie vacuous rather than let it drive a COSTUME verdict."""
        BC = importlib.import_module("harmonia.primitives.baseline_costume")
        rows = [{"key": k, "label": "A" if k % 2 else "B"} for k in range(40)]
        claim = {k: r["label"] for k, r in enumerate(rows)}
        v = BC.costume_check(claim, rows, key_fn=lambda r: r["key"], label_fn=lambda r: r["label"], n_null_trials=10, seed=0)
        verdict = getattr(v, "verdict", None)
        txt = json.dumps(getattr(v, "__dict__", {}), default=str)
        vacuous = "vacuous" in txt.lower()
        return not str(verdict).startswith("COSTUME") and vacuous, {"verdict": verdict, "vacuous_flag_present": vacuous, "headline": v.headline[:200]}

    # ------------------------------------------------------------------ kill_scheme_info_audit (harmonia/primitives)
    @case("kill_scheme_info_audit.ACCEPT.selftest_passes", "kill_scheme_info_audit", "ACCEPT")
    def _():
        K = importlib.import_module("harmonia.primitives.kill_scheme_info_audit")
        K._selftest()
        return True, {"note": "module _selftest raised nothing"}

    @case("kill_scheme_info_audit.SYNTHETIC_SIGNAL.mi_recovers_coordinate_dependence", "kill_scheme_info_audit", "SYNTHETIC_SIGNAL")
    def _():
        K = importlib.import_module("harmonia.primitives.kill_scheme_info_audit")
        rng = random.Random(0)
        xs = [rng.randrange(4) for _ in range(600)]
        ys = [x if rng.random() < 0.9 else rng.randrange(4) for x in xs]
        mi = K.mi_bits(xs, ys)
        null95 = K.perm_null95(xs, ys, n_perms=200, seed=0)
        return mi > null95 and mi > 1.0, {"mi_bits": mi, "perm_null95": null95}

    @case("kill_scheme_info_audit.SYNTHETIC_NULL.independent_labels_below_null95", "kill_scheme_info_audit", "SYNTHETIC_NULL")
    def _():
        K = importlib.import_module("harmonia.primitives.kill_scheme_info_audit")
        rng = random.Random(1)
        xs = [rng.randrange(4) for _ in range(600)]
        ys = [rng.randrange(4) for _ in range(600)]
        mi = K.mi_bits(xs, ys)
        null95 = K.perm_null95(xs, ys, n_perms=200, seed=0)
        return mi <= null95, {"mi_bits": mi, "perm_null95": null95}
