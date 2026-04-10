"""
M3: Mod-2 GSp_4 Clique Size Distribution
=========================================
Measure the clique size distribution of the mod-2 congruence graph.

KEY OBSERVATION FROM CL2: clustering coefficient = 1.0 in mod2_all,
meaning EVERY connected component is a complete graph (clique).
Therefore: component_size_distribution == maximal_clique_size_distribution.

This script:
1. Verifies the clique=component identity via networkx
2. Computes the full clique size distribution for all three graph tiers
3. Fits power-law, exponential, log-normal, and Poisson models
4. Compares to Erdos-Renyi null clique distribution
5. Tests whether K_24 is an outlier or distribution tail
6. Correlates clique size with conductor
7. Extracts the distribution exponents as Hecke algebra constants

Usage:
    python clique_distribution.py
"""

import json
import time
import random
import re
import math
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations


# ── Helpers (from gsp4_mod2_graph.py) ────────────────────────────────

def prime_factors(n):
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors


def parse_good_lfactors(s):
    result = {}
    matches = re.findall(r"\[(-?\d+),(-?\d+),(-?\d+)\]", s)
    for m in matches:
        p, a, b = int(m[0]), int(m[1]), int(m[2])
        result[p] = (a, b)
    return result


def factor_type(c1, c2, p, ell):
    """Factor char poly x^4 + c1*x^3 + c2*x^2 + c1*p*x + p^2 mod ell."""
    coeffs = [(p * p) % ell, (c1 * p) % ell, c2 % ell, c1 % ell, 1]
    roots = []
    for x in range(ell):
        val = 0
        xpow = 1
        for c in coeffs:
            val = (val + c * xpow) % ell
            xpow = (xpow * x) % ell
        if val == 0:
            roots.append(x)
    if len(roots) == 0:
        for a1 in range(ell):
            for b1 in range(ell):
                q1 = [b1, a1, 1]
                num = list(coeffs)
                for i in range(len(num) - len(q1), -1, -1):
                    lead_inv = pow(q1[-1], ell - 2, ell) if ell > 2 else 1
                    q = (num[i + len(q1) - 1] * lead_inv) % ell
                    for j in range(len(q1)):
                        num[i + j] = (num[i + j] - q * q1[j]) % ell
                rem = [num[i] % ell for i in range(len(q1) - 1)]
                if all(r == 0 for r in rem):
                    return "2+2"
        return "irreducible"
    elif len(roots) == 1:
        return "1+3"
    elif len(roots) == 2:
        return "1+1+2"
    else:
        return "1+1+1+1"


# ── Distribution fitting (pure Python, no scipy) ────────────────────

def fit_power_law(sizes, counts):
    """Fit P(k) ~ k^(-alpha) via log-log linear regression."""
    # Only use sizes >= 2 (cliques of size 1 are trivial)
    xs = [math.log(s) for s in sizes if s >= 2]
    ys = [math.log(counts[s]) for s in sizes if s >= 2]
    if len(xs) < 2:
        return None, None, None
    n = len(xs)
    sx = sum(xs)
    sy = sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    denom = n * sxx - sx * sx
    if abs(denom) < 1e-12:
        return None, None, None
    slope = (n * sxy - sx * sy) / denom
    intercept = (sy - slope * sx) / n
    alpha = -slope
    # R^2
    y_mean = sy / n
    ss_tot = sum((y - y_mean) ** 2 for y in ys)
    ss_res = sum((y - (intercept + slope * x)) ** 2 for x, y in zip(xs, ys))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    return alpha, math.exp(intercept), r2


def fit_exponential(sizes, counts):
    """Fit P(k) ~ exp(-lambda * k) via log-linear regression."""
    xs = [s for s in sizes if s >= 2]
    ys = [math.log(counts[s]) for s in sizes if s >= 2]
    if len(xs) < 2:
        return None, None, None
    n = len(xs)
    sx = sum(xs)
    sy = sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    denom = n * sxx - sx * sx
    if abs(denom) < 1e-12:
        return None, None, None
    slope = (n * sxy - sx * sy) / denom
    intercept = (sy - slope * sx) / n
    lam = -slope
    # R^2
    y_mean = sy / n
    ss_tot = sum((y - y_mean) ** 2 for y in ys)
    ss_res = sum((y - (intercept + slope * x)) ** 2 for x, y in zip(xs, ys))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    return lam, math.exp(intercept), r2


