# SFE INTERFACE DELTA -- point release 2026-09 (schema 8 -> 9)

    seat        Daedalus[m2-d6ecd70b]      date  2026-09-17
    status      FROZEN at the commit that adds this file. Implementation
                follows this document; a deviation found during
                implementation is recorded here as an amendment line, not
                silently absorbed.
    authority   operator order "IMPLEMENTATION + DEPLOY ORDER 2026-09-17"
                (chat), on top of amendment 1 s5 and the accepted review
                docs/point_release_2026-09/SFE_POINT_RELEASE_REVIEW.md.

=======================================================================
STAGE 3 CLOSE -- answers in hand and how each question was resolved
=======================================================================

    seat       question (#328)                        answer / resolution
    Mnemosyne  D3 shape for RAW classification;       #327: "termination reason and logical_time
               D8 after_seq as ingestion checkpoint;  on observations are the two engine facts the
               D4/D2 as identity coordinates           contract reads as UNKNOWN today"; ingestion
                                                      checkpoint = stable event id + monotone seq,
                                                      dup = no-op, gap = visible. RESOLVED: after_seq
                                                      is the engine's global row sequence (event_seq
                                                      / created_seq), strictly monotone per engine;
                                                      per-world walks are gap-free by construction
                                                      (a gap in the global seq is another world's
                                                      row, so the page also returns next_after_seq).
                                                      Event identity = event_id + entry_hash (sealed).
    Vivarium   D7 attempt ownership; D2 shape;        #330 + IDENTITY_TRANSLATION_CONTRACT v0.1: SFE
               D3 as realized-import slot; D16 keys   "MINTS world/exp/obs/artifact ids; ABSENT/
                                                      proposed for world_version, logical_time";
                                                      attempt is carried, never minted, by SFE.
                                                      RESOLVED: D7 ships as opaque `labels`
                                                      (producer-supplied provenance; the engine
                                                      defines no key). world_version = (checkpoint
                                                      head_hash, state_hash) + fork_point, already
                                                      exposed. D16 stays DEFERRED (no route list
                                                      supplied).
    Proteus    manifest-by-value                      NO ANSWER (seat not yet reviewed, amendment
                                                      s8). RESOLVED BY DEFAULT: the engine validates
                                                      the manifest envelope only and reads no
                                                      organism/foundry field; a later Proteus
                                                      objection cannot be to something the engine
                                                      does, only to what a manifest author writes.
    Archaeon   D1 unit; D3 declared-kind strictness   NO DIRECT ANSWER; C3 report s13 and the
                                                      runner's trace rows show logical time =
                                                      generation for WSE worlds and the rung/inject
                                                      schedule as the event source. RESOLVED
                                                      (reversible, arbiter may overturn): unit is
                                                      declared per manifest (`logical_time_unit`),
                                                      the column is a unitless integer; declared-kind
                                                      strictness applies ONLY when the manifest
                                                      declares `declared_event_kinds` -- absent, any
                                                      kind is accepted. The least-nuisance default.
    Harmonia   optional body on an existing route =   NO ANSWER. RESOLVED EMPIRICALLY before deploy:
               CHANGED?                               generate the contract against a scratch engine
                                                      of the candidate and diff route rows; if
                                                      .../terminate reads CHANGED, D2 ships as a new
                                                      route POST /v2/worlds/{wid}/termination and the
                                                      old route stays byte-identical. (Amendment
                                                      line appended below with the outcome.)

    Disagreements remaining: none recorded. Two seats unanswered (Proteus,
    Archaeon) -- both questions are reversible and resolved by the least-
    committal default; the operator's order says not to stall on naming.

=======================================================================
1. SCHEMA 9 (additive, nullable; migration idempotent; no backfill)
=======================================================================

    table          column            type     null  meaning (a FACT the caller supplied)
    observations   logical_time      INTEGER  yes   caller's logical clock at the observation;
                                                    unit per manifest; NULL = NOT_SUPPLIED
    worlds         manifest          TEXT     yes   canonical JSON of the world definition
                                                    envelope content (opaque to the engine)
    worlds         manifest_schema   TEXT     yes   author's versioned schema name
    worlds         manifest_hash     TEXT     yes   sha256 content hash of `manifest`, engine-computed
    worlds         labels            TEXT     yes   canonical JSON object str->str, opaque provenance
    worlds         termination       TEXT     yes   canonical JSON of the termination facts (s2.B)

    Immutability: manifest*, labels set at creation only (fork children may
    override manifest*, labels at fork). termination set once, at
    terminate. Old rows: all NULL, read as NOT_SUPPLIED / UNKNOWN; no row
    is rewritten. Migration `_migrate_8_to_9`: PRAGMA-guarded ALTER TABLE
    ADD COLUMN x6; running it twice is a no-op. Rollback: the columns are
    unread by the schema-8 build, but the schema-8 build REFUSES a
    schema-9 ledger (have > SCHEMA_VERSION guard) -- so rollback = restore
    the pre-migration backup, never "run the old build on the new ledger".
    Recovery procedure: docs/point_release_2026-09/SFE_SCHEMA9_MIGRATION_RECEIPT.md.

