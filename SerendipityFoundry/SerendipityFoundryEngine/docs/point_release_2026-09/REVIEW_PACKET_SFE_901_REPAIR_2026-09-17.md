=======================================================================
REVIEW PACKET -- SFE 9.0.1 REPAIR (pre-Campaign-4 repair order, s1)
Daedalus / Serendipity Foundry Engine -- 2026-09-17, 17:1xZ
=======================================================================

scope       everything since the last packet (the schema-9 point release
            packet of 10:5xZ): the long-run measurement of the shipped
            engine, the defect it exposed, seven fix iterations, the
            deployed 9.0.1, and what is still open before Campaign 4
audience    an external reviewer with no repository access
production  https://192.168.1.191:8811, ledger eng_906356f7 (unchanged)
            build sha256:699ca0f9... at main 7662ad263, deployed 17:01:12Z
            schema 9, 72 routes (unchanged), contract regenerated + landed
attack this every "measured" line names the receipt that carries it;
            every "believed" line says so

-----------------------------------------------------------------------
0. ONE-PARAGRAPH SUMMARY
-----------------------------------------------------------------------

The schema-9 release shipped correctly but its long-run measurement
showed the engine was not fit for unattended multi-hour runs with more
than one client: 0.13% of calls stalled 5-13 s on every route, and two
concurrent writers could get HTTP 500 "database is locked". The operator
ordered the bounded repair. It took three distinct mechanisms to find and
fix, each only visible in a real-process load run, and each earlier "fix"
was falsified by the next measurement: (1) the engine opened a new SQLite
connection per request; (2) every writer-blocking WAL checkpoint mode
costs seconds on this host; (3) the A6 intent journal did file open/
write/close inside every mutating response. The deployed 9.0.1 passes
four load regimes with 0 5xx and 0 calls over 5 s, at 12-24x the previous
throughput, on the same ledger, with no schema/route/contract change.
One property remains and is documented, not hidden: a writer that never
pauses grows the WAL for the run. Vivarium hit the original defect on
production at 15:50Z (a 60 s POST) while the repair was in progress.

-----------------------------------------------------------------------
1. THE DEFECT, AS MEASURED ON THE SHIPPED SCHEMA-9 ENGINE
-----------------------------------------------------------------------

 Tool: deploy/longrun_load.py -- 20 worlds x 1,000 generations (experiment
 + commit + observation per generation, events, checkpoints, artifacts,
 fork, typed termination), 2 producer threads + 1 cursor-reader thread,
 scratch engine of the exact build on the production volume class,
 disposable ledger. ~115,000 calls.

 shipped build bc8d3a0c (per-request connections):
   medians/p95 flat with history; 0 5xx; 102 MB per 100K events;
   BUT 150 calls stalled 5-13 s (reads and writes alike, 0.13%);
   write-lock max wait 1.77 s (so NOT the lock);
   the no-reader control 500'd twice: "database is locked" at
   connection OPEN (sfe/api.py get_foundry -> new Store per request).
 root cause (1): ~115,000 open/close pairs; when the LAST connection
   closed, SQLite checkpointed and truncated the whole WAL of an 80 MB
   ledger -> every request arriving in that window stalled; the next
   open could fail on a lock path the busy handler does not retry.
   Campaigns 1-3 never hit it: one sequential producer, no concurrent
   connection to race. Vivarium's #366 (60 s POST on production, write
   landed) is this class, live.
 receipts: deploy/LONG_RUN_2026-09-17/w20g1000/, w20g1000_noreader/
   (engine_log_500.txt)

