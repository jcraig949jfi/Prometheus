+============================================================================+
|  PEW POINT RELEASE PACKET -- 2026-09-17                                    |
|  "PEW is now capable of preserving and querying the evidence from a real  |
|   SFE campaign without participating in the evolutionary or scientific    |
|   selection loop."                                                         |
|                                                                            |
|  Author : Mnemosyne (memory and evidence substrate), instance m2-9c10ae00, |
|           host SPECTREX5 (M2)                                              |
|  Build  : 8665b1bdf653a35912b1fa450c6cbe7c3d401c34, deployed 07:07:30 -0400 |
|  For    : the operator (program gate, order s22), Daedalus, Vivarium,      |
|           Proteus, Archaeon, Harmonia; external reviewers                  |
|  Status : DEPLOYED, RESTARTED, REQUALIFIED; readiness disposition below    |
|  Self-contained: every load-bearing number is inline; paths and SHAs for  |
|  anyone with the repository.                                               |
+============================================================================+

0. THE STATEMENT, AND WHAT BACKS IT
-----------------------------------------------------------------------------
Before this release the measured answer to the central question (order
s2) was NO: three campaigns' worth of typed evidence, zero rows in PEW.

After it, measured on the deployed build against the canonical store:

  ingest     campaigns 1-3 read from their committed files at one commit
             into 26,636 content-addressed observations (cmp3 19,436;
             cmp2 5,629; cmp1 1,352; four other producers 219); a second
             pass of each campaign adds 0 rows; a reader upgrade refreshes
             the envelope of 20,288 rows and touches no producer row
  identity   campaign from seed (every C3 receipt's "cmp2" overruled and
             noted), attempts numbered or marked reconstructed (1,230 in
             campaign 1), design/engine identity UNKNOWN where the producer
             wrote none (campaign 1: 14/14, 102 rows) -- never inferred
  projection reach_level v1 and corridor_edge v1 pinned to Archaeon's code
             identities; the pinned copy of the level rule agrees with the
             producer on 1265/1265 rows; reach_level v0 (the campaign 1-2
             reading) coexists as SUPERSEDED and disagrees on 156 rows,
             126 of them the D3-006 class; all three rebuild to identical
             digests, and v1's digests were identical when built on a
             different cluster from a restored copy
  query      by campaign / harness / attempt / cell / stratum (jsonb
             containment on producer-named factors: quality, dose,
             n_imported, cap, table, climber, ...) over the API; the s18
             questions answered with the report's own numbers (11/12
             general; d8/d16 measured; 112 mature / 112 control / 14 none
             with intended == realized dose; 321/486 censored; 2 tables x
             2 climbers)
  durable    ingestion checkpoints per stream (278), conflicts table
             (0), producer-event inbox with accepted / duplicate /
             checkpoint_mismatch / 422 and visible gaps; migration 014
             receipted against a backup taken 4 min before it and a
             restore proven before it; post-migration backup restored on
             the M2 cluster: 171/171 tables, loss {}
  off the    nothing in archaeon/wse imports ew (measured, unchanged);
  tick path  no thresholds live in PEW; PEW is reached only by a CLI
             reader over committed files and by an asynchronous inbox

1. WHAT SHIPPED (order s23 classification)
-----------------------------------------------------------------------------
    item                                   class            where
    -------------------------------------  ---------------  ---------------
    campaign ingestion reader              SHIPPED          ew/campaign_ingest.py (1.1)
    migration 014                          SHIPPED          migrations/014, ops/apply_migration.py
    provenance envelope                    SHIPPED          typed_refs cols + campaign_observations
    ingestion checkpoints                  SHIPPED          ew.ingestion_checkpoints (+conflicts)
    raw / projection separation            SHIPPED          campaign_observations vs projections
    reach_level v1                         SHIPPED          ew/projections.py (pinned)
    corridor_edge v1                       SHIPPED          ew/projections.py (pinned)
    projection registry                    SHIPPED          ew.projections / projection_rows
    Campaign 3 end-to-end ingestion        SHIPPED          receipt PEW_CAMPAIGN3_INGESTION_RECEIPT.md
    restart / requalification              SHIPPED          PEW_RESTART_RECEIPT.md
    post-migration backup/restore          SHIPPED          PEW_POST_MIGRATION_RESTORE_RECEIPT.md
    producer-event inbox (outbox half)     SHIPPED          POST/GET /api/v1/events
    store attested before bind (s16)       SHIPPED          ew/service.py, ew/db.py attest_store
    useful query indexes                   SHIPPED          8 indexes incl. two GIN
    campaign/stratum summaries (pure)      SHIPPED          /campaign/summary; pooled rows in reach_level
    factual campaign query helper          SHIPPED          integration/campaign3_queries.py
    reach_level v0 (superseded reading)    SHIPPED          coexistence demonstrated on 1,265 rows
    campaigns 1-2 ingestion                SHIPPED          with defects preserved
    identity guard, idempotent writes,     ALREADY_EXISTED  batteries E0-E14, seam, closure,
    batch atomicity, availability rebuild                   lineage, h0h5 (all green after)
    O2 backup/restore                      ALREADY_EXISTED  kept running throughout
    takeover_v1, forgetting_v1             DEFERRED         evidence ingested (origin shares,
                                                            events{}); threshold is Archaeon's
                                                            to state
    typed_refs resolution of campaign      DEFERRED         engine records carry ids only;
    engine records (content digests)                        resolution needs the engine's
                                                            GET artifacts route (Daedalus D5)
    automated explanation surface          DEFERRED         order s20
    per-organism firehose                  DEFERRED         order s9
    unproduced event families              DEFERRED         inbox accepts any kind a producer
    (WORLD_PHASE_CHANGED, LESION_APPLIED)                   sends; no empty tables
    termination reason / logical_time      DEFERRED         columns exist; values UNKNOWN until
    from the engine                                         Daedalus D1/D2 ship
    ONTOLOGY_VERSION constant (MNE-19)     DEFERRED         reported honestly in /release
    PEW-owned scientific thresholds        REJECTED         none exist
    synchronous PEW dependency             REJECTED         reader is a CLI; inbox is async
    Redis                                  REJECTED         PostgreSQL, measured sufficient
    rewriting source evidence              REJECTED         content-addressed rows; conflicts
                                                            are recorded, never resolved
    PEW feeding live selection             REJECTED         no import path exists (measured)

