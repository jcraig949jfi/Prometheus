#!/usr/bin/env python3
"""
R4-1: Does the Gamma Wormhole Metric Satisfy the Triangle Inequality?

Tests whether CL5's Gamma-mediated distance matrix forms a genuine metric space.
A metric requires: (1) d(A,A)=0, (2) d(A,B)=d(B,A), (3) d(A,B)>0 for A!=B,
(4) d(A,C) <= d(A,B) + d(B,C) for all triples.

Violations reveal "shortcut" paths where Gamma connects domains through
non-obvious algebraic identities.
"""

import json
import itertools
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_FILE = SCRIPT_DIR / "gamma_wormhole_results.json"
OUT_FILE = SCRIPT_DIR / "gamma_triangle_results.json"


def load_distance_matrix():
    """Load and parse the Gamma distance matrix."""
    with open(DATA_FILE) as f:
        data = json.load(f)

    dm = data["gamma_distance_matrix"]
    modules = dm["modules"]
    raw = dm["distances"]

    # Build numeric matrix
    n = len(modules)
    D = {}
    for i, a in enumerate(modules):
        for j, b in enumerate(modules):
            D[(a, b)] = raw[a][b]

    return modules, D, raw


def test_identity(modules, D):
    """Test d(A,A) = 0 for all A."""
    violations = []
    for m in modules:
        val = D[(m, m)]
        if val != 0.0:
            violations.append({"module": m, "d_self": val})
    return violations


def test_symmetry(modules, D):
    """Test d(A,B) = d(B,A) for all pairs."""
    violations = []
    max_asym = 0.0
    for a, b in itertools.combinations(modules, 2):
        diff = abs(D[(a, b)] - D[(b, a)])
        max_asym = max(max_asym, diff)
        if diff > 1e-10:
            violations.append({
                "module_a": a, "module_b": b,
                "d_ab": D[(a, b)], "d_ba": D[(b, a)],
                "asymmetry": diff
            })
    violations.sort(key=lambda x: x["asymmetry"], reverse=True)
    return violations, max_asym


def test_positive_definiteness(modules, D):
    """Test d(A,B) > 0 for A != B."""
    violations = []
    for a, b in itertools.combinations(modules, 2):
        val = D[(a, b)]
        if val <= 0.0:
            violations.append({"module_a": a, "module_b": b, "distance": val})
    return violations


def test_triangle_inequality(modules, D):
    """Test d(A,C) <= d(A,B) + d(B,C) for all triples.

    Uses symmetrized distances: d_s(A,B) = (d(A,B)+d(B,A))/2
    and corrected distances: d_c(A,B) = d_s(A,B) - d_s(A,A)/2 - d_s(B,B)/2
    to handle non-zero self-distances.

    Also tests raw distances for comparison.
    """
    n = len(modules)

    # Symmetrize
    D_sym = {}
    for a in modules:
        for b in modules:
            D_sym[(a, b)] = (D[(a, b)] + D[(b, a)]) / 2.0

    # Correct for non-zero self-distances
    # d_corrected(A,B) = d_sym(A,B) - d_sym(A,A)/2 - d_sym(B,B)/2
    D_corr = {}
    for a in modules:
        for b in modules:
            D_corr[(a, b)] = D_sym[(a, b)] - D_sym[(a, a)] / 2 - D_sym[(b, b)] / 2

    # Test raw triangle inequality
    raw_violations = []
    raw_total = 0
    for a, b, c in itertools.permutations(modules, 3):
        raw_total += 1
        lhs = D[(a, c)]
        rhs = D[(a, b)] + D[(b, c)]
        if lhs > rhs + 1e-10:
            ratio = lhs / rhs if rhs > 0 else float('inf')
            raw_violations.append({
                "A": a, "B": b, "C": c,
                "d_AC": round(lhs, 6),
                "d_AB_plus_d_BC": round(rhs, 6),
                "excess": round(lhs - rhs, 6),
                "shortcut_ratio": round(ratio, 6)
            })

    raw_violations.sort(key=lambda x: x["shortcut_ratio"], reverse=True)

    # Test symmetrized triangle inequality
    sym_violations = []
    sym_total = 0
    for a, b, c in itertools.combinations(modules, 3):
        sym_total += 1
        # Check all 3 orientations
        for x, y, z in [(a, b, c), (a, c, b), (b, c, a)]:
            lhs = D_sym[(x, z)]
            rhs = D_sym[(x, y)] + D_sym[(y, z)]
            if lhs > rhs + 1e-10:
                ratio = lhs / rhs if rhs > 0 else float('inf')
                sym_violations.append({
                    "A": x, "B": y, "C": z,
                    "d_AC": round(lhs, 6),
                    "d_AB_plus_d_BC": round(rhs, 6),
                    "excess": round(lhs - rhs, 6),
                    "shortcut_ratio": round(ratio, 6)
                })

    sym_violations.sort(key=lambda x: x["shortcut_ratio"], reverse=True)

    # Test corrected triangle inequality
    corr_violations = []
    for a, b, c in itertools.combinations(modules, 3):
        for x, y, z in [(a, b, c), (a, c, b), (b, c, a)]:
            lhs = D_corr[(x, z)]
            rhs = D_corr[(x, y)] + D_corr[(y, z)]
            if lhs > rhs + 1e-10:
                ratio = lhs / rhs if rhs > 0 else float('inf')
                corr_violations.append({
                    "A": x, "B": y, "C": z,
                    "d_AC": round(lhs, 6),
                    "d_AB_plus_d_BC": round(rhs, 6),
                    "excess": round(lhs - rhs, 6),
                    "shortcut_ratio": round(ratio, 6)
                })

    corr_violations.sort(key=lambda x: x["shortcut_ratio"], reverse=True)

    return (raw_violations, raw_total,
            sym_violations, sym_total * 3,
            corr_violations, D_sym, D_corr)


