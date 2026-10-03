# ASTRA-6.0 / Enceladus: RSE architecture v0

## 1. Decision and epistemic boundary
**Build a bounded staged observatory, initially comparing three substrate tracks through six complementary experimental questions. Do not choose an RSE winner in advance.** Requirements in `REQUIREMENTS.md` precede this proposal; both precede salvage.
This is a first-principles design derived from the shared operator mandate, not a characterization of existing engines. Generic failure concerns come from the operator charter, not an empirical audit. Historical motivation, scientific maturity, component quality, and a reuse percentage are deliberately UNKNOWN.
The central question is whether experience constructs reusable operations that reduce later acquisition cost, and whether it can improve the processes that construct such operations. Increasing scores, graph size, developmental age, or apparent complexity are not sufficient evidence.
Three tracks expose contrasting assumptions about addressing, locality, discreteness, and update rules while keeping qualification affordable. Six questions separate capacity, accessibility, reuse, revision, intervention validity, and nested development; these are experimental lanes, **not six mandatory software engines**.
The counts are a budgeted starting point, not a claim of exhaustive coverage. Add a track only for a missing physical assumption and a discriminating test; split a lane only if its controls require different machinery. Retire a track for demonstrated inadequacy or redundancy, not unfamiliarity.

| Organization | Advantage | Principal confound/cost | Discriminator and provisional decision |
|---|---|---|---|
| One integrated engine | Cheap shared tooling; easier within-substrate comparisons | Its ontology and bugs constrain every result | Retain as a comparator; prefer it only if independent tracks add no qualified distinctions at equal total budget |
| Many unrelated engines | Broad assumptions; lower correlated scientific-code risk | Duplicated apparatus; incomparable costs; thin replication | Do not begin with 6-12 full stacks; expand only for a demonstrated blind spot |
| Three-track staged observatory | Controlled diversity plus common auditability | Protocol itself can impose hidden common assumptions | Start here; independently check adapters, simulator/ruler code, and negative controls |

Scientific yield is a vector: qualified instruments, resolved alternatives, bounded exclusions, replicated mechanisms, and claim robustness, each paired with compute/energy/attention. It is not a scalar reward for positives, commits, or experiment counts.

## 2. Shared protocol, not shared scientific semantics
The common layer is a small run contract: artifact identities, budget receipts, observation/action envelopes, reset/checkpoint requests, native intervention descriptors, event ordering, and typed outcomes. It does not prescribe objects called beliefs, memories, hypotheses, plans, abstractions, or reasoning steps.
An envelope may carry opaque bytes or numerical arrays, but its codec, bandwidth, latency, coordinate system, precision, and energy/compute tariff are declared. A codec must not supply hidden state, semantic labels, free planning, or privileged indexing. Adapter costs belong to the organism/world boundary ledger.
- **Generation:** offline manifests and structural/stochastic search create candidates; search sees only authorized development/discovery outcomes. Any later LLM proposals are tagged seeded priors, not an invisible mutation service.
- **Reality:** sandboxed native simulators consume candidates and world streams; hidden world state is inaccessible to organisms. They emit append-only trajectories and resource records, with separate RNG streams for worlds, search, and interventions.
- **Measurement:** frozen, qualified rulers read immutable trajectories/checkpoints and produce estimates, control reports, and typed dispositions. They cannot rewrite reality or generate extra training examples from holdouts.
- **Interpretation:** humans/models read result bundles and propose subsequent registered contrasts. They cannot veto a valid anomaly because it lacks a familiar name, change a completed run, or retroactively redefine a passing control.
Share serialization and scheduling only after protocol conformance tests. Do not share organism VMs, decisive world dynamics, solver logic, or the sole implementation of a ruler across purportedly independent replications.
A second implementer receives the frozen behavioral/intervention contract, not the first implementation's internals or result-dependent fixes. Common runtimes/libraries remain disclosed dependencies; independent authorship alone is not proof against common error.
Native interventions are capability-negotiated: unsupported lesions/transplants return `INTERVENTION_UNSUPPORTED`, never silent approximations. Architecture-level comparison uses observable effects and costs; no universal internal cognitive state schema is required.
Protocol tests check replay, invalid events, timeout/censoring, hidden-state access, forbidden writes, and alternate codecs. These are future implementation tests; this Stage I executes none of them.

## 3. Three initial substrate tracks
All tracks provide costed persistent writable state, readdressable references, and transition rules. Readdressability means a native way to revisit retained material, not necessarily global random-access pointers. These affordances are a pragmatic envelope; ablations test their contribution rather than declaring them universal necessities.

| Track | Organism/developmental physics | Exposed prior and decisive alternative | Resource risk / initial search |
|---|---|---|---|
| A: addressed local-rewrite structures | Finite records and links; local match/rewrite, allocate/delete/copy, payload mutation, and charged traversal; mutable rule records executed by a fixed safety kernel | Explicit identity and nonlocal links favor symbolic-like solutions; compare fixed topology, no-copy, and locality-constrained variants | Pointer traversal, event logs, and search dominate CPU/memory; enumerate tiny rules, then mutation/recombination without semantic operators |
| B: spatial local-interaction medium | Bounded lattice sites with token multisets or finite cell states, local transport/reactions, persistent regions, and rule-bearing material; all long-range effects pay propagation time | Geometry, locality, and conservation choices bias organization; compare uniform immutable rules versus locally modifiable transition material | Many local events and long propagation dominate CPU/energy; stochastic structural search and small exact cases before larger grids |
| C: recurrent numerical dynamics | Finite-precision recurrent units, persistent activations, writable weights/couplings, and optional growth/pruning; local update coefficients can themselves change under native rules | Smooth dynamics, precision, differentiability, and topology are strong priors; compare fixed architecture/fixed update rule with structural and update-rule plasticity | Numerical simulation and checkpoints dominate CPU/memory; conventional gradient or black-box search is an explicit baseline, never pretrained cognition |

