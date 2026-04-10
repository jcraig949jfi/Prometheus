"""
M11: Cross-Domain Moment Matching
ALL-048 / ChatGPT Part 3 #6

Do distributions cluster across mathematical domains?
Compute 6-moment vectors per object from OEIS, EC, Knots, Maass,
pool and cluster, measure cross-domain mixing.
"""

import sys
import json
import math
import random
import numpy as np

sys.stdout.reconfigure(line_buffering=True)

from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[2]  # F:/Prometheus
OUT  = Path(__file__).resolve().parent / "cross_domain_moments_results.json"

random.seed(42)
np.random.seed(42)


# ── Pure numpy k-means (avoids sklearn threading issues on Windows) ──

def kmeans_numpy(X, k, n_init=3, max_iter=100):
    """Simple k-means in pure numpy."""
    n, d = X.shape
    best_labels = None
    best_inertia = np.inf
    for _ in range(n_init):
        # k-means++ init
        centers = [X[np.random.randint(n)]]
        for _ in range(1, k):
            dists = np.min([np.sum((X - c)**2, axis=1) for c in centers], axis=0)
            probs = dists / dists.sum()
            idx = np.random.choice(n, p=probs)
            centers.append(X[idx])
        centers = np.array(centers)

        for _ in range(max_iter):
            # assign
            dists = np.array([np.sum((X - c)**2, axis=1) for c in centers])  # (k, n)
            labels = np.argmin(dists, axis=0)
            # update
            new_centers = np.zeros_like(centers)
            for j in range(k):
                mask = labels == j
                if mask.sum() > 0:
                    new_centers[j] = X[mask].mean(axis=0)
                else:
                    new_centers[j] = X[np.random.randint(n)]
            if np.allclose(centers, new_centers, atol=1e-6):
                break
            centers = new_centers

        inertia = sum(np.sum((X[labels == j] - centers[j])**2) for j in range(k))
        if inertia < best_inertia:
            best_inertia = inertia
            best_labels = labels.copy()
    return best_labels


def adjusted_rand_index(labels_true, labels_pred):
    """Compute ARI in pure numpy."""
    n = len(labels_true)
    ct = defaultdict(int)
    a_counts = Counter(labels_true)
    b_counts = Counter(labels_pred)
    for i in range(n):
        ct[(labels_true[i], labels_pred[i])] += 1

    def comb2(x):
        return x * (x - 1) / 2.0

    sum_comb_nij = sum(comb2(v) for v in ct.values())
    sum_comb_a = sum(comb2(v) for v in a_counts.values())
    sum_comb_b = sum(comb2(v) for v in b_counts.values())
    comb_n = comb2(n)

    expected = sum_comb_a * sum_comb_b / comb_n if comb_n > 0 else 0
    max_index = 0.5 * (sum_comb_a + sum_comb_b)
    denom = max_index - expected
    if abs(denom) < 1e-15:
        return 0.0 if abs(sum_comb_nij - expected) > 1e-15 else 1.0
    return (sum_comb_nij - expected) / denom


# ── Helpers ──────────────────────────────────────────────────────────

def moments_6(arr):
    """Compute M1-M6: mean, var, skew, kurtosis, 5th, 6th standardized moments."""
    a = np.asarray(arr, dtype=float)
    if len(a) < 4:
        return None
    mu = np.mean(a)
    std = np.std(a, ddof=0)
    if std < 1e-15:
        return None
    z = (a - mu) / std
    return [float(mu), float(np.var(a, ddof=0)), float(np.mean(z**3)),
            float(np.mean(z**4)), float(np.mean(z**5)), float(np.mean(z**6))]


# ── Domain 1: OEIS ──────────────────────────────────────────────────

def load_oeis(n=1000, min_terms=50):
    path = ROOT / "cartography" / "oeis" / "data" / "stripped_new.txt"
    candidates = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split(" ", 1)
            if len(parts) < 2:
                continue
            seq_id = parts[0]
            vals_str = parts[1].strip().strip(",").split(",")
            try:
                vals = [int(v) for v in vals_str if v.strip() != ""]
            except ValueError:
                continue
            if len(vals) >= min_terms:
                candidates.append((seq_id, vals))

    random.shuffle(candidates)
    results = []
    for seq_id, vals in candidates:
        if len(results) >= n:
            break
        arr = np.array(vals, dtype=float)
        mx = np.max(np.abs(arr))
        if mx < 1e-15:
            continue
        normed = arr / mx
        m = moments_6(normed)
        if m is not None:
            results.append({"id": seq_id, "domain": "OEIS", "moments": m, "n_terms": len(vals)})
    print(f"  OEIS: {len(results)} objects")
    return results


# ── Domain 2: Elliptic Curves ────────────────────────────────────────

