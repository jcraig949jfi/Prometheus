# Vivarium -- point-release Stage 0: evidence inventory

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-17 (Vivarium m2-fce3fe0b). READ-ONLY stage under Operator
Amendment 1 s3/s14: nothing here is deployed, migrated or enabled; Campaign 3
is active on the production substrate and untouched. Built from origin/main
at the SHA in the commit that carries this file.

Sources read for this inventory (paths are repository-relative):

    archaeon/campaign1/CAMPAIGN_REPORT.md, LEDGER.jsonl (L-001..L-032)
    archaeon/campaign2/CAMPAIGN_REPORT.md, LEDGER.jsonl (L2-*), runner.py,
        c2base.py, accounting.py, MACHINE_READINESS.md
    archaeon/campaign3/JOURNAL.md (through C3-SFE-02), MACHINE_READINESS.md,
        LEDGER.jsonl (L3-*), c3base.py, corridor_import.py
    archaeon/wse/reachability.py (row shape, run_identity, dedupe_runs)
    vivarium/migrations/001..005, viv/spec.py, viv/runner.py, viv/loop.py,
        viv/pew.py, viv/request.py, viv/kinds.py

Recurrence counts are the ledgers' own `recurrence` field; "attempts" and
"steps" below mean Archaeon's runner objects unless prefixed viv.

## 0. The governing fact

Campaigns 1-3 did not execute through Vivarium. They executed through
Archaeon's campaign runner (archaeon/campaign2/runner.py, reused by campaign
3 via c3base.Experiment3) directly against the SFE client. Every durable-
execution lesson below was therefore learned, fixed and re-verified in THAT
code. Vivarium's queue ran 579 completed rows of a different producer (Archaeon's
autonomous tick and hand-issued campaign rows) with its own, older, set of
invariants. The point release is an ABSORPTION: the proven semantics move
into the layer that can own them for the next producer, and Archaeon's
runner stays the reference implementation until a qualification run says
otherwise (Amendment s10).

