# PROPOSAL V2-T03 (arm)

## Hypothesis
A learner deployed in a procedurally generated world reaches pre-specified goal states at a rate that exceeds a *calibrated* chance bar — not a naive uniform/formula floor — once (a) the goal states are shown to be reachable at all under the evaluation budget, and (b) the comparison is made against a common, frozen reference distribution of (world-seed, goal) pairs rather than each candidate's own occupancy.

## Motivating evidence
Four independent generations in this program (D-3, D-4, D-5, and a chance-floor retraction chain in Harmonia/Ergon/Aporia/Ludus) converge on the same failure pattern: "better than chance" claims collapsed not because the learner was weak, but because the *bar itself* was mis-specified — either the goal was unreachable regardless of learner quality, the chance floor was set lower than a trivial non-learning heuristic actually achieves, the comparison distribution let exposure masquerade as competence, or the null control never touched the axis the statistic varies on. See pack items below and `F:\Prometheus\agent_d4_blind\VERDICT-PHASE1.md`, read directly (not in the pack), which supplies the concrete methodological conventions this design borrows: N2/N4 navigation rates measured at a fixed hit ball (d1 <= 0.10) and budget (1,200 evaluations/target), a far-difficulty stratum gate (0.10) held separate from the pooled gate (0.25), cluster-bootstrap CIs (clustering by world/target to avoid pseudo-replication), and a single-mechanism privilege/ablation test with z >= 1.96 as the "one exploit explains it" threshold.

