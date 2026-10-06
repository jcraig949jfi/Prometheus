# AETH-V2B-AIM01 preregistration: frozen-aim causal test

Order: roles/Aether/prompts/2026-10-05_aim01 (operator, 2026-10-05). Seat Aether[m2-95eba442], host SPECTREX5 (M2),
RTX 5060 Ti 16 GB. Frozen at the commit that adds this file. Rules file: RULES.json (sha256 recorded by the
reducer). Nothing below changes after production launch.

## Questions
- Q1 (initial-condition alternative): under aeth01.v1, does eventual reachable support change with initial WRITE
  density?
- Q2 (primary): at matched density and seed, does reaim1 materially expand EFFECT ever_changed?
- Q3: does the expanded region keep changing late?
- Q4: is the new activity more than scanning, flicker, counting, or a short cycle?

## Disclosure: what had been seen before freezing
- Flight 1: 256^2 x 3000 ticks, 2 seeds, full factorial.
- Flight 2: 512^2 x 12,000 ticks, 2 seeds, full factorial, plus 1024^2 x 3000 for L0/L1 D50.
- Both reductions were seen (no rules applied).
Every threshold below is either specified by the order (0.05 materiality, >= 2 of 3 densities, 5/6 replication) or
carried over unchanged from ER01's frozen rules (novelty <= 0.10, periodic >= 0.5, one field >= 0.9, persistence
>= 0.5). Three are new and were chosen for their meaning before any rule was applied to data:
- target-support growth >= 0.05 (same materiality as the support threshold);
- late change outside the initial support >= 0.10 of late EFFECT changes (10x the ~0.01 L0 share seen in
  Flight 1);
- INITIAL_GEOMETRY_DOMINANT overlap >= 0.9.

## Semantics
- L0 = aeth01.v1: the frozen kernel Aether/runpod/aeth01_canary/aeth01_gpu_kernel.py, unmodified.
- L1 = aeth01.reaim1. The single law difference: after the aeth01.v1 tick, every WRITE source whose proposal WON
  its target contest that tick (any of the 5 fields, including an energy transfer) has arg0 := arg0 + 1 (mod 256),
  i.e. direction (arg0 mod 4) := direction + 1 (mod 4), unless its own arg0 received a winning write that tick (the
  written value stands).
  - Byte +1 rather than "mod 4" keeps arg0's upper bits intact; direction advances by exactly one in both readings.
  - Winners are read from the kernel's own observer side channel. Implementation:
    Aether/V2B/AIM01/aim01_run.py law_step.
- Energy: B_balanced (w 1, m 1, rain 8 @ 1/8). Perturbation OFF. Unchanged from ER01 R0 P0.

## Initial densities and pairing
- D25 / D50 / D75 = WRITE density 0.25 / 0.50 / 0.75. Built with observatory.aeth01_run.build_initial(sparse_soup,
  write_density=d) and the SAME rng seed per seed index.
- The generator draws the background opcode, one uniform u per site (WRITE iff u < d), then arg0, arg1, payload
  and energy, in a fixed order and size independent of d. So within a seed every byte is identical across
  densities except the opcode of sites with u between the two densities, and the WRITE sets are nested. Verified
  per seed (flight1/conformance C3).
- Seed namespace = ER01's: rng 0xE2010000+k, physics 0xE2011000+k. L0 D50 seed k is therefore ER01 R0 P0 seed k.

## RAW / EFFECT
- RAW: template fields as stored.
- EFFECT: identical, except arg0 is read as (arg0 - c) mod 256, where c counts re-aims applied at that site. A
  re-aim is never an EFFECT change; a write onto arg0 is.
- Under L0, c = 0 and RAW == EFFECT (gated).
- Gate: no EFFECT change on a (site, field) without an executed write onto it that tick (subset_violations = 0).
- Known answers: Aether/test/test_aim01_meter.py: STATIC, FIXED_FLICKER, EXPANDING_SUPPORT, AIM_BOOKKEEPING_ONLY
  (mandatory), and bookkeeping plus a real write.

## Observables (EFFECT unless marked)
- Late window = final 2000 ticks.
- ER01 set:
  - ever_changed; frozen_strict (no change at any late tick); frozen_net64; late turnover;
  - persistence (last 10% of bins / bins at 50-60%); t_quiesce;
  - active density; energy;
  - tail-64 novelty (16-tick memory) and periodic share p <= 16; per-field late share.
