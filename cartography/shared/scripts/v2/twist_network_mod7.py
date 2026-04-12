"""
ALL-041: Twist Network of Mod-7 Anomaly
=========================================
The 8 mod-7 starved forms: do their quadratic twists also show mod-7 starvation?
If so, starvation is an invariant of the twist orbit. If not, it's level-specific.

Method:
1. Load the 8 known mod-7 starved forms from starvation results
2. For each, compute all quadratic twists chi_d * f for small d
3. Search DuckDB for matching twisted forms (a_p -> chi_d(p)*a_p)
4. Check mod-7 starvation of the twisted forms
5. Build the twist network graph
"""

import json, time, math
import numpy as np
import duckdb
from pathlib import Path
from collections import Counter, defaultdict

V2 = Path(__file__).resolve().parent
DB_PATH = V2.parents[3] / "charon" / "data" / "charon.duckdb"
STARV_PATH = V2 / "residue_starvation_results.json"
OUT_PATH = V2 / "twist_network_mod7_results.json"

# The 8 mod-7 starved forms
MOD7_LABELS = [
    "49.2.a.a", "294.2.a.e", "490.2.a.k", "637.2.a.c",
    "637.2.a.d", "1274.2.a.o", "3822.2.a.w", "4018.2.a.s",
]

SMALL_DISCS = list(range(-20, 0)) + list(range(2, 21))
PRIMES_168 = None  # will load


