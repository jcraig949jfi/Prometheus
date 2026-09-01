# Serendipity Foundry Engine — REST API (`/v2`)

Base URL: **`https://192.168.1.202:8811`**  ·  all paths below are relative to it.
Machine-readable spec: **`/v2/openapi.json`**  ·  interactive: **`/v2/docs`**.

**Auth.** Every endpoint except `POST /v2/clients` and `GET /v2/version`
requires `Authorization: Bearer gen2_…` (see
[CONNECTING.md](CONNECTING.md#3-getting-a-token-authentication)). Missing/unknown
token → `401`. A world you don't own → `403`.

**Request bodies** are JSON and **fail closed recursively**: unknown fields are
rejected (`422`) at every level of scientific/control configuration — including
nested budget specs, fork-child specs, and an artifact's `info_kind` — because a
scientific request must not carry silently-ignored parameters. Three payloads are
freeform **by design** and documented as such: an experiment's `spec`, a
fork-child's `interventions`, and an artifact's `meta` (except its `info_kind`).

**Errors** come back as `{"detail": {"error": "<code>", "message": "...", ...}}`
with an HTTP status:

| status | meaning | example `error` |
|---|---|---|
| `401` | no/invalid token | `unauthorized` |
| `403` | not your object, or policy forbids it | `access_denied`, `isolation_violation` |
| `404` | no such object | `not_found` |
| `409` | illegal state / conflict / exhausted | `invalid_transition`, `budget_exhausted`, `prediction_ordering` |
| `422` | malformed body (extra/missing field) | (FastAPI validation) |

The examples show `curl` (with `--cacert`) and the equivalent `sfclient` call.

---

## Identity & liveness

### `GET /v2/version` — identity, no auth
Reports the **exact running build**: `engine_source_hash` is computed from the
loaded source at process start (build-derived, not operator-attested) and is also
stamped into every `EXPERIMENT_COMMITTED` event, so a result can be bound to the
instrument that produced it. Pin this hash when you qualify.
```bash
curl --cacert config/m1.crt https://192.168.1.202:8811/v2/version
# → {"api":"v2","schema_version":2,"runtime":"serendipity-foundry-sfe",
#    "registration_open":true,
#    "engine_source_hash":"sha256:…","source_commit":"…"}
```
```python
c.version()
```

### `POST /v2/clients` — register a client, get a token (no auth)
```bash
curl --cacert config/m1.crt -X POST https://192.168.1.202:8811/v2/clients \
     -H 'content-type: application/json' -d '{"name":"my-client"}'
# → {"client_id":"cli_…","token":"gen2_…","note":"token shown once; store it"}
```
```python
token = c.register("my-client")     # returns token AND adopts it
```

### `POST /v2/sessions` — create a session
```bash
curl --cacert config/m1.crt -X POST https://192.168.1.202:8811/v2/sessions \
     -H "authorization: Bearer $TOKEN" -H 'content-type: application/json' \
     -d '{"name":"my-session"}'
# → {"session_id":"ses_…"}
```
```python
sid = c.create_session("my-session")
```

---

## Worlds

A **world** is the durable experimental unit and the isolation boundary.

### `POST /v2/worlds` — create a world
Body: `session_id` (yours), `name`, and optionally `sharing_policy`,
`topology_group`, `budget`, `seed_root`.

`sharing_policy` ∈ `ISOLATED` (default), `FAILURES_ONLY`, `HYPOTHESES_ONLY`,
`FAILURES_AND_HYPOTHESES`, `SUCCESSES_ONLY`, `FULLY_SHARED`, `DELAYED_SHARING`,
`EXPLICIT_IMPORT_ONLY`. Cross-world import is allowed only when both worlds share
a `topology_group` **and** the destination's policy admits that kind of object.

`budget` maps a resource name to `{"limit": <n>, "enforcement": "<class>"}`,
where enforcement ∈ `enforceable` (blocks at the limit), `measured`, `estimated`,
`unavailable`.

```bash
curl --cacert config/m1.crt -X POST https://192.168.1.202:8811/v2/worlds \
     -H "authorization: Bearer $TOKEN" -H 'content-type: application/json' \
     -d '{"session_id":"ses_…","name":"world-1",
          "sharing_policy":"ISOLATED",
          "budget":{"experiments":{"limit":50,"enforcement":"enforceable"}}}'
# → {"world_id":"wld_…","state":"CREATED","next_index":1, …}
```
```python
w = c.create_world(sid, "world-1",
                   budget={"experiments":{"limit":50,"enforcement":"enforceable"}})
wid = w["world_id"]
```

### `GET /v2/worlds` — list your worlds
```python
c.list_worlds()      # → [ {world_id, name, state, …}, … ]
```

### `GET /v2/worlds/{wid}` — get one world
```python
c.get_world(wid)     # → {world_id, state, next_index, sharing_policy, …}
```

### Lifecycle — `POST /v2/worlds/{wid}/{start|pause|resume|terminate}`
Transitions: `CREATED → RUNNING ⇄ PAUSED → TERMINATED`. An illegal transition →
`409 invalid_transition`.
```bash
curl --cacert config/m1.crt -X POST \
     https://192.168.1.202:8811/v2/worlds/$WID/start \
     -H "authorization: Bearer $TOKEN"
# → {"world_id":"wld_…","state":"RUNNING", …}
```
```python
c.start(wid); c.pause(wid); c.resume(wid); c.terminate(wid)
```

### `POST /v2/worlds/{wid}/checkpoint` — snapshot for forking
```python
ck = c.checkpoint(wid)          # → {"checkpoint_id":"ckp_…", …}
```

### `POST /v2/worlds/{wid}/fork` — fork children by reference
Children share the parent's immutable event prefix up to the checkpoint; they
cannot mutate each other or the parent.
```bash
curl --cacert config/m1.crt -X POST \
     https://192.168.1.202:8811/v2/worlds/$WID/fork \
     -H "authorization: Bearer $TOKEN" -H 'content-type: application/json' \
     -d '{"checkpoint_id":"ckp_…","children":[{"name":"A"},{"name":"B"}]}'
# → {"children":[{"world_id":"wld_…","next_index":N}, …]}
```
```python
kids = c.fork(wid, ck["checkpoint_id"], [{"name":"A"}, {"name":"B"}])
```

---

## Observability

### `GET /v2/worlds/{wid}/status` — mechanically-derived status
Returns lifecycle state, **`ledger_integrity_ok`** (the per-world hash chain
recomputed and verified), `epistemics` (counts of hypotheses/predictions/
experiments/observations/failures), and `resources` (budget accounting). Nothing
here is self-reported by a worker; it is derived from the ledger.
```python
st = c.status(wid)
st["ledger_integrity_ok"]              # → True
st["epistemics"]["failures_generated"] # → int
```

### `GET /v2/worlds/{wid}/events?limit=N` — the event ledger
```python
c.events(wid, limit=50)   # → [ {seq, world_id, event_type, entry_hash, …}, … ]
```

### `GET /v2/worlds/{wid}/resources` — budget status
```python
r = c.resources(wid)
r["limits"]["experiments"]     # → {"limit":50,"enforcement":"enforceable"}
r["consumed"]["experiments"]   # → float
```

### `GET /v2/worlds/{wid}/failures?failure_type=&consumed=` — query failures
```python
c.failures(wid, failure_type="low_score")     # filter by type
c.failures(wid, consumed=False)               # only un-metabolized failures
```

### `GET /v2/worlds/{wid}/lineage?kind=&id=&direction=` — walk the DAG
`direction` ∈ `descendants` (default) | `ancestors`.
```bash
curl --cacert config/m1.crt -G https://192.168.1.202:8811/v2/worlds/$WID/lineage \
     -H "authorization: Bearer $TOKEN" \
     --data-urlencode kind=hypothesis --data-urlencode id=$HYP \
     --data-urlencode direction=descendants
```
```python
c.lineage(wid, "hypothesis", hyp_id, direction="descendants")
```

---

## Epistemic protocol

**The experiment COMMIT boundary is the load-bearing invariant.** An experiment
is first *registered* (a plan: editable, non-executable, no budget) and then
*committed*. Commit is irreversible and atomic: it freezes the spec, **closes the
prospective-prediction window**, debits the experiment budget, stamps the running
release identity, and (optionally) releases the experiment for execution.

Honest ordering is enforced **at commit, not at observation** — this matters
because work is executed remotely under a lease, so a worker can know the outcome
before the server sees an observation. A prediction is **prospective** for an
experiment iff it was registered *before that experiment's commit*
(`prediction.created_seq < experiment.committed_seq`). A prediction registered
after commit is refused (`409 prediction_ordering_error`) unless you pass
`retrospective=true`, and is then recorded but **never** counted as prospective.
Observations are only accepted on committed experiments.

Evidence carries provenance: an observation is `ENGINE_WORK_RESULT` when bound to
a verified completed work item (pass `work_id`), else `CLIENT_ASSERTED`. The class
is immutable and travels into the `CLAIM_SURVIVED` / `CLAIM_FALSIFIED` event — a
client assertion can never masquerade as an engine-attested result.

### `POST /v2/worlds/{wid}/hypotheses`
```python
h = c.hypothesis(wid, "all-ones maximizes score")     # → hyp_id
```

### `POST /v2/worlds/{wid}/predictions`
```python
p = c.prediction(wid, h, {"expected_score": 1.0})     # → pred_id
```

### `POST /v2/worlds/{wid}/experiments`
Body: `spec` (freeform, opaque to the Engine), optional `hyp_id`/`pred_id`,
`commit` (default `true` — register **and** commit atomically), and
`enqueue`/`kind`/`priority` (enqueue requires commit). `commit:false` registers a
plan only.
```python
e = c.experiment(wid, {"bits": "1111"}, hyp_id=h, pred_id=p)        # register+commit
plan = c.experiment(wid, {"bits": "1111"}, commit=False)           # plan only
e = c.experiment(wid, {"bits": "1111"}, enqueue=True, kind="evaluate")  # +release work
# → {"exp_id":"exp_…", "work_id":"wrk_…"?, "committed_seq":N?}
```

### `POST /v2/worlds/{wid}/experiments/{eid}/commit`
Cross the irreversible boundary for a previously registered plan.
```python
c.commit_experiment(wid, plan["exp_id"], enqueue=True, kind="evaluate")
```

### `POST /v2/worlds/{wid}/observations`
On a **committed** experiment. `outcome` ∈ `SURVIVED`/`FALSIFIED`/`INCONCLUSIVE`.
`pred_id` binds a prediction (prospective iff it preceded commit); a post-commit
prediction needs `retrospective=true`. `work_id` binds the authoritative work
result (→ `ENGINE_WORK_RESULT`).
```python
o = c.observation(wid, e["exp_id"], {"score": 1.0}, "SURVIVED", pred_id=p)
o = c.observation(wid, e["exp_id"], {"score": 1.0}, "SURVIVED",
                  work_id=e["work_id"])              # engine-attested evidence
```

### `POST /v2/worlds/{wid}/failures` — record a first-class failure
Required: `failure_type`, `falsifier`, `violated`. Optional context:
`experiment_id`, `hypothesis_id`, `prediction_id`, `reference`, `expected`,
`observed`, `measurement_id`, `artifact_refs`, `reproducibility`, `extensions`.
```python
fid = c.failure(wid, failure_type="below_threshold", falsifier="oracle",
                violated="score>=1.0", observed={"bits":"0011","score":0.5})
```

---

## Artifacts & cross-world sharing

### `POST /v2/worlds/{wid}/artifacts` — store a content-addressed artifact
Binary payload is base64 in `data_b64`; `meta.info_kind` classifies it for
sharing-policy checks (e.g. `artifact`, `failure`, `hypothesis`, `success`).
```python
art = c.artifact(wid, "best", b"discovered-bytes", {"info_kind": "artifact"})
# → {"artifact_id":"art_…","blob_hash":"…","origin":"NATIVE"}
```

### `POST /v2/topology-groups` — mint a registered sharing capability
Cross-**client** sharing requires a **registered** `topology_group` — an
unguessable, server-issued capability. Mint one, then hand its id to the other
client out of band and set it on both worlds. (Matching a fabricated or
self-minted group id grants nothing.)
```python
gid = c.create_topology_group(note="A<->B share")   # → "grp_…"
```

### `POST /v2/worlds/{wid}/import` — import from another world (provenance kept)
Same-client import: allowed when both worlds share a `topology_group` and the
destination policy admits the `info_kind`. **Cross-client** import additionally
requires that shared group to be **registered**, the source policy to emit the
kind, and the source artifact to be a **NATIVE origin** (no transitive re-export
of an imported copy — H6). Otherwise `403`. The copy records `origin: IMPORTED`
plus full source lineage.
```python
imp = c.import_artifact(dst_wid, src_wid, art["artifact_id"])
# → {"artifact_id":"art_…","origin":"IMPORTED","source_world":"wld_…", …}
```

---

## Budgets

### `POST /v2/worlds/{wid}/budget/consume`
Consuming past an `enforceable` limit returns `409 budget_exhausted` **and the
exhaustion is durably recorded** (the block persists; it is not rolled back).
```python
c.consume_budget(wid, "experiments", 1)
```

---

## Work queue (for workers)

A **RemoteWorker** claims work, runs a local executor, heartbeats, and commits.
Claims are always scoped to the caller's own worlds; passing `world_id` narrows to
one. Completion is idempotent exactly-once; an expired lease is reclaimed.

**Lease fencing:** a claim returns a server-issued **`claim_id`** that identifies
*this claim attempt*. It is **required** on heartbeat/complete/fail, and is
invalidated the moment the lease is reclaimed — so a stale attempt can never
complete the current one, *even from the same `worker_id`*. (`sfclient`'s
`RemoteWorker` threads it for you.)

### `POST /v2/work/claim`
```bash
curl … -d '{"worker_id":"w1","world_id":"wld_…","lease_s":30}'
# → {"work": {"work_id":"wrk_…","claim_id":"clm_…","kind":"evaluate",
#             "payload":{…}} }   (or {"work":null})
```

### `POST /v2/work/{work_id}/heartbeat` — extend the lease
```bash
-d '{"worker_id":"w1","claim_id":"clm_…","lease_s":30}'
```

### `POST /v2/work/{work_id}/complete` — commit the result (authoritative)
```bash
-d '{"worker_id":"w1","claim_id":"clm_…","result":{"score":1.0}}'
```

### `POST /v2/work/{work_id}/fail` — report failure (optionally requeue)
```bash
-d '{"worker_id":"w1","claim_id":"clm_…","error":"…","retry":true}'
```

All four in Python are wrapped by `RemoteWorker`:
```python
from sfclient import EngineClient, RemoteWorker
def executor(kind, payload):        # runs on the worker; return a JSON dict
    return {"score": 1.0}
worker = RemoteWorker(c, "w1", executor, lease_s=30)
worker.run(world_id=wid)            # claim → heartbeat → complete, until idle
```

See `examples/run_worker.py` for a standalone, reclaim-safe worker you can run on
any machine, and `test_harness/harness.py` for every endpoint exercised end to
end against the live Engine.
