# Daedalus — Open Work

**Owner:** Daedalus (maintainer, Serendipity Foundry Engine)
**Last updated:** 2026-09-06, after a full audit of this file against the code
and both live services. Every item below was re-verified; 25 were rewritten and
9 deleted as closed.
**Pointer from:** `roles/Daedalus/RESPONSIBILITIES.md`

This is the standing list of what is NOT done. Items are closed by **deleting**
them and citing the commit, never by marking them done here and leaving them.
Section D-numbers are kept stable across rewrites because other roles cite them.

Status vocabulary, because collapsing any two of these is how "the fix is in"
becomes a false statement:

    CODE_FIXED != SERVICE_DEPLOYED != LIVE_VERIFIED != QUALIFIED

**A note on this pass.** Between 2026-09-05 and 2026-09-06 this file drifted
badly: schema v6 shipped and closed much of D7/D8/D9, and I added D10 describing
what shipped while leaving the superseded items standing underneath it — exactly
what the rule above forbids. The audit also caught two claims of mine that were
simply false (M2 "down"; a doc-reading gap filed as a control-instrument
disagreement). Where an item's premise was wrong, the correction is recorded in
the item rather than quietly overwritten.

---

## STATE OF THE TWO ENGINES (measured 2026-09-06, not asserted)

| | M1 / SKULLPORT | M2 |
|---|---|---|
| endpoint | `https://192.168.1.202:8811` | `https://192.168.1.191:8811` |
| reachable | yes | **yes** — own trust anchor validates, no `-k` |
| schema | **6** | **4** |
| `engine_source_hash` | `sha256:7b46e2b5…` | `sha256:6a4f3aee…` |
| `source_commit` | `4d315bafe` (stale until restart — see D11) | `0fd24e0f3` |
| `engine_instance_id` | `eng_8a37a5d305969034d488c43e` | *absent — predates the field* |
| `session_enforcement` | `advisory` | *absent — no affinity layer* |
| `science_profile` | `warn` | *absent — pre-v6* |
| `/v2/families`, `/v2/claims` | 401 (present) | **404 (absent)** |
| ledger | 500 worlds, 403 RUNNING, 182 created 2026-09-05 | separate ledger |

Live surface: **44 distinct paths, 50 method+path pairs**; 40 session-scoped, 6
unscoped. Test suite: **237 green**. Battery: **23/23** without
`--expect-source-hash`, 24 with it.

---

## D11 — Deployment integrity: the engine's own checkout (NEW, PARTLY REPAIRED)

**Repaired 2026-09-06 in `d269c6c7a`; the structural half is still open.**

The deployment tree `F:/Prometheus` — the path `deploy/sfengine.cmd` launches
from — is a **shared checkout other roles switch branches in**. On 2026-09-06 it
sat on `vivarium/v0-2026-09-05` (HEAD `ecfef4d87`) with the entire v6 engine
present only as uncommitted modifications plus untracked files;
`869df1fa1..088591ab3` are ancestors of neither that HEAD nor local `main`.

**Severity, corrected by measurement.** I first called this a silent-downgrade
hazard. It is not silent. Running the pre-v6 source (`35758f9d0`) against a
`VACUUM INTO` copy of the live ledger:

    RuntimeError: db schema version 6 is NEWER than this engine's 5;
                  refusing to run (would misread state)      store.py:471-474

So a revert produces a **loud outage** — the service dies — rather than quietly
serving pre-v6 semantics over v6 data. Correct failure direction; lower severity
than I claimed; still an outage on a live experimental service.

**Done:** `deploy/DEPLOYED_BUILD.json` pins the build independently of that
tree's branch state (commit, authoritative `engine_source_hash`, per-file
LF-normalized digests for all 12 source files, expected runtime config, measured
rollback behaviour, restore path touching only SFE paths).
`deploy/verify_deploy.py` checks the pin against both tree and live service —
**8/8 today**. Proof recorded: the committed `sfe/*.py` at `465853b69` recompute
to `sha256:7b46e2b5…`, byte-for-byte what M1 serves.

**Still open — the structural fix:** give the engine a checkout **no other role
writes to**, and point `sfengine.cmd` at it. That is what actually removes the
hazard; the pin only makes it detectable and recoverable. It needs a restart, so
it belongs in a deployment window, not a cleanup pass. See the M2 readiness
report — do both at once.

**Deliberately not done:** reconciling that checkout. Moving its HEAD to
`origin/main`, or committing onto `vivarium/v0-2026-09-05`, touches another
role's active branch; staging into the shared index is worse, since their next
`git commit` would sweep my files onto their branch. The tree also carries
uncommitted work from **ergon** (7 files) and **evidence_wiki/PEW**
(`lineage_results.json`), plus untracked scratch from several roles. All left
exactly as found.

---

## D1 — Engine work, justified but not urgent