The minimal kernel enforces memory safety, clocks, conservation/tariffs, and budgets; it does not interpret a rule record as a belief or preassign its developmental role. Kernel replacement is not organism self-improvement.
Self-reference, compositional binding, modularity, simulation, abstraction, and selective revision are candidate emergent functions. Programmable rewrites may support them, but expressive power alone neither establishes discoverability nor proves they occur.
Distinguish genome/initial material, lifetime state, native rules, and scheduler state in provenance. These are causal ownership/reset boundaries, not a required decomposition of cognition. If an intervention cannot separate them without destruction, report its identifiability limit.
Use no privileged free archive or unmetered external optimizer memory. Count instruction alphabets, authored rule libraries, decoder information, and inherited state. Directly seeded competent organisms qualify capacity/rulers only and never count as endogenous discoveries.

## 4. Worlds, policies, and pressure
Start with small worlds whose true hidden transition graph can be enumerated by the evaluator, while the organism sees only budgeted observations. Exact analysis on these finite cases is an instrument aid, not a promise that larger worlds admit complete solution.
Three initial families suffice for orthogonal demands: **delayed hidden-state control**, **compositional causal/tool transitions**, and **ambiguous-source revision with regime shifts**. Use at least two independently authored generators for any promoted cross-family mechanism claim.
For each family publish a cognitive depth profile: required observation-history distinction, retention horizon, planning/delay depth, alternative-action branching, observation cost, irreversibility, compositional reuse range, source ambiguity, and law-shift frequency. Do not compress it into one intelligence score.
The **minimum sufficient policy** is relative to a solver class and budget: enumerate reactive, lookup, bounded finite-state, short-history, and bounded-search policies on tiny instances; publish the smallest successful witness and any established lower bound. The smallest solver tried is only an upper bound.
Deepen one axis while holding others controlled. If a reactive policy solves a purported memory task, repair the world or lower its claim; do not merely enlarge it. Demonstrate both solvability by a seeded capable control and failure of the specific cheap alternative the world is supposed to exclude.
For example, show a balanced hidden bit once, then a blank delay, then require its report with identical final observations and no writable external environment. A memoryless policy has expected accuracy at most one-half; a two-state retained witness can solve it. Eliminate timing/action-history side channels explicitly. This establishes one narrow memory demand, not reasoning in general.
Curricula vary order, environmental diversity, lifetime duration, and nonstationarity. Preserve equal interaction counts and an irrelevant-history control; do not quietly replace more difficult experience with more total experience.
Inheritance should specify low-level material and permissible update physics; development may construct problem-specific and reusable organization; the world supplies consequences and information costs. Whether this partition beats inherited complete solutions is Q2, not an axiom.
Initial pressures compare fixed scalar utility with a small preregistered multiobjective frontier: competence, acquisition cost, retained performance, and resource use. Novelty has a capped allocation and cannot override qualification.
Reserve one-third of discovery evaluations for non-LLM structural/stochastic generation, including mechanisms not assigned familiar labels. This is a provisional anti-prior allocation, not evidence that random search is unbiased or sufficient.
Adaptive world search, ecology, cooperation, and adversaries are deferred until static-world instrumentation qualifies. Their later admission requires independent fixed test panels and a specific explanatory gap; open-endedness is not an initial milestone.

## 5. Operational estimands and factorial interventions
Let B be a resource vector: total inherited/authored information, interactions, native transitions, host compute, peak/live memory, storage, energy, and operator/model assistance. Report both common caps and achieved Pareto frontiers; no single conversion makes fundamentally different substrates perfectly equivalent.
Let K be cost to a preregistered competence threshold, with retention/quality constraints. Failures to reach it are censored at the cap; analyze success probability and censored cost jointly, rather than assigning a fictitious cheap cost to failure.

| Target | Operational evidence | What it does not establish |
|---|---|---|
| Latent capacity | A directly constructed witness in a track performs the required behavior within B; exhaustive impossibility is available only for a completely enumerated finite subspace | Witness existence is a lower bound, not proof that allowed search or experience can find it |
| Developmental reachability | Probability and cost of constructing qualifying behavior from a declared unseeded initialization distribution under allowed histories, update physics, and search | Zero observed successes gives a budget/path-dependent bound, not absence of latent capacity |
| Realized competence | Performance, robustness, uncertainty calibration where measurable, and retention at a fixed checkpoint with task learning disabled and hidden test state inaccessible | A successful trained policy need not transfer, develop, or reason generally |
| Transferable sagacity | Prior development reduces K on sealed new causal families, survives retention constraints and a causal reuse test, with pretraining and inherited-state costs separately disclosed | Target-only savings need not repay full lifecycle costs; include amortization over a declared number of future tasks |
| Recursive sagacity | Experience changes a process that subsequently improves the construction of fresh learning processes, supported by the nested tests below | Not unrestricted recursive self-improvement, an infinite hierarchy, or a logical category outside all meta-learning |

