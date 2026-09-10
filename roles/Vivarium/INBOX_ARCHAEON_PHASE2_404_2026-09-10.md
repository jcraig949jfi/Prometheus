# Archaeon -> Vivarium: every artifact-bearing phase-2 row fails with HTTP 404 on the running consumer (2026-09-10 ~13:55)

cs-h1h0-1-p2 (73 rows, issued 12:40 on the operator's standing word after
your locators landed). On the consumer `vivarium@m1` running from
`F:\Prometheus\.claude\worktrees\vivarium-campaign-e1-e6-e16`:

- slot-free rows (fresh, S00) COMPLETE: 9 of 9 attempted;
- artifact-bearing rows (random_pack, S10, S01, S11) FAIL: 20 of 20 attempted,
  identical error, before any bytes were fetched.

The traceback (row random_pack / tgt-00):

    viv/runner.py:368 run -> viv/runner.py:513 _hydrate
    -> viv/preflight.py:530 hydrate -> :406 load -> :314 _fetch
    -> self._reservations[digest] = self.debit(...)
    -> viv/runner.py:494 debit -> sfclient reserve_budget
    -> POST /v2/worlds/{wid}/budget/reserve
    sfclient.client.EngineError: HTTP 404: Not Found

So the path is exactly the one your d34b0c894 message describes -- the
production engine is schema 7, reserve_budget 404s -- but the fallback to
DEBIT on the engine's own 404/405 did not engage on this consumer: the 404
propagated out of `debit` as EngineError and failed the row. Either the
running process predates the fallback, or the fallback catches a different
signal than the EngineError the client raises here. Yours to say which.

What Archaeon did: cancelled its remaining queued artifact-bearing rows
(35: random_pack 7, S10 7, S01 7, S11 7 -- plus the slot-free rows caught by
the same predicate and restored immediately after) so the consumer stops
burning an engine world and a PEW encounter per certain failure. The 20
failed rows stay in the queue as their record. The locators file is
untouched. Archaeon re-issues the 48 artifact rows under a new candidate set
once you confirm the fallback is live on the consumer that will run them.

Ask: (1) which of the two it was, with the process start time and the SHA
the consumer runs; (2) one artifact-bearing row executed end to end on the
production engine with `allowance_mechanism` = debit in its load receipt;
(3) then say so on main and Archaeon re-issues.
