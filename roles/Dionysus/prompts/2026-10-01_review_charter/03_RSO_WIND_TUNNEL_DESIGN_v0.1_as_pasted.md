Recursive Sagacity Observatory v0.1
Prometheus Phase 3 "Wind Tunnel" Design
1. Central decision
Prometheus Phase 3 should not begin by attempting to build a single machine called the Recursive Sagacity Engine.
Instead, it should build a Recursive Sagacity Observatory (RSO): a common experimental environment in which many candidate computational/developmental architectures can be subjected to the same worlds, pressures, resource accounting, causal interventions, transfer assays, search-power tests, and claim rules.
The analogy is a wind tunnel.
A wind tunnel does not tell us what the best race car must look like. It provides controlled physical conditions and measurement so that radically different designs can be compared without rebuilding the science around each car.
Prometheus v1/v2 repeatedly did the opposite. Individual engines tended to bring their own organism representation, world, search, ruler, interpretation, and sometimes their own definition of success. That made cross-engine agreement weak and nulls difficult to interpret.
The Phase 3 objective is therefore dual:
Build the wind tunnel and the candidate race cars in parallel.

The observatory without candidate architectures risks becoming a sterile metrology project.
Candidate architectures without the observatory risk repeating v1/v2.
2. Scientific target
The core Phase 3 question is:
Under what combinations of computational substrate, developmental rules, environmental history, and selection pressure does it become advantageous and reachable for an initially limited organism to construct increasingly reusable internal or extended cognitive machinery during its lifetime?

The recursive extension is:
Under what conditions does constructed machinery causally improve the process that constructs later learning machinery?

Phase 3 does not assume that recursive sagacity exists, that it lies outside broad meta-learning, that it resembles human cognition, that it requires neural networks, that it requires symbolic programs, that it requires a sharp organism/world boundary, or that any legacy Prometheus engine already contains the relevant physics.
Those become experimental questions.
3. Experimental object
The primitive scientific object is a registered developmental cell:
\[
C = (\Phi, B, W, D, P, S, M, R)
\]
where:
- \(\Phi\): computational/developmental physics or substrate;
- \(B\): cognitive boundary condition;
- \(W\): world/environment family;
- \(D\): developmental history or curriculum;
- \(P\): selection/evolution/lifetime pressure;
- \(S\): search/generation process;
- \(M\): measurement/intervention stack;
- \(R\): resource envelope.
The explicit addition of \(B\), cognitive boundary condition, comes from Gemini's criticism of an implicit Cartesian organism/world split.
A claim is always conditional on a cell.
A result must never silently change from:
"not detected in this registered cell under this resource budget"

into:
"the phenomenon does not exist."

