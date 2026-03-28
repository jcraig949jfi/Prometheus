# Constitutional Enforcement — System Design

*How the Constitution becomes code. Two machines, automated deposition, blocking gates, and per-agent impact.*

---

## Deployment Architecture: Two Machines

The system splits cleanly along the GPU boundary. Machine A handles content discovery and knowledge curation (CPU + API). Machine B handles reasoning evolution and the forge pipeline (GPU + API). They share state via synced files.

```
┌─────────────────────────────────────────────────────┐
│  MACHINE A — "The Library" (CPU, any spare PC)      │
│                                                     │
│  Eos ──→ Aletheia ──→ Metis ──→ Hermes             │
│            ↑                                        │
│  Clymene   │  Pronoia (constitutional guardian)     │
│  Skopos    │                                        │
│            │                                        │
│  knowledge_graph.db  [THE SUBSTRATE]                │
│                                                     │
│  Sync: pushes knowledge_graph.db → Machine B        │
│  Sync: pulls forge/, nous/runs/, ignis/results/     │
└─────────────────────────────────────────────────────┘
              ↕  rsync every 5 min (small files)
              ↕  or shared network folder
┌─────────────────────────────────────────────────────┐
│  MACHINE B — "The Forge" (GPU, current machine)     │
│                                                     │
│  Nous ──→ Hephaestus ──→ Nemesis ──→ Coeus ──→     │
│    ↑                                          │     │
│    └──────────────────────────────────────────┘     │
│                                                     │
│  Ignis / Rhea  [GPU-BOUND, TransformerLens]         │
│                                                     │
│  Autonomous Athena (claude CLI)                     │
│                                                     │
│  Sync: pushes forge/, runs/, results/ → Machine A   │
│  Sync: pulls knowledge_graph.db from Machine A      │
└─────────────────────────────────────────────────────┘
```

### Why This Split Works

| Agent | GPU? | API? | CPU Load | Machine |
|-------|------|------|----------|---------|
| **Eos** | No | NVIDIA/Cerebras/Groq | Light | A |
| **Aletheia** | No | NVIDIA (for extraction) | Light | A |
| **Metis** | No | NVIDIA | Light | A |
| **Hermes** | No | Gmail SMTP | Minimal | A |
| **Clymene** | No | HuggingFace (optional) | Light (git clones) | A |
| **Skopos** | No | NVIDIA | Light | A |
| **Pronoia** | No | None | Minimal | A |
| **Nous** | No | NVIDIA | Medium | B |
| **Hephaestus** | No | NVIDIA (397B codegen) | Medium | B |
| **Nemesis** | No | None | Medium (numpy) | B |
| **Coeus** | No | None | Medium (scipy) | B |
| **Ignis** | **YES** | None | High | B |
| **Rhea** | **YES** | None | High | B |

Machine A is pure CPU + API calls. Any old laptop, desktop, or Raspberry Pi with decent internet will do. Machine B keeps the GPU for Ignis/Rhea and runs the forge pipeline on API calls in parallel.

### Sync Mechanism

The two machines share state through a small set of files. Options from simplest to most robust:

**Option 1: Shared network folder (simplest)**
- Map a network drive between machines
- All agents read/write to the same paths
- SQLite in WAL mode handles concurrent reads
- Risk: file locking issues on Windows across SMB

**Option 2: rsync on a timer (most reliable)**
```bash
# On Machine A, every 5 minutes:
rsync -av B:/Prometheus/agents/hephaestus/forge/ /Prometheus/agents/hephaestus/forge/
rsync -av B:/Prometheus/agents/nous/runs/ /Prometheus/agents/nous/runs/
rsync -av B:/Prometheus/ignis/results/ /Prometheus/ignis/results/ --exclude='*.pt'

# On Machine B, every 5 minutes:
rsync -av A:/Prometheus/agents/aletheia/data/ /Prometheus/agents/aletheia/data/
```

**Option 3: Git-based sync (constitutional)**
- Both machines share the same git repo
- Machine A commits substrate changes; Machine B commits forge/evolution changes
- Pronoia runs `git pull` before each cycle
- Natural audit trail — every substrate change is a commit

**Recommended: Start with Option 2 (rsync).** Upgrade to NFS or shared folder if latency matters.

### What Gets Synced

