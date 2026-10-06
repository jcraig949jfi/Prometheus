# AETH-V2B-ER01 RESULT: energy-regime generality of the frozen medium

Order: roles/Aether/prompts/2026-10-05_er01. Seat Aether[m2-95eba442], SPECTREX5 (M2), RTX 5060 Ti 16 GB.
Preregistration frozen at 7ce2a58b9 (PREREGISTRATION.md, RULES.json, production/plan.json; hashes re-verified
before reduction). Production 2026-10-05 11:30:37Z - 20:33:17Z (32,561 s = 9.04 h; predicted 9.13 h).
Reduction: production/REDUCTION.json (er01_reduce.v2, rules sha256 57e138b0...).

## Technical disposition: PASS
- 38/38 units rc=0. None was re-run or terminated. No new unit was started after the cap, and the cap was never
  approached.
- Gates:
  - continuity: R0 P1 frozen_net64 median 0.92589, inside [0.90, 0.95]. The historical exact value is 0.92592
    at 256^2.
  - determinism: dup_R0P0_s0 matches its original bit-for-bit (final digest and the full 1000-bin series).
  - one regime_table_hash: 3a340a210f8a8165.
- Kernel: aeth01.v1, frozen CuPy kernel, unmodified. Conformance to the independent NumPy text was verified at
  every regime and both arms, to 5000 ticks.
- GPU stayed 70 C / 91% / 2782 MHz throughout. VRAM 240-248 MiB per unit; host RSS ~405 MiB per process.
  Evidence: 21 MB, 41 files.

## Scientific disposition (preregistered rules): MOBILE_BUT_TRIVIAL
- R1 C_free_compute: MOBILE_BUT_TRIVIAL.
- R2 rich_rain_x2: MOBILE_BUT_TRIVIAL.
- R3 scarce_rain_half: NOT_MOBILE.

Both R1 and R2 pass the mobility screen. Late turnover is 3.14x and 2.48x R0, in 8/8 paired seeds, and is
sustained (persistence 1.000). Both then fall to the cheap attack on two counts:
- **low novelty**: 0.000 and 0.001 of late changes reach a template state the site had not held within the
  previous 16 ticks;
- **spatial confinement**: the paired change in the late frozen fraction vs R0 is -0.0015 and -0.000003,
  against a required -0.05.

In words: energy changes how OFTEN the same small set of sites flips. It does not change WHICH or HOW MUCH of the
medium is rewritten, and the extra flips return to recently held states.

Read alongside the order's semantic definitions, the result is closest to REGIME_ROBUST_FROZEN in substance:
- the extent of the frozen medium is energy-invariant;
- the differences are in rate, i.e. quantitative.

It is reported under the preregistered label MOBILE_BUT_TRIVIAL because the rate rule fired. That label is not
softened here.

## Primary table (P0, 1024^2, 50,000 ticks, 8 paired seeds; medians [min, max])

| | R0 B_balanced | R1 free_compute | R2 rain x2 | R3 rain /2 |
|---|---|---|---|---|
| inflow /site/tick | 1.0 | 0 (no costs) | 2.0 | 0.5 |
| late turnover (sites/tick) | 0.002393 [.002365,.002411] | 0.007523 [.007391,.007570] | 0.005918 [.005856,.005960] | 0.000984 [.000973,.000992] |
| paired ratio vs R0 | 1 | 3.14 (3.12-3.17) | 2.48 (2.47-2.48) | 0.41 (0.41-0.41) |
| frozen_strict, last 2000 ticks | 0.9880 | 0.9865 | 0.9880 | 0.9880 |
| frozen_net64 (historical def.) | 0.9942 | 0.9940 | 0.9940 | 0.9941 |
| ever changed by tick 50,000 | 0.3733 | 0.3736 | 0.3733 | 0.3732 |
| persistence (last 10% / 50-60%) | 1.000 | 1.000 | 1.000 | 1.000 |
| t_quiesce (ticks) | 150 | 100 | 100 | 175 |
| active WRITE density (late) | 0.202 | 0.442 | 0.374 | 0.101 |
| starved WRITE density (late) | 0.240 | 0 | 0.067 | 0.340 |
| final energy mean / median | 80.3 / 36 | 122.7 / 123 | 189.4 / 248 | 6.0 / 0 |
| zero-energy fraction | 0.247 | 0.100 | 0.067 | 0.598 |
| rain events /site/tick | 0.125 | 0 | 0.25 | 0.0625 |
| starve = revive events /site/tick | 0.0311 | 0 | 0.0175 | 0.0229 |
| novel-change fraction (attack) | 0.077 | 0.000 | 0.001 | 0.280 |
| periodic p<=16 (attack) | 0.000 | 0.110 | 0.001 | 0.000 |
| max field share (attack) | 0.263 | 0.395 (payload) | 0.265 | 0.264 |

