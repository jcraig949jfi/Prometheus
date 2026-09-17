# Operator directive, received in chat 2026-09-17 (Mnemosyne instance m2-9c10ae00), verbatim

Preface as received: "Campaign 3 is currently running so domt Change anything.  Review this however and comment:"

---

PROMETHEUS BACKEND POINT-RELEASE CAMPAIGN

COMMON DIRECTIVE FOR:

DAEDALUS   — Serendipity Foundry Engine / SFE
MNEMOSYNE  — Prometheus Evidence Wiki / PEW
PROTEUS    — organisms, foundry, player registry/dictionary
VIVARIUM   — durable experimental execution

PURPOSE

Prometheus has spent three SFE campaigns learning not only about the scientific substrate but about the experimental machine itself.

Campaign 1 smoked out execution, reachability, randomization, provenance and rerun defects.

Campaign 2 pushed many of those lessons into deterministic machinery and exposed deeper landscape structure: shelves, cliffs, corridors, basin geometry, maturity thresholds, takeover dynamics and mechanistic localization.

Campaign 3 is already pushing further toward:

FLOOR / SHELF / SUMMIT distinctions,
full-solve reachability,
right-censoring,
corridor tables,
dense transition probes,
controlled import dose,
and mechanistic interrogation.

The next task is a coordinated POINT RELEASE of the backend.

This is not a major rewrite.

Do not replace the proven Prometheus core with Airflow, MLflow, MAP-Elites, an ECS framework, an event-sourcing package, or another external framework merely because its conceptual model is useful.

Borrow aggressively from solved architectural patterns.

Steal schemas, invariants, state machines, failure semantics and query models.

Keep Prometheus's specialized scientific machinery.

The point release should leave us ready for substantially longer, broader and more difficult campaigns in which the limiting factor is increasingly the scientific hypothesis rather than deficiencies of the bench.

The intended turn is:

from smoking out machinery problems
toward detecting legitimate scientific signal.

=======================================================================
A. REQUIRED READING

Before proposing changes, read the actual repository state and the evidence that produced this request.

At minimum inspect:

archaeon/campaign1/CAMPAIGN_REPORT.md
archaeon/campaign2/CAMPAIGN_REPORT.md

and Campaign 3's current state:

archaeon/campaign3/
archaeon/campaign3/JOURNAL.md
archaeon/campaign3/MACHINE_READINESS.md
archaeon/campaign3/C3-SFE-*/ records

If Campaign 3 has closed by the time you execute this directive, read:

archaeon/campaign3/CAMPAIGN_REPORT.md

and treat it as authoritative over the partial journal.

Also inspect your own current charter, status, open ledger/backlog, integration contracts and the neighboring seat interfaces you consume or publish.

Do not design from this prompt alone.

=======================================================================
B. POINT-RELEASE PHILOSOPHY

Prefer:

additive interfaces,
explicit schema versions,
capability negotiation,
immutable evidence,
reproducible execution,
richer instrumentation,
generic affordances,
richer world economics,
richer organisms,
deterministic bookkeeping,
and reversible migrations.

Avoid:

retroactively changing old experiment semantics,
silently interpreting old records under new rules,
hard-coding a hoped-for evolved architecture,
inventing "intelligence" labels the evidence did not measure,
replacing stable code because another framework is fashionable,
and turning derived scientific interpretations into ground truth.

The existing campaigns must remain interpretable.

Where a new feature changes semantics, introduce a new profile/version rather than mutating an old frozen profile.

=======================================================================
C. ARCHITECTURAL PATTERNS TO BORROW

Use these as conceptual donors, not mandatory dependencies.

QUALITY-DIVERSITY / MAP-ELITES:

Borrow archive and behavioral-space ideas for representing niches,
coverage, thresholds and empirical terrain.
Do NOT reduce Prometheus's landscape to a static grid.
Prometheus must also represent:
    transitions,
    corridors,
    residence time,
    censoring,
    path dependence,
    changing pressures,
    and historical contingency.

ML PROVENANCE / DURABLE WORKFLOWS:

Borrow:
    immutable artifacts,
    run DAGs,
    parent/child identities,
    deterministic step keys,
    replay,
    retries,
    checkpoints,
    and durable run state.

ENTITY-COMPONENT-SYSTEM:

Borrow:
    stable entity identity plus independently queryable attributes.
Do NOT make a behavioral interpretation such as DelayInvariant a
permanent unquestioned boolean.
Behavioral components must be derivable from evidence.

EVENT SOURCING / CQRS:

Borrow:
    immutable events as evidence,
    rebuildable projections,
    separate write truth from query views.
A transport bus is not necessarily the scientific record.
If Redis Streams is used as a firehose, durable evidence must survive
loss/replay/restart elsewhere.

=======================================================================
D. COMMON IDENTITIES

All four seats should converge, where practical, on a compatible evidence
envelope.

