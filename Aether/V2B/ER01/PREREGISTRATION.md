# AETH-V2B-ER01 preregistration: energy-regime generality of the frozen medium

Order: roles/Aether/prompts/2026-10-05_er01 (operator, 2026-10-05). Seat Aether[m2-95eba442], host SPECTREX5 (M2),
RTX 5060 Ti 16 GB. Frozen at the commit that adds this file. Rules file: RULES.json (its sha256 is recorded by the
reducer in REDUCTION.json). Nothing below may change after production launch.

## Question
Under aeth01.v1, with perturbation OFF, does the medium stay frozen across materially different energy economies, or
does some economy sustain endogenous rewriting of the medium? The ONLY axis varied is the energy economy.

## What I had seen before freezing (disclosure)
Flight 1 (512^2, 5000 ticks, 2 seeds) and Flight 2 (1024^2, 8000 ticks, 2 seeds) outputs, and a dry run of the draft
rules on Flight 1 (provisional R1/R2 class MOBILE_BUT_TRIVIAL by low novelty + spatial confinement; R3 NOT_MOBILE).
The thresholds below are round numbers chosen for mechanistic meaning, not fitted. Two of them sit near observed
values and are flagged: the paired turnover ratio of R1/R2 in the flights was ~2.5-3.2 against a 2.0 threshold.

## Fixed semantics
- Law: aeth01.v1, frozen CuPy kernel runpod/aeth01_canary/aeth01_gpu_kernel.py (unmodified), verified state-digest-
  and measurement-identical to the independent NumPy text test/reference/gpu_aeth01.py for all 8 regime x arm cells
  (64^2 x 300 ticks, 2 seeds) and to 5000 ticks (128^2, all cells): phaseA/conformance_v2_*.json.
- Runner er01_run.v2; reducer er01_reduce.v2; driver er01_flight.py. regime_table_hash recorded in every unit.
- Initial condition: sparse soup, 50% WRITE, uniform energy 0..255 (the historical aeth02/first-light family).
  Energy initialization is NOT coupled to the regime: for a given seed index every regime starts from the identical
  lattice (common random numbers), and uses the identical keyed physics seed.
- Seed namespace: rng_seed = 0xE2010000 + k, physics seed = 0xE2011000 + k, k = 0..11. Flights used k = 0, 1;
  production uses k = 0..11 (k = 0, 1 are re-run at the production horizon; flight outputs are not pooled).

## Energy-regime panel (write cost, maintenance, replenish amount @ probability; inflow = amount x p per site per tick)
| id | label | w | m | rain | inflow | rationale |
|---|---|---|---|---|---|---|
| R0 | B_balanced | 1 | 1 | 8 @ 1/8 | 1.0 | historical reference (aeth02_falsifiers.B_BALANCED) |
| R1 | C_free_compute | 0 | 0 | none | 0 | historical ECONOMICS.md regime C, exact semantics (aeth01_scout); every WRITE site always active; activity is uninformative by construction |
| R2 | rich_rain_x2 | 1 | 1 | 8 @ 1/4 | 2.0 | costs unchanged; inflow covers maintenance + one write per tick, so an active writer breaks even in expectation. Hypothesis: freezing is substantially starvation-driven; relieving it raises sustained rewriting |
| R3 | scarce_rain_half | 1 | 1 | 8 @ 1/16 | 0.5 | costs unchanged; inflow half of maintenance. Hypothesis: if mobility is energy-controlled, scarcity accelerates freezing and lowers activity |
R0/R2/R3 differ in ONE number (rain probability) with the rain quantum fixed, so intermittency per event is held.

## Arms
- P0 perturbation OFF (mut_numer = 0) from tick 1: primary.
- P1 historical perturbation 0.1: secondary / continuity only. Not used for the disposition except the R0 continuity gate.

## Production configuration
See PRODUCTION section at the end (filled from measured Flight-2 throughput before launch, part of this freeze).

## Observables (per unit; definitions in er01_run.py / er01_reduce.py docstrings)
late window = final 2000 ticks.
- late_turnover: mean fraction of sites whose template (opcode, arg0, arg1, payload) changes per tick, late window.
- frozen_strict: fraction of sites with no template change at ANY tick of the late window.
- frozen_net64: historical H1b definition (no NET change over the final 64 ticks).
- persistence: turnover over the last 10% of bins / turnover over bins in [50%, 60%) of the horizon.
- t_quiesce: first bin end tick with turnover <= 2x the late-window rate.
- active / write / starved densities, rain / starve / revive events per site per tick, energy mean / median / zero
  fraction / 255 fraction, ever_changed.
- Attack metrics over the final 64 ticks, among sites that changed: periodic_le16 (state sequence exactly periodic
  with some p <= 16), novel_change_frac (share of changes producing a template state not held by that site in the
  previous 16 ticks), field_share (per-field share of late changes).

