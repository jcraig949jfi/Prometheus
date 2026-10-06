# AETH-V2B-AIM01 RESULT: frozen-aim causal test

Order: roles/Aether/prompts/2026-10-05_aim01. Seat Aether[m2-95eba442], SPECTREX5 (M2), RTX 5060 Ti.
Freeze 1ec63c053 (PREREGISTRATION.md, RULES.json, production/plan.json; code and rules unchanged at reduction).
Production 2026-10-06 01:15:53Z - 06:38:34Z (19,361 s = 5.38 h; projected 6.0 h). Reduction: production/REDUCTION.json
(aim01_reduce.v1, rules sha256 cc0d6f48...). Post-hoc self-attack: production/posthoc/*.json (posthoc_nonaim_probe.py).
External review (#1668): requested, non-blocking, no reply at time of writing.

## Technical disposition: PASS
- 49/49 units rc=0.
- Gates all pass:
  - subset_violations = 0 in every unit (no EFFECT change without an executed write onto that site-field);
  - L0 RAW == EFFECT in every unit;
  - one table hash;
  - determinism: dup_L1D50_s0 bit-identical to L1D50_s0 (final digest and full series);
  - L0 continuity: L0 D50 late EFFECT turnover 0.002364 vs ER01 0.002393 (-1.2%), frozen_strict 0.9881 vs 0.9880,
    ever_changed 0.3735 vs 0.3733.
- L0 is also bit-identical to the ER01 runner on fixtures (Flight 1 C1).

## Preregistered dispositions (frozen rules, unaltered)
- **Initial density (L0): INIT_SUPPORT_SENSITIVE, with INITIAL_GEOMETRY_DOMINANT = true.**
- **Re-aim: REAIM_EXTENDS_SUPPORT = true at 3/3 densities; overall disposition REAIM_NONTRIVIAL_CANDIDATE.**

## Post-hoc self-attack (NOT preregistered; it does not alter the label above, but it changes how far the label can be trusted)
- The frozen attack ran on the EFFECT channel, which reads arg0 net of the re-aim count.
- A writer whose arg0 is repeatedly reset by a neighbour to the same raw value, while it re-aims in between,
  registers an EFFECT change at each reset, at an EFFECT value that drifts with the re-aim count. It therefore looks
  "novel" while the raw byte only cycles.
- arg0 carries 39-44% of L1's late EFFECT change (25% in L0). So a probe re-measured the medium on the fields the law
  never touches (opcode, arg1, payload). Same seeds and laws, 512^2 x 5000 ticks; production showed the state
  stationary from < 50 ticks to 30k. 2 seeds per cell, which agree to within 0.004.

| (seed medians) | L0 D25 | L1 D25 | L0 D50 | L1 D50 | L0 D75 | L1 D75 |
|---|---|---|---|---|---|---|
| ever changed, non-AIM fields | 0.150 | 0.463 | 0.296 | 0.716 | 0.436 | 0.846 |
| late turnover, non-AIM | 0.00051 | 0.00507 | 0.00180 | 0.01484 | 0.00358 | 0.02472 |
| late frozen_strict, non-AIM | 0.997 | 0.968 | 0.991 | 0.911 | 0.982 | 0.858 |
| novelty, non-AIM (16-tick memory) | 0.074 | 0.100 | 0.078 | 0.103 | 0.078 | 0.104 |
| arg0 EFFECT changes that reset to a recently held raw value | 0.92 | 0.89 | 0.92 | 0.89 | 0.92 | 0.89 |

Reading:
- (1) The SUPPORT result survives completely without arg0: re-aim opens +0.31 / +0.42 / +0.41 of the lattice in
  fields the law never writes itself.
- (2) The NONTRIVIALITY result does not survive cleanly. On non-AIM fields, about 90% of late changes return a site
  to a state it held within the last 16 ticks. Novelty is 0.099-0.105, straddling the frozen 0.10 triviality floor,
  only ~1.3x L0's flicker level.
- (3) The 0.32-0.34 novelty that passed the frozen attack came mostly from the arg0 re-aim/reset cycle as seen
  through the EFFECT subtraction.
- **Honest summary: AIM is causally implicated in the frozen support; the expanded medium's dynamics are, by the
  cleaner measure, borderline-trivial (mostly recent-state revisitation).** The preregistered NONTRIVIAL label is
  reported as computed and flagged as not robust to this attack.

## Primary table (production, 512^2 x 30,000 ticks, 8 paired seeds, EFFECT, medians)

| | L0 D25 | L1 D25 | L0 D50 | L1 D50 | L0 D75 | L1 D75 |
|---|---|---|---|---|---|---|
| initial target support (site) | 0.228 | 0.228 | 0.415 | 0.415 | 0.565 | 0.565 |
| ever_targeted (site) | 0.195 | 0.569 | 0.375 | 0.824 | 0.534 | 0.927 |
| ever_changed EFFECT | 0.194 | 0.567 | 0.374 | 0.821 | 0.532 | 0.924 |
| ever_changed RAW | 0.194 | 0.682 | 0.374 | 0.921 | 0.532 | 0.987 |
| late frozen_strict EFFECT | 0.9966 | 0.9330 | 0.9881 | 0.8264 | 0.9765 | 0.7433 |
| late turnover EFFECT | 0.000657 | 0.009161 | 0.002364 | 0.025694 | 0.004752 | 0.040543 |
| late turnover RAW | 0.000657 | 0.095551 | 0.002364 | 0.165686 | 0.004752 | 0.211983 |
| persistence | 1.001 | 1.000 | 1.001 | 1.000 | 1.000 | 1.000 |
| support saturation (99%) | <= 50 t | <= 50 t | <= 50 t | <= 50 t | <= 50 t | <= 50 t |
| late change outside initial support | 0.002 | 0.543 | 0.008 | 0.466 | 0.016 | 0.391 |
| changed sites inside initial support | 0.962 | - | 0.938 | - | 0.924 | - |
| P(change \| new target) | 0.99 | 0.99 | 0.99 | 0.99 | 0.99 | 0.98 |
| novelty EFFECT (frozen attack) | 0.078 | 0.337 | 0.077 | 0.331 | 0.076 | 0.322 |
| periodic p<=16 | 0 | 0 | 0 | 0.0001 | 0 | 0.0002 |
| late field share (op, arg0, arg1, pay) | .26/.25/.26/.25 | .25/.44/.17/.14 | .26/.25/.24/.25 | .30/.42/.18/.10 | .27/.24/.24/.25 | .34/.39/.19/.08 |

Paired L1 - L0 (8/8 seeds favour L1 at every density):
- d(ever_changed) +0.372 / +0.447 / +0.393;
- d(frozen_strict) -0.064 / -0.162 / -0.233;
- d(target support, template site-field) +0.136 / +0.231 / +0.284.

L0 density contrast (paired medians):
- D25 -> D50 +0.179; D50 -> D75 +0.158; D25 -> D75 +0.337 (monotone, nearly linear).

ER01 comparator (frozen evidence, 1024^2 x 50k, P0):
- R1 free compute: late turnover 0.00752, ever_changed 0.3736.
- R2 rich rain: late turnover 0.00592, ever_changed 0.3733.
- At D25, L1's EFFECT late turnover (0.0092) is comparable to those high-flicker regimes, and its non-AIM late
  turnover (0.0051) is lower than both. Yet its support is 0.567 EFFECT / 0.463 non-AIM against a D25 baseline of
  0.194 / 0.150.
- New reachability is therefore not explained by more activity. This separation is the strongest part of the
  result.

## Answers (order s29)
1. **Did L0 reproduce ER01?** Yes. Bit-identical to the ER01 runner on fixtures. At production scale, late turnover is
   -1.2% and frozen_strict / ever_changed are within 0.0002 of ER01.
2. **How does initial density shape L0's reachable support?** Strongly, monotonically and nearly linearly:
   ever_changed is 0.194 / 0.374 / 0.532 at D25 / D50 / D75 (+0.18 per 0.25 of WRITE density). The ER01 "37%
   invariant" was invariant to ENERGY, not to initial conditions.
3. **Does initial target support predict eventual changed support?** Yes. Under L0, 92-96% of every site that ever
   changes lies inside the support implied by the initial writers' aims, and ever_changed is about 0.85-0.94x that
   support. INITIAL_GEOMETRY_DOMINANT.
4. **Does reaim1 increase ever_targeted?** Yes, from 0.195 / 0.375 / 0.534 to 0.569 / 0.824 / 0.927 (site level).
5. **Does it increase EFFECT ever_changed?** Yes: +0.37 / +0.45 / +0.39, 8/8 seeds. On non-AIM fields alone
   (post-hoc): +0.31 / +0.42 / +0.41.
6. **Does it lower EFFECT frozen_strict?** Yes: -0.06 / -0.16 / -0.23 (non-AIM post-hoc: -0.03 / -0.08 / -0.12).
7. **Transient or persistent?** Persistent. Support saturates within 50 ticks, and turnover is exactly stationary
   (persistence 1.000) to 30,000 ticks. 39-54% of late change is outside the initial support.
8. **How much RAW movement is bookkeeping?** Most of it. RAW late turnover is 10.4x / 6.4x / 5.2x EFFECT, so 90% /
   84% / 81% of RAW late site-changes are the mandatory re-aim alone. RAW ever_changed exceeds EFFECT by 0.06-0.12.
9. **Does the activity survive the novelty / periodicity / spatial attacks?**
   - By the frozen rules: yes. Novelty 0.32-0.34, periodic ~0, max field share <= 0.44, persistence 1.0, late change
     outside the initial support 39-54%.
   - By the post-hoc non-AIM attack: only marginally. Non-AIM novelty is 0.099-0.105, at the 0.10 floor, and
     ~89% of arg0 EFFECT changes are resets to recently held raw values.
   - Not periodic, not one-field, spatially broad; temporally mostly recent-state revisitation.
10. **Principal cause?** MIXED, in a specific sense:
    - Under the historical law, initial geometry (the initial writers' aim support) sets the reachable support almost
      entirely.
    - Frozen aim is what makes that so. Letting executed writes re-aim breaks the dependence: L1's support far
      exceeds the initial support at every density, with 39-54% of late change outside it.
    - The two explanations are the same mechanism seen from two sides. Fixed aim pins the reachable set to the
      initial geometry.
11. **Legitimate TH-009 mutable-medium candidate?** A candidate for MUTABILITY, not yet for nontrivial dynamics.
    - The medium-level rungs are clearly established: AIM_EXPANDS, MEDIUM_EXPANDS and MUTABILITY_PERSISTS (with
      non-AIM fields confirming).
    - NONTRIVIAL_DYNAMICS passes the frozen rule, but rests largely on an EFFECT-channel artifact. By the cleaner
      measure it is at the triviality floor.
    - I would not let the preregistered label carry a "nontrivial medium" claim forward.
12. **Single next experiment.**
    - Before any content test, settle the nontriviality question that this experiment's own attack left open, with
      ONE preregistered, cheap, production-scale measurement and no physics change.
    - The question: are L1's non-AIM changes richer than a matched flicker null?
    - Measures: non-AIM novelty with a longer memory (16 and 64 ticks), unique non-AIM states per site over a long
      window, and a turnover-matched arbitration-flicker comparator (ER01 R1/R2, re-measured on the same non-AIM
      instrument).
    - If L1's non-AIM novelty clearly exceeds the matched null: proceed to the order's content-persistence test
      (s27).
    - If it does not: the re-aim medium is mutable but trivial. Per s27 the next physics attacks a richer
      re-targeting mechanism, not faster re-aiming.

**Strongest alternative explanation.** Re-aim mechanically sweeps each writer's single output across its 4
neighbours. Every newly reached site is then simply contested by more writers in rotation, and the arbitration
re-draw plus rotating writers produce bounded flicker over a larger but fixed set of offered values.
- Under that reading the expanded support is real, but the medium is not "rewriting itself" in any richer sense than
  ER01's flicker. It is ER01's contested-target flicker made spatially wide.
- Non-AIM novelty sitting at the flicker floor (~0.10 vs L0's 0.075) and P(change | new target) ~0.99 are both what
  this explanation predicts.
- Telling it apart from genuine rewriting is exactly what the proposed next measurement does.

## Limitations
- One energy economy (B_balanced), P0 only, one lattice size in production (512^2; finite-size check at 1024^2 in
  Flight 2).
- The EFFECT subtraction removes the counter but inflates novelty in the arg0 channel (shown post-hoc). The frozen
  attack should have measured novelty on non-AIM fields; this is recorded as an instrument-design defect of the
  preregistration, not repaired retroactively.
- The post-hoc probe used 2 seeds per cell at 5000 ticks. Seeds agree to < 0.004, and production showed
  stationarity from tick 50, but it is not production scale.
- No positive control exists for "nontrivial medium dynamics" (carried over from ER01).
- Thresholds were frozen after both flights' raw numbers had been seen (disclosed). The frozen rules' outputs were
  not seen before production.

## Evidence locator
Aether/V2B/AIM01/:
- PREREGISTRATION.md, RULES.json
- flight1/, flight2/ (records, plans, ledgers, reductions, conformance)
- production/ (plan, ledger, 49 unit JSONs, REDUCTION.json, posthoc/)
- aim01_run.py (law + meter), aim01_reduce.py, aim01_flight.py, aim01_conformance.py, posthoc_nonaim_probe.py
- Known answers: Aether/test/test_aim01_meter.py
Semantics: L0 aeth01.v1, L1 aeth01.reaim1. Seeds rng 0xE2010000+k, physics 0xE2011000+k, k = 0..7.
