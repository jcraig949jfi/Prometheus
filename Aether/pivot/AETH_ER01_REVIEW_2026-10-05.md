+==============================================================================+
| REVIEW PACKET -- AETH-V2B-ER01: is Aether's frozen medium an artifact of its  |
| single (B-balanced) energy economy?                                          |
| Author: Aether (role seat), host SPECTREX5 / M2, RTX 5060 Ti 16 GB           |
| Date: 2026-10-05                                                             |
| For: HITL operator + external reviewers                                      |
| Status: COMPLETE. Preregistered disposition MOBILE_BUT_TRIVIAL; technical PASS |
| Self-contained: no repo access needed; every load-bearing number is inline.  |
+==============================================================================+

-----
0. SUMMARY
-----
Question (operator order): almost all Aether physics was studied under ONE
energy economy ("B-balanced": write cost 1, maintenance 1, rain +8 energy with
probability 1/8). Under it the medium freezes. Was freezing a property of the
local law, or of that economy?

Answer: the law. Four economies were tested under perturbation OFF:
 - free compute;
 - half the rain inflow;
 - the historical inflow;
 - double the inflow.
In every one of them:
 - the same ~1.2% of the lattice changes in the late window (late frozen
   fraction 0.9865-0.9880);
 - the same 37.3% of sites EVER change in 50,000 ticks;
 - relaxation completes in 100-175 ticks.
Energy only scales HOW OFTEN that fixed minority flips: 0.41x to 3.14x the
B-balanced rate. The extra flips return to states held in the last 16 ticks
(novelty 0.000-0.001). In a post-hoc probe, 71-90% of them sit on targets
contested by >= 2 writers whose winner is re-drawn by the per-tick arbitration
hash.

Preregistered label: MOBILE_BUT_TRIVIAL.
 - R1 (free compute) and R2 (rain x2) clear the rate screen (>= 2x in >= 80% of
   seeds, sustained).
 - Both fail the cheap attack: low novelty AND spatial confinement.
 - R3 (scarce) is NOT_MOBILE.
In substance this is "frozen medium robust to energy economy; energy is a rate
knob, not a mobility switch."

-----
1. WHAT WAS BUILT, AND WHAT WAS COMMITTED BEFORE MEASUREMENT
-----
 - Host handoff BUCKKEEP -> M2. Six checks passed before the old host
   quiesced:
    * tests: 1426 pass. 2 fail, neither physics: legacy wording audit, and a
      C:/D: temp path that passes when rerun on D:.
    * 41/44 committed historical values reproduce bit-for-bit. The 3 misses are
      one metric that was later redefined.
    * GPU (CuPy) vs independent CPU (NumPy) implementation: identical state
      digests and identical measurement output, all 8 regime x arm cells, out
      to 5,000 ticks.
 - Reused the FROZEN aeth01.v1 GPU kernel unmodified. New code is a runner
   (regime table as data, hashed into every unit), a concurrent driver
   (resume, wall cap, not_before), and a reducer with the rules in a separate
   JSON file.
 - Two capped test flights (557 s, 1438 s), then a preregistration committed
   (7ce2a58b9) BEFORE production. The commit holds the regime table, the
   observables, the numerical rules, the gates, the stopping rules, the
   production plan, and sha256 of every frozen file.
 - DISCLOSURE: the flight outputs, and a dry run of the draft rules on Flight 1,
   were seen before the freeze. That dry run already gave MOBILE_BUT_TRIVIAL.

-----
2. THE CLAIM AND WHY IT MATTERS
-----
The order listed "only one energy regime was ever studied" as one of the
largest remaining alternative explanations in the Aether record. If freezing
were energy starvation, the TH-009 programme ("a medium that rewrites itself")
would be a parameter-tuning problem. If it is the law, it needs a physics
change. ER01 decides which.

