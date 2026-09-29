# W-D: interventions that could not have fired -- REPORT

(Saved by Ananke from W-D's final message. The worker's own Write of this
file was refused by the harness. Content as delivered; the worker ran no
experiments and executed no other seat's code.)

All cases were verified from primary files on origin/main.

## Case table

1a PTE C1 M3, "packet ablation does nothing -> SETRULE carries it".
   Intervention: drop arrivals over [t0, readout). WINDOW: delay == delta
   == 4, so every cue-bearing arrival lands on the readout tick
   (spikes/out/s_f.json: M3 lag-0 share 1.00, C1-window share 0.00; C1b:
   C1 window 0.697/0.686 vs corrected 0.501/0.500; pte/C1_ERRATA.md E1).
   Found by the author re-reading code, then re-derived by Aporia #640.
   Catch: reach counter + a delay==delta relay plant. Cost: 25 s wall.
1b PTE C1 M3, "frozen routing no effect". INERT CHANNEL: under dest_mode
   "all" w is never read (E2). Catch: a plastic-routing plant that
   freeze_routing MUST drop. Cost: 1 run.
2a Nestor C9 H1, "cue gating no detected effect" (M = I = 0.0). UNWIRED
   SWITCH: world.Runner stores output_gate / cue_cost, but no TaskSpec
   receives them. The four arms are identical to the last decimal
   (z80atlas-verify-2026-09-22/observatory/C9_OUTCOME_AND_ADDENDUM.md).
   Catch: a fail-on-old-code gate, i.e. a hand answer-before-read guesser
   run through the arm's own Runner (repaired 0.0 vs 1.0; old 1.0 vs
   1.0; c9x-explore-2026-09-24/c9_h1r/GATE.json). Cost: 4 competence
   calls, seconds.
2b Nestor cycle 8 A-3, FORCED_READ. WRONG TARGET: tasks.episodes() sets
   base = v XOR key and adds a third input (z80atlas-2026-09-19/tasks.py
   L105-108), so the arms score different targets. Catch: an arm-diff of
   actual inputs/targets on one seed; only the declared factor may
   differ. Static, seconds.
3a Archaeon SFE-01 attempt 1, "failures help". CONDITION NEVER MET:
   tabu_hits = 0 in 9/9 rows. Cell-label RNG seeding made the 0-hit
   control read 0.31 vs a 0.07 baseline: a SPURIOUS POSITIVE (DECISIONS.md
   D-007/D-008; LEDGER.jsonl L-007/L-008). Catch: an applied count per arm
   + common random numbers, so a 0-hit arm equals the baseline exactly.
   Free.
3b SFE-05 adaptive curriculum. DEAD BRANCH: the down-rule never fired;
   the up-rule never fired in 2/3 seeds (SFE-05/RECORD.md E, F). No null
   was read; recorded as untested. Catch: a firing count per rule. Free.
4  Aether AETH-03, "propagation needs active matter". FORCED BY
   CONSTRUCTION: influence travels only by emission, and energy 0 cannot
   emit, so full-ring starvation had to block (0/128 vs sham 17/128). The
   specified OFF arm was underpowered: 3.1% of origins reach radius 8
   (PHYSICS_DESIGN_02_2026-09-26.md s4.1). Catch: a could-fail control (a
   law variant where the hypothesis is false) + a count of origins able to
   show the effect. One derivation or one run.
5  Bellerophon (BEE) G1T, "replication is task-independent". INERT
   PATHWAY: energy inflow 1.0 + 0.5*score always covers cost 0.9 +
   steps/1000, so the score never decides survival; 5 of 6 task cells are
   identical run for run (roles/Bellerophon/forensics_2026-09-23/
   GROUNDING_REPORT.md s3). Catch: check the inequality, or plant twins at
   score 0 and 1 that must differ in survival. Zero runs.

Guards that existed and could not see 2a: Nestor NPE calibration
controls.py (10/10 PASS; tests the VM and the task, not the world->task
handoff); SFE runtime inert-intervention findings (sfe/runtime.py
~L640-700: compares declared fields with the values the child carries;
D16's value was carried, just never consumed).

## Generalization

Five kinds, following mutation testing's RIPR (Reach, Infect, Propagate,
Reveal):
- REACH: the switch is never set, or its condition never holds (2a, 3a, 3b).
- INFECT: set but never read by the pathway (1b, 5).
- PROPAGATE: the state changed, but not within the readout's window (1a).
- WRONG TARGET: a confound (2b).
- FORCED OUTCOME: the result could not have been otherwise (4).

One pattern covers 5/8: a PLANT whose output depends on the claimed
pathway, run through the arm's OWN code, must be flipped by the
intervention (and not by the old code), with a REACH COUNTER beside every
null. Mechanism-in-isolation calibration passed D16; going through the
arm's code is the key.
Free alarm: under common random numbers, an arm IDENTICAL to its control
means the intervention never took effect (flags 2a, 3a, 5). Without
common random numbers, an inert arm produced a false positive (3a), so
reach matters for positives too.
Escapes: 2b needs an ARM-DIFF (only the declared factor differs). 4 needs
a COULD-FAIL counter-plant plus a count of eligible units.
JUDGEMENT: no single pattern generalizes. Three checks (plant-through-own-
code + reach counter; arm-diff; could-fail counter-plant) plus the
identical-arms alarm cover all 8 cases. Caution (Hauser, Ellsworth &
Gonzalez 2018): an embedded check can itself intervene. Reach counters
must not consume world RNG (the D-007 divergence).

## Proposed follow-up Threads (Ananke only)
T-D1 A reach counter for every lens intervention, beside each verdict.
T-D2 A plant library: must-flip and must-not-flip plants per intervention
     type, run through lens.run.
T-D3 An ARM_IDENTICAL flag when an arm equals its control on all mirror
     pairs.

Sources: RIPR (arxiv.org/pdf/2410.21904; Cornell CS5154 mutation-testing
notes); Hauser, Ellsworth & Gonzalez, "Are Manipulation Checks
Necessary?", Front. Psychol. 2018.
