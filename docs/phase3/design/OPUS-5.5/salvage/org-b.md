# Salvage digest org-b -- Organism machinery B: other substrates and organism code

Evaluator: salvage worker for EPIMETHEUS (Phase 3 independent architect OPUS-5.5). Date 2026-10-01.
Frozen baseline: commit 77d3c99c3 (RSE_ARCHITECTURE.md, requirements.jsonl). Worktree
C:/prometheus-worktrees/epimetheus-phase3, read-only. No path containing holdout / nestor_secrets / credentials was
opened (Aether/runpod/prometheus_gpu/credentials.py and secrets.py were not opened). Nothing under docs/phase3/design/
other than OPUS-5.5/ and nothing under roles/Dionysus/ was opened.

Question asked of every component: DOES THIS SATISFY A PHASE 3 REQUIREMENT BETTER THAN REBUILDING IT?

## 0. Bottom line

No component in this group should become the primary substrate, the probe kernel, the familiar reference learner or
the second substrate. The DGM (RSE_ARCHITECTURE s3) is a new build. What survives is (a) verification and
intervention PATTERNS that the DGM and the R2 bench should copy, (b) a few small primitives worth lifting nearly
verbatim, and (c) a large, well-documented corpus of false positives, search misses and known answers. That corpus is
worth more to Phase 3 than any of the engines that produced it.

    component                                   category            slot     cost  decisive reason
    ------------------------------------------  ------------------  -------  ----  ------------------------------------------
    Ares substrate + worlds + GA                HISTORICAL_CONTROL  R2       S     W4 latch = the MEA-16 "latch for memory"
                                                                                   non-target; D1-D4 = canary classes
    Ares carriers.py                            EXTRACT             R2       S     carrier-class lesion matrix is the right
                                                                                   shape for ORG-19/CAU-05; implementation
                                                                                   forces silence and has sham defects
    Ananke PTE engine + GA + envs + plants      HISTORICAL_CONTROL  R4/R2    S     canonical "plant exists, GA 96x36 never
                                                                                   finds it" reachability fixture
    Ananke oracle + conformance harness         EXTRACT (pattern)   R3/R0    S     best bit-exact reference pattern in the
                                                                                   repo; oracle omits every Control
    Ananke rng.py (counter-hash keyed streams)  EXTRACT             R0       S     62 lines that already satisfy REP-07 shape
    Ananke mirror-twin interchange (lens*)      EXTRACT (pattern)   R2       S     exact state interchange between twins that
                                                                                   share all exogenous draws (CAU-04)
    Aether aeth01 byte lattice + variants       RETIRE              -        NA    no organism, no task, frozen medium
    Aether verification kit                     EXTRACT (pattern)   R0/R3    S     shared-path bit identity, mutant-killing
                                                                                   conformance suite, LF-normalised hashes
    Nestor Z8 / NPE                             HISTORICAL_CONTROL  R2       S     richest false-positive record (splice
                                                                                   copies, pair-tape identity)
    Bellerophon BEE prometheus/z80atlas         HISTORICAL_CONTROL  R2       S     golden-replayed engineered replication
                                                                                   basin; YOKED pressure control record
    Archaeon z80atlas + census + denovo         HISTORICAL_CONTROL  R2/R4    S     measured random-tape copier prior; 26/26
                                                                                   "spontaneous" flags were transplants
    Z80 material-taint shadow interpreters      EXTRACT (pattern)   R3/R2    S     "shadow must equal VM or refuse" is the
                                                                                   ORG-08 / DEV-14 provenance pattern
    Tyche lens ecology                          HISTORICAL_CONTROL  R2       S     planted GRAMMAR-BORNE case for AGR-15;
                                                                                   parity-3 needle never reached
    Tyche audits + certify                      EXTRACT             R1       S     causality (future-replacement) audit and
                                                                                   structure-destroyed / PRF negative worlds
    Ensorain TT substrates (E0-E2, D1, LM01)    RETIRE              -        NA    regressors under a fixed hand policy;
                                                                                   E1.5 positive was a tautology
    Ensorain WTP-01..03 foundry                 HISTORICAL_CONTROL  R2       S     three ruler false positives killed by
                                                                                   constant / tuned-batch baselines
    Ensorain WTP-03 collider protocol           EXTRACT (pattern)   R1/R2    S     experience-stream replay, pair-block
                                                                                   recombination holdout, null ladder
    Ensorain arc3/suff sufficiency ladder       EXTRACT             R1/R2    M     exact-Bayes Even / golden-mean worlds = F3
                                                                                   seed; CSSR + EM-HMM = MEA-07 learners
                                                                                   (need hardening)
    Theseus synth                               RETIRE              -        NA    no world, no task; deep lane = random
                                                                                   matched programs
    herakles.evca (+ eca)                       HISTORICAL_CONTROL  R2/R4    S     pure, tested reconstruction of published
                                                                                   EvCA rules: WLD-21 / SCI-07 fixture

Answers to the brief's direct questions:

- Primary substrate: none. The closest structural relatives of the DGM are the PTE (deterministic integer register
  programs, oracle-checked) and the Z80 tapes (code = data). Neither has lifetime structural development, stable
  substructure ids under rewrite, an in-kernel provenance shadow, individual organisms (PTE sites are identical copies
  of one law) or a physics-ablation lattice on one path (ORG-04, ORG-08, ORG-20).
- Probe kernel: none qualifies. AGR-07 needs <= ~1.5k lines authored at computed class >= I2 with deliberately
  different conventions. Every candidate is same-family code that the Phase 3 builders (and this salvage pass) have
  read, so it is I1 at best under REP-06. The Z80 VMs and PTE also share exactly the conventions the probe is meant to
  differ from: zero-initialised registers and absolute/offset addressing (evidence/atl.md:362; z8.py:171; PTE
  engine.py:153).