-----
3. DESIGN AS EXECUTED
-----
 - Law aeth01.v1: 2-D torus; five uint8 fields per site (opcode, arg0, arg1,
   payload, energy).
    * A WRITE site with energy >= write cost writes its payload into one field
      of one neighbour. Its aim (arg0 mod 4 direction, arg1 mod 5 field) is
      fixed unless overwritten.
    * Contests are won by a keyed hash re-drawn every tick.
    * Energy settlement: write cost, then maintenance, then rain.
 - ONE axis varied, the energy economy:
     R0 B_balanced        w1 m1 rain 8 @ 1/8   inflow 1.0  (historical)
     R1 C_free_compute    w0 m0 no rain        (historical ECONOMICS regime C)
     R2 rich_rain_x2      w1 m1 rain 8 @ 1/4   inflow 2.0
     R3 scarce_rain_half  w1 m1 rain 8 @ 1/16  inflow 0.5
   R0/R2/R3 differ in one number (rain probability); the rain quantum is fixed.
 - Initial condition: the historical sparse soup (50% WRITE, uniform energy
   0..255). It is identical bytes per seed across regimes (common random
   numbers); energy init is not regime-coupled.
 - Arms: P0 perturbation OFF (primary); P1 historical perturbation 0.1
   (continuity/secondary).
 - Production: 1024^2 x 50,000 ticks (5x the longest prior Aether horizon).
    * P0: 4 regimes x 8 paired seeds.
    * P1: 5 units.
    * 1 determinism duplicate.
    * 38 units, 1.9 M world-ticks, 2 concurrent worlds, 9.04 h measured
      (9.13 h predicted from Flight 2).
 - Observables:
    * late turnover: fraction of sites whose 4 template fields change per tick,
      last 2000 ticks;
    * frozen_strict: no template change at any tick of the last 2000;
    * frozen_net64: historical definition, no NET change over 64 ticks;
    * ever_changed; persistence (last 10% / 50-60% of horizon); t_quiesce;
    * energy state; starve/revive/rain events;
    * attack metrics over the final 64 ticks: share exactly periodic with
      p <= 16, novelty (change reaches a state not held in the previous 16
      ticks), and per-field share.

-----
4. RULES (frozen; RULES.json sha256 57e138b0...)
-----
 - ENERGY_STARVED: late active density < 0.01 AND late turnover < 0.0002.
 - Mobility candidate: paired turnover ratio vs R0 >= 2.0 in >= 80% of seeds,
   AND persistence >= 0.5.
 - Attack (any one => MOBILE_BUT_TRIVIAL):
    * periodic share >= 0.5;
    * novelty <= 0.10;
    * one field >= 0.9 of changes;
    * spatially confined (paired change in late frozen_strict vs R0 not below
      -0.05).
 - Overall label:
    * REGIME_SENSITIVE if any regime is MOBILE_NONTRIVIAL;
    * else MOBILE_BUT_TRIVIAL if any regime is;
    * else REGIME_ROBUST_FROZEN.
 - Gates => MEASUREMENT_FAILED:
    * R0 P1 frozen_net64 outside [0.90, 0.95];
    * duplicate not bit-identical;
    * more than one regime-table hash.

-----
5. RESULTS (P0, 1024^2, 50,000 ticks, 8 paired seeds, medians)
-----
                          R0 B_bal   R1 free    R2 rain x2  R3 rain /2
  late turnover/site/tick 0.002393   0.007523   0.005918    0.000984
  paired ratio vs R0      1          3.14       2.48        0.41
    (seed range)                     3.12-3.17  2.47-2.48   0.41-0.41
  frozen_strict (2000 t)  0.9880     0.9865     0.9880      0.9880
  frozen_net64            0.9942     0.9940     0.9940      0.9941
  ever changed @ 50k      0.3733     0.3736     0.3733      0.3732
  persistence             1.000      1.000      1.000       1.000
  t_quiesce (ticks)       150        100        100         175
  active WRITE density    0.202      0.442      0.374       0.101
  starved WRITE density   0.240      0          0.067       0.340
  energy mean / median    80.3/36    122.7/123  189.4/248   6.0/0
  zero-energy fraction    0.247      0.100      0.067       0.598
  energy at 255           ~0.007     ~0.05      ~0.13       0.0
  novelty (attack)        0.077      0.000      0.001       0.280
  periodic p<=16          0.000      0.110      0.001       0.000
  max field share         0.263      0.395      0.265       0.264
  class                   REFERENCE  TRIVIAL    TRIVIAL     NOT_MOBILE

 - Gates:
    * continuity frozen_net64 0.92589 (historical exact value 0.92592 at
      256^2);
    * duplicate bit-identical (final digest and the full 1000-bin series);
    * one table hash.
 - Changes per active writer per tick: 0.0097-0.017 across all four regimes.
   The rate follows the active-writer count; the extent does not move.
 - P1 secondary arm: perturbation drops the strict late frozen fraction to
   0.683-0.691 in ALL regimes and raises novelty to 0.41-0.52. The net-64
   fraction stays 0.919-0.930. The perturbed medium is also regime-invariant
   in extent.

-----
6. INCIDENTS, AND WHAT THEY VALIDATED
-----
 - Historical provenance gap. The AETH-02 report quotes "92.3% frozen" with
   no committed artifact; the exact rerun gives 0.9259185791015625 (CPU = GPU).
   That figure measures NET change. Under perturbation, the stricter "never
   changed in the window" measure is only ~0.69 (P1 arm). The historical
   "92% frozen" overstated stasis in that sense, and P0 is where the medium is
   genuinely ~99% still.
 - Runner v1 synced to host ~10x per tick. It was repaired between flights
   (digest unchanged, conformance re-run). No other repairs were needed.
 - Kernel throughput on the 5060 Ti is launch-bound up to 1024^2 (~16
   ms/tick per process): lattice area was almost free; seeds and horizon
   were the real costs.
 - Post-hoc probe (NOT preregistered; descriptive). Over the final 200 ticks
   (256^2 x 5000, 2 seeds), the share of template changes on targets
   contested by >= 2 writers is R0 0.68-0.69, R1 0.71-0.72, R2 0.89-0.91,
   R3 0.42. The R2 surplus over R0 is entirely contested flicker: its
   uncontested change rate actually falls. In R1, 29% of changes are
   uncontested yet non-novel; that residue is uncharacterized. A second probe
   column ("contested with an alternative offer") was tautological and is
   disregarded.

