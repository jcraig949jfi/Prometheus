# SFE 9.0.1 REPAIR RECEIPT -- request-path WAL choke removed (pre-Campaign-4 repair order s1)

    seat        Daedalus[m2-d6ecd70b]      date  2026-09-17
    defect      the engine paid for SQLite WAL maintenance inside the request path
                (SFE_LONG_RUN_REPORT.md s4-s12): per-request connections
                (checkpoint + WAL delete/recreate on nearly every request -> 5-13 s
                stalls, 'database is locked' 500s under two writers); every
                persistent-connection variant that reset the WAL from a request or
                with a writer-blocking checkpoint (5-15 s lock-step stalls, 60 s
                hangs); and, last and only found with a stack, the A6 intent journal
                opening/writing/closing its file per line inside the response path
                (21 s stall). Vivarium hit the first class on production at 15:50:25Z
                (#366: a 60 s POST, write landed).
    build       sha256:699ca0f952448b41555ad2658d0f6f5ef007d1f0bdcc6127395563f0a32264cc
                at main b0d752183. No schema, route, identity or contract-semantics
                change (the contract's engine hash is regenerated after the restart).
    tests       511 (new: request-path pragmas pinned; the checkpointer's PASSIVE /
                idle-TRUNCATE branches and its refusal-not-blocking with a reader
                holding the WAL; pool correctness under in-process concurrency;
                Idempotency-Key on import). D11 restart fixture 16/16.

=======================================================================
1. WHAT CHANGED (all in sfe/store.py, sfe/api.py, sfe/attestation.py, serve.py)
=======================================================================

    pool          a checkout/checkin pool of Foundry (one SQLite connection each),
                  exclusive per request, never opened or closed per request;
                  app.state.foundry_generation retires pooled handles on demand
    pragmas       request-path handles: wal_autocheckpoint=0, journal_size_limit=64 MiB
    checkpointer  one daemon thread, own connection, busy handler OFF:
                  PASSIVE every 2 s (50 ms while the WAL is over 8 MB); TRUNCATE
                  only after 3 s without a write; NEVER a writer-blocking reset
                  under load (measured and rejected: TRUNCATE-when-clean, RESTART
                  at 8 MB, RESTART at 512 MB); state on /v2/health.checkpointer
    A6 journal    day file kept open (write + flush); intent synchronous (on disk
                  before the ledger write); effected/refused via a writer thread;
                  in-memory attestation state unchanged and immediate
    access log    uvicorn logging through a QueueHandler (off the event loop)
    import        Idempotency-Key honoured (Vivarium's 7th route)
    NOT changed   schema 9; 72 routes; identity model; contract semantics; strict
                  bodies; retry semantics (a keyed replay returns the original id)

=======================================================================
2. ACCEPTANCE (order s1), shipped build, scratch engine on the production volume
=======================================================================

    20 worlds x 1,000 generations unless noted; keep-alive client; WAL sampled every
    5 s; stall watchdog (py-spy on the serving pid when a request exceeds 4 s)

    R0_campaign_rate_writer_paced_reader      331.8 s  5xx 0  >5s 0  lock_max 0.015 s  obsPOST p50 q1/q4 0.0/2.0 ms  WAL max    8 MB  ck runs 2920 err 0  restart 1.05 s  anchors 50/50
    R1_seq_writer_paced_reader                127.9 s  5xx 0  >5s 0  lock_max 0.016 s  obsPOST p50 q1/q4 0.0/0.0 ms  WAL max 3321 MB  ck runs  785 err 0  restart 0.55 s  anchors 50/50
    R3_two_writers_no_reader                  131.2 s  5xx 0  >5s 0  lock_max 0.265 s  obsPOST p50 q1/q4 0.0/0.0 ms  WAL max 3402 MB  ck runs  890 err 0  restart 4.86 s  anchors 50/50
    R2_two_writers_tight_reader               254.4 s  5xx 0  >5s 0  lock_max 0.344 s  obsPOST p50 q1/q4 3.1/7.9 ms  WAL max 3417 MB  ck runs 2081 err 0  restart 9.71 s  anchors 50/50

    criteria    0 5xx: MET in all four.  0 calls > 5 s: MET in all four.
                sequential campaign-style writer + paced reader: R0 (2 gen/s,
                600 obs) and R1 (saturating). modest concurrent writers reproducing
                the old defect: R3 (the regime of the original 500s). WAL bounded:
                MET at campaign rate (R0 plateau 8 MB, SQLite restarting it in the
                gaps); under a SATURATING writer (100-240 gen/s, 300-800x any
                campaign) the file grows for the run (3.3-3.4 GB) and restart cost
                scales with it (0.5-9.7 s) -- a documented property, visible on
                /v2/health (wal_bytes, max_wal_bytes_seen), not a defect at
                Campaign 4's rate. checkpointer alive/observable: MET (runs, errors 0).
                restart/recovery fixture: 16/16. idempotent retry semantics
                unchanged: keyed replays return the original id (tests +
                longrun_restart duplicate-post shape); import gained a key.
    throughput  12-24x the deployed engine on the same shapes (R2 254 s vs 3,042 s)

=======================================================================
3. REJECTED ATTEMPTS, PRESERVED (deploy/LONG_RUN_2026-09-17/)
=======================================================================

    f8ae501de  thread-local Foundry per worker: shared a connection across two
               requests (FastAPI runs dependency and endpoint on different
               threads) -> 500 at request 1,751
    de09dc421  pool only: 60 s hang at request 8,570; py-spy: COMMIT blocked behind
               a 344 MB WAL (autocheckpoint inside COMMIT)                   w20g1000_pool/
    v2/v3      pool + checkpointer with TRUNCATE-when-clean: 5-13 s lock-step
               pairs (writer-blocking backfill + fsync); Defender falsified by
               A/B (exclusion changed nothing; CPU flat at stall time)
                                              accept901_v2_3c7c3732/, _v3_, defender_ab/
    modes_ab   RESTART at 8 MB + synchronous=FULL: 1,556 resets, 34 stalls,
               throughput halved                                       modes_ab/M1
    v6         RESTART valve at 512 MB: held writers > 30 s -> busy_timeout -> 500
                                                            accept901_v6_valve_rejected/
    v7         journal still in the response path: R2 5 stalls to 21 s, with the
               stack that ended the hunt           accept901_v7_journal_in_response_path/
    tooling    keep-alive client (ephemeral-port exhaustion), py-spy aimed at the
               serving pid (three empty-stack runs before), a self-inflicted abort
               (I deleted a live run's scratch dir)  -- all kept in the logs

=======================================================================
4. DEPLOYMENT (appended by release_v9.py apply / qualify_v9.py)
=======================================================================

    [appended below]
