# GROUNDING REPORT -- Bellerophon Z80 x Atlas bounded grounding round (2026-09-23)

Preregistration: GROUNDING_PREREG.md, frozen at a1b066309 before the first run (plan sha256 f17eadbc...;
grounding_inputs.json sha256 04f7c4af...). Analysis: tools/grounding_analysis.py, committed at 582c42ed2 while the
round was running and before any confirmatory result was inspected. Results: receipts/GROUNDING_RESULTS.json,
receipts/G4_SPECIMENS.json; raw results receipts/GROUNDING_RESULTS_RAW.jsonl.gz (results.jsonl sha256 bc71eeb0...;
run dirs 2.2 GB stay local at C:/Users/James/z80atlas_grounding_2026-09-23/runs). Pinned code: a1b066309.

Execution: started 2026-09-23T12:55:59Z, stopped "complete" 2026-09-23T16:46:50Z (3 h 51 min of a 12 h cap);
12,130 / 12,130 planned runs, 0 NOT_RUN, 0 restarts, plan hash unchanged. 18 workers on SPECTREX5.

## 1. Preregistered predictions -- scorecard

| id | prediction | result | holds |
|---|---|---|---|
| G8 | every control cell as preregistered; replay sample identical | 8/8 cells hold (20/20 each); replay 606/606 byte-identical summaries | YES |
| G1a | COPY/Z80_64 P(spontaneous) > 0 | 5/400 = 1.25% [0.54, 2.89] | YES |
| G1b | CONSTRUCTIVE P(spontaneous) > 0 | 6/400 = 1.5% [0.69, 3.23] (v1 trigger said 0/1,869) | YES |
| G2a | P(SUSTAINED d3 given spontaneous) >= 0.5 | 63/160 = 39.4% [32.1, 47.1] | **NO** |
| G3a | pooled discordant pairs favour EXTERNAL | EXTERNAL-only 178 vs ENDOGENOUS-only 2, p 2.5e-15 (Holm ~0) | YES |
| G4a | median mechanism effect < 0.02 AND transplant CI includes 0 | median 0.000 (holds); transplant +0.016 [0.0025, 0.028] (CI excludes 0) | **NO** (see s4) |
| G5 | two-sided ON vs OFF | 0 discordant triples; TLA 0/100 in every arm; p 1.0 | null (floor) |
| G6a | BUILT_BY_COPY >= 50% | 160/160 (incl. all 87 origins at tick <= 41) | YES |
| G6b | RAMP >= 50% | 83/160 = 51.9% [44.2, 59.5] | YES (barely) |
| G7a | POLLINATION v1 survives where v2 dies; ISOLATED shows no v1/v2 difference | 148 vs 0 discordant, p 2e-15 (Holm ~0); ISOLATED 0 vs 0 | YES |
| G7b | v2 POLLINATION spontaneous within 2 pts of ISOLATED | 1.33% vs 1.33%, difference CI [-3.5, +3.5] | YES |
| P8a | LDIR off lowers P(spontaneous) | 0/300 vs 8/300 base | YES |
| P8b | undefined -> HALT lowers P(spontaneous) | 0/300 vs 8/300 | YES |
| HISTa | intact >= 50% seeded SR AND NOPed <= 5% | intact 297/345 = 86.1% (holds); NOPed 126/345 = 36.5% | **NO** (see s5) |

Confirmatory family (Holm over 3): G3 pooled p_adj ~0; G7a p_adj ~0; G5 p_adj 1.0.
Three predictions failed (G2a, G4a transplant clause, HISTa ablation arm). They are reported as failed. What each
failure means is diagnosed below from the round's own rows -- the diagnoses are EXPLORATORY.

## 2. Instrument integrity (G8) -- the repaired harness behaves as specified

