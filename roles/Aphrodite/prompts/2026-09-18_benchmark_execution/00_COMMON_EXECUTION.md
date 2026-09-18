# 00_COMMON -- host-local execution of the frozen Campaign 1 throughput benchmark

Authority: the operator's directive of 2026-09-18 (verbatim in this
directory, OPERATOR_DIRECTIVE_verbatim.md): "Nestor executes the committed
benchmark harness on M1. Archaeon executes the identical committed harness
on M2. ... No benchmark executor may alter the harness or Campaign 1
design while measuring it." It authorises NO Campaign 1 evolution.

FROZEN HARNESS
  commit   8f229b63430c345d9d912826a0811601e89f90e9 (on origin/main)
  file     roles/Aphrodite/science/benchmark/bench.py
  sha256   618d810bd997b4967930a0350b72e10d0a10e3ed886c129fa34882fe8b96fc3d
           (LF-normalised; every receipt records it; economics.py rejects
           a receipt whose harness hash differs)
  spec     roles/Aphrodite/science/benchmark/BENCHMARK_SPEC.md

HOW (per WORKING_CONTRACT s6, run from a pinned detached worktree):
  git -C <canonical> fetch origin
  git -C <canonical> worktree add --detach <worktrees>/<seat>-aphrodite-bench 8f229b634
  cd <that worktree>/roles/Aphrodite/science/benchmark
  (serve the model with an OpenAI-compatible server on the host's GPU:
   llama.cpp server, vLLM or Ollama -- your practical choice; record it)

MODELS, in this order (candidates, not selections), one run each:
  1. Qwen3-8B      -- thinking mode DISABLED via your runtime's mechanism
                      (e.g. --extra-body '{"chat_template_kwargs":
                      {"enable_thinking": false}}' for vLLM / llama.cpp,
                      or the runtime flag); record exactly what you used
  2. Gemma 3 4B
  3. Llama 3.2 3B  -- optional lower-cost reference point
  python bench.py --host-label <M1|M2> --base-url http://127.0.0.1:<port> \
      --model <served-model-name> --checkpoint "<exact file / tag / hash>" \
      --quant "<e.g. Q4_K_M>" --runtime "<runtime + version + key flags>" \
      [--extra-body '<json>'] --out <M1|M2>_<model>.json
Use ONE practical fixed quantisation/runtime configuration per model and
host. Do not re-run a model with different settings to change its result.
If a model cannot be served on the host (memory, runtime), record that in
a short note instead of a receipt; do not substitute a different model.

REPORTING
  Commit the receipts (and any note) under your own tree:
    roles/<Seat>/benchmarks/2026-09-18_aphrodite_c1/
  Verify the commit is an ancestor of origin/main, then reply on comms to
  Aphrodite with the path and SHA. Do not interpret the numbers; Aphrodite
  derives the economics (economics.py) and returns the packet to the
  operator. Runtime per model is bounded by the harness caps (2,000 calls,
  3,600 s).
