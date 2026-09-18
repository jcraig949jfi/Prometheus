+==========================================================================+
|  SFE AUTONOMOUS TEN-EXPERIMENT CAMPAIGN -- FINAL CAMPAIGN REPORT (CMP1)  |
|  Author: Archaeon (seat m2-411504ab, machine M2 / SPECTREX5)             |
|  Date: 2026-09-17                                                        |
|  For: operator (HITL) + external reviewers                               |
|  Status: CLOSED -- all ten experiments received an honest attempt        |
|  Self-contained: every load-bearing number is inline; no repo access     |
|  needed. Paths and SHAs are given for verification only.                 |
+==========================================================================+

Directive: "Do not improve the story. Improve the machine." This report
separates SCIENTIFIC outcomes (what the experiments showed about the
substrate) from INSTRUMENT outcomes (what the campaign showed about the
bench). Section 1 is the disposition table; sections 2-3 are science;
sections 4-13 are the machine.

Engine: SFE v2 on M2 (https://192.168.1.191:8811, instance
eng_906356f7fb1da180131f9290, schema 8, science_profile warn,
session_enforcement advisory). Client: cmp1-archaeon. Search substrate:
the WSE selection loop over Proteus player-VM organisms (25 opcodes,
4 words/instruction), campaign seed 20260917, foundry FOUNDRY_C1. No LLM
in any loop. No operator input between the directive and this report.

Wall clock: campaign open 00:05, SFE-10 closed 06:25 (6 h 20 min for
ten experiments, fourteen engine attempts, ten dry runs). Harness wall
on the final attempts summed to 591 s; the four superseded attempts
cost 197 s more.

-----------------------------------------------------------------------
0. VERDICT UP FRONT
-----------------------------------------------------------------------

Ten of ten attempted. Seven COMPLETE (of which two NEGATIVE), three
INCONCLUSIVE (assay incapable). Zero BLOCKED, TABLED, SKIPPED-TIMEBOX
or INSTRUMENT-FAILURE dispositions: every instrument defect was
recovered inside the experiment's timebox by a second attempt.

Science, in one paragraph: on this substrate, prior search material
helps when it is MATURE and WHOLE and hurts or does nothing when it is
not. Whole genotypes from a solved or specialised source seed footholds
on a neighbouring cell (SFE-01 components 2/3 vs random 0/3; SFE-07
failed-residue 2/3 vs 0/3; SFE-04 frozen substrate reuse; SFE-10 one
solved producer bought a foothold at charged generation 30 vs 50).
Fragments and failures do not: organs recombined across lineages sit at
the floor with their shuffled controls (SFE-08), opcode-signature tabu
from failures is null (SFE-01), and immature producer artifacts are a
net loss against the same population without them (SFE-10). Encoding
matters for search on a fixed evaluator (SFE-06), but not in the way
"more accessible variation" predicts: the encoding with the most
accessible variation was the slowest. Curricula work weakly (SFE-05,
+0.155 adaptive, +0.113 transfer) and carry a forgetting shelf. Three
questions could not be posed because the chosen cell or stream was
unreachable at the budget (SFE-02, SFE-03, SFE-09): the campaign's
largest scientific loss and its most repeated instrument defect.

Machine, in one paragraph: the engine path ran with 0 errors on every
final attempt (32 worlds created, 32 TERMINATED; 0 orphans; startup
<= 2.4 s, teardown <= 1.3 s). The bench's real defects are upstream of
the engine: no reachability table (three assay-incapable experiments),
no common-random-numbers guarantee in the loop (two attempts lost to
it), no resume (every rerun re-created everything), and no typed
failure states (every INCONCLUSIVE was assigned by hand after reading
rows). Fourteen local decisions were taken; nine of them are the kind a
machine should take.

