-- 009: immutable audit/replay envelope (Mnemosyne, R2-1 PEW side, 2026-09-04)
--
-- A content-addressed SEAL over the producer-supplied immutable identities of
-- ONE recorded encounter, so an independent investigator can recover the whole
-- sealed experiment record FROM PEW ALONE -- without the producing SFE client's
-- credential. PEW invents NO scientific semantics: it stores the producer-
-- supplied identities / content-addressed material verbatim and content-
-- addresses the whole envelope (that hash IS the seal). A re-seal of identical
-- content is idempotent (same envelope_id); any changed slot yields a different
-- envelope_id (tamper-evident). Additive; the pew.fossil.v2 write contract is
-- unchanged.
--
-- Documented envelope slots (ALL producer-supplied, nullable -- PEW does not
-- invent them; missing slots are the producer's / cross-component gap, not a
-- PEW defect):
--   experiment_spec_id            (experiment / spec identity)
--   organism_ids, interpretation_id
--   registry_id, entry_id         (registry / entry identity)
--   composition_id, topology      (composition / topology)
--   ablation                      (ablation relation)
--   action_id, input_digest       (exact action / input identity)
--   world_id, world_config_digest (world / config identity)
--   measurement_def, measurement_version
--   output_digest                 (output identity)
--   sfe_engine_id                 (SFE engine identity)
--   causal_anchor {sfe_event_id, sfe_entry_hash, sfe_event_seq}

CREATE TABLE IF NOT EXISTS ew.sealed_records (
    envelope_id       text PRIMARY KEY,          -- SEAL-<sha256(content_canonical)[:24]> ; the seal
    content_sha256    text NOT NULL,             -- sha256 of content_canonical (== the seal source)
    content_canonical text NOT NULL,             -- exact canonical string that was hashed (tamper-verify source)
    encounter_id      text NOT NULL,
    encounter_run_id  text,
    encounter_run_key text GENERATED ALWAYS AS (coalesce(encounter_run_id, '')) STORED,
    envelope          jsonb NOT NULL,            -- producer-supplied slots, stored verbatim (opaque to PEW)
    attestation       jsonb,                     -- server identity at seal time
    namespace         text NOT NULL DEFAULT 'prod',
    created_by        text NOT NULL,
    machine           text NOT NULL,
    created_at        timestamptz NOT NULL DEFAULT now(),
    revision          bigint NOT NULL,
    CONSTRAINT sealed_fossil_fk FOREIGN KEY (encounter_id, encounter_run_key)
        REFERENCES ew.fossil_encounters(encounter_id, run_key)
);
CREATE INDEX IF NOT EXISTS idx_sealed_encounter ON ew.sealed_records(encounter_id, encounter_run_key);

COMMENT ON TABLE ew.sealed_records IS
 'R2-1 PEW side: content-addressed immutable audit/replay envelope binding a fossil encounter to producer-supplied immutable identities. envelope_id = SEAL-<sha256 of the canonical {encounter_id,run_id,envelope}>; a re-seal of identical content is idempotent, any changed slot is a new seal (tamper-evident). Recoverable from PEW without the SFE client credential. PEW invents no semantics; slots are producer-supplied and nullable.';
