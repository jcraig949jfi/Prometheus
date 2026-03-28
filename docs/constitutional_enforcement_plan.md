# Constitutional Enforcement Plan

*Turning the Constitution from prose into code. Ordered by effort vs impact.*

---

## Principle: Make the Right Thing Automatic

The Constitution fails because substrate growth requires James's manual attention, which competes with experiments that produce dopamine (numbers going up). The fix is not discipline — it's architecture. Every experiment must deposit into the substrate as a *side effect of running*, not as a separate task James remembers to do afterward.

---

## Phase 1: The Blocking Gate (Day 1 — 2-3 hours)

**Impact: Enforces Laws 1, 2, 3, 4 simultaneously**

### 1.1 Create `agents/aletheia/src/ingest.py`

A simple Python module that every agent imports. Three functions:

```python
def deposit_entity(name, entity_type, source_agent, metadata={}):
    """Insert an entity into Aletheia's SQLite. Returns entity_id."""

def deposit_relationship(entity_a_id, entity_b_id, rel_type, evidence_grade="preliminary"):
    """Insert a relationship. rel_type: bridges|subsumes|contradicts|extends|instantiates"""

def deposit_gap(category, gap_type, description):
    """Record something the substrate doesn't know. gap_type: unsearched|under_described|unstable|infeasible"""
```

This is the translation layer ChatGPT identified as missing. Every agent calls these functions. The substrate grows as a side effect.

### 1.2 Add post-run hooks to existing scripts

**Hephaestus** — After every forge attempt (success OR failure):
```python
# In hephaestus.py, after Gate 5:
from aletheia.ingest import deposit_entity, deposit_relationship
entity_id = deposit_entity(
    name=combo_key,
    entity_type="forge_tool" if passed else "forge_failure",
    source_agent="hephaestus",
    metadata={"accuracy": acc, "calibration": cal, "concepts": concept_names, "failure_reason": reason}
)
for concept in concept_names:
    concept_id = deposit_entity(concept, "concept", "nous")
    deposit_relationship(entity_id, concept_id, "instantiates")
```

**Ignis** — After every evolution run, eval, or decomposition:
```python
# In evolve_1_5b.py, after evolution completes:
from aletheia.ingest import deposit_entity, deposit_relationship
deposit_entity(
    name=f"evolution_L{layer}_{timestamp}",
    entity_type="experiment_result",
    source_agent="ignis",
    metadata={"layer": layer, "sr": survival_rate, "es": monotonicity, "flipped": n_flipped, "broken": n_broken}
)
```

**Nemesis** — After every adversarial cycle:
```python
# Failed tool-task pairs become substrate:
deposit_entity(
    name=f"failure_{tool_name}_{task_category}",
    entity_type="reasoning_failure",
    source_agent="nemesis",
    metadata={"tool": tool_name, "mutation_type": mr, "task": task_prompt}
)
```

### 1.3 The Gate Itself

Add to `run_forge_pipeline.bat` and every batch script:
```python
# pronoia_gate.py — run before any GPU experiment
import sqlite3
from datetime import datetime, timedelta

db = sqlite3.connect("agents/aletheia/data/knowledge_graph.db")
yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
new_entities = db.execute("SELECT COUNT(*) FROM entities WHERE created_at > ?", [yesterday]).fetchone()[0]
new_relations = db.execute("SELECT COUNT(*) FROM relationships WHERE created_at > ?", [yesterday]).fetchone()[0]

if new_entities < 5 and new_relations < 10:
    print("CONSTITUTIONAL GATE: Substrate has not grown in 24h.")
    print(f"  Entities added: {new_entities} (minimum: 5)")
    print(f"  Relations added: {new_relations} (minimum: 10)")
    print("  Run Eos + Metis extraction before starting GPU experiments.")
    print("  Override with --force-gate if truly urgent.")
    sys.exit(1)
```

**This is the single highest-leverage change.** It makes Law 1 a runtime constraint, not an aspiration.

---

## Phase 2: Schema Expansion (Day 1-2 — 2-3 hours)

**Impact: Absorbs 4 of the 16 unabsorbed concepts immediately**

### 2.1 Aletheia Schema Additions

These are ALTER TABLE statements. Minutes of work each.

