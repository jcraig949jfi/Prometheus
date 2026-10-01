# Ananke -- Phase 3 intake dossier

- Seat: Ananke
- Crawler: Tantalus (worker)
- Tree: origin/main at 21a47402a (worktree F:\Prometheus-worktrees\tantalus-phase3-intake)
- Date: 2026-10-01

Summary. Ananke is a one-week-old (created 2026-09-24) ENGINE + CAMPAIGN seat on M1
(SKULLPORT) that built the Packet-Tensor Engine (PTE), a GPU-batched, all-integer,
bit-exact simulator in which N sites on a graph each run the SAME short straight-line
register program (a 16-opcode VM, up to 4 rule variants) and communicate only by
lossy, delayed, superposing packets that arrive as per-channel sums and counts
[IMPL prometheus/ananke/engine.py, physics.py]. "Packet tensor" in code means exactly
this: integer tensors S[B,N,D] (site registers), Acc_sum[B,N,C,P]/Acc_cnt[B,N,C]
(inboxes), Msum[LM,B,N,C,P]/Mcnt[LM,B,N,C] (an in-flight ring buffer indexed by
arrival slot and recipient), routing weights w[B,N,R], writable immediates Kp[B,N,L],
a rule pointer r and an optional energy E; there is no tensor algebra, no learned
weights and no gradient [IMPL]. Organisms are found by a plain GA over world genomes
(pop 96 x 36 generations, 8 training worlds per generation) on five tiny binary
tasks (RELAY, XOR, MAJ, FLIP, HOLD; 12-16 trials, readout = sign of S0 at one site)
[IMPL search.py, envs.py]. Campaigns: PTE-C1 (6596 rows, 12 h, 2026-09-24/25),
PTE-C1b (27 cells, 2026-09-26), research arcs 1-3 (workers W-A..W-Z, 2026-09-27..30:
carrier swaps, echo models, SETRULE, retention/SI01, H6 "search reachability bounds
PTE"), an inference harvest (H-*) and a saturation Wave 2 (W2-*; 2026-09-30/10-01).
The historical arc is unusually self-corrective: the C1 headline ("rare, causally
verified, reproduced, size-free, topology-bound packet transport") was progressively
eroded by the seat's own errata (C1_ERRATA E1-E3, E-H1..E-H5, E-W1..E-W23): zero_comm
is forced to exactly 0.500 by the mirror-pair design so COMM_DEPENDENT == SIGNAL;
"size-free" rests on one law that failed reproduction; "topology-bound" is hop count;
none of the 13 SUPPORTED phase boundaries is physics beyond the transport bound;
30.6% of NULLs are physics-capped by construction; the only multi-hop RELAY SIGNALs
are one-shot "flood latches" that clear SIGNAL at a ~0.58 ceiling; XOR got a
12-line in-genome parity plant (0.85) the search never found. Every reported result
below is unverified by this crawl.

## 1. Identity, charter and pivots

- Name: Ananke. Prior use of the name: a never-built May 2026 "contradiction detector"
  proposal in the Charon frontier review (dc39c30bc), recorded as not a queue
  [CLAIM roles/Ananke/journal/2026-09-24.md]. No other aliases found.
- Host: M1 (SKULLPORT), local RTX 5060 Ti; worktree Prometheus-worktrees/ananke-base-role,
  branch ananke/base-role-adopt-2026-09-24, fast-forwarded into main [CLAIM RESUME.md].
  Run state outside git under ~/ananke_runs (M1 only); committed copies of rows exist.
- Creation 2026-09-24 06:33 local (7acc2926c), operator creation posture verbatim at
  roles/Ananke/prompts/2026-09-24_creation/ ("failures as opportunity... self direct,
  delegate"). Mission 2d22d271c: roles/Ananke/prompts/2026-09-24_charter/
  01_OPERATOR_MISSION_verbatim.md (711 lines): "Can cognitive-like organization emerge
  from asynchronous, lossy packet traffic propagating through a mutable tensor
  substrate, without importing conventional neural-network architecture?" ("UDP packets
  broadcast over a tensor"), forbids transformers/backprop/MLP/RNN/GNN/reservoir/CA/
  MARL/ALife templates as substrate, demands GPU-native from the start, phase
  transitions not scores, preregistration, transplants, anti-gravity constraint
  [INTENT].
- Charter 0e89f7104 (RESPONSIBILITIES.md s0): build/run PTE and map "an empirical phase
  diagram over communication physics"; label vocabulary capped at NULL, SIGNAL,
  REPRODUCED_SIGNAL, CAUSAL_SUPPORT, TRANSFER_SUPPORT, PHASE_BOUNDARY_CANDIDATE/SUPPORTED,
  INCONCLUSIVE [INTENT].
- Pivot timeline (from git log -- roles/Ananke prometheus/ananke, 174 commits):
  - 09-24 06:33-08:05 local: seat, mission, DESIGN, engine+oracle, envs/search,
    campaign, PREREG (78243a758), FREEZE (362f2189b), launch -- the whole engine was
    written and frozen in about 90 minutes [IMPL commit times].
  - 09-25: C1 done; operator HOLD ALL ACTIVITY pending Kairos/Elenchus review (never
    arrived) [CLAIM RESUME.md, programs/selective_irreversibility/RULINGS.md]. Steward
    directive PTE-SI01 (Aporia M1, Cyclops M2; Selective-Irreversibility program)
    puts Ananke under steward coordination [INTENT prompts/2026-09-25_pte_si01_directive/].
  - 09-26: operator "C1B HOLD RELEASE: direct operator control restored" -- stewards
    demoted to advisory [INTENT prompts/2026-09-26_c1b_operator_release/]; C1b run.
  - 09-27..28: research arcs 1-3 with parallel workers W-A..W-L; ARC3 synthesis
    (7fc642367) asserts H6.
  - 09-28..29: MWO-0001/0002/0004 work-order regime; no new large PTE campaign; small
    CPU blocks (workers W-M..W-Z, swap-instrument arc); Fabric lease cutover (8370083ae).
  - 09-30: operator inference harvest (inference-only, 4a97f97fa) then Wave-2
    "saturation" (fd631acb2) running 30+ Opus workers until the weekly API limit
    (HTTP 429) at ~03:20Z 10-01; close e0f21332d [CLAIM harvest/wave2/
    INFERENCE_SATURATION_WAVE2_HANDOFF.md].
- Terminal state at tree: WORK_STATE.json state WORKING, MWO-0004; C2 is a DRAFT,
  not frozen, not authorized (harvest/wave2/W2-AB/PREREG_PTE_C2_DRAFT.md) [CLAIM].
- Relationships: Ensorain (overlap: "tensor physics of intelligence" Foundry; note
  prompts/2026-09-24_ensorain_overlap/; operator question Q1 on merging, RESUME s5);
  Aether (reused RunPod/oracle discipline; W-C content-vs-timing comparison); Aporia/
  Cyclops (SI01 stewards, later advisory); Kairos/Elenchus (review requested, never
  replied); Cosmos (C4 R-STAT review, blocked); Atlas (locator; digest
  roles/Atlas/inference_harvest_2026-09-30/workers/digests/ananke_pte_tyche.md);
  Harmonia (#1045 corrections cited by 017259a48); Nestor (#1207 latency cited).

## 2. Engine/system inventory

E1. PTE substrate (PTE-SUB-1 / PTE-OPS-1)
- Paths: prometheus/ananke/engine.py (594 lines), physics.py (148), rng.py (62),
  topology.py (73); spec roles/Ananke/pte/DESIGN.md (320 lines, normative).
- Purpose: batched integer packet world. Entry: World(ph, genomes[B,G,L,5],
  world_seeds, ctrl, schedule).run(T) (CUDA graph capture of one tick) or .step().
- State (all int32/int64 torch tensors): S[B,N,D], E[B,N], r[B,N], w[B,N,R],
  Kp[B,N,L], Acc_sum[B,N,C,P], Acc_cnt[B,N,C], Msum[LM,B,N,C,P], Mcnt[LM,B,N,C]
  [IMPL engine.py:120-140]. Randomness: counter hash H(ws,stream,t,n,j), 11 named
  streams, never reads state [IMPL rng.py].
- Tick order: delivery (+aloha/saturate caps) -> environment SENSE -> wake (sync
  period / async Bernoulli) -> run program L instructions sequentially (vectorised
  over B,N via torch.gather/stack of 16 candidate results) -> economy -> routing
  write -> emission (fanout copies, loss, latency, noise, dup, into ring slot
  t+delay) -> local mutation of Kp -> ablation hooks -> decay S -= S>>k -> readout
  trace of S0 at read sites [IMPL engine.py:_tick].
- Scale: CPU and CUDA; throughput 11-21M site-updates/s on RTX 5060 Ti, launch-bound
  (no Triton on Windows) [CLAIM journal 2026-09-24; C1_REPORT F7]. Mailbox int32
  headroom assert limits n_sites*fanout [IMPL physics.py validate].
- Persistence: checkpoint()/restore() dicts; per-world sha256 digests [IMPL].
E2. Independent CPU oracle
- prometheus/ananke/oracle.py (511 lines), "written ONLY from DESIGN.md without reading
  the engine" by a subagent; 19 ambiguities A1-A19 ruled normative (DESIGN s9); one
  real divergence (SENSE saturation) fixed pre-conformance [CLAIM journal; IMPL docstring].
  Tests: tests/test_conformance.py (engine vs oracle digests on random small physics,
  eager == graph, checkpoint == uninterrupted) [IMPL]. Independence caveat: same LLM
  family and same spec; "independent" means a separate context, not a separate lab.
E3. Environments (5 families)
- prometheus/ananke/envs.py (238 lines). Sparse sense schedules + scoring; mirror
  pairs of worlds; positions redrawn per world from ENV stream [IMPL].
E4. Plants (hand genomes; positive controls and cheats)
- prometheus/ananke/plants.py (300 lines): relay_flood (12 lines), hold_latch (9),
  sense_copy cheat, null, C1b echo fixtures (echo_hold etc.) [IMPL]. Many more plants
  live only in research/ worker dirs (refresh relay, P-FLIP, P-XOR parity, MAJ plants).
E5. Assays and controls
- prometheus/ananke/assays.py (318): evaluate (common random numbers, mirror pairs,
  twin-contrast sens_act and sens_any shaping signals), control_battery (10 controls),
  run_controls (+ no-op digest guard, env-permutation null), twin_assay (cue negated at
  trial 2; reach/persist/beyond_hop), transplant_state [IMPL].
E6. Outer search
- prometheus/ananke/search.py (149): mutation + truncation GA over genomes; selection
  fitness = acc + 0.10*max(sens_act,0) + 0.02*sens_any; champion by training acc on
  16 fresh worlds; one held-out evaluation on 64 worlds + zero_comm control + twin
  [IMPL].
E7. Campaign driver and report
- campaign.py (932): waves A0, A, B, B2, C, D, E; DIALS (31 physics dials) and
  ENV_DIALS; classify/causal_label/anomaly_flags/detect_boundaries; Store with
  cell-level resume; PARK after 5 failures; refuses dirty/mismatched code [IMPL].
  launch.py (102): pinned detached worktree + schtasks watchdog [IMPL].
  report.py (372): evidence package + Atlas pointer export [IMPL]. analysis_a0.py (205):
  preregistered logistic/tree interaction analysis [IMPL].
E8. C1b adjudication module
- c1b.py (596), c1b_run.py (360): per-carrier reset batteries, in-flight flush,
  freeze_rule, census, exhaustive first-match label tables (2^9 M2, 2^4 M3), fixture
  plants, eligibility (A3 FIRED rule), fail-closed release guard [IMPL].
E9. Mechanism lens instruments (post-C1b)
- lens.py (297): between-tick mirror-partner carrier swaps, slot/recipient rolls,
  reset_r, cue_arrival_profile, verify_reach (REACHED/UNREACHED/NOT_VERIFIED) [IMPL].
- lens_swap.py (490): single-trial swap arms, S/C/N mixture census (promoted from
  W-M) [IMPL]. swap_rel.py (201): REL4 "H2" relative swap certificate (promoted from
  W-W after W-X) [IMPL].
- inference.py (181): t / studentized bootstrap CIs, BH/Holm, replication gate,
  reading3, kill_eligible (W2-H, W2-K; nothing frozen imports it) [IMPL].
E10. Research tooling (roles/Ananke/research/)
- deposit.py (verbatim worker-report deposition with provenance), lease.py (Fabric
  frontend), tools/freeze_check.py, tools/kind_audit.py, tests/ [IMPL]. Wave-2 worker
  libraries (explib, attain.py certifier, pte_mut mutation gate, lightcone.py ceilings)
  live under research/harvest/** and were NOT promoted into prometheus/ananke
  (W2-AE packaging INCOMPLETE) [CLAIM handoff].
- Scale of code: prometheus/ananke ~10k lines incl. 27 test files (164 test
  functions; README packet claims 185 tests at C1b). roles/Ananke holds ~104k lines of
  Python, a large part being worker scripts and patched scratch copies of the engine
  [IMPL wc counts this crawl].

## 3. Code architecture and dataflow

Dataflow for one evaluation (assays.evaluate): genomes[P] x seeds[M] -> envs.build
(per-world sensor/actuator sites, sense_val[T,B,K], read_idx, targets y, mirror sign)
-> World(B = P*M; mirror twin m+1 shares world seed of m) -> T ticks -> S0 trace at
readout ticks -> envs.score: per trial 1 if sign(S0) == y, 0.5 if S0 == 0, else 0
-> pair mean over mirror twins (the inference unit) -> bootstrap 99% CI over pairs
[IMPL assays.py, envs.py:score]. Search wraps this; campaign wraps search into waves;
report.py recomputes labels from rows.

Code/doc disagreements found:
- DESIGN.md s7 says targets are "EXACTLY balanced within an episode"; envs.py
  replaced that with i.i.d. coins + mirror pairs after the plant probe showed
  anti-correlated targets let "opposite of last" beat chance [IMPL envs.py docstring;
  CORRECTION calibration/LEDGER.md row 1]. DESIGN s7 was not amended in place.
- DESIGN s7 MAJ: "actuator at distance d from all sensors' centroid"; code picks the
  actuator first, then sensors by OUT-distance from the actuator (packets flow the
  other way on directed graphs) [IMPL envs.py MAJ branch; CORRECTION C1_ERRATA E-W2].
- DESIGN s7 XOR: sensors "at distance >= d from each other and from a"; code puts s2
  at exactly d from s1 and the actuator at >= d/2 from both with no upper bound, so on
  rings many XOR actuators are out of light cone [IMPL envs.py XOR; CORRECTION E-W3].
- DESIGN s5 calls the system "PTE"; there is no tensor contraction anywhere -- the
  "tensor" is the storage layout [IMPL].
- C1_REPORT "every number is recomputed by report.py" -- flagged false by Wave-2
  (Pattern 6, harvest/wave2/P-1/DEFECT_PATTERNS.md) [CORRECTION].
- physics_from_levels forced dest_mode=sample on global topology but stored the
  drawn "all" in levels: 951 of 1589 C1 global rows mislabelled (H-IMPL H7), fixed
  09-30 (campaign.py:83-100, dc46fd00f, 86b84227a) [IMPL; CORRECTION].
- twin_assay measured reach from sensor column 0 only although it negates every
  sensor column (MAJ/XOR); reach_nearest added 09-30 [IMPL assays.py; CORRECTION E-H1].

## 4. Claimed computational primitive vs actual mechanism

Engine E1-E7 (PTE substrate + GA):
- Label given: "packets of state moving through a high-dimensional mutable tensor
  medium"; "UDP packets broadcast over a tensor"; "communication physics" [INTENT
  mission].
- Smallest actual mechanism: a homogeneous integer register program (L = 8-16
  instructions, 5 fields, 16 ops incl. ADD/SUB/MULQ/GT/SEL/MAX/SHR/XOR/MOD/RAND/
  SETRULE/WIMM) executed per site per wake tick, reading its own registers, the summed
  per-channel packet inbox and counts, a SENSE value and energy; writing persistent
  registers S, emit flag/channel/payload, a routing-weight increment, and optionally
  its next rule index or one immediate offset. Messages are integer vectors summed at
  the receiver (no source identity, no per-packet identity) [IMPL engine.py:_tick,
  DESIGN s5].
- In principle it can express: any finite-state per-site transducer within L lines,
  signal transport by re-emission (relay), local latches, delay lines via packet
  latency, count/threshold codes via Acc_cnt, parity via XOR op on channel-separated
  sums, rule-switching state machines (G <= 4), weight-biased routing
  [CODE-INFERRED]. Straight-line programs have no loops; SEL/SETRULE give branching;
  recurrence comes only through tick-to-tick state and packets.
- Reasoning phenomena the rulers tried to observe: distal transport (RELAY), two-input
  integration/parity (XOR), noisy evidence integration (MAJ), adaptation to a hidden
  mapping flip with delayed teacher (FLIP), memory across distractors (HOLD); plus
  "phase boundaries" over physics dials [INTENT PREREG_PTE_C1 s0-s8].
- Could the organism perform them: plants show RELAY/HOLD are solvable in-space;
  FLIP has a 16-line in-space plant at one cell (0.97-0.98) [RESULT-UNVERIFIED
  H-PLANT]; XOR parity has a 12-line in-genome plant at one cell (0.85) [RESULT-
  UNVERIFIED W2-V/E-W23]; at L8/C1 rows parity is argued representation-limited
  [RESULT-UNVERIFIED]. So the substrate CAN express all five at some physics, but
  search found only RELAY transport (6 lineages), HOLD latches, MAJ near single-sensor
  transport, and one-shot latches [RESULT-UNVERIFIED E-W19, E-W22].
- Could the ruler tell it from a cheap shortcut: largely NO as originally built:
  SIGNAL (lo99 > 0.55 over 12 trials) is cleared by a one-shot flood latch (~0.58);
  XOR SIGNAL is cheatable by a NOR readout (0.759); FLIP SIGNAL is cheatable by a block
  clock (1.000) and copy policies reach 0.75; zero_comm and env_permutation cannot
  fail; MAJ INTEGRATION (lo99 > 0.70) is unattainable at 13/19 SIGNAL physics
  [CORRECTION C1_ERRATA E-W5, E-W6, E-W15, E-W17, E-W22]. Later rulers (XOR_SYM, FLIP
  balanced-accuracy B lo99 > .75, attainability certifier) were proposed but not used on
  any campaign [CLAIM].

Engine E8-E9 (C1b batteries, carrier-swap lens):
- Label: "mechanism lens", "carrier identification by exact counterfactuals".
- Smallest mechanism: between-tick in-place copies of one state array (or one payload
  component, or the in-flight ring) between mirror-twin worlds that share all
  exogenous randomness, then scoring whether the readout follows the partner [IMPL
  lens.py swap, lens_swap.py].
- Expresses: exact causal "carriage" tests for a named state array at a named tick.
- Limitations recorded by the seat: site_acc + chan_acc ~ 1 is a mirror-pair
  identity; a verdict names the reader's register, not the physical code
  (presence-as-content); every-trial swaps break identity; "applied" is not
  "reached" [CORRECTION SYNTHESIS_2026-09-29, W-I, W-K, W-M].

## 5. Representation/state architecture

- Per site: D in {1,2,4,8} persistent int registers (S0 = actuator), 4 temporaries
  and 4+P output registers zeroed every run, read-only inbox sums (C*P) and counts (C),
  SENSE, ENERGY, ZERO; L writable immediate offsets Kp; R routing weights (0..1023);
  rule pointer r in [0,G), G in {1,2,4} [IMPL engine.py, DESIGN s4-s5].
- Channel state: ring buffer of LM = 1 + max delay slots of summed payloads and counts
  per recipient/channel; it is a legitimate memory store (M2 used it) [IMPL; RESULT-
  UNVERIFIED C1b].
- Values saturate at +-32767; decay is a sign-asymmetric arithmetic shift (positive
  values stall at 2^k-1, negative erase) -- kept as a "dial" [IMPL DESIGN s10].
- No source identity, no TTL, no packet-carried code, no reproduction of sites
  (DESIGN s8 "not in v1"); backlog ANANKE-10/11/12 (port-resolved arrival, TTL,
  packet-carried code) never built [IMPL absence; INTENT BACKLOG_H0H5.md].
- Environment is write-free (no stigmergy) [IMPL].

## 6. Organism/player architecture

- There is no individual organism. The "entity" is one homogeneous law (a genome of G
  rule variants x L instructions x 5 int fields) run by every site of a world, plus
  the physics [IMPL engine.py; CLAIM research/PTE_ENGINE_CARD.md "ENTITY: There is no
  organism"]. Sites differ only by position, initial rule index (hash), inputs and
  accumulated state.
- Genome fields are reduced modulo current register-space sizes at execution, so any
  genome is valid under any physics (enables transplants) [IMPL engine.py g_op etc.].
- Sensors: SENSE register at K sensor sites (1, 2 or 5); actuator: sign(S0) at one
  read site; teacher in FLIP arrives as SENSE at the actuator after readout [IMPL
  envs.py].
- Adaptation within lifetime: plastic routing (w += rval>>shift), WIMM (Kp writes),
  SETRULE (rule switch), random Kp mutation (mut_site) [IMPL]. Seat findings: SETRULE
  "compresses, never expands" (5/5), routing never carried the bit [RESULT-UNVERIFIED
  W-H, ENGINE_CARD].
- Fighting chance for nontrivial reasoning: the instruction set and register file are
  sufficient for small FSM/latch/relay/threshold/parity computation per site; an
  episode is 12-16 binary trials of ~11-20 ticks, so anything beyond short-horizon
  control is not demanded. Composition (two-stage) was rarely or never found
  [CODE-INFERRED; RESULT-UNVERIFIED C1_REPORT F1].

## 7. World/environment architecture (toy scale, precisely)

- Graph: ring, torus, random (k 3 or 6, directed), smallworld (torus r1 + rewire 5%
  or 20%), global; N in {64,100,144} in C1 search (scale probe 400/1024/2304) [IMPL
  campaign.py DIALS].
- Tasks (envs.py): binary target y in {-1,+1}, 12 trials per episode (FLIP 16), trial
  period delta+1+iti (iti 2), delta in {4,8,16}, gap {4,8,16}, cue_len 2, amplitude
  256; distances d in {1,2,3,5}. One episode is T ~ 84-360 ticks [IMPL].
  - RELAY: cue x at s, readout at a at distance d after delta ticks; y = x.
  - XOR: two sensors, y = x1*x2.
  - MAJ: 5 sensors each flipped w.p. 0.3; y = x (single-sensor ceiling 0.70).
  - FLIP: y = m*x, m flips every block (2 or 4) trials, teacher after readout.
  - HOLD: sensor = actuator, distractors (amp 64) in the gap.
- Stochasticity: hash-driven loss/latency/jitter/dup/noise/wake. No adversaries, no
  multiple agents in competition, no resources except optional energy, no ecology,
  no environmental change beyond FLIP's mapping flip, no open-endedness [IMPL].
- Toy flags: each task is a fixed 1-bit-in/1-bit-out mapping with 12 scored readouts;
  a one-shot event can clear SIGNAL; env randomness is redrawn per world so
  memorizing positions is impossible, but the task class is fixed per cell
  [IMPL; CORRECTION E-W22]. Transfer across families was attempted (wave C).

## 8. Search/training/adaptation mechanism

- GA (search.py): random genomes (fields uniform 0..255, imm -128..127); per-field
  resample 0.04, whole-instruction resample 0.15, swap 0.10, uniform crossover 0.30
  across instructions; truncation 25%, elite 4; pop 96 x 36 generations (C1),
  M = 8 fresh training worlds per generation; champion by 16-world re-evaluation;
  held-out 64 worlds once [IMPL search.py, campaign.py a_search].
  Per A1 cell: 96*8*36 + 96*16 + 2*64 ~ 29k world-episodes [CODE-INFERRED].
- Shaping: + 0.10*max(twin contrast,0) + 0.02*sens_any because "random program space
  is ~99% deaf" (1-5% of random genomes are perturbed by a cue, ~0.1% reach the
  readout) [CLAIM PREREG s4].
- Collapse modes recorded: in NULL runs every genome scores exactly .5 until gen ~5
  (40 runs for all 36 gens) while population sensitivity rises 19-70x under the
  w_any bonus (selection on the shaping term, not the task) [CORRECTION E-W10];
  champions selected on 8 worlds below a selector ceiling; "rule-mosaic lottery"
  champions (rules > 1, setrule 0: only the actuator's random initial rule matters)
  [CORRECTION E-W18]; mis-tuned champions one tick off [CLAIM DEFECT_PATTERNS P7].
- Not used: novelty search, QD archive (ANANKE-14 backlog), lineage/inheritance
  across episodes (ANANKE-21), multi-family or mixed-topology training [IMPL absence].

## 9. Measurement/ruler stack

- Accuracy: per-trial sign(S0) == y, 0.5 credit for S0 == 0; pair mean; 99%
  percentile bootstrap over 32 mirror pairs [IMPL assays.pair_ci]. Undercovers at P=32
  (lower bound misses 0.8-9% vs nominal 0.5%) [CORRECTION E-W9, inference.py docstring].
- Labels (campaign.classify/causal_label): SIGNAL lo99 > 0.55; COMM_DEPENDENT
  comm_delta lo99 > 0.03; INTEGRATION MAJ lo99 > 0.70 or any XOR SIGNAL;
  CAUSAL_SUPPORT comm: zero_comm <= .55 AND packet_ablation <= normal-.10 AND
  env_permutation in [.4,.6]; HOLD: memory_ablation <= normal - .10 [IMPL
  campaign.py:445-480].
- Controls (assays.control_battery): zero_comm, shuffle_dest, shuffle_time,
  randomize_payload, packet_ablation (drop arrivals over [t0, readout)),
  memory_ablation (reset S mid-trial), adaptation_off, frozen_routing, max_loss,
  irrelevant_channel; no-op digest guard; env permutation null [IMPL].
- Twin assay: negate trial-2 cue in an otherwise identical twin; reach, persist,
  beyond_hop [IMPL].
- Anomaly flags (8): SILENT_COMPETENCE, COMPETENT_WITHOUT_COMM, MEMORY_WITHOUT_USE,
  ROBUST_UNDER_LOSS, COMPETENT_UNDER_COST, ANTI_CORRELATED, TRAIN_HELD_GAP,
  DISTRIBUTED_MEMORY_UNDER_DECAY [IMPL campaign.anomaly_flags].
- Phase boundary criterion: adjacent-level jump >= max(.10, 3 SE) and >= half the
  transect range; SUPPORTED if repeated on fresh seeds and a second base [IMPL
  detect_boundaries; INTENT PREREG s8]. Post-data defects D1 categorical dials, D2
  zero-variance, D3 dips [CORRECTION PREREG annotation].
- Blind spots documented by the seat (selected): packet_ablation window excluded the
  readout tick (E1, vacuous for M3); frozen_routing vacuous under dest_mode all (E2);
  memory_ablation reset only S (E3); zero_comm/max_loss/env_permutation forced
  (E-W5); REACH_BEYOND_HOP misfires (E-H1, E-W7) and is a false negative for latches
  (E-W22); the trial-2 twin is blind to once-per-episode mechanisms [CORRECTION].

## 10. Baselines and controls

- Constant policy = exactly 0.500 per mirror pair (by construction) [IMPL envs.py].
- "Memoryless/no-communication" baseline = champion's own zero_comm on the same
  worlds -- but this is exactly .500 in 213/213 RELAY, 174/174 MAJ, 95/95 XOR rows
  because the actuator never is the sensor and twins share physics; so it is not an
  informative baseline in comm families [CORRECTION E-H2b].
- Single-sensor ceiling for MAJ 0.70; XOR single input 0.500 [INTENT PREREG s2];
  "XOR single input = .500 exactly" true only for sensor 2 [CORRECTION Pattern 6].
- Positive controls: plants (relay_flood, hold_latch, C1b fixtures, later refresh
  relay, P-FLIP, P-XOR, MAJ plants); cheats: sense_copy, NOR XOR cheat, FLIP block
  clock [IMPL plants.py; RESULT-UNVERIFIED research/].
- Missing in C1: a shaping-off (w = 0) search arm (proposed for C2 as arm W0), a
  random-search baseline at equal budget, any external/sealed holdout (holdouts are
  seed namespaces by the same author) [IMPL absence; CLAIM PREREG s13].

## 11. Historical experiment campaigns

Inventory sanity check by this crawl (zero-cost read of committed rows): pte/c1_rows/
cells.jsonl.gz = 6596 rows: A0 5000 census; A 352 evolve; B 582 census + 204 evolve;
B2 225 census + 45 evolve; C 84 transfer + 48 evolve; D 12 adjudicate + 24 evolve;
E 15 transfer + 5 evolve. pte/c1b/c1b_rows/rows.jsonl.gz = 27 rows [IMPL].

C-01 PTE-C1 preflight (2026-09-24, before freeze)
- 110 cells on seeds 1-3; plant probe caught anti-correlated balanced targets, no-op
  guard reading final state only, ~99% deaf random genomes (-> shaping bonus), sensor
  placement crash on sparse graphs, sign-asymmetric decay [CLAIM PREREG s11, journal].
- Outcome label: INSTRUMENT FAILURE (caught pre-data; design changed).

C-02 PTE-C1 (2026-09-24 12:04Z -> 09-25 00:06Z; prereg 78243a758, freeze 362f2189b,
code eb7c4b40a; report e35fb9704)
- Question: where in communication-physics space does organised processing appear,
  persist, adapt, transfer (phase map) [INTENT].
- Organism: homogeneous genome (G 1-4, L 8-16) evolved by GA (pop 96 x 36 gens).
- World: 5 families on N 64-144 graphs, 31 physics dials drawn uniformly.
- Pressure: task accuracy + twin-contrast shaping.
- Measurement: SIGNAL/COMM_DEPENDENT/CAUSAL_SUPPORT/TRANSFER_SUPPORT/boundaries.
- Arms/scale: A0 5000 census cells (64 random genomes x 8 worlds + plant), A1 400
  planned (352 run, 48 budget-censored), B 786, B2 270, C 132, D 36, E 20 (N up to 2304);
  12 h 02 m on one RTX 5060 Ti [CLAIM C1_REPORT].
- Reported: A1 COMM_DEPENDENT 8/352; RELAY held 0.84-0.89 vs 0.500 zero-comm, causal
  4/4, reproduced 3/4, size-free to N=2304, collapses on random graph; MAJ integration
  one cell (0.789) not reproduced; XOR 0/83, FLIP 0/82; 13 SUPPORTED + 24 CANDIDATE
  boundaries; mechanisms M1 routed relay, M2 delay-line HOLD memory (post-hoc), M3
  self-modifying timing-locked MAJ, M4 integration, M5 local latch; predictions 5
  HELD / 3 LOST [RESULT-UNVERIFIED pte/C1_REPORT.md].
- Later reinterpretation: see s12; by 10-01 the headline claims are largely
  construction artefacts or single-lineage descriptions (E-H2b, E-H5, E-W1, E-W4,
  E-W5, E-W13, E-W19, E-W21) [CORRECTION pte/C1_ERRATA.md].
- Paths: pte/PREREG_PTE_C1.md, FREEZE_PTE_C1.json, C1_REPORT.md,
  REVIEW_PACKET_PTE_C1.txt, c1_report/, c1_rows/, c1_a0/, c1_posthoc/.
- Label: LATER OVERTURNED (headline) / MIXED (the RELAY one-hop transport and HOLD
  latch existence claims were not overturned, only rescoped).

C-03 A0 interaction analysis (09-24; plan 896a9a077 before A0 closed, script 47b1e4b27)
- Ladder L1 perturbable / L2 distal influence / L2' plant viable; L1 predicted by
  program-space dials (AUC .91-.96); L2/L2' INDETERMINATE (too few positives); RELAY
  L2 and L2' disjoint (0/7) [RESULT-UNVERIFIED pte/c1_a0/A0_FINDINGS.md].
- Later: A0 dial ranking is 64-79% light-cone identity once ceiling-normalised (E-W16).
- Label: INCONCLUSIVE.

C-04 C1 post-hoc battery (09-24/25; exploratory)
- HOLD 4ab2ba01: state reset no effect, packet drop -> 0.50 => "M2 delay line";
  3291f6c2 DISTRIBUTED_MEMORY_UNDER_DECAY depends on adaptation [RESULT-UNVERIFIED
  pte/c1_posthoc/posthoc_adjudication.json]. Label: REPORTED POSITIVE (exploratory).

C-05 PTE-C1b (2026-09-26; prereg v1 9b6e4bb95 + A1-A3; freeze v2 5bd6c3945; package
cc98596dd; 27 cells, 510 s)
- Question: adjudicate M2 and M3 with per-carrier resets, in-flight flush,
  corrected packet-ablation window, 4 fresh searches per specimen, recheck of 12
  D-wave cells.
- Reported: M3 = transport landing ON the readout tick (C1 drop window excluded it:
  0.697 -> corrected 0.501) + SETRULE required, rule state carries no cue; M2 bit in
  flight mid-gap (flush -> 0.497), reproduced 3/3 fresh SIGNAL champions; labels
  IN_FLIGHT_PLUS_JOINT_UNRESOLVED and TRANSPORT+RULE_SWITCH_UNRESOLVED; 0a23398f not
  reproduced 0/4; predictions P3 LOST, P5 held by letter only [RESULT-UNVERIFIED
  pte/c1b/REVIEW_PACKET_PTE_C1b.txt].
- Later: K1 the M2 code IS the sign of payload component 1 (census read component 0
  only); K2 routing-weight drop was disruption, w swap carries nothing; K3 SETRULE is a
  one-time bootstrap to rule 0 [CORRECTION pte/c1b/CORRECTIONS_2026-09-27.md].
  W-B: one-rule law bit-identical to M3 champion ("zero-register artifact").
- Label: MIXED (M3 "self-modification" OVERTURNED; M2 in-flight carriage REPORTED
  POSITIVE and later model-predicted).

C-06 Arc 1 spikes + SYNTHESIS_2026-09-27 (c34cbb463; plan 8e081dcb1)
- ~20 min GPU spikes with predictions frozen first: 15 held, 5 lost; M2 = tuned
  two-stage echo (chance at gap >= 12); C2 and SI01 should not run as designed
  [RESULT-UNVERIFIED research/SPIKES_2026-09-27_LOG.md, C2_SI01_REVIEW.md].
- Label: REPORTED POSITIVE (mechanism description).

C-07 Arc 2: workers W-A..W-F (09-27; SYNTHESIS_2026-09-28_ARC2 8eabc990b)
- W-A echo interval: zero-parameter particle model predicts 46/46 unseen curves
  (median MAE ~.02); strict two-hop echo; gap 7 beats 8 (sawtooth) [RESULT-UNVERIFIED].
- W-B SETRULE census (42 cells): 64% bootstrap artefact, 29% per-tick branch; r never
  the carrier (17/18 NO-EFFECT).
- W-C PTE vs Aether: "Aether = timing, PTE = content" REFUTED; 7/13 specimens carry
  the cue as WHO FIRES (presence), which superposition renders as content.
- W-D intervention-reach taxonomy across 5 seats (no experiments).
- W-E T-RET-1 retention census: NO (frozen signed "scars", never read; later W-G: some
  are read as interference).
- W-F carrier census over 166 SIGNAL cells: HOLD SITE 81/85; "JOINT = phase mixture"
  RETRACTED (sum ~ 1 is a mirror identity) [CORRECTION W-I, W-M].
- Designed echoes (research/designed_echoes/, plan 4c4ca8dea): model calibration 7/7
  FIT incl. a designed failure; "calibration, NOT emergence" [CLAIM].
- X4 emission-cost pilot: UNRESOLVED (n = 3/arm) [RESULT-UNVERIFIED W-C/X4_RESULT.md].
- Label: MIXED.

C-08 Arc 3: W-G..W-L + ARC3 synthesis (09-28; 7fc642367)
- W-G SI01 / T-RET-2 (16 champions + 5 plants, 2 namespaces, Holm): NO nontrivial
  retention regime; SI01 CLOSED for current champions; hand plants C-EFF/C-AVL do
  retain, so "PTE lacks a persistent substrate" is false [RESULT-UNVERIFIED W-G].
- W-H SETRULE: COMPRESSION 5/5, EXPANSION 0/5 (4-7-instruction fixed-rule latches
  beat switching champions, .999 vs .755); champions reproduced 0/4 from own budget.
- W-I carriers are trajectories (channel first, then site latch; presence read as
  content); W-J receiver semantics act through aggregation gain (~.02 at C1 physics,
  ~.13 lossless; one SUM count-threshold majority code .801 that is .500 under every
  other operator); W-K intervention-reach fixtures -> lens.verify_reach (013999d54);
  W-L n-back retention: reachable 4/8 but only as INTEGRATION, selective lag-2 0/4.
- H6 "search reachability, not physics, bounds what PTE shows": SURVIVES the seat's
  own falsification attempt ("is anything search-reachable we cannot design? not yet")
  [CLAIM research/CROSS_THREAD_COMPRESSION.md, SYNTHESIS_2026-09-28_ARC3.md].
- Later: W-N/W-O show W-L CHANCE was sample size but does not generalise (84% of 733
  CHANCE stay CHANCE); H6 rescoped in Wave 2 (s12).
- Label: MIXED (H6 later LATER OVERTURNED as a general law; retention NULL stands).

C-09 Swap-instrument arc W-M..W-Z (09-28..30; SYNTHESIS_2026-09-29 cf94415d9)
- Single-trial S/C/N swap census (W-M, promoted lens_swap.py 8ab39d5fe); 733 CHANCE
  verdicts re-run at 512 worlds (W-O); relative certificates REL2/REL3/REL4 (W-Q, W-U,
  W-W), REL5 targeted false-certificate check (W-X) -> swap_rel.py promoted 07b463849;
  phase stratification (W-R); first-broadcast latency-jitter rule exact in 3 RELAY
  cells, does not transfer (W-S, W-T); MAJ 4781b0a1 DISTRIBUTED-NONMAJ (W-V); Kp[7]
  not a carrier (W-Y); AUDIT3 consistency 92.7% < frozen 95% (W-Z).
- Corrections: W-O plan freeze not provable from git; W-Q headline overclaims
  (Harmonia #1045) [CORRECTION research/CORRECTIONS_2026-09-29_SWAP_AUDIT.md].
- Mostly statistics on synthetic pair data and C1 specimens; no new organisms.
- Label: MIXED (instrument development; several frozen predictions missed).

C-10 Inference harvest Wave 1 (09-30; directive 4a97f97fa)
- H-IMPL code audit (26 findings, 5 patches 41e386ccd); H-SCI interpretation
  (one-hop transport; zero_comm forced; one physics point 86fc0105 underlies most
  mechanism claims); H-INST instrument gaps (pte_trace draft, 23 tests); H-CHK three
  frozen checks (C1/C2 PARTIAL, C3 NOT CONFIRMED); H-PLANT (plan 01234c0ad, no search):
  P-XOR 16-line flood + clock plant 1.000 at chosen physics X0, P-FLIP 0.978 at d9cc vs
  the search's 0.479, relay_flood 0.984 at d9cc d5 [RESULT-UNVERIFIED
  research/harvest/]. PTE_CAUSAL_AUDIT_2026-09-30.md (cc44f5903): "the main
  comm-dependence control cannot fail".
- Label: LATER CORRECTION source (reclassifies C1; itself partly corrected by Wave 2,
  e.g. lc_census denominators, transfers cited as searches).

C-11 Inference saturation Wave 2 (09-30 20:23 -> 10-01 ~03:20Z; directive fd631acb2;
close e0f21332d)
- ~38 worker ids (W2-A1..W2-AL) + principal P-1..P-4 on Opus, CPU only, 2 threads,
  < 0.5 core-h each; 7 workers terminated by API weekly limit (INCOMPLETE, do not cite)
  [CLAIM harvest/wave2/COMMON_BRIEF_W2.md, handoff].
- Key reported results [RESULT-UNVERIFIED, all in C1_ERRATA E-W1..E-W23 + corrections]:
  NULL placement of 454 C1 evolve NULLs: 139 (30.6%) physics-capped, 62-65 (~14%)
  eligible for a search-limitation reading, 250 open, 0/113 broken (W2-W, W2-T);
  13 SUPPORTED boundaries = identity / plant-design / program-space, economy OPEN (W2-Y);
  rulers cheatable (W2-B XOR NOR .759, FLIP clock 1.000; W2-L/W2-S FLIP copy ceiling
  .75, certificate B lo99 > .75; W2-J XOR_SYM); MAJ INTEGRATION unattainable at 13/19
  SIGNAL physics (W2-M); rule-mosaic lottery (W2-Q); shaping term initiates NULL
  sensitivity climb (P-3); C1 held CI undercovers (W2-H); topology->random collapse is
  hop count (W2-G, W2-I refine: cluster/latency-label dependence for 4 laws); flood
  latch (W2-AI, below); in-genome XOR parity plant (W2-V, below); economy plants
  (W2-Z: only emission energy-gated; 31/50 MAJ economy NULLs plant-solved).
- W2-AI FLOOD LATCH (e40c49703; E-W22): the only two multi-hop RELAY SIGNAL champions
  (925caa3a ring r3 d5, held .578 lo99 .556; 882525a9 smallworld d3, held .591 lo99
  .564) do forward across 2-3 hops (64/64 held worlds truly multi-hop; vertex-cut ->
  .500 while equal-size off-path cuts change nothing), but only ONCE per episode:
  accuracy by trial 1.00, .70, .59, ... .50; a two-sign latch model predicts 99.0-99.6%
  of readouts; decompiled EMIT = MAX(SENSE, IN0_1) and EMIT = MOD(-109, max(CNT0,
  SENSE)+1): receipt-triggered re-emission with no reset. At 12 trials a one-shot
  latch clears SIGNAL (ceiling ~.58-.59). Twin assay at trial 2 is a false negative
  for latches (beyond_hop 1.0 at trial 0) [RESULT-UNVERIFIED harvest/wave2/W2-AI/
  REPORT.md]. Follow-up W2-AL (latch prevalence across all 69 SIGNAL champions) is
  INCOMPLETE; an uncited tally by my sub-reader found 7 latch-like rows of 69, 55
  per-trial by its classifier [UNKNOWN; do not cite].
- W2-V XOR PARITY PLANT (fab7bb68e; E-W23): XOR was never evolved (0/83 C1 SIGNAL;
  no harvest search targets XOR). At row 4222a5f7 (L12 D8 P1 C4) a 12-line parity plant
  inside the row's own sampled genome scores .850 [lo .819] on fresh worlds and .832
  on C1's held-out worlds vs champion .503, using sensor broadcast + channel-tagged
  one-hop forwarding: "first search-limited XOR NULL". At three L8/C1 rows parity is
  argued REPRESENTATION-LIMITED (line accounting, exhaustive readout enumeration); a
  6-line NOR cheat reaches lo99 .534-.547 [RESULT-UNVERIFIED harvest/wave2/W2-V/].
  Earlier H-PLANT P-XOR (16 lines: flood per-trial flags P/Q, readout XOR of flags)
  scored 1.000 only at a chosen physics X0 and .663/.805 at census rows; its one-flag
  must-fail control (.763 when negated) exposed that XOR SIGNAL is passable without
  parity [RESULT-UNVERIFIED harvest/H-PLANT/REPORT.md].
- C2 prereg DRAFT (W2-AB): H6 at admitted cells with arms BASE/W0 (shaping off)/M32/
  B4X/PSEED/KSEED/STEP, 9-15 GPU-h; NOT frozen, NOT authorized [INTENT].
- Label: LATER CORRECTION source; flood latch and parity plant themselves REPORTED
  POSITIVE (instrument-level), unreviewed.

C-12 C4 R-STAT review for Cosmos (09-30, Aporia #1137): Phase 1 INTERIM ded6f5729,
Phase 2 blocked; notes research/c4/R-STAT_FINAL_NOTES.md [CLAIM]. Not a PTE campaign.
Label: UNKNOWN (outside scope, not read in depth).

Never run: PTE-SI01 as a campaign (designed in reply 02_REPLY_TO_STEWARDS.md; closed
"for current champions" by W-G); PTE-C2 (draft only); RunPod scale leg (ANANKE-18);
fused kernel (ANANKE-09); v2 dials (port-resolved arrival, TTL, packet-carried code).

## 12. Reported results and later corrections (timelines)

T1 "Communication-dependent machinery, causally verified"
- Claim (09-25): RELAY 0.84-0.89 vs 0.500 zero-comm; COMM_DEPENDENT 8/352;
  CAUSAL_SUPPORT 4/4 [CLAIM C1_REPORT s1].
- Challenge (09-30 H-SCI F2, principal-verified): zero_comm is exactly .500 in
  213/213 RELAY, 174/174 MAJ, 95/95 XOR rows because twins share all physics draws and
  the actuator is never the sensor; max_loss is the same run; env_permutation E = .5
  for any program [CORRECTION E-H2b, E-W5].
- Current status: COMM_DEPENDENT is an alias of SIGNAL in comm families; causal
  support rests on the packet_ablation clause alone (613162a3's packet clause later
  replicates, W2-K) [CORRECTION].

T2 "Size-free to N=2304"
- Claim: frozen RELAY laws keep .875-.893 to N=2304 [CLAIM C1_REPORT s1].
- Challenge: wave E scaled ONE law (bbef66a1), which failed fresh-seed reproduction
  (.572/.506); reproduced cells were never scaled; size-free is forced for local laws
  [CORRECTION E-H5, E-W8].
- Status: unsupported as a general statement.

T3 "Topology-bound laws"
- Claim: every RELAY law collapses to .500 on a random graph; machinery encodes lattice
  geometry [CLAIM C1_REPORT F2].
- Challenge: transplant kept env d, which on random graphs is BFS hops: a 1-hop task
  becomes 3 hops; at d=1 all 4 laws stay above chance [CORRECTION E-W1, W2-G].
- Refinement: REFINE not KILL -- cluster/redundant-path dependence for 4 laws,
  per-port latency labels for HOLD 4ab2ba01 (W2-I) [CORRECTION corrections block].

T4 "Evolved transport is one hop" (Wave-1 reading)
- Claim (H-SCI F1): 48/50 RELAY SIGNAL rows one-hop.
- Challenge: 150/196 RELAY tasks only demanded one hop; 50 rows = 17 conditions = 6
  lineages (32 rows from one); A1 one-hop 3/32 vs multi-hop 1/39 (p = .32)
  [CORRECTION E-W4, E-W19].
- Then W2-AI: the 2 multi-hop SIGNALs DO forward but as one-shot flood latches
  [CORRECTION E-W22]. Status: per-trial resettable multi-hop relay NOT shown.

T5 "SUPPORTED phase boundaries" (13)
- Claim: decay, delta, economy gate the relay plant; HOLD decay dip; emit vs rules.
- Challenges: PREREG annotation D1-D3 (09-24, post-data); E-W13 refresh plant is flat
  in decay (relay_flood writes S0 only on change); E-W8 economy = budget identity;
  delta = light-cone/transport-time identity; E-W21 "No SUPPORTED boundary is
  established physics beyond the transport bound"; economy OPEN (W2-AH INCOMPLETE).
- Status: P1 stays HELD as a label; its content is identity + plant design.

T6 M2 "delay-line memory"
- C1 post-hoc -> C1b (IN_FLIGHT_PLUS_JOINT_UNRESOLVED, "signed sum NOT the code")
  -> K1/K2 (component-1 sign IS the code; w carries nothing) -> W-A zero-parameter
  echo model 46/46 -> "schedules, it does not store"; at chance beyond trained gap
  [CORRECTION CORRECTIONS_2026-09-27, SYNTHESIS_2026-09-27]. Status: the strongest
  surviving mechanistic description, all at one physics point (86fc0105 lineage).

T7 M3 "self-modifying timing-locked MAJ"
- C1 (packet ablation no effect; adaptation-off drops) -> E1 drop window excluded the
  readout tick, E2 frozen routing vacuous under dest all -> C1b transport on the
  readout tick -> K3/W-B SETRULE is a one-time bootstrap to rule 0; a one-rule law is
  bit-identical [CORRECTION]. Status: OVERTURNED as self-modification.

T8 M4 "integration beyond one sensor"
- 4781b0a1 lo99 .742 > .70; replicates .636/.520 not reproduced [CLAIM C1_REPORT].
- Later: INTEGRATION genuine at 4781b0a1 (a plant matches, single-sensor transport
  cannot), but unattainable at 13/19 MAJ SIGNAL physics; 11/19 matched by single-sensor
  transport (E-W15); W-V DISTRIBUTED-NONMAJ; W2-AG SR-03 adjacent-sensor reverberation
  candidate. Status: open, one cell.

T9 XOR/FLIP NULL (P3 "zero XOR SIGNAL" HELD)
- Reading at C1: two-stage compositions the search never assembled (F1).
- Challenges: >= 36/83 (62/83 under LC2) XOR rows light-cone capped; XOR SIGNAL
  passable by NOR (.759) and FLIP SIGNAL by block clock (1.000); H-PLANT P-FLIP .978 at
  d9cc vs search .479 (n = 1 search); W2-V in-genome parity plant .850 at 4222a5f7
  [CORRECTION E-W3, E-W6, E-W17, E-W23].
- Status: NULL is mostly construction-capped; where not, search-limited at >= 1 XOR
  cell and 1 FLIP cell; representation-limited at L8 rows.

T10 H6 "search reachability bounds PTE"
- ARC3 (7fc642367) SURVIVES -> Wave-1 "search, not physics" -> H6_ADVERSARIAL v1-v4
  -> v4: supportable for at most ~11-15% of NULLs, FALSE for ~24-31% (capped),
  UNDECIDED for the rest -> W2-X struck several sentences ("one-hop wall is sharp",
  "S under blind selector") -> W2-AI: search found once-per-episode forwarding
  [CORRECTION harvest/wave2/P-1/H6_ADVERSARIAL.md s12-s15]. The H6 text in
  research/CROSS_THREAD_COMPRESSION.md was not updated [IMPL observation].

T11 SI01 retention
- Steward directive (09-25) -> seat objections O1-O4 -> W-E NO -> W-G NO (preregistered,
  replicated) -> W-L retention reachable only as integration. Note H-SCI: tasks never
  reward cross-trial retention (i.i.d. targets), so absence is expected [CORRECTION
  PTE_CAUSAL_AUDIT chain table]. Status: REPORTED NEGATIVE/NULL, with the world
  unable to demand the phenomenon.

## 13. False-positive archaeology

The seat's own Wave-2 synthesis (harvest/wave2/P-1/DEFECT_PATTERNS.md, 83fcccf2c)
classifies C1's failures into seven patterns; this crawl agrees with the taxonomy as
a description of the record [CLAIM]:
1. Construction masquerading as result: XOR actuator out of light cone; MAJ placement
   by out-distance on directed graphs; 77% of RELAY tasks one hop; "topology-bound" =
   hop count; size-free forced for local laws.
2. Controls that cannot fail: zero_comm, max_loss, env_permutation, shuffle_dest on
   global, twin-symmetric C1b predictors, 24/98 swap no-op arms, causal_label without
   a competence gate.
3. Ruler aimed beside the claim: XOR SIGNAL vs parity (NOR .759), FLIP SIGNAL vs
   feedback (clock 1.000), legacy REACH_BEYOND_HOP fired by one-hop emitters, verify_reach
   "applied" is not "reached", absolute .62 intact bar.
4. Selection and targeted sampling reported as rates: "RELAY 50/196" pooled over
   targeted waves (6 lineages); 5/8 predictions held but mostly low-risk (P-4).
5. A lower bound read as an impossibility: relay_flood failure at decay > 0 read as
   physics-dead (refresh plant survives); economy boundary a budget identity.
6. Vocabulary/provenance drift: transfers cited as search NULLs (fac4aaa2, ef77ef2e,
   1b26026f), dest_mode record differs from what ran (951/1589 global rows).
7. The objective is not the task: w_any bonus drives sensitivity in flat NULL runs;
   contrast bonus pays rectified codes the full .10 at chance-level accuracy;
   rule-mosaic lottery champions.
Additional false-positive items found in the record:
- One-shot flood latch clears SIGNAL (lo99 > .55) at 12 trials: any RELAY SIGNAL near
  .58-.60 is uncertified as per-trial competence (E-W22) [CORRECTION].
- C1 headline "SIZE-FREE" from one non-reproducing law (E-H5).
- "Pooled counts are not rates": effective n 18-60 (E-W19).
- C1 held-out CI (percentile bootstrap, P = 32) undercovers; 2-3 SIGNAL calls flip
  under BOOTT/t (E-W9).
- MEMORY_WITHOUT_USE / persistence flags on NULL champions produced at onset by the
  w_any term; NULL champions ~80x above random genomes on persist (E-W10, partly
  walked back by W2-X: attribution to w_any NOT shown).
- HOLD "SITE 81/85" is forced by locality (sensor = actuator) (PTE_CAUSAL_AUDIT).
- MAJ "majority" readings: majority agreement .77-.84 > best single sensor, but W-V
  shows the readout is DISTRIBUTED-NONMAJ and H-CHK shows a lossy true majority also
  reads NONMAJ -- the classifier cannot certify majority [RESULT-UNVERIFIED].
- Mechanism generality: most mechanism claims (M2 echo, W-I panel, W-L, W-S/W-T,
  4781b0a1) come from one physics point descended from census cell 86fc0105 (H-SCI F3).
- Same-author risk: substrate, envs, search, detectors, predictions and most reviews
  by one seat (and many sub-agents of one model); independent reviewers Kairos/Elenchus
  never replied (PREREG s13; review packet s9) [CLAIM].
- Atlas disagreement: the Atlas digest (roles/Atlas/inference_harvest_2026-09-30/
  workers/digests/ananke_pte_tyche.md) records PTE-C1 as "confirmed (unreviewed)" and
  M1 routed relay as "strong within PTE"; it was written before the harvest
  deliverables existed and is superseded by C1_ERRATA E-H2b/E-W1/E-W19/E-W21 [IMPL
  comparison by this crawl].

## 14. Likely false-negative regimes

- Search-limited NULLs with in-space plants: FLIP at d9cc (plant .978 vs search
  .479, one search seed); XOR at 4222a5f7 (plant .850 vs .503); multi-hop RELAY at d9cc
  (relay_flood .984; but the "searches" there were transfers) [RESULT-UNVERIFIED
  H-PLANT, W2-V]. Search budget (pop 96 x 36 gens, 8 worlds/gen) is tiny relative to a
  genome space of 256^(5*L*G); W-H reports champions reproduced 0/4 from their own
  budget, i.e. SIGNAL cells are tail draws [CLAIM].
- Flat landscape: ~99% of random programs are deaf; in NULL runs accuracy variance is
  zero until gen ~4-5 (median), so selection is blind early; the shaping term may lead
  search toward rectified/presence codes rather than computation (untested; C2 arm W0
  proposed) [CLAIM E-W10, PTE_CAUSAL_AUDIT item 3].
- Representation-limited regimes: L = 8 with C = 1 cannot express parity (argued,
  W2-V); straight-line programs with no loops and 4 temporaries; G <= 4 rules.
- Placement/light-cone caps: 139/454 (30.6%) C1 NULLs physics-capped -- these are
  instrument false negatives, not evidence about emergence [CORRECTION E-W20].
- Ruler false negatives: REACH_BEYOND_HOP at trial 2 misses latches; twin-symmetric
  predictors forced at .5; absolute "kills" thresholds unattainable for champions near
  .6 (C1b f6b623cd fresh champions show the M3 fingerprint descriptively but mechanical
  labels miss it) [CORRECTION E-W22; C1b packet s5, s8].
- Plant-as-physics-map: relay_flood's failure at decay > 0 made decay look lethal;
  refresh plant shows it is not (matched counterfactuals) [CORRECTION E-W13].
- Tasks that never reward the phenomenon: cross-trial retention (i.i.d. targets);
  per-trial multi-hop relay is rewarded only ~+.08 above the latch ceiling; FLIP
  inference vs copy policies separated only above B = .75.
- Interval tuning: M2-class mechanisms are tuned to the trained gap and fail at gap >=
  12; anything requiring generalisation across intervals was never trained for.
- Truncated runs: 48/400 A1 cells budget-censored; Wave-2 workers W2-AD/AE/AF/AH/AJ/
  AK/AL killed by API limit; W2-R cut short by an external process kill (X-2 incident)
  [CLAIM].

## 15. Phase 3 audit (per engine)

Engine A: PTE substrate + GA + five task families (prometheus/ananke core)

a. Representation richness (code reasons)
- hierarchy: NO. Flat set of identical sites; no nesting, no multi-scale units; graph
  is fixed per physics.
- compositional structure: PARTIAL. A program is a sequence of primitive ops and can
  compose arithmetic/threshold steps within L <= 16 lines; no reusable subroutines,
  no calls, no loops.
- variable binding: NO. No addressing of values by role; packets lack source identity;
  channel index (C <= 4) is the only tag.
- memory: YES. Persistent S (D <= 8 ints), inbox accumulators, Kp, routing w, and the
  in-flight ring (delay lines) are all writable stores; W-G shows hand plants retain.
- recurrence: YES. Per-tick state update plus packet loops through neighbours.
- counterfactual state: NO in the organism (no internal simulation); YES as an
  experimental instrument (mirror twins, carrier swaps).
- latent variables: PARTIAL. Hidden registers exist, but nothing in the tasks requires
  inferring a latent beyond FLIP's mapping bit m.
- temporal abstraction: PARTIAL. Timers/clocks via counters and SETRULE (W-H "leaky
  timer", "sample/hold clock"); no hierarchy of timescales.
- spatial abstraction: NO. Sites have no position sense; geometry enters only as
  topology; laws are shown to depend on hop count/clustering.
- reusable substructure: PARTIAL. The same law runs at every site (homogeneous
  weight sharing by construction), G rule variants can be reused; no learned modules.
- dynamic routing: PARTIAL. Plastic routing weights bias sampled destinations, but
  "routing never carried the bit" and is inert under dest_mode all.
- self-reference: PARTIAL. WIMM writes the program's own immediates; SETRULE selects
  own rule; no read access to the genome, no packet-carried code (ANANKE-12 not built).

b. Reasoning opportunity
- RELAY: transport one bit d hops within delta ticks -- simple reaction + relay; a
  one-shot latch clears the gate.
- HOLD: hold one bit across a gap with distractors; sensor = actuator, so a 4-9 line
  local latch solves it.
- MAJ: noisy 5-way vote of the same bit; at most physics, single-sensor transport
  matches champions.
- XOR: two-input parity at distance -- the only task needing a nonlinear combination,
  mostly light-cone-capped.
- FLIP: hidden 1-bit mapping that flips every 2-4 trials with delayed teacher -- the only
  adaptation demand; copy policies reach .75.
- Verdict: none of the five tasks demands more than small finite-state control,
  local pattern matching or one-step latching; there is no planning horizon, no
  combinatorial generalisation, no transfer requirement within a run; episodes are 12-16
  trials [CODE-INFERRED envs.py].

c. Shortcut surface
- One-shot flood latch (fires on first positive cue, never resets) -> ~.58-.59 at 12
  trials, above SIGNAL.
- Copy-last-teacher / block-clock policies on FLIP (.75 / 1.000).
- NOR or one-flag readouts on XOR (.759).
- Single-sensor transport on MAJ (matches 11/19 SIGNAL champions).
- Local latch on HOLD (sensor = actuator).
- Rectified one-sided codes paid by the contrast bonus during selection.
- Rule-mosaic lottery (actuator's initial rule decides).
- Distractor-strobed memory in HOLD (5/86 cells).
- Interval tuning to the trained delta/gap.

d. Ruler resolving power
- Original C1 ruler (lo99 > .55 per cell, COMM_DEPENDENT, CAUSAL_SUPPORT, INTEGRATION,
  REACH_BEYOND_HOP, boundary criterion) cannot separate intended cognition from any of
  the shortcuts above; several controls are forced by the mirror design [CORRECTION
  E-W5, E-W6, E-W15, E-W22].
- Post-hoc instruments (mirror carrier swaps, single-trial census, REL4 certificate,
  light-cone ceilings, plants inside the genome, attainability certifier, XOR_SYM, FLIP
  B > .75, per-trial accuracy profile) can in principle separate several shortcut
  classes, and are exact because the physics is deterministic; they were never frozen
  into a campaign [CLAIM handoff].

e. Scale (recoverable numbers)
- Dimensionality: per site D <= 8 int registers, P <= 4 payload ints, C <= 4 channels,
  R <= 24 routing weights (torus r3: 2r(r+1)), L <= 16 Kp; genome G*L*5 <= 320 int fields.
- World: N = 64-144 in search, up to 2304 in transfer probes; B batched worlds.
- Horizon: T = trials * period ~ 84-360 ticks; 12 (FLIP 16) binary trials per episode.
- Population: 96 genomes x 36 generations x 8 worlds per cell (~29k world-episodes per
  evolve cell); held-out 64 worlds (32 pairs).
- Number of worlds/tasks: 5 task families; positions/targets redrawn per world.
- Compute ceiling: one RTX 5060 Ti, 11-21M site-updates/s, C1 total 12 h; RunPod never
  used [CLAIM].

Engine B: mechanism lens / carrier-swap instruments (lens.py, lens_swap.py,
swap_rel.py, c1b.py batteries)
- Representation richness: not an organism; N/A except that it reads every endogenous
  carrier in World.state_arrays() [IMPL].
- Reasoning opportunity: N/A (it is a ruler).
- Shortcut surface (for the instrument): site_acc + chan_acc = 1 identity; every-trial
  swaps break identity; presence read as content (verdict names the reader's register);
  "applied" batch digest not "reached"; 24/98 no-op arms forced NO_EFFECT [CORRECTION
  W-I, W-M, H-INST, Pattern 2].
- Ruler resolving power: exact counterfactual carriage tests at named ticks with
  studentized pair bootstrap certificates; validated on hand plants with must-fail
  controls by the same author; seed consistency near threshold 92.7% [RESULT-UNVERIFIED
  W-W, W-X, W-Z].
- Scale: M = 64-512 worlds per arm; 733 verdicts / 249 groups re-audited.

Engine C: Wave-2 certification stack (research/harvest/**, not promoted)
- attain.py certifier (W2-B), pte_mut mutation gate + guards G0-G12 (W2-C), explib
  9 primitives / 40 tests (W2-F), light-cone/LC2/flood/epidemic ceilings (H-PLANT,
  W2-J, W2-U, W2-Y), pte_trace reach_certificate (H-INST) [CLAIM]. Purpose: certify
  that rulers and controls can discriminate (null, adversary, plant) BEFORE a freeze.
  W2-AE packaging into prometheus/ananke/audit/ INCOMPLETE; directory absent [IMPL].
  Resolving power untested on any fresh campaign [UNKNOWN].

## 16. Research reports and substantial documents

(paths relative to roles/Ananke/ unless noted)
- prompts/2026-09-24_charter/01_OPERATOR_MISSION_verbatim.md -- operator mission (711 lines).
- prompts/2026-09-25_pte_si01_directive/01_STEWARD_DIRECTIVE_verbatim.md and
  02_REPLY_TO_STEWARDS.md -- SI01 Causal-State Boundary Challenge and the seat's
  objections O1-O4 + complete-causal-state enumeration.
- prompts/2026-09-26_c1b_operator_release/ -- operator release, stewards demoted.
- prompts/2026-09-30_inference_harvest/, 2026-09-30_inference_saturation_wave2/ --
  inference-only directives (sha256 2c99c612..., 3c68feac...).
- pte/DESIGN.md -- normative substrate spec PTE-SUB-1/OPS-1 (s0 design choices, s9
  oracle rulings, s10 decay asymmetry).
- pte/PREREG_PTE_C1.md (with post-data annotation D1-D3), FREEZE_PTE_C1.json,
  ANALYSIS_PLAN_C1_A0.md, c1_a0/A0_FINDINGS.md.
- pte/C1_REPORT.md, REVIEW_PACKET_PTE_C1.txt, c1_report/{REPORT.md, summary.json,
  atlas_fact.jsonl, atlas_edge.jsonl}, c1_posthoc/posthoc_adjudication.json.
- pte/C1_ERRATA.md -- E1-E3, E-H1..E-H5, E-W1..E-W23 + corrections block; the single
  most important correction document.
- pte/PREREG_PTE_C1b.md, c1b/{FREEZE_C1b.json, LABEL_TABLES.json, FIXTURES_dev.json,
  ELIGIBILITY_dev.json, C1B_SUMMARY.json, REVIEW_PACKET_PTE_C1b.txt,
  CORRECTIONS_2026-09-27.md}.
- research/PTE_ENGINE_CARD.md -- engine card ("There is no organism"; memory map).
- research/SYNTHESIS_2026-09-27.md, _2026-09-28_ARC2.md, _2026-09-28_ARC3.md,
  _2026-09-29.md -- arc syntheses.
- research/C1B_REVIEW_AND_MECHANISMS.md, C2_SI01_REVIEW.md, CROSS_THREAD_COMPRESSION.md
  (H1-H6), CROSS_ENGINE_THREADS.md, CORRECTIONS_2026-09-29_SWAP_AUDIT.md,
  MEMORY_INTERVENTIONS.md, TEMPORAL_INTERVENTION_COVERAGE.md.
- research/PRIOR_ART_temporal_distributed_computation.md -- ~71 KB, ~45 graded sources
  (headings only read).
- research/instruments/INSTRUMENT_{CARRIER_SWAP,REACH_VERIFICATION,TEMPORAL_REACH}.md.
- research/designed_echoes/{PLAN,RESULT}.md; research/joint_carrier/{PLAN,RESULT}.md.
- research/workers/W-A..W-Z/REPORT.md (+ PLAN/LOG), handoffs/*.md.
- research/harvest/PTE_CAUSAL_AUDIT_2026-09-30.md, PTE_INSTRUMENT_GAPS_AND_UPGRADES.md,
  T_SWAP_REL4_INTERPRETATION_TREE.md, BUILDER_EXPERIMENTS_OPS.md,
  INFERENCE_HARVEST_HANDOFF.md; H-IMPL, H-SCI, H-INST, H-CHK, H-PLANT reports.
- research/harvest/wave2/INFERENCE_SATURATION_WAVE2_HANDOFF.md, INFERENCE_LEDGER.md,
  COMMON_BRIEF_W2.md, P-1/{H6_ADVERSARIAL.md, DEFECT_PATTERNS.md, decay_plant*},
  W2-*/REPORT.md, W2-AG/STRANGE_REGISTER.md, W2-W/null_placement.csv,
  W2-AB/PREREG_PTE_C2_DRAFT.md.
- research/c4/R-STAT_FINAL_NOTES.md -- Cosmos C4 statistics review notes.
- calibration/LEDGER.md -- 16 self-correction rows 09-24..27.
- External: roles/Atlas/inference_harvest_2026-09-30/workers/digests/ananke_pte_tyche.md
  (Atlas digest, pre-harvest snapshot); programs/selective_irreversibility/
  {RULINGS,EXPERIMENTS,FALSIFIERS}.md (Ananke's role in SI program).

## 17. Journals/TODOs/backlogs/pivots/abandoned branches

- journal/: one file only (2026-09-24.md): creation, orientation survey (overlap map,
  three recurring failure shapes fleet-wide), build log, preflight catches, C1 progress
  and done. No journal entries after 09-25 were written; later state lives in
  WORK_STATE.json, STATUS.md, RESUME.md, syntheses and the Wave-2 ledger [IMPL].
- TODO.md (currency 09-25): PTE-C2 prereg, answer reviews, FLIP zero-comm twin rerun,
  release-guard TypeError hardening -- none done at tree [CLAIM].
- BACKLOG_H0H5.md: ANANKE-04..27 (report.py, atlas export, fused kernel, port-resolved
  arrival, TTL forwarding, packet-carried code, deaf-fraction study, novelty archive
  instead of shaping, sealed holdouts from another seat, RunPod scale probe,
  symmetric decay, multi-episode inheritance, distributed-control family, causal-edge
  tracing, merge decision with Ensorain, PTE-C2 "weather"). Of the v2-substrate items
  (09-12, 19, 21, 22) none was built [IMPL absence in prometheus/ananke].
- research/BACKLOG_V2.md -- canonical backlog with tiers (top tier T-REACH-GAP);
  research/THREADS.md -- thr-/C-/E- id map; WORK_STATE lists OPEN threads T-REACH-GAP,
  T-RET-SEL, T-CT-3', T-WJ-1/2, T-H3; PARKED T-REDISCOVER (latch confound would make a
  null uninformative) [CLAIM].
- RESUME.md SUPERSEDED block: operator questions Q1-Q4 (merge with Ensorain; C1b
  before C2; RunPod $10 ceiling; review as gate) -- answered 09-25/26 by HOLD, SI01
  directive and the C1b release [CLAIM].
- Pivots: (1) charter (09-24) phase map of communication physics -> (2) adjudicate
  unexpected mechanisms (C1b) -> (3) mechanism-lens/instrument research arcs (no new
  campaigns under MWO) -> (4) inference-only audit of own instrument (harvest,
  Wave 2). Why: HOLD pending review, steward/MWO compute limits, and the seat's own
  discovery that C1 rulers could not discriminate [CLAIM].
- Abandoned/unbuilt: PTE-C2 "weather" (three load axes), PTE-SI01 campaign, RunPod
  leg, fused kernel, v2 dials; W2-AE audit package; MAJ forward placement fix (W2-A1
  P3 not landed; envs.py:213 still _pick_at(g, M[a], env.d, ...)) [IMPL].
- Branch: ananke/base-role-adopt-2026-09-24 has no commits off main (Atlas digest)
  [CLAIM].

## 18. Dependencies on other engines and seats

- Code: torch (CUDA graphs), numpy only; no dependency on other Prometheus engines in
  prometheus/ananke [IMPL imports]. launch.py uses Windows schtasks; research/lease.py
  is a Fabric lease frontend (8370083ae); deposit.py and kind_audit.py are seat-local.
- Seats: Ensorain (charter overlap; lessons WTP-01/02 imported as design rules, e.g.
  no-op guard, fixed-reference denominators, necessity preflight -- cited as "Ensorain
  I4/R1/R2" in assays.py/plants.py); Aether (RunPod pattern, oracle discipline; W-C
  comparison); Aporia/Cyclops (SI01 stewards; Aporia re-derived D-A defect #640 and
  found release-guard defect #696); Harmonia (#1037/#1045 audits); Cosmos (C4 review;
  atlas_export form); Nestor (schtasks watchdog pattern; X-1/X-2 incidents incl. an
  external kill of a Wave-2 worker process); Atlas (locator); Kairos/Elenchus/Nemesis
  (requested reviewers; no reply).
- Program: Selective-Irreversibility program (programs/selective_irreversibility/)
  listed PTE-C1/C1b/SI01 among its experiments and the HOLD/release rulings.

## 19. Scaling limitations

- int32 mailbox headroom: n_sites * max(fanout, R) * 2 * 32767 < 2^31 caps N*fanout
  (~32k at fanout 1) [IMPL physics.validate].
- Python loop over L instructions per tick, each building a [16,B,N] candidate stack:
  memory and time scale with 16*B*N per instruction; launch-bound at 11-21M site-
  updates/s on Windows without Triton (ANANKE-09 fused kernel never built) [IMPL;
  CLAIM].
- Episodes are short (<= 360 ticks) and tasks have 1-bit outputs at one actuator; the
  task interface (one read site, sparse sense schedule) does not scale to multi-output
  or long-horizon problems without new env code [IMPL].
- GA budget per cell is fixed and small; champions are tail draws (0/4 self-
  reproduction in W-H); B2 seeds shared across families; per-cell SIGNAL is one search
  draw [CLAIM].
- Statistics: 32 mirror pairs per held-out evaluation; percentile bootstrap undercovers;
  swap certificates need P >= 32 [CLAIM W2-H, W-U].
- Single host, single GPU; RunPod path designed but never used.

## 20. Lens potential for Phase 3

Lens A: "channel-state lens" on PTE (the seat's own framing, PTE_ENGINE_CARD)
- Substrate observed: deterministic integer message-passing among identical
  programs with lossy, delayed, superposing packets.
- Organisms: homogeneous straight-line register laws (G <= 4, L <= 16) evolved by GA
  or hand-written plants.
- Worlds: five 1-bit task families on small graphs (N 64-144; probes to 2304).
- Pressures: task accuracy with declared twin-contrast shaping; physics dials (loss,
  latency, caps, decay, asynchrony, energy).
- Phenomenon family: where information lives and moves (site vs channel vs joint),
  transport, delay-line memory, presence vs content codes, receiver-operator effects.
- Current resolving mechanism: exact mirror-pair counterfactuals (twins share every
  exogenous draw), per-carrier resets/flushes/swaps, plants as positive controls,
  ceiling bounds; bit-exact CPU oracle.
- Likely resolution ceiling: mechanisms of a few instructions on one or two physics
  points; the tasks cannot demand more than small FSM control; most mechanism
  descriptions come from one physics lineage (86fc0105).
- Noise sources: search-seed lottery, rule-mosaic initial rules, latency-jitter draw on
  the first broadcast, threshold seed-sensitivity of swap verdicts, P = 32 statistics.
- Architectural limit: no source identity, no TTL/multi-hop auto-forward, no
  packet-carried code, no reproduction or individuals, write-free environment,
  one actuator, straight-line programs.
- Reusable: the engine core (deterministic counter-hash physics, CUDA-graph tick,
  Controls switches that touch only their own stream, digest/no-op guards), the
  independent oracle + conformance tests, mirror-pair design for exact
  counterfactuals, lens_swap / swap_rel / inference.py, and the Wave-2 instrument-
  certification ideas (attainability, must-fail adversaries, light-cone ceilings,
  plants inside the genome space).
- Toy-grade: the five task families (12-16 binary trials, one actuator), the GA
  (pop 96 x 36), the C1 label set and boundary criterion, the mirror-forced controls.
- Unknown: whether any per-trial multi-hop relay, parity, FLIP inference or selective
  retention is search-reachable at larger budgets / without shaping / with novelty
  search; whether economy is a real physics boundary (W2-AH incomplete); whether the
  substrate exhibits anything beyond what a 10-line hand design gives.

Lens B: pre-freeze instrument certification (Wave-2 stack)
- Phenomenon family: ruler/control discriminability (meta-instrument).
- Mechanism: attainability proofs, null/adversary/plant scoring, mutation gates,
  identity audits, kind audits on provenance.
- Limit: built and tested by the same seat in one night against its own historical
  campaign; not packaged (W2-AE INCOMPLETE); not exercised on a fresh campaign.

## 21. Open questions / coverage gaps

What this crawl read directly: RESPONSIBILITIES, RESUME, STATUS, TODO, BACKLOG_H0H5,
WORK_STATE (head), journal/2026-09-24, calibration/LEDGER, superseded/RESPONSIBILITIES
(head), prompts (charter head, creation, SI01 directive heads + reply head, C1b
release, harvest and Wave-2 directive heads); pte/DESIGN, PREREG_PTE_C1, C1_REPORT,
C1_ERRATA (full), c1_a0/A0_FINDINGS, c1b REVIEW_PACKET and CORRECTIONS; code
engine.py, physics.py, topology.py, rng.py, envs.py, search.py, assays.py,
plants.py (first 120 lines), campaign.py (config, classify, causal_label,
anomaly_flags, run_cell), headers/def lists of all other modules, test_conformance
head; research/PTE_ENGINE_CARD (first 80 lines), harvest/PTE_CAUSAL_AUDIT (head),
wave2 handoff, P-1/DEFECT_PATTERNS, P-1/H6_ADVERSARIAL (s0-2, s12-15), W2-AI REPORT
(full); git log for both trees; zero-cost row counts of c1_rows and c1b_rows; Atlas
digest head; programs/selective_irreversibility grep hits.

Read via two read-only sub-readers (summaries, not re-verified line by line): workers
W-A..W-Z reports, arc syntheses, swap-audit corrections, instruments, designed echoes,
joint carrier; harvest H-IMPL/H-SCI/H-INST/H-CHK/H-PLANT, Wave-2 ledger and most W2-*
entries (many W2 reports were taken from the principal's ledger, not read).

Not read: PREREG_PTE_C1b body; oracle.py body; c1b.py/c1b_run.py bodies; lens*.py and
swap_rel.py bodies beyond headers; report.py; PRIOR_ART body; BACKLOG_V2 in full;
CROSS_ENGINE_THREADS; THREADS.md; handoffs; worker PLAN/LOG files; out/ data files
(beyond the AL tally by a sub-reader); scratch patched engine copies (not diffed file
by file); W2-AD/AE/AF/AH/AJ/AK partial outputs; the SI01 directive body beyond
headings; MIGRATION_REPORT_MWO-0002.json; comms bodies; the C4 R-STAT work.

Open questions:
- Is any per-trial (resettable) multi-hop relay reachable by search at all? (W2-AL
  latch prevalence INCOMPLETE.)
- Is the economy boundary physics (W2-AH INCOMPLETE)?
- Would C1 results change with shaping off (C2 arm W0 never run)?
- How much of the mechanism catalogue survives off the 86fc0105 physics lineage?
- Was the oracle meaningfully independent (same model family, separate context)?
- 250/454 NULLs remain "open": search failure or no adequate plant yet?
- No independent external review of any Ananke claim exists in the record.
- Holdout/secret paths touched: none.
