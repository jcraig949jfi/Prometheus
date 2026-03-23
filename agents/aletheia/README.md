# Aletheia — Knowledge Harvesting & Taxonomy Agent

> *Aletheia* (ἀλήθεια): Ancient Greek for "truth" or "disclosure" — the unconcealment of what is.

Aletheia is the structured memory of the Prometheus research program. It reads papers discovered by **Eos** (the horizon scanner), sends them through an LLM extraction pipeline, and accumulates the results in a persistent SQLite knowledge graph. The graph captures seven entity types — techniques, reasoning motifs, tools, terms, claims, papers, and review flags — queryable at any time.

**Eos is the eyes. Metis is the analyst. Aletheia is the long-term memory.**

---

## Architecture

```
Eos (scanner)
  └── paper_index.json
        │
        ▼
Aletheia (this agent)
  ├── Reads unprocessed papers from Eos index
  ├── Sends each paper to LLM for structured extraction
  ├── Merges extracted entities into SQLite knowledge graph
  ├── Flags conflicts for human review
  └── Exposes graph to Metis via generate_taxonomy_summary()
        │
        ▼
Metis (analyst) — injects taxonomy context into briefs
        │
        ▼
Grammata (future) — navigable UI for Aletheia's graph
```

---

## Object Model

Aletheia tracks seven entity types:

### 1. `techniques`
Methods, algorithms, and training procedures used in or proposed by papers.

| Field | Description |
|---|---|
| `name` | Canonical name (e.g. "chain-of-thought prompting") |
| `description` | One-paragraph explanation |
| `aliases` | JSON list of alternative names |
| `tags` | JSON list of topic tags |
| `source_papers` | JSON list of Eos paper IDs that cite this |
| `related_techniques` | JSON list of related technique IDs |
| `occurrence_count` | How many papers mention this |

### 2. `reasoning_motifs`
Recurring reasoning patterns or cognitive strategies observed in LLMs.

| Field | Description |
|---|---|
| `name` | Pattern name (e.g. "backtracking", "self-correction") |
| `description` | What the motif looks like in practice |
| `examples` | JSON list of concrete textual examples |
| `occurrence_count` | Frequency across the corpus |
| `source_papers` | Papers that demonstrate this motif |

### 3. `tools`
Software libraries, frameworks, and evaluation harnesses.

| Field | Description |
|---|---|
| `name` | Tool name (e.g. "TransformerLens") |
| `repo_url` | GitHub/PyPI URL |
| `description` | What it does |
| `use_case` | Primary use case |
| `compatible_models` | JSON list of model families it targets |
| `tags` | Topic tags |

### 4. `terms`
Technical vocabulary — definitions that are non-obvious or field-specific.

| Field | Description |
|---|---|
| `term` | The term (e.g. "residual stream") |
| `definition` | Concise definition |
| `field` | Sub-field (e.g. "mechanistic interpretability") |
| `synonyms` | Alternative names |
| `first_seen_paper` | Eos paper ID where first encountered |

### 5. `claims`
Empirical or theoretical assertions made by papers, with epistemic metadata.

| Field | Description |
|---|---|
| `assertion` | The claim in plain language |
| `evidence_level` | `weak` / `moderate` / `strong` |
| `falsification_criteria` | What would prove the claim wrong |
| `status` | `open` / `supported` / `falsified` / `contested` |
| `source_paper` | Eos paper ID |

### 6. `papers`
A local mirror of the Eos paper index, extended with processing metadata.

| Field | Description |
|---|---|
| `id` | Same key as Eos `paper_index.json` |
| `processed` | Boolean — has Aletheia extracted from this paper? |
| `processed_at` | Timestamp |
| `extraction_notes` | Any notes from the extraction run |

### 7. `review_queue`
Items flagged for human inspection — usually definition conflicts or near-duplicate entities.

| Field | Description |
|---|---|
| `entity_type` | Which table the item lives in |
| `entity_id` | Row ID in that table |
| `reason` | Why it was flagged |
| `resolved` | Boolean |

---

## CLI Reference

