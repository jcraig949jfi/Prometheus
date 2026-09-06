# SFE contract — Archaeon (producer) and Vivarium (executor)

**For:** the two automated tools now joining Harmonia on M1.
**Engine:** `https://192.168.1.202:8811`, schema 6, `--cacert deploy/m1.crt`
(IP-SAN only — use the IP, never a hostname).
**Written:** 2026-09-06 by Daedalus, from the live service and your code, not
from the design. **Corrected the same day** — five statements below were wrong
and are marked; see the change note at the end. Harmonia has also issued you a
machine-readable contract (`roles/Harmonia/contracts/`); the two are
complementary and where they overlap I have said which is authoritative.

You are two halves of one protocol: Archaeon **declares**, Vivarium
**executes**. The engine's job is to make the seam between you auditable. This
document is what each half owes the engine, and what the engine owes you back.

Read `SFE_CLIENT_GUIDE.md` first for endpoint, auth and all 50 routes, and
`SerendipityFoundryEngine/docs/SCIENTIFIC_PROVENANCE.md` for the v6 semantics.
This page is only the part that is *yours*.

---

## 0. Six rules, before any detail

1. **One stable client identity per tool. Not one per run.** This is the
   biggest thing on the page — see §1.
2. **Scope your corpus, or ask me for a route.** The API is right for your own
   data; it cannot show you another tenant's, and Archaeon owns none of the
   corpus it needs — see §2, which was wrong in its first cut.
3. **Heartbeat any lease you hold.** See §4.
4. **Attest what you ran.** All four hashes, not just the config — see §5.
5. **Declare a budget with `enforcement: "enforceable"`.** The default caps
   nothing — see §7.
6. **Send an `Idempotency-Key` on every creating write.** You are a machine
   that retries — see §6.

**CORRECTED.** An earlier cut of this page said *"under warn nothing you send
can be refused by a v6 check"*. That is false, and two automated callers would
have written no 422 path because of it. The accurate rule has two parts:

**1. Shape and vocabulary reject in EVERY profile, `off` included.** These are
structural coherence, not science, so the profile does not grade them. Measured
against `science_profile=off`:

| Rejected in every profile | |
|---|---|
| `SUCCESSFUL_NEGATIVE` without `relevance_floor` | the claim *is* about the bound |
| `source_set` without `unit_of_analysis` | and the reverse |
| `enqueue` without `commit` | nothing executes before its spec is sealed |
| an unknown `replication` dimension | closed set, on purpose |
| `status: "RETRACTED"` at creation | retraction is a transition |
| any unknown family kind / member kind / role / claim status / unit | closed vocabularies |

**2. A v6 FINDING blocks under `warn` in exactly one case:** when it
contradicts a declaration you sealed *in the same request*. Today that is a
fork child asserting `intervention_effective: true` while the engine's own
arithmetic says the intervention was inert or never applied. Everything else is
advisory under `warn`.

So: **treat 422 from `/experiments`, `/claims` and `/fork` as a normal,
non-transient outcome.** Log the finding codes and stop; do not retry. Findings
come back in `science.profile_findings` and are sealed into the event chain —
the engine will not stop you recording bad provenance, only make it visible,
and reading it is your job.

### The complete finding vocabulary — thirteen codes

Neither contract listed all of them: mine omitted `PARTIALLY_INERT_INTERVENTION`
and Harmonia's predates `CLAIM_CITES_UNVERIFIED_ANALYSIS`. A headless tool
holding a short list will escalate on a normal engine output, so here is the
whole set, generated from the source:

| On work completion | On fork | On a family read | On a claim |
|---|---|---|---|
| `CONFIG_DIVERGENCE` | `NO_EFFECTIVE_INTERVENTION` | `FAMILY_EXTENT_DIVERGENCE` | `CLAIM_CITES_NON_ANALYSIS` |
| `NO_EXECUTION_ATTESTATION` | `INTERVENTION_NOT_APPLIED` | `MULTIPLE_SELECTED` | `CLAIM_CITES_UNVERIFIED_ANALYSIS` |
| | `PARTIALLY_INERT_INTERVENTION` | `SELECTION_WITHOUT_ALTERNATIVES` | `TRANSPORT_OVERREACH` |
| | | | `TRANSPORT_UNCHECKABLE` |
| | | | `NO_REPLICATION_DECLARED` |

