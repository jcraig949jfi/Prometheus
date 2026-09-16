PROMETHEUS MECHANISM ARCHAEOLOGY PIPELINE

Founding Charter

TECHNE → NYX → HARMONIA → THEOPHRASTUS → ARCHAEON / VIVARIUM → SOUP

0. PURPOSE

Prometheus will systematically recover computational experiments, algorithms, implementations, mechanisms, and experimental artifacts from the history of science and computation; make them reproducible; decompose them into experimentally addressable machinery; expose that machinery to pressures and worlds unavailable to the original researchers; map its failure and interaction geometry; and admit experimentally interesting residues into an evolutionary substrate where larger reasoning organisms may consume, combine, mutate, discard, or repurpose them.

The objective is not preservation for its own sake.

The objective is not to reproduce famous algorithms.

The objective is not to prove that old ideas were secretly correct.

The objective is:

Strip-mine the history of computation for experimentally reusable reasoning machinery.

Many historical experiments were constrained by hardware, simulation cost, storage, instrumentation, datasets, compiler environments, and the number of trials a researcher could afford.

Prometheus operates under a different assumption:

An experiment that could be sampled at five points when it was invented may eventually be sampled at five million, five billion, or more.

Therefore the historical record is not exhausted.

It is an unexplored experimental landscape.

⸻

1. THE LONG HORIZON

Prometheus is being built before exhaustive reasoning-space exploration is economically possible.

That is intentional.

The near-term product is not a complete map of reasoning.

The near-term product is the machinery required to construct that map later:

* immutable provenance;
* canonical mechanism identities;
* reproducible worlds;
* resurrection environments;
* executable modern surrogates;
* intervention semantics;
* standardized observables;
* failure vectors;
* ancestry;
* negative results;
* interaction records;
* sparse experimental coordinates;
* replayable experiments.

Future compute must make Prometheus cheaper to interrogate, not merely larger.

A result recorded in 2026 is not doctrine.

It is a coordinate that future machinery must be able to reopen, surround with millions of neighboring measurements, falsify, refine, or reinterpret.

⸻

2. THE FUNDAMENTAL UNIT

Prometheus does not primarily accumulate algorithms.

It accumulates mechanisms under pressures.

A mechanism may originate inside:

* an optimization algorithm;
* theorem prover;
* compression system;
* operating system;
* numerical method;
* search procedure;
* evolutionary system;
* scheduler;
* control system;
* database;
* game-playing program;
* symbolic algebra package;
* scientific simulation;
* machine-learning architecture;
* biological model;
* failed research program.

Historical names are provenance.

They are not ontology.

A mechanism extracted from a 1984 optimizer may eventually have more in common experimentally with a memory-control mechanism from a 2018 theorem prover than with the rest of its original algorithm.

Prometheus must be capable of discovering that.

⸻

3. PIPELINE LAW

Every stage consumes the evidence produced upstream and adds evidence.

No stage silently rewrites the history of the object.

The canonical chain is:

FOSSIL
  │
  ▼
TECHNE
acquisition + provenance
  │
  ▼
NYX
dissection + mechanism extraction
  │
  ▼
HARMONIA
reproduction + resurrection + equivalence
  │
  ▼
THEOPHRASTUS
landscape expansion + damage geometry
  │
  ▼
ARCHAEON / VIVARIUM
composition + ecology + selection
  │
  ▼
SOUP
experimentally characterized machinery
available for future organisms

Each transition is a gate.

A downstream stage may reject an upstream object.

Rejection is evidence.

Failure is not pipeline waste.

⸻

4. TECHNE — THE GATHERER

Mission

Techne finds and acquires potentially useful computational fossils.

Techne does not determine whether a fossil contains an important mechanism.

Techne establishes:

What is this thing, where did it come from, and what survived?

Techne searches broadly.

Targets may include celebrated systems, obscure implementations, abandoned software, failed experiments, forgotten papers, unusual control structures, old benchmarks, research code, binaries, datasets, test suites, experimental notebooks, and machinery that was never fully explored.

Techne seeks

Whenever available:

* source;
* binaries;
* compiler and interpreter versions;
* operating-system requirements;
* architecture requirements;
* libraries;
* datasets;
* seeds;
* configuration;
* test vectors;
* expected outputs;
* papers;
* documentation;
* historical bug reports;
* known failures;
* benchmarks;
* execution traces;
* author commentary.

Absence is recorded, never silently repaired.

Techne produces

A FOSSIL PACKET.

Minimum identity:

fossil_id
artifact hashes
provenance
source location
historical date / version where known
associated literature
available execution material
missing material
license / redistribution constraints
acquisition confidence

Where practical:

environment recipe
known invocation
known input/output pairs
historical benchmark
dependency inventory
runtime capsule candidate

Techne must not

* claim scientific importance;
* infer mechanisms as established facts;
* modernize the artifact;
* silently replace missing components;
* discard failed acquisition attempts;
* promote famous systems preferentially merely because they are famous.

Techne gathers.

⸻

5. NYX — THE DISSECTOR

Mission

Nyx breaks acquired fossils into experimentally addressable pieces.

Nyx asks:

What machinery appears to exist inside this thing?

Nyx does not need to know whether the machinery is useful.

Nyx does not prove resurrection.

Nyx does not rewrite the artifact into modern form.

Nyx searches for

* mechanisms;
* state transitions;
* control structures;
* memory structures;
* routing decisions;
* update rules;
* search policies;
* pruning policies;
* persistence mechanisms;
* recovery behaviors;
* assumptions;
* hidden coupling;
* parameter dependencies;
* boundaries;
* feedback loops;
* implementation quirks;
* recurrent structures;
* possible pressure responses.

A strange lookup table is not “cruft” until experimentation establishes that.

A bug is not irrelevant merely because it was unintended.

Implementation accidents may themselves contain mechanisms.

Nyx produces

MECHANISM CANDIDATES

Each candidate carries:

mechanism_id
fossil_id
location / ancestry
description
observed implementation
suspected function
candidate boundaries
candidate pressure sensitivities
possible interventions
confidence
supporting evidence

PRESSURE HYPOTHESES

Examples:

sparse feedback
delayed feedback
adversarial ambiguity
memory scarcity
deceptive objective
distribution shift
resource starvation
noisy observation
partial observability
branch explosion
premature commitment

INTERVENTION SURFACES

Nyx identifies places where causal experimentation may be possible:

remove
replace
freeze
randomize
delay
amplify
attenuate
duplicate
invert
constrain
perturb

Nyx must not

* declare a mechanism useful because it looks clever;
* treat recurrence as validation;
* silently reinterpret historical behavior;
* construct an improved descendant and call it reproduction;
* promote a candidate directly into the Soup.

Nyx performs anatomy.

⸻

6. HARMONIA — THE RESURRECTOR

Mission

Harmonia makes the fossil experimentally alive again and produces a fast modern surrogate whose relationship to the fossil is explicitly measured.

Harmonia asks:

Can we make the historical system run, and can we construct a modern instrument that demonstrably preserves the behavior we care about?

Harmonia exists because interpretation and verification must remain separated.

Nyx may hypothesize what a mechanism does.

Harmonia establishes what can actually be reproduced.

⸻

HARMONIA R0 — HISTORICAL REPRODUCTION

Can the historical artifact execute?

Possible substrates include:

native execution
OCI container
virtual machine
QEMU
architecture emulator
historical operating system
historical interpreter
historical compiler
preserved disk image
compatibility layer

Docker is an implementation option.

It is not the abstraction.

The abstraction is the Fossil Runtime.

Required interface conceptually resembles:

instantiate(fossil)
execute(fossil, input)
observe(fossil)
intervene(fossil, change)
snapshot(fossil)
destroy(instance)

⸻

HARMONIA R1 — BEHAVIORAL RESURRECTION

Harmonia constructs a behavioral oracle from the historical executable.

The oracle may contain:

* input/output pairs;
* traces;
* convergence behavior;
* timing-independent state sequences;
* failure conditions;
* invariants;
* edge cases;
* numerical tolerances;
* pathological cases;
* randomized trials;
* adversarial cases.

