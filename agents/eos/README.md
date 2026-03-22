# Eos — The Dawn Scanner

> *Eos, goddess of the dawn, who sees the new day first.*

Eos is Prometheus's horizon scanner — a daemon that continuously monitors the
frontier of AI research, open-source tools, and free API resources. She watches
the primordial soup and reports what's emerging.

## What Eos Does

1. **Meta-searches for free tokens and API access** — discovers and tracks free
   tiers, trial periods, open-source model endpoints, and low-cost API access
   across the ecosystem (GitHub Models, OpenRouter, Groq, HuggingFace, etc.)

2. **Monitors the research frontier** — scans arxiv, Semantic Scholar, and
   GitHub for new papers, repos, and tools in our domains (mechanistic
   interpretability, steering vectors, evolutionary algorithms, autonomous agents)

3. **Tracks the open-source landscape** — watches for new model releases,
   framework updates, toolkit announcements that could accelerate Prometheus

4. **Maintains a living database** — API resources, rate limits, token budgets,
   and cost-per-query for every service, updated continuously

5. **Reports digests** — writes daily/weekly summaries to `reports/` with
   actionable intelligence. Only surfaces what deserves human attention.

## Architecture

```
Eos (daemon)
├── Heartbeat loop (configurable interval)
│   ├── scan_apis()        — Check known free-tier APIs, discover new ones
│   ├── scan_arxiv()       — New papers in target categories
│   ├── scan_github()      — Trending repos, new releases in target topics
│   ├── scan_news()        — AI announcements via Tavily or similar
│   ├── update_registry()  — Refresh rate limits, token budgets, costs
│   └── write_digest()     — Summarize findings, flag what matters
├── Rate limit engine
│   ├── Per-source request budgets
│   ├── 429/rate-limit backoff with jitter
│   ├── Request caching and deduplication
│   └── Budget tracking (daily/hourly quotas)
└── Data stores
    ├── api_registry.json      — Known APIs, free tiers, limits, status
    ├── paper_index.json       — Tracked papers with relevance scores
    ├── repo_index.json        — Tracked repos with last-checked dates
    └── reports/YYYY-MM-DD.md  — Daily digest
```

## Running

```powershell
cd F:\Prometheus\agents\eos
python src/eos_daemon.py

# Single scan (no loop)
python src/eos_daemon.py --once

# Custom interval (default: 1 hour)
python src/eos_daemon.py --interval 3600
```

## Configuration

`configs/eos_config.yaml` — API keys, search terms, scan intervals, report preferences.

API keys should be set via environment variables or a `.env` file (never committed):
- `GITHUB_TOKEN` — GitHub PAT for API access
- `TAVILY_API_KEY` — Tavily search API (if available)
- Additional keys discovered by Eos herself get added to the registry

## Design Principles (The Dawn Constitution)

- **Frugal by default** — cache aggressively, batch requests, respect rate limits
- **75% Rule** — never exceed 75% of any API's stated rate limit. Banging on
  the door causes progressive time bans. We calibrate, we respect, we conserve.
  A 429 is a warning. A second 429 means we miscalculated. A third means we stop
  and reassess.
- **Know before you knock** — before using any API, research and document its
  rate limits, free tier caps, and billing triggers. Never discover limits by
  hitting them. This is law, not guidance.
- **Autonomous** — James cannot be pulled into every decision
- **Resilient** — 429 errors are expected, not exceptional. Exponential backoff
  with jitter. Never retry at the same rate that triggered the limit.
- **Discoverable** — Eos's first mission is to find more resources for herself
- **Portable** — no hardcoded drive letters, runs from any location
- **Report what matters** — every item scored by relevance. ATTENTION REQUIRED
  section at the top. James reads the top 10 and skips the rest unless curious.

Also known as **Dawn**.

## Roadmap

- [ ] Wire Groq for LLM-powered paper summarization (verified: 14.4K RPD free)
- [ ] Wire Cerebras for deep analysis (verified: Qwen 3-235B FREE, 14.4K RPD)
- [ ] Wire Semantic Scholar live API (awaiting API key)
- [ ] Download S2 bulk CS papers dataset → local JSON/SQLite index
- [ ] Add `scan_local_s2()` — query local S2 database with zero API overhead
- [ ] Add nightly S2 diffs sync (incremental updates like git pull for literature)
- [ ] Add SPECTER v2 embedding search (semantic similarity, no LLM needed)
- [ ] Wire Serper for targeted web searches (2500 lifetime budget — conserve)
- [ ] Wire OpenRouter as fallback model router (rate limits TBD)
- [ ] Add relevance scoring v2: boost papers citing our prior work or using our tools
