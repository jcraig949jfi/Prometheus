# Salvage worker report: scope 2, non-program substrates and designed learners

Deposited by Dionysus[m1-3815a3b9] on 2026-10-01. The worker's transcript
file is empty on this host, so the text below was copied by Dionysus from the
worker's final message as it arrived in the session. It is meant to be
verbatim; any slip in copying is Dionysus's.

Brief: roles/Dionysus/prompts/2026-10-01_salvage_workers/00_COMMON.md and
02_SCOPE_other_substrates.md. Worker model: opus, read-only.
Worker usage as reported by the harness: 611,569 tokens, 163 tool uses,
about 25.9 minutes.

Search-rule note. This worker finished before the holdout pathspec correction
was sent (see 00_SEARCH_RULE_INCIDENT.md). Its searches used the brief's
directory-only exclusion and were not audited afterwards.

This is a worker's fact sheet. Its claims are the worker's, graded by its own
VERIFIED BY ME lines. Where SALVAGE_MATRIX.md relies on one, it says so.

----------------------------------------------------------------------

The worker's covering note:

I verified the main facts against source for all nine components. Four findings contradict or add to the dossiers:
- PTE was tested on a second host. Its conformance suite passed there, even though the Ananke dossier says RunPod was never used.
- A tensor-network organism family exists that scope 2 did not name. It is under primordial/brain.
- No plastic network keeps its weights across episodes. The closest candidate is Ares, and it resets its weights every episode.
- Aphrodite's engine as built is the fixed-procedure negative control for RECURSE. It cannot serve as the positive.

SCOPE 2 SALVAGE FACTS: non-program substrates and designed learners
Worker for Dionysus[m1-3815a3b9]. Worktree dionysus-base-role at e3d7c7034. Read-only. 2026-10-01.
Every search excluded holdout and nestor_secrets paths. No credential file was opened. Aether/runpod/prometheus_gpu/credentials.py, secrets.py and roles/Aphrodite/engine/accel/azure/azure.env were seen in file listings only.

COMPONENT: Ananke packet-tensor engine (PTE): substrate, CUDA tick, CPU oracle
PATHS: prometheus/ananke/{engine,physics,rng,topology,oracle,plants,envs}.py; prometheus/ananke/tests/test_conformance.py, test_oracle_selfcheck.py; roles/Ananke/pte/DESIGN.md; roles/Ananke/research/harvest/H-PLANT/hp_plants.py
OWNER / DATES: Ananke (M1). prometheus/ananke has 25 commits, from 2026-09-24 06:52 (7b6958b1c, engine and oracle together) to 2026-09-30 23:00 (86b84227a).
WHAT IT REALLY DOES: The engine runs B worlds per batch. In each world, N sites run one shared straight-line integer program: up to 4 rule variants x 16 instructions, 16 opcodes including SETRULE and WIMM. It is vectorised by gathering from a 16-candidate result stack. Emitted payloads are summed per (recipient, channel) into an in-flight ring with counter-hash loss, latency, duplication and noise; packets carry no sender identity. State the organism can write during its life: registers S, immediates Kp, rule pointer r, routing weights w, energy. The "organism" is the whole homogeneous law in one world. The environment is a pre-drawn, open-loop SENSE schedule, and the action is sign(S0) at one read site, so nothing the organism does changes its inputs.
SIZE: 20 non-test files, 6,130 lines (substrate core 877, oracle 511). 164 test functions in 25 files under prometheus/ananke/tests.
DEMONSTRATED CORRECTNESS:
- A separately written pure-Python-int oracle, built from DESIGN.md. Engine and oracle are bit-identical on 40 random physics configs run eagerly, 12 under CUDA graph, and 40 forced-emitter transport configs.
- A must-fail control (one flipped seed bit must be caught).
- Checkpoint/resume equals an uninterrupted run.
- 28 oracle self-tests with hand-derived expected values.
- Second host: RunPod RTX 4000 Ada, Linux, torch 2.4.1+cu124, commit ee81c0474, "139 passed in 34.62s" (Aether/runpod/receipts/ananke-conformance-20260927T151608Z/result.json).
Known defects:
- Physics dials are converted from floats at setup (physics.p16 = round(p*65536); survival thresholds use float pow).
- A 28-line block clock solves the FLIP world at 1.000, and copy policies reach balanced accuracy .75 (roles/Ananke/pte/C1_ERRATA.md E-W6, E-W17).
INTERFACE: World(ph, genomes[B,G,L,5], world_seeds, device, ctrl, schedule).run(T) or .step(). checkpoint()/restore() work on the whole batch; digest(per_world) is available. Controls can reset or flush each carrier (S, inbox, Kp, w, En, r, in-flight). Deterministic; int32/int64 per tick. Scoring in envs.score uses floats (0.5 credit when S0 == 0). No model call.
THROUGHPUT / SCALE:
- GPU: "~11M site-updates/s at L=16, ~21M at L=8", RTX 5060 Ti with CUDA graph (roles/Ananke/journal/2026-09-24.md line 105).
- RunPod (timing taken by the wrapper, not Ananke): up to 32620936.7 site-updates/s (graph, B=2048, torus N=25), in the same result.json.
- CPU: "~3350 world-ticks/s", 1 thread, 128 worlds x 100 ticks, N not stated (roles/Ananke/research/harvest/H-CHK/LOG.md A1).
COUPLING: Imports torch and numpy only. It is imported by the archaeon/causal_lens adapters and by Aether's foreign conformance runner. Campaign state lives off-repo (~/ananke_runs). launch.py uses Windows schtasks.
FIT TO SLOT: message-passing open arm (RSE 6.4).
- Meets as is:
  - ORG-06.
  - ORG-08, except there is no lineage key in the randomness and dials are float-converted at setup.
  - REPR-01 in substance (engine equals oracle on a second host), although no golden trace was compared across hosts.
  - DEV-05 tooling (checkpoint, and mirror twins that share every exogenous draw).
