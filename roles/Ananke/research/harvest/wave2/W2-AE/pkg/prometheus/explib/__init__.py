"""prometheus.explib -- an engine-agnostic BELOW-ENGINE experiment-audit library.

Promoted from the Ananke Wave-2 harvest (W2-F explib draft, W2-B attainability certifier; promotion package
W2-AE, 2026-10-01). Pure Python + numpy. NO engine import anywhere in this package (enforced by
tests/test_core_isolation.py); engines plug in through small protocols (lockstep.LockstepEngine,
metamorphic.Experiment / MutationOperator, attainable.Ruler.measure) or by handing over plain arrays. The PTE
adapters live with their engine in prometheus.ananke.audit.

Modules (one per primitive):
  outcomes     shared three-valued outcomes (PASS / FAIL / NOT_VERIFIED) and the Check record
  trace        (2) causal difference record, closure invariant, LOCAL/TRANSPORTED paths, difference cones
  lockstep     the LockstepEngine protocol and the runner that turns an engine into a DiffRecord
  reach        (1) reachability certificate UNAPPLIED / NOT_REACHED / ABSORBED / REACHED (+ path)
  authority    (3) state and write-authority tracing; difference-vs-use filter
  controls     (4) control competence: identity audit (no-op, forced constant, mirror identity, can-fail witness)
  metamorphic  (5) metamorphic experiment-testing harness protocol and mutation adequacy
  attainable   (6) attainable-range certification of a gate: G1-G4 checks (certify_gate) and the role-based
               family certifier (certify_family: UNREACHABLE / DEGENERATE / CHEATABLE / SOUND / NO_PLANT),
               plus the analytic CI-gate power / eligibility threshold
  provenance   (7) intervention provenance records: seed namespace, hook digest, plan-commit linkage
  stats        (8) independence-unit declaration, stratified / Simpson guard; (9) pairing-aware CIs,
               ratio guard, margin / replication label
  toys         tiny numpy engines used by the tests (and as worked examples of the protocols)

Importing this package runs nothing and imports no submodule.
"""
from __future__ import annotations

VERSION = "explib-0.1.0"