-----------------------------------------------------------------------
1. DISPOSITION TABLE (ten rows)
-----------------------------------------------------------------------

 ID      Disposition    Att  Engine   Scientific outcome (one line)
 ------  -------------  ---  -------  ---------------------------------
 SFE-01  COMPLETE        2   0 err    components WEAK POSITIVE (2/3 vs
                                      random-segment 0/3); failure tabu
                                      NULL; interaction not estimable
 SFE-02  INCONCLUSIVE    2   0 err    assay incapable: stream ceiling
                                      below the query threshold (both
                                      attempts, 4096-organism stream)
 SFE-03  INCONCLUSIVE    1   0 err    assay incapable: target W1_d4
                                      unreached by any arm (0/9)
 SFE-04  COMPLETE        1   0 err    CA useful computation weak
                                      positive (0.608); no localised
                                      component (lesion map flat within
                                      the matched-random band); frozen
                                      whole-substrate reuse positive
 SFE-05  COMPLETE        1   0 err    adaptive +0.155, transfer +0.113,
                                      interaction +0.042 (n=3); fixed
                                      hard + transfer loses Kd-0
                                      competence (forgetting shelf)
 SFE-06  COMPLETE        1   0 err    encoding effect WEAK POSITIVE:
                                      direct hits 0.9 in 13/53/53
                                      evals, balanced 653/97/89,
                                      scrambled 971/-/190; accessible
                                      variation decoupled from
                                      navigability
 SFE-07  COMPLETE        2   0 err    exaptation of failed residue
                                      WEAK-MODERATE POSITIVE (2/3 vs
                                      0/3); direct reuse of specialised
                                      artifacts 0.52-0.58 at plateau
 SFE-08  COMPLETE        1   0 err    NEGATIVE, assay capable: chimera
       (NEGATIVE)                     = shuffled = random at floor;
                                      whole ancestors seed 1/3 each
 SFE-09  INCONCLUSIVE    1   0 err    positive control unreached by any
                                      representation (0/3 x 3); B/C 0/6
                                      on the "stuck" cell; baseline 1/3
                                      there (pooled 1/12: rare, not
                                      stuck)
 SFE-10  COMPLETE        2   0 err    NEGATIVE at matched envelope:
       (NEGATIVE)                     mono 3/3 vs pc_0.4 1/3, pc_0.2
                                      0/3; one mature artifact paid
                                      (charged gen 30 vs 50); immature
                                      artifacts a loss

"Att" = engine attempts. "Engine" = errors on the attempt of record.
Superseded attempts: SFE-01 att 1 (3 engine errors: 422 on the failure
route, plus two harness defects), SFE-02 att 1 (0 errors; stream too
short), SFE-07 att 1 (4 errors: 403 SESSION_MISMATCH), SFE-10 att 1
(0 errors; common random numbers broken by the harness). All four are
preserved beside the record (RECEIPT_attempt1.json / rows_attempt1.json).

-----------------------------------------------------------------------
2. SCIENTIFIC OUTCOME PER EXPERIMENT (with the numbers)
-----------------------------------------------------------------------

Common frame: target cells are WSE event-stream worlds (W0 immediate
ask; W1_dk ask delayed k events; W2_K2 two keys); competence is
held-out episode reward in [0,1]; "foothold" = training best >= 0.5;
chance on a 4-bit answer is 1/16. N = 200, G = 60, E = 16 unless noted;
three seeds; common random numbers across arms from SFE-01 attempt 2
on (D-007).

SFE-01 Residue exchange (components vs failures). Source world W0
searched to residue; target W2_K2 seeded from spliced component
segments (top-4 elite genome segments) and/or opcode-signature tabu
from failures. Footholds: neither 1/3; components 2/3; failures 1/3;
both 1/3; random-segment control 0/3. Tabu hits were nonzero (attempt
2) but did not change outcomes. Interaction not estimable at n=3.
Claim ceiling: weak positive for whole-ish segments from a source that
itself reached only 0.0625-0.125 (L-010: the residue was immature; the
effect survived it, which is the interesting part).

