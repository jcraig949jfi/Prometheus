# Salvage digest: search / evolution machinery (R4)

Evaluator: salvage evaluator for EPIMETHEUS (Phase 3 architect OPUS-5.5). Date 2026-10-01.
Worktree: C:/prometheus-worktrees/epimetheus-phase3 (HEAD 91f1c9c2d), read-only.
Frozen inputs read first: docs/phase3/design/OPUS-5.5/RSE_ARCHITECTURE.md and requirements.jsonl
(ids cited below, e.g. PRS-03). Locators: evidence/{sis-a,sis-b,sis-c,tan-b,atl,idx}.md and
intake/tantalus/seats/Theseus.md. Every verdict below was made after opening the source.
Independence: nothing under docs/phase3/design/ other than OPUS-5.5/ was opened; roles/Dionysus/
was not opened; no holdout / nestor_secrets / credential path was opened (none lie in this group's
code paths; Cosmos holdout directories are outside this group and were not listed or touched).

The question asked of every component: DOES THIS SATISFY A PHASE 3 REQUIREMENT BETTER THAN
REBUILDING IT? Not "how do we preserve it".

-----------------------------------------------------------------------------------------------
## 0. Bottom line

1. NONE of the search engines in this group should be carried into Phase 3 as an engine. Every
   loop is welded to a retired substrate (Proteus v0 tape VM, Apollo blackboard of human solvers,
   Tyche lens programs, D-5 8-register toy, Z8 soups), and the R4 engine must be written against the
   DGM genome anyway. The engine itself is small (a few hundred lines of selection logic); what is
   expensive is the instrumentation around it, and that is where the salvage lies.
2. The four R4 estimators the architecture depends on -- rediscovery-from-distance p_hit(k)
   (PRS-03a), random-sampling needle rate at plant length (PRS-03d, CMP-01), the concentration-floor
   launch gate (PRS-13, CMP-05) and the pressure certificate (PRS-12) -- DO NOT EXIST anywhere in this
   group. The closest artefact, Archaeon's reachability table, estimates a different quantity
   (fraction of whole runs that reached a level) and actively types "unreachable" on 0/3 runs, which
   is exactly the null PRS-03 refuses. All four are REBUILD, from scratch.
3. Worth extracting (small, tested, generic): Tyche eps-lexicase (20 lines); the Theseus QD archive
   data structure (frozen calibration, multi-grid, quality = reproducibility, no scalar novelty);
   the SFE NK landscape with certified optimum + strict coordinate scan as R4 known-answer fixtures;
   the Proteus crucible's generic Markov-kernel analysis + two-route Holm (the only existing
   implementation of "publish the unselected variation kernel", AGR-15); the Proteus keyed stream
   primitive (seed_from / SplitMix64.derive); Tyche v2's declared-policy matrix (STRICT / LEX / RES
   with neutral drift; MUT / GRAFT / LOL chemistry) and its per-parent "deciding case" selection log;
   the Tyche natural-history tracer concept (why did stepping stones survive?).
4. Worth keeping as control / known-answer corpus: SFE Gen-2 canary (identical RNG per arm,
   parity-preserving mutation: the REP-07 motivating defect), PROTEUS-46 greedy walk (strict
   tie-rejection with a 3-step horizon: the PRS-02/PRS-03 motivating defect), Apollo O1 enumeration
   (exhaustive enumeration with a mandatory positive control), Apollo crossover default 0.0 (PRS-09),
   D-5 M0 navigator suite + R == E constructive proof + fast/slow equivalence, Ergon planted-witness
   library cheat (channel sensitivity at stated MDE), the WOW/D-13 archaeology fact that 85/87
   selection events were fully tied (selection was drift), Deep Frontier as a whole (3.72M
   evaluations steered by rulers with 25% / 0% planted catch).
5. Retire outright: Apollo v2 NSGA-III/AOS/LLM evolver, Apollo Branch C as an engine, Deep Frontier
   scheduler/loop/allocation, campaign 6 segment loop as an engine, NPE soup scheduler (wall-clock
   staged, scalar "interest" from unqualified signals), Archaeon campaign 2-3 harness machine (SFE
   HTTP client coupling), Ergon learner MAP-Elites (math domain, stub evaluator).

Estimated R4 build (new code, incl. tests): engine M (8-18M tokens), PRS-03 estimator M (6-12M),
pressure certificate M (6-12M), launch gate + feasibility S (1-3M), unselected-kernel audit port S-M
(3-8M), extractions S each. Total roughly 30-55M tokens, i.e. comparable to the architecture's
"60-200M build tokens for 20-25k LOC" envelope share for R4. Salvage saves perhaps 5-10M tokens of
design and test-fixture work, not engine work.

-----------------------------------------------------------------------------------------------
## 1. R4 needs vs what exists (one line each)

    need (requirement)                                   best existing artefact            verdict
    declared acceptance policy, >= 2 policies incl.      D-5 M0 suite (HC tie-accept, POP,  REBUILD engine;
      random sampling at same budget (PRS-02)              RX); Tyche v2 STRICT/LEX/RES       EXTRACT policy matrix
    neutral-accepting arm / neutral networks (ORG-11)    D-5 m0_hc `d <= best_d`;           EXTRACT protocol
                                                         Archaeon C4-05 neutral walk;
                                                         Tyche RES drift 12/gen
    lexicase / QD with stable descriptors over >= k      Tyche eps_lexicase; Theseus        EXTRACT + HARDEN
      seeds, strict tie-break counterfactual (PRS-05)      Archive; Tyche STRICT arm         (stability filter absent)
    mechanical novelty archive (AGR-10)                  Tyche novelty(); Theseus rulers    EXTRACT structure only;
                                                                                            rulers unqualified (MEA-18)
    recombination as declared factor (PRS-09)            D-5 use_crossover; Apollo          REBUILD (clean switch);
                                                         --crossover-frac; Tyche --chem     Archaeon has none
    optimiser plurality incl. novelty search (PRS-08)    Apollo NSGA/novelty (LLM-bound)    REBUILD
    rediscovery-from-distance p_hit(k) (PRS-03a,b,c)     nothing (reachability table is     REBUILD
                                                         run-frequency, not p_hit(k))
    random-sampling needle rate (PRS-03d, CMP-01)        Apollo O1 (exhaustive, substrate-  REBUILD
                                                         bound); SFE NK enumeration
    concentration floor launch gate (PRS-13, CMP-05)     nothing (campaign4/launch_gate is  REBUILD
                                                         an infra readiness gate)
    pressure certificate N_e*s >= 10 (PRS-12)            nothing (WSE POS controls exist    REBUILD
                                                         but never scored under selection)
    cost ramps with zero-cost arm (PRS-06)               WSE Regime + ramp multiplier       REBUILD (concept ok)
    change-rate schedules (PRS-07)                       campaign6 pressure schedules       REBUILD (world-bound)
    keyed independent streams (REP-07)                   proteus.foundry.prng (good);       EXTRACT primitive;
                                                         WSE/C6 default SHARES streams      default must invert
    unselected variation kernel published (AGR-15)       Proteus crucible V0.3-V0.6         EXTRACT
    selection-event telemetry (ties, deciding case)      Tyche SELECTION.jsonl; WOW tie     EXTRACT schema
                                                         audit
    known-answer search fixtures (PRS-03 test)           SFE NK certified optimum; D-5      EXTRACT / HISTORICAL_CONTROL
                                                         witnesses

