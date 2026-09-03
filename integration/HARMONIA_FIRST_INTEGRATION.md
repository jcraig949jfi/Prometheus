# SFE / World Server — First Integration

**Audience:** the first experimentalist (Harmonia, M2) and anyone integrating
against the Serendipity Foundry Engine for the first time.
**Maintainer:** Daedalus (M1 / SKULLPORT).
**Written:** 2026-09-03, verified live against the running service the same day.

This document is meant to be sufficient on its own. If you have to ask Daedalus
how something works, that is a defect in this file — say so.

---

## 0. The one thing to know first

**There is no separate "World Server."** One service does both jobs.

| Component | What it is | Where |
|---|---|---|
| **SFE Engine** | The live service. Owns worlds, artifacts, work queue, ledger. | `https://192.168.1.202:8811/v2` — always-on |
| `worldfoundry/wforge` | An **offline** Python package (world generation prototype). No server, no port, no listener. | repo only |

When a directive says "the world server," it means the SFE Engine. `wforge` is a
library you import, not a service you connect to. Nothing in this document
requires it.

---

## HARMONIA FIRST INTEGRATION -- SFE / WORLD SERVER

Copy-paste, in order, from any machine on `192.168.1.0/24`. Nothing here needs
`pip install`; the battery is standard-library only.

### 1. Get the repo (this also gets you the TLS trust anchor)

```bash
git clone https://github.com/jcraig949jfi/Prometheus.git
cd Prometheus
git checkout main
```

The Engine's certificate is **committed** at
`SerendipityFoundry/SerendipityFoundryClient/config/m1.crt`. There is no manual
copy step and nothing to request from Daedalus. (The private key `m1.key` is
gitignored and lives only on M1 — you never need it.)

### 2. Prove you can reach the Engine

```bash
curl --cacert SerendipityFoundry/SerendipityFoundryClient/config/m1.crt \
     https://192.168.1.202:8811/v2/version
```

Expected — an `api` of `v2` and a `schema_version` of **3** or higher:

```json
{"api":"v2","schema_version":3,"runtime":"serendipity-foundry-sfe",
 "registration_open":true,
 "engine_source_hash":"sha256:5274ddbe9120ddbbd75a36965106d2efe640a3b72278e7bb97b82e356e1fc9fc",
 "source_commit":"a2898d19601b9cfc2619e105418cb637562accb7"}
```

**Connect by IP, never by hostname.** The certificate carries an IP SAN
(`192.168.1.202`) and no DNS name, so `https://SKULLPORT:8811` fails TLS
verification even though it reaches the right machine.

### 3. Run the standard battery

```bash
python integration/sfe_battery.py \
    --cacert SerendipityFoundry/SerendipityFoundryClient/config/m1.crt
```

It runs 23 checks against the live service (24 with `--expect-source-hash`),
writes `handoff.json`, and **leaves you a RUNNING world**. Expect `23/23 PASS`.
Verified 24/24 on 2026-09-03 against build `sha256:5274ddbe…`.

To pin the exact build you expect (recommended once you are past first contact):

```bash
python integration/sfe_battery.py \
    --cacert SerendipityFoundry/SerendipityFoundryClient/config/m1.crt \
    --expect-source-hash sha256:5274ddbe9120ddbbd75a36965106d2efe640a3b72278e7bb97b82e356e1fc9fc
```

`handoff.json` contains your `base_url`, `cacert`, `token`, `session_id`,
`world_id`, and the engine build identity. **It contains a bearer token — treat
the file as a credential.** Keep the token: it is shown once and is not
retrievable later. Reuse it with `--token gen2_…` so you stop minting a new
identity on every run.

That is the whole first integration. Everything below is reference.

---

## 4. What the battery checks (S0–S8)

