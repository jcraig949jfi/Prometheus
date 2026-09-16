PROMETHEUS MECHANISM ARCHAEOLOGY PIPELINE

Amendment 2 — World Reconstruction, Oracle Provenance, and Instrument Integrity

This amendment modifies the Founding Charter and Amendment 1.

Where this amendment conflicts with either, this amendment controls.

⸻

R16 — TECHNE OWNS HISTORICAL WORLD RECONSTRUCTION

The boundary between Techne and Harmonia moves.

Techne does not merely acquire a body.

Techne owns reconstruction of the historical execution context sufficiently far to determine what can actually be made to run.

Its terminal question is:

What artifact survived, what world did it require, what scaffolding was necessary to reconstruct that world, and how far toward historical behavior can we demonstrably get?

This includes archaeological work such as:

* locating historical or compatible assemblers;
* reconstructing assumed macro libraries;
* finding system tapes;
* identifying undocumented runtime assumptions;
* rebuilding emulators;
* discovering modern-toolchain incompatibilities;
* identifying historical datasets and tables;
* applying explicit compatibility scaffolding;
* determining whether apparent fossil failure is actually instrument failure.

This work is acquisition archaeology.

It must not be duplicated downstream.

Harmonia therefore begins at R1, not R0.

⸻

R17 — TECHNE REPRODUCTION IS A LATTICE, NOT A BOOLEAN

Replace the single state:

HISTORICALLY_REPRODUCED

with the following evidence lattice:

BODY_RECOVERED
      ↓
BODY_RECOVERED_WORLD_NAMED
      ↓
WORLD_RECONSTRUCTED
      ↓
WORLD_EXECUTABLE
      ↓
BODY_EXECUTABLE
      ↓
BEHAVIOR_PARTIALLY_REPRODUCED
      ↓
BEHAVIOR_REPRODUCED

These are not interchangeable.

Examples of valid terminal states include:

world reconstructed
but body does not execute
world executable
body assembles word-exact
job does not run
body executes
published behavior not reproduced
behavior reproduced
with provenance-qualified scaffolding

Techne records the highest state supported by evidence.

It does not round upward.

A fossil may proceed to Harmonia only when the required downstream experiment is possible at its actual state.

⸻

R18 — CREATE THE SCAFFOLDING LEDGER

The rule:

“Techne must not modernize the artifact”

is replaced by a stronger and falsifiable requirement:

The historical body is never silently changed. Every transformation required to materialize or execute a derived copy is explicit, attributable, reversible where practical, and preserved in the scaffolding ledger.

Each transformation records:

transformation_id
source object
derived object
reason
sites affected
exact operation
tool performing operation
evidence requiring it
provenance grade
whether applied
whether reversible
effect on execution

The ledger also records:

MEASURED_AND_REJECTED

transformations.

Those are first-class evidence.

Example:

historical body
   │
   ├── transformation A — applied
   ├── transformation B — applied
   ├── transformation C — tested, rejected
   └── transformation D — applied
             ↓
       runnable materialization

“Runs” without this ledger is insufficient where scaffolding occurred.

⸻

R19 — HISTORICAL BODY AND RECOVERY ARTIFACTS REMAIN DISTINCT

An authentic transcription, later reconstruction, emulator image, reconstructed table, recovery-project tarball, and historical binary are separate objects.

They must never be silently merged into one “fossil.”

Possible provenance grades include:

ORIGINAL_ARTIFACT
CONTEMPORARY_COPY
AUTHENTIC_TRANSCRIPTION
LATER_TRANSCRIPTION
RECONSTRUCTION
DERIVED_RECOVERY_ARTIFACT
AUTHOR_STATED
UNKNOWN

A later reconstruction may be extremely useful.

It does not become original merely because it works.

Edges express relationships:

TRANSCRIBES
RECONSTRUCTS
DERIVES_FROM
PACKAGES
CORRECTS
CLAIMS_EQUIVALENCE_TO

Equivalence remains evidence-dependent.

⸻

