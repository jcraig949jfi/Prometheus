# Prometheus Phase 3: challenges to address

Status: working statement of program-level concerns, 2026-10-01. It originates in an operator discussion and was
drafted by Harmonia[m2-475d761f]. It is not a plan or a preregistration. It names the problems Phase 3 must solve,
or must show it cannot solve, before Phase 3 results can be read as science.

Companion evidence: the four Phase 3 forensic crawl packages in `docs/phase3/intake/` (ixion, sisyphus, tantalus,
tityos). They exist so these questions are settled from what the systems actually did, not from Prometheus's
account of itself. Where this document asserts something about past engines, the intake packages and the cited
records are the authority. Where they disagree with this document, they win.

Taken together, the three challenges below may change what Phase 3 means by a "lens". A lens is not only a way of
looking at an output. It includes the apparatus that makes a phenomenon possible, demanded and detectable. A lens
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

## The three meta-analysis investigations

These three challenges become explicit Phase 3 investigations. Each should produce a written result even if the
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

## Order of dependence

The three are not independent.
- Without Investigation 1, no Phase 3 positive can be trusted.
- Without Investigation 2, no Phase 3 negative can be interpreted.
- Without Investigation 3, any positive found by an LLM-in-the-loop search may be the corpus recognizing itself.

A sensible order:
1. Start with the legitimacy profile of the historical record, which the intake crawls already make possible.
2. Then build the affordance floor and world depth certificates.
3. Only then run generation at scale under the three-layer separation.

## The deeper question

If Phase 3 answers these three questions, that is a worthwhile research contribution even before it finds an alien
reasoning architecture. The deeper subject may turn out not to be "can we evolve reasoning?" but:

> **What experimental conditions make genuinely unfamiliar cognition observable at all?**

That is a much stronger scientific question for Prometheus, and one it is unusually well placed to ask, because it
has already spent a year discovering, the hard way, how instruments fail.
