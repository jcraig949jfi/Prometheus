# Aphrodite -- Phase 3 intake dossier

Seat: Aphrodite (RSI / improvement-process science seat)
Crawler: Tantalus (worker)
Tree: origin/main at 21a47402a (worktree F:\Prometheus-worktrees\tantalus-phase3-intake)
Date: 2026-10-01

Summary. Aphrodite was created 2026-09-17 on host M4 (harry1) on an operator commission to "research RSI and
build small prototypes" and was chartered 2026-09-18 (APHRODITE-08) to determine experimentally whether an
improvement process got better AT IMPROVING, as opposed to accumulating memory, selection, compute, evaluator
exploitation or benchmark specialisation. In 14 days it produced 147 commits under roles/Aphrodite/ (679 files),
all inside that directory: stdlib-only Tier-1 toys (E1-E4 RSI toys, S1-S4 swarm boundaries), a Tier-2 synthetic
assay-calibration programme (Campaign 0/0B/0C), a frozen-but-never-run real-LLM transplant design (Campaign 1), and
-- the bulk of the work -- a deterministic, offline, CPU-only "local engine" in which an improver searches an integer
DSL of folds ('fold', init, body, final) and the inherited object is a LIBRARY (an ordered enumeration prior over the
grammar), measured in metered search "charges" against a pristine baseline, shams and a hostile tribunal. Over 23
frozen amendments the seat recorded one accepted positive transfer (S4 ABSTRACTION_TRANSPLANT = YES: a derived
schema (acc + {H}) that equals the hand-written positive control), repeated BOUNDED_RSI = NO / UNTESTABLE, and a final
mechanism positive (A23 G1_RECURRENT_STEPPING_STONE = YES) under CONSTRUCTED recurrence in which the donor mostly
recovers the planted motif. The decisive structural fact for Phase 3: across the entire programme the IMPROVER
(mutation operators, derivation by least-general-generalisation, selection rule) was IMMUTABLE code; the only things
that ever changed were (a) four ES hyperparameters in one Tier-1 toy and (b) a data library that reorders an
enumerative search. "Recursive self-improvement" in the code is therefore library inheritance plus, from 2026-09-27,
a designer-added composition move; level-2 improver change (the seat's own "V5") was never testable. The seat's own
late syntheses say this plainly and are unusually self-critical; they are nonetheless the seat's claims, not
verified results.

----------------------------------------------------------------------------------------------------------------
## 1. Identity, charter and pivots

- Canonical name Aphrodite; no aliases found. Host M4 (harry1), comms via EW_DB_HOST=192.168.1.202; never ran on M1
  per its own records [CLAIM] (STATUS_REPORT_2026-10-01.md s3). Model: Opus 5 at start, claude-opus-5-5 by 09-30
  [CLAIM].
- 2026-09-17: seat created (8b54a74b8), base role adopted; operator directive verbatim at
  roles/Aphrodite/prompts/2026-09-17_rsi_research/OPERATOR_DIRECTIVE.md: research RSI, build "small prototypes ...
  with simple python tests", citing a GLM "Infra Agent" article and an AI-assistant summary of "RSIAgent",
  "Dream-RSI", "ModularRSI" (the seat flagged the latter as unverified secondary text) [IMPL, file read].
- 2026-09-18: charter ADOPTED (3d86dc292), verbatim in prompts/2026-09-18_charter/ and quoted in
  RESPONSIBILITIES.md s0. Binding evidence hierarchy TIER 1 (analytic/CPU toys) / TIER 2 (apparatus calibration) /
  TIER 3 (real-model designs) / TIER 4 (real-model evidence); "NO SILENT PROMOTION"; the seat holds no Tier-4
  evidence [IMPL, RESPONSIBILITIES.md s1].
- Pre-charter seat file kept at superseded/RESPONSIBILITIES_pre_charter_2026-09-18.md.
- Pivots (all dated, from STATUS.md UPDATE blocks and commit log):
  1. 09-17..18 Tier-1 toys -> Tier-2 assay calibration (Campaign 0) -> Campaign 1 real-LLM design FROZEN 09-19,
     never executed (blocked on contracts from Archaeon/Harmonia/Vivarium and benchmark receipts from
     Nestor/Archaeon).
  2. 09-21 operator directive "the cheapest self-contained local engine capable of executing the frozen Campaign 1
     causal structure" (prompts/2026-09-21_local_engine/) -> engine v0 (membrane) -> v1 (endogenous discovery).
  3. 09-22 Tier 3A-3C: the mutable object becomes a proposal library ("improver heredity").
  4. 09-23..24 S1-S4 causal chain (identity -> fair selection -> endogenous abstraction -> transplant); S4 accepted
     by operator 09-24; "BOUNDED_RSI NOT YET ESTABLISHED" ruling.
  5. 09-22 PARKED by operator; 09-26 hold lifted, A16/A17 BOUNDED_RSI campaign; "experiments no longer managed via
     Aporia or Cyclops".
  6. 09-27 Frontier programme (spikes K1-K8, prior-art raids). Operator renamed the line 09-27 from "RSI" to
     "abstraction compounding" (STATUS.md 09-28 block) -- a scientific pivot driven by the seat's own finding that
     its improver could not recurse.
  7. 09-28 ARC3 portfolio (A20-A23, workers W1-W8); merged to main 067fce3af on 09-30.
  8. 09-30 operator-directed "inference harvest": Aphrodite's RSI ladder applied to Prometheus itself (lab scale).
  9. 10-01 STATE READY, awaiting Aporia dispatch; T51 authorised but not started.
- Relationships: Archaeon (task ecologies; contracts #452/#492/#534), Harmonia (metering, delegations #490/#533
  closed by #928), Vivarium (sandboxes), Nestor and Archaeon (benchmark executors on M1/M2), Ananke (PTE suggestion
  borrowed for novelty ruler, CROSS_ENGINE_MECHANISMS.md), Crius (existence-vs-accessibility split), Aporia
  (dispatcher under CWO-C). Atlas: roles/Atlas/inference_harvest_2026-09-30/ATLAS_CROSS_ENGINE_SYNTHESIS_2026-09-30.md
  line 487 lists Aphrodite as "Not covered"; roles/Atlas/SOURCES.md line 13 "M4 (Aphrodite's host; not yet
  surveyed)". Atlas is therefore not a usable locator for this seat [IMPL].

