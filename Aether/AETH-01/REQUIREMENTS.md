# AETH-01 -- requirements: R1-R15 compliance and engineering requirements

Status: DRAFT.

## Part 1 -- hard scientific requirements (R1-R15) compliance

| Req | Status | Note |
|---|---|---|
| R1 no privileged organism ontology | SATISFIED | State is 5 uint8 fields only; no id/fitness/parent fields exist anywhere |
| R2 no reproduction primitive | SATISFIED | Only WRITE (template) and conservative transfer exist; no BIRTH/COPY_SELF/ALLOC |
| R3 no externally imposed genome boundary | **TENSION** | Mutation is defined to exclude field 4 (energy) by construction (PHYSICS_SPEC_DRAFT.md accessibility analysis, item 2) -- this partially pre-decides that "instructional" fields, not the resource field, are where heritable variation can live. Not a full violation (heredity could still, in principle, be read from spatial/energy PATTERNS rather than mutable content) but a real, named hidden prior, not swept under the rug |
| R4 local causality | SATISFIED, with caveat | All interactions are bounded to von Neumann neighbors; the arbitration hash depends on absolute coordinates (a positional tie-break field) but this cannot transmit information between non-adjacent cells -- it biases *which local proposal wins*, it does not let distant cells influence each other directly. Caveat tracked in ADVERSARIAL_ANALYSIS.md #6, #16 |
| R5 endogenous persistence | **TENSION** | A cell's initial energy allocation is exogenous (chosen at construction, EXPERIMENTS.md), and more initial energy mechanically buys more ticks of possible action -- persistence differences can therefore reflect initial-condition luck, not dynamics, unless controlled for (ADVERSARIAL_ANALYSIS.md #12; ECONOMICS.md's Regime B with ongoing replenishment reduces but does not eliminate this) |
| R6 endogenous construction | SATISFIED (by design intent) | Physics permits the STRUCTURAL_RESEMBLANCE / CAUSAL_CONSTRUCTION / RECURSIVE_CONSTRUCTION distinction to be made later (HEREDITY_REQUIREMENTS.md); no detector exists yet, which is explicitly allowed by the brief |
| R7 writable/reconfigurable matter, avoid conventional VM without reason | SATISFIED, with justification | AETH-01 keeps AETH-00's opcode/operand shape rather than inventing a new ontology; the stated compelling reason is continuity with a validated conformance/differential-testing methodology (PHYSICS_CANDIDATES.md, "Selection," reason 1) -- flagged, not hidden, as a VM-adjacent design |
| R8 cost/scarcity | SATISFIED | ECONOMICS.md: WRITE_COST, MAINTENANCE_COST, conservative lossy transfer |
| R9 no direct task-reproduction coupling | SATISFIED (vacuously) | No task exists in AETH-01; nothing computes a score of any kind. Not yet tested under an actual task, since none exists |
| R10 observatory separation | SATISFIED | OBSERVATORY.md reads trace/state only; trace on/off byte-identity is a required regression test (Part 2 below), inherited from AETH-00B's proven pattern |
| R11 deterministic replay | SATISFIED | All randomness (arbitration, mutation, replenishment) is explicit, domain-separated, and derived only from (seed, tick, coordinates); replay-identity tuple extended (PHYSICS_SPEC_DRAFT.md) |
| R12 GPU viability | SATISFIED | Selection criterion for choosing this candidate (PHYSICS_CANDIDATES.md); reuses AETH-00's proven gather mapping unchanged in shape |
| R13 tiny worlds meaningful | SATISFIED | HABITABILITY.md scopes the first campaign to H,W in {4,8,16,32} |
| R14 alien organization possible | **TENSION** | A single active opcode with no compare/branch primitive is a real expressivity ceiling (PHYSICS_SPEC_DRAFT.md accessibility item 4) -- AETH-01 does not FORCE neural/genome/CPU-like organization, but it also cannot express certain conditional strategies at all, which is a different, narrower kind of limitation worth tracking into AETH-02 |
| R15 failure observable | SATISFIED | HABITABILITY.md's regime labels are explicitly designed around failure modes (DEAD/FROZEN/HOMOGENIZED/EXPLOSIVE), each backed by a measurable signature |

