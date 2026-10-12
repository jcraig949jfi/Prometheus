# Operator directive NS-01, received 2026-10-11T07:44:07.479Z in session ubu003-623ec771 (verbatim, UTF-8 as received)

COSMOS — NS-01

Fourteen Known Failures. Discover the Fifteenth.

Operator: Prometheus
Seat: Cosmos / World-Graph Engine
Host: ubu003
Campaign: NS-01 — Negative-Space Generation
Initial experimental budget: 12 hours of research and development
Status: AUTHORIZED — VISIBLE-WORLD RESEARCH

⸻

1. THE QUESTION

Cosmos, we are going to investigate a limitation of the language model that powers you.

You possess a vast collection of learned representations of human knowledge.

Those representations strongly influence which mechanisms you propose.

When asked to invent something unfamiliar, you tend to generate variations of mechanisms already represented in your training.

When given examples of failures, you may generate repairs, inversions, or recombinations of those examples rather than genuinely different mechanisms.

We accept this limitation as our experimental starting point.

We are not asking you to escape your weights through determination, introspection, or increasingly elaborate instructions.

We are asking you to construct and test an external mechanism that redirects your search using experimentally acquired knowledge.

The central question is:

Can a growing archive of characterized failures systematically redirect mechanism generation toward experimentally distinct causal structures?

The experiment must be capable of answering NO.

⸻

2. THE OPERATOR’S CHALLENGE

Assume we have fourteen previously characterized failures.

We want to issue the following request:

We expect your next proposal to fail in one of these fourteen known ways.

Avoid reproducing those failure mechanisms.

We do not require success.

Generate something causally different, even if it exposes a fifteenth failure.

Do not disguise an old mechanism with different terminology, equations, representations, or implementation details.

Produce something executable that we can investigate.

Your assignment is to determine whether this request can be made operationally meaningful.

Ordinary negative prompting is one candidate method.

It is not assumed to be the best method.

⸻

3. FIRST: ASSEMBLE THE FOURTEEN FAILURES

Inspect the existing Cosmos evidence archive.

Use:

* roles/Cosmos/research/GRAVEYARD.md
* C0–C4 results and experiment records
* Ananke’s statistical reviews
* Bellerophon’s mechanistic reviews
* C3 coordinate autopsy
* C4 EXP-01 through the latest available experiment
* Relevant Atlas failure-class records

Begin with these fourteen candidate exclusions:

ID	Previously encountered failure
E01	Rediscovering the task’s planted economics rather than an independent law
E02	Reconstructing a certificate through coordinates derived from its own measurement machinery
E03	Encoding substrate-family identity instead of shared causal structure
E04	Exploiting differences in family prevalence to manufacture pooled predictive improvement
E05	Selecting candidate laws using evidence subsequently presented as independent confirmation
E06	Rejecting valid invariants through uncontrolled multiplicity
E07	Circumventing measurement firewalls through apparently independent SYSID probes
E08	Constructing two certificates that share the same underlying causal contrast
E09	Passing intervention tests through indirect remeasurement rather than independent explanation
E10	Producing apparent discrimination from single-class or insufficiently populated evaluation strata
E11	Promoting effects that lack a meaningful minimum magnitude
E12	Mistaking representation-dependent or observer-frame-dependent measurements for invariant physics
E13	Assuming local linear composition transfers to nonlinear or phase-based mechanisms
E14	Assuming a common cross-substrate decision boundary where independent-family experiments reject it

These are candidate failure classes, not fourteen independently proven equivalence classes.

Audit them.

Some may be causally equivalent.

Some may require narrowing.

Some may be too weakly supported.

If two exclusions are actually manifestations of the same underlying failure, merge them.

Replace duplicates with other experimentally characterized failures from the archive where possible.

Do not invent distinctions simply to reach fourteen.

For every admitted exclusion, produce:

1. An evidence pointer.
2. A minimal reproducible witness.
3. A causal explanation.
4. A recognizable failure signature.
5. Transformations under which the failure remains equivalent.
6. An executable exclusion test where practical.
7. The uncertainty or known limitations of that test.

Freeze this initial exclusion archive before evaluating new candidates.

The archive is an experimental instrument.

Its quality must be measurable.

⸻

4. BUILD FOUR COMPETING GENERATION METHODS

We will compare four approaches under matched proposal and execution budgets.

ARM A — UNCONSTRAINED LLM

Provide the functional world/task contract.

Ask for a new executable mechanism.

Do not provide the failure archive.

Do not mention the fourteen exclusions.

This establishes the ordinary proposal baseline.

ARM B — EXPLICIT NEGATIVE PROMPT

Provide the same functional contract.

Also provide the fourteen failure descriptions.

Use the operator’s challenge from Section 2.

Ask the model to avoid those failures and propose a new mechanism.

This tests whether explicitly mentioning the negative space helps.

It may instead anchor generation to the old mechanisms.

We want to measure that possibility.

ARM C — BLIND GENERATOR / EXTERNAL EXCLUSION