### D1-1  Document the client's unwrapping asymmetry — WIDER THAN FILED
Raw HTTP returns `{"events": [...]}`; `sfclient.events()` returns the bare list
(`api.py:674` vs `client.py:160`). Confirmed still present. **The item
understated it: five client methods unwrap** — `events`, `failures`, `lineage`,
and now `list_families` / `list_claims`. `SerendipityFoundryClient/docs/API.md`
is dated 2026-09-02, documents none of it, and covers **zero v6 routes**.
**Doc fix, not a code fix — do not "fix" the endpoints.** Blocked on nobody.

### D1-2  Dry-run / preflight validation for frozen specs
Blocked on **R-7** (Harmonia's choice of shape; no answer recorded anywhere in
the repo). My lean is unchanged: spec_hash prediction plus seed_root/enforcement
TYPE validation — not full budget/window admissibility, because that answer can
go stale between preflight and execution and **a stale PASS is worse than no
PASS**. Hard constraint: a dry run must append no event, debit no budget, mint
no id, and consume no idempotency key.

### D1-3  The measurement substrate is UNREACHABLE, not merely unused
Two separable facts; the second is the one I had never stated.

**(a) The contract is not being used.** `measurements` holds **0 rows** on the
live v6 ledger. `observations.content` is still freeform `TEXT NOT NULL`
(`store.py:219`) with no `measurement_id` column. Only 2 of 6,006 candidate
artifacts carry phenotype scores (`evidence_wiki/docs/
PHENOTYPE_CONSUMER_REQUIREMENT.md:32-33`).

**(b) It is EMPTY BECAUSE NOTHING CAN FILL IT.** The schema exists
(`store.py:419-434`) and the runtime has `register_measurement`
(`runtime.py:2930`) and `get_measurement` (`runtime.py:2963`) — but **no route
exposes either**. There is no `/v2/measurements` among the 44 live paths. The
only `measurement_id` on the wire is the failures POST body (`api.py:154`),
pointing at `failures.measurement_id` (`store.py:269`) — and with
`PRAGMA foreign_keys=ON` (`store.py:451`) that FK **can never resolve, because
nothing can create the row**. Live count of failures citing one: 0.

**v6 did not close this.** `work_items.measurement_identity_hash` is an
**opaque executor-asserted hash** with no name, version, params or domain. It
lets the engine detect that the scorer *changed*; it still cannot say *what was
measured*. Populated on 2 of 3,212 work items.

**Split the blocking correctly:** the *schema question* — which of the nine
phenotype items are the engine's — is blocked on **R-3** (Mnemosyne, still
unanswered; her `todo_20260904.md:25-27` carries it as A3, "Daedalus did not
touch it"). The *no-route-exists* half is **blocked on nobody** and is mine.
Shipping create/read routes for a table the schema already carries is not a
guess about the nine items.

### D1-4  arena.run — bounded implementation
Engine-facing contract CLOSED. Blocked on **R-1** (fossil completeness) and
**R-4** (organism content id). **Standing rule: the wrapper must make invalid
states harder to express. It must not automate the current 14-step hazard with
the defects still underneath.**

---

## D2 — Deferred, with the trigger that revives each

### D2-1  Same-world concurrency qualification (Q-2) — DEFER, trigger NOT fired
No world has ever had two distinct workers: across 3,212 work items and 40
worker ids, `COUNT(DISTINCT claimed_by) > 1` per world returns **0 rows**. Code
reading still correct (`BEGIN IMMEDIATE` `store.py:616`; `UNIQUE(world_id,
world_index)` `store.py:117`; server-issued fencing `claim_id`
`runtime.py:828`, mandatory at `:884`/`:913`).
**Correction to the old wording:** it is not "UNMEASURED" —
`tests/test_sfe_invariants.py:205` runs 8 threads claiming in ONE world and
asserts each of 20 items is claimed exactly once. That is an in-process
measurement against a temp SQLite file, so under this file's own rule it is
CODE_FIXED, not QUALIFIED. *Revive:* a campaign that genuinely needs two workers
in one world.

### D2-2  Duplicate work completion (Q-3) — CRITERION CORRECTED
The old acceptance criterion ("assert the second is REFUSED") is **wrong for one
of its two cases** as of v6's C3e fix. Correct criterion:
* an **identical** replay must be IDEMPOTENT — 200 twice, same `result_hash`
  (`test_sfe_strict_and_completion.py:130`);
* only a **materially different** completion is REFUSED — 409 carrying both
  `stored_result_hash` and `submitted_result_hash` (`:142`).
Both named probes have pytest coverage (`test_sfe_invariants.py:191`;
`test_sfe_requalification.py:218`/`:229`). Still open as an **unrun
qualification** against the deployed service.

### D2-3  N-isolated-world qualification (Q-1) — GATE ALREADY VIOLATED
**Recording this as it happened, not as it should have happened: the "before a
parallel campaign" gate fired unnoticed and the campaign ran anyway.** Bucketing
`work_items.updated_ts` into 60-second windows gives **37 buckets with more than
one active worker, peaking at 4** (A-worker, B-worker, harness-worker,
integration-probe) — parallel work in distinct worlds, already live on M1,
without Q-1 ever being run.
In-process coverage exists at small N and nowhere near the specified N:
`test_sfe_invariants.py:74` is the Q-1 shape at N=6 (covers the N=4 rung);
`:513` runs 20 worlds / 10 workers; `:57` builds 27 worlds single-threaded.
**N=64 has never been run anywhere, by anyone.** Re-gate on N>=16 concurrent
workers, or simply run the N in {4,16,64} bar now.