Secondary arm P1 (historical perturbation 0.1; 2 seeds for R0, 1 for the others):
- Perturbation lowers the strict late frozen fraction to 0.683-0.691 in every regime.
- It raises novelty to 0.41-0.52.
- The net-64 fraction stays at 0.919-0.930.
- The perturbed medium is likewise regime-insensitive in extent.

## Post-hoc mechanism probe (NOT preregistered; does not enter the disposition)
posthoc_contest_probe.py, production/posthoc_contest_probe.json. Setup: 256^2, 5000 ticks, P0, 2 seeds per regime,
final 200 ticks, using the frozen kernel's own observer channel. Question: what share of template changes occur
at a (site, field) contested that tick by >= 2 active writers, so that the per-tick keyed arbitration re-draw picks
among fixed offers?

| Regime | Contested share |
|---|---|
| R0 | 0.68-0.69 |
| R1 | 0.71-0.72 |
| R2 | 0.89-0.91 |
| R3 | 0.42 |

(The probe's second column, "contested with an alternative", is tautologically equal to the first, because a
change implies an offer different from the current value. Ignore it.)

The R2 surplus over R0 is almost entirely re-draw flicker on contested targets. In R1, 29% of the changes are
uncontested but still non-novel (novelty 0.000; 11% strictly periodic): writers re-aimed by each other's writes and
cycling among a few values. That residue is uncharacterized. R3 has the fewest contested changes and the most
novel ones (0.28), consistent with rain-revived writers re-entering after starvation and writing values their
targets have not recently held. Its rate is the lowest of the four.

## Answers to the order's questions (s23)
1. **Did B-balanced reproduce?** Yes.
   - frozen_net64 is 0.92589 at 1024^2 x 50k under historical perturbation, against the exact historical value of
     0.92592 at 256^2.
   - The H1b number reproduces bit-exactly at 256^2 on CPU and GPU.
   - Under P0 the late strict frozen fraction is 0.988 and novelty 0.077, consistent with H4's ~95% collapse of
     template change without perturbation.
   - The quoted "0.923" has no committed artifact; the reproducible value is 0.9259.
2. **How quickly did each regime approach quiescence?** All four reach within 2x of their late rate in 100-175
   ticks (R1/R2 100, R0 150, R3 175). They then stay exactly stationary to 50,000 ticks (persistence 1.000). No
   regime avoids quiescence. They differ only in the level they settle at.
3. **Late-time frozen fraction?** In the strict sense (no change in the last 2000 ticks): 0.9880 (R0), 0.9865
   (R1), 0.9880 (R2), 0.9880 (R3). Net over 64 ticks: 0.994 in all four. The fraction ever changed by tick 50,000
   is 0.373 in all four, identical to the 4th decimal: the set of sites that can EVER move is fixed by the initial
   wiring, not by energy.
4. **Late-time endogenous turnover?** 0.00239 (R0), 0.00752 (R1), 0.00592 (R2), 0.00098 (R3) sites per tick. Ratios
   to R0: 3.14 / 2.48 / 0.41, with 8/8 seeds within +-1%.
5. **How much do starvation and replenishment explain?**
   - They explain the RATE well: late turnover tracks active-writer density, at 0.010-0.017 changes per active
     writer per tick across all four regimes.
   - Scarcity (R3) starves 34% of WRITE sites and leaves 60% of sites at zero energy. Every starvation is balanced
     by a revival (0.023/site/tick).
   - They explain none of the EXTENT. The fraction of the medium that moves is unchanged when energy is abundant
     (R1, R2), scarce (R3) or free (R1).
