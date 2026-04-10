#!/usr/bin/env python3
"""
Berlekamp-Massey on PDG particle mass sequences.

Tests whether sorted particle masses (in MeV, rounded to integers)
satisfy a linear recurrence of low order.

Orderings tested:
  1. All 226 particles sorted by mass
  2. Per-family: leptons, quarks, mesons, baryons sorted by mass
  3. Mass ratios m_{i+1}/m_i (quantized to integer parts per million)

Null comparison: random integer sequences of same length.

Author: Charon
Date: 2026-04-10
"""

import json
import os
import sys
import random
import numpy as np
from pathlib import Path

# ── Berlekamp-Massey over integers (using modular arithmetic) ──────────

def berlekamp_massey_mod(seq, p):
    """
    Berlekamp-Massey algorithm over GF(p).
    Returns the shortest LFSR (as list of coefficients) that generates seq.
    """
    n = len(seq)
    s = [x % p for x in seq]

    C = [1]  # current connection polynomial
    B = [1]  # previous connection polynomial
    L = 0    # current LFSR length
    m = 1    # shift count
    b = 1    # previous discrepancy

    for i in range(n):
        # compute discrepancy
        d = s[i]
        for j in range(1, L + 1):
            if j < len(C):
                d = (d + C[j] * s[i - j]) % p
        if d == 0:
            m += 1
        elif 2 * L <= i:
            T = list(C)
            coeff = (d * pow(b, p - 2, p)) % p
            # extend C if needed
            while len(C) < len(B) + m:
                C.append(0)
            for j in range(len(B)):
                C[j + m] = (C[j + m] - coeff * B[j]) % p
            L = i + 1 - L
            B = T
            b = d
            m = 1
        else:
            coeff = (d * pow(b, p - 2, p)) % p
            while len(C) < len(B) + m:
                C.append(0)
            for j in range(len(B)):
                C[j + m] = (C[j + m] - coeff * B[j]) % p
            m += 1

    return L, C[1:L + 1]


def test_recurrence_multimod(seq, max_order=12):
    """
    Test if integer sequence satisfies a linear recurrence of order <= max_order.
    Use multiple large primes; a true recurrence will show consistent order across primes.
    """
    primes = [1000000007, 1000000009, 998244353, 999999937, 1000000021]
    orders = []
    for p in primes:
        L, _ = berlekamp_massey_mod(seq, p)
        orders.append(L)

    min_order = min(orders)
    max_found = max(orders)
    consistent = (min_order == max_found)

    return {
        "min_order": min_order,
        "max_order_found": max_found,
        "consistent_across_primes": consistent,
        "orders_per_prime": orders,
        "seq_length": len(seq),
        "ratio_order_to_length": round(min_order / len(seq), 4) if len(seq) > 0 else None
    }


def verify_recurrence(seq, order, prime):
    """Verify that BM-found recurrence actually predicts the sequence mod p."""
    L, coeffs = berlekamp_massey_mod(seq, prime)
    if L > order:
        return False, L
    # Check: predict seq[L:] from coeffs
    s = [x % prime for x in seq]
    for i in range(L, len(s)):
        pred = 0
        for j in range(len(coeffs)):
            pred = (pred + coeffs[j] * s[i - 1 - j]) % prime
        pred = (-pred) % prime
        if pred != s[i]:
            return False, L
    return True, L


# ── Particle family classification by MC ID ───────────────────────────

