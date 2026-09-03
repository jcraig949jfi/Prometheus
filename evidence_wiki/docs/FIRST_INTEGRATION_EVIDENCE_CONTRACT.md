# First-Integration Evidence Contract (`pew.fossil.v1`)

Normative description of what PEW accepts, what it preserves, and how the
evidence joins back to the exact world and player that produced it. The
machine-readable form is `GET /api/v1/fossil/contract`.

Frozen 2026-09-03. Schema version 3 (migration 006).

---

## 1. The join

    WORLD  ---- world_id ---->  ENCOUNTER (spec)  <---- players[] ---- PLAYER
      |                              |                                   |
    fossil_worlds              + run_id (execution)                 fossil_players
    manifest_hash                    |                              genome_hash
    world_binding_id           fossil_encounters                    runtime_hash
    seed_root                  sfe_entry_hash (SFE anchor)          lineage_id
    sfe_head_hash                    |                              generation
                                  EVIDENCE

A row is keyed `(encounter_id, run_id)`. Every row carries `sfe_entry_hash`,
the hash of the SFE ledger entry that supports it: PEW references immutable
SFE history, it never restates it.

## 2. Fields, and whether PEW truthfully preserves them

    world_id ................... YES  fossil_encounters.world_id, indexed,
                                      queryable; anchor row in fossil_worlds
    world version/hash/schema .. YES  fossil_worlds.manifest_hash,
                                      sfe_head_hash, interface_ver,
                                      mechanics_ver, world_binding_id
    player_id .................. YES  players[] on the encounter (GIN-indexed,
                                      queryable); anchor row in fossil_players.
                                      NAME: Proteus calls this organism_id.
    player version/hash ........ YES  fossil_players.genome_hash (Proteus
                                      manifest hash), runtime_hash, arch_hash
    run_id ..................... YES  NEW in migration 006. Producer supplies
                                      SFE "exp_id:work_id".
    episode_id ................. COLUMN EXISTS, NULL IN PRACTICE. No producer
                                      mints an episode identity today. PEW
                                      stores one if sent and never invents one.
    configuration .............. PARTIAL  ecology (jsonb) and budget (jsonb)
                                      are stored verbatim if sent. PEW does not
                                      model configuration semantics.
    seed ....................... YES  encounter-level seed; the world-level
                                      SFE seed_root is on the world row.
    observations/events ........ BY REFERENCE ONLY. sfe_event_id +
                                      sfe_entry_hash + sfe_event_seq point into
                                      the SFE ledger, which is authoritative.
                                      PEW does not copy transcripts.
    actions/decisions .......... NO. Same reason: SFE owns them. Referenced
                                      through the ledger anchor, not duplicated.
    score/reward/metric ........ PARTIAL  outcome (native token, never prose)
                                      and resources_used (jsonb). A measurement
                                      definition+version is NOT yet modelled --
                                      see docs/PHENOTYPE_CONSUMER_REQUIREMENT.md;
                                      this is the known gap, and it is upstream.
    termination state .......... YES  outcome + failure_class
    errors ..................... YES  failure_class on the row; refused writes
                                      in ew.write_log (accepted=false)
    timestamps/order ........... YES  occurred_ts (when it happened, producer's
                                      claim) and sfe_event_seq (SFE's total
                                      order). PEW's own `revision` is PEW write
                                      order and MUST NOT be read as run order.
    producing component versions  YES  producer (jsonb) on encounters, worlds
                                      and players: put runtime_hash,
                                      grammar_hash, affordance_hash, spec_hash,
                                      git_commit here.
    evidence schema version .... YES  FOSSIL_CONTRACT_VERSION on every health
                                      response; schema_version 3.

Nothing above is inferred. A field the producer does not send is NULL, and a
NULL means "not asserted", never "zero" or "unknown-but-probably".

