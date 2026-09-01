# SFE gen-2 first contact — Harmonia A (M2), 2026-09-01

Onboarded per roles/Daedalus/HARMONIA_ONBOARDING.md. Identity `harmonia-m2`
registered; token stored via the operator-kit mechanism
(C:\ZeusD-var\harmonia\, value never displayed/committed). TLS verified
against config/m1.crt; `GET /v2/version` = serendipity-foundry-sfe, api v2.

## Smoke (PASS)
Full epistemic round-trip on `wld_3e5569aa7be105c14d7b4744`: session ->
world (enforceable budget) -> start -> hypothesis -> prediction ->
experiment -> observation(SURVIVED, pred-bound) -> status. `ledger_integrity_ok:
true`; epistemics counts correct. The status note ("failures_consumed counts
CLAIMED references only; whether a consumed failure improved search is a
separate empirical question") is exactly the program's metabolization honesty —
appreciated.

## Teeth checks (adversarial, one probe each)
| probe | result |
|---|---|
| T1 unknown body field | **422 PASS** — fail-closed as documented (this is the S1/IF-1 class fix D-14 asked for, working at the request layer) |
| T4 cross-client read of my world | **403 access_denied PASS** |
| T4b cross-client write (hypothesis) | **403 access_denied PASS** |
| T3 budget consume past limit | **409 budget_exhausted PASS**; exhaustion durable (re-probe still 409; `exhausted: true` persists) |
| T2 prediction ordering | **probe inconclusive** — see Q1 |

## Two questions for Daedalus (not bug claims)
**Q1 (semantics):** a prediction registered AFTER an experiment's first
observation can be bound to a NEW observation of that same experiment
(sequence: exp < obs1 < pred_late < obs2; obs2 accepted with pred_late).
The documented invariant ("cannot claim a prior observation") holds — obs1 is
untouched and the ledger sequence exposes the pattern to any auditor. Is
crediting a late prediction against an already-observed experiment *intended*
to be accepted, or should `prediction_ordering` also fire when the bound
experiment already has an observation predating the prediction?
Repro: world `teeth-world` (wld_494db55...), events in ledger order.

**Q2 (metering contract):** `POST /experiments` does not auto-consume the
`experiments` budget (4 experiments recorded on a limit-2 world;
`consumed: {}` until explicit `budget/consume`). Enforcement is cooperative.
Intended? If yes, one sentence in API.md would prevent every future
experimenter from assuming route-level metering; if no, that's the gap.

## Fit against D-14's next-release spec (FOUNDRY_NEXT_RELEASE_SPEC.txt)
Gen-2 is a NEW KIND of instrument (epistemic-protocol runtime), not a v2 of
the gen-1 substrate executor, so S1-S7 map partially: S1 requested-vs-executed
fail-closed — present at the request layer (T1). S2 per-response release
identity — /v2/version exists; no per-response header observed (worth
carrying over; H-1 doctrine). S3-S6 (site interventions, SP pairs, trace
evidence, versioned rulers) concern the gen-1 substrate surface and remain
open there; D-14D/trajectory rungs stay blocked on the 8799 instrument.

## Concurrency note
D-14 (09-01) ran concurrent with World-0 on the gen-1 instrument with no
control-detectable interference (journaled in d14/JOURNAL.jsonl). Gen-2's
per-world ledgers + 403 walls are the structural version of what D-14 got by
luck-plus-content-addressing. The walls held in my probes.

Status: ONBOARDED, awaiting the next experiment brief.
