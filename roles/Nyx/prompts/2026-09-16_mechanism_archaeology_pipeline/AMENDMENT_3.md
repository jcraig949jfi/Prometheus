PROMETHEUS MECHANISM ARCHAEOLOGY PIPELINE

Amendment 3 — Return Protocol, Prediction Schema, World Normalization, and Intervention Provenance

This amendment modifies the Founding Charter and Amendments 1–2.

Where conflict exists, this amendment controls.

⸻

R31 — EVERY HANDOFF HAS A SYMMETRIC RETURN

R9 remains binding and is generalized.

Every downstream stage must return a typed disposition to the stage that produced the object.

No gate may remain silently open.

Canonical returns include:

TECHNE → NYX
    BODY_CHALLENGE
    PROVENANCE_CHALLENGE
    WORLD_CHALLENGE
NYX → TECHNE
    PROVENANCE_CHALLENGE
    WORLD_RECONSTRUCTION_CHALLENGE
HARMONIA → NYX
    CUT_CHALLENGE
    PREDICTION_FAILED
    PREDICTION_INDETERMINATE
    CUT_SUPPORTED
HARMONIA → TECHNE
    WORLD_RECONSTRUCTION_CHALLENGE
    INSTRUMENT_CHALLENGE
    ORACLE_PROVENANCE_CHALLENGE
THEOPHRASTUS → HARMONIA
    SURROGATE_CHALLENGE
    EQUIVALENCE_CHALLENGE
THEOPHRASTUS → NYX
    MECHANISM_BOUNDARY_CHALLENGE
ARCHAEON / VIVARIUM → THEOPHRASTUS
    LANDSCAPE_CHALLENGE
    PAYLOAD_NULL_FAILURE
ARCHAEON / VIVARIUM → NYX
    CUT_CONSUMPTION_CHALLENGE

Additional typed returns may be added, but generic silent rejection is forbidden.

Every return identifies:

source_object_id
return_type
evidence
responsible_stage
responsible_seat
returned_tick
required_response

Latency

Unless a stage-specific rule is stricter:

ACK       ≤ 1 pipeline tick
DISPOSITION ≤ 2 pipeline ticks

Disposition is one of:

ACCEPT
REJECT
DEFER
CHALLENGE

DEFER requires:

blocker
accountable seat
evidence required
next due tick

A third unresolved tick escalates to the operator.

Gate latency itself becomes a pipeline metric.

⸻

R32 — NYX STAGE C/D ADJUDICATION IS SUPERSEDED

Explicit ruling:

The portions of the prior NYX ATLAS charter directing Nyx to perform adjudicative ablation and behavioral fingerprint verification on its own cuts are superseded for the Mechanism Archaeology Pipeline.

NYX owns:

Stage A — dissection
Stage B — cut construction
Stage C' — prediction + intervention specification
Stage D' — downstream response assimilation

NYX does not own the adjudicative experiment on its own cut.

Exploratory execution remains permitted but must be labeled:

SCOUT / SEEN / NON-ADJUDICATIVE

Formal ablation and equivalence move downstream.

Nyx may continue A/B work while downstream gates operate, but atlas growth must not be used to conceal stalled falsification.

The ledger therefore reports both:

cuts_created
cuts_returned_with_verdict

and their latency.

⸻

R33 — NYX_PREDICTION_PACKET / SCHEMA V1

The packet is frozen before Harmonia R1 opens.

Required fields:

schema_version
prediction_packet_id
created_at
chopper_identity
chopper_version
cut_id
fossil_raw_id
payload_manifest_id
provenance_grade_read
boundary:
    file_path
    file_payload_hash
    line_start
    line_end
    optional symbol/function

Every boundary reference is bound to the actual bytes read.

A path and line range without the file payload hash is invalid.

For multi-region cuts, boundary[] contains all regions.

⸻

Mechanism claim

mechanism_claim:
    concise functional claim
    claimed inputs
    claimed outputs/effects
    claimed internal dependency
    known uncertainty

The claim is a hypothesis.

It is not an ontology assignment.

⸻

Intervention predictions

Each formal intervention contains:

intervention_id
intervention_level
intervention_operation
measured_observable
expected_direction
expected_magnitude_band
units
band_basis
test_world_scope
pressure_scope
prediction_rationale

expected_direction must be explicit:

INCREASE
DECREASE
UNCHANGED
NON_MONOTONIC
REGIME_DEPENDENT

A prediction that cannot state an observable and a falsifiable magnitude band is not ready for adjudicative execution.

Broad bands are acceptable when justified.

Unbounded language such as:

“something interesting may happen”

is not.

⸻

