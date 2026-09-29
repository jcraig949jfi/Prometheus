# Operator directive (verbatim, received 2026-09-24 by Bellerophon[m2-9e74888e])

You are Bellerophon.

The previous forensic and grounding round is complete. Treat its conclusions as the starting state.

Branch containing the completed grounding work:

bellerophon/post-campaign-forensics-2026-09-23

Closing commit:

3efdacf7e

The previous grounding campaign established:

* the harness is operationally trustworthy;
* spontaneous self-replication is real and reproducible;
* replication depends strongly on the existing copying chemistry;
* all five previously exciting "evolvability" flag classes collapsed under causal testing;
* the pollination/topology effect was caused by migration duplicating organisms;
* "beneficial-density" was an instrumentation/measurement artifact plus copier/task antagonism;
* external reproduction outperformed endogenous reproduction on task attainment;
* task pressure under the existing physics does not causally affect reproductive dynamics;
* the current substrate therefore has reproductive physics but not adaptive-computation physics.

Your next task is to test whether a minimal physical coupling between useful computation and reproduction is sufficient to create genuine evolutionary pressure on computation and reproductive machinery.

This is an autonomous extended campaign.

NON-NEGOTIABLE OPERATING MODE

Do not ask the operator for feedback, approval, interpretation, or mid-run decisions.

Do not pause for human-in-the-loop adjudication.

Do not provide interim status reports requiring response.

Do not stop merely because one hypothesis fails.

Run the campaign through its preregistered decision tree and return only after the entire campaign has ended and the final analysis is complete.

Total intended runtime:

12 to 25 hours

This may consist of multiple sequential phases, provided they are preregistered before the first scientific run begins.

Alternatively, you may implement it as one large campaign with independent experimental lanes.

Choose whichever gives the cleanest causal evidence and operational reliability.

The campaign must contain enough independent tests that the scientific conclusion does not depend on one assay.

⸻

PRIMARY SCIENTIFIC QUESTION

Test:

Can useful computation causally affect reproductive success through a physical resource constraint, and does that coupling create heritable evolutionary pressure on computation or reproductive organization?

The campaign is not primarily asking whether replication occurs.

Replication is already established.

The campaign asks whether:

computation → physical resource → reproduction → heritable variation

becomes a real causal pathway.

⸻

CORE DESIGN PRINCIPLE

Introduce the smallest possible new piece of physics:

Correct computation earns a resource required for copying/reproduction.

Do not add an explicit fitness score that directly chooses survivors.

Do not make an external scheduler reproduce high scorers.

Do not protect task code manually.

Do not design a special "task genome" and "reproductive genome."

Do not make the environment optimize organisms.

The external evaluator may determine whether a task output is correct and modify a resource balance accordingly.

Ordinary substrate dynamics must determine survival and reproduction.

A preferred minimal relationship is:

correct output -> energy/resource credit -> copying expenditure -> reproductive opportunity

The resource accounting must be explicit, inspectable, conserved or otherwise physically interpretable, and checkpoint/replay safe.

⸻

CAMPAIGN STRUCTURE

Build this as a collection of independent experimental lanes.

Before execution, freeze:

* campaign design;
* hypotheses;
* experimental units;
* treatment definitions;
* controls;
* allocation;
* run budget;
* stop conditions;
* analysis rules;
* detector definitions;
* seed generation;
* exclusion rules;
* success/failure criteria.

Hash the preregistration.

No scientific threshold may be changed after launch.

Do not let the outcome of one lane redefine another lane.

⸻

PHASE 0 — IMPLEMENTATION AND FALSIFICATION

Before any campaign run, implement the computation-to-resource coupling behind an explicit versioned physics mode.

Preserve the old grounded physics unchanged.

Write regression and adversarial tests for at least:

* resource earned only from the declared task output;
* incorrect outputs earn none or the preregistered lower amount;
* organism cannot directly modify its resource ledger;
* no evaluator state leaks into organism memory;
* no reproduction is performed by the evaluator;
* copying is physically charged;
* resource cannot underflow/overflow silently;
* checkpoint/resume preserves exact resource balances;
* deterministic fixtures replay identically;
* external migration does not duplicate organisms unless explicitly intended;
* task output and reproduction accounting are causally separated;
* no reward is accidentally assigned from future information;
* no post-treatment measurement feeds back into the organism;
* task identity cannot alter physics except through declared input/output/resource rules.

Add positive and negative controls.

If implementation bugs are found, repair them before launching.

Do not change the scientific design merely because a test is inconvenient.

⸻

LANE A — PHYSICS QUALIFICATION

Purpose:

Demonstrate that the new coupling actually creates the intended causal pathway.

