"""
Noesis v2 — Typed Chain Search

Given two operations in different domains, find:
1. Known paths through the derivation graph (verified bridges)
2. Type-compatible but unverified paths (composition candidates)
3. Primitive sequence templates that match (pattern-based discovery)

The gap between "type-compatible" and "verified" is the search space.
That's where discovery happens.
"""

import duckdb
import sys
from pathlib import Path
from collections import defaultdict
from itertools import product as iterproduct

sys.stdout.reconfigure(encoding='utf-8')

V2_DIR = Path(__file__).resolve().parent
DB_PATH = V2_DIR / "noesis_v2.duckdb"

# Composition pattern templates (verified search patterns)
COMPOSITION_TEMPLATES = [
    # (name, primitive_sequence, description)
    ("quantization", ["MAP", "EXTEND"], "Classical → quantum"),
    ("variational", ["EXTEND", "REDUCE", "LIMIT"], "All paths → extremum → δ→0"),
    ("renormalization", ["REDUCE", "MAP", "LIMIT"], "Coarse-grain → rescale → fixed point"),
    ("discretization", ["REDUCE", "BREAK_SYMMETRY"], "Continuous → finite grid"),
    ("fourier_analysis", ["DUALIZE", "MAP"], "Transform → operate in dual"),
    ("linear_stability", ["LINEARIZE", "MAP"], "Approximate → eigenanalyze"),
    ("gauge_theory", ["EXTEND", "SYMMETRIZE"], "Enlarge → constrain"),
    ("ssb", ["SYMMETRIZE", "BREAK_SYMMETRY"], "Define symmetry → break it"),
    ("perturbation", ["LINEARIZE", "EXTEND"], "Approximate → series expand"),
    ("equilibrium", ["STOCHASTICIZE", "LIMIT"], "Noise → settle"),
    ("path_integral", ["STOCHASTICIZE", "REDUCE"], "Sum over paths → average"),
    ("representation", ["MAP", "SYMMETRIZE"], "Represent → find invariants"),
    ("compactification", ["EXTEND", "COMPLETE"], "Embed → close"),
    ("renormalization_group", ["REDUCE", "MAP"], "Coarse-grain → rescale"),
]


def connect():
    return duckdb.connect(str(DB_PATH), read_only=True)


def find_type_compatible_bridges(db, source_field=None, target_field=None, limit=20):
    """Find operations in different fields with compatible I/O types."""
    where_clause = "WHERE o1.field != o2.field AND o1.output_type = o2.input_type"
    params = []
    if source_field:
        where_clause += " AND o1.field = ?"
        params.append(source_field)
    if target_field:
        where_clause += " AND o2.field = ?"
        params.append(target_field)

    query = f"""
        SELECT o1.field, o1.op_name, o1.output_type,
               o2.field, o2.op_name, o2.input_type,
               o1.primary_primitive, o2.primary_primitive
        FROM operations o1
        JOIN operations o2 ON o1.output_type = o2.input_type
            AND o1.field != o2.field
        {where_clause.replace("WHERE o1.field != o2.field AND o1.output_type = o2.input_type AND", "AND") if params else ""}
        ORDER BY o1.field, o2.field
        LIMIT {limit}
    """

    # Simpler approach
    if source_field and target_field:
        results = db.execute("""
            SELECT o1.field, o1.op_name, o1.output_type,
                   o2.field, o2.op_name, o2.input_type,
                   o1.primary_primitive, o2.primary_primitive
            FROM operations o1
            JOIN operations o2 ON o1.output_type = o2.input_type
            WHERE o1.field = ? AND o2.field = ?
            LIMIT ?
        """, [source_field, target_field, limit]).fetchall()
    elif source_field:
        results = db.execute("""
            SELECT o1.field, o1.op_name, o1.output_type,
                   o2.field, o2.op_name, o2.input_type,
                   o1.primary_primitive, o2.primary_primitive
            FROM operations o1
            JOIN operations o2 ON o1.output_type = o2.input_type
            WHERE o1.field = ? AND o1.field != o2.field
            LIMIT ?
        """, [source_field, limit]).fetchall()
    else:
        results = db.execute("""
            SELECT o1.field, o1.op_name, o1.output_type,
                   o2.field, o2.op_name, o2.input_type,
                   o1.primary_primitive, o2.primary_primitive
            FROM operations o1
            JOIN operations o2 ON o1.output_type = o2.input_type
            WHERE o1.field != o2.field
            ORDER BY RANDOM()
            LIMIT ?
        """, [limit]).fetchall()

    return results


