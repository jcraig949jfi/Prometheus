Benchmark v2 architecture accepted. Campaign 1 remains NOT AUTHORIZED.

Before either host executes request #471 or #472, add one freeze-layer amendment. Do not alter benchmark logic.

1. FREEZE THE WHOLE BENCHMARK BUNDLE

Create a canonical BENCHMARK_MANIFEST containing hashes for every input that can alter a receipt:

* benchmark harness;
* benchmark spec;
* task generators / task fixture manifest;
* fixed task seeds;
* model configuration file(s);
* generation/evaluation configuration;
* retry policy;
* starting-accuracy task manifest;
* economics receipt schema.

Record:

* git commit;
* SHA-256 of each file;
* one canonical SHA-256 of the complete manifest.

Nestor and Archaeon must record that manifest hash in every receipt.

The existing harness SHA-256 remains useful but is not sufficient by itself.

No benchmark logic needs to change for this amendment.

2. MODEL IDENTITY IS THE SERVED VARIANT

Treat the benchmark candidate as:

model checkpoint

* quantization
* runtime/server
* inference settings

not merely “Qwen3-8B”, “Gemma 3 4B”, etc.

Starting accuracy, throughput and eligibility belong to that exact served variant.

If M1 and M2 use materially different quantization or inference settings, preserve them as distinct measurements. Do not average their starting accuracies into one model-family accuracy.

3. STARTING-ACCURACY RULE

Keep the frozen 200-task / 50-per-family assay.

Eligibility remains 15%-70%.

Also report per-family starting accuracy, not only aggregate accuracy. The aggregate controls substrate eligibility unless the current preregistration says otherwise; per-family values are diagnostic only and may not be used after the fact to include or exclude a model.

Identical model/configuration + identical seed/task manifest should produce scientifically consistent starting-accuracy measurements across hosts. Any material discrepancy is an infrastructure/configuration anomaly to investigate before economics are combined.

4. QWEN THINKING MODE

The pre-result decision to disable Qwen3-8B thinking is accepted.

Record that setting as part of the exact served-variant identity and bundle manifest.

Do not later compare a thinking-enabled Qwen run against the frozen non-thinking candidate without a new benchmark amendment.

5. CONSERVATIVE WALL-TIME PROJECTION

Preserve both:

A. mean measured throughput;
B. slowest-observed-generation bound.

Add a preregistered variance-aware bound to the economics calculation, preferably an upper 95% bound derived from the observed generation-time distribution.

Report all three.

For the 30-day kill/resize rule, use the larger of:

* the preregistered variance-aware projection; and
* any stronger bound already required by the frozen design.

Do not allow one anomalous transient stall to silently redefine the entire campaign estimate, but do not discard stalls from the raw receipt either.

6. TWO-HOST COMBINATION

Continue to assign independent lineages according to measured host capacities and minimize projected makespan.

Do not average host throughput first.
Do not assume 2x scaling.
Do not allow a fast host to conceal an ineligible model/configuration on the other host.

If the exact served variant is eligible on one host and ineligible on the other because of a material configuration difference, economics may characterize each host separately but must not call them one homogeneous two-host substrate.

7. TASK-DISTRIBUTION BOUNDARY

The currently frozen four procedural task families are valid for benchmark-based substrate selection.

Archaeon’s later sealed Campaign 1 generators may replace them only through a design amendment.

If that amendment materially changes task difficulty or task form, rerun the starting-accuracy qualification on the final frozen Campaign 1 task distribution before Campaign 1 authorization.

A throughput rerun is required only if the final task workload materially changes token/evaluation economics.

Do not tune the final task distribution to force a preferred model into the 15%-70% eligibility window.

8. EXECUTION

Because Nestor and Archaeon are currently offline, post this amendment before either begins execution.

Requests #471 and #472 otherwise stand unchanged.

Campaign 1 remains blocked pending:

* valid benchmark receipt(s);
* economics analysis;
* substrate selection;
* outstanding Archaeon/Harmonia/Vivarium contracts and cheat fixtures;
* operator review of the updated Campaign 1 packet.