| Direction | Files | Size | Frequency |
|-----------|-------|------|-----------|
| A → B | `aletheia/data/knowledge_graph.db` | 100-500MB | Every 10 min |
| A → B | `coeus/graphs/concept_scores.json` | <1MB | After Coeus rebuild |
| B → A | `hephaestus/forge/*.py, *.json` | <20MB | After each forge |
| B → A | `hephaestus/ledger.jsonl` | <10MB | After each forge |
| B → A | `nous/runs/*/responses.jsonl` | <50MB/run | After each batch |
| B → A | `nemesis/grid/grid.json` | <60MB | After each cycle |
| B → A | `ignis/results/**/*.json` | <10MB/run | After each experiment |
| B → A | `ignis/results/**/*.pt` | 8KB-8MB each | **Selective** (best genomes only) |

Note: Ignis checkpoint `.pt` files are small (8KB for steering vectors) but can accumulate. Only sync `best_genome_*.pt` and `final_eval_*.json`, not every checkpoint.

---

## The Ingest Module: `aletheia/src/ingest.py`

Every agent calls this to deposit into the substrate. Three functions, one SQLite database.

```python
# agents/aletheia/src/ingest.py

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "knowledge_graph.db"

def _get_db():
    db = sqlite3.connect(str(DB_PATH))
    db.execute("PRAGMA journal_mode=WAL")  # Concurrent read-safe
    return db

def deposit_entity(name, entity_type, source_agent, metadata=None, evidence_grade="preliminary"):
    """Insert an entity. Returns entity_id. Idempotent on (name, entity_type)."""
    db = _get_db()
    existing = db.execute(
        "SELECT id FROM entities WHERE name = ? AND entity_type = ?",
        [name, entity_type]
    ).fetchone()
    if existing:
        # Update metadata if entity exists
        if metadata:
            db.execute(
                "UPDATE entities SET metadata = ?, updated_at = ? WHERE id = ?",
                [json.dumps(metadata), datetime.now().isoformat(), existing[0]]
            )
            db.commit()
        return existing[0]
    db.execute(
        "INSERT INTO entities (name, entity_type, source_agent, metadata, evidence_grade, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        [name, entity_type, source_agent, json.dumps(metadata or {}), evidence_grade, datetime.now().isoformat()]
    )
    db.commit()
    entity_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    return entity_id

def deposit_relationship(entity_a_id, entity_b_id, rel_type, evidence_grade="preliminary", metadata=None):
    """Insert a relationship. rel_type: bridges|subsumes|contradicts|extends|instantiates|drives|synergizes|handles"""
    db = _get_db()
    db.execute(
        "INSERT OR IGNORE INTO relationships (entity_a_id, entity_b_id, rel_type, evidence_grade, metadata, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        [entity_a_id, entity_b_id, rel_type, evidence_grade, json.dumps(metadata or {}), datetime.now().isoformat()]
    )
    db.commit()

def deposit_gap(category, gap_type, description, discovered_by="unknown"):
    """Record something the substrate doesn't know. gap_type: unsearched|under_described|unstable|infeasible"""
    db = _get_db()
    db.execute(
        "INSERT INTO gaps (category, gap_type, description, discovered_by, created_at) VALUES (?, ?, ?, ?, ?)",
        [category, gap_type, description, discovered_by, datetime.now().isoformat()]
    )
    db.commit()

def get_substrate_health(hours=24):
    """Returns growth metrics for the constitutional gate."""
    db = _get_db()
    since = (datetime.now() - timedelta(hours=hours)).isoformat()
    entities = db.execute("SELECT COUNT(*) FROM entities WHERE created_at > ?", [since]).fetchone()[0]
    relations = db.execute("SELECT COUNT(*) FROM relationships WHERE created_at > ?", [since]).fetchone()[0]
    gaps = db.execute("SELECT COUNT(*) FROM gaps WHERE created_at > ?", [since]).fetchone()[0]
    return {"entities": entities, "relations": relations, "gaps": gaps}
```

---

## Per-Agent Impact

### Eos (Machine A)

**Current behavior:** Scans arXiv/OpenAlex/GitHub, writes reports to `eos/reports/`, updates `paper_index.json`.

**After enforcement:**
- After each scan cycle, calls `deposit_entity()` for each paper found
- Extracts technique names, author names, key claims as separate entities
- Links papers to techniques via `deposit_relationship(paper_id, technique_id, "describes")`
- Flags papers related to active Ignis/Rhea experiments via metadata tag

**Code change:** Add 15-20 lines to `eos_daemon.py` post-scan hook. Import `ingest.py`.

**Impact on Machine A load:** Negligible. One SQLite write per paper (~50-200 papers per scan).

---

### Aletheia (Machine A)