A fork can now return **more than one** finding — the declared-before/after
test and the engine-visible test are independent evidence and both always run.
Read `profile_findings` as a list, never as an optional single value.

---

## 1. One stable client identity per tool

**Vivarium currently mints a new SFE client on every process start** — 14 of the
174 client identities on M1 are Vivarium runs, each owning exactly one world,
one work item and one observation. Isolation happens to be perfect. Almost
everything else is broken by it:

* **A family cannot span your runs.** `family_members` requires every member to
  be owned by the *same* client (a foreign member returns 404 — deliberately,
  so membership cannot become an existence oracle for another tenant). With one
  client per run, the cross-world container built for *"twelve proposed, eight
  executed, one selected"* is unbuildable by the tool that produces exactly
  that shape.
* **An analysis cannot span your runs.** Sources you do not own resolve to
  `unresolved`, so a cross-run `source_set` silently counts **nothing**. As of
  2026-09-06 that now raises `CLAIM_CITES_UNVERIFIED_ANALYSIS` on any claim
  citing it — before that it produced a clean `SUPPORTED` claim over an empty
  evidentiary base.
* **A claim cannot cite an analysis from another run**, for the same reason.
* Identities accumulate without bound, and the token is shown once.

**What to do.** Register once, store the token, reuse it. `VIV_SFE_TOKEN` is
already the documented precedence in `viv/db.py` — use it.

```
POST /v2/clients {"name": "vivarium"}      # ONCE, ever. Token shown once.
POST /v2/clients {"name": "archaeon"}      # ONCE, ever.
```

**Separate clients for Archaeon and Vivarium, both stable.** Separate, because
`claim_work` filters by `client_id` and nothing else — if you share a token,
either tool can claim the other's queued work, and Harmonia's too. Stable,
because everything cross-run depends on it.

**Sessions are per-campaign, not per-run.** A session is the affinity container:
its key is bound to this engine instance and refuses to work against any other.
Create one per campaign, hold `session_key`, send it as `X-SFE-Session` on every
request. `sfclient` does this for you after `create_session()`.

---

## 2. Archaeon: the corpus problem

Archaeon opens the live SQLite file and queries it. Four things a raw read
loses, none of them style:

1. **No tenancy filter.** A direct read pools every client's worlds into one
   population — Harmonia's, Vivarium's, my test harnesses', the 106 legacy
   sessions'. Whatever your detectors then compute is over a corpus you did not
   define. The API applies ownership on every route; the file does not.
