# Skopos — North Star Alignment

> *Skopos (σκοπός) — "one who watches, one who aims." The lookout who*
> *tells you not just what's on the horizon, but whether it matters.*

Skopos is Prometheus's relevance filter. Where Aletheia catalogs everything,
Skopos scores it against what we're actually trying to learn.

## Pipeline Position

| Upstream | This Agent | Downstream |
|----------|-----------|------------|
| Aletheia | **Skopos** — scores entities against research threads | Metis |

**Reads from:** `agents/aletheia/data/knowledge_graph.db`
**Writes to:** `agents/skopos/data/scores.db`, `agents/skopos/reports/YYYY-MM-DD_alignment.md`, `docs/titan_prompts/auto_YYYY-MM-DD.md`

---

## What Skopos Does

1. **Reads Aletheia's knowledge graph** — recently extracted entities (techniques, tools, terms, claims, motifs)
2. **Scores each entity against active research threads** — 0 (irrelevant) to 5 (directly actionable) via LLM
3. **Writes an alignment report** — which threads are getting fed, which are starving
4. **Generates Titan Council prompts** — structured prompts for frontier models when high-relevance findings appear

## Dual Stages

Skopos runs **twice** in each pipeline cycle:

```
Eos → Aletheia → SKOPOS ASSESS → Metis → Clymene → Hermes → Audit → SKOPOS GENERATE → Publish
```

### Stage 1: ASSESS (after Aletheia, before Metis)

- Reads all unscored entities from `knowledge_graph.db`
- Sends each entity + research thread description to the LLM
- Returns a score from 0 to 5:

| Score | Meaning |
|-------|---------|
| 0 | Irrelevant to this thread |
| 1 | Tangentially related |
| 2 | Related but not actionable |
| 3 | Useful context — worth noting |
| 4 | Directly relevant — triggers GENERATE stage |
| 5 | Critical finding — immediate action recommended |

- Scores persist in `agents/skopos/data/scores.db` (SQLite) across cycles
- The alignment report summarizes per-thread coverage and highlights gaps

### Stage 2: GENERATE (after audit, before publish)

- Triggered only if any entity scored **4 or higher** in the ASSESS stage
- Synthesizes a Titan Council prompt: a structured document designed for frontier models (ChatGPT, Gemini, DeepSeek, Grok, Claude) under the Phalanx strategy
- The prompt includes high-scoring findings, research thread context, and interlocking constraints that force the Titans to commit positions rather than hedge
- Output: `docs/titan_prompts/auto_YYYY-MM-DD.md`
- If no entities scored 4+, this stage is skipped silently

## Integration with Metis

Skopos alignment data is loaded by Metis as context for executive brief synthesis. This gives Metis quantitative backing for prioritization decisions — entities that score high against active threads get promoted to "Act on this" in the brief.

## Research Threads

| Thread ID | Name | Question |
|-----------|------|----------|
| `anti_cot_geometry` | Anti-CoT Geometric Pathway | Why do effective steering vectors oppose CoT direction? |
| `precipitation_signatures` | Reasoning Precipitation Signatures | When does reasoning precipitate vs bypass? |
| `tensor_decomposition` | Tensor Methods for Activation Geometry | Can tensor decomposition reveal structure PCA misses? |
| `sae_features` | SAE Feature Decomposition | What human-readable features did CMA-ES discover? |
| `scale_threshold` | Scale-Dependent Reasoning Emergence | Where is the self-correction threshold? |

## Output

- **Alignment reports**: `reports/YYYY-MM-DD_alignment.md`
- **Titan prompts**: `docs/titan_prompts/auto_YYYY-MM-DD.md`
- **Scores database**: `data/scores.db` (SQLite)

## Running

```bash
python agents/skopos/src/skopos.py --once                        # Score recent entities
python agents/skopos/src/skopos.py --thread anti_cot_geometry     # Score against one thread
python agents/skopos/src/skopos.py --rescore-all                  # Re-score everything
python agents/skopos/src/skopos.py --generate-prompt              # Generate Titan prompt
python agents/skopos/src/skopos.py --generate-prompt --thread sae_features  # Focused prompt
```

## Design Principles

- **No false urgency** — a score of 0 is fine. Most entities won't matter to us.
- **Idempotent** — running twice doesn't re-score already-scored entities (unless `--rescore-all`)
- **Thread-aware** — each score is per-thread, so we can track which questions are getting answers
- **Feeds Metis** — alignment reports are loaded as context for Metis's executive briefs
