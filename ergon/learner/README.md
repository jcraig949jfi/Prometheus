# Ergon Learner — MVP Build

**Status:** MVP build in progress. Design frozen at v8 (`pivot/ergon_learner_proposal_v8.md`). Target: 15-day MVP, 30-day deadline.

## Canonical design

Read in order:
1. [`pivot/ergon_learner_v7_final.md`](../../pivot/ergon_learner_v7_final.md) — full operational treatment (architecture + libraries + risks + logging + RAG + LLM strategy)
2. [`pivot/ergon_learner_proposal_v8.md`](../../pivot/ergon_learner_proposal_v8.md) — focused delta with four-trial structure and round-6 revisions
3. [`pivot/ergon_learner_proposal_v5.md`](../../pivot/ergon_learner_proposal_v5.md) — full architectural treatment (canonical)
4. [`pivot/ergon_learner_proposal_v6.md`](../../pivot/ergon_learner_proposal_v6.md) — operational refinements

## MVP structure

```
ergon/learner/
├── README.md                 — this file
├── MVP_PLAN.md               — day-by-day execution plan (Days 1-30)
├── genome.py                 — Genome dataclass; typed DAG over arsenal atoms
├── archive.py                — MAP-Elites archive with content-aware 5-axis descriptor
├── descriptor.py             — Behavior descriptor (hot-swappable per v5 §6.2)
├── scheduler.py              — Operator-class scheduler with minimum-share enforcement
├── reward.py                 — Agreement-weighted reward (substrate + cross-model + holdout + non-LLM + residual)
├── triviality.py             — F_TRIVIAL_BAND_REJECT signature library (4 static + 2 temporal)
├── stability.py              — Magnitude perturbation-stability check
├── operators/
│   ├── __init__.py
│   ├── structural.py         — DAG topology mutation
│   ├── symbolic.py           — Argument-value mutation
│   ├── anti_prior.py         — Anti-correlated with corpus frequency stats
│   ├── uniform.py            — Strawman null
│   └── structured_null.py    — Type-respecting null
├── trials/
│   ├── __init__.py
│   ├── trial_1_residual_benchmark.py        — Adversarial residual benchmark
│   ├── trial_1_5_optimization_probe.py      — Adversarial optimization probe
│   ├── trial_2_evolutionary_engine.py       — Bounded buckets + trivial detector
│   └── trial_3_five_counts_diagnostic.py    — Multi-arm pilot
└── tests/
    ├── __init__.py
    ├── test_genome.py
    ├── test_archive.py
    ├── test_descriptor.py
    ├── test_scheduler.py
    ├── test_reward.py
    ├── test_triviality.py
    └── test_stability.py
```

## Library commitments (per v8 §10)

- **PyTorch 2.x** — primary ML
- **Hugging Face Transformers + PEFT + TRL + bitsandbytes** — LoRA stack (v0.5+)
- **Unsloth** — LoRA training at MVP (faster, less VRAM than Axolotl)
- **vLLM** — inference serving (v0.5+)
- **pyribs** — MAP-Elites archive (with pointer-storage discipline; heavy data in Postgres)
- **DEAP** — genetic operator implementations
- **LiteLLM** — cross-model evaluator API standardization (v0.5+)
- **scipy.stats** — Welch t-test, Holm correction, ECE
- **PostgreSQL + pgvector + TimescaleDB** — substrate storage
- **Redis 7+** — agora message bus
- **structlog + Grafana** — observability

## Trials sequence

1. **Trial 1 (Days 1-4):** Residual classifier benchmark on 200 curated samples
2. **Trial 1.5 (Days 5-7):** Adversarial optimization probe (gates Trial 2)
3. **Trial 2 (Days 8-17):** Evolutionary engine; primary criterion `structural ≥1.5× uniform` on signal-class-residual rate
4. **Trial 3 (Days 18-22):** Five-counts diagnostic on three-arm pilot

15-day target with 30-day deadline (15-day buffer for debugging interaction effects per round-6 reviewer guidance).

## Open simulation requests

Two external-reviewer simulation offers accepted:
- [`pivot/simulation_request_round4_reviewer.md`](../../pivot/simulation_request_round4_reviewer.md) — 10K-episode pilot outcome distributions
- [`pivot/simulation_request_round6b_reviewer.md`](../../pivot/simulation_request_round6b_reviewer.md) — pass/fail patterns per trial

These run in parallel with MVP build; provide a-priori expected-distribution baseline against which actual MVP results compare.
