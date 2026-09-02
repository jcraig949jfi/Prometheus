# PROPOSAL V2-T03 (arm)

## Hypothesis
A new learner operating in a procedurally generated world reaches goal states at a rate that exceeds not naive uniform-random chance, but a pre-registered **attainable-without-reasoning ceiling** — the best rate a cheap, non-learning policy (one-ply greedy heuristic and shallow fixed-depth search) achieves on the same held-out generated instances — by a margin that itself exceeds the ceiling's own measurement error.

Naive "beats random chance" is not adopted as the operative claim: prior evidence (below) shows procedurally generated worlds can be almost fully solved by trivial search, and shows naive chance floors can be statistically indistinguishable from population-level null performance. Either failure mode would let a non-competent learner clear an uninformative bar.

## Motivating evidence
- Procedurally generated (or authored) worlds can instantiate an apparently strategic domain while containing essentially no strategic decision: a one-ply greedy heuristic picks the optimal action in 85-100% of states and four plies of trivial search solves the world (Ludus, [REF]). If this world class were used as-is, a learner matching greedy performance would look "successful" while having learned nothing.
- A naive chance/null floor is not automatically informative or well-separated from real performance: an independent re-evaluation found a non-promoted survivor population re-evaluating TRUE at 45.9% against a 46.1% random-pairing chance floor — indistinguishable from chance despite looking like a real result on its face (Harmonia, [REF]). This is the direct cautionary precedent for what happens if "better than chance" is asserted without characterizing the floor's own uncertainty.
- Baseline/comparator choice is known to be substrate-sensitive and must be frozen before seeing learner data, not selected post hoc to flatter either arm (contradiction [REF]: Daedalus vs Aporia disagree on outcome for the same abstract claim across two substrates, traced to differing frozen comparator rules, not to differing learner competence).
- The "attainable-without-reasoning ceiling" pattern recurs across substrates (graph edge SAME_MECHANISM linking [REF] to [REF], a coprime-heuristic-vs-one-ply-greedy world ceiling held out during V0 benchmarks) — evidence this is a general confound class for PCG-world evaluations, not a one-off.
- Memory-resident hard rules directly bear on comparator construction: an on-policy/competence score is exposure x competence and needs a common reference distribution, never self-occupancy (feedback_onpolicy_score_conflates_exposure_and_competence); a gate must exceed measurement error, computed before the threshold is chosen (feedback_gate_must_exceed_measurement_error); a gate must be shown reachable before it is read as a null (feedback_gate_must_be_shown_reachable); a control must break the actual selection relation, not merely resemble a control (feedback_control_must_break_the_selection_relation).

## Prospective predictions
1. A pilot triviality audit (one-ply greedy + 4-ply search) run on N_pilot held-out generated instances will show a nonzero probability of failing the admissibility gate (i.e., we predict some risk the first-draft generator is too easy, consistent with the Ludus precedent).
2. The random-pairing chance floor for this world class will sit measurably below the shallow-search ceiling (they are different quantities); reporting only one of them would misstate the bar.
3. If the learner has any real competence at this task, its held-out goal-reach rate will exceed the shallow-search ceiling by a margin larger than 3x the ceiling's standard error, not merely exceed 50% or exceed uniform-random.

## Experiment
Design (no execution in this document):
1. **World generator.** A parameterized procedurally-generated world: a directed state graph per episode, generated from a seed, with a fixed action vocabulary, a designated start state, and one or more goal states placed by the generator. Parameters (branching factor, depth-to-goal, distractor-goal density, dead-end density) are drawn from a pre-registered distribution so difficulty varies across instances rather than clustering at one difficulty.
2. **World-triviality audit (precondition gate, runs BEFORE the learner is scored).** On N_audit ≥ 500 held-out seeds, compute: (a) one-ply greedy optimal-action rate, (b) k-ply (k=4) lookahead goal-reach rate. If either exceeds the pre-registered admissibility ceiling (Falsifier F1 below), the world class is INADMISSIBLE and the generator's difficulty parameters must be revised before any learner evaluation proceeds.
3. **Baseline stack**, all evaluated on the identical held-out instance set as the learner (common reference distribution):
   - B0 — uniform-random action policy (reported, not primary gate).
   - B1 — one-ply greedy heuristic (primary comparator input to the admissibility gate).
   - B2 — k-ply (k=4) fixed-depth search (primary comparator input to the admissibility gate; also serves as the "attainable-without-reasoning ceiling" proper).
   - B3 — random-pairing permutation null: break the selection relation by reassigning each episode's goal-state label across a random permutation of generated worlds (not shuffling actions within a world), then re-score B1/B2 and the learner under this broken relation. This yields an unbiased chance floor with its own empirical SE, per the Harmonia precedent.
