# Pronoia — The Forethought Orchestrator

> *Pronoia, Titaness of forethought and foresight. She who thinks*
> *ahead so you don't have to.*

Pronoia is the single entry point for the entire Prometheus agent pipeline.
One command launches a chain of specialized agents that scan the research
frontier, extract structured knowledge, synthesize executive briefs, and
optionally publish everything to GitHub so you can read it on your phone.

**Entry point:** `F:\Prometheus\pronoia.py`

---

## The Pipeline — Step by Step

When you run `python pronoia.py scan`, here is exactly what happens:

### Step 1: Eos scans the horizon

**Agent:** Eos (Dawn Scanner)
**Script:** `agents/eos/src/eos_daemon.py --once`
**Duration:** ~2-5 minutes depending on API response times

Eos queries five data sources in sequence:

| Source | What it searches | Typical yield |
|--------|-----------------|---------------|
| **arXiv** | New papers in cs.AI, cs.LG, cs.CL (mechanistic interp, steering vectors, reasoning) | ~20 papers |
| **OpenAlex** | Academic papers with citation context | ~15 papers |
| **Semantic Scholar** | Papers with TLDRs, citation graphs | ~15 papers |
| **GitHub** | Trending repos in mech-interp, transformers, evolutionary ML | ~15 repos |
| **Tavily** | Web intelligence — blog posts, announcements, releases | ~5 results |

For each finding, Eos:
1. Checks against `data/paper_index.json` — **skips anything already seen** (dedup)
2. Scores relevance to Prometheus research priorities (0.0 - 1.0)
3. Sends top items to **Nemotron 120B** (NVIDIA NIM API) for deep analysis
4. Flags anything scoring above threshold as **ATTENTION REQUIRED**

**Output:** `agents/eos/reports/YYYY-MM-DD.md` — the daily digest
**Persistent state:** `agents/eos/data/paper_index.json` — grows across cycles

**Rate limit discipline:** Eos never exceeds 75% of any API's stated limit.
429 errors trigger exponential backoff with jitter. A third 429 halts that
scanner for the cycle. Keys are loaded from `agents/eos/.env`.

---

### Step 2: Aletheia harvests knowledge

**Agent:** Aletheia (Knowledge Harvester)
**Script:** `agents/aletheia/src/aletheia.py --once`
**Duration:** ~1-3 minutes (LLM extraction calls)

Aletheia reads the papers Eos just indexed and extracts structured entities
via LLM into a persistent SQLite knowledge graph:

| Entity type | What it captures | Example |
|-------------|-----------------|---------|
| **Techniques** | Methods, algorithms, training procedures | "contrastive activation addition" |
| **Reasoning motifs** | Recurring LLM cognitive patterns | "backtracking", "self-correction" |
| **Tools** | Libraries, frameworks, evaluation harnesses | "SAELens", "TransformerLens" |
| **Terms** | Technical vocabulary with definitions | "residual stream", "ghost trap" |
| **Claims** | Empirical/theoretical assertions with evidence levels | "steering vectors compose linearly" |
| **Papers** | Processing status for each Eos paper | processed/unprocessed tracking |
| **Review queue** | Conflicts flagged for human inspection | near-duplicate entity detection |

Aletheia only processes papers it hasn't seen before (tracked in the `papers`
table). Running it twice is safe — it's idempotent.

**Output:** `agents/aletheia/data/knowledge_graph.db` — SQLite database
**Conflict detection:** Flags entities with >85% name similarity but divergent
descriptions for human review.

**LLM cascade:** NVIDIA Nemotron 120B → Cerebras Qwen3-235B → Groq Llama 3.3-70B
(first available key wins).

---

### Step 3: Skopos scores against research threads

**Agent:** Skopos (North Star Alignment — ASSESS stage)
**Script:** `agents/skopos/src/skopos.py --once`
**Duration:** ~1-2 minutes (LLM scoring calls)

Skopos reads Aletheia's knowledge graph and scores every entity against five
active research threads:

| Thread | What it tracks |
|--------|---------------|
| `anti_cot_geometry` | Orthogonality, nullspace, non-CoT reasoning mechanisms |
| `precipitation_signatures` | Scale-dependent emergence, phase transitions in reasoning |
| `tensor_decomposition` | Tucker/CP decomposition of activations, weight structure |
| `sae_features` | Sparse autoencoder feature discovery, monosemantic features |
| `scale_threshold` | Critical scale boundaries, 1.5B→3B→7B transitions |

Each entity gets a score from 0 (irrelevant) to 5 (directly actionable).
Scores persist in `agents/skopos/data/scores.db` (SQLite) across cycles.

**Output:** `agents/skopos/reports/YYYY-MM-DD_alignment.md` — alignment report

---

### Step 4: Metis synthesizes the brief

**Agent:** Metis (Cunning Intelligence)
**Script:** `agents/metis/src/metis.py --digest <path_to_eos_digest>`
**Duration:** ~1-2 minutes (single LLM call with large context)

Metis reads:
- The Eos digest from Step 1
- `docs/PRIORITIES.md` — what we're currently working on
- `docs/TODO.md` — active task list
- `docs/RPH.md` — our core hypothesis (Reasoning Precipitation)
- Aletheia's taxonomy summary — what the knowledge graph already contains
- Skopos alignment data — which entities scored highest against research threads

She feeds all of this into a single LLM prompt and asks: *"Given what we're
working on, what in today's scan actually matters?"*

**Output:** `agents/metis/briefs/YYYY-MM-DD_brief.md` — executive brief with three sections:

| Section | Purpose |
|---------|---------|
| **Act on this** | Items requiring immediate action (new tool, relevant paper, free API) |
| **Watch this** | Worth monitoring but not urgent |
| **For the record** | Notable but no action needed |

Metis compresses ~50+ raw findings into 3-5 actionable items. She is
deliberately opinionated — she knows our priorities and filters ruthlessly.
Skopos alignment scores give her quantitative backing for what to prioritize.

---

### Step 5: Clymene hoards knowledge (if due)

**Agent:** Clymene (Knowledge Hoarder)
**Script:** `agents/clymene/src/clymene.py --once`
**Duration:** ~2-5 minutes (git clones/pulls)
**Frequency:** Every 72 hours (configurable) — skips silently if cooldown hasn't elapsed

Clymene checks a timestamp file (`data/last_run.txt`). If 72+ hours have
passed since her last run, she:

1. Pulls updates for all repos in the vault (SAELens, TransformerLens, etc.)
2. Clones any new repos added to the manifest
3. Downloads any new high-priority model weights
4. Writes a hoard report to `agents/clymene/reports/YYYY-MM-DD_hoard.md`
5. Updates the timestamp

If the cooldown hasn't elapsed, she prints how long until the next run
and moves on. No API keys needed — just git and disk space.

**Output:** `agents/clymene/reports/YYYY-MM-DD_hoard.md` — what was cloned/updated/failed

---

### Step 6: Hermes delivers the digest

**Agent:** Hermes (The Messenger)
**Script:** `agents/hermes/src/hermes.py --once`
**Duration:** ~5 seconds

Hermes collects today's outputs from all agents and compiles a unified digest:

| Order | Source | What |
|-------|--------|------|
| 1 | Metis brief | Executive summary (Act/Watch/Record) |
| 2 | Aletheia stats | Knowledge graph entity counts |
| 3 | Clymene report | New clones, updates, failures (if run) |
| 4 | Eos digest | Raw findings (truncated to 3000 chars) |

The digest is:
- Saved locally to `agents/hermes/digests/YYYY-MM-DD_digest.md`
- Emailed to you via Gmail SMTP (if configured)

If Metis's brief contains "Act on this" items, the email subject is
prefixed with `[ACTION]` so you can spot it in your inbox.

**Setup:** See [agents/hermes/README.md](../hermes/README.md) for Gmail app
password configuration.

