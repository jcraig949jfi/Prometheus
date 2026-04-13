"""
theorem_edges.py — Probe the boundaries of 7 verified theorems in LMFDB.
Interior = 100% verified. Edges = where theorems barely hold or predict unchecked territory.
"""

import json, math, time, sys
from pathlib import Path
from decimal import Decimal
from collections import Counter

import psycopg2
import psycopg2.extras

OUTFILE = Path(__file__).resolve().parent.parent / "results" / "theorem_edges.json"

def connect():
    return psycopg2.connect(
        host="devmirror.lmfdb.xyz", port=5432,
        user="lmfdb", password="lmfdb", dbname="lmfdb",
        connect_timeout=15,
        options="-c statement_timeout=30000"
    )

def dec(v):
    """Recursively convert Decimal/non-JSON types to float/str."""
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (list, tuple)):
        return [dec(x) for x in v]
    if isinstance(v, dict):
        return {k: dec(val) for k, val in v.items()}
    return v

def q(cur, sql, label=""):
    t0 = time.time()
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        elapsed = round(time.time() - t0, 2)
        print(f"  [{label}] {len(rows)} rows in {elapsed}s")
        return cols, [list(r) for r in rows]
    except Exception as e:
        print(f"  [{label}] ERROR: {e}")
        cur.connection.rollback()
        return [], []

def rows_to_dicts(cols, rows):
    return [dict(zip(cols, dec(r))) for r in rows]

# ─────────────────────────────────────────────────────────────
results = {}
conn = connect()
cur = conn.cursor()

# ═══════════════════════════════════════════════════════════════
# 1. MODULARITY EDGES
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("1. MODULARITY EDGES")
edge1 = {}

# Weight/dim distribution
cols, rows = q(cur,
    "SELECT weight, dim, COUNT(*) as cnt FROM mf_newforms GROUP BY weight, dim ORDER BY cnt DESC LIMIT 30",
    "weight_dim_dist")
edge1["weight_dim_distribution"] = rows_to_dicts(cols, rows)

# Non-EC newforms: weight>2 or dim>1
cols, rows = q(cur,
    "SELECT weight, dim, COUNT(*) FROM mf_newforms WHERE NOT (weight=2 AND dim=1) GROUP BY weight, dim ORDER BY COUNT(*) DESC LIMIT 20",
    "non_ec_newforms")
edge1["non_ec_newforms"] = rows_to_dicts(cols, rows)

# Total weight=2 dim=1 vs rest
cols, rows = q(cur,
    """SELECT
        SUM(CASE WHEN weight=2 AND dim=1 THEN 1 ELSE 0 END) as ec_like,
        SUM(CASE WHEN NOT (weight=2 AND dim=1) THEN 1 ELSE 0 END) as non_ec
    FROM mf_newforms""",
    "ec_vs_non_ec_count")
edge1["ec_vs_non_ec"] = rows_to_dicts(cols, rows)

# Simplest non-EC newform: lowest level, weight=2, dim=2
cols, rows = q(cur,
    "SELECT label, level, weight, dim, char_order, field_poly FROM mf_newforms WHERE weight=2 AND dim=2 ORDER BY level LIMIT 10",
    "simplest_abelian_variety")
edge1["simplest_dim2_weight2"] = rows_to_dicts(cols, rows)

# Weight 3,4 newforms — what are they?
cols, rows = q(cur,
    "SELECT label, level, weight, dim FROM mf_newforms WHERE weight > 2 ORDER BY level, weight LIMIT 15",
    "higher_weight")
edge1["higher_weight_examples"] = rows_to_dicts(cols, rows)

results["1_modularity_edges"] = edge1

# ═══════════════════════════════════════════════════════════════
# 2. PARITY EDGES
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("2. PARITY EDGES")
edge2 = {}

# Check what columns exist for sign/root number
cols, rows = q(cur,
    """SELECT column_name FROM information_schema.columns
       WHERE table_name='ec_curvedata' AND column_name IN
       ('rank','analytic_rank','root_number','signep','torsion','sha','regulator')
       ORDER BY column_name""",
    "ec_columns_check")
