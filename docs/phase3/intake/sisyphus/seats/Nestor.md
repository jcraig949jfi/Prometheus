# Seat dossier: Nestor

- Crawler: Sisyphus (forensic crawl worker), crawl date 2026-10-01
- Base SHA of worktree: 19299e06b (F:/Prometheus-worktrees/sisyphus-base-role, = origin/main at crawl time)
- Epistemic tags used inline: [IMPL] implementation fact; [INTENT] design intent; [HIST] historical claim;
  [RESULT-UNVERIFIED] reported result not re-established here; [CORRECTION] later correction/contradiction;
  [CODE-INFERRED] capability inferred from code; [UNKNOWN] unknown/ambiguous.
- Nothing in this dossier was re-run. Every number is a recorded number unless tagged [IMPL].

## Coverage statement

Read directly (by me or by read-only helper passes whose notes I spot-checked against source):
- roles/Nestor/RESPONSIBILITIES.md, STATUS.md, FINDINGS.md (all 644 lines), EXPERIMENT_GRAPH.jsonl (92 ids,
  last-line-wins summary computed here), journal/2026-09-14.md, WORK_STATE.json, LEASES.jsonl, calibration/LEDGER.md,
  PROMETHEUS_SUCCESS_CONTRACT.md, the prompts/ directives 2026-09-14 .. 2026-09-30.
- sidequests/graphworld/ review packets R1-R8, SWARM*.md, POSTMORTEM, FRAMEWORK_WRITEUP, R8_* files; primordial/core,
  primordial/qd/e4_run.py, primordial/brain/{genomes,tt_policy,plastic}.py, primordial/soup/b2/graphworld.py,
  primordial/metric/*; SerendipityFoundry/worldfoundry/wforge/world.py (reference world).
- campaigns/cw01-2026-09-17/ CAMPAIGN_STATE.json, DEFECTS.jsonl, lib/, experiment world_e0N.py + PREREG/DISPOSITION
  files, loop/LOOP_RULES.md, loop/CYCLE_REPORT_* and BOUNDARY_REPORT_CYCLE5; proteus/foundry/vm.py (substrate of the
  loop cycles).
- campaigns/z80atlas-2026-09-19/ (z8.py, world.py, grammar.py, tasks.py, PREREGISTRATION.md, CALIBRATION.json,
  DEFECTS.md, observatory PACKET/ADJUDICATION, REPORT rev 2), z80atlas-verify-2026-09-22/ (z8.py, world.py, p11.py,
  P11_SPEC.md, PREFREEZE_STOP, C9 outcome/addendum), z80atlas-forensics-2026-09-23/ (S1A_FUNNEL, H4_AUTOPSY,
  S1C_P11_REASSAY), c9x-explore-2026-09-24/CAMPAIGN_REPORT.md and run scripts for the c_* confirms.
- campaigns npe-w1 / npe-p2 / npe-arc3 / npe-frontier reports, syntheses and verdicts; ancestry-replay-2026-09-28
  (GATES, INCIDENT_RUN3, PRODUCTION_RUN1_INVALIDATED, CVTR_RECONCILIATION, review READMEs).
- inference_harvest_2026-09-30/ handoff + theories; inference_saturation_wave2/ handoff, INFERENCE_LEDGER headers,
  W2-8, W2-9, W2-15, W2-18, W2-25, W2-35, W2-36 reports.
- Cross-seat: roles/Artemis/challenge/cvtr_nestor/RESULT.md, Artemis p11 challenge, Odysseus recert (via FINDINGS
  citations), Atlas digests (roles/Atlas/inference_harvest_2026-09-30/workers/digests/nestor_npe.md,
  ATLAS_CROSS_ENGINE_SYNTHESIS, ATLAS_BURIED_SIGNALS_AND_RESIDUALS, ATLAS_CONTRADICTIONS_AND_NATURAL_EXPERIMENTS,
  roles/Atlas/SOURCES.md).

NOT read, and why:
- Anything under a path containing "holdout" or "nestor_secrets" (hard rule). C3_HOLDOUT_D_REPORT.md was read only
  for custody/status; it concerns a Cosmos diffusion-channel world, not a Nestor engine.
- Per-run result JSONs (thousands of files under c_atomic/results etc.), git-ignored per-run replays, the M1-local
  off-repo stores (C:/Users/jcrai/lab/pm-data) -- not inspected; numbers come from verdict/summary files.
- The graphworld per-lane journals (~5,800 lines) line by line; the CW01 cycle-8 report (169 KB) in full; P2
  BACKLOG.md (40 threads) and ARC3 work packages in detail; about half of the 56 wave-2 worker directories.
- Unmerged early branches bld-g/bld-q/bld-h/design-review (graphworld-era build lanes, no later relevance found).

---

## 1. Identity and purpose

- Canonical name: Nestor. Created 2026-09-14 by operator chat directive ("You are a new role named Nestor ... create a
  base role") [HIST: roles/Nestor/journal/2026-09-14.md; commit 0100d36cd]. Charter initially PENDING.
- Historical aliases / instance tags: Nestor-A..E[m1-xxxxxxxx] lane instances during the graphworld swarm
  (e.g. Nestor-A[m1-918ab2b0], Nestor-B[m1-5b2d34d4], Nestor-C[m1-b36900c1], Nestor-E[m1-f333105f]); later
  Nestor[m1-7438ee6f] etc. Builder lanes F/G/H/P/Q/T/U/W and predictor lane R in later swarm rounds.
  "NPE" (Nestor Primordial Engine) is a name with two referents (see section 2) [IMPL: atlas/harvest/npe.py header;
  archaeon/causal_lens/adapters/npe.py header].
- Host: M1 (SKULLPORT), heavy-capability boot [HIST: journal 2026-09-14]. Worktrees F:/Prometheus-worktrees/nestor-*
  (about 80 exist on disk: graphworld rounds r2-r8, lanes, s1-forensics, s4v2, g2rerun, c3-d, d2v*, arch4).
- Charter history (pivots, details in section 11):
  1. 09-14 seat created, then the same day: graphworld / "Primordial Machine" swarm side quest (5 lanes; operator
     directive committed verbatim, prompts/2026-09-14_graphworld_swarm/).
  2. 09-17 CW01 campaign (10 preregistered experiments e01-e10; ~e09 reached).
  3. 09-18 operator "nothing scientific is ever killed" loop (loop cycles 1-8) + T-ARCH4/T-ARCH5 Archaeon
     reactivation.
  4. 09-19 72 h autonomous Z80 x Atlas campaign on its own Z8 substrate (frozen grammar 570c8037).
  5. 09-22 Cycle-9 verification/repair; 09-23 S1-S4 forensic pass; HARD STOP before C9 freeze on C9-D14.
  6. 09-24 promotion directive: Nestor becomes a "budgeted autonomous scientific loop" (RESPONSIBILITIES s2;
     prompts/2026-09-24_promotion_autonomous_loop/DIRECTIVE_VERBATIM.md). 48 h window, 12 workers, 20% reserve.
  7. 09-26 "direct operator control": Aporia/Cyclops stewards reduced to advisory; SI (selective irreversibility)
     framing of Nestor results withdrawn (prompts/2026-09-26_direct_operator_control/).
  8. 09-26 .. 09-28 NPE windows W1 (donor discovery), P2 (endogenous heredity), ARC3 (internalization portfolio).
  9. 09-28 post-ARC3: Nestor becomes the independent NPE-side reconstruction/tracing seat for Archaeon's ancestry
     replay (prompts/2026-09-28_post_arc3_directive/).
  10. 09-28/29 fleet work-order model (MWO-0001..0004); 09-30 CWO with Aporia as fleet scheduler; NPE frontier
      (X-MAT-INTERNALIZE executed; X-TASK-GATE frozen, never run).
  11. 09-30 / 10-01 inference harvest and "inference saturation wave 2": LLM-reasoning passes over existing NPE data
      with bounded static assays.
- Current/terminal role: READY under MWO-0004 + CWO-C, no running work [HIST: WORK_STATE.json]. The seat contract
  (RESPONSIBILITIES s1) [INTENT]: "budgeted, autonomous, long-horizon campaigns in computational artificial life and
  algorithm search ... accountable for the evidence being worth less than it first appears wherever that is true."
- Relationships: consumer of Archaeon/Proteus VM (CW01 loop cycles, T-ARCH4); peer/adversary of Bellerophon (BEE:
  parallel Z80 engine from the same directive; BEE REPL-01 attempted an independent rebuild of Nestor's
  C-A3-INTERNALIZE); audited by Artemis (P-11 painter challenge, CVT-R), Odysseus (recertification #803, holdout
  firewall audits), Harmonia (#1057 audit of X-MAT), Aporia (stewardship then fleet scheduling); delegation for Cosmos
  (C3 holdout D custody); instrument for Archaeon (ancestry replay T-003).

## 2. Engine / system inventory

Nestor did not have one engine. Five distinct substrates were built or materially used:

### 2.1 Primordial Machine ("primordial/", graphworld swarm), 09-14 .. 09-17
- Paths: primordial/ (core, fabric, bus, brain, cohorts, ledger, lingua, metric, qd, soup ...; 789 tracked files),
  roles/Nestor/sidequests/graphworld/. Added a901ba0c9 (09-14); imported into main only by merge b10161316
  (2026-09-22, "Merge nestor/sidequest-graphworld-2026-09-14 into main", parents 02ffd7603 + 3b407946e) [IMPL: git].
  The commit message mentions CW01/Z80 only, not primordial [IMPL].
- Purpose [INTENT: SWARM.md]: a multi-lane "Primordial Machine": A conductor/fabric, B soup (worlds and kernels),
  C brain (tensor brains), D lingua (metered channels), E selection (QD/MAP-Elites). Target CHIMERA-0: E evolves C's
  brains inside B's batched world with D's channel, events through A's fabric, trace-hash equal to a wforge replay.
  CHIMERA-0 was never assembled [HIST: REVIEW_PACKET_ROUND1].
- Key modules [IMPL]: primordial/core/contract.py (World/Brain/Channel/Genome protocols; receipt STATUSES
  PASS/FAIL/KILL/NULL/INDETERMINATE; board_eligible), primordial/qd/e4_run.py (MAP-Elites over Encounter; Redis Lua
  archive), primordial/brain/genomes.py, tt_policy.py, plastic.py (tensor-train policies), cohorts/b/b1_qlinear.py
  (int4 linear brain), primordial/metric/* (floors, world screen, EVIDENCE_N sample rule),
  primordial/soup/b2/graphworld.py (GraphBLAS/FalkorDB predator-prey equivalence toy).
- Reference world: SerendipityFoundry/worldfoundry/wforge/world.py "Encounter" (not Nestor's code).
- Infrastructure [HIST: SWARM.md s1]: Redis 8.6.3 + FalkorDB 4.20.4 container gw-substrate on 127.0.0.1:6390, Redis
  Streams bus, JSONL receipts ledger plus committed rows.
- Scale: R1 alone 49 receipts / 132 commits in one day; 2,000+ commits touch primordial/ [IMPL: git log count].
- Note: Atlas SOURCES.md (last touched 09-19) says "primordial/ is NOT on origin/main". That was true then and is
  false now (since b10161316) -- an Atlas staleness, not a contradiction of fact [CORRECTION of Atlas].

### 2.2 CW01 bespoke worlds (campaigns/cw01-2026-09-17/), 09-17 .. 09-18
- One in-process numpy world per experiment (experiments/cw01-e0N/world_e0N.py), job contract run by lib/localrun.py
  without Redis; seeds from attempt_id (lib/seeds.py) [IMPL].
- lib/ is infrastructure born from defects: guardproof (a guard is not evidence until seen refusing; D043),
  infometrics (MI only vs shuffled null), learnability (gate before spending budget), lineage, residue,
  recordsafety, repopath, writerlock [IMPL].
- e08/e09 instead used the real primordial organism (tt_digits TT policy) in wforge world w13 [IMPL: e08
  world_e08.py docstring].

### 2.3 Archaeon/Proteus tape VM as used by the CW01 loop and T-ARCH4/5, 09-18 .. 09-19
- proteus/foundry/vm.py (not Nestor's code): bounded tape machine, genome copied onto the tape and executed in place,
  persist policies none/regs/tape/all, total interpreter (opcode mod table size; no fault state) [IMPL; HIST
  archaeon/campaign4/DECISIONS.md D4-002]. Worlds from archaeon/wse/worlds.py (PUT/ASK/NOISE episodes; families W0,
  W1_d delay, W2_K2). Loop driver scripts live under cw01-2026-09-17/experiments/cw01-loopN|arch4/P-*/.

