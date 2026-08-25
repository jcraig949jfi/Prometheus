"""Replicate the sweep's small-step detections across seeds. Required by the prereg, not optional.

The two-sided sensitivity sweep returned a NON-MONOTONIC curve:

    step  1   detected    margin +0.0078   (structural, upper tail)
    step  2   detected    margin +0.0102   (lexical, lower tail)
    step  3   not detected
    step 10   not detected
    step 30   detected    margin +0.1124   (both adversaries, upper tail)

A dose-response cannot go detected -> not detected -> detected. Steps 1 and 2 carry margins near
0.01 and disagree about which tail fired; step 30 carries a margin an order of magnitude larger
with both adversaries on the same side. That is the signature of a false alarm, and the gate's
own preregistration (§4.1) says what is owed when a detection fires: *inspection and replication,
never the conclusion "leakage proved"*. The multiplicity is the reason -- 4 pairs per step at a
two-sided 5%+5% gives a family-wise false-alarm probability near 34% per step under the null, and
the hair trigger is kept deliberately.

So this script does the replication rather than asserting the conclusion. It re-runs the small
steps under several independent permutation seeds and asks whether detection REPRODUCES.

The honest prior, written before running: I expect steps 1 and 2 not to replicate, and step 30
to replicate every time. I record this because I already over-read the first result once --
having seen "step 1 detected" I reported it as a genuine sensitivity improvement before looking
at the rest of the curve, which was in the same output and disconfirmed it.

    python ergon/probe/leakage_floor_replication.py

No LLM. No network.
"""
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import GroupKFold

from ergon.probe.adversarial_leakage import (
    FACTORIAL_CELLS, OUT, _dictvec, build, cv_balanced_accuracy, permute_within_task,
    structural_features, target_labels,
)
from ergon.probe.leakage_sensitivity_sweep import make_injector

STEPS = (1, 2, 3, 30)          # 30 is the positive control for the replication itself
SEEDS = (11, 22, 33, 44, 55)
N_PERM = 50


def one(texts, arm_labels, groups, seed):
    rng = np.random.default_rng(seed)
    Xtext = TfidfVectorizer(analyzer="char", ngram_range=(1, 5), min_df=2,
                            lowercase=False).fit_transform(texts)
    Xstruct, _ = _dictvec([structural_features(t) for t in texts])
    hits = {}
    for target in ("arm6", "cell4"):
        y_all = target_labels(arm_labels, target)
        keep = (np.isin(arm_labels, FACTORIAL_CELLS) if target == "cell4"
                else np.ones(len(arm_labels), dtype=bool))
        idx = np.where(keep)[0]
        g, y = groups[idx], y_all[idx]
        folds = list(GroupKFold(n_splits=5).split(np.zeros(len(y)), y, g))
        for adv, X, kind in (("lexical", Xtext, "text"), ("structural", Xstruct, "trees")):
            Xk = X[idx]
            obs = cv_balanced_accuracy(Xk, y, g, kind, folds)
            null = np.array([cv_balanced_accuracy(Xk, permute_within_task(y, g, rng), g, kind,
                                                  folds) for _ in range(N_PERM)])
            p05, p95 = np.percentile(null, 5), np.percentile(null, 95)
            hits[f"{adv}|{target}"] = bool(obs > p95 or obs < p05)
    return hits


def main():
    import ergon.probe.campaign as C
    OUT.mkdir(parents=True, exist_ok=True)
    rows = C.manifest()
    gold = {r["uid"]: r["gold_int"] for r in rows}
    arms_obj = C.Arms(rows, gold)

    report = {"purpose": "does a small-step detection REPLICATE across permutation seeds?",
              "prior_stated_before_running":
                  "steps 1 and 2 will not replicate; step 30 will replicate every time",
              "why": "the sweep curve was non-monotonic (1 and 2 detected, 3 and 10 not, 30 "
                     "detected), which a real dose-response cannot be",
              "n_seeds": len(SEEDS), "n_perm": N_PERM, "steps": {}}

    for step in STEPS:
        texts, labels, groups, _ = build(rows, arms_obj, inject=make_injector(step))
        per_seed = {}
        for sd in SEEDS:
            per_seed[str(sd)] = one(texts, labels, groups, sd)
        rate = sum(any(h.values()) for h in per_seed.values()) / len(SEEDS)
        # how often does the SAME pair fire?
        pairs = sorted(next(iter(per_seed.values())))
        pair_rate = {p: sum(per_seed[s][p] for s in per_seed) / len(SEEDS) for p in pairs}
        report["steps"][str(step)] = {"any_detection_rate": rate, "per_pair_rate": pair_rate,
                                      "per_seed": per_seed}
        print(f"step {step:>3}  any-detection in {rate:.0%} of seeds   "
              f"max single-pair rate {max(pair_rate.values()):.0%}")

    r1 = report["steps"]["1"]["any_detection_rate"]
    r2 = report["steps"]["2"]["any_detection_rate"]
    r30 = report["steps"]["30"]["any_detection_rate"]
    report["verdict"] = (
        "STEPS 1-2 ARE FALSE ALARMS. They fired once and did not reproduce, while step 30 "
        "reproduced. The sweep's `smallest_detected_step: 1` is an artifact of the "
        "deliberately-hair-trigger multiplicity rule and MUST NOT be published as a "
        "sensitivity floor."
        if (r1 < 1.0 and r2 < 1.0 and r30 == 1.0) else
        "REPLICATED — the small-step detections are not obviously false alarms and the "
        "non-monotonicity needs a different explanation. Do not treat this as a clean floor "
        "either; investigate before publishing any number."
        if (r1 == 1.0 or r2 == 1.0) else
        "INCONCLUSIVE — including the step-30 positive control, which did not replicate. If the "
        "control does not fire reliably, no null from this harness is interpretable.")
    (OUT / "floor_replication.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\n" + report["verdict"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