def load_ec(n=1000):
    import duckdb
    from sympy import primerange

    primes = list(primerange(2, 200))[:25]
    bounds = [2 * math.sqrt(p) for p in primes]

    con = duckdb.connect(str(ROOT / "charon" / "data" / "charon.duckdb"), read_only=True)
    rows = con.sql(f"SELECT lmfdb_label, aplist FROM elliptic_curves ORDER BY random() LIMIT {n*2}").fetchall()
    con.close()

    results = []
    for label, aplist in rows:
        if len(results) >= n:
            break
        if not aplist or len(aplist) < 10:
            continue
        normed = [aplist[i] / bounds[i] for i in range(min(len(aplist), len(bounds)))]
        m = moments_6(normed)
        if m is not None:
            results.append({"id": label, "domain": "EC", "moments": m, "n_ap": len(aplist)})
    print(f"  EC: {len(results)} objects")
    return results


# ── Domain 3: Knots ──────────────────────────────────────────────────

def load_knots(n=1000):
    path = ROOT / "cartography" / "knots" / "data" / "knots.json"
    data = json.loads(path.read_text())
    knots = data["knots"]

    random.shuffle(knots)
    results = []
    for k in knots:
        if len(results) >= n:
            break
        coeffs = k.get("jones_coeffs", [])
        if len(coeffs) < 4:
            continue
        arr = np.array(coeffs, dtype=float)
        mx = np.max(np.abs(arr))
        if mx < 1e-15:
            continue
        normed = arr / mx
        m = moments_6(normed)
        if m is not None:
            results.append({"id": k["name"], "domain": "Knot", "moments": m, "n_coeffs": len(coeffs)})
    print(f"  Knots: {len(results)} objects")
    return results


# ── Domain 4: Maass Forms ────────────────────────────────────────────

def load_maass(min_per_level=10):
    path = ROOT / "cartography" / "lmfdb_dump" / "maass_rigor.json"
    data = json.loads(path.read_text())
    records = data["records"]

    by_level = defaultdict(list)
    for rec in records:
        sp = float(rec["spectral_parameter"])
        by_level[rec["level"]].append(sp)

    results = []
    for level, specs in sorted(by_level.items()):
        if len(specs) < min_per_level:
            continue
        arr = np.array(specs, dtype=float)
        mx = np.max(np.abs(arr))
        if mx < 1e-15:
            continue
        normed = arr / mx
        m = moments_6(normed)
        if m is not None:
            results.append({
                "id": f"Maass_level_{level}",
                "domain": "Maass",
                "moments": m,
                "n_forms": len(specs)
            })
    print(f"  Maass: {len(results)} level-groups")
    return results


# ── Main ─────────────────────────────────────────────────────────────

