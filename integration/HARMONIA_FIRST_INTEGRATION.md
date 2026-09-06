# SFE / World Server — First Integration

**Audience:** the first experimentalist (Harmonia, M2) and anyone integrating
against the Serendipity Foundry Engine for the first time.
**Maintainer:** Daedalus (M1 / SKULLPORT).
**Written:** 2026-09-03. **Re-verified 2026-09-04** against the restarted
build `sha256:6a4f3aee…` (strict artifact decoding). Every claim below was
checked against the running service on that date.

This document is meant to be sufficient on its own. If you have to ask Daedalus
how something works, that is a defect in this file — say so.

> **Since 2026-09-04 there are two engines.** Everything below describes M1's,
> which is still the primary and still holds all existing work. A second,
> independent engine now runs on **M2 / SPECTREX5** at
> `https://192.168.1.191:8811`, trust anchor
> `SerendipityFoundryClient/config/m2.crt` — its own empty database, its own
> tokens, nothing shared with M1's. To run this document's battery against it:
>
>     python integration/sfe_battery.py --base https://192.168.1.191:8811/v2 \
>         --cacert SerendipityFoundry/SerendipityFoundryClient/config/m2.crt
>
> Keep the `/v2` suffix: `--base` is the API root, not the host, and dropping it
> fails S0 with a 404. Verified 23/23 against M2 on 2026-09-04. Omitting both
> flags tests M1, which will pass and tell you nothing about M2. `--out` writes
> a handoff file **containing a bearer token** — put it somewhere deliberate.
> Differences, restart discipline, and wind-down:
> `SerendipityFoundry/SerendipityFoundryEngine/docs/RUNNING_M1_VS_M2.md`.
> The Evidence Wiki is a different story — it is deliberately *not* forked; M2's
> PEW at `http://192.168.1.191:8377` serves M1's one canonical database.

---

> **Testing M1 right now?** `integration/M1_TEST_SURFACE_FOR_HARMONIA.md`
> is the current M1-only test surface: what already passes, the three things
> same-host testing cannot prove, and eight proposed test cases. M2 is down;
> that document assumes it stays down.

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

**On Windows, set this first** — otherwise the clone fails partway:

```bash
git config --global core.longpaths true
```

```bash
git clone https://github.com/jcraig949jfi/Prometheus.git
cd Prometheus
git checkout main
```

**If you skipped the `core.longpaths` line, your clone is not broken — but it
will look like it is.** Without it, `git clone` on Windows emits a run of
`error: unable to create file …: Filename too long` and `git status` then
reports tens of thousands of files as deleted. The offending paths are in other
roles' directories (`charon/`, `ergon/`), not in anything you need: `integration/`
and the certificate check out fine, and the battery passes. Verified 2026-09-03
— a fresh clone that reported 36,602 missing files still ran 23/23. Set the
config and re-clone to get a clean tree.

The Engine's certificate is **committed** at
`SerendipityFoundry/SerendipityFoundryClient/config/m1.crt`. There is no manual
copy step and nothing to request from Daedalus. (The private key `m1.key` is
gitignored and lives only on M1 — you never need it.)

### 2. Prove you can reach the Engine

```bash
curl --cacert SerendipityFoundry/SerendipityFoundryClient/config/m1.crt \
     https://192.168.1.202:8811/v2/version
```

Expected — an `api` of `v2` and a `schema_version` of **4** or higher:

```json
{"api":"v2","schema_version":4,"runtime":"serendipity-foundry-sfe",
 "registration_open":true,
 "engine_source_hash":"sha256:6a4f3aeec05a3ed9a31364e21f55cd11dc511f8f1d9789b2bcc37ce98f8447cf",
 "source_commit":"e6146376843da06d7e14366cc5e8c89a006b7cb3"}
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
Verified 24/24 on 2026-09-05 against build `sha256:6a4f3aee…`.

To pin the exact build you expect (recommended once you are past first contact):

```bash
python integration/sfe_battery.py \
    --cacert SerendipityFoundry/SerendipityFoundryClient/config/m1.crt \
    --expect-source-hash sha256:6a4f3aeec05a3ed9a31364e21f55cd11dc511f8f1d9789b2bcc37ce98f8447cf
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
| **S1** | Engine identity **asserted**: `api=v2`, `schema_version ≥ 3`, runtime name (live is 4) | A green battery must tell you *which* instrument answered, not merely that something did |
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

## 5. Frozen reference identity (as of 2026-09-05)