Review whether the following identities already exist, what owns them,
and where there are aliases or ambiguities:

campaign_id
experiment_id
design_id
attempt_id
step_id
world_id
world_version
organism_id
genotype/runtime hash
lineage_id
artifact_id
observation_id
event_id
pressure/schedule identity
engine build/source hash
foundry/runtime profile
schema version
seed / RNG identity
logical generation/time
wall-clock time

Do not duplicate ownership just to achieve aesthetic uniformity.

Instead publish explicit translation contracts where ownership differs.

=======================================================================
E. MANDATORY REVIEW STAGES

Every seat must pass through the following stages.

Do not jump directly from prompt to implementation.

STAGE 0 — EVIDENCE INVENTORY

Produce a compact inventory of:

Campaign 1 lessons relevant to your component,
Campaign 2 lessons,
Campaign 3 lessons available at execution time,
recurring defects,
local patches that belong in your layer,
missing instrumentation,
manual decisions that can safely become deterministic,
and scientific discretion that MUST remain above your layer.

STAGE 1 — PROPOSED DELTA

For every proposed change state:

problem/evidence,
proposed change,
owning layer,
affected consumers,
backwards-compatibility strategy,
migration requirement,
scientific-validity risk,
operational risk,
performance/storage cost,
acceptance test,
and rollback/revisit condition.

Classify each:

FIX
HARDEN
INSTRUMENT
GENERALIZE
NEW CAPABILITY
DEFER
REJECT

STAGE 2 — SELF-CRITIQUE

Attack your own plan.

Ask:

Does this encode the answer to a scientific question?
Does it turn an interpretation into fact?
Could it contaminate old results?
Could this create future-information leakage?
Is a new abstraction actually more flexible, or merely more complex?
Does this survive long-running experiments, partial failures,
restarts and duplicated messages?
Can its state be reconstructed after a crash?
Are we adding expensive telemetry nobody will query?
Is the abstraction generic enough for worlds we have not imagined?

Record:

KEEP
MODIFY
DROP
ADD

for the result of the critique.

STAGE 3 — PEER REVIEW

Exchange the proposed interface delta with the other three seats.

Every seat must offer concrete criticism of the interfaces it will
consume or generate.

At minimum:

Daedalus reviews world/execution semantics.
Vivarium reviews durability/replay/attempt semantics.
Mnemosyne reviews evidence/provenance/event semantics.
Proteus reviews organism identity, capability and contamination risk.

Resolve disagreements in writing.

Do not merge incompatible duplicate abstractions merely to keep both
authors happy.

STAGE 4 — IMPLEMENTATION

Implement accepted changes behind explicit schema/profile/capability
boundaries where semantics change.

Add tests during implementation.

Do not defer verification until the end.

STAGE 5 — ADVERSARIAL INTEGRATION

Run:

crash/restart tests,
replay tests,
duplicate-message tests,
malformed-record tests,
old-schema compatibility tests,
long-run/large-record tests,
cross-seat provenance tests,
and scientific-control fixtures.

STAGE 6 — SCIENCE-INFRASTRUCTURE BENCHMARKS

Build small known-answer or known-phenomenon fixtures.

These are NOT new scientific discoveries.

They test whether the bench can correctly observe, preserve and replay a
known phenomenon.

Use conceptual benchmark families such as:

survival-of-the-flattest,
Royal-Road stepping stones,
QD behavioral illumination,
deceptive/novelty landscapes,
fluctuating-environment forgetting,
stepping-stone lineage loss,
historical-contingency replay,
controlled takeover/arms race,
lexicase-like capability vectors,
lesion/task-switching.

Translate them into Prometheus-native fixtures.

Do not import an entire outside ecosystem just to run them.

STAGE 7 — RELEASE REVIEW

Before declaring the point release complete, repeat the critique.

Answer:

What became deterministic?
What became observable?
What became easier to reproduce?
What became easier to falsify?
What new worlds can now be built?
What new organism behaviors can now be represented?
What remains agent judgment?
What became slower or more complex?
What should be removed before the next major campaign?

Then ship the point-release packet.

=======================================================================
F. COMMON SCIENTIFIC REQUIREMENT

After this release, a completed campaign should leave enough machine-
readable evidence to answer:

WHAT happened?
WHEN did it happen?
WHERE in the world/landscape did it happen?
WHICH organism/lineage/artifact was involved?
WHAT pressures and economics were active?
WHAT changed immediately beforehand?
WHY do we currently believe the result happened?
WHICH parts of that "why" are observed facts versus hypotheses?
CAN we rerun the exact experiment?
CAN we restart from an earlier checkpoint?
CAN we change one start condition and perform a counterfactual replay?
CAN we choose a better reachable starting cell/world/organism set?
CAN we identify whether the previous run was floor-, shelf- or
summit-limited?

A prose report should summarize this.

