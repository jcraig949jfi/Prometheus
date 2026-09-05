-- 010: SFE session affinity + engine lineage + fork witness
--      (Mnemosyne, 2026-09-05, session-affinity provenance sprint)
--
-- WHY. M1 and M2 are byte-parity engines: engine_source_hash is IDENTICAL on
-- both, so the BUILD cannot say which engine produced an anchor. Daedalus's
-- engine_instance_id (minted once, stored in the SQLite meta table) is the
-- ledger's identity and travels with the substrate -- correct for restore, and
-- NOT sufficient for execution lineage. Measured 2026-09-05: two copies of one
-- engine.db report the SAME engine_instance_id and each minted DIFFERENT events
-- at the SAME event_seq (32162/32163/32164, divergent entry_hash). Identity
-- alone therefore cannot distinguish two live divergent ledgers.
--
-- WHAT PEW RECORDS. Non-secret handles only. The SFE session key is bearer
-- material; PEW stores its FINGERPRINT (sfp_<sha256[:16]>, Daedalus's
-- key_fingerprint) and never the key. The engine instance id and session id are
-- already published by verify_anchor and the audit envelope, so neither is a
-- new secret. PEW gains a provenance handle, not a credential store.
--
-- LEGACY IS LEGACY. Every column is nullable and additive. Existing fossils
-- keep NULL session/engine fields and are reported as affinity LEGACY. Nothing
-- back-fills a binding that did not exist when the row was written: a
-- synthesized session id would be a fabricated provenance claim, which is the
-- exact failure this migration exists to prevent.

ALTER TABLE ew.fossil_encounters
    ADD COLUMN IF NOT EXISTS sfe_engine_instance_id text,
    ADD COLUMN IF NOT EXISTS sfe_session_id         text,
    ADD COLUMN IF NOT EXISTS sfe_session_key_fp     text,
    ADD COLUMN IF NOT EXISTS sfe_affinity_mode      text,
    ADD COLUMN IF NOT EXISTS sfe_ledger_head_hash   text;

COMMENT ON COLUMN ew.fossil_encounters.sfe_engine_instance_id IS
 'SFE engine_instance_id (eng_<hex>) claimed by the producer AND confirmed by the verifying engine when anchor verification runs. NOT unique across a cloned database -- see ew.ledger_observations.';
COMMENT ON COLUMN ew.fossil_encounters.sfe_session_key_fp IS
 'Non-secret fingerprint of the SFE session key (sfp_<sha256[:16]>). The raw key is bearer material and is NEVER stored.';
COMMENT ON COLUMN ew.fossil_encounters.sfe_affinity_mode IS
 'STRICT = minted under a session-affine engine and bound. LEGACY = pre-session evidence, or an engine that does not issue session keys. NULL = unknown/not asserted. LEGACY is never upgraded in place.';

CREATE INDEX IF NOT EXISTS idx_fossil_enc_engine  ON ew.fossil_encounters(sfe_engine_instance_id);
CREATE INDEX IF NOT EXISTS idx_fossil_enc_session ON ew.fossil_encounters(sfe_session_id);

-- ---------------------------------------------------------------- fork witness
-- PEW is the one component that sees anchors from many engines, so it can act
-- as a witness to ledger divergence WITHOUT any engine change.
--
-- The SFE event ledger is hash-chained and event_seq is a per-database ledger
-- position. Therefore, for a single logical engine identity, one (engine, seq)
-- must have exactly ONE entry_hash. Two different entry_hashes at the same
-- (engine_instance_id, event_seq) is PROOF that two divergent ledgers are
-- claiming one identity -- i.e. a clone/split-brain -- and the primary key below
-- turns that proof into a refused write instead of a silent contradiction.
--
-- Scope, stated honestly: this witnesses forks among the anchors THIS PEW store
-- observes. M1 and M2 run separate PEW stores by ruling, so neither sees the
-- other's anchors; a fleet-wide witness needs a federated or central PEW, which
-- is not built here. Detection is also after-the-fact: it cannot stop an engine
-- from forking, only stop PEW from recording the contradiction as if coherent.
CREATE TABLE IF NOT EXISTS ew.ledger_observations (
    engine_instance_id text   NOT NULL,
    event_seq          bigint NOT NULL,
    entry_hash         text   NOT NULL,
    first_encounter_id text,
    first_run_id       text,
    first_seen         timestamptz NOT NULL DEFAULT now(),
    observed_by        text,
    PRIMARY KEY (engine_instance_id, event_seq)
);
COMMENT ON TABLE ew.ledger_observations IS
 'Fork witness: one (engine_instance_id, event_seq) -> one entry_hash. A conflicting insert means two divergent ledgers claim one engine identity (split brain) and the fossil write is refused with 409 split_brain_ledger_fork.';

-- Divergence events are themselves evidence and are kept even when the write
-- they arrived on was refused; a refused write that leaves no trace would erase
-- the only record that a fork was ever seen.
CREATE TABLE IF NOT EXISTS ew.ledger_fork_events (
    fork_id            bigserial PRIMARY KEY,
    engine_instance_id text NOT NULL,
    event_seq          bigint NOT NULL,
    stored_entry_hash  text NOT NULL,
    offered_entry_hash text NOT NULL,
    offered_encounter  text,
    offered_run_id     text,
    detected_at        timestamptz NOT NULL DEFAULT now(),
    detected_by        text
);

INSERT INTO ew.ontology_versions(version, description) VALUES
 (5, 'V5: SFE session affinity -- engine/session lineage on fossils, non-secret key fingerprint, LEGACY vs STRICT, ledger fork witness')
ON CONFLICT DO NOTHING;

-- ------------------------------------------------- cross-session splice witness
-- Measured gap, 2026-09-05: an anchor from the CORRECT experiment/observation
-- but a DIFFERENT session still verifies, because SFE's verify-anchor does not
-- yet assert binds_session (checks.binds_session is absent). Until it does,
-- PEW can still catch the splice itself, because an SFE world belongs to
-- exactly one session: for one engine, (engine_instance_id, world_id) must map
-- to exactly ONE session_id. A second, different session claiming the same
-- world on the same engine is evidence spliced across sessions.
--
-- This is a witness, not a proof of correctness: it fires only once PEW has
-- seen the world's true session first, and it cannot police a world PEW has
-- never observed. Engine-side binds_session remains the real fix and is filed
-- as a cross-component request to Daedalus.
CREATE TABLE IF NOT EXISTS ew.world_session_bindings (
    engine_instance_id text NOT NULL,
    world_id           text NOT NULL,
    session_id         text NOT NULL,
    first_encounter_id text,
    first_seen         timestamptz NOT NULL DEFAULT now(),
    observed_by        text,
    PRIMARY KEY (engine_instance_id, world_id)
);
COMMENT ON TABLE ew.world_session_bindings IS
 'Splice witness: for one engine, a world belongs to one session. A fossil claiming a different session for an already-witnessed (engine, world) is refused with 409 cross_session_splice.';

CREATE TABLE IF NOT EXISTS ew.session_splice_events (
    splice_id          bigserial PRIMARY KEY,
    engine_instance_id text NOT NULL,
    world_id           text NOT NULL,
    stored_session_id  text NOT NULL,
    offered_session_id text NOT NULL,
    offered_encounter  text,
    detected_at        timestamptz NOT NULL DEFAULT now(),
    detected_by        text
);
