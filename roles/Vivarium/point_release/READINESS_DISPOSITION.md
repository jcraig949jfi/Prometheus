# Vivarium -- READINESS DISPOSITION after window C4-20260917-W1

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-17 17:0x UTC (Vivarium m2-fce3fe0b). Window C4-20260917-W1 CLOSED at canary run 10. Operator "PRE-CAMPAIGN-4 REPAIR ORDER" s2 (execute the
rehearsed window; resolve the five foreign rows; fixture; canary; disposition) and "Stage 3 / implementation
order" s16 (exactly one disposition) and s18 (the five plain statements).

## DISPOSITION

    QUALIFIED_FOR_CAMPAIGN  --  Vivarium's execution seat, at pinned build 08081c6ed, on production `viv`
                                (migrations 001-010) against engine eng_906356f7 (schema 9, bc8d3a0c), with
                                the caveats in s3 below, which are named and bounded, none of them Vivarium
                                defects that could masquerade as a Campaign 4 result.

Deployment state: **DEPLOYED_AND_QUALIFIED** for the 09-16 durability fixes (identity guard, D2/D2b value
checks, C2 row pulse, dead-man, ClaimGrant) and the point release (attempts/steps, NEW ATTEMPT, start bundle,
gate + intervention receipts, termination envelope, PEW outbox, production descriptor).