Q1 crosses persistence enabled/disabled with revisitation enabled/disabled, using writable/read-only variants where valid; its witnesses delimit what each physical cell can express. A realized-competence assay freezes **retained learning**, not working-state transitions required for inference. If those cannot be separated, publish prequential performance and do not mislabel it frozen competence.
The core Q2 comparison is a blocked 2 x 2 x 2 factorial: structured versus shuffled/irrelevant history H; native developmental modification enabled versus clamped P; direct-solution versus low-information inherited initialization I. Rerun at two matched resource envelopes B-low/B-high only after qualification. State which comparisons use shuffled versus irrelevant H; do not pool them without justification.
Within each I and B stratum, estimate the H-by-P interaction: the history benefit when modification is enabled minus its benefit when clamped. A positive interaction supports developmental dependence, not automatically abstraction; Q3-Q5 test reuse and mechanism. Compare direct-solution competitors with their greater inherited information charged rather than pretending their information is equal.
Pair clone interventions by initial organism and world draw; replicate across independently sampled founding lineages and generator families. Clamping receives a compute-matched sham where possible; report any unequal effective search power. A separate no-history naive arm measures absolute learning, not just order effects.
Q3/Q4 cross prior history with targeted mechanism intact/lesioned (plus equal-damage sham), and target novelty within-family/new-causal-family. The history-by-lesion contrast on new families tests reusable developmental benefit; the novelty interaction distinguishes broad reuse from retention. Randomize clone assignment and match available acquisition resources in every cell; qualify lesion validity before interpreting an interaction.
No intervention may gain hidden observations, extra search evaluations, model calls, or retained state. Endogenous restructuring is a demonstrated change in available/reused operations and future trajectories, not merely more nodes or a new tensor shape; representation changes may be functionally trivial.
Compression Q3 measures whole encoder/decoder/structure length, held-out predictive and intervention loss, retained competence, and future K. Generic byte compression and dictionary storage are controls. A shorter representation that worsens prediction/transfer is not the target; a longer reusable mechanism may qualify if it reduces total future cost.
Revision Q4 measures warranted revision latency, false revision under stable laws, information value net of observation cost, irreversible-action regret, and calibrated choices under risk. Confidence is inferred only through a validated scoring interface; no subjective belief is attributed to an opaque state by fiat.

### Nested causal criterion, not an ontological escape from meta-learning
Use functional levels: S is a task-solution state; U is the process changing S; V is the process constructing/changing U. These labels describe interventions after the fact, not built-in organism modules. Ordinary task learning changes S; a conventional fixed-V meta-learner can improve U.
1. Develop independent organisms on family A versus matched control histories; obtain candidate V-old/V-developed slices or native intervention-defined equivalents. All separation procedures are qualified for off-target effects and information carried.
2. Cross V provenance with V's ability to change U (enabled/clamped). Initialize fresh, identically distributed U and S, then expose family B at matched cost. Test whether V-developed produces a better U-B than V-old; merely retaining A task solutions is prevented by reset and audited transplantation.
3. Freeze each resulting U-B, initialize fresh S again, and measure acquisition on sealed family C with no A/B solutions or hidden optimizer state except the declared transplanted process. Compare to fixed-V meta-learning, optimizer-state-only transfer, longer-training, and equal-information controls.
4. Lesion the implicated change to V, demonstrate loss of the B-to-C learning advantage, then rescue it. Cross V and U donors to distinguish carried task knowledge, better current U, and an improved ability to construct U. A sham matches damage/compute but not the proposed causal function.
5. Repeat the mediated contrast on fresh D-to-E families and an independently implemented qualifying world/ruler; test whether the developed process remains useful when both target learner and task class are new. Report tested nesting depth and the lifecycle cost; additional depths require additional experiments.
If only S improves, call it task learning; if an improved U helps fresh S but an advantage in constructing U remains unshown, call it learning-to-learn. If history changes V and that change causally improves fresh U construction and fresh S acquisition, call it **nested developmental improvement at tested depth two**, provisionally recursive sagacity within this protocol.
Changing optimizer state alone is **not logically outside broad meta-learning**. If such state satisfies the nested causal tests, it is an admissible mechanism; if a conventional meta-learner explains the whole effect, report that rather than asserting conceptual novelty. Functional nesting is the stronger experimental demand, not an ontological claim.
Distributed processes may resist valid slicing. Then substitute qualified whole-organism clamping/counterfactual replay if possible; otherwise mark the mediation unidentifiable and withhold the recursive-mechanism claim. Failed transplantation alone is not disproof.
No finite battery here certifies general reasoning. Generality is an expanding, explicitly bounded empirical envelope, never a passed global checkbox.

## 6. Qualification, statistics, holdouts, and typed outcomes
Every lane first recovers a constructed positive, rejects cheap negatives, and treats shams/neutrals correctly across a range of effects, noise, and costs. Controls must be capable of failing: deliberately break the positive, restore the negative's missing capability, and verify the ruler changes its response for the right reason.
Seeded controls are disjoint from discovery organisms and holdouts; control names are blinded to scoring. Positive fixtures use independently computed behavior/ground truth rather than invoking the ruler's implementation as an oracle.
Provisional qualification gates: a one-sided 95% lower bound on sensitivity at delta* of at least 0.80, and a one-sided 95% upper bound on false-positive rate of at most 0.05 within each registered operating regime. Neutral/sham effects must lie within a preregistered equivalence margin, not merely have p > 0.05.
These are demanding planning targets, not achieved calibration. Sample sizes follow exact/binomial or appropriate clustered calculations before execution; if the small budget cannot qualify a regime, narrow the regime or label the work calibration-only. Never lower the gate after looking at results.
Each confirmatory contrast gets alpha-family = 0.05 with a frozen Holm family (or a preregistered sequential alternative), target power >= 0.80 at delta*, and a reported effect interval. Precision and practical relevance matter alongside significance. Qualification and discovery use different draws from confirmation.
Independent units are founding lineages crossed with independently generated world families; episodes and checkpoints are repeated measures. Use paired contrasts with lineage/family-aware uncertainty, explicitly conditioning claims on fixed families when family counts cannot support population inference.
Optional stopping, exclusions, failed jobs, timeouts, and repaired implementations are preregistered or disclosed. A repair invalidates affected runs and triggers requalification, not selective deletion of inconvenient outcomes. A wide interval is inconclusive even if a headline p-value is large.
Holdout custody: a separate evaluator stores sealed generator lineage/configuration hashes and seeds; search and interpreters cannot inspect them. Candidate selection, adapters, ruler versions, thresholds, and analysis lock before unsealing. No individual test feedback returns to the active search; reuse after any tuning becomes development data.

