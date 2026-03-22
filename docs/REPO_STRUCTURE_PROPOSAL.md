# Repo Structure Proposal
*Date: 2026-03-21*

---

## The Core Question: Sub-Project or Extension?

**Answer: RPH is the scientific theory. Ignis (formerly SETI v2) is the experimental engine. They are one thing.**

The `reasoning-precipitation` GitHub repo was a well-intentioned false start — Claude Code built
it from scratch without knowing Ignis existed. Once Ignis was shown, the correct call was
immediately clear: don't rebuild, integrate. The `reasoning-precipitation` repo is now a source
of real metric code to port (Δ_cf, MI_step, Δ_proj, statistical_tests), nothing more.

There is no meaningful distinction between "RPH sub-project" and "Ignis extension." They share:
- the same model (Qwen residual stream)
- the same genome format (SteeringGenome)
- the same search engine (CMA-ES → MAP-Elites)
- the same experimental subjects (steering vectors as precipitation candidates)

What they add to each other: Ignis adds the search infrastructure; RPH adds the measurement
framework that answers whether what was found is *bypass* or *precipitation*.

**Conclusion: One project. Needs a name and a home worthy of what it actually is.**

---

## Current State (What We Have)

```
f:\bitfrost-mech\                         ← git root
├── aethon/                               ← prompt-level MAP-Elites
├── bitfrost-core/                        ← shared infra, data, models
├── bitfrost-mech/                        ← confusing inner folder
│   ├── seti-pipeline/                    ← v1, probably stale
│   ├── seti-pipeline_v2/                 ← THE THING (currently running)
│   │   ├── src/                          ← all working code
│   │   ├── configs/marathon.yaml
│   │   ├── data/
│   │   └── results/
│   ├── mech/                             ← path patching, CSI gate (code not yet written)
│   ├── EXISTENCE_PROOF_SPEC.md           ← mechanistic gate: PASSED
│   ├── results/
│   └── tests/
├── docs/                                 ← RPH theory docs (good location)
├── prometheus/                           ← dual-classifier
├── reasoning-precipitation/             ← false start repo (port metrics then archive)
└── vesta/                               ← agent registry
```

Problems with current state:
1. **Three-level nesting:** `f:\bitfrost-mech\bitfrost-mech\seti-pipeline_v2\` buries the main project
2. **`seti-pipeline_v2` is not a first-class name** — version suffixes in directory names are fragile
3. **`reasoning-precipitation/` is a ghost** — useful code already documented for porting, the repo itself adds confusion
4. **`mech/` is split** — the path patching spec lives in `bitfrost-mech/EXISTENCE_PROOF_SPEC.md`, code would live in `bitfrost-mech/mech/`, and it's all buried in the inner folder
5. **`seti-pipeline/` (v1)** is presumably stale and taking up mental space

---

## Proposed Clean Structure

```
f:\bitfrost-mech\
├── aethon/                               ← unchanged
├── bitfrost-core/                        ← unchanged
├── docs/                                 ← unchanged (already well-organized)
│   ├── RPH.md                            ← original ChatGPT session (archive, keep)
│   ├── reasoning_precipitation_v4_final.md  ← the paper
│   ├── RPH_experimental_section.md       ← ✅ extracted
│   ├── RPH_phase2_implementation.md      ← ✅ extracted
│   ├── RPH_paper_draft.md               ← ✅ extracted
│   └── RPH_SETI_Integration_Strategy.md  ← ✅ integration plan
├── mech/                                 ← ELEVATED from bitfrost-mech/mech/
│   ├── EXISTENCE_PROOF_SPEC.md           ← move here
│   └── src/                              ← path_patching.py, csi_gate.py (Phase 2)
├── prometheus/                           ← unchanged
├── seti/                                 ← ELEVATED + RENAMED from bitfrost-mech/seti-pipeline_v2/
│   ├── src/
│   │   ├── seti_orchestrator.py
│   │   ├── tii_engine.py
│   │   ├── fitness.py
│   │   ├── genome.py
│   │   ├── inception_protocol.py
│   │   ├── probe_runner.py
│   │   ├── night_watchman.py
│   │   ├── review_watchman.py
│   │   ├── seti_log_analyzer.py
│   │   ├── stop_seti.py
│   │   └── rph_metrics.py               ← TO BUILD (Phase 1)
│   ├── configs/
│   │   └── marathon.yaml
│   ├── data/
│   │   └── rph_counterfactual_pairs.json ← TO BUILD (Phase 1)
│   ├── results/                          ← gitignored run outputs
│   └── README.md                         ← comprehensive, first-class
└── vesta/                                ← unchanged
```

**Archived / deleted:**
- `bitfrost-mech/` inner folder (dissolved — contents moved up or archived)
- `bitfrost-mech/seti-pipeline/` (v1 — archive or delete)
- `reasoning-precipitation/` (after RPH metrics ported — archive or delete)

---

## Naming Discussion

**Resolution: `ignis/`** — Latin for "fire," chosen to match the Prometheus naming convention
(Greek/Latin mythology). The project was renamed from SETI v2 to Ignis as part of the
Prometheus reorganization. The code internally still uses some `seti_` prefixes in filenames
(e.g., `seti_orchestrator.py`) which will be updated incrementally.

---

## When to Execute

**NOT NOW.** The 1.5B run is live. Moving `seti-pipeline_v2/` out from under a running process
would break the PID file, log paths, and result directory references mid-run.

**Execute after the current run completes.** The run takes roughly 1–2 days. When it finishes:

1. Archive run results (`archive_run.py` already exists for this)
2. Do the rename/move while no process is running
3. Update any hardcoded paths (log launchers, `seti_launch.log` references)
4. Test that `python src/main.py --config configs/marathon.yaml` still works from new location

---

## Phase 1 Build List (Can Do While Run Is Live)

These don't require touching the running pipeline:

1. **`src/rph_metrics.py`** — port Δ_cf, MI_step, Δ_proj, classify_vector() from reasoning-precipitation
2. **Extend `genome.py`** — add RPH fields with defaults (backward compatible)
3. **Add `score_rph_proxies()`** to `fitness.py` — disabled by default (`enabled: false`)
4. **Add `rph_proxies` config block** to `marathon.yaml`
5. **`data/rph_counterfactual_pairs.json`** — merge the 9 pairs from reasoning-precipitation
6. **Analyzer upgrades** — surface RPH signals in seti_log_analyzer, night_watchman, review_watchman

---

## The Final Scientific Picture

At full build, this project makes a layered claim:

> **Layer 1 (behavioral):** Steering vectors reliably induce correct reasoning behavior on hard traps.
>
> **Layer 2 (geometric):** These vectors align with endogenous reasoning states (Δ_proj > 0), not random directions.
>
> **Layer 3 (mechanistic):** The effect is mediated through sparse, identifiable internal features (SAE mediation ≥ 30% drop).
>
> **Layer 4 (structural):** Reasoning corresponds to a structured, low-measure subspace of activation space (MAP-Elites landscape, ~8% of novelty vectors).
>
> **Layer 5 (scale):** The cosine-fitness zero-crossing between 0.5B → 3B marks where circuit development crosses the threshold for native precipitation (H3).

Each layer is testable and falsifiable. Each has a go/no-go gate. The current 1.5B run is testing H3 at Layer 5.