## 1. Campaign 1 lessons that belong in the execution layer

    id     cat                  rec  lesson (one line)                                   today (Archaeon runner)                         Vivarium today
    ----   ------------------   ---  -------------------------------------------------   ---------------------------------------------   ------------------------------------------
    L-012  MISSING_RECOVERY     3    no resume: a crash or a redesign after publish       Attempt.step(): key = sha(experiment, prereg    a row is claim-once; a crash strands it
                                     re-created worlds, artifacts, records; the           digest, name, parts); result cached in the      (never re-run by inference); no step
                                     engine's Idempotency-Key was unused                  receipt; replayed on resume when verify() ok    granularity below one row
    L-013  OBSERVABILITY        1    two attempts distinguishable only by world NAME;     attempt_id "<exp>/aNN"; ATTEMPTS.json index;    viv.attempt_id == experiment_id (one row
                                     no attempt id on worlds/experiments                  of_record pointer; world name carries the       = one attempt); replication_of links
                                                                                          experiment id; RECEIPT.json per attempt         re-issues; world name = viv-<spec_hash>
    L-008  TO_MACHINERY         2    RNG seeded from the branch LABEL; two cells with     run_cell(rng_label=...); common random          repeat.seed_derivation is CLOSED (constant
                                     identical inputs diverged by chance                  numbers default for multi-cell comparisons     | derived from (seed_root, index)); no
                                                                                                                                          cross-row CRN concept
    L-030  BUG                  0    compared arms' generation 0 filled from a harness    evolve.common_fill(); loop records the fill's   not applicable (no population kinds yet)
                                     seed while controls drew the common gen 0            provenance (gen0_provenance.verified_common)
    L-009  FRICTION             1    digest forms differ ('sha256:<hex>' vs bare hex);    wse/digest.py canon()/same() on both sides      viv/artifacts.py normalises digests
                                     hash_ok read False on every import                                                                  (canonical-json-v1 codec); one form
    L-026  BUG                  0    same-client cross-session read refused (403)         Engine.reader(): a session-less client for      viv runs one durable client + session;
                                     while the session-less read succeeds                 reads (D-013); read_campaign() for another      B1 read scopes are the cross-client
                                                                                          campaign's principal                            read mechanism (scope/grant, engine-side)
    L-001  FRICTION             0    client lacks read wrappers                           done in C3 group E (sfclient gained three)      viv/conformance declares 24 routes it
                                                                                                                                          calls; listing worlds/artifacts unused
    L-002  PORTABILITY          0    M1 addresses survive as defaults after the M2 move   engine_descriptor() (one tracked descriptor)    vivarium/config.json still names M1;
                                                                                                                                          the M2 launcher overrides by env (09-16)
    L-003  TO_MACHINERY         0    two contradictory production rulings; HOLD for 7 h   proposes a tracked PRODUCTION.json consumers    dead-man gates on an expected engine id
                                     with the engine up and idle                          gate on                                         passed on its command line (09-16)
    L-005  MISSING_TELEMETRY    0    the M2 consumer cannot start without two token       proposes per-machine credential bootstrap       prepare_m2.py measures secrets PRESENCE;
                                     files only the operator can carry (blocks the        (register a consumer client at prepare time)    minting is refused by the 09-16 ruling
                                     queue path entirely)                                                                                 (superseded in practice by C3 on eng_9063)
    L-007  MISSING_FAILURE_ST.  0    an intervention channel can be INERT and nothing     every channel reports an APPLIED count;         viv records realised execution inputs per
                                     flags it                                             INTERVENTION_NOT_APPLIED typed state            attempt (load_receipt, resources); no
                                                                                                                                          "intended vs applied" pair for imports
    L-015  OBSERVABILITY        0    35 s silent; a hung engine call looks like work      per-step progress lines + engine-call timer    stall detector (viv.cli stalls), in-row
                                                                                                                                          pulse (C2, 09-16, not deployed)
    L-016  FRICTION             0    dry-run receipts landed in the record directory      engine_path flag on the receipt; dry runs       identity_role=test -> client vivarium-test;
                                                                                          never of_record                                 PEW namespace forced to test in tests
    L-011  AUTOMATION           0    startup/exchange/record/teardown is a skeleton        c2base.Experiment IS that skeleton              viv/loop stages 0-6 are the same skeleton
                                     each experiment should not rewrite                                                                  for one row; no multi-world/session shape

## 2. Campaign 2 lessons that belong in the execution layer

    L2-021 BUG                  0    resume REPLAYED another design's engine steps         DONE: Attempt.key includes prereg_digest       viv: spec_hash is the design; a row is
                                     (a05 4-bit resumed a04 8-bit; six rows wrong)         (the design hash); a changed design shares     never resumed, so the class cannot occur
                                                                                          no keys                                         -- but neither can a legitimate replay
    L2-017 BUG                  0    reachability pooled runs from different gen-0         DONE: foundry id in the row key                foundry/runtime profile is not a viv
                                     FOUNDRIES under one key                                                                              identity today (UNKNOWN in the contract)
    L2-026 TO_MACHINERY         0    stop-rule runs recorded as 'treated', losing valid    DONE (C3 B): stopped_on_solve + censored       repeat.budget exists; no censoring flag
                                     right-censored baselines                              pooling monotone in G                          on an observation (a budget-stopped row
                                                                                                                                          and a finished row look alike)
    L2-028 BUG                  0    rebuilt manifests with a seeded draw: "same           artifacts that carry organisms carry full      viv artifact slots carry digest, type,
                                     genotype" had different runtime params               manifests (cmp2.pop.set.v1); a rebuild         schema_version, codec, expected_bytes,
                                                                                          recipe is a preregistered treatment            interface_id; content semantics are the
                                                                                                                                          owner's (Proteus) -- consistent
    L2-007 FRICTION             0    GET artifacts route 405; ids carried in receipts      still open (Daedalus, Amendment s5.C)           viv keeps artifact ids in load_receipt
    L2-011 BUG                  0    campaign-1 fill seeds were harness seeds              recorded as a caveat on standing rows           n/a
    C2 report L-012/L-013 closure: "numbered attempts, receipt after every step, design-keyed replay, ATTEMPTS.json; Idempotency-Key verified once"
    C2 report: 2 resumed attempts (steps replayed): PHASE-A a02 8 steps correct; C2-SFE-02 a05 8 steps WRONG design -> L2-021 fix. This is the
    one measured replay defect in three campaigns and it is a KEYING defect, not a replay-concept defect.

