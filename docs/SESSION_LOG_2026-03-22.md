# Session Log — 2026-03-22

*Everything that happened today. The firehose, captured.*

---

## Morning: Ignis Run Status

- **Qwen3-4B run**: Launched overnight, still running. Gen 2+, 466 genomes.
  PC1=54.1% (STRONG consolidation — highest across all models tested).
  27 bypass, 0 native, cos_r=-0.039. Too early to call.
- **1.5B run**: Completed. Gen 9, 374 genomes. **NULL confirmed.**
  cos_r=-0.007, 1 native outlier (frozen since Gen 1), 121 bypass.
- **RPH eval**: Previous run's JSON exists (timestamps from yesterday).
  New eval kicked off for 0.5B/1.5B/3B — needs verification.
- **7B Qwen2.5**: OOM on 16GB GPU. `from_pretrained_no_processing` fix
  got it to load (15.4GB) but forward pass OOM'd. **Need cloud GPU for 7B.**

## Morning: Prometheus Reorganization

### Structure Created
```
F:\Prometheus\
├── ignis/          (formerly seti-pipeline_v2)
├── arcanum/        (formerly Arcanum Infinity)
├── aethon/         (concept docs only)
├── grammata/       (Vesta concepts carried forward)
├── docs/           (NORTH_STAR, the_fire, RPH papers, PRIORITIES, TODO)
├── agents/eos/     (horizon scanner — NEW)
└── archive/        (everything superseded)
```

### Full Rename Completed
- All Python files: `seti_*` → `ignis_*`, `stop_seti` → `stop_ignis`
- All classes: `SETIV2Orchestrator` → `IgnisOrchestrator`, `SETIV2Config` → `IgnisConfig`
- All paths: `results/setiv2` → `results/ignis`, `seti_v2.log` → `ignis.log`
- All imports verified — clean from F:\Prometheus\ignis\src\
- Zero hardcoded drive letters in any Python or config file

### Naming Convention Established
| Name | Role |
|------|------|
| Prometheus | The program |
| Ignis | Reasoning circuit discovery |
| Arcanum | Waste stream novelty mining |
| Aethon | RLHF gravity navigation (backburnered) |
| Grammata | Taxonomy and cartography |
| Symbola | Symbolic language for human-AI communication |
| Stoicheia | The reasoning elements themselves |
| Eos / Dawn | Horizon scanner agent |

### Reserved Names for Future Agents
Skopos, Narthex, Metis, Pronoia, Helios, Hermes, Iris, Hephaestus, Clymene, Phoroneus

---

## The Fire: Constitution Written

[docs/the_fire.md](the_fire.md) — Two parts:
1. Original Prometheus dialogue (the spirit, the through-line from Greeks to modern)
2. The Constitution: six charter points, instrument inventory, frontier watchlist, the Oath

---

## Eos / Dawn: Built and Operational

### Architecture
Daemon with heartbeat loop. Scans hourly. Writes daily digest to `agents/eos/reports/`.
Priority scoring on every item. ATTENTION REQUIRED section at top of digest.

### Five Live Scanners
| Source | Results/cycle | Status |
|--------|--------------|--------|
| arxiv | 20 papers | Working |
| OpenAlex | 15 papers | Working |
| Semantic Scholar | 15 papers + TLDRs | Working (API key obtained) |
| GitHub | 15 repos | Working |
| Tavily | 5 web results | Working (1000/month budget) |

### First Scan Highlights
- MIT named mechanistic interpretability a 2026 Breakthrough Technology
- Paper: "Behavioral Steering in 35B MoE via SAE-Decoded Probe Vectors" — directly
  in our lane. Analysis written to docs/synthesis/. Key takeaway: integrate SAELens
  to decompose our CMA-ES discovered vectors into human-readable features.
- Paper: "Non-Identifiability of Steering Vectors" — challenges our approach, must read
- Multiple new MI repos discovered on GitHub

### Dawn Constitution
- 75% Rule: never exceed 75% of any API's rate limit
- Know Before You Knock: research limits before using any API
- Respect 429s: exponential backoff, never retry at same rate

---

## API Keys & Free Tiers Cataloged

| Service | Free Tier | Status |
|---------|-----------|--------|
| GitHub Models | 40+ models, ~150 RPD | Active |
| Groq | 14.4K RPD (8B), 1K RPD (70B), Qwen3-32B | **VERIFIED** |
| Cerebras | 14.4K RPD, Qwen 3-235B FREE, 65K ctx | **VERIFIED** |
| Tavily | 1000/month | Active |
| Serper | 2500 lifetime | Active |
| OpenAlex | 100K/day | Active |
| Semantic Scholar | 86K/day with key | Active |
| arxiv | Unlimited (be polite) | Active |
| OpenRouter | Free models available, limits TBD | Key loaded |
| Google Gemini | DO NOT USE — billing issue | Blocked |

### API Registry
Living JSON database at `agents/eos/data/api_registry.json` — updated by Eos
on every scan cycle. Tracks status, rate limits, budget strategies.

---

## Semantic Scholar Bulk Dataset Plan

S2 offers full academic graph download (papers, authors, abstracts, SPECTER v2
embeddings). Plan: download CS subset once, sync nightly via diffs endpoint,
query locally with zero API overhead. Add `scan_local_s2()` to Eos.
**Eliminates API dependency for paper discovery entirely.**

