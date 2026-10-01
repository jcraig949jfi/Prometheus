# Theseus -- seat dossier

- Seat: Theseus (two unrelated tenants of one name; see section 1)
- Crawler: Tantalus (worker)
- Tree SHA: 21a47402a (origin/main)
- Date: 2026-10-01

Summary. The name "Theseus" covers two systems that share only the directory
theseus/. (1) The SEAT Theseus, created and chartered on 2026-09-30 on host
DESKTOP-RUAPVAI ("THESEUS CONCEPT TENSOR / SYNTHETIC ANCESTRY"), built the
package theseus/synth/ (about 3,300 lines of numpy) in one day and ran two
preregistered campaigns, v0 (H1 FAIL) and the corrected replication v0_1 (H1
INDETERMINATE). Its "concept" is a 1-D reaction-diffusion-style program over a
4 x 32 real field for 128 steps; its "concept tensor" is a per-parent gain
computed by a fixed random readout of the parent's own behavioural
fingerprint, inserted as one multiplicative "react" rule; its "synthetic
ancestry" is exact parent-id bookkeeping over rule-splicing collisions. The
seat itself reports that its mechanistic and lens rulers do not separate
random programs from deep descendants. (2) The ENGINE theseus/ of May 2026
(Techne-operated "substrate generation engine") is a bandit-scheduled battery
of about 56 claim generators that emitted about 658M self-verdicted
arithmetic-relation records (for example "crossing_number(knot) equal_mod_2
rank(EC)") for sigma and the paused Ergon Learner; later Techne, Ergon,
Charon and Harmonia audits showed its apparent corpus signal was a bug and a
claim-shape category error, its promotion gate was shape-only, its handoff
inverted kill labels, and 99.98% of records were verdicted by the generator
that wrote them. Atlas merges the two under one name. Neither system was
shown to exhibit a nontrivial reasoning primitive; both contain reusable
instrument parts.

---------------------------------------------------------------------------

## 1. Identity, charter and pivots

Two tenants, kept separate throughout this dossier.

### 1A. Seat Theseus (2026-09-30 -)

- Creation: operator chat directive, verbatim
  roles/Theseus/prompts/2026-09-30_creation/01_OPERATOR_CREATION_verbatim.md
  ("You're @roles/Theseus a new role. Set yourself up..."). Creation commit
  2c3674def (2026-09-30 07:50 -0400). [IMPL]
- Charter: roles/Theseus/prompts/2026-09-30_charter/01_OPERATOR_CHARTER_verbatim.md
  ("PROJECT: THESEUS CONCEPT TENSOR / SYNTHETIC ANCESTRY"), adopted 46a8faf82.
  Core asks: compile G0 human concepts into primitive properties; collide them
  k-way in an executable substrate, never by an LLM; synthetic descendants
  become collision matter; lanes G0 / SHALLOW / DEEP / VERY_DEEP; behavioural
  fingerprint from >= 20 perturbations; mechanistic reproduction by known
  machinery; Tyche-style evolved lenses; dark objects; "giant ball" ecology;
  arity experiment; FIRST HARD TEST (do deep descendants reach niches not
  reached by LLM synthesis, triplets, sextuplets, matched random programs).
  [INTENT]
- Host: DESKTOP-RUAPVAI (Windows 11, 4 logical CPUs, 192.168.1.160), first
  seat on that host; worktree Prometheus-worktrees/theseus-base-role; instance
  desktop-ruapvai-01f15f15; model claude-opus-5-5. (roles/Theseus/RESPONSIBILITIES.md s5,
  journal 2026-09-30) [CLAIM]
- Pre-charter body: roles/Theseus/superseded/RESPONSIBILITIES_pre_charter_2026-09-30.md
  and BACKLOG_H0H5_pre_charter_2026-09-30.md (generic base-role scaffold, no
  science). [IMPL]
- Pivots: none within the seat's life except the v0 -> v0_1 amendment.
  Current state READY under CWO-2026-09-30B "finish in place, no
  self-promotion"; last seat commit 56f0fc547 (2026-09-30 10:45 -0400).
  (roles/Theseus/STATUS.md, WORK_STATE.json) [IMPL]
- Relationships: reads G0 ore from agents/nous/src/concepts.py (95 concepts;
  "historical Hephaestus/Nous") and Hecate Pass-0 extractions
  (hecate/programs/HT-*/program.json); imports tyche.lens read-only; sent a
  question to Tyche (roles/Theseus/prompts/2026-09-30_to_tyche/01_TO_TYCHE.md,
  comms #1124) that is unanswered at this SHA (THESEUS-06 BLOCKED); sent a
  courtesy report to Techne (#1114, prompts/2026-09-30_to_techne/). [IMPL]
  The seat explicitly refused to use agents/hephaestus/forge/ tools (368 .py
  "text-answer scorers built on NCD and regex") as seeds. [CLAIM, journal]

### 1B. May 2026 engine theseus/ (Techne, 2026-05-18 - 2026-06-23)

- theseus/CHARTER.md (2026-05-18): "Theseus -- The Substrate Generation
  Engine ... Sigma verifies; I generate." Consumer: "the future Ergon Learner
  (currently paused)". 40 generator types in 10 families; five per batch;
  epsilon-greedy bandit; 7-axis yield scoring. [INTENT]
- First commit 0bd7b5c27 (2026-05-18, "Theseus v0.1: substrate generation
  engine -- separate from sigma"). Commit activity by date (paths outside
  theseus/synth): 33 on 05-18, then 34/36/22/18/38 on 05-21..05-25, 74 on
  05-28, 38 on 05-29, sparse to 06-23, then 08-12 salvage and 08-18 recovery
  sweep 2f666d46d. About 318 tracked files outside theseus/synth. [IMPL]
- "Fires" #1 .. #141+ (journals/BATCH_LOG.md is 466 KB; 273 batches in
  orchestration/lifetime_stats.json, first 2026-05-18T14:23Z, last
  2026-05-30T09:56Z). [IMPL]
- Owner of record: Techne (the seat Theseus calls it "Techne's May 2026
  substrate-generation engine"); the name was never a seat before 09-30.
  Cited by Aporia, Charon, Diomedes, Ergon, Artemis, agents/talos (seat
  journal). [CLAIM]
- Pivot to audit era (2026-05-30 onward): calibration v2/v3/v3c, promotion
  replay, seam-fidelity fixes (see section 12). [IMPL via commits]

## 2. Engine/system inventory

### E1. theseus.synth (seat Theseus, "concept tensor / synthetic ancestry")

- Paths: theseus/synth/{substrate, compile_g0, entities, collide, battery,
  rulers, known, dark, ecology, run_v0, analysis}.py; tests
  theseus/synth/tests/test_synth_v0.py (10 tests after amendment 1). Line
  counts: substrate 400, collide 270, compile_g0 267, battery 269, rulers
  193, known 161, dark 184, ecology 132, entities 156, run_v0 654,
  analysis 494. [IMPL]
- Entrypoint: `python -m theseus.synth.run_v0 --tag <tag> --workers 4
  [--gens 30] [--smoke]`. Multiprocessing Pool, BLAS pinned to 1 thread.
  [IMPL run_v0.py]
- Versions: v0 code hashed in roles/Theseus/prereg/2026-09-30_v0/CODE_SHA256.txt
  (prereg commit 66f7f0db1); amendment-1 code in CODE_SHA256_AMENDMENT_1.txt
  (308330aaf). [IMPL]
- Dependencies: numpy; tyche.lens (execute, random_genome, mutate,
  lens_id), blob 2f309eeb8 at v0 and 5f3df8cc2 at v0_1. git (compile_g0
  calls `git show HEAD:agents/nous/src/concepts.py`). [IMPL]
- Inputs: 95 concept dicts (name, field, mechanism, short_description);
  45 enriched with Hecate extraction text; 60 LLM-arm genomes
  (theseus/controls/llm_arm_v0/GENOMES.jsonl, written by a fresh Claude
  agent from SPEC.md + TUPLES.json). [IMPL]
- Outputs/persistence (per run tag, all committed): theseus/corpus/g0/,
  entities/, lineages/, fingerprints/, collisions/, tensor/, archive/,
  dark_objects/, controls/ (incl. arms_<tag>.jsonl in v0_1), runs/<tag>/
  (CAL, CONFIG, POPULATION_HISTORY, REPRODUCTION, CANDIDATES, LENS_MARGINAL,
  VISUAL_EXPORT + trace_*.npz, REPORT.json, STDOUT), reports/<tag>.md.
  [IMPL]
- Scale: per run about 1,200 collision children over 30 generations; 95 G0;
  arms P/B/C 300 each, R 300, A 60, W 60, X 40, HK 20; known library 12 x 40
  = 480; 290-299 dark objects; 60 lens evolutions; 8-10 lenses admitted. v0
  wall 48 min, measured worker CPU 9,049 s; v0_1 wall 36 min, REPORT.json
  measured 6,677 s (commit message says "~7144 s"; phase 1/4 uninstrumented).
  [IMPL rows; RESULT-UNVERIFIED for CPU]

### E2. May 2026 claim-generation engine (theseus/ outside synth/)

- Paths: theseus/daemon.py (752 lines, batch loop), config.py, registry.py,
  generators/ (about 56 modules a1..z1, aa1, bb1 plus generators/stubs),
  scoring/ (info_density, diversity, training_weight, content_aware_promote,
  yield_tracker, corpus_health, h4 audits), bandit/ (epsilon_greedy,
  yield_proportional), emit/ (record_schema TheseusRecord, corpus writer),
  orchestration/ (heartbeat, lifetime, signature_index, telemetry),
  optimization/ (bayes_tuner), handoff/ (ergon_handoff 869 lines, CONTRACT,
  outbox), scripts/ (calibration_v0..v3c, promotion_replay_audit, fetchers),
  tests/ (about 40 test files). [IMPL]
- Entrypoint: `python -m theseus.daemon --batch-hours 1 --generators
  a1,b5,c1,d1,e1`. [IMPL README]
- Inputs: local catalogs (knots, BSD-rich elliptic curves, genus-2, modular
  forms, OEIS subset, LMFDB knowls, arXiv/Wikipedia caches). [IMPL a1,
  inventory.md]
- Output: TheseusRecord JSONL to theseus/corpus/<batch>.jsonl (ignored by
  git; theseus/corpus is empty in tree and was absent on M2 per Harmonia);
  training_anchor bundles to handoff/ergon_outbox/. [IMPL / CLAIM]
- Scale: lifetime_records 658,454,531; kills 367,214,821; confirmations
  244,417,008; inconclusive 46,670,435; "lifetime_discoveries_emitted" 2,351
  (theseus/orchestration/lifetime_stats.json). Throughput up to ~1.8e8
  records/h for a1 (BATCH_LOG). [IMPL file; RESULT-UNVERIFIED as counts]

## 3. Code architecture and dataflow

### E1 (synth), as read

run_v0.main phases:
0. compile_g0.compile_corpus(): concept text -> regex keyword hits for 16
   properties (PROPS table) -> fixed property->op table -> genome; numeric
   parameters drawn from an RNG seeded by sha256(name). Then G0 is evaluated
   (battery + dark assess), and the calibration Cal is built from viable G0
   and frozen (desc scales, z-scoring, PCA bases, grid edges at G0
   quantiles, tau_rep = median nearest-neighbour z-distance among viable G0,
   sparseness thresholds). [IMPL compile_g0.py:149-229, rulers.py:115-141]
1. known.build_library: 12 hand-written families x 40 random
   parameterisations, fingerprinted. [IMPL known.py]
2. Ecology, 30 generations: for each lane (G0, SHALLOW, DEEP, VERY_DEEP,
   DEEP_LENS) x arity (2, 3, 6) x 3: ecology.choose_coalition picks an
   ordered parent tuple from the active pool (seed weighted by 1/(1+uses);
   partners by mode near 0.3 / far 0.3 / under 0.2 / random 0.2 in an 8-D
   "field" that is tanh of a random projection of the z-fingerprint);
   collide.collide makes a child genome; battery.evaluate + dark.assess in
   the pool; viable children enter the archive and active pool; dark
   objects queue for lens evolution (2 per generation, tyche lens genomes,
   16 x 12 (mu+lambda)); admitted lenses become entities of kind "lens";
   fossilisation above POP_CAP 400 (non-binding in practice). [IMPL
   run_v0.py:246-372, ecology.py]
3. One-shot arms P/B/C (random G0 tuples, k = 2/3/6, one collision), arm A
   (LLM genomes, provenance overwritten to "llm"), R (random genomes
   complexity-matched to sampled D children), W (weird), X (neutral), HK
   (known-family genomes renamed "SYN"). [IMPL run_v0.py:376-420]
4. Mechanistic reproduction on the top-sparse candidates per arm and all
   HK; replication at IC seeds 2 and 3; "transfer"; rule-destroyed twins;
   lens-marginal sample of 60 per arm D/E/R/B. [IMPL run_v0.py:432-520]
5. analysis.analyse -> REPORT.json, report md; exports. [IMPL]

Code vs docs disagreements (seat docs are mostly accurate; these are the
gaps):
- "Concept tensor T[i1..ik] in CP form" (charter, collide.py docstring). In
  code the gain for slot j is 2*tanh(2*<u_i, w_j>) where u_i =
  tanh(fp_i @ P) (P a fixed random 34 x 8 projection, fp_i the parent's own
  fingerprint) and w_j a fixed random per-position vector (16 x 8). Each
  gain depends on ONE parent and ONE position; there is no term coupling
  indices i1..ik. The only higher-order interaction is the substrate "react"
  op, prod_j (bias + gain_j * tanh(S[src_j])), applied as one rule. The
  TensorStore.edges dict is written and exported but read only to forbid
  repeating an exact ordered tuple; uses/pair_uses feed the "underexplored"
  partner weight. Nothing is learned or fitted in the tensor. [IMPL
  collide.py:52-96,155-165; ecology.py:88-117]
- "Transfer" (charter: survival across implementation or substrate change)
  is computed as 1 - mean of six intervention-response entries already in
  the fingerprint (scale_up, scale_down, substrate_quantize,
  synchronous_update, topology_rewire, bc_change). No second substrate
  exists (THESEUS-12 backlog). [IMPL run_v0.py:494-506]
- "DEEP lane: all parents generation >= 5" is implemented as generation =
  1 + max parent generation; min_depth_to_g0 is a shortest path. So a DEEP
  child can sit 2 collisions from a G0 concept. Measured on committed v0_1
  entities (this crawl, zero-cost read): DEEP+VERY_DEEP min_depth_to_g0
  distribution {2: 127, 3: 84, 4: 183, 5: 32}; mean raw-human rule fraction
  0.30. The review packet reports this ("DEEP: min depth median 2"). [IMPL
  entities.py:50-51,68-84,126-148; CODE-INFERRED]
- "lensDependencies" in v0 was inherited ancestry (fixed in amendment 1);
  "requires evolved lens L" is still unmeasured for every strongest
  candidate (D7 in review packet). [CORRECTION]

### E2 (May engine), as read

daemon selects 5 generators (bandit), each generator.next() samples a tuple
and computes the verdict itself: a1 picks a random knot, random EC, random
integer invariant on each, random relation in {equal, equal_mod_2, divides,
abs_diff_le_3}, evaluates it, and sets verdict = SHADOW_CATALOG if holds
else REJECTED (generators/a1_catalog_cross_product.py, lines ~176-185). The
record is content-addressed (record_id = sha256 canonical), scored on
info_density / diversity / yield, journaled, and later mapped to Ergon
training anchors. F2 (content_aware_promote) ran in observation mode only
(daemon.py:432 per Harmonia). [IMPL; CLAIM for daemon line]

## 4. Claimed computational primitive vs actual mechanism

### E1 synth

- Label: "concept tensor / synthetic ancestry"; "human-derived conceptual
  primitives collided k-way in an executable high-dimensional substrate".
- Smallest actual mechanism: a list of <= 14 sequential numeric update rules
  from 19 hand-written ops (diffuse, advect, react, saturate, conserve,
  decay, remember, recall, threshold, replicate, select, mirror, coarse,
  delay, wrap, rank, drive, gate, lensmap) over X[C<=4, N=32] plus a memory
  field M, T = 128 steps, deterministic (substrate.py). A "concept" is the
  set of ops whose keyword fired in its prose plus name-seeded random
  parameters (compile_g0.py). A "collision" is splicing contiguous rule runs
  from each parent with a channel shift by parent position, inserting one
  react rule whose gains are a fixed random function of each parent's own
  fingerprint, applying 1-3 of 8 edit operators, and truncating to 14 rules
  (collide.py). "Ancestry" is exact parent-id bookkeeping. [IMPL]
- What it could express in principle: coupled 1-D reaction-diffusion /
  coupled-map-lattice dynamics with simple memory, delay (9 steps),
  switching, selection and forcing; an embedded Tyche lens can act as a
  causal feature map along the cell axis. No organism, no task, no
  input/output channel to an environment. [CODE-INFERRED]
- Phenomenon the ruler tried to observe: "behavioural novelty" -- whether
  deep descendants' 34-dim fingerprints occupy grid cells or distances not
  reached by other generators. Plus mechanistic non-reproduction and lens
  marginal value. This is a property of the generator distribution, not a
  reasoning act by an organism. [INTENT/IMPL]
- Could the "organism" perform it: there is no agent; the genome is the
  world. The relevant question is whether recursive splicing reaches
  fingerprint regions that single-shot splicing or random programs cannot.
  Given a 14-rule cap, contiguous copying, and the same 19 ops, the
  reachable program space for D, B, C and R is essentially the same set;
  only the distribution over it differs. [CODE-INFERRED]
- Could the ruler tell it from a cheap shortcut: no, by the seat's own
  measurement. NOT_REPRODUCED_YET rates: v0_1 D 12/20, R 8/10, A 0/10;
  lens-dependent fraction R 12/60 > E 8/60 > D 5/60. Weird high-gain
  programs pass viability 38-39/60. The hidden-known control passes 20/20
  because the hidden genomes are drawn from the same 12 family builders as
  the library they are matched against (run_v0.py:410-418, known.py), so it
  checks the search, not the ruler's ability to tell unknown mechanism from
  distance-to-library. [RESULT-UNVERIFIED; CODE-INFERRED]

### E2 May engine

- Label: "substrate generation engine"; "kills are first-class output";
  "novelty_vs_pretraining".
- Smallest actual mechanism: random sampling of (object, invariant,
  relation) tuples from local catalogs and evaluating a fixed integer
  predicate; mutation generators perturb previous records; the verdict is
  the generator's own evaluation. [IMPL a1]
- Could express: membership tests of a closed family of 33-35 claim kinds
  over catalog integers. No learning in the engine; bandit only reallocates
  generator time by a heuristic yield score. [CODE-INFERRED]
- Phenomenon targeted: cross-catalog coupling (for example knot invariant
  vs EC invariant parity) and training substrate for a downstream Learner.
- Shortcut: equal_mod_2 "holds" about 50-67% for arithmetic reasons
  (small-range invariants such as rank 0/1, torsion, tamagawa; the
  stratified audit shows divides ranging 32.8-90.6% by invariant); "kills"
  are random relations failing. Calibration v3 (c59d782de) shows the a1-only
  stream promotes 0/96 groups vs a re-pairing null. [RESULT-UNVERIFIED;
  CORRECTION]

## 5. Representation/state architecture

E1: genome JSON {C, topo {ring|line|rrg|mean|star, seed}, bc {periodic|
fixed0|reflect|absorb}, init {spike|random|gradient|blocks|alternate, amp},
rules [{op, src[], dst, p[], prov, lens?}]}. Runtime state X[C, N] float64,
M[C, N], 9-step history H for delay. Values clipped at 1e6. Entity record
{id, generation, ancestry (sorted all-ancestor ids), origin human|synthetic|
control|known, kind concept|mechanism|lens, executableRepresentation,
behavioralFingerprint (34 floats), lensDependencies, parentIds (ordered),
metadata, lane, state}. Fingerprint = 12 trace descriptors (log level,
temporal/spatial std, lag-1 autocorr, spectral entropy, dominant period,
active-cell fraction, moving-step fraction, spatial ac1, cross-channel
corr, memory of IC, value entropy) + 22 intervention responses, each
mean tanh(|d_i - d_0| / s), averaged over IC seeds 0 and 1. [IMPL
substrate.py, entities.py, battery.py]

E2: TheseusRecord (claim_kind, canonical claim string, payload with values,
verdict, kill_pattern, generator_id, record_id). Shape-keyed signature
index in orchestration/signature_index.sqlite (not present in tree). [IMPL
emit/record_schema.py; CLAIM for sqlite]

## 6. Organism/player architecture

E1: none in the agent sense. The "organisms" are (a) the genomes themselves
(evaluated, not acting) and (b) in dark.py a ridge regression that predicts
next-step per-channel spatial mean and std from observation features
(identity lenses L0 = [obs_t, obs_t-1], optionally + Tyche lens features),
trained on IC seeds {0,2,3,4}, tested on seed 1. "Exploitation by organisms"
ruler is backlog THESEUS-17. [IMPL dark.py]

E2: none. The "Learner" is Ergon's (paused; later greedy LoRA judged
"surface not reasoning" per commit 6439311af message). [CLAIM]

## 7. World/environment architecture

E1: the world is the genome's own field: 1-D, N = 32 cells (16 or 64 under
scale interventions), C <= 4 channels, T = 128 (256 under long_horizon),
five topologies, four boundary conditions, five IC kinds. Fully observed by
the battery; partial observation only in dark.py's 2C+3-dim observation
(spatial means, stds, 3 probe cells of channel 0). No external task, no
reward, no other agents. TOY SCALE: 128 real numbers per channel-time
slice at most 4 x 32; horizon 128. [IMPL]

E2: closed catalogs of math objects; the "world" is a lookup over a few
thousand knots and ECs (sizes not read here). [IMPL a1; UNKNOWN sizes]

## 8. Search/training/adaptation mechanism

E1: no fitness. Population drift by collision with partner modes; QD
archive per grid cell keyed by reproducibility (quality = -rep_dist), so
elites are the most reproducible members, not the most novel; vitality +1
per viable child, +2 if >= 2 rulers flag novelty, decay 0.9; fossilisation
above 400 (did not bind: active 581 in v0). Lens evolution inside dark.py:
(16 + 16) x 12 generations of tyche.lens.mutate, fitness = ridge residual
on training seeds. Bottlenecks/collapse modes the seat itself found: the
14-rule cap plus contiguous binding recycles G0 rule runs (raw-human rule
fraction 0.27 in DEEP v0, 0.24-0.35 v0_1); arity is irrelevant to viability
under the cap (P 0.703, B 0.707, C 0.720); generation correlates with
distance to the one-shot union at rho about 0.08-0.10. [IMPL;
RESULT-UNVERIFIED]

E2: epsilon-greedy bandit over generators by yield_score = info_density x
diversity / learner_delta_steps; per-generator Bayesian tuner
(optimization/). Collapse: a "92-consecutive-0-promoted bandit streak"
(c59d782de message). [IMPL; CLAIM]

## 9. Measurement/ruler stack

E1 (all in theseus/synth):
- Viability (battery.evaluate): deterministic (bitwise rerun), stable (no
  blowup), nontrivial, lifetime, transforms (|x_T - x_0| > 1e-3),
  responsive (not all responses < 0.02, not > 90% of them > 0.9),
  replicable (seed-0 vs seed-1 fingerprint z-distance < tau_rep).
- Niche grids: pca (top-4 PCs of G0 z-fingerprint), desc (mean response,
  log temporal std, spectral entropy, value entropy), resp (top-3 PCs of
  response block); 7 bins per axis at G0 quantiles 1/20/40/60/80/99.
- Metrics: euclid_z, cosine on z, quantile_l1 via G0 empirical CDF.
- H1 hard test (analysis.hard_test): equal-n subsample of viable D, A, B, C,
  R (n = min, here 51 because A has 51 viable of 60); EX_g(D) = cells only D
  occupies; 1000-permutation null; O_m = median min-distance to the other
  arms; 200-bootstrap CI of O(D) - O(R). PASS needs >= 2 grids p < .05 and
  >= 2 metric CIs above 0; FAIL if >= 2 grids <= null median or >= 2 CIs
  below 0. [IMPL analysis.py:80-132]
- Mechanistic reproduction (known.reproduce): nearest of 480 library
  fingerprints + 16 refinement evaluations; d* <= tau_rep REPRODUCED, <= 2
  tau_rep PARTIAL, else NOT_REPRODUCED_YET.
- Dark object gate: viable, resid_L0 >= 0.25 on held-out IC, max |ac1| of
  targets >= 0.5. Lens admission: held-out drop >= 0.05 and > p95 of 30
  random lenses.
- Validity gates: HK >= 80% reproduced/partial; X <= 5% viable; lineage
  integrity 0 mismatches.
- Predictions P1-P10 scored mechanically (analysis.score_predictions).
Blind spots: tau_rep is the median G0 nearest-neighbour distance, so
"replicable" means "closer to itself than a typical G0 neighbour" -- the
seat's Q2 asks whether that is too permissive; the descriptors are coarse
summary statistics of 1-D traces, so two different mechanisms with similar
summary statistics are indistinguishable; NOT_REPRODUCED_YET is distance
from a 12-family library; HK is self-referential (see s4). [IMPL;
CODE-INFERRED]

E2: per-generator 7-axis scores (throughput, info_density, diversity,
build_cost, run_cost, novelty_vs_pretraining as "heuristic estimate",
learner_delta_steps); F2 content_aware_promote (substrate_hold vs a random
re-pairing null) in observation mode; training_weight promotion threshold
0.6. Calibration scripts v0 (Murasugi, planted known-true relation) and v1
(EC torsion) were positive controls that F2 recovered. [IMPL scripts;
CLAIM for recovery]

## 10. Baselines and controls

E1 arms (run_v0.py): P/B/C one-shot G0 collisions at k = 2/3/6 (fixed-depth
controls); A = 60 Claude-written genomes (same model family as builder;
declared conflict, PREREG s9); R = random programs complexity-matched to D
(n_rules, C, max_src); W = weird high-gain programs; X = execution-neutral
programs (exact no-ops); HK = known families renamed SYN; rule-destroyed
twins; lineage-shuffle and behaviour-shuffle nulls (reported, not gated).
Missing: property-shuffled G0 (THESEUS-08), second model family for A
(THESEUS-21), planted deep-ancestry positive control (THESEUS-23; the
charter asked for this as "FIRST POSITIVE CONTROLS" and v0 did not build
it). [IMPL; CORRECTION vs charter]

E2: F1 monte-carlo random pairs generator as null baseline; calibration
v0/v1 planted relations; v3 a1-only uniform stream as unbiased null. [IMPL]

## 11. Historical experiment campaigns

C1. Theseus v0 (seat)
- id v0_2026-09-30; date 2026-09-30; prereg 66f7f0db1; result b63ae617f.
- Question: H1 FIRST HARD TEST. Organism: none (genomes). World: 1-D field.
  Pressure: none beyond viability; QD archive. Measurement: s9. Arms: D, E,
  P, B, C, A, R, W, X, HK. Scale: 30 gens, 1,202 ecology entities.
- Reported: H1 FAIL (grids EX(D) 23/24/8 vs null medians 22/24/8; CIs
  straddle 0); gates pass (HK 20/20, X 0/40, lineage 0/1202). P2, P4, P9
  wrong.
- Later reinterpretation: amendment 1 found the lens-parent leak into DEEP
  lanes, PYTHONHASHSEED-dependent coalition order, inherited
  lensDependencies, empty VISUAL_EXPORT. This crawl confirmed on committed
  v0 entities that 77 of 450 DEEP/VERY_DEEP children had a lens parent and
  19 had generation < 5 (minimum 1). [CORRECTION, verified]
- Label: INSTRUMENT FAILURE (contaminated D arm; recorded verdict FAIL).
- Paths: theseus/runs/v0_2026-09-30/, theseus/reports/v0_2026-09-30.md.

C2. Theseus v0_1 corrected replication (seat)
- Amendment 308330aaf; result c96bc5538; PYTHONHASHSEED=0.
- Reported: H1 INDETERMINATE (EX(D) 21/23/11 vs 21/21/7; resp p .089); viable
  D 338, A 51, B 223, C 219, R 175; same gates pass; strongest candidates
  M000617 (D, gen 15, min depth 4, raw-human rule fraction 0.08, euclid_z
  distance 8.1, NOT_REPRODUCED_YET 10.0, "transfer" 0.90, lens dependence
  NOT MEASURED) and M000946 (E). P10 ("FAIL again", p 0.8) wrong. Verified
  in this crawl: REPORT.json verdicts and grid numbers match the packet; v0_1
  D arm has 0 lens parents, min generation 6. Bitwise reproducibility NOT
  verified by a rerun (THESEUS-25).
- Label: INCONCLUSIVE.
- The v0 -> v0_1 flip from FAIL to INDETERMINATE under bug fixes plus a new
  random stream, at n = 51, is the seat's own headline: a single H1 run does
  not decide. [RESULT-UNVERIFIED]

C3. Smoke run (seat): outputs deleted unread except health lines (PREREG
s8). Label: UNKNOWN (not a campaign).

C4. May engine "fires" #1..#141+ (Techne, 2026-05-18..05-30)
- Question: produce volume of typed claims; measure per-generator yield.
- Reported: 658M lifetime records; corpus_health (05-18): 483,277
  emissions, 394,623 unique, 64.7% REJECTED, 31.7% SHADOW_CATALOG; "H4
  bridge" parity > divides > equal hierarchy (67.2% / 50.7% / 2.4%).
- Label: REPORTED POSITIVE at the time (volume, bridge hierarchy), LATER
  OVERTURNED as signal (see C5-C7).

C5. Calibration v2 / v2.1 corpus sweep (2026-05-30, e761891fd)
- v2.0 "cross-catalog parity contrast" (three_genus equal_mod_2 rank 77.8%
  vs 50.6%) was a field-name bug; fixed, parity is about null. 198/1,068
  groups divergent, mostly mutated-K relations from parent selection.
- Label: LATER OVERTURNED (v2.0) / MIXED (v2.1).

C6. Calibration v3 / v3c (2026-06-03, c59d782de, 962012725)
- Removing mutation inheritance: 1,068 -> 96 groups; a1-only promotes 0/96,
  max contrast 0.023. Residual contrast localised to g4/g5/a3 whose SHADOW
  verdict answers a different predicate stored in the same payload shape
  (claim-shape category error). F2 recovered planted v0/v1 relations.
- Label: REPORTED NEGATIVE/NULL (for corpus coupling); the instrument
  itself passed planted positives.

C7. Promotion replay and ledger census (2026-06-23, b092b86ac, 1f86b2590)
- total_promoted = 0 under the current training_weight formula; the cited
  2,351 discoveries is "a fossil of a superseded pre-Fire-#141 gate";
  ledger is shape-keyed with verdict in the dedup key, not content-replayable.
- Label: INSTRUMENT FAILURE (promotion gate shape-only).

C8. Ergon seam fixes (2026-06-15 db4b2cac4; 2026-06-22 6439311af)
- Handoff never emitted predicate_holds, so the ingester labelled every
  record, including kills, as promoted (79% promoted / 1.4% rejected
  inversion); a stopgap dropped about 89% of the corpus; the leak gate was a
  denylist that leaked CONFIRMED/REFUTED tokens into prompts. Fixed to an
  allowlist; "does not overturn greedy_lora_surface_not_reasoning".
- Label: CONTAMINATED (all pre-06-15 Learner consumption).

C9. Harmonia detector-band audit (2026-08-19,
roles/Harmonia/AUDIT_20260819_detector_band.md)
- 47 of 53 executing generators self-verdict at emission; 658,302,367 /
  658,454,531 = 99.98% self-verdicted; verify() never received a Theseus
  record. Ruling: the "blind band" excuse fails; the nulls are "367M genuine
  falsifications, within 33 claim kinds" -- sound but narrow.
- Label: REPORTED NEGATIVE/NULL (class-relative).

## 12. Reported results and later corrections (timelines)

T1 (May engine signal): claim "cross-catalog parity coupling" (v2.0) ->
evidence F2 contrast 77.8% vs 50.6% -> challenge field-name bug (v2.1,
05-30) -> correction parity at null; residual groups are mutation
selection bias (v3, 06-03) and claim-shape category error (v3c, 06-03) ->
status: no coupling detected under unbiased sampling. [CORRECTION]

T2 (May engine discoveries): claim 2,351 "discoveries emitted" ->
challenge promotion replay (06-23) -> correction total_promoted = 0 under
the current formula, count is a fossil; Charon/Ergon then corrected the
replay's own "bridge_extension absent" (sampling artifact) and ".176 dark
Postgres" (stale address) -> status: zero promotable; ledger not
content-replayable. [CORRECTION, two layers]

T3 (May engine as training substrate): claim Learner corpus -> challenge
program_audit_2026-06-10 79/1.4 inversion -> correction seam fixes (06-15,
06-22) -> status: consumption restored; reasoning transfer not shown.
[CORRECTION]

T4 (May engine nulls): claim "a year of nulls / blind band" -> Harmonia
08-19: verdicts were issued by emitters, not detectors -> status: nulls
sound within 33 claim kinds. [CORRECTION]

T5 (seat H1): v0 FAIL (b63ae617f) -> seat's own defect list -> amendment 1
-> v0_1 INDETERMINATE (c96bc5538) -> status: undecided; the seat recommends
fixing rulers before rerunning (THESEUS-23). [CORRECTION]

T6 (seat lens dependence): v0 strongest candidates "carry" lenses ->
measured drop about 0.004 -> lensDependencies redefined (amendment 1) ->
status: "requires evolved lens" unmeasured for every strongest candidate.
[CORRECTION]

T7 (Atlas): Atlas ATLAS_BURIED_SIGNALS_AND_RESIDUALS.md F1 lists "Theseus:
367,214,821 kills are SOUND within 33 claim kinds" and REGULARITIES.md
lists "Theseus | detector-band audit"; ARTIFACT_MAP.md cites "Theseus' 367
M kills are sound" and "self-verdicting at emission: Theseus". These all
refer to the May engine (E2), not the 2026-09-30 seat; Atlas does not
distinguish them. ATLAS_CROSS_ENGINE_SYNTHESIS_2026-09-30.md line 487
says Theseus is "Not covered ... (apart from the detector-band audit)", so
Atlas has no reading of theseus/synth. Atlas ARTIFACT_MAP.md also mentions
"the C4 foreign family from Theseus is not committed" (Cosmos context);
this crawl did not trace that item. [CORRECTION of locator; UNKNOWN for C4]

## 13. False-positive archaeology

- May engine parity coupling (T1): a field-name bug made 95% of raw-value
  records invisible to the scorer, leaving transformed records that
  manufactured contrast. Then mutation inheritance and meta-relational
  generators sharing a payload shape manufactured residual contrast.
- May engine "discoveries" (T2): promotion by assertion, never by content
  re-check; formula drift made the count non-replayable.
- May engine training labels (T3): one missing field flipped kills to
  positives for the downstream learner.
- Seat strongest candidates (M000617, M000946): "occupies cells absent from
  every control arm", "NOT_REPRODUCED_YET", "transfer 0.90" all read like
  novelty, but random programs score comparably on the same rulers and
  "transfer" is a fingerprint subset. The seat states this. Positive-looking
  table, no discriminating ruler behind it. [CORRECTION by seat]
- Seat HK gate: 20/20 looks like ruler validation, but hidden knowns are
  drawn from the library's own generator code; it validates the
  nearest-neighbour search, not mechanistic discrimination.
  [CODE-INFERRED]
- Seat genealogy: "generation 15 / VERY_DEEP" sounds far from human seeds;
  min depth 2-5 and 24-35% unchanged G0 rules say otherwise (the seat
  records this as P4 wrong). [RESULT-UNVERIFIED]

## 14. Likely false-negative regimes

- E1 H1 null could reflect: (a) the op set (19 human ops, 14-rule cap) so
  every arm samples the same program space; (b) the fingerprint (summary
  statistics of 1-D traces at 32 cells and 128 steps) too coarse to see
  mechanism differences; (c) n = 51 per arm (bounded by the A arm), at
  which the H1 statistic flipped between runs; (d) 30 generations and
  about 1,200 children; (e) no selection pressure toward anything (the
  ecology has no objective and the QD quality is reproducibility); (f) the
  "concept tensor" does not carry concept interactions, so the thesis about
  higher-order concept interaction was never actually instantiated. Any of
  these alone could hide a real depth effect. [CODE-INFERRED]
- E1 lens loop: the lens organism is ridge regression predicting spatial
  means/stds; Tyche lenses evolved 12 generations of 16; a dark object may
  be dark because the observation (2C+3 dims) discards spatial structure.
- E2: Harmonia's ruling is explicitly class-relative: the emitter could
  only pose 33 claim kinds; any coupling outside them was unposeable.
  Literature miners e2/e4/e5 produced nothing on M2. [CLAIM]

## 15. Phase 3 audit

### E1 theseus.synth

a. Representation richness:
- hierarchy: NO (flat rule list; no nesting; ancestry is metadata, not
  structure the program can use).
- compositional structure: PARTIAL (programs are sequential compositions of
  ops; collisions splice them; no reusable named sub-blocks).
- variable binding: NO (channel indices are fixed integers; remap by
  position only).
- memory: PARTIAL (M field via remember/recall; 9-step delay history).
- recurrence: YES in the dynamical sense (state iterates 128 steps); no
  recurrence over programs.
- counterfactual state: NO inside the program; the battery runs
  counterfactual interventions externally.
- latent variables: PARTIAL (memory field and non-observed channels in
  dark.py's observation).
- temporal abstraction: NO (coarse is spatial; delay is fixed lag).
- spatial abstraction: PARTIAL (coarse blockmean at 2^b scales).
- reusable substructure: PARTIAL (rule runs are copied from parents; no
  library or call mechanism).
- dynamic routing: PARTIAL (gate op routes by threshold on a channel).
- self-reference: NO.
b. Reasoning opportunity: none demanded. There is no environment, input
   stream, goal or reward; viability is satisfied by any non-trivial
   bounded dynamics. The H1 question is about the sampling distribution of
   a program generator. Nothing requires more than running fixed dynamics.
c. Shortcut surface: any random program of matched size reaches the same
   regions (measured); weird high-gain programs pass viability 63-65%;
   being far from a 12-family library earns NOT_REPRODUCED_YET; lens
   "dependence" can be gained by programs whose observation is poorly
   predicted by identity lenses for any reason; generation count inflates
   apparent depth while G0 rules survive verbatim.
d. Ruler resolving power: low for the intended claim. Viability, X and HK
   gates resolve what they target (broken vs not; neutral vs not; search
   reach). Niche, mechanistic and lens rulers do not separate R from D at
   n = 51 (seat's own finding).
e. Scale: field 4 x 32 (max 128 values), T 128; genome <= 14 rules from 19
   ops; fingerprint 34 dims; population active about 400-581; 30
   generations; about 1,200 children per run; 2 runs; 1 world type; 4 CPUs,
   under 3 core-hours per run.

### E2 May engine

a. Representation richness: all NO except compositional PARTIAL (mutation
   generators compose claim templates) and reusable substructure PARTIAL
   (kill-neighbourhood reuses records). Records are flat claim strings.
b. Reasoning opportunity: none in the engine; arithmetic predicate
   evaluation over sampled tuples. The downstream learner question lived
   in Ergon.
c. Shortcut surface: self-verdicting; small-range invariants make parity
   and divides relations hold at high base rates; mutation inheritance
   concentrates records near parents; payload-shape reuse across
   predicates.
d. Ruler resolving power: F2 resolved planted relations and refused
   artifacts after fixes (v3); promotion and yield scoring did not.
e. Scale: 658M records, 273 batches, about 56 generators, 33-35 claim kinds;
   compute small per record; catalogs local.

## 16. Research reports and substantial documents

- roles/Theseus/prompts/2026-09-30_charter/01_OPERATOR_CHARTER_verbatim.md --
  operator charter (17 KB).
- roles/Theseus/prereg/2026-09-30_v0/PREREG.md, PREREG_AMENDMENT_1.md,
  CODE_SHA256*.txt -- frozen design, H1 rule, predictions, defects.
- roles/Theseus/REVIEW_PACKET_v0_2026-09-30.txt -- self-contained v0/v0_1
  packet with exact numbers, defects D1-D7, reviewer questions.
- roles/Theseus/calibration/LEDGER.md -- 10 wrong-call rows.
- theseus/reports/v0_2026-09-30.md, v0_1_2026-09-30.md and
  theseus/runs/<tag>/REPORT.json -- machine reports.
- theseus/controls/llm_arm_v0/SPEC.md -- A-arm task spec.
- theseus/CHARTER.md, README.md, ROADMAP.md, inventory.md -- May engine
  doctrine and generator catalog.
- theseus/docs/frontier_techniques_analysis.md -- Fire #2 analysis of 17
  techniques (21 KB, not read in full).
- theseus/corpus_health_report.md, cross_catalog_h4_report.md,
  h4_stratified_audit_report.md -- May 18 corpus statistics.
- theseus/handoff/CONTRACT.md -- Theseus to Ergon bundle protocol.
- pivot/calibration_v2_corpus_sweep_2026-05-30.md,
  pivot/calibration_v3_VERDICT_2026-06-03.md,
  pivot/..._VERDICT_generator_category_error_2026-06-03.md -- audit verdicts
  (not opened; content taken from commit messages).
- roles/Techne/M05_PROMOTION_REPLAY_FINDINGS_2026-06-23.md -- promotion
  replay (not opened).
- roles/Ergon/SEAM_FIDELITY_FIX_2026-06-15.md,
  SEAM_ALLOWLIST_REBUILD_2026-06-22.md -- handoff fixes (not opened).
- roles/Harmonia/AUDIT_20260819_detector_band.md -- 99.98% self-verdict
  ruling (read in part).

## 17. Journals/TODOs/backlogs/pivots/abandoned branches

- roles/Theseus/journal/2026-09-30.md -- creation, charter, build, runs,
  CWO-B; records environment fixes (psycopg2, pytest installed user-scoped).
- roles/Theseus/TODO.md, BACKLOG_H0H5.md -- THESEUS-23 (make rulers
  discriminate with planted deep-ancestry positives), 24 (raise n via 300
  LLM genomes), 20 (multi-seed), 25 (bitwise rerun), 26 (binding pop cap),
  06 (Tyche interface, blocked), 07-22 (length-normalised compiler,
  property-shuffled G0, bigger known library, Tyche organisms for dark
  objects, evolvable fingerprint, second substrate, SYN concepts, higher
  arities, arity x depth factorial, evolved experiments, organism
  exploitation ruler, visual export, scale-up, second LLM family, wiki).
  All open. [IMPL]
- Branch theseus/charter-v0-2026-09-30 (seat); merged to main. No
  abandoned branch found for the seat.
- May engine: journals/BATCH_LOG.md (466 KB batch log, not read in full);
  ROADMAP Tier 2-4 (local LLM paraphrase, frontier API, Learner curiosity)
  never built (stub_tier2/3/future in inventory.md). Handoff outbox from
  May recovered from a dropped stash on 2026-08-18 (2f666d46d), "stored,
  not endorsed". [IMPL]

## 18. Dependencies on other engines and seats

E1: agents/nous/src/concepts.py (G0 ore, read via git show); hecate/programs/
HT-*/program.json (Pass-0 text); tyche/lens.py (lens executor imported
read-only inside substrate and dark); comms on M1 (192.168.1.202); MWO-0004
envelope. Would feed: Tyche (dark objects, unanswered), Visual Cortex
(VISUAL_EXPORT rows, format not committed). [IMPL]

E2: sigma_kernel, prometheus_math (imports), local catalogs, Techne
contracts (training_anchor schema), Ergon ingester, Aporia deep-research
batches (E1 generator), Charon signature_index review. [IMPL/CLAIM]

## 19. Scaling limitations

E1: O(22 interventions x 2 seeds x T x rules) per candidate (0.93 s each on
the host); quadratic distance matrices in sparseness/H1 (fine at 10^3,
not at 10^6); single 4-CPU host; the A arm caps H1 n at 51 regardless of
ecology size; MAXRULES and CMAX are hard constants; POP_CAP non-binding.
Scaling the ecology without changing op set, cap or fingerprint would, by
the seat's own reasoning, "buy compute, not evidence". [IMPL; CLAIM]

E2: volume scaled to 10^8 records/h easily; the limit was semantic (claim
kinds) and evaluative (self-verdict, shape-keyed ledger), not compute.

## 20. Lens potential for Phase 3 (descriptive, no ranking)

E1 synth as a lens on "does recursive recombination expand behaviour space":
- substrate: sequential op programs over a small 1-D multichannel field;
  organisms: none (genomes as worlds); worlds: the genome's own field;
  pressures: none (drift + QD reproducibility); phenomenon family:
  generator-distribution coverage / open-endedness of recombination;
  current resolving mechanism: equal-n grid occupancy + nearest-distance
  bootstrap + library reproduction; likely resolution ceiling: cannot
  separate structured descent from matched random programs at n about 50;
  noise sources: arm subsampling, IC seeds, set-order (fixed), small A arm;
  architectural limit: fixed op set, 14-rule cap, summary-statistic
  fingerprint, no task.
- reusable parts: exact lineage registry with ordered parents and
  rule-level provenance (raw-human rule fraction); intervention battery
  pattern (22 named interventions, frozen scales); frozen-calibration
  discipline; execution-neutral and rule-destroyed-twin controls;
  equal-n permutation niche test; preregistered prediction scoring.
- toy-grade parts: keyword compiler (text-length confound: enriched
  concepts compile to 10-14 rules, others 2-3); "concept tensor" (random
  fixed readout, no interaction); 12-family known library; "transfer"
  score; LLM arm from the builder's model family.
- unknowns: whether any fingerprint can see mechanism-level differences in
  this substrate; v0_1 reproducibility; what planted deep-ancestry
  positives would show.

E2 May engine as a lens on "falsification at volume":
- reusable: content-addressed records, the F2 substrate-vs-null contrast
  with planted calibrations (v0 Murasugi, v1 EC torsion), the leak-free
  allowlist renderer, promotion replay tooling, the signature census.
- toy-grade: the claim kinds themselves (random cross-catalog integer
  relations).
- unknowns: the content of BATCH_LOG decisions beyond the last entries;
  whether the 1,694-record "trace_field_class abs_diff_le_0 torsion"
  residual (v2.1) was ever followed up.

## 21. Open questions / coverage gaps

Not read or read only in part: theseus/synth/analysis.py beyond hard_test
and function list; theseus/reports/*.md (used REPORT.json and the packet
instead); runs/*/REPRODUCTION, CANDIDATES, LENS_MARGINAL rows; the LLM arm
genomes; theseus/docs/frontier_techniques_analysis.md; journals/BATCH_LOG.md
(only the tail); most of the 56 May generators (only a1 read in full);
daemon.py, scoring/*.py, handoff/ergon_handoff.py bodies; the pivot/ verdict
files, Techne M05 findings and Ergon seam documents (taken from commit
messages); comms bodies #1114, #1124, #1125 (not read; only seat copies).
Unresolved: whether Tyche ever answered #1124; the Cosmos "C4 foreign family
from Theseus" Atlas mention; whether any later seat re-ran H1. Zero-cost
inspections run by this crawl: Python reads of committed REPORT.json and
entities JSONL for both runs (counts in s11 C1/C2 and s3). No code was
executed.