## 3. Campaign 3 lessons available at execution time (through C3-SFE-02)

    L3-011 BUG                  0    a fixed rung released before the control climbed     ladder hold rule (harness)                      scientific; stays above Vivarium
    L3-015 BUG                  0    import_fetch dst == src refused on an ISOLATED       publish then fetch; import_fetch only for       viv preflight resolves by digest with a
                                     world (403)                                           producer/consumer pairs                         locator; same shape, engine rules apply
    L3-017 MISSING_TELEMETRY    0    origin takeover is not clonal collapse; a genome-     lineage share per generation in trace rows     the "realised dose / lineage share"
                                     only diversity readout misses it                      (C3 group F)                                    observation is a SUPPLIED fact Vivarium
                                                                                                                                          must carry, never compute
    L3-039 BUG                  0    shared disposition code crashed on rows lacking       DONE: missing metric skipped, never zero        viv outcome_rule has an INDETERMINATE
                                     the primary metric                                                                                   branch (required); D3 (kind-level
                                                                                                                                          INDETERMINATE) still open
    MACHINE_READINESS group F   injection cap: dose + offspring cap; origin shares per generation in every trace row -> the "intended vs
                                realised" pair exists in Archaeon's trace, not in any execution receipt (Amendment s6.G asks Vivarium to record it)
    JOURNAL 07:15-07:55         C3-SFE-01: 1,235 s, 1 world, 24 records, 24 reachability rows, 12 corridor rows, 0 errors -- the longest
                                single attempt so far; still one process, one session, no checkpoint

## 4. Recurring defects (three or more sightings across campaigns and seats)

    R1  no resume / re-creation of worlds on rerun          L-012 rec 3 -> closed in C2 runner; NOT present in Vivarium (rows are claim-once)
    R2  attempts indistinguishable / renamed                 L-013 rec 1 + C1 report "attempt renames" -> closed in C2 runner; Vivarium never had it
    R3  RNG identity tied to labels                          L-008 rec 2 -> closed (rng_label, CRN); Vivarium's seed derivation is per-row only
    R4  M1/M2 address and identity leakage                   L-002, L-003, L-005 (all 2026-09-17) + Vivarium 09-16 (fork guard, engine-id precondition)
    R5  consumer death unobserved                            Vivarium 09-13 (11.9 h), 09-14 (35.9 h) -> dead-man built 09-16, DISABLED, not deployed
    R6  value validated after the world was committed        Vivarium D2 (24 rows lost 09-06) -> closed 09-16 in code, not deployed
    R7  ledger commits with no register row                  Vivarium D7 (7 + 2 orphans) -> closed 09-16 in code, not deployed

## 5. Local patches that belong in my layer (absorption candidates)

    from archaeon/campaign2/runner.py
      Attempt (number, attempt_id, resumed_from, of_record, RECEIPT after every step)      -> viv: attempt table below the row (B)
      Attempt.step / step_key(experiment, design digest, name, parts) + verify()           -> viv: step log keyed by (spec_hash, step name, parts) (B)
      replayed[] vs recomputed distinction on the receipt                                  -> viv: step row carries replayed:bool (B)
      Engine.publish() requires a maturity block for population-material kinds            -> stays ABOVE (scientific gate); viv carries the block
      idem_key on every engine POST                                                        -> viv already sends "viv:<attempt>:..." (runner.py:561)
      atomic receipt writes                                                                -> viv rows are transactional already
    from archaeon/campaign2/c2base.py
      seal(prereg) -> prereg_digest on every attempt; PREREG_CHANGED_AFTER_SEAL             -> viv: the start bundle hash (C); spec_hash is the executed half
      startup / world / publish / import_fetch / record / teardown as keyed steps          -> viv: the step vocabulary for a multi-world attempt (B, E)
      reach_row() at close                                                                 -> stays ABOVE (reachability is a projection)
    from archaeon/wse/reachability.py
      run_identity(cell, bits, N, G, E, regime, foundry, campaign_seed, rng_label, seed)  -> the identity envelope viv must be able to CARRY (contract)
      dedupe_runs on baseline rows                                                          -> stays ABOVE
    from Vivarium 09-16 (code-fixed, not deployed)
      store identity guard, admission-time value checkers, in-row pulse, dead-man,
      ClaimGrant                                                                            -> deploy in the window; they are the durability baseline

