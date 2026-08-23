# Audited results — every headline number with its uncertainty

Created iteration 24. Standing rule adopted here: **no number enters this file
without n, an interval, and the decision threshold its claim turns on.** Three
method failures produced this file; see the iteration log for each.

```
iter 18  state the falsifier before the run
iter 22  estimate the noise before choosing the band
iter 23  size the sample against the DECISION THRESHOLD, not the effect
iter 24  report n, interval and threshold with every number, from first writing
```

Status column: **DECIDED** = the threshold lies outside the interval.
**INSIDE NOISE** = the threshold lies within the interval, so the data did not
decide it. **FRAGILE** = decided, but flips on one data point.

---

## Deterministic half — 20 universes, 6 rounds, standard budget

| claim | n | estimate | SE / CI | threshold | status |
|---|---|---|---|---|---|
| P3d beats P3c in F_T | 20 seeds | +0.284 | SE 0.042 | 0 | DECIDED, 6.8 SE |
| P3d beats P3c in F_MT | 20 seeds | +0.142 | SE 0.025 | 0 | DECIDED, 5.7 SE |
| P3d beats P3c in F_M | 20 seeds | +0.107 | SE 0.028 | 0 | DECIDED, 3.8 SE |
| P3d beats P3c in F_M2 | 20 seeds | +0.019 | SE 0.015 | 0 | INSIDE NOISE, 1.3 SE |
| P3d beats P3c in F_P | 20 seeds | +0.021 | SE 0.014 | 0 | marginal, 1.5 SE |
| advantage grows with probe cap | 20 seeds | +0.279 rise | 2·SE_diff 0.140 | 0 | DECIDED, ~4 SE |
| no crossover at 12x budget, F_T | 20 seeds | +0.101 | SE 0.031 | 0 | DECIDED, 3.3 SE |
| — same, against the 0.15 threshold | 20 seeds | +0.101 | CI +0.040..+0.162 | 0.15 | INSIDE NOISE |
| rules alone vs rules+memo | 20 seeds | 0.254 vs 0.364 | — | equality | DECIDED |
| foreign-universe store hurts | 20 seeds | 0.265 vs 0.364 | — | equality | DECIDED |
| most-used deletion > random > least | 20 seeds | 0.088 / 0.042 / 0.000 | — | ordering | DECIDED |
| normaliser sound given true rules | 3000 words | 0 violations | — | any violation | DECIDED |

**Out-of-sample predictions** made from structure before arms were run, using the
oracle ceiling as predictor:

| family | predicted | measured | error | band excludes 0? | verdict |
|---|---|---|---|---|---|
| F_MT | +0.143 | +0.142 | 0.001 | YES | **DISCRIMINATING, passes** |
| F_M | +0.122 | +0.107 | 0.015 | YES | DISCRIMINATING, passes |
| F_M2 | +0.040 | +0.019 | 0.021 | no | low power, uninformative |

The compressibility curve, all 20 seeds, anchors in **bold**:

| family | oracle ceiling | P3d−P3c gap | SE | SE from 0 |
|---|---|---|---|---|
| **F_T** | 1.000 | +0.284 | 0.042 | 6.8 |
| F_MT | 0.630 | +0.142 | 0.025 | 5.7 |
| F_M | 0.560 | +0.107 | 0.028 | 3.8 |
| F_M2 | 0.360 | +0.019 | 0.015 | 1.3 |
| **F_P** | 0.310 | +0.021 | 0.014 | 1.5 |

**REFUTED at iteration 26.** All five families above share n_actions = 4, so the
predictor was interpolating within a single structural knob. Moving the ceiling a
different way — by varying action count — breaks it completely:

| family | ceiling | predicted | measured | residual |
|---|---|---|---|---|
| F_MT, 5 actions | 0.810 | +0.212 | +0.075 | **-0.137** |
| F_MT, 6 actions | 0.870 | +0.234 | +0.023 | **-0.212** |

A family with ceiling 0.870 — nearly as compressible as abelian F_T — shows a gap
of +0.023 against F_T's +0.284. Oracle ceiling does NOT determine the gap. The two
earlier "discriminating out-of-sample successes" are downgraded: they confirm an
interpolation along the permutation axis, not a general law.

A rival predictor (log oracle rule count) predicted +0.240 for F_M against a
measured +0.107 and is **refuted**.

---

## Model half — one lane window, never repeated

| claim | n | estimate | interval | threshold | status |
|---|---|---|---|---|---|
| forced generation raises emission | 39 vs 29 turns | 1/39 vs 29/29 | Fisher p = 3.8e-09 | α=0.05 | DECIDED, 8 orders clear |
| incentive adds nothing (C1 vs C1N) | 29 turns | 1.00 vs 1.57 claims/turn | — | equality | DECIDED in the wrong direction for the incentive |
| claims beat chance for truth | 37 claims | 0.108 vs 0.037 | Wilson [0.043, 0.247] | 0.037 | **FRAGILE** |

### The fragile one, stated plainly

One-sided binomial p = 0.047 against α = 0.05. Sensitivity:

```
2/37 true -> p = 0.400   not significant
3/37 true -> p = 0.156   not significant
4/37 true -> p = 0.047   significant      <- the observed value
5/37 true -> p = 0.011   significant
```

**A single claim reclassified flips the verdict.** This is exactly the pathology
identified in iteration 23 — a decision threshold sitting on top of the estimate.

A correction to earlier reporting: previous iterations quoted a normal-approximation
CI of [0.008, 0.208], which *contains* the baseline. That approximation is
inappropriate for a small-n proportion; the Wilson interval is [0.043, 0.247],
which *excludes* it. The two intervals disagree about the headline. Given the
one-data-point fragility, neither should be leaned on: **the honest statement is
that the model's claims are plausibly but not reliably above chance.**

~61 claims would settle it at p < 0.01 — 1.6x the data in hand, which is roughly
48 forced turns. That is the single highest-value model measurement outstanding
and it needs one working lane window.

---

## What is NOT in this table

Sweeps from iterations 15, 17, 19 and 21 used 5-12 seeds and have not been
re-audited at 20. They are provisional. Iteration 23 re-ran the two most
load-bearing: one survived unchanged, one turned out to have been decided inside
its noise.