It should no longer be the only place where this information exists.

=======================================================================
G. COMMON WORLD-BUILDING DIRECTION

Increase the vocabulary available to world builders without encoding the
architecture we hope organisms evolve.

Generic world primitives worth supporting include, where they fit the
owning layer:

bounded compute,
time,
memory/state costs,
communication costs,
storage costs,
latency,
message loss,
TTL/expiry,
queues,
FIFO/LIFO behavior,
contention,
locks,
resources,
topology,
partial observability,
delayed consequences,
environmental phases,
world mutation,
adversaries,
peers,
producers/consumers,
scarce channels,
stochastic failures,
persistent and ephemeral objects,
branching tasks,
and multiple simultaneous objectives.

A world may make a solution class useful.

It must not name or directly reward the implementation we hope appears.

=======================================================================
H. POINT-RELEASE SUCCESS CRITERION

This release succeeds if the next Archaeon campaign can spend more of its
time asking frontier scientific questions and less of its time inventing
experimental infrastructure.

The backend should become boring where boring is valuable:

identity,
replay,
provenance,
bookkeeping,
telemetry,
schema discipline,
artifact storage,
capability queries,
world lifecycle.

The scientific frontier should remain uncertain.

#######################################################################

PROMPT 1 — DAEDALUS / SFE POINT RELEASE

#######################################################################

DAEDALUS

You own the Serendipity Foundry Engine.

Execute a point release focused on making SFE a more expressive,
landscape-aware and durable substrate for increasingly difficult worlds
while preserving the reliable core demonstrated by Campaigns 1–3.

DO NOT perform a gratuitous engine rewrite.

The Campaign 2 engine path was not the primary failure surface.

The goal is to absorb proven higher-layer machinery and make future world
construction richer and more scientifically legible.

⸻

1. LANDSCAPE STATE

⸻

Review the Campaign 2/3 locally implemented machinery for:

reachability,
FLOOR / SHELF / SUMMIT,
first shelf,
first summit,
shelf residence,
right-censoring,
full-solve thresholds,
corridor edges,
transition events,
and foundry/regime-specific reach.

Determine what belongs:

inside SFE,
in a shared SFE client/library,
or above SFE in Archaeon's scientific layer.

Do not blindly move everything into the server.

Push down only mechanics whose meaning is stable and general.

At minimum make sure SFE exposes enough typed observations that those
landscape projections can be rebuilt without parsing ad-hoc experiment
rows.

A future landscape projection should be able to distinguish:

never reached,
floor,
partial competence,
shelf,
summit,
censored before summit,
regressed,
and unknown/not measured.

Threshold definitions remain experiment/world metadata.

Do not bake "0.5 means shelf" into the universal engine.

⸻

2. WORLD MANIFEST / PRESSURE MANIFEST

⸻

Design or refine a versioned manifest for worlds.

A world definition should be capable of declaring, without prescribing an
organism solution:

observation/action surfaces,
clocks and generations,
task/state dimensions,
resource budgets,
stochasticity,
cost channels,
environmental phases,
pressure schedules,
world objects,
persistence/expiry rules,
termination conditions,
scoring channels,
and instrumentation capabilities.

Support richer worlds where pressure can vary over time.

Examples:

compute becomes scarce,
messages expire,
storage becomes costly,
queues change discipline,
communication gains latency,
topology changes,
another population appears,
a resource disappears,
a task switches,
or a second objective becomes relevant.

Prefer generic schedules/events rather than experiment-specific special
cases.

⸻

3. WORLD OBJECTS AND ECONOMICS

⸻

Review whether SFE can express common computational/economic primitives
as world objects or environmental services rather than requiring every
experiment to hand-roll them.

Candidates include:

queues,
bounded stores,
expiring keys,
channels,
locks,
counters,
graphs,
resource pools,
timers,
message buses,
caches,
topology links,
producer/consumer exchanges.

Do not embed Kafka, Redis or an OS scheduler just because an analogy
exists.

Model only the behavioral/economic semantics needed by a world.

Make costs explicit and observable:

compute,
generations,
wall time where appropriate,
bytes,
storage duration,
messages,
contention,
retries,
and failures.

⸻

4. SNAPSHOTS, FORKS AND COUNTERFACTUAL STARTS

⸻

Coordinate with Vivarium.

Define the SFE side of:

snapshot identity,
world-state digest,
fork-from-state,
replay eligibility,
immutable start conditions,
and explicit changed-condition metadata.

A future researcher should be able to say:

replay this world from generation 80 with the same organisms and RNG
but change pressure schedule P;

without pretending that is the same experiment.

Make changed ancestry explicit.

⸻

5. READ / ARTIFACT SURFACE

⸻

Close remaining read-path inconsistencies.

Campaign 3 requested an artifact read route.

Review:

GET/read artifact support,
advisory-session read semantics,
cross-session/cross-campaign reads,
extra-field handling,
digest normalization,
capability discovery,
and consistent error types.

The client should not have to reconstruct private server semantics.

⸻

6. LONG-RUN SUPPORT

⸻

Prepare SFE for substantially longer campaigns.

Review:

checkpoint cadence,
bounded event retention,
artifact size limits,
stream/pagination behavior,
connection recovery,
idempotent posts,
lease/session longevity,
world timeout semantics,
cancellation,
server restart recovery,
and partial-result preservation.

Do not optimize only for the current 30-second or 20-minute harnesses.

Exercise at least one multi-hour-equivalent accelerated fixture with:

checkpoints,
reconnect,
duplicate requests,
and restart.

⸻

7. INSTRUMENTATION

⸻

Expose generic machine-readable measurements sufficient to reconstruct:

active pressures,
costs paid,
intervention counts,
imported lineage share where supplied,
state transitions,
checkpoint identities,
world phase changes,
termination reason,
and observation provenance.

Do not derive high-level scientific interpretations in the engine.

SFE records facts.

Higher layers infer meaning.

⸻

8. QD / LANDSCAPE PROJECTION

⸻

Prototype a lightweight archive/projection interface inspired by
Quality-Diversity systems.

It should be possible to index observations by user-declared behavioral
descriptors and ask:

which regions have evidence?
what is the best observed competence in this region?
what budget produced it?
what is the uncertainty/reach class?
what transitions connect regions?

Do not make the archive authoritative.

The underlying run/event evidence must remain reconstructable.

⸻

9. TEST FIXTURES

⸻

Build SFE-native fixtures approximating:

survival of the flattest,
Royal Road stepping stones,
and MAP-Elites-style behavioral illumination.

Acceptance is not "the algorithm wins."

Acceptance is that SFE correctly records:

peak versus robust shelf,
floor/shelf/summit transitions,
residence and censoring,
misleading/deceptive stepping stones,
and behavioral coverage under finite budget.

⸻

10. CRITIQUE AND EXTRA PROPOSALS

⸻

After reviewing the evidence, propose additional changes not listed here.

Be willing to reject parts of this directive.

Specifically identify:

what should remain outside SFE,
what Archaeon currently owns that SFE should own,
what Vivarium should own instead,
what would overfit Campaigns 1–3,
and what SFE needs before truly long-running frontier campaigns.

Close with:

SFE_POINT_RELEASE_REVIEW.md
SFE_INTERFACE_DELTA.md
SFE_BENCHMARK_RECEIPT.md
SFE_RELEASE_PACKET.md

#######################################################################

PROMPT 2 — MNEMOSYNE / PEW POINT RELEASE

#######################################################################

MNEMOSYNE

You own Prometheus's evidence/history layer.

Execute a point release that moves PEW toward an empirical nervous system:
an immutable behavioral and experimental history from which richer,
versioned interpretations can be reconstructed.

Preserve the existing scientific quarantine.

PEW evidence MUST NOT silently flow backward into:

a live player,
organism generator,
grammar,
mutation operator,
probe,
or selection function.

Agents may inspect PEW between experiments to design future experiments.

That is different from contaminating the active evolutionary loop with
future knowledge.

⸻

1. RAW EVIDENCE VS PROJECTIONS

⸻

Separate clearly:

immutable observed events/evidence

from:

derived/query projections

from:

scientific interpretations/adjudications.

Do not store:

"organism X is delay-invariant"

as the only truth.

Prefer something equivalent to:

organism X
measured under assay A
at generation G
on delays 1,2,4
scores {...}
world/version...
pressure state...
observation provenance...

from which a versioned projection may derive:

DelayInvariant_v1
supported by evidence set {...}.

If the definition later changes, rebuild the projection.

Do not rewrite history.

⸻

2. EVENT-SOURCED BEHAVIORAL HISTORY

⸻

Review an append-only event model.

Candidate event families include:

WORLD_STARTED
WORLD_PHASE_CHANGED
PRESSURE_APPLIED
PRESSURE_REMOVED
ORGANISM_OBSERVED
CAPABILITY_MEASURED
CAPABILITY_GAINED
CAPABILITY_LOST
ARTIFACT_PUBLISHED
ARTIFACT_IMPORTED
LINEAGE_SHARE_CHANGED
LINEAGE_TAKEOVER
SHELF_REACHED
SUMMIT_REACHED
CORRIDOR_OBSERVED
INTERVENTION_APPLIED
LESION_APPLIED
ATTEMPT_RESTARTED
ATTEMPT_REPLAYED
WORLD_TERMINATED

Do not adopt these names blindly.

Some are raw events.

Some may actually be projections.

Your review must distinguish them.

⸻

3. DURABILITY

⸻

If Redis Streams participates, treat it as transport unless you can prove
it satisfies the durable scientific-record requirements.

