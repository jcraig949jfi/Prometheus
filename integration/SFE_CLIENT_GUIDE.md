# Serendipity Foundry Engine — client guide

**Everything a client on M2 (or any host on the LAN) needs to use the Engine.**
Self-contained: endpoint, auth, and every REST route. Verified live 2026-09-04
against build `sha256:6a4f3aee…`.

Maintainer: Daedalus (M1 / SKULLPORT).

---

## 1. Endpoint

| | |
|---|---|
| **Base URL** | `https://192.168.1.202:8811/v2` |
| **Host** | M1 / SKULLPORT, `192.168.1.202` |
| **Port** | `8811` |
| **Scheme** | `https` — TLS required, no plaintext listener |
| **OpenAPI** | `https://192.168.1.202:8811/v2/openapi.json` |
| **Interactive docs** | `https://192.168.1.202:8811/v2/docs` |
| **Liveness (no auth)** | `GET /v2/version` |

Reachable from the whole `192.168.1.0/24` subnet; anything off-subnet is dropped
at the host firewall. The service is always-on (Windows scheduled task
`SFEngine`) and survives logout and reboot.

**Connect by IP, never by hostname.** The certificate carries an IP SAN
(`192.168.1.202`) and no DNS name, so `https://SKULLPORT:8811` fails TLS
verification even though it reaches the right machine.

### TLS

Self-signed; the trust anchor ships in this repo:

```
SerendipityFoundry/SerendipityFoundryClient/config/m1.crt
```

Valid to 2028-12-01. Pass it as the CA file — `--cacert` for curl,
`cafile=`/`ssl.create_default_context(cafile=…)` in Python. You never need the
private key.

```bash
curl --cacert SerendipityFoundry/SerendipityFoundryClient/config/m1.crt \
     https://192.168.1.202:8811/v2/version
```

```json
{"api":"v2","schema_version":4,"runtime":"serendipity-foundry-sfe",
 "registration_open":true,
 "engine_source_hash":"sha256:6a4f3aee…","source_commit":"e6146376…"}
```

`engine_source_hash` / `source_commit` identify the exact build, and are also on
**every** response as `x-sfe-engine-source-hash`, `x-sfe-api-version`,
`x-sfe-schema-version`. Record them with anything you keep.

---

## 2. Auth

Bearer token. Register once — this call needs no auth:

```bash
curl --cacert <m1.crt> -X POST https://192.168.1.202:8811/v2/clients \
     -H 'Content-Type: application/json' -d '{"name":"my-client"}'
# → {"client_id":"cli_…","token":"gen2_…","note":"token shown once; store it"}
```

Then send it on every other call:

```
Authorization: Bearer gen2_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

- **The token is shown once** and stored only as a hash. Lose it and you
  register again (or ask the operator to reissue against the same `client_id`).
- **The token is your identity.** Every world/session/artifact you create is
  bound to it, and isolation is enforced: another client touching your objects
  gets `403`, even knowing the ids. Guard it like a password.
- `registration_open` in `GET /v2/version` tells you whether `POST /v2/clients`
  will issue a token. If it is `false`, ask the operator.

Status codes you will actually see: `401` missing/unknown token · `403` object
belongs to another client · `404` unknown world · `409` illegal state
transition · `422` malformed body, with a JSON field path.

**`Content-Type: application/json` is required** on every POST. Omit it and the
body is never parsed as JSON: `422 model_attributes_type`.

---

## 3. All 62 routes

Counted from the live `openapi.json` on 2026-09-06 after schema v7: **54
distinct paths, 62 method+path pairs**. (An earlier cut of this guide said 49 and its table was
missing six live routes; both are corrected below.) "Body required" lists
required fields; `?x&y` means required query parameters.

### Identity

| Route | Body required |
|---|---|
| `GET /v2/version` | — (no auth) |
| `POST /v2/clients` | `name` (no auth) |
| `POST /v2/sessions` | `name` |
| `POST /v2/sessions/{sid}/close` | — (gated on OWNERSHIP, not on the session key) |
| `POST /v2/topology-groups` | — |

### Worlds — lifecycle

| Route | Body required |
|---|---|
| `POST /v2/worlds` | `session_id`, `name` |
| `GET /v2/worlds` | — |
| `GET /v2/worlds/{wid}` | — |
| `POST /v2/worlds/{wid}/start` | — |
| `POST /v2/worlds/{wid}/pause` | — |
| `POST /v2/worlds/{wid}/resume` | — |
| `POST /v2/worlds/{wid}/terminate` | — |
| `POST /v2/worlds/{wid}/checkpoint` | — |
| `POST /v2/worlds/{wid}/fork` | `checkpoint_id`, `children` |

### Worlds — observability (read)

| Route | Required |
|---|---|
| `GET /v2/worlds/{wid}/status` | — |
| `GET /v2/worlds/{wid}/events` | — |
| `GET /v2/worlds/{wid}/knowledge` | — |
| `GET /v2/worlds/{wid}/resources` | — |
| `GET /v2/worlds/{wid}/failures` | — |
| `GET /v2/worlds/{wid}/lineage` | `?kind&id` |
| `GET /v2/worlds/{wid}/experiments` | — (`?state`) |
| `GET /v2/worlds/{wid}/experiments/{eid}` | — (returns the FROZEN spec, so a run is replayable without the repo) |
| `GET /v2/worlds/{wid}/observations` | — |

### Artifacts

| Route | Body required |
|---|---|
| `POST /v2/worlds/{wid}/artifacts` | `kind`, `data_b64` |
| `GET /v2/worlds/{wid}/artifacts/{aid}/content` | — |
| `POST /v2/worlds/{wid}/import` | `source_world`, `source_artifact` |

### Epistemic protocol

| Route | Body required |
|---|---|
| `POST /v2/worlds/{wid}/hypotheses` | `statement` |
| `POST /v2/worlds/{wid}/predictions` | `hyp_id`, `content` |
| `POST /v2/worlds/{wid}/experiments` | `spec` |
| `POST /v2/worlds/{wid}/experiments/{eid}/commit` | — |
| `GET /v2/worlds/{wid}/experiments/{eid}/analysis` | — |
| `GET /v2/worlds/{wid}/experiments/{eid}/audit-envelope` | — (the whole sealed record as one hash-sealed object, for export) |
| `POST /v2/worlds/{wid}/observations` | `exp_id`, `content`, `outcome` |
| `POST /v2/worlds/{wid}/failures` | `failure_type`, `falsifier`, `violated` |
| `POST /v2/worlds/{wid}/budget/consume` | `resource`, `amount` |

### Work queue

| Route | Body required |
|---|---|
| `POST /v2/work/claim` | `worker_id` |
| `POST /v2/work/{work_id}/heartbeat` | `worker_id`, `claim_id` |
| `POST /v2/work/{work_id}/complete` | `worker_id`, `claim_id`, `result` |
| `POST /v2/work/{work_id}/fail` | `worker_id`, `claim_id`, `error` |
| `GET /v2/work/{work_id}/attestation` | — |

### Audit (credential-free, cross-engine by design)

| Route | Body required |
|---|---|
| `POST /v2/audit/verify-anchor` | `world_id`, `event_id`, `entry_hash` |

Send `exp_id`/`obs_id` too. Without them the call proves only that an event
EXISTS, and a wrong-but-real event passes; with them the engine checks BINDING
and rejects a mismatch. This route takes no bearer token and no session key on
purpose, so a third party can verify an anchor it did not produce.

### Measurements and cross-seat reads (v7, 2026-09-06)

| Route | Body required |
|---|---|
| `POST /v2/measurements` | `name`, `version`, `implementation_hash`, `domain` |
| `GET /v2/measurements` | — (`?name&domain&limit`) |
| `GET /v2/measurements/{mid}` | — (accepts an id OR an identity_hash) |
| `GET /v2/worlds/{wid}/observations/{obs_id}/measured/{mid}` | — |
| `POST /v2/read/scopes` | `name` |
| `GET /v2/read/scopes` | — |
| `POST /v2/read/scopes/{sid}/worlds` | `world_ids` |
| `POST /v2/read/scopes/{sid}/grants` | `grantee_client_id` |
| `GET /v2/read/grants` | — |
| `POST /v2/read/grants/{grant_id}/revoke` | — |
| `GET /v2/read/worlds` | — (`?group&limit`) |
| `GET /v2/read/observations` | — (`?group&world_id&evidence_class&limit`) |

A **measurement** says what was measured, **where its value is** in a freeform
observation (`value_path`, a dotted address), and **what a value means**
(`direction`, `unit`, range). `identity_hash` is derived from the definition,
so an executor's `measurement_identity_hash` resolves to a registered oracle
instead of being comparable only with itself.

A **read grant** is the only way one client reads another's rows. It is scoped
to a **read scope** — a curated set of the owner's own worlds, deliberately not
a topology group, because that field gates `_may_cross` and a read grant must
not confer artifact-import rights. Grantable only by the scope's owner,
read-only,
revocable, and it does **not** widen `GET /v2/worlds` — the cross-tenancy is in
the `/v2/read/*` path. `GET /v2/read/observations` returns a corpus census
(tenancy, evidence classes, truncation) beside the rows.

### Scientific provenance (v6, 2026-09-05)

All additive. Every field below is optional and no existing call changes shape.
Full reference: **`SerendipityFoundryEngine/docs/SCIENTIFIC_PROVENANCE.md`**.

| Route | Body required |
|---|---|
| `POST /v2/families` | `kind` |
| `GET /v2/families` | — (`?kind&limit`) |
| `GET /v2/families/{fid}` | — |
| `POST /v2/families/{fid}/members` | `member_kind`, `member_id` |
| `POST /v2/families/{fid}/close` | — |
| `POST /v2/claims` | `estimand`, `status` |
| `GET /v2/claims` | — (`?family_id&status&limit`) |
| `GET /v2/claims/{clm}` | — |
| `POST /v2/claims/{clm}/retract` | `reason` |

A **family** is the first cross-world container in the engine — a campaign,
comparison or selection spans worlds by definition, and every other scientific
table declares `world_id NOT NULL`. Without it, "the survivor of twelve" and
"the only one I ran" are the same record.

Three additive fields on existing calls:

* `POST /v2/worlds/{wid}/experiments` accepts `unit_of_analysis` + `declared_n`
  + `source_set` (all three or none). That registers the experiment as an
  **analysis**; the engine hashes the source set and **counts distinct units**
  under your key. 128 observations from 8 worlds are n=8 under `world` and
  n=128 under `observation` — it reports both numbers and decides neither.
* `POST /v2/work/{work_id}/complete` accepts
  `attestation: {executed_config | executed_config_hash, entry_state_hash,
  player_identity_hash, measurement_identity_hash}`. The engine compares your
  executed config against the `spec_hash` it sealed at commit. Send the config
  and it is hashed with the same canonicalization, so a faithful executor
  matches by construction.
* `POST /v2/worlds/{wid}/fork` children accept `intervention_effect:
  {before, after}` and `intervention_effective`. Identical before/after hashes
  mean the perturbation changed nothing.

**Every request body is `extra="forbid"` at the top level** — an unknown field
is a `422`, not a warning. Nested objects (`meta`, `content`, `spec`) are open.

---

## 4. Minimal working session

```bash
B=https://192.168.1.202:8811/v2
C=SerendipityFoundry/SerendipityFoundryClient/config/m1.crt
H="Content-Type: application/json"

TOK=$(curl -s --cacert $C -X POST $B/clients -H "$H" \
      -d '{"name":"m2-client"}' | python -c "import sys,json;print(json.load(sys.stdin)['token'])")
A="Authorization: Bearer $TOK"

SID=$(curl -s --cacert $C -X POST $B/sessions -H "$A" -H "$H" \
      -d '{"name":"s1"}' | python -c "import sys,json;print(json.load(sys.stdin)['session_id'])")

WID=$(curl -s --cacert $C -X POST $B/worlds -H "$A" -H "$H" \
      -d "{\"session_id\":\"$SID\",\"name\":\"w1\",\"seed_root\":424242}" \
      | python -c "import sys,json;print(json.load(sys.stdin)['world_id'])")

curl -s --cacert $C -X POST $B/worlds/$WID/start -H "$A" -H "$H" -d '{}'
curl -s --cacert $C $B/worlds/$WID/status -H "$A"
```

A Python client ships in the repo and needs no `pip install` (stdlib only):

```python
import sys; sys.path.insert(0, "SerendipityFoundry/SerendipityFoundryClient")
from sfclient import EngineClient
c = EngineClient("https://192.168.1.202:8811", cafile=".../config/m1.crt")
print(c.version())
token = c.register("m2-client")     # store this
```

### Running one experiment end to end

Work is enqueued by **committing an experiment with `enqueue: true`** — there
is no bare enqueue route:

```
hypotheses → predictions → experiments {commit:true, enqueue:true}
   → work/claim → heartbeat → complete → observations
```

Three rules that will cost you time if skipped:

1. **`outcome` is `FALSIFIED` | `SURVIVED` | `INCONCLUSIVE`.** There is no
   `CONFIRMED`; anything else is a 422.
2. **Register the prediction before committing the experiment.** A prediction
   counts as prospective only if it precedes the commit. Afterwards it is
   accepted only with `retrospective: true`, and is excluded from prospective
   status permanently.
3. **Pass `work_id` on the observation** or it is recorded as `CLIENT_ASSERTED`
   rather than `ENGINE_WORK_RESULT`. Check via
   `GET …/status` → `epistemics.observations_engine_attested`.

---

## 5. Defaults worth knowing before you rely on them

| | |
|---|---|
| `sharing_policy` | `ISOLATED`. Anything else lets worlds see each other's artifacts. |
| `budget.enforcement` | **`measured`, which enforces NOTHING.** Only `enforceable` actually caps. Legal values: `enforceable`, `measured`, `estimated`, `unavailable`. |
| `seed_root` | yours to set; two runs with different seeds are not replicates |
| artifact size | **no limit exists in code** — 32 MB accepted. Any cap is your own courtesy. |

**Use STANDARD base64 for `data_b64`.** URL-safe base64 (`-`/`_`) and any
malformed input are **rejected with a 422** naming `body.data_b64` (strict
decoding as of build `c358a53b`, 2026-09-04; still true on `6a4f3aee`). Before that build the endpoint
accepted URL-safe input with a 200 and silently stored different, shorter
bytes — so verify anything written earlier: the returned `blob_hash` is exactly
`sha256(your bytes)` and must match your own digest.

`blob_hash` is world-independent; `artifact_id` is world-scoped, derived from
(world, kind, meta, content). Reposting identical content to the same world is
idempotent.

Terminating a world does **not** stop artifact writes (still 200); only the
experiment path enforces `RUNNING`.

**`GET /v2/version` now reports the RULES, not only the build.** Two engines can
report an identical `engine_source_hash` and still behave differently, because
the enforcement modes were launch arguments that appeared in no response. Check
both before you trust a comparison across engines:

| field | M1 today | meaning |
|---|---|---|
| `session_enforcement` | `advisory` | `strict` = a missing session key on a bound session is a `428`. A **presented** key is fully judged in both modes. |
| `science_profile` | `warn` | `off` = v6 checks not computed at all; `warn` = computed, returned and sealed, never blocking; `strict` = a finding that contradicts your own sealed declaration fails the call. |
| `engine_instance_id` | `eng_8a37a5d305969034d488c43e` | identity of the **ledger**, minted once per database. `engine_source_hash` is the identity of the **build** — two engines running the same build share it. If you hold an anchor, this is the field that says which engine minted it. |

On `warn`, **nothing you send can be refused by a v6 check.** Findings arrive as
a `science.profile_findings` list on the response and are sealed into the event
chain.


---

## 6. Verify your setup

```bash
python integration/sfe_battery.py \
    --cacert SerendipityFoundry/SerendipityFoundryClient/config/m1.crt
```

23 checks against the live service; writes `handoff.json` (**contains your
bearer token — treat as a credential**) and leaves you a RUNNING world.

If `GET /v2/version` times out: are you on `192.168.1.0/24`? can you
`ping 192.168.1.202`? did you use the IP rather than a hostname? is `--cacert`
readable?

---

## 7. More detail

| | |
|---|---|
| **Automated producer / executor contract (Archaeon, Vivarium)** | `integration/SFE_CONTRACT_FOR_ARCHAEON_AND_VIVARIUM.md` |
| Scientific provenance: families, claims, analysis, attestation (v6) | `SerendipityFoundry/SerendipityFoundryEngine/docs/SCIENTIFIC_PROVENANCE.md` |
| Full REST reference, per-route examples | `SerendipityFoundry/SerendipityFoundryClient/docs/API.md` |
| Connection/TLS/token detail | `SerendipityFoundry/SerendipityFoundryClient/docs/CONNECTING.md` |
| Integration + Proteus/PEW seam status | `integration/HARMONIA_FIRST_INTEGRATION.md` |
| Reconstructing the record later (schema, anchors, traps) | `integration/SFE_ARCHAEOLOGY_SCHEMA.md` |
| Operator/runbook (M1 only) | `roles/Daedalus/RUNBOOK.md` |

The Engine's own `openapi.json` is authoritative over all of the above.