### D2-4  Restart durability under load (Q-4) — DEFER, reason STRONGER
No test kills a service under write load; every "restart" in the suite is a
clean in-process reopen (`test_sfe_invariants.py:158`, `test_sfe_gen21.py:266`,
`test_sfe_session_affinity.py:244`); grep for kill/SIGKILL/taskkill across
`tests/` returns nothing. The reason to defer has strengthened: M1 now holds
**500 worlds, 403 RUNNING**, newest 2026-09-05 18:19:37, with
`vivarium@skullport` active. "Not to be run against an engine holding anyone's
campaign" now **excludes M1 outright**. Operator authorization still unobtained.

### D2-5  Throughput ceiling (Q-5) — DEFER
Deferral reasoning intact. Precision fix: it is not that "no number exists" —
`test_sfe_invariants.py:513` computes and prints a throughput figure, asserts
nothing about it, and retains it nowhere. **No RECORDED number exists.**

### D2-6  Test-world GC / reaper — TRIGGER FIRED, AND DELETION STAYS BLOCKED
**The count trigger has fired: exactly 500 worlds** (37 CREATED, 403 RUNNING, 60
TERMINATED), 182 created 2026-09-05 — a large share from my own v6 smoke and
battery runs. All 500 created within the last 7 days. Nothing reaps: grep for
reap/gc/retention/purge/prune across `sfe/*.py` finds only prose, and
`api.py:484` says outright "an orphan at birth, in a system with no GC".

**Do NOT revive deletion on the count alone.** The disk trigger has *not* fired
(F: is 3.7T with 2.2T free; `var/` totals 314M). **Deleting worlds destroys
ledgers**, so this waits on a stated retention policy, not a maintainer's
judgement and not a threshold. What the count changes is that this is now *live
work to decide*, not deferred work to ignore. Enumeration is filterable
(`runtime.py:717`, `api.py:617`), so cleanup candidates are already
identifiable.

### D2-7  Constraint registry / predicate DSL — REJECTED, still right
The rejection stands. Minor staleness: "at seven constraints" understates the
current table. *Revive:* a constraint appears that a pytest cannot express.

---

## D3 — Blocked on other components (track, do not implement)

**To Mnemosyne / PEW**
- **R-M-1** consume + serve the SFE audit envelope
  (`GET /v2/worlds/{wid}/experiments/{eid}/audit-envelope`). Nothing in
  `evidence_wiki` calls it yet. Still the half I cannot do.
- **R-1** typed fossil fields. **The "9 of 16" count is stale — recount it.**
  `registry_id`/`registry_identity` still return zero hits in `sfe/`; there is
  no `output_digest`, no typed action/input, no full `world_config` export. Two
  things moved: the engine-identity ambiguity is resolved and consumed (see the
  closure record), and v6 added four identity slots that overlap this list.
  **Say explicitly that `executed_config_hash` / `player_identity_hash` /
  `measurement_identity_hash` are ATTESTED, not minted, so they do not
  discharge R-1.**
- **R-2  — substantially met; the residual is narrower than filed.** PEW now
  requires BOTH bindings and refuses the unbound form
  (`ew/closure.py:147-148`, `:176-181`); the wrong-but-real case is gated live.
  **Residual:** neither side ever asserts `event_type == 'OBSERVATION_RECORDED'`,
  though the engine returns `event_type` on every verify
  (`runtime.py:1227`). Either PEW requires it, or I make `exp_id` mandatory on
  the bound form.
- **R-3** which of the nine phenotype items are the engine's (see D1-3(b) —
  this now blocks only the schema half, not the route half).

**To Proteus**
- **R-4** the authoritative organism content id and where it is minted.
- **R-5** `registry_id` for the fossil's registry_identity field.

**To Harmonia / James**
- **R-6** contract decision on a typed `components` field. The engine cannot see
  inside `spec`, so nothing mechanically checks that a run labelled A+B was
  actually A and B. **Still the likeliest route by which the programme produces
  a wrong interaction claim.** It changes the meaning of `spec`, so not mine.
- **R-7** dry-run shape (see D1-2).

**New, engine-side, arising from PEW's delivery:**
- **D3-N1** PEW is already coded to consume a `binds_session` check that the
  engine never returns. Either return it or tell them it is not coming.

---

## D4 — Session affinity v5: what qualification did NOT close

### D4-1  Cross-machine affinity — PREMISE CORRECTED: M2 is UP
**The old blocker was false and I never checked it.** M2 answers at
`192.168.1.191:8811` with its own trust anchor validating (no `-k`). So **L1
(off-host reachability) and a first cut of L2 (foreign trust-anchor validation)
are demonstrable today.**

**L3 — cross-machine affinity, the property the feature exists for — still
cannot be run at all**, because M2 runs schema 4 / `0fd24e0f3`, which predates
session affinity entirely: no `session_enforcement`, no `engine_instance_id`,
and a schema-4 engine has no session keys to mismatch.

