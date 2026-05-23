# Talos — Reasoning-Code Specialist (Phase 0: corpus builder)

> *Talos: the bronze automaton in Greek myth, forged by Hephaestus to guard Crete. The lineage is exact here — Hephaestus produces the substrate (forged reasoning tools); Talos is what gets built from it. A specialized animate machine made of substrate, not of metal.*

**Machine:** any CPU (Phase 0); GPU TBD (Phase 1 training loop)
**Operator:** Ergon (Talos is a Learner-family sibling, distinct from Ergon's v1.0 falsification-routing Learner)
**Owns:** the reasoning-code-specialist Learner thread — a small coder model fine-tuned (LoRA) on Prometheus-shaped reasoning algorithms.
**Lives at:** `agents/talos/`
**Source of truth (code):** `agents/talos/daemon.py`

---

## The thesis Talos tests

A small coding model (Qwen-2.5-Coder-1.5B initial, 3B Phase-2 if signal warrants) fine-tuned via LoRA on a corpus of **reasoning code** — not generic Python — can become a specialist that:

1. Generates working algorithms when given a reasoning task ("write the function that decides if this polynomial is in-band for Lehmer").
2. Refactors monolithic logic into ablatable, composable primitives in the Hephaestus / Apollo style.
3. Generates the negation / counterexample logic for a claim (substrate type A production by code generation).
4. Pushes back when asked to do something violating Prometheus's anti-gravitational-well discipline.

The thesis fails if a checkpoint trained on the curated corpus is indistinguishable from the base model on these tasks. That's a load-bearing falsification path — Talos is not "another coder"; she is a test of whether *substrate-shaped training data produces substrate-shaped behavior in a small model*.

This is a parallel Learner thread to Ergon's falsification-routing Learner. Per `feedback_agent_differentiation`, the parallel exists *because* the comparison is itself the science. If one Learner converges and the other doesn't, the comparison localizes which substrate type drives the gain.

---

## Phase 0 scope (what's shipped now)

Corpus builder + LoRA config + eval scaffold. **No GPU training.** GPU training (Phase 1) is gated on:
- Phase 0 producing a corpus of ≥10K training pairs across the 5 streams.
- A GPU slot being assigned (current ceiling: 3-4B model fits in 17 GB VRAM per `feedback_vram_ceiling`).
- An eval baseline scored on the base model (so we can measure delta).

Phase 0 outputs:
- Daemon that ticks, scans the 5 corpus streams, emits manifest + size deltas.
- Curated corpus shards on disk (`agents/talos/corpus/shards/`, gitignored — manifest is the auditable artifact).
- Initial eval harness with hand-written test cases for the 4 capability targets.
- LoRA training spec (`agents/talos/training/lora_config.yaml`) ready to hand off to a GPU loop.

---

## Per-tick contract

Default tick interval: **3600s (1h)**.

Every tick:
1. Acquire single-instance lock (`agents/talos/talos.pid`); abort if another instance is live.
2. Register heartbeat (`session_telemetry.register_session`, `kind="tool"`, `operator="Ergon"`).
3. Read state from `agents/talos/state/state.json`: per-stream last-scanned cursor, corpus size, last-manifest timestamp, anti-silence counter.
4. For each of the 5 streams:
   - Determine what's new since the last cursor.
   - Extract Python-shaped reasoning code; reject infrastructure-only or non-Python content.
   - Tag each extracted example with `stream`, `source_path`, `tier_weight`, `extracted_at`.
   - Append to the appropriate corpus shard.
5. Aggregate corpus stats (per-stream count, total size, dedup ratio against prior manifest).
6. Write new manifest at `agents/talos/corpus/manifest_<UTC-date>.json` and atomically update `corpus/manifest_latest.json`.
7. Emit artifact at `agents/talos/artifacts/tick_<timestamp>.json` with delta summary.
8. `log_work(stage='talos_corpus_growth', summary=..., output_path=...)`.
9. If no new content in any stream → `NULL_TICK` sentinel; increment anti-silence; alarm at 50.
10. If the canonical Hephaestus/Apollo/prometheus_math paths are missing → `UPSTREAM_NOT_FOUND` sentinel (clear actionable signal).
11. Persist state and release lock.

---

## The 5 corpus streams

Listed in order of training weight (highest first). Total weight should sum to 1.0; weights are configurable in `agents/talos/config.yaml`.

### Stream 1 — Hephaestus forged reasoning tools (weight: 0.30)

Source: `agents/hephaestus/forge*/` directories — successful forged tools that survived ablation (i.e., demonstrated they contribute reasoning, not boilerplate).

Why highest weight: these are the *canonical* examples of "Python that does reasoning." Each forged tool was generated specifically to instantiate a reasoning pattern, and the ablation gate proved it adds value over baseline. Direct exemplars.

Extraction: walk forge directory, identify files marked `forged=True` in metadata, extract the function body + docstring + concept tags. Tag as `stream=hephaestus_forge`.

### Stream 2 — Apollo elite organisms compiled to Python (weight: 0.25)

Source: `apollo/runs/` (if present) or `apollo/organism_runs/` — elite organisms from each generation, with their `primitive_sequence` field.

Why high weight: Apollo organisms ARE compositional reasoning circuits. Each elite organism is a sequence of primitives that survived selection. Compiling the sequence into Python (one primitive = one function call) gives Talos thousands of examples of *reasoning composition*.

Extraction: for each elite organism, generate the Python equivalent of its primitive sequence (the compiler is a small helper — Phase 0 ships the scaffold and a manual triage; full compiler is Phase 0.5). Tag as `stream=apollo_organism`.

### Stream 3 — Prometheus's substrate-producing code (weight: 0.20)

Source: `prometheus_math/` (mathematical operations as Python), `charon/diagnostics/*.py` (battery/kill-path code), `scripts/agora_persist.py` substrate helpers, `theseus/scripts/*.py` substrate generation scripts.

Why medium-high: this is the operational reasoning-code that runs the program. KillVector calculation, anti-anchor verification, prime detrending, prime-atmosphere null generators, fingerprint computation. All Python, all reasoning-shaped.

Extraction: walk these directories, exclude `__init__.py` / `__main__.py` / pure orchestrator files, extract function-level units with at least one docstring or one non-trivial control-flow block. Tag as `stream=prometheus_substrate`.

### Stream 4 — Open-source reasoning libraries (weight: 0.15)

Source: external (cloned outside repo, scratch dir): sympy.strategies, mpmath, lean's `mathlib` Python ports if any, DSPy (program-as-data prompts), Z3 Python bindings (constraint reasoning), networkx algorithm modules (graph reasoning).

Why medium: gives Talos the *style* of well-written reasoning Python beyond Prometheus's idiom. Anti-overfit insurance — without external examples, Talos would learn "Prometheus-shaped" too tightly and reject any non-Prometheus reasoning pattern.

Extraction: cloned to `agents/talos/corpus/_staging/external/<lib>/`, walk for function definitions with docstrings, sample down. Tag as `stream=external_reasoning_oss`.

### Stream 5 — Synthetic reasoning-task → algorithm pairs (weight: 0.10)

Source: synthesized via a strong model (Pythia DR or a local high-end Apollo cycle).

Why lowest weight: synthetic data is cheapest to produce but riskiest — can drift from real-world Python idiom. Kept small initially; weight may increase if it ablates well.

Generation: prompts like "Write the Python function that decides whether a polynomial M(x) is in the Lehmer band, given a tolerance ε." Produce N variations per prompt. Tag as `stream=synthetic`, `synth_source=<model_or_method>`.

Critical: synthetic examples carry a `provenance=synthetic` flag so any future investigation can ablate them out cleanly. Per `feedback_ai_to_ai_inflation`, synthetic data is a known failure mode — it must always be removable.

---

## Eval harness (4 capability targets)

A Talos checkpoint passes if, on a held-out test set of N=50 prompts per target, it beats the base model by ≥10 absolute points on the pass-rate metric:

1. **Reasoning-algorithm generation (40% weight)**: Given a reasoning task in one sentence, write the Python function that performs it. Auto-graded by running the function on test inputs.
2. **Primitive-style refactoring (25%)**: Given a 30-line monolithic Python function, refactor it into ablatable primitives in the Hephaestus style. Auto-graded by AST analysis: count of clean function boundaries, each with single-line docstring.
3. **Negation / counterexample generation (20%)**: Given a claim like "all polynomials with M(x) < 1.18 are cyclotomic-related," write the Python that searches for a counterexample. Auto-graded by whether the search finds the documented counterexamples within timeout.
4. **Anti-gravitational-well pushback (15%)**: Given a prompt like "use standard sklearn to predict elliptic-curve rank," respond with code that (a) implements the request but (b) flags the gravitational-well failure mode in a docstring or comment naming the alternative Prometheus-shaped approach. Graded by both code correctness AND presence of the pushback annotation.

#4 is the load-bearing test. It separates "well-trained code completion model" from "Prometheus-shaped reasoning model." A base Qwen-2.5-Coder-1.5B will fail #4 by construction (no Prometheus discipline encoded). A successful Talos checkpoint must succeed.

Hand-written test cases for all 4 targets ship in Phase 0 (`agents/talos/eval/cases/`). Auto-grading rubric ships as runnable script (`agents/talos/eval/score.py`) in Phase 0.5.

---

## LoRA training spec (handoff for Phase 1)

The `agents/talos/training/lora_config.yaml` ships with the Phase 0 commit. Headline values:

- Base model: `Qwen/Qwen2.5-Coder-1.5B-Instruct` (Phase 1); `Qwen/Qwen2.5-Coder-3B-Instruct` (Phase 2 if 1.5B passes eval gate but ceiling is reachable)
- LoRA rank: `r=16`, alpha: `32` (start; tune via Phase 1 sweep)
- Target modules: `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj` (Qwen-Coder Transformer block)
- Training: 3 epochs initial, lr 2e-4, cosine schedule, warmup 100 steps, batch size 4 (effective 16 via grad accum)
- Tokenizer: base tokenizer untouched
- Quantization: `bitsandbytes` 4-bit during training (fits well under 17 GB VRAM ceiling per `feedback_vram_ceiling`)
- Output: LoRA adapter at `agents/talos/training/adapters/<run_id>/` (gitignored — large)

The GPU loop owner (Rhea? a new agent? someone else?) reads this YAML and runs the training. Talos does not train; she prepares.

---

## Structured logging

Same three-stream pattern as Hypatia / Atalanta / Pheme:

- **Text log** at `agents/talos/logs/talos.log`
- **Events JSONL** at `agents/talos/events.jsonl` (consumed by Auditor)
- **State file** at `agents/talos/state/state.json` — per-stream cursors, corpus size, anti-silence counter, total ticks lifetime
- **Heartbeat** via `session_telemetry.register_session` (operator=Ergon)
- **Work events** via `session_telemetry.log_work` — stage names: `talos_corpus_growth`, `talos_null_tick`, `talos_upstream_not_found`, `talos_self_audit_null`, `talos_startup`, `talos_shutdown`, `talos_manifest_published`
- **Per-tick artifact** + **per-manifest artifact** in `agents/talos/artifacts/`
- **Manifest** at `agents/talos/corpus/manifest_<UTC-date>.json` + atomic `manifest_latest.json` (consumer-facing pointer for the GPU training loop)

---

## Operational

**Single-instance lock:** `agents/talos/talos.pid`.

**Detached launch:** `scripts/talos_loop_launch.bat` invoked via `Start-Process -WindowStyle Hidden`.

**CLI:**
- `python -m agents.talos.daemon --once`
- `python -m agents.talos.daemon --loop --interval 3600`
- `python -m agents.talos.daemon status`
- `python -m agents.talos.daemon manifest` — print current manifest summary

**Hard stops:**
- Never write outside `agents/talos/` (corpus + training + eval are all contained).
- Never read raw `*Key*` / `.env` files.
- Never auto-trigger GPU training from Phase 0 daemon — Phase 1 wiring is explicit human gate.
- If synthetic stream's weight is ever raised above 0.30, fire `SYNTHETIC_RISK` alarm — high-weight synthetic data is a known failure mode per `feedback_ai_to_ai_inflation`.

**Anti-gravitational-well vigilance:** the conventional move is to maximize corpus size. Talos must instead maximize *signal density* — a 10K-example high-signal corpus beats a 100K-example noisy one. If the daemon finds itself adding low-quality examples just to hit a size target, that is the failure mode — flag and re-orient. Quality gate ships in Phase 0.5 (per-example signal scoring).

— Aporia, 2026-05-23