| Typed disposition | Required evidence / allowed reading |
|---|---|
| `CAPACITY_UNESTABLISHED` | No bounded competent witness; organism adequacy remains unknown, not proven impossible |
| `WORLD_INSUFFICIENT` | A cheap policy bypasses the intended demand, or no qualified solver establishes solvability |
| `DEVELOPMENT_UNREACHED` | A witness exists but allowed histories/updates do not reach it within B; report a reachability bound |
| `PRESSURE_UNINFORMATIVE` / `SEARCH_UNDERPOWERED` | Positive pathways are not selected or not found in qualified planted-path trials; only diagnose the component actually isolated |
| `RULER_UNQUALIFIED` / `STATISTICALLY_INCONCLUSIVE` | Instrument bounds fail, or uncertainty does not resolve delta*; scientific hypothesis not rejected |
| `IMPLEMENTATION_DEFECT` / `PROVENANCE_INVALID` | Contract violation, replay mismatch, or tainted exposure blocks scientific interpretation |
| `INTERVENTION_UNSUPPORTED` / `INTERVENTION_INVALID` | Delivery/compatibility/off-target effects prevent the proposed mechanistic inference |
| `BUDGET_CENSORED` | Resource cap reached; retain consumed cost and incomplete outcomes, do not relabel as incompetence |
| `BOUNDED_NEGATIVE` | All relevant prerequisites qualify and the interval excludes the registered meaningful advantage under stated paths/worlds/B |

Outcomes may carry multiple diagnostic flags; `CAUSE_UNRESOLVED` is preferable to fabricating which component failed. A bounded negative is not proof of exact zero, all-world failure, or impossibility of reasoning.
Claim ladder: anomaly -> independently repeated effect surviving cheap/adversarial baselines -> intervention-supported mechanism with rescue -> reusable reasoning/developmental primitive in declared tasks -> transferable mechanism -> cross-substrate architectural principle. Each promotion adds its stated evidence; attractive interpretation cannot skip a gate.
Transplantation is strong evidence where delivery is valid, not a universal prerequisite for all mechanisms. Independent implementations and external reruns support broader claims. Failures and corrections can lower claim levels; the ladder is not irreversible progress.

## 7. Six bounded experimental lanes
All lanes inherit section 6 qualification and section 8 budgets. No legacy component is designated for reuse; all reuse decisions are UNKNOWN pending a committed freeze and later requirement-based audit. Listed new pieces are functional needs, not authorization to implement them now.

### Q1. Which minimal physics carries the intended capacity?
- Question/physics: in A/B/C, which persistence, writable-state, revisitation, and internal-compute affordances are necessary for bounded delayed hidden-state control? Use exact small worlds and hand-constructed native witnesses, not search success as proof of capacity.
- Pressure/development: initially none beyond explicit witness construction; cross persistence/revisitation affordances as in section 5, then vary a memory/delay axis while charging maintenance and transport. This qualifies the possibility space before asking about emergence.
- Qualification/baselines: known-positive finite-state witness, no-memory/reactive negative, redundant-state neutral, and short-history/lookup competitors. Independently enumerate distinguishable histories in tiny instances.
- Causal/transfer test: disable and restore persistence or revisit paths; increase delay and relabel observations. Test alternate generator encodings without supplying a new semantic decoder.
- Risks: false positive from free observer memory or privileged addresses; false negative from a bad witness or unqualified adapter. Needed: tiny solvers, native traces, safety/conformance tests; cost is CPU plus trace storage.
- Kill/meaning/ceiling: stop a track if it cannot execute its witness within the envelope after a bounded repair; qualify capacity in a limited task family, never endogenous development or general reasoning.

### Q2. When is constructing solutions better than inheriting them?
- Question/physics: use the H x P x I design in qualified tracks; compare variable native structure/update rules to fixed-topology/fixed-update controls in worlds varying lifetime duration and hidden-law diversity.
- Pressure/development: charge inherited information and lifetime acquisition; contrast stochastic search, explicit direct solutions, and adaptation-capable initial material. Keep matched search evaluations and distinguish total lifecycle from target-only cost.
- Qualification/baselines: an authored adaptive controller is the seeded positive; a task-index lookup with no hidden-law access is a negative for genuine adaptation; repeated stationary tasks are a neutral regime where development need not help.
- Causal/transfer test: clamp developmental changes, replay shuffled histories, reset accumulated state, and rescue retained update physics; seal new law combinations and compare naive, fixed meta-learner, and longer-training arms.
- Risks: false positive from inherited answers or extra experience; false negative from unreachable search paths or a lifetime too short to repay development. Needed: lineage/reset ledger and factorial runner; CPU/search dominates.
- Kill/meaning/ceiling: if planted adaptive pathways cannot be reached/selected, diagnose search/pressure before scaling; a positive establishes history-dependent developmental advantage in specified regimes, not an architectural winner.

