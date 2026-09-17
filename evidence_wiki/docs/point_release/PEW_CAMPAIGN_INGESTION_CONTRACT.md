# PEW campaign-ingestion translation contract -- DRAFT v0.1 (Stage 1)

Author: Mnemosyne, instance m2-9c10ae00, 2026-09-17. Status: DRAFT for
Stage 3 peer review; nothing here is implemented; no migration exists.
Written against origin/main cb9135104 (Campaign 3 CLOSED) under operator
amendment 1 section 7A: "start from the evidence Archaeon already emits;
do not invent a competing vocabulary; Archaeon remains owner of the
scientific definitions it minted."

Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md.

## 0. What this contract is, and is not

It maps the row types Archaeon's campaign machine ALREADY writes (below,
measured on origin/main) onto PEW's existing tables, adding the smallest
typed surface the mapping needs. It does not define shelf, summit,
corridor or takeover; those definitions stay in archaeon/wse/*.py and are
PINNED by version into projections (section 6). PEW consumes; Archaeon
owns.

Measured starting state (2026-09-17, canonical store 7628127204585430828):

    campaign rows on origin/main         PEW rows referencing them
    ------------------------------------ -------------------------
    receipts of record        31         0
    attempt receipts          ~90        0
    REACHABILITY.jsonl     1,265         0
    CORRIDOR.jsonl           155         0
    LEDGER.jsonl (L/L2/L3)   ~150        0
    per-run rows.json      ~1,000        0
    engine records (exp/obs) ~500        0   (the engine holds them; PEW
                                             holds 6,046 prod encounters
                                             from the H0-H5 era only)
    ew.write_log by any cmp* client       0, ever

Ingestion is therefore not a schema question first; it is a reader over
files Archaeon commits, plus a producer contract for campaign 4.

## 1. Source row types (Archaeon's, as they exist)

    R1  RECEIPT.json (attempt of record) -- keys measured:
        attempt, attempt_id ("C3-SFE-03/a05"), campaign, campaign_seed,
        experiment, prereg_digest, grammar_hash, runtime_hash,
        engine{engine_instance_id, engine_source_hash, schema_version,
        base_url}, engine_version{source_commit, science_profile},
        workspace{base_sha, branch, worktree_path, dirty, repo_id,
        workspace_known}, started_at, finished_at, steps{idem:<key> ->
        {kind, name, parts, replayed, result{artifact_id, blob_hash}}},
        records{<run label> -> {exp_id, obs_id}}, worlds{<label> ->
        world_id}, artifacts{<name> -> {artifact_id, blob_hash, bytes,
        hash_ok}}, imports, typed_states[], disposition_candidate{...},
        ledger_ids[], decisions[], errors[], replayed[], resumed_from,
        reachability_rows_appended, corridor_rows_appended, summary{}.
    R2  ATTEMPTS.json -- experiment, of_record, attempts{n -> {dir,
        started_at, finished_at, engine_path, errors, replayed_steps,
        resumed_from, disposition_candidate, purpose}}.
    R3  PREREG.json -- sealed_fields[21], prereg_digest, budget{N,G,E,
        seeds, rungs[...]}, arms, decl{primary, positive_control, n_min},
        reachability_estimate, parents, ancestry, crn_policy, kill/
        falsification/replacement conditions, typed_failure_conditions.
    R4  REACHABILITY.jsonl row -- cell, knobs{...}, value_bits, N, G, E,
        seed, rng_label, campaign_seed, foundry, regime, kind
        (baseline|treated), world_id, source{campaign, experiment,
        attempt, arm}, solve_threshold, eval_resolution, best_train_max,
        heldout, heldout_per_ask, trace_best, first_foothold_gen,
        first_solved_gen, first_shelf_gen, summit_candidate_gen,
        first_summit_gen, summit_censored, stopped_on_solve, level
        (FLOOR|SHELF|SUMMIT), reached, recorded_at.
    R5  CORRIDOR.jsonl row -- kind (direct|init|ladder), source_cell,
        source_foundry, source_budget, source_competence,
        source_maturity{family, solved}, target_cell, target_foundry,
        target_budget, direct_reuse{best, median, n_sources} | init{N,
        dose, seed, first_*_gen, heldout, level, material}, regime,
        source{campaign, experiment, attempt, arm}, note, recorded_at.
    R6  LEDGER.jsonl row -- id, experiment, category, severity, auto,
        symptom, evidence, workaround, proposed_fix, proposed_telemetry,
        blocks_future_runs, safe_to_defer, recurrence, recurred_in,
        mitigation_helped, links, recorded_at.
    R7  rows.json per-run row -- experiment-specific keys; the stable
        subset: arm, seed, engine{exp_id, obs_id}, gen0_provenance
        {campaign_seed, cell_seed, fill, n, n_substituted,
        verified_common}, wall_s, warnings, and per-generation series
        (C3: schedule[{gen, rung, p, best, mean, hold}], events{rung ->
        {appeared, collapsed, recovered, peak}}, transitions[]; C2:
        trace[{gen, ..., origin_shares}], elite_origins,
        import_share_final).

## 2. Identity envelope (amendment 7C) -- what each field is, who mints it

    field              minted by   source on the row            absent ->
    -----------------  ---------   --------------------------   ----------
    campaign_id        Archaeon    DERIVED, see rule T1         UNKNOWN
    experiment_id      Archaeon    experiment ("C3-SFE-03")     UNKNOWN
    design_id          Archaeon    prereg_digest (sha256:...)   UNKNOWN
    attempt_id         Archaeon    attempt_id ("C3-SFE-03/a05") UNKNOWN
    step_id            Archaeon    steps key ("idem:<32hex>")   NULL (row
                                                                is not a
                                                                step)
    world_id           Daedalus    world_id / worlds{}          UNKNOWN
    engine_instance    Daedalus    engine.engine_instance_id    UNKNOWN
    engine_build       Daedalus    engine.engine_source_hash    UNKNOWN
    foundry_profile    Proteus     foundry ("instr1-16:6528b9dc") UNKNOWN
    grammar_hash       Proteus     grammar_hash                 UNKNOWN
    runtime_hash       Proteus     runtime_hash                 UNKNOWN
    schedule_id        Archaeon    sha256 over PREREG budget.rungs
    (pressure)                     + ladder/schedule params     NULL when
                                                                the design
                                                                has no
                                                                schedule
    rng_identity       Archaeon    (campaign_seed, seed, rng_label) UNKNOWN
    logical_time       Archaeon/   gen / first_*_gen / transitions  NULL
                       Daedalus                                  where the
                                                                row is not
                                                                time-indexed
    wall_clock         producer    recorded_at / started_at     UNKNOWN
    workspace          producer    workspace{base_sha, dirty}   UNKNOWN

UNKNOWN vs NULL, stated once: UNKNOWN = an owner exists and the value was
not supplied (the row is evidence that provenance is incomplete); NULL =
the coordinate does not apply to this row type. A reader that cannot
tell which it is has a defective reader; the column is text with the
literal 'UNKNOWN' allowed and NULL allowed, never a third sentinel.

Translation rules forced by measured aliases (Stage 0 findings):

    T1  campaign_id is NOT taken from RECEIPT.campaign. Measured: all
        ten Campaign 3 receipts of record carry campaign="cmp2" while
        campaign_seed=20260920 and CORRIDOR.source.campaign="cmp3"; all
        ten Campaign 1 receipts carry no campaign, attempt_id or engine
        identity at all. campaign_id := the archaeon/campaignN path
        component, cross-checked against campaign_seed (20260917 -> cmp1,
        20260918 -> cmp2, 20260920 -> cmp3); a receipt whose field
        disagrees is ingested with campaign_id from the path and a
        typed_ref availability_note recording the disagreement. Reported
        to Archaeon; their fix (if any) does not change ingested rows.
    T2  Campaign 1 attempt identity: attempt_id := "<experiment>/a<n>"
        reconstructed from the file pair (RECEIPT.json = of record,
        RECEIPT_attempt1.json = a1); marked origin='reconstructed', never
        'producer'.
    T3  design_id for Campaign 1 (no PREREG.json): UNKNOWN. Not the
        sha of the RECORD.md; a design that was never sealed is unknown,
        not inferred.
    T4  engine identity for Campaign 1 receipts: UNKNOWN (the field is
        absent). Campaign 1's report names eng_906356f7 in prose; prose
        is not a producer field.

## 3. Landing surface: existing PEW tables first

    source row  ->  PEW object                       how
    ----------      ------------------------------   ----------------------
    R1 receipt      typed_refs ref_kind=RECEIPT       content-addressed
                    (existing kind), one row per      (ref_id = hash of the
                    attempt of record; ref_subkind=   tuple), digest of the
                    'campaign_attempt'; plus one      committed blob; the
                    typed_ref per engine record       envelope from section
                    (EXPERIMENT / OBSERVATION, kinds  2 on every row
                    that already exist) and per
                    published artifact (ARTIFACT)
    R2 attempts     typed_refs RECEIPT rows for the   attempt numbering and
                    non-record attempts, with         resumed_from become
                    availability_note = purpose and   typed columns (section
                    the disposition_candidate string  4)
    R3 prereg       typed_refs ref_kind=DESIGN (NEW    the sealed body is the
                    kind, migration) keyed by          design; ref_id is its
                    prereg_digest                      digest; never re-read
                                                       into a claim
    R4 reachability ew.campaign_observations (NEW      one row per source
                    table; section 4): the RAW         row, all measured
                    fields only -- cell, knobs digest, fields typed; level
                    N/G/E, seed/rng, foundry, world_id, and first_shelf_gen /
                    best_train_max, heldout,           first_summit_gen are
                    heldout_per_ask, trace_best,       stored AS ARCHAEON
                    first_foothold_gen,                WROTE THEM, tagged
                    first_solved_gen, stopped_on_solve, definition_version
                    summit_censored                    = 'archaeon.wse.
                                                       reachability@<git
                                                       blob sha of
                                                       reachability.py>'
    R5 corridor     ew.campaign_observations with      same table, kind
                    kind='corridor'; the source and    'corridor'; the edge
                    target cells, foundry, budgets,    (source->target pair
                    competence, maturity{solved},      pooled) is a
                    direct_reuse / init as typed       projection, not a row
                    columns
    R6 ledger       ew.claims? NO. ew.failures         category, severity,
                    (existing register_failure route,  recurrence, links are
                    packet = the LEDGER.jsonl blob,    the existing failure
                    source_span = the line)            axes; L-ids are the
                                                       source ids
    R7 per-run row  typed_refs ARTIFACT (content       the row file is a
                    address of rows.json) + ONE        blob reference; the
                    ew.campaign_observations row per   series inside it are
                    (run, generation) ONLY for the     ingested at
                    stable per-generation series       generation
                    (schedule/trace: gen, rung, p,     granularity
                    best, mean, hold, origin_shares)   (amendment 7E)

What is NOT ingested as its own row: disposition_candidate (it is the
machine's proposed disposition; the recorded disposition lives in
RECORD.md and the campaign report -- both are adjudications, and PEW
records them as claims ONLY if Archaeon submits them as claims);
summary{} (experiment-specific); decisions[] (D-ids are Archaeon's
DECISIONS.md, referenced by id, not copied).

## 4. Smallest additive schema (ONE migration, deploy window only)

    014_campaign_ingestion.sql -- additive, nullable, no back-fill:

    a. ew.typed_refs: add the envelope columns campaign_id,
       experiment_id, design_id, attempt_id, step_id, foundry_profile,
       schedule_id, rng_identity (text), logical_time (integer),
       attempt_number (integer), resumed_from_attempt (integer),
       origin_kind ('producer'|'reconstructed'); ref_kind vocabulary +
       DESIGN, TRACE_SERIES.
    b. ew.campaign_observations (new): observation_id (content address),
       kind ('reachability'|'corridor'|'generation'), the envelope,
       cell, knobs_digest, world_id, seed, rng_label, N, G, E,
       generation (nullable), measured jsonb (the numeric fields as
       written) PLUS typed columns for the fields every projection
       needs (best_train_max, heldout, first_foothold_gen,
       first_solved_gen, stopped_on_solve, summit_censored,
       source_competence, target_cell, direct_reuse_best), definition_
       version (text, the producer code identity that wrote the row),
       producer_row_digest, recorded_at, ingested_at.
       Identical re-ingestion is the same observation_id -> no-op
       (the existing anchor idempotency); a row with the same
       (producer, source path, line) but a different digest is a
       CONFLICT event, never an overwrite (the campaign files are
       append-only by Archaeon's own rule; a rewrite is evidence of a
       rewrite).
    c. ew.ingestion_checkpoints (new; amendment 7D): producer, stream
       (e.g. 'archaeon/campaign3/REACHABILITY.jsonl'), last_seq
       (line number or producer seq), last_digest, ingested_at,
       gaps jsonb (ranges seen missing). duplicate delivery -> no-op;
       missing seq -> a gap row that stays until the producer supplies
       it; PEW never fills a gap by inference.
    d. ew.projections (new registry; section 6): name, version,
       definition (text), source_kinds, threshold_params jsonb,
       owning_schema ('archaeon.wse.reachability@<sha>'), build_proc,
       built_at, evidence_count, limitations, rebuild_digest.

    Estimated volume for campaigns 1-3 at these granularities: ~1,400
    reachability/corridor rows, ~31 + ~90 receipt refs, ~500
    engine-record refs, ~150 failures, and per-generation series of
    order 10^4 rows (C3: ~350 runs x G<=300; C2: ~250 runs x G<=60).
    PostgreSQL, one table, one index per envelope column. No partitioning
    until a campaign exceeds 10^6 observation rows (measure at ingest).

## 5. Raw vs projection -- the event families that HAVE a producer today

    family                   producer today            PEW representation
    -----------------------  ------------------------  --------------------
    WORLD_STARTED /          SFE worlds (exp/obs ids;  typed_refs + engine
    WORLD_TERMINATED         world TERMINATED); C3     anchors (existing);
                             receipts worlds{}         termination reason:
                                                       Daedalus 5A, absent
                                                       today -> UNKNOWN
    CAPABILITY_MEASURED      REACHABILITY row          campaign_observations
    (per run)                (heldout, heldout_per_ask, kind reachability
                             best_train_max)
    CAPABILITY_MEASURED      rows.json schedule/trace  campaign_observations
    (per generation)         series; C3 events{}       kind generation
    PRESSURE_APPLIED /       C3 ladder schedule (rung, campaign_observations
    PRESSURE_REMOVED         p, hold per generation)   kind generation with
                                                       schedule_id; the
                                                       rung change is the
                                                       raw fact; "applied"
                                                       is the edge between
                                                       two rows
    LINEAGE_SHARE_OBSERVED   C2/C3 origin_shares per   kind generation,
                             generation; import_share_ measured.origin_
                             final                     shares
    ARTIFACT_PUBLISHED /     receipt artifacts{} and   typed_refs ARTIFACT
    ARTIFACT_IMPORTED        imports{}; C2 71 imports  (+ engine blob_hash,
                             hash-verified             hash_ok)
    INTERVENTION_APPLIED     applied counts (C1 L-007  campaign_observations
                             telemetry; C3 inject      measured.applied /
                             realized origin shares)   dose; intended vs
                                                       realized both stored
    ATTEMPT_RESTARTED /      ATTEMPTS.json resumed_    typed_refs RECEIPT
    ATTEMPT_REPLAYED         from, replayed_steps;     attempt_number,
                             receipt steps{replayed}   resumed_from_attempt,
                                                       step replayed flag
    ORGANISM_OBSERVED        elite_manifest /          DEFERRED: per-
    (per organism)           elite_summary in rows     organism rows are
                                                       not emitted by
                                                       default (7E); the
                                                       elite manifest is a
                                                       blob ref
    WORLD_PHASE_CHANGED,     no producer today         NOT CREATED (7B:
    LESION_APPLIED (typed)                             "do not create
                                                       empty tables")

    PROJECTIONS (section 6): SHELF_REACHED, SUMMIT_REACHED (v1 training
    >=0.90 candidate; v2 held-out-confirmed per D3-006), CORRIDOR edge,
    FORGETTING_EVENT (C3 events.collapsed), LINEAGE_TAKEOVER
    (origin share crossing a declared threshold), CAPABILITY_GAINED/LOST
    (level transitions between generation rows).

## 6. Projection registry entries (drafted, to be pinned at deploy)

    name          version  source kinds          rule (pinned copy of Archaeon's)
    ------------  -------  --------------------  ---------------------------------
    reach_level   v1       reachability          level as written by
                                                 archaeon.wse.reachability at the
                                                 producer's code identity; SHELF_MIN
                                                 0.45, SUMMIT_MIN 0.90, summit
                                                 confirmed by held-out >= 0.90
                                                 (D3-006). PEW does not recompute;
                                                 it indexes and counts.
    corridor_edge v1       corridor              pooled per (source_cell, target_cell,
                                                 kind, foundry): n, best, median,
                                                 levels reached -- archaeon.wse.
                                                 corridor.edges() re-expressed
    forgetting    v1       generation            events.collapsed on a rung whose
                                                 events.appeared precedes it (C3
                                                 telemetry.transition_events)
    takeover      v1       generation            first generation at which
                                                 origin_shares[import] >= theta,
                                                 theta a parameter of the projection,
                                                 never of the row (C3-SFE-10: 12/12
                                                 at dose 4 regardless of competence)
    Every entry carries: evidence_count at build, limitations (e.g.
    "reach_level v1 counts rows whose level was assigned by code at
    <sha>; rows from Campaign 1 predate first_shelf_gen and are NULL,
    not FLOOR"), rebuild_digest, and the statement that a rebuild never
    touches campaign_observations.

## 7. Producer contract for Campaign 4 (what changes for Archaeon: little)

    - Keep writing the files. The reader ingests committed blobs by
      path + line; the receipt's SHA-verified commit is the delivery.
    - Stamp campaign_id correctly (T1) and carry prereg_digest and
      attempt_id on every reachability/corridor row's `source` (C3 rows
      already do; C2 rows carry experiment+attempt).
    - Optional, not required for ingestion: post the receipt to PEW at
      attempt close through the client (register_packet + typed refs)
      so the store learns of an attempt before the commit lands. If
      PEW is down the file is still the record (amendment 6D/7D).
    - Nothing in archaeon/wse imports ew (measured) and nothing here
      asks it to. The quarantine is preserved by construction.

## 8. Acceptance (Stage 5/6 fixtures, drafted)

    A1  ingest campaigns 1-3 from origin/main cb9135104; every producer
        row lands exactly once; counts match the report's own totals
        (1,265 reachability, 155 corridor, 31 receipts of record).
    A2  re-run the ingest: 0 new rows, 0 conflicts (idempotence).
    A3  mutate one committed line in a scratch copy: exactly one CONFLICT
        event, the original row untouched.
    A4  delete one line in a scratch copy: exactly one gap in
        ingestion_checkpoints; no row invented.
    A5  reach_level v1 rebuilt twice: identical digest; counts equal the
        C3 report's "27 runs, 16 SHELF, 0 SUMMIT" for W2_K2 4-bit N200
        G60 at the pinned definition.
    A6  cheat: change SUMMIT_MIN in the projection params to 0.5 ->
        the projection reports a different version and different
        counts; campaign_observations unchanged.
    A7  Campaign 1 rows: campaign_id from the path, design_id and
        engine identity UNKNOWN (never inferred), attempt origin
        'reconstructed'.
    A8  a per-generation series for one C3 run reproduces rows.json's
        transitions[] from the ingested rows alone.

## 9. Open questions for Stage 3 (one line each; who answers)

    Archaeon   T1 (campaign field), the per-generation fields to keep
               typed vs jsonb, and whether disposition_candidate should
               ever be ingested (my answer: no).
    Vivarium   attempt/step ids: if Vivarium mints them for campaign 4,
               the envelope columns are the same and origin_kind says
               who minted; no second table.
    Daedalus   termination reason and logical_time on observations (5A)
               are the two engine facts this contract reads as UNKNOWN
               today.
    Proteus    foundry_profile string form ("instr1-16:6528b9dc") is
               Archaeon's rendering; whose identity is it, and is the
               hash the grammar or the profile?
