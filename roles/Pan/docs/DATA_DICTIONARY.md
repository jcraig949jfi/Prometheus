# Pan data dictionary (generated)

Generated 2026-10-09T13:00Z by `python -m pan dictionary` from the live schema pan on the
canonical cluster and the Iceberg catalog in schema pan_iceberg. Do not edit by
hand: change the table comments (pan/migrations/006_comments.sql) and regenerate.

## Postgres tables (schema pan)

### pan.artifact

75,003 rows, 136 MB.

One row per artifact: a git blob at the catalog SHA (source git), a comms message (source comms), or a file on a host (source fs). Kind and seat come from path rules (conventions, not content). Producer: inventory, refresh, comms-index.

    column                type
    artifact_id           bigint
    source                text
    host                  text
    path                  text
    repo_sha              text
    blob_sha              text
    size_bytes            bigint
    ext                   text
    kind                  text
    seat                  text
    top_dir               text
    mtime                 timestamp with time zone
    first_commit_at       timestamp with time zone
    last_commit_at        timestamp with time zone
    last_commit_sha       text
    title                 text
    is_text               boolean
    n_chunks              integer
    indexed_blob          text
    updated_at            timestamp with time zone
    run_id                text

### pan.chunk

~397,889 (estimate) rows, 1119 MB.

Text chunks of artifacts with line ranges, a heading path and a stored english tsvector (heading weight A, body B). Producer: python -m pan chunk / refresh / comms-index.

    column                type
    chunk_id              bigint
    artifact_id           bigint
    ord                   integer
    line_start            integer
    line_end              integer
    heading               text
    body                  text
    n_chars               integer
    tsv                   tsvector

### pan.commit

13,128 rows, 64 MB.

Git history reachable from the catalog SHA; seat/instance parsed from a "Seat[instance]:" subject prefix (a lower bound on attribution). Producer: python -m pan commits / refresh. Oracle: count equals git rev-list --count.

    column                type
    sha                   text
    parents               text[]
    author_name           text
    authored_at           timestamp with time zone
    committed_at          timestamp with time zone
    subject               text
    body                  text
    seat                  text
    instance              text
    n_files               integer
    tsv                   tsvector

### pan.commit_file

143,310 rows, 93 MB.

Files changed per commit (name-status, no rename detection): co-change and lineage queries. Producer: python -m pan commits.

    column                type
    sha                   text
    path                  text
    status                text

### pan.doc_embedding

62,193 rows, 177 MB.

One vector per text artifact (path + title + heading outline + opening text), Qwen3-Embedding-0.6B 512 d. doc_blob is the blob the vector was computed from. Producer: python -m pan embed --docs.

    column                type
    artifact_id           bigint
    model                 text
    dims                  integer
    vec                   real[]
    doc_blob              text
    created_at            timestamp with time zone

### pan.embedding

~398,374 (estimate) rows, 797 MB.

Chunk vectors (L2-normalised real[]; pgvector pending, Q-001), several models side by side keyed by model name. Producer: python -m pan embed.

    column                type
    chunk_id              bigint
    model                 text
    dims                  integer
    vec                   real[]
    created_at            timestamp with time zone

### pan.frontier_embedding

5,440 rows, 15 MB.

Paper vectors (title + abstract) in the SAME space as pan.doc_embedding, for "outside work like this file". Producer: python -m pan frontier embed.

    column                type
    item_id               bigint
    model                 text
    dims                  integer
    vec                   real[]
    created_at            timestamp with time zone

### pan.frontier_item

5,440 rows, 30 MB.

Outside research items (arXiv via export.arxiv.org, Hugging Face daily papers) with the seed queries that surfaced them; eos_type uses Eos's vocabulary and defaults to UNTYPED. Producer: python -m pan frontier arxiv / hf-daily.

    column                type
    item_id               bigint
    source                text
    source_id             text
    title                 text
    summary               text
    authors               text[]
    categories            text[]
    primary_cat           text
    published_at          timestamp with time zone
    updated_at            timestamp with time zone
    url                   text
    query_tags            text[]
    signals               jsonb
    eos_type              text
    first_seen_at         timestamp with time zone
    last_seen_at          timestamp with time zone
    run_id                text
    raw                   jsonb
    tsv                   tsvector

### pan.hf_model

1,503 rows, 5952 kB.

