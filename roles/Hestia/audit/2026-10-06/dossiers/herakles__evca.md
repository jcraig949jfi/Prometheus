# Dossier: herakles/evca (+ ca_stream, eca) and herakles/HERAKLES_HISTORICAL_COLLIDER_V0

Hestia audit 1, group G8(c). Auditor: Hestia worker fork (Opus 5.5), 2026-10-06.
Rubric: roles/Hestia/audit/2026-10-06/AUDIT_PLAN.md s2-s4.

VERDICT: SALVAGE_COMPONENT -- the evca executor, its criteria-with-floors discipline and the 11 reproduced historical organisms are a calibrated ruler with a KNOWN ceiling; as a substrate for reasoning, radius-3 binary CA rule-table evolution is a field-documented dead end that Prometheus inherits, and Herakles itself has never run an evolutionary search.

---

## 0. Identity

- Paths audited: herakles/evca/ (16 files), herakles/ca_stream/ (14), herakles/eca/ (9),
  herakles/CRITERIA.md, herakles/HERAKLES_HISTORICAL_COLLIDER_V0/ (42 files),
  herakles/specimens/spec-{evca-density, juille-pollack-1998, andre-bennett-koza-1996,
  capcarrere-r1-density}/ (results only). herakles/ total 619 tracked files; 524 of
  them are the Toussaint specimen (spec-toussaint-exploration), audited only at the
  verdict level because it is not a CA substrate.
- Seat: Herakles (roles/Herakles/, 164 files). Last seat commit a8258db99 (2026-09-17).
- Census (docs/fleet/fleet_state.json): two rows. `herakles/evca` kind research-engine,
  DORMANT, last engine commit 6c9c55bfb 2026-09-16, consumers Theophrastus and
  Archaeon. `herakles/HERAKLES_HISTORICAL_COLLIDER_V0` kind auditor, DORMANT.
  Census purpose text says "CA stream used for the C1-e synchronisation work"; that
  is inaccurate. C1-e is the historical density reproduction
  (herakles/evca/c1e/REPORT.md:1); synchronisation is a separate 2026-09-10/16
  criterion (herakles/evca/core.py:634-698, 721-814).
- SHA read: worktree C:/Prometheus-worktrees/hestia-boot-2026-10-06 at 3fed30ac9.
- READ IN FULL: herakles/evca/core.py, genomes.py, MAJ_STRUCTURAL_ZERO.md,
  c1e/REPORT.md, c1e/PROTOCOL.md (s1-s4), herakles/CRITERIA.md,
  ca_stream/OBSTRUCTION.md, ca_stream/CA_STREAM_V2_PLAN.md, ca_stream/core.py
  header (1-60), D18_AMENDMENT_v1.md s1-s5, collider README.md,
  FIRST_EXPERIMENT_PROPOSAL.md, EVCA_HCA1_HCA2_DESIGN_NOTE.md s1-s4,
  spec-juille-pollack-1998/REPORT.md, spec-andre-bennett-koza-1996/REPORT.md,
  spec-capcarrere-r1-density/REPORT.md (head), roles/Herakles/journal/2026-09-16.md,
  todo_2026-09-16.md, Elenchus epistemic-debt LEDGER entries C-04/C-05
  (roles/Elenchus/investigations/2026-09-11_epistemic_debt/LEDGER.md:89-117),
  archaeon/campaign1/SFE-06/RECORD.md (head), Sisyphus intake
  docs/phase3/intake/sisyphus/seats/Herakles.md (head).
- READ PARTIALLY: herakles/evca/derive.py (signatures), c3_null_check.py (1-80),
  committed rows c1e_results.json (all 18 primary cells printed),
  spec-juille-pollack-1998/derived/reproduction_results.json (15 primary cells
  printed), archaeon/docs/h0h5/C3_2_NULL_CHECK_HERAKLES_2026-09-10.json (head),
  spec-evca-density/derived/verify_rule_tables.py (grep), L_COMPUTE_LEVERAGE_TABLE.md,
  HC_T01_CORRECTION_2026-09-03.md (s1-s2), HC_T01_RESULTS.jsonl (head).
