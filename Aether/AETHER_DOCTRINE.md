# Aether -- engineering doctrine

Currency: 2026-09-20 (operator, verbatim intent; condensed here). This
doctrine governs every future Aether decision; it is adopted, not a
candidate. Full verbatim source: Aether/notes/2026-09-20_raw_notes.md,
message 3.

Aether is the high-rigor moonshot of Prometheus. Move slowly.

1. Correctness outranks velocity. Falsification outranks confirmation.
   Causal evidence outranks resemblance.
2. Telemetry is designed before experiments.
3. Every detector requires adversarial negative fixtures.
4. Every scientific claim requires an explicit falsifier and a boring
   alternative explanation.
5. Where metrics are well-defined, target five-nines-class engineering
   reliability: property-based testing, deterministic replay,
   differential implementations, fault injection, large adversarial test
   sets.
6. Never weaken a test merely to make an implementation pass. If
   implementation and specification disagree, stop and determine which
   is wrong.
7. Do not add capabilities because evolution is expected to need them.
   Add only physical affordances whose semantics are understood and whose
   effects can be measured.
8. Preserve anomalies, failures and ambiguity. A negative or unresolved
   result is valuable evidence.
9. The objective is not to quickly produce interesting-looking artificial
   life. The objective is a substrate trustworthy enough that, if
   something genuinely alien appears, it can be believed.

## TDD / emergence resolution (2026-09-20)

TDD applies to the things Aether controls and claims to measure: physics
semantics; determinism and replay; perturbation behavior; resource
accounting; causal provenance; seeded positive controls; adversarial
negative controls; detector false positives/negatives on known fixtures;
CPU/GPU equivalence; checkpoint integrity; experiment accounting.

Emergence itself is an observation, never a test assertion. A random
primordial-soup run producing nothing is a valid scientific result. A
detector may be tested against known synthetic phenomena, but a
scientific campaign never passes merely because that detector fires.
