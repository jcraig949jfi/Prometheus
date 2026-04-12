"""
Aletheia Audit – Task 3: Database summary reports
Reads from noesis_v2.duckdb (read-only) and writes to audit/reports/
"""
import json, os, re
from datetime import datetime, timezone

import duckdb

DB   = os.path.join(os.path.dirname(__file__), "..", "noesis", "v2", "noesis_v2.duckdb")
OUT  = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(OUT, exist_ok=True)

con = duckdb.connect(DB, read_only=True)

def _ser(v):
    """Make any value JSON-serialisable."""
    if isinstance(v, datetime):
        return v.isoformat()
    return v

def write_json(filename, payload):
    path = os.path.join(OUT, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"  wrote {filename}")

# ── Report 1: Table inventory ──────────────────────────────────────────────
print("=== Report 1: Table inventory ===")

tables = [r[0] for r in con.execute("SHOW TABLES").fetchall()]
inventory = {}

for tbl in tables:
    q_count = f"SELECT COUNT(*) FROM {tbl}"
    row_count = con.execute(q_count).fetchone()[0]

    cols_info = con.execute(f"DESCRIBE {tbl}").fetchall()
    col_names = [c[0] for c in cols_info]

    q_sample = f"SELECT * FROM {tbl} LIMIT 3"
    sample_rows = con.execute(q_sample).fetchall()
    sample = [
        {col: _ser(val) for col, val in zip(col_names, row)}
        for row in sample_rows
    ]

    # NULL counts per column
    null_parts = ", ".join(
        f"SUM(CASE WHEN \"{c}\" IS NULL THEN 1 ELSE 0 END) AS \"{c}_nulls\""
        for c in col_names
    )
    q_nulls = f"SELECT {null_parts} FROM {tbl}"
    null_row = con.execute(q_nulls).fetchone()
    null_counts = {col_names[i]: int(null_row[i]) for i in range(len(col_names))}

    # Duplicate row count (rows where entire row appears more than once)
    all_cols = ", ".join(f'"{c}"' for c in col_names)
    q_dupes = f"""
        SELECT COALESCE(SUM(cnt - 1), 0) AS duplicate_rows
        FROM (
            SELECT {all_cols}, COUNT(*) AS cnt
            FROM {tbl}
            GROUP BY {all_cols}
            HAVING COUNT(*) > 1
        ) sub
    """
    dupe_count = con.execute(q_dupes).fetchone()[0]

    inventory[tbl] = {
        "row_count": row_count,
        "column_names": col_names,
        "sample_3_rows": sample,
        "null_counts_per_column": null_counts,
        "duplicate_row_count": int(dupe_count),
        "queries_used": {
            "count": q_count,
            "sample": q_sample,
            "nulls": q_nulls.strip(),
            "duplicates": q_dupes.strip(),
        },
    }

payload1 = {
    "exported_at": datetime.now(timezone.utc).isoformat(),
    "table_count": len(tables),
    "tables": inventory,
}
write_json("table_inventory.json", payload1)

# ── Report 2: Provenance report ───────────────────────────────────────────
print("\n=== Report 2: Provenance report ===")

# cross_domain_edges by provenance and edge_type
q_prov_edge = """
SELECT provenance, edge_type, COUNT(*) AS cnt
FROM cross_domain_edges
GROUP BY provenance, edge_type
ORDER BY cnt DESC
"""
prov_edge = con.execute(q_prov_edge).fetchall()

# Summarise provenance into categories (many are long strings)
q_prov_summary = """
SELECT
    CASE
        WHEN provenance = 'aletheia_overnight' THEN 'aletheia_overnight'
        WHEN provenance = 'aletheia_overnight_isolated' THEN 'aletheia_overnight_isolated'
        WHEN provenance = 'aletheia_manual' THEN 'aletheia_manual'
        WHEN provenance LIKE 'aletheia_tradition:%' THEN 'aletheia_tradition'
        ELSE 'other'
    END AS provenance_category,
    edge_type,
    COUNT(*) AS cnt
FROM cross_domain_edges
GROUP BY provenance_category, edge_type
ORDER BY cnt DESC
"""
prov_summary = con.execute(q_prov_summary).fetchall()

# composition_instances by tradition
q_ci_tradition = """
SELECT tradition, COUNT(*) AS cnt
FROM composition_instances
GROUP BY tradition
ORDER BY cnt DESC
"""
ci_tradition = con.execute(q_ci_tradition).fetchall()

