"""
M26: Congruence lattice mechanism
====================================
For forms f,g congruent mod ℓ, is there a lattice structure?
If f≡g mod 2 and g≡h mod 2, does f≡h mod 2? (Transitivity test)
If f≡g mod 2 and f≡g mod 3, does f≡g mod 6? (Multiplicativity test)

Compute the fraction of transitive closures that hold and the fraction
of CRT composites that hold. This tests whether congruences form a
lattice vs a random graph.
"""
import json, time
import numpy as np
import duckdb
from pathlib import Path
from collections import defaultdict

V2 = Path(__file__).resolve().parent
DB = V2.parents[3] / "charon" / "data" / "charon.duckdb"
OUT = V2 / "m26_congruence_lattice_results.json"

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

def check_cong(ap1, ap2, ell, good_idx, min_tested=10):
    tested = 0
    for k in good_idx:
        if k >= len(ap1) or k >= len(ap2): break
        tested += 1
        if (ap1[k] - ap2[k]) % ell != 0: return False
        if tested >= 20: break
    return tested >= min_tested

def main():
    t0 = time.time()
    print("=== M26: Congruence lattice mechanism ===\n")

    con = duckdb.connect(str(DB), read_only=True)
    rows = con.execute("""
        SELECT lmfdb_label, level, ap_coeffs FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND char_order = 1
        ORDER BY level LIMIT 3000
    """).fetchall()
    con.close()
    print(f"  {len(rows)} forms loaded")

    ap_primes = sieve(100)
    ELLS = [2, 3, 5]

    forms = []
    for label, level, ap_json in rows:
        ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
        ap_vals = [x[0] if isinstance(x, list) else x for x in ap]
        forms.append({"label": label, "level": level, "ap": ap_vals})

    # Group by level
    by_level = defaultdict(list)
    for f in forms: by_level[f["level"]].append(f)

    # Build congruence edges per ell
    print("  Building congruence graphs...")
    edges = {ell: set() for ell in ELLS}
    for level, group in by_level.items():
        if len(group) < 2: continue
        bad = prime_factors(level)
        good_idx = [i for i, p in enumerate(ap_primes) if p not in bad and p not in ELLS]
        for i in range(len(group)):
            for j in range(i+1, len(group)):
                for ell in ELLS:
                    if check_cong(group[i]["ap"], group[j]["ap"], ell, good_idx):
                        edges[ell].add((group[i]["label"], group[j]["label"]))

    for ell in ELLS:
        print(f"  mod-{ell} edges: {len(edges[ell])}")

    # Transitivity test: if (a,b) and (b,c) in edges, is (a,c)?
    print("\n  Transitivity test...")
    trans_results = {}
    for ell in ELLS:
        adj = defaultdict(set)
        for a, b in edges[ell]:
            adj[a].add(b); adj[b].add(a)
        n_trans_test = 0; n_trans_pass = 0
        for b in adj:
            nbrs = list(adj[b])
            for i in range(len(nbrs)):
                for j in range(i+1, len(nbrs)):
                    a, c = nbrs[i], nbrs[j]
                    n_trans_test += 1
                    if c in adj[a]:
                        n_trans_pass += 1
        rate = n_trans_pass / n_trans_test if n_trans_test > 0 else 0
        trans_results[str(ell)] = {
            "tested": n_trans_test, "passed": n_trans_pass,
            "rate": round(rate, 4),
        }
        print(f"  mod-{ell}: {n_trans_pass}/{n_trans_test} = {rate:.1%} transitive")

    # Multiplicativity test: if f≡g mod 2 AND mod 3, is f≡g mod 6?
    print("\n  Multiplicativity test (mod-2 ∩ mod-3 → mod-6)...")
    both_23 = edges[2] & edges[3]
    print(f"  Pairs congruent mod 2 AND 3: {len(both_23)}")

    n_mult_test = 0; n_mult_pass = 0
    for a, b in both_23:
        # Find ap data
        fa = next((f for f in forms if f["label"] == a), None)
        fb = next((f for f in forms if f["label"] == b), None)
        if not fa or not fb: continue
        bad = prime_factors(fa["level"])
        good_idx = [i for i, p in enumerate(ap_primes) if p not in bad and p > 5]
        n_mult_test += 1
        if check_cong(fa["ap"], fb["ap"], 6, good_idx):
            n_mult_pass += 1

    mult_rate = n_mult_pass / n_mult_test if n_mult_test > 0 else 0
    print(f"  mod-6 verification: {n_mult_pass}/{n_mult_test} = {mult_rate:.1%}")

    elapsed = time.time() - t0
    output = {
        "probe": "M26", "title": "Congruence lattice mechanism",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_forms": len(forms),
        "edge_counts": {str(ell): len(edges[ell]) for ell in ELLS},
        "transitivity": trans_results,
        "multiplicativity": {
            "pairs_mod2_and_3": len(both_23),
            "tested_mod6": n_mult_test,
            "passed_mod6": n_mult_pass,
            "rate": round(mult_rate, 4),
        },
        "assessment": None,
    }

    avg_trans = np.mean([v["rate"] for v in trans_results.values()])
    if avg_trans > 0.8 and mult_rate > 0.9:
        output["assessment"] = f"LATTICE: transitivity={avg_trans:.0%}, multiplicativity={mult_rate:.0%} — congruences form an algebraic lattice"
    elif avg_trans > 0.5:
        output["assessment"] = f"PARTIAL LATTICE: transitivity={avg_trans:.0%}, multiplicativity={mult_rate:.0%} — some lattice structure"
    else:
        output["assessment"] = f"NO LATTICE: transitivity only {avg_trans:.0%} — congruences are a random graph, not a lattice"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