### 2.4 Nestor Z8 engine ("Z80 x Atlas" E-NES; later "NPE"), 09-19 .. 09-30
- Paths: roles/Nestor/campaigns/z80atlas-2026-09-19/{z8.py, world.py, grammar.py, tasks.py, runner, observatory/},
  then frozen copies in z80atlas-verify-2026-09-22/ (world.py 1,439 lines, z8.py, z8taint.py, p11.py) and
  z80atlas-forensics-2026-09-23/substrate/. Later experiments subclass the frozen verify engine from their own
  directories (c9x-explore-2026-09-24/*, npe-*/); roles/Nestor/lib/reset_axis.py adds the register-reset axis
  (607023bab).
- IMPORTANT [IMPL, verified by git grep]: no Nestor engine file imports prometheus.z80atlas. Nestor's Z8 engine and
  Bellerophon's prometheus/z80atlas ("BEE") are separate code bases built the same day under one directive; a third
  (archaeon/z80atlas) also exists. Atlas calls these the "Z80 triplet" and notes that "Z80" names three different
  ISAs [HIST: ATLAS_CONTRADICTIONS s0]. The crawl brief's grouping of prometheus/z80atlas under Nestor is a
  [CORRECTION]: that package is Bellerophon's (see Bellerophon dossier); only two late Nestor inference-ledger notes
  mention it.
