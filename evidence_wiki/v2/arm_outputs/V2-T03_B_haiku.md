# PROPOSAL V2-T03 (arm B)

## Hypothesis

A learner operating in a procedurally generated world reaches goal states at a rate exceeding what
an **exchangeability-broken control** predicts, where the control's superiority derives from prior
observation of the task distribution itself (not from inherent task structure). Concretely: if the
learner is initialized with priors extracted from a TRAINING world population P_train but tested on
a TEST world population P_test drawn from the same generative procedure, it must outperform a
baseline constructed by pooling uniform random actions, frequency-matched action selection from
P_train, and action distributions learned from a disjoint HELD-OUT world population P_control
(which shares generative family but was never observed by the learner in any form). The learner's
advantage is attributed to world-conditioned strategic reasoning, not mere action frequency
absorption.

## Motivating evidence

- `roles/Ludus/CHARTER.md` (§5-7): outcomes and decisions are mechanically separable; the learner
  must be evaluated on decision quality under uncertainty, not on win/loss, and counterfactual
  replay under multiple stochastic realizations is the standard instrument for decision-quality
  measurement in game worlds (direct read, lines 123-161).
- `roles/Ludus/ATLAS_OF_WORLDS.md`: procedurally generated worlds can be structurally classified
  and tagged with exogenous-process, loss-shape, interaction-type vectors (confirmed in review
  packets); this permits stratified control selection — holding strategic family constant while
  breaking the learner's observational access (confirming `feedback_control_must_break_the_selection_relation`).
- D-5 **contradiction cluster** (Evidence Wiki, relation R-e68c9331eca2): history advantage
  (+10.95pp in D-5 blind program-ecology substrate) failed to replicate in D-8 blind foundry-ecology
  substrate (NO_EFFECT verdict). The differing dimension was **substrate ecology** and **baseline
  selection** (D-5 used GA-based M0b, D-8 used metered fixed budget); this motivates V2-T03's
  stratified control design to isolate world-induced advantage from substrate artifacts.
- `roles/Aporia/resume_aporia.md` (§-0.4 to -0.5): cost-sensitive baselines matter; controls
  must include random action, frequency-matched action, and learned-from-disjoint-data variants,
  separated at execution time to avoid confounding the learner's strategic cost with its mere
  probability-matching behavior (read lines 94-150).
- Memory index `feedback_control_must_break_the_selection_relation`: "a control drawn from the
  treatment's selection relation IS the treatment; exchangeability dominates matching" — direct
  consequence: baseline must not be a subset or distillation of the learner's own training
  distribution.

## Prospective predictions

1. **Primary stand (learner advantage)**: mean solve rate (binary success on goal reaching) on P_test
   must exceed the three-component baseline (random + frequency-matched + held-out-learned) by at
   least 15 percentage points, with 95% CI not touching zero. This operationalizes "better than
   chance" by requiring the learner to beat a composite control that already captures action
   distribution and prior-world strategic structure.
2. **Baseline-component ranking (secondary, falsifiable)**: if the learner's advantage derives from
   memorizing training-world action frequencies (rather than world-conditioned reasoning), the
   "frequency-matched-from-P_train" component should approach or exceed the learner's performance
   on P_test. Predicted: learner >> frequency-matched > random, with a visible 5pp+ gap.
3. **Held-out baseline floor (tertiary, calibration check)**: the held-out-learned component
   (trained on P_control, tested on P_test) should show minimal advantage over random (0-3pp
   expected), since P_control and P_test share generative family but were observationally
   independent. If held-out > learner, the advantage is attributable to task-family generalization,
   not world-specific learning.
4. **Null-consistent-with-substrate-failure (falsifiable alternative)**: because baseline selection
   was critical in D-5/D-8 contradictions, this experiment may find learner ≈ frequency-matched
   (both ~55% on a moderately hard goal), meaning the learner absorbed action frequency but never
   developed world-conditioned strategy — a null result on reasoning, not a null result on learning.

## Experiment

**Phase 0 (preflight: engineering seeds only, seeds 1000-1999)**

1. Define the procedural world generator `G` with three instantiation modes: `train(seed)` produces
   worlds for the learner's training; `test(seed)` produces fresh worlds for evaluation (same
   generator, different seed); `control(seed)` produces a third independent stream (used only to
   train the held-out baseline, never seen by the main learner). All seeds are deterministic and
   reproducible.
