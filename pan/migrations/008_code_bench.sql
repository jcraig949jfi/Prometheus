-- Pan migration 008: local code benchmark rows (PAN-33, HumanEval+). One row per
-- (run, model configuration, task); verdict = the executed EvalPlus test suite.
create table if not exists pan.code_bench (
    run_id       text not null references pan.run(run_id),
    model        text not null,              -- ollama:<tag>@<think|nothink><budget>
    hf_repo      text,
    task_id      text not null,
    ok           boolean not null,
    detail       text,
    latency_s    real,
    eval_tokens  integer,
    tok_per_s    real,
    response     text,
    created_at   timestamptz not null default now(),
    primary key (run_id, model, task_id)
);
comment on table pan.code_bench is 'HumanEval+ (evalplus/humanevalplus) greedy pass@1 per task for local models; verdicts are executed hidden test suites; protocol in pan/tests/codebench_prereg.json. Producer: python -m pan codebench run.';
