"""
Skopos — North Star Alignment Scorer & Titan Prompt Generator

Scores Aletheia knowledge graph entities against active research threads,
and optionally generates structured prompts for the Titan Council.

Usage:
    python skopos.py --once                              # Score recent entities
    python skopos.py --thread anti_cot_geometry           # Score against one thread
    python skopos.py --rescore-all                        # Re-score everything
    python skopos.py --generate-prompt                    # Generate Titan Council prompt
    python skopos.py --generate-prompt --thread <id>      # Focus on one thread
"""

import argparse
import json
import logging
import os
import re
import sqlite3
import ssl
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SKOPOS_ROOT = Path(__file__).resolve().parent.parent
AGENTS_ROOT = SKOPOS_ROOT.parent
PROMETHEUS_ROOT = AGENTS_ROOT.parent

ALETHEIA_DB = AGENTS_ROOT / "aletheia" / "data" / "knowledge_graph.db"
SCORES_DB = SKOPOS_ROOT / "data" / "scores.db"
REPORTS_DIR = SKOPOS_ROOT / "reports"
TITAN_PROMPTS_DIR = PROMETHEUS_ROOT / "docs" / "titan_prompts"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SKOPOS] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("skopos")

# Load .env from eos (shared API keys)
_env_file = AGENTS_ROOT / "eos" / ".env"
if _env_file.exists():
    for line in _env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

# ---------------------------------------------------------------------------
# Research Threads
# ---------------------------------------------------------------------------

RESEARCH_THREADS = [
    {
        "id": "ejection_mechanism",
        "name": "Ejection Mechanism Characterization",
        "description": "Language models compute correct answers internally then suppress them at late layers. Pretraining-induced, not RLHF. Operates via v_proj (attention) at small scale, gate_proj (MLP) at large scale. Redundant distributed suppression at 1.5B across L19-L26 with per-layer specialization.",
        "keywords": ["ejection", "suppression", "logit lens", "monotonicity", "v_proj", "gate_proj", "MLP", "attention head", "epistemic suppressor", "pretraining"],
    },
    {
        "id": "evolution_steering",
        "name": "CMA-ES Evolution & LoRA Perturbation",
        "description": "Evolving steering vectors and LoRA weight perturbations to suppress ejection. SR 92% at 135M/360M, 63% at 1.5B. Phase transitions confirmed. Order of operations: corpus first, evolution second. v_proj dual-use problem.",
        "keywords": ["CMA-ES", "LoRA", "evolution", "steering vector", "phase transition", "fitness function", "RLVF", "corpus-first", "metacognition emergence"],
    },
    {
        "id": "reasoning_evaluation",
        "name": "Automated Reasoning Evaluation (Forge + Sphinx)",
        "description": "239 genuine reasoning tools forged by Hephaestus, improved by CAITL to 74% median unseen accuracy. Sphinx taxonomy: 105 reasoning failure categories across 14 domains. Tier A (parsing) vs Tier B (judgment/metacognition). Apollo evolves these tools via open-ended evolution.",
        "keywords": ["reasoning tool", "forge", "Sphinx", "trap battery", "NCD", "calibration", "metacognition", "Goodhart", "adversarial", "CAITL", "Apollo"],
    },
    {
        "id": "knowledge_substrate",
        "name": "Knowledge Substrate & Ontology",
        "description": "Building the living knowledge base that reasoning operates ON. Aletheia knowledge graph, Arcanum waste stream mining, Grammata human-AI bridge. Gap-type classification. Evidence grades. The substrate is the product.",
        "keywords": ["knowledge graph", "substrate", "ontology", "Arcanum", "Xenolexicon", "waste stream", "gap detection", "evidence grade", "taxonomy", "Grammata"],
    },
    {
        "id": "scale_universality",
        "name": "Scale Transfer & Cross-Architecture Universality",
        "description": "Does the ejection mechanism exist in all architectures (Qwen, Llama, Gemma) and at all scales (135M to 7B+)? Layer sweep at 1.5B shows ejection spans L19-L26. 7B needs cloud GPU. SAE decomposition for mechanistic understanding.",
        "keywords": ["scale", "universality", "cross-architecture", "Llama", "Gemma", "Qwen", "SAE", "sparse autoencoder", "7B", "13B", "scaling law"],
    },
]