A modern implementation is then subjected to differential testing.

historical(input_n) → observation A
modern(input_n)     → observation B

Agreement and disagreement are recorded.

No disagreement may disappear by editorial decision.

⸻

HARMONIA R2 — MECHANISM RESURRECTION

Where experimentally possible, Harmonia tests whether the modern implementation preserves not merely outputs but the mechanism identified by Nyx.

This can include:

* ablation;
* substitution;
* causal intervention;
* internal-state comparison;
* branch behavior;
* perturbation response.

A modern system that mimics the outputs while implementing unrelated machinery is behaviorally useful but must not be falsely labeled mechanistically equivalent.

⸻

Harmonia produces

A RESURRECTION PACKET:

fossil_id
mechanism_id(s)
historical_runtime
runtime_hashes
historical reproduction result
oracle corpus
oracle hashes
modern surrogate
surrogate hashes
behavioral equivalence results
mechanistic equivalence evidence
divergence ledger
known unsupported regions
performance characteristics
replay instructions

Harmonia’s hard law

Improvement and resurrection are different experiments.

Harmonia may discover an improvement.

It must first preserve the faithful branch.

Only afterward may a divergent descendant be created.

The ancestry must remain explicit:

historical fossil
       │
       ├── faithful modern surrogate
       │
       └── divergent descendants

Harmonia builds experimental instruments.

⸻

7. THEOPHRASTUS — THE CARTOGRAPHER

Mission

Theophrastus takes resurrected mechanisms and pushes them into landscapes their original creators could not economically explore.

Theophrastus asks:

Where does this mechanism work, fail, recover, interact, bifurcate, become pathological, or behave unexpectedly?

The target is not a leaderboard.

The target is behavioral geometry.

⸻

Experimental coordinate

A conceptual cell may be represented as:

[
T[m,p,w,b,i,t,\dots]
]

where:

m = mechanism
p = pressure
w = world
b = branch / composition
i = intervention
t = timescale

Additional dimensions may be introduced only when operationally defined.

Each measured cell may contain:

survival
damage
recovery
performance
resource cost
stability
interaction
sensitivity
failure mode
novel behavior
uncertainty

An empty cell means:

NOT MEASURED

Never:

probably false

⸻

Theophrastus explores

mechanism
× pressure
× world
× branch
× intervention
× seed
× scale
× timescale

But brute-force enumeration is not required.

Sampling may become:

* adaptive;
* novelty-directed;
* uncertainty-directed;
* boundary-seeking;
* failure-frontier seeking;
* interaction-seeking.

The sampling policy itself must remain experimentally auditable.

⸻

Damage geometry

Theophrastus gives special attention to the geometry of failure.

Not merely:

PASS
FAIL

but:

where failure begins
how rapidly damage grows
whether damage is reversible
which perturbations move the boundary
which mechanisms shift the surface
where multiple failure surfaces intersect

The intersection of failure surfaces may be more informative than isolated success.

A weak signal can therefore be:

Mechanism D consistently shifts the shared failure boundary of unrelated mechanisms A, B, and C.

That may warrant downstream ecological testing even if D is mediocre in isolation.

⸻

Theophrastus produces

MEASURED CELLS carrying full ancestry.

Each cell must retain:

mechanism identity
surrogate identity
world identity
pressure identity
intervention identity
seed / randomness identity
observations
failure vector
controls
uncertainty
replay information

Theophrastus maps.

⸻

8. ARCHAEON / VIVARIUM — THE ECOLOGY

Mission

Archaeon and Vivarium stop treating mechanisms as historical artifacts and begin treating them as biological material.

They ask:

What happens when experimentally characterized machinery is allowed to coexist, compete, combine, mutate, disappear, reappear, and become incorporated into larger reasoning organisms?

A mechanism’s historical name becomes secondary.

Its measured behavior becomes primary.

⸻

Archaeon

Archaeon operates on evolutionary possibility.

It may:

* assemble mechanisms;
* create descendants;
* mutate connections;
* alter routing;
* alter composition;
* branch lineages;
* test inheritance;
* expose organisms to selection pressures.