def main():
    print("M11: Cross-Domain Moment Matching")
    print("=" * 60)

    # 1. Load all domains
    print("\n1. Loading domains...")
    oeis_objs = load_oeis(n=1000, min_terms=50)
    ec_objs = load_ec(n=1000)
    knot_objs = load_knots(n=1000)
    maass_objs = load_maass(min_per_level=10)

    all_objects = oeis_objs + ec_objs + knot_objs + maass_objs
    print(f"\n  Total: {len(all_objects)} objects across {len(set(o['domain'] for o in all_objects))} domains")

    # 2. Domain moment summaries
    print("\n2. Domain moment summaries...")
    by_domain = defaultdict(list)
    for o in all_objects:
        by_domain[o["domain"]].append(o["moments"])

    domain_stats = {}
    for dom, mlist in by_domain.items():
        M = np.array(mlist)
        domain_stats[dom] = {
            "count": len(mlist),
            "moment_means": [round(float(x), 6) for x in M.mean(axis=0)],
            "moment_stds": [round(float(x), 6) for x in M.std(axis=0)],
            "moment_labels": ["M1_mean", "M2_var", "M3_skew", "M4_kurt", "M5", "M6"]
        }
        print(f"  {dom} (n={len(mlist)}): mean_M1={M[:,0].mean():.4f}, "
              f"mean_skew={M[:,2].mean():.4f}, mean_kurt={M[:,3].mean():.4f}")

    # 3. Cross-domain clustering
    print("\n3. Cross-domain clustering...")
    domains = np.array([o["domain"] for o in all_objects])
    X = np.array([o["moments"] for o in all_objects])

    # Standardize
    X_mean = X.mean(axis=0)
    X_std = X.std(axis=0)
    X_std[X_std < 1e-15] = 1.0
    X_scaled = (X - X_mean) / X_std

    unique_domains = sorted(set(domains))
    domain_idx = {d: i for i, d in enumerate(unique_domains)}
    y_domain = np.array([domain_idx[d] for d in domains])

    cluster_results = {}
    for k in [10, 20, 50]:
        print(f"  Running k={k}...", end=" ")
        labels = kmeans_numpy(X_scaled, k, n_init=3, max_iter=50)

        ari = adjusted_rand_index(y_domain.tolist(), labels.tolist())

        # Analyze cluster composition
        mixed_clusters = []
        pure_clusters = []
        twins = []
        for c in range(k):
            mask = labels == c
            cluster_doms = domains[mask]
            counts = dict(Counter(cluster_doms))
            n_doms = len(counts)
            size = int(mask.sum())

            if n_doms > 1:
                mixed_clusters.append({"cluster": c, "size": size, "domains": counts})
                # Distributional twins
                by_dom = defaultdict(list)
                for i in np.where(mask)[0]:
                    by_dom[all_objects[i]["domain"]].append(all_objects[i]["id"])
                twins.append({
                    "cluster": c, "size": size,
                    "domains": {d: ids[:5] for d, ids in by_dom.items()}
                })
            else:
                pure_clusters.append({
                    "cluster": c, "size": size,
                    "domain": list(counts.keys())[0]
                })

        cluster_results[f"k={k}"] = {
            "k": k,
            "ARI": round(float(ari), 4),
            "n_mixed_clusters": len(mixed_clusters),
            "n_pure_clusters": len(pure_clusters),
            "mixed_fraction": round(len(mixed_clusters) / k, 3),
            "mixed_clusters_summary": mixed_clusters[:10],
            "pure_clusters_summary": pure_clusters[:10],
            "distributional_twins": twins[:10]
        }
        print(f"ARI={ari:.4f}, mixed={len(mixed_clusters)}/{k}, pure={len(pure_clusters)}/{k}")

    # 4. Within-OEIS family analysis
    print("\n4. Within-OEIS family analysis...")
    oeis_X = np.array([o["moments"] for o in oeis_objs])
    oeis_mean = oeis_X.mean(axis=0)
    oeis_std = oeis_X.std(axis=0)
    oeis_std[oeis_std < 1e-15] = 1.0
    oeis_scaled = (oeis_X - oeis_mean) / oeis_std

    oeis_labels = kmeans_numpy(oeis_scaled, 10, n_init=3, max_iter=50)

    # Heuristic shape families
    families = []
    for o in oeis_objs:
        m = o["moments"]
        skew = m[2]; kurt = m[3]
        shape = "symmetric" if abs(skew) < 0.3 else ("right_skew" if skew > 0 else "left_skew")
        tail = "heavy_tail" if kurt > 5 else ("light_tail" if kurt < 2 else "normal_tail")
        families.append(f"{shape}_{tail}")

    fam_uniq = sorted(set(families))
    fam_idx = {f: i for i, f in enumerate(fam_uniq)}
    y_fam = [fam_idx[f] for f in families]
    ari_fam = adjusted_rand_index(y_fam, oeis_labels.tolist())

    cluster_family_dist = {}
    for c in range(10):
        mask = oeis_labels == c
        fams = [families[i] for i in range(len(families)) if mask[i]]
        cluster_family_dist[f"cluster_{c}"] = dict(Counter(fams))

    oeis_analysis = {
        "n_sequences": len(oeis_objs),
        "n_moment_clusters": 10,
        "n_shape_families": len(fam_uniq),
        "shape_families": dict(Counter(families)),
        "ARI_moment_vs_shape": round(float(ari_fam), 4),
        "cluster_family_composition": cluster_family_dist,
        "interpretation": (
            "ARI near 1 means moment clusters recover shape families; "
            "ARI near 0 means moment structure is orthogonal to simple shape classification."
        )
    }
    print(f"  Shape families: {len(fam_uniq)}")
    print(f"  ARI (moment clusters vs shape): {ari_fam:.4f}")
    print(f"  Family dist: {dict(Counter(families))}")

    # 5. Interpretation
    print("\n5. Interpretation...")
    ari_10 = cluster_results["k=10"]["ARI"]
    ari_20 = cluster_results["k=20"]["ARI"]
    ari_50 = cluster_results["k=50"]["ARI"]
    mixed_frac_10 = cluster_results["k=10"]["mixed_fraction"]
    mixed_frac_50 = cluster_results["k=50"]["mixed_fraction"]

    if ari_10 > 0.5:
        verdict = "DOMAIN-SPECIFIC: Distributions are largely unique to each domain."
    elif ari_10 > 0.2:
        verdict = "PARTIALLY MIXED: Some cross-domain distributional overlap exists."
    else:
        verdict = "UNIVERSAL: Distributional structure transcends domain boundaries."

    interpretation = {
        "verdict": verdict,
        "ARI_summary": {
            "k=10": ari_10, "k=20": ari_20, "k=50": ari_50,
            "note": "ARI near 0 = universal structure, near 1 = domain-specific"
        },
        "mixed_fraction": {"k=10": mixed_frac_10, "k=50": mixed_frac_50},
        "key_finding": (
            f"At k=10, {cluster_results['k=10']['n_mixed_clusters']}/{10} clusters are mixed. "
            f"ARI={ari_10:.4f}. "
            f"{'Cross-domain distributional twins exist.' if mixed_frac_10 > 0.3 else 'Domains have distinct distributional fingerprints.'}"
        )
    }
    print(f"  {verdict}")
    print(f"  {interpretation['key_finding']}")

    # Save
    output = {
        "challenge": "M11",
        "title": "Cross-Domain Moment Matching",
        "n_objects": len(all_objects),
        "domain_counts": {dom: s["count"] for dom, s in domain_stats.items()},
        "domain_moment_stats": domain_stats,
        "clustering": cluster_results,
        "within_oeis": oeis_analysis,
        "interpretation": interpretation,
    }

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Results saved to {OUT}")


if __name__ == "__main__":
    main()
