# Campaign 1 host-path throughput benchmark: specification (2026-09-18)

Authority: operator directive of 2026-09-18, item 8 ("run a bounded
throughput benchmark on the intended M1/M2 host path using representative
short procedural tasks and the actual evolutionary/evaluation loop.
Measure rather than extrapolate ... This benchmark authorizes no Campaign
1 evolution."). Evidence tier: a MEASUREMENT OF HARDWARE COST, not of any
scientific quantity.

## What it runs (bench.py)

The loop shape of Campaign 1 at capped scale: per lineage and generation,
the improver makes (variants - 1) model calls proposing worker
instructions; each variant is evaluated on tasks-per-eval short
procedural tasks (four families: arithmetic, sort-by-key, string ops,
number theory; answers checked by code; one model call per task); the
best variant is kept. Defaults: 2 lineages x 2 generations x 4 variants x
20 tasks = 320 task evaluations + 12 improver calls. Hard caps: 2,000
model calls, 3,600 s wall; the script refuses more than 4 lineages or 3
generations. Concurrency 8 (to use a batching server).

## What it measures

tokens/task (mean, p50, p95); wall time per evaluation (mean, p95);
evaluations per generation; wall per generation; evaluation throughput at
the chosen concurrency; lineage cost (tokens, wall); GPU utilisation and
memory (nvidia-smi, 1 s); task accuracy (only to show the tasks are not
trivially failed -- not a result); and a projection of full-campaign
task evaluations and single-host wall days for L = 32 and 64, 8
generations, at the measured evaluations/generation and at 200 and 1,000.

## Host path (the gate this seat cannot pass)

It must run ON M1 or M2 against an OpenAI-compatible server (llama.cpp
server, vLLM or Ollama) serving the candidate small model on the RTX
5060. From M4 (harry1) neither host is reachable (ssh port 22 timed out;
no model server on 11434/8000/8080/5000/1234; probed 2026-09-18). The
operator decides who runs it (the operator, or a seat on M1/M2) and which
model to serve. One command:
    python roles/Aphrodite/science/benchmark/bench.py --base-url http://127.0.0.1:<port> \
        --model <served-model-name> --out <host>_<model>_bench.json
Commit the JSON under roles/Aphrodite/science/benchmark/results/ (or post
it to Aphrodite on comms); run once per candidate model.

## Validation done here

Dry run with the stub model on M4: 332 calls, 320 evaluations; task
generators and checkers verified. Stub timings are meaningless by design.
