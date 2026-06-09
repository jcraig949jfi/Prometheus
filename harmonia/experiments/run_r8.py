"""R8 lemma-selection across 3 models — does the over-reach (capability-vs-control)
failure generalize from R2/R5 to lemma-handling? (EXPERIMENTAL)

Identical probes across Opus 4.8 / Sonnet 4.6 / Haiku 4.5, deterministic index
grading. The key morphology: among WRONG answers, how often did the model grab the
'over_general_false' lemma (the control trap) vs an irrelevant/trivial one?

Usage: python harmonia/experiments/run_r8.py [N]
"""
import sys, random
from collections import Counter
import numpy as np

sys.path.insert(0, "harmonia/experiments")
from reasoning_phase0 import gen_R8, grade
from reasoners_llm import make_opus_reasoner

MODELS = [("claude-opus-4-8", True), ("claude-sonnet-4-6", True), ("claude-haiku-4-5", False)]
N = int(sys.argv[1]) if len(sys.argv) > 1 else 30


def main():
    rng = random.Random(20260529)
    allp = gen_R8(rng); rng.shuffle(allp)
    probes = allp[:N]
    print(f"R8 lemma-selection | n={N} | models={[m for m,_ in MODELS]}")
    for model, think in MODELS:
        print(f"\n--- {model} ---", flush=True)
        log = []
        r = make_opus_reasoner(model=model, use_thinking=think, call_log=log)
        rows = []
        for i, p in enumerate(probes):
            ans, tr = r(p)
            v, ok = grade(p, ans, tr)
            rows.append((ok, v["_kill_pattern"]))
            if (i + 1) % 15 == 0:
                print(f"    {i+1}/{len(probes)}", flush=True)
        acc = np.mean([ok for ok, _ in rows])
        wrong = Counter(kp for ok, kp in rows if not ok and kp)
        perr = len([c for c in log if c.get("parse_error")])
        tin = sum(c.get("in", 0) for c in log); tout = sum(c.get("out", 0) for c in log)
        rate = {"claude-opus-4-8": (5, 25), "claude-sonnet-4-6": (3, 15),
                "claude-haiku-4-5": (1, 5)}.get(model, (5, 25))
        est = tin * rate[0] / 1e6 + tout * rate[1] / 1e6
        n_over = wrong.get("grabbed_overgeneral_lemma", 0)
        n_wrong = sum(wrong.values())
        print(f"  accuracy={acc:.2f}  failures={perr}  est=${est:.3f}")
        print(f"  errors={n_wrong}  of which over-general-trap grabs={n_over}  "
              f"full error morphology={dict(wrong)}")

    print("\nRead: if Opus's errors are dominated by 'grabbed_overgeneral_lemma' "
          "(the tempting FALSE powerful lemma) more than Sonnet's, the over-reach / "
          "capability-vs-control signal generalizes from R2/R5 to lemma handling.")


if __name__ == "__main__":
    main()
