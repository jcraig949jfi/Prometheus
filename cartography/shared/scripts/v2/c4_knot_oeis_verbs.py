"""
Challenge 4: Knot-OEIS Verb Distribution
===========================================
The torus knot→OEIS bridge uses Jones polynomial determinant channel.
Find torus-knot-related OEIS sequences by matching determinant values
(characteristic polynomial x²(x+1) → det = 7, 9, 11 for T(2,7/9/11)).
Analyse the operadic "verb" distribution of these bridge sequences.
Are they dominated by "Equal" (equational) or "And" (cross-constraint)?
"""
import json, time, math
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

V2 = Path(__file__).resolve().parent
KNOTS = V2.parents[3] / "cartography" / "knots" / "data" / "knots.json"
OEIS_PATH = V2.parents[3] / "cartography" / "oeis" / "data" / "stripped_new.txt"
FUNGRIM = V2.parents[3] / "cartography" / "fungrim" / "data" / "fungrim_index.json"
DNA = V2 / "algebraic_dna_fungrim_results.json"
OUT = V2 / "c4_knot_oeis_verbs_results.json"

# Torus knot determinants: T(2,n) has det = n for odd n
TORUS_KNOTS = {
    "T(2,3)": {"det": 3, "crossing": 3},
    "T(2,5)": {"det": 5, "crossing": 5},
    "T(2,7)": {"det": 7, "crossing": 7},
    "T(2,9)": {"det": 9, "crossing": 9},
    "T(2,11)": {"det": 11, "crossing": 11},
    "T(2,13)": {"det": 13, "crossing": 13},
    "T(3,4)": {"det": 12, "crossing": 8},  # Actually |det|=12
    "T(3,5)": {"det": 15, "crossing": 10},
}

