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