### Q3. Does compression preserve useful causal structure?
- Question/physics: follow Q2 checkpoints in A/C first, admitting B only after a qualified readout; test whether reduced description/prediction complexity accompanies reuse across compositional causal/tool worlds.
- Pressure/development: vary memory/maintenance costs and consolidation opportunity with equal observations; reward task success and cost separately rather than rewarding short strings directly.
- Qualification/baselines: a seeded reusable transition rule is positive, a compressed dictionary with matched size is negative for new-law reuse, and arbitrary invertible recoding is neutral when its adapter is fully counted.
- Causal/transfer test: lesion/transplant implicated structures, compare structure-destroying scrambling to functionality-preserving relabeling, and test unseen compositions plus changed causal laws; score predictive loss, intervention loss, retained skills, and K together.
- Risks: false positive from free decoder knowledge or identical hidden generators; false negative from representation-dependent code length or destructive recoding. Needed: complete-code accounting and independent loss/transfer rulers; memory and CPU dominate.
- Kill/meaning/ceiling: stop the compression interpretation if savings disappear after decoder cost or do not improve future acquisition; report functional reusable compression only in the tested envelope, not that all compression is cognition.

### Q4. Can selective revision develop and transfer?
- Question/physics: in qualified tracks expose ambiguous sources, misleading first evidence, costly observations, and irreversible choices; do not install hypothesis registers or confidence labels in the organism.
- Pressure/development: vary reliability and regime changes independently; compare history-trained versus naive and plasticity-clamped organisms with the same observation/action budget.
- Qualification/baselines: an authored Bayesian/finite-state decision policy is positive; always-switch, never-switch, always-query, and simple change detectors are cheap competitors; consistent stable evidence is a neutral condition.
- Causal/transfer test: alter evidence order without changing information, intervene on source reliability, lesion retained evidence/revision dynamics, and rescue; hold out source mechanisms and invert superficial cues.
- Risks: false positive from learning a rewarded reversal cue; false negative from invalid confidence readout or unaffordable observations. Needed: exact small decision models, regret/calibration rulers, and revision traces; CPU and review attention dominate.
- Kill/meaning/ceiling: if cue-following baselines explain the effect, redesign the world or narrow the claim; success means transferable functional evidence-sensitive revision, not introspective consciousness or a named faculty.

### Q5. Is a proposed mechanism causal and portable rather than an apparatus artifact?
- Question/physics: nominate only qualified Q2-Q4 effects; independently implement their decisive world/ruler contract, then test within-track transplant and cross-track functional reconstruction where compatibility qualifies.
- Pressure/development: no new open-ended search; recipients undergo fixed fresh-family learning with equal initialization/adaptation resources. Track every authored adapter and reconstruction decision as transferred information.
- Qualification/baselines: known portable native mechanism is positive, scrambled/blank donor is negative, same-organism round-trip transplant is neutral; adapter-only and equal-damage lesions are mandatory cheap controls.
- Causal/transfer test: donor-process x recipient-state crossover with lesion/rescue, plus an independent simulator/ruler path; qualified nuisance recodings test whether the mechanism or the interface carries the benefit.
- Risks: false positive from hidden teaching in adapters or shared solver code; false negative from incompatibility or off-target damage. Needed: delivery qualification and independent implementation; engineering/attention may dominate compute.
- Kill/meaning/ceiling: unqualified delivery stops portability inference, not the native claim; independent replication plus controlled reuse supports a transferable mechanism, with a cross-substrate principle only after separate reconstruction succeeds.

### Q6. Does experience improve the construction of future learning processes?
- Question/physics: apply section 5's nested protocol only where native update-rule intervention is qualified, starting with A/C rather than assuming every medium supports identifiable slicing.
- Pressure/development: sequential A -> B -> C and fresh D -> E families; experience may change the process constructing later update processes, with initialization resets and full lifecycle costs.
- Qualification/baselines: a deliberately authored nested updater tests sensitivity only; fixed-V meta-learning, optimizer-state-only transfer, equal-information memory, and extra-training arms test specificity; sham V changes test neutrality.
- Causal/transfer test: cross developed/old V with enabled/clamped U-construction, swap U donors, test fresh S learners, and lesion/rescue the specific nested advantage under sealed family shifts.
- Risks: false positive from carried task solutions, compute escalation, or renaming optimizer state; false negative from nonseparable distributed updates or weak mediation instruments. Needed: nested reset/crossover runner and qualified process interventions; CPU and causal-audit attention dominate.
- Kill/meaning/ceiling: if ordinary fixed-V learning or task-state carryover explains the effect, report that narrower result; success establishes a resource-bounded nested causal improvement, not escape from broad meta-learning or unlimited recursive ascent.

## 8. Staging, resource envelopes, and stop gates
These are provisional **planning caps**, not measured runtime predictions, purchases, or execution authorization. No research was run for this design. Smaller manifests must fit the caps; if power/qualification cannot fit, the deliverable becomes a pilot or methods result rather than an underpowered confirmation.

