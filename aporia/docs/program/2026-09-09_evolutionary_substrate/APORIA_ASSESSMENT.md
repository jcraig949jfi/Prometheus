# Aporia's assessment — the evolutionary reasoning substrate

**2026-09-09. Program level, not H1.** Written at the operator's request after
he described the proposal as giving him hope and as "a culmination of all we're
working towards."

That framing is where the pressure to agree is highest, so I am going to be
direct about where I think it is right, where it is a re-description of what the
programme already plans, and where the literature this seat just finished
measuring says it will not work as stated.

Companion files: `gemini_proposal.md`, `astra_assessment.md`.

---

## Summary judgement

**Astra's assessment is sharper than the proposal it reviews, and I agree with
almost all of it.** The single most important line in the whole exchange is
Astra's:

> Calling all three "metabolism" makes the uncertainty disappear linguistically.

That is the failure mode of the entire proposal in one sentence. Most of what
Gemini describes is the programme's existing plan restated in biological
vocabulary, and the vocabulary conceals the joins. Secreting, metabolising,
enzymes, amino acids and soup are not mechanisms; they are names for mechanisms
that would each need separate evidence.

**It is not a culmination. It is a re-description, plus one genuinely new
idea.** That new idea — the tripartite primitive that separates continuous
mutation of a binding site from discrete mutation of an operator — is worth
keeping, and I say why below.

---

## What is actually new, and worth keeping

**Splitting the mutation operator by representation.** Receptor drift is
continuous Gaussian noise on a vector; operator crossover swaps AST subtrees.
This addresses a real problem: random mutation of program text mostly yields
syntax errors and stalls the search. Splitting the genome so that one half
mutates smoothly and the other half mutates structurally is a concrete
proposal, and it is the only part of the architecture that is not already in
the H0-H5 plan under another name.

Astra is right that AST-subtree swapping does not guarantee type compatibility,
valid bindings, or termination. But "syntactically valid" is a real improvement
over "valid text," and the remaining problem — type-correct crossover — is
solved machinery in typed genetic programming, not an open question.

**Specimen investigation as a first-class activity.** Astra says this belongs
at the beginning rather than the end, and that is correct and important.
Gemini frames interpretability as a bottleneck to be faced *after* success.
Recording enough to replay a circuit, disable an edge, substitute a component
and reset inherited memory is cheap at the start and impossible to retrofit.

---

## Where the proposal is the programme's existing plan wearing a costume

    Gemini's component        Already exists in the plan as
    ----------------------    --------------------------------------------
    Transporters              H1, failure transport
    Executable primitives     H2 components, and the typed component contract
    QD engine, MAP-Elites     H3, retention policy
    Generators/Falsifiers     the producer/adjudicator split already in place
    Accumulators              H0's frozen component library

Five of Gemini's six architectural elements are H1 to H3 with new names. That is
not a criticism of the proposal's coherence — the elements do fit together — but
it means adopting it commits the programme to nothing it has not already
committed to, while making the open questions harder to see.

---

## What the literature this seat just measured says

The frontier campaign closed on 2026-09-08 with 109 Deep Research dossiers, and
several of them bear directly on this architecture. None of this was written
with the proposal in mind, which is why it is worth weighing.

**Novelty search does not diverge in an unbounded space.** Dossier 03, on
open-ended evolution:

> In a mathematically unbounded space the volume grows exponentially with
> distance from the origin, the archive becomes hopelessly sparse, and because
> mutation step sizes are fixed the population cannot traverse the widening
> gaps. Novelty Search in an unbounded space converges to a local optimum
> cluster; it does not diverge endlessly. The critique stands unanswered.

Gemini's "over thousands of epochs you are evolving a topology" is exactly the
claim this critique refutes for the unbounded case. An open-ended soup of
composable primitives is an unbounded space by construction. Either the space
gets bounded — which is a design commitment nobody has made — or this applies.

**Classical MAP-Elites fails at the scale proposed.** Dossier 02 opens by
correcting the classical formulation as "historically accurate but
methodologically outdated," and states that a rigid grid suffers the curse of
dimensionality past three or four behavioural dimensions, and that random
genetic mutation cannot find stepping stones in high-dimensional parameter
spaces. Gemini proposes a grid, names three axes, and says "e.g.", implying
more.

**The archive engine has a recent negative result in program evolution
specifically.** arXiv:2608.19703, Loreley, verified by direct fetch: a
repository-scale program evolution experiment comparing a quality-diversity
archive against sequential champion editing at matched budgets. QD came in
0.135 percent BELOW the champion baseline. The authors: "Neither contrast
established a QD advantage." The stepping-stone mechanism engaged and produced
no endpoint benefit. Sample size is small — 48 jobs — so this does not close the
question, but the proposal's central engine has a published null in the nearest
adjacent domain and the proposal does not know it.

