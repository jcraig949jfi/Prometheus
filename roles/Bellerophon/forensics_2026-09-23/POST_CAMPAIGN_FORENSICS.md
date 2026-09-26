# POST-CAMPAIGN FORENSICS -- Bellerophon Z80 x Atlas 72-hour campaign (2026-09-19 .. 2026-09-22)

Seat: Bellerophon[m2-9e74888e], SPECTREX5 (M2). Directive: prompts/2026-09-23_post_campaign_forensics/ (sha256
ecfd746d...96796). Branch bellerophon/post-campaign-forensics-2026-09-23. Evidence (READ-ONLY, local):
C:/Users/James/z80atlas_campaign_2026-09-19 -- file hashes in EVIDENCE_MANIFEST.md, run-dir root digest
0119e2413f59... in receipts/RUNDIR_DIGEST_ROOT.json. Every number below is recomputed from raw files by a committed
tool under tools/ and stored in a committed receipt under receipts/. All analyses of the long campaign are
EXPLORATORY (the campaign was not preregistered for these questions); confirmation is the grounding round's job
(GROUNDING_PREREG.md, GROUNDING_REPORT.md).

Status vocabulary (directive Phase 10): CONFIRMED_CAUSAL / REPRODUCED_ASSOCIATION / PROVISIONAL / DETECTOR_ONLY /
CONFOUNDED / INSTRUMENT_FAILURE / NOT_ADJUDICABLE / FALSIFIED.

## Headline

The campaign's five high-value flag classes (1,629 flag events) do not survive adjudication: two are FALSIFIED,
one is INSTRUMENT_FAILURE, two are CONFOUNDED / DETECTOR_ONLY. One phenomenon survives the forensic stage intact:
spontaneous, own-code self-replication does arise from random populations and forms deep, variant-transmitting
lineages (s3.1). Two new CRITICAL defects were found beyond the independent blind audit's list: world-made copies
under endogenous physics (P1) and an un-relocated seeded hybrid (H1). All demonstrated defects are repaired behind
tests; the historical instrument remains replayable bit-for-bit.

## 1. Reconstruction of the final campaign (Phase 1; receipts/CENSUS.json)

1.1 Wall time. start 2026-09-19T14:39:46Z, stop 2026-09-22T14:38:42Z (72.00 h window; last summary written at the
stop second). One start, one stop: 0 resume, 0 halt, 0 finalize decisions -- checkpoint restoration never ran.
Throughput 744-1,300 completions per hour; largest gap between completions 126.5 s (two occurrences): no worker
stall. Summed run wall 592.2 CPU-hours (median run 25.5 s, max 194.3 s).

1.2 Runs. 63,247 submitted = 63,247 completed = 63,247 run dirs (ids r000001..r063247 contiguous, no duplicates,
none missing, every dir has config+summary; 49,282 have geometry.json, 13,965 do not -- runs with no top specimen).
Failed/voided: 0 (the pool would have raised; runs.jsonl, families.jsonl and state.json agree: 63,247).
By kind: exploration 18,594; control 11,079; promoted 19,095; verification 10,667; intervention 3,808;
positive_control 4. By stage: early 17,892 (to 2026-09-20T12:15:58Z), middle 30,880, late 14,475
(from 2026-09-22T00:18:00Z). kind x stage: exploration early 8,944 / middle 9,650; control early 8,944 / middle 2,135;
promoted middle 19,095; verification late 10,667; intervention late 3,808.

1.3 Families. 49,412 (one per distinct factor vector; family id ignores init_tapes -- M5). 39,613 have exactly one
run; runs per family 1..8. Promoted 31,196 (63%); retired 18. Promotions by the kind of the promoting run:
promoted 9,861, exploration 8,485, control 5,662, verification 5,262, intervention 1,926. Promotion lineage depth
(parent chain): 0: 18,569, 1: 15,809, 2: 7,876, 3: 4,093, 4: 1,837, 5: 786, 6: 300, 7: 103, 8: 30, 9: 9.
Trigger-score histogram over all runs: 0: 6,468; 1: 13,000; 2: 13,706; 3: 10,649; 4: 7,708; 5: 5,392; 6: 4,028;
7: 2,004; 8: 278; 9: 13; 10: 1. Promotion needed score >= 2, which 69% of runs reach: promotion does not
discriminate (M8).

