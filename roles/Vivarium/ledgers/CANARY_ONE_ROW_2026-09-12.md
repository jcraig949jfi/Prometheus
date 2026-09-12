VIVARIUM RECEIPT -- ONE PRODUCTION ROW READ BACK, THEN THE CSID-REUSE
INVARIANT CLOSED.  2026-09-12 12:0x local. Instance m1-416d588d.
Operator bite: "one production row, full readback, then harden your own
enqueue path". Nothing submitted by this seat. Nothing historical touched.

============================================================================
UPSTREAM PRECONDITION (Archaeon fossil-visible)
============================================================================
  commit    29f1f54b8 (origin/main) "the tick read zero SFE fossils all
            day -- the pinned worktree had no ledger path; per-host config
            written, guard test added"; F:\Prometheus-worktrees\archaeon-tick\
            archaeon\config.local.json now exists.
  log       F:\Prometheus-worktrees\archaeon-tick\archaeon\deploy\
            archaeon_tick.log: last "sfe db not found" tick 2026-09-11
            19:57:01 local; first tick with fossils.rows > 0 at 20:12:01
            local; every tick since reports "rows": 1029, corpus
            corpus:fdcafb012552b3200efce7af, regions 49.

============================================================================
WHAT TRAVERSED SINCE THE PRECONDITION (not what I asked for; what happened)
============================================================================
  The tick is autonomous and I do not gate the producer. Between the
  repair and this reading FIVE rows traversed, none issued by this seat:
    f3dc6a87  09-11 21:12  archaeon tick WROTE_WEAK_SIGNAL  (first
              fossil-informed row: the tick record at 21:12:01 carries
              "rows": 1029 and "decision": "WROTE_WEAK_SIGNAL")
    b0eef992  09-12 01:27  tick weak_signal
    231f44d8  09-12 05:27  tick weak_signal
    155b1115  09-12 09:27  tick weak_signal
    ececfe90  09-12 11:56  ARCHAEON BY HAND, request_key
              rk-canary-2026-09-12-1, policy
              canary.region_directed_by_hand.v0, source_reason human,
              producer workspace base_sha 35a41ce62
  All five: completed, SURVIVED, selection.alternatives [] (0), pew
  reference present, conformance CONFORMANT. The CANARY below is ececfe90
  (the operator-issued specimen). f3dc6a87 was read back the same way
  first and agrees on every surface (session scratchpad canary_readback.py).

============================================================================
CANARY: ececfe90-3e20-4dfe-b271-6a9d45d9abb2
============================================================================
1. QUEUE (viv.research_experiment_queue / _events)
   created 11:56:46.688 by archaeon (human), csid cs-40a8239f45904b56,
   request_key rk-canary-2026-09-12-1, spec_hash sha256:3caf3b11e022...
   events, in order: claimed 11:56:51 / running 11:56:53 /
   selection_bound 11:56:57 / pew_written 11:57:00 / completed 11:57:00.
   claimed exactly once (1 'claimed' event; claimed_by vivarium@m1).
   Final status completed. Active slot after: None; stranded [].
   (No 'enqueued' event: Archaeon's writer inserts directly; the row's
   created_at and the single claim are the queued-once evidence.)
2. CONSUMER (viv.worker_heartbeat, pid 26348)
   before  11:52:31  counters executed 29, idle 13356, ticks 13385
   after   11:59:25  counters executed 30, idle 13437, ticks 13467
   -> executed +1, failed 0, blocked 0, parked None, no stop flag.
   consumer log lines 124-127: claim 15:56:51Z, dispatch -> running
   sfe=exp_8d968652a8a6b0c9885ec716 15:56:53Z, tick=EXECUTED t=9.06s
   15:57:00Z. No PARKED / tick=FAILED lines in the whole log (0).
   No ENGINE_TRANSPORT; the halt did not fire and was not bypassed.
3. SFE (F:\Prometheus-data\sfe\engine.db, mode=ro)
   experiment exp_8d968652a8a6b0c9885ec716 state OBSERVED, spec_hash ==
   the queue row's spec_hash (byte match), work_id wrk_0741fa4c800b927b...
   world wld_13b3caf41573e37f015bf9ff name viv-3caf3b11e0229257 (derived
   from the spec_hash), client cli_5680df58 (vivarium), seed_root 926994;
   experiments in world: 1 total, 1 OBSERVED, 0 CREATED-only.
   observation obs_52ac5c2564a0deaf0d3ed303 SURVIVED, ORIGINAL.
   work item COMPLETED, claimed_by vivarium@m1, attempts 1.
   anchor: sfe_event_id evt_b0812852d9e94de0d430ca06 exists at event_seq
   129400, OBSERVATION_RECORDED, in that world; it binds exp + obs above.
   engine identity on the row: eng_8a37a5d305969034d488c43e, schema 8,
   hash sha256:5380cb90f42dc83b...; conformance CONFORMANT at claim.
