# Salvage worker report: scope 3, world machinery

Deposited by Dionysus[m1-3815a3b9] on 2026-10-01. The worker's transcript
file is empty on this host, so the text below was copied by Dionysus from the
worker's final message as it arrived in the session. It is meant to be
verbatim; any slip in copying is Dionysus's.

Brief: roles/Dionysus/prompts/2026-10-01_salvage_workers/00_COMMON.md and
03_SCOPE_worlds.md. Worker model: opus, read-only.
Worker usage as reported by the harness: 585,484 tokens, 169 tool uses,
about 25.4 minutes.

Search-rule note. This worker was the first to report that the brief's holdout
exclusion covers directories only (its SURPRISES item 1). See
00_SEARCH_RULE_INCIDENT.md.

This is a worker's fact sheet. Its claims are the worker's, graded by its own
VERIFIED BY ME lines. Where SALVAGE_MATRIX.md relies on one, it says so.

----------------------------------------------------------------------

The worker's covering note:

I've finished the scope-3 fact-finding: ten sheets plus a comparison table, gaps and surprises, below. Four things matter most before you decide:

- No component computes a best value for any restricted class (memoryless, k-state, non-adaptive, lookup). The demand certificates have to be written new for every family.
- The R6 answer-key leak is still in the code.
- The brief's holdout exclusion pattern misses files. One of my count-only searches touched a holdout-named file as a result; details in SURPRISES item 1.
- Each family has one fairly clear starting point:
  - RECALL: Archaeon's WSE grammar.
  - TRACK and IDENTIFY: Ensorain's exact-Bayes worlds.
  - RECOMBINE: Ensorain's marginal surrogate and pair-block holdout.
  - DOUBT: Ludus's exact solver as a pattern only.
  - Sealed custody: Cosmos's broker.
  - Admission: Hecate's draft evaluator contract.
  - RETAIN and FAMILIES: nothing in scope; write them new.

Most sheets run past the 250-word target, because each also answers the scope's eight per-component questions.

SALVAGE FACT-FINDING, SCOPE 3: WORLD MACHINERY
Worker for Dionysus[m1-3815a3b9]. Worktree dionysus-base-role at e3d7c7034, 2026-10-01. Read only. Nothing was executed except read-only git commands and python one-liners that read committed JSON. Sheets run past 250 words where needed to answer the scope's eight questions.

----------------------------------------------------------------------
COMPONENT: Ludus (exact stopping solver, depth profile, occupancy regret, arena plus differential leak audit, qualification controls, 1,338-row atlas)
PATHS: ludus/bench/core.py, ludus/bench/run.py, ludus/bench/occupancy.py, ludus/depth_profile.py, ludus/arena/core.py, ludus/arena/audit.py, ludus/arena/worlds_epistemic.py, ludus/controls/fixtures.py, ludus/controls/CONTROLS_2026-09-16.json, ludus/atlas_of_worlds/
OWNER / DATES: Ludus. 2026-09-01 (e85bfa6b9) to 2026-09-16 (fb858dd5c), 14 commits.
WHAT IT REALLY DOES:
- Bench worlds are fully observed single-agent stopping and selection DAGs. They are solved by exact float backward induction, and any fixed policy can be evaluated exactly.
- Policies are handed the world object and call world.draws(), so they hold the transition model. The optimum is memoryless (0 bits demanded).
- gap(k) is the share of states where a depth-k search, using the world's own score, misses the optimal action set.
- Arena: an OpenSpiel-like interface. In the Ball-under-couch world every observation carries the whole sensor_history (0 bits demanded), and UNKNOWN is paid by the size of the possibility set, not by probability.
- Differential audit: in one post-chance state, change one hand-named secret attribute and compare 10 channels the player can reach.
- Atlas: a catalogue in M1 Postgres (ludus_atlas). Nothing in it is executable.
SIZE: 47 .py files, 12,335 lines (3,728 of them atlas). 0 pytest functions. 25 scripted assertions in ludus/arena/test_epistemic.py. 25 control rows.
DEMONSTRATED CORRECTNESS:
- CONTROLS JSON:
  - LEDGER negative control: 0.0 at k=1..4.
  - ORCHARD positive control: gap(4) 0.3448.
  - NIM345 cheat control: the gate ADMITTED it, at gap(4) 0.2398 exhaustive and 0.2 at n=250, while the Bouton rule scores 1.0.
  - Bench verify passes a one-ray Martian Dice.
  - Differential audit fires on 4/4 injected Kuhn leaks; the key-name check fires on 1/4.
