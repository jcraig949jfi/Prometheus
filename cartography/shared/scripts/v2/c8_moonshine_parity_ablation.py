"""
Challenge 8: Moonshine Parity After 2-Adic Ablation
======================================================
M46 found null parity signal. But 2 is the anomalous prime.
Ablate Monstrous/modular (the p=2 drivers), keep only Mock Theta +
Umbral M24. Does 2-adic noise suppress a hidden parity anomaly?
"""
import json, time, math
import numpy as np
from pathlib import Path
from collections import Counter

V2 = Path(__file__).resolve().parent
OEIS_PATH = V2.parents[3] / "cartography" / "oeis" / "data" / "stripped_new.txt"
MOON_OEIS = V2 / "moonshine_oeis_results.json"
MOON_SCALE = V2 / "moonshine_scaling_results.json"
OUT = V2 / "c8_parity_ablation_results.json"

# Moonshine OEIS sequences by partition
MOONSHINE_SEQS = {
    "monstrous": ["A000521","A007191","A014708","A007246","A007267","A045478","A045479",
                  "A045480","A101558","A004009","A006352","A005928","A008615"],
    "mock_theta": ["A000025","A000039","A003114","A006304","A000122","A002448","A000609",
                   "A053250","A000118","A008443","A029750","A078124"],
    "umbral_M24": ["A006571","A006352","A000594","A004009","A000727","A000735",
                   "A000731","A002107","A006571"],
    "theta_lattice": ["A004011","A004018","A004015","A004016","A005872","A005884",
                      "A008444","A000118","A004025"],
    "modular_forms": ["A000594","A000727","A000735","A000731","A000144","A002107",
                      "A006352","A004009","A005928"],
}

def load_oeis_sequence(sid, oeis_data):
    return oeis_data.get(sid, [])

def parity_stats(terms):
    if not terms or len(terms) < 5: return None
    nonzero = [t for t in terms if t != 0]
    if len(nonzero) < 5: return None
    even = sum(1 for t in nonzero if t % 2 == 0)
    odd = len(nonzero) - even
    even_frac = even / len(nonzero)
    bias = abs(even_frac - 0.5)
    return {"even_frac": round(even_frac, 4), "odd_frac": round(1-even_frac, 4),
            "bias": round(bias, 4), "n": len(nonzero)}

