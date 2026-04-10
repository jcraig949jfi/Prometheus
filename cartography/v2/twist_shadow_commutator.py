"""
OSC-3: Twist/Shadow Commutator — Does Twisting Preserve Oscillation?
=====================================================================

Test whether the autocorrelation structure of a_p sequences is invariant
under the quadratic twist operator. If AC(twist(f)) ~ AC(f) for twist
partners, then oscillation is an intrinsic property of the twist orbit,
not the individual form.

The commutator test: if T = twist and S = "extract AC shadow",
does T∘S ≈ S∘T?  Measure ||AC(twist(f)) - AC(f)|| for twist partners
vs random form pairs.

Data: charon.duckdb modular_forms table + graph_edges twist network.
"""

import sys
import json
import math
import random
import numpy as np
import duckdb
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(line_buffering=True)

ROOT = Path(__file__).resolve().parents[2]  # F:/Prometheus
DB_PATH = ROOT / "charon" / "data" / "charon.duckdb"
OUT_PATH = Path(__file__).resolve().parent / "twist_shadow_commutator_results.json"

random.seed(42)
np.random.seed(42)

MAX_LAG = 15

# ── The 5-form twist orbit from OSC-2 ──
TWIST_ORBIT = ["15.2.a.a", "45.2.a.a", "75.2.a.b", "240.2.a.d", "960.2.a.l"]