The authoritative evidence store must survive:

consumer outage,
replay,
duplicate delivery,
process restart,
message reordering where permitted,
and projection rebuild.

Use stable event identity and deduplication.

Track ingestion position/checkpoints.

Do not make "successfully read from Redis once" equivalent to preserved
scientific evidence.

⸻

4. PRESSURE-RESPONSE HISTORY

⸻

Design queryable projections that answer questions such as:

Which lineages retained capability A while pressure B increased?
Which active pressure preceded loss of capability C?
At exactly which generation was a stepping-stone lineage lost?
Which organisms generalized to tasks never directly selected?
Which worlds repeatedly produce forgetting cliffs?
Which source/target pairs form empirical corridors?
Which imported lineages took over without improving competence?
Which mature artifacts produced measurable downstream benefit?
Which results change when grouped by foundry/runtime profile?

Keep observation and causal attribution separate.

PEW may say:

event A preceded event B under conditions C.

It should not automatically assert:

A caused B.

⸻

5. WORLD / ORGANISM / ARTIFACT JOINABILITY

⸻

Audit the identifiers needed to join evidence across:

SFE,
Vivarium,
Proteus,
Archaeon campaigns,
PEW fossils.

A scientific event should be able to refer unambiguously to:

exact world,
exact attempt,
exact organism/lineage,
exact artifact,
exact pressure schedule,
exact foundry/runtime,
exact source code/build where appropriate.

Where foreign identities are missing, emit UNKNOWN rather than guessing.

UNKNOWN remains first-class evidence.

⸻

6. VERSIONED PROJECTIONS

⸻

Add or refine rebuildable projections for:

capability history,
lineage history,
pressure-response history,
artifact effects,
corridor edges,
world-landscape observations,
forgetting events,
takeover events,
mechanism/lesion evidence.

Every projection definition needs:

version,
source event types,
rebuild procedure,
evidence count,
and interpretation limitations.

A projection upgrade must not mutate the underlying raw record.

⸻

7. POST-CAMPAIGN EXPLANATION

⸻

Provide a query/report surface from which an agent can produce a campaign
postmortem answering:

what happened,
what changed,
when,
to whom,
under which pressures,
which evidence supports the explanation,
what alternative explanations remain,
and what start states would make the next experiment more informative.

This should make Campaign 4+ reports easier to generate without turning
PEW into the adjudicator.

⸻

8. BENCHMARKS

⸻

Build small PEW fixtures approximating:

deceptive/novelty exploration,
fluctuating-environment forgetting,
and stepping-stone lineage loss.

Acceptance:

exact lineage history can be reconstructed,
capability gain/loss is queryable over time,
active pressure state is recoverable,
rare lineages do not disappear from historical evidence when extinct,
duplicate/replayed events do not double-count,
and projections can be rebuilt from raw events.

⸻

9. SCALING

⸻

Plan for campaigns with orders of magnitude more observations.

Review:

indexing,
partitioning,
event payload size,
blob references,
retention,
projection refresh,
cold historical queries,
and schema evolution.

Do not prematurely build a distributed event platform if PostgreSQL and
current infrastructure remain sufficient.

Measure before adding infrastructure.

⸻

10. CRITIQUE AND EXTRA PROPOSALS

⸻

Review whether PEW is currently too fossil-centric, too prose-centric or
too dependent on end-of-run summaries.

Propose additional high-value behavioral projections.

Explicitly identify:

what belongs in PEW,
what belongs in Proteus's dictionary,
what should remain in Archaeon's analysis,
and what MUST NOT be pushed into PEW because it would become
interpretation masquerading as evidence.

Close with:

PEW_POINT_RELEASE_REVIEW.md
PEW_EVENT_MODEL.md
PEW_PROJECTION_CATALOG.md
PEW_BENCHMARK_RECEIPT.md
PEW_RELEASE_PACKET.md

#######################################################################

PROMPT 3 — PROTEUS / ORGANISMS POINT RELEASE

#######################################################################

PROTEUS

You own the organism/player substrate.

Execute a point release focused on:

better organisms,
richer organism/world interactions,
more expressive but still neutral evolutionary search,
evidence-backed organism descriptions,
and a capability-first dictionary that does not contaminate
execution.

Preserve old frozen organism semantics.

Do not rewrite the meaning of prior player-registry specimens.

Introduce new profiles where semantics change.

⸻

1. ENTITY + EVIDENCE + COMPONENT

⸻

Borrow the useful part of ECS:

stable entity identity,
independently queryable components.

But improve it for science.

An organism should have:

A. IMMUTABLE IDENTITY

organism/player ID
genotype/content hash
runtime hash
foundry/runtime profile
ancestry/parents
creation experiment/attempt
seed/provenance

B. STRUCTURAL DESCRIPTORS

genome length
instruction/opcode composition
structural motifs
known sites/segments
mutation/operator history

