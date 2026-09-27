# Ananke spikes 2026-09-27 -- PLAN (committed before any spike runs)

Scope: bounded mechanism probes on the C1/C1b specimens after PTE-C1b.
These are NOT a campaign and not a prereg for promotion. They are cheap
discriminators whose predictions and decision rules are fixed here,
before the data. The frozen C1b code is not touched. Probes live in
prometheus/ananke/lens.py and act on engine state only BETWEEN ticks, so
the physics is unchanged. Host: M1 GPU, measured free at 19:08Z (5%, no
other seat's compute). Worlds: analysis namespace 0x5E1 (new), 64 worlds
= 32 mirror pairs, 12 trials. Unit: mirror pair. CI: 99% bootstrap, as
C1b. Every Attempt, failed or not, is kept in SPIKES_2026-09-27_LOG.md.

Mirror-pair logic. Worlds 2p and 2p+1 share ALL exogenous randomness and
have negated cue and target sequences. Swapping a carrier X between the
two partners at mid-gap therefore hands each world its partner's version
of X. If X carries the bit, the trial's answer follows the partner:
per-trial accuracy goes toward 1 - normal, i.e. BELOW 0.5. If X carries
nothing, accuracy stays at normal. This is the sharpest carrier test PTE
allows: FLIP means "carries the bit", NO-EFFECT means "does not", and
CHANCE means "needed but not sufficient".
Decision rule per swap, on per-trial accuracy over the swapped trials:
  FLIP       hi99 < 0.40
  NO-EFFECT  lo99 >= normal_lo99 - 0.05
  CHANCE     otherwise (disrupts without transferring the bit)

## S-M2 (HOLD 4ab2ba01; plus the 3 fresh SIGNAL champions, regenerated
## deterministically from their stored search seeds)
All interventions are applied at each trial's mid-gap tick (C1b t_m),
after that tick.
  D1 swap_inflight      Msum and Mcnt (all slots) swapped with the partner
  D2 swap_sitestate     S, Acc_sum, Acc_cnt, w, Kp, E swapped
  D3 swap_payload_only  Msum swapped, Mcnt kept (content, not counts)
  D4 swap_counts_only   Mcnt swapped, Msum kept
  D5 swap_pay0 / D6 swap_pay1   one payload component swapped
  D7 slot_roll +1 / -1  in-flight ring rolled one slot (timing shifted by
                        one tick, content kept)
  D8 recipient_roll     in-flight recipients rolled by +1 site (topology
                        shifted, timing and content kept)
  D9 swap_w_only        routing weights only
Predictions (Ananke): D1 FLIP; D2 NO-EFFECT or small; D3 FLIP (content,
not counts); D4 NO-EFFECT; D6 FLIP, D5 NO-EFFECT (the code is in payload
component 1, which the C1b census never read: P=2, and the census used
component 0 only); D7 CHANCE or small (a delay line tolerates a +-1
shift only if the readout is not phase-locked); D8 CHANCE; D9 NO-EFFECT.
Analysis-first descriptive decoders at t_m (fit sign map on the first
16 pairs, score on the last 16, permutation p): sign of total pay0, pay1;
the same restricted to packets addressed to the actuator; total count;
count to the actuator; arrival-slot centroid to the actuator. A decoder
counts as MECHANISTIC only if its swap (D3-D6) FLIPS.

## S-M3 (MAJ 0a23398f, f6b623cd)
  E1 rule census: per tick, the fraction of sites whose r differs between
     mirror partners (a cue-dependent configuration) and the fraction
     changing r (configuration dynamics).
  E2 configure-then-freeze: freeze_rule from the start of trial 2 (after
     two trials of free SETRULE); score trials 2-11.
  E3 swap_r at the mid-point of each trial's delta (before transport lands).
  E4 reset_r to r0 at the same tick.
  E5 emission count under freeze_rule vs normal (does SETRULE gate
     transport?).
Predictions: E1 cue-dependence of r < 5% of sites; E2 accuracy stays
within 0.05 of normal (configuration settles and needs no maintenance);
E3 NO-EFFECT; E4 CHANCE; E5 freeze_rule changes emission counts
(SETRULE enables transport).

## S-F temporal coverage (C1 D-wave comm cells + M2 + M3)
Single-cue twins: a world and its copy differing ONLY in trial k's cue.
At each tick, record whether the delivery to the actuator differs between
the twins. That gives the arrival-lag profile of cue-bearing deliveries
relative to the readout tick. Report, per cell, the fraction of that mass
at lag 0 (missed by C1's window) and the earliest and latest lags.
Prediction: M3 cells ~100% at lag 0; RELAY cells < 30% at lag 0.

Stop rule: 45 min of wall time for all spikes; anything unrun is noted.