---

### Step 7: Audit — Pipeline health check

**Function:** `run_audit()` (built into Pronoia, not a separate agent)
**Duration:** ~1 second
**Runs:** Every cycle, automatically

The audit inspects captured logs from every agent that ran during the cycle
and checks for:

| Check | Severity | What it catches |
|-------|----------|----------------|
| **Rate limits** | HIGH | 429 errors, backoff warnings, "too many requests" |
| **API errors** | MEDIUM | Connection failures, timeouts, HTTP errors |
| **Zero output** | LOW | Agent produced <20 chars — search terms too narrow or all items processed |
| **Knowledge growth** | INFO | Aletheia entity counts — flat growth means scanner needs tuning |
| **VRAM state** | LOW | GPU memory >1GB after pipeline — something didn't clean up |

Overall status: **HEALTHY** (no issues) / **DEGRADED** (medium findings) / **UNHEALTHY** (rate limits hit)

**Output:** `agents/pronoia/logs/audit_YYYY-MM-DD_HHMMSS.md`

---

### Step 8: Skopos generates Titan Council prompt (conditional)

**Agent:** Skopos (North Star Alignment — GENERATE stage)
**Script:** `agents/skopos/src/skopos.py --generate-prompt`
**Duration:** ~1-2 minutes
**Triggered by:** Any entity scoring 4+ in the ASSESS stage

If the ASSESS stage found high-relevance entities, Skopos synthesizes a
Titan Council prompt — a structured document designed to be fed to frontier
models (ChatGPT, Gemini, DeepSeek, Grok, Claude) under the Phalanx strategy.

The prompt includes the high-scoring findings, their research thread context,
and interlocking constraints that force the Titans to commit positions rather
than hedge.

**Output:** `docs/titan_prompts/auto_YYYY-MM-DD.md`

If no entities scored 4+, this step is skipped silently.

---

### Step 9: Publish to GitHub (optional)

**Triggered by:** `--publish` flag
**Duration:** ~5 seconds

If `--publish` is set, Pronoia stages and pushes the following files:

| File/directory | Content |
|---------------|---------|
| `agents/eos/reports/*.md` | Eos daily digests |
| `agents/aletheia/data/*` | Knowledge graph DB |
| `agents/metis/briefs/*.md` | Metis executive briefs |
| `agents/skopos/reports/*.md` | Skopos alignment reports |
| `agents/clymene/reports/*.md` | Clymene hoard reports |
| `agents/hermes/digests/*.md` | Hermes compiled digests |
| `agents/pronoia/logs/*.md` | Pipeline audit logs |
| `docs/titan_prompts/*.md` | Auto-generated Titan Council prompts |
| `docs/RESULTS.md` | Consolidated experimental results |
| `docs/TODO.md` | Current task list |
| `agents/eos/data/paper_index.json` | Paper dedup index |

Commit message: `pronoia: auto-publish reports YYYY-MM-DD HH:MM`

This lets you read briefs on your phone via the GitHub app while away
from the workstation.

---

## Data Flow Diagram

