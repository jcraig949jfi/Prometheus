# Campaign 1 host-path throughput benchmark: specification v2 (FROZEN, 2026-09-18)

Authority: operator directives of 2026-09-18 (item 8 of the post-0B
directive; the "BENCHMARK EXECUTION / MODEL CANDIDATES / WALL-TIME BUDGET"
directive, verbatim in roles/Aphrodite/prompts/2026-09-18_benchmark_
execution/). Evidence tier: a MEASUREMENT OF HARDWARE COST and of the
selection-rule input (starting accuracy); not a scientific result. No
Campaign 1 evolution is authorised.

## Executors and hosts

Nestor runs it on M1; Archaeon runs it on M2. Same harness commit, same
file (sha256 recorded in every receipt and checked by economics.py), same
fixtures, settings, caps and schema. Executors do not alter the harness
or the Campaign 1 design. M4 does not run it (not reachable; not to be
repaired in this campaign).

## Models, in order (candidates, not selections)

1. Qwen3-8B (primary). Thinking mode DISABLED (the 512-token output cap
   would otherwise truncate reasoning); pass the runtime's mechanism in
   --extra-body or the runtime flags and record it.
2. Gemma 3 4B (independent-family substrate-transfer candidate).
3. Llama 3.2 3B (optional lower-cost reference point).
One practical fixed quantisation/runtime configuration per host and
model, recorded exactly (--checkpoint, --quant, --runtime). No repeated
re-tuning of a model to pass the selection rule.

## What bench.py v2 runs (frozen settings in the file)

Phase 1 STARTING ACCURACY: base worker, 200 fixed tasks (50 per family:
arithmetic, sort-by-key, string ops, number theory), fixed seeds shared by
all hosts, temperature 0. Phase 2 LOOP: 2 lineages x 2 generations x 4
variants x 20 tasks + 3 improver calls per generation; concurrency 8;
max_tokens 512; retries 2; caps 2,000 calls and 3,600 s.
These four procedural families are FROZEN as the Campaign 1 task
distribution for substrate selection; replacing them (e.g. by Archaeon's
sealed generators) requires a design amendment and re-qualification.

## What each receipt records

harness version, sha256 and git HEAD; host label; model (requested,
served list, checkpoint, quant, runtime, extra body); GPU identity (name,
total memory, driver); starting accuracy (overall with Wilson 95%, by
family, format-failure rate); tokens in and out per task separately;
tokens per task; wall time per evaluation (mean, p95); evaluations and
model calls per generation; per-generation wall and throughput; eval
throughput (mean and conservative = min of per-generation throughputs,
or mean - 1.2816 sd when 3+); failure, retry and format-failure rates;
GPU utilisation and memory high-water mark; single-host projections for
32 and 64 lineages x evolution effort {measured, 200, 1000} x
{mean, conservative} throughput, with lineages/day.

## Economics (economics.py, run by Aphrodite on the committed receipts)

Validity: frozen harness sha256; measurement present; failure rate <=
0.05. Two-host: integer sharding of independent lineages minimising
makespan over MEASURED capacities (never an assumed 2x); one valid host
is reported alone. Selection: the fastest model (shortest conservative
64-lineage time at measured evolution effort) whose starting accuracy is
in [0.15, 0.70] on every measured host; else NO_ELIGIBLE_SUBSTRATE.
Budget (frozen): target <= 14 days; hard ceiling 30 days (conservative
throughput near the boundary). Beyond 30 days the resize ladder applies
in the operator's order; delta 3 is never widened; 16 lineages excluded.
