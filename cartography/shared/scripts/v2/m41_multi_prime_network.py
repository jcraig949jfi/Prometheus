"""
M41: Multi-prime constraint interference network
===================================================
Build the full multi-prime congruence graph: nodes = forms, edges labeled by
which primes ℓ they're congruent at. For pairs congruent at ≥2 primes,
measure the graph properties vs single-prime subgraphs.

Is the multi-prime intersection a lattice? A hypergraph? Random?
"""
import json, time
import numpy as np
import duckdb
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations

V2 = Path(__file__).resolve().parent
DB = V2.parents[3] / "charon" / "data" / "charon.duckdb"
HECKE = V2 / "hecke_graph_results.json"
OUT = V2 / "m41_multi_prime_network_results.json"

def sieve(limit):
    is_p = [True] * (limit + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_p[i]:
            for j in range(i*i, limit+1, i): is_p[j] = False
    return [i for i in range(2, limit+1) if is_p[i]]

def prime_factors(n):
    f = set(); d = 2
    while d*d <= n:
        while n % d == 0: f.add(d); n //= d
        d += 1
    if n > 1: f.add(n)
    return f

def check_cong(ap1, ap2, ell, good_idx, min_tested=10):
    tested = 0
    for k in good_idx:
        if k >= len(ap1) or k >= len(ap2): break
        tested += 1
        if (ap1[k] - ap2[k]) % ell != 0: return False
        if tested >= 20: break
    return tested >= min_tested

def main():
    t0 = time.time()
    print("=== M41: Multi-prime constraint interference network ===\n")

    # Load from Hecke results for single-prime stats
    with open(HECKE) as f:
        hecke = json.load(f)
    per_ell = hecke.get("per_ell", {})
    for ell in sorted(int(e) for e in per_ell.keys()):
        d = per_ell[str(ell)]
        print(f"  Single-prime ℓ={ell}: {d.get('n_congruences', d.get('n_edges', 0))} congruences")

    # Compute multi-prime from DuckDB
    print("\n  Loading forms for multi-prime analysis...")
    con = duckdb.connect(str(DB), read_only=True)
    rows = con.execute("""
        SELECT lmfdb_label, level, ap_coeffs FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND char_order = 1
        ORDER BY level LIMIT 3000
    """).fetchall()
    con.close()

    ap_primes = sieve(100)
    ELLS = [2, 3, 5, 7, 11]
    forms = []
    for label, level, ap_json in rows:
        ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
        ap_vals = [x[0] if isinstance(x, list) else x for x in ap]
        forms.append({"label": label, "level": level, "ap": ap_vals})

    by_level = defaultdict(list)
    for f in forms: by_level[f["level"]].append(f)

    # Build edge labels
    print(f"  {len(forms)} forms, computing pairwise multi-prime congruences...")
    multi_edges = []
    edge_label_counts = Counter()
    for level, group in by_level.items():
        if len(group) < 2: continue
        bad = prime_factors(level)
        good_idx = [i for i, p in enumerate(ap_primes) if p not in bad and p not in ELLS]
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                cong_at = set()
                for ell in ELLS:
                    if check_cong(group[i]["ap"], group[j]["ap"], ell, good_idx):
                        cong_at.add(ell)
                if cong_at:
                    label_key = tuple(sorted(cong_at))
                    edge_label_counts[label_key] += 1
                    if len(cong_at) >= 2:
                        multi_edges.append({
                            "a": group[i]["label"], "b": group[j]["label"],
                            "primes": sorted(cong_at), "n_primes": len(cong_at),
                        })

    # Summary
    print(f"\n  Edge label distribution:")
    for label, cnt in sorted(edge_label_counts.items(), key=lambda x: -x[1]):
        print(f"    {label}: {cnt}")

    n_single = sum(v for k, v in edge_label_counts.items() if len(k) == 1)
    n_double = sum(v for k, v in edge_label_counts.items() if len(k) == 2)
    n_triple = sum(v for k, v in edge_label_counts.items() if len(k) >= 3)
    print(f"\n  Single-prime edges: {n_single}")
    print(f"  Double-prime edges: {n_double}")
    print(f"  Triple+ prime edges: {n_triple}")

    # Independence test: is n_double > expected under independence?
    total = sum(edge_label_counts.values())
    p_single = {}
    for ell in ELLS:
        p_single[ell] = sum(v for k, v in edge_label_counts.items() if ell in k) / total if total > 0 else 0
    expected_double = 0
    for l1, l2 in combinations(ELLS, 2):
        expected_double += p_single[l1] * p_single[l2] * total
    interference_ratio = n_double / expected_double if expected_double > 0 else 0
    print(f"\n  Expected double-prime (independence): {expected_double:.1f}")
    print(f"  Observed: {n_double}")
    print(f"  Interference ratio: {interference_ratio:.4f}")

    elapsed = time.time() - t0
    output = {
        "probe": "M41", "title": "Multi-prime constraint interference network",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_forms": len(forms),
        "edge_label_distribution": {str(k): v for k, v in sorted(edge_label_counts.items(), key=lambda x: -x[1])},
        "n_single_prime_edges": n_single,
        "n_double_prime_edges": n_double,
        "n_triple_plus_edges": n_triple,
        "independence_test": {
            "expected_double": round(expected_double, 1),
            "observed_double": n_double,
            "interference_ratio": round(interference_ratio, 4),
        },
        "multi_edge_examples": multi_edges[:20],
        "assessment": None,
    }

    if interference_ratio > 2.0:
        output["assessment"] = f"CONSTRUCTIVE: multi-prime congruences {interference_ratio:.1f}x more common than independence predicts"
    elif interference_ratio > 0.5:
        output["assessment"] = f"NEAR-INDEPENDENT: ratio={interference_ratio:.2f}. Multi-prime congruences near chance level"
    elif interference_ratio > 0:
        output["assessment"] = f"DESTRUCTIVE: ratio={interference_ratio:.2f}. Multi-prime congruences suppressed below independence"
    else:
        output["assessment"] = f"ZERO: no multi-prime edges found. Complete suppression (consistent with M19 β₃=0)"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
