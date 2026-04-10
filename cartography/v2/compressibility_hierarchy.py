#!/usr/bin/env python3
"""
F29: Arithmetic Object Compressibility Hierarchy
=================================================
For each mathematical domain, measure "compressibility" of objects:
what fraction of their information can be captured by a low-order
linear recurrence?

Method:
  - Sample 500 objects per domain
  - Extract primary integer sequence per object
  - Run Berlekamp-Massey (BM) algorithm over GF(p) to find minimal
    linear recurrence relation
  - Compressibility C = 1 - (BM_order / sequence_length)
  - Rank domains by mean compressibility
  - Correlate with spectral gap from F28

Domains:
  OEIS:     first terms of the sequence
  EC:       a_p trace sequence
  MF:       Hecke eigenvalue traces
  Knots:    Jones polynomial coefficients
  Lattices: theta series first terms
  NF:       discriminant-derived sequence

BM is computed mod p=101 (a prime large enough to avoid accidental
degeneracies but small enough for fast arithmetic).
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
OUT  = Path(__file__).resolve().parent / "compressibility_hierarchy_results.json"

random.seed(42)
np.random.seed(42)

N_SAMPLE = 500
BM_MOD_P = 101    # prime modulus for Berlekamp-Massey
SEQ_LEN_MAX = 30  # max terms to use per object
SEQ_LEN_MIN = 8   # minimum terms required (BM needs at least this)


# ── Berlekamp-Massey over GF(p) ──────────────────────────────────────

def berlekamp_massey_gfp(seq, p):
    """
    Berlekamp-Massey algorithm over GF(p).
    Returns the minimal LFSR length (order of minimal linear recurrence).

    Input: list of integers (will be reduced mod p)
    Output: integer = order of minimal linear recurrence

    If the entire sequence is zero, returns 0.
    If no recurrence shorter than len(seq)/2 exists, returns len(seq)//2+1
    (sequence is essentially incompressible).
    """
    n = len(seq)
    s = [x % p for x in seq]

    # Check all-zero
    if all(x == 0 for x in s):
        return 0

    # BM state
    C = [1]  # current connection polynomial
    B = [1]  # previous connection polynomial
    L = 0    # current LFSR length
    m = 1    # shift counter
    b = 1    # previous discrepancy

    def modinv(a, mod):
        """Extended Euclidean modular inverse."""
        g, x, _ = extended_gcd(a % mod, mod)
        if g != 1:
            return None
        return x % mod

    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        g, x1, y1 = extended_gcd(b % a, a)
        return g, y1 - (b // a) * x1, x1

    for i in range(n):
        # Compute discrepancy
        d = s[i]
        for j in range(1, len(C)):
            d = (d + C[j] * s[i - j]) % p
        d = d % p

        if d == 0:
            m += 1
        elif 2 * L <= i:
            # Update LFSR
            T = C[:]
            inv_b = modinv(b, p)
            if inv_b is None:
                m += 1
                continue
            coeff = (p - d * inv_b % p) % p

            # C = C - d/b * x^m * B
            shift_B = [0] * m + B
            while len(C) < len(shift_B):
                C.append(0)
            for j in range(len(shift_B)):
                C[j] = (C[j] + coeff * shift_B[j]) % p

            L = i + 1 - L
            B = T
            b = d
            m = 1
        else:
            inv_b = modinv(b, p)
            if inv_b is None:
                m += 1
                continue
            coeff = (p - d * inv_b % p) % p

            shift_B = [0] * m + B
            while len(C) < len(shift_B):
                C.append(0)
            for j in range(len(shift_B)):
                C[j] = (C[j] + coeff * shift_B[j]) % p
            m += 1

    return L


# ── Domain loaders ───────────────────────────────────────────────────

def load_oeis_sequences(n=N_SAMPLE):
    """OEIS: first terms of each sequence. Uses up to SEQ_LEN_MAX terms."""
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
            if len(vals) >= SEQ_LEN_MIN:
                candidates.append((seq_id, vals[:SEQ_LEN_MAX]))
    random.shuffle(candidates)
    selected = candidates[:n]
    print(f"  OEIS: {len(selected)} objects (from {len(candidates)} candidates)")
    return [(s[0], s[1]) for s in selected]


def load_ec_sequences(n=N_SAMPLE):
    """EC: a_p trace sequence (25 primes available in DB)."""
    import duckdb
    con = duckdb.connect(str(ROOT / "charon" / "data" / "charon.duckdb"), read_only=True)
    rows = con.execute(f"""
        SELECT lmfdb_label, aplist FROM elliptic_curves
        WHERE aplist IS NOT NULL AND list_count(aplist) >= {SEQ_LEN_MIN}
        ORDER BY random() LIMIT {n * 3}
    """).fetchall()
    con.close()

    results = []
    for label, aplist in rows:
        if len(results) >= n:
            break
        vals = [int(round(v)) for v in aplist[:SEQ_LEN_MAX]]
        if len(vals) >= SEQ_LEN_MIN:
            results.append((label, vals))
    print(f"  EC: {len(results)} objects (seq_len={len(results[0][1]) if results else 0})")
    return results


def load_mf_sequences(n=N_SAMPLE):
    """MF: Hecke eigenvalue traces."""
    import duckdb
    con = duckdb.connect(str(ROOT / "charon" / "data" / "charon.duckdb"), read_only=True)
    rows = con.execute(f"""
        SELECT lmfdb_label, traces FROM modular_forms
        WHERE traces IS NOT NULL AND list_count(traces) >= {SEQ_LEN_MIN}
        ORDER BY random() LIMIT {n * 3}
    """).fetchall()
    con.close()

    results = []
    for label, traces in rows:
        if len(results) >= n:
            break
        vals = [int(round(t)) for t in traces[:SEQ_LEN_MAX]]
        if len(vals) >= SEQ_LEN_MIN:
            results.append((label, vals))
    print(f"  MF: {len(results)} objects (seq_len={len(results[0][1]) if results else 0})")
    return results


def load_knot_sequences(n=N_SAMPLE):
    """Knots: Jones polynomial coefficients (typically 4-13 terms)."""
    path = ROOT / "cartography" / "knots" / "data" / "knots.json"
    data = json.loads(path.read_text())
    knots = data["knots"]
    random.shuffle(knots)

    results = []
    for k in knots:
        if len(results) >= n:
            break
        coeffs = k.get("jones_coeffs", [])
        if len(coeffs) >= SEQ_LEN_MIN:
            vals = [int(round(c)) for c in coeffs[:SEQ_LEN_MAX]]
            results.append((k["name"], vals))
    print(f"  Knots: {len(results)} objects (seq_len range {SEQ_LEN_MIN}-{min(13, SEQ_LEN_MAX)})")
    return results


def load_lattice_sequences(n=N_SAMPLE):
    """Lattices: theta series first terms."""
    path = ROOT / "cartography" / "lmfdb_dump" / "lat_lattices.json"
    with open(path) as f:
        data = json.load(f)
    records = data.get("records", [])
    random.shuffle(records)

    results = []
    for rec in records:
        if len(results) >= n:
            break
        theta = rec.get("theta_series", [])
        if len(theta) >= SEQ_LEN_MIN:
            vals = [int(round(t)) for t in theta[:SEQ_LEN_MAX]]
            results.append((rec.get("label", rec.get("id", f"lat_{len(results)}")), vals))
    print(f"  Lattices: {len(results)} objects (seq_len={len(results[0][1]) if results else 0})")
    return results


def load_nf_sequences(n=N_SAMPLE):
    """Number fields: discriminant-derived integer sequence.
    Build: [disc_abs, degree, disc_sign, class_number, class_group elts..., ramified primes...]
    Pad to SEQ_LEN_MAX with zeros."""
    path = ROOT / "cartography" / "number_fields" / "data" / "number_fields.json"
    with open(path) as f:
        data = json.load(f)
    random.shuffle(data)

    results = []
    for nf in data:
        if len(results) >= n:
            break
        disc = int(nf.get("disc_abs", 0))
        deg = int(nf.get("degree", 0))
        ds = int(nf.get("disc_sign", 0))
        cn = int(nf.get("class_number", 0))
        cg = nf.get("class_group", [])
        cg_vals = [int(x) for x in cg] if cg else []
        rp = nf.get("ramps", [])
        rp_vals = [int(x) for x in rp] if rp else []

        seq = [disc, deg, ds, cn] + cg_vals + rp_vals
        # Pad to SEQ_LEN_MAX with zeros or truncate
        if len(seq) < SEQ_LEN_MAX:
            seq = seq + [0] * (SEQ_LEN_MAX - len(seq))
        seq = seq[:SEQ_LEN_MAX]
        results.append((nf.get("label", f"nf_{len(results)}"), seq))
    print(f"  NF: {len(results)} objects")
    return results


# ── Analysis ─────────────────────────────────────────────────────────

def compute_domain_compressibility(objects, domain_name, p=BM_MOD_P):
    """Run BM on each object's sequence and compute compressibility stats.
    Each object may have a different sequence length; C = 1 - BM_order/len(seq)."""
    bm_orders = []
    compressibilities = []
    seq_lengths = []
    for label, seq in objects:
        order = berlekamp_massey_gfp(seq, p)
        seq_len = len(seq)
        c = 1.0 - (order / seq_len) if seq_len > 0 else 0.0
        bm_orders.append(order)
        compressibilities.append(c)
        seq_lengths.append(seq_len)

    arr = np.array(compressibilities)
    orders_arr = np.array(bm_orders)
    lens_arr = np.array(seq_lengths)

    return {
        "domain": domain_name,
        "n_objects": len(objects),
        "mean_seq_len": round(float(lens_arr.mean()), 1),
        "min_seq_len": int(lens_arr.min()),
        "max_seq_len": int(lens_arr.max()),
        "bm_mod_p": p,
        "mean_compressibility": round(float(arr.mean()), 6),
        "std_compressibility": round(float(arr.std()), 6),
        "median_compressibility": round(float(np.median(arr)), 6),
        "min_compressibility": round(float(arr.min()), 6),
        "max_compressibility": round(float(arr.max()), 6),
        "mean_bm_order": round(float(orders_arr.mean()), 2),
        "median_bm_order": round(float(np.median(orders_arr)), 2),
        "frac_fully_compressible": round(float((arr >= 0.9).mean()), 4),
        "frac_incompressible": round(float((arr <= 0.1).mean()), 4),
        "quartiles": [round(float(np.percentile(arr, q)), 6) for q in [25, 50, 75]],
    }


def main():
    print("=" * 70)
    print("F29: Arithmetic Object Compressibility Hierarchy")
    print("=" * 70)
    print(f"N_SAMPLE={N_SAMPLE}, SEQ_LEN={SEQ_LEN_MIN}-{SEQ_LEN_MAX}, BM mod p={BM_MOD_P}")
    print()

    # Load all domains
    print("Loading domains...")
    loaders = {
        "OEIS":     load_oeis_sequences,
        "EC":       load_ec_sequences,
        "MF":       load_mf_sequences,
        "Knots":    load_knot_sequences,
        "Lattices": load_lattice_sequences,
        "NF":       load_nf_sequences,
    }

    domain_objects = {}
    for name, loader in loaders.items():
        try:
            domain_objects[name] = loader()
        except Exception as e:
            print(f"  WARNING: {name} failed: {e}")
            domain_objects[name] = []

    # Compute compressibility per domain
    print()
    print("Computing Berlekamp-Massey compressibility...")
    domain_results = {}
    for name, objects in domain_objects.items():
        if not objects:
            print(f"  {name}: SKIPPED (no data)")
            continue
        print(f"  {name}: processing {len(objects)} objects...")
        result = compute_domain_compressibility(objects, name)
        domain_results[name] = result
        print(f"    mean C = {result['mean_compressibility']:.4f}, "
              f"mean BM order = {result['mean_bm_order']:.1f}/{result['mean_seq_len']:.0f}")

    # Rank by mean compressibility (most compressible first)
    ranked = sorted(domain_results.values(),
                    key=lambda x: x["mean_compressibility"], reverse=True)
    print()
    print("=" * 70)
    print("Compressibility Hierarchy (most compressible first):")
    print("-" * 70)
    for i, r in enumerate(ranked, 1):
        print(f"  {i}. {r['domain']:12s}  C = {r['mean_compressibility']:.4f} "
              f"(+/- {r['std_compressibility']:.4f})  "
              f"BM order = {r['mean_bm_order']:.1f}/{r['mean_seq_len']:.0f}")

    # Correlate with F28 spectral gaps
    f28_path = Path(__file__).resolve().parent / "spectral_gap_universality_results.json"
    correlation = None
    spectral_gaps_used = {}
    if f28_path.exists():
        with open(f28_path) as f:
            f28 = json.load(f)
        f28_gaps = f28.get("summary", {}).get("gaps", {})

        # Match domains
        paired_c = []
        paired_g = []
        for name, res in domain_results.items():
            if name in f28_gaps:
                paired_c.append(res["mean_compressibility"])
                paired_g.append(f28_gaps[name])
                spectral_gaps_used[name] = f28_gaps[name]

        if len(paired_c) >= 3:
            from scipy import stats as sp_stats
            r_val, p_val = sp_stats.pearsonr(paired_c, paired_g)
            rho_val, rho_p = sp_stats.spearmanr(paired_c, paired_g)
            correlation = {
                "pearson_r": round(float(r_val), 6),
                "pearson_p": round(float(p_val), 6),
                "spearman_rho": round(float(rho_val), 6),
                "spearman_p": round(float(rho_p), 6),
                "n_domains_matched": len(paired_c),
                "domains_matched": list(spectral_gaps_used.keys()),
                "compressibilities": paired_c,
                "spectral_gaps": paired_g,
            }
            print()
            print(f"F28 spectral gap correlation:")
            print(f"  Pearson  r = {r_val:.4f}, p = {p_val:.4f}")
            print(f"  Spearman rho = {rho_val:.4f}, p = {rho_p:.4f}")
            if abs(r_val) > 0.7 and p_val < 0.1:
                print(f"  => STRONG correlation between compressibility and spectral gap")
            elif abs(r_val) > 0.4:
                print(f"  => MODERATE correlation")
            else:
                print(f"  => WEAK or no correlation")
    else:
        print("\nF28 results not found — skipping spectral gap correlation.")

    # Null model: length-matched random sequences per domain
    # BM on random sequences of length L converges to ~L/2, so C ~ 0.5.
    # But we need per-domain null because seq lengths differ.
    print()
    print("Running length-matched null models (random integer sequences)...")
    null_per_domain = {}
    for r in ranked:
        domain_len = int(round(r["mean_seq_len"]))
        null_cs = []
        for _ in range(500):
            seq = [random.randint(-100, 100) for _ in range(domain_len)]
            order = berlekamp_massey_gfp(seq, BM_MOD_P)
            c = 1.0 - (order / domain_len)
            null_cs.append(c)
        null_arr_d = np.array(null_cs)
        null_per_domain[r["domain"]] = {
            "mean": round(float(null_arr_d.mean()), 6),
            "std": round(float(null_arr_d.std()), 6),
            "seq_len": domain_len,
        }
        print(f"  {r['domain']:12s} (L={domain_len}): null C = {null_arr_d.mean():.4f} +/- {null_arr_d.std():.4f}")

    # Global null at max length for summary
    null_stats = null_per_domain.get(ranked[0]["domain"],
                                      {"mean": 0.5, "std": 0.01})

    # Check which domains are significantly more compressible than their length-matched null
    print()
    print("Significance vs length-matched null:")
    for r in ranked:
        nd = null_per_domain[r["domain"]]
        # Use domain's own std if null std is degenerate (BM on random is very tight)
        null_std = max(nd["std"], r["std_compressibility"] / math.sqrt(r["n_objects"]), 0.001)
        z = (r["mean_compressibility"] - nd["mean"]) / null_std
        sig = "***" if z > 3 else "**" if z > 2 else "*" if z > 1 else ""
        print(f"  {r['domain']:12s}  z = {z:+.2f} {sig}  (null C={nd['mean']:.4f} at L={nd['seq_len']})")
        r["z_vs_null"] = round(float(z), 4)
        r["null_mean_at_length"] = nd["mean"]

    # Hierarchy verdict
    comps = [r["mean_compressibility"] for r in ranked]
    spread = max(comps) - min(comps)
    hierarchy_exists = spread > 0.1
    verdict = ("HIERARCHY EXISTS: domains differ significantly in compressibility"
               if hierarchy_exists else
               "NO CLEAR HIERARCHY: domains have similar compressibility")
    print()
    print(f"Verdict: {verdict}")
    print(f"  Spread = {spread:.4f} (max - min of mean compressibility)")

    # Assemble output
    output = {
        "experiment": "F29_compressibility_hierarchy",
        "parameters": {
            "n_sample": N_SAMPLE,
            "seq_len_min": SEQ_LEN_MIN,
            "seq_len_max": SEQ_LEN_MAX,
            "bm_mod_p": BM_MOD_P,
        },
        "domain_results": {r["domain"]: r for r in ranked},
        "hierarchy": [
            {"rank": i + 1, "domain": r["domain"],
             "mean_compressibility": r["mean_compressibility"]}
            for i, r in enumerate(ranked)
        ],
        "null_model_per_domain": null_per_domain,
        "f28_correlation": correlation,
        "summary": {
            "hierarchy_exists": hierarchy_exists,
            "spread": round(spread, 6),
            "verdict": verdict,
            "most_compressible": ranked[0]["domain"] if ranked else None,
            "least_compressible": ranked[-1]["domain"] if ranked else None,
        }
    }

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT}")


if __name__ == "__main__":
    main()
