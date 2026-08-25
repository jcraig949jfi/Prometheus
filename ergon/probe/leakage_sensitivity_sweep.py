"""How small a leak can the assignment gate actually see? Bisect it, do not bracket it.

The gate (`adversarial_leakage.py`) returned PASS on the live packets, and its two positive
controls fired: the historical lead line and the historical +40000 slug band were both caught,
the band trivially (balanced accuracy 1.0000 on two targets). The preregistered sensitivity
probe -- a per-arm slug offset of +3/+6/+9/+12 -- was NOT caught.

That leaves the detection floor bracketed between 3 and 40,000: three orders of magnitude, which
is close to no information about what the PASS is worth. A gate whose sensitivity is unknown
licenses nothing, so this sweep replaces the bracket with a number.

Design: the same adversaries, nulls, split and gate as the parent module -- imported, never
re-implemented, so the sweep cannot drift from the thing whose sensitivity it reports. Only the
injected offset varies.

Scope, stated because it is a cap: the two adversaries that caught the band (lexical,
structural) and the two targets they caught it most strongly on (cell4, arm6), at 50
permutations. The distributional adversary and the marginal targets are omitted -- they were
strictly weaker on the positive control, so including them could only lower the estimated floor,
never raise it. The number this produces is therefore a floor for the BEST adversary available,
which is the conservative direction for a claim about what the gate can miss.

    python ergon/probe/leakage_sensitivity_sweep.py

No LLM. No network. Read-only on the manifests.
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
    ARMS, FACTORIAL_CELLS, OUT, SEED, _dictvec, _reslug, build,
    cv_balanced_accuracy, permute_within_task, structural_features, target_labels,
)

#: Multipliers on a per-arm rank, so arm k gets offset k*STEP. STEP=3 reproduces the
#: preregistered probe that was NOT detected; 40000 reproduces the historical defect that was.
STEPS = (1, 2, 3, 10, 30)   # extended DOWN: the two-sided rule caught +3, so the
#                             floor is below the old sweep's smallest rung
N_PERM = 50
ARM_RANK = {a: i for i, a in enumerate(sorted(ARMS))}


def make_injector(step):
    def inject(arm, uid, payload):
        return _reslug(payload, ARM_RANK[arm] * step)
    return inject


def evaluate(texts, arm_labels, groups, n_perm=N_PERM):
    """Lexical + structural, on arm6 and cell4. Returns the max margin over null p95."""
    rng = np.random.default_rng(SEED)
    Xtext = TfidfVectorizer(analyzer="char", ngram_range=(1, 5), min_df=2,
                            lowercase=False).fit_transform(texts)
    Xstruct, _ = _dictvec([structural_features(t) for t in texts])
    out, detected = {}, False
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
                                                  folds) for _ in range(n_perm)])
            p95 = float(np.percentile(null, 95))
            p05 = float(np.percentile(null, 5))
            # TWO-SIDED (ATK-018, Techne). The first version used `obs > p95` alone. Balanced
            # accuracy BELOW chance carries the same information as above it -- an adversary
            # inverts its own prediction -- so the quantity for a recoverability question is
            # |obs - null|, and a one-sided rule discards half the evidence.
            #
            # DO NOT COMPARE THIS SWEEP'S FLOOR TO THE OLD ONE AS IF ONE VARIABLE MOVED. Two
            # things changed between them: the verdict became two-sided, AND INV 7 re-keyed the
            # slug so it is now constant across arms. On the old packets the slug already
            # varied per arm, so an injected offset was a signal on top of existing per-arm
            # noise; on these it is a clean band in an otherwise constant field. The old
            # number described a configuration that no longer exists and is RETIRED rather
            # than corrected. I wrote "that number was a property of the broken verdict" in the
            # first version of this comment -- that was an over-attribution of exactly the kind
            # this file exists to prevent, and it is withdrawn.
            hit = (obs > p95) or (obs < p05)
            detected |= hit
            out[f"{adv}|{target}"] = {
                "observed": round(obs, 4), "null_p05": round(p05, 4), "null_p95": round(p95, 4),
                "null_mean": round(float(null.mean()), 4),
                "signed_delta": round(obs - float(null.mean()), 4),
                "margin_upper": round(obs - p95, 4), "margin_lower": round(p05 - obs, 4),
                "side": "upper" if obs > p95 else "lower" if obs < p05 else "none",
                "detected": bool(hit)}
    return out, detected


def main():
    import ergon.probe.campaign as C
    OUT.mkdir(parents=True, exist_ok=True)
    rows = C.manifest()
    gold = {r["uid"]: r["gold_int"] for r in rows}
    arms_obj = C.Arms(rows, gold)

    report = {"purpose": "smallest per-arm slug offset this gate detects",
              "parent": "ergon/probe/adversarial_leakage.py",
              "prereg": "ergon/probe/PREREG_adversarial_leakage_gate_2026-08-25.md",
              "manifest_sha16": C.manifest_sha256(rows)[:16],
              "scope_cap": "lexical+structural adversaries, arm6+cell4 targets, 50 permutations; "
                           "the omitted adversary/targets were strictly weaker on the positive "
                           "control, so this is a floor for the BEST available adversary",
              "arm_offset_rule": "arm k (alphabetical) receives offset k*STEP on the slug index",
              "steps": {}}

    smallest = None
    for step in STEPS:
        texts, labels, groups, nc = build(rows, arms_obj, inject=make_injector(step))
        pairs, detected = evaluate(texts, labels, groups)
        report["steps"][str(step)] = {"detected": detected, "pairs": pairs,
                                      "nonconforming_payloads": nc}
        if detected and smallest is None:
            smallest = step
        best = max(max(v["margin_upper"], v["margin_lower"]) for v in pairs.values())
        print(f"step {step:>6}  detected={detected!s:5s}  best_margin={best:+.4f}")

    report["smallest_detected_step"] = smallest
    report["largest_undetected_step"] = max(
        [int(k) for k, v in report["steps"].items() if not v["detected"]], default=None)
    report["interpretation"] = (
        "The slug index ranges over [0,200), so a per-arm offset of STEP is a mean shift of "
        "roughly STEP/200 of the field's range, wrapped mod 100000. A leak SMALLER than the "
        "smallest detected step is invisible to this gate, and the live PASS is therefore a "
        "statement about leaks at or above that size -- not about leakage in general."
        if smallest else
        "NO step in the swept range was detected, which would mean the sweep's range is wrong "
        "or the injection is not doing what it claims; check against the parent module's "
        "POSCTRL_slug_band, which used +40000 and was caught at balanced accuracy 1.0000.")
    (OUT / "sensitivity_sweep.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\nsmallest detected offset:", smallest,
          "| largest undetected:", report["largest_undetected_step"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
