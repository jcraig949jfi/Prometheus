-- Pan migration 010: review queue (PAN-37). One row per Python module at the catalog sha: measured signals
-- that say where a review is most likely to pay. A derived snapshot, rebuilt by `python -m pan review build`;
-- Pan never dispatches review work from it (QUESTIONS.md Q-011).

create table if not exists pan.review_unit (
    path            text primary key,
    repo_sha        text not null,
    seat            text,                          -- seats of the last 30 days' commits, else the path's seat
    lines           integer,
    commits_7d      integer not null default 0,
    commits_30d     integer not null default 0,
    last_commit_at  timestamptz,
    tested_by       integer not null default 0,    -- test files that import this module (static)
    smells          jsonb not null default '{}'::jsonb,   -- kind -> line numbers (capped at 20 each)
    dup_chunks      integer not null default 0,    -- chunks that are verbatim copies of another file's chunk
    score           double precision not null default 0,
    run_id          text references pan.run(run_id),
    built_at        timestamptz not null default now()
);
create index if not exists review_unit_score_idx on pan.review_unit (score desc);