6. **Did any alternative regime produce persistent mobility?** In rate, yes: R1 and R2 sustain 2.5-3x B-balanced
   turnover to 50,000 ticks. In extent, no.
7. **Did it survive the trivial-mobility attack?** No. Novelty is 0.000 / 0.001 and spatial confinement holds. In
   the post-hoc probe, 71-90% of the changes sit on contested targets re-drawn by the arbitration hash.
8. **Robust or energy-regime-sensitive?** The frozen-medium conclusion is ROBUST to energy economy in the sense
   that matters for TH-009.
   - Over a 4x range of rain inflow, plus free compute, the same ~1.2% of the medium churns, the same ~37% is ever
     touched, and relaxation completes in under 200 ticks.
   - Energy is a rate knob on a fixed churning minority, not a mobility switch.
   - Formal label: MOBILE_BUT_TRIVIAL.
9. **Strongest alternative explanation.** The invariance could belong to the initial-condition family rather than
   to the law. Every regime started from the same 50%-WRITE sparse soup with uniform energy. In P0, a site's
   template can only change if some writer's aim covers it, and aims change only when written. So the ~37%
   reachable set may be largely fixed by the initial aim field. A different initial family (writer density, or
   energy-coupled initialization) was deliberately not varied today (one axis), and could change the extent where
   energy did not. A second alternative: the panel spans inflow 0.5-2.0 plus free compute, and an extreme
   intermittency regime (rare, large rain) was not tested.
10. **Single most informative next experiment for TH-009.** Energy is closed as the explanation for freezing. The
    next experiment should attack the reachable-set mechanism directly with one local physics change. The writer's
    aim (arg0 direction, arg1 field) is only ever changed by being overwritten, so a writer's target set is frozen
    by construction. The test: a minimal law in which a successful write re-aims the WRITER (for example, an
    executed write advances the writer's own direction), so writers sweep their neighbourhood instead of pinning
    one target. Measure:
    - whether ever_changed and the late frozen_strict move;
    - against the same novelty and spatial-confinement attack;
    - against a turnover-matched arbitration-flicker null.
    This targets the observed bottleneck (fixed aim, so a fixed reachable set), not a parameter. It is a TH-009
    physics change, as the order's s22 anticipates for a robust-frozen outcome. (The TEST-3 recoil/exchange family
    touches this from another side; this experiment does not start until this report is accepted.)

## Limitations
- One initial-condition family (sparse soup, 50% WRITE, uniform energy), as the order required.
- Four regimes. Rain quantum fixed at 8; intermittency at fixed inflow not varied.
- The attack metrics have a known-trivial calibration (contest flicker gives novelty ~0, as predicted) but no
  positive control for MOBILE_NONTRIVIAL: no Aether law is known to produce rich medium-level rewriting. The rule
  could not have been shown to pass a true positive.
- Thresholds were frozen after both flights and a dry run on Flight 1 data (disclosed in the prereg). The near-
  threshold rule (ratio >= 2.0) fired for R1/R2 with ratios of 3.1 and 2.5. The disposition does not hinge on it:
  had the rule not fired, R1/R2 would be NOT_MOBILE and the overall label REGIME_ROBUST_FROZEN. Either way the
  extent result is the same.
- The post-hoc probe is 256^2 x 5000 ticks with 2 seeds, not production scale. It is descriptive only.
- R1 "activity" is uninformative by construction (every WRITE site is always active).

## Evidence locator
Aether/V2B/ER01/:
- phaseA/ (handoff conformance), flight1/, flight2/ (records, plans, ledgers, reductions)
- PREREGISTRATION.md, RULES.json
- production/ (plan, ledger, 38 unit JSONs, stderr, REDUCTION.json, posthoc_contest_probe.json)
- er01_run.py (v2), er01_reduce.py (v2), er01_flight.py, er01_conformance.py, posthoc_contest_probe.py

Code SHA at freeze: 7ce2a58b9. Semantics id: aeth01.v1. Seed namespace: rng 0xE2010000+k, physics 0xE2011000+k.
