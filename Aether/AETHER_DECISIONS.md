# Aether -- decisions and rejected alternatives

Currency: 2026-09-20. Numbered, dated, never renumbered; a reversed
decision is annotated in place, not deleted.

D-1 (2026-09-20, operator). Aether is developed independently of BEE, NPE
and SFE: no copying, adapting, reverse-engineering or borrowing of their
architecture or mechanisms, even though their code and branches are
visible in the repository. Clean-room design.

D-2 (2026-09-20, operator). Strict incremental TDD workflow: testable
contract -> tests -> minimal design -> minimal code that passes -> review
-> next increment. Do not redesign around a failing test unless the
specification is explicitly decided to be wrong (that decision itself
gets logged here).

D-3 (2026-09-20, operator). Correctness and observability outrank speed
during initial development. Performance optimization is deferred until
semantics are well tested.

D-4 (2026-09-20, operator). Runpod is the eventual execution target.
Hard budget $19.93. No paid run without explicit operator approval and a
pre-stated question / duration / hardware / max cost / decision
criterion. See AETHER_RUNPOD.md.
  ANNOTATION (2026-09-20, operator, message 3): each approved probe
  answers exactly one engineering question. Does not replace the
  five-part disclosure; adds a one-question-per-probe scoping rule.

D-5 (2026-09-20, operator). Claude Sonnet 5 (this session) is the primary
design-session model. Astra may later be brought in for an independent
architecture/research review; the design is not to be shaped to
anticipate or optimize for Astra's conclusions. No automatic/blended
model selection unless explicitly requested.

D-6 (2026-09-20, operator). Evaluating Augment Cosmos for potential
usefulness to Aether is a low-priority background item; it must not
interrupt design work. No stopping rule defined yet (AETHER_OPEN_QUESTIONS
question 26, Process/meta).

D-7 (2026-09-20, operator). No implementation before AETH-00 is jointly
defined. This phase is notes capture, organization and open-question
surfacing only.

D-8 (2026-09-20, operator). Aether Engineering Doctrine adopted verbatim
(Aether/AETHER_DOCTRINE.md): correctness over velocity, falsification
over confirmation, causal evidence over resemblance, telemetry designed
before experiments, every detector needs adversarial negative fixtures,
every scientific claim needs an explicit falsifier and a boring
alternative explanation, five-nines-class rigor where metrics are
well-defined, never weaken a test to pass it, no capability added merely
because evolution might need it, anomalies/failures/ambiguity preserved
as evidence.

D-9 (2026-09-20, operator). TDD/emergence resolution: TDD applies to
physics semantics, determinism/replay, perturbation behavior, resource
accounting, causal provenance, seeded positive controls, adversarial
negative controls, detector false positive/negative rates on known
fixtures, CPU/GPU equivalence, checkpoint integrity, and experiment
accounting. Emergence itself is never a test assertion -- a null
primordial-soup run is a valid result, and a scientific campaign never
passes merely because a detector fires. Answers or partially answers
AETHER_OPEN_QUESTIONS.md questions 4, 5, 11, 12 and 15 (see that file for
the per-question resolution).

D-10 (2026-09-20, operator). Runpod success metric is useful simulated
interactions per dollar and information gained per dollar, not raw
ticks/sec.

D-11 (2026-09-20, operator). Causal configuration transmission is tracked as three distinct,
non-interchangeable concepts: STRUCTURAL_RESEMBLANCE, CAUSAL_CONSTRUCTION,
RECURSIVE_CONSTRUCTION. Structural resemblance alone is never replication
evidence.

D-12 (2026-09-20, operator). Runpod is used during development for small
compatibility/performance probes only. No broad scientific campaign runs
on Runpod until the substrate is qualified trustworthy.