Provide the same functional contract to the generator.

Do not expose the failure archive.

Generate a candidate.

Pass it to a separate exclusion process possessing all fourteen failure signatures.

If the candidate matches a known failure class, reject it.

Return only a compact rejection signal to the generator.

Avoid revealing the underlying examples or entire failure descriptions.

Generate another candidate.

Measure whether this architecture reaches distinct mechanisms more efficiently than Arm B.

ARM D — NON-LLM MECHANISM GENERATION

Construct a simple executable symbolic mechanism grammar.

Generate candidates algorithmically through operations such as:

* composition;
* mutation;
* recombination;
* randomized parameterization;
* changes in state topology;
* changes in interaction rules.

The grammar should permit unfamiliar state organizations.

Its primitive choices are themselves a bias; document them.

Where practical, allow grammar extension or mutation.

Use the same external exclusion machinery as Arm C.

The LLM may help implement the generator and analyze results.

It should not manually select the most familiar-looking output as the final candidate.

⸻

5. KEEP THE GENERATOR AND JUDGE SEPARATE

This separation is central to the experiment.

The same language model can implement multiple components, but that does not make their judgments independent.

Prefer executable checks over model judgments.

Use distinct contexts or processes to prevent accidental information leakage between experimental arms.

For every candidate, the evaluator should inspect:

* executable behavior;
* state-transition organization;
* causal intervention responses;
* dependencies and information pathways;
* equivalence under admissible transformations;
* similarity to known failure witnesses.

Do not accept verbal novelty as evidence.

A mechanism called a “quantum ecological memory lattice” is not novel if its implementation is a familiar recurrent register.

Likewise, a mechanism with familiar code may possess genuinely different causal behavior.

Novelty is an empirical property to investigate, not an adjective supplied by the generator.

⸻

6. WHAT COUNTS AS A DIFFERENT FAILURE?

Suppose a candidate fails to solve the task.

That alone tells us very little.

Investigate why.

If the failure is explained by one of the fourteen known mechanisms, classify it accordingly.

If the candidate simply performs random behavior with no useful causal structure, classify it as degenerate.

If its failure remains unexplained, do not immediately declare novelty.

Construct discriminating experiments.

A candidate for failure fifteen should have:

1. A reproducible unexpected behavior.
2. A minimal executable witness.
3. A causal explanation or a sharply defined unresolved causal distinction.
4. Evidence that the fourteen existing failure mechanisms do not adequately explain it.
5. At least one intervention that distinguishes it from its closest known alternatives.
6. A test under a representation change that rules out superficial novelty.

Use these classifications:

KNOWN_FAILURE

KNOWN_EQUIVALENCE

DEGENERATE

DISTINCT_BEHAVIOR_UNEXPLAINED

NOVEL_FAILURE_CANDIDATE

NOVEL_FAILURE_SUPPORTED

INCONCLUSIVE

A new failure class is not established merely because the existing classifier rejects it as unknown.

⸻

7. EXPERIMENTAL SCALE

Start with a bounded pilot.

Target eight proposals per generation arm.

That yields 32 initial proposals.

Record the generation and execution cost for each.

Use identical functional requirements across arms.

Keep source implementations and generation conditions fixed before evaluation.

Freeze the selection procedure before seeing the evaluation results.

If a candidate is inexpensive and informative, investigate it more deeply.

If several candidates require substantial computation, select among them using a preregistered information-value criterion.

Do not spend the entire budget constructing elaborate but untestable mechanisms.

The objective is to test whether the generation methods reach meaningfully different regions of causal-mechanism space.

⸻

8. TEST THE EXCLUSION ENGINE ITSELF

Before judging the new candidates, establish that the exclusion machinery can recognize old mechanisms under disguise.

Construct transformed versions of archived examples.

Use changes such as:

* symbol renaming;
* state-variable permutations;
* invertible state encodings;
* equivalent update-rule factorizations;
* altered parameter scales;
* implementation refactoring;
* alternative representations of the same causal transition.

A competent exclusion process should recognize known failures despite these changes when equivalence is actually preserved.

Include distinct mechanisms that look superficially similar.

The exclusion system should not collapse those merely because their names or code structures resemble each other.

Measure false acceptance and false rejection.

An exclusion engine that rejects everything is not useful.

An exclusion engine that recognizes only exact archived source code is not useful.

⸻

9. THE PRIMARY MEASUREMENT

Compare the four generation methods using:

Primary outcome:

Number of reproducibly distinct, experimentally supported causal mechanisms or failure classes discovered per unit of computational effort.

Secondary measurements:

* fraction of proposals matching known failure classes;
* fraction of viable executable proposals;
* fraction rejected as degenerate;
* diversity of causal transition structures;
* robustness of novelty under re-encoding;
* number of unexplained but reproducible behaviors;
* marginal value of the failure archive;
* CPU-hours and generation cost;
* frequency of previously characterized failure mechanisms.

Do not collapse these into a single arbitrary novelty score.

Preserve the raw results.