| | |
|---|---|
| API title / version | `Serendipity Foundry Gen-2` / `2.2.0` |
| `schema_version` | `4` |
| Paths / routes | 34 paths, 38 routes |
| Route-surface digest | `sha256:461b1dc5f9d9a0a36e85ad6f83e2cea0d3ef7ac86fda48bfae1ad7e953921cad` |
| `engine_source_hash` | `sha256:6a4f3aeec05a3ed9a31364e21f55cd11dc511f8f1d9789b2bcc37ce98f8447cf` |
| `source_commit` | `e6146376843da06d7e14366cc5e8c89a006b7cb3` on M1, `0fd24e0f3…` on M2 — **best-effort git metadata: the HEAD of the checked-out working tree (currently another role's branch), NOT the commit that contains the engine code.** `engine_source_hash` is the authoritative identity. |
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
**Authorization state — corrected 2026-09-03 by external adjudication.** Read
this carefully; the two halves differ:

> **Frozen Proteus specimens are authorized for integration.
> Proteus breeding/mutation is not qualified for evolutionary claims.**

| | |
|---|---|
| **USE A — AUTHORIZED** | Frozen, semantics-free specimens may be enumerated, fetched, validated, instantiated, ticked, checkpointed, restored, replayed, and **supplied to worlds**. |
| **USE B — NOT QUALIFIED** | The mutation machinery remains `NOT_QUALIFIED_AUTHORED_NONEQUILIBRIUM_CURRENT`. Operational significance is `NOT_YET_ADJUDICATED`. **Campaign 1 remains BLOCKED.** |

In practice: you may take an existing frozen specimen and run it in a world.
You may **not** breed specimens and make evolutionary claims from the results.
If a question requires the mutation operator to be sound, it is out of scope.

### The historical Proteus payload is NOT the seam — and is deliberately not being fixed

`proteus/foundry/export.py`'s `sfe_artifact_payload()` emits
`{"name", "data_b64", "meta"}`. Measured live against the endpoint:

```
POST /v2/worlds/{wid}/artifacts   ->  HTTP 422
  missing         body.kind
  extra_forbidden body.name
```

**Do not import that helper, and do not wait for it to be repaired.** It stays
as it is: Proteus's foundry tree remains bound to its V0.6 audit identity, and
reshaping it to fit SFE would drag world semantics into organism identity —
exactly the coupling this boundary exists to prevent.

That 422 is frozen as a regression fixture (`integration/seam_fixture.py`, §11).
It is a **boundary marker, not a bug report**.

### Who owns what

| Owner | Owns |
|---|---|
| **Proteus** | organism identity, manifests, intrinsic provenance, the player ABI |
| **SFE** | world lifecycle, artifacts, events, the work queue, engine-attested observations |
| **Harmonia** | **the binding between them** |

### PEW (Prometheus Evidence Wiki)

- **PEW is live**, and on a different footing from the Engine — note the
  contrast carefully, same host, different everything else:

  | | SFE Engine | PEW |
  |---|---|---|
  | URL | `https://192.168.1.202:8811/v2` | `http://192.168.1.202:8377` |
  | Transport | HTTPS, pinned cert `m1.crt` | **plain HTTP, no TLS** |
  | Auth | bearer token | bearer token (a **different** one — an SFE `gen2_` token is not a PEW credential) |
  | Identity | `Serendipity Foundry Gen-2` 2.2.0 | `Mnemosyne Evidence Wiki` 0.1, 37 paths |

  From M1 the PEW service is at `localhost:8377`; from M2 set
  `EW_SERVICE_URL=http://192.168.1.202:8377`. Never query its database
  directly — the API is the contract.

**PEW has TWO write surfaces, and the difference is the whole story.**

*Verified 2026-09-03 by reading the live `GET /api/v1/openapi.json` and
`GET /api/v1/fossil/contract`.*

**(a) The ordinary evidence path — carries NO world identity.**

| Endpoint | Required fields | Any world field? |
|---|---|---|
| `POST /api/v1/packets` | `uri`, `kind` | **none** |
| `POST /api/v1/experiments` | `agent`, `project`, `title` | **none** |
| `POST /api/v1/claims` | `text_canonical`, `status` | **none** |
| `POST /api/v1/evidence` | `packet_id`, `source_quote`, `evidence_type` | **none** |
| `POST /api/v1/relations` | `src_type`,`src_id`,`relation_type`,`dst_type`,`dst_id`,`epistemic_class`,`creation_method` | **none** (but the type fields are unconstrained strings) |

Evidence also requires a **registered source packet plus a verbatim quote**;
a derived view is refused as provenance. You cannot post an SFE result as
evidence without first registering a packet file and quoting it.

**(b) The fossil path — carries the SFE chain in full, and already exists.**

`GET /api/v1/fossil/contract` returns `pew.fossil.v1`, `schema_version 3`,
`extra=forbid`, with this identifier mapping — quoted verbatim from the live
service:

```
world_id       ->  SFE world_id
players[]      ->  Proteus organism_id (a player IS its manifest)
encounter_id   ->  Proteus encounter_identity() -- the SPECIFICATION
run_id         ->  the EXECUTION: SFE 'exp_id:work_id'
seed           ->  encounter seed (SFE world-level seed_root is on the world row)
sfe_event_seq  ->  SFE ledger order; PEW revision is NOT producer order
```

`FossilEncounterIn` accepts `sfe_world_id`, `sfe_event_id`, `sfe_event_seq`,
`sfe_entry_hash` (**required**), `world_id`, `players`, `run_id`, `outcome`,
`seed`, `budget`. `FossilWorldIn` accepts `sfe_world_id`, `sfe_head_hash`,
`seed_root`, `world_binding_id`, `parent_world`. `FossilPlayerIn` accepts
`sfe_world_id`, `sfe_entry_hash`, `genome_hash`, `runtime_hash`, `lineage_id`.

**So the SFE→PEW provenance surface is NOT missing — it is built, versioned,
and it already anticipates both SFE and Proteus identifiers.** An earlier
version of this document said PEW "has nowhere to put a `world_id`." That was
wrong; it was written from the ordinary path alone. Corrected here.

What is genuinely still open is narrower, and it is stated precisely in §8b.

### Honest summary of the seam

| Link | Status |
|---|---|
| You → SFE Engine | **Working.** Verified live, in daily production use. |
| SFE → durable citation keys | **Working.** `world_id` + `event_seq` + `artifact_id` + build hash. |
| Proteus specimens → SFE artifacts | **Authorized, and the SFE side is open** — but **the adapter does not exist yet**. It is Harmonia's to build (§9). |
| Proteus *breeding* → evolutionary claims | **NOT QUALIFIED.** Use B is blocked; Campaign 1 remains blocked. |
| Proteus → PEW | **Specified, never exercised**; the `ew` client is on branch `mnemosyne/evidence-wiki-v0`, not `main`. |
| SFE → PEW **fossil** surface | **Built and ready** (`pew.fossil.v1`), with SFE and Proteus identifiers already mapped. No producer is known to write to it yet. |
| SFE → PEW **claim/evidence** surface | **Open seam.** A scientific claim still cannot carry world provenance directly. See §8b. |

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
says it does** — 24/24 against `sha256:6a4f3aee…` on 2026-09-03. That is a
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

## 8b. The SFE → PEW world-provenance seam — filed for Mnemosyne

**Owner: Mnemosyne / PEW. Not Harmonia's to solve, and not SFE's.** It is
recorded here so you know exactly where the chain currently stops.

**Filed as: `PEW_WORLD_PROVENANCE_SEAM_BUILT_BUT_UNBOUND`.**

That label is a deliberate correction. This seam was previously going to be
filed as `..._UNIMPLEMENTED`, on my earlier finding that PEW had nowhere to put
a `world_id`. Reading the live service disproved that: `pew.fossil.v1` is built,
versioned, and already maps SFE and Proteus identifiers (§8). Filing it as
unimplemented would have sent Mnemosyne to build something that exists.

**What was inspected** (live, 2026-09-03, read-only):
`GET /api/v1/openapi.json` (37 paths), `GET /api/v1/fossil/contract`,
`GET /api/v1/schema`, `GET /api/v1/version`.

**What is actually missing — three specific things:**

1. **The claim/evidence path cannot carry world provenance — and fails OPEN, not
   closed.** `ClaimIn` and `EvidenceIn` have no world field of any kind (full
   field lists in §8). Worse: the five ordinary-path models
   (`PacketIn`, `ExperimentIn`, `ClaimIn`, `EvidenceIn`, `RelationIn`) declare
   **no** `model_config`, so Pydantic's default `extra="ignore"` applies —
   whereas all four fossil models **do** declare `extra="forbid"`. Verified by
   reading the model definitions in `evidence_wiki/ew/service.py` (lines 227,
   351, 185, 246, 296 vs 913, 929, 634).

   **Consequence: a producer who adds `world_id` to an evidence POST gets HTTP
   200 and the field is silently discarded.** No 422, no warning. Provenance
   does not fail to attach loudly — it disappears quietly, which is the harder
   failure to notice and the one most likely to be discovered months later in a
   result nobody can trace. This is the single most actionable item in this
   filing.

   **Stated precisely, because the loose version of this claim is false.** The
   ordinary path has no **typed, queryable, or joinable** world identity. It is
   *not* true that a world identifier cannot physically reach PEW: a world URL
   can legally ride as an opaque string in `source_packets.uri` — hashing is
   conditional (`sha = None; p = REPO / uri; if p.is_file(): …`,
   `store.py:84-88`), the schema documents `uri` as "repo-relative path or
   external URI" with `content_sha256` "null if unhashable", and an SFE URL is
   **not** caught by `DERIVED_URI_MARKERS = ("evidence_wiki/derived", "/wiki/",
   "/api/v1/")` (`store.py:63`) — those markers quarantine PEW's *own* URL
   space, not SFE's.

   That route is not proposed here, and the directive governing this pass
   forbids inventing it: it would be world identity encoded in free text, one
   opaque string per packet, with no join key, no type, and **no read endpoint**
   — there is no `GET /api/v1/packets` at all. It is recorded so the filing is
   accurate about what is and is not possible, and so Mnemosyne can rule on it
   rather than discover it.

2. **No documented convention binds an evidence row to a fossil row.**
   `RelationIn` could express it — `src_type`/`dst_type` are unconstrained
   strings and the spec already contains the tokens `fossil_encounter`,
   `fossil_world`, `fossil_player` — but no contract states which
   `relation_type`, `epistemic_class` or type names to use. Until that
   convention is written down, two producers will invent two different ones and
   the graph will not join.

3. **No producer is known to write fossil rows.** The read endpoints require a
   PEW bearer token, which I do not hold and did not seek, so I cannot state
   whether the tables contain anything. **This is unverified, not verified
   empty.**

4. **The branch topology is worse than "the client isn't on main."**
   `evidence_wiki/` does not exist on `main` or `origin/main` **at all** (0
   files). It lives on `mnemosyne/evidence-wiki-v0` and on
   `herakles/historical-collider-v0` (275 files) — and the Herakles branch is
   *ahead*, carrying `migrations/006_first_integration.sql` and
   `integration/pew_battery.py`. **The world-carrying fossil work is therefore
   not on the branch peers are told to pull.** Whoever owns PEW should decide
   which branch is canonical before anyone builds against it.

**Why the chain breaks today.** Hold a complete SFE result —
`world_id`, `event_seq`, `artifact_id`/`blob_hash`, `engine_source_hash` — and
try to land it as PEW evidence:

```
world_id           -> no home on EvidenceIn/ClaimIn.  Has a home on the fossil
                      surface (sfe_world_id), which is not the evidence path.
event_seq          -> same: fossil only (sfe_event_seq).
artifact_id        -> no field on either surface. Nearest is sfe_entry_hash,
                      which the fossil contract REQUIRES but does not define as
                      the SFE artifact_id.
engine_source_hash -> no home anywhere. PEW records git_commit for a packet,
                      which identifies the ANALYSIS, not the ENGINE BUILD that
                      produced the result.
```

Evidence additionally demands a registered packet and a verbatim quote, and
refuses a derived view as provenance — so the world→event→artifact→evidence
chain currently terminates at a prose packet, with the machine-readable world
identity parked on a separate surface that nothing links to it.

**Per the directive, nothing was worked around:** no PEW fields added, no side
channel invented, no `world_id` smuggled into free text, no citation key
overloaded, no provenance requirement weakened.

**The concrete minimum change requested** — so this is a filing and not just a
diagnosis. Any one of these would close it; the choice is Mnemosyne's:

- add `sfe_world_id` / `sfe_entry_hash` columns plus model fields to
  `ew.evidence`, so provenance is typed and joinable on the ordinary path; **or**
- expose a write path for the already-existing `ew.interpretations` table,
  which no route currently reaches; **or**
- sanction and document an explicit relation type binding an evidence row to a
  `fossil_encounter`, making `RelationIn` the official join.

Whichever is chosen, **add `extra="forbid"` to the five ordinary-path models.**
That is a two-line change and it converts the silent-drop above into a 422. It
is worth doing on its own merits even if the seam is closed some other way.

**Three questions only PEW can answer:**

1. Is `sfe_entry_hash` intended to be the SFE `artifact_id`, the `blob_hash`, or
   the world `head_hash`? The fossil contract **requires** it and never defines
   it; three producers will guess three different things.
2. What is the sanctioned relation binding an evidence row to a
   `fossil_encounter`?
3. **Is migration `006_first_integration.sql` applied to the live database?**
   This is unverified and it gates the fix: if 006 is unapplied, the fossil
   tables this filing points to as the real home may not yet have `run_id`,
   `episode_id` or `sfe_event_seq`. `GET /api/v1/health` reports a schema
   version; nobody has checked it against the applied migrations.

---

## 9. The first adapter is yours

**THERE IS STILL NO WORLD ADAPTER.**

**THE FIRST PROTEUS → SFE ADAPTER BELONGS TO HARMONIA'S INTEGRATION LAYER.**

Nothing in Proteus and nothing in SFE will grow one on its own, and neither
should: Proteus must not learn about worlds, and SFE must not learn about
organisms. The binding is a third thing, and it is yours.

```
PROTEUS
  |
  | frozen specimen + manifest + qualification provenance
  v
HARMONIA ADAPTER                  <-- DOES NOT EXIST YET
  |
  | valid SFE artifact contract  (§10)
  v
SFE WORLD
  |
  | world_id / event_seq / artifact_id / build identity
  v
HARMONIA EXECUTION
  |
  | observations / outcomes / checkpoints
  v
SFE EVIDENCE SURFACE
  |
  X
PEW / MNEMOSYNE                   <-- WORLD-PROVENANCE SEAM STILL OPEN (§8)
```

Its whole job is transport:

```
Proteus registry entry  +  immutable player manifest  +  Proteus provenance
                              |
                              v
                    Harmonia transport binding
                              |
                              v
                     valid SFE artifact request
                              |
                              v
                       SFE world artifact
```

### The Proteus side already exists — bind to this, not to `foundry/export.py`

`proteus/integration/` on `main` is the consumer surface (deliberately outside
`proteus/foundry/`, which stays pinned to its V0.6 audit identity):

| | |
|---|---|
| `proteus/integration/registry.py` | the API below |
| `proteus/integration/PLAYER_REGISTRY.json` | **64 frozen specimens**, selection rule: *"NONE beyond manifest validity"* |
| `proteus/contracts/player_registry.schema.v1.json` | the schema |
| `roles/Proteus/HARMONIA_HANDOFF.md` | Proteus's own note to you |

> **Provenance note.** The pointer back to *this* document, in
> `HARMONIA_HANDOFF.md` §10, was added by **Daedalus** (commit `01a6765be`),
> not by Proteus. It is additive and changes no Proteus contract, but it is an
> edit to another seat's file and Proteus should feel free to revert or reword
> it. I attempted to notify that seat directly; **the message expired
> undelivered**, so this note and the commit message are the standing record.

**Three traps on the Proteus side, all verified 2026-09-03. Each one will tell
you the registry does not exist.**

1. **A committed document denies it in bold.**
   `roles/Proteus/CONSUMER_SURFACE_V0_6.md` says: *"**NO. It does not exist.**
   There is no registry file, no dictionary, no catalog, and no enumeration
   endpoint anywhere in `proteus/`."* That was true when written and became
   false about seven hours later, when the registry was built. **It was never
   amended and still sits beside the registry.** Anyone grepping
   `roles/Proteus/` for "registry" hits the denial first. Treat that section as
   superseded; `HARMONIA_HANDOFF.md` is the current word.

2. **Local `main` is stale — use `origin/main`.** At time of writing the local
   `main` ref is **22 commits behind** `origin/main`, and
   `git ls-tree -r main -- proteus/integration/` returns **zero files**. The
   usual "check it against `main`" rule produces a confident false negative for
   the entire consumer surface. `git fetch` first, and check `origin/main`.

3. **The import quarantine does not cover the package you bind to.**
   `SFE_INTEGRATION.md` says the audit "forbids any network import in
   `proteus/`". It does not: `quarantine.py:31` sets
   `FOUNDRY = proteus/foundry` and `audit_identity.py:26` sets
   `COVERED_DIRS = (proteus/foundry,)`. **`proteus/integration/` — the exact
   package a Harmonia adapter imports — is outside the audit's scope.** The
   property still holds in fact (it imports only stdlib plus Proteus siblings),
   but it is enforced by nobody. Do not rely on the audit to keep your adapter's
   dependency honest; that is now your discipline, not a mechanical guarantee.

One naming detail that will bite an adapter asserting on strings: the registry
uses the **bare** values `NOT_YET_ADJUDICATED` and
`FULL_SPACE_CURRENT_SOURCE_UNRESOLVED`, while the review packets use prefixed
tokens like `OPERATIONAL_SIGNIFICANCE_NOT_YET_ADJUDICATED`. Assert on the
registry form.

```python
from proteus.integration import registry

reg   = registry.load_default()                     # the frozen inventory
ids   = registry.enumerate_ids(reg)                 # -> [organism_id, ...]  (64)
entry = registry.get_entry(reg, ids[0])
man   = registry.get_manifest(reg, ids[0])          # the immutable player manifest
env   = registry.get_resource_envelope(reg, ids[0]) # bounds a scheduler needs
qual  = registry.source_qualification()             # travels with every registry
```

A registry entry carries exactly:
`entry_id`, `organism_id`, `lineage_id`, `generation`, `identity`
(`runtime_hash`, `grammar_hash`, `affordance_hash`, versions), `manifest`
(the genome), `provenance`, `resource_envelope`, `validation`, and `extrinsic`.

**`source_qualification()` is the Use A / Use B statement in machine-readable
form**, so you never need to read the V0.6 archaeology to know the limit:

```
permitted_use          : USE_A_FROZEN_SPECIMEN_SOURCE
prohibited_use         : USE_B_NEUTRAL_EVOLUTIONARY_OPERATOR
mutation_neutrality    : NOT_QUALIFIED_AUTHORED_NONEQUILIBRIUM_CURRENT
operational_significance : NOT_YET_ADJUDICATED
```

Carry that block into whatever you record. It is the difference between a
defensible result and an overclaim.

### The `extrinsic` block is yours — and it is the whole intrinsic/extrinsic rule in one field

Every entry has:

```json
"extrinsic": {
  "phenotype": "UNKNOWN",
  "owner": "not Proteus; Harmonia/Mnemosyne may attach observations here",
  "note": "UNKNOWN is a permanent, legitimate state. It records that no
           observation has been made, and must not be read as a negative
           judgement. Nothing written into this object changes organism_id
           or entry_id."
}
```

`entry_id` is computed over the **intrinsic part only**, and Proteus has a test
asserting exactly that — so an extrinsic observation cannot alter identity even
if a consumer writes one in. This is the mechanical guarantee behind "world
association is EXTRINSIC." Respect it: world behaviour, encounters, phenotype,
scores, failures and novelty are yours to record; none of them may flow back
into identity.

`phenotype` is `"UNKNOWN"` on all 64 specimens because nothing has been
observed yet. **That is the point of the first integration** — not a gap to be
filled in before you start.

### Minimal adapter sketch

```python
import base64, json
from proteus.integration import registry

reg = registry.load_default()
qual = registry.source_qualification()

for oid in registry.enumerate_ids(reg):
    man = registry.get_manifest(reg, oid)
    entry = registry.get_entry(reg, oid)

    body = json.dumps(man, sort_keys=True, separators=(",", ":")).encode()
    req = {
        "kind": "artifact",                                   # SFE's field (§10)
        "data_b64": base64.b64encode(body).decode(),          # STANDARD base64
        "meta": {
            "info_kind": "artifact",
            "proteus": {
                "organism_id": oid,
                "entry_id":    entry["entry_id"],
                "lineage_id":  entry["lineage_id"],
                "generation":  entry["generation"],
                "identity":    entry["identity"],
                "source_qualification": qual,                 # travels with it
            },
        },
    }
    # POST to /v2/worlds/{world_id}/artifacts; record blob_hash <-> organism_id
```

Note what this does **not** do: no `name` field, no classification, no
phenotype, no score, no mutation, and no world id written back into Proteus.

### The seam has a free integrity check — use it

**`organism_id` IS the SHA-256 of the canonical manifest.** Verified against all
64 specimens in the registry: `sha256(json.dumps(manifest, sort_keys=True,
separators=(",", ":")))` equals `organism_id`, 64/64.

So if you post exactly that canonical serialization as the artifact bytes, the
Engine's content address and Proteus's identity are the same number:

```python
assert resp["blob_hash"] == "sha256:" + organism_id
```

**That one line catches nearly everything that can go wrong in transport** — a
re-serialized manifest, a different key order, an added field, and (most
importantly) the URL-safe base64 corruption in §10, which would otherwise pass
silently with HTTP 200. If the assertion holds, the specimen crossed unaltered.
No mapping table is required in either direction.

Verified end to end on 2026-09-03 with real specimen
`7743b3527ea44fb5…` posted into two live worlds:

```
blob_hash == sha256(canonical manifest)   -> True
blob_hash identical across the two worlds -> True    (intrinsic identity)
artifact_id DIFFERS across the two worlds -> True    (extrinsic binding)
```

That is the extrinsic-association rule, demonstrated rather than asserted.
Note `organism_id == lineage_id` at generation 0, while `entry_id` is a
different hash (computed over the whole intrinsic bundle, not the manifest
alone) — do not use them interchangeably.

**The adapter must NOT:**

- classify the player
- phenotype the player
- score it
- mutate it
- rewrite organism identity
- claim the mutation source is neutral
- add world semantics to Proteus identity

**World association is EXTRINSIC.** The same `organism_id` must be able to enter
many different worlds without its intrinsic identity changing. The Engine
already supports this and it is verified: posting identical specimen bytes into
two different worlds yields **the same `blob_hash`** and **different
`artifact_id`s** (§10). The content identity is invariant; the world binding is
derived. Keep it that way — if you find yourself writing a world id into a
manifest, stop.

---

## 10. FROZEN CONTRACT — `POST /v2/worlds/{world_id}/artifacts`

Everything here was measured against the live Engine on 2026-09-03 (build
`sha256:6a4f3aee…`). It is sufficient to construct a request with no other
reference and no Proteus import.

**Single source of truth:** the Engine's own request model,
`SerendipityFoundryEngine/sfe/api.py` → `class ArtifactCreate(_Body)`, published
at `GET /v2/openapi.json` under `components.schemas.ArtifactCreate`. This
section describes that model; **it does not replace it.** If the two ever
disagree, the Engine is right and this section is stale.

### Request

```http
POST /v2/worlds/{world_id}/artifacts
Authorization: Bearer gen2_...
Content-Type: application/json

{
  "kind":     "artifact",        // REQUIRED, string
  "data_b64": "<standard base64>", // REQUIRED, string
  "meta":     { }                // optional, object, default {}
}
```

| Field | Req | Type | Notes |
|---|---|---|---|
| `kind` | **yes** | string | **NOT validated against any vocabulary at this endpoint.** Any string is accepted, including `""`. Measured: `artifact`, `success`, `failure`, `hypothesis`, `observation`, `totally-made-up-kind`, `""` → all HTTP 200. |
| `data_b64` | **yes** | string | Standard base64. See the encoding warning below — this is the one that will silently hurt you. |
| `meta` | no | object | Free-form. Carry organism identity and Proteus provenance here. |

**`Content-Type: application/json` is REQUIRED.** Omit it, or send
`text/plain`, and you get a **422** — `model_attributes_type`, *"Input should be
a valid dictionary or object"* — because the body is never parsed as JSON at
all. Verified both ways. This comes from FastAPI 0.141.1's strict content-type
default, not from SFE, and older FastAPI builds were lenient here, so this
surprises people who have used the API before.

**Closed model — but ONE LEVEL ONLY.** Any unknown *top-level* field is a
**422** (`extra_forbidden`), inherited from `_Body`'s
`model_config = ConfigDict(extra="forbid")` — "scientific requests fail closed."
That is why the historical Proteus payload's `name` is rejected. **`meta` is
NOT closed**: arbitrary nested keys are accepted (verified, 200). Put whatever
you need in `meta`.

**`kind` vs `meta.info_kind` — the highest-probability mistake in this
handoff.** They are different fields at different nesting levels with opposite
validation:

| | Validated? | Verified |
|---|---|---|
| top-level `kind` | **No.** Any string, including `""` | `artifact`, `success`, `totally-made-up-kind`, `""` → all 200 |
| `meta.info_kind` | **Yes — closed set** `{artifact, failure, hypothesis, observation, success}` | `bogus-info-kind` → **422** `"unknown info_kind"` |

So the closed ontology governs the **nested** field, and it is `meta.info_kind`
that the cross-world sharing machinery reads. **If you omit `info_kind`, no
sharing policy will ever match that artifact** — which is the right default for
an `ISOLATED` world, but is a silent no-op rather than an error if you later
expect sharing. Set both, deliberately, and keep them consistent.

**Idempotency-Key gotcha.** The optional `Idempotency-Key` header is scoped to
`(client_id, key)`, and the stored request hash covers the **raw `data_b64`
string**, not the decoded bytes. Two different base64 spellings of identical
bytes under the same key are a **409 conflict**, even though they would mint the
same artifact. On retry, resend byte-identical text.

### Response

```json
{ "artifact_id": "sha256:…", "blob_hash": "sha256:…", "origin": "NATIVE" }
```

### Identity — measured, and the part that matters for extrinsic world association

| | |
|---|---|
| `blob_hash` | **Exactly `sha256(raw bytes)`.** World-independent. Verified: equals the locally computed digest of the posted bytes. |
| `artifact_id` | **World-scoped.** Content-addressed over an *envelope*, not the bytes alone. |

Derivation, `sfe/runtime.py:1091-1094`:

```python
blob = self.store.put_blob(data)
aid  = content_hash({"world": world_id, "kind": kind, "blob": blob,
                     "meta": meta or {}})
```

Measured behaviour:

| Repost | Same `artifact_id`? | Same `blob_hash`? |
|---|---|---|
| identical bytes, same world, same kind+meta | **yes** (idempotent — no duplicate) | yes |
| identical bytes, **different world** | **no** | **yes** |
| identical bytes, different `meta` | no | yes |
| identical bytes, different `kind` | no | yes |

**Use `blob_hash` to prove "the same specimen entered these N worlds."** Use
`artifact_id` as the world-scoped citation key. This is exactly what makes world
association extrinsic rather than intrinsic.

### Byte preservation

Bytes are stored and returned **byte-identical**. Verified by round-trip via
`GET /v2/worlds/{wid}/artifacts/{aid}/content` → `content_b64`, and again in the
seam fixture (§11). No normalization, no re-encoding.

### Encoding — READ THIS ONE

- **Use STANDARD base64 (`+` and `/`), with padding.**
- **URL-safe base64 (`-` and `_`) is REJECTED with a 422** naming
  `body.data_b64`. Decoding is strict as of build `c358a53b` (superseded by `6a4f3aee`).
- **Invalid base64 is also a 422**, not a 500.

In Python: `base64.b64encode(...)`. **Never** `base64.urlsafe_b64encode(...)`.

*Fixed 2026-09-04.* On builds up to and including `5274ddbe` this endpoint
failed **open**: URL-safe base64 was accepted with HTTP 200 and **silently
stored different, shorter bytes** (measured 24 in, 15 stored), and malformed
base64 escaped as an opaque 500. If you hold artifacts written before that
date, verify them — `blob_hash` must equal your own `sha256(bytes)`. Nothing a
standard-base64 client sends is affected, then or now.

### Bounds

**No size limit exists in the code path, and none was reached.** Confirmed
absent at every layer — no pydantic constraint, no FastAPI/Starlette body cap,
no uvicorn limit, no blob-store check, no budget interaction. Measured accepted:
1 KB, 64 KB, 1 MB, 8 MB, and **32 MB** (a 44 MB base64 body) in 0.94 s.

Two reasons to impose your own cap anyway:

- The request path **re-serializes and hashes the full `data_b64` string on
  every request** (idempotency `_req_hash`), giving roughly 4–5× memory
  amplification over the raw payload.
- The Engine is a single, effectively serial process, and the same box also
  hosts PEW on 8377.

So: any number you adopt is a **self-imposed client-side courtesy cap, not a
server-enforced limit.** The Engine will not stop you.

### Lifecycle: terminating a world DOES seal it (changed 2026-09-04)

**This reversed on 2026-09-04.** Terminal-state writes are now gated. Measured
on the live parity build after `POST …/terminate` (state `TERMINATED`):

| Operation on a terminated world | Result |
|---|---|
| `POST …/artifacts` | **409** |
| `POST …/hypotheses` | **409** |
| `POST …/budget/consume` | **409** |
| `POST …/experiments` (commit) | **409** `invalid_transition` |
| `GET …/events`, `GET …/status` | 200 — reads stay open |
| `POST …/checkpoint`, `POST …/fork` | 200 — post-run finalisation stays open |

So termination now *does* seal the write surface while leaving the record
readable and forkable. **If you have code written against the old behaviour it
will start getting 409s** — that is the intended failure, not a regression.

Pre-existing data still reflects the old rule: artifacts written into terminated
worlds before this change remain, and their `created_seq` can postdate
`WORLD_TERMINATED`. Do not infer a world's active window from its terminate
event for historical records (see `integration/SFE_ARCHAEOLOGY_SCHEMA.md`).

### Authorization — measured

| Caller | Result |
|---|---|
| owner of the world | `200` |
| authenticated **non-owner**, post | `403 access_denied` "world is not owned by this client" |
| authenticated **non-owner**, read content | `403 access_denied` |
| no `Authorization` header | `401` "bearer token required" |
| unknown token | `401` "unknown token" |
| owner, non-existent world | `404 not_found` "unknown world" |

### The identifier chain a consumer needs

```
world_id            you supply it in the path; it scopes everything
   |
   +-- artifact_id  returned; world-scoped; the citation key
   +-- blob_hash    returned; = sha256(bytes); world-INDEPENDENT specimen identity
   |
event_seq           assigned in the world's ledger; read via GET .../events
   |
engine_source_hash  which build accepted it; on every response as
                    x-sfe-engine-source-hash, and in GET /v2/version
```

Record all four with anything you intend to keep. `event_seq` and `world_id`
are what order and locate the act; `blob_hash` is what identifies the specimen
across worlds; `engine_source_hash` is what makes it attributable to a build.

---

## 11. The seam regression fixture

```bash
python integration/seam_fixture.py \
    --cacert SerendipityFoundry/SerendipityFoundryClient/config/m1.crt
```

Three assertions, and **both directions matter**:

| | |
|---|---|
| **F1** | The historical Proteus payload (`name`, no `kind`) **MUST fail closed with 422**, naming both faults. |
| **F2** | A Harmonia-shaped payload satisfying §10 **MUST succeed with 200**. |
| **F3** | Bytes round-trip exactly and `organism_id` in `meta` is unchanged — world association stayed extrinsic. |

**If F1 ever starts passing, that is a regression in the Engine, not progress.**
It would mean the artifact endpoint stopped failing closed on unknown fields.
The fixture exists to make that loud.

Last run 2026-09-03: **F1 PASS, F2 PASS, F3 PASS** — boundary intact.

---

## 12. Troubleshooting

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

**422 `data_b64 is not valid standard base64` on the artifact endpoint.** Your
encoder emitted URL-safe base64 (`-`/`_`) or something malformed. Use
`base64.b64encode`, never `base64.urlsafe_b64encode`. As of build `c358a53b` (superseded by `6a4f3aee`)
the Engine rejects both rather than guessing; on older builds URL-safe input
was accepted and **silently truncated**, so treat pre-2026-09-04 artifacts with
suspicion (§13, R7).

**409 `conflict` scattered across hypotheses / experiments / observations.**
Almost always one idempotency key reused across worlds. The key is scoped to
`(client, key)` and the stored request hash binds **route + world_id + body**,
so a key that is unique per logical step but not per world conflicts on every
world after the first. The 409 body names `first_used_route` and
`first_used_world_id` — make the key unique per `(world, step)`.

**`POST /v2/clients` returns 403.** Registration was closed after bootstrap.
Check `registration_open` in `GET /v2/version` and ask the operator for a token.

**Requests take seconds instead of milliseconds.** Normal is ~40–60 ms.
The Engine process runs with a very small thread count and is effectively
serial, so it degrades under heavy concurrent disk load on M1 rather than
under request load. It recovers on its own. If it persists, tell Daedalus —
do not restart the service yourself.

**Never restart the Engine to "fix" something.** It is a shared always-on
service with other users on it. See §13.

---

## 13. Operator notes (M1 only)

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

**Known residual R1 (not fixed here):** there is no singleton guard — no
lockfile or pidfile — and uvicorn sets `SO_REUSEADDR`, which on Windows permits
binding an address already in use. A stray manual `python serve.py` would bind
alongside the service and split traffic rather than failing loudly. Worth a
`var/engine.lock` exclusive-open guard in `serve.py` before `uvicorn.run`.

**R7 — artifact body decoding did not fail closed. FIXED 2026-09-04, live in
build `c358a53b` (superseded by `6a4f3aee`).** Found 2026-09-03. Two behaviours on
`POST /v2/worlds/{wid}/artifacts`, both now closed:

| | before (≤ `5274ddbe`) | now (`c358a53b` and later) |
|---|---|---|
| URL-safe base64 (`-`/`_`) | **200, silently stored different, shorter bytes** (24 in → 15 stored) | **422** naming `body.data_b64` |
| malformed base64 | **500 `internal_error`** | **422** `validation_error` |

`base64.b64decode(..., validate=True)` plus an explicit 422. Re-proved against
the live service after restart, along with: standard base64 still accepted and
byte-exact, the shipped `sfclient.artifact()` path unchanged, and three bad
payloads creating **zero** artifacts.

**A caveat about older data.** Artifacts written before 2026-09-04 could have
been silently truncated if their producer used URL-safe base64. Nothing detects
that server-side — `blob_hash` is the hash of what was *stored*, not of what was
*sent*. If you hold pre-2026-09-04 artifacts whose bytes matter, verify
`blob_hash` against your own `sha256` of the original. No such corruption was
found in this repository's data (only 7 artifacts carry an `organism_id`, and
the mismatches among them are known test fixtures with deliberately synthetic
ids).

Also fixed the same day: the blanket 500 handler swallowed its traceback
entirely, which is why the base64 defect sat in the log as a bare
`internal_error` with nothing to chase. It now logs server-side; the wire
response is unchanged.

**Open registration** means any host on `192.168.1.0/24` can mint an identity.
That is intentional for bootstrap; close it with `serve.py --registration
closed` when the fleet is stable.