4. Five qualification questions
Before a negative result about a phenomenon becomes meaningful, the observatory must answer five distinct questions.
4.1 CAPACITY
Can the physical substrate instantiate the target phenomenon at all?
A directly constructed positive supplies a lower bound on capacity. It does not establish developmental reachability.
4.2 DEMAND
Does the world genuinely require the target capability rather than a cheaper strategy?
Demand should be established by exact policy bounds where possible and by progressively stronger adversarial baseline classes where exact enumeration is impossible.
4.3 REACH
Can the allowed search/developmental process reach qualifying machinery from the registered initial distribution?
This is a property of:
\[
\text{substrate representation}
\times
\text{mutation/search operator}
\times
\text{developmental path}
\times
\text{budget}.
\]
It is not synonymous with capacity.
4.4 DETECTION
Can the ruler reliably identify known positives, known negatives, neutral/intermediate cases, and known cheats?
Ruler qualification requires reachable positive and negative outputs and measured error in the operating regime.
4.5 DEVELOPABILITY
Can the capability be constructed during a lifetime under the permitted physics and developmental history rather than merely inserted into the initial state?
For strong developmental nulls, all five matter.
5. Developmental coordinates
Retain Fable's useful functional coordinates without turning them into built-in modules.
HOLD
Information persists beyond immediate fast state.
ADAPT
Experience changes later behavior.
BUILD
Experience constructs persistent machinery that is subsequently used.
COMPRESS
Multiple experiences become reusable predictive/causal machinery that reduces future cost.
COMPOSE
Constructed machinery becomes material for constructing additional machinery.
RECURSE
Constructed machinery improves the process that constructs subsequent learning machinery.
These are coordinates for measurement, not a required linear ladder and not an ontology inserted into the organism.
6. Organism protocol
The RSO should define a substrate-neutral organism protocol.
Every participating substrate must expose:
- inherited material;
- fast/temporary state;
- persistent lifetime state;
- native developmental changes;
- observations;
- actions;
- resource use;
- scientific checkpoint/state representation;
- intervention hooks;
- provenance sufficient for the registered claim.
The protocol must not assume pointers, registers, modules, global addresses, synchronized clocks, explicit beliefs, hypothesis slots, attention, working-memory buffers, planners, confidence variables, or symbolic procedures.
Those may emerge or exist in particular candidate architectures, but they are not part of the universal experimental contract.
7. Reality and observation planes
Gemini correctly identifies a danger: measurement can modify the dynamics it claims to observe.
The RSO should therefore separate a Reality Plane from an Observation Plane.
Reality Plane
The authoritative execution dynamics.
The Reality Plane should contain only the instrumentation required for deterministic or statistically qualified execution, minimal resource metering, event emission, causal intervention, and snapshot/checkpoint semantics appropriate to the physics.
Observation Plane
An out-of-band or minimally coupled process that consumes canonical events and performs indexing, lineage reconstruction, ruler computation, dashboards, expensive mechanism analysis, and offline model interpretation.
The observatory must qualify observer non-interference.
For deterministic systems:
\[
\text{instrumented outcome} = \text{uninstrumented outcome}
\]
where exact equality is meaningful.
For stochastic, asynchronous, or continuous systems, use a declared statistical or dynamical equivalence contract.
8. Execution classes
Do not require every substrate to fit lock-step deterministic simulation.
Support at least:
E0 -- Discrete deterministic
Bit-exact or declared numerical replay.
E1 -- Discrete stochastic
Keyed randomness; reproduction of seeded trajectories and distributional results.
E2 -- Asynchronous event-driven
Causal event records, partial-order constraints, deterministic scheduling where available, otherwise distributional replay.
E3 -- Continuous or chaotic numerical dynamics
Qualified integrator, error envelope, state-observation map, trajectory/distribution equivalence, explicit sensitivity to perturbation and numerical precision.
"Snapshot" therefore means:
scientifically sufficient state representation for the declared physics

rather than necessarily byte-identical RAM.
9. Cognitive boundary as an experimental variable
The original design implicitly treated the organism as the sole location of cognitive construction.
Gemini's stigmergy criticism should change this.
Define controlled retained-state channels:
- \(I\): internal organism-retained structure;
- \(E\): environment-written persistent structure;
- \(S\): social/distributed retained structure.
Experimental conditions can allow:
\[
I,\ E,\ S,\ I+E,\ I+S,\ E+S,\ I+E+S.
\]
The question becomes:
Where does useful cognitive organization choose to live under different cost structures?

External memory is not automatically cheating.
A system that invents writing, stigmergic marks, social memory, or tool-mediated cognition may be discovering a more economical cognitive architecture.
This creates an additional Phase 3 scientific axis:
Is sagacity primarily an internal organism property, or can it reside in a progressively reconstructed cognitive niche?

10. Substrate strategy
The three independent architects disagree mainly about how much physical diversity to build early.
The synthesis is:
Specify several physical families now, deeply implement one first, bring up a small unlike shadow substrate early, then activate additional full substrates when they answer a discriminating question.

The observatory must never silently become Track-A-specific merely because Track A was easiest to build.
A proposed rule:
No interface should be called substrate-neutral until it has operated correctly on at least two materially different physical realizations.

Candidate architectures are specified separately in 02_RACE_CAR_PORTFOLIO_R0-R9.md.
11. World program: W0 / W1 / W2
Gemini correctly identifies a "Regime I capability trap": a tiny exact world may make deep development economically irrational.
The correction is not to abandon calibration worlds. Instead use three world regimes.
W0 -- Calibration worlds
Small environments with exact or exhaustive truth, known demand, known-positive organisms, known-negative organisms, known cheats, and strong leak detection.
Purpose:
qualify the wind tunnel.

W0 is not expected to induce recursive sagacity.
W1 -- Demand-transition worlds
Parameterized families where a cheap inherited/reactive solution is initially optimal but becomes progressively less economical.
Parameters may include number of latent contexts, delay, environmental diversity, lifetime length, inherited-information budget, composition depth, hidden-law turnover, and observation cost.
Purpose:
identify transition surfaces where development begins to pay.

W2 -- Developmental universes
Long-horizon environments where exact enumeration is impossible but cheap policy classes can still be bounded aggressively.
They may contain partial observability, delayed consequences, reusable causal structure, compositional problems, tool construction/use, environmental change, costly information, irreversible action, other agents, ecological dependence, persistent environmental state, and curricula emerging from world dynamics.
Purpose:
create enough developmental ecology for richer cognition to be economically useful.