# ---------------------------------------------------------------------------
# Scores Database
# ---------------------------------------------------------------------------

def init_scores_db() -> sqlite3.Connection:
    """Initialize the scores database."""
    SCORES_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(SCORES_DB), timeout=10)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS skopos_scores (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            entity_id   TEXT NOT NULL,
            entity_name TEXT NOT NULL,
            thread_id   TEXT NOT NULL,
            score       INTEGER NOT NULL DEFAULT 0,
            rationale   TEXT,
            scored_at   TEXT NOT NULL,
            UNIQUE(entity_type, entity_id, thread_id)
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_scores_thread
        ON skopos_scores(thread_id, score DESC)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_scores_entity
        ON skopos_scores(entity_type, entity_id)
    """)
    conn.commit()
    return conn


def already_scored(scores_conn: sqlite3.Connection, entity_type: str, entity_id: str) -> bool:
    """Check if an entity has already been scored."""
    row = scores_conn.execute(
        "SELECT 1 FROM skopos_scores WHERE entity_type = ? AND entity_id = ? LIMIT 1",
        (entity_type, entity_id),
    ).fetchone()
    return row is not None


# ---------------------------------------------------------------------------
# Aletheia Reader
# ---------------------------------------------------------------------------

def load_recent_entities(since_hours: int = 24) -> list[dict]:
    """Load entities from Aletheia's knowledge graph added recently."""
    if not ALETHEIA_DB.exists():
        log.warning(f"Aletheia DB not found at {ALETHEIA_DB}")
        return []

    conn = sqlite3.connect(str(ALETHEIA_DB), timeout=10)
    conn.row_factory = sqlite3.Row
    entities = []

    # Get recently processed papers
    rows = conn.execute(
        """SELECT id, title, authors FROM papers
           WHERE processed = 1
           AND processed_at IS NOT NULL
           AND datetime(processed_at) >= datetime('now', ?)""",
        (f"-{since_hours} hours",),
    ).fetchall()

    paper_ids = [r["id"] for r in rows]
    if not paper_ids:
        log.info("No recently processed papers found")
        conn.close()
        return entities

    log.info(f"Found {len(paper_ids)} recently processed papers")

    # Collect entities from each table
    entity_tables = {
        "techniques": "name",
        "reasoning_motifs": "name",
        "tools": "name",
        "terms": "term",
        "claims": "assertion",
    }

    for table, name_col in entity_tables.items():
        try:
            # Get entities linked to recent papers via source_papers JSON
            for row in conn.execute(f"SELECT id, {name_col} as name, description, source_papers FROM {table}").fetchall():
                source = row["source_papers"] or "[]"
                try:
                    sources = json.loads(source)
                except (json.JSONDecodeError, TypeError):
                    sources = []
                if any(pid in sources for pid in paper_ids):
                    entities.append({
                        "type": table,
                        "id": str(row["id"]),
                        "name": row["name"],
                        "description": (row["description"] or "")[:200],
                    })
        except sqlite3.OperationalError as e:
            log.warning(f"Could not query {table}: {e}")

    conn.close()
    log.info(f"Loaded {len(entities)} entities from {len(paper_ids)} papers")
    return entities


def load_all_entities() -> list[dict]:
    """Load ALL entities from Aletheia's knowledge graph (for --rescore-all)."""
    if not ALETHEIA_DB.exists():
        log.warning(f"Aletheia DB not found at {ALETHEIA_DB}")
        return []

    conn = sqlite3.connect(str(ALETHEIA_DB), timeout=10)
    conn.row_factory = sqlite3.Row
    entities = []

    entity_tables = {
        "techniques": "name",
        "reasoning_motifs": "name",
        "tools": "name",
        "terms": "term",
        "claims": "assertion",
    }

    for table, name_col in entity_tables.items():
        try:
            for row in conn.execute(f"SELECT id, {name_col} as name, description FROM {table}").fetchall():
                entities.append({
                    "type": table,
                    "id": str(row["id"]),
                    "name": row["name"],
                    "description": (row["description"] or "")[:200],
                })
        except sqlite3.OperationalError as e:
            log.warning(f"Could not query {table}: {e}")

    conn.close()
    log.info(f"Loaded {len(entities)} total entities")
    return entities


# ---------------------------------------------------------------------------
# LLM Interface
# ---------------------------------------------------------------------------

def _get_ssl_context():
    ctx = ssl.create_default_context()
    try:
        import certifi
        ctx.load_verify_locations(certifi.where())
    except ImportError:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    return ctx


def call_llm(prompt: str, system: str = "", max_tokens: int = 4000, temperature: float = 0.2) -> str:
    """Call the best available LLM. Tries NVIDIA -> Cerebras -> Groq."""
    providers = [
        {
            "name": "NVIDIA Nemotron",
            "endpoint": os.environ.get("NVIDIA_API_ENDPOINT", "https://integrate.api.nvidia.com/v1"),
            "key": os.environ.get("NVIDIA_API_KEY"),
            "model": os.environ.get("NVIDIA_MODEL", "nvidia/nemotron-3-super-120b-a12b"),
        },
        {
            "name": "Cerebras Qwen3-235B",
            "endpoint": "https://api.cerebras.ai/v1",
            "key": os.environ.get("CEREBRAS_API_KEY"),
            "model": "qwen-3-235b-a22b-instruct-2507",
        },
        {
            "name": "Groq Llama 3.3-70B",
            "endpoint": "https://api.groq.com/openai/v1",
            "key": os.environ.get("GROQ_API_KEY"),
            "model": "llama-3.3-70b-versatile",
        },
    ]

    ctx = _get_ssl_context()

    for provider in providers:
        if not provider["key"]:
            continue

        log.info(f"Calling {provider['name']}...")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = json.dumps({
            "model": provider["model"],
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                f"{provider['endpoint']}/chat/completions",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {provider['key']}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            choices = data.get("choices", [])
            if choices:
                msg = choices[0].get("message", {})
                text = msg.get("content") or msg.get("reasoning_content") or ""
                if text.strip():
                    log.info(f"Got {len(text)} chars from {provider['name']}")
                    return text.strip()

        except Exception as e:
            log.warning(f"{provider['name']} failed: {e}")
            continue

    return ""


# ---------------------------------------------------------------------------
# ASSESS — Score entities against research threads
# ---------------------------------------------------------------------------

def format_threads_for_prompt(thread_filter: str | None = None) -> str:
    """Format research threads as a numbered list for the LLM prompt."""
    threads = RESEARCH_THREADS
    if thread_filter:
        threads = [t for t in RESEARCH_THREADS if t["id"] == thread_filter]

    lines = []
    for i, t in enumerate(threads, 1):
        lines.append(f"{i}. **{t['name']}** (id: {t['id']})")
        lines.append(f"   {t['description']}")
        lines.append(f"   Keywords: {', '.join(t['keywords'])}")
        lines.append("")
    return "\n".join(lines)


def score_entities(entities: list[dict], thread_filter: str | None = None) -> list[dict]:
    """Score entities against research threads using LLM."""
    if not entities:
        log.info("No entities to score")
        return []

    # Build entity list for prompt
    entity_lines = []
    for e in entities:
        desc = f" — {e['description']}" if e["description"] else ""
        entity_lines.append(f"- [{e['type']}:{e['id']}] {e['name']}{desc}")
    entity_text = "\n".join(entity_lines)

    threads_text = format_threads_for_prompt(thread_filter)

    # Determine which thread IDs to expect in response
    if thread_filter:
        thread_ids = [thread_filter]
    else:
        thread_ids = [t["id"] for t in RESEARCH_THREADS]

    thread_ids_str = ", ".join(f'"{tid}"' for tid in thread_ids)

    system = "You are a research relevance scorer for the Prometheus mechanistic interpretability project. Return ONLY valid JSON — no markdown fences, no commentary."

    prompt = f"""Our active research threads:
{threads_text}

For each entity below, score its relevance to EACH thread on a 0-5 scale:
0 = completely unrelated
1 = tangentially related field
2 = related methodology but different application
3 = directly relevant technique or finding
4 = high-priority — addresses an open question in our research
5 = critical — contradicts, confirms, or extends our specific findings

Entities:
{entity_text}

Return JSON: {{"scores": [{{"entity_id": "<type>:<id>", "thread_scores": {{{thread_ids_str}: N}}, "rationale": "one sentence"}}]}}"""

    raw = call_llm(prompt, system=system, max_tokens=4000, temperature=0.1)
    if not raw:
        log.warning("LLM returned empty response for scoring")
        return []

    # Parse JSON from response (strip markdown fences if present)
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    # Detect truncation: incomplete JSON
    stripped = raw.strip()
    if stripped and stripped[-1] not in ('}', ']'):
        log.warning(f"LLM response appears truncated ({len(raw)} chars, ends with '{stripped[-20:]}')")
        # Try to repair: find the last complete score entry
        last_brace = raw.rfind('}')
        if last_brace > 0:
            # Find the scores array and close it properly
            repaired = raw[:last_brace + 1]
            # Close any open arrays/objects
            open_brackets = repaired.count('[') - repaired.count(']')
            open_braces = repaired.count('{') - repaired.count('}')
            repaired += ']' * open_brackets + '}' * open_braces
            log.info(f"Attempting truncation repair ({open_brackets} brackets, {open_braces} braces)")
            raw = repaired

    try:
        result = json.loads(raw)
        scores = result.get("scores", [])

        # Validate: all expected thread_ids present in each score
        validated = []
        for item in scores:
            ts = item.get("thread_scores", {})
            missing = [tid for tid in thread_ids if tid not in ts]
            if missing:
                log.warning(f"Score for {item.get('entity_id', '?')} missing threads: {missing}")
            # Validate score range
            for tid, val in ts.items():
                try:
                    v = int(val)
                    if v < 0 or v > 5:
                        log.warning(f"Score {v} out of range [0-5] for {item.get('entity_id', '?')} thread {tid}")
                        ts[tid] = max(0, min(5, v))
                except (ValueError, TypeError):
                    ts[tid] = 0
            validated.append(item)

        log.info(f"Got scores for {len(validated)} entities ({len(validated)}/{len(entities)} expected)")
        return validated
    except json.JSONDecodeError as e:
        log.warning(f"Failed to parse LLM scoring response: {e}")
        log.info(f"Raw response ({len(raw)} chars): {raw[:1000]}")
        return []


def store_scores(scores_conn: sqlite3.Connection, scores: list[dict], entities: list[dict]) -> int:
    """Store scores in the database. Returns count of new scores stored."""
    now = datetime.now(timezone.utc).isoformat()
    stored = 0

    # Build lookup from entity_id string to entity dict
    entity_lookup = {f"{e['type']}:{e['id']}": e for e in entities}

    for item in scores:
        eid = item.get("entity_id", "")
        thread_scores = item.get("thread_scores", {})
        rationale = item.get("rationale", "")

        entity = entity_lookup.get(eid)
        if not entity:
            continue

        for thread_id, score_val in thread_scores.items():
            try:
                score_int = int(score_val)
            except (ValueError, TypeError):
                continue

            try:
                scores_conn.execute(
                    """INSERT INTO skopos_scores
                       (entity_type, entity_id, entity_name, thread_id, score, rationale, scored_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?)
                       ON CONFLICT(entity_type, entity_id, thread_id)
                       DO UPDATE SET score = ?, rationale = ?, scored_at = ?""",
                    (entity["type"], entity["id"], entity["name"],
                     thread_id, score_int, rationale, now,
                     score_int, rationale, now),
                )
                stored += 1
            except sqlite3.Error as e:
                log.warning(f"Failed to store score for {eid}/{thread_id}: {e}")

    scores_conn.commit()
    log.info(f"Stored {stored} scores")
    return stored


def write_alignment_report(scores_conn: sqlite3.Connection) -> Path:
    """Write an alignment report summarizing today's scores."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    report_path = REPORTS_DIR / f"{today}_alignment.md"

    # High relevance (score >= 4)
    high = scores_conn.execute(
        """SELECT entity_type, entity_name, thread_id, score, rationale
           FROM skopos_scores WHERE score >= 4
           ORDER BY score DESC, thread_id"""
    ).fetchall()

    # Per-thread summary
    thread_stats = {}
    for t in RESEARCH_THREADS:
        row = scores_conn.execute(
            "SELECT COUNT(*), MAX(score), AVG(score) FROM skopos_scores WHERE thread_id = ?",
            (t["id"],),
        ).fetchone()
        thread_stats[t["id"]] = {
            "name": t["name"],
            "count": row[0] or 0,
            "max": row[1] or 0,
            "avg": round(row[2] or 0, 1),
        }

    # Total counts
    total = scores_conn.execute("SELECT COUNT(*) FROM skopos_scores").fetchone()[0]
    relevant = scores_conn.execute("SELECT COUNT(*) FROM skopos_scores WHERE score >= 3").fetchone()[0]
    high_count = len(high)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# Skopos Alignment Report -- {today}",
        f"*Generated: {ts}*",
        "",
        f"**{total} scored entities | {relevant} relevant (3+) | {high_count} high-priority (4+)**",
        "",
    ]

    # High relevance section
    if high:
        lines.append("## HIGH RELEVANCE (score 4+)")
        lines.append("")
        for entity_type, entity_name, thread_id, score, rationale in high:
            lines.append(f"- **[{score}] {entity_name}** ({entity_type}) -> {thread_id}")
            if rationale:
                lines.append(f"  {rationale}")
        lines.append("")

    # Thread summary
    lines.append("## Thread Status")
    lines.append("")
    for tid, stats in thread_stats.items():
        status = "STARVING" if stats["count"] == 0 else (
            "ACTIVE" if stats["max"] >= 3 else "LOW"
        )
        lines.append(f"- **{stats['name']}** [{status}]: {stats['count']} entities, max={stats['max']}, avg={stats['avg']}")
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    log.info(f"Alignment report: {report_path}")
    return report_path


def run_assess(thread_filter: str | None = None, rescore_all: bool = False) -> Path | None:
    """Run the ASSESS stage: score entities against research threads."""
    scores_conn = init_scores_db()

    if rescore_all:
        log.info("Rescoring ALL entities")
        scores_conn.execute("DELETE FROM skopos_scores")
        scores_conn.commit()
        entities = load_all_entities()
    else:
        entities = load_recent_entities(since_hours=24)

    if not rescore_all:
        # Filter out already-scored entities
        unscored = [e for e in entities if not already_scored(scores_conn, e["type"], e["id"])]
        log.info(f"{len(entities)} entities found, {len(unscored)} unscored")
        entities = unscored

    if not entities:
        log.info("No new entities to score")
        report = write_alignment_report(scores_conn)
        scores_conn.close()
        return report

    # Batch entities (max ~30 per LLM call to stay within context)
    batch_size = 30
    all_scores = []
    for i in range(0, len(entities), batch_size):
        batch = entities[i:i + batch_size]
        log.info(f"Scoring batch {i // batch_size + 1} ({len(batch)} entities)")
        batch_scores = score_entities(batch, thread_filter)
        if batch_scores:
            store_scores(scores_conn, batch_scores, batch)
            all_scores.extend(batch_scores)

    report = write_alignment_report(scores_conn)
    scores_conn.close()
    return report


# ---------------------------------------------------------------------------
# GENERATE — Titan Council Prompt
# ---------------------------------------------------------------------------

def has_high_relevance() -> bool:
    """Check if there are any high-relevance scores (4+) from the current cycle."""
    if not SCORES_DB.exists():
        return False
    conn = sqlite3.connect(str(SCORES_DB), timeout=10)
    row = conn.execute("SELECT COUNT(*) FROM skopos_scores WHERE score >= 4").fetchone()
    conn.close()
    return (row[0] or 0) > 0


def run_generate(thread_filter: str | None = None) -> Path | None:
    """Generate a Titan Council prompt from high-scoring entities."""
    TITAN_PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    prompt_path = TITAN_PROMPTS_DIR / f"auto_{today}.md"

    if not SCORES_DB.exists():
        log.warning("No scores database found — run --once first")
        return None

    scores_conn = sqlite3.connect(str(SCORES_DB), timeout=10)

    # Get entities scoring 3+ on any thread
    if thread_filter:
        high_rows = scores_conn.execute(
            """SELECT entity_type, entity_name, thread_id, score, rationale
               FROM skopos_scores WHERE score >= 3 AND thread_id = ?
               ORDER BY score DESC""",
            (thread_filter,),
        ).fetchall()
    else:
        high_rows = scores_conn.execute(
            """SELECT entity_type, entity_name, thread_id, score, rationale
               FROM skopos_scores WHERE score >= 3
               ORDER BY score DESC"""
        ).fetchall()

    scores_conn.close()

    if not high_rows:
        msg = "No high-relevance findings this cycle. Titan prompt generation skipped."
        log.info(msg)
        prompt_path.write_text(f"# Titan Prompt -- {today}\n\n{msg}\n", encoding="utf-8")
        return prompt_path

    # Format high-scoring entities
    entity_lines = []
    for etype, ename, tid, score, rationale in high_rows:
        entity_lines.append(f"- [{score}/5] **{ename}** ({etype}) -> thread: {tid}")
        if rationale:
            entity_lines.append(f"  {rationale}")
    entity_text = "\n".join(entity_lines)

    # Load latest experimental results
    results_text = ""
    results_path = PROMETHEUS_ROOT / "docs" / "RESULTS.md"
    if results_path.exists():
        results_text = results_path.read_text(encoding="utf-8")[-2000:]

    # Format research threads
    threads_text = format_threads_for_prompt(thread_filter)

    system = "You are a research director for a mechanistic interpretability project studying reasoning circuits in language models. Return the prompt as clean markdown."

    prompt = f"""Current experimental state:
{results_text if results_text else "(No RESULTS.md found)"}

New findings from today's literature scan:
{entity_text}

Active research threads:
{threads_text}

Generate a structured prompt that we can send to frontier AI models (Claude, GPT, Gemini, DeepSeek, Grok) asking them to:
1. React to the new findings in context of our experimental results
2. Suggest specific experiments we can run on our hardware (17GB VRAM, max 4B models with TransformerLens)
3. Write code for the highest-ROI experiment

The prompt should:
- Include enough context that the receiving model can give specific, actionable advice
- NOT ask for reassurance — ask for critique and concrete next steps
- Reference our actual data (numbers, cosine values, verdicts)
- Be under 3000 words

Return the prompt as markdown."""

    titan_prompt = call_llm(prompt, system=system, max_tokens=4000, temperature=0.3)

    if not titan_prompt:
        log.warning("LLM returned empty response for prompt generation")
        return None

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    content = (
        f"# Titan Council Prompt -- {today}\n"
        f"*Auto-generated by Skopos: {ts}*\n\n"
        f"---\n\n"
        f"{titan_prompt}\n"
    )

    prompt_path.write_text(content, encoding="utf-8")
    log.info(f"Titan prompt written: {prompt_path}")
    return prompt_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Skopos -- North Star Alignment Scorer")
    parser.add_argument("--once", action="store_true",
                        help="Score recent entities (default action)")
    parser.add_argument("--thread", type=str, default=None,
                        help="Score only against one research thread")
    parser.add_argument("--rescore-all", action="store_true",
                        help="Re-score all entities (use after thread list changes)")
    parser.add_argument("--generate-prompt", action="store_true",
                        help="Generate a Titan Council prompt from high-scoring entities")
    args = parser.parse_args()

    print("=" * 62)
    print("  SKOPOS -- NORTH STAR ALIGNMENT")
    print("  Scoring the horizon against our research threads.")
    print("=" * 62)
    print()

    # Validate thread filter
    if args.thread:
        valid_ids = [t["id"] for t in RESEARCH_THREADS]
        if args.thread not in valid_ids:
            log.error(f"Unknown thread '{args.thread}'. Valid: {', '.join(valid_ids)}")
            sys.exit(1)

    if args.generate_prompt:
        result = run_generate(thread_filter=args.thread)
        if result:
            print(f"\nTitan prompt saved to: {result}")
    else:
        # Default: score recent entities
        result = run_assess(thread_filter=args.thread, rescore_all=args.rescore_all)
        if result:
            print(f"\nAlignment report: {result}")


if __name__ == "__main__":
    main()
