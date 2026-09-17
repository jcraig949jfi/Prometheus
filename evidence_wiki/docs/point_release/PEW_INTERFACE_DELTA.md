# PEW interface delta -- point release 2026-09-17 (deployed at 8665b1bdf)

Author: Mnemosyne, instance m2-9c10ae00. Companion: PEW_CAMPAIGN_INGESTION_
CONTRACT.md (the contract this implements), PEW_RELEASE_PACKET.md.
Everything here is ADDITIVE. No existing route, column, battery gate or
producer contract changed meaning. Schema constant 4 -> 5.

## Schema (migration 014, applied 2026-09-17 06:50:07 to db_system_id
## 7628127204585430828; receipt ops/migration_receipts/014_20260917T065006.json)

    ew.schema_migrations        guard + receipt row per migration
    ew.typed_refs               + envelope columns: campaign_id, harness_id,
                                execution_id, design_id, design_kind,
                                attempt_id, step_id, foundry_profile,
                                schedule_id, rng_identity, logical_time,
                                origin_kind (NULL on every pre-existing row)
    ew.campaign_observations    NEW raw table: one content-addressed row per
                                producer row (kinds: reachability, corridor,
                                ledger, receipt, attempt, design, run,
                                generation, engine_record, artifact_ref,
                                import); envelope; typed measured subset;
                                termination/censoring facts; strata jsonb;
                                measured jsonb (the row verbatim);
                                definition_version (producer code identity);
                                source_commit/path/line/blob; reader_version
    ew.ingestion_checkpoints    per (producer, stream): last_seq, digest,
                                commit, reader, rows, gaps (never healed)
    ew.ingestion_conflicts      append-only: same (stream, seq) or committed
                                line with a different digest
    ew.producer_events          the producer-outbox inbox: event_id PK,
                                UNIQUE (producer, stream, seq), kind (text),
                                logical_time, actor, payload, payload_digest,
                                envelope
    ew.projections              registry: name, version, definition,
                                source_kinds, source_code_identity,
                                thresholds, owner_seat, builder_version,
                                built_at, evidence_count, rebuild_digest,
                                limitations, status (BUILT|SUPERSEDED|RETIRED)
    ew.projection_rows          (name, version, row_key) -> payload,
                                evidence_ids[], evidence_count

## Identity envelope (order s4) -- column, owner, absent value

    campaign_id      Archaeon (path+seed, T1)     never absent (NOT NULL)
    harness_id       Archaeon (experiment)        UNKNOWN
    execution_id     Vivarium                     NULL today (no Vivarium row
                                                  has been ingested); UNKNOWN
                                                  once a Vivarium-run harness
                                                  omits it
    design_id        Archaeon prereg_digest /     UNKNOWN (campaign 1: 14/14)
    design_kind      Vivarium spec_hash
    attempt_id       Archaeon                     UNKNOWN; 'reconstructed'
                                                  origin for campaign 1 (T2)
    step_id          Archaeon idem key            NULL (rows are not steps)
    foundry_profile  Proteus (string as Archaeon  UNKNOWN on receipts (the
                     renders it)                  rows carry it)
    schedule_id      Archaeon (sha over PREREG    NULL when no schedule
                     rungs/ladder params)
    rng_identity     Archaeon (seed:cell_seed:    UNKNOWN when absent
                     rng_label)
    world_id         Daedalus                     UNKNOWN / NULL (N/A)
    engine_instance_id, engine_source_hash  Daedalus   UNKNOWN (campaign 1)
    logical_time     generation                   NULL where not time-indexed

## Routes (69 total after; the new ones)

    GET  /api/v1/campaign/observations   selectors campaign_id, harness_id,
         attempt_id, kind, cell, world_id, arm, foundry_profile, stratum
         (json, jsonb containment on strata), generation_min/max; one
         selector required (400); malformed stratum 422; limit <= 2000;
         every read logged
    GET  /api/v1/campaign/summary?campaign_id=     counts only
    GET  /api/v1/projections                       registry
    GET  /api/v1/projections/{name}/{version}      definition + rows;
         row_key_prefix, stratum (containment on payload)
    GET  /api/v1/ingestion/checkpoints, /api/v1/ingestion/conflicts
    POST /api/v1/events  (write scope) one event or a list ->
         accepted | duplicate | checkpoint_mismatch | 422 malformed;
         gap:true when seq skipped (gap recorded on the checkpoint);
         late:true when seq < checkpoint (accepted, checkpoint kept)
    GET  /api/v1/events?producer&stream&after_seq&kind   next_after_seq
    GET  /api/v1/release  schema constant, ontology registry version,
         fossil contract, migrations applied (with backup ids), reader
         version, ingestion contract, projection builder, projection
         registry digest, route digest, db identity
    /api/v1/health now carries `store` (environment, db_system_id,
         db_name, host, attested_at) -- attested BEFORE the port binds

## CLI (task worktree only; never the pinned one)

    python -m ew.campaign_ingest --campaign N [--commit sha] [--receipt p]
    python -m ew.projections build|rebuild-check|list <name> <version>
    python ops/apply_migration.py NNN --backup-id .. --restore-receipt ..
    python ops/pew_backup.py / ops/pew_restore_verify.py  (O2, unchanged)

## Client (ew/client.py)  unchanged this release; fossil methods from 09-16.

## Stage 3 answers folded in (Daedalus #328, Vivarium #330)

    Daedalus D3 (WORLD_EVENT + kind + logical_time + actor): sufficient.
      producer_events stores exactly that shape; kind is text, PEW
      classifies nothing. D8 after_seq: adopted as the read cursor
      (`GET /events?after_seq`) and as the outbox checkpoint semantics.
      D4 manifest_hash / D2 termination: the campaign_observations
      columns termination_reason, horizon, censored, censoring_reason
      exist and read UNKNOWN/NULL until an engine writes them;
      manifest_hash will be an envelope column when D4 ships (additive).
    Vivarium event_id = sha(attempt, step, kind, n): accepted verbatim;
      PEW dedupes on event_id AND (producer, stream, seq); the payload
      digest decides duplicate vs checkpoint_mismatch. UNKNOWN vs NULL
      per column: the table above.
    Archaeon T1: receipts' campaign field is not trusted; rows carry the
      seed-derived id and a note. The producer's fix, if any, will not
      change ingested rows (content-addressed on the producer row; a
      changed row is a new observation plus a conflict record).
    Proteus: foundry_profile carries Archaeon's string "instr1-16:<hex>"
      verbatim, owner Proteus; renaming is Proteus's to rule.

## Not changed (deliberately)

    Thresholds: none owned by PEW. Fossil contract pew.fossil.v2. Closure
    V0. Namespace firewall. Every 09-11 battery gate. The M1 service (dead
    since 09-15) and the M1 backup jobs.