| ID | Check | Why it is here |
|---|---|---|
| **S0** | `GET /version` reachable, no auth | Distinguishes "service down" from "you are misconfigured" before anything else can confuse you |
| **S1** | Engine identity **asserted**: `api=v2`, `schema_version ≥ 3`, runtime name | A green battery must tell you *which* instrument answered, not merely that something did |
| **S1b** | `x-sfe-engine-source-hash` header == `engine_source_hash` in body | Detects split-brain: two responses from different builds |
| **S1c** | Build matches `--expect-source-hash` | Only when you pass it |
| **S1d/e** | Client registration (or supplied token), session opens | Identity works |
| **S2** | World created with fixed `seed_root=424242` | The standard integration world |
| **S3** | Spec invariants: seed, `state=CREATED`, `ISOLATED`, `head_hash` is a sha256 | The world is what you asked for |
| **S3b** | `start` → `RUNNING`, `head_hash` advances | Lifecycle works and the ledger moves |
| **S4** | `status` returns `ledger_integrity_ok: true`, plus `epistemics` and `engine` | The hash chain verifies **now**, not at creation |
| **S5** | Checkpoint created | You can snapshot |
| **S5b** | Fork from checkpoint, child's `parent_world_id` is the parent | You can branch without disturbing the original |
| **S6** | Malformed request → **422 with a field path** | The Engine fails overtly, never silently |
| **S6b** | Unauthenticated read → 401 | Isolation is on |
| **S7/S7b** | **PUSH**: post an artifact, read it back byte-exactly | The write path a player uses |
| **S7c/d** | Hypothesis + prediction registered; experiment committed **with `enqueue: true`** | How work actually gets created |
| **S7e/f/g** | **PULL**: claim that work, heartbeat the lease, complete it with a result | The queue path a worker uses |
| **S7h** | Observation is **engine-attested**: `observations_engine_attested ≥ 1` | The loop closes *and* the evidence is the Engine's, not the client's word |
| **S8** | Events carry `world_id` **and** `event_seq` | The citation keys evidence needs |
| **S8b** | Knowledge frontier queryable | What is visible to a consumer |

**On the two player contracts.** Both work. There is no bare "enqueue" route and
none is needed: **work is enqueued by committing an experiment with
`enqueue: true`** (`POST /v2/worlds/{wid}/experiments` with `commit: true,
enqueue: true`, or `POST …/experiments/{eid}/commit`). A worker then claims it
from `POST /v2/work/claim`. If you read somewhere that HTTP enqueue is
impossible, that claim is wrong and this battery disproves it every run.

---

## 5. Frozen reference identity (as of 2026-09-03)

| | |
|---|---|
| API title / version | `Serendipity Foundry Gen-2` / `2.2.0` |
| `schema_version` | `3` |
| Paths / routes | 31 paths, 33 routes |
| Route-surface digest | `sha256:723b369b81503b9008a4487e8b7dbc2e3d5cd435adb84e066ac6688ecc9b9b68` |
| `engine_source_hash` | `sha256:5274ddbe9120ddbbd75a36965106d2efe640a3b72278e7bb97b82e356e1fc9fc` |
| `source_commit` | `a2898d19601b9cfc2619e105418cb637562accb7` |
| `m1.crt` fingerprint | `sha256:825153dda5608783b605009748bf44aa8d1f109b88f26c7dac685c96fdf64237` |
| Certificate validity | 2026-08-29 → 2028-12-01, IP SAN `192.168.1.202` |

If `engine_source_hash` differs from the above, the Engine was rebuilt. That is
not automatically wrong — but any result you carry across that boundary must
record which build produced it.

---

## 6. The minimal first experiment

The order below is the one the battery executes and the one that works. The
`spec` is yours; the Engine does not interpret it.

```
1.  POST /v2/sessions                   {"name": …}                         -> session_id
2.  POST /v2/worlds                     {"session_id","name",…}             -> world_id  (CREATED)
3.  POST /v2/worlds/{wid}/start         {}                                  -> RUNNING
4.  POST /v2/worlds/{wid}/hypotheses    {"statement": …}                    -> hyp_id
5.  POST /v2/worlds/{wid}/predictions   {"hyp_id","content":{…}}            -> pred_id
6.  POST /v2/worlds/{wid}/experiments   {"spec":{…},"hyp_id","pred_id",
                                         "commit":true,"enqueue":true}      -> exp_id (+ work queued)
7.  POST /v2/work/claim                 {"worker_id","world_id","lease_s"}  -> work (incl. claim_id)
8.  POST /v2/work/{work_id}/heartbeat   {"worker_id","claim_id"}             (extend the lease)
9.  POST /v2/work/{work_id}/complete    {"worker_id","claim_id",
                                         "result":{…}}
10. POST /v2/worlds/{wid}/observations  {"exp_id","content","outcome",
                                         "pred_id","work_id"}
```

Required fields, verbatim from the live schema:

- `HypothesisCreate` → `statement`
- `PredictionCreate` → `hyp_id`, `content` (object)
- `ExperimentCreate` → `spec` (object); optional `hyp_id`, `pred_id`, `commit`, `enqueue`, `kind`, `priority`
- `ObservationCreate` → `exp_id`, `content` (object), `outcome`; optional `pred_id`, `work_id`, `retrospective`, `replication`
- `ArtifactCreate` → **`kind`**, **`data_b64`**; optional `meta`
- `WorkClaim` → `worker_id`; optional `world_id`, `lease_s`
- `WorkHeartbeat` → `worker_id`, **`claim_id`**; optional `lease_s`
- `WorkComplete` → `worker_id`, **`claim_id`**, **`result`** (object — *not* `artifacts`)
- `WorkFail` → `worker_id`, `claim_id`, `error`; optional `retry`

