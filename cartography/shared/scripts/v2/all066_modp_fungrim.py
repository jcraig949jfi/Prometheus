"""
ALL-066: Mod-p Fingerprint vs Fungrim
========================================
For each Fungrim formula in the index, extract its "mod-p fingerprint":
evaluate the formula's numerical constant (if present) modulo small primes.
Do Fungrim formulas cluster by mod-p fingerprint?
Does the fingerprint correlate with the operadic skeleton module?
"""
import json, time, math
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

V2 = Path(__file__).resolve().parent
FUNGRIM = V2.parents[3] / "cartography" / "fungrim" / "data" / "fungrim_index.json"
OUT = V2 / "all066_modp_fungrim_results.json"

# Well-known mathematical constants with approximate values
KNOWN_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
    "euler_gamma": 0.5772156649,
    "golden_ratio": (1 + math.sqrt(5)) / 2,
    "catalan": 0.9159655941,
    "sqrt2": math.sqrt(2),
    "sqrt3": math.sqrt(3),
    "ln2": math.log(2),
    "ln10": math.log(10),
    "apery": 1.2020569031,
}

def mod_p_fingerprint(val, primes=[2, 3, 5, 7, 11]):
    """Approximate mod-p fingerprint of a real number by rounding."""
    if val is None or not math.isfinite(val): return None
    # Use the first 6 decimal digits as an integer
    digits = int(abs(val) * 1000000) % (2*3*5*7*11*13)
    return tuple(digits % p for p in primes)

def main():
    t0 = time.time()
    print("=== ALL-066: Mod-p Fingerprint vs Fungrim ===\n")

    with open(FUNGRIM) as f:
        index = json.load(f)

    # Examine structure
    if isinstance(index, dict):
        entries = list(index.values()) if not isinstance(list(index.values())[0], str) else [index]
        if isinstance(list(index.values())[0], dict):
            entries = list(index.values())
        elif isinstance(list(index.values())[0], list):
            entries = []
            for v in index.values():
                if isinstance(v, list):
                    entries.extend(v)
        print(f"  Index type: dict with {len(index)} keys")
        print(f"  Sample keys: {list(index.keys())[:5]}")
    elif isinstance(index, list):
        entries = index
        print(f"  Index type: list with {len(entries)} entries")

    # Try to extract module and formula info
    modules = Counter()
    formulas_with_constants = []

    for entry in entries[:10000] if isinstance(entries, list) else []:
        if isinstance(entry, dict):
            module = entry.get("module", entry.get("topic", entry.get("category", "unknown")))
            modules[module] += 1
            # Look for numerical values
            for key in ["value", "numerical_value", "constant", "rhs"]:
                val = entry.get(key)
                if isinstance(val, (int, float)):
                    formulas_with_constants.append({"module": module, "value": val})
                    break

    # If entries are just strings or IDs, use the index keys as modules
    if not modules and isinstance(index, dict):
        for key, val in index.items():
            if isinstance(val, list):
                modules[key] = len(val)
            elif isinstance(val, dict):
                modules[key] = 1

    print(f"\n  {len(modules)} modules found")
    print(f"  Top modules: {modules.most_common(10)}")
    print(f"  Formulas with numerical constants: {len(formulas_with_constants)}")

    # Fingerprint known constants
    print("\n  Known constant mod-p fingerprints:")
    const_fps = {}
    for name, val in KNOWN_CONSTANTS.items():
        fp = mod_p_fingerprint(val)
        const_fps[name] = fp
        print(f"    {name} ({val:.6f}): {fp}")

    # Fingerprint collisions among constants
    fp_groups = defaultdict(list)
    for name, fp in const_fps.items():
        fp_groups[fp].append(name)
    collisions = {str(fp): names for fp, names in fp_groups.items() if len(names) > 1}
    print(f"\n  Fingerprint collisions: {len(collisions)}")
    for fp, names in collisions.items():
        print(f"    {fp}: {names}")

    # If we have formulas with constants, fingerprint them
    if formulas_with_constants:
        print(f"\n  Fingerprinting {len(formulas_with_constants)} formulas...")
        fp_by_module = defaultdict(Counter)
        for fc in formulas_with_constants:
            fp = mod_p_fingerprint(fc["value"])
            if fp:
                fp_by_module[fc["module"]][fp] += 1

        # Entropy per module
        module_entropy = {}
        for mod, fp_counts in fp_by_module.items():
            total = sum(fp_counts.values())
            if total < 3: continue
            probs = np.array(list(fp_counts.values())) / total
            H = float(-np.sum(probs * np.log2(probs)))
            module_entropy[mod] = round(H, 4)

        if module_entropy:
            sorted_ent = sorted(module_entropy.items(), key=lambda x: x[1])
            print(f"\n  Module entropy (low = concentrated fingerprints):")
            for mod, H in sorted_ent[:10]:
                print(f"    {mod}: H={H:.4f}")

    # Module-level analysis from index structure
    print("\n  Module size distribution:")
    sizes = sorted(modules.values(), reverse=True)
    print(f"    Total formulas: {sum(sizes)}")
    print(f"    Modules: {len(sizes)}")
    print(f"    Largest: {sizes[0] if sizes else 0}")
    print(f"    Median: {sizes[len(sizes)//2] if sizes else 0}")

    # Zipf fit
    if len(sizes) >= 5:
        from scipy import stats as sp_stats
        rank = np.arange(1, len(sizes)+1, dtype=float)
        log_r = np.log(rank)
        log_s = np.log(np.array(sizes, dtype=float) + 1)
        slope, _, r, _, _ = sp_stats.linregress(log_r, log_s)
        zipf_alpha = -slope
        print(f"    Zipf α = {zipf_alpha:.3f} (R²={r**2:.4f})")
    else:
        zipf_alpha = None

    elapsed = time.time() - t0
    output = {
        "challenge": "ALL-066", "title": "Mod-p Fingerprint vs Fungrim",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_modules": len(modules),
        "n_formulas": sum(modules.values()),
        "n_with_constants": len(formulas_with_constants),
        "known_constant_fingerprints": {k: list(v) for k, v in const_fps.items()},
        "fingerprint_collisions": collisions,
        "module_distribution": {
            "top_modules": dict(modules.most_common(20)),
            "zipf_alpha": round(zipf_alpha, 4) if zipf_alpha else None,
        },
        "assessment": None,
    }

    if formulas_with_constants:
        output["assessment"] = f"FINGERPRINTED: {len(formulas_with_constants)} formulas have mod-p signatures. {len(collisions)} constant collisions detected. Module Zipf α={zipf_alpha:.2f}" if zipf_alpha else "FINGERPRINTED but no Zipf fit"
    else:
        output["assessment"] = f"INDEX ONLY: {sum(modules.values())} formulas across {len(modules)} modules. No numerical constants extractable from index. Zipf α={zipf_alpha:.2f}" if zipf_alpha else "INDEX ONLY"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
