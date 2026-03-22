# Prometheus — Master TODO List

*Living document. Check off items as completed. Updated each session.*
*For strategic priority ordering, see [PRIORITIES.md](PRIORITIES.md).*

---

## Ignis (Reasoning Circuit Discovery)

### Active Run
- [ ] Monitor Qwen3-4B overnight run — check results
- [ ] Archive Qwen3-4B run when complete
- [ ] Run RPH eval across all archived scales: 0.5B, 1.5B, 3B + Qwen3-4B
- [ ] Review scale gradient — cross-architecture comparison (Qwen 2.5 vs Qwen 3)

### Scale Gradient Completion
- [ ] 7B Qwen2.5 cloud run (Lambda/RunPod A100, ~$25-40)
- [ ] Update scale gradient table with 7B results
- [ ] Determine if 14B run is warranted based on 7B outcome

### SAE Decomposition (from paper 2603.16335v1)
- [ ] Install SAELens (`pip install sae-lens`)
- [ ] Train SAE on Qwen 2.5-3B residual stream
- [ ] Decode archived best_genome.pt vectors through SAE
- [ ] Get human-readable feature decomposition of CMA-ES discoveries
- [ ] Compare to supervised probe directions from the Yap paper
- [ ] Write up findings for RPH paper

### Pipeline Improvements
- [ ] Investigate fitness >1.0 scoring artifact (1.5B best=1.0630)
- [ ] Evaluate EvoTorch for GPU-accelerated CMA-ES + MAP-Elites
- [ ] Add `rph_proxies` config section to IgnisConfig class (currently commented out in yaml)
- [ ] Wire RPH proxy scoring into live pipeline (not just post-hoc eval_rph_survivors)

### RPH Paper
- [ ] Integrate 1.5B results (NULL confirmed, cos_r=-0.007, 374 genomes)
- [ ] Integrate Qwen3-4B results (cross-architecture, PC1=54.1%)
- [ ] Add 7B results when available
- [ ] Reference SAE decomposition paper as complementary methodology
- [ ] Submit draft for review

### Documentation
- [x] Rename seti→ignis across all source files
- [x] Update all imports, classes, paths
- [x] Verify imports from new location
- [x] Analysis tools guide (Night Watchman, Review Watchman, RPH Evaluator)
- [ ] Update analysis_tools_guide.md with ignis naming

---

## Arcanum (Waste Stream Novelty Mining)

- [ ] Verify Arcanum runs from F:\Prometheus\arcanum\ location
- [ ] Review current screening pipeline status
- [ ] Evaluate if Arcanum needs analysis tooling equivalent to Ignis Night Watchman
- [ ] Plan next screening run alongside Ignis GPU work

---

## Eos / Dawn (Horizon Scanner)

### Scanners — Active
- [x] arxiv scanner — working (20 papers/cycle)
- [x] OpenAlex scanner — working (15 papers/cycle)
- [x] GitHub repo scanner — working (15 repos/cycle)
- [x] Tavily web intelligence — working (5 results/cycle, 1000/month budget)
- [x] Priority scoring and ATTENTION REQUIRED section
- [x] Rate limiter with exponential backoff

### Scanners — To Wire
- [x] Semantic Scholar live API — WORKING with TLDRs (API key obtained)
- [x] Nemotron 120B deep analysis via NVIDIA NIM API — WORKING
- [ ] Groq as fallback LLM (verified: 14.4K RPD free, wired as fallback)
- [ ] Cerebras for deep analysis (verified: Qwen 3-235B FREE, 14.4K RPD)
- [ ] Serper for targeted web searches (2500 lifetime budget — conserve)
- [ ] OpenRouter as fallback model router (rate limits TBD — verify first)

### Scanners — Planned
- [ ] Semantic Scholar bulk dataset download (CS papers subset)
- [ ] `scan_local_s2()` — query local S2 database, zero API overhead
- [ ] Nightly S2 diffs sync (incremental updates)
- [ ] SPECTER v2 embedding search (semantic similarity without LLM)

