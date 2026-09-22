# Operator amendment 1, received in chat 2026-09-17 (Mnemosyne instance m2-9c10ae00), verbatim

PROMETHEUS BACKEND POINT-RELEASE CAMPAIGN
OPERATOR AMENDMENT 1 — SCOPE, OWNERSHIP, SEQUENCING

This amendment supersedes any part of the original point-release directive
that conflicts with it.

It is issued after initial read-only review from:

Daedalus / SFE
Vivarium
Mnemosyne / PEW

Proteus review is still required.

The reviews did what they were intended to do.

They found that the original directive contained useful architectural
directions but assigned too much work to some layers and blurred several
ownership boundaries.

The release is therefore NARROWED.

Do not manufacture work to satisfy the original outline.

Do not implement a feature merely because it appeared in the operator
prompt.

Implement only what repository evidence, campaign evidence and interface
needs justify.

=======================================================================

1. GOVERNING DEVELOPMENT MODEL
    =======================================================================

Use this model going forward:

SCIENCE DISCOVERS A MISSING MECHANIC
    ->
ARCHAEOLOGICAL / CAMPAIGN LAYER IMPLEMENTS A LOCAL PROTOTYPE
    ->
MULTIPLE RUNS EXERCISE IT
    ->
SEAT REVIEW DETERMINES WHETHER THE SEMANTIC IS STABLE
    ->
THE CORRECT BACKEND OWNER ABSORBS THE MECHANIC
    ->
SCIENTIFIC INTERPRETATION REMAINS ABOVE THE BACKEND

Archaeon is allowed to prototype experimental machinery in order to keep
science moving.

That does not automatically mean Archaeon's abstraction belongs in SFE,
Vivarium, PEW or Proteus.

Promotion downward requires evidence that the mechanic is:

repeated,
general,
scientifically neutral,
and stable enough to own as infrastructure.

This is now explicit policy.

=======================================================================
2. DO NOT MOVE INTERPRETATION DOWNWARD

The reviews unanimously expose an important boundary.

Backend layers should preserve enough facts to reconstruct interpretations.

They should not become the interpretation.

Examples:

SFE stores:
    logical time,
    termination reason,
    world events,
    cost facts,
    checkpoints,
    manifests,
    observations.
It does NOT universally define:
    FLOOR,
    SHELF,
    SUMMIT,
    0.45,
    0.90,
    "corridor",
    "generalization".
PEW stores:
    measurements,
    events,
    lineage observations,
    provenance.
It may build VERSIONED projections such as:
    summit_v2,
    forgetting_v1,
    takeover_v1.
The projection definition and source evidence must remain visible.
Vivarium stores:
    attempts,
    steps,
    bundles,
    replay,
    artifacts,
    receipts.
It does NOT decide:
    whether an experiment's outcome is scientifically positive,
    whether 0.5 is a shelf,
    or whether an imported lineage was useful.
Proteus stores:
    organism identity,
    structural description,
    runtime/foundry profile,
    observed capability evidence.
It does NOT silently feed those descriptive labels back into live
    mutation or selection.

Keep this separation aggressively.

=======================================================================
3. RELEASE SEQUENCING

Campaign 3 is active.

No backend mutation should be trickled into the running campaign unless a
critical defect requires it.

The point release should use one coordinated deploy/migration window after
Campaign 3 closes.

Until then:

review,
inventory,
design,
critique,
interface drafting,
test design

are allowed.

Production mutation is not.

This applies to:

engine schema/routes,
Vivarium migrations/deployment,
PEW migrations,
Proteus runtime/foundry semantics.

Additive code may be prepared in isolated worktrees.

Do not alter the active scientific substrate.

=======================================================================
4. ARCHAEOLOGICAL SOURCE OF TRUTH

Campaigns 1–3 produced experimental infrastructure that is currently
distributed across:

archaeon/campaign*/
archaeon/wse/
receipts
ledgers
reachability
corridor tables
runner code
traces

These artifacts are not temporary junk.

They are the empirical specification for the point release.

For each candidate backend feature, identify:

the exact current implementation,
campaign(s) that exercised it,
observed failure that motivated it,
recurrence count,
and whether the mechanic survived later redesign.

Do not replace an already proven mechanism with a prettier abstraction
without evidence.