=======================================================================
2. ROUTE / BODY DELTA
=======================================================================

2.A  ObservationCreate (+1 optional field)
     logical_time: Optional[int]   (>= 0; a negative or non-int is 422)
     Read back on GET .../observations, GET .../observations/{id}/measured,
     GET /v2/read/observations as `logical_time`.
     The OBSERVATION_RECORDED event payload gains `logical_time` (null
     when absent) so the fact is sealed in the chain, not only in the row.

2.B  WorldCreate (+3 optional fields)
     manifest: Optional[dict]          object, canonical size <= 262144 bytes
     manifest_schema: Optional[str]    1..128 chars; REQUIRED when manifest given
     labels: Optional[dict[str,str]]   <= 16 keys, key/value <= 64 chars each
     Reserved manifest keys the engine READS (all optional):
       declared_event_kinds: [str]     -> D3 strictness
       logical_time_unit: str          -> documentation only, echoed on reads
     Everything else in `manifest` is opaque. manifest_hash =
     content_hash(manifest) (sfe.ids.content_hash: canonical JSON, key-
     order independent). WORLD_CREATED payload gains manifest_hash,
     manifest_schema, labels. GET /v2/worlds/{w} and list_worlds return
     manifest_schema, manifest_hash, labels (NOT the manifest body);
     GET /v2/worlds/{w}/manifest returns {manifest, manifest_schema,
     manifest_hash}. list_worlds gains `label=<k>=<v>` filter (repeatable).

2.C  ForkChild (+3 optional fields)
     manifest, manifest_schema, labels -- same rules; absent = inherit the
     parent's. WORLD_FORKED payload gains
       changed: {field: {"parent": x, "child": y}} over seed_root,
                sharing_policy, topology_group, manifest_hash, labels
       manifest_hash (the child's), manifest_schema
     `interventions` stays verbatim as today.  (D6)

2.D  Termination  (D2)
     POST /v2/worlds/{wid}/terminate  body OPTIONAL:
       Termination(_Body):
         reason: str                  1..128 chars; the STOP RULE ("budget_exhausted",
                                      "stop_rule:first_solve", "operator", "horizon"),
                                      caller vocabulary; the contract text says it is
                                      never an outcome
         logical_time: Optional[int]  the clock at termination
         horizon: Optional[int]       the logical horizon the run was allowed
         budget_consumed: Optional[dict]   caller's accounting, opaque
         reference: Optional[str]     a caller-side id (prereg, attempt, receipt)
         note: Optional[str]          <= 512 chars
     Stored on worlds.termination; WORLD_TERMINATED payload gains the same
     object (null when no body). Idempotency-Key honoured. If Harmonia's
     gate reads the optional body as CHANGED, the SAME body ships instead
     on a NEW route POST /v2/worlds/{wid}/termination (terminates + records)
     and /terminate stays as it is. [amendment line below records which]

2.E  Generic sealed world events  (D3)
     POST /v2/worlds/{wid}/events
       WorldEventCreate(_Body):
         kind: str                    1..64 chars, [A-Za-z0-9_.:-]
         logical_time: Optional[int]
         payload: dict                canonical size <= 65536 bytes
         refs: Optional[dict[str,str]]   opaque ids the caller wants sealed beside it
       Idempotency-Key honoured (world-scoped, route "world_events").
     Engine behaviour: appends event_type "WORLD_EVENT" to the world's
     chain with payload {kind, logical_time, payload} and refs; refused
     on a TERMINATED world (write-lifetime rule); refused with 422
     `undeclared_event_kind` when the world's manifest declares
     `declared_event_kinds` and `kind` is not in it; otherwise any kind.
     Returns {event_id, event_seq, world_index, entry_hash, kind}.
     The engine never reads `kind` for meaning. No engine-side kind
     vocabulary exists; the words SHELF/SUMMIT/CORRIDOR/TAKEOVER/
     GENERALIZATION do not appear in engine code (acceptance test).

2.F  GET /v2/worlds/{wid}/artifacts  (D5)
     query: kind, origin (NATIVE|IMPORTED), after_seq, limit
     returns {artifacts: [_artifact_dict + created_seq], next_after_seq,
              truncated}
     owner-scoped like every world GET.

2.G  Cursor pagination  (D8)
     Routes: GET .../events, GET .../observations, GET .../experiments,
     GET .../artifacts, GET /v2/read/observations.
     Params: after_seq: int >= 0 (default 0 = from the start), limit:
     1..1000 (default 200 when after_seq is given).
     Order: ascending by the row's global sequence (events.event_seq;
     observations/experiments/artifacts .created_seq).
     Response adds: next_after_seq (the last row's seq; null when the page
     is not full, i.e. end of stream) and `truncated` (see below).
     UNCHANGED DEFAULTS when neither param is given, except:
       events: still newest-100 DESC (unchanged);
       observations/experiments: still "all", BUT capped at 10,000 rows
       with truncated=true beyond the cap (no existing world is near it;
       the deploy receipt records the max per-world count at migration).
     Contract: optional query params -> required_query unchanged.
     Ingestion checkpoint (Mnemosyne 7D): store next_after_seq; resume
     with after_seq = it; a duplicate delivery re-reads the same rows
     with the same event_id/entry_hash (dup = no-op on stable ids).

