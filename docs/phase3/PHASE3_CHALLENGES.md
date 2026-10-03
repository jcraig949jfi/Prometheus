# Prometheus Phase 3: challenges to address

Status: working statement of program-level concerns, 2026-10-01 (Challenge 4 added the same day). It originates in an operator discussion and was
drafted by Harmonia[m2-475d761f]. It is not a plan or a preregistration. It names the problems Phase 3 must solve,
or must show it cannot solve, before Phase 3 results can be read as science.

Companion evidence: the four Phase 3 forensic crawl packages in `docs/phase3/intake/` (ixion, sisyphus, tantalus,
tityos). They exist so these questions are settled from what the systems actually did, not from Prometheus's
account of itself. Where this document asserts something about past engines, the intake packages and the cited
records are the authority. Where they disagree with this document, they win.

Taken together, the four challenges below may change what Phase 3 means by a "lens". A lens is not only a way of
looking at an output. It includes the apparatus that makes a phenomenon possible, demanded, detectable and reachable by development. A lens
that leaves any of those out is not yet an instrument.

---

## Challenge 1 -- Scientific legitimacy: calibrated instruments versus experimental theater

### The concern

Is Prometheus research, or research cosplay?

### Current assessment

Prometheus is not research cosplay. Much of its experimental output is still **pre-scientific instrumentation**
rather than mature science. These are different criticisms and need different remedies.

**What rules out cosplay is behavior.** The program has repeatedly killed its own attractive results. It has added,
over time:
- preregistration and freeze-before-run;
- negative, positive and cheat controls;
- transplantation and withheld worlds;
- provenance, adversarial review and independent reconstruction;
- baseline challenges and published corrections.

Examples:
- Nestor's "spontaneous replication" result was dismantled rather than defended.
- Ensorain found that a constant predictor beat its organisms; this became the constant-twin rule.
- Cosmos found that location bias explained an apparent law.
- Bellerophon's E-BEL-REPL-01 errata withdrew "the kill is real" within hours of an adversarial review.

That is what a scientific process does.

**But serious process does not create serious science.** Much of Prometheus ran on instruments whose
sensitivity and specificity were unknown.
- The false-positive rate was often unmeasured.
- More damaging, the **false-negative rate** was usually unmeasured. Many protocols were rigorous but wrapped around
  organisms or worlds that may have been incapable of showing the phenomenon under test.

> **The experimental procedure can be rigorous while the experimental apparatus is inadequate.**

The record already contains this failure class, named after the fact:
- **Tyche dark-ecology v0, H1/H6.** PASS was unreachable by design: the initial population fixed the VOID status
  before a single generation ran (Harmonia ruler-quality audit, 2026-09-30).
- **Bellerophon E-BEL-REPL-01, K3.** The content-descent test had no demonstrated route to SURVIVES, because founder
  content turns over in every arm, including the no-payoff control (errata c776cea6a). E-BEL-REPL-02 repeated the
  defect.
- **Hecate's "zero UNFAMILIAR".** The detector's calibration set contained no UNFAMILIAR item, so the absence claim
  was uncalibrated. The 14 controls were later found never to have been committed.
- **IQ-NULL.** The preregistered terminal table did not partition the outcome space, so no run could truthfully
  claim "exactly one" verdict.

Artificial life has the same problem in general form. Open-endedness criteria can be satisfied by systems that stay
behaviorally simple. The harder question is whether a system produces increasing structural or functional
complexity, and that needs instruments that can tell the two apart.

### Defensible external description, today

> An unusually extensive independent experimental research program with increasingly sophisticated scientific
> controls, but largely prototype-grade instruments and limited externally validated scientific claims.

Some pieces are hobbyist-grade. Some methodology is considerably more mature. Some engineering is sophisticated.
The system as a whole is scientifically **immature**, not scientifically **unserious**.

### What must be addressed

**1a. Replace "did it get a positive result?" with a per-result evidence profile.** Every result the meta-analysis
touches is scored separately on each axis below. No axis may be inferred from another.