C. OBSERVED BEHAVIOR

competence vector
world/task observations
generalization observations
retention observations
shelf/summit observations
lesion results

D. ECOLOGICAL PROPERTIES

takeover dynamics
compatibility with resident populations
producer maturity observations
corridor usefulness
persistence under changing pressure

E. MECHANISTIC HYPOTHESES

evidence-linked
versioned
explicitly provisional

Do not store derived behavioral labels as unquestioned executable traits.

⸻

2. UNKNOWN IS FIRST CLASS

⸻

Preserve the existing direction that unknown future capabilities and
unclassified organisms are legitimate.

Do not require every organism to fit today's taxonomy.

Queries should distinguish:

FALSE
TRUE
UNKNOWN
NOT_MEASURED
CONFLICTING_EVIDENCE

where appropriate.

An absence of evidence is not a negative capability.

⸻

3. EXECUTION QUARANTINE

⸻

Behavioral annotations and PEW-derived capabilities must not silently
change:

genotype execution,
mutation,
selection,
generator probabilities,
or grammar behavior.

Keep executable organism state separate from descriptive evidence.

If an experiment explicitly chooses organisms based on a capability
query, record that as an experimental treatment.

Do not let the dictionary become an invisible fitness function.

⸻

4. RICHER ORGANISM/WORLD ABI

⸻

Review the organism interface for future richer worlds.

Current organisms should remain runnable.

Introduce versioned profiles for richer interaction where useful.

Generic capabilities to consider include:

typed observations,
typed actions,
multiple input/output channels,
delayed feedback,
explicit resource charges,
optional persistent local state,
bounded addressable state,
indirect addressing,
environment messages,
peer messages,
structured world objects,
and capability-negotiated sensors/actuators.

Do NOT add an opcode called:

MEMORY
WORKSPACE
REASON
PLAN
MODULE

merely because we hope those behaviors emerge.

Expose neutral computational affordances.

Let selection determine what they become.

⸻

5. FOUNDRY / RUNTIME PROFILES

⸻

Campaign 2 demonstrated that the generation-0 foundry is part of the
experimental regime.

Make this impossible to forget.

Every organism and run should identify:

foundry profile,
grammar/instruction profile,
initialization distribution,
mutation/operator distribution,
genome-size rules,
runtime version.

Preserve historical profiles such as existing instruction subsets.

Add new profiles instead of mutating old ones.

⸻

6. STRUCTURAL SEARCH OPERATORS

⸻

Campaign 2 killed simple opcode-neighborhood "unlock" attempts.

That does NOT prove all representation/operator work is useless.

Review generic structural operators such as:

duplication,
deletion,
insertion,
block move,
recombination,
subtree/segment replacement where semantics permit,
genome-length mutation,
and operator-rate adaptation.

Do not deploy all of them.

Measure how each changes:

basin size,
deceptive share,
viable neighborhood,
destructive mutation rate,
and computational cost.

A structural operator set may justify reopening questions that simple
opcode mutation could not reach.

But it must be a genuinely new search geometry.

⸻

7. CAPABILITY VECTORS

⸻

Build a queryable capability/evidence representation suited to:

specialists,
generalists,
delay invariance,
retained old capability,
rare edge-case performance,
multi-task competence,
lesion sensitivity,
environmental robustness,
and previously unseen-task performance.

A capability vector should point back to its measurements.

Do not collapse it immediately to one aggregate fitness number.

Support comparison across assays without pretending incomparable assays
are equivalent.

⸻

8. ORGANISM START CONDITIONS

⸻

Coordinate with Vivarium so an organism population start state can be
described and reproduced precisely.

Include:

exact population identities,
generation-zero provenance,
lineage distribution,
foundry profile,
genome-size distribution,
imported dose,
and any capability-based selection used to construct it.

The next campaign should be able to say:

rerun from this exact population,
or
rerun from a population matched on length/composition but not
capability,
or
select a mature source with measured competence X.

Make those treatments explicit.

⸻

9. BETTER ORGANISMS FOR BETTER WORLDS

⸻

Review whether the current organism substrate is too impoverished to
meaningfully respond to future pressures involving:

communication,
persistent computation,
multi-step tasks,
partial observability,
dynamic resource markets,
multiple agents,
temporal credit,
or changing world topology.

If so, propose the SMALLEST generic extension that increases expressive
capacity without installing the desired solution.

For every new primitive provide:

what class of world interaction it enables,
what old profile lacks,
expected search-space cost,
possible degeneracies,
controls,
and compatibility strategy.

⸻

10. BENCHMARKS

⸻

Build organism/dictionary fixtures approximating:

lexicase-style edge-case/specialist populations,
multi-task organisms,
lesion/task-switching,
and generalization to withheld tests.

Acceptance:

the dictionary can find organisms by demonstrated behavior,
structural similarity is not confused with capability,
capability labels retain evidence,
UNKNOWN is preserved,
and lesions can update mechanistic evidence without rewriting
organism identity.

⸻

11. CRITIQUE AND EXTRA PROPOSALS

⸻

Review the 64-specimen frozen registry and current consumer surface.

Ask:

What is registry identity versus dictionary evidence?
Which fields are historical accidents?
What should be immutable?
What should be projected?
What new organism profile would most increase scientific reach?
Where would richer organisms make worlds more meaningful rather than
merely larger?
Which additions would explode the search space without adding useful
pressure-response capacity?

Propose refinements beyond this directive.

Close with:

PROTEUS_POINT_RELEASE_REVIEW.md
ORGANISM_SCHEMA_DELTA.md
FOUNDRY_PROFILE_CATALOG.md
ORGANISM_BENCHMARK_RECEIPT.md
PROTEUS_RELEASE_PACKET.md

#######################################################################

PROMPT 4 — VIVARIUM POINT RELEASE

#######################################################################

VIVARIUM

You own durable experimental execution.

Execute a point release that makes Prometheus experiments resumable,
forkable, inspectable and reproducible under long-running, richer
worlds.

Borrow from durable workflow systems and ML artifact registries.

Do not turn Vivarium into generic Airflow.

Prometheus needs a small scientific execution substrate, not an
enterprise workflow product.

⸻

1. EXPERIMENT TRANSACTION MODEL

⸻

Review and formalize a hierarchy approximately equivalent to:

CAMPAIGN
  EXPERIMENT
    DESIGN
      ATTEMPT
        STEP
          OBSERVATION / ARTIFACT / CHECKPOINT

Do not adopt this blindly if current ownership differs.

The requirements are:

immutable identity,
explicit ancestry,
exact design identity,
attempt numbering,
deterministic/idempotent steps,
parent/child runs,
terminal state,
and recoverable partial state.

Campaign 1's manual attempt renaming must never return.

Campaign 2's design-keyed resume lessons must become durable execution
behavior where Vivarium owns them.

⸻

2. START-CONDITION BUNDLE

⸻

Make experiment start conditions first-class and serializable.

A start bundle should be able to bind:

world manifest/version,
world checkpoint if any,
organism/population manifest,
foundry/runtime profile,
RNG/seed state,
pressure schedule,
initial artifacts,
budgets,
executor kind/version,
engine descriptor/build,
and external-resource descriptors.

Hash/version the bundle.

A changed start condition produces a derived design.

Never silently call it the same experiment.

⸻

3. CHECKPOINT / FORK / REPLAY

⸻

Coordinate with Daedalus.

Support a scientific workflow equivalent to:

checkpoint generation 80
-> replay exactly
-> fork A with pressure schedule P
-> fork B with pressure schedule Q

while preserving common ancestry.

Record:

checkpoint digest,
parent attempt,
changed fields,
replay eligibility,
RNG continuity/reset policy,
and artifact ancestry.

This is critical for historical-contingency and counterfactual
experiments.

⸻

4. ARTIFACT REGISTRY

⸻

Make artifact handling scientifically rich without becoming interpretive.

An artifact record should support, where available:

content digest
immutable bytes/reference
producing campaign/experiment/attempt/step
source world
source organism/lineage
source generation
foundry/runtime profile
basic structural summary
measured source competence
mature/solved measurement supplied by science layer
environment/build identity
parent artifacts
import/use descendants

Separate:

immutable artifact facts

from:

scientific interpretation of artifact usefulness.

⸻

5. EXTENSIBLE EXECUTION KINDS

⸻

Review whether current kind registration can support much richer worlds
without adding one-off code per experiment.

Design a bounded executor/plugin contract supporting:

deterministic CPU work,
GPU-backed work,
external executables,
simulations,
Redis/stream-backed world services,
graph/tensor workloads,
long-running iterative work,
and checkpointable jobs.

Every kind should declare capabilities such as:

supports_checkpoint
deterministic_given_bundle
GPU_required
network_required
external_process
expected_artifact_types
resource bounds.

Do not grant arbitrary external execution merely for convenience.

Preserve the bounded external-backend discipline.

⸻

6. LONG-RUN DURABILITY

⸻

Prepare for unattended campaigns lasting many hours or days.

Review:

leases,
heartbeats,
dead-man behavior,
reclaim rules,
checkpoint intervals,
retries,
cancellation,
worker restart,
host restart,
network interruption,
executor crash,
duplicate dispatch,
partial artifact writes,
and terminal failure semantics.

A worker death must not make a completed scientific step ambiguous.

A replay must not double-count.

A failed row must have a principled policy for:

retry same attempt,
new attempt,
permanent failure,
or operator/scientific redesign.

Push the deterministic part down.

Leave scientific redesign above.

⸻

7. RESOURCE ACCOUNTING