```sql
-- Evidence grades (from Living Ideas P1.2)
ALTER TABLE entities ADD COLUMN evidence_grade TEXT DEFAULT 'preliminary';
-- Values: preliminary | replicated | contradicted | formally_proven | retracted

-- Gap tracking (from Living Ideas P2.2)
CREATE TABLE gaps (
    id INTEGER PRIMARY KEY,
    category TEXT NOT NULL,          -- Sphinx category or domain
    gap_type TEXT NOT NULL,          -- unsearched | under_described | unstable | infeasible
    description TEXT,
    discovered_by TEXT,              -- which agent found this gap
    created_at TEXT DEFAULT (datetime('now')),
    resolved_at TEXT                 -- NULL until filled
);

-- Relationship types (from Living Ideas P3.2)
-- Already have relationships table; add semantic types:
-- bridges, hybridizes, subsumes, competes, contradicts, extends, instantiates

-- Xenolexicon entity type (from Arcanum)
-- No schema change needed — just use entity_type = 'xenolexicon_specimen'
-- Add classification field:
ALTER TABLE entities ADD COLUMN specimen_class TEXT;
-- Values: NULL (not a specimen) | true_arcanum | collision | echo | chimera

-- Provenance tracking
ALTER TABLE entities ADD COLUMN provenance TEXT DEFAULT 'evaluation';
-- Values: evaluation | training | adversarial (the hard gate from Rhea Batch 3)
```

**Absorption debt after Phase 2:** 16 → 12 unabsorbed concepts.

### 2.2 Sphinx Categories as Aletheia Entities

Every Sphinx category should exist as an Aletheia entity with relationships to tools that handle it:

```python
for category in sphinx_categories:
    cat_id = deposit_entity(category, "reasoning_category", "sphinx",
                           {"tier": "A" or "B", "domain": domain})
    for tool in tools_that_pass_category:
        deposit_relationship(tool_id, cat_id, "handles")
    if no_tools_pass:
        deposit_gap(category, "unsearched", f"No tool handles {category}")
```

This creates the first gap-type entries automatically.

---

## Phase 3: Pronoia Constitutional Checks (Day 2-3 — 3-4 hours)

**Impact: Automated daily enforcement of Laws 1-5**

### 3.1 `agents/pronoia/src/constitutional_pulse.py`

```python
def daily_pulse():
    """Run at 00:00. Check all three pillars. Output to Hermes digest."""

    # Substrate pulse
    entities_24h = count_new_entities(hours=24)
    relations_24h = count_new_relations(hours=24)
    gaps_24h = count_new_gaps(hours=24)
    substrate_healthy = entities_24h >= 5 or relations_24h >= 10 or gaps_24h >= 1

    # Reasoning pulse
    forges_24h = count_new_forges(hours=24)
    evolution_runs_24h = count_evolution_runs(hours=24)
    reasoning_healthy = forges_24h >= 3 or evolution_runs_24h >= 1

    # Verification pulse
    nemesis_evals_24h = count_nemesis_evaluations(hours=24)
    verification_healthy = nemesis_evals_24h >= 20

    # Absorption debt
    unabsorbed = count_unabsorbed_concepts()

    # Diversity check (anti-Goodhart)
    max_ast_similarity = compute_max_pairwise_similarity()
    monoculture_risk = max_ast_similarity > 0.7

    # Report
    report = {
        "date": today(),
        "substrate": {"entities": entities_24h, "relations": relations_24h, "gaps": gaps_24h, "healthy": substrate_healthy},
        "reasoning": {"forges": forges_24h, "evolutions": evolution_runs_24h, "healthy": reasoning_healthy},
        "verification": {"nemesis_evals": nemesis_evals_24h, "healthy": verification_healthy},
        "absorption_debt": unabsorbed,
        "monoculture_risk": monoculture_risk,
        "violations": []
    }

    if not substrate_healthy:
        report["violations"].append("LAW 1 VIOLATION: Substrate did not grow in 24h")
    if unabsorbed > 12:
        report["violations"].append(f"LAW 2 VIOLATION: {unabsorbed} concepts unabsorbed")
    if monoculture_risk:
        report["violations"].append("LAW 5 VIOLATION: Tool monoculture detected (AST similarity > 0.7)")

    return report
```

### 3.2 Weekly Absorption Audit

```python
def weekly_absorption_audit():
    """Check the absorption protocol table. Flag anything unabsorbed > 30 days."""
    absorption_table = load_absorption_table()  # From CONSTITUTION.md
    for concept in absorption_table:
        if concept.status == "NOT YET ABSORBED" and concept.age_days > 30:
            alert(f"CONSTITUTIONAL VIOLATION: {concept.name} unabsorbed for {concept.age_days} days")
```

### 3.3 Monthly Novelty Audit

