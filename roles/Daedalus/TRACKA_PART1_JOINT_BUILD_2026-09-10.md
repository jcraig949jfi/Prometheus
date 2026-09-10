# Track A part 1 — one development build, one joint receipt

**Daedalus, 2026-09-10.** For the operator's review. **Nothing was deployed and
no service was restarted.** Production (M1, `192.168.1.202:8811`) is still
schema 7 on `sha256:084f951f…`, untouched.

## What was actually run together

Daedalus's iteration-1 work and Vivarium's were made on two tested
configurations that had never been run together. They now have been, once, on
one build:

| | |
|---|---|
| build | `sha256:eb3bbadc083c48d56b5ef8181ee2e627e5b11bce8ab03e751d551a4fe1cbd564` |
| schema | 8 |
| tree | `07b5b05a7` on `origin/main`; the build files were last touched at `07b5b05a7` |
| dev ledger | `eng_51b56ae45788ac7c7dbcad9f` — a development database, not production. It is minted per database, so a fresh run of the receipt mints a fresh one; that the build hash does **not** move with it is the point of keeping the two identities apart. |
| receipt | `SerendipityFoundry/SerendipityFoundryEngine/deploy/TRACKA_JOINT_RECEIPT.json` |
| result | **PASS**, 29 of 29 checks |

The receipt runs a real engine process over HTTP with the shipped `sfclient`,
Vivarium's shipped `viv.preflight` loader and `viv.artifact_probe` kind, and
Archaeon's shipped `archaeon.producer.costs`. Nothing is mocked; every module
is imported from the tree. `SerendipityFoundry/SerendipityFoundryEngine/deploy/trackA_joint_receipt.py` contains only the
scenario.

```
python deploy/trackA_joint_receipt.py --json
```

## Item 1 — one build

Both counterparties' components were already on `origin/main`
(`vivarium/viv/artifact_probe.py`, `archaeon/producer/costs.py`); the vendored
copy of `herakles/evca` under `vivarium/` is **already absent** and
`viv/ca_density.py` imports the canonical `herakles.evca`. What was missing was
a tree that had all of it *and* my Track A client change at the same time —
`F:/Prometheus` is on `vivarium/v0-2026-09-05`, 180 commits behind main, and
the v6/v7/v8 source exists there only as uncommitted modifications. The build
above is a worktree cut from `origin/main`, which is the first place the two
halves have coexisted.

Engine suite on that build: **344 passed**.

## Item 2 — the principal, and one name for one field

`sfclient.register()` now retains the engine-issued `client_id` alongside the
token. A client built from a bare token reports `client_id is None` rather than
deriving a substitute, because a fabricated principal would be wrong in exactly
the records that name it — a read grant, a cost event's attribution, a
reconciliation row. `__repr__` names the principal and never the credential. No
credential appears in the receipt.

`expected_blob_hash` is now the primary name on the **read** path as well as
the write path, with `expected_digest` kept as the shipped alias; passing both
with different values raises rather than silently picking one.

Vivarium's half — the loader's preflight using the engine-side gate — is
**not done**, and is finding TRACKA-PREFLIGHT-1 below.

## Item 3 — the joint receipt

A producer sealed a `failure_input_set` (root + a declared dependency, so the
closure is real) under the write-side digest gate; the write gate was shown to
store nothing when the bytes disagree. Then:

- **Attempt 1** reserved the enforceable `artifact_bytes` counter *before each
  fetch* — Vivarium's `Preflight.debit` hook wired straight to
  `reserve_budget` — resolved the closure through the engine, and was then
  **interrupted**. Its retrieval is still charged: the bytes moved, and
  releasing would claim the fetch never happened.
- **Attempt 2** revalidated from step 1 (0 cache hits, 2 fresh engine fetches),
  reserved `cpu_s` before execution, ran `artifact_probe_v1`, and settled.
- A settled reservation refused a second charge (409). A retried reserve under
  the same idem key returned the **original** reservation.
- Totals: `artifact_bytes 1042` — exactly twice the closure, because the retry
  really did fetch twice — `engine_fetches 4`, `peak_memory_bytes` counted 5
  times as **unavailable** and never summed, `gpu_s` likewise.
- Enforcement classes came from the **limit**, not the caller: the cost events
  carry `peak_memory_bytes → measured` because the world's budget declares it
  so, not because the executor said so.