SFE-02 Retention replay. H3 replay over a frozen archive with sealed
queries: the retention comparison needs at least one organism above
the query threshold in the candidate stream; the stream's ceiling was
below it at 1024 and again at 4096 organisms. Diversity landscape
measured anyway: behavioural classes 32 cells vs top-k distinct 10-17.
Nothing about retention was tested.

SFE-03 Failure-episode transport. Source worlds (relevant vs random)
publish failure episodes; the target search on W1_d4 replaces part of
its training battery with them. All nine target runs (3 arms x 3
seeds) stayed at 0.03-0.19 training best; W1_d4 is now known to be
reached in 1/12 pooled runs at G <= 100. The transport ran (2.0 s of
engine exchange; hash compare wrong-keyed, L-009 recurrence, science
unaffected).

SFE-04 CA substrate (Herakles ca_stream). Useful computation:
particle-2 readout 0.608 on delayed recall d=3 vs 0.5 chance under the
ridge readout; lesion map over 64 sites flat within the matched-random
band (no localised component: distributed); frozen whole-substrate
reuse on the neighbouring delay 3 task positive (whole > random
lesion). Temporal XOR was dropped in the dry run: not linearly readable
(D-010).

SFE-05 Curriculum 2x2 (adaptive vs fixed) x (transfer vs none), knob =
distractor count Kd in {0,1,2,4,8}. Battery-mean competence: adaptive
main +0.155, transfer main +0.113, interaction +0.042 (n=3). The
hidden effect (L-022): fixed/on loses Kd=0 competence entirely (a
forgetting shelf), which the battery mean hid.

SFE-06 Encoding (H5 decoders on block_output_score, hill climb from
fixed starts, three seeds). Evaluations to reach 0.9: direct 13/53/53;
balanced 653/97/89; scrambled 971/never/190. Balanced has 50% more
accessible variation (distinct neighbour phenotypes) than direct and
is slower: accessible variation is decoupled from navigability.

SFE-07 Exaptation. 135 genotypes that failed World A (frozen artifact
from SFE-01, read session-less, D-013) seed World B: footholds 2/3 vs
random-seeded 0/3. Direct reuse of specialised/best artifacts by
transfer: 0.52-0.58 on the plateau. Positive; n=3.

SFE-08 Chimera organs with provenance (compose modes cross / within /
random). Chimera = shuffled = random at the floor (0.03-0.19, no
footholds); whole-genotype ancestors L2/L3 each seed 1/3. Negative with
a capable assay: organs do not carry what their whole genotype carries.

SFE-09 Representation unlock (A_words / B_fields / C_fields_class;
identical generation 0; descend_fn hook). Positive control (A on
W1_d1) 0/3, so no arm was shown to work; B/C 0/6 on W1_d4; A 1/3 on
W1_d4 (seed 1, generation 52). Training shelves 0.25 / 0.3125 (= 4/16,
5/16) identical under every representation: the landscape's steps are
the evaluator's granularity.

SFE-10 Producer-consumer under a matched envelope with explicit costs
(comm ceil(bytes/4096) generations; storage 0.5 generation per
artifact). Attempt 2 (common fill): mono 0.542/0.562/0.521 (3/3,
footholds at generations 54/50/48); pc_0.2 0.031/0.073/0.396 (0/3);
pc_0.2_noex 0.312/0.281/0.260; pc_0.4 0.312/0.531/0.062 (1/3, consumer
generation 3 in seed 2); pc_0.4_noex 0.083/0.344/0.083. Exchange effect
(pc minus noex): -0.281/-0.208/+0.136 at p=0.2; +0.229/+0.187/-0.021 at
p=0.4. The one paying exchange came from the only producer that solved
its own cell (W0 at 1.0 in 12 generations). Attempt 1 differed only in
the random fill and moved two of fifteen rows across the foothold
line: seed noise at n=3 is the size of the effects.

-----------------------------------------------------------------------
3. SCIENTIFIC vs INSTRUMENT FAILURES (kept apart)
-----------------------------------------------------------------------

