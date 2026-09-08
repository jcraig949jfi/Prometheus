# VIVARIUM v0 — deliverable

Seat opened and v0 built 2026-09-05, on M1 / SKULLPORT.

---

## 1. What was built

A long-running Python service and its shared PostgreSQL queue, sitting between
Archaeon and the scientific record:

    Archaeon -> viv.research_experiment_queue -> VIVARIUM -> SFE -> PEW

* `vivarium/migrations/001_vivarium_queue.sql` — the queue, the append-only
  event log, the worker heartbeat, and the state machine **as database
  objects** (constraints, a partial unique index, two plpgsql triggers).
* `vivarium/viv/spec.py` — canonical spec hashing, byte-identical to SFE's
  `sfe/ids.py::content_hash`, plus strict total validation. Unknown key =
  rejected. Nothing is ever defaulted in: validation returns the original spec
  or a list of reasons, never a repaired spec.
* `vivarium/viv/queue.py` — the legal moves, each with its event row, in the
  caller's transaction.
* `vivarium/viv/runner.py` — the SFE adapter, driving the engine's own
  published `/v2` REST API through the repo's stdlib client. No engine
  semantics were modified; no SFE file was touched.
* `vivarium/viv/executors.py` — `noop_v0`, and `evaluate_bitstring`, which
  delegates to the engine's own reference executor rather than reimplementing
  the landscape.
* `vivarium/viv/pew.py` — the `pew.fossil.v2` write.
* `vivarium/viv/loop.py` — the service.
* `vivarium/viv/cli.py` — the status surface.
* `vivarium/tests/` — 37 tests, all against real PostgreSQL and (where
  applicable) the real engine.

Reused rather than rebuilt: the SFE stdlib client, the SFE reference executor,
the SFE audit-envelope and verify-anchor routes, the PEW fossil contract, and
evidence_wiki's existing shared-Postgres credential loader. No credential is
committed; `vivarium/config.json` holds non-secret defaults only, and
`config.local.json` is already covered by the repo `.gitignore`.

## 2. Database / schema changes

New schema `viv` in `prometheus_fire` (PostgreSQL 17.9 on M1). Nothing existing
was altered.

**`viv.research_experiment_queue`** — as specified, plus one generated column:

    active_singleton boolean GENERATED ALWAYS AS
        (CASE WHEN status IN ('claimed','running') THEN true ELSE NULL END) STORED

with `CREATE UNIQUE INDEX uq_req_single_active ON ... (active_singleton)`.
NULLs do not conflict in a unique index, so **at most one experiment can be
claimed-or-running globally, enforced by the database**. The v0 single-slot
rule is therefore a property of the schema, not of the loop — running the loop
twice by accident cannot double-run anything.

Other constraints: status enumeration; `spec_hash ~ '^sha256:[0-9a-f]{64}$'`;
`priority >= 0`. Indexes: `(priority, created_at) WHERE status='queued'`,
`(status, finished_at DESC)`, `(spec_hash)`.

**`viv.research_experiment_events`** — `event_id bigserial`, `experiment_id`,
`occurred_at`, `actor`, `event_type`, `payload jsonb`. A BEFORE UPDATE OR
DELETE trigger refuses both, so history cannot be tidied.

**`viv.worker_heartbeat`** — `worker_id`, `host`, `pid`, `started_at`,
`last_seen`, `current_experiment`, `build`. Deliberately separate from the
queue: "is Vivarium alive" and "is an experiment running" are different
questions, and conflating them is how a crashed worker looks busy.

**Trigger `trg_req_transition`** (BEFORE UPDATE on the queue) enforces:

* terminal rows (`completed`/`failed`/`cancelled`) are **frozen whole** — any
  UPDATE is refused, not just a status change;
* `experiment_spec`, `spec_hash`, `created_at`, `created_by`, `source_reason`,
  `source_evidence` are immutable for the row's whole life;
* only the legal transition graph below is accepted.

The migration is idempotent and takes a `{schema}` placeholder, so the
identical DDL is applied to `viv` in production and to a throwaway schema in
tests. There is no second, test-only schema definition to drift.

