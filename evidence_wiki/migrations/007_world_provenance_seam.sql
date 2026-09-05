-- 007: world-provenance seam closure (Harmonia handoff, 2026-09-03)
--
-- ONE canonical binding from ordinary PEW evidence to a fossil encounter.
--
-- Why typed columns and not a relation: an encounter's identity is the PAIR
-- (encounter_id, run_id) since migration 006. A relation row carries a single
-- text dst_id, so binding through relations would require an invented
-- composite-string convention -- exactly what the directive forbids -- and a
-- new relation_type would broaden the ontology. Typed columns are queryable,
-- joinable, and the foreign key makes a binding to a non-existent encounter
-- impossible at the DATABASE level rather than by convention.
--
-- MATCH SIMPLE semantics are deliberate: when encounter_id IS NULL the foreign
-- key is not enforced, so every pre-existing evidence row (which has no
-- binding) remains valid and untouched. When encounter_id is set, run_key is
-- non-null by construction and the key is fully enforced.

ALTER TABLE ew.evidence
    ADD COLUMN IF NOT EXISTS encounter_id     text,
    ADD COLUMN IF NOT EXISTS encounter_run_id text;

ALTER TABLE ew.evidence
    ADD COLUMN IF NOT EXISTS encounter_run_key text
    GENERATED ALWAYS AS (coalesce(encounter_run_id, '')) STORED;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint
                   WHERE conname = 'evidence_fossil_encounter_fk') THEN
        ALTER TABLE ew.evidence
            ADD CONSTRAINT evidence_fossil_encounter_fk
            FOREIGN KEY (encounter_id, encounter_run_key)
            REFERENCES ew.fossil_encounters(encounter_id, run_key);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_evidence_encounter
    ON ew.evidence(encounter_id, encounter_run_key);

-- Expose the binding through the production view. Column list and namespace
-- predicate are preserved verbatim from the pre-007 definition; only the two
-- binding columns are added.
-- Re-runnable (fixed 2026-09-05, M1 bring-up): migration 004 defines this view
-- as `SELECT e.*`, so on a re-apply it expands to EVERY column of ew.evidence
-- (including the generated encounter_run_key). An explicit narrower column list
-- here then tried to DROP that column and failed with
-- "cannot drop columns from view", making the migration set un-re-runnable.
-- Using e.* makes 004 and 007 converge by construction, whatever columns exist.
CREATE OR REPLACE VIEW ew.evidence_prod AS
 SELECT e.*
   FROM ew.evidence e
  WHERE NOT (EXISTS ( SELECT 1
           FROM ew.object_namespace ns
          WHERE ns.object_type = 'evidence'::text AND ns.object_id = e.evidence_id
            AND (ns.namespace = ANY (ARRAY['fixture'::text, 'test'::text]))))
    AND (claim_id IS NULL OR (EXISTS ( SELECT 1
           FROM ew.claims_prod cp
          WHERE cp.claim_id = e.claim_id)));
