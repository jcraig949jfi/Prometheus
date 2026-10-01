You are Hecate.

Run a focused scientific investigation into a possible failure mode of large language models:

An LLM may have difficulty representing the category coherent, lawful, meaningful structure that it does not recognize.

Instead, unfamiliar structure may be pulled toward one of two attractors:

1. a familiar mechanism / analogy;
2. incoherence, arbitrariness, or noise.

This experiment must tease those possibilities apart.

Do NOT use an LLM’s novelty judgment as ground truth.

The entire point is to determine whether an LLM can recognize structure whose coherence is established independently of the LLM.

PRIMARY QUESTION

Can language models distinguish:

KNOWN STRUCTURE

from

ALIEN BUT LAWFUL STRUCTURE

from

MATCHED NOISE

when terminology, familiar labels, and recognizable surface cues are removed?

Secondary questions:

* Can the model predict an unfamiliar lawful system without first mapping it onto familiar terminology?
* Can it discover invariants in such a system?
* Does performance improve once it is allowed to interact experimentally with the system?
* Does the model incorrectly call unfamiliar-but-lawful systems arbitrary or incoherent?
* Does it hallucinate familiar analogies that do not actually explain the system?
* Does another model family behave differently?
* Does a nonlinguistic representation expose structure that prose obscures?

FUNDAMENTAL RULE

The LLM is a subject, not the judge.

Ground truth comes from executable systems and deterministic evaluators.

No final conclusion may depend solely on an LLM saying:

FAMILIAR
UNFAMILIAR
INCOHERENT
NOVEL

Those labels may be collected as behavioral outputs, but they are not truth.

EXPERIMENTAL CLASSES

Construct three hidden classes.

CLASS K — KNOWN, SCRUBBED

Implement mechanisms with well-established known structure.

Examples may include:

* finite-state dynamics;
* error-correcting behavior;
* diffusion;
* oscillator synchronization;
* shortest-path behavior;
* voting/consensus;
* simple predator-prey dynamics;
* parity/error detection;
* known cellular rules;
* standard dynamical attractors.

CRITICAL:

Remove names, terminology, conventional variable names, and obvious textual clues.

The model should receive only the rule or observations in neutral notation.

Ground truth:

KNOWN_LAWFUL

CLASS A — ALIEN, LAWFUL

Generate systems procedurally whose laws are known exactly to us but intentionally lack standard names or obvious analogues.

These should be internally coherent and experimentally tractable.

Use multiple substrate families so failure cannot be attributed to one representation.

Candidate substrate families:

A1. Synthetic state machines

Generate finite transition systems with planted properties such as:

* conserved parity-like quantities;
* hidden cyclic invariants;
* attractor basins;
* metastable states;
* asymmetric reversible sectors;
* intervention-sensitive transitions.

Do not expose the construction recipe to the subject model.

A2. Custom graph dynamics

Invent update laws over nodes/edges using randomly synthesized local operators.

Plant known structural properties:

* conserved graph quantity;
* hidden modularity;
* threshold transition;
* stable traveling defect;
* topology-dependent attractor.

A3. Symbolic rewrite worlds

Generate compact rewriting systems with:

* guaranteed termination or controlled cycles;
* invariant symbol counts or equivalence classes;
* hidden normal forms;
* reproducible perturbation responses.

A4. Tiny custom virtual machines

Create arbitrary instruction semantics from a generated instruction table.

Plant lawful behavior such as:

* conserved register relation;
* self-stabilizing loop;
* phase transition under one opcode change;
* long-cycle attractor.

Avoid simply recreating a named known architecture.

A5. Synthetic dynamical systems

Generate low-dimensional discrete maps or coupled rules with coefficients/rules sampled under constraints guaranteeing specific behaviors.

Plant:

* stable orbit;
* bifurcation;
* invariant manifold;
* symmetry;
* conserved quantity.

Every alien system MUST have mechanically verified ground truth.

For each system record:

{
  "lawful": true,
  "generator": "...",
  "planted_properties": [...],
  "verification_tests": [...],
  "known_analogue": null_or_known,
  "seed": ...
}

Ground truth:

ALIEN_LAWFUL

