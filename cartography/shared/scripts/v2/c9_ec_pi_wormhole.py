"""
Challenge 9: Force-Route EC↔OEIS Through the π Hub
=====================================================
71% of OEIS sequences are silent (unmatchable to ECs via a_p).
π is the true Fungrim hub. Can we find EC↔OEIS bridges by routing
through π-related transformations (π·a_p, a_p/π, etc.)?
"""
import json, time, math
import numpy as np
import duckdb
from pathlib import Path
from collections import Counter, defaultdict

V2 = Path(__file__).resolve().parent
DB = V2.parents[3] / "charon" / "data" / "charon.duckdb"
OEIS_PATH = V2.parents[3] / "cartography" / "oeis" / "data" / "stripped_new.txt"
OUT = V2 / "c9_ec_pi_wormhole_results.json"

def main():
    t0 = time.time()
    print("=== C9: Force-Route EC↔OEIS Through π Hub ===\n")

    # Load EC a_p data
    con = duckdb.connect(str(DB), read_only=True)
    rows = con.execute("""
        SELECT lmfdb_label, level, ap_coeffs FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND char_order = 1
        ORDER BY level LIMIT 3000
    """).fetchall()
    con.close()
    print(f"  {len(rows)} EC forms loaded")

    # Build EC fingerprints: a_p sequences
    ec_fingerprints = {}
    for label, level, ap_json in rows:
        ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
        ap_vals = tuple(int(x[0] if isinstance(x, list) else x) for x in ap[:10])
        ec_fingerprints[label] = ap_vals

    # Load OEIS (sample)
    print("  Loading OEIS...")
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
            if len(terms) >= 10: oeis[sid] = terms[:50]
    print(f"  {len(oeis)} OEIS sequences")

    # Direct match (no transform)
    print("\n[1] Direct EC→OEIS matching...")
    direct_matches = 0
    matched_ec = set()
    for label, ap in ec_fingerprints.items():
        for sid, terms in oeis.items():
            if tuple(terms[:len(ap)]) == ap:
                direct_matches += 1
                matched_ec.add(label)
                break
    direct_rate = direct_matches / len(ec_fingerprints)
    print(f"  Direct matches: {direct_matches} ({direct_rate:.1%})")
    silence_rate = 1 - direct_rate

    # π-transforms
    PI_TRANSFORMS = {
        "round(π·a_p)": lambda x: tuple(round(math.pi * v) for v in x),
        "round(a_p/π)": lambda x: tuple(round(v / math.pi) for v in x),
        "round(a_p²/π)": lambda x: tuple(round(v*v / math.pi) for v in x),
        "round(π²·a_p)": lambda x: tuple(round(math.pi**2 * v) for v in x),
        "|a_p|": lambda x: tuple(abs(v) for v in x),
        "a_p mod 12": lambda x: tuple(v % 12 for v in x),
        "round(a_p·√2)": lambda x: tuple(round(v * math.sqrt(2)) for v in x),
        "partial_sums": lambda x: tuple(sum(x[:i+1]) for i in range(len(x))),
        "abs_diffs": lambda x: tuple(abs(x[i+1]-x[i]) for i in range(len(x)-1)),
    }

    # Build OEIS lookup for fast matching
    oeis_prefixes = defaultdict(list)
    for sid, terms in oeis.items():
        prefix = tuple(terms[:8])
        oeis_prefixes[prefix].append(sid)

    print("\n[2] π-transform matching...")
    transform_results = {}
    for name, transform in PI_TRANSFORMS.items():
        matches = 0
        matched_pairs = []
        for label, ap in list(ec_fingerprints.items())[:1000]:
            try:
                transformed = transform(ap)
                prefix = transformed[:8]
                if prefix in oeis_prefixes:
                    matches += 1
                    matched_pairs.append({"ec": label, "oeis": oeis_prefixes[prefix][:3],
                                         "transform": name})
                    if len(matched_pairs) <= 3:
                        print(f"    {name}: {label} → {oeis_prefixes[prefix][:2]}")
            except: pass
        transform_results[name] = {
            "n_matches": matches,
            "match_rate": round(matches / min(1000, len(ec_fingerprints)), 6),
            "examples": matched_pairs[:5],
        }
        if matches > 0:
            print(f"  {name}: {matches} matches ({matches/min(1000,len(ec_fingerprints)):.2%})")

    # Subsequence matching: does any contiguous sub-8-tuple of OEIS appear in EC a_p?
    print("\n[3] Subsequence bridge search...")
    ec_set = set(ec_fingerprints.values())
    subseq_matches = 0
    subseq_examples = []
    for sid, terms in list(oeis.items())[:50000]:
        for start in range(len(terms)-9):
            sub = tuple(terms[start:start+10])
            if sub in ec_set:
                subseq_matches += 1
                ec_label = [l for l, ap in ec_fingerprints.items() if ap == sub]
                subseq_examples.append({"oeis": sid, "ec": ec_label[:1], "start": start})
                break

    print(f"  Subsequence matches: {subseq_matches}")

    # Total bridges found
    total_bridges = direct_matches + sum(r["n_matches"] for r in transform_results.values()) + subseq_matches
    total_unique_transforms = sum(1 for r in transform_results.values() if r["n_matches"] > 0)

    elapsed = time.time() - t0
    output = {
        "challenge": "C9", "title": "EC-OEIS via π Wormhole",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_ec": len(ec_fingerprints),
        "n_oeis": len(oeis),
        "direct_matches": direct_matches,
        "silence_rate": round(silence_rate, 4),
        "transforms": transform_results,
        "subsequence_matches": subseq_matches,
        "total_bridges": total_bridges,
        "assessment": None,
    }

    working = [name for name, r in transform_results.items() if r["n_matches"] > 0]
    if working:
        best = max(transform_results.items(), key=lambda x: x[1]["n_matches"])
        output["assessment"] = (
            f"π WORMHOLE PARTIALLY OPEN: {total_unique_transforms} transforms find bridges. "
            f"Best: '{best[0]}' with {best[1]['n_matches']} matches. "
            f"Silence rate reduced from {silence_rate:.0%} to {max(0, silence_rate - total_bridges/len(ec_fingerprints)):.0%}. "
            f"But {total_bridges} total bridges is still sparse — the gap is ALGEBRAIC, not transformational.")
    else:
        output["assessment"] = (
            f"π WORMHOLE CLOSED: no π-transform bridges found. "
            f"The EC-OEIS gap ({silence_rate:.0%}) is a fundamental algebraic wall, "
            f"not a coordinate mismatch. π does not mediate EC↔OEIS connection.")

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
