# SFE LONG-RUN REPORT (D10) -- measured, not asserted

    seat      Daedalus[m2-d6ecd70b]     date  2026-09-17
    build     sha256:bc8d3a0c (the shipped schema-9 build), scratch engine on
              loopback, disposable ledger on the production volume class (D: NVMe)
    tool      deploy/longrun_load.py ; receipts deploy/LONG_RUN_2026-09-17/
                w20g1000/{receipt.json,RECEIPT.md,engine.log}     (main run)
                w20g1000_noreader/                                  (control; appended when done)
    headline  medians and p95 FLAT across the whole run (no degradation with
              history); 0 HTTP 5xx; restart at full history 1.05 s; 102 MB per
              100K events. AND: 150 calls (0.13%) stalled 5-13 s, on READS AND
              WRITES ALIKE, beginning ~14 min in. The SQLite write lock is NOT
              the cause (max wait 1.77 s). A server-wide freeze class exists
              and its mechanism is identified as a candidate below. Consumers
              with a 10 s timeout (Archaeon's gate) WOULD trip on it.

=======================================================================
1. WORKLOAD (the shape Campaign 4+ intends, ~10x Campaign 3 per-run rows)
=======================================================================

    20 worlds x 1,000 logical generations; per generation: POST experiment
    (Idempotency-Key) + POST commit + POST observation (logical_time = g,
    Idempotency-Key); every 10th generation a WORLD_EVENT; every 50th a
    checkpoint; every 100th an 8 KiB artifact; per world one fork (at the
    last checkpoint) and one typed termination. 2 producer threads (10
    worlds each) + 1 reader thread walking every world's observations by
    cursor (limit 200) continuously. Then: full paginated event walk of all
    worlds; kill -9; relaunch; verify-anchor on 50 events.

    totals    events 82,660  observations 20,000  experiments 20,000
              artifacts 200  checkpoints 380  worlds 40 (20 + 20 forks)
    calls     ~115,000 (62,664 write transactions; 52,765 reader pages)
    wall      write phase 3,042 s (50.7 min); 6.6 generations/s overall;
              ~130 ms per generation per producer under contention

=======================================================================
2. LATENCY BY QUARTER OF THE RUN (ms; q1 = first 12.7 min ... q4 = last)
=======================================================================

    route                              q1 p50/p95/max      q2 p50/p95/max      q3 p50/p95/max      q4 p50/p95/max
    POST experiments                   21.8/213.9/1889.6   16.6/320.0/10693.2  16.1/209.2/12782.3  16.0/200.9/9654.4
    POST .../commit                    18.8/183.1/1921.2   -                   -                    15.8/184.5/12247.7
    POST observations                  66.9/204.2/1896.8   59.6/303.1/12356.2  57.9/206.2/12749.8  56.3/197.1/8194.7
    POST events (WORLD_EVENT)          18.0/217.9/773.5    -                   -                    15.7/181.6/2475.2
    POST checkpoint                    15.1/218.0/632.3    15.1/322.8/421.0    15.0/309.2/900.7    18.8/175.2/207.6
    POST artifacts (8 KiB)             32.3/267.9/563.6    -                   -                    12.9/167.7/213.0
    GET observations (cursor, 200)     19.5/118.9/1737.9   18.6/142.8/11685.6  17.2/125.6/12733.1  17.7/127.0/12113.7
    GET events (cursor, 500) at end    -                   -                   -                    29.1/40.5/65.2
    POST verify-anchor at end          -                   -                   -                    4.5/18.8/26.0

    Reading: p50 and p95 do not move with accumulated history (q1 -> q4);
    the observation POST is 3x an experiment POST (idempotency record +
    event + row + experiment state update, one transaction); a 200-row
    cursor page reads in ~18 ms at 20K rows/world. The MAX column is the
    finding (section 4).

=======================================================================
3. STORAGE, CHECKPOINT, RESTART
=======================================================================

    DB size          84.4 MB at 82,660 events -> 1,071 bytes/event ->
                     102 MB per 100K events (blobs separate: 200 x 8 KiB)
    WAL              0.0 MB after the final checkpoint on restart; 0.37 MB
                     observed mid-run (autocheckpoint working)
    checkpoint       380 checkpoints: p50 16.6 ms, max 0.90 s
    full event walk  82,660 events in 180 pages of 500: 4.65 s (26 ms/page)
    default list x3  0.11 s for three worlds' unbounded (capped) lists
    kill -9 -> free  1.12 s ; relaunch -> /v2/version 1.05 s at full history
    identity         same engine_instance_id after restart; anchors 50/50
    5xx              0 ; write-lock failures 0

    At this rate a campaign the size of Campaign 3 (~6 h compute, ~1,000
    per-run rows) is ~10 MB; a two-week production ledger was 129K events
    (~130 MB by this measure). Nothing here argues for retention; see 5.

=======================================================================
4. THE FINDING: server-wide stalls of 5-13 s
=======================================================================

    count        150 of ~115,000 calls (0.13%); none in the first 868 s;
                 then ~0.6/min for the remaining 36 min (per 5-min bucket:
                 3, 20, 31, 18, 20, 28, 14, 15, 1)
    duration     p50 7.1 s, max 12.8 s
    which routes GET observations 46, POST experiments 35, POST commit 33,
                 POST observations 33, POST events 3 -- i.e. EVERYTHING,
                 reads included, in proportion to call volume
    NOT the      /v2/health write_lock at end of write phase: 62,664
    write lock   acquisitions, 0 failures, max_wait 1.765 s, waits_over_1s
                 1. The B3 instrument measures BEGIN IMMEDIATE only; these
                 stalls are elsewhere.
    mechanism    sfe/store.py: ONE sqlite3 connection (check_same_thread=
    (candidate)  False) serves every read (read() returns it bare) and every
                 write; there is no Python-level lock. Under uvicorn, sync
                 handlers run in a thread pool, so the reader thread's
                 SELECT/fetchall and the producers' BEGIN IMMEDIATE ... COMMIT
                 interleave on the same handle, serialized only by SQLite's
                 own connection mutex. Everything that touches the ledger
                 then waits behind whichever statement holds it, and a
                 stall on one is a stall on all -- exactly the observed
                 shape (reads and writes, same durations). Why 7-12 s and
                 not 100 ms is not yet measured: the candidates are the WAL
                 autocheckpoint being deferred while the shared handle has a
                 statement in progress and then running large, and Python-
                 level contention on the connection mutex under the GIL
                 with a 52K-page reader.
    control      RUNNING: the identical run with --no-reader (no concurrent
                 cursor reader). If stalls vanish, the shared-connection
                 read/write interleave is the cause; if they persist, the
                 cause is in the write path alone (WAL checkpoint / fsync /
                 Defender on the file). Appended below when done.
    consumer     Archaeon's conformance gate and runner use 10 s timeouts
    impact       (#266). A 12.8 s stall reads as ENGINE_TRANSPORT to them.
                 Idempotency keys make the retry safe (the retried POST
                 replays), and the runner does retry -- so the failure mode
                 is a spurious transport error, not lost or duplicated
                 science. Vivarium's C11 class ("halt on ENGINE_TRANSPORT")
                 would park a consumer on it.

=======================================================================
5. DECISIONS FROM DATA (order s10: bounded recommendation, no redesign)
=======================================================================

    SQLite          KEEP. Medians/p95 flat with history, 0 5xx, 0 lock
                    failures, 1 s restart at 83K events, 102 MB/100K events.
                    Nothing in the data argues for another store.
    retention       NONE in this release. The numbers that would change it:
                    a ledger past ~1 GB (~1M events, ~50 Campaign-3s) or a
                    cursor page above 100 ms at that size. Neither is near.
                    The ledger is tamper-evident; truncation is a policy act.
    the stalls      NEXT POINT RELEASE, must-fix-before-unattended-multi-hour:
                    (a) separate READ connections (one per worker thread, or
                        a small pool) from the single WRITE connection --
                        WAL mode is built for exactly that; ~40 lines in
                        store.py; the write path and its B3 measurement are
                        untouched;
                    (b) measure again with this tool; acceptance = 0 calls
                        over 5 s at this shape, p95 unchanged.
                    Until then, for Campaign 4: consumer timeouts >= 30 s on
                    engine calls, idempotency keys on every POST that has
                    one (the runner already does), and the D11 fixture's
                    duplicate-post shape as the retry contract.
    is the engine   For ATTENDED hour-scale runs: yes, with the timeout
    ready for       guidance above. For UNATTENDED multi-hour runs with a
    unattended      10 s-timeout consumer: NO until (a) lands -- a 0.13%
    multi-hour?     spurious transport rate over 50 min is ~50 halts/hour
                    for a consumer that halts on the first one.
    what breaks     At 10x Campaign 3 (this run): nothing in throughput or
    first at 10x?   storage; the stall class is what a consumer sees first.
                    At 100x (~8M events, ~10 GB): unmeasured; the tool takes
                    the same flags.

=======================================================================
6. NOT SHOWN
=======================================================================

    - the cause of the stall's DURATION (only its scope and onset are
      measured); the control run and a WAL-size trace are the next two
      measurements
    - behaviour with the M1-era ledger size (129K events) as a starting
      point rather than an empty one
    - concurrent clients from another host (this run was loopback)

=======================================================================
7. CORRECTION 2026-09-17 12:2xZ -- the control run overturned section 4's mechanism
=======================================================================

    control    the identical 20 x 1,000 run with NO reader thread (2 producers
               only) did not finish: at ~13,100 successful calls the engine
               answered 500 "unhandled server error" twice within 100 ms on
               two different worlds (POST .../events and POST .../commit).
               Receipt: deploy/LONG_RUN_2026-09-17/w20g1000_noreader/engine.log
               lines 13138-13307.
    traceback  sfe/api.py get_foundry -> Foundry(app.state.db_path, ...) ->
               Store.__init__ -> `PRAGMA journal_mode=WAL` ->
               sqlite3.OperationalError: database is locked
    what that  The API constructs a NEW Foundry -- a new Store, a new sqlite3
    shows      connection, PRAGMA journal_mode=WAL -- ON EVERY REQUEST, and
               closes it after (api.py: `def get_foundry(): f = Foundry(...);
               yield f; f.close()`). Store's docstring says "a per-thread
               connection; open one per worker"; the API opens one per
               request. Section 4's "one shared connection with no lock" was
               WRONG: I read Store.read() and did not read who constructs the
               Store. Retracted.
    mechanism  Per-request connection churn (~115,000 open/close pairs in the
    (revised)  main run). When the LAST open connection closes, SQLite
               checkpoints the whole WAL into the main file and truncates it;
               on an 80 MB ledger under two writers that is the multi-second
               window in which every new request's open blocks -- the stall on
               EVERY route, reads included, exactly the observed shape. The
               next open can also fail outright: `database is locked` on
               journal-mode/WAL-index recovery is one of the SQLite lock paths
               the busy handler does not retry -> the 500. The main run never
               hit that path (reader thread kept a connection open almost
               always, so the "last close" was rare); the control, with only
               two producers pausing between requests, did.
    evidence   - stalls in the main run began at ~868 s and never before: the
      that fits  WAL/ledger had to be large enough for checkpoint-on-close
                 to take seconds (DB ~25 MB at that point)
               - stalls hit reads and writes in proportion to volume
               - write-lock waits (BEGIN IMMEDIATE) stayed tiny: the wait is
                 at CONNECT, before any transaction, where B3 does not measure
               - "WAL 0.0 MB" at every inspection: it was being truncated on
                 every last-close, not autocheckpointed at 1000 pages
               - 0 errors in Campaigns 1-3: single sequential producers, so a
                 close-then-open of the same request stream never raced
                 another connection's open
    why it     Campaign 4 with a concurrent reader (PEW ingestion walking
    matters    cursors) or two runners is exactly the two-connection regime.
    the fix    one Store per worker THREAD (thread-local; uvicorn's sync
    (bounded)  handlers run in a pool of ~40), never closed per request; the
               boot-time Store already runs the migration. ~25 lines in
               api.py; store.py untouched; the write path and B3 untouched.
               CODE ONLY, no schema, no route: a 9.0.1 with the load tool as
               acceptance (0 calls over 5 s AND 0 5xx at 20 x 1,000 with 2
               producers + reader, and with 2 producers alone).
    status     being implemented on the branch now; measured before it is
               offered; deployed only on an operator-opened window (freeze
               rule s11; the fix is a candidate "critical defect" exception
               and is stated as such, but production has 0 consumers today).

    Sections 4 and 5 above stand as the record of what I believed at 11:4xZ
    and are not rewritten; this section supersedes their mechanism and
    recommendation. Consumer guidance (>= 30 s timeouts, idempotent retries)
    stands until 9.0.1 is measured.

=======================================================================
8. 2026-09-17 12:0xZ -- the fix attempts, what each one measured, and the actual item
=======================================================================

    attempt 1  thread-local Foundry per worker thread (f494f533). Real-process
               run died at request 1,751: 500 "cannot start a transaction
               within a transaction". FastAPI runs a sync dependency and a sync
               endpoint on DIFFERENT threadpool threads, so a thread-local
               keyed on the dependency's thread handed one connection to two
               concurrent requests. Wrong shape; retracted.
    attempt 2  checkout/checkin pool, exclusive per request (18d78869, branch
               de09dc421, NOT on main). 505+2 tests, D11 16/16. Real-process
               run: 8,570 requests OK, 0 5xx, then a 60 s client timeout on
               reads and writes alike. The server was alive and its CPU flat.
               py-spy on the hung process: a worker thread BLOCKED INSIDE
               `COMMIT` (store.py:929) across 4+ consecutive 1 s samples;
               the main (event-loop) thread in the A6 journal's synchronous
               file append and in the access-log flush. load.db was 10 MB;
               load.db-wal was 344 MB. With the engine idle a PASSIVE
               checkpoint found only 505 un-backfilled frames and TRUNCATE
               emptied the file in 0.14 s -- so nothing leaks a snapshot; the
               WAL had simply never been RESTARTED under continuous readers
               and grew to its high-water mark, and each commit's automatic
               checkpoint walked a wal-index of ~84K frames.
    the actual Both designs pay for WAL maintenance in the request path:
    mechanism    per-request connections: the LAST close runs a full
                 checkpoint + WAL/SHM delete, and the next open recreates
                 them (the 5-13 s stalls; the locked-open 500s);
                 persistent connections: the WAL never restarts while any
                 reader holds a snapshot, grows without bound, and the
                 autocheckpoint INSIDE each COMMIT becomes O(WAL) -> the
                 60 s hang. Neither is a SQLite limit; both are how the
                 engine drives it. Also seen: the event loop does
                 synchronous file I/O for the A6 intent journal and the
                 access log (small today; it stalls EVERY route when the
                 disk hiccups).
    the item   9.0.1, PROPERLY: (a) the pool from attempt 2 (exclusive per
    (bounded)  request, never per request); (b) a background checkpointer
               thread owning ONE connection: PRAGMA wal_checkpoint(PASSIVE)
               every ~2 s, TRUNCATE when log == checkpointed, with
               `PRAGMA wal_autocheckpoint=0` on the pooled connections so no
               request's COMMIT ever runs a checkpoint; (c) `PRAGMA
               journal_size_limit` so a reset WAL is truncated; (d) the A6
               journal append and the access log off the event loop (a
               queue + writer thread). ~150 lines; no schema, no route, no
               contract. Acceptance unchanged: 20 x 1,000 with 2 producers +
               reader AND with 2 producers alone: 0 5xx, 0 calls over 5 s,
               WAL file bounded; plus the D11 fixture; plus /v2/health
               reporting checkpointer last_run and WAL bytes so the next
               stall of this class is visible without py-spy.
    status     NOT built in this release. The branch carries attempt 2 as a
               non-deployable candidate for the record. Consumer guidance
               stands: engine-call timeouts >= 30 s, idempotent retries.
               Campaign 4 with one sequential runner and a paced PEW reader
               is inside the envelope Campaigns 1-3 ran in (0 errors).

=======================================================================
9. 2026-09-17 14:2xZ -- 9.0.1 BUILT AND MEASURED (repair order s1)
=======================================================================

    design    (a) connection POOL, exclusive per request (attempt 2's shape);
              (b) request-path handles: PRAGMA wal_autocheckpoint=0 and
                  journal_size_limit=64 MiB -- a request never checkpoints;
              (c) Checkpointer thread on its own connection, busy handler OFF:
                  wal_checkpoint(PASSIVE) every 2 s, TRUNCATE only when the
                  passive result is clean (refused, never blocked, when a
                  reader holds the WAL); ADAPTIVE: 50 ms cadence while the WAL
                  file is above 8 MB, so backfills stay small;
              (d) /v2/health.checkpointer: alive, runs, truncates, errors,
                  last_run_age_s, wal_bytes, db_bytes, max_wal_bytes_seen;
              (e) A6 journal appends via the threadpool (ordering kept, loop
                  freed); uvicorn access log via a QueueHandler.
              No schema, route, identity or contract-semantics change.
              build sha256:3c7c3732ea13... at main 36f8608be.

    tests     510 (3 new: request-path pragmas pinned; 1,500 commits leave a
              > 1 MB WAL untouched by the request path and one checkpointer
              tick backfills + truncates it; TRUNCATE with a reader holding
              the WAL returns in < 2 s -- measured 5.6 s of blocking before
              the busy handler was disabled; thread alive on /v2/health and
              its death visible). D11 fixture 16/16 with kill -9 under the
              checkpointer. The unit tests SAY they do not reproduce the
              real-process race; the runs below are the acceptance.

    acceptance runs: 20 worlds x 1,000 generations, scratch engine of the
    candidate, disposable ledger on D:, keep-alive client (a connection per
    request exhausted Windows' ephemeral ports at ~117 req/s in the very
    first attempt: WinError 10048, a defect of the measurement, kept in
    accept901_v1_fixed_cadence/R1 as the record)

    v1 fixed 2 s cadence           R1  ABORTED (client/self-inflicted; see s9 text)  engine side: 5xx 1 stalls 0
    v1 fixed 2 s cadence           R2  write  355.3 s  5xx 0  >5s 2  lock_max 10.09 s  wal_peak  88 MB  ck runs 122 trunc  73 err 0  restart 0.73 s  anchors 50/50
    v1 fixed 2 s cadence           R3  write  190.9 s  5xx 0  >5s 2  lock_max 10.86 s  wal_peak 137 MB  ck runs  52 trunc  37 err 0  restart 0.54 s  anchors 50/50
    v2 adaptive cadence (SHIPPED)  R1  write  187.9 s  5xx 0  >5s 0  lock_max  0.89 s  wal_peak  94 MB  ck runs  60 trunc  52 err 0  restart 0.51 s  anchors 50/50
    v2 adaptive cadence (SHIPPED)  R2  write  370.4 s  5xx 0  >5s 0  lock_max  2.44 s  wal_peak  81 MB  ck runs 208 trunc 118 err 0  restart 0.53 s  anchors 50/50
    v2 adaptive cadence (SHIPPED)  R3  write  188.7 s  5xx 0  >5s 0  lock_max  1.69 s  wal_peak  87 MB  ck runs  70 trunc  52 err 0  restart 0.52 s  anchors 50/50

    v1 -> v2  the fixed 2 s cadence let a saturating writer build 90-137 MB
              of WAL between resets; each such backfill competed with the
              writers for the disk while one held the lock, and B3 measured
              the wait exactly (write_lock max_wait 10.09 s in R2, 10.86 s in
              R3; both writers stalled at the same instant, once per run).
              v2's adaptive cadence keeps backfills small: lock max wait
              0.89 / 2.44 / 1.69 s, 0 calls over 5 s, in all three regimes.
              v2's R1 first attempt ABORTED because I deleted the live run's
              scratch directory while cleaning orphans (FileNotFoundError on
              a blob write -> 500); self-inflicted, rerun clean.

    what the numbers say
      - throughput 8-16x the deployed engine at the same shape (188-370 s vs
        3,042 s): the per-request open/pragma/schema-check was most of every
        call (POST p50 1-9 ms vs 16-67 ms)
      - medians and p95 flat across quarters; no growth with history
      - WAL: a sawtooth that resets every few seconds; peaks 77-103 MB only
        under 100-240 generations/s of saturating load (two to three orders
        above any campaign's rate); at campaign rates it stays in the KB
      - write-lock waits now the ONLY residual tail (max 2.4 s) and visible
        on /v2/health as before
      - restart at full history 0.5 s; identity unchanged; anchors 50/50

    operational consequence (recorded in the tests and the runbook): a
    plain file copy of engine.db is NOT a complete backup with persistent
    handles -- recent writes live in engine.db-wal until the checkpointer
    resets it; the SQLite backup API (release tool preflight) is the method.

    NOT done, by order: no storage-engine change; no generalised high-
    concurrency guarantee beyond the three declared regimes; no retention
    change. D16 (idempotency keys on the remaining routes) still deferred.

=======================================================================
10. 2026-09-17 14:4xZ -- run-to-run VARIANCE on the same code; the machine is shared
=======================================================================

    v3 (build d4b8283c = v2 + Idempotency-Key on import; the checkpointer
    and pool byte-identical to v2's) at 14:30-14:44Z:
      R1 0 stalls; R2 NINE stalls 6-12 s (write-lock max wait 12.3 s);
      R3 two stalls of 15.7 s (lock max 15.75 s). WAL in R2 stayed SMALL
      (10-30 MB), so the v1 "big backfill" mechanism does not explain v3.
    What was different: Vivarium's production window ran on this machine
    at the same time (83 events on 8811 between 14:33 and 14:41Z, plus its
    migration I/O), and Windows Defender (MsMpEng) had consumed 5,190 CPU-
    seconds -- more than any other process -- with NO path exclusions
    configured: every WAL append, checkpoint backfill and blob write on
    D:\Prometheus-data\sfe (production) and the scratch dir is scanned in
    real time.
    A write-lock wait of 12-15 s means one writer's transaction took that
    long; inside a transaction the only slow thing is I/O. Concurrent disk
    load from another process plus real-time scanning of the files being
    written is the candidate; the v2 runs (0/0/0) happened in a quieter
    window. Being measured now: R2 again with a py-spy stall watchdog
    (engine stacks captured whenever a request exceeds 4 s), first WITHOUT
    and then WITH a Defender path exclusion on the two data directories.
    Receipts: accept901_v3_d4b8283c_contended/ (the variance run),
    accept901/ (the diagnosed runs).

=======================================================================
11. 2026-09-17 15:1xZ -- the residual DIAGNOSED: the checkpointer's own TRUNCATE blocked writers
=======================================================================

    controlled A/B on the v2/v3 checkpointer (TRUNCATE whenever the passive
    result was clean), R2 shape (2 writers + tight reader), MsMpEng CPU
    sampled every 5 s beside the WAL:
      A1  no Defender exclusion        18 stalls (9 lock-step PAIRS, 5-13 s),
                                        onset t=265 s; MsMpEng 0.1-0.4 CPU-s per
                                        5 s throughout, no spike at any stall
      B1  scratch dir excluded         26 stalls (13 pairs), onset t=270 s;
                                        MsMpEng delta 49.5 s over the run
      -> Defender FALSIFIED as the cause (exclusion changes nothing; its CPU
         is flat when the stalls happen). Vivarium's concurrent window was
         also over by then (last production event 14:41Z; A1 ran 15:00-15:08Z).
    The tell was in the pairing: BOTH writers wait the same 5-13 s at the
    same instant, and B3 reports the wait as write-lock acquisition time.
    Neither writer holds the lock while both wait; the only other
    connection is the checkpointer's. SQLite's own documentation for
    wal_checkpoint(FULL | RESTART | TRUNCATE): "blocks new database writers
    while it is pending" -- for the whole backfill + database fsync. With the
    busy handler off the call is REFUSED if a writer is active at entry, but
    once it gets in (a gap between two writers' transactions, frequent at
    100-240 gen/s) every writer arriving during its 5-13 s of work waits.
    Onset at ~265 s in both runs = the point where the database is large
    enough (~55 MB) for backfill + fsync to take seconds. The lock-step
    pairs in v1 (s9) were the same mechanism, mis-attributed to "big
    backfills competing for disk".

    fix (build f528f235): TRUNCATE only when the engine has been IDLE for
    WAL_IDLE_S = 3 s (no write-lock acquisition, read from the B3 counter);
    under load PASSIVE only, which never blocks anyone. SQLite restarts the
    WAL by itself when a writer finds it fully backfilled, and
    journal_size_limit truncates the file at that restart -- so the file is
    bounded without a writer-blocking call. Unit test pins both branches
    (busy engine -> no TRUNCATE; idle -> TRUNCATE; reader-held WAL -> refused
    in < 2 s). 511 passed.

    measurement tool: added a stall watchdog that runs py-spy against the
    engine whenever a request exceeds 4 s (the 15:1x runs); its first two
    attempts recorded no stacks (a filter bug, then a broken string literal
    from the editing tool) -- kept in accept901_v4_watchdog_runs/ as the
    record; the mechanism was settled from the lock-step timing + B3 +
    SQLite's documented semantics, not from a stack.