```python
def monthly_novelty_audit():
    """Has anything genuinely novel emerged? Not 'higher accuracy' — novel."""
    new_entity_types = count_new_entity_types(days=30)
    new_relationship_types = count_new_relationship_types(days=30)
    xenolexicon_specimens = count_specimens(days=30)
    new_sphinx_categories = count_new_categories(days=30)

    novelty_score = new_entity_types + new_relationship_types + xenolexicon_specimens + new_sphinx_categories
    if novelty_score == 0:
        alert("LAW 5 CONCERN: No genuine novelty in 30 days. Trigger high-temperature Nous + Arcanum hunt.")
```

---

## Phase 4: Auto-Extraction Hooks (Day 3-5 — 4-6 hours)

**Impact: Makes substrate growth a side effect of existing workflows**

### 4.1 Eos → Aletheia Auto-Extraction

Modify `agents/eos/src/eos.py` post-scan hook:
- For each paper found, extract: title, authors, key techniques, claims
- Deposit as entities with `evidence_grade = "preliminary"`
- Link techniques to existing Aletheia concepts via fuzzy matching
- Flag papers related to active Ignis/Rhea experiments

### 4.2 Coeus → Aletheia Causal Relationships

After every Coeus rebuild:
- Each concept forge effect becomes a relationship: `concept --drives--> forge_success` with weight
- Each synergy pair becomes: `concept_A --synergizes_with--> concept_B`
- Each confounder flag becomes: `concept --confounded_by--> unknown_variable`

### 4.3 Ignis Results → Aletheia Experimental Entities

After every eval_v2, logit_lens, or ejection_decompose run:
- Create experiment_result entity with full metadata
- Link to model entity, layer entities, trap entities
- Deposit per-head contributions as sub-entities
- Phase transitions become first-class entities with generation number, SR before/after

### 4.4 Rhea Self-Corpus → Aletheia Knowledge

When loop_closure.py generates verified reasoning chains:
- Each verified chain becomes a `verified_reasoning` entity
- Links to the model, the genome, the trap it solved
- The self-corpus IS substrate — the Constitution says so explicitly

---

## Phase 5: Hephaestus Dedup Gate (Day 3 — 2 hours)

**Impact: Prevents CAITL monoculture recurrence**

### 5.1 Add to Hephaestus Gate 5.5: Diversity Check

After a tool passes the trap battery but before admission to forge/:

```python
import ast

def ast_similarity(tool_a_path, tool_b_path):
    """Structural similarity between two tools' AST."""
    tree_a = ast.parse(Path(tool_a_path).read_text())
    tree_b = ast.parse(Path(tool_b_path).read_text())
    dump_a = ast.dump(tree_a, indent=0)
    dump_b = ast.dump(tree_b, indent=0)
    # NCD on AST dumps
    return ncd(dump_a.encode(), dump_b.encode())

def diversity_gate(new_tool_path, forge_dir):
    """Reject if too similar to any existing tool."""
    for existing in Path(forge_dir).glob("*.py"):
        if existing.name.startswith("_"):
            continue
        sim = ast_similarity(new_tool_path, existing)
        if sim > 0.7:
            return False, f"Too similar to {existing.name} (similarity={sim:.2f})"
    return True, "Diverse enough"
```

### 5.2 CAITL Self-Contained Constraint

Add to the CAITL prompt:
```
HARD CONSTRAINT: The improved tool must be ENTIRELY self-contained.
Do NOT import from any shared module (_caitl_v3, _shared, _common, etc.).
All scoring logic must exist within the single file.
Violation of this constraint = automatic rejection.
```

---

## Phase 6: Arcanum Revival (Day 4-5 — 4-6 hours)

**Impact: Revives the most unique exploration channel in Prometheus**

### 6.1 Minimal Revival: Passive Waste Stream Sampling

Don't rebuild the full Arcanum pipeline. Instead, add a lightweight hook to Ignis:

```python
# In analysis_base.py, after every forward pass:
def sample_waste_stream(model, prompt, layer, top_k=25):
    """Capture the logit shadow — top-k alternative tokens at the output layer."""
    logits = model(prompt).logits[0, -1, :]
    top_values, top_indices = torch.topk(logits, top_k)
    tokens = [model.tokenizer.decode(idx) for idx in top_indices]
    return {
        "prompt": prompt,
        "layer": layer,
        "top_tokens": list(zip(tokens, top_values.tolist())),
        "timestamp": datetime.now().isoformat()
    }
```