Every request body is `extra="forbid"`. An unexpected field is a **422**, not a
warning. This is deliberate: scientific requests fail closed.

### Three rules that will bite you if you skip them

**1. `outcome` is Popperian, and the vocabulary is closed.** Legal values are
exactly `FALSIFIED`, `SURVIVED`, `INCONCLUSIVE`. There is no `CONFIRMED` — a
prediction that holds has *survived*, not been proven. Anything else is a 422
`{"error":"validation_error","message":"bad outcome"}`.

**2. Register the prediction BEFORE committing the experiment.** A bound
prediction counts as *prospective* only if `pred.created_seq <
exp.committed_seq`. The commit closes the foresight window before execution is
possible, so a post-hoc prediction cannot be laundered into foresight. A
prediction registered after the commit is accepted **only** if you explicitly
pass `retrospective: true`, and it is then excluded from prospective status
permanently. No later observation reopens the window.

**3. Pass `work_id` on the observation, or your evidence is only your own
word.** With `work_id` bound to a COMPLETED work item enqueued for *that*
experiment, the Engine verifies it and records
`evidence_class = ENGINE_WORK_RESULT`. Without it, the class is
`CLIENT_ASSERTED` — recorded as such on the observation, the event, and any
downstream adjudication. Both are accepted; only one is attested. Check which
you got via `GET …/status` → `epistemics.observations_engine_attested`.

The `claim_id` returned by `/work/claim` is a **server-issued fencing token**.
It is required on heartbeat/complete/fail and is invalidated when a lease is
reclaimed, so a timed-out worker's late result can never become authoritative.
Do not cache it across claims.

Read state with `GET …/status`, `…/events`, `…/knowledge`, `…/resources`,
`…/lineage?kind=&id=` (both query params are required), `…/artifacts/{aid}/content`.

---

## 7. Knobs you must NOT touch on a first integration

These change what a result *means*, silently. Leave every one at its default
until you have a reason and have written the reason down.

| Knob | Default | Why not to touch it |
|---|---|---|
| `sharing_policy` | `ISOLATED` | Anything else lets worlds observe each other's artifacts. Cross-world visibility destroys the independence that makes replication meaningful, and it does so without any error. |
| `seed_root` | `424242` for the standard world | Changing it changes the world. Two runs with different seeds are not replicates, and nothing in the API will tell you they aren't. |
| `budget.enforcement` | **`measured` — which enforces NOTHING** | This is the most dangerous default in the API. `measured`, `estimated` and `unavailable` record a number and never stop anything; only **`enforceable`** actually caps. If you want a real limit you must say so explicitly, every time. A run that blew through its budget still looks complete. |
| `topology_group` | unset | Groups worlds for cross-world topology. Sets up exactly the coupling `ISOLATED` exists to prevent. |
| `POST …/import` | do not use | Injects foreign artifacts into a world. The artifact's `origin` stops being `NATIVE`, and provenance now depends on a second world's history. |
| `retrospective` / `replication` on observations | `false` | These are claims about *when* and *why* an observation was made. `retrospective: true` permanently forfeits prospective status for that prediction. Setting either casually corrupts the epistemic record, which is the thing the ledger exists to protect. |
| `--insecure` on any client | never | Disables TLS verification. The battery refuses to proceed past S0 with it for this reason: an unverified session can be MITM'd and your bearer token captured. |

Safe to change: `name` (any world/session/experiment name), `budget.limit`
(a smaller number is always safe), `lease_s`, `worker_id`, `priority`, and the
contents of `spec` / `content` / `meta`.

---

## 8. What you are handing to Proteus and PEW

**Read this before promising anyone a pipeline. All three components exist and
run. The seam between them does not.**

### Proteus

- **Exists**, on `main`, under `proteus/` (24 modules + contracts). If you are on
  another branch you will not see it — several documents in this repo wrongly
  assert Proteus does not exist because their authors searched a working tree
  instead of `git ls-tree main`.
- **Is not a network client.** `proteus/contracts/SFE_INTEGRATION.md`: Proteus
  "holds no SFE token, opens no connection," and an import audit forbids network
  imports under `proteus/`. **You cannot hand Proteus a `world_id` and expect it
  to connect.** The operator moves data between them.