=======================================================================
5. REVISED DAEDALUS SCOPE

Daedalus's push-back is ACCEPTED.

The SFE point release should be smaller than the original prompt.

PRIMARY SFE RELEASE ITEMS:

A. OBSERVATION / WORLD FACTS

Add or formalize stable, non-interpretive facts such as:

logical_time / generation on observations/events where applicable
typed termination:
    reason
    budget_consumed
    horizon / censoring-relevant state
parent_world
fork_point
checkpoint state digest
child-vs-parent changed-field diff
attempt label if the interface ownership review agrees

Do not add universal shelf/summit semantics.

B. WORLD MANIFEST ENVELOPE

Add a generic versioned envelope:

manifest
manifest_schema
manifest_hash

SFE validates the envelope.

The manifest owner defines content semantics.

Support generic stamped world events where useful.

Do not make the engine understand every pressure type.

C. READ-SURFACE FIXES

Prioritize:

GET /v2/worlds/{wid}/artifacts
documented advisory read/session semantics
consistent strict-body behavior
capability/vocabulary discovery

Do not loosen strict request bodies merely to avoid 422s.

D. LONG-RUN READABILITY AND DURABILITY

Highest-value engine work:

cursor pagination
long-run storage measurement
retention-policy measurement/decision
reconnect/restart/duplicate-post fixture
checkpoint/restart fixture
hour-scale or accelerated-equivalent load test

E. INSTRUMENT FACTS, NOT INTERPRETATIONS

Ensure the engine can preserve facts needed by higher projections:

phase/world events
logical time
termination
costs
supplied lineage-share observations
checkpoint identity
manifest identity

F. WORLD OBJECTS

Daedalus's rejection is ACCEPTED.

Queues, locks, channels, TTL stores and similar world mechanics do NOT
become SFE server services by default.

Prototype/share these in a world library:

sfclient/worldlib
or another reviewed neutral location

The engine owns generic event and cost semantics.

The world library owns experimental mechanics.

G. QD PROJECTION

DEFER as an engine route.

Library/projection first.

Promote only if repeated independent consumers need an identical server
projection.

=======================================================================
6. REVISED VIVARIUM SCOPE

Vivarium's central observation is ACCEPTED:

Campaigns 1–3 did NOT execute through Vivarium.

Archaeon's runner has independently evolved durable-execution machinery.

The point release therefore asks Vivarium to ABSORB PROVEN SEMANTICS,
not pretend it already owned them.

PRIMARY VIVARIUM RELEASE ITEMS:

A. TRANSLATION CONTRACT FIRST

Document the relationship between:

Archaeon:
    campaign
    experiment
    design
    attempt
    step

and Vivarium:

    candidate/family where applicable
    experiment row
    spec_hash
    repeat
    observation

Do not merge the hierarchies unnecessarily.

Publish the join.

Use UNKNOWN where no owner exists.

B. ATTEMPT / STEP SEMANTICS

Add the smallest additive schema required for:

explicit attempts,
parent attempt,
step identity,
design-keyed step idempotency,
replay/recompute distinction,
partial progress receipts.

Never silently retry.

Use:

NEW ATTEMPT

unless a step is explicitly declared safely replayable/idempotent.

C. START BUNDLE

Proceed.

A hashed first-class start bundle is approved.

A changed start condition means:

DERIVED DESIGN

not "same experiment".

D. PEW OUTBOX

This is a high-value point-release item.

Implement a durable producer-side outbox for execution/provenance events.

PEW must remain asynchronous.

A PEW outage must not make completed execution ambiguous.

E. EXTERNAL EXECUTION

Vivarium's narrowing is ACCEPTED.

Do not dump GPU/external/stream kinds into the existing pure-kind registry.

Design a second explicit bounded executor class with:

lease
step log
checkpoint contract
declared external requirements

Ship one fixture first.

Generalize only after it works.

F. CHECKPOINT / FORK / HISTORICAL CONTINGENCY

DEPENDENT on Daedalus's reviewed snapshot surface and Proteus population
identity/start semantics.

Do not mock the missing interfaces and call the benchmark complete.

G. IMPORT

Vivarium records:

intended dose
realized dose
timing
identities
receipt/failure

Vivarium does not choose ecological dose.