- AIM-specific:
  - ever_targeted at site and template-site-field level (executed writes);
  - initial target support (every initial WRITE site's aim, energy-blind; site and site-field);
  - target_support_growth(t) = ever_targeted_sf(t) - initial support;
  - change_given_new_target / change_given_init_target;
  - overlap of ever_changed with ever_targeted and with initial support;
  - late_out_init_share: share of late EFFECT changes at sites outside the initial site support;
  - tail-64 unique non-AIM states per changed site (descriptive);
  - RAW late turnover and RAW ever_changed (bookkeeping share).

## Rules (RULES.json)
Pairs are (density, seed), L1 minus L0, EFFECT.

Per density:
- AIM_EXPANDS: median d(ever_targeted template site-field) >= 0.05.
- MEDIUM_EXPANDS (= the order's REAIM_EXTENDS_SUPPORT conditions at that density):
  - median d(ever_changed) >= 0.05;
  - >= S seeds with d(ever_changed) > 0 (S = 5 of 6, or 7 of 8, fixed with the seed count below);
  - median d(frozen_strict) < 0;
  - AIM_EXPANDS.
- MUTABILITY_PERSISTS: MEDIUM_EXPANDS, AND L1 median persistence >= 0.5, AND L1 median late_out_init_share >= 0.10.
- NONTRIVIAL_DYNAMICS: MUTABILITY_PERSISTS and none of these trivial signatures (L1 medians):
  - novelty <= 0.10;
  - periodic(p <= 16) share >= 0.5;
  - max late field share >= 0.9.

Overall:
- REAIM_EXTENDS_SUPPORT if MEDIUM_EXPANDS at >= 2 of 3 densities.
- Disposition:
  - MEASUREMENT_FAILED if any gate fails;
  - else REAIM_NO_SUPPORT_EFFECT if not REAIM_EXTENDS_SUPPORT;
  - else REAIM_NONTRIVIAL_CANDIDATE if NONTRIVIAL_DYNAMICS at >= 2 densities;
  - else REAIM_MOBILE_BUT_TRIVIAL. This includes support that expands but does not persist (a transient).

Initial-density verdict (L0; paired medians of ever_changed differences D25->D50, D50->D75, D25->D75):
- INIT_SUPPORT_ROBUST: all |diffs| < 0.05.
- INIT_SUPPORT_SENSITIVE: |D25->D75| >= 0.05 and both steps have the same sign (monotone).
- MIXED: otherwise.
- INITIAL_GEOMETRY_DOMINANT (an additional flag): SENSITIVE, and at every density the L0 median share of
  ever-changed sites lying inside the initial target support is >= 0.9.

## Gates (any failure => MEASUREMENT_FAILED; order s24)
- subset_violations = 0 in every unit.
- L0 RAW == EFFECT in every unit.
- One table hash.
- Determinism duplicate bit-identical (final digest and series).
- Every planned unit rc = 0. A unit lost to an OS or hardware fault may be re-run once from scratch; that is
  recorded.
- Code and rules sha256 unchanged from the freeze (checked before reduction).
- L0 continuity: see PRODUCTION.

## Stopping rules
- Fixed plan. No change to law, densities, energy, perturbation, horizon or seeds after launch. No early stop on
  the curves.
- Early stop only for: a gate breaking in a way that invalidates the rest; evidence corruption; hardware
  instability.
- No new unit starts after the wall cap. 12 h hard wall.

## Comparator (descriptive, not a rule)
ER01 high-flicker regimes, frozen evidence: R1 free compute (late turnover 0.00752, ever_changed 0.3736,
frozen_strict 0.9865) and R2 rain x2 (0.00592, 0.3733, 0.9880), at 1024^2 x 50k, P0, seeds 0-7. They are reported
next to L1, so that "more activity" can be told apart from "new reachability".

## PRODUCTION (frozen from measured Flight-2 runtime and saturation; science thresholds untouched)
- Lattice 512^2.
  - Flight 2 finite-size check at D50: L1 512^2 vs 1024^2, ever_changed 0.8203 vs 0.8199, frozen_strict 0.8262 vs
    0.8264. L0 is likewise unchanged.
  - ER01 already showed L0 512^2 == 1024^2.
- Horizon 30,000 ticks; late window 2000; bin 50.
  - In Flight 2, support (ever_changed, ever_targeted) saturates within the first 25-tick bin in every cell, and
    EFFECT turnover is stationary (persistence 0.999-1.005) to 12,000 ticks.
  - 30,000 = 2.5x that demonstrated-stationary horizon and ~200x the relaxation time. That leaves a long late
    window and a check for slow support creep.
- Seeds k = 0..7 (8 per cell). The "favor" replication count is therefore 7 of 8 (prospective adjustment of the
  order's 5 of 6).
- 2 laws x 3 densities x 8 seeds = 48 units, plus the determinism duplicate dup_L1D50_s0 = 49 units, 1.47 M
  world-ticks.
- Measured Flight-2 rate: 4 concurrent 512^2 units at 51-59 ms/tick each (<= 14.7 ms per world-tick). That
  projects 6.0 h against the 11 h target. Driver: --jobs 4, --wall-cap 39600, --drain. Hard wall 12 h.
- L0 continuity gate (RULES.json continuity_L0_D50): L0 D50 median late EFFECT turnover within 5% of ER01 R0 P0's
  0.002393, and frozen_strict and ever_changed within 0.003 of 0.9880 and 0.3733. Flight 2 at 512^2 x 12k: 0.002391
  / 0.9879 / 0.3727.
- Unit order: continuity and the duplicate first, then seed-major across the 6 cells.
- The rules were executed once on the Flight 2 data as a smoke test of the reducer code path, with the output
  discarded unread.
- Frozen sha256 (LF as stored in git):
  1466db589ab4cde5a010b7048c51ce8c5de8249699a4141363bb82a2ce5f6d9c production/plan.json
  cc0d6f48fa5255c62a5f31e8920e4485d49bf63c82fb5ab0e25d9bfebf9beb0f RULES.json
  fdd515f089b7b4d73d76f1d46d7b54fee98aa7543ed20acdf69868214e171a90 aim01_run.py
  980485999a8a85096b4bdbe313cb830d67b809d0a67dfe843f6e786a3e369a92 aim01_reduce.py
  7d58043c044afb5025edd9cea5946b4ad34939ca002a17832c2f8530346a9aa3 aim01_flight.py
  1e89830d62e50266705ab95250890a80ab45479f336fd5b894e5b6af7f773f65 ../../runpod/aeth01_canary/aeth01_gpu_kernel.py