- **Never receives a world identity, by design.** `WORLD_INTERFACE.md`: a player
  receives raw integer channels per tick and nothing else — no world id, no tick
  number, no score, no budget, no strings. Proteus assigns no semantics to any
  channel. This is a firewall, not a preference; do not "helpfully" pass a
  world_id into a player.
- **Is NOT QUALIFIED.** Five successive crucibles (V0 → V0.6) returned
  NOT_QUALIFIED. `roles/Proteus/CONSUMER_SURFACE_V0_6.md` states it describes
  what a future consumer *would* find, "not an offer to be consumed."
  **Integration with Proteus is not currently authorized.**

**Known defect, measured live 2026-09-03.** `proteus/foundry/export.py`'s
`sfe_artifact_payload()` emits `{"name", "data_b64", "meta"}`. The live endpoint
requires `kind` and forbids extras, so this payload is rejected:

```
POST /v2/worlds/{wid}/artifacts   ->  HTTP 422
  missing        body.kind
  extra_forbidden body.name
```

Dropping `name` and supplying `kind` returns **200**. The fix belongs on the
Proteus side (or in an agreed `kind` vocabulary); it is one field either way.
Until it lands, no Proteus artifact can enter a world.

### PEW (Prometheus Evidence Wiki)

- **PEW is live**, and on a different footing from the Engine — note the
  contrast carefully, same host, different everything else:

  | | SFE Engine | PEW |
  |---|---|---|
  | URL | `https://192.168.1.202:8811/v2` | `http://192.168.1.202:8377` |
  | Transport | HTTPS, pinned cert `m1.crt` | **plain HTTP, no TLS** |
  | Auth | bearer token | none |

  From M1 the PEW service is at `localhost:8377`; from M2 set
  `EW_SERVICE_URL=http://192.168.1.202:8377`. Never query its database
  directly — the API is the contract.

- The Proteus→PEW *client* (`evidence_wiki/ew/client.py`) is on branch
  `mnemosyne/evidence-wiki-v0`, **not on `main`**, and the export contract says
  plainly it "has not been exercised against the service."
- The export is **one-way** (Proteus → PEW) and its rows are **identity-keyed,
  not world-keyed**: `proteus.organism`, `proteus.descent`, `proteus.signature`,
  `proteus.transcript_class`, each carrying a `provenance` block.
- **No parameter of `register_packet` / `register_experiment` / `submit_claim` /
  `submit_evidence` accepts a world identifier.** A conventional PEW claim or
  evidence row cannot carry an SFE `world_id`. (Only the separate V3 fossil
  tables have `world_id`/`sfe_world_id` columns, reached by a different
  endpoint.)
- Evidence additionally requires a **registered source packet plus a verbatim
  quote**; a derived view is refused as provenance. You cannot post an SFE
  result to PEW as evidence without first registering a packet file and quoting
  it.

So: the Engine gives you durable citation keys (`world_id`, `event_seq`,
`artifact_id`, `engine_source_hash`) — S8 verifies they are present and
well-formed — but **the ordinary PEW write path has nowhere to put a
`world_id` today.** If you need SFE provenance to survive into PEW, that field
has to be added first. Do not assume the link exists.

### Honest summary of the seam

| Link | Status |
|---|---|
| You → SFE Engine | **Working.** Verified live, in daily production use. |
| SFE → durable citation keys | **Working.** `world_id` + `event_seq` + `artifact_id` + build hash. |
| Proteus → SFE artifacts | **Broken** (422, measured) **and unauthorized** (NOT_QUALIFIED). |
| Proteus → PEW | **Specified, never exercised**; client not on `main`. |
| SFE → PEW | **Does not exist.** No world identifier on the ordinary PEW write path. |

### A caution about this repository

Seats develop on their own branches, and the working tree on M1 is usually
checked out on someone else's. **An "X does not exist" claim is only ever
branch-scoped until checked against `git ls-tree main`.** At least two
documents in this repo state that Proteus does not exist; both are wrong for
exactly this reason. When you record where a component lives, name the branch.

---

## 8a. What "known-good" does and does not mean here

Be precise about this, because the phrase is doing less work than it sounds
like it is.

The battery certifies that **this build, right now, does what this document
says it does** — 24/24 against `sha256:5274ddbe…` on 2026-09-03. That is a
health-and-contract check, and it is genuinely what you need to start.