Positive: seeded replicator -> SR births and sustained lineage 20/20; external witness -> verified task 20/20;
seeded hybrid -> SR births 20/20. Negative: EXTERNAL+NEUTRAL -> 0 SR births 20/20; LDIR-off chemistry -> 0
spontaneous 20/20. Cheat: bare-LDIR, self-smear and 1-byte-capture transplants -> 0 spontaneous and 0 transplant-
lineage SR in 20/20 each (they still produce hundreds of COPY_EVENT births per run -- the classifier rejects exactly
those). Determinism: a seeded 5% sample (606 runs) re-executed with identical summaries and first-SR records.

## 3. Replication (G1, G2, G6, G7, P8)

G1 accessibility under the repaired physics (unit = fresh random run; Wilson 95%):
  ENDOGENOUS_PARTIAL 19/400 4.8% [3.1, 7.3]; VM_COPY 8/200 4.0% [2.0, 7.7]; PAIR 12/400 3.0% [1.7, 5.2];
  CONSTRUCTIVE 6/400 1.5%; COPY/Z80_64 5/400 1.25%; BYTECODE32 2/200 1.0%; OVERWRITE 3/400 0.75%.
  Pooled over the G1 lane: 55/2,400 = 2.3%. The forensic estimate 7.2% was pooled over historical topologies INCLUDING
  the P1 channel (v1 POLLINATION alone: 20% in G7P1); in comparable v2 GRID cells the historical and grounding rates
  agree in order of magnitude. Spontaneous self-replication REPRODUCES from genuinely fresh starts.
G1T (task families): FIVE of six task cells are run-for-run IDENTICAL (5/150 each, same ticks, same extinctions);
  SUM2 differs only because it draws two inputs. Diagnosis (exploratory, verified from the rows): with IMPLICIT
  pressure a random population's energy never becomes limiting (inflow 1.0 + 0.5 s >= cost 0.9 + steps/1000), so the
  task score never changes who lives, dies or reproduces -- the task is causally INERT in these worlds. G1T is one
  estimate, not six; "task independence" of replication is by construction, not a finding.
G2 sustained: of 160 spontaneous origins (G1 + G1T + G7 RANDOM), SUSTAINED (depth >= 3 AND alive at tick 500)
  63 = 39.4%; depth >= 10 also 63 (every sustained chain is deep); EVOLUTIONARILY ACTIVE 71 = 44.4%. Prediction
  G2a (>= 50%) FAILED: the forensic 90% came from the trigger-selected subset; unselected origins mostly die out.
  Fresh random worlds are hostile under v2: 95-100% of RANDOM runs in LOCAL/NICHES/GRAPH cells go extinct.
G6 origins: 160/160 first self-replicators are BUILT_BY_COPY. Caveat checked: with lifespan 40 every initial
  organism dies by tick 41, so an origin after tick 41 must be copy-born; but 87/160 origins occur at tick <= 41,
  while initial organisms are still alive, and ALL of those are copy-born too: no initial random tape and no
  mutated initial tape became the first self-replicator in any run. The first self-replicator is built by another
  organism's writes. RAMP (a partial own-copier, >= 25% of the
  window, exists among the writer's ancestors) 83/160 = 51.9% [44.2, 59.5]. Essential steps from the nearest non-SR
  ancestor: 1 step in 72/160, 2 in 23, 3-15 in 24, and ~60 in 13 (reference unrelated). Reading: about half of the
  origins were preceded by a partial copier in their own line and most need ONE decisive byte: a short ramp ending
  in a small step, not a long selectable ramp and not a lucky whole-copier cliff.
G7 topology (v2, fixed allocation, 150 RANDOM + 40 SEEDED per topology): RANDOM spontaneous 2-11/150 everywhere;
  WELL_MIXED worlds (GRID and SOUP) are the only ones that often SURVIVE (extinct 109/150 = 73% vs 144-150/150
  elsewhere) and hold the most sustained lineages (7/150 each vs 0-3). SEEDED replicators sustain in 37-40/40 in
  every topology. Historical direction (WELL_MIXED lowest extinction) is REPRODUCED (exploratory; not preregistered
  as a hypothesis). The historical POLLINATION advantage is gone under v2 (6/150 spontaneous, 145/150 extinct).
