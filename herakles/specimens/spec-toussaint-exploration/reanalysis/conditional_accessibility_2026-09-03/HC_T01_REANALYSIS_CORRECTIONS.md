# HC-T01 REANALYSIS CORRECTIONS

**Annotations, not rewrites.** Every original HC-T01 document is left intact.
This file records what the RA pass and the upstream Lexis adjudication change
about how those documents should be read.

---

## 1. Corrections propagated from Lexis

Recorded here as received from `roles/Lexis/archaeology/hct01_prior_art_2026-09-03/`.
This seat did not re-verify them and does not claim to have.

- **Misevic, Ofria and Lenski 2006** is prior art for five of six headline cells
  and was absent from the original HC-T01 descendants population.
- **Kumawat et al. 2024** supplies the within-run acquisition shape and is also
  five of six.
- **Petak 2025 DOES contain a variation-regime intervention.** The HC-R01 packet
  and the HC-R01 registry row both describe it as having no operator-side
  intervention. That description is wrong and is corrected here.
- **The prior missing-cell justification for HC-T01 is obsolete.** It had already
  been downgraded once to a rigour cell; it is now superseded outright.
- **A Kouvaris reconstruction is NOT required as calibration.**
- **K7's original marginal-statistic interpretation was under adjudication** by
  this pass. See section 3.

### The narrow truth about prior art, stated as Lexis framed it

Not "HC-T01 was already published". Not "HC-T01 was historically novel". The
accurate statement is:

> the exact intersection appears unoccupied in the surveyed literature, but
> essentially all constituent design ideas were already demonstrated in closely
> adjacent published systems.

---

## 2. What this pass confirms about the hazards

**H-2, the ceiling-bounded outcome, is confirmed numerically and it is worse than
argued.** At the original K7 window `alpha=0.03, beta=0.1, 100 -> 500`, the
Spearman between current fitness and subsequent gain is **exactly -1.0000**, and
`1 - r^2 = 0.00000`. Gain is a perfect deterministic rank function of current
fitness there. No conditional statistic exists at that point; the partial is
undefined rather than small.

Saturation is also asymmetric across exactly the arms HC-T01 compared. By
generation 80, 63 per cent of `alpha=0.06, beta=0.1` runs are already at the
optimum, against 0 per cent of `beta=0.0` runs.

**H-3, machinery presence, is confirmed as a hard structural fact.** `nops` is
identically zero in every `beta=0.0` row at every generation, fraction zero
1.000.

---

## 3. What this pass changes about K7

The original K7 finding stands as an accurate description of a marginal
comparison. This pass reproduced it exactly from the same frozen rows: current
best fitness at -1.000 for both alphas over the 100 to 500 window, avgfit -0.975
and -0.750, modular degree -0.950 and -0.765.

What changes is the **interpretation**. K7 was read as evidence that
accessibility carries no prospective information beyond current fitness. That
reading is not supported, because at the windows where it was computed the
outcome was a deterministic function of the conditioner, so the comparison could
not have come out any other way.

**But the adjudication does NOT rescue the accessibility claim either.** The
preregistered conditional test returns `RA1_INDETERMINATE` for both treated
cells. The correct statement is:

> K7's original marginal comparison cannot support the conclusion that was drawn
> from it, and the frozen rows cannot support the corrected conditional test
> either. The question is unanswered in this substrate, not answered either way.

---

## 4. What this pass changes about CP-REPRESENTATION-REWRITE

RA-2 returns `RA2_MACHINERY_COUNT_EXPLAINS_EFFECT` in both treated cells, and the
mechanism is a step rather than a gradient. Mean modular degree by operator
count, `alpha=0.03, beta=0.1`:

    nops bin    n     mean md_on
    0          284         0.341
    1          185         2.730
    2          123         3.092
    3           90         3.172
    4           43         3.161
    5           14         3.167

Going from no operator to one operator moves the detector by 2.39. Every
subsequent operator together moves it by 0.44. The unconditional generation trend
of +0.786 falls to a mean absolute within-stratum trend of +0.291, and `nops`
alone accounts for a rank R-squared of 0.739.

**Consequence, applying the prompt's own instruction.** Language of the form
"evolved reorganisation of the generator" or "history changed machinery
organisation" is not supported by these rows. The defensible statement concerns
ACCUMULATED MACHINERY, and more precisely its PRESENCE:

> in the Toussaint substrate the accessibility detector is largely reading
> whether the genome contains at least one production rule.

`CP-REPRESENTATION-REWRITE` is downgraded accordingly. It was already
Toussaint-specific and unpromoted; it now additionally carries the finding that
its own substrate's detector response is dominated by machinery presence.

One honest limitation on that conclusion: `nops` in these rows is a POPULATION
MEAN, not an integer per-genome count, so the integer bins conflate populations
with differing operator composition. The floor-0 bin in particular contains
populations averaging anywhere in [0, 1) operators, which is why a residual
generation trend of +0.65 survives inside it.

---

## 5. What is NOT changed

The durable HC-T01 result is untouched by this pass: evolutionary history changed
the measured local accessibility, at 24 to 108 times the estimator noise, while
the contemporaneous mechanical effect of the operator knob was at or below that
noise. RA-2 explains a large part of WHY the accessibility differed. It does not
make the difference unreal, and it does not touch the mechanical-null result.

The HC-T01 verdict of `HC_T01_WEAK_SIGNAL_ONLY` is unchanged by this pass.
`RA1_INDETERMINATE` provides no basis for an upgrade, and the prompt is explicit
that an upgrade requires `RA1_CONDITIONAL_SIGNAL_SURVIVES`.
