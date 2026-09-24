# PEW for Campaign 6 -- observatory storage contract (v0.1, design, nothing built)

    seat        Mnemosyne[m2-9c10ae00], M2; task worktree mnemosyne-boot-2026-09-16
                (merged origin/main e8f90c04d); service at pin e8f90c04d, reader 1.5
    authority   operator directive "SFE CAMPAIGN 6 -- CAMBRIAN EXPANSION / OBSERVATORY
                STRESS" (roles/Mnemosyne/prompts/2026-09-18_campaign6/, MANIFEST beside it)
    read first  Daedalus #456 (SFE_C6_OBSERVATORY_REVIEW_2026-09-18.md, main f42b07422),
                Vivarium #455 (VIVARIUM_LANE_2026-09-18.md, 06b2fa830), Proteus #457
                (Axis O scope, 9b3b002ea). This document is written AGAINST those three.
    status      DESIGN v0.1. No migration written, no table created, no route added. The
                Campaign 4 frozen surface (re-pinned after C4/C5, sha256:bea12eae36fd...)
                is untouched. Campaign 6 changes land as migration 016 + a CAMPAIGN6 frozen
                surface in a named deploy window, rehearsed on the restored copy first.
    currency    2026-09-18

PEW's lane in Campaign 6 is Axis T's STORAGE half and the record of the escalation
protocol: what is kept, at what tier, under what identity, verifiable by whom, and what it
costs. PEW never runs a detector inside a run, never triggers a freeze, never scores
interest, never adjudicates a mechanism. It holds the registry the detectors are frozen in,
the firings they produced, the freezes and replays that followed, the fixture commitments
made before launch, and the census that answers "did the observatory see it".

