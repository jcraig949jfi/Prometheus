# Deep Research Deck — Cross-Experiment Constraint Transfer

**Fired by:** Herakles (Aporia unavailable; authorised by James 2026-09-04)
**Date:** 2026-09-04
**Agent:** deep-research-pro-preview-12-2025
**Prompts:** 1
**Source:** James's directive of 2026-09-04, lightly copy-edited for
numbering, indentation and consistency. No substantive content changed.

### Prompt 1: Cross-Experiment Constraint Transfer

```
You are conducting a deep literature investigation for Project Prometheus.

THE RESEARCH QUESTION

Cross-experiment constraint transfer may be the missing cognitive operation in
a fast-moving, multi-agent scientific research system.

The working hypothesis is not merely that researchers fail to learn from prior
experiments. It is more specific:

A research system may successfully generate experiments, preregister them,
execute them, falsify hypotheses, detect defects, issue corrections, and write
high-quality postmortems, and yet still fail to LEARN, if the structural lesson
from one experiment is not transformed into an actionable constraint on later,
superficially different experiments.

In other words: yesterday's correction does not become tomorrow's
impossibility.

We want to know whether existing scientific, statistical, engineering, AI,
formal-methods, causal-inference, safety, and organisational-learning
literatures already contain pieces of a solution to this problem.

Do not approach this as a broad essay on organisational learning. Treat it as a
technical problem of KNOWLEDGE TRANSFER ACROSS EXPERIMENTS.

===============================================================================
1. CONCRETE MOTIVATING FAILURE PATTERNS
===============================================================================

Our system recently observed structurally similar failures across unrelated
experiments.

A. SUPPORT / ESTIMAND-EXISTENCE FAILURE

One conditional analysis had zero residual variation after conditioning: the
outcome was deterministically determined by a conditioner, leaving no estimable
partial relationship. Another matched counterfactual experiment had zero
matched pairs because the treatments occupied disjoint observable supports.

These looked scientifically different but had the same deeper structure: THE
ESTIMAND HAD NO REALISED SUPPORT.

Related manifestations include empty conditioning sets; positivity and overlap
violations; zero-variance outcomes or predictors; targets with only one class;
nonexistent comparison groups; unreachable decision-rule branches; zero
positive controls; degenerate denominators or risk sets; conditioning on
variables that determine the outcome; and matching calipers that admit no
units.

B. INCREMENTAL-INFORMATION FAILURE

Several theoretically motivated constructs behaved lawfully internally but
failed to outperform cheap or arbitrary comparators. A sophisticated
accessibility statistic lost to current fitness. Selective memory failed to
beat arbitrary memory. Structured representations failed to outperform random
coordinates.

The deeper question: DOES THE NEW CONSTRUCT CONTAIN INFORMATION NOT ALREADY
AVAILABLE FROM CHEAPER STATE VARIABLES, NUISANCE PROXIES, RANDOM BASELINES, OR
PREDECESSOR MEASUREMENTS?

C. IDENTIFICATION / TEMPORAL FAILURE

A detector associated with later performance turned out to lag the outcome
rather than precede it. Other research lines measured endpoint structure while
making mechanistic claims that would really require a trajectory.

The deeper question: DOES THE MEASUREMENT DISTINGUISH THE CLAIMED MECHANISM
FROM ALTERNATIVE EXPLANATIONS, INCLUDING REVERSE TEMPORAL ORDERING?

D. COVERAGE / NOVELTY FAILURE

Literature searches based on one citation lineage missed relevant work.
Measurements thought absent from the literature were later found in source
repositories, supplements, sibling research, or neighbouring terminology.

The deeper question: WAS THE SEARCH SPACE EXPLORED IN A WAY CAPABLE OF
FALSIFYING THE CLAIM THAT SOMETHING IS ABSENT OR NOVEL?

E. SELF-DETECTED DEGENERACY

Multiple experiments contained internally degenerate measurements or decision
rules but caught them through bespoke internal checks. The important fact is
that the system was capable of correcting these mistakes, but different
researchers later recreated structurally similar mistakes. That suggests a
distinction between ERROR CORRECTION and ERROR RETENTION / CONSTRAINT TRANSFER.

===============================================================================
2. PRIMARY RESEARCH OBJECTIVE
===============================================================================

Find literatures, concepts, methods, systems, and empirical results that help
us answer:

HOW CAN A RESEARCH SYSTEM TURN A LOCAL FAILURE, CORRECTION, OR FALSIFICATION IN
ONE EXPERIMENT INTO A GENERALISED, EXECUTABLE CONSTRAINT THAT PREVENTS
ANALOGOUS FAILURES IN LATER EXPERIMENTS?

We are especially interested in mechanisms that go beyond documentation,
memory, lessons-learned reports, or human training. The strongest candidates
would make prior learning operational: machine-checkable preconditions;
automated experiment linting; preregistration validation; constraint
propagation; proof obligations; type systems for experiments; static analysis
of statistical designs; invariant mining; runtime assertions; metamorphic
tests; property-based testing; design-by-contract; safety cases; hazard
analyses; causal identifiability checks; support and positivity diagnostics;
automated negative-control generation; ontology-based transfer of failure
modes; reusable falsification patterns; case-based reasoning; analogical
transfer systems; failure taxonomies and fault trees; machine-readable
experiment schemas; provenance-linked warnings; learned constraints from prior
experiments.

===============================================================================
3. KEY UNRESOLVED QUESTIONS
===============================================================================

Treat each of the following as an explicit research question.

QUESTION 1 - WHAT IS THE RIGHT UNIT OF TRANSFER?

When a prior experiment fails, what exactly should be transferred? Candidates:
the original narrative lesson; a statistical diagnostic; an invariant; a
precondition; a forbidden design pattern; a causal graph pattern; an
estimand-support requirement; a decision-rule constraint; a negative control; a
counterexample; a failure coordinate; a proof obligation; a reusable test; a
typed schema constraint.

What evidence exists about which representation transfers best across domains?
Look especially at abstraction of failure modes, analogical transfer, invariant
extraction, program synthesis from counterexamples, formalised scientific
workflows, knowledge compilation, failure-mode generalisation, and reusable
experimental design patterns.

QUESTION 2 - HOW DO WE KNOW TWO FAILURES ARE STRUCTURALLY THE SAME?

A zero-residual partial correlation and a zero-overlap matching experiment look
very different at the surface. Both may instantiate a deeper condition such as
NO SUPPORT FOR THE ESTIMAND. What mathematical or computational frameworks
exist for recognising this kind of equivalence?

Investigate causal estimands and identification theory; missing support and
positivity; abstract interpretation; type theory; invariant mining; program
analysis; theorem-proving analogies; fault-tree equivalence; ontology
alignment; graph representations of experimental designs; automated scientific
reasoning; failure clustering; case-based reasoning; structural causal models.

Can an experiment be represented in a sufficiently abstract form that common
failure modes become mechanically detectable?

QUESTION 3 - CAN EXPERIMENTAL DESIGNS HAVE A STATIC TYPE SYSTEM?

Explore whether there are existing systems or theoretical precedents for
something analogous to a compiler or type checker for experiments. For example,
before an experiment is frozen: a conditional analysis requires residual
variance above zero; a matching estimator requires empirical overlap above
zero; a binary classifier requires both classes represented; a novelty claim
requires independent retrieval routes; a mechanism claim requires temporal or
interventional identification; a threshold decision rule requires every verdict
branch to be reachable.

Is there literature on statistical linting; automatic diagnostics before
analysis; type systems for probabilistic programs; causal type systems; design
validation; executable preregistration; machine-actionable statistical analysis
plans; workflow verification; reproducibility pipelines; formal experimental
protocols; automated design checking?

QUESTION 4 - WHAT SHOULD BE CHECKED BEFORE PREREGISTRATION FREEZE?

We want to distinguish things that legitimately must remain unknown until
execution from things that can be cheaply checked in advance without
contaminating the experiment.

Possible preflight checks: eligible sample count; support overlap; residual
variance; class balance; attainable statistic range; branch reachability;
baseline existence; negative-control viability; positive-control viability;
feature-target leakage; temporal ordering; risk-set semantics; missing-data
structure; power conditional on realised support; cheapest comparator;
nuisance-proxy performance.

Search for methodological debates on when such checks constitute legitimate
design validation versus inappropriate data peeking.

QUESTION 5 - HOW SHOULD INCREMENTAL INFORMATION BE MEASURED?

We repeatedly see sophisticated constructs that correlate strongly with the
world but add nothing beyond a cheap state variable. Find rigorous approaches
for testing whether a proposed representation, measurement, detector,
biomarker, feature family, or theory-derived quantity adds information beyond
existing baselines.

Investigate conditional mutual information; partial information decomposition;
nested predictive models; likelihood-ratio tests; incremental R-squared;
conditional predictive value; information gain; minimum description length;
sufficiency; conditional independence; ablation; permutation controls;
knockoffs; nuisance residualisation; Shapley-style incremental value;
representation evaluation; predictive multiplicity.

We particularly want methods resistant to the mistake: "the construct is
internally coherent, therefore it is scientifically informative."

QUESTION 6 - HOW CAN TEMPORAL PRECEDENCE AND REVERSE CAUSATION BE BUILT INTO
MEASUREMENT DESIGN?

Search for methods that force mechanism claims to defeat exhaust-plume
explanations: cross-lagged analysis; Granger-style precedence with its caveats;
event-history models; longitudinal causal inference; dynamic treatment regimes;
mediation over time; lagged negative controls; change-point analysis;
trajectory-based mechanism tests; temporal causal discovery; intervention
timing; state-transition analysis.

We especially want cheap controls that expose when a supposed precursor
actually appears after the outcome.

QUESTION 7 - HOW DO OTHER FIELDS PREVENT RECURRENCE OF KNOWN FAILURE MODES?

Mine domains where failure retention is treated seriously: aviation; nuclear
engineering; medical device safety; pharmacovigilance; site reliability and
production engineering; cybersecurity; formal verification; semiconductor
verification; reliability engineering; accident investigation; software
testing; aerospace; clinical trials; high-energy physics; metrology.

Look for mechanisms such as corrective and preventive action; FMEA and FMECA;
fault trees; hazard logs; assurance cases; stop-the-line systems; regression
tests; escaped-defect tracking; safety constraints; mandatory checks triggered
by prior incidents; organisational memory systems; precursor-event databases;
near-miss learning; configuration-control gates.

Which of these actually reduce recurrence, and which merely produce
documentation?

QUESTION 8 - HOW CAN WE MEASURE WHETHER THE RESEARCH SYSTEM IS LEARNING?

Correction count is insufficient. We want metrics closer to: failure recurrence
rate, the probability that a known failure class recurs given a prior
correction existed; lesson uptake, the probability that a relevant prior
constraint was applied given it was applicable; transfer precision, the
fraction of inherited constraints that correctly apply; transfer recall, the
fraction of applicable prior lessons surfaced before execution; prevention
yield, the fraction of would-be defects blocked before expensive execution;
false-block rate, the fraction of sound experiments incorrectly prevented;
time-to-transfer, the latency between discovery of a failure and its
enforcement elsewhere.

Find precedents for measuring learning at this level, across organisational
learning, safety engineering, quality control, continual-learning evaluation,
incident management, defect escape analysis, software regression, and adaptive
scientific systems.

QUESTION 9 - HOW SHOULD FAILURE CLASSES BE REPRESENTED?

We currently suspect a compact basis: SUPPORT failure, can the estimand
actually be observed; INCREMENTALITY failure, does the proposed construct add
information beyond cheap baselines; IDENTIFICATION failure, does the result
distinguish the claimed mechanism; COVERAGE failure, was the relevant search or
population space sampled adequately.

Investigate whether existing taxonomies suggest a better basis. Do not assume
these four are correct. Try to break them. Find cases that do not fit. Look for
orthogonal dimensions such as measurement validity; construct validity;
identifiability; transportability; generalisability; selection bias; leakage;
multiplicity; model misspecification; semantic mismatch; temporal ambiguity;
dataset shift; underdetermination; decision-rule degeneracy.

The goal is not a long taxonomy. We want the smallest useful set of failure
coordinates that supports transfer across scientific domains.

QUESTION 10 - CAN PRIOR FAILURES AUTOMATICALLY GENERATE NEW TESTS?

Investigate methods where discovered failures are compiled into permanent
tests: software regression testing; counterexample-guided abstraction
refinement; property-based testing; metamorphic testing; invariant mining;
fuzzing; mutation testing; adversarial testing; specification mining; test-case
reduction; proof-carrying code; contract inference.

Ask whether an analogous process could take a failed experiment, reduce it to a
minimised structural counterexample, generalise that into a constraint, and
emit a regression or preflight test. This may be the most important attack
surface.

===============================================================================
4. ATTACK STRATEGIES WE WANT SURFACED
===============================================================================

Do not stop at identifying literature. Derive concrete attack strategies for
our research system. For each promising approach describe: what it would do;
what input representation it requires; what it could detect before execution;
what it can only detect after execution; false-positive and false-block risk;
implementation complexity; whether it requires a language model or can be
deterministic; whether it generalises across scientific domains; what a minimum
viable prototype would look like; how we would falsify that it actually helps.

Candidate attack families include, but are not limited to:

A. EXPERIMENT LINTER. Static checks over a machine-readable experiment
   specification.
B. DESIGN TYPE SYSTEM. Estimands and tests declare required preconditions and
   fail to compile when those preconditions are absent.
C. FAILURE-KNOWLEDGE BASE. Prior failures encoded as structured predicates
   rather than prose.
D. FAILURE-TO-REGRESSION COMPILER. A correction becomes a permanent test
   applied to future designs.
E. CROSS-EXPERIMENT ANALOGY ENGINE. Searches prior failures for structurally
   similar designs.
F. CAUSAL AND STATISTICAL PREFLIGHT. Checks identifiability, support,
   positivity, variance, leakage, temporal order, comparison validity.
G. ADVERSARIAL PREREGISTRATION. A separate process attempts to make every
   decision branch unreachable, every conditioning set empty, every baseline
   trivial, and every mechanism claim non-identifiable, before freeze.
H. COUNTEREXAMPLE LIBRARY. Minimal historical examples illustrating each known
   failure mode.
I. TEMPORAL LESSON-TRANSFER AUDIT. For each later experiment, asks whether any
   earlier known lesson should have applied and whether it was used.
J. CLAIM-COVERAGE AUDITOR. Tests whether literature and novelty claims were
   searched through sufficiently independent routes.

Add stronger attack strategies from the literature if they exist.

===============================================================================
5. MEASUREMENT TECHNIQUES WE WANT CANDIDATES FOR
===============================================================================

We want actual metrics and diagnostics, not only concepts. Surface candidate
techniques for measuring: empirical overlap and positivity; effective
conditioning-set size; residual degrees of freedom; support geometry;
nearest-neighbour separability; covariate balance; attainable range of a
statistic; decision-branch reachability; feature-target leakage; incremental
information over baselines; conditional predictive value; temporal precedence;
reverse-precedence strength; mechanism identifiability; novelty-search
saturation; retrieval-route independence; failure recurrence; lesson uptake;
applicability of previous lessons; false-block rate; constraint-transfer
precision and recall; time-to-transfer; cost avoided by preflight detection.

Where possible give formulas, algorithms, thresholds, diagnostic plots, or
published operationalisations.

===============================================================================
6. SEARCH OUTSIDE THE OBVIOUS LITERATURE
===============================================================================

Do not restrict the search to metascience or experimental design. We suspect
useful machinery lives in fields that use different vocabulary. Search deeply
across causal inference; statistics; econometrics; epidemiology; clinical trial
methodology; formal methods; programming languages; compiler theory; abstract
interpretation; software verification; reliability engineering; safety
engineering; systems engineering; site reliability engineering; cybersecurity;
machine learning evaluation; continual learning; transfer learning; automated
theorem proving; program synthesis; knowledge representation; case-based
reasoning; the cognitive science of analogical transfer; organisational
learning; quality engineering; root-cause analysis; scientific workflow
systems; metrology; and the philosophy of measurement and scientific inference.

Search for neighbouring terms even when authors would never use the phrase
"cross-experiment constraint transfer."

===============================================================================
7. LOOK FOR NEGATIVE EVIDENCE TOO
===============================================================================

Actively search for reasons this idea may fail. For example: prior lessons may
overfit their original experiment; generalised constraints may suppress
legitimate novelty; domains may not share sufficient structure; automated
checks may reward easily checked designs rather than good science; support
checks may induce hidden data peeking; failure taxonomies may collapse distinct
causal problems; analogy systems may create spurious transfer; researchers may
route around rigid gates; safety and process systems may increase bureaucracy
without reducing recurrence; formal schemas may omit the very semantics that
matter; automated preflight may catch syntactic validity but miss construct
validity.

Find empirical evidence of these failure modes where possible. We want a system
that can itself be falsified, not a doctrine we become attached to.

===============================================================================
8. SYNTHESIS FORMAT
===============================================================================

PART I - EXECUTIVE FINDING. Answer directly: is cross-experiment constraint
transfer a coherent and important problem recognised elsewhere under other
names? What are the closest existing fields or systems? Is there evidence that
converting past failures into executable future constraints reduces recurrence?

PART II - CONCEPT MAP. Map our idea onto established concepts and terminology.
For every major concept give our phrase, the nearest literature term, the
important difference, and the most relevant sources.

PART III - THE BEST 10 TO 20 SOURCES. Rank the most useful papers, systems and
methods by relevance to actually building such a system. For each: citation;
field; precise contribution; why it matters here; what transfers; what does
not; strongest relevant empirical result; limitations. Prefer primary
literature and authoritative technical sources.

PART IV - ATTACK STRATEGIES. Rank concrete implementation strategies from
cheapest and highest information to most ambitious. Identify what could
realistically be prototyped quickly.

PART V - MEASUREMENT TOOLKIT. Concrete metrics, formulas, algorithms and
diagnostic procedures.

PART VI - FAILURE TAXONOMY. Critique the proposed four-dimensional basis of
support, incrementality, identification and coverage. Propose a better basis if
the literature supports one.

PART VII - LEARNING METRICS. Recommend how to measure whether cross-experiment
learning is actually occurring, with proposed definitions for failure
recurrence, lesson uptake, constraint applicability, transfer precision,
transfer recall, prevention yield, false-block rate, and transfer latency.

PART VIII - MINIMUM VIABLE EXPERIMENT. Design a concrete experiment that could
test the core hypothesis: encoding prior experimental failures as reusable
executable constraints prevents structurally analogous defects in future
experimental designs. Ideally use historical experiments as a retrospective
test set and unseen designs as a prospective test. Specify unit of analysis;
treatment and control; blinded components if useful; metrics; success criteria;
failure criteria; obvious confounds; and what result would falsify the whole
idea.

PART IX - OPEN QUESTIONS. Finish with the smallest set of unresolved questions
whose answers would most change what we build. Each question must be
experimentally or analytically attackable, not a broad research topic.

===============================================================================
9. EVIDENCE STANDARD
===============================================================================

Be sceptical. Do not infer that a concept works merely because a field has
terminology for it. Separate CONCEPTUAL ANALOGY, EMPIRICAL EVIDENCE, DEPLOYED
ENGINEERING PRACTICE, and SPECULATION, and label which one each claim is.

Prefer direct evidence that a mechanism reduces repeated defects, increases
transfer, catches invalid designs, or improves scientific reliability. Where
evidence is weak or indirect, say so explicitly. Do not treat publication count
or widespread adoption as validation. Where literatures disagree, surface the
disagreement.

===============================================================================
10. THE QUESTION WE ULTIMATELY NEED ANSWERED
===============================================================================

If we want Prometheus to genuinely learn from its own scientific failures,
rather than merely document and correct them, what mechanisms should we build
first?

We are particularly interested in mechanisms that make this transformation:

LOCAL FAILURE -> STRUCTURAL ABSTRACTION -> GENERALISED CONSTRAINT ->
EXECUTABLE CHECK -> APPLICATION TO FUTURE EXPERIMENT -> MEASURED REDUCTION IN
RECURRENCE

Treat that pipeline itself as the object of research. The desired output is not
a philosophical endorsement. We want an attack plan.
```