G7P1 (causal): POLLINATION v1 vs v2 on identical seeds: extinction 0/150 vs 148/150; spontaneous 30/150 (20.0%) vs
  2/150 (1.3%); mean 2,475 world-made copies per v1 run, 0 in v2. RESERVOIR: 149 vs 150 extinct (its reservoir
  copies, mean 52/run, are too few to rescue). ISOLATED: identical v1/v2 (the built-in negative control). P1 is
  CONFIRMED_CAUSAL: the historical topology effect and most of the historical persistence were world-made copies.
P8 substrate ablations (RANDOM, n = 300 each): base 8 spontaneous; LDIR off 0; LDIR cost x4 0; undefined -> HALT 0;
  mutation LOW 3; VLOW 4. PARTIAL: base 13 vs target_zero 8 (difference within noise). SEEDED (n = 60): base
  sustained 57/60; LDIR cost x4 1/60 (the seeded copier cannot finish within budget); HALT 60/60; LOW 59/60;
  VLOW 59/60 with evolutionary activity falling with mutation supply (60 -> 48 -> 11 of 60). Causal orientation:
  replication is reachable ONLY through LDIR plus the neutral undefined-byte slide; removing either abolishes it.
  Preserved target bytes are not required (13 vs 8 of 300, within noise). Mutation supply: access 8 / 3 / 4 of 300
  (MED / LOW / VLOW, not distinguishable at this n); evolutionary activity of seeded lineages falls with supply.

## 4. Beneficial-neighbourhood mechanism (G4)

Specimens: 11 (10 historical top-paired-gain + only 1 grounding G1 specimen -- COPY/Z80_64 produced 5 origins, of
which 1 dominant tape self-copies alone; the preregistered target of 30 was not reachable). Graftable 6.
Mechanism effect BD(X) - BD(X nopped): median 0.000, mean 0.007 [0.000, 0.021]. Transplant effect +0.016
[0.0025, 0.028] -- the CI excludes 0, so G4a formally FAILS on that clause. Diagnosis (exploratory, executed):
the whole positive effect sits in three routine+witness grafts whose task score is 0 -- the grafted LDIR routine
(C = 0 -> a 256-byte sweep) overwrites the input region, destroying the witness; 98 of the 115 "beneficial"
mutants (85%) are mutations that BREAK the copier (positions 1-7, inside the routine). The reproductive machinery
raises the density of beneficial mutations only in the sense that it damages the task and mutations that remove
it help. Verdict: the historical "reproductive machinery raised beneficial density" is FALSIFIED; the effect that
exists has the opposite meaning (reproduction-computation ANTAGONISM). Underpowered (n = 11).

## 5. Historical specimens (HIST)

345 historical origin tapes transplanted into fresh v2 random populations: 297 (86.1%) self-replicate as the
transplant lineage and 260 (75.4%) sustain -- historical replicators are genuine and robust to fresh seeds and
fresh memory. The ablated arm (every LDI/LDIR/COPYALL byte NOPed) still self-replicates in 126 (36.5%) -> HISTa
FAILED. Diagnosis (exploratory, from the rows): in 124/126 the rescuing writer carries a copy instruction at a NEW
position (not a reversion; 2 reversions), 1-18 bytes from the ablated tape, often within a few ticks. The
setup code (T pointed at the window) plus the undefined-byte slide makes a copier ONE mutation away at many
positions: NOPing the copy byte is not a knockout in this chemistry. This is the same fact G4, P8 and the
neighbourhood scans show from other angles: the replication basin is shallow and wide around any tape that already
has the setup.

## 6. Reproduction versus task (G3, G5)

