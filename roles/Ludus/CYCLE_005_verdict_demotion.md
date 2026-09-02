# Cycle 005 — the cycle 004 verdict is DEMOTED

**Date:** 2026-08-27. **Prompted by:** external review, point 1 (support vs context).
**Data:** `ludus/atlas/cycle005_occupancy.json`. **Zero model calls, all quantities exact.**

## What the review claimed

`E_ijk` is an on-policy outcome, so it measures **exposure x conditional competence** as a product.
Cycle 004 attributed the whole `circuit x world` term to competence. It may be exposure: a circuit
can implement an identical computation everywhere and still show world-dependent value if worlds
differ in how consequential their decision states are.

## The test

Per-decision regret against the OPTIMAL continuation, which is partner-free by construction:

```
best(s)   = max(pot(s), V(s))
chosen(s) = pot(s) if the circuit stops, else V(s)
regret(s) = (best(s) - chosen(s)) / EV*
```

decomposed circuit x world under three state weightings.

## Result

```
REAL (reconstructed worlds)          circuit    world    circuit x world
  REFERENCE occupancy (common dist)   0.8528    0.0451       0.1021
  SELF occupancy (circular)           0.7409    0.0301       0.2289
  UNWEIGHTED (all states equal)       0.2623    0.1155       0.6222
  DISAGREEMENT rate                   0.2530    0.0564       0.6906

FOUNDRY
  REFERENCE occupancy (common dist)   0.7313    0.1039       0.1648
  SELF occupancy (circular)           0.7337    0.0455       0.2208
  UNWEIGHTED (all states equal)       0.5718    0.0900       0.3382
  DISAGREEMENT rate                   0.7701    0.0308       0.1992

for comparison, cycle 004 on-policy E_ijk (real):
  circuit 0.2126   world 0.0696   circuit x world 0.4374
```

**Under a common reference distribution of decision states, the circuit main effect dominates
(0.8528) and `circuit x world` collapses to 0.1021.** Cycle 004 measured 0.2126 / 0.4374 on the same
worlds. The review was right: a large part of what was called contextual competence was
**support mismatch**.

## VERDICT DEMOTED

`CONTEXTUAL_BASIS_REQUIRED` (cycle 004) is **DEMOTED to CHALLENGED-AND-NOT-SUSTAINED.** It is not
deleted and the cycle 004 document is not rewritten; the fossil discipline applies to verdicts as
well as to circuits.

Replacement, registered now with its own kill condition:

> **`EXPOSURE_CONFOUNDED_HETEROGENEITY`** — circuit performance varies far more by world than by
> partner on-policy, but most of that variation is attributable to differences in which decision
> states each world presents, not to world-dependent competence. Under a common reference
> distribution, circuits behave substantially like stable primitives.
>
> **Kill condition:** if a common-reference decomposition on any set of >= 4 worlds returns
> `circuit x world > circuit`, this class is wrong and contextual dependence returns.

## The finding underneath, which is sharper than either verdict

**The verdict is determined by the choice of state weighting**, and the three weightings disagree
violently: 0.1021 / 0.2289 / 0.6222 for the same circuits on the same worlds.

Two of the three are defective in opposite directions, and it is worth naming both:
- **self-occupancy is circular** — it weights states the circuit steered itself into, which are
  disproportionately states it handles well;
- **uniform is the cycle-001 defect in mirror image** — it counts states no competent play ever
  reaches, exactly as uniform sampling once inflated a reading from 0.412 to 0.900.

Reference occupancy under optimal play is the defensible one, and it is the weighting this bench
adopted in cycles 002-003 and then failed to apply to its own basis audit.

**The residual structure is real and now precisely located.** Compare the last two rows of the real
block: the DISAGREEMENT rate is strongly world-conditional (`circuit x world` = 0.6906) while the
reference-weighted VALUE COST is not (0.1021). So:

> **Where** a circuit is wrong is world-conditional. **How much its errors cost, where competent play
> actually goes,** is largely circuit-determined.

That is a more useful statement than either "circuits are primitives" or "circuits are contextual",
and neither cycle 004 nor the review stated it.

## What also changed

Cycle 004 wrote *"what survives is rank, not magnitude"* on the strength of a cross-PARTNER Kendall
tau of 0.9721. The cross-WORLD rank matrix was never computed. It has now been:

```
                      mean tau    min tau    negative pairs
REAL (reconstructed)   +0.1079    -0.5556       3 of 6
FOUNDRY                +0.7981    -0.1111       2 of 120
```

Across real worlds **rank does not survive either** — half the world pairs are negatively correlated.
That sentence in cycle 004 is wrong as applied to worlds and is corrected here rather than edited
there.

It also instantiates the review's point 7 concretely: FOUNDRY says worlds *rescale* (0.80), the
reconstructed worlds say worlds *reorder* (0.11). The synthetic block would have misled us.

## Consequences

1. **`r_i(W)` is NOT built.** The evidence that motivated it has been substantially explained away.
   Building it now would be responding to an artifact by making the representation more elaborate.
2. **The world-property registry is deferred**, for the same reason. `w0001` still has zero
   confirmatory evidence outside the world that produced it.
3. **On-policy retention is retained but demoted to a secondary estimand.** Reference-weighted
   conditional regret becomes primary: it separates the two things `E_ijk` fuses.
4. **The review's four-arm learning-cost design is adopted** over the seat's two-arm proposal, with
   `D must beat C` as the decisive criterion.
5. **"Real worlds" are relabelled "reconstructed named worlds" throughout** until rules are audited.
