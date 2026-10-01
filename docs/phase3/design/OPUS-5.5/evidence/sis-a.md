# Evidence digest sis-a -- Sisyphus A: Archaeon, Vivarium, Daedalus, Apollo, Lexis

Reader: read-only evidence reader for EPIMETHEUS (Phase 3 architect OPUS-5.5).
Date: 2026-10-01. Worktree: C:/prometheus-worktrees/epimetheus-phase3 (HEAD 4c071e3c5).
Inputs: docs/phase3/intake/sisyphus/REPORT.md (skimmed), seats/{Archaeon,Vivarium,Daedalus,
Apollo,Lexis}.md (read in full), seats/_frag/<seat>.{engines,artifacts}.jsonl (all records),
plus targeted source checks listed in s0.2. Independence: nothing under docs/phase3/design/
other than this file's own directory was opened; nothing under roles/Dionysus/.

Tags: IMPL (read in code/data here), INTENT, HIST (historical claim in a committed doc),
REPORTED (unverified result), CORR (later correction), INFER (inferred from code/data),
UNK. "Confirmed" means I opened the underlying artifact in this session.

Question applied to every result: WHAT DID THE APPARATUS HAVE THE CAPACITY TO REVEAL?

-----------------------------------------------------------------------------------------
## 0. Bottom line for the architect

