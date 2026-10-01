"""explib: a shared, engine-agnostic BELOW-ENGINE experiment library (draft, W2-F, 2026-10-01).

Pure Python + numpy. NO engine import anywhere in this package; engines plug in through small protocols
(explib.lockstep.LockstepEngine, explib.metamorphic.Experiment) or by handing over plain arrays.

Modules (one per primitive; see ../API.md):
  outcomes     shared three-valued outcomes (PASS / FAIL / NOT_VERIFIED) and the Check record
  trace        (2) causal difference record, closure invariant, LOCAL/TRANSPORTED paths, difference cones
  lockstep     the LockstepEngine protocol and the runner that turns an engine into a DiffRecord
  reach        (1) reachability certificate UNAPPLIED / NOT_REACHED / ABSORBED / REACHED (+ path)
  authority    (3) state and write-authority tracing; difference-vs-use filter
  controls     (4) control competence: identity audit (no-op, forced constant, mirror identity, can-fail witness)
  metamorphic  (5) metamorphic experiment-testing harness protocol and mutation adequacy
  attainable   (6) attainable-range certification of a gate: null, adversary, ceiling, eligibility count
  provenance   (7) intervention provenance records: seed namespace, hook digest, plan-commit linkage
  stats        (8) independence-unit declaration, stratified / Simpson guard; (9) pairing-aware CIs,
               ratio guard, margin / replication label
  toys         tiny numpy engines used by the tests (and as worked examples of the protocols)
"""
from __future__ import annotations

VERSION = "explib-0.1.0-draft"