def main():
    t0 = time.time()
    print("=== C8: Moonshine Parity After 2-Adic Ablation ===\n")

    # Load OEIS
    print("[1] Loading OEIS sequences...")
    oeis = {}
    with open(OEIS_PATH, 'r', errors='ignore') as f:
        for line in f:
            if not line.strip() or not line.startswith('A'): continue
            parts = line.split(',')
            sid = parts[0].strip().split()[0]
            terms = []
            for t in parts[1:]:
                t = t.strip()
                if t:
                    try: terms.append(int(t))
                    except: pass
            if terms: oeis[sid] = terms[:100]
    print(f"  {len(oeis)} OEIS sequences loaded")

    # Full moonshine parity
    print("\n[2] Full moonshine parity...")
    all_moon_sids = set()
    for sids in MOONSHINE_SEQS.values():
        all_moon_sids.update(sids)

    full_parities = {}
    for sid in all_moon_sids:
        terms = oeis.get(sid, [])
        ps = parity_stats(terms)
        if ps: full_parities[sid] = ps

    if full_parities:
        all_biases = [p["bias"] for p in full_parities.values()]
        all_even = [p["even_frac"] for p in full_parities.values()]
        print(f"  {len(full_parities)} moonshine sequences with parity data")
        print(f"  Mean even fraction: {np.mean(all_even):.4f}")
        print(f"  Mean bias: {np.mean(all_biases):.4f}")

    # Partition-specific parity
    print("\n[3] Parity by partition:")
    partition_parity = {}
    for partition, sids in MOONSHINE_SEQS.items():
        parities = []
        for sid in sids:
            terms = oeis.get(sid, [])
            ps = parity_stats(terms)
            if ps: parities.append(ps)
        if parities:
            biases = [p["bias"] for p in parities]
            evens = [p["even_frac"] for p in parities]
            partition_parity[partition] = {
                "n_seqs": len(parities),
                "mean_even": round(float(np.mean(evens)), 4),
                "mean_bias": round(float(np.mean(biases)), 4),
                "max_bias": round(float(max(biases)), 4),
                "individual": parities,
            }
            print(f"  {partition}: n={len(parities)}, mean_even={np.mean(evens):.3f}, "
                  f"mean_bias={np.mean(biases):.4f}, max_bias={max(biases):.4f}")

    # ABLATION: Remove monstrous + modular_forms (the 2-adic drivers)
    print("\n[4] 2-ADIC ABLATION: removing monstrous + modular_forms...")
    ablated_sids = set()
    for partition in ["mock_theta", "umbral_M24", "theta_lattice"]:
        ablated_sids.update(MOONSHINE_SEQS.get(partition, []))
    # Remove any that are also in monstrous/modular
    keep_sids = ablated_sids - set(MOONSHINE_SEQS["monstrous"]) - set(MOONSHINE_SEQS["modular_forms"])

    ablated_parities = {sid: full_parities[sid] for sid in keep_sids if sid in full_parities}
    if ablated_parities:
        abl_biases = [p["bias"] for p in ablated_parities.values()]
        abl_even = [p["even_frac"] for p in ablated_parities.values()]
        print(f"  Ablated set: {len(ablated_parities)} sequences")
        print(f"  Mean even fraction: {np.mean(abl_even):.4f} (full: {np.mean(all_even):.4f})")
        print(f"  Mean bias: {np.mean(abl_biases):.4f} (full: {np.mean(all_biases):.4f})")
        print(f"  Max bias: {max(abl_biases):.4f}")

        # Compare to random OEIS sample
        np.random.seed(42)
        random_sids = list(oeis.keys())
        np.random.shuffle(random_sids)
        random_parities = []
        for sid in random_sids[:2000]:
            ps = parity_stats(oeis[sid])
            if ps: random_parities.append(ps)
        rand_biases = [p["bias"] for p in random_parities]
        rand_even = [p["even_frac"] for p in random_parities]
        print(f"\n  Random baseline ({len(random_parities)} seqs):")
        print(f"  Mean even: {np.mean(rand_even):.4f}, Mean bias: {np.mean(rand_biases):.4f}")

        # Statistical test
        from scipy import stats
        if len(abl_biases) >= 3:
            stat, p_val = stats.mannwhitneyu(abl_biases, rand_biases, alternative='greater')
            print(f"\n  MWU test (ablated bias > random): U={stat:.0f}, p={p_val:.4e}")
        else:
            p_val = 1.0

        # Show most biased ablated sequences
        print("\n  Most biased (ablated set):")
        for sid, ps in sorted(ablated_parities.items(), key=lambda x: -x[1]["bias"])[:10]:
            partition = [p for p, sids in MOONSHINE_SEQS.items() if sid in sids]
            print(f"    {sid} ({partition}): even={ps['even_frac']:.2f}, bias={ps['bias']:.4f}")
    else:
        p_val = 1.0; abl_biases = []; abl_even = []

    elapsed = time.time() - t0
    output = {
        "challenge": "C8", "title": "Moonshine Parity After 2-Adic Ablation",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "full_moonshine": {"n": len(full_parities),
                          "mean_bias": round(float(np.mean(all_biases)), 4) if all_biases else None,
                          "mean_even": round(float(np.mean(all_even)), 4) if all_even else None},
        "partition_parity": partition_parity,
        "ablated": {"n": len(ablated_parities),
                   "mean_bias": round(float(np.mean(abl_biases)), 4) if abl_biases else None,
                   "mean_even": round(float(np.mean(abl_even)), 4) if abl_even else None,
                   "mwu_pvalue": float(p_val)},
        "assessment": None,
    }

    if abl_biases and p_val < 0.05:
        output["assessment"] = (
            f"HIDDEN PARITY REVEALED: ablating 2-adic drivers exposes bias={np.mean(abl_biases):.4f} "
            f"(p={p_val:.4e}). The v₂ wall WAS suppressing a genuine parity anomaly in Mock Theta/Umbral.")
    elif abl_biases and p_val < 0.2:
        output["assessment"] = (
            f"MARGINAL SIGNAL: ablated bias={np.mean(abl_biases):.4f} (p={p_val:.3f}). "
            f"2-adic ablation slightly increases parity signal but remains non-significant.")
    else:
        output["assessment"] = (
            f"STILL NULL: ablated bias={np.mean(abl_biases):.4f} if ablated, p={p_val:.3f}. "
            f"The parity null is ROBUST to 2-adic ablation. Moonshine parity is genuinely unbiased.")

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
