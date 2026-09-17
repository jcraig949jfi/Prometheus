-- 013: typed columns for MINTED players (Mnemosyne, 2026-09-16, Proteus #287
--      under Archaeon ruling #268 "Proteus MINTS derived CA mechanisms")
--
-- A minted rule-table player carries provenance that fossil_players had no
-- typed column for: a SECOND parent (a crossover child has two), the organism
-- FAMILY (today's rows are VM programs; minted rows are CA rule tables), and
-- the two version strings that say which representation and which semantics
-- the player_id was minted under. Putting these inside the freeform
-- `producer` jsonb would have been the exact distortion THEO-REQ-001 (#239)
-- is about: a coordinate nobody can select on. Schema is contract.
--
-- Additive, nullable, no back-fill: every row written before this migration
-- keeps NULLs, which reads as "single parent, family unstated", i.e. what
-- those rows always were. Identical-idempotent re-registration is unchanged:
-- a NULL on the stored row is skipped by the comparison in _upsert_anchor,
-- so a pre-013 row re-registered with the new fields is a 409 only if a
-- NON-NULL stored value differs.

ALTER TABLE ew.fossil_players
    ADD COLUMN IF NOT EXISTS mate_player            text,
    ADD COLUMN IF NOT EXISTS family                 text,
    ADD COLUMN IF NOT EXISTS representation_version text,
    ADD COLUMN IF NOT EXISTS semantic_version       text;

COMMENT ON COLUMN ew.fossil_players.mate_player IS
    'second parent of a crossover child (Proteus mint record mate_player); NULL = single parent or unstated';
COMMENT ON COLUMN ew.fossil_players.family IS
    'organism family, e.g. rule_table (Proteus mint) or the VM-program families of earlier rows; NULL = unstated';
COMMENT ON COLUMN ew.fossil_players.representation_version IS
    'representation the player_id was minted under, e.g. herakles.evca.rule_hex.r3.v1';
COMMENT ON COLUMN ew.fossil_players.semantic_version IS
    'semantics the player_id was minted under, e.g. herakles.evca.core.v1';

-- Lineage reads by either parent (the visited-parent map, both directions).
CREATE INDEX IF NOT EXISTS fossil_players_parent_idx ON ew.fossil_players(parent_player);
CREATE INDEX IF NOT EXISTS fossil_players_mate_idx   ON ew.fossil_players(mate_player);
CREATE INDEX IF NOT EXISTS fossil_players_family_idx ON ew.fossil_players(family);