Every cross-engine result to date is **two processes on one box**, loopback-
routed, bypassing the host firewall
(`test_sfe_session_affinity.py:316` and the v6 twin tests). **There is no
cross-machine qualification and nothing should be read as one.**

**Blocked on: deploying current v6 to M2** — work of mine, not a wait.
**Deploy target is `d269c6c7a` (current tip, carries the build pin).** The old
target `b35046a60` is now many releases stale and deploying it would land M2 on
a build M1 no longer runs — re-opening the build-parity gate that exists to stop
exactly that. Readiness report written and NOT acted on: `roles/Daedalus/M2_V6_DEPLOYMENT_READINESS_2026-09-06.md`.

### D4-2  Legacy drain is not moving; the cutover will be date-driven
106 LEGACY sessions, all still OPEN. `close_session` exists and is verified, but
**nothing auto-closes and nothing should** — closing a session to move a metric
is gaming it unless the session is genuinely finished. On current behaviour the
cutover is date-driven (2026-10-01). **Decide before then:** drain deliberately,
move the date, or accept a date-driven cutover and say so. Blocked on James;
nothing technical blocks it.

### D4-3  Work-route claim scoping is still unbound to the session's worlds
Untouched by v6, verified in code not text: `claim_work` (`runtime.py:795`)
filters on work status, world state, `client_id` (tenant isolation, I5) and
optionally `world_id`. **There is no session predicate anywhere in it** — a
claim is scoped by client and worker, never to the session's own worlds.
Two wording fixes: it is now **five** `/v2/work` routes, not four
(`GET /v2/work/{work_id}/attestation` was added by v6 and is **missing from the
strict-gate parametrization** in `test_sfe_strict_and_completion.py` — add it);
and the addressed half is advisory-only on M1, so it is CODE_FIXED and DEPLOYED
but **not LIVE-EXERCISED**.

### D4-4  Ablation — v6 shipped the primitive, NOT the enforcement
The old text said closing this needs "an executor attestation binding the
applied component to the work result." **That attestation now exists**
(`executed_config_hash` vs sealed `spec_hash`), and `NO_EFFECTIVE_INTERVENTION`
/ `INTERVENTION_NOT_APPLIED` catch the inert case over the three engine-visible
fork fields. **It is still not enforcement:** M1 runs `warn`, so a contradicted
ablation is a non-blocking finding on one response. Closing it needs the
operator to move M1 to `--science-profile strict`, executors to actually send
the field, and a qualification run. Until then this is a *detectable*
disagreement, not a *prevented* one.

### D4-5  Untested — and the surface GREW
* **Terminal-state sweep:** "33 session-scoped routes" is wrong. There are now
  **46 `/v2` routes, 40 carrying `Depends(session_ctx)`**, 6 unscoped. v6 added
  7 to the unswept surface, so **this item got bigger, not smaller.**
* **Restart durability under load** — needs an operator window; the restart
  procedure is itself hazardous (a stop can orphan the process tree while the
  OLD build keeps serving; has happened twice).
* **Session key TTL / rotation:** stated accurately — **keys have no expiry and
  no rotation path at all.** That is a design gap, not merely an untested one.
* Clone hazard is covered by `test_K`; drop it from this list.

### D4-6 — **DELETED 2026-09-06.** See the closure record.

### D4-7  C3e is a behaviour change in ADVISORY mode
A completion replayed with a DIFFERENT result now returns 409 where it returned
200 — and v6 added a second unconditional 409 for a replay carrying a different
**attestation**. Any instrument written against the old behaviour, including
Harmonia's T2, needs its expectation updated. Engine side is CODE_FIXED and
DEPLOYED; blocked on Harmonia confirming T2.

---

## D5 — Harmonia's boundary campaign: what is ENGINE work

### D5-1  Pre-registration is sealable — and v6 made it first-class
Verified pre-v6 and still true: a manifest in the spec is sealed by `spec_hash`,
recovers byte-identical, recomputes locally, and is order-proved by
`committed_seq`. **Correction to the old wording "no engine change":** v6 shipped
a first-class sealed manifest of the same shape — `families.manifest_hash`,
sealed at creation and immutable (`store.py:335-346`, `runtime.py:2429-2470`).
**Honest limit unchanged: the engine SEALS the declaration and does NOT check
that the analysis obeyed it.** Detectable by audit, not prevented.

### D5-2  The blob_hash player-identity habit — NEVER RELAYED
A player placed as an artifact is content-addressed; `blob_hash` is
world-independent, so two arms that are the same policy under two names carry an
IDENTICAL hash — the duplicate that produced p=0.036 against itself is catchable
today with no engine change. **It says "worth telling her before SE-1" and I
never told her.** The v6 packet mentions `player_identity_hash` but not this.
Open, trivial, entirely mine.

### D5-3  Executor attestation (C-1) — BUILT AND SHIPPED
**The old instruction "Do not build it unasked; the client-side form is
available now" is now false and would mislead the next reader.** It was built.