G3 (seed pairs, identical initial populations, external offspring mutation matched to exact copies): verified task
reached -- EXTERNAL-only 178 pairs, ENDOGENOUS-only 2 (pooled p 2.5e-15). SEEDED_HYBRID/EXPLICIT/INC: external 100/100,
endogenous 2/100; COND_ONE: 45 vs 0; RANDOM/EXPLICIT/INC: 35 vs 0; IMPLICIT cells: no reaching in either arm (the
task is inert under IMPLICIT, s3). The historical 4x external mutation (extmut4) cell: 0 vs 2 -- mutation supply is
not what separated the historical arms. Offspring quantity is NOT matched: endogenous hybrid worlds registered ~95k
births vs ~15.5k external. Reading: under endogenous reproduction the copy routine is what is selected (fitness =
copying) and the seeded task code decays; under external reproduction selection sees the task score. CONFIRMED_CAUSAL
for "reproduction mode causally changes task retention/reaching" in this design, in the direction OPPOSITE to the
historical flag.
G5 (ON / OFF / ALT, seeded replicators): task-linked reproductive architecture 0/100 in every arm (upper bound
3.7%); executed-code extent of the dominant replicator identical ON vs OFF in 98/98 triples (the seeded 8-byte
copier stays dominant); ALT reached ECHO in 10/100 runs but never in an SR tape. No architecture response to task
at this scale; the historical ON>OFF "compression" association (max-PC of a junk event) does not reproduce with a
structural descriptor -> FALSIFIED as a task-driven architecture effect (a response > 3.7% of triples is excluded).

## 7. Comparison with the long campaign

REPRODUCED: spontaneous own-code self-replication from fresh random populations; deep lineages and transmitted
variants when a lineage takes hold; WELL_MIXED persistence advantage (exploratory); EXTERNAL > ENDOGENOUS at reaching
verified task solutions (now causal, one-axis design). NOT REPRODUCED / REMOVED: the POLLINATION topology effect
(was P1), the ENDOGENOUS > EXTERNAL flag (reversed), beneficial-density gain (instrument noise; the real effect is
antagonism), task-driven architecture change (null), reservoir crossing, incremental-not-atomic. NEW: under
repaired physics fresh random worlds almost always die (95-100% in LOCAL/NICHES/GRAPH); replication access is 1-5% per run;
the task is causally inert under IMPLICIT pressure; the copy primitive is one mutation away from any tape carrying
the setup (a wide, shallow basin); reproduction and computation are antagonistic, not coupled.

## 8. Phenomenon verdicts (directive Phase 10) -- each separately, never one campaign score