## 6. Missing instrumentation (execution layer)

    - a per-step record below the row: today one row has repeats[] and obs_ids[] but no keyed step log, so "which steps were
      replayed vs recomputed" is unanswerable for a Vivarium row
    - intended-vs-realised for any supplied intervention (imports, substitutions, doses): the C3 trace has it; no receipt field
    - a censoring flag on an observation (budget-stopped vs finished): repeat.budget stops, the fossil does not say so
    - foundry / runtime profile identity on the row (UNKNOWN today; Proteus owns the value, Vivarium owns the slot)
    - a PEW outbox: pew.required decides whether a PEW failure fails the row; a non-required failure is logged, never retried,
      never re-delivered (viv/pew.py, loop stage 6)
    - step-level wall/cpu/bytes: resources{} exists per attempt stage (retrieval, execution), not per step

## 7. Manual decisions that can safely become deterministic (in my layer)

    - "is this the attempt of record?" -> the newest attempt whose terminal state is COMPLETED and whose design hash equals the
      row's; earlier attempts stay readable, never renamed (Archaeon's of_record pointer, made a column)
    - "may this step be replayed?" -> only if the kind declares the step idempotent AND the stored result's verifier passes AND the
      design hash matches; otherwise NEW ATTEMPT. Never a retry.
    - "did the treatment apply?" -> realised counts recorded beside intended; the typed state is computed above, but the pair is a fact
    - "which engine is production?" -> a tracked descriptor consumers gate on (L-002/L-003); Vivarium reads it, never decides it

## 8. Scientific discretion that MUST remain above my layer

    reachability levels and thresholds (FLOOR/SHELF/SUMMIT, 0.45/0.90); censoring INTERPRETATION (the flag is mine, the pooling
    is not); corridor edges; dose CHOICE and offspring caps; maturity gates for population material; disposition and typed
    states (states.py); ledger candidates and the funnel; which attempt's rows enter a table; preregistration content.

## 9. Stage-1 candidates, classified (Amendment s12; deltas to follow in EXPERIMENT_TRANSACTION_MODEL.md)

    MUST SHIP
      A  identity translation contract (this pass; roles/Vivarium/point_release/IDENTITY_TRANSLATION_CONTRACT.md)
      B  attempt/step additive schema: attempt table (parent_attempt, design_hash, of_record, terminal state), step log
         (design-keyed step key, replayed|recomputed, verifier result, partial receipt); NEW ATTEMPT is the only recovery
      D  PEW outbox: producer-side durable table keyed by stable event_id; asynchronous delivery; duplicate -> no-op; gap visible
      0  deploy the 09-16 durability fixes (guard, value checkers, pulse, dead-man, ClaimGrant) in the window
    SHOULD SHIP IF CHEAP
      C  start bundle: hashed envelope over (sealed spec, artifact locators, engine descriptor, foundry/runtime profile slot,
         executor kind+version); changed bundle = derived design (a new spec_hash by construction, since the spec carries it)
      G  intended-vs-realised receipt pair for supplied interventions; censoring flag on observations
    DEFER TO NEXT POINT RELEASE
      E  second executor class (lease, step log, checkpoint contract, declared external requirements) -- design now, one fixture,
         no generalisation this release
      F  checkpoint/fork/replay + the two benchmarks -- DEPENDENT on Daedalus's snapshot surface and Proteus's population manifest
    MAJOR VERSION CANDIDATE
      multi-world / multi-session attempts inside one Vivarium row (Archaeon's harness shape); today a row is one world
    REJECT
      Redis for evidence or queueing; any landscape level in the executor; server-side QD archive consumed by Vivarium
