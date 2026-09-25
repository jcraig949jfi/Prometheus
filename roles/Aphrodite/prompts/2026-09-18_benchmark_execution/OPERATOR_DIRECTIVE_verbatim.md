Campaign 0C and Campaign 1 design packet v2 accepted for purposes of continued design. Campaign 1 execution remains NOT AUTHORIZED.

Resolve the two open items as follows.

BENCHMARK EXECUTION

Do not repair M4 -> M1/M2 reachability as part of this campaign.

Run the frozen benchmark host-locally:

* Nestor executes the committed benchmark harness on M1.
* Archaeon executes the identical committed harness on M2.
* Both must use the same harness commit, task fixtures, generation/evaluation settings, caps, and reporting schema.
* Aphrodite receives the resulting committed benchmark receipts and derives Campaign 1 economics from them.
* No benchmark executor may alter the harness or Campaign 1 design while measuring it.

The two hosts are measurements, not interchangeable replicas. Preserve host-specific:

* model and exact checkpoint;
* quantization/runtime configuration;
* GPU identity and available memory;
* tokens/task;
* input and output tokens separately;
* wall time/evaluation;
* evaluations/generation;
* model calls/generation;
* GPU utilization and memory high-water mark;
* failure/retry rate;
* lineage throughput;
* projected 32- and 64-lineage campaign time.

If both hosts succeed, also compute the achievable two-host campaign throughput by sharding independent lineages across their measured capacities. Do not infer “2x” scaling.

If only one host produces a valid measurement, report economics for that host only. Do not extrapolate it into a two-host result.

MODEL CANDIDATES

Benchmark, in this order:

1. Qwen3-8B – primary candidate.
2. Gemma 3 4B – independent-family substrate-transfer candidate.
3. Llama 3.2 3B – fallback/reference only if useful for establishing a lower-cost throughput point.

Use a practical fixed local quantization/runtime configuration appropriate to each host, and record it exactly. Do not optimize one model repeatedly until it wins the selection rule.

These are candidates, not selected Campaign 1 substrates.

The existing selection rule remains controlling:
choose the fastest measured model whose frozen starting accuracy on the Campaign 1 task distribution lies between 15% and 70%.

If no candidate satisfies that window, return NO_ELIGIBLE_SUBSTRATE. Do not alter task difficulty or the 15-70% window after seeing benchmark results without a new design amendment.

WALL-TIME BUDGET

Freeze:

* design target: <= 14 calendar days;
* hard Campaign 1 ceiling: 30 calendar days on the available M1 + M2 capacity.

The 14-day target is not a kill gate. The 30-day ceiling is.

If the measured 64-lineage configuration projects beyond 30 days, resize in this order:

1. reduce unnecessary evaluation/token expenditure while preserving the scientific estimands and fixed-compute comparison;
2. shorten procedural task instances while preserving the frozen task-family contract and difficulty qualification;
3. reduce evolutionary effort only under a preregistered symmetric rule;
4. only then consider dropping from 64 to 32 lineages.

Never widen delta = 3 to satisfy compute constraints.

If reduced to 32, automatically narrow Campaign 1 claims to the subset supported by qualification. Do not retain 64-lineage claims by extrapolation.

Sixteen lineages remains excluded.

For projections near the 30-day boundary, use measured runtime variance and a conservative upper estimate rather than mean throughput alone.

CAMPAIGN STATUS

Campaign 0C remains a qualification of the rare-discovery instrument, not RSI evidence.

The family-correlated / task-family-specific discovery blind spot remains an explicit limitation. Do not silently broaden the secondary endpoint beyond what 0C qualified.

Once M1 and M2 receipts are committed, Aphrodite should update only the measured-economics and substrate-selection sections of the Campaign 1 packet and return it for review.

No Campaign 1 evolutionary run is authorized by this directive.
