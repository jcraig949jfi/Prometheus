"""
M27: Algebraic DNA fragmentation
===================================
From algebraic_dna_fungrim_results.json, analyse how many unique
operadic "DNA fingerprints" exist per Fungrim module. The fragmentation
ratio = unique_fingerprints / total_formulas.

High fragmentation = each formula is structurally unique (no compression).
Low fragmentation = many formulas share operadic structure (high compression).

Also: which modules have the most shared DNA? These are the structurally
richest — candidates for cross-domain bridges.
"""
import json, time
import numpy as np
from pathlib import Path
from collections import Counter

V2 = Path(__file__).resolve().parent
DNA = V2 / "algebraic_dna_fungrim_results.json"
OUT = V2 / "m27_algebraic_dna_results.json"

def main():
    t0 = time.time()
    print("=== M27: Algebraic DNA fragmentation ===\n")

    with open(DNA) as f:
        data = json.load(f)

    print(f"  Keys: {list(data.keys())[:15]}")

    # Extract per-module data
    modules = data.get("modules", data.get("per_module", {}))
    if not modules:
        # Try flat structure
        if "total_formulas" in data:
            print(f"  Total formulas: {data['total_formulas']}")
            print(f"  Unique fingerprints: {data.get('unique_fingerprints', 'N/A')}")

    # Try to get fingerprint data
    fingerprints = data.get("fingerprints", data.get("skeleton_hashes", {}))
    hash_counts = data.get("hash_frequency", data.get("skeleton_frequency", {}))

    if isinstance(modules, dict):
        print(f"\n  Analysing {len(modules)} modules...")
        module_stats = {}
        for mod_name, mod_data in modules.items():
            if isinstance(mod_data, dict):
                n_formulas = mod_data.get("n_formulas", mod_data.get("count", 0))
                n_unique = mod_data.get("n_unique_hashes", mod_data.get("unique", 0))
                frag = n_unique / n_formulas if n_formulas > 0 else 0
                module_stats[mod_name] = {
                    "n_formulas": n_formulas,
                    "n_unique_hashes": n_unique,
                    "fragmentation": round(frag, 4),
                    "compression": round(1 - frag, 4),
                }
        # Sort by compression (low fragmentation = high compression)
        sorted_mods = sorted(module_stats.items(), key=lambda x: x[1]["compression"], reverse=True)
        print("\n  Top 15 most compressed (shared DNA) modules:")
        for mod, stats in sorted_mods[:15]:
            print(f"    {mod}: {stats['n_unique_hashes']}/{stats['n_formulas']} unique "
                  f"(compression={stats['compression']:.0%})")

        # Summary statistics
        frags = [s["fragmentation"] for s in module_stats.values() if s["n_formulas"] > 0]
        mean_frag = float(np.mean(frags)) if frags else 0
        print(f"\n  Mean fragmentation: {mean_frag:.4f}")
        print(f"  Mean compression: {1-mean_frag:.4f}")
    else:
        module_stats = {}
        mean_frag = 0

    # Global DNA analysis
    total_formulas = data.get("total_formulas", sum(s.get("n_formulas", 0) for s in modules.values()) if isinstance(modules, dict) else 0)
    total_unique = data.get("unique_fingerprints", data.get("unique_hashes", 0))

    if total_unique == 0 and isinstance(hash_counts, dict):
        total_unique = len(hash_counts)
    global_frag = total_unique / total_formulas if total_formulas > 0 else 0

    print(f"\n  Global: {total_unique} unique / {total_formulas} total = {global_frag:.4f} fragmentation")

    # Hash frequency distribution (power law?)
    if isinstance(hash_counts, dict) and hash_counts:
        freqs = sorted([int(v) if isinstance(v, str) else v for v in hash_counts.values()], reverse=True)
        arr = np.array(freqs, dtype=float)
        # Fit power law to frequency distribution
        if len(arr) >= 10:
            rank = np.arange(1, len(arr) + 1, dtype=float)
            # Zipf fit: freq ~ rank^(-alpha)
            log_rank = np.log(rank[:min(100, len(rank))])
            log_freq = np.log(arr[:min(100, len(arr))])
            from scipy import stats as sp_stats
            slope, _, r, _, _ = sp_stats.linregress(log_rank, log_freq)
            zipf_alpha = -slope
            print(f"\n  Zipf law: α={zipf_alpha:.3f} (R²={r**2:.4f})")
        else:
            zipf_alpha = None
    else:
        zipf_alpha = None

    elapsed = time.time() - t0
    output = {
        "probe": "M27", "title": "Algebraic DNA fragmentation",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "total_formulas": total_formulas,
        "total_unique_hashes": total_unique,
        "global_fragmentation": round(global_frag, 6),
        "global_compression": round(1 - global_frag, 6),
        "per_module_top15": {k: v for k, v in sorted_mods[:15]} if module_stats else {},
        "mean_fragmentation": round(mean_frag, 4),
        "zipf_alpha": round(zipf_alpha, 4) if zipf_alpha else None,
        "assessment": None,
    }

    if global_frag < 0.3:
        output["assessment"] = f"HIGH COMPRESSION: {1-global_frag:.0%} of formulas share DNA — operadic structure is highly reused"
    elif global_frag < 0.7:
        output["assessment"] = f"MODERATE: {global_frag:.0%} fragmentation — mix of shared and unique structures"
    else:
        output["assessment"] = f"HIGH FRAGMENTATION: {global_frag:.0%} — each formula is structurally distinct, little reuse"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