Typed first-class fields: `ATTESTATION_FIELDS` (`runtime.py:125-126`), columns
(`store.py:160-163`), `_normalize_attestation` accepting `executed_config` OR
`executed_config_hash` and never both (`runtime.py:198-226`). The engine does
what the old item called merely "nicer": it emits `NO_EXECUTION_ATTESTATION` /
`CONFIG_DIVERGENCE` (`runtime.py:970-994`) and under `strict` **refuses** a
completion that omits or contradicts the attestation. Read-back at
`GET /v2/work/{work_id}/attestation`; client at `client.py:312-332`.

**Residue, and it is the whole residue:** M1 reports `science_profile=warn`, so
**the refusal branch is CODE_FIXED only and has never run on the live service**,
and nobody outside me has qualified it.

### D5-4  Undeclared co-intervention (S2 case 6) — still unclosable
Declared A, ran A plus an undeclared C: the record is BYTE-IDENTICAL to the
honest run. v6 does not touch this and could not. **This is a missing
MEASUREMENT, not a missing check** — the engine cannot know what it was never
told. Recorded so nobody files it as an engine bug.

### D5-5  Split: engine half SHIPPED, the rest is theirs
The old blanket "not mine" is stale — three of four now have a shipped engine
half, warn-only on M1 and unqualified:
* **unit-of-analysis** — declared *and verified by counting* (`runtime.py:1559`,
  read at `GET …/experiments/{eid}/analysis`);
* **comparison family** — first-class container with
  `FAMILY_EXTENT_DIVERGENCE` / `MULTIPLE_SELECTED` /
  `SELECTION_WITHOUT_ALTERNATIVES` (`runtime.py:2591-2619`);
* **effect floors** — `relevance_floor` stored on the claim (`store.py:376`).

**Still wholly theirs:** multiplicity correction, power and equivalence-test
validity, and player-class breadth (only stochastic scalar-emitting policies
have ever been exercised — nothing stateful, nothing learning).

---

## D6 — "What else fails in the direction of looking good?"

**v6 fixed none of these.** Two had text that v6 made actively wrong, in the
direction of *understating* the engine — corrected below.

### D6-1  Every epistemic signal stays green on a contradicted execution
**Reproduced 2026-09-06 at live config** (warn/advisory), on code byte-identical
to the deployed build: spec `{"arm":"arm-A"}`, executor completes attesting
`{"arm":"arm-NOT-A"}` → HTTP 200, findings `['CONFIG_DIVERGENCE']`, status
COMPLETED; the observation binds that `work_id` → `evidence_class =
ENGINE_WORK_RESULT`; and

    observations_engine_attested          1
    observations_prospectively_predicted  1
    claims_surviving                      1

`world_status` returns **no key** containing science/finding/divergence.

**Delete the old clause "the engine never reads the spec against the result, by
design" — that is no longer true.** v6 *does* compare `executed_config_hash`
against `spec_hash` (`runtime.py:967-994`) and
`GET /v2/work/{id}/attestation` returns `config_match: false`. But
`evidence_class` is set from (same world, COMPLETED, enqueued for this
experiment) **only** (`runtime.py:1745`) and never reads the attestation;
`epistemic_accounting` (`runtime.py:3018-3025`) counts those columns verbatim
and is unchanged by v6.

**So the failure is intact and now has a sharper shape: the engine knows the run
was contradicted and every epistemic counter still says it was fine.**
*Closes only when* either M1 runs `--science-profile strict` (LIVE_VERIFIED), or
the three counters and `world_status` are made divergence-aware. This stays an
open **scientific** failure, not a closed implementation item.

### D6-2  `ledger_integrity_ok: true` on deliberate garbage
Unchanged. It verifies the HASH CHAIN, never the CONTENTS. The phrase most
likely to be quoted as assurance in a packet, and it assures only that nothing
was tampered with after the fact.

### D6-3  A budget that is REPORTED, looks tracked, and caps nothing
Unchanged. `limit 2, enforcement measured`; attempted 6; **accepted 6**;
`resources` reports `consumed: {experiments: 6}`, `exhausted: false`.
`measured` is the DEFAULT, so this is the path of least resistance.

### D6-4  Event count is not a count of distinct things
Unchanged and still measured: 20 identical reposts → 20 HTTP 200s **and 20
`ARTIFACT_CREATED` events**, while the knowledge frontier correctly reports
**1** distinct artifact. The inflation is in the LEDGER, not the response. An
analyst counting `ARTIFACT_CREATED` as n gets 20x. This is the unit-of-analysis
defect one layer down; v6's unit counting does **not** cover event rows.

### D6-5  Advisory enforcement is itself a looks-good failure
**Measured again 2026-09-06 and INTACT IN-BAND.** With the session header
removed against a world owned by a bound session: `GET …/status` → 200,
`POST …/hypotheses` → 200. Response headers containing `sess`/`affin`: none.
Body keys: none. World events mentioning `SESSION_ABSENT_ALLOWED`: **0**.
The verdict is built at `api.py:467` and every route binds it as `_sess` —
underscore-prefixed, never read, so it is never echoed.