2. Sample five representative world configurations from P_test (open the goal variety, difficulty,
   and decision density), and set target solve rates T by running the random-action baseline (no
   learner, pure uniform action sampling) on each. This establishes the **attainable range** for
   solve rates: e.g., if random achieves 18% on world A and 42% on world B, the ladder is bounded.
   Falsifier F1 depends on this: if all five worlds have random > 45%, the task family is too easy
   and the ceiling is gone.
3. Measure the empirical **cost per goal** (e.g., wall-clock time, state evaluations, action
   samples) for the learner to reach one goal, stratified by world and difficulty class. This sizes
   Phase 1 compute budget (all learners are bounded by evaluation count, not time, per LUDUS
   charter). Measure cost for each baseline component separately.
4. Preregister the specific worlds (P_train count, P_test count, P_control count), learner
   architecture (if any hyperparameters vary, they must be frozen here, not in Phase 1), baseline
   component budgets (same evaluation cap as the learner, to ensure fair comparison), and
   statistical powering (sample size per world × world count, chosen to reach CI width ≤ 10pp on
   the primary statistic).

**Phase 1 (evidence: seeds 4000-4999 / 7000-7999, never engineering seeds)**

1. Train the learner on P_train (fixed world-count, fixed budget per world) to convergence or
   budget exhaustion. Learner produces a policy π_learn (world → action distribution).
2. In parallel, train three baselines on held-out disjoint data:
   - `B_random`: trivial, returns uniform action distribution for any world.
   - `B_freq`: trained on P_control (the disjoint held-out world stream), produces
     `P(action | world_family)` frequency distributions.
   - `B_oracle_freq`: trained on P_test worlds themselves (oracle version of B_freq, as an
     upper-bound sanity check that the task is learnable at all from frequency matching).
3. Evaluate all four (learner + three baselines) on P_test worlds:
   - For each test world w ∈ P_test: run the learner (π_learn) and each baseline (π_random,
     π_freq, π_oracle) on the same sequence of goal-reaching trials, seeded identically,
     capped at the same evaluation budget per component.
   - Record: solved (yes/no), steps-to-goal, wall-clock, evaluation count, decision sequence.
4. Compute the primary statistic: mean solve rate (learner − baseline_composite), where
   baseline_composite is the average of B_random and B_freq (the two fully-disjoint components).
   This is a paired within-world comparison.
5. Report stratified breakdown: results by world family, by difficulty class (if applicable), and
   separately for first-goal-reaching vs. any-goal-reaching, to detect any systematic failures.

## Controls

- **Exchangeability-broken disjoint-data baseline**: P_train and P_test are independent samples
  from the same generator; P_control is a third independent stream. None of P_control's worlds
  appear in the learner's training. This breaks the learner's selection relation: if the learner
  memorized P_train's action frequencies, B_freq (trained on P_control) will not capture that
  memorization, so learner will appear to have an advantage even though neither learned strategy.
- **Frequency-matched component control**: B_freq is not a random policy; it learned structure
  from P_control, which may contain genuine strategic insights that transfer to P_test (since both
  share the generator family). This baseline measures whether learning-from-disjoint-data is enough
  to reach the learner's performance. If B_freq ≈ learner, strategy transfer is absent.
- **Oracle frequency component (B_oracle_freq)**: trained on P_test itself, provides an upper
  bound on what frequency matching alone can achieve. If B_oracle ≈ learner, the learner learned
  no strategy beyond frequency. If learner >> B_oracle, the learner achieved something frequency
  matching never can (impossible; this detects implementer error).
- **Difficulty-stratified evaluation**: report results separately for easy, medium, hard goal
  classes (if the generator supports such classification), to test whether the learner's advantage
  is stable across problem difficulty or collapses on hard tasks (a signature of shallow learning).
- **Matched evaluation budget**: learner and all baselines are capped at the same evaluation count
  per world, ensuring no component gets a stealth advantage from more computation.

## Confound defenses

- **World-distribution confound**: if P_train, P_test, and P_control are sampled from different
  regions of the generative space, a learner advantage could reflect task overlap, not reasoning.
  Defense: all three streams use the same random-seed stream and generator parameters, differing
  only in seed value (ensuring statistical independence, not structural independence). Phase 0
  step 2 explicitly measures random-action solve rates, bounding any task-hardness differences.
- **Baseline under-specification confound**: if B_freq is poorly trained (e.g., too few P_control
  worlds, too-short training), it may underestimate the achievable performance from frequency
  learning, making the learner look better than it is. Defense: Phase 0 step 3 measures empirical
  cost curves; Phase 1 gives all baselines the same total evaluation budget as the learner, ensuring
  fair comparison (no hidden advantage to complexity).