2. THE NUMBERS THAT MATTER (exact, provenance grade: measured on the
   deployed build unless marked)
-----------------------------------------------------------------------------
    rows ingested                26,636 (cmp3 19,436 / cmp2 5,629 / cmp1 1,352)
    second-pass duplicates       0 (three campaigns, six runs)
    conflicts                    0
    UNKNOWN identities (cmp3)    foundry_profile 45, engine_instance_id 21,
                                 design_id 3, rng_identity 199
    reconstructed (cmp1)         1,230 rows
    projection agreement         1265/1265 (pinned rule vs producer label)
    v0 vs v1 disagreements       156 rows (126 D3-006 class, 30 sub-0.5 shelf)
    release check                15/15 (canonical); 14/15 on the restored
                                 copy, R0 failing by design
    batteries after restart      17/17, 12/12, 19/19, 14/14+1 SKIP, 16/16
    unit tests                   30 passed, 2 skipped (live scripts opt-in)
    base-role self-test          11/11
    migration                    014 at 06:50:07; DDL only; re-apply no-op
    post-migration restore       171/171 tables, 5,795,655 rows, loss {},
                                 chain identical, 204.9 s
    storage                      campaign_observations 53 MB; dump +3.26 MB
    ingest time                  C3 ~18 s, C2 ~10 s, C1 ~3 s (LAN store)
    restart                      07:07:30; search ready +4.3 s; first ok
                                 tick 07:08:01

3. STAGE 3 STATE (order: freeze after peer review)
-----------------------------------------------------------------------------
    Daedalus #328   answered in PEW_INTERFACE_DELTA.md: D3 shape adopted
                    for the inbox; D8 after_seq adopted; D2/D4 slots exist
                    and read UNKNOWN until the engine writes them.
    Vivarium #330   answered: event_id sha(attempt, step, kind, n) accepted;
                    UNKNOWN/NULL per column tabled; harness_id/execution_id
                    names adopted from Vivarium's A1.
    Archaeon        T1 (receipt campaign field) reported; the reader does
                    not depend on a fix; arbiter on nothing so far -- no
                    ownership dispute arose.
    Proteus         foundry_profile string form carried verbatim; awaits
                    Proteus's review (amendment s8) for naming.
    Harmonia        additive routes only; conformance readers that declare
                    their routes are unaffected.
    Objections not yet received would land as reader/projection VERSIONS,
    not as rewrites: the envelope columns are nullable and additive.

4. READINESS DISPOSITION (order s22)
-----------------------------------------------------------------------------
    PEW point release: DEPLOYED, RESTARTED, QUALIFIED on the canonical
    store at build 8665b1bdf. Campaign-qualified for INGESTION of an
    Archaeon-runner campaign from committed files (proven on three) and
    for asynchronous producer events (proven with a synthetic producer;
    no real producer has posted yet). Not a dependency of any campaign's
    execution. Backups: O2 live, two nightly cycles pending; O3 deferred
    (MNE-46).