def compute_violation_heatmap(violations, modules):
    """Which modules appear most in violations?"""
    counts = defaultdict(int)
    for v in violations:
        counts[v["A"]] += 1
        counts[v["C"]] += 1  # The endpoints of the violated inequality
    # Sort by count
    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return ranked


def compute_geodesics_and_diameter(modules, D_sym):
    """Floyd-Warshall for shortest paths through the module graph."""
    n = len(modules)
    idx = {m: i for i, m in enumerate(modules)}

    # Initialize distance matrix
    dist = [[float('inf')] * n for _ in range(n)]
    nxt = [[None] * n for _ in range(n)]

    for a in modules:
        for b in modules:
            i, j = idx[a], idx[b]
            if a == b:
                dist[i][j] = 0.0
                nxt[i][j] = j
            else:
                dist[i][j] = D_sym[(a, b)]
                nxt[i][j] = j

    # Floyd-Warshall
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    nxt[i][j] = nxt[i][k]

    # Extract diameter and path
    max_dist = 0.0
    max_i, max_j = 0, 0
    for i in range(n):
        for j in range(n):
            if i != j and dist[i][j] > max_dist:
                max_dist = dist[i][j]
                max_i, max_j = i, j

    # Reconstruct path
    def get_path(i, j):
        if nxt[i][j] is None:
            return []
        path = [i]
        while i != j:
            i = nxt[i][j]
            path.append(i)
        return [modules[p] for p in path]

    diameter_path = get_path(max_i, max_j)

    # Also find most-compressed pairs (shortest geodesic vs direct)
    compressions = []
    for a, b in itertools.combinations(modules, 2):
        i, j = idx[a], idx[b]
        direct = D_sym[(a, b)]
        geodesic = dist[i][j]
        if direct > geodesic + 1e-10:
            path = get_path(i, j)
            compressions.append({
                "from": a, "to": b,
                "direct": round(direct, 6),
                "geodesic": round(geodesic, 6),
                "compression": round(direct - geodesic, 6),
                "compression_ratio": round(direct / geodesic, 4) if geodesic > 0 else float('inf'),
                "path": path
            })
    compressions.sort(key=lambda x: x["compression"], reverse=True)

    return {
        "diameter": round(max_dist, 6),
        "diameter_endpoints": [modules[max_i], modules[max_j]],
        "diameter_path": diameter_path,
        "n_compressed_paths": len(compressions),
        "top_compressions": compressions[:20],
        "full_geodesic_matrix": {
            modules[i]: {modules[j]: round(dist[i][j], 6) for j in range(n)}
            for i in range(n)
        }
    }