# tradition_hub_matrix by source
q_thm_source = """
SELECT source, COUNT(*) AS cnt
FROM tradition_hub_matrix
GROUP BY source
ORDER BY cnt DESC
"""
thm_source = con.execute(q_thm_source).fetchall()

payload2 = {
    "exported_at": datetime.now(timezone.utc).isoformat(),
    "cross_domain_edges_provenance_summary": {
        "query": q_prov_summary.strip(),
        "rows": [{"provenance_category": r[0], "edge_type": r[1], "count": r[2]} for r in prov_summary],
    },
    "cross_domain_edges_provenance_full": {
        "query": q_prov_edge.strip(),
        "row_count": len(prov_edge),
        "rows": [{"provenance": r[0], "edge_type": r[1], "count": r[2]} for r in prov_edge],
    },
    "composition_instances_by_tradition": {
        "query": q_ci_tradition.strip(),
        "rows": [{"tradition": r[0], "count": r[1]} for r in ci_tradition],
    },
    "tradition_hub_matrix_by_source": {
        "query": q_thm_source.strip(),
        "rows": [{"source": r[0], "count": r[1]} for r in thm_source],
    },
}
write_json("provenance_report.json", payload2)

# ── Report 3: Operator statistics ─────────────────────────────────────────
print("\n=== Report 3: Operator statistics ===")

operators = [r[0] for r in con.execute("SELECT name FROM damage_operators ORDER BY name").fetchall()]

op_stats = {}
for op in operators:
    # Count in cross_domain_edges
    q_edge = f"SELECT COUNT(*) FROM cross_domain_edges WHERE shared_damage_operator = '{op}'"
    edge_cnt = con.execute(q_edge).fetchone()[0]

    # Count in composition_instances (grep notes for operator name)
    q_ci = f"SELECT COUNT(*) FROM composition_instances WHERE notes ILIKE '%{op}%'"
    ci_cnt = con.execute(q_ci).fetchone()[0]

    # Unique hubs in cross_domain_edges
    q_hubs_edge = f"""
    SELECT COUNT(DISTINCT hub) FROM (
        SELECT source_resolution_id AS hub FROM cross_domain_edges WHERE shared_damage_operator = '{op}'
        UNION
        SELECT target_resolution_id AS hub FROM cross_domain_edges WHERE shared_damage_operator = '{op}'
    )
    """
    hubs_edge = con.execute(q_hubs_edge).fetchone()[0]

    # Unique hubs in tradition_hub_matrix
    q_hubs_thm = f"SELECT COUNT(DISTINCT hub_id) FROM tradition_hub_matrix WHERE damage_operator = '{op}'"
    hubs_thm = con.execute(q_hubs_thm).fetchone()[0]

    # Top 5 keywords from composition_instances notes where this operator appears
    q_notes = f"SELECT notes FROM composition_instances WHERE notes ILIKE '%{op}%' LIMIT 200"
    notes_rows = con.execute(q_notes).fetchall()
    word_freq = {}
    stop = {"the","a","an","of","to","in","is","and","for","by","on","at","as","or","it","its","with","from","that","this","are","was","be","but","not","all","has","had","have","can","each","into","via","per","no","one","two","up"}
    for (note,) in notes_rows:
        if note:
            for w in re.findall(r"[a-z]{4,}", note.lower()):
                if w not in stop and w != op.lower():
                    word_freq[w] = word_freq.get(w, 0) + 1
    top5 = sorted(word_freq.items(), key=lambda x: -x[1])[:5]

    # Depth2 matrix count
    q_d2 = f"""
    SELECT COUNT(*) FROM depth2_matrix
    WHERE op1 = '{op}' OR op2 = '{op}'
    """
    d2_cnt = con.execute(q_d2).fetchone()[0]

    op_stats[op] = {
        "cross_domain_edges_count": edge_cnt,
        "composition_instances_count": ci_cnt,
        "unique_hubs_in_edges": hubs_edge,
        "unique_hubs_in_tradition_hub_matrix": hubs_thm,
        "depth2_matrix_appearances": d2_cnt,
        "top_5_keywords_in_notes": [{"word": w, "count": c} for w, c in top5],
        "queries_used": {
            "edges": q_edge,
            "composition_instances": q_ci,
            "unique_hubs_edges": q_hubs_edge.strip(),
            "unique_hubs_thm": q_hubs_thm,
            "depth2": q_d2.strip(),
        },
    }

payload3 = {
    "exported_at": datetime.now(timezone.utc).isoformat(),
    "operator_count": len(operators),
    "operators": op_stats,
}
write_json("operator_statistics.json", payload3)

con.close()
print("\nDone.")
