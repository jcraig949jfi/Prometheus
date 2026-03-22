# Prometheus — Active Priorities

*Living document. Updated as work completes and new priorities emerge.*

---

## IMMEDIATE (do next)

### 1. Qwen3-4B overnight run — monitor and archive
- Run is live on GPU. Check results when complete.
- Archive, then run RPH eval across 0.5B/1.5B/3B + Qwen3-4B
- Review scale gradient with cross-architecture comparison

### 2. Eos — wire remaining APIs
- Serper, Cerebras, OpenRouter need scanners
- Google — hold until free tier confirmed
- Semantic Scholar — James to request API key
- Rate limits documented for every source before use

### 3. 7B Qwen2.5 on cloud
- 16GB GPU can't fit 7B with TransformerLens overhead
- Plan a cloud run (Lambda/RunPod A100, ~$25-40 for 24hrs)
- Required to complete the Qwen 2.5 scale gradient

---

## HIGH PRIORITY (this week)

### 4. SAE decomposition of Ignis-discovered vectors
**Source:** Eos scan — paper 2603.16335v1 (SAE steering in Qwen 3.5-35B)
- Train SAE on Qwen 2.5-3B residual stream using SAELens
- Decode archived best_genome.pt vectors through SAE
- Get human-readable feature decomposition of what CMA-ES discovered
- Compare to supervised probe directions from the paper
- **This transforms "we found something" into "here is what it is"**

### 5. Prometheus repo — git init and GitHub push
- F:\Prometheus structure complete, imports verified
- All renames done (seti→ignis, bitfrost→prometheus)
- Ready for git init when James gives the go-ahead
- Old repos (bitfrost-mech, ArcanumInfinity) become read-only archives

### 6. RPH paper update
- Integrate 1.5B results (NULL confirmed, cos_r=-0.007)
- Add Qwen3-4B cross-architecture comparison when available
- Reference SAE decomposition paper as complementary methodology

---

### 7. Semantic Scholar bulk dataset — local knowledge base
**Source:** S2 Datasets API (api.semanticscholar.org/datasets/v1/)
- Download CS papers subset as local JSON/SQLite database
- Zero rate limits on local queries — unlimited search
- Use diffs endpoint for nightly incremental updates (like git pull for literature)
- SPECTER v2 embeddings included — enables semantic similarity search locally
- Reserve live API only for TLDRs and citation graph lookups
- Add `scan_local_s2()` scanner to Eos — self-sufficient paper discovery
- **This eliminates API dependency for paper scanning entirely**

---

## MEDIUM PRIORITY (this month)

### 8. EvoTorch integration evaluation
- GPU-accelerated CMA-ES + MAP-Elites for quality-diversity search
- Could map the SPACE of circuits, not just find the best one
- Evaluate whether it replaces pycma or supplements it

### 9. GPU Scheduler agent (Helios?)
- Auto-queue experiments when runs complete
- Keep both GPUs saturated 24/7
- Monitor VRAM, handle OOM gracefully

### 10. Qwen2.5-Coder-3B local setup
- Download model, test basic code analysis
- Evaluate for use in Eos (local summarization without API costs)
- Needs second GPU or idle-window scheduling

---

## BACKBURNER (when bandwidth allows)

### 11. Aethon revival
- Use Ignis circuit findings to inform prompt engineering
- Test whether discovered steering directions can be activated via prompting
- Bridges mechanistic findings to deployment

### 12. Grammata — taxonomy bootstrap
- Start naming validated discoveries
- Design the registry schema
- Connect to Symbola (symbolic representation) concept

### 13. NemoClaw/OpenClaw exploration
- Deploy always-on agents in WSL2 sandbox
- Evaluate for Eos-as-a-service deployment
- Low priority until agent constellation matures
