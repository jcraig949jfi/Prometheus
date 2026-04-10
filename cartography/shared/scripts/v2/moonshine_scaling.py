"""
R3-7: Universal Scaling Law on Moonshine Bridges
==================================================
Test whether the ~8x flat mod-p enrichment (universal across OEIS families,
genus-2 ST groups, and Fungrim modules) holds for moonshine bridges specifically.

Partition the 307 moonshine bridges by type:
  - McKay-Thompson / monstrous (j-function, Monster group)
  - Modular (Eisenstein, Ramanujan tau)
  - Mock theta (Ramanujan mock theta functions)
  - Umbral M24
  - Theta / lattice theta (Jacobi theta, D4/E8/Leech lattice)

Then compute mod-p fingerprint enrichment within each partition and compare
to the universal ~8x baseline.

Usage:
    python moonshine_scaling.py
"""

import gzip
import json
import random
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[4]
V2_DIR = Path(__file__).resolve().parent
EXPANSION_RESULTS = V2_DIR / "moonshine_expansion_results.json"
OEIS_RESULTS = V2_DIR / "moonshine_oeis_results.json"
OEIS_STRIPPED_GZ = ROOT / "cartography" / "oeis" / "data" / "stripped_full.gz"
OEIS_STRIPPED_TXT = ROOT / "cartography" / "oeis" / "data" / "stripped_new.txt"
OUT_FILE = V2_DIR / "moonshine_scaling_results.json"

PRIMES = [2, 3, 5, 7, 11]
FP_LEN = 8  # fingerprint window length (shorter for reliable statistics at larger primes)
N_RANDOM_PAIRS = 200000  # for random baseline

random.seed(42)
np.random.seed(42)


# ---------------------------------------------------------------------------
# Core sequence metadata: type classification for all 21 cores
# ---------------------------------------------------------------------------
CORE_META = {
    "A000521": {"type": "monstrous", "name": "Klein j-function"},
    "A007191": {"type": "monstrous", "name": "McKay-Thompson T_2"},
    "A014708": {"type": "monstrous", "name": "McKay-Thompson T_3"},
    "A007246": {"type": "monstrous", "name": "McKay-Thompson T_5"},
    "A007267": {"type": "monstrous", "name": "j-function (1728*j)"},
    "A000594": {"type": "modular", "name": "Ramanujan tau (weight 12)"},
    "A006352": {"type": "modular", "name": "Eisenstein E_2"},
    "A004009": {"type": "modular", "name": "Eisenstein E_4"},
    "A013973": {"type": "modular", "name": "Eisenstein E_6"},
    "A008410": {"type": "modular", "name": "Eisenstein E_8"},
    "A013974": {"type": "modular", "name": "Eisenstein E_10"},
    "A029829": {"type": "modular", "name": "Eisenstein E_12"},
    "A045488": {"type": "mock_theta", "name": "Ramanujan mock theta f(q)"},
    "A001488": {"type": "mock_theta", "name": "Mock theta 2nd order"},
    "A053250": {"type": "umbral", "name": "Umbral moonshine M24"},
    "A000118": {"type": "theta", "name": "Sum of 4 squares (theta_3^4)"},
    "A008443": {"type": "theta", "name": "Sum of 8 triangular numbers"},
    "A000122": {"type": "theta", "name": "Jacobi theta_3"},
    "A004011": {"type": "lattice_theta", "name": "D_4 lattice theta"},
    "A008408": {"type": "lattice_theta", "name": "E_8 lattice theta"},
    "A004027": {"type": "lattice_theta", "name": "Leech lattice theta"},
}

# Group into broader partitions for enrichment analysis
PARTITION_MAP = {
    "monstrous": ["A000521", "A007191", "A014708", "A007246", "A007267"],
    "modular": ["A000594", "A006352", "A004009", "A013973", "A008410", "A013974", "A029829"],
    "mock_theta": ["A045488", "A001488"],
    "umbral_M24": ["A053250"],
    "theta_lattice": ["A000118", "A008443", "A000122", "A004011", "A008408", "A004027"],
}

# Reverse map: core_id -> partition name
CORE_TO_PARTITION = {}
for pname, cores in PARTITION_MAP.items():
    for c in cores:
        CORE_TO_PARTITION[c] = pname