-----------------------------------------------------------------------------------------------
## 2. Component verdicts

Cost scale: S < 5M tokens, M 5-30M, L 30-100M, XL > 100M of agentic coding.

### 2.1 Archaeon WSE GA loop -- REBUILD
Paths: archaeon/wse/evolve.py (450), economics.py (50); depends on proteus/foundry/{generate,
lineage,grammar,vm,prng}.py.
What it really does: generational GA over Proteus v0 manifests. evaluate() runs a Player over
episodes and returns per-ask and all-or-nothing reward plus a resource meter (evolve.py:68-154).
Evolution keeps elitism 4, tournament 4 with strict `>` (first drawn wins ties, evolve.py:157-163),
draws a mate for every child and calls proteus descend(parent, seed, mate) (evolve.py:319-355).
Fitness = reward - m_g * cost vector, with a foothold ramp m_g (economics.py:29-31,
evolve.py:258-264). Fresh training episodes every generation (evolve.py:266-267). Step API
(evaluate_generation / reproduce / inject) lets curricula change spec between generations.
Correctness evidence: archaeon/tests/test_wse.py (independent reference evaluator of the event
grammar, POS/NULL organisms, cheat battery, determinism of run_cell) and test_campaign3_machine.py
-- RUN this session from a temp dir: 31 passed.
Defects:
- COMMON RANDOM NUMBERS BY DEFAULT: every arm in a cell shares the selection RNG unless the
  harness opts out (evolve.py:17-21, 43, 221-222). REP-07 requires the opposite default (independent
  keyed streams; sharing must be declared and pass SCI-05). This default is how geometric nulls get
  manufactured.
- No clean recombination switch. Recombination is the grammar's `splice` operator at weight 0.05
  (proteus/foundry/grammar.py:36) and with mate=None it splices from SELF (grammar.py:230-231), so
  "crossover off" changes the operator mix instead of removing one factor (PRS-09).
- Acceptance policy is implicit (generational + elitism 4 + tournament 4 strict); no declared
  policy object, no neutral/strict arm, no random-sampling arm at matched budget (PRS-02).
- Selection on noisy, per-generation training batteries; readouts mix training max and held-out
  (the C5 vs Deep Frontier contradiction, sis-a s0 item 5).
- SplitMix64.weighted() sums float weights with builtin sum (proteus/foundry/prng.py:72-80): a
  cross-CPython (3.11 vs 3.12 sum algorithm) bit-identity hazard on operator choice (REP-01); the
  crucible team fixed the same class in analysis with math.fsum but not here.
Serves (concept): PRS-02, PRS-06 (ramp + E0 zero-cost regime), REP-01. Slot R4.
Coupling: imports proteus.foundry everywhere; pathlib, OS-neutral; no GPU.
Decisive reason: the loop is ~300 lines that must be rewritten for the DGM genome anyway, and its two
load-bearing defaults (shared streams, no clean recombination off) are the wrong way round for
Phase 3. Keep the step-API shape, gen0 provenance (common_fill, evolve.py:177-197) and the
dual per-ask / episode readout as design notes. Cost M as part of the new engine.

### 2.2 Archaeon reachability table, corridor table, typed states -- REBUILD (estimand wrong)
Paths: archaeon/wse/reachability.py (455), corridor.py (110), states.py (227);
data archaeon/campaign2/REACHABILITY.jsonl, campaign3/CORRIDOR.jsonl.
What it really does: one row per GA run; pools rows by (cell, value_bits, N, G, E, regime,
foundry) and reports the FRACTION OF RUNS whose training best crossed a level, with Wilson bands
(reachability.py:61-81, 204-251); monotone pooling of right-censored stopped-on-solve runs
(reachability.py:263-299) is correct and is the one good idea. Corridor = does a mature source
population, used as initialization at a dose, reach the target (corridor.py:1-20).
Correctness: tests in test_campaign2_machine.py / test_campaign3_machine.py (levels need held-out
for SUMMIT; monotone pooling) -- campaign3 file RUN, passed.
Defects:
- Wrong estimand for PRS-03: no planted solutions, no k-step walks, no d0, no path profile, no
  random-sampling rate. It measures "did this whole GA configuration succeed".