## Decision rules (RULES.json)
Per alternative regime r in {R1, R2, R3}, P0, using the 12 paired seeds:
1. ENERGY_STARVED if median late active density < 0.01 and median late_turnover < 0.0002.
2. Mobility candidate if (a) the paired ratio late_turnover(r,k)/late_turnover(R0,k) >= 2.0 in >= 80% of seeds AND
   (b) median persistence >= 0.5 (change is sustained, not relaxation residue). Otherwise NOT_MOBILE.
3. Trivial-mobility attack on every candidate (order s8). It is MOBILE_BUT_TRIVIAL if ANY holds (seed medians):
   - periodic_le16 >= 0.5 (deterministic short oscillation);
   - novel_change_frac <= 0.10 (flicker among recently held states: contest re-draws, short cycles);
   - max field_share >= 0.9 (one field flipping);
   - spatially confined: median paired change in frozen_strict vs R0 is not below -0.05, i.e. the extra turnover is
     not spread over at least 5 more percentage points of the medium than R0's.
   Otherwise MOBILE_NONTRIVIAL.
Overall: REGIME_SENSITIVE if any r is MOBILE_NONTRIVIAL; else MOBILE_BUT_TRIVIAL if any r is; else
REGIME_ROBUST_FROZEN if every r is NOT_MOBILE or ENERGY_STARVED; else UNRESOLVED.

## Validity gates (any failure => MEASUREMENT_FAILED, stop interpretation, order s16)
- continuity: median frozen_net64 of R0 P1 units in [0.90, 0.95] (historical 0.926 exact at 256^2; F1/F2 0.926).
- determinism: the duplicate unit dup_<id> has identical final digest and identical series.
- one regime_table_hash across all units.
- every planned unit completed with rc = 0 (a unit lost to hardware/OS failure may be re-run once from scratch with
  the same parameters; that is recorded, it is not a change of plan).

## Stopping rules
- Fixed horizon; no early stop for boring or exciting curves; no extension.
- Stop early only for: all units complete; a validity gate failing in a way that invalidates the rest (non-determinism,
  conformance break); evidence corruption; hardware instability (GPU errors, thermal throttling making the cap
  unreachable). Hard wall: 12 h from launch; the driver stops launching new units at the cap.
- A scientific null is not a reason to re-run with other parameters.

## Strongest alternative explanations to report against
- Arbitration re-draw noise (keyed hash every tick) as an internal noise source: a contested target flickers between
  fixed values without any medium-level rewriting.
- Energy as rate knob only: more energy -> more active writers -> more redundant re-writes of the same values in the
  same places (quantitative, not qualitative).
- Initial relaxation mistaken for sustained activity (handled by persistence and the late window).
- Finite size (Flight 2 compares 512^2 with 1024^2 for R0).

## PRODUCTION (frozen from measured Flight-2 throughput)
- Lattice 1024^2 (Flight 2: R0 at 512^2 and 1024^2 agree to 4 decimals on every primary observable, so lattice size
  is sufficient; 1024^2 is chosen because it costs the same per tick as 512^2 on this device).
- Horizon 50,000 ticks (5x the longest prior Aether horizon of 10,000); late window 2000 ticks; bin 50 ticks.
- P0: R0, R1, R2, R3 x seed k = 0..7 (8 paired seeds, 32 units).
- P1 (secondary/continuity): R0 k = 0, 1; R1, R2, R3 k = 0 (5 units).
- Determinism duplicate: dup_R0P0_s0 (identical parameters to R0P0_s0).
- 38 units, 1.9 M world-ticks. Measured throughput: 2 concurrent 1024^2 worlds at 34.5 ms/tick each, i.e. 17.3 ms
  per world-tick, so a predicted 9.1 h of compute against the 11 h budget. Driver: --jobs 2, --wall-cap 39600 s
  (no unit starts after 11 h), --drain (a running unit finishes, <= 0.5 h, inside the 12 h hard wall).
- Unit order (production/plan.json): continuity and determinism first, then seed-major across regimes, so a truncated
  run stays balanced; secondary P1 units last.
- Evidence: unit JSONs, ledger and stderr under Aether/V2B/ER01/production/ (each ~0.5 MB; committed).
- Frozen file hashes (sha256, LF line endings as stored in git):
  production/plan.json cafc1324b079d1698f2dcba8c145bd61d226126a8f9b311c791d0479ddbbd6f1
  RULES.json 57e138b0d284129b65a33c60d10a8d927d2c54ae88025c338ad055cfd8990428
  er01_run.py 7c983a7c5829f57289f41231f2f3da4879ef4ecb952a65dc29d041c27e031e6b
  er01_reduce.py e9707dddab5dbd3f1e4ca22b225fc6c4e73337daec8041517f14036a829ce0c0
  er01_flight.py 419741ea55fadf6068b3d47e83134668a03e691b139ece97a724288199b41829