```bash
# Process all unprocessed Eos papers (up to batch_size per run)
python agents/aletheia/src/aletheia.py --once

# Print the current taxonomy summary as Markdown
python agents/aletheia/src/aletheia.py --summary

# Search for entities by keyword
python agents/aletheia/src/aletheia.py --query techniques "chain of thought"
python agents/aletheia/src/aletheia.py --query terms "residual stream"
python agents/aletheia/src/aletheia.py --query motifs "backtracking"
python agents/aletheia/src/aletheia.py --query tools "TransformerLens"
python agents/aletheia/src/aletheia.py --query claims "scaling"

# Export the full knowledge graph as JSON
python agents/aletheia/src/aletheia.py --export

# Show pending review queue items
python agents/aletheia/src/aletheia.py --review

# Resolve (dismiss) a review queue item by ID
python agents/aletheia/src/aletheia.py --resolve 42

# Use a custom config file
python agents/aletheia/src/aletheia.py --once --config /path/to/config.yaml
```

All commands must be run from the **Prometheus repo root** (or anywhere — paths are resolved relative to `aletheia.py`'s location).

---

## Integration: Eos

Aletheia reads `agents/eos/data/paper_index.json` directly. Each entry in that file has a unique key (derived from title + author + year). Aletheia tracks which keys it has already processed in the `papers` table, so re-running `--once` is safe and idempotent — it will only pick up new papers.

Papers with a score below `min_score_threshold` (default: 0.3) are skipped. Eos assigns scores based on relevance to Prometheus research priorities.

**API keys** are loaded from `agents/eos/.env` — Aletheia shares the same key file (NVIDIA, Cerebras, Groq).

---

## Integration: Metis

Metis can call `agent.generate_taxonomy_summary()` to get a Markdown block listing:
- Entity counts by type
- Top 10 techniques by occurrence
- Top 10 terms
- Recent claims
- Pending review queue size

This context can be injected into Metis's analysis prompt to ground its recommendations in the accumulated knowledge graph rather than only the latest digest.

**Future**: once Metis is wired to Aletheia, it will automatically flag papers that introduce techniques already in the graph (as confirmatory evidence) versus papers that challenge existing claims (as contested evidence).

---

## Review Queue Workflow

When Aletheia detects a potential conflict during merging, it adds an item to the `review_queue` table. Conflicts are triggered when:

- A new entity has a name similarity ≥ 85% (configurable) to an existing entity *but* the description diverges significantly (< 40% similarity). This catches cases like "DPO" vs "Direct Preference Optimization" being processed separately with different descriptions.
- A term's definition is substantially different from a previously stored definition (same threshold).

To handle flagged items:
1. `python aletheia.py --review` — lists all unresolved items
2. Inspect the entity: `python aletheia.py --query techniques "the name"`
3. Manually edit the DB if needed (SQLite — any SQLite browser works)
4. `python aletheia.py --resolve <id>` — marks item resolved

---

## First Run

```bash
# 1. Ensure Eos has populated its index
python agents/eos/src/eos.py --once   # or check agents/eos/data/paper_index.json

# 2. Run Aletheia — processes up to 10 papers per run
python agents/aletheia/src/aletheia.py --once

# 3. Check the summary
python agents/aletheia/src/aletheia.py --summary

# 4. Export for inspection
python agents/aletheia/src/aletheia.py --export
# Output: agents/aletheia/exports/aletheia_export_YYYYMMDD_HHMMSS.json
```

The SQLite database is created automatically at `agents/aletheia/data/knowledge_graph.db` on first run.

No extra Python packages are required — only the standard library (sqlite3, json, re, urllib). `PyYAML` is used to read the config if available, but falls back gracefully to defaults if not installed.

---

## Configuration

`configs/aletheia_config.yaml`:

```yaml
processing:
  batch_size: 10                # papers per --once run
  min_score_threshold: 0.3      # skip papers below this Eos relevance score
  conflict_similarity_threshold: 0.85  # trigram Jaccard threshold for dedup flagging

logging:
  level: INFO
  log_file: "agents/aletheia/aletheia.log"
```

LLM provider order: **NVIDIA Nemotron → Cerebras Qwen3-235B → Groq Llama 3.3-70B**. The first provider with a valid API key in the environment is used. Aletheia uses low temperature (0.1) for deterministic extraction.

---

## Future: Grammata

Grammata will be the navigable, human-facing interface to Aletheia's knowledge graph — a browsable hypertext of techniques, terms, and claims with cross-links between entities and source papers. Aletheia is designed with Grammata in mind: the `--export` JSON output and the `query()` API are the primary integration points.

---

## Agent Lineage

| Agent | Role | Feeds |
|---|---|---|
| Eos | Horizon scanner — finds papers | → Aletheia |
| Aletheia | Knowledge harvester — extracts entities | → Metis, Grammata |
| Metis | Analyst — synthesizes briefs | → Human |
| Grammata | Navigator — browsable graph UI | → Human |

---

*"Truth is not a property of propositions but an event of unconcealment."*
