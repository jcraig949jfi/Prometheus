"""
Charon Frontier Batch 5 -- Test 5 hypotheses against g2c_curves, knots, nf_fields.
All DB columns are TEXT (except topology.knots which has proper types).
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import json
import math
import os
import sys
from collections import defaultdict
from datetime import datetime

import numpy as np
import psycopg2
from scipy import stats

# ── DB connections ──────────────────────────────────────────────────────────
LMFDB = dict(host="localhost", port=5432, dbname="lmfdb", user="postgres", password="prometheus")
PROMSCI = dict(host="localhost", port=5432, dbname="prometheus_sci", user="postgres", password="prometheus")

results = {}


def safe_int(x):
    try:
        return int(x)
    except (ValueError, TypeError):
        return None


def safe_float(x):
    try:
        return float(x)
    except (ValueError, TypeError):
        return None


def aut_order(aut_grp_id_str):
    """Parse '[n,k]' -> n (group order)."""
    try:
        s = aut_grp_id_str.strip().strip("[]")
        return int(s.split(",")[0])
    except:
        return None


# ── Möbius function ─────────────────────────────────────────────────────────
def mobius(n):
    """Compute μ(n). Returns 0 if n has squared prime factor."""
    if n <= 0:
        return 0
    if n == 1:
        return 1
    factors = 0
    d = 2
    temp = n
    while d * d <= temp:
        if temp % d == 0:
            temp //= d
            factors += 1
            if temp % d == 0:
                return 0  # squared factor
        d += 1
    if temp > 1:
        factors += 1
    return 1 if factors % 2 == 0 else -1


def is_perfect_square(n):
    if n < 0:
        return False
    s = int(math.isqrt(n))
    return s * s == n


# ═══════════════════════════════════════════════════════════════════════════
# H39: Genus-2 Aut Group Predicts Sha
# ═══════════════════════════════════════════════════════════════════════════
def test_h39():
    print("\n" + "=" * 70)
    print("H39: Genus-2 Aut Group Predicts Sha")
    print("=" * 70)

    conn = psycopg2.connect(**LMFDB)
    cur = conn.cursor()
    cur.execute("SELECT aut_grp_id, analytic_sha FROM g2c_curves")
    rows = cur.fetchall()
    conn.close()

    groups = defaultdict(list)
    for aut_id, sha_str in rows:
        sha = safe_float(sha_str)
        order = aut_order(aut_id)
        if sha is not None and sha > 0 and order is not None:
            groups[order].append(sha)

    print(f"  Groups found: {sorted(groups.keys())}")
    log_orders = []
    log_geomeans = []
    for order in sorted(groups.keys()):
        shas = groups[order]
        geomean = np.exp(np.mean(np.log(shas)))
        n = len(shas)
        print(f"  |Aut|={order}: N={n}, geomean(sha)={geomean:.4f}")
        log_orders.append(np.log(order))
        log_geomeans.append(np.log(geomean))

    if len(log_orders) >= 2:
        slope, intercept, r, p, se = stats.linregress(log_orders, log_geomeans)
        gamma = slope
        print(f"  Fit: gamma = {gamma:.4f}, r^2 = {r**2:.4f}, p = {p:.4e}")
        killed = gamma <= 0
        verdict = "KILLED" if killed else "SURVIVES"
    else:
        gamma = None
        verdict = "INCONCLUSIVE"
        p = None
        r = None

    print(f"  Verdict: {verdict}")
    results["H39"] = {
        "name": "Aut Group Predicts Sha",
        "verdict": verdict,
        "gamma": gamma,
        "r_squared": r**2 if r is not None else None,
        "p_value": p,
        "kill_criterion": "γ ≤ 0",
        "n_groups": len(groups),
        "group_sizes": {str(k): len(v) for k, v in groups.items()},
    }


# ═══════════════════════════════════════════════════════════════════════════
# H45: Manin-Mumford in Genus-2
# ═══════════════════════════════════════════════════════════════════════════
def test_h45():
    print("\n" + "=" * 70)
    print("H45: Manin-Mumford in Genus-2")
    print("=" * 70)

    conn = psycopg2.connect(**LMFDB)
    cur = conn.cursor()
    cur.execute("SELECT abs_disc, analytic_sha FROM g2c_curves")
    rows = cur.fetchall()
    conn.close()

    square_shas = []
    nonsquare_shas = []
    for disc_str, sha_str in rows:
        disc = safe_int(disc_str)
        sha = safe_int(sha_str)
        if disc is None or sha is None or sha <= 0:
            continue
        if is_perfect_square(disc):
            square_shas.append(sha)
        else:
            nonsquare_shas.append(sha)

    print(f"  Square disc curves: {len(square_shas)}")
    print(f"  Non-square disc curves: {len(nonsquare_shas)}")

    primes = [2, 3, 5, 7]
    ratios = {}
    for p in primes:
        if len(square_shas) > 0 and len(nonsquare_shas) > 0:
            p_sq = np.mean([1 if s % p == 0 else 0 for s in square_shas])
            p_nsq = np.mean([1 if s % p == 0 else 0 for s in nonsquare_shas])
            ratio = p_sq / p_nsq if p_nsq > 0 else float("inf")
            expected = 1 - 1 / p
            print(f"  p={p}: P(p|sha)_square={p_sq:.4f}, P(p|sha)_nonsquare={p_nsq:.4f}, "
                  f"R={ratio:.4f}, expected~{expected:.4f}")
            ratios[str(p)] = {"R": ratio, "expected": expected, "P_sq": p_sq, "P_nsq": p_nsq}
        else:
            ratios[str(p)] = {"R": None, "note": "insufficient data"}

    # Kill: R_p indistinguishable from 1.0 for all p
    any_different = False
    for p in primes:
        r = ratios[str(p)].get("R")
        if r is not None and abs(r - 1.0) > 0.05:
            any_different = True

    # Also do a Fisher exact test for the biggest deviation
    if len(square_shas) > 0 and len(nonsquare_shas) > 0:
        best_p_val = 1.0
        for p in primes:
            a = sum(1 for s in square_shas if s % p == 0)
            b = len(square_shas) - a
            c = sum(1 for s in nonsquare_shas if s % p == 0)
            d = len(nonsquare_shas) - c
            _, pval = stats.fisher_exact([[a, b], [c, d]])
            best_p_val = min(best_p_val, pval)
        killed = best_p_val > 0.05
    else:
        killed = True
        best_p_val = None

    verdict = "KILLED" if killed else "SURVIVES"
    print(f"  Best Fisher p-value: {best_p_val}")
    print(f"  Verdict: {verdict}")

    results["H45"] = {
        "name": "Manin-Mumford in Genus-2",
        "verdict": verdict,
        "ratios": ratios,
        "n_square": len(square_shas),
        "n_nonsquare": len(nonsquare_shas),
        "best_fisher_p": best_p_val,
        "kill_criterion": "R_p ≈ 1.0 for all p (p > 0.05)",
    }


# ═══════════════════════════════════════════════════════════════════════════
# H85: Chowla Deviation at Genus-2 Discriminants
# ═══════════════════════════════════════════════════════════════════════════
def test_h85():
    print("\n" + "=" * 70)
    print("H85: Chowla Deviation at Genus-2 Discriminants")
    print("=" * 70)

    conn = psycopg2.connect(**LMFDB)
    cur = conn.cursor()
    cur.execute("SELECT abs_disc, aut_grp_id FROM g2c_curves")
    rows = cur.fetchall()
    conn.close()

    groups = defaultdict(list)
    for disc_str, aut_id in rows:
        disc = safe_int(disc_str)
        order = aut_order(aut_id)
        if disc is not None and disc > 0 and order is not None:
            mu = mobius(disc)
            groups[order].append(mu)

    print(f"  Groups: {sorted(groups.keys())}")
    z_scores = {}
    max_z = 0
    any_z_over_3 = False
    all_large_groups_under_1 = True

    for order in sorted(groups.keys()):
        mus = groups[order]
        n = len(mus)
        mean_mu = np.mean(mus)
        # Under random expectation: mean ~ 0, std ~ 1/sqrt(N)
        # But more precisely: for Mobius on random integers, Var(mu) ~ 6/pi^2 per element
        # so std of mean ~ sqrt(6/pi^2 / N)
        expected_std = np.sqrt(6 / (np.pi**2 * n))
        z = abs(mean_mu) / expected_std if expected_std > 0 else 0
        print(f"  |Aut|={order}: N={n}, mean(mu)={mean_mu:.6f}, z={z:.2f}")
        z_scores[str(order)] = {"N": n, "mean_mu": mean_mu, "z": z}
        if z > max_z:
            max_z = z
        if z > 3:
            any_z_over_3 = True
        if n > 5000 and z >= 1.0:
            all_large_groups_under_1 = False

    # Kill: z < 1.0 for ALL groups with N > 5000
    large_groups = {k: v for k, v in z_scores.items() if v["N"] > 5000}
    killed_strict = all(v["z"] < 1.0 for v in large_groups.values()) if large_groups else True

    verdict = "KILLED" if killed_strict else "SURVIVES"
    print(f"  Max z-score: {max_z:.2f}")
    print(f"  Any z > 3: {any_z_over_3}")
    print(f"  Verdict: {verdict}")

    results["H85"] = {
        "name": "Chowla Deviation at Genus-2 Discriminants",
        "verdict": verdict,
        "z_scores": z_scores,
        "max_z": max_z,
        "any_z_over_3": any_z_over_3,
        "kill_criterion": "z < 1.0 for ALL groups with N > 5000",
    }


# ═══════════════════════════════════════════════════════════════════════════
# H69: Genus-2 Sato-Tate at Additive p=2
# ═══════════════════════════════════════════════════════════════════════════
def test_h69():
    print("\n" + "=" * 70)
    print("H69: Genus-2 Sato-Tate at Additive p=2")
    print("=" * 70)

    conn = psycopg2.connect(**LMFDB)
    cur = conn.cursor()

    # Check what columns might contain Frobenius trace data
    cur.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name='g2c_curves'
        AND (column_name LIKE '%trace%' OR column_name LIKE '%point%'
             OR column_name LIKE '%a_%' OR column_name LIKE '%frob%'
             OR column_name LIKE '%euler%' OR column_name LIKE '%lfactor%'
             OR column_name LIKE '%bad%')
        ORDER BY column_name
    """)
    trace_cols = [r[0] for r in cur.fetchall()]
    print(f"  Trace-related columns: {trace_cols}")

    # bad_lfactors might encode local Euler factors at bad primes
    cur.execute("SELECT bad_primes, bad_lfactors FROM g2c_curves LIMIT 5")
    samples = cur.fetchall()
    for s in samples:
        print(f"  Sample bad_primes={s[0]}, bad_lfactors={s[1]}")

    # Check for curves with additive reduction at p=2
    # bad_primes is a list like [2, 3, 5]. If 2 is in bad_primes, check bad_lfactors
    cur.execute("SELECT bad_primes, bad_lfactors, st_group FROM g2c_curves WHERE bad_primes LIKE '%2%' LIMIT 10")
    bad2_samples = cur.fetchall()
    print(f"\n  Curves with 2 in bad_primes: sample...")
    for s in bad2_samples[:3]:
        print(f"    bad_primes={s[0]}, bad_lfactors={s[1]}, st_group={s[2]}")

    # The table does not contain Frobenius traces a_p directly.
    # bad_lfactors gives Euler factors at bad primes but not a_p for good primes.
    # Without a_p or point counts, we cannot compute kurtosis of a_2.
    # Mark INCONCLUSIVE.

    verdict = "INCONCLUSIVE"
    note = ("g2c_curves lacks Frobenius trace (a_p) or point count columns. "
            "Only bad_lfactors available at bad primes. Cannot compute a_2 kurtosis.")
    print(f"  Verdict: {verdict}")
    print(f"  Note: {note}")

    conn.close()

    results["H69"] = {
        "name": "Sato-Tate at Additive p=2",
        "verdict": verdict,
        "note": note,
        "available_columns": trace_cols,
        "kill_criterion": "Kurtosis ≥ 1.8 (not testable)",
    }


