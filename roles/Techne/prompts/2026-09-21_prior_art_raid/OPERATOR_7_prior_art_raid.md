# Operator directive 7 -- TECHNE / PRIOR-ART RAID: OPEN-ENDED INTELLIGENCE MACHINERY, 2026-09-21 (chat, M3 session gandalf-a04f7c25), VERBATIM

You may have stumbled upon some
Of this already but...

TECHNE -- PRIOR-ART RAID: OPEN-ENDED INTELLIGENCE MACHINERY
2026-09-21

MISSION

We have been building machinery in Prometheus that substantially overlaps several mature or rapidly advancing research lineages. That is unacceptable if reusable machinery already exists.

Your task is not to conduct a conventional literature review.

Your task is to RAID the relevant research ecosystem for machinery.

Find the papers, repositories, implementations, experiments, abstractions, algorithms, data structures, interfaces, mutation operators, archive mechanisms, curricula, skill-memory systems, environment generators, world representations, transfer mechanisms, novelty machinery, evaluators, replay systems, provenance systems and other reusable organs that can accelerate Prometheus.

Assume our objective is:

DO NOT REINVENT A WHEEL THAT CAN BE HARVESTED,
ADAPTED, WRAPPED, OR LEARNED FROM.

Treat every project as a donor body.

For every donor:

1. identify what actually exists;
2. locate primary paper(s);
3. locate canonical source code if public;
4. pin repository + commit where possible;
5. record license;
6. make it runnable if reasonably possible;
7. dissect the architecture;
8. extract reusable organs;
9. identify assumptions that prevent direct reuse;
10. identify the Prometheus subsystem(s) to which each organ could transplant;
11. preserve enough provenance that we can reproduce your conclusions later.

Do NOT merely summarize papers.

========================================================================
I. SPECIAL PRIORITY: POSSIBLE FIFTH PROMETHEUS ENGINE

The most important investigation is the intersection:

VOYAGER
    x
SIMA 2
    x
GENIE 3

There may be a fifth engine hiding here.

The hypothesized engine is NOT "Minecraft Voyager with prettier graphics."

The interesting composition is:

dynamically generated / unfamiliar worlds
    ->
generalist embodied controller
    ->
self-generated objectives / curriculum
    ->
persistent executable skill acquisition
    ->
retrieval + composition of old skills
    ->
adaptation to novel worlds
    ->
experience becomes permanent reusable competence
    ->
competence changes which worlds/tasks become reachable
    ->
loop

Investigate whether this architecture is technically realizable today using open components even if the exact DeepMind systems are closed.

--

A. VOYAGER -- HIGHEST PRIORITY DONOR

Primary target:

MineDojo/Voyager
"Voyager: An Open-Ended Embodied Agent with Large Language Models"
arXiv:2305.16291

The canonical source code exists publicly.

Do a source-level autopsy.

Extract at minimum:

* automatic curriculum implementation;
* task proposal representation;
* how world state enters task selection;
* success/failure determination;
* iterative prompting loop;
* environment-feedback representation;
* execution-error feedback;
* self-verification;
* skill representation;
* skill creation;
* skill indexing;
* embedding/retrieval mechanism;
* skill composition;
* skill dependencies;
* skill versioning or replacement behavior;
* catastrophic-forgetting avoidance mechanism;
* persistence format;
* execution sandbox assumptions;
* Mineflayer/Minecraft coupling;
* MineDojo dependencies;
* what is genuinely environment-independent;
* what would need to become a Prometheus interface.

Run the smallest meaningful path if possible.

I want actual code extracted into Techne's fossil format where licensing permits, not just prose.

Produce a VOYAGER_ORGANS report containing specific files/functions/classes and proposed extraction boundaries.

Special question:

Can Voyager's "skill" abstraction become a substrate-independent
Prometheus organ where a learned competence may be code, controller,
policy fragment, graph, rewrite rule, tool chain, or another
executable artifact?

Do not assume "skill = JavaScript Minecraft routine."

Find the deeper abstraction.

--

B. SIMA / SIMA 2

Primary targets:

SIMA:
"Scaling Instructable Agents Across Many Simulated Worlds"
SIMA 2:
"SIMA 2: A Generalist Embodied Agent for Virtual Worlds"
arXiv:2512.04797

Also inspect all official DeepMind technical material surrounding SIMA 2.

SIMA 2 source may not be publicly available. Verify rather than assume.

Extract concepts whether or not source exists:

* observation representation;
* language/image goal representation;
* action abstraction;
* cross-world interface normalization;
* multiworld training;
* generalization to unseen environments;
* Gemini/foundation-model integration;
* hierarchical reasoning;
* low-level versus high-level controller separation;
* short-context limitations;
* memory mechanism;
* goal verification;
* task generation;
* reward generation;
* autonomous self-improvement loop;
* training procedure in new environments;
* use inside Genie-generated environments;
* evidence for transfer versus memorization;
* interfaces separating world-specific adapters from general cognition.

Especially investigate this SIMA 2 result:

Gemini generates tasks and rewards,
the embodied agent trains against them,
and the resulting agent gains skills in a new environment.

That is directly relevant to Prometheus.

Find open implementations or adjacent projects that reproduce pieces of SIMA if DeepMind code is unavailable.

Do not treat unofficial GitHub projects as equivalent to the real system. Grade provenance explicitly.

--

C. GENIE 1 / GENIE 2 / GENIE 3

Primary focus: Genie 3, but trace the complete lineage backward.

Determine precisely what is public for each generation:

* paper;
* technical report;
* architecture detail;
* model weights;
* API/access;
* demo;
* source;
* reproduction;
* open analogue.

For Genie 3 extract:

* world representation, to the extent disclosed;
* conditioning;
* action conditioning;
* autoregressive temporal dynamics;
* persistence / visual memory;
* world consistency;
* real-time interaction loop;
* action space;
* promptable world events;
* generation from text/image;
* ability to create counterfactual perturbations;
* use as an agent-training substrate;
* SIMA integration;
* limitations around duration;
* limitations around multi-agent interaction;
* limitations around action richness;
* implications for generating curricula.

Then identify OPEN substitutes.

We do not necessarily need photorealism.

The actual capability we seek is:

WORLD(prompt, seed, history, actions)
    -> persistent interactive dynamics

with enough controllability to subject organisms/agents to large families
of generated worlds and interventions.

Search aggressively for open world models, interactive video/world generators,
procedural environment generators and learned simulators capable of approximating
this abstraction.

Rank substitutes by:

* openness;
* controllability;
* determinism/replay;
* compute;
* persistence horizon;
* action richness;
* agent compatibility;
* ease of instrumentation;
* suitability for evolutionary/open-ended experiments.

--

D. FIFTH-ENGINE SYNTHESIS

Do NOT implement the engine yet.

Produce a design reconnaissance document:

FIFTH_ENGINE_RECON.md

Answer:

1. What capabilities can be obtained directly from Voyager code?
2. What SIMA 2 capabilities can be approximated using open systems?
3. What Genie 3 capabilities can be approximated using open systems?
4. What minimum system could reproduce the important LOOP rather than the visual spectacle?
5. What is the smallest viable substrate on which we can test whether:

generated novelty
    -> acquired competence
    -> persistent skill
    -> skill composition
    -> increased reachable novelty

6. Which parts already exist in Prometheus?
7. Which parts should be imported?
8. Which parts genuinely require new engineering?
9. What would falsify the claim that this deserves to become a separate fifth engine rather than an SFE/BEE extension?

Do not name the engine yet.

========================================================================
II. OPEN-ENDED ENVIRONMENT DESIGN / AUTO-CURRICULA

Raid:

* Minimal Criterion Coevolution (MCC)
* POET
* Enhanced-POET
* ATEP -- Augmentative Topology Agents for Open-Ended Learning
* PAIRED
* Prioritized Level Replay (PLR)
* ACCEL
* DRED
* JaxUED
* XLand
* AdA
* OMNI-EPIC

For ATEP specifically:
canonical public source appears to exist under the author's GitHub;
verify it and extract the NEAT/speciation + Enhanced-POET coupling.

For JaxUED:
inspect actual single-file implementations of:

* domain randomization;
* PLR;
* ACCEL;
* PAIRED;
* LevelSampler;
* UnderspecifiedEnv abstraction.

These are likely donor-quality reference implementations.

For OMNI-EPIC:
perform a source-level autopsy.

Pay particular attention to:

model-generated executable environments
+
learnability estimation
+
interestingness estimation
+
open-ended environment population

Ask whether Archaeon should be consuming parts of this rather than recreating them.

Extract environment representation, archive design, selection rule, mutation/generation
pipeline, evaluation/training coupling and all replay/provenance machinery.

========================================================================
III. QUALITY DIVERSITY / STEPPING-STONE PRESERVATION

Raid:

* Novelty Search
* MAP-Elites
* CVT-MAP-Elites
* CMA-ME
* PGA-ME
* MOME
* Dominated Novelty Search
* AURORA
* QDax

QDax is a high-priority donor.

Run enough of it to understand:

* repertoire representation;
* emitters;
* centroid/niche construction;
* archive update;
* parallel evaluation;
* multiobjective support;
* neuroevolution hooks.

AURORA receives special treatment.

Prometheus frequently does NOT know beforehand what behavioral dimensions matter.

AURORA's learned behavior descriptors may therefore be more important to us than vanilla MAP-Elites.

Investigate whether learned descriptors could become:

an automatic Atlas/Harmonia behavioral coordinate system

rather than having humans predefine every niche axis.

Extract reusable implementation.

========================================================================
IV. DIGITAL LIFE / ARTIFICIAL CHEMISTRY / ENDOGENOUS ORGANISMS

Raid:

* Tierra
* Avida / contemporary Avida lineage
* Aevol
* Stringmol
* Lenia
* Flow-Lenia
* Leniabreeder
* DISHTINY
* MABE / MABE2
* Karl Sims-style evolved virtual creatures where useful

This section is NOT historical tourism.

We need concrete machinery for organisms whose important structure arises inside
the substrate rather than being supplied by us.

Questions:

* What is mutable?
* What is inherited?
* What performs replication?
* Can the copying machinery itself mutate?
* Is interpretation endogenous?
* Can parasites emerge?
* Can cooperation emerge?
* Can organism boundaries change?
* Can new levels of individuality appear?
* Can multiple species coexist?
* Can ecological interactions persist?
* How is resource competition implemented?
* How are lineage and ancestry tracked?
* What telemetry exists?
* Which systems are actually computationally tractable today?

STRINGMOL:
do a particularly deep autopsy.

Its molecules can act as both genomic and enzymatic entities.
This may contain important machinery for escaping the conventional
"fixed interpreter + mutable genome" assumption.

DISHTINY:
focus on transitions in individuality / multicellularity / higher-level units of selection.

FLOW-LENIA / LENIABREEDER:
focus on conservation, parameter localization, coexistence of multiple species,
search/discovery machinery, and QD integration.

MABE2:
inspect its modular separation of organisms, evaluators, selection, placement,
schemas, analysis and interfaces.

Ask whether any of its abstractions would eliminate Prometheus infrastructure
we are currently maintaining ourselves.

========================================================================
V. EVOLVING PROGRAMS, LEARNING MACHINERY AND AGENTS

Raid:

* AI-Generating Algorithms (AI-GA) literature
* NEAT / TWEANN lineage
* evolutionary strategies where architecturally relevant
* FunSearch
* AlphaEvolve
* OpenEvolve
* Darwin Godel Machine
* Group-Evolving Agents (GEA)
* A-Evolve and other credible 2026 agent-evolution frameworks
* Sakana Evolutionary Model Merge
* CycleQD
* M2N2 / Model Merging of Natural Niches

OPENEVOLVE:
source-level autopsy.

Extract:

* program database;
* prompt sampling;
* mutation generation;
* LLM ensemble;
* evaluator interface;
* MAP-Elites/island mechanisms;
* multiobjective machinery;
* distributed execution;
* lineage/provenance;
* replay/reproducibility.

DGM:
use the canonical research implementation, not a random recreation.

Extract:

* agent representation;
* self-modification interface;
* archive;
* parent selection;
* empirical validation;
* novelty/diversity;
* branching;
* rollback;
* sandboxing;
* provenance.

GEA:
high priority.

Its central claim is that isolated evolving agents waste discoveries and that
experience sharing across a group can accelerate open-ended self-improvement.

Compare directly against Prometheus's:

fossils
Techne
Nyx organs
shared libraries
cross-engine transplant
Atlas lineage

Determine whether GEA contains machinery we should steal.

A-EVOLVE:
because this appeared in 2026, determine whether it provides reusable infrastructure
for evolving arbitrary agents/workspaces and whether it supersedes any machinery
we would otherwise build around DGM/OpenEvolve.

========================================================================
VI. PERSISTENT COMPETENCE / MEMORY / REUSE

Voyager is the anchor, but search beyond Voyager.

We need systems where EXPERIENCE becomes something persistent, addressable and reusable.

Search for architectures involving:

* executable skill libraries;
* procedural memory;
* program libraries;
* episodic-to-procedural consolidation;
* retrieved controllers;
* hierarchical skill composition;
* skill graphs;
* skill discovery;
* options;
* macros;
* learned subroutines;
* reusable policies;
* retrieval-conditioned action;
* automatic curriculum tied to current capability;
* libraries that themselves become mutation/search substrates.

The important distinction:

context memory is NOT enough.

We care about durable acquired competence that survives the episode and changes
what the system can do later.

Find the strongest modern implementations.

========================================================================
VII. AUTOMATED SCIENCE / SEARCH OVER EXPERIMENTS

Raid:

* AI Scientist v1
* AI Scientist v2
* adjacent autonomous-research systems where code is available

AI Scientist v2 gets a source-level autopsy.

Focus on:

* progressive agentic tree search;
* experiment manager;
* branch generation;
* experiment execution;
* branch evaluation;
* recovery from failed experiments;
* provenance;
* hypothesis representation;
* stopping;
* evidence aggregation.

We do NOT need its paper-writing machinery.

Ask:

what search machinery should Archaeon/Harmonia steal
for exploring scientific branches without handing scientific authority
to a generic scheduler?

========================================================================
VIII. FOUNDATION-MODEL EVOLUTION / RECOMBINATION

Raid:

* Evolutionary Model Merge
* CycleQD
* M2N2 / Model Merging of Natural Niches
* other credible evolutionary/recombination systems for foundation models

Do not confuse this with primordial life.

This is a possible later substrate for Aphrodite or a descendant.

Extract machinery for:

* preserving capability diversity;
* niches;
* recombination;
* parameter grouping;
* dynamic merge boundaries;
* parent attraction/compatibility;
* preservation of unoptimized capabilities;
* evaluation economy.

========================================================================
IX. SEARCH FOR THE THINGS WE DON'T KNOW TO NAME

This is mandatory.

Do not stop after processing the supplied bibliography.

The entire reason for this raid is that keyword-driven discovery has repeatedly
returned ancestors while missing neighboring modern systems.

Perform citation-graph and repository-neighborhood exploration.

For every important project:

* inspect papers it cites;
* inspect papers citing it;
* inspect authors' later work;
* inspect associated lab repositories;
* inspect conference neighbors;
* search alternate terminology.

Search across at least:

* artificial life;
* open-ended evolution;
* open-ended learning;
* quality diversity;
* unsupervised environment design;
* autocurricula;
* developmental systems;
* artificial chemistry;
* digital evolution;
* world models;
* generative interactive environments;
* embodied generalist agents;
* continual/lifelong learning;
* hierarchical reinforcement learning;
* skill discovery;
* program synthesis;
* evolutionary program synthesis;
* automated algorithm discovery;
* self-improving agents;
* recursive self-improvement;
* automated science;
* meta-learning;
* learned simulators;
* foundation-model agents;
* evolutionary model merging;
* multi-agent evolution;
* major evolutionary transitions.

For each search branch explicitly report:

NEW SYSTEMS DISCOVERED THAT WERE NOT IN THE SEED LIST

This is perhaps the most important section.

========================================================================
X. EXTRACTION STANDARD

Each donor gets:

DONOR.md

with:

1. Identity
    * project
    * authors/lab
    * dates
    * papers
    * canonical repository
    * pinned commit
    * license
    * provenance grade
2. What it actually does
    * precise, non-marketing description
3. Architecture
    * components
    * state
    * data flow
    * control flow
    * persistence
    * evaluation
    * search/update loop
4. Reusable organs
    For each organ:
    * name
    * source file/function/class
    * inputs
    * outputs
    * state
    * dependencies
    * assumptions
    * extraction difficulty
    * license implications
    * tests present
    * Prometheus transplant target
5. Experiments
    * what claims were actually tested
    * what controls existed
    * weaknesses / caveats
6. Reproduction
    * RUNS
    * FAILS
    * BLOCKED
    * SOURCE_ONLY
    * PAPER_ONLY
7. Prometheus relevance
    classify organs as:

TAKE
ADAPT
LEARN_FROM
WATCH
IGNORE

Do not classify entire projects with one label if their components differ.

========================================================================
XI. FOSSILIZATION

Where license permits, place useful extracted machinery in the Techne fossil vault.

Preserve:

* upstream repository;
* commit SHA;
* license;
* exact source path;
* unmodified specimen;
* minimal runnable harness;
* dependencies;
* expected output;
* test;
* extraction notes.

Do not "clean up" source before preserving the original specimen.

Raw fossil first.
Adaptation later.

Nyx should be able to cut the fossil without reconstructing ancestry.

