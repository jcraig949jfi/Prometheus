# Metis — Cunning Intelligence

> *Metis, Titaness of wisdom and deep thought. Zeus swallowed her whole*
> *to prevent her child from surpassing him. We do the opposite: we*
> *extract intelligence and share it.*

Metis is Prometheus's analysis brain. Where Eos scans the horizon and returns
raw findings, Metis distills them into actionable intelligence.

## What Metis Does

1. **Reads Eos's daily digest** — papers, repos, web intelligence
2. **Deep-analyzes the top items** against our research program (Ignis, Arcanum, RPH)
3. **Cross-references with our codebase** — "does this paper's technique apply to
   something we already have?"
4. **Produces a 1-page executive brief** — the 3 things that matter today
5. **Flags pivots** — anything that suggests we should change direction or accelerate

## Output

A daily brief at `briefs/YYYY-MM-DD.md` with three sections:

- **Act on this** — items requiring immediate action (new tool to integrate,
  paper that challenges our approach, free API discovered)
- **Watch this** — items worth monitoring but not urgent
- **For the record** — notable but no action needed

## Architecture

Metis uses Nemotron 120B (or Cerebras Qwen3-235B as fallback) to analyze
findings. She reads Eos's digest, loads our project context (PRIORITIES.md,
RPH paper abstract, current run status), and asks the LLM to synthesize.

```
Eos digest (raw findings)
    │
    ▼
Metis (LLM analysis with project context)
    │
    ▼
Executive brief (1 page, 3 sections)
```

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