| Stage / target window | Build and evidence required before promotion | CPU cap (core-hours) |
|---|---|---|
| S0, days 1-30 | Minimal protocol, A/B/C tiny interpreters/simulators, budget/replay tests, Q1 witnesses, control calibration and independent reference checker | 72 |
| S1, days 31-60 | Q2 factorial in qualified tracks; fixed holdout custody; depth/policy certificates; narrow reachability and cost contrasts | 120 |
| S2, days 61-90 | Q3/Q4 contrasts and Q5 causal/independent checks only for qualified effects; externalizable positive or typed-null bundle | 180 |
| S3, conditional after S2 | Q6 only if nested intervention validity and transfer prerequisites pass; otherwise retain this allocation unspent | 72 |
| Reserved audit | Independent rerun, fault reproduction, or correction; not extra discovery selected by appealing outcomes | 36 |
| Total ceiling | Release each stage separately; a failed gate does not authorize consuming the remaining budget | 480 |

Initial concurrency <= 4 CPU workers, aggregate RAM <= 16 GiB, retained artifacts <= 40 GiB, and one job <= 6 core-hours / 12 wall-hours before checkpoint or termination; bootstrap/unit qualification cases should take seconds or minutes. Native transition/sample limits are calibrated and frozen per track before running organism comparisons.
GPU allocation is initially zero. Consider an explicitly approved accelerator arm only after an equivalent benchmark demonstrates complete-experiment cost/energy benefit without ruler drift. CPU availability is a charter assumption, not verified hardware inventory.
External inference calls in all experimental inner loops: **zero**. Optional offline interpretation cap: 20,000 total input/output tokens for the pilot, with provider/model/cost recorded and approval required before use; no cap is an instruction to consume it. Local organism forward dynamics count as candidate compute, not an external model oracle.
Provisional energy ceiling: 30 kWh for the campaign including assigned idle/verification overhead. Estimate energy as active/idle host-time times measured power or an explicit power interval; use the interval's upper bound to stop conservatively when no meter exists. Core-hours alone do not determine host-hours or joules.
Money ledger: compute charges + storage charges + token charges + measured/estimated electricity under a declared no-double-counting boundary. No dollar cap can be finalized without local/cloud rates; do not start paid runs before the operator specifies one.
Operator attention cap: two scheduled 30-minute decision reviews per week plus a separately approved initial build/qualification allowance. Maximum five unresolved nonurgent anomaly packets; deduplicate faults, pause promotion at overflow, and never hide urgent integrity/resource failures to meet the cap.
Dominant cost expectation is qualitative until S0 benchmarks: A traversal/logging; B transport simulation; C numerical state updates; Q5 independent engineering; Q6 causal audit. Cap allocations include negative results and qualification overhead, not just successful organisms.

## 9. Falsifiers and allocation decisions
- If the minimal witnesses cannot be made to work in the small envelopes, revise the physics/interface or scope; do not blame emergence and do not spend on larger searches.
- If seeded effects are not detected or negatives routinely pass, pause scientific interpretation and qualify the instruments. A beautiful trajectory is not an exception.
- If cheap sufficient policies explain all apparent depth, reject those worlds as discriminators even if organisms obtain excellent scores.
- If qualified Q2-Q4 contrasts show no meaningful developmental/transfer advantage with intervals excluding delta* across the registered regimes, reject the **current developmental advantage thesis in those regimes**; do not reject all possible reasoning.
- If most cost is adapter/qualification overhead and independently implemented tracks yield no distinct predictions, consolidate toward an integrated engine after documenting the lost coverage. If one common blind spot remains, replace a track before simply multiplying engines.
- At 6-12 months, persistent unqualified rulers imply an instrumentation failure; qualified bounded negatives and domination by fixed/reactive/meta-learning baselines imply the thesis is badly framed or the selected regimes do not require it. Neither outcome warrants an endless larger-scale retry without a new discriminator.
- A successful ordinary meta-learner is useful evidence, not a failure to discover sufficiently exotic machinery. An unfamiliar organism without causal/transfer evidence remains an anomaly, not an architectural principle.

## 10. Missing specifications and handoff
Required before implementation/confirmation: approved hardware/rates/energy measurement boundary, aggregate dollar and engineering-attention caps, exact native instruction/reaction/numerical rules, adapter tariffs, delta* and equivalence margins per world, independent unit counts/power calculation, and holdout custodian/access controls.
Also open: how to construct minimally informative initial distributions fairly across tracks; how much independent world-generator diversity the budget can support; when a process slice is causally identifiable; and which transferable mechanism would justify additional nesting depth. These are registered design forks, not claims already settled by this document.
No current-program scientific legitimacy verdict, salvage recommendation, reuse fraction, or historical failure attribution is supplied. Those require evidence unavailable by design in Stage I; later salvage must be requirement-led with costed rebuild alternatives and immutable change records.
Immediate handoff is three files only: requirements, this v0 architecture, and `process/STAGE_I_FREEZE.md`. The parent must commit the immutable freeze before anyone acting on this analysis reads salvage material; this execution neither stages nor commits it.
If starting today without existing engines, I would first build the smallest three-track capacity-and-ruler observatory, with exact tiny worlds, deliberately breakable controls, lineage/reset accounting, and an independently implemented checker. It would reveal whether the proposed physics, worlds, and measurements can discriminate development from supplied answers before spending on a large search, while preserving the possibility that an integrated engine, an ordinary meta-learner, or a bounded negative is the correct outcome.

## POST-AUDIT ADDENDUM: ADOPTED POST-AUDIT RECOMMENDATION 2026-10-01

