"""
Aletheia Ingest Module — Constitutional Substrate Deposition

Every Prometheus agent calls these functions to deposit into the knowledge graph.
This is the enforcement mechanism for Law 1 ("The Substrate Is the Product") and
Law 3 ("Every Agent Feeds the Substrate").

Usage:
    from aletheia.ingest import deposit_entity, deposit_relationship, deposit_gap, get_substrate_health

    # Deposit an entity
    eid = deposit_entity("chaos_theory_x_fep", "forge_tool", "hephaestus",
                         metadata={"accuracy": 0.67}, evidence_grade="replicated")

    # Deposit a relationship
    deposit_relationship(eid, concept_id, "instantiates")

    # Record a gap (something the substrate doesn't know)
    deposit_gap("temporal_ordering", "unsearched", "No tools handle temporal ordering traps")

    # Check substrate health (for the constitutional gate)
    health = get_substrate_health(hours=24)
    # Returns: {"entities": 12, "relationships": 25, "gaps": 3}
"""

import json
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Find the Aletheia DB relative to this file
_THIS_DIR = Path(__file__).resolve().parent
DB_PATH = _THIS_DIR.parent / "data" / "knowledge_graph.db"


def _get_db():
    """Get a WAL-mode SQLite connection."""
    db = sqlite3.connect(str(DB_PATH))
    db.execute("PRAGMA journal_mode=WAL")
    return db


def _ensure_tables():
    """Create the constitutional tables if they don't exist yet."""
    db = _get_db()

    # Substrate growth tracking table
    db.execute("""
        CREATE TABLE IF NOT EXISTS substrate_entities (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            source_agent TEXT NOT NULL,
            metadata    TEXT DEFAULT '{}',
            evidence_grade TEXT DEFAULT 'preliminary',
            specimen_class TEXT,
            provenance  TEXT DEFAULT 'evaluation',
            created_at  TEXT NOT NULL,
            updated_at  TEXT,
            UNIQUE(name, entity_type)
        )
    """)

    # Relationships between entities
    db.execute("""
        CREATE TABLE IF NOT EXISTS substrate_relationships (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_a_id INTEGER NOT NULL,
            entity_b_id INTEGER NOT NULL,
            rel_type    TEXT NOT NULL,
            evidence_grade TEXT DEFAULT 'preliminary',
            metadata    TEXT DEFAULT '{}',
            created_at  TEXT NOT NULL,
            UNIQUE(entity_a_id, entity_b_id, rel_type)
        )
    """)

    # Gaps — what the substrate doesn't know
    db.execute("""
        CREATE TABLE IF NOT EXISTS substrate_gaps (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            category    TEXT NOT NULL,
            gap_type    TEXT NOT NULL,
            description TEXT,
            discovered_by TEXT DEFAULT 'unknown',
            created_at  TEXT NOT NULL,
            resolved_at TEXT
        )
    """)

    db.commit()
    db.close()


# Ensure tables exist on import
_ensure_tables()


