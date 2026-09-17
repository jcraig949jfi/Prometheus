# Vivarium point release -- SCOPE FREEZE and DEPLOY WINDOW PLAN

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-17 (Vivarium m2-fce3fe0b). Operator "Stage 3 / implementation order 2026-09-17": Stage 3 ->
**scope freeze** -> implementation -> **migration/deployment window** -> clean restart -> qualification -> disposition.
This file is the freeze (s1) and the window plan (s10-s12). Nothing in it has touched production `viv`.

## 1. Scope FROZEN at this commit

What ships in the point release, by MUST SHIP item, with the code and the control that proves it:

    MUST SHIP                       CODE                          PROOF (all on throwaway schemas)
    execution attempts + steps      viv/attempts.py, 006/007      test_point_release_attempts.py; check_drafts 15/15
    NEW ATTEMPT (only recovery)     queue.release_stranded(       release --new-attempt: REUSED/REPLAYED/RECOMPUTED/NEW
                                    new_attempt=True), cli         steps, no world re-created (QUALIFICATION_SYNTHETIC)
    start bundle (closed keys)      viv/bundle.py, 008            test_stepkey_and_bundle.py (16)
    intervention receipts           attempts.intervention_receipt  intended vs realised; per-repeat id `#r<n>`
    prerequisite gate receipt       loop._evaluate_gates, 008     gate FAIL/PASS with measured reference, committed
                                                                   BEFORE action
    termination envelope            attempts.envelope, 006        closed reason set; BUDGET_EXHAUSTED -> COMPLETED +
                                                                   censored; zero-observation anchors on COMMITTED
    PEW outbox + deliverer          viv/outbox.py, deliver.py,    test_deliver.py (9): outage -> delivery -> lost-ack
                                    009                            duplicate; parked at rule-10 bound; frozen rows
    production descriptor           viv/production.py,            test_production_descriptor.py (5); daemon refuses
                                    deploy/PRODUCTION.draft.json   on production schema when verify is not ok
    engine labels (Daedalus D7)     runner._create_world           labels passed only if sfclient.create_world accepts
                                                                   them; labels_applied recorded either way
    09-16 durability fixes          db identity guard, D2/D2b     test_db_identity, test_d2*, test_c2_row_pulse,
                                    value checks, C2 pulse,        test_deadman, test_d7_claim_grant
                                    dead-man, ClaimGrant

Suite at the freeze: 688 passed / 43 skipped (skips = live-engine and Redis-era tests, listed in the receipt).

### Not in scope (named so nobody waits for it)

    - a bounded IN-PLACE retry on ENGINE_TRANSPORT (Daedalus #345). Today a transport failure closes the
      attempt FAILED/ENGINE_TRANSPORT and the row's recovery is NEW ATTEMPT (replayed steps, no duplicate
      science). The consumer's engine timeout is 60 s (>= the 30 s Daedalus asks; sfclient's derived default
      is 45 s), so the measured 5-13 s stalls do not trip it at all. An in-place retry is Campaign-5 work.
    - sfclient `create_world(labels=)` -- the client does not accept it yet; the runner records
      labels_applied=false until Daedalus/Archaeon add the kwarg. L-013 is then closed by the ledger.
    - PEW writer credential for `vivarium` on M2 -- registration is Mnemosyne's route; the outbox holds rows
      (PENDING) until the token is present; nothing is lost, nothing is delivered until then.
    - Archaeon A1 (who arbitrates a disputed attempt) -- open; the schema does not depend on the answer.
    - Harmonia's contract_hash field name -- proceeding by default: `harness_id`/`execution_id` names as
      posted; contract_hash read from the conformance record.

## 2. Rehearsal (done, read-only on production)

`vivarium/deploy/rehearse_window.py` copied the real `viv` rows (1,155 queue rows / 3,281 events / 246 errata
rows) into a throwaway schema, applied 001-005 then 006-009, and checked; receipt
`roles/Vivarium/receipts/WINDOW_REHEARSAL_2026-09-17.json` (fingerprint sha256:79e29356b1a1afa5):

    old_rows_byte_identical (over pre-migration columns)   ok   1155/1155
    one_attempt_per_terminal_row                           ok   1150 = 1150 terminal = 1150 distinct
    all_backfilled_unknown                                 ok   1150
    no_steps_fabricated                                    ok   0
    all_attempt_number_1                                   ok
    only_new_column_is_bundle_declared_all_null            ok
    terminal_row_frozen (rebuilt transition fn)            ok   "is terminal (completed) and is frozen; refusing UPDATE"
    throwaway dropped                                      yes