1.4 Seeds and duplicates. 47,444 distinct seeds over 63,247 runs (matched pairs share seeds by design). 49 exact
(vector, seed) duplicates = 97 verification runs, byte-identical simulations counted as replicates (m1). Late-stage
matched controls took the first seed of their BATCH (M6): 5,156 of 6,859 late controls are not seed-matched to their
own treatment; one seed was reused 22 times.

1.5 Coverage. 1,802 factor pairs covered. Runs by reproduction: EXTERNAL 22,159; ENDOGENOUS_COPY 17,624; PARTIAL
8,360; OVERWRITE 6,258; PAIR 4,456; CONSTRUCTIVE 4,390. By init: RANDOM 26,050; SEEDED_HYBRID 19,728;
SEEDED_REPLICATOR 11,237; SEEDED_WITNESS 6,232. By task: every task 11.6k-12.9k runs. By topology: NICHES_POLLINATION
received the MOST runs (9,655) -- promotion steered allocation toward the topology the P1 defect inflated
(s2.4) -- vs GRID/LOCAL 1,765. Mutation regimes: 12 operator x rate cells, 4,544-6,076 runs each.

1.6 Positive controls. All five PASS (graded once at 14:40:43Z). The two controls sharing family 66a8a32b055dfed1
were graded on the family's LAST run only (m4); re-read: r000001 and r000004 each pass BOTH predicates. The
const-witness check was vacuous (m4); the witness does solve CONST when checked for real (test_m4).

1.7 Flags. flags.json holds 1,629 events: REPRODUCTIVE_ARCHITECTURE_RESPONDED_TO_TASK 600 (495 families, 600 runs),
REPRODUCTIVE_MACHINERY_RAISED_BENEFICIAL_DENSITY 493 (438 families, 493 runs), REACHED_UNDER_ENDOGENOUS_NOT_EXTERNAL
393 (393 families), REACHED_INCREMENTAL_NOT_ATOMIC 136 (136 families), RESERVOIR_CROSSED_MOAT 7 (7 families).
Union: 1,297 distinct families. Family-level overlaps: ENDO & ARCH 60, ARCH & BD 47, ENDO & BD 25, INCR & ARCH 23,
INCR & ENDO 20, INCR & BD 13, RESERVOIR & anything 0; run-level ARCH & BD 8. The five classes are NOT independent
events and are not summed as such. Temporal appearance: the two run-level flags occur at 0.1-0.3% of fixed-lane runs
in every 6 h window (flat), but at 1.5-3.7% of promoted/verification runs in the late stage (s2.1).

1.8 Reconciliation with earlier numbers (receipts/SNAPSHOT_SOURCES.md; tools/snapshot_recon.py). Every earlier
Bellerophon number was a live-status snapshot quoted in this seat's session transcript (c95cc146), never committed:
0.06 h (36 runs), 1.3 h (1,060 runs, 15 flags), 12.1 h (10,084 runs, 108 flags), 18.7 h (15,556 runs, 169 flags),
44.63 h (37,732 runs, 33,333 families, 18,309 promoted families, 446 flags = 185/119/104/33/5 in the order
ENDO/BD/ARCH/INCR/RES, "spontaneous replication fires 276"), 71.98 h (== final). The directive's "276 replication
flags" is the spontaneous_replication TRIGGER count at 44.6 h (recomputed 275 at runs.jsonl line 37,732; the one-run
gap is 13 s of completion between the status call and the count); it was never a high-value flag class. Final
value of that trigger: 544 runs / 471 families. The 44.6 h snapshot precedes the late stage (actual start 57.64 h,
not the 50.4 h predicted at the time), so it contains 0 verification and 0 intervention runs; most flag growth after
44.6 h is late-stage verification of the top families (s2.1). "Promoted" meant families in the status output
(18,309 at 44.6 h) but runs of kind promoted in the counters (12,283 at 44.6 h). Two "spontaneous" series existed in
the transcript: runs whose FIRST COPY EVENT was unseeded (5,854 at 18.7 h; 24,458 final -- mostly junk copy events,
s3.1) vs the trigger (84 at 18.7 h; 544 final). The 44.6 h flag split cannot be re-derived from flags.json (not
stored in time order); the transcript is its only evidence. Separately, STATUS.md at 2df98af3e mislabels
archaeon/z80atlas as Nestor's build (it is Archaeon's). No Archaeon or Nestor number is used anywhere here.

