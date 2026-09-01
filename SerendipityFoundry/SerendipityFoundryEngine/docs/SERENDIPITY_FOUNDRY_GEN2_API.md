# Gen-2 API (`/v2`)

FastAPI app in `gen2/api.py`. Machine-readable spec at `GET /v2/openapi.json`
(interactive docs at `/v2/docs`). Versioned; scientific request bodies are
`extra="forbid"` (unknown fields -> 422).

## Auth & ownership

- `POST /v2/clients {name}` -> `{client_id, token}` (token shown once).
- All other routes require `Authorization: Bearer <token>`; the token resolves
  to a client id, which is passed into the runtime. Missing/unknown token -> 401.
- A client may only touch its own worlds/sessions. Knowing another world's id
  while holding a valid token yields 403 on every operation (proved: `test_http_
  isolation_attack`). Runtime `AccessDenied` -> 403, `NotFound` -> 404,
  `InvalidTransition`/`Conflict`/`BudgetExhausted` -> 409, `ValidationError` ->
  422, `IsolationViolation` -> 403, `LedgerIntegrityError` -> 500. Bodies:
  `{"detail": {"error": <code>, "message": ...}}`.

## Routes

Identity / session
- `POST /v2/clients` `{name}`
- `POST /v2/sessions` `{name}`
- `GET  /v2/version`

Worlds
- `POST /v2/worlds` `{session_id, name, sharing_policy?, topology_group?, budget?, seed_root?}`
- `GET  /v2/worlds`  (this client's worlds)
- `GET  /v2/worlds/{wid}`
- `POST /v2/worlds/{wid}/start|pause|resume|terminate`
- `POST /v2/worlds/{wid}/checkpoint`
- `POST /v2/worlds/{wid}/fork` `{checkpoint_id, children:[{name, sharing_policy?, topology_group?, seed_root?, interventions?}]}`
- `GET  /v2/worlds/{wid}/events?limit=`
- `GET  /v2/worlds/{wid}/status`   (machine-readable: state, queue depth, active
  workers, expired leases, resources, failure counts, epistemics, ledger_integrity_ok, head_hash)
- `GET  /v2/worlds/{wid}/resources`
- `GET  /v2/worlds/{wid}/failures?failure_type=&consumed=`
- `GET  /v2/worlds/{wid}/lineage?kind=&id=&direction=descendants|ancestors`

Research objects
- `POST /v2/worlds/{wid}/hypotheses` `{statement}`
- `POST /v2/worlds/{wid}/predictions` `{hyp_id, content}`   (sealed at registration)
- `POST /v2/worlds/{wid}/experiments` `{spec, hyp_id?, pred_id?, enqueue?, kind?, priority?}`
- `POST /v2/worlds/{wid}/observations` `{exp_id, content, outcome, pred_id?}`   (ordering enforced)
- `POST /v2/worlds/{wid}/failures` `{failure_type, falsifier, violated, ...}`
- `POST /v2/worlds/{wid}/artifacts` `{kind, data_b64, meta}`
- `POST /v2/worlds/{wid}/import` `{source_world, source_artifact}`   (policy-gated; records provenance)
- `POST /v2/worlds/{wid}/budget/consume` `{resource, amount}`

Work queue
- `POST /v2/work/claim` `{worker_id, world_id?, lease_s?}` -> `{work}` (or null)
- `POST /v2/work/{work_id}/heartbeat` `{worker_id, lease_s?}`
- `POST /v2/work/{work_id}/complete` `{worker_id, result}`   (idempotent, exactly-once)
- `POST /v2/work/{work_id}/fail` `{worker_id, error, retry?}`

## Running it (separate process, separate port, own DB)

Gen-2 does NOT touch the live D-13 service. Run it as its own process:

```
.venv/Scripts/python -c "import uvicorn; from gen2.api import create_app; \
  uvicorn.run(create_app(r'C:\\gen2-var\\gen2.db'), host='127.0.0.1', port=8811)"
```

Pick any free port other than 8799. For LAN exposure, apply the same TLS + token
+ firewall discipline the D-13 deployment uses; the auth model here is bearer-
token ownership, suitable for a trusted research LAN.

## Backward compatibility

Gen-2 is a new `/v2` surface; it does not modify or replace the existing D-13
`/v0` API. The two are independent services with independent databases.