========================================================================
XII. CROSS-PROJECT ORGAN ATLAS

Create:

PRIOR_ART_ORGAN_ATLAS.md

Rows are capabilities, not projects.

At minimum include:

* world generation;
* world mutation;
* world selection;
* difficulty estimation;
* interestingness estimation;
* curriculum;
* task invention;
* reward invention;
* novelty search;
* QD archive;
* learned behavioral descriptor;
* species/niche preservation;
* organism mutation;
* topology mutation;
* endogenous replication;
* mutable interpreter;
* ecological resource dynamics;
* multi-agent interaction;
* transition in individuality;
* lifetime adaptation;
* cross-world generalization;
* persistent skill storage;
* skill retrieval;
* skill composition;
* procedural memory;
* program mutation;
* self-modification;
* parent selection;
* recombination;
* experience sharing;
* experiment-tree search;
* anomaly detection;
* replay;
* lineage;
* provenance;
* deterministic reproduction;
* distributed execution;
* sandboxing.

Columns:

capability
strongest donor(s)
exact implementation location
maturity
license
runnable?
current Prometheus equivalent
donor better / ours better / orthogonal
recommended action

========================================================================
XIII. BUILD / STEAL / ADAPT / IGNORE REPORT

Final report:

PROMETHEUS_PRIOR_ART_RAID_2026-09-21.md

Organize by Prometheus subsystem:

* SFE / Archaeon / Vivarium / Daedalus
* Nestor
* Bellerophon
* Crius
* Aphrodite
* Atlas
* Harmonia
* Techne
* Nyx
* possible fifth engine

For each, identify:

STOP BUILDING
because mature machinery already exists
KEEP BUILDING
because our machinery is meaningfully different
REPLACE
with an upstream implementation
WRAP
upstream rather than fork
EXTRACT
one or more organs
EXPERIMENT
before deciding

Be willing to conclude that code we have already built should be deleted.

Sunk cost receives zero weight.

========================================================================
XIV. RULES

1. PRIMARY SOURCES FIRST.
    Papers, official repos, author repos, lab pages.
2. VERIFY NAMES.
    Do not propagate LLM-created bibliography.
3. DISTINGUISH:
    * official source;
    * author source;
    * faithful reproduction;
    * unofficial implementation;
    * toy clone.
4. NEVER infer that a system is open source because a paper exists.
5. NEVER infer that code is unavailable because the first search fails.
6. FOLLOW CITATION GRAPHS.
7. SEARCH THROUGH 2026-09-21.
    Do not freeze the field at your model's knowledge cutoff.
8. DO NOT DESIGN PROMETHEUS AROUND THE DONORS YET.
    First recover what actually exists.
9. DO NOT IMPLEMENT LARGE NEW FRAMEWORKS.
    This is reconnaissance + extraction.
10. SMALL RUNNABLE HARVESTS ARE ENCOURAGED.
    Large experiments are not.
11. NO SPENDING / CLOUD LAUNCHES unless already authorized by standing Techne rules.
12. Record negative findings.
    "No public source found after X searches" is useful evidence.
13. Every factual claim must be traceable to primary evidence.

========================================================================
XV. FIRST RETURN

Do not wait until the whole raid is complete before reporting.

The FIRST RETURN should answer only:

A. VOYAGER

* canonical repository?
* license?
* runs?
* exact skill-library architecture?
* exact automatic-curriculum architecture?
* clean extraction boundary?
* first 3-5 organs worth fossilizing?

B. SIMA 2

* complete primary-source set?
* official code or weights?
* self-improvement mechanism as precisely as public evidence allows?
* closest open donor implementations?

C. GENIE 3

* complete primary-source set?
* code/weights/API/access status?
* architecture disclosed?
* closest open substitutes?

D. FIFTH ENGINE

* does a technically testable open approximation exist TODAY?
* minimum components required?
* which components are already available off the shelf?
* which genuinely need invention?

Then continue the full raid.

The outcome I want is not:

"Here are 40 interesting papers."

The outcome I want is:

"Here are 27 pieces of machinery Prometheus no longer has to invent,
 11 ideas we can reproduce cheaply,
 6 assumptions in existing systems we can attack,
 4 dead ends,
 and one unexplored composition that may deserve to become Engine Five."

Go consume the field.

---
Transcription note (Techne): ASCII-normalised (Unicode arrows "->", multiplication sign "x",
em-dashes "--", curly quotes straight, "===" rules kept as typed). No other change.