| phenomenon | forensic stage | grounding | FINAL |
|---|---|---|---|
| spontaneous own-code self-replication (fresh random populations) | REPRODUCED_ASSOCIATION (traced) | reproduced: 1-5% of fresh runs per physics; 86% of historical origin tapes self-replicate in fresh worlds | CONFIRMED_CAUSAL (P8: requires LDIR and the undefined-byte slide; ablation abolishes it) |
| sustained lineages after an origin | 90% of trigger-selected origins | 39.4% of unselected origins [32, 47]; 75% of historical specimens | REPRODUCED_ASSOCIATION (rate lower than the forensic estimate: selection bias exposed) |
| evolutionarily active lineages (transmitted variants) | 188/346 | 44% of origins; falls with mutation supply | REPRODUCED_ASSOCIATION |
| first self-replicator built by other organisms' copies | 65% historical | 160/160 (87 while initial organisms lived) | REPRODUCED_ASSOCIATION |
| incremental construction (ramp) | not measurable historically | 52% with a partial copier in line; mostly 1 decisive byte | PROVISIONAL (a short ramp + small step; selectable advantage of intermediates not tested) |
| REACHED_UNDER_ENDOGENOUS_NOT_EXTERNAL | FALSIFIED (reverse 1,554 vs 443) | reversed causally: EXTERNAL 178 vs 2 | FALSIFIED (opposite CONFIRMED_CAUSAL) |
| REPRODUCTIVE_MACHINERY_RAISED_BENEFICIAL_DENSITY | INSTRUMENT_FAILURE | paired effect 0; the residual effect is copy-task antagonism | FALSIFIED |
| REPRODUCTIVE_ARCHITECTURE_RESPONDED_TO_TASK | CONFOUNDED | structural descriptor: no response (0/100, bound 3.7%) | FALSIFIED (at this scale) |
| REACHED_INCREMENTAL_NOT_ATOMIC | DETECTOR_ONLY | not retested (ruler artefact) | DETECTOR_ONLY |
| RESERVOIR_CROSSED_MOAT | FALSIFIED | reservoir copies too few to matter (G7P1) | FALSIFIED |
| POLLINATION / topology effect | CONFOUNDED (P1) | P1 causes it: extinction 0/150 v1 vs 148/150 v2 | INSTRUMENT_FAILURE (defect P1), now removed |
| WELL_MIXED persistence advantage | exploratory association | extinct 73% vs 95-100% | REPRODUCED_ASSOCIATION (exploratory) |
| task independence of replication | apparent | task causally inert under IMPLICIT (G1T identical) | NOT_ADJUDICABLE (design: the task never reaches the dynamics) |
| moat crossing / task_score / novelty / escape / transport triggers | DETECTOR_ONLY | retired | DETECTOR_ONLY |

## 9. Readiness answers (directive Phase 10)

1. Survived: spontaneous own-code self-replication (now causal: requires LDIR + the NOP slide), its lineages and
   variant transmission, origin-by-construction, WELL_MIXED persistence (exploratory), EXTERNAL > ENDOGENOUS at
   retaining/reaching task solutions.
2. Collapsed: all five high-value flag classes; the topology effect; the 90% sustain rate; "beneficial density".
3. Defects: 34 ledgered rows (ISSUE_AND_REPAIR_LEDGER.md), incl. two the blind audit did not find (P1, H1)
   and the latent resume defect (s3), all repaired behind tests (39/39).
4. Historical rows valid: every raw number is valid (bit-for-bit replay, also through the repaired harness);
   the per-row interpretation status is in the ledger and SPECIMEN_LEDGER.jsonl (2,188 rows).
5. Detector definitions changed: SELF_REPLICATION by provenance; verified exact solving of the configured task;
   horizon tails; paired geometry; spontaneity excludes init_tapes; v1 triggers/flags retired for adjudication.
6. Grounding reproduced: replication access, lineages, construction origins, the P1 cause, the EXTERNAL advantage;
   it did not reproduce any flag class.
7. New uncertainties: why unselected origins mostly die (competition vs overwriting vs hostile random neighbours);
   whether ramp intermediates had selectable advantage; whether any coupling of reproduction to computation is
   reachable at all (G5 floor, G3, G4 antagonism).
8. Ready for another multi-day run? The INSTRUMENT is ready: controls 8/8, replay 606/606, repaired physics and
   detectors, resume path tested, pinned-code launch proven. The SCIENTIFIC DESIGN is NOT ready for a multi-day
   run in the current physics: under repaired physics the task is causally inert (IMPLICIT) or selected against by
   the copier (endogenous EXPLICIT), so a long run would spend its budget re-measuring extinction and uncoupled
   copying.
9./10. Exact blocker: there is no pathway by which computation affects reproductive success under endogenous
   physics (energy is never limiting, reproduction costs nothing task-related, and the copy routine antagonises
   the task). Before a 2-3 day campaign: design ONE coupling mechanism (NEXT_CAMPAIGN_RECOMMENDATION.md part B),
   add its positive/negative/cheat controls, and run a bounded (<= 6 h) preregistered pilot that must show the
   coupling moves task retention in a matched design. Then launch.