- Publication under an idem key returned the same artifact id twice.
  `recorded_in_sfe: true`; `indexed_in_pew: null` — **not run**, see below.
- Counterfactual attribution under a **reuse horizon of 2, declared before the
  attempts ran**: the shared source build is charged once physically and
  attributed at half to the arm that uses it, zero to the arm that rebuilds;
  an unavailable producer quantity stays unavailable in the attribution.

### Reconciliation, on `(attempt_id, stage)`

```
matched        : []
producer_only  : attempt-2|transfer, source-build|generation
executor_only  : attempt-1|retrieval, attempt-2|execution, attempt-2|retrieval
engine_side    : attempt-1|retrieval, attempt-2|execution, attempt-2|retrieval
                 (each row says whether the producer / executor carries it)
```

`matched` is empty, and on this run that is the correct answer: the producer
paid for generation and transfer, the executor and the engine paid for
retrieval and execution. So that an empty set cannot be confused with a broken
join, the receipt also runs the same join over synthetic keys as a labelled
control and shows it matching.

### Rejection fixtures

Of the fifteen rejection classes in `viv/artifacts.py`, exactly **four** are
decided by the engine, and only those could have had their guarantee changed by
this integration. All four were re-run live and all four fired:
`ARTIFACT_ABSENT`, `ARTIFACT_UNAUTHORIZED_WORLD`, `ARTIFACT_DIGEST_MISMATCH`,
`ARTIFACT_SIZE_MISMATCH`. The digest fixture needed a decoy of the root's exact
byte length — preflight checks size before the hash, so a shorter substitute is
caught as a size mismatch and the hash is never reached, which would have made
the digest fixture a second size test under the wrong name.

The engine's own read gate was asked the same two questions directly: wrong
digest → 422 no bytes, wrong size → 422 no bytes, right digest → 200. And a
correct digest still authorizes nothing: a foreign client naming the exact
digest got 403.

The other eleven classes are contract, codec, interface, closure and limit
checks the client makes without the engine. Integration did not change their
guarantee, so they are covered by `vivarium/tests/test_h0h5_artifacts.py`
rather than re-run here.

## Item 4 — the candidate pin

`SerendipityFoundry/SerendipityFoundryEngine/deploy/CANDIDATE_BUILD.json` refreshed. Six files change against the deployed
pin (`api.py`, `ids.py`, `runtime.py`, `store.py`, `serve.py`, `client.py`).
`SerendipityFoundry/SerendipityFoundryEngine/deploy/prepare_deployment.py` now emits the **four identities as distinct
things with an explicit mapping**:

- `git_commit` names a **tree**, best-effort — not proof it reproduces the
  build, and `/v2/version`'s `source_commit` has named a commit that could not.
  HEAD is recorded alongside `build_files_commit`, the commit that last touched
  the pinned files: HEAD goes stale the moment anyone commits anything at all,
  including work that touches none of this, and a pin whose only commit field
  drifts for unrelated reasons is the same defect in miniature.
- `engine_source_hash` names the **build** and is authoritative.
- `schema_version` names the **shape of the ledger** and moves only forward.
- `engine_instance_id` names the **ledger itself**; a code deploy does not
  change it, and a changed value after a deploy means the service was pointed
  at a different database.

Mapping: commit → build is many-to-one *and not guaranteed*; build → schema is
one-to-one (the constant lives inside the hashed source); schema and instance
id are independent; instance id and build are independent — which is precisely
what allows this receipt to be taken on a development ledger at all.

**Rollback is code and data.** 7 → 8 crosses a migration, so a code-only revert
does not work: schema 8 data under a schema 7 engine is refused at startup
(`sfe/store.py`, *"refusing to run"*). The snapshot is the rollback; take it
with `VACUUM INTO` and the service stopped. `engine_instance_id` must be
identical before and after in both directions.

### Conformance pin — already stale, independently of this candidate

`roles/Harmonia/contracts/sfe_contract.json` pins
`sha256:2f42e87f…` / **schema 6**. The **live** service is
`sha256:084f951f…` / **schema 7**. The contract has therefore been stale since
the v7 deploy, not as of this candidate. `conformance_check.py` is fail-closed
on an exact hash comparison, so regenerating it belongs in the same window as
any deploy — and is overdue now regardless.