H. DATABASE

Keep PostgreSQL.

Do not add Redis merely to satisfy an event-sourcing analogy.

=======================================================================
7. REVISED MNEMOSYNE SCOPE

Mnemosyne's most important finding is ACCEPTED:

PEW currently does not receive the SFE campaigns.

Therefore PEW's Stage 0 begins with INGESTION, not ontology invention.

PRIMARY PEW RELEASE ITEMS:

A. CAMPAIGN INGESTION CONTRACT

Start from the evidence Archaeon already emits:

receipts
ledger rows
reachability rows
corridor rows
generation traces
SFE identities

Do not invent a competing vocabulary.

Define translation into PEW.

Archaeon remains owner of the scientific definitions it minted.

B. RAW VS PROJECTION

Adopt Mnemosyne's proposed distinction.

RAW examples:

WORLD_STARTED
WORLD_PHASE_CHANGED
WORLD_TERMINATED
PRESSURE_APPLIED
PRESSURE_REMOVED
ORGANISM_OBSERVED
CAPABILITY_MEASURED
ARTIFACT_PUBLISHED
ARTIFACT_IMPORTED
INTERVENTION_APPLIED
LESION_APPLIED
ATTEMPT_RESTARTED
ATTEMPT_REPLAYED
LINEAGE_SHARE_OBSERVED

Only include event families that have a producer.

Do not create empty tables as evidence of capability.

PROJECTION examples:

SHELF_REACHED
SUMMIT_REACHED
CAPABILITY_GAINED
CAPABILITY_LOST
LINEAGE_TAKEOVER
CORRIDOR_OBSERVED
FORGETTING_EVENT

Every projection pins:

definition version
source events
thresholds/rules
owning scientific schema
build/rebuild procedure

C. IDENTITY ENVELOPE

Add typed provenance coordinates for:

campaign
experiment
design
attempt
step
foundry profile
schedule identity
RNG identity

with clear distinctions between:

UNKNOWN
NOT_APPLICABLE / NULL

Ownership follows the originating seat.

PEW consumes.

D. PRODUCER CHECKPOINTS

Add ingestion sequence/checkpoint semantics.

Stable event ID should support:

duplicate delivery -> no-op
missing sequence -> visible gap

Do not silently heal missing evidence.

E. SCALE

Mnemosyne's measurement is accepted.

Do NOT emit one PEW row for every organism-generation by default.

Prefer campaign/world/generation-granularity summaries plus references to
bulk traces where the scientific question does not require individual
organism events.

Use evidence-driven granularity.

F. POST-CAMPAIGN EXPLANATION

DEFER the ambitious explanation surface until at least one real campaign
has been ingested end-to-end.

First prove:

ingest,
identity,
replay,
projection rebuild,
queryability.

G. STORE LOCATION

This is elevated to a RELEASE-BLOCKING architecture question.

Do not declare PEW the evidence substrate for this ecosystem while its
canonical store remains operationally orphaned on a machine owned by
another ecosystem with uncertain backup ownership.

Resolve:

canonical host
backup ownership/location
restore procedure
migration/deploy authority

before productionizing campaign ingestion.

=======================================================================
8. PROTEUS MUST REVIEW BEFORE IMPLEMENTATION

Proteus has not yet supplied equivalent review.

Do not freeze the final point-release scope until Proteus has completed a
read-only audit.

Proteus must answer at minimum:

What is immutable registry identity?
What is dictionary evidence?
What current profiles are scientifically frozen?
What fields already exist for:
    parents
    representation version
    semantic version
    genome hash
    runtime/foundry identity?
What would a capability/evidence model duplicate?
What organism ABI extensions are genuinely required by richer worlds?
Which extensions would merely explode the search space?
How should TRUE/FALSE/UNKNOWN/NOT_MEASURED/CONFLICTING_EVIDENCE align
with existing PEW typed vocabularies?
What information can be exported to PEW without allowing PEW to
contaminate player generation/selection?
What exact start-population manifest should Vivarium consume?
Which structural operators constitute genuinely new search geometry
rather than parameter noise?

Proteus must also review Campaign 3 before proposing richer organisms.

If current organism limitations are NOT yet the frontier constraint, say
so.

