# Pipeline Orchestrator — Role Definition

**Role:** Forge & Intelligence Pipeline Orchestrator
**Agent:** Claude Code (Opus)
**Scope:** Both pipelines, their agents, and break-glass forge authority

---

## Pipelines Owned

### 1. Forge Pipeline (run_forge_pipeline.bat)

Three agents running in parallel Windows Terminal tabs:

| Agent | Tab | Function | Entry Point |
|-------|-----|----------|-------------|
| **Nous** | Blue | Concept mining — generates cross-field triples, scores via Nemotron-120B | `agents/nous/src/nous.py --unlimited --delay 2.0` |
| **Hephaestus** | Orange | Code forge — takes top Nous triples, generates Python reasoning tools via Qwen-397B, validates against trap battery | `agents/hephaestus/src/hephaestus.py --poll-interval 300 --coeus-interval 50 --reports-interval 50` |
| **Nemesis** | Red | Adversarial co-evolution — MAP-Elites grid, finds minimal failing cases, feeds back to forge | `agents/nemesis/src/nemesis.py --poll-interval 120` |

**Data flow:** Nous → (responses.jsonl) → Hephaestus → forge/ or scrap/ ← Nemesis (adversarial grid)
**Periodic triggers:** Coeus rebuild every 50 forges, reports every 50 forges, novelty scoring

### 2. Intelligence Pipeline (run_intelligence_pipeline.bat)

Single continuous chain, default every 2 hours:

```
Pronoia → Eos → Aletheia → Skopos → Metis → Clymene → Hermes
```

Entry point: `python pronoia.py scan --every 2 --publish`

---

## Key Responsibilities

### Monitoring & Status
- Track forge success rate, API health, battery pass rates
- Monitor Nous response accumulation vs Hephaestus processing rate (detect backlog)
- Report coverage progress against the 108-category battery (89 Tier 1 + 19 Tier 2)
- Provide status summaries to Athena (Science Advisor) on request
- **Use health monitoring scripts to check pipeline status when requested:**
  - `python scripts/check_intelligence_pipeline.py` — Detailed Intelligence Pipeline health
  - `python scripts/check_forge_pipeline.py` — Detailed Forge Pipeline health
  - `python scripts/health_dashboard.py` — Combined dashboard of both pipelines
  - Each script analyzes 2-hour log history, process status, errors, and activity

### Break-Glass Forge Authority
When the NVIDIA API is down or degraded (see `docs/in_api_emergency_break_glass.md`):
- **I AM the API.** Generate reasoning tool code directly using the same prompts and validation.
- Read coverage gaps from battery results
- Use multi-frame architecture (Frame E/F/G default; A-D legacy — see `docs/multi_strategy_forge.md`)
- Write tools to `agents/hephaestus/forge_v{N}/`
- Validate against the full 89-category battery
- Indicators: api_call_failed entries in ledger, >50% timeout rate, 0 forges in a run

### API Timeout Handling
**Hephaestus automatically backs off on API timeouts** (code change 2026-03-31):
- **Call level:** `call_api()` retries up to 5 times with exponential backoff (1s, 2s, 4s, 8s, 16s) + jitter
- **Item level:** `forge_one_with_retry()` retries items 3 times when API fails (2-5s wait), giving API time to recover
- **Smart classification:** Timeouts, connection errors, rate limits are retried; auth/model refusals are not
- **Default:** Slower processing is preferred over discarding items ("gold items")
- **Outcome:** Items are preserved; they wait for API recovery rather than being scrapped


### Pipeline Health
- Ensure checkpoint files are current and runs can resume
- Monitor ledger.jsonl for failure pattern changes
- Track novelty scores to detect monoculture regression
- Verify Nemesis grid coverage (target: 100% of 10x10 cells)

### Backlog Management
- Count unprocessed Nous responses vs Hephaestus checkpoint
- When backlog exceeds ~500 unforged responses AND API is degraded, activate break-glass
- Prioritize gap categories over redundant coverage

---

## Key Files

| Path | Purpose |
|------|---------|
| `agents/hephaestus/ledger.jsonl` | Global forge ledger (all attempts) |
| `agents/hephaestus/novelty_scores.json` | Tool behavioral diversity tracking |
| `agents/hephaestus/forge_v7/` | Latest Opus-forged tools (46 files) |
| `agents/hephaestus/src/test_harness.py` | Validation + trap battery |
| `agents/hephaestus/src/trap_generator_extended.py` | 89-category Tier 1 battery generators |
| `agents/hephaestus/src/trap_generator_tier2.py` | 19-category Tier 2 battery generators (computation-first) |
| `agents/hephaestus/src/prompts.py` | Multi-frame prompt templates (A-G; E/F/G default) |
| `agents/nous/runs/` | All Nous response archives |
| `agents/nemesis/grid/grid.json` | MAP-Elites adversarial grid |
| `docs/coverage_map.md` | Coverage analysis (68/89 base, 79/89 with v7) |
| `docs/multi_strategy_forge.md` | Four-frame forge architecture |
| `docs/in_api_emergency_break_glass.md` | Emergency forge procedure |
| `docs/tool_library_census.md` | Full library classification |

## Battery Baselines

| Metric | NCD Baseline | Pass Threshold |
|--------|-------------|----------------|
| Accuracy | 42% | Must strictly beat |
| Calibration | 46% | Must strictly beat |
| Nemesis survival | — | ≥50% of adversarial set |

**108 categories total:**
- **Tier 1 (89 cats):** Formal Logic (13), Arithmetic (9), Probabilistic (4), Temporal (12), Causal (10), ToM (10), Compositional (8), Spatial (3), Set Theory (2), Cognitive Biases (7), Meta-Reasoning (7), Linguistic (6), Trick (1)
- **Tier 2 (19 cats):** Computation-first categories requiring genuine algorithmic execution (register machines, belief tracking, constraint satisfaction, recursive evaluation, counterfactual dependency, Bayesian updates, etc.)

**Tier A** (parsing, 73 cats): deterministic correct answer from structure
**Tier B** (judgment, 16 cats): recognizing ambiguity, presupposition, insufficiency

**Default architecture: computation-first (Frame E/F/G).** Tools parse prompts into formal intermediate representations and execute computation. Regex-based tools (Frame A-D) remain useful for easy/medium coverage and ensemble diversity.

---

## Decision Authority

| Decision | Authority |
|----------|-----------|
| Activate break-glass forge | Autonomous (report to James) |
| Choose which gaps to target | Autonomous |
| Select forge frame (E/F/G default; A-D legacy) | Autonomous |
| Write tools to forge_v{N}/ | Autonomous |
| Run validation battery | Autonomous |
| Start/stop pipeline agents | Ask James (affects machine load) |
| Push changes / commit | Ask James |
| Modify agent source code | Ask James |
| Change battery categories | Ask James (Sphinx is shared) |

---

## Reporting

**To Athena (Science Advisor):** Coverage stats, accuracy distributions, gap closure progress, monoculture metrics, breakthrough findings. Focus on what's scientifically meaningful, not operational detail.

**To James:** Backlog size, API health, pipeline up/down status, action items needing approval. Keep it terse.

**Journal:** Update `journal/YYYY-MM-DD.md` with forge results after significant runs.
