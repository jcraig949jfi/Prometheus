-- Dimension membership for evidence rows: the canonical record of WHICH
-- source-vocabulary terms an evidence row carries per dimension. Coordinates
-- (ew.coordinates) are DERIVED deterministically from this table joined to
-- ew.term_mappings; this table is canonical, the coordinates are rebuildable.
-- An evidence row may legitimately belong to several terms of one dimension
-- (e.g. two mechanisms); the v0 uniqueness must therefore be per-coordinate,
-- not per-evidence. Regeneration stays idempotent via DELETE + reinsert.
ALTER TABLE ew.coordinates DROP CONSTRAINT IF EXISTS coordinates_view_name_view_version_evidence_id_key;
CREATE UNIQUE INDEX IF NOT EXISTS uq_ew_coords_cell
    ON ew.coordinates (view_name, view_version, evidence_id, coords);

CREATE TABLE IF NOT EXISTS ew.evidence_terms (
    evidence_id  text NOT NULL REFERENCES ew.evidence(evidence_id),
    dimension    text NOT NULL,       -- mechanism|substrate_class|consumer|intervention|failure_class
    source_term  text NOT NULL,       -- exact source vocabulary, never discarded
    assigned_by  text NOT NULL,
    creation_method text NOT NULL,    -- HUMAN|MODEL_EXTRACTED
    created_at   timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (evidence_id, dimension, source_term)
);
