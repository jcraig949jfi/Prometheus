"""
Charon Frontier Batch 2: Test 5 hypotheses against LMFDB + prometheus_sci.
Writes results to charon/data/frontier_batch2.json.
"""

import json
import math
import os
import sys
import time
from collections import Counter
from pathlib import Path

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
import psycopg2

# ── DB connections ──────────────────────────────────────────────────────────
LMFDB = dict(host="localhost", port=5432, dbname="lmfdb", user="postgres", password="prometheus")
PSCI  = dict(host="localhost", port=5432, dbname="prometheus_sci", user="postgres", password="prometheus")

def get_conn(params):
    return psycopg2.connect(**params)

results = {}

# ═══════════════════════════════════════════════════════════════════════════
# H46: Autocatalytic EC Rank Collapse
# ═══════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("H46: Autocatalytic EC Rank Collapse")
print("=" * 70)
t0 = time.time()
try:
    conn = get_conn(LMFDB)
    cur = conn.cursor()
    cur.execute("""
        SELECT conductor::float, szpiro_ratio::float, rank::int
        FROM ec_curvedata
        WHERE conductor IS NOT NULL
          AND szpiro_ratio IS NOT NULL
          AND rank IS NOT NULL
          AND szpiro_ratio::float > 0
        LIMIT 500000
    """)
    rows = cur.fetchall()
    conn.close()

    conductors = np.array([r[0] for r in rows])
    szpiros = np.array([r[1] for r in rows])
    ranks = np.array([r[2] for r in rows])

    C = conductors / szpiros
    rank_gt1 = (ranks > 1).astype(float)

    # Bin into 100 equal-width bins
    c_min, c_max = np.percentile(C, [1, 99])  # clip outliers
    mask = (C >= c_min) & (C <= c_max)
    C_clipped = C[mask]
    rank_clipped = rank_gt1[mask]

    bin_edges = np.linspace(c_min, c_max, 101)
    bin_indices = np.digitize(C_clipped, bin_edges) - 1
    bin_indices = np.clip(bin_indices, 0, 99)

    probs = np.zeros(100)
    counts = np.zeros(100)
    for i in range(100):
        m = bin_indices == i
        if m.sum() > 0:
            probs[i] = rank_clipped[m].mean()
            counts[i] = m.sum()

    # Moving average (window=5) and jumps
    window = 5
    valid = counts > 10
    jumps = np.abs(np.diff(probs))

    # Moving average of jumps
    if len(jumps) > window:
        ma = np.convolve(jumps, np.ones(window)/window, mode='same')
        std_jumps = np.std(jumps)
        if std_jumps > 0:
            z_scores = (jumps - ma) / std_jumps
            max_z = float(np.max(z_scores))
        else:
            max_z = 0.0
    else:
        max_z = 0.0

    killed = max_z <= 4.0
    verdict = "KILLED" if killed else "SURVIVES"
    stat = f"max_z={max_z:.2f}, n={len(rows)}, P(rank>1)_mean={rank_gt1.mean():.5f}"
    print(f"  {verdict}: {stat}")
    print(f"  Kill criterion: No spike > 4σ → {'MET' if killed else 'NOT MET'}")

    results["H46"] = {
        "hypothesis": "Autocatalytic EC Rank Collapse",
        "verdict": verdict,
        "key_statistic": stat,
        "kill_criterion_met": killed,
        "elapsed_s": round(time.time() - t0, 1)
    }
except Exception as e:
    print(f"  ERROR: {e}")
    results["H46"] = {"verdict": "ERROR", "error": str(e)}