Its mutations are proposals.

They are not judgments.

⸻

Vivarium

Vivarium provides worlds and ecological conditions in which organisms must live.

Selection arises from explicit environments and measurements.

Not from model preference.

Not from aesthetic judgment.

Not from human expectation of what intelligence ought to look like.

Vivarium records:

* survival;
* resource use;
* adaptation;
* extinction;
* reproduction;
* specialization;
* interaction;
* transfer;
* unexpected persistence.

⸻

9. THE SOUP

The Soup is not a junk drawer.

It is a provenance-bearing reservoir of experimentally characterized machinery available for future composition.

A mechanism does not enter because:

* it is famous;
* it is elegant;
* a paper says it worked;
* Nyx finds it interesting;
* Harmonia reproduced it;
* an LLM likes it.

It enters because experimentation produced sufficiently interesting residue.

Possible admission signals include:

* unusual failure geometry;
* repeatable recovery behavior;
* robust cross-world effect;
* interaction with unrelated mechanisms;
* damage-surface displacement;
* regime-specific advantage;
* unexpected resource behavior;
* persistence under pressure;
* complementary failure geometry;
* causal effect established by intervention.

Weak signals are allowed.

They must be labeled weak.

⸻

Soup record

A Soup mechanism should resemble:

MECH-2197
ancestry:
    fossil F-883
    Nyx fragment N-441
    Harmonia surrogate H-119
behavior:
    retains low-frequency evidence across local failure
observed pressures:
    sparse reward
    delayed feedback
    deceptive landscape
damage geometry:
    ...
interactions:
    synergistic MECH-1402
    antagonistic MECH-0188
    unknown MECH-7711
world support:
    ...
failures:
    ...
controls:
    ...
evidence class:
    weak / replicated / causal / blind / etc.
replay:
    ...

The Soup stores machinery plus evidence, not claims stripped from ancestry.

⸻

10. CONSTITUTIONAL RULES

C1 — PROVENANCE NEVER BREAKS

Every descendant points backward.

No modernization erases its fossil.

No composition erases its mechanisms.

No mechanism erases its experimental cells.

⸻

C2 — FAILURE IS PRIMARY DATA

A failure boundary may be more scientifically valuable than a successful benchmark.

Negative experiments remain first-class records.

⸻

C3 — INTERPRETER AND VERIFIER REMAIN SEPARATE

Nyx may hypothesize.

Harmonia must independently establish reproduction and equivalence.

Theophrastus must independently measure landscapes.

⸻

C4 — NO SILENT NORMALIZATION

Historical quirks, numerical differences, undefined behavior, implementation accidents, missing dependencies, and divergences are recorded.

They are not cleaned away merely because modern engineering practice dislikes them.

⸻

C5 — EMPTY IS NOT FALSE

Unmeasured experimental space remains explicitly unmeasured.

⸻

C6 — REPRODUCTION IS NOT PROMOTION

A successfully resurrected algorithm has earned the right to be experimented on.

Nothing more.

⸻

C7 — FAME PROVIDES NO PRIOR

Historically celebrated and historically obscure mechanisms enter under the same experimental rules.

⸻

C8 — NO LLM AS SELECTOR

LLMs may:

* search;
* summarize;
* propose;
* mutate;
* decompose;
* suggest interventions;
* generate implementations.

They do not determine experimental truth.

Selection rests on reproducible downstream measurement.

⸻

C9 — BRANCH BEFORE IMPROVEMENT

Before changing a resurrected mechanism, preserve the faithful branch.

Every improvement becomes a descendant.

⸻

C10 — THE PIPELINE MUST SCALE WITH FUTURE COMPUTE

Instrumentation must support experiments much larger than those affordable at design time.

Do not encode today’s computational scarcity as tomorrow’s scientific ontology.

⸻

11. STATE MACHINE

Canonical lifecycle:

ACQUIRED
   ↓
FOSSIL
   ↓
DISSECTED
   ↓
MECHANISM_CANDIDATE
   ↓