edge2["available_columns"] = rows_to_dicts(cols, rows)

# Rank distribution with root_number parity check
cols, rows = q(cur,
    """SELECT rank, COUNT(*) as cnt,
       SUM(CASE WHEN root_number = -1 THEN 1 ELSE 0 END) as root_neg1,
       SUM(CASE WHEN root_number = 1 THEN 1 ELSE 0 END) as root_pos1
    FROM ec_curvedata WHERE rank IS NOT NULL AND root_number IS NOT NULL
    GROUP BY rank ORDER BY rank""",
    "rank_vs_rootnumber")
edge2["rank_vs_root_number"] = rows_to_dicts(cols, rows)

# Parity check: rank even <=> root_number=+1, rank odd <=> root_number=-1
cols, rows = q(cur,
    """SELECT rank, root_number, COUNT(*)
    FROM ec_curvedata
    WHERE rank IS NOT NULL AND root_number IS NOT NULL
    GROUP BY rank, root_number
    ORDER BY rank, root_number""",
    "parity_full")
edge2["parity_full_breakdown"] = rows_to_dicts(cols, rows)

# How many rank >= 3?
cols, rows = q(cur,
    "SELECT rank, COUNT(*) FROM ec_curvedata WHERE rank >= 3 GROUP BY rank ORDER BY rank",
    "high_rank_counts")
edge2["high_rank_counts"] = rows_to_dicts(cols, rows)

results["2_parity_edges"] = edge2

# ═══════════════════════════════════════════════════════════════
# 3. MAZUR EDGES
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("3. MAZUR EDGES")
edge3 = {}

# Torsion distribution over Q
cols, rows = q(cur,
    "SELECT torsion, COUNT(*) FROM ec_curvedata GROUP BY torsion ORDER BY torsion",
    "torsion_dist_Q")
edge3["torsion_distribution_Q"] = rows_to_dicts(cols, rows)

# Torsion structure distribution
cols, rows = q(cur,
    "SELECT torsion_structure, COUNT(*) as cnt FROM ec_curvedata GROUP BY torsion_structure ORDER BY cnt DESC",
    "torsion_structure_dist")
edge3["torsion_structure_distribution"] = rows_to_dicts(cols, rows)

# Curves with torsion_structure = [2,8] (the rarest Mazur group)
cols, rows = q(cur,
    """SELECT lmfdb_label, conductor, rank, torsion_structure, regulator, sha
    FROM ec_curvedata WHERE torsion_structure = '{2,8}' OR torsion_structure = ARRAY[2,8]::smallint[]
    LIMIT 20""",
    "torsion_2_8")
if not rows:
    # Try text representation
    cols, rows = q(cur,
        """SELECT lmfdb_label, conductor, rank, torsion_structure
        FROM ec_curvedata WHERE torsion = 16 LIMIT 20""",
        "torsion_16")
edge3["torsion_16_curves"] = rows_to_dicts(cols, rows)

# Check if ec_nfcurves exists
cols, rows = q(cur,
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_name='ec_nfcurves'",
    "nfcurves_exists")
edge3["ec_nfcurves_exists"] = rows_to_dicts(cols, rows)

if rows and rows[0][0] > 0:
    cols, rows = q(cur,
        "SELECT COUNT(*) FROM ec_nfcurves",
        "nfcurves_count")
    edge3["ec_nfcurves_count"] = rows_to_dicts(cols, rows)

    # Torsion over number fields
    cols, rows = q(cur,
        """SELECT column_name FROM information_schema.columns
           WHERE table_name='ec_nfcurves' AND column_name LIKE '%tors%'""",
        "nf_torsion_cols")
    edge3["nf_torsion_columns"] = rows_to_dicts(cols, rows)

    if rows:
        tors_col = rows[0][0]
        cols2, rows2 = q(cur,
            f"SELECT {tors_col}, COUNT(*) as cnt FROM ec_nfcurves GROUP BY {tors_col} ORDER BY cnt DESC LIMIT 30",
            "nf_torsion_dist")
        edge3["nf_torsion_distribution"] = rows_to_dicts(cols2, rows2)

    # Degree of field
    cols, rows = q(cur,
        """SELECT column_name FROM information_schema.columns
           WHERE table_name='ec_nfcurves' AND column_name LIKE '%deg%' OR
           (table_name='ec_nfcurves' AND column_name = 'degree')""",
        "nf_degree_cols")
    edge3["nf_degree_columns"] = rows_to_dicts(cols, rows)