- Theory check: Kuhn -1/18 within 0.02 over 12,000 sampled episodes.
- Defect: r0003 stops on ties (ludus/bench/core.py:226).
INTERFACE: Python, floats. The bench is exact with no RNG. The arena uses random.Random(seed) per episode. Clone by deepcopy. The replay digest excludes timing. The only LLM call is in ludus/ceiling1.py.
THROUGHPUT / SCALE: ludus/atlas/transfer_matrix.json records compile+solve times:
- CANT_STOP: 69,038 states, 60.9 s.
- INCAN_GOLD: 442,368 states, 19.0 s.
- COLORETTO: 296,925 states, 19.6 s.
COUPLING: stdlib (plus requests and sqlite3 for the atlas). git grep finds no importer outside ludus/.
FIT TO SLOT: DOUBT seed (bank-or-bust is an irreversible commitment; UNKNOWN is an opt-out) and WLD-13 (Kuhn, RPS, Nim).
- An exact optimum exists. Restricted classes appear only as fixed circuits and an 8-40 point threshold grid, never as the best value of the class.
- Floor circuits shipped with the bench. The controls arrived 2026-09-16, after the cycles that relied on them.
- No held-out or sealed sets.
- Satisfies WLD-17.
- Fails WLD-01, 02, 03, 05 (one state pair, no trained probe, no twins), 06, 07 (admits Nim) and 11.
- Missing: hidden state, belief-state DP, rational values, twins.
MODIFICATION COST: M. Extend the evaluator to a finite-horizon belief-state DP in rationals, and port the audit plus the Ledger/Orchard/Nim fixtures as admission attackers. Rebuild: M; reuse saves under a day.
VERIFIED BY ME: every code and JSON fact above. From the dossier only: cycle histories and 17/21 worlds lacking invariants.

----------------------------------------------------------------------
COMPONENT: Bellerophon Worlds Kernel (prometheus.toolbox)
PATHS: prometheus/toolbox/ir.py, prometheus/toolbox/receipt.py, prometheus/toolbox/admission.py, prometheus/toolbox/backends/local.py, prometheus/toolbox/ref/worlds.py, prometheus/toolbox/ref/worlds_integer_alt.py, roles/Bellerophon/science/
OWNER / DATES: Bellerophon. 2026-09-18 (4c0435544) to 2026-09-19 (97109bd95), 102 commits. No commits since.
WHAT IT REALLY DOES:
- Experiment IR, lowered by compile(target): local is complete, SFE partial, NPE UNAVAILABLE.
- Loop: reset(seed), observe, act, step, events, observers. Players get only an integer list and an ActionSpace.
- Receipts: a sha256 content id plus a prev_receipt_id chain, with a strict reader and a forensic scan. There is no external anchor.
- Admission, per component:
  - conformance;
  - BIT replay on 3 seeds;
  - reference agreement with a probe-power check;
  - the cheat parameter must change the trace;
  - extension demonstrability.
- Kernel wrappers: seeded channel permutation, observation delay, scheduled parameter change.
- world.integer.v1: 6 registers mod 2^16 with xorshift64 streams keyed by sha256(tags). It observes 4 registers plus a charge bucket; the yield window and linear ops are hidden. No optimum or bound is computed anywhere.
SIZE: 62 .py files, 11,070 lines (5,846 non-test). 231 test functions in prometheus/toolbox/tests.
DEMONSTRATED CORRECTNESS:
- MUTATION_LEDGER_2026-09-19.json: 92 mutants, all CAUGHT.
- CROSS_PLATFORM_FULL: 38 receipt files (1,296 runs) reproduce on Linux/CPython 3.12.
- Defect: world.integer_alt.v1, the "second implementation", imports the reference's stream, XS64 and DEFAULTS, so the agreement check shares the random draws.
INTERFACE: Deterministic. Integer, except the pendulum world and the C6 wrap (SEMANTIC, quantum 1e-6). Snapshot/restore. Scoring runs in-process. No model calls.
THROUGHPUT / SCALE: BATCH_THROUGHPUT_2026-09-19.json: world.integer.v1 at 6.05 us per env-tick (SPECTREX5, py 3.14.4). The batched path is slower: 8.55 to 33.23 us.
COUPLING: optional numpy and redis. Wraps SerendipityFoundry wforge and archaeon.campaign6 when importable. Imported only by prometheus/atlas_bee.
FIT TO SLOT: infrastructure only; it seeds no family.
- Holdout seeds are base+n_seeds+i: labelled in receipts and never read by search.py.
- Satisfies WLD-01 in part.
- Fails WLD-02, 03, 05, 06, 07, 11 (shared RNG), SRCH-05 and PROV-10.
- Reusable for the foundry: the permutation wrapper (scrambled-channel twin), the delay wrapper (delay dial), the schedule wrapper (rule-change dial) and the power-checked agreement test.
MODIFICATION COST:
- S to lift the wrappers and the agreement test into the foundry.
- L to harden it as the kernel: counter-based RNG, out-of-process scorer, ladder-hash gate, sealed seeds.
- Rebuilding the protocol, receipts and replay core: M.
VERIFIED BY ME: IR, loop, wrappers, seeds_for, receipt, admission, both integer worlds, test count, the JSON files, dates and importers. From the dossier only: the 1,421-pass suite and EXP results.

