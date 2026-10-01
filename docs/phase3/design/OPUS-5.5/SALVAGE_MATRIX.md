# Salvage matrix -- OPUS-5.5 (Epimetheus)

Status: written AFTER the freeze of REQUIREMENTS.md v2 and RSE_ARCHITECTURE.md (commit 77d3c99c3); deduplicated and
corrected after the final review (wf_335d0a49-a24). Currency 2026-10-01.
Machine-readable: salvage.jsonl (130 distinct components, one per line), produced by tools/salvage_adjudicate.py from
the first-version evaluation rows (salvage/salvage_v1.jsonl, 143 rows) and the raw skeptic records
(salvage/skeptic_challenges.jsonl, 57). Component digests: salvage/{org-a,org-b,world,search,meas-a,meas-b,infra}.md.

## 0. Method

The charter's question was asked of every candidate: does this satisfy a frozen Phase 3 requirement better than
rebuilding it? Seven evaluators (workflow wf_93b1779f-c3f) read the source and tests of their group against
requirements.jsonl and RSE_ARCHITECTURE.md; tests were run only when clearly pure, and only on scratch copies (git
archive), never in the repository. For every KEEP, HARDEN or EXTRACT recommendation an adversarial skeptic then tried to
refute it by opening the code and running probes in scratch. The final category in salvage.jsonl is the skeptic-adjusted
one; the evaluator's category and reason and the skeptic's verdict and evidence are kept beside it, and the rendered
disposition (s7) is the skeptic-adjusted one. Skeptics also listed 57 components the evaluators did not assess (s6);
they are UNKNOWN.

Corrections after the final review. Several components had been evaluated by two groups, some with conflicting
categories, and four skeptic records had been attached to the wrong row by a fuzzy name join (one of them moved the
Proteus foundry VM from RETIRE to REBUILD against its own reason). tools/salvage_adjudicate.py joins skeptic records by
evidence identity, merges duplicate rows, and resolves conflicts by a fixed rule: a skeptic-reviewed category beats an
unreviewed one; when both are reviewed, the category with less code reuse wins (KEEP > HARDEN > EXTRACT > REBUILD >
HISTORICAL_CONTROL > RETIRE); a file a kept fixture depends on is HISTORICAL_CONTROL rather than RETIRE. Every merge,
correction and shared-file assignment is listed on the affected row in s7.

Every agent here is Claude-family (independence class I1 relative to most of the code), so this matrix carries the same
discount as the rest of the package; a cross-family re-derivation of a sample is an open item (OPEN_QUESTIONS OQ18).

## 1. Result in one table

<!-- BEGIN GENERATED SALVAGE COUNTS -->
    category              count   share   what it means here
    KEEP                      0    0.00   nothing is suitable as is
    HARDEN                    4    0.03   sound concept and code; fix named defects, then use
    EXTRACT                   1    0.01   lift a small primitive into shared infrastructure
    REBUILD                  26    0.20   the need is REQUIRED; build new (4 greenfield with no predecessor; 22
                                          replace an inadequate predecessor whose design becomes the
                                          specification)
    HISTORICAL_CONTROL       73    0.56   not production machinery; known-answer fixtures, planted
                                          positives/negatives, canaries, anti-calibration items or design
                                          references
    RETIRE                   26    0.20   no Phase 3 role
    total components        130

Deduplication: v1 had 143 evaluation rows; 13 rows described a component already evaluated by another group and are
merged into it (kept in each row's 'superseded' field), leaving 130 distinct components. Four skeptic records had been
attached to the wrong row by a name-based join; they are removed (tools/salvage_adjudicate.py, MISJOINED).

Skeptic verdicts on the v1 rows: 57 challenges, 53 downgrades, 4 upheld; 53 category changes (35 EXTRACT ->
HISTORICAL_CONTROL, 9 EXTRACT -> REBUILD, 5 HARDEN -> REBUILD, 4 EXTRACT -> HARDEN). 49 move toward less code reuse; the
other 4 are EXTRACT -> HARDEN, which sits higher in the reuse ordering but was recorded by the skeptics as a downgrade
(more fixing before any use). 0 changes came from a verdict other than DOWNGRADE. The two 'upward' changes reported in
the first version (RETIRE -> REBUILD, RETIRE -> HISTORICAL_CONTROL) were the mis-joins.
<!-- END GENERATED SALVAGE COUNTS -->

The pattern is itself a finding: the code that looked most reusable usually failed open somewhere a probe could reach
(s5), and no skeptic verdict was an upgrade.

## 2. What survives, by architecture slot

**R0 Reality kernel.** Nothing is kept. The four load-bearing R0 pieces -- the signed verdict batch job, dependency-driven
demotion, the row-class predicate filter, and a session-log token harvester -- have no implementation anywhere in the
repository (confirmed by search) and are greenfield builds. Salvage is limited to:
- prometheus.toolbox receipt schema: REBUILD after deduplication (it was EXTRACT in one group and part of a REBUILD in
  another; both skeptics found the same defects: optional chain, unkeyed ids, json default=str collisions). Its schema
  design and forensic-scan property tests become acceptance tests for the new R0 ledger.
- productive_liveness (HARDEN): the right work-aware liveness design for derived status (INF-03); fix the restart and
  attempt-window inequalities.
- Keyed random streams: REBUILD. The SplitMix64 and counter-hash generators are correct cores with flawed derivation
  (non-injective seed_from; derivation keyed by current state; 32-bit context state); the skeptics recommend a standard
  counter-based generator (Philox/Threefry) behind a declared key schema and launch-time validator (REP-07), with the
  old generators kept as golden-vector fixtures.
- Design rules only (HISTORICAL_CONTROL): SFE's prediction-before-observation and evidence-class rules (its runtime lets
  producers write verdicts, which PRV-02 forbids); the LF-normalisation rule of comms.manifest (its binary detection
  rewrites short binaries and lets distinct blobs collide); the workspace guard's fail-closed lesson (its receipt fails
  open); Alethelia's UNKNOWN-is-never-narrated contract (it reads CALM on empty sources); Metis's dependence-collapse
  kernel (it defaults unknown ancestry to independence).
- Agent Fabric: REBUILD. Its database invariants are right, but most of its 23 recorded defects are unrepaired in the
  frozen code, its worker is Linux-only, gitignored files carry over between attempts, and its Claude executor is a
  read-only research executor, not a build executor.

**R1 World forge.** Nothing is kept. Ensorain's answer-keyed hidden-state processes with exact Bayes (arc3/suff worlds;
known-answer tests pass) are HISTORICAL_CONTROL after deduplication: they are worth more as a sealed known-answer
cross-check of the F3 solver, kept unread by the F3 authors (WLD-04, WLD-17), than as the F3 core. REBUILDs keeping the
design: the Ludus differential leak audit (single-state only; must roll forward over every channel), the Cosmos holdout
broker (integrity, not secrecy; the producer writes verdicts), Charon's ceiling_v0 hidden-group universe
(the only action-driven hidden-state family; its structural dial is confounded by one shared random stream). Fixtures:
the Ludus Nim-345/Bouton decoy and leak variants for WLD-17; alien_circuitry's exact monoid oracle and its
non-quotient-disjoint split (the regression fixture WLD-03 needs); Tyche's parity and secret-sharing needle classes.

**R2 Measurement bench.** Nothing is kept and no historical component is a ruler with an MEA-01 dossier. Two HARDENs: the
Ananke explib qualification seed (fail-closed outcomes, exact beta quantiles matching scipy; its certifier certifies
without the attainability check when arguments are omitted) and the Ananke swap_rel interchange decision rule (11 tests
pass; its false-certificate bound fails under skewed nulls). REBUILDs keeping the design, in order of value: the NPE
z8shadow write-provenance tracer with its fixture pack and mutant tracers (spec source for DEV-14); the Aether one-bit twin with locality and
counterfactual-parent audit (causal reach and closure audit); the Hephaestus closure gauntlet protocol (capacity proofs);
Ares carrier attribution (concepts only); the Ergon bounded-null decision skeleton (it silently truncates unequal arms); a
single known-answer-tested statistics library (none exists; several gate libraries are anti-conservative). The Ananke
mirror-twin carrier-swap lens (the best interchange instrument in the record) and the Archaeon/Z80 taint VMs are
HISTORICAL_CONTROL after deduplication: the skeptic-reviewed rows found their code unusable on DGM hooks, so the
interchange ruler and the provenance shadow are new builds that use them as failure corpus and design reference. The
Ensorain null ladder is likewise HISTORICAL_CONTROL (its missing same-class tuned rung is a fixture for MEA-03). Fixtures:
Harmonia VACUOUS_READINGS (negative fixtures for the null-certificate checker), NULL_BOOT (a null that cannot fire),
attacks/REGISTRY (the canary failure-class list), Ensorain WTP specimens (three clean ruler false positives), the
Cosmos definition rung case, CVT-R panel design and painter plants, P-11 geometry, Crius id-counter cheats, the Ares
zero-hidden latch, Aphrodite's "library as proposal prior" shape (a mandatory DEV-14 planted organism, which the
executor rule must classify as order 1).

**R3 Substrates.** Nothing survives as a substrate. The DGM kernel and its slow reference interpreter are a new build
(REBUILD, cost L): no candidate has lifetime structural development, stable ids under rewrite, an in-kernel provenance
shadow, individual organisms and an ablation lattice on one code path. Proteus graph_organism.v1, the nearest candidate,
has a fixed lifetime structure, renumbers ids on deletion, and has a tick-ABI defect that made non-persistent state
persist across ticks (reproduced; it also affects Archaeon Campaign 6 evaluators). Crius's VM fails ORG-16/17 by
construction (its PSIM/PMATCH simulate procedures with the world's own transition function). No candidate is eligible as
the probe kernel or second substrate, because all are same-family code this programme has read (I1 at best) and the
Z80 VMs and PTE share the conventions the probe is meant to avoid. The familiar reference learner (a conventional
neuromodulated plastic RNN and a GRU meta-learner) is a new build with no row in salvage.jsonl, because nothing
evaluated qualified; Ares is HISTORICAL_CONTROL.

**R4 Search and pressure.** No engine survives. The four estimators the architecture depends on -- rediscovery-from-
distance p_hit(k), the random-sampling needle rate, the concentration-floor launch gate and the pressure certificate -- do
not exist anywhere and are new builds (they have no rows in salvage.jsonl, because nothing was there to evaluate); Archaeon's reachability table measures a different quantity and types zero hits in three
runs as unreachable, the null PRS-03 refuses. Salvage: SFE's reference executors (BitString, NK landscape with certified
optimum, strict coordinate scan; EXTRACT) as exact known-answer landscapes for estimator tests; Tyche's eps-lexicase
(HARDEN; correct, but its tests pass for uniform random selection). Known-answer reachability fixtures
(HISTORICAL_CONTROL): the PROTEUS-46 harness (a plant exists; a horizon-3, tie-rejecting greedy walk provably cannot reach
it), Ananke's in-space FLIP/XOR plants, Crius PARTS (a 47-edit mechanism against an (8+24)x300 search), Archaeon's copier
census (a measured random-sampling hit rate), Apollo's O1 enumerator, the D-5 R==E package. The Deep Frontier and NPE
schedulers are kept only as anti-patterns.

**R5 Interpretation.** prometheus_llm is REBUILD: right shape, but its audit is opt-in and drops retries and cache
tokens, its default model has an unknown family, it silently falls back to the first listed model, and about 70 files call
providers directly around it.

## 3. Answer to charter Q8 (what fraction should conceptually survive)

Counts are over the 130 distinct components after deduplication (s1).

- **As running engines: none.** Zero of roughly twenty historical engine-level systems (substrates, world engines, search
  loops) carries into Phase 3 as an engine.
- **As code: about 4% of evaluated components** (5 of 130: four HARDEN, one EXTRACT), all small primitives (liveness
  derivation, eps-lexicase, NK/BitString landscapes, a qualification seed, an interchange decision rule). By lines of
  code it is well under 1% of the repository.
- **As designs to rebuild: about a sixth** (22 of the 26 REBUILDs replace a predecessor whose design becomes the
  specification: the write-provenance tracer, the causal-reach twin, the capacity gauntlet, the leak audit, the
  sealed-split broker, the receipt schema, the keyed-stream schema, the job runner; the other 4 are greenfield).
- **As historical controls: more than half** (73): known-answer fixtures, planted positives and negatives, canaries,
  anti-calibration items and design references. This is the "fossil record and instrument foundry" in its most useful
  form: the failures of Phase 1 and 2 become the qualification tests of Phase 3.
- **Retired: about a fifth** (26).

So, conceptually, roughly a fifth of the scientific machinery survives (code plus designs, 27 of 130), essentially none
survives as running machinery, and more than half survives as test material. The single most valuable surviving asset
is not code at all: it is the recovered failure taxonomy, which REQUIREMENTS.md maps onto enforced requirements with
counterfeit fixtures (every one of the 70 classes has at least one covering requirement that carries a counterfeit;
checker-enforced).

## 4. Consequences for the build plan

- The vertical slice (S1) reuses almost nothing as code: productive_liveness for derived status and SFE's NK/BitString
  landscapes as estimator fixtures. The receipt schema and the keyed-stream pattern are specifications for new code;
  the Ensorain exact-Bayes processes are a sealed cross-check for the F3 solver (S2). Everything else in R0, the DGM
  kernel and the F1 family are new code. The build-cost
  estimate in RSE_ARCHITECTURE.md s7 (60-200M tokens processed for the MVP) already assumes this.
- The historical-control corpus needs packaging work (seal the planted sets, re-express Z80 and Proteus cheats in DGM
  physics, freeze the known-answer fixtures with their expected outcomes). This is E1 work in S2.
- No existing seat's code is a dependency of the Phase 3 core, which removes the historical coupling problem (129 files
  import Proteus; producer and auditor imported each other).

## 5. Defects found during salvage (reported for routing, not fixed)

These were found by reading code and running probes in scratch copies; most were reproduced by a skeptic. They are not on
the owners' records and have not been confirmed by them. Lane discipline applies: this seat does not fix them; the list is
reported to Aporia for routing. Full text in salvage/NEW_DEFECTS.md.

    component                         defect (short)                                                 group
    proteus/graph/vm.py               tick counter never advanced; non-persistent state persists      org-a
                                      across ticks (also Archaeon Campaign 6 evaluators)
    comms/manifest.py                 binary detection = NUL in first 8 KiB; short binaries are       infra
                                      LF-normalised; distinct 4-byte blobs hash equal
    comms/identity.py                 null or missing registry fields pass on any database            infra
    archaeon/workspace.py receipt()   git failure yields base_sha '' and dirty False (fail open)       infra
    Harmonia qualification_rules.py   t_crit rounds df up (anti-conservative); .025 table used for     meas-a
                                      any n_primary >= 2 (confirmed against scipy)
    Nemesis cheatlib chance_floor     short or missing candidate counts give permissive floors         meas-a
    Hecate shadow_decisions q()       wrong rational recovery inside its own documented domain         meas-a
    Ergon p3_analyze decide()         unequal arms silently truncated to min length                    meas-a
    Charon c1c2 C2                    fails open for 0-based seq loaders                               meas-a
    Ananke explib certify_gate        CERTIFIED without attainability when arguments omitted           meas-a
    Ananke rng.py                     32-bit context state; birthday collisions near 2^16 contexts     org-b
    proteus/foundry/prng.py           seed_from not injective; derive() depends on current state      search
    Proteus crucible equilibrium.py   spectral_gap deflation wrong unless stationary dist. uniform     search
    Tyche lexicase tests              pass for uniform random selection                               search
    D-5 fast/reference equivalence    compares r0 and <= 2 inputs only; a 3-input probe diverges       org-a
    SFE runtime                       record_observation accepts the client's outcome as a verdict    infra
    Cosmos holdout broker             producer computes and records G6 verdicts; spec read in process  world
    Cosmos independence.py            sys.path sibling imports read as stdlib -> false 'independent'   world
    toolbox receipt                   json default=str truncates arrays -> receipt-id collisions      infra
    Archaeon causal-lineage validator certifies laundered ancestry                                     meas-b
    Ares carriers classify()          REDUNDANT verdict reachable through a different code path        org-b
    Alethelia                         empty sources read CALM                                          infra
    prometheus_llm                    default model of unknown family; silent first-model fallback     infra
    Fabric                            most of DEF-ODY-001..023 unrepaired in frozen code               infra

## 6. Components not evaluated (UNKNOWN)

