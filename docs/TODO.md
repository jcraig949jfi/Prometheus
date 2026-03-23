# Prometheus — Master TODO List

*Living document. Cleared and updated each session.*
*For strategic priority ordering, see [PRIORITIES.md](PRIORITIES.md).*
*For consolidated experimental results, see [RESULTS.md](RESULTS.md).*

---

## Ignis (Reasoning Circuit Discovery)

### Precipitation Hunt (Steps 1-4 COMPLETE, Step 5 RUNNING)
- [x] Compute Δ_proj at 1.5B <!-- 2026-03-22 -->
- [x] Expand RPH eval to 53 pairs (was 9) <!-- 2026-03-22 -->
- [x] Build reasoning subspaces at layers 14, 18, 21 <!-- 2026-03-22 -->
- [x] Compute Δ_proj across all 4 scales <!-- 2026-03-22 -->
- [ ] Analyze multi-layer Ignis run results (L14/L18/L21 at 1.5B) — **RUNNING NOW**
- [ ] If mid-layer shows different bypass/native ratio → design follow-up experiment

**Key finding:** 0.5B/1.5B/3B produce ZERO self-corrections — Δ_proj unmeasurable.
Only Qwen3-4B self-corrects (3/8 traps), subspace Δ_proj = +0.058 (weak positive).
Expanded RPH eval weakened 1.5B signal (Δ_cf 0.178→0.110) — small-N artifact confirmed.

### Alignment-Aware Fitness (from reviewer feedback)
- [x] Add alignment term to fitness: F = task_score × alignment_bonus <!-- 2026-03-22 -->
- [x] Replace Ghost Trap cosine with subspace projection test <!-- 2026-03-22 -->
- [ ] Analyze A/B: standard fitness vs alignment-aware fitness at 1.5B (Step 5 data)
- [ ] Decision table: if aligned vectors found → RPH supported; if not → strong falsification

### Full Analysis Suite (7 Verdicts) — READY TO RUN
- [ ] Kill multi-layer run (PID 4048, 12h+ running, only L14 done)
- [ ] Run `run_full_analysis.bat` on Qwen3-4B genome FIRST (the interesting one)
- [ ] Run `run_full_analysis.bat` on 1.5B genome SECOND
- [ ] Collect 7 verdicts: dose-response, ablation, probing, patching, CoT, DAS, generalization
- [ ] If all BYPASS → paper reframes around "how we proved bypass + scale threshold"
- [ ] If any PRECIPITATION → design follow-up, this changes everything

### Scale Gradient Completion
- [ ] 7B Qwen2.5 cloud run (Lambda/RunPod A100, ~$25-40)
- [ ] Update scale gradient table with 7B results
- [ ] Determine if 14B run is warranted based on 7B cos_r trend

### SAE Decomposition (Layer 3)
- [ ] Install SAELens (`pip install sae-lens`)
- [ ] Train SAE on Qwen 2.5-3B residual stream
- [ ] Decode archived best_genome.pt vectors through SAE
- [ ] Get human-readable feature decomposition — "what is the bypass doing?"
- [ ] Compare to supervised probe directions from paper 2603.16335v1

### RPH Paper
- [ ] Integrate Δ_proj results when available
- [ ] Reframe paper around bypass finding (per Claude/GPT reviewer advice)
- [ ] Separate Qwen 2.5 scale gradient from Qwen3 cross-architecture ablation (per Gemini)
- [ ] Add 7B results when available
- [ ] Submit draft for review

### Future Ideas
- [ ] EvoTorch MAP-Elites: map the *space* of vectors, not just find the best one
- [ ] Cross-prompt generalization test: train on traps A, evaluate on traps B
- [ ] Rollout stability test: do bypass vectors degrade faster than precipitation vectors over long generation?

---

## Arcanum (Waste Stream Novelty Mining)

- [ ] Smoke-test Arcanum from F:\Prometheus\arcanum\ (alert.py patched, ready to run)
- [ ] Review current 1.5B screening results
- [ ] Plan 3B screening run with Token Autopsy + Naming Scaffold
- [ ] Design cross-pollination: feed Arcanum specimens to Ignis as steering seed candidates

### Future Ideas
- [ ] Auto-catalog pipeline: Arcanum discovery → Grammata registry entry
- [ ] Cross-model specimen tracking: do the same Arcanum appear in Qwen 2.5 and Qwen 3?

---

## Eos / Dawn (Horizon Scanner)

### Scanners — To Wire
- [ ] Groq as fallback LLM (verified: 14.4K RPD free)
- [ ] Cerebras for deep analysis (verified: Qwen 3-235B FREE)
- [ ] Serper for targeted web searches (2500 lifetime budget — conserve)
- [ ] OpenRouter as fallback model router (rate limits TBD)

### Scanners — Planned
- [ ] Semantic Scholar bulk dataset download (CS papers subset)
- [ ] `scan_local_s2()` — query local S2 database, zero API overhead
- [ ] SPECTER v2 embedding search (semantic similarity without LLM)