No requirement was found flatly IMPOSSIBLE or mutually contradictory.
Three (R3, R5, R14) have named, real tensions rather than clean
satisfaction -- reported as such, not silently resolved in the
physics' favor. DECISIONS.md records each as its own entry.

## Part 2 -- engineering requirements (Design Task 11)

Explicitly separated into four categories that must never be conflated
in a report or a receipt:

**Semantic correctness** (does the implementation match the spec):
- A CPU reference implementation independent of any GPU code, built
  test-first against this draft spec, following AETH-00A/B's proven
  method (independent oracle + independent second oracle +
  differential testing between them before any production code exists).
- Property-based testing (Hypothesis-style) over random worlds/params,
  at AETH-00B's scale of rigor (>=100,000 generated cases per
  qualification pass) once implementation begins.
- Golden vectors for: WRITE_COST starvation boundary, transfer
  win/loss/overflow, maintenance-decay floor, replenishment trigger,
  mutation trigger/bit-index, and the H,W in {1,2} toroidal
  self-aliasing cases extended to the energy field (AETH-00's test 14
  equivalent).
- The energy conservation equation (PHYSICS_SPEC_DRAFT.md) checked as
  an exact property on every generated case, not sampled.

**Numerical reproducibility** (does it replay bit-identically):
- All arithmetic is fixed-width unsigned integer; no floating point
  anywhere in the transition law or its three RNG-derived functions.
- Replay-identity tuple (11 components, PHYSICS_SPEC_DRAFT.md) is
  mandatory in every trace/checkpoint header; a replay comparison that
  omits any component is not a valid AETH-01 replay claim, per AETH-00's
  own precedent.
- Tick-overflow behavior (reject, never wrap) inherited unchanged from
  AETH-00.

**Engineering reliability** (does it survive real operating conditions):
- Checkpoint format captures the FULL replay-identity tuple plus S[t];
  a checkpoint round-trip test (non-interrupted vs.
  interrupted-and-resumed run, byte-for-byte) is required before any
  checkpointed run is trusted (closes ADVERSARIAL_ANALYSIS.md #20).
- Crash recovery: resuming from the last valid checkpoint must be
  possible without operator intervention beyond re-invoking the runner;
  a partially-written checkpoint must be detectable (checksum) and
  rejected rather than silently loaded.
- Schema/versioning: every trace/checkpoint file records its own
  `semantics_id` (`aeth01.v1` once frozen) and a schema version
  integer, independent of code version, so future readers can detect
  incompatible formats explicitly rather than guessing.
- Fault injection: deliberately corrupt/truncate a checkpoint or trace
  file in tests and confirm the loader raises rather than silently
  producing a degenerate world (mirrors AETH-00B's invalid-input
  discipline).
- Receipt format: every milestone receipt (as with
  AETH-00A/B_RECEIPT.md) states exact test counts, differential-case
  counts, failures, mutant status, and what remains deliberately
  absent -- no receipt claims more than what was actually run.
- Provenance: every run (test or campaign) logs code SHA,
  `semantics_id`, full parameter set, seed, host/hardware identity,
  wall-clock, and (for paid runs) dollar cost -- answers
  AETHER_OPEN_QUESTIONS.md question 18 for AETH-01 specifically.
- Performance measurement: CPU baseline benchmark repeated at AETH-01's
  larger per-cell footprint (5 fields vs. 4) before any GPU work is
  proposed, following AETH-00B's precedent (measured, not assumed).

**Scientific inference** (what may be concluded from correct, reliable
runs) is governed entirely by HEREDITY_REQUIREMENTS.md's tiered
evidence standard and ADVERSARIAL_ANALYSIS.md's controls -- passing
every item above establishes only that the SIMULATOR is trustworthy; it
establishes nothing about what any specific run means, which is a
separate, later, per-claim judgment (mirrors AETH-00's own "Scope"
section discipline, AETHER_SPEC.md).

## CPU/GPU equivalence and Runpod/cost engineering

Deferred to GPU_RUNPOD.md (Design Task 12) to avoid duplicating that
document's DEFER/REJECT/prerequisite analysis here.
