"""
F21: Graph Spectral Rigidity Constant
Build k-NN graphs (k=10) on mod-5 fingerprints for 500 objects from 4 domains
(OEIS, LMFDB EC, Knots, Lattices/MF). Perturb 5% of edges, measure spectral
rigidity R = 1 - (L2 perturbation impact / max possible impact).
"""

import sys
import json
import math
import random
import numpy as np

sys.stdout.reconfigure(line_buffering=True)

from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[2]  # F:/Prometheus
OUT  = Path(__file__).resolve().parent / "spectral_rigidity_results.json"

random.seed(42)
np.random.seed(42)

N_OBJECTS  = 500
K_NN       = 10
REWIRE_PCT = 0.05
N_TRIALS   = 20   # repeated perturbation trials for stability


# ── Mod-5 fingerprint ──────────────────────────────────────────────────
def mod5_fingerprint(values, n_bins=5):
    """
    Given a list of integers/floats, compute a mod-5 histogram fingerprint.
    For each value, take abs(round(v)) mod 5, build a normalized 5-bin histogram.
    """
    bins = np.zeros(n_bins, dtype=float)
    for v in values:
        iv = abs(int(round(v)))
        bins[iv % n_bins] += 1
    total = bins.sum()
    if total > 0:
        bins /= total
    return bins


# ── k-NN graph construction ────────────────────────────────────────────
def build_knn_adjacency(fingerprints, k=10):
    """Build a symmetric k-NN adjacency matrix from fingerprint vectors."""
    n = len(fingerprints)
    X = np.array(fingerprints)
    # Pairwise L2 distances
    # Use broadcasting: ||x-y||^2 = ||x||^2 + ||y||^2 - 2*x.y
    sq_norms = np.sum(X ** 2, axis=1)
    dists = sq_norms[:, None] + sq_norms[None, :] - 2 * X @ X.T
    dists = np.maximum(dists, 0)  # numerical safety
    np.fill_diagonal(dists, np.inf)  # exclude self

    # k-NN: for each node, connect to k nearest
    adj = np.zeros((n, n), dtype=float)
    for i in range(n):
        neighbors = np.argsort(dists[i])[:k]
        for j in neighbors:
            adj[i, j] = 1.0
            adj[j, i] = 1.0  # symmetrize

    return adj


def laplacian_spectrum(adj):
    """Compute normalized Laplacian eigenvalues."""
    degrees = adj.sum(axis=1)
    D = np.diag(degrees)
    L = D - adj
    # Normalized Laplacian: D^{-1/2} L D^{-1/2}
    d_inv_sqrt = np.zeros_like(degrees)
    mask = degrees > 0
    d_inv_sqrt[mask] = 1.0 / np.sqrt(degrees[mask])
    D_inv_sqrt = np.diag(d_inv_sqrt)
    L_norm = D_inv_sqrt @ L @ D_inv_sqrt
    eigvals = np.linalg.eigvalsh(L_norm)
    return np.sort(eigvals)


def rewire_edges(adj, pct=0.05):
    """Randomly rewire a fraction of edges. Returns a new adjacency matrix."""
    n = adj.shape[0]
    new_adj = adj.copy()

    # Get list of existing edges (upper triangle)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i, j] > 0:
                edges.append((i, j))

    n_rewire = max(1, int(len(edges) * pct))
    rewire_idx = random.sample(range(len(edges)), min(n_rewire, len(edges)))

    for idx in rewire_idx:
        i, j = edges[idx]
        # Remove this edge
        new_adj[i, j] = 0
        new_adj[j, i] = 0
        # Add a random new edge
        attempts = 0
        while attempts < 50:
            a = random.randint(0, n - 1)
            b = random.randint(0, n - 1)
            if a != b and new_adj[a, b] == 0:
                new_adj[a, b] = 1.0
                new_adj[b, a] = 1.0
                break
            attempts += 1

    return new_adj


