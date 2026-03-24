# Skopos — North Star Alignment

> *Skopos (σκοπός) — "one who watches, one who aims." The lookout who*
> *tells you not just what's on the horizon, but whether it matters.*

Skopos is Prometheus's relevance filter. Where Aletheia catalogs everything,
Skopos scores it against what we're actually trying to learn.

## What Skopos Does

1. **Reads Aletheia's knowledge graph** — recently extracted entities (techniques, tools, terms, claims, motifs)
2. **Scores each entity against active research threads** — 0-5 relevance via LLM
3. **Writes an alignment report** — which threads are getting fed, which are starving
4. **Generates Titan Council prompts** — structured prompts for frontier models when high-relevance findings appear

## Pipeline Position

```
Eos → Aletheia → SKOPOS (assess) → Metis → Clymene → Hermes → AUDIT → SKOPOS (generate) → Publish
```

Skopos runs twice:
- **ASSESS** (after Aletheia): scores new entities
- **GENERATE** (after Audit): creates Titan prompts if high-relevance entities found

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
