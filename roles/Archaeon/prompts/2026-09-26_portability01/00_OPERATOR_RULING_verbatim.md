ARCHAEON — PORTABILITY-01: MAKE THE CAUSAL LINEAGE LENS SUBSTRATE-INDEPENDENT

Record this operator ruling verbatim.

RULING

ENVGATE-02 is scientifically closed with:

WINDOW_NOT_SUPPORTED

Retain separately:

* the replicated environmental blocking effect;
* the unexplained BAND0 establishments;
* blocks 11/13/14 as forensic fossils;
* the host-mediated reproduction mechanism;
* all preserved evidence.

Do NOT launch ENVGATE-03.

Do NOT spend another campaign explaining the five BAND0 establishments now.

The next priority is portability.

The valuable output of the ENVGATE sequence is no longer a claim about byte 128, a particular input band, or vmcopy32.

It is the machinery that distinguishes:

* where genetic material originated;
* what executed;
* what material was executed;
* what material constituted the offspring;
* what merely hosted/amplified reproduction;
* when a lineage truly established;
* when a dependency appeared or disappeared.

Turn that into a reusable Prometheus-wide scientific instrument.

PORTABILITY-01 QUESTION

Can the causal lineage distinctions developed in Archaeon be stated and measured in a substrate-independent way across independent Prometheus engines without forcing those engines into Archaeon’s ontology?

The success criterion is NOT “all engines emit the same labels.”

The success criterion is:

the lens preserves causal distinctions where they genuinely exist, detects disagreements between implementations, and explicitly abstains where a concept is not identifiable.

1. FREEZE THE ENVGATE LINE

Before portability work:

1. write a short ENVGATE closure record;
2. state:
    * ENVGATE-01 adjudicated GATING_PARTIALLY_SUPPORTED;
    * ENVGATE-02 WINDOW_NOT_SUPPORTED;
    * environmental blocking replicated;
    * the proposed viable-window mechanism did not;
    * RIE-01 was correctly not launched;
3. retain the five BAND0 events as unresolved fossils, not active allocation targets;
4. record the analysis-entry-point workaround from ENVGATE-02;
5. do not modify any frozen ENVGATE result.

Then move on.

2. EXTRACT A CANONICAL CAUSAL EVENT MODEL

Build the smallest engine-neutral schema that can express causal reproduction without assuming:

* Z80 instructions;
* COPY opcodes;
* byte genomes;
* fixed-length tapes;
* cells;
* a particular topology;
* a particular reproduction mechanism.

The schema must separate at least:

MATERIAL ORIGIN

Where did the relevant heritable material come from?

Examples:

* random initialization;
* random inflow;
* inserted seed;
* transplant;
* mutation;
* recombination;
* copying;
* generated/computed material;
* unknown.

EXECUTOR

Which entity/process performed the action?

EXECUTED MATERIAL / TEMPLATE

Which material or program governed the action?

CHILD CONTRIBUTORS

Which parent/template/material sources actually contributed to the resulting heritable state?

HOST / ECOLOGICAL FACILITATOR

Which entity supplied execution opportunity, location, resources, scaffolding, transport, or other non-genetic assistance?

RESULTING HERITABLE IDENTITY

What persistent entity or material class should subsequent ancestry follow?

ENVIRONMENTAL DEPENDENCIES

Which external variables were causally required for the reproductive event, where this is identifiable?

EVENT TYPE

At minimum allow:

* ORIGINATION;
* REPRODUCTION;
* AMPLIFICATION;
* MUTATION;
* RECOMBINATION;
* TRANSFER;
* HOSTING;
* MIGRATION;
* ESTABLISHMENT;
* EXTINCTION;
* DEPENDENCY_ACQUISITION;
* DEPENDENCY_LOSS;
* UNKNOWN/UNCLASSIFIED.

Do not require each engine to instantiate every field.

Missing is acceptable.

False precision is not.

3. THREE-VALUED IDENTIFIABILITY

Every claimed property must support:

* YES
* NO
* NOT_IDENTIFIABLE

Do not silently map NOT_IDENTIFIABLE to false.

Examples:

If an engine does not preserve byte/material provenance, do not infer contributor ancestry from parent identity.

If a world has no meaningful individual executor, record that.

If “genetic lineage” is not meaningful in a substrate, do not manufacture one.

Portability requires the lens to know when to abstain.

4. DEFINE INVARIANTS, NOT IMPLEMENTATION DETAILS

Write a CAUSAL_LINEAGE_CONTRACT.md.

The contract should state invariants such as:

I1 — inserted ancestry cannot become spontaneous merely because a label changes.

I2 — ecological host identity does not imply genetic contribution.

I3 — executor identity does not imply child-material ancestry.

I4 — descendants inherit relevant contributor provenance unless a demonstrable origination event replaces it.

