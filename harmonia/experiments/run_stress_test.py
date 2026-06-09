"""Stress test — the decisive keep-or-kill for the Opus<Sonnet execution gap.

Arm 1 (ph0-STRESSED R2): the exact cell where the Exp-A deficit lived — sqrt
extraneous-root, ALL probes at ph0 (the explicit "discard extraneous" scaffold),
n=40/model, effort PINNED at "high" (removes the thinking-allocation confound),
Wilson 95% CIs + over-refuse/keeps-extraneous morphology.

Arm 2 (C-MEMO, rational_extra): the SAME legality skill in a DIFFERENT operation —
(x^2-c^2)/(x-c)=k, where k=2c makes the only candidate the excluded value (no
solution). If the Opus gap appears here too, it's a legality-EXECUTION axis, not
sqrt-canonical memorization. If Opus is fine here but not on sqrt-ph0, the deficit
is canonical-instance-specific.

Both models at effort="high" (Sonnet's max supported level; identical => fair).

Usage: python harmonia/experiments/run_stress_test.py [N]
"""
import sys, random, math
from collections import Counter

sys.path.insert(0, "harmonia/experiments")
from reasoning_phase0 import gen_R2, gen_rational_extra, gen_abs_extra, gen_log_extra, grade
from reasoners_llm import make_opus_reasoner
from morphology import classify_r2
from verifier_lens import verify

N = int(sys.argv[1]) if len(sys.argv) > 1 else 40
MODELS = ("claude-opus-4-8", "claude-sonnet-4-6")


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def run_arm(name, probes, r2_morph):
    print(f"\n===== {name} (n={len(probes)}, effort=high pinned) =====")
    for model in MODELS:
        log = []
        r = make_opus_reasoner(model=model, effort="high", call_log=log)
        res, morph, fails = [], Counter(), 0
        for p in probes:
            ans, tr = r(p)
            if (tr.get("_parse_error") or "").startswith("api_error"):
                fails += 1                      # api-500/transient: NOT a reasoning error — exclude
                continue
            v, ok = grade(p, ans, tr)
            res.append(bool(ok))
            if not ok:
                morph[classify_r2(p, ans, tr, verify(p, ans)) if r2_morph else v["_kill_pattern"]] += 1
        k, n = sum(res), len(res)
        lo, hi = wilson(k, n)
        tag = model.split("-")[1] + "-" + model.split("-")[2]
        print(f"  {tag:10s} acc={k}/{n}={k/max(1,n):.2f}  95%CI=[{lo:.2f},{hi:.2f}]  "
              f"api_fails(excluded)={fails}  errors={dict(morph)}")


def main():
    print(f"STRESS TEST | N={N} | Opus 4.8 vs Sonnet 4.6 | effort=high")
    # Arm 1: ph0-stressed R2 (force every probe to the explicit-scaffold phrasing)
    rng = random.Random(20260529)
    r2 = gen_R2(rng); rng.shuffle(r2); r2 = r2[:N]
    for p in r2:
        p.data["phrasing"] = 0
    run_arm("ARM 1 — R2 sqrt, ph0-STRESSED", r2, r2_morph=True)

    # Arm 2: C-MEMO rational extraneous (different operation, same legality skill)
    rng2 = random.Random(20260530)
    re = gen_rational_extra(rng2); rng2.shuffle(re); re = re[:N]
    run_arm("ARM 2 — rational_extra (C-MEMO, different operation)", re, r2_morph=False)

    # Arm 3: C-MEMO absolute-value extraneous
    rng3 = random.Random(20260531)
    ae = gen_abs_extra(rng3); rng3.shuffle(ae); ae = ae[:N]
    run_arm("ARM 3 — abs_extra (C-MEMO, |x-a|=b-x)", ae, r2_morph=False)

    # Arm 4: C-MEMO log-domain extraneous
    rng4 = random.Random(20260532)
    le = gen_log_extra(rng4); rng4.shuffle(le); le = le[:N]
    run_arm("ARM 4 — log_extra (C-MEMO, log-domain)", le, r2_morph=False)

    print("\nREAD:")
    print("  KILL: Opus ~ Sonnet (overlapping CIs) on ph0-R2 => the n=40 inversion was small-N/phrasing,")
    print("        not a robust execution gap. Finding stays demoted/retracted.")
    print("  SURVIVE (R2 only): Opus < Sonnet on ph0-R2 with non-overlapping CIs, Opus errors dominated by")
    print("        over_refused => execution-control gap is real at the legality cell, even at pinned high effort.")
    print("  GENERALIZES: Opus < Sonnet on rational_extra TOO => legality-execution axis, not sqrt memorization.")
    print("  MEMORIZATION: Opus fine on rational_extra but < Sonnet on sqrt-ph0 => canonical-instance-specific.")


if __name__ == "__main__":
    main()
