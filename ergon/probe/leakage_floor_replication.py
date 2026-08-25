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

#: STEP 0 IS THE CONTROL THIS DESIGN WAS MISSING. See `one()` for why the first version could
#: not distinguish a real small signal from a borderline observation against a stable null.
STEPS = (0, 1, 2, 3, 30)       # 0 = NO injection; 30 = positive control for the harness
SEEDS = (11, 22, 33, 44, 55)
N_PERM = 50


def _shuffled_folds(y, g, seed):
    """5 grouped folds with the GROUP-TO-FOLD ASSIGNMENT SHUFFLED by `seed`.

    THIS IS THE CORRECTION. The first version of this script varied only the permutation seed,
    which re-estimates the NULL and leaves `obs` untouched -- `GroupKFold` is deterministic
    given the groups, and the classifier seed was fixed, so the observed statistic was
    literally identical across every "replicate". A borderline `obs` sitting just outside a
    stable null therefore reproduced 100% of the time WITHOUT BEING REAL, and I read that as
    evidence about signal. It was evidence about null-estimation noise.

    Varying the fold assignment moves `obs` as well, so a detection now has to survive a
    different partition of the data and not merely a different null draw.
    """
    groups = np.unique(g)
    rng = np.random.default_rng(seed)
    rng.shuffle(groups)
    assign = {grp: i % 5 for i, grp in enumerate(groups)}
    fold_of = np.array([assign[x] for x in g])
    return [(np.where(fold_of != k)[0], np.where(fold_of == k)[0]) for k in range(5)]


def one(texts, arm_labels, groups, seed):
    """One replicate: BOTH the fold assignment and the permutation null vary with `seed`."""
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
        folds = _shuffled_folds(y, g, seed)
        for adv, X, kind in (("lexical", Xtext, "text"), ("structural", Xstruct, "trees")):
            Xk = X[idx]
            obs = cv_balanced_accuracy(Xk, y, g, kind, folds, seed=seed)
            null = np.array([cv_balanced_accuracy(Xk, permute_within_task(y, g, rng), g, kind,
                                                  folds, seed=seed) for _ in range(N_PERM)])
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

    r0 = report["steps"]["0"]["any_detection_rate"]
    r1 = report["steps"]["1"]["any_detection_rate"]
    r30 = report["steps"]["30"]["any_detection_rate"]
    report["control_step0_false_alarm_rate"] = r0
    if r30 < 1.0:
        report["verdict"] = ("INCONCLUSIVE — the step-30 positive control did not fire in every "
                             "replicate. If the control is unreliable, no null from this harness "
                             "is interpretable and nothing else here may be read.")
    elif r0 >= 0.5:
        report["verdict"] = (
            "SINGLE-PAIR DETECTIONS ARE AN ARTIFACT. With NO injected leak at all, 'any pair "
            "fires' occurs in %.0f%% of replicates — so a lone pair firing carries no evidence, "
            "and the steps 1-2 detections must not be read as a sensitivity floor. Only "
            "unanimous multi-pair detections (step 30) mean anything in this harness." % (100 * r0))
    elif r0 == 0.0 and r1 >= 0.8:
        report["verdict"] = (
            "SMALL-STEP DETECTIONS SURVIVE THE CORRECTED DESIGN. The step-0 control never fired, "
            "and step 1 fired across shuffled folds as well as shuffled nulls. The gate detects "
            "a per-arm offset of 1 on an otherwise-constant field. NOTE this is a statement "
            "about a CONSTANT baseline field (INV 7), not about the old packets.")
    else:
        report["verdict"] = (
            "MIXED — control fired at %.0f%%, step 1 at %.0f%%. Not clean either way. Do NOT "
            "publish a floor from this; the honest statement is that only unanimous multi-pair "
            "detections are trustworthy in this harness." % (100 * r0, 100 * r1))
    (OUT / "floor_replication.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\n" + report["verdict"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