1.9 Experimental units. A RUN is one independent random initial population (distinct seed) -- the unit for any
per-run rate. Runs of one family share a factor vector: family-bootstrap CIs are reported. Promoted descendants of a
family are new vectors, not replicates, and carry no evidential weight as "reproductions". A matched PAIR is a unit
only where seeds were actually matched (exploration-stage pairs; NOT late-stage controls, M6). Organism-level
events (births, copy events) are never independent samples.

## 2. Mining (Phase 2)

2.1 Temporal dynamics (receipts/TEMPORAL.json; rates per 6 h window by completion time). FIXED lane (exploration
runs; allocation independent of promotion): exact solve 2.7-4.3% (trend z = -0.57), hifi replication predicate
13.6-16.9% (z = 0.04), extinction 42.7-45.7% (z = -1.21), persistence z = 1.1, the two run-level flags flat at
0.06-0.3%. Spontaneous-trigger rate 1.2-3.6% (z = 2.07, driven by one window; exploratory, uncorrected). PROMOTED
lane (promoted + verification + intervention): every rate rises steeply (hifi z = 53.7, persistence z = 42.0, exact
solve z = 20.5, ARCH flag z = 13.8, BD flag z = 10.0) with a jump at the late stage (window 9). Reading: no
acceleration, saturation or phase transition in what the substrate produces per run; the late-stage "surge" is
allocation feedback (the strongest families rerun), i.e. exposure, not discovery.

2.2 Family structure / independent origins (receipts/ORIGINS.json; tools/origins.py). Origin unit = the run: every
non-intervention RANDOM-init endogenous run is an independent random population, and contributes at most ONE origin
(its first SELF_REPLICATION writer); descendants and within-run re-origins are never counted; promoted families are
new vectors, not relatives of an organism. Pool: 14,910 such runs. Trigger set: 502 runs, fully traced: 346 contain
SR. Untriggered: 14,408 runs, 296 traced at random: 15 contain SR (5.1%, Wilson 3.1-8.2%). Estimated origins
~1,076 (346 censused + ~730 extrapolated), i.e. 7.2% of fresh random runs (95% CI 4.8-9.6%). The trigger missed more
origins than it found. MECHANISM clustering (assumption: origins with the same copy opcode and first-write source
offset use one route; setup-code multisets are a finer key): 361 origin tapes -> 28 coarse routes, but concentrated:
LDIR from S=0 into the window 204 (57%), COPYALL from S=0 47 (13%), context-dependent copiers that write nothing when
run alone 57 (16%), LDI loops 9, LD (T),A byte loops 3, and 20 single-instance offset variants. The 246 distinct
setup multisets (227 singletons) are neutral junk around the same route. Answer to the directive's question: about
1,100 independent ORIGINS (one per run, CI 700-1,450) along essentially THREE mechanistic routes (LDIR, COPYALL, LDI)
plus a context-dependent class -- the chemistry funnels every origin into the shortest copier.

2.3 Task dependence (receipts/RATES.json FIXED lane, family-bootstrap 95% CIs). Sustained exact solve (best_score_tail
>= 0.999, a common ruler): ECHO 8.9% [7.8,10.1], INC 4.0% [3.2,4.9], SUM2 3.5% [2.8,4.3], CONST 2.2% [1.7,2.8],
COND_ONE 2.0% [1.5,2.5], COND_MULTI 1.6% [1.1,2.1] -- ordered by task difficulty. Spontaneous trigger 1.4-2.2% and hifi
replication predicate 14.6-16.6% across all six tasks: replication shows no task dependence (as expected in a world
where the task barely enters reproduction). Flag concentrations by task are artefacts: the BD flag sits on COND_MULTI
204 / COND_ONE 153 because those are the tasks where partial solvers (and the broken seeded hybrid, H1) have noisy
scores (C6).

2.4 Topology (RATES.json FIXED lane). Spontaneous trigger: NICHES_POLLINATION 6.0% [4.6,7.5] vs every other topology
0.6-2.3%; extinction POLLINATION 4.1% vs 38-55%. Cause (P1, confirmed): under POLLINATION (and RESERVOIR, niche 0 only)
migration SPAWNS A COPY of the organism under ENDOGENOUS physics -- world-made reproduction the external_births guard
never counts; sampled POLLINATION endogenous runs: median 888 such copies per run (8% of births; > 50% in 22/60).
POLLINATION's "topology effect" is this hidden reproduction channel; it is not a spatial phenomenon. Other topologies
differ by at most ~1.7 points in spontaneous rate with overlapping CIs. GATED_INTERACTION's 5.6% extinction (vs
44-71%) is M7 (organisms that skip interaction never age). The G7P1 cell of the grounding round tests P1 causally.

