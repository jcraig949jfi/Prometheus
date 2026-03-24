# Implementation Prompt — Three New Pipeline Stages for Pronoia

*Hand this to a Claude Code window. It has everything it needs.*

---

## Context

You are working on the Prometheus research program at `F:\Prometheus`. Prometheus is a mechanistic interpretability research project that probes reasoning circuits inside language models. It has an agent pipeline orchestrated by `pronoia.py` at the project root.

The current pipeline runs: **Eos → Aletheia → Metis → Clymene → Hermes → Publish**

Read `agents/pronoia/README.md` for the full architecture. Read `pronoia.py` for the current implementation. Read `agents/aletheia/src/aletheia.py` and `agents/metis/src/metis.py` to understand the existing agent patterns (logging, LLM calls, pathlib, .env loading from `agents/eos/.env`, graceful fallbacks).

You need to build THREE new stages that slot into this pipeline. The pipeline after your work will be:

```
Eos → Aletheia → ASSESS → Metis → Clymene → Hermes → AUDIT → GENERATE → Publish
```

---

## Stage 1: ASSESS (North Star Alignment Scoring)

**Agent name:** Skopos (σκοπός — "one who aims/watches")
**Location:** `agents/skopos/src/skopos.py`
**When it runs:** After Aletheia, before Metis
**Duration:** ~1-2 minutes (one LLM call)

### What it does

Reads Aletheia's knowledge graph (SQLite at `agents/aletheia/data/knowledge_graph.db`) and scores every entity added in the current cycle against our active research threads.

### Active research threads (hardcode these, they change slowly)

```python
RESEARCH_THREADS = [
    {
        "id": "anti_cot_geometry",
        "name": "Anti-CoT Geometric Pathway",
        "description": "Evolved steering vectors oppose chain-of-thought direction (cos ≈ -0.25). Why does an effective vector point away from reasoning? Is this anti-heuristic suppression?",
        "keywords": ["steering vector", "chain-of-thought", "activation direction", "heuristic suppression", "anti-correlation", "geometric"]
    },
    {
        "id": "precipitation_signatures",
        "name": "Reasoning Precipitation Signatures",
        "description": "One held-out trap (Overtake Race) showed signal at injection layer propagating downstream. Looking for more examples and mechanistic explanation of precipitation vs bypass.",
        "keywords": ["precipitation", "regime shift", "phase transition", "activation patching", "causal mediation", "bypass"]
    },
    {
        "id": "tensor_decomposition",
        "name": "Tensor Methods for Activation Geometry",
        "description": "Using tensor train decomposition (THOR, TensorLy) to map multi-dimensional structure in activation space that PCA collapses. Looking for tools and techniques.",
        "keywords": ["tensor decomposition", "tensor train", "Tucker", "CP decomposition", "high-dimensional", "manifold"]
    },
    {
        "id": "sae_features",
        "name": "SAE Feature Decomposition",
        "description": "Decomposing steering vectors through sparse autoencoders to get human-readable feature descriptions of what CMA-ES discovered.",
        "keywords": ["sparse autoencoder", "SAE", "feature", "interpretable", "decomposition", "monosemantic"]
    },
    {
        "id": "scale_threshold",
        "name": "Scale-Dependent Reasoning Emergence",
        "description": "Models below 4B show zero self-correction. At 4B, 3/8 traps self-correct. Where is the threshold? Is it parameter count, architecture, or training data?",
        "keywords": ["scale", "emergence", "self-correction", "model size", "threshold", "scaling law"]
    }
]
```

### Implementation

1. Query Aletheia's `papers` table for rows where `processed_at` is within the last 24 hours (or since last Skopos run)
2. For each recent paper, query its linked entities from `techniques`, `reasoning_motifs`, `tools`, `terms`, `claims`
3. Send a batch to Nemotron 120B with this prompt structure:

```
You are a research relevance scorer for the Prometheus mechanistic interpretability project.

Our active research threads:
{RESEARCH_THREADS formatted as numbered list with descriptions}

For each paper/entity below, score its relevance to EACH thread on a 0-5 scale:
0 = completely unrelated
1 = tangentially related field
2 = related methodology but different application
3 = directly relevant technique or finding
4 = high-priority — addresses an open question in our research
5 = critical — contradicts, confirms, or extends our specific findings

{entities formatted as list}

Return JSON: {"scores": [{"entity_id": "...", "thread_scores": {"anti_cot_geometry": N, ...}, "rationale": "one sentence"}]}
```