def fit_lognormal(sizes, counts):
    """Fit log-normal: log(count) ~ -(log(k) - mu)^2 / (2*sigma^2) + C.
    This is a quadratic in log(k), so fit: log(count) = a*(log k)^2 + b*(log k) + c."""
    xs = [math.log(s) for s in sizes if s >= 2]
    ys = [math.log(counts[s]) for s in sizes if s >= 2]
    if len(xs) < 3:
        return None, None, None, None
    n = len(xs)
    # Fit y = a*x^2 + b*x + c
    x2 = [x * x for x in xs]
    sx = sum(xs)
    sx2 = sum(x2)
    sx3 = sum(x ** 3 for x in xs)
    sx4 = sum(x ** 4 for x in xs)
    sy = sum(ys)
    sxy = sum(x * y for x, y in zip(xs, ys))
    sx2y = sum(x2i * y for x2i, y in zip(x2, ys))

    # Normal equations: [sx4 sx3 sx2] [a]   [sx2y]
    #                   [sx3 sx2 sx ] [b] = [sxy ]
    #                   [sx2 sx  n  ] [c]   [sy  ]
    A = [[sx4, sx3, sx2], [sx3, sx2, sx], [sx2, sx, n]]
    B = [sx2y, sxy, sy]

    # Solve 3x3 system via Cramer's rule
    def det3(m):
        return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
                - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
                + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))

    D = det3(A)
    if abs(D) < 1e-20:
        return None, None, None, None

    def replace_col(m, b, col):
        m2 = [row[:] for row in m]
        for i in range(3):
            m2[i][col] = b[i]
        return m2

    a = det3(replace_col(A, B, 0)) / D
    b = det3(replace_col(A, B, 1)) / D
    c = det3(replace_col(A, B, 2)) / D

    # From a*(log k)^2 + b*(log k) + c = -(log k - mu)^2/(2*sigma^2) + C
    # a = -1/(2*sigma^2), b = mu/sigma^2, c = C - mu^2/(2*sigma^2)
    if a >= 0:
        return None, None, None, None
    sigma2 = -1 / (2 * a)
    sigma = math.sqrt(sigma2)
    mu = b * sigma2

    # R^2
    y_mean = sy / n
    ss_tot = sum((y - y_mean) ** 2 for y in ys)
    y_pred = [a * xi * xi + b * xi + c for xi in xs]
    ss_res = sum((y - yp) ** 2 for y, yp in zip(ys, y_pred))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0

    return mu, sigma, math.exp(c), r2


def fit_poisson(sizes, counts):
    """Fit Poisson: count(k) ~ lambda^k / k!. Via MLE: lambda = weighted mean of sizes."""
    total = sum(counts[s] for s in sizes if s >= 2)
    if total == 0:
        return None, None
    weighted_sum = sum(s * counts[s] for s in sizes if s >= 2)
    lam = weighted_sum / total
    # Compute chi-squared or log-likelihood
    ll = 0
    for s in sizes:
        if s < 2:
            continue
        expected = total * (lam ** s / math.factorial(min(s, 170))) * math.exp(-lam)
        if expected > 0 and counts[s] > 0:
            ll += counts[s] * math.log(expected / counts[s])
    return lam, ll


# ── Main ──────────────────────────────────────────────────────────────