# ---------------------------------------------------------------------------
# Load OEIS
# ---------------------------------------------------------------------------
def load_oeis():
    """Load OEIS sequences into {id: terms_list}."""
    cache = {}
    src = OEIS_STRIPPED_TXT if OEIS_STRIPPED_TXT.exists() else OEIS_STRIPPED_GZ
    if not src.exists():
        print(f"  WARNING: {src} not found")
        return cache
    opener = gzip.open if str(src).endswith('.gz') else open
    mode = "rt" if str(src).endswith('.gz') else "r"
    print(f"  Loading OEIS from {src.name}...")
    with opener(src, mode, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) < 3:
                continue
            sid = parts[0].strip()
            terms = []
            for t in parts[1:]:
                t = t.strip()
                if t:
                    try:
                        terms.append(int(t))
                    except ValueError:
                        pass
            if terms:
                cache[sid] = terms
    print(f"  Loaded {len(cache):,} sequences")
    return cache


# ---------------------------------------------------------------------------
# Load all 307 bridges from C09
# ---------------------------------------------------------------------------
def load_bridges():
    """Load existing bridges (from oeis_results) and new bridges (from expansion_results).
    Returns list of dicts: [{core, match, partition}, ...]
    """
    bridges = []
    seen = set()

    # Existing bridges from moonshine_oeis_results.json
    if OEIS_RESULTS.exists():
        with open(OEIS_RESULTS, "r") as f:
            oeis_data = json.load(f)
        for b in oeis_data.get("coefficient_bridges", []):
            core = b["core"]
            match = b["match"]
            key = (core, match)
            if key not in seen:
                seen.add(key)
                bridges.append({
                    "core": core,
                    "match": match,
                    "partition": CORE_TO_PARTITION.get(core, "unknown"),
                })

    # New bridges from moonshine_expansion_results.json
    if EXPANSION_RESULTS.exists():
        with open(EXPANSION_RESULTS, "r") as f:
            exp_data = json.load(f)
        for b in exp_data.get("top_new_bridges", []):
            core = b["core"]
            match = b["match"]
            key = (core, match)
            if key not in seen:
                seen.add(key)
                bridges.append({
                    "core": core,
                    "match": match,
                    "partition": CORE_TO_PARTITION.get(core, "unknown"),
                })

    print(f"  Loaded {len(bridges)} unique bridges")
    return bridges


# ---------------------------------------------------------------------------
# Fingerprint and enrichment
# ---------------------------------------------------------------------------
def fingerprint(terms, p, fp_len=FP_LEN):
    """Compute mod-p fingerprint of first fp_len terms (using abs for negatives)."""
    if len(terms) < fp_len:
        return None
    return tuple(t % p for t in terms[:fp_len])


def compute_within_group_match_rate(seq_ids, oeis_data, p):
    """Compute fraction of within-group pairs sharing exact mod-p fingerprint."""
    fps = {}
    for sid in seq_ids:
        if sid in oeis_data and len(oeis_data[sid]) >= FP_LEN:
            fp = fingerprint(oeis_data[sid], p)
            if fp is not None:
                fps[sid] = fp
    sids = list(fps.keys())
    if len(sids) < 2:
        return 0.0, 0
    matches = 0
    total = 0
    for i in range(len(sids)):
        for j in range(i + 1, len(sids)):
            total += 1
            if fps[sids[i]] == fps[sids[j]]:
                matches += 1
    return matches / total if total > 0 else 0.0, total


def compute_random_match_rate(oeis_data, p, n_pairs=N_RANDOM_PAIRS):
    """Compute exact match rate for random OEIS pairs."""
    all_ids = [s for s in oeis_data if len(oeis_data[s]) >= FP_LEN]
    matches = 0
    tested = 0
    for _ in range(n_pairs):
        a, b = random.sample(all_ids, 2)
        fp_a = fingerprint(oeis_data[a], p)
        fp_b = fingerprint(oeis_data[b], p)
        if fp_a is not None and fp_b is not None:
            tested += 1
            if fp_a == fp_b:
                matches += 1
    return matches / tested if tested > 0 else 0.0, tested


