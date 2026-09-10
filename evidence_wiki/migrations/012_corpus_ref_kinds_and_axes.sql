-- 012: corpus reference kinds + evidence axes on typed_refs
--      (Mnemosyne, 2026-09-10, index today's corpora)
--
-- Order: roles/Archaeon/prompts/2026-09-10_delegation/MNEMOSYNE_PROTEUS.md --
-- index cs-c3-2 and cs-h1h0-1-p1 as typed refs (experiment, observation, PEW
-- encounter, artifact where present) WITH THE FOUR EVIDENCE AXES, from
-- authoritative references only.
--
-- Two additive changes, both forced by that order:
--
-- 1. The ref-kind vocabulary in migration 011 covered the H0-H5 object types
--    (WITNESS, COMPONENT, GENERATED_TASK, DECODER, SOURCE_SET, RECEIPT). The
--    corpora need EXPERIMENT, OBSERVATION, ENCOUNTER and ARTIFACT as well.
--    011 states the vocabulary is closed and extended only by migration; this
--    is that migration. Mapping one of the new types onto an existing kind
--    (an observation filed as a RECEIPT, say) would have been a distortion
--    that no later reader could undo.
--
-- 2. The axes live on ew.evidence today. The order asks for them ON the typed
--    refs, so they are added here with the same four vocabularies. A reference
--    is not itself evidence; carrying the axes lets a corpus row state what
--    stage produced it and what was (and was NOT) concluded, without minting
--    an evidence record that asserts a scientific claim nobody adjudicated.
--
-- Nothing is back-filled. Rows written before this migration keep NULL axes.

ALTER TABLE ew.typed_refs
    ADD COLUMN IF NOT EXISTS software_stage      text,
    ADD COLUMN IF NOT EXISTS connection_evidence text,
    ADD COLUMN IF NOT EXISTS scientific_outcome  text,
    ADD COLUMN IF NOT EXISTS reproduction_state  text,
    -- which corpus this reference belongs to, so a set can be counted,
    -- re-indexed and rebuilt as a unit
    ADD COLUMN IF NOT EXISTS candidate_set_id    text,
    ADD COLUMN IF NOT EXISTS producer_experiment_id text;

COMMENT ON COLUMN ew.typed_refs.scientific_outcome IS
 'not-run|inconclusive|supported-in-scope|meaningful-effect-not-supported|harmful-in-scope. PEW records the ABSENCE of an adjudicated outcome as inconclusive; it never adjudicates one. Promotion belongs to Harmonia/Archaeon.';
COMMENT ON COLUMN ew.typed_refs.candidate_set_id IS
 'The corpus this reference was indexed under (e.g. cs-c3-2). Indexing is per-set so counts, re-indexing and rebuilds are per-set.';

CREATE INDEX IF NOT EXISTS idx_typed_refs_cs ON ew.typed_refs(candidate_set_id, ref_kind);

INSERT INTO ew.ontology_versions(version, description) VALUES
 (7, 'V7: ref kinds EXPERIMENT/OBSERVATION/ENCOUNTER/ARTIFACT; source kinds EXPERIMENT/ENCOUNTER/EVENT; evidence axes and candidate_set_id on typed_refs')
ON CONFLICT DO NOTHING;
