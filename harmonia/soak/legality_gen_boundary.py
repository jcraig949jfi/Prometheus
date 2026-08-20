"""Two-part test of SOAK-38 (Harmonia-A soak P19).

NOTE (P19 self-audit, 5th of this soak): my first draft read p.answer; the
Probe field is ground_truth. Corrected before drawing any conclusion.

SOAK-38 claims every harness defect this soak found sits at the same structural
position: a guard that handles the anticipated failure and is silent about the
adjacent unanticipated one. It is a spanning claim at N=4, and every spanning
claim of mine that has been tested has needed narrowing.

But SOAK-38 has a sharper problem than being unverified: it may describe WHERE I
AIM rather than where defects are. I only find adjacent-to-guard defects because
that is the only place I probe. So this pass has a CONTROL.

  PART 1 (adjacent to a guard): gen_abs_extra_clean guarantees a<=b so that a
      root always exists. The boundary of that guard is a==b, reachable since
      b = a + rng.randint(0, 8). At a==b the equation |x-a| = b-x becomes
      |x-a| = a-x, satisfied by EVERY x <= a -- a half-line, not a point --
      while gt is recorded as the single root [(a+b)/2].

  PART 2 (NOT adjacent to any guard): determinism under a fixed seed. Nothing in
      the suite guards it and it is a different axis entirely. If a defect turns
      up here, SOAK-38's "one shape" is refuted; if nothing does, the claim stays
      confounded with my own aim and cannot be promoted.

Read-only w.r.t. the repo.
"""
import random
import sys

sys.path.insert(0, "harmonia/experiments")
import sympy as sp  # noqa: E402
from reasoning_phase0 import gen_abs_extra_clean, gen_log_extra_3arg  # noqa: E402

x = sp.Symbol("x", real=True)

print("=== PART 1 — adjacent to the a<=b guard: is a==b reachable, and sound? ===")
probes = gen_abs_extra_clean(random.Random(20260820))
deg = [p for p in probes if p.data["a"] == p.data["b"]]
print(f"  probes generated: {len(probes)}   with a==b: {len(deg)}")
if deg:
    p = deg[0]
    a, b = p.data["a"], p.data["b"]
    sol = sp.solveset(sp.Eq(sp.Abs(x - a), b - x), x, domain=sp.S.Reals)
    print(f"  example a={a} b={b}: recorded gt = {p.ground_truth}")
    print(f"    true solution set = {sol}")
    print(f"    gt is the COMPLETE solution set: {sol == sp.FiniteSet(*p.ground_truth)}")

print("\n=== PART 2 — CONTROL, not adjacent to any guard: determinism ===")
for name, gen in (("gen_abs_extra_clean", gen_abs_extra_clean),
                  ("gen_log_extra_3arg", gen_log_extra_3arg)):
    r1 = [(q.kind, tuple(sorted(q.data.items())), tuple(q.ground_truth)) for q in gen(random.Random(7))]
    r2 = [(q.kind, tuple(sorted(q.data.items())), tuple(q.ground_truth)) for q in gen(random.Random(7))]
    print(f"  {name:22s} same seed -> identical output: {r1 == r2}  (n={len(r1)})")