def main():
    t0 = time.time()
    print("=== Challenge 4: Knot-OEIS Verb Distribution ===\n")

    # Load knot data — find torus knots by determinant matching
    with open(KNOTS) as f:
        kd = json.load(f)

    torus_dets = set(v["det"] for v in TORUS_KNOTS.values())
    print(f"  Torus knot determinants: {sorted(torus_dets)}")

    # Find matching knots in data
    matching_knots = [k for k in kd["knots"] if k.get("determinant") in torus_dets]
    print(f"  Knots with torus-like determinants: {len(matching_knots)}")

    # Load OEIS and find sequences containing torus knot determinants
    print("\n  Loading OEIS for determinant matching...")
    bridge_seqs = defaultdict(set)  # det → set of OEIS IDs
    n_loaded = 0
    with open(OEIS_PATH, 'r', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or not line.startswith('A'): continue
            parts = line.split(',')
            sid = parts[0].strip().split()[0]
            terms = []
            for t in parts[1:]:
                t = t.strip()
                if t:
                    try: terms.append(int(t))
                    except: pass
            if len(terms) >= 5:
                n_loaded += 1
                term_set = set(terms[:50])
                # Check for sequences where torus knot dets appear prominently
                for det in torus_dets:
                    if det in term_set:
                        # More specific: det appears in first 20 terms
                        if det in set(terms[:20]):
                            bridge_seqs[det].add(sid)

    print(f"  {n_loaded} OEIS sequences scanned")
    for det in sorted(torus_dets):
        n_matches = len(bridge_seqs.get(det, set()))
        print(f"    det={det}: {n_matches} OEIS matches")

    # Too many matches for common numbers — use stricter filter
    # Require ALL 8 torus knot dets to appear (very restrictive)
    multi_det_seqs = Counter()
    all_det_seqs = set()
    for det, sids in bridge_seqs.items():
        all_det_seqs.update(sids)
    for sid in all_det_seqs:
        n_dets = sum(1 for det, sids in bridge_seqs.items() if sid in sids)
        multi_det_seqs[sid] = n_dets

    # Use ≥7 matching dets (nearly all torus knot dets present)
    threshold = 7
    strong_bridges = [sid for sid, cnt in multi_det_seqs.items() if cnt >= threshold]
    if len(strong_bridges) > 2000:
        threshold = 8
        strong_bridges = [sid for sid, cnt in multi_det_seqs.items() if cnt >= threshold]
    if len(strong_bridges) < 10:
        threshold = 6
        strong_bridges = [sid for sid, cnt in multi_det_seqs.items() if cnt >= threshold]
    if len(strong_bridges) < 10:
        threshold = 5
        strong_bridges = [sid for sid, cnt in multi_det_seqs.items() if cnt >= threshold]
    print(f"\n  Sequences with ≥{threshold} torus knot determinants: {len(strong_bridges)}")

    # Analyse these bridge sequences for structural patterns
    # Load the first 50 terms of each bridge sequence
    bridge_data = {}
    with open(OEIS_PATH, 'r', errors='ignore') as f:
        for line in f:
            if not line.strip() or not line.startswith('A'): continue
            parts = line.split(',')
            sid = parts[0].strip().split()[0]
            if sid in set(strong_bridges):
                terms = []
                for t in parts[1:]:
                    t = t.strip()
                    if t:
                        try: terms.append(int(t))
                        except: pass
                bridge_data[sid] = terms[:50]

    # Operadic verb analysis: classify sequences by structural type
    # "Equal" = monotonic, single-relation sequences (e.g. n^2, primes)
    # "And" = multi-constraint sequences (e.g. numbers satisfying P1 AND P2)
    verb_analysis = {}
    for sid, terms in bridge_data.items():
        if len(terms) < 5: continue
        arr = np.array(terms, dtype=float)
        diffs = np.diff(arr)

        # Monotonicity
        is_monotone = np.all(diffs >= 0) or np.all(diffs <= 0)

        # Growth rate classification
        if len(arr) > 2 and arr[-1] > 0 and arr[0] > 0:
            growth = np.log(abs(arr[-1]) + 1) / np.log(abs(arr[0]) + 2)
        else:
            growth = 1

        # Gaps analysis: are gaps regular or irregular?
        if len(diffs) > 2:
            gap_cv = float(np.std(diffs) / (np.mean(np.abs(diffs)) + 1e-10))
        else:
            gap_cv = 0

        # Verb classification
        if is_monotone and gap_cv < 0.5:
            verb = "Equal"  # Equational: regular, predictable
        elif is_monotone and gap_cv < 2:
            verb = "Map"    # Mapping: monotone but irregular
        elif not is_monotone:
            verb = "And"    # Cross-constraint: oscillating
        else:
            verb = "And"    # Irregular monotone → likely multi-constraint

        verb_analysis[sid] = {
            "verb": verb,
            "is_monotone": bool(is_monotone),
            "gap_cv": round(gap_cv, 4),
            "growth": round(growth, 4),
            "n_terms": len(terms),
            "n_matching_dets": multi_det_seqs[sid],
        }

    verb_dist = Counter(v["verb"] for v in verb_analysis.values())
    print(f"\n  Verb distribution of bridge sequences:")
    for v, cnt in verb_dist.most_common():
        print(f"    {v}: {cnt} ({cnt/len(verb_analysis):.0%})")

    # Baseline: random OEIS sample
    print("\n  Computing baseline verb distribution...")
    np.random.seed(42)
    baseline_verbs = Counter()
    sample_count = 0
    with open(OEIS_PATH, 'r', errors='ignore') as f:
        for line in f:
            if not line.strip() or not line.startswith('A'): continue
            if np.random.random() > 0.01: continue  # 1% sample
            parts = line.split(',')
            terms = []
            for t in parts[1:]:
                t = t.strip()
                if t:
                    try: terms.append(int(t))
                    except: pass
            if len(terms) < 5: continue
            arr = np.array(terms[:50], dtype=float)
            diffs = np.diff(arr)
            is_mono = np.all(diffs >= 0) or np.all(diffs <= 0)
            gap_cv = float(np.std(diffs) / (np.mean(np.abs(diffs)) + 1e-10)) if len(diffs) > 2 else 0
            if is_mono and gap_cv < 0.5: baseline_verbs["Equal"] += 1
            elif is_mono and gap_cv < 2: baseline_verbs["Map"] += 1
            else: baseline_verbs["And"] += 1
            sample_count += 1
            if sample_count >= 3000: break

    print(f"  Baseline ({sample_count} sequences):")
    for v, cnt in baseline_verbs.most_common():
        print(f"    {v}: {cnt} ({cnt/sample_count:.0%})")

    # Enrichment ratios
    bridge_total = sum(verb_dist.values())
    enrichment = {}
    for v in ["Equal", "Map", "And"]:
        bridge_rate = verb_dist.get(v, 0) / bridge_total if bridge_total > 0 else 0
        base_rate = baseline_verbs.get(v, 0) / sample_count if sample_count > 0 else 0
        enrichment[v] = round(bridge_rate / base_rate, 4) if base_rate > 0 else 0
    print(f"\n  Verb enrichment (bridge vs baseline): {enrichment}")

    elapsed = time.time() - t0
    output = {
        "challenge": "C4", "title": "Knot-OEIS Verb Distribution",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "torus_determinants": sorted(torus_dets),
        "n_strong_bridges": len(strong_bridges),
        "bridge_verb_distribution": dict(verb_dist),
        "baseline_verb_distribution": dict(baseline_verbs),
        "verb_enrichment": enrichment,
        "bridge_sequences": {sid: verb_analysis[sid] for sid in sorted(verb_analysis.keys())[:30]},
        "assessment": None,
    }

    # Find most ENRICHED verb (not most common — most enriched vs baseline)
    dominant_verb = max(enrichment, key=enrichment.get) if enrichment else "unknown"
    dominant_enrich = enrichment.get(dominant_verb, 0)
    if dominant_verb == "Equal":
        output["assessment"] = (
            f"EQUATIONAL TIGHTNESS: bridge sequences are {dominant_enrich:.1f}x enriched for 'Equal' verb. "
            f"Knot-OEIS bridges are governed by single-relation equational structure, not cross-constraint webs.")
    elif dominant_verb == "And":
        output["assessment"] = (
            f"CROSS-CONSTRAINT WEBS: bridge sequences are {dominant_enrich:.1f}x enriched for 'And' verb. "
            f"Knot-OEIS bridges arise from multi-constraint intersections — combinatorial, not equational.")
    else:
        output["assessment"] = (
            f"MAPPING STRUCTURE: bridges are {dominant_enrich:.1f}x enriched for 'Map' verb. "
            f"Knot-OEIS connections are monotone but irregular — functional, not equational or conjunctive.")

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