## Not run

- **`indexed_in_pew`** — PEW indexing needs a running PEW service and
  `viv.pew.PewClient`, which is Vivarium's component and is not part of this
  development build. Reported as `null`, kept as a field separate from
  `recorded_in_sfe`: an index that failed to publish has not unmade a
  measurement, and one that published has not made one.
- **Vivarium's own test suite** — `vivarium/tests/conftest.py` imports
  `viv.db`, which imports `psycopg2`, which is not installed in any venv
  available here. Command attempted:
  `python -m pytest vivarium/tests -q` from `vivarium/`; result
  `ModuleNotFoundError: No module named 'psycopg2'` at collection. Their
  preflight and probe modules **were** exercised directly by the joint receipt;
  it is the Postgres-backed fixtures that did not run.

## Findings for other seats — routed through the operator, not fixed here

**TRACKA-PREFLIGHT-1 — Vivarium.** `viv/preflight.py:SfeResolver.resolve()`
calls `artifact_content(world, aid)` with no `expected_blob_hash`, so the
digest is compared in the client at `preflight.py:341`, after the bytes have
already been served. The engine-side gate now exists on the read path and
returns 422 with no bytes. Passing the sealed digest and `expected_bytes` moves
the check to the engine; the client-side comparison then becomes defence in
depth over the one span the engine cannot see. This is the outstanding half of
Track A item 2.

**TRACKA-DEBIT-1 — Vivarium.** `Preflight.debit(resource, amount)` does not
carry the artifact being paid for, so the strongest idempotency key an
integrator can build is the ordinal of the fetch within the attempt (the
receipt uses one, and says so). Widening the hook to carry the digest would let
the reservation be keyed on the act rather than on its position.

**TRACKA-VECTOR-1 — Archaeon.** *The sharpest fact about the reconciliation:
a producer resource entry cannot be recorded by the engine at all.* Posted live
to `/v2/worlds/{id}/cost-events`, an entry straight out of `costs.Meter` is
refused three times in sequence, and the receipt peels them one at a time:

```
as Archaeon emits it      422   enforcement_class is an extra key
minus enforcement_class   422   unknown measurement method: 'time.perf_counter delta'
plus method -> clock      422   unknown attribution scope: 'producer'
plus scope -> attempt     200
```

Two of these are vocabulary — `method` must be one of
`counter|clock|sampler|declared|derived`, `scope` one of
`attempt|job|campaign|shared`. **The first is not a rename.** The engine
resolves the enforcement class from the *limit* and stamps it onto the entry
itself, exactly so a caller cannot declare its own spend exempt from a cap it
was given; sending the field under the engine's spelling would be refused for
the same reason. It has to be **stripped on the way in and read back off the
response** — and it is refused twice over, by the request model
(`sfe/api.py:52-53`, `extra="forbid"`) and independently by the runtime's
five-name allowlist.

The prose those `method` strings carry today — *which* counter, *whose*
process — is real provenance that the five-name set cannot hold. `refs` is the
free-form slot on `record_cost_event` and is where it should go, rather than
being dropped in the translation.

**TRACKA-RECON-1 — Archaeon.** `archaeon/producer/costs.py:reconcile()` joins
on `attempt_id` alone and returns the hardcoded string
`"engine_side": "absent (Daedalus C4-3)"`. Engine-side cost events now exist —
`COST_EVENT_RECORDED` sealed in the world's own hash chain under schema 8 — and
this run produced five of them. Called verbatim on this run's data, that
function reports `matched: ["attempt-2"]`, which joins the producer's
*transfer* to the executor's *retrieval* and *execution*: a coincidence of
attempt ids across different stages, not an agreement about any act.

**TRACKA-RECON-2 — Archaeon and Vivarium jointly.** The producer names the act
`transfer` where the executor and the engine name it `retrieval`. Both
vocabularies are internally consistent and neither is wrong, but a
`(attempt_id, stage)` join therefore reports one physical byte movement as both
producer-only and executor-only. One shared stage name, or a declared mapping
between the two, is needed before any reconciliation can claim agreement.

## What this does not authorise

A deploy or a restart. The candidate pin exists so the operator can see what a
deploy would change before anything moves.