- **Solver-selection confound**: if the learner uses a different action sampler or decision rule
  than the baselines (e.g., learner uses argmax-softmax, baselines sample uniformly), the learner's
  advantage may reflect its decision rule, not learned strategy. Defense: all components use
  identical action sampling logic; the only difference is the policy π — all policies are
  probability distributions over actions, sampled identically.
- **Goal-variability confound**: if some goals are easier than others, and the learner is lucky to
  face easier goals while baselines face harder ones, the learner's advantage is an artifact.
  Defense: within-world paired design — learner and baselines run on identical goal sequences,
  identical random seeds for world state, differing only in their policy π.
- **Hindsight selection confound**: if P_test is chosen after observing partial learner results
  (e.g., picking worlds where the learner does well), the reported advantage is not predictive of
  generalization. Defense: P_test is preregistered in Phase 0 before any Phase 1 results are read;
  the world sample is fixed before evidence collection begins.

## Preregistered falsifiers (numeric thresholds)

- **F1 (primary, reachability check, Phase 0)**: on the five P_test world samples, random-action
  baseline must show variance in solve rate (empirical range > 20pp) and mean > 15%. If random >
  50% on all five or random < 5% on all five, the task family is too easy (ceiling) or too hard
  (floor) and provides no discriminative signal. If triggered: TASK_FAMILY_UNFIT, redesign world
  difficulty before Phase 1.
- **F2 (primary, learner advantage)**: mean solve rate difference (learner − baseline_composite)
  must exceed 15pp on P_test, with 95% CI lower bound > 0pp. If learner − baseline < 15pp or CI
  touches zero: LEARNER_ADVANTAGE_NOT_ESTABLISHED. (Note: "better than chance" is operationalized
  as beating a composite control that already captures action frequency and prior-world structure,
  not as beating random alone.)
- **F3 (sanity check, learner > oracle)**: if learner performance < B_oracle_freq performance
  on any world, the oracle baseline outperformed the learner on frequency matching alone —
  impossible by design. If triggered: IMPLEMENTER_ERROR, audit action sampling and policy
  definition before interpreting results.
- **F4 (secondary, baseline ranking)**: if B_freq ≥ learner (difference < 5pp), the learner did
  not achieve an advantage over learning from disjoint-data. If triggered:
  NO_WORLD_CONDITIONED_REASONING (learner absorbed frequency, not strategy). Report this as an
  alternative finding, not as a failure of the primary hypothesis — it is a different, valuable
  null result.
- **F5 (tertiary, held-out calibration)**: if B_oracle_freq − random > 5pp (oracle frequency
  baseline beats random by > 5pp on P_test), the generator class contains inherent structure
  discoverable from action frequency, complicating interpretation of learner advantage. If
  triggered: CONFOUNDED_BY_FAMILY_STRUCTURE; report oracle baseline results as a methodological
  note but do not suppress primary findings.
- **F6 (interaction falsifier)**: if learner advantage appears only on easy worlds (< 30% goal
  difficulty) and vanishes on hard worlds (> 70% difficulty), the learner is not generalizing
  strategy — it is shallow-fitting the easy regime. If triggered: ADVANTAGE_NOT_ROBUST_TO_DIFFICULTY,
  report as null result on reasoning (positive on pattern-matching).

## Stopping rule

Fixed-N, fully preregistered in Phase 0, no early stopping. P_test world count and learner seed
count are frozen before any Phase 1 evaluation row is collected. If early results show learner >>
baseline, do not stop; collect all preregistered evidence. If early results show learner ≈ baseline,
do not add worlds or runs; collect all preregistered evidence and report null. No post-hoc
threshold adjustment, no within-generation rescue, no outcome-contingent redesign after evidence
collection begins.

## Expected failure modes

- **Shallow pattern-matching ceiling**: learner may absorb action-frequency distributions from
  P_train and apply them to P_test with zero world-specific reasoning. Signature: learner ≈ B_freq
  >> random. This is a valuable null result (F4 triggered), not an experimental failure.
- **Held-out baseline too strong**: if P_control is too similar to P_test (e.g., both sample from
  the same mode of the generator), B_freq may achieve 80%+ solve rate, leaving little room for
  learner advantage. Phase 0 step 2 must confirm that baseline room exists (random << B_freq <<
  100%) before Phase 1 begins.
- **Task-family hardness collapse**: if the generator produces a narrow range of difficulty (all
  worlds trivial or all intractable), F1 will trigger and Phase 1 cannot proceed. Mitigation: Phase
  0 explicitly measures difficulty spread before freezing the world sample.