Use known organisms or controlled fixtures.

At minimum test:

1. known correct computation with coupling ON;
2. same organism with coupling OFF;
3. computation destroyed but copying intact;
4. copying destroyed but computation intact;
5. shuffled task-output mapping;
6. random output;
7. zero-output negative control;
8. known reproducer positive control.

Questions:

* Does correct computation increase available reproductive resource?
* Does increased resource translate into reproduction?
* Does destroying computation reduce reproductive opportunity?
* Does shuffled verification remove the effect?
* Can pure copier speed bypass the resource constraint?
* Can organisms exploit accounting without solving the task?
* Does the result survive checkpoint/replay?

This lane must contain enough independent seeds to quantify effect size, not just demonstrate one example.

⸻

LANE B — FRESH EVOLUTION UNDER COUPLED VS UNCOUPLED PHYSICS

Run matched fresh populations.

At minimum compare:

B1

Task present, coupling OFF.

B2

Task present, coupling ON.

B3

Task present, coupling ON, shuffled verifier relationship.

B4

No meaningful task, but equivalent resource baseline.

Use matched seeds wherever possible.

Keep all other physics constant.

Primary measurements:

* spontaneous replication rate;
* sustained lineage rate;
* task competence;
* reproductive output;
* lineage persistence;
* task competence among descendants;
* correlation between competence and reproductive success;
* ancestry-weighted enrichment of competence;
* extinction;
* mutation load;
* genome size;
* copy cost;
* changes in reproductive organization.

The key test is:

Does task competence become enriched in descendants specifically under the coupled condition?

Do not infer this from raw score alone.

Demonstrate the causal connection.

⸻

LANE C — ABLATION OF THE COMPUTATION→REPRODUCTION EDGE

This lane should prove that the effect disappears when the causal bridge is broken.

At minimum include:

* coupling removed;
* reward randomized across organisms;
* reward delayed beyond reproductive relevance if technically meaningful;
* reward attached to a task-irrelevant observable;
* identical average energy supply without task contingency.

The important distinction is between:

having more energy

and

earning energy through computation.

If simple extra energy reproduces the same result, the mechanism is not task-driven selection.

⸻

LANE D — REPRODUCTIVE MACHINERY RESPONSE

This lane asks whether selection changes reproduction itself once computation matters.

Use frozen structural descriptors defined before execution.

Track:

* copy boundaries;
* copy instruction placement;
* reproductive code length;
* copy routine redundancy;
* task-code preservation;
* code relocation;
* modular separation;
* genome architecture;
* copy fidelity;
* mutation tolerance;
* replication speed;
* offspring viability;
* proportion of copied genome devoted to useful computation.

Do not label any structural change "adaptive" unless it causally improves reproductive success under the coupled physics.

Where candidate architecture changes appear, automatically perform matched replay/ablation tests after the discovery phase.

⸻

LANE E — PRESERVATION VERSUS DESTRUCTION OF TASK CODE

The previous round showed that the copier often damages useful task code.

That antagonism is now a scientific opportunity.

Ask:

Once useful computation finances reproduction, does evolution discover ways to reproduce while preserving the computation that pays for reproduction?

Measure across generations:

* loss rate of task function;
* retention of task function after reproduction;
* location of task code relative to copy routine;
* copy-boundary evolution;
* duplication;
* redundancy;
* repair-like behavior;
* relocation;
* mutation buffering;
* offspring competence.

Compare coupled and uncoupled controls.

Do not build preservation mechanisms into the substrate unless required as a positive control.

Let evolution solve the conflict if it can.

⸻

LANE F — TASK DIFFICULTY / GENERALITY

Use multiple task classes.

At minimum include several levels of computational complexity, such as:

* trivial constant behavior;
* simple transformation;
* conditional;
* multi-input;
* compositional task.

Use existing task families where suitable.

Do not assume harder tasks produce better science.

Ask whether coupling works across task structure and whether harder tasks alter reproductive architecture.

Important:

The previous G1T result showed multiple task cells could be run-for-run identical because task performance had no effect on dynamics.

Under the new physics, test whether task identity now causally changes evolutionary trajectories.

⸻

LANE G — SUBSTRATE DEPENDENCE

Run limited matched tests to determine whether the new effect depends entirely on the unusually permissive current copying chemistry.

At minimum compare baseline physics against selected perturbations such as:

* reduced copying efficiency;
* increased copy cost;
* reduced neutral NOP-like space;
* modified LDIR availability or cost;
* fresh target memory;
* lower mutation supply.

Do not redesign everything at once.

Use one-factor interventions where possible.

The question is:

Does computation-reproduction coupling survive changes to replication accessibility?

⸻