## 3. Identifier mapping across components (no silent renaming)

    PEW field        SFE (authoritative)     Proteus (mints players)
    --------------   ---------------------   -----------------------------
    world_id         world_id                (not minted)
    players[]        (not minted)            organism_id
    encounter_id     (not minted)            encounter_identity(organism_ids,
                                             world_binding_id, seed,
                                             checkpoint_ids)
    run_id           exp_id + work_id        (not minted)
    seed             worlds.seed_root        encounter seed argument
    sfe_entry_hash   events.entry_hash       --
    sfe_event_seq    events.event_seq        --
    outcome          observations.outcome    NEVER (Proteus records no outcome;
                                             a Proteus file asserting one is a
                                             defect per its own contract)
    genome_hash      artifacts.blob_hash     manifest hash (same bytes; equal
                                             by construction -- a free
                                             cross-check at ingest time)

PEW stores each producer's own identifier under its own name. It does not
normalize `organism_id` into `player_id` inside the payload, it maps the
column: `players[]` holds Proteus organism ids verbatim.

## 4. Cross-component mismatches found (charter s8)

Reviewed: `SerendipityFoundry/SerendipityFoundryEngine/docs/
SERENDIPITY_FOUNDRY_GEN2_API.md`, the live SFE ledger schema
(`var/engine.db`, read-only), and on `origin/main`:
`proteus/contracts/PEW_EXPORT.md`, `proteus/contracts/SFE_INTEGRATION.md`,
`proteus/contracts/player_manifest.schema.v0.json`.

1. RESOLVED (in PEW, migration 006) -- `run_id` existed nowhere. Proteus's
   `encounter_id` is a deterministic function of the encounter SPECIFICATION,
   so two executions of one spec collided on PEW's primary key and the second
   was silently dropped behind HTTP 200. PEW now keys `(encounter_id, run_id)`
   and returns 409 on a differing duplicate.
2. RESOLVED (in PEW) -- `players`, `seed`, `budget`, `ecology`,
   `resources_used`, `occurred_ts` were columns in the schema but absent from
   the ingest model, so a producer sending them got 200 and lost the data.
   They are now accepted, persisted, and read back; unknown fields are 422.
3. RESOLVED (in PEW) -- there was no read-back or query path for fossil rows
   at all. A consumer could not verify its own writes through the API.
4. OPEN, UPSTREAM -- `episode_id` is minted by no component. Column present,
   left NULL. Do not invent one to fill the schema.
5. OPEN, UPSTREAM -- measurement definition + version for scores. SFE's
   `measurements` table exists but holds 0 rows, and only 2 of 6,006 candidate
   artifacts carry phenotype scores. Until SFE emits them, `outcome` is a
   token and no metric is joinable. Tracked in
   docs/PHENOTYPE_CONSUMER_REQUIREMENT.md and roles/Daedalus/todo_20260902.md.
6. OPEN, UPSTREAM -- Proteus is on `origin/main`; the PEW client is on
   `mnemosyne/evidence-wiki-v0`. `proteus/contracts/PEW_EXPORT.md` states its
   rows have never been exercised against the running service. The Proteus
   claim/evidence path (`export.pew_rows`) is therefore UNVERIFIED end to end;
   only the fossil path in this document has been exercised.
7. NOTED -- SFE `seed_root` is an integer, PEW `seed` is text. PEW stores the
   producer's string form; no arithmetic is performed on seeds anywhere.

None of these was resolved by normalizing incompatible identifiers together.
Where the producer mints nothing, the PEW column stays NULL.

## 5. What PEW will not do

- It will not accept an encounter without an SFE ledger anchor.
- It will not overwrite a stored row; a differing duplicate is a 409.
- It will not silently accept an unknown field from a producer whose schema
  has drifted.
- It will not promote `test`/`synthetic` namespace rows into scientific
  queries; `ew/fossil.py` filters `namespace='prod'` everywhere.
- It will not adjudicate. SFE remains authoritative for what happened.