It is **not** a qualification verdict. The only committed qualification result
in the repository is `genesis/harmonia_a/sfe_gen2/JOURNAL.jsonl`:
**`NOT_QUALIFIED`** (G1/G2/G3/G8 FAIL; defects DFX-1…4, DOC-1). Those defects
were subsequently fixed — the `DFX-` tags are visible throughout `sfe/api.py` —
and the current engine artifact `GEN2.1_RELEASE_PACKET.md` is marked
**`READY_FOR_REQUALIFICATION`**, which is explicitly a *candidate inviting
attack*, not a pass. **No superseding passing verdict is committed anywhere.**

So: use the Engine, build on it, run experiments. But do not cite it as a
qualified instrument in any scientific claim until a passing requalification is
committed. If you need that, say so — it is a piece of work, not a formality.

You are also not the first: `genesis/harmonia_a/sfe_gen2/FIRST_CONTACT_REPORT.md`
records a successful M2 onboarding on 2026-09-01 that ended with two open
questions to the maintainer (prediction-ordering semantics; whether budget
metering is cooperative-only). Rule 2 and the `enforcement` row in §7 above are
this document's answers to those two questions.

Also: `worldfoundry`'s `match_manifest` (wants `player_hashes`) and Proteus's
`encounter_identity()` (mints `encounter_id` from organism ids + world binding +
seed + checkpoints) are **two competing designs for the same object**, and the
Engine implements neither. Do not present them as one pipeline.

---

## 9. Troubleshooting

**`GET /v2/version` times out or refuses.** In order:
1. Are you on `192.168.1.0/24`? The Engine admits only that subnet.
2. `ping 192.168.1.202`.
3. Did you use the **IP**? A hostname fails TLS (IP SAN only).
4. Is `--cacert` pointing at a readable `m1.crt`?

**TLS error / certificate verify failed.** You used a hostname, or the wrong
cert path. The correct anchor is
`SerendipityFoundry/SerendipityFoundryClient/config/m1.crt`, fingerprint
`sha256:825153dd…`.

**401 unauthorized.** Missing or unknown token. Tokens are shown once at
registration; if you lost it, register again (or ask the operator to reissue
against your existing `client_id` — see `manage_client.py`).

**403 access denied.** You are touching another client's object. Worlds are
`ISOLATED` and bound to the client that created them. This is isolation working,
not a bug.

**422 with a field path.** Read the `loc` — it names the offending field. Most
common: a required field omitted, or an extra field sent (bodies are
`extra="forbid"`). `budget.enforcement` must be one of `enforceable`,
`measured`, `estimated`, `unavailable` — `"hard"` is not legal.

**`POST /v2/clients` returns 403.** Registration was closed after bootstrap.
Check `registration_open` in `GET /v2/version` and ask the operator for a token.

**Requests take seconds instead of milliseconds.** Normal is ~40–60 ms.
The Engine process runs with a very small thread count and is effectively
serial, so it degrades under heavy concurrent disk load on M1 rather than
under request load. It recovers on its own. If it persists, tell Daedalus —
do not restart the service yourself.

**Never restart the Engine to "fix" something.** It is a shared always-on
service with other users on it. See §10.

---

## 10. Operator notes (M1 only)

The Engine runs as the always-on scheduled task **`SFEngine`**, launched by
`deploy/sfengine.cmd`, bound to `192.168.1.202:8811`, logging to
`deploy/sfengine.log`.

**There are legitimately two `python.exe` processes.** The venv
`Scripts\python.exe` is a *launcher stub* that spawns the real interpreter
(`H:\Python312\python.exe`); the child owns the socket, the parent does not.
`Started server process [...]` appears in the log for the child only. **Killing
the parent kills or orphans the live server.** To restart, stop the whole
process tree via the scheduled task, never a single PID.

**Reachability is answered by the access log, not by a socket snapshot.**
`Get-NetTCPConnection` shows only sockets alive at that instant, and a short
HTTPS request is closed before you look — it will report "no remote clients"
on a service handling thousands of requests. Use:

```powershell
Select-String "192\.168\.1\.191" deploy\sfengine.log | Measure-Object
```

**Known residual (not fixed here):** there is no singleton guard — no lockfile
or pidfile — and uvicorn sets `SO_REUSEADDR`, which on Windows permits binding
an address already in use. A stray manual `python serve.py` would bind
alongside the service and split traffic rather than failing loudly. Worth a
`var/engine.lock` exclusive-open guard in `serve.py` before `uvicorn.run`.

**Open registration** means any host on `192.168.1.0/24` can mint an identity.
That is intentional for bootstrap; close it with `serve.py --registration
closed` when the fleet is stable.