----------------------------------------------------------------------
COMPONENT: Archaeon world machinery (WSE event-stream grammar, Campaign 6 composed worlds, ENVGATE)
PATHS: archaeon/wse/worlds.py, archaeon/wse/controls.py, archaeon/wse/ssf.py, archaeon/wse/survey.py, archaeon/tests/test_wse.py, archaeon/campaign6/worlds/generator.py, archaeon/campaign6/worlds/runtime.py, archaeon/envgate/engine.py, archaeon/envgate/mechanism.py, archaeon/envgate2/
OWNER / DATES: Archaeon.
- WSE: 2026-09-16 (cd68cea96 design, 6d14ec5e6 code) to 2026-09-17 (cb9135104), 23 commits.
- campaign6: 2026-09-18 to 09-19.
- envgate: 2026-09-24. envgate2: to 2026-09-26.
WHAT IT REALLY DOES:
- WSE, per tick: the organism reads one list of uint32 words (PUT, ASK, ASKX, ASK2, ASKO, SETOP, DEF, NOISE, RETIRE). Its first output word on an ask tick is scored exactly.
- Hidden state: K tagged values of value_bits each, with identities drawn fresh per episode. Minimum memory is about K x value_bits bits, plus at least log2(K!) bits to bind tags when asks are shuffled (code-inferred).
- Independent dials: K, D, delays, Kd distractors, interference, retire/recycle, value_bits, ask kind, vocab range.
- Chance (1/2^value_bits) is stated; no bound is computed.
- Shipped in the grammar's own commit: positives POS_REGS and POS_TABLE, nulls CONST0 and ECHO_LAST.
- The lagged-echo payload nulls arrived 62 minutes later (1c0e39ccf), after survey v01 found W8 leaking (READOUT_v01 s4).
- train/heldout/controls are separate SplitMix64 families keyed by campaign seed: separated, but predictable and unsealed.
- C6: 0-10 float feature modules over 24 ticks. Reward is divided by an upper bound; no optimum.
- ENVGATE: frozen z80atlas physics and five lockstep arms with byte-identical inflow; the sham band was frozen by rule before any data. It is a reproduction assay and demands nothing cognitive.
SIZE:
- wse: 16 files, 3,333 lines, 8 tests.
- c6 worlds: 382 lines, 0 tests.
- envgate: 1,055 + 546 lines, 9 tests.
DEMONSTRATED CORRECTNESS:
- test_wse.py: an independent reference evaluator, sharing only the kind codes, matches the world on 20 episodes per survey cell.
- READOUT_v01: POS 1.000 on W0-W3; nulls 0.000.
- Defect: the SSF stream cells have no test (searched archaeon/tests).
- Defect: the ASKO permutation rule that leaked W8 is unchanged in worlds.py; no later diff touches it.
INTERFACE: Integer and deterministic, with keyed streams. The harness scores. The organism is the Proteus VM.
THROUGHPUT / SCALE: archaeon/wse/READOUT_v01.md: 126 rows (N=200, G=100, E=24), 1532 s on 24 procs (M2).
COUPLING: proteus.foundry (prng, vm) and archaeon.workspace. Nestor CW01 and Odysseus code import archaeon.wse. C6 needs proteus.graph; ENVGATE needs archaeon.z80atlas.
FIT TO SLOT: RECALL (the best seed in scope) and partial CHAIN (ASK2, DAG).
- Satisfies WLD-01 mostly, WLD-04, and in part MEAS-04 and WLD-11 (same seat).
- Fails WLD-02, 03, 05, 06 and 07.
- C6 contributes only a MINED generator idea. ENVGATE contributes the pattern of twin arms on shared streams.
MODIFICATION COST: M. Port worlds.py and SplitMix64 to the protocol; add information bounds with enumeration receipts, absence and scrambled twins and commit-reveal families; fix ASKO; add a reference for the SSF cells. Certified CHAIN bounds: L. Rebuilding RECALL: M. Retire the C6 and ENVGATE code.
VERIFIED BY ME: all of the above in source, plus commit order. From the dossier only: campaign results.

----------------------------------------------------------------------
COMPONENT: Herakles CA libraries (evca with the recovered historical rule tables, eca, ca_stream)
PATHS: herakles/evca/core.py, herakles/evca/genomes.py, herakles/evca/c1e/REPORT.md, herakles/eca/core.py, herakles/ca_stream/core.py, herakles/ca_stream/OBSTRUCTION.md, herakles/specimens/spec-juille-pollack-1998/, herakles/specimens/spec-andre-bennett-koza-1996/
OWNER / DATES: Herakles.
- evca: 2026-09-08 (0641c567b) to 09-16 (6c9c55bfb).
- eca: 2026-09-09 to 09-11.
- ca_stream: 2026-09-09 (175b5da08) to 09-11 (91ca75f9f).
WHAT IT REALLY DOES:
- evca scores one radius-3, 128-bit rule on an odd periodic numpy ring against density criteria. It runs no search; genomes.py holds 6 tables.
- eca enumerates the 256 elementary rules on 7-11 rings.
- ca_stream injects one bit per step at a port, steps the CA once, and fits a closed-form ridge readout (32 params) on the post-step lattice only.
  - Targets: delayed recall d=0..3 and temporal XOR d=0,1, over the complete catalogue of all 256 length-8 streams.
  - Partition: 64/64/128. The fit function cannot receive confirmation data.
  - Controls share the substrate interface:
    - shift register: solves recall, must fail XOR;
    - shift-xor;
    - direct input: the memoryless reference, fails every delayed target;
    - frozen random: base rate.
  - Demand: d bits for recall, d+1 bits for XOR (code-inferred).