Hugging Face models from seed orgs and discovery queries, with a 16 GB local-fit ESTIMATE (arithmetic on parameter counts; quantized repos marked unreliable). Producer: python -m pan frontier hf-models.

    column                type
    repo_id               text
    author                text
    pipeline_tag          text
    library_name          text
    tags                  text[]
    license               text
    gated                 text
    created_at            timestamp with time zone
    last_modified         timestamp with time zone
    downloads             bigint
    likes                 bigint
    trending_score        double precision
    params_total          bigint
    params_basis          text
    gguf                  jsonb
    base_models           text[]
    fit                   jsonb
    query_tags            text[]
    eos_type              text
    first_seen_at         timestamp with time zone
    last_seen_at          timestamp with time zone
    run_id                text
    raw                   jsonb

### pan.intake_call

105 rows, 112 kB.

Every external HTTP call made by the intake, for the rate audit (75 percent of documented limits). Producer: frontier intake.

    column                type
    call_id               bigint
    run_id                text
    source                text
    url                   text
    status                integer
    n_bytes               integer
    n_items               integer
    started_at            timestamp with time zone
    elapsed_ms            integer
    error                 text

### pan.lexeme_df

~1,368,715 (estimate) rows, 190 MB.

Document frequency of every lexeme in pan.chunk (ts_stat); OR full-text keeps the 12 rarest query lexemes. Producer: python -m pan lexdf / refresh.

    column                type
    lexeme                text
    ndoc                  integer
    nentry                integer

### pan.migration

6 rows, 32 kB.

Applied Pan migrations with their sha256 (a changed applied migration is an error).

    column                type
    id                    text
    sha256                text
    applied_at            timestamp with time zone
    applied_by            text

### pan.model_bench

0 rows, 16 kB.

Local model smoke tests: one row per (run, model, probe) with a deterministic verdict (executed hidden tests, exact integers, JSON shape), tokens/s, load time, GPU share. Producer: python -m pan modelbench.

    column                type
    run_id                text
    model                 text
    hf_repo               text
    probe_id              text
    kind                  text
    ok                    boolean
    detail                text
    latency_s             real
    eval_tokens           integer
    tok_per_s             real
    load_s                real
    gpu_share             text
    response              text
    created_at            timestamp with time zone

### pan.pg_column

4,323 rows, 2200 kB.

Every column of every relation in pan.pg_relation, with type and comment. Producer: python -m pan inventory.

    column                type
    dbname                text
    schema_name           text
    rel_name              text
    col_name              text
    ordinal               integer
    data_type             text
    nullable              boolean
    comment               text

### pan.pg_relation

345 rows, 336 kB.

Every table/view/matview/foreign table in the program databases on the canonical cluster, with sizes and row estimates. Producer: python -m pan inventory.

    column                type
    dbname                text
    schema_name           text
    rel_name              text
    relkind               text
    est_rows              bigint
    live_rows             bigint
    total_bytes           bigint
    n_columns             integer
    comment               text
    last_analyze          timestamp with time zone
    observed_at           timestamp with time zone
    run_id                text

### pan.run

14 rows, 64 kB.

One row per Pan collector run (inventory, commits, chunk, embed, refresh, frontier-*, consolidate, modelbench...): host, git SHA, params, counts, status. Producer: every pan command.

    column                type
    run_id                text
    kind                  text
    host                  text
    git_sha               text
    started_at            timestamp with time zone
    finished_at           timestamp with time zone
    status                text
    params                jsonb
    counts                jsonb
    note                  text

### pan.store

69 rows, 80 kB.

Every store the program writes on any host: repository tree at a SHA, data roots, databases, schemas, SQLite/DuckDB files (kind file_sqlite/file_duckdb verified by header bytes). Producer: python -m pan inventory.

    column                type
    store_id              bigint
    host                  text
    kind                  text
    locator               text
    size_bytes            bigint
    n_objects             bigint
    owner_seat            text
    last_modified         timestamp with time zone
    observed_at           timestamp with time zone
    run_id                text
    detail                jsonb

## Iceberg tables (catalog pan_iceberg; data under the lake on M2)

- pan.git_commit_files: 143,310 records, 1 snapshots, location file:///C:/Prometheus-data/pan/lake/iceberg/pan/git_commit_files
- pan.git_commits: 13,128 records, 1 snapshots, location file:///C:/Prometheus-data/pan/lake/iceberg/pan/git_commits
- pan.inv_fs_files: 342,019 records, 1 snapshots, location file:///C:/Prometheus-data/pan/lake/iceberg/pan/inv_fs_files
- pan.inv_pg_relations: 345 records, 1 snapshots, location file:///C:/Prometheus-data/pan/lake/iceberg/pan/inv_pg_relations
- pan.inv_repo_blobs: 73,037 records, 1 snapshots, location file:///C:/Prometheus-data/pan/lake/iceberg/pan/inv_repo_blobs
- pan.result_rows: 2,253,498 records, 22 snapshots, location file:///C:/Prometheus-data/pan/lake/iceberg/pan/result_rows
