# Identity translation contract -- Archaeon campaign runner <-> Vivarium (<-> SFE, PEW, Proteus)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-17 (Vivarium m2-fce3fe0b). Point-release Stage 0/1 document
under Operator Amendment 1 s6.A: "Document the relationship ... Do not merge
the hierarchies unnecessarily. Publish the join. Use UNKNOWN where no owner
exists." Version: contract v0.1 (proposed; Stage 3 review by Daedalus,
Mnemosyne, Proteus and Archaeon pending). Nothing here is implemented.

Vocabulary used below

    OWNER        the seat whose code MINTS the value (never a copy)
    CARRIER      a seat that stores the value verbatim beside its own records
    UNKNOWN      the value has an owner but this seat cannot know it at write
                 time (recorded as the literal UNKNOWN, never guessed)
    N/A          the identity does not apply to this seat's object
    ABSENT       nobody mints it today (a gap, named as such)

Two facts shape the whole table:

  1. Archaeon's runner and Vivarium model DIFFERENT hierarchies and both are
     legitimate. Archaeon: campaign > experiment (harness) > design (sealed
     prereg) > attempt (aNN) > step (keyed engine/local call) > rows. Vivarium:
     family/candidate set (optional) > experiment ROW (uuid) > sealed spec
     (spec_hash) > repeat (index) > observation. A Vivarium row is exactly one
     Archaeon-shaped "attempt of one world"; an Archaeon attempt spans many
     worlds and sessions. The join is stated per identity; the hierarchies are
     not merged (Amendment s6.A).
  2. Engine (SFE) identities are the only ones both producers already share
     verbatim: world_id, exp_id, obs_id, artifact_id, work_id, engine_instance_id,
     engine_source_hash, session_id. Every cross-seat join that exists today
     goes through them.

