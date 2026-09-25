AETHER — NATIVE CIRCUITRY ROUND

Use the current qualified aeth01.v1 implementation and existing First Light evidence.

Start by reading:

* Aether/AETH-01/FIRST_LIGHT_01_2026-09-22.md
* current Observatory / requirements / economics / habitability docs
* the GPU memory-optimization receipt
* the terminology contract

Purpose

First Light showed that coarse spatial organization is mostly absent and that the balanced regime remained unresolved at tick 5,000.

The next question is NOT:

Did Aether make an organism?

It is:

Does Aether spontaneously produce persistent functional circuitry — distributed causal graphs that carry state, route resources, transmit changes, or alter later behavior?

We are still walking before running.

Do not add selection pressure or reward circuitry yet.

First learn what Aether naturally produces.

⸻

TRACK 1 — FINISH THE BALANCED TRAJECTORY

Extend the existing B-balanced regime to approximately 50,000 ticks.

Prefer continuing/reproducing the exact First Light conditions rather than inventing new ones.

Measure whether B:

* reaches a fixed point;
* asymptotically slows;
* continues changing indefinitely;
* undergoes a late regime transition;
* develops increasingly structured causal interactions.

Record the same First Light observables so the trajectory is directly comparable.

Also add:

* GPU memory over lifetime;
* tick latency over lifetime;
* artifact growth;
* deterministic replay spot-checks.

Do not stop early merely because the trajectory appears boring.

⸻

TRACK 2 — CAUSAL GRAPH OBSERVATORY

Instrument actual successful interactions.

For each relevant event, capture enough information to reconstruct a temporal causal edge:

source site -> target site

with at least:

* tick;
* source coordinate;
* target coordinate;
* target field;
* written/transferred value where appropriate;
* arbitration outcome;
* whether the edge changed target state;
* source/target resource state where useful.

Do not dump an impossibly large raw edge stream if unnecessary.

Use bounded aggregation / sampling / sparse forensic capture while preserving exact replay pointers.

Construct time-windowed functional graphs and measure things such as:

* active node count;
* edge count;
* degree distributions;
* strongly connected components;
* component persistence;
* recurring edges;
* recurring motifs;
* fan-in / fan-out;
* bottlenecks;
* path lengths;
* graph modularity/community structure where meaningful;
* resource-flow subgraphs;
* state-write subgraphs;
* cross-field coupling;
* persistence of topology across windows.

The physical lattice is local.

The object of interest is the functional graph produced over time.

Do not assume interesting circuitry must be spatially compact.

⸻

TRACK 3 — SEARCH FOR STATEFUL CIRCUITS

Look for candidate subgraphs whose future behavior depends on their prior state.

Examples of evidence worth flagging:

* recurrent subgraphs with multiple persistent states;
* delayed responses;
* activity that propagates and later returns;
* modules whose output differs after different prior inputs;
* resource-routing patterns that persist longer than individual edges;
* one subgraph modifying the later connectivity/activity of another.

Do not call these “memory”, “communication”, “control”, etc. from appearance alone.

Use neutral labels such as:

PERSISTENT_SUBGRAPH_CANDIDATE

STATE_DEPENDENCE_CANDIDATE

LONG_RANGE_PROPAGATION_CANDIDATE

RESOURCE_ROUTING_CANDIDATE

until intervention establishes function.

⸻

TRACK 4 — PERTURBATION / COUNTERFACTUAL ASSAY

For the strongest naturally occurring graph candidates, perform cheap replay-based counterfactuals.

Examples:

* perturb/remove one node or small subgraph;
* alter a candidate source state;
* break one high-betweenness edge-producing site;
* replay with an otherwise identical world.

Ask:

Does downstream behavior measurably change beyond the local mechanical consequence?

Look for:

* loss of a persistent graph motif;
* changed distant activity;
* changed resource routing;
* changed future state distribution;
* recovery/reconstruction;
* delayed causal effects.

Use matched controls with equivalent perturbations outside the candidate graph.

This is the important filter:

Weak effects are acceptable. Mechanically trivial effects are not.

⸻

TRACK 5 — SUB-LATTICE FORENSICS

First Light’s coarse block statistics may miss sparse circuitry.

Retain at least one full-resolution 256×256 window per selected world over meaningful intervals.

Choose windows without cherry-picking whenever possible; preregister the selection rule.

Use them to inspect:

* fine-scale causal topology;
* persistent interaction motifs;
* local state transitions;
* repeated routing patterns.

If an anomaly detector selects an additional window, preserve that separately and label it as detector-selected rather than preregistered.

⸻

DETERMINISM CHECK

Run one moderate world — approximately 512² for 5,000 ticks — through both CPU and GPU implementations if practical.

Compare a full or sufficiently dense digest series.

Goal:

establish long-horizon CPU/GPU determinism, not just one-tick replay and seven-tick small-world agreement.

Any divergence is an engineering blocker and stops scientific interpretation.

⸻

NO STEERING YET

Do not reward:

* loops;
* SCCs;
* modularity;
* persistence;
* resource routing;
* “memory”;
* communication;
* graph complexity.

Those measurements are observational in this round.

We specifically want to avoid evolving structures that merely game our newly constructed detector.

At the end, however, identify 2–4 capability-level pressures that might later be appropriate.

Examples of acceptable future pressure concepts:

* retain distinguishable state after an input disappears;
* transmit state influence across distance;
* recover function after partial disruption;
* route resource more efficiently under changing demand.

Do NOT implement them yet.

⸻

COMPUTE

Use the already-qualified RunPod/A40 path.

Budget:

up to $3 total, one Pod at a time.

Prioritize time and replicated trajectories over maximum lattice size.

4096² is likely sufficient for the main long-duration work unless measurement shows otherwise.

Terminate cleanly and verify zero active Pods.

⸻

OUTPUT

Create:

Aether/AETH-01/NATIVE_CIRCUITRY_01_2026-09-23.md

Separate explicitly:

OBSERVED

Direct measurements only.

INTERVENTION RESULTS

Matched perturbation/counterfactual evidence.

INTERPRETATION

Mechanistic explanations supported by the above.

REJECTED INTERPRETATIONS

Interesting-looking signals explained by trivial transition mechanics.

HYPOTHESES

What deserves another test.

FUTURE LIGHT PRESSURES

Capabilities we might eventually reward, without prescribing architecture.

Report especially:

* what happened to B by tick 50,000;
* whether persistent functional subgraphs exist;
* whether any candidate graph shows state dependence;
* whether any long-range causal propagation exists;
* whether perturbing candidate circuitry has nonlocal consequences;
* whether fine-resolution windows reveal structure invisible to coarse statistics;
* long-run CPU/GPU determinism;
* runtime stability and actual cost.

If nothing survives the counterfactual tests, say so clearly.

That is useful evidence.

Do not redesign aeth01.v1 during this round.

Do not add steering during this round.

First discover Aether’s native circuitry.