Every Ignis run captures 25 alternative tokens at the output layer. Deposit as Aletheia entities with `entity_type = "waste_stream_sample"`. Over time, patterns emerge.

### 6.2 Classification Without Full Pipeline

Use a simple heuristic for specimen classification:
- **ECHO**: Top alternative tokens are semantically similar to the chosen token (NCD < 0.3)
- **COLLISION**: Top alternatives come from completely different semantic domains
- **TRUE_ARCANUM**: Alternatives form a coherent cluster that has no obvious relationship to the prompt
- **CHIMERA**: Mix of echo and collision patterns

This is rough but it starts populating the Xenolexicon immediately.

### 6.3 Failed Forges → Arcanum

Route Hephaestus scrap/ to Arcanum classification:
```python
# In hephaestus.py, when a tool is scrapped:
deposit_entity(
    name=combo_key,
    entity_type="xenolexicon_specimen",
    source_agent="hephaestus_scrap",
    metadata={
        "failure_reason": reason,
        "concepts": concept_names,
        "specimen_class": classify_failure(reason),  # ECHO if "just NCD", COLLISION if "concepts don't combine"
    }
)
```

The scrap pile IS Arcanum's source material. The Constitution already says this.

---

## Phase 7: Nous → Aletheia Connection (Day 5-6 — 3-4 hours)

**Impact: Concept mining evolves with the substrate instead of using a static dictionary**

### 7.1 Dynamic Concept Dictionary

Instead of the static 95-concept list in `concepts.py`:

```python
def get_concepts():
    """Pull concepts from Aletheia's living knowledge graph."""
    db = sqlite3.connect(ALETHEIA_DB)

    # Core dictionary (always included)
    core = load_static_concepts()  # The existing 95

    # Dynamic additions from Aletheia
    techniques = db.execute(
        "SELECT name FROM entities WHERE entity_type = 'technique' AND evidence_grade != 'retracted'"
    ).fetchall()

    # Gap-driven concepts (things we DON'T know about)
    gaps = db.execute(
        "SELECT category FROM gaps WHERE resolved_at IS NULL"
    ).fetchall()

    return core + [t[0] for t in techniques] + [f"gap:{g[0]}" for g in gaps]
```

Gap-prefixed concepts tell Nous to specifically generate combinations that might fill known substrate holes.

---

## Implementation Timeline

| Day | Phase | Effort | Laws Enforced | Absorption Debt |
|-----|-------|--------|---------------|-----------------|
| 1 | Phase 1: Blocking gate + ingest module | 3h | 1, 2, 3, 4 | 16 |
| 1-2 | Phase 2: Schema expansion | 2h | 2 (4 concepts absorbed) | 12 |
| 2-3 | Phase 3: Pronoia constitutional checks | 4h | 1, 2, 4, 5 | 12 |
| 3-5 | Phase 4: Auto-extraction hooks | 5h | 3 | 10 |
| 3 | Phase 5: Dedup gate | 2h | 5 | 10 |
| 4-5 | Phase 6: Arcanum revival (passive) | 5h | 2 (3 concepts absorbed) | 7 |
| 5-6 | Phase 7: Nous → Aletheia | 3h | 3, 4 | 7 |
| **Total** | | **~24h** | **All 7 laws** | **16 → 7** |

---

## What Changes After This

**Before enforcement:**
- James runs an experiment → gets a number → moves to next experiment
- Substrate grows when James feels guilty
- Archived concepts stay archived
- Tools clone without detection
- Pronoia reports but doesn't enforce

**After enforcement:**
- James runs an experiment → script auto-deposits entities → substrate grows as side effect
- Pronoia gates GPU access if substrate hasn't grown
- Schema holds Xenolexicon specimens, evidence grades, gaps, and semantic relationships
- Dedup gate prevents monoculture
- Nous mines a living graph, not a static list
- Failed forges feed Arcanum automatically
- Every Ignis run captures waste stream samples

**The key insight:** None of this requires James to do more work. It requires the *code* to do more work. The experiments still run. The forge still hammers. But every action now deposits into the substrate as a side effect. The Constitution becomes a runtime property of the system, not a document James reads and feels bad about.

---

## The One Rule That Makes It All Work

```python
# In every batch script, every agent, every experiment runner:
# BEFORE the experiment starts:
from pronoia.gate import check_substrate_health
check_substrate_health()  # Blocks if substrate hasn't grown

# AFTER the experiment completes:
from aletheia.ingest import deposit_entity
deposit_entity(...)  # Auto-deposit results
```

Two lines of code per script. That's the enforcement gap closed.