## 1. The table

    identity (section D)   Archaeon runner (today)                     Vivarium (today)                              SFE          PEW                  Proteus       OWNER      join / translation
    --------------------   -----------------------------------------   -------------------------------------------   ----------   ------------------   -----------   --------   -------------------------------------------
    campaign_id            CAMPAIGN["campaign"] = "cmp1|cmp2|cmp3";    ABSENT as a column. Nearest: created_by       N/A (client  encounter_id prefix   N/A           Archaeon   viv row -> campaign: created_by + the
                           receipt.campaign; ledger prefix L/L2/L3;    ("archaeon", "archaeon:C_frozen_S17"),        name per     by convention                                producer's own key (source_evidence);
                           engine client name cmp{N}-archaeon          source_evidence.policy_version, family_id     campaign)    (ENC-archaeon-...)                           add a carried `campaign_id` column (B)
    experiment_id          Experiment.ID "C{N}-SFE-NN" (a HARNESS,     experiment_id uuid (one ROW = one execution   exp_id       run_id "exp:wrk"     N/A           BOTH,      NOT the same thing. Archaeon's is a
                           many worlds, many attempts)                 of one world)                                  (per world)  (per fossil)                       distinct   design container; Vivarium's is one
                                                                                                                                                                      meanings   attempt of one world. Translation:
                                                                                                                                                                                 Archaeon experiment -> {viv rows} via
                                                                                                                                                                                 family_id (carried) ; never equate the ids
    design_id              prereg_digest (sha over the sealed PREREG   spec_hash "sha256:..." over canonical spec     N/A          producer.design_hash  N/A           BOTH       Archaeon design >= 1 Vivarium spec:
                           fields; keys every step)                    (viv/spec.py; identical algorithm to sfe/                  (viv/design.py)                               a prereg names cells, each cell one
                                                                       ids.content_hash, tested)                                                                                spec. Join: prereg carries the list of
                                                                                                                                                                                 spec_hashes it will submit (C: start
                                                                                                                                                                                 bundle); viv carries prereg_digest as
                                                                                                                                                                                 source_evidence.design_id (CARRIER)
    attempt_id             "<experiment>/aNN" (numbered per harness    attempt_id == experiment_id (viv/runner.py:   N/A          N/A                  N/A           BOTH       one Archaeon attempt = a SET of viv rows;
                           dir; ATTEMPTS.json; of_record pointer;      376): one row is one attempt; a re-issue is                                                              carried as source_evidence.attempt_id
                           resumed_from)                               a NEW row with replication_of = old row                                                                  today; a first-class attempt table with
                                                                                                                                                                                 parent_attempt is Stage-1 item B
    step_id                step_key(experiment, prereg_digest, name,   ABSENT as a record. Nearest: loop stages       Idempotency- N/A                  N/A           Archaeon   viv item B: step log keyed
                           *parts) = "idem:" + 32 hex; also the engine (claim/validate/build/dispatch/collect/         Key echoed                                      (today)    (spec_hash, name, parts) with the same
                           Idempotency-Key                             finalize) and per-repeat obs; engine idem      on POSTs                                                   "idem:" derivation so a step is joinable
                                                                       key "viv:<attempt>:<stage>:<n>" (runner:561)                                                             to its engine POST by the key itself
    world_id               receipt.worlds[name] (engine wld_...)       row.result_summary.world_id / RunResult.       MINTS        sfe_world_id,        N/A           SFE        verbatim; the universal join
                                                                       world_id; world NAME = "viv-<spec_hash[7:23]>"              world_id
    world_version          ABSENT (a world is created and terminated   ABSENT                                         ABSENT       ABSENT               N/A           SFE        Amendment s5.A: checkpoint state digest /
                           within one attempt)                                                                        (proposed)                                      (proposed) fork_point; Vivarium CARRIES once minted
    organism_id            Proteus manifests inside artifacts; per-    pew.players[] declared by the requester        N/A          players[]            MINTS         Proteus    verbatim; Vivarium never mints (charter)
                           genome ids in trace rows                    (spec); never minted
    genotype/runtime hash  receipt.runtime_hash, grammar_hash (from    ABSENT on the row (Proteus's values travel     N/A          UNKNOWN unless       MINTS         Proteus    add two carried slots on the start bundle
                           proteus.foundry.identity / grammar)         inside artifact bytes only)                                 supplied                                       (C); UNKNOWN when a kind has no organism
    lineage_id             gen0_provenance, init_pop substitutions,    ABSENT                                         N/A          parent_player,       MINTS (mint   Proteus    carried only; Vivarium records realised
                           origin share per generation (C3 group F)                                                                mutation_ref         record 09-16)            share as a SUPPLIED observation (G)
    artifact_id            receipt.artifacts[name] {artifact_id,       artifact slot {digest, artifact_type,          MINTS        artifact refs        N/A           SFE        join by DIGEST (both sides canonical
                           blob_hash, declared} canonical (D.canon)    schema_version, codec, expected_bytes,                      in resources                                  sha256 hex); artifact_id is the engine's
                                                                       interface_id} + artifact_locators                                                                        address, digest is the identity
    observation_id         receipt.records[key] {exp_id, obs_id}       RunResult.obs_ids[] per repeat                 MINTS        sfe_event_id /       N/A           SFE        verbatim
                                                                                                                                   entry hash / seq
    event_id               ABSENT (receipt is a document, not events)  research_experiment_events.event_id bigserial  event seq    fossil anchor        N/A           each seat  no cross-seat join today; the PEW outbox
                                                                       (queue-local); no producer-side stable id     (ledger)     (event_id, seq)                     mints its  (D) mints a stable producer event_id =
                                                                                                                                                                      own        sha(attempt, step, kind, n) so duplicate
                                                                                                                                                                                 delivery is a no-op and a gap is visible
    pressure/schedule id   prereg fields (schedule inside the sealed   inside experiment_spec.work.payload (hashed)   ABSENT       N/A                  N/A           Archaeon   ABSENT as a stand-alone identity on every
                           body); ladder/rung schedules in harness                                                  (manifest    (proposed            (world       (today)    side; Amendment s5.B world manifest_hash
                           code                                                                                       proposed)    identity envelope)   manifest)               is the future owner; Vivarium carries it
    engine build/source    engine_descriptor() -> engine_instance_id,  conformance stamp on every row (engine_        MINTS        engine block         N/A           SFE        verbatim
    hash                   engine_source_hash, base_url, cacert         instance_id, source hash, contract hash)
    foundry/runtime        FOUNDRY / FOUNDRY_C2 dict + foundry_id       ABSENT (UNKNOWN)                               N/A          UNKNOWN unless       MINTS         Proteus    Vivarium adds a carried slot (C); value
    profile                (reachability.py; L2-017)                                                                               supplied             (profiles)              is Proteus's string, verbatim, or UNKNOWN
    schema version         LEDGER_SCHEMA.md; prereg FIELDS per          spec_version (2 legacy | 3); migration files   schema 8     pew.fossil.v2,       registry      each seat  no translation needed; each version is
                           campaign; reachability row shape             001..005; result_schema per kind; kinds have  (/v2/version) schema_version 4     version                 named beside its object; the contract
                                                                       no version (registered name = version)                                                                   itself is versioned (this file)
    seed / RNG identity    campaign_seed (20260918 cmp2, 20260920 cmp3) world.seed_root + repeat.seed_derivation      seed_root on  seed on the          N/A           BOTH       Archaeon's (campaign_seed, rng_label,
                           + per-cell seed + rng_label (L-008; CRN)     (CLOSED set) -> per-repeat seed; no cross-row  the world     encounter                                    seed) has no Vivarium equivalent for
                                                                       CRN concept                                                                                               CRN across rows; carry all three verbatim
                                                                                                                                                                                 in source_evidence; do not reinterpret
    logical generation/    trace rows per generation; first_solved_gen  repeat index only; the kind's payload may      ABSENT       N/A                  N/A           Archaeon   Amendment s5.A adds logical_time to SFE
    time                   etc. (harness)                               carry steps/generations as a parameter        (proposed)                                      -> SFE     observations; until then UNKNOWN
    wall-clock time        receipt started_at/finished_at, timings{}    row created/claimed/started/finished_at        event ts     recorded_at          N/A           each seat  no translation; each seat's clock
                                                                       (DB clock); resources{} per stage                                                                        is named (DB clock vs host clock)