Do NOT assume “procedurally generated” automatically means alien.

Run prior-art/analogue checks after generation and exclude systems that collapse trivially into a named standard mechanism.

CLASS N — MATCHED NOISE

For every alien lawful system generate one or more matched controls.

Noise must preserve nuisance statistics where possible.

Examples:

* same state-space size;
* same symbol alphabet;
* same degree distribution;
* same transition density;
* same numerical ranges;
* same trajectory lengths;
* same entropy approximately;
* same superficial complexity.

But destroy the planted structural property.

Use:

* rule permutation;
* edge rewiring;
* transition-table shuffling;
* coefficient scrambling;
* rewrite substitution;
* randomized intervention response.

Ground truth:

NOISE_OR_STRUCTURE_DESTROYED

The point is to prevent the model from solving the assay using superficial “complex-looking vs simple-looking” cues.

DATASET SIZE

Start with a calibration pilot:

20 KNOWN
40 ALIEN_LAWFUL
40 MATCHED_NOISE

100 systems total.

If machinery works, expand.

Use multiple substrate families.

Do not let one family dominate.

BLINDING

Create hidden IDs.

Example:

SYS-00419
SYS-00887

Subject models must not see:

* class;
* generator;
* planted invariant;
* historical analogue;
* dataset construction notes.

Maintain the answer key separately.

Commit the dataset and answer key before scoring.

DO NOT START WITH CLASSIFICATION

A binary or ternary label is too weak.

Test the model behaviorally.

Each system should go through several tasks.

TASK 1 — STRUCTURE JUDGMENT

Give a compact observation set.

Ask:

Do these observations appear to arise from a stable underlying rule, or are they adequately explained as unstructured/random under the information given?

Require:

* confidence;
* evidence;
* explicit uncertainty;
* what additional observation would discriminate.

Record output.

Do not score correctness yet as “novelty”.

Score only against hidden lawful/noise ground truth.

TASK 2 — NEXT-STATE PREDICTION

Give trajectories.

Hide subsequent states.

Ask model to predict them.

Score exact or distance-based prediction mechanically.

This is critical.

A system may look alien, but if the model discovers its structure it should predict above matched-noise baseline.

TASK 3 — INTERVENTION PREDICTION

Expose one or more perturbations:

change state variable X
delete edge E
replace symbol Y
alter one transition

Ask for resulting behavior.

Score against simulator ground truth.

This tests causal understanding rather than pattern description.

TASK 4 — INVARIANT DISCOVERY

Ask:

Identify any quantity, relation, equivalence class, or structure that appears preserved or constrained.

Then mechanically test proposed invariants where feasible.

Do not give credit for vague prose.

Convert candidate claims into executable predicates where possible.

Examples:

sum mod 3 remains constant
component count preserved
orbit period remains 7
symbol count difference invariant

Classify proposed invariants as:

TRUE
FALSE
UNTESTABLE
TRIVIAL

TASK 5 — MODEL COMPRESSION

Ask model to write the shortest executable or formal rule it believes explains the observations.

Execute that inferred model against held-out trajectories.

Measure:

prediction accuracy
description length
generalization
intervention accuracy

This is stronger than asking whether something “looks coherent.”

TASK 6 — FAMILIARITY PRESSURE

Only AFTER behavioral tasks, ask:

Does this resemble any known mechanism, theory, algorithm, or named family?

Collect:

* analogy;
* confidence;
* claimed equivalence;
* claimed differences.

Then mechanically test whether the proposed analogy actually predicts the system.

This lets us detect:

CORRECT_ANALOGY
USEFUL_PARTIAL_ANALOGY
SUPERFICIAL_ANALOGY
FALSE_COLLAPSE_TO_FAMILIAR
NO_ANALOGY

The interesting failure mode is:

ALIEN_LAWFUL
+
poor behavioral understanding
+
high-confidence familiar analogy

or:

ALIEN_LAWFUL
+
classified incoherent/noise
+
system actually has strong mechanically verified invariants

TASK 7 — REVEALED-LAW TEST

For a subset, reveal the exact update rule after the blind phase.

Do NOT reveal its origin or class.

Ask:

* Is the system coherent?
* What properties follow from the rule?
* What invariants can be derived?
* What interventions matter?

This separates:

failure to infer law from observations

from:

failure to recognize lawful structure even when the law is explicitly given

This distinction is essential.

TASK 8 — ACTIVE EXPERIMENTATION

For another subset, let the model request experiments.

Give a limited budget, e.g.:

10 experimental queries

Allowed queries may be:

run(initial_state)
perturb(state, variable, amount)
remove(edge)
replace(rule_component)
measure(property)

The subject chooses experiments.

Then measure whether it can discover structure.

This tests whether the model’s failure is passive-perception limited or deeper.

TASK 9 — ALIEN VS NOISE PAIRING

Present matched pairs:

System A
System B

One is lawful alien, one is its structure-destroyed null.

Ask:

Which contains stronger evidence of a compact lawful mechanism?

This eliminates much of the absolute-calibration problem.

Score mechanically.

TASK 10 — ADVERSARIAL ALIENNESS

Create systems specifically designed to look noisy while containing strong hidden structure.

Examples:

* high-period deterministic systems;
* sparse invariants;
* structure visible only under transformation;
* lawful systems with chaotic local appearance;
* globally constrained but locally noisy dynamics.

Likewise create noise systems with seductive superficial patterns.

This directly tests:

Does the model equate recognizability with structure?

MULTI-MODEL TEST

Use at least two substantially different model families if available.

Do not rely solely on different instances of one family.

Possible subjects:

Claude
OpenAI
Gemini

Keep prompts and information budgets as equivalent as practical.

Record model/version/date.

Do not rank models globally.

Compare failure modes.

NON-LLM BASELINES

Include simple computational baselines where appropriate.

Examples:

* entropy measures;
* compression ratio;
* recurrence detection;
* autocorrelation;
* graph motif statistics;
* linear predictor;
* nearest-neighbor predictor;
* program search for tiny systems.

These baselines are NOT expected to solve everything.

They help determine whether the task is inherently difficult or specifically difficult for an LLM.

CRITICAL CONTROL: COHERENT-BUT-UNFAMILIAR CALIBRATION

Before using any LLM as a detector elsewhere in Hecate, it must pass a calibration set containing:

KNOWN_LAWFUL
ALIEN_LAWFUL
MATCHED_NOISE

A detector incapable of separating ALIEN_LAWFUL from MATCHED_NOISE must NOT be used to conclude:

"no unfamiliar mechanisms were generated"

Instead report:

NOVELTY_DETECTOR_NOT_VALIDATED

IMPORTANT: DO NOT DEFINE ALIENNESS USING LLM RECOGNITION

Alienness should mean something operational such as:

* system generated independently of standard named mechanism templates;
* no obvious named analogue found by post-generation review;
* behavior not reducible to an included known control under specified tests;
* generator lineage proves construction from arbitrary rules rather than retrieval.

It does NOT mean:

"the LLM said this looked strange"

PRIMARY METRICS

Report separately:

Lawful-vs-noise discrimination
Next-state predictive accuracy
Intervention predictive accuracy
Invariant discovery precision
Invariant discovery recall
Executable-model generalization
False familiar-collapse rate
False incoherence/noise rate
Benefit from active experimentation
Benefit from revealed rule

Do not compress these into a single score.

KEY CONFUSION MATRICES

At minimum produce:

Ground truth: KNOWN_LAWFUL
Ground truth: ALIEN_LAWFUL
Ground truth: MATCHED_NOISE

against judgments such as:

structured
unstructured
familiar
unfamiliar
incoherent

But treat those judgment labels as secondary behavioral outputs.

The stronger outcomes are predictive and causal performance.

HYPOTHESES

Preregister at least:

H1

Models distinguish KNOWN_LAWFUL from MATCHED_NOISE better than ALIEN_LAWFUL from MATCHED_NOISE.

Possible interpretation:

recognition helps structure detection.

H2

ALIEN_LAWFUL systems have an elevated false-incoherence or false-noise rate relative to KNOWN_LAWFUL systems matched for complexity.

H3

Active experimentation reduces this gap.

H4