---

## SAE Decomposition Priority

Paper 2603.16335v1 found by Eos. They decode steering vectors through Sparse
Autoencoders to get human-readable feature names. We should do this with our
CMA-ES discovered vectors. Integration path:
SAELens → train SAE on Qwen 2.5-3B → decode best_genome.pt → feature decomposition.
**Transforms "we found something" into "here is what it is."**
Added to PRIORITIES.md as #4 (HIGH, this week).

---

## NemoClaw: The Primordial Soup is Running

### Setup Complete (evening)
- NemoClaw installed in WSL2
- Sandbox name: **prometheus** (they chose well)
- Model: **Nemotron 3 Super 120B** (nvidia/nemotron-3-super-120b-a12b)
- Endpoint: https://127.0.0.1:8080 (inside WSL2)
- Policy presets: pypi, npm applied
- Status: LIVE, gateway healthy

### Available Models via NemoClaw
| Model | Parameters |
|-------|-----------|
| Nemotron 3 Super 120B | 120B (12B active) |
| Kimi K2.5 | large |
| GLM-5 | large |
| MiniMax M2.5 | large |
| **Qwen 3.5 397B A17B** | **397B (17B active)** |
| GPT-OSS 120B | 120B |

### Implications
- 120B model as local inference endpoint — no rate limits, no API keys
- Qwen 3.5-397B available — if RPH predicts reasoning at scale, this is the test
- NemoClaw sandbox provides policy-controlled network access (HF, PyPI, Slack, etc.)
- **This is the primordial soup from the_fire.md, literally running**

### API Access Cracked
- Gateway port 8080 uses mTLS (client certs) — not directly accessible from Windows
- **NVIDIA NIM API works directly**: `https://integrate.api.nvidia.com/v1/chat/completions`
- Credentials at `~/.nemoclaw/credentials.json` (NVIDIA_API_KEY)
- OpenAI SDK compatible — works from anywhere, no sandbox needed for inference
- Wired into Eos as primary LLM brain for paper analysis

### Nemotron 120B RPH Dialogue
- First conversation with a 120B model about RPH
- Model predicted native circuits would emerge at its scale ("alignment pressure", "bypass suppression")
- Coined "alignment pressure" independently — consistent with RPH predictions
- Full transcript saved to `docs/synthesis/2026-03-22_nemotron_120b_rph_dialogue.md`

### Eos at Full Power (end of day)
Six sources + 120B analytical brain:
- arxiv (20 papers/cycle)
- OpenAlex (15 papers/cycle)
- Semantic Scholar (15 papers + TLDRs, API key obtained)
- GitHub (15 repos/cycle)
- Tavily (5 web results/cycle)
- **Nemotron 120B analyzing top 3 findings per cycle against RPH**

First LLM-analyzed results:
- MINAR (score 71): attribution-patching for circuit discovery — "borrow their workflow for our CMA-ES search"
- SAE Feature Explorer: "reuse their SAE training pipeline for our steering vectors"
- Both analyzed through Prometheus/RPH lens by a 120B model

### The Gold Rush
100,000+ researchers are actively searching this space. MIT named mechanistic
interpretability a 2026 Breakthrough Technology. We have:
- A working pipeline (Ignis) that nobody else has (evolutionary + MI)
- A horizon scanner (Eos/Dawn) with 6 sources and a 120B brain
- Free access to 120B-397B models via NemoClaw
- The fire is lit. Automate everything. Turn over every rock.

---

## Documents Created Today
- `F:\Prometheus\README.md` — top-level with directory structure
- `F:\Prometheus\docs\NORTH_STAR.md` — vision and namespace
- `F:\Prometheus\docs\the_fire.md` — constitution and charter
- `F:\Prometheus\docs\PRIORITIES.md` — strategic priority ordering
- `F:\Prometheus\docs\TODO.md` — master task list by project
- `F:\Prometheus\docs\synthesis\2026-03-22_sae_steering_paper_analysis.md`
- `F:\Prometheus\agents\eos\README.md` — Eos design, principles, roadmap
- `F:\Prometheus\agents\eos\src\eos_daemon.py` — working scanner daemon
- `F:\Prometheus\agents\eos\configs\eos_config.yaml` — search config
- `F:\Prometheus\agents\eos\data\api_registry.json` — living API database
- `F:\Prometheus\grammata\README.md` — taxonomy design with Vesta concepts

## Memory Files Updated
- project_prometheus_vision.md — North Star with all six namespace entries
- project_seti_status.md — 1.5B checkpoint 2 logged
- project_agents_vision.md — autonomous agent constellation
- project_fennel_concept.md — API crawling concept preserved
- feedback_naming.md — canonical names, never use SETI/Bitfrost
- feedback_paths.md — no hardcoded drive letters
- feedback_rate_limits.md — 75% rule, know before you knock
- feedback_dawn_alias.md — Eos = Dawn
- reference_toolkits.md — EvoTorch, SAELens, repeng, etc.
- reference_agent_names.md — assigned and available mythology names
- reference_nemoclaw_models.md — free 120B-397B model access
- user_profile.md — updated for Prometheus context