```
                    ┌─────────────────────────────────────────┐
                    │              PRONOIA                     │
                    │   (orchestrator — pronoia.py)            │
                    │   Captures all agent stdout/stderr       │
                    └──────────────┬──────────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────────┐
                    │         STEP 1: EOS (Dawn)               │
                    │   arXiv + OpenAlex + S2 + GitHub + Tavily│
                    │   → Nemotron 120B deep analysis          │
                    │   → dedup against paper_index.json       │
                    │                                          │
                    │   OUTPUT: reports/YYYY-MM-DD.md           │
                    └──────────────┬──────────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────────┐
                    │       STEP 2: ALETHEIA (Truth)            │
                    │   Reads new papers from Eos index        │
                    │   → LLM extracts 7 entity types          │
                    │   → Merges into SQLite knowledge graph   │
                    │   → Flags conflicts for review           │
                    │                                          │
                    │   OUTPUT: data/knowledge_graph.db         │
                    └──────────────┬──────────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────────┐
                    │     STEP 3: SKOPOS ASSESS (Watcher)      │
                    │   Reads knowledge graph entities          │
                    │   → Scores against 5 research threads    │
                    │   → Persists scores in SQLite             │
                    │                                          │
                    │   OUTPUT: reports/YYYY-MM-DD_alignment.md │
                    │   + data/scores.db                        │
                    └──────────────┬──────────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────────┐
                    │       STEP 4: METIS (Cunning)            │
                    │   Reads Eos digest + Aletheia taxonomy   │
                    │   + Skopos alignment + PRIORITIES + RPH  │
                    │   → LLM synthesizes executive brief      │
                    │                                          │
                    │   OUTPUT: briefs/YYYY-MM-DD_brief.md     │
                    └──────────────┬──────────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────────┐
                    │   STEP 5: CLYMENE (if cooldown met)      │
                    │   git pull/clone repos + models           │
                    │   Runs every 72h, skips otherwise         │
                    │                                          │
                    │   OUTPUT: reports/YYYY-MM-DD_hoard.md     │
                    └──────────────┬──────────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────────┐
                    │       STEP 6: HERMES (Messenger)         │
                    │   Collects all agent outputs              │
                    │   → Compiles unified digest               │
                    │   → Emails via Gmail (if configured)      │
                    │                                          │
                    │   OUTPUT: digests/YYYY-MM-DD_digest.md    │
                    │   + email to your inbox                   │
                    └──────────────┬──────────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────────┐
                    │       STEP 7: AUDIT (Pronoia)            │
                    │   Scans captured logs for:               │
                    │   → 429s, API errors, zero output        │
                    │   → Knowledge growth trends              │
                    │   → VRAM leaks (nvidia-smi)              │
                    │                                          │
                    │   OUTPUT: logs/audit_TIMESTAMP.md         │
                    │   STATUS: HEALTHY / DEGRADED / UNHEALTHY │
                    └──────────────┬──────────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────────┐
                    │  STEP 8: SKOPOS GENERATE (if score ≥ 4)  │
                    │   High-relevance findings detected        │
                    │   → Synthesizes Titan Council prompt      │
                    │   → Phalanx-ready for 5 frontier models   │
                    │                                          │
                    │   OUTPUT: docs/titan_prompts/auto_DATE.md │
                    └──────────────┬──────────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────────┐
                    │     STEP 9: PUBLISH (if --publish)       │
                    │   git add → git commit → git push        │
                    │   Read on phone via GitHub app            │
                    └─────────────────────────────────────────┘
```

---

## Commands

| Command | What it does |
|---------|-------------|
| `scan` | Full pipeline: Eos → Aletheia → Skopos → Metis → Clymene → Hermes → Audit → (Generate) → (Publish) |
| `eos` | Eos scan only (Step 1) |
| `metis` | Metis analysis only (uses latest existing digest) |
| `status` | Show what files have been produced today |
| `review` | Run review_watchman on latest Ignis experimental data |

## Flags

| Flag | Applies to | Effect |
|------|-----------|--------|
| `--every N` | `scan` | Repeat every N hours (0 = once, default) |
| `--publish` | `scan` | Auto-commit+push reports to GitHub after each cycle |

---

## Usage Examples

```powershell
cd F:\Prometheus

# === Single scan cycle (most common) ===
python pronoia.py scan

# === Continuous mode: scan every 2 hours, push to GitHub ===
python pronoia.py scan --every 2 --publish

# === Scan every 30 minutes, no publish ===
python pronoia.py scan --every 0.5

# === Just re-run Metis on the latest Eos digest ===
python pronoia.py metis

# === Check what exists ===
python pronoia.py status

# === Review latest Ignis watchman digest ===
python pronoia.py review

# === Easter egg ===
python pronoia.py scan --every -1
```

---

## File Locations