- **Cost-estimation under-specification**: if learner cost-per-goal (Phase 0 step 3) is measured
  on engineering seeds but Phase 1 discovers the true cost is 3x higher, the total compute budget
  in Phase 1 may be insufficient. Mitigation: include 2x safety margin in Phase 0 cost estimate
  before freezing Phase 1 budget.
- **Reproducibility breakdown**: if the procedural world generator or random-number streams are
  not fully deterministic, seeded evaluation will fail to match between components. Mitigation:
  audit that G(seed) is deterministic before Phase 0 preflight; use isolated RNG streams for
  learner, baseline, and world generation.

## Compute estimate

Assume: learner uses a bounded search (e.g., Monte-Carlo tree search, genetic algorithm, or
neural-network policy gradient) with evaluation budget per world estimated at 10,000 evaluations
(Phase 0 measurement required to confirm). Baseline components have identical budgets. Procedural
world generator is fast (< 1ms per state evaluation, based on LUDUS arena design). Estimate:

- Phase 0 (preflight): 5 worlds × 5 seeds × 1000 eval/world = 25K evals, typically < 1 hour.
- Phase 1 (evidence): 20 P_test worlds × 50 learner seeds × (learner + 3 baselines) × 10K eval
  = 40M evaluations, roughly 8–15 CPU-hours on a single machine (parallelizable by world or seed).

Total compute: low to moderate, single-machine feasible. Does not require distributed infrastructure
if the world generator is fast and learner is not a massive neural network.

## Prior evidence that materially changed this design (or 'none found')

- **D-5/D-8 contradiction (Evidence Wiki R-e68c9331eca2)**: history advantage findings contradicted
  between D-5 (+10.95pp, program-ecology substrate, M1 vs M0b baseline) and D-8 (NO_EFFECT, 
  foundry-ecology substrate, metered baseline). The differing dimension was baseline selection and
  substrate ecology. This directly motivated V2-T03's **stratified, disjoint-data baseline design**
  — breaking baseline selection relation explicitly, rather than relying on a single fixed control.
- **LUDUS Charter §5-7 (outcomes ≠ decisions, counterfactual replay)**: standard LUDUS instrument
  is decision-quality measurement via counterfactual simulation under multiple stochastic
  realizations, not binary win/loss. This motivated V2-T03's inclusion of decision-sequence
  recording and stratified goal-difficulty evaluation, enabling future counterfactual analysis
  beyond this specification.
- **Aporia cost-sensitive controls (roles/Aporia/resume_aporia.md)**: baselines include random,
  frequency-matched, and no-reuse variants, separated at execution time (not post-hoc). This
  directly shaped V2-T03's three-component baseline design (B_random, B_freq, B_oracle_freq) and
  the explicit separation of cost-per-goal measurement for each component in Phase 0.
- **Memory index feedback_control_must_break_the_selection_relation**: controls drawn from the
  treatment's selection relation ARE the treatment; exchangeability dominates matching. This ruled
  out V2-T03 initially considering a "learner with poor initialization" as a baseline (still in the
  learner's selection relation); pivoting to disjoint-data baselines (P_control, P_freq) instead.

## Unresolved uncertainty

- The **exact form of the learner's architecture** (neural network, tree search, symbolic program
  synthesis, etc.) is not specified in this proposal. V2-T03 must supply it in Phase 0 (learner
  definition is part of preflight before evidence collection begins).
- The **generative procedure** `G` (world generator) is assumed to exist and be deterministic,
  reproducible, and parameterizable; V2-T03 must confirm this before Phase 0 begins. If `G` itself
  is stochastic or irreproducible, the control design breaks.
- **Decision-quality measurement beyond solve rate**: LUDUS charter motivates counterfactual replay
  analysis (expected value, variance, robustness estimates per decision), but this proposal measures
  only solve rate (binary) and cost per goal. Phase 1 can extend to richer decision metrics if
  desired, but must be preregistered in Phase 0.
- Whether **goal-conditioned vs. reward-maximizing framing** matters: this proposal assumes the
  learner has a well-defined goal state; if goals are reward-shaped or sparse-reward, goal-reaching
  and reward-maximizing diverge (a known Aporia confound), and the primary statistic must be adjusted
  accordingly. Must be resolved in learner specification (Phase 0).

## Evidence Wiki consultation log (queries + object ids retrieved)

1. Query: "learner goal state procedural world" (OP 1) → returned results with None IDs (API
   result structure ambiguity, no usable claims retrieved).
2. Query: "baseline random chance learner" (OP 1) → found 3 results with titles but None IDs
   (including "Independent re-evaluation resurrected 0 of 92 historical kills").