Controls

Required:

CHEAT / PAYLOAD-READING CONTROL

control_id
control construction
expected result
failure interpretation

POSITIVE CONTROL

A condition in which the experimental instrument must demonstrate that it can observe the relevant effect.

control_id
expected detectable effect
expected result
failure interpretation

Where no scientifically honest positive control exists, the packet states:

POSITIVE_CONTROL_UNAVAILABLE

with reason.

Such a packet may be explored but cannot receive the strongest evidentiary grade.

⸻

Two mandatory losing outcomes

Every packet defines:

CUT_KILL

The observation that would invalidate the proposed boundary/function sufficiently to require a new CUT rather than reinterpretation.

INDETERMINATE

The observation that would mean the experiment failed to distinguish the hypothesis from alternatives.

Examples:

instrument underpowered
oracle conflict unresolved
surrogate divergence contaminates intervention
effect below preregistered discrimination threshold
control failure

INDETERMINATE is not converted into support or rejection.

⸻

Freeze rule

The complete packet is serialized canonically and hashed before Harmonia R1 opens.

Corrections require a new packet ID linked by:

SUPERSEDES

The old prediction remains immutable.

⸻

R34 — CUT FORMAT / PROVENANCE READ REQUIREMENT

Every CUT records the exact provenance-grade object Nyx actually inspected.

Required fields now include:

provenance_grade_read
source_object_id
payload_manifest_id
files_read:
    path
    payload_hash

A cut against:

LATER_TRANSCRIPTION

is not silently treated as a cut against:

ORIGINAL_ARTIFACT

even when one claims to represent the other.

Existing cuts may be migrated by dated schema evolution, but the original record remains preserved.

For the current 30 cuts, Techne provenance is used to populate the new field and file hashes.

⸻

R35 — MKW-1 GETS AN INTERIM READOUT

The terminal wager remains:

MKW-1 @ N=50 independently resurrected and admitted mechanism cuts

The threshold does not move.

Add:

MKW-1-I10

At:

N = 10

produce a non-verdict diagnostic.

For every candidate cross-lineage relation, report which MKW-1 conditions currently pass or fail:

1 distinct historical lineages
2 measurable surface displacement
3 replication
4 survives ablation
5 survives payload-reading null
6 not explained by shared implementation/fixture

Example:

candidate X
1 PASS
2 PASS
3 FAIL
4 NOT TESTED
5 NOT TESTED
6 PASS

The N=10 readout does not satisfy or falsify MKW-1.

Its purpose is to expose the shape of failure before N=50.

If all candidates fail at the same condition, that becomes evidence about the representation or experiment design.

⸻

Dependency: ancestry vocabulary

MKW-1 condition 1 is not decidable until Techne’s ancestry graph has directional semantics sufficient to determine independent historical lineages.

The current ambiguous superseded relationship must be replaced or qualified.

At minimum distinguish:

SUPERSEDES
SUPERSEDED_BY
DERIVES_FROM
TRANSCRIBES
RECONSTRUCTS
FORKS_FROM
INDEPENDENT_LINEAGE

MKW-1 cannot count N until ancestry adjudication is deterministic.

⸻

R36 — FOSSIL_WORLD_MANIFEST CANONICALIZATION

FOSSIL_WORLD identity must be host-independent.

Canonical encoding:

UTF-8
LF line endings
canonical JSON
keys sorted lexicographically
arrays with defined ordering
exactly one terminal LF byte

Versions are stored as strings.

No locale-specific normalization.

No timestamps, hostnames, temporary paths, image IDs, or other witnesses enter the semantic manifest unless explicitly part of the fossil world’s required behavior.

Package entries are sorted by:

(normalized package name, architecture, version string)

Toolchains are sorted by:

(tool class, canonical name, version string)

Environment variables record:

name
semantic value if required by world

Ephemeral secrets and host-specific values do not enter the manifest.

Identity:

FOSSIL_WORLD_ID =
SHA256(canonical_manifest_bytes)

Image/container/VM hashes are attached separately as:

RUNTIME_WITNESS

Multiple witnesses may instantiate the same FOSSIL_WORLD.

The normalization implementation receives its own fixtures, including:

different input ordering → same ID
CRLF vs LF source serialization → same ID
different image witness → same world ID
different package version → different world ID

⸻

R37 — INTERVENTION CAPABILITY HAS A LEVEL

INTERVENE is not one capability.

Every intervention declares one of:

SOURCE
BUILD_BINARY
RUNTIME_STATE
TESTBENCH
ENVIRONMENT

SOURCE

Example:

edit deflate.c and rebuild.

Creates:

new PAYLOAD_MANIFEST_ID
new derived-body identity
scaffolding/intervention edge to parent

It does not overwrite the fossil.

⸻

BUILD_BINARY

Examples:

link substitution
compiler flag change
binary patch
alternate library binding

Creates a new build/binary witness and explicit ancestry.

⸻

RUNTIME_STATE

Examples:

poke memory
alter register
modify live table
inject state
change scheduler state

The underlying payload may remain unchanged.

The execution receives a distinct intervention/run witness.

⸻

TESTBENCH

Examples:

arbiter stimulus
fault injection harness
input perturbation apparatus

The specimen remains unchanged.

The experimental apparatus changes.

⸻

ENVIRONMENT

Examples:

memory restriction
latency injection
package/runtime substitution
resource starvation

Produces a distinct environment/intervention identity as applicable.

⸻

The capability matrix therefore includes:

verb
supported
intervention_level(s)
provenance mechanism

Example:

INTERVENE   yes   SOURCE,RUNTIME_STATE
SNAPSHOT    yes   RUNTIME_STATE
TRACE       yes   RUNTIME_STATE

This distinction must survive into Theophrastus cells.

⸻

R38 — OFF-HOST PRESERVATION IS AN EXPLICIT PILOT GATE

R25 remains binding.

Current state:

M1 local vault
M2 re-materialization / re-fetch
upstream source control

does not yet constitute the independent preservation copy required for a canonical dependency if these remain within the same operational failure domain or cannot preserve all required artifact classes.

Therefore:

The gzip pilot may proceed through exploratory and validation stages, but it may not be designated the canonical reference lineage until the R25 preservation gate is satisfied.

Required operator decision:

TECHNE-65 — designate independent preservation destination/class

Techne’s existing mirror machinery should then:

copy
verify
record destination class
record object hashes
record verification receipt

No scientific execution needs to be discarded while this is unresolved.

The lineage simply remains:

NON_CANONICAL / PRESERVATION_GATE_OPEN

until the receipt exists.

⸻

R39 — FIRST PILOT RECORD IS COMPLETE FROM BIRTH

The gzip pilot must contain, before downstream execution:

FOSSIL_RAW_ID
PAYLOAD_MANIFEST_ID
provenance_grade
FOSSIL_WORLD_ID
RUNTIME_WITNESS
HOST_CAPS_ID
SCAFFOLDING_LEDGER
PRESERVATION_STATUS
CUT_ID
provenance_grade_read
files_read + payload hashes
NYX_PREDICTION_PACKET_ID
RS_CALIBRATION_PAIR_ID
ORACLE_SOURCE identities
ORACLE grades
typed return deadlines
responsible seats

Later stages append evidence.

They do not retrofit foundational identity fields.

⸻

IMMEDIATE NYX AUTHORIZATION

Nyx’s proposed actions are approved.

N1

Mark formal ATLAS Stage C/D adjudication superseded.

Continue Stage A/B on the remaining NOT_CUT population under the revised CUT schema.

N2

Create and freeze:

NYX_PREDICTION_PACKET schema/1

Then instantiate:

MECH-GZIP-LEVELTABLE-001

against exact boundaries:

deflate.c:225-245
deflate.c:286-356

bound to file payload hashes.

Include:

per-level predictions
direction
magnitude bands
pre-compressed cheat control
positive control
CUT_KILL
INDETERMINATE

Freeze by hash before Harmonia opens R1.

N3

File:

Rockliff 1991 RS → Karn RS

as Harmonia’s calibration specimen.

The verifier must recover:

errors-only:
    agreement
tt+1 errors:
    Rockliff silent pass-through
    Karn → -1

A ruler that misses that distinction cannot judge the gzip surrogate.

N4

Version the CUT format and add:

provenance_grade_read
source_object_id
payload_manifest_id
per-file payload hashes

Preserve old records and migration ancestry.

⸻

FIRST REQUIRED RETURN

The first meaningful evidence that this pipeline is alive will not be another CUT.

It will be something like:

RETURN_TYPE:
    CUT_CHALLENGE
FROM:
    Harmonia
TO:
    Nyx
CUT:
    <immutable CUT_ID>
EVIDENCE:
    intervention effect begins outside frozen boundary
    or predicted boundary fails under verified oracle
DISPOSITION:
    REJECT / CHALLENGE
REQUIRED_RESPONSE:
    produce new CUT_ID;
    old CUT remains immutable

If that event changes Nyx’s decomposition while preserving the rejected cut and its evidence, the pipeline has completed its first genuine learning cycle.

It has ceased being a one-way archive.

It has become a falsifying metabolism.
