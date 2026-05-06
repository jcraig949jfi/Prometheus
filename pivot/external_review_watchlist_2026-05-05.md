# External Review Watchlist — 2026-05-05

**Source:** External review of Substrate v2.2 + Learner v0.5 (received 2026-05-05)
**Owner:** Aporia (watchlist maintenance); Techne, Ergon, Charon to revisit at trigger conditions
**Purpose:** Track three substantive critiques as falsifiable concerns to revisit as testing accumulates evidence. NOT to redesign v2.2 around speculative worries — but also NOT to forget them.

## How to use this doc

Each critique below has:
- **Critique** — what the reviewer flagged
- **Reviewer's recommendation** — the suggested fix
- **Our current position** — defer / partial mitigation / accept
- **Trigger condition** — what evidence forces revisiting
- **Falsification test** — what would settle the question
- **Watch cadence** — when to recheck

Anyone landing a result that changes a trigger condition should append to the corresponding section + ping the owner. If a trigger fires, the design pass becomes load-bearing for the next sprint cycle.

---

## Watch-1: Σ-kernel lacks a logical foundation

**Critique:** The kernel opcodes (RESOLVE / CLAIM / FALSIFY / GATE / PROMOTE / ERRATA / TRACE) read as imperative VM operations, not as a logic. BIND/EVAL gestures at declarative rewriting; REWRITE/EQUIV will extend further. The semantics is operationally state-transition on a ledger but rhetorically equivalence-classes-under-rewriting. Until the underlying logic is committed, the formalism risks being too flexible to be foundational.

**Reviewer's recommendation:** Prototype the Σ-kernel as a lightweight extension of a proof-assistant kernel — Calculus of Constructions with native falsification records, or similar. A tiny dependent-type-theory kernel gives resolution + rewriting + counterexample-falsification "for free" without inventing a new logic from scratch.

**Our current position:** **Defer with explicit acknowledgment.** v2.2 ships with the imperative VM as designed. The reviewer is right that this is the strongest critique in the review, and we don't yet have a clean answer.

