#!/usr/bin/env python3
"""
F28: Spectral Gap Universality Across Domains
==============================================
Build k-NN similarity graph (k=10) on mod-5 fingerprints per domain,
compute spectral gap (lambda_2 - lambda_1 of normalized Laplacian).
Sample 500 objects per domain.

Domains: OEIS, LMFDB EC, LMFDB MF, genus-2, knots, lattices, number fields.
Physics comparison: PDG particles on mass (k=5).

Question: Is the spectral gap a universal constant, or does each domain
have its own geometric character?
"""

import sys
import json
import math
import random
import numpy as np
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(line_buffering=True)

ROOT = Path(__file__).resolve().parents[2]  # F:/Prometheus
OUT  = Path(__file__).resolve().parent / "spectral_gap_universality_results.json"

random.seed(42)
np.random.seed(42)

N_SAMPLE = 500
K_NN = 10
K_NN_PDG = 5
MOD_P = 5
FP_WIDTH = 8  # number of terms used in mod-5 fingerprint


# ── Mod-5 fingerprint ─────────────────────────────────────────────────

def mod5_fingerprint(seq, width=FP_WIDTH):
    """Compute mod-5 fingerprint: tuple of (val mod 5) for first `width` integer terms."""
    terms = seq[:width]
    if len(terms) < width:
        return None
    try:
        return tuple(int(t) % MOD_P for t in terms)
    except (ValueError, TypeError):
        return None


def fingerprint_distance(fp1, fp2):
    """Hamming-style distance between two mod-5 fingerprints, normalized."""
    return sum(1 for a, b in zip(fp1, fp2) if a != b) / len(fp1)


# ── k-NN graph and spectral gap ───────────────────────────────────────

def build_knn_graph_from_fingerprints(fingerprints, k):
    """Build k-NN graph from fingerprints using pairwise Hamming distance.
    Returns adjacency matrix (symmetric, binary)."""
    n = len(fingerprints)
    # Compute pairwise distance matrix
    fps = np.array(fingerprints, dtype=np.int32)  # (n, width)
    # Hamming distance: count mismatches
    # Vectorized: for each pair
    dist = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        diff = (fps != fps[i]).sum(axis=1).astype(np.float64)
        dist[i] = diff / fps.shape[1]

    # Build symmetric k-NN adjacency
    adj = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        # Exclude self
        d = dist[i].copy()
        d[i] = np.inf
        nn_idx = np.argsort(d)[:k]
        for j in nn_idx:
            adj[i, j] = 1.0
            adj[j, i] = 1.0  # symmetric

    return adj, dist


def spectral_gap(adj):
    """Compute spectral gap of normalized Laplacian: lambda_2 - lambda_1.
    lambda_1 = 0 always for connected graph.
    Returns (gap, lambda_2, eigenvalues[:5])."""
    n = adj.shape[0]
    degree = adj.sum(axis=1)
    # Handle isolated nodes
    degree[degree == 0] = 1.0

    # Normalized Laplacian: L_norm = I - D^{-1/2} A D^{-1/2}
    d_inv_sqrt = 1.0 / np.sqrt(degree)
    D_inv_sqrt = np.diag(d_inv_sqrt)
    L_norm = np.eye(n) - D_inv_sqrt @ adj @ D_inv_sqrt

    # Eigenvalues (symmetric matrix)
    eigenvalues = np.linalg.eigvalsh(L_norm)
    eigenvalues = np.sort(eigenvalues)

    # lambda_1 should be ~0
    lam1 = eigenvalues[0]
    lam2 = eigenvalues[1] if n > 1 else 0.0
    gap = lam2 - lam1

    return {
        "spectral_gap": round(float(gap), 8),
        "lambda_1": round(float(lam1), 8),
        "lambda_2": round(float(lam2), 8),
        "lambda_3": round(float(eigenvalues[2]), 8) if n > 2 else None,
        "eigenvalues_first_5": [round(float(e), 8) for e in eigenvalues[:5]],
        "n_nodes": n,
    }