SIZE:
- evca: 1,558 lines, 64 tests.
- eca: 410 lines, 33 tests.
- ca_stream: 760 lines, 29 tests.
DEMONSTRATED CORRECTNESS:
- Known answers: C1-e 17 of 18 cells; JP98 15 of 15; ABK96 4 of 4 (report headers).
- ca_stream alpha: 0 of 63,488 features are nonzero; the held rules annihilate the injected bit. v2 was never run.
INTERFACE: Pure numpy with explicit integer seeds and no I/O. Integer lattice, float readout. Deterministic.
THROUGHPUT / SCALE: herakles/ca_stream/alpha_results.json: elapsed_s 0.72.
COUPLING: numpy only. Imported by vivarium/viv/ca_density.py, archaeon campaigns, proteus/eval/rule_table_identity.py, nyx and Artemis FR-101.
FIT TO SLOT: ca_stream is a tiny RECALL/TRACK seed with exact whole-catalogue scoring. evca and eca belong to the lattice open arm (RSE 6.4), not the foundry.
- Satisfies WLD-17, and in part WLD-03 (memoryless and positive references ship) and WLD-05 (a no-input leakage probe).
- Fails WLD-01, 02, 04 (horizon fixed at 8), 06 and 11.
MODIFICATION COST: S (lift the catalogue, targets, partition and controls). Rebuild: S.
VERIFIED BY ME: all of the above in source and reports. From the dossier only: ABK run time.

----------------------------------------------------------------------
COMPONENT: Hecate (control-first probe worlds, evaluator contract, null twins, alien-lawful assay)
PATHS: hecate/programs/_prompts/pass3_v2.md, hecate/programs/_lib/evaluator_contract.py, hecate/alien/systems.py, hecate/alien/verify.py, hecate/alien/baselines.py, hecate/alien/tasks.py, hecate/alien/dataset.py, hecate/alien/data/, hecate/tests/
OWNER / DATES: Hecate. 2026-09-29 (e0bd2e312) to 2026-10-01 (2dc4fbb01). The assay was frozen at 1fed85d95 (2026-09-30 01:40) with its key and baselines, "before any model sees a pilot system".
WHAT IT REALLY DOES:
- The control-first generator is an LLM prompt. The model writes spec.json and controls.py (POSITIVE_CONTROL, CHEAT, NULL_TWIN, >= 5 seeds), runs them, then writes ATTAINABILITY.json. A spec is frozen when every success clause is attainable and discriminating and the cheat is detected. I counted 19 receipts, 17 of them frozen.
- evaluator_contract.py is marked "DRAFT -- not issued, not frozen". It requires the arms TREATMENT, NULL_TWIN, POSITIVE_CONTROL, CHEAT and SIMPLE_ALT, compares exactly with Fraction, and maps a pilot positive-control miss to SPEC_UNATTAINABLE.
- Alien assay: 100 deterministic integer maps on <= 4,096 states, plus scramble/smooth/linmix nulls.
  - Properties are checked by exhaustive enumeration.
  - LLM subjects read transition text, or run up to 10 experiments (run, clamp).
  - Predictions are scored against the simulator over the full state space.
  - Baselines shipped in the freeze commit: identity, nearest neighbour, exhaustive best affine mod m, local table, linear invariants, zlib.
SIZE: 28,180 py lines (9,245 outside the generated HT-* programs; 3,956 in the alien assay). 89 test functions (33 for the contract, 9 for alien generation).
DEMONSTRATED CORRECTNESS:
- Tests check that every alien property verifies, every null destroys it, and answers match the simulator.
- Defect: answer_key.json (305,165 lines) is tracked in git and can be regenerated from seed 20260930 (dataset.py:35).
- Defect: the public leak test is a 13-word substring list.
- Dossier, not checked: null-twin drift in about 11 worlds; 32/42 evaluators accept copied seeds.
INTERFACE: integer systems, deterministic from a public seed. The LLM both writes worlds and is the subject.
THROUGHPUT / SCALE: 32.5 core-minutes for all probes (dossier).
COUPLING: corpus built from gitignored Nous runs plus the Hephaestus ledger. tyche/worlds.py imports hecate.alien.
FIT TO SLOT: the contract can serve as the WLD-07 admission verdict engine. NULL_TWIN is a WLD-05 arm. The alien systems seed TRACK, IDENTIFY (the active task) and MINED.
- Satisfies WLD-03 on timing.
- Fails WLD-01, 02 (no class values), 05, 06 (key in the repo) and 11 (one model family).
MODIFICATION COST: S to issue the contract as the admission gate. M to build hidden-component TRACK/IDENTIFY worlds with exact best-k-state values by enumeration and sealed keys. Rebuild: S for the contract, M for the worlds.
VERIFIED BY ME: all of the above except the counts marked as from the dossier.