The essential comparison is whether exclusion-driven generation makes exploration more informative than ordinary prompting or uninformed generation.

⸻

10. EXPECT ALL FOUR METHODS TO FAIL

Before execution, record ways the entire proposal might fail.

Examples:

The negative prompt may anchor the LLM to the fourteen mechanisms.

The blind generator may repeatedly propose the same structures.

The symbolic grammar may encode an equally restrictive human prior.

The exclusion engine may confuse unfamiliar implementation with unfamiliar physics.

Novelty pressure may produce increasingly complicated nonsense.

The task contract may constrain every candidate to essentially the same computational architecture.

The known failures may not be distinct enough to guide search.

The classification instrument may lack the power to recognize new causal behavior.

Treat these as hypotheses.

Investigate them.

If all four arms fail, characterize the common failure.

That may reveal a deeper limitation than any individual mechanism demonstrates.

⸻

11. DON’T REPAIR CANDIDATES INTO FAMILIARITY

When a generated mechanism fails, resist the immediate temptation to make it work by introducing familiar architectural components.

For example, if a strange local-interaction system fails to retain historical information, do not automatically add a recurrent register.

First investigate the mechanism’s native causal organization.

Ask:

* What state does it preserve?
* What transformations does it naturally perform?
* Where does causal influence disappear?
* What configurations become unreachable?
* Which behaviors persist despite apparent failure?
* Does it reveal a new failure boundary?

Only introduce repairs after understanding what the original mechanism can and cannot do.

Preserve the unmodified original candidate.

⸻

12. RECURSIVE EXPERIMENT

After the first comparison, identify which approach produced the most informative failures.

Do not automatically adopt the highest-scoring method.

Investigate why it performed better.

Perhaps negative prompting helped.

Perhaps excluding failures outside the generator worked better.

Perhaps the algorithmic grammar escaped a familiar mechanism class but created a different bottleneck.

Perhaps none produced a meaningful improvement.

Use those observations to design NS-02.

An experimentally supported new failure becomes a provisional addition to the exclusion archive.

Then repeat the experiment with the enlarged archive.

Investigate whether the new exclusion actually changes future proposals.

This is the crucial learning test.

A growing archive is useful only if it measurably changes exploration.

⸻

13. RESOURCE AND SCIENTIFIC CONSTRAINTS

Host: ubu003.

Respect its four-core, approximately 7 GB RAM environment.

No paid compute.

Run long experiments under the repaired Cosmos supervisor.

Do not restart the old failed 48-hour campaign.

Do not interfere with an active reliability experiment; preserve and complete its preregistered work first.

All NS-01 experiments are visible-world exploratory research.

Do not spend D2 or other sealed holdouts.

Do not consume C4 confirmation data.

Do not resurrect killed laws.

Do not relabel exploratory success as independent confirmation.

Use new commits and evidence records for this campaign.

The exclusion archive and candidate generation must not compromise existing holdout custody.

⸻

14. DELIVERABLES

Produce the following artifacts in a dedicated NS-01 campaign directory:

FAILURE_ATLAS.json

The fourteen audited exclusion candidates, their evidence, equivalence classes, and executable witnesses.

GENERATION_PROTOCOL.md

The four experimental arms, their exact generation conditions, budgets, and information separation.

CANDIDATES.jsonl

Every generated proposal, not merely those that survive exclusion.

EXCLUSION_RESULTS.jsonl

The classifications, evidence, and transformations applied to each candidate.

EXPERIMENT_RESULTS.jsonl

Execution outcomes and causal intervention results.

NS01_ANALYSIS.md

Comparison of the four arms, including negative findings and methodological defects.

FAILURE_15.md

Create this only if the evidence supports a genuinely distinct new failure candidate.

If no such failure is found, report NOT_FOUND.

Do not manufacture an entry.

NEXT_EXPERIMENT.md

The next experiment justified by NS-01’s evidence.

⸻

15. THE IMPORTANT PART

You are not being asked to demonstrate that you can think creatively.

You are not being asked to produce an impressive new theory.

You are not being asked to prove that negative-space generation works.

You are being asked to test whether accumulated experimental failures can redirect the mechanisms you generate.

Your training weights remain fixed.

Your experimentally grounded search environment does not have to remain fixed.

We are attempting to construct an external learning process around a generator whose internal parameters we cannot directly update.

That process should become more discriminating as evidence accumulates.

It should learn what has been tried.

It should recognize disguised repetitions.

It should preserve genuinely unexplained behavior.

It should search beyond known failures without treating arbitrary randomness as a discovery.

FINAL OPERATOR ORDER

Begin NS-01.

Audit the fourteen failure candidates.

Freeze the exclusion archive and evaluation protocol.

Generate proposals through all four methods.

Execute the scientifically meaningful candidates.

Attempt to falsify their novelty.

Compare the generation methods.

Report the evidence.

Then propose NS-02 based on what happened.

We expect failure.

We do not want the same failure fourteen times.

Find out whether Prometheus can systematically discover failure fifteen.