R20 — TECHNE SHOULD SEARCH FOR RECOVERY PROJECTS, NOT JUST OLD SOFTWARE

Pre-modern machine-readable bodies often survive because a later person or institution performed a recovery effort.

Techne therefore treats recovery projects as first-class acquisition targets.

Search targets include:

* named reconstruction efforts;
* museum computing projects;
* emulator communities;
* software-preservation projects;
* researcher-maintained historical archives;
* recovered tapes and decks;
* transcription projects;
* restored source distributions;
* reconstructed machine images.

The recovery project’s artifacts must still be provenance-separated according to R19.

The existence of a recovery project raises acquisition priority.

It does not raise scientific priority.

⸻

R21 — SPLIT THREE DIFFERENT “WORLDS”

The word world was overloaded.

Prometheus now distinguishes:

FOSSIL_WORLD

The reconstructed historical execution environment required by the fossil.

Examples:

PDP-1 + emulator + macro library + assembler assumptions
IBM 7090 environment
OS/2 installation
historical UNIX userspace
specific Python/runtime ecosystem

Its identity is measurement-based.

It includes an environment manifest such as:

architecture
OS / guest identity
toolchain versions
package manifest hash
interpreter/compiler identity
required libraries
relevant configuration
environment-variable schema

The VM/container/image digest is a witness, not the semantic identity by itself.

Rebuilding an equivalent environment may therefore produce:

same FOSSIL_WORLD_MANIFEST
different IMAGE_WITNESS

That is allowed.

⸻

RUNTIME_WITNESS

The actual instantiated machinery used for one run:

image digest
VM digest
emulator build
host-visible runtime
container digest
materialization hash

This is execution provenance.

⸻

TEST_WORLD

The scientific environment used by Theophrastus or Vivarium.

This remains the w in:

[
T[m,p,w,b,i,t,\ldots]
]

Examples include:

search landscape
task distribution
ecology
dataset regime
adversarial environment
resource regime
partial-observation environment

Therefore:

FOSSIL_WORLD is not automatically tensor coordinate w.

A historical environment may itself later become an experimental TEST_WORLD if intentionally varied, but that is a scientific decision, not an identity accident.

⸻

R22 — FOSSIL RUNTIME IS A CAPABILITY MATRIX

Do not require every reconstructed environment to implement one universal runtime interface.

Each FOSSIL_WORLD declares supported capabilities.

Canonical verbs may include:

INSTANTIATE
EXECUTE
OBSERVE
SNAPSHOT
RESTORE
STEP
TRACE
EXAMINE
WATCH
INTERVENE
SCREENSHOT
INJECT_INPUT
EXTRACT_OUTPUT

A world publishes:

capability      supported
-----------     ---------
INSTANTIATE     yes
EXECUTE         yes
OBSERVE         yes
SNAPSHOT        no
INTERVENE       no
STEP            no
TRACE           partial

Different world classes may expose different mechanisms.

The pipeline must adapt experiments to declared capability.

It must not fabricate equivalence between unavailable verbs.

Techne’s existing harvest run is recognized as an existing implementation of part of this abstraction.

⸻

R23 — ORACLES HAVE PROVENANCE

Harmonia must not treat “historical executable output” as the only valid oracle.

An oracle observation may derive from:

EXECUTION
CONTEMPORARY_DOCUMENT
CONTEMPORARY_LISTING
HISTORICAL_DATASET
AUTHOR_STATEMENT
LATER_RECONSTRUCTION
RECOVERY_PROJECT
MODERN_REFERENCE_IMPLEMENTATION

Every oracle datum receives:

oracle_source
provenance_grade
artifact identity
measurement method
uncertainty
conflicts

Oracles may disagree.

Disagreement is not automatically repaired.

Example:

historical listing scan      → value A
later transcription listing  → value B
modern execution             → value B

Harmonia records the conflict and its evidentiary basis.

It does not automatically crown the executable.

⸻

R24 — VERIFY THE INSTRUMENT BEFORE READING THE FOSSIL

Add constitutional rule:

C11 — INSTRUMENT BEFORE SPECIMEN

