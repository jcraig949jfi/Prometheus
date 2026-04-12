"""
M51: Starvation-twist commutator
===================================
Extends ALL-041. For forms starved at ANY prime (not just mod-7),
compute quadratic twists and check: does twisting preserve starvation?

Define the commutator [S, T] = S∘T - T∘S where S = starvation check,
T = quadratic twist. If [S,T]=0 at some prime, starvation commutes
with twisting at that prime.
"""
import json, time
import numpy as np
import duckdb
from pathlib import Path
from collections import Counter, defaultdict

V2 = Path(__file__).resolve().parent
DB = V2.parents[3] / "charon" / "data" / "charon.duckdb"
STARV = V2 / "residue_starvation_results.json"
OUT = V2 / "m51_starvation_twist_commutator_results.json"

def sieve(limit):
    is_p = [True] * (limit + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_p[i]:
            for j in range(i*i, limit+1, i): is_p[j] = False
    return [i for i in range(2, limit+1) if is_p[i]]

def kronecker(d, n):
    if n == 0: return 0
    if n == 1: return 1
    result = 1
    if n < 0: n = -n; result = -1 if d < 0 else 1
    while n % 2 == 0:
        n //= 2
        if d % 2 != 0:
            r = d % 8
            if r == 3 or r == 5: result = -result
    while n > 1:
        if n % 2 == 0: n //= 2; continue
        if d % n == 0: return 0
        # Quadratic reciprocity (simplified)
        result *= 1 if pow(d, (n-1)//2, n) <= 1 else -1
        d, n = n, d % n
    return result

def main():
    t0 = time.time()
    print("=== M51: Starvation-twist commutator ===\n")

    with open(STARV) as f:
        starv_data = json.load(f)
    starved = starv_data["starved_forms"]
    starv_labels = {f["label"] for f in starved}
    starv_by_label = {f["label"]: f for f in starved}
    print(f"  {len(starved)} starved forms")

    # Load from DuckDB
    con = duckdb.connect(str(DB), read_only=True)
    rows = con.execute("""
        SELECT lmfdb_label, level, ap_coeffs FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND char_order = 1
    """).fetchall()
    con.close()

    form_by_label = {}
    form_by_level = defaultdict(list)
    for label, level, ap_json in rows:
        ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
        ap_vals = [x[0] if isinstance(x, list) else x for x in ap]
        form_by_label[label] = {"level": level, "ap": ap_vals}
        form_by_level[level].append(label)

    ap_primes = sieve(50)
    TWIST_DISCS = [-3, -4, -7, -8, 5, 8, 12, 13, -11, -15]
    STARVATION_PRIMES = [2, 3, 5, 7, 11]

    # For each starved form, find its twist and check starvation
    print("  Computing twist commutators...")
    results_by_prime = {str(p): {"preserved": 0, "lost": 0, "gained": 0, "n_tested": 0}
                       for p in STARVATION_PRIMES}
    twist_pairs = []

    for label in sorted(starv_labels)[:200]:  # Cap for speed
        form = form_by_label.get(label)
        if not form: continue

        starv_info = starv_by_label[label]
        starv_primes_form = set(starv_info.get("starvation", {}).keys())

        for d in TWIST_DISCS:
            # Twisted level
            N = form["level"]
            d_abs = abs(d)
            N_twist = N * d_abs**2 // (1 if N % d_abs != 0 else d_abs**2)
            if N_twist > 50000 or N_twist < 1: continue

            # Twist the ap coefficients
            twisted_ap = []
            for i, p in enumerate(ap_primes):
                if i >= len(form["ap"]): break
                chi = kronecker(d, p)
                twisted_ap.append(form["ap"][i] * chi)

            # Find matching form at twisted level
            candidates = form_by_level.get(N_twist, [])
            best_match = None
            best_score = 0
            for cand_label in candidates:
                cand = form_by_label[cand_label]
                # Score = number of matching a_p
                score = 0
                for i in range(min(len(twisted_ap), len(cand["ap"]), 10)):
                    if twisted_ap[i] == cand["ap"][i]:
                        score += 1
                if score > best_score:
                    best_score = score; best_match = cand_label

            if best_match and best_score >= 7:
                is_twist_starved = best_match in starv_labels
                twist_starv_primes = set(starv_by_label.get(best_match, {}).get("starvation", {}).keys())

                for p in STARVATION_PRIMES:
                    ps = str(p)
                    results_by_prime[ps]["n_tested"] += 1
                    orig_starved = ps in starv_primes_form
                    twist_starved = ps in twist_starv_primes

                    if orig_starved and twist_starved:
                        results_by_prime[ps]["preserved"] += 1
                    elif orig_starved and not twist_starved:
                        results_by_prime[ps]["lost"] += 1
                    elif not orig_starved and twist_starved:
                        results_by_prime[ps]["gained"] += 1

                twist_pairs.append({
                    "original": label, "twist_disc": d, "twisted_form": best_match,
                    "match_score": best_score,
                    "orig_starved_at": sorted(starv_primes_form),
                    "twist_starved_at": sorted(twist_starv_primes),
                    "is_twist_starved": is_twist_starved,
                })

    # Summary
    print(f"\n  {len(twist_pairs)} twist pairs found")
    print("\n  Commutator by prime:")
    for p in STARVATION_PRIMES:
        ps = str(p)
        r = results_by_prime[ps]
        n = r["n_tested"]
        if n > 0:
            pres_rate = r["preserved"] / max(r["preserved"] + r["lost"], 1)
            print(f"    mod-{p}: preserved={r['preserved']}, lost={r['lost']}, "
                  f"gained={r['gained']} (preservation={pres_rate:.0%})")

    elapsed = time.time() - t0
    total_preserved = sum(r["preserved"] for r in results_by_prime.values())
    total_lost = sum(r["lost"] for r in results_by_prime.values())
    total_gained = sum(r["gained"] for r in results_by_prime.values())
    pres_rate = total_preserved / max(total_preserved + total_lost, 1)

    output = {
        "probe": "M51", "title": "Starvation-twist commutator",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_starved_forms": len(starved),
        "n_twist_pairs": len(twist_pairs),
        "commutator_by_prime": results_by_prime,
        "overall": {
            "preserved": total_preserved, "lost": total_lost, "gained": total_gained,
            "preservation_rate": round(pres_rate, 4),
        },
        "twist_pair_examples": twist_pairs[:20],
        "assessment": None,
    }

    if pres_rate > 0.8:
        output["assessment"] = f"COMMUTES: starvation-twist preservation rate {pres_rate:.0%} — [S,T]≈0"
    elif pres_rate > 0.3:
        output["assessment"] = f"PARTIAL: preservation {pres_rate:.0%} — starvation partially commutes with twist"
    elif total_preserved + total_lost > 0:
        output["assessment"] = f"NON-COMMUTATIVE: preservation only {pres_rate:.0%} — twisting destroys starvation"
    else:
        output["assessment"] = f"NO TWIST MATCHES: {len(twist_pairs)} pairs found but no starvation overlap data"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
