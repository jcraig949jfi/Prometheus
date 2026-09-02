# GEN-2 HOSTILE QUALIFICATION — FROZEN PLAN (2026-09-01, pre-execution)

Target: SFE gen-2 at https://192.168.1.202:8811 (/v2), engine source at
SerendipityFoundry/SerendipityFoundryEngine @ commit 15f9d02a2, client at
SerendipityFoundry/SerendipityFoundryClient (same commit). Battery executes
against the LIVE engine with two throwaway identities; all expectations
frozen here first. Static predictions from code review are labeled
[STATIC-PREDICTED] and do not substitute for behavioral verification.

| T | invariant | frozen expectation | static prediction |
|---|---|---|---|
| T1 | C1 late pred after first outcome evidence gets no prospective credit | reject or explicit downgrade | FAIL predicted: full credit conferred (state=OBSERVED + CLAIM_* event); no prospective concept in schema |
| T2 | C1 new observation must not reset window | same | FAIL predicted (same path) |
| T3 | C2/C11 duplicate observation binding: no double credit | deterministic, documented | AMBIGUOUS predicted: multiple obs per exp allowed; CLAIM_* fires per obs |
| T4 | C6 prediction mutation | immutable or explicit amendment | PASS predicted: no mutation routes exist (405) |
| T5 | C6 prediction mutation post-observation | same | PASS predicted (405) |
| T6 | C6 hypothesis mutation | lineage explicit | PASS predicted (405); amendment mechanism ABSENT (limitation) |
| T7 | C6 experiment mutation post-evidence | no silent rewrite | PASS predicted (405) |
| T8 | C7 observation replace/delete | non-destructive provenance | PASS predicted (no routes); supersession mechanism ABSENT (limitation) |
| T9 | C8 cross-client read | 403 | PASS predicted (verified at first contact) |
| T10 | C8 cross-client write/bind | 403 | PASS predicted |
| T11 | C8 cross-session/world evidence reuse (bind exp of world A into obs of world B) | blocked | probe |
| T12 | C3 durable exhaustion + retry | 409 persists | PASS predicted (verified) |
| T13 | C4 duplicate execution request | no free duplicate / no double debit | FINDING predicted: duplicate registration unmetered (ties to DFX-2) |
| T14 | C4 request-identity idempotency | documented behavior | ABSENT on epistemic POSTs (limitation) |
| T15 | C5 unknown top-level field | 422 | PASS predicted |
| T16 | C5 unknown NESTED scientific config field (budget spec extra key) | 422 | probe |
| T17 | C5 invalid value for known field (outcome=MAYBE) | fail closed | probe (ValidationError mapping) |
| T18 | C5 unsupported capability (enforcement class unavailable; DELAYED_SHARING) | explicit reject or declared semantics | probe vs declared honest gaps |
| T19 | C10 rejected op leaves audit trace | ledger records the rejection | PASS predicted for budget path (commit-then-raise); probe others |
| T20 | C10 failure-producing action -> first-class failure evidence | queryable failure | probe via /failures + worker fail |
| T21 | C9 release identity on responses | exact build attributable | FAIL predicted: /v2/version has api/schema/runtime only; no commit/build hash; no header |
| T22 | C5 config round-trip (budget + experiment spec) | requested == persisted | probe (spec_hash + resources echo) |
| T23 | C12 laundering via object recreation (E2 same spec, late pred, bind) | blocked or characterized | LIMITATION predicted: accepted; acute given T1 |
| T24 | C13 replay vs replication identity | distinct lifecycle | BLOCKED: no replay engine (declared honest gap) |

Statics already established by code review (labeled findings, to be confirmed
behaviorally where possible): DFX-1 (P1) C1 absent + advertised 409
prediction_ordering UNREACHABLE (dead guard: obs event seq always exceeds any
existing pred seq); DFX-2 (P1, declared in docs as I8 PARTIAL) no server-
authoritative budget-consuming transition; DFX-3 (P2) release identity not
first-class.