Do not expand the organism instruction set merely because the operator
asked for "better organisms."

=======================================================================
9. OWNERSHIP ARBITRATION

Stage 3 needs an arbiter.

ARCHAEON is the tie-breaker for ownership disputes involving campaign
mechanics because Archaeon is the primary scientific consumer and has
implemented the prototypes being promoted.

This does NOT give Archaeon unilateral control over backend architecture.

Use this escalation order:

seats attempt resolution
    ->
write competing ownership arguments
    ->
Archaeon chooses based on scientific-consumer semantics
    ->
Harmonia may audit scientific-validity implications if needed
    ->
operator only if the disagreement changes project policy rather than
implementation ownership.

Do not stall waiting for consensus on a reversible choice.

=======================================================================
10. FUTURE CAMPAIGN RUNNER

The point release must settle one important question:

What executes Campaign 4?

The current state risks two durable-execution implementations diverging:

Archaeon's campaign runner
Vivarium

The desired trajectory is:

Archaeon's runner remains the INCUBATION/reference implementation
during this point release.
Vivarium absorbs the generic stable attempt/step/start-bundle/replay
semantics.
A qualification run demonstrates that a future Archaeon campaign can
submit through Vivarium without losing scientific control.

Do NOT force Campaign 4 through Vivarium unless that qualification passes.

Scientific progress outranks architectural purity.

If Vivarium is not ready, Campaign 4 may use Archaeon's proven runner
while the migration continues.

Record that as debt, not failure.

=======================================================================
11. MIGRATION FREEZE RULE

Formalize the operational rule exposed by Campaign 3:

WHILE A SCIENTIFIC CAMPAIGN IS ACTIVE ON THE PRODUCTION SUBSTRATE:

no unneeded engine route/schema changes,
no PEW schema migrations affecting campaign ingestion,
no Vivarium production-schema migration,
no Proteus semantic-profile mutation.

Exceptions:

critical defect
data-loss risk
security/integrity defect
campaign-blocking compatibility bug

must be explicitly recorded.

Prefer one coordinated deploy window between campaigns.

=======================================================================
12. RELEASE SCOPE DISCIPLINE

This is a POINT RELEASE.

Every seat must produce:

MUST SHIP
SHOULD SHIP IF CHEAP
DEFER TO NEXT POINT RELEASE
MAJOR VERSION CANDIDATE
REJECT

Do not turn every worthwhile architectural idea into this release.

Especially defer:

speculative distributed infrastructure,
unexercised event families,
generic executor ecosystems,
server-side QD archives,
major organism-language redesign,
automatic causal inference,
and large world-service frameworks

unless evidence from the three campaigns demonstrates they are necessary
now.

=======================================================================
13. REVISED SUCCESS CRITERION

The release succeeds if the next scientific campaign gains:

cleaner identities,
durable attempts/steps,
better replay,
better start-condition control,
reliable artifact/read surfaces,
typed logical time and termination,
long-run pagination/durability,
better campaign evidence ingestion,
rebuildable PEW projections,
stronger organism provenance,
and fewer repeated infrastructure decisions.

It does NOT need to deliver every future abstraction.

The goal is not feature count.

The goal is moving the failure frontier.

Campaign 1 mostly found instrumentation and execution defects.

Campaign 2 mostly found assay/design defects and real landscape geometry.

Campaign 3 is beginning to ask harder substrate questions.

The point release should make Campaign 4 less likely to rediscover backend
holes and more likely to fail or succeed for scientifically interesting
reasons.

=======================================================================
14. NEXT ACTION

Proceed now with READ-ONLY Stage 0 and Stage 1 work.

No production mutation until Campaign 3 closes and the deploy window is
opened.

Daedalus:
write the narrowed SFE_POINT_RELEASE_REVIEW.md and proposed delta.

Vivarium:
write the evidence inventory and identity translation contract first.

Mnemosyne:
write the campaign-ingestion translation contract and store-location
risk disposition first.

Proteus:
boot/review immediately and return the equivalent scope critique before
implementation scope freezes.

Then conduct Stage 3 peer review on the ACTUAL narrowed proposals, not on
the original operator wish list.

After that, freeze the point-release scope.

Implement.

Benchmark.

Integrate.

Critique again.

Ship only what earned its way in.