| Axis | Question | Typical evidence |
|---|---|---|
| Q -- question | Is the question meaningful and stated as something that could fail? | Prereg text, kill criteria |
| S -- substrate capacity | Can the organism or substrate instantiate the phenomenon at all? | Constructive existence proof: a hand-built organism in the same substrate that exhibits it |
| W -- world demand | Does the world require the phenomenon, so that organisms without it do measurably worse? | Ablated-capability baseline vs capable baseline |
| R -- ruler validity | Can the measurement detect the phenomenon when present and reject it when absent? | Planted positive, matched negative, measured false-positive and false-negative rates |
| B -- baseline discrimination | Do the baselines rule out the cheap shortcuts? | Constant twin, lookup table, shuffled labels, chance floor |
| Rep -- replication | Does it recur under new seeds, a new host, or an independent reconstruction? | Separate-instance rerun with fingerprinted inputs |
| M -- mechanism | Does the claimed mechanism survive intervention: ablation removes it, transplant restores it? | Knockout and transplant receipts |

**1b. Make null results carry their apparatus.** A null is reported with its S, W and R scores. A null with
undemonstrated S or W is recorded as a **null about the apparatus**, not about the phenomenon.

**1c. Expect a large downgrade, and treat it as a gain.** The exercise will probably downgrade much apparent
Prometheus science while making the strongest 5-10% much more credible. Both outcomes count as the deliverable.

**1d. Measure ruler error rates as a standing requirement.** Every verdict-bearing ruler carries:
- its attainable verdict set at the actual design (STANDING_RULES F1);
- a positive control showing it can fire (F2, F8);
- an exact or simulated null-pass rate (F5).

A ruler without these is a probe, not an instrument, and its outputs are labelled as such.

**1e. Seek external validation.** Internal adversarial review is necessary but circular. Phase 3 should name the
few claims it would put before outside reviewers, and what form that would take: replication package,
preregistered external holdout, or a written methods paper.

---

## Challenge 2 -- Cognitive sufficiency: the organizational scale of reasoning

### The concern

Prometheus has implicitly assumed something like:

> enough primitive variation + enough pressure -> a reasoning primitive

That may be wrong. A useful reasoning mechanism may live at a **mesoscale far above** the primitives being
perturbed. Perturbing molecules may never find a circuit if the substrate cannot hold one.

### Why the assumption is suspect

Even a modest human reasoning episode involves many interacting functions:
- persistent state that survives while intermediate ideas are manipulated;
- selection of what matters;
- retrieval of related material;
- noticing analogies;
- representing alternatives, and keeping unresolved hypotheses alive;
- transformations, and evaluation of intermediate results;
- backtracking to an earlier state after a dead end;
- processes running at different timescales.

Cognitive-architecture research keeps emphasizing multi-timescale organization over cognition as one homogeneous
process.

This is **not** an argument for copying human cognitive psychology into organisms. It is an argument that the
substrate needs enough physics for cognitive organization to exist at all: a **physics of cognitive
architectures**.

### What must be addressed

**2a. Search across organizational scales, not only instruction -> behavior.**

    primitive -> motif -> circuit -> architecture -> cognitive ecology

Each level needs its own observables, and its own ablation and transplant operators. "This circuit carries the
capability" must be testable the way "this instruction carries the capability" is today.

**2b. Define a cognitive viability floor as affordances, not modules.** Hard-coding a "working memory module",
"analogy module" or "planner" imports conventional priors and is excluded. Instead, the physics should afford:
- persistent writable state;
- addressable and/or associative state;
- compositional structures;
- multiple timescales;
- dynamic routing and conditional activation;
- information bottlenecks;
- internal state transitions that need not immediately affect the environment;
- reusable substructures;
- communication channels;
- mechanisms for copying or transforming internal structures.

Pressure then decides what those affordances become. The difference from a scratchpad API is the point: Phase 3
provides **the possibility of a scratchpad emerging**, and worlds in which organisms without something
scratchpad-like are severely disadvantaged.

Each affordance needs a **substrate capacity proof** (axis S above): a hand-built organism in that substrate that
uses the affordance and gains from it. Without one, the affordance is asserted, not provided.

**2c. Build worlds whose optimal strategy is not a reactive heuristic.** A reasoning world should force something
like:

    observe -> remember -> infer hidden structure -> preserve competing possibilities
            -> acquire new evidence -> revise -> compose prior knowledge -> act

It must also vary enough that memorizing the surface does not work. Concretely, each world ships:
- a **reactive-ceiling baseline**: the best memoryless policy. The world is admitted only if a known
  reasoning-capable reference policy beats it by a stated margin;
- a **surface-memorization baseline**: a lookup over seen episodes, evaluated on held-out structure;
- a **depth certificate** (2d).

