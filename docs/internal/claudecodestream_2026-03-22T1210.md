# Claude Code Stream — 2026-03-22 Session Handoff

*Handoff document for resuming from F:\Prometheus working directory.*
*Previous working directory: F:\bitfrost-mech*

---

## CRITICAL: DO NOT KILL THESE PROCESSES

These are still running from the OLD location (`F:\bitfrost-mech`):

1. **RPH eval** (`eval_rph_survivors.py --device cpu --models 0.5B 1.5B 3B`)
   - Running from: `F:\bitfrost-mech\bitfrost-mech\seti-pipeline_v2\src\`
   - Writing results to: `F:\bitfrost-mech\bitfrost-mech\seti-pipeline_v2\results\rph_eval_*.json`
   - Status: Processing 3B model (last and largest). Should finish within ~20 min.
   - When done: copy the JSON to `F:\Prometheus\ignis\src\results\`

2. **Eos daemon** (hourly horizon scanner)
   - Running from: `F:\Prometheus\agents\eos\` (already in new location)
   - Writing to: `F:\Prometheus\agents\eos\reports\2026-03-22.md`
   - Status: Scanning hourly with arxiv + OpenAlex + Semantic Scholar + GitHub + Tavily + Nemotron 120B analysis
   - Leave running. Terminal must stay open.

3. **NemoClaw sandbox** (WSL2, optional)
   - Nemotron 120B accessible via direct API regardless of sandbox state
   - Can close WSL2 session without affecting Eos or Metis

---

## WHAT HAPPENED TODAY (the full session)

### Morning: Ignis Science
- Qwen3-4B overnight run checked: **NULL confirmed** (545 genomes, 0 native, 49 bypass, cos_r=-0.061, PC1=54.1%)
- 1.5B run already archived (NULL, 374 genomes, cos_r=-0.007)
- 7B Qwen2.5 **OOM on 16GB GPU** — needs cloud A100 ($25-40)
- Qwen3-4B has strongest PC1 consolidation (54.1%) but deepest bypass (cos_r=-0.061)
- Run archived. RPH eval kicked off for 0.5B/1.5B/3B.

### Scale Gradient (all NULL so far)
| Model | Arch | N | Best | cos_r | PC1 | Verdict |
|-------|------|---|------|-------|-----|---------|
| 0.5B | Qwen 2.5 | 225 | 0.7754 | -0.032 | 41.1% | NULL |
| 1.5B | Qwen 2.5 | 374 | 1.0630 | -0.007 | 46.6% | NULL |
| 3B | Qwen 2.5 | 421 | 0.6941 | +0.037 | 44.1% | NULL |
| 4B | Qwen 3 | 545 | 1.1521 | -0.061 | 54.1% | NULL |

### Prometheus Reorganization (COMPLETE)
- `F:\Prometheus\` created with full directory structure
- All Python files renamed: `seti_*` → `ignis_*`, classes updated
- All imports verified working from new location
- README, NORTH_STAR, the_fire (constitution), PRIORITIES, TODO all written
- Archive of superseded work (seti-v1, mech, vesta, fennel, aethon scripts)

### Naming Convention
| Name | Role |
|------|------|
| Prometheus | The program |
| Ignis | Reasoning circuit discovery (formerly SETI v2) |
| Arcanum | Waste stream novelty mining |
| Aethon | RLHF gravity navigation (backburnered) |
| Grammata | Taxonomy and cartography |
| Symbola | Symbolic language for human-AI communication |
| Stoicheia | The reasoning elements themselves |
| Eos (aka Dawn) | Horizon scanner agent |
| Metis | Analysis brain — distills Eos findings into briefs |

### Eos Built and Operational
- **6 sources**: arxiv, OpenAlex, Semantic Scholar, GitHub, Tavily
- **Nemotron 120B** analyzing top 3 findings per cycle
- **Priority scoring** (0-100) on every item
- **ATTENTION REQUIRED** section at top of digest
- Running as daemon (hourly scans)
- Dawn Constitution: 75% rule, know before you knock

### Metis Built and Operational
- Reads Eos digest + project context (PRIORITIES, TODO, RPH)
- Produces 1-page executive brief via Nemotron 120B
- Three sections: Act on this / Watch this / For the record
- LLM cascade: NVIDIA → Cerebras → Groq
- First brief generated with 9 actionable items

### NemoClaw Breakthrough
- Nemotron 120B accessible via `https://integrate.api.nvidia.com/v1`
- OpenAI SDK compatible, works from anywhere
- Also available: Qwen 3.5-397B, GPT-OSS-120B, Kimi K2.5, GLM-5
- First RPH dialogue with 120B model — it predicted native circuits at its scale
- Transcript saved: `docs/synthesis/2026-03-22_nemotron_120b_rph_dialogue.md`