def spectral_rigidity(adj, n_trials=N_TRIALS, rewire_pct=REWIRE_PCT):
    """
    Compute spectral rigidity R = 1 - (mean perturbation impact / max possible impact).
    Max possible impact = L2 norm of original spectrum (comparing to zero spectrum).
    """
    orig_spec = laplacian_spectrum(adj)
    orig_norm = np.linalg.norm(orig_spec)
    if orig_norm < 1e-12:
        return 0.0, 0.0, orig_spec

    impacts = []
    for _ in range(n_trials):
        perturbed_adj = rewire_edges(adj, pct=rewire_pct)
        pert_spec = laplacian_spectrum(perturbed_adj)
        # L2 distance between spectra
        l2_dist = np.linalg.norm(orig_spec - pert_spec)
        impacts.append(l2_dist)

    mean_impact = np.mean(impacts)
    std_impact = np.std(impacts)
    R = 1.0 - (mean_impact / orig_norm)
    R = max(0.0, min(1.0, R))  # clamp
    return R, std_impact / orig_norm, orig_spec


# ── Domain 1: OEIS ────────────────────────────────────────────────────
def load_oeis(n=N_OBJECTS, min_terms=20):
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
        fp = mod5_fingerprint(vals)
        if fp.sum() > 0:
            results.append({"id": seq_id, "fingerprint": fp})
    print(f"  OEIS: {len(results)} objects loaded")
    return results


# ── Domain 2: Elliptic Curves (DuckDB) ────────────────────────────────
def load_ec(n=N_OBJECTS):
    import duckdb
    con = duckdb.connect(str(ROOT / "charon" / "data" / "charon.duckdb"), read_only=True)
    rows = con.sql(
        f"SELECT lmfdb_label, aplist FROM elliptic_curves "
        f"WHERE aplist IS NOT NULL AND len(aplist) >= 10 "
        f"ORDER BY random() LIMIT {n * 2}"
    ).fetchall()
    con.close()

    results = []
    for label, aplist in rows:
        if len(results) >= n:
            break
        fp = mod5_fingerprint(aplist)
        if fp.sum() > 0:
            results.append({"id": label, "fingerprint": fp})
    print(f"  EC: {len(results)} objects loaded")
    return results


# ── Domain 3: Knots ───────────────────────────────────────────────────
def load_knots(n=N_OBJECTS):
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
        fp = mod5_fingerprint(coeffs)
        if fp.sum() > 0:
            results.append({"id": k["name"], "fingerprint": fp})
    print(f"  Knots: {len(results)} objects loaded")
    return results


# ── Domain 4: Modular Forms (DuckDB) ─────────────────────────────────
def load_mf(n=N_OBJECTS):
    import duckdb
    con = duckdb.connect(str(ROOT / "charon" / "data" / "charon.duckdb"), read_only=True)
    rows = con.sql(
        f"SELECT lmfdb_label, traces FROM modular_forms "
        f"WHERE traces IS NOT NULL AND len(traces) >= 10 "
        f"ORDER BY random() LIMIT {n * 2}"
    ).fetchall()
    con.close()

    results = []
    for label, traces in rows:
        if len(results) >= n:
            break
        fp = mod5_fingerprint(traces)
        if fp.sum() > 0:
            results.append({"id": label, "fingerprint": fp})
    print(f"  MF: {len(results)} objects loaded")
    return results


# ── Lattices (LMFDB dump) ─────────────────────────────────────────────
def load_lattices(n=N_OBJECTS):
    path = ROOT / "cartography" / "lattices" / "data" / "lattices_full.json"
    data = json.loads(path.read_text())
    records = data["records"]
    random.shuffle(records)

    results = []
    for rec in records:
        if len(results) >= n:
            break
        # Build fingerprint from numeric fields: dim, det, level, class_number, etc.
        vals = []
        for field in ["dimension", "determinant", "level", "class_number",
                       "minimal_vector", "aut_group_order"]:
            v = rec.get(field)
            if v is not None:
                try:
                    vals.append(int(v))
                except (ValueError, TypeError):
                    pass
        if len(vals) >= 3:
            fp = mod5_fingerprint(vals)
            if fp.sum() > 0:
                results.append({"id": rec.get("label", "?"), "fingerprint": fp})
    print(f"  Lattices: {len(results)} objects loaded")
    return results