----------------------------------------------------------------------
COMPONENT: Ensorain (exact-Bayes sufficiency worlds ARC3 PKG-S1, WTP-03 null ladder, marginal surrogate, named streams)
PATHS: ensorain/arc3/suff/worlds.py, ensorain/arc3/suff/learners.py, ensorain/arc3/suff/ladder.py, ensorain/arc3/suff/tests/test_worlds.py, ensorain/arc3/suff/results/ladder.json, ensorain/wtp3/collider.py, ensorain/wtp2/world2.py
OWNER / DATES: Ensorain. 2026-09-23 (20a4bab5c) to 2026-09-30 (26a490702). The suff engine is bef057f44 (2026-09-28). The WTP-03 engine bcba874b9 (2026-09-24) was committed before any row.
WHAT IT REALLY DOES:
- suff: streams with exact Bayes predictive distributions:
  - iid with known p;
  - Bernoulli with unknown p ~ Beta;
  - order-k Markov with an unknown table;
  - known HMMs, by forward filtering: the Even process (2 causal states, no finite window is sufficient), golden mean and SNS;
  - a key-value Zipf stream.
  - suff_bits(t) is the answer key. Learners with declared bit budgets are scored by excess log-loss. The organism only predicts; there are no actions.
- WTP3: nulls N0 zero, N1 constant/recent, N2 marginal, N3 linear and N4 bounded lookup, all batch fits. The tuned batch rung N6 was added post-data.
  - An exact marginal-preserving surrogate keeps the mean, the per-mode marginals and the variance, and destroys interactions.
  - The recomb test set is a pair-block holdout.
- WTP2: a numpy SeedSequence spawned into 8 named streams.
SIZE: suff 1,570 lines, 7 tests. wtp3 2,421 lines, 5 tests. 120 test functions across ensorain/.
DEMONSTRATED CORRECTNESS:
- The Bayes oracles hit the known entropy rate of 2/3 bit (tolerance 0.01).
- STAT(2) equals Bayes on W2(2) to 1e-9.
- ladder.json: the Even process's best window learner STAT_k6 has excess 0.060202520979811616 bits/symbol at 1537.666548908237 bits, against suff_bits 1.0.
- Dossier: N6 beat all 9 promoted specimens; DEF-ENS-002.
INTERFACE: numpy floats, seeded. No model calls.
THROUGHPUT / SCALE: ladder.json wall_s 93.4 (16 seeds, T 4,000).
COUPLING: numpy and scipy. Imported by Artemis D002/D004 scripts.
FIT TO SLOT: TRACK (the best seed), IDENTIFY (unknown-parameter streams), RECOMBINE twin and holdout machinery, WLD-03 rungs, and MEAS-03 bit keys.
- The exact optimum exists; restricted-class values are only estimated.
- Satisfies WLD-02 and MEAS-04 in part.
- Fails WLD-01 (no actions, floats), 05, 06 and 11.
MODIFICATION COST: M. Wrap it in the protocol; compute exact class values (order-k window, k-state) from the generating machines; use rationals; add twins and sealed seeds. Extracting the surrogate and holdout: S-M. Rebuild: M.
VERIFIED BY ME: all suff code, the tests, ladder.json, the null ladder, the surrogate, the stream names and commit order. From the dossier only: WTP histories.

----------------------------------------------------------------------
COMPONENT: Cosmos (sealed-holdout broker and receipts, C3 P1/P2 memory certificate, boundary-location attack, definition rung)
PATHS: prometheus/cosmos/broker.py, prometheus/cosmos/audit.py, prometheus/cosmos/c3/task.py, prometheus/cosmos/c3/certify.py, prometheus/cosmos/c3/calib.py, prometheus/cosmos/c3/gate.py, prometheus/cosmos/locate.py, prometheus/cosmos/research_check.py, roles/Cosmos/c3/runs/, roles/Cosmos/research/RESULTS.md
OWNER / DATES: Cosmos. 2026-09-23 (70ce535a2) to 2026-09-30 (5f5051e66).
WHAT IT REALLY DOES:
- Broker, read from its code only:
  - checks that the law is frozen;
  - compares the sealed spec's sha256 to a preregistered commitment and checks the family source hash;
  - runs the sealed family only in a subprocess;
  - receipts the prediction hash before the run.
- audit.py R1-R6 checks the chain, freeze hashes, order, predictions-before-reveal, seals and the committed-copy prefix.
- Sealing is tamper evidence, not access control. Nothing logs reads.
- C3 task: a cue among V symbols at t=0, k distractors, a query at k+1, and an optional hint that reveals the cue with probability h. The memoryless bound is 1/V, or h + (1-h)/V with the hint (code-inferred, not computed).
- C3 certificate:
  - P1: cross-validated decodability of the cue from state and observation, against observation alone, with a stratified permutation null.
  - P2: a full-state swap at t=k on paired CRN episodes.