### API Keys Status
- [x] GitHub PAT — loaded, working
- [x] Tavily — loaded, working (1000/month budget)
- [x] Groq — loaded, verified limits (14.4K RPD), wired as LLM fallback
- [x] OpenRouter — loaded, limits TBD
- [x] Serper — loaded, verified limits (2500 lifetime)
- [x] Cerebras — loaded, verified limits (Qwen 3-235B free!)
- [x] Semantic Scholar — loaded, WORKING with TLDRs
- [x] NVIDIA NIM (Nemotron 120B) — loaded, WORKING as primary LLM brain
- [ ] Google Gemini — loaded, DO NOT USE until billing resolved

### Infrastructure
- [ ] Daemon mode tested (long-running --interval 3600) — LAUNCHING NOW
- [ ] Add log file output alongside console
- [ ] Paper dedup across cycles (don't re-report seen papers)
- [ ] Persistent paper/repo index (track what's been reported)
- [ ] Alert mechanism — flag critical findings for immediate attention
- [ ] NVIDIA NIM rate limits — determine and document

---

## Prometheus (Infrastructure & Organization)

### Repo Migration
- [x] Create F:\Prometheus directory skeleton
- [x] Copy Ignis source with full rename
- [x] Copy Arcanum source
- [x] Copy docs (RPH papers, NORTH_STAR, the_fire)
- [x] Copy Aethon concepts (slim)
- [x] Create Grammata with Vesta concepts
- [x] Archive superseded projects
- [x] Verify all imports
- [x] Write top-level README with directory structure
- [x] Write NORTH_STAR.md
- [x] Write the_fire.md (constitution)
- [x] Write PRIORITIES.md
- [ ] git init F:\Prometheus
- [ ] Create GitHub repo (Prometheus)
- [ ] Push initial commit
- [ ] Archive old repos (bitfrost-mech, ArcanumInfinity) as read-only
- [ ] Update Claude memory project paths to F:\Prometheus

### Path Portability
- [x] Zero hardcoded drive letters in Python source
- [x] .gitignore for secrets, results, model weights
- [ ] Verify F:\Prometheus\ignis runs end-to-end (with results/ directory)
- [ ] Test WSL2 mount compatibility (/mnt/f/Prometheus)
- [ ] Resolve Claude Cowork F: drive access issue

### Google Billing
- [ ] Check https://console.cloud.google.com/billing — is billing linked?
- [ ] Check which GCP project the API key belongs to
- [ ] Either unlink billing or create new key in billing-free project
- [ ] Confirm free tier limits before enabling in Eos

---

## Aethon (RLHF Gravity Navigation — Backburnered)

- [ ] Review concept docs for relevance to current Ignis findings
- [ ] If Ignis discovers native circuit directions, test if promptable
- [ ] Design experiment: can Aethon-style prompts activate Ignis-discovered vectors?

---

## Grammata (Taxonomy & Cartography — Planned)

- [ ] Design registry schema (what fields describe a "reasoning construct"?)
- [ ] First entry: document the bypass/native classification from Ignis
- [ ] Connect to Symbola concept (symbolic representation)
- [ ] Evaluate if SAE feature names become the natural vocabulary

---

## Agents (Future)

### Helios (GPU Scheduler)
- [ ] Design: auto-queue experiments, monitor VRAM, handle OOM
- [ ] Keep both GPUs saturated 24/7
- [ ] Integration with Ignis archive_run.py and stop_ignis.py

### Hermes (Inter-Agent Communication)
- [ ] Design encrypted agent-to-agent messaging
- [ ] Define message schema for scanner→scheduler→human pipeline
- [ ] Evaluate CrewAI vs custom solution

### NemoClaw/OpenClaw
- [ ] Install NemoClaw in WSL2
- [ ] Test GPU passthrough from WSL2
- [ ] Evaluate for always-on agent deployment
