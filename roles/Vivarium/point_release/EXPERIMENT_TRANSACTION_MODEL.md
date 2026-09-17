# Experiment transaction model -- additive delta to the Vivarium queue (point release)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-17 (Vivarium m2-fce3fe0b). Stage 1 design under the operator's
"Stage 1/2 direction after Campaign 3" (s3, s15) and Amendment 1 s6.B. Design
only: the migration is a DRAFT under vivarium/migrations/drafts/ and is not
picked up by viv.db.apply_migrations (which globs migrations/*.sql, not
subdirectories). Nothing here is applied before the coordinated window.

## 0. What is absorbed, from where, and why

    absorbed mechanic                          source (Archaeon runner)                          campaign evidence
    ---------------------------------------    -----------------------------------------------   -----------------------------------------------
    numbered attempts, never renamed           runner.Attempt (number, attempt_id, of_record)    C1 L-013 (rec 1) -> closed in C2; C3: 2-5
                                                                                                  attempts per slot, 0 full recreations
    parent attempt / resumed_from              Attempt.receipt.resumed_from                      C3 slot 09 a04 replayed 29 verified steps
    step key CONTAINS the design digest        Attempt.key(): sha(experiment, prereg_digest,     C2 L2-021: a05 (4-bit) replayed a04 (8-bit)
                                               name, parts)                                       records -- the ONE replay defect in 3 campaigns
    REPLAYED vs RECOMPUTED on the receipt      Attempt.step(): replayed=True + verify()           C2 report "2 resumed attempts (8 + 8 steps)"
    receipt after EVERY step (atomic write)    Attempt.save() -> RECEIPT.json                     C1 L-012 (rec 3): a crash re-created everything
    Idempotency-Key = the step key             runner.Engine.publish/record(idem_key=...)         C1 L-012 "Idempotency-Key was available and unused"
    engine_path (dry vs live) never mixed      Attempt: a live attempt never resumes a dry one   C1 L-016

NOT absorbed (stays above, by Amendment s2): disposition, typed states,
of_record as a SCIENTIFIC choice (below, of_record is a deterministic
pointer the producer may override), ledger candidates, reachability rows.

## 1. The hierarchy, side by side (from IDENTITY_TRANSLATION_CONTRACT.md)

    Archaeon   campaign > harness (C4-SFE-NN) > design (prereg_digest) > attempt aNN > step (idem key) > rows
    Vivarium   [family / candidate set] > execution row (experiment_id uuid) > spec_hash > repeat > observation

The row stays the unit of claim, of the single-running-slot constraint, and
of the SFE world. What is ADDED is a level beneath the row (attempt, step)
and a level of provenance beside it (envelope). Multi-world attempts are a
MAJOR-version item (s15) and are not modelled.

## 2. New objects (additive; old rows keep their exact meaning)

### 2.1 viv.execution_attempt

One row per attempt to execute a queue row. Today every queue row has
implicitly exactly one attempt (attempt_id == experiment_id, runner.py:376);
the migration backfills attempt_number 1 for every existing row so history
is representable, not reinterpreted.

    attempt_id            uuid PK
    experiment_id         uuid FK -> research_experiment_queue      the row (execution_id in the envelope)
    attempt_number        integer NOT NULL                          1, 2, ... per experiment_id; UNIQUE (experiment_id, attempt_number)
    parent_attempt_id     uuid NULL FK -> execution_attempt          the attempt this one was opened FROM (NEW ATTEMPT after failure);
                                                                    NULL for the first
    design_digest         text NOT NULL                             == the row's spec_hash at open time (a changed spec is a NEW ROW,
                                                                    never a new attempt; the column exists so a step key can be
                                                                    checked against it without a join, and so the invariant in s4 is
                                                                    a CHECK, not a convention)
    bundle_hash           text NULL                                 START_BUNDLE_SCHEMA.md; NULL for pre-release rows (UNKNOWN)
    worker_id             text NOT NULL
    claim_grant           jsonb NOT NULL                            the ClaimGrant that authorised it (D7)
    opened_at             timestamptz NOT NULL DEFAULT now()
    closed_at             timestamptz NULL
    terminal_state        text NULL                                 COMPLETED | FAILED | CANCELLED | STRANDED (see TERMINATION_ENVELOPE.md)
    termination           jsonb NULL                                the termination envelope
    receipt_digest        text NULL                                 sha256 over the canonical attempt receipt at close
    of_record             boolean NOT NULL DEFAULT false            exactly one per experiment_id may be true (partial unique index);
                                                                    set deterministically = the newest COMPLETED attempt, overridable by
                                                                    the producer through an erratum, never silently

### 2.2 viv.execution_step

One row per keyed step inside an attempt. The step VOCABULARY is the loop's
existing stage set plus per-repeat and per-artifact steps, so a row that
executes today emits the same steps it implicitly performs now:

    step kinds (closed set, v1):  conformance | claim | validate | build | preflight:<slot> | world | hypothesis |
                                  reserve:<n> | run:<repeat n> | observe:<repeat n> | artifact:<name> | selection_bind |
                                  fossilize | finalize

    step_id               uuid PK
    attempt_id            uuid FK -> execution_attempt
    step_key              text NOT NULL                             "idem:" + sha256(design_digest, step_kind, parts)[:32]
                                                                    -- the SAME derivation as archaeon.campaign2.runner.step_key, from ONE
                                                                    shared module (viv/stepkey.py; Stage-2 Q1) both can import, so a
                                                                    producer's own key and Vivarium's coincide when they name the same
                                                                    (design, kind, parts); UNIQUE (attempt_id, step_key)
    step_kind             text NOT NULL
    parts                 jsonb NOT NULL DEFAULT '[]'
    status                text NOT NULL                             NEW | REUSED | REPLAYED | RECOMPUTED | FAILED  (s3)
                                                                      NEW         executed for the first time in this lineage of attempts
                                                                      REUSED      not executed; the stored result of a prior attempt's step
                                                                                  with the SAME key was taken without a verifier (only legal
                                                                                  for steps the kind declares pure)
                                                                      REPLAYED    not executed; prior result taken after its verifier passed
                                                                                  (a world still alive, an artifact still readable)
                                                                      RECOMPUTED  executed again although a prior result existed (verifier
                                                                                  failed, or the kind declares the step non-replayable)
                                                                      FAILED      raised; the error is on the row; the attempt closes
    replay_of_step        uuid NULL FK -> execution_step             the prior step whose result was taken (REUSED/REPLAYED)
    recomputed_from_step  uuid NULL FK -> execution_step             the prior step whose result was rejected (RECOMPUTED)
    idempotency_key       text NULL                                 the key sent to the engine on this step's POST, if any (== step_key)
    started_at            timestamptz NOT NULL DEFAULT now()
    completed_at          timestamptz NULL
    result                jsonb NULL                                the step's result as the receipt held it (engine ids, digests, counts)
    result_digest         text NULL                                 sha256 over canonical result
    error                 text NULL

Partial progress receipt = the set of execution_step rows of an open
attempt: readable at any moment without the process (s3 "partial progress
receipts").

### 2.3 viv.provenance_envelope (the translation contract, stored)

    experiment_id         uuid PK FK -> research_experiment_queue
    envelope              jsonb NOT NULL                             the shared envelope (IDENTITY_TRANSLATION_CONTRACT.md s2), verbatim as
                                                                    the producer supplied it; every key from the contract's section-D list
                                                                    present, with the literal "UNKNOWN" where the producer cannot know
    envelope_version      text NOT NULL                             "viv.envelope.v1"
    factors               jsonb NOT NULL DEFAULT '{}'                producer-defined stratum labels (s11): evaluator_family, cell, foundry_profile,
                                                                    operator_profile, search_profile, budget_class, treatment_arm, ...; verbatim

Today `source_evidence` on the row already carries producer facts unhashed;
the envelope is a typed, versioned sibling with a contract, not a rename.

## 3. State machine (attempt level)

    OPEN --(all steps terminal, fossilize ok)--> COMPLETED
    OPEN --(a step FAILED)------------------> FAILED         (terminal for THIS attempt; the row's status follows the policy table)
    OPEN --(operator cancel)----------------> CANCELLED
    OPEN --(worker gone, pid dead, lease lost)-> STRANDED     (never resolved by inference; `viv.cli release` opens a NEW ATTEMPT
                                                              with parent_attempt_id = the stranded one, or cancels)

Row status stays as today (queued/claimed/running/completed/failed/cancelled)
and is derived from the attempt lineage: completed iff some attempt is
COMPLETED; failed iff the newest attempt is FAILED and the policy table
says terminal. A row is never `running` without exactly one OPEN attempt.

## 4. Invariants (database-enforced where possible)

    I1  a step key contains the design digest: CHECK (step_key = expected) cannot be expressed in SQL over a hash, so the
        trigger recomputes sha256(design_digest || kind || parts) from the attempt's design_digest and REFUSES the insert
        if it differs. A producer-supplied key that omits the design cannot enter the table. This is the structural form of
        the L2-021 fix.
    I2  REUSED/REPLAYED require replay_of_step to point at a step with the SAME step_key in an attempt of the SAME
        experiment_id with a COMPLETED-or-FAILED-after status; trigger-enforced. A replay across designs is therefore
        impossible even by a buggy loop.
    I3  at most one OPEN attempt per experiment_id (partial unique index); at most one of_record.
    I4  attempt_number is dense per experiment_id (trigger); never renumbered; never deleted (no DELETE grant on either table).
    I5  the attempt's design_digest equals the row's spec_hash at open (trigger); a spec change is a new row (existing rule).
    I6  a NEW ATTEMPT is the only recovery: no code path re-executes a step inside a FAILED or STRANDED attempt. "Retry" does
        not appear in the vocabulary (s3, REJECT list).

## 5. Recovery policy table (written, per failure class; absent row = terminal)

    failure_class            recovery                     who decides
    -----------------------  ---------------------------  ------------------------------
    ENGINE_TRANSPORT         NEW ATTEMPT (auto, bounded   Vivarium (deterministic; bound = 1 automatic attempt, then park to Daedalus,
                             by rule 10)                   existing halt rider)
    LEASE_LOST               NEW ATTEMPT (auto, 1)         Vivarium
    STRANDED                 operator release -> NEW       operator (existing rule)
                             ATTEMPT
    BUDGET (terminal, not a  none: COMPLETED with          -- (TERMINATION_ENVELOPE.md: a budget stop is a completion with censoring,
    failure any more)        censoring                     not a failure)
    SPEC_REJECTED, EXECUTOR  none (terminal)               producer redesign (a new row)
    _ERROR, VALUE refusals
    PEW_*                    never a failure of the        outbox (PEW_OUTBOX_DESIGN.md)
                             attempt

## 6. What the loop does differently (no behaviour change for rows that succeed first time)

    claim      -> open attempt 1 (or n+1 with parent), write claim_grant
    each stage -> insert the step row (NEW) before the call; complete it after; on a prior attempt with the same step_key:
                  consult the kind's replayability declaration and the verifier; mark REPLAYED/REUSED/RECOMPUTED accordingly
    engine POST-> idempotency_key = step_key (already "viv:<attempt>:<stage>:<n>" today; becomes the design-keyed form)
    finalize   -> termination envelope, receipt_digest, of_record if COMPLETED, outbox events

## 7. Old rows

Every existing row gets ONE execution_attempt (attempt_number 1, design_digest
= spec_hash, bundle_hash NULL, terminal_state from status, opened/closed from
claimed_at/finished_at, of_record = (status = completed)) and NO step rows
(they were never recorded; UNKNOWN, not fabricated). The backfill is a
separate, reversible migration (drafts/007) so 006 can land without it.

## 8. Acceptance tests (to be written with the implementation, Stage 4)

    positive   a row executes; its attempt has steps NEW in stage order; receipt_digest matches a recomputation over the rows
    positive   a worker dies mid-row (pid killed); the row is STRANDED; `release` opens attempt 2 with parent = 1; steps whose kind
               declares them replayable and whose verifier passes are REPLAYED; the rest RECOMPUTED; the engine sees the same
               Idempotency-Key for the replayed POSTs and no duplicate world
    negative   a step insert whose key omits the design digest is refused by the trigger (the L2-021 shape, made impossible)
    negative   a second OPEN attempt for one row is refused
    cheat      a loop that marks a step REPLAYED pointing at a step of another experiment_id is refused by the trigger
    cheat      a spec edit between attempts produces a different design_digest and zero REPLAYED steps
    old rows   every pre-release row reads back unchanged through `viv.cli show`; its backfilled attempt has no steps and says so
