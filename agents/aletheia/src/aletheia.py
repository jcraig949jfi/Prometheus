"""
Aletheia — Knowledge Harvesting & Taxonomy Agent

Reads Eos's paper index, extracts structured entities (techniques, tools, terms,
claims, reasoning motifs) via LLM, and stores them in a persistent SQLite
knowledge graph. Designed to feed structured context into Metis and eventually
Grammata (the navigable face of the graph).

Usage:
    python aletheia.py --once              # process all unprocessed Eos papers
    python aletheia.py --normalize         # LLM dedup pass over techniques, motifs, tools
    python aletheia.py --summary           # print taxonomy summary markdown
    python aletheia.py --query techniques "chain of thought"
    python aletheia.py --query terms "residual stream"
    python aletheia.py --export            # export full graph to exports/
    python aletheia.py --review            # show pending review queue items
    python aletheia.py --resolve <id>      # mark a review queue item resolved
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

ALETHEIA_ROOT = Path(__file__).resolve().parent.parent
PROMETHEUS_ROOT = ALETHEIA_ROOT.parent.parent

DB_PATH = ALETHEIA_ROOT / "data" / "knowledge_graph.db"
EXPORTS_DIR = ALETHEIA_ROOT / "exports"
EOS_INDEX_PATH = PROMETHEUS_ROOT / "agents" / "eos" / "data" / "paper_index.json"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

log_file = ALETHEIA_ROOT / "aletheia.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ALETHEIA] %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(log_file), encoding="utf-8"),
    ],
)
log = logging.getLogger("aletheia")

# Load .env from eos (shared API keys)
_env_file = PROMETHEUS_ROOT / "agents" / "eos" / ".env"
if _env_file.exists():
    for line in _env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


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


def call_llm(prompt: str, system: str = "", max_tokens: int = 2048, temperature: float = 0.1) -> str:
    """Call the best available LLM. Tries NVIDIA → Cerebras → Groq."""
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
                    log.info(f"  Got {len(text)} chars from {provider['name']}")
                    return text.strip()

        except Exception as e:
            log.warning(f"  {provider['name']} failed: {e}")
            continue

    return ""


# ---------------------------------------------------------------------------
# Extraction prompt
# ---------------------------------------------------------------------------

EXTRACTION_SYSTEM = """You are Aletheia, a precision knowledge extraction engine for AI research.
Your output must be valid JSON and nothing else — no preamble, no commentary, no markdown fences.

Extract entities from the provided paper metadata. Be concise and accurate.
If a field is unknown or not applicable, use an empty string or empty list.
Only extract entities that are clearly present in or implied by the paper content.

IMPORTANT CANONICALIZATION RULES:
- Use the most widely accepted canonical name for each technique (e.g., always use "Sparse Autoencoder" not "SAE" or "sparse auto-encoder")
- For reasoning motifs, prefer the form used in the mechanistic interpretability literature
- If a technique is a variant or special case of another, note that in the description rather than creating a separate top-level entry
- Common canonicalizations: "chain-of-thought" → "Chain-of-Thought Prompting", "SAE" → "Sparse Autoencoder", "MI" → "Mechanistic Interpretability", "activation patching" stays as "Activation Patching", "circuit analysis/tracing/discovery" → "Circuit Analysis", "RLHF" → "Reinforcement Learning from Human Feedback", "DPO" → "Direct Preference Optimization", "LoRA" → "Low-Rank Adaptation"
- Never use abbreviations alone as a technique name — always expand them
"""

EXTRACTION_PROMPT_TEMPLATE = """Paper metadata:
Title: {title}
URL: {url}
Date: {date}
Abstract/context: {abstract}

Extract all of the following entity types present in this paper and return strict JSON:

{{
  "techniques": [
    {{"name": "...", "description": "...", "aliases": [], "tags": []}}
  ],
  "reasoning_motifs": [
    {{"name": "...", "description": "...", "examples": [], "tags": []}}
  ],
  "tools": [
    {{"name": "...", "repo_url": "...", "description": "...", "use_case": "...", "tags": []}}
  ],
  "terms": [
    {{"term": "...", "definition": "...", "field": "...", "synonyms": []}}
  ],
  "claims": [
    {{"assertion": "...", "evidence_level": "weak|moderate|strong", "falsification_criteria": "...", "status": "open"}}
  ]
}}

