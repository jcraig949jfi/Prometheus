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
