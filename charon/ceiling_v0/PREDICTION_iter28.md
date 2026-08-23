# Pre-registered prediction — iteration 28. THE ONE PERMITTED CONFIRMATORY TEST.

## Standing decision
Iteration 27 established causally that ENLARGING the candidate pool halves P3d's
advantage (+0.284 -> +0.129) with the arena algebra untouched. The binary decision
recorded before that run permits exactly ONE confirmatory experiment. Whatever
happens here, mechanism search in ceiling_v0 TERMINATES afterwards and effort
redirects to the model lane.

## The test — the reverse direction, in the arena where the gap collapsed
At 6 actions the advantage collapsed to +0.023 despite an oracle ceiling of 0.870
(nearly as compressible as abelian F_T at 1.000). If candidate burden is the
operative variable, then REDUCING burden there should RESTORE some advantage.

Lever: `sig_depth=1`. A candidate is admitted only if its two words agree on all
tags AND on every observed one-step continuation. Strictly stronger evidence, so a
smaller and purer pool. No arena change, no extra interactions — it reuses
observations already paid for.

This is an ORTHOGONAL intervention to iteration 27's: that one loosened admission
in a 4-action arena, this one tightens it in a 6-action arena, in the opposite
direction, in the regime where the effect was absent.

## Prediction
  P1. Pool size falls at sig_depth=1 versus sig_depth=0 in the 6-action arena.
  P2. The P3d-P3c gap RISES from its collapsed +0.023 by more than 2 SE of the
      difference (SE per condition ~0.01-0.03, so a rise of roughly >0.06).

## Falsifiers
  F1. The gap does not rise by more than 2 SE. Candidate burden is then NOT
      sufficient to explain the cross-arena divergence. Mechanism is reported
      UNRESOLVED and the search ends.
  F2. Pool size does not fall — the lever failed to do what it claims, and the
      test is void rather than informative.

---

## VERDICT — F1 fires, BUT THE INSTRUMENT WAS DEGENERATE

```
arena                sig_depth  pool    P3c    P3d      gap     SE
F_MT 6 actions               0   122  0.276  0.299   +0.023  0.009
F_MT 6 actions               1     0  0.275  0.275   +0.000  0.000
F_T 4 actions (control)      0   124  0.364  0.647   +0.284  0.042
F_T 4 actions (control)      1     1  0.249  0.249   +0.000  0.005
```

Requiring agreement on EVERY observed one-step continuation is so strict that at
this observation density essentially no candidate qualifies. The pool went to
zero, both arms acquired nothing, and both scored fallback.

**The control settles the interpretation.** F_T's advantage also collapsed,
+0.284 -> +0.000. A valid graded burden-reducer would have preserved or increased
it. The lever destroyed the pool rather than shrinking it, so this is a VOID TEST,
not evidence against candidate burden.

F1 fired by the letter of the pre-registration, so the stopping rule is honoured:
mechanism search in ceiling_v0 ENDS and mechanism is reported UNRESOLVED. That is
"the question was not answered", NOT "burden was refuted". Iteration 27's positive
result stands on its own: enlarging the pool causally halves the advantage.
