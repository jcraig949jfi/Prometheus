# PROPOSAL V2-T03 (arm)

## Hypothesis

A learner operating in a procedurally generated task environment, initialized with a fixed random seed and access to deterministic state/action/observation, reaches goal states (defined as verified exact task solution) at a rate significantly exceeding the strongest blind baseline under equal computation, without human-authored tactical heuristics or task-domain knowledge.

## Motivating evidence

- **D-8 REPORT**: learner with evolved heuristics (M1) showed +0.10pp over strongest baseline (M0b) but within CI [−0.033, +0.233]; controlled ablations (H-BAG, H-SHUFFLE, H-RANDOM) available for contamination diagnosis.
- **Ludus ROLE §5 GATE-W1**: a procedurally generated world is admissible only if depth-profile gap(4) >= 0.20, ensuring a world cannot be trivially solved by 4-ply search; prevents ceiling effects and ensures measurable daylight between trivial and competent agents.
- **D-10 DESIGN_BRIEF §6 p5b**: cold-start solve rate 0.000 at B=600; same-family reference programs 0.568; large clean headroom with bounded outputs (L=12) and deliberate screening to reject trivially solvable tasks (rejects ~85%).
- **PILOT-1 Controls §98–§109**: paired within-task design, structureless-control floor, family-matched strata, admission-filter disclosure; prevents confounding elapsed time with task family adjacency or selection bias.

## Prospective predictions

1. **Primary (goal-achievement):** Learner mean solve rate on procedurally held-out test tasks, aggregated over N >= 30 tasks from the evaluation battery, exceeds the strongest blind baseline (random search) by a minimum margin of +0.15 (e.g., learner 0.45 vs random 0.30), measured under identical per-task computation budget. Predicted primary statistic: McNemar exact test, two-sided, alpha=0.05.

2. **Null-consistent-with-random-floor (live alternative):** Learner solve rate ≈ random floor +/− 0.05 (not significantly different), indicating the learner has discovered no generalizable strategy and the environment has no learnable structure above chance, consistent with D-8's own null on organization.

3. **Blind-baseline-superiority (falsifiable):** A greedy heuristic (score-gradient following) or structured baseline (e.g., depth-2 tree search seeded from random init) achieves >= 0.60 solve rate, exceeding the learner at equal compute. This would indicate the learner cannot compete even with modest transparency and predefined utility signals.

## Experiment

**Phase 0 (preflight, engineering seeds 1000–1099 only):**

1. Construct N=50 procedurally generated task instances: each task is a reference program (randomly initialized in the substrate, length L=12, halting within 200 steps) paired with n_train=8 example (input, output) pairs and n_test=16 disjoint held-out pairs. Inputs uniform over [0, 255]^2; outputs in [0, 255].

2. Screen all 50 tasks: reject any task where a frozen pool of 500 random baseline programs reproduces train+test exactly (triviality gate). Expected survivor rate ~40% (replicating D-10 §6 p4 findings), yielding ~20 eligible tasks for sizing.

3. Measure per-task baseline solve rates (random search, n=100 candidate evals/task, matched seeds) across the 20 eligible tasks. Compute pooled SE on the random floor to set target power for Phase 1.

4. Run a single-task pilot of the learner under test budget B (e.g., B=2000 evaluations). Record: (a) solve achieved (yes/no); (b) step-to-solve if solved; (c) wall-clock time; (d) any resource violations.

5. Preregister the exact task battery (hashes of all reference programs), learner initialization seed, baseline algorithm variants (M0_random, M0_greedy, M0_search_k=2), and per-task budget B.

**Phase 1 (evidence, seed streams 4000–4999, never engineering streams):**

For each task t in the frozen battery:
- Run learner: initialize from seed s, receive task state/actions/observation, run for B evaluations (capped), record solved/solved_step.
- Run M0_random: uninformed random search, B evaluations, same seed, record solved/solved_step.
- Run M0_greedy: greedy score-chasing (one-ply local max over available actions), same seed, record solved.
- Paired comparison: Δ_t = (learner_solved_t − random_solved_t), McNemar discordant count.

Aggregate over all N tasks. Compute McNemar exact test statistic and two-sided p-value.

## Controls

- **Random-floor matched-seed:** every learner run has a same-seed random-search counterpart on the identical task, so Δ is a within-task paired delta, not a population average.
- **Greedy-heuristic control:** same budget, same substrate, learner compared against a hard-coded gradient-following agent; if learner is inferior, the primary hypothesis is falsified.
- **Computation-matched null (H-RANDOM):** learner is given access to the same evaluated-candidate hoard size and structure as random search (i.e., no privileged proposal distribution). This prevents "learner wins by caching more" confounds.
- **Task-family stratification:** tasks are tagged by reference-program length, output range, and mutational distance from a frozen seed set; solve-rate is reported stratified by these, so family-specific ceiling effects can be detected.
- **Triviality screen:** all tasks pass the triviality gate (§Phase 0 step 2) before evidence reading, preventing "learner solves trivial tasks" artifacts.

## Confound defenses