- Familiar reference learner (AGR-08): none. Ares is the nearest "evolved plastic recurrent network", but it has
  non-standard two-port ops, no neuromodulation, at most 8 hidden nodes, float32 argmax ties and a held-out
  selection bug in its search. REBUILD a conventional evolved neuromodulated plastic RNN and a GRU meta-learner
  (S-M); Ares's stacked-array lockstep runtime is a design reference only.
- Second substrate: none (I2+ authorship required by AGR-07; none of these is I2 relative to the program).
- Bit-exact oracle pattern: EXTRACT. Ananke is the template, Aether adds mutation testing of the suite, and the Z80
  taint shadows add "observation-only shadow must equal the VM or the caller refuses". Required upgrades are listed in
  s4 and s8.
- Carrier attribution: EXTRACT the taxonomy and the lesion matrix (Ares carriers.py), not the code. It must be
  rebuilt against DGM hooks with matched-resampling ablation (CAU-01), declared dangling-pointer rules (CAU-02), shams
  that really are matched, and I1+ plants (MEA-02).

## 1. Method and what was actually verified

Read first: RSE_ARCHITECTURE.md, requirements.jsonl (all 180 ids; full text for ~60 relevant ones),
ENGINE_PORTFOLIO.md (E1, E10, experiment table). Seat dossiers (docs/phase3/intake/*/seats/{Ares, Ananke, Aether,
Nestor, Bellerophon, Archaeon, Tyche, Ensorain, Theseus, Herakles}.md) were used as locators. Then the source and tests
were opened (file list in the structured result).

Tests run (all from a scratch directory, PYTHONDONTWRITEBYTECODE=1, pytest -p no:cacheprovider, PYTHONPATH = worktree,
timeout <= 300 s; `git status` was clean before and after):

    suite                                                                  result
    ares/tests (test_ares.py, test_carriers.py)                            19 passed, 82 s
    prometheus/ananke/tests/test_oracle_selfcheck.py + test_conformance.py 110 passed, 13 skipped (CUDA-only graph
                                                                           replay and checkpoint tests), 52 s, CPU
    prometheus/ananke/tests/test_c1b_switches.py                           12 passed, 67 s
    prometheus/ananke/tests/test_lens_swap.py + test_lens_instruments.py   INCOMPLETE: 26 passed before the 300 s cap
    Aether/test/test_aeth03_variants.py                                    39 passed, 4 s
    Aether/test/test_aeth01_gpu_differential.py                            NOT RUN (needs `hypothesis`, absent)
    herakles/evca/tests/test_evca.py                                       60 passed, 20 s
    ensorain/arc3/suff/tests/test_worlds.py                                7 passed, 23 s
    prometheus/z80atlas/tests/{test_verify_exact, test_reg_world,
      test_forensic_regressions}.py (incl. v1 golden byte replay)          37 passed, 96 s
    Nestor z8taint vs z8 equivalence (tests/test_h3_material.equivalence,
      called in memory; main() not run because it writes a JSON into
      the repository)                                                      0 mismatches / 400 random programs
    archaeon/tests/test_lineage_attribution.py                             11 passed, 1 skipped, 17 s
    tyche/tests/test_v0.py                                                 14 passed, 22 s
    theseus/synth/tests                                                    NOT RUN (compile_g0 shells `git show` in
                                                                           the current directory)

Passing tests here are same-author tests. They show internal consistency, not independence or qualification.

## 2. Ares -- batched graph organisms (ares/substrate.py, worlds.py, search.py, develop.py)

What it really does. A population of P organisms is held as stacked numpy arrays: alive, op, bias, keep, W1, W2 and a
plasticity-rate matrix R (substrate.py:77-93). There are 17 node slots: 6 inputs, 8 hidden, 3 outputs
(substrate.py:18-19, 62-63). The runtime does `ticks` (default 2) synchronous updates per world step:
v = keep*v + (1-keep)*op(W1 v, W2 v, bias), clipped to +-8. Plastic W1 is updated by dW = R*v_i*v_j after every tick
(substrate.py:402-420). The action is argmax over three float32 outputs (substrate.py:419-420). There are 9 scalar
ops (substrate.py:20, 423-435). Mutation is 1 + Poisson(1) draws from 10 operators with fixed weights; keep is
clipped to [0, 0.98] (substrate.py:200-238, 297-301). Search is truncation + tournament + elitism with no crossover
(search.py:211-300). The W10 developmental arm grows the organism from a 4-rule x 11-field rewrite table for 4 steps
(develop.py:1-30). The worlds are 16 hand-written episodic tasks with present/absent/shuffled modes. The
best-studied world, W4, demands one bit held for about 37 steps.

Correctness evidence. 19/19 tests pass (run here). They cover determinism, fixed-policy floors, hand-wired cheat
controls on W2/W4, genome round trip, coevolution smoke and the catalogue wiring. All controls are by the same
author.

Defects (named):
- D1 is still in the code. The final champion is chosen ON the held-out set (search.py:291-294:
  `fit = rollout(pop, world, eval_seeds); champ = int(np.argmax(fit))`), and best_ever is also chosen on held-out
  (search.py:268-269). The cycle-0 and cycle-1 control readings were never re-derived.
- The float32 argmax readout breaks exact ties toward action 0 (substrate.py:420). Artemis R-17 found a bit held as a
  ~1e-22 residue that is read through such a tie. This is an unlisted channel (ORG-19).
- The keep clip at 0.98 (substrate.py:300) truncates the designated carrier's basin. The "narrow basin" result is
  partly this constant.
- Node ablation zeroes the node's rows and columns (substrate.py:545-560). That forces silence (CAU-01) and is blind
  to output-node self-loops (D3).
- The episode noise stream is keyed `sd ^ 0x5EED`, and arms share episode seeds without declaring it
  (search.py:71-73; REP-07).
- Only the champion's ancestry chain is persisted.
- No lifetime structural plasticity (ORG-04 fails), fixed ticks (ORG-05 metering only as a constant), no provenance
  shadow or stable ids (ORG-08), at most 8 hidden nodes.

Phase 3 role. HISTORICAL_CONTROL, slot R2 (plant library, canary injector, anti-calibration set).
(i) The W4 latch is a ready-made "latch for memory": per Nyx, a zero-hidden-node organism (output self-loop plus cue
    edge) that solves W4 at cap. MEA-16 names exactly this as the cheapest organism satisfying the memory clause
    without the property. Re-express it as a DGM plant.
(ii) D1 (held-out selection), D2 (best-of-N statistic), D3 (node-only ablation blind to output-side structure),
    D4 (shuffles balanced on the first binary only) and the float32 tie are documented failure classes for MEA-17
    canaries and SCI-07.
(iii) The substrate has exactly three cross-step channels (keep, cycles, plastic W1), so its closure is enumerable.
    That makes it a small known-answer closure for testing an ORG-19 audit.
Serves: MEA-16, MEA-17, SCI-07, ORG-19, CAU-05. Reference-learner use (AGR-08): rejected (s0).
Coupling: numpy only and imports nothing outside ares/. Read by nyx/readings/ares_w4_reading.py and an Artemis
script. receipt() shells `git rev-parse`. OS-neutral, CPU.

## 3. Ares carriers.py -- carrier attribution

What it really does. Edge- and SCC-aware carrier inventory and lesions for one genome.
- sccs() finds non-trivial strongly connected components from the boolean closure (carriers.py:28-49).
- _cut zeroes self-loops, recurrent edges, keep or plasticity (carriers.py:77-90).
- carrier_ablation runs the intact organism, each class cut, all cuts together (keep off + reset_each_step +
  plasticity off), each SCC cut and each recurrent edge cut (carriers.py:93-134).
- classify() returns NONE / REDUNDANT / RECUR / KEEP / PLAST / MIXED:<set>, where a cut "collapses" if the remaining
  gain is <= 25% of the gain over the floor (carriers.py:128-149).
- opportunity() estimates the probability that one mutation creates each carrier (carriers.py:156-187).
- Also: splice_carrier and transplant against a "matched random" subcircuit, and swap between lineages
  (carriers.py:221-343).

Correctness evidence. test_carriers.py passes (run here). It separates a hand-wired RECUR from a hand-wired KEEP
organism, finds the single carrier edge, sees an output self-loop that node ablation misses, moves that loop by
transplant, and binds the exclusion constraints. Plants: 3, same author (class I0 under MEA-02).

Defects:
- Every lesion is a zeroing, i.e. forced silence (carriers.py:77-90). CAU-01 requires matched replacement.
- random_carrier_like claims "the same number of recurrent edges" (carriers.py:272-275), but the code draws n_int
  random internal edges and never matches the recurrent count (carriers.py:291-293). It also zeroes plasticity, so the
  sham is not statistics-matched.
- swap() says it removes the host's carrier, but it cuts only recurrence and keep, leaving plasticity intact
  (carriers.py:332-333). The comment "free the donor's hidden slots" is not implemented (carriers.py:336), so the
  splice silently fails when the host has no free slots.
- External edges are re-attached at random (carriers.py:252-254, 265-268). There is no declared dangling-pointer
  rule and no null / host-corresponding / carried arms (CAU-02).
- The 25% threshold is a constant, not a preregistered SESOI. There are no confidence intervals and the method is
  single-organism.

Phase 3 role. EXTRACT the design into the R2 closure / lesion ruler, rebuilt on DGM intervention hooks:
- one lesion per carrier class listed by the ORG-19 closure audit, plus the joint lesion;
- the NONE / REDUNDANT / single / MIXED taxonomy;
- SCC-aware recurrent-edge masks;
- explicit coverage of output-side structure (CAU-05).
Replace zeroing with matched resampling. Add shams, preregistered thresholds and I1+ plants. The record's lesson that
the report author mislabelled MIXED as "redundancy" (Artemis D001-08) argues for the taxonomy being computed, never
narrated.
Serves: ORG-19, CAU-05, CAU-09, CAU-06 (after rebuild), CAU-01 and CAU-02 (only after the fixes). Cost S.

## 4. Ananke PTE -- engine, oracle, keyed RNG, interchange lens

### 4a. PTE engine + GA + envs + plants (prometheus/ananke/engine.py, physics.py, topology.py, envs.py, search.py,
plants.py, campaign.py)

What it really does. B batched worlds of N identical sites. Each site runs the same straight-line register program:
L instructions x 5 fields, 16 opcodes (engine.py:342-377), with up to 4 rule variants chosen by a rule pointer.
Sites talk only by lossy, delayed, summed packets held in a ring buffer Msum/Mcnt (engine.py:153-163, 483-549). All
state is int32/int64 torch. The tick order is fixed: delivery, sense, wake, run, economy, routing write, emission,
local mutation, ablation hooks, decay, readout (engine.py:268-472). CUDA-graph capture is used on GPU (engine.py:569-
594).

The GA has pop 48-96 and 20-36 generations. Selection fitness is accuracy plus declared shaping (search.py:94). The
champion is chosen by training accuracy on fresh worlds, then evaluated once on held-out worlds with a zero_comm
control (search.py:121-129). That champion discipline is correct, unlike Ares.

There are five 1-bit tasks of 12-16 trials. Hand plants (relay_flood, hold_latch, echo fixtures) live in plants.py.

Correctness evidence. See 4b. The physics is deterministic and bit-exact against an independent oracle on CPU here.

Defects (dossier corrections, consistent with the code read):
- Mirror pairs share all physics randomness (assays.py:54). That forces zero_comm to exactly 0.5, so COMM_DEPENDENT
  equals SIGNAL. The SIGNAL ruler (lo99 > .55) is cleared by a one-shot flood latch (~.58).
- physics_from_levels mislabelled 951 of 1589 C1 global rows (fixed 09-30).
- twin_assay measured reach from sensor column 0 only (fixed).
- Decay is a sign-asymmetric arithmetic shift (engine.py:444-445): positive values stall at 2^k-1.
- No lifetime structure change. The graph is fixed per physics, and sites are not individuals.
- launch.py depends on Windows schtasks plus a detached worktree. Run state lives outside git (~/ananke_runs on M1).
- The Wave-2 certification stack (attainability certifier, mutation gate, light-cone ceilings) was never promoted
  into the package.

Phase 3 role. HISTORICAL_CONTROL, slots R4/R2. The architecture's binding constraint 2 cites this exact record:
plants solved FLIP (.978) and XOR (.850), yet the GA (96 x 36) never found them. Packaged with its plants, the PTE is a
ready known-answer fixture for the PRS-03 reachability estimator and the X6 needle-inflation method:
- planted solutions at known operator distance;
- a known search miss;
- a deterministic CPU-runnable physics.
The flood-latch and mirror-forced-control cases also belong in the WLD-17 sealed known-answer set
("one-shot-latch-solvable" worlds) and in MEA-03 (one-shot latch rung).
Serves: PRS-03, WLD-17, MEA-03, SCI-07. Cost S.

### 4b. Independent CPU oracle + conformance harness (oracle.py, tests/test_conformance.py,
tests/test_oracle_selfcheck.py)

What it really does.
- oracle.py (511 lines) is a pure-Python, arbitrary-precision re-implementation written from DESIGN.md. Its docstring
  states that the author did not read engine.py. It records 19 spec ambiguities, each ruled normative
  (oracle.py:17-96).
- test_oracle_selfcheck.py hand-derives known values for hash32, H, all 16 opcodes, the topologies, LM, relay arrival,
  loss, aloha/saturate and determinism.
- test_conformance.py draws 40 random physics x random genomes x random sense and compares every state array, the S0
  trace and the stats counters for equality (test_conformance.py:68-90). It adds 40 forced-emitter transport configs
  (177-193).
- A vacuity check flips one bit of one world seed and requires detection (test_conformance.py:100-115).
- A default-Controls digest must equal the no-Controls digest, and zero_comm must change it
  (test_conformance.py:135-158).

Correctness evidence. 110 passed, 13 skipped (run here, CPU). The skipped tests are the CUDA graph-replay and
checkpoint/resume tests, so snapshot/restore bit identity was NOT verified here.

Gaps:
- oracle.run(phys, genomes, world_seeds, sense, T) has no Controls argument (oracle.py:277). None of the intervention
  channels are differentially tested: reset_parts, flush_inflight, drop_packets, shuffle_dest/time,
  randomize_payload, distractor, freeze_rule, census. They are the instruments, and only engine-vs-engine unit tests
  cover them (test_c1b_switches: 12 passed here).
- Authorship independence is declared, not computed. REP-06 I2 requires sandbox logs and a spec-only brief. As it
  stands it is a same-family reference, which is exactly the REP-02 CORE part, not the I2 reimplementation.

Phase 3 role. EXTRACT (pattern + harness template) for the DGM slow reference interpreter (R3) and the R0 replay
tests. Required changes:
- the reference must also implement every intervention operator and the provenance shadow;
- mutation-test the differential suite (borrow Aether's mutants, s5b);
- run the snapshot/restore test on the CPU path in CI;
- log the authoring sandbox so the independence class can be computed.
Serves: REP-02 (CORE part), CMP-01, REP-01, MEA-05 (vacuity check), ORG-08 (snapshot/restore). Cost S.

### 4c. Counter-hash keyed streams (prometheus/ananke/rng.py, 62 lines)

What it really does. H(k1..kn) chains a 32-bit integer hash over (world seed, stream id, tick, site, sub-index), with
11 named streams (rng.py:16-62). The randomness is stateless: it never reads state, so twins and arms differ only
where their keys differ. torch, host and oracle forms agree bit for bit (exercised by the conformance tests).

Phase 3 role. EXTRACT nearly verbatim into R0 as the keyed-stream primitive. Add a numpy/compiled form for the DGM
kernel and a stream-registry validator (REP-07 "two arms sharing a stream undeclared: launch refused"). Caveat: a 32-bit
hash is fine for keyed draws, but its period and collision properties should be checked against the expected draw
counts.
Serves: REP-07, REP-01, ORG-08, ORG-20 ("arms differ only by switches and keyed random streams"). Cost S.

### 4d. Mirror-twin interchange lens (lens.py, lens_swap.py, swap_rel.py, inference.py; Controls in engine.py:33-88)

What it really does. Between ticks, lens.swap copies named state arrays between mirror partners b and b^1. The partners
share all exogenous randomness and have negated cues (lens.py:27-45). roll_slots / roll_recipients perturb in-flight
packets. lens_swap runs single-trial swap arms and an S/C/N mixture census. swap_rel computes a relative swap
certificate with a studentized pair bootstrap. Controls consume only their own CTRL stream, so a control run differs
from its twin only in the ablated channel (engine.py:12-14).

Correctness evidence. Partial. The lens tests did not finish within 300 s here (26 passed before the cap). The
dossier records that the swap instrument was repaired five times in three days. Known defects:
- site_acc + chan_acc ~ 1 is a mirror-pair identity;
- a verdict names the reader's register (presence read as content);
- every-trial swaps break identity;
- 24/98 no-op arms forced NO_EFFECT.

Phase 3 role. EXTRACT the pattern for the R2 interchange ruler (CAU-04/CAU-09): exact state interchange between twins
that share every exogenous draw, with the carrier named by a state array and a tick. Do not lift the code. Its
statistics must move to the MEA-11 library and pass known-answer tests, and its identities must be qualified on
planted organisms first. The Controls-own-stream discipline is the in-miniature version of the ORG-20 regression-hash
gate. Cost S.

## 5. Aether -- byte lattice and verification kit

### 5a. aeth01.v1 lattice physics + AETH-03 variants (Aether/test/reference/gpu_aeth01.py, oracle_aeth01.py,
observatory/aeth03_variants.py, aeth03_propagation.py)

What it really does. A 2-D torus of sites, each with five uint8 fields. The only active opcode is WRITE, 1 of 256 byte
values. An energised WRITE site proposes a byte into one field of one von Neumann neighbour. Contests are decided by a
splitmix64 hash of (seed, tick, target, field, source). A hash-keyed bit flip is injected, and energy is
debited / decays / is replenished (gpu_aeth01.py:111-197). The 16 variants each change one phase. They are dispatched
by name in one function with per-variant branches (aeth03_variants.py:135-310). There are no organisms, no task, no
selection and no objective.

Correctness evidence. test_aeth03_variants: 39 passed here, including test_shared_path_is_v1_bit_for_bit
(test_aeth03_variants.py:58-74), which checks every field and the observer stream for equality. The CPU-oracle vs
GPU-shaped differential was not run here (missing `hypothesis`).

Defects:
- The propagation docstring claims generation is "the length of the shortest causal chain"
  (aeth03_propagation.py:15-24). The seat's own audit showed it is a lower bound.
- The gpu_aeth01 docstring still says "NOT TESTED ON REAL GPU HARDWARE" (gpu_aeth01.py:17-19).
- There is an irreducible 3.04% energy leak per 5,000 ticks with costs at zero.
- About 92% of the medium freezes. Only one energy regime was ever run.
- The aether/ vs Aether/ case collision on Windows.

Phase 3 role. RETIRE as a substrate: it has no organisms, no demand and a frozen medium. It is not a candidate second
substrate (same-family authorship, no task).

### 5b. Aether verification kit (oracle_aeth01 vs gpu_aeth01 differential; reference/mutants.py + golden_vectors.py;
v1g shared-path test; twin propagation assay; observatory/aeth03_unit.py)

What is reusable:
(i) Two structurally different implementations restated from one spec, differentially tested.
(ii) mutants.py: deliberately broken implementations, one per plausible bug (min-priority, signed-priority, ...),
    which the suite must reject (mutants.py:1-40, test_mutants.py). This is exactly MEA-05's "code checkers that gate
    claims are mutation-tested in CI", applied to the reference/kernel differential corpus.
(iii) A variant layer whose baseline route is proven bit-identical to the frozen kernel before any single change is
    layered on. This is the motivating precedent of ORG-20.
(iv) A one-bit twin assay that checks locality on every tick and voids the result on any violation, with a
    flip-twice null self-test (aeth03_propagation.py:52-56).
(v) Unit receipts with sha256 over LF-normalised code and canonical result JSON that excludes host fields
    (aeth03_unit.py:1-30, 55-68).

Phase 3 role. EXTRACT the patterns: (ii) into the REP-02 corpus discipline, (iii) into the ORG-20 regression-hash
gate, (v) into R0 receipts. Note that the ORG-20 gate must go further than Aether: there is a per-switch regression
hash on switch-irrelevant runs, not only one baseline route. Also, PRV-01's canonical form is the git blob, not plain
LF sha256.
Serves: ORG-20, REP-02, MEA-05, PRV-01, CMP-04. Cost S. The RunPod platform under Aether/runpod was not evaluated
(infrastructure, outside this group; its credential modules were deliberately not opened).

## 6. The Z80 triplet (three ISAs from one directive)

Common facts. All three are same-family byte VMs with dense opcode spaces (undefined bytes are NOPs). All have
zero-initialised registers by default, a block-copy primitive and a neighbour / partner window. evidence/atl.md:29-32
and :396 already rule that agreement among them is one design family agreeing with itself. None can be a probe kernel
or a second substrate (s0).

### 6a. Nestor Z8 / NPE (roles/Nestor/campaigns/z80atlas-verify-2026-09-22/z8.py, world.py, p11.py)

What it really does. A pure-Python, Z80-flavoured, variable-length ISA in an arena:
- Every write goes through a sandbox policy OWN / ARENA / FREE (z8.py:146-157, 178-204).
- ED-prefixed world ops are gated by an ops mask: ALLOC, BIRTH, SELF, GETPC, SENSE, SPLIT, LDIR, LDDR (z8.py:18-31,
  160-166).
- Registers, flags and PC persist across slices. Fresh registers are zero (z8.py:171).
- There are per-position provenance hooks (z8.py:118-124).
- world.py (1,439 lines) holds pair-tape / soup / grid / graph worlds and a 16-factor grammar.

Correctness evidence. selftest_z8 positive controls exist (not run here).

Defects (dossier, partly visible in code):
- Fidelity is measured after _mutate, so 6,287 of 6,547 RECOMBINATION events were splice-made copies (Z80A-D05).
- The validation cache is keyed on genome bytes only, which leaks across niches.
- Both critical anticheat guards can never fire.
- Z8_SLOTTED ignores the mutation operator.
- "1,031 spontaneous replicators" collapsed to about 2.
- Pure-Python throughput.

Phase 3 role. HISTORICAL_CONTROL, slot R2 canaries and painter plants. The failure classes "copy made by the
variation operator", "pair-tape identity read as heredity" and "competence certified from zeros" are exactly what
MEA-16's "painter for heredity" and MEA-17 canaries need. The CARRIED/ZERO/CONST/RANDOM register-reset axis is a
reusable control idea for ORG-19's "initialisation values" channel.
Serves: MEA-16, MEA-17, SCI-07, PRV-10, ORG-19. Cost S.

### 6b. Bellerophon BEE (prometheus/z80atlas/)

What it really does. A 256-byte address space per execution: own tape, partner window, input bytes at 0xE0 and output
bytes at 0xF0. Every address is taken mod 256 (vm.py:1-20). There are about 45 opcodes, real Z80 LDIR, and an
LDIR on/off/cost4 switch (vm.py:96, 120). World physics versions are gated by Config.physics, with v1 kept
byte-replayable. Most of its life used the v3 copy-resource ledger with ON / OFF / SHUFFLED / RANDOM_REWARD / YOKED /
IRRELEVANT / DELAYED arms.

Correctness evidence. 37 passed here, including the v1 golden byte replay (test_forensic_regressions.py:25-44) and
verify_exact == verify_tape on 300+ tapes across all tasks, gates and layouts.

Defects:
- LDIR with C=0 sweeps 256 bytes plus an ~80% NOP slide, so replication is an engineered basin.
- glineage is assigned by resemblance (world.py:562; DEF-BEL-008).
- Hidden world copies under endogenous physics (P1, repaired in v2).
- Superlinear cost with horizon.
- Raw evidence is host-local on M2.

Phase 3 role. HISTORICAL_CONTROL. Two discipline records worth copying into requirements practice rather than code:
- the YOKED equal-total contingency control (evidence/atl.md:380: ON vs YOKED extinction 1 vs 67/150);
- v1-golden plus gated physics versions.
The LDIR-off ablation (8/300 -> 0/300) is a clean ORG-21 / AGR-15 "affordance created the result" fixture.
Serves: MEA-17, SCI-07, PRS-12 (YOKED control idea), AGR-15. Cost S.

### 6c. Archaeon z80atlas (archaeon/z80atlas/vm.py, engine.py, census/, denovo/)

What it really does. A 141-line VM in which every byte decodes (op = byte & 31). The neighbour window at 128 is the
only place descendants can be caused (vm.py:1-50). The engine asserts births == endogenous births.
census/copier_census.py measured exact copier density in random vmcopy32 tapes: 9.6e-6, with 0 on real-Z80 tapes
(evidence/atl.md:90).

Defects:
- All 26 headline "spontaneous_replication" flags were transplanted lineages.
- The sampler drew 0 of 209 bare-niche configurations.
- test_z80atlas_provenance.py:257 hardcodes a D:\ host path.

Phase 3 role. HISTORICAL_CONTROL, slots R2/R4. The census is a measured random-sampling hit rate at plant length,
which is precisely PRS-03(d), and a worked example of a two-sided classifier (0 on one ISA, 96/1e7 on another). The
26/26 transplant misreading is the PRV-10 canonical case.
Serves: PRS-03, PRV-10, MEA-17, SCI-07. Cost S.

### 6d. Material-taint shadow interpreters (Nestor z8taint.py; archaeon/lineage/taint_vm.py + core.py)

What they really do. Each is a line-for-line copy of its VM that carries a tag per byte and register:
- Nestor: the niche in which the VALUE was made (z8taint.py:1-40).
- Archaeon: E(p) / N(q) / I / K / Z atoms, and X(set) for computed values (taint_vm.py:1-20).
Both must equal the VM exactly or the caller refuses attribution.

Correctness evidence. 0 mismatches over 400 random programs for z8taint (run here). test_lineage_attribution: 11
passed, 1 skipped (run here; includes a taint-vs-VM differential). The dossier reports a 9/9 vs 4/9 ruler tournament
for material vs id-based heredity rulers.

Phase 3 role. EXTRACT the pattern, not the code. The DGM must carry its provenance shadow in-kernel from day one
(ORG-08), and DEV-14's write-provenance tracer needs the same "tags flow with data; computed values are new material;
observation never alters physics; differential equality or refuse" contract. These shadows show what the contract
looks like. They also show its blind spot: a copy shadow is a copy of the VM, so it shares the VM's bugs. Pair it with
an intervention confirmation (DEV-14 "trace plus intervention confirmation").
Serves: ORG-08, PRV-10, DEV-14, DEV-12, CAU-02 (persistence / execution / competence reported separately). Cost S.

## 7. Tyche -- lens DAG chemistry

### 7a. Lens ecology (tyche/lens.py, ecology.py, organisms.py, worlds.py, v1/, v2/)

What it really does. A lens is a causal feed-forward register program of up to 48 instructions over 27 ops: delay,
windows, accmod, fsm, xor, ... (lens.py:1-23, 115-140). Its output columns are appended to the inputs of a fixed weak
classifier: ridge, depth-4 tree or a median-split table. Selection keeps lenses that raise held-out accuracy
(ecology.py), under eps-lexicase. The worlds are boolean or modular functions of delayed i.i.d. inputs, plus Hecate
finite systems. Prediction only: there are no actions.

Correctness evidence. tyche/tests/test_v0.py: 14 passed (run here). These include causality of random lenses, the LEAD
cheat being caught, planted laws attainable while twins stay dead, and lexicase keeping specialists.

Defects:
- The chemistry contains the generators' own primitives (xor, delay, accmod, wsum, fsm), so success measures
  reachability of the author's construction.
- The v0 tab feature budget manufactured residuals.
- The v2 OV clock censored nearly everything.
- Parity-3 (5 instructions) was never reached.

Phase 3 role. HISTORICAL_CONTROL, slot R2. It is a ready planted GRAMMAR-BORNE case for AGR-15 (the grammar
contains the target; re-search under a random basis should inflate description length) and a PRS-03 needle case. It
has no organism role: the classifiers are fixed, and ORG-17 would reject capability supplied by the chemistry.
Serves: AGR-15, PRS-03, SCI-07. Cost S.

### 7b. Audits and certificates (tyche/audits.py; worlds.py tsd/prf kinds; v2/certify.py)

What is reusable:
- causality_audit replaces the future at 5 cuts with fresh random values and requires bit-identical outputs up to
  each cut (audits.py:26-38).
- cheat_control requires that a LEAD-op lens is seen by the gain channel AND rejected by the audit, while an honest
  delay lens passes (audits.py:41-59).
- Structure-destroyed twin worlds and keyed-PRF worlds are must-stay-flat negatives.
- certify.py gives subset-MI "lowest informative order" certificates against a permutation null
  (certify.py:33-104).

Defects. The permutation null is the 99th percentile of 20 permutations (certify.py:44-47), effectively the
maximum of 20, which is a weak null. Plug-in MI is biased at small counts. The certificate is empirical, not
bound-typed (WLD-01).

Phase 3 role. EXTRACT into R1:
- the future-replacement audit is one channel of WLD-07's differential all-channel leak audit, and its cheat
  control is the template for "a planted leak on each channel must be detected";
- tsd / prf twins belong in the WLD-17 sealed known-answer set and the MEA-03 shuffled-structure rung;
- the order certificate needs hardening (exact computation where the law is a table, proper nulls) before it can
  type anything.
Serves: WLD-07, WLD-17, MEA-03, MEA-05, WLD-01 (partial). Cost S.

## 8. Ensorain -- tensor-train / regressor substrates and the sufficiency ladder

### 8a. TT substrates E0-E2, D1 dials, LM01 (ensorain/e0, e1, e1p5, e2, d1, lm01)

What it really does. A single organism walks a 4096-cell graph whose values are a hidden low-rank tensor-train field.
It predicts exit values from a bounded TT (or rival) memory and moves by a FIXED hand-coded epsilon-greedy policy
with tabu (e0/life.py:1-30; e0/tt.py NLMS updates on TT cores). D1 is a randomized dial search. LM01 was frozen twice
and never launched.

Defects:
- E1.5's only "positive" (TT beats a matrix on a TT-generated world) was called a tautology by the seat itself.
- The founding directive was truncated, so the critical measurement was improvised.

Phase 3 role. RETIRE. Online regression over cell addresses under a fixed policy fails ORG-04 and ORG-17, and the
worlds certify nothing (WLD-01).

### 8b. WTP-01..03 foundry (ensorain/wtp, wtp2, wtp3)

What it really does. A JSON "world genome" (34 field / observation transforms, 10 memory substrates, 7 learning
rules, 7 fixed search policies) builds tensor-cell regression worlds and scores memories.

Record:
- WTP-01's top anomalies were a variance-collapse artefact of a ruler normalised by current field variance.
- WTP-02's sole EXPAND specimen was a one-float running mean, killed post-data by a constant-predictor test.
- WTP-03's 9 promoted specimens were beaten by a post-data tuned batch fit (N6).

Phase 3 role. HISTORICAL_CONTROL, slot R2. These are three clean, documented ruler false positives, each killed by a
MEA-03 rung (constant, optimal constant, same-class tuned batch estimator). Their committed specimen rows are ready
MEA-17 canary material and SCI-07 calibration items.
Serves: MEA-03, MEA-17, SCI-07. Cost S.

### 8c. WTP-03 collider protocol (ensorain/wtp3/collider.py)

What is reusable (collider.py:1-15, 165-215), as protocol:
(i) One experience stream per (world, seed), generated by a fixed behaviour carrier and replayed to every substrate
    and null. This is acquisition matching from the same experience.
(ii) A pair-block recombination holdout: every held value is seen alone, no pair of held values ever co-occurs, and
    the test set is the held block. Tested by test_holdout_never_shows_a_pair; not run here.
(iii) A null ladder: zero, constant, recent constant, marginal, linear, bounded lookup, best simple substrate, plus
    the post-data tuned batch N6.

Phase 3 role. EXTRACT the protocol, not the tensor-cell code:
- (i) is the MEA-07 / MEA-14 acquisition-matched comparison;
- (ii) is a generator rule for F6 (pair-block recombination holdout) and TRF-02;
- (iii) maps onto MEA-03 rungs.
Serves: MEA-07, MEA-14, MEA-03, TRF-02, WLD-03. Cost S.

### 8d. arc3/suff sufficiency ladder (ensorain/arc3/suff/worlds.py, learners.py, cssr.py, hmm_learner.py, cssr_em.py)

What it really does.
- Worlds with EXACT Bayes predictors and declared sufficient statistics (worlds.py:1-195):
  - iid with known p;
  - Beta-Bernoulli;
  - order-k Markov with unknown table (per-context Beta posterior);
  - finite HMMs with forward filtering, including the Even process (2 causal states, infinite Markov order;
    worlds.py:132-137), the golden mean (order-1 control; worlds.py:140-144) and the simple nonunifilar source;
  - a key-value long-tail stream.
- Learners: STAT(k) / KT, verbatim windows, PPM-like NEAREST, CSSR (state merging), HMM_EM (Baum-Welch with restarts),
  CSSR initialised EM.

Correctness evidence. test_worlds.py: 7 passed (run here).
- Even and golden-mean Bayes log-loss converge to the analytic entropy rate 2/3 bit within 0.01.
- The Even process has no finite window.
- STAT(k) equals Bayes at the true order to 1e-9.

Defects:
- Split-mode CSSR collapses to the window floor on the Even process (excess .034 vs the k=6 floor .0315).
  Determinization drops the oldest symbol (CSSR_T25.md readings 1-3).
- Vote mode fixes Even but fails catastrophically on Markov order 3.
- The learners are predictors, while MEA-07 asks for controllers.
- The test file builds an unused array (test_worlds.py:28).

Phase 3 role. EXTRACT into R1 and R2:
- the worlds module is the seed of anchor family F3 ("hidden-state process pair (Even-like vs golden-mean-like) with
  exact Bayes; d_mem exact via causal states") and of WLD-04 exact solvers, with its tests as known-answer tests;
- STAT / CSSR / HMM_EM are exactly the ">= 2 generic FSC/PSR learners, e.g. state merging and EM-trained HMMs" of
  MEA-07, but they must be HARDENED: fix or replace the CSSR determinization, qualify both on the known-answer worlds,
  and extend from prediction to control-from-the-same-experience;
- the Bayes predictors give TRF-02's B_C for these families.
Serves: WLD-04, WLD-01, MEA-07, MEA-11, TRF-02, WLD-17. Cost M (worlds S; learner hardening plus control extension M).

## 9. Theseus synth (theseus/synth/)

What it really does. 1-D reaction-diffusion-style rule lists over a 4 x 32 field for 128 steps, with 19 ops
(substrate.py:1-70). "Collisions" splice parents' rules. The "concept tensor" gain is 2*tanh(<u_i, w_j>), which
depends on ONE parent and ONE position, so there is no cross-index coupling (collide.py:14, 68, 82).

Seat's own findings:
- "Transfer" is 1 minus a mean of fingerprint entries.
- The DEEP lane's minimum depth to G0 is 2.
- Niche, mechanism and lens rulers do not separate matched random programs from deep descendants.

Tests not run (compile_g0 shells `git show` in the cwd). Coupling: imports tyche.lens; reads agents/nous concepts via
git.

Phase 3 role. RETIRE. There is no world, no demand and no organism, and its single lesson (generation counts inflate
depth; random matched arms are mandatory) is already encoded in the requirements (AGR-14, PRS-03(d)).

## 10. herakles.evca (+ eca) (herakles/evca/core.py, genomes.py, derive.py; herakles/eca/)

What it really does. A pure library evaluating radius-3, 128-entry binary CA rule tables on odd periodic rings for
density classification and related criteria. Every convention is pinned and enforced:
- MSB-leftmost neighbourhood order re-derived from maj and GKL in a test;
- no default step count;
- even N refused;
- accuracy "at T" vs fixed-point reporting;
- bounded witness with visible truncation;
- reflection / complement equivariance (core.py:1-80).
The historical genomes (maj, GKL, particle rules, ...) are embedded and checked against the specimen JSON.

Correctness evidence. 60 passed (run here). The tests include the independent-oracle step check, golden results,
a side-effect-free import, input non-mutation and instrument controls. The library is widely imported
(archaeon campaigns, proteus mint, evidence_wiki, nyx).

Defects. One task family and r=3 only. The 1990s EvCA GA ("Stage 1") was never re-run, so the published
reachability of particle strategies is NOT reproduced in-house.

Phase 3 role. HISTORICAL_CONTROL, usable as is as a known-answer fixture.
- WLD-21: a verified reconstruction of externally sourced rules and results.
- SCI-07: a true-but-surprising literature result (evolved emergent distributed computation; particle strategies
  are rare) that kill paths must not kill.
- PRS-03: a published external reachability datum. It becomes a full R4 known-answer test only if a preregistered
  EvCA GA reproduction is built (M).
Serves: WLD-21, SCI-07, PRS-03, MEA-11 (golden fixtures). Cost S.

## 11. Cross-cutting EXTRACT list (what to lift, in priority order)

1. Bit-exact reference + conformance discipline (Ananke 4b + Aether 5b). This is the template for the DGM slow
   reference interpreter. It is non-negotiable that the reference cover every intervention operator and the
   provenance shadow, that the differential corpus is mutation-tested, that a vacuity check is included, that
   snapshot/restore is tested on the CPU path, and that authoring is sandbox-logged so REP-06 can compute the class.
2. Counter-hash keyed streams (rng.py). Lift nearly verbatim into R0, with a stream registry and validator.
3. Shared-path bit-identity gate (Aether v1g, Ananke default-Controls digest). Generalise to a per-switch regression
   hash for the ORG-20 lattice.
4. Carrier-class lesion matrix + taxonomy (Ares carriers.py). Rebuild on DGM hooks with matched resampling, shams and
   I1+ plants.
5. Twin-world exact interchange (Ananke lens). Becomes the R2 interchange ruler after MEA-11 statistics and planted
   qualification.
6. Material-taint shadow contract (Z80 taint VMs). Becomes the in-kernel provenance shadow and the DEV-14 tracer
   contract, with intervention confirmation.
7. Future-replacement causality audit + cheat control (Tyche). One WLD-07 channel and its planted-leak template.
8. Exact-Bayes hidden-state worlds + generic FSC learners (Ensorain suff). F3 seed and MEA-07 baselines after
   hardening.
9. Experience-stream replay, pair-block holdout, null ladder (Ensorain collider). MEA-07 / MEA-14 / F6 / MEA-03
   protocol.

HISTORICAL_CONTROL corpus to seal (R2 plant / canary / anti-calibration library, authored or re-expressed at I1+ per
MEA-02):
- Ares W4 latch;
- the Ares D1-D4 defect classes and float32 tie;
- PTE plants with GA misses, the flood latch and the mirror-forced zero_comm;
- NPE splice-made copies and pair-tape identity;
- BEE LDIR-off ablation, YOKED arms and golden v1;
- Archaeon copier census and the 26/26 transplant misreading;
- Tyche grammar-contains-target and the parity-3 miss;
- the WTP-01/02/03 ruler false positives;
- herakles.evca published rules.

## 12. Retire list

- Aether aeth01.v1 lattice as a substrate.
- Ensorain E0-E2, D1, LM01.
- Theseus synth.
- Every engine in this group as an organism substrate: the GA loops, the campaign drivers and the world sets are
  toy-grade (one-bit or one-byte demand), and the Phase 3 substrate, worlds and search are new builds.