- locate.py fits the flip location along a 33-point cost ladder at 1,600 episodes per point.
- The definition rung is only a regex requirement on the prose in RESULTS.md.
SIZE: 4,639 non-test lines, holdout directories excluded. 65 test functions, 10 of them in a holdout-named file that I did not open. The C3 package is 461 lines and no test imports it.
DEMONSTRATED CORRECTNESS:
- test_audit.py has 5 cheat controls.
- GATE_v3_PASS_seeds6to10.json: all 6 planted systems are classified correctly on all 5 seeds.
- v2 failed, and seeds 1-5 informed amendment A2.
- Laws A and B tie the definition rung (RESULTS R-0001/2).
INTERFACE: numpy floats, CRN seeds, a subprocess for sealed runs. No model calls.
THROUGHPUT / SCALE: 30 certify calls at 3.38 to 24.4 s each, 292.86 s in total (GATE_v3 JSON).
COUPLING: numpy and stdlib. It borrows the archaeon/wse/ssf.py contract without importing it.
FIT TO SLOT: the best existing sealed custody (PROV-10, WLD-06), a RECALL micro-world with a misleading-evidence dial, a MEAS-12 locator and the last rung of WLD-03.
- Satisfies PROV-10 in part: prediction order is provable, access is not.
- Fails WLD-02, 05 and 06 (no commit-reveal seeds; D, E and F were all spent in one day).
MODIFICATION COST: M for custody (out-of-repo or encrypted seeds, an access log, commit-reveal). S for the task, the locator and the rung. Rebuild: M custody, S for the rest.
VERIFIED BY ME: the files listed. Not opened: the holdout directories, D2, the withheld branches.

----------------------------------------------------------------------
COMPONENT: Tyche v2 worlds (hidden-precursor certificates, keyed PRF negatives, TSD twins)
PATHS: tyche/v2/worlds_v2.py, tyche/v2/certify.py, tyche/runs/v2_certs/CERTIFICATES.json, tyche/worlds.py, tyche/tests/test_v2.py, tyche/tests/test_v0.py
OWNER / DATES: Tyche. 2026-09-30 (075e5fc21) to 2026-10-01 (59f68caf4). The certificates went in with the prereg at 7899a9ef0 (09:11), before the Block R results at 4dbbc07d0 (10:50).
WHAT IT REALLY DOES:
- Worlds: six i.i.d. binary input channels over T 12,100, with fixed index splits. The label is Y = g(hidden precursors), where precursors are delays, window majority, accumulator mod m or window parity. The learner sees X and predicts Y each tick; there are no actions.
- Certificates, on seed 0: plug-in MI of Y with every subset of precursors, minus the 99th percentile of 20 permutations. This is empirical, not exact.
- An exact lowest informative order is computed only for truth-table laws. That gives a true exclusion: any predictor reading fewer than s precursors is at chance (code-inferred).
- TSD twin: the same law applied to an independent hidden copy of X.
- PRF negatives: a SHA-256 bit keyed by the literal strings "tyche-prf-1" and "tyche-prf-2".
- Admission includes 64 size-matched random lenses as a null.
SIZE: 35 py files, 5,439 lines (worlds_v2.py 349, certify.py 122). 35 test functions.
DEMONSTRATED CORRECTNESS:
- Tests check certified orders (D3 2, D4a 3, D4b 3, D4c 4, D5t 2) and exact oracles, and that the causality audit catches the LEAD cheat.
- The 25 certificate rows match their intended orders.
- The leak test uses agreement minus chance < 0.3, so an inverted copy of Y would pass (code-inferred).
INTERFACE: integer data, default_rng([seed, uid, 2]). The learners are float (sklearn, per the dossier).
THROUGHPUT / SCALE: not recorded per world. 418 s for v0 evolution (dossier).
COUPLING: imports hecate.alien. Imported by theseus/synth.
FIT TO SLOT: HOLD/TRACK seeds with an order dial; TSD absence twins and PRF negatives for WLD-05.
- Satisfies WLD-02 and 05 in part.
- Fails WLD-01, 03, 06 (index splits, public PRF key) and 11.
MODIFICATION COST: M. Compute MI and class values exactly from the law, add per-delay memory bounds, move it into the protocol, seal the PRF keys. Rebuild: S-M.
VERIFIED BY ME: certify.py, the order function, the PRF/TSD code, the tests, CERTIFICATES.json and commit order.

----------------------------------------------------------------------
COMPONENT: Ares W-family worlds and Vivarium kinds (what they demand, briefly)
PATHS: ares/worlds.py, ares/search.py, vivarium/viv/kinds.py
OWNER / DATES: Ares: ares/worlds.py 2026-09-19 (eed9c7121) to 2026-09-23 (ab137f52b). Vivarium: kinds.py 2026-09-06 to 2026-09-17.
WHAT IT REALLY DOES:
- Ares worlds are batched float32: four world channels plus a clock and a constant, three actions. Every world has present, absent (feature neutralised) and shuffled (feature decoupled) modes, with CRN per batch.
- Demands, read from code:
  - W4 and W16 hold 1 regime bit, shown for 3 of 40 steps.
  - W5 holds 1 token from step 2 to T-2.
  - W3 has one rule reversal.
  - W11: a probe costs 0.1 and gives evidence with mean +-0.4 and sd 1; commitment is irreversible and pays +-2 per remaining step. This is a DOUBT sketch.
  - W9 is matching pennies.
