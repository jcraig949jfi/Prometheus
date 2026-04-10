#!/usr/bin/env python3
"""
F19: Cross-Domain Fingerprint Transport Rate
=============================================
For each prime p in {3,5,7}, compute the transport matrix T where
T_{A->B} = fraction of B objects that share a mod-p fingerprint with
at least one sampled object from A.

Domains: {OEIS, LMFDB_EC, LMFDB_MF, Knots, Lattices, NumberFields}

Fingerprint = tuple(val % p for val in integer_sequence[:WIDTH])

For each directed pair (A->B):
  1. Sample 500 objects from A, compute fingerprint set F_A
  2. Compute fingerprints for all of B, count how many match any in F_A
  3. T_{A->B} = match_count / |B_sample|

Also compute:
  - Symmetry measure: ||T - T^T|| / ||T||
  - Spectral gap (lambda_1 - lambda_2) of symmetrized T
  - Dominant eigenvector interpretation
  - Random null baseline
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
OUT  = Path(__file__).resolve().parent / "transport_matrix_results.json"

random.seed(42)
np.random.seed(42)

PRIMES = [3, 5, 7]
WIDTH  = 5       # fingerprint width: first 5 terms
SAMPLE = 500     # objects sampled per domain
B_SAMPLE = 1000  # max objects in target domain to test against

DOMAIN_NAMES = ["OEIS", "LMFDB_EC", "LMFDB_MF", "Knots", "Lattices", "NumberFields"]


# ── Data Loaders ─────────────────────────────────────────────────────────

def load_oeis(n=SAMPLE * 3):
    """Load OEIS sequences as lists of integers."""
    path = ROOT / "cartography" / "oeis" / "data" / "stripped_new.txt"
    seqs = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.strip().split(' ', 1)
            if len(parts) < 2:
                continue
            aid = parts[0]
            terms_str = parts[1].strip().strip(',')
            if not terms_str:
                continue
            try:
                terms = [int(x) for x in terms_str.split(',') if x.strip()]
            except ValueError:
                continue
            if len(terms) >= WIDTH:
                seqs[aid] = terms[:20]
            if len(seqs) >= n:
                break
    return seqs


def load_ec(n=SAMPLE * 3):
    """Load elliptic curve a_p lists from DuckDB."""
    import duckdb
    db = ROOT / "charon" / "data" / "charon.duckdb"
    con = duckdb.connect(str(db), read_only=True)
    rows = con.execute(f"""
        SELECT lmfdb_label, aplist
        FROM elliptic_curves
        WHERE aplist IS NOT NULL AND list_count(aplist) >= {WIDTH}
        ORDER BY conductor
        LIMIT {n}
    """).fetchall()
    con.close()
    return {r[0]: list(r[1]) for r in rows}


def load_mf(n=SAMPLE * 3):
    """Load modular form Hecke traces from DuckDB."""
    import duckdb
    db = ROOT / "charon" / "data" / "charon.duckdb"
    con = duckdb.connect(str(db), read_only=True)
    rows = con.execute(f"""
        SELECT lmfdb_label, traces
        FROM modular_forms
        WHERE traces IS NOT NULL AND list_count(traces) >= {WIDTH}
        ORDER BY level, weight
        LIMIT {n}
    """).fetchall()
    con.close()
    result = {}
    for r in rows:
        traces = list(r[1])
        # traces are floats from LMFDB; round to int
        int_traces = []
        for t in traces:
            if t is not None and math.isfinite(t):
                int_traces.append(int(round(t)))
            else:
                int_traces.append(0)
        if len(int_traces) >= WIDTH:
            result[r[0]] = int_traces[:20]
    return result


def load_knots(n=SAMPLE * 3):
    """Load knot polynomial coefficients as integer sequences."""
    path = ROOT / "cartography" / "knots" / "data" / "knots.json"
    with open(path, 'r') as f:
        data = json.load(f)
    result = {}
    for knot in data.get('knots', []):
        name = knot.get('name', '')
        # Use Jones polynomial coefficients as integer sequence
        coeffs = knot.get('jones_coeffs', [])
        if len(coeffs) < WIDTH:
            coeffs = knot.get('alex_coeffs', [])
        if len(coeffs) >= WIDTH:
            result[name] = coeffs[:20]
        if len(result) >= n:
            break
    return result


def load_lattices(n=SAMPLE * 3):
    """Load lattice numerical invariants as integer sequences."""
    path = ROOT / "cartography" / "lattices" / "data" / "lattices_full.json"
    with open(path, 'r') as f:
        data = json.load(f)
    result = {}
    for rec in data.get('records', []):
        label = rec.get('label', '')
        # Build integer sequence from numerical fields
        seq = []
        for field in ['dimension', 'determinant', 'level', 'class_number',
                       'minimal_vector', 'aut_group_order']:
            val = rec.get(field)
            if val is not None:
                try:
                    seq.append(int(val))
                except (ValueError, TypeError):
                    seq.append(0)
            else:
                seq.append(0)
        if len(seq) >= WIDTH:
            result[label] = seq
        if len(result) >= n:
            break
    return result


def load_number_fields(n=SAMPLE * 3):
    """Load number field invariants as integer sequences."""
    path = ROOT / "cartography" / "number_fields" / "data" / "number_fields.json"
    with open(path, 'r') as f:
        data = json.load(f)
    result = {}
    for rec in data:
        label = rec.get('label', '')
        seq = []
        for field in ['degree', 'disc_abs', 'disc_sign', 'class_number']:
            val = rec.get(field)
            if val is not None:
                try:
                    seq.append(abs(int(val)))
                except (ValueError, TypeError):
                    seq.append(0)
            else:
                seq.append(0)
        # Add class group elements
        cg = rec.get('class_group', [])
        if isinstance(cg, list):
            for v in cg:
                try:
                    seq.append(int(v))
                except (ValueError, TypeError):
                    seq.append(0)
        # Pad with regulator digits if short
        reg = rec.get('regulator')
        if reg is not None and len(seq) < WIDTH + 2:
            try:
                r = float(reg)
                # extract significant digits
                if r > 0:
                    seq.append(int(round(r * 1000)) % 10000)
                    seq.append(int(round(r * 1000000)) % 10000)
            except (ValueError, TypeError):
                pass
        if len(seq) >= WIDTH:
            result[label] = seq[:20]
        if len(result) >= n:
            break
    return result


LOADERS = {
    "OEIS": load_oeis,
    "LMFDB_EC": load_ec,
    "LMFDB_MF": load_mf,
    "Knots": load_knots,
    "Lattices": load_lattices,
    "NumberFields": load_number_fields,
}


# ── Fingerprint ──────────────────────────────────────────────────────────

def compute_fingerprint(seq, p, width=WIDTH):
    """mod-p fingerprint: tuple of (val mod p) for first `width` terms."""
    terms = seq[:width]
    if len(terms) < width:
        return None
    return tuple(t % p for t in terms)


# ── Transport Computation ────────────────────────────────────────────────

def compute_transport_rate(source_seqs, target_seqs, p, n_source=SAMPLE, n_target=B_SAMPLE):
    """
    Sample n_source from source, compute fingerprints.
    Sample n_target from target, compute fingerprints.
    Return fraction of target fingerprints that match any source fingerprint.
    """
    # Sample source
    src_keys = list(source_seqs.keys())
    if len(src_keys) > n_source:
        src_keys = random.sample(src_keys, n_source)

    # Compute source fingerprint set
    src_fps = set()
    for k in src_keys:
        fp = compute_fingerprint(source_seqs[k], p)
        if fp is not None:
            src_fps.add(fp)

    if not src_fps:
        return 0.0, 0, 0

    # Sample target
    tgt_keys = list(target_seqs.keys())
    if len(tgt_keys) > n_target:
        tgt_keys = random.sample(tgt_keys, n_target)

    matches = 0
    total = 0
    for k in tgt_keys:
        fp = compute_fingerprint(target_seqs[k], p)
        if fp is not None:
            total += 1
            if fp in src_fps:
                matches += 1

    rate = matches / total if total > 0 else 0.0
    return rate, matches, total


def compute_null_transport(source_seqs, target_seqs, p, n_trials=50,
                           n_source=SAMPLE, n_target=B_SAMPLE):
    """Random null: shuffle target sequences, measure transport."""
    tgt_keys = list(target_seqs.keys())
    tgt_vals = [target_seqs[k] for k in tgt_keys]

    rates = []
    for _ in range(n_trials):
        shuffled = list(tgt_vals)
        random.shuffle(shuffled)
        fake_target = {f"fake_{i}": shuffled[i] for i in range(len(shuffled))}
        rate, _, _ = compute_transport_rate(source_seqs, fake_target, p,
                                             n_source, n_target)
        rates.append(rate)
    return float(np.mean(rates)), float(np.std(rates))


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    print("F19: Cross-Domain Fingerprint Transport Rate")
    print("=" * 55)

    # Load all domains
    print("\nLoading domains...")
    domains = {}
    for name, loader in LOADERS.items():
        try:
            data = loader()
            domains[name] = data
            print(f"  {name}: {len(data)} objects loaded")
        except Exception as e:
            print(f"  {name}: FAILED - {e}")
            domains[name] = {}

    results = {
        "experiment": "F19_transport_matrix",
        "primes": PRIMES,
        "fingerprint_width": WIDTH,
        "sample_size_source": SAMPLE,
        "sample_size_target": B_SAMPLE,
        "domain_sizes": {name: len(data) for name, data in domains.items()},
        "transport_matrices": {},
        "null_baselines": {},
        "spectral_analysis": {},
    }

    active_domains = [d for d in DOMAIN_NAMES if len(domains.get(d, {})) >= 10]
    print(f"\nActive domains: {active_domains}")
    n = len(active_domains)

    for p in PRIMES:
        print(f"\n{'='*55}")
        print(f"Prime p = {p}")
        print(f"{'='*55}")

        T = np.zeros((n, n))
        T_null = np.zeros((n, n))

        for i, src_name in enumerate(active_domains):
            for j, tgt_name in enumerate(active_domains):
                rate, matches, total = compute_transport_rate(
                    domains[src_name], domains[tgt_name], p)
                T[i, j] = rate

                # Compute null baseline for off-diagonal
                if i != j:
                    null_mean, null_std = compute_null_transport(
                        domains[src_name], domains[tgt_name], p, n_trials=20)
                    T_null[i, j] = null_mean
                    excess = (rate - null_mean) / null_std if null_std > 0 else 0
                    print(f"  {src_name:>12s} -> {tgt_name:<12s}: "
                          f"rate={rate:.4f} (null={null_mean:.4f} +/- {null_std:.4f}, "
                          f"z={excess:+.1f}), matches={matches}/{total}")
                else:
                    # Self-transport = self-match rate
                    print(f"  {src_name:>12s} -> {tgt_name:<12s}: "
                          f"rate={rate:.4f} (self), matches={matches}/{total}")

        # ── Symmetry analysis ──
        T_sym = (T + T.T) / 2
        T_asym = T - T_sym
        asym_ratio = np.linalg.norm(T_asym) / np.linalg.norm(T) if np.linalg.norm(T) > 0 else 0

        # ── Spectral analysis of symmetrized matrix ──
        eigenvalues = np.linalg.eigvalsh(T_sym)
        eigenvalues = np.sort(eigenvalues)[::-1]  # descending
        spectral_gap = float(eigenvalues[0] - eigenvalues[1]) if len(eigenvalues) > 1 else 0

        # Dominant eigenvector
        vals, vecs = np.linalg.eigh(T_sym)
        idx = np.argsort(vals)[::-1]
        dominant_vec = vecs[:, idx[0]]
        # Normalize to positive
        if dominant_vec[0] < 0:
            dominant_vec = -dominant_vec

        # Explained variance ratio
        total_var = np.sum(eigenvalues**2)
        explained_ratio = eigenvalues[0]**2 / total_var if total_var > 0 else 0

        print(f"\n  Symmetry: ||T-T^T||/||T|| = {asym_ratio:.4f}")
        print(f"  Eigenvalues: {[f'{e:.4f}' for e in eigenvalues]}")
        print(f"  Spectral gap: {spectral_gap:.4f}")
        print(f"  Explained variance (lambda_1): {explained_ratio:.4f}")
        print(f"  Dominant eigenvector:")
        for di, dname in enumerate(active_domains):
            print(f"    {dname}: {dominant_vec[di]:.4f}")

        # ── Null excess matrix ──
        T_excess = T - T_null
        np.fill_diagonal(T_excess, 0)

        # Store results
        pkey = f"p={p}"
        results["transport_matrices"][pkey] = {
            "matrix": T.tolist(),
            "domains": active_domains,
            "null_matrix": T_null.tolist(),
            "excess_matrix": T_excess.tolist(),
        }
        results["spectral_analysis"][pkey] = {
            "asymmetry_ratio": float(asym_ratio),
            "eigenvalues": [float(e) for e in eigenvalues],
            "spectral_gap": float(spectral_gap),
            "dominant_eigenvector": {
                dname: float(dominant_vec[di])
                for di, dname in enumerate(active_domains)
            },
            "explained_variance_ratio": float(explained_ratio),
        }

    # ── Cross-prime consistency ──
    print(f"\n{'='*55}")
    print("Cross-prime consistency")
    print(f"{'='*55}")
    matrices = []
    for p in PRIMES:
        pkey = f"p={p}"
        if pkey in results["transport_matrices"]:
            matrices.append(np.array(results["transport_matrices"][pkey]["matrix"]))

    if len(matrices) >= 2:
        # Correlation between transport matrices at different primes
        correlations = {}
        for i in range(len(PRIMES)):
            for j in range(i+1, len(PRIMES)):
                flat_i = matrices[i].flatten()
                flat_j = matrices[j].flatten()
                corr = float(np.corrcoef(flat_i, flat_j)[0, 1])
                key = f"p={PRIMES[i]}_vs_p={PRIMES[j]}"
                correlations[key] = corr
                print(f"  corr(T@p={PRIMES[i]}, T@p={PRIMES[j]}) = {corr:.4f}")

        results["cross_prime_consistency"] = correlations

        # Average transport matrix
        T_avg = np.mean(matrices, axis=0)
        vals_avg = np.linalg.eigvalsh((T_avg + T_avg.T) / 2)
        vals_avg = np.sort(vals_avg)[::-1]
        print(f"\n  Average matrix eigenvalues: {[f'{e:.4f}' for e in vals_avg]}")
        print(f"  Average spectral gap: {vals_avg[0] - vals_avg[1]:.4f}")

        results["average_matrix"] = {
            "matrix": T_avg.tolist(),
            "eigenvalues": [float(e) for e in vals_avg],
            "spectral_gap": float(vals_avg[0] - vals_avg[1]),
        }

    # ── Summary ──
    print(f"\n{'='*55}")
    print("SUMMARY")
    print(f"{'='*55}")
    for p in PRIMES:
        pkey = f"p={p}"
        sa = results["spectral_analysis"].get(pkey, {})
        print(f"\n  p={p}:")
        print(f"    Asymmetry ratio: {sa.get('asymmetry_ratio', 0):.4f}")
        print(f"    Spectral gap:    {sa.get('spectral_gap', 0):.4f}")
        print(f"    Explained var:   {sa.get('explained_variance_ratio', 0):.4f}")
        ev = sa.get('dominant_eigenvector', {})
        if ev:
            top = sorted(ev.items(), key=lambda x: abs(x[1]), reverse=True)
            print(f"    Dominant domain: {top[0][0]} ({top[0][1]:.4f})")

    # Save
    with open(OUT, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT}")


if __name__ == "__main__":
    main()