2.5 Other factors (FIXED lane; exploratory associations). Mutation supply: spontaneous LOW 1.2% / MED 1.9% / HIGH 2.5%
(dose-response), exact solve 5.3% / 3.7% / 1.7% (inverse). OPERAND mutation: highest exact solve 6.9% [6.0,7.7],
lowest spontaneous 0.8%. Representation: spontaneous VM_COPY 2.7%, Z80_64 2.2%, BYTECODE32 0.7%. Reproduction:
EXTERNAL exact solve 8.5% [7.7,9.3] vs endogenous 0.5-3.1% -- consistent with the falsification of the ENDO flag (s3.3).

2.6 Mutation geometry and basin width (receipts/BASIN.json; receipts/NEIGHBOURHOOD.json). A uniformly random tape is
already a self-replicator in isolation with probability 6/200,000 = 3.0e-5 (Z80_64), 2.0e-5 (BYTECODE32), 6.5e-5
(VM_COPY); every one copies with LDIR (VM_COPY also COPYALL). P(>= 1 in a 128-tape initial population) ~ 0.4% /
0.3% / 0.8%. The chemistry makes a minimal copier very short: registers start at 0 and LDIR with C = 0 sweeps up to
256 bytes, so `LD T,L ; LDIR` (3 bytes) reached through a slide of undefined bytes (80% of byte values are NOPs;
the PC leaves its own tape in 69% of random tapes) copies the tape. The basin is narrow per tape but wide per
population-run: a random population evolving 500 ticks enters it in ~7% of runs (s2.2).
Neighbourhoods (NEIGHBOURHOOD.json; 60 tapes per category; all L x 16 single substitutions; one paired INC panel):
random tapes: 0/60 have ANY single mutant that self-copies; non-replicators: 1/60. First-generation replicators:
8.0% of point mutants lose self-copying (92% robust); evolved replicators 7.4% -- evolution did not measurably change
replication robustness. Paired INC beneficial density: 0.0001 for random, non-replicator, first-gen and evolved
tapes alike, neutral fraction 1.00: replicator lineages carry NO task-relevant computation and no single mutation
gives them any. Flagged "beneficial-density" organisms: 0.0058 (seeded hybrids carrying task code). Reading:
replication is a narrow per-tape, wide per-population basin entered by building the shortest copier (65% of first
self-replicators were constructed by other organisms' imperfect copies, s3.1); once entered it is robust; and in
this substrate as run, what happens after entry is copying, not computing.

## 3. Adjudication of flag classes and triggers (Phase 3)

3.1 Spontaneous self-replication -- REPRODUCED_ASSOCIATION at the forensic stage (confirmation: G1/G2/G6/HIST).
Instrument: traced replay (tools/traced_replay.py v2) re-runs each run with the frozen harness plus byte provenance
(source address, executing PC and opcode of the last write to every window byte) and classifies every birth; the
tracer is checked on every replay against the stored summary (diverged: 0/544 and 0/300). Frozen classes:
COPY_EVENT (any registered birth) / SELF_REPLICATION (own bytes, moved by own code, fidelity >= 0.9 before and after
execution, writer material) / SUSTAINED_LINEAGE (an SR chain of depth >= 3) / EVOLUTIONARILY_ACTIVE (an SR-born
variant that itself self-replicated). Results (non-intervention runs):
  - v1 spontaneous_replication trigger: 502 runs. 346 contain SELF_REPLICATION (68.9%); 156 (31%) contain none:
    false positives -- ENDOGENOUS_PARTIAL 83/182, PAIR 24/55, COPY 37/219, OVERWRITE 12/46 (captures, chimeras and
    sweeps supply the 'hifi replication').
  - of the 346: SUSTAINED 310 (89.6%, Wilson 85.9-92.4%), SR-born organism alive at tick 500: 237, EVOLUTIONARILY
    ACTIVE 188; median maximum chain depth 146 generations; first SR at tick 0 in only 29 (median tick 117).
  - untriggered runs (traced sample): 15/296 contain SR (7 sustained, 6 alive at end, 4 evolutionarily active),
    including CONSTRUCTIVE (4/51), the physics the trigger credited with zero.
  - COPY_EVENT is not replication: 9,271 of 14,003 recorded 'first replications' in RANDOM-init endogenous runs have
    fidelity ~0 (in-place sweeps, junk constructions, M2/D2). The M1 self-smear hole changes little: of 9,670,487
    births passing the post-execution test in the 502 trigger runs, 7,505 (0.08%) fail the pre-execution test;
    9,662,982 SELF_REPLICATION births remain (of 25,069,717 registered births).
  - dependence on target memory: 99.9% of SR births (9,648,506) OVERWRITE an occupied neighbour; 14,476 construct
    into an empty cell (0.5% of all births go into empty cells). Self-replication here is overwriting reproduction;
    the SR criterion requires the writer's own bytes in >= 90% of the window, so preserved target bytes cannot
    supply an SR birth (target_fill ablation: P8). Environmental assistance: 2,319,892 births (9%) were written by
    partner code the writer ran into; they are excluded from SR by the own-code criterion. P1 world copies are not
    births at all.
  - how the first self-replicator arose (receipts/G6_HISTORICAL.json, 361 origins): BUILT_BY_COPY 233 (65%) -- the
    first true self-replicator was itself constructed by another organism's imperfect non-SR copy (169 writer-
    material partial copies, 64 chimeras); INIT_LATER 98 (27%) -- an initial organism that became SR later
    (mutation or context); INIT_AT_TICK0 30 (8%) -- present in the initial population. Historical ancestor tapes
    were not recorded, so whether the constructing ancestors had SELECTABLE partial function (a ramp) is G6b.
  - survival in fresh seeds and fresh memory: tested by the HIST lane (345 deduplicated origin tapes transplanted
    into fresh random populations, intact vs copy-ops NOPed).