def sieve(limit):
    is_p = [True] * (limit + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_p[i]:
            for j in range(i*i, limit+1, i):
                is_p[j] = False
    return [i for i in range(2, limit+1) if is_p[i]]


def kronecker(d, p):
    if p == 2:
        if d % 2 == 0: return 0
        r = d % 8
        return 1 if r in (1, 7) else -1
    if d % p == 0: return 0
    return pow(d, (p-1)//2, p) if pow(d, (p-1)//2, p) <= 1 else pow(d, (p-1)//2, p) - p


def prime_factors(n):
    f = set()
    d = 2
    while d*d <= n:
        while n % d == 0: f.add(d); n //= d
        d += 1
    if n > 1: f.add(n)
    return f


def compute_starvation_mod7(ap_vals, level):
    primes = sieve(997)
    bad = prime_factors(level)
    good = []
    for i, p in enumerate(primes):
        if i >= len(ap_vals): break
        if p not in bad and p != 7:
            good.append(ap_vals[i])
    if len(good) < 30:
        return None
    residues = set(v % 7 for v in good)
    ratio = len(residues) / 7
    return {
        "classes_hit": len(residues),
        "ratio": round(ratio, 4),
        "classes": sorted(residues),
        "missing": sorted(set(range(7)) - residues),
        "starved": ratio < 0.75,
        "n_good": len(good),
    }


def main():
    t0 = time.time()
    print("=== ALL-041: Twist Network of Mod-7 Anomaly ===\n")

    # Load all forms from DuckDB
    print("[1] Loading modular forms...")
    con = duckdb.connect(str(DB_PATH), read_only=True)
    rows = con.execute("""
        SELECT lmfdb_label, level, traces, ap_coeffs, is_cm, self_twist_type
        FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND char_order = 1
        ORDER BY level, lmfdb_label
    """).fetchall()
    print(f"    {len(rows)} forms loaded")

    # Build lookup
    forms = {}
    for label, level, traces, ap_json, is_cm, st_type in rows:
        ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
        ap_vals = [x[0] if isinstance(x, list) else x for x in ap]
        forms[label] = {
            "label": label, "level": level, "traces": traces,
            "ap": ap_vals, "is_cm": bool(is_cm), "self_twist": st_type,
        }
    con.close()

    primes = sieve(997)

    # Load starvation data for the 8 forms
    print("\n[2] Checking mod-7 starvation of source forms...")
    source_starvation = {}
    for label in MOD7_LABELS:
        if label in forms:
            s = compute_starvation_mod7(forms[label]["ap"], forms[label]["level"])
            source_starvation[label] = s
            if s:
                print(f"    {label} (N={forms[label]['level']}): classes={s['classes']} "
                      f"missing={s['missing']} ratio={s['ratio']}")

    # For each source form, find quadratic twists
    print("\n[3] Searching for quadratic twists...")
    twist_network = []

    for src_label in MOD7_LABELS:
        if src_label not in forms:
            continue
        src = forms[src_label]
        src_ap = src["ap"]
        src_level = src["level"]

        found_twists = []
        for d in SMALL_DISCS:
            # Compute twisted a_p values
            twisted_ap = []
            for i, p in enumerate(primes):
                if i >= len(src_ap): break
                chi = kronecker(d, p)
                twisted_ap.append(src_ap[i] * chi)

            # Search for matching form: compare first 20 good primes
            for label, f in forms.items():
                if label == src_label: continue
                f_ap = f["ap"]
                # Quick filter: check first few primes
                match = True
                tested = 0
                for i, p in enumerate(primes[:30]):
                    if i >= len(twisted_ap) or i >= len(f_ap): break
                    if f["level"] % p == 0 or src_level % p == 0: continue
                    tested += 1
                    if twisted_ap[i] != f_ap[i]:
                        match = False
                        break
                if match and tested >= 8:
                    # Verify deeper
                    deep_match = True
                    deep_tested = 0
                    for i, p in enumerate(primes[:100]):
                        if i >= len(twisted_ap) or i >= len(f_ap): break
                        if f["level"] % p == 0 or src_level % p == 0: continue
                        deep_tested += 1
                        if twisted_ap[i] != f_ap[i]:
                            deep_match = False
                            break
                    if deep_match and deep_tested >= 20:
                        starv = compute_starvation_mod7(f_ap, f["level"])
                        found_twists.append({
                            "disc": d, "twist_label": label,
                            "twist_level": f["level"],
                            "primes_verified": deep_tested,
                            "twist_is_cm": f["is_cm"],
                            "twist_starvation": starv,
                        })
                        break  # found the twist for this d

        twist_network.append({
            "source": src_label, "source_level": src_level,
            "source_starvation": source_starvation.get(src_label),
            "n_twists_found": len(found_twists),
            "twists": found_twists,
        })
        print(f"    {src_label}: {len(found_twists)} twists found")
        for tw in found_twists:
            s = tw["twist_starvation"]
            tag = "STARVED" if s and s["starved"] else "NOT starved"
            print(f"      d={tw['disc']:>3} → {tw['twist_label']} (N={tw['twist_level']}) {tag}")

    # Aggregate: is starvation twist-invariant?
    print("\n[4] Starvation invariance test...")
    total_twists = sum(len(t["twists"]) for t in twist_network)
    starved_twists = sum(
        1 for t in twist_network for tw in t["twists"]
        if tw["twist_starvation"] and tw["twist_starvation"]["starved"]
    )
    not_starved = total_twists - starved_twists

    elapsed = time.time() - t0
    output = {
        "challenge": "ALL-041",
        "title": "Twist Network of Mod-7 Anomaly",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "source_forms": MOD7_LABELS,
        "twist_network": twist_network,
        "summary": {
            "total_twists_found": total_twists,
            "starved_twists": starved_twists,
            "not_starved_twists": not_starved,
            "invariance_rate": round(starved_twists / total_twists, 4) if total_twists > 0 else None,
        },
        "assessment": None,
    }

    if total_twists == 0:
        output["assessment"] = "NO TWISTS FOUND — forms may be twist-minimal or search range too small"
    elif starved_twists == total_twists:
        output["assessment"] = f"PERFECT INVARIANCE: all {total_twists} twists are also mod-7 starved — starvation is a twist-orbit property"
    elif starved_twists / total_twists > 0.8:
        output["assessment"] = f"STRONG INVARIANCE: {starved_twists}/{total_twists} twists starved — starvation mostly preserved by twisting"
    elif starved_twists / total_twists > 0.3:
        output["assessment"] = f"PARTIAL: {starved_twists}/{total_twists} twists starved — starvation is NOT fully twist-invariant"
    else:
        output["assessment"] = f"BROKEN: only {starved_twists}/{total_twists} twists starved — starvation is level-specific, NOT twist-invariant"

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