## 3. The execution state machine, exactly

    queued  --claim_next-------------->  claimed
    queued  --cancel------------------>  cancelled          (terminal)
    claimed --execution begins-------->  running
    claimed --validation/setup fails->   failed             (terminal)
    running --result recorded-------->   completed          (terminal)
    running --execution fails-------->   failed             (terminal)

Nothing else is legal. Terminal is terminal.

Per cycle:

1. heartbeat.
2. `active()` — if any row is claimed or running, do nothing. (v0 = one
   globally.)
3. `claim_next(worker_id)`, one statement:

       WITH nxt AS (SELECT experiment_id FROM viv.research_experiment_queue
                     WHERE status='queued'
                       AND (not_before IS NULL OR not_before <= now())
                     ORDER BY priority ASC, created_at ASC
                     FOR UPDATE SKIP LOCKED LIMIT 1)
       UPDATE ... SET status='claimed', claimed_by=..., claimed_at=now()
         FROM nxt WHERE q.experiment_id = nxt.experiment_id RETURNING ...

   `SKIP LOCKED` is used although v0 permits one worker: the locking has to be
   right *before* a second worker exists. A loser of the race is refused by the
   unique index (`QueueBusy`), not by timing.
4. **While still `claimed`**, validate the spec and recompute its hash. A
   malformed or corrupted request fails here, having never been `running` — the
   distinction between "never executed" and "executed and failed" is the whole
   point of the state.
5. Drive SFE: session -> world -> start -> hypothesis -> prediction ->
   `experiment {commit:true, enqueue:true}`.
6. Read the seal back out of the **ledger** (audit envelope), not out of the
   create response, and require `sealed_spec_hash_in_ledger` *and*
   `spec_hash_recomputed` to equal the hash the queue admitted. This happens
   **before any work is claimed**, so a mis-sealed experiment never executes.
7. `mark_running` — at this boundary, the moment execution actually became
   possible. `sfe_experiment_id` is recorded here, so even a crash one
   millisecond later leaves the SFE identity attached to the row.
8. Claim the work item, execute the local executor, `complete` with
   `attestation={"executed_config": <the whole spec>}` — the engine hashes it
   with the same canonicalization that produced `spec_hash`, so a faithful
   executor matches by construction.
9. Apply the requester's pre-registered `outcome_rule` mechanically and record
   an observation bound to `work_id` (so the evidence is `ENGINE_WORK_RESULT`,
   not `CLIENT_ASSERTED`).
10. Resolve the anchoring ledger event; write the PEW fossil if the spec
    declared one; `mark_completed` with `sfe_experiment_id`, `pew_reference`
    and `result_summary`.
11. On any execution failure: `mark_failed` with the error preserved. **No
    retry, ever.** The row stays failed and visible.

Every transition appends an event in the same transaction.

## 4. How SFE and PEW identities are linked

| queue column | value | source |
|---|---|---|
| `spec_hash` | `sha256:<64hex>` | `viv/spec.py`, byte-identical to `sfe/ids.py::content_hash`; verified against the ledger's `sealed_spec_hash_in_ledger` before execution |
| `sfe_experiment_id` | `exp_<hex>` | written at `mark_running`, before any result exists |
| `pew_reference` | `pew:encounter/<encounter_id>:<run_id>` | written at `mark_completed` |
| `result_summary.run_id` | `exp_<hex>:wrk_<hex>` | PEW's execution identity, per `HARMONIA_PEW_WRITE_CONTRACT.md` |
| `result_summary.anchor` | `{sfe_event_id, sfe_entry_hash, sfe_event_seq}` | the ledger event that anchors the run |

**The anchor is `OBSERVATION_RECORDED`, not `WORK_COMPLETED`.** Both are real
events for the run, but PEW validates an anchor's class and shape and never its
ledger membership, so the only defence against naming a wrong-but-real event is
to choose one whose `refs` *bind* the assertion. `OBSERVATION_RECORDED` carries
`{exp_id, obs_id, pred_id}` and `POST /v2/audit/verify-anchor` can therefore
return `binds_exp_id` and `binds_obs_id`; `WORK_COMPLETED` carries only
`{work_id, result_hash}` and would pass a pure existence test. `WORK_COMPLETED`
is recorded beside it, never instead of it. An unresolved anchor is reported as
unresolved and blocks the PEW write; Vivarium never substitutes whichever
sha256-shaped string is at hand.