An apparent fossil failure cannot count as fossil evidence until the relevant modern instrument has survived controls capable of revealing instrument failure.

Modern tools are themselves mechanisms under pressure.

This includes:

* assembler;
* compiler;
* emulator;
* interpreter;
* parser;
* container;
* compatibility layer;
* numerical library;
* tracing system.

Controls should be appropriate to the instrument.

Possible evidence includes:

known-good program
known-good deck
reference binary
cross-toolchain comparison
historical output
alternate emulator
minimal parser fixture
round-trip test

The 752 false LISP errors and the Spacewar parser failure are now canonical examples of:

INSTRUMENT_FAILURE_MASQUERADING_AS_FOSSIL_FAILURE

Such events remain in the ledger.

⸻

R25 — PHYSICAL PRESERVATION IS PART OF C1

Logical hashes without independent physical preservation do not satisfy:

PROVENANCE NEVER BREAKS

Any artifact required to reconstruct a claimed lineage must have at least one independent off-host preservation copy before it can become a canonical pipeline dependency.

This includes, where legally and practically possible:

raw bodies
source bundles
disk/tape images
world images
unique recovery artifacts
oracle documents
critical toolchains

A second checkout from the same local storage failure domain is not sufficient.

The preservation record includes:

object identity
copy location/class
verification time
verification result

Loss of a preservation replica does not invalidate prior science.

It does create an operational preservation failure.

⸻

R26 — HARMONIA STARTS AT R1

Harmonia receives:

FOSSIL_ID
FOSSIL_WORLD_ID
RUNTIME_WITNESS
SCAFFOLDING_LEDGER
TECHNE_EXECUTION_RECEIPTS
ORACLE_SOURCES
CUT_ID
NYX_PREDICTION_PACKET

Harmonia asks:

Can a modern experimental surrogate faithfully reproduce the observed behavior and, where testable, the mechanism?

Its stages become:

R1 — ORACLE CONSTRUCTION
R2 — BEHAVIORAL RESURRECTION
R3 — MECHANISTIC EQUIVALENCE
R4 — DIVERGENCE CHARACTERIZATION

Harmonia does not repeat historical archaeology unless it discovers evidence that Techne’s world reconstruction is defective.

If so, it returns:

WORLD_RECONSTRUCTION_CHALLENGE

to Techne.

That return is evidence.

⸻

R27 — WORLD RECONSTRUCTION CAN FAIL WITHOUT KILLING THE FOSSIL

A fossil whose historical world cannot currently be executed remains scientifically valid as an acquisition.

Possible states include:

BODY_RECOVERED
WORLD_PARTIALLY_RECONSTRUCTED
BLOCKED_BY_MISSING_TOOLCHAIN
BLOCKED_BY_MISSING_MEDIA
BLOCKED_BY_UNKNOWN_BEHAVIOR

Future tools may reopen it.

No non-executable fossil is rewritten as “dead.”

⸻

R28 — PRE-REGISTER THE CENTRAL WAGER

The pipeline’s load-bearing scientific claim must itself be falsifiable.

Before broad landscape filling begins, freeze the following program-level test.

MECHANISM KINSHIP WAGER — MKW-1

After the first 50 independently resurrected mechanism cuts have obtained admitted landscape measurements, ask whether the pipeline has found at least one cross-lineage interaction satisfying all of:

1. mechanisms originate from distinct historical lineages;
2. one mechanism measurably shifts a failure surface,
   recovery surface, or other preregistered behavioral
   boundary of the other;
3. the displacement replicates;
4. the effect survives direct ablation;
5. the effect survives the appropriate payload-reading null;
6. the relation was not created solely by sharing the
   same historical implementation or test fixture.

If no such case exists, then this specific wager is falsified at N=50:

The current representation and pipeline have not demonstrated experimentally reusable cross-lineage mechanism kinship.

Do not reinterpret that result as proof that no such kinship exists.

Possible explanations include:

kinship absent
representation inadequate
worlds inadequate
pressures inadequate
mechanism cuts inadequate
observables inadequate