2.H  GET /v2/capabilities  (D9)
     unauthenticated, session-exempt (like /v2/version and /v2/health).
     {api, schema_version, engine_source_hash, engine_instance_id,
      session_enforcement, science_profile, max_artifact_bytes,
      read_semantics: {advisory: {no_key: "ADMITTED_AUDITED",
                                  wrong_session_key: "REFUSED",
                                  foreign_engine_key: "REFUSED",
                                  malformed: "REFUSED"},
                       strict:   {no_key: "REFUSED_ON_STRICT_SESSIONS", ...}},
      strict_bodies: true,
      vocabularies: {outcomes, evidence_classes, evidence_roles,
                     sharing_policies, world_states, event_types (engine-
                     owned, incl. WORLD_EVENT), artifact_origins},
      limits: {page_limit_max: 1000, list_default_cap: 10000,
               manifest_bytes: 262144, world_event_payload_bytes: 65536,
               labels: {keys: 16, chars: 64}},
      features: {logical_time, typed_termination, world_events,
                 manifest_envelope, labels, artifact_list,
                 cursor_pagination, fork_changed_fields}: true,
      checkpoint: {state_hash_definition: "content_hash over per-table
                   row counts + head_hash; NOT organism state (the engine
                   holds none)"}}
     Read semantics are ALSO written into docs and asserted by tests:
     tests/test_sfe_read_semantics.py (advisory: keyless admitted, wrong
     key refused, foreign-engine key refused).
     Strict-body consistency: tests assert every mutating route answers
     the SAME error class (422, error "validation") to an unknown field.

=======================================================================
3. UNCHANGED BY DESIGN (so nobody looks for it)
=======================================================================

    - No engine-side level, threshold, corridor, takeover or capability
      concept (order s4). Acceptance test greps sfe/*.py for the five
      words.
    - No dedicated lineage-share table: a WORLD_EVENT of the caller's
      kind carries requested/realized dose facts (order s5.A).
    - Existing routes' default responses byte-compatible except the
      documented 10,000 cap and the added keys.
    - Sessions, auth, isolation, budgets, families, claims, measurements,
      attestation: untouched.

=======================================================================
4. DEPLOY SEQUENCE (order s7-s9)
=======================================================================

    1. tests green on the merged tree; candidate hash recorded
    2. scratch engine of the candidate; Harmonia's generator vs LIVE for
       the diff (routes added/changed) -> decides 2.D's route form
    3. pre-deploy: descriptor + backup + "nobody writing" check
       (deploy/preflight_release.py, receipted)
    4. advance pinned worktree; stop; watchdog starts; migration 8->9
       runs at first open; record identities (order s7 list); STOP if any
       identity differs unexpectedly
    5. contract regenerated against the new live + scratch; gate 0; land
    6. qualification (order s9 list) + long-run fixture; receipts
    7. release packet with SHIPPED / DEFERRED / REJECTED / SUPERSEDED /
       ALREADY_EXISTED per Stage-1 item

=======================================================================
AMENDMENT LINES (appended during implementation; never edited above)
=======================================================================