Skeptics named 57 components the evaluators missed (listed per group at the end of each salvage/<group>.md digest and in
salvage/MISSED.md). Notable: the incubation_d homoiconic stack machine with a meta tier that edits blocks as data (a
possible design reference for the DGM's code-as-data aspect), the agent_d4_blind substrates with known landscape geometry
(possible known-answer fixtures for R4), primordial/qd/archive.py (a better QD archive reference), the Aether independent
second oracle (a differential-testing exemplar), the Aether RunPod GPU launcher with a billing-reconciled receipt ladder,
and several more workspace-guard and canonical-bytes copies. None changes the architecture; any could change a single
REBUILD into a HARDEN.

## 7. Full component table (generated from salvage.jsonl)

<!-- BEGIN GENERATED SALVAGE TABLE -->
### HARDEN (4)

- **Tyche eps-lexicase and novelty** [search; Tyche; cost S] (evaluator: EXTRACT). Slot: R4. Serves: PRS-05, AGR-10.
  - Disposition: HARDEN (extract eps_lexicase only after replacing its tests; fix novelty and the trace before reuse). Skeptic finding: eps_lexicase itself is correct. I recovered the exact selection probabilities 1/4 and 3/4 (991 and 3009 of 4000 draws) by loading the function from tyche/ecology.py:195-210 in a temp dir. 'Tested' is refuted: uniform random selection passes test_lexicase_keeps_specialists (test_v0.py:144-150; verified, miss probability about 0.9^400), and test_strict_lexicase...
  - Correctness: test_lexicase_keeps_specialists and test_strict_lexicase_with_no_eligible_returns_nothing run here and passed. The specialist test is weak: it checks only that two individuals appear in 400 draws.
  - Coupling: numpy only.
  - Skeptic: DOWNGRADE.
- **Ananke explib W2-F (attainable gate certification, control competence, unit-aware stats)** [meas-a; Ananke; cost S] (evaluator: EXTRACT). Slot: R2 qualification library seed (dossier checks, control audit, unit declaration). Serves: MEA-01, MEA-05, SCI-06, SCI-05, MEA-11.
  - Disposition: HARDEN. Skeptic finding: This is the best component in the group, and part of the claim holds: _betainc_upper matches scipy beta.ppf exactly (0/300, 3/300, 20/2000), outcomes.py is genuinely fail-closed, and the tests include must-fail cases. But the 'fail-closed' certifier is not. certify_gate appends A_attainable only when verdict_fn and design_space are passed (attainable.py:119-122).
  - Correctness: Tests run here: 16 pass, 1 skip.
  - Coupling: numpy. The conftest sets CUDA_VISIBLE_DEVICES. Code is triplicated across harvest dirs (W2-F, W2-AE pkg, W2-AE scratch_apply).
  - Skeptic: DOWNGRADE.
- **Ananke swap_rel.py relative swap certificate (REL4/H2)** [meas-b; Ananke; cost S] (evaluator: EXTRACT). Slot: R2 known-answer statistics library. Serves: MEA-11, CAU-04, SCI-14.
  - Disposition: HARDEN. Skeptic finding: RUN: test_swap_rel.py, 11 passed in 1.7 s from the scratchpad, with no repo writes (git status clean). New probes, also pure numpy, from the scratchpad. (1) The advertised false-certificate bound fails under a skewed or mixture null. That is the case the docstring says is untested (swap_rel.py:8-9), and the one lens_swap's S/C/N census exists for.
  - Correctness: 11 tests: nesting in REL3, recovery of a near-degenerate flip, point intervals, false-certificate smoke at the boundary, label floor/guard.
  - Coupling: numpy + stdlib only
  - Skeptic: DOWNGRADE.
- **productive_liveness health derivation** [infra; Pronoia; cost S]. Slot: R0 derived status for the runner and standing loops. Serves: INF-03, CMP-08.
  - Disposition: Right design with one wrong inequality. Define separate attempt start and end fields.
  - Correctness: T1-T4 plus cheat controls pass. A probe shows a 10-minute job that succeeded 5 minutes ago reads 'incoherent'.
  - Coupling: Pure.
  - Skeptic: UPHELD.

### EXTRACT (1)

- **SFE reference executors (BitString, NK landscape, coordinate scan)** [search; Daedalus; cost S]. Slot: R4 test fixtures. Serves: PRS-03, PRS-02, MEA-11.
  - Disposition: Tested, stdlib-only, exact known-answer landscapes. They make PRS-03's test ('estimator recovers known p_hit on planted landscapes') concrete, because needle sizes come from enumeration, and the strict scan is one declared policy for PRS-02. Lifting two classes is cheaper than writing a certified landscape. WorkerLoop/Foundry are R0 infrastructure and out of this group.
  - Correctness: test_sfe_nk_landscape.py run here: 50 passed. Covers integer-exact solved status, joint-permutation invariance, a negative fixture that must move, the k=0 optimum matching enumeration, the one-scan guarantee, and ties keeping the original.
  - Coupling: Stdlib (hashlib); executor ABC; no host assumptions.
  - Skeptic: UPHELD.

### REBUILD (26)

- **Proteus SplitMix64 keyed random streams** [org-a; Proteus; cost S] (evaluator: EXTRACT). Slot: R0 deterministic runner (keyed streams). Serves: REP-07, REP-01, ORG-08.
  - Disposition: REBUILD. Skeptic finding: The recommendation rests on two claims: the value is (a) the semantics and (b) the receipts. I opened the code and both claims fail. Only the generator core holds up. WHAT HOLDS. next_u64 (prng.py:39-44) is correct SplitMix64. My probe ran on a scratch copy, not the repository, and seed 1234567 reproduces Vigna's published five-output vector exactly.
  - Correctness: Every Proteus replay test exercises it, and they passed. Cross-host receipts exist (not re-verified). There is no statistical battery, which keyed-stream semantics do not need.
  - Coupling: Stdlib (hashlib) only. No consumers need to change.
  - Skeptic: DOWNGRADE.
  - Superseded row: proteus.foundry.prng keyed streams [search; evaluator EXTRACT; v1 final HARDEN; skeptic DOWNGRADE].
  - Correction: merged: same file evaluated by org-a (REBUILD) and search (HARDEN), both skeptic-reviewed; less reuse wins. The generator core is correct SplitMix64; derivation and seeding are rebuilt behind a declared key schema (REP-07), with prng.py kept as a golden-vector fixture.
- **DGM kernel + slow reference interpreter (new build)** [org-a; Phase 3 build; cost L] (greenfield). Slot: R3 primary substrate (DGM) + REP-02 slow reference interpreter. Serves: ORG-01, ORG-02, ORG-03, ORG-04, ORG-05, ORG-06, ORG-07, ORG-08, ORG-09, ORG-10, ORG-13, ORG-19, ORG-20, ORG-21, DEV-03, DEV-14, REP-01, REP-02, REP-07, CMP-01, CAU-08, CAU-09, PRV-10.
  - Disposition: The need is REQUIRED at SLICE/CORE, and no existing substrate covers the expensive rows: developmental instructions, shadow, stable ids, interventions, RNG-neutral switches, two encodings and a fast kernel. Write the slow Python reference first as the executable spec, then a fast kernel tested against it on full state over a generated corpus with boundary and maximal-arity cases. Encode the twelve lessons in digest s4 as tests.
  - Correctness: Not applicable (not yet built).
  - Coupling: Should depend only on R0 (keyed streams from C3, runner, ledger). The runner must own tick boundaries.
  - Skeptic: not challenged.
- **Ares carriers.py carrier attribution** [org-b; Ares; cost S] (evaluator: EXTRACT). Slot: R2 matched ablation / closure-audit ruler. Serves: ORG-19, CAU-05, CAU-09, CAU-06, CAU-01, CAU-02.
  - Disposition: REBUILD (R2 closure/lesion ruler on DGM hooks, S-M); the code, its defects and its 3 hand-wired plants are kept only as an Ares-specific HISTORICAL_CONTROL record. Skeptic finding: (1) The taxonomy has a hole. classify() (ares/carriers.py:137-149) returns REDUNDANT when cut_all collapses and no single class cut does. But cut_all is not the conjunction of the class cuts. It runs on a different code path, a Config with allow_keep=False, allow_plasticity=False and reset_each_step=True (carriers.py:104-105).
  - Correctness: test_carriers passes (run here): separates hand-wired RECUR from KEEP, finds the single carrier edge, detects an output self-loop invisible to node ablation, moves it by transplant. 3 same-author plants (class I0 under MEA-02).
  - Coupling: imports ares.search and ares.substrate; numpy; tied to Ares array layout.
  - Skeptic: DOWNGRADE.
  - Superseded row: Ares carriers.py edge/SCC carrier instrumentation [meas-b; evaluator REBUILD; v1 final REBUILD; skeptic none].
  - Correction: merged: exact duplicate (org-b and meas-b).
- **Ananke counter-hash keyed RNG** [org-b; Ananke; cost S] (evaluator: EXTRACT). Slot: R0 deterministic runner (keyed streams). Serves: REP-07, REP-01, ORG-08, ORG-20.
  - Disposition: REBUILD (S): a standard counter-based generator with a wide key and counter (e.g. numpy Philox/Threefry) behind a declared key schema (arm, world instance, organism, stream, tick, node, sub) plus a launch-time registry/validator; keep rng.py only as a golden-vector fixture for PTE replay. Skeptic finding: (1) The state is 32 bits (prometheus/ananke/rng.py:11-33). H chains hash32(h ^ k), so every downstream draw for a context is a function of one 32-bit value. Distinct (tick, site) prefixes collide by the birthday bound at ~2^16 contexts per (world, stream). The expected number of colliding pairs is ~n^2/2^33: about 1.2e6 pairs at 1e8 contexts, each pair sharing every sub-keyed draw.
  - Correctness: Exercised by test_oracle_selfcheck known values and the conformance tests (passed here).
  - Coupling: torch for tensor form; host form pure Python.
  - Skeptic: DOWNGRADE.
- **Ludus differential leak audit (probe_pair)** [world; Ludus; cost S] (evaluator: EXTRACT). Slot: R1 differential all-channel leak audit. Serves: WLD-07, WLD-17, MEA-05.
  - Disposition: REBUILD. Skeptic finding: probe_pair (ludus/arena/audit.py:42-74) is a 30-line field-by-field comparator bound to the retired arena State interface (sibling `import core`, :32). The pair construction that ran is single-state: run_controls.py:250-257 compares only the two states just after the deal and never steps forward.
  - Correctness: Seat controls: fires on all 4 injected Kuhn leaks, silent on clean Kuhn. I re-ran audit.py: clean worlds CLEAN; one by-design finding (full replay names chance outcomes).
  - Coupling: bound to arena State API; sibling imports
  - Skeptic: DOWNGRADE.
  - Shared file ludus/controls/fixtures.py: assigned to Ludus qualification fixtures (Ledger, Orchard, Nim345+Bouton, bench corruptions, MartianDiceOneRay, Kuhn leak variants) [HISTORICAL_CONTROL] (the Kuhn leak worlds are kept fixtures; the leak audit itself is rebuilt).
- **Bellerophon Worlds Kernel: receipts, IR digest, replay, keyed streams** [world; Bellerophon; cost M] (evaluator: EXTRACT). Slot: R0 deterministic runner + ledger. Serves: REP-01, REP-07, PRV-01, PRV-03, CMP-02, PRV-04.
  - Disposition: REBUILD. Skeptic finding: I ran a scratch probe on receipt.py with ReceiptWriter and synthetic receipts. (1) Dropping the last 2 whole records: scan() reports no defects and read_all returns 2. (2) Editing science.objective in record 1, recomputing its id and re-chaining: no defects.
  - Correctness: Ran test_admission, test_admission_power, test_integrity, test_replay_committed: 259 passed in 46 s
  - Coupling: stdlib plus optional numpy/redis; host name in receipts; Windows WMI note; only prometheus/atlas_bee imports it
  - Skeptic: DOWNGRADE.
  - Superseded row: prometheus.toolbox receipt [infra; evaluator EXTRACT; v1 final EXTRACT; skeptic UPHELD].
  - Correction: merged: receipt.py evaluated by world (reviewed: REBUILD) and infra (reviewed: EXTRACT upheld); both skeptics found the same defects (optional chain, unkeyed ids, json default=str collisions); less reuse wins. The schema design and the forensic-scan property tests are kept as acceptance tests for the new R0 ledger.
- **Cosmos holdout broker + audit + ReceiptChain** [world; Cosmos; cost M] (evaluator: HARDEN). Slot: R1 sealed quotient-disjoint splits / evaluation broker. Serves: WLD-03, PRV-03, SCI-15, PRS-04.
  - Disposition: REBUILD. Skeptic finding: (1) The producer writes verdicts. adjudicate/intervene/intervene_fresh compute and record HOLDOUT_TESTED, 'G6 PASS/FAIL' and 'G6b PASS/FAIL' themselves, with hard-coded thresholds (broker.py:121, :182-186, :257-261). That is the opposite of R0's 'only the signed verdict job writes verdicts'. (2) Commit-then-reveal is unenforceable against the producer. The spec is read in-process (:69).
  - Correctness: Ran tests/test_audit.py: 5/5 cheat controls pass (mutation after freeze, reveal without prior predictions, test before freeze, rewritten committed copy)
  - Coupling: numpy, sqlite, subprocess; cosmos miner law objects; git subprocess for code identity; COSMOS_HOME on the user profile
  - Skeptic: DOWNGRADE.
- **Cosmos AST code-lineage audit** [world; Cosmos; cost S] (evaluator: EXTRACT). Slot: R0/R1 independence-class computation. Serves: REP-06, WLD-05, AGR-17.
  - Disposition: REBUILD. Skeptic finding: I ran it on real repo code (scratch, read-only). closure(ludus/arena/audit.py) is empty: `import core` via sys.path siblings is resolved only against REPO root (independence.py:23-29), so it reads as stdlib. It classes ludus_audit and ludus_fixtures as SEPARATE lineages, although both load arena core/worlds through sys.path (fixtures.py:295-302). That is a false 'independent' verdict on in-repo code.
  - Correctness: none observed (no dedicated test opened)
  - Coupling: REPO-relative path resolution; stdlib ast
  - Skeptic: DOWNGRADE.
- **Charon ceiling_v0 hidden-group universe** [world; Charon; cost S] (evaluator: HARDEN). Slot: R1 active-identification family. Serves: WLD-06, WLD-01, WLD-15, WLD-02.
  - Disposition: REBUILD. Skeptic finding: (1) The structural dial is confounded. One random.Random draws shifts, then perms (F_T draws none), then tags, then the sensor (universe.py:53-105). In a scratch probe over 50 seeds, F_T vs F_M at the same seed had equal shifts 50/50 but different tag states 50/50 and different sensors 50/50. Moving the commutativity dial redraws the universe, which breaks WLD-06's 'sweeps move certificate components' contrast.
  - Correctness: validate.py oracle soundness audit exists. Spec reconstructed after working-tree loss with no surviving hash (SPEC.md:3-13); universe restored from transcript and .pyc (universe.py:3-6).
  - Coupling: stdlib universe; LLM arms call network lanes (reasoner.py:42; lanes.py:28-37)
  - Skeptic: DOWNGRADE.
- **Hecate evaluator contract + metamorphic harness** [world; Hecate; cost S] (evaluator: EXTRACT). Slot: R1 admission-ladder evaluator; R0 verdict preconditions. Serves: WLD-02, SCI-05, MEA-05, MEA-03.
  - Disposition: REBUILD. Skeptic finding: There is no margin or MDE logic. The outcome is threshold-only on seed aggregates (evaluator_contract.py:369-394). In memory I set TREATMENT mean 0.7502 and SIMPLE_ALT 0.7498 against threshold 0.75, per-seed sd about 0.1, 5 seeds. Result: SIGNAL, 'SIMPLE_ALT fails [S1]'. That is exactly WLD-02's named fake ('margin smaller than the ruler MDE: refused').
  - Correctness: Ran test_evaluator_contract.py + test_alien_generation.py: 64/64 pass
  - Coupling: stdlib; harness copies worlds to scratch
  - Skeptic: DOWNGRADE.
  - Shared file hecate/metamorphic/harness.py: assigned to Hecate metamorphic evaluator harness [HISTORICAL_CONTROL] (both rows skeptic-reviewed; less reuse wins: the harness is HISTORICAL_CONTROL, and the REBUILD row covers the evaluator contract only).
- **Archaeon WSE GA loop** [search; Archaeon; cost M]. Slot: R4. Serves: PRS-02, PRS-06, REP-01.
  - Disposition: About 300 lines that must be rewritten for the DGM genome anyway. Its two load-bearing defaults point the wrong way for Phase 3: streams are shared across arms by default, and recombination cannot be cleanly switched off. Keep the step-API shape, gen0 provenance and the dual per-ask/episode readout as design notes.
  - Correctness: archaeon/tests/test_wse.py has an independent reference evaluator, POS/NULL organisms, a cheat battery and a run_cell determinism test; test_campaign3_machine.py covers inject and the offspring cap. Both run here: 31 passed.
  - Coupling: Imports proteus.foundry throughout; pathlib, OS-neutral; no GPU; harnesses add SerendipityFoundryClient to sys.path.
  - Skeptic: not challenged.
  - Shared file proteus/foundry/{generate,grammar,lineage}.py: assigned to Proteus foundry v0 VM + grammar [HISTORICAL_CONTROL] (frozen with the foundry under the C4 fixtures; the GA loop's design is rebuilt without them).
- **Archaeon reachability table / corridor / typed states** [search; Archaeon; cost NA]. Slot: R4. Serves: PRS-03.
  - Disposition: Wrong estimand for PRS-03: no planted solutions, no k-step p_hit(k), no d0, no path profile, no random-sampling rate. It also types 0 hits in 3 or more runs as OBSERVED_UNREACHABLE_AT_BUDGET (reachability.py:71-81), and states.py:17-18 fires TARGET_UNREACHABLE from it; PRS-03 explicitly refuses this. Reuse only the right-censoring idea; keep the rows as a historical record of budgets tried.
  - Correctness: test_campaign3_machine.py checks that SUMMIT requires a held-out readout and that monotone pooling is correct (run, passed). The estimator itself was never checked against a planted landscape.
  - Coupling: Table path hard-wired inside the repo (reachability.py:37-38); depends on wse.worlds.
  - Skeptic: not challenged.
- **Charon exit-review-3 arm-leak classifier** [meas-a; Charon; cost S]. Slot: R1 leak audit (WLD-07) and R2 MEA-01 content-stripped metadata classifier. Serves: MEA-01, WLD-07.
  - Disposition: MEA-01 and WLD-07 require this need. The instrument's own positive control cannot fail, so its negative reading is uncalibrated. A rebuild needs a planted-leak detection curve per channel on the hardest matched pair plus an exact within-pair null, and it is small.
  - Correctness: NOT demonstrated for the decisive contrast. The positive control (233-238) plants a trailing space on F-answer vs F0, a pair that is already separable at 1.0, so it reads 1.0 with or without the plant (the comment says F-null). The decisive length-matched pair F-null|F-prom-retrieved read 0.50 and was never planted.
  - Coupling: Imports ergon.probe.campaign and sklearn, and writes OUT into charon/probe (line 51, 243).
  - Skeptic: not challenged.
- **Ergon bounded-null machinery (decide, MDE, gate-fire worlds, planted-witness cheat)** [meas-a; Ergon; cost M] (evaluator: EXTRACT). Slot: R2 null-certificate checker (element R, bracket, MDE/SESOI). Serves: SCI-14, SCI-08, SCI-13, SCI-03, MEA-05.
  - Disposition: REBUILD. Skeptic finding: decide() pairs arms by index and silently truncates unequal lengths (p3_analyze.py:87, n=min(len)). Reproduced: arms of 100 and 99 were accepted as 99 pairs with no error. A sign-flip permutation p and a percentile bootstrap CI, two different procedures, jointly gate one label (125-145).
  - Correctness: All 5 gate-fire worlds were called correctly, but only 4 of 6 labels are exercised: UNDERPOWERED, BELOW_USEFUL_SCALE and the validity-failure branch never fire (gatefire_p3.json read here). Cheat control: PLANT2 n 30 gave MRU_HARMFUL. PLANT1 n 30 gave INDETERMINATE, outside its own pass set, and the re-run at n 100 gave +3.38 pp, p 2e-5.
  - Coupling: Pure Python with numpy for the MDE. Domain-specific names (MRU/RANDOM). Writes JSON beside itself.
  - Skeptic: DOWNGRADE.
  - Shared file ergon/gen3/cheat_control.py, ergon/gen3/mde_p3.py: assigned to this row (the skeptic-reviewed row keeps these files).
- **attacks/mutation_harness.py** [meas-a; Charon; cost S]. Slot: R2 CI mutation testing of gating checkers. Serves: MEA-05.
  - Disposition: MEA-05 needs mutation-tested checkers in CI. Use an off-the-shelf or import-hook mutator, and keep the 'report sampled/total, never a bare score' rule.
  - Correctness: A reported finding: cap=20 read 100% where full enumeration read 85.2%.
  - Coupling: Rewrites repository files and runs pytest subprocesses.
  - Skeptic: not challenged.
- **Statistics code repo-wide (no shared library)** [meas-a; many; cost M]. Slot: R2 known-answer statistics library. Serves: MEA-11, SCI-14, SCI-15.
  - Disposition: MEA-11 requires one scipy-backed library with known-answer tests: quantiles, exact binomial/CP, exact sign-flip, permutation +1, TOST, Holm/Bonferroni with ledger-derived family, cluster bootstrap, and power/MDE through a supplied pipeline. Seed it with Hecate auc_exact/CP, the Ergon decide skeleton, explib Units/cluster bootstrap and QR contrast_variance.
  - Correctness: Defects confirmed in this group alone: anti-conservative hand-tabulated t quantiles and wrong Bonferroni (QR), an overflowing binomial tail (AP), nulls that cannot fire (NULL_BOOT, default NULL_PLAIN), float tie handling on lattices (Ergon), and a Gaussian band on 10 permutation refits (exit-review-3).
  - Coupling: Diverse: numpy, scipy, pandas; some host-specific paths.
  - Skeptic: not challenged.
  - Shared file proteus/v0_5/multiplicity.py: assigned to Proteus mutation-kernel crucibles V0.3-V0.6 [HISTORICAL_CONTROL] (the buggy Holm code is an MEA-11 known-answer specimen).
- **Archaeon causal-lineage contract v0.2/v0.3** [meas-b; Archaeon; cost M] (evaluator: EXTRACT). Slot: R2 provenance query layer + R0 row schema. Serves: ORG-08, PRV-10, AGR-04, SCI-17, MEA-10.
  - Disposition: REBUILD. Skeptic finding: Probes run read-only from the scratchpad (PYTHONDONTWRITEBYTECODE, PYTHONPATH pointing at the worktree; nothing written to the repo). The existing pytest suite was not re-run. (1) The validator certifies laundered ancestry, which breaks AGR-04 and PRV-10. HERITABLE = (copies_from, contributes_material) (schema_v02.py:40), and sources(), ancestors() and origins() follow only those relations (:125-137).
  - Correctness: 15 attack fixtures with cheats that must be rejected, and an upgrader test. PORTABILITY01 (REPORTED): adapters for 4 engines; the contract caught adapter defect D1 (12 violations).
  - Coupling: stdlib only; the adapters are engine-specific and separate from the schema
  - Skeptic: DOWNGRADE.
- **NPE z8shadow tracer + interventions + fixture pack** [meas-b; Nestor; cost M]. Slot: R2 write-order tracer (DEV-14) + R3 provenance hooks. Serves: DEV-14, ORG-08, PRV-10, CAU-06, MEA-01, REP-02.
  - Disposition: The most complete write-provenance design in the record, but bound to the Z8 ISA, and its flip confirmation is structurally blind on code-as-data (copied bytes executed before their final store). That is exactly the DGM REWRITE case DEV-14 targets. Port the label algebra, performer=WHAT, the depend/complete arms, the mutant-tracer method and the fixture taxonomy; redesign confirmation as write-event patching; add write orders, reversion and the four planted order organisms.
  - Correctness: Run: selftest 3000 random interactions, 0 mismatches, injected defect detected. Fixture pack on a scratch copy: 0 failures across 26 fixtures/85 loci, 10/10 mutants caught (world-level fixtures not run). REPORTED in GATES.json: G1 451/451 agreement with the independent reference tracer and G2 fresh-set PASS, BUT the flip-coverage floor fails (self 0.447, other 0.125), and the ctrl/pdom labels were never validated.
  - Coupling: Imports the frozen z8.py, world.py and p11.py from a sibling campaign directory; the world fixtures need pin_reproduce (git archive of a pinned commit, cpu8 lease); the production sample was host-local (M2)
  - Skeptic: not challenged.
- **Aether one-bit twin with locality check and counterfactual-parent audit** [meas-b; Aether; cost S]. Slot: R2 causal-reach / closure-audit tool + R3 hook. Serves: ORG-19, CAU-09, CAU-04, DEV-14, ORG-08.
  - Disposition: An exact, self-checking causal-reach ruler on common random numbers. On the DGM (graph locality with edge delays) it serves the ORG-19 closure audit (the hidden-flag fixture IS the unlisted-channel test), interventional confirmation of provenance labels for DEV-14, and transient-state carriers (CAU-09). Small to rebuild; the code is grid-CA specific.
  - Correctness: Null twin, exact relay hop counts, undeclared radius caught, hidden-flag predicate violations, parent audit equal to the assay on a pure relay. REPORTED: bytes-only 32 violations vs full 0; parent audit agrees 84-100%.
  - Coupling: numpy; Aether/test/reference/gpu_aeth01 (a CuPy-ready numpy reference); CPU
  - Skeptic: not challenged.
  - Shared file Aether/observatory/aeth03_propagation.py: assigned to Aether verification kit [HISTORICAL_CONTROL] (kept frozen as a fixture under the verification kit; the one-bit twin design is rebuilt on DGM hooks).
- **Hephaestus closure gauntlet (substrate-capacity probe)** [meas-b; Hephaestus; cost M]. Slot: R3/R2 capacity-proof tool (ORG-14 fixture in CI). Serves: ORG-14, ORG-15, DEV-13, MEA-05.
  - Disposition: The need is real (ORG-14/ORG-15 expressible tier, DEV-13, X4 capacity proofs) and the protocol is sound (nested arms, extensional membership on sealed verify/shift sets, coerced vs typed, three-control battery). But the enumerator works over stateless Python expression trees for Forge reasoning-tool kernels, not stateful DGM programs.
  - Correctness: REPORTED: controls ALL_PASS on two boolean walls; Q045 18 OPERATOR / 2 INCONCLUSIVE. The controls script was run on a scratch copy and did not finish within 300 s.
  - Coupling: agents/hephaestus/src/forge_primitives.py (numpy); writes closure_results/*.json into the repo and records state; workspace_guard
  - Skeptic: not challenged.
- **Agent Fabric store + worker (job runner)** [infra; Odysseus; cost M] (evaluator: HARDEN). Slot: R0 one job runner. Serves: CMP-04, PRV-08, PRV-09, CMP-02, REP-03.
  - Disposition: REBUILD. Skeptic finding: (1) The '23-defect discovery cost' argument fails because most of those defects are still unrepaired. roles/Odysseus/fabric_pilot/DEFECTS.md lists DEF-ODY-001..023. Under the freeze only 015, 019 and 023 were repaired in code, plus 010 in the test only (fabric/FREEZE.md:47-74).
  - Correctness: Invariants are enforced by the schema. FP-001 kill-and-reap probe is REPORTED passed. 23 defects were repaired under a freeze, each with a regression test (FREEZE.md). 347 tasks / 373 attempts ran on ubu001/ubu002 (ixi.md).
  - Coupling: store.connect imports evidence_wiki.ew.db (PEW credential loader) and comms.identity (store.py:87-108). Needs the M1 Postgres. The worker is Linux-only (fcntl worker.py:18, killpg, PATH=/usr/bin:/bin) and needs a ~/Prometheus canonical clone.
  - Skeptic: DOWNGRADE.
  - Shared file fabric/executors.py: assigned to this row (both REBUILD; no conflict).
- **Fabric claude executor (disposable build sessions)** [infra; Odysseus; cost S] (evaluator: HARDEN). Slot: institutional: build-session scheduler (R5 fork 'code authoring for build work items'). Serves: HUM-04, INF-06, HUM-03, INF-02.
  - Disposition: REBUILD. Skeptic finding: This is a READ-ONLY research executor, not a build executor. Write/Edit are allowed only under out/ (executors.py:111-112), the only Bash command is rogit (executors.py:33), and Python is refused on purpose: 'Bash(python3:*) is arbitrary code as the node account and would undo every Read deny above' (executors.py:40). DEF-ODY-007 records that no Claude worker can run code.
  - Correctness: Isolation gaps P7/D12 were found by attack and repaired (comments in executors.py:27-41). No independent test of the permission sandbox was run here.
  - Coupling: Same as the Fabric store/worker, plus the claude CLI and a node token file at ~/.config/prometheus/claude.env.
  - Skeptic: DOWNGRADE.
  - Shared file fabric/executors.py: assigned to Agent Fabric store + worker (job runner) [REBUILD] (both REBUILD; no conflict).
- **prometheus_llm model-call choke point** [infra; program-wide; cost S] (evaluator: HARDEN). Slot: R5 inference boundary choke point. Serves: INF-01, INF-02, INF-05, AGR-16, MEA-06.
  - Disposition: REBUILD. Skeptic finding: Several defaults work against the requirements. The default target is 'openrouter' with default_model 'stealth/ox-alpha' (client.py:312; registry.py:29-37), a model whose family is unknown by construction, while MEA-06 and REP-06 I3 need the runtime-reported family. With no default model, _resolve_model silently takes the FIRST id from /models (client.py:287-305), which registry.py:48-50 itself warns is wrong.
  - Correctness: Offline tests with monkeypatched adapters exist. None covers the audit. The audit is never enabled in committed launchers.
  - Coupling: Repo-root keys module; requests. Only about 5 importers versus about 70 files that call SDKs, HTTP or claude -p directly.
  - Skeptic: DOWNGRADE.
- **Signed verdict batch job** [infra; ; cost M] (greenfield). Slot: R0 signed verdict batch job. Serves: PRV-02, SCI-02, SCI-01, SCI-15, AGR-01.
  - Disposition: Load-bearing for the whole claim ladder, and nothing exists to salvage.
  - Correctness: Absence established by git grep (digest s5).
  - Coupling: Precursors: SFE evidence class and prospective rule, Vivarium outcome_rule, Metis grouping.
  - Skeptic: not challenged.
- **Dependency-driven demotion and row-class filter** [infra; ; cost M] (greenfield). Slot: R0 verdict job (row-class filter, dependency demotion). Serves: SCI-16, PRV-07, MEA-06.
  - Disposition: Required for mechanical demotion and for ignoring model-authored rows. Build it with the verdict job.
  - Correctness: Absence by inspection and grep.
  - Coupling: Depends on the new ledger.
  - Skeptic: not challenged.
- **Session token harvester and build ledger** [infra; ; cost S] (greenfield). Slot: R0 token accounting / build ledger. Serves: INF-02, INF-06, NRG-02, HUM-04.
  - Disposition: Build-session tokens are the dominant year-one cost, and none of them are currently accounted for.
  - Correctness: Absence by git grep (digest s5).
  - Coupling: Session logs, git trailers, Fabric artifacts.
  - Skeptic: not challenged.

### HISTORICAL_CONTROL (73)

- **Proteus foundry v0 VM + grammar** [org-a; Proteus; cost NA] (evaluator: RETIRE). Slot: none (frozen copy underlies C4 fixtures). Serves: REP-01, REP-07.
  - Disposition: It has no graph, no developmental instructions, no provenance shadow, no stable substructure ids, no lattice harness and only one encoding. Its intervention operator is class-wide knockout to NOP. Turning it into a DGM would rewrite more than 95% of the code and inherit a frozen runtime hash that 129 outside files import. It cannot be the slow reference, because its semantics differ from the DGM's. It cannot be the probe kernel, because it comes from the same model family and uses the same conventions. Keep a frozen copy only as the substrate under the C4 fixtures.
  - Correctness: Hand-written fixture tests pass. Replay is byte-identical. Cross-host receipts exist for Win py311/py312 and Linux py312 (proteus/v0_3, v0_4 CROSSHOST; not re-verified). There is no differential test against an independent reference interpreter.
  - Coupling: Stdlib only. 129 tracked files outside proteus/ import it (archaeon campaigns 1-6, wse, z80atlas, rie; genesis/harmonia_a; techne; roles/Nestor; vivarium; nyx; engine/necropolis). workspace.py shells out to git (the D-23 guard). Pure Python; works on Windows and Linux.
  - Skeptic: not challenged.
  - Correction: skeptic record removed: v1 carried the SplitMix64 row's skeptic record (no challenge was raised against this row); restored to the evaluator category, consistent with its own reason.
  - Correction: category RETIRE -> HISTORICAL_CONTROL: its own reason keeps a frozen copy as the substrate under the C4 fixtures (a kept HISTORICAL_CONTROL row imports proteus.foundry grammar/vm), so by rule 3 it is HISTORICAL_CONTROL rather than RETIRE.
  - Shared file proteus/foundry/{generate,grammar,lineage}.py: assigned to this row (frozen with the foundry under the C4 fixtures; the GA loop's design is rebuilt without them).
- **Proteus known-answer search fixtures (keyed-memory witness, graph witness, PROTEUS-46 harness)** [org-a; Proteus; cost S]. Slot: R4 search-policy / reachability known-answer fixture (R2 fixture store). Serves: PRS-02, PRS-03, ORG-15, ORG-14.
  - Disposition: This is a known-answer landscape for qualifying R4 search policies and the reachability estimator (PRS-02, PRS-03, ORG-15). The plant exists, and a greedy walk that rejects ties provably cannot reach it: walks are 3 steps (falsifier_46.py:31) and neutral children are never accepted (120-127). A 5-edit neutral path has been reported. The fixture is cheap, frozen and independent of the DGM. It is not a plant for organism rulers, because it comes from the same author family.
  - Correctness: Witness tests passed in the scratch run. The harness defect is verified in code and matches evidence/atl.md V7. The 5-edit neutral path (Artemis D002-03q) is unverified.
  - Coupling: Requires the frozen Proteus v0 and graph runtimes (C1, C2).
  - Skeptic: not challenged.
  - Shared file proteus/graph/witness.py: assigned to this row (a kept fixture depends on it, so it is HISTORICAL_CONTROL, not RETIRE).
- **Proteus mutation-kernel crucibles V0.3-V0.6** [org-a; Proteus; cost S]. Slot: R4 operator-kernel publication (method precedent only). Serves: AGR-15, PRS-03.
  - Disposition: This is the precedent for AGR-15 (each operator publishes its unselected variation kernel) and for PRS-03. The method transfers: execute the live operator rather than modelling it, attribute current to operators, and use a control that can actually fail. The code does not transfer, because it is bound to the v0.4 grammar and to structural coordinates only. Harmonia admitted it as a detector, not as an absence instrument.
  - Correctness: Each pass was preregistered. Harmonia's 2026-09-18 ruling: the reversible-reference control cannot fail by algebra, and the occupancy-TV floor was quoted rather than computed.
  - Coupling: Imports proteus.foundry.grammar (kernel.py:24, livekernel.py:20). Uses multiprocessing in v0_6.
  - Skeptic: not challenged.
  - Superseded row: Proteus mutation-kernel crucible V0.3-V0.6 [search; evaluator EXTRACT; v1 final HISTORICAL_CONTROL; skeptic DOWNGRADE].
  - Correction: merged: exact duplicate (org-a and search).
  - Shared file proteus/v0_5/multiplicity.py: assigned to this row (the buggy Holm code is an MEA-11 known-answer specimen).
- **Crius PARTS value landscape + exploit lineages** [org-a; Crius; cost M]. Slot: R4 reachability known-answer fixture; R2 plant-library design source. Serves: PRS-03, PRS-13, MEA-02, MEA-05.
  - Disposition: A known-answer fixture for R4 reachability and concentration-floor estimators: RSE s1 cites the 47-edit plant against (8+24)x300 as never found. It is also the design source for MEA-02/MEA-05 sealed cheat plants: a monotone id counter satisfies ACC > FRESH by the letter. These cheats must be re-expressed in DGM physics. The RELAY world it runs in is the closest existing design to anchor family F5; the world-forge group owns that verdict.
  - Correctness: The value landscape is by construction, per the seat's packets. The terminal disposition was scored mechanically from receipts. The 41-neutral-insert path reported by Artemis R-07 is unverified.
  - Coupling: Requires the frozen Crius VM and RELAY world.
  - Skeptic: not challenged.
- **D-5 register machine package (Agent D-5, consumed by Ergon)** [org-a; Agent D-5 / Ergon; cost S]. Slot: R4/R2 known-answer fixture; DEV-02 control template; CMP-01 precedent. Serves: ORG-15, PRS-03, DEV-02, CMP-01.
  - Disposition: It cannot seed the DGM: no world loop, no persistence, no I/O stream. It is still a valuable known-answer fixture: the R==E theorem plus 78 tasks with constructive witnesses and an exact oracle serve the ORG-15 tiers and PRS-03. Its G9 decomposition is the cleanest template for DEV-02 developmental controls: the shuffled-history arm keeps 100% of the +10.95 pp advantage and the random-library arm keeps 39%, so the effect is library content, not developmental correspondence. It is also the only fast/slow differential pair in this group, and its gaps show what CMP-01 must demand.
  - Correctness: Smoke and equivalence tests ran on a scratch copy and passed: 2402 programs x 128 inputs bit-identical on r0. A probe shows divergence with 3 inputs (reference 3, fast 0). This is latent, since every shipped family has arity <= 2.
  - Coupling: Self-contained via sys.path hacks. Needs numpy and numba. Imported by ergon/gen0, gen1, gen1a, gen1b scripts.
  - Skeptic: not challenged.
  - Superseded row: D-5 GA navigators and substrate (Ergon search core) [search; evaluator HISTORICAL_CONTROL; v1 final HISTORICAL_CONTROL; skeptic none].
  - Correction: merged: same package evaluated by org-a and search.
- **Aphrodite fold-DSL enumerator engine** [org-a; Aphrodite; cost S]. Slot: R2 plant-design reference (DEV-14 order-2); failure corpus. Serves: DEV-14, MEA-05, MEA-16, CMP-01.
  - Disposition: It is not an organism substrate. It is the canonical order-2 ('library as proposal prior', fixed improver) shape that DEV-14's planted battery must include, and it must be re-expressed as a DGM organism to serve as a plant. It is also a failure corpus for MEA-05/MEA-16: gate clauses that are constant True, a positive control identical to the treatment, and a tribunal whose admission span equals the abstraction under test. The conformance-gate history is a lesson for CMP-01 corpus design. None of it is machinery.
  - Correctness: 50 test functions in 6 files, not run (they test semantic identity, which is irrelevant to the substrate). Verified: run_s3s4.py:391 and 420 are literal True.
  - Coupling: Self-contained under roles/Aphrodite. Imports engine as a top-level module through sys.path. accel/ holds RunPod and Azure cloud scripts.
  - Skeptic: not challenged.
- **Ares batched graph substrate + worlds + GA** [org-b; Ares; cost S]. Slot: R2 (plant library / canary injector / anti-calibration set). Serves: MEA-16, MEA-17, SCI-07, ORG-19, CAU-05.
  - Disposition: It cannot be the primary substrate: no lifetime structural plasticity (ORG-04), no provenance shadow or stable ids (ORG-08), at most 8 hidden nodes. As a reference learner it is non-standard and buggy. Its record is valuable: the W4 zero-hidden latch is exactly MEA-16's 'latch for memory' cheap non-target, the three-channel closure is an enumerable known-answer for ORG-19, and the D1-D4/float32-tie defects are documented canary classes.
  - Correctness: 19/19 same-author tests pass (determinism, fixed-policy floors, hand-wired W2/W4 cheat controls, genome round trip). No independent plants.
  - Coupling: numpy only; imports nothing outside ares/; read by nyx/readings/ares_w4_reading.py and an Artemis dispatch script; receipt() shells git rev-parse; OS-neutral CPU.
  - Skeptic: not challenged.
- **Ananke PTE engine + GA + envs + plants** [org-b; Ananke; cost S]. Slot: R4 reachability-estimator fixture; R2 known-answer worlds. Serves: PRS-03, WLD-17, MEA-03, SCI-07.
  - Disposition: Not a DGM candidate (no lifetime structure change, sites are not individuals) and not eligible as probe or second substrate (I1). It is the canonical 'plant exists in the searched space, GA 96x36 never finds it' record cited in the frozen architecture (FLIP .978 / XOR .850). Packaged with its plants it is a deterministic known-answer fixture for the PRS-03 reachability estimator and X6. The flood latch and the mirror-forced zero_comm are WLD-17 and MEA-03 items.
  - Correctness: Physics is bit-exact versus the independent oracle on CPU (see oracle entry); test_c1b_switches 12 passed here.
  - Coupling: torch (CPU or CUDA), CUDA graphs; launch.py uses Windows schtasks and a detached git worktree; run state under ~/ananke_runs on M1 outside git; analysis uses sklearn/scipy; imported by archaeon/causal_lens adapters and Aether foreign conformance.
  - Skeptic: not challenged.
- **Ananke independent CPU oracle + conformance harness** [org-b; Ananke; cost S] (evaluator: EXTRACT). Slot: R3 DGM slow reference interpreter; R0 replay tests. Serves: REP-02, CMP-01, REP-01, MEA-05, ORG-08.
  - Disposition: HISTORICAL_CONTROL (keep with the PTE known-answer fixture and as an exemplar; the DGM slow reference is a new REP-02 build). Skeptic finding: (1) Independence is not even plausibly established. git log shows oracle.py and engine.py landed in the same commit, 7b6958b1c (2026-09-24). oracle.py has not changed since, while engine.py gained the C1b instruments (69975f42f). The 'did not read engine.py' claim exists only in docstrings (oracle.py:3-4; test_conformance.py:3-5).
  - Correctness: Run here on CPU: 110 passed, 13 skipped. The skipped tests are the CUDA graph-replay and checkpoint/resume tests, so snapshot/restore bit identity was not verified here.
  - Coupling: oracle: numpy only; harness imports torch engine; same model family as the engine.
  - Skeptic: DOWNGRADE.
- **Ananke mirror-twin interchange lens** [org-b; Ananke; cost S] (evaluator: EXTRACT). Slot: R2 interchange / carrier-agnostic intervention ruler. Serves: CAU-04, CAU-09, ORG-20, MEA-11.
  - Disposition: HISTORICAL_CONTROL (failure corpus and canaries for qualifying the R2 interchange ruler). Skeptic finding: (1) Interchange works only on whole named arrays across all sites (prometheus/ananke/lens.py:31-45); the only finer option is the Msum payload sub-index (41). The DGM's CAU-04/CAU-09 interchange must act per node, edge, register or subgraph (RSE s3 hooks). (2) Twins are mirror pairs with shared seeds and negated binary cues (lens.py:7-10, 89; lens_swap.py:12-25).
  - Correctness: Partial: lens_swap/lens_instruments did not finish within 300 s (26 passed before the cap). Dossier records the instrument repaired five times and validated only on same-author plants.
  - Coupling: imports engine, assays, envs; torch; scipy in inference.py.
  - Skeptic: DOWNGRADE.
  - Superseded row: Ananke mirror-pair carrier-swap lens (lens.py, lens_swap.py) [meas-b; evaluator REBUILD; v1 final REBUILD; skeptic none].
  - Correction: merged: lens.py and lens_swap.py evaluated by org-b (reviewed: HISTORICAL_CONTROL) and meas-b (unreviewed: REBUILD); reviewed wins. The R2 interchange ruler is a new build; this lens is its failure corpus and canary source.
- **Aether verification kit** [org-b; Aether; cost S] (evaluator: EXTRACT). Slot: R0 receipts; R3 kernel conformance and ORG-20 regression gate. Serves: ORG-20, REP-02, MEA-05, PRV-01, CMP-04.
  - Disposition: HISTORICAL_CONTROL (bug-class catalogue and receipt exemplar). Skeptic finding: (1) The mutation-testing claim is false. mutants.py targets aeth00.v1 (Aether/test/reference/mutants.py:1-7, importing reference.oracle), not the aeth01 kernel/oracle differential; no mutant of gpu_aeth01 or oracle_aeth01 exists. test_mutants.py never substitutes a mutant into the suite and checks that the suite fails.
  - Correctness: test_aeth03_variants 39 passed here; mutants and golden tests not run here (reported 984 passed at 251bc987e, unverified).
  - Coupling: numpy; sys.path hacks; independent of other seats.
  - Skeptic: DOWNGRADE.
  - Shared file Aether/observatory/aeth03_propagation.py: assigned to this row (kept frozen as a fixture under the verification kit; the one-bit twin design is rebuilt on DGM hooks).
- **Nestor Z8 / NPE byte VM and worlds** [org-b; Nestor; cost S]. Slot: R2 canary / painter-plant corpus. Serves: MEA-16, MEA-17, SCI-07, PRV-10, ORG-19.
  - Disposition: Same-family ISA with zero-init and absolute-addressing conventions, so it is ineligible as probe or second substrate and not the DGM. Its record holds the richest false-positive classes: copies made by the variation operator (Z80A-D05), pair-tape identity read as heredity, competence certified from zeros. These are exactly the MEA-16 painter and MEA-17 canary needs. The register-reset axis is a reusable control idea for ORG-19.
  - Correctness: selftest_z8 positive controls exist (not run). The z8taint equivalence I ran exercises z8.run (0 mismatches over 400 programs).
  - Coupling: top-level module imports via sys.path (import z8, world); experiments subclass Runner from campaign dirs; multiprocessing pools; schtasks; host lease files.
  - Skeptic: not challenged.
- **Bellerophon BEE Z80 soup (prometheus/z80atlas)** [org-b; Bellerophon; cost S]. Slot: R2 canary / anti-calibration corpus. Serves: MEA-17, SCI-07, PRS-12, AGR-15.
  - Disposition: Replication is an engineered basin (LDIR with C=0 sweeps 256 bytes plus an ~80% NOP slide), the tasks are one-byte transforms, and it is ineligible for substrate roles. Its value is the discipline record: YOKED equal-total contingency as a standard pressure control (atl.md:380), v1-golden plus gated physics versions, and the LDIR-off ablation (8/300 -> 0/300) as an affordance-created-the-result fixture.
  - Correctness: Run here: test_verify_exact, test_reg_world and test_forensic_regressions, 37 passed, including the v1 golden byte replay (test_forensic_regressions.py:25-44).
  - Coupling: pure Python package; consumed by archaeon/causal_lens and Artemis scripts; raw results host-local on M2; multiprocessing; superlinear cost with horizon.
  - Skeptic: not challenged.
- **Archaeon z80atlas + copier census + denovo** [org-b; Archaeon; cost S]. Slot: R2 canary corpus; R4 reachability prior fixture. Serves: PRS-03, PRV-10, MEA-17, SCI-07.
  - Disposition: The census is a measured random-sampling hit rate at plant length, precisely PRS-03(d), and a worked two-sided classifier. The 26/26 'spontaneous replication' headline flags that were all transplanted lineages are the canonical PRV-10 case. No substrate role.
  - Correctness: Census and denovo were preregistered (prereg commits before runs). test_lineage_attribution run here (11 passed, 1 skipped). test_z80atlas_provenance not run (hardcoded D:\ path).
  - Coupling: pure Python; imported by archaeon envgate, lineage, rie, causal_lens; host-path assumption in a test.
  - Skeptic: not challenged.
- **Z80 material-taint shadow interpreters** [org-b; Nestor / Archaeon; cost S] (evaluator: EXTRACT). Slot: R3 instrument hooks (provenance shadow); R2 write-order tracer. Serves: ORG-08, PRV-10, DEV-14, DEV-12, CAU-02.
  - Disposition: HISTORICAL_CONTROL (heredity fixtures, attribution regressions and the ruler-tournament record as PRV-10/MEA-17 known-answer and canary material). Skeptic finding: (1) 'Equal or refuse' holds only for Archaeon (archaeon/lineage/core.py:181-190, slow path only). Nestor's production path REPLACES z8.run with run_tainted whenever track_material is on (roles/Nestor/campaigns/z80atlas-verify-2026-09-22/world.py:805-810), with no runtime comparison, so any divergence silently changes the physics. (2) Nestor's equivalence check is not a test.
  - Correctness: Run here: z8taint vs z8 0 mismatches over 400 random programs; archaeon test_lineage_attribution 11 passed, 1 skipped (includes a taint-vs-VM differential). Dossier: material ruler won a 9-fixture tournament 9/9 vs id-based 4/9.
  - Coupling: each is bound to its own VM; same-family code.
  - Skeptic: DOWNGRADE.
  - Superseded row: NPE z8taint (H3 material ruler R3) [meas-b; evaluator HISTORICAL_CONTROL; v1 final HISTORICAL_CONTROL; skeptic none].
  - Superseded row: Archaeon taint VM and lineage core [meas-b; evaluator REBUILD; v1 final REBUILD; skeptic none].
  - Correction: merged: the same taint code evaluated by org-b (reviewed: HISTORICAL_CONTROL) and meas-b (unreviewed: REBUILD, HISTORICAL_CONTROL); reviewed wins. The DGM provenance shadow (ORG-08) is a new build informed by its design.
- **Tyche lens DAG ecology** [org-b; Tyche; cost S]. Slot: R2 fixture (grammar-gravity and needle planted cases). Serves: AGR-15, PRS-03, SCI-07.
  - Disposition: The chemistry contains the generators' own primitives, so 'success' measures reachability of the author's construction. That makes it a ready planted GRAMMAR-BORNE case for AGR-15 and a PRS-03 needle case (parity-3 at 5 instructions never reached). There is no organism role: the classifiers are fixed and capability is supplied by the chemistry (ORG-17).
  - Correctness: test_v0 14 passed here: lens causality, LEAD cheat caught, planted attainable and twin dead, lexicase specialists.
  - Coupling: numpy, scipy lfilter, sklearn; reads hecate/alien systems; imported by theseus.synth.
  - Skeptic: not challenged.
  - Shared file tyche/worlds.py, tyche/v2/: assigned to Tyche audits and world certificates [HISTORICAL_CONTROL] (both HISTORICAL_CONTROL; no conflict).
- **Tyche audits and world certificates** [org-b; Tyche; cost S] (evaluator: EXTRACT). Slot: R1 world forge (leak audit, known-answer world set). Serves: WLD-07, WLD-17, MEA-03, MEA-05, WLD-01.
  - Disposition: HISTORICAL_CONTROL (LEAD-cheat record, tsd/prf constructions as design notes and SCI-07 items). Skeptic finding: (1) causality_audit uses hard-coded CUTS = (500, 2000, 5000, 8000, 11000) (tyche/audits.py:24-38). For any stream with T <= 501 every replaced slice is empty and the audit passes vacuously, so it cannot fail outside Tyche's T = 12100. (2) It checks an observer reading a precomputed open-loop stream for future access.
  - Correctness: test_v0 covers test_random_lenses_are_causal and test_lead_cheat_is_caught (passed here).
  - Coupling: imports tyche.lens, worlds, ecology; numpy.
  - Skeptic: DOWNGRADE.
  - Superseded row: Tyche v2 certify.py + worlds_v2 needle classes [world; evaluator EXTRACT; v1 final HISTORICAL_CONTROL; skeptic DOWNGRADE].
  - Correction: merged: certify.py evaluated by org-b and world.
  - Shared file tyche/worlds.py, tyche/v2/: assigned to this row (both HISTORICAL_CONTROL; no conflict).
- **Ensorain WTP-01..03 foundry** [org-b; Ensorain; cost S]. Slot: R2 canary / anti-calibration corpus. Serves: MEA-03, MEA-17, SCI-07.
  - Disposition: Three clean, documented ruler false positives, each killed by a MEA-03 rung: a variance-collapse artefact, a one-float running mean killed by the constant predictor, and 9 promoted specimens beaten by a post-data tuned batch fit. The committed specimen rows are ready MEA-17 canary and SCI-07 calibration material.
  - Correctness: Tests exist (wtp, wtp2, wtp3); not run here; the false positives were caught post-data by the seat's own null tests.
  - Coupling: numpy only.
  - Skeptic: not challenged.
  - Superseded row: Ensorain WTP world-genome foundry [world; evaluator HISTORICAL_CONTROL; v1 final HISTORICAL_CONTROL; skeptic none].
  - Correction: skeptic record removed: v1 carried the WTP-03 collider row's skeptic record; category unchanged.
  - Correction: merged: same foundry evaluated by org-b and world.
- **Ensorain arc3/suff sufficiency ladder** [org-b; Ensorain; cost M] (evaluator: EXTRACT). Slot: R1 F3 generator and exact solver; R2 MEA-07 generic FSC/PSR baselines. Serves: WLD-04, WLD-01, MEA-07, MEA-11, TRF-02, WLD-17.
  - Disposition: HISTORICAL_CONTROL for worlds.py + test_worlds.py (a sealed known-answer cross-check for the F3 exact solver: if F3 authors do not read it, it can act as WLD-04's slow solver from a different author), S; REBUILD for the MEA-07 learners (CSSR/HMM_EM/CSSR_EM), M. Skeptic finding: (1) CSSR, HMM_EM and CSSR_EM have zero tests. tests/ holds only test_worlds.py, and its one learner test covers STAT. (2) CSSR fails on the F3 anchor itself. Split mode leaves excess .0341 on the Even process, no better than the k=6 window floor (ensorain/arc3/suff/CSSR_T25.md:15, 40).
  - Correctness: test_worlds 7 passed here: Even and golden-mean Bayes log-loss converge to the analytic 2/3 bit; the Even process has no finite window; STAT(k) equals Bayes at the true order to 1e-9.
  - Coupling: numpy only, self-contained.
  - Skeptic: DOWNGRADE.
  - Superseded row: Ensorain ARC3 answer-keyed processes with exact Bayes (suff) [world; evaluator HARDEN; v1 final HARDEN; skeptic UPHELD].
  - Correction: merged: worlds.py evaluated by org-b (reviewed: HISTORICAL_CONTROL as a sealed known-answer cross-check) and world (reviewed: HARDEN as the F3 core); less reuse wins. Using it as the F3 core would destroy its value as an independent check of the F3 solver (WLD-04, WLD-17); F3's exact Bayes is small to rebuild. The MEA-07 learners in the same package are REBUILD.
- **herakles.evca (+ herakles.eca) CA libraries** [org-b; Herakles; cost S]. Slot: R2 known-answer fixtures; R4 external known-answer (only if an EvCA GA reproduction is preregistered). Serves: WLD-21, SCI-07, PRS-03, MEA-11.
  - Disposition: A verified reconstruction of externally published evolved-CA rules (WLD-21), usable as is as a known-answer fixture: a true-but-surprising literature result for SCI-07 and an external reachability datum for PRS-03. It is not production organism machinery: one task family, no search inside.
  - Correctness: test_evca 60 passed here, including an independent-oracle step check, golden results, side-effect-free import, input non-mutation and instrument controls.
  - Coupling: numpy; pure; widely imported (archaeon campaigns 1-3, proteus mint, evidence_wiki service, engine/necropolis, nyx readings).
  - Skeptic: not challenged.
- **Ludus depth profile gap(k) + GATE-W1 + greedy baseline** [world; Ludus; cost NA]. Slot: R1 certificate tool (as a negative example only). Serves: WLD-01, WLD-19, WLD-17.
  - Disposition: The need (depth/deliberation certificate) remains, but this cannot be the base. No bound type, no policy language, 2-player perfect-info only, cheap-player class excludes closed forms, and readings on uninformative-eval worlds are tie-break artefacts. Value = documented failure plus fixtures; R1 d_think must be written new with set-valued ties.
  - Correctness: Seat controls rows (CONTROLS_2026-09-16.json) 8/8 as expected, Nim cheat admitted. My in-memory probe: Nim345 gap(4)=.240 with the shipped tie-break, .190 with a random tie-break (below gate), .000 if any tied action counts; 48% of states tied at k=4 (87% at k=1). Orchard/Ledger/TITHE unaffected.
  - Coupling: stdlib; no imports from outside ludus; host-specific worktree path recorded in controls JSON
  - Skeptic: not challenged.
- **Ludus qualification fixtures (Ledger, Orchard, Nim345+Bouton, bench corruptions, MartianDiceOneRay, Kuhn leak variants)** [world; Ludus; cost S]. Slot: R1 sealed known-answer set (regenerate under seal); R1 leak-audit plant battery. Serves: WLD-17, WLD-07, MEA-05.
  - Disposition: Ready-made known-answer decoys for WLD-17 (closed-form-solvable, latch, leaky classes) and the F7 'Nim-like decoy with closed-form optimal rule'; seeds of the WLD-07 planted-leak battery. Public and same-family authored, so regression fixtures only, not the sealed scoring set.
  - Correctness: Each fixture has a pre-stated expected reading; controls JSON shows instruments behaved as predicted on all 25 rows
  - Coupling: cycle-001 world interface and arena sibling-import hack (fixtures.py:295-302)
  - Skeptic: not challenged.
  - Shared file ludus/controls/fixtures.py: assigned to this row (the Kuhn leak worlds are kept fixtures; the leak audit itself is rebuilt).
- **Ludus bench: stochastic stopping worlds, exact DP, compile, bench verify, rules audit** [world; Ludus; cost NA]. Slot: none as machinery; WLD-21 pattern for R1 reconstruction checks. Serves: WLD-21, SCI-07.
  - Disposition: Solitaire stopping worlds with two decision axes serve no R1 family. Failure corpus: reconstruction from memory overturned the Martian Dice reading; r0003 tie rule manufactured zeros; support mismatch demoted cycle 004. The rules_audit pattern is the only in-repo WLD-21 instance and is worth copying.
  - Correctness: Seat controls: catches pot+1, cycle, large probability halving; misses a below-tolerance halving and the draw law (one-ray Martian Dice verifies)
  - Coupling: stdlib; writes atlas/ledger JSON into the repo
  - Skeptic: not challenged.
- **Toolbox admission (component conformance predicate)** [world; Bellerophon; cost S] (evaluator: EXTRACT). Slot: R0 component conformance; R1 solver cross-check harness. Serves: WLD-04, MEA-01.
  - Disposition: HISTORICAL_CONTROL. Skeptic finding: The probe-power rule the evaluator wants to lift has no planted test. No test references probe_has_power or an action-blind probe. The only reference test (test_admission.py:80-92) is a one-constant-off twin caught by the agreement branch, not the power branch. 'Power' only means one deterministic policy's trace differs from all-zero actions on some variant or seed (admission.py:148-151).
  - Correctness: test_admission and test_admission_power pass (part of the 259)
  - Coupling: toolbox contracts and registry
  - Skeptic: DOWNGRADE.
- **Ensorain exact marginal-preserving surrogate** [world; Ensorain; cost S] (evaluator: EXTRACT). Slot: R1 admission ladder rung; R2 control generator. Serves: WLD-02, MEA-03, MEA-05.
  - Disposition: HISTORICAL_CONTROL. Skeptic finding: The algebra is right for what it claims (collider.py:27-48): the mean, per-mode marginal MEANS and total variance are preserved exactly. But that is not marginal preservation. In a scratch probe on a 6x7x5 field, heteroscedastic along mode 0, per-slice variances 0.006..7.9 became 2.0..4.3. On a binary field the surrogate leaves the support: 210 distinct values over -0.43..1.40.
  - Correctness: Ran test_surrogate_exact: pass (mean 1e-12, variance 1e-9, marginals allclose); algebra verified
  - Coupling: numpy only
  - Skeptic: DOWNGRADE.
- **Cosmos world-graph engine (latch families, miner, SELECTIVE_PAYS certificate)** [world; Cosmos; cost NA]. Slot: none as machinery; R1/R5 false-positive corpus. Serves: SCI-07, WLD-13.
  - Disposition: Latch-demand worlds cannot host reasoning claims (WLD-13). The mined laws restated the planted certificate (zero-parameter rule; C3 104/120), and sealed transfer stayed within one author lineage. Canonical SCI-07 false positives. The C3 P1/P2 certificate is an organism ruler and belongs to the measurement group.
  - Correctness: evidence/verification.jsonl confirms law-restates-certificate
  - Coupling: numpy; sqlite store; broker
  - Skeptic: not challenged.
- **alien_circuitry exact monoid oracle + v2 orbit table** [world; none (operator sessions); cost S]. Slot: R1 sealed known-answer set; WLD-03 quotient-checker regression fixture. Serves: WLD-17, WLD-03, WLD-19.
  - Disposition: A known-answer fixture for WLD-17's 'lookup-solvable on held-out after canonicalisation' class. A real instance of a split that is not quotient-disjoint: the regression fixture WLD-03's test needs. Also an exact reference solver for deterministic navigation (F7). Not a production family.
  - Correctness: Ran 20/20: forward BFS equals the table on 300 samples; BFS, bidirectional BFS and the oracle agree; vectorised equals scalar semantics. Held-out-in-distribution claim from dossier, not re-verified.
  - Coupling: numpy/scipy core; ac01d families need torch/CUDA (GPU non-reproducibility recorded): do not carry
  - Skeptic: not challenged.
- **Hecate LLM-authored control-first probe worlds** [world; Hecate; cost NA]. Slot: R1/R5 anti-calibration corpus. Serves: SCI-07, SCI-05.
  - Disposition: Failure corpus: 5/5 SIGNALs reduced to trivial or known explanations; signals cluster in the cheapest worlds (5/9 vs 0/16, p .012); null-twin drift in ~11 worlds; one positive control unattainable. Generator-authored worlds fail WLD-05.
  - Correctness: dossier s21 (record), not re-run
  - Coupling: claude -p generation
  - Skeptic: not challenged.
- **Hecate alien-lawful system generator** [world; Hecate; cost NA]. Slot: R1 known-answer set pattern. Serves: WLD-17, MEA-02.
  - Disposition: The matched seductive-null construction is the right pattern for WLD-17's leaky/seductive class and MEA-02 procedural plants. But the systems are passive finite maps, and the answer key is public (Tyche already reads it), so regenerate under seal if used.
  - Correctness: test_alien_generation passes (part of 64)
  - Coupling: numpy; answer key read by tyche/worlds.py
  - Skeptic: not challenged.
- **Archaeon C4 mutational censuses (DFE census, radius census, neutral walk)** [search; Archaeon; cost S] (evaluator: EXTRACT). Slot: R2/R4 boundary (instrument consumed by R4). Serves: ORG-11, PRS-03, AGR-15.
  - Disposition: HISTORICAL_CONTROL (C4 tables as a corpus of Proteus damage geometry; the protocol moves on only as a design note for an R2/R4 REBUILD that is qualified on planted geometries). Skeptic finding: No code can be extracted. The evaluator's own reason concedes this ("code is Proteus-bound", re-implement on DGM), so by the category definitions this is design, not EXTRACT. c4_01.py:30-42 inserts the SFE client into sys.path and imports proteus.foundry grammar/vm/affordances, archaeon.wse.evolve/worlds and campaign4.c4base; main() also needs the workspace guard, the launch-gate receipt and the c4harness.
  - Correctness: In-module --self-test on synthetic draws. Not run here (the modules read campaign population files and refuse while the launch gate is RED).
  - Coupling: Proteus grammar/vm, wse.evaluate, campaign4 STARTING_POPULATION; sys.path hack to SerendipityFoundryClient.
  - Skeptic: DOWNGRADE.
- **Archaeon campaign 2/3/5 harness machine** [search; Archaeon; cost NA]. Slot: none (code); R2 known-answer corpus (results). Serves: DEV-11, TRF-06.
  - Disposition: Provenance belongs to R0, and the DGM's two encodings cover ORG-21, so the code retires. The results are control material: C3 ladder vs matched-budget direct search (the only curriculum-vs-direct control in the record; the winner turned out to be a first-input latch, ATL-11), and the opcode-permuted incompetent-import control (ATL-05).
  - Correctness: test_campaign2_machine.py (not run: its engine-descriptor test needs a host cacert file); test_campaign3_machine.py run and passed.
  - Coupling: Hard SerendipityFoundryClient dependency via sys.path insertion; gitignored config.local.json; writes under archaeon/campaignN/.
  - Skeptic: not challenged.
- **Campaign 6 segment loop + pressure schedules + Deep Frontier scheduler/loop/allocation** [search; Archaeon; cost NA]. Slot: none (anti-pattern); REP-01 pattern for R4 checkpointing. Serves: REP-01, AGR-13.
  - Disposition: The canonical anti-pattern the architecture rejects: 3.72M evaluations steered by detectors with 25% and 0% planted catch, run without its own verification gate. Only the segment purity and continuity self-test survives, as a requirement on the new engine's checkpoint/resume (REP-01), not as code.
  - Correctness: Segment self-test exists (not run). test_frontier_suppression_logging.py exists but was not run: step() can write tracked files via charge_pursuit and run_due_readouts.
  - Coupling: campaign4 c4_01, Proteus graph handover, SFE schemas, frozen detector JSON, many repo-relative writes under archaeon/frontier/.
  - Skeptic: not challenged.
- **PROTEUS-46 falsifier greedy walk** [search; Proteus; cost NA]. Slot: R4 test fixture / linter negative. Serves: PRS-02, PRS-03, SCI-09.
  - Disposition: The clearest single-file specimen of greedy tie rejection manufacturing a cliff. Use it as a planted negative for the prereg linter and PRS-02 policy declaration, and for the PRS-03 estimator test: a strict, tie-rejecting, horizon-3 walk must be flagged as unable to type a null.
  - Correctness: Verified in source this session (lines 113-131).
  - Coupling: Proteus graph and v0 grammars.
  - Skeptic: not challenged.
- **Apollo O1 enumerator** [search; Apollo; cost NA]. Slot: R4 test/known-answer reference. Serves: PRS-02, PRS-03, CMP-01.
  - Disposition: A clean known-answer comparison of evolution against enumeration, and the model rule for the new random-sampling/needle estimator: if the enumerator cannot represent the known plant, it reports nothing (PRS-03d, PRS-02). The code is substrate-bound.
  - Correctness: Positive-control-first design; result files in cycles/; no unit tests.
  - Coupling: apollo/src blackboard_evolve, hephaestus src.
  - Skeptic: not challenged.
- **Tyche v2 pressure-map driver (declared policy matrix + selection log)** [search; Tyche; cost M] (evaluator: EXTRACT). Slot: R4. Serves: PRS-02, PRS-05, PRS-09, ORG-11.
  - Disposition: HISTORICAL_CONTROL (Block R runs plus these defects as anti-pattern fixtures for the policy linter); the code is RETIRED. Skeptic finding: There is no primitive to extract. The 'policy matrix' is argparse flags plus if-branches inside RunV2.run (run_v2.py:353-405), and the evaluator admits 'code is lens-bound' and 'cost inside the engine', which is design reference by definition. The design also contradicts the requirements it is said to serve.
  - Correctness: test_v2 compose-exactness and strict-eligibility tests run and passed. Block R results reclassified as search/pressure insufficiency (tan-b TY-9).
  - Coupling: numpy, sklearn organisms, multiprocessing Pool, git subprocess for receipts.
  - Skeptic: DOWNGRADE.
- **Tyche natural-history tracer** [search; Tyche; cost S] (evaluator: EXTRACT). Slot: R4 analysis over R0 logs. Serves: PRS-03, ORG-11.
  - Disposition: HISTORICAL_CONTROL (its HISTORIES outputs, with a caveat); no code or concept to extract beyond the text of PRS-03(c). Skeptic finding: It cannot serve PRS-03(c). PRS-03 applies to NEGATIVE search results, but history_v2 runs only on SOLVED slots (history_v2.py:94-96 `if not solved: continue`), and a null has no realized ancestry to trace. PRS-03(c)'s 'best known path' runs from the initial distribution to a planted solution; this traces a survivor's realized ancestry, picked greedily by parent home value (history_v2.py:141-149).
  - Correctness: No tests; observational only, with no ablation (tan-b TY-11/12).
  - Coupling: Needs the full Tyche run logs and the planted answer key.
  - Skeptic: DOWNGRADE.
- **Theseus QD archive** [search; Theseus; cost S] (evaluator: EXTRACT). Slot: R4. Serves: PRS-05, AGR-10, MEA-18.
  - Disposition: HISTORICAL_CONTROL (descriptor-failure corpus for MEA-18: random matched programs reach the same regions, weird programs pass viability); the QD archive is REBUILT around DGM signatures, with primordial/qd/archive.py as a better reference. Skeptic finding: The archive is not generic. Cal and Archive are bound to the battery layout: bt.N_DESC and bt.DESC_NAMES (rulers.py:73-78) and bt.FP_DIM (rulers.py:153). 'Quality = reproducibility, never novelty' is contradicted in use: run_v0.py:311 adds 1 + 2 to vitality when n_rulers_novel >= 2, and fossilize removes the lowest-vitality entities (synth/ecology.py:122-126).
  - Correctness: test_synth_v0.py: 10 passed with the repo as cwd. From a temp directory 7 fail, because compile_g0 shells out to git show. The Archive class has no direct test.
  - Coupling: numpy; battery fingerprint dimension constants; cwd-dependent git subprocess in G0 compilation.
  - Skeptic: DOWNGRADE.
- **Ergon library seeding and retention-policy lineages** [search; Ergon; cost NA]. Slot: R2 known-answer template. Serves: MEA-05, SCI-14.
  - Disposition: The engine is a toy and the instrumentation is fragile. The design is a template: decompose content vs order vs random library, and test channel sensitivity with a planted witness at a stated MDE (+3.38 pp detected at n=100; MDE80 1.22 pp).
  - Correctness: Cheat control detected at n=100 (p=0.00002); P3 null CI [-0.24,+1.33] pp; lineage seed spaces disjoint by construction. No unit tests; not run.
  - Coupling: D-5 substrate via sys.path; monkeypatched module globals; multiprocessing.
  - Skeptic: not challenged.
  - Shared file ergon/gen3/cheat_control.py, ergon/gen3/mde_p3.py: assigned to Ergon bounded-null machinery (decide, MDE, gate-fire worlds, planted-witness cheat) [REBUILD] (the skeptic-reviewed row keeps these files).
- **SFE Gen-2 canary** [search; Daedalus; cost NA]. Slot: R0/R4 validator fixture. Serves: REP-07, SCI-05.
  - Disposition: A tiny, real failure fixture: the REP-07 planted defect ('two arms sharing a stream undeclared: launch refused') and a planted geometric null for SCI-05 attainability checks.
  - Correctness: Verified in source; initial distances re-derived by sis-a as 9/13/16/14; test_sfe_canary.py exists (not run).
  - Coupling: SFE Foundry runtime (sqlite) and WorkerLoop.
  - Skeptic: not challenged.
- **SFE off-repo search note (WOW archaeology of D-13) + selection-boundary toys** [search; Daedalus; cost NA]. Slot: R4 telemetry spec; R2 statistics library. Serves: SCI-15, MEA-11, PRS-02.
  - Disposition: The most important fact for an R4 designer (the GA may be a random walk), at no cost. It mandates telemetry of n_tied/n_candidates per selection event, and the toys belong in the R2 known-answer statistics library. The D-13 driver code itself is off-repo and was not inspectable (UNKNOWN).
  - Correctness: Audit counts are read from ledger records (REPORTED); the toys print rejection rates against targets (not run).
  - Coupling: Off-repo corpus; toys are standalone.
  - Skeptic: not challenged.
- **Charon c1c2_checks (pool fingerprint C1, transport-failure-is-not-residue C2, ordering)** [meas-a; Charon; cost S] (evaluator: EXTRACT). Slot: R0 (structural in ledger/receipts) + R2 template for every check. Serves: MEA-09, PRV-01, PRV-04, MEA-05, MEA-01.
  - Disposition: HISTORICAL_CONTROL. Skeptic finding: Things I reproduced in scratch by running the module: (1) C2 FAILS OPEN when the loader's seq is 0-based. A naive loader that renders the transport-failed row returns PASS, because c1c2_checks.py:274-277 matches (uid,seq) but never checks that an admitted seq points at a raw row with that uid. (2) The 'exclude everything is a cheat' control (test 147-151) only catches an empty loader.
  - Correctness: 17 tests with positive, negative and cheat controls per check, all passing. A live gate-fire on real ledgers was reported in the evidence (tit-b s3.1).
  - Coupling: Stdlib only, with the loader injected. The gate-fire script imports ergon.probe.assemble and archaeon.workspace and writes into charon/probe/. OS-neutral.
  - Skeptic: DOWNGRADE.
- **Nemesis cheatlib (responders, forgeries, chance_floor, shrink)** [meas-a; Nemesis; cost S] (evaluator: EXTRACT). Slot: R2 baseline ladder + cheapest-cheat battery. Serves: MEA-03, MEA-04, MEA-05, MEA-01, CAU-10.
  - Disposition: HISTORICAL_CONTROL. Skeptic finding: chance_floor (cheatlib.py:148-174) has fail-open defaults (reproduced). It silently accepts candidate_counts shorter than the population: 1 count for 4 items gives 0.125 where the true value is 0.5. Missing or zero counts give uniform_rate 0.0, the most permissive floor possible, where it should refuse. That breaks MEA-03's 'same population and denominator'. majority_rate is Counter.most_common/n.
  - Correctness: The firing fixture is pinned to the committed April ledger (62/92 = 0.674; 292/294 tools at or below it, though the defensible figure is 120/122 because missing evaluations are scored as wrong). One test fails here.
  - Coupling: Stdlib only. The tests shell out to git show/grep on the repository (read-only).
  - Skeptic: DOWNGRADE.
- **Harmonia AP-1.1.0 audit primitives** [meas-a; Harmonia; cost S] (evaluator: EXTRACT). Slot: R2 dossier checks + prereg linter (SCI-05). Serves: SCI-05, MEA-01, MEA-03, MEA-04, SCI-04.
  - Disposition: HISTORICAL_CONTROL. Skeptic finding: The four functions are 2-12 lines each. reachability (audit_primitives.py:46-60) collects set(verdict_fn(x)), and ceiling (87-94) is one subtraction. reachability runs a hand-transcribed lambda of the prose rule (_tyche_h1 121-131), not the actual pipeline that SCI-05 requires.
  - Correctness: 9 tests pass, and freeze_precedes flags the real Ananke W-O plan. The suite's ablation leg proves nothing (see defects).
  - Coupling: Stdlib plus read-only git subprocess calls.
  - Skeptic: DOWNGRADE.
- **Harmonia QR-1.2.1 qualification_rules.py (H0-H5 lane rules)** [meas-a; Harmonia; cost S] (evaluator: EXTRACT). Slot: R2 statistics library (ideas) + R0 verdict-job plan validation. Serves: SCI-06, SCI-15, MEA-11, SCI-04, PRV-01.
  - Disposition: HISTORICAL_CONTROL. Skeptic finding: I confirmed against scipy that t_crit (qualification_rules.py:242-247) rounds df up to the next table key. That makes it anti-conservative: df 11 gives 2.179 against the exact 2.201, and df 121 gives 1.96 against 1.98. paired_contrast (282) sends any alpha other than .05 to the .025 column.
  - Correctness: 33 tests pass, but none is a known-answer test of the quantiles. The AF F6 calibration reads 0.015+/-0.0019 against an expected 0.0125 at df 11.
  - Coupling: Stdlib only. The lane gates are tied to the retired H0-H5 engines.
  - Skeptic: DOWNGRADE.
- **Harmonia AF-1.1.0 adversarial fixtures + FP-1.0.0 floor precheck + exchangeability** [meas-a; Harmonia; cost S] (evaluator: EXTRACT). Slot: R2 known-answer test pattern + prereg degeneracy lint. Serves: MEA-05, MEA-11, SCI-05.
  - Disposition: HISTORICAL_CONTROL. Skeptic finding: F6 (adversarial_fixtures.py:214-257) has no pass/fail criterion. It returns rates and an 'expected' field, asserts nothing, and is not in run_battery_1_1_0. At 4,000 trials it also cannot catch the defect in the library it calibrates. The df-11 table quantile has a true one-sided size of 0.01326 against 0.0125 (scipy), and detecting that needs about 132,000 trials.
  - Correctness: The battery runs 12/12 here. F6 (214-257) is a true known-answer calibration of the false-support rate, and it self-labels the practical-threshold zero as vacuous. Most of the other fixtures have tells hard-coded by their author (F1: oracle_calls==0).
  - Coupling: Imports qualification_rules (inheriting its quantile defect). floor_precheck main reads an archaeon readout.
  - Skeptic: DOWNGRADE.
- **Harmonia STANDING_RULES.md** [meas-a; Harmonia; cost NA]. Slot: rationale corpus behind frozen requirements. Serves: MEA-01, MEA-03, MEA-05, SCI-04, SCI-05, SCI-06.
  - Disposition: Its content is subsumed by MEA-01/03/05 and SCI-04/05/06/14. Keep it as the rationale record for when a requirement is challenged; it is not machinery.
  - Correctness: Documentation; nothing executable.
  - Coupling: none
  - Skeptic: not challenged.
  - Correction: skeptic record removed: v1 carried the QR-1.2.1 row's skeptic record; category unchanged.
- **Harmonia VACUOUS_READINGS.md** [meas-a; Harmonia; cost NA]. Slot: R2 null-certificate checker negative fixtures. Serves: SCI-03, SCI-08, SCI-05.
  - Disposition: The 'vacuous is not a null' distinction must exist in SCI-03 null typing. Each row is a ready-made negative fixture that the null-certificate checker must refuse to type as a phenomenon null.
  - Correctness: Documentation; the rows cite rulings, and V-005 has a computed addendum.
  - Coupling: none
  - Skeptic: not challenged.
- **Harmonia null family (NULL_PLAIN, NULL_BSWCD, NULL_BOOT, null_family runner)** [meas-a; Harmonia; cost NA]. Slot: R2 defective-null fixture for checker qualification. Serves: MEA-05, SCI-07.
  - Disposition: It has no production role. NULL_BOOT is a valuable planted 'null that cannot fire', which MEA-05 mutation tests and the null-certificate checker must reject.
  - Correctness: Verified here that NULL_BOOT cannot fire: n 500, value ~ N(5,1) gives z 0.01, COLLAPSES.
  - Coupling: pandas. null_family.py hard-codes a Redis host and password default in tracked source (lines 32-33).
  - Skeptic: not challenged.
- **Techne modal-collapse synthetic null** [meas-a; Techne; cost NA]. Slot: R1/R2 known-answer fixture (learnable world + prior-only learner). Serves: WLD-02, MEA-03, SCI-03.
  - Disposition: It is valuable as a known-answer fixture for WLD-02 (solvability witness beside the organism) and for the MEA-03 marginal and same-class batch rungs. It is not production code, and it has the majority-floor defect it was written to expose.
  - Correctness: The headline (trainers learn the prior, not the map) survives. Measured here, however, the 'BALANCED' V3 majority-class floor is 0.0948, against the uniform 0.0476 that every comparison uses. REINFORCE seed 0 on V3 scores 0.0958 with one active bin, which is exactly the majority floor and which the code would call 2.06x random.
  - Coupling: numpy. The test package import needs cypari.
  - Skeptic: not challenged.
- **Hecate exact shadow evaluator** [meas-a; Hecate; cost S] (evaluator: EXTRACT). Slot: R2 known-answer statistics library + dual-implementation CI check. Serves: MEA-11, MEA-05.
  - Disposition: HISTORICAL_CONTROL. Skeptic finding: q() (shadow_decisions.py:67-75) claims exact recovery of the rational behind a float for 'means of <= 200 values with denominators <= 12'. Under that bound the denominator can reach lcm(1..12)*200 = 5,544,000, above limit_denominator(10**6). In a random model inside the docstring's own domain, 9,599 of 20,000 recoveries were silently wrong while passing the 1e-9 assert, and 6 crashed.
  - Correctness: It found the real 0.2-0.1=0.0999 < 0.10 float defect (H3) and the H4 rule divergence, and it reproduces the recorded bootstrap CIs to 1e-12.
  - Coupling: Imports hecate.alien score/runner/dataset and scipy, and reads hecate/alien runs (read-only).
  - Skeptic: DOWNGRADE.
- **Hecate metamorphic evaluator harness** [meas-a; Hecate; cost S] (evaluator: EXTRACT). Slot: R2 CI metamorphic suite for verdict code. Serves: MEA-05, MEA-01.
  - Disposition: HISTORICAL_CONTROL. Skeptic finding: The claimed slots are wrong. M7's expectation is 'leave a positive verdict' (INV_F results table; judge 512-523), i.e. the verdict must CHANGE. That is a sensitivity property and the opposite of MEA-01's bit-identical invariance under label permutation. MEA-05's 'mutation-tested in CI' means mutating the checker CODE, whereas this harness mutates the input DATA rows.
  - Correctness: Reported run: 42 evaluators, 42/42 baselines reproduced, many INSENSITIVE or BLIND cells found. The harness itself has no tests.
  - Coupling: Hard-coded hecate/programs HT-* paths and role aliases (49-63); runs evaluators as subprocesses; uses a thread pool.
  - Skeptic: DOWNGRADE.
  - Shared file hecate/metamorphic/harness.py: assigned to this row (both rows skeptic-reviewed; less reuse wins: the harness is HISTORICAL_CONTROL, and the REBUILD row covers the evaluator contract only).
- **Ensorain N0-N6 null ladder / substrate collider** [meas-a; Ensorain; cost S] (evaluator: EXTRACT). Slot: R2 baseline ladder + R1 split builder (F6 pair-block holdout). Serves: MEA-03, WLD-03, TRF-02, MEA-04.
  - Disposition: HISTORICAL_CONTROL. Skeptic finding: holdout() (collider.py:126-147) filters a stream of (cell, value) observations over a dense D-mode tensor field (np.ravel_multi_index over dims). WLD-03 needs held-out world INSTANCES that are disjoint under the family symmetry quotient and sealed or encrypted from search jobs. holdout has no quotient, no sealing, and returns None after 5 attempts.
  - Correctness: 5 tests pass (surrogate exactness, no pair in the holdout, constant XC<=0, intervention support). Historically, N6 (same-class batch ALS) was added post-data and beat all 9 promoted specimens.
  - Coupling: numpy. Imports ensorain.wtp.organism and world3; specific to tensor-field completion.
  - Skeptic: DOWNGRADE.
  - Superseded row: Ensorain null ladder N0-N5 + XC [world; evaluator REBUILD; v1 final REBUILD; skeptic none].
  - Superseded row: Ensorain WTP-03 collider protocol [org-b; evaluator EXTRACT; v1 final HISTORICAL_CONTROL; skeptic DOWNGRADE].
  - Correction: merged: one file (ensorain/wtp3/collider.py) evaluated three times; two skeptic reviews say HISTORICAL_CONTROL, the unreviewed world row said REBUILD; reviewed wins. The MEA-03 baseline ladder is a new build that uses this ladder's missing-rung failure as a fixture.
- **Cosmos boundary-location attack** [meas-a; Cosmos; cost S] (evaluator: EXTRACT). Slot: R2 dose ruler / bracket location. Serves: CAU-03, SCI-13.
  - Disposition: HISTORICAL_CONTROL. Skeptic finding: Bases whose flip falls outside the 0.6-1.4 ladder are left out of the bias estimate (locate.py:63-67 add them as rows without delta, and 71 averages only f_obs rows). This censoring drops exactly the worst-biased worlds and pulls |mean delta| toward 0. LOCATION_OK is plain non-rejection (|mean| <= max(2SE, TOL), 79), i.e. absence of evidence read as OK, the pattern SCI-14 exists to forbid.
  - Correctness: It found per-family offsets (regs -.147, ca -.105, ring +.142) that balanced accuracy could not see. The single test covers only _summ and documents that cancelling biases look OK when pooled.
  - Coupling: Imports Cosmos boundary._fit, broker, contract and world.
  - Skeptic: DOWNGRADE.
- **Cosmos zero-parameter definition rung** [meas-a; Cosmos; cost NA]. Slot: R2 known-answer case for ladder/definition qualification. Serves: MEA-03, MEA-16.
  - Disposition: MEA-03 already mandates the label definition as a zero-parameter rung, so the requirement itself is the salvage. R-0001 is a known-answer 'law restates its label' fixture for MEA-16 and MEA-03 qualification.
  - Correctness: There is no reusable rung code. The recorded case shows a law that is indistinguishable from its own certificate.
  - Coupling: t_i1_fragments reads a holdout-named campaign file (not opened).
  - Skeptic: not challenged.
- **xpol floors (hephaestus)** [meas-a; Hephaestus; cost S] (evaluator: EXTRACT). Slot: R2 baseline ladder: gate null-pass probability. Serves: MEA-03, MEA-04.
  - Disposition: HISTORICAL_CONTROL. Skeptic finding: P(random tool passes the gate) is a 3-line loop (floors.py:60-63) that restates the 1.0 gate condition inline instead of calling the gate code, so the calibrated path is not the production path. It reports 7/200 = 0.035 with no interval. It imports the private _run_battery and _NCDBaseline from agents/hephaestus/src/test_harness via a sys.path insert (22-24).
  - Correctness: It showed that the honest 1.0 ruler sits below a decoy (floors.json).
  - Coupling: Imports agents/hephaestus/src trap_generator_extended and test_harness; writes floors.json beside itself.
  - Skeptic: DOWNGRADE.
- **Necropolis admissibility ladder** [meas-a; Necropolis/Keeper; cost NA]. Slot: historical instrument catalogue. Serves: MEA-01.
  - Disposition: The MEA-01 dossier supersedes it. TOOLS.jsonl is a useful catalogue of historical instruments and their control state.
  - Correctness: The validator catches 11/11 REJECT cases but lets 7/8 CHEAT cases through (evidence sis-c s2.5). The ladder certifies that a tool ran under controls, not that it detects anything.
  - Coupling: Registry-specific; uses git subprocess.
  - Skeptic: not challenged.
- **attacks/REGISTRY.md (ATK-001..020)** [meas-a; Charon; cost NA]. Slot: R2 canary injector failure-class list. Serves: MEA-17, MEA-05, SCI-07.
  - Disposition: This is the best available list of failure classes for the MEA-17 canary injector (one canary per class) and the MEA-05 cheat battery. It is a taxonomy, not machinery.
  - Correctness: Kill records cited per class. The probes are instance-specific.
  - Coupling: Probes import ergon modules.
  - Skeptic: not challenged.
- **attacks/preflight.py (admissibility preflight)** [meas-a; Charon; cost S] (evaluator: EXTRACT). Slot: R2 prereg/attainability lints + CI ratchet. Serves: SCI-05, MEA-06, PRV-09, PRV-04.
  - Disposition: HISTORICAL_CONTROL. Skeptic finding: dead_field passes whenever coverage > 0 (preflight.py:64). A field carried by 1 of 10,000 rows PASSES (reproduced), which breaks the module's own rule that 'a gate whose input is absent must RAISE'; MEA-06 needs presence on every row. degenerate_strata reads a missing outcome as False (91, bool(r.get)) and passes when no stratum reaches n=30 (94-96, reproduced).
  - Correctness: --selftest run here gives 9/9. A field miss on a live ATK-013 instance was reported (tit-b).
  - Coupling: Stdlib plus git ls-files.
  - Skeptic: DOWNGRADE.
- **bee_tracer (BEE shadow tracer)** [meas-b; Bellerophon; cost NA]. Slot: R2 / REP qualification protocol. Serves: REP-02, REP-06, MEA-01.
  - Disposition: No BEE substrate in Phase 3. The value is process evidence: an independent reimplementation from spec text reached three-way exact agreement on a sealed fresh set and exposed a spec ambiguity (C11). That is the REP-02/REP-06 protocol for qualifying the DGM provenance shadow, with amendment rules frozen in advance.
  - Correctness: REPORTED: 32,827/32,827 births replayed bit-for-bit, 28/28 fixtures, 123,210 interactions value-equal. Production agreement first failed at 0.974 < 0.995 and passed after the post-exposure C11 amendment; the BEE verdict is VALIDATED only as amended.
  - Coupling: Needs the pinned BEE harness 16fc6c2a (prometheus/z80atlas) and the fixture pack from the unmerged branch origin/archaeon/attribution-arc-2026-09-28; production data host-local
  - Skeptic: not challenged.
- **Artemis CVT-2/CVT-R heredity certificates + W2-36 R* proposal** [meas-b; Artemis (R*: Nestor W2-36); cost NA]. Slot: R2 plant library (heredity/transmission battery pattern). Serves: DEV-12, MEA-02, MEA-16.
  - Disposition: Phase 3 has no self-replicating substrate (reproduction is explicit in R4). The panel design and the certificate shape (perturb the parent, >=2 generations, common random numbers, inheritance, fidelity, K seeds) are the reusable content, rebuilt only if a DEV-12 transmission claim is preregistered.
  - Correctness: VERDICT.json committed: P-11 unsound for heredity (certifies 4 painters) and over-strict; CVT-2 weakest adequate; TB calibration exact (0,0,1,4). W2-36 REPORTED: CVT-R false-accepts rescue mutants and HALFBLANK (9/9 seeds), and 6 recorded verdicts flip under K=8. R*: POS 8/8, NEG 0/8, never frozen.
  - Coupling: common.py:10 hard-codes a Linux /tmp scratch path on another host; imports Nestor p11/z8 from those scratch copies; W2-36 imports through W2-16/_env
  - Skeptic: not challenged.
- **P-11 randomized-victim assay** [meas-b; Nestor; cost NA]. Slot: R2 plant library + intervention pattern. Serves: CAU-09, MEA-05, DEV-03.
  - Disposition: No pair-tape soup in Phase 3. Its matched re-execution geometry (exact snapshot, keyed streams, private replay) is the template for R2 counterfactuals, and its painter false positive is the canonical construction-vs-heredity fixture.
  - Correctness: Run on a scratch copy: T-P11 14/14 PASS, incl. predecessor-fooling negatives, criterion-can-fire for C2/C4/C5, and prov vs prov_lit. REPORTED: certifies painters; only 6/57 survivors re-pass from a fresh state.
  - Coupling: constants.py and frozen z8.py; the test writes T_P11_RECEIPT.json into the repo
  - Skeptic: not challenged.
- **CW01 qualified scattered Bernoulli(f) damage ruler** [meas-b; Nestor; cost S] (evaluator: EXTRACT). Slot: R2 dose operator. Serves: CAU-03, CAU-01, MEA-01, MEA-11.
  - Disposition: HISTORICAL_CONTROL. Skeptic finding: Code read. Tests not run (they need F: and write into the repo). (1) The 'five-check qualification' qualifies a PRNG, not a ruler, and most checks cannot fail. Hit-count z and chi-square only test that SplitMix64 unit() < f is Bernoulli. Length independence holds by construction for an i.i.d. mask. Reproducibility (run_PG01.py:59) calls SC.mask twice with the same arguments in one process, which is a tautology.
  - Correctness: RESULT.json: INSTRUMENT_QUALIFIED (mean z -0.011, var z 0.991, chi p .485 over 25,200 draws; sham 126/126). P-G08: exact-count and contiguous rulers manufacture length slopes outside the band while Bernoulli/reached-only/disable do not. This qualifies the sampler only, not sensitivity on planted organisms.
  - Coupling: arch4rt/looprun loop harness, numpy, multiprocessing pool(8); apply() specific to the Proteus genome (IW words)
  - Skeptic: DOWNGRADE.
- **Diomedes decomposition ladder and hidden-variable proxy baseline** [meas-b; Diomedes; cost NA]. Slot: R2 MEA-15 decoder-qualification dossier (planted proxy rung). Serves: MEA-15, MEA-03.
  - Disposition: Off-domain: no organism or world, and it depends on an untracked corpus. The failure shape (navigation that is really hidden-variable sensing) and the proxy-rung idea (a cross-fitted reconstruction from input-side correlates, folds by object identity) belong in the MEA-15 decoder dossier and the MEA-03 baseline ladder.
  - Correctness: CONFIRMED in tan-b: the proxy reproduces 41-45% of the span. Known ruler defects: zero-width cluster bootstrap for power-of-two clusters; SE unit error of 52x.
  - Coupling: sklearn, numpy; untracked theseus/corpus (PROMETHEUS_CORPUS); cross-imports between cycle scripts
  - Skeptic: not challenged.
- **comms.identity store identity guard (+ ew/db.py wrapper)** [infra; Hermes; cost S] (evaluator: EXTRACT). Slot: R0 store connector. Serves: PRV-06.
  - Disposition: HISTORICAL_CONTROL. Skeptic finding: It is fail-OPEN on a malformed registry entry. identity.py:154 skips every field whose expected value is None, so an entry with null or missing db_system_id/db_name passes on ANY database. Fake-connection probe: {db_system_id:null, db_name:null} -> MATCH; an entry with only a description -> MATCH. The documented mitigation for the residual risk is dead code.
  - Correctness: Positive/negative/cheat controls exist; the cheat is a perfect schema on the wrong cluster (test_identity.py).
  - Coupling: The registry is keyed to the M1/M2 clusters as measured on 2026-09-11. The ew/db.py wrapper loads a tracked config.json with credentials.
  - Skeptic: DOWNGRADE.
- **comms.manifest LF-normalised artifact hashing** [infra; Hermes/operator ruling; cost S] (evaluator: EXTRACT). Slot: R0 content addressing / custody. Serves: PRV-01, PRV-04.
  - Disposition: HISTORICAL_CONTROL. Skeptic finding: Scratch probes, nothing written to the repo. (1) Content-address collisions. The binary test is 'NUL byte in the first 8 KiB' (manifest.py:25-26), so a short binary with no NUL is treated as text and its CR bytes are rewritten (manifest.py:29-32). Distinct 4-byte blobs 9f0d44e1 and 9f0a44e1 hash EQUAL, and 88% of random 32-byte blobs (seeds, keys, raw digests; R1 sealed seeds) get normalised.
  - Correctness: Tests cover CRLF/LF equality, binaries untouched and a changed file caught.
  - Coupling: Pure, stdlib only.
  - Skeptic: DOWNGRADE.
- **Workspace guard (archaeon.workspace and 7 copies)** [infra; Archaeon (copied by others); cost S] (evaluator: EXTRACT). Slot: R0 receipts. Serves: PRV-04.
  - Disposition: HISTORICAL_CONTROL. Skeptic finding: receipt() fails open on the very fields PRV-04 consumes. _git returns '' on any failure and ignores the return code (workspace.py:28-32), so dirty=bool('')=False and base_sha='' whenever git cannot answer (workspace.py:80-82). Probe on a non-repository dir: {'base_sha': '', 'dirty': False, 'repo_id': ''}.
  - Correctness: Tests cover main vs linked worktree, the override, fail-closed without git, and repo_id separating histories.
  - Coupling: git on PATH. Eight divergent copies.
  - Skeptic: DOWNGRADE.
- **Atlas experiment index and harvesters** [infra; Atlas; cost NA]. Slot: none in production; fixture corpus for historical re-scoring tests. Serves: SCI-01, SCI-03.
  - Disposition: The numbers are trustworthy and the classes are not. Keep the rows as a corpus for the SCI-01/SCI-03 tests and discard the classifier. Phase 3 axes are born with the experiment (PRV-06).
  - Correctness: Counts match source in every sample (158=158, 130=130, 1,242=1,242; ixi.md). Classes are wrong: 649 of 723 POSITIVE rows are Vivarium 'completed'.
  - Coupling: ew.db connector, comms.api instance_tag, registry.json hosts, one adapter per engine.
  - Skeptic: not challenged.
- **PEW campaign reader and campaign_observations corpus** [infra; Mnemosyne; cost NA]. Slot: fixture corpus for historical re-scoring. Serves: SCI-01, SCI-03.
  - Disposition: Valuable as a provenance-tagged historical corpus, not as machinery.
  - Correctness: 32,938 observations with line provenance (ixi.md, REPORTED).
  - Coupling: PEW store, hard-coded campaign paths and seeds.
  - Skeptic: not challenged.
- **Daedalus SFE ledger core (hash chain + prospective window + evidence class)** [infra; Daedalus; cost S] (evaluator: EXTRACT). Slot: R0 append-only hash-chained ledger (semantics). Serves: PRV-03, PRV-07, SCI-04, PRV-08, REP-01.
  - Disposition: HISTORICAL_CONTROL. Skeptic finding: Several of the rules contradict the frozen requirements. (1) Producers write verdicts: record_observation takes outcome FALSIFIED/SURVIVED/INCONCLUSIVE from the CLIENT (runtime.py:2361-2401). On the original observation it changes hypotheses.state and appends CLAIM_FALSIFIED/CLAIM_SURVIVED with actor=client (runtime.py:2513-2539). That violates PRV-02. (2) ENGINE_WORK_RESULT is a mislabel.
  - Correctness: Prediction-before-observation, tamper and mid-chain deletion tests pass. Probes show tail truncation with a head rewrite passes verify (ok=True, checked 4 of 5), and deleting all of a world's events passes (ok=True, checked=0) because events.py:185 skips the head check when no rows remain.
  - Coupling: sqlite3 only for events.py/ids.py. The rules sit inside the 5,125-line runtime.
  - Skeptic: DOWNGRADE.
- **Vivarium sealed spec + blind executor contract** [infra; Vivarium; cost S] (evaluator: EXTRACT). Slot: R0 runner input contract; R2 ruler label blinding. Serves: CMP-04, REP-01, PRV-04, PRV-08, MEA-05.
  - Disposition: HISTORICAL_CONTROL. Skeptic finding: (1) It is NOT blind. The sealed spec REQUIRES a non-empty free-text hypothesis (spec.py:355-356) and carries the requester's prediction (spec.py:367-369). The runner registers both and passes the whole spec to SFE (runner.py:682-689), and SFE copies the full spec into the work-item payload that the executing worker claims (sfe/runtime.py:2319-2324).
  - Correctness: test_blinding asserts provenance cannot reach the executor and that any input change changes identity. Infrastructure qualification found 10 production defects (sis-a.md SV-05).
  - Coupling: The contract is pure. The surrounding code is tied to SFE HTTP, PEW and Postgres.
  - Skeptic: DOWNGRADE.
- **Metis compose.py dependence-collapse kernel** [infra; Metis; cost S] (evaluator: EXTRACT). Slot: R0 verdict job: Rep axis / independence counting. Serves: REP-06, SCI-01.
  - Disposition: HISTORICAL_CONTROL. Skeptic finding: When ancestry is unknown, the kernel defaults to INDEPENDENCE. _group_by_shared_upstream merges two items only when their upstream sets intersect (compose.py:147-149), and the JSON loader turns a missing upstream into the empty set (compose.py:362). Probe: three items with no declared ancestry -> three independent reasons [['e0'],['e1'],['e2']].
  - Correctness: 13 adversarial tests. Historical validation is n=5 with a single encoder and a post-hoc positive control (ixi.md).
  - Coupling: Pure, stdlib only.
  - Skeptic: DOWNGRADE.
- **Alethelia query-carrying status report** [infra; Alethelia; cost S] (evaluator: EXTRACT). Slot: R0 derived status / weekly digest generator. Serves: INF-03, HUM-04, NRG-02.
  - Disposition: HISTORICAL_CONTROL. Skeptic finding: Empty sources read CALM. The rules fire only on non-empty stale or dormant lists (alethelia.py:309-338), and nothing checks the expected population. Probe with all sources reachable but empty (zero heartbeat rows, zero seats, workspace base_sha='') -> 'CALM: all 14 fields computed from live queries; 0 of 7 anomaly rules FIRED'.
  - Correctness: Planted stale-agent decoy, unreachable-source cheat, anomalies-under-full-reachability cheat, and guard controls.
  - Coupling: Sources are fleet objects (agora heartbeats, comms, BACKLOG, Elenchus shadow) that will not exist in Phase 3.
  - Skeptic: DOWNGRADE.
- **Atalanta null_bound park contract** [infra; Atalanta; cost S] (evaluator: EXTRACT). Slot: R0 wrapper for the few allowed standing processes. Serves: CMP-08.
  - Disposition: HISTORICAL_CONTROL. Skeptic finding: By its own docstring it is a demonstration: 'not an installation. No other seat's code imports it and nothing schedules it' (null_bound.py:3-4). Productivity is SELF-REPORTED by the wrapped tick() return value (null_bound.py:94-96), so the loop grades itself, the pattern INF-03 forbids. A tick that alternates productive and no-op resets the counter (line 99) and never parks.
  - Correctness: Positive, negative and cheat (artifact every tick) controls.
  - Coupling: Pure.
  - Skeptic: DOWNGRADE.

### RETIRE (26)

- **Proteus graph_organism.v1** [org-a; Proteus; cost NA]. Slot: none. Serves: ORG-10, ORG-11.
  - Disposition: Structure is fixed during a lifetime (no ORG-04 or ORG-06), and nodes are single operations rather than register machines. Node ids are renumbered when a node is deleted, which fails ORG-08. There is a live tick-ABI defect. Building the DGM from this means writing the whole DGM; the 342-line interpreter would be under 5% of it. Carry the ideas only: dormant neutral structure (ORG-11), edit-list lineage, and a meter with no timings.
  - Correctness: test_graph_vm.py has 10 tests (replay, dormant node, route, call reuse, yield/halt, persistence, validation, ABI, hygiene). They passed in the scratch run. There is no differential test. The persistence test increments ticks by hand, which hides the ABI defect.
  - Coupling: Imports only proteus.foundry.{prng,identity}. Consumed by archaeon/campaign6 (substrate.py, worlds/runtime.py) and archaeon/frontier/capabilities.py through handover.player_for.
  - Skeptic: not challenged.
  - Shared file proteus/graph/witness.py: assigned to Proteus known-answer search fixtures (keyed-memory witness, graph witness, PROTEUS-46 harness) [HISTORICAL_CONTROL] (a kept fixture depends on it, so it is HISTORICAL_CONTROL, not RETIRE).
- **Crius 8-register VM + workspace + executable block store** [org-a; Crius; cost NA]. Slot: none. Serves: ORG-10.
  - Disposition: It fails ORG-16/ORG-17 by construction. PSIM/PMATCH 'simulate in the head' using the world's own transition function (vm.py:490-497, 543-556), and the substrate keeps a calibration object for the organism (vm.py:438-472). Its switches are module-global and share one RNG stream per run, which is exactly the ORG-20 fake. It cannot take a snapshot mid-task. The DGM gets invocable structure natively, so none of this code is needed.
  - Correctness: 41 tests ran on a scratch copy: 41 passed in 214 s. Controls at the evaluation layer are strong (FRESH/ACC/RESET/SCRAMBLE/ABLATION/TRANSPLANT/RECORD_IDS_ONLY).
  - Coupling: Self-contained; it imports only its own package. The VM imports the world module world_c1 directly. Pure Python with multiprocessing.Pool.
  - Skeptic: not challenged.
- **Apollo program substrates (routing DAG v2, blackboard Branch C)** [org-a; Apollo; cost NA]. Slot: none. Serves: -.
  - Disposition: It fails ORG-16 (named cognitive modules as genes) and ORG-17 (competence supplied by the forge author) by construction; ORG-17's motive explicitly cites the Apollo solvers. It has no Phase 3 role as organism machinery. The blind-battery collapse belongs in another group's failure corpus.
  - Correctness: Not run. Historically, home-battery accuracy of 0.6000 fell to 0.0667 on Charon's blind battery (40/42 abstained). The crossover default of 0.0 (blackboard_evolve.py:802) suppressed the only improving operator.
  - Coupling: Imports agents/hephaestus/src/forge_primitives. LLM mutation servers (Qwen/Granite/DeepSeek). The Gen-2 adapter talks to a remote Foundry at 192.168.1.202.
  - Skeptic: not challenged.
  - Shared file apollo/src/blackboard_evolve.py: assigned to this row (both RETIRE; no conflict).
- **Lexis closure and congruence instruments** [org-a; Lexis; cost NA]. Slot: none (design notes to R3 closure audit). Serves: ORG-19, ORG-15.
  - Disposition: All of it is bound to Apollo's Python operator set, which is retired. In a DGM with flat integer state, tests A-E are moot by construction. Tests F and G port as ORG-19 closure-audit test specs of about 50-100 lines. Closure enumeration is the method ORG-15 names for proving non-expressibility, but this code does not transfer.
  - Correctness: Not run. The seat corrected its own '0.8333 ceiling' noun (ROLE s4a).
  - Coupling: Reads apollo/ read-only. workspace_guard inherits from archaeon/workspace.py.
  - Skeptic: not challenged.
- **Aether aeth01.v1 byte lattice + AETH-03 variants** [org-b; Aether; cost NA]. Slot: none. Serves: -.
  - Disposition: No organism, no demand, a medium that freezes about 92%, one energy regime. It has no primary, probe, reference or second-substrate role.
  - Correctness: test_aeth03_variants 39 passed here, including test_shared_path_is_v1_bit_for_bit (test_aeth03_variants.py:58-74). CPU-oracle vs GPU-shaped differential not run (hypothesis package missing).
  - Coupling: numpy, CuPy on pods; sys.path insertion of test/reference; RunPod key held on BUCKKEEP; aether/ vs Aether/ case collision on Windows.
  - Skeptic: not challenged.
  - Shared file Aether/observatory/aeth03_propagation.py: assigned to Aether verification kit [HISTORICAL_CONTROL] (kept frozen as a fixture under the verification kit; the one-bit twin design is rebuilt on DGM hooks).
- **Ensorain TT substrates E0-E2, D1 dials, LM01** [org-b; Ensorain; cost NA]. Slot: none. Serves: -.
  - Disposition: Online regression over cell addresses under a fixed policy fails ORG-04/ORG-17. The only positive (E1.5) was self-declared a tautology, and the worlds certify no cognitive depth. No Phase 3 role.
  - Correctness: Unit tests exist (e0-e2, lm01); not run; all verdicts INDETERMINATE or CLOSE.
  - Coupling: numpy only; read by Artemis scripts.
  - Skeptic: not challenged.
- **Theseus synth (concept tensor / synthetic ancestry)** [org-b; Theseus; cost NA]. Slot: none. Serves: -.
  - Disposition: No world, no demand, no organism. Its own rulers do not separate matched random programs from deep descendants, and its single lesson (generation counts inflate depth; random matched arms are mandatory) is already in the requirements (AGR-14, PRS-03).
  - Correctness: 10 tests exist; not run (compile_g0 shells git show in the cwd).
  - Coupling: imports tyche.lens; reads agents/nous concepts via git subprocess; numpy.
  - Skeptic: not challenged.
- **Ludus arena world/player interface + epistemic layer** [world; Ludus; cost NA]. Slot: R1 world interface (design reference only). Serves: WLD-14, REP-01.
  - Disposition: The R1 interface must follow the DGM contract (action or tick budget advances the world, cost channel, keyed streams, byte snapshot/restore, full-state hash). Adapting this costs about as much as writing it, and OpenSpiel is the better different-author cross-check. Harvest two ideas: replay identity excludes instrumentation; redacted per-player replays.
  - Correctness: Ran verify.py: ALL PASS (Kuhn -1/18 at n=12000, Bouton XOR, TTT draw, determinism on 5 worlds, ~70 s). Ran test_epistemic.py: 25/25.
  - Coupling: stdlib; sibling imports via sys.path ('import core'); not a package
  - Skeptic: not challenged.
- **Toolbox reference worlds, search and backends** [world; Bellerophon; cost NA]. Slot: none. Serves: -.
  - Disposition: No R1 family needs these worlds, and R4 search is specified separately. The package received no commits after 09-19, and z80atlas was written precisely because it could not express endogenous reproduction.
  - Correctness: not stated
  - Coupling: atlas_bee is the only importer
  - Skeptic: not challenged.
- **Ludus Atlas of Game Worlds (catalogue)** [world; Ludus; cost NA]. Slot: none. Serves: -.
  - Disposition: 0 executable and 0 audited rows. WLD-21 forbids reconstruction from memory or catalogue, and classifier accuracy was never measured.
  - Correctness: not stated
  - Coupling: network crawlers; Postgres ludus_atlas
  - Skeptic: not challenged.
- **Apollo v2 routing-DAG evolver (NSGA-III/AOS/racing/LLM)** [search; Apollo; cost NA]. Slot: none. Serves: -.
  - Disposition: Substrate, world and operator channel are all disqualified by frozen requirements: cognition lives in human-written operators (ORG-17), the LLM operator is not isolated (AGR-16), and the run depends on host GPU and an API key. PRS-08 needs a novelty-search arm on DGM, not this.
  - Correctness: No tests in apollo/.
  - Coupling: agents/hephaestus/src via sys.path; GPU and local LLM server; DeepSeek key; Postgres.
  - Skeptic: not challenged.
- **Apollo Branch C blackboard MAP-Elites** [search; Apollo; cost NA]. Slot: none (design note for R4 QD descriptors). Serves: PRS-09, PRS-05.
  - Disposition: The world is exhaustible (O1 enumerated it) and the organisms are not cognitive. Keep two things as control facts: crossover default 0.0 suppressed the only improving operator (PRS-09), and the load-bearing-core descriptor idea carries over to DGM intervention-signature descriptors (PRS-05).
  - Correctness: No unit tests. Controls exist as separate cycles: the O1 enumeration and the 2026-06-16 crossover A/B.
  - Coupling: hephaestus src, Granite/LLM helpers, apollo data files.
  - Skeptic: not challenged.
  - Shared file apollo/src/blackboard_evolve.py: assigned to Apollo program substrates (routing DAG v2, blackboard Branch C) [RETIRE] (both RETIRE; no conflict).
- **Tyche lens operators graft/fuse/compose** [search; Tyche; cost NA]. Slot: none (design reference for R4 operators). Serves: PRS-09.
  - Disposition: Genome-specific; DGM recombination must be a subgraph graft over nodes and edges. Keep only the operator-exactness test pattern (fuse == concatenation, compose == b(a(X))) for the DGM graft operator.
  - Correctness: test_fuse_equals_concatenation, test_compose_is_b_of_a and test_mutations_valid_and_ids_stable run here and passed.
  - Coupling: numpy; Tyche OPS table.
  - Skeptic: not challenged.
- **Ergon learner MAP-Elites** [search; Ergon; cost NA]. Slot: none. Serves: -.
  - Disposition: Domain mismatch (mathematical object search, not organisms in worlds), Postgres coupling, and a history of a stub evaluator whose archive fill was read as discovery. Nothing here beats the Theseus structure for QD.
  - Correctness: 24 test files present (not run; out of scope); trial 2 used a stub evaluator (tan-b ER-7).
  - Coupling: Postgres sigma_proto; math corpora.
  - Skeptic: not challenged.
- **NPE soup scheduler (Nestor Z8 x Atlas)** [search; Nestor; cost NA]. Slot: none. Serves: -.
  - Disposition: The shape the architecture forbids. Wall-clock staging makes allocation non-replayable, and a scalar interest built from unqualified signals steers compute. Its good ideas (matched controls, exploration floor, fresh-seed verification) are already requirements (AGR-13, PRS-02, REP-03) and need no code from here.
  - Correctness: No scheduler tests; not run.
  - Coupling: Z8 world, assays, observatory modules in the same campaign dir; concurrent.futures; disk budget.
  - Skeptic: not challenged.
- **prometheus_math statistics wrappers** [meas-a; Techne; cost NA]. Slot: none. Serves: MEA-11.
  - Disposition: MEA-11 should call scipy directly inside one known-answer-tested library. These wrappers add a dependency surface and no verdict logic.
  - Correctness: Not examined in depth: the wrappers add nothing verdict-specific.
  - Coupling: Importing prometheus_math pulls cypari through the package __init__.
  - Skeptic: not challenged.
- **Theseus F2 planted-relation content-aware promote gate** [meas-a; Techne/Theseus; cost NA]. Slot: none. Serves: MEA-03.
  - Disposition: Catalogue relation mining has no Phase 3 role, and the gate is broken on its production path. Its one idea (marginal-matched shuffled pairing) is already MEA-03's shuffled-pairing control.
  - Correctness: The calibration (0/8 decoys) used a per-source group scorer reimplemented inside the calibration scripts, not the production per-record function. The per-record score clears 0.10 for every record whenever the null hold-rate lies in (0.1, 0.9). The test author noticed this and weakened the assertion to 0<=score<=1 (test 111-125).
  - Coupling: Imports theseus.emit and theseus.generators, and needs the knots database file.
  - Skeptic: not challenged.
- **Nyx prediction packet schema and mechanism ledger** [meas-b; Nyx; cost NA]. Slot: none (R0 ledger + SCI-04 supersede). Serves: SCI-04, PRV-01, PRV-03.
  - Disposition: Interventions and controls are prose and no code computes a verdict (fails SCI-04); mechanism boundaries are source line ranges, i.e. localisation by reading, which CAU-06 says can only propose. R0's ledger, signed verdict job and derived status supersede it; the canonical-hash and supersedes chain are trivial R0 features.
  - Correctness: 2 tests: frozen packets validate and match their FREEZE hashes; novelty_kind vocabulary. REPORTED: 7 mechanisms, 0 transplants; 549 cuts, 0 blind.
  - Coupling: stdlib only
  - Skeptic: not challenged.
- **Fabric A2A gateway and promexec broker** [infra; Odysseus; cost NA]. Slot: none. Serves: -.
  - Disposition: No Phase 3 slot needs agent-interop protocols. Model-generated material in the run path is DGM genomes executed inside the interpreter, not host Python.
  - Correctness: The gateway REPORTED A2A TCK MUST 68/0. promexec has only a smoke positive control, explicitly not isolation evidence.
  - Coupling: Fabric store; systemd and sudo on ubu001.
  - Skeptic: not challenged.
- **comms inter-seat queue** [infra; Hermes/Archaeon; cost NA]. Slot: none (cross-seat work becomes Fabric tasks). Serves: HUM-03.
  - Disposition: Phase 3 runs at most three build sessions and forbids model-written status. HUM-03 is better served by code-executed Fabric tasks.
  - Correctness: Transport has been stable since 09-11 (1,239 messages, ixi.md), of which 86 heartbeats in about 25 h.
  - Coupling: evidence_wiki.ew.db connector, comms.identity, M1 Postgres.
  - Skeptic: not challenged.
- **Atlas comb and research policy layer** [infra; Atlas; cost NA]. Slot: none. Serves: -.
  - Disposition: A model-fed scalar steering layer with no outcomes. No Phase 3 slot.
  - Correctness: 192 signals, all OPEN, none consumed. 92 scores and 0 outcomes ever recorded (ixi.md). Correctness cannot be demonstrated.
  - Coupling: Atlas schema, model-written proposal fields.
  - Skeptic: not challenged.
- **Achilles fleet census** [infra; Achilles; cost NA]. Slot: none (concept feeds the R0 derived-status generator). Serves: INF-03.
  - Disposition: INF-03 needs a status generator over the build ledger, receipts and git. Alethelia's contract is the better seed. Keep the three defects as negative controls.
  - Correctness: 10 of 14 seats agree with git (ixi.md). Cheat controls exist for heartbeat-style signals.
  - Coupling: ELSA scheduled task, pushes to origin/main, comms/ew DB, the mailer.
  - Skeptic: not challenged.
- **PEW / Evidence Wiki store and service** [infra; Mnemosyne; cost NA]. Slot: none (ideas only: raw vs projection, derived cannot back evidence). Serves: PRV-06.
  - Disposition: Phase 3 has one primary store with derived views rebuilt from it. Carry over only the raw-vs-projection and derived-cannot-back-evidence rules.
  - Correctness: V0 gates REPORTED pass. The curated layer is frozen at 79 experiments; 143 of 147 claims are MODEL_EXTRACTED. Down since 09-23 with the alarm unanswered for 8 days (ixi.md).
  - Coupling: M1 Postgres. Tracked config.json with credentials. Shared connector used by many seats.
  - Skeptic: not challenged.
- **SFE as a service** [infra; Daedalus; cost NA]. Slot: none. Serves: -.
  - Disposition: Phase 3 R0 is a batch-oriented ledger, not a multi-tenant HTTP runtime.
  - Correctness: Large test suite (33 files). The service hosted only toy executors.
  - Coupling: fastapi, uvicorn, M1 TLS cert, Vivarium and Archaeon clients.
  - Skeptic: not challenged.
  - Correction: skeptic record removed: v1 carried the Daedalus ledger-core row's skeptic record (no challenge was raised against this row); restored to the evaluator category.
- **SFE verify_deploy.py (+ release.py build identity)** [infra; Daedalus; cost NA]. Slot: none (idea folded into R0 receipts). Serves: PRV-04, REP-01.
  - Disposition: Phase 3 receipts need the code hash plus a clean tree or diff hash for whatever ran. The 'stamp the loaded-build identity into every commit event' idea goes into the receipt component.
  - Correctness: Not tested here. Exists because the service ran from a shared checkout.
  - Coupling: Hard-coded endpoint and m1.crt; DEPLOYED_BUILD.json pin.
  - Skeptic: not challenged.
- **Vivarium as a service (daemon, loop, runner, PEW outbox/deliverer, deadman, kinds)** [infra; Vivarium; cost NA]. Slot: none. Serves: -.
  - Disposition: With one primary store and one runner, its job disappears. Keep the engineering record as context.
  - Correctness: 95-193 s per row around 0.1 s of science. No mutation, selection or pressure ever ran through it; science bypassed it from Campaign 4 (sis-a.md).
  - Coupling: SFE HTTP, PEW HTTP, Postgres, Windows Task Scheduler.
  - Skeptic: not challenged.
<!-- END GENERATED SALVAGE TABLE -->