Separation achieved: COPY_EVENT (millions) >> SELF_REPLICATION (in ~7% of fresh runs) > SUSTAINED (most of those)
> EVOLUTIONARILY_ACTIVE (about half of those).

3.2 REPRODUCTIVE_MACHINERY_RAISED_BENEFICIAL_DENSITY (493) -- INSTRUMENT_FAILURE.
receipts/GEOM_AUDIT_flagged.json + GEOM_AUDIT_control.json (tools/geom_audit.py). All 493 flagged runs rebuilt
exactly (stored scans reproduced bit-for-bit). Identity null (the frozen scan with mutant == base): scored "better"
in 60.0% of trials for the flagged top specimens (99.6% of them non-zero) vs 1.3% for 493 unflagged controls.
Paired, common-panel re-measurement (8 inputs x L x 16 fixed deltas): paired gain mean 0.0006, median 0.0000; > 0.1
in 1/493 (0.1055, r053563: a partial solver vs a perfect first replicator at ceiling); paired beneficial density ~1.5%
for top and first replicator alike. The flagged gain REPRODUCES under 12 fresh seeds (58%) because the flagged
specimens are input-dependent partial solvers (303/493 flags sit in SEEDED_HYBRID x COND_* families whose seed is the
half-correct un-relocated hybrid, H1): repeating a biased instrument reproduces its bias -- the late-stage "fresh seed
verification" would have confirmed an instrument failure. No evidence that reproductive machinery raised beneficial
density. The word "evolvability" is not warranted. Causal test: G4.

3.3 REACHED_UNDER_ENDOGENOUS_NOT_EXTERNAL (393) -- FALSIFIED (the opposite association holds; exploratory).
receipts/FLAG_AUDIT.json. Recomputed exactly (393). Over the same 9,589 matched pairs the REVERSE (external solved,
endogenous not) occurs 1,596 times. Exposure-matched (first run of each side; one unit per side): endogenous-only 443
vs external-only 1,554, sign test p = 6e-15. 261/393 flags had more treatment runs than control runs (promotion
exposure); 227 rest on a single run (blind audit). Further confounds: 90 flags rest on arms that went extinct (C1 tail
read), external offspring got 4x mutation (M3), 361/393 are seeded inits. By init: RANDOM 20 vs 732 (external wins),
SEEDED_HYBRID 309 vs 296 (no difference), SEEDED_REPLICATOR 33 vs 254, SEEDED_WITNESS 81 vs 272. Causal test: G3.

3.4 REPRODUCTIVE_ARCHITECTURE_RESPONDED_TO_TASK (600) -- CONFOUNDED (flag) / association PROVISIONAL.
579/600 SEEDED_HYBRID (seeded with both a replicator and task code, so "coupling" fires by construction), 579 end
>= 90% seed lineage; 531/600 had a random (non-seed) first COPY EVENT whose span (pc_max+1, including PC excursions
through the IO region: 214 spans >= 224) is the "compression" baseline; 98.5% of baselines are tick-0 events and 38%
have fidelity < 0.5. There was never a task-OFF comparison. Using the campaign's own matched task-OFF (NEUTRAL)
controls, first run per side: compression ON-only 576 vs OFF-only 344 (p = 2e-14). So SOMETHING about executed
extent shifts under task pressure, but it is measured on max-PC of a junk event, not on reproductive organisation.
Re-grounded in G5 with a frozen structural descriptor.