- "NPE" referent shift [IMPL]: atlas/harvest/npe.py and prometheus/toolbox/backends/npe.py use NPE = primordial
  (graphworld-era); from 09-26 Nestor's own documents use NPE = the Cycle-9 Z8 engine
  (archaeon/causal_lens/adapters/npe.py: "NPE adapter (Nestor Z80xAtlas, Cycle-9 engine ...)"). Documents conflate
  the two [UNKNOWN whether Atlas's index reconciles them].
- Execution: Python multiprocessing pools (6-12 workers), launched by one-shot schtasks wrappers, resumable runners
  (skip finished runs), host lease files ~/ananke_runs/leases/<res>.json from 09-28 [HIST].
- Scale: 72 h campaign 23,471 runs / 20,638 families; C9 1,200 runs; c9x CONFIRMs 36-240 fresh seeds per arm; W1
  ~1,000 world runs ~11 h pool; X-MAT 26 replays ~28,000 CPU-s [HIST].

### 2.5 Ancestry-replay shadow tracer (campaigns/ancestry-replay-2026-09-28/tracer/), 09-28 .. 09-29
- z8shadow.py / observe.py: independent Z8 shadow tracer asserted value-identical to the frozen VM on every one of
  256,000 interactions per record; exports births and a seeded 1% interaction sample; s4_run.py / s4v2.py per-birth
  flip tests (perturb a source locus, see whether the child locus changes); fixture pack (npe_fixtures.py,
  check_fixtures.py; 23 fixtures, 451 expectations), selftests (guards, pdom, shadow) [IMPL file list; HIST results].

### 2.6 Measurement libraries
- P-11 randomized-victim causal-copy assay (z80atlas-verify-2026-09-22/p11.py, P11_SPEC.md, committed f28e5fd72
  before the 1,031 were inspected) [IMPL].
- z8taint.py / dense_taint.py: per-byte material-provenance taint (tags D0, PRE, MKL, MKN, MUT) [IMPL]; claimed
  bit-identical to z8.run [RESULT-UNVERIFIED].
- report_audit.py + test_report_audit.py (12 reinjected defects), verify_freeze, graph.py (experiment graph CLI)
  [IMPL].

## 3. Architecture (code level)

### 3.1 Primordial / graphworld
- World [IMPL: wforge/world.py; primordial/soup/b1/common.py:25]: "Encounter" -- integer register bank mod 2^16,
  linear transition maps, optional regime switch, delay queue, corruption; slots (players) emit action vectors of A
  ints that add magnitude to target registers (action read mod 8; 0 = abstain); each slot holds conserved charge
  with metabolic and action costs; YIELD from a hidden window predicate on a register, contested; observation = a
  seeded permutation of registers plus a charge bucket; xorshift64* RNG; sha256 trace hash per tick. A world is a
  seed: make_world(gen_seed) -> "w<seed>". Train/held splits TRAIN8 9100-9107, TRAIN128 9100-9227, HELD64
  30000-30063 [HIST].
- Organism/genome [IMPL: qd/e4_run.py; brain/*]: (a) open-loop action tensor [T,S,W] in 0..15 with per-element
  mutation 2/n and row zero/fill; (b) tensor-train policy over hex digits of a uint16 observation (alpha, G[d,16,r,r],
  Wo); (c) rank-adaptive plastic TT; (d) QLin int4 linear brain with nibble codebook.
- Search: MAP-Elites (33x33 descriptor grid of abstain fraction x magnitude) in a Redis Lua archive, hill climbers,
  GA [IMPL]. Fitness = summed clipped final charge over seeds [INTENT/HIST].
- Rulers: floors (abstain, best_constant, uniform_random_median, input_invariant_learner); world screen
  (SURVIVED/HELD/CULLED/PENDING); EVIDENCE_N_v1 (32 runs / 4 RNG families / 8 per family) [IMPL: metric/].
- Learning: plastic TT "adapt" exists; communication: metered channel D (lingua/channel.lua per-bit settlement)
  [IMPL]. No reproduction physics: organisms are search candidates, not self-reproducers.

### 3.2 Nestor Z8 engine (E-NES / NPE)
- VM [IMPL: z80atlas-2026-09-19/z8.py; z80atlas-verify-2026-09-22/z8.py]: byte-addressable Z80-flavoured subset with
  real Z80 encodings for LD r,r', ALU A,r, INC/DEC, LD r,n, 16-bit LD rr,nn, indirect loads, JR/JP with conditions,
  immediate ALU, IN/OUT; every other byte a 1-byte NOP; HALT 0x76. ED-prefixed WORLD OPS: ED30 ALLOC, ED31 BIRTH,
  ED32 SELF (HL = own base, BC = own length), ED33 GETPC, ED34 SENSE, ED35 SPLIT, EDB0 LDIR, EDB8 LDDR (1 step per
  byte, per-byte copy error at the mutation rate). An ops mask (grammar factors self_location, copy_primitive,
  world_ops) decides which world ops exist; a disabled op decodes as a 2-byte no-op. Write sandbox policies OWN /
  ARENA (pair tape) / FREE. Registers B C D E H L (HL) A; fresh registers are all zero
  (`r = [0] * 8 if ctx.regs is None`, z8.py:171 in the verify copy) [IMPL, checked]. Registers, flags and PC persist
  across slices: organisms are continuing processes [IMPL].
- World [IMPL: world.py]: arena of fixed slots (slot = 2L bytes, n_slots = 2 x pop_cap). Representations Z8_64, Z8_32,
  Z8_SHARED/SEPARATED (96 B), Z8_SLOTTED (64 B, slot-aligned mutation). World types PAIR_TAPE, SOUP_MEM, GRID (torus,
  ALLOC limited to neighbours), GRAPH (preferential attachment m=2). Tiers S/M/L: pop 128/256/384, 600/2000/4000
  epochs, slice 220/300/360 steps, validation every 6/10/12 epochs.
- Reproduction [IMPL]:
  - Non-pair (ENDOGENOUS_COPY / PARTIAL / CONSTRUCTIVE / OVERWRITE): organism must ALLOC (world snapshots the slot
    pre-image), write, then BIRTH; wrote_bytes = bytes differing from the pre-image; child mutated at birth.
  - PAIR_EXECUTION on PAIR_TAPE (world.py `_pair_epoch`, line 572 in the 09-19 copy): shuffled pairs concatenated on
    a 2L tape (power of two, wraps); each half runs one slice from its own start under ARENA policy with CARRIED
    registers; both halves written back and mutated every epoch. A half that is overwritten by the other above
    threshold is "renamed in place" (victim keeps its Org object, including registers, with new oid and pid = donor)
    [IMPL per late helper read of verify world.py:768-890].
  - EXTERNAL: the manager copies ~5%/epoch with tournament-of-3 on competence.
- Mutation [IMPL]: opcode bytes uniform replacement; operand bytes 45% +/-8, 45% bit flip, 10% uniform; STRUCTURAL 50%
  indel; rates 0.002/0.01/0.04. RECOMBINATION axis = with p 0.2 a one-point splice with a random living organism
  inside `_mutate` (world.py:291-360 in the 09-19 copy) -- the "splice". [CORRECTION, ARC3 delegate] the late 7ae3 /
  ffa6 cells use the OPERAND operator with no indels; in 7ae3 opcode bytes never mutate; [CORRECTION, W2-8 D4]
  Z8_SLOTTED ignores the operator so 87% of ffa6 "OPERAND" mutations hit opcodes (~8x supply).
- Selection [IMPL]: reaper (oldest / lowest energy / QD-protected), task gating at ALLOC, energy pools
  (RESOURCE_GATED, COMPETITION, METABOLIC), PREDATION, TAPE_COST, EXEC_TIME_COST, NOVELTY, QD. [CORRECTION, W2-8 D3]
  on the pair tape 7 of 12 pressure levels give a byte-identical arena; in the late 7ae3/ffa6 cells "nothing dies:
  the only selection is being overwritten by a copy" (FINDINGS ARC3 correction).
- Energy [IMPL]: endogenous newborn starts at energy 0; energy-economy pressures cap the slice length at energy
  (root of the "newborn starvation" wall, E-7).
- Tasks [IMPL: tasks.py]: cycle-8 conditional task. Inputs [v, r] (or [v, key, r] under FORCED_READ); answer = base
  if r = 0 else T(base) with T in XOR1/ADD1 (incremental) or XOR15/XOR5A/ADD37 (atomic); scored on the first OUT byte
  over 8 episodes in a scratch arena with world ops disabled; NEUTRAL_BRIDGE 0.5 credit for echoing base; held-out
  via a disjoint seed stream; crossing threshold 0.90 held-out. Validation is cached by genome hash and children
  inherit parent competence until the next validation pass [IMPL]; [CORRECTION, W2-8 D1] the cache is keyed on genome
  bytes only, so cross-niche scores leak (recorded held 1.0 vs true 0.25 in a constructed case).
- Seeding [IMPL]: SEEDED_* fills the WHOLE initial population with a hand program padded with random bytes; the
  primitive replicator is SELF; ALLOC; JRZ; HALT; LDIR; SELF; BIRTH; HALT.
- Grammar 570c8037ccf4f86d [IMPL]: 16 factors (~4.3e9 cells): world, environment, representation, reproduction,
  self_location, copy_primitive, pressure, structure, task_transform, read_order, bridge, seeding, mutation
  operator/locality/rate, atlas_axis; declarative constraints (PAIR_TAPE requires PAIR_EXECUTION or EXTERNAL;
  EXPLICIT_FITNESS requires EXTERNAL; ...); one-factor CONTROL_AXES; tier deliberately outside the cell; hash-gated
  start/resume. Thresholds, interest weights and stage rules were PROSE-declared, not hashed
  [IMPL: PREREGISTRATION.md "PROSE DECLARED"].
- Later deformations (each a Runner subclass in an experiment dir) [IMPL per CAMPAIGN_REPORT and run scripts]:
  per-epoch in-place search for non-pair physics; "free self-location" (HL/BC preset every slice); half-energy
  transfer at birth; one-byte aliases for ALLOC/LDIR/BIRTH (X-DENSE-OPS) and later for LDIR/LDDR only (0xE5/0xE7,
  DENSE VM, x_dd_dense_copy/run_dc.py); splice off; ATOMIC write-back (c_atomic/run_cat.py: a half keeps new contents
  only if an accepted replication re-identified it as a child, otherwise restored then mutated); STATELESS execution
  (regs None before every execution); register-reset world axis CARRIED (default) / ZERO / CONST 0x5A / RANDOM /
  SCHEDULE (lib/reset_axis.py).
- Lineage/provenance: 72 h predecessor kept only the last 400 lineage events (thinned to 50 under disk pressure),
  stored only the parent niche at birth, counted migrations without logging [HIST: FINDINGS A-5, C-1 P-1]. Repairs
  P-1/P-2 added an ancestry certificate and causal-only depth; anc marker (slot lineage); z8taint material taint
  [IMPL].
- Experimental control: frozen grammar + calibration gate (10 checks) + one-factor matched pairs (72 h); later
  inner experiments with PREREG + protocol hash + verify_freeze + fresh seeds + one-sided Fisher / LRT; graph nodes
  with lane EXPLORE / CONFIRM / FORENSIC [IMPL/INTENT].
- Design vs implementation disagreements found by later passes (all [CORRECTION]): P-8 initial population all in
  niche 0; P-9 COEVO_ENV bypasses the reservoir easy niche; P-10 ENV_MIG gate can never fire; C9-D16 H1 gate never
  plumbed from world to task; C9-D24 implant arms not paired (RANDOM_MATCHED == in situ; ACTUAL shifts the RNG
  stream) although comments said "B and C share the same background"; W2-8 D5 both critical anticheat guards can
  never fire (`voided` always False); W2-8 D2 C9-H3 arms A == B in 64/64 bundles.

### 3.3 CW01 worlds (bespoke)
- e01-e07: small numpy economic worlds; organisms are short real-valued policy vectors or linear/recurrent nets
  (5 genes, 9 genes, 82-param linear activation, two 5-param policies, 8-gene inclusion vector, TREE/TAPE programs,
  464-param linear recurrent net). GA with tournament selection. Docstrings themselves say "not a rich program"
  [IMPL].

## 4. World capability audit

| engine | state size | spatial | observability | stochastic | actions | horizon | agents/ecology | change | open-endedness |
|---|---|---|---|---|---|---|---|---|---|
| wforge Encounter (graphworld) | small integer register bank, a few slots | no | partial (permuted registers + charge bucket) | seeded, delays/corruption | action vector mod 8 per slot | T ticks per episode | 2+ slots share a bank, contested yield | regime switch option | none: a world is a seed; the screen found 1/74 cells where any learner beat the abstain floor |
| CW01 e01-e07 worlds | tens of scalars | no | full or designed-partial | seeded | continuous genes | lifetimes of a few episodes | single population, GA | scripted "weather" (e07) | none; hand-built per question |
| Proteus VM worlds (loop cycles) | tape + 32-bit channels | no | episode words | NOISE family | instruction programs | PUT/ASK delay episodes | single lineage populations | delay families | none; tiny PUT/ASK tasks |
| Z8 engine (72 h, C9, NPE) | arena up to 384 orgs x 2 x 128 B (rounded to 2^17 B) | slots; GRID torus / GRAPH options; PAIR_TAPE is non-spatial pairing | an organism can read the whole arena (ARENA/FREE) and SENSE one byte | seeded copy errors, mutation, partner shuffle | full instruction set + world ops | 600-4000 epochs | up to 384 organisms, pairwise interaction, overwrite competition, energy pools, 4 niches, reservoir, migration | SHIFT/COEVO_ENV environments | bounded: genome length fixed by slot, one fixed task family (8-episode conditional), no new tasks |

Explicit toy limits:
- The graphworld Encounter world is a tiny integer economy; R3 showed a zero-byte ALWAYS-ABSTAIN policy beat every
  baseline in 28/28 Clause A cells, and the R7 74-cell screen admitted one world x pressure (w13 train128_held64)
  plus one L1 neighbour in R8 [HIST]. This is a near-degenerate world family for learning.
- CW01 worlds are single-question toys; e09's own reconciliation records that the real organism's only act is "one
  3-bit nudge into one register per tick" (primordial/soup/b1/np_world.py:92-102 quoted in
  cw01-e09/SUBSTRATE_RECONCILE.md; D068) [HIST quoting code].
- The Z8 late cells (7ae3, ffa6) are fixed 128-byte pair-tape worlds of L = 64 genomes with no deaths except by
  overwrite and (per W2-8 D3) mostly inert pressures; the task is a single conditional byte transform. The world is
  rich in instruction-level physics but has essentially no environmental task diversity, no delayed consequences
  beyond a slice, and no environment generation.
- Transfer between worlds: only "transplant" experiments (implant a genome into foreign cells; X-DONOR-SWAP,
  X-RUNAWAY-TRANSPLANT), which found competence is a property of genome x cell [RESULT-UNVERIFIED].

## 5. Organism capability audit

- Graphworld organisms: open-loop action tensors or small TT / int4 policies; reactive mapping observation -> action
  with optional plasticity. No memory beyond what the brain carries, no reproduction, no self-modification. A
  successful organism could at best be a compact reactive controller for a tiny integer economy. The best recorded
  case (B-R5-1) is a 16-byte int4 brain matching a 200-byte float baseline in one screened world [RESULT-UNVERIFIED,
  unreplicated].
- CW01 organisms: by design single-mechanism probes. e07's recurrent net never reached state-dependent computation
  (state dependence ~0.05-0.09; hand-built accumulator 0.74) [RESULT-UNVERIFIED]; e09 organism has no call, compose
  or reuse (D068). These closures were explicitly "DESIGN UNREACHABLE": the organism lacked the capacity the
  question presupposed.
- Proteus VM organisms (loop): Turing-ish bounded tape programs with persistence policies; cycle 7-8 found an
  "identity plateau" and an "answer-before-read" obstruction; a 4-instruction "valley" separates the plateau from an
  XOR-1 witness; a single verified witness fixes 10/12 runs, so selection was not the obstruction [RESULT-UNVERIFIED].
- Z8 organisms: genuinely general byte programs: control flow (JR/JP), 8 registers, writable shared memory,
  self-modification (code = data), reproduction primitives (ALLOC/BIRTH/LDIR/LDDR/SELF), sensing (SENSE), persistent
  registers across slices (a carried internal state that later proved to be the dominant establishment variable).
  No arithmetic beyond add/sub/logic; no learning within lifetime other than register state; no communication
  channel other than writing into another organism's bytes on a shared tape.
- Fighting chance for a nontrivial reasoning primitive? Grounded answer:
  - For self-copying / heredity: yes in a narrow sense -- the instruction set can express a copier in a few bytes,
    and sustained causal copying was shown from implanted founders and, after making copy instructions one byte,
    from random bytes [RESULT-UNVERIFIED].
  - For task reasoning coupled to reproduction: almost no chance as built. The task is scored in a scratch arena
    with world ops disabled, decoupled from reproduction in PAIR_EXECUTION; the explicit-fitness effect exists only
    under EXTERNAL reproduction (FINDINGS A-2 scope note 09-29); the only test of task competence spreading through
    endogenous replication (X-TASK-GATE) was frozen with a ruler that is 0 by construction in its Stage-0 arms and
    was never run [HIST: ERRATA_2026-10-01_DO_NOT_DISPATCH_AS_FROZEN.md].
  - Wave-2 W2-10 reports that a copier-plus-task genome (CT_UA) exists in the space, so coupling is expressible
    [RESULT-UNVERIFIED].

## 6. Search and pressure mechanism

- Graphworld: MAP-Elites, hill climbing, GA on brain genomes. R1 E4: QD never beat random at equal evaluations; E8:
  closed loop catches up only at 128 seeds; D1: a hill climber stalls in silence on the metered channel; D-R8-3: E4b
  QD coverage is descriptor-dependent [RESULT-UNVERIFIED / CORRECTION].
- CW01: GA with tournament selection on tiny genomes; collapse modes: convergence in <10 generations (e02 D028),
  bimodal per-lineage held-out success (e08), no state use (e07).
- Z8 72 h: evolution inside a combinatorial grammar of physics; in non-pair physics, mutation occurred only at
  birth, so random populations that never reproduced never varied (S1-A: 907 FREE-policy runs, zero births; 114,485
  BIRTH calls with no pending allocation) -- a structural "no search" collapse [RESULT-UNVERIFIED, mechanism IMPL].
  In pair physics every organism mutates every epoch, plus the splice.
- Z8 late (c9x/NPE): variation = per-epoch mutation + pair-tape write-back erosion (~5%/byte/epoch, ~25x nominal,
  X-STALL-F0) [RESULT-UNVERIFIED]; [CORRECTION W2-18 P07 / N9-N10] BASE branching is near-critical and "erosion" may
  not be an extra mutation process; ATOMIC's effect is ~75% the world's fidelity clause ("the world's detector, not
  the organism, maintains copy fidelity").
- Bottlenecks named by the seat's own barrier map (W1): variation -> acquisition (copy-capable material availability)
  -> establishment (zero-addressing dependence / self-poisoned carried state) -> sustained heredity. Acquisition
  landscape: 0/6,400 random genomes or 1-2 step mutants competent; competent copiers on broad neutral networks;
  losing the copy instruction is a trap [RESULT-UNVERIFIED: ARC3 accessibility delegate].
- Missing baseline [HIST, flagged by Atlas buried signal A6]: whether the pair soup searches better than a neutral
  random walk for first appearance of a donor -- pilot ratio 1.75, p = 0.20; the full WP-9 baseline (~9 CPU-h) never
  ran.

## 7. Measurement / ruler stack

Chronological ruler stack and its failures:
1. Graphworld receipts: PASS/FAIL/KILL/NULL/INDETERMINATE with cheat strings; abstain/constant/random/input-invariant
   floors (added after R3); world screen; EVIDENCE_N sample rule; Clause B sham (featperm v2) and scratch controls.
   Failures: board_eligible accepts any non-empty cheat string (R-08, PARTLY TRUE); top-16-mean readout under-read
   (operator 15); unreceipted R8 results after lane sessions died.
2. CW01: MI vs shuffled null; noise floors; knockouts vs neutral shams; guardproof; preregistered P-criteria with
   gates. Failures: D043 guard comparing a dict with itself (could never fail); D022 gain detector fired on noise;
   D058 P1 bar unattainable at the primary dose (no attainability computation); D066 min-count rule frozen against
   a pilot predicting marginal attainability.
3. CW01 loop damage rulers: fixed-count deletion of k instructions; replaced by scattered Bernoulli(f) after P-G01/G08
   (see section 9).
4. Z8 72 h: non-pair replication = fid >= 0.90 AND wrote_bytes >= 0.5 x len; pair replication = fid_other >= 0.90,
   fid_self < 0.90, donor writes >= 0.25n, measured AFTER `_mutate` (the Z80A-D05 hole); crossing = held-out >= 0.90
   at any validation; interest = weighted signals, replication signal x0.25 for seeded runs; anticheat list;
   adjudicate.py (0.90 at final state, 0.25 margin over control, evidence-backed birth); matched pairs Hamming-1.
5. C9: P-1 ancestry certificate, P-2 causal-only depth, P-3 crossed_ever vs crossed_at_final, P-11 randomized-victim
   causal-copy assay (3 draws, majority 2; C2 rebuild >= 0.90, C4 donor authorship >= 0.90, C5 donor-disabled control
   < 0.90), R3 material certificate (z8taint; won a 9-fixture ruler tournament 9/9 vs id-based 4/9).
6. c9x / NPE: one-sided Fisher with frozen bars; LRT dose model; anc marker; founder-byte share; fresh-state P-11
   "competence" rate (L2: rate >= 0.5 over 20 seeds from zero registers), L3 depth >= 2, L4 depth >= 20; self-state
   robustness ruler; cycle-aware robustness (k = 1..6); DOM painter screen.
7. External: Artemis CVT-R heredity certificate (prereg 77bc0dbce, result d050937ec), Odysseus recertification.

Positive/negative controls: 72 h calibration 10/10 (VM semantics, witness, 4 seeded replicators fid 1.0, no general
replicator without self-location, invasion from seed, no runner births, external crosses a one-edit constant);
T-P11 14/14 with 3 negative fixtures; random-implant nulls (X-ATOMIC-RANDOM 0/80); ancestry tracer fixture pack 451
expectations, 10 mutants caught [HIST].

Known blind spots (each documented by a later artifact) [CORRECTION]:
- Similarity is not copying (90% identity detector; fixed before launch).
- Copy measured after the world's own variation operator (Z80A-D05: 6,287 of 6,547 RECOMBINATION events
  splice-made).
- Organism id is not heredity (C9-D14).
- P-11 certifies construction, not heredity: painters pass (Artemis #793); of the 57 S1-C certified donors, 2 copy
  themselves, 1 context-dependent, 17 paint, 37 inert (Odysseus #803).
- World-level depth is not founder depth; certification breaks (~5-16% of edges) cap certified founder depth at
  ~1/p (X-CERT-BREAK).
- anc marker is slot lineage, not content (X-CONTENT: 13-25% founder bytes).
- One-point snapshot self-state ruler on cycling register state (ARC3 forensic 16000006).
- Zero-context competence screen inside a CARRIED world (W2-46 CONTEXT_MISMATCH; N13).
- Genome-keyed validation cache (W2-8 D1); cached single-draw competence (W2-19, C9-H1R DEGENERATE).
- Inherited sibling controls (Z80A-D04: 64 of 65 endogenous-reach flags judged against a control not run for them).
- Implant arms unpaired (C9-D17/D24).
- CVT-R itself accepts rescue mutants and a constructed non-reproducer (HALFBLANK 9/9), and is a single-seed coin
  flip (6 recorded verdicts flip vs an 8-seed majority) [RESULT-UNVERIFIED: W2-36, repair R* sent to Artemis #1221].
- Rotation leak: LDIR on the 128-byte ring makes rotated, D-periodic copies (0.25 per birth) that form heritable
  "label without frame" lineages; BASE-only; ATOMIC immunity checked on 2 seeds x 80 epochs only (W2-35).
- R-05: P-11 per-draw files gitignored; 26 of 57 survivors rest on one event passing exactly 2 of 3 draws.

## 8. Experiment inventory (campaigns)

Outcome labels are on the historical record, not my verdicts.

### 8.1 GW: Graphworld / Primordial Machine swarm rounds R1-R8
- Dates: 09-14 07:00 .. 09-17 (R8 close d74753ef3 09-16 23:15; recovered results 447101ae8 09-17 10:35).
- Question: can a multi-lane swarm build and evolve compact brains in batched integer worlds; later the operator's
  success contract clauses A (compression), B (transfer), C (scaffolding) [INTENT:
  PROMETHEUS_SUCCESS_CONTRACT.md].
- Organism: action tensors, TT/QLin brains. World: wforge Encounter seeds, NK, signal worlds, GraphWorld toy.
  Pressure: MAP-Elites/GA/hill climbing on summed charge. Measurement: receipts vs floors, screens, EVIDENCE_N.
- Scale: R1 49 receipts; R2 37 receipts; R7 74-cell screen; R8 12 h science clock.
- Reported: R1 engine equalities PASS (Encounter trace-hash equal across numpy/numba/Lua/Cypher); C1/C1b/C1c KILLs on
  GPU/memory-bound predictions; E4 QD FAIL vs random; R2 "8-byte brains at parity in 5 of 6 cells"; R5 B-R5-1 first
  Clause A PASS (progress 1.591, CI [1.139, 1.827]); R7 E-R7-1 Clause B FAIL (sham beat graft); R8 second surviving
  world w8000036, C-R8-AP-01/02 PASS (AP-01 disputed VACUOUS).
- Reinterpretation: R2 headline falsified by the abstain floor (R3); R4 brain claims invalidated (operator 15);
  B-R5-1 not replicable in the grid; R8 replication trigger never ran; AP-01 dispute unadjudicated.
- Paths: roles/Nestor/sidequests/graphworld/ (REVIEW_PACKET_ROUND{1,2,4,5,6,7}*, ROUND3_G_METRIC_HARDENING_REPORT,
  SWARM_R8.md, R8_RECOVERED_RESULTS.json, R8_DISPUTES.json), primordial/.
- Label: MIXED (engineering PASSes; science mostly REPORTED NEGATIVE/NULL; the one compression PASS candidate is
  unreplicated; the R2 headline LATER OVERTURNED).

### 8.2 CW01-E: CW01 experiments e01-e09
- Dates: 09-17 16:54 .. 09-18. Path: roles/Nestor/campaigns/cw01-2026-09-17/.
- Totals [HIST: CAMPAIGN_STATE.json]: 9 attempted; 2 COMPLETE (e01, e03), 2 NULL (e02, e05), 5 INCONCLUSIVE (e04
  downgraded, e06, e07, e08, e09); 92 defect rows D001-D091 (+D038a/b), 28 of them science defects.

| exp | question | organism / world | arms | reported | label |
|---|---|---|---|---|---|
| e01 | does retention evolve under necessity | 5-gene policy, priced addressable region | treatment vs no-retention vs zero-recurrence; sham | +9.70% ancestor-relative (an early +40% was a seed artifact D010) | REPORTED POSITIVE (small) |
| e02 | ancestral efficiency ratchet | 9-gene transformation economics | 3 selection strengths; K1 knockout vs sham | +174%, ordering not foundation-first; gain detector fired on noise (D022) | REPORTED NEGATIVE/NULL |
| e03 | conditional sparse coalitions | 82-param linear activation | treatment vs non-conditional | MI excess 1.19 bits; I1 collapses 4/4 | REPORTED POSITIVE |
| e04 | queue/TTL triage | two 5-param linear policies | treatment vs controls; worth-scramble | decisive scramble clears floor 3/4; driver COMPLETE, Nestor downgraded (016e4a5b8) | INCONCLUSIVE |
| e05 | superadditive mixtures | 8-gene inclusion vector | conjunctive vs disjunctive | superadditivity clears null 2/4; exact independent replica 0 divergences | REPORTED NEGATIVE/NULL |
| e06 | representation ecology TREE vs TAPE | two program substrates | treatment vs label-only | mutual invasibility never held | INCONCLUSIVE (DESIGN UNREACHABLE) |
| e07 | computational weather / damage | 464-param recurrent net | STATIC / WEATHER / SHAMWEATHER | gate refused twice: D058 P1 unattainable, D059 no state use | INCONCLUSIVE (DESIGN UNREACHABLE; 397dad9a2) |
| e08 | rank-tax tensor evolution | real tt_digits in w13 | CONTROL/TAX/AMP/TAX+AMP | competent lineages 2/1/2/3 vs min 6 | INCONCLUSIVE (10ece30ba) |
| e09 | algorithmic soup / composition | real organism probe | none | single-op ceiling = abstain floor; scrambled op tables score like arithmetic ones | INCONCLUSIVE (DESIGN UNREACHABLE at RECONCILE, 7e17bacc8) |

### 8.3 CW01-L: CW01 loop cycles 1-8 and ARCH4 (T-ARCH4/T-ARCH5)
- Dates: 09-18 10:57 .. 09-19 08:57. Substrates: re-posed CW01 worlds and the Proteus/Archaeon VM. Rules
  (loop/LOOP_RULES.md, operator 09-18): nothing killed, TEMPORAL_STASIS instead, append-only TRAJECTORIES (39) /
  EVIDENCE (336), frozen top-10 per cycle with PREREG hashes.
- Headline claims [RESULT-UNVERIFIED]: ARCH4 locality law (scattered deletion of k loses more than contiguous; P-C15);
  trap-NOP walks grow length by acceptance not proposal (P-C03/P-C16); dose surface (P-D01); recombination prefix
  dominance 135/135 (P-H02); delay regimes drive populations to an "IMMUNE" geometry (P-H03); minimal causal
  transplantation FAILS (P-H04); cycle 7 "CRITICAL NEGATIVE" context worlds not crossed, identity plateau; cycle 8
  answer-before-read obstruction, 4-edit valley, single witness fixes 10/12, ADD-1 crossed 1/2 seeds at generation 0
  of a seeded stage ("partial seeded gateway"); opcode edits lose function at 2.3x the operand rate (P-C05).
- Reinterpretation: cycle 5 ruler audit removed 4 of 7 fixed-count damage claims and shrank 2 (section 9.3); P-D05
  NOT_REPLICATED corrected P-A07; P-D11 reframed e06 "coexistence unreachable" as "invasion from rarity fails";
  P-E03/P-E09 run 1 voided (D083 arm-name seeding).
- Paths: cw01-2026-09-17/loop/ (CYCLE_REPORT_*, BOUNDARY_REPORT_CYCLE5_2026-09-19.md, EVIDENCE.jsonl), commits
  94153f68b, 622d64632, 7976d5ce1, bdf8c5df4, 74fcf1ff9, 66d964f9a, 18760ed17, ce97fbcc4, 8a01ddede, 422f80caf,
  6c14b17f8, 3af735d67.
- Label: MIXED (several LATER OVERTURNED by the ruler audit; obstruction findings REPORTED POSITIVE as negatives).

### 8.4 Z80A-72H: Nestor's Z80 x Atlas 72 h autonomous campaign
- Dates: launched aa5833488 09-19 10:49; frozen 09-22. Path: roles/Nestor/campaigns/z80atlas-2026-09-19/.
- Question: which physics x representation x ecology combinations open paths that external reproduction cannot reach.
- Organism: Z8 tapes; world: all 4 world types; pressure: 16-factor grammar; measurement: section 7 item 4; arms:
  matched one-factor pairs; scale: 23,471 runs, 0 failed, 0 voided, 20,638 families, 10,741 pairs, 6 workers,
  schtasks watchdog loop.
- Reported [HIST: observatory/PACKET.json, ADJUDICATION.json; FINDINGS A]: 1,031 ADMISSIBLE
  "SPONTANEOUS_REPLICATOR_FROM_RANDOM_BYTES" (fid 0.906-0.990); one endogenous-only accessibility instance (A-4);
  124 reservoir flags; matched-pair effects (explicit fitness +0.30 over implicit, 513 pairs; EXTERNAL beats
  PAIR_EXECUTION by 0.12; answer-before-read > forced read).
- Reinterpretation: all 1,031 are PAIR_EXECUTION (C9-D01); depth 1 in 911; splice artifacts (Z80A-D05); P-11 leaves
  57 (48 literal); of those 2 genuine self-copiers (Odysseus #803). A-4 WITHDRAWN (frozen population, inherited
  control). A-5/A-6 WITHDRAWN. Pressure row valid only inside EXTERNAL reproduction (scope note 09-29). Report rev 1
  had sign inversions and summary-of-summary defects R-01..R-04; the audit receipt certified a deleted temp file
  (C9-D03, fixed b05a34f1b).
- Commits: aa5833488, 9d9ef1980, 3b407946e, 5b5443959, b05a34f1b.
- Label: LATER OVERTURNED (heredity headline, endogenous-only, reservoir); the matched-pair table is REPORTED
  POSITIVE with narrowed scope.

### 8.5 C9: Cycle-9 verification inner experiment
- Dates: repairs f13a563b4 (09-22); pre-freeze HARD STOP 6436fe4ec on C9-D14 (09-24); frozen b661fe43f (protocol
  5819bc6d, manifest 8d88cf06); addendum ab94f5399. Path: z80atlas-verify-2026-09-22/.
- Questions: H1 read-order (true same-task intervention), H2 do implanted specimens propagate, H3 reservoir stepping
  stones, H4 endogenous accessibility (WITHHELD: arm cannot reproduce, C9-D07).
- Scale: 1,200 runs (H1 240, H2 768, H3 192); audit 21/21.
- Reported: H1 NO_DETECTED_EFFECT; H2 replication events without propagation; H3 NOT_DEMONSTRATED.
- Reinterpretation: H1 INVALID (C9-D16 four identical arms) -> C9-H1R rerun COST_INTERACTION_ONLY (I = +0.20; gate
  abolishes competence only when reading the cue costs instructions) -> [CORRECTION W2-19] H1R competence was a cached
  single lucky draw, DEGENERATE. H2 WEAK_SIGNAL concentrated in specimen 7ae3 (implant 4/16 depth >= 5 vs 0/16),
  but "random 0/16 and in situ 0/16" are one null (C9-D24). H3 -> INVALID (W2-8 D2 arms identical).
- Label: INSTRUMENT FAILURE (H1, H3), MIXED (H2).

### 8.6 S1-S4: forensic pass on the 72 h record
- Dates 09-23/24. Path: z80atlas-forensics-2026-09-23/. S1-A funnel (non-pair physics never searched; zero births in
  907 FREE runs), S1-B H4 autopsy (A-4 withdrawn), S1-C P-11 reassay (57/1,031), S2 P-11 instrument (T-P11 14/14).
  Commits 9a3cd4a94, ee2d018de, d7641744d, f28e5fd72.
- Label: REPORTED NEGATIVE/NULL as a re-assay; functions as the correction to 8.4.

### 8.7 C9X: c9x autonomous loop (EXPLORE/CONFIRM chain)
- Dates: 09-24 06:47 .. 09-26 07:42 (48 h + 55 min reboot extension). Path: c9x-explore-2026-09-24/ (CAMPAIGN_REPORT.md).
- Organism: implanted founders (mostly specimen 7ae3f9c1437c8000, mined from a 72 h random-start run) or random
  bytes; world: deformed FREE non-pair worlds and the 7ae3/ffa6 pair-tape cells.
- Confirmed (fresh seeds, frozen bars) [RESULT-UNVERIFIED]: C-SELFLOC 13/36 vs 0/36 (implanted copier needs free
  self-location); C-ENERGY 20/40 vs 4/40 (depth-1 wall = newborn starvation); C-DENSE 13/40 vs 0/40 (spontaneous
  non-pair replication once world ops are 1 byte; max depth 5); C-ABLATE (self-location and search necessary);
  C-RUNAWAY 7/150 vs 0/150 (splice prevents runaway pair-tape heredity; max depth 549); C-CRITICAL-MASS 41/80 vs 5/80
  (establishment-limited; "critical mass" refuted by X-DOSE-CURVE: independent tickets, LRT p = 0.42); C-ATOMIC C1
  46/80 vs 1/80 (tape-write erosion stops heredity in 7ae3's cell); C-CORE 17/27 vs bar 60% (runaways conserve the
  founder's SELF + LDIR instructions and little else). Not confirmed: C-NORECOMB 5/48 vs 5/48; C-ATOMIC C2 1/120 vs
  0/120; C-SWAP-ACQUIRE 9/240 vs 0/240 (bar 10).
- Reinterpretation: world-level vs founder depth (X-ROOT-AUDIT 12/80); X-ATOMIC-RANDOM reverses that; X-CONTENT
  "founder-descended" = lineage, not content; X-CERT-BREAK caps certified depth; C-CORE is what purifying selection
  predicts and was theory-aware by date (Aporia #621, accepted); SI framing withdrawn by operator 09-26; W2-9: C-RUNAWAY
  FRAGILE (7/150 = minimum passing count, prior power 0.05-0.56, second attempt), C-CORE FRAGILE (17 vs bar 16.2),
  C-ABLATE SEARCH FRAGILE; ROBUST: C-SELFLOC, C-ENERGY, C-ATOMIC C1, C-CRITICAL-MASS. X-PAIR-NORECOMB downgraded to
  INVALID (no positive arm, R-11).
- Commits: fa1ef0015, 8801b40bc, 4309646db, 48ee4cafb, 155c7e737, 2684e7a9b, bfa29c437, 783de17c6, 3ba6d8a97,
  778f00e90, 76061ddd9.
- Graph: 92 ids in EXPERIMENT_GRAPH.jsonl (computed here: last-line classifications SIGNAL 30, WEAK_SIGNAL 27,
  CLEAN_NULL 14, INVALID 5, other/none 16).
- Label: MIXED (several REPORTED POSITIVE confirms within narrow cells; some FRAGILE; mechanism readings corrected).

### 8.8 W1: NPE window, donor discovery
- 09-26 09:32 .. ~20:50. Path: npe-w1-donor-discovery-2026-09-26/ (W1_REPORT.md, d63b76a5f).
- Question: how do competent hereditary donors arise from non-competent material.
- Organism: random Z8 populations; world: 7ae3/ffa6 pair-tape cells, ATOMIC; ruler: L1-L4 funnel.
- Reported: C-DENSE-COPY CONFIRMED (1-byte LDIR/LDDR alias: donor acquisition 1/64 -> 39/64, p 1e-14); C-STATELESS
  NOT_CONFIRMED in both cells; C-STATELESS-FFA6 CONFIRMED (11/33 -> 34/42; restriction chosen post hoc, declared).
- Reinterpretation: "encoding accessibility" -> "availability of copy-capable material" (P2 SHAM 0/96, PLANT 32/96) ->
  "carrier exposure" (ARC3); "register persistence barrier" -> "zero addressing" (P2); self-poison labels unreliable
  (cycling-state ruler defect); X-DD-ESTABLISH validity defect (W2-34).
- Label: REPORTED POSITIVE (statistics) / LATER OVERTURNED (mechanism readings).

### 8.9 P2: endogenous heredity program
- 09-27 16:52 .. 21:32. Path: npe-p2-endogenous-heredity-2026-09-27/ (SYNTHESIS.md, fdc73636f).
- Reported: C-ZERO-SPECIFIC CONFIRMED (ZERO 26/48 vs CONST 2/48, p 2.4e-8; CARRY 6/48; RANDOM 3/48); corpus: 95.7% of
  competent donors are SELF-free offset-64 copiers working at tape offset 0.
- Reinterpretation: 14 of 16 panel donors cannot copy from 0x5A at all, so the contrast is built in by the zero-state
  donor screen (N11, W2-18 P11); donor-clustered, donor-level p 0.003 fails the frozen 0.001 (W2-9); CVT-R accepts
  23/32 P2 donors (Artemis). FINDINGS itself notes "Part of this is by construction".
- Label: MIXED.

### 8.10 ARC3: internalization portfolio
- 09-28 01:13 .. 10:12. Path: npe-arc3-2026-09-28/ (SYNTHESIS_ARC3.md, f443bcef0).
- Reported: C-A3-INTERNALIZE CONFIRMED (8/144 fresh runs vs bar 4; lineages founded by state-dependent donors come to
  carry state-free competent genomes); X-A3-WITHDRAW CLEAN_NULL on speed with robust share 0.22 -> 0.94 after
  scaffold removal; forensic 16000006 killed the single-change transition; self-location almost never internalized
  (280/280 SELF-free copiers fail when moved >= 16 bytes; 2/332 true locators).
- Reinterpretation: W2-8 D10 / W2-9 / W2-18 P12 -> CONFIRMED-FRAGILE (only 4 events hold at the final checkpoint, 3
  by majority; no null arm; zero-context screen; cell split confounded by D4); WITHDRAW rise may be a sweep of
  standing robust members (P03); state-free genomes appear even in the ZERO no-payoff world. BEE REPL-01 independent
  rebuild: DISAPPEARS (K3), descent UNRESOLVED in BEE [HIST: roles/Bellerophon/STATUS_REPORT_2026-10-01.md].
- Label: MIXED (REPORTED POSITIVE, downgraded to fragile; not replicated in BEE).

### 8.11 AR: Ancestry replay of NPE T-003 (instrument for Archaeon)
- 09-28 10:46 .. 09-29 13:02. Path: ancestry-replay-2026-09-28/.
- Question: do Archaeon's attribution claims about NPE T-003 births survive independent reconstruction.
- Unit: 11 run records of specimen 4931614d912c52b2; arms A_in_situ / B_reimplant_actual / C_reimplant_random
  (C == A per C9-D24, so 11 records = 9 distinct simulations, 34 births = 29 distinct).
- Timeline: gates G1-G4 cleared; production run 1 INVALIDATED (duplicate_of = itself; 8153aaa8e); run 2 (81895e729);
  review: s4_run.py DOES NOT CONFORM (two BLOCKING items); s4v2, v2.1 non-conforming; v2.2 CONFORMS (f8b589b2d); result
  flip coverage self 0.321 / other 0.286 / tied 0.25, below the preregistered floor; CVT-R reconciliation: 27/29
  children are 0x36 near-homopolymers (LD (HL),0x36 painting), heredity NOT MEASURED (334b6ad55).
- Incident run 3 (section 9.6).
- Label: INCONCLUSIVE (floor not met) with INSTRUMENT FAILURE episodes.

### 8.12 FRONTIER: X-MAT-INTERNALIZE and X-TASK-GATE
- X-MAT (09-30, prereg c3e9eae9e, verdict ae38658fe, disclosures ac5ed7a26): C-A3 internalization events are
  ENDOGENOUS material 8/8 (median XENO share 0.020). Disclosed: pilot started before freeze; no planted-transplant
  control; WORK_STATE timestamps ran ahead of the clock. W2-9: ARTIFACT-RISK (7/8 endpoints at L_share 1.0, where X ~ 0
  by structure; counting MUT bytes as foreign would give MIXED). Label: MIXED.
- X-TASK-GATE (frozen 62d30e443 09-30, never executed; ERRATA_2026-10-01_DO_NOT_DISPATCH_AS_FROZEN.md 51c665a00):
  decisive ruler 0 by construction in Stage-0 EXTERNAL arms; ADD37 never scored after epoch 25 under COEVO_ENV.
  Label: INSTRUMENT FAILURE (pre-execution); outcome UNKNOWN.

### 8.13 HARVEST: inference harvest wave 1 and saturation wave 2
- 09-30 17:59 .. 10-01 ~09:00Z. Paths: roles/Nestor/inference_harvest_2026-09-30/,
  roles/Nestor/inference_saturation_wave2/ (INFERENCE_LEDGER.md 115 KB; ~56 workers W2-1..W2-56; N1-N18).
- Nature: LLM reasoning passes over existing data, bounded static assays, bit-exact replays and small fits (~20-25
  core-h). No new world campaigns; no frozen verdict edited.
- Key outputs: W2-8 15 engine/runner defects (4 invalidating); W2-9 all 20 frozen statistics reproduce exactly but
  several are fragile; W2-15 95 verdicts x 17 defects matrix (1 flip, 22 relabels, no CONFIRMED flips); W2-18 17
  FINDINGS correction proposals; W2-35 rotation leak; W2-36 CVT-R false accepts; seven competing theories collapsed
  into one "supplied rewrite field" framework F, judged unfalsifiable as practised, tolerances F* frozen.
- Not landed: the W2-48 FINDINGS appendix was never appended; FINDINGS.md ends with the 09-28 "RECEIVED, UNVERIFIED"
  section [IMPL: file read].
- Label: MIXED (a correction harvest; itself unverified; usage-limit interrupted).

## 9. False-positive / false-negative archaeology

### 9.1 "1,031 spontaneous replicators from random bytes" (false positive, layered)
- Claim: 09-22 campaign close, 1,031 ADMISSIBLE (3b407946e; b10161316 merge message).
- Evidence: pair-tape fidelity events, fid 0.906-0.990.
- Challenge: REPORT rev 2 (5b5443959) -- events are not lineages (depth 1 in 911); C9-D01 all PAIR_EXECUTION.
- Correction: Z80A-D05 -- fidelity measured after `_mutate`; under RECOMBINATION the splice made the match in 6,287 of
  6,547 events; S1-C P-11 reassay leaves 57 (d7641744d); R-05: 26 of 57 rest on one 2-of-3 event; Odysseus #803:
  2 genuine self-copiers, 17 painters, 37 inert.
- Status: LATER OVERTURNED (~95% artifact). The 7ae3 founder used downstream is one of the genuine copiers.

### 9.2 "Similarity is not copying" (caught before launch)
- In the 09-19 rehearsal a 90% byte-identity pair detector fired 5 times in 3 minutes and raised the top flag on junk
  (copy_bytes 0). Fixed before the launch commit aa5833488: replication requires fid_other >= .90, fid_self < .90,
  donor_wrote >= 0.25n (world.py:600-637 of the 09-19 copy) [HIST via memory note; fix IMPL]. No commit contains the
  bad detector [CODE-INFERRED]. The fix itself still measured after the splice (9.1), so the lesson had to be learned
  twice: FINDINGS D lesson 2 ends "and P-11 now says even that is not enough", and Artemis later showed P-11 is not
  enough either (construction vs heredity).

### 9.3 Fixed-count damage rulers manufacture coordinates (CW01 loop)
- Claims: P-D01 (cycle 2) length protects / loss is a dose in units; P-E05 (cycle 3) depth and growth lower loss;
  P-F06 (cycle 4) selection lowers loss, SELECTED_REPLICATED 6/6; P-E03 selected tops robust.
- Evidence: fixed-count deletion of k instructions.
- Challenge: P-F01 (cycle 4, ce97fbcc4): NOP padding "protection" is dilution of a contiguous window; D084 the
  fraction-matched arm was itself one contiguous window.
- Correction: cycle 5 (8a01ddede, 09-19 03:28): scattered Bernoulli(f) ruler qualified (hit counts Binomial(n,f),
  chi-square p .49, sham displacement 0); P-G08 shows exact-count round(f n) reproduces the artifacts because
  round(fn)/n is larger for short programs; P-G02 audit: 4 claims DISAPPEAR, 2 SHRINK, 1 SURVIVES (operand
  softness). Artifacts: loop/BOUNDARY_REPORT_CYCLE5_2026-09-19.md s3, CYCLE_REPORT_CYCLE5 lines ~199-218.
- Status: corrected. Open: the ARCH4 locality law (P-C15 scattered > contiguous at fixed k) and P-C04 were not in the
  7-claim audit [UNKNOWN whether they survive the qualified ruler]. Atlas ranks re-scoring Proteus "cliff" / "length
  protects" rows under Bernoulli(f) as its top cheap separating test (ATLAS_CONTRADICTIONS s0 rank 1).

### 9.4 Pair-tape identity is not heredity (C9-D14)
- Claim: H3 certificate would certify lineages by organism id.
- Evidence: PREFREEZE_STOP_2026-09-24.md probe: on the pair tape an organism keeps its id while its bytes are
  replaced (identity to birth genome 0.97 after 1 epoch, 0.00 by 600, no lineage event).
- Correction: freeze stopped (6436fe4ec); R3 material certificate via z8taint built by a ruler tournament.
- Status: the defect caught a false-positive pathway before it ran; later W2-8 D2 found H3 arms identical anyway.

### 9.5 Read order / answer-before-read
- Claim (REPORT rev 1): forced read beats answer-before-read -- with sign inversion (R-01); cycle 8 said to have
  established a forced-read advantage (withdrawn: it was a proposal).
- Challenge: FORCED_READ changes the target (base = v XOR key), so arms score different tasks.
- Correction: C9 H1 true intervention -> INVALID (C9-D16) -> H1R COST_INTERACTION_ONLY -> W2-19 DEGENERATE (cached
  single-draw competence, true held 0.50).
- Status: OPEN; the cost-of-reading interpretation rests on a degenerate measurement.

### 9.6 Unauthorized ancestry run 3 (process failure destroying evidence)
- 09-28 10:29 and 20:16 Nestor created launchers as `schtasks /create /sc once /st 23:59` placeholders and ran them by
  hand. At 23:59 both triggers fired, blocked on the cpu8 lease held by Ananke; at 00:45:03 09-29 the production
  launcher acquired the lease and started run 3; noticed ~00:48, killed 00:49:25. 10 of 11 git-ignored run-2 1%
  sample files were overwritten with truncated gzip; tracked births files partially rewritten and restored. Defects
  D-INC-1..3 (stale trigger + wait-acquire; no never-overwrite guard; no immutable evidence copy). Recovery from
  run-1 copies matched by content (8927e1fbf; stage 2 agreement 168c8b81d) [HIST: INCIDENT_RUN3_2026-09-29.md].
  LEASES.jsonl lacked 8 lease records for ~2 days until 797d338ff (10-01).

### 9.7 False negatives / null searches that lacked capability
- Non-pair spontaneous replication "absent" in the 72 h record: the physics mutated only at birth (no search) and
  allocators never declared births; once search, free self-location, energy transfer and 1-byte op encodings were
  added, spontaneous replication appeared (C-DENSE 13/40) -- the 72 h null was a physics/instrument artifact.
- CW01 e06/e07/e08/e09 "DESIGN UNREACHABLE": organisms or rulers could not express the question (no state use, no
  composition, unattainable P1, min-count rule vs bimodal success). These are capability nulls, not evidence of
  absence.
- C9-H3 and X-PAIR-NORECOMB nulls are INVALID (identical arms; no positive arm). C-NORECOMB had power ~0.08;
  C-ATOMIC C2 had 2/15 capable specimens; C-STATELESS in 7ae3 was low power (8 donor runs).
- Graphworld: the world family was so degenerate (abstain beats learners) that QD/brain nulls say little about the
  methods.
- Atlas buried signal B9: the only random-origin survivor of a Z80 x Atlas campaign (84616cf8257b, input-gated
  self-copier, exact only at input 121, late fidelity 0.482) was excluded by the fidelity threshold -- this is from
  Archaeon's z80atlas adjudication, not Nestor's [HIST, attribution checked only at the Atlas row level].

### 9.8 Construction is not heredity (ruler class change)
- 09-28 Artemis #793 (painters pass P-11) + Odysseus #803 + CVT-R #891: 19 P-11-certified genomes fail CVT-R (11 at
  generation 2). Nestor qualified every "competent" claim to construction. Then W2-36 (10-01) showed CVT-R itself
  false-accepts. Status: the heredity status of most donor sets is UNKNOWN under any validated ruler.

## 10. Research outputs

- roles/Nestor/FINDINGS.md -- findings ledger with HOLDS/NARROWED/WITHDRAWN/OPEN/DEFECT statuses and 12 standing
  methodological lessons (section D); last substantive section 09-28.
- roles/Nestor/sidequests/graphworld/FRAMEWORK_WRITEUP_2026-09-14.txt; REVIEW_PACKET_ROUND{1,2,4,5,6,7}*;
  ROUND3_G_METRIC_HARDENING_REPORT_2026-09-14.md; POSTMORTEM_2026-09-14_A_D.md; SWARM.md; SWARM_R8.md.
- cw01-2026-09-17/CAMPAIGN_STATE.json; loop/CYCLE_REPORT_{ARCH4, CYCLE1..8}; loop/BOUNDARY_REPORT_CYCLE5_2026-09-19.md
  (ruler audit); SUCCESSOR_WORLDS_CYCLE7.json.
- z80atlas-2026-09-19/PREREGISTRATION.md, REPORT.html (rev 2), observatory/PACKET.md/ADJUDICATION.md, DEFECTS.md.
- z80atlas-verify-2026-09-22/PREREGISTRATION.md (amendments A-1..A-28), P11_SPEC.md, PREFREEZE_STOP_2026-09-24.md,
  H3_RULER_TOURNAMENT.json, observatory/REPORT_C9.md, C9_OUTCOME_AND_ADDENDUM.md.
- z80atlas-forensics-2026-09-23/S1A_FUNNEL.md, H4_AUTOPSY.md, S1C_P11_REASSAY.md.
- c9x-explore-2026-09-24/CAMPAIGN_REPORT.md (barrier geometry, confirms).
- npe-w1.../W1_REPORT.md; npe-p2.../SYNTHESIS.md, BACKLOG.md; npe-arc3.../SYNTHESIS_ARC3.md, delegates/
  (ACCESSIBILITY.md, forensic_16000006, selflocation, external research); npe-frontier.../x_mat_internalize/RESULT.md.
- ancestry-replay-2026-09-28/REVIEW_PACKET_RUN2.md, CVTR_RECONCILIATION.md, INCIDENT_RUN3_2026-09-29.md.
- inference_harvest_2026-09-30/INFERENCE_HARVEST_HANDOFF.md, NPE_COMPETING_THEORIES.md, NPE_MECHANISTIC_SYNTHESIS,
  NPE_UNMINED_EVIDENCE, BUILDER specs B1-B8; inference_saturation_wave2/INFERENCE_SATURATION_WAVE2_HANDOFF.md,
  INFERENCE_LEDGER.md, W2-8/W2-9/W2-15/W2-18/W2-35/W2-36 reports.
- C3_HOLDOUT_D_REPORT.md (custody report for a Cosmos holdout; not a Nestor engine).
- External prior-art: ARC3 delegates/external (e.g. Bourrat 2022 scaffold withdrawal prereg question) [HIST].

## 11. Journals, TODOs, pivots, abandoned branches

- Journal: only roles/Nestor/journal/2026-09-14.md exists; CW01-onward narrative lives in commit messages, STATUS,
  CAMPAIGN_STATE and syntheses [IMPL]. calibration/LEDGER.md is header-only (09-14) despite many withdrawals [IMPL].
  BACKLOG_H0H5.md has 3 provisional 09-14 items [IMPL].
- Pivot reasons (from directives):
  - graphworld -> CW01: the swarm's science yield was thin and the operator moved to preregistered campaign work
    [CODE-INFERRED from dates; directive text not fully read].
  - CW01 -> loop: operator 09-18 "nothing scientific is ever killed" after e07-e09 closed DESIGN UNREACHABLE.
  - loop -> Z80 x Atlas: 09-19 directive for a 72 h autonomous combinatorial campaign (same directive also produced
    Bellerophon's BEE and Archaeon's z80atlas).
  - 72 h -> C9 repair -> S1-S4 forensics: the report-integrity defects and the 1,031 narrowing.
  - 09-24 promotion: from micro-tasks to a budgeted autonomous loop.
  - 09-26: steward model abandoned; SI retrofit withdrawn; direct operator control.
  - 09-28: ARC3 closed with no successor arc; Nestor repurposed as an instrument seat ("construction != heredity",
    C9-D24 frozen as a design defect).
  - 09-30: fleet scheduler (Aporia) dispatches; finish-in-place; then inference-burn directives before a usage reset.
- Abandoned / never-run: CHIMERA-0; w8000036 replication trigger (fired into a dead session); C9-H4 (WITHHELD);
  C-A3-WITHDRAW-ROBUST (PLANNED, never run); X-TASK-GATE (frozen, do-not-dispatch); WP-9 soup-vs-random-walk
  baseline; E4 genealogy for C-A3; W2-53 out-of-sample keep test (interrupted by a 429 usage limit).
- Branches: origin still holds nestor/bld-g/h/p/q/u, design-review, gw-c, r5-r (graphworld era, unmerged commits in
  bld-g/q/h/design-review), s1-forensics, s4v2, s4v21, d2v3, d-seal-merge, c3-holdout-d (these later ones have 0
  commits not on main per Atlas digest). Candidate merge 91d6a6d66 (09-17) was NOT used; main imported the branch at
  b10161316 (09-22).

## 12. Lens inventory

### Lens N-1: Z8 pair-tape heredity lens (NPE)
- Substrate: byte programs on a shared 128-byte pair tape with ED world ops and carried registers.
- Organisms: 64-byte Z8 genomes, implanted founders or random bytes.
- Worlds: two specimen cells (7ae3 Z8_64 well-mixed; ffa6 Z8_SLOTTED niches), ATOMIC or BASE write-back, reset axis.
- Pressures: effectively overwrite-by-copy only (most nominal pressures inert per W2-8 D3).
- Phenomenon family: origin, establishment and maintenance of copying/heredity; dependence on environment-supplied
  initialization ("scaffold") and its internalization; erosion vs fidelity.
- Resolving mechanism: P-11 causal construction assay, z8taint/dense_taint material provenance, CVT-R (external),
  reset-axis interventions, Fisher-tested frozen CONFIRMs.
- Likely resolution ceiling: single-digit to tens of events per arm in two cells; heredity vs construction not
  separated by any validated ruler; most mechanism names revised within days (Atlas: "read NPE mechanism names from
  the last 10 days as provisional").
- Noise sources: splice and write-back artifacts, rotation leak, cached competence, cell-confounded mutation supply
  (D4), unpaired implant arms, gitignored per-draw data, LLM-generated reinterpretations.
- Architectural limits: fixed genome length; one tiny conditional task decoupled from reproduction; no environment
  generation; heavy dependence on the zero-register convention of the ISA.
- Reusable: P-11 assay concept and randomized-victim design; material taint; reset axis as a declared world axis; the
  frozen-confirm/explore graph discipline; the defect x verdict matrix (W2-15).
- Toy-grade: the two-cell world; the task module; the pressure catalogue as implemented on the pair tape.
- Unknown: whether any finding transfers to BEE or other ISAs (BEE REPL-01 did not reproduce C-A3); whether soup
  search beats a neutral walk.

### Lens N-2: Combinatorial physics grammar (72 h Z80 x Atlas)
- Substrate: 16-factor grammar over world/reproduction/representation/pressure/ecology; matched one-factor pairs.
- Phenomenon: which physics open which reproduction/competence paths.
- Resolving mechanism: matched-pair effects, preregistered flags + adjudication.
- Ceiling: once rulers were corrected, the grammar's headline flags collapsed; matched-pair effects survive only
  scoped (e.g. pressure effect only under EXTERNAL).
- Reusable: grammar-as-data with hash-gated start/resume, control axes, report_audit pattern.
- Toy-grade: many factor levels were inert or broken (P-8/P-9/P-10, pressures).

### Lens N-3: Proteus-VM damage/robustness and accessibility loop (CW01 loop)
- Substrate: Proteus/Archaeon tape VM; damage rulers; neutral walks; recombination.
- Phenomenon: robustness geometry, locality of damage, accessibility valleys (answer-before-read, 4-edit valley).
- Resolving mechanism: qualified scattered Bernoulli(f) ruler; witness seeding; append-only evidence.
- Ceiling: tiny PUT/ASK tasks; a fixed-count ruler artifact class already demonstrated; locality law unaudited.
- Reusable: the ruler-qualification procedure (binomial hit check, sham displacement) and the stasis-not-kill loop
  bookkeeping.

### Lens N-4: Primordial Machine compression/transfer harness (graphworld)
- Substrate: batched integer Encounter worlds, TT/int4 brains, QD archive in Redis.
- Phenomenon: compression (bytes per competence), transfer (graft vs scratch vs sham), scaffolding.
- Resolving mechanism: floors, world screen, sham controls, EVIDENCE_N.
- Ceiling: world family nearly degenerate (1-2 of 74 cells admit learning above floor).
- Reusable: floor discipline (abstain/constant/random/input-invariant), sham-vs-scratch transfer control,
  cross-implementation trace-hash equality.
- Toy-grade: Encounter seeds as worlds.

### Lens N-5: Independent shadow-tracer reconstruction (ancestry replay)
- Substrate: a second implementation of the Z8 VM asserted value-identical per interaction; per-birth flip tests.
- Phenomenon: attribution of who built which bytes.
- Ceiling: flip coverage below preregistered floor; children mostly painted homopolymers.
- Reusable: shadow-VM equivalence assertion, fixture/mutant packs, gate ledger.

## Open questions / unknowns

- Whether the ARCH4 locality law survives the qualified Bernoulli(f) damage ruler.
- Whether any donor set's heredity status is established under a validated (repaired, multi-seed) CVT-R (R* pending
  with Artemis, #1221).
- Whether W2-35's ATOMIC immunity to the rotation leak holds beyond 2 seeds x 80 epochs.
- Whether C-A3 internalization arises de novo or from standing founder variation (genealogy never run; no
  planted-transplant control for X-MAT).
- Whether the pair soup is a better search than a neutral random walk (WP-9 never run).
- Whether any wave-2 correction proposal (W2-18 P01-P17) was adopted; as of 19299e06b none appears in FINDINGS or the
  graph.
- The 72 h prose-declared thresholds were not hash-enforced; whether they were followed exactly is unverified.
- 7ae3 founder origin event: whether splice-assisted (not re-audited).
- P-11 per-draw data (R-05) is gitignored; the "57" cannot be re-audited without regeneration.
- The "NPE" name refers to two different engines across documents; Atlas's harvester and later documents are not
  reconciled.
- Graphworld R8: AP-01 PASS vs VACUOUS dispute never adjudicated; w8000036 replication never run.
- Why calibration/LEDGER.md stayed empty under a standing requirement.