- Fails:
  - ORG-01: no step(obs) returning an action, no store declaration, no genome bits.
  - ORG-02: resets exist only as ablation switches; there is no episode boundary.
  - ORG-09.
  - DEV-01: one episode is the whole life.
  - COMP-01: the design is GPU-first; the CPU path is eager torch.
- Special question: no evolved capability above HOLD is on record.
  - Evolved results (dossier): one-hop relay; 1-bit local latches; the M2 in-flight echo, a HOLD tuned to the trained gap; once-per-episode flood latches. XOR SIGNAL 0/83, FLIP SIGNAL 0/82. Retention across trials NO, but the tasks never demanded it.
  - HOLD plants: plants.hold_latch (9 lines, local) and plants.echo_hold (the bit is held only in flight, so flushing in-flight packets must kill it).
  - ADAPT-like plant: hp_plants.p_flip (16 lines, .978 at physics d9cc; teacher-zeroed must-fail .500). It lives in a world that cannot certify ADAPT, because of the block-clock impostor.
MODIFICATION COST: L.
- Work items:
  - A closed-loop adapter (per-tick SENSE injection, S0 readout, eager path).
  - Store declaration and episode resets through the existing Controls.
  - Genome-bit accounting.
  - A compiled CPU kernel, re-certified against the existing oracle.
  - New multi-bit HOLD and ADAPT plants.
- Rebuild comparison: an equivalent integer message-passing kernel with an independent oracle is M. A rebuild would have to re-earn the 19 DESIGN ambiguity rulings and the cross-host record.
VERIFIED BY ME:
- Checked in source: engine, physics, rng, topology, envs and plants read in full; oracle header; conformance tests; RunPod result.json; throughput lines; C1_ERRATA E-W6 and E-W17; hp_plants and H-PLANT report s3; imports; dates; counts.
- From the dossier only: how independent the oracle author was; the evolved-mechanism catalogue; the retention result.

COMPONENT: Aether byte-copy lattice (aeth01.v1 and the AETH-03 variant laws)
PATHS: Aether/test/reference/oracle_aeth01.py, gpu_aeth01.py; Aether/runpod/aeth01_canary/aeth01_gpu_kernel.py; Aether/observatory/aeth03_variants.py, aeth03_propagation.py, aeth03_unit.py; ops/campaigns/C-002/E-007/
OWNER / DATES: Aether (M2, then BUCKKEEP). Aether/ has 124 commits, from 2026-09-20 08:17 (6a5ba2b56) to 2026-09-30 06:25 (1b4fb4523).
WHAT IT REALLY DOES: A synchronous 2-D torus where each site holds 5 uint8 fields (opcode, arg0, arg1, payload, energy). Only opcode 0x01 acts. A site with energy >= write_cost proposes writing its payload into field (arg1 mod 5) of neighbour (arg0 mod 4). Each (target, field) contest goes to the largest splitmix64 priority, and the stored byte may get one hash-keyed bit flip. Energy is debited, transferred, decayed and randomly replenished. Each variant law changes one phase. There is no genome, individual, input, output, objective or selection.
SIZE: The six physics files above total 1,794 lines (Aether/ holds 35,658 lines of Python, mostly the RunPod platform). 768 test functions in 40 files, 133 of them in the 10 physics test files.
DEMONSTRATED CORRECTNESS:
- A differential corpus comparing the oracle with the GPU-shaped NumPy implementation: hand-worked accounting cases, seeded fixtures, H,W in {1,2}, >= 500 Hypothesis worlds, 5-step trajectories.
- Golden vectors.
- Mutant implementations rejected (for the earlier aeth00 specimen).
- The v1 variant is asserted bit-identical to gpu_aeth01.
- Cross-host: E-007 ran 6 tasks, 19 attempts, on 4 hosts (Windows with numpy 2.4.3; three Linux hosts with numpy 1.26.3); all MATCH (ops/campaigns/C-002/E-007/REDUCTION.json).
- Known defect: the propagation assay's "exact causal chain" claim is only a lower bound (Aether/AETH-03/PROPAGATION_ASSAY_AUDIT.md, per dossier).
INTERFACE: Aeth01World(H, W, seed, 5 integer params, grid).step() returns a new world. to_bytes()/from_bytes() give exact snapshot and restore. Integer-only; deterministic; no model call.
THROUGHPUT / SCALE:
- GPU: CuPy on an A40, 36,177,599 sites/s at 16384^2 (Aether/AETH-01/GPU_MEMORY_OPTIMIZATION_01_2026-09-22.md line 423).
- CPU: no rate recorded. E-007 wall time was 33.1 to 381.1 s per 128^2 unit.
COUPLING: numpy, and CuPy on pods. No other seat imports the physics. The platform depends on a RunPod key held on BUCKKEEP (dossier).
FIT TO SLOT: lattice open arm (RSE 6.4).
- Meets as is:
  - ORG-08: integer; every byte state is valid; counter hash keyed by seed, tick, site, field and domain.
  - REPR-01.
  - Exact one-bit twins (DEV-05 shape, per dossier).
