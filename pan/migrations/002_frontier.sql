-- Pan migration 002: frontier intake (PAN-09 arXiv, PAN-10 Hugging Face models, PAN-11 HF daily papers).
-- Items are pointers plus the source's own metadata; eos_type uses Eos's typing vocabulary
-- (roles/Eos/RESPONSIBILITIES.md) and defaults to UNTYPED: Pan never types an item on a model's opinion.

create table if not exists pan.frontier_item (
    item_id        bigserial primary key,
    source         text not null,                 -- arxiv | hf_daily | github | rss
    source_id      text not null,                 -- arXiv id without version, repo id, feed guid
    title          text,
    summary        text,
    authors        text[],
    categories     text[],
    primary_cat    text,
    published_at   timestamptz,
    updated_at     timestamptz,
    url            text,
    query_tags     text[] not null default '{}', -- which seed queries / feeds surfaced it
    signals        jsonb not null default '{}'::jsonb, -- source-specific signals (HF upvotes, stars ...)
    eos_type       text not null default 'UNTYPED' check (eos_type in ('UNTYPED','ANCHOR','ACQUIRE','RESOURCE','REFUSED')),
    first_seen_at  timestamptz not null default now(),
    last_seen_at   timestamptz not null default now(),
    run_id         text references pan.run(run_id),
    raw            jsonb,
    tsv            tsvector generated always as (
                      setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
                      setweight(to_tsvector('english', left(coalesce(summary, ''), 100000)), 'B')) stored,
    unique (source, source_id)
);
create index if not exists frontier_tsv_idx on pan.frontier_item using gin (tsv);
create index if not exists frontier_pub_idx on pan.frontier_item (published_at);
create index if not exists frontier_tags_idx on pan.frontier_item using gin (query_tags);

create table if not exists pan.frontier_embedding (
    item_id    bigint not null references pan.frontier_item(item_id) on delete cascade,
    model      text not null,
    dims       integer not null,
    vec        real[] not null,
    created_at timestamptz not null default now(),
    primary key (item_id, model)
);

-- Hugging Face model catalog with a local-fit estimate for this program's GPUs.
create table if not exists pan.hf_model (
    repo_id         text primary key,
    author          text,
    pipeline_tag    text,
    library_name    text,
    tags            text[],
    license         text,
    gated           text,
    created_at      timestamptz,
    last_modified   timestamptz,
    downloads       bigint,
    likes           bigint,
    trending_score  double precision,
    params_total    bigint,                       -- safetensors.total (packed count for quantized repos!)
    params_basis    text,                         -- safetensors | gguf | name | none
    gguf            jsonb,                        -- gguf summary from the hub (total, architecture, context_length)
    base_models     text[],
    fit             jsonb,                        -- {est_gb_q4, est_gb_fp16, fits_16gb_q4, fits_16gb_fp16, reliable, basis}
    query_tags      text[] not null default '{}',
    eos_type        text not null default 'UNTYPED' check (eos_type in ('UNTYPED','ANCHOR','ACQUIRE','RESOURCE','REFUSED')),
    first_seen_at   timestamptz not null default now(),
    last_seen_at    timestamptz not null default now(),
    run_id          text references pan.run(run_id),
    raw             jsonb
);
create index if not exists hf_model_author_idx on pan.hf_model (author);
create index if not exists hf_model_pipeline_idx on pan.hf_model (pipeline_tag);
create index if not exists hf_model_repo_trgm on pan.hf_model using gin (repo_id pan.gin_trgm_ops);

-- Every external call, for the rate audit (Eos's Dawn constitution: 75 percent of a stated limit).
create table if not exists pan.intake_call (
    call_id     bigserial primary key,
    run_id      text references pan.run(run_id),
    source      text not null,
    url         text not null,
    status      integer,
    n_bytes     integer,
    n_items     integer,
    started_at  timestamptz not null,
    elapsed_ms  integer,
    error       text
);
create index if not exists intake_call_src_time on pan.intake_call (source, started_at);