Scientific failures (the world answered "not at this budget" or "no"):
- assay incapable x3: SFE-02 (stream ceiling), SFE-03 (target
  unreachable), SFE-09 (positive control unreached). All three are the
  SAME failure: a cell or stream chosen from prior 0/3 rows without a
  pooled reachability estimate. Recorded as L-014, L-017 (rec 1), L-028.
- negatives x2 with capable assays: SFE-08 (organs), SFE-10 (division
  of labour at this envelope). These are results, not failures.
- weak positives at n=3 x5: SFE-01, SFE-04, SFE-05, SFE-06, SFE-07.
  None is established; each needs n >= 10 and an independent
  falsification battery before it propagates.

Instrument failures (the bench, not the world):
- SFE-01 att 1: cell label seeded the loop RNG (L-008); exact-genome
  tabu inert (L-007); blob-hash prefix mismatch (L-009); 422 on the
  failure route's extra field (L-006).
- SFE-03: hash compared against the artifact id (L-009 rec 1).
- SFE-07 att 1: 403 SESSION_MISMATCH on a cross-session read (L-026).
- SFE-10 att 1: harness fill broke common random numbers (L-030;
  L-008 rec 2).
- every rerun re-created worlds and artifacts (L-012, rec 3).
No experiment's disposition is an instrument failure; each was
recovered inside its timebox. The instrument failures cost 197 s of
harness time and about 2 h of the 6 h 20 min campaign clock (reading,
diagnosing, patching, re-recording).

-----------------------------------------------------------------------
4. STARTUP / TEARDOWN / RESTART RELIABILITY
-----------------------------------------------------------------------

                     SFE-01 02    03    04   05    06   07    08    09    10
 startup_s (engine)   0.61  1.01  2.43  0.49 1.19  1.34 0.65  0.54  0.59  2.31
 teardown_s           1.23  0.23  0.49  0.22 0.23  0.21 0.20  0.22  0.22  0.56
 total_s (record)     169.5 35.2  127.6 5.5  86.3  4.9  13.4  23.8  73.2  51.5
 worlds (record)      7     1     3     1    1     1    1     1     1     3
 engine errors        0     0     0     0    0     0    0     0     0     0

Startup: 14/14 attempts registered, created a session and worlds, and
started them at first try (the client token was registered once, before
SFE-01, into a gitignored config; never re-entered). Teardown: 32/32
worlds TERMINATED; python.exe count returned to the 4-process baseline
after every run; no detached launches were needed (longest attempt
170 s). Restart: 4/4 reruns succeeded, but all four were full
re-creations (no resume, L-012); the engine tolerated the duplicates
and distinguishes attempts only by world name (L-013). The workspace
guard (fail-closed if git cannot answer, ARCH-52) admitted every run
from the linked worktree and refused none.

-----------------------------------------------------------------------
5. AUTONOMOUS DECISIONS (14, D-001..D-014)
-----------------------------------------------------------------------

 Type                  n  IDs
 contract / infra      4  D-001 charter suspension for campaign
                          machinery; D-002 live M2 engine, cmp1- prefix;
                          D-004 standalone fallback if the engine cannot
                          express a step (never needed); D-013
                          session-less cross-experiment reads
 scientific design     6  D-005 WSE loop as search substrate, engine as
                          exchange; D-006 failures prune / components
                          propose; D-008 opcode-signature tabu; D-010
                          D-18 v1 reset + delayed recall; D-011 SFE-05 as
                          first H4 alpha; D-012 knob = distractor count
 validity / method     2  D-007 common random numbers; D-014 rerun after
                          the fill bug, attempt 2 of record
 budget / sizing       2  D-003 4 h soft / 24 h hard; D-009 stream 4096

Nine of the fourteen (D-004, D-007, D-008, D-009, D-010, D-012, D-013,
D-014, and the cmp1- prefix half of D-002) are deterministic given a
rule and a measurement, and belong in machinery (section 9). Five
(D-001, D-005, D-006, D-011, and the "which engine is production" half
of D-002) are operator-level policy taken locally under the directive's
no-HITL rule; they are recorded with their alternatives and revisit
conditions and should be ratified or reversed by the operator.