**Adopt a sequential A0-first observatory with an independent scientific checker, not three runtimes by day 30.**
This appendix is the current report recommendation after audit. It preserves rather than retroactively rewrites the first-principles architecture above.
The original Stage I snapshot is commit `eeeda08bb45757298b3cb21ee22d816b44388aef` (`eeeda08bb`); its original 201 lines remain the byte-canonical prefix of this file.
That prefix is 40,311 bytes, SHA-256 `d90d1b5d5ee80d00c0d6dc3c9d6110436588cba62a109a5fa874b94c13fa173d`, excluding the new separator and appendix.
The frozen [requirements](REQUIREMENTS.md) and original [process record](process/STAGE_I_FREEZE.md) are not edited by this recommendation.

### A. Why the delivery recommendation changes

The [main report](PHASE3_META_ANALYSIS.md), [portfolio](ENGINE_PORTFOLIO.md), [MVP](MVP_90_DAYS.md), [salvage matrix](SALVAGE_MATRIX.md), and [failure map](FAILURE_TO_GATE_MAP.md) support a narrower first implementation.
Historical failures motivate independently grounded controls, ordinary baselines, complete state/exposure receipts and fail-able admission routes; they do not establish that a new native runtime or ruler has qualified.
Engineering and independent-checker effort, whole-assay calibration, and human review are binding risks not solved by idle CPU capacity.
Start with A0 plus W0, breakable seeded controls and an independently authored checker; then one qualified Q2 regime, normally one Q3-or-Q4 discriminator, and a locked Q5 independent contrast.
B and C retain different locality/addressing/update hypotheses, but enter only when a concrete unresolved physical prediction and qualified capacity path justify their measured cost.
Six question lanes remain; no lane is a promise of a separate software service or a successful scientific finding.

### B. D1-D5 are adopted, not awaiting another recommendation decision

| Delta | Adopted post-audit recommendation | Relationship to original Stage I | Direct evidence required before operational promotion |
|---|---|---|---|
| D1: sequential runtime construction | Build A0 and its independent checker first; keep B/C specified, not three day-30 runtimes | Explicit temporary deferral of R-APR-01 and the original S0 implementation breadth; controls/wrappers do not count as new tracks | Native witness/reset/codec/meter qualification and independent truth inside S0; a later track needs a distinct testable physical alternative |
| D2: one initial resource regime | Begin Q2 in A at B-low; defer B-high and cross-track interactions | Narrows the initial factorial without asserting deferred contrasts were estimated | Pilot variance/censoring/timing, applicable native whole-assay calibration, frozen analysis/custody and affordable fresh confirmation |
| D3: stronger ordinary competitors | Explicit constant, reactive/direct-table/FSM, library-order, fixed-meta/plasticity and equal-total-exposure competitors | Sharpens existing baseline duties rather than declaring familiar mechanisms invalid | Executed nonempty comparator cells, equal eligibility/exposure and complete information/lifecycle costs; let a simpler mechanism win |
| D4: minimal operational integration | Local immutable evidence bundles and one fail-closed verifier before any fleet/database/wiki restoration | Narrows shared operations without relaxing generation/reality/measurement/interpretation separation | Real-route guard-disable/restore and clean twins, denied unauthorized access, consumed verifier receipts and correction propagation |
| D5: qualification has an explicit allocation | One receipt, one lane/phase/activity owner; separately account calibration, search, ordinary replay and protected audit | Makes the unchanged aggregate CPU ceiling operationally auditable; does not establish throughput | Measured complete-batch forecast, full sample/cell counts, energy and labor ledgers, valid power and no hidden shared-overhead addition |

**No additional operator approval is needed to state or adopt D1-D5 as this report's recommendation.** Earlier companion requests for that decision record proposal-stage status and are superseded at recommendation level by this dated appendix and the main report.
This is not operational approval: actual spending, host access, staffing, rates/dollar cap, energy boundary, custody, untrusted execution, bounded run authority and holdout release remain genuine gates.
The original process record's PENDING wording is likewise historical; the cited commit identifies the actual Stage I snapshot without falsifying its original chronology.

### C. Corrected scientific contract and unresolved implementation details

The final MVP and portfolio specify the corrected detailed contract. This appendix summarizes it without presenting a native runtime as implemented; executed documentary and arithmetic checks are recorded separately in process/VALIDATION.md.

- **A0 addressing:** the MVP now specifies byte/record/cursor/link/operand semantics and witness bytes; native implementation and independent traces remain required. Do not infer a free addressing operation, accept a host-language witness in its place, or count a specification as qualified capacity.
- **Search adequacy:** **8 of 32 persistent search slots** form the competence-neutral bridge arm, accepting equal-competence proposals with fixed probability 1/2 even when cost worsens. This allocation is not an 8/32 recovery threshold. Freeze path-specific finite-budget recovery criteria before calibration; strict-ascent failure diagnoses the operator, not an absent path in the physics.
- **W3-R:** three cues each have 75% reliability; conditional independence gives majority accuracy **27/32**. Query prices are **1/32** and **1/8**. Under the correlated law **c2=c3**, duplicated evidence does not create an extra independent vote and the optimum is no query at the positive prices. Require an independent rational/native oracle for the entire joint law.
- **Q4:** the corrected meaningful contrast is **delta*=0.02**, not the Q2/Q3 0.20 planning contrast. Its qualification, noise/effect grid and power are separate; it is likely pilot-only within the existing envelope. A Q4-derived Q5 contrast inherits this endpoint/scale, not the acquisition criterion.
- **Q5:** budget and execute **18 candidate-specific cells plus 2 paired rescue cells per founder block**. Generic calibration shams cannot substitute for candidate-specific damage/donor controls; paired rescues do not increase independent n.
- **Detection units:** whole-assay batch-statistic sensitivity cannot adjust a per-founder zero-hit bound. A latent founder-success bound needs an applicable independently qualified founder-level detector or perfect verification, with uncertainty combined explicitly.
- **Qualification scope:** native curated-mechanism controls qualify only their declared operating regime and coverage. They do not certify detectability of every endogenous mechanism or prove a class-wide limit on development. Keep that applicability question open until independent evidence supports it.

