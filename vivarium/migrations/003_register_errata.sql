-- 003: ERRATA. Contamination is recorded, never erased.
--      (Vivarium, 2026-09-06, operator decision)
--
-- On 2026-09-06 Archaeon's test suite wrote 245 rows into the PRODUCTION
-- register, and a live Vivarium cycle claimed one of them and attempted to
-- execute it. The cause is fixed (archaeon.vivqueue now honours VIV_SCHEMA and
-- its conftest creates a throwaway schema). The ROWS remain, and the operator's
-- decision is that they stay: deleting from a pre-execution register is exactly
-- the erasure Harmonia S15 classes as an unobservable selection mechanism, and
-- a register that can be tidied is not a register.
--
-- So the exclusion lives OUTSIDE the rows, which is also the only place it CAN
-- live: the BEFORE UPDATE trigger freezes terminal rows whole, so there is no
-- flag to set on a cancelled row and no way to smuggle one in. That constraint
-- produced the right design rather than obstructing it.
--
--   viv.register_errata        one row per DECLARED incident, append-only
--   viv.register_errata_rows   the ENUMERATED member rows, append-only
--   viv.register_clean         the register minus every excluded row
--
-- Membership is ENUMERATED, not predicated. A predicate ("everything Archaeon
-- wrote after 03:00") is re-evaluated against a moving table and would silently
-- capture future honest rows; a frozen list of experiment_ids says exactly what
-- was excluded and can be audited row by row for ever. It is also the only
-- honest option here, because the contaminated rows are indistinguishable from
-- real candidate registrations in every column -- which is itself the finding.
--
-- WHAT IS NOT DONE. `candidate_sets` and `execution_attempts` are NOT filtered.
-- A contaminated candidate set must announce itself rather than quietly shrink,
-- so `candidate_sets` gains an `excluded` count instead. Analysis reads
-- `viv.register_clean`; operations keep reading the table.

CREATE TABLE IF NOT EXISTS {schema}.register_errata (
    erratum_id  bigserial PRIMARY KEY,
    declared_at timestamptz NOT NULL DEFAULT now(),
    declared_by text NOT NULL,
    kind        text NOT NULL,
    reason      text NOT NULL,
    detail      jsonb NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT errata_kind_ck CHECK (kind IN ('CONTAMINATION', 'MISFILED',
                                              'SUPERSEDED_CONTRACT'))
);

COMMENT ON TABLE {schema}.register_errata IS
 'Declared defects in the register. An erratum EXCLUDES rows from analysis; it never deletes them and never modifies them. Append-only.';

CREATE TABLE IF NOT EXISTS {schema}.register_errata_rows (
    erratum_id    bigint NOT NULL
                  REFERENCES {schema}.register_errata(erratum_id),
    experiment_id uuid   NOT NULL
                  REFERENCES {schema}.research_experiment_queue(experiment_id),
    PRIMARY KEY (erratum_id, experiment_id)
);

CREATE INDEX IF NOT EXISTS ix_errata_rows_experiment
    ON {schema}.register_errata_rows (experiment_id);

CREATE OR REPLACE FUNCTION {schema}.refuse_errata_mutation()
RETURNS trigger AS $fn$
BEGIN
    RAISE EXCEPTION
        '%: errata are append-only. An erratum that can be edited is not a '
        'record of what was excluded, it is a record of what someone last '
        'thought.', TG_OP USING ERRCODE = 'raise_exception';
END;
$fn$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_errata_append_only ON {schema}.register_errata;
CREATE TRIGGER trg_errata_append_only
    BEFORE UPDATE OR DELETE ON {schema}.register_errata
    FOR EACH ROW EXECUTE FUNCTION {schema}.refuse_errata_mutation();

DROP TRIGGER IF EXISTS trg_errata_rows_append_only
    ON {schema}.register_errata_rows;
CREATE TRIGGER trg_errata_rows_append_only
    BEFORE UPDATE OR DELETE ON {schema}.register_errata_rows
    FOR EACH ROW EXECUTE FUNCTION {schema}.refuse_errata_mutation();


-- ------------------------------------------------------------- the exclusion
DROP VIEW IF EXISTS {schema}.register_clean;
CREATE VIEW {schema}.register_clean AS
SELECT q.*
  FROM {schema}.research_experiment_queue q
 WHERE NOT EXISTS (SELECT 1 FROM {schema}.register_errata_rows x
                    WHERE x.experiment_id = q.experiment_id);

COMMENT ON VIEW {schema}.register_clean IS
 'The register minus every row named by an erratum. THIS is what analysis reads. The table itself keeps everything, so an excluded row is always recoverable and always auditable -- exclusion is a statement about a row, not a deletion of it.';

DROP VIEW IF EXISTS {schema}.register_excluded;
CREATE VIEW {schema}.register_excluded AS
SELECT q.experiment_id, q.created_at, q.created_by, q.source_reason, q.status,
       q.candidate_set_id, e.erratum_id, e.kind, e.reason, e.declared_at,
       e.declared_by
  FROM {schema}.research_experiment_queue q
  JOIN {schema}.register_errata_rows x ON x.experiment_id = q.experiment_id
  JOIN {schema}.register_errata e      ON e.erratum_id    = x.erratum_id;


-- A contaminated candidate set must ANNOUNCE itself, not quietly shrink.
DROP VIEW IF EXISTS {schema}.candidate_sets;
CREATE VIEW {schema}.candidate_sets AS
    SELECT q.candidate_set_id,
           count(*)                                          AS registered,
           count(*) FILTER (WHERE q.status = 'cancelled')     AS cancelled,
           count(*) FILTER (WHERE q.status <> 'cancelled')    AS retained,
           count(*) FILTER (WHERE q.started_at IS NOT NULL)   AS executed,
           count(*) FILTER (WHERE EXISTS (
               SELECT 1 FROM {schema}.register_errata_rows x
                WHERE x.experiment_id = q.experiment_id))     AS excluded,
           min(q.created_at)                                  AS registered_at,
           max(q.created_at)                                  AS last_registered_at,
           count(DISTINCT q.created_by)                       AS registrars
      FROM {schema}.research_experiment_queue q
     WHERE q.candidate_set_id IS NOT NULL
     GROUP BY q.candidate_set_id;

COMMENT ON VIEW {schema}.candidate_sets IS
 'Candidate-set sizes DERIVED from the register, never attested. `excluded` counts members named by an erratum: a set with excluded > 0 is contaminated and its registered/retained counts must not be read as a selection decision.';
