-- 010: a row whose NEWEST attempt FAILED on ENGINE_TRANSPORT may be released
--      to a NEW ATTEMPT (Vivarium, window C4-20260917-W1; s14 canary run 7 row D).
--
-- The canary hit a real 60 s read stall on POST observation: the write landed
-- on the engine, the client timed out, the attempt closed FAILED /
-- ENGINE_TRANSPORT (typed, correct) and the ROW went terminal `failed` --
-- frozen. Nothing scientific failed; the wire did. Under 006 the only rerun
-- was a NEW ROW, whose steps replay nothing across rows (VIV22), so the rerun
-- would have minted a SECOND world for the same design -- exactly the
-- duplicate the point release exists to prevent. Campaign 4 will meet this
-- stall (Daedalus #345/#348; the 9.0.1 repair is not deployed at this window),
-- so such a row must be re-attemptable, and only such a row: a row that
-- failed for any other reason (executor, instrument, engine rejected,
-- prerequisite) is a fact about the design or the executor and stays frozen.
--
-- The rule, narrow: failed -> queued is legal ONLY inside the release path
-- (SET LOCAL viv.release = 'new_attempt'), ONLY when the newest attempt is
-- terminal with termination_reason ENGINE_TRANSPORT, ONLY when no attempt is
-- open. Every freeze below (spec, provenance, relations, locators) still
-- applies. The body is 006's function (derived from 006 by script,
-- kept in step with the newest migration that redefines it) plus the two marked clauses.
CREATE OR REPLACE FUNCTION {schema}.enforce_queue_transition()
RETURNS trigger AS $fn$
DECLARE
    legal boolean;
    transport_release boolean := false;
    last_reason text;
BEGIN
    -- 010: the ONE way out of a terminal `failed`: the newest attempt failed
    -- on ENGINE_TRANSPORT, no attempt is open, and the release path declared
    -- itself (SET LOCAL viv.release = 'new_attempt').
    IF OLD.status = 'failed' AND NEW.status = 'queued'
       AND current_setting('viv.release', true) = 'new_attempt' THEN
        SELECT termination->>'termination_reason' INTO last_reason
          FROM {schema}.execution_attempt
         WHERE experiment_id = OLD.experiment_id
         ORDER BY attempt_number DESC LIMIT 1;
        IF last_reason = 'ENGINE_TRANSPORT'
           AND (SELECT count(*) FROM {schema}.execution_attempt
                 WHERE experiment_id = OLD.experiment_id AND terminal_state IS NULL) = 0 THEN
            transport_release := true;
        END IF;
    END IF;

    IF OLD.status IN ('completed', 'failed', 'cancelled') AND NOT transport_release THEN
        RAISE EXCEPTION
            'vivarium: experiment % is terminal (%) and is frozen; refusing UPDATE',
            OLD.experiment_id, OLD.status
            USING ERRCODE = 'raise_exception';
    END IF;

    IF NEW.experiment_spec IS DISTINCT FROM OLD.experiment_spec
       OR NEW.spec_hash IS DISTINCT FROM OLD.spec_hash
       OR NEW.created_at IS DISTINCT FROM OLD.created_at
       OR NEW.created_by IS DISTINCT FROM OLD.created_by
       OR NEW.source_reason IS DISTINCT FROM OLD.source_reason
       OR NEW.source_evidence IS DISTINCT FROM OLD.source_evidence THEN
        RAISE EXCEPTION
            'vivarium: the sealed request (spec, spec_hash, provenance) of % is immutable',
            OLD.experiment_id
            USING ERRCODE = 'raise_exception';
    END IF;

    -- added 2026-09-06 (archaeon/003): the experimental-relation declaration
    IF NEW.family_id IS DISTINCT FROM OLD.family_id
       OR NEW.arm_id IS DISTINCT FROM OLD.arm_id
       OR NEW.replication_of IS DISTINCT FROM OLD.replication_of
       OR NEW.candidate_set_id IS DISTINCT FROM OLD.candidate_set_id
       OR NEW.request_key IS DISTINCT FROM OLD.request_key
       OR NEW.cadence_lane IS DISTINCT FROM OLD.cadence_lane
       OR NEW.cadence_day_ordinal IS DISTINCT FROM OLD.cadence_day_ordinal THEN
        RAISE EXCEPTION
            'vivarium: the experimental-relation declaration (family, arm, '
            'replication_of, candidate set, cadence) of % is immutable; a '
            'comparison may not be re-drawn after execution', OLD.experiment_id
            USING ERRCODE = 'raise_exception';
    END IF;

    -- added 2026-09-09 (vivarium/004): the address book
    IF NEW.artifact_locators IS DISTINCT FROM OLD.artifact_locators THEN
        RAISE EXCEPTION
            'vivarium: the artifact address book of % is immutable; an '
            'experiment may not be re-addressed after admission',
            OLD.experiment_id
            USING ERRCODE = 'raise_exception';
    END IF;

    IF NEW.status = OLD.status THEN
        RETURN NEW;                       -- annotation, not a transition
    END IF;

    legal := (OLD.status = 'queued'  AND NEW.status IN ('claimed', 'cancelled'))
          OR (OLD.status = 'claimed' AND NEW.status IN ('running', 'failed'))
          OR (OLD.status = 'running' AND NEW.status IN ('completed', 'failed'))
          OR transport_release;                       -- 010

    -- point release (006): claimed|running -> queued is legal ONLY inside the
    -- release path (SET LOCAL viv.release = 'new_attempt') once the row has
    -- no OPEN attempt left; every other writer meets the rule above.
    IF NOT legal AND OLD.status IN ('claimed', 'running') AND NEW.status = 'queued'
       AND current_setting('viv.release', true) = 'new_attempt' THEN
        IF (SELECT count(*) FROM {schema}.execution_attempt
             WHERE experiment_id = OLD.experiment_id AND terminal_state IS NULL) = 0 THEN
            legal := true;
        END IF;
    END IF;

    IF NOT legal THEN
        RAISE EXCEPTION 'vivarium: illegal transition % -> % on %',
            OLD.status, NEW.status, OLD.experiment_id
            USING ERRCODE = 'raise_exception';
    END IF;

    RETURN NEW;
END;
$fn$ LANGUAGE plpgsql;
