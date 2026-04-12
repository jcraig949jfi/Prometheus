"""
Challenge 1: Adelic Survivors
================================
The adelic fibre decays as exp(-1.42k). By k=6, 99.1% are singletons.
But what are the ~0.9% that AREN'T? These "survivors" resist identification.
Does adelic resistance correlate with high algebraic symmetry (CM, high endo rank)?
"""
import json, time, math
import numpy as np
import duckdb
from pathlib import Path
from itertools import combinations
from collections import Counter, defaultdict

V2 = Path(__file__).resolve().parent
DB = V2.parents[3] / "charon" / "data" / "charon.duckdb"
OUT = V2 / "c1_adelic_survivors_results.json"

def sieve(limit):
    is_p = [True] * (limit + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_p[i]:
            for j in range(i*i, limit+1, i): is_p[j] = False
    return [i for i in range(2, limit+1) if is_p[i]]

def prime_factors(n):
    f = set(); d = 2
    while d*d <= n:
        while n % d == 0: f.add(d); n //= d
        d += 1
    if n > 1: f.add(n)
    return f

def main():
    t0 = time.time()
    print("=== Challenge 1: Adelic Survivors ===\n")

    con = duckdb.connect(str(DB), read_only=True)
    rows = con.execute("""
        SELECT lmfdb_label, level, ap_coeffs, is_cm
        FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND char_order = 1
        ORDER BY level
    """).fetchall()
    con.close()
    print(f"  {len(rows)} forms loaded")

    ap_primes = sieve(50)
    ELLS = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]  # Extended to 10 primes

    # Build residue tuples for ALL primes
    forms = []
    for label, level, ap_json, is_cm in rows:
        ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
        ap_vals = [x[0] if isinstance(x, list) else x for x in ap]
        bad = prime_factors(level)
        residues = {}
        for ell in ELLS:
            idx = ap_primes.index(ell) if ell in ap_primes else -1
            if idx >= 0 and idx < len(ap_vals) and ell not in bad:
                residues[ell] = ap_vals[idx] % ell
        forms.append({"label": label, "level": level, "is_cm": bool(is_cm),
                      "residues": residues, "n_good": len(residues)})

    # For k=6 primes, find forms that share the SAME residue tuple with at least one other
    print("\n  Finding survivors at k=6...")
    ELLS_6 = ELLS[:6]
    tuple_groups = defaultdict(list)
    for f in forms:
        tup = tuple(f["residues"].get(ell, -1) for ell in ELLS_6)
        if -1 not in tup:
            tuple_groups[tup].append(f)

    # Survivors = forms in groups of size > 1
    survivor_groups = {t: g for t, g in tuple_groups.items() if len(g) > 1}
    survivor_forms = [f for g in survivor_groups.values() for f in g]
    singleton_forms = [g[0] for g in tuple_groups.values() if len(g) == 1]

    n_valid = sum(len(g) for g in tuple_groups.values())
    n_survivors = len(survivor_forms)
    n_singletons = len(singleton_forms)
    print(f"  Valid forms (6 good primes): {n_valid}")
    print(f"  Singletons: {n_singletons} ({n_singletons/n_valid:.1%})")
    print(f"  Survivors: {n_survivors} ({n_survivors/n_valid:.1%})")
    print(f"  Survivor groups: {len(survivor_groups)}")

    # How many more primes do survivors need?
    print("\n  Resolving survivors with additional primes...")
    resolution_k = []
    for tup, group in survivor_groups.items():
        resolved = False
        for k_extra in range(1, 5):
            if k_extra + 6 > len(ELLS): break
            extra_ells = ELLS[6:6+k_extra]
            sub_tuples = defaultdict(list)
            for f in group:
                ext = tuple(f["residues"].get(ell, -1) for ell in extra_ells)
                if -1 not in ext:
                    sub_tuples[ext].append(f)
            max_size = max(len(g) for g in sub_tuples.values()) if sub_tuples else len(group)
            if max_size <= 1:
                resolution_k.append(6 + k_extra)
                resolved = True
                break
        if not resolved:
            resolution_k.append(11)  # Still unresolved

    print(f"  Resolution distribution:")
    for k_val, cnt in sorted(Counter(resolution_k).items()):
        print(f"    k={k_val}: {cnt} groups")

    # CM correlation
    cm_survivors = sum(1 for f in survivor_forms if f["is_cm"])
    cm_singletons = sum(1 for f in singleton_forms if f["is_cm"])
    cm_rate_surv = cm_survivors / len(survivor_forms) if survivor_forms else 0
    cm_rate_sing = cm_singletons / len(singleton_forms) if singleton_forms else 0
    print(f"\n  CM rate among survivors: {cm_rate_surv:.1%} ({cm_survivors}/{n_survivors})")
    print(f"  CM rate among singletons: {cm_rate_sing:.1%} ({cm_singletons}/{n_singletons})")
    cm_enrichment = cm_rate_surv / cm_rate_sing if cm_rate_sing > 0 else 0
    print(f"  CM enrichment in survivors: {cm_enrichment:.2f}x")

    # Level distribution of survivors vs singletons
    surv_levels = Counter(f["level"] for f in survivor_forms)
    sing_levels = Counter(f["level"] for f in singleton_forms)
    surv_mean_level = float(np.mean([f["level"] for f in survivor_forms])) if survivor_forms else 0
    sing_mean_level = float(np.mean([f["level"] for f in singleton_forms])) if singleton_forms else 0
    print(f"\n  Mean level: survivors={surv_mean_level:.0f}, singletons={sing_mean_level:.0f}")

    # Group size distribution
    group_sizes = [len(g) for g in survivor_groups.values()]
    print(f"\n  Survivor group sizes: {sorted(group_sizes, reverse=True)[:20]}")

    # Show specific survivor examples
    print("\n  Top survivor groups:")
    for tup, group in sorted(survivor_groups.items(), key=lambda x: -len(x[1]))[:10]:
        labels = [f["label"] for f in group]
        cms = sum(1 for f in group if f["is_cm"])
        levels = [f["level"] for f in group]
        print(f"    size={len(group)}, CM={cms}, levels={levels}, labels={labels[:3]}...")

    elapsed = time.time() - t0
    output = {
        "challenge": "C1", "title": "Adelic Survivors",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_forms": len(forms), "n_valid_k6": n_valid,
        "n_singletons": n_singletons, "n_survivors": n_survivors,
        "survivor_rate": round(n_survivors / n_valid, 6) if n_valid > 0 else 0,
        "n_survivor_groups": len(survivor_groups),
        "group_sizes": sorted(group_sizes, reverse=True),
        "resolution_distribution": dict(Counter(resolution_k)),
        "cm_enrichment": {
            "survivors_cm_rate": round(cm_rate_surv, 4),
            "singletons_cm_rate": round(cm_rate_sing, 4),
            "enrichment": round(cm_enrichment, 4),
        },
        "mean_level_survivors": round(surv_mean_level, 0),
        "mean_level_singletons": round(sing_mean_level, 0),
        "top_groups": [{"size": len(g), "labels": [f["label"] for f in g],
                       "cm_count": sum(1 for f in g if f["is_cm"]),
                       "levels": [f["level"] for f in g]}
                      for _, g in sorted(survivor_groups.items(), key=lambda x: -len(x[1]))[:20]],
        "assessment": None,
    }

    if cm_enrichment > 2.0:
        output["assessment"] = (f"CM ENRICHED SURVIVORS: {cm_enrichment:.1f}x CM enrichment. "
            f"{n_survivors} forms ({n_survivors/n_valid:.2%}) resist 6-prime identification. "
            f"Adelic resistance CORRELATES with algebraic symmetry.")
    elif cm_enrichment > 1.3:
        output["assessment"] = (f"WEAK CM CORRELATION: {cm_enrichment:.1f}x. "
            f"Survivors slightly more likely to be CM but effect is moderate.")
    else:
        output["assessment"] = (f"NO CM CORRELATION: enrichment={cm_enrichment:.2f}x. "
            f"Adelic resistance is NOT driven by algebraic symmetry — it is a number-theoretic phenomenon.")

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