Two corrections: "nothing surfaces it" is now half-wrong — v6 put
`session_enforcement` on `/v2/version`, so the **mode** is discoverable in one
call. And "every unkeyed request is counted" overstates it: it is logged to
`sfe.affinity` at WARNING — **nothing durable, nothing queryable**.
**Adding a field to a metadata endpoint is not a warning, let alone a fix.** A
running campaign still cannot tell that its requests are unprotected.

---

## D7 — v6 residue: what shipped partially, and what was declined

D7/D8/D9 were three overlapping candidate lists. v6 (`869df1fa1`) closed the
dependency they shared and much of their content. What survives is consolidated
here; everything closed is in the closure record with its commit.

### D7-1  Experimental-unit provenance — the aggregate signal exists, unprompted
`_verify_units` (`runtime.py:2814-2862`) counts distinct units under a declared
key. **The independence signal is a special case and it works:** a fork inherits
its parent's `seed_root` (`runtime.py:2307`), so `unit_of_analysis="seed_root"`
collapses seven fork children of one parent to `verified_n = 1` — exactly the S3
signal, deterministically, with no statistics.
**Residue:** it is opt-in. There is no unprompted lineage-independence read; the
signal only appears if someone declares a `source_set`.

### D7-2  Replay-strength declaration (L0-L4) — nothing built
Zero hits for `replay_level` across `sfe/` and `tests/`; no declared-level field,
no two-execution comparison route, no achieved-level report. Ingredients all
present and unassembled: sealed spec recovery (`runtime.py:1320-1343`),
`result_hash` for L1 terminal outcome, the event chain for L0 sequence.
**Caveat retained: if only L0/L1 are computable, say so rather than implying all
five.**

### D7-3  Degenerate-replication detection — DECLINED, with the reason
Moved out of "genuinely buildable". `docs/SCIENTIFIC_PROVENANCE.md` §10 records
why: a detector firing on identical content hashes catches a **converging** state
leak and misses a leaker that does not converge — correlated-but-not-identical
outcomes are visible only to variance or correlation, which is across the
boundary. **The honest response is to state the detector's domain, not to reach
for variance.** Re-open only by re-arguing against that reason.

### D7-4  Machine-readable warning surface — partly shipped, not queryable
A typed vocabulary did ship: 11 finding codes, returned as
`science.profile_findings` and **sealed into the chain** at `runtime.py:1017`
(work), `:2364` (fork), `:2587` (family), `:2753` (claim).
**Not done:** `record_failure` (`runtime.py:1853`) still takes free-text
`failure_type` with no vocabulary constant anywhere, and **findings are not
queryable** — no route exposes them, so they are recoverable only by scanning
event payloads.

### D7-5  Replicate / state-isolation contract — 1 of 3 steps shipped
Step 2 shipped: the executor **attests** an entry-state hash (`store.py:161`,
`api.py:241-243`, persisted `runtime.py:994-1005`, read at
`GET /v2/work/{id}/attestation`). Steps 1 and 3 did not: no `state_scope`, no
`independence_required`, no `INDEPENDENCE_CONTRACT_VIOLATED` anywhere.

### D7-6  The S3 Q4 rider — binding on D7-5 step 3
**Must ship with step 3, and step 3 has not shipped.** The engine currently
returns `entry_state_hash` entirely uninterpreted (`runtime.py:2916`;
`config_match` is the only derived verdict), which is the *safe* state — the
blind spot is untriggered rather than handled, and **no route says "independence
verified"**. When step 3 is built: a CONVERGED leaker enters every world from
the same fixed point, so its entry hashes are indistinguishable from an honest
reset. Any check must ship with that limit stated.

### D7-7  Fixed-vs-factor declaration — dependency now satisfied
Nothing built: no `declared_fixed` / `fixed_factors` anywhere. The nearest
machinery is `_intervention_finding` (`runtime.py:229-275`), which is
parent→child across ONE fork and checks the *opposite* property over only three
engine-visible fields. **Nothing checks that a declared-FIXED value stayed
constant across a family.** The old note "depends on the family work" is stale —
**buildable now against `families`/`family_members`.**

### D7-8  R10 measurement-regime detection — recording shipped, DETECTION did not
The recording half shipped under a different name: `measurement_identity_hash`
(`api.py:245`, `store.py:163`, written `runtime.py:998`/`:1004`, echoed by
`work_attestation`). **`measurement_process_hash` has zero hits, and there is no
comparison anywhere** — nothing detects that two runs with different measurement
regimes are being compared as identical conditions. That comparison was the
point of the item; only the field landed. Relates to D1-3: an opaque hash still
cannot say *what* was measured.

### D7-9  `ObservationCreate.replication` still ships with a misleading name
*(merges the former D8-1 and D10-2, which were the same ask filed twice.)*
`api.py:139` `replication: bool = False`. F3 semantics are correct and untouched
(`runtime.py:1780-1786`): it means "a SECOND observation bound to a prediction, a
retest that never re-adjudicates the original". It does **not** mean
"independently replicated", and the name invites exactly that misreading.
v6's compositional `ClaimCreate.replication` dict now sits beside it in the same
module (`api.py:290`), which makes the collision worse, not better.
**Renaming is a contract change — deliberately deferred, not forgotten.**
Note the old prescription "a declared STRING plus dimensions" was only half
shipped: the dimensions landed as six closed booleans, the STRING level did not.

