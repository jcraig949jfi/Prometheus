# Ananke research program 2026-09-27: temporal computation and distributed memory

The integrated product, with pointers into roles/Ananke/research/.

1 ADVERSARIAL READING OF C1b (C1B_REVIEW_AND_MECHANISMS s1). One real
  error: "the signed payload sum is not the encoding" came from a census
  that read only payload component 0. Two claims were too weak: routing's
  role in M2 (disruption, not storage) and SETRULE as configuration (now
  shown). One claim was right for a slightly wrong reason: M3's deadline
  is really "after the previous wake and by the readout". The C1b labels
  stand as computed; the reading changes.

2 M2 (the plausible specific carrier is identified): a TUNED TWO-STAGE
  ECHO. The cue leaves on payload component 0 and is re-emitted on
  component 1 by the neighbours. It lands back at the actuator 0-2 ticks
  before readout, which overwrites S0 with that tick's arrivals. Carrier:
  the sign of the in-flight sum of one component (decoder 1.00; swap of
  that component FLIPS; counts, timing, destinations, routing and site
  state do not carry it). The same code in 3/3 fresh champions (one on
  the other component). It is tuned to the trained gap: at chance at gap
  >= 12.

3 M3: transport riding in flight (swap FLIPs) with a staleness-bounded
  readout, on a population configured by a ONE-TIME SETRULE BOOTSTRAP
  (every site converges to rule 0 in trial 0; rule state never cue-
  dependent; freezing SETRULE afterwards changes nothing; freezing it from
  the start cuts emissions 4x).

4 EXTERNAL RESEARCH (PRIOR_ART_..., ~45 sources, graded). Most
  decision-relevant:
  - Chandy-Lamport channel state is the right name for M2's carrier.
  - Lizier et al. show storage at the loop level = transfer at the edge
    level, so our "memory vs transport" split was primitive.
  - Delay lines and bundled-data pipelines are the known mechanisms PTE
    rediscovered.
  - Activity-silent working memory maps to M3's configuration, not to M2.
  - GA-evolved CA particle computation (Das-Mitchell-Crutchfield) sets
    the proof standard: a reduced carrier model that predicts the tuning
    curve.

5 MEMORY / TRANSPORT / TIMING / CONFIGURATION (MEMORY_INTERVENTIONS).
  One operational rule, the mirror-pair CARRIER SWAP:
  - FLIP = carries the bit;
  - NO-EFFECT = irrelevant;
  - CHANCE = needed but not carrying it.
  Distinctions are kept only where a swap separates them. Dropped:
  "transient configuration", "temporal state" as a class, "phase".

6 TEMPORAL-INTERVENTION LESSON (TEMPORAL_INTERVENTION_COVERAGE). The C1
  window covered 0% of the cue-bearing arrivals in both M3 cells and
  69-100% elsewhere. It is one case of a fleet-wide shape, "an
  intervention that could not fire": window miss, channel inert by
  physics, switch never wired. Remedy: a reach check
  (cue_arrival_profile). Carrier swaps largely sidestep window choice.

7 CROSS-ENGINE (CROSS_ENGINE_THREADS). Genuine connections:
  - Aether: timing carries there, where content carries in PTE.
  - Cosmos: P1/P2 present vs used, with a deliberately timed swap.
  - Archaeon: FF-20; M2 is load-bearing, non-material state.
  - Fleet-wide: "cannot fire" failures in 4 seats.
  - Herakles EvCA: step-T vs stable readout.
  The rest are terminology matches only.

8 ENGINE CARD (PTE_ENGINE_CARD). PTE is the fleet's lens on CHANNEL
  STATE with exact counterfactuals.

9 BACKLOG (BACKLOG_TEMPORAL_DISTRIBUTED). About 25 Threads in 6 areas,
  with a consumption log.

10 RESEARCH-READY THREADS (threads/): T-M2-2 interval tuning, T-M3-1
  SETRULE as init escape, T-INS-1 carrier-swap assay, T-TA-1 temporal
  reach, T-X-1 content vs timing with Aether, T-EXT-1 prior-art
  instruments. Each is 2-4 h, CPU-scale, from git alone.

11 SPIKES EXECUTED (SPIKES_2026-09-27_PLAN/LOG; ~20 min of GPU). Plan
   committed before any run.
   - Predictions held: 15. Lost: 5 (delay +1 tolerance, recipient roll,
     E4 reset_r, one RELAY lag share, and site/joint carriers in 3 cells).
   - Failures kept: 1 script bug, 1 infeasible arm.
   - What they changed: M2 decoded; M3 settled; carrier heterogeneity
     found (T-CT-1); first joint carrier (MAJ 4781b0a1); "is M2 memory?"
     reframed as interval tuning.

12 CHALLENGES
   - To the operator brief and my C1b text: the payload sum IS the code,
     on the other component.
   - To "memory" for M2: it schedules, it does not store.
   - To "self-modifying" for M3: it is a bootstrap, possibly an init
     artefact.
   - To C1's family labels: they hide carrier diversity.
   - To C1b's mechanical labels: they are weaker than a carrier swap.

13 C2 / SI01 (C2_SI01_REVIEW). Neither as designed.
   - C2: re-derive as a carrier-resolved load map (C2') after the carrier
     assay exists.
   - SI01: not on HOLD/M2, because a tuned echo forgets by delay, not by
     relevance. First run a cheap retention census; if PTE has no
     non-trivial retention, PTE is the wrong SI lens.

14 AUTONOMOUS WORK (no HITL needed). The six READY threads, T-CT-1, and
   T-DM-2 mapping. All are CPU-scale, bounded, planned-then-run, and use
   no cloud.
