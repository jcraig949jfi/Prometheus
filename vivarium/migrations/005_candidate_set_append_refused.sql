-- 005: A CANDIDATE SET IS REGISTERED ONCE. Appending to it is refused.
--      (Vivarium, 2026-09-12, operator directive "close the residual burst path")
--
-- WHAT HAPPENED. On 2026-09-10/11 a campaign producer reused ONE
-- candidate_set_id across 256 separate submit calls to carry the CAMPAIGN
-- grouping. The contract says a set is one atomic registration with one
-- selection; viv/selection.py, doing what the contract says, registered every
-- other member as an UNCOMMITTED "alternative" experiment in the engine --
-- about 255 per row, 85,727 phantom experiments in this seat's worlds, and
-- the write bursts that preceded both engine stalls of 09-11.
--
-- Archaeon's writer now refuses a reused id (archaeon/vivqueue.py
-- assert_candidate_set_unused, 6fc3ea619). That is a check in ONE writer's
-- Python. This seat's own writer (viv/queue.py enqueue, viv.cli enqueue) had
-- no such check, and a plain SELECT-then-INSERT in either writer cannot hold
-- under a race. The invariant belongs in the database, where every writer
-- meets it (RESPONSIBILITIES: "if a new invariant can be a constraint, a
-- trigger or an index, it must be").
--
-- THE INVARIANT. A row may carry a candidate_set_id that already has rows
-- ONLY inside the same transaction that wrote those rows. Same transaction =
-- the atomic registration Archaeon's submit performs (N candidates, one
-- INSERT loop, one COMMIT). A later transaction naming that id is an APPEND
-- and is refused with SQLSTATE 'VIV01' before the row lands.
--
-- HOW THE RACE IS CLOSED. The trigger takes a transaction-scoped advisory
-- lock on the id before it looks. Two transactions racing to register the
-- same id serialise on the lock; the second's EXISTS runs after the first
-- committed (READ COMMITTED takes a fresh snapshot per statement) and sees it.
-- A refusal is an exception, so nothing of the refused transaction lands.
--
-- WHAT IT DOES NOT TOUCH. Rows with candidate_set_id NULL (campaign rows after
-- Archaeon's fix carry the campaign in source_evidence.campaign_set). Updates
-- (candidate_set_id is already frozen by the relation trigger of 002).
-- Historical rows: 510 sets already misregistered stay as they are; this
-- refuses the NEXT append, it does not rewrite the past.

CREATE OR REPLACE FUNCTION {schema}.candidate_set_append_refused()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    prior integer;
BEGIN
    IF NEW.candidate_set_id IS NULL THEN
        RETURN NEW;
    END IF;
    -- serialise every writer that names this id, for the rest of this xact
    PERFORM pg_advisory_xact_lock(hashtext('{schema}.candidate_set:' || NEW.candidate_set_id));
    SELECT count(*) INTO prior
      FROM {schema}.research_experiment_queue q
     WHERE q.candidate_set_id = NEW.candidate_set_id
       AND q.xmin <> pg_current_xact_id()::xid;      -- written by ANOTHER xact
    IF prior > 0 THEN
        RAISE EXCEPTION USING
            ERRCODE = 'VIV01',
            MESSAGE = format('candidate_set_id %s already has %s registered row(s); '
                             'a candidate set is registered in ONE transaction and never appended',
                             NEW.candidate_set_id, prior),
            HINT = 'For a campaign whose rows all execute, pass no candidate_set_id and carry the '
                   'campaign id in source_evidence.campaign_set. For a new set, use a new id.';
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_candidate_set_append_refused
    ON {schema}.research_experiment_queue;
CREATE TRIGGER trg_candidate_set_append_refused
    BEFORE INSERT ON {schema}.research_experiment_queue
    FOR EACH ROW
    EXECUTE FUNCTION {schema}.candidate_set_append_refused();