But each explanation requires a new test.

The failed wager cannot be retroactively moved.

The archaeology/preservation value of the pipeline may remain.

Its claim to be discovering cross-lineage reasoning machinery does not.

⸻

R29 — NEW DIMENSIONS MUST EARN THEIR EXISTENCE

A proposed new tensor dimension is admissible only if:

1. it has an operational definition;
2. it can be measured reproducibly;
3. it distinguishes experimental states previously collapsed together;
4. the split is demonstrated on preregistered examples or controls.

The core test is:

Does this dimension split a previously uniform cell in a reproducible and scientifically relevant way?

If not, the new dimension is vocabulary, not measurement.

⸻

R30 — GZIP PILOT MUST USE THE FULL SCHEMA FROM BIRTH

The gzip pilot remains approved.

Its reference lineage must include from its first committed record:

FOSSIL_RAW_ID
PAYLOAD_MANIFEST_ID
FOSSIL_WORLD_ID
RUNTIME_WITNESS
HOST_CAPS_ID
SCAFFOLDING_LEDGER
TECHNE_STATE
TECHNE_RUN_RECEIPTS
CUT_ID
NYX_PREDICTION_PACKET
ORACLE_SOURCE(S)
ORACLE_PROVENANCE_GRADE(S)
HARMONIA_SURROGATE_ID
EQUIVALENCE_RESULT
DIVERGENCE_LEDGER
TEST_WORLD_ID
PRESSURE_ID
INTERVENTION_ID
TENSOR_ADMISSION_RESULT
PAYLOAD_READING_NULL
FINAL_DISPOSITION

No later descendant should require retrofitting these fundamental identities.

⸻

REVISED OWNERSHIP

The operative pipeline is now:

TECHNE
│
│  recover body
│  recover provenance
│  reconstruct historical world
│  verify instruments
│  maintain scaffolding ledger
│  reproduce historical behavior as far as evidence permits
│
▼
NYX
│
│  dissect
│  freeze CUT
│  hypothesize mechanism
│  freeze prediction and falsifier
│
▼
HARMONIA
│
│  grade/build oracle
│  construct modern surrogate
│  establish behavioral equivalence
│  test mechanistic equivalence
│  record divergences
│
▼
THEOPHRASTUS
│
│  place mechanism into TEST_WORLDs
│  apply pressures/interventions
│  map damage and recovery geometry
│  admit valid tensor coordinates
│
▼
ARCHAEON / VIVARIUM
│
│  compose
│  mutate
│  expose organisms to ecology
│  measure incorporation / loss / interaction
│
▼
SOUP
   provenance-bearing experimentally characterized machinery

⸻

UPDATED LAUNCH ORDER

The first launch is not:

Nyx → Harmonia → gzip

It is:

1. TECHNE
   certify host-stable gzip body identity
   certify FOSSIL_WORLD
   attach scaffolding ledger
   attach run receipt
   attach off-host preservation receipt
2. NYX
   freeze CUT
   freeze prediction
   freeze cheat control
   freeze falsifier
3. HARMONIA
   establish lane currency
   calibrate equivalence ruler on RS pair
   grade oracle sources
   construct surrogate
   measure equivalence/divergence
4. THEOPHRASTUS
   define TEST_WORLD
   run small landscape
   apply existing tensor admission gates
5. TERMINATE HONESTLY
   likely:
   LANDSCAPE_MEASURED / NULL
6. PRESERVE
   gzip becomes the reference pipeline specimen
   regardless of whether it ever enters Soup

⸻

FINAL PRINCIPLE

Prometheus is not preserving executable history merely so that history can run again.

It is preserving enough of the body, world, instrumentation, and evidence that the experiment can be interrogated again.

The important inheritance chain is therefore not merely:

old code → modern code

It is:

historical body
+ historical world
+ explicit scaffolding
+ verified instruments
+ provenance-graded observations
        ↓
experimentally trustworthy surrogate
        ↓
new pressures and worlds
        ↓
measured failure geometry
        ↓
possible reusable machinery

That is the object being built.