def match_composition_templates(source_primitive, target_primitive):
    """Find composition templates whose primitive sequence starts with source
    and ends with target."""
    matches = []
    for name, seq, desc in COMPOSITION_TEMPLATES:
        if seq[0] == source_primitive or seq[-1] == target_primitive:
            matches.append((name, seq, desc))
        # Also match if the pair appears consecutively anywhere in the sequence
        for i in range(len(seq) - 1):
            if seq[i] == source_primitive and seq[i+1] == target_primitive:
                matches.append((name, seq, desc))
                break
    return matches


def find_cross_domain_candidates(db, max_results=50):
    """Find the most promising cross-domain composition candidates.

    Scoring: higher score for pairs where:
    - The primitive types match a known composition template
    - The domains are maximally distant (different fields)
    - The type signatures chain cleanly
    """
    # Get random type-compatible pairs
    pairs = db.execute("""
        SELECT o1.field, o1.op_name, o1.output_type,
               o2.field, o2.op_name, o2.input_type,
               o1.primary_primitive as p1, o2.primary_primitive as p2,
               o1.description as d1, o2.description as d2
        FROM operations o1
        JOIN operations o2 ON o1.output_type = o2.input_type
        WHERE o1.field != o2.field
        ORDER BY RANDOM()
        LIMIT 5000
    """).fetchall()

    scored = []
    for row in pairs:
        f1, op1, out_t, f2, op2, in_t, p1, p2, d1, d2 = row
        templates = match_composition_templates(p1, p2)
        if templates:
            score = len(templates)  # More template matches = more promising
            scored.append({
                "source": f"{f1}.{op1}",
                "target": f"{f2}.{op2}",
                "type_bridge": f"{out_t} → {in_t}",
                "primitives": f"{p1} → {p2}",
                "templates": [(t[0], t[2]) for t in templates],
                "score": score,
                "source_desc": d1[:60] if d1 else "",
                "target_desc": d2[:60] if d2 else "",
            })

    scored.sort(key=lambda x: -x["score"])
    return scored[:max_results]


def domain_connectivity_matrix(db):
    """Show which domains have type-compatible connections."""
    results = db.execute("""
        SELECT o1.field as source, o2.field as target, COUNT(*) as bridges
        FROM operations o1
        JOIN operations o2 ON o1.output_type = o2.input_type
        WHERE o1.field != o2.field
        GROUP BY o1.field, o2.field
        HAVING COUNT(*) >= 5
        ORDER BY bridges DESC
        LIMIT 30
    """).fetchall()
    return results


def main():
    db = connect()

    print("=" * 70)
    print("NOESIS v2 — TYPED CHAIN SEARCH")
    print("=" * 70)

    # 1. Domain connectivity
    print("\n--- TOP CROSS-DOMAIN CONNECTIONS (by type-compatible pairs) ---\n")
    conns = domain_connectivity_matrix(db)
    for src, tgt, count in conns[:15]:
        print(f"  {src:35s} → {tgt:35s}  ({count} bridges)")

    # 2. Composition candidates
    print("\n--- TOP COMPOSITION CANDIDATES (template-matched) ---\n")
    candidates = find_cross_domain_candidates(db, max_results=20)
    for c in candidates:
        templates = ", ".join(t[0] for t in c["templates"])
        print(f"  [{c['score']}] {c['source']:50s} → {c['target']}")
        print(f"       Primitives: {c['primitives']}  |  Templates: {templates}")
        print(f"       {c['source_desc']}")
        print(f"       → {c['target_desc']}")
        print()

    # 3. Specific cross-domain probe
    print("\n--- PROBE: feynman_diagram_algebra → topology ---\n")
    bridges = find_type_compatible_bridges(db, "feynman_diagram_algebra", "topological_data_analysis", limit=10)
    if bridges:
        for b in bridges:
            print(f"  {b[0]}.{b[1]} ({b[6]}) --[{b[2]}]--> {b[3]}.{b[4]} ({b[7]})")
    else:
        print("  No direct type-compatible bridges found.")

    # 4. Statistics
    print("\n--- SEARCH SPACE ---\n")
    r = db.execute("""
        SELECT COUNT(*)
        FROM operations o1
        JOIN operations o2 ON o1.output_type = o2.input_type
        WHERE o1.field != o2.field
    """).fetchone()
    print(f"  Total type-compatible cross-domain pairs: {r[0]}")

    r = db.execute("SELECT COUNT(*) FROM transformations").fetchone()
    print(f"  Verified typed edges: {r[0]}")
    print(f"  Composition search space: {int(r[0])} verified / ~{int(r[0])*100} potential")

    db.close()


if __name__ == "__main__":
    main()
