# SFE RELEASE PACKET -- point release 2026-09 (schema 8 -> 9)

    seat        Daedalus[m2-d6ecd70b]         date  2026-09-17
    engine      https://192.168.1.191:8811   ledger eng_906356f7fb1da180131f9290 (M2 production)
    shipped     build sha256:bc8d3a0caea47efdc766aaa49abdba9a9d1a5ac9dc35f3b722d0aa3397e99153
                commit 1b9286292 (origin/main); deployed 2026-09-17T10:51:30Z; schema 9
    authority   operator: directive -> amendment 1 (scope) -> "IMPLEMENTATION + DEPLOY ORDER
                2026-09-17" (chat, after Campaign 3 closed #326)
    documents   SFE_POINT_RELEASE_REVIEW.md (Stage 0-2), SFE_INTERFACE_DELTA.md (frozen scope +
                amendment lines), SFE_SCHEMA9_MIGRATION_RECEIPT.md, SFE_DEPLOYMENT_RECEIPT.md,
                SFE_RESTART_RECEIPT.md, SFE_LONG_RUN_REPORT.md, SFE_BENCHMARK_RECEIPT.md,
                WORLDLIB_INTERFACE_NOTE.md; receipts deploy/POINT_RELEASE_2026-09-17/

=======================================================================
1. EVERY STAGE-1 ITEM, CLASSIFIED (order s13: nothing quietly dropped)
=======================================================================

    id   item                                          status           where it is
    D1   logical_time on observations (+ sealed in     SHIPPED          observations.logical_time; OBSERVATION_RECORDED
         the event)                                                     payload; read back on 3 routes
    D2   typed termination {reason = stop rule,        SHIPPED          POST .../terminate optional strict body; worlds.
         logical_time, horizon, budget_consumed,                        termination; WORLD_TERMINATED payload; route row
         reference, note}                                               UNCHANGED in the contract (A1)
    D3   sealed generic world events                   SHIPPED          POST .../events -> WORLD_EVENT {kind, logical_
                                                                        time, payload}; idempotent; refused on TERMINATED;
                                                                        declared-kind refusal only when the manifest pins
    D4   manifest envelope                             SHIPPED          WorldCreate.manifest/manifest_schema -> manifest_
                                                                        hash sealed; GET .../manifest; fork inherits
    D5   GET /v2/worlds/{wid}/artifacts                SHIPPED          kind/origin filters; cursor; no bytes (#325 closed)
    D6   fork changed-field diff                       SHIPPED          WORLD_FORKED.changed {field: {parent, child}}
    D7   world labels (opaque producer provenance)     SHIPPED          WorldCreate.labels (<=16 x 64); ?label=k=v;
                                                                        attempt identity is Vivarium's/Archaeon's, carried
    D8   cursor pagination                             SHIPPED          after_seq/limit on events, observations,
                                                                        experiments, artifacts, read/observations; next_
                                                                        after_seq null at end; default lists capped 10,000
                                                                        with truncated=true
    D9   read/session semantics + capabilities +       SHIPPED          GET /v2/capabilities (unauthenticated, session-
         strict-body consistency                                        exempt); tests pin advisory keyless-admitted /
                                                                        wrong-key-refused; 25+ mutating routes refuse an
                                                                        unknown field with 422 (test)
    D10  long-run measurement; retention decision      SHIPPED          deploy/longrun_load.py; numbers in SFE_LONG_RUN_
                                                        (measure)       REPORT.md; retention: DECISION "none", with the
                                                                        numbers that would change it
    D11  restart / duplicate / checkpoint fixture      SHIPPED          test_harness/longrun_restart.py; 16/16 scratch
                                                                        (kill -9 mid-run), 15/15 on production in
                                                                        running-engine mode; part of qualify_v9.py
    D12  dedicated lineage-share slot                  SUPERSEDED       by D3: a WORLD_EVENT of the caller's kind carries
                                                                        requested/realized dose facts (C3 s12 lesson)
    D13  world objects as engine services              REJECTED         amendment 5F; WORLDLIB_INTERFACE_NOTE.md is the
                                                                        handoff for a neutral library
    D14  QD / landscape projection route               DEFERRED         amendment 5G: library first; promote on two
                                                                        independent consumers needing the same projection
    D15  universal FLOOR/SHELF/SUMMIT, thresholds,     REJECTED         order s4; acceptance test greps sfe/*.py for the
         corridors                                                      five words on every run (it caught my own docstring)
    D16  idempotency keys on all 34 mutating routes    DEFERRED         9 of 34 accept one; nobody has named the rest
    --   parent_world_id / fork_point / checkpoint     ALREADY_EXISTED  struck from the delta in Stage 0.4; now ALSO
         head_hash + state_hash                                         documented on /v2/capabilities.checkpoint
    --   idempotent posts, immutable artifacts, cost   ALREADY_EXISTED  Stage 0.4
         events, lineage, attestation, verify-anchor

    Schema 8 -> 9: six nullable columns; migration idempotent; no backfill; 351 pre-v9 worlds
    and 1,622 pre-v9 observations read NULL facts; verified backup + written rollback.
    Routes 68 -> 72 (+4), 0 changed, 0 removed. Contract regenerated + landed; gate 0.
    Tests 483 -> 505 (+22: v9 facts 13, read surface 8, campaign fixture 1).

=======================================================================
2. WHAT WAS VERIFIED, AND HOW (numbers; "appears fine" appears nowhere)
=======================================================================

    unit suite                     505 passed on the merged tree (bc8d3a0c)
    D11 fixture, scratch           16/16 shapes at n=300: relaunch to /v2/version 0.53 s; kill to
                                   port free 1.11 s; identity, chain, cursor resume, anchors intact
    preflight                      8/8; backup sha256 394202ba... 10,995 events, integrity ok
    apply                          12/12 identity checks; outage 20.3 s
    qualification (production)     20/20 (qualify.json): old-schema reads, anchors 20/20, capabilities,
                                   manifest round-trip, logical_time, events ordering + idempotent dup +
                                   undeclared refused, pagination traversal + resume, artifact list,
                                   checkpoint + fork diff, advisory read semantics (200/403/422),
                                   typed termination + 409 after, harness 12/12, isolation 7/7, gate 0,
                                   D11 on the live service
    acceptance fixture (s12)       tests/test_sfe_v9_campaign_fixture.py: a ladder + intended (4) vs
                                   realized (3) import + checkpoint + counterfactual fork + early stop
                                   (99 of horizon 120) reconstructed by a consumer from read routes
                                   alone; the engine's source holds none of the five words; the
                                   caller's words travel through as opaque bytes
    long-run                       see SFE_LONG_RUN_REPORT.md (20 worlds x 1000 generations, 2
                                   producers + 1 reader, restart at full history)

=======================================================================
3. FINAL REVIEW (order s14)
=======================================================================

    What did SFE become responsible for?
        Holding, sealed and queryable, five kinds of FACT it previously could not: when (logical
        time), why a run stopped (termination), what changed in the world and when (WORLD_EVENT),
        which world definition ran (manifest_hash), and who says this world is which attempt
        (labels). Plus: listing artifacts, paging every list, and stating its own semantics on
        /v2/capabilities instead of letting consumers discover them by failure.

    What did it explicitly refuse to own?
        Every interpretation: levels, thresholds, corridors, takeover, capability, dispositions.
        World mechanics (queues, locks, TTL stores). Attempt/step identity. A vocabulary of event
        kinds. A QD archive. The acceptance test makes the refusal mechanical.

    Which Archaeon-local mechanics can now disappear?
        - reading generation out of observation.content by convention -> logical_time column
        - reconstructing "stopped on solve at G" from receipts -> termination facts on the world
        - carrying rung/inject/phase schedules only in trace rows -> WORLD_EVENTs (kinds theirs)
        - naming the world by campaign+cell in prose -> manifest_hash
        - the artifact-id-in-receipt workaround for verification -> GET .../artifacts
        - private client assumptions about session rules -> /v2/capabilities.read_semantics
        None of these is REQUIRED to disappear; Archaeon's runner is the reference implementation
        (amendment s10) and adopts them when Campaign 4 wants them.

    Which remain properly scientific?
        reachability levels and their thresholds; censoring rules; corridor definitions; ladder
        schedules; injection caps and doses; per-ask credit; every disposition. All above the
        engine, all reconstructable from its facts.

    What information can Vivarium now rely on?
        stable world identity incl. manifest_hash and fork_point (its "world_version"); the
        carried label slot for its attempt/execution ids; typed termination on the world row for
        its terminal state; WORLD_EVENT as the realized-import receipt slot; after_seq cursors
        for its own reads; the checkpoint digest definition (counts + head hash, NOT organism
        state) stated on /v2/capabilities so its start bundle cites the right thing.

    What information can PEW ingest directly?
        every list with a monotone cursor and stable ids (event_id + entry_hash; obs_id;
        artifact_id) -> dup = no-op, gap visible; WORLD_EVENT with kind + logical_time + actor
        for RAW classification by producer; manifest_hash, labels, termination as identity-
        envelope coordinates; logical_time on every observation (NULL = NOT_SUPPLIED, never 0).

    What breaks first at 10x Campaign 3 scale?
        Not throughput, not storage, not restart (medians/p95 flat across 83K events;
        102 MB per 100K events; 1 s relaunch). What a consumer sees first is a server-
        wide stall class: 150 of ~115K calls (0.13%) took 5-13 s, reads and writes
        alike, starting ~14 min in -- NOT the SQLite write lock (max wait 1.77 s).
        Candidate mechanism: one shared sqlite3 connection serves every read and
        write with no Python-level lock; a control run without the reader thread is
        in progress. A consumer with a 10 s timeout trips on it; idempotency keys
        make the retry safe. SFE_LONG_RUN_REPORT.md s4.

    Is SQLite still justified by measurement?
        Yes. Flat medians with history, 0 5xx, 0 lock failures, 1 s restart, 102 MB
        per 100K events. The stall class is a connection-handling defect in the
        engine (one shared handle), not a storage-engine limit; the fix is ~40 lines
        (separate read connections in WAL mode) and is the first item of the next
        point release. Retention: NONE; the numbers that would change it are stated.

    Is the engine ready for unattended multi-hour campaigns?
        Attended, hour-scale: yes, with consumer timeouts >= 30 s on engine calls.
        Unattended, multi-hour, with a 10 s-timeout consumer: NO until the read-
        connection fix lands and this tool measures 0 calls over 5 s at this shape --
        0.13% spurious transport errors is ~50 halts/hour for a consumer that halts
        on the first. Said plainly because the alternative is a Campaign 4 that
        parks at 2 a.m. for a reason this packet already knew.

    What became slower or more complex?
        - one JOIN more on /v2/read/observations (experiments) since 4dbcd3fd; measured in the
          qualification at ~20 ms per page of 200
        - WorldCreate carries up to 256 KiB of manifest; the row is read on every world GET
          (identity only; the body has its own route)
        - list routes gained three keys; no consumer parses positionally
        - the schema-8 build can no longer open the ledger (by design)

    What should be removed before the next major campaign?
        - `deploy/adopt_m1_ledger.py` (the M1 ledger stays an archive; the tool is dead code)
        - the canonical-checkout copies of the M2 ledger and key (`var/engine.db`,
          `deploy/m2.key`) -- a separate, explicitly confirmed step
        - the 10,000-row default cap on unbounded lists should become a required cursor on the
          NEXT point release once every consumer paginates

    What is the smallest next engine change that would materially expand scientific reach?
        Idempotency keys on the remaining 25 mutating routes (D16) once Vivarium names which
        its steps need -- it is what makes an unattended, restarting campaign runner safe to
        retry on EVERY call, not only on observations/artifacts/failures. ~60 lines.

    Major version? NOT proposed. Every change was additive and nullable; the evidence does
    not require one.