- **Ceiling-floor truncation confound:** learner and baseline could both hit ceiling or floor on the same task set, making Δ silent. Defense: Phase 0 step 3 measures the empirical SE on the random floor and Phase 1 stratifies by task difficulty (measured by random-solver variance), so silent regions are disclosed.
- **Measurement-error gate confound:** if SE on Δ is large relative to the hypothesized effect (+0.15), the gate is not sufficiently powered. Defense: F2 (below) requires +0.15 to exceed 2× bootstrap SE; gate must be shown reachable before reading.
- **Selection-into-learner-design bias:** learner parameters (e.g., mutation rate, population size, selection criterion) could be tuned post-hoc to fit the task battery. Defense: all learner hyperparameters are frozen in Phase 0 before Phase 1 evidence is read; no within-generation rescue.
- **Task-generation oracle leakage:** learner could exploit information about the reference program (e.g., its seed or length) if that metadata reaches the learner. Defense: learner receives only uid + example pairs; no reference-program metadata is observable.
- **Admission-filter selection bias:** if the learner's early attempts happen to cluster on easy tasks, later improve on hard tasks, and those hard tasks are only tested late (confounding learner-age with task-difficulty), the age effect could masquerade as learning. Defense: Δ is reported per-task (not aggregated in time order); per-task results are shuffled in presentation so temporal adjacency is not visible.

## Preregistered falsifiers (numeric thresholds)

- **F1 (primary: goal-achievement):** McNemar exact test on pooled discordant pairs across all N tasks, two-sided alpha=0.05. Learner solve rate − random floor >= +0.15 (in percentage points). If not met: GOAL_ACHIEVEMENT_NOT_ESTABLISHED.
- **F2 (instrument sufficiency):** mean Δ at the easiest task quartile (by random-baseline variance) must exceed 2× bootstrap SE; if not, INSTRUMENT_UNDERPOWERED (mirrors D-8 G5 pattern).
- **F3 (reachability, checked in Phase 0):** if > 50% of tasks remain below random floor 0.10 after triviality screening, the battery is TRIVIAL_BATCH and must be regenerated before Phase 1 — never adjusted after evidence is read.
- **F4 (opposite direction, always reported if triggered):** learner solve rate significantly BELOW random (p < 0.05, direction opposite F1) falsifies the goal-achievement hypothesis in favor of a learning-interference claim and must be reported as such.
- **F5 (greedy-superiority check):** if M0_greedy achieves >= 0.60 solve rate and is significantly superior to the learner (p < 0.05, McNemar), the learner hypothesis is rejected regardless of F1's outcome.

## Stopping rule

Fixed-N, not sequential. The task battery (N), learner budget (B), and baseline variants are all frozen in Phase 0 before Phase 1 evidence is read. No early stopping on favorable interim McNemar; no added tasks, learner modifications, or budget changes after the freeze. Seed streams 4000–4999 are carved off pre-publication and hashed; any result read from those streams is final.

## Expected failure modes

- **Triviality collapse:** despite screening, procedurally generated tasks may still be mostly solvable by random guessing (e.g., output range [0, 255] is small, solutions cluster on common values like 0 or 255). Then random floor is already high (~0.50) and daylight to learner is closed. Must be detected in Phase 0.
- **Budget-exhaustion truncation:** if the learner hits its budget cap on most tasks without solving, mean solve rate is zero and Δ ≈ −baseline. This is a truthful negative finding (learner too slow) but morphologically identical to "learner is broken." Must be disclosed explicitly.
- **Seed-dependent failure:** the learner's performance could be highly sensitive to initialization seed; some seeds permit learning, others do not. Then averaging over a fixed seed stream hides high variance. Defense: compute per-seed variance and report CIs, not just point Δ.
- **Greedy-heuristic-dominance masking:** if the greedy heuristic is nearly optimal (solve >> learner) for all task families, F1 could pass but F5 fires, revealing that the task battery is simply too easy for learner advantage to appear. This is a truthful finding (battery mismatch) and must be disclosed.

## Compute estimate

- Phase 0: 50 tasks × (500 random-baseline evals + 1 learner pilot at B=2000 + 1 greedy run) ≈ 1.25M evals, ~1–2 hours on CPU.
- Phase 1: N≈20 eligible tasks × (B=2000 evals/task × 3 arms × ~10 seed replicates per task to reach target SE) ≈ 1.2M evals, ~2–3 hours on CPU.
- Total: ~3–5 hours, single-machine, no GPU required.

## Prior evidence that materially changed this design (or 'none found')

- **D-8 NO_EFFECT verdict**: the null on history-constructed reusable objects (S0) changed the target from "learner discovers reusable sub-programs" (overambitious) to "learner reaches goal states" (more tractable, grounded operationalization).
- **Ludus GATE-W1 (depth gap >=0.20)**: worlds that fail this gate are degenerate (4-ply search solves them). This motivated the adoption of D-10's task-screening and depth-profile measurement as a preflight, preventing silent ceiling effects.
- **D-10 preflight findings (p5b)**: cold 0.000, same-family 0.568 shows that procedurally generated tasks have huge headroom between random and best-case. This licensed the +0.15 threshold as plausible and measurable.
- **D-8 M0_baseline suite (M0a/b/c)**: having multiple blind baselines (random, hill-climber, GA) let D-8 diagnose whether learner advantage came from search-form or content. Adopted here as M0_random, M0_greedy, (M0_search deferred).

## Unresolved uncertainty

- Whether the learner's proposal distribution (e.g., mutation rates, recombination operators) can be held constant across task families or must be task-adaptive. Currently assumed constant; deviation would affect interpretation of Δ if learner re-tunes and blind baselines do not.
- Whether the reference-program screening (rejecting trivial tasks) is sufficient to prevent D-10's "all cold tasks at floor" failure mode, or whether a secondary depth-profile measure (analogous to Ludus r0002) is needed. Deferred pending Phase 0.
- Whether the greedy heuristic's one-ply lookahead is the right difficulty level for M0_greedy. If one-ply is too easy (greedy solves everything) or too hard (greedy solves nothing), F5 fires but provides no causal insight. Alternative: depth-2 search or a learned-weight heuristic (but this moves back toward "learner competing against near-learner" rather than a truly blind baseline).