- classify(): 0 hits in >= 3 runs -> OBSERVED_UNREACHABLE_AT_BUDGET (reachability.py:71-81), and
  states.py:17-18 fires TARGET_UNREACHABLE from it. PRS-03 refuses exactly this ("zero hits bounds
  nothing"; a null needs >= 3 expected hits at k >= d0).
- Wilson intervals, not the exact binomial PRS-03 specifies.
- Table path hard-wired inside the repo (reachability.py:37-38) and migrate_* rewrite the
  "append-only" file in place (reachability.py:409, 428, 454): PRV-03 violation.
Serves: PRS-03 only nominally. Slot R4.
Decisive reason: the quantity is the wrong one and the null typing is the forbidden one. Reuse the
right-censoring idea in the budget-curve part of the new estimator. Rows are a HISTORICAL record of
what budgets were tried (keep the data file, retire the code). Cost: absorbed in 3.1.

### 2.3 Archaeon C4 mutational censuses (DFE census, radius census, neutral walk) -- EXTRACT (protocol)
Paths: archaeon/campaign4/c4_01.py (456), c4_02.py (305), c4_05.py (322).
What it really does: C4-01 applies every frozen grammar operator x 8 draws to 57 manifest-backed
parents, evaluates children under common episodes on 4-5 environments and labels each child
D0..D7 (UNDECODABLE ... NEUTRAL, EXAPTIVE, IMPROVED) with a frozen floor (3/16) and band (1/16)
(c4_01.py:47-60, 115-137). C4-02 does the same at edit radius r. C4-05 runs bounded neutral walks:
a step is accepted iff the walker stays within the band of the ORIGINAL parent (c4_05.py:52-91),
archiving walkers at depths 0/2/4/8/16 and exposing them to held-out environments.
Correctness: in-module --self-test paths (synthetic draws); not run this session (they import the
campaign4 population files and refuse while the launch gate is RED, c4_01.py:316-321).
Defects: Proteus-bound; neutral walk does not count no-op proposals as tries (c4_05.py:68-69),
so a proposal-starved state could spin; reward is training per-ask on 16 episodes (resolution
1/16 = the band itself).
Serves: ORG-11 (neutral fraction and connectivity measured), PRS-03(c) inputs (what the operator
does to fitness near a solution), AGR-15 (selected-state view of the kernel, complementing the
crucible's random-genome view). Slot R2/R4 boundary (instrument that R4 consumes).
Decisive reason: the protocol (DFE census per operator on certified-capable parents + band-neutral
walks with held-out exposure) is exactly the ORG-11 test and is cheap to re-implement on DGM; the
code is not portable. Cost S.

### 2.4 Archaeon campaign 2 / 3 / 5 harness machine -- HISTORICAL_CONTROL (code RETIRE)
Paths: archaeon/campaign2/{runner,c2base,accounting,prereg}.py, c2_sfe01..10.py;
campaign3/{c3base,ladder,corridor_import}.py, c3_sfe01..10.py; campaign5/repb/*.py.
What it really does: experiment harness classes with sealed PREREG, attempts/resume, receipts and an
SFE HTTP engine wrapper (runner.py:1-60; c2base.py:1-40); C3 delay ladder with revisit share
(ladder.py:1-40); C5 Representation B (FAIL/FIZZLE faults) as a second encoding.
Correctness: test_campaign2_machine.py (attempts, resume, prereg seal, engine descriptor -- the last
requires a host cacert file; not run) and test_campaign3_machine.py (run, passed).
Defects: hard dependency on SerendipityFoundryClient via sys.path insertion and a gitignored
config.local.json (runner.py:30-46); every campaign rewrites its own prereg/ledger machinery that
R0 will own; RepB duplicates what ORG-21 gives DGM natively.
Serves: nothing in R4 directly. Its results are a control corpus: C3 ladder vs matched-budget
direct search (the only curriculum-vs-direct control in the record; ATL-11 shows the "delay
general" winner was a first-input latch) and the opcode-permuted incompetent-import control
(ATL-05: incompetent imports take over 11-12/12 like competent ones).
Decisive reason: provenance belongs in R0; keep the rows and the two controls as known-answer
material for DEV-11 / TRF tests. Cost NA.

### 2.5 Campaign 6 segment loop, pressure schedules, Deep Frontier scheduler/loop/allocation -- HISTORICAL_CONTROL (code RETIRE)
Paths: archaeon/campaign6/segment.py (470), pressure/schedules.py (192), observatory/detectors.py;
archaeon/frontier/{scheduler (519), loop (303), allocation (79), registry, queues, specs}.py,
OPERATOR_EXECUTION_AUTHORIZED.json, suppressions/.
What it really does: run_segment(spec, checkpoint_in) is a pure function over generations
[g0, g1) carrying rng_state in the checkpoint, with a determinism + continuity self-test
(segment.py:144-367, 432-465) -- a genuinely good pattern. Selection is again elitism 4 /
tournament 4, hard-coded (segment.py:331-333), regime hard-coded E0 (segment.py:147), training
episodes (segment.py:219); 11 FIRE/QUIET detectors run on every child every generation and drive
freezes (segment.py:276-316). The scheduler pops items from EXPLORATION/EXPLOITATION/AUDIT pools by
share deficit (scheduler.py:239-248), branches only on hard-coded ADMITTED detector firings
(scheduler.py:178-200), reorders by an operator-editable pursue.json multiplier table
(scheduler.py:204-237, 332-343) and runs arbitrary readout modules that rewrite a tracked JSON
(scheduler.py:408-436). Allocation adapts pool shares on a yield count (allocation.py:1-75).
Correctness: segment self-test exists (not run: it reads campaign files and is a 20-generation run);
test_frontier_suppression_logging.py exists but NOT run (step() may call charge_pursuit and
run_due_readouts, which write tracked files under archaeon/frontier/).
Defects:
- Ran without its own gate: OPERATOR_EXECUTION_AUTHORIZED.json has is_verification false,
  G6_0_ALL_COMPONENTS_VERIFIED false, five unverified items.
- Steered 3.72M evaluations with detectors whose planted-positive catch was 25% and 0% at 1%
  false-fire (campaign6/DECISIONS.md D6-010 via sis-a). The "every N climbs" headline is a TRAINING
  max (segment.py:219, 319-320).
- One unchanged suppression produced 299,991 identical event rows (repaired, scheduler.py:266-278).
- Stream key defaults to run_id, so "same seed" arms did not share streams until a later fix
  (segment.py:115-119) -- the mirror image of the WSE CRN default; neither is declared per REP-07.
Serves: nothing as is. The architecture names this as the shape to avoid (RSE_ARCHITECTURE s1).
Decisive reason: keep as the canonical anti-pattern (steering by unqualified detectors, AGR-13 must
be served by a mechanical battery, not by "interest"); extract only the segment purity +
continuity self-test as a REQUIREMENT on the new engine's checkpoint/resume (REP-01), not the code.

### 2.6 Proteus mutation-kernel crucible V0.3-V0.6 -- EXTRACT
Paths: proteus/v0_3..v0_6/*.py (about 6.4k lines incl. runners); generic cores
proteus/v0_6/equilibrium.py (425), proteus/v0_4/holm.py (148), proteus/v0_5/multiplicity.py (111);
substrate-bound proteus/v0_5/kernel.py (385), v0_3/battery.py, run_crucible.py.
What it really does: measures the UNSELECTED variation process. V0.3-V0.5: pure-mutation lineages
(no selection) tracked on ~70 genome/phenotype coordinates against null references NC1-NC5
(length- and configuration-matched), one global step-down Holm implemented twice by independent
routes that must agree or adjudication aborts (holm.py:1-16, 102), a frozen one-sided confirmatory
replication with a fresh seed from a public hash (PREREG_V0_5.md s2-3). V0.5/V0.6: the structural
Markov kernel of the live operator on (genome_length, tape_words), measured by applying the real
operator to random genomes (kernel.py:54-87), with two numerically independent stationary solvers,
probability currents, entropy production, a cycle basis, reversible and Metropolis references
(equilibrium.py).
Correctness: test_v0_5_gates.py, test_v0_6_gates.py, test_holm_and_symmetry.py, test_mutation.py --
RUN this session from a temp dir: 51 passed (incl. "two stationary solvers agree", "reversible
reference has zero current", "Holm implementations agree on random families", "V0.3 buggy Holm
over-declares"). Cross-host replay files exist for three hosts (Windows py311/py312, Linux py312).
Defects (from code + Harmonia ruling via sis-c): state space is structural only, content is
marginalised over random genomes, so it cannot see directionality conditional on selected genomes;
the reversible reference "cannot fail" by algebra (a tautology, not a control); admitted only as a
DETECTOR, not an absence instrument (no positive control at declared MDC, no floor guard); V0.4's
halt/yield "discovery" failed its own confirmatory replication (z 1.90, p .97) -- which is the
machinery working, not failing.
Serves: AGR-15 ("every variation operator publishes its unselected variation kernel"), ORG-11
(neutral fraction), MEA-11 (known-answer statistics: two-route Holm with fixtures). Slot R4
(operator audit) feeding R2.
Coupling: pure stdlib + proteus.foundry; refuses to run against a different grammar hash
(run_crucible.py load_prereg) -- correct discipline, but means the runners themselves are not
portable. equilibrium.py and holm.py import nothing substrate-specific.
Decisive reason: it is the only existing implementation of an unselected-kernel audit and its
generic cores are tested and small. Port equilibrium.py + holm.py as-is into R2's known-answer
statistics library; re-implement the crucible protocol on DGM coordinates (node/edge counts,
instruction-class mix, developmental-instruction share) WITH a planted positive control at stated
magnitude so it can serve as an absence instrument. Cost S (port) to M (DGM protocol + positive
control).

### 2.7 PROTEUS-46 falsifier greedy walk -- HISTORICAL_CONTROL
Paths: proteus/round2/falsifier_46.py:30-31, 113-131.
What it really does: best_key = (cur, 0) sentinel for the parent vs child key (two, -ops) with
ops >= 1, so equal-score children can never be accepted; WALK_STEPS = 3. Verified this session.
A 5-edit duplicate-and-diverge path with 4 neutral steps exists (Artemis D002, via sis-c) and is
outside the attainable verdict set of both probes. Its CLIFF_SURVIVES verdict became a frontier-wide
suppression.
Serves: as a planted NEGATIVE for the prereg linter / PRS-02 policy declaration and for the PRS-03
estimator test: a strict tie-rejecting horizon-3 walk must be flagged as unable to type any null.
Decisive reason: the clearest single-file specimen of "greedy tie rejection manufactured a cliff".

### 2.8 Apollo v2 routing-DAG evolver (NSGA-III / AOS / racing / LLM mutation) -- RETIRE
Paths: apollo/src/apollo.py (1203), selection.py, novelty.py, map_elites.py, aos.py, racing.py,
mutation.py, mutation_llm.py, llm_server*.py, deepseek_client.py.
What it really does: routing DAGs over 25 puzzle-named human-written primitives evaluated on static
NL tasks; 6-objective NSGA-III, adaptive operator selection, racing, LLM mutation through a local
Qwen server (VRAM check) or DeepSeek API, Postgres heartbeat (apollo.py:1-60, 101-130, 302-372,
481-556).
Correctness: no tests in apollo/.
Defects: organisms order human solvers (cognition lives in the operators, ORG-17); global Python
random; LLM operator receives organism code and is not isolated, hashed or capped (AGR-16);
NoveltyArchive kNN includes the population (self-distance 0 possible, novelty.py:15-27).
Serves: nothing (PRS-08 optimiser plurality needs a novelty-search arm on DGM, not this).
Decisive reason: substrate, world and operator channel are all disqualified by frozen requirements.

### 2.9 Apollo Branch C blackboard MAP-Elites -- RETIRE (as engine); HISTORICAL_CONTROL (crossover A/B)
Paths: apollo/src/blackboard_evolve.py (817), blackboard*.py, dataflow_fitness.py.
What it really does: MAP-Elites over linear typed pipelines (<= 6 body ops) of ~26 hand-written
operators; descriptor = (scorer set, load-bearing core by ablation) (blackboard_evolve.py:432-445);
archive insertion only on strict lexicographic improvement (ccs, acc, -len) (:664-668); uniform cell
selection; optional crossover `--crossover-frac` with DEFAULT 0.0 (:802); global random.seed
(:491); default run_dir inside the repo (:525).
Correctness: no unit tests; O1 enumeration (2.10) and the 2026-06-16 crossover A/B are its controls.
Defects: strict insertion (ties rejected); evaluation world of 120 static tasks authored by the same
hand as the parsers; crossover default 0.0 suppressed the only improving operator (atl.md C5).
Serves: as control: PRS-09 motivating fact; the "load-bearing core" descriptor idea (descriptor
keyed on ablation-necessary structure so decorative padding cannot inflate the archive) is a good
idea for DGM QD descriptors (PRS-05 "intervention signatures").
Decisive reason: world exhaustible (O1 enumerated it), organisms not cognitive.

### 2.10 Apollo O1 enumerator -- HISTORICAL_CONTROL
Paths: apollo/scripts/o1_enumerate.py (263); cycles/o1_enumeration/.
What it really does: type-directed exhaustive enumeration of pipelines by subset size and valid
topological orders, every candidate scored by the substrate's own evaluator; the known 0.833
organism is checked FIRST as a positive control and the run aborts as ENUMERATOR_BROKEN if it is not
representable (o1_enumerate.py:150-171). Docstring records a caught defect: an earlier prune made the
known organism unreachable (:21-27).
Correctness: positive-control-first design; no unit tests; result files in cycles/.
Serves: pattern for PRS-02 (a non-evolutionary baseline at the same budget) and PRS-03(d)
(random / exhaustive hit rate at plant length) -- "the enumerator must represent the known plant or it
reports nothing" is exactly the rule the new random-sampling estimator needs.
Decisive reason: substrate-bound code, but a clean known-answer comparison (evolution 0.833 in 3,144
evaluations vs enumeration) and a model of positive-control gating.

### 2.11 Tyche eps-lexicase and novelty -- EXTRACT (HARDEN on extraction)
Paths: tyche/ecology.py:195-223; tyche/v2/run_v2.py:96-114 (lexicase_trace).
What it really does: eps_lexicase(M, rng, n): per-case epsilon = median absolute deviation over the
population, shuffled case order, filter to within eps of the current best, random final tie
(ecology.py:195-210). lexicase_trace additionally returns the deciding case and accepts an
`eligible` subset (the STRICT gate). novelty(): mean L1 distance to the k nearest pool signatures,
excluding clones (ecology.py:213-223).
Correctness: test_lexicase_keeps_specialists, test_strict_lexicase_with_no_eligible_returns_nothing
-- RUN this session: passed (5/5 Tyche tests run). The specialist test is weak (only membership of
two individuals in 400 draws).
Defects: epsilon computed over one evaluation seed (select_seed = 1, run_v0.py:37), so noise-level
cases decide parents: the v2 natural history counts 395 persistence events decided by a noise-level
case (tan-b TY-12), and Tyche v1's GATE 6 counterfactual failed because "noisy lexicase ... preserve
useless lineages" (tan-b TY-7). PRS-05 requires descriptors/cases stable over >= k re-evaluation
seeds and a strict noise-free tie-break counterfactual arm. `Zs` argument of lexicase_trace is unused.
Serves: PRS-05, AGR-10. Slot R4.
Coupling: numpy only; no host assumptions.
Decisive reason: correct, tiny, tested; extraction plus a stability filter (cases admitted only if
their sign is stable over k seeds) is cheaper than rewriting and keeps a known implementation.
Cost S.

### 2.12 Tyche v2 pressure-map driver (declared policy matrix + selection logging) -- EXTRACT (design)
Paths: tyche/v2/run_v2.py (489), v2/eco_v2.py.
What it really does: one run = one point of a declared policy map: --harsh STRICT (parents/elites
must hold a significant case, z >= 2; no reserve) | LEX (eps-lexicase, elites, no reserve) | RES
(LEX + 48-slot utility-free reserve with age, novelty, 1/3 random, 12 neutral-drift births per
generation, credit) and --chem MUT | GRAFT | LOL (run_v2.py:1-20, CFG 45-53). Every parent choice is
logged with deciding case, gain and z (SELECTION.jsonl), plus GENEALOGY, EVALS, POP, receipts with git
HEAD / dirty flag / host (run_v2.py:128-147).
Correctness: tests for compose exactness, strict-lexicase eligibility, regime phases (run, passed).
Defects: one rng stream for the whole run (run_v2.py:129), so arms that differ only in --harsh share
streams undeclared (REP-07); Block R ran PAIRS / GRAFT only with 30 post-switch generations
(search_insufficiency, tan-b TY-9); needle size never measured before typing parity-3 "unreached".
Serves: PRS-02 (policy declared and plural), ORG-11 (neutral drift arm), PRS-05 (strict counterfactual
arm), PRS-09 (chemistry as factor). Slot R4.
Decisive reason: this is the closest existing artefact to the R4 "declared acceptance policy incl.
neutral-accepting, lexicase/QD, recombination switch" shape; take the policy matrix, the reserve
semantics and the selection-log schema as the design of the new engine's policy object. Code is
lens-bound. Cost: inside the engine (M).

### 2.13 Tyche lens operators graft / fuse / compose -- RETIRE (design reference only)
Paths: tyche/lens.py:428-510.
What it really does: graft appends the cone of a donor output and optionally binds it (:428-455);
fuse concatenates two genomes' outputs exactly (:458-472); compose builds b(a(X)) (:475-490); mutate
applies 1-2 operators and silently drops invalid ones (:501-510).
Correctness: test_fuse_equals_concatenation, test_compose_is_b_of_a, test_mutations_valid_and_ids_stable
-- RUN, passed.
Defects: lens chemistry contains every planted-law primitive (tan-b "chemistry_contains_answer");
silent drop of invalid mutations changes the effective kernel without being reported (AGR-15).
Serves: nothing directly; DGM's recombination operator must be a subgraph graft over nodes/edges.
Decisive reason: genome-specific. Keep the "operator exactness test" pattern (fuse == concatenation)
for the DGM graft operator.

### 2.14 Tyche natural-history tracer -- EXTRACT (concept)
Paths: tyche/v2/history_v2.py (187).
What it really does: for every solved slot, walks the ancestry DAG, finds the first ancestor that
functionally carries each planted hidden precursor (MI above a permutation null), counts generations
the carrier line had no significant home value, attributes each survival to elite / significant
parent choice / noise-level parent choice / reserve reason / drift birth, finds the largest-jump
edge, and computes strict_survivable_frac = share of path ancestors that would have survived STRICT
gating (history_v2.py:1-27, 105-183).
Correctness: no tests; requires the answer key (planted precursors), legitimately, on plants.
Defects: observational only, no ablation (tan-b TY-11/TY-12); depends on the full run logs.
Serves: PRS-03(c) (fitness profile of the best known path against the acceptance rule: that is what
strict_survivable_frac is), ORG-11 (did neutral/drift carriage matter), DEV-14 is NOT served (that
is within-lifetime write order). Slot R4 analysis over R0 logs.
Decisive reason: the question "would this path have survived the declared acceptance rule" is a
required estimator input and this is the only prototype; re-implement over the new engine's selection
log. Cost S-M.

### 2.15 Theseus QD archive (synth/rulers.py) -- EXTRACT (data structure); rulers NOT reusable
Paths: theseus/synth/rulers.py (193); used by theseus/synth/run_v0.py:234-305, 346, 408-409.
What it really does: Cal is computed once from the generation-0 population and frozen (z-scaling,
PCA bases, grid edges at G0 quantiles with open outer bins, tau_rep replicability gate, per-metric
sparseness thresholds) (rulers.py:6-20, 115-141). Archive keeps per-grid cell elites for three grids
(pca, desc, resp) with QUALITY = REPRODUCIBILITY (smaller replicate distance), never novelty
(:144-182); "agreement" between rulers is a count, no scalar novelty anywhere. run_v0 adds weird-
random (W) and execution-neutral (X) control arms (run_v0.py:408-409) and protects archive elites from
culling (:346).
Correctness: theseus/synth/tests/test_synth_v0.py -- RUN: 10 passed, but only with cwd inside the
git repo (compile_g0 shells out to `git show HEAD:agents/nous/src/concepts.py`; from a temp dir 7 of
10 fail with CalledProcessError). The Archive class itself has no direct test.
Defects: F grows by np.vstack per insertion (rulers.py:181), O(n^2); grid edges relative to G0 make
cells population-relative (stable within a run, not across runs); no k-seed stability admission
(PRS-05) -- only a replicate-distance quality; the descriptors were shown NOT to discriminate: random
programs of matched size reach the same regions and weird high-gain programs pass viability 63-65%
(Theseus dossier s13-14). MEA-18 qualification fails as is.
Serves: PRS-05, AGR-10 (structure), MEA-18 (has partial garbage / neutral arms). Slot R4.
Decisive reason: the structure (frozen calibration before any arm, multi-grid, reproducibility as
quality, counts not scalars, control arms in the same archive) is the right discipline and costs
little to lift; the fingerprint descriptors must be replaced by DGM behavioural + intervention
signatures and qualified on garbage/static/noise/drift/extremal/neutral-shadow arms. Cost S.

### 2.16 D-5 GA navigators and substrate (Ergon's search core) -- HISTORICAL_CONTROL
Paths: agent_d5_blind/navigators/m0.py (139), learner/m1.py (128), mutation/physics.py (87),
substrate/{rm_vm,rm_fast,test_equivalence}.py, reachability_oracle/reachability.py (84).
What it really does: three declared navigators on one physics: M0a-HC hill climber that ACCEPTS
TIES (`if d <= best_d`, m0.py:53-55) with stall restarts; M0b-POP and M0c-RX generational GA
(tournament-3, immigrants 0.10, NO elitism, crossover 50% only in RX via use_crossover,
m0.py:81-111); run_ladder derives every smaller budget from one run's first-solve index
(m0.py:130-139). Every claimed solve on the fast scorer is re-verified on the reference VM and a
divergence is an assertion failure (m0.py:24-33). Reachability oracle builds an explicit verified
INSERT/DELETE path seed -> witness (reachability.py:33-60) and an ablated-physics length bound gives
planted UNREACHABLE cases.
Correctness: test_equivalence.py (fast vs reference VM, all opcodes, loops, step truncation) -- RUN:
"EQUIVALENCE PASS: 2402 programs x 128 inputs, bit-identical".
Defects: m1.py inserts '..\\substrate' style Windows separators (m1.py:20-21): breaks on Linux; no
elitism; R == E holds because INSERT makes every expressible program reachable, so reachability
"carries no information" in this physics (tan-b 4.2) -- the oracle is trivial, not a PRS-03 estimator.
Serves: known-answer material for ORG-15 tier separation (expressible / reachable / findable with
constructive witnesses per task), CMP-01 (fast kernel vs slow reference pattern), PRS-02 (plural
declared policies incl. a tie-accepting climber), PRS-09 (clean crossover flag). Slot R2 fixtures / R4
test fixtures.
Decisive reason: too small a world to search in, but the cleanest existing demonstration of the
policy-plural, witness-backed, fast/slow-verified search discipline Phase 3 requires.

### 2.17 Ergon library seeding and retention-policy lineages -- HISTORICAL_CONTROL (code RETIRE)
Paths: ergon/gen1b/gen1_run.py (299), ergon/gen3/p3_common.py (147), p3_run.py, cheat_control*.py,
mde_p3.py.
What it really does: immigrants draw 50% from a 64-slot genotype library (m1.py:51-54), i.e. about 5%
of children; four eviction policies (MRU, mutationally-redundant, effective-usage, random)
(gen1_run.py:59-156); effective use credited online by MONKEYPATCHING physics.mutate,
M1.mutate and rm_fast.FastTask.dist (gen1_run.py:159-199); a planted-witness cheat arm admits the
oracle witness before chosen tasks to show the channel can see an effect (p3_common.py:64-103).
Correctness: cheat control +3.38 pp detected at n 100 (p 0.00002), MDE80 1.22 pp; P3 null CI
[-0.24, +1.33] pp (tan-b ER-3; p3_results.json); lineage seed spaces disjoint by construction
(p3_common.py:25-31). No unit tests; not run.
Defects: monkeypatched module globals are fragile instrumentation; the cheat is a CONTENT injection
used to validate an ORDER null (ruler gap, tan-b ER-3); the channel itself is weak (5%).
Serves: as known answer: the content vs order vs random-library decomposition and a planted-witness
channel-sensitivity test at stated MDE (MEA-05, SCI-14 template). Slot R2.
Decisive reason: the engine is a toy; the experimental design is a template.

### 2.18 Ergon learner MAP-Elites -- RETIRE
Paths: ergon/learner/{archive,descriptor,engine,scheduler}.py (~1.8k lines + 24 test files).
What it really does: MAP-Elites over math-domain genomes (polynomial / Salem-cluster searches) with
pointer storage intended for Postgres (archive.py:1-30).
Correctness: tests exist (not run; out of scope). Historical trial used a stub evaluator; archive fill
was read as discovery (tan-b ER-7).
Decisive reason: domain mismatch (mathematical object search, not organisms in worlds) and Postgres
coupling; nothing here beats 2.15 for QD structure.

### 2.19 NPE soup scheduler (Nestor Z8 x Atlas campaign) -- RETIRE
Paths: roles/Nestor/campaigns/z80atlas-2026-09-19/scheduler.py (511), producer.py (221).
What it really does: a 72-hour campaign allocator over a frozen factor grammar: EARLY/MIDDLE/LATE
stages keyed to WALL-CLOCK fraction (scheduler.py:8-25, 43, 104-114); producer chooses cells by
factor-level / pair / triple coverage counts + UCB "interest" + a uniform exploration floor
(producer.py:1-30); every proposal is paired with a matched control on a declared axis; LATE re-runs
the strongest families on fresh seeds plus single-factor interventions. Interest is a weighted
SCALAR of run signals (replicated .30, crossed .30, serendipity .10, novel_genome .10 ...,
scheduler.py:51-54, 233-260).
Correctness: no unit tests for the scheduler; not run.
Defects: wall-clock staging makes allocation non-replayable (REP-01, INF-04); scalar interest built
from unqualified signals (MEA-18, SCI-12) steers compute -- the Deep Frontier shape again; seeds
from random.Random(seed ^ 0xBEEF) shared across families (REP-07 undeclared).
Serves: nothing. The good ideas (auto-paired matched controls, exploration floor, fresh-seed late
verification, single-factor interventions) are already requirements (AGR-13, PRS-02, REP-03) and
need no code from here.
Decisive reason: architecture-forbidden shape; nothing to lift.

### 2.20 SFE reference executors (BitString, NK landscape, coordinate scan) -- EXTRACT (R4 test fixtures)
Paths: SerendipityFoundry/SerendipityFoundryEngine/sfe/executors.py:71-437 (NKLandscape :150-245,
NKLandscapeExecutor :247-382, nk_coordinate_scan :385-437); WorkerLoop :439-492.
What it really does: SFE contains no search; executors score one candidate (docstring :1-13).
NK landscape: neighbours by hash-driven partial Fisher-Yates, integer table entries hashed on demand,
CERTIFIED optimum by direct computation at k = 0 and full enumeration at k > 0 for N <= 20
(:205-245), joint locus permutation as an executable exchangeability null, refusal of any malformed
payload. nk_coordinate_scan is a strict-increase, ties-keep climber with a termination proof in its
docstring.
Correctness: tests/test_sfe_nk_landscape.py -- RUN this session: 50 passed (integer-exact solved
status, joint-permutation invariance, a negative fixture that must move, k = 0 optimum equals
enumeration, one-scan guarantee at k = 0, tie keeps original).
Defects: sha256 per table entry is slow for large search budgets (memoized, fine for fixtures);
N <= 20 only (by design).
Serves: PRS-03 test ("estimator recovers known p_hit on planted landscapes": NK with certified optimum
gives exact needle sizes by enumeration), PRS-02 (strict climber as one declared policy), MEA-11
(known-answer). Slot R4 test fixtures. WorkerLoop / Foundry runtime is R0 infrastructure, out of this
group (not salvaged here).
Decisive reason: tested, stdlib-only, exact; lifting two classes is cheaper than writing a certified
landscape. Cost S.

### 2.21 SFE Gen-2 canary -- HISTORICAL_CONTROL
Paths: SerendipityFoundry/SerendipityFoundryEngine/sfe/canary.py:40-46, 74-79.
What it really does: five worlds forked from one checkpoint with identical initial population AND
identical RNG (random.Random(seed_root + 1) per world, :78), a (mu + lambda) search with a 2-bit-flip
mutation (:40-46) that preserves Hamming-distance parity; sharing topology is the only difference.
Verified this session (and re-derived by sis-a: initial distances 9/13/16/14).
Serves: REP-07 planted defect ("two arms sharing a stream undeclared: launch refused") and a planted
geometric null for SCI-05 attainability checks.
Decisive reason: a perfect, tiny, real failure fixture.

### 2.22 SFE off-repo search note (WOW archaeology of the D-13 Foundry) -- HISTORICAL_CONTROL; D-13 drivers UNKNOWN
Paths: SerendipityFoundry/wow/WOW_ARCHAEOLOGY_REVIEW_PACKET.txt (s1, s3); selection_boundary/
{toy_selection_bias,toy_candidate_conditional_randomization,selection_replay_audit}.py and
SELECTION_BOUNDARY_RESULTS.txt; stackvm_admission/*.
What it really does: audit of the off-repo D-13 corpus (stackvm-v1, treegp-deap, push-pyshgp;
objective_ga then map_elites drivers; 71,683 executions): 85 of 87 selection events were FULLY TIED
and resolved by seeded tie-break ("selection was drift"); 89.3% of failures came from a 100-400 step
ceiling; the population was two non-interbreeding length modes. The selection-boundary toys show a
selection-replicating null restores level after max-of-N selection and that undercounting search
depth is anti-conservative.
Correctness: toys print their own rejection rates against targets; not run. The D-13 driver code is
off-repo (F:/SerendipityD per sis-a) and was not inspectable: UNKNOWN.
Serves: mandatory search telemetry (log n_tied / n_candidates per selection event; flag a run whose
selection is mostly tied as drift), SCI-15 / MEA-11 (selection-replicating nulls as known-answer
statistics). Slot R4 telemetry spec; R2 statistics library.
Decisive reason: the single most important fact for an R4 designer ("your GA may be a random walk")
comes from here, and it costs nothing to keep.

### 2.23 proteus.foundry.prng keyed streams -- EXTRACT (dependency; R0 slot)
Paths: proteus/foundry/prng.py (83).
What it really does: seed_from(*parts) = first 8 bytes of a domain-separated sha256 over typed parts;
SplitMix64 integer generator with rejection-sampled randbelow (no modulo bias) and derive(*tags) for
independent child streams without consuming the parent.
Correctness: exercised by every Archaeon/Proteus determinism test run above (passed).
Defects: weighted() uses float builtin sum (prng.py:72-80) -- replace with integer weights or
math.fsum for cross-runtime bit identity.
Serves: REP-07, REP-01. Slot R0 (consumed by every R4 component).
Decisive reason: correct, minimal, already the pattern Phase 3 asks for; the R4 engine should use
derive(arm, world, organism, purpose) by default, the inverse of the WSE CRN default. Cost S.

-----------------------------------------------------------------------------------------------
## 3. What R4 must build new (nothing in this group serves it)

1. DGM evolutionary engine (REBUILD, M, 8-18M tokens). Declared policy object: generational
   tournament with elitism; (mu + lambda) with explicit tie rule (strict | accept-ties | accept within
   band eps, the C4-05 semantics); eps-lexicase over stable cases (2.11 + stability filter); QD
   archive (2.15 structure, DGM intervention signatures); novelty-search arm (PRS-08); random sampling
   at matched budget (PRS-02); recombination as a clean binary factor (operator removed, not
   replaced by self-splice); reserve / neutral-drift option (2.12 RES). Independent keyed streams by
   default; sharing declared. Checkpoint/resume as a pure function with continuity self-test (2.5
   pattern). Selection-event log: deciding case, n_tied, parent ids, policy id (2.12, 2.22).
   Unselected-kernel publication per operator (2.6).
2. PRS-03 reachability estimator (REBUILD, M, 6-12M). From >= 5 independently authored plants of the
   target class (R2 plant library): walks of k = 1, 2, 4, 8, ... operator steps, re-search from each,
   p_hit(k) with exact Clopper-Pearson intervals; d0 = operator distance from the initial distribution
   to the nearest plant (constructive upper bound + bounded BFS lower bound where feasible); best
   path fitness profile vs the declared acceptance rule (2.14 concept); random-sampling hit rate at
   plant length (2.10 positive-control-first rule). Known-answer test on SFE NK (2.20) and on the D-5
   ablated physics (2.16).
3. Concentration-floor launch gate + feasibility (REBUILD, S, 1-3M). Reads the p_hit(k) curve and
   measured throughput; refuses any arm below 3 expected hits; funds fewer arms when the envelope is
   short (PRS-13, CMP-05). Refusal semantics GREEN / RED / UNVERIFIED as in
   archaeon/campaign4/launch_gate.py:1-20 (pattern only).
4. Pressure certificate (REBUILD, M, 6-12M). Score capability fixtures (ORG-14, DEV-13) and best
   incapable baselines (detect-and-dispatch genome, flat learner, fixed-rule learner) under the exact
   regime at every cost-ramp point; require N_e*s >= 10 and paired advantage above per-evaluation noise;
   planted failures (cost above benefit, task off reproductive path, N_e*s < 1) must fail (PRS-12).
   Nothing in the record does this; Archaeon's hand-written POS organisms (archaeon/wse/controls.py)
   proved solvability, never selectability.

-----------------------------------------------------------------------------------------------
## 4. Cross-cutting defects found in this group (lint these in the new engine)

- Stream sharing defaults point in opposite directions in sibling code (WSE: shared by default;
  campaign 6: per run_id by default; SFE canary: identical per arm; Tyche v2: one stream per run) and
  none is declared per arm. REP-07 validator must refuse undeclared sharing.
- Tie handling is never declared: strict `>` tournaments (WSE), strict archive insertion (Apollo,
  Theseus), sentinel-rejecting greedy walks (PROTEUS-46), tie-accepting climbers (D-5 HC), and fully
  tied selections that silently become drift (D-13). The policy object must name the tie rule and the
  log must count ties.
- Recombination rate is a hidden default (Apollo 0.0; Proteus splice 0.05 with self-splice fallback).
- Readout on training batteries reported as competence (Deep Frontier, WSE best_train_max).
- Zero hits typed as unreachable (reachability.classify, states TARGET_UNREACHABLE; Tyche parity-3).
- Mutable steering files and readouts that rewrite tracked JSON from inside the loop (Deep Frontier).
- Host / platform assumptions: Windows path separators (D-5 m1.py), cwd-dependent git shell-outs in
  tests (Theseus), LLM servers with VRAM checks and API keys in the evolution loop (Apollo), Postgres
  heartbeats (Apollo, Ergon learner).
- Instrumentation by monkeypatching module globals (Ergon Credit).

-----------------------------------------------------------------------------------------------
## 5. Tests run this session (all from a temp cwd unless stated; PYTHONDONTWRITEBYTECODE=1,
## pytest -p no:cacheprovider; `git status --porcelain` empty after every run)

    file(s)                                                        result
    tyche/tests/test_v0.py::{lexicase_keeps_specialists,           5 passed
      mutations_valid_and_ids_stable}, test_v1.py::fuse_equals_
      concatenation, test_v2.py::{compose_is_b_of_a, strict_
      lexicase_with_no_eligible_returns_nothing}
    proteus/tests/{test_v0_6_gates,test_v0_5_gates,                51 passed
      test_holm_and_symmetry,test_mutation}.py
    SerendipityFoundryEngine/tests/test_sfe_nk_landscape.py        50 passed
    archaeon/tests/{test_wse,test_campaign3_machine}.py            31 passed
    agent_d5_blind/substrate/test_equivalence.py (script)          PASS, 2402 programs x 128 inputs
    theseus/synth/tests/test_synth_v0.py                           temp cwd: 7 failed / 3 passed
                                                                   (git show needs repo cwd);
                                                                   repo cwd (read-only git): 10 passed
    NOT run: archaeon/tests/test_frontier_suppression_logging.py (step() can write tracked files via
    charge_pursuit / run_due_readouts); test_campaign2_machine.py (host cacert dependency); segment
    and scheduler self-tests (campaign data + multi-generation runs); Ergon gen3, Apollo (no tests),
    NPE scheduler (no tests), C4 self-tests (gate-coupled).

-----------------------------------------------------------------------------------------------
## 6. Files read (source and tests opened for this digest)

archaeon/wse/{evolve,reachability,economics,states,corridor,ssf,controls}.py (evolve, reachability,
economics in full; others head/structure); archaeon/campaign2/{runner,c2base}.py (heads);
archaeon/campaign3/ladder.py (head); archaeon/campaign4/{c4_01,c4_05,launch_gate}.py;
archaeon/campaign6/{segment.py (full), pressure/schedules.py (head)}; archaeon/frontier/{scheduler.py
(full), allocation.py (full), loop.py (head), capabilities.py, OPERATOR_EXECUTION_AUTHORIZED.json};
archaeon/tests/{test_wse,test_frontier_suppression_logging,test_campaign2_machine,
test_campaign3_machine}.py (structure); proteus/foundry/{lineage,prng,grammar(parts)}.py;
proteus/v0_5/{run_crucible,kernel}.py (heads), v0_6/equilibrium.py (head), v0_4/holm.py (head),
v0_5/PREREG_V0_5.md, v0_6/PREREG_V0_6.md (s5); proteus/round2/falsifier_46.py:25-135;
proteus/tests/test_v0_6_gates.py; apollo/src/{blackboard_evolve.py (loop, descriptor, archive),
apollo.py (head), novelty.py}, apollo/scripts/o1_enumerate.py:1-200; tyche/{ecology.py (full),
lens.py:420-544, v2/run_v2.py (head, lexicase_trace, RunV2 init), v2/history_v2.py (full),
tests/test_v0,v1,v2 (relevant)}; theseus/synth/{rulers.py (full), run_v0.py (grep), README.md,
tests/test_synth_v0.py}; agent_d5_blind/{learner/m1.py, navigators/m0.py,
reachability_oracle/reachability.py, mutation/physics.py, substrate/test_equivalence.py} (full);
ergon/gen1b/gen1_run.py:1-210; ergon/gen3/p3_common.py (full); ergon/learner/archive.py (head);
roles/Nestor/campaigns/z80atlas-2026-09-19/{scheduler.py:1-260, producer.py:1-60};
SerendipityFoundry/SerendipityFoundryEngine/sfe/{executors.py (full), canary.py:1-170},
tests/{conftest.py, test_sfe_nk_landscape.py (structure)}; SerendipityFoundry/wow/
WOW_ARCHAEOLOGY_REVIEW_PACKET.txt:1-140; selection_boundary/SELECTION_BOUNDARY_RESULTS.txt:1-80.
Locators: docs/phase3/design/OPUS-5.5/{RSE_ARCHITECTURE.md, requirements.jsonl, ENGINE_PORTFOLIO.md
(grep), evidence/sis-a.md:1-200, sis-c.md:88-160, tan-b.md:110-300, atl.md / idx.md (grep)};
docs/phase3/intake/tantalus/seats/Theseus.md (s8, s13-14).