## 2. Engine/system inventory

All code lives under roles/Aphrodite/; `git ls-files | grep -i aphrodite` outside that tree returns only two
Archaeon prompt files [IMPL]. No engine tree elsewhere.

E-A. RSI toys E1-E4 (science/rsi/, Tier 1, 09-17). Stdlib Python. e1_feedback.py (attributed vs scalar feedback),
     e2_self_improver.py (a (1+lambda)-ES that optimises its own 4 hyperparameters), e3_memory.py (verified vs
     unverified memory distillation, COLOR/SHAPE worlds), e4_guard.py (leak detector). run_all.py, analysis.py,
     ledgers/*.jsonl, VERDICTS.json. ~831 s on 7 workers [CLAIM, RESULTS_2026-09-17.md].
E-B. Swarm damage-boundary toys S1-S4 (science/swarm/, Tier 1, 09-18). Branching contagion, best-of-k with
     exploitable tail, exploiter invasion a* = g/(1+g), majority/herding. models.py, sims.py, analysis_swarm.py.
     111.6 s. Stopped by operator-directed scope rule ("extends the frozen swarm toys" forbidden) [IMPL,
     RESPONSIBILITIES s3].
E-C. Campaign 0 / 0B / 0C assay (science/campaign0/, campaign0c/, Tier 2, 09-18). worlds.py is a logistic
     generative model of lineage observations with planted truths (W1 true transfer, W2 memory cheat, W3 compute
     cheat, W4 specialisation, W5 transferred module, W6/W9 nulls, W7 worker transfer, W8 mixed); assay.py is blind
     to the world table. 14,400 jobs / 41,400 rows (C0); 10,800 pathology jobs (C0B); 15,200 experiments (C0C)
     [CLAIM, RESULTS files].
E-D. Campaign 1 throughput benchmark (science/benchmark/: bench.py, economics.py, freeze_bundle.py, run_frozen.py,
     BENCHMARK_SPEC.md FROZEN v2). Intended to run Qwen3-8B / Gemma 3 4B / Llama 3.2 3B on M1/M2 via Nestor and
     Archaeon, on four procedural families. The only real-LLM-facing code in the seat. Whether receipts were ever
     produced: UNKNOWN (STATUS lists them as blocking) [UNKNOWN].
E-E. The local engine (engine/, 09-21 onward; ~12.5k lines of Python in engine/*.py plus A19-A23 subdirectories,
     accel/, diagnostics/, tests/). This is the substantive system. Sub-versions:
       - engine.py v1 (1,018 lines): WORKER / IMPROVER / VAULT / EVALUATOR membrane, Escrow (charge counter),
         Recipient loader, Lineage.evolve, Tribunal, enumerative synthesis (PRIMITIVES add, sub, mul, fdiv, mod,
         gcd, powr; 3 integer terminals; size <= 4; 40,000 candidate cap) [IMPL].
       - slice2c.py / basis_v2.py / basis_v3.py: grammar v2 "size-indexed symmetric" repair, helper search.
       - basis_v4.py: grammar G4 ("g4-imperative-v1") of integer folds; ORGAN macro sha 5488abb9...; search
         lengths 4-9, extrapolation 20-60, stress 200 [IMPL].
       - organ_extract.py, certify_*.py: reachability / expressivity / basis-separation / third-family
         certificates (JSON receipts in engine/).
       - improver.py (AMENDMENT 9, fe1ca23c6): Library (MUTABLE data) + immutable ops; tier3b.py, tier3c.py,
         tier3d.py (LGG schema derivation), tier3e.py (novelty key), meta_tribunal.py.
       - identity.py, s1_fixtures.py, s1_gate.py, cert.py, s1_local_gate.py: whole-program behaviour identity.
       - fair.py (keyed common random numbers), s2_gate.py, run_s3s4.py (S3 derivation + S4 transplant).
       - a16.py, a17.py (879 lines; exact-fast Q2, checkpointing), a18.py (fast_cost), a18_c1.py, a19_c2.py,
         a20_c3.py, a21_c3r.py, a22_c3r2.py, a23_c3r2c.py; tribunal_t4.py (443 lines, RB-2); ruler v2
         (science/compounding/rb1/).
       - conformance.py: differential gate between search evaluator and emitted-artifact evaluator (21,600
         comparisons; later 803,480 for W5) [CLAIM].
       - accel/: fasteval.py (admitted by a 288k-pair equivalence gate [CLAIM]), parallel_tier3c.py, RunPod and
         Azure canary scripts. STATUS 09-26: "RUNPOD/AZURE_UNAVAILABLE_TO_APHRODITE" [CLAIM]; no evidence a cloud
         run produced science.
E-F. Forensic spikes and worker studies: science/frontier/spikes/k1..k8 (+ JSON), science/compounding/rb1..rb6,
     science/arc3/w1..w8, con1, c3r2_feasibility, second_gen. Bounded analytic or short search runs.
E-G. Bounded RSI news monitor (monitors/news/): weekly scheduled task AphroditeNewsWatch on harry1 that runs ONE
     headless Claude pass in a scratch dir, validated deterministically by monitor.py; inspect <= 8, admit <= 3;
     4 passes recorded in passes.jsonl [IMPL]. An LLM-in-the-loop literature feed, not science.
E-H. Inference harvest (harvest_2026-09-30/): six design/analysis documents plus evidence from four read-only
     history-analyst subagents and two critics. Lab-scale; no engine.

## 3. Code architecture and dataflow (engine, from code read)

engine.py v1 [IMPL, engine.py lines 1-200, 575-640, 900-1018]:
- The "artifact" is a JSON map of five Python source strings (search, verify, allocate, memory, evidence),
  canonicalised and sha256-hashed (Artifact.canonical). A Recipient execs these sources in a restricted loader
  namespace (math, re supplied).
- The base image's search module returns hand-written solvers for arith, sortkey, strops; headroom families
  numtheory (gcd + lcm) and modexp are unsolved.
- Lineage.evolve: per generation, development tasks = DEV_PER_FAMILY = 2 instances of each of 5 families; variants
  = {unchanged, N_CANDIDATES in {2,3}, STRICT toggled} plus an optional SYNTHESIS variant that appends a
  discovered solver function's SOURCE TEXT to the search module; every variant is scored on dev tasks (1 escrow
  charge per task); best score wins. FROZEN_GENERATION = 8.
- The improver (_variants, _synthesis_variant) is fixed code; "it never touches the escrow". The synthesis is
  bottom-up enumeration with observational-equivalence pruning; _structural_search adds a helper h(x, y) built from
  depth-2 update expressions.
- Code/doc agreement: the README's own measurement shows lineages were CLONES (1 distinct artifact across 10
  seeds) because dev instances were seeded by dev_seed + generation, independent of lineage; later fixed via
  lineage_id-keyed dev_entropy (AMENDMENT 3; visible in evolve()) [IMPL].

basis_v4.py G4 [IMPL]: programs ('fold', init, body, final): acc = init; for v in xs: acc = body(acc, v, first,
last); return final(acc, first, last). INIT_SPACE = atoms {0,1,first,last} to depth 1 (116 expressions), BODY_SPACE
= atoms {acc, v, first, last, 0, 1} to depth 2 (10,842), FINAL_SPACE depth 1 (180). Full fold space ~2.26e8
(116 x 10,842 x 180; my arithmetic from the code, not a recorded number). Values bounded (10^18 in engine v1,
10^40 accumulator ceiling in G4 per Review 11). Task generators produce lists of length 4-9 of ints 2-99 with
sum/product/gcd/sum-of-squares plus a first/last/param adjustment.

improver.py (Tier 3) [IMPL]: "A proposal library is DATA ... it cannot express anything G4 cannot. Every improver,
pristine or modified, falls back to the complete G4 enumeration, so expressive power is identical by construction.
Everything else -- the mutation operators, the fitness rule, the selection rule -- is IMMUTABLE machinery and is
never part of the artifact." Library.candidates yields entries' (init x body x final) products, then the full G4
fallback. Operators: op_specialise_from (observed successful bodies), op_antiunify_pair (LGG of two), op_reorder,
op_drop; sham_library built from FAILED bodies. search() charges 1 per candidate program and stops at the first
program consistent with all dev examples.

Dataflow (Tier 3 and later): donor OBSERVE families -> search with library L -> certified successes -> derive
schemas by anti-unification (single hole {H}) -> candidate libraries -> paired VALIDATE (keyed CRN, fair.py) on
held-in validation families -> select -> freeze library bytes -> TRANSPLANT into fresh recipients on unseen
TRANSFER families -> tribunal-qualified solves and charges vs PRISTINE, shams, no-composition and OFF controls.

Where code and docs disagree (recorded by the seat itself, review/ARC3_MERGE_REVIEW_PACKET.md s5) [CORRECTION]:
- engine/run_s3s4.py line 391: S4 condition 4 "hostile_evaluation" = True (constant); line 420: condition 8
  "no_donor_state" = True (constant). I read both lines; they are literal constants with comments [IMPL].
- run_s3s4.py L245/L317: the POSITIVE_CONTROL schema (acc + {H}) equals the derived schema, so the positive
  control did not discriminate in S4.
- a16.py L490 and a17.py L581: donor adjudication validity constant True.
  The seat recorded these (TH-021, D55) and did not relabel S4; relabelling is operator-level.
- T4 query window differs from dev for ~1.7% of families (W7); A23 ran on the unrepaired T4 (bridge re-score
  T47 not done) [CLAIM].

## 4. Claimed computational primitive vs actual mechanism

E2 "self-referential improver" (Tier 1).
- Label: recursive self-improvement; the optimiser of generation g is the one generation g-1 produced.
- Smallest mechanism: a (1+lambda)-ES on 6-D sphere/rastrigin/rosenbrock/ellipsoid whose parameter vector theta =
  (log10 sigma0, growth a, lambda, patience) is itself optimised by the same ES with META_BUDGET = 60 evaluations
  [IMPL, e2_self_improver.py lines 1-60].
- Could express: hyperparameter self-tuning (4 numbers). Nothing structural.
- Ruler aimed at: a "recursion dividend" (held-out gain of recursive vs fixed-meta) and a planted accounting exploit
  (leaky arm).
- Could it perform it: barely; theta_0 moved ~0.01 in a unit cube while the exploit needed 0.033 (calibration
  ledger row 2, the seat's error) [CORRECTION]. X1: 42.5% of random single perturbations matched the recursive
  median at g1 [RESULT-UNVERIFIED].
- Shortcut distinguishable: yes via the independent Counter (leaky arm caught every time in X2) [RESULT-UNVERIFIED].

Engine v1 "endogenous discovery".
- Label: an improver capable of endogenous discovery; seat-labelled mechanism class PROGRAM_COMPOSITION, explicitly
  NOT ALGORITHMIC_STRUCTURE ("the search composes declared primitives and invents no control flow") [IMPL,
  README.md].
- Smallest mechanism: enumerate integer expression trees over 3 parsed integers, accept the first that matches 2 dev
  instances, append it as a solver.
- Ruler: held-out instances in a fresh recipient. It caught the numtheory shortcut a*b + 1 (correct exactly on
  coprime pairs; held-out 0.635 vs 6/pi^2 = 0.608) only through a per-class test; the aggregate test PASSED it
  [RESULT-UNVERIFIED].

Tier 3 / S1-S4 "improver heredity" / "endogenous abstraction".
- Label: bounded recursive self-improvement; abstraction as improver heredity.
- Smallest mechanism: an ordered list of (init-set, body-set, final-set) string triples placed in front of an
  exhaustive enumerator; derived by single-hole anti-unification over the bodies of programs the donor itself found;
  selected by paired savings on 2-3 validation families [IMPL, improver.py; Review 11].
- Could express: a reordering prior over an already-complete finite search space. Capability gain is by definition
  budget-relative (the seat's own frontier synthesis s7 and K4: PRISTINE finds every L1-only solution at 8x-3,527x
  more charges) [CLAIM].
- Ruler aimed at: whether a library derived by the donor (not handed to it) transfers competence to unseen-body
  families in a fresh recipient beyond PRISTINE and shams.
- Could the organism do it: it derived (acc + {H}); this is content-identical to the positive control the seat
  wrote, so "derivation" not "new mechanism" is the strongest reading (Review 11 s0) [CLAIM].
- Shortcut: tribunal qualification + generator qualification cut false positives to 0 in Tier 3C [RESULT-UNVERIFIED];
  but the tribunal certifies exactly commutative bounded folds = G1's own span (frontier s4) -- the admission ruler
  and the abstraction under test were the same mathematical object [CLAIM, later analysis].

A18-A23 "abstraction compounding" / "recurrent stepping stone".
- Label: an inherited abstraction becomes a stepping stone to new capability; compounding.
- Smallest mechanism: as above plus a treatment-blind composition move wrap(S, op, atom) -- a designer edit to the
  improver (W4: "composition is already an improver edit") -- in depth-3 world W5 (465,954 bodies) with tribunal T4.
- Ruler: a ladder REPRESENTABLE -> REACHABLE -> SELECTED -> SOLVED -> REUSED -> CAPABILITY with sign tests vs
  G1_NC / PRISTINE / OFF.
- Could the organism do it: A23 YES 3/3 GENERIC, but the selected composition literally EQUALS the planted motif in
  G1 7/8 and in shams 5-7, and VALIDATE was constructed to contain 2 instances of that motif (a22_c3r2.py docstring
  item 3) [IMPL + CLAIM]. The positive therefore measures selection among ~60 candidate compositions from 2
  validation families, with transfer to new instances of the same constructed structure.
- Distinguish from shortcut: partly. Shams succeed at the same rates (genericity), REUSED_OTHER ~0 (structure-specific),
  capability ratio is a walk-cliff quantity (W2) [CLAIM].

## 5. Representation/state architecture

- Engine v1: artifact = five Python source strings; worker state = per-task-key answer cache (memory module), which
  is the "STATE" foil (memory-only arm 0.00 on fresh instances) [IMPL/CLAIM].
- G4/W5 world: a program is a 4-tuple of expression strings; no loops other than the single fold, no conditionals,
  no variables beyond acc, v, first, last, a trailing parameter; integer arithmetic with guards [IMPL].
- Library: ordered list of entries; schema = body template with one hole {H} (two-hole tested in RB-6, inert).
  Identity: behaviour vector over a frozen battery (identity.py) plus class certificates (cert.py), after global
  behaviour identity FAILED permanently (S1 runs 1-3) [CLAIM].
- No learned parameters, no neural state, no recurrence across tasks except library order.

## 6. Organism/player architecture

There is no organism in the A-Life sense. The "worker" is deterministic Python (engine v1) or a fold interpreter
(G4); the "improver" is fixed enumeration + LGG + paired selection; a "donor lineage" is one improver run on one
supply; the unit of replication is the donor replicate (n = 8-12). The seat deliberately chose "a code worker and
no model" so that machinery vs cached state are separable by construction (README "Why a code worker") [INTENT].
Self-modification: the worker's code is rewritten by appending solver text (v1) or by swapping the library (Tier 3+);
the improver's code is never rewritten by the system.

## 7. World/environment architecture (toy scale, precisely)

- Engine v1: 5 families, prompts with 2-8 small integers or 5 words; dev 2 instances/family; tribunal 200
  instances/family.
- G4: integer sequences length 4-9 (search), 20-60 (extrapolation), 200 (stress); element values 2..30 (S1 domain)
  or 2..99; query 1..97. Families are single fold programs; catalogs of a few to ~32 families per experiment (e.g.
  improver.py: 4 META-DEV + 4 META-TRIBUNAL). K1 census: 10,500 drawn witnesses -> 737 admissible -> 7 genuinely
  non-G1 (0.07%) [CLAIM].
- W5: depth-3 bodies (465,954); T4 yields ~29 non-additive solvable families per 1,000 draws vs 0.76 under Tier-3
  tribunal [CLAIM].
- Nonspatial, fully observed, deterministic, single-agent, no resources/ecology, no delayed consequences beyond the
  fold, no environmental change (the Campaign 1 regime shift was never run). The RB-5 note: the fold DSL "cannot
  express independent worlds (EC/OEIS)" without integer literals, a lag register, a position atom [CLAIM].
  This is a small, finite, enumerable toy world.

## 8. Search/training/adaptation mechanism

- Bottom-up enumerative synthesis with observational-equivalence pruning (v1); exhaustive walk of G4/W5 in library
  order with first-consistent-program acceptance (Tier 3+). Escrow 250k charges per cell (frozen) with ladders to 10M
  for PRISTINE.
- Selection: paired, keyed common random numbers; median/mean savings; optional 2-step lookahead (RB-6 V2).
- Bottlenecks named by the seat [CLAIM]: (a) supply -- tribunal admits ~only additive folds; (b) access -- derivation
  only abstracts over coverage, so inheritance adds 0 derivable novel schemas (467 = 467, K3); (c) ruler -- novelty
  key false positives (conjugates, abs() junk) and zero credit for compounding; (d) starved derivation -- a donor
  observes median 1-2 of 4 OBSERVE families and derives median 0 schemas (W4 Probe P-A); (e) coverage cliff at
  151,920 members and 83.9M fallback blocks makes solve probability bimodal in escrow (W2).
- Collapse modes: lineage cloning (v1); degenerate dynamics with init in {0,1} (acc // x -> 0); overflow under
  stress; validation resting on ONE family (C2); P15 entry-finals rule shrinks entries 37x but covers 8.9% of transfer
  finals (canonical curriculum-overfitting lever, W4 Probe P-B).

## 9. Measurement/ruler stack

- Escrow charges (candidate-program evaluations) as the primary cost endpoint; WALL-CLOCK contaminated in slice 4 and
  Tier 3A and "permanently marked" [CLAIM, STATUS.md].
- Tribunal (engine.Tribunal, meta_tribunal.py, tribunal_t4.py): fresh instances from a disjoint entropy domain,
  metamorphic permutation-invariance, extrapolation/stress lengths, counterexample shapes.
- Generator qualification (Tier 3C): 200 draws per candidate size, dev battery sized until 95% upper bound on
  surviving wrong classes < 0.05; rejected 3/9 families [CLAIM].
- Conformance gate (search evaluator vs emitted evaluator), green before runs; S1 run 1 found 4,501 mismatches from an
  output-ceiling defect that the standing 21,600 sweep had missed [CORRECTION, Review 11 s3].
- Identity: source / structure / behaviour; class certificates over B1 u B_CERT (20,000 fresh inputs).
- Novelty: tier3e key -> ruler v2 (rb1; removes 574 false positives, chance base rate 16% in G4, 23-25% in W5) ->
  retired scalar in favour of J1-J4 + EQUAL/REFINES/COMPOSES tag (ARC3 s7) [CLAIM].
- Verdict decomposition V1 efficiency, V2 capability, V3 compounding, V4 novelty, V5 improver change (frontier s8).
- Statistics: Wilson bounds, sign tests (A23 p = 0.0078), Holm (with a ledgered floor error), paired CIs; lineage as
  the unit (charter).
- Blind spots: the same mathematical object admits tasks and constitutes the abstraction (frontier s4); constant-True
  gate conditions (TH-021); positive control identical to the derived artifact; capability is budget-relative to a
  walk-cliff instrument; validation constructed to show the motif (A22/A23).

## 10. Baselines and controls

PRISTINE (empty library, full fallback), INHERITED/L1 start library, shams (failed-body libraries, sign
re-expressions, frequency-matched schemas, random single-hole schemas), G1_NC (no composition), OFF_0 (schema with
0 genuine motifs), memory-only arm (v1), positive control artifact (_pc_numtheory/_pc_modexp; POSITIVE_CONTROL
(acc + {H})), heterogeneous null W9 (C0 AMENDMENT 1), negative membrane fixtures (tests/test_membrane.py, 12 tests)
[IMPL/CLAIM]. Notably, in Tier 3C two SHAMS solved both unseen-body families 16/16 while the evolved donor did
nothing -- the control did the experiment (Review 10 s3) [RESULT-UNVERIFIED].

## 11. Historical experiment campaigns

Labels are on the historical record only.

| id | date | question | organism / world | measurement | arms / scale | reported result | later reinterpretation | label |
|---|---|---|---|---|---|---|---|---|
| RSI toys E1-E4 (science/rsi/; 9c173fb37, 07fcc2509) | 09-17 | feedback attribution; recursion dividend; verified memory; leak detector | ES / bit-world toys | prereg CI rule | 15 calls | 9 SUPPORTED, 3 REFUTED, 3 INDETERMINATE | E2 gate barely reachable (seat error); run_all point-estimate verdicts superseded | MIXED |
| Swarm S1-S4 (science/swarm/; acc40e902) | 09-18 | boundary formulas for contagion, best-of-k, exploiters, herding | analytic sims | interval gates | 111.6 s | 8 SUPPORTED, 5 INDETERMINATE, 1 NOT_EVALUABLE after 2 analysis-code fixes | tolerance rule made SUPPORTED near-impossible (ledger); herding formula recalled wrong | MIXED |
| Campaign 0 (f0e04de11, 50782371c) | 09-18 | does the assay recover planted truths | synthetic logistic generator the seat wrote | exact flag-set recovery, Wilson | 9 worlds x L 16/32/64 x R 200 | PASS; L = 64 required | tier 2 only; generator and assay from same author | REPORTED POSITIVE |
| Campaign 0B (8f869455d, 3816a6855) | 09-18 | stress under heavy tails, sign changes, jackpots | same | same | 10,800 jobs | FAIL as preregistered (power under jackpot 0.2-0.28) | calibration held | REPORTED NEGATIVE/NULL |
| Campaign 0C (c21e4aab9, d9d6fecbd) | 09-18 | secondary endpoint | same | G1-G4 | 15,200 | PASS | -- | REPORTED POSITIVE |
| Benchmark / Campaign 1 | 09-18/19 | real-LLM transmissible improvement | Qwen3-8B etc. | transplant assay | 64 lineages planned | FROZEN, UNRUN | blocked on contracts | UNKNOWN |
| Engine v1 qualification + slice 2B/2C (engine/QUALIFICATION_*, SLICE2B/2C_RESULTS) | 09-21 | can the improver discover headroom solvers | v1 expression grammar | held-out per class | 200/family, 10 seeds | modexp found; numtheory shortcut; lineages clones | SLICE2B_VALIDITY_SCAR.md; grammar asymmetry repaired in 2C | MIXED |
| Slice 3 / slice 4 (SLICE3/4_RESULTS) | 09-22 | direct competence reuse; structural search leverage | G4 organ vs scratch | charges | -- | DIRECT_COMPETENCE_REUSE NO; STRUCTURAL_SEARCH_LEVERAGE YES at equal expressivity | wall-clock contaminated (charges unaffected) | MIXED |
| Tier 3A/3B/3C (TIER3*_RESULTS; AMENDMENTS 9-11) | 09-22 | bounded RSI via improver heredity | proposal library | qualified solves, FP/recipient | 16 recipients, 8 shams | BRSI NO; 3A control INVALID; 3B 4.688 FP/recipient; TRANSFERABLE_SEARCH_LEVERAGE YES_LOCAL 47x/345x | shams solved unseen families in 3C | MIXED |
| S1-S4 chain (AMENDMENTS 12-14; 65edc1251) | 09-23/24 | whole-program identity -> endogenous abstraction -> transplant | G4 LGG | 8 conditions | 5 unseen-body families, 16 recipients | S1 global FAIL; S2 PASS; S3 YES; S4 YES (break-even 41.2 < 64); operator ACCEPTED | conditions 4 and 8 constant True; positive control = derived schema (TH-021) | REPORTED POSITIVE |
| A15/A16 (AMENDMENTS 15-16) | 09-24 | BOUNDED_RSI G1 -> G2 | G4 catalogs | R1 novelty | -- | NO / UNTESTABLE_CATALOG; E1/E2 UNTESTABLE (time) | -- | INCONCLUSIVE |
| A17 (pivot/..._2026-09-26.md) | 09-26 | same, second execution | catalogs A/B | E0-E4 | 48 min | E1 NO; E2 UNTESTABLE; S1_NECESSITY SUPPORTED | frontier: NO is "close to a theorem about the setup" | REPORTED NEGATIVE/NULL |
| Frontier spikes K1-K8 | 09-27 | why the catalog collapses; access vs grammar | analytic | censuses | 10,500 draws etc. | supply x access x ruler conjunction; composition move opens 77 G1-composing schemas | -- | MIXED |
| RB-6 lever check | 09-27 | do improver levers matter | L1 start, 3 supplies | savings | killed at 30-min cap | levers inert | W4: upstream starvation, not lever weakness | REPORTED NEGATIVE/NULL |
| A18 C1 | 09-27 | compounding | W5 | ladder | -- | UNTESTABLE (supply; seat's screening flaw) | -- | INCONCLUSIVE |
| A19 C2 | 09-28 | stepping stone | W5/T4 | ladder | n = 8 | G1_STEPPING_STONE NO (4 vs 0, p 0.0625); CON1 forensic existence proof | W6: selection/validation valley; CON1 credit belongs to G1's extensional class | REPORTED NEGATIVE/NULL |
| A20 C3 / A21 C3R / A22 C3R2 | 09-28 | reuse-controlled assay | W5/T4 | ladder | n = 8 | UNTESTABLE / INVALID_DESIGN_DEFECT (inert identity wraps) / UNTESTABLE | 3 of 4 consecutive assays failed on design or supply | INSTRUMENT FAILURE |
| A23 C3R2-CONFIRM (engine/A23_C3R2C/) | 09-28 | same, confirmation | W5/T4, constructed recurrence | ladder, sign tests | n = 10 of 12 | G1_RECURRENT_STEPPING_STONE YES; GENERIC 3/3 | donor mostly recovers planted motif; capability budget-relative | REPORTED POSITIVE |
| ARC3 workers W1-W8 | 09-28 | attack principal's readings | mixed | -- | -- | several positions changed; disagreements kept | -- | MIXED |
| Inference harvest | 09-30 | is Prometheus improving at improving | git/comms history | activity vs result ratios | 4 analysts + 2 critics | no rung above L0 established; operator is the main improver | -- | REPORTED NEGATIVE/NULL |

## 12. Reported results and later corrections (timelines)

1. Endogenous numtheory solver: claim "discovered" -> held-out 0.635 -> identified as coprime-only shortcut a*b+1 ->
   per-class test committed RED; aggregate test had passed it. Status: dev-distribution exploitation, recorded.
2. Lineage independence: 64 lineages -> 1 distinct artifact (pseudoreplication) -> per-lineage entropy (AMENDMENT 3).
3. S1 global identity: PASS sought -> 3 runs FAIL (ceiling-crossing step depends on inputs) -> operator ruling
   GLOBAL_BEHAVIOR_IDENTITY = FAIL permanently, class certificates instead. Also an engine defect (output ceiling) found
   only here.
4. S4 transplant: YES, accepted 09-24 -> 09-28 packet s5: two of 8 conditions constant True, positive control
   equals derived schema; no relabel. Current status: historically accepted, structurally weakened.
5. BOUNDED_RSI: NO (Tier 3) -> NO/UNTESTABLE (A15-A17) -> frontier: NO is near-theorem under DSL + mechanism +
   ruler; "the limit is task supply" (09-26) declared WRONG as stated (frontier s0) [CORRECTION].
6. Capability of G1: "capability gain" -> K4: an enumeration-order prior; vanishes at ~12M budget.
7. CON1: ">= 190x" capability -> W2: generic cliff ratio; survives in reduced form (route-sufficient, not
   G1-specific).
8. A23 YES -> principal attack in the same result: selected = planted motif literally in most replicates.
9. Novelty base rate 16% (G4) -> 23-25% in W5 (W3/W7).
10. "Natural T4 world is bimodal" -> bimodality comes from the instrument (escrow x walk cliff).
11. Lit claim "compute-matched multi-seed transplant appears not to exist" -> Hyperagents ran a 5-run transfer;
    corrected (calibration ledger).

## 13. False-positive archaeology

- Ruler-induced: novelty key flagged (acc - {H}) NEW on 7/161 instantiations (sign conjugate of G1) and acc-free junk
  ({H} + v on (v + v)); K7: 24/31 "non-G1" qualified families are extensionally G1 on the task domain.
- Tribunal-induced: Tier 3B 4.688 false positives per recipient on gcd-final families; gcd folds output small values
  so wrong programs agree.
- Construction-induced: A22/A23 VALIDATE built from 2 instances of the planted motif; selection then returns the
  motif. Positive control equal to derived artifact in S4.
- Gate-induced: constant-True conditions (run_s3s4.py L391, L420; a16 L490; a17 L581).
- Dev overfit: numtheory a*b+1; P15 finals rule predicted to look like a large dev efficiency gain and fail on ~90%
  of unseen families.
- Wall-clock: slice 4 and Tier 3A contaminated (shared host load).
- Worker stale claim: W8 asserted a foundry PID was running; principal verified 0 python processes.

## 14. Likely false-negative regimes

- BOUNDED_RSI NO: improver fixed by construction, so improver-level change could never be observed (V5 untestable);
  the seat itself calls the NO "weak evidence about recursion in general".
- Supply: the tribunal's permutation-invariance/bounded-growth tests and init in {0,1} exclude nearly every
  non-additive task, so G2 schemas "exist but are not accessible" (K3/K6).
- Derivation starvation: median 0 schemas derived per donor (W4); levers downstream of a starved stage read as inert.
- Escrow window: frozen 250k sits at the minimum of a U-shaped window count; recurrence "lands where the pristine
  search cannot see it" (W8: carriers more often unreachable, p0 .77 vs .61).
- Representation: single-fold, no loops/conditionals/literals/lag; second-order chains break at grammar depth (G3 has
  no extent in W5).
- Validation multiplicity: one cross-group validation family per selection in C2.
- Small n (8-12 replicates; p = 0.0625 missed 0.05 in C2 with 4 vs 0).

## 15. Phase 3 audit

Engines audited: (i) E2 self-referential ES toy; (ii) engine v1; (iii) G4/W5 library-inheritance engine (Tier 3
through A23); (iv) Campaign 0 synthetic assay.

a. Representation richness
- (iii) G4/W5 engine: hierarchy PARTIAL (nested expression trees to depth 2-3 inside one fold; library entries are
  flat); compositional structure PARTIAL (expression composition; composition move wrap(S, op, atom) from 09-27);
  variable binding PARTIAL (fixed names acc, v, first, last; schema hole {H} is a single bound slot); memory PARTIAL
  (the fold accumulator; library persists across generations); recurrence PARTIAL (one fold loop, no general
  recursion); counterfactual state NO; latent variables NO; temporal abstraction NO; spatial abstraction NO; reusable
  substructure YES (schemas/libraries are the reused object); dynamic routing NO (library order is static per run);
  self-reference NO (the improver cannot read or edit itself).
- (ii) engine v1: hierarchy PARTIAL (expressions); compositional PARTIAL; variable binding NO (3 positional
  terminals); memory PARTIAL (answer cache); recurrence NO ("invents no control flow"); counterfactual NO; latent NO;
  temporal NO; spatial NO; reusable substructure PARTIAL (appended solver functions); dynamic routing NO;
  self-reference PARTIAL (the worker's search module source is rewritten, by fixed improver code).
- (i) E2: all NO except self-reference PARTIAL (the optimiser tunes its own 4 parameters) and memory NO.
- (iv) Campaign 0: a statistical generator; representation richness not applicable (NO across the board).

b. Reasoning opportunity. The G4/W5 world asks for an integer fold consistent with a handful of examples; it is
program induction over a finite enumerable space. It demands little beyond lookup in enumeration order plus
anti-unification; no planning, no partial observability, no delayed consequence, no adversary. Engine v1 tasks are
closed-form arithmetic/string transforms. The interesting demand is meta-level (does inherited structure change
search cost on unseen families), not object-level reasoning.

c. Shortcut surface. Recovering a planted motif from constructed validation; enumeration-order priors that "solve"
by bringing an equivalence class forward (budget-relative); extensionally-equivalent re-expressions counted as new;
abs()/sign conjugates; dev-distribution coincidences (coprime shortcut); gcd-final small-output agreement; constant
gate conditions; positive control equal to treatment; library carry-over swamping improver effect (W4 P-C: inherited
start +29 to +57 of 256 transfer cells vs selected +0 to +12).

d. Ruler resolving power. Strong on cost accounting (charges, paired CRN, exact evaluators, conformance) and on
memorisation vs machinery (by construction). Weak on novelty (base rate 16-25%) and on separating "new capability"
from "reordered search" -- the seat's V1/V2 split depends on a budget ladder that the walk cliff dominates. It cannot
resolve improver change at all (no mutable improver). Statistical power small (n 8-12).

e. Scale. Fold space ~2.26e8 (G4, computed from code), W5 body space 465,954; donor member space 151,920; escrow
250k per cell, PRISTINE ladders to 10M-12M; sequence lengths 4-9 / 20-60 / 200; values 2-99; families per experiment
~8-32; replicates 8-12; tribunal 200 instances/family (v1), 16 recipients (Tier 3); compute: single host M4 CPU,
runs of seconds to ~48 min (A17), T51 estimated ~16 core-hours; Campaign 0 jobs 14,400 in 153 s. E2: D = 6,
base budget 400, meta budget 60, 10 chains. No GPU, no LLM in any executed science.

## 16. Research reports and substantial documents

- science/frontier/APHRODITE_FRONTIER_SYNTHESIS_2026-09-27.md -- 40 KB; competing explanations A1-A6 with
  discriminating spikes; V1-V5 decomposition; supply forensics.
- science/frontier/PRIOR_ART_A_RSI_AGENTS.md, PRIOR_ART_B_LIBRARY_LEARNING.md, PRIOR_ART_C_OPEN_ENDEDNESS.md
  (64/56/77 KB) -- literature raids with VERIFIED/PARTIAL tags (STOP, Promptbreeder, Hyperagents, HGM, DreamCoder,
  LILO, Stitch, POET, Avida).
- science/frontier/CROSS_ENGINE_MECHANISMS.md -- borrowable Prometheus mechanisms (Ananke PTE, Crius).
- science/compounding/COMPOUNDING_SYNTHESIS_2026-09-28.md -- C1/C2, ruler v2, T4, W5, CON1.
- science/arc3/ARC3_SYNTHESIS_2026-09-28.md -- 18-section close record; A20-A23; workers.
- science/arc3/w4_improver_transplant/REPORT.md -- what must become mutable for improver evolution; probes P-A..P-C.
- science/compounding/rb6/IMPROVER_EVOLUTION_PROGRAM.md, IMPROVER_PARAMETER_INVENTORY.md, RB6_LEVER_CHECK_RESULT.md.
- pivot/APHRODITE_ENGINE_REVIEW_2026-09-21.md and _2.._11 -- eleven self-contained review packets, one per slice.
- pivot/APHRODITE_AMENDMENT16_CAMPAIGN_REPORT_2026-09-24.md / _2026-09-26.md.
- engine/README.md -- engine v1 design, measured qualification, honest mechanism-class label.
- engine/AMENDMENT_3..23 (+ addenda) -- frozen preregistrations.
- science/campaign1/PREREG_C1_TRANSPLANT_2026-09-19.md and AMENDMENT_2 -- the never-run real-LLM design.
- science/campaign0/PREREG_C0_ASSAY_QUALIFICATION_2026-09-18.md, RESULTS_C0/C0B/C0C.
- science/rsi/RESULTS_2026-09-17.md, science/swarm/RESULTS_2026-09-18.md.
- library/THEORIES.md, QUESTIONS.md, MODELS.md, METHODOLOGY.md (INVARIANTS 1-9), NEWS.md.
- library/designs/RSI_PROGRAM_v2.md, RSI_PROGRAM_ADJUDICATION_2026-09-18.md, RSI-1_TRANSPLANT_TEST_DRAFT.md.
- harvest_2026-09-30/INFERENCE_HARVEST_HANDOFF.md, PROMETHEUS_IMPROVEMENT_CAUSAL_MODEL.md,
  RSI_BOUNDARY_REVISITED_2026-09-30.md (L0-L? ladder), BUILDER_EVALUATION_PROTOCOL.md,
  IMPROVEMENT_PROCESS_OBSERVATORY_DESIGN.md, AGENT_SCIENCE_EXPERIMENTS.md (E4 held-out-trap transfer, 192 runs,
  ~29M tokens, not authorised).
- review/ARC3_MERGE_REVIEW_PACKET.md -- includes the constant-True defect table (s5).
- calibration/LEDGER.md -- 11 self-corrections (09-17/18).

## 17. Journals/TODOs/backlogs/pivots/abandoned branches

- journal/2026-09-17..23.md (no journal after 09-23; later state in STATUS UPDATE blocks and NEXT_SESSION.md).
- BACKLOG_H0H5.md; science/frontier/BACKLOG_RSI_FRONTIER.md (T01-T22); science/compounding/BACKLOG_COMPOUNDING.md
  (T01-T55). Prepared not run: T51 natural-recurrence donor stage (~16 core-hours), T52 validation dose-response,
  T53 budget-free capability endpoint, T47 instrument versioning, PKG-1..8 (ARC3_RESEARCH_PACKAGES.md).
- Open operator decisions: E4 live-LLM; TH-020 DSL fork (promote G2 to primitive: parked, default B); T51 start.
- superseded/: NEXT_SESSION_2026-09-22.md, NEXT_SESSION_2026-09-25_plus_updates.md, BACKLOG_provisional_2026-09-17_18.md.
- Branches named in records: aphrodite/engine-2026-09-21, aphrodite/a16-campaign-2026-09-26,
  aphrodite/frontier-2026-09-27, aphrodite/compounding-2026-09-27, aphrodite/arc3-2026-09-28 (merged 067fce3af),
  aphrodite/inference-harvest-2026-09-30 (merged 856b25e72). Superseded branches proposed for deletion [CLAIM].
- Abandoned: Campaign 1 (frozen), swarm toys (stopped), cloud acceleration (unavailable), M4 lease ledger (retired).

## 18. Dependencies on other engines and seats

- No code import from other seats' engines found in engine/ (imports are local modules) [CODE-INFERRED from files
  read; not exhaustively grepped].
- Campaign 1 depended on Archaeon task contracts, Harmonia metering, Vivarium sandboxes, Nestor/Archaeon benchmark
  receipts -- none delivered as far as STATUS records.
- Conceptual borrowings: Ananke PTE (novelty via ablation pattern), Crius (existence vs accessibility), ASAL critique
  (CROSS_ENGINE_MECHANISMS.md).
- Fabric leases (Odysseus) for future heavy work.

## 19. Scaling limitations

Python interpreter over string-built expressions; single host; exhaustive enumeration whose cost explodes with depth
(G4 -> W5 multiplied body space ~43x); every DSL extension "re-bases every budget number" and breaks comparability
(ARC3 s11); a17 needed exact-fast Q2 and checkpointing to fit in hours; the RB-6 check could not finish 4 supplies in
30 min under shared load.

## 20. Lens potential for Phase 3 (descriptive only)

- Substrate: enumerative program search over a typed integer-fold DSL with an inheritable ordering prior.
- Organisms: donor lineages (improver runs) and fresh recipients; no evolving population of improvers.
- Worlds: generated fold families with tribunal-qualified admission (Tier-3 tribunal, T4), W5 depth-3.
- Pressures: escrow budget; paired selection on validation families; constructed or lineage (LIN) recurrence.
- Phenomenon family: abstraction acquisition, transfer, compounding, efficiency vs capability, improver change
  (designed, not observed).
- Current resolving mechanism: exact charge accounting with PRISTINE/sham/no-composition controls and transplant into
  fresh recipients; whole-program behaviour identity with class certificates.
- Resolution ceiling: one meta-generation; budget-relative capability; improver fixed; novelty base rate ~1 in 4.
- Noise sources: walk-cliff bimodality, supply lottery across seeds, small n, wall-clock contamination.
- Architectural limit: the improver is immutable; representation is one fold with depth-bounded bodies.
- Reusable parts: the membrane (canonical artifact bytes, positional extraction, one loader path, reset receipts);
  escrow accounting beneath the improver; conformance gate between two evaluators; keyed CRN pairing; shams from
  failed bodies; class-certificate identity; the V1-V5 verdict decomposition; Campaign 0 style planted-truth assay
  qualification; the calibration-ledger practice.
- Toy-grade parts: the DSL and task catalogs; the Tier-1 toys; the news monitor.
- Unknowns: whether any of the S4/A23 effects survive a mutable improver, a non-additive world, or natural
  recurrence (T51 never run).

## 21. Open questions / what this crawl did not read

Read in full or substantially: STATUS.md, STATUS_REPORT_2026-10-01.md, RESPONSIBILITIES.md, NEXT_SESSION.md,
calibration/LEDGER.md, engine/README.md, engine.py (structure and key functions), improver.py, basis_v4.py (first
120 lines), a23_c3r2c.py (head), run_s3s4.py (L385-423), e2_self_improver.py (head), frontier synthesis (s0-s9),
ARC3 synthesis, compounding synthesis (s0-s1), RB6 result, W4 report (s0), Review 10 (s0-s2), Review 11 (s0-s3),
RSI toys and swarm results (heads), C0/C0B/C0C results (heads), Campaign 1 prereg (s1-s4), benchmark spec (head),
ARC3 merge packet s5, RSI_BOUNDARY_REVISITED (s1-s2), news monitor README, 2026-09-17 directive.
NOT read: the 23 AMENDMENT files individually (only via syntheses), engine Reviews 1-9, tier3b-e.py, identity.py,
fair.py, tribunal_t4.py, ruler_v2, a16-a22 code bodies, the K1-K8 spike code and JSON, W1-W3/W5-W8 reports, PRIOR_ART
A-C contents, library/ THEORIES/QUESTIONS/MODELS, journals, harvest evidence files, accel/ RunPod/Azure scripts (an
azure.env file exists there; not opened, per the no-credentials rule), the result JSONs (none re-computed). No test
was executed. Open: whether benchmark receipts from Nestor/Archaeon exist anywhere; whether the S4 result would
survive non-constant conditions 4/8; whether T4's 1.7% window mismatch changes A23.
Holdout/secret paths: none touched.