# ═══════════════════════════════════════════════════════════════════════════
# H16: Knot Determinant ↔ NF Class Number Divisibility
# ═══════════════════════════════════════════════════════════════════════════
def test_h16():
    print("\n" + "=" * 70)
    print("H16: Knot Determinant <-> NF Class Number Divisibility")
    print("=" * 70)

    # Get knots
    conn_sci = psycopg2.connect(**PROMSCI)
    cur_sci = conn_sci.cursor()
    cur_sci.execute("SELECT determinant, crossing_number FROM topology.knots WHERE determinant IS NOT NULL AND determinant > 0")
    knot_rows = cur_sci.fetchall()
    conn_sci.close()
    print(f"  Knots with determinant > 0: {len(knot_rows)}")

    knot_dets = set()
    knot_data = []
    for det, cn in knot_rows:
        knot_dets.add(int(det))
        knot_data.append((int(det), int(cn)))

    # Get degree-2 NF with disc_abs matching knot determinants
    conn_lmfdb = psycopg2.connect(**LMFDB)
    cur_lmfdb = conn_lmfdb.cursor()

    # Build lookup: disc_abs -> class_number for degree=2 NFs
    # Sample efficiently: get NFs whose disc_abs is in the set of knot determinants
    det_list = list(knot_dets)
    # Use ANY for efficient lookup. Convert to strings since columns are text.
    det_strs = [str(d) for d in det_list]

    # Batch in chunks to avoid query size limits
    chunk_size = 5000
    nf_lookup = {}
    for i in range(0, len(det_strs), chunk_size):
        chunk = det_strs[i : i + chunk_size]
        cur_lmfdb.execute(
            "SELECT disc_abs, class_number FROM nf_fields WHERE degree = '2' AND disc_abs = ANY(%s)",
            (chunk,)
        )
        for disc, cn in cur_lmfdb.fetchall():
            d = safe_int(disc)
            c = safe_int(cn)
            if d is not None and c is not None:
                if d not in nf_lookup:
                    nf_lookup[d] = []
                nf_lookup[d].append(c)

    conn_lmfdb.close()

    print(f"  Unique knot determinants: {len(knot_dets)}")
    print(f"  NF disc_abs matches found: {len(nf_lookup)}")

    # For each knot with a matching NF: check if det | class_number
    hits = 0
    total = 0
    for det, cn in knot_data:
        if det in nf_lookup:
            for class_num in nf_lookup[det]:
                total += 1
                if class_num % det == 0:
                    hits += 1

    hit_rate = hits / total if total > 0 else 0
    print(f"  Matched pairs (knot det = NF disc_abs): {total}")
    print(f"  Hits (det | class_number): {hits}")
    print(f"  Hit rate: {hit_rate:.4f}")

    # Permutation null: shuffle class numbers among matched NFs
    if total > 10:
        all_class_nums = []
        pair_dets = []
        for det, cn in knot_data:
            if det in nf_lookup:
                for class_num in nf_lookup[det]:
                    pair_dets.append(det)
                    all_class_nums.append(class_num)

        rng = np.random.default_rng(42)
        null_hits = []
        for _ in range(10000):
            shuffled = rng.permutation(all_class_nums)
            h = sum(1 for d, c in zip(pair_dets, shuffled) if c % d == 0)
            null_hits.append(h)

        null_mean = np.mean(null_hits)
        null_std = np.std(null_hits)
        z = (hits - null_mean) / null_std if null_std > 0 else 0
        p_val = np.mean([1 for nh in null_hits if nh >= hits]) / len(null_hits)
        print(f"  Null mean hits: {null_mean:.2f} ± {null_std:.2f}")
        print(f"  z-score vs null: {z:.2f}")
        print(f"  Permutation p-value: {p_val:.4f}")
    else:
        null_mean = None
        null_std = None
        z = None
        p_val = None
        print("  Too few matched pairs for permutation test.")

    # Kill if hit rate is not significantly ABOVE random (one-sided test)
    # hits <= null_mean means no enrichment at all -> killed
    killed = (p_val is None or p_val > 0.05 or hits <= null_mean) if total > 0 else True
    verdict = "KILLED" if killed else "SURVIVES"
    if total == 0:
        verdict = "INCONCLUSIVE"
    print(f"  Verdict: {verdict}")

    results["H16"] = {
        "name": "Knot Determinant <-> NF Class Number Divisibility",
        "verdict": verdict,
        "total_pairs": total,
        "hits": hits,
        "hit_rate": hit_rate,
        "null_mean": float(null_mean) if null_mean is not None else None,
        "null_std": float(null_std) if null_std is not None else None,
        "z_score": float(z) if z is not None else None,
        "p_value": float(p_val) if p_val is not None else None,
        "kill_criterion": "Hit rate = random (p > 0.05)",
    }


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Charon Frontier Batch 5")
    print(f"Timestamp: {datetime.now().isoformat()}")

    test_h39()
    test_h45()
    test_h85()
    test_h69()
    test_h16()

    # ── Summary Table ───────────────────────────────────────────────────
    print("\n" + "=" * 90)
    print(f"{'Hypothesis':<10} {'Name':<42} {'Verdict':<14} {'Key Statistic':<25} {'Kill Met?'}")
    print("-" * 90)

    def fmt_stat(h):
        r = results[h]
        if h == "H39":
            g = r.get("gamma")
            return f"gamma={g:.4f}" if g is not None else "N/A"
        elif h == "H45":
            return f"Fisher p={r.get('best_fisher_p', 'N/A')}"
        elif h == "H85":
            return f"max z={r.get('max_z', 0):.2f}"
        elif h == "H69":
            return "no a_p data"
        elif h == "H16":
            z = r.get("z_score")
            return f"z={z:.2f}, p={r.get('p_value', 'N/A')}" if z is not None else "no matches"

    for h in ["H39", "H45", "H85", "H69", "H16"]:
        r = results[h]
        kill_met = "YES" if r["verdict"] == "KILLED" else ("N/A" if r["verdict"] == "INCONCLUSIVE" else "NO")
        print(f"{h:<10} {r['name']:<42} {r['verdict']:<14} {fmt_stat(h):<25} {kill_met}")

    print("=" * 90)

    # ── Save JSON ───────────────────────────────────────────────────────
    out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "frontier_batch5.json")
    # Convert numpy types for JSON serialization
    def convert(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            r = convert(obj)
            if r is not obj:
                return r
            return super().default(obj)

    with open(out_path, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results,
        }, f, indent=2, cls=NumpyEncoder)

    print(f"\nResults saved to {out_path}")