def sieve(limit):
    """Sieve of Eratosthenes."""
    is_p = [True] * (limit + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_p[i]:
            for j in range(i * i, limit + 1, i):
                is_p[j] = False
    return [i for i in range(2, limit + 1) if is_p[i]]


PRIMES = sieve(1000)  # primes up to 997


def get_good_primes(level):
    """Return primes not dividing the level (good primes)."""
    return [p for p in PRIMES if level % p != 0]


def extract_ap_at_good_primes(traces, level):
    """
    traces is indexed by prime index: traces[i] = a_{p_i} where p_i is the
    (i+1)-th prime (p_0=2, p_1=3, ...).
    Return list of (prime, a_p) for good primes only.
    """
    result = []
    for i, p in enumerate(PRIMES):
        if i >= len(traces):
            break
        if level % p != 0:
            result.append((p, traces[i]))
    return result


def autocorrelation(values, max_lag):
    """
    Compute normalized autocorrelation for lags 1..max_lag.
    AC(k) = (1/N) sum_{i=0}^{N-k-1} (x_i - mu)(x_{i+k} - mu) / var
    """
    x = np.array(values, dtype=float)
    n = len(x)
    if n < max_lag + 2:
        return [0.0] * max_lag
    mu = x.mean()
    var = x.var()
    if var < 1e-12:
        return [0.0] * max_lag
    xc = x - mu
    ac = []
    for k in range(1, max_lag + 1):
        c = np.sum(xc[:n - k] * xc[k:]) / (n * var)
        ac.append(float(c))
    return ac


def ac_distance(ac1, ac2):
    """Euclidean distance between two AC vectors."""
    a = np.array(ac1)
    b = np.array(ac2)
    return float(np.sqrt(np.sum((a - b) ** 2)))


def strongest_lag(ac_vec):
    """Return the 1-indexed lag with strongest |AC|."""
    abs_ac = [abs(v) for v in ac_vec]
    return abs_ac.index(max(abs_ac)) + 1


def main():
    print("=" * 70)
    print("OSC-3: Twist/Shadow Commutator")
    print("=" * 70)

    con = duckdb.connect(str(DB_PATH), read_only=True)

    # ── Step 1: Extract a_p at good primes for the 5 orbit forms ──
    print("\n[1] Extracting a_p sequences for twist orbit...")
    orbit_data = {}
    for label in TWIST_ORBIT:
        row = con.execute(
            "SELECT level, traces FROM modular_forms WHERE lmfdb_label = ?",
            [label]
        ).fetchone()
        if row is None:
            print(f"  WARNING: {label} not found in DB!")
            continue
        level, traces = row
        good = extract_ap_at_good_primes(traces, level)
        orbit_data[label] = {
            "level": level,
            "good_primes": [g[0] for g in good],
            "ap_values": [g[1] for g in good],
            "n_good": len(good),
        }
        print(f"  {label}: level={level}, {len(good)} good primes")

    # ── Step 2: Compute AC(1..15) for each form ──
    print("\n[2] Computing autocorrelation vectors (lags 1-15)...")
    orbit_ac = {}
    for label, data in orbit_data.items():
        ac = autocorrelation(data["ap_values"], MAX_LAG)
        orbit_ac[label] = ac
        best_k = strongest_lag(ac)
        print(f"  {label}: AC = [{', '.join(f'{v:.4f}' for v in ac)}]")
        print(f"    strongest lag = {best_k} (AC={ac[best_k-1]:.4f}), lag-3 AC = {ac[2]:.4f}")

    # ── Step 3: Compare lag-3 structure across orbit ──
    print("\n[3] Lag-3 comparison across twist orbit:")
    lag3_values = {label: ac[2] for label, ac in orbit_ac.items()}
    lag3_signs = {label: (1 if v > 0 else -1 if v < 0 else 0) for label, v in lag3_values.items()}
    all_same_sign = len(set(lag3_signs.values())) == 1

    ref_ac3 = lag3_values[TWIST_ORBIT[0]]
    print(f"  Reference (15.2.a.a) lag-3 AC = {ref_ac3:.4f}")
    for label in TWIST_ORBIT:
        v = lag3_values[label]
        sign_str = "+" if v > 0 else "-" if v < 0 else "0"
        print(f"  {label}: AC(3) = {v:.4f} (sign={sign_str})")
    print(f"  All same sign at lag 3? {all_same_sign}")

    # ── Step 4: AC distance between all twist partner pairs ──
    print("\n[4] AC distance between twist orbit pairs:")
    orbit_labels = list(orbit_ac.keys())
    n_orbit = len(orbit_labels)
    twist_distances = []
    for i in range(n_orbit):
        for j in range(i + 1, n_orbit):
            d = ac_distance(orbit_ac[orbit_labels[i]], orbit_ac[orbit_labels[j]])
            twist_distances.append(d)
            print(f"  d({orbit_labels[i]}, {orbit_labels[j]}) = {d:.4f}")

    mean_twist_dist = np.mean(twist_distances)
    print(f"  Mean twist-partner AC distance: {mean_twist_dist:.4f}")

    # ── Step 5: Compare with random form pairs ──
    print("\n[5] Random baseline: AC distance between random weight-2 dim-1 form pairs...")

    # Get a sample of weight-2, dim-1 forms
    all_forms = con.execute(
        "SELECT lmfdb_label, level, traces FROM modular_forms "
        "WHERE weight = 2 AND dim = 1 AND char_order = 1 "
        "ORDER BY RANDOM() LIMIT 200"
    ).fetchall()
    print(f"  Loaded {len(all_forms)} random weight-2 dim-1 forms")

    random_acs = {}
    for label, level, traces in all_forms:
        good = extract_ap_at_good_primes(traces, level)
        if len(good) < MAX_LAG + 5:
            continue
        ac = autocorrelation([g[1] for g in good], MAX_LAG)
        random_acs[label] = ac

    # Compute random pair distances (sample 500 pairs)
    random_labels = list(random_acs.keys())
    n_random = len(random_labels)
    random_distances = []
    for _ in range(min(500, n_random * (n_random - 1) // 2)):
        i, j = random.sample(range(n_random), 2)
        d = ac_distance(random_acs[random_labels[i]], random_acs[random_labels[j]])
        random_distances.append(d)

    mean_random_dist = np.mean(random_distances)
    std_random_dist = np.std(random_distances)
    z_score = (mean_twist_dist - mean_random_dist) / std_random_dist if std_random_dist > 0 else 0
    print(f"  Mean random AC distance: {mean_random_dist:.4f} +/- {std_random_dist:.4f}")
    print(f"  Twist orbit mean: {mean_twist_dist:.4f}")
    print(f"  z-score (twist vs random): {z_score:.2f}")
    print(f"  Twist partners {'MORE' if mean_twist_dist < mean_random_dist else 'LESS'} "
          f"AC-similar than random")

    # ── Step 6: Commutator test ──
    # For twist partners, AC(twist(f)) should ~ AC(f) if oscillation is twist-invariant.
    # The "commutator" measures how much the AC extraction and twist operators fail to commute.
    # Since we're looking at AC of actual forms (not twisting AC vectors), the commutator
    # ||AC(twist(f)) - AC(f)|| is just the pairwise distance already computed.
    # We formalize: commutator magnitude = mean ||AC(f_i) - AC(f_j)|| for twist-connected pairs.
    print("\n[6] Commutator test: ||S.T(f) - T.S(f)||")
    print("  S = extract AC shadow, T = twist operator")
    print(f"  Since T maps f -> f', commutator = ||AC(f') - AC(f)|| = twist pair distance")
    print(f"  Mean commutator magnitude (orbit): {mean_twist_dist:.4f}")
    print(f"  Mean commutator magnitude (random): {mean_random_dist:.4f}")
    commutator_ratio = mean_twist_dist / mean_random_dist if mean_random_dist > 0 else float('inf')
    print(f"  Ratio (twist/random): {commutator_ratio:.3f}")
    if commutator_ratio < 0.5:
        print("  => Commutator is SMALL: twist approximately preserves AC shadow")
    elif commutator_ratio < 0.8:
        print("  => Commutator is MODERATE: partial preservation")
    else:
        print("  => Commutator is LARGE: twist does NOT preserve AC shadow")

    # ── Step 7: Full population test using twist edges ──
    print("\n[7] Full population: strongest-lag agreement across twist pairs...")

    # Get all twist pairs between weight-2, dim-1 forms
    twist_pairs = con.execute("""
        SELECT DISTINCT g.source_label, g.target_label
        FROM graph_edges g
        JOIN modular_forms m1 ON g.source_label = m1.lmfdb_label
        JOIN modular_forms m2 ON g.target_label = m2.lmfdb_label
        WHERE g.edge_type = 'twist'
          AND m1.weight = 2 AND m1.dim = 1 AND m1.char_order = 1
          AND m2.weight = 2 AND m2.dim = 1 AND m2.char_order = 1
        LIMIT 2000
    """).fetchall()
    print(f"  Found {len(twist_pairs)} twist pairs (weight-2, dim-1, trivial char)")

    # Need AC for all forms involved
    involved_labels = set()
    for s, t in twist_pairs:
        involved_labels.add(s)
        involved_labels.add(t)
    print(f"  Unique forms involved: {len(involved_labels)}")

    # Batch load
    label_list = list(involved_labels)
    all_acs = {}
    batch_size = 200
    for start in range(0, len(label_list), batch_size):
        batch = label_list[start:start + batch_size]
        placeholders = ", ".join(["?" for _ in batch])
        rows = con.execute(
            f"SELECT lmfdb_label, level, traces FROM modular_forms "
            f"WHERE lmfdb_label IN ({placeholders})",
            batch
        ).fetchall()
        for label, level, traces in rows:
            good = extract_ap_at_good_primes(traces, level)
            if len(good) >= MAX_LAG + 5:
                ac = autocorrelation([g[1] for g in good], MAX_LAG)
                all_acs[label] = ac

    # Compute strongest lag agreement
    same_kstar = 0
    total_pairs = 0
    pair_distances = []
    lag3_sign_agree = 0
    lag3_mag_diffs = []

    for s, t in twist_pairs:
        if s not in all_acs or t not in all_acs:
            continue
        total_pairs += 1
        ac_s, ac_t = all_acs[s], all_acs[t]

        # k* agreement
        ks_s = strongest_lag(ac_s)
        ks_t = strongest_lag(ac_t)
        if ks_s == ks_t:
            same_kstar += 1

        # AC distance
        d = ac_distance(ac_s, ac_t)
        pair_distances.append(d)

        # Lag-3 sign agreement
        if (ac_s[2] > 0 and ac_t[2] > 0) or (ac_s[2] < 0 and ac_t[2] < 0):
            lag3_sign_agree += 1
        lag3_mag_diffs.append(abs(ac_s[2] - ac_t[2]))

    kstar_rate = same_kstar / total_pairs if total_pairs > 0 else 0
    lag3_sign_rate = lag3_sign_agree / total_pairs if total_pairs > 0 else 0
    pop_mean_dist = np.mean(pair_distances) if pair_distances else 0

    print(f"  Pairs with AC data: {total_pairs}")
    print(f"  Same k* (strongest lag) rate: {same_kstar}/{total_pairs} = {kstar_rate:.3f}")
    print(f"  Lag-3 sign agreement rate: {lag3_sign_agree}/{total_pairs} = {lag3_sign_rate:.3f}")
    print(f"  Mean twist-pair AC distance (population): {pop_mean_dist:.4f}")
    print(f"  Mean lag-3 magnitude difference: {np.mean(lag3_mag_diffs):.4f}")

    # Random baseline for k* agreement
    random_same_kstar = 0
    random_total = 0
    random_pop_dists = []
    random_labels_pop = list(all_acs.keys())
    for _ in range(min(total_pairs, 500)):
        i, j = random.sample(range(len(random_labels_pop)), 2)
        ac_i = all_acs[random_labels_pop[i]]
        ac_j = all_acs[random_labels_pop[j]]
        random_total += 1
        if strongest_lag(ac_i) == strongest_lag(ac_j):
            random_same_kstar += 1
        random_pop_dists.append(ac_distance(ac_i, ac_j))

    random_kstar_rate = random_same_kstar / random_total if random_total > 0 else 0
    random_pop_mean = np.mean(random_pop_dists) if random_pop_dists else 0
    print(f"\n  Random baseline k* agreement: {random_same_kstar}/{random_total} = {random_kstar_rate:.3f}")
    print(f"  Random baseline AC distance: {random_pop_mean:.4f}")
    print(f"  k* enrichment (twist/random): {kstar_rate / random_kstar_rate:.2f}x" if random_kstar_rate > 0 else "")

    # ── Summary ──
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    preserves = mean_twist_dist < mean_random_dist and commutator_ratio < 0.8
    print(f"  Lag-3 peak in all 5 orbit forms (same sign): {all_same_sign}")
    print(f"  Commutator ratio (twist/random): {commutator_ratio:.3f}")
    print(f"  Twist preserves AC shadow: {'YES' if preserves else 'NO'}")
    print(f"  Population k* agreement: {kstar_rate:.3f} (random: {random_kstar_rate:.3f})")
    print(f"  Population lag-3 sign agreement: {lag3_sign_rate:.3f}")

    # ── Build results ──
    results = {
        "challenge": "OSC-3",
        "title": "Twist/Shadow Commutator",
        "twist_orbit": TWIST_ORBIT,
        "orbit_ac_vectors": {label: ac for label, ac in orbit_ac.items()},
        "orbit_lag3": lag3_values,
        "orbit_lag3_all_same_sign": all_same_sign,
        "orbit_strongest_lags": {label: strongest_lag(ac) for label, ac in orbit_ac.items()},
        "orbit_pairwise_distances": {
            f"{orbit_labels[i]} vs {orbit_labels[j]}": ac_distance(
                orbit_ac[orbit_labels[i]], orbit_ac[orbit_labels[j]]
            )
            for i in range(n_orbit) for j in range(i + 1, n_orbit)
        },
        "orbit_mean_ac_distance": float(mean_twist_dist),
        "random_mean_ac_distance": float(mean_random_dist),
        "random_std_ac_distance": float(std_random_dist),
        "z_score_twist_vs_random": float(z_score),
        "commutator_ratio": float(commutator_ratio),
        "commutator_verdict": "SMALL" if commutator_ratio < 0.5 else
                              "MODERATE" if commutator_ratio < 0.8 else "LARGE",
        "population": {
            "n_twist_pairs": total_pairs,
            "kstar_agreement_rate": float(kstar_rate),
            "kstar_agreement_count": same_kstar,
            "lag3_sign_agreement_rate": float(lag3_sign_rate),
            "mean_twist_pair_ac_distance": float(pop_mean_dist),
            "mean_lag3_magnitude_diff": float(np.mean(lag3_mag_diffs)) if lag3_mag_diffs else None,
            "random_kstar_rate": float(random_kstar_rate),
            "random_mean_ac_distance": float(random_pop_mean),
            "kstar_enrichment": float(kstar_rate / random_kstar_rate) if random_kstar_rate > 0 else None,
        },
        "verdict": (
            "TWIST PRESERVES AC SHADOW" if preserves else
            "TWIST DOES NOT PRESERVE AC SHADOW"
        ),
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")

    con.close()


if __name__ == "__main__":
    main()
