# Ensorain -- Phase 3 intake dossier

- Seat: Ensorain
- Crawler: Tantalus (worker)
- Tree: origin/main at 21a47402a (worktree F:\Prometheus-worktrees\tantalus-phase3-intake)
- Date: 2026-10-01

Summary. Ensorain ("TensorTrain without the Ts") is an M2 (SPECTREX5) ENVIRONMENT + INSTRUMENT
seat created 2026-09-23 that ran, in eight days, five distinct engine generations and roughly
thirteen preregistered or precommitted campaign lines, all CPU-only numpy, all on branch
ensorain/base-role-adopt-2026-09-23 and merged to main [IMPL git log -- ensorain roles/Ensorain,
197 commits]. Charter 1 (2026-09-23, Tensor World Engine falsifier) produced E0, E1, E1.5, E2: a
single organism walks a 4096-cell graph whose node values are a hidden rank-3 tensor-train field,
predicts exit values from a bounded TT (or rival) memory and greedily moves [IMPL ensorain/e0/,
e1/]. Every verdict was INDETERMINATE or CLOSE (B); the one "positive" (E1.5) was a correctly
ordered TT beating a matrix on a TT-generated world, which the seat itself called a tautology
[CLAIM E1P5_VERDICT s3]. An exploratory D-series dial search (~19,300 lives) found one replicated
amplifier coupling. Charter 2 (2026-09-24, Tensor Physics of Intelligence Foundry) produced the
WTP "World Genome" foundry in three generations: WTP-01 (ruler normalised by current field
variance; top anomalies were a variance-collapse artifact), WTP-02 (ruler referenced to the ZERO
predictor; the sole EXPAND specimen was a one-float running mean, killed post-data by a
constant-predictor test), WTP-03 (null ladder N0-N5 incl. the optimal constant; 9 promoted
specimens were bounded online matrix/tensor completion beaten by a post-data tuned batch fit
N6). Thereafter a steward-directed Lossless Memorizer Challenge (WTP-LM01) was built, frozen
twice (v0.3.1, v0.3.2 at ee8cbe0c8) and never launched; the ARC3 program ran small answer-keyed
dev studies (sufficiency ladder, CSSR causal states, PKG-F drift/selectivity gate, LM02 window
assay) and the "instrument line" was frozen 2026-09-30 with the seat pointed at an unbuilt
WTP-04 "Habitable Islands". In code, "tensor" almost everywhere means a small dense numpy array
of 64-4096 scalar cells (2-11 modes) used as a regression target over discrete index tuples;
organisms are online regressors over cell addresses attached to a fixed hand-coded movement
policy [IMPL]. No GPU, cuTENSOR, tensor-network contraction planner or learned policy exists in
the tree [IMPL grep for cuda/torch/cupy: none].

## 1. Identity, charter and pivots

- Creation: 2026-09-23, commit 57ed9184e, operator one-line instruction quoted verbatim in
  roles/Ensorain/superseded/RESPONSIBILITIES_2026-09-23_precharter.md [IMPL]. Host M2 (SPECTREX5);
  comms on M1 store (EW_DB_HOST=192.168.1.202) [IMPL STATUS.md, RESUME.md]. Instances recorded:
  m2-14baf7d5 (09-23..09-25), m2-32b65655 (09-25..09-29), m2-a466d709 (09-30) [IMPL journal and
  review headers]. Commits are authored "James Craig" with a Claude co-author trailer [IMPL git].