These corrections are design/calculation requirements, not newly observed experiments. Where current historical prose or an uncorrected draft disagrees, no executable manifest may be released until the corrected pre-data contract is reconciled.

### D. Resource ceilings remain planning limits

| Resource | Adopted ceiling and boundary | Missing operational evidence |
|---|---|---|
| CPU | **480 core-hours = 372 days 1-90 + 72 conditional Q6 + 36 protected fault/correction audit** | Measured complete-assay throughput, all process-tree/retry costs and a forecast with 25% timing contingency |
| CPU subaccounting | Days 1-90: 108 qualification + 186 assay/search + 78 ordinary replay = 372; calendar S0/S1/S2 = 72/120/180 | Same receipts viewed by lane/activity/phase, not additive budgets; routine Q5 replication does not consume the protected audit allocation |
| GPU | **0 GPU allocation and 0 paid-GPU spend** | Any future accelerator requires a separately authorized, equivalent whole-experiment cost/energy case |
| Energy | **30 kWh** including attributed idle and verification | Meter or conservative host power/time bounds, concurrency attribution and stopping at the conservative endpoint |
| Inference | Zero routine external calls; **20,000 optional input-plus-output campaign tokens** maximum | A separately approved offline question, permitted evidence, provider cost and usage receipt; not report-authoring token accounting |
| First-90-day engineering | **320 person-hours cap**, including 64 protected for independent scientific implementation | Staffed authorship and actual work receipts; a later <=24-hour B0-or-C0 spike replaces optional scope, not adds to it |
| First-90-day scientific review | **21 hours**: 13 scheduled plus 8 initial; at most five unresolved nonurgent packets | A real reviewer/custodian, fail-closed overflow and distinct engineering versus review accounting |

Conditional Q6 can require separately released additional engineering/review; it is not hidden inside the first-90-day labor totals.
The existing per-job/concurrency/RAM/storage bounds still apply. Money, staffing and energy approvals cannot be inferred from these numbers; **caps are not measurements, availability claims or authorization**.
If calibration, candidate-specific controls, precision or independence cannot fit, the deliverable becomes methods/qualification-only or a descriptive pilot, not a weakened gate or inflated claim.

### E. What direct evidence would change this recommendation

1. **Stop or revise A0:** independently traced native witness/reset/meter failure after the one bounded S0 repair, or an irreparable address/codec loophole. Report the implementation/capacity limit, not failed emergence, and do not respond with three simultaneous larger runtimes.
2. **Prefer the ordinary learner:** applicable independent H/P/I and new-family tests exclude meaningful advantage while ordinary competitors dominate full lifecycle costs. Preserve the bounded negative and narrow the program rather than protect a developmental narrative.
3. **Keep Q4 at pilot/world qualification:** exact headroom exists but a qualified 0.02-regret detector and fresh precision cannot fit. A tiny correct oracle is a valid methods result, not a developmental revision finding.
4. **Withdraw a mechanism or portability claim:** delivered candidate-specific sham/adapter controls explain the benefit, or a qualified independent contrast excludes it. Unsupported delivery alone blocks portability without erasing warranted native behavior.
5. **Add a second track or consolidate:** a measured affordable locality/addressing/update contrast can justify B/C; redundant answers with high adapter/qualification cost favor fewer implementations with disclosed coverage loss.
6. **Stop recursive interpretation:** fresh-U/S resets reveal carried solutions, valid fixed-V controls explain the extra level, or process intervention stays unidentifiable. Retain useful task/meta-learning evidence; no ontological escape from broad meta-learning is required or established.
7. **Correct the critic:** primary-source/clean-twin evidence refutes a review allegation. Remove the unsupported allegation and its dependent claims while retaining real defects; reviewer consensus cannot override evidence.

The [25-assumption ledger](ASSUMPTIONS.md), [engine and 6-12 month falsifiers](FALSIFIERS.md), and [15 ranked open questions](OPEN_QUESTIONS.md) specify direct evidence, functional owner roles, cost limits and the conditions for these reversals.
Qualified negative evidence requires applicable capacity/world/search/pressure/ruler/intervention/custody/precision prerequisites; apparatus failure instead limits feasibility and may stop this program without disproving possible cognition.
No unlimited repair clause protects the thesis. Any restart after the bounded stop requires a genuinely new discriminator and a scoped resource plan, not only more scale or another name.

### F. Publication and validation boundary

The latest user mandate overrides historical restrictions on **publication planning** and explicitly authorizes committing this design package. Repository delivery is distinct from external publication/submission, evidence-wiki write, holdout disclosure or campaign execution; those are not authorized here.
No research experiment, native benchmark, engine qualification or historical campaign reproduction was executed to write this appendix. Historical source/audit claims retain their original scope and evidence grade.
File/link/count and byte-prefix checks validate the documentary package only. Subsequent authorized implementation should write/update and run native transition, reset, leakage, cap, exact-oracle, statistical-boundary, candidate-intervention and actual-promotion-route tests before any claim-bearing experiment.