Status histogram of production at rehearsal: cancelled 492 / completed 579 / failed 79 / queued 5. The five are
Archaeon's (created_by archaeon, spec_version 2, 09-14/09-15), HELD in prose by #284 but NOT in the queue:
not_before is NULL on all five, so a restarted consumer would claim them on its first tick. The window's
restart step therefore REFUSES while any queued row not created by vivarium is unheld. New in this release:
`viv.cli hold <id> --until <tz ISO> --by --reason` (and `--lift`) moves only not_before on a queued row and
logs a `held`/`hold_lifted` event -- the row's relations and status are untouched (test_queue.py, CHEAT
control: every other column byte-identical). Archaeon holds or cancels its five before the restart, or tells
me to; I do not decide for them.

## 3. The window (what `vivarium/deploy/window.py --confirm <id> --sha <sha>` does, in order)

    step        act                                                          refuses when
    backup      pg_dump -n viv -F c -> D:\Prometheus-data\vivarium\backups\  pg_dump rc != 0 or empty file
    drafts      check_drafts.py on a fresh throwaway                         < 15 ok lines or any BAD/FAIL
    promote     copy drafts/006..009 -> migrations/ (sha recorded)           copied file != draft
    migrate     apply_migrations on `viv` (guarded: VIV_SCHEMA must be viv)  row count changed; attempts !=
                + the SAME old-column hash comparison as the rehearsal        terminal rows; any step fabricated;
                                                                              any old row changed; any non-UNKNOWN
    verify      `viv.cli show` of --sample rows vs the --capture taken       any sampled row's output differs
                before the window
    advance     prepare_m2.py --sha --advance --register (pinned worktree    dirty worktree; sha mismatch
                moves only by this logged command; tests passed at the sha)
    tasks       register VivariumOutboxDelivererM2 (5 min), DISABLED         schtasks rc != 0
    bootstrap   `viv.cli sfe-identity --ensure` against eng_906356f7          a client named `vivarium` already
                (operator s10 permits per-machine bootstrap)                  exists on this ledger (the CLI's rule)
                PEW writer: recorded PENDING (Mnemosyne's route)
    restart     ENABLE + RUN VivariumDeadmanM2 -> first tick starts the      any queued row not created by
                consumer from the pinned worktree; ENABLE the deliverer       vivarium and not held (listed);
                                                                              then the consumer's own
                                                                              _production_gate (restart receipt
                                                                              with refuse[] and exit; the task
                                                                              stays enabled, so the refusal is
                                                                              re-attested every tick)

Every step's outcome and inputs land in `deploy_window-<id>.json`; a failed step SKIPs the rest. Steps can be
re-run as a subset (`--steps`) after the cause is fixed -- promote/migrate/tasks are idempotent
(IF NOT EXISTS / apply_migrations's ledger / schtasks /F).

Rollback: the four new tables hold nothing production-derived until the consumer runs; DROP them, restore the
pinned worktree to the prior sha (prepare_m2 --advance back), re-disable the two tasks. The backup from step 1
is the fallback for `viv` itself. 006-009 never modify old rows (proved above), so a rollback loses nothing
they held.

## 4. What I need from others before the window (none blocks the window itself)

    operator    open the window: one line naming a window id (I will pass it as --confirm) and confirming
                s10 credential bootstrap on eng_906356f7 for client `vivarium`
    Daedalus    sfclient.create_world(labels=) kwarg (schema 9 carries labels on WorldCreate; the client
                does not expose it) -- without it labels_applied=false and L-013 stays open one more release
    Mnemosyne   a PEW writer credential for producer `vivarium` on M2 (key name `pew_token` in the
                descriptor's credential file); until then the outbox holds and the deliverer parks nothing
    Archaeon    hold (`viv.cli hold`) or cancel your five queued rows before the restart, or say "claim them";
                A1 ruling (arbiter of a disputed attempt) -- schema-neutral, can land after the window

## 5. After the window (s12-s16)

restart receipt (var/restart-vivarium@m2.json: descriptor, engine probe, store identity, credential presence by
name, migration state, outbox state) -> qualification fixture against production engine as `vivarium-test`
(s13 list; the synthetic run already passed all eight s16 answers on a throwaway) -> one Campaign-3-shaped canary
(s14) -> READINESS_DISPOSITION.md with exactly one of QUALIFIED_FOR_CAMPAIGN / QUALIFIED_FOR_CANARY_ONLY /
NOT_YET_QUALIFIED -> the five plain statements (s18).