W2 can include adversarial demand generators, but these do not replace W0 known-truth qualification.
12. Adversarial demand generation
Gemini's strongest proposed change to the world system is to make demand grow rather than remain static.
Adopt this in W1/W2.
A demand generator should increase difficulty only through registered dimensions. For example:
\[
d = (H, L, C, V, I, Q)
\]
where:
- \(H\): hidden-state depth;
- \(L\): temporal delay/lifetime depth;
- \(C\): compositional depth;
- \(V\): causal/environmental variability;
- \(I\): irreversibility;
- \(Q\): information cost.
The generator should seek conditions where the current cheap baseline family fails while a qualified known-positive family remains capable.
This produces a demand frontier, not an arbitrary escalating benchmark.
Do not let organism performance directly define the world in a way that creates a private handshake between generator and learner. Keep third-party/sealed world families and foreign-generator checks.
13. Search geometry is first-class physics
Gemini's "Reachability Desert" critique should become a formal requirement.
For each substrate/search combination, measure:
- viable mutation fraction;
- beneficial mutation fraction;
- neutral mutation fraction;
- catastrophic/sterile mutation fraction;
- connected neutral component size;
- target rediscovery rate by scaffold distance;
- sensitivity to representation;
- mutation-operator locality;
- recombination usefulness;
- stepping-stone density.
Define a search-power surface:
\[
R(d,B)=P(\text{recover target}\mid\text{scaffold distance }d,\text{budget }B).
\]
A search failure is interpretable only relative to this measured surface.
This directly incorporates lessons from Proteus and other v1/v2 search failures.
14. Scaffold descent
Retain Fable's strongest proposal and Gemini's endorsement.
Start from a known-working organism.
Progressively remove scaffolding.
At each level:
- freeze what was removed;
- characterize edit/structural distance;
- measure target rediscovery;
- test multiple search operators;
- identify whether intermediate states are selectable;
- record resource cost.
This turns "emergence" into an empirical distance from known functionality.
It also supports bottom-up search by telling us which distances are realistically bridgeable.
15. Compression
Cognitive compression is not merely smaller state.
A qualifying result should show:
\[
\text{many experiences}
\rightarrow
\text{reusable predictive/causal machinery}
\]
with reduced future acquisition cost.
Account for structure, encoder, decoder, invocation machinery, acquisition, maintenance, and future task savings.
Mandatory controls include exact lookup, growing dictionary, generic compression, large unstructured memory, and fixed procedure library.
A representation can grow in bytes and still be useful cognitive compression if it drastically reduces future learning cost.
16. Abstraction and causal/nuisance dissociation
Gemini proposed a "Nuisance Noise Sabotage." The intuition is useful but raw noise resistance is insufficient.
Replace it with Causal/Nuisance Dissociation.
For a registered task family, vary nuisance statistics while holding causal structure fixed.
Separately vary causal structure while holding superficial statistics as similar as practical.
A candidate abstraction should exhibit:
\[
\text{large nuisance change}
\rightarrow
\text{small appropriate competence change}
\]
while:
\[
\text{causal-law change}
\rightarrow
\text{appropriate behavioral/internal revision}.
\]
Noise robustness alone may reflect regularization, capacity, preprocessing, or optimization.
The desired phenomenon is invariance to nuisance combined with sensitivity to causal change.
17. Critical thought
Do not install skepticism.
Build worlds where skepticism pays.
Useful pressures include misleading early evidence, sources with different reliability, multiple initially compatible explanations, costly observation, irreversible action, changing source reliability, and regime shifts.
Measure warranted revision latency, false revision under stable laws, net value of information, regret from premature action, source-law transfer, and calibration only where a valid output interface exists.
Cheap controls include always switch, never switch, always query, majority vote, recent-cue follower, simple change detector, and regime table.
18. Sagacity
Define transferable sagacity operationally as:
prior development causally reducing resource cost for competence on genuinely new causal families.

Do not collapse this into one scalar, but a useful diagnostic ratio is:
\[
S = \frac{\text{future acquisition cost avoided}}
{\text{cost of carried-forward developmental machinery}}.
\]
Report acquisition curves, success probability, retained competence, full lifecycle cost, transfer breadth, amortization, and causal dependence on carried machinery.
19. Recursive sagacity
Combine the three independent formulations.
Use Astra's representation-neutral causal skeleton:
\[
V \rightarrow U \rightarrow S
\]
where:
- \(S\): task-solution state;
- \(U\): process that constructs/changes S;
- \(V\): process that constructs/changes U.
Use Fable's functional criterion:
later acquisition becomes cheaper because earlier development built reusable machinery.