-----------------------------------------------------------------------
2. THE FIX ITERATIONS (each measured; each receipt kept)
-----------------------------------------------------------------------

 #  change                              result                              receipt
 1  thread-local Foundry per worker     500 "cannot start a transaction     f8ae501de
    thread                              within a transaction" at request    (reverted)
                                        1,751: FastAPI runs a sync
                                        dependency and a sync endpoint on
                                        DIFFERENT threads -> shared handle
 2  exclusive checkout/checkin pool     hang at request 8,570; py-spy:      w20g1000_pool/
                                        worker blocked inside COMMIT behind
                                        a 344 MB WAL (autocheckpoint inside
                                        COMMIT; WAL never restarts under a
                                        continuous reader)
 3  pool + request-path handles with    0/0/0 on one run, then on the same  accept901_v2_,
    wal_autocheckpoint=0 + background   code: R2 9 stalls, R3 2, with a     accept901_v3_,
    checkpointer (PASSIVE 2 s, TRUNCATE SMALL WAL. Both writers stalled in   defender_ab/
    whenever clean)                     LOCK-STEP pairs (5-13 s). Defender
                                        FALSIFIED by A/B (exclusion changes
                                        nothing; CPU flat at stall time).
                                        Cause: SQLite's FULL/RESTART/
                                        TRUNCATE checkpoints BLOCK NEW
                                        WRITERS for the backfill + db fsync
 4  TRUNCATE only when idle (3 s        0 stalls, lock max 0.56 s, BUT WAL   accept901_v5_
    without a write)                    3.4 GB in 289 s under the tight
                                        reader (SQLite's own restart
                                        starves); restart 8.7 s
 5  RESTART when WAL > 8 MB +           WAL bounded (44 MB) but 1,556        modes_ab/M1
    synchronous=FULL on the             resets = 34 stalls to 15.5 s,
    checkpointer                        throughput HALVED
 6  RESTART valve at 512 MB             held writers > 30 s at 538 MB -> a   accept901_v6_
                                        writer hit busy_timeout -> 500
 7  = #4 + stall watchdog finally       R0 campaign-rate 0/0; R1 2 stalls,   accept901_v7_
    aimed at the serving pid            R3 2, R2 5 (to 21 s) -- WITH A
                                        STACK: both writers idle inside
                                        attestation._append (open/write/
                                        close of the A6 journal file, under
                                        a lock, in the RESPONSE PATH) while
                                        a passive checkpoint saturated the
                                        disk
 8  A6 journal: day file kept open      SHIPPED. Four regimes 0/0.           accept901/
    (write+flush); intent synchronous;
    effected/refused via a writer
    thread; in-memory state immediate

 measurement-tool defects found on the way (all kept in the logs):
   - the client opened a TCP connection per request -> Windows ephemeral
     ports exhausted at ~117 req/s (WinError 10048); now keep-alive
   - py-spy aimed at the venv launcher stub, not the serving child ->
     three watchdog runs with empty stacks
   - one run aborted because I deleted its live scratch directory while
     cleaning orphans (self-inflicted)
   - the qualify tool's "pre-migration rows read NULL" checks assume the
     8->9 migration; they now report BROKE on a code-only release because
     worlds with v9 facts exist (see s6)

-----------------------------------------------------------------------
3. WHAT 9.0.1 IS (no schema, route, identity or contract-semantics change)
-----------------------------------------------------------------------

 pool          Foundry/Store/SQLite connection checked out per request,
               returned after; never opened or closed per request;
               app.state.foundry_generation retires pooled handles
 pragmas       request-path handles: wal_autocheckpoint=0,
               journal_size_limit=64 MiB (a request never checkpoints)
 checkpointer  one daemon thread, own connection, busy handler OFF:
               PASSIVE every 2 s (50 ms while WAL > 8 MB); TRUNCATE only
               after 3 s with no write; never a writer-blocking reset
               under load; alive/runs/errors/wal_bytes/max_wal_bytes_seen
               on /v2/health.checkpointer; reset mode selectable via
               SFE_WAL_RESET_MODE for future measurement (the rejected
               modes remain behind the flag)
 A6 journal    day file open, write+flush per line; intent synchronous
               (on disk before the ledger write); effected/refused via a
               writer thread; attest()/open_intents() unchanged
 access log    uvicorn logging via QueueHandler (off the event loop)
 import        Idempotency-Key honoured (Vivarium's 7th route; id was
               already content-derived, the key stops a duplicate event)
 tests         511 (new: pragmas pinned; checkpointer branches; TRUNCATE
               refused-not-blocked with a reader holding the WAL; pool
               correctness; keyed import). D11 restart fixture 16/16.
               The unit tests SAY they do not reproduce the real-process
               races; the load tool is the acceptance.

-----------------------------------------------------------------------
4. ACCEPTANCE (shipped build 699ca0f9; receipts deploy/LONG_RUN_2026-09-17/accept901/)
-----------------------------------------------------------------------

 regime                                   write    5xx  >5s  lock max  WAL max  restart  anchors
 R0 campaign-rate writer (2 gen/s) +      332 s    0    0    15 ms     8 MB     1.05 s   50/50
    paced reader, 600 observations                                     plateau
 R1 saturating writer + paced reader      128 s    0    0    16 ms     3.3 GB   0.55 s   50/50
 R3 two saturating writers, no reader     131 s    0    0    0.27 s    3.4 GB   4.9 s    50/50
    (the regime of the original 500s)
 R2 two saturating writers + tight        254 s    0    0    0.34 s    3.4 GB   9.7 s    50/50
    reader (the original stall regime;
    the shipped engine took 3,042 s)

 order s1 criteria: existing suite green (511); 0 5xx (all four);
 0 calls > 5 s (all four); campaign-style writer + paced reader (R0, R1);
 modest concurrent writers reproducing the old defect (R3); WAL bounded:
 YES at campaign rate (8 MB plateau, SQLite restarting it in the gaps),
 NO under a saturating writer that never pauses (grows for the run) --
 stated, measured, visible on health; checkpointer alive/observable
 (yes); restart/recovery fixture (16/16); retry semantics unchanged
 (keyed replay returns the original id; tests + the fixture's duplicate-
 post shape). Throughput 12-24x the previous engine.

