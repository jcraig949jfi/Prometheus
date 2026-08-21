# Loop Cycle 009 — 2026-08-21 (ran early: James asked "did you get this?" re round 3 restated)

**Answer: most of it landed in 008; four items were genuinely new and are now built
(11 new tests, suite 79 green).**

1. **Guarded product state** — their exact toy (b advances only when a_k == b_k). Sharper
   than cycle-008's arithmetic coupling because the coupling sits in the GUARD. Hand-traced
   chasing behaviour (0,0)->(1,2)->(2,2)->...->(6,6); NO fixed snapshot of A reproduces it.
2. **Symbolic held-out abstraction** — train 2a->2a+1, 2b, 2c; test a novel SYMBOL z and a
   novel compound (a+b). Stronger than held-out integers. Caught a real bug doing it:
   sympy's Wild SOLVES rather than matches ((3a).match(2t) succeeds with t=3a/2), which
   would have installed a rule from unsupporting evidence — the fake-synthesis failure this
   module exists to detect, nearly committed by the detector itself.
3. **Revisability (negative plasticity)** — invent -> evaluate -> revise/delete. Add-only
   system's degradation MEASURED (keeps a net-harmful operator past threshold).
4. **CLAIM v7: epistemic objective as the seventh coordinate.** Their strongest point, and
   it answers the exact question I had just sent them. Executable separation: identical
   unit-cost experiment pool, only the objective differs; info-greedy optimal on every
   instance (ceil log2|H| = 6 at |H|=64), myopic progress-greedy O(|H|) in expectation,
   worst case 63.

**Methodological finding (new, from building #4):** the separation is in EXPECTATION. The
myopic arm sometimes WINS per instance (truth=0 -> 1 step vs 6). A battery sampling one
instance per system can certify the wrong selector. This is the 4th instance of the
cheaper-mechanism law and the first where the cheaper mechanism can beat the better one on a
single draw — strengthening HITL #13's case for a doctrine memory.

**Their two-ceiling prediction, recorded:** operator plasticity is the Band-S ceiling;
epistemic objective is the Band-G ceiling, and the latter is more dangerous for
Prometheus-like research behaviour. Directly relevant: our batteries measure whether kills
happened, not whether the kills CHOSEN were the informative ones.