Guidelines:
- techniques: Methods, algorithms, training procedures (e.g. "chain-of-thought prompting", "DPO", "steering vectors")
- reasoning_motifs: Recurring reasoning patterns or cognitive strategies observed in LLMs (e.g. "backtracking", "self-correction", "analogy generation")
- tools: Software libraries, frameworks, evaluation harnesses with a repo or package (e.g. "TransformerLens", "SAELens")
- terms: Technical vocabulary and definitions specific to this field (e.g. "residual stream", "superposition", "mechanistic interpretability")
- claims: Empirical or theoretical assertions the paper makes, with evidence level and how they could be falsified
Return only valid JSON. If no entities of a type are found, use an empty list for that key.
"""


def _extract_abstract_hint(paper: dict) -> str:
    """Pull any available abstract or description text from a paper dict."""
    for key in ("abstract", "description", "summary", "snippet", "notes"):
        val = paper.get(key, "")
        if val:
            return str(val)[:1500]
    return "(no abstract available)"


# ---------------------------------------------------------------------------
# Fuzzy name matching + abbreviation expansion
# ---------------------------------------------------------------------------

# Canonical expansions for common abbreviations in AI/MI literature.
# Keys are lowercase stripped forms; values are canonical names.
ABBREV_EXPANSIONS = {
    "sae":  "Sparse Autoencoder",
    "saes": "Sparse Autoencoder",
    "cot":  "Chain-of-Thought Prompting",
    "mi":   "Mechanistic Interpretability",
    "vlm":  "Vision-Language Model",
    "vla":  "Vision-Language-Action Model",
    "llm":  "Large Language Model",
    "rl":   "Reinforcement Learning",
    "rlhf": "Reinforcement Learning from Human Feedback",
    "dpo":  "Direct Preference Optimization",
    "lora": "Low-Rank Adaptation",
    "moe":  "Mixture of Experts",
    "mlp":  "Multi-Layer Perceptron",
    "attn": "Attention",
    "kv":   "Key-Value Cache",
}


def _normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _expand_abbrev(name: str) -> str:
    """If name is a known abbreviation, return its canonical expansion."""
    key = _normalize(name)
    return ABBREV_EXPANSIONS.get(key, name)


def _similarity(a: str, b: str) -> float:
    """Trigram Jaccard similarity on normalized strings."""
    def trigrams(s):
        s = _normalize(s)
        return set(s[i:i+3] for i in range(len(s) - 2)) if len(s) >= 3 else {s}

    t_a = trigrams(a)
    t_b = trigrams(b)
    if not t_a and not t_b:
        return 1.0
    if not t_a or not t_b:
        return 0.0
    return len(t_a & t_b) / len(t_a | t_b)


def _names_match(a: str, b: str) -> bool:
    """True if two entity names should be considered the same entity."""
    # 1. Exact match after normalization
    if _normalize(a) == _normalize(b):
        return True
    # 2. Either expands to the same canonical form
    if _normalize(_expand_abbrev(a)) == _normalize(_expand_abbrev(b)):
        return True
    # 3. One is an abbreviation expansion of the other
    if _normalize(_expand_abbrev(a)) == _normalize(b):
        return True
    if _normalize(a) == _normalize(_expand_abbrev(b)):
        return True
    return False


# ---------------------------------------------------------------------------
# AletheiaAgent
# ---------------------------------------------------------------------------

class AletheiaAgent:
    def __init__(self, config_path: str = None):
        self.db_path = DB_PATH
        self.exports_dir = EXPORTS_DIR
        self.eos_index_path = EOS_INDEX_PATH
        self.batch_size = 10
        self.min_score = 0.3
        self.conflict_threshold = 0.85

        # Load config if provided
        if config_path and Path(config_path).exists():
            self._load_config(config_path)

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.init_db()
        log.info(f"Aletheia initialized. DB: {self.db_path}")

    def _load_config(self, config_path: str):
        try:
            import yaml  # optional
            with open(config_path, encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
            proc = cfg.get("processing", {})
            self.batch_size = proc.get("batch_size", self.batch_size)
            self.min_score = proc.get("min_score_threshold", self.min_score)
            self.conflict_threshold = proc.get("conflict_similarity_threshold", self.conflict_threshold)
        except Exception as e:
            log.warning(f"Config load failed ({e}), using defaults")

    # -----------------------------------------------------------------------
    # DB init
    # -----------------------------------------------------------------------

    def init_db(self):
        cur = self.conn.cursor()

        cur.executescript("""
        CREATE TABLE IF NOT EXISTS papers (
            id              TEXT PRIMARY KEY,
            title           TEXT NOT NULL,
            authors         TEXT,
            url             TEXT,
            score           REAL DEFAULT 0,
            date_added      TEXT,
            processed       INTEGER DEFAULT 0,
            processed_at    TEXT,
            extraction_notes TEXT
        );

        CREATE TABLE IF NOT EXISTS techniques (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            name                TEXT NOT NULL,
            description         TEXT,
            aliases             TEXT DEFAULT '[]',
            tags                TEXT DEFAULT '[]',
            source_papers       TEXT DEFAULT '[]',
            related_techniques  TEXT DEFAULT '[]',
            occurrence_count    INTEGER DEFAULT 1,
            created_at          TEXT,
            updated_at          TEXT
        );

        CREATE TABLE IF NOT EXISTS reasoning_motifs (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            description     TEXT,
            examples        TEXT DEFAULT '[]',
            occurrence_count INTEGER DEFAULT 1,
            source_papers   TEXT DEFAULT '[]',
            tags            TEXT DEFAULT '[]',
            created_at      TEXT,
            updated_at      TEXT
        );

        CREATE TABLE IF NOT EXISTS tools (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            name                TEXT NOT NULL,
            repo_url            TEXT,
            description         TEXT,
            use_case            TEXT,
            compatible_models   TEXT DEFAULT '[]',
            tags                TEXT DEFAULT '[]',
            source_papers       TEXT DEFAULT '[]',
            occurrence_count    INTEGER DEFAULT 1,
            created_at          TEXT,
            updated_at          TEXT
        );

        CREATE TABLE IF NOT EXISTS terms (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            term            TEXT NOT NULL,
            definition      TEXT,
            field           TEXT,
            synonyms        TEXT DEFAULT '[]',
            first_seen_paper TEXT,
            occurrence_count INTEGER DEFAULT 1,
            created_at      TEXT,
            updated_at      TEXT
        );

        CREATE TABLE IF NOT EXISTS claims (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            assertion           TEXT NOT NULL,
            evidence_level      TEXT DEFAULT 'weak',
            falsification_criteria TEXT,
            status              TEXT DEFAULT 'open',
            source_paper        TEXT,
            related_techniques  TEXT DEFAULT '[]',
            created_at          TEXT,
            updated_at          TEXT
        );

        CREATE TABLE IF NOT EXISTS review_queue (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            entity_id   TEXT,
            reason      TEXT,
            flagged_at  TEXT,
            resolved    INTEGER DEFAULT 0
        );
        """)
        self.conn.commit()

    # -----------------------------------------------------------------------
    # Eos index loader
    # -----------------------------------------------------------------------

    def load_eos_index(self) -> list:
        """Return list of paper dicts not yet processed in our DB."""
        if not self.eos_index_path.exists():
            log.warning(f"Eos paper index not found: {self.eos_index_path}")
            return []

        with open(self.eos_index_path, encoding="utf-8") as f:
            index = json.load(f)

        papers_raw = index.get("papers", {})
        results = []

        cur = self.conn.cursor()
        for paper_id, meta in papers_raw.items():
            cur.execute("SELECT processed FROM papers WHERE id = ?", (paper_id,))
            row = cur.fetchone()
            if row and row["processed"]:
                continue  # already done

            score = float(meta.get("score", meta.get("seen_count", 1)) or 0)
            if score < self.min_score:
                continue

            results.append({
                "id": paper_id,
                "title": meta.get("title", paper_id),
                "authors": meta.get("authors", ""),
                "url": (meta.get("source_urls") or [""])[0],
                "score": score,
                "date_added": meta.get("first_seen", ""),
                "abstract": meta.get("abstract", ""),
            })

        log.info(f"Eos index: {len(papers_raw)} total, {len(results)} unprocessed")
        return results

    # -----------------------------------------------------------------------
    # Entity extraction
    # -----------------------------------------------------------------------

    def extract_entities(self, paper: dict) -> dict:
        """Call LLM to extract structured entities from a paper."""
        prompt = EXTRACTION_PROMPT_TEMPLATE.format(
            title=paper.get("title", ""),
            url=paper.get("url", ""),
            date=paper.get("date_added", ""),
            abstract=_extract_abstract_hint(paper),
        )

        raw = call_llm(prompt, system=EXTRACTION_SYSTEM, max_tokens=2048, temperature=0.1)

        if not raw:
            log.warning(f"  No LLM response for: {paper['title'][:60]}")
            return self._fallback_extraction(paper)

        # Strip any accidental markdown fences
        raw = re.sub(r"^```[a-z]*\n?", "", raw.strip(), flags=re.MULTILINE)
        raw = re.sub(r"\n?```$", "", raw.strip(), flags=re.MULTILINE)

        # Find JSON object in response
        json_match = re.search(r"\{[\s\S]+\}", raw)
        if not json_match:
            log.warning(f"  No JSON found in LLM response for: {paper['title'][:60]}")
            return self._fallback_extraction(paper)

        try:
            extracted = json.loads(json_match.group(0))
        except json.JSONDecodeError as e:
            log.warning(f"  JSON parse error for {paper['title'][:60]}: {e}")
            return self._fallback_extraction(paper)

        # Ensure all keys present
        for key in ("techniques", "reasoning_motifs", "tools", "terms", "claims"):
            if key not in extracted or not isinstance(extracted[key], list):
                extracted[key] = []

        total = sum(len(extracted[k]) for k in extracted)
        log.info(f"  Extracted {total} entities from: {paper['title'][:60]}")
        return extracted

    def _fallback_extraction(self, paper: dict) -> dict:
        """Return empty extraction structure when LLM is unavailable."""
        return {"techniques": [], "reasoning_motifs": [], "tools": [], "terms": [], "claims": []}

    # -----------------------------------------------------------------------
    # Entity merging
    # -----------------------------------------------------------------------

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _json_append(self, existing_json: str, value: str) -> str:
        lst = json.loads(existing_json or "[]")
        if value not in lst:
            lst.append(value)
        return json.dumps(lst)

    def _find_similar(self, table: str, name_col: str, name: str) -> sqlite3.Row | None:
        """Find an existing row whose name matches or is highly similar to `name`.

        Match priority:
          1. Exact normalized match or abbreviation expansion match (_names_match)
          2. Trigram Jaccard >= conflict_threshold
        """
        # Expand the incoming name if it's a known abbreviation
        expanded_name = _expand_abbrev(name)

        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {table}")
        rows = cur.fetchall()

        best_score = 0.0
        best_row = None
        for row in rows:
            row_name = row[name_col] or ""
            # Fast path: exact/abbreviation match → treat as perfect similarity
            if _names_match(row_name, name) or _names_match(row_name, expanded_name):
                return row
            # Trigram similarity on both original and expanded forms
            sim = max(
                _similarity(row_name, name),
                _similarity(row_name, expanded_name),
            )
            if sim > best_score:
                best_score = sim
                best_row = row

        if best_score >= self.conflict_threshold:
            return best_row
        return None

    def _merge_technique(self, entity: dict, paper_id: str):
        name = (entity.get("name") or "").strip()
        if not name:
            return
        now = self._now()
        existing = self._find_similar("techniques", "name", name)
        if existing:
            # Update
            new_papers = self._json_append(existing["source_papers"], paper_id)
            new_count = existing["occurrence_count"] + 1
            # Flag if description conflict is significant
            if existing["description"] and entity.get("description") and \
               _similarity(existing["description"], entity["description"]) < 0.4:
                self.flag_for_review("technique", str(existing["id"]),
                    f"Description conflict: existing vs paper {paper_id}")
            self.conn.execute(
                "UPDATE techniques SET source_papers=?, occurrence_count=?, updated_at=? WHERE id=?",
                (new_papers, new_count, now, existing["id"])
            )
        else:
            self.conn.execute(
                """INSERT INTO techniques
                   (name, description, aliases, tags, source_papers, related_techniques, occurrence_count, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, '[]', 1, ?, ?)""",
                (
                    name,
                    entity.get("description", ""),
                    json.dumps(entity.get("aliases", [])),
                    json.dumps(entity.get("tags", [])),
                    json.dumps([paper_id]),
                    now, now,
                )
            )

    def _merge_reasoning_motif(self, entity: dict, paper_id: str):
        name = (entity.get("name") or "").strip()
        if not name:
            return
        now = self._now()
        existing = self._find_similar("reasoning_motifs", "name", name)
        if existing:
            new_papers = self._json_append(existing["source_papers"], paper_id)
            self.conn.execute(
                "UPDATE reasoning_motifs SET source_papers=?, occurrence_count=?, updated_at=? WHERE id=?",
                (new_papers, existing["occurrence_count"] + 1, now, existing["id"])
            )
        else:
            self.conn.execute(
                """INSERT INTO reasoning_motifs
                   (name, description, examples, occurrence_count, source_papers, tags, created_at, updated_at)
                   VALUES (?, ?, ?, 1, ?, ?, ?, ?)""",
                (
                    name,
                    entity.get("description", ""),
                    json.dumps(entity.get("examples", [])),
                    json.dumps([paper_id]),
                    json.dumps(entity.get("tags", [])),
                    now, now,
                )
            )

    def _merge_tool(self, entity: dict, paper_id: str):
        name = (entity.get("name") or "").strip()
        if not name:
            return
        now = self._now()
        existing = self._find_similar("tools", "name", name)
        if existing:
            new_papers = self._json_append(existing["source_papers"], paper_id)
            self.conn.execute(
                "UPDATE tools SET source_papers=?, occurrence_count=?, updated_at=? WHERE id=?",
                (new_papers, existing["occurrence_count"] + 1, now, existing["id"])
            )
        else:
            self.conn.execute(
                """INSERT INTO tools
                   (name, repo_url, description, use_case, compatible_models, tags, source_papers, occurrence_count, created_at, updated_at)
                   VALUES (?, ?, ?, ?, '[]', ?, ?, 1, ?, ?)""",
                (
                    name,
                    entity.get("repo_url", ""),
                    entity.get("description", ""),
                    entity.get("use_case", ""),
                    json.dumps(entity.get("tags", [])),
                    json.dumps([paper_id]),
                    now, now,
                )
            )

    def _merge_term(self, entity: dict, paper_id: str):
        term = (entity.get("term") or "").strip()
        if not term:
            return
        now = self._now()
        existing = self._find_similar("terms", "term", term)
        if existing:
            # Flag definition conflicts
            if existing["definition"] and entity.get("definition") and \
               _similarity(existing["definition"], entity["definition"]) < 0.4:
                self.flag_for_review("term", str(existing["id"]),
                    f"Definition conflict from paper {paper_id}")
            self.conn.execute(
                "UPDATE terms SET occurrence_count=?, updated_at=? WHERE id=?",
                (existing["occurrence_count"] + 1, now, existing["id"])
            )
        else:
            self.conn.execute(
                """INSERT INTO terms
                   (term, definition, field, synonyms, first_seen_paper, occurrence_count, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, 1, ?, ?)""",
                (
                    term,
                    entity.get("definition", ""),
                    entity.get("field", ""),
                    json.dumps(entity.get("synonyms", [])),
                    paper_id,
                    now, now,
                )
            )

    def _merge_claim(self, entity: dict, paper_id: str):
        assertion = (entity.get("assertion") or "").strip()
        if not assertion:
            return
        now = self._now()
        evidence = entity.get("evidence_level", "weak")
        if evidence not in ("weak", "moderate", "strong"):
            evidence = "weak"
        status = entity.get("status", "open")
        if status not in ("open", "supported", "falsified", "contested"):
            status = "open"
        self.conn.execute(
            """INSERT INTO claims
               (assertion, evidence_level, falsification_criteria, status, source_paper, related_techniques, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, '[]', ?, ?)""",
            (
                assertion,
                evidence,
                entity.get("falsification_criteria", ""),
                status,
                paper_id,
                now, now,
            )
        )

    def merge_entities(self, extracted: dict, paper_id: str):
        """Merge extracted entities into the DB and mark paper processed."""
        now = self._now()

        for entity in extracted.get("techniques", []):
            self._merge_technique(entity, paper_id)
        for entity in extracted.get("reasoning_motifs", []):
            self._merge_reasoning_motif(entity, paper_id)
        for entity in extracted.get("tools", []):
            self._merge_tool(entity, paper_id)
        for entity in extracted.get("terms", []):
            self._merge_term(entity, paper_id)
        for entity in extracted.get("claims", []):
            self._merge_claim(entity, paper_id)

        # Mark paper processed
        self.conn.execute(
            """INSERT INTO papers (id, title, url, processed, processed_at)
               VALUES (?, ?, ?, 1, ?)
               ON CONFLICT(id) DO UPDATE SET processed=1, processed_at=excluded.processed_at""",
            (paper_id, "", "", now)
        )
        self.conn.commit()

    # -----------------------------------------------------------------------
    # Review queue
    # -----------------------------------------------------------------------

    def flag_for_review(self, entity_type: str, entity_id: str, reason: str):
        now = self._now()
        self.conn.execute(
            "INSERT INTO review_queue (entity_type, entity_id, reason, flagged_at, resolved) VALUES (?, ?, ?, ?, 0)",
            (entity_type, entity_id, reason, now)
        )
        self.conn.commit()
        log.info(f"  Flagged for review: [{entity_type} #{entity_id}] {reason}")

    # -----------------------------------------------------------------------
    # run_once
    # -----------------------------------------------------------------------

    def run_once(self):
        papers = self.load_eos_index()
        if not papers:
            log.info("No unprocessed papers found.")
            return

        batch = papers[:self.batch_size]
        log.info(f"Processing {len(batch)} papers (batch_size={self.batch_size})")

        stats = {"techniques": 0, "reasoning_motifs": 0, "tools": 0, "terms": 0, "claims": 0, "errors": 0}

        for i, paper in enumerate(batch, 1):
            log.info(f"[{i}/{len(batch)}] {paper['title'][:70]}")
            try:
                # Upsert paper record first
                now = self._now()
                self.conn.execute(
                    """INSERT INTO papers (id, title, authors, url, score, date_added, processed)
                       VALUES (?, ?, ?, ?, ?, ?, 0)
                       ON CONFLICT(id) DO UPDATE SET title=excluded.title""",
                    (paper["id"], paper["title"], paper.get("authors", ""),
                     paper.get("url", ""), paper.get("score", 0), paper.get("date_added", ""))
                )
                self.conn.commit()

                extracted = self.extract_entities(paper)

                for key in stats:
                    if key != "errors":
                        stats[key] += len(extracted.get(key, []))

                self.merge_entities(extracted, paper["id"])

            except Exception as e:
                log.error(f"  Failed to process {paper['id']}: {e}")
                stats["errors"] += 1

        log.info("Run complete.")
        log.info(f"  techniques={stats['techniques']}, motifs={stats['reasoning_motifs']}, "
                 f"tools={stats['tools']}, terms={stats['terms']}, claims={stats['claims']}, "
                 f"errors={stats['errors']}")

    # -----------------------------------------------------------------------
    # Normalize / deduplicate existing DB entries
    # -----------------------------------------------------------------------

    NORMALIZE_SYSTEM = """You are a taxonomy curator for mechanistic interpretability and AI research.