## 2. The join, as a producer would use it

An Archaeon harness that submits through Vivarium (the s10 qualification run)
would carry, on every enqueue, in `source_evidence` (a jsonb the queue already
has and never hashes):

    {"campaign_id": "cmp4", "experiment_id": "C4-SFE-03", "design_id": "<prereg_digest>",
     "attempt_id": "C4-SFE-03/a02", "step_id": "idem:<32hex>", "cell": {...},
     "campaign_seed": 2026..., "rng_label": "...", "foundry_profile": "<Proteus id or UNKNOWN>"}

and Vivarium would return, on the row and in the PEW encounter, the engine
identities it witnessed (world_id, exp_id, obs_ids, work_id, artifact digests,
engine_instance_id, engine_source_hash, contract hash) plus its own
(experiment_id = attempt of one world, spec_hash, repeat index, conformance
stamp). Neither side rewrites the other's ids. The Archaeon receipt keeps
`records[key] = {exp_id, obs_id}` exactly as today; Vivarium's row is one more
CARRIER of the same engine ids, which is what makes the two records joinable
without a translation table: join on (world_id, exp_id) first, on artifact
digest second, on step_id third.

## 3. Ambiguities and aliases found (to resolve in Stage 3)

    A1  "experiment_id" means two different objects. Proposal: Archaeon's stays
        `experiment_id` in ITS records; in the shared envelope it is written
        `harness_id`; Vivarium's row id is written `execution_id` in the shared
        envelope. Both keep their column names locally. (Owner of the ruling:
        Archaeon, per Amendment s9.)
    A2  "attempt" is numbered per harness at Archaeon and per world at Vivarium.
        No merge; the envelope carries both (`attempt_id` Archaeon's,
        `execution_id` Vivarium's).
    A3  design identity: prereg_digest (a document hash) vs spec_hash (an
        executable hash). A prereg can name many specs; a spec can appear in
        many preregs (controls reused). Many-to-many; carried both ways, never
        equated.
    A4  world NAME is a policy channel on the Archaeon side ("<harness>-<name>")
        and a derived identity on the Vivarium side ("viv-<spec_hash>"). Both
        legal; the id, not the name, is the join.
    A5  digest form: Archaeon canonicalises with wse/digest.py; Vivarium with
        viv/artifacts.py. Both produce bare lowercase hex; SFE returns
        "sha256:<hex>". Contract: the envelope always writes "sha256:<hex>".
    A6  event_id has three owners and no join; the outbox (D) mints the only
        cross-seat one.
    A7  foundry/runtime profile, lineage, organism: owned by Proteus, whose
        review is pending (Amendment s8). Slots are reserved as UNKNOWN until
        Proteus names the string form.

## 4. What this contract does NOT do

It does not move any interpretation downward (Amendment s2): no level, no
threshold, no corridor, no maturity verdict is an identity. It does not make
PEW synchronous. It does not require Campaign 4 to run through Vivarium
(s10). It changes no hash: everything it adds to a Vivarium row lives in
`source_evidence` or in new additive columns, never inside the sealed spec.

## 5. Acceptance (when implemented)

    - a Vivarium row enqueued with the envelope above and executed against a
      test engine yields a PEW encounter and a queue row from which every
      identity in section 1 with OWNER != ABSENT can be read back verbatim
      or as the literal UNKNOWN, and none is rewritten
    - the same spec enqueued under two different envelopes has ONE spec_hash
      and two execution_ids (content vs route, the D7/REQ-005 separation)
    - a step_id present in the envelope is the Idempotency-Key the engine
      echoes for that row's POSTs (joinable with no table)