def compute_moonshine_vs_random_rate(moonshine_ids, all_ids, oeis_data, p, n_pairs=N_RANDOM_PAIRS):
    """Compute match rate: moonshine sequence vs random OEIS sequence."""
    moon_valid = [s for s in moonshine_ids if s in oeis_data and len(oeis_data[s]) >= FP_LEN]
    rand_valid = [s for s in all_ids if s in oeis_data and len(oeis_data[s]) >= FP_LEN]
    if not moon_valid or not rand_valid:
        return 0.0, 0
    matches = 0
    tested = 0
    for _ in range(n_pairs):
        a = random.choice(moon_valid)
        b = random.choice(rand_valid)
        fp_a = fingerprint(oeis_data[a], p)
        fp_b = fingerprint(oeis_data[b], p)
        if fp_a is not None and fp_b is not None:
            tested += 1
            if fp_a == fp_b:
                matches += 1
    return matches / tested if tested > 0 else 0.0, tested


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    print("=" * 70)
    print("R3-7: Universal Scaling Law on Moonshine Bridges")
    print("=" * 70)

    # 1. Load data
    print("\n[1] Loading data...")
    oeis_data = load_oeis()
    bridges = load_bridges()

    if not oeis_data or not bridges:
        print("ERROR: Missing data, cannot proceed")
        sys.exit(1)

    # 2. Partition bridges by type
    print("\n[2] Partitioning bridges by moonshine type...")
    partitions = defaultdict(list)
    for b in bridges:
        partitions[b["partition"]].append(b)

    # Collect unique match sequences per partition
    partition_seqs = {}
    for pname, blist in partitions.items():
        seqs = set()
        for b in blist:
            seqs.add(b["match"])
            seqs.add(b["core"])
        partition_seqs[pname] = list(seqs)

    for pname in sorted(partitions.keys()):
        print(f"  {pname}: {len(partitions[pname])} bridges, {len(partition_seqs[pname])} unique sequences")

    # All moonshine-connected sequences (union)
    all_moonshine_seqs = set()
    for b in bridges:
        all_moonshine_seqs.add(b["match"])
        all_moonshine_seqs.add(b["core"])
    all_moonshine_list = list(all_moonshine_seqs)
    print(f"  TOTAL moonshine-connected: {len(all_moonshine_list)} unique sequences")

    # 3. Compute random baseline
    print("\n[3] Computing random baseline match rates...")
    random_rates = {}
    for p in PRIMES:
        rate, n = compute_random_match_rate(oeis_data, p)
        random_rates[p] = rate
        print(f"  mod-{p}: random match rate = {rate:.6f} ({n} pairs tested)")

    # 4. Compute enrichment per partition
    print("\n[4] Computing enrichment by partition...")
    results_by_partition = {}
    for pname in sorted(partitions.keys()):
        seqs = partition_seqs[pname]
        print(f"\n  --- {pname} ({len(seqs)} sequences) ---")
        partition_result = {"n_bridges": len(partitions[pname]), "n_sequences": len(seqs), "primes": {}}
        for p in PRIMES:
            within_rate, n_pairs = compute_within_group_match_rate(seqs, oeis_data, p)
            baseline = random_rates[p]
            enrichment = within_rate / baseline if baseline > 0 else float('inf')
            partition_result["primes"][str(p)] = {
                "within_rate": round(within_rate, 6),
                "random_rate": round(baseline, 6),
                "enrichment": round(enrichment, 2),
                "n_pairs": n_pairs,
            }
            print(f"    mod-{p}: within={within_rate:.6f}, random={baseline:.6f}, enrichment={enrichment:.1f}x ({n_pairs} pairs)")
        results_by_partition[pname] = partition_result

    # 5. Compute "moonshine premium": all moonshine seqs vs random OEIS
    print("\n[5] Computing moonshine premium (all moonshine vs random)...")
    moonshine_premium = {}
    for p in PRIMES:
        within_rate, n_pairs = compute_within_group_match_rate(all_moonshine_list, oeis_data, p)
        baseline = random_rates[p]
        enrichment = within_rate / baseline if baseline > 0 else float('inf')
        moonshine_premium[str(p)] = {
            "within_rate": round(within_rate, 6),
            "random_rate": round(baseline, 6),
            "enrichment": round(enrichment, 2),
            "n_pairs": n_pairs,
        }
        print(f"  mod-{p}: within={within_rate:.6f}, random={baseline:.6f}, enrichment={enrichment:.1f}x ({n_pairs} pairs)")

    # Also compute cross-match: moonshine vs random OEIS sequences
    print("\n  Cross-match: moonshine seq vs random OEIS seq...")
    moonshine_cross = {}
    all_ids = list(oeis_data.keys())
    for p in PRIMES:
        cross_rate, n_tested = compute_moonshine_vs_random_rate(
            all_moonshine_list, all_ids, oeis_data, p
        )
        baseline = random_rates[p]
        enrichment = cross_rate / baseline if baseline > 0 else float('inf')
        moonshine_cross[str(p)] = {
            "cross_rate": round(cross_rate, 6),
            "random_rate": round(baseline, 6),
            "enrichment": round(enrichment, 2),
            "n_tested": n_tested,
        }
        print(f"  mod-{p}: cross={cross_rate:.6f}, random={baseline:.6f}, enrichment={enrichment:.1f}x")

    # 6. M24->EC Hecke matches specifically
    print("\n[6] M24 -> EC Hecke match enrichment...")
    m24_ec_result = {}
    if EXPANSION_RESULTS.exists():
        with open(EXPANSION_RESULTS, "r") as f:
            exp_data = json.load(f)
        hecke_matches = exp_data.get("hecke_matches", [])
        print(f"  Found {len(hecke_matches)} Hecke matches")

        # The Hecke matches are M24 (A053250) -> modular forms
        # Collect the OEIS sequences that bridge to A053250
        m24_bridges = [b for b in bridges if b["core"] == "A053250"]
        m24_match_seqs = list(set(b["match"] for b in m24_bridges))
        print(f"  M24 bridge sequences: {len(m24_match_seqs)}")

        # Get the Hecke form levels for reference
        hecke_levels = [h["mf_level"] for h in hecke_matches]
        hecke_labels = [h["mf_label"] for h in hecke_matches]
        print(f"  Hecke levels: {hecke_levels}")
        print(f"  Hecke labels: {hecke_labels}")

        # Compute enrichment for M24 bridge sequences
        for p in PRIMES:
            within_rate, n_pairs = compute_within_group_match_rate(m24_match_seqs, oeis_data, p)
            baseline = random_rates[p]
            enrichment = within_rate / baseline if baseline > 0 else float('inf')
            m24_ec_result[str(p)] = {
                "within_rate": round(within_rate, 6),
                "random_rate": round(baseline, 6),
                "enrichment": round(enrichment, 2),
                "n_pairs": n_pairs,
            }
            print(f"  mod-{p}: M24 bridges within={within_rate:.6f}, enrichment={enrichment:.1f}x ({n_pairs} pairs)")

        m24_ec_result["hecke_levels"] = hecke_levels
        m24_ec_result["hecke_labels"] = hecke_labels
        m24_ec_result["n_m24_bridges"] = len(m24_bridges)
        m24_ec_result["n_m24_match_seqs"] = len(m24_match_seqs)

    # 7. Summary and interpretation
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    # Collect mean enrichment per partition (exclude inf values from means)
    summary_table = {}
    for pname, res in results_by_partition.items():
        enrichments = [res["primes"][str(p)]["enrichment"] for p in PRIMES]
        finite_e = [e for e in enrichments if np.isfinite(e)]
        mean_e = np.mean(finite_e) if finite_e else 0.0
        std_e = np.std(finite_e) if finite_e else 0.0
        summary_table[pname] = {
            "mean_enrichment": round(float(mean_e), 2),
            "std_enrichment": round(float(std_e), 2),
            "enrichments_by_prime": {str(p): res["primes"][str(p)]["enrichment"] for p in PRIMES},
            "n_bridges": res["n_bridges"],
            "n_sequences": res["n_sequences"],
        }
        print(f"  {pname:20s}: mean enrichment = {mean_e:.1f}x +/- {std_e:.1f} (n={res['n_bridges']} bridges)")
        for p in PRIMES:
            e = res["primes"][str(p)]["enrichment"]
            print(f"    mod-{p:2d}: {e:.1f}x")

    # Moonshine premium summary
    moon_enrichments = [moonshine_premium[str(p)]["enrichment"] for p in PRIMES]
    finite_moon = [e for e in moon_enrichments if np.isfinite(e)]
    moon_mean = np.mean(finite_moon) if finite_moon else 0.0
    moon_std = np.std(finite_moon) if finite_moon else 0.0
    print(f"\n  MOONSHINE PREMIUM (all 307 bridges pooled):")
    print(f"    Mean enrichment = {moon_mean:.1f}x +/- {moon_std:.1f}")
    for p in PRIMES:
        e = moonshine_premium[str(p)]["enrichment"]
        print(f"    mod-{p:2d}: {e:.1f}x")

    # Cross-match summary
    cross_enrichments = [moonshine_cross[str(p)]["enrichment"] for p in PRIMES]
    finite_cross = [e for e in cross_enrichments if np.isfinite(e)]
    cross_mean = np.mean(finite_cross) if finite_cross else 0.0
    print(f"\n  MOONSHINE CROSS (moonshine vs random OEIS):")
    print(f"    Mean enrichment = {cross_mean:.1f}x")
    for p in PRIMES:
        e = moonshine_cross[str(p)]["enrichment"]
        print(f"    mod-{p:2d}: {e:.1f}x")

    # M24->EC
    if m24_ec_result:
        m24_enrichments = [m24_ec_result[str(p)]["enrichment"] for p in PRIMES]
        finite_m24 = [e for e in m24_enrichments if np.isfinite(e)]
        m24_mean = np.mean(finite_m24) if finite_m24 else 0.0
        print(f"\n  M24->EC HECKE MATCH ENRICHMENT:")
        print(f"    Mean enrichment = {m24_mean:.1f}x")
        for p in PRIMES:
            e = m24_ec_result[str(p)]["enrichment"]
            print(f"    mod-{p:2d}: {e:.1f}x")
        # Compare to moonshine average
        ratio = m24_mean / moon_mean if moon_mean > 0 else float('inf')
        print(f"    Ratio to moonshine average: {ratio:.2f}x")

    # Flatness test: is enrichment flat across primes (like the universal ~8x)?
    print(f"\n  FLATNESS TEST (is enrichment independent of prime?):")
    for pname, s in summary_table.items():
        cv = s["std_enrichment"] / s["mean_enrichment"] if s["mean_enrichment"] > 0 else float('inf')
        flat = "FLAT" if cv < 0.3 else "NOT FLAT"
        print(f"    {pname:20s}: CV = {cv:.2f} -> {flat}")

    # Interpretation
    print(f"\n  INTERPRETATION:")
    print(f"    Universal baseline: ~8x flat enrichment")
    print(f"    Moonshine pooled:   {moon_mean:.1f}x")
    if moon_mean > 12:
        print(f"    -> Moonshine is DEEPER than generic algebraic families")
    elif moon_mean > 5:
        print(f"    -> Moonshine matches the universal algebraic depth")
    else:
        print(f"    -> Moonshine is SHALLOWER than generic algebraic families")

    # Check if partitions differ significantly
    partition_means = [s["mean_enrichment"] for s in summary_table.values() if np.isfinite(s["mean_enrichment"])]
    if len(partition_means) >= 2:
        spread = max(partition_means) - min(partition_means)
        overall_mean = np.mean(partition_means)
        if spread > 0.5 * overall_mean:
            print(f"    -> Partitions show DIFFERENT enrichment levels (spread={spread:.1f})")
            print(f"       The two sides of moonshine have different algebraic depth")
        else:
            print(f"    -> Partitions show SIMILAR enrichment (spread={spread:.1f})")
            print(f"       Moonshine algebraic depth is uniform across types")

    # 8. Save results
    output = {
        "summary": {
            "n_bridges": len(bridges),
            "n_unique_sequences": len(all_moonshine_list),
            "universal_baseline": "~8x flat enrichment",
            "primes_tested": PRIMES,
            "fp_length": FP_LEN,
            "random_pairs_per_test": N_RANDOM_PAIRS,
        },
        "random_baseline": {str(p): round(random_rates[p], 6) for p in PRIMES},
        "enrichment_by_partition": summary_table,
        "moonshine_premium": {
            "within_group": moonshine_premium,
            "cross_match": moonshine_cross,
            "mean_within_enrichment": round(float(moon_mean), 2),
            "mean_cross_enrichment": round(float(cross_mean), 2),
        },
        "m24_ec_hecke": m24_ec_result,
        "flatness_test": {},
        "interpretation": {},
    }

    # Flatness
    for pname, s in summary_table.items():
        cv = s["std_enrichment"] / s["mean_enrichment"] if s["mean_enrichment"] > 0 else float('inf')
        output["flatness_test"][pname] = {
            "coefficient_of_variation": round(cv, 3),
            "is_flat": cv < 0.3,
        }

    # Interpretation
    safe_moon_mean = float(moon_mean) if np.isfinite(moon_mean) else 0.0
    output["interpretation"] = {
        "moonshine_vs_universal": (
            "deeper" if safe_moon_mean > 12 else
            "matches" if safe_moon_mean > 5 else
            "shallower"
        ),
        "partition_uniformity": (
            "different" if len(partition_means) >= 2 and (max(partition_means) - min(partition_means)) > 0.5 * np.mean(partition_means)
            else "uniform"
        ),
        "moonshine_premium_magnitude": round(safe_moon_mean, 2),
    }

    with open(OUT_FILE, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Results saved to {OUT_FILE}")

    elapsed = time.time() - t0
    print(f"\n  Done in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
