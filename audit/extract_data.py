"""
Aletheia Audit – Task 2: Export data samples as JSON
Reads from noesis_v2.duckdb (read-only) and writes to audit/data/
"""
import json, os, sys
from datetime import datetime, timezone

import duckdb

DB   = os.path.join(os.path.dirname(__file__), "..", "noesis", "v2", "noesis_v2.duckdb")
OUT  = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(OUT, exist_ok=True)

con = duckdb.connect(DB, read_only=True)

def export(filename: str, source_table: str, query: str):
    """Run query, write results to JSON with full provenance."""
    rows = con.execute(query).fetchall()
    cols = [d[0] for d in con.description]
    data = [dict(zip(cols, r)) for r in rows]
    # Convert non-serialisable types
    def _fix(v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v
    data = [{k: _fix(v) for k, v in row.items()} for row in data]
    payload = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "source_table": source_table,
        "query_used": query.strip(),
        "row_count": len(data),
        "rows": data,
    }
    path = os.path.join(OUT, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"  {filename}: {len(data)} rows")

print("=== Task 2: Exporting data samples ===\n")

# 1. CONCENTRATE spokes
q1 = """
SELECT * FROM composition_instances
WHERE notes ILIKE '%CONCENTRATE%'
ORDER BY instance_id
LIMIT 20
"""
export("sample_spokes_concentrate.json", "composition_instances", q1)

# 2. HIERARCHIZE spokes
q2 = """
SELECT * FROM composition_instances
WHERE notes ILIKE '%HIERARCHIZE%'
ORDER BY instance_id
LIMIT 20
"""
export("sample_spokes_hierarchize.json", "composition_instances", q2)

# 3. TRUNCATE spokes
q3 = """
SELECT * FROM composition_instances
WHERE notes ILIKE '%TRUNCATE%'
ORDER BY instance_id
LIMIT 20
"""
export("sample_spokes_truncate.json", "composition_instances", q3)

# 4. INVERT – ALL rows
q4 = """
SELECT * FROM composition_instances
WHERE notes ILIKE '%INVERT%'
ORDER BY instance_id
"""
export("sample_spokes_invert.json", "composition_instances", q4)

# 5. 50 edges, computed_similarity, sorted by edge_id DESC
q5 = """
SELECT * FROM cross_domain_edges
WHERE edge_type = 'computed_similarity'
ORDER BY edge_id DESC
LIMIT 50
"""
export("sample_edges.json", "cross_domain_edges", q5)

# 6. 20 diverse traditions excluding MAP-only vectors
q6 = """
SELECT * FROM ethnomathematics
WHERE enriched_primitive_vector NOT IN ('[["MAP", 1.0]]', '[["MAP", 0.1]]')
ORDER BY md5(system_id)          -- pseudo-random but deterministic diversity
LIMIT 20
"""
export("sample_traditions.json", "ethnomathematics", q6)

# 7. 20 hubs sorted by chain_count DESC
q7 = """
SELECT * FROM abstract_compositions
ORDER BY chain_count DESC
LIMIT 20
"""
export("sample_hubs.json", "abstract_compositions", q7)

# 8. ALL discoveries
q8 = """
SELECT * FROM discoveries
ORDER BY discovery_id
"""
export("sample_predictions.json", "discoveries", q8)

# 9. Fill-rate computation
q9_cells = """
SELECT shared_damage_operator AS operator,
       source_resolution_id,
       target_resolution_id,
       COUNT(*) AS edge_count
FROM cross_domain_edges
GROUP BY shared_damage_operator, source_resolution_id, target_resolution_id
"""

q9_operator_hub = """
SELECT shared_damage_operator AS operator,
       COUNT(*) AS edge_count
FROM cross_domain_edges
GROUP BY shared_damage_operator
ORDER BY shared_damage_operator
"""

q9_hub_count = """
SELECT COUNT(*) AS hub_count FROM abstract_compositions
"""

q9_ci_count = """
SELECT COUNT(*) AS ci_count FROM composition_instances
"""

q9_thm_count = """
SELECT COUNT(*) AS thm_count FROM tradition_hub_matrix
"""

q9_thm_filled = """
SELECT COUNT(*) AS filled
FROM tradition_hub_matrix
WHERE status IS NOT NULL AND status != ''
"""