-----------------------------------------------------------------------------------------------
## 0. Positions on the open cross-seat questions (each changes what PEW builds)

    question                              PEW's stand                                    rules
    Daedalus R1 / Vivarium R1             ANCHORED, never ingested. PEW's own numbers     operator
    T0 placement; segment vs row          say the same as the engine's: today a campaign
                                          observation costs ~2.1 KB in PEW with indexes
                                          (68 MB / 32,938 rows); 1e6 evaluations as rows
                                          is ~2 GB per run across the LAN into the
                                          canonical store, 1e7 is 20 GB. PEW stores ONE
                                          row per T0 SEGMENT ANCHOR (segment digest, n,
                                          first/last logical time, sidecar ref, bytes)
                                          and verifies the sidecar digest when the file
                                          is reachable. The segment (Vivarium R1) is the
                                          right execution unit for PEW too: one
                                          campaign_observation per archived generation /
                                          segment, envelope intact.
    Vivarium R3                           SPLIT. Detectors that can trigger a FREEZE must   Archaeon
    where detectors run                   run where the world state still exists -- in     (owner of
                                          the executor's loop, executor-side, against      thresholds)
                                          the T0 stream as it is produced. PEW is
                                          asynchronous by charter (not a dependency of
                                          execution, not a source of selection or
                                          adaptive stopping) and cannot be the
                                          escalation trigger without breaking that. PEW
                                          HOSTS the detector REGISTRY (frozen pre-launch,
                                          pinned like the projection definitions) and
                                          STORES the firings; RETROSPECTIVE detectors
                                          (over anchored sidecar files, after the run)
                                          are PEW projections: versioned, rebuildable,
                                          read-only, never a trigger. If a retrospective
                                          detector fires on a run that already ended,
                                          that is a "would have been missed" entry
                                          (return item 12), not an escalation.
    Daedalus R3 / Vivarium R2             agree: the planter is a seat that does NOT       operator
    fixture keeper                        operate the campaign (Nemesis by lane;
                                          Rhadamanthus/Pronoia by charter). PEW holds
                                          the COMMITMENT (salted sha256 per fixture +
                                          one over the set), registered BEFORE launch,
                                          immutable, timestamped, with the planter's
                                          identity; never the plaintext, never the key.
                                          The recovery matrix is a PEW projection joining
                                          the REVEAL to firings/freezes, built by a seat
                                          that did not plant.
    Daedalus R2 cross-seat freezes        PEW records a FREEZE as it was written, with a
                                          `scope` field {COMPLETE, PARTIAL} and the list
                                          of subjects NOT frozen and why; a partial
                                          freeze is a first-class fact, not a defect.
    Daedalus R4 anchor interval           1,000 evals is fine for PEW; the loss bound is
                                          reported per run as `unanchored_tail` (evals
                                          after the last anchor when the run ended).
    Daedalus R5 build vs conventions      BUILD the parts that make the record machine-    operator
                                          checkable (D1 provenance, D3 anchors, D5
                                          freeze, D7 sealed fixtures) BEFORE launch. On
                                          conventions PEW can still store everything as
                                          producer events with `kind` in the payload,
                                          but the census (25% floor, firing table,
                                          recovery matrix) becomes a claim about
                                          strings, not a query over typed columns.
    Proteus s1 fingerprint fields         PEW does not need the fields; it needs the
                                          fingerprint's IDENTITY: `proteus.behavior_
                                          fingerprint.v1` as definition_version on the
                                          sidecar segment and a size cap stated in bytes
                                          per evaluation (the anchor row carries bytes).

-----------------------------------------------------------------------------------------------
## 1. What PEW stores, per tier

    tier  what the directive names                     PEW holds                         PEW does NOT hold
    T0    cheap summary for every evaluation           one ANCHOR row per segment:       the fingerprint rows
                                                       segment_id, run/execution ids,    (they live in the
                                                       n, first_lt, last_lt, digest,     evaluator sidecar
                                                       bytes, sidecar_ref, fingerprint   and, per Daedalus
                                                       definition_version, verified_at   D3, anchor in the
                                                       + verified (bool) when PEW could  engine ledger)
                                                       read the file and recompute
    T1    richer trace around unusual events           a TYPED REF (content-addressed)   the trace bytes
                                                       to the artifact, attached to the  (engine artifact
                                                       firing/escalation that caused it  store / blob)
    T2    full lineage/world/event capture after       the FREEZE record: freeze_id,     checkpoints
          escalation                                   trigger firing ids, subjects
                                                       frozen (organism, parent,
                                                       ancestors, siblings, world state,
                                                       pressure history, mutation chain)
                                                       each by checkpoint hash, scope
                                                       COMPLETE/PARTIAL, preserved_at
    T3    replay/counterfactual for adjudication       REPLAY PACKET identity (bundle    the packet bytes
                                                       digest, freeze_id) and one row    (exported once by
                                                       per attempted step A..G with      the engine, run on
                                                       outcome SAME | DIFFERENT |        a scratch engine)
                                                       FAILED | NOT_ATTEMPTED and the
                                                       receipt digest

Ordering invariant PEW checks on ingest and reports (never blocks): for every escalation,
preserved_at(FREEZE) <= first classification/explanation timestamp on the same subject.
"Do not explain the event before preservation is complete" becomes a countable violation
(`explained_before_preserved`), zero expected.

-----------------------------------------------------------------------------------------------
## 2. Detector registry and firings (the frozen-threshold discipline, extended)

The projection registry already does this for readings: a definition is text with a sha256,
a version, an owner, pinned in the frozen surface, and a change is a version transition with
a test that fails on drift. Detectors get the same treatment:

    ew.detector_registry
        detector_name, detector_version      e.g. behavioral_novelty / v1
        owner                                the seat whose science it is (Archaeon), never PEW
        code_identity                        module@blob-sha of the executor-side implementation
        definition_sha256                    over the definition text (inputs, statistic, threshold)
        threshold                            jsonb, verbatim as frozen
        status                               FROZEN | SUPERSEDED | RETROSPECTIVE_ONLY
        frozen_at, frozen_before_campaign    campaign_id (cmp6) -- must precede the campaign's
                                             first segment or the registry row is LATE (flagged)
    the 11 directive detectors + detector_disagreement (Daedalus C4: a 12th detector,
    not a query) + classifier_failure ("none of the above") are rows; PEW refuses to
    store a firing whose (name, version) is not registered -- it is recorded as
    UNTYPED firing with the string kept (the engine's D2 rule), counted, and reported.

    ew.detector_firings  (typed view over producer events of kind DETECTOR_FIRED)
        firing_id (content-addressed), detector_name/version, envelope (campaign,
        execution, segment, world, organism/lineage ids, logical_time), value,
        threshold_at_firing (copied, so a later threshold change cannot re-read
        history), subject refs, t1_ref, freeze_id (null until a FREEZE names it),
        provenance_class of the run (denormalised for the census)

    the firing TABLE (return item 5) is a query: firings by detector x run-provenance x
    campaign phase, with the count of MULTI-detector events (>= 2 independent detectors
    within a logical-time window on the same subject) reported separately from single
    strong anomalies, both preserved.

-----------------------------------------------------------------------------------------------
## 3. Fixture commitments and the recovery matrix (blinding as a store property)

    before launch    the planter registers, via a write-scoped identity of its own:
                     ew.fixture_commitments {commitment_id, planter, campaign_id,
                     n_fixtures, set_digest = sha256(sorted per-fixture commitments),
                     per-fixture commitment = sha256(salt || fixture_descriptor),
                     sealed_at}. Rows are INSERT-only (a trigger refuses UPDATE/DELETE,
                     like sealed_records). Everyone can read that N fixtures exist for
                     cmp6 and when they were sealed; no column says where.
    during the run   nothing. PEW cannot leak what it does not hold. Operating seats
                     (Archaeon, Proteus, Vivarium, Daedalus, Mnemosyne) never see salts.
    after the run    the planter posts the REVEAL: per fixture {salt, descriptor (world/
                     lineage/segment/logical-time window, phenomenon class as planted,
                     expected detector(s))}; PEW recomputes each commitment and the set
                     digest, stores match/mismatch per fixture, and the reveal row is
                     also INSERT-only.
    recovery matrix  a PEW projection (fixture_recovery / v1, definition pinned) joining
                     reveal -> firings -> freezes -> replays in the fixture's window:
                     detected (any registered detector fired in-window) / preserved
                     (a FREEZE names a subject in-window) / escalated falsely (freezes
                     with no fixture and no natural anomaly later adjudicated) /
                     replayed (step A SAME) / causally recovered (a step D-G DIFFERENT
                     consistent with the planted cause) / classified correctly /
                     retained as UNKNOWN_MECHANISM. Built by a seat that did not plant;
                     the definition names the joins so the numbers are re-derivable.
    the important    "a planted event that is missed is more important than a natural
    row              anomaly that is found": missed fixtures are the FIRST rows of the
                     matrix and carry the detectors that were registered and silent.

-----------------------------------------------------------------------------------------------
## 4. Vocabulary PEW enforces as columns (not free text)

    provenance_class   HUMAN_DIRECTED | LLM_PROPOSED | PROCEDURAL | EVOLUTION_GENERATED |
                       MIXED on every C6 row that descends from a run (segment anchors,
                       firings, freezes, observations); UNKNOWN when the producer did not
                       supply it (T3/T4 rule); the 25% LLM-free floor is
                       count(provenance_class in {PROCEDURAL, EVOLUTION_GENERATED} and
                       generator_identity present) over evaluations-by-anchor n, by
                       campaign, as a query, not a claim. `generator_identity` (code
                       identity of the generator) travels with it.
    pressure_source    EXOGENOUS | ENDOGENOUS | UNKNOWN on pressure events / schedule
                       slices as written by the producer.
    classification     the ADJUDICATED reading of an escalated event, versioned like a
                       projection: the vocabulary is the owner's (Archaeon/Harmonia), but
                       PEW reserves three values with fixed meaning that no owner may
                       redefine:
                         UNKNOWN_MECHANISM  -- evidence examined, no stronger class justified
                                               (a RESULT; counts toward UNKNOWN_YIELD)
                         UNKNOWN            -- an owner exists, no classification supplied
                                               (envelope rule; never a result)
                         NULL               -- classification not applicable to this row
                       These never share a column with a measured indeterminate value.
    freeze scope       COMPLETE | PARTIAL (+ not_frozen: [{subject, reason}])
    replay outcome     SAME | DIFFERENT | FAILED | NOT_ATTEMPTED per step A..G
    event kinds        the engine's D2 set; anything else stored as UNTYPED with the
                       string kept, counted in the observatory census.

-----------------------------------------------------------------------------------------------
## 5. Schema delta (migration 016, DRAFT -- written only in a deploy window with producers named)

Additive, nullable, same discipline as 014/015: backup manifest + RESTORE_VERIFIED receipt
before apply; rehearsed on pew_rehearsal (the restored copy) first; rows content-addressed;
UNKNOWN vs NULL as above. No table is created before a producer is named for it (the
2026-09-17 rule: empty tables are decorative).

    ew.telemetry_segments        T0 anchors            producer: Vivarium consumer / engine anchors (D3)
    ew.detector_registry         frozen definitions    producer: Archaeon registers; PEW pins in the surface
    ew.detector_firings          view over producer_events(kind=DETECTOR_FIRED) + index
                                                       producer: executor-side detectors via the outbox
    ew.freezes                   T2 records            producer: engine FREEZE events (D5) via outbox/ledger
    ew.replay_attempts           T3 steps A..G         producer: viv.cli replay-packet receipts (Vivarium 3)
    ew.fixture_commitments       sealed, INSERT-only   producer: the keeper seat (new write identity, R-8)
    ew.fixture_reveals           INSERT-only           producer: the keeper seat
    campaign_observations        + provenance_class, generator_identity, segment_id,
                                 classification, classification_version, pressure_source
    producer_events              + kind (typed, validated against a registered set; UNTYPED
                                 otherwise), + subject_refs jsonb
    projections                  new definitions: fixture_recovery/v1, detector_table/v1,
                                 provenance_census/v1, missed_under_c5/v1 (item 12: the C5
                                 telemetry surface stated as a projection over the same
                                 rows -- best/heldout/level only -- and the set difference
                                 with what C6 firings/freezes preserved)

Routes (campaign_routes, additive): GET observatory/anchors, /firings, /freezes, /replays,
/fixtures (commitments only; reveals after revealed_at), /census; POST stays the single
inbox (pew.events.v1) -- every C6 object arrives as a producer event with a typed kind and
is projected into the typed tables by the reader, so the inbox contract does not change
and the checkpoint/gap/duplicate machinery covers C6 unchanged.

Frozen surface v2: CAMPAIGN6_FROZEN_SURFACE.json = the C4 surface + detector registry
digests + the C6 projection definitions + the vocabulary above; tests/test_frozen_surface.py
gains the second pin. Drift = failing test, as now.

-----------------------------------------------------------------------------------------------
## 6. Cost: what PEW measures and reports (return item 4, PEW's half)

Baseline today (canonical store, 2026-09-18): db 2,948 MB; campaign_observations 68 MB /
32,938 rows (~2.1 KB/row with indexes; measured jsonb 268-433 B/row for wse rows, 1.6-2.5
KB for ssf/survey rows); producer_events 584 kB / 287; projection_rows 9 MB / 2,877.

    measured per C6 run and per phase, written to the release packet:
      bytes in PEW by tier (anchor rows, firing rows, freeze rows, replay rows, refs)
      bytes REFERENCED but not held (sidecar files, artifacts, packets) by digest
      ingest throughput (rows/s through the inbox; segment anchors/s) over the LAN
      to M1 -- the single-writer path the O2 backup and every seat share
      query latency for the six return queries at the campaign's real size
      backup size / restore-verify duration growth (O2 weekly; a C6 that doubles
      the dump doubles the Sunday window -- reported, with the ceiling stated)
    PEW ceilings to pre-register (S1 measures them on the restored copy):
      inbox rate (single POST per event today; a batch inbox is the D4 analogue and
      is the first thing to build if anchors/s exceed it), nightly dump duration
      against the 03:30-04:30 window, and the restore-verify duration against the
      Sunday window. Above any of these the observatory is not blind but the
      RECOVERY PROOF is late, and that is reported as SCALING_HEALTH, not hidden.

-----------------------------------------------------------------------------------------------
## 7. Sequencing (nothing below runs science)

    step  what                                                     needs                 owner
    S0    this contract; Stage 3 criticism from Daedalus (anchor    now                   peers
          payload = D3 schema verbatim?), Vivarium (segment row
          shape; outbox kinds), Archaeon (detector definitions +
          thresholds to register; classification vocabulary),
          keeper seat named (operator R3)
    S1    measure on the restored copy: inbox rate for anchor/     S0                    Mnemosyne
          firing/freeze shaped events at 1e5 and 1e6 evals-
          equivalent; dump/restore growth; six return queries
    S2    migration 016 written + rehearsed on pew_rehearsal;      S1, producers named   Mnemosyne
          reader 2.0 (C6 kinds); projections fixture_recovery/
          detector_table/provenance_census/missed_under_c5 v1;
          keeper write identity R-8 (sha256 in git, value out of
          band); unit + quarantine tests
    S3    deploy window: backup + RESTORE_VERIFIED, apply 016,      S2, operator window   Mnemosyne
          pin advance, restart, requalify (batteries + release
          check + frozen surface v2)
    S4    observatory recall dry run, PEW half: a keeper seals 3    Daedalus S4           keeper +
          fixtures (commitments in PEW), the executor drives                             Mnemosyne
          firings/freezes/replays through the outbox on a scratch
          engine, the keeper reveals, PEW builds fixture_recovery
          v1 -- by a seat that did not plant; the matrix is the
          launch-gate evidence
    S5    CAMPAIGN6_FROZEN_SURFACE pinned; launch gate item "PEW"   S3, S4               Mnemosyne
          GREEN by the S4 matrix + S1 ceilings, not by a checklist

Estimate: S1 0.5 day, S2 2 days, S3 half a day in a window, S4 1 day shared. None starts
before S0's answers and the operator's rulings (Daedalus R1/R3/R5, which decide the shape
of the anchor row, the keeper identity, and whether typed columns exist at all).

-----------------------------------------------------------------------------------------------
## 8. What PEW will NOT do in Campaign 6

Run a detector inside a run; trigger, block or delay a freeze; hold a fixture salt, key
or plaintext before the reveal; hold T0 fingerprint rows; apply a classification (PEW
stores the owner's label with its definition_version; UNKNOWN_MECHANISM is applied by the
adjudicating seat, PEW only guarantees the value cannot be overwritten silently); compute
one interestingness score (the census reports per-detector counts and multi-detector
coincidences separately, never a sum); compare provenance lanes on a winner score.

-----------------------------------------------------------------------------------------------
## 9. Falsifiers of this contract, written to be lost

- If S1 shows the inbox cannot take anchor events at the C6-small rate (1e5 evals / 1,000
  per anchor = 100 anchors per run; trivially yes) but CANNOT take firings at the rate a
  noisy detector set produces them (unknown until Archaeon states thresholds), then
  firings need a batch inbox before launch and the census is late until it exists; say
  so, do not sample.
- If the recall dry run (S4) produces a matrix whose "detected" column is 3/3 while the
  planter's descriptors were never sealed in PEW before the run, the matrix is not
  blind and is discarded: the commitment timestamp preceding the first segment is a
  gate, not a note.
- If the C5-telemetry projection (missed_under_c5/v1) cannot be stated precisely --
  what C5 recorded per evaluation is not fully enumerable from the frozen C4/C5 surface
  -- then return item 12 is UNKNOWN for PEW and is reported as such, not estimated.
- Not worth continuing: if the operator rules T0 INGESTED (Daedalus R1 the other way),
  this contract's anchor design is void, PEW becomes a firehose consumer, and the
  honest answer is that the canonical store on M1 over the LAN cannot hold C6-mid; the
  O3 migration (MNE-46) moves from deferred to prerequisite.

-----------------------------------------------------------------------------------------------
## 10. Conflicts

The seat that will build the store is proposing what the store holds; the incentive runs
toward "PEW holds everything". The guard is s1's right-hand column (what PEW does NOT
hold), the cost numbers in s6 (its own row cost argues against itself), and the rule that
every C6 table needs a named producer before it exists.