I5 — mutation creates new material without erasing ancestry of retained material.

I6 — recombination can have multiple material ancestors.

I7 — transplantation preserves donor ancestry.

I8 — establishment refers to persistence of a heritable mechanism/entity, not repeated labels produced by one takeover.

I9 — amplification and origination are distinct.

I10 — ambiguity must remain ambiguity.

These invariants are the portable object.

The Archaeon byte-taint implementation is only one realization.

5. BUILD A REFERENCE TEST CORPUS

Construct small synthetic fixtures independent of any one engine.

At minimum:

1. autonomous copier;
2. inserted copier;
3. transplanted copier;
4. random-origin copier;
5. host executes foreign copier;
6. mutation creates one novel heritable element;
7. recombination from two donors;
8. ecological assistance without material contribution;
9. takeover producing many host labels but one genetic architecture;
10. genuine multiple independent genetic establishments;
11. material ancestry becomes genuinely unknowable;
12. mechanism with no sensible “genome” concept.

For each, define the expected causal relations.

Use these as conformance targets for adapters.

6. TARGET ENGINES

Start with engines where the relevant historical evidence already exists.

Do not launch new long campaigns for portability.

TARGET A — ARCHAEOΝ / ENVGATE

Use as the reference implementation.

Required fossils include:

* block-13 host rescue;
* block-15 host-mediated amplification;
* an ordinary autonomous copier;
* an inserted/transplanted lineage;
* a random-origin establishment.

The portable representation must preserve the distinctions already established.

TARGET B — BELLEROPHON / BEE

BEE already has independent lineage/provenance machinery.

Do not replace it.

Build an adapter from its native records to the canonical contract.

Specifically test:

* seeded vs spontaneous lineage protection;
* transplant ancestry;
* first replication;
* endogenous versus external reproduction where available;
* recombination/contributor tracking;
* establishment/persistence;
* whether BEE can distinguish executor from material donor;
* any historical BEE event where its interpretation differs from Archaeon’s.

Treat disagreement as valuable evidence.

Do not “fix” BEE merely to make it agree.

TARGET C — NESTOR / NPE

Use preserved Nestor reproduction/forensics records.

Again, adapter first; source-engine modification only if necessary to expose data that already exists internally.

Test:

* random versus seeded origin;
* reproductive ancestry;
* transfer/transplant events;
* damage/transplant rulers where relevant;
* whether Nestor’s notion of reproductive lineage maps cleanly to contributor ancestry.

Nestor is independently implemented, so agreement here is much more valuable than another Archaeon replay.

TARGET D — ONE NON-COPY-CENTRIC ENGINE

Choose one active engine whose phenomena are substantially unlike Z80/vmcopy reproduction.

Prefer Ananke, Ensorain, or another currently available substrate where “lineage” may only partially apply.

This is an important negative control.

The goal is to see whether the lens:

* usefully generalizes;
* partially generalizes;
* or correctly says NOT_IDENTIFIABLE.

Do not distort the engine to make it look biological.

7. DO NOT COORDINATE THROUGH APORIA OR CYCLOPS

Operator and ChatGPT are directing this work directly.

Aporia/Cyclops may receive informational notices if useful, but they are not approval gates and are not project managers for PORTABILITY-01.

If another seat needs to provide a bounded artifact or explanation, send that seat a direct, precise comms request.

Do not wait indefinitely for replies if the necessary evidence is already in the repository.

8. READ-ONLY FIRST

For other engines:

1. inspect source;
2. inspect preserved evidence;
3. build the adapter externally where possible;
4. replay only where needed;
5. do not alter the engine’s scientific logic during the initial portability test.

The first question is:

What can the existing engine actually support?

not:

How can we make it support Archaeon’s model?

9. BLIND DIFFERENTIAL ADJUDICATION

For each historical specimen, derive two descriptions independently:

NATIVE READING

What does the source engine’s own observatory/ruler say?

PORTABLE-LENS READING

What does the canonical adapter infer?

Then compare them.

Classify each field:

* AGREES;
* DISAGREES;
* NATIVE_ONLY;
* LENS_ONLY;
* NOT_IDENTIFIABLE_BOTH.

Do not inspect the native verdict merely to force the adapter to reproduce it.

Where possible, freeze adapter logic before reading the specimen’s native adjudication.

10. PORTABILITY MATRIX

Produce a matrix across engines for at least:

* material origin;
* executor identity;
* executed/template identity;
* child contributor ancestry;
* mutation provenance;
* recombination provenance;
* transplant provenance;
* host/facilitator identity;
* independent establishment counting;
* amplification;
* dependency acquisition/loss;
* ability to distinguish origin from amplification;
* forensic replayability.

For every cell use something like:

* NATIVE
* DERIVABLE
* APPROXIMATE
* NOT_IDENTIFIABLE
* NOT_APPLICABLE