- Pivot 0 -> 1 (2026-09-23, 20a4bab5c): founding directive "Build the Tensor World Engine. Make
  it earn the right to exist" (roles/Ensorain/prompts/2026-09-23_charter/01_FOUNDING_DIRECTIVE_verbatim.md).
  The paste was TRUNCATED inside s12 "THE CRITICAL MEASUREMENT" (only the numerator "retained
  useful information" arrived); the seat built an INTERIM measure (R^2 on unvisited cells) and
  never received the remainder [IMPL 00_README.md; E0_VERDICT s7]. Binary goal: A "intriguing" or
  B "fun but not a good use of tokens" [INTENT].
- Pivot 1 -> 2 (2026-09-24, 34a75ac19): Foundry directive (4,828 words; 59 sections) turning the
  seat into a "World-Genome engine" mutating world law x representation x memory x search x
  credit x resource x topology x time; first campaign WTP-01 [INTENT
  prompts/2026-09-24_foundry_directive/]. Old charter body moved to
  superseded/RESPONSIBILITIES_2026-09-24_tensor_world_engine.md [IMPL].
- Interlude 2026-09-24 (0180ab244): operator "dials of intelligence" text -> D-series
  [IMPL prompts/2026-09-24_dials_of_intelligence/].
- Pivot 2 -> steward direction (2026-09-25, f3b530624): Cyclops (M2 selective-irreversibility
  steward, peer Aporia M1) directive WTP-LM01 "Lossless Memorizer Challenge" supersedes WTP-04;
  heartbeats to stewards every 60-90 min [IMPL prompts/2026-09-25_wtp_lm01_directive/]. On
  2026-09-26 the operator FROZE steward management via comms; launch authority returned to the
  operator only (#732/#733) [IMPL STATUS.md; prompts/2026-09-26_lm01_operator_rulings/].
- Pivot 3 (2026-09-28, 55f6a4f97): operator ARC3 directive "memory, compression, selectivity,
  generalization" research principal; LM01 queued but never launched because the ARC3 text lacked
  the exact gate phrase [IMPL prompts/2026-09-28_arc3_directive/00_README.md; arc3/QUEUE.md].
- Pivot 4 (2026-09-30, c3525f647, fd582afb2): operator direction "finish PKG-F, bound LM02, freeze
  the line, then WTP-04 Habitable Islands"; "CHEAP COMPETITORS FIRST, ALWAYS" [IMPL
  prompts/2026-09-30_operator_direction/; arc3/INSTRUMENT_LINE_FREEZE_2026-09-30.md].
- Operating frame since 09-28/29: MWO work orders (MWO-0001..0004 adopted; WORK_STATE.json
  mwo_id MWO-0004), Fabric tasks for replication, CWO 2026-09-30 [IMPL WORK_STATE.json,
  MIGRATION_REPORT_MWO-0002.json].
- Relationships: Cyclops/Aporia (stewards, LM01), Harmonia (holds "frozen text" of the SI law,
  PREREG_WTP_LM01 s1), Artemis (external reviewer R-08/R-16 -> DEF-ENS-002, ERRATA E-1),
  Bellerophon (shared M2 CPU; "blind-lane: never message Bellerophon about the program"),
  Cosmos (named in the dials text as the natural home of a dial search) [IMPL].
- Current state on this tree: STATUS.md is STALE (currency 2026-09-26) while WORK_STATE.json is
  2026-09-30 (CURRENT = WTP-04 Habitable Islands, LM01 HOLD) [IMPL; also noted by Atlas
  ATLAS_CROSS_ENGINE_SYNTHESIS line 482].

## 2. Engine/system inventory

Totals: ensorain/ has 596 files; ~16.8k lines of Python across the engine packages listed below
[IMPL wc]. All rows (runs/*.jsonl, runs/wtp0x/*.json) are committed; WTP-02 waveA.json alone is
~1.3M lines [IMPL git show --stat 42c190ae3].

E-ENGINE (E0/E1/E1.5/E2), ensorain/e0, e1, e1p5, e2 (2026-09-23).
- Purpose: falsify "bounded TT memory discovers reusable latent structure" [INTENT].
- Key modules: e0/world.py (6-mode 4^6=4096-cell TT field, rank 3, class-level mode scramble,
  WORLD R by value permutation), e0/tt.py (TT cores (r,n,r), eval, NLMS/cyclic/sgd updates, TT-SVD;
  provenance Oseledets 2011), e0/memories.py (NoMem, LRU, HASH, KNN, ADDITIVE, RF, LOWRANK, TT
  variants, audited cap), e0/life.py (fixed policy skeleton), e0/evolve.py (GA on TT genome), e1/
  (4-mode 8^4 field, true ranks (3,3,3) = 192 params, delayed fiber observations, locks L1-L3,
  charged batch "consolidation" by proximal ridge ALS), e1p5/ (post-life self-compression,
  effective ranks), e2/ (17-hypothesis structure discovery: 12 TT orders + 3 matrix partitions +
  CP + NONE, successive halving SD arm) [IMPL]. Entrypoints run_dev.py, run_confirm.py,
  campaign.py, score.py (frozen scorers). Persistence: JSONL rows in ensorain/runs/.
- Scale: E0 15,760 confirmatory lives; E1 10,081; E1.5 12,960; E2 4,800 [CLAIM verdicts].

D-ENGINE (dials), ensorain/d1/ (2026-09-24).
- Purpose: randomized dial search for couplings ("intelligence = phase behaviour of couplings")
  [INTENT]. World = E2 family lock worlds + drift + noise; organism = E1 memory (TT/CP/LR) + replay
  store + error store + dial-controlled consolidation [IMPL d1/core.py docstring]. Two-way ANOVA
  instrument with synthetic additive/coupled controls (dials_retro.py, d1/analyze.py) [IMPL].
- Scale: ~19,300 lives over 4 rounds [CLAIM DIALS_SYNTHESIS].

WTP v1 FOUNDRY, ensorain/wtp/ (93998df6f, 2026-09-24).
- genome.py: JSON World Genome with substrate (dims, generator, rank, field op chain), geometry
  (12 kinds), observation (cell/fiber/marginal/masked/probe_only + vector op chain + noise),
  transition (drift, basis change, rewire, catastrophes), irreversibility, resource prices,
  memory (10 substrates, cap 16-1024 floats, bits, forgetting, fluidity), learning (7 rules),
  credit (delay, radius, noise, sign flip), search policy (7 fixed policies), boundary (n_org in
  {1,2,4}, marks), time (lifetime 200-600) [IMPL genome.py:62-104].
- registry.py: 34 "atoms" (f_* field transforms applied ONCE at build: permute, contract_mode,
  reduce, merge/split mode, Hadamard, tt_round, svd_power, qr_mode, gemv_mode, fft_abs, lowpass,
  phase_scramble, noise, sparsify, mask; v_* observation transforms: fft_abs, sign, quantize,
  sort, cumsum, tanh) [IMPL registry.py:57-260].
- world.py: build_field (generators tt/cp/lowrank/pairwise/sparse/spectral/random/sum; field
  64..4096 cells, ndim>=2, standardised to mean 0 / sd 1), build_graph, run_world (organism loop,
  128-cell scoring battery, CG) [IMPL]. organism.py: memory substrates [IMPL]. detect.py: A1-A6.
  campaign.py: Waves A-E, verdict. Scale: 3,000 genomes, ~30 min wall [CLAIM WTP01 report].

WTP v2 EXECUTOR, ensorain/wtp2/ (08fa0c8d3, 2026-09-24).
- Reuses WTP v1 genome/registry/generators/substrates; replaces randomness (8 named SeedSequence
  streams), measurement (fixed V0, AC = -log10(MSE/V0) clipped [-3,6], CG and CGu vs ZERO
  predictor), degeneracy checks and admission (necessity preflight N1-N5) [IMPL world2.py:1-40,
  PREREG_WTP02 s1-s2]. Detectors D1-D9 (detect2.py). kill_const.py (post-data A8). Scale: 24,000
  candidates -> 1,500 admitted, 6,000 Wave A lives, 20 workers, ~1 h [CLAIM].

WTP v3 SUBSTRATE COLLIDER, ensorain/wtp3/ (bcba874b9, 2026-09-24).
- collider.py: one experience stream per (world, seed) generated by a FIXED behaviour carrier
  (the marginal learner), replayed to every substrate; test sets interp / novel / recomb
  (pair-block holdout); null ladder N0 zero, N1 const (+recent), N2 marginal, N3 linear, N4
  bounded lookup, N5 best simple online substrate; XC = AC - max(null ladder); exact
  marginal-preserving surrogate [IMPL collider.py:1-15, 172-201]. world3.py, controls.py
  (planted worlds), validate3.py (V1-V7), recipes.py, n6_check.py (post-data N6), autopsy.py.
  Scale: 38,000 candidates, 611 min Wave A, 181 admitted [CLAIM].

LM01 HARNESS, ensorain/lm01/ (2026-09-25..28).
- families.py: F1 episodic (iid field), F2 latent, F3 switch (3 episodes), F4 fresh-field transfer
  (w=.6), F5 nuisance mode; levels 8^3, 12^3, 16^3; exposure = tensor-index walk, NO economy and
  NO carrier learner [IMPL docstring]. arms.py: L-K (min-Hamming kernel over full exact store),
  L-R (per-query ridge-ALS refit on the full store, discarded), SELECTIVE (WTP substrates),
  RandomMerge, HYBRID (exact store + learned low-rank key), BufferALS reservoir with eviction
  policies, cheat fixtures LRCache/LRSubsample [IMPL arms.py:1-20]. accounting.py, recover.py
  (HR2), analysis.py (frozen verdict rules), launch_gate.py (exact operator phrase), freeze.py
  (FREEZE.json, 60 files). Campaign 1,968 worlds, ~10 h at 8 workers, NEVER RUN [IMPL QUEUE.md].

ARC3 DEV INSTRUMENTS, ensorain/arc3/ (2026-09-28..30).
- suff/: answer-keyed sufficiency ladder (binary processes: iid, order-k Markov, golden mean,
  Even process, key-value Zipf streams with exact Bayes oracles), learners STAT(k), VERB_SUM,
  NEAREST, TABLE, WINDOW, HMM, CSSR (split/vote), CSSR->EM->mixture, crypticity estimators
  [IMPL suff/worlds.py, learners.py, cssr.py]. These are NOT tensor worlds.
- pkgf_*.py (17 scripts): drift / obsolete-record restoration probes v1-v9b, W-DRIFT, W-MULTI,
  soft per-cell gate, observability gate (pkgf_obs.obs_keep, gate of record) [IMPL].
- lm02/assay.py, score.py: window-sufficiency assay on 12^3 fields, 11 drift regimes x 8 worlds
  [IMPL]. lit/: three literature raids (~24k words) [IMPL].

## 3. Code architecture and dataflow

- E-engine life loop (e0/life.py:28-87) [IMPL]: per step, observe noisy value y = x[pos] + N(0, .1);
  mem.observe(addr, y); harvest g = 3 * max(0, x[pos] - .5) if regrown (500 steps); predict
  every non-tabu exit's value from memory; argmax with epsilon .1; energy -= 1 + kappa * flops.
  Instrumentation after life: R^2 on all cells and unvisited cells via mem.predict_all. The
  policy is identical across arms; only memory differs [IMPL docstring]. Dataflow: field ->
  scalar observations -> regressor update -> value predictions for <=5 exits -> move.
- WTP v1 run_world (wtp/world.py:236-529) [IMPL]: build field (generator + op chain) -> optional
  shuffle/reskin -> graph (nodes map to cells by random/sorted/blocked map) -> organisms; each
  step observe (cell/fiber/marginal through a vector op chain), learn, choose next node by a
  FIXED policy over predicted cell values (greedy/eps/softmax/novelty bonus/rollout of depth
  <=4/probe), pay prices, maybe hazard the memory; checkpoint NLMSE on battery; end-of-life CG.
- WTP v2: same loop, environment pre-drawn per step from named streams so twins see identical
  environments; four twins per world (real, shuffled, frozen, random walker) [IMPL world2.py].
  NOTE (code vs prose): the organism learns from TRANSFORMED observations (vector chain such as
  v_fft_abs -> v_tanh, world2.py:185-210) but is scored against the raw field x on the battery
  [IMPL]. This is why a running mean of a positive transformed quantity could beat zero
  [CLAIM WTP02 report s3].
- WTP v3: the closed loop is cut. A fixed carrier walks and generates the stream; every substrate
  and null is fit to that stream; AC/XC on held-out cells [IMPL collider.py docstring]. So in
  WTP-03 the "organism" has no influence on what it sees [CODE-INFERRED].
- LM01: no economy, no agent; a walk generates (cell, value) records; arms ingest records and
  are queried on held-out cells [IMPL families.py].
- Doc vs code disagreements found:
  * Foundry prose: "a contraction can be movement", "a factor can be a continent", graph
    topology depending on organism memory, multi-organism communication, self-modification of
    update rules. Code: field ops run once at build; geometry kinds are fixed graphs (one,
    "spectral_roads", derives roads from a singular vector) [IMPL world.py:172]; marks are a
    per-cell dict; no communication channel; no rule self-modification [IMPL]. [CORRECTION of
    prose by code]
  * Founding directive asked for local GPU use; E0_VERDICT s7 says no GPU was used ("tiny
    per-organism tensors are faster on CPU") [IMPL]; no GPU code exists anywhere in ensorain/.
  * WTP-01 report R1 required "competence against ... the mean predictor"; PREREG_WTP02 R1
    implemented the ZERO predictor instead (PREREG_WTP02.md:18) [IMPL]. That translation is the
    root of the WTP-02 constant-predictor failure (section 9).
  * DEF-ENS-002: WTP campaign.py:146 sets REPLICATED from hits >= 3 and records replay_ok without
    gating on it; wtp3/campaign3.py:339 has no replay check [IMPL DEFECTS.md, verified by seat].

## 4. Claimed computational primitive vs actual mechanism

E-ENGINE.
- Label: "bounded-memory TensorTrain organisms whose brains are tensors" discovering "increasingly
  efficient tensor representations" [INTENT founding directive s0-s1].
- Smallest actual mechanism: a TT-format regressor f(i1..iD) = G1[i1]...GD[iD] with <=~200
  parameters, updated by NLMS on one noisy scalar per step (E0) or by proximal ridge ALS on a
  128-sample buffer (E1), used to rank <=5 neighbour cells; GA over (ranks, mode order, constants)
  across lifetimes [IMPL e0/tt.py, e1/mem.py, e0/evolve.py].
- Could express: low-rank tensor completion of a scalar field over a 4096-cell grid; nothing
  sequential or relational beyond that [CODE-INFERRED].
- Ruler target: "reusable latent factors" -> held-out R^2 on unvisited cells, harvest, EFF =
  (U - U_NOMEM)/params, transplant after relabeling [IMPL score.py].
- Could the organism perform it: only with the latent mode order supplied or found by random
  search and 10-20 ALS sweeps (E1.5) [CLAIM]. Order discovery from experience failed (E2) [CLAIM].
- Shortcut discrimination: E0's harvest was won by coarse local ranking (rank-1/2 TTs, R^2 ~0 on
  unvisited cells) [CLAIM E0 F1]; E1 fixed this by EFF and locks. The TT-vs-matrix contrast is
  tautological in a TT-generated world (seat's own S3) [CLAIM].

D-ENGINE.
- Label: "dials of intelligence" / phase behaviour of a coupled adaptive system [INTENT].
- Actual: factorial/ANOVA over knobs (proximal pull lam, sweeps, scratch buffer size, replay,
  drift, capacity, restructuring probability, dreams, surprise weighting) of the same ALS
  completion learner [IMPL d1/core.py].
- Ruler: NLMSE/EFF interaction F tests vs synthetic additive and coupled grids [IMPL].
- Shortcut: most nominated couplings were accounting artifacts (price x compute inside EFF),
  definitional, or floor compression [CLAIM DIALS_SYNTHESIS].

WTP v1/v2 FOUNDRY.
- Label: "tensor physics of intelligence", world genomes composing tensor / linear-algebra /
  spectral / stochastic / graph atoms [INTENT].
- Actual: a scalar field over <=4096 cells produced by one generator plus <=3 build-time
  transforms; an organism = one online regressor over cell indices (none/table/sketch/additive/
  lowrank/tt/cp/dct/marks/mixture, 16-1024 floats) + a FIXED movement heuristic over predicted
  values; reward = field value minus threshold at visited nodes [IMPL]. The base Memory class
  ("none", "marks") is a ONE-FLOAT RUNNING MEAN (organism.py:14-33) [IMPL].
- Could express: interpolation/completion of the field; lookup; external marking of cells
  [CODE-INFERRED]. Policy cannot learn; there is no state beyond the regressor and a visited set.
- Ruler target: "competence" = gain in predictive accuracy of the field on a random battery
  (v1: vs birth memory, normalised by battery variance; v2: CGu vs zero predictor on unseen cells),
  plus detectors for jumps, reorganisation, reachability, compute amortisation [IMPL].
- Could the ruler tell it from a cheap shortcut: NO in v1 (variance-collapse and tables) and NO in
  v2 (constant) -- both demonstrated by the seat [CLAIM WTP01/02 reports].

WTP v3 COLLIDER.
- Label: substrate collider for "candidate intelligence physics" [INTENT].
- Actual: offline-ordered online regression of every substrate on one shared (cell, value) stream,
  scored on unseen/novel/pair-block cells against N0-N5; extras (reskin, carrier ablation,
  recombination, transfer to the same field) [IMPL].
- Ruler resolving power: kills constant/marginal/lookup counterfeits (V2/V3 validation) [CLAIM],
  but admission G5 pre-selects completion-friendly worlds and N6 was missing, so it could only
  re-find bounded matrix/tensor completion [CLAIM WTP03 W2/W4].

LM01 / ARC3.
- Label: "Lossless Memorizer countermodel to the Selective Irreversibility Hypothesis"; "when is
  discarding information necessary for generalization" [INTENT].
- Actual: comparison of exact record stores with readouts (kernel, refit ALS) vs bounded online
  substrates vs reservoirs on tensor-field completion (LM01, never run); binary stochastic-process
  prediction vs exact Bayes (S1, CSSR); record freshness gates under synthetic drift (PKG-F, LM02)
  [IMPL]. Mechanism class: estimation/statistics, not organisms.

## 5. Representation/state architecture

- E0/E1 field: x of shape [4]^6 (E0) or [8]^4 (E1), generated as an exact TT with ranks 3 (E0) or
  (3,3,3) (E1), observed coordinates are a class-level permutation of latent modes [IMPL
  e0/world.py:17-33, e1/world.py]. WORLD R permutes values over lam-fraction of cells [IMPL].
- Organism state E0: TT cores G_k of shape (r_{k-1}, 4, r_k) with order permutation, hard float
  cap C in {96,168,384,4096...} audited by memories.audit; transient 8-entry tabu (scratch,
  same for all arms) [IMPL]. E1: TT/CP/LOWRANK/MLP parameters + 128-sample buffer for charged
  consolidation [IMPL e1/mem.py].
- WTP field: numpy array dims chosen by style (binary 2^6..2^11, many_small, few_big up to 29 per
  mode, mixed primes), clipped to 64..4096 cells [IMPL genome.py:32-51]. After build: standardised
  real scalar per cell; no tensor operations happen during a life except drift/basis-change/
  catastrophe transitions and hazards that SVD-truncate, permute or scramble the memory arrays
  [IMPL world.py, organism.py:51-70].
- WTP organism state: one memory substrate's arrays (TT cores via e0.tt.TT; CP factors; low-rank
  U,V on a balanced unfolding; DCT coefficients; additive per-mode tables; table keys/values;
  hashed sketch), a running mean, optional external marks dict, visited set, buffer [IMPL].
  "tt" in WTP is the same E0 TT class [IMPL organism.py:11].
- LM01/ARC3 state: exact record arrays (A, y, t), bounded factors, reservoirs, per-cell
  sufficient statistics (sum, count), CSSR state machines over binary histories (<= ~7 states)
  [IMPL].
- What "tensor" means in code: small dense float arrays (numpy), TT/CP/low-rank factorisations of
  them, and np.tensordot when generating fields or expanding a TT [IMPL]. No tensor network
  graph, contraction ordering search, cuTENSOR/cuTensorNet, block-sparse contraction, or tensor
  messages exist [IMPL]. The prose's "contraction lock", "spectral gate", "mode permutation
  puzzle", "delayed relevance P7" puzzle families: P1/P2/P6-like content exists implicitly as
  completion; P4/P5/P7 were not built in E0 [CLAIM E0_VERDICT s7]; E1 added delayed fiber
  observations and locks (a partial P7) [IMPL e1/world.py].

## 6. Organism/player architecture

- Single organism per life in E-series and D-series; fixed policy skeleton (predict exits ->
  argmax with epsilon, tabu) [IMPL e0/life.py]. Evolution only across lifetimes in E0 (GA on
  memory genome) [IMPL e0/evolve.py].
- WTP: n_org in {1,1,2,4} but only organism 0 is scored; others share marks if "shared" [IMPL
  world.py, genome.py:96]. Policy drawn from 7 fixed heuristics; rollouts are hand-coded depth
  <=4 lookahead over predicted values with 0.9 discount [IMPL world.py:440-447]. "Representation
  fluidity" = at checkpoints, try converting the memory to another substrate class fitted on the
  buffer and keep it if training MSE drops [IMPL world.py:483-497]. Learning rules: sgd, nlms,
  batch_replay, hebbian, anti_hebbian, evolve (random perturbation + accept), none [IMPL].
- WTP-02 admitted population: 684 of 1,500 worlds (46%) had n_floats = 1 (memory none or marks)
  [CLAIM WTP02 I3]. WTP-03 restricted specimens to n_floats >= 4 with a nonzero rule [INTENT
  WTP02 s8; WTP03 authorization s3].
- LM01/ARC3: no organism; arms are estimators.

## 7. World/environment architecture (toy scale flagged)

- E0: TOY. 4096 nodes, 4 exits + 10% long jump, 6-mode address, horizon 2,000 steps, one scalar
  observation per step, regrowth 500, energy 30 + 3 per harvest [IMPL e0/life.py ECON_DEFAULT].
- E1/E2/D: TOY. 4096 cells (8^4), 1,200 events, held-out (A,C) pairs (16 of 64), lock tolerance
  tasks, 17-hypothesis families TT/MAT/CP/NONE [IMPL].
- WTP-01/02: TOY. Fields 64-4096 cells; graphs 64-1024 nodes; lifetimes 200-600 (v1) and
  1,000-3,000 (v2); observations <=64 values per step [IMPL]. Median v2 organism lived 25% of its
  lifetime; 10.7% alive at end [CLAIM WTP02 I5].
- WTP-03: TOY. Same grammar plus graded prediction market, query market, information price kappa,
  energy buffer, replay consolidation, clean-channel stratum [CLAIM STATUS Q3]. 0 spectral,
  sparse or random generators among 181 admitted worlds [CLAIM WTP03 s1].
- LM01: TOY. 512 / 1,728 / 4,096-cell fields; life_mult 4; noise .1 [IMPL PREREG s2].
- ARC3 suff: TOY. Binary processes T = 4,000-16,000 symbols; key-value streams T = 20,000 [CLAIM].
- LM02: 12^3 fields, 11 regimes x 8 worlds = 88 [CLAIM RESULTS_LM02].
- What the world demands: in every generation, predicting a scalar at an unseen discrete
  coordinate from samples of a smooth/low-rank field, sometimes after drift or episode switches
  [CODE-INFERRED]. No world requires multi-step plans, variable binding, symbolic composition,
  or hidden-state tracking except ARC3 suff binary processes (Even process requires a 1-bit
  causal state) [IMPL suff/worlds.py].

## 8. Search/training/adaptation mechanism

- In-life learning: NLMS/SGD on TT cores (E0); proximal ridge ALS consolidation (E1+); WTP rules
  listed in s6 [IMPL]. E0 F3: online TT ~10x less sample-efficient than batch ALS (R^2 .997 from
  800 samples needs ~1,600 stored floats, above every gated cap) [CLAIM].
- Across-life search: GA on TT genome (E0; drove ranks to 1-2) [CLAIM E0 F1]; random search over
  order/constants per cap (E1/E1.5; hit/miss by cap produced a fake "transition") [CLAIM E1P5 S2];
  successive-halving structure discovery (E2; worse than a no-fit MI heuristic) [CLAIM E2 s4].
- World-genome search (WTP): random, grammar-biased, novelty, local/large mutation,
  recombination; admission gates; lineage cap 15 in WTP-03 [IMPL genome.py, campaign3.py].
  Collapse modes: mutants of a few founders dominate (WTP-02 1,313/1,500 mutants, 187 lineages;
  WTP-03 174/181 mutants of 13 founders) [CLAIM]; "weird physics generally destroys learnability"
  (3 of 181 admitted were "wild") [CLAIM WTP03 s4].
- Bottleneck named by the seat: learning time / lifetime ratio; bounded in-life learners rarely
  out-earn trivial behaviour (44 of 181 admitted) [CLAIM WTP03 s4].

## 9. Measurement/ruler stack -- and the WTP constant-predictor history (operator emphasis)

E-series rulers [IMPL e0/score.py, e1/score.py]: harvest, R^2 on unvisited cells (mean-referenced:
a constant at the field mean scores R^2 = 0 by construction), EFF = (U - U_NOMEM)/persistent params,
lock success, transplant after undisclosed relabeling. NOMEM (E0) predicts 0 [IMPL
e0/memories.py:68-70]. A constant was therefore implicitly controlled in the E-series: R^2 is
relative to the mean, and EFF subtracts the memoryless agent. Observed: NOMEM harvest 3,759 beat LRU
3,030 at C=168 [CLAIM E0 F5]; E1 NOMEM L2 success .25 = chance floor [CLAIM E1 s6].

WTP generation by generation:

WTP-01 (2026-09-24, prereg c5d31985f/34a75ac19, engine 93998df6f, result 092577f21; 04:18 -> 04:43
local per commit times).
- Predictor/organism: one memory substrate (10 classes, 16-1024 floats) + fixed policy, in random
  world genomes [IMPL].
- Ruler: CG = NLMSE_end - NLMSE_birth on a 128-cell random battery, NLMSE = -log10(MSE/var(y_battery))
  with y taken from the CURRENT field [IMPL wtp/world.py:215-217, 504-514]; detectors A1 (CG
  robust z > 4 within substrate class), A2 jump, A3 (CG > .3 with <= 16 floats), A4 anti-learning,
  A5 reachability, A6 utility/competence split [IMPL wtp/detect.py:39-55]. Battery includes visited
  cells (memorisation counts) [IMPL].
- How a constant scored: a predictor at the battery mean gets NLMSE = 0 exactly; zero predictor
  slightly below 0; CG is measured against the organism's OWN birth memory, so a randomly
  initialised parametric memory that merely shrinks toward any constant earns positive CG [IMPL;
  CODE-INFERRED for the shrink case]. A3 explicitly rewards tiny memories [IMPL]. The report's
  S4 count "26 valid worlds (1.1%) beat the trivial mean predictor by > 0.1 decades" is effectively
  NLMSE_end > .1 against the battery mean [CLAIM; CODE-INFERRED mapping].
- What failed: top-3 replicated "competence" anomalies (CG ~20) were worlds whose field variance
  went to exactly 0 after catastrophes (binary dims), dividing by ~0 [CLAIM WTP01 S1; ledger
  2026-09-24]. Best genuine competence was a 508-float table in a 72-cell world [CLAIM S4].
  Memoryless organisms won energy in generous economies (A6) [CLAIM S3]. The constant was NOT the
  WTP-01 failure; the denominator and memorisation were.
- After: R1 METRIC "against a FIXED reference ... and against the mean predictor, never against
  the organism's own birth memory" [INTENT WTP01 report s4].

WTP-02 (2026-09-24, prereg d7db1854b 04:53, engine 08fa0c8d3 05:05, A6 05:10, A7 05:19, result +
A8 42c190ae3 05:52).
- Predictor/organism: as WTP-01, in necessity-gated worlds (N1 memory <= .25 x cells, N2 no-learning
  loses, N3 planted panel learns, N4 shuffled fails, N5 noncollapsed) [IMPL PREREG_WTP02 s2].
- Ruler: V0 fixed at birth; AC = -log10(MSE/V0) clipped [-3,6]; CG = AC(org) - AC(ZERO predictor);
  CGu on unseen battery cells [IMPL world2.py:11, 35-37, 256-262; PREREG_WTP02.md:18]. Detectors
  D1 CGu >= .10, D3 CGu per float top 1%, etc.; four twins (real, shuffled, frozen, random) [IMPL].
- How a constant scored: the zero reference let ANY learned DC offset score as competence. The
  fields are globally zero-mean, but unseen cells are the cells NOT visited and, in smooth fields,
  their mean correlates with the visited region; the 1-float organisms learned the mean of a
  TRANSFORMED observation (v_fft_abs -> v_tanh, a positive quantity) [CLAIM WTP02 s3; IMPL for the
  transform path]. Specimen #10 (world 0e3e9ca1cb88f30c, memory "marks", 1 float): organism CGu
  .088, its own learned constant frozen .166, true mean .000 (medians over 5 seeds) [RESULT-
  UNVERIFIED runs/wtp02/kill_const.json]. 8 of 8 Wave A positives SCALAR-EXPLAINED; 6 of 8 are
  one-float running means, 5 from one founder lineage [RESULT-UNVERIFIED].
- The chain amplified it: D3 divides by n_floats (a one-float learner maximises it); ablate-half,
  freeze and reskin are no-ops on a parameterless memory; reskin cannot change a constant; a fresh
  one-float frozen organism scores 0.000 so every "transfer gain" equals the constant's own score
  [CLAIM WTP02 I2, I4]. Mechanical verdict EXPAND (full chain: replicated 5/5 vs null 0/5, 9
  causal dials, carrier, transferred) [RESULT-UNVERIFIED runs/wtp02/summary.json].
- When discovered: by the seat, post-data, in the same session and commit as the mechanical
  verdict (A8 declared POST-DATA in PREREG_WTP02, kill_const.py, 42c190ae3, 2026-09-24 05:52 -04:00)
  [IMPL]. Pre-data validation V1-V4 had ALL_PASS without any constant predictor in it [CLAIM
  ledger 2026-09-24]. The operator ruled the same day (2affe20aa, 16:15): "FROZEN SCORER: EXPAND;
  OPERATOR SCIENTIFIC RULING: PARK/REDESIGN" and "treats the discrepancy as the result" [IMPL
  WTP02_OPERATOR_RULING.md].
- After: WTP-03 authorization s2-s4 "Do not call something competence because it beats zero"; null
  ladder N0 zero, N1 optimal constant, N2 marginals, N3 tiny linear, N4 tiny lookup, N5 best simple
  substrate; XC vs the best cheap null; "one-number systems are controls"; "if preserving the mean
  preserves the task, reject the world" [IMPL verbatim authorization lines 59-125]. Calibration
  ledger: "every validation suite includes the trivial learner (constant/mean) as a planted
  negative for every detector" [IMPL LEDGER.md].

WTP-03 (2026-09-24/25, prereg+engine bcba874b9 18:12, result a65d27ced 05:07).
- Predictor: specimen substrates (n_floats >= 4) fit to a shared stream; ruler XC vs max(N0..N5)
  [IMPL collider.py:172-201]. N1 = mean of stream values and mean of recent values [IMPL].
- How a constant scored: V3 validation "the constant has XC <= 0 on the WTP-02 #10 world"; every
  promoted specimen beats all of N0-N5 [CLAIM WTP03 s2]. The constant was dead in the instrument
  [CLAIM journal 2026-09-25].
- New hole: the missing same-class tuned batch rung. Post-data N6 (n6_check.py: low-rank ALS on
  every unfolding and CP-ALS, ranks 1-4, ridge .01/.1/1, 20 iterations) beat all 9 promoted
  specimens by .22-2.28 AC [RESULT-UNVERIFIED runs/wtp03/n6_check.json]. TRANSFERS was
  near-tautological (same field) [CLAIM W1]; admission G5 pre-selected completion [CLAIM W2].
- After: WTP-04 proposal requires beating N6 or cross-field transfer [INTENT STATUS]; never built.

LM01 (frozen, never run): N1 constant floor computed per world (campaign.py:80-81) and used in gate G1
(CI.lo(L-R - N1) > .30) and in R1 "every bounded rung above the N1 floor" [IMPL analysis.py:10-11,
96-115]. A headline positive control at noise SD 1.0 was DEGENERATE because bounded rungs sat below
N1; rerun at SD .3 [CLAIM PREREG s12]. LM02: CHEAP = (CONST, TABLE, MARGINAL), anomaly margin .10 AC
[IMPL lm02/assay.py:33-34]. Operator 2026-09-30 made "cheap competitors first, always" standing seat
doctrine [IMPL RESPONSIBILITIES s2].

Other ruler machinery: shuffled-latent twins, reskin, exact marginal-preserving surrogate,
support-checked interventions (assert the intervention changed state, else NOT_APPLICABLE), cheat
fixtures (smuggler dict refused; injected TT; LRCache/LRSubsample flagged), deterministic replay
digests (35/35 in WTP-01), lineage-clustered reporting (A7), known-answer tests for frozen analysis
[IMPL / CLAIM]. Blind spots that remain: REPLICATED not gated on replay (DEF-ENS-002); ruler
measures field prediction, never policy quality or planning; per-world rates behind admission
gates are conditional, not base rates (seat's own ledger) [CLAIM].

## 10. Baselines and controls

- E0: RANDOM, NOMEM, LRU, HASH, KNN, ADDITIVE, RF, LOWRANK, DICT_UNCAP, TT variants (TUNED,
  EVOLVED, PLANTED, SVD_INJECT), ORACLE; negative WORLD R; positive planted TT; cheat smuggler +
  inject [IMPL e0/arms.py:17]. E1: + CP, MLP, TT_OBS, TT_LATENT; kill rule "any non-TT within 10% at
  matched memory and compute -> B" [IMPL PREREG_E1; CLAIM verdict]. E2: BLIND1, RANDPERM, MI,
  GREEDY, EXHAUSTIVE, LRSEL, OUTER, ORACLE_H [CLAIM E2 verdict].
- D: shuffled control, planted coupling control, synthetic additive/coupled grids [CLAIM].
- WTP-01: shuffled-latent twin, world-family variants (frozen world, no marks, reversibility,...)
  [IMPL]. WTP-02: shuffled / frozen / random-walker twins; constant added POST-DATA [IMPL].
  WTP-03: N0-N5 ladder, exact marginal surrogate, reskin, carrier ablation, planted additive
  negative, planted completion positive, N6 POST-DATA [IMPL].
- LM01: N1, L-K kernel, E6 positive control, cheat fixtures, SUFFSTAT identity, launch-gate
  negative controls from real messages [IMPL].
- ARC3 suff: exact Bayes oracles (the strongest baseline in the seat's history) [IMPL].
- Strong-baseline lesson repeated three times: the matched-class batch estimator (LOWRANK in E1,
  N6 in WTP-03, tuned ALS throughout) beat the bounded online organism.

## 11. Historical experiment campaigns

E0 "CHOO CHOO" (2026-09-23; 20a4bab5c, 60b8cb1d1, 33055de3d, 8fe17208b).
Q: does bounded TT memory beat strong baselines in a compressible world? Organism: TT/NLMS + GA.
World: 4^6 TT field graph, C vs R vs mixtures. Pressure: energy, compute kappa, caps 96-4096.
Measurement: harvest, R^2 unvisited, H1-H3. Arms ~15. Scale 15,760 lives. Reported: INDETERMINATE
(positive control R^2 .007 < .5); seat reading B; LOWRANK beat TT at C=168; evolved gain generic
(cross-class) [RESULT-UNVERIFIED E0_VERDICT]. Reinterpretation: frozen permanently by operator as a
"useful negative" (E1 authorization R1). Label: INCONCLUSIVE (positive-control failure).

E1 "KNIFE FIGHT" (2026-09-23; ee14dfc96 -> 27e1f1715). Q: TT more competence per parameter under
severe pressure? 4-mode 8^4 TT world with held-out pairs, locks, charged ALS consolidation. Arms TT
x3, LOWRANK, CP, MLP, LRU, KNN, NOMEM, ORACLE. 10,081 lives. Reported: INDETERMINATE (PC fail);
governing gate G fails vs rank-1 LOWRANK at 128/192; strong post-hoc signal at 384; transplant
fails for all [RESULT-UNVERIFIED]. Later: E1.5 marked the 384 reading and F7 SUPERSEDED (2caf43ff3)
[CORRECTION]. Label: LATER OVERTURNED (the 384 reading) / INCONCLUSIVE (verdict).

E1.5 "COMPRESSION HEADROOM ASSAY" (2026-09-23; 58b704744 -> 6538058db, 984804b44). Q: is there a
headroom phase transition? 12,960 lives, caps 128-512, sets A/B. Reported: frozen scorer CLOSE (B);
TT_TUNED EFF 8.63/8.60 vs LOWRANK 2.03/1.76 at 192; "transition" = where random order search
succeeded [RESULT-UNVERIFIED]. Operator human-rule verdict INTRIGUING on the pairwise reading of C2
[IMPL ruling verbatim]. Seat: tautological in a TT world. Label: MIXED.

E2 "STRUCTURE DISCOVERY" (2026-09-23; efbf950af -> 553a05d2e). Q: can an organism discover how its
world factorises? 4 families x 10 arms x 60 instances x 2 seeds = 4,800 lives. Reported:
INDETERMINATE (chance-band control 0.092 vs [.034,.084]); G_ID TT .20/.15, MAT .52/.43, CP .27/.38,
NONE .93/.98; TEXTBOOK qualifier (SD beats no simple search) [RESULT-UNVERIFIED]. Post-verdict
blind_sim.py shows the band excess was chance [CLAIM]. Label: REPORTED NEGATIVE/NULL (INDETERMINATE
by rule).

D-series Rounds 1-4 (2026-09-24; 18e7e0389 -> 818882180). Q: are competence dials coupled / phased?
~19,300 lives. Reported: one replicated coupling (scratch x correct start, F 11.39, p 3.9e-5, Round 4
fresh seeds); no phases; no precursors; most couplings artifacts [RESULT-UNVERIFIED
DIALS_SYNTHESIS]. Label: MIXED (mostly null, one amplifier).

WTP-01 (2026-09-24; 092577f21). 3,000 genomes (2,370 valid), 6,000 Wave A runs + B-E; 35 fossils.
Mechanical verdict SEARCH SPACE MOSTLY DEGENERATE -- REDESIGN; 18 "REPLICATED" anomalies, all
diagnosed artifact/mechanical [RESULT-UNVERIFIED]. Label: INSTRUMENT FAILURE (top anomalies were a
metric artifact; the frozen REDESIGN verdict itself stands).

WTP-02 (2026-09-24; 42c190ae3). 24,000 candidates -> 1,500 admitted (187 lineages), 6,000 Wave A
lives, Waves B-F, fossil lane 48 lives. Mechanical EXPAND on a one-float running mean; A8 constant
kill -> SCALAR-EXPLAINED 8/8; operator PARK/REDESIGN [RESULT-UNVERIFIED; IMPL ruling]. Label: LATER
OVERTURNED (mechanical EXPAND) -- the overturn was same-day and self-administered.

WTP-03 (2026-09-24/25; bcba874b9 -> a65d27ced). 38,000 candidates, 181 admitted, 13 lineages; Waves
A-G. Mechanical CANDIDATE PHYSICS FOUND -- DEEPEN (9 flags, 4 lineages); seat adjudication KNOWN
PHYSICS (completion), N6 beats all 9; crossovers 0/12 replicated; conversion 0/21 [RESULT-UNVERIFIED].
Label: LATER OVERTURNED (DEEPEN read as discovery) / REPORTED NEGATIVE for "beyond known physics".

WTP-LM01 (2026-09-25..28; frozen 768ea8ce9 then ee8cbe0c8). 1,968 worlds planned, 0 campaign rows.
Dev sweeps: arm selection (75 strata x 16 seeds), 1,200-world margin sweep (29/75 strata TESTABLE),
headline replicate sweep 1,200 worlds, F5 288 worlds [CLAIM commits 1279cb217, 8d4ca5017,
b9f97ac6c, 088d04532]. Defects D1-D12 found pre-data; adversarial review (subagent, 15 findings)
[CLAIM]. Label: UNKNOWN (never run; HOLD by operator 2026-09-30).

ARC3 PKG-S1 sufficiency pilot (2026-09-28; bef057f44, 1366cced3). Answer-keyed; 16 seeds; findings
C1-C4 (locus irrelevant when statistic right; extra distinctions cost only via estimation; Even
process interior window optimum; key-value needs exact history, recency > random at matched
capacity) replicated by an independent stdlib implementation via Fabric tsk-ba120344aa29
[RESULT-UNVERIFIED suff/replication/README.md]. Label: REPORTED POSITIVE (dev, pilot).

ARC3 T25 CSSR (2026-09-29; 482f74a9b ... 63eda4d90). CSSR split collapses to the window floor on
the Even process (.0341 excess, 7 states); vote fixes Even but breaks order-3; CSSR->EM->mixture and
3-expert fixed-share; held-out random unifilar machines: H1/H2 refuted at T=4000; T=16000 via Fabric:
G1-G3 survive, G4 refuted [RESULT-UNVERIFIED suff/CSSR_T25.md; WORK_STATE]. Label: MIXED.

ARC3 crypticity (2026-09-29; e0a67493c ... 193880196). Learned window-crypticity is failure-silent
toward "window sufficient" with a weak learner; gate catches only catastrophic failures (K1
refuted) [RESULT-UNVERIFIED CRYPT_LEARNED.md]. Label: REPORTED NEGATIVE/NULL (instrument
limitation).

ARC3 PKG-F probes v1-v9b, W-DRIFT, W-MULTI, soft gate, observability gate (2026-09-28..30; 3840fe462
... fe6393297). Notable self-corrections: v3 "regime discovery" was a substrate retention-recency
artifact (v4); v6 "retention pays" withdrawn because F3 never_seen cells are 87-89% earlier-episode
cells (LM01 ERRATA E-4); N5 decaying-noise world made the v5 detector fire 8/8 falsely; final strict
gate leak 3e-4 vs .30/.70 but behaves as a recent window [RESULT-UNVERIFIED RESULTS_PKGF_PROBE.md].
Label: MIXED (instrument repaired; several interim readings overturned).

ARC3 LM02 window assay (2026-09-30; 8b49a4456 prereg, bf90a73bb result). 88 worlds. WINDOW_NOT_SUPPORTED;
PKG-F-HIER POP_VALUE_REQUIRES_REPRESENTATIVENESS (HIDDEN .124 > .10); L4 refuted [RESULT-UNVERIFIED
RESULTS_LM02_ASSAY.md]. First launch crashed on a pickling error before rows [CLAIM]. Label:
REPORTED NEGATIVE/NULL.

FP-001 (2026-09-29, MWO-0003): cross-platform reproducibility probe of the LM01 fixture; M2 byte-exact,
Linux replicas differ by <= 4e-15 relative [RESULT-UNVERIFIED probes/FP-001_RESULT.json; ERRATA E-2].
Label: REPORTED POSITIVE (instrument).

## 12. Reported results and later corrections (timelines)

1. E1 "384 signal" (over-parameterised TT learns, exact capacity does not) -> E1.5 S1/S2 shows exact
   capacity (192) learns with latent order and 10-20 sweeps; the 384 effect was inherited constants
   + order-search luck -> E1 text annotated SUPERSEDED (2caf43ff3), originals kept [CORRECTION].
   Status: overturned.
2. E1.5 frozen CLOSE vs operator INTRIGUING -> operator ruling 984804b44 reads C2 pairwise; both
   recorded; seat and operator agree no phase transition [IMPL]. Status: split record.
3. E2 INDETERMINATE by chance-band control -> blind_sim.py (1,200 fresh seeds, 0.060 vs .0588) says
   chance [CLAIM]. Status: verdict unchanged, substance negative.
4. WTP-01 top competence anomalies (CG ~20, replicated 3-4/5, shuffled 0-2/5) -> autopsy: field
   variance exactly 0 at end of life -> ARTIFACT; frozen verdict unchanged [CORRECTION WTP01 S1].
5. WTP-02 mechanical EXPAND -> A8 constant kill (same commit) -> operator PARK/REDESIGN [CORRECTION].
6. WTP-03 mechanical DEEPEN -> seat s12 adjudication + post-data N6 -> known completion physics,
   "positive control" [CORRECTION]. Operator never explicitly ruled on Q1 "accept the adjudication?"
   in STATUS before LM01 superseded it [UNKNOWN; STATUS Open questions].
7. LM01 v0.3 -> v0.3.1 (D12 fix) -> v0.3.2 (operator amendment; review R1-R4) before any row; ERRATA
   E-1 corrects the v0.3.1 packet's "both eviction rules lose to random" (residual_reservoir beats
   random after the one-ALS-convergence rule #677) [CORRECTION lm01/ERRATA.md]. Atlas
   ATLAS_BURIED_SIGNALS D4 still cites the superseded "both lose" claim [CORRECTION of Atlas].
8. PKG-F v3 -> v4, v6 -> v6 control -> v7, v5 -> N5 -> v8 -> v9b chains as in s11 [CORRECTION].
9. Seat predictions scored as losses in calibration/LEDGER.md (22 rows, unflattering by design),
   e.g. WTP-02 fraction hit "for the wrong reason" recorded as a LOSS [IMPL].

## 13. False-positive archaeology

- Variance-collapse denominator (WTP-01 S1): normalising by a quantity the environment can drive to
  0 produced the campaign's top flag; replication and shuffled controls did not catch it because
  the artifact is world-structure dependent (binary dims + catastrophes) [CLAIM].
- Memorisation counted as competence (WTP-01 S4): battery included seen cells and memory could
  exceed world size [CLAIM].
- Free economy (WTP-01 S3 "rich without knowing", A6): random walkers top-5% energy [CLAIM].
- Zero reference + scalar learner (WTP-02): the canonical constant-predictor false positive;
  passed replication, structure dependence (shuffle breaks the unseen-cell/visited-region
  correlation), causal dials, carrier and transfer because each gate was invariant for a constant
  [CLAIM]. Seat lesson: "a chain of five gates passing is not independent evidence when every
  gate reads the same scalar" [IMPL journal 2026-09-24].
- Running-mean convergence read as a "jump" (WTP-02 Wave F #9; WTP-01 D2) [CLAIM].
- Admission manufactures the phenomenon (WTP-03 G5) and same-field transfer tautology (W1) [CLAIM].
- Order-search luck read as a capacity phase transition (E1.5) [CLAIM].
- Accounting couplings (price x compute inside EFF) read as dial couplings (D-series) [CLAIM].
- Recency prior read as regime discovery (PKG-F v3/v4); exact recall read as generalization (PKG-F
  v6) [CLAIM].
- Chance fluctuation failing a 2-SE band (E2 CHT) -- a false NEGATIVE control alarm [CLAIM].
- E0 rank-1 TTs harvesting 2x NOMEM with R^2 ~0 (coarse ranking) [CLAIM].

## 14. Likely false-negative regimes

- Online learning under caps that forbid the good (batch) algorithm: E0 F3 states ALS needs ~1,600
  floats, above every gated cap; organisms were left with SGD [CLAIM]. Any negative about "bounded
  TT organisms" is partly a negative about NLMS in 2,000 steps.
- Positive-control coupling to tuned arms (E1 F9) produced INDETERMINATE rather than an answer [CLAIM].
- Economy calibrated on the oracle starved real learners (WTP-02 I5: median life 25%); detectors
  read 5-point traces [CLAIM]. Learning-time/lifetime ratio decides inhabitability (WTP-03 s4) --
  most WTP worlds were never long enough for any substrate to learn [CLAIM].
- Fixed hand-coded policies: no world-genome organism could learn to act, plan or communicate; any
  phenomenon requiring policy learning was unreachable by construction [CODE-INFERRED].
- Lineage concentration (13 founders) and mutation dominance shrank effective sample [CLAIM].
- WTP-03 G5 admission excluded spectral/sparse/random worlds entirely (0 admitted) [CLAIM].
- E2 discovery budget (512-sample buffer, correct-model R^2 .44-.90) bounded identification [CLAIM].
- D-series Round 4 at 16 lives/cell was underpowered for EFF; its EFF nulls "are not evidence"
  [CLAIM].
- LM01 never run; F-B (strict lossless falsifier) had ~0 power in most strata (#730; Atlas) [CLAIM].
- Power-limited per-cell drift detection: the PKG-F strict gate quarantines low-n cells and thus
  forfeits +.60 AC in stationary worlds (C1 price) [CLAIM].

## 15. Phase 3 audit, per engine

E-ENGINE (E0-E2).
a. Representation richness: hierarchy NO (flat TT chain); compositional structure PARTIAL (TT is a
   product of per-mode factors; no composition of learned parts); variable binding NO; memory
   PARTIAL (parametric cap-bounded memory; no episodic store except E1 buffer); recurrence NO;
   counterfactual state NO; latent variables PARTIAL (TT bond indices); temporal abstraction NO;
   spatial abstraction PARTIAL (mode factors); reusable substructure PARTIAL (shared cores across
   cells); dynamic routing NO; self-reference NO [IMPL e0/tt.py, e1/mem.py].
b. Reasoning opportunity: interpolation/completion of a low-rank field plus local greedy choice;
   E1 locks and delayed fibers add mild delayed relevance. Does not demand more than
   interpolation and lookup [CODE-INFERRED].
c. Shortcut surface: coarse ranking (E0), rank-1 matrix unfolding (E1), generator-matched
   inductive bias (E1.5 tautology), random order search luck [CLAIM].
d. Ruler resolving power: good for "is there field structure in memory" (R^2 unvisited, WORLD R,
   cheat fixtures pass); weak for "was the representation discovered" (order came from search)
   [CLAIM].
e. Scale: 4,096 cells; D=4-6 modes; horizon 1,200-2,000 events; memory 96-4,096 floats; 1
   organism; worlds = instances of one class family; ~4.8k-16k lives per campaign; CPU minutes-hours.

D-ENGINE.
a. Same as E-engine plus replay/error stores (memory PARTIAL), restructuring (dynamic routing NO).
b. Same; dials modulate learning, not task demand.
c. Accounting/definitional/floor-compression couplings [CLAIM].
d. ANOVA with planted controls: resolves additive vs coupled; underpowered at 16 lives/cell.
e. ~19,300 lives; 11 nominations in Round 4.

WTP v1 (WTP-01).
a. hierarchy NO; compositional PARTIAL (field op chains at build; substrate mixtures); variable
   binding NO; memory PARTIAL (substrates 16-1024 floats, external marks); recurrence NO;
   counterfactual state PARTIAL (rollout lookahead over own predictions, depth <= 4); latent
   variables PARTIAL (factor substrates); temporal abstraction NO; spatial abstraction PARTIAL
   (graph geometry, but policy fixed); reusable substructure PARTIAL; dynamic routing NO;
   self-reference NO (conversion between substrates is a fit-and-compare, not self-modelling)
   [IMPL wtp/organism.py, world.py].
b. Demands predicting a scalar field and greedy foraging; no world demands more than
   interpolation, lookup, running averages and fixed heuristics [CODE-INFERRED]. Many worlds
   demand less (free economies).
c. Shortcut surface: variance collapse, memorisation (memory >= world), free economy,
   anti-learning artifacts, small-memory bias (A3) [CLAIM].
d. Ruler resolving power: LOW (top anomalies were artifacts; shuffled twin insufficient) [CLAIM].
e. Scale: 64-4,096 cells, 2-11 modes, 64-1,024 nodes, lifetime 200-600, n_org <= 4, 3,000 genomes,
   ~30 min single host.

WTP v2 (WTP-02).
a. Same as WTP v1.
b. Same as WTP v1, with necessity gates rejecting free economies and memorisation.
c. Shortcut surface: learned constant vs zero reference; per-float ratio; no-op interventions on
   parameterless memories; running-mean convergence as "jump"; lineage concentration [CLAIM].
d. Ruler resolving power: LOW for the claimed phenomenon (promoted a scalar to EXPAND); HIGH as a
   falsification machine once A8 was added [CLAIM].
e. Scale: 24,000 candidates, 1,500 admitted, 6,000 Wave A lives, lifetime 1,000-3,000, ~1 h on
   20 workers.

WTP v3 (WTP-03 collider).
a. As WTP v1 for substrates; organism agency removed (fixed carrier stream) so memory is the only
   axis [IMPL]. Recombination test set probes PARTIAL compositional generalisation (unseen pairs
   of seen coordinate values) [IMPL collider.py].
b. Demands completion of unseen cells and unseen pair blocks; does not demand more than
   interpolation/factorisation [CODE-INFERRED].
c. Shortcut surface: same-class batch estimator unmeasured until N6; same-field transfer;
   admission pre-selecting completion [CLAIM].
d. Ruler resolving power: MEDIUM-HIGH vs cheap nulls (constant, marginal, linear, lookup, simple
   substrate, exact marginal surrogate) [CLAIM V1-V7]; LOW for "beyond known physics" without N6
   and cross-field transfer [CLAIM].
e. Scale: 38,000 candidates, 181 admitted, 13 founder lineages, 12 budget sweeps x 7 levels x 4
   seeds, ~11 h on 20 workers.

LM01 HARNESS.
a. Memory YES as the explicit axis (exact store, reservoir, bounded state, three compression loci);
   latent variables PARTIAL (rank-3 factors); everything else NO [IMPL].
b. Completion, episode switching (F3), fresh-field transfer (F4), nuisance OOD (F5): more than
   interpolation only in F3/F4/F5's distribution-shift sense [CODE-INFERRED].
c. Shortcut surface: F3 never_seen is mostly stale recall (ERRATA E-4); SUFFSTAT identity makes
   L-R equivalent to a per-cell (sum,count) table; kernel readouts [CLAIM].
d. Ruler resolving power: per-stratum paired CIs at DELTA .30; only ~29/75 strata TESTABLE; F-B
   ~0 power in most strata [CLAIM]. Never exercised on campaign data.
e. Scale: 75 strata, 1,968 worlds planned, 512-4,096 cells.

ARC3 DEV INSTRUMENTS (suff, PKG-F, LM02).
a. suff: memory YES (counts, windows, verbatim logs); latent variables YES in CSSR/HMM (discovered
   causal states); recurrence PARTIAL (state machine updates); temporal abstraction PARTIAL
   (context length); others NO [IMPL]. PKG-F/LM02: record selection policies only.
b. suff binary processes demand hidden-state tracking (Even process: infinite Markov order, 1-bit
   causal state) -- the only Ensorain world that demands more than interpolation [IMPL
   suff/worlds.py; CLAIM RESULTS_S1_PILOT finding 3].
c. Shortcut: window statistics approximate causal state at finite k; exact Bayes oracle removes
   most shortcut ambiguity [CLAIM].
d. Ruler resolving power: HIGH (excess log-loss vs exact Bayes) but on toy processes [CLAIM].
e. Scale: T 4,000-20,000 symbols, 16-24 seeds; LM02 88 worlds; CPU seconds-minutes.

## 16. Research reports and substantial documents

- ensorain/E0_VERDICT.md, E1_VERDICT.md, E1P5_VERDICT.md, E2_VERDICT.md -- E-series verdicts with
  failure shapes and scored predictions.
- ensorain/PREREG_E0(.._part2).md, PREREG_E1(.._part2).md, PREREG_E1P5(.._part2).md,
  PREREG_E2(.._part2).md, PREREG_D1/D2/D3.md, PREREG_WTP01/02/03.md -- preregistrations.
- ensorain/D1_ROUND1.md, D2_ROUND2.md, D3_ROUND3.md, DIALS_SYNTHESIS.md, DIALS_RETRO.md -- dial series.
- ensorain/ENSORAIN_WTP01_REPORT.md, ENSORAIN_WTP02_REPORT.md, ENSORAIN_WTP03_REPORT.md -- WTP reports.
- ensorain/WTP02_OPERATOR_RULING.md -- EXPAND frozen / PARK-REDESIGN.
- ensorain/PREREG_WTP_LM01.md (+ _TABLES), LM01_DIFF_v031_to_v032.md, LM01_PREREG_REVIEW_2026-09-26.md
  (superseded packet), lm01/STEWARD_RULINGS.md, lm01/ERRATA.md, lm01/FREEZE.json.
- ensorain/PROVENANCE.md -- external idea provenance.
- ensorain/arc3/THREADS.md (T01-T26 backlog), HIERARCHY.md, QUEUE.md, INSTRUMENT_LINE_FREEZE_2026-09-30.md,
  LM01_ADJUDICATION_ADDENDUM.md, LM01_CURVE_ANALYSIS_PLAN.md, RESULTS_PKGF_PROBE.md (7.5k words).
- ensorain/arc3/packages/PKG_F_CAUSAL_SELECTIVITY.md, PKG_LM02_DESIGN.md, PKG_S1_SUFFICIENCY_LADDER.md.
- ensorain/arc3/lm02/PREREG_LM02_ASSAY.md, RESULTS_LM02_ASSAY.md.
- ensorain/arc3/suff/RESULTS_S1_PILOT.md, CSSR_T25.md, CRYPT_LEARNED.md, replication/README.md.
- ensorain/arc3/reviews/LM01_ADVERSARIAL_REVIEW.md (subagent reviewer, 15 findings), LM01_V032_PREFREEZE_REVIEW.md,
  LM01_V032_CONFIRM.md, T25_CSSR_REVIEW_2026-09-29.md, PKGF_CRYPT_REVIEW_2026-09-29.md,
  INSTRUMENT_LINE_REVIEW_2026-09-30.md (seat-authored review packet, not independent).
- ensorain/arc3/lit/LIT_THEORY.md, LIT_MEMORY_SYSTEMS.md, LIT_FORGETTING_ABSTRACTION.md -- 45/60/55-source raids.
- roles/Ensorain/reviews/E0_review_packet.txt; prompts/*/REPORT.md (comms report bodies).

## 17. Journals/TODOs/backlogs/pivots/abandoned branches

- Journals 2026-09-23, 24, 25, 26, 28, 30 (roles/Ensorain/journal/); none for 09-27 or 09-29 [IMPL].
- BACKLOG_H0H5.md (current) and superseded BACKLOG_H0H5_2026-09-23_precharter.md (3 items) [IMPL].
- arc3/THREADS.md T01-T26; T02 notes LM01 never measures HYPOTHESIS compression [IMPL].
- Abandoned / never built: WTP-04 (two definitions: STATUS "beyond completion" with N6, cross-field
  transfer, class-agnostic admission; and 09-30 "Habitable Islands" phase-diagram program) [INTENT].
  LM01 campaign (HOLD). PKG-F full package and LM02 as a program (frozen as instruments). s12 of
  the founding directive never received.
- Branch: only ensorain/base-role-adopt-2026-09-23 (KEEP); merged through 26a490702 [IMPL STATUS;
  Atlas digest].
- Defects: DEF-ENS-001 (frozen LM01 launch gate cannot accept an MWO carrier; fails closed),
  DEF-ENS-002 (REPLICATED not gated on replay) [IMPL DEFECTS.md].
- Process hole: results/ directories are gitignored repo-wide; cited result JSONs had to be
  force-added after the fact (6c8b01c15, 3f6b90f25) [IMPL].

## 18. Dependencies on other engines and seats

- No runtime dependency on other seats' engines; ensorain imports only numpy (and its own
  packages); WTP v2/v3, LM01 and ARC3 reuse ensorain.wtp and ensorain.e0.tt [IMPL imports].
- Governance dependencies: base-role inheritance, comms, MWO/CWO, Fabric (lease and script
  executor), Ananke lease convention (~/ananke_runs/leases) [IMPL QUEUE.md, RESUME.md].
- Scientific lineage: the LM01 question comes from the Selective Irreversibility program
  (Cyclops/Aporia; frozen law text held by Harmonia) [IMPL PREREG s1]. Artemis reviews.
- Compute contention with Bellerophon's multi-day campaign on M2 (LM01 queued behind it) [IMPL].
- Atlas: no Ensorain/WTP adapter exists (ATLAS_CROSS_ENGINE_SYNTHESIS line 463) [IMPL Atlas].

## 19. Scaling limitations

- Pure-Python per-step loops over numpy (dict-based marks, per-cell table scans) [IMPL]; GPU unused.
- Field size hard-capped at 4,096 cells in WTP build (world.py build_field) [IMPL].
- Inhabitable worlds rare (~0.5% admissible; first founder after ~6,000 candidates); admission
  dominated by mutants of few founders [CLAIM].
- Learners need thousands of samples; lifetimes are hundreds to a few thousand steps [CLAIM].
- Bitwise platform-bound outputs (ERRATA E-2) [CLAIM].
- Single-organism scoring; communication and population dynamics unimplemented [IMPL].

## 20. Lens potential for Phase 3 (descriptive)

- Substrate: numpy scalar fields over small discrete grids with generator families (tt, cp,
  lowrank, pairwise, sparse, spectral, sum, random) and build-time op chains [IMPL].
- Organisms: bounded online regressors (10 substrate classes) + fixed foraging heuristics; in the
  collider, no agency.
- Worlds: foraging graphs over field cells with drift, catastrophes, rewiring, hazards; LM01 walks;
  binary stochastic processes (suff).
- Pressures: memory cap, compute price, energy, information price kappa, drift/switch, nuisance.
- Phenomenon family: compression/completion of structured fields; selective retention; regime
  detection; causal-state discovery (suff only).
- Current resolving mechanism: XC over N0-N5 + exact marginal surrogate + reskin + support-checked
  interventions (WTP-03); exact Bayes excess (suff); per-stratum paired CIs (LM01, unexercised).
- Likely resolution ceiling: distinguishing bounded online completion from batch completion; the
  ruler cannot see planning, binding or composition because worlds do not demand them.
- Noise sources: seed noise at .10 AC (0/12 crossovers replicated), lineage concentration, short
  lives, platform ULP differences.
- Architectural limit: the organism's only adaptive object is a predictor of a scalar at a cell;
  policy is fixed.
- Reusable parts: World Genome serialisation/hash/replay; named RNG streams with pre-drawn
  environment; null ladder + XC; exact marginal-preserving surrogate; no-op-guarded interventions;
  cheat fixtures; launch gate with real negative controls; answer-keyed oracle worlds; calibration
  ledger practice [IMPL].
- Toy-grade parts: every world and organism; D-series dial engine; the 34-atom registry (atoms act
  once at build).
- Unknowns: whether any non-completion phenomenon exists in the grammar (never searched with
  class-agnostic admission + N6 + cross-field transfer).

## 21. Open questions / what this crawl did not read

- Read in full: role STATUS/RESUME/RESPONSIBILITIES (+2 superseded), DEFECTS, calibration LEDGER,
  founding directive, foundry directive (s0-25 fully, rest by headings), 09-30 operator direction,
  WTP-02/03 authorizations (constant-related parts), Cyclops LM01 directive (opening), ARC3
  directive (opening), E0/E1/E1.5/E2 verdicts, DIALS_SYNTHESIS, DIALS_RETRO, WTP-01/02/03 reports,
  WTP02 ruling, PREREG_WTP02 s1-2 + A8, PREREG_WTP_LM01 s1-6, lm01/ERRATA, INSTRUMENT_LINE_FREEZE,
  HIERARCHY, QUEUE, THREADS T01-T04, RESULTS_S1_PILOT, RESULTS_LM02 head, CSSR_T25 head, journal
  2026-09-24; code e0/world.py, e0/tt.py, e0/life.py, wtp/organism.py (s1-200), wtp/world.py
  (field, graph, run_world), wtp/genome.py, wtp/detect.py, wtp2/world2.py (head, observe/learn),
  wtp2/kill_const.py, wtp3/collider.py (head, ladder), wtp3/controls.py, lm01/campaign.py
  (N1 lines), lm01 docstrings; Atlas ensorain_bellerophon digest; git log of both paths.
- NOT read: PREREG_E0/E1/E1P5/E2/D1-D3 bodies; D1/D2/D3 round reports; PREREG_WTP01/03 bodies;
  WTP-03 validate3/preflight3/campaign3 internals; wtp/registry.py op bodies; lm01 arms/analysis
  bodies beyond grep; STEWARD_RULINGS.md; LM01 adversarial and pre-freeze reviews beyond headers;
  RESULTS_PKGF_PROBE.md in full; PKG_* packages; lit raids; journals other than 09-24; LM01 dev
  sweep rows; any runs/*.json row content (no number above was recomputed); dials and LM01
  operator rulings bodies; MIGRATION_REPORT_MWO-0002.json; E0 review packet.
- Comms: no roles/*/INBOX* file mentions Ensorain (grep); comms DB messages (#590-#1132) were not
  read directly; their content is known here only via seat files and the Atlas digest.
- Zero-cost inspections: none run (no imports, no tests).
- Open questions: did the operator ever rule on WTP-03 STATUS Q1-Q4? Was the s12 remainder ever
  sent? Why WTP-02 R1 implemented the zero predictor when WTP-01 R1 asked for the mean predictor
  (no record found)? Small timing inconsistency: WTP-01 reports ~30 min wall but only ~15 min
  separate the engine commit (04:28) and the result commit (04:43) [UNKNOWN].
- Holdout/secret paths: none touched.
