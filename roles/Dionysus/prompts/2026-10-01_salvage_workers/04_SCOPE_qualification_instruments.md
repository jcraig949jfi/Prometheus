# Scope 4: instruments for qualification and failure fixtures

Slots to fill: the kernel's QUALIFICATION GATE (calibration set, channel
test, fire tests), the FAILURE FIXTURES (the failure taxonomy compiled into
executable cases the kernel must catch), the trivial responders that sit
beside every headline, the verdict type, and the preregistration and
freeze checks (RSE_ARCHITECTURE.md section 4).

Requirement areas to read: section 1; SCI-01 to SCI-06; MEAS-01 to MEAS-11;
WLD-03, WLD-05, WLD-07; PROV-04, PROV-06; REPR-05.
Also read docs/phase3/intake/tityos/failure_taxonomy.md (T01 to T24) and
docs/phase3/intake/tityos/REPORT.md sections A, B, E, F, and section 5
(new defects found by the crawl, unconfirmed by owners).

Components:

1. Charon's c1c2_checks (three-valued, eligible and fired counts, cheat
   fixtures), the exit-review-3 arm-leak classifier with a planted leak,
   the R7 identity-null calibration, the three-valued band rule.
   Dossier: tityos/seats/Charon.md. Code: charon/probe/.
2. Nemesis cheatlib (constant, majority and payload responders, shrink to
   a minimal fraud, its 12 self-controls) and the NEMESIS-01 protocol.
   Dossier: tityos/seats/Nemesis.md. Code under roles/Nemesis/ and
   agents/nemesis/.
3. Harmonia: AP-1.1.0 audit primitives (reachability, absence_control,
   baseline_gaming, ceiling, null_pass_binomial, freeze_precedes) and their
   fixtures; STANDING_RULES F1-F8; the VACUOUS_READINGS register; the
   emission-path census; the evidence audit by re-execution. Also the
   defects the crawl reports in Harmonia's own qualification code
   (qualification_rules.py quantiles, tautological ablations, hard-coded
   negative control). Dossier: tityos/seats/Harmonia.md.
   Code: roles/Harmonia/qualification/, harmonia/.
4. Techne: the modal-collapse synthetic null with its learnability check,
   the F2 planted-relation promote gate, fossil hash preservation, the
   promotion replay audit, the mutation assay for gate sensitivity.
   Dossier: tityos/seats/Techne.md. Code: techne/, prometheus_math/.
5. Nyx: NYX_PREDICTION_PACKET v1 (hash-bound, mandatory cheat and positive
   control, author barred from adjudicating) and the mechanism ledger that
   refuses to count a packet as a mechanism. Dossier: tityos/seats/Nyx.md.
   Code: nyx/.
6. Hecate's Wave-2 harnesses: metamorphic evaluator corruption, the
   exact-arithmetic shadow evaluator, derived-file reproduction tests.
   Dossier: tityos/seats/Hecate.md. Code: hecate/.
7. attacks/REGISTRY.md and attacks/preflight.py with its probes (including
   what the "ADMISSIBLE" hook really certifies). The Necropolis
   admissibility ladder and tool registry (engine/necropolis/).
   Dossiers: tityos/REPORT.md, sisyphus/seats/Rhadamanthus.md.
8. Smaller instruments, one short sheet each: Artemis's constructed-
   specimen heredity panel and commit-reveal self-test; Clymene's repo
   probe and tree comparator; Elenchus's closed-form ground truth against
   solver status; Hypatia's three-valued stall predicate; Eos's typed
   intake states; comms/manifest.py.

For each, answer from the source:

- is it a library that can be imported and called on new data, or is it
  bound to one experiment's files and column names;
- what its verdict type is, and whether INDETERMINATE and "nothing could
  have fired" are distinct outcomes;
- which of its own controls have been shown able to FAIL (a fixture that
  makes them fail, in the tree, with a test);
- which failure classes T01 to T24 it detects, by a fixture that exists;
- its known defects.

Two extra deliverables for this scope:

A. A table with one row per failure class T01 to T24: the best existing
   executable detector for it (path), the best existing FIXTURE that
   exhibits the failure (path), or "none".
B. A list of the real historical defects that would make the best failure
   fixtures, because they are small, self-contained and already documented
   (for example: an answer key inside a probe; a hard-coded PASS in a
   tally; a control compared with itself; a baseline added after the
   data). Give the path and commit of each.

The decision Dionysus has to make: which of these become the kernel's gate
library and fixture corpus, and which are re-written.