- No optimum is computed.
- The Vivarium kinds (noop, random_walk, ca_density, artifact_probe, cegis_boolean, eca_rule_eval, plus bitstring Hamming scoring) are fitness evaluators with no perception-action loop. They demand nothing of an organism's memory.
SIZE: ares/worlds.py 483 lines.
DEMONSTRATED CORRECTNESS: not examined. Defect: ares/search.py:291-294 picks the final champion by argmax over the 32 held-out evaluation seeds.
INTERFACE: numpy floats. The hidden schedule is in the info dict, outside the observation.
THROUGHPUT / SCALE: about 13 ms per 128-organism episode (engine index, not checked).
COUPLING: ares/substrate.py.
FIT TO SLOT: patterns only (three-mode twins; W11 shape for DOUBT). Fails WLD-01, 02, 03 and SRCH-05.
MODIFICATION COST: retire the code. Rewriting W11 as an exact DOUBT world: M.
VERIFIED BY ME: the world docstrings, the W4/W5/W11/W12 code, the selection lines and the kind list.

----------------------------------------------------------------------
COMPONENT: The reasoning ladder (v0.1 R0-R12, Canon v2.0, Harmonia probes and leakage audit)
PATHS: pivot/reasoning_ladder_v01_2026-05-24.md, aporia/doctrine/reasoning_ladder.md, harmonia/memory/architecture/reasoning_ladder_testable.md, harmonia/experiments/reasoning_phase0.py, harmonia/diagnostics/ladder_leakage_audit.py, agents/icarus/ladder.py, roles/Harmonia/REVIEW_20260812_program_and_instrument_audit.md
OWNER / DATES:
- v0.1: 2026-05-24 (5b1b983ae), superseded 2026-08-17.
- Testable ladder: 2026-05-27.
- Probes: 830a83a3f, 2026-06-09, the only commit.
- Audit: bb2037496, 2026-08-12.
- Canon: ratified 2026-08-17 (9f6dd1782).
WHAT IT REALLY DOES:
- v0.1: tiers R0-R12, each with a perturbation falsification test. "Tier assignment is the lowest test the system passes consistently." Plus F, M and H axes.
- Canon v2.0, the only definer, from R0 to R12:
  - R0 recall
  - R1 local rule
  - R2 constraint tracking
  - R3 multi-step composition
  - R4 representation shift
  - R5 invariant detection
  - R6 counterexample
  - R7 proof repair
  - R8 strategy selection
  - R9 lemma invention
  - R10 analogy
  - R11 calibrated uncertainty
  - R12 generative conjecture
- A rung is held only if the mechanism survives perturbation, beats lower-rung baselines, fails in the predicted way and emits its artifact.
- Grading: reasoning_phase0.py generates math probes for R0-R3 and R5-R8. There is no R4 generator anywhere.
  - Each probe comes in 4 versions (clean, iso, adversarial, transfer) x 40, giving 160 per tier.
  - Ground truth comes from sympy, and a deterministic grade() produces a trace vector.
  - There is no environment.
- The Icarus ladder freezes the v0.1 text, with gate defaults of 5 cycles, 100 trials and p 0.01.
SIZE: probes 596 lines; audit 125 lines.
DEMONSTRATED CORRECTNESS:
- The audit flags a field equal to the ground truth on every probe, and reports a constant floor.
- R6 LEAKS at 100.0% (field "truth"), with a floor of 57.5%. R5's floor is 75.0%.
- At this SHA, gen_R6 still writes truth and cex into the payload (line 131).
- The reference "falsifier" reads truth and cex; "careful" returns p.ground_truth on sqrt probes.
INTERFACE: sympy, seed 20260527.
THROUGHPUT / SCALE: not recorded.
COUPLING: sympy and numpy; Icarus.
FIT TO SLOT: not a world family (WLD-16). Reusable: the perturbation versions, payload_reader plus a constant floor (MEAS-04), and R6 as a kernel fixture.
MODIFICATION COST: retire. Extracting the fixture: S.
VERIFIED BY ME: all files listed, git dates.

----------------------------------------------------------------------
COMPARISON (slot: world foundry; best fit first)

SLOT        RANK COMPONENT                      ONE-LINE REASON
RECALL      1    Archaeon WSE grammar           independent dials, integer, keyed streams, controls; no bounds
            2    Cosmos C3 task                 73 lines, misleading-hint dial h, 6 planted systems
            3    Herakles ca_stream             exact full catalogue, memoryless reference; horizon 8
            4    Tyche v2 delay worlds          exact order for table laws; prediction only
            5    Ares W4/W5/W16                 1 bit, floats, no bounds
TRACK       1    Ensorain suff HMM worlds       exact Bayes, causal-state key checked; floats, no actions
            2    Tyche v2                       hidden precursors plus TSD twin; MI empirical
            3    Hecate alien systems           exhaustive <= 4,096 states; needs hidden part and class values
IDENTIFY    1    Ensorain suff W1/W2            exact posterior predictive; no acting
            2    Hecate alien active task       acting with a budget of 10; LLM subject; no exact value