4. **Learner evaluation.** Train/tune the learner using one held-out-disjoint seed pool; evaluate goal-reach rate on a second, never-seen-during-training seed pool (≥5 independent seed-pool replicates, per feedback_replicate_seeds), matched to the same instance-parameter distribution as the baselines.
5. **Compute-matched comparison.** Cap the learner's per-episode action budget (or environment-step budget) at the same value given to B2's k-ply search, so a margin over B2 cannot be attributed to the learner simply being allowed to look further ahead.
6. **Primary statistic.** Δ = learner_goal_reach_rate − B2_goal_reach_rate, on the common held-out set, with bootstrap or exact binomial CI; compare Δ against the pre-registered margin (Falsifier F2), and separately confirm B3's permutation-null floor is well-separated from B2 (Falsifier F3).

## Controls
- Held-out seed pools disjoint from any seed used in learner training or hyperparameter tuning.
- World-triviality audit run and passed (or generator revised) before any learner data is collected — sequencing enforced, not merely reported.
- Common reference distribution: B0/B1/B2/B3 and the learner all scored on the identical held-out instance set, same seeds, same episode count — avoids self-occupancy circularity.
- Compute/action-budget parity between learner and B2 (shallow search), so the margin reflects competence, not budget.
- Stratification of the held-out set across the generator's difficulty parameters (branching factor, depth, distractor density) rather than an alphabetical/first-N or single-difficulty slice.
- Random-pairing permutation null (B3) constructed by reassigning goal labels across worlds, which breaks the actual state→goal selection relation rather than merely permuting within-episode actions (a within-episode shuffle would not break the relation the outcome depends on).

## Confound defenses
- **World triviality** (Ludus [REF]): defended by the mandatory pre-registered admissibility gate (F1) run before learner scoring; if it fails, the evaluation is aborted and the generator is redesigned, not silently re-interpreted as a learner result.
- **Chance floor sitting at/near real performance** (Harmonia [REF]): defended by computing B3's SE empirically via permutation rather than asserting a nominal chance value (e.g. 50% or 1/branching-factor), and requiring the learner's margin over B2 to exceed 3x B2's own SE (feedback_gate_must_exceed_measurement_error), not just be numerically positive.
- **Exposure vs. competence conflation** (feedback_onpolicy_score_conflates_exposure_and_competence): defended by the common reference distribution across learner and all baselines; no self-occupancy scoring.
- **Selection-relation leakage into the "control"** (feedback_control_must_break_the_selection_relation): defended by constructing B3 as a cross-world goal-label permutation, which severs the actual causal path (start state → goal), not an easier-to-implement within-world action shuffle that would leave the relation intact.
- **Gate not shown reachable** (feedback_gate_must_be_shown_reachable): defended by computing the maximum attainable goal-reach rate under the generator's own reachability guarantees (episodes are only admitted if a goal is provably reachable from start) before fixing F2's margin, so the pre-registered threshold cannot sit above the ceiling the generator can produce.
- **Sampling-window bias** (feedback_prefix_sampling_invalidated_three_passes / feedback_sampling_strategy_is_analysis): defended by stratifying held-out seeds across all pre-registered difficulty parameters rather than iterating seeds in generation order.

## Preregistered falsifiers (numeric thresholds)
- **F1 (admissibility, precondition).** If, on N_audit ≥ 500 held-out seeds, the one-ply greedy heuristic achieves ≥85% optimal-action rate OR the 4-ply search achieves ≥90% goal-reach rate, the world class is INADMISSIBLE. Evaluation halts; generator parameters must be revised and the audit re-run. (Threshold set directly from the observed 85-100% range in [REF].)
- **F2 (primary gate).** Learner goal-reach rate on held-out seeds must exceed B2 (4-ply search) goal-reach rate by ≥10 percentage points, AND that margin must exceed 3x B2's bootstrap SE. If either condition fails, the hypothesis is FALSIFIED for this world class.
- **F3 (floor characterization).** B3's (permutation-null) goal-reach rate for B2 must differ from B2's real goal-reach rate by ≥2x B3's own SE. If B2's real performance is not distinguishable from its own permutation-null floor, the world/metric combination is declared uninformative and the evaluation is voided (mirrors the [REF] failure mode directly).
- **F4 (replication).** The F2 margin must hold at Holm-corrected p<0.01 across ≥5 independent held-out seed-pool replicates (feedback_replicate_seeds); a result significant in only 1-2 of 5 replicates is not sufficient.