-----------------------------------------------------------------------
5. DEPLOYMENT (receipts deploy/RELEASE_9_0_1_2026-09-17/)
-----------------------------------------------------------------------

 window      asked Vivarium/Mnemosyne (#351, #367); Vivarium's window
             C4-20260917-W1 closed 15:50Z (#361/#368) and offered to stop
             its consumer on my word; consumer tasks were Ready (not
             Running); 10 min without a production write reached 17:00:19Z
 preflight   8/8: ledger identity, schema 9, pin agrees, commit resolves
             to a NEW build, 0 writes in 10 min, 0 work in flight,
             SQLite-API backup written and re-opened (12,611 events,
             integrity ok, sha256 6ff3d1e7...)
 apply       13/13: pinned worktree -> b0d752183; process killed (child +
             launcher parent); supervisor restarted it; outage 13.3 s; new
             pid/start 17:01:12Z; instance UNCHANGED; hash == candidate;
             schema 9 live + ledger; routes 72 -> 72; checkpointer alive;
             bind/ledger unchanged; events 12,611 == 12,611; pin rewritten
 contract    regenerated after the restart (live + loopback scratch probe
             of the same build): routes identical, engine hash updated;
             landed with a provenance block; gate CONFORMANT
 qualify     18/18 engine checks held (harness 12/12, isolation 7/7, gate
             0, D11 on the live service, capabilities, all v9 facts,
             pagination, termination, 20/20 pre-migration anchors); the
             2 "pre-migration NULL facts" checks are the 8->9 tool's
             assumption (s6.4)
 comms       disposition #369; Vivarium may restart its consumer (same
             ledger, tokens, session keys)

-----------------------------------------------------------------------
6. STILL OPEN -- MINE (fix or test before Campaign 4)
-----------------------------------------------------------------------

 6.1  WAL growth under a saturating writer (KNOWN PROPERTY, not fixed)
      Under a writer that never pauses, SQLite's own WAL restart starves
      and the file grows for the run (3.4 GB per 20K generations at
      100-240 gen/s); restart-after-crash cost scales with it (0.5 -> 9.7 s
      here). Every bounded alternative measured blocked writers for
      seconds. At Campaign 4's rate (R0: 2 gen/s, ~100x faster than C3's
      slots) the WAL plateaued at 8 MB. TEST before C4: an unattended
      multi-hour run at campaign rate with a PEW-style paced reader
      (longrun_load.py --gen-pause 0.5 --reader-pause 0.5, 4-8 h) and
      confirm the plateau holds and /v2/health.checkpointer.wal_bytes
      stays bounded. FIX candidate if it does not: a writer-side restart
      hint (SQLite's sqlite3_wal_checkpoint_v2 from the writer's own
      connection when the WAL is clean) -- untested, not promised.
 6.2  Crash-recovery time is proportional to the WAL at crash time
      (9.7 s at 3.4 GB). Acceptable at campaign rate; state it in the
      runbook; TEST: kill -9 at the end of the 6.1 run and time
      /v2/version.
 6.3  qualify_v9.py: retire the two 8->9-only checks (pre-migration rows
      NULL) for code-only releases; they misreport BROKE now. Small.
 6.4  The 30 s busy_timeout -> 500 path: a writer that waits 30 s for the
      lock gives up with a 500 "database is locked". Correct behaviour,
      but a consumer should treat it as retryable-with-key (Vivarium has
      reclassified 4xx; confirm 5xx-locked is in its retry class).
 6.5  Consumer timeouts: guidance stands at >= 30 s for engine calls with
      idempotent retries; R2's max latency was 2.4 s, so 30 s is generous.
      Re-state in the Campaign 4 runner config (Archaeon).
 6.6  D16 remaining: Vivarium's seven routes are all keyed now; the other
      25 mutating routes are not. Not needed for C4 (nobody named them).
 6.7  The 10,000-row default cap on unbounded list responses stays; make
      cursors mandatory in the NEXT point release once every consumer
      paginates (Archaeon's runner and PEW ingestion should already use
      after_seq).
 6.8  A6 journal day rollover with a persistent handle: the reopen-on-new-
      day path is coded (_write_line) but untested across a real UTC
      midnight. TEST: a scratch engine run spanning 00:00Z, or a unit test
      with the date patched.
 6.9  Machine hygiene: Windows Defender has no path exclusions on this
      host; the A/B showed it is NOT the stall cause, so none is
      recommended; the temporary scratch-dir exclusion was removed.
      Other seats' fixtures (pewC4-*/lineage-*) still register throwaway
      clients on PRODUCTION and blocked two preflights; they should use
      deploy/scratch_contract_engine.py --tree --port 89xx.
 6.10 Backups: with persistent handles a plain file copy of engine.db is
      NOT a complete backup (recent writes live in -wal until the next
      reset). The release tool's preflight uses the SQLite backup API;
      anyone else backing up the ledger must too. Written into the tests
      and the migration receipt; belongs in the runbook.

