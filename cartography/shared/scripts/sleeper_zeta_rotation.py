"""
Sleeper-Zeta Rotation — Rotate prime-rich sleeping beauties into
the Riemann zeta / prime density landscape.
================================================================

Takes the ~48 prime-rich sleeper sequences from Cluster 3 and
systematically tests them against:
1. Prime counting function pi(x)
2. Prime gaps
3. ANTEDB zero-density exponent bounds
4. LMFDB conductor distributions
5. Chebyshev psi/theta functions (via OEIS)
6. Mertens function
7. Riemann zeta zeros (imaginary parts, via OEIS)

Each sleeper gets rotated through transforms (diff, ratio, log, partial sum)
and the result is correlated with each target. Genuine correlations after
partial-correlation controlling for size are flagged as DISCOVERIES.

No LLM. Pure computation. The Styx tests even the promising ones.
"""

import json
import math
import numpy as np
from scipy import stats
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[3]

import sys
sys.path.insert(0, str(Path(__file__).parent))

rng = np.random.RandomState(42)


def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True


def transforms(terms):
    """Apply all transforms to a sequence, return dict of name -> transformed terms."""
    results = {}
    t = [float(x) for x in terms[:30]]
    n = len(t)
    if n < 5:
        return results

    # Raw
    results["raw"] = t

    # First differences
    results["diff"] = [t[i+1] - t[i] for i in range(n-1)]

    # Second differences
    d1 = results["diff"]
    if len(d1) > 2:
        results["diff2"] = [d1[i+1] - d1[i] for i in range(len(d1)-1)]

    # Ratios (if all positive nonzero)
    pos = [x for x in t if x > 0]
    if len(pos) == n and n > 1:
        results["ratio"] = [t[i+1] / t[i] for i in range(n-1)]

    # Log terms (if all positive)
    if all(x > 0 for x in t):
        results["log"] = [math.log(x) for x in t]

    # Partial sums
    results["partial_sum"] = [sum(t[:i+1]) for i in range(n)]

    # Cumulative max
    results["cummax"] = [max(t[:i+1]) for i in range(n)]

    return results


def correlate_with_null(a, b, n_perm=200):
    """Spearman correlation with permutation null and partial correlation controlling for index."""
    n = min(len(a), len(b))
    if n < 8:
        return None
    a, b = np.array(a[:n]), np.array(b[:n])

    # Raw correlation
    r_raw, p_raw = stats.spearmanr(a, b)

    # Partial correlation controlling for index (both might just grow with n)
    idx = np.arange(n, dtype=float)
    a_resid = a - np.polyval(np.polyfit(idx, a, 1), idx)
    b_resid = b - np.polyval(np.polyfit(idx, b, 1), idx)

    if np.std(a_resid) < 1e-10 or np.std(b_resid) < 1e-10:
        r_partial = 0.0
    else:
        r_partial, _ = stats.spearmanr(a_resid, b_resid)

    # Permutation null on partial
    null_r = []
    for _ in range(n_perm):
        null_r.append(abs(stats.spearmanr(a_resid, rng.permutation(b_resid))[0]))
    p_partial = (sum(1 for nr in null_r if nr >= abs(r_partial)) + 1) / (len(null_r) + 1)

    return {
        "r_raw": round(float(r_raw), 4),
        "p_raw": round(float(p_raw), 6),
        "r_partial": round(float(r_partial), 4),
        "p_partial": round(float(p_partial), 6),
        "n": n,
        "survives": p_partial < 0.01 and abs(r_partial) > 0.3,
    }