results["3_mazur_edges"] = edge3

# ═══════════════════════════════════════════════════════════════
# 4. HASSE BOUND EDGES
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("4. HASSE BOUND EDGES")
edge4 = {}

# Get traces from weight=2 dim=1 newforms
cols, rows = q(cur,
    """SELECT label, level, traces FROM mf_newforms
    WHERE weight = 2 AND dim = 1 AND traces IS NOT NULL
    LIMIT 2000""",
    "traces_sample")

primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

# Analyze Hasse ratios
hasse_ratios = []
supersingular_fractions = []
near_bound_examples = []

for row in rows:
    label, level, traces = row[0], row[1], row[2]
    if not traces or len(traces) < 48:
        continue

    max_ratio = 0.0
    ss_count = 0
    prime_count = 0

    for p in primes:
        if p <= len(traces) - 1:  # traces is 0-indexed, traces[n] = a_n
            a_p = traces[p]
            if a_p is None:
                continue
            bound = 2 * math.sqrt(p)
            ratio = abs(float(a_p)) / bound
            max_ratio = max(max_ratio, ratio)
            if a_p == 0:
                ss_count += 1
            prime_count += 1

    if prime_count > 0:
        hasse_ratios.append(max_ratio)
        supersingular_fractions.append(ss_count / prime_count)
        if max_ratio > 0.95:
            near_bound_examples.append({
                "label": label, "level": int(level),
                "max_ratio": round(max_ratio, 6),
                "ss_fraction": round(ss_count / prime_count, 4)
            })

if hasse_ratios:
    # Distribution of max |a_p|/(2√p)
    buckets = Counter()
    for r in hasse_ratios:
        bucket = round(r, 1)  # 0.0, 0.1, ..., 1.0
        buckets[bucket] += 1

    edge4["hasse_ratio_distribution"] = {str(k): v for k, v in sorted(buckets.items())}
    edge4["hasse_ratio_stats"] = {
        "n_curves": len(hasse_ratios),
        "mean": round(sum(hasse_ratios) / len(hasse_ratios), 6),
        "max": round(max(hasse_ratios), 6),
        "min": round(min(hasse_ratios), 6),
        "above_95pct": len([r for r in hasse_ratios if r > 0.95]),
        "above_90pct": len([r for r in hasse_ratios if r > 0.90]),
    }

    # Supersingular stats
    edge4["supersingular_stats"] = {
        "mean_fraction": round(sum(supersingular_fractions) / len(supersingular_fractions), 6),
        "max_fraction": round(max(supersingular_fractions), 4),
        "min_fraction": round(min(supersingular_fractions), 4),
    }

    # Near-bound examples (sorted by ratio)
    near_bound_examples.sort(key=lambda x: -x["max_ratio"])
    edge4["near_bound_examples"] = near_bound_examples[:20]

    # Finer distribution near the top
    fine_buckets = Counter()
    for r in hasse_ratios:
        if r >= 0.8:
            bucket = round(r, 2)
            fine_buckets[bucket] += 1
    edge4["hasse_ratio_fine_above_80pct"] = {str(k): v for k, v in sorted(fine_buckets.items())}

results["4_hasse_edges"] = edge4

# ═══════════════════════════════════════════════════════════════
# 5. CONDUCTOR EDGES
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("5. CONDUCTOR EDGES")
edge5 = {}

