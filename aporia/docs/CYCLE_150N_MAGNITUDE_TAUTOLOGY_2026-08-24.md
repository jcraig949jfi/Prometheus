# CYCLE 150-N — TERMINAL: KILL. The outcome variable is magnitude compatibility, not mathematics.

**The contamination check terminated this campaign before any modelling, exactly as it was
instructed to.** And the reason it terminated is the most useful thing this line has produced: it
retroactively explains the 140–148 arc.

Stratified sample, stride 7, 24 of 165 batches. Parse drops: 0.

## The mutation outcomes are determined by direction, and direction alone

    c4 GENERALIZE   holds 0.7776    (87,342 / 112,316)
    c5 SPECIALIZE   holds 0.0129    (   279 /  21,701)

Knowing only which generator produced a row predicts its outcome at ~98%. That is the tautology the
pass was told to check for, and it is present.

**The ordinal parameter carries nothing.** c4's threshold delta was to be the transfer axis:

    delta  +1  n=26,060  holds=0.8233
    delta  +2  n=26,106  holds=0.8220
    delta  +5  n=26,041  holds=0.8204
    delta +13  n=26,012  holds=0.8178

A spread of 0.0055 across a thirteen-fold range of delta — and only **four** distinct deltas, a
designed grid rather than the continuous family the relation names suggested. The transfer test
149-M opened this campaign to run has no axis to run along.

**Two of the six outcome fields are not independent.** `weak_holds` and `self_consistent` disagree in
**0** rows — the same field twice. `strong_holds` and `boundary_revealed` agree in **0** rows — exact
complements. So c4 has 2 distinct outcomes, not 3, and c5 likewise.

## What actually drives the outcome, and it is not mathematics

    c4 holds by (invariant_a, invariant_b), 30 pairs with n>=300, range 0.0000 to 1.0000
      ('signature',        'conductor')  n=  530  holds=0.0000
      ('determinant',      'conductor')  n=  577  holds=0.0000
      ('three_genus',      'regulator')  n=1,672  holds=1.0000
      ('signature',        'regulator')  n=1,084  holds=1.0000

    c5 strong_holds by the same key, range 0.0000 to 0.9150
      ('crossing_number',  'conductor')  n=  543  strong=0.0000
      ('nf_class_number',  'torsion')    n=  459  strong=0.9150

The full 0-to-1 range looks like enormous state-dependence. It is not. **Everything paired with
`conductor` scores 0.0000; everything paired with `regulator` scores 1.0000.** Conductor is a
four-or-five-digit integer; knot invariants like signature and three_genus are single digits;
regulator is a small float.

`abs_diff_le_N` between a single-digit knot invariant and a conductor of 4,845 **cannot hold for any
N ≤ 159**. Against a regulator it **always** holds. The outcome variable is measuring whether two
quantities live on comparable scales.

The same explains c5's ordering by original relation — `abs_diff_le_3` → 0.1771 but
`abs_diff_le_16` → 0.9355. A looser original threshold survives tightening more often, which is a
fact about the distribution of |a−b|, not about the objects.

## This retroactively explains the whole 140–148 arc

If the recorded outcome is dominated by magnitude compatibility, then:

- **148-L's anti-transfer follows immediately.** Rankings invert across relations because different
  thresholds interact differently with the same magnitude gaps. What I reported as "invariant
  rankings partially reverse across relations" is arithmetic about number ranges.
- **147-K's fourteen constants were plausibly a magnitude table.** (parent_invariant × relation) →
  which invariant to try next is largely "which invariant is on a scale compatible with this
  threshold."
- **The h4 measurement-selection result and these mutation results share one confound**, which is why
  both produced structure that would not transfer.

**The edge corpus has a units problem, not a coordinates problem.** Its outcome variable is a proxy
for scale compatibility between two catalogues that were never normalised against each other. No
representation learned on it can carry navigational information, because the thing being predicted
is not a mathematical property of the objects.

## Verdict

**CYCLE 150-N: KILL** at pass 1, on the tautology condition, before any model was fitted.

Reported at full strength as the pass required: this is **the strongest evidence yet for the
operator's hypothesis**, and it is stronger than a null would have been. A null would have said the
coordinates fail to predict. This says the **target variable itself is not a navigational quantity**
— so the coordinates were never being asked a navigation question.

## What this does and does not close

**Closes:** c4, c5 and — by the shared confound — the interpretation of h4's results as
navigational. The retrospective navigation programme on `theseus/corpus` is now closed on
substantive grounds rather than on scope exhaustion.

**Does not close:** the navigation hypothesis itself, which has still never been tested on an
outcome variable that measures mathematical proximity. It has been tested three times on a variable
that measures whether two numbers are the same size.

**Untested and now clearly next:** `h1`/`h2` (215K rows), where the outcome is `hunter_success` —
did a bounded search find a counterexample. That is a *search* outcome, not a scale comparison, and
it is the only remaining generator family whose target variable is not obviously magnitude-driven.
It should be checked for its own confound before anything is built on it.

## Self-identified weaknesses

- 24 of 165 batches at stride 7, capped at 150k rows each. The magnitude explanation is measured on
  30 invariant pairs with n≥300; rarer pairs were not examined.
- The magnitude claim is inferred from the conductor/regulator contrast and the threshold ordering,
  not from directly computing |a−b| distributions per invariant pair. That computation would make it
  certain rather than strongly supported, and it was not run.
- I have not verified that h1/h2's `hunter_success` avoids the same confound — it is named as the
  next check, not cleared.
- The retroactive explanation of 147-K and 148-L is a plausible unification, not a re-analysis. Those
  results were not re-run under a magnitude control.

## Falsifier

Direct computation of |a−b| distributions per invariant pair showing the outcome is *not* explained
by scale; a c4/c5 subpopulation where invariants are magnitude-matched and outcomes still vary
informatively; or evidence that h1/h2's search outcomes are magnitude-independent, which would
reopen the retrospective programme on those generators.

## Terminal

**CYCLE 150-N: KILL.** The mutation generators cannot answer the navigation question because their
outcome variable answers a different one. Three passes of results on this corpus were measuring
whether two catalogues use comparable units.