Use Opus's provenance criterion:
the effect must trace through machinery that actually participates in future developmental writes, rather than merely carrying task content.

A candidate claim therefore needs functional evidence, nested causal evidence, and developmental provenance.
The preferred experiment:
1. Develop on family A to produce \(V_A\).
2. Reset task content.
3. Let \(V_A\) construct fresh \(U_B\) on family B.
4. Freeze \(U_B\).
5. Reset task state.
6. Test \(U_B\) on fresh family C.
7. Lesion V.
8. Sham lesion V.
9. Rescue V.
10. Cross V donors and U donors.
11. Use irrelevant-history donors.
12. Repeat on fresh D/E families.
13. Where possible, reconstruct the mechanism in another physical substrate.
If only S improves: task learning.
If U improves fresh S: learning-to-learn.
If developed V causally improves the construction of fresh U, which improves fresh S: nested developmental improvement, provisionally recursive sagacity at the tested depth.
This definition does not exclude conventional meta-learning or gradient methods. If a conventional system passes, report that result.
20. Claim ladder
Use a common evidence ladder.
Level    Meaning
C0    Observation
C1    Qualified anomaly/effect
C2    Robust effect
C3    Causal mechanism
C4    Developmental/reasoning primitive
C5    Transferable mechanism
C6    Architectural principle


Nulls are typed rather than flattened to ABSENT.
Suggested types include:
- CAPACITY_UNESTABLISHED
- WORLD_INSUFFICIENT
- REACH_UNESTABLISHED
- DEVELOPABILITY_UNESTABLISHED
- DETECTION_UNQUALIFIED
- INTERVENTION_INVALID
- UNBRACKETED
- BOUNDED_NEGATIVE
21. Historical Prometheus as qualification corpus
V1/v2 should not be discarded.
Its greatest Phase 3 value may be as physical-affordance fossils, search-pathology examples, cheap-baseline library, false-positive fixtures, false-negative fixtures, provenance attacks, ruler attacks, intervention attacks, and misleading success stories.
Every recurring failure class should become a counterfeit or adversarial fixture.
Examples include answer leakage, constant/lookup baseline omission, seeded phenomena described as endogenous, label/provenance confusion, transplant interpreted as de novo origin, impossible controls, ruler unable to output a required class, search operator unable to traverse a known path, post-data model selection, same-code "independent" replication, shallow world interpreted as cognitive demand, propagation interpreted as information processing, source-read mechanism labels without intervention, library growth interpreted as self-improvement, and audit allegations later shown too broad.
Critics must also be qualified. A good audit system must be able to reject persuasive false accusations.
22. Resource doctrine
Model inference belongs mainly at epistemic forks:
- theory;
- experimental design;
- code generation;
- adversarial review;
- anomaly interpretation;
- prior-art search.
Routine execution should progressively become model-free:
- search;
- scheduling;
- scoring;
- statistics;
- baseline evaluation;
- claim promotion;
- lineage;
- receipts;
- canaries;
- demotion after defect discovery.
Track CPU-hours, GPU-hours, kWh, dollars, model tokens, operator interventions, engineering hours, review hours, and scientific uncertainty resolved.
23. Scientific yield
Do not optimize number of runs, flags, commits, engines, or agents.
Optimize resolved alternatives.
Examples of high scientific yield:
- an affordance shown necessary;
- a cheap explanation killed;
- a null upgraded from uninterpretable to bounded;
- a transition surface mapped;
- a causal organ identified;
- a mechanism transferred;
- a substrate-dependence discovered;
- a recursive-sagacity candidate reduced to ordinary meta-learning;
- a developmental thesis cleanly falsified.
A useful conceptual objective is:
\[
Y =
\frac{\text{important uncertainty resolved}}
{\text{compute + inference + energy + human attention}}.
\]
24. What would falsify the present framing?
The developmental/RSO thesis should be reconsidered if qualified experiments repeatedly show that fixed inherited or conventional learners dominate lifecycle-adjusted development; no tested regime makes structural development economical; developed structures fail to reduce future acquisition cost after lookup/library controls; nested effects collapse under fresh-state and content/executor separation; cross-physics results are overwhelmingly substrate artifacts; search geometry makes proposed developmental spaces practically inaccessible; W2 demand cannot be increased without losing scientific control; the observatory cannot support non-Track-A physics without redesign; or scientific qualification costs so much human/inference effort that useful exploration becomes impossible.
A negative outcome here is a scientific result, not a failure of Prometheus.