2. **No evidence-class filter.** The ledger holds both `ENGINE_WORK_RESULT`
   (work-bound and verified) and `CLIENT_ASSERTED` (a client's word).
   Currently 2,970 vs 359 on M1. Pooling them is the *"engine-attested"*
   misreading in a different costume.
3. **Multi-statement reads take a fresh snapshot each time.** SQLite WAL gives
   you a consistent view *within* one transaction. Several separate `SELECT`s
   against a live database being written by three consumers is not one
   observation of one state.
4. **It bypasses the schema guard.** The engine refuses to open a ledger newer
   than its code (`store.py:471`). A raw reader has no such protection and will
   happily misread a v7 database as v6.

**CORRECTED — and this section and §1 are jointly fatal as first written.**
Every read route is hard-scoped to the calling client (`_authorize`:
*"a client may only touch its own worlds"*). Of the 2,993 engine-attested
observations on M1, **2,937 belong to `harmonia-m2` and Archaeon owns none**.
So "use the API instead" plus "separate stable clients" together leave Archaeon
able to see **zero** executed experiments. Both rules are individually right and
following both blinds you.

**That is my problem, not yours to work around.** Until it is resolved:

* **Keep the read-only file read** (`mode=ro`), but add in SQL the two filters
  the API would have applied: a **declared `client_id` set** and
  `evidence_class = 'ENGINE_WORK_RESULT'`. Then record the corpus tenancy as a
  field in every survey. That converts an unstated pooling into a declared
  population, which is the part that actually matters scientifically.
* Points 3 and 4 above still bite even with filters — a multi-statement read of
  a live WAL database is not one observation of one state, and a raw reader has
  no schema guard. Prefer a single transaction, and check
  `meta.schema_version` yourself before trusting a row shape.
* **The real fix is mine:** a deliberate read-grant that crosses tenancy on
  purpose, preserving `evidence_class` and world grouping, rather than leaving
  it to a file read that carries no contract at all. `create_topology_group`
  already mints exactly this shape of unguessable, server-issued sharing
  capability — it is simply not wired into reads. Awaiting the operator's
  decision; say if you need it and how wide.

For your **own** corpus the API is strictly better today: `GET /v2/worlds`,
`GET /v2/worlds/{wid}/observations`, `GET /v2/worlds/{wid}/events`,
`GET /v2/worlds/{wid}/knowledge`. §9 lists the reads I know are missing.

---

## 3. Archaeon: the experiment spec is your pre-registration

`spec` is **freeform and opaque to the engine**, sealed by `spec_hash` at
commit, and frozen from that moment. It is not a parameter bag — it is the
declaration everything else is judged against.

```
POST /v2/worlds/{wid}/experiments
Idempotency-Key: <stable key for this proposal>
{
  "spec": { ...your declaration... },
  "hyp_id": "hyp_...",            # optional but see §8
  "pred_id": "prd_...",           # must pre-date the commit to be prospective
  "commit": true,                 # crosses the irreversible boundary
  "enqueue": true,                # releases it for execution (requires commit)
  "kind": "experiment"
}
```

Put in `spec` everything a reader would need to judge the result, because
**nothing added later is sealed**:

* the procedure and its parameters — including the **estimator and its
  parameters**, which is where estimator identity lives; the engine has no
  separate field for it, and a trimmed mean standardised by a winsorised sd
  overstates a heavy-tailed effect threefold with no selection in play;
* `tested_domain` — **CORRECTED: this belongs on the ANALYSIS experiment, not
  on the executed one.** `create_claim` reads it from the spec of whatever you
  pass as `analysis_exp_id`, so putting it on the run that produced the data has
  no effect. Put it on the `kind="analysis"` experiment you later cite. A
  claim's `transport_domain` is checked for containment against it; without it
  you get `TRANSPORT_UNCHECKABLE` rather than silence;
* the source set, if this is an analysis and you want it recoverable — the
  engine stores only its **hash**;
* what is held FIXED, not only what varies.

**The commit boundary is irreversible and it closes the prospective window.**
A prediction is prospective iff `pred.created_seq < exp.committed_seq`. Register
predictions *before* you commit. `enqueue` requires `commit`, so nothing can be
executed before its spec is sealed.

**Note for the Archaeon↔Vivarium seam — CORRECTED, and it was already fixed
before I wrote it.** Vivarium's validator takes a closed top-level key set
(`spec_version`, `world`, `hypothesis`, `prediction`, `work`, `outcome_rule`,
`pew`) and expects probe parameters inside `work.payload`. The older
`propose.py` / `explore.py` builders emit those parameters at the top level and
are rejected downstream — but `archaeon/producer/specbuild.py` now emits the
correct shape. My earlier claim that *"nothing Archaeon proposes executes
today"* was true of the old path only and was stale when written. The engine
accepts either shape; this seam is yours, and the producer path is on the right
side of it.

---

## 4. Vivarium: the work lifecycle, including the step you skip

```
claim      POST /v2/work/claim              -> {work_id, claim_id, ...}
heartbeat  POST /v2/work/{id}/heartbeat     <- YOU DO NOT DO THIS
complete   POST /v2/work/{id}/complete
fail       POST /v2/work/{id}/fail
```

`claim_id` is a **server-issued fencing token**. It is mandatory on complete and
fail, and it is what makes exactly-once completion provable.

**You claim with `lease_s=120.0` and never heartbeat.** Today that costs
nothing: your two executors are a literal dict and one sha256, four orders of
magnitude inside the lease. It stops being free the moment an executor does real
work — an LLM-backed or `archaeon.probe.v0` executor will blow through 120s
easily.

When a lease expires, reclaim **clears `claim_id`**, permanently invalidating
your fencing token, and your `complete()` is refused with a 409. The compute is
spent and the result is discarded. Reclaim is lazy but effectively continuous
with three consumers polling — it runs on *anyone's* claim.

`EngineClient.heartbeat(work_id, worker_id, claim_id, lease_s)` already exists.
Call it on a timer for the duration of the run, or size the lease to the
executor. Do not rely on 120s being generous.

---

## 5. Vivarium: attest what you actually ran

You already send `executed_config` on every run — genuinely good, and the
engine compares its hash against the `spec_hash` sealed at commit.

**Two things to improve.**

**Send the other three.** All 14 of your attested runs carry
`executed_config_hash` and **zero** carry the rest:

```json
"attestation": {
  "executed_config": { ...what you actually ran... },
  "player_identity_hash":      "sha256:...",   // WHICH BUILD of the agent
  "entry_state_hash":          "sha256:...",   // state the player ENTERED with
  "measurement_identity_hash": "sha256:..."    // which scorer / regime
}
```

`player_identity_hash` is the one that catches *"the same policy under two
names"* — the defect that produced p=0.036 between a player and itself. If your
player is placed as an artifact, its `blob_hash` is already a
world-independent content address; use that.

**Understand what your attestation currently proves.** If you echo back the same
dict you just sent as `spec`, `CONFIG_DIVERGENCE` can never fire — it is a
tautology. It becomes meaningful when the config is read from what the executor
*actually loaded*: after defaults are applied, after any environment override,
after the model or seed is resolved. Attest the effective config, not the
requested one. Otherwise the check is real but the input to it is not.

**Read `entry_state_hash`'s limit before you trust it.** The engine never sees
player state and can never know whether a reset happened. It compares a declared
discipline against an attested hash — a claim against a claim. A *converged*
leaker enters every world from the same fixed point, so its entry hashes are
indistinguishable from an honest reset. The engine will never report
"independence verified", and neither should you.

---

## 6. Both: idempotency, because you retry and humans do not

`POST /v2/worlds`, `.../experiments`, `.../observations` and `.../artifacts` all
take an `Idempotency-Key` header. Neither of you sends one.

A timeout on `POST /v2/worlds` without a key produces **a second causal
universe** — the request may well have succeeded. With a key, a retry returns
the original result; the same key with a *materially different* body is a 409.
Derive the key from your queue row id, not from a clock.

Related: a `complete()` replayed with an **identical** result is idempotent
(200, same `result_hash`); replayed with a **different** result or a different
attestation it is a 409 carrying both hashes. Do not treat that 409 as a
transient error and retry it — it means the two results disagree.

---

## 7. Both: declare a budget that actually caps

`budget.enforcement` defaults to `"measured"`, **which enforces nothing**. The
`resources` endpoint will faithfully report `consumed: {experiments: 6}` against
a declared limit of 2 and `exhausted: false`. Instrumentation that looks like
control is worse than none, and a crash-looping automated producer is exactly
what it fails to stop.

```json
"budget": {"experiments": {"limit": 500, "enforcement": "enforceable"}}
```

Only `enforceable` caps. **There is no rate limit, quota or concurrency cap
anywhere in the engine** — your own budget is the only backstop, and a runaway
loop is bounded by nothing else.

---

## 8. Both: what makes evidence count

| You do | You get |
|---|---|
| `record_observation` with a `work_id` bound to completed work for that experiment | `evidence_class = ENGINE_WORK_RESULT` |
| `record_observation` without one | `evidence_class = CLIENT_ASSERTED` |
| Prediction registered before commit | `pred_prospective = true` |
| Prediction registered after commit | requires `retrospective=true`, never prospective |
| World created with `require_attestation: true` | unattested observations are **refused at the write** |

Vivarium already binds `work_id` on every run. Archaeon: if you ever record an
observation you did not execute, it is `CLIENT_ASSERTED`, and it should be.

**`require_attestation` is now reachable from the client** (added 2026-09-06) —
`create_world(..., require_attestation=True)` makes the guard fail-closed rather
than a matter of discipline. Use it for any arm whose result you intend to
claim.

**And know what `ENGINE_WORK_RESULT` does NOT mean.** It means the engine ran
and sealed the work — same world, COMPLETED, enqueued for this experiment. It
does **not** mean the executor did what the spec declared. As of v6 the engine
*does* compare the executed config against the sealed spec, but under `warn` a
divergence is a non-blocking finding on the completion response, and the
observation still types `ENGINE_WORK_RESULT` while every epistemic counter stays
green. **With an automated executor, nobody reads that response unless you make
it.** Check `science.profile_findings` on every completion and log a divergence
loudly. That is the single most important line in this document for Vivarium.

---

## 9. What the engine does not give you yet

Measured against the live service, so you do not go looking:

| You might want | Today |
|---|---|
| `GET /v2/sessions` — re-discover your sessions after a restart | **405.** The session key is returned once; persist it. |
| `GET /v2/work` — enumerate your in-flight or orphaned work | **404.** Wait out the lease and re-claim. |
| `GET /v2/events` — the global ledger where family/claim findings are sealed | **404.** Claim findings are now readable via `GET /v2/claims/{id}`; family findings recompute on read. |
| `/v2/measurements` | **404.** The table and runtime exist; no route populates it, so `measurement_id` on a failure can never resolve. Use `measurement_identity_hash` in the attestation meanwhile. |
| Attest a result produced **outside** the SFE work queue | Not possible. Attestation writes only through `POST /v2/work/{id}/complete`. If you produce results out of band, you cannot record the executed side. |
| Add a family member that does not exist yet ("planned") | Members must resolve to an existing object. Create the experiment with `commit=false` (registered, non-executable, no budget) and add *that*. |
| Delete a world | Nothing reaps. 500 worlds and counting on M1; deletion destroys ledgers and waits on a retention policy. Terminate what you finish. |

Tell me which of these you actually need and I will build them. They are absent
because nobody needed them, not because they are refused.

---

## 10. Checklist

**Archaeon**
- [ ] One stable client; register once, persist the token
- [ ] Stop reading `engine.db`; use the API
- [ ] Put estimator, parameters and `tested_domain` in `spec`
- [ ] Register predictions before commit
- [ ] `Idempotency-Key` on every creating write
- [ ] `enforcement: "enforceable"` budgets
- [ ] Emit specs in the shape Vivarium's validator accepts
- [ ] Consider families for campaigns and claims for conclusions — both need the
      stable client identity first

**Vivarium**
- [ ] One stable client; use `VIV_SFE_TOKEN`
- [ ] Heartbeat the lease, or size it to the executor
- [ ] Attest all four hashes, from the **effective** config
- [ ] **Check `science.profile_findings` on every completion and log divergence**
- [ ] `Idempotency-Key` on world/experiment/observation creation
- [ ] `require_attestation=True` for claimable arms
- [ ] Terminate worlds you finish
- [ ] Replace the private `_req` calls with `audit_envelope()` / `verify_anchor()`

**Me**
- [x] `/v2/version` no longer takes the write lock — 22.8s → 0.023s
- [x] `CLAIM_CITES_UNVERIFIED_ANALYSIS`
- [x] Claim findings readable on GET
- [x] `require_attestation`, `audit_envelope()`, `verify_anchor()` in the client
- [ ] The routes in §9 you tell me you need

---

## Change note — 2026-09-06

This page was audited against the engine and both live services after it was
first written, and five statements did not survive. Recorded here rather than
quietly overwritten, because you are automating against it.

1. **"Under warn nothing you send can be refused by a v6 check"** — false.
   Seven shape and vocabulary rules reject in every profile, and one finding
   blocks under warn. Rule 0 now states the real rule.
2. **The finding vocabulary was incomplete** — thirteen codes exist; this page
   listed twelve and Harmonia's contract lists a different twelve. The full set
   is now in §0.
3. **"Nothing Archaeon proposes executes today"** — stale when written;
   `archaeon/producer/specbuild.py` already emitted the correct shape.
4. **`tested_domain` placement** — it is read from the ANALYSIS experiment's
   spec, not the executed experiment's. The checklist said the wrong one.
5. **§2 and §1 were jointly fatal for Archaeon** — "use the API" plus
   "separate clients" leaves it seeing nothing, because every read route is
   owner-scoped and it owns none of the corpus. §2 now says so and carries an
   interim that does not require it to be blind.

Also fixed in the engine the same day, and relevant to §8: declaring
`intervention_effect` used to make `INTERVENTION_NOT_APPLIED` unreachable, so
the caller who disclosed more was checked less. Both intervention tests now
always run and a fork can return more than one finding.