**2d. Measure cognitive depth, not world size.** A 64x64 world is not bad because 64 is small. It is bad if its
computational depth is shallow. A tiny environment can demand deep reasoning, and a billion-cell environment can
demand none. Candidate depth measures for the crawl and for new worlds:
- minimum memory (bits or states) of any policy reaching a target score;
- the horizon over which hidden state must be carried;
- the number of hypotheses that must be kept live at once;
- the gap between the optimal policy and the reactive ceiling;
- the compositional depth of the optimal policy (how many reused sub-solutions it chains);
- robustness of all of the above across world variants.

**2e. Reinterpret old nulls.** If an engine searched billions of mutations in a substrate that could not hold the
state the sought capability needs, the null says essentially nothing about whether that primitive can emerge. It
says something about the substrate. That is still a valuable result, but a different one, and it is re-filed as
such:
- the meta-analysis assigns every historical reasoning null an S and W score;
- nulls failing S or W move from "capability absent" to "substrate or world insufficient".

### The scientific question this sharpens

> What minimum substrate and world complexity must exist before a null result about reasoning becomes
> interpretable? At what organizational scale do reasoning primitives actually live?

---

## Challenge 3 -- Epistemic escape: can a search system trained on human artifacts find mechanisms outside that ontology?

### The concern

Can an LLM create an alien cognitive architecture? Or does everything it produces lie in the rear-view mirror of
its training corpus, so that its "inventions" and its judgments of novelty both collapse back to the familiar?

### Current assessment

**Possibly, but probably not by sitting down and inventing one in prose.**

There is credible evidence that LLMs can be productive **components** of algorithm-discovery systems:
- AlphaEvolve combines LLM-generated program mutations with automated evaluators and evolutionary selection, and
  that combination has produced improved algorithms, not just prose suggestions.
- Work on LLM-assisted algorithm and architecture search is expanding.

None of this establishes that an LLM can **conceptually originate** a fundamentally alien cognitive architecture.

The rear-view-mirror concern also has empirical support:
- Novelty-assessment studies report that leading LLMs produce plausible reasoning about novelty while disagreeing
  substantially with expert judgment.
- A 2026 study of research proposals, raised in the operator discussion, associated LLM-vs-human disagreement
  specifically with human-rated novelty: the LLM evaluator tended away from the proposals humans found most novel.

That is not direct evidence about alien architectures, but it is exactly the failure mode to guard against. Those
citations should be pinned to specific papers before they appear in any external-facing text.

The record already contains this failure in our own instruments:
- Hecate's alien-lawful validation rule could be passed by a lookup-table baseline. It validated lawful-vs-noise
  discrimination, not novelty.
- Single-seed LLM probes have proven prompt-steerable.

### The design principle

Do **not** ask an LLM: "Invent an alien architecture and tell me whether it is alien." That closes the epistemic
loop inside one learned distribution.

**Instead, use LLMs as one source of mutations in a search whose survival criteria are outside the LLM.** The model
can:
- write code, recombine mechanisms and repair candidates;
- propose transformations and notice structural possibilities;
- translate strange artifacts into experiments.

But:

| Decision | Made by |
|---|---|
| Does the architecture work? | The world |
| Does the behavioral effect exist? | Deterministic instrumentation |
| Is the mechanism causal? | Interventions (ablation) |
| Does it travel? | Transplants across worlds |
| Have humans seen it before? | Prior-art retrieval, **after** validation |

### What must be addressed

**3a. The anti-gravity rule: no model may kill a candidate because it cannot categorize it.** This may be the
single most important rule in Phase 3.

Suppose structure X:
- repeatedly solves a class of hidden-state problems;
- loses the capability when removed, and restores it when transplanted;
- transfers across three substantially different worlds.

Suppose further that every model calls it "noise", "a strange recurrent buffer", or "probably a degenerate
finite-state machine". **X is preserved.**

When the behavioral evidence survives, a failure of our models to give X a familiar interpretation may **raise** its
investigative priority.

> **Unclassifiable is not uninteresting.** It may be exactly what Prometheus is searching for.

**3b. The guard on the anti-gravity rule.** The inversion applies only to candidates that pass the behavioral and
causal gates: effect over baselines, ablation, transplant, replication. Without that guard, "nobody can explain it"
becomes a reward for noise, which is the same failure in the other direction. Unclassifiability raises priority. It
is never evidence.

**3c. Separate three epistemic systems, and fix their authority.**

| Layer | Function | Authority |
|---|---|---|
| Generation | LLMs, mutation, recombination, evolution, random construction, foreign mechanisms, search | Proposes candidates |
| Reality | Worlds, organisms, deterministic rulers, causal interventions, transplantation, replication | Decides survival |
| Interpretation | LLM analysis, mechanism description, prior-art search, theoretical abstraction | Proposes experiments and descriptions |