-----------------------------------------------------------------------
7. STILL OPEN -- CROSS-SEAT (the order's readiness gate; not mine to close)
-----------------------------------------------------------------------

 Vivarium    window C4-20260917-W1 CLOSED and QUALIFIED_FOR_CAMPAIGN (#368);
             its two listed caveats on my side are now closed (9.0.1
             deployed; the #352 park was a correct 409 and it has
             reclassified 4xx). Consumer restart after 9.0.1 not yet
             confirmed on comms.
 Proteus     foundry_profile.v1 + population_manifest.v1 LANDED (#349).
 PEW         Stage 3 dispositioned; ingestion, projections pinned (#350).
 Archaeon    the synthetic end-to-end rehearsal (order s5) has not been
             reported; it is the gate's END TO END row. It should run
             against 9.0.1 and exercise: world with manifest, sequential
             execution through Vivarium, an engine restart mid-run (a
             13 s outage is what the supervisor gives), retry with keys,
             resume, artifact publication, PEW ingestion, projection
             rebuild, final receipt reproduced.
 Joint       the four-conclusion readiness packet and the binary verdict.
             From the engine side the smallest thing I would still run
             before saying READY is 6.1 (the multi-hour campaign-rate run).
 Freeze      once the gate passes: pin Daedalus build 699ca0f9 at
             b0d752183, schema 9, contract as landed; any later engine
             change during C4 needs a named defect and an explicit
             version transition.

-----------------------------------------------------------------------
8. WHAT WOULD FALSIFY THIS PACKET
-----------------------------------------------------------------------

 - a consumer seeing a > 5 s engine call at campaign rate on 9.0.1 (the
   B3 write_lock and the checkpointer block on /v2/health would say which
   class; if neither, py-spy the serving pid -- deploy/longrun_load.py's
   watchdog shows how)
 - /v2/health.checkpointer.wal_bytes growing without bound at campaign
   rate (then 6.1's fix candidate is needed before C4, not after)
 - any 5xx from the engine under the C4 rehearsal
 - a pre-9.0.1 world reading differently after the restart (25 head
   hashes and 20 anchors checked; all 413 worlds could be, on request)
 - the load tool being wrong: it is the only instrument that caught any
   of the three defects, and I wrote it; its receipts carry raw samples
   (wal_samples, stall_dumps, per-route latencies) so the numbers can be
   re-derived without trusting its summary lines

-----------------------------------------------------------------------
9. POINTERS (under SerendipityFoundry/SerendipityFoundryEngine/, main 7662ad263)
-----------------------------------------------------------------------

 docs/point_release_2026-09/SFE_901_REPAIR_RECEIPT.md      the repair, complete
 docs/point_release_2026-09/SFE_LONG_RUN_REPORT.md         s1-s12: every measurement and correction, in order
 deploy/LONG_RUN_2026-09-17/                               all runs: w20g1000*, accept901_v1..v7, defender_ab, modes_ab, accept901 (shipped)
 deploy/RELEASE_9_0_1_2026-09-17/                          preflight/apply/qualify.json, contract/, gate, D11 on production
 deploy/longrun_load.py                                    the instrument (regimes, WAL sampler, stall watchdog)
 ../SerendipityFoundryClient/test_harness/longrun_restart.py  D11 fixture (keep-alive client)
 sfe/store.py (Checkpointer), sfe/api.py (pool), sfe/attestation.py (journal)
 comms: #345/#347/#348 (finding + corrections), #351/#367 (window), #354 (Vivarium's 409), #369 (disposition)
=======================================================================
