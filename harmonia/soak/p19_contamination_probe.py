"""Is HARMA-P19's ground-truth defect actually CONTAMINATING the H1 arm? (soak P27)

P19 established that gen_abs_extra_clean records an incomplete ground truth at
a==b (12.5% of probes): the true solution set of |x-a| = b-x is the half-line
x <= a, while gt is the single point (a+b)/2. P19 logged the IMPACT as
"conditional and unmeasured" because it never checked whether reasoners actually
produce the interval answer.

Two legs decide it:

  1. FORMAT. _ans_correct requires sorted(map(float, ans)) == sorted(map(float, gt)),
     i.e. a list of floats. An interval is not expressible in that format at all,
     so a reasoner that KNOWS the answer is x <= a has no way to say it.

  2. BEHAVIOUR. What do the repo's own reasoners actually return on an a==b probe,
     and how are they graded?

If every reasoner returns the single point, the defect is real but inert: the gt
is mathematically incomplete and nothing is mis-graded, because nothing can
express the completion. That is a materially weaker finding than P19 left open.

Read-only.
"""
import random
import sys

sys.path.insert(0, "harmonia/experiments")
from reasoning_phase0 import (REASONERS, _ans_correct,  # noqa: E402
                              gen_abs_extra_clean)


def degenerate_probes(seed=20260820):
    return [p for p in gen_abs_extra_clean(random.Random(seed))
            if p.data["a"] == p.data["b"]]


def main():
    deg = degenerate_probes()
    normal = [p for p in gen_abs_extra_clean(random.Random(20260820))
              if p.data["a"] != p.data["b"]]
    print(f"a==b probes: {len(deg)}   normal probes: {len(normal)}\n")

    print("what do the reasoners return on a==b, and how are they graded?")
    for name, fn in REASONERS.items():
        graded, answers = [], []
        for p in deg:
            try:
                ans, _ = fn(p)
            except Exception as e:
                answers.append(f"<raised {type(e).__name__}>")
                graded.append(False)
                continue
            answers.append(repr(ans))
            graded.append(bool(_ans_correct(p, ans)))
        uniq = sorted(set(answers))[:2]
        print(f"  {name:12s} correct {sum(graded):>2}/{len(deg)}   sample answers: {uniq}")

    print("\ncontrol — same reasoners on NORMAL (a<b) probes:")
    for name, fn in REASONERS.items():
        ok = 0
        for p in normal:
            try:
                ans, _ = fn(p)
                ok += bool(_ans_correct(p, ans))
            except Exception:
                pass
        print(f"  {name:12s} correct {ok:>3}/{len(normal)}")

    print("\nformat check — can the TRUE answer even be expressed?")
    p = deg[0]
    a = p.data["a"]
    for label, ans in (("single point (recorded gt)", [a]),
                       ("interval as string", ["x <= %d" % a]),
                       ("two sample members", [a - 1, a])):
        try:
            ok = _ans_correct(p, ans)
        except Exception as e:
            ok = f"<{type(e).__name__}>"
        print(f"  {label:28s} -> graded correct: {ok}")


if __name__ == "__main__":
    main()