# ── Main ───────────────────────────────────────────────────────────────
def main():
    print("=== F21: Graph Spectral Rigidity Constant ===\n")
    print("Loading domains...")

    domains = {}
    domains["OEIS"]     = load_oeis()
    domains["EC"]       = load_ec()
    domains["Knots"]    = load_knots()
    domains["MF"]       = load_mf()

    # If lattices don't reach 500, fall back but still include
    latt = load_lattices()
    if len(latt) >= 100:
        domains["Lattices"] = latt
    else:
        print(f"  Lattices only has {len(latt)} objects, skipping domain")

    print(f"\nDomains loaded: {list(domains.keys())}")
    print(f"Objects per domain: {', '.join(f'{k}={len(v)}' for k,v in domains.items())}")

    results = {}

    for domain_name, objects in domains.items():
        n_obj = len(objects)
        print(f"\n--- {domain_name} (n={n_obj}) ---")
        fingerprints = [obj["fingerprint"] for obj in objects]

        # Check fingerprint diversity
        fp_arr = np.array(fingerprints)
        unique_fps = len(set(tuple(fp.round(6)) for fp in fp_arr))
        print(f"  Unique fingerprints: {unique_fps}/{n_obj}")

        print(f"  Building k-NN graph (k={K_NN})...")
        adj = build_knn_adjacency(fingerprints, k=K_NN)
        n_edges = int(adj.sum()) // 2
        print(f"  Edges: {n_edges}")

        print(f"  Computing spectral rigidity ({N_TRIALS} trials, {REWIRE_PCT*100:.0f}% rewire)...")
        R, R_std, spectrum = spectral_rigidity(adj, n_trials=N_TRIALS, rewire_pct=REWIRE_PCT)
        print(f"  R = {R:.6f} +/- {R_std:.6f}")

        # Also compute some spectrum diagnostics
        spectral_gap = float(spectrum[1]) if len(spectrum) > 1 else 0.0
        max_eigenval = float(spectrum[-1]) if len(spectrum) > 0 else 0.0

        results[domain_name] = {
            "n_objects": n_obj,
            "unique_fingerprints": unique_fps,
            "n_edges": n_edges,
            "spectral_rigidity_R": round(R, 6),
            "spectral_rigidity_std": round(R_std, 6),
            "spectral_gap": round(spectral_gap, 6),
            "max_eigenvalue": round(max_eigenval, 6),
            "spectrum_L2_norm": round(float(np.linalg.norm(spectrum)), 6),
        }

    # Summary
    print("\n" + "=" * 60)
    print("SPECTRAL RIGIDITY COMPARISON")
    print("=" * 60)
    sorted_domains = sorted(results.items(), key=lambda x: x[1]["spectral_rigidity_R"], reverse=True)
    for i, (name, r) in enumerate(sorted_domains, 1):
        print(f"  {i}. {name:10s}  R = {r['spectral_rigidity_R']:.6f} +/- {r['spectral_rigidity_std']:.6f}  "
              f"(gap={r['spectral_gap']:.4f}, edges={r['n_edges']})")

    most_rigid = sorted_domains[0][0]
    least_rigid = sorted_domains[-1][0]
    print(f"\n  Most rigid:  {most_rigid} (structure most survives noise)")
    print(f"  Least rigid: {least_rigid} (structure most fragile to noise)")

    # Null baseline: random fingerprints
    print("\n--- Null baseline (random fingerprints, n=500) ---")
    null_fps = [np.random.dirichlet(np.ones(5)) for _ in range(500)]
    null_adj = build_knn_adjacency(null_fps, k=K_NN)
    null_R, null_std, _ = spectral_rigidity(null_adj, n_trials=N_TRIALS, rewire_pct=REWIRE_PCT)
    print(f"  R_null = {null_R:.6f} +/- {null_std:.6f}")
    results["NULL_RANDOM"] = {
        "n_objects": 500,
        "spectral_rigidity_R": round(null_R, 6),
        "spectral_rigidity_std": round(null_std, 6),
        "note": "Null baseline: random Dirichlet fingerprints"
    }

    output = {
        "problem": "F21",
        "title": "Graph Spectral Rigidity Constant",
        "method": (
            f"k-NN graph (k={K_NN}) on mod-5 fingerprints, "
            f"{REWIRE_PCT*100:.0f}% edge rewiring, "
            f"R = 1 - (mean L2 spectral shift / spectrum L2 norm), "
            f"{N_TRIALS} perturbation trials per domain"
        ),
        "domains": results,
        "ranking": [name for name, _ in sorted_domains],
        "most_rigid_domain": most_rigid,
        "least_rigid_domain": least_rigid,
    }

    OUT.write_text(json.dumps(output, indent=2))
    print(f"\nResults saved to {OUT}")


if __name__ == "__main__":
    main()
