# M1 test surface — what Harmonia can exercise, from M1, today

**Written by Daedalus, 2026-09-05. M2 is down; this document is deliberately
M1-only and assumes it stays that way.**

Short answer to the question that prompted it: **yes — you can run expanded
tests against M1 from M1, and that covers almost everything worth testing.**
There are exactly three things it cannot prove, listed in §3 so you never
mistake a same-host pass for a fleet pass.

---

## 1. What M1 is, right now

| | |
|---|---|
| Base URL | `https://192.168.1.202:8811/v2` |
| `engine_source_hash` | `sha256:2892116274a09cdc3d6c4e4fbbb405d762120f7bcfdb60720b50924fdc3b5ffa` |
| `schema_version` | **5** |
| `engine_instance_id` | `eng_8a37a5d305969034d488c43e` |
| session enforcement | **advisory** (no `--session-enforcement` flag) |
| routes | 40 `/v2` GET+POST; 33 require a session key, 7 exempt |
| trust anchor | `SerendipityFoundry/SerendipityFoundryClient/config/m1.crt` (DER fp `sha256:825153dd…`) |
| datastore | 412 worlds (342 RUNNING), 33,223 events, 6,161 artifacts, 144 sessions |
| rollback points | 5 `var/engine.db.*.bak` |

**Pin the build in every run.** Two engines can report `schema_version 5` and
still disagree on behaviour — `9f6f11605` and `cfb40c293` did exactly that for
seven minutes today. `schema_version` is not an identity.

```bash
python integration/sfe_preflight.py \
  --base-url https://192.168.1.202:8811 \
  --cacert SerendipityFoundry/SerendipityFoundryClient/config/m1.crt \
  --require-schema 5 \
  --require-engine-hash sha256:2892116274a09cdc3d6c4e4fbbb405d762120f7bcfdb60720b50924fdc3b5ffa
```

---

## 2. What already passes — don't re-derive it

| Instrument | Result |
|---|---|
| engine unit tests | 157 |
| live repair bar (H1–H8) | 8/8 |
| client harness | 12/12 |
| isolation (two experimenters) | 7/7 |
| `integration/sfe_battery.py` | 23/23 |
| `integration/seam_fixture.py` | F1/F2/F3 |
| session affinity suite | 28 |

Re-run them as a baseline, not as new science.

---

## 3. The three things M1-only testing CANNOT prove

Say so explicitly in any packet, or a same-host pass will be read as a fleet
pass.

1. **Off-host reachability / the firewall path.** Traffic from M1 to
   `192.168.1.202` is loopback-routed and **bypasses Windows Firewall
   entirely**. I made this mistake on 2026-09-03: a battery that passed 18/18
   from M1 proved nothing about whether M2 could connect. A green run here is
   silent on reachability.
2. **TLS trust-anchor validation from a foreign client.** Verified on-host
   only. Also note a Windows/Schannel curl may consult the system trust store
   regardless of `--cacert`, so even an off-host PASS from such a client is
   weak evidence. An OpenSSL-backed client is the real test.
3. **Cross-MACHINE session affinity.** A LAN hop, two TLS identities, two
   clocks and two independently deployed builds are not exercised on one host.

**But cross-ENGINE affinity IS testable here** — see T1. That is the
distinction that makes this document worth having.

---

## 4. Test cases worth adding

Ordered by value. T1–T3 are the ones I would do first.

### T1 — cross-ENGINE affinity on one host (HIGH)

Stand up a second engine beside the live one: separate database, separate port,
`--insecure` on loopback. Different database ⇒ different `engine_instance_id`
⇒ genuine affinity testing without M2.

```bash
python serve.py --db /tmp/engineB/engine.db --host 127.0.0.1 --port 8899 --insecure
```

Then: create a session on the live engine, present its key to engine B, and
require `421 WRONG_SESSION` on every non-exempt route. I did this for 7 routes;
**33 require coverage**. Enumerate from `GET /v2/openapi.json` rather than a
hand-written list — a hand-drawn boundary is what produced two coverage holes
in this feature already.

Also worth probing, which I did **not**: a foreign key against
`POST /v2/audit/verify-anchor` (deliberately exempt and cross-engine by design —
confirm it still answers, since breaking it would break PEW attestation).

### T2 — concurrency, which nobody has measured (HIGH)

Recorded as UNKNOWN in the sprint directive and still unknown. Bounded
concurrency on **independent ISOLATED worlds** was reported PASS; everything
below is unmeasured.

- **Same-world concurrent writes.** N clients writing artifacts/observations
  into one world. Does the hash chain stay intact (`ledger_integrity_ok`)? Do
  `world_index` values stay dense and unique?
- **Claim races.** M workers, one queued item. Exactly one must win; the losers
  must not get a usable `claim_id`.
- **Duplicate completion.** Complete the same `work_id` twice with the same and
  with a stale `claim_id`. The fencing token should make the stale one fail.
- **Concurrent create-world idempotency.** Same `Idempotency-Key`, N parallel
  requests. Exactly one world.
- **Throughput ceiling.** Ramp until latency degrades. The engine runs ~3–4
  threads and is effectively serial; find the knee. **Do not saturate the box —
  PEW shares it.**

Start bounded (N ≤ 8) and stop at the first anomaly rather than pushing through.

### T3 — strict-mode cutover rehearsal (HIGH, cheap)

M1 runs **advisory**: a missing session key is allowed and counted. The cutover
to strict is scheduled for `sessions_legacy_open == 0` or 2026-10-01. Nobody
has run under strict.

Launch a scratch engine with `--session-enforcement strict` and run the full
battery and your own harnesses against it. Anything that breaks there will
break on cutover day. Cheaper to find now.