### Metis Integration
- [x] Schedule Metis to auto-run after Eos via Pronoia <!-- 2026-03-22 -->
- [ ] Add Ignis run status to Metis project context feed
- [ ] Add precipitation hunt results to Metis context when available

### Infrastructure
- [x] Paper dedup across cycles (PaperIndex in eos_daemon.py) <!-- 2026-03-22 -->
- [x] Persistent paper/repo index (data/paper_index.json) <!-- 2026-03-22 -->
- [ ] Add log file output alongside console
- [ ] Alert mechanism — flag critical findings for immediate attention
- [ ] NVIDIA NIM rate limits — determine and document

### Future Ideas
- [ ] Eos self-improvement: let Metis suggest new search terms based on findings
- [ ] Citation graph walking: when a paper scores high, auto-fetch its references

---

## Pronoia (Agent Orchestrator — NEW)

- [x] Built pronoia.py with scan/eos/metis/status/review commands <!-- 2026-03-22 -->
- [x] --every flag for continuous cycling <!-- 2026-03-22 -->
- [x] --publish flag: auto-commit+push reports to GitHub after each cycle <!-- 2026-03-22 -->
- [ ] Add `ignis` command: launch Ignis + Night Watchman pair
- [ ] Add `rph-eval` command: run RPH eval on latest archives
- [ ] Add `all` command: Eos → Metis → review_watchman in one pass
- [ ] Log all agent outputs to `pronoia/logs/YYYY-MM-DD.log`
- [ ] Process health monitoring: detect if a child process died

### NotebookLM Audio Blog Pipeline
- [ ] Auto-generate session summary for NotebookLM after each major session
- [ ] Template: gather results, findings, decisions, anecdotes → structured markdown
- [ ] Pronoia `blog` command: collects RESULTS.md + session log + agent outputs → blog draft

### Future Ideas
- [ ] Pronoia as always-on daemon: manage all agents, auto-restart on failure
- [ ] Web dashboard: simple Flask page showing agent status, last outputs, next scheduled run

---

## Prometheus (Infrastructure & Organization)

### Git & GitHub
- [x] Create GitHub repo (Prometheus) <!-- 2026-03-22 -->
- [x] Push initial commit <!-- 2026-03-22 -->
- [ ] Archive old repos (bitfrost-mech, ArcanumInfinity) as read-only

### Path Portability
- [ ] Verify F:\Prometheus\ignis runs end-to-end (with results/ directory)
- [ ] Test WSL2 mount compatibility (/mnt/f/Prometheus)

### Google Billing
- [ ] Check billing status, either unlink or create billing-free API key
- [ ] Confirm free tier limits before enabling Gemini in Eos

### Autonomy & Automation
- [ ] Design science synthesis pipeline: raw results → RESULTS.md → paper sections
- [ ] Design autonomous experiment loop: Pronoia queues → Ignis runs → Watchman analyzes → Metis synthesizes
- [ ] Evaluate Claude Code Agent SDK for running Athena as a persistent research agent

### Clymene (Knowledge Hoarder — NEW)
- [x] Build Clymene agent: manifest-driven repo/model archiver <!-- 2026-03-22 -->
- [x] Hoard 26 repos (tensor, mech-interp, evolutionary, agents, datasets) <!-- 2026-03-22 -->
- [x] Register 4 active models in vault registry <!-- 2026-03-22 -->
- [ ] Add Clymene to Pronoia (weekly repo update cycle)
- [ ] Identify more repos from Aletheia's tools table — auto-feed to manifest

### Titan Council (Cross-Model Collaboration)
- [ ] Template: hypothesis → critique prompt for all 5 Titans
- [ ] When Aletheia flags related papers → queue as reproduction candidates
- [ ] Wire Gemini free API into Eos as backup analyzer (free tier)
- [ ] Wire DeepSeek API as cheap ($0.28/M) secondary reviewer

### Future Ideas
- [ ] Helios (GPU scheduler): auto-queue experiments, keep GPUs saturated 24/7
- [ ] Hermes (inter-agent messaging): structured message passing between Eos, Metis, Ignis, Pronoia

---

## Aethon (RLHF Gravity Navigation — Backburnered)

- [ ] Review concept docs for relevance to current Ignis bypass findings
- [ ] Design experiment: can Aethon-style prompts activate Ignis-discovered vectors?

### Future Ideas
- [ ] If alignment-aware search finds native vectors, test if promptable without steering
- [ ] Aethon as the "deployment bridge": mechanistic findings → practical prompt techniques

---

## Grammata (Taxonomy & Cartography — Planned)

- [ ] Design registry schema (what fields describe a "reasoning construct"?)
- [ ] First entry: document the bypass/native classification from Ignis

### Future Ideas
- [ ] SAE feature names as the natural vocabulary for Grammata entries
- [ ] Visual atlas: 2D projection of discovered vector space with labeled regions