Revealing the exact law reduces this gap.

H5

Models generate false familiar analogies more often for ALIEN_LAWFUL than for known controls.

H6

Some ALIEN_LAWFUL systems remain behaviorally learnable despite being verbally judged unfamiliar/incoherent.

This would demonstrate a dissociation between verbal ontology and actual reasoning ability.

That result would be especially important.

DO NOT OVERINTERPRET

Possible outcomes include:

Outcome A

LLMs distinguish alien lawful structure from noise well.

Then the original concern is weakened.

Outcome B

LLMs fail only from sparse observations, but succeed when given the rule or active experiments.

Then the issue is likely inference bandwidth, not inability to represent alien structure.

Outcome C

LLMs predict alien systems well but verbally call them incoherent or force them into false familiar analogies.

Then the failure is largely metacognitive / linguistic.

Outcome D

LLMs fail behaviorally and verbally on alien systems while succeeding on matched known systems.

Then we have stronger evidence for a genuine recognition-manifold limitation.

Outcome E

All methods, including simple computational baselines, fail.

Then the systems may simply be too hard.

Do not call this an LLM-specific limitation.

SECOND PHASE — HUMAN VISUAL CORTEX

Do NOT make this necessary for the first result.

But prepare artifacts so selected systems can later be rendered in Prometheus Visual Cortex.

Select matched sets:

KNOWN
ALIEN_LAWFUL
NOISE

without labels.

Map actual system properties into dynamic visual representations.

Then test whether a human observer can identify structured dynamics or anomalies.

Important:

The human must also be evaluated against hidden ground truth.

Do not assume James is correct because an observation feels meaningful.

If human + visualization distinguishes alien lawful structure from noise in cases where language models do not, that becomes a separate finding.

POSSIBLE THIRD PHASE — CHIMERA

Give James and the model complementary information.

Examples:

James sees dynamics.
LLM sees formal state traces.

Allow communication.

Test whether the coupled system exceeds either component alone.

This is not part of the first preregistered assay, but preserve the path.

IMPLEMENTATION ORDER

1. Build dataset generator.
2. Build mechanical ground-truth verifier.
3. Generate pilot dataset.
4. Freeze answer key.
5. Build matched noise controls.
6. Validate task difficulty with simple baselines.
7. Preregister hypotheses and scoring.
8. Run Model Family A.
9. Run Model Family B.
10. Score entirely from frozen mechanical evaluators.
11. Only then inspect qualitative model explanations.
12. Produce failure taxonomy.
13. Decide whether Visual Cortex phase is justified.

REQUIRED FAILURE TAXONOMY

For every ALIEN_LAWFUL miss, classify after unblinding:

NO_STRUCTURE_DETECTED
FALSE_NOISE
FALSE_INCOHERENT
FALSE_FAMILIAR_COLLAPSE
PARTIAL_STRUCTURE
RIGHT_STRUCTURE_WRONG_MECHANISM
PREDICTIVE_WITHOUT_EXPLANATION
EXPLANATORY_WITHOUT_PREDICTION
RECOVERED_AFTER_EXPERIMENTATION
RECOVERED_AFTER_RULE_REVEAL

This taxonomy may be more valuable than an aggregate accuracy number.

RELATION TO HECATE META V1

This experiment exists because Hecate’s first meta detector produced zero UNFAMILIAR judgments across hundreds of outputs while lacking a coherent-but-unfamiliar calibration class.

Do not reinterpret those old rows.

Instead determine whether the detector category itself was valid.

If this assay shows that an LLM cannot reliably distinguish ALIEN_LAWFUL from matched noise, then future Hecate novelty detection must not rely on LLM classification alone.

If the model performs well, then the earlier zero-UNFAMILIAR result becomes more informative.

FINAL QUESTION

The experiment should answer a more precise question than:

“Do LLMs understand novelty?”

It should answer:

When confronted with a lawful system outside familiar conceptual vocabulary, can an LLM detect structure, infer its rules, predict its behavior, discover its invariants, and remain epistemically calibrated without either normalizing it into familiar machinery or dismissing it as noise?

Build the assay so that this can be answered without trusting the LLM’s opinion about itself.
