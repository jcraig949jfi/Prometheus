"""
ALL-057: Berlekamp-Massey on Graph Statistics vs Prime
=======================================================
Apply BM to the sequences formed by graph statistics (# edges, # triangles,
max clique, # components) as functions of ell for the GL(2) Hecke congruence
graph. If these statistics obey a linear recurrence in ell, the arithmetic
of congruences has algebraic structure beyond what random graphs produce.

Also test the GSp(4) mod-ell graph statistics across ell=2,3,5.
"""

import json, time
import numpy as np
from pathlib import Path
from fractions import Fraction
from collections import defaultdict

V2 = Path(__file__).resolve().parent
HECKE_RESULTS = V2 / "hecke_graph_results.json"
GSP4_RESULTS = V2 / "gsp4_mod2_graph_results.json"
CONG_RESULTS = V2 / "congruence_graph.json"
OUT_PATH = V2 / "bm_graph_statistics_results.json"


def berlekamp_massey_rational(seq, max_order=6):
    """BM over Q. Returns {order, coefficients} or None."""
    n = len(seq)
    if n < 3:
        return None
    s = [Fraction(v) for v in seq]
    c = [Fraction(1)]
    b = [Fraction(1)]
    l_deg = 0
    m = 1
    d_val = Fraction(1)
    for i in range(n):
        disc = s[i]
        for j in range(1, l_deg + 1):
            if j < len(c):
                disc += c[j] * s[i - j]
        if disc == 0:
            m += 1
        elif 2 * l_deg <= i:
            t = list(c)
            coef = -disc / d_val
            while len(c) < len(b) + m:
                c.append(Fraction(0))
            for j in range(len(b)):
                c[j + m] += coef * b[j]
            l_deg = i + 1 - l_deg
            b = t
            d_val = disc
            m = 1
        else:
            coef = -disc / d_val
            while len(c) < len(b) + m:
                c.append(Fraction(0))
            for j in range(len(b)):
                c[j + m] += coef * b[j]
            m += 1
    if l_deg == 0 or l_deg > max_order:
        return None
    # Verify
    for i in range(l_deg, n):
        val = s[i]
        for j in range(1, l_deg + 1):
            if j < len(c):
                val += c[j] * s[i - j]
        if val != 0:
            return None
    coeffs = [float((-c[j]) if j < len(c) else 0) for j in range(1, l_deg + 1)]
    return {"order": l_deg, "coefficients": coeffs}