# ── Domain loaders ─────────────────────────────────────────────────────

def load_oeis(n=N_SAMPLE):
    """OEIS sequences: mod-5 fingerprint of first terms."""
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
            if len(vals) >= FP_WIDTH:
                fp = mod5_fingerprint(vals)
                if fp is not None:
                    candidates.append((seq_id, fp))
    random.shuffle(candidates)
    result = candidates[:n]
    print(f"  OEIS: {len(result)} objects")
    return [r[1] for r in result], [r[0] for r in result]


def load_ec(n=N_SAMPLE):
    """Elliptic curves: mod-5 fingerprint of a_p trace sequence."""
    import duckdb
    con = duckdb.connect(str(ROOT / "charon" / "data" / "charon.duckdb"), read_only=True)
    rows = con.execute(f"""
        SELECT lmfdb_label, aplist FROM elliptic_curves
        WHERE aplist IS NOT NULL AND list_count(aplist) >= {FP_WIDTH}
        ORDER BY random() LIMIT {n * 3}
    """).fetchall()
    con.close()

    results = []
    labels = []
    for label, aplist in rows:
        if len(results) >= n:
            break
        fp = mod5_fingerprint(aplist)
        if fp is not None:
            results.append(fp)
            labels.append(label)
    print(f"  EC: {len(results)} objects")
    return results, labels


def load_mf(n=N_SAMPLE):
    """Modular forms: mod-5 fingerprint of Hecke traces."""
    import duckdb
    con = duckdb.connect(str(ROOT / "charon" / "data" / "charon.duckdb"), read_only=True)
    rows = con.execute(f"""
        SELECT lmfdb_label, traces FROM modular_forms
        WHERE traces IS NOT NULL AND list_count(traces) >= {FP_WIDTH}
        ORDER BY random() LIMIT {n * 3}
    """).fetchall()
    con.close()

    results = []
    labels = []
    for label, traces in rows:
        if len(results) >= n:
            break
        # traces are floats; round to int for mod-5
        int_traces = [int(round(t)) for t in traces[:FP_WIDTH]]
        fp = mod5_fingerprint(int_traces)
        if fp is not None:
            results.append(fp)
            labels.append(label)
    print(f"  MF: {len(results)} objects")
    return results, labels


def load_genus2(n=N_SAMPLE):
    """Genus-2 curves: mod-5 fingerprint from [conductor, discriminant, torsion elements, ...]."""
    path = ROOT / "cartography" / "genus2" / "data" / "genus2_curves_full.json"
    with open(path) as f:
        data = json.load(f)

    random.shuffle(data)
    results = []
    labels = []
    for rec in data:
        if len(results) >= n:
            break
        # Build integer sequence from numeric fields
        cond = int(rec.get("conductor", 0))
        disc = int(rec.get("discriminant", 0))
        ds = int(rec.get("disc_sign", 0))
        tsr = int(rec.get("two_selmer_rank", 0))
        rn = int(rec.get("root_number", 0))
        tor = rec.get("torsion", [])
        tor_vals = [int(t) for t in tor[:3]] if tor else [0, 0, 0]
        while len(tor_vals) < 3:
            tor_vals.append(0)
        seq = [cond, disc, ds, tsr, rn] + tor_vals
        if len(seq) >= FP_WIDTH:
            fp = mod5_fingerprint(seq[:FP_WIDTH])
            if fp is not None:
                results.append(fp)
                labels.append(rec.get("label", f"g2_{len(results)}"))
    print(f"  Genus-2: {len(results)} objects")
    return results, labels