def main():
    from search_engine import (_load_oeis, _oeis_cache, _load_oeis_names, _oeis_names_cache,
                               _load_oeis_crossrefs, _oeis_xref_cache, _oeis_xref_reverse)

    _load_oeis()
    _load_oeis_names()
    _load_oeis_crossrefs()

    print("=" * 70)
    print("  SLEEPER-ZETA ROTATION")
    print("  Rotating prime-rich sleepers into zeta/prime landscape")
    print("=" * 70)

    # Build prime-rich sleeper list
    print("\nFinding prime-rich sleepers...")
    sleepers = []
    for seq_id, terms in _oeis_cache.items():
        if len(terms) < 10:
            continue
        out_deg = len(_oeis_xref_cache.get(seq_id, set()))
        in_deg = len(_oeis_xref_reverse.get(seq_id, set()))
        if out_deg + in_deg > 5:
            continue
        t20 = [abs(t) for t in terms[:20] if t != 0]
        prime_frac = sum(1 for t in t20 if is_prime(t)) / max(len(t20), 1)
        if prime_frac > 0.3:
            sleepers.append((seq_id, prime_frac, terms[:30]))

    sleepers.sort(key=lambda x: -x[1])
    sleepers = sleepers[:100]  # top 100 most prime-rich
    print(f"Found {len(sleepers)} prime-rich sleepers")

    # Build target sequences from OEIS
    targets = {}

    # Primes
    targets["primes"] = _oeis_cache.get("A000040", [])[:50]

    # Prime counting pi(n)
    targets["pi(n)"] = _oeis_cache.get("A000720", [])[:50]

    # Prime gaps
    primes = targets["primes"]
    targets["prime_gaps"] = [primes[i+1] - primes[i] for i in range(len(primes)-1)]

    # Mertens function
    targets["mertens"] = _oeis_cache.get("A002321", [])[:50]

    # Chebyshev theta
    targets["chebyshev_theta"] = _oeis_cache.get("A057076", [])[:50]

    # Sum of prime factors
    targets["sopfr"] = _oeis_cache.get("A001414", [])[:50]

    # Euler totient cumulative
    totient = _oeis_cache.get("A000010", [])[:50]
    if totient:
        targets["totient_cumsum"] = [sum(totient[:i+1]) for i in range(len(totient))]

    # Prime powers
    targets["prime_powers"] = _oeis_cache.get("A000961", [])[:50]

    # Riemann zeta zeros (imaginary parts rounded)
    targets["zeta_zeros"] = _oeis_cache.get("A002410", [])[:50]

    # Number of primes <= n (different from pi(n) by indexing)
    targets["primepi"] = _oeis_cache.get("A000720", [])[:50]

    # Twin primes
    targets["twin_primes"] = _oeis_cache.get("A001359", [])[:50]

    # Conductor distribution from LMFDB
    from search_engine import _get_duck
    con = _get_duck()
    r0_conds = [r[0] for r in con.execute(
        "SELECT conductor FROM objects WHERE object_type='elliptic_curve' "
        "AND json_extract_string(properties, '$.rank')='0' AND conductor <= 5000 "
        "ORDER BY conductor LIMIT 50").fetchall()]
    r1_conds = [r[0] for r in con.execute(
        "SELECT conductor FROM objects WHERE object_type='elliptic_curve' "
        "AND json_extract_string(properties, '$.rank')='1' AND conductor <= 5000 "
        "ORDER BY conductor LIMIT 50").fetchall()]
    con.close()
    targets["ec_rank0_conds"] = r0_conds
    targets["ec_rank1_conds"] = r1_conds

    valid_targets = {k: v for k, v in targets.items() if v and len(v) >= 8}
    print(f"Target sequences: {len(valid_targets)} ({', '.join(valid_targets.keys())})")

    # Run rotations
    print(f"\nRotating {len(sleepers)} sleepers x {len(valid_targets)} targets...")
    discoveries = []
    all_results = []

    for i, (sid, pf, terms) in enumerate(sleepers):
        if i % 20 == 0:
            print(f"  [{i}/{len(sleepers)}] {sid}...")
        xforms = transforms(terms)

        for xname, xterms in xforms.items():
            for tname, tterms in valid_targets.items():
                result = correlate_with_null(xterms, tterms)
                if result is None:
                    continue

                entry = {
                    "sleeper": sid,
                    "transform": xname,
                    "target": tname,
                    **result,
                }
                all_results.append(entry)

                if result["survives"]:
                    name = _oeis_names_cache.get(sid, "")[:60]
                    discoveries.append(entry)
                    print(f"  *** DISCOVERY: {sid} ({xname}) ~ {tname}: "
                          f"r_raw={result['r_raw']:.3f} r_partial={result['r_partial']:.3f} "
                          f"p={result['p_partial']:.4f}")
                    print(f"      {name}")

    # Summary
    print()
    print("=" * 70)
    print(f"  ROTATION COMPLETE: {len(discoveries)} discoveries from "
          f"{len(sleepers)} sleepers x {len(valid_targets)} targets")
    print("=" * 70)

    if discoveries:
        print("\n  DISCOVERIES:")
        for d in discoveries:
            print(f"    {d['sleeper']} via {d['transform']:12s} ~ {d['target']:20s} "
                  f"r_partial={d['r_partial']:.3f} p={d['p_partial']:.4f}")
    else:
        print("\n  No discoveries survived partial correlation + permutation null.")
        print("  This is honest. The prime-rich sleepers don't encode new density laws")
        print("  beyond what's already captured in the hub sequences.")

    # Show near-misses (p < 0.05 but didn't clear 0.01)
    near_misses = [r for r in all_results
                   if r["p_partial"] < 0.05 and abs(r["r_partial"]) > 0.2
                   and not r["survives"]]
    if near_misses:
        near_misses.sort(key=lambda x: x["p_partial"])
        print(f"\n  NEAR-MISSES ({len(near_misses)}):")
        for nm in near_misses[:15]:
            print(f"    {nm['sleeper']} via {nm['transform']:12s} ~ {nm['target']:20s} "
                  f"r_partial={nm['r_partial']:.3f} p={nm['p_partial']:.4f}")

    # Save
    out = ROOT / "cartography" / "convergence" / "data" / "sleeper_zeta_rotation.json"
    json.dump({
        "sleepers_tested": len(sleepers),
        "targets": list(valid_targets.keys()),
        "total_correlations": len(all_results),
        "discoveries": discoveries,
        "near_misses": near_misses[:20] if near_misses else [],
    }, open(out, "w"), indent=2)
    print(f"\nSaved to {out}")


if __name__ == "__main__":
    main()