Vivarium also fills the `pew.fossil.v2` execution-lineage fields it actually
witnessed — `sfe_engine_instance_id`, `sfe_ledger_head_hash`, `sfe_session_id`,
`sfe_session_key_fp` — and never the session key itself, which is bearer-like.

Every *scientific* identity in a fossil (`encounter_id`, `players`,
`world_binding_id`) is declared by the requester in `spec.pew` and copied
through unchanged. Vivarium mints none of them. A spec with no `pew` block
writes no fossil and records `pew_write_skipped` — an absent link is stated,
never implied.

`python -m viv.cli trace` prints the mapping directly.

## 5. Tests and results

`vivarium/tests`, run against real PostgreSQL 17.9 and the live engine.
Full verbose output: `roles/Vivarium/TEST_RESULTS_2026-09-05.txt`.

    37 passed in 5.55s

Requested coverage, mapped:

| requirement | test |
|---|---|
| one queued experiment executes once | `test_one_queued_experiment_executes_once` |
| two execute serially | `test_two_queued_experiments_execute_serially` |
| concurrent claims do not double-run | `test_concurrent_claim_attempts_do_not_double_run`, `test_only_one_experiment_may_be_active_globally` |
| completed cannot be reclaimed | `test_completed_experiment_cannot_be_reclaimed_or_edited` |
| failed remains visible | `test_failed_experiment_remains_visible_and_is_not_retried`, `test_a_failure_is_preserved_and_the_queue_moves_on` |
| cancelled does not execute | `test_cancelled_experiment_does_not_execute`, `test_a_cancelled_experiment_is_never_executed` |
| `not_before` respected | `test_not_before_is_respected` |
| malformed spec fails visibly | `test_malformed_specifications_are_rejected_with_reasons`, `test_enqueue_refuses_a_malformed_specification`, `test_enqueue_reports_every_reason_a_spec_was_rejected` |
| same spec hashes identically | `test_same_specification_hashes_identically`, `test_key_order_does_not_change_the_hash` |
| changed spec hashes differently | `test_changed_specification_hashes_differently` |
| worker crash leaves reconstructable state | `test_worker_crash_leaves_reconstructable_state`, `test_a_second_worker_will_not_start_over_a_stranded_row` |

Beyond the list: hash parity with `sfe.ids.content_hash`; the DB refusing
illegal transitions and edits to a sealed request; the events table refusing
UPDATE and DELETE; a corrupted stored spec failing *before* `running`; release
never returning an item to `queued`; PEW failure fatal only when the spec says
so; and the CLI answering each operational question.

### Live evidence (real engine, real fossil service)

Engine: `schema_version 6`, `engine_instance_id eng_8a37a5d305969034d488c43e`,
`engine_source_hash sha256:7b46e2b5f868…`, `source_commit 4d315bafe…`.