| What | Path (relative to Prometheus root) |
|------|-----------------------------------|
| Pronoia entry point | `pronoia.py` |
| Eos daemon | `agents/eos/src/eos_daemon.py` |
| Eos config | `agents/eos/configs/eos_config.yaml` |
| Eos reports | `agents/eos/reports/YYYY-MM-DD.md` |
| Eos paper index | `agents/eos/data/paper_index.json` |
| Eos API keys | `agents/eos/.env` (shared, never committed) |
| Aletheia script | `agents/aletheia/src/aletheia.py` |
| Aletheia knowledge graph | `agents/aletheia/data/knowledge_graph.db` |
| Aletheia exports | `agents/aletheia/exports/` |
| Metis script | `agents/metis/src/metis.py` |
| Metis briefs | `agents/metis/briefs/YYYY-MM-DD_brief.md` |
| Clymene script | `agents/clymene/src/clymene.py` |
| Clymene hoard reports | `agents/clymene/reports/YYYY-MM-DD_hoard.md` |
| Clymene cooldown timestamp | `agents/clymene/data/last_run.txt` |
| Clymene manifest | `agents/clymene/configs/manifest.yaml` |
| Skopos script | `agents/skopos/src/skopos.py` |
| Skopos alignment reports | `agents/skopos/reports/YYYY-MM-DD_alignment.md` |
| Skopos scores database | `agents/skopos/data/scores.db` |
| Hermes script | `agents/hermes/src/hermes.py` |
| Hermes digests | `agents/hermes/digests/YYYY-MM-DD_digest.md` |
| Hermes config (credentials) | `agents/hermes/config.json` (gitignored) |
| Audit logs | `agents/pronoia/logs/audit_TIMESTAMP.md` |
| Titan Council prompts | `docs/titan_prompts/auto_YYYY-MM-DD.md` |
| Ignis review watchman | `ignis/src/review_watchman.py` |
| Ignis results | `ignis/src/results/ignis/` |

---

## Sibling Agents (Not in the scan pipeline)

These agents are part of Prometheus but are invoked separately, not through Pronoia's `scan` command:

| Agent | Role | How to run |
|-------|------|-----------|
| **Ignis** | Reasoning circuit discovery via CMA-ES + TransformerLens | `python ignis/src/main.py --config configs/marathon.yaml` |
| **Arcanum** | Waste-stream novelty mining (xenolinguistic screening) | `python arcanum/run.py` |

---

## The Gating Model

What's autonomous vs. what needs a human:

| Level | Examples |
|-------|---------|
| **Fully autonomous** | Scanning, dedup, entity extraction, brief generation, publishing |
| **Prepared but gated** | Experiment queuing, findings staged for human review |
| **Human decides** | Which experiment to run, what results mean, direction changes |

Pronoia serves the coffee. You drink it.

---

## API Keys & Rate Limits

All agents share keys from `agents/eos/.env`. Current active APIs:

| API | Used by | Free tier |
|-----|---------|-----------|
| GitHub PAT | Eos (repo scanning) | 5,000 req/hr |
| NVIDIA NIM (Nemotron 120B) | Eos, Aletheia, Metis | TBD — document limits |
| Semantic Scholar | Eos | 100 req/5min (with key) |
| Tavily | Eos | 1,000/month |
| Cerebras (Qwen3-235B) | Aletheia, Metis (fallback) | 14,400 req/day |
| Groq (Llama 3.3-70B) | Aletheia, Metis (fallback) | 14,400 req/day |
| Serper | Reserved | 2,500 lifetime — conserve |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Eos not found" | Make sure you're running from `F:\Prometheus` (or wherever the repo lives) |
| No digest produced | Check Eos console output for API errors. Usually a key issue or rate limit. |
| Metis brief empty | Metis needs an Eos digest to exist. Run `scan` not `metis` alone on first use. |
| Publish fails | Check `git status` — unrelated unstaged changes can block the commit. |
| Aletheia skips all papers | All papers already processed. Only new Eos discoveries get extracted. |