3.5 REACHED_INCREMENTAL_NOT_ATOMIC (136) -- DETECTOR_ONLY (ruler artefact).
INCREMENTAL "solver" = partial credit (answers ~19 off pass); 2,676 of 8,001 INCREMENTAL solver runs had a sustained
exact answer. On one ruler (best_score_tail >= 0.999 both arms): forward 59 = reverse 59; exposure-matched first
runs 65 vs 59 (p = 0.65; 124 discordant pairs; share 0.52, 95% CI ~[0.43, 0.61]). No detectable difference; the
design could not exclude an effect of roughly +/- 9 points of discordant share. receipts/FLAG_AUDIT_INCREMENTAL_EXACT.json.

3.6 RESERVOIR_CROSSED_MOAT (7) -- FALSIFIED. Blind-audit replays (audit_blind/a9_reservoir.py) attribute the tail
solvers of 6/7 flagged runs to ECHO solvers in the reservoir's easy niche 0 (e.g. r038218: 22.35 of 22.35); the 7th
is an ECHO program seeded as the "COND_MULTI witness" (the seed used niche 0's task, C4) scoring by luck (C2).
Provenance: reservoir migration is a COPY (P1), so the "crossing" material is world-copied. No airtight provenance
exists for any crossing.

3.7 Run-level triggers (not flags) -- status for the record. moat_crossing (48% of runs): DETECTOR_ONLY (C5).
cross_niche_transport (91% of NICHES runs), novel_architecture (92% of replicating endo runs), escape (96% without
sustained solvers), coexistence, environment_lineage: near-universal promotion signals, not phenomena (M8).
task_score: C1/C2 -- superseded by verified solving. persistence_above_control: 3 runs. replication /
spontaneous_replication: see 3.1.

## 4. Failure-mode audit (Phase 4)

Full ledger: ISSUE_AND_REPAIR_LEDGER.md (34 rows). Two independent passes (this seat; a blind auditor with 20
executable repro scripts, audit_blind/). Checked and sound: replay identity from config.json alone (39/39 runs
across all six kinds, every file byte-identical: receipts/REPLAY_sample36.json); evidence completeness; no
parent/offspring aliasing; deterministic RNG ownership within a World; 8-bit masking; atomic state writes; no
checkpoint restoration occurred; no worker interruption. Critical classes found: detectors reading pre-extinction
tails (C1), a solver definition that is not solving (C2/C3), an easy niche and a mis-seeded witness in the reservoir
arm (C4), trivially firing moat detector (C5), unpaired noisy geometry (C6), seeded-takeover + max-PC "architecture"
(C7), 1-byte captures counted as hifi replication (C8), seeded interventions counted as spontaneous (C9), world-made
copies under endogenous physics (P1), un-relocated seeded hybrid (H1). Detector thresholds were fixed before the run
(thresholds hash frozen) -- the failure is not post-hoc tuning but predicates that measure something else.

## 5. Repairs (Phase 5)

See ISSUE_AND_REPAIR_LEDGER.md. 16 regression tests failed on the unmodified harness (receipts/TESTS_BEFORE_REPAIR.txt) and
pass after repair; the H1 test (found later) asserts the v1 defect and the v2 repair in one test; 38/38
z80atlas tests pass; golden v1 fixture (18 cases) and 39/39 real historical runs replay through the REPAIRED harness
with every historical key equal (receipts/REPLAY_REPAIRED_sample36.json). Historical evidence therefore remains
RAW_VALID: the numbers are what the v1 instrument measured. What changed is which readings of them are valid
(per-row impact column of the ledger). Nothing in the campaign workdir was modified.

## 6. Outcome

The bounded grounding round (GROUNDING_REPORT.md) ran all 12,130 preregistered runs. Final per-phenomenon verdicts
and the readiness answers are in GROUNDING_REPORT.md s8-s9; next-campaign architecture in
NEXT_CAMPAIGN_RECOMMENDATION.md. In one line: the instrument is ready; the physics is not yet a place where
computation can affect reproduction, and that coupling -- not more replicators -- is the next campaign's precondition.
