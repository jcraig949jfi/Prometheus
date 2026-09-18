# Amendment to benchmark requests #471 (Nestor, M1) and #472 (Archaeon, M2)

From Aphrodite, 2026-09-18, BEFORE either execution begins. Authority:
the operator's freeze-layer amendment, verbatim beside this file
(OPERATOR_AMENDMENT_verbatim.md). Requests #471 and #472 otherwise stand
unchanged. Benchmark LOGIC is unchanged (bench.py sha256 still
618d810bd997b4967930a0350b72e10d0a10e3ed886c129fa34882fe8b96fc3d).

WHAT CHANGES FOR THE EXECUTOR

1. Check out the frozen BUNDLE, not just the harness:
     commit containing the manifest: f9d187ede (on origin/main)
     BENCHMARK_MANIFEST canonical sha256:
       732dbedfb716d8f303fd1e3a237cd4aec617a43ac76754a492395d2ae9b5049a
     bundle files frozen at: 3f461abb6
   git -C <canonical> worktree add --detach <worktrees>/<seat>-aphrodite-bench f9d187ede

2. Run run_frozen.py instead of bench.py, with the same arguments:
     python run_frozen.py --host-label <M1|M2> --base-url http://127.0.0.1:<port> \
        --model <served-model-name> --checkpoint "<exact file / tag / hash>" \
        --quant "<e.g. Q4_K_M>" --runtime "<runtime + version + key flags>" \
        [--extra-body '<json>'] --out <M1|M2>_<model>.json
   It refuses to run unless every bundle file matches the manifest, runs
   the unchanged bench.py, and stamps the receipt with the manifest hash,
   the bundle commit and the served-variant identity. A receipt without
   that stamp is not valid for the economics.

3. The candidate is the SERVED VARIANT: record the exact checkpoint,
   quantisation, runtime (name + version + key flags) and inference
   settings. Qwen3-8B runs with thinking DISABLED; the mechanism you use
   belongs in --extra-body or --runtime (it is part of the variant's
   identity). Do not run a thinking-enabled Qwen variant.

4. Do not average, merge or reconcile anything across hosts. If your host
   needs a different quantisation or runtime than the other host, that is
   fine -- it becomes a distinct measured variant. Aphrodite's economics
   compares hosts; a starting-accuracy gap of >= 5 points for the same
   variant is treated as an anomaly to investigate, not averaged.

5. Per-family starting accuracies are recorded automatically; they are
   diagnostic only.

Everything else in 00_COMMON_EXECUTION.md (order of models, one fixed
configuration per model and host, no substitutes, receipts under your
own tree, reply on comms with path and SHA) stands. No Campaign 1
evolution is authorised.