### SAE Paper Discovery (from Eos)
- "Behavioral Steering in 35B MoE via SAE-Decoded Probe Vectors" (2603.16335v1)
- SAE decomposition of steering vectors gives human-readable feature names
- Integration path: SAELens → train SAE on Qwen 2.5-3B → decode our best_genome.pt
- Analysis saved: `docs/synthesis/2026-03-22_sae_steering_paper_analysis.md`

### API Keys Established
| Service | Status |
|---------|--------|
| GitHub | Active, working |
| Tavily | Active, working (1000/month) |
| Groq | Verified: 14.4K RPD free |
| Cerebras | Verified: Qwen 3-235B FREE, 14.4K RPD |
| Semantic Scholar | Active, working with TLDRs |
| NVIDIA NIM | Active, Nemotron 120B |
| OpenRouter | Key loaded, limits TBD |
| Serper | Key loaded, 2500 lifetime queries |
| Google Gemini | DO NOT USE — billing issue unresolved |

### GitHub Repo
- **https://github.com/jcraig949jfi/Prometheus**
- 2 commits pushed (initial + Metis)
- Public repo, 976+ files

---

## IMMEDIATE NEXT STEPS (when James returns)

1. **Check RPH eval results** — should be done by now
   ```powershell
   dir F:\bitfrost-mech\bitfrost-mech\seti-pipeline_v2\results\rph_eval_*.json
   ```
   Copy results to: `F:\Prometheus\ignis\src\results\`

2. **Read Metis brief** — `F:\Prometheus\agents\metis\briefs\2026-03-22_brief.md`

3. **Read Eos digest** — `F:\Prometheus\agents\eos\reports\2026-03-22.md`

4. **Decide GPU next step:**
   - Another Ignis run (which model/scale?)
   - Cloud run for 7B Qwen2.5 (complete the scale gradient)
   - SAE training on 3B residual stream (priority #4)

5. **2-hour research queue (papers to read):**
   - "Non-Identifiability of Steering Vectors in LLMs" — challenges our approach
   - "Behavioral Steering in 35B MoE via SAE-Decoded Probe Vectors" (2603.16335v1)
   - MINAR: Mechanistic Interpretability for Neural Algorithmic Reasoning
   - MIT 2026 Breakthrough article on mechanistic interpretability
   - Our own synthesis docs in `docs/synthesis/`

---

## KEY FILE LOCATIONS

| What | Path |
|------|------|
| Top-level README | `F:\Prometheus\README.md` |
| Vision | `F:\Prometheus\docs\NORTH_STAR.md` |
| Constitution | `F:\Prometheus\docs\the_fire.md` |
| Priorities | `F:\Prometheus\docs\PRIORITIES.md` |
| Master TODO | `F:\Prometheus\docs\TODO.md` |
| Session log | `F:\Prometheus\docs\SESSION_LOG_2026-03-22.md` |
| Eos reports | `F:\Prometheus\agents\eos\reports\` |
| Metis briefs | `F:\Prometheus\agents\metis\briefs\` |
| Eos daemon | `F:\Prometheus\agents\eos\src\eos_daemon.py` |
| Metis | `F:\Prometheus\agents\metis\src\metis.py` |
| API keys | `F:\bitfrost-mech\key.txt` (shared, DO NOT commit) |
| API keys (Eos) | `F:\Prometheus\agents\eos\.env` (gitignored) |
| API registry | `F:\Prometheus\agents\eos\data\api_registry.json` |
| Ignis source | `F:\Prometheus\ignis\src\` |
| Arcanum source | `F:\Prometheus\arcanum\src\` |
| Old location | `F:\bitfrost-mech\` (RPH eval still running here) |

---

## CLAUDE MEMORY LOCATION

Memory files persist at: `C:\Users\jcrai\.claude\projects\f--bitfrost-mech\memory\`

**Note:** When VS Code switches to `F:\Prometheus`, Claude may create a new memory
project path. Key memories to carry over:
- `project_prometheus_vision.md` — North Star
- `project_seti_status.md` — scale gradient data
- `feedback_naming.md` — canonical names
- `feedback_paths.md` — no hardcoded drive letters
- `feedback_rate_limits.md` — 75% rule
- `feedback_dawn_alias.md` — Eos = Dawn
- `reference_toolkits.md` — integration targets
- `reference_agent_names.md` — assigned and available names
- `reference_nemoclaw_models.md` — free 120B-397B access

---

*The GPUs don't rest. The agents don't sleep. The fire keeps burning.*