**Current behavior:** Extracts structured entities from papers via LLM. Writes to `knowledge_graph.db`.

**After enforcement:**
- Already writes to the database — this is the primary substrate builder
- New: must populate `evidence_grade` for every entity (defaults to "preliminary")
- New: must create `gaps` entries when extraction finds references to concepts not yet in the graph
- New: must create relationship types from the expanded schema (bridges, subsumes, contradicts, extends)

**Code change:** Modify extraction prompts to return evidence strength and relationship types. Add gap detection logic. ~30-50 lines.

**Impact:** Moderate. LLM calls for extraction are the bottleneck, not the database writes.

---

### Metis (Machine A)

**Current behavior:** Reads Eos digest, produces executive briefs.

**After enforcement:**
- After each brief, deposits key findings as entities: `deposit_entity("finding: ...", "metis_finding", "metis", {...})`
- Links findings to the papers they came from
- New: identifies gaps in the substrate by comparing brief topics to existing Aletheia entities. If a brief topic has no matching entity, creates a gap.

**Code change:** Add 10-15 lines post-brief. Import `ingest.py`.

**Impact:** Minimal.

---

### Hermes (Machine A)

**Current behavior:** Collects outputs from all agents, sends email digest.

**After enforcement:**
- No change to core behavior
- New: includes substrate health metrics in every digest (entities added, relations added, gaps found, violations)
- Reads `get_substrate_health()` from ingest module

**Code change:** Add 5-10 lines to digest template. Import `ingest.py` for health check.

**Impact:** Minimal.

---

### Pronoia (Machine A — constitutional guardian)

**Current behavior:** Orchestrates Eos → Aletheia → Metis → Hermes chain.

**After enforcement (major upgrade):**

**Daily Pulse (runs at start of each cycle):**
```python
health = get_substrate_health(hours=24)
if health["entities"] < 5 and health["relations"] < 10 and health["gaps"] < 1:
    log("CONSTITUTIONAL ALERT: Substrate starvation detected")
    # Option 1: Force Eos + Aletheia extraction run before anything else
    # Option 2: Send alert to Hermes for James's morning digest
    # Option 3: Block Machine B's forge pipeline (aggressive)
```

**Weekly Absorption Audit:**
```python
absorption_table = load_absorption_table()  # Parse from CONSTITUTION.md
for concept in absorption_table:
    if concept.status == "NOT YET ABSORBED":
        days_unabsorbed = (now - concept.first_logged).days
        if days_unabsorbed > 30:
            log(f"LAW 2 VIOLATION: {concept.name} unabsorbed for {days_unabsorbed} days")
```

**Monthly Novelty Audit:**
```python
new_entity_types = count_distinct_entity_types_created(days=30)
xenolexicon_specimens = count_entities(entity_type="xenolexicon_specimen", days=30)
if new_entity_types == 0 and xenolexicon_specimens == 0:
    log("LAW 5 CONCERN: No genuine novelty in 30 days")
```

**Code change:** New file `pronoia/src/constitutional_pulse.py` (~100 lines). Wire into `pronoia.py` main loop.

**Impact:** This is the enforcement mechanism. Without it, the Constitution is prose.

---

### Nous (Machine B)

**Current behavior:** Mines concept combinations from a static 95-concept dictionary. Writes to `runs/*/responses.jsonl`.

**After enforcement:**
- Reads concepts from Aletheia's knowledge graph in addition to static dictionary
- Gap-prefixed concepts tell Nous to specifically generate combinations targeting substrate holes
- After each batch, deposits high-scoring combinations as entities

**Code change:** Modify `concepts.py` to optionally pull from Aletheia DB. Add post-batch deposition. ~40 lines.

**Cross-machine impact:** Needs read access to `knowledge_graph.db` from Machine A. This is the primary A→B sync dependency.

---

### Hephaestus (Machine B)

**Current behavior:** Forges reasoning tools. Writes to `forge/`, `scrap/`, `ledger.jsonl`.

**After enforcement:**
- After every forge attempt (pass OR fail), deposits entity into Aletheia
- Successful forges: entity_type = "forge_tool", linked to concept entities
- Failed forges: entity_type = "forge_failure" (feeds Arcanum)
- New Gate 5.5: AST similarity dedup. Reject if similarity > 0.7 to any existing tool.

**Code change:**
- Add post-forge deposition (~20 lines in `hephaestus.py`)
- Add dedup gate (~40 lines, new function `diversity_gate()`)
- Add CAITL self-contained constraint to prompt