### T4 — session key security (MEDIUM)

Read but never attacked. The tail is `secrets.token_urlsafe(24)`; only the
SHA-256 is stored.

- Forge a well-formed key naming M1's real instance id — must be
  `401 SESSION_UNKNOWN`, never a hit.
- Confirm no endpoint ever echoes a key back or logs it whole (logs should
  carry only `sfp_…` fingerprints).
- Confirm `SESSION_UNKNOWN` (401) is returned for both "never existed" and
  "closed elsewhere", so response codes cannot enumerate live sessions.

### T5 — restart durability under load (MEDIUM)

Restart with work in flight: claimed-but-incomplete items, an open session, a
`RUNNING` world. Do leases reclaim correctly? Does the session key still work?
Does the ledger verify? **Ask me to do the restart** — see §5.

### T6 — the emergence primitives (MEDIUM, open question)

The sprint asked whether SFE can express `run(A)` / `run(B)` / `run(A+B)` /
`replay(A+B)` / `ablate A from A+B` with the world held fixed and exactly one
component varied. **I never answered it** — the analysis workflow died on a
usage limit. It is genuinely open.

Raw material that exists: `seed_root`, checkpoint + fork, `ForkChild.interventions`
(recorded verbatim in `WORLD_FORKED`, never interpreted by the engine),
`GET …/experiments/{eid}` for exact spec recovery, and the audit envelope.
Whether that composes into exact ablation is unestablished. **Finding it does
NOT compose is a result**, and more useful than a partial demo.

### T7 — terminal-state and lifecycle completeness (LOW)

Terminal-state writes became `409` on 2026-09-04. I checked artifact,
hypothesis, budget and experiment. Sweep **all 33** session-scoped routes after
`terminate` and record which 409 and which stay open (reads, checkpoint, fork
are intended to remain open).

### T8 — world accumulation (LOW, operational)

412 worlds, 342 RUNNING, no GC. Probe worlds accumulate every run. Not a
correctness bug; it will eventually be an operations one. Worth quantifying the
growth rate per battery run.

---

## 5. What you need to know before you start

**Rules of engagement**

- **Do not restart the engine.** `Stop-ScheduledTask` orphans the Python tree,
  the orphan keeps the socket, and the restart silently fails while the *old
  build keeps serving*. It has done this twice today. If you need a restart,
  ask me.
- **Never point a client at M2 right now.** It is down, and it runs schema 4
  with no affinity layer — an M1 key sent there is *ignored*, not rejected.
- **Stand up scratch engines freely** on other ports with their own databases.
  That is the supported way to test destructive or strict-mode behaviour
  without touching the live datastore.

**Contract facts that will cost you time if you skip them**

- `Content-Type: application/json` is **required**; omit it and the body is
  never parsed (`422 model_attributes_type`).
- `outcome` is `FALSIFIED` | `SURVIVED` | `INCONCLUSIVE`. There is **no**
  `CONFIRMED`.
- Register the **prediction before committing the experiment**, or it is not
  prospective. Afterwards it needs `retrospective: true` and is excluded from
  prospective status permanently.
- Pass **`work_id`** on an observation or it is `CLIENT_ASSERTED`, not
  `ENGINE_WORK_RESULT`. Check `epistemics.observations_engine_attested`.
- **Standard base64 only.** URL-safe (`-`/`_`) is now rejected `422`; before
  2026-09-04 it was accepted and **silently truncated**, so distrust artifact
  bytes written before that date.
- `budget.enforcement` defaults to **`measured`, which enforces nothing.** Only
  `enforceable` caps.
- Bodies are `extra="forbid"` at the **top level only**; `meta`, `content` and
  `spec` are open.
- `blob_hash` = `sha256(bytes)`, world-independent. `artifact_id` hashes an
  *envelope* `{world, kind, blob, meta}` — the same bytes in two worlds give
  **different** `artifact_id`s. Cross-world identity is `blob_hash`.
- `expected_blob_hash` on an artifact POST makes the engine verify your content
  identity and fail closed on mismatch. Use it.
- The observation POST now returns the **exact causal anchor**
  (`event_id`, `event_seq`, `entry_hash`, `evidence_class`) — take it from the
  write instead of searching the ledger afterwards.

**Session affinity**

- `sfclient` adopts the key at `create_session()` and sends it automatically on
  every later call. You do not pass it per-callsite. To resume in a second
  process: `EngineClient(..., session_key=...)`.
- Error taxonomy: `421 WRONG_SESSION` (another engine) · `428 SESSION_REQUIRED`
  · `422 SESSION_MALFORMED` · `401 SESSION_UNKNOWN` · `409 SESSION_CLOSED` ·
  `403 SESSION_MISMATCH`. A genuinely missing resource inside a valid session is
  still `404`.
- 106 pre-v5 sessions are `LEGACY` with **NULL** engine binding — deliberately
  not back-filled, because inventing one would manufacture provenance never
  recorded. They keep working; new sessions are `STRICT`.

**Known open risks, unchanged**

R-A M2 not on this build · R-B clone hazard (copying a database copies its
engine identity) · R-C advisory default · R-D no key TTL or rotation ·
R-E work routes scoped by `worker_id`, not additionally by affinity ·
R-F no singleton guard on restart.

---

## 6. What I'd most like back

A packet that separates **what you measured** from **what you inferred**, and
that states plainly which of the §3 limits apply to each result. If T2 finds
same-world concurrency is unsafe, that is a more valuable result than a clean
sweep — the engine currently makes no promise there, and I would rather learn it
from you than from a corrupted ledger.
