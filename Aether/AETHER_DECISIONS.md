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
physics semantics, determinism/replay, mutation behavior, resource
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

D-11 (2026-09-20, operator). Causal heredity is tracked as three distinct,
non-interchangeable concepts: STRUCTURAL_RESEMBLANCE, CAUSAL_CONSTRUCTION,
RECURSIVE_CONSTRUCTION. Structural resemblance alone is never replication
evidence.

D-12 (2026-09-20, operator). Runpod is used during development for small
compatibility/performance probes only. No broad scientific campaign runs
on Runpod until the substrate is qualified trustworthy.

## Rejected alternatives

None proposed yet.