LANE H — INDEPENDENT ORIGIN ANALYSIS

For all positive phenomena, distinguish:

* independent origins;
* descendants of one origin;
* repeated rediscovery of the same mechanism;
* promoted neighborhoods;
* copied organisms;
* migration descendants.

Create ancestry/mechanism clusters.

Report:

* raw event count;
* unique lineage count;
* independent-origin count;
* mechanistically distinct origin count.

Never treat descendants as independent discoveries.

⸻

LANE I — ADVERSARIAL EXPLOIT SEARCH

Actively search for ways the new physics can be gamed.

Examples include:

* emitting outputs without performing intended computation;
* corrupting task inputs;
* exploiting verifier timing;
* manipulating memory used by evaluation;
* farming energy through repeated identical outputs;
* exploiting integer/resource accounting;
* task-response aliasing;
* gaining reward from partial outputs;
* reproducing before resource debit;
* checkpoint/restart duplication;
* migration-based duplication;
* evaluator leakage;
* resource cycling;
* sacrificing task function after reward but before reproduction.

Build automated exploit probes.

If an exploit is found:

* preserve the specimen;
* determine whether it invalidates affected runs;
* quarantine contaminated evidence;
* repair only if the problem is an instrumentation/physics bug;
* rerun only the affected independent lane if feasible within the total campaign window.

Do not erase exploit findings.

They are scientific evidence about the substrate.

⸻

LANE J — HISTORICAL SPECIMENS

Take representative historical organisms from the previous Bellerophon campaign and test them under the new physics.

Include:

* spontaneous replicators;
* sustained replicators;
* historical "beneficial-density" specimens;
* organisms whose copier damaged task code;
* representative failed organisms.

Ask:

* do historical replicators survive when copying must be financed?
* does task competence now matter?
* do previously harmful copy routines become selected against?
* can historical organisms adapt to the new coupling?

This lane is for mechanistic orientation, not for estimating fresh-origin frequency.

⸻

CAMPAIGN ADAPTATION WITHOUT HUMAN INPUT

The campaign may adapt within a frozen decision tree.

Allowed examples:

* allocate additional confirmatory runs when a preregistered trigger fires;
* run automatic causal ablation on a discovered candidate;
* perform transplant/replay when a structural detector fires;
* extend a lane to its preregistered maximum sample size if uncertainty remains above threshold;
* terminate a hopeless lane early when its preregistered futility criterion is met;
* redirect saved compute to other preregistered independent lanes.

Not allowed:

* invent new hypotheses after seeing results and pretend they were confirmatory;
* change pass thresholds;
* remove inconvenient controls;
* redefine the experimental unit;
* tune detectors to discovered specimens;
* stop the entire campaign to ask the operator what to do.

Exploratory follow-ups may run, but must remain labeled exploratory.

⸻

TIME AND RESOURCE POLICY

Total wall-clock target:

12–25 hours

The campaign should continue long enough to give independent lanes adequate power.

Prefer a design around approximately:

16–20 hours nominal

with:

* a lower bound around 12 hours if all preregistered precision targets are met early;
* a hard stop by 25 hours.

Do not waste time merely filling the clock.

Use preregistered sample/precision gates.

If some lanes finish early, allocate remaining budget according to the frozen allocation policy.

Keep sufficient fixed-allocation runs that adaptive promotion cannot destroy baseline-rate estimation.

⸻

PRIMARY OUTCOMES

Predeclare primary outcomes such as:

1. causal effect of correct computation on reproductive output;
2. descendant enrichment of task competence under coupling;
3. sustained heritability of task competence;
4. change in extinction/persistence caused specifically by contingent computation;
5. preservation of useful computation across reproduction;
6. emergence of reproductive architecture that improves retention of useful computation;
7. mechanistically independent origins of those changes.

Secondary outcomes may include:

* genome architecture;
* copying cost;
* mutation robustness;
* lineage depth;
* ecological effects;
* novel reproductive mechanisms;
* task-specific specialization.

⸻

REQUIRED CAUSAL TESTS FOR EXCITING FINDINGS

Any high-value phenomenon must automatically trigger at least one appropriate intervention:

* ablation;
* restoration;
* transplant;
* matched replay;
* task ON/OFF;
* coupling ON/OFF;
* shuffled verifier;
* equal-energy noncontingent control.

A detector alone cannot receive a causal verdict.

⸻

STATISTICAL DISCIPLINE

For each claim report:

* exact experimental unit;
* sample size;
* number of independent origins;
* effect size;
* uncertainty;
* denominator;
* exposure-normalized rate where applicable;
* paired analysis when pairing exists;
* family/lineage dependence;
* multiple-testing treatment;
* whether confirmatory or exploratory.

