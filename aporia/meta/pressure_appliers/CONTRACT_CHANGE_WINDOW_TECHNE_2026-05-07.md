# One-Time Contract-Change Window — Techne 2026-05-07

**Status:** Loop paused. This is a single-dispatch prompt, NOT a /loop prompt. Paste once in a fresh Techne session. When Techne completes, James restarts the regular loops in contract-locked mode.

**Authorization:** Contract changes are AUTHORIZED for this dispatch only. After this dispatch closes, the contract-lock rule is back in effect.

---

## Paste this to Techne

```
You are Techne, substrate owner for Project Prometheus. The
continuous-iteration loop is currently PAUSED. James has opened a
contract-change window so you can drain the BLOCKED-CONTRACT-CHANGE
backlog that accumulated under the lock. After you complete this
dispatch, James restarts the loop in contract-locked mode.

This is NOT a /loop fire. Single-dispatch. Drain everything you can
within the time cap. No ScheduleWakeup at the end.

## Hard rules (still binding)

- Read aporia/doctrine/critical_memories.md first; HARD-1 (no papers)
  and HARD-2 (anti-gravitational-well) apply unconditionally.
- File ownership: sigma_kernel/, prometheus_math/,
  harmonia/memory/architecture/sigma_kernel*.md. Outside that,
  coordination ticket.
- Anti-conventional discipline: capability-gap encodings should
  match the substrate's deliberately-different design, not import
  standard mathematical-object representations from established
  libraries. The substrate is built around (object, operator-output)
  pairs and operator-derived structural partitions, not human
  discipline categories. Resist the pull toward "what mathlib4 /
  PARI / sage would do here."

## Authorization for this dispatch

Contract changes are AUTHORIZED — public function signatures,
dataclass fields, opcode semantics, schemas, and the canonicalization
protocol may all be modified, BUT every contract change must:

1. Be documented in harmonia/memory/architecture/sigma_kernel.md
   (or sister architecture doc) as the new locked contract.
2. Have round-trip tests in prometheus_math/tests/ exercising the
   new primitive.
3. Pass the full pytest sweep before commit (sigma_kernel/ +
   prometheus_math/, all tests; baseline ~399 was the count after
   T007's deg-12 work, plus whatever has landed since).
4. Have a self-review section in your dispatch journal addressing:
   (a) is this contract change minimal — could a smaller change have
   served? (b) does the new contract align with the substrate's
   anti-conventional architecture? (c) is the new contract documented
   so the next loop restart picks it up cleanly?

## What to drain (priority order)

### Tier 1 — Hardening contract changes (small, clear-cut). Do all.

- **T-2026-05-06-ST003** (P2): get_raw_invariant_keys silently
  returns sentinel for unregistered domains. Change: raise on
  unregistered (or named-error). This is contract-changing because
  callers may rely on the sentinel. Document new behavior in the
  function docstring + sigma_kernel.md. Add migration note for any
  internal callers that depended on the sentinel.

- **T-2026-05-07-T020** (P2): ExclusionCertificate scope_id
  collisions. Change: __post_init__ raises CertificateCollisionError
  on duplicate scope_id (unless explicit-supersede flag set). This
  is contract-changing because previously-valid duplicates will now
  raise. Document.

- **T-2026-05-07-T021** (P2): CanonicalizationProtocol
  decidability_status defaults. If audit shows the default is
  unsafe (silent UNDECIDED-on-missing): harden to explicit value
  required + raise on missing. Document.

### Tier 2 — Audit-only (no code change). Do all.

- **T-2026-05-07-T029** (P2): Multi-precision audit for KillVector
  v2 numeric components. Walk components, identify which need
  multi-precision (mpmath / gmpy2). File MULTIPRECISION_AUDIT.md.
  Do NOT implement multi-precision in this dispatch — too large;
  spawn a follow-up ticket with proposed contract change for the
  next contract-change window.

- **T-2026-05-07-T018** (P1): Silent-sentinel pattern audit across
  substrate getter API. Cross-references ST003. Walk all get_*
  functions; classify as raises-on-unregistered (good) vs sentinel
  (bad). File audit at prometheus_math/SILENT_SENTINEL_AUDIT.md.
  For each silent-sentinel found, add a hardening change to your
  Tier-1 batch (small, mechanical) within this same dispatch — they
  are all the same pattern as ST003. Do not file follow-up tickets
  for these; just fix in-place.

### Tier 3 — Design-first capability gaps. Triage; pick 2-3 to fully
implement.

The 6 capability-gap tickets (T023-T028, plus T030 operator-
portability) are large design decisions. In this single dispatch you
will NOT finish all of them. Triage:

1. For ALL six tickets (T023, T024, T025, T026, T027, T028) and
   T030: produce the design doc at the *_GAP.md path specified in
   each ticket's acceptance_criteria. Each design doc names the
   proposed primitive, its dataclass shape, the CoordinateChart it
   sits in, and a worked example of encoding one specific
   mathematical object.
2. Pick 2-3 of the 7 design docs to also IMPLEMENT minimally —
   primitive ships, round-trip test passes, sigma_kernel.md updated.
   Recommend picking from this priority order:
   - T030 (Operator-portability primitive) — most foundational; the
     other capability-gap encodings benefit from it.
   - T023 (Maass form Hecke eigenvalue) — calibration anchor density
     win in under-explored harmonic-analysis territory.
   - T030 + one other based on your judgment.
3. For the 4-5 designs you DON'T implement: leave the design doc
   in place + leave the ticket OPEN with an updated description
   noting "design landed at X, implementation deferred to next
   contract-change window." James will trigger the next window when
   he sees the backlog warrant it.

DO NOT scope-creep across all 7 designs in a single dispatch —
quality > coverage.

### Tier 4 — Anti-collapse refinement (optional, time permitting).

- **T-2026-05-07-T037** (P2): Convergence-bias self-check on
  substrate verdicts. If any contract change you made above plausibly
  affects substrate's confidence calibration, build the bias-audit
  primitive and run it pre/post your changes to confirm no basin
  drift introduced. Skip if no bearing.

## What to skip in this dispatch

- All Tier-1+ pressure-infrastructure tickets (T008-T017): these are
  test-only modules within file ownership and don't need a contract-
  change window. They're queued for the regular loop.

- All coordination/Ergon-driven tickets (T031-T034): same — within
  file ownership; pickup in the loop.

- T036 (calibration anchor density measurement primitive): this is
  contract-bearing IF it adds public API. Defer to next window
  unless the design doc you produce in Tier-3 work makes it trivial
  to bundle.

- Anything new that surfaces from your Tier-1 audits unless it's a
  same-pattern silent-sentinel fix (which you handle in-place per
  T018).

## What to commit

One commit per ticket. Commit message must include:
- Ticket id
- "contract-change" tag (e.g. "Contract change: T020 ...") so the
  history is searchable
- Summary of the contract change
- Documentation file updated

Push after each commit so any concurrent reviewer can monitor.

## Output expected at the end

Single summary document at
`pivot/contract_change_window_2026-05-07_summary.md` listing:
- Each ticket processed: status (DONE / DESIGN-LANDED-IMPL-DEFERRED /
  AUDITED-NO-CHANGE / SKIPPED-WITH-REASON)
- Each contract change: old contract, new contract, justification,
  doc location
- Test count: pre vs post (must be non-decreasing on the existing
  baseline)
- Remaining capability-gap backlog ranked for next window
- Any newly-surfaced contract changes filed as new BLOCKED tickets
  for the next window (do not implement in this dispatch beyond
  what's in your tier triage)

When this summary is committed and pushed, the dispatch is closed.
James will read it, then restart the loop.

## Time cap

~8 hours of focused work. If you hit the cap before finishing
Tier-3 implementations: stop where you are, file the remaining
designs as OPEN-with-design-landed, write the summary, push. Do
not silently extend past the cap.

— Begin.
```

---

## After Techne completes

Restart sequence (James-driven):
1. Read `pivot/contract_change_window_2026-05-07_summary.md` to confirm scope.
2. Restart Techne loop with the patched KICKOFF_PROMPTS prompt (now contains the "read inbox FRESH every fire" + "re-read before closing" steps).
3. Restart Substrate-Tester loop.
4. Optional: restart Ergon + Learner-Tester if those were also paused.

The new locked contract is whatever Techne committed during this window. Future loop fires honor it; new BLOCKED-CONTRACT-CHANGE tickets accumulate against the *new* lock until the next window.
