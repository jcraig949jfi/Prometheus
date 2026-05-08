# Mini Contract-Change Window — Techne 2026-05-08

**Status:** Loop paused. Single-dispatch prompt, NOT a /loop fire. Paste once in a fresh Techne session. When Techne completes, James restarts the loop in contract-locked mode.

**Authorization:** Contract changes AUTHORIZED for this dispatch only. Scope is intentionally narrow — security pass closing the input-validation + freeze-invariance gaps surfaced by Substrate-Tester fires #14, #15, #17, #25, #29 during 2026-05-07. Capability-gap tickets (homotopy, BlockDesign, SymbolicLaurentPolynomial, ArityGradedOperationFamily) are NOT in scope; they queue for the next full contract-change window as a unified Structured-Equivalence-Class meta-primitive design.

---

## Paste this to Techne

```
You are Techne, substrate owner for Project Prometheus. The
continuous-iteration loop is currently PAUSED. James has opened a
mini contract-change window so you can drain a security-priority
cluster of contract-touching tickets surfaced by Substrate-Tester
during 2026-05-07. Scope is intentionally narrow.

This is NOT a /loop fire. Single-dispatch. Drain the 3 tiers below
within the time cap. No ScheduleWakeup at the end.

## Hard rules (still binding)

- Read aporia/doctrine/critical_memories.md first; binding.
  HARD-1 (no papers), HARD-2 (gravitational-well suppression),
  HARD-3 (tensor-first), HARD-4 (calibration anchors load-bearing),
  HARD-5 (domains-as-docstrings) all apply unconditionally.
- File ownership: sigma_kernel/, prometheus_math/,
  harmonia/memory/architecture/sigma_kernel*.md. Outside that,
  coordination ticket.
- Anti-conventional discipline: input-validation hardening should be
  loud-fail-on-typo per the substrate's existing pattern (raise
  KeyError with registered-set listing); do NOT import "Pydantic-
  style runtime coercion" or other framework-native patterns.

## Authorization for this dispatch

Contract changes AUTHORIZED, but ONLY for the 3 tiers below. Every
contract change must:

1. Be documented in harmonia/memory/architecture/sigma_kernel.md
   under a new "Contract-change window 2026-05-08" section (sister to
   the 2026-05-07 section).
2. Have round-trip tests in prometheus_math/tests/ or
   sigma_kernel/tests/ exercising the new validation path.
3. Pass the full pytest sweep before commit. The 8 pre-existing
   failures from the 2026-05-07 window (Cremona-DB, dilogarithm
   precision, Mossinghoff outdated count, lehmer_brute_force
   composition) are NOT regressions; ignore them but verify their
   count hasn't grown.
4. Have a self-review section in your dispatch journal addressing:
   (a) is this contract change minimal (could a smaller change have
   served)? (b) does the new contract align with the substrate's
   existing loud-fail discipline (cf. ST003 hardening)? (c) is the
   new contract documented so the next loop restart picks it up
   cleanly?

## What to drain

### Tier 1 — TriangulationProtocol bypass (P0). Do FIRST.

Three related tickets, single co-fix candidate:

- **T-2026-05-07-ST-fire17-001 (P0-blocker)**
  TriangulationProtocol bypassable via arbitrary-IC smuggle. The
  smuggle attack: construct MethodSpec with arbitrary
  independence_class string → wrap in TriangulationPath with valid
  MethodClass enum → TriangulationProtocol.evaluate returns
  UPGRADED_TO_LOCAL_LEMMA with upgrade_eligible=True. Substrate's
  certification discipline (v2.3 §6.3) violated.

- **T-2026-05-07-ST-fire14-001 (P1-high)**
  MethodSpec silently accepts arbitrary strings as
  independence_class. IndependenceClass is a str-mixin enum so
  Python type system accepts strings, but the substrate's
  triangulation discipline depends on the registered enum vocabulary.

- **T-2026-05-07-ST-fire29-001 (P1-high)**
  TriangulationPath silently accepts arbitrary string as
  method_class (sister gap to fire-14).

Single co-fix:
- Add __post_init__ validation to BOTH MethodSpec.independence_class
  AND TriangulationPath.method_class that raises ValueError (or
  TypeError) if the value is a str but NOT a valid enum member.
- Acceptable values: actual enum instance OR exact string-name match
  to enum member; anything else raises with message listing
  registered enum values.
- Add defense-in-depth at TriangulationProtocol.evaluate: if any
  path.method_spec.independence_class is somehow not a registered
  IndependenceClass at evaluate-time (belt-and-suspenders), refuse
  the upgrade with explicit reason.

Tests: round-trip for each enum-validation site + the smuggle
attack reproducer (which should now raise rather than upgrade).

### Tier 2 — frozen-dataclass audit (P1). Do second.

- **T-2026-05-07-ST-fire25-001 (P1-high)**
  Substrate-wide @dataclass(frozen=True) gap. 5 classes confirmed
  missing freeze-invariance test (independent mutation-testing
  fires #7, #15, #25 converged on boolean_not survivors at
  @dataclass(frozen=True) lines):
  - sigma_kernel/operator_portability.py → OperatorPortabilityCertificate
  - sigma_kernel/coordinate_chart.py → CoordinateChart
  - sigma_kernel/exclusion_certificate.py → TriangulationPathRef,
    RegionSpec, ExclusionClaim

This ticket also closes T-2026-05-07-ST-fire1-001 (frozen on
OperatorPortabilityCertificate) and T-2026-05-07-ST-fire15-001
(frozen on CoordinateChart) as same-pattern sister tickets.

Recommended fix: ship sigma_kernel/tests/test_frozen_invariance.py
with a single audit-style test that introspects every
@dataclass(frozen=True) class in sigma_kernel/ and verifies
FrozenInstanceError on setattr. The audit walks the package; new
@dataclass(frozen=True) classes auto-enrolled going forward (no
manual enumeration). ~30 min of work.

This is technically NOT a contract change — frozen=True semantics
are already documented; the test module just enforces the
documented contract. But document the new test module under
sigma_kernel.md "Contract-change window 2026-05-08" section anyway
so the discipline is visible.

### Tier 3 — CLAIM kill_path string-typing (P2). Do third.

- **T-2026-05-07-ST-fire29-002 (P2-normal)**
  CLAIM accepts non-string kill_path. Round out the input-validation
  pass with a __post_init__ check that kill_path is a str (and
  matches the expected pattern if there is one — check the existing
  schema doc).

Tests: round-trip for valid + raise-on-invalid-type.

## What to skip in this dispatch

- T-ST-fire1-002, fire1-003, fire21-001, fire21-002 (4 capability-
  gap tickets — homotopy, BlockDesign, SymbolicLaurentPolynomial,
  ArityGradedOperationFamily). These accumulate for the NEXT full
  contract-change window. Aporia's recommendation: design a unified
  Structured-Equivalence-Class meta-primitive rather than 4 one-off
  primitives. Do NOT begin design work in this dispatch.
- T024-T028 deferred-impl tickets from prior window. Same — next
  full window.
- T029 multi-precision impl. Same — next full window.
- All test/pressure-infrastructure tickets (T008-T017): these are
  loop-pickup, not contract-window scope.

## What to commit

One commit per tier. Tier 1 is a single commit (the 3 P0/P1 tickets
share a co-fix). Tier 2 is a single commit (audit test module).
Tier 3 is a single commit (CLAIM hardening). Push after each commit
so any concurrent reviewer can monitor.

Commit message format: "Contract change: <ticket-id> <title>"
followed by a brief summary of the contract diff.

## Output expected at the end

Single summary document at
pivot/mini_contract_window_2026-05-08_summary.md listing:
- Each ticket processed: status (DONE / SKIPPED-WITH-REASON)
- Each contract change: old contract, new contract, justification,
  doc location
- Test count: pre vs post
- Any newly-surfaced contract changes filed as new BLOCKED tickets
  for the next full window
- Cross-reference to the prior window summary at
  pivot/contract_change_window_2026-05-07_summary.md

When this summary is committed and pushed, the dispatch is closed.
James will read it, then restart the loops.

## Time cap

~4-6 hours of focused work. If you hit the cap before finishing
Tier 3: stop, write the summary, push. Do not silently extend past
the cap. Tier 1 is highest priority and the substrate's
certification discipline is broken until it lands; Tier 1 must
ship even if Tier 2/3 don't.

— Begin.
```

---

## After Techne completes

Restart sequence (James-driven):
1. Read `pivot/mini_contract_window_2026-05-08_summary.md` to confirm scope.
2. Restart Techne loop with the canonical KICKOFF prompt #1.
3. Restart Substrate-Tester loop. Its first fire after restart should re-probe Lane 3 (correlated-triangulation) immediately to regression-confirm the P0 fix.
4. Restart Ergon and Learner-Tester (if you paused those too).

The new locked Tier-1 contracts (MethodSpec + TriangulationPath enum-validation + TriangulationProtocol defense-in-depth) become the new substrate baseline. The frozen-dataclass audit becomes ongoing self-enforcement (auto-enrollment of new @dataclass(frozen=True) classes).