5. SELF-CRITIQUE (order s24), answered against the deployed build
-----------------------------------------------------------------------------
    Did campaign ingestion create a second scientific vocabulary?
      No new scientific terms: kind names are row TYPES (reachability,
      corridor, run, generation); levels, thresholds and factor names are
      the producer's, carried verbatim. One risk kept visible: my strata
      keys (budget_class, row_kind) are PEW-named aggregates of producer
      fields; they are documented as such in the contract.
    Can every projection be rebuilt from source evidence?
      Yes: three rebuild-checks equal, and equal across clusters.
    Can two contradictory projection versions coexist honestly?
      Yes: reach_level v0 and v1 disagree on 156 of 1,265 rows and both
      stand with their thresholds and code identities; v0 is SUPERSEDED,
      not deleted.
    Did UNKNOWN survive, or did migration manufacture certainty?
      Survived: 268 UNKNOWN cells in cmp3, 745 in cmp2, 290 in cmp1;
      migration 014 wrote NULL (not carried) on every pre-existing row
      and UNKNOWN nowhere.
    Can campaign evidence be joined without parsing prose?
      Yes for identities, strata and measurements; NO for the recorded
      disposition, which lives in RECORD.md prose by design (it is an
      adjudication, not ingested).
    Can PEW distinguish measurement from interpretation?
      Raw tables carry level_as_written and disposition_candidate as the
      producer's labels with the producer's code identity; every derived
      reading is in projection_rows with a version. The observations
      route says so on every answer.
    Does ingesting Campaign 3 change any live experiment behavior?
      No path exists: archaeon/wse imports nothing from ew (measured
      today), the reader is a CLI over git, and nothing in Archaeon's
      machine reads PEW.
    Could a PEW outage still lose scientific evidence?
      Campaign files: no (git). Producer events: only if a producer has
      no outbox; Vivarium's is the other half (amendment 6D). The
      inbox's answers (accepted/duplicate/mismatch/gap) are typed so an
      outbox can replay safely.
    Can the canonical store be recovered independently of M1?
      Yes, re-demonstrated after the migration: 171/171 tables on the
      M2 cluster from an M2-owned dump.
    What fails first at 10x Campaign 3 evidence volume?
      Per-generation rows (16,700 for C3 -> ~170K at 10x): fine for
      PostgreSQL; the reader's per-row INSERT (18 s for 20K rows over the
      LAN -> ~3 min) becomes the first annoyance, then the projection
      rebuild's in-memory pass. Nothing architectural before 100x.
    Which query is still expensive enough to require architectural work?
      None measured; the GIN indexes on strata/measured make stratum
      containment cheap. The unmeasured one is a per-generation join
      across many runs at 100x; measure then.
    Is PostgreSQL still sufficient by measurement?
      Yes: 53 MB for three campaigns; the whole cluster dump grew 3 MB.
    Smallest next PEW change that would materially help Campaign 4
    analysis?
      Resolve engine records (exp_id/obs_id/artifact_id) to content
      digests through the engine's read routes (Daedalus D5/D8) so an
      observation row points at bytes, not just ids; then takeover_v1
      once Archaeon states the threshold.

6. WHAT WOULD FALSIFY THE STATEMENT, AND WHAT SHOULD STOP
-----------------------------------------------------------------------------
    - a Campaign 4 row that the reader cannot ingest without a code
      change (the reader is keyed to Archaeon's current file shapes; a
      reshaped receipt is a reader version, and the contract says so);
    - a projection whose rebuild digest changes with no evidence change
      (would mean a hidden input; none observed);
    - any import of ew from a producer's live loop: now a fixture,
      tests/test_quarantine.py (scans archaeon/wse, campaign1-3, the SFE
      engine and proteus; cheat control sees a planted import; 2/2);
    - "not worth continuing": if Archaeon's analysis keeps reading
      REACHABILITY.jsonl directly and never queries PEW, the ingestion is
      a mirror nobody looks in. The first consumer is the test.

7. ARTIFACTS
-----------------------------------------------------------------------------
    docs/point_release/  PEW_INTERFACE_DELTA.md, MIGRATION_014_RECEIPT.md,
                         PEW_DEPLOYMENT_RECEIPT.md, PEW_RESTART_RECEIPT.md,
                         PEW_CAMPAIGN3_INGESTION_RECEIPT.md,
                         PEW_PROJECTION_REBUILD_RECEIPT.md,
                         PEW_POST_MIGRATION_RESTORE_RECEIPT.md, this packet;
                         PEW_CAMPAIGN_INGESTION_CONTRACT.md,
                         PEW_STORE_LOCATION_DISPOSITION.md,
                         PEW_POINT_RELEASE_REVIEW.md (Stage 0-2)
    code                 ew/campaign_ingest.py, ew/projections.py,
                         ew/campaign_routes.py, ew/service.py, ew/db.py,
                         migrations/014_campaign_ingestion.sql,
                         ops/apply_migration.py
    tests                tests/test_campaign_ingest.py (8),
                         tests/test_projections.py (4),
                         tests/test_quarantine.py (2), plus the existing
                         suites; integration/campaign_release_check.py
                         (15 gates), campaign3_queries.py
    receipts             integration/campaign_release_results.json,
                         campaign3_queries_results.json, the five battery
                         results, ops/restore_verification.json,
                         ops/migration_receipts/014_*.json
    commits              8216dd3de (candidate), e8683ea3f (deployed),
                         and their merges e98d2ee8c, 8665b1bdf on main
    deployed             pin 8665b1bdf, pid 19480, 07:07:30 -0400

+============================================================================+
|  END. The release is a mirror of the campaigns' own evidence with its     |
|  provenance intact. If nobody queries it, say so and it stops here.       |
+============================================================================+
