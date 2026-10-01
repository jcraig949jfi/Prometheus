# W2-37: F\* K1 frozen test — PASSED (weak)

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **Key files:** `PREREG.md`, `a1_analysis.json`, `e0_eligibility.json`, `v1_validate.json`, scripts, logs.
> - **Compute:** about 50 CPU-min. The run exited by itself; nothing was killed.

## Answer
**K1 is PASSED.** This is the **first frozen pass on any F\* kill criterion**, and it is a weak one.

On fresh seeds, FIELD BANK − FREE BANK on R2 = P(maxA ≥ 40 and B ≥ 27) at 300 epochs has a 95% Newcombe CI wholly inside ±0.05, under both censoring treatments:

| treatment | Δ | 95% CI |
|---|---|---|
| C− | +0.004 | [−0.014, +0.025] |
| C+ | −0.023 | [−0.043, −0.001] |

**Order of events:**
- freeze commit 32135ddc5 at 02:36:39Z;
- PREREG written at 02:39:27Z;
- data generated from 02:40Z.

**Scope:** BASE, 7ae3, one background bank. This is one passed instance, not a pass of F\*.

**The brief was wrong that the 256-cap does not affect R2.** 33 of 68 FREE cap256 stops had B < 27 when they stopped, so their B ≥ 27 status is censored. PREREG therefore scored R2 both ways: C− counts these as 0, C+ counts them as 1.

## Eligibility
- **Seeds:** 9_998_000 + s.
  - FIELD: s = 50000..50599 (n = 600).
  - FREE: s = 50000..51199 (n = 1200).
  - Disjoint from X-TICKET, W2-14, W2-22, W2-29 and the neighbouring campaign seed bases.
- **Sample size and power:**
  - The normal approximation needs n ≥ 232 per arm.
  - At 230/230, P(pass under both treatments) is only 0.10, which is effectively ineligible.
  - At 600/1200, expected half-widths are 0.019 (C−) and 0.021 (C+), P(pass under both) = 0.85, and P(kill) ≈ 0.
- **CI method:** fixed in advance as Newcombe method 10 (hybrid score). It reproduces Newcombe's worked examples.
- **Validation:** 15/15 checks match.
  - `run2(stop="orig")` = `ffield.run`.
  - `run2(stop="xk")` reproduces W2-22's records.
  - The imported files are clean against HEAD, with sha256 recorded in PREREG.

## Results

| readout | FIELD | FREE C− | FREE C+ | Δ C− | Δ C+ |
|---|---|---|---|---|---|
| **R2 (K1)** | 24/600 = 0.040 | 43/1200 = 0.036 | 76/1200 = 0.063 | **+0.004 [−0.014, +0.025]** | **−0.023 [−0.043, −0.001]** |
| R1 (descriptive) | 25/600 = 0.042 | 50/1200 = 0.042 | 83/1200 = 0.069 | 0.000 [−0.019, +0.022] | −0.028 [−0.048, −0.004] |
| R3 (descriptive) | 6/25 = 0.24 | 10/50 = 0.20 | 35/83 = 0.42 | +0.04 [−0.14, +0.25] | −0.18 [−0.35, +0.04] |

- **R3 on B, C−:** FIELD 12/27 = 0.44 vs FREE 10/50 = 0.20. Kin re-conversions make up 39.5% of FIELD's B, so they inflate the B-based readout but not the B_xk-based one.
- **Label floods** (maxA ≥ 40 with B < 27): FIELD 26/50, FREE 42/85.
- **Stop reasons:** FIELD frozen 410 / extinct 152 / horizon 32 / runaway 6; FREE frozen 837 / extinct 295 / cap256 68.
- **W2-22 re-scored with the same rule** (consistency only; its data predate the freeze): C− +0.001 [−0.017, +0.022]; C+ −0.020 [−0.039, +0.002].

## Adversarial round
1. **The absolute ±0.05 tolerance is coarse against a base rate of about 0.04.** The Katz ratio CI is about [0.68, 1.82] (C−) and [0.40, 0.99] (C+). A FIELD rate of 0 would also have passed. This is a weakness of the frozen rule, not of the execution.
2. **Under C+, FREE is significantly higher than FIELD** (−0.023, CI excludes 0). Density or kin may lower R2 by about 2 points: inside tolerance, but possibly real.
3. **Censoring is about 2.75% of FREE**, comparable in size to R2 itself. The verdict holds under both extremes.
4. **The "frozen" stop rule** is shared by both arms and is part of M\*.
5. **One bank realization** was used.
6. **Scope:** one genotype, one cell, BASE only.
7. **K1 doesn't put much at risk:** FIELD BANK vs M\* is rung 4 vs rung 3. K4 remains the live threat.
8. **Process integrity:** one pre-specified analysis, with no interim looks.

## Ledger entry (W2-37)
- **Inference:**
  - K1 is PASSED at the frozen tolerance for this cell, the first frozen pass of F\*.
  - On the absolute R2 scale, kin plus density do not move the rate by more than 0.05.
- **Confidence:**
  - high that the rule-defined verdict holds;
  - low to moderate that kin and density are negligible in relative terms (ratio about 0.4–1.8).
- **Strongest objection:** the absolute tolerance cannot detect a relative effect of up to about 2x, and there is a small significant FIELD deficit under C+.
- **Next:**
  - Freeze a log-ratio companion tolerance.
  - Run FREE with the cap lifted, as an M\* variant.
  - Repeat on a second bank and under ATOMIC.
  - Prioritize K4.