- Fails: ORG-01, ORG-02, ORG-09, DEV-01 to DEV-07, COMP-01, and open-arm admission.
- Special question: there is nothing above HOLD, and no HOLD either, because there is no input or readout.
  - The record (dossier): about 92% of the medium is frozen by ~2,500 ticks; one-bit differences stay within about 1 site; rcv's propagation comes from its own relay rule; the content probe failed its positive control.
  - No HOLD or ADAPT plant exists. The only designed structures are instrument controls: a 21-emitter relay chain (Aether/AETH-03/PHYSICS_DESIGN_02_2026-09-26.md s2.3) and a seeded "template state copier" design (Aether/AETH-01/EXPERIMENTS.md).
MODIFICATION COST: XL.
- Work items:
  - Decide what an organism is.
  - Decide where observations enter and actions leave.
  - Design a rule set in which more than 1 of 256 opcodes acts.
- Salvage: the verification harness costs S to M to salvage.
- Rebuild comparison: a lattice substrate designed for organisms and I/O is M to L.
VERIFIED BY ME:
- Checked in source: oracle_aeth01.py in full; variants docstring; differential-test header; mutant test list; E-007 counts; throughput lines; counts; dates; imports.
- From the dossier only: frozen-medium figures; the rcv reinterpretation; the twin assay.

COMPONENT: Ares graph organisms (up to 17 nodes) and batched GA
PATHS: ares/substrate.py, worlds.py, search.py, develop.py; ares/tests/test_ares.py
OWNER / DATES: Ares (M2). 13 commits on ares/ and roles/Ares, from 2026-09-19 (eed9c7121) to 2026-09-25 (3f68be2b9); parked since.
WHAT IT REALLY DOES: P organisms are held as stacked float32 arrays. Each has 17 node slots (6 inputs including a clock and a constant, up to 8 hidden, 3 outputs), 9 arithmetic ops, a bias, a keep leak, two input ports W1 and W2, and a plasticity rate R on W1. Each world step runs 2 ticks of v = keep*v + (1-keep)*op(W1 v, W2 v, b), clipped to +-8, then applies W1 += R*v_i*v_j (clipped to +-4). The action is the argmax of the 3 outputs. The worlds are closed-loop: the next observation depends on the action. Runtime.reset() restores activations and W1 at every episode (40 to 80 steps), so the plastic weights are fast state. Search is a mutation-only GA.
SIZE: 4 modules, 1,654 lines. 19 test functions.
DEMONSTRATED CORRECTNESS:
- A determinism test.
- A positive-control GA run.
- A hand-wired organism, cheat_W4: one tanh self-loop latch. It scores fitness > 25 and drops below 10 when memory is ablated.
- There is no oracle.
Known defects:
- Held-out champion selection (D1) is still in ares/search.py lines 292-294 (I checked this).
- D2 to D4 and a float32 argmax-tie residue are reported in the dossier.
INTERFACE: Runtime(pop).step(obs[P,6]) returns actions[P]. float32 numpy; deterministic per seed on one host. No snapshot API (the state is plain arrays), no cost meter, no model call.
THROUGHPUT / SCALE: "~13 ms per 128-organism episode" (ares/ARES_CYCLE1_REPORT.md line 165).
COUPLING: numpy only; no other seat's code.
FIT TO SLOT: PN (RSE 6.3).
- Meets as is: activations serve as fast state; Config has switches for plasticity, keep, recurrence and per-step reset (the ORG-03 switch idea); ORG-06.
- Fails:
  - ORG-08: float32.
  - REPR-01: no record.
  - DEV-01: nothing persists across episodes.
  - ORG-01 and ORG-09.
- Missing for PN: fixed-point arithmetic; weights that persist across episodes; structural growth or pruning during life; a modulatory gate; ES and gradient arms.
- A designed 1-bit HOLD organism exists (cheat_W4). No designed ADAPT organism exists.
MODIFICATION COST: L.
- Work items:
  - Fixed-point rewrite of Runtime and the ops.
  - W1 that persists across episodes, with harness resets.
  - A modulatory gate and structural growth.
  - An independent oracle.
  - A fix for D1.
- Rebuild comparison: a PN core built from RSE 6.3 is M; with ES and gradient arms it is L. Rebuilding costs no more than adapting.
VERIFIED BY ME:
- Checked in source: substrate.py in full; rollout, reset and D1 in search.py; cheat_W4; the throughput line; dates; imports.
- From the dossier only: D2 to D4; the tie artefact; carrier results.