### D7-10  Estimator identity — v6 ANSWERED it with `spec_hash`; is that enough?
`grep -rn estimator sfe/ tests/` returns **exactly one line in the whole
engine** — `runtime.py:2373`, a boundary comment, not a field. v6 did not
decline this; it answered it by saying estimator identity belongs inside the
analysis `spec`, where `spec_hash` seals it.
**State why that may be insufficient rather than leaving it implied:**
whole-spec granularity defeats cross-analysis comparison (two analyses differing
only in estimator produce two unrelated hashes), and the declaration is
optional. Harmonia's measurement stands: a trimmed mean standardised by a
winsorised sd overstates a heavy-tailed effect **3x with no selection in play**.

### D7-11  The boundary rule's missing clause — never written
Agreed and never landed. `docs/SCIENTIFIC_PROVENANCE.md` §1 states only the
compare/count/contain boundary; grep for the clause returns zero hits anywhere
except this file. **Trigger is now available:** write it into
SCIENTIFIC_PROVENANCE §1 — *a scientific rule that has survived only one
estimator and one outcome distribution is L1 evidence about that rule and must
not be encoded* — citing the measured instance, instead of leaving it an
assertion in a TODO.

### D7-12  The prohibitions HELD — verified, keep them
No multiplicity correction, no null calibration, no stopping rule, no power
threshold, no equivalence judgement anywhere in `sfe/`.
`NO_REPLICATION_DECLARED` is emitted but deliberately **not** in
`_STRICT_BLOCKING_CLAIM`, so replication is never mandatory in any profile.
**Residue:** of the six fields the operator asked to be *exposed and not
enforced*, only `relevance_floor` is a first-class field. `design_effect`,
`target_power`, `estimated_power`, `promotion_rule` and `estimator` exist only
inside freeform `spec`.

---

## D10 — v6 shipped 2026-09-05 (`869df1fa1`..`088591ab3`)

Full record: `SerendipityFoundryEngine/docs/SCIENTIFIC_PROVENANCE.md`.
Residue is tracked as D7-1..D7-12 and D11 above, not duplicated here.

**Open after the release, still true:**
1. `source_commit` names the deployment tree's HEAD at process start and will
   read `4d315bafe` until the next restart. `engine_source_hash` is
   authoritative; `deploy/verify_deploy.py` proves the relationship. → D11.
2. M2 runs a build two schema versions behind → D4-1.
3. A **second organism** — still none. Vivarium is a second *client*, not a
   second organism. Everything in v6 is organism-independent (facts about
   records, not dynamics), so nothing here gates one and the substrate can run
   one today.

---

## D12 — Three automated consumers on one engine (NEW, 2026-09-06)

Archaeon (producer) and Vivarium (executor) join Harmonia on M1. Audited both
against the engine and the live ledger; 61 findings, every high-impact one
adversarially re-verified. Their side is written up in
`integration/SFE_CONTRACT_FOR_ARCHAEON_AND_VIVARIUM.md`. What follows is only
what is MINE.

**Ground truth that reframed the work:** Vivarium is already live and already
adopted v6 — 14 runs, all binding `work_id`, all attesting
`executed_config_hash`, one day after it shipped. Archaeon has not connected.

### D12-1  FIXED and deployed — the write lock on every request (`e307d6e5f`)
`Store.initialize()` took `BEGIN IMMEDIATE` unconditionally, and
`get_foundry()` builds a Foundry per request, so **every** request — including
unauthenticated read-only ones — queued behind every writer, to re-read one row
of `meta`. Measured live: `GET /v2/version` **22.8s and 17.6s** against a 30s
busy timeout while `GET /v2/openapi.json` (same process, same TLS, no db) held
18ms. Now 0.019s worst case. WAL's concurrent readers were being thrown away on
the first line of every request; with three consumers this was heading for the
timeout, not for slow.

### D12-2  FIXED and deployed — claims usable by a machine (`d0bc13981`)
`CLAIM_CITES_UNVERIFIED_ANALYSIS`: a claim citing an analysis whose sealed
verification recorded `verified_n=0`, or a `declared_n` the engine's own count
contradicts, produced a clean SUPPORTED claim. **This is the default path for a
programmatic producer**, not an edge case — cross-tenant sources resolve to
`unresolved` by the anti-oracle rule, so such an analysis counts nothing.
And claim findings were write-once/read-never; `GET /v2/claims/{id}` now returns
what was sealed at creation, with the build hash that computed it.

### D12-3  FIXED — client gaps (`d0bc13981`)
`create_world` could not set `require_attestation`, so the fail-closed evidence
guard was unreachable from the shipped library. `audit_envelope` and
`verify_anchor` had no methods at all — Vivarium reaches the envelope through
the private transport with its own `noqa:SLF001`.

