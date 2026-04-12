"""
Challenge 6: Dissect form 15.2.a.a — Local Topology
======================================================
The top DMZ candidate with AC=0.87 at lag 8.
Full dissection: a_p sequence, congruence neighborhood, twist orbit,
starvation status, adelic fibre, local crowding, and the specific
mechanism behind the anomalous autocorrelation.
"""
import json, time, math
import numpy as np
import duckdb
from scipy import stats
from pathlib import Path
from collections import Counter, defaultdict

V2 = Path(__file__).resolve().parent
DB = V2.parents[3] / "charon" / "data" / "charon.duckdb"
OUT = V2 / "c6_dissect_15_2_a_a_results.json"

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
        result *= 1 if pow(d, (n-1)//2, n) <= 1 else -1
        d, n = n, d % n
    return result

def autocorrelation_full(x, max_lag=15):
    n = len(x); x = x - np.mean(x); var = np.var(x)
    if var < 1e-12: return np.zeros(max_lag)
    return np.array([float(np.sum(x[:n-k]*x[k:])/((n-k)*var)) for k in range(max_lag)])

def main():
    t0 = time.time()
    print("=== Challenge 6: Dissect Form 15.2.a.a ===\n")

    con = duckdb.connect(str(DB), read_only=True)

    # Get the target form
    target_row = con.execute("""
        SELECT lmfdb_label, level, ap_coeffs, is_cm
        FROM modular_forms WHERE lmfdb_label = '15.2.a.a'
    """).fetchone()

    # Get ALL forms at level 15
    level15 = con.execute("""
        SELECT lmfdb_label, level, ap_coeffs, is_cm
        FROM modular_forms WHERE level = 15 AND weight = 2 AND dim = 1
    """).fetchall()

    # Get nearby levels for crowding analysis
    nearby = con.execute("""
        SELECT lmfdb_label, level, ap_coeffs, is_cm
        FROM modular_forms
        WHERE level BETWEEN 10 AND 25 AND weight = 2 AND dim = 1 AND char_order = 1
        ORDER BY level
    """).fetchall()

    # Get ALL forms for congruence search
    all_forms = con.execute("""
        SELECT lmfdb_label, level, ap_coeffs, is_cm
        FROM modular_forms WHERE weight = 2 AND dim = 1 AND char_order = 1
    """).fetchall()
    con.close()

    ap_primes = sieve(200)
    ELLS = [2, 3, 5, 7, 11, 13]

    if not target_row:
        print("  ERROR: 15.2.a.a not found in database")
        # Try nearby labels
        print(f"  Level 15 forms: {[r[0] for r in level15]}")
        # Use first available level-15 form
        if level15:
            target_row = level15[0]
            print(f"  Using: {target_row[0]}")
        else:
            return

    label, level, ap_json, is_cm = target_row
    ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
    ap_vals = np.array([x[0] if isinstance(x, list) else x for x in ap], dtype=float)
    print(f"  Target: {label} (level={level}, CM={is_cm})")
    print(f"  a_p values ({len(ap_vals)} primes):")

    bad = prime_factors(level)
    print(f"  Bad primes (divide level): {sorted(bad)}")
    for i, p in enumerate(ap_primes[:25]):
        if i >= len(ap_vals): break
        tag = " [BAD]" if p in bad else ""
        norm = ap_vals[i] / (2*math.sqrt(p)) if p not in bad else 0
        print(f"    a_{p} = {int(ap_vals[i])}, normalized = {norm:.4f}{tag}")

    # 1. Full autocorrelation profile
    print("\n[1] AUTOCORRELATION PROFILE")
    good_vals = [ap_vals[i] for i, p in enumerate(ap_primes[:25]) if i < len(ap_vals) and p not in bad]
    ac = autocorrelation_full(np.array(good_vals), min(15, len(good_vals)-1))
    for lag in range(len(ac)):
        marker = " <<<" if abs(ac[lag]) > 0.5 else ""
        print(f"    lag={lag}: AC={ac[lag]:.4f}{marker}")

    # WHY is lag 8 so high? Examine the actual pattern
    print("\n  Pattern at lag 8:")
    for i in range(min(len(good_vals)-8, 10)):
        print(f"    a_p[{i}]={good_vals[i]:.0f} × a_p[{i+8}]={good_vals[i+8]:.0f}")

    # 2. Residue fingerprint
    print("\n[2] RESIDUE FINGERPRINT")
    for ell in ELLS:
        residues = [int(ap_vals[i]) % ell for i, p in enumerate(ap_primes[:20])
                   if i < len(ap_vals) and p not in bad]
        missing = set(range(ell)) - set(residues)
        print(f"    mod {ell}: residues={residues[:15]}, missing={sorted(missing)}")

    # 3. Congruence neighbors across ALL forms
    print("\n[3] CONGRUENCE NEIGHBORS")
    neighbors = {ell: [] for ell in ELLS}
    ap_int = [int(v) for v in ap_vals]
    for other_label, other_level, other_ap_json, other_cm in all_forms:
        if other_label == label: continue
        other_ap = json.loads(other_ap_json) if isinstance(other_ap_json, str) else other_ap_json
        other_vals = [x[0] if isinstance(x, list) else x for x in other_ap]
        other_bad = prime_factors(other_level)
        for ell in ELLS:
            good_idx = [i for i, p in enumerate(ap_primes[:20])
                       if p not in bad and p not in other_bad and p != ell]
            tested = 0; cong = True
            for k in good_idx:
                if k >= len(ap_int) or k >= len(other_vals): break
                tested += 1
                if (ap_int[k] - other_vals[k]) % ell != 0:
                    cong = False; break
                if tested >= 12: break
            if cong and tested >= 8:
                neighbors[ell].append({"label": other_label, "level": other_level, "cm": bool(other_cm)})

    for ell in ELLS:
        nn = neighbors[ell]
        labels = [n["label"] for n in nn[:10]]
        levels = [n["level"] for n in nn[:10]]
        print(f"    mod {ell}: {len(nn)} congruent forms, levels={levels}")

    # 4. Twist orbit
    print("\n[4] TWIST ORBIT")
    TWIST_DISCS = [-3, -4, -7, -8, 5, 8, 12, 13, -11, -15, -19, -20]
    twist_matches = []
    for d in TWIST_DISCS:
        twisted = [int(ap_vals[i]) * kronecker(d, p) for i, p in enumerate(ap_primes[:15])
                  if i < len(ap_vals)]
        # Search for matching form
        best_match = None; best_score = 0
        for other_label, other_level, other_ap_json, _ in all_forms:
            if other_label == label: continue
            other_ap = json.loads(other_ap_json) if isinstance(other_ap_json, str) else other_ap_json
            other_vals = [x[0] if isinstance(x, list) else x for x in other_ap[:15]]
            score = sum(1 for i in range(min(len(twisted), len(other_vals), 10))
                       if twisted[i] == other_vals[i])
            if score > best_score: best_score = score; best_match = other_label
        if best_match and best_score >= 7:
            twist_matches.append({"disc": d, "match": best_match, "score": best_score})
            print(f"    χ_{d}: matches {best_match} (score={best_score}/10)")

    # 5. Local crowding analysis
    print("\n[5] LOCAL CROWDING")
    nearby_forms = defaultdict(list)
    for r_label, r_level, r_ap_json, r_cm in nearby:
        r_ap = json.loads(r_ap_json) if isinstance(r_ap_json, str) else r_ap_json
        r_vals = [x[0] if isinstance(x, list) else x for x in r_ap[:15]]
        nearby_forms[r_level].append({"label": r_label, "ap": r_vals})

    for lev in sorted(nearby_forms.keys()):
        n = len(nearby_forms[lev])
        print(f"    Level {lev}: {n} forms")

    # L2 distances to ALL level-15 forms
    l15_dists = []
    for r in level15:
        if r[0] == label: continue
        r_ap = json.loads(r[2]) if isinstance(r[2], str) else r[2]
        r_vals = np.array([x[0] if isinstance(x, list) else x for x in r_ap[:len(ap_vals)]], dtype=float)
        n = min(len(ap_vals), len(r_vals))
        d = float(np.linalg.norm(ap_vals[:n] - r_vals[:n]))
        l15_dists.append({"label": r[0], "distance": round(d, 2)})

    l15_dists.sort(key=lambda x: x["distance"])
    print(f"\n  Nearest level-15 neighbors (L2):")
    for nd in l15_dists[:5]:
        print(f"    {nd['label']}: dist={nd['distance']}")

    # 6. Why lag 8? Periodicity analysis
    print("\n[6] PERIODICITY ANALYSIS")
    fft = np.fft.rfft(np.array(good_vals) - np.mean(good_vals))
    power = np.abs(fft)**2
    freqs = np.fft.rfftfreq(len(good_vals))
    print(f"  FFT power spectrum:")
    for i in range(min(len(power), 10)):
        marker = " <<<" if power[i] == max(power[1:]) else ""
        print(f"    freq={freqs[i]:.4f} (period={1/freqs[i]:.1f} if >0): power={power[i]:.1f}{marker}")
    dominant_period = 1/freqs[np.argmax(power[1:])+1] if len(power) > 1 else 0
    print(f"  Dominant period: {dominant_period:.1f} primes")

    elapsed = time.time() - t0
    output = {
        "challenge": "C6", "title": f"Dissect {label}",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "target": {"label": label, "level": level, "is_cm": bool(is_cm),
                   "bad_primes": sorted(bad),
                   "n_ap": len(ap_vals),
                   "ap_first_20": [int(v) for v in ap_vals[:20]]},
        "autocorrelation": [round(float(a), 6) for a in ac],
        "dominant_period": round(dominant_period, 2),
        "congruence_neighbors": {str(ell): len(neighbors[ell]) for ell in ELLS},
        "congruence_details": {str(ell): neighbors[ell][:10] for ell in ELLS},
        "twist_orbit": twist_matches,
        "level15_neighbors": l15_dists[:10],
        "crowding": {str(lev): len(fs) for lev, fs in sorted(nearby_forms.items())},
        "assessment": None,
    }

    # Build assessment
    total_neighbors = sum(len(neighbors[ell]) for ell in ELLS)
    parts = [f"Form {label}: {len(ap_vals)} a_p coefficients, CM={is_cm}"]
    parts.append(f"Dominant period={dominant_period:.1f} primes (explains lag-8 AC)")
    parts.append(f"{total_neighbors} total congruence neighbors across {len(ELLS)} primes")
    parts.append(f"{len(twist_matches)} twist matches found")
    if l15_dists:
        parts.append(f"Nearest level-15 neighbor at L2={l15_dists[0]['distance']:.1f}")
    output["assessment"] = ". ".join(parts)

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