- NOT READ: the 13+ recovered PDFs; A_FIELD_MAP.md and the B..Q registry JSONL
  bodies; HC_R01_RESEARCH_REVIEW_PACKET.txt; CROSS_SEAT_META_ANALYSIS; the
  Toussaint specimen CSVs, hct01.c and reanalysis scripts; eca/core.py body;
  test bodies (counted only: 35 + 29 tests in evca, 29 ca_stream, 33 eca);
  run_c1e.py, compare_c3_2.py; Vivarium's ca_density_v0 kind; Archaeon C3 campaign
  outputs; roles/Herakles/deep_research/*. Literature numbers not printed in a
  committed Herakles file are marked MODEL_RECALL below and must be checked.

## 1. Mechanism (what the code does)

### 1a. herakles/evca: a pure executor, not an evolver

- Representation: a radius-3, 2-state rule table, 128 bits (core.py:90-96), hex
  encoded (167-186). Neighbourhood index with leftmost cell as MSB, pinned and
  re-derived from maj/GKL definitions (25-33, 193-204, 512-536).
- Dynamics: synchronous update on a periodic ring, `step` is one table lookup per
  cell (207-210); `evolve` loops it (213-233). Odd N enforced (127-132).
- Measurements (all scorers, none optimisers):
  `classify` = at_T density accuracy with witness and mask (322-370);
  `cellwise_majority_match` (566-625); `synchronisation_score` (663-698);
  `blinker_rule_table` positive control (701-718);
  `cellwise_synchronisation_match` (777-814); `random_table` (628-633).
- Exact symmetries (reflection, complement) on rules and ICs (416-503), used by
  `c3_null_check.py` to decide IDENTICAL / NOT_IDENTICAL / INDETERMINATE on
  transformed twin runs using per-IC correctness masks (c3_null_check.py:1-45).
- `derive.py`: content-addressed variation operators -- derive_edit (134),
  derive_flip (158), derive_crossover with one-point / uniform masks (191-240),
  derive_transform (242), verify_record (264). It "mints nothing" and contains
  NO selection loop.
- genomes.py:41-98: six recovered organisms (maj, exp, par, particle1, particle2,
  GKL) embedded with published P at N = 149/599/999.

Grep for crossover|mutat|population|generation over herakles/*.py returns only
literature-registry strings in the collider build scripts; there is no GA, GP,
coevolution or hill-climber anywhere in herakles/. The EvCA Stage 1 GA
reconstruction is "PARKED, operator's" (roles/Herakles/todo_2026-09-16.md:51) and
ca_stream rule search is explicitly forbidden until a baseline exists
(ca_stream/CA_STREAM_V2_PLAN.md:72). The ONLY search ever run over a Herakles CA
evaluator is Archaeon's SFE-06: a (1+4) single-bit hill-climb over the 256
elementary (radius-1) rules (archaeon/campaign1/SFE-06/RECORD.md:23-59).

### 1b. herakles/ca_stream: reservoir-computing probe

Wraps evca.step as a streaming substrate: inject a bit at a port, one CA step,
linear ridge readout over 31 cells (ca_stream/core.py:1-54; N_CELLS 31, HORIZON 8,
256-stream catalogue). This is the only place the CA is asked to do something
other than the original classification task (delayed recall, temporal XOR).

### 1c. The collider

A literature-archaeology instrument (README.md "revised thesis"): recover
historical specimens, re-execute them, register detector parts (Q) and mechanism
parts (E). Its executable output in the CA lane is the four reproduction reports.

### Documented vs code

- CLAIMED (FIRST_EXPERIMENT_PROPOSAL.md) "Reimplement the GA ... Run 1e4 times";
  CODE: no GA exists.
- CLAIMED (L_COMPUTE_LEVERAGE_TABLE.md:11, labelled EST) "1-10 core-sec (bit-packed)"
  per EvCA run, 1e4-1e5 runs per CPU-day. CODE: the only executor is numpy uint8,
  measured at about 5e7 cell-updates/s (c1e/PROTOCOL.md s3). One PPSN-III-shaped
  GA run is 100 pop x 100 gens x 100 ICs x 149 cells x ~320 steps = 4.8e10
  cell-updates, i.e. about 950 s, about 90 runs per CPU-day -- three orders of
  magnitude below the EST. No bit-packed executor exists in the repo.
- CLAIMED (census) "C1-e synchronisation"; CODE: C1-e is density reproduction.

## 2. Evidence

| Claim | Tier | Source |
|---|---|---|
| 17/18 EvCA cells reproduced (N=149/599/999, 6 rules); particle2 N=149 DISCREPANT 0.733 vs 0.755 | OBSERVED | herakles/evca/c1e/c1e_results.json `primary`; REPORT.md:15-31 |
| maj = 0.000 exactly over 16000 ICs; structural (never reaches uniform in 177/200 samples) | OBSERVED | c1e_results.json; MAJ_STRUCTURAL_ZERO.md s1-s2 |
| Juille-Pollack 1998 Table 1: 15/15 reproduced; coev1 0.8548, coev2 0.8574 at N=149 | OBSERVED | spec-juille-pollack-1998/derived/reproduction_results.json; REPORT.md |
| ABK 1996: 4/4 reproduced; abk_gp 0.8243 vs 82.326%, das1995 0.8235 vs 82.178% | OBSERVED (report table; rows file not opened) | spec-andre-bennett-koza-1996/REPORT.md |
| Capcarrere-Sipper-Tomassini: rules 184, 226 = 1.000 on every IC under block-output criterion; 184 = 0.000 under at_T | OBSERVED (report) | spec-capcarrere-r1-density/REPORT.md P1, P6 |
| at_T floor is {0}: 40/40 random tables score exactly 0 | CLAIMED in CRITERIA.md:79 citing cs-c3-2 corpus; rows not opened | herakles/CRITERIA.md |
| cellwise_majority random band 0.4939-0.5099 (20 tables) | CLAIMED with table in MAJ_STRUCTURAL_ZERO.md s3 | |
| cellwise_sync random band [0.057, 0.307], mean 0.227; all six genomes ~0 | OBSERVED (file present; keys checked) | herakles/evca/sync_floor_2026-09-16.json |
| ca_stream v1 inert: 0 of 63488 feature entries non-zero for all six rules | OBSERVED by seat; independently re-verified by Elenchus (C-04 EARNED) | OBSTRUCTION.md:27; Elenchus LEDGER:89-104 |
| "A density classifier MUST annihilate a lone minority cell" | REFUTED by Elenchus C-05 (counterexample: maj with centre-only bit set) | OBSTRUCTION.md:49; LEDGER:105-117 |
| ca_stream_v2 (non-uniform reset) | DESIGNED, unissued; blocked on Vivarium kind | CA_STREAM_V2_PLAN.md; todo_2026-09-16.md |
| EvCA GA Stage 1 / Stage 3 replay; HCA-1/HCA-2 | DESIGNED, never run | FIRST_EXPERIMENT_PROPOSAL.md; EVCA_HCA1_HCA2_DESIGN_NOTE.md |
| Synchronisation-solving rule (L-7) | NOT STARTED | todo_2026-09-16.md:30 |
| HC-T01 (Toussaint, not CA): verdict downgraded to WEAK_SIGNAL_ONLY; K7 fired (current fitness predicts acquisition at least as well as every accessibility statistic) | OBSERVED + operator adjudication | HC_T01_CORRECTION_2026-09-03.md s1 |

Seat self-negatives already recorded and used here: the opening thesis declared
dead (collider README 2026-09-03b); the "particle-strategy rate" error caught
(7/300 vs 0/50, FIRST_EXPERIMENT_PROPOSAL.md:8); prediction lost on the sync floor
width (CRITERIA.md, core.py:760-771); the exp anomaly that did not replicate
(c1e/REPORT.md s2); refusal to fit 480 single-digit particle2 variants
(REPORT.md:122). This is an unusually honest ledger.

One internal inconsistency the seat did not flag: the specimen record gives
particle1 measured 0.733 at N=149 (below published 0.742; also
EVCA_HCA1_HCA2_DESIGN_NOTE.md:67), while C1-e measures 0.7542 (above published).
The recovery verifier used 1000-2000 ICs in some calls
(spec-evca-density/derived/verify_rule_tables.py:131,143), so this is probably
noise, but C1-e REPORT s3's argument against the transcription story
("the two deviations have OPPOSITE signs") rests on the single C1-e sample of
particle1. The particle2 lead stays a lead.

### Prometheus numbers against the field

    organism      source                     published P149   Prometheus measured
    GKL           hand, 1978                 0.816            0.8145 (C1-e), 0.819 (JP98 run)
    par           GA, Das/Mitchell 1994      0.769            0.7708
    das1995       hand, Das 1995             0.82178          0.8235
    abk_gp        GP+ADF, ABK 1996           0.82326          0.8243
    coev2         coevolution, JP 1998       0.860            0.8574

Every number Prometheus holds is a re-measurement of a 1978-1998 organism. Not one
CA rule in the repo was found by Prometheus.

What the field learned (cited where a committed Herakles file prints it, else
MODEL_RECALL, to be checked):
- GA on 2^128 tables found mostly block-expanding strategies; particle-based
  strategies in 7/300 PPSN III runs, 0/50 Physica D runs
  (FIRST_EXPERIMENT_PROPOSAL.md:8, PRIMARY_SOURCE_READ).
- Authors' own diagnosis: fitness noise floor ~0.02 SD on 100 ICs prevented the GA
  resolving GKL-quality rules; uniform-over-density ICs made the task easier as
  rules improved (FIRST_EXPERIMENT_PROPOSAL.md:52-53).
- GP+ADF (ABK 1996) 0.823, coevolution (Juille-Pollack 1998) 0.86: each new search
  paradigm bought ~0.01-0.04 (OBSERVED via reproductions above).
- Land and Belew 1995: no 2-state 1-D CA of any finite radius perfectly classifies
  density under the fixed-point output convention (MODEL_RECALL; the seat's
  CRITERIA.md cites Capcarrere 1996, which sidesteps it by changing the output
  convention -- reproduced, rule 184).
- Later bests around 0.88-0.89 at N=149 (e.g. Wolz and de Oliveira 2008)
  (MODEL_RECALL). Fuks 1997 two-rule sequence and Fates 2013 stochastic CA reach
  arbitrary precision by changing the model, not by search (MODEL_RECALL).
- Every rule degrades with N (OBSERVED here: coev2 0.857 -> 0.779, GKL 0.815 ->
  0.749 from N=149 to 999). The evolved "computation" does not scale even in its
  own task.
- Computational mechanics (Crutchfield-Hanson domains and particles; Hordijk,
  Crutchfield, Mitchell 1996 particle models) explained the strategies post hoc
  (MODEL_RECALL; the papers are in spec-evca-density/original/ but not read).

Does Prometheus inherit the ceiling? YES, completely. ca_density_v0 (Vivarium kind)
uses exactly this representation, task and at_T criterion (CRITERIA.md row 1).
Any organism Prometheus evolves there is bounded above by a ~0.86-0.89 empirical
frontier reached with orders of magnitude more search than Prometheus has spent,
and below 1.0 by theorem.

## 3. Matrix

### 3a. Combinatorial explosion and reachability

Side calculation (scratchpad herakles_calc.py):

    rule space r=3                       2^128 = 3.40e38
    quotient by reflect x complement     >= 8.5e37
    1-flip neighbourhood                 128;  2-flip 8128
    IC space at N=149                    2^149 = 7.1e44; 1e4 ICs sample 1.4e-41 of it
    historical GA budget (300 runs x 100 pop x 100 gens) = 3e6 evals = 2^21.5,
                                          fraction of rule space 8.8e-33
    Prometheus GA budget on r=3 tables   0 evaluations
    per-rule eval at C1-e precision      4.4e8 cell-updates, ~9 s (numpy)
    one HCA-2 detector reading           128 x 1e4 ICs = 5.7e10 cell-updates, ~19 min
    SFE-06 (only search run)             256-rule space, 1288 evals/arm = 5.0x the space

- Explosion: rule space is not the binding wall (the field never needed to
  enumerate it); the binding walls are (i) fitness noise -- at I=100 ICs the SE is
  0.038-0.043 at p=0.75-0.82, larger than the entire 0.033 gap between ABK and
  coevolution (6 SE at 1e4 ICs, i.e. only resolvable at 100x the per-eval cost);
  and (ii) the cost of an exact neighbourhood reading (19 CPU-min per point).
- Reachability desert, measured: at_T gives random tables exactly {0} (40/40,
  CRITERIA.md:79); synchronisation gives every held organism and every random
  table {0} (CRITERIA.md, sync rows). From a random start, a selection loop on
  at_T has no gradient at all. The historical GA only worked because it used the
  uniform-over-density IC ensemble, under which even maj scores 0.443
  (c1e/REPORT.md s3 table) -- i.e. the fitness signal at the bottom is supplied by
  an easier task, not by the target task.
- Hit rate: particle strategies 7/300 = 2.3%, Wilson [0.011, 0.047] (proposal).
  The "interesting" regime is rare, seed-dependent and non-transferable.
- ca_stream: the six organisms from an all-zero reset are a point attractor; the
  reachable set of lattice states under single-port injection is exactly {0}
  (OBSTRUCTION.md:27, verified by Elenchus).

### 3b. Cosplay vs foundation

- What does the work called "computation": a fixed 128-entry lookup table applied
  synchronously; the "answer" is read by a hand-chosen global halting criterion
  (uniform configuration at step T). The task is a single fixed bit-valued
  predicate (majority). There is no input stream, no memory beyond the lattice,
  no output channel other than "whole lattice uniform", no composition of
  sub-results across tasks.
- Herakles's own components are honest instruments: scorers, controls, symmetry
  checker, reproduction harness. They do not claim reasoning. The seat states
  that ca_stream "refuses to conclude" substrate computation (ca_stream/core.py:31-36).
- The historically real phenomenon -- embedded-particle computation, where domain
  boundaries act as signals and their collisions as logic -- IS a genuinely
  compositional primitive in principle (signals plus collisions are how rule 110
  universality is built; MODEL_RECALL). But: (i) Prometheus has no domain/particle
  detector in code (grep for domain filter / computational mechanics over
  herakles/*.py: nothing); the instrument scores task outcome only and would NOT
  detect a particle circuit if one evolved; (ii) the particles found by GA are
  task-locked: they compute one predicate, degrade with N, and nothing in the
  historical record or in this repo shows them reused for a second task.
- Ceiling stated concretely: on the native task, P149 <= ~0.89 empirically and < 1
  by theorem; on any new task, unknown and unmeasured; on sequence tasks (ca_stream)
  the measured value equals the null baseline to the last digit for all six
  organisms (OBSTRUCTION.md s3 table).

### 3c. Substrate bottlenecks

- Representation: a flat 128-bit lookup table has no modularity, no addressing, no
  reuse; every neighbourhood is an independent bit. Mutation is a bit flip;
  crossover splices unrelated neighbourhood entries. There is no representation
  for "a particle type" or "a collision rule" that variation could act on.
- State: 1 bit per cell, 149-999 cells, radius 3. Information propagates at most 3
  cells/step; any global decision costs Omega(N) steps, and the decision must be
  written into the whole lattice.
- Memory / I/O: the task has one input (the IC) and one output (uniform state).
  ca_stream showed the density organisms erase injected input in one step from a
  uniform reset; with a random reset (D-18) the four particle rules carry Hamming
  divergence that grows over 10 steps (D18_AMENDMENT_v1.md s4) -- the only
  measured hint of state-carrying, and it is unread by any readout yet.
- Credit assignment: none below whole-rule fitness. HC-T01's K7 is the warning:
  in the one accessibility experiment the seat ran, current fitness predicted the
  future as well as every structural statistic (HC_T01_CORRECTION s1).
- Compositionality: zero mechanisms for it. derive.py adds edit / flip / crossover
  / transform on whole tables; none composes behaviours.
- Throughput: numpy uint8 at ~5e7 cell-updates/s (PROTOCOL.md s3) vs a bit-sliced
  executor that would give ~64x per core; the proposal's compute budget silently
  assumes the latter.

## 4. Deliverable sections

### Discovery approach
Herakles does not try to generate intelligence. It recovers 1978-1998 evolved and
hand-designed CA classifiers from printed hex, re-executes them under pinned
conventions, reproduces their published accuracies to within Bonferroni-corrected
bands, and builds criteria with measured random floors so that any future
Prometheus organism on the same task can be placed against a known historical
ceiling. ca_stream asks whether the same organisms can serve as a reservoir for
sequence tasks. The collider generalises this to an archaeology of
"evolvability microscopes".

### The brick walls
1. Inherited ceiling: r=3 binary density classification has an empirical frontier
   of ~0.86 (coev2 0.8574, OBSERVED here) to ~0.89 (MODEL_RECALL) and a proof that
   1.0 is impossible (Land-Belew, MODEL_RECALL). Thirty years and three search
   paradigms moved it by ~0.04. Prometheus has 0 search evaluations on it.
2. Reachability desert at the bottom: random tables score exactly 0 under at_T
   (40/40) and under synchronisation; selection has no gradient without changing
   the task ensemble (uniform-density ICs lift maj from 0.000 to 0.443).
3. Noise and cost: fitness SE ~0.04 at the historical 100 ICs exceeds the 0.033
   gap separating the best paradigms; an exact one-step accessibility reading
   costs ~5.7e10 cell-updates (~19 CPU-min) per point on the current executor,
   and a single historical-shape GA run ~950 s, ~1000x the compute table's EST.
4. Task-lock: the organisms degrade with N (0.857 -> 0.779) and are inert or at
   null on every other task tried (sync 0.000 for 5/6; ca_stream = null baseline).
5. No circuit detector: nothing in the code identifies domains, particles or
   collisions, so the instrument cannot see the one compositional structure the
   field found.

### Seed viability
Not a reasoning seed. The density-classification CA is a closed, single-predicate
benchmark whose field already hit its ceiling; Prometheus inherits that ceiling
in ca_density_v0 and has added no search, no new organism and no new mechanism.
What should be carried forward is the INSTRUMENT: (a) herakles/evca as a pinned,
tested, pure executor (core.py) with an 11-organism calibration catalogue
reproduced against print (C1-e 17/18, JP98 15/15, ABK96 4/4, CST footnote);
(b) the criteria discipline -- every criterion ships with its attainable range,
random floor, eligible count and positive / cheat / negative controls
(CRITERIA.md "Rules for adding a sixth"), which is exactly what most Prometheus
engines lack; (c) c3_null_check.py, a per-IC-mask symmetry checker that would
catch orientation bugs in any lattice engine. As a ruler, it would detect a real
improvement on the density task (a P149 > 0.86 organism is a 6-SE event at 1e4
ICs) but would not detect a reasoning circuit as such.

### Evolutionary roadmap
Only worth pursuing if the question is changed from "score on density" to "do
evolved signal/collision structures compose across tasks". Concretely:
1. Build the missing microscope: a computational-mechanics domain filter
   (regular-language domain identification, then particle catalogue: velocity,
   period, collision table). Validate it on the held organisms: it must find
   particles in par/particle1/particle2 and the GKL particle set, and none in maj.
2. Replace the table representation for the search arm with a typed, modular one:
   a rule defined as a small set of domain patterns plus a particle-collision
   grammar (graph rewriting over space-time defects), so variation acts on
   particles and collisions, not on 128 independent bits. Keep the table executor
   as the semantic ground truth (compile grammar -> table, r=3 or larger).
3. Bit-sliced executor (64 cells/word or GPU) before any GA; the compute model
   requires ~1e9+ cell-updates/s.
4. Multi-task curriculum: density, synchronisation, ordering (sort 1s left), and a
   delayed-recall stream (ca_stream_v2 with D-18 reset). Score each with the
   CRITERIA floor discipline. Measure reuse with an MDL-style statistic: the
   description length of the particle catalogue for task B given task A's catalogue.
5. Credit assignment: replace whole-rule fitness with per-collision attribution
   (knock out a collision entry in the grammar, measure task delta), which is the
   compositional analogue of the bit-ablation the proposal already specifies.

THE ONE DECISIVE EXPERIMENT (next): Particle reuse transfer test.
Bit-sliced GA in the PPSN III configuration, 200 runs on density; select runs
whose elites the validated domain filter classifies as particle-based. Then
evolve synchronisation (task B) from three starting pools at matched compute:
(i) particle-based density elites, (ii) block-expanding density elites matched on
density fitness, (iii) random tables. Measure generations to sync P >= 0.9 and the
fraction of task-B particle types already present in the task-A catalogue.
KILL CRITERION: if pool (i) shows < 1.5x speedup over pool (ii) at 95% CI AND
particle-catalogue overlap is no higher than for pool (ii), then evolved CA
particle computation does not compose in this representation; record CA
rule-table evolution as DEAD_END for the reasoning question and keep evca only as
a ruler. Cost estimate: ~200 GA runs x 4.8e10 cell-updates on task A plus ~300 on
B; feasible in a day only with the bit-sliced executor.

## 5. What would change this verdict

- Upward to VIABLE_SEED: a committed run in which a Prometheus-evolved organism on
  any CA task shows a filter-identified particle/collision set that is measurably
  reused on a second task (the experiment above passing its kill criterion), or
  an organism above ~0.89 P149 under the published convention with 1e4 ICs.
- Downward to DEAD_END: the evca library proving untrustworthy as a ruler (e.g.
  the particle2 discrepancy traced to an executor defect rather than
  transcription; the oracle comparison at REPORT.md suspect 5 makes this
  unlikely), or Vivarium/Archaeon ceasing to consume ca_density_v0 so the ruler
  has no user.
- Literature check: if the MODEL_RECALL claims (Land-Belew impossibility, ~0.89
  frontier, absence of cross-task particle reuse in the EvCA line) are wrong --
  in particular if published work already demonstrated particle reuse across
  tasks -- the roadmap's decisive experiment should be replaced by reproducing
  that work, per the seat's own GATE-3 ("no invented measure before Q records
  whether the field already has a better one").
- Auditor conflict of interest: same model family as the seat; the HC-T01 and
  C1-e verdicts were not re-executed by this audit.
