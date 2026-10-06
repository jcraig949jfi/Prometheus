# AETH-V2B-AIM02 preregistration: matched-flicker richness test

Order: roles/Aether/prompts/2026-10-06_aim02. Seat Aether[m2-95eba442], SPECTREX5 (M2), RTX 5060 Ti. Branch
aether/aim02-2026-10-06, cut from main 9bffb1f7c (AIM01 integrated). Frozen at the commit adding this file.
Measurement only: no new physics.

## Question
On fields untouched by the re-aim law, are aeth01.reaim1's late dynamics measurably richer than an
activity-matched flicker process? AIM01 rungs 1-3 (aim expands, support expands, support stays writable) are taken
as established and are not re-tested. This tests rung 4 only.

## Conditions (all perturbation OFF; seeds rng 0xE2010000+k, physics 0xE2011000+k, k = 0..7)
| id | law | WRITE density | energy | role |
|---|---|---|---|---|
| L1D25 / L1D50 / L1D75 | aeth01.reaim1 (AIM01 L1, unchanged) | 0.25 / 0.50 / 0.75 | B_balanced | primary |
| C1FREE | aeth01.v1 | 0.50 | ER01 R1 free compute (w0 m0, no rain) | natural flicker comparator |
| C2RICH | aeth01.v1 | 0.50 | ER01 R2 rich rain (w1 m1, rain 8 @ 1/4) | natural flicker comparator |
| L0D25 / L0D50 / L0D75 | aeth01.v1 | 0.25 / 0.50 / 0.75 | B_balanced | reference for report Q1 (descriptive) |
- Conformance (qual/conformance_n64_t300.json):
  - the L0/L1 conditions are bit-identical to AIM01's runner;
  - C1/C2 are bit-identical to ER01's runner (R1/R2, P0);
  - CPU == GPU for every condition, including the full analysis output.
- Comparator seeds use the D50 initial family with the same seed k, so lattices are common-random-number paired
  with L1D50 and nested with L1D25/L1D75.

## Primary channel and instrument (aim02_meter.py, aim02_run.record_columns)
- Fields opcode, arg1, payload ONLY. arg0 and energy never enter the primary channel; the AIM_BOOKKEEPING fixture
  proves it (arbitrary arg0 and energy changes give exactly zero).
- arg0 RAW is analysed separately as a labelled diagnostic. The AIM01 EFFECT channel is not used.
- Sample: the 256 x 256 grid of sites with row and column even, x 3 fields = 196,608 site-field columns per unit.
- Late window W = 2000 ticks, ending at the horizon.
- Per column with >= 2 changes:
  - n_ch;
  - U (distinct values held);
  - upc = (U-1)/n_ch;
  - tpc = distinct (prev, new) transitions / n_ch;
  - n16 / n64: share of change events whose new value was not held in the previous 16 / 64 ticks (clamped at
    the window start);
  - dr2 = values first held in the second half / changes in the second half;
  - return gaps (time between consecutive holdings of the same value, > 1 tick).
- Activity conditioning: columns are binned by n_ch into log2 bins [2,4) ... [128,256) [256,inf).
  - compare_conds() weights the comparator's per-bin mean by the TREATMENT's bin column counts.
  - Only bins with >= 30 columns on both sides are used; coverage = the share of treatment columns in usable bins.
  - "More changes -> more unique states" therefore cannot carry the result.

## Known answers (Aether/test/test_aim02_meter.py; 8/8 pass with the frozen rules)
- STATIC, TWO_STATE_FLICKER, K_STATE_FLICKER.
- RECENT_REVISIT (period 32: N16 > 0.95, N64 < 0.05).
- EXPANDING_CATALOG.
- AIM_BOOKKEEPING (exactly zero).
- Positive control at the instrument level (expanding vs K-state diff > 0.2 on upc/tpc/n64; flicker vs flicker
  < 0.01).
- Positive control through the frozen decision rule: expanding catalogue vs flicker comparators =>
  RICHNESS_SUPPORTED; flicker vs flicker => FLICKER_EQUIVALENT.

## Rules (RULES.json)
- For each L1 density and each seed k, compare L1 (seed k) with C1FREE (seed k) and with C2RICH (seed k).
- A family "beats both" for that seed if, against BOTH comparators, coverage >= 0.5 and the family's statistic
  clears its margin:
  - NOVELTY: n64 diff >= 0.05
  - REPERTOIRE: upc diff >= 0.05
  - DISCOVERY: dr2 diff >= 0.05
  - TRANSITIONS: tpc diff >= 0.05
  - RECURRENCE: return-time median ratio >= 1.5