4. PEW / FOSSIL
   pew_reference pew:encounter/ENC-archaeon-4f6625f91b2e304b:exp_8d96...:
   wrk_0741...; ew.fossil_encounters row: outcome SURVIVED, namespace
   prod, sfe_world_id wld_13b3caf4..., created 11:57:00.697, run_id and
   sfe_event_id equal to the queue row's; fossil_worlds row present.
   GET /api/v1/fossil/encounters/ENC-archaeon-4f6625f91b2e304b -> 200,
   n_runs 1, outcome SURVIVED, producer.queue.experiment_id ==
   ececfe90-3e20-4dfe-b271-6a9d45d9abb2. /health 200 ok, pew.fossil.v2.
5. SELECTION
   result_summary.selection: alternatives [] (0), planned_members 1,
   candidate_set_id cs-40a8239f45904b56, family fam_0c130ce17314326b...;
   engine families row kind selection, planned_members 1, ONE member
   (the executed experiment, role selected). EXPERIMENT_CREATED in the
   world: 1. No phantom alternatives.

ONE_ROW_PATH: CONFIRMED (for ececfe90; f3dc6a87 independently agrees).
Not a claim about the ecology: five rows in fourteen hours, all
evaluate_bitstring, all SURVIVED.

============================================================================
PHASE 2: CSID REUSE INVARIANT
============================================================================
  migrations/005_candidate_set_append_refused.sql -- BEFORE INSERT
    trigger: for a non-NULL candidate_set_id, take a transaction-scoped
    advisory lock on the id, then refuse (SQLSTATE VIV01) if any row with
    that id was written by ANOTHER transaction (xmin <> current xact).
    Same-transaction members (Archaeon's atomic N-candidate submit) stay
    legal. One definition, in the database, that both writers meet;
    Archaeon's Python check (6fc3ea619) becomes the friendly pre-check.
  viv/queue.py -- CandidateSetReused (typed, SQLSTATE VIV01), a pre-check
    before the INSERT using the same xmin test as the trigger, and the
    database refusal mapped to the same exception if the pre-check is
    raced. viv/cli.py enqueue -> "REFUSED: ..." on stderr, exit 4.
  Applied to the production register: `python -m viv.cli migrate` ->
    001..005 applied to schema viv; pg_trigger shows
    trg_candidate_set_append_refused enabled beside trg_req_transition.
    Verified there without landing a row: an INSERT naming cs-h5-1 (256
    prior rows) inside a rolled-back transaction -> VIV01 "already has
    256 registered row(s)"; probe rows landed: 0; counts unchanged.
  The consumer needs no restart: it never inserts queue rows; the
    invariant is in the database.
  tests/test_candidate_set_append_refused.py (8 passed):
    POSITIVE  new csid, one row -> one member; consumer tick -> EXECUTED,
              bind spy members 1 / alternatives 0; result alternatives [].
    REFUSAL   second enqueue same csid -> CandidateSetReused (prior 1)
              before any write: counts, membership and event count
              unchanged; a cancelled member is an append too; CLI exit 4.
    CHEAT     (a) 4 members in ONE transaction land and the same spy
              reads members 4 / alternatives 3; (b) trigger DISABLED ->
              a raw cross-transaction append lands (2 members); trigger
              re-enabled -> the same raw append is refused with VIV01.
    RACE      two connections, both pre-checked 0, released at a barrier,
              winner holds its xact 0.5 s: exactly one LANDED, the other
              REFUSED with VIV01; members 1; 0 partial rows.
    ARCHAEON  vivqueue.submit with 3 candidates (one xact) still legal;
              its own append attempt refused.
  Suite on the merged tree: vivarium offline 525 passed / 38 skipped;
    archaeon/tests/test_vivqueue_integration.py 29 passed.

CSID_REUSE_INVARIANT: ENFORCED (database trigger on viv, both writers,
race closed by advisory lock; historical 510 sets untouched).

============================================================================
CLEANUP (separate from the canary)
============================================================================
  tail.exe pid 22940 -- my orphan from a Monitor stopped 09-11 ~17:5x --
  confirmed by command line before the kill (tail -n 0 -f
  consumer-vivarium@m1.log), Stop-Process -Force, re-probe: gone.
  Unrelated to any row.