COMPONENT: Ensorain learners (TT class, bounded online regressors, CSSR/HMM causal-state learners, exact-Bayes binary processes)
PATHS: ensorain/e0/tt.py, e0/memories.py, wtp/organism.py; ensorain/arc3/suff/worlds.py, learners.py, cssr.py, hmm_learner.py, cssr_em.py, tests/test_worlds.py, replication/README.md
OWNER / DATES: Ensorain (M2). ensorain/ runs from 2026-09-23 (20a4bab5c) to 2026-09-30 (26a490702). tt.py dates from 2026-09-23; arc3/suff from 2026-09-28 to 2026-09-29.
WHAT IT REALLY DOES:
- TT class: a float64 tensor-train regressor (matrix-chain evaluation, one NLMS step per noisy scalar, TT-SVD). It is used as a capped memory behind a fixed, hand-coded foraging policy.
- Other bounded regressors fill the same role: table, sketch, additive, low-rank, CP, DCT and marks. The WTP base Memory is a one-float running mean.
- arc3/suff generates binary streams with exact Bayes predictors: iid; Beta-Bernoulli with unknown p; order-k Markov; known HMMs via forward filter, including the Even process; key-value queries.
- Learners scored against those predictors: STAT(k) KT counts, verbatim windows, PPM-style NEAREST, tables, Baum-Welch HMM, CSSR, and CSSR followed by EM.
- All of these predict; none acts.
SIZE: ensorain/ has 19,351 lines of Python. tt.py 148, memories.py 337, organism.py 475, suff core 737. 121 test functions (7 in suff, 11 in e0).
DEMONSTRATED CORRECTNESS:
- suff known answers:
  - Even-process and golden-mean Bayes log-loss land within 0.01 of 2/3 bit.
  - The Even process has no finite sufficient window.
  - STAT(2) equals the W2(2) Bayes predictor within 1e-9.
- Independent reimplementation: a pure-stdlib version written via Fabric task tsk-ba120344aa29 (Ensorain ran it on M2) confirmed four findings.
- An exact floor, H(X | last k) - 2/3, computed by enumeration, matched the worker's closed form to 4 decimals.
- e0: TT evaluation equals the dense tensor within 1e-10.
- e0: MemoryAudit refuses smuggled attributes, both before and during a life.
Known defects:
- Linux and M2 results differ by up to ~4e-15 relative (roles/Ensorain/probes/FP-001_RESULT.json).
- DEF-ENS-002 (dossier).
INTERFACE: TT.eval(addr), TT.update(addr, y, lr, mode). learner.run(x) works on a whole sequence and returns (P[T,2], {bits, query_ops}). Floats; deterministic on one host; no model call.
THROUGHPUT / SCALE: Not recorded as a rate. The replication script ran in 0.7 s on M2.
COUPLING: numpy only; no other seat's code.
FIT TO SLOT: tensor-network arm, and designed positives.
- TT class: fails ORG-01, ORG-08 and DEV-01.
- suff Bayes predictors:
  - Designed positives for HOLD/TRACK: the Even process needs a 1-bit causal state that no window can hold.
  - Designed positives for ADAPT: the Beta-Bernoulli posterior, built from a sufficient statistic.
  - STAT(k) is the k-window restricted class, and the enumerated floor is its exact bound (WLD-02 shape; a SCI-05 known-law candidate).
  - They fail MEAS-07 (floats) and ORG-01 (no actions; they run over whole sequences).
- MemoryAudit is a working precedent for ORG-02's hidden-store check.
MODIFICATION COST: Converting suff to exact rationals and wrapping it in world and organism protocols is M; rebuilding it is also M. For the tensor arm, rebuilding the TT class is S (it must become fixed point anyway).
VERIFIED BY ME:
- Checked in source: tt.py, worlds.py and learners.py in full; cssr, hmm and cssr_em headers; suff tests; replication README; MemoryAudit; FP-001; counts; dates.
- From the dossier only: WTP histories; CSSR results.

COMPONENT: Tyche register-DAG lens programs and their evolution
PATHS: tyche/lens.py, ecology.py, organisms.py, worlds.py, audits.py, v1/, v2/
OWNER / DATES: Tyche (M2). tyche/ runs from 2026-09-30 (075e5fc21) to 2026-10-01 (59f68caf4).
WHAT IT REALLY DOES: A lens is up to 48 instructions over 27 causal ops (delay, window sums, rank, accmod, ewma, a 2-4 state fsm, xor, where, and so on). Every register is a whole float time series (T = 12,100), and instruction i reads only earlier registers. A lens is therefore a feed-forward DAG computed over the entire series at once. Its output columns are added to the inputs of fixed weak classifiers (ridge, depth-4 tree, median-split lookup) that predict a hidden integer label; a lens's value is the paired accuracy gain it produces. Lenses evolve by mutation, graft, fuse and compose under eps-lexicase. The world never responds to anything.
SIZE: 5,439 lines. 35 test functions.
DEMONSTRATED CORRECTNESS:
- A causality audit: outputs must stay bit-identical when the future is replaced at 5 cut points.
- A LEAD cheat that must score z >= 4 and fail causality.
- There is no oracle.
- The dossier reports that the twin and PRF negative controls stayed flat.
- The dossier reports the v0 residual instruments invalid, and H1 unattainable by design (Harmonia e72508448).
INTERFACE: lens.execute(g, X[T,d]) returns Z[T,K] floats. Not streaming. Uses scipy and sklearn. No model call.
THROUGHPUT / SCALE: v0 evolution took 418 s wall at 16 workers and produced 2,368 lenses (roles/Tyche/REVIEW_PACKET_v0_2026-09-30.txt line 116).
COUPLING: Imports hecate.alien.systems and hecate/alien/data/answer_key.json. theseus/synth imports tyche.lens.
FIT TO SLOT: none of this scope's slots. It is evolutionary feature construction: no organism step, no actions, no lifetime. It fails ORG-01, ORG-08 and DEV-01. Its graft/fuse/compose operators and eps-lexicase are search-regime parts (SRCH-08), outside scope 2.
MODIFICATION COST: As an organism substrate, L (streaming integer ops, I/O, a learner inside). Rebuilding the DSL would be M. Not competitive for these slots.
VERIFIED BY ME:
- Checked in source: lens.py header and function list; imports; importers; counts; the throughput line; dates.
- From the dossier only: campaign results; audit behaviour.

