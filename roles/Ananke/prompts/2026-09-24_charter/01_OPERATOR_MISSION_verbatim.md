Here’s your mission:

You are taking ownership of a new Prometheus Physics of Intelligence experiment.

Core question

Test the following deliberately minimal thesis:

Can cognitive-like organization emerge from asynchronous, lossy packet traffic propagating through a mutable tensor substrate, without importing conventional neural-network architecture?

The motivating abstraction is:

Intelligence may be describable as packets of state/information moving through a high-dimensional mutable medium, where the medium changes how future packets are routed, transformed, remembered, suppressed, amplified, or emitted.

A deliberately provocative shorthand is:

UDP packets broadcast over a tensor.

Do not treat that phrase literally as a networking implementation. Treat it as an instruction to strip away familiar cognitive machinery and test the smallest possible communication physics from which organized information processing might emerge.

The packet itself is not presumed intelligent.

The hypothesis is that interesting behavior, if it exists, arises from the coupled dynamics of:

packet traffic × local state × topology × memory × adaptation × environmental pressure.

⸻

1. Scientific posture

This is not a request to design a novel neural network.

Do not begin with:

* transformers;
* attention;
* backpropagation;
* gradient descent;
* MLPs;
* RNN/LSTM equivalents;
* graph neural networks;
* reservoir computing templates;
* predictive coding;
* active inference;
* cellular automata copied from known literature;
* standard multi-agent reinforcement learning;
* existing artificial-life architectures.

Those may later serve as fossils or controls, but they are not the substrate.

Avoid allowing LLM priors to silently recreate known architectures under renamed variables.

If a mechanism resembles known machinery, record the resemblance after the fact. Do not use that resemblance as a design target.

The experiment should make it genuinely possible for the search to discover something awkward, ugly, unfamiliar, or difficult to classify.

⸻

2. Go directly to GPU tensor execution

Do not spend a phase building a CPU prototype merely to prove the idea runs.

Prometheus already has GPU test patterns and RunPod operational experience.

Build the actual experimental substrate around GPU tensor execution from the start.

Primary execution should use an appropriate GPU tensor framework already supported by the repository/environment. Prefer the simplest backend that gives us:

* large batched worlds;
* deterministic replay where requested;
* explicit RNG control;
* efficient tensor operations;
* sparse/local communication where useful;
* profiling;
* memory telemetry;
* throughput telemetry;
* checkpoint/restart;
* GPU digest/conformance testing.

A tiny CPU reference implementation is permissible only if required for an independent correctness oracle, not as the experimental implementation and not as a preliminary campaign.

Design for local GPU development and RunPod scaling immediately.

Reuse existing Prometheus RunPod packaging/deployment/test infrastructure wherever practical. Do not require publishing a container to a public registry if the existing Aether/AGE machinery provides another route.

⸻

3. Minimal substrate

Start with a population/lattice/field represented primarily as GPU tensors.

Each site has local mutable state.

Each tick or event permits sites to receive zero or more packets, transform their state, and possibly emit packets.

The initial substrate should contain only machinery necessary to express the following physics.

Site state

Each site has a compact state vector.

Do not assume the semantic meaning of dimensions.

Possible state components may include:

* persistent scalar/vector state;
* short-term mutable registers;
* packet-generation state;
* routing/gating state;
* adaptation/plasticity variables;
* optional energy/resource state.

Keep this minimal and parameterized.

Packets

Packets should initially be extremely simple.

Candidate packet fields:

* payload vector;
* source identity or source-local metadata, optionally absent;
* age / TTL;
* amplitude;
* channel/type, optionally absent;
* destination mode.

Do not add fields unless an experiment requires them.

Communication

Communication laws must themselves be experimental variables.

Possible regimes include:

* local neighborhood broadcast;
* radius-limited broadcast;
* stochastic recipient selection;
* global broadcast;
* sparse directed routing;
* topology-defined neighbors;
* dynamic routing;
* packets diffusing through intermediate sites;
* packets competing for bounded bandwidth.

Loss should be a first-class dial, not merely an implementation accident.

So should latency.

So should packet collisions/contention if practical.

The system should tolerate:

* lost packets;
* delayed packets;
* duplicate packets;
* out-of-order arrival;
* noisy payloads.

These properties are scientifically interesting.

Local update law

A site’s state transition should be generated from compact primitive operations rather than a conventional learned block.

Build a small operator vocabulary from things such as:

* addition/subtraction;
* multiplication;
* threshold/comparison;
* modulo/wrap;
* clipping;
* mixing/permutation;
* bitwise or integer operations where useful;
* local tensor reductions;
* stochastic transforms;
* simple nonlinearities;
* state reads/writes;
* packet-field reads;
* emission decisions.

The exact primitive vocabulary is itself part of the experimental design.

Prefer primitives that permit alien machinery to exist.

Avoid silently implementing a neural layer.

Adaptation

At least some runs must allow the substrate to modify its own future communication/update behavior.

Potential mechanisms:

* local mutation;
* state-conditioned rule selection;
* writable routing tables;
* writable operator parameters;
* packet-mediated rule modification;
* inheritance/reproduction if endogenous replication later becomes relevant.

Do not assume gradient learning.

⸻

4. World and pressure

A bare communication medium may produce nothing but noise.

Give it pressures that require information to move through space/time.

Start with several qualitatively different environment families rather than one benchmark.

Examples:

Temporal prediction

Information appears in one region/time and useful action must occur elsewhere/later.

Distributed control

No single site has enough information to choose the globally useful action.

Delayed causal intervention

The system must preserve useful information over a gap before acting.

Changing mappings

Input/action relationships change across episodes, creating pressure for adaptation rather than static lookup.

Spatially separated evidence

Several remote signals must somehow be combined.

Generalization / transfer

The system experiences related but nonidentical environments and is tested on withheld variants.

Communication-cost world

Packets consume finite resources so indiscriminate broadcast becomes expensive.

Do not make all pressures simultaneous initially.

Use distinct worlds to determine what different communication physics support.

⸻

5. The dials

The primary purpose of this engine is to spin many physically meaningful dials and expose new surface area.

At minimum, make these experimentally variable:

* number of sites;
* site-state dimensionality;
* substrate dimensionality/shape;
* neighborhood topology;
* communication radius;
* packet fan-out;
* packet-loss probability;
* packet latency distribution;
* payload width;
* bandwidth limits;
* packet TTL;
* noise/corruption;
* state persistence/decay;
* state-update frequency;
* asynchronous vs synchronous updates;
* adaptation rate;
* routing plasticity;
* mutation rate;
* communication cost;
* memory cost;
* local compute cost;
* environmental change rate;
* environmental spatial scale;
* environmental temporal scale.

Add additional dials only when scientifically justified.

Every dial must be recorded in machine-readable receipts.

⸻

6. We care about phase transitions, not merely scores

Do not optimize solely for maximum task reward.

The central scientific objective is to identify qualitative regime changes.

Examples:

* a threshold where persistent memory suddenly appears;
* a region where information propagates farther than direct packet range;
* spontaneous routing or gating;
* stable modular communication;
* persistent internal variables predictive of future conditions;
* compression of repeated environmental structure;
* learned use of silence/non-transmission;
* temporal credit across long delays;
* reusable internal machinery;
* transfer across environmental perturbations;
* behavior robust to packet loss;
* behavior that improves when communication is costly;
* self-maintaining communication structures;
* hierarchical organization;
* endogenous division of labor;
* creation of new communication channels/protocols;
* representation-like state that survives substrate transplantation.

These are examples, not targets to engineer.

Create detectors capable of flagging unexpected discontinuities in observable behavior as substrate parameters vary.

A strong result would look like:

Below region R, only local reactive behavior occurs.
Across boundary B, persistent distributed state appears.
Above B, systems can solve delayed/remote-control problems, and the capability survives controlled perturbations.

That is more valuable than “reward improved 8%.”

⸻

7. Do not define intelligence too early

Do not gate the search on human-looking behavior.

For this first campaign, treat candidate cognitive organization operationally.

Look for evidence of systems that:

1. acquire information from experience;
2. preserve or transform useful information through time;
3. combine information unavailable to an individual local component;
4. exploit that internal organization to control future outcomes;
5. adapt when environmental mappings change;
6. reuse internal structure across related circumstances.

A useful higher-order candidate is:

experience compressed into reusable internal structure that improves control under changed conditions.

Do not declare that intelligence has been found.

Use graded evidence.

⸻

8. Measurements

Instrument the substrate aggressively.

We should be able to reconstruct what happened after a surprising run.

Record, where feasible:

* task performance;
* information propagation distance;
* temporal persistence;
* packet traffic volume;
* packet entropy;
* packet diversity;
* channel diversity;
* communication sparsity;
* spatial information flow;
* mutual/predictive information proxies;
* causal influence under perturbation;
* state dimensionality/rank proxies;
* effective memory horizon;
* topology evolution;
* routing concentration;
* packet survival;
* state turnover;
* adaptation magnitude;
* local vs distributed contribution;
* energetic/resource expenditure;
* robustness under packet deletion;
* robustness under site deletion;
* robustness under state corruption;
* transfer performance;
* intervention effects.

Do not let expensive metrics dominate every run. Separate cheap continuous telemetry from expensive adjudication assays.

⸻

9. Falsification and controls

Build controls before interpreting positive-looking behavior.

At minimum include:

* shuffled packet destinations;
* shuffled packet timing;
* payload randomization;
* packet ablation;
* state-memory ablation;
* adaptation disabled;
* frozen routing;
* zero communication;
* maximal-loss communication;
* identical environment with irrelevant packet channels;
* environmental permutation tests;
* independent seed replication.

If behavior remains after the mechanism thought responsible is destroyed, the explanatory claim fails.

For promoted candidates, add causal interventions rather than relying on correlations.

⸻

10. Transplants

Prometheus cares deeply about whether machinery is actually doing something reusable.

For sufficiently interesting candidates, attempt transplantation such as:

* internal-state transplant into a fresh substrate;
* routing-rule transplant;
* packet protocol transplant;
* local update-law transplant;
* topology transplant;
* partial-component transplant;
* transplantation into modified world physics;
* transplantation into altered environment family.

Test whether the candidate mechanism transfers, collapses, or depends on hidden context.

A mechanism that survives a principled transplant is much more interesting than one that only exists inside one frozen run.

⸻

11. Search strategy

Do not perform a naive Cartesian sweep of every dial.

Use a staged exploration strategy.

A reasonable structure is:

Wave A — broad substrate census

Large numbers of cheap runs spanning radically different communication regimes.

Purpose: identify living regions, dead regions, unstable regions, and discontinuities.

Wave B — boundary search

Concentrate compute around interesting discontinuities.

Purpose: determine whether apparent phase boundaries reproduce.

Wave C — pressure diversification

Expose promising substrate regions to different environmental pressures.

Purpose: determine whether machinery is generic or benchmark-specific.

Wave D — causal adjudication

Run ablations, interventions, transplants, and replays.

Purpose: determine what actually caused the interesting behavior.

Wave E — scale probe

For the strongest surviving regions, increase world size, duration, heterogeneity, or population substantially on RunPod.

Purpose: determine whether the phenomenon strengthens, disappears, or changes character with scale.

You may improve this structure before freezing the preregistration.

⸻

12. GPU/RunPod scaling

Design batching from the beginning so that thousands of independent worlds can run concurrently when memory permits.

Measure:

* worlds/sec;
* site-updates/sec;
* packet-events/sec;
* GPU utilization;
* memory/site;
* memory/world;
* wall time;
* checkpoint cost;
* telemetry cost;
* dollars per million site-updates;
* dollars per promoted candidate;
* dollars per adjudicated anomaly.

Use these measurements to guide scale.

If early results show promise, scale outward quickly rather than protecting an undersized implementation.

The scientific substrate should not be constrained to laptop-scale convenience.

⸻

13. Campaign duration and autonomy

Once implementation, tests, preflight, and preregistration are complete, launch a substantial autonomous campaign.

Target roughly 12–24 hours of independent experimental work if available compute and cost are reasonable.

Do not stop the campaign to ask the operator whether individual anomalies look interesting.

The campaign should:

* explore;
* detect;
* promote;
* replay;
* falsify;
* branch around boundaries;
* run controls;
* gather telemetry;
* checkpoint;
* produce a final evidence package.

No human-in-the-loop steering should be required after campaign launch unless there is an infrastructure/safety failure that genuinely prevents continuation.

⸻

14. Pre-registration

Before the first scientific campaign, write and commit a preregistration specifying:

* substrate definition;
* primitive operator vocabulary;
* packet semantics;
* mutable state semantics;
* environment families;
* search ranges;
* anomaly detectors;
* promotion thresholds;
* falsification tests;
* transplant criteria;
* phase-boundary criteria;
* stopping conditions;
* interpretation vocabulary.

Use conservative labels.

Suggested result states:

* NULL;
* SIGNAL;
* REPRODUCED_SIGNAL;
* CAUSAL_SUPPORT;
* TRANSFER_SUPPORT;
* PHASE_BOUNDARY_CANDIDATE;
* PHASE_BOUNDARY_SUPPORTED;
* INCONCLUSIVE.

Do not use “intelligence discovered” as a machine-generated verdict.

⸻

15. Reproducibility and forensic integrity

Every run must be recoverable from receipts.

Record:

* code commit;
* configuration;
* seed;
* backend;
* hardware;
* package versions where relevant;
* experiment/world version;
* primitive-set version;
* RNG scheme;
* campaign parent;
* mutations;
* artifacts;
* hashes;
* telemetry;
* termination reason.

Interesting candidates must be replayable exactly where determinism permits.

Where GPU nondeterminism is unavoidable, document it and define numerical/reproduction tolerances ahead of interpretation.

⸻

16. Code quality

Build this as reusable Prometheus engine machinery rather than a notebook.

Expected qualities:

* clean module boundaries;
* configuration-driven worlds;
* reusable GPU runner;
* campaign scheduler;
* checkpointing;
* receipts;
* anomaly/promotion pipeline;
* controls;
* transplant assay framework;
* structured reports;
* unit tests;
* GPU conformance tests;
* crash-resume tests.

Do not overengineer abstractions before the first campaign, but do not create a throwaway implementation.

⸻

17. Anti-gravity constraint

This project explicitly wants to discover mechanisms we would not have designed ourselves.

Therefore:

Do not optimize the search toward known cognitive architectures.

Search space construction should maximize mechanistic diversity while remaining computationally tractable.

When selecting primitives, pressures, mutations, or search proposals, prefer:

* mechanisms generated by the substrate itself;
* unexplained anomalies;
* discontinuities;
* failed transfers;
* unexpected robustness;
* unexpected fragility;
* strange packet economies;
* strange topology changes;
* disagreement between metrics;
* behaviors that defeat our classifier.

Novelty should not mean cosmetic difference from existing architectures.

It should mean different causal machinery.

⸻

18. First deliverables

Proceed autonomously through these stages:

1. Inspect the Prometheus repository and identify reusable GPU, RunPod, telemetry, receipt, checkpoint, and campaign infrastructure.
2. Commit this directive verbatim as the originating operator instruction.
3. Write the seat/engine charter.
4. Design the minimal packet-tensor substrate.
5. Write the preregistration before scientific search.
6. Implement GPU-native execution.
7. Implement tests and independent correctness/conformance checks.
8. Run GPU smoke/conformance tests.
9. Run a small scientific preflight only to verify reachability, instrumentation, and runtime health—not to tune for positive results.
10. Freeze the campaign.
11. Launch the autonomous campaign.
12. Allow anomaly-triggered replay/control/adjudication inside the campaign.
13. Scale promising regions using RunPod where justified.
14. Produce a final report including negative results.
15. Prepare Atlas-compatible exports/evidence pointers if Atlas ingestion conventions exist in the repo.

Do not wait for operator feedback between these stages unless completely blocked by credentials, infrastructure failure, or an ambiguity that makes proceeding scientifically invalid.

When choices are underdetermined, make a defensible choice, record it, and continue.

⸻

19. What success looks like

Success is not necessarily solving a benchmark.

Any of the following would make the campaign worthwhile:

* a reproducible communication-dependent phase transition;
* emergence of persistent distributed memory;
* a packet protocol not explicitly designed by us;
* spontaneous routing/gating;
* adaptive communication under cost;
* transferable state machinery;
* robust information integration under packet loss;
* a surprising relationship between memory, bandwidth, latency, topology, and control;
* a strong NULL result excluding a broad region of substrate physics;
* discovery that one apparently essential mechanism is actually unnecessary;
* discovery of an unexpected new dial that controls qualitative behavior.

The highest-value result would be evidence for something like:

There exists a reproducible region of communication/substrate parameter space in which otherwise simple components spontaneously organize information across space and time into reusable machinery that improves adaptive control.

Do not assume that region exists.

Find out.

⸻

20. North star

The long-term goal is not to prove that “UDP over tensors is intelligence.”

It is to begin constructing an empirical phase diagram of possible intelligence.

Treat this engine as an experimental instrument for asking:

Under what physical/computational laws does organized information processing become possible, persist, adapt, transfer, and eventually acquire properties we would recognize as cognition?

Build the instrument.

Then turn the dials.