**Cross-machine impact:** Deposits go to local copy of `knowledge_graph.db`, synced back to Machine A.

---

### Nemesis (Machine B)

**Current behavior:** Generates adversarial tasks, fills MAP-Elites grid, evaluates tools.

**After enforcement:**
- After each adversarial cycle, deposits failure patterns as entities
- `entity_type = "reasoning_failure"` with metadata: tool, mutation type, task category, failure geometry
- Links to the tool entity and the Sphinx category entity
- This is the "graveyard of failed ideas" that Gemini identified as core substrate

**Code change:** Add post-cycle deposition (~15 lines). Import `ingest.py`.

**Impact:** This is the most undervalued change. Failure data is substrate. Currently it's thrown away after scoring.

---

### Coeus (Machine B)

**Current behavior:** Builds causal graphs from forge history. Writes to `graphs/`, `enrichments/`.

**After enforcement:**
- After each rebuild, deposits causal relationships into Aletheia
- `concept_A --drives--> forge_success` (with weight as metadata)
- `concept_A --synergizes_with--> concept_B` (with synergy score)
- `concept_A --confounded_by--> unknown_variable` (FCI flag)
- Confounder flags become gaps: `deposit_gap(concept, "unstable", "correlation may be spurious")`

**Code change:** Add post-rebuild deposition (~25 lines). Import `ingest.py`.

**Impact:** Causal relationships ARE substrate. They should be queryable entities, not just JSON files.

---

### Ignis (Machine B — GPU)

**Current behavior:** Runs evolution, eval, decomposition. Writes to `results/`.

**After enforcement:**
- After every experiment, deposits structured results as entities
- Evolution runs: layer, SR, ES, flipped traps, broken traps, phase transition generation
- Eval_v2 runs: 7-pillar scores as metadata
- Decomposition: per-head contributions linked to model entity
- Logit lens: L* values, ejection profiles
- New: waste stream sampling (passive Arcanum). Top-25 alternative tokens at output layer captured during every forward pass.

**Code change:**
- Add post-run deposition to each script (~10-15 lines each, 8 scripts = ~100 lines total)
- Add waste stream sampler to `analysis_base.py` (~30 lines)

**Impact:** Ignis produces the richest experimental data in the system. Currently none of it reaches the substrate automatically. This is the highest-volume deposition source.

---

### Rhea (Machine B — GPU)

**Current behavior:** Evolves models via CMA-ES. Writes genomes, logs, self-corpus.

**After enforcement:**
- After each evolution run: deposit genome metadata, fitness trajectory, flipped traps
- After self-corpus generation: each verified reasoning chain becomes a `verified_reasoning` entity
- Link chains to model, genome, and trap entities
- Self-corpus IS substrate — the Constitution says this explicitly

**Code change:** Add post-run and post-corpus deposition (~20 lines per script).

**Impact:** Verified reasoning chains are among the most valuable substrate entities. Currently they exist only as training data.

---

## The Constitutional Gate: Blocking Mechanism

### For GPU experiments (Machine B)

```python
# pronoia_gate.py — import at top of every batch script
import sys
sys.path.insert(0, "agents/aletheia/src")
from ingest import get_substrate_health

def check_gate(force=False):
    health = get_substrate_health(hours=24)
    total = health["entities"] + health["relations"] + health["gaps"]
    if total < 10 and not force:
        print("=" * 60)
        print("CONSTITUTIONAL GATE — SUBSTRATE STARVATION")
        print(f"  Last 24h: {health['entities']} entities, {health['relations']} relations, {health['gaps']} gaps")
        print(f"  Minimum required: 10 total (any combination)")
        print()
        print("  The substrate has not grown. Law 1 says: the substrate is the product.")
        print("  Run Eos + Aletheia extraction before GPU experiments.")
        print("  Override with --force-gate if experiment is urgent.")
        print("=" * 60)
        sys.exit(1)
    print(f"Gate passed: {total} substrate additions in last 24h")
```

### For batch scripts (.bat)

```batch
REM Constitutional gate — check substrate health before GPU work
python agents\aletheia\src\ingest.py --health-check
if errorlevel 1 (
    echo [GATE] Substrate starvation. Run Eos chain first.
    echo [GATE] Override: set FORCE_GATE=1
    if not "%FORCE_GATE%"=="1" exit /b 1
)
```

### Override mechanism

The gate can be overridden with `--force-gate` for truly urgent experiments. But the override is logged:
```python
if force:
    deposit_entity("gate_override", "constitutional_event", "pronoia",
                   {"reason": "manual override", "health": health})
    log("GATE OVERRIDDEN — logged as constitutional event")
```