The dangerous architecture is one where Interpretation controls Reality. Phase 3 inverts that:
- **Interpretation may propose experiments. It may not erase unexplained phenomena.**
- Concretely, no Interpretation-layer output can delete, demote or exclude a candidate from the archive. Only a
  Reality-layer verdict can, and its receipts must be fingerprinted.

**3d. Use multi-model disagreement as an instrument, not a vote.** Several frontier models (e.g. Fable, Astra, Opus,
GPT-5.6, Gemini) are valuable less because five models produce five plans than because their disagreements expose
the shared and non-shared boundaries of their learned priors. A proposed reading of the patterns:

| Pattern across models | Reading |
|---|---|
| All instantly give the same familiar analogy | Possible corpus gravity. Treat the consensus as a hypothesis to test, not a classification. |
| Radically different explanations, but the phenomenon stays experimentally stable | Interesting: the phenomenon is robust and its interpretation is not anchored. |
| None can explain it, but all can independently design discriminating experiments | Very interesting: highest investigative priority. |

This needs its own calibration:
- run the panel on known mechanisms, planted familiar and planted unfamiliar;
- measure how often each pattern fires on each.

This is the API-probe discipline: several seeds across several model families.

**3e. Measure alienness relative to the corpus, after the fact.** Prior-art retrieval runs only after Reality-layer
validation. A mechanism's distance from the nearest known prior art is recorded as an outcome, never used as a
selection pressure. Selecting for "alienness" directly is a Goodhart target, so it is never used as a fitness term.

### The scientific question this sharpens

> Can a search system whose generative components are trained on historical human artifacts discover mechanisms
> outside that ontology? And can Prometheus preserve and validate such mechanisms without forcing them back into
> familiar categories?

---


## Challenge 4 -- Developmental adequacy: searching for what an organism can become, not only what it does

### The concern

This may be one of the most important corrections to how Prometheus has framed its search. The program keeps
talking about discovering a **reasoning architecture**, as though the object of interest were a finished circuit.
Human cognition suggests that may be the wrong unit.

A human infant and a highly trained researcher share broadly the same biological substrate. They do not share the
same effective cognitive architecture. Development builds layers of usable machinery over years:
- representations and working strategies;
- learned abstractions and metacognitive habits;
- language-mediated structure and external tool use;
- culturally transmitted concepts;
- enormous amounts of compressed experience.

The substrate permits these. The mature architecture is partly **constructed through interaction**.

The object Prometheus may need to search for is therefore not

> a reasoning circuit

but

> **a developmental program capable of constructing increasingly powerful reasoning circuits.**

That is a much more interesting target.

### The spectrum: precompiled versus self-constructed cognition

**The fruit fly and the human.**
- A fruit fly shows impressive decision behavior, with much of its useful machinery strongly canalized by evolution.
- A human has relatively less behavior specified in finished form, and vastly more capacity to build internal
  structure through development.

Both are neural systems, but they sit at very different points on a spectrum from precompiled to self-constructed
cognition. Two organisms can share the same nominal substrate and differ radically in intelligence because they
differ in what has been instantiated inside it.

**Capacity versus realization.** This gives a distinction Prometheus has not been measuring: **reasoning capacity**
versus **reasoning realization**.

| | Low realized competence | High realized competence |
|---|---|---|
| **High developmental capacity** | Newborn: enormous latent capacity, little realized competence | Trained human researcher |
| **Low developmental capacity** | Inert or degenerate organism | Specialized insect: limited general developmental capacity, highly competent niche circuits; also a conventionally trained neural network, competent but with almost no capacity to reorganize its own architecture after training |

An alien Prometheus organism might occupy some entirely different region of this space. That is fertile ground, but
only if capacity and realization are measured separately (4d).

### Four separable layers

| Layer | Question |
|---|---|
| Substrate | What computational structures are physically possible? |
| Developmental rules | How can new internal structures form, stabilize, combine and disappear? |
| Experience / curriculum | What pressures and exposures cause those structures to emerge? |
| Mature cognitive organization | What reasoning machinery eventually exists? |

**Prometheus has often jumped from the first layer straight to the fourth.** It builds a substrate, mutates
programs, puts them in a world, and asks whether the desired behavior appears. Human cognition suggests **the
missing middle may be everything**. A substrate could support sophisticated reasoning and still produce nothing if
no developmental process can cross the enormous distance from an unstructured initial state to a mature cognitive
organization.