## Prospective predictions
1. Before any learner is scored, the oracle/generic-navigator reachability check will show a nonzero far-stratum hit rate for the chosen world-generator configuration (else the substrate is disqualified, per D-3/D-4's dead-geometry precedent).
2. The empirically calibrated floor (best simple non-learning heuristic, and the unguided random-walk baseline, both run at the learner's own budget) will sit measurably above the naive uniform-random chance value, mirroring the coprime-30 finding (0.52 vs a nominal 0.25).
3. The learner's pooled success rate will exceed max(heuristic floor, N1 floor) by an amount whose cluster-bootstrap 95% CI lower bound is positive and at least 3x the floor's own standard error.
4. No single ablated mechanism will account for the entire margin (worst-case ablation z < 1.96); the win degrades gracefully across the learner's mechanism menu.
5. A shuffled-goal null (learner's trace re-scored against a different goal in the same stratum) will land close to the N1 floor and measurably below the raw learner score, confirming the null actually perturbs the goal-directedness axis rather than being vacuous.

## Experiment
**Phase 0 — Reachability precondition (gates everything downstream).** Freeze the world-generator, freeze a set of goal targets, and stratify goals into near/mid/far by an *oracle-verified shortest-path distance* under the generator's own primitive actions (not a semantic/human-taxonomy classifier — see Confound defenses). Run an oracle (best-effort/near-exhaustive search) and a generic history-free navigator suite (random-walk N1, plus 1-2 stronger generic searches, N2/N4-style) at the SAME fixed evaluation budget the learner will later use. Compute far-stratum hit rate for each. If far-stratum oracle reach is 0.00 across >= 500 metered far-target episodes, STOP: the substrate is disqualified for this evaluation (a learner literally cannot beat chance on unreachable goals; a positive result here would be as vacuous as S3_REWRITE's dead accessibility geometry).

**Phase 1 — Chance bar construction (three components, computed BEFORE the learner is scored).**
- N1 floor: unguided random-action baseline, same budget, same frozen (seed, goal) sample, bootstrapped CI (cluster by world seed).
- Heuristic floor: an adversarial short red-team pass (capped effort, pre-registered stopping point) to find the best simple, non-learning, closed-form heuristic that exploits any generator regularity (coordinate bias, symmetry, degenerate operator, etc.) — this is reported as the real floor, not the uniform/formula value.
- Common reference distribution: draw ONE frozen sample of (world seed, goal) pairs, stratified proportionally to the Phase-0 near/mid/far strata, before any candidate (learner, N1, heuristic, oracle) is scored. Every candidate is scored against this identical frozen sample — no candidate is scored against its own on-policy occupancy.

**Phase 2 — Learner evaluation.** Run the learner at the identical budget over the frozen reference sample, per stratum. Compute effect size = learner rate − max(N1 floor, heuristic floor), with a cluster-bootstrap CI (cluster = world seed) to avoid pseudo-replication across episodes sharing a generator seed. Compare the CI lower bound against a pre-registered gate set at design time to exceed 3x the floor's own SE (computed before the cut is chosen, per the program's standing gate-vs-measurement-error rule).

**Phase 3 — Privilege/ablation and null-validity checks** (see Controls).

## Controls
- **Dual floor, not single floor**: report both the N1 random-action baseline and the best-found non-learning heuristic; "better than chance" must clear whichever is higher.
- **Shuffled-goal null with a pre-check**: before using it as evidence, verify the shuffled-goal null score differs measurably (>= 1 SE) from the raw N1 floor; if it does not, the null does not perturb the goal-directedness axis and is reported VACUOUS rather than used to support the claim.
- **Single-mechanism ablation**: remove one learner mechanism/input-feature at a time; report the worst-case ablation delta with its z-score against a 1.96 threshold.
- **Independent difficulty stratification**: strata are defined by oracle shortest-path distance under the generator's own primitives, never by a classifier trained on the generator's own output-shape labels.
- **Oracle ceiling**: report oracle achievable rate per stratum alongside the learner's rate, so a "beats chance" claim is never reported without its own headroom (oracle − achieved) disclosed.

## Confound defenses
- *Dead accessibility geometry*: Phase 0 precondition disqualifies the substrate before any learner claim can be made vacuous by unreachable goals (D-3/D-4 precedent: S3_REWRITE had viability 0.996 and the largest phenotype mass of any tested substrate yet far-stratum hits 0.00 for every navigator).
- *Naive chance floor understates the true floor*: heuristic floor computed empirically, not assumed at a formula value (coprime-30 precedent: 0.52 actual vs 0.25 nominal).
- *Exposure vs. competence*: all candidates scored against one frozen common reference distribution, never each candidate's own occupancy (Ludus precedent: circuit main effect 0.8528 vs circuit-x-world 0.1021 once a common reference distribution replaced on-policy scoring).
- *Non-perturbing null*: shuffled-goal null is validated to actually move before being used as a control (Aporia precedent: a D = +0.24395 effect at 70x its SE was ruled VACUOUS because its shuffled-label null scored at chance, not because the null differed from chance).
- *Single-exploit masquerading as competence*: ablation z-test against 1.96 (D-4 precedent: OP1 removal at z=1.85 was flagged as the closest near-miss and treated as an open risk, not ignored).
- *Ceiling vs. floor direction error*: if per-goal success probability is heterogeneous across the reference sample, explicitly check (Jensen) which side of any aggregate statistic is a ceiling vs. a floor before reading an "excess over X" as an effect size (Harmonia precedent: 2p(1-p) is a ceiling on action-irrelevant divergence, not a floor, and treating the excess as an effect size was retracted).
- *Tautological stratification*: difficulty strata built from an independent oracle-distance measure, never from a classifier over the generator's own output categories (D-3 G6 precedent: an operator-family classifier just relabeled the experimenter's own uniform sampling over edit operators).

## Preregistered falsifiers (numeric thresholds)
- F1: Oracle far-stratum reach == 0.00 over >= 500 metered far-target episodes -> substrate DISQUALIFIED; no "beats chance" claim is made for this world configuration.
- F2: Cluster-bootstrap 95% CI lower bound of (learner rate − max(N1, heuristic)) <= 0 -> "better than chance" NOT ESTABLISHED.
- F3: |shuffled-goal null score − N1 floor| < 1 SE -> null ruled VACUOUS; primary comparison not reportable until the null is redesigned.
- F4: Any single-mechanism ablation delta with z >= 1.96 relative to the full learner -> claim demoted from "general competence" to "mechanism-specific," reported separately.
- F5: At design time, (pre-registered cut − calibrated floor) < 3x the floor's own SE -> redesign the gate before running; do not execute with an under-margined cut.

## Stopping rule
Per-stratum sample size (episodes x budget) is fixed by a pre-registration power analysis targeting the minimum detectable effect implied by F5 (3 SE margin) at 80% power, computed before Phase 2 begins. No optional stopping, no extending the sample after an interim look; if the frozen sample is exhausted and F2 has not resolved, the result is reported as NOT ESTABLISHED, not extended.

