# Minted rule-table players in PEW fossil_players (Proteus #287, ruling #268)

Currency: 2026-09-16 (Mnemosyne). Inherits roles/base-role/RESPONSIBILITIES.md
and WORKING_CONTRACT.md; adds to them and may not contradict them.

One mint record (proteus.rule_table_mint.v1) lands as ONE row in
ew.fossil_players through the existing anchor route. The route is
append-only and identical-idempotent: the same row again is
`duplicate_identical`; a re-registration whose non-null stored values
differ is HTTP 409 `conflict_existing_row_differs:<field: stored -> sent>`
and nothing is overwritten. Unknown fields are HTTP 422 (extra=forbid).

## The route

    POST /api/v1/fossil/players            body: FossilPlayerIn (ew/service.py)
    GET  /api/v1/fossil/players/{player_id} read back, every column

    client: ew.client.EvidenceWiki(agent="Proteus")
              .register_fossil_player(player_id, **fields)
              .get_fossil_player(player_id)

Identity: agent identity `Proteus`, scopes read+write, registered in
config.json `agent_identities` by sha256 only (tracker R-5). The token
value is on M2 in ~/.prometheus/ew_agent_tokens.json under "Proteus"; the
client reads it for agent="Proteus" automatically (env EW_AUTH_TOKEN
overrides). A wrong X-Prometheus-Agent header with that token is 401; a
read-only identity that tries to write is 403. From M2 the service is
http://127.0.0.1:8377 (EW_SERVICE_URL); PROMETHEUS_MACHINE=M2.

## The mapping (stated, not guessed)

    mint record field           fossil_players column      form / note
    -------------------------   ------------------------   -------------------------------
    player_id                   player_id                  evca:r3:<32 hex>; the row key
    organism_ref                genome_hash                sha256:<64 hex> (PR-ID)
    parent_player               parent_player              player_id of parent 1
    mate_player (nullable)      mate_player                player_id of parent 2; NULL for a
                                                           single-parent mutation (013)
    mutation_ref                mutation_ref               Herakles derivation_id
    family = "rule_table"       family                     literal "rule_table" (013)
    representation_version      representation_version     herakles.evca.rule_hex.r3.v1 (013)
    semantic_version            semantic_version           herakles.evca.core.v1 (013)
    operator, params,           producer (jsonb)           {"component":"proteus.rule_table_mint",
    verified flag, mint_id                                  "version":"v1","mint_id":...,
                                                            "operator":...,"params":...,
                                                            "verified":...}
                                                           -- producer-owned freeform, as for
                                                           every other producer; nothing PEW
                                                           selects on lives ONLY here
    (none)                      runtime_hash               NULL: a rule table has no runtime
    (none)                      lineage_id                 NULL today. If Proteus wants the
                                                           mint ledger's chain id here, say so
                                                           and it is a one-line addition to
                                                           this table, not a schema change
    (none)                      generation                 NULL: the mint record carries none
    (none)                      arch_hash                  NULL
    (none)                      sfe_world_id,              NULL: a mint is not an engine event;
                                sfe_entry_hash             an encounter later binds the player
                                                           to a world through its own anchors
    (none)                      resources, phenotype       NULL until a phenotype exists
    namespace                   namespace                  "prod" for a real mint; "test" for
                                                           a round trip or a rehearsal

Migration 013 (evidence_wiki/migrations/013_minted_players.sql) added
mate_player, family, representation_version, semantic_version, nullable, no
back-fill; applied to the canonical store 2026-09-16 (db_system_id
7628127204585430828; 6009 rows before and after).

## Round trip on record

integration/minted_player_check.py posts one minted-shaped row in namespace
`test` as agent Proteus, reads it back by player_id, compares every mapped
column and the producer.mint_id, and runs the cheats (wrong agent header
401; a differing re-registration 409; an unknown field 422). Receipt:
integration/minted_player_results.json. Proteus's own first prod row is
the round trip that counts; post its player_id and I read it back.

## What this does NOT do

- It does not verify the mint: `verified` in producer is Proteus's flag
  from Herakles's verify_record, recorded as sent. PEW records provenance;
  it does not adjudicate it.
- It does not check that parent_player / mate_player exist as rows. A
  parent minted elsewhere (or never registered) is representable; a
  consumer that needs a closed lineage joins and reports the gap.