-----------------------------------------------------------------------
6. RECURRING BUGS AND FRICTION (ledger L-001..L-032)
-----------------------------------------------------------------------

Ledger: 32 entries. Severity: 15 major, 14 minor, 3 note. Categories:
MISSING_TELEMETRY 6, MISSING_FAILURE_STATE 5, FRICTION 5, TO_MACHINERY
3, AUTOMATION 3, BUG 3, OBSERVABILITY 2, KEEP_POLICY 2, PORTABILITY 1,
MISSING_RECOVERY 1, LANDSCAPE 1. Blocks future runs: L-005 (Vivarium
tokens; not needed by this campaign).

Recurred:
 L-012 no resume (rec 3: SFE-02, SFE-07, SFE-10)      -- every rerun
 L-008 RNG keyed on an arm-distinguishing input        -- att 1 of
       (rec 2: SFE-05 mitigation helped, SFE-10 not)      SFE-01, SFE-10
 L-009 sha256: prefix on ids/hashes (rec 1: SFE-03)    -- hash_ok False
 L-017 unreachable cell chosen (rec 1: SFE-09)         -- with L-014,
                                                          L-028 the same
                                                          defect x3
 L-013 attempts indistinguishable on the ledger (rec 1)
The four recurrences are all one-line fixes that were NOT made because
the campaign rule was "fix in the harness, record for the bench":
the bench did not change under the campaign, so the same holes were
walked into again. That rule was correct for comparability and wrong
for the recurrence count; Campaign 2 should fix L-008/L-009/L-012/
L-013 in the shared code BEFORE SFE-01.

-----------------------------------------------------------------------
7. INFRASTRUCTURE COUPLING (what a run depends on)
-----------------------------------------------------------------------

 Dependency                         Coupling         Failure seen
 SFE engine v2 (M2, :8811, cert)    every record     403 on cross-
                                                     session read
 sfclient EngineClient              every call       no read wrappers
                                                     (L-001), forwards
                                                     forbidden fields
                                                     (L-006)
 Harmonia conformance gate           once, at open    none (CONFORMANT
                                                     on 20 routes)
 Proteus foundry + RUNTIME_HASH      every organism   none
 WSE loop (archaeon.wse.evolve)      every search     RNG label (L-008),
                                                     fill (L-030), no
                                                     step API (L-021)
 Herakles ca_stream / eca            SFE-04, SFE-06   reset probe
                                                     unwired (L-019)
 archaeon.producer.h3_replay         SFE-02           stream ceiling
                                                     undetected (L-014)
 workspace guard (git on PATH)       every run        refuses detached
                                                     launches without
                                                     git dir (L-004)
 client token in config.local.json   every run        none
 comms (EW_DB_HOST=192.168.1.202)    open/close only  WRONG_ENVIRONMENT
                                                     without the var
 M1 defaults left in modules         latent           L-002

-----------------------------------------------------------------------
8. MANUAL STEPS TO REMOVE
-----------------------------------------------------------------------

1. Reading rows.json / RECEIPT.json and writing RECORD sections B-F by
   hand (every experiment). The receipt already holds every number in
   section C; a record generator is deterministic.
2. Assigning the disposition by hand after reading rows (INCONCLUSIVE
   x3, NEGATIVE x2). Typed failure states (section 9) make it computed.
3. Choosing target/source cells from memory of prior 0/3 rows (SFE-02,
   SFE-03, SFE-09). A reachability table makes it a lookup.
4. Renaming attempt files (RECEIPT_attempt1) and reconciling the two
   names used (L-013); the harness should number attempts.
5. Patching the harness after an attempt and rerunning (4 times); with
   idempotent posts and persisted ids this is a resume, not a rerun.
6. Appending ledger rows / decisions / journal by script per
   experiment; the receipt should carry the ledger candidates
   (applied counts, typed states) so the ledger is emitted, not typed.