4. Store scores in a new SQLite table `skopos_scores` in the Aletheia database (or a separate `agents/skopos/data/scores.db`)
5. Write a summary to `agents/skopos/reports/YYYY-MM-DD_alignment.md`:
   - Entities scoring 4+ on any thread → "HIGH RELEVANCE" section
   - Thread-level summary: which threads got new relevant material, which are starving
   - Overall: "X new entities, Y relevant to active research, Z high-priority"

### Output consumed by Metis

Metis should load the Skopos alignment summary as additional context (same pattern as how it loads PRIORITIES.md). Add it to `load_project_context()` in metis.py.

### CLI

```
python agents/skopos/src/skopos.py --once          # Score recent entities
python agents/skopos/src/skopos.py --thread anti_cot_geometry  # Score only against one thread
python agents/skopos/src/skopos.py --rescore-all    # Re-score everything (after thread list changes)
```

---

## Stage 2: AUDIT (Pipeline Health Monitor)

**Agent name:** Part of Pronoia itself (not a separate agent — it's a function in `pronoia.py`)
**Location:** Add `run_audit()` function to `pronoia.py`
**When it runs:** After Hermes, before Publish
**Duration:** ~2 seconds (no LLM, just log parsing)

### What it does

Reads the log output from each agent that ran in this cycle and produces a health report. NO LLM calls — pure log parsing and threshold checks.

### Checks to perform

```python
AUDIT_CHECKS = {
    "rate_limits": {
        "description": "Check for 429 errors or rate limit warnings",
        "pattern": r"429|rate.?limit|too many requests|backoff",
        "severity": "HIGH",
        "action": "Reduce scan frequency or add delay"
    },
    "api_errors": {
        "description": "Check for API failures",
        "pattern": r"HTTP Error|ConnectionError|Timeout|failed.*fetch|API.*error",
        "severity": "MEDIUM",
        "action": "Check API key validity and service status"
    },
    "zero_output": {
        "description": "Agent produced no new output",
        "check": "compare output file modification time to cycle start",
        "severity": "LOW",
        "action": "Search terms may be too narrow or all items already processed"
    },
    "knowledge_growth": {
        "description": "Track Aletheia entity counts over time",
        "check": "query COUNT(*) from each entity table, compare to previous cycle",
        "severity": "INFO",
        "action": "Log trend — flat growth means scanner or extractor needs tuning"
    },
    "vram_state": {
        "description": "Check GPU memory after cycle (detect leaks)",
        "check": "nvidia-smi query",
        "severity": "LOW",
        "action": "If VRAM > 1GB after pipeline, something didn't clean up"
    }
}
```

### Implementation

1. After each agent runs in `cmd_scan()`, capture its stdout/stderr (change `subprocess.run()` to capture output)
2. After Hermes completes, call `run_audit(captured_logs)`
3. Parse each agent's output against the check patterns
4. Query Aletheia DB for entity counts (simple SQL COUNT queries)
5. Run `nvidia-smi --query-gpu=memory.used --format=csv,noheader` to check VRAM
6. Write `agents/pronoia/logs/audit_YYYY-MM-DD_HHMMSS.md` with:
   - Per-agent health status (OK / WARN / ERROR)
   - Any 429s or API errors with source
   - Entity growth stats (techniques: +3, motifs: +0, tools: +1, etc.)
   - VRAM state
   - Overall pipeline health: HEALTHY / DEGRADED / UNHEALTHY

7. If any HIGH severity issues found, prepend `[ALERT]` to Hermes email subject

### Integration into pronoia.py

```python
def cmd_scan(every, publish):
    logs = {}

    digest = run_eos(once=True)
    logs["eos"] = last_captured_output

    if digest:
        run_aletheia()
        logs["aletheia"] = last_captured_output

        run_skopos()  # NEW — assess stage
        logs["skopos"] = last_captured_output

        run_metis(digest)
        logs["metis"] = last_captured_output

    run_clymene()
    logs["clymene"] = last_captured_output

    run_hermes()
    logs["hermes"] = last_captured_output

    run_audit(logs)  # NEW — audit stage

    if publish:
        publish_reports()
```

To capture output, change subprocess calls from:
```python
subprocess.run(cmd, cwd=...)
```
to:
```python
result = subprocess.run(cmd, cwd=..., capture_output=True, text=True)
# Still print to console for real-time feedback:
if result.stdout:
    print(result.stdout)
# But also store for audit:
return result.stdout + result.stderr
```

---

## Stage 3: GENERATE (Titan Prompt Generator)

**Agent name:** Part of Skopos (same agent, different command)
**Location:** `agents/skopos/src/skopos.py --generate-prompt`
**When it runs:** After Audit, before Publish (only if high-relevance entities found)
**Duration:** ~1 minute (one LLM call)

### What it does

Takes the highest-scored entities from the ASSESS stage + the latest experimental results, and generates a structured prompt for the Titan Council (Claude, Gemini, ChatGPT, DeepSeek, Grok).

### Implementation

1. Read Skopos scores from this cycle — filter for entities scoring 3+ on any thread
2. Read latest experimental results from `ignis/src/results/ignis/full_analysis/` (most recent JSON files)
3. Read `docs/RESULTS.md` for the current state of knowledge
4. Send to Nemotron 120B:

```
You are a research director for a mechanistic interpretability project studying reasoning circuits in language models.

Current experimental state:
{summary from RESULTS.md, last 2000 chars}

New findings from today's literature scan:
{high-scoring entities with their relevance rationale}

Active research threads:
{RESEARCH_THREADS list}

Generate a structured prompt that we can send to frontier AI models (Claude, GPT, Gemini, DeepSeek, Grok) asking them to:
1. React to the new findings in context of our experimental results
2. Suggest specific experiments we can run on our hardware (17GB VRAM, max 4B models with TransformerLens)
3. Write code for the highest-ROI experiment

The prompt should:
- Include enough context that the receiving model can give specific, actionable advice
- NOT ask for reassurance — ask for critique and concrete next steps
- Reference our actual data (numbers, cosine values, verdicts)
- Be under 3000 words

Return the prompt as markdown.
```

5. Save to `docs/titan_prompts/auto_YYYY-MM-DD.md`
6. If no high-scoring entities this cycle, write a one-liner: "No high-relevance findings this cycle. Titan prompt generation skipped."

### CLI

```
python agents/skopos/src/skopos.py --generate-prompt    # Generate based on latest scores
python agents/skopos/src/skopos.py --generate-prompt --thread anti_cot_geometry  # Focus on one thread
```

---

## Wiring into Pronoia

Update `pronoia.py` to add these stages. The full `cmd_scan` flow becomes:

```python
def cmd_scan(every, publish):
    logs = {}

    digest = run_eos(once=True)
    logs["eos"] = capture_output(...)

    if digest:
        run_aletheia()
        logs["aletheia"] = capture_output(...)

        run_skopos()           # ASSESS — score against research threads
        logs["skopos"] = capture_output(...)

        run_metis(digest)      # Now has Skopos alignment data in context
        logs["metis"] = capture_output(...)

    run_clymene()
    logs["clymene"] = capture_output(...)

    run_hermes()
    logs["hermes"] = capture_output(...)

    audit_result = run_audit(logs)   # AUDIT — pipeline health

    if has_high_relevance_scores():
        run_skopos_generate()        # GENERATE — Titan prompt

    if publish:
        publish_reports()
```

Add to `publish_paths`:
```python
"agents/skopos/reports/",
"agents/pronoia/logs/",
"docs/titan_prompts/",
```

---

## Patterns to Follow

- **Logging:** `logging.basicConfig(level=logging.INFO, format="%(asctime)s [AGENT_NAME] %(message)s")`
- **Paths:** All relative via `pathlib.Path(__file__).resolve().parent.parent`
- **No hardcoded drive letters.** Ever.
- **LLM calls:** Use `agents/eos/.env` for API keys. Cascade: NVIDIA Nemotron → Cerebras → Groq. See `agents/aletheia/src/aletheia.py` for the exact pattern (lines 85-149).
- **Config:** YAML with graceful fallback to defaults if PyYAML missing
- **Error handling:** Log and continue. Never abort the pipeline because one stage failed.
- **Idempotent:** Running twice produces the same result. Don't re-score already-scored entities.

## Directory Structure to Create

```
agents/skopos/
├── README.md
├── configs/
│   └── skopos_config.yaml    # Research threads, score thresholds
├── data/
│   └── scores.db             # SQLite: entity scores per thread
├── reports/
│   └── YYYY-MM-DD_alignment.md
└── src/
    └── skopos.py

agents/pronoia/
└── logs/
    └── audit_YYYY-MM-DD_HHMMSS.md

docs/titan_prompts/
└── auto_YYYY-MM-DD.md
```

## Testing

After building, verify:
1. `python agents/skopos/src/skopos.py --once` — should score recent Aletheia entities
2. `python agents/skopos/src/skopos.py --generate-prompt` — should write a Titan prompt
3. `python pronoia.py scan` — full pipeline should complete with all new stages
4. `python pronoia.py status` — should show Skopos reports and audit logs

## README.md for Skopos

Write a README following the same format as `agents/metis/README.md` — explain what Skopos does, how it fits in the pipeline, CLI usage, and the research thread scoring system.