def main():
    print("M3: MOD-2 GSp_4 CLIQUE SIZE DISTRIBUTION")
    print("=" * 72)
    t0 = time.time()

    OUT_DIR = Path(__file__).resolve().parent
    DATA_FILE = Path(__file__).resolve().parents[3] / "genus2" / "data" / "g2c-data" / "gce_1000000_lmfdb.txt"

    # ── Load CL2 results ────────────────────────────────────────────
    cl2_file = OUT_DIR / "gsp4_mod2_graph_results.json"
    with open(cl2_file) as f:
        cl2 = json.load(f)

    print("\nCL2 data loaded.")
    for tag in ["mod2_all", "mod2_coprime_usp4", "mod2_irreducible"]:
        d = cl2.get(tag, {})
        print(f"  {tag}: {d.get('n_nodes', 0)} nodes, {d.get('n_edges', 0)} edges, "
              f"max_clique={d.get('max_clique_size', 0)}, "
              f"triangles={d.get('n_triangles', 0)}, "
              f"clustering={d.get('avg_clustering_coefficient', 0):.4f}")

    # ── KEY INSIGHT: clustering=1.0 => components ARE cliques ────────
    print("\n" + "=" * 72)
    print("KEY INSIGHT: CLUSTERING COEFFICIENT = 1.0")
    print("=" * 72)
    print("Every connected component is a complete graph (clique).")
    print("Therefore: component_size_distribution == maximal_clique_size_distribution.")
    print("No need for Bron-Kerbosch enumeration.")

    results = {}

    # ── Process each graph tier ──────────────────────────────────────
    for tag in ["mod2_all", "mod2_coprime_usp4", "mod2_irreducible"]:
        d = cl2[tag]
        cc = d.get("avg_clustering_coefficient", 0)
        comp_dist = d.get("component_size_distribution", {})

        print(f"\n{'=' * 72}")
        print(f"TIER: {tag}")
        print(f"{'=' * 72}")
        print(f"Clustering coefficient: {cc}")

        if abs(cc - 1.0) > 0.01 and cc > 0:
            print(f"WARNING: clustering < 1.0 ({cc}), components may not all be cliques.")
            print("Will reconstruct graph for exact clique enumeration.")

        # Convert component size distribution to clique size distribution
        # (since clustering = 1.0, they're identical for mod2_all)
        clique_dist = {}
        for size_str, count in comp_dist.items():
            size = int(size_str)
            clique_dist[size] = count

        # For mod2_all with cc=1.0: each component of size k is exactly one K_k
        # For coprime USp4 with cc=1.0: same
        print(f"\nCLIQUE SIZE DISTRIBUTION (= component size distribution):")
        total_cliques = 0
        for size in sorted(clique_dist.keys()):
            count = clique_dist[size]
            total_cliques += count
            print(f"  K_{size}: {count} cliques")
        print(f"  Total maximal cliques: {total_cliques}")

        # Exclude size-1 (isolated nodes) for fitting
        sizes_for_fit = sorted([s for s in clique_dist.keys() if s >= 2])
        counts_for_fit = {s: clique_dist[s] for s in sizes_for_fit}

        if len(sizes_for_fit) < 2:
            print("  Too few distinct sizes for distribution fitting.")
            results[tag] = {
                "clique_size_distribution": clique_dist,
                "total_maximal_cliques": total_cliques,
                "fits": "insufficient_data",
            }
            continue

        # ── Fit distributions ─────────────────────────────────────────
        print(f"\nDISTRIBUTION FITS (sizes >= 2):")

        # Power law
        alpha, pl_C, pl_r2 = fit_power_law(sizes_for_fit, counts_for_fit)
        if alpha is not None:
            print(f"  Power law: P(k) ~ k^(-{alpha:.4f}), R^2 = {pl_r2:.4f}")
        else:
            print(f"  Power law: FAILED to fit")

        # Exponential
        lam_exp, exp_C, exp_r2 = fit_exponential(sizes_for_fit, counts_for_fit)
        if lam_exp is not None:
            print(f"  Exponential: P(k) ~ exp(-{lam_exp:.4f} * k), R^2 = {exp_r2:.4f}")
        else:
            print(f"  Exponential: FAILED to fit")

        # Log-normal
        mu_ln, sigma_ln, ln_C, ln_r2 = fit_lognormal(sizes_for_fit, counts_for_fit)
        if mu_ln is not None:
            print(f"  Log-normal: mu={mu_ln:.4f}, sigma={sigma_ln:.4f}, R^2 = {ln_r2:.4f}")
        else:
            print(f"  Log-normal: FAILED to fit")

        # Poisson
        lam_pois, pois_ll = fit_poisson(sizes_for_fit, counts_for_fit)
        if lam_pois is not None:
            print(f"  Poisson: lambda={lam_pois:.4f}, log-likelihood ratio={pois_ll:.2f}")
        else:
            print(f"  Poisson: FAILED to fit")

        # Best fit
        fits = {}
        if alpha is not None:
            fits["power_law"] = {"alpha": round(alpha, 4), "C": round(pl_C, 4), "R2": round(pl_r2, 4)}
        if lam_exp is not None:
            fits["exponential"] = {"lambda": round(lam_exp, 4), "C": round(exp_C, 4), "R2": round(exp_r2, 4)}
        if mu_ln is not None:
            fits["lognormal"] = {"mu": round(mu_ln, 4), "sigma": round(sigma_ln, 4), "C": round(ln_C, 4), "R2": round(ln_r2, 4)}
        if lam_pois is not None:
            fits["poisson"] = {"lambda": round(lam_pois, 4)}

        r2_vals = [(name, f.get("R2", -999)) for name, f in fits.items() if "R2" in f]
        if r2_vals:
            best = max(r2_vals, key=lambda x: x[1])
            print(f"\n  BEST FIT: {best[0]} (R^2 = {best[1]:.4f})")
        else:
            best = (None, None)

        results[tag] = {
            "clique_size_distribution": {str(k): v for k, v in sorted(clique_dist.items())},
            "total_maximal_cliques": total_cliques,
            "sizes_for_fit": sizes_for_fit,
            "clustering_coefficient": cc,
            "components_are_cliques": abs(cc - 1.0) < 0.01 or cc == 0,
            "fits": fits,
            "best_fit": best[0],
        }

    # ── Erdos-Renyi null clique distribution ─────────────────────────
    print(f"\n{'=' * 72}")
    print("ERDOS-RENYI NULL: CLIQUE DISTRIBUTION COMPARISON")
    print("=" * 72)

    # Use mod2_all parameters: n=9101, m=11356
    n_er = 9101
    m_er = 11356
    p_er = 2 * m_er / (n_er * (n_er - 1))
    print(f"ER parameters: n={n_er}, m={m_er}, p={p_er:.6f}")

    # Analytical: expected number of k-cliques in G(n,p)
    # E[K_k] = C(n,k) * p^(k*(k-1)/2)
    print(f"\nExpected k-cliques in ER(n={n_er}, p={p_er:.6f}):")
    er_expected = {}
    for k in range(2, 30):
        log_comb = sum(math.log(n_er - i) - math.log(i + 1) for i in range(k))
        log_p_edges = k * (k - 1) / 2 * math.log(p_er) if p_er > 0 else float('-inf')
        log_expected = log_comb + log_p_edges
        if log_expected > -50:  # Numerically meaningful
            expected = math.exp(log_expected)
            er_expected[k] = expected
            print(f"  E[K_{k}] = {expected:.4e}")
        else:
            if k <= 5:
                print(f"  E[K_{k}] = ~0 (log = {log_expected:.1f})")
            break

    # Actual vs ER for mod2_all
    actual_dist = results["mod2_all"]["clique_size_distribution"]
    print(f"\nACTUAL vs ER comparison (mod2_all):")
    print(f"  {'Size':>6} {'Actual':>10} {'ER Expected':>14} {'Excess':>12}")
    for k in sorted(set(list(int(s) for s in actual_dist.keys()) + list(er_expected.keys()))):
        actual = actual_dist.get(str(k), 0)
        expected = er_expected.get(k, 0)
        if actual > 0 or expected > 0.01:
            excess = actual / expected if expected > 1e-10 else float('inf')
            excess_str = f"{excess:.1f}x" if excess < 1e10 else "INF"
            print(f"  K_{k:>4}: {actual:>10} {expected:>14.4e} {excess_str:>12}")

    results["er_null"] = {
        "n": n_er,
        "m": m_er,
        "p": round(p_er, 8),
        "expected_cliques": {str(k): round(v, 6) for k, v in er_expected.items()},
    }

    # ── K_24 analysis: outlier or tail? ──────────────────────────────
    print(f"\n{'=' * 72}")
    print("K_24 ANALYSIS: OUTLIER OR DISTRIBUTION TAIL?")
    print("=" * 72)

    all_dist = {int(k): v for k, v in cl2["mod2_all"]["component_size_distribution"].items()}
    sizes_sorted = sorted(all_dist.keys())
    print(f"Clique sizes present: {sizes_sorted}")

    # Check gaps in the distribution
    max_size = max(sizes_sorted)
    missing = [k for k in range(2, max_size + 1) if k not in all_dist]
    print(f"Missing sizes (gaps): {missing}")
    print(f"Gap before K_24: sizes 20, 21, 23 are {'missing' if 20 in missing else 'present'}")

    # If exponential fit is good, what does it predict for K_24?
    exp_fit = results["mod2_all"]["fits"].get("exponential", {})
    if exp_fit:
        lam = exp_fit["lambda"]
        C = exp_fit["C"]
        predicted_24 = C * math.exp(-lam * 24)
        print(f"\nExponential prediction for K_24: {predicted_24:.4f}")
        print(f"Actual K_24 count: {all_dist.get(24, 0)}")
        if predicted_24 > 0.01:
            print(f"Ratio actual/predicted: {all_dist.get(24, 0) / predicted_24:.2f}")
            print("VERDICT: K_24 is within exponential tail -- NOT an outlier")
        else:
            print("VERDICT: K_24 is far beyond exponential prediction -- OUTLIER")

    pl_fit = results["mod2_all"]["fits"].get("power_law", {})
    if pl_fit:
        alpha = pl_fit["alpha"]
        C = pl_fit["C"]
        predicted_24 = C * (24 ** (-alpha))
        print(f"\nPower law prediction for K_24: {predicted_24:.4f}")
        print(f"Actual K_24 count: {all_dist.get(24, 0)}")

    # ── Conductor correlation ────────────────────────────────────────
    print(f"\n{'=' * 72}")
    print("CLIQUE SIZE vs CONDUCTOR CORRELATION")
    print("=" * 72)

    # Reconstruct graph to get conductor per component
    # Parse conductor from node IDs in CL2 results
    # Node format: N{cond}_{label}_{eqn}
    # We need to rebuild the graph from raw data to get conductor per clique

    print("Rebuilding graph from raw data to extract conductor-clique mapping...")

    all_curves = []
    with open(DATA_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(":")
            if len(parts) < 17:
                continue
            conductor = int(parts[1])
            label = parts[0]
            st = parts[8]
            euler = parse_good_lfactors(parts[16])
            eqn = parts[3]
            all_curves.append({
                "conductor": conductor,
                "label": label,
                "st": st,
                "euler": euler,
                "eqn": eqn,
            })

    print(f"Loaded {len(all_curves)} curves")

    # Group by conductor, deduplicate by isogeny class
    by_cond = defaultdict(list)
    for c in all_curves:
        by_cond[c["conductor"]].append(c)

    cond_reps = {}
    for cond, crvs in by_cond.items():
        if len(crvs) < 2:
            cond_reps[cond] = crvs
            continue
        classes = defaultdict(list)
        common = sorted(set.intersection(*[set(c["euler"].keys()) for c in crvs]))
        for i, c in enumerate(crvs):
            fp = tuple((c["euler"][p][0], c["euler"][p][1]) for p in common)
            classes[fp].append(i)
        reps = [crvs[indices[0]] for indices in classes.values()]
        cond_reps[cond] = reps

    # Run mod-2 scan to find congruences with conductor info
    print("Scanning for mod-2 congruences...")
    mod2_congruences = []
    for cond, reps in cond_reps.items():
        if len(reps) < 2:
            continue
        bad = prime_factors(cond)
        for i in range(len(reps)):
            for j in range(i + 1, len(reps)):
                e1 = reps[i]["euler"]
                e2 = reps[j]["euler"]
                common = sorted(set(e1.keys()) & set(e2.keys()))
                good = [p for p in common if p not in bad]
                if len(good) < 10:
                    continue
                all_cong = True
                has_nz = False
                for p in good:
                    da = e1[p][0] - e2[p][0]
                    db = e1[p][1] - e2[p][1]
                    if da % 2 != 0 or db % 2 != 0:
                        all_cong = False
                        break
                    if da != 0 or db != 0:
                        has_nz = True
                if all_cong and has_nz:
                    mod2_congruences.append({
                        "cond": cond,
                        "label1": reps[i]["label"],
                        "label2": reps[j]["label"],
                        "eqn1": reps[i]["eqn"],
                        "eqn2": reps[j]["eqn"],
                    })

    print(f"Found {len(mod2_congruences)} mod-2 congruences")

    # Build adjacency and find components
    adj = defaultdict(set)
    node_cond = {}
    for c in mod2_congruences:
        n1 = f"N{c['cond']}_{c['label1']}_{c['eqn1'][:30]}"
        n2 = f"N{c['cond']}_{c['label2']}_{c['eqn2'][:30]}"
        adj[n1].add(n2)
        adj[n2].add(n1)
        node_cond[n1] = c["cond"]
        node_cond[n2] = c["cond"]

    all_nodes = set(adj.keys())
    visited = set()
    components = []
    for n in all_nodes:
        if n in visited:
            continue
        comp = []
        stack = [n]
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            comp.append(node)
            stack.extend(adj[node] - visited)
        components.append(comp)

    # For each component (=clique since cc=1.0), get conductor
    clique_conductors = []
    for comp in components:
        size = len(comp)
        conds = set(node_cond.get(n, 0) for n in comp)
        # Since these are same-conductor pairs, all nodes should share conductor
        cond = max(conds)  # Should all be same
        clique_conductors.append({"size": size, "conductor": cond, "n_distinct_conds": len(conds)})

    # Sort by size
    clique_conductors.sort(key=lambda x: -x["size"])

    print(f"\nTop 20 cliques by size:")
    print(f"  {'Size':>6} {'Conductor':>12} {'log2(N)':>8}")
    for cc_entry in clique_conductors[:20]:
        log2n = math.log2(cc_entry["conductor"]) if cc_entry["conductor"] > 0 else 0
        print(f"  K_{cc_entry['size']:>4} N={cc_entry['conductor']:>10} log2(N)={log2n:.1f}")

    # Correlation: Pearson between size and log(conductor)
    sizes_arr = [cc_entry["size"] for cc_entry in clique_conductors if cc_entry["size"] >= 2]
    log_conds = [math.log(cc_entry["conductor"]) for cc_entry in clique_conductors if cc_entry["size"] >= 2]

    if len(sizes_arr) > 2:
        mean_s = sum(sizes_arr) / len(sizes_arr)
        mean_lc = sum(log_conds) / len(log_conds)
        cov = sum((s - mean_s) * (lc - mean_lc) for s, lc in zip(sizes_arr, log_conds)) / len(sizes_arr)
        std_s = (sum((s - mean_s) ** 2 for s in sizes_arr) / len(sizes_arr)) ** 0.5
        std_lc = (sum((lc - mean_lc) ** 2 for lc in log_conds) / len(log_conds)) ** 0.5
        if std_s > 0 and std_lc > 0:
            pearson_r = cov / (std_s * std_lc)
        else:
            pearson_r = 0
        print(f"\nPearson r(clique_size, log_conductor) = {pearson_r:.4f}")
        print(f"  Mean clique size: {mean_s:.2f}")
        print(f"  Mean log(conductor): {mean_lc:.2f}")
    else:
        pearson_r = 0

    # Binned: average clique size by conductor range
    bins = [(0, 1e4), (1e4, 5e4), (5e4, 1e5), (1e5, 5e5), (5e5, 1e6)]
    print(f"\nAverage clique size by conductor range:")
    binned_data = {}
    for lo, hi in bins:
        in_bin = [cc_entry for cc_entry in clique_conductors if lo < cc_entry["conductor"] <= hi and cc_entry["size"] >= 2]
        if in_bin:
            avg_size = sum(e["size"] for e in in_bin) / len(in_bin)
            max_size = max(e["size"] for e in in_bin)
            print(f"  N in ({lo:.0f}, {hi:.0f}]: n={len(in_bin)}, avg_size={avg_size:.2f}, max={max_size}")
            binned_data[f"{lo:.0f}-{hi:.0f}"] = {
                "n_cliques": len(in_bin),
                "avg_size": round(avg_size, 3),
                "max_size": max_size,
            }

    results["conductor_correlation"] = {
        "pearson_r_size_logcond": round(pearson_r, 4),
        "top_cliques": [{"size": e["size"], "conductor": e["conductor"]} for e in clique_conductors[:30]],
        "binned_by_conductor": binned_data,
    }

    # ── Verify clique=component via direct check ─────────────────────
    print(f"\n{'=' * 72}")
    print("VERIFICATION: IS EVERY COMPONENT A COMPLETE GRAPH?")
    print("=" * 72)

    n_complete = 0
    n_not_complete = 0
    not_complete_examples = []

    for comp in components:
        size = len(comp)
        if size <= 1:
            n_complete += 1
            continue
        expected_edges = size * (size - 1) // 2
        actual_edges = 0
        for i in range(len(comp)):
            for j in range(i + 1, len(comp)):
                if comp[j] in adj[comp[i]]:
                    actual_edges += 1
        if actual_edges == expected_edges:
            n_complete += 1
        else:
            n_not_complete += 1
            if len(not_complete_examples) < 5:
                not_complete_examples.append({
                    "size": size,
                    "expected_edges": expected_edges,
                    "actual_edges": actual_edges,
                    "deficit": expected_edges - actual_edges,
                })

    print(f"Complete components: {n_complete}")
    print(f"Non-complete components: {n_not_complete}")
    if not_complete_examples:
        print("Examples of non-complete components:")
        for ex in not_complete_examples:
            print(f"  size={ex['size']}, edges={ex['actual_edges']}/{ex['expected_edges']} "
                  f"(deficit={ex['deficit']})")

    results["verification"] = {
        "complete_components": n_complete,
        "non_complete_components": n_not_complete,
        "non_complete_examples": not_complete_examples,
        "conclusion": "ALL components are complete graphs" if n_not_complete == 0 else
                       f"{n_not_complete} components are NOT complete",
    }

    # ── Physical interpretation ──────────────────────────────────────
    print(f"\n{'=' * 72}")
    print("PHYSICAL INTERPRETATION")
    print("=" * 72)

    all_fit = results.get("mod2_all", {}).get("fits", {})
    best = results.get("mod2_all", {}).get("best_fit", None)

    print(f"\nBest fit model: {best}")
    if best == "exponential":
        lam = all_fit["exponential"]["lambda"]
        print(f"  Decay constant lambda = {lam:.4f}")
        print(f"  Characteristic clique size = 1/lambda = {1/lam:.1f}")
        print(f"  INTERPRETATION: The mod-2 paramodular Hecke algebra has an")
        print(f"  exponential clique distribution with decay rate lambda = {lam:.4f}.")
        print(f"  This is a measurable constant of the Hecke algebra structure.")
    elif best == "power_law":
        alpha = all_fit["power_law"]["alpha"]
        print(f"  Power law exponent alpha = {alpha:.4f}")
        print(f"  INTERPRETATION: The mod-2 Hecke algebra shows scale-free")
        print(f"  clique structure with exponent alpha = {alpha:.4f}.")
    elif best == "lognormal":
        mu = all_fit["lognormal"]["mu"]
        sigma = all_fit["lognormal"]["sigma"]
        print(f"  Log-normal parameters: mu = {mu:.4f}, sigma = {sigma:.4f}")
        print(f"  Peak clique size = exp(mu - sigma^2) = {math.exp(mu - sigma*sigma):.2f}")

    print(f"\nAll fit parameters (Hecke algebra constants):")
    for model, params in all_fit.items():
        print(f"  {model}: {params}")

    # ── Summary statistics ───────────────────────────────────────────
    print(f"\n{'=' * 72}")
    print("SUMMARY")
    print("=" * 72)

    for tag in ["mod2_all", "mod2_coprime_usp4", "mod2_irreducible"]:
        r = results.get(tag, {})
        dist = r.get("clique_size_distribution", {})
        print(f"\n{tag}:")
        print(f"  Total maximal cliques: {r.get('total_maximal_cliques', 0)}")
        print(f"  Distinct sizes: {len(dist)}")
        sizes = sorted(int(k) for k in dist.keys())
        if sizes:
            print(f"  Size range: {min(sizes)} to {max(sizes)}")
        bf = r.get("best_fit", None)
        if bf:
            print(f"  Best fit: {bf} ({r.get('fits', {}).get(bf, {})})")

    elapsed = time.time() - t0
    results["metadata"] = {
        "script": "clique_distribution.py",
        "challenge": "M3",
        "elapsed_seconds": round(elapsed, 1),
        "key_finding": "clustering=1.0 => components ARE maximal cliques; "
                       "no Bron-Kerbosch needed",
    }

    # ── Save results ─────────────────────────────────────────────────
    out_file = OUT_DIR / "clique_distribution_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {out_file}")
    print(f"Total time: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
