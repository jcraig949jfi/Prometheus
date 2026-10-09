-- Pan migration 001: the catalog core (roles/Pan/BACKLOG_H0H5.md PAN-01, PAN-03, PAN-04, PAN-06, PAN-12).
-- Schema pan on prometheus_fire (prometheus-canonical). Every row points at an
-- authoritative source; nothing here is the source of anything but itself.

create extension if not exists pg_trgm with schema pan;

-- One row per collector run: what ran, where, against which SHA, and what it produced.
create table if not exists pan.run (
    run_id        text primary key,               -- e.g. inv-20261009T1120Z-spectrex5
    kind          text not null,                  -- inventory | catalog | chunk | embed | commits | frontier-* ...
    host          text not null,
    git_sha       text,
    started_at    timestamptz not null default now(),
    finished_at   timestamptz,
    status        text not null default 'RUNNING', -- RUNNING | OK | FAILED | PARTIAL
    params        jsonb not null default '{}'::jsonb,
    counts        jsonb not null default '{}'::jsonb,
    note          text
);

-- Every store the program writes, on any host: a repository tree, a data root,
-- a database, a schema, a SQLite/DuckDB file, a Parquet set, an Iceberg table.
create table if not exists pan.store (
    store_id      bigserial primary key,
    host          text not null,                  -- SPECTREX5 | SKULLPORT | repo (host-independent, at a SHA)
    kind          text not null,
    locator       text not null,                  -- path, db.schema, db, or git:<sha>
    size_bytes    bigint,
    n_objects     bigint,                         -- files, tables, rows: see detail.unit
    owner_seat    text,
    last_modified timestamptz,
    observed_at   timestamptz not null default now(),
    run_id        text references pan.run(run_id),
    detail        jsonb not null default '{}'::jsonb,
    unique (host, kind, locator)
);

-- One row per artifact (a git blob at the catalog SHA, or a file on a host).
create table if not exists pan.artifact (
    artifact_id     bigserial primary key,
    source          text not null,                -- git | fs
    host            text not null,                -- 'repo' for git rows
    path            text not null,                -- repository-relative for git; absolute for fs
    repo_sha        text,                         -- the tree the git row was read from
    blob_sha        text,
    size_bytes      bigint,
    ext             text,
    kind            text,                         -- journal | prompt | prereg | result | receipt | status | charter | code | data | doc | config | binary | archive | other
    seat            text,                         -- owner by path rule (roles/<Seat>/, mapped top dirs); null if unknown
    top_dir         text,
    mtime           timestamptz,                  -- fs rows only
    first_commit_at timestamptz,
    last_commit_at  timestamptz,
    last_commit_sha text,
    title           text,                         -- first markdown heading or docstring line
    is_text         boolean,
    n_chunks        integer,
    indexed_blob    text,                         -- blob_sha whose text is in pan.chunk (incremental refresh key)
    updated_at      timestamptz not null default now(),
    run_id          text references pan.run(run_id),
    unique (source, host, path)
);
create index if not exists artifact_kind_idx on pan.artifact (kind);
create index if not exists artifact_seat_idx on pan.artifact (seat);
create index if not exists artifact_ext_idx on pan.artifact (ext);
create index if not exists artifact_last_commit_idx on pan.artifact (last_commit_at);
create index if not exists artifact_path_trgm on pan.artifact using gin (path pan.gin_trgm_ops);

-- Text chunks with a stored full-text vector (heading weighted A, body B).
create table if not exists pan.chunk (
    chunk_id     bigserial primary key,
    artifact_id  bigint not null references pan.artifact(artifact_id) on delete cascade,
    ord          integer not null,
    line_start   integer,
    line_end     integer,
    heading      text,
    body         text not null,
    n_chars      integer not null,
    tsv          tsvector generated always as (
                    setweight(to_tsvector('english', coalesce(heading, '')), 'A') ||
                    setweight(to_tsvector('english', left(body, 200000)), 'B')) stored,
    unique (artifact_id, ord)
);
create index if not exists chunk_tsv_idx on pan.chunk using gin (tsv);
create index if not exists chunk_artifact_idx on pan.chunk (artifact_id);

-- Embeddings, one row per (chunk, model); real[] until pgvector exists on the
-- cluster (roles/Pan/QUESTIONS.md Q-001). Vectors are L2-normalised.
create table if not exists pan.embedding (
    chunk_id     bigint not null references pan.chunk(chunk_id) on delete cascade,
    model        text not null,
    dims         integer not null,
    vec          real[] not null,
    created_at   timestamptz not null default now(),
    primary key (chunk_id, model)
);

-- Git history (PAN-06): one row per commit reachable from the catalog SHA.
create table if not exists pan.commit (
    sha           text primary key,
    parents       text[] not null,
    author_name   text,
    authored_at   timestamptz,
    committed_at  timestamptz,
    subject       text,
    body          text,
    seat          text,                           -- from the "Seat[instance]:" subject prefix, if present
    instance      text,
    n_files       integer,
    tsv           tsvector generated always as (
                     setweight(to_tsvector('english', coalesce(subject, '')), 'A') ||
                     setweight(to_tsvector('english', left(coalesce(body, ''), 100000)), 'B')) stored
);
create index if not exists commit_tsv_idx on pan.commit using gin (tsv);
create index if not exists commit_seat_idx on pan.commit (seat);
create index if not exists commit_time_idx on pan.commit (committed_at);

create table if not exists pan.commit_file (
    sha     text not null references pan.commit(sha) on delete cascade,
    path    text not null,
    status  text,
    primary key (sha, path)
);
create index if not exists commit_file_path_idx on pan.commit_file (path);

-- The cluster's own catalog (PAN-12): every relation and column in every
-- program database, so "which table holds X" is a query.
create table if not exists pan.pg_relation (
    dbname        text not null,
    schema_name   text not null,
    rel_name      text not null,
    relkind       text not null,                  -- r table, p partitioned, v view, m matview, f foreign
    est_rows      bigint,
    live_rows     bigint,
    total_bytes   bigint,
    n_columns     integer,
    comment       text,
    last_analyze  timestamptz,
    observed_at   timestamptz not null default now(),
    run_id        text references pan.run(run_id),
    primary key (dbname, schema_name, rel_name)
);
create table if not exists pan.pg_column (
    dbname        text not null,
    schema_name   text not null,
    rel_name      text not null,
    col_name      text not null,
    ordinal       integer not null,
    data_type     text,
    nullable      boolean,
    comment       text,
    primary key (dbname, schema_name, rel_name, col_name)
);
create index if not exists pg_column_name_trgm on pan.pg_column using gin (col_name pan.gin_trgm_ops);
create index if not exists pg_relation_name_trgm on pan.pg_relation using gin (rel_name pan.gin_trgm_ops);

comment on schema pan is 'Pan (roles/Pan): catalog, indices and lake pointers over every program store. Sources stay authoritative; rows here are pointers plus extracted text.';