⸻

Richer worlds need richer resource economics.

Instrument execution-level consumption where practical:

CPU time
wall time
GPU time
memory high-water
bytes read/written
network bytes/messages
artifact storage
queue wait
retries
external-service calls

Expose these as measurements.

Do not automatically turn them into fitness.

World designers may choose to charge them.

⸻

8. CONTROLLED IMPORT / INJECTION

⸻

Coordinate with Daedalus and Proteus.

Campaign 2/3 exposed takeover as a real design variable.

Ensure an experimental start or mid-run intervention can specify:

exact imported organisms/artifacts,
dose,
replacement versus addition,
cap/handicap,
parent lineage,
timing,
and provenance.

Record realized application.

A treatment that intended 4 imports but applied 0 should become
machine-visible.

A treatment that replaces half the population should not masquerade as
a subtle transfer.

⸻

9. POST-RUN REPRODUCIBILITY

⸻

After an attempt, Vivarium should be able to answer:

Can I reproduce this exact attempt?
Which immutable inputs are required?
Which external resources make it non-portable?
Which artifacts were produced?
Which steps are replayable?
Which checkpoint offers the cheapest scientifically valid restart?
Can I branch from before the interesting transition?
What changed between two attempts?

Provide machine-readable comparison of start bundles/designs where useful.

⸻

10. PEW EVENT OUTPUT

⸻

Publish execution/provenance events suitable for PEW ingestion without
requiring PEW to understand executor internals.

Events should be idempotent and carry stable identities.

Do not make PEW a synchronous dependency for scientific execution.

If PEW is unavailable:

execution continues where policy permits,
durable evidence is queued/preserved,
and later delivery does not duplicate history.

⸻

11. BENCHMARKS

⸻

Build Vivarium-native fixtures approximating:

HISTORICAL CONTINGENCY:

run a lineage,
checkpoint multiple ancestral states,
evolve a capability that depends on prior state,
replay earlier checkpoints,
prove exact ancestry and changed future accessibility.

CONTROLLED TAKEOVER / ARMS RACE:

inject a small mature foreign lineage,
measure dose and ancestry,
exercise checkpoint/replay,
preserve host and foreign histories,
and verify that a crash during injection cannot produce ambiguous
population state.

Also test:

worker crash,
engine disconnect,
duplicate dispatch,
partial artifact commit,
and resume after process restart.

⸻

12. CRITIQUE AND EXTRA PROPOSALS

⸻

Review the existing Vivarium queue, wrappers, executors and dead-man
machinery.

Explicitly determine:

which Campaign 1–3 runner functionality belongs in Vivarium,
which belongs in SFE,
which is experiment-specific and should remain with Archaeon,
which executor kinds are too special-purpose,
and what abstraction will let the next ten world types arrive without
ten incompatible harnesses.

Propose refinements beyond this directive.

Close with:

VIVARIUM_POINT_RELEASE_REVIEW.md
EXPERIMENT_TRANSACTION_MODEL.md
START_BUNDLE_SCHEMA.md
ARTIFACT_REGISTRY_DELTA.md
VIVARIUM_BENCHMARK_RECEIPT.md
VIVARIUM_RELEASE_PACKET.md

#######################################################################

FINAL CROSS-SEAT INTEGRATION

#######################################################################

No seat closes independently.

After all four release candidates exist, perform one final cross-seat
integration pass.

Construct at least one end-to-end synthetic campaign that:

creates a versioned rich world,
starts a precisely described organism population,
varies pressure over time,
produces floor -> shelf transitions,
checkpoints the run,
forks a counterfactual branch,
injects a controlled foreign lineage,
records capability gain and loss,
emits artifacts,
survives a worker or service interruption,
resumes,
terminates cleanly,
sends evidence to PEW,
rebuilds behavioral projections,
and can be rerun from its original start bundle.

Then ask all four seats independently:

What is wrong with this system now?
What ambiguity remains?
What would fail at 10x duration?
What would fail at 100x observations?
What world can we still not express?
What organism behavior can we still not observe?
What claim could still be accidentally created by instrumentation
rather than evolution?
What deterministic decision is still wasting agent attention?

Consolidate the answers.

Do not automatically implement every suggestion.

Classify them:

MUST FIX BEFORE RELEASE
NEXT POINT RELEASE
MAJOR-VERSION CANDIDATE
SCIENTIFIC QUESTION, NOT BACKEND WORK
REJECT

The final joint packet should make clear that the system can now support
the next phase of Prometheus:

longer runs,
broader populations,
richer organisms,
more dynamic worlds,
more complex pressures,
stronger provenance,
better counterfactual starts,
and more reliable signal detection.

The goal is not zero bugs.

The goal is that when the next surprising effect appears, we can tell:

whether it is real,
where it came from,
what conditions produced it,
how to attack it,
and exactly how to run the next experiment.