def load_knots(n=N_SAMPLE):
    """Knots: mod-5 fingerprint of Jones polynomial coefficients."""
    path = ROOT / "cartography" / "knots" / "data" / "knots.json"
    data = json.loads(path.read_text())
    knots = data["knots"]
    random.shuffle(knots)

    results = []
    labels = []
    for k in knots:
        if len(results) >= n:
            break
        coeffs = k.get("jones_coeffs", [])
        if len(coeffs) >= FP_WIDTH:
            fp = mod5_fingerprint(coeffs)
            if fp is not None:
                results.append(fp)
                labels.append(k["name"])
    print(f"  Knots: {len(results)} objects")
    return results, labels


def load_lattices(n=N_SAMPLE):
    """Lattices: mod-5 fingerprint of theta series."""
    path = ROOT / "cartography" / "lmfdb_dump" / "lat_lattices.json"
    with open(path) as f:
        data = json.load(f)
    records = data.get("records", [])
    random.shuffle(records)

    results = []
    labels = []
    for rec in records:
        if len(results) >= n:
            break
        theta = rec.get("theta_series", [])
        if len(theta) >= FP_WIDTH:
            fp = mod5_fingerprint(theta)
            if fp is not None:
                results.append(fp)
                labels.append(rec.get("label", rec.get("id", f"lat_{len(results)}")))
    print(f"  Lattices: {len(results)} objects")
    return results, labels


def load_number_fields(n=N_SAMPLE):
    """Number fields: mod-5 fingerprint from [disc_abs, degree, class_number, ...]."""
    path = ROOT / "cartography" / "number_fields" / "data" / "number_fields.json"
    with open(path) as f:
        data = json.load(f)
    random.shuffle(data)

    results = []
    labels = []
    for nf in data:
        if len(results) >= n:
            break
        disc = int(nf.get("disc_abs", 0))
        deg = int(nf.get("degree", 0))
        ds = int(nf.get("disc_sign", 0))
        cn = int(nf.get("class_number", 0))
        cg = nf.get("class_group", [])
        cg_vals = [int(x) for x in cg[:4]] if cg else []
        while len(cg_vals) < 4:
            cg_vals.append(0)
        seq = [disc, deg, ds, cn] + cg_vals
        if len(seq) >= FP_WIDTH:
            fp = mod5_fingerprint(seq[:FP_WIDTH])
            if fp is not None:
                results.append(fp)
                labels.append(nf.get("label", f"nf_{len(results)}"))
    print(f"  NF: {len(results)} objects")
    return results, labels


def load_pdg():
    """PDG particles: k-NN on log(mass), not fingerprints. Separate analysis."""
    path = ROOT / "cartography" / "physics" / "data" / "pdg" / "particles.json"
    with open(path) as f:
        data = json.load(f)

    results = []
    labels = []
    for p in data:
        mass = p.get("mass_GeV", 0)
        if mass is not None and mass > 0:
            results.append(mass)
            labels.append(p.get("name", f"pdg_{len(results)}"))
    print(f"  PDG: {len(results)} particles with mass > 0")
    return results, labels


def find_largest_component(adj):
    """Find largest connected component via BFS."""
    n = adj.shape[0]
    visited = np.zeros(n, dtype=bool)
    best_comp = []
    for start in range(n):
        if visited[start]:
            continue
        comp = []
        queue = [start]
        visited[start] = True
        while queue:
            node = queue.pop(0)
            comp.append(node)
            for nb in range(n):
                if adj[node, nb] > 0 and not visited[nb]:
                    visited[nb] = True
                    queue.append(nb)
        if len(comp) > len(best_comp):
            best_comp = comp
    return best_comp


def pdg_spectral_gap(masses, k=K_NN_PDG):
    """Build k-NN graph on log(mass) for PDG particles.
    Uses binary adjacency. Extracts largest connected component."""
    log_mass = np.log10(np.array(masses, dtype=np.float64))
    n = len(log_mass)

    # Pairwise distance on 1D
    dist = np.abs(log_mass[:, None] - log_mass[None, :])

    adj = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        d = dist[i].copy()
        d[i] = np.inf
        nn_idx = np.argsort(d)[:k]
        for j in nn_idx:
            adj[i, j] = 1.0
            adj[j, i] = 1.0

    # Extract largest connected component
    lcc = find_largest_component(adj)
    n_components_approx = n - len(lcc)  # rough estimate
    adj_lcc = adj[np.ix_(lcc, lcc)]
    print(f"    (largest component: {len(lcc)}/{n} nodes)")

    result = spectral_gap(adj_lcc)
    result["n_components_other"] = n_components_approx
    return result


