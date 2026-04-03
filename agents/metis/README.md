# Metis — Cunning Intelligence

> *Metis, Titaness of wisdom and deep thought. Zeus swallowed her whole*
> *to prevent her child from surpassing him. We do the opposite: we*
> *extract intelligence and share it.*

Metis is Prometheus's analysis brain. Where Eos scans the horizon and returns
raw findings, Metis distills them into actionable intelligence.

## Pipeline Position

| Upstream | This Agent | Downstream |
|----------|-----------|------------|
| Skopos | **Metis** — synthesizes executive briefs from all upstream data | Clymene |

**Reads from:** Eos digest, `docs/PRIORITIES.md`, `docs/TODO.md`, `docs/RPH.md`, Aletheia taxonomy summary, Skopos alignment data
**Writes to:** `agents/metis/briefs/YYYY-MM-DD_brief.md`

---

## What Metis Does

1. **Reads Eos's daily digest** — papers, repos, web intelligence
2. **Deep-analyzes the top items** against our research program (Ignis, Arcanum, RPH)
3. **Cross-references with our codebase** — "does this paper's technique apply to
   something we already have?"
4. **Produces a 1-page executive brief** — the 3 things that matter today
5. **Flags pivots** — anything that suggests we should change direction or accelerate

## Output

A daily brief at `agents/metis/briefs/YYYY-MM-DD_brief.md` with three sections:

- **Act on this** — items requiring immediate action (new tool to integrate,
  paper that challenges our approach, free API discovered)
- **Watch this** — items worth monitoring but not urgent
- **For the record** — notable but no action needed

## Architecture

Metis uses Nemotron 120B (or Cerebras Qwen3-235B as fallback) to analyze
findings. She reads multiple context sources and asks the LLM to synthesize.

```
Eos digest (raw findings)
    │
    ├── docs/PRIORITIES.md (current focus areas)
    ├── docs/TODO.md (active task list)
    ├── docs/RPH.md (core hypothesis)
    ├── Aletheia taxonomy summary (knowledge graph state)
    ├── Skopos alignment data (entity scores per thread)
    │
    ▼
Metis (LLM analysis with full project context)
    │
    ▼
Executive brief (1 page, 3 sections: Act / Watch / Record)
```

**LLM cascade:** Nemotron 120B → Cerebras Qwen3-235B → Groq Llama 3.3-70B

## Running

```powershell
cd F:\Prometheus\agents\metis
python src/metis.py                    # Analyze latest Eos digest
python src/metis.py --digest path.md   # Analyze specific digest
```

## Design Principles

- **Compress, don't expand** — Eos produces 50+ items. Metis produces 3-5.
- **Context-aware** — knows our priorities, current runs, RPH status
- **Actionable** — every item in "Act on this" has a concrete next step
- **James-proof** — assumes a 10-second goldfish loop. Lead with the headline.