## 1. What the window did (all receipted under roles/Vivarium/receipts/window_C4-20260917-W1/)

    backup      viv-2026-09-17T134620Z.dump, 24,041,802 bytes, sha256:ee23aa7f..., pg_restore --list: 5 tables    run1
    migrate     006-009 promoted (byte-identical to the drafts) and applied to production `viv`:               run2
                1,155 rows before = after; every old row byte-identical over its 28 old columns; 7 sampled
                `viv.cli show` outputs byte-identical to the pre-window capture; 1,150 attempts backfilled
                UNKNOWN (one per pre-release terminal row); 0 steps fabricated; terminal row UPDATE and
                attempt DELETE refused live
    hold        Archaeon's five queued rows (spec_version 2) held to 2027-01-01 with `viv.cli hold`
                (not_before only; `held` events logged); the restart step refused until they were held
    advance     pinned worktree D:\Prometheus-worktrees\vivarium-consumer -> 493043b21 ... 609772a79            run3..
                (detached, clean, never the canonical checkout; every advance logged)
    tasks       VivariumOutboxDelivererM2 registered (5 min); MONITORS.md rows (Harmonia #356)
    bootstrap   durable SFE identities `vivarium` (cli_2bb36261) and `vivarium-test` (cli_ec9977ed)          run4
                registered ONCE on eng_906356f7 (s10); pew_token PENDING (Mnemosyne's route; OPTIONAL key)
    restart     dead-man ENABLED -> first tick launched the consumer; restart receipt ok (engine ANSWERED,     run6
                store prometheus-canonical, credential sfe_token present, hold none, point_release_tables true)
    fixture     s13 synthetic qualification at the deployed SHA: 16/16 checks, all eight s16 answers true      qualification-*.json
    canary      s14: 10 runs + one deliberate re-attempt on production (below)
    010         migration 010 applied through the same migrate step (invariants re-proved: 1,150 = 1,150,      run12
                0 steps fabricated, every old row unchanged)

## 2. What the canary found and what was fixed (each with an acceptance test that would have caught it)

The canary (vivarium/deploy/canary.py) runs through the PRODUCTION consumer, queue and engine as the production
identity: A gate-FAIL control; B a 3-repeat GKL run; C the consumer killed inside the repeat loop; D the
consumer killed while posting observations. Ten runs; every failure below was a real defect on the
production path that the synthetic fixture had not caught because its doubles were more permissive than the
engine:

    #  found in   defect                                                     fix (commit)                              proof
    1  run 2      dead-man read LIVE for 15 min after the kill (never pid-   young heartbeat + pid gone on this host    test_deadman: 4 controls;
                  checked a young heartbeat)                                 -> DEAD after 60 s (16d41d287)             relaunch 132-282 s live
    2  run 2      engine binds a world to the SESSION that created it (403   affinity key held host-locally, world     session-bound double: adopt
                  SESSION_MISMATCH from any other session); a relaunched     step records session_id, new process       -> REPLAYED / no key or wrong
                  consumer opened a new session -> every verifier False ->   ADOPTS the prior session when it holds     key -> RECOMPUTED (fefc313d0)
                  world RECOMPUTED (duplicate world; obs orphaned)           the key and the engine accepts it
    3  run 2      release --new-attempt emitted no ATTEMPT_TERMINATED for    the stranded attempt's termination is an   outbox counts in the same test
                  the stranded attempt                                       outbox row, same transaction (fefc313d0)
    4  run 3      ONE work item per experiment; attempt 1 had COMPLETED it;  claim is a keyed step: REPLAYED when the   work-item state-machine double:
                  attempt 2 re-claimed -> WORK_NOT_CLAIMABLE                 item is COMPLETED (no lease keeper, no      completed once, claimed once;
                                                                             second complete), RECOMPUTED when RETRYABLE lease-expired -> fresh claim
                                                                             (fa8a8442e; sfclient.work_attestation)
    5  run 5      attempt 1's observe:0 landed on the engine but its step    a NULL-result prior is a recovery          ORIGINAL-once double: commit-
                  result never did (killed in between) -> attempt 2 re-      candidate; verifiers find the act BY       then-die -> REPLAYED with the
                  posted -> 409 one ORIGINAL per experiment                  CONTENT (obs by exp_id+repeat_index, world  recovered id; two observations
                                                                             by name, experiment by spec_hash) -> REPLAYED
                                                                             with the recovered result; nothing found ->
                                                                             NEW, never invented (ebf15cc93)
    6  run 5      the 409 was classed ENGINE_TRANSPORT = the consumer's      4xx after the commit = ENGINE_REJECTED     409 / 503 / OSError test
                  HALT class: it parked and paged Daedalus (#352) for        (row fails typed, reason EXECUTOR_ERROR,
                  Vivarium's own defect                                      no park); 5xx + socket stay transport (3a671820b)
    7  window     deliverer parked 12 ticks after registration on "no PEW    no credential = HELD_NO_CREDENTIAL, exit 0,  test_no_credential_holds_and_
                  client (no credential)"                                    rows kept; the bound counts ticks that tried never_parks
    8  run 6      schema 9 list routes answer PAGE OBJECTS ({observations:   _items() reads the page and refuses a       page/list/truncated test;
                  [...], next_after_seq, truncated}); the verifiers iterated truncated page as evidence of absence; the  doubles answer the engine's shape
                  the dict's KEYS -> every 'present' read False              (963740678)
    9  run 7      a real 60 s read stall on POST observation (the write      migration 010: failed -> queued legal ONLY  3 controls (queue refuses by
                  landed): attempt FAILED/ENGINE_TRANSPORT (correct) and     in the release path, ONLY when the newest   name; trigger refuses; bare
                  the ROW went terminal `failed` -- frozen; the only rerun   attempt's reason is ENGINE_TRANSPORT, ONLY  UPDATE refused); rehearsal
                  was a new row = a second world                             with no open attempt (ca1a5a314)            001-010 on a copy of live rows 7/7
    -  #354       Daedalus: send the Idempotency-Key                         step key = Idempotency-Key on hypothesis/   keys equal the scoped key
                                                                             prediction/experiment/observation posts
    10 run 8      the step key is per DESIGN (on purpose); the engine's      engine key = step key SCOPED TO THE ROW     a second row of one design
                  idempotency store is per client: the same design enqueued  (stepkey.engine_key; unique per row,        gets a different key; the
                  twice -> 409 "key reused for a materially different        stable across its attempts) (08081c6ed)     same row's attempts the same
                  request" on the first observation of every row

Production evidence at the end (row D of run 7, experiment ad6254d7, the hardest shape, on production):

    attempt 1  STRANDED   (killed while posting)        world NEW, experiment NEW, claim NEW, observe:0 NEW (result never landed)
    attempt 2  FAILED     ENGINE_TRANSPORT (60 s stall) world REPLAYED, experiment REPLAYED, claim REPLAYED, observe:0 REPLAYED,
                                                        observe:1 NEW, observe:2 FAILED (timed out; the engine HAS it)
    attempt 3  COMPLETED  12 observations              world/experiment/claim REPLAYED; observe:0,1 REPLAYED; observe:2 RECOVERED
                                                        by content; observe:3..11 NEW
    engine     ONE world, the experiment, EXACTLY 12 observations (read as the owner)
    outbox     ATTEMPT_OPENED x3, GATE_EVALUATED x3, ATTEMPT_TERMINATED x3 (PENDING: no PEW token yet)
    events     enqueued, claimed, running, stranded_released, claimed, running, execution_failed, failed,
               transport_failure_released, claimed, running, completed

Run 9 (build 08081c6ed, every fix above deployed): A, B, C green; D COMPLETED on production in attempt 2
with 12 observations in ONE world -- the recorder had seen 1 observation at the kill, the engine held 2 (a
POST landed before its step result), attempt 2 REPLAYED both (one by id, one recovered by content) and posted
10 NEW. The canary's own predicate (replayed == recorded at the kill) was the only thing that flagged; it is
corrected to replayed >= recorded (the receipt carries the re-evaluation).

**Run 10 (build 08081c6ed): canary OK, 35/35** -- A (gate FAIL, no world), B (3 repeats, every step NEW,
engine holds exactly 3), C (killed in the loop: claim RECOMPUTED after the lease expired, 5 observations, ONE
world, relaunch 234 s), D (killed while posting: claim REPLAYED, 12 observations, ONE world, relaunch 237 s);
no canary work left in the queue. Receipt canary-C4-20260917-W1-run10.json.

Rows C (killed inside the loop) passed end to end in runs 5, 6, 7 and 9: world/experiment REPLAYED, claim
RECOMPUTED after the lease expired, 5 observations, ONE world, both attempts in the outbox, dead-man relaunch
in 132-282 s. Row A (gate FAIL, no world) and row B (3 repeats, every step NEW, labels recorded, engine holds
exactly 3 observations) passed in every run.

## 3. Caveats -- named, bounded, not Vivarium defects

    a  ENGINE STALLS   the 60 s read stall (run 7) is Daedalus's request-path item (#345/#348; 9.0.1 accepted
                       #351, NOT deployed at this window). Vivarium's behaviour on it is the designed one
                       (attempt FAILED/ENGINE_TRANSPORT, consumer parks and pages Daedalus per rider #136) and
                       recovery is `viv.cli unpark` + `release --new-attempt` (010), proved above. Until 9.0.1
                       is deployed a multi-hour C4 run will meet this and need that two-command recovery; it
                       loses no science and mints no duplicate.
    b  PEW TOKEN       Mnemosyne has not issued the `vivarium` writer identity. The outbox holds every fossil
                       and provenance event (74+ PENDING rows now), the deliverer HOLDS (never parks) and
                       delivery starts the tick the token lands. Nothing is lost; nothing is delivered yet.
    c  LABELS          sfclient.create_world has no `labels` kwarg; labels are recorded on the step
                       (labels_applied=false), not on the engine's world. L-013 stays open one more release.
    d  B1 READ GRANT   the consumer's scope reconcile fails HTTP 404 "unknown grantee cli_1029e9255a074157a1b3ba1e"
                       -- the Archaeon read grant named an M1-ledger client id; on the M2 ledger the grantee
                       must be re-issued (Archaeon/Daedalus). Receipted every tick, touches no row.
    e  TRUNCATED PAGES a world with > 10,000 observations answers a truncated page; the verifiers then refuse
                       to claim absence and RECOMPUTE (a re-post the engine answers 409 -> ENGINE_REJECTED).
                       Campaign 4 worlds hold ~10-300 observations.
    f  PID CHECK       death detection is by pid on THIS host after 60 s; a consumer on another host is
                       judged only by its 15-minute heartbeat (by design; no farm).

## 4. Frozen for Campaign 4 (operator s7)

    Vivarium build         08081c6ed (pinned worktree D:\Prometheus-worktrees\vivarium-consumer, detached, clean)
    queue schema           viv, migrations 001-010 (apply_migrations ledger in the restart receipt)
    step key               "idem:" + sha256(design_digest|kind|parts_json)[:32]; statuses NEW/REUSED/REPLAYED/RECOMPUTED/FAILED
    termination reasons    the closed set in viv/attempts.py (COMPLETED_ALL_REPEATS ... UNKNOWN); 4xx = ENGINE_REJECTED -> EXECUTOR_ERROR
    outbox streams         viv.fossil.v1 (encounters), viv.execution.v1 (ATTEMPT_OPENED/TERMINATED, GATE_EVALUATED, ...)
    descriptor             vivarium/deploy/PRODUCTION.draft.json: eng_906356f7 @ https://192.168.1.191:8811, schema_floor 9,
                           store prometheus-canonical, keys [sfe_token], optional [pew_token]
    identities             vivarium = cli_2bb36261427e607191ece250; vivarium-test = cli_ec9977ed07be328cc30247b3
    tasks                  VivariumDeadmanM2 (5 min, ENABLED), VivariumOutboxDelivererM2 (5 min, ENABLED), VivariumConsumerM2 (on demand)
    engine                 eng_906356f7, schema 9, source bc8d3a0c (Daedalus's 9.0.1 restart changes the hash, not the floor)

A later change needs a named defect, the pre-change receipt kept, an explicit version transition (a new pin),
and a canary run.

## 5. The five plain statements (operator s18)

1. **What runner semantics the point release absorbed.** Every engine act is a keyed, typed step; a NEW
   ATTEMPT re-creates nothing it can prove it already made -- by id, or by content when the record never
   landed -- including the session the world lives in and the work item the engine completed; the gate is
   evaluated and receipted before the action; the termination envelope says why an attempt ended and whether
   it is censored; the start bundle is sealed at claim over the producer's declaration; fossils and provenance
   leave through an outbox that survives PEW being down.
2. **What it did not absorb.** In-place transport retry (a stall fails the attempt and parks the consumer by
   rider #136; recovery is two operator commands); the engine's `labels`; the B1 read grant on the M2 ledger;
   PEW delivery itself (no token). None of these changes what a Campaign 4 row means.
3. **What archaeological code can retire.** Archaeon's runner-side world/experiment/observation bookkeeping,
   its own resume logic and its private gate-in-control-flow can retire for rows executed through Vivarium:
   the queue's execution_step, gate_receipt, intervention_receipt and termination envelope are the record.
   The `execution_attempts` (plural) table from the pre-release era is unused by this code and can be dropped
   in a later window.
4. **What must remain for Campaign 4.** Archaeon's producer side (spec, bundle_declared, gate measurements,
   population manifest via Proteus), its campaign runner for anything not enqueued through Vivarium, and the
   operator's two recovery commands (`viv.cli unpark`, `viv.cli release --new-attempt`) until Daedalus's 9.0.1
   removes the stall.
5. **Whether a real campaign should trust Vivarium today.** Yes, for sequential unattended execution: on
   production it ran a gate control, a 3-repeat experiment and two death shapes (in the loop; while posting)
   plus a real engine stall, and finished with one world, exactly the declared observations, every step typed,
   every attempt in the outbox, and no manual database repair -- the remaining defects are the engine's stall
   (Daedalus) and the missing PEW token (Mnemosyne), both named, neither able to masquerade as a result.

## 6. Where everything is

    receipts   roles/Vivarium/receipts/window_C4-20260917-W1/ (backup, migrate, advance, bootstrap, restart, 010, fixture,
               canary runs 5-10 + row D attempt 3, restart receipt at the pinned build); the live copies under
               D:\Prometheus-data\vivarium\window\ and \var\ (restart-vivarium@m2.json, deadman state, park clearances)
    tools      vivarium/deploy/{window.py, rehearse_window.py, canary.py, redeploy.sh, prepare_m2.py}
    tests      vivarium/tests/test_point_release_attempts.py (16), test_deadman.py (14), test_deliver.py (9), test_qualification.py
    docs       roles/Vivarium/point_release/*.md (this file is the disposition; SCOPE_FREEZE_AND_WINDOW_PLAN.md is the plan)