def main():
    t0 = time.time()
    print("=== ALL-057: Berlekamp-Massey on Graph Statistics vs Prime ===\n")

    # Load Hecke graph results (GL2, per ell)
    print("[1] Loading Hecke congruence graph data...")
    with open(HECKE_RESULTS) as f:
        hecke = json.load(f)

    per_ell = hecke.get("per_ell", {})
    ells = sorted(int(e) for e in per_ell.keys())
    print(f"    Primes available: {ells}")

    # Extract graph statistics as sequences indexed by ell
    stat_names = ["n_congruences", "n_nodes", "n_edges", "n_components", "n_triangles"]
    gl2_seqs = {}
    for stat in stat_names:
        vals = []
        for e in ells:
            v = per_ell[str(e)].get(stat, 0)
            vals.append(v)
        gl2_seqs[stat] = vals
        print(f"    GL2 {stat}: {vals}")

    # Also extract component sizes (largest component)
    largest_comp = []
    for e in ells:
        cs = per_ell[str(e)].get("component_sizes", [])
        largest_comp.append(cs[0] if cs else 0)
    gl2_seqs["largest_component"] = largest_comp
    print(f"    GL2 largest_component: {largest_comp}")

    # Run BM on each sequence
    print("\n[2] Running Berlekamp-Massey on GL2 graph statistics...")
    gl2_bm_results = {}
    for stat, vals in gl2_seqs.items():
        bm = berlekamp_massey_rational(vals)
        gl2_bm_results[stat] = {
            "values": vals,
            "primes": ells,
            "bm_result": bm,
        }
        if bm:
            print(f"    {stat}: RECURRENCE found - order {bm['order']}, coeffs={bm['coefficients']}")
        else:
            print(f"    {stat}: NO recurrence (sequence is genuinely irregular)")

    # Also try ratios: stat(ell+1)/stat(ell)
    print("\n[3] Testing ratios and differences...")
    derived_results = {}
    for stat, vals in gl2_seqs.items():
        # First differences
        diffs = [vals[i+1] - vals[i] for i in range(len(vals)-1)]
        bm_diff = berlekamp_massey_rational(diffs) if len(diffs) >= 3 else None
        # Ratios (skip zeros)
        ratios = []
        for i in range(len(vals)-1):
            if vals[i] != 0:
                ratios.append(round(vals[i+1] / vals[i], 6))
        bm_ratio = berlekamp_massey_rational([Fraction(r).limit_denominator(1000) for r in ratios]) if len(ratios) >= 3 else None

        derived_results[stat] = {
            "differences": diffs,
            "bm_differences": bm_diff,
            "ratios": ratios,
            "bm_ratios": bm_ratio,
        }
        if bm_diff:
            print(f"    Δ{stat}: RECURRENCE order={bm_diff['order']}")
        if bm_ratio:
            print(f"    {stat} ratios: RECURRENCE order={bm_ratio['order']}")

    # GSp4 data (only 2-3 ell values usually)
    print("\n[4] Loading GSp4 data...")
    with open(GSP4_RESULTS) as f:
        gsp4 = json.load(f)
    gsp4_stats = {}
    for tag in ["mod2_all", "mod3_all"]:
        if tag in gsp4:
            d = gsp4[tag]
            gsp4_stats[tag] = {s: d.get(s, 0) for s in stat_names if s in d}
    print(f"    GSp4 tags: {list(gsp4_stats.keys())}")
    for tag, stats in gsp4_stats.items():
        print(f"    {tag}: {stats}")

    # Power-law fit: stat ~ ell^alpha
    print("\n[5] Power-law fits: stat(ell) ~ A * ell^alpha...")
    power_law_results = {}
    for stat, vals in gl2_seqs.items():
        pos_mask = [(e > 0 and v > 0) for e, v in zip(ells, vals)]
        pos_ells = [e for e, m in zip(ells, pos_mask) if m]
        pos_vals = [v for v, m in zip(vals, pos_mask) if m]
        if len(pos_ells) >= 3:
            log_e = np.log(pos_ells)
            log_v = np.log(pos_vals)
            alpha, log_A = np.polyfit(log_e, log_v, 1)
            predicted = np.exp(log_A) * np.array(pos_ells)**alpha
            residuals = np.array(pos_vals) - predicted
            r2 = 1 - np.sum(residuals**2) / np.sum((np.array(pos_vals) - np.mean(pos_vals))**2)
            power_law_results[stat] = {
                "alpha": round(float(alpha), 4),
                "A": round(float(np.exp(log_A)), 4),
                "R2": round(float(r2), 4),
            }
            print(f"    {stat}: alpha={alpha:.3f}, A={np.exp(log_A):.2f}, R²={r2:.4f}")

    elapsed = time.time() - t0
    n_recurrences = sum(1 for v in gl2_bm_results.values() if v["bm_result"] is not None)
    n_derived = sum(1 for v in derived_results.values() if v["bm_differences"] or v["bm_ratios"])

    output = {
        "challenge": "ALL-057",
        "title": "Berlekamp-Massey on Graph Statistics vs Prime",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "gl2_hecke": {"primes": ells, "statistics": gl2_bm_results, "derived": derived_results},
        "gsp4": gsp4_stats,
        "power_law_fits": power_law_results,
        "summary": {
            "n_raw_recurrences": n_recurrences,
            "n_derived_recurrences": n_derived,
            "total_sequences_tested": len(gl2_seqs),
        },
        "assessment": None,
    }

    if n_recurrences > 0:
        output["assessment"] = f"ALGEBRAIC STRUCTURE: {n_recurrences}/{len(gl2_seqs)} graph statistics obey linear recurrences in ell — congruence counting has hidden regularity"
    elif n_derived > 0:
        output["assessment"] = f"WEAK STRUCTURE: raw statistics irregular, but {n_derived} derived sequences (diffs/ratios) show recurrence"
    else:
        best_r2 = max((v["R2"] for v in power_law_results.values()), default=0)
        output["assessment"] = f"NO RECURRENCE: graph statistics are genuinely irregular in ell. Best power-law R²={best_r2:.3f}"

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
