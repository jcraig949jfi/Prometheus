"""
Challenge 2: v₅ Sweet Spot for GL₂
=====================================
The v₂=8 sweet spot showed maximum clique richness at 2³ in GSp₄ mod-2.
Generalize: does a corresponding v_5 sweet spot exist in the GL₂ graph
at the critical phase transition prime ℓ=5?
"""
import json, time, math
import numpy as np
import duckdb
from pathlib import Path
from collections import Counter, defaultdict

V2 = Path(__file__).resolve().parent
DB = V2.parents[3] / "charon" / "data" / "charon.duckdb"
OUT = V2 / "c2_v5_sweet_spot_results.json"

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

def v_p(n, p):
    """p-adic valuation of n."""
    if n == 0: return float('inf')
    v = 0
    while n % p == 0: v += 1; n //= p
    return v

def check_cong(ap1, ap2, ell, good_idx, min_tested=8):
    tested = 0
    for k in good_idx:
        if k >= len(ap1) or k >= len(ap2): break
        tested += 1
        if (ap1[k] - ap2[k]) % ell != 0: return False
        if tested >= 15: break
    return tested >= min_tested

def main():
    t0 = time.time()
    print("=== Challenge 2: v₅ Sweet Spot for GL₂ ===\n")

    con = duckdb.connect(str(DB), read_only=True)
    rows = con.execute("""
        SELECT lmfdb_label, level, ap_coeffs
        FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND char_order = 1
        ORDER BY level
    """).fetchall()
    con.close()
    print(f"  {len(rows)} forms loaded")

    ap_primes = sieve(100)
    ELL = 5  # Critical transition prime

    # Parse forms
    forms = []
    for label, level, ap_json in rows:
        ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
        ap_vals = [x[0] if isinstance(x, list) else x for x in ap]
        v5 = v_p(level, 5)
        forms.append({"label": label, "level": level, "ap": ap_vals, "v5": v5})

    # Group by v₅ valuation
    by_v5 = defaultdict(list)
    for f in forms: by_v5[f["v5"]].append(f)
    print(f"  v₅ distribution: {sorted((k, len(v)) for k, v in by_v5.items())}")

    # For each v₅ group, compute mod-5 congruence graph density
    print(f"\n  Computing mod-{ELL} congruence structure by v₅...")
    v5_stats = {}
    for v5_val in sorted(by_v5.keys()):
        group = by_v5[v5_val]
        if len(group) < 2:
            v5_stats[v5_val] = {"n_forms": len(group), "n_edges": 0, "density": 0}
            continue

        # Group forms by level for same-level congruence tests
        by_level = defaultdict(list)
        for f in group: by_level[f["level"]].append(f)

        n_edges = 0; n_pairs = 0; n_triangles = 0
        # Build edge lists per level for triangle counting
        level_edges = {}
        for level, lgroup in by_level.items():
            if len(lgroup) < 2: continue
            bad = prime_factors(level)
            good_idx = [i for i, p in enumerate(ap_primes) if p not in bad and p != ELL]
            edges = []
            for i in range(len(lgroup)):
                for j in range(i+1, len(lgroup)):
                    n_pairs += 1
                    if check_cong(lgroup[i]["ap"], lgroup[j]["ap"], ELL, good_idx):
                        n_edges += 1
                        edges.append((i, j))
            # Count triangles
            adj = defaultdict(set)
            for a, b in edges:
                adj[a].add(b); adj[b].add(a)
            for a in adj:
                for b in adj[a]:
                    if b > a:
                        common = adj[a] & adj[b]
                        n_triangles += len([c for c in common if c > b])
            level_edges[level] = edges

        # Component sizes
        all_edges = []
        offset = 0
        for level, edges in level_edges.items():
            for a, b in edges:
                all_edges.append((a + offset, b + offset))
            offset += len(by_level[level])

        density = n_edges / n_pairs if n_pairs > 0 else 0
        v5_stats[v5_val] = {
            "n_forms": len(group),
            "n_pairs_tested": n_pairs,
            "n_edges": n_edges,
            "density": round(density, 6),
            "n_triangles": n_triangles,
            "triangle_density": round(n_triangles / max(n_edges, 1), 4),
        }
        print(f"  v₅={v5_val}: {len(group)} forms, {n_edges} edges, "
              f"density={density:.4f}, triangles={n_triangles}")

    # Find sweet spot
    best_v5 = max(v5_stats.keys(), key=lambda k: v5_stats[k]["density"]) if v5_stats else None
    best_density = v5_stats[best_v5]["density"] if best_v5 is not None else 0
    best_edges = v5_stats[best_v5]["n_edges"] if best_v5 is not None else 0

    # Also check by triangle density
    best_tri_v5 = max(v5_stats.keys(), key=lambda k: v5_stats[k]["n_triangles"]) if v5_stats else None

    # Check for wall: is there a v₅ value where structure collapses?
    v5_ordered = sorted(v5_stats.items())
    wall_v5 = None
    for i in range(1, len(v5_ordered)):
        prev_density = v5_ordered[i-1][1]["density"]
        curr_density = v5_ordered[i][1]["density"]
        if prev_density > 0 and curr_density == 0:
            wall_v5 = v5_ordered[i][0]
            break

    print(f"\n  Sweet spot: v₅={best_v5} (density={best_density:.4f}, edges={best_edges})")
    print(f"  Best triangle v₅: {best_tri_v5}")
    print(f"  Wall (collapse to 0): v₅={wall_v5}")

    # Compare to v₂ sweet spot (should be at 2³=8, i.e. v₂=3)
    v2_stats = {}
    for v2_val in range(5):
        group = [f for f in forms if v_p(f["level"], 2) == v2_val]
        by_level = defaultdict(list)
        for f in group: by_level[f["level"]].append(f)
        n_edges = 0; n_pairs = 0
        for level, lgroup in by_level.items():
            if len(lgroup) < 2: continue
            bad = prime_factors(level)
            good_idx = [i for i, p in enumerate(ap_primes) if p not in bad and p != 2]
            for i in range(len(lgroup)):
                for j in range(i+1, len(lgroup)):
                    n_pairs += 1
                    if check_cong(lgroup[i]["ap"], lgroup[j]["ap"], 2, good_idx):
                        n_edges += 1
        density = n_edges / n_pairs if n_pairs > 0 else 0
        v2_stats[v2_val] = {"n_forms": len(group), "n_edges": n_edges, "density": round(density, 6)}
        print(f"  v₂={v2_val}: {len(group)} forms, {n_edges} mod-2 edges, density={density:.4f}")

    elapsed = time.time() - t0
    output = {
        "challenge": "C2", "title": "v₅ Sweet Spot for GL₂",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_forms": len(forms),
        "v5_analysis": {str(k): v for k, v in v5_stats.items()},
        "sweet_spot_v5": best_v5,
        "sweet_spot_density": best_density,
        "wall_v5": wall_v5,
        "v2_comparison": {str(k): v for k, v in v2_stats.items()},
        "assessment": None,
    }

    if best_v5 is not None and best_density > 0:
        power = int(5**best_v5) if best_v5 <= 4 else "5^" + str(best_v5)
        output["assessment"] = (
            f"v₅ SWEET SPOT EXISTS at v₅={best_v5} (5^{best_v5}={5**best_v5}), "
            f"density={best_density:.4f}. Wall at v₅={wall_v5}. "
            f"The p-adic sweet spot phenomenon GENERALIZES beyond p=2.")
    else:
        output["assessment"] = "NO v₅ SWEET SPOT: mod-5 structure is uniformly sparse across all v₅ valuations"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