D-13 (2026-09-20, operator). GPU-native means the intended
high-performance implementation is massively parallel, but GPU execution
must never define the scientific semantics. Physics has an
implementation-independent specification and a CPU oracle FIRST; GPU is a
performance target implementing that same specification, checked by
differential testing (AETHER_OPEN_QUESTIONS.md question 17). (A candidate
GPU mapping -- per-site parallel evaluation/proposal generation followed
by deterministic parallel arbitration/commit -- is recorded as a
candidate in AETHER_SPEC.md, not frozen here.)

D-14 (2026-09-20, operator). Executable matter is intentional: at
Aether's base level, instruction-bearing state IS physical matter. No
privileged code/data distinction is introduced unless a later experiment
deliberately adds one as an explicit variant.

D-15 (2026-09-20, operator). The first accessibility transplant
reproduces a stated SCIENTIFIC PROPERTY, not any existing engine's
implementation, and is built without inspecting any existing engine's
code. The property: a system can contain the required information and
sufficient selection pressure while useful conditional computation
remains inaccessible because of representation topology. In the observed
case, an existing behavior produced its answer before reading the
information required for the better behavior; the viable conditional
form required several coordinated changes separated from the incumbent
by a zero-evaluation score valley, no beneficial local one/two-edit route existed,
and a seeded viable witness was strongly selectable.

D-16 (2026-09-20, operator). AETH-00 opcode semantics (resolves
AETHER_OPEN_QUESTIONS.md question 27): 0x01 is the sole active opcode
(WRITE); every other value (0x00 and 0x02-0xFF, 255 values total) is
RESERVED_INERT, not "unknown-opcode-as-NOP." 0x00 may be called NOP for
readability only. RESERVED_INERT values are preserved byte-for-byte,
emit no proposal, remain writable by neighbors, and never trap.
Assigning semantics to any RESERVED_INERT byte later requires a new
semantics_id.

D-17 (2026-09-20, operator). AETH-00 dimension policy (resolves
AETHER_OPEN_QUESTIONS.md question 28): transition semantics are defined
for every positive H, W (up to the arbitration law's range, D-18);
H<=0 or W<=0 is invalid input. Ordinary (non-adversarial) runs require
H>=3 && W>=3, solely to remove immediate-neighbor aliasing under
toroidal wrap -- not a claim of scientific adequacy. H=1 and H=2 (and
W=1, W=2) remain supported by the semantics and are mandatory
adversarial test cases, never rejected as invalid.

D-18 (2026-09-20, operator). AETH-00 arbitration construction (resolves
AETHER_OPEN_QUESTIONS.md question 31, supersedes the prior packed
12/12/2/12/12 candidate and its <4096-per-axis limit): coordinates are
unsigned 32-bit components combined as C(row,col) = (uint64(row) << 32)
| uint64(col), valid semantic dimensions 1 <= H,W <= 2^32-1. Priority is
a five-step SplitMix64-finalizer chain over (seed, tick, target
coords, target field, source coords) -- exact construction in
AETHER_SPEC.md. No coordinate tie-break exists in the frozen semantics;
distinct physical sources always yield distinct priorities by
construction (proof in AETHER_SPEC.md). Implementations that emit 2+
proposals from one physical source in one contest are defective, not a
case the law resolves.

D-19 (2026-09-20, operator). AETH-00 is FROZEN as semantics_id
`aeth00.v1` (AETHER_SPEC.md). Replay-complete identity is
(semantics_id, H, W, seed:uint64, tick:uint64, lattice bytes); tick
starts at 0; a step from tick == 2^64-1 is rejected, never wraps.
Freezing `aeth00.v1` means: this exact contract (D-16, D-17, D-18, and
the transition/arbitration text in AETHER_SPEC.md) is never edited in
place again. Any future change -- including assigning behavior to a
RESERVED_INERT opcode -- requires a NEW semantics_id and a new decision
entry here. Per D-19's own scope statement (AETHER_SPEC.md, "Scope"),
freezing AETH-00 licenses engineering progression only; it does not
establish suitable primordial physics, scientific neutrality,
open-endedness, configuration transmission, emergence, evolutionary accessibility, GPU
correctness, or Runpod qualification.

## Rejected alternatives

None proposed yet.