# ═══════════════════════════════════════════════════════════════════════════
# H80: Lehmer Bound for L-function Leading Terms
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("H80: Lehmer Bound for L-function Leading Terms")
print("=" * 70)
t0 = time.time()
try:
    conn = get_conn(LMFDB)
    cur = conn.cursor()
    # order_of_vanishing is text, but >= '2' works for single digits (2-9)
    # To be safe, cast to int
    cur.execute("""
        SELECT leading_term, order_of_vanishing::int
        FROM lfunc_lfunctions
        WHERE order_of_vanishing IS NOT NULL
          AND leading_term IS NOT NULL
          AND leading_term != ''
          AND order_of_vanishing::int >= 2
        LIMIT 500000
    """)
    rows = cur.fetchall()
    conn.close()

    n_total = len(rows)
    violations = 0
    min_val = float('inf')
    LEHMER = 1.17628

    for lt_str, ov in rows:
        try:
            lt = float(lt_str)
            val = math.exp(abs(lt))
            if val < LEHMER:
                violations += 1
            if val < min_val:
                min_val = val
        except (ValueError, OverflowError):
            continue

    killed = violations > 0
    verdict = "KILLED" if killed else "SURVIVES"
    stat = f"n={n_total}, violations={violations}, min_exp_lt={min_val:.6f}"
    print(f"  {verdict}: {stat}")
    print(f"  Kill criterion: Single counterexample → {'MET' if killed else 'NOT MET'}")

    results["H80"] = {
        "hypothesis": "Lehmer Bound for L-function Leading Terms",
        "verdict": verdict,
        "key_statistic": stat,
        "kill_criterion_met": killed,
        "elapsed_s": round(time.time() - t0, 1)
    }
except Exception as e:
    print(f"  ERROR: {e}")
    results["H80"] = {"verdict": "ERROR", "error": str(e)}

# ═══════════════════════════════════════════════════════════════════════════
# H72: Weight-Dimension Concentration
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("H72: Weight-Dimension Concentration")
print("=" * 70)
t0 = time.time()
try:
    conn = get_conn(LMFDB)
    cur = conn.cursor()
    cur.execute("""
        SELECT weight::int, dim::int
        FROM mf_newforms
        WHERE level IS NOT NULL AND weight IS NOT NULL AND dim IS NOT NULL
          AND level::int <= 100
    """)
    rows = cur.fetchall()
    conn.close()

    n = len(rows)
    weights = np.array([r[0] for r in rows])
    dims = np.array([r[1] for r in rows])

    # P(weight = dim + 1) observed
    match_mask = weights == (dims + 1)
    p_observed = match_mask.mean()

    # Marginal distributions
    weight_counts = Counter(weights)
    dim_counts = Counter(dims)
    p_weight = {w: c/n for w, c in weight_counts.items()}
    p_dim = {d: c/n for d, c in dim_counts.items()}

    # P(weight=w) * P(dim=w-1) summed over all w
    p_expected = 0.0
    for w in weight_counts:
        if (w - 1) in dim_counts:
            p_expected += p_weight[w] * p_dim[w - 1]

    ratio = p_observed / p_expected if p_expected > 0 else float('inf')

    if ratio > 2.0:
        verdict = "SURVIVES"
        killed = False
    elif ratio < 1.3:
        verdict = "KILLED"
        killed = True
    else:
        verdict = "INCONCLUSIVE"
        killed = False

    stat = f"ratio={ratio:.3f}, p_obs={p_observed:.5f}, p_exp={p_expected:.5f}, n={n}"
    print(f"  {verdict}: {stat}")
    print(f"  Kill criterion: Factor < 1.3 → {'MET' if killed else 'NOT MET'}")

    results["H72"] = {
        "hypothesis": "Weight-Dimension Concentration",
        "verdict": verdict,
        "key_statistic": stat,
        "kill_criterion_met": killed,
        "elapsed_s": round(time.time() - t0, 1)
    }
except Exception as e:
    print(f"  ERROR: {e}")
    results["H72"] = {"verdict": "ERROR", "error": str(e)}

