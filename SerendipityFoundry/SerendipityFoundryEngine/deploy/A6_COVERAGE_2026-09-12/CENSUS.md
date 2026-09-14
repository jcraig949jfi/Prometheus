# A6 coverage census, 2026-09-12 (a census, not a redesign)

Question: which UNKNOWN outcomes can A6 settle today, and which stay
UNKNOWN_UNRECONCILABLE by construction? Measured on the live ledger
(D:\Prometheus-data\sfe\engine.db, read-only), the deployed api.py, and the
consumers' code on main. A6 itself is in the HELD build (8c53d04e6); nothing
below is a live journal count -- there is no journal yet.

## 1. What A6 attests WITHOUT any key (the request path alone)

    intent   written for every mutating request (34 routes) before the lock
    refused  written on every 4xx/5xx/exception  -> CONFIRMED_NO_EFFECT
    effected written after the handler's COMMIT returned, before the response
             bytes leave -> CONFIRMED_EFFECT

A client that TIMES OUT on a slow-but-alive engine still gets an outcome
line: the handler runs to completion in the threadpool and the middleware
writes `effected` (or `refused`) regardless of whether anyone is still
listening. Against the thirteen rows of 2026-09-11 that means: the 8
`create_world` refusals -> CONFIRMED_NO_EFFECT; the 4 post-commit-step
timeouts -> the commit itself CONFIRMED_EFFECT; rule 146 (commit timed out
on the client, landed on the engine) -> CONFIRMED_EFFECT once the handler
finished, keyless. Stated as reasoning from the code order in
sfe/api.py (`_stamp_release`: effected/refused are written before `return
response`), not as a measurement of a real disconnect; the wiring test
covers the order, not the disconnect.

## 2. What needs a key: an intent with NO outcome line

That happens only when the engine PROCESS dies (or the journal write fails)
between `intent` and the outcome -- a crash, a kill, a power loss. Then the
separate witness (deploy/reconcile_attestations.py) settles the row IF the
intent carried an Idempotency-Key, by the ledger's idempotency_keys row
written in the same transaction as the effect. Without a key:
UNKNOWN_UNRECONCILABLE, by construction and by design (nothing to look up).

## 3. Keyed callers vs unkeyed callers (measured)

Engine routes that ACCEPT a key: 9 of 34 mutating routes -- POST /v2/worlds,
.../hypotheses, .../predictions, .../experiments, .../observations,
.../failures, .../artifacts, .../budget/reserve, .../budget/consume.
Routes that do NOT (a key is ignored): work/claim, work/complete, work/fail,
families, family members, claims, sessions, fork, checkpoint, commit, the
read-scope management routes.

idempotency_keys on the ledger, lifetime: 14 rows, 0 today.
    daedalus-livebar-*   worlds        4   (my qualification probes)
    harmonia-m2          hypotheses    4, experiments 3, artifacts 1
    gen21-A / live-regression  hypotheses 2
    vivarium             0
Effects, lifetime: worlds 1,241; experiments 89,859; work completions 3,816;
observations 4,427. Keyed fraction: 14 / 1,241 world creations (1.1%);
0 of 89,859 experiments; 0 of 4,427 observations; 0 of 3,816 completions
(the route takes no key).

Consumer code (main): Vivarium's SfeRunner sends a key on ONE call --
budget reserve (`viv:<attempt_id>:...`, runner.py:533). Those keys land in
budget_reservations.idem_key (60 rows, all keyed), NOT in idempotency_keys,
so the reconciler as written does not see them; the reserve is also not
the write a row cannot afford to duplicate. Vivarium sends none on
create_world / experiment / observation / complete. Archaeon does not call
the engine's mutating routes (it produces queue rows). Harmonia's arena and
T2 harness send keys on hypotheses/experiments.
Reconciler limit, exact: it consults idempotency_keys only; a keyed reserve
would need a second lookup in budget_reservations -- not added, because the
reserve is not the ambiguous write.

## 4. Exact coverage today

    shape                                   keyless A6      with key
    refusal (lock timeout, 4xx, 5xx)        CONFIRMED_NO_EFFECT   same
    slow engine, client timed out           CONFIRMED_EFFECT      same
    engine process died after COMMIT        UNKNOWN_UNRECONCILABLE  CONFIRMED_EFFECT
    engine process died before COMMIT       UNKNOWN_UNRECONCILABLE  CONFIRMED_NO_EFFECT

Reconcilable fraction of the last two shapes for Vivarium's rows today: 0 of
N (no keys). Reconcilable fraction for Harmonia's keyed calls: 100% on the
keyed routes.

## 5. Does this materially limit A6's intended value?

Partly. The incident A6 was designed from (a stall, engine alive) is covered
keyless. The uncovered case is a crash mid-transaction, which has not been
observed on this engine; its consequence is one row per crash whose outcome
must be settled by hand. Before recurrent fossil consumption grows volume,
the cheap closure is:

SMALLEST FOLLOW-UP REQUIREMENT (not applied; Vivarium's lane):
    Vivarium's SfeRunner must send Idempotency-Key on the two creations a
    row cannot afford to duplicate --
        POST /v2/worlds                 key = viv:<queue experiment_id>:world
        POST /v2/worlds/{w}/experiments key = viv:<queue experiment_id>:exp
    The queue experiment_id is already the row's stable UUID (it reaches the
    engine today in the work result as attempt_id and PEW as
    producer.queue.experiment_id), so no new identifier is minted. Both
    routes already accept the header; the engine changes nothing.
    Completion (POST /v2/work/{id}/complete) takes no key by design: it is
    fenced by claim_id and replay-idempotent by result_hash (v6 C3e).