# Log10 distribution
cols, rows = q(cur,
    """SELECT FLOOR(LOG(conductor)/LOG(10))::int as log10_N, COUNT(*) as cnt
    FROM ec_curvedata WHERE conductor IS NOT NULL AND conductor > 0
    GROUP BY FLOOR(LOG(conductor)/LOG(10))::int ORDER BY log10_N""",
    "conductor_log_dist")
edge5["conductor_log10_distribution"] = rows_to_dicts(cols, rows)

# Most popular conductors
cols, rows = q(cur,
    """SELECT conductor, COUNT(*) as n_curves
    FROM ec_curvedata GROUP BY conductor ORDER BY n_curves DESC LIMIT 30""",
    "popular_conductors")
edge5["most_popular_conductors"] = rows_to_dicts(cols, rows)

# Smallest conductors with many curves
cols, rows = q(cur,
    """SELECT conductor, COUNT(*) as n_curves
    FROM ec_curvedata WHERE conductor <= 100
    GROUP BY conductor ORDER BY conductor""",
    "small_conductors")
edge5["small_conductor_density"] = rows_to_dicts(cols, rows)

# Conductor gaps in small range: which integers ≤ 1000 are NOT conductors?
cols, rows = q(cur,
    """SELECT generate_series(1,1000) as n
    EXCEPT SELECT DISTINCT conductor FROM ec_curvedata WHERE conductor <= 1000
    ORDER BY n LIMIT 50""",
    "conductor_gaps")
# Might fail due to syntax — try alternative
if not rows:
    cols, rows = q(cur,
        """WITH all_n AS (SELECT generate_series(1,500) as n),
             used AS (SELECT DISTINCT conductor FROM ec_curvedata WHERE conductor <= 500)
        SELECT n FROM all_n WHERE n NOT IN (SELECT conductor FROM used) ORDER BY n""",
        "conductor_gaps_v2")
edge5["conductor_gaps_under_500"] = rows_to_dicts(cols, rows)

# Total number of distinct conductors
cols, rows = q(cur,
    "SELECT COUNT(DISTINCT conductor) FROM ec_curvedata",
    "distinct_conductors")
edge5["distinct_conductor_count"] = rows_to_dicts(cols, rows)

# Max conductor
cols, rows = q(cur,
    "SELECT MAX(conductor) FROM ec_curvedata",
    "max_conductor")
edge5["max_conductor"] = rows_to_dicts(cols, rows)

results["5_conductor_edges"] = edge5

# ═══════════════════════════════════════════════════════════════
# 6. RANK EDGES
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("6. RANK EDGES")
edge6 = {}

# Rank distribution
cols, rows = q(cur,
    "SELECT rank, COUNT(*) as cnt FROM ec_curvedata WHERE rank IS NOT NULL GROUP BY rank ORDER BY rank",
    "rank_dist")
edge6["rank_distribution"] = rows_to_dicts(cols, rows)

# Goldfeld comparison: compute percentages
if rows:
    total = sum(r[1] for r in rows)
    goldfeld = []
    for r in rows:
        goldfeld.append({
            "rank": int(r[0]),
            "count": int(r[1]),
            "percentage": round(100.0 * r[1] / total, 4),
            "goldfeld_prediction": "~50%" if r[0] in (0, 1) else "~0%"
        })
    edge6["goldfeld_comparison"] = goldfeld

# Highest rank curves
cols, rows = q(cur,
    "SELECT lmfdb_label, conductor, rank, torsion, regulator FROM ec_curvedata ORDER BY rank DESC LIMIT 15",
    "highest_rank")
edge6["highest_rank_curves"] = rows_to_dicts(cols, rows)

# Rank vs analytic_rank — any disagreement? (should be 0 but let's be thorough)
cols, rows = q(cur,
    """SELECT COUNT(*) as mismatches FROM ec_curvedata
    WHERE rank IS NOT NULL AND analytic_rank IS NOT NULL AND rank != analytic_rank""",
    "rank_analytic_mismatch")
edge6["rank_analytic_mismatches"] = rows_to_dicts(cols, rows)