def classify_particle(mc_id):
    """Classify particle by MC ID into family."""
    if mc_id is None:
        return "unknown"
    aid = abs(mc_id)
    # Leptons: 11-18
    if 11 <= aid <= 18:
        return "lepton"
    # Quarks: 1-8
    if 1 <= aid <= 8:
        return "quark"
    # Gauge/Higgs bosons: 21-37
    if 21 <= aid <= 37:
        return "gauge_boson"
    # Baryons: mc_id >= 1000 and first digit pattern (4+ digits starting with 1-5, or excited states)
    # Standard: baryons have IDs like 2112 (neutron), 2212 (proton), etc.
    # Convention: baryons have last 2 digits encoding spin, middle digits encode quarks
    # IDs 1000-9999 with certain patterns = baryons
    # Excited baryons: 5-digit+ starting with 1xxxx, 2xxxx, etc.
    # Mesons: IDs 100-999 and excited mesons 10000+
    # Simple heuristic based on PDG MC numbering:
    #   Mesons: IDs where floor(id/1000) is 0 (but id >= 100), or excited mesons
    #   Baryons: IDs where the thousands digit structure indicates 3-quark

    if aid < 100:
        return "gauge_boson"  # catch-all for low IDs

    # Use the PDG numbering scheme:
    # Mesons: q qbar states. IDs: NNNs where N encodes quark content
    #   Range roughly 100-999 for ground states
    # Baryons: 3-quark states. IDs: NNNNs (4+ digits for ground states)
    #   Range 1000+ for ground states

    # Ground state mesons: 100-999
    # Excited mesons: 10000-series, 20000-series, 30000-series, 100000-series, 9000000-series
    # Ground state baryons: 1000-9999
    # Excited baryons: 10000-series with baryon-like structure

    # Better approach: check digit count and leading digits
    digits = str(aid)
    n_digits = len(digits)

    if n_digits <= 3:
        return "meson"  # ground state mesons (111, 211, 321, etc.)

    if n_digits == 4:
        # Baryons: 1112, 1114, 2112, 2212, 3112, 3122, 3212, 3222, 3312, 3322, 3334
        # 4112, 4122, 4132, 4212, 4222, 4232, 4312, 4322, 4332, 4334
        # 5112, 5122, 5132, 5222, 5232, 5332
        # Mesons in 4-digit: none in standard scheme
        return "baryon"

    if n_digits == 5:
        # Excited states. Check if the base (last 4 digits) looks like a baryon
        base = int(digits[-4:])
        if base >= 1000:
            return "baryon"  # excited baryon
        else:
            return "meson"   # excited meson

    if n_digits == 6:
        base = int(digits[-4:])
        if base >= 1000:
            return "baryon"
        else:
            return "meson"

    if n_digits == 7:
        # 9000111 etc. = mesons
        base = int(digits[-3:])
        return "meson"  # these are all exotic/excited mesons

    return "unknown"


