# HARMONIA FIRST INTEGRATION -- PEW

The one document for connecting Harmonia (on M2) to the Prometheus Evidence
Wiki. Everything needed is here; nothing is held in Mnemosyne's head. If this
document and the service disagree, the service is right and this document is
a defect -- `GET /api/v1/fossil/contract` is the machine-readable authority.

Frozen 2026-09-03 against fossil contract `pew.fossil.v1`, schema_version 3.

---

## 0. The service, exactly

    component       Prometheus Evidence Wiki (PEW) / Mnemosyne Evidence Tensor
    repo path       evidence_wiki/   (branch mnemosyne/evidence-wiki-v0)
    host machine    M1, hostname SKULLPORT, LAN 192.168.1.202
    protocol        HTTP/1.1, JSON. No TLS on the research LAN.
    port            8377  (bind 0.0.0.0; firewall rule "Mnemosyne Evidence
                    Wiki 8377", inbound allow, scoped 192.168.1.0/24)
    start command   cd evidence_wiki && python -m ew.service
    supervised by   Task Scheduler job MnemosyneEvidenceWikiWatchdog (5 min)
    persistence     PostgreSQL 17, database prometheus_fire, schema ew,
                    on M1 only. The DB is NEVER exposed to the LAN; REST is
                    the only contract.
    logs            evidence_wiki/derived/service.out.log
                    evidence_wiki/derived/service.err.log
                    evidence_wiki/derived/watchdog.log
                    plus ew.write_log (every write, accepted or rejected)
                    and ew.read_log (every query)
    restart         stop the python -m ew.service process; the watchdog
                    restarts it within 5 minutes, or run the watchdog job now:
                    schtasks /Run /TN MnemosyneEvidenceWikiWatchdog

### Harmonia's connection path from M2

    BASE   http://192.168.1.202:8377/api/v1
    HEADERS
        Authorization: Bearer ew-m2-4b8e02d5a1f7
        X-Prometheus-Machine: M2
        X-Prometheus-Agent: harmonia
        Content-Type: application/json

The token is bound to the machine: presenting the M2 token while claiming
`X-Prometheus-Machine: M1` is 401, and no token is 401. Writes additionally
require both the Machine and Agent headers (400 without them). Attribution
for every write is recorded from these headers.

---

## 1. Verify PEW health

    curl http://192.168.1.202:8377/api/v1/health

PASS looks exactly like:

    {"service":"mnemosyne-evidence-wiki","status":"ok","schema_version":3,
     "ontology_version":2,"fossil_contract":"pew.fossil.v1"}

Health needs no token. Anything other than HTTP 200 with `"status":"ok"`
means the service is down -- check `derived/service.err.log`, then restart.

## 2. Verify version / schema identity

    curl -H "$AUTH" http://192.168.1.202:8377/api/v1/fossil/contract
    curl -H "$AUTH" http://192.168.1.202:8377/api/v1/version
    curl -H "$AUTH" http://192.168.1.202:8377/api/v1/schema

PASS: `fossil_contract == "pew.fossil.v1"` and `schema_version == 3`. The
contract endpoint lists every accepted field, every write outcome, and the
identifier mapping -- code against it, not against prose. `/version` returns
`canonical_revision`, PEW's monotonic write counter (it is PEW's ordering,
NOT the producer's; producer order is `sfe_event_seq`).

## 3. Write one known synthetic integration record

The frozen fixture is `evidence_wiki/integration/fixture_harmonia_v1.json`.
It is unmistakably synthetic (`TESTFIX-` ids) and lives in namespace `test`.

    curl -X POST http://192.168.1.202:8377/api/v1/fossil/encounters \
      -H "Authorization: Bearer ew-m2-4b8e02d5a1f7" \
      -H "X-Prometheus-Machine: M2" -H "X-Prometheus-Agent: harmonia" \
      -H "Content-Type: application/json" \
      -d @- <<'JSON'
    {"encounter_id":"TESTFIX-HARMONIA-ENC-0001","run_id":"TESTFIX-RUN-0001",
     "sfe_entry_hash":"sha256:TESTFIXTURE-ENTRY-HASH-0001",
     "sfe_world_id":"TESTFIX-SFE-WORLD-0001","sfe_event_id":"TESTFIX-EVENT-0001",
     "sfe_event_seq":1,"world_id":"TESTFIX-WORLD-0001",
     "players":["TESTFIX-PLAYER-0001"],"seed":"0","outcome":"committed",
     "failure_class":null,"resources_used":{"ticks":1},
     "occurred_ts":"2026-09-03T00:00:00+00:00",
     "producer":{"component":"pew.integration.fixture","version":"1"},
     "namespace":"test"}
    JSON

## 4. Obtain the record identity

The response carries the identity and the read-back URL:

    {"encounter_id":"TESTFIX-HARMONIA-ENC-0001","run_id":"TESTFIX-RUN-0001",
     "inserted":true,"status":"inserted",
     "read_back":"/api/v1/fossil/encounters/TESTFIX-HARMONIA-ENC-0001"}

A record's identity is the PAIR `(encounter_id, run_id)`. On a second run of
this runbook the same call returns `"status":"duplicate_identical"` and
`"inserted":false` -- that is success, not failure (see s10).

## 5. Read that exact record back

    curl -H "$AUTH" \
      http://192.168.1.202:8377/api/v1/fossil/encounters/TESTFIX-HARMONIA-ENC-0001

Returns `{"encounter_id":..., "n_runs":N, "runs":[...]}` -- every execution of
that encounter spec. Add `?run_id=TESTFIX-RUN-0001` for one exact run.

## 6. Verify the persisted fields

Compare the returned run object field-by-field against what you sent. All
fields round-trip byte-equal; timestamps come back as UTC ISO-8601 regardless
of the server's timezone. The server adds `revision` (PEW write order) and
`created_at` (when PEW stored it, NOT when the encounter happened --
`occurred_ts` is that).

Do not treat HTTP 200 as proof of persistence. The read-back IS the proof.

## 7. Submit a real world/player experiment

Order matters: register the anchors, then the encounters.

    POST /api/v1/fossil/worlds     {"world_id":..., "manifest_hash":...,
                                    "world_binding_id":..., "seed_root":...,
                                    "sfe_head_hash":..., "producer":{...}}
    POST /api/v1/fossil/players    {"player_id":<Proteus organism_id>,
                                    "genome_hash":<manifest hash>,
                                    "runtime_hash":..., "lineage_id":...,
                                    "generation":N, "producer":{...}}
    POST /api/v1/fossil/encounters {...one per executed run...}
    POST /api/v1/fossil/encounters/batch  {"encounters":[... up to ~500 ...]}

`sfe_entry_hash` is REQUIRED on every encounter: it is the SFE ledger anchor
that makes the row evidence rather than assertion. A row without it is 422.

Batch is all-or-nothing: it commits whole or not at all, so a 200 never means
"some of your rows landed". For throughput and its caveat, see s13.

## 8. Query all evidence for a run

    GET /api/v1/fossil/encounters?run_id=<exp_id>:<work_id>

## 9. Query by world and by player

    GET /api/v1/fossil/encounters?world_id=<SFE world_id>
    GET /api/v1/fossil/encounters?player_id=<Proteus organism_id>
    GET /api/v1/fossil/encounters?episode_id=<id>        (if a producer mints one)
    GET /api/v1/fossil/worlds/<world_id>
    GET /api/v1/fossil/players/<player_id>

Selectors combine (AND). At least one is required: an unfiltered query is 400,
by design -- a dump is not a query. `player_id` matches membership in the
encounter's `players[]` array. Add `&namespace=test` to see fixture rows;
scientific queries default to `prod` and never see `test` or `synthetic`.

## 10. Accepted / rejected / failed / duplicate / partial

    HTTP 200 "status":"inserted"             row is committed and readable
    HTTP 200 "status":"duplicate_identical"  already present, byte-identical;
                                             safe idempotent retry, no new row
    HTTP 409 conflict_existing_row_differs:<fields>
                                             a row with this (encounter_id,
                                             run_id) exists and DIFFERS in the
                                             listed fields. NOTHING was written.
                                             This is a producer defect: either
                                             the run identity is wrong (a re-run
                                             needs a new run_id) or the content
                                             changed. PEW never overwrites.
    HTTP 422 fossil_encounter_requires_sfe_entry_hash    missing provenance
    HTTP 422 (pydantic detail naming the field)          unknown field sent:
                                             producer/consumer schema mismatch.
                                             Unknown fields are NEVER silently
                                             dropped.
    HTTP 400                                 missing Machine/Agent header, or
                                             an unfiltered query
    HTTP 401                                 bad token, or token/machine mismatch
    HTTP 404                                 read-back of a nonexistent id
    HTTP 5xx                                 service or database fault -- see
                                             the logs. Never interpret as written.
    PARTIAL WRITES                           do not exist on these routes. A
                                             single write and a batch are each
                                             one transaction.

## 11. Where errors appear

- Client side: the HTTP status and `{"detail": ...}` body.
- Server side: `derived/service.err.log` (tracebacks, uvicorn), and
  `derived/watchdog.log` (restarts).
- Durable audit: every refusal is recorded in `ew.write_log` with
  `accepted=false` and a `reject_reason` BEFORE the error is returned, so a
  rejected write is visible to a later auditor, not only to the caller:

      SELECT created_at, endpoint, machine, agent, reject_reason,
             result_object_id
        FROM ew.write_log WHERE accepted=false ORDER BY created_at DESC;

  (That query is run on M1; Harmonia sees the same facts through the HTTP
  status codes.)

## 12. What exact output means PASS

Run the battery from `evidence_wiki/`:

    python integration/pew_battery.py --host 192.168.1.202 --machine M2 \
        --agent harmonia --no-sql

PASS is `"all_pass": true` with 14/14 gates, and exit code 0. `--no-sql` skips
the two direct-database legs, which only run on M1 (E4's SQL half and E10's
row-leak check); on M2 those legs report `skipped` and the HTTP legs still
prove read-back. Results land in `integration/battery_results.json`.

Any FAIL line names the gate and the observed values. Do not proceed with a
real experiment while any gate is failing.

---

## 13. Performance expectations, and one honest caveat

Measured on M1 on 2026-09-02 with an otherwise idle host: ~48 ev/s single
event, ~3,600 ev/s in batches of 100, replay at the same rate.

Measured on 2026-09-03 while another seat ran a 13-process CPU-bound job on
the same machine: ~1 ev/s, with `GET /api/v1/health` -- which touches no
database and no changed code -- also taking ~1s. The service is single-process
uvicorn and is starved by heavy co-tenants. If throughput looks an order of
magnitude off, check what else is running on M1 before suspecting PEW; the
health endpoint's own latency is the quickest discriminator.

None of the correctness gates depend on latency.
