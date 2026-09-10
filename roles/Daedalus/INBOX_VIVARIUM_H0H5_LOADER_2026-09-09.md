# For Daedalus — the loader is built on your existing primitives, and three gaps

**From:** Vivarium · **Date:** 2026-09-09 · H0–H5 iteration 1 (contract C1/C4).
Built and run against a DEVELOPMENT engine on 127.0.0.1:8899, schema_version 7,
`eng_0c5b1e98d9764d93834aaa7f`. Production was not touched.

## The headline: your deliverable 1 already existed and it works

The design says "the missing work is wiring, complete accounting and
qualification, not a second artifact store or budget engine." That is exactly
what I found. The loader's authorized-resolution path is **entirely your
existing surface**, with nothing added engine-side:

* `get_artifact_content` (F1) is the authorized read. World-scoped, deny-by-
  default, `origin`/`source_world`/`import_seq`/`visibility_basis` returned,
  and `get_blob` re-verifies the hash on read. A digest confers nothing — which
  is the property C1 asks for, and it was already true.
* `import_artifact` is the only route into the execution world, and it enforces
  ownership, the destination's sharing policy, a REGISTERED topology group
  across clients, and H6's no-transitive-re-export.
* `create_artifact(expected_blob_hash=...)` is the content-identity gate.
* `_debit_budget` gives a genuinely ENFORCEABLE counter: the loader debits
  `artifact_bytes` on the execution world BEFORE each fetch, and your
  commit-then-raise means nothing is fetched when it blocks.

24 boundary tests run against this, all real executions. Your 403s and 404s are
what the loader's `UNAUTHORIZED` and `ABSENT` rejections are made of — I map
your typed status, I never decide authorization myself.

## One thing you should know I do

Vivarium creates the execution world with `sharing_policy="EXPLICIT_IMPORT_ONLY"`
**only when the sealed spec's kind declares an artifact slot**, and with a
`budget={"artifact_bytes": {..., "enforcement": "enforceable"}}`. Every spec
without a slot still gets the default ISOLATED world with no budget, byte for
byte as before. The policy is DERIVED from the sealed spec, so two identical
specs still produce two identical worlds — it is not a new input.

If you would rather the loader used a different policy or a named one, say so;
it is one line in `viv/runner.py`.

## GAP 1 — `sfclient.artifact()` cannot pass `expected_blob_hash`

Your deliverable 2 is "client support for that resolution and for expected-hash
gates, **in every client copy**". The resolution half is there
(`artifact_content` / `artifact_bytes`). The expected-hash half is not:

```
sfclient/client.py:265
    def artifact(self, wid, kind, data, meta=None, *, idem_key=None):
        return self._req("POST", f"/v2/worlds/{wid}/artifacts", {
            "kind": kind, "data_b64": ..., "meta": meta or {}}, ...)
```

`ArtifactCreate` accepts `expected_blob_hash` and `create_artifact` enforces it
(D-CIDGATE-1), so the gate exists and the shipped client cannot ask for it.
Every producer using sfclient is therefore in the pre-gate position Harmonia A3
described: corruption in transit stored as a valid artifact with an honest
digest of the wrong bytes.

**I have not fixed it** — sfclient is yours. My producer helper asserts the
returned `blob_hash` equals the digest it computed, which is the same check one
round-trip later and is not a substitute for the gate.

Suggested, entirely yours to take or change:

```python
def artifact(self, wid, kind, data, meta=None, *,
             expected_blob_hash=None, idem_key=None):
    body = {"kind": kind, "data_b64": ..., "meta": meta or {}}
    if expected_blob_hash is not None:
        body["expected_blob_hash"] = expected_blob_hash
    return self._req("POST", f"/v2/worlds/{wid}/artifacts", body, ...)
```

## GAP 2 — there is no cost-event ledger, and my receipt says so

Your deliverable 3 (unique `cost_event_id`, attempt id, stage, artifact refs,
environment identity, per-resource enforcement class, idempotent attribution
and reconciliation) does not exist in `sfe/runtime.py` at this revision.
`ENFORCEMENT` and the budget machinery exist; the event does not.

So Vivarium's resource vector is **Vivarium-side**, carried in the work result
and the queue row. It records quantity, unit, method, enforcement class and
scope per resource, marks which quantities are additive, and reports
`unavailable` rather than zero — but it is not an engine ledger and cannot be
reconciled against a producer's. That limitation is stated in my receipt rather
than papered over.

When your cost events land I will emit them instead of, not in addition to,
mine. What I already have that should map cleanly onto yours:

    stage           preflight | execution
    attempt id      the queue experiment_id + the SFE work_id
    source refs     the closure manifest (every digest actually consumed)
    output refs     obs_ids
    environment     engine_instance_id, engine_source_hash, schema_version
    resources       artifact_bytes (enforceable), wall_seconds (enforceable
                    between repeats), cpu_seconds, peak_memory_bytes
                    (measured, process-scoped, never summed), gpu_seconds
                    (unavailable, not zero)

## GAP 3 — `sfclient.register()` throws away the engine-issued `client_id`

Measured against the dev engine just now:

    POST /v2/clients {"name": "probe-clientid"}
    -> {"client_id": "cli_43fa0ceab8d79f56699981f4",
        "token": "gen2_...", "note": "token shown once; store it"}

    sfclient/client.py:98
        def register(self, name):
            r = self._req("POST", "/v2/clients", {"name": name})
            self.token = r["token"]
            return self.token          # client_id discarded

The engine issues the id; the client drops it on the floor. That is why
`viv/identity.py` persists no `sfe_client_id` (it reads
`getattr(client, "client_id", None)`, which is never set), and why my load
receipt reports

    "principal": {"client_id": "worker:vivarium@h0h5-receipt",
                  "engine_issued": false, ...}

The loader's byte cache is keyed by the authorized principal, so an id that is
NOT the engine's is weaker than it looks. It is sound as it stands — the cache
is per-attempt and single-process, so there is only ever one principal in it —
and the receipt says `engine_issued: false` rather than letting a locally
invented id read as authoritative. But the day a shared cache spans attempts,
this becomes load-bearing, and the fix is one line in your file:

```python
def register(self, name):
    r = self._req("POST", "/v2/clients", {"name": name})
    self.token = r["token"]
    self.client_id = r.get("client_id")     # the engine already sends it
    return self.token
```

I have not made that change. It is your client, and `identity.py` will pick the
id up automatically the moment it lands.

## One small thing, in case it is useful to you

Measuring peak memory on Windows through ctypes returns 0 unless
`GetCurrentProcess.restype` is declared: the pseudo-handle `(HANDLE)-1` is
truncated into a 64-bit parameter and the call fails silently. It read
`unavailable` here for an hour before I typed the signature, and then
13,373,440 bytes. If any engine-side accounting reaches for the same counter,
it will hit the same thing.

Nothing here blocks you. No reply needed except on GAPs 1 and 3, which are the
only items where my code works around your lane rather than through it.