## Stopping rule
Fixed-N, no optional stopping. N per replicate (episodes per seed pool) is set by a power analysis run on B2's pilot SE from the audit stage (N_audit), targeting 90% power to detect the F2 10-point margin at the F2 SE-multiple requirement. Once N and the 5 seed-pool replicates are fixed and hashed pre-registration is committed, no additional seeds/episodes are added regardless of interim results. The only permitted early stop is F1 failure (admissibility gate), which halts the whole evaluation for generator redesign, not for re-reading the data under a new threshold.

## Expected failure modes
- The first-draft generator fails F1 (plausible given the direct Ludus precedent on authored "strategic" worlds); expect at least one redesign cycle on difficulty parameters before a world class is admitted.
- The learner clears B0 (uniform-random) comfortably but fails to clear B2 (shallow search) — the informative and likely outcome if the learner has not internalized anything beyond what four plies of lookahead already captures.
- B3's SE is large if the state space per instance is small, making F3 hard to satisfy at reasonable N — may require increasing N_audit specifically for B3 rather than reusing N from B1/B2.
- Learner is compute-budget-sensitive in a way that only shows up once matched to B2's budget (e.g., it was implicitly relying on a larger action budget in development), producing an apparent regression at parity that is actually the confound being correctly removed.
- Generator difficulty parameters covary with an exploitable surface feature (e.g., goal is always reachable via the same structural shortcut), which the triviality audit alone may not catch if the audit's own held-out sample under-represents that regime — stratification mitigates but does not guarantee detection.

## Compute estimate
Audit stage: N_audit=500 seeds x {B1, B2, B3-on-B2} ≈ 1,500 lightweight graph-search evaluations, seconds to low minutes on a single machine (no learner involved). Main evaluation: 5 replicates x N (from power analysis, expect low thousands of episodes per replicate) x {learner, B0, B1, B2, B3} — dominated by the learner's own inference cost if it is model-based; if the learner is a lightweight tabular/planning agent, total wall-clock is expected to be under an hour on a single machine. If the learner is LLM-backed, add a token budget proportional to (episodes x action-budget x replicates) and treat that as the binding cost, to be sized once the learner's per-step token cost is known.

## Prior evidence that materially changed this design (or 'none found')
- [REF] materially changed the design: without it, this proposal would have used a naive random-chance baseline; instead it adds a mandatory pre-registered world-triviality admissibility gate (F1) and makes shallow fixed-depth search (B2), not uniform-random chance, the primary comparator.
- [REF] materially changed the design: it added the requirement to empirically characterize the chance floor's own SE via a random-pairing permutation null (B3) and to require the learner's margin over B2 to exceed 3x B2's SE (F2) rather than merely be positive — directly modeled on the observed 45.9%-vs-46.1% near-miss.
- Contradiction [REF] materially changed the design: it reinforced fixing the comparator rule (B1/B2 as primary, B0/B3 as reported-not-primary) before any learner data is seen, rather than choosing post hoc whichever baseline makes the learner look best.
- [REF] (related_findings graph edge, SAME_MECHANISM) did not change a concrete design decision beyond confirming the "attainable-without-reasoning ceiling" is a recognized recurring pattern across substrates, which supported naming and framing B2 this way with more confidence.

## Unresolved uncertainty
- Whether the specific procedurally generated world class proposed here will pass F1 at all is genuinely unknown until the audit is run; no implementation of this generator currently exists in the repository as far as this proposal's search reached.
- The random-pairing null precedent ([REF]) comes from a records/retrodiction substrate, not a graph/gridworld PCG substrate; whether cross-world goal-label reassignment is the correct way to break the selection relation for THIS world's structure (versus, e.g., reassigning start states, or edge sets) is an open design choice that the pilot audit should surface, not one this specification can resolve in advance.
- The sample size needed for B3's SE to be small enough to satisfy F3 is unknown until pilot (N_audit) data exists; if the world's state space is small, N_audit may need to be substantially larger than 500 for B3 specifically.