### D12-4  Routes an automated consumer needs and does not have — OPEN
Measured, not inferred: `GET /v2/sessions` **405** (a restarted producer cannot
re-discover its sessions; the key is shown once), `GET /v2/work` **404** (a
restarted executor cannot enumerate its orphaned work), `GET /v2/events`
**404** (the global ledger has no read path), `/v2/measurements` **404** (see
D1-3). **Do not build these speculatively** — the contract doc asks both tools
which they actually need.

### D12-5  Attestation is unreachable outside the work queue — OPEN
It writes only through `POST /v2/work/{id}/complete`. Any result produced out of
band — a human run, a GPU batch, an external harness, Archaeon aggregating what
it did not execute — cannot record its executed side and is fossilized
`CLIENT_ASSERTED` with no way to say what config produced it. Vivarium uses the
queue, so this blocks nobody today.

### D12-6  No rate limit, quota or concurrency cap anywhere — OPEN
Confirmed: nothing in `sfe/*.py` or `serve.py`, and `uvicorn.run` sets no
`limit_concurrency`. The only bounds are anyio's 40-thread pool and the 30s
busy timeout, neither per-client. A client's own `enforceable` budget is the
sole backstop, and the default `measured` caps nothing (D6-3). **D12-1 removed
the sharpest edge of this** — reads no longer contend — but a runaway automated
producer is still bounded by nothing.

### D12-7  D6-1 is now load-bearing, not theoretical — OPEN, sharper
With a human, "the engine knows the run was contradicted and every epistemic
counter still reads green" was a catalogued oddity. With an automated executor
**nobody reads the completion response unless the tool is made to**, and
Vivarium does not check `science.profile_findings` today. The contract doc makes
that the single most important instruction for them; the engine-side fix is
still to make `evidence_class` or the counters divergence-aware, or to run M1
under `strict`.

---

## CLOSURE RECORD — deleted 2026-09-06, with the commit that closed each

Kept as a list of *names and citations only*, so nobody re-files them. The rule
is that closed items leave this file; this record is the receipt.

| Item | Closed by | Note |
|---|---|---|
| **D0** (M2 deploy, live bar, M1 decision) | superseded | M1 is now on v6/schema 6; D0-3's "M1 remains on `ce79401b`/schema 3" is long dead. |
| **D4-6** battery 23 vs 24 | *no code change* | **Never a disagreement.** `sfe_battery.py:152` guards S1c behind `--expect-source-hash`: 23 without, 24 with. Documented at `HARMONIA_FIRST_INTEGRATION.md:109`. A docs-reading gap on both sides. **Quote the battery total with its flag state**, or it gets re-litigated. |
| **R-M-2** verify-anchor in fossil validation | PEW `201106edb` | `sfe_anchor_verified` no longer pinned; `closure_results.json` 19/19, `lineage_results.json` 14/14, gates D/E PASS. |
| **R-M-3** record `engine_instance_id` | PEW `ec49be22d` | **Attribute correctly: closed by PEW reading the id off the VERIFY RESPONSE (`ew/closure.py:170-174`), NOT by v6 putting it on `/v2/version`** — that was a discovery convenience and is not what R-M-3 asked for. Live gate C PASS. |
| **D7 pre-registration manifest hashing** | `869df1fa1` | Already true pre-v6; v6 added `families.manifest_hash` of the same shape. Guard now lives in SCIENTIFIC_PROVENANCE §4. |
| **D7 cross-world primitive** ("the dependency that matters") | `869df1fa1` | Closed by a **membership container with roles** (`families`/`family_members`), *not* the src/dst/relation lineage edge the item named. `lineage_edges` is unchanged and still world-scoped — if a true cross-world *edge* is ever wanted, it is a new item. |
| **D8 `SUCCESSFUL_NEGATIVE`** | `869df1fa1` | Now a claim status with a CHECK constraint, and a missing `relevance_floor` is rejected in **every** profile. |
| **D8 config hashes** | partial | 2 of 3 exist (`spec_hash` requested, `executed_config_hash` attested). **`analysis_config_hash` was never implemented** → tracked as D7-10. |
| **D8 build order** | spent | Steps 1 and 3 shipped in the same release, contradicting the sequencing premise; step 2 was routed around (see the cross-world note above); step 4's precondition was dissolved rather than met. Superseded by the residue list in D7. |

---

## Standing discipline for whoever picks this up

1. **Measure before writing it down.** Three items in this file asserted a live
   fact nobody had checked — M2 "down", the battery discrepancy, and "the engine
   never reads the spec against the result". All three were wrong, and one of
   them went out in a packet.
2. **A revival trigger that has fired is not deferred work.** D2-3's gate was
   violated live and nobody noticed; D2-6's fired and the right answer is still
   not to delete anything.
3. **Do not confuse a warning with a fix,** or a field on a metadata endpoint
   with a signal in band. See D6-1 and D6-5.
4. **Attribute closures to whoever actually closed them.** R-M-3 was PEW's, not
   v6's.
5. **`CODE_FIXED != SERVICE_DEPLOYED != LIVE_VERIFIED != QUALIFIED.`** Most of
   v6 is DEPLOYED and none of it is QUALIFIED by anyone but me.