def deposit_entity(name, entity_type, source_agent, metadata=None, evidence_grade="preliminary",
                   specimen_class=None, provenance="evaluation"):
    """
    Insert or update an entity in the substrate. Returns entity_id.
    Idempotent on (name, entity_type) — updates metadata if entity exists.

    entity_type: paper | technique | forge_tool | forge_failure | experiment_result |
                 concept | reasoning_failure | verified_reasoning | waste_stream_sample |
                 xenolexicon_specimen | metis_finding | research_alignment | briefing_finding
    evidence_grade: preliminary | replicated | contradicted | formally_proven | retracted
    specimen_class: null | true_arcanum | collision | echo | chimera
    provenance: evaluation | training | adversarial
    """
    db = _get_db()
    now = datetime.now().isoformat()
    meta_json = json.dumps(metadata or {})

    existing = db.execute(
        "SELECT id FROM substrate_entities WHERE name = ? AND entity_type = ?",
        [name, entity_type]
    ).fetchone()

    if existing:
        db.execute(
            "UPDATE substrate_entities SET metadata = ?, evidence_grade = ?, updated_at = ? WHERE id = ?",
            [meta_json, evidence_grade, now, existing[0]]
        )
        db.commit()
        db.close()
        return existing[0]

    db.execute(
        """INSERT INTO substrate_entities
           (name, entity_type, source_agent, metadata, evidence_grade, specimen_class, provenance, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        [name, entity_type, source_agent, meta_json, evidence_grade, specimen_class, provenance, now]
    )
    db.commit()
    entity_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    db.close()
    return entity_id


def deposit_relationship(entity_a_id, entity_b_id, rel_type, evidence_grade="preliminary", metadata=None):
    """
    Insert a relationship between two substrate entities.

    rel_type: bridges | subsumes | contradicts | extends | instantiates |
              drives | synergizes | handles | describes | produces
    """
    db = _get_db()
    now = datetime.now().isoformat()
    try:
        db.execute(
            """INSERT OR IGNORE INTO substrate_relationships
               (entity_a_id, entity_b_id, rel_type, evidence_grade, metadata, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            [entity_a_id, entity_b_id, rel_type, evidence_grade, json.dumps(metadata or {}), now]
        )
        db.commit()
    finally:
        db.close()


def deposit_gap(category, gap_type, description, discovered_by="unknown"):
    """
    Record something the substrate doesn't know.

    gap_type: unsearched | under_described | unstable | infeasible
    """
    db = _get_db()
    now = datetime.now().isoformat()
    try:
        db.execute(
            "INSERT INTO substrate_gaps (category, gap_type, description, discovered_by, created_at) VALUES (?, ?, ?, ?, ?)",
            [category, gap_type, description, discovered_by, now]
        )
        db.commit()
    finally:
        db.close()


def resolve_gap(gap_id):
    """Mark a gap as resolved."""
    db = _get_db()
    now = datetime.now().isoformat()
    try:
        db.execute("UPDATE substrate_gaps SET resolved_at = ? WHERE id = ?", [now, gap_id])
        db.commit()
    finally:
        db.close()


def get_substrate_health(hours=24):
    """
    Returns substrate growth metrics for the constitutional gate.

    Returns dict with entities, relationships, gaps added in the last N hours.
    """
    db = _get_db()
    since = (datetime.now() - timedelta(hours=hours)).isoformat()
    try:
        entities = db.execute(
            "SELECT COUNT(*) FROM substrate_entities WHERE created_at > ?", [since]
        ).fetchone()[0]
        relationships = db.execute(
            "SELECT COUNT(*) FROM substrate_relationships WHERE created_at > ?", [since]
        ).fetchone()[0]
        gaps = db.execute(
            "SELECT COUNT(*) FROM substrate_gaps WHERE created_at > ?", [since]
        ).fetchone()[0]
        total_entities = db.execute("SELECT COUNT(*) FROM substrate_entities").fetchone()[0]
        total_relationships = db.execute("SELECT COUNT(*) FROM substrate_relationships").fetchone()[0]
        total_gaps = db.execute(
            "SELECT COUNT(*) FROM substrate_gaps WHERE resolved_at IS NULL"
        ).fetchone()[0]
        return {
            "entities_24h": entities,
            "relationships_24h": relationships,
            "gaps_24h": gaps,
            "total_entities": total_entities,
            "total_relationships": total_relationships,
            "open_gaps": total_gaps,
        }
    finally:
        db.close()


def check_constitutional_gate(force=False):
    """
    Check if substrate has grown enough to allow GPU experiments.
    Returns True if gate passes, False if blocked.

    Called by batch scripts before GPU work starts.
    """
    health = get_substrate_health(hours=24)
    total_24h = health["entities_24h"] + health["relationships_24h"] + health["gaps_24h"]

    if total_24h >= 5 or force:
        if force and total_24h < 5:
            # Log the override
            deposit_entity("gate_override", "constitutional_event", "pronoia",
                           metadata={"reason": "manual override", "health": health})
        return True

    print("=" * 60)
    print("CONSTITUTIONAL GATE — SUBSTRATE STARVATION")
    print(f"  Last 24h: {health['entities_24h']} entities, "
          f"{health['relationships_24h']} relationships, "
          f"{health['gaps_24h']} gaps")
    print(f"  Total needed: 5 (any combination)")
    print(f"  Total substrate: {health['total_entities']} entities, "
          f"{health['total_relationships']} relationships, "
          f"{health['open_gaps']} open gaps")
    print()
    print("  Law 1: The substrate is the product.")
    print("  Run the intelligence pipeline before GPU experiments.")
    print("  Override: pass force=True or --force-gate")
    print("=" * 60)
    return False


# CLI interface for health checks
if __name__ == "__main__":
    if "--health-check" in sys.argv:
        health = get_substrate_health()
        print(json.dumps(health, indent=2))
        total = health["entities_24h"] + health["relationships_24h"] + health["gaps_24h"]
        sys.exit(0 if total >= 5 else 1)
    elif "--gate" in sys.argv:
        force = "--force" in sys.argv
        passed = check_constitutional_gate(force=force)
        sys.exit(0 if passed else 1)
    else:
        print("Usage:")
        print("  python ingest.py --health-check   # Print substrate health")
        print("  python ingest.py --gate            # Check constitutional gate")
        print("  python ingest.py --gate --force    # Override gate")