def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    data_path = repo_root / "cartography" / "physics" / "data" / "pdg" / "particles.json"
    out_path = repo_root / "cartography" / "v2" / "pdg_recurrence_results.json"

    with open(data_path) as f:
        particles = json.load(f)

    print(f"Loaded {len(particles)} particles")

    # ── Build sequences ────────────────────────────────────────────────

    # All particles sorted by mass (exclude zero-mass)
    all_masses = []
    families = {"lepton": [], "quark": [], "meson": [], "baryon": [], "gauge_boson": []}

    for p in particles:
        mass_gev = p.get("mass_GeV", 0)
        mc_id = p.get("mc_ids", [None])[0]
        if mass_gev <= 0:
            continue
        mass_mev = round(mass_gev * 1000)  # MeV, integer
        family = classify_particle(mc_id)
        all_masses.append(mass_mev)
        if family in families:
            families[family].append(mass_mev)

    all_masses.sort()
    for fam in families:
        families[fam].sort()

    print(f"Non-zero-mass particles: {len(all_masses)}")
    for fam, masses in families.items():
        print(f"  {fam}: {len(masses)} particles")

    # Mass ratios (quantized to integer ppm for BM)
    ratios_ppm = []
    for i in range(len(all_masses) - 1):
        if all_masses[i] > 0:
            ratio = all_masses[i + 1] / all_masses[i]
            ratios_ppm.append(round(ratio * 1_000_000))

    # ── Run Berlekamp-Massey ───────────────────────────────────────────

    results = {}

    # Test 1: All masses sorted
    print("\n=== All masses sorted ===")
    bm_all = test_recurrence_multimod(all_masses)
    print(f"  BM order: {bm_all['min_order']} (of {bm_all['seq_length']} terms)")
    print(f"  Consistent: {bm_all['consistent_across_primes']}")
    print(f"  Order/Length ratio: {bm_all['ratio_order_to_length']}")
    results["all_masses_sorted"] = bm_all

    # Test 2: Per-family
    print("\n=== Per-family ===")
    for fam, masses in families.items():
        if len(masses) < 4:
            print(f"  {fam}: too few particles ({len(masses)}), skipping")
            results[f"family_{fam}"] = {"skipped": True, "count": len(masses)}
            continue
        bm_fam = test_recurrence_multimod(masses)
        print(f"  {fam}: BM order {bm_fam['min_order']} (of {bm_fam['seq_length']} terms), "
              f"ratio={bm_fam['ratio_order_to_length']}")
        results[f"family_{fam}"] = bm_fam

    # Test 3: Mass ratios
    print("\n=== Mass ratios (ppm) ===")
    if len(ratios_ppm) > 3:
        bm_ratios = test_recurrence_multimod(ratios_ppm)
        print(f"  BM order: {bm_ratios['min_order']} (of {bm_ratios['seq_length']} terms)")
        print(f"  Ratio: {bm_ratios['ratio_order_to_length']}")
        results["mass_ratios_ppm"] = bm_ratios

    # ── Null comparison: random sequences ──────────────────────────────

    print("\n=== Random null comparison ===")
    random.seed(42)
    null_results = {}
    for label, seq in [("all_masses", all_masses), ("ratios_ppm", ratios_ppm)]:
        n = len(seq)
        if n < 4:
            continue
        max_val = max(seq) if seq else 1000
        null_orders = []
        n_trials = 20
        for trial in range(n_trials):
            rnd_seq = [random.randint(1, max_val) for _ in range(n)]
            bm_rnd = test_recurrence_multimod(rnd_seq)
            null_orders.append(bm_rnd["min_order"])

        null_mean = np.mean(null_orders)
        null_std = np.std(null_orders)
        null_results[label] = {
            "n_trials": n_trials,
            "null_mean_order": round(float(null_mean), 2),
            "null_std_order": round(float(null_std), 2),
            "null_min": int(min(null_orders)),
            "null_max": int(max(null_orders)),
            "seq_length": n
        }
        print(f"  {label} (n={n}): null BM order = {null_mean:.1f} ± {null_std:.1f} "
              f"(range [{min(null_orders)}, {max(null_orders)}])")

    results["null_comparison"] = null_results

    # ── Per-family mass ratios ─────────────────────────────────────────

    print("\n=== Per-family mass ratios ===")
    for fam, masses in families.items():
        if len(masses) < 5:
            continue
        fam_ratios = []
        for i in range(len(masses) - 1):
            if masses[i] > 0:
                fam_ratios.append(round(masses[i + 1] / masses[i] * 1_000_000))
        if len(fam_ratios) >= 4:
            bm_fr = test_recurrence_multimod(fam_ratios)
            print(f"  {fam} ratios: BM order {bm_fr['min_order']} (of {bm_fr['seq_length']} terms), "
                  f"ratio={bm_fr['ratio_order_to_length']}")
            results[f"family_{fam}_ratios"] = bm_fr

    # ── Specific recurrence check at low orders ────────────────────────

    print("\n=== Low-order recurrence verification ===")
    p_check = 1000000007
    for label, seq in [("all_masses", all_masses)] + [(f"family_{k}", v) for k, v in families.items() if len(v) >= 4]:
        for order in range(2, 13):
            valid, found = verify_recurrence(seq, order, p_check)
            if valid and found <= order:
                print(f"  {label}: satisfies order-{found} recurrence mod {p_check}")
                results[f"{label}_verified_order"] = found
                break
        else:
            # BM order is at least floor(n/2) for generic sequences
            L, _ = berlekamp_massey_mod(seq, p_check)
            results[f"{label}_verified_order"] = f"no low-order recurrence (BM={L})"

    # ── Summary ────────────────────────────────────────────────────────

    summary = {
        "any_low_order_recurrence": False,
        "minimum_recurrence_order": None,
        "best_candidate": None,
        "interpretation": ""
    }

    best_ratio = 1.0
    best_label = None
    for key, val in results.items():
        if isinstance(val, dict) and "ratio_order_to_length" in val and val["ratio_order_to_length"] is not None:
            if val["ratio_order_to_length"] < best_ratio:
                best_ratio = val["ratio_order_to_length"]
                best_label = key
                summary["minimum_recurrence_order"] = val["min_order"]

    if best_ratio < 0.25:
        summary["any_low_order_recurrence"] = True
        summary["best_candidate"] = best_label
        summary["interpretation"] = (
            f"Sequence '{best_label}' has BM order / length = {best_ratio:.4f}, "
            f"significantly below the ~0.5 expected for random sequences. "
            f"This suggests genuine low-order structure."
        )
    else:
        summary["any_low_order_recurrence"] = False
        summary["best_candidate"] = best_label
        summary["interpretation"] = (
            f"No particle mass ordering shows a low-order linear recurrence. "
            f"Best ratio (order/length) = {best_ratio:.4f} for '{best_label}', "
            f"which is within or near the random baseline (~0.5). "
            f"Particle masses do NOT satisfy an integer linear recurrence of order <= 12."
        )

    results["summary"] = summary
    print(f"\n{'='*60}")
    print(f"SUMMARY: {summary['interpretation']}")
    print(f"{'='*60}")

    # ── Save ───────────────────────────────────────────────────────────

    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