# ═══════════════════════════════════════════════════════════════════════════
# H70: Trace Hash Collision Geometry
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("H70: Trace Hash Collision Geometry")
print("=" * 70)
t0 = time.time()
try:
    conn = get_conn(LMFDB)
    cur = conn.cursor()
    # Find trace_hash collisions with different levels
    cur.execute("""
        SELECT a.trace_hash, a.level::int, b.level::int
        FROM mf_newforms a
        JOIN mf_newforms b ON a.trace_hash = b.trace_hash AND a.level != b.level AND a.id < b.id
        WHERE a.trace_hash IS NOT NULL
        LIMIT 10000
    """)
    pairs = cur.fetchall()
    conn.close()

    n_pairs = len(pairs)

    if n_pairs == 0:
        verdict = "KILLED"
        killed = True
        stat = f"n_collision_pairs=0 (no data to test; trace_hash is near-unique across levels)"
    else:
        # Factor ratios and compute geometric mean of prime factors
        from sympy import factorint
        smooth_count = 0
        for _, l1, l2 in pairs:
            ratio = max(l1, l2) / min(l1, l2) if min(l1, l2) > 0 else 0
            if ratio == 0:
                continue
            # Get integer ratio (or close)
            from fractions import Fraction
            f = Fraction(l1, l2)
            num_factors = factorint(f.numerator)
            den_factors = factorint(f.denominator)
            all_primes = list(num_factors.keys()) + list(den_factors.keys())
            if all_primes:
                gm = np.exp(np.mean(np.log(all_primes)))
                if gm < 7:
                    smooth_count += 1

        pct = smooth_count / n_pairs * 100 if n_pairs > 0 else 0
        killed = pct < 50
        verdict = "KILLED" if killed else ("SURVIVES" if pct >= 80 else "INCONCLUSIVE")
        stat = f"n_pairs={n_pairs}, smooth_pct={pct:.1f}%"

    print(f"  {verdict}: {stat}")
    print(f"  Kill criterion: Smoothness < 50% → {'MET' if killed else 'NOT MET'}")

    results["H70"] = {
        "hypothesis": "Trace Hash Collision Geometry",
        "verdict": verdict,
        "key_statistic": stat,
        "kill_criterion_met": killed,
        "elapsed_s": round(time.time() - t0, 1)
    }
except Exception as e:
    print(f"  ERROR: {e}")
    results["H70"] = {"verdict": "ERROR", "error": str(e)}