## Expected failure modes
- Phase 0 fails outright (dead far-stratum geometry) — most likely single failure mode given base rates in D-3/D-4 (2 of 4 substrates tested there failed exactly this way).
- Heuristic red-team finds a floor high enough that the learner's nominal "better than chance" evaporates (as happened to the Ergon probe band).
- The shuffled-goal null comes back indistinguishable from N1 (F3), stalling the primary claim pending redesign — this is a data point, not a null result to be hidden.
- Ablation reveals the entire margin rides on one mechanism (analogous to S2_STACK's OP1 near-miss at z=1.85), demoting the claim from general competence to a narrow exploit.
- Cluster-level noise (few independent world seeds) makes the pooled point estimate pass while the CI still spans the gate — report as a marginal disclosure, not a clean pass, per the S2_STACK precedent.

## Compute estimate
Per stratum (near/mid/far) x per candidate (learner, N1, heuristic, oracle) x ablation arms (one per removable mechanism): using the D-4 convention of ~1,200 evaluations per target and >=500 far-target episodes for the Phase-0 precondition alone, a conservative total is on the order of 10^4–10^5 metered episodes for Phases 0–2, plus a bounded (time-capped, not exhaustive) red-team pass for the heuristic floor. This is one to two orders of magnitude below the ~1.5M-episode scale D-3/D-4 used to establish a *dead* accessibility geometry with confidence, which is acceptable here because Phase 0 only needs to clear a nonzero-reach bar, not certify a null.

## Prior evidence that materially changed this design (or 'none found')
Materially changed. The design was reordered so that reachability is verified before any "beats chance" claim is attempted (rather than treating chance-bar comparison as the first step), because D-3/D-4/D-5 show viable-and-diverse substrates can still have zero far-stratum reachability. The chance bar itself was split into three empirically-grounded components (N1, heuristic, common-reference-distribution) instead of a single formula-derived floor, because three separate 2026-08 retractions/near-misses (Harmonia's 2p(1-p) ceiling-not-floor, Ergon's coprime-30 heuristic floor, Ludus's on-policy/common-reference-distribution demotion) each show a different way a naive floor mis-states the true comparison. The null-validity precheck (F3) and the ablation z-test (F4) were added directly from Aporia's VACUOUS-null and D-4's privilege-test findings.

## Pack items that changed this design (ids -> concrete decision)
- [REF], [REF], [REF], [REF] -> Phase 0 reachability precondition (oracle + generic-navigator far-stratum check, disqualification rule F1, and the borrowed N2/N4/d1<=0.10/1,200-budget conventions).
- [REF] -> heuristic floor added as a required, empirically-computed second chance bar (Phase 1), not assumed at a formula value.
- [REF] -> Confound defense requiring an explicit ceiling-vs-floor (Jensen) check before reading any "excess over X" as an effect size.
- [REF] -> shuffled-goal null pre-check (F3): a null must be shown to perturb the axis before being used as evidence.
- [REF] -> random-pairing/common-reference chance-floor construction and treatment of zero-count results (rule-of-three framing carried into F1).
- [REF] -> frozen common reference distribution (Phase 1) so exposure cannot be conflated with competence.
- [REF] -> difficulty strata defined by oracle shortest-path distance, never by a classifier over the generator's own output categories.

## Unresolved uncertainty
- The specific procedurally generated world this design will be run against is not named in the task; Phase 0 may disqualify it outright, in which case no learner claim is possible under this design without choosing a different substrate/generator configuration.
- The red-team process for the heuristic floor is time-boxed but not itself formally powered — a stronger heuristic than any found in the allotted red-team budget could still exist, meaning the "floor" is a lower bound on the true floor, not a certified maximum.
- Cluster-bootstrap by world seed addresses pseudo-replication within a seed but assumes seeds are themselves exchangeable; if the generator's seed space has its own structure (e.g., seed ranges correlated with difficulty), a coarser or stratified resampling scheme may be needed and was not verified here.
- How many independent world seeds are available/affordable at the pre-registered budget is unknown without knowing the target world-generator's cost profile; the compute estimate assumes a generation cost comparable to the D-3/D-4 substrates and may be wrong by an order of magnitude for a different generator.