# rank = analytic_rank NULL cases
cols, rows = q(cur,
    """SELECT
        SUM(CASE WHEN rank IS NULL THEN 1 ELSE 0 END) as rank_null,
        SUM(CASE WHEN analytic_rank IS NULL THEN 1 ELSE 0 END) as analytic_null,
        COUNT(*) as total
    FROM ec_curvedata""",
    "null_rank_counts")
edge6["null_rank_counts"] = rows_to_dicts(cols, rows)

results["6_rank_edges"] = edge6

# ═══════════════════════════════════════════════════════════════
# 7. EC-MAASS GL(2) STRUCTURE EDGES
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("7. EC-MAASS STRUCTURE EDGES")
edge7 = {}

# Check what Maass form tables exist
cols, rows = q(cur,
    """SELECT table_name FROM information_schema.tables
    WHERE table_name LIKE '%maass%' ORDER BY table_name""",
    "maass_tables")
edge7["maass_tables"] = rows_to_dicts(cols, rows)

if rows:
    maass_table = rows[0][0]

    # Columns of the Maass table
    cols2, rows2 = q(cur,
        f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name='{maass_table}' ORDER BY ordinal_position",
        "maass_cols")
    edge7["maass_columns"] = rows_to_dicts(cols2, rows2)

    # Count
    cols2, rows2 = q(cur,
        f"SELECT COUNT(*) FROM {maass_table}",
        "maass_count")
    edge7["maass_count"] = rows_to_dicts(cols2, rows2)

    # Sample
    cols2, rows2 = q(cur,
        f"SELECT * FROM {maass_table} LIMIT 5",
        "maass_sample")
    edge7["maass_sample"] = rows_to_dicts(cols2, rows2)

# Check for shared levels between EC conductors and Maass levels
# First find the level column name in Maass table
if rows:
    # Try to find level overlap
    cols2, rows2 = q(cur,
        f"""SELECT column_name FROM information_schema.columns
        WHERE table_name='{maass_table}' AND column_name IN ('level','conductor','eigenvalue')""",
        "maass_level_col")
    edge7["maass_level_columns"] = rows_to_dicts(cols2, rows2)

    if rows2:
        level_col = rows2[0][0]

        # Shared levels
        cols3, rows3 = q(cur,
            f"""SELECT e.conductor as ec_conductor, COUNT(DISTINCT e.lmfdb_label) as n_ec
            FROM ec_curvedata e
            WHERE e.conductor IN (SELECT DISTINCT {level_col} FROM {maass_table})
            GROUP BY e.conductor ORDER BY n_ec DESC LIMIT 20""",
            "shared_levels")
        edge7["shared_levels"] = rows_to_dicts(cols3, rows3)

        # How many distinct levels overlap?
        cols3, rows3 = q(cur,
            f"""SELECT COUNT(DISTINCT {level_col}) as maass_levels,
                (SELECT COUNT(DISTINCT conductor) FROM ec_curvedata) as ec_conductors,
                (SELECT COUNT(*) FROM (
                    SELECT DISTINCT {level_col} FROM {maass_table}
                    INTERSECT
                    SELECT DISTINCT conductor FROM ec_curvedata
                ) t) as overlap
            FROM {maass_table}""",
            "level_overlap_stats")
        edge7["level_overlap_stats"] = rows_to_dicts(cols3, rows3)

# Also check mf_maass_forms or similar
cols, rows = q(cur,
    """SELECT table_name FROM information_schema.tables
    WHERE table_name LIKE '%maass%' OR table_name LIKE '%gl2%' OR table_name LIKE '%hecke%'
    ORDER BY table_name""",
    "related_tables")
edge7["related_spectral_tables"] = rows_to_dicts(cols, rows)

results["7_ec_maass_edges"] = edge7

# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("Writing results...")

cur.close()
conn.close()

with open(OUTFILE, "w") as f:
    json.dump(results, f, indent=2, default=str)

print(f"Saved to {OUTFILE}")
print("Done.")