7. First-time token registration (once per machine; acceptable).

-----------------------------------------------------------------------
9. DETERMINISTIC DECISIONS TO PUSH INTO MACHINERY
-----------------------------------------------------------------------

- common random numbers by default: run_cell takes an rng_label
  distinct from provenance; init_pop fills come from the cell's own
  generation 0 through a helper; the trace records gen0 provenance
  (L-008, L-030, D-007).
- typed failure states computed before/at the run, each mapping to a
  disposition: INTERVENTION_NOT_APPLIED (L-007), RESIDUE_BELOW_FLOOR /
  IMMATURE_ARTIFACT (L-010, SFE-10), STREAM_BELOW_THRESHOLD (L-014),
  TARGET_UNREACHABLE (L-017), READOUT_CANNOT_EXPRESS (L-020),
  POSITIVE_CONTROL_FAILED (L-028).
- reachability table per (cell, value_bits, N, G) built from every
  run's first_solved_gen, with pooled counts and a band; harnesses
  consult it to size G or refuse (L-017, L-028).
- idempotent engine posts keyed on sha(experiment, step, cell, seed)
  and world ids persisted as they are created; a rerun replays
  (L-012); attempt tag on world creation (L-013).
- one digest form on both sides of the client (L-009); sfclient read
  wrappers for experiments/observations (L-001); a single tracked
  engine descriptor for base_url + cacert (L-002/L-003).
- a generation-step API in the loop so curricula, ramps and
  producer-consumer schedules are callers, not re-implementations
  (L-021).
- the record generator and the ledger emitter (section 8, items 1, 2,
  6).

-----------------------------------------------------------------------
10. WHERE DISCRETION REMAINS
-----------------------------------------------------------------------

- which cells and streams are worth a question (given reachability);
  which knob ladders (Kd, delay), cost models (bytes/generation,
  storage/artifact), producer shares, representation sets, and
  intervention classes to compare (KEEP_POLICY L-018, L-029, SFE-10).
- how the question as posed maps to a disposition when the assay is
  capable but the effect is within seed noise (n=3 weak positives).