Every override is visible in the substrate. James can see how often he's bypassing his own Constitution.

---

## Machine A Daily Cycle (Automated, No James Required)

```
00:00  Pronoia constitutional pulse
       → Check substrate health
       → Check absorption debt
       → Generate violation alerts

01:00  Eos scan cycle
       → Scan arXiv, OpenAlex, GitHub
       → Deposit papers + techniques into Aletheia
       → Flag papers related to active experiments

02:00  Aletheia extraction
       → Process new Eos papers
       → Extract entities, relationships, evidence grades
       → Identify gaps (concepts referenced but not in graph)

03:00  Metis synthesis
       → Read Eos findings
       → Produce executive brief
       → Deposit findings into Aletheia

04:00  Hermes digest
       → Collect all agent outputs (from both machines via sync)
       → Include substrate health metrics
       → Include constitutional violation alerts
       → Send email digest

05:00-23:00  Idle (or continuous Eos scanning on slow timer)

23:00  Pronoia end-of-day audit
       → Re-check substrate health
       → If starvation: trigger forced extraction sprint
       → Prepare morning brief for James
```

This runs entirely unattended on Machine A. When James wakes up, his email has the Hermes digest with substrate health, violations, and the day's findings.

---

## Machine B Daily Cycle (GPU + Forge Pipeline)

```
00:00  Constitutional gate check
       → Reads substrate health from synced knowledge_graph.db
       → Blocks if starvation (unless overridden)

00:05  GPU experiments (Ignis/Rhea/Athena CLI)
       → Whatever's queued: evolution, eval, decomposition
       → Post-run: auto-deposit results into local Aletheia copy
       → Sync results back to Machine A

[parallel with GPU]
       Nous → Hephaestus → Nemesis → Coeus (API-based, no GPU)
       → Each deposits entities after completion
       → Hephaestus dedup gate active
       → Nemesis deposits failure patterns

[after GPU run completes]
       Next GPU experiment starts
       → Gate re-checked
       → Cycle continues
```

---

## Summary: What Changes Per Agent

| Agent | Machine | New Code | Key Change |
|-------|---------|----------|------------|
| **Eos** | A | ~15 lines | Deposits papers + techniques into Aletheia after scan |
| **Aletheia** | A | ~40 lines | Evidence grades, gap detection, expanded relationship types |
| **Metis** | A | ~10 lines | Deposits findings, identifies substrate gaps |
| **Hermes** | A | ~10 lines | Includes substrate health in digest |
| **Pronoia** | A | ~100 lines (new file) | Constitutional pulse, absorption audit, novelty audit, gate |
| **Clymene** | A | ~5 lines | Deposits repo metadata into Aletheia |
| **Nous** | B | ~40 lines | Reads concepts from Aletheia, deposits high-scoring combos |
| **Hephaestus** | B | ~60 lines | Post-forge deposition (pass + fail), dedup gate |
| **Nemesis** | B | ~15 lines | Deposits failure patterns as substrate entities |
| **Coeus** | B | ~25 lines | Deposits causal relationships + confounder gaps |
| **Ignis** | B | ~130 lines (across 8 scripts) | Deposits experiment results, waste stream sampling |
| **Rhea** | B | ~20 lines | Deposits genomes, verified reasoning chains |
| **Total** | | **~470 lines** | Constitution becomes runtime, not prose |

---

## What James Actually Does Differently

**Before:** Run experiments → maybe update Aletheia → feel guilty → run more experiments

**After:**
- **Morning:** Read Hermes email digest on phone. Check: any constitutional violations? Any substrate starvation? Any novelty in 30 days?
- **Machine A:** Running autonomously. Eos scans, Aletheia extracts, Pronoia audits. No James required.
- **Machine B:** GPU experiments + forge pipeline. Constitutional gate ensures substrate grew before experiments run. Auto-deposition after every experiment.
- **Evening:** Review what both machines produced. The substrate grew as a side effect. The gate prevented substrate starvation. The audit caught violations.

**Net change in James's workload:** Less manual curation, more steering. The 470 lines of new code do the work that James was supposed to do manually but never did because experiments were more fun.

---

## The Guarantee, Codified

The Constitution says: "If you don't push for it, it doesn't happen."

After enforcement: The code pushes for it. The gate blocks experiments if the substrate doesn't grow. The deposits happen automatically. The audits run on a timer. The violations are logged and reported.

James doesn't need to push for it anymore. The system pushes for itself.
