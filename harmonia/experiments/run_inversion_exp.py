"""Experiment A — confirm/kill the Opus 4.8 < Sonnet 4.6 inversion on R2/R5.

R2 + R5 only, Opus 4.8 vs Sonnet 4.6, identical probes, n per tier, 3 prompt
phrasings rotated (to separate model capability from probe-wording resonance),
deterministic verifier, and — the point — failure-MORPHOLOGY labels, not just
score. Output: score (overall + per phrasing) + a model x failure-shape matrix.

Usage: python harmonia/experiments/run_inversion_exp.py [N_per_tier]
"""
import sys, random
from collections import Counter, defaultdict
import numpy as np

sys.path.insert(0, "harmonia/experiments")
from reasoning_phase0 import gen_R2, gen_R5, grade
from reasoners_llm import make_opus_reasoner
from morphology import classify_r2, classify_r5
try:
    from verifier_lens import verify
    HAVE_VER = True
except Exception:
    HAVE_VER = False

MODELS = [("claude-opus-4-8", True), ("claude-sonnet-4-6", True)]
N = int(sys.argv[1]) if len(sys.argv) > 1 else 40


def sample(gen, rng):
    allp = gen(rng)
    rng.shuffle(allp)
    picked = allp[:N]
    for i, p in enumerate(picked):
        p.data["phrasing"] = i % 3        # rotate 3 phrasings
    return picked


def main():
    rng = random.Random(20260529)
    r2 = sample(gen_R2, rng)
    r5 = sample(gen_R5, rng)
    probes = [("R2", p) for p in r2] + [("R5", p) for p in r5]
    print(f"Experiment A | inversion confirm | n={N}/tier | R2+R5 | "
          f"models={[m for m,_ in MODELS]} | verifier={HAVE_VER}")

    per = {}  # (model,tier) -> list of (correct, phrasing, label)
    ver = defaultdict(lambda: [0, 0])  # model -> [agree, disagree]
    cost = {}
    for model, think in MODELS:
        print(f"\n--- {model} ---", flush=True)
        log = []
        reasoner = make_opus_reasoner(model=model, use_thinking=think, call_log=log)
        for i, (tier, p) in enumerate(probes):
            ans, tr = reasoner(p)
            _v, ok = grade(p, ans, tr)
            if tier == "R2":
                vres = verify(p, ans) if HAVE_VER else None
                if vres and vres.get("valid") is not None:
                    ver[model][0 if bool(vres["valid"]) == bool(ok) else 1] += 1
                label = classify_r2(p, ans, tr, vres)
            else:
                label = classify_r5(p, ans, tr)
            per.setdefault((model, tier), []).append((ok, p.data["phrasing"], label))
            if (i + 1) % 20 == 0:
                print(f"    {model}: {i+1}/{len(probes)}", flush=True)
        tin = sum(c.get("in", 0) for c in log); tout = sum(c.get("out", 0) for c in log)
        rate = {"claude-opus-4-8": (5, 25), "claude-sonnet-4-6": (3, 15)}.get(model, (5, 25))
        cost[model] = (len([c for c in log if c.get("parse_error")]),
                       tin * rate[0] / 1e6 + tout * rate[1] / 1e6)

    print("\n================= SCORE (overall + by phrasing) =================")
    print(f"{'model':22s} {'tier':4s}  overall   ph0    ph1    ph2")
    for model, _ in MODELS:
        for tier in ("R2", "R5"):
            rows = per[(model, tier)]
            overall = np.mean([ok for ok, _, _ in rows])
            byp = []
            for ph in (0, 1, 2):
                cell = [ok for ok, p, _ in rows if p == ph]
                byp.append(np.mean(cell) if cell else float("nan"))
            print(f"{model:22s} {tier:4s}  {overall:5.2f}   " +
                  " ".join(f"{v:5.2f}" for v in byp))

    print("\n================= FAILURE-MORPHOLOGY MATRIX (model x shape) =================")
    for tier in ("R2", "R5"):
        labels = sorted({l for (m, t), rows in per.items() if t == tier for _, _, l in rows})
        print(f"\n[{tier}]  " + "  ".join(f"{l}" for l in labels))
        for model, _ in MODELS:
            c = Counter(l for _, _, l in per[(model, tier)])
            print(f"  {model:20s} " + "  ".join(f"{l}={c.get(l,0)}" for l in labels))

    print("\n================= VERIFIER / COST =================")
    for model, _ in MODELS:
        a, d = ver[model]
        f, est = cost[model]
        print(f"  {model}: verifier(agree/disagree)={a}/{d}  failures={f}  est=${est:.3f}")

    print("\nINTERPRETATION GUIDE:\n"
          "  - converge within noise -> earlier inversion was provisional noise.\n"
          "  - Sonnet stays ahead on R2/R5 -> promote to a named finding.\n"
          "  - DIFFERENT failure shapes (e.g. Opus 'keeps_extraneous'/'correct_invalid_"
          "justification' while Sonnet 'correct_sound') -> promote EVEN IF the score gap "
          "narrows: that is the 'strength is not ladder-monotone / worse local control' signal.\n"
          "  - phrasing columns: if Opus only fails on ph1/ph2 (no explicit legality/invariant "
          "scaffold) it's a CONTROL-discipline gap, not a capability gap.")


if __name__ == "__main__":
    main()