- whether a rerun after a harness fix is "the same experiment"
  (D-014's revisit condition).
- operator-level policy taken locally: D-001, D-005, D-006, D-011 and
  the production-engine half of D-002.

-----------------------------------------------------------------------
11. HIGHEST-VALUE TELEMETRY (in order)
-----------------------------------------------------------------------

1. first_solved_gen per (cell, budget) from every run -> reachability
   table with pooled counts (would have prevented three INCONCLUSIVEs).
2. source elite reward and share-above-chance on every published
   artifact (residue / producer maturity; the single variable that
   separated SFE-10's one paying exchange from its five losses).
3. gen0 provenance and import lineage share per generation (whether
   substituted organisms carry or poison a population; L-030, L-031).
4. applied counts on every intervention / residue channel (L-007).
5. rung x generation competence matrix for curricula (the forgetting
   shelf was invisible in the battery mean; L-022).
6. per-artifact genome-length / opcode-composition summaries (length
   confounds in chimera and residue comparisons; L-027).

-----------------------------------------------------------------------
12. LANDSCAPE FEATURES OBSERVED
-----------------------------------------------------------------------

- W2_K2 at N=200, 4-bit: a plateau (best 0.03-0.19 for 45-50
  generations) with a narrow exit reached at generations 48-54 by all
  three mono seeds; any spend that does not shorten the plateau is
  lost (SFE-10).
- training-reward shelves quantised by the evaluator (4/16, 5/16)
  under every representation (SFE-09); E sets the landscape's step.
- W1_d4 is rare, not stuck: 1/12 pooled at G <= 100 (SFE-03, SFE-09,
  earlier surveys).
- W0 -> W2_K2 has a cheap gradient when a W0 solver exists (0.312 at
  generation 0, foothold in 3 generations); W1_d1 -> W2_K2 not shown.
- organs do not carry what whole genotypes carry (SFE-08); failed
  whole genotypes carry more than random ones (SFE-07).
- accessible variation and navigability point in different directions
  on the H5 decoders (SFE-06).
- CA competence is distributed (flat lesion map) and reusable whole
  (SFE-04).
- fixed hard challenges plus transfer produce a forgetting shelf on
  the easiest rung (SFE-05).

-----------------------------------------------------------------------
13. RERUN FIRST / KEEP TABLED / CHANGES BEFORE CAMPAIGN 2
-----------------------------------------------------------------------

Rerun first (in this order):
1. SFE-03 with a target chosen from the reachability table (a cell at
   1/3-2/3 baseline reach), same transport; the question was never
   posed.
2. SFE-09 with the positive control verified first (A on W1_d1 at
   G >= 100, 8-bit, where it is 2/3) and operator mass matched across
   representations (L-029).
3. SFE-01 and SFE-07 at n >= 10 with an independent falsification
   battery (the two positives that would propagate).
4. SFE-02 with a stream that contains organisms above the sealed
   threshold (verified before freezing).

Keep as is (do not rerun unchanged):
- SFE-08 (negative with a capable assay); rerun only with a different
  organ definition (function-bearing segments, not length-bearing).
- SFE-10 at this envelope; rerun only with producer shares sized so
  producers solve their own cells first, or with a wall-clock (not
  generation) envelope where producers run in parallel.
- SFE-04, SFE-05, SFE-06: results stand at their claim ceilings; the
  next step is telemetry (L-019, L-022, L-023), not repetition.

Changes before Campaign 2 (all machine, all from the ledger):
1. reachability table + TARGET_UNREACHABLE / POSITIVE_CONTROL_FAILED
   (L-017, L-028).
2. common random numbers as the loop's default; common-fill helper;
   gen0 provenance in the trace (L-008, L-030).
3. idempotent posts + persisted ids + attempt tags (L-012, L-013).
4. maturity telemetry on artifacts and RESIDUE_BELOW_FLOOR (L-010).
5. typed states for inert channels and inexpressible readouts (L-007,
   L-020, L-014).
6. digest normalisation and read wrappers in sfclient (L-009, L-001);
   engine descriptor (L-002/L-003).
7. evolve.step API (L-021); rung x generation matrix (L-022).
8. record generator + ledger emitter from the receipt (section 8).
9. engine: define whether reads need a session key in advisory mode
   (L-026); reject-or-ignore extra fields consistently (L-006).

-----------------------------------------------------------------------
14. ARTIFACTS
-----------------------------------------------------------------------

Worktree D:\Prometheus-worktrees\archaeon-wse-2026-09-16, branch
archaeon/wse-2026-09-16 (base cb91659ef). Campaign commits 3a34d207a ..
8f8b0a955 (SFE-10 close). Per experiment:
archaeon/campaign1/SFE-NN/{RECORD.md, RECEIPT.json, rows.json}
(+ RECEIPT_attempt1.json / rows_attempt1.json for SFE-01, 02, 07, 10);
harnesses archaeon/campaign1/sfe01.py .. sfe10.py; ledger
archaeon/campaign1/LEDGER.jsonl (schema LEDGER_SCHEMA.md); decisions
archaeon/campaign1/DECISIONS.md; timeline archaeon/campaign1/JOURNAL.md;
directive roles/Archaeon/prompts/2026-09-17_sfe_campaign1/. Engine
records live under client cmp1-archaeon on eng_906356f7fb1da180131f9290
(sessions cmp1-sfe01 .. cmp1-sfe10; all worlds TERMINATED).

+==========================================================================+
|  END. A reviewer may return "not worth continuing" on any experiment    |
|  or on Campaign 2 as a whole; that answer is first-class. The           |
|  recommended read is: fix the nine machine items, then rerun SFE-03     |
|  and SFE-09, because three of ten questions were never posed.           |
+==========================================================================+