- A family is material at a density if it beats both in >= 7 of 8 seeds.
- A density is SUPPORTED if NOVELTY (n64) is material AND >= 2 families are material.
- Disposition:
  - RICHNESS_SUPPORTED: >= 2 of 3 densities SUPPORTED.
  - RICHNESS_WEAK: otherwise, if any family is material at any density, or N16 novelty (diff >= 0.05 vs both, 7 of
    8 seeds) is material at any density. This covers novelty that does not persist with 64-tick memory.
  - FLICKER_EQUIVALENT: otherwise. Interpretation: REAIM_MOBILE_BUT_TRIVIAL.
- Gates (any failure => MEASUREMENT_FAILED):
  - one table hash;
  - the determinism duplicate dup_L1D50_s0 identical (final digest and primary analysis);
  - every unit rc = 0 (a unit lost to an OS fault may be re-run once from scratch; recorded).

## Disclosure: qualification numbers seen before this freeze
qual/ held 8 conditions x seeds 0-1, 512^2 x 6000, W 2000, plus L1D50 and C1FREE seed 0 at 10000 / W 4000. The
reduction (no rules) is qual/REDUCTION_W2000.json.

L1 minus comparator, activity-matched:

| | n16 | n64 | upc | tpc | dr2 | return-median ratio |
|---|---|---|---|---|---|---|
| vs C1/C2, all densities, both seeds | +0.097 to +0.101 | +0.0023 to +0.0028 | +0.0021 to +0.0023 | +0.0044 to +0.0050 | 0.0000 | 2.00x |
| vs L0, same density | +0.019 to +0.023 | +0.0006 to +0.0011 | +0.0006 | +0.0013 to +0.0017 | 0 | 1.30-1.33x |

- Absolute values: in every condition, changing site-fields hold about 2 distinct values (U ~2.01-2.09).
  - L1D50: 92% hold exactly 2.
  - L1D50 return-gap quantiles (p10/p50/p90) in the dominant bin: 2/4/16. C1FREE: 2/2/4.
- Window convergence: doubling W to 4000 leaves L1D50's and C1FREE's U histograms identical.
- With these numbers known, the margins were chosen for their meaning, NOT fitted:
  - 0.05 is AIM01's materiality, carried over to the difference families;
  - "broader" = a return-time median >= 1.5x.
- Two clauses are known to sit near or above qualification values: RECURRENCE (observed 2.00x vs margin 1.5) and N16
  (observed ~+0.10 vs margin 0.05). Both feed only RICHNESS_WEAK unless N64 is also material, and N64 was observed
  ~20x below its margin. A reviewer should read the disposition with this in view.
- Runtime: 4 concurrent 512^2 units at ~50 ms/tick each, ~295 s per 6000-tick unit. CuPy pool ~2.8 GiB per unit
  (W 2000 recording), host RSS ~470 MiB.

## Production
- 512^2, 6000 ticks, W 2000 (window = ticks 4001-6000).
  - AIM01 showed L1 support saturating within 50 ticks, stationary to 30k, with 512^2 == 1024^2.
  - Qualification showed catalogue convergence at W 2000.
- 8 conditions x 8 seeds + dup_L1D50_s0 = 65 units. Projected ~80 min at --jobs 4. Cap --wall-cap 39600; hard wall
  12 h.
- Frozen sha256 (LF as stored in git):
  d3c4d14cd140ebed3494f024df2e727b7f3cf462b9ead5229225823cfc649618 production/plan.json
  4ba232ca452f141b2536d5bb3757c747f282364453ad77f00496414d2d93bf5c RULES.json
  9cf1c62579ea13ba787bcbb1064d93fa694715d9d0c0c087f5cdc9124067f5a4 aim02_run.py
  ef778a7fabc0b242b6d65a6362d4300fadc63d26db0a03e82ea621b6dd07ecd6 aim02_meter.py
  01f2bc53d555c08a17d0b1c82076de8489326db66653b62935fc53ac82ee9e14 aim02_reduce.py
  db778b234a391f909203f4ef023190a8cc26411818aaf6fca400bcdddbe2665a aim02_flight.py
  1e89830d62e50266705ab95250890a80ab45479f336fd5b894e5b6af7f773f65 ../../runpod/aeth01_canary/aeth01_gpu_kernel.py

## Stopping
Fixed plan. No change to conditions, window, horizon, seeds, rules or instrument after launch. A null is not a stop
condition.