# ═══════════════════════════════════════════════════════════════════════════
# H90: EC Rank vs Group Order Smoothness (Null Test)
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("H90: EC Rank vs Group Order Smoothness (Null Test)")
print("=" * 70)
t0 = time.time()
try:
    # Get EC conductors and ranks
    conn = get_conn(LMFDB)
    cur = conn.cursor()
    cur.execute("""
        SELECT conductor::numeric, rank::int
        FROM ec_curvedata
        WHERE conductor IS NOT NULL AND rank IS NOT NULL
          AND conductor::numeric < 2000000
        ORDER BY RANDOM()
        LIMIT 50000
    """)
    ec_rows = cur.fetchall()
    conn.close()

    ec_by_cond = {}
    for c, r in ec_rows:
        ec_by_cond[int(c)] = r

    # Get group orders from prometheus_sci
    conn2 = get_conn(PSCI)
    cur2 = conn2.cursor()
    cond_list = list(ec_by_cond.keys())

    # Batch query -- check which conductors appear as group orders
    # Use chunks to avoid huge IN clauses
    matching = {}
    chunk_size = 5000
    for i in range(0, len(cond_list), chunk_size):
        chunk = cond_list[i:i+chunk_size]
        placeholders = ",".join(["%s"] * len(chunk))
        cur2.execute(f"""
            SELECT DISTINCT order_val::numeric
            FROM algebra.groups
            WHERE order_val::numeric IN ({placeholders})
        """, chunk)
        for (ov,) in cur2.fetchall():
            matching[int(ov)] = True
    conn2.close()

    # For matching conductors, compute smoothness (largest prime factor)
    from sympy import factorint

    matched_ranks = []
    matched_smoothness = []

    for cond in matching:
        if cond in ec_by_cond and cond > 1:
            rank = ec_by_cond[cond]
            factors = factorint(int(cond))
            if factors:
                largest_prime = max(factors.keys())
                matched_ranks.append(rank)
                matched_smoothness.append(largest_prime)

    n_matched = len(matched_ranks)
    print(f"  Matched conductors: {n_matched}")

    if n_matched < 20:
        verdict = "INCONCLUSIVE"
        killed = False
        stat = f"n_matched={n_matched} (too few for MI estimate)"
    else:
        # Compute mutual information via histogram method
        ranks_arr = np.array(matched_ranks)
        smooth_arr = np.log2(np.array(matched_smoothness) + 1)  # log-scale smoothness

        # Discretize smoothness into bins
        n_bins = min(20, n_matched // 5)
        smooth_binned = np.digitize(smooth_arr, np.linspace(smooth_arr.min(), smooth_arr.max(), n_bins + 1)) - 1
        smooth_binned = np.clip(smooth_binned, 0, n_bins - 1)

        # Joint and marginal distributions
        joint = np.zeros((int(ranks_arr.max()) + 1, n_bins))
        for r, s in zip(ranks_arr, smooth_binned):
            joint[int(r), int(s)] += 1
        joint /= joint.sum()

        p_rank = joint.sum(axis=1)
        p_smooth = joint.sum(axis=0)

        # MI = sum p(x,y) * log(p(x,y) / (p(x)*p(y)))
        mi = 0.0
        for i in range(joint.shape[0]):
            for j in range(joint.shape[1]):
                if joint[i, j] > 0 and p_rank[i] > 0 and p_smooth[j] > 0:
                    mi += joint[i, j] * np.log2(joint[i, j] / (p_rank[i] * p_smooth[j]))

        # Random-pairing null (10 shuffles)
        mi_nulls = []
        for _ in range(100):
            perm = np.random.permutation(len(smooth_binned))
            joint_null = np.zeros_like(joint)
            for r, s in zip(ranks_arr, smooth_binned[perm]):
                joint_null[int(r), int(s)] += 1
            joint_null /= joint_null.sum()
            mi_null = 0.0
            for i in range(joint_null.shape[0]):
                for j in range(joint_null.shape[1]):
                    if joint_null[i, j] > 0 and p_rank[i] > 0 and p_smooth[j] > 0:
                        mi_null += joint_null[i, j] * np.log2(joint_null[i, j] / (p_rank[i] * p_smooth[j]))
            mi_nulls.append(mi_null)

        mi_null_mean = np.mean(mi_nulls)
        mi_corrected = mi - mi_null_mean

        killed = mi_corrected > 0.05
        if mi_corrected < 0.01:
            verdict = "SURVIVES (null confirmed)"
        elif mi_corrected > 0.05:
            verdict = "KILLED"
        else:
            verdict = "INCONCLUSIVE"

        stat = f"MI={mi:.4f} bits, MI_null={mi_null_mean:.4f}, MI_corrected={mi_corrected:.4f}, n={n_matched}"

    print(f"  {verdict}: {stat}")
    print(f"  Kill criterion: MI > 0.05 bits → {'MET' if killed else 'NOT MET'}")

    results["H90"] = {
        "hypothesis": "EC Rank vs Group Order Smoothness (Null Test)",
        "verdict": verdict,
        "key_statistic": stat,
        "kill_criterion_met": killed,
        "elapsed_s": round(time.time() - t0, 1)
    }
except Exception as e:
    print(f"  ERROR: {e}")
    results["H90"] = {"verdict": "ERROR", "error": str(e)}

# ═══════════════════════════════════════════════════════════════════════════
# Summary Table
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 100)
print(f"{'Hypothesis':<12} {'Verdict':<25} {'Key Statistic':<50} {'Kill Met?'}")
print("-" * 100)
for h_id in ["H46", "H80", "H72", "H70", "H90"]:
    r = results.get(h_id, {})
    v = r.get("verdict", "N/A")
    s = r.get("key_statistic", r.get("error", "N/A"))
    k = str(r.get("kill_criterion_met", "N/A"))
    print(f"{h_id:<12} {v:<25} {s:<50} {k}")
print("=" * 100)

# Save results
out_path = Path("F:/Prometheus/charon/data/frontier_batch2.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults saved to {out_path}")