RETAIN      -    write new                      nothing here holds a hidden mapping across fast-state resets
RECOMBINE   1    Ensorain WTP3 machinery        exact interaction twin plus pair-block test; float fields
CHAIN       1    Archaeon WSE W7/W8/W10         compositional asks and a reference; no step budget; W8 leak
FAMILIES    -    write new                      nothing in scope
DOUBT       1    Ludus bench solver             exact stopping DP and policy evaluation; fully observed
            2    Ares W11                       right shape (probe cost, irreversible commit); no optimum
            3    Ludus Ball-under-couch         opt-out action; zero memory demand; possibilistic
MINED       1    Hecate alien generator         sampled finite systems, exhaustive checks, matched nulls
            2    Tyche D7 tables                sampled resilient laws with exact order
            3    Archaeon C6 sampler            provenance records; floats; no bounds
SEALED SETS 1    Cosmos broker and audit        commitments, predict-before-reveal; no access control
            2    Herakles ca_stream partition   structural fit/confirm split; not sealed
            3    Toolbox seed_policy            labelled holdout seeds; unenforced
ADMISSION   1    Hecate contract v3             mandatory NULL_TWIN/CHEAT/SIMPLE_ALT, exact; draft
            2    Ludus fixtures                 Ledger/Orchard/Nim; Nim exposes a class blind spot
            3    Toolbox admission              determinism plus power-checked agreement
TWINS/LEAK  1    Tyche TSD + causality audit    absence twin and future-read check, with tests
            2    Ludus differential audit       4/4 injected leaks; one state pair; secrets hand-named
            3    Ensorain marginal surrogate    exact twin for interaction structure
            4    Ares three modes               absent and shuffled twins on every world
            5    Cosmos P1 probe                cross-validated probe plus null; template for WLD-05
BASELINES   1    Ensorain N0-N4 (+N6)           constant to tuned batch; N6 came post-data
            2    Archaeon WSE nulls/positives   constant, echo, lagged echo; equality only
            3    Hecate alien baselines         shipped before any data
            4    Cosmos definition rung         zero-parameter label rule; enforced as text only
THRESHOLDS  1    Cosmos locate.py               CRN-ladder location with SE; the only one in scope

----------------------------------------------------------------------
COULD NOT DETERMINE
- The Ludus atlas contents: they are in M1 Postgres, not in git. The 716 dossiers were not opened.
- Test pass counts. I report function counts from git grep only; no suites were run, by rule.
- Archaeon's S1-S7 hidden-bitstring world (exact DP optimum O for small L, per the dossier) was not opened. It is a possible IDENTIFY seed.
- Not read beyond line counts and headers:
  - campaign6 fixtures.py and pressure/schedules.py;
  - the z80atlas engine used by ENVGATE.
- Hecate: none of the 36 evaluate.py or 17 spec.json files in HT-* were opened.
- Ensorain: WTP v1/v2 genome and detectors, the LM01 harness, validate3.py.
- Cosmos:
  - the holdout directories and test_holdout_isolation.py, not opened by rule;
  - the withheld C3 branches (not on origin);
  - D2 custody (dossier only);
  - store.py.
- Tyche: the v0/v1 code and organisms.py.
- Per-tick throughput for the WSE, C6, Tyche and Hecate worlds is not recorded anywhere I found.
- Restricted-class optimum, searched by reading each solver and by git grep over the scope directories for memoryless, k-state, non_adaptive, best_window and restricted class. Nothing computes the best value of any restricted class.
- Other R6 or R4 generators, searched with git grep for "def gen_R6", the truth payload pattern and "def gen_R4". The R6 pattern exists only in reasoning_phase0.py and a copy in harmonia/experiments/test_verifier_z3.py. No R4 generator exists.

----------------------------------------------------------------------
SURPRISES
1. The brief's pathspec ':!**/*holdout*/**' excludes directories only. A tracked file, prometheus/cosmos/tests/test_holdout_isolation.py, is not covered. One of my count-only git greps scanned it and returned a match count (10). No content was shown or opened. My later searches added ':!**/*holdout*'. The common brief should add it too.
2. Tyche's "exact subset MI" is plug-in MI with a permutation correction. Only the table-law order is exact.
3. Hecate:
   - The certified answer key is tracked in git and can be regenerated from a public seed.
   - The leak test is a substring match.
   - The "control-first generator" is an LLM prompt; the deterministic contract is an unissued draft.
4. The R6 answer leak is still live in code (one commit, 2026-06-09). Separately, gen_R8 tests lemma selection, while Canon R8 means strategy selection.
5. WSE W8: the ASKO construction that leaked is unchanged, although READOUT_v01 says it was fixed in v0.2. survey.py never calls null_scores.
6. Ares search.run selects its final champion on the held-out evaluation set. This is the Sis D6 failure, still in code.
7. Ludus:
   - Bench policies are given the transition model.
   - Ball-under-couch demands zero memory, because the observation carries the full history.
   - Ludus has no pytest tests; the dossier's "25 tests" are scripted asserts.
8. The toolbox's second implementation shares RNG code with the reference. The committed mutation ledger has 92 entries, all CAUGHT; the dossier says 85/85.
9. Cosmos: sealing is tamper evidence plus subprocess isolation, not access control. The definition rung is enforced only as a regex on prose. The C3 certificate has no unit tests.
10. No component in scope computes the best value of any restricted class, so every demand certificate for the nine families must be written new.