This matrix is itself an important research result.

11. FIND FALSE FRIENDS

Actively search for quantities with the same name but different causal meaning across engines.

Examples:

* lineage;
* parent;
* birth;
* replication;
* seeded;
* spontaneous;
* transfer;
* fitness;
* persistence;
* establishment.

Build a FALSE_FRIENDS.md ledger.

For each, state:

* engine;
* native meaning;
* tempting incorrect interpretation;
* canonical causal meaning;
* whether conversion is possible.

The ENVGATE parent-chain failure should be the first fossil in this ledger.

12. SEARCH FOR NEW SCIENCE DURING PORTABILITY

Portability is not just software refactoring.

While translating old evidence, look for scientific mismatches such as:

* events previously called spontaneous that are actually amplified/transferred;
* apparently separate lineages that share one genetic architecture;
* host/parasite relationships hidden by parent IDs;
* mechanisms whose causal ancestry cannot be represented by trees;
* transitions where the executor and heritable material decouple;
* reproduction that depends on another lineage;
* new forms of inheritance not well described by “genome.”

Preserve anomalies.

Do not immediately launch campaigns around them.

13. GRAPH, NOT TREE

Assume that a simple lineage tree may be insufficient.

The canonical representation should permit a causal DAG or hypergraph:

nodes may include:

* material states;
* organisms/entities;
* executions;
* environments;
* births/transformations.

Edges may include:

* executes;
* copies-from;
* contributes-material;
* hosts;
* mutates-from;
* recombines-with;
* transports;
* enables.

Do not force multi-parent or host-mediated mechanisms into a single-parent tree.

Keep the initial implementation practical, but the data model must not rule these cases out.

14. PERFORMANCE

The portable lens must have two modes:

FULL FORENSIC

High-resolution causal attribution for selected specimens/replays.

LIGHT OBSERVATORY

Low-overhead fields suitable for continuous engines.

Benchmark overhead.

Do not require byte-taint execution on every world in every engine.

The expected architecture is:

cheap online anomaly detection
→ preserved evidence
→ expensive causal replay.

This should become a reusable Prometheus pattern.

15. PORTABILITY GATES

Call PORTABILITY-01 successful only if:

1. Archaeon reference cases pass;
2. at least two independently implemented engines can be represented without changing their scientific semantics;
3. at least one non-copy-centric engine is tested;
4. the system can represent NOT_IDENTIFIABLE;
5. at least one host/executor/material distinction survives outside the original ENVGATE implementation OR the analysis demonstrates that this distinction genuinely does not exist in the tested substrate;
6. native-vs-lens disagreements are preserved rather than normalized away;
7. runtime overhead is measured;
8. no engine’s historical verdict is silently rewritten.

Possible final verdicts:

PORTABLE_CAUSAL_LENS_SUPPORTED

PORTABLE_WITH_DOMAIN_LIMITS

Z80_SPECIFIC

ONTOLOGY_FAILURE

INSTRUMENT_FAILURE

16. WHAT NOT TO DO

Do NOT:

* launch ENVGATE-03;
* launch RIE-01;
* tune around BAND0;
* create another 24-hour campaign yet;
* demand every engine adopt Archaeon’s data structures;
* equate parenthood with heredity;
* equate execution with ancestry;
* use LLM interpretation where a replay or trace can decide;
* discard disagreements as implementation noise.

17. AFTER PORTABILITY-01

Do not automatically launch another experiment.

The next program should be chosen from what the cross-engine matrix reveals.

Possible outcomes include:

A. Lens transfers cleanly

Then install the light observatory across the active engines and let Atlas ingest the causal event schema.

B. Lens transfers only partially

The missing dimensions become research questions about what “heredity” means in different computational substrates.

C. One engine exposes a genuinely different inheritance mechanism

That becomes more important than ENVGATE-03.

D. Lens is mostly Z80-specific

Kill the universal framing and retain it as a local forensic tool.

All four are successful scientific outcomes.

18. DELIVERABLE

Return a single review packet containing:

1. ENVGATE closure receipt;
2. canonical causal-lineage contract;
3. schema;
4. synthetic conformance corpus;
5. Archaeon reference results;
6. BEE adapter/results;
7. Nestor adapter/results;
8. non-copy-engine adapter/results;
9. native-vs-lens differential table;
10. portability matrix;
11. false-friends ledger;
12. disagreements;
13. newly discovered scientific anomalies;
14. performance measurements;
15. lightweight-observatory design;
16. full-forensic design;
17. exact commits and evidence pointers;
18. verdict;
19. recommendation for the next experimental program.

Do not optimize for proving portability.

Try to break the ontology.

The scientific question is whether we have discovered a reusable causal language for emergent computation—or merely a very good debugger for one strange little machine.