HISTORICALLY_REPRODUCED
   ↓
BEHAVIORALLY_RESURRECTED
   ↓
MECHANISTICALLY_TESTED
   ↓
LANDSCAPE_MEASURED
   ↓
WEAK_SIGNAL / NEGATIVE / INTERESTING
   ↓
SOUP_ADMITTED
   ↓
ORGANISM_CONSUMED
   ↓
LINEAGE

Objects may terminate at any stage.

Termination is not failure of the pipeline.

The terminated object itself becomes evidence.

⸻

12. FIRST END-TO-END PILOT

Do not begin by collecting another thousand fossils.

Prove the pipe.

Use the existing Nyx gzip level-table target.

Techne

Freeze the exact gzip fossil and all currently known provenance.

Required output:

FOSSIL-GZIP-001

No new scientific interpretation required.

⸻

Nyx

Freeze its existing anatomical claim around the level-table mechanism.

Produce:

MECH-GZIP-LEVELTABLE-001

Specify:

* exact code boundary;
* hypothesized behavior;
* proposed ablation;
* candidate pressures;
* known uncertainties.

Do not change the hypothesis after seeing Harmonia results.

⸻

Harmonia

H0

Instantiate the historical implementation.

H1

Build an oracle corpus.

H2

Construct the smallest modern experimental surrogate justified by the fossil.

H3

Run differential tests.

H4

Produce a divergence ledger.

H5

Verify that the level-table intervention can be expressed identically or equivalently on fossil and surrogate.

Deliver:

RESURRECTION-GZIP-001

⸻

Theophrastus

Run the first intentionally small landscape:

mechanism:
    gzip level-table
intervention:
    intact / ablated / altered
pressures:
    small frozen set
worlds:
    small frozen set
seeds:
    frozen
objective:
    locate behavioral boundaries,
    NOT demonstrate superiority

Populate real tensor cells.

Find at least one of:

stable region
failure boundary
null result
interaction
unexpected behavior

A null result is acceptable.

⸻

Archaeon / Vivarium

Only if Theophrastus produces an admissible signal:

remove the historical label.

Present the mechanism as behavior plus interface.

Create at least one organism capable of consuming it.

Run it in a controlled Vivarium world.

Compare:

without mechanism
with mechanism
ablation after incorporation

⸻

Soup

If the mechanism earns admission, create the first complete lineage:

FOSSIL
→ NYX MECHANISM
→ HARMONIA RESURRECTION
→ THEOPHRASTUS CELLS
→ VIVARIUM ORGANISM
→ SOUP RECORD

That record becomes the reference specimen for every subsequent pipeline implementation.

⸻

13. LAUNCH ORDER

Effective immediately:

TECHNE

Continue gathering, but prioritize completeness of fossil packets over volume for candidates likely to reach resurrection.

NYX

Continue Stage A/B dissection.

Do not block dissection on execution infrastructure.

Send resurrection candidates downstream rather than absorbing resurrection into Nyx.

HARMONIA

ESTABLISH NOW.

Initial charter:

Reproduce historical computational artifacts, construct faithful modern experimental surrogates, establish behavioral and where possible mechanistic equivalence, maintain explicit divergence ledgers, and deliver fast replayable instruments downstream without silently improving the originals.

First specimen:

Nyx gzip level-table fossil.

THEOPHRASTUS

Accept only sufficiently reproducible instruments for expensive landscape mapping.

Begin with small frozen maps before widening combinatorially.

ARCHAEON / VIVARIUM

Do not consume historical fame or prose descriptions.

Consume experimentally characterized mechanisms.

SOUP

Create the canonical admission schema before volume arrives.

⸻

14. NORTH STAR

Prometheus is not trying to guess the architecture of reasoning.

It is constructing an experimental system in which possible reasoning machinery can eventually be generated, recovered, dissected, reproduced, perturbed, composed, pressured, falsified, and selected at scales that are currently impractical.

The wager is simple:

When the compute exists to explore the combinatorial space of reasoning circuitry, the scarce resource should no longer be instrumentation.

Build that instrumentation now.

Then let future compute fill the map.