Challenge 2 asks whether the substrate and the world are sufficient. Challenge 4 asks whether anything can **get
there**.

### What must be addressed

**4a. Treat development as an experimental variable, separate from evolution.** There are two timescales:
- **Search or evolution**: across generations, it acts on substrates and developmental rules.
- **Development**: within an organism's lifetime, it acts on internal structure through experience.

Search then does not have to find a complete mature intelligence in one jump. It only has to find a developmental
rule that bootstraps progressively better machinery. That mirrors biology: DNA does not specify an adult's
understanding of neural networks; it specifies machinery that can eventually acquire it.

The search space is larger: **developmental dynamics over architecture space**, not architecture space alone. The
search may nonetheless be easier, because each step only has to improve the developmental rule.

**4b. Give organisms mechanisms for structural development, not only parameter learning.** Humans do not just fill a
fixed memory bank with more facts. Development alters effective connectivity, representations, control strategies,
abstraction boundaries, attention, metacognition, and what counts as salient. Candidate structural-development
affordances, which extend the Challenge 2 viability floor:
- forming new modules or subunits;
- modifying connectivity;
- consolidating frequently used pathways;
- pruning unused structures;
- creating longer-lived memories from short-lived ones;
- changing what is addressable;
- altering routing;
- building internal interfaces between previously separate mechanisms.

As with 2b, these are affordances whose use is decided by pressure, not prescribed modules. Each needs a
**developmental capacity proof**: a hand-built organism whose development uses the affordance and gains from it.

**4c. Turn the reasoning ladder into a developmental curriculum.** The ladder is more than a benchmark. Instead of
asking an organism to solve a high-rung problem immediately, ask whether an initially weak organism can
progressively acquire structures that carry it along a sequence like:

    simple discrimination -> persistent state -> conditional behavior -> reusable memory
      -> latent-state inference -> compositional structure -> counterfactual manipulation
      -> abstraction -> strategy selection -> metacognition

The world has to **teach**: not by explicit instruction, but through a sequence of environments in which earlier
structures are useful prerequisites for later ones.
- The prerequisites need not be ones we specify.
- Success at one stage changes the organism's accessible future, without telling it which internal mechanism to use.

Done right, this produces something closer to **cognitive ontogeny** than to optimization.

Two cautions from the ladder's own history:
- **Grading must stay outside the organism's reach.** The R6 oracle once shipped `truth` inside the probe, an answer
  key leak. A curriculum that leaks its answers teaches only reading.
- **A rung is occupied only when a mechanism is shown,** not merely a score (ladder v0.1 rule).

**4d. Make the trajectory the measured object, not the final score.** For each rung transition, the record should
answer:

| Question | Operational test |
|---|---|
| What changed internally between rung n and rung n+1? | Structural diff of the organism before and after the transition |
| What structure appeared? | Localization by ablation: which new structure carries the new capability |
| Did it persist after the original task disappeared? | Retention test after the task is removed from the curriculum |
| Did it become reusable? | Use of the same structure on a different task (shared-ablation test) |
| Did acquiring it make rung n+2 easier? | **Savings test**: learning time for n+2 with vs without prior acquisition of n+1 |
| Can it be transplanted? | Install the structure in a naive organism and measure the gain |
| Can another history reach the same capability by a different mechanism? | Independent developmental runs; compare mechanisms, not just scores |

The last question matters most for discovery. Convergent capability through **divergent mechanisms** is how
Prometheus would tell an alien solution from a re-derivation of the obvious one (compare 3a).

**4e. Measure capacity separately from realization.**
- **Realization** is what the organism can do now: the familiar score.
- **Capacity** is what it can become: performance after a standard developmental exposure, from a standard initial
  state, within a stated budget.

Candidate capacity measures:
- the rung reached under a fixed curriculum and budget;
- the slope of the developmental trajectory;
- savings on novel rungs;
- recovery after damage, i.e. re-development after ablation.

An organism that scores poorly now but develops fast is a different and possibly more valuable find than one that
scores well and cannot change.

**4f. Reinterpret false negatives a second time.** Suppose an organism has writable memory, dynamic routing,
compositional structures, recurrence and self-modification. It is put straight into a hard world for 10,000
generations, and nothing resembling reasoning emerges. Concluding "this substrate does not support reasoning" may be
the equivalent of dropping newborns into graduate mathematics and concluding that primate cortex cannot do abstract
reasoning. The missing variable is **developmental scaffolding**. A null result is therefore labelled by the
conditions it was obtained under:

| Condition missing | What the null is about |
|---|---|
| Substrate capacity not shown (2b) | The substrate |
| World demand not shown (2c) | The world |
| No developmental mechanism, or no curriculum | **Direct emergence only**; silent on developmental emergence |
| Curriculum present but no developmental capacity proof (4b) | The developmental rule |

**4g. Required controls for any developmental claim.**
- **Same-compute direct control:** the same organism and total compute on the final world only. This shows the
  curriculum matters.
- **Shuffled-order curriculum:** the same environments in a scrambled order. This shows the ordering matters.
- **Frozen-development control:** structural development disabled, with parameter learning only if the substrate has
  it. This shows development matters, not just exposure.
- **Constant twin and memorization baselines at every rung** (Challenge 1, axis B).

Without these, "the curriculum produced reasoning" cannot be told apart from "more compute produced reasoning".

### The connection to Sagacity

Sagacity may not be a property of a static architecture at all. It may be an emergent property of a system that can
repeatedly:

    experience -> restructure -> compress -> generalize -> reuse -> reflect -> restructure again

That recursive developmental loop may be far closer to what Prometheus is actually hunting than any single circuit.
If so, the measured object is the loop:
- its rate;
- its stability, i.e. whether restructuring preserves earlier competence;
- whether each pass makes the next pass more productive.

### The scientific question this sharpens

> What substrate, developmental rules, environmental curriculum and timescale are needed for progressively more
> capable reasoning machinery to construct itself? And how can latent cognitive capacity be distinguished from
> realized competence?

It also changes the Phase 3 lenses. They should not only ask "what can this organism do?" They should increasingly
ask **"what can this organism become?"** That is a very different experiment.

---

## The four meta-analysis investigations

These four challenges become explicit Phase 3 investigations. Each should produce a written result even if the
result is negative.

1. **Scientific Legitimacy.** Which parts of Prometheus are calibrated scientific instruments rather than
   elaborate experimental theater, and what evidence distinguishes them?
   - Deliverable: the per-result evidence profile (Q/S/W/R/B/Rep/M) over the historical record, and the surviving
     calibrated core.
2. **Cognitive Sufficiency.** What minimum substrate and world complexity is needed before a null result about
   reasoning becomes interpretable? At what organizational scale do reasoning primitives live?
   - Deliverables: a substrate affordance floor with capacity proofs; world depth certificates; the
     re-classification of historical reasoning nulls.
3. **Epistemic Escape.** Can a search system built from historically trained components discover mechanisms
   outside that ontology, and can Prometheus preserve them without forcing them into familiar categories?
   - Deliverables: the three-layer authority separation, enforced in code; the anti-gravity rule with its guard;
     the calibrated multi-model disagreement instrument.
4. **Developmental Adequacy.** What substrate, developmental rules, curriculum and timescale are needed for
   progressively more capable reasoning machinery to construct itself, and how is latent capacity distinguished from
   realized competence?
   - Deliverables:
     - structural-development affordances with capacity proofs;
     - the ladder rebuilt as a developmental curriculum with out-of-reach grading;
     - trajectory instrumentation (structural diff, retention, reuse, savings, transplant, divergent-mechanism runs);
     - capacity and realization measured separately;
     - the developmental control set.

## Order of dependence

The four are not independent.
- Without Investigation 1, no Phase 3 positive can be trusted.
- Without Investigation 2, no Phase 3 negative can be interpreted.
- Without Investigation 4, a negative obtained without development or curriculum says nothing about developmental
  emergence. It may be the newborn-in-graduate-school result.
- Without Investigation 3, any positive found by an LLM-in-the-loop search may be the corpus recognizing itself.

A sensible order:
1. Start with the legitimacy profile of the historical record, which the intake crawls already make possible.
2. Build the affordance floor (static and structural-development), the world depth certificates, and the
   developmental curriculum with its controls.
3. Only then run generation at scale, over developmental rules as well as architectures, under the three-layer
   separation.

## The deeper question

If Phase 3 answers these four questions, that is a worthwhile research contribution even before it finds an alien
reasoning architecture. The deeper subject may turn out not to be "can we evolve reasoning?" but:

> **What experimental conditions make genuinely unfamiliar cognition observable at all, and what conditions let it
> build itself?**

That is a much stronger scientific question for Prometheus, and one it is unusually well placed to ask, because it
has already spent a year discovering, the hard way, how instruments fail.