3. Query: "procedural world goal state" (OP 1) → found 3 results (including "Push-your-luck is a
   real family and nearly empty").
4. Query: "naive baseline fails learner" (OP 3) with status='contradicted' → returned empty
   results.
5. Call: `ew.contradictions()` (OP 4) → returned 2 contradictions: **R-e68c9331eca2** (D-5 vs D-8
   history advantage, substrates differ), and R-2dc413ddca43 (FAILS_TO_REPLICATE, direct).
   **ID retrieved: R-e68c9331eca2**, used in design of disjoint-data baseline strategy.
6. Query: "learner population control null hypothesis random" (OP 5) → found 2 results (including
   "Independent re-evaluation resurrected 0 of 92 historical kills").
7. Query: "learner sample efficiency cost cost-per-goal" (OP 7) → found 2 results (including "In
   v3's recursion world...").

## Evidence that changed this design (ids -> concrete decision; 'retrieved but did not affect design' is valid)

- **R-e68c9331eca2** (D-5 vs D-8 contradiction on history advantage):
  **Concrete decision affected**: Baseline selection strategy. Initial draft considered a single
  fixed "uninformed" baseline (e.g., learner initialized without P_train experience, or learner
  with frozen random policy). Evidence contradictions motivated **pivot to stratified disjoint-data
  baselines** (B_random, B_freq, B_oracle_freq), explicitly breaking the learner's selection
  relation. This is a critical design choice: without the contradiction, V2-T03 would have accepted
  a simpler, less robust baseline comparison.

- **LUDUS Charter §5-7** (read directly, decision quality ≠ outcomes):
  **Concrete decision affected**: Evaluation metric scope. Initial draft considered binary win/loss
  outcome metrics only. Evidence on decision quality motivated **addition of stratified
  goal-difficulty evaluation and commitment to recording decision sequences** (not merely solve
  rates), enabling future counterfactual replay analysis. Also motivated preregistering **F6
  falsifier** (advantage must be robust across difficulty levels, not shallow-fitting easy cases).

- **Aporia cost-separated controls** (read directly):
  **Concrete decision affected**: Baseline component structure. Evidence on cost-sensitive measures
  (C_search vs C_execution) and multi-control designs (random, frequency-matched, no-reuse)
  motivated V2-T03's **three-component baseline** (B_random, B_freq, B_oracle_freq) with explicit
  separate cost accounting. Also motivated **Phase 0 step 3** (measure cost per goal for each
  component) before Phase 1.

## Operation log (numbered; ops used / 15, documents opened / 12)

1. Wiki query "learner goal state procedural world" (OP 1) — result structure ambiguous, no IDs
   retrieved but confirmed API working.
2. Wiki query "baseline random chance learner" (OP 1) — 3 results, titles retrieved but IDs None.
3. Wiki query "procedural world goal state" (OP 1) — 3 results retrieved.
4. Wiki query "naive baseline fails learner" (OP 3) — no results with status='contradicted'.
5. Wiki API call `ew.contradictions()` (OP 4) — **2 contradictions returned**, retrieved
   **R-e68c9331eca2** (D-5 vs D-8 history advantage, used in baseline design).
6. Wiki query "learner population control null hypothesis random" (OP 5) — 2 results.
7. Wiki query "learner sample efficiency cost cost-per-goal" (OP 7) — 2 results.
8. Read `F:\Prometheus\roles\Ludus\CHARTER.md` (lines 1-298) — **doc 1**, sourced LUDUS evaluation
   doctrine (decision quality, counterfactual replay, expertise gradients).
9. Read `F:\Prometheus\roles\Aporia\resume_aporia.md` (lines 1-150) — **doc 2**, sourced
   cost-sensitive baseline designs and control patterns (random, frequency-matched, no-reuse).
10. Read `F:\Prometheus\roles\Ludus\REVIEW_PACKET_3_2026-09-01.md` (lines 1-100) — **doc 3**,
    world classification and vector fields (confirmed stratification strategy available).
11. Read `F:\Prometheus\evidence_wiki\v2\arm_outputs\PILOT-1_A_sonnet.md` (full, lines 1-283) —
    **doc 4**, template and methodology for multi-phase preregistration with engineering/evidence
    separation, falsifiers, and control design.

**Operations used: 7 / 15. Documents opened: 4 / 12.** Stopped after reaching sufficient grounding
in baseline design (D-5 contradiction resolved the core question), evaluation methodology (LUDUS
doctrine), and control patterns (Aporia precedents). Remaining budget preserved; additional
operations would be useful for confirming learner architecture, world generator spec, and cost
estimates, but the design framework is complete and coherent.