# Build the fill-rate object manually
operator_hub_rows = con.execute(q9_operator_hub).fetchall()
hub_count = con.execute(q9_hub_count).fetchone()[0]
ci_count  = con.execute(q9_ci_count).fetchone()[0]
thm_count = con.execute(q9_thm_count).fetchone()[0]
thm_filled = con.execute(q9_thm_filled).fetchone()[0]

total_possible_cells = 9 * hub_count
actual_edges = sum(r[1] for r in operator_hub_rows)
fill_rate = actual_edges / total_possible_cells if total_possible_cells else 0

# Also compute the 99.4% fill rate from composition_instances
# This is likely: distinct (comp_id, tradition) pairs vs total possible
q9_ci_distinct = """
SELECT COUNT(DISTINCT comp_id || '||' || COALESCE(tradition,'')) AS filled_pairs
FROM composition_instances
"""
ci_filled = con.execute(q9_ci_distinct).fetchone()[0]

# tradition_hub_matrix fill rate
thm_fill_rate = thm_filled / thm_count if thm_count else 0

fill_payload = {
    "exported_at": datetime.now(timezone.utc).isoformat(),
    "source_table": "cross_domain_edges + abstract_compositions + composition_instances + tradition_hub_matrix",
    "queries_used": {
        "operator_hub_breakdown": q9_operator_hub.strip(),
        "hub_count": q9_hub_count.strip(),
        "ci_count": q9_ci_count.strip(),
        "thm_count": q9_thm_count.strip(),
        "thm_filled": q9_thm_filled.strip(),
        "ci_distinct_pairs": q9_ci_distinct.strip(),
    },
    "row_count": len(operator_hub_rows),
    "rows": [{"operator": r[0], "edge_count": r[1]} for r in operator_hub_rows],
    "computation": {
        "hub_count": hub_count,
        "operator_count": 9,
        "total_possible_cells_9xhubs": total_possible_cells,
        "actual_edge_count": actual_edges,
        "edge_fill_rate": round(fill_rate, 4),
        "composition_instances_count": ci_count,
        "composition_instances_distinct_comp_tradition_pairs": ci_filled,
        "tradition_hub_matrix_total_rows": thm_count,
        "tradition_hub_matrix_filled_rows": thm_filled,
        "tradition_hub_matrix_fill_rate": round(thm_fill_rate, 4),
        "note": "The 99.4% figure likely refers to tradition_hub_matrix fill rate"
    },
}
path = os.path.join(OUT, "fill_rate_computation.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(fill_payload, f, indent=2, default=str)
print(f"  fill_rate_computation.json: {len(operator_hub_rows)} operator rows")

# 10. Hit-rate computation – ALL discoveries with classification and verification
q10 = """
SELECT discovery_id,
       hub_id,
       damage_operator,
       resolution_name,
       description,
       discovery_method,
       tensor_score,
       tensor_rebuild_number,
       verification_status,
       verified_as,
       timestamp
FROM discoveries
ORDER BY discovery_id
"""
rows10 = con.execute(q10).fetchall()
cols10 = [d[0] for d in con.description]
data10 = [dict(zip(cols10, r)) for r in rows10]

# Compute hit-rate summary
status_counts = {}
for r in data10:
    s = r["verification_status"]
    status_counts[s] = status_counts.get(s, 0) + 1

hit_payload = {
    "exported_at": datetime.now(timezone.utc).isoformat(),
    "source_table": "discoveries",
    "query_used": q10.strip(),
    "row_count": len(data10),
    "rows": data10,
    "verification_summary": {
        "total_discoveries": len(data10),
        "status_breakdown": status_counts,
        "verified_exact_count": status_counts.get("VERIFIED_EXACT", 0),
        "verified_partial_count": status_counts.get("VERIFIED_PARTIAL", 0),
        "not_verified_count": status_counts.get("NOT_VERIFIED", 0),
        "hit_rate_exact": round(status_counts.get("VERIFIED_EXACT", 0) / len(data10), 4) if data10 else 0,
        "hit_rate_any_verified": round(
            (status_counts.get("VERIFIED_EXACT", 0) + status_counts.get("VERIFIED_PARTIAL", 0)) / len(data10), 4
        ) if data10 else 0,
    },
}
path = os.path.join(OUT, "hit_rate_computation.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(hit_payload, f, indent=2, default=str)
print(f"  hit_rate_computation.json: {len(data10)} rows")

con.close()
print("\nDone.")
