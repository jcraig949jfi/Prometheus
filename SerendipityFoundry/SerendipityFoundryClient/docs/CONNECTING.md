# Connecting to the Serendipity Foundry Engine

Everything a client needs to reach the Engine: **where it listens, how to get a
token, and which cert to trust.** Read this once and you can connect from any
machine on the LAN.

> **First time integrating?** Read
> [`integration/HARMONIA_FIRST_INTEGRATION.md`](../../../../integration/HARMONIA_FIRST_INTEGRATION.md)
> at the repo root and run `integration/sfe_battery.py`. It verifies the whole
> surface in one command and hands you a working world. This file is the
> connection reference it builds on.

---

## 1. Where the Engine listens

| | |
|---|---|
| **Host** | **M1 / SKULLPORT** |
| **IP address** | **`192.168.1.202`** |
| **Port** | **`8811`** |
| **Scheme** | **`https`** (TLS is required off-loopback) |
| **Base URL** | **`https://192.168.1.202:8811`** |
| **API prefix** | `/v2` |
| **OpenAPI (machine-readable)** | `https://192.168.1.202:8811/v2/openapi.json` |
| **Interactive docs** | `https://192.168.1.202:8811/v2/docs` |
| **Liveness / identity (no auth)** | `GET /v2/version` |

The Engine binds a **specific** address (never `0.0.0.0`). It runs as an
always-on Windows scheduled task named **`SFEngine`** under an S4U principal, so
it survives logout and the lock screen and restarts at boot. If `GET /v2/version`
answers, the Engine is up:

```json
{ "api": "v2", "schema_version": 3, "runtime": "serendipity-foundry-sfe",
  "registration_open": true,
  "engine_source_hash": "sha256:5274ddbe9120ddbb…",
  "source_commit": "a2898d19601b9cfc2619e105418cb637562accb7" }
```

`engine_source_hash` and `source_commit` identify the exact build answering you,
and are also stamped on **every** response as `x-sfe-engine-source-hash`,
`x-sfe-api-version` and `x-sfe-schema-version`. Record them alongside any result
you intend to keep: they are what makes a run attributable to a build.
`registration_open` tells you whether `POST /v2/clients` will issue you a token
(see §3) before you try.

**Connect by IP, never by hostname.** The certificate carries an IP SAN
(`192.168.1.202`) and no DNS name, so `https://SKULLPORT:8811` fails
verification even though it reaches the right machine.

### Firewall / reachability

M1 admits `8811` **only from the local subnet** (`192.168.1.0/24`). A client on
that subnet (e.g. **M2 = `192.168.1.191`**) can connect; anything off-subnet is
dropped at the host firewall. If a connection times out, check first that your
machine is on `192.168.1.0/24` and can `ping 192.168.1.202`.

---

## 2. The TLS certificate (keys & certs)

The Engine terminates TLS with a self-signed certificate whose **CN/SAN is
`192.168.1.202`**, valid **through December 2028**. Because it is self-signed,
your client must trust it explicitly — the trust anchor ships with this package:

```
config/m1.crt      ← give this to the client as the CA file
```

- **Python client:** pass `cafile="config/m1.crt"` (the examples do this by
  default). The connection then verifies the Engine's identity and refuses an
  impostor.
- **curl:** `curl --cacert config/m1.crt https://192.168.1.202:8811/v2/version`
- **The `--insecure` escape hatch** disables verification. Use it only for a
  throwaway local probe, never in anything that carries a real token — an
  unverified TLS session can be MITM'd and your bearer token captured.

You never need the Engine's **private key** (`m1.key`) to be a client; it lives
only on the Engine host. Clients only need the **public certificate**
`config/m1.crt`.

---

## 3. Getting a token (authentication)

Auth is a **bearer token**. You obtain one by registering a client — a single
unauthenticated call:

```
POST /v2/clients
{ "name": "my-client" }
```

The response returns the token **once** (it is not retrievable later — the Engine
stores only a SHA-256 hash of it):

```json
{ "client_id": "cli_…", "token": "gen2_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "note": "token shown once; store it" }
```

Tokens are prefixed **`gen2_`**. Send it on every subsequent call:

```
Authorization: Bearer gen2_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

With the Python client, `register()` does this for you and adopts the token:

```python
from sfclient import EngineClient
c = EngineClient("https://192.168.1.202:8811", cafile="config/m1.crt")
token = c.register("my-client")     # returns the token AND sets it on the client
print("store this:", token)
```

To **reuse** an existing token (a second process, a worker on another box),
construct the client with it directly — no re-registration:

```python
c = EngineClient("https://192.168.1.202:8811", token="gen2_…",
                 cafile="config/m1.crt")
```

### What the token authorizes

A token *is* a client identity. The Engine binds every object you create
(sessions, worlds, work, artifacts) to that identity and enforces isolation:
**another client cannot read, drive, or fish the work queue of your worlds, even
if it learns their ids** — the attempt returns `403`. An unauthenticated call
returns `401`. Guard the token like a password; anyone holding it acts as you.

Tokens do not expire on their own, but the operator can **revoke** a token
(it returns `401` thereafter) and **reissue** a new token bound to the *same*
`client_id` — so you can rotate a credential without losing your identity or
provenance (operator tool: `manage_client.py`). After bootstrap the operator may
also close open registration (`serve.py --registration closed`), in which case
`POST /v2/clients` returns `403` and you obtain a token from the operator.

---

## 4. Connection profile (`config/engine.example.json`)

A ready-to-edit profile so you don't hard-code connection details:

```json
{
  "base_url": "https://192.168.1.202:8811",
  "cafile":   "config/m1.crt",
  "client_name": "my-client",
  "token": null,
  "_notes": "Copy to engine.json and fill token after first register()."
}
```

Copy it to `config/engine.json`, register once, paste the returned token into
`token`, and load it:

```python
import json
from sfclient import EngineClient
cfg = json.load(open("config/engine.json"))
c = EngineClient(cfg["base_url"], token=cfg["token"], cafile=cfg["cafile"])
```

---

## 5. Quick verification

From this machine (M1/SKULLPORT) or any LAN client:

```powershell
# no auth needed — proves reachability + TLS trust
curl --cacert config/m1.crt https://192.168.1.202:8811/v2/version

# full round-trip: register, drive a world, run a worker, fork, print status
python examples/run_sample.py

# every capability, PASS/FAIL table, non-zero exit on any failure
python test_harness/harness.py
```

If `/v2/version` answers but `run_sample.py` fails on TLS, your `cafile` path is
wrong. If it fails on `401`, your token is missing or unknown. If a foreign
object call returns `403`, isolation is working as designed.

Next: **[API.md](API.md)** — every endpoint with example calls.