# ── Null model: random fingerprints ───────────────────────────────────

def random_fingerprint_spectral_gap(n=N_SAMPLE, k=K_NN, n_trials=5):
    """Null: random mod-5 fingerprints, compute spectral gap."""
    gaps = []
    for trial in range(n_trials):
        fps = [tuple(random.randint(0, MOD_P - 1) for _ in range(FP_WIDTH))
               for _ in range(n)]
        fps_arr = np.array(fps, dtype=np.int32)
        adj, _ = build_knn_graph_from_fingerprints(fps, k)
        sg = spectral_gap(adj)
        gaps.append(sg["spectral_gap"])
        print(f"    Null trial {trial + 1}: gap = {sg['spectral_gap']:.6f}")
    return {
        "mean_gap": round(float(np.mean(gaps)), 8),
        "std_gap": round(float(np.std(gaps)), 8),
        "gaps": [round(float(g), 8) for g in gaps],
    }


# ── Main ───────────────────────────────────────────────────────────────

def main():
    print("F28: Spectral Gap Universality Across Domains")
    print("=" * 60)

    # 1. Load all domains
    print("\n1. Loading domains...")
    loaders = {
        "OEIS": load_oeis,
        "EC": load_ec,
        "MF": load_mf,
        "Genus2": load_genus2,
        "Knots": load_knots,
        "Lattices": load_lattices,
        "NF": load_number_fields,
    }

    domain_fps = {}
    domain_labels = {}
    for name, loader in loaders.items():
        fps, lbls = loader(N_SAMPLE)
        domain_fps[name] = fps
        domain_labels[name] = lbls

    # 2. Compute spectral gap for each domain
    print("\n2. Computing spectral gaps...")
    results = {}
    for name, fps in domain_fps.items():
        n_actual = len(fps)
        if n_actual < 20:
            print(f"  {name}: SKIP (only {n_actual} objects)")
            continue
        k_use = min(K_NN, n_actual - 1)
        print(f"  {name} (n={n_actual}, k={k_use})...", end="", flush=True)
        adj, dist = build_knn_graph_from_fingerprints(fps, k_use)
        sg = spectral_gap(adj)
        sg["k"] = k_use
        sg["domain"] = name

        # Fingerprint entropy: how many unique fingerprints?
        unique_fps = len(set(fps))
        sg["unique_fingerprints"] = unique_fps
        sg["fingerprint_diversity"] = round(unique_fps / n_actual, 6)

        # Mean distance stats
        dists_flat = dist[np.triu_indices(n_actual, k=1)]
        sg["mean_pairwise_distance"] = round(float(np.mean(dists_flat)), 6)
        sg["std_pairwise_distance"] = round(float(np.std(dists_flat)), 6)

        results[name] = sg
        print(f" gap = {sg['spectral_gap']:.6f}, lambda_2 = {sg['lambda_2']:.6f}")

    # 3. PDG particles (mass-based, not fingerprint)
    print("\n3. PDG particles (mass-based k-NN)...")
    pdg_masses, pdg_labels = load_pdg()
    if len(pdg_masses) >= 10:
        k_pdg = min(K_NN_PDG, len(pdg_masses) - 1)
        pdg_result = pdg_spectral_gap(pdg_masses, k=k_pdg)
        pdg_result["k"] = k_pdg
        pdg_result["domain"] = "PDG"
        pdg_result["n_particles"] = len(pdg_masses)
        pdg_result["note"] = "k-NN on log10(mass_GeV), not mod-5 fingerprints"
        results["PDG"] = pdg_result
        print(f"  PDG: gap = {pdg_result['spectral_gap']:.6f}")

    # 4. Null model
    print("\n4. Null model (random mod-5 fingerprints)...")
    null_result = random_fingerprint_spectral_gap(n=N_SAMPLE, k=K_NN, n_trials=5)
    print(f"  Null: mean gap = {null_result['mean_gap']:.6f} +/- {null_result['std_gap']:.6f}")

    # 5. Analysis
    print("\n5. Analysis")
    print("-" * 60)

    math_domains = [name for name in results if name != "PDG"]
    gaps = [results[name]["spectral_gap"] for name in math_domains]

    if gaps:
        mean_gap = np.mean(gaps)
        std_gap = np.std(gaps)
        cv = std_gap / mean_gap if mean_gap > 0 else float("inf")

        print(f"\n  Mathematical domains ({len(math_domains)}):")
        for name in sorted(math_domains, key=lambda x: results[x]["spectral_gap"]):
            r = results[name]
            print(f"    {name:12s}: gap = {r['spectral_gap']:.6f}  "
                  f"(n={r['n_nodes']}, unique_fp={r.get('unique_fingerprints', '?')}, "
                  f"diversity={r.get('fingerprint_diversity', '?')})")

        print(f"\n  Mean spectral gap:  {mean_gap:.6f}")
        print(f"  Std spectral gap:   {std_gap:.6f}")
        print(f"  CV (std/mean):      {cv:.4f}")
        print(f"  Null model mean:    {null_result['mean_gap']:.6f} +/- {null_result['std_gap']:.6f}")

        if "PDG" in results:
            pdg_gap = results["PDG"]["spectral_gap"]
            print(f"  PDG gap:            {pdg_gap:.6f}")

        # Verdict
        print("\n  VERDICT:")
        if cv < 0.15:
            verdict = "UNIVERSAL: spectral gap is approximately constant across mathematical domains"
            print(f"    {verdict}")
            print(f"    CV = {cv:.4f} < 0.15 -- low variation")
        elif cv < 0.30:
            verdict = "WEAKLY UNIVERSAL: spectral gaps cluster but show moderate variation"
            print(f"    {verdict}")
            print(f"    CV = {cv:.4f} -- moderate variation")
        else:
            verdict = "DOMAIN-SPECIFIC: each mathematical domain has its own geometric character"
            print(f"    {verdict}")
            print(f"    CV = {cv:.4f} > 0.30 -- high variation")

        # Compare to null
        null_gap = null_result["mean_gap"]
        deviation_from_null = [(name, (results[name]["spectral_gap"] - null_gap) / null_result["std_gap"]
                                if null_result["std_gap"] > 0 else 0)
                               for name in math_domains]
        print(f"\n  Deviation from null (in sigma):")
        for name, dev in sorted(deviation_from_null, key=lambda x: x[1]):
            print(f"    {name:12s}: {dev:+.2f} sigma")

    # 6. Save results
    output = {
        "experiment": "F28_spectral_gap_universality",
        "parameters": {
            "n_sample": N_SAMPLE,
            "k_nn": K_NN,
            "k_nn_pdg": K_NN_PDG,
            "mod_p": MOD_P,
            "fp_width": FP_WIDTH,
        },
        "domain_results": results,
        "null_model": null_result,
        "summary": {
            "math_domains": math_domains,
            "gaps": {name: results[name]["spectral_gap"] for name in math_domains},
            "mean_gap": round(float(mean_gap), 8) if gaps else None,
            "std_gap": round(float(std_gap), 8) if gaps else None,
            "cv": round(float(cv), 6) if gaps else None,
            "null_mean_gap": null_result["mean_gap"],
            "null_std_gap": null_result["std_gap"],
            "verdict": verdict if gaps else "INSUFFICIENT DATA",
        },
    }

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT}")


if __name__ == "__main__":
    main()