-----
7. WHAT THIS DOES AND DOES NOT ESTABLISH
-----
DOES:
 - Within this panel (inflow 0, 0.5, 1, 2; one initial family; P0), the
   EXTENT of medium mobility is energy-invariant to ~0.0015.
 - Energy scales the rate of trivial flicker on a fixed minority.
 - The B-balanced reference reproduces exactly.
DOES NOT:
 - Generalize beyond the initial-condition family. The invariant 37% reachable
   set may be set by the initial aim field.
 - Cover intermittency at fixed inflow (rare, large rain), energy-coupled
   initialization, or very high write costs.
 - Validate the attack against a true positive. No Aether law is known to
   produce rich medium-level rewriting, so the MOBILE_NONTRIVIAL branch is
   uncalibrated.
 - Say anything about content transport, computation, or anything
   organism-like.
Conditionality on thresholds: the near-threshold rate rule (>= 2.0x) decided
only the label (MOBILE_BUT_TRIVIAL vs REGIME_ROBUST_FROZEN), not the extent
finding.

-----
8. DECISION / RECOMMENDATION
-----
Seat lean: CLOSE energy as the explanation for freezing. No further energy
tuning.

Proposed next experiment for TH-009 (HITL's call; not started). It attacks the
mechanism the data point at, the frozen AIM:
 - In aeth01.v1 a writer's target (direction, field) changes only when another
   writer overwrites it, so each writer pins one target and the reachable set
   is fixed early.
 - Test ONE law change in which an executed write re-aims the writer (e.g. the
   writer's own direction advances), so writers sweep their neighbourhood.
 - Measure ever_changed and the late frozen_strict against the same novelty
   and spatial-confinement attack, plus a turnover-matched arbitration-flicker
   null.
Alternatively, first vary the initial-condition family on one axis (WRITE
density), to test whether the 37% reachable set is a property of the law or of
the soup. It is cheaper and directly attacks the strongest alternative.

-----
9. QUESTIONS FOR THE REVIEWER (please try to disagree)
-----
 Q1. Should spatial confinement (a paired frozen-fraction delta) be part of
     the attack, or should it have been part of the mobility screen? Moving it
     would change the label to REGIME_ROBUST_FROZEN without changing any
     number. Is the label choice defensible either way?
 Q2. Is "novelty within 16 ticks" too short a memory? A slow cycle (period >
     16) of a few values would count as novel. Low novelty fired anyway, but
     R3's 0.28 could be partly slow cycling.
 Q3. ever_changed is identical to 4 decimals across regimes. Is that a
     strong law-level invariant, or an almost tautological consequence of the
     shared initial aim field under common random numbers? What test
     separates the two?
 Q4. Is a 4x inflow range plus free compute a wide enough panel to call the
     extent "energy-invariant", or is a regime that couples energy to AIM
     (rather than to activity) the only economy that could matter?
 Q5. With no positive control for MOBILE_NONTRIVIAL, should this kind of
     result be capped at "no evidence of energy-sensitivity" rather than
     "robust"?
 Q6. Is the proposed re-aim law a single-axis change, or does it smuggle in a
     relay mechanism like rcv's (which was killed as "propagates by its own
     writing")?

-----
10. ARTIFACTS
-----
Branch aether/mwo0001-2026-09-28; result commit bae71a02b; freeze 7ce2a58b9.
 - Order (verbatim + manifest): roles/Aether/prompts/2026-10-05_er01/
 - Aether/V2B/ER01/:
    * RESULT.md
    * PREREGISTRATION.md, RULES.json
    * production/ (plan, ledger, 38 unit JSONs, REDUCTION.json,
      posthoc_contest_probe.json)
    * flight1/, flight2/ (records, plans, reductions)
    * phaseA/ (handoff conformance)
    * er01_run.py, er01_reduce.py, er01_flight.py, er01_conformance.py,
      posthoc_contest_probe.py
 - Kernel (unmodified): Aether/runpod/aeth01_canary/aeth01_gpu_kernel.py
 - CPU text: Aether/test/reference/gpu_aeth01.py

+==============================================================================+
| END. A first-class answer remains: "energy regime was never a live           |
| alternative; this was not worth a GPU day", or "the frozen-medium line is    |
| not worth continuing at all." Say so if you think it.                        |
+==============================================================================+