**Trigger condition** (any one fires the design pass):
- Two or more substrate primitives end up requiring inconsistent semantics (e.g., a CLAIM whose typed payload requires equational reasoning that ERRATA can't represent)
- A bug surfaces where TRACE produces inconsistent provenance under semantically-equivalent BIND/EVAL paths
- Techne or Ergon attempts to formalize a substrate invariant and finds the formalization requires logic the kernel doesn't express
- A frontier-model review independently flags the same critique within 30 days of v2.2 ship

**Falsification test:** spend ~1 week prototyping the Σ-kernel as a CoC extension with native falsification records. If the prototype subsumes all 7 opcodes + BIND/EVAL + REWRITE/EQUIV cleanly, the imperative-VM design becomes the deprecated path. If it doesn't (specific opcodes resist clean type-theoretic encoding), document precisely why and commit to the imperative-VM design with the documented limitation.

**Watch cadence:** review at end of v2.2 sprint (Day 17-19) AND after any trigger condition fires. Aporia revisits unconditionally at next 14-day external-review cycle.

---

## Watch-2: F9 ("simpler explanation") and F6 ("base rate") need formal computable definitions

**Critique:** Several falsification battery components are heuristic, not computable:
- F9 "simpler explanation" implicitly requires a complexity measure (Kolmogorov / MDL territory)
- F6 "base rate" requires a well-defined reference class
- "Reciprocity" in the bidirectional-check sense needs formal symmetry definitions

Without computable criteria, the gauntlet only works on toy fragments and slips into pattern-matching pretending to be falsification.

**Reviewer's recommendation:** Replace heuristic battery components with two well-defined filters until evidence shows more is needed: a type-checker (excludes syntactically ill-formed claims) and a decision procedure for a decidable fragment (Presburger arithmetic, or a small SAT-based fragment). See if the system can recover anything nontrivial in that sandbox before re-adding heuristic batteries.

**Our current position:** **Partial mitigation acknowledged; full fix deferred.** F1 (permutation null) and F11 (cross-validation) are computable as designed. F6 and F9 are currently "heuristic with HITL backstop" — the substrate doesn't auto-falsify on these alone. Worth documenting this explicitly in the v2.2 spec so downstream consumers don't treat F6/F9 as auto-decidable.

**Trigger condition** (any one fires):
- A PROMOTE happens where F6 or F9 was the load-bearing falsifier and the result later turns out wrong (false positive directly attributable to a heuristic battery component)
- Charon's per-domain π₀ analysis shows F6/F9 kill rates correlate suspiciously with surface features (e.g., paper venue, author identity) rather than mathematical content
- A G4-style F-gate orthogonality MI audit (already queued in `aporia/meta/charon_pending_tasks.md`) finds that F6 or F9 carries near-zero MI vs F1+F11 → they're decorative, not load-bearing
- Techne attempts to make F9 commit-blocking and finds the heuristic produces unstable verdicts across re-runs

**Falsification test:** implement a Solomonoff-flavored MDL filter as a candidate F9 replacement on the existing 314K kill ledger. Compare its kill-rate to current F9 on the same data. If MDL-F9 kill set ⊃ heuristic-F9 kill set (i.e., MDL catches everything heuristic does plus more), promote MDL. If the sets diverge in opposite directions, document and pick the one that better predicts cross-seed reproducibility.

**Watch cadence:** revisit at G4 audit completion (currently pending Techne's Pre-Tier-0 0b telemetry instrumentation). Aporia flags any false-positive PROMOTE traceable to F6/F9 immediately.

---

## Watch-3: Substrate is good at checking, not at concept invention

**Critique:** The substrate's language (opcodes, typed ledger, KillVector components) is designed for rigorous checking of proposed claims. Truly novel mathematics often requires *new concepts that aren't simply recombinations of existing concepts in training* (Wiles's reframe of FLT via modular forms, Grothendieck's schemes, Khovanov's categorification). The substrate's vocabulary may not easily express the conceptual shift needed for novel discovery — it would catch wrong elementary attempts cleanly but wouldn't *suggest* "switch to modular forms."

**Reviewer's recommendation:** Implicit — the reviewer doesn't propose a fix, just flags it as where most discovery-oriented systems stall. Worth a separate design pass before claiming the substrate enables discovery (vs rediscovery).

**Our current position:** **Accept the gap; defer the design.** This is the v1.0 / v2.0 question, not v0.5 / v2.2. The Learner v0.5 is correctly framed as *first tire-kick on rediscovery*, not as a discovery engine. The substrate's "discovery via rediscovery" framing already concedes that we're starting where ground truth exists.

**Trigger condition** (any one fires):
- Ergon's Learner v1.0 or v2.0 design starts and we find the substrate vocabulary genuinely cannot express a candidate concept-shift the Learner wants to propose
- A successful rediscovery of a famous result (e.g., the FLT-via-modularity bridge, if we ever instrumented it) requires substrate primitives we don't have
- Aporia's open-question catalog (322 open problems) hits a problem class that the substrate cannot represent without new vocabulary
- A Learner architecture review identifies "concept invention" as a separable workstream that needs its own design

**Falsification test:** pick one famous concept-invention moment in mathematical history (Wiles → modular forms; Grothendieck → schemes; Khovanov → categorification of Jones polynomial). Express the BEFORE state in the substrate's current vocabulary. Express the AFTER state. If the substrate can represent both states AND the transition between them, the gap is smaller than the reviewer fears. If the AFTER state requires substrate primitives we don't have, the gap is real and needs design work.

**Watch cadence:** revisit when Ergon Learner v0.5 tire-kick completes (Day 17-19 of joint sprint). The tire-kick result will partly diagnose this — if the Learner can't rediscover even simple bridges, the concept-invention gap is the larger problem; if it can, the substrate vocabulary is at least covering the rediscovery path.

---

## Maintenance protocol

- **Aporia owns this file.** Updates on trigger-condition firings, watch-cadence reviews, and any new external-review critiques.
- **Append-only.** Do not delete watch items even after they're resolved; mark resolution status. The substrate's discipline is to preserve the trace.
- **Frontier-model second pass.** When this doc reaches a stable state, bundle with v2.2 + v0.5 + joint-sprint docs for the Claude / Grok / DeepSeek frontier review. If they raise the same three concerns, the prior probability that the critiques are real (not artifact of one reviewer's prior) goes up substantially.
- **Status tracking:** add a top-level summary to `pivot/sister_projects_2026-05-05.md` referencing this watchlist as the canonical critique-tracking surface.

## Resolution status (current)

| Watch item | Status | Last reviewed |
|---|---|---|
| Watch-1: Σ-kernel logical foundation | OPEN — defer; revisit at end of v2.2 sprint | 2026-05-05 |
| Watch-2: F9/F6 formal definitions | OPEN — partial mitigation; revisit at G4 audit | 2026-05-05 |
| Watch-3: concept invention vs verification | OPEN — defer; revisit at Learner v0.5 tire-kick completion | 2026-05-05 |

— Aporia, 2026-05-05