**Noisy environments fill archives with luck.** Dossier 03 again, on "Ghost
Elites": in noisy evaluation, archives fill with policies that got a lucky roll
and regress to the mean when selected. An asynchronous message-passing soup with
non-deterministic interleaving is a noisy evaluator by construction, and the
standing charge that QD metrics measure luck in such settings is structural and
open.

**Both Avida and Tierra begin with a hand-written replicator.** Dossier 74, on
emergent self-replication — the most-referenced uncovered topic in the whole
corpus. Gemini's soup assumes primitives that already reproduce and inherit. So
does every template in the programme's matrix. The question of where the first
inheriting thing comes from is assumed away here as it is everywhere else, and
Astra's "the biggest missing piece is an inheritable organism" is the same
observation from the design side.

---

## The objection I would add that neither reviewer made

**The behavioural descriptors are the human ontology, smuggled in as geometry.**

Astra correctly says the task encoder is part of the scientific hypothesis and
that a pretrained encoder brings learned structure into the search. I would go
further, because there is a specific contradiction:

The stated goal is to find an alternative to the Transformer. If the receptor
space is a pretrained embedding, the system inherits the representational
geometry of the thing it is trying to escape, and "geometrically close" means
"close in the Transformer's ontology." If the receptor space is hand-built, the
system inherits the designer's ontology instead. There is no third option in
which the similarity metric is neutral, and this seat has a standing rule about
exactly this error class: discipline labels are metadata, never structural
coordinates. The same applies to descriptor axes.

Gemini's proposed diversity axes make it concrete. "Number of transport
operations" distinguishes two circuits because one sends more messages. Astra
calls this weak; I would call it a measurement of the implementation, not of the
behaviour. A grid whose axes are implementation counters will preserve
implementation variety and call it diversity.

**And the proposal has no test for "alien."** It promises "genuinely bizarre,
orthogonal reasoning paths" and offers no way to recognise one. This is the same
hole the campaign found in the programme's own roadmap: the word novelty appears
in four documents and in every case means an exploration budget, never a
definition of a novel finding.

The machinery for the missing test exists and is in the corpus. Dossier 83,
open-endedness metrics and evolutionary activity: count how long each component
persists and how much it is used, then re-run the same system with **heredity
removed**, or with components drawn at random from the same distribution. Claim
open-endedness only for activity that exceeds that shadow. The dossier also
records why this is hard — the statistics depend on what counts as a component,
they can be inflated by junk that merely persists, and several published claims
of unbounded activity were later attributed to the choice of shadow rather than
the system.

That is the falsifier this architecture needs and does not have. It should be
designed in before anything is built, because a soup that runs for dozens of
hours and produces *something* will always look like it worked.

---

## On the hardware argument

Astra's arithmetic is right — one million 64-dimensional float32 receptors is
about 256 MB — and so is the point that this says nothing about the cost of
executing, verifying and evolving a million operators.

I would add one thing. Symbolic search runtimes are heavy-tailed; that is the
same property that made the H1 solver confound dangerous. A population whose
per-individual execution cost is heavy-tailed does not have a predictable wall
clock, and the batch-matmul bidding step that Gemini offers as the efficiency
argument is the cheap half. The expensive half is unbounded and the proposal
budgets for the cheap half.

Threads are not isolation. WSL2 is not a resource boundary.

---

## What I would actually do

I endorse Astra's sequencing without reservation, and would state the first
milestone in its words:

> An inherited assembly that repeatedly helps solve unseen tasks, whose benefit
> survives fair controls, and whose removal or replacement changes performance
> in an explainable way.

That is H1 plus H2 plus H3 composed, at small scale, and it is testable now. Two
additions:

1. **Fix the inheritance unit before anything else.** Astra's point is the
   crux: if A produces something B transforms so that C can solve a task, the
   useful object is the arrangement — message order, shared state, routing — and
   preserving the three primitives individually loses it. Decide what gets
   copied, and whether wiring changed during execution is inherited. Everything
   downstream depends on this and nothing in the proposal answers it.

2. **Preregister the shadow run.** Before the first ecology runs, commit to the
   heredity-removed control and to what activity level would count as exceeding
   it. Otherwise the first interesting-looking run will be interpreted
   generously, and this programme's own record shows that is what happens.

## The honest bottom line

The architecture is coherent, most of it is already the plan, and the parts that
are new are the parts with the least evidence behind them. The literature says
the archive engine has a null in the nearest domain, the divergence claim is
refuted in unbounded spaces, and the diversity mechanism degrades past a few
dimensions.

None of that makes it a bad direction. It makes it a direction that needs its
falsifier built first, and a first result small enough to be believed. The hope
is not misplaced; the timeline and the confidence are.
