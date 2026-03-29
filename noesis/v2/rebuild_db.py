"""
Noesis v2 — Rebuild DuckDB from clean exported JSON.

Usage:
    cd F:/prometheus
    python noesis/v2/rebuild_db.py

Reads from: noesis/v2/export/*.json (9 files, ~1MB total)
Writes to:  noesis/v2/noesis_v2.duckdb (overwrites existing)

This is the disaster recovery and canonical rebuild script. The DuckDB file
is a derived artifact — this script produces it from the clean JSON exports.

Tables rebuilt:
    operations           - 1,714 typed mathematical operations from 191 fields
    chains               - 20 verified derivation chains (298 SymPy tests, 296 pass)
    chain_steps          - 80 steps within derivation chains
    transformations      - 60 typed edges using 11-primitive basis
    ethnomathematics     - 153 cross-cultural mathematical systems from 71 traditions
    abstract_compositions - 30 impossibility theorem hubs
    composition_instances - 147 resolution spokes (damage allocation strategies)
    damage_operators     - 7 second-order operators (how impossibilities get resolved)
    cross_domain_links   - 185 typed edges connecting resolutions across domains

Total: 2,396 rows

The 11-primitive basis:
    COMPOSE, MAP, EXTEND, REDUCE, LIMIT, DUALIZE,
    LINEARIZE, STOCHASTICIZE, SYMMETRIZE, BREAK_SYMMETRY, COMPLETE

The 7 damage operators:
    DISTRIBUTE, CONCENTRATE, TRUNCATE, EXTEND,
    RANDOMIZE, HIERARCHIZE, PARTITION

Created: 2026-03-29 (Aletheia's first session)
Verified: rebuild tested — produces identical database from exports
"""
import duckdb, json, sys, os
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = Path("noesis/v2/noesis_v2.duckdb")
EXPORT_DIR = Path("noesis/v2/export")

SCHEMA = {
    "operations": """
        CREATE TABLE operations (
            op_id VARCHAR PRIMARY KEY, field VARCHAR NOT NULL, op_name VARCHAR NOT NULL,
            input_type VARCHAR, output_type VARCHAR, description VARCHAR,
            primary_primitive VARCHAR, secondary_primitive VARCHAR,
            created_at TIMESTAMP DEFAULT current_timestamp
        )""",
    "chains": """
        CREATE TABLE chains (
            chain_id VARCHAR PRIMARY KEY, name VARCHAR NOT NULL, domain_tags VARCHAR,
            invariants VARCHAR, destroyed VARCHAR, failure_mode VARCHAR,
            source VARCHAR DEFAULT 'council', verified BOOLEAN DEFAULT false,
            test_count INTEGER DEFAULT 0, pass_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT current_timestamp
        )""",
    "chain_steps": """
        CREATE TABLE chain_steps (
            step_id VARCHAR PRIMARY KEY, chain_id VARCHAR NOT NULL,
            step_order INTEGER NOT NULL, label VARCHAR, content VARCHAR,
            structure_type VARCHAR
        )""",
    "transformations": """
        CREATE TABLE transformations (
            transform_id VARCHAR PRIMARY KEY, chain_id VARCHAR NOT NULL,
            from_step VARCHAR NOT NULL, to_step VARCHAR NOT NULL,
            primitive_type VARCHAR NOT NULL, ontology_type VARCHAR,
            operation_desc VARCHAR, invertible BOOLEAN DEFAULT false,
            structure_preserved VARCHAR, structure_destroyed VARCHAR
        )""",
    "ethnomathematics": """
        CREATE TABLE ethnomathematics (
            system_id VARCHAR PRIMARY KEY, tradition VARCHAR, system_name VARCHAR,
            region VARCHAR, period VARCHAR, description VARCHAR,
            key_operations VARCHAR, structural_features VARCHAR,
            candidate_primitives_council VARCHAR, unique_aspects VARCHAR,
            verification_difficulty VARCHAR, formalization_status VARCHAR,
            open_questions VARCHAR, candidate_primitives_noesis VARCHAR,
            classification_agreement BOOLEAN DEFAULT NULL,
            composition_mode VARCHAR
        )""",
    "abstract_compositions": """
        CREATE TABLE abstract_compositions (
            comp_id VARCHAR PRIMARY KEY, primitive_sequence VARCHAR NOT NULL,
            description VARCHAR, structural_pattern VARCHAR,
            chain_count INTEGER DEFAULT 0
        )""",
    "composition_instances": """
        CREATE TABLE composition_instances (
            instance_id VARCHAR PRIMARY KEY, comp_id VARCHAR NOT NULL,
            system_id VARCHAR, tradition VARCHAR, domain VARCHAR, notes VARCHAR
        )""",
    "damage_operators": """
        CREATE TABLE damage_operators (
            operator_id VARCHAR PRIMARY KEY, name VARCHAR NOT NULL,
            meaning VARCHAR, primitive_form VARCHAR,
            canonical_form VARCHAR, examples VARCHAR
        )""",
    "cross_domain_links": """
        CREATE TABLE cross_domain_links (
            link_id VARCHAR PRIMARY KEY, source_resolution VARCHAR NOT NULL,
            source_hub VARCHAR NOT NULL, target_hub VARCHAR,
            target_resolution VARCHAR, link_type VARCHAR DEFAULT 'analog',
            damage_operator VARCHAR, notes VARCHAR
        )""",
}

def rebuild():
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"[REBUILD] Removed old database")

    db = duckdb.connect(str(DB_PATH))

    # Create tables
    for table, ddl in SCHEMA.items():
        db.execute(ddl)
        print(f"[SCHEMA] Created {table}")

    # Load data
    total = 0
    for table in SCHEMA:
        json_path = EXPORT_DIR / f"{table}.json"
        if not json_path.exists():
            print(f"[WARN] Missing {json_path}, skipping")
            continue

        data = json.loads(json_path.read_text(encoding='utf-8'))
        if not data:
            continue

        cols = list(data[0].keys())
        # Filter to only columns that exist in schema
        schema_cols = [c[0] for c in db.execute(f"DESCRIBE {table}").fetchall()]
        cols = [c for c in cols if c in schema_cols]

        placeholders = ", ".join(["?" for _ in cols])
        col_names = ", ".join(cols)

        for row in data:
            values = []
            for c in cols:
                v = row.get(c)
                if v == "None" or v == "null":
                    v = None
                values.append(v)
            try:
                db.execute(f"INSERT OR REPLACE INTO {table} ({col_names}) VALUES ({placeholders})", values)
            except Exception as e:
                print(f"[ERROR] {table}: {e}")

        total += len(data)
        print(f"[LOAD] {table:30s} {len(data):6d} rows")

    db.commit()
    db.close()
    print(f"\n[DONE] Rebuilt {DB_PATH} with {total} total rows")
    print(f"       Size: {DB_PATH.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    rebuild()