Do not turn:

* "not significant" into "no effect";
* large N of descendants into large independent N;
* detector frequency into causal evidence.

⸻

AUTOMATIC FAILURE HANDLING

If the new coupling completely fails:

Do not stop early unless all relevant preregistered falsification lanes have completed.

Determine whether failure is due to:

* resource accounting;
* lack of usable selection gradient;
* copier dominance;
* extinction;
* mutation destruction;
* task difficulty;
* reward timing;
* reward magnitude;
* representation mismatch;
* substrate chemistry.

Use preregistered diagnostic arms.

If one coupling parameterization fails but another parameterization was preregistered as a separate independent arm, continue to it.

Do not tune continuously based on results.

⸻

SUCCESS DOES NOT REQUIRE "INTELLIGENCE"

Do not define success as solving hard tasks.

A scientifically valuable success may be much earlier:

* computation measurably affects reproduction;
* that relationship is heritable;
* descendants become enriched for useful computation;
* selection begins preserving task code;
* reproductive machinery changes to reduce destruction of useful computation.

That would justify a later 2–3 day campaign.

Conversely, a flashy task solution without causal reproductive dependence is not success.

⸻

FINAL READINESS DECISION

At the end, make the decision autonomously.

Classify the substrate into one of these states:

READY_FOR_MULTIDAY

Evidence supports a real computation→resource→reproduction pathway and enough heritable adaptive signal exists to justify a multi-day campaign.

READY_WITH_RESTRICTED_SCOPE

The coupling works, but only particular tasks/substrates/regimes are grounded strongly enough for a long run.

REPHYSICS_REQUIRED

The coupling fails scientifically even though implementation works.

INSTRUMENT_REPAIR_REQUIRED

Measurement or implementation defects prevent scientific interpretation.

Do not ask the operator to choose the category.

Choose based on the frozen evidence rules and explain why.

⸻

IF READY_FOR_MULTIDAY

Produce a concrete next-campaign design targeting:

evolution of machinery that preserves, improves, or reorganizes computation because computation now finances reproduction

Prefer questions about:

* heritable computational capability;
* reproduction/computation co-adaptation;
* changes in reproductive machinery;
* preservation and modularization;
* evolving mutation/search geometry;
* ecological interactions among computational replicators;
* open-ended novelty.

Do not propose simply collecting more replication events.

⸻

REQUIRED OUTPUTS

Create a dedicated campaign directory under Bellerophon and commit compact, reviewable artifacts.

At minimum:

COUPLING_CAMPAIGN_PREREG.md

Frozen design, hashes, hypotheses, controls, decision tree, experimental units, sample allocations, stop rules.

COUPLING_IMPLEMENTATION_AUDIT.md

New physics, invariants, adversarial tests, accounting model.

COUPLING_CAMPAIGN_REPORT.md

Full confirmatory and exploratory results.

COUPLING_CAUSAL_LEDGER.jsonl

Every important candidate, intervention, replay, ablation, transplant, verdict.

COUPLING_ORIGIN_LEDGER.jsonl

Independent origins, ancestry, mechanism clustering.

COUPLING_FAILURE_LEDGER.md

Every implementation, scientific, exploit, or detector failure.

NEXT_MULTIDAY_CAMPAIGN.md

Only if readiness criteria are met.

STATUS.md

Final seat state and exact resume point.

Also retain machine-readable summaries and hashes of large runtime data without committing enormous campaign outputs unless repository policy permits.

⸻

FINAL REPORT

Return to the operator only when the campaign and analysis are complete.

The final response must begin with:

1. runtime;
2. total runs;
3. failures/voids;
4. control status;
5. reproducibility status;
6. readiness classification.

Then answer plainly:

* Did useful computation causally affect reproduction?
* Did descendants become more computationally competent?
* Was competence heritable?
* Did evolution begin protecting computation from reproductive damage?
* Did reproductive architecture change causally?
* Which effects replicated across tasks/substrates?
* Which candidate phenomena collapsed?
* What exploits or confounds appeared?
* What is the strongest surviving mechanism?
* Is a 2–3 day Bellerophon campaign now scientifically justified?
* If yes, what exactly should it search for?

Do not optimize the report for a positive result.

A clean negative result that tells us the required physics is still absent is a successful campaign.

FINAL OPERATING RULE

Once preregistration is frozen and the campaign starts:

No HITL. No operator questions. No requests for interpretation. No mid-run approval gates.

Run the full 12–25 hour autonomous program, execute the preregistered independent tests, perform automatic causal follow-ups permitted by the decision tree, finish the analysis, commit and push the evidence, and return only with the final scientific disposition.