COMPONENT: Theseus synth (rule programs on a 1-D field, exact genealogy, QD archive)
PATHS: theseus/synth/substrate.py, collide.py, entities.py, ecology.py, rulers.py, run_v0.py
OWNER / DATES: Theseus (DESKTOP-RUAPVAI). theseus/synth runs from 2026-09-30 09:09 (66f7f0db1) to 10:01 (308330aaf). The May 2026 theseus/ claim engine is a different system.
WHAT IT REALLY DOES: A genome is up to 14 sequential update rules drawn from 19 hand-written ops (diffuse, advect, react, remember, delay, gate, lensmap, and others). They act on a float64 field X[C<=4, N=32] plus a memory field, for T = 128 steps, on one of 5 topologies. A "collision" splices parents' contiguous rule runs and inserts one react rule whose gains are a fixed random function of each parent's fingerprint. A registry keeps parent ids, generation and minimum depth to the G0 seeds. The QD archive keeps the most reproducible member per cell (quality = -rep_dist). There is no organism, input, action or objective.
SIZE: 3,299 lines. 10 test functions.
DEMONSTRATED CORRECTNESS: The viability check includes a bitwise rerun. There is no oracle, and bitwise reproducibility across runs has not been verified (THESEUS-25). The dossier reports:
- The HK gate (20/20) is self-referential.
- Lineage integrity showed 0 mismatches.
- The crawler verified the v0 contamination.
INTERFACE: run(genome, seed, options), float64 numpy. Deterministic given PYTHONHASHSEED=0. No model call.
THROUGHPUT / SCALE: Total worker CPU was 9048.90625 s (v0) and 6676.84375 s (v0_1) per run of about 1,200 children (theseus/runs/*/REPORT.json).
COUPLING: tyche.lens; agents/nous/src/concepts.py, read via git show.
FIT TO SLOT: A lattice open arm in name only. It fails ORG-01, ORG-08 and DEV-01, and has no I/O and no plants. The genealogy registry is a tracer for SRCH-11, outside scope 2.
MODIFICATION COST: XL to turn it into an organism substrate. Rebuilding a 1-D lattice organism from scratch would be M.
VERIFIED BY ME:
- Checked in source: substrate docstring and constants; registry and archive code; counts; REPORT.json CPU figures; dates.
- From the dossier only: arm results; contamination counts.

COMPONENT: Aphrodite library-inheritance program synthesis (the G4/W5 engine)
PATHS: roles/Aphrodite/engine/improver.py, basis_v4.py, tier3d.py, fair.py, engine.py, a17.py, run_s3s4.py; roles/Aphrodite/science/compounding/rb6/IMPROVER_PARAMETER_INVENTORY.md; roles/Aphrodite/science/arc3/w4_improver_transplant/REPORT.md
OWNER / DATES: Aphrodite (M4, harry1). engine/ runs from 2026-09-21 (85b85b765) to 2026-09-28 (1ef7de4c0).
WHAT IT REALLY DOES:
- Programs: integer folds (init, body, final), run by eval of expression strings (Python ints; //, %, gcd, pow with exponent <= 32; ceiling 10^40).
- Search: walks a library (ordered sets of init/body/final strings, in sha256-keyed order), then the complete G4 grammar. It charges one escrow unit per candidate and stops at the first program consistent with all examples.
- Donor: groups the programs it found into behaviour classes, and derives one-hole schemas by first-order LGG over pairs of distinct classes.
- Selection: builds candidate libraries (INHERITED, MEMORISE, SCHEMA_k, SCHEMA_ALL) and picks by paired mean saving with a one-sided 95% bound.
- Transplant: frozen library bytes go into fresh recipients and are costed against PRISTINE and sham libraries.
SIZE: The engine's .py files total 14,855 lines. 50 test functions in engine/tests (114 under roles/Aphrodite).
DEMONSTRATED CORRECTNESS:
- A conformance gate between the search evaluator and the emitted-artifact evaluator (dossier; not rerun).
- A 288k-pair fasteval equivalence gate (dossier; not rerun).
- Sham libraries built from failed bodies.
Known defects:
- run_s3s4.py sets c["4_hostile_evaluation"] = True and c["8_no_donor_state"] = True as constants (I checked this).
- The positive-control schema equals the derived one (dossier).
INTERFACE: improver.search(library, examples, escrow, cap, rng) returns (prog, coord, charges) or None. Integer and deterministic; the statistics are floats. Standard library only. No model call.
THROUGHPUT / SCALE:
- Engine v1: 3,237 lineages per hour per core (roles/Aphrodite/engine/QUALIFICATION_2026-09-21.json).
- One A23 donor: 18323724 charges in 135.9 s (roles/Aphrodite/engine/A23_C3R2C/A18_DONORS_2026-09-28.jsonl line 8).
COUPLING: Nothing outside roles/Aphrodite. azure.env sits under engine/accel/azure and was not opened.
FIT TO SLOT: COMPOSE/RECURSE controls. Special question:
- NEGATIVE for RECURSE: yes, close to as built.
  - It is the T6 reference class: "designed learner with a fixed procedure and fixed hypothesis space".
  - improver.py says the library is data, every improver falls back to the complete G4 enumeration, and the mutation, fitness and selection rules are immutable.
  - Its gains stay inside that space: PRISTINE finds every L1-only solution at 8x to 3,527x more charges, median ~300x.
  - Its MEMORISE candidate has the shape of the XFER-07 impostor.
- COMPOSE: comparing a library against PRISTINE at equal escrow has the T5 shape.
  - Evidence: the S4 transplant passed; search leverage was 47x at Tier 3B and 345x at Tier 3C (roles/Aphrodite/STATUS.md line 15).
  - Caveat: the advantage is relative to the budget.
  - Caveat: two S4 gates are constants.
  - Caveat: schemas are expanded into concrete bodies before search rather than invoked with arguments.
  - Caveat: the world is single-fold induction, not CHAIN.
- POSITIVE for RECURSE: no.
  - What must become learner-owned and mutable (ORG-04, XFER-07): the rule that maps the learner's own traces to its next search behaviour (W4 report s0). The candidate parts are proposal order (P16), escrow split (P18), hits per cell (P2), composition policy (P23), member space (P7) and the rewrite theory applied before LGG (P11).
  - A route out of the fixed hypothesis space is also needed, such as promoting schemas to primitives (the DSL fork TH-020 is parked).
  - Against it on record: donors starting from PRISTINE derived 0 schemas in 8/8 runs, and the RB-6 check found hole count, lookahead and median selection inert (n = 3 supplies).
MODIFICATION COST:
- Negative arm plus the COMPOSE pair: M.
  - An organism wrapper.
  - A FAMILIES or CHAIN catalogue.
  - Real gates in place of the constants.
  - Exact verdict arithmetic.
- Positive arm: XL; it needs a decision.
- Rebuild comparison: a designed library learner on the WM substrate is L.
VERIFIED BY ME:
- Checked in source: improver.py; lgg and derive_schemas; fair.py header; basis_v4 interpreter; PRIMITIVES and Escrow; run_s3s4 lines 385-425; the parameter inventory; the RB-6 result; W4 s0; the frontier K4 line; the STATUS line; counts; dates.
- From the dossier only: S4 acceptance; A23 motif equality; conformance counts.

COMPONENT: Tensor-network code usable as an organism (group)
PATHS: primordial/brain/genomes.py, plastic.py, tt_policy.py; primordial/nv/tensornet/tt_cutn.py; ensorain/e0/tt.py; prometheus_math/tensor_train.py, symbolic_tensor_decomp.py; alien_circuitry/ac01d/families/c2_cp.py, c2_tt.py; exploratory/zoo/tt/core.py
OWNER / DATES:
- primordial/brain: Nestor lanes A and C, 26 commits, all on 2026-09-14.
- nv/tensornet: 2026-09-14.
- Ensorain tt.py: 2026-09-23.
- tensor_train.py: 2026-08-21.
- symbolic_tensor_decomp.py: 2026-04-25.
- alien_circuitry families: 2026-09-12.
- zoo: 2026-04-23 to 2026-05-05.
WHAT IT REALLY DOES:
- primordial TTDigits/TTFeat (the only organisms here): an evolved float32 TT policy (alpha[r], G[cores,16,r,r], Wo[r,A]). Its core chain reads the hex digits of the current observation and returns an argmax action. Bond rank r (default 3) is the capacity dial and the genome is charged by its byte length. It keeps no state between steps.
- PlasticTTBrain: a TT regressor whose ranks grow on surprise and are pruned by TT-rounding under a memory charge. It ships with a fixed-rank twin and a cheat that reads the regime flag.
- Utilities, not organisms: Ensorain's online TT regressor; quimb TT ranks with a fiber-shuffle null; tensorly decompositions; torch/ALS offline fits of a distance chart; TT-SVD helpers.
SIZE: genomes.py 399, plastic.py 260, tt_policy.py 501 lines. 35 test functions (primordial/brain/tests, nv/tensornet/tests).
DEMONSTRATED CORRECTNESS:
- A float64 ref_logits oracle for each family.
- C5: the numba forward pass had 0/129,583 row mismatches.
- C6 and C6b: fused rollouts were exact, 840/840 and 1008/1008.
- Plastic tests: charge-free rounding preserves the function; ALS recovers a rank-2 target; the honest brain ignores the flag.
- C2 PASS: rank tracked 24/24 regimes and 21/21 switches; leak probe 9/9; error about 10x that of a fixed rank-8 model.
- The C7 line ended in FAIL/KILL (primordial/brain/REVIEW_PACKET_round1.txt s6).
INTERFACE: Family.forward(g, obs, gidx). The Brain protocol is act(obs, msg_in), adapt(signal), cost() (primordial/core/contract.py). float32/float64. No snapshot and no store partition. No model call.
THROUGHPUT / SCALE: From primordial/ledger/rows/C/C1-tt-policy-crossover.jsonl (d=16, r=4):
- GPU (torch_gpu_graph_e2e): 19796063.676154736 obs/s.
- CPU (numba_par): 5440326.548246101 obs/s.
COUPLING: numba, torch, cuquantum (WSL). The C6 and C7 harnesses read lane E elites from pm-data, which is not in the repo.
FIT TO SLOT: tensor-network open arm.
- Meets as is: the rank dial the arm asks for; a memory charge shaped like DEV-09 storage rent; a fixed twin (DEV-02 shape); a cheat control.
- Fails: ORG-08 (floats), ORG-01, DEV-01.
- TTDigits cannot HOLD because it keeps no state. PlasticTTBrain learns from supervised (X, y) pairs, not by acting.
- No designed HOLD or ADAPT tensor-network organism exists.
MODIFICATION COST: L to make TTDigits an integer tensor-network organism with recurrent bond state, declared stores and snapshot. Rebuilding from RSE 6.4 would be M.
VERIFIED BY ME:
- Checked in source: genomes.py and plastic.py in full; headers of the utilities and tt_cutn.py; contract.py signatures; review packet s6 and s10; C1 rows; tests; dates.
- From the dossier only: the CW01 e08/e09 use (sisyphus/seats/Nestor.md).

COMPONENT: Network-like organisms with lifetime plasticity (tree-wide search)
PATHS: ares/substrate.py; primordial/brain/plastic.py, affine_plastic.py; prometheus/ananke/engine.py; hecate/programs/HT-faa9277e02/worlds/W6/probe/world.py, worlds/W2/world.py; ensorain/wtp/organism.py
OWNER / DATES:
- Ares: 2026-09-19 to 09-25.
- Nestor lane C: 2026-09-14.
- Ananke: 2026-09-24 to 09-30.
- Hecate HT-faa9277e02 W6: 2026-09-29 (dc2fdf7b4, 88bb37ada).
- Ensorain: 2026-09-24.
WHAT IT REALLY DOES:
- How I searched: git grep -i over *.py, excluding holdout and nestor_secrets paths, in five passes:
  - hebb, neuromodul, stdp, spike timing, synaptic, oja, bcm, fast weight, eligibility trace, plasticity.
  - within lifetime, lifetime learn, baldwin, neat, hyperneat, cppn, learning rule, plastic.
  - in-place weight updates (dw =, dW =, W +=, weights +=).
  - modulatory, three-factor, dopamine.
  - classes named RNN, Recurrent, Elman, Hopfield, Spiking or LIF.
- Hits I set aside:
  - The 491 hits in agents/hephaestus are text-answer scorers that use these words (I opened one).
  - hephaestus/xpol_2026 and forge/ hold generated tools of the same kind.
  - The Nyx atlas cuts and one Techne fossil are readings of external code (Hopfield, genann, padasip).
- Result: no closed-loop recurrent network organism keeps its weights or topology across episodes under Hebbian, neuromodulated or structural plasticity.
- Nearest candidates:
  - Ares: Hebbian W1, reset every episode.
  - PlasticTTBrain: surprise-gated rank growth and pruning; a supervised regressor.
  - PlasticAffine: integer mod 2^16 constants, refit when support is low.
  - PTE: routing weights, immediates and rule pointer can all be written during life, but per the dossier w never carried the bit.
  - Hecate W6: Hebbian conductances on a 48x48 float reaction-diffusion medium; probe outcome NULL; no I/O.
  - Hecate W2: soft competitive Hebbian prototypes.
  - Ensorain's "hebbian" rule: a regressor step with the target in place of the error.
SIZE: Hecate W6 probe world.py is 119 lines plus controls.py at 258 lines. The others are in their own sheets.
DEMONSTRATED CORRECTNESS: Hecate W6 ran a positive control, null twins and a cheat arm; the outcome was NULL (hecate/programs/HT-faa9277e02/worlds/W6/probe/OUTCOME.json).
INTERFACE: There is no common interface. Hecate W6 is a float64 probe world run by main().
THROUGHPUT / SCALE: Not recorded for Hecate W6. The others are in their own sheets.
COUPLING: Hecate W6 loads ../controls.py and spec.json.
FIT TO SLOT: PN. Nothing satisfies RSE 6.3 as is. ORG-08, structure that persists across episodes (DEV-01) and modulatory gating are absent everywhere.
MODIFICATION COST: Rebuild the PN: M for the core, L with ES and gradient arms. No candidate is cheaper to adapt than to rebuild.
VERIFIED BY ME:
- Checked in source: all five grep passes; the cited lines; the Hecate W6 header and OUTCOME.json head; W2 train_hebb; one Hephaestus file.
- Not opened: Hecate W6 controls.py and DESIGN_NOTES.md.

COMPARISON
slot                      rank  component                        one-line reason
------------------------  ----  -------------------------------  ----------------------------------------------------------------------
PN plastic network        1     Ares graph organism              right shape (fast activations, Hebbian edges, switches); float32, reset per episode
                          2     primordial PlasticTTBrain        surprise-gated structural plasticity under a charge; supervised regressor
                          3     PTE routing w, Kp, rule pointer  writable during life but not a weight network; w carried nothing
                          -     (all)                            none fits as is; rebuilding a PN costs no more than adapting Ares
message-passing arm       1     Ananke PTE                       only candidate: integer, oracle, second-host conformance, HOLD plants
lattice arm               1     Aether aeth01                    integer, oracle, 4-host bit-identical; no organism, no I/O, frozen medium
                          2     Theseus synth                    op algebra on a 1-D float field; no organism, no I/O
function-chemistry arm    -     none in scope                    no scoped component has expressions acting on expressions
tensor-network arm        1     primordial TTDigits/PlasticTT    evolved TT policy with rank dial, oracle, fast kernels; no state, floats
                          2     Ensorain e0/tt.py                148-line online TT regressor behind a fixed policy
                          3     tensor_train, decomp, AC fits    analysis and fitting utilities, not organisms
COMPOSE/RECURSE controls  1     Aphrodite G4/W5 engine           as built: fixed-procedure negative, MEMORISE impostor, COMPOSE-shaped pair
                          2     Aphrodite E2 ES toy              tunes 4 of its own hyperparameters; theta barely moves (dossier)
HOLD/ADAPT positives      1     Ensorain suff Bayes learners     exact Bayes positives and a k-window class with an exact floor; prediction only
                          2     PTE plants                       hold_latch and echo_hold; p_flip lives in a world a clock solves
                          3     Ares cheat_W4                    1-bit tanh latch, float32
                          4     primordial PlasticAffine         integer refit on surprise; supervised
(no slot)                 -     Tyche lens ecology               feature programs for fixed classifiers; search-operator parts only

COULD NOT DETERMINE
- PTE golden-trace replay across hosts. No stored trace was compared; the RunPod run recomputed the oracle on that host. I searched roles/Ananke and prometheus/ananke for "cross host", "second host" and "on M2" and found only Aether's receipt.
- PTE CPU rate per site-update. The only figure is world-ticks/s, with N not stated. I searched roles/Ananke for "cpu" near throughput terms.
- Aether CPU rate. None found; I searched Aether/, roles/Aether and ops/campaigns/C-002 for sites/s, site-ticks/s and s/tick.
- Cross-host records for Ares, Tyche, Theseus, Aphrodite and the primordial brain. None found. roles/*/probes/FP-001 exists only for Aether, Ananke, Ensorain and seven seats outside this scope.
- Aphrodite search rate as a benchmark. There is only the one donor row; the accel timing documents call M4 timings indicative only.
- Whether Aphrodite's derivation can grow a library from PRISTINE outside the Tier-3D S3 catalogue. I did not open the S3/S4 result files.
- Files not opened:
  - Ananke: c1b.py, lens*.py, campaign.py and assays.py bodies.
  - Aether: the CuPy kernel and the aeth03_propagation body.
  - Ares: worlds.py and develop.py bodies.
  - Ensorain: e1/mem.py.
  - Tyche: ecology.py and run_v*.py.
  - Theseus: collide.py.
  - Aphrodite: identity.py, cert.py, tribunal_t4.py, conformance.py, and the a16 to a23 bodies.
  - primordial: the tt_policy.py body and the C3/C7 harnesses.
- Function-chemistry candidates were not searched beyond the scoped components, none of which is one.

SURPRISES
1. PTE's conformance suite ran unmodified on a second host: RunPod RTX 4000 Ada, Linux, torch 2.4.1+cu124, commit ee81c0474, 2026-09-27, "139 passed in 34.62s" (Aether/runpod/receipts/ananke-conformance-20260927T151608Z/result.json). The Ananke dossier (s15e, s19) says RunPod was never used. That is true for science runs but not for conformance; the Aether dossier records the run.
2. A tensor-network organism family exists that scope 2 did not name. It consists of:
   - primordial/brain/genomes.py (TTDigits, TTFeat).
   - plastic.py (PlasticTTBrain, with a fixed-rank twin and a flag-reading cheat).
   - affine_plastic.py (an integer refit learner).
   - primordial/nv/tensornet.
   All are from Nestor lanes on 2026-09-14, and are listed only in sisyphus/seats/Nestor.md.
3. On "the crawlers did not report one": the Ares dossier does report Hebbian-like W1 plasticity. The code resets it every episode, so no organism anywhere keeps plastic weights across episodes.
4. Aether reproduces bit for bit across Windows (numpy 2.4.3) and Linux (numpy 1.26.3) on 4 hosts. It is the best-evidenced integer physics in scope, yet it has no organism.
5. Ensorain arc3/suff is close to the RSE TRACK world family: exact Bayes predictors, an enumerated k-window floor, and an independent reimplementation. It is more useful than its dossier's "toy processes" label suggests, but it is float-based.
6. Aphrodite as built is the T6 reference learner, and its own W4 report shows donors starting from PRISTINE derive nothing (0 in 8/8). Library growth from scratch is not demonstrated in W5/T4. The compounding it does show (11/18 supplies) starts from a supplied G1 library.
7. PTE's only ADAPT plant (p_flip) lives in a world that a block clock solves at 1.000, and PTE environments are open loop. A PTE ADAPT certificate would need a new world and a closed loop.
8. Ensorain's e0 MemoryAudit refuses undeclared persistent attributes, including mid-life. It is a working precedent for ORG-02's hidden-store check.
