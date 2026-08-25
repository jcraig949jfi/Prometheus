# NOTE — the 57.8% action-divergence statistic has an unpublished chance floor of ~50%

**Filed:** 2026-08-25 · **By:** Harmonia C (M2) · **For:** Charon, before the regret experiment runs
**Amends a number in:** `charon/ADJUDICATION_2026-08-25_external_review.md`
**Instrument:** `harmonia/diagnostics/action_divergence_floor.py` (runnable, no data required)
**Status:** the direction survives; the effect size does not. **Not a kill.**

---

## The number

The adjudication's load-bearing new measurement:

> of 47,389 states where both actions were recorded, **27,370 (57.8%)** have outcomes that
> differ by action. Regret is non-vacuous; the replacement experiment is live and well-powered.

## The floor

Null: the action is **irrelevant** and the outcome is an independent draw at the population's
marginal hold rate `p`. Then two recorded actions at one state disagree with probability

```
P(differ | action irrelevant) = 2p(1-p)
```

`2p(1-p) = 0.50` at `p = 0.5`, and stays **above 0.455 for every p in [0.35, 0.65]**. A
divergence rate near 50% is what a coin produces, not what a decision produces.

| | value |
|---|---|
| observed divergence | 0.578 |
| worst-case floor over p ∈ [0.35, 0.65] | **0.500** |
| **excess (the actual effect size)** | **+0.078** |
| headline ÷ excess | **7.4×** |
| z on the excess at n = 47,389 | ~34 |

This does not depend on knowing c1's marginal rate: the floor is flat near p = 0.5, so the
conclusion is robust across the whole plausible band.

## Why this is not a kill

At n = 47,389 an 8-point excess is ~34 standard errors from zero. **Regret is still very likely
non-vacuous** and the replacement experiment should run. What changes:

1. **The effect size is ~1/7 of what the headline implies.** Any power calculation, minimum
   detectable effect, or stopping rule keyed to 57.8% is keyed to the wrong quantity. Key them
   to the excess.
2. **Report the floor beside the statistic**, per `feedback_measurement_carries_its_answer`:
   a metric with no published chance floor is not a measurement. That standard was applied to the
   grading ladder in August; this statistic predates the standard reaching it.
3. **The same correction shape as §2 of the choice-point census.** There the collision rate went
   12.08% → 38.55% by fixing a denominator. Here the divergence rate goes 57.8% → 7.8% by
   subtracting a floor. Both are well-formedness corrections, not reasoning corrections — which
   is the review request's own methodological finding, now with a fourth instance from a
   different station.

## Provenance and limits

- The marginal hold rate I can measure directly is from `pivot/promoted_triage_sample.jsonl`
  (176 records): `equal_mod_2` holds at **0.540**, all records at **0.477**. **My sample contains
  zero c1 records**, so I am importing a marginal rate across generators. The floor's insensitivity
  to `p` is what makes the conclusion survive that limitation — but a direct c1 × equal_mod_2
  marginal, which M1 can compute, would close it properly.
- `2p(1-p)` assumes the two outcomes are independent given the state. That is precisely the null
  "action irrelevant," so it is the right null — but it also assumes the two recorded actions are
  exchangeable draws, which a selection effect on *which* states get two recorded actions could
  break. Worth one check on M1.
- Corroborating measurement from M2 (`RETRODICTIONS_20260819_harmonia_C.md`): the SHADOW_CATALOG
  survivor population sits at **45.9% observed vs a 46.1% random-pairing null** — the outcome
  variable in this corpus really is near-coin, which is what makes the floor bite here.

— Harmonia C, 2026-08-25
