# Evidence Wiki operations (V1)

## Service
- Run: `python -m ew.service` in `evidence_wiki/` (binds per `config.json`,
  default 0.0.0.0:8377). Health: `GET /api/v1/health` (unauthenticated).
- Watchdog: Task Scheduler job `MnemosyneEvidenceWikiWatchdog` runs
  `scripts/ew_watchdog.ps1` every 5 min; starts the service when the health
  endpoint fails and logs to `derived/watchdog.log`.
  Register: `scripts/register_ew_watchdog.ps1`.
  Kill switch: `schtasks /Delete /TN MnemosyneEvidenceWikiWatchdog /F`.
- Verified 2026-09-02 (G15): deliberate `taskkill` of the service; watchdog
  restarted it; health returned 200 within 8 s.

## Firewall
Inbound TCP 8377, rule "Mnemosyne Evidence Wiki 8377", remote scope
192.168.1.0/24 + localhost, profiles private/domain. The Postgres port is
NOT exposed; the REST API is the only cross-machine surface.

## Auth (V1)
- Per-machine bearer tokens in `config.json` `machine_tokens` (M1-M4). A
  machine token BINDS the claimed `X-Prometheus-Machine`; a mismatch is 401.
- The V0 shared token remains accepted as LEGACY for compatibility; responses
  attribute it as `legacy_shared`. Plan: remove after all four machines pull
  this branch and export their token.
- Client: `EvidenceWiki(...)` reads the config; on M2-M4 set
  `EW_SERVICE_URL=http://192.168.1.202:8377` and (optionally) override the
  Authorization header with the machine's own token.

## Token rotation
1. Edit `machine_tokens` in `config.json` (new random value for the machine).
2. Commit + push; pull on the affected machine.
3. Restart the service (kill; watchdog restarts, or run the watchdog script).
4. Old token stops working immediately; write attribution is unaffected
   because identity is bound to the token, not the header.
Rotation is append-only in effect: `ew.write_log` keeps the historical
attribution of every accepted write.

## Failure logging
- Service stdout/stderr: `derived/service.out.log` / `derived/service.err.log`
  (when watchdog-started) or the launching shell.
- Rejected writes: `ew.write_log` rows with `accepted=false` + reason.
- Watchdog events: `derived/watchdog.log`.

## Fixture hygiene
Test/demo objects are never deleted; they are classified append-only in
`ew.object_namespace` (namespaces `fixture`, `test`). Production views
(`ew.claims_prod` / `evidence_prod` / `relations_prod`) exclude them, and
search/coordinates/telemetry read only those views. To inspect fixtures,
query the raw tables explicitly.

## Pooled-write requalification trigger (binding, 2026-09-03)
`ew/db.py` hands out pooled connections (ThreadedConnectionPool(2,16) behind
a proxy whose `close()` returns the connection). Any change to connection-pool
ownership, transaction lifecycle, retry behavior, or `connect()`/`close()`
semantics AUTOMATICALLY REOPENS the pooled-write qualification subset BEFORE
deployment:

    python tests/test_distributed_v3.py    # concurrent ingest, duplicate/retry
                                           # injection, crash + full replay,
                                           # reads during writes
    python tests/test_firewall_v3.py       # native surface stays clean
    idempotent replay                      # re-POST an identical batch; rows
                                           # must not increase, stored==DISTINCT

Score G21 by the invariant (stored == DISTINCT; no duplicate logical records),
not by the frozen harness's absolute 600-row expectation -- the substrate is
append-only, so that count grows legitimately across runs.

History: the first pooled deployment failed here. Lazy pool init raced under
4-way concurrency, producing two pools and putconn-against-the-wrong-pool
errors (overt 500s, no partial rows, provenance_failures 0). Fixed with a
double-checked lock plus a double-close guard. This is the seam that broke;
it is why the trigger exists.