Your output must be valid JSON and nothing else — no preamble, no commentary, no markdown fences.
"""

    NORMALIZE_PROMPT = """Below is a list of {entity_type} names extracted from papers. Many are duplicates or near-synonyms.

Return a JSON array of merge groups. Each group has:
  - "canonical": the best canonical name to keep (prefer full expanded forms over abbreviations)
  - "merge_ids": list of DB ids to merge into the canonical entry (must include the id of the row whose name matches "canonical", if it exists)
  - "reason": brief one-line explanation of why these are synonymous

Rules:
- Only group things that are genuinely synonymous or abbreviations of the same concept
- Do NOT merge related-but-distinct techniques (e.g. "Sparse Autoencoder" and "Activation Patching" are different)
- Every id in merge_ids must appear in the input list
- If a name already IS the canonical form and has no duplicates, omit it from the output entirely
- Prefer IEEE/ML-community canonical names (e.g. "Chain-of-Thought Prompting" over "chain of thought")

{entity_type} list (id, name, description):
{entries_json}

Return only the JSON array of merge groups. If nothing needs merging, return [].
"""

    _NORMALIZE_CHUNK_SIZE = 20  # entries per LLM call for large tables

    def _call_normalize_llm(self, entries: list, label: str) -> list:
        """Send one chunk of entries to LLM; return merge groups or []."""
        prompt = self.NORMALIZE_PROMPT.format(
            entity_type=label,
            entries_json=json.dumps(entries, indent=2),
        )
        raw = call_llm(prompt, system=self.NORMALIZE_SYSTEM, max_tokens=4096, temperature=0.1)
        if not raw:
            log.warning(f"  {label}: no LLM response for chunk")
            return []
        raw = re.sub(r"^```[a-z]*\n?", "", raw.strip(), flags=re.MULTILINE)
        raw = re.sub(r"\n?```$", "", raw.strip(), flags=re.MULTILINE)
        arr_match = re.search(r"\[[\s\S]*\]", raw)
        if not arr_match:
            log.warning(f"  {label}: no JSON array in chunk response")
            return []
        try:
            result = json.loads(arr_match.group(0))
            return result if isinstance(result, list) else []
        except json.JSONDecodeError as e:
            log.warning(f"  {label}: JSON parse error: {e}")
            return []

    def _run_normalize_pass(self, table: str, name_col: str, label: str) -> dict:
        """Send all entries in `table` to LLM (in chunks), execute merge groups."""
        cur = self.conn.cursor()
        cur.execute(f"SELECT id, {name_col}, description FROM {table} ORDER BY id")
        rows = cur.fetchall()

        if len(rows) < 2:
            log.info(f"  {label}: only {len(rows)} entries, nothing to normalize")
            return {"checked": len(rows), "groups": 0, "merged": 0}

        entries = [{"id": r["id"], "name": r[name_col], "description": (r["description"] or "")[:120]} for r in rows]

        # Chunk into batches to stay within model context limits
        chunk_size = self._NORMALIZE_CHUNK_SIZE
        all_groups = []
        for chunk_start in range(0, len(entries), chunk_size):
            chunk = entries[chunk_start: chunk_start + chunk_size]
            log.info(f"  {label}: normalizing entries {chunk_start+1}-{chunk_start+len(chunk)} of {len(entries)}...")
            groups = self._call_normalize_llm(chunk, label)
            all_groups.extend(groups)

        if not all_groups:
            log.info(f"  {label}: LLM found nothing to merge")
            return {"checked": len(rows), "groups": 0, "merged": 0}

        groups = all_groups

        now = self._now()
        valid_ids = {r["id"] for r in rows}
        total_merged = 0

        for group in groups:
            canonical_name = group.get("canonical", "").strip()
            merge_ids = group.get("merge_ids", [])
            reason = group.get("reason", "")

            if not canonical_name or not merge_ids:
                continue

            # Validate all ids are real
            merge_ids = [int(i) for i in merge_ids if int(i) in valid_ids]
            if len(merge_ids) < 2:
                log.info(f"    Skip group '{canonical_name}': fewer than 2 valid ids")
                continue

            log.info(f"    Merging {merge_ids} -> '{canonical_name}' ({reason})")

            # Fetch all rows to be merged
            placeholders = ",".join("?" * len(merge_ids))
            cur.execute(f"SELECT * FROM {table} WHERE id IN ({placeholders})", merge_ids)
            to_merge = cur.fetchall()
            if not to_merge:
                continue

            # Choose canonical row: prefer whichever row already has the canonical name,
            # else use the one with highest occurrence_count
            canonical_row = None
            for r in to_merge:
                if _normalize(r[name_col]) == _normalize(canonical_name):
                    canonical_row = r
                    break
            if canonical_row is None:
                canonical_row = max(to_merge, key=lambda r: r["occurrence_count"])

            keep_id = canonical_row["id"]
            delete_ids = [r["id"] for r in to_merge if r["id"] != keep_id]

            # Union source_papers
            all_papers: list = []
            seen_papers: set = set()
            for r in to_merge:
                for p in json.loads(r["source_papers"] or "[]"):
                    if p not in seen_papers:
                        all_papers.append(p)
                        seen_papers.add(p)

            # Sum occurrence_count
            total_count = sum(r["occurrence_count"] for r in to_merge)

            # Union aliases (add merged names as aliases too)
            all_aliases: list = []
            seen_aliases: set = set()
            for r in to_merge:
                raw_aliases = r["aliases"] if "aliases" in r.keys() else "[]"
                for a in json.loads(raw_aliases or "[]"):
                    if a not in seen_aliases:
                        all_aliases.append(a)
                        seen_aliases.add(a)
            # Add the names of deleted rows as aliases
            for r in to_merge:
                nm = r[name_col]
                if nm != canonical_name and nm not in seen_aliases:
                    all_aliases.append(nm)
                    seen_aliases.add(nm)

            # Update canonical row
            if table == "techniques":
                self.conn.execute(
                    """UPDATE techniques SET name=?, source_papers=?, occurrence_count=?,
                       aliases=?, updated_at=? WHERE id=?""",
                    (canonical_name, json.dumps(all_papers), total_count,
                     json.dumps(all_aliases), now, keep_id)
                )
            elif table == "reasoning_motifs":
                self.conn.execute(
                    """UPDATE reasoning_motifs SET name=?, source_papers=?, occurrence_count=?,
                       updated_at=? WHERE id=?""",
                    (canonical_name, json.dumps(all_papers), total_count, now, keep_id)
                )
            elif table == "tools":
                self.conn.execute(
                    """UPDATE tools SET name=?, source_papers=?, occurrence_count=?,
                       updated_at=? WHERE id=?""",
                    (canonical_name, json.dumps(all_papers), total_count, now, keep_id)
                )

            # Delete duplicate rows
            if delete_ids:
                del_placeholders = ",".join("?" * len(delete_ids))
                self.conn.execute(f"DELETE FROM {table} WHERE id IN ({del_placeholders})", delete_ids)

            self.conn.commit()
            total_merged += len(delete_ids)

        return {"checked": len(rows), "groups": len(groups), "merged": total_merged}

    def _local_dedup_pass(self, table: str, name_col: str, label: str) -> int:
        """Deterministic pre-pass: merge entries with identical normalized names.

        Returns count of rows deleted.
        """
        cur = self.conn.cursor()
        cur.execute(f"SELECT id, {name_col}, description, source_papers, occurrence_count FROM {table} ORDER BY id")
        rows = [dict(r) for r in cur.fetchall()]

        # Group by normalized name
        groups: dict[str, list] = {}
        for r in rows:
            key = _normalize(r[name_col])
            groups.setdefault(key, []).append(r)

        now = self._now()
        deleted = 0
        for key, members in groups.items():
            if len(members) < 2:
                continue
            # Keep the row with the highest occurrence_count (break ties by lowest id)
            keep = max(members, key=lambda r: (r["occurrence_count"], -r["id"]))
            dupes = [m for m in members if m["id"] != keep["id"]]

            # Merge source_papers
            all_papers: list = []
            seen: set = set()
            for m in members:
                for p in json.loads(m["source_papers"] or "[]"):
                    if p not in seen:
                        all_papers.append(p)
                        seen.add(p)

            total_count = sum(m["occurrence_count"] for m in members)
            cur.execute(
                f"UPDATE {table} SET source_papers=?, occurrence_count=?, updated_at=? WHERE id=?",
                (json.dumps(all_papers), total_count, now, keep["id"])
            )
            del_ids = [m["id"] for m in dupes]
            cur.execute(
                f"DELETE FROM {table} WHERE id IN ({','.join('?'*len(del_ids))})", del_ids
            )
            self.conn.commit()
            log.info(f"  [{label}] Local dedup: merged {[m['id'] for m in dupes]} into "
                     f"id={keep['id']} (norm key: '{key}')")
            deleted += len(del_ids)

        return deleted

    def normalize_entities(self):
        """Two-pass deduplication over techniques, motifs, and tools.

        Pass 1 — local: merge entries with identical normalized names (deterministic).
        Pass 2 — LLM:   send chunks to LLM to catch semantic synonyms.
        """
        log.info("Starting normalization pass...")
        results = {}

        for table, name_col, label, key in [
            ("techniques",       "name", "techniques",      "techniques"),
            ("reasoning_motifs", "name", "reasoning motifs","reasoning_motifs"),
            ("tools",            "name", "tools",           "tools"),
        ]:
            log.info(f"\n--- {label} ---")
            local_deleted = self._local_dedup_pass(table, name_col, label)
            llm_stats = self._run_normalize_pass(table, name_col, label)
            results[key] = {
                "checked": llm_stats["checked"],
                "local_deleted": local_deleted,
                "llm_groups": llm_stats["groups"],
                "llm_deleted": llm_stats["merged"],
            }

        print("\n## Normalization Summary\n")
        total_deleted = 0
        for entity_type, stats in results.items():
            row_del = stats["local_deleted"] + stats["llm_deleted"]
            total_deleted += row_del
            print(f"- **{entity_type}**: checked {stats['checked']}, "
                  f"local deletions {stats['local_deleted']}, "
                  f"LLM groups {stats['llm_groups']}, LLM deletions {stats['llm_deleted']}")
        print(f"\n**Total rows deleted (deduped):** {total_deleted}")

    # -----------------------------------------------------------------------
    # Taxonomy summary
    # -----------------------------------------------------------------------

    def generate_taxonomy_summary(self) -> str:
        cur = self.conn.cursor()

        def count(table):
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            return cur.fetchone()[0]

        lines = ["# Aletheia Knowledge Graph — Taxonomy Summary", ""]
        lines.append(f"_Generated: {self._now()}_")
        lines.append("")

        # Counts
        lines.append("## Entity Counts")
        lines.append("")
        tables = [
            ("papers", "Papers (indexed)"),
            ("techniques", "Techniques"),
            ("reasoning_motifs", "Reasoning Motifs"),
            ("tools", "Tools"),
            ("terms", "Terms"),
            ("claims", "Claims"),
        ]
        for table, label in tables:
            lines.append(f"- **{label}**: {count(table)}")

        proc_count = cur.execute("SELECT COUNT(*) FROM papers WHERE processed=1").fetchone()[0]
        lines.append(f"- **Papers (processed)**: {proc_count}")
        lines.append("")

        # Top techniques
        cur.execute("SELECT name, occurrence_count FROM techniques ORDER BY occurrence_count DESC LIMIT 10")
        rows = cur.fetchall()
        if rows:
            lines.append("## Top 10 Techniques (by occurrence)")
            lines.append("")
            for r in rows:
                lines.append(f"- **{r['name']}** ({r['occurrence_count']})")
            lines.append("")

        # Top terms
        cur.execute("SELECT term, occurrence_count, field FROM terms ORDER BY occurrence_count DESC LIMIT 10")
        rows = cur.fetchall()
        if rows:
            lines.append("## Top 10 Terms (by occurrence)")
            lines.append("")
            for r in rows:
                field_str = f" [{r['field']}]" if r["field"] else ""
                lines.append(f"- **{r['term']}**{field_str} ({r['occurrence_count']})")
            lines.append("")

        # Recent claims
        cur.execute("""
            SELECT assertion, evidence_level, status, source_paper
            FROM claims ORDER BY created_at DESC LIMIT 5
        """)
        rows = cur.fetchall()
        if rows:
            lines.append("## Recent Claims")
            lines.append("")
            for r in rows:
                lines.append(f"- [{r['evidence_level'].upper()}] [{r['status']}] {r['assertion'][:120]}")
            lines.append("")

        # Pending reviews
        cur.execute("SELECT COUNT(*) FROM review_queue WHERE resolved=0")
        pending = cur.fetchone()[0]
        lines.append(f"## Review Queue")
        lines.append("")
        lines.append(f"- **Pending items**: {pending}")
        lines.append("")

        return "\n".join(lines)

    # -----------------------------------------------------------------------
    # Query
    # -----------------------------------------------------------------------

    def query(self, entity_type: str, search_term: str) -> list:
        """Keyword search across name/description for an entity type."""
        table_map = {
            "techniques": ("techniques", ["name", "description"]),
            "motifs": ("reasoning_motifs", ["name", "description"]),
            "tools": ("tools", ["name", "description", "use_case"]),
            "terms": ("terms", ["term", "definition"]),
            "claims": ("claims", ["assertion", "falsification_criteria"]),
        }
        if entity_type not in table_map:
            log.error(f"Unknown entity type: {entity_type}. Choose from: {list(table_map.keys())}")
            return []

        table, cols = table_map[entity_type]
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {table}")
        rows = cur.fetchall()

        term_lower = search_term.lower()
        results = []
        for row in rows:
            for col in cols:
                if col in row.keys() and term_lower in str(row[col] or "").lower():
                    results.append(dict(row))
                    break
        return results

    # -----------------------------------------------------------------------
    # Export
    # -----------------------------------------------------------------------

    def export_json(self, output_path: str = None):
        if output_path is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(self.exports_dir / f"aletheia_export_{ts}.json")

        cur = self.conn.cursor()
        graph = {}
        for table in ("papers", "techniques", "reasoning_motifs", "tools", "terms", "claims", "review_queue"):
            cur.execute(f"SELECT * FROM {table}")
            rows = cur.fetchall()
            graph[table] = [dict(r) for r in rows]

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(graph, f, indent=2, ensure_ascii=False)

        log.info(f"Exported to {output_path}")
        return output_path

    # -----------------------------------------------------------------------
    # Review queue display
    # -----------------------------------------------------------------------

    def show_review_queue(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM review_queue WHERE resolved=0 ORDER BY flagged_at DESC")
        rows = cur.fetchall()
        if not rows:
            print("No pending review queue items.")
            return
        print(f"\n{'ID':<6} {'Type':<16} {'Entity ID':<12} {'Reason':<60} Flagged")
        print("-" * 110)
        for r in rows:
            print(f"{r['id']:<6} {r['entity_type']:<16} {str(r['entity_id']):<12} "
                  f"{str(r['reason'])[:58]:<60} {r['flagged_at'][:19]}")

    def resolve_review(self, item_id: int):
        self.conn.execute("UPDATE review_queue SET resolved=1 WHERE id=?", (item_id,))
        self.conn.commit()
        log.info(f"Resolved review queue item #{item_id}")

    def close(self):
        self.conn.close()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Aletheia — Knowledge Harvesting & Taxonomy Agent"
    )
    parser.add_argument("--once", action="store_true", help="Process all unprocessed Eos papers")
    parser.add_argument("--summary", action="store_true", help="Print taxonomy summary markdown")
    parser.add_argument("--normalize", action="store_true",
                        help="LLM-powered dedup pass over techniques, motifs, and tools")
    parser.add_argument("--query", nargs=2, metavar=("TYPE", "TERM"),
                        help="Keyword search: --query techniques 'chain of thought'")
    parser.add_argument("--export", action="store_true", help="Export full graph to exports/")
    parser.add_argument("--review", action="store_true", help="Show pending review queue items")
    parser.add_argument("--resolve", type=int, metavar="ID", help="Mark a review queue item resolved")
    parser.add_argument("--config", default=None, help="Path to aletheia_config.yaml")

    args = parser.parse_args()

    # Default config path
    config_path = args.config or str(ALETHEIA_ROOT / "configs" / "aletheia_config.yaml")
    agent = AletheiaAgent(config_path=config_path)

    try:
        if args.once:
            agent.run_once()

        elif args.normalize:
            agent.normalize_entities()

        elif args.summary:
            print(agent.generate_taxonomy_summary())

        elif args.query:
            entity_type, search_term = args.query
            results = agent.query(entity_type, search_term)
            if not results:
                print(f"No results for '{search_term}' in {entity_type}")
            else:
                print(f"\n{len(results)} result(s) for '{search_term}' in {entity_type}:\n")
                for r in results:
                    name = r.get("name") or r.get("term") or r.get("assertion", "")
                    desc = r.get("description") or r.get("definition") or ""
                    print(f"  [{r.get('id')}] {name}")
                    if desc:
                        print(f"       {desc[:120]}")
                    print()

        elif args.export:
            path = agent.export_json()
            print(f"Exported to: {path}")

        elif args.review:
            agent.show_review_queue()

        elif args.resolve is not None:
            agent.resolve_review(args.resolve)
            print(f"Resolved review queue item #{args.resolve}")

        else:
            parser.print_help()

    finally:
        agent.close()


if __name__ == "__main__":
    main()