Bring-up run, production schema `viv`:

    queue      e009b59e-8714-4dbb-be32-de2c377f9752
    spec_hash  sha256:1b2a64d7dbca34b52a44eed853ccf0a6731deca502896279453cfaf140f03fca
    SFE        exp_a76deb678c425d4b5767ef0c  in  wld_8a73fde58b05914c8db35ff4
    work       wrk_557e5fe49fc50326c91681a7
    obs        obs_fbd9d40ee2ae6a1b07d7c87b
    anchor     evt_5dbc4f1c95ebc6adb0385691
               sha256:2079121536b779e01fcdf31200e9dc6aa856438348de9192fe6e4c96027d89c7
               event_seq 34749, OBSERVATION_RECORDED
    outcome    SURVIVED   (from the spec's pre-registered rule: solved == false)
    PEW        pew:encounter/enc_viv_bringup_849a5b7710721bfa:
               exp_a76deb678c425d4b5767ef0c:wrk_557e5fe49fc50326c91681a7

`POST /v2/audit/verify-anchor` on the fossil's own anchor:

    {"valid": true, "checks": {"event_exists": true, "entry_hash_matches": true,
                               "binds_exp_id": true, "binds_obs_id": true}}

The fossil's persisted execution lineage, read straight from
`ew.fossil_encounters`:

    sfe_engine_instance_id  eng_8a37a5d305969034d488c43e
    sfe_session_id          ses_69b9999a203b7011c699e8d0
    sfe_session_key_fp      sfp_59c5401eb0b0b9e3
    sfe_ledger_head_hash    sha256:2239930fd61ec7c48e4eedc280ce38ae2cda02edcf93aedb752eb65386667731

(The PEW read view does not project those four columns; they are in the table.
The `encounter_id` and `player_id` above are SYNTHETIC bring-up identities in
`namespace=test`, not Proteus lineage — spelled out in the spec's `notes`.)

## 6. Unresolved failure modes

Stated, not hidden. In rough order of how much they should worry a reviewer.

1. **No player execution.** v0 executes SFE *work items* (`noop_v0`,
   `evaluate_bitstring`). It does not run a Proteus organism. The Proteus -> SFE
   placement adapter is Harmonia-owned, carries its own byte-integrity gates
   (`blob_hash == "sha256:" + organism_id`, read-back equality), and hardcodes
   another machine's paths. Absorbing a copy of it into Vivarium would create a
   second, drifting identity gate on the specimen path, which is exactly the
   class of error the seat exists to avoid. The right fix is a
   `proteus_player` executor kind whose implementation *calls* the owned
   adapter — a Harmonia/Proteus decision, not a Vivarium one. Until then any
   spec naming that kind is rejected at validation, visibly.

2. **The PEW write is not transactional with queue completion.** If the process
   dies between `pew_written` and `mark_completed`, the fossil exists and the
   queue row is stranded in `running`. Recoverable — the event log holds the
   `pew_reference` and the SFE ids — but it needs a human. No two-phase commit
   across three systems in v0.

3. **Stranded rows need a human, by design.** Between `claimed` and any SFE
   call, nothing ran; between `mark_running` and `mark_completed`, something may
   have. The queue cannot tell which, so `release` always resolves to `failed`
   and never requeues. The cost is that a genuinely-never-started experiment
   must be re-enqueued by hand. This is deliberate: the alternative is guessing,
   and the guess double-runs experiments.

4. **`stale_after_s` is a heuristic, not a liveness proof.** A worker paused by
   the OS for longer than the threshold is reported as stranded while still
   alive. Reporting is all `status` does — nothing acts on it — so the failure
   mode is a false alarm, not a false recovery. A real fencing token (a lease
   epoch in the DB) is the v1 fix.

5. **One outcome rule shape.** The rule language is a single comparison over one
   top-level result field. Anything richer will need either a real expression
   language (with all the review that deserves) or an Archaeon-side
   adjudication step that hands Vivarium the outcome directly. It must not grow
   informally.

6. **The single-slot index is global to the schema.** Two workers with different
   ids on the same schema cannot double-run, but the second simply idles rather
   than being told it is redundant. Multi-slot execution needs a partition key
   in that index and an explicit concurrency policy.

7. **Not exercised:** cross-machine operation (both bring-up runs were on M1,
   where the DB, SFE and PEW all live); the engine being unreachable *mid-run*
   after a work item was claimed (the claim would expire and the engine would
   reclaim the work while Vivarium records a failure — correct, but untested);
   PEW returning `409 conflict` for a differing row under the same
   `(encounter_id, run_id)`.

8. **The bring-up rows are in the production `viv` schema and in production PEW
   under `namespace=test`.** They are real rows, deliberately kept as evidence,
   not cleaned up. `test_live_pew.py` is double-gated (`VIV_LIVE_PEW=1`) so the
   suite does not add more on every run.

## 7. Commit hash

`8b940a16561b621b4763b002f0b2d37bb7b71de8` — Vivarium v0: migration, code, 37 tests, role docs.
Branch `vivarium/v0-2026-09-05`. This stamp is carried by the immediately
following commit, because a document cannot contain the hash of the commit
that carries it.