def main():
    print("=" * 70)
    print("R4-1: GAMMA WORMHOLE TRIANGLE INEQUALITY TEST")
    print("=" * 70)

    modules, D, raw = load_distance_matrix()
    n = len(modules)
    print(f"\nModules: {n}")
    print(f"Total pairs: {n*(n-1)//2}")
    print(f"Total ordered triples: {n*(n-1)*(n-2)}")

    # === 1. Identity: d(A,A) = 0 ===
    print("\n--- TEST 1: Identity (d(A,A) = 0) ---")
    id_violations = test_identity(modules, D)
    print(f"Violations: {len(id_violations)} / {n}")
    if id_violations:
        for v in id_violations:
            print(f"  {v['module']}: d(self) = {v['d_self']:.6f}")
    zero_self = [m for m in modules if D[(m, m)] == 0.0]
    nonzero_self = [v for v in id_violations]
    print(f"Zero self-distance: {len(zero_self)} modules: {zero_self}")
    print(f"Non-zero self-distance: {len(nonzero_self)} modules")

    # === 2. Symmetry: d(A,B) = d(B,A) ===
    print("\n--- TEST 2: Symmetry (d(A,B) = d(B,A)) ---")
    sym_violations, max_asym = test_symmetry(modules, D)
    print(f"Non-symmetric pairs: {len(sym_violations)} / {n*(n-1)//2}")
    print(f"Max asymmetry: {max_asym:.6f}")
    if sym_violations:
        print("Top 10 asymmetric pairs:")
        for v in sym_violations[:10]:
            print(f"  {v['module_a']} <-> {v['module_b']}: "
                  f"d(A,B)={v['d_ab']:.6f}, d(B,A)={v['d_ba']:.6f}, "
                  f"asym={v['asymmetry']:.6f}")

    # === 3. Positive definiteness: d(A,B) > 0 for A != B ===
    print("\n--- TEST 3: Positive Definiteness (d(A,B) > 0 for A != B) ---")
    pd_violations = test_positive_definiteness(modules, D)
    print(f"Violations: {len(pd_violations)} / {n*(n-1)//2}")

    # === 4. Triangle Inequality ===
    print("\n--- TEST 4: Triangle Inequality ---")
    (raw_viol, raw_total,
     sym_viol, sym_total,
     corr_viol, D_sym, D_corr) = test_triangle_inequality(modules, D)

    print(f"\n  Raw distances:")
    print(f"    Violations: {len(raw_viol)} / {raw_total} ordered triples")
    print(f"    Violation rate: {100*len(raw_viol)/raw_total:.2f}%")
    if raw_viol:
        print(f"    Worst shortcut ratio: {raw_viol[0]['shortcut_ratio']:.6f}")
        print(f"    Top 10 violations:")
        for v in raw_viol[:10]:
            print(f"      d({v['A']},{v['C']}) = {v['d_AC']:.4f} > "
                  f"d({v['A']},{v['B']}) + d({v['B']},{v['C']}) = {v['d_AB_plus_d_BC']:.4f} "
                  f"  ratio={v['shortcut_ratio']:.4f}")

    print(f"\n  Symmetrized distances:")
    print(f"    Violations: {len(sym_viol)} / {sym_total} oriented triples")
    if sym_viol:
        print(f"    Worst shortcut ratio: {sym_viol[0]['shortcut_ratio']:.6f}")
        print(f"    Top 10 violations:")
        for v in sym_viol[:10]:
            print(f"      d({v['A']},{v['C']}) = {v['d_AC']:.4f} > "
                  f"d({v['A']},{v['B']}) + d({v['B']},{v['C']}) = {v['d_AB_plus_d_BC']:.4f} "
                  f"  ratio={v['shortcut_ratio']:.4f}")

    print(f"\n  Corrected distances (self-distance removed):")
    print(f"    Violations: {len(corr_viol)}")
    if corr_viol:
        print(f"    Worst shortcut ratio: {corr_viol[0]['shortcut_ratio']:.6f}")
        for v in corr_viol[:10]:
            print(f"      d({v['A']},{v['C']}) = {v['d_AC']:.4f} > "
                  f"d({v['A']},{v['B']}) + d({v['B']},{v['C']}) = {v['d_AB_plus_d_BC']:.4f} "
                  f"  ratio={v['shortcut_ratio']:.4f}")

    # === 5. Violation heatmap (who violates most?) ===
    print("\n--- VIOLATION HEATMAP ---")
    if raw_viol:
        heatmap = compute_violation_heatmap(raw_viol, modules)
        print("Modules most involved in violations (as endpoints):")
        for m, c in heatmap[:10]:
            print(f"  {m}: {c} violations")

        # Check if specific modules are systematic violators
        b_modules = defaultdict(int)
        for v in raw_viol:
            b_modules[v["B"]] += 1
        b_ranked = sorted(b_modules.items(), key=lambda x: x[1], reverse=True)
        print("\nModules most involved as intermediary B (shortcut bypass):")
        for m, c in b_ranked[:10]:
            print(f"  {m}: {c} times bypassed")

    # === 6. Geodesics and diameter ===
    print("\n--- GEODESICS & DIAMETER ---")
    geo = compute_geodesics_and_diameter(modules, D_sym)
    print(f"Diameter: {geo['diameter']:.6f}")
    print(f"Most distant pair: {geo['diameter_endpoints']}")
    print(f"Geodesic path: {' -> '.join(geo['diameter_path'])}")
    print(f"\nPaths compressed by transiting through intermediaries: {geo['n_compressed_paths']}")
    if geo['top_compressions']:
        print("Top compressions (direct distance >> geodesic):")
        for c in geo['top_compressions'][:10]:
            print(f"  {c['from']} -> {c['to']}: "
                  f"direct={c['direct']:.4f}, geodesic={c['geodesic']:.4f}, "
                  f"ratio={c['compression_ratio']:.3f}x")
            print(f"    via: {' -> '.join(c['path'])}")

    # === 7. Summary interpretation ===
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    is_metric = (len(id_violations) == 0 and len(sym_violations) == 0
                 and len(pd_violations) == 0 and len(raw_viol) == 0)

    if is_metric:
        print("The Gamma wormhole distance is a genuine METRIC.")
    else:
        issues = []
        if id_violations:
            issues.append(f"identity fails ({len(id_violations)}/{n} modules have d(A,A)!=0)")
        if sym_violations:
            issues.append(f"symmetry fails ({len(sym_violations)} asymmetric pairs)")
        if pd_violations:
            issues.append(f"positive definiteness fails ({len(pd_violations)} pairs)")
        if raw_viol:
            issues.append(f"triangle inequality fails ({len(raw_viol)} violations)")
        print(f"NOT a metric. Issues: {'; '.join(issues)}")

        # But check if it's a quasimetric or semimetric
        if len(raw_viol) == 0 and len(sym_violations) > 0:
            print("-> It IS a quasimetric (triangle holds, symmetry fails).")
        if len(raw_viol) == 0 and len(id_violations) > 0:
            print("-> It IS a pseudometric modulo self-distances.")

    # === Save results ===
    results = {
        "meta": {
            "test": "R4-1 Triangle Inequality",
            "n_modules": n,
            "modules": modules,
            "total_ordered_triples": raw_total
        },
        "identity_test": {
            "n_violations": len(id_violations),
            "zero_self_modules": zero_self,
            "nonzero_self_modules": [v["module"] for v in nonzero_self],
            "violations": id_violations
        },
        "symmetry_test": {
            "n_violations": len(sym_violations),
            "max_asymmetry": round(max_asym, 10),
            "is_symmetric": len(sym_violations) == 0,
            "top_violations": sym_violations[:20]
        },
        "positive_definiteness_test": {
            "n_violations": len(pd_violations),
            "is_positive_definite": len(pd_violations) == 0,
            "violations": pd_violations
        },
        "triangle_inequality": {
            "raw": {
                "n_violations": len(raw_viol),
                "n_tested": raw_total,
                "violation_rate": round(len(raw_viol) / raw_total, 6) if raw_total > 0 else 0,
                "worst_ratio": raw_viol[0]["shortcut_ratio"] if raw_viol else None,
                "top_violations": raw_viol[:30]
            },
            "symmetrized": {
                "n_violations": len(sym_viol),
                "worst_ratio": sym_viol[0]["shortcut_ratio"] if sym_viol else None,
                "top_violations": sym_viol[:30]
            },
            "corrected": {
                "n_violations": len(corr_viol),
                "worst_ratio": corr_viol[0]["shortcut_ratio"] if corr_viol else None,
                "top_violations": corr_viol[:20]
            }
        },
        "violation_heatmap": {
            "endpoint_counts": compute_violation_heatmap(raw_viol, modules) if raw_viol else [],
            "intermediary_counts": sorted(
                [(v["B"], sum(1 for x in raw_viol if x["B"] == v["B"]))
                 for v in raw_viol[:1]],  # just get unique Bs
                key=lambda x: x[1], reverse=True
            ) if raw_viol else []
        },
        "geodesics": {
            "diameter": geo["diameter"],
            "diameter_endpoints": geo["diameter_endpoints"],
            "diameter_path": geo["diameter_path"],
            "n_compressed_paths": geo["n_compressed_paths"],
            "top_compressions": geo["top_compressions"]
        },
        "is_metric": is_metric,
        "classification": (
            "metric" if is_metric
            else "quasimetric" if len(raw_viol) == 0 and len(sym_violations) > 0
            else "semimetric" if len(sym_violations) == 0 and len(raw_viol) > 0
            else "pre-metric (multiple failures)"
        )
    }

    # Compute proper heatmap for violations
    if raw_viol:
        endpoint_map = defaultdict(int)
        intermediary_map = defaultdict(int)
        for v in raw_viol:
            endpoint_map[v["A"]] += 1
            endpoint_map[v["C"]] += 1
            intermediary_map[v["B"]] += 1
        results["violation_heatmap"] = {
            "endpoint_counts": sorted(endpoint_map.items(), key=lambda x: x[1], reverse=True),
            "intermediary_counts": sorted(intermediary_map.items(), key=lambda x: x[1], reverse=True),
            "systematic": len(set(v["A"] for v in raw_viol) | set(v["C"] for v in raw_viol)) < n,
            "n_endpoint_modules": len(endpoint_map),
            "n_intermediary_modules": len(intermediary_map)
        }

    with open(OUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_FILE}")


if __name__ == "__main__":
    main()