1. This group contains exactly one evolutionary organism substrate that carried real
   campaigns (the Proteus v0 VM, via Archaeon WSE/CMP1-3/C4/C5/C6/Deep Frontier), one
   byte-soup reproduction substrate (Archaeon's Z80 build, used for ENVGATE), and a large
   amount of provenance infrastructure (SFE, Vivarium) that hosted only toy executors.
   Apollo/Lexis are composition-over-human-solvers substrates with exact closure rulers.
   [IMPL/HIST]
2. The highest cognitive demand any world here actually posed to an evolving organism was
   two-slot keyed recall (WSE W2_K2: hold two 4-bit values keyed by stream tag, answer the
   ask). It was never reached (0/60 summits). Everything else that ran was a 1-value latch,
   a delay hold, a lookup/1-step function, a static fitness landscape, or a routing choice
   among human-written solvers. No world in this group demanded hidden-state inference that
   an organism was shown to face at a reachable level. [HIST, WSE packet s7.1]
3. Almost every null in the group is apparatus-bounded, and the bound is usually
   identifiable: search reachability (SSF, W2_K2, C5, D-13, Apollo S1), ruler floor/
   saturation (Vivarium C3-2, C6 detectors), estimator mismatch (C5 vs Deep Frontier),
   world exhaustibility (Apollo/Lexis 0.833; CEGIS 3-input), or design-forced geometry
   (SFE canary). Very few results qualify as true_negative.
4. The instruments that demonstrably detect are: the Archaeon taint VM / lineage core
   (differential-tested + known-answer births), ENVGATE's sham-arm geometry on byte-identical
   input streams, WSE held-out confirmation, the opcode-permuted incompetent-import control,
   the copier census with substrate ablation, Lexis exact closure + blind-author re-measure,
   Apollo O1 enumeration and dead-world control, Vivarium exact-symmetry null and
   library-leak checker. The instruments that steered the most compute (C6/Deep Frontier
   detectors: 3.72M evaluations) had the weakest demonstrated detection (planted-positive
   catch 25% and 0% at 1% false-fire).
5. Two verified apparatus facts change how historical contradictions should be read:
   (a) the Deep Frontier "every N climbs" number is a TRAINING-battery max, while C5's
   "flat" .382 is a HELD-OUT best-of-57 screen value (segment.py:219, C5 packet l.49-50);
   (b) the SFE Gen-2 canary null was forced by identical RNG streams, identical initial
   populations and a parity-preserving 2-bit mutation (canary.py:40-45, 74-79; initial
   distances re-derived here as 9/13/16/14, leading lineage odd).

### 0.1 Coverage limits
- Off-repo evidence (Archaeon C:/Prometheus-data, M2 SFE ledgers, F:/SerendipityD, Apollo
  M2 run dirs) not available; the D-13 ancestor is known only through the Daedalus dossier
  and the in-repo WOW packet. [UNK beyond git]
- Campaign slot-level files (C2-C5) not opened individually; I opened campaign-level review
  packets and specific lines.
- No experiment was run. One zero-cost stdlib re-derivation of the canary's initial state
  was done (no engine, no evolution).

### 0.2 What I re-checked in source (this session)

| claim | artifact checked | result |
|---|---|---|
| SFE canary identical RNG + population per world; 2-flip mutation | SerendipityFoundry/SerendipityFoundryEngine/sfe/canary.py:40-45, 74-79 | CONFIRMED IMPL. Also: W1 and W2 receive no pop imports (W2's failure imports pass pop=None, l.124) so their trajectories are identical; HYPOTHESES_ONLY and SUCCESSES_ONLY import the same top_bits payload (l.147-156) |
| canary leading lineage odd parity | executors.py:92-95 target_for + random.Random(20260901) | CONFIRMED by re-derivation: target 000011110000111100100000, initial distances [9,13,16,14]; parity under 2-flip invariant (IMPL); "odd lineage dominates truncation" is INFER |
| Deep Frontier ADMITTED rulers hard-coded | archaeon/frontier/scheduler.py:178 | CONFIRMED IMPL |
| Frontier ran without its gate | archaeon/frontier/OPERATOR_EXECUTION_AUTHORIZED.json | CONFIRMED IMPL: is_verification false; G6_0_ALL_COMPONENTS_VERIFIED false; 5 unverified items |
| Frontier "max" is training reward | archaeon/campaign6/segment.py:219 (episodes_for(..., "train", ...)), :319; archaeon/frontier/digest.py reward_max_over_run | CONFIRMED IMPL |
| C5 .382 is a held-out screen value | roles/Archaeon/REVIEW_PACKET_CAMPAIGN5_2026-09-18.md l.49-50, 76-77 | CONFIRMED HIST |
| Proteus v0 VM is a total interpreter | proteus/foundry/vm.py:181 `op = tape[ip] % nops` | CONFIRMED IMPL |
| C4: 932/932 words out of table, P(fatal)=1.000, REPRESENTATION_BLOCKED | REVIEW_PACKET_CAMPAIGN4 l.31-41 | CONFIRMED HIST |
| WSE two-stream 0/60; shelf one-value; delay invariance; import takeover | REVIEW_PACKET_WSE_ARCHITECTURE l.355-445 | CONFIRMED HIST (numbers as quoted below) |
| Z80 spontaneous flag read a run label | archaeon/z80atlas/engine.py:448 (legacy: spec["init"]=="random") vs :450 (repaired: provenance endo_clean) | CONFIRMED IMPL |
| Z80 verify transplants force migration none / reservoir False on topology change | archaeon/z80atlas/scheduler.py:252 | CONFIRMED IMPL |
| ENVGATE-01 adjudication R1/R2 | archaeon/envgate/ADJUDICATION_ADDENDUM_2026-09-24.md | CONFIRMED HIST |
| ENVGATE-02 numbers and gate | archaeon/envgate2/VERDICT_2026-09-26.md | CONFIRMED HIST |
| Taint VM exactness + known-answer fixtures | archaeon/lineage/taint_vm.py l.1-12; archaeon/tests/test_lineage_attribution.py l.41-152 | CONFIRMED IMPL: 2x3,000 random-tape differential test vs frozen vm.execute; 10 named known-answer birth tests incl. inert host |
| Copier census 9.6e-6, z80 0 in 1.2e7, LOTTERY band 0.05-20 | archaeon/z80atlas/pivot/Z80ATLAS_RULINGS_FOLLOWUP_REVIEW_2026-09-24.md l.14-40, 115-140 | CONFIRMED HIST |
| DENOVO-01 0/80, controls pass | archaeon/z80atlas/denovo/RESULTS.json, PREREG.json | CONFIRMED IMPL (N=128 random start, 4,000 epoch cap) |
| C6 detector power 25% / 0% | archaeon/campaign6/DECISIONS.md D6-010 l.102-104 | CONFIRMED HIST |
| Nestor CW01 count-fixing ruler reread | roles/Nestor/campaigns/cw01-2026-09-17/loop/BOUNDARY_REPORT_CYCLE5_2026-09-19.md l.82-89 | CONFIRMED HIST (control reproduces old effects under count-fixing variants) |
| Vivarium C3-2 zeros are a ruler floor | git show 30e97ed94 | CONFIRMED HIST (40/40 random tables 0.0 under both masks) |
| Vivarium dead-man auto-releases stranded rows | vivarium/viv/deadman.py:396-398, 500-509 | CONFIRMED IMPL |
| Apollo crossover A/B | apollo/pivot/recombination_findings_2026-06-16.md; apollo/cycles/type_bridge/RESULT.json; apollo/src/blackboard_evolve.py:802-805 | CONFIRMED HIST/IMPL; ingredients seeding = the exact two splice-parents |
| Apollo E9 mechanism | apollo/src/blackboard_ops_compare.py:25 precondition startswith("is ") | CONFIRMED IMPL |
| Lexis exact closure | roles/Lexis/notes/STEP1_CEILING_CLOSED_2026-08-25.md l.1-80 | CONFIRMED HIST |
| Lexis G7 positive controls and ceiling 2/42 | roles/Lexis/notes/G7_CHARON_2026-09-01.md l.18-52, 133 | CONFIRMED HIST |
| Task 2 never ran; identity re-adjudication never happened | git ls-files apollo/cycles (0 state_injection files); last apollo commit 2b7c6e4fb, last Lexis a37988536 (both 2026-09-11); roles/base-role/RESPONSIBILITIES.md:221 | CONFIRMED IMPL |
| D-7 geometry | SerendipityFoundry/D7/README.md l.1-45 | CONFIRMED HIST |
| D-13 selection was drift | SerendipityFoundry/wow/WOW_ARCHAEOLOGY_REVIEW_PACKET.txt l.44-46, 132 | CONFIRMED HIST |

-----------------------------------------------------------------------------------------
## 1. What was really built (organism / world / pressure / ruler actually present)

### 1.1 Archaeon (four unrelated code families, ~51k LOC) [IMPL size per dossier]
- Family A, fossil-to-queue producer: NO organism, NO world. Six arithmetic detectors over
  SFE/PEW rows; coverage-biased exploration that cannot propose unobserved combinations.
  The fossil->experiment arrow never carried information (evidence-link dry run: draw
  byte-identical with and without corpus). [HIST: EVIDENCE_LINK_DRYRUN; dossier T1]
- Family A', exact producer-policy bench (S1-S7, ARCH-46A): "agent" is a proposal policy
  on a hidden L-bit target with exact Hamming feedback (Mastermind-like). Exact DP optimum
  as ruler. Toy but fully calibrated. [HIST]
- Family B, Proteus-VM GA harnesses (WSE, CMP1-3, C4, C5, C6, Deep Frontier):
  organism = Proteus player program, 4-word instructions, 25 opcodes, every word legal
  (total interpreter, IMPL vm.py:181), registers 2-16, tape 16-4096 words, LD/ST by
  register address, no call/stack, no lifetime learning; reproduction external (GA,
  N=200, tournament 4, elitism 4, one grammar-v0.4 mutation per child). World = event-
  stream grammar (PUT/ASK/... over K streams, 4-bit values so chance 1/16, delays,
  distractors, train/held-out vocabulary). C5 added Representation B (narrow encoding
  with FAIL/FIZZLE faults). C6 added procedurally composed worlds (0-10 modules: resource
  pools, locality, objects, delay, hidden lagged channel, hazards, coupling via shared
  pools, regime change; 24-tick episodes) and pressure schedules, plus Proteus graph
  organisms. [HIST: WSE packet; IMPL: campaign6/worlds, segment.py]
- Family C, Z80 byte-VM ecology: 32/64-byte tapes, 32 opcodes incl. a COPY primitive in
  the vmcopy substrate, 4 registers zeroed every execution, step cap 256, 128 cells, six
  reproduction physics, twelve pressures, tasks that are single-byte functions (ECHO,
  INC1, NEG, ADD2, COND). Phenomenon of interest: reproduction/heredity, not reasoning.
  ENVGATE = one frozen configuration plus 2,048 write-protected inflow chambers of random
  tapes; the manipulated variable is the input-byte distribution. [HIST/IMPL]
- Family D, causal lens / attribution v0: no organism of its own; adapters map other
  engines' records (BEE, NPE, PTE, Archaeon) into a common event schema; validator A1-A17.
  [HIST]

### 1.2 Vivarium [IMPL per dossier, spot-checked]
NOT an alife engine. A Postgres single-slot experiment queue + SFE runner + PEW outbox.
"Kinds" wrap other seats' toys: onemax bitstring (16-32 bit), radius-3 density CA (rule
table organism), 256 ECA rules on a 7-ring (exhaustive), 3-input Boolean CEGIS (256
possible targets, 12-task family). No mutation, no selection, no pressure ever ran
through it. From Campaign 4 on, science bypassed it (no kind could evaluate a program
variant). Its scientific value is provenance (sealed spec, blinding, errata view,
attempt/step replay) and a record of execution failures that looked like science.

### 1.3 Daedalus / SFE [IMPL]
SFE contains NO search, mutation, selection or simulation (executors.py docstring: the
executor scores one candidate; search is the caller's). It is a hash-chained per-world
ledger with prediction-before-observation, families, attestation, sharing topologies and
world fork-by-reference. Only physics shipped: onemax bitstring, NK (N<=20, certified
optimum), a nondeterminism negative control. The search that existed lived off-repo in
the D-13 Foundry (stackvm-v1 with stack, 8 regs, 256 memory, bounded loops; PushGP;
tree-GP; random/GA/novelty/MAP-Elites drivers). Pre-seat D-series (D-6A, D-7, D-8, D-10)
are archived toy experiments, D-7 the only positive. wforge (integer register worlds with
partial observation, delay, regime switch, 2-slot contention) and MHC (microstructure
observatory) were built but never used for science. [IMPL/HIST]

### 1.4 Apollo [IMPL/HIST]
Organisms never minted reasoning; they ordered and gated human-written solvers.
v2: routing DAGs over 25 puzzle-named primitives (bat_and_ball, sally_anne_test, ...).
Branch C: linear typed pipelines (body <= 6) of ~26 hand-written Python operators over a
fixed-schema blackboard, guarded scorers for dispatch, MAP-Elites, optional crossover
(--crossover-frac, CLI default 0.0, used at 0.3 in the A/B). World: 120 static NL
multiple-choice tasks authored by the same hand that wrote the parsers. The whole
reachable program space was enumerable (O1: 1.737M pipelines in ~3,000 s CPU).
Gen-2: drove D-13 /v0 drivers at budgets 80-600 on 12-case integer functions.

### 1.5 Lexis [IMPL/HIST]
No organism, world or search of its own. Measurement instruments over Apollo's substrate:
exact reachable-state closure (keyed on a proved answer-relevant slot projection D, 17/23
slots), joint product BFS, dE/dS split (outside closure vs reachable-but-unrouted),
admission gates G5 (redundancy), G6 (24-permutation null), G7 (blind-author re-measure),
G1 forge ablation census.

-----------------------------------------------------------------------------------------
## 2. Engines: actual organism, world and maximum cognitive demand

| engine (seat) | organism actual | world actual | max cognitive demand actually posed | pressure actual | ruler actual |
|---|---|---|---|---|---|
| v0 producer (Archaeon) | none | experiment ledger rows | none (statistics over records) | none | 6 detectors, mostly ineligible on live corpus |
| S1-S7 bench (Archaeon) | proposal policy (code) | hidden L-bit target, exact Hamming feedback, L 8-32 | version-space elimination over a static hidden target (solved by code, not evolved) | work budgets | exact DP optimum, sign tests |
| WSE / CMP1-3 (Archaeon) | Proteus v0 program, total interpreter | event streams, K 1-8, 4-bit values, delays 0-16 | W0: 1-value latch; W2_K2: 2-slot keyed recall (never reached); ASKO/ASK2 composition (never reached) | tournament GA, cost vectors, curricula, imports | per-ask exact reward, 48-episode held-out confirmation, reachability table, disposition ladder |
| C4/C5 (Archaeon) | Proteus programs, OLD total vs Representation B FAIL/FIZZLE | screened WSE cells | same as WSE (question was mutational robustness) | edit censuses, walks, equal-compute evolution | damage labels on 16-episode answer vectors; count-fixing edit rulers |
| C6 + Deep Frontier (Archaeon) | Proteus v0 + graph organisms | composed worlds 0-10 modules, 24 ticks, coupling, hidden lagged channel, regime change | in principle hidden-state inference and endogenous competition; in practice many bins dead (bin 5 reward 0 for 40,000 evals) | pressure schedules, frontier pools | 11 FIRE/QUIET/UNABLE detectors, weak positive controls; training-max readout |
| Z80 x Atlas (Archaeon) | 32/64-byte tapes, COPY primitive | 128-cell ecologies, 6 reproduction physics | lookup / 1-step byte functions; phenomenon = reproduction | factor grammar, flags->promotion | mechanical flags (label-reading until repair) |
| ENVGATE (Archaeon) | random vmcopy32 tapes | one frozen ecology + random inflow | none (establishment of copiers) | manipulated input-byte distribution | paired arms, sham, McNemar/Holm, block tests, taint-VM genetic identity |
| causal lens (Archaeon) | host engines' organisms | preserved records | none | none | contract + validator + fixtures |
| Vivarium kinds | bitstring / CA rule table / ECA rule / Boolean expr | onemax, density CA (149 cells), 7-cell ECA, 3-input Boolean | lookup; density classification posed to fixed rule tables (no adaptation) | none | single-field outcome rule; symmetry null; leak checker |
| SFE + executors (Daedalus) | none / 24-bit string in canary | onemax, NK N<=20 | none (static fitness) | caller's; canary (mu+lambda) 2-flip | provenance rulers; fraction matched; certified NK optimum |
| D-13 /v0 (Daedalus ancestor, off-repo) | stackvm-v1 / PushGP / tree-GP | 12-case integer functions | arithmetic function induction (only identity, x+1 reached) | random/GA/novelty/MAP-Elites, budget-metered | exact solve on test cases |
| D-7 (Daedalus genesis) | synthesized transforms | 3-register mod-13 machine, 2,197 states, certified barrier | composition across two artifacts to open a gated nonlinear coordinate | history-conditioned synthesis | exact closure certifier |
| Apollo v2 / Branch C | pipelines of human solvers | 120 static NL MC tasks | routing/dispatch among pre-built solvers (cognition lives in operators) | NSGA / MAP-Elites, LLM or deterministic mutation, crossover | accuracy, composition lift, load-bearing core, O1, E9 |
| Lexis instruments | Apollo programs | T_home 120, T_charon 42 | same | none | exact closure, dE/dS, G5/G6/G7 |

-----------------------------------------------------------------------------------------
## 3. Historical results reclassified (evidence-profile axes)

Axes: Q question could fail; S substrate capacity (constructive proof?); W world demand
(ablated baseline?); R ruler validity (planted positive / matched negative); B baseline
discrimination; Rep replication (new seeds/host/independent reimplementation, NOT replay);
M mechanism (ablation/transplant). Y / P / N / U.

### Archaeon

SA-01 "Fossils direct the next experiment" (C-01, C-02, S1). Hist: REPORTED NULL.
- Apparatus: live corpus had no player identity (3/6 detectors ineligible), detectors
  fired on regions disjoint from steerable regions, S1 n=12 pairs with predicted advantage
  .059 on L=32. [HIST: dossier C-02, T1; Vivarium V-7]
- Reclass: world_insufficiency (corpus) + statistical_insufficiency (S1). Not
  hypothesis_failure.
- Axes: Q P / S P (S3/S4 show info-consuming producers beat uniform on synthetic worlds) /
  W N / R P (synthetic calibration at 200 seeds; ineligible live) / B Y (uniform) / Rep N / M N.

SA-02 Synthetic producer policies (S3, S4, ARCH-46A). Hist: info producers beat U by
.024-.091 nAUC; NO_SEPARATION among G/W/M; endgame repair licensed after exact-rational
re-run showed the S7 regression and 3/49 "improvements" were float tie splits.
- Reclass: instrument_positive on a toy (exact feedback); implementation_defect (float
  ties) found and corrected inside one result.
- Axes: Q Y / S Y / W Y / R Y (exact DP optimum) / B Y / Rep P (seeds) / M N.

SA-03 WSE survey v01 (C-05). Hist: under cost regimes E1-E3 every cell, every seed ends
persist=none, reward 0; under E0 only register-only recurrence.
- Reclass: pressure_insufficiency (costs applied from generation 0 on a flat landscape:
  "cost before capability is extinction") + search_insufficiency.
- Axes: Q Y / S P (expressible in principle, INFER) / W P / R P / B P / Rep P (3 seeds) / M N.

SA-04 Selective State Formation (C-06). Hist: hand-written selective organisms beat
logger and last-value by >= .10 on 7/7 runnable cells BEFORE evolution; evolution 0/60
naive footholds, 2/9 at 512x200.
- Reclass: search_insufficiency. This is the cleanest null localization in the group:
  constructive capacity proof (S) and world-demand proof (W, against named baselines)
  exist, so the null is about reachability under this operator/budget.
- Axes: Q Y / S Y (hand-written) / W Y (beats logger, last-value) / R P / B Y / Rep P / M N.

SA-05 Two-stream ceiling W2_K2 (CMP2/CMP3). Hist: 0 confirmed summits in 60 runs across
budget (G300), seeded shelf, all-or-nothing payoff and corridor attacks; best training
excursion .875 read .60 held-out; shelf elites remember ONE value (first-put 6/12,
last-put 4/12); 1 improving child in 4,800; 0 of 58 second-stream gains kept the first.
[CONFIRMED HIST: WSE packet s7.1-7.2]
- Reclass: search_insufficiency OR organism_insufficiency -- not separable, because
  organism primitives and operator were never varied independently (C4/C5 changed
  encoding, not addressing/memory). Seat itself asks (Q3) whether the substrate is right.
- Axes: Q Y / S U (expressible by LD/ST in principle, INFER; no hand-written summit
  organism found in what I read) / W Y (two values needed; shelf = .5) / R Y (held-out
  confirmation caught training luck) / B Y (first-put/last-put strategies named) /
  Rep P (n=12 per attack, same VM/operator) / M P (shelf strategy identified by measurement).

SA-06 Delay-invariant reader (C3-SFE-03). Hist: delay curriculum 0->1->2->4 gives
delay-general elites (held-out 1.0) in 11/12 seeds; all 11 read untrained delays 8 and 16
at held-out 1.0 while matched-budget direct search reaches delay 8 in 0/6 and 16 in 1/6;
mature single-task solvers score 0.0. Caveat: in 5/12 seeds the first delay-1 battery
promoted an organism already present. [CONFIRMED HIST: WSE packet s7.3]
- Reclass: survives_as_anomaly. Open whether a capability or evidence the delay knob was
  never a difficulty (packet Q2); Nestor CW01 later classed the lineage as "start-anchored"
  (dossier open q.6). No ablation; no test in a cell where delay cannot be ignored.
- Axes: Q Y / S Y / W P / R P / B Y / Rep P (11/12 seeds) / M N.
- Developmental note: the ONLY curriculum (developmental-pressure) positive in the group;
  generality appeared abruptly (8/11 within one probe gap), minted at rung 1 or 2.

SA-07 Import takeover is mechanics (C3-SFE-10). Hist: 228 runs; opcode-permuted controls
(same length, opcode multiset, operands; competence verified .0-.125) take over 11-12/12
almost as fast as mature solvers; dose sets speed not outcome; only an offspring cap moved
the clock; genome diversity stays .78-.99 so diversity readouts see nothing.
[CONFIRMED HIST: WSE packet s7.4]
- Reclass: instrument_positive (the control detected a confound) and it retro-converts
  CMP1 "mature whole material helps" into false_positive (SA-08).
- Axes: Q Y / S Y / W - / R Y / B Y (no-import 0/12) / Rep P / M P (cap).

SA-08 CMP1 "mature whole material helps" (components 2/3 vs 0/3). Hist: killed at n>=10
in CMP2 (+.009, +.002). Reclass: false_positive (statistical_insufficiency n=3; import
mechanics). Axes: Q Y / S Y / W P / R N / B P / Rep Y (CMP2 re-measure killed it) / M N.

SA-09 Basin share and CA delayed-recall margin (CMP2->CMP3). Hist: pooled rho -.568 was a
two-point correlation across strata differing 13x; causal rewrite effect -.083 vs declared
+.25; a hand-designed rule shows the same CA localization; lattice permutation preserves
it 5/8. Reclass: false_positive (stratification artefact) + ruler_insufficiency
(no permuted-structure control at first). Axes: Q Y / S - / W N / R P / B P / Rep Y (killed) / M P.

SA-10 C4 damage geometry. Hist: no single edit improved any of 57 parents (0/5,472);
displacement bimodal; loss .52->.99 over radius 1-16; neutral network connected (188/188
to depth 16); recombination 0/6 vs 0/6; selection builds neutrality and length (single-
edit loss .419/.185/.125 at mean length 19/40/62); two slots REPRESENTATION_BLOCKED;
C4-09/10 worlds pre-solved by the starting parents. [CONFIRMED HIST: C4 packet s1-s2]
- Reclass: descriptive map = instrument_positive (replicated digest-for-digest);
  "length/selection builds robustness" = ruler_insufficiency (count-fixing ruler; Nestor
  CW01 D084 shows 4/7 fixed-count claims disappear under scattered Bernoulli(f) on the same
  VM; applies to C4-08 by INFER, never re-read); REPRESENTATION_BLOCKED = organism
  (substrate) insufficiency for fault questions (total interpreter, IMPL vm.py:181);
  pre-solved worlds = implementation_defect.
- Axes: Q Y / S P / W P / R P / B P (identity 57/57, randomization 56/57) / Rep P (mostly deterministic replay) / M N.

SA-11 C5 "OLD_SUBSTRATE_EXHAUSTED / flat elite" vs Deep Frontier "every N climbs".
Hist: C5-02 0/24 cells improved at equal total compute (9k-36k evaluations); DF C5-flat.T1
max .500 > .382 and N family .479-.562 at 60,000 evaluations (PROVISIONAL).
- Verified: DF numbers are per-generation population maxima of TRAINING reward
  (segment.py:219, 319; digest.py reward_max_over_run); C5 .382 is best HELD-OUT over 57
  parents (C5 packet l.49-50, 76-77). CMP3 already showed training .9375 -> .53 held-out.
- Reclass: ruler_insufficiency (estimator mismatch) for the contradiction; C5 itself is
  search_insufficiency-bounded (compute 9k-36k). Neither side established.
- Axes: Q Y / S U / W P / R N (comparison not like-for-like) / B P / Rep N / M N.

SA-12 C5 Representation B. Hist: real local recovery at single-edit level (229 replicated
recoveries vs 154 insulation losses); insertion the only asymmetric-rescue operator
(C5-06, 102 recoveries, 0 losses, per dossier); reach at equal compute 0/+1/+1 nets over 24
cells; first held-out gain over starting best: none in 96 cells; one labelled post-hoc
amendment (F3 statistic).
- Reclass: instrument_positive (a fault boundary changes local repair) + survives_as_
  anomaly (insertion asymmetry) + search_insufficiency for discovery (budget-bounded
  true_negative at best).
- Axes: Q Y / S Y / W P / R P (post-hoc amendment) / B Y (equal compute) / Rep P / M P.

SA-13 C6 observatory and Deep Frontier detectors. Hist: 3,719,136 evaluations;
structural_reuse 1,658,614 and detector_disagreement 1,753,735 firings; four rulers UNABLE
on 1,775,074 evaluations each; planted positives caught 25% (novelty) and 0%
(discontinuity) at the 1% false-fire rule; ADMITTED rulers hard-coded; executed with
G6-0 unverified. [CONFIRMED IMPL/HIST]
- Reclass: ruler_insufficiency + provenance_defect (admission never recorded). Any
  "novelty" in C6 worlds would be indistinguishable from saturation noise.
- Axes: Q P / S U / W U / R N / B P (1% false-fire calibration only) / Rep N / M N.

SA-14 P-boom. Hist: within-arm spike rate spread 0.17-5.67; DF-015 found run_id folded into
random streams (identical-by-design arms differed from generation 1); post-fix readout
still within-arm dominated; a later "finding 3" inversion compares shared-stream to
independent-stream arms (crawler INFER, not re-verified here).
- Reclass: implementation_defect (hidden seed) + false_positive (finding 3, REPORTED/INFER).
- Axes: Q Y / S U / W U / R N / B N / Rep N / M N.

SA-15 Z80 x Atlas "26 spontaneous replications". Hist: all 26 were transplants; repaired
predicate 0/26; random founders 0/3,252; corrected top-30 a 30-way tie.
- Verified: legacy predicate engine.py:448 reads spec["init"]=="random"; repaired :450
  uses provenance (endo_clean). [IMPL]
- Reclass: provenance_defect -> false_positive.
- Axes: Q Y / S Y (seeded replicators replicate) / W - / R N (label-reading) / B P / Rep Y (byte-identical replay reclassified; replay, not replication) / M N.

SA-16 DENOVO-01. Hist: 0/80 de-novo events, controls 21/21 pass (seeded replicator
replicates; inserted lineages correctly not flagged spontaneous), every treatment world
extinct (median epoch 61). [CONFIRMED IMPL: RESULTS.json, PREREG.json N=128]
- Reclass: statistical_insufficiency. INFER: with the census density 9.6e-6 and a random
  start of N=128 (plus mutants before extinction), expected copier-founder worlds in 80 is
  order 0.1; the test had essentially no power against the later-measured prior.
- Axes: Q P / S Y / W P / R P (negative/cheat control yes; no planted random-origin positive) / B - / Rep N / M N.

SA-17 Copier census (COPIER-CENSUS-01). Hist: uniform random vmcopy32 tapes are exact
self-copiers at 9.6e-6 [7.8e-6, 1.17e-5], 99% input-gated (85% only at input 128 = window
base); 96/96 breed true; z80 substrate without COPY: 0 copiers of any grade in 1.2e7 tapes;
predicted 6.86 copier-founder worlds vs 1 observed -> LOTTERY_CONSISTENT (band 0.05-20).
- Reclass: instrument_positive (measured prior; substrate ablation shows copying is a
  property of one world-supplied primitive). The LOTTERY reading itself is weak (a 400x
  band; conversion estimate rests on one event, CP CI [.004,.58]).
- Axes: Q P (band) / S Y / W - / R Y (exactness with input-skip; breed-true) / B Y (no-COPY substrate) / Rep P / M Y (primitive ablation at substrate level).

SA-18 Moat_advantage / niches / recombination (Z80). Hist: sampler drew 0 bare-niches
worlds; promotion sent 8,682 runs to niches; matched controls dropped recombination by
grammar constraint. Reclass: implementation_defect (confounded by construction; scheduler
coupling verified at scheduler.py:252 for verify transplants). Axes: Q N / R N / B N.

SA-19 Transplant persistence without competence. Hist: transplanted lineages persist and
self-replicate 39/39, task competence 0/39. Reclass: survives_as_anomaly (copying
heritable, function not). Axes: Q Y / S Y / W P / R P / B P / Rep U / M N.

SA-20 ENVGATE-01. Hist: copier-founded establishments U 47 / SHAM 45 / BLOCK_128 18 /
RESCUE_128 1 / BAND_BLOCK 1; byte-identical arrival sequences across arms (sha256 per arm,
16 blocks); preregistered composite verdict GATING_CAUSALLY_SUPPORTED downgraded by
operator R1 to GATING_PARTIALLY_SUPPORTED because RESCUE's significance came from one
takeover world (block 15, copier gated at 255; block-level p=.5). R2: host-mediated
reproduction is real amplification, not origination. [CONFIRMED HIST]
- Reclass: instrument_positive (band 120..135 blocking is causal; sham does nothing) +
  false_positive (rescue component) + survives_as_anomaly (host-mediated reproduction).
- Axes: Q Y / S Y / W Y (environment is the manipulated variable) / R Y (sham arm, paired streams) / B Y / Rep P (replicated by ENVGATE-02 on new blocks, same code family) / M P.

SA-21 ENVGATE-02 (window rescue under genetic identity). Hist: genetic establishments U 24
/ RRIGHT 3 / RWEAK 2 / R128 5 / BAND0 5; P1 U>BAND0 12+/2- blocks, p=.0065; Page's L
p=.001; gate condition 6 failed (P2 0+/2-, P3 1+/0-) -> WINDOW_NOT_SUPPORTED; BAND0/R128 ~7x
above frozen prediction; parent-chain counts 8-42x genetic counts; takeovers 38% of
establishments; frozen analyze.main() KeyError handled by a wrapper without editing the
frozen file. [CONFIRMED HIST: VERDICT]
- Reclass: law = instrument_positive (replicates under genetic identity); window-rescue
  model = hypothesis_failure (but rescue contrasts have 1-2 non-tied blocks:
  statistical_insufficiency); BAND0 = survives_as_anomaly.
- Axes: Q Y / S Y / W Y / R Y / B Y / Rep P / M P.

SA-22 PORTABILITY-01 / attribution v0 (C-18, C-20). Hist: lens portable with domain limits
across Archaeon/BEE/NPE/PTE; 33.1% of BEE births NOT_IDENTIFIABLE; reproduction boundary
not found (15 cases x 9 definitions); several claims withdrawn after adversarial review.
Reclass: instrument_positive (portability) with ruler limits. Axes: Q Y / R P (known-answer
fixtures TH-014) / Rep P / M P (TH-015 interventions).

SA-23 E-003 cross-engine ancestry. Hist/CORR: BEE VALIDATED only after post-exposure
amendments; under pre-exposure rules ALTERED (P2 .504); NPE leg below its own 30-birth
floor by construction; Harmonia audit item H rules VALIDATED not supported; Q8c .00115
robust. Reclass: provenance_defect (post-exposure amendment) for the verdict; the
amendment-independent number stands. Axes: Q Y / R P / Rep N / M N.

### Vivarium

SV-01 C3-2 "116/116 random rules are structural zeros" (D3-over-C3-acq STRUCTURALLY_VOID).
CORR (30e97ed94, confirmed): 40/40 random tables score exactly 0.0 under both at_T and
stable masks; under cellwise random tables score ~.49-.51 and maj .5919. Never rerun.
Reclass: ruler_insufficiency (floor). Same set: exact-symmetry null 18/18 IDENTICAL with
transform flags measured from arrays, not declared = instrument_positive.
Axes: Q N (acquisition arm could not fail) / S - / W - / R N (acq) Y (symmetry) / B N / Rep N / M N.

SV-02 H1/H0 CEGIS alpha (cegis_boolean_v1). Hist: solved of 12 per cell 2-3; every
unsolved row BUDGET_VM_OPS; H1 relevance inert; H0 library cells had ZERO eligible input
(no shared abstractions on the split); fixed enumeration order means only cost can differ.
Possible contamination of S01/S11 library unresolved (UNK). Reclass: world_insufficiency
(task family cannot exhibit reuse) + statistical_insufficiency. Axes: Q P / S Y / W N / R P (leak checker) / B Y / Rep N / M N.

SV-03 H5-1 ECA encoding. Hist: 256 rules, 224 classes, 0 disagreements with published map;
reach quantities at analytic bounds by construction. Reclass: ruler_insufficiency for the
evolvability question (calibration only); known-answer calibration positive.
Axes: Q N / R Y (calibration) / others N.

SV-04 Autonomous tick and S1 over evaluate_bitstring. Hist: 246 pytest rows in the
production register (quarantined by errata view); tick read 0 fossils on 45/45 ticks on
09-11 ("sfe db not found"); S1 8/4 p=.194. Reclass: provenance_defect + implementation_
defect (pre-09-12) ; S1 statistical_insufficiency on a world (onemax) that leaks exact
Hamming information per fossil. Axes: Q P / W N / R P / B Y / Rep N / M N.

SV-05 Infrastructure qualification (point release, 11 canaries). Hist: 10 production
defects found and fixed; QUALIFIED_FOR_CAMPAIGN; never exercised on a real campaign
(queue empty after 09-18). Reclass: instrument_positive (engineering), unexercised.

SV-06 Process failures that mimic science (consumer 4h47m older than its "closed" fix, 48
rows lost; 85,727 phantom experiments; 13-row stall gap flagged before being read as rule
space). Reclass: implementation_defect; the stall-gap flag is a correctly prevented
false_positive.

### Daedalus / SFE

SD-01 Gen-2 canary "no information topology improved best objective; all 0.958".
Verified apparatus: identical RNG seed (seed_root+1) and identical initial population in
every world; W1/W2 identical trajectories; W3/W5 identical payload; 2-flip mutation keeps
Hamming-distance parity; re-derived initial distances 9/13/16/14 so the leading lineage
(odd) cannot pass 23/24. [IMPL + re-derivation; dominance INFER]
- Reclass: search_insufficiency (parity-locked operator) + implementation_defect (arms
  collapse by shared streams). The null says nothing about information topology.
- Axes: Q N / S N (bitstring has nothing to execute) / W N / R N / B P (W1 isolated) / Rep N / M N.

SD-02 D-7 "CERTIFIED_NONLINEAR_WORMHOLE". Hist: 2,197-state mod-13 machine with a barrier
certified by exact closure + invariant; history-conditioned synthesizer crosses in median
23.5 evals vs 73 (best history-free), 65.5 (edges removed), 86 (shuffled edges); 7
auditors re-implemented and found it SOUND; never challenged later.
- Reclass: instrument_positive / survives_as_anomaly (toy, designer-built barrier; auditors
  likely the same model family, UNK).
- Axes: Q Y / S Y / W Y (certified unreachable without the transform) / R Y (exact certifier) / B Y / Rep P / M P (edge removal/shuffle ablations).

SD-03 D-13 corpus (WOW). Hist: 71,683 executions, 7 successes (all stackvm); 85/87
selection events fully tied (seeded tie-break drift); 89.3% of failures under 100-400 step
ceilings; tree-GP 0.000 even on identity (suspected adapter defect).
- Reclass: search_insufficiency (selection was drift) + implementation_defect (tie-break,
  adapters, step ceilings). A substrate with loops and memory was never exercised.
- Axes: Q P / S P (stackvm capable in principle, INFER) / W P / R P / B N / Rep N / M N.

SD-04 Search Physics cross-representation assay. Hist: a searchability gain was
manufactured by comparing max-over-300 with max-over-12 (+.0741 vs +.0001 under an
equal-budget null); after repair, no common viable world (|W*|=0). Reclass:
false_positive (unequal max-over-N) then world_insufficiency.

SD-05 stackvm admission language qualified -> compromised 12 minutes later (saturating
observable, non-exchangeable sampler, selection-detector nulls, spec multiplicity).
Reclass: ruler_insufficiency (self-caught).

SD-06 Selection boundary. Hist: candidate-conditional tests hold level under specimen
selection (.0533 vs .0647) but best-of-20 observables reject at .648; ~84% of random stackvm
programs inert. Reclass: instrument_positive (statistics; reusable lesson).

SD-07 D-10 relevance keying. Hist: relevance structure exists (artifact x task interaction
69.3% of variance; oracle .042->.375) but not recoverable through the syntax-only interface.
Reclass: organism_insufficiency (interface) with an oracle demonstrating W -- a good
geometry: oracle proves the structure exists, the organism interface cannot reach it.

SD-08 D-6A / D-8. Hist: P3 causal findability FAIL (+.010, CI [-.010,+.042]); transfer
0/144; D-8 S0 NO_EFFECT. Reclass: true_negative at toy scale only, plausibly world-bounded
(unrelated-by-construction tasks). Axes: Q Y / S P / W P / R P / B Y / Rep N / M N.

### Apollo

SP-01 v2 "hybrid LLM wins" / decorative compositions. CORR: the report's own table lists
0% DeepSeek calls for the "50/50" runs; LLM survival hidden by a lineage-wipe bug (fixed
e94ca44b1); baseline matrix 0/5 elites with lift over the best single primitive; the gate
measured output change. Reclass: false_positive + implementation_defect.

SP-02 Crossover crosses a multi-op valley (06-16; type-bridge 08-19). Hist: 1-edit
neighbourhoods of both parents (117/92 neighbours) stay at .30; 8,000 random single-step
walks (depth 4) reach the solver 0 times; 2,000 crossover ops solve at 6.1%; A/B de novo
4/5 (xover .3) vs 0/5 (xover 0) over 5 seeds x 400 gens; type-bridge replay A3 3/5 vs A2 0/5,
8.6x slower on a drifted operator set. [CONFIRMED HIST/IMPL]
- Apparatus caveat (confirmed in the findings file): the "ingredients" seeding places the
  two exact parents whose one-point splice IS the solver; recombine() always ends in the
  second parent's terminal. The geometry tests "can one splice assemble a known two-part
  solution present in the population", not open-ended discovery.
- Reclass: instrument_positive (operator ablation shows crossover necessary within this
  planted geometry). Representation-bound; contrasts with NPE/SFE/CW01 where recombination
  is null/harmful (cross-group, not verified here).
- Axes: Q Y / S Y (validated solver, construct validity .30/.30 vs 1.00) / W Y / R Y (1-edit census) / B Y (single-step control) / Rep P (n=5 replay, drifted substrate) / M P (operator on/off).

SP-03 Climb to 0.833 and O1 enumeration. Hist: dispatch arc 0.392->0.833; 5/5 widenings
human-supplied; O1 enumeration reaches exactly 0.833 with the identical per-subset profile;
evolution used 3,144 evals vs 1,687,896 (537x). Reclass: true_negative for "evolution
invents" (organism_insufficiency by construction: the registry is the ceiling);
instrument_positive for O1 as ground truth. Axes: Q Y / S Y / W P / R Y / B Y / Rep P / M N.

SP-04 E9 blind battery. Hist: mix-adjusted .0667 vs home .6000; 40/42 abstained, 0 guesses;
mechanism: transformer preconditions key on problem_text surface (verified
blackboard_ops_compare.py:25 startswith("is ")). Reclass: retro-converts every home
accuracy number to false_positive (author-fit world/parser co-adaptation); E9 itself is an
instrument_positive. Axes: Q Y / R Y (positive control: E9 reproduced exactly by Lexis
adapter and rebuilt e9_score.py) / Rep P (Artemis R-20 third author, REPORTED) / M Y (precondition located).

SP-05 Gen-2 S1 "no nontrivial source population at feasible cost". Hist: budgets 80-600;
reachable solves {identity, x+1}; tree-GP 0.000 everywhere; dead (random) world MAP-Elites
coverage .1875 equals live world, QD .833 vs .083. Reclass: search_insufficiency +
implementation_defect (adapter suspect); the dead-world control is an instrument_positive
(QD coverage is an unsafe observable). Axes: Q P / S P / W P / R P / B Y (dead world) / Rep N / M N.

SP-06 0.558 plateau and "aggregate sub-pipeline falsified". CORR: plateau = single-terminal
metric artifact + canary floor; the falsification was a guard reading a slot nothing wrote
(false negative by wiring). Reclass: ruler_insufficiency; implementation_defect.

SP-07 Task 2 (state injection: raw / oracle-state / corrupted arms). Accepted 09-11, never
preregistered or run (verified absence). Status UNK. This was the one experiment that
could separate parser failure from routing/inference failure.

### Lexis

SL-01 Exact ceiling 0.8333 of Apollo's admissible language; all 20 unreached tasks dE
(outside operator closure), dS = 0. Method: proved answer-relevant projection D (17/23
slots), per-task reachable-answer closure (5,029 states) and joint product BFS (484,218
states). Self-correction: "substrate ceiling" -> "admissibility rules" (unrestricted pool
reaches 107/120 by unconditional guessing). [CONFIRMED HIST]
- Reclass: instrument_positive; establishes organism (vocabulary) insufficiency
  constructively for that battery.
- Axes: Q Y (pre-committed kill could fire) / S Y (exhaustive) / W Y / R Y (replays Apollo's own evaluator; congruence audit) / B Y / Rep P (re-run 09-11, count 5026->5029 documented) / M -.

SL-02 G7 blind re-measure. Hist: positive controls P1 (.8333 home) and P2 (2/42, 40
abstain) MATCH; exact ceiling over Charon 2/42; 15/42 tasks unrecognised by any clean-pool
operator; compute+readout pair +4/6 robust over all 24 permutations. Reclass:
instrument_positive. Axes: Q Y / R Y / B Y / Rep P / M P.

SL-03 Forge G1 ablation census. Hist: 2,103 deltas, 89.73% zero, 86.19% of called
primitives decoration, 5.94% load-bearing; the forge's anti-decoration gate never fired
(cannot fire on an all-zero tool). Reproduced by Artemis D002-07 (REPORTED). Reclass:
instrument_positive (census) + ruler_insufficiency of the forge gate.

SL-04 Pair regresses the production organism (9 correct->wrong flips via a write-write
hazard) unless placed compute_first. Reclass: ruler_insufficiency class: closure ceilings
report the best program in the closure and hide placement hazards.

SL-05 HC-T01 K7 kill degenerate at its window (Spearman exactly -1.0000); the
accessibility detector largely reads "genome has >= 1 production rule". Reclass:
ruler_insufficiency (a kill that could not fail).

SL-06 LEX-07 leakage-detector cheat control never run; identity re-adjudication never
happened (verified). Status UNK; every "no leak" reading in the slice is unqualified.

-----------------------------------------------------------------------------------------
## 4. Which nulls were apparatus-bounded, and by what

| null | bounding apparatus | evidence |
|---|---|---|
| SSF no foothold | search (operator/budget); S and W proven by hand-written organisms | SA-04 |
| W2_K2 0/60 | search or organism, inseparable (both held fixed) | SA-05 |
| C5 flat elite | compute 9k-36k; estimator mismatch with DF | SA-11 |
| WSE E1-E3 extinction | pressure schedule (cost from generation 0) | SA-03 |
| C4 REPRESENTATION_BLOCKED | total interpreter has no fault event | SA-10, vm.py:181 |
| C4/C5 "length protects" | count-fixing ruler | SA-10, D084 |
| C6 "no discovery" | detectors saturated / UNABLE / 25%-0% power | SA-13 |
| DENOVO 0/80 | exposure ~0.1 expected events under measured prior (INFER) | SA-16 |
| ENVGATE-02 rescue | 1-2 non-tied blocks | SA-21 |
| Fossil producer | corpus structure (no player identity; disjoint populations) | SA-01 |
| Vivarium C3-2 acquisition | ruler floor (single attainable value) | SV-01 |
| H1/H0 library | task family has zero shared abstractions | SV-02 |
| H5-1 | analytic bounds by construction | SV-03 |
| SFE canary | identical streams + parity-preserving mutation | SD-01 |
| D-13 sterility | selection drift, tie-break, adapters, step ceilings | SD-03 |
| Apollo S1 | budgets 80-600, adapter defect, 12-case tasks | SP-05 |
| Apollo 0.833 ceiling | registry of human solvers (exhaustible) | SP-03, SL-01 |
| Apollo E9 0.0667 | author-fit surface parsers (organism and world co-adapted) | SP-04 |
| LLM mutation "adds nothing" | tested only where the space was already exhausted (ceiling at gen 131) | Apollo dossier s9 |

Candidates for true_negative (bounded): D-6A transfer 0/144 and D-8 NO_EFFECT (toy);
Apollo "evolution invents operators" (cannot, by construction -- a definitional negative);
ENVGATE-02 window-rescue model (frozen gate failed, though thinly powered).

-----------------------------------------------------------------------------------------
## 5. Instruments: demonstrated detectability vs not

Demonstrated (planted positive and/or matched negative on the same substrate):
1. Taint VM + lineage core (Archaeon): differential test vs frozen VM on 6,000 random
   tapes (both copy modes) and 10 known-answer births (self-copy; inert host executing a
   resident copier is NOT the ancestor; host mutation contributing no bytes stays out;
   recombination both contributors; mutation byte = new material; migration; inflow origin;
   inserted control cannot become random; block-15 host labels collapse to one lineage;
   block-13 near-copier). Used to show parent-chain labels inflate establishment 8-42x.
   [IMPL: archaeon/tests/test_lineage_attribution.py l.41-152]
2. ENVGATE paired-arm geometry: equal-size sham block (U 47 vs SHAM 45) and band block
   (1); byte-identical arrival streams across arms; frozen code-hash launch gate. [HIST]
3. WSE held-out confirmation (48 episodes): caught training .9375 -> .53 and .875 -> .60.
   [HIST: WSE packet l.235-237, 369-371]
4. Opcode-permuted incompetent-import control: detected takeover-as-mechanics. [HIST]
5. Copier census with substrate ablation (no COPY -> 0 in 1.2e7). [HIST]
6. Lexis exact closure with positive controls; permutation null caught a candidates[0]
   fallback ("solves 3/5 temporal" -> 0). [HIST]
7. Blind-author re-measure (E9/G7) with positive controls reproducing the known result.
   [HIST]
8. Apollo O1 enumerator (known-organism positive control; two invalid O1 runs that would
   have produced false wins were caught and archived) and the dead-world control. [HIST]
9. Vivarium exact-symmetry null (measured transform flags) and library_leak.py (fired on
   a demo library containing a task solution). [HIST]
10. Daedalus selection-boundary toolkit and MHC qualification (power curves, admission FP
    0/20; states its own blindness). Qualified, never applied. [REPORTED]
11. Benchmark attack (13 trivial heuristics; oracle .925 beat a .833 portfolio claim). [HIST]

Not demonstrated or demonstrated weak:
- C6/Deep Frontier eleven detectors: planted catch 25% / 0% at 1% false-fire; four
  structurally UNABLE; saturated; admission hard-coded. Yet they steered 3.72M evaluations.
- Archaeon D1-D6 on the live corpus (ineligible); synthetic calibration only.
- Z80 mechanical flags (label-reading until repair); LOTTERY band too wide to fail easily.
- SFE epistemic counters (green on contradicted execution, TODO D6-1; evidence_class does
  not consult config_match, crawler INFER); ledger integrity verifies chain, not content.
- Vivarium ca_density at_T/stable masks (single attainable value for random rules).
- Lexis/Apollo leakage detector (LEX-07 cheat control never run).
- HC-T01 K7 kill (degenerate).

-----------------------------------------------------------------------------------------
## 6. Most informative experimental geometries (worth carrying forward as patterns)

G1. Environment-as-variable with frozen organism physics (ENVGATE): one held
    configuration; arms differ only in an input-distribution transform; equal-size sham
    arm; byte-identical arrival streams; genetic-identity endpoints from a material tracer;
    preregistered gate with stop rule. Weakness: rare events -> thin rescue contrasts.
G2. Constructive demand map before evolution (SSF boundary map): hand-written organism
    family (logger, last-value, selective) scored under the economics first; then ask
    whether evolution finds what is known to win. Localizes a null to search.
G3. Curriculum + untrained-generalization probe + matched-budget direct-search control +
    mature-solver control (delay ladder). Missing piece: a cell where the probed dimension
    cannot be ignored, and an ablation.
G4. Incompetent-but-structurally-matched control for transfer/import (opcode-permuted
    manifests: same length, multiset, operands), with dose and offspring-cap arms and an
    origin-share readout (diversity readouts are blind to takeover).
G5. Operator ablation across a certified valley (Apollo): 1-edit neighbourhood census of
    the parents, large random-walk control, operator on/off A/B. Must be repeated without
    planting the exact splice parents.
G6. Exact closure as ground truth for expressiveness vs search (Lexis): prove a
    congruent projection, enumerate reachable states, split unreached tasks into dE
    (vocabulary) vs dS (routing). Requires a small finite substrate.
G7. Base-rate measurement with substrate ablation before interpreting rare events
    (copier census), and power computed from the measured prior.
G8. Certified-barrier synthesis (D-7): region provably unreachable by base physics;
    history-conditioned vs history-free vs edge-removed vs edge-shuffled.
G9. Blind-author re-measure with positive controls that must reproduce a known number.
G10. Equal-total-compute controls and pre-solution world screens (C5), and the
    "replication digest-for-digest" check (C4/C5) -- noting deterministic replay is not
    replication.
G11. Oracle-reachable vs interface-reachable split (D-10): an oracle shows structure
    exists; the organism interface shows whether it can be reached.

-----------------------------------------------------------------------------------------
## 7. Failure shapes (how this apparatus fooled the program)

| class | direction | instance | cite |
|---|---|---|---|
| label-for-property | false positive | Z80 spontaneous flag read spec["init"]; 26 -> 0 | archaeon/z80atlas/engine.py:448 |
| label-for-property | false positive (inflation) | parent-chain establishment 8-42x genetic | archaeon/envgate2/VERDICT_2026-09-26.md |
| estimator mismatch | spurious contradiction | DF training max vs C5 held-out screen | archaeon/campaign6/segment.py:219 |
| training-battery luck | false positive | .9375 train -> .53 held-out; .875 -> .60 | REVIEW_PACKET_WSE_ARCHITECTURE l.235, 369 |
| shared/hidden random streams | forced null / spurious difference | canary identical RNG; P-boom run_id seed | sfe/canary.py:78; frontier DF-015 |
| operator invariant | forced null | 2-flip parity caps odd lineage at 23/24 | sfe/canary.py:40-45 |
| count-fixing ruler | manufactured coordinate | "length protects" 4/7 vanish under Bernoulli(f) | BOUNDARY_REPORT_CYCLE5 l.82-89 |
| ruler floor | false negative | C3-2 random rules 0.0 under both masks | commit 30e97ed94 |
| ruler saturation / weak power | false negative (and steering on noise) | C6 detectors 25%/0%; 1.66M firings | archaeon/campaign6/DECISIONS.md D6-010 |
| import mechanics | false positive | incompetent imports take over 11-12/12 | WSE packet s7.4 |
| stratification artefact | false positive | basin-share rho -.568 two-point | Archaeon dossier T5 |
| unequal max-over-N | false positive | Search Physics +.0741 vs +.0001 | Daedalus dossier T10 |
| author fit | false positive | Apollo .60 home -> .0667 blind | apollo/src/blackboard_ops_compare.py:25 |
| decorative composition | false positive | gate on output change; 0/5 lift | Apollo dossier T3 |
| total interpreter | question unaskable | no fault event; REPRESENTATION_BLOCKED | proteus/foundry/vm.py:181 |
| pressure before capability | false negative | E1-E3 extinction 18/18 cells | archaeon/wse/READOUT_v01.md (HIST) |
| selection as drift | false negative | D-13 85/87 selections fully tied | WOW packet l.44-46 |
| exhaustible world | vacuous discovery | O1 reaches the same .833 | Apollo dossier T6 |
| float ties | false positive and false negative | S7 / ARCH-46A | archaeon/docs/h0h5/ARCH46A_* (HIST) |
| post-exposure amendment | contaminated confirmation | E-003 C4.2 17 min after exposure | Harmonia audit item H (HIST) |
| unverified gate executed | provenance defect | DF ran with G6-0 false, ADMITTED hard-coded | OPERATOR_EXECUTION_AUTHORIZED.json; scheduler.py:178 |
| process state lies | lost rows / phantom data | consumer 4h47m older than fix; 85,727 phantoms | Vivarium dossier T1, T2 |
| control that cannot fail | false comfort | HC-T01 K7; Vivarium acquisition arm; LEX-07 never run | Lexis dossier T6, T7 |
| seeded answer in population | inflated discovery claim | Apollo ingredients = exact splice parents | apollo/pivot/recombination_findings_2026-06-16.md |
| underpowered test vs measured prior | false negative | DENOVO-01 ~0.1 expected events (INFER) | archaeon/z80atlas/denovo/PREREG.json |

-----------------------------------------------------------------------------------------
## 8. Design implications for Phase 3 (each tied to evidence)

D1. Require a constructive capacity proof and a world-demand proof for every target
    phenomenon before any evolutionary null is admissible: a hand-built organism that
    solves the world in the organism's own language, plus an ablated-capability baseline
    that fails. SSF (SA-04) is the model; W2_K2 (SA-05) shows what is lost without it.
D2. Treat organism primitives, mutation operator and search policy as separately varied,
    declared factors. The W2_K2 ceiling is uninterpretable because they moved together;
    Apollo SP-02 shows operator choice alone can flip 0/5 to 4/5.
D3. One declared estimator per claim: held-out readouts mandatory for capability claims;
    training maxima can be telemetry only. Verified mismatch in SA-11; training luck in
    SA-05.
D4. Material provenance is part of the organism substrate, not a later lens: a
    label-propagating shadow executor that must equal the real one exactly, with
    known-answer births, from day one (SA-15, SA-20, SA-21; taint VM tests).
D5. Random streams are design objects: key streams by declared stream_key; prove arms
    differ only in the manipulated factor; audit operator invariants (parity) before
    interpreting a convergent null (SD-01, SA-14).
D6. Rulers must pass planted-positive, matched-negative and cheat controls on the same
    substrate before they may steer allocation or suppress branches; publish their power
    (C6 25%/0% steered 3.72M evaluations, SA-13; LEX-07 never run).
D7. Damage/robustness rulers must be dilution-neutral when organism size changes
    (fraction-fixing, scattered); count-fixing rulers manufacture length effects (SA-10).
D8. Representation features that make questions askable (fault events, addressing,
    call/stack, persistence) must be explicit axes; a total interpreter makes failure-
    boundary questions unaskable (SA-10, SA-12).
D9. Pressure timing is a developmental variable: costs from generation 0 extinguish
    capability (SA-03); a staged curriculum produced the only generalization positive
    (SA-06). Developmental trajectories need instrumentation separating construction from
    selection of pre-existing variants (5/12 seeds in SA-06).
D10. Worlds must be scalable past exhaustive enumeration yet keep a small exactly-solvable
     core: exhaustibility makes "evolution discovered" vacuous (SP-03) but enables exact
     closure rulers that split vocabulary from search (SL-01). Plan both regimes.
D11. World/task authorship must be independent of organism and ruler authorship, with a
     blind-author re-measure gate (SP-04, SL-02).
D12. Imports/transfer claims require incompetent structural-match controls and
     origin-share readouts; diversity metrics are blind to takeover (SA-07, SA-08).
D13. Power from measured base rates before running rare-event assays (SA-16, SA-17,
     SA-21; S1 n=12 SV-04).
D14. Provenance at evolutionary scale must be segment-anchored, not one service call per
     evaluation (SFE ~400-900 events/s; Vivarium 95-193 s per row with 0.1 s of science;
     Vivarium's own C6 segment proposal).
D15. Keep frozen-code hashing, prereg-before-run, and "frozen verdict != adjudication"
     records (ENVGATE) -- they localized defects without rewriting history; forbid
     post-exposure amendment of confirmatory rules (SA-23).
D16. The highest cognitive demand ever posed here was 2-slot keyed recall; Phase 3 must
     add worlds whose demands (hidden-state inference, multi-step composition) are
     certified by an ablated baseline AND reachable by at least one constructed organism,
     or nulls about reasoning primitives remain uninformative (s2 table).

-----------------------------------------------------------------------------------------
## 9. Open questions (unresolved by the record)

1. Is the W2_K2 ceiling an organism limit, an operator limit, or a world-decomposition
   artefact (half-credit shelf)? Never separated.
2. Is the delay-invariant reader a capability or a sign the delay knob was ignorable?
   No ablation; no non-ignorable delay cell tested.
3. Does the frontier N family climb on HELD-OUT episodes at matched compute?
4. Do C4-08/C5-08 robustness-by-length readings survive a scattered Bernoulli(f) ruler?
5. What carries ENVGATE-02 BAND0/R128 establishments at ~7x the frozen prediction?
6. Does Apollo's crossover advantage survive without planting the splice parents, and on
   a representation where recombination was null/harmful elsewhere?
7. Would Apollo Task 2 (oracle-state injection) show routing works once parsing is given?
8. Was any C6 ruler ever admitted by Harmonia? None found.
9. Is the canary parity reading confirmed by a full rerun (only initial state re-derived)?
10. Are the D-13 tree-GP/PushGP adapters defective? Is D-7 robust to an independent,
    non-LLM-family reimplementation?
11. Was the H1/H0 S01/S11 library the leaky demo library (tgt-11 contamination)?
12. Custody and durability of off-repo evidence (ENVGATE rows, BEE traced logs, SFE
    ledgers, Apollo run dirs, F:/SerendipityD).

-----------------------------------------------------------------------------------------
## 10. Files opened in this session

docs/phase3/intake/sisyphus/REPORT.md
docs/phase3/intake/sisyphus/seats/{Archaeon,Vivarium,Daedalus,Apollo,Lexis}.md
docs/phase3/intake/sisyphus/seats/_frag/{Archaeon,Vivarium,Daedalus,Apollo,Lexis}.{engines,artifacts}.jsonl
SerendipityFoundry/SerendipityFoundryEngine/sfe/canary.py
SerendipityFoundry/SerendipityFoundryEngine/sfe/executors.py (l.1-125)
SerendipityFoundry/D7/README.md (l.1-45)
SerendipityFoundry/wow/WOW_ARCHAEOLOGY_REVIEW_PACKET.txt (grep)
archaeon/frontier/scheduler.py (l.165-195); archaeon/frontier/digest.py (l.55-85)
archaeon/frontier/OPERATOR_EXECUTION_AUTHORIZED.json; archaeon/frontier/DECISIONS.md (l.132-145, grep)
archaeon/campaign6/segment.py (l.217-268, 305-330); archaeon/campaign6/DECISIONS.md (D6-010)
archaeon/campaign6/observatory/ADMISSION_PACKET_v0.1.md (grep)
roles/Archaeon/REVIEW_PACKET_WSE_ARCHITECTURE_2026-09-17.md (l.235-237, 355-445, 575-650)
roles/Archaeon/REVIEW_PACKET_CAMPAIGN4_2026-09-18.md (l.20-100)
roles/Archaeon/REVIEW_PACKET_CAMPAIGN5_2026-09-18.md (l.40-100, 175-200)
proteus/foundry/vm.py (l.165-200)
archaeon/z80atlas/engine.py (grep l.175, 448, 450); archaeon/z80atlas/scheduler.py (l.250-262)
archaeon/z80atlas/pivot/Z80ATLAS_RULINGS_FOLLOWUP_REVIEW_2026-09-24.md (l.14-40, 115-140)
archaeon/z80atlas/denovo/RESULTS.json; archaeon/z80atlas/denovo/PREREG.json
archaeon/envgate/ADJUDICATION_ADDENDUM_2026-09-24.md; archaeon/envgate/ENVGATE01_REVIEW_2026-09-24.md (grep)
archaeon/envgate2/VERDICT_2026-09-26.md
archaeon/lineage/taint_vm.py (l.1-60); archaeon/lineage/core.py (l.1-80)
archaeon/tests/test_lineage_attribution.py (grep, l.140-160)
roles/Nestor/campaigns/cw01-2026-09-17/loop/BOUNDARY_REPORT_CYCLE5_2026-09-19.md (grep)
vivarium/viv/deadman.py (grep); git show 30e97ed94
apollo/pivot/recombination_findings_2026-06-16.md; apollo/cycles/type_bridge/RESULT.json
apollo/src/blackboard_evolve.py (l.795-810); apollo/src/blackboard_ops_compare.py (grep)
apollo/cycles/campaign_20260825/E9_FINDINGS.md (grep)
roles/Lexis/notes/STEP1_CEILING_CLOSED_2026-08-25.md (l.1-80); roles/Lexis/notes/G7_CHARON_2026-09-01.md (grep)
roles/base-role/RESPONSIBILITIES.md (l.215-224)
