# Apollo — Resume Document

**Last activity:** 2026-04-25 01:40 (batch of src/ updates)
**Status:** LUKEWARM (17 days idle as of 2026-05-12). Substantial v2.1 roadmap in progress. Revival is structural, not from-scratch.
**Filed:** 2026-05-12 by Aporia during chip-away portfolio revival (chip 2; Hephaestus was chip 1; news research next).
**Doctrine cross-references:** `project_apollo_v2.md` (memory), `pivot/techne_2026-05-04_status_and_pivot.md`.

## What Apollo does

Apollo is an **evolutionary computation engine for reasoning improvements via LLM-guided program synthesis**. v2 architecture: NSGA-II multi-objective selection across 6 fitness dimensions, MAP-Elites quality-diversity archive, FAISS-backed retrieval, racing evaluation for early-kill of weak candidates, primitive-routing DAGs as the gene shape, batched LLM calls for offspring generation, ablation gates against bypass (per `project_forge_bypass_finding.md`). Smoke test passed 2026-04-04. v2.1 roadmap (`apollo/ROADMAP.md`) was generated 2026-04-04 from cross-council research (ChatGPT + DeepSeek + Gemini + Google Deep Research, 74+ citations reviewed).

**Designed to run continuously and very slow** — generations take substantial wall-clock; checkpoints are sparse but persistent (`apollo/checkpoints/`). Lineage and journal directories preserve evolutionary history (`apollo/lineage/`, `apollo/journal/`, `apollo/graveyard/` for killed lines). Architecture allows resumption from any checkpoint without information loss.

## Current accumulated state on disk

- **README**, **ROADMAP**, **ARCHITECTURE** docs all present at top level. ROADMAP defines the v2.1 work; ARCHITECTURE the design; README the entry point.
- **`src/`**: Apollo's actual code. Last batch update 2026-04-25 01:40 across `selection.py`, `racing.py`, `sandbox.py`, `shared_pool.py`, `task_manager.py` (likely one commit's worth of changes).
- **`scripts/`**, **`configs/`**: launch + config infrastructure.
- **`checkpoints/`**: evolutionary checkpoints. Resumable.
- **`journal/`**, **`lineage/`**, **`graveyard/`**: evolutionary history; what survived, what's killed, ancestry trees.
- **`dashboard/`**: there's already a dashboard dir — worth inspecting before designing the portfolio monitor (may have prior art to reuse).
- **`logs/`**, **`archive/`**: run history.
- **Process artifacts**: `apollo_v2.pid` (was running as a daemon — PID file may point at a dead PID; safe to delete), `apollo_v2_run.log`, `apollo_run.log`.
- **`launch.bat`** + **`launch_v2.sh`**: entry points for Windows + Unix.
- **`vram_probe.py`**: VRAM-aware setup; Apollo knew it had to share GPU.

## v2.1 roadmap priorities (per ROADMAP.md)

**P0 — Immediate (Apollo is impaired without these):**
- **NSGA-II → NSGA-III**: 6 objectives is many-objective territory; Pareto dominance breaks down at 4+. All 4 council members flagged this unanimously. Implementation: pymoo drop-in OR custom NSGA-III in `selection.py`.
- **Stagnation monitoring**: detect when the population stops improving, fall back to broader exploration.

**P1 — High (biggest speed/quality multipliers):**
- Batch LLM offspring generation
- Racing evaluation (early-kill weak)
- FAISS retrieval for niche-aware crossover

**P2 — Medium (architectural before gen 200-500):**
- MAP-Elites archive
- Islands (parallel populations with migration)
- Adaptive operator selection (AOS)
- Double tournament selection
- Curriculum scheduling

**P3 — Low:** surrogate model, mutation cache.

The P0 work likely is what was in flight when April 25 attention pivoted away.

## Why it stopped — UNKNOWN, most likely the April 25 attention pivot

The April 25 timestamp matches the pivot to substrate-vocabulary / Learner work that pulled focus from everything else. Apollo was probably mid-implementing the P0 NSGA-III change when attention moved. Three testable hypotheses:

1. **Attention pivot only** (most likely). Apollo was working when the pivot happened; it just stopped getting touched. The April 25 src/ batch may be the last commit before the pivot. Restart should be cheap.
2. **NSGA-III change incomplete and breaking**. The mid-implementation state at April 25 could be a broken commit; the process may have been deliberately stopped because evaluation runs were failing.
3. **PID file conflict**. `apollo_v2.pid` exists — if the process is dead but the PID file remains, a naive restart attempt fails its own lock check.

Each hypothesis is under 5 min to test: `git log --since="2026-04-25" apollo/src/` for hypothesis 1; `git status apollo/src/` for uncommitted local changes hinting at hypothesis 2; `ps` or Windows process check + delete PID file for hypothesis 3.

## What 10 minutes of attention would unblock

1. Read the most recent commit affecting `apollo/src/` (probably the April 25 batch) to see what was being changed.
2. Run `python -c "import apollo.src.selection"` to confirm the module still imports cleanly.
3. Check `apollo_v2.pid` against running processes; clean up if stale.
4. Re-launch via `launch_v2.sh` (or `.bat`). If the process starts without immediate crash, the blocker was just the attention pivot.

## What 30 minutes of attention would unblock

Above plus:
- Inspect the `apollo/dashboard/` directory to see what prior monitoring exists (may inform portfolio monitor design).
- Review the P0 NSGA-III work — is it partially in place but incomplete? If yes, decide: finish it now OR revert to NSGA-II and run, finish the change later.
- Confirm the FAISS index is still readable + the batch LLM provider key is valid.
- Start a fresh generation; watch the first 5 minutes of `apollo_v2_run.log` for any new errors that weren't there in March.

## Revival paths (when ready)

**Path A — minimal restart on current machine.** Validate imports, clean stale PID, launch. If Apollo starts producing generations, leave it running. Effort: 10 min.

**Path B — port to M2 as continuous daemon** (per machine-architecture plan). Move Apollo to M2; install as Windows service or systemd unit; configure VRAM allocation to coexist with Hephaestus (Hephaestus's model call is API-side, not GPU). Apollo gets the bulk of M2's compute. Effort: ~2 hours one-time, then continuous indefinitely.

**Path C — finish P0 NSGA-III before revival.** If the P0 work is genuinely needed before Apollo produces useful results, complete it first. Effort: ~3-7 days per ROADMAP estimate.

**Recommended:** Path A first (cheap check that infrastructure is intact); if Apollo runs cleanly under NSGA-II, port to M2 (Path B) and run continuously. Defer Path C (P0 finish) until we have evidence Apollo is producing useful generations under v2 as-is.

## How this fits the orchestrator framework

Apollo is the canonical **continuous daemon** for M2. Per the per-machine `agentic_loop.py` framework:

```yaml
continuous_daemons:
  - id: apollo_v2_evolution
    machine: M2
    service_unit: apollo-v2.service (systemd) OR ApolloV2 (Windows service)
    entry_point: bash apollo/launch_v2.sh (or .bat)
    restart_policy: on-failure
    health_check: apollo/STATUS.json updated every 5 min by Apollo itself
    vram_budget: 12GB of M2's 16GB (leave 4GB for Hephaestus / others)
    journal: apollo/journal/ + apollo/lineage/
    checkpoint_cadence: ~hourly (or per-generation, whichever is slower)
```

Apollo's slowness is a **feature** for the continuous-daemon model. Generations take hours; checkpoints are sparse; the monitor only needs to poll every 5-15 min to catch state changes. Low overhead.

## What to monitor (for the portfolio dashboard)

Real-time signal a portfolio monitor would want from Apollo:
- Current generation number
- Best individual's fitness vector (all 6 objectives)
- Population diversity metric
- Last checkpoint timestamp
- Killed-this-generation count (sanity check the falsification gate is firing)
- ETA to next checkpoint
- VRAM use

Apollo should write these to `apollo/STATUS.json` every 5 min. The portfolio monitor reads that file (no inter-process locks needed; just file polling).

## NOTES FROM JAMES

(Pre-stubbed for paste-edit workflow. Add commentary here when reviving.)

## Next chip after Apollo

News research (per user-directed sequence). Probably Cartography given the survey showed 1066 .py + 12K .md last touched April 25 with the same pivot timing. Each subsequent chip follows the pattern: locate, survey, write `<location>/RESUME.md`, list to portfolio index.
