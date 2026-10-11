-- Pan migration 004: local model smoke tests (PAN-19). One row per (run, model, probe);
-- every verdict is a deterministic check (executed tests, exact integers, JSON parse),
-- never a model's opinion. The raw response is kept so any check can be re-run.
create table if not exists pan.model_bench (
    run_id       text not null references pan.run(run_id),
    model        text not null,              -- runtime tag, e.g. ollama:qwen3:8b
    hf_repo      text,                       -- matching pan.hf_model.repo_id where known
    probe_id     text not null,
    kind         text not null,              -- code | math | json
    ok           boolean not null,
    detail       text,                       -- why it failed (test output, parsed value)
    latency_s    real,
    eval_tokens  integer,
    tok_per_s    real,
    load_s       real,
    gpu_share    text,                       -- from `ollama ps` (e.g. '100% GPU')
    response     text,
    created_at   timestamptz not null default now(),
    primary key (run_id, model, probe_id)
);
