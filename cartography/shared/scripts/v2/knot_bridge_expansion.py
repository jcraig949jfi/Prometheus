"""
ALL-067: Knot Bridge Expansion
================================
Extend the confirmed torus knot → OEIS bridge to a full scan:
1. For ALL 12,965 knots, compute determinant + Jones/Alexander coefficient fingerprints
2. Match determinants against OEIS sequences (beyond just torus knots)
3. Match coefficient subsequences against OEIS
4. Classify matches: structural (e.g., Fibonacci) vs coincidental
5. Build the complete knot↔OEIS bridge graph

Uses knots.json + OEIS stripped sequences.
"""

import json, time
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

V2 = Path(__file__).resolve().parent
KNOTS_PATH = V2.parents[3] / "cartography" / "knots" / "data" / "knots.json"
OEIS_PATH = V2.parents[3] / "cartography" / "oeis" / "data" / "stripped_new.txt"
OEIS_NAMES = V2.parents[3] / "cartography" / "oeis" / "data" / "oeis_names.json"
MOONSHINE_RESULTS = V2 / "moonshine_oeis_results.json"
OUT_PATH = V2 / "knot_bridge_expansion_results.json"


def load_oeis_sequences(path, max_seqs=400000):
    seqs = {}
    with open(path, 'r', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or not line.startswith('A'):
                continue
            parts = line.split(',')
            seq_id = parts[0].strip().split()[0]
            terms = []
            for t in parts[1:]:
                t = t.strip()
                if t:
                    try: terms.append(int(t))
                    except: pass
            if terms:
                seqs[seq_id] = terms
            if len(seqs) >= max_seqs:
                break
    return seqs


def main():
    t0 = time.time()
    print("=== ALL-067: Knot Bridge Expansion ===\n")

    print("[1] Loading knots...")
    with open(KNOTS_PATH) as f:
        knot_data = json.load(f)
    knots = knot_data["knots"]
    print(f"    {len(knots)} knots loaded")

    print("[2] Loading OEIS sequences...")
    oeis = load_oeis_sequences(OEIS_PATH)
    print(f"    {len(oeis)} OEIS sequences loaded")

    try:
        with open(OEIS_NAMES) as f:
            names = json.load(f)
    except: names = {}

    # Phase 1: Determinant matching
    print("\n[3] Phase 1: Determinant sequence matching...")
    # Build the full determinant sequence (ordered by crossing number)
    knots_sorted = sorted(knots, key=lambda k: (k["crossing_number"], k["name"]))
    det_seq = [k["determinant"] for k in knots_sorted if k.get("determinant") is not None]
    det_set = set(det_seq)
    print(f"    Knot determinants: {len(det_seq)} values, {len(det_set)} unique")

    # Search OEIS for sequences containing knot determinant subsequences
    det_matches = []
    det_window = det_seq[:15]  # First 15 determinants as search key
    for sid, terms in oeis.items():
        if len(terms) < 6:
            continue
        # Check if any 5-term window of det_seq appears in this OEIS sequence
        for i in range(min(len(det_window) - 4, 10)):
            window = tuple(det_window[i:i+5])
            if all(w == 0 for w in window):
                continue
            for j in range(len(terms) - 4):
                if tuple(terms[j:j+5]) == window:
                    det_matches.append({
                        "oeis_id": sid, "name": names.get(sid, ""),
                        "window": list(window), "offset_knot": i, "offset_oeis": j,
                    })
                    break
            if det_matches and det_matches[-1]["oeis_id"] == sid:
                break

    print(f"    Determinant subsequence matches: {len(det_matches)}")

    # Phase 2: Individual determinant value overlap
    print("\n[4] Phase 2: Determinant value overlap with OEIS sequences...")
    # For each OEIS seq, how many of its terms are knot determinants?
    overlap_scores = []
    for sid, terms in oeis.items():
        term_set = set(terms)
        overlap = det_set & term_set
        if len(overlap) >= 5:
            frac = len(overlap) / min(len(det_set), len(term_set))
            overlap_scores.append({
                "oeis_id": sid, "name": names.get(sid, "")[:80],
                "overlap_count": len(overlap),
                "overlap_fraction": round(frac, 4),
            })
    overlap_scores.sort(key=lambda x: -x["overlap_count"])
    print(f"    Sequences with ≥5 shared values: {len(overlap_scores)}")
    for o in overlap_scores[:10]:
        print(f"      {o['oeis_id']}: {o['overlap_count']} shared, {o['name'][:60]}")

    # Phase 3: Jones coefficient fingerprint matching (hash-based)
    print("\n[5] Phase 3: Jones coefficient subsequence scan (hash index)...")
    # Build index: 4-gram -> list of OEIS IDs
    oeis_4gram_index = defaultdict(list)
    for sid, terms in oeis.items():
        if len(terms) < 4:
            continue
        seen_grams = set()
        for j in range(min(len(terms) - 3, 50)):
            gram = tuple(terms[j:j+4])
            if gram not in seen_grams:
                seen_grams.add(gram)
                oeis_4gram_index[gram].append((sid, j))
    print(f"    Built 4-gram index: {len(oeis_4gram_index)} unique 4-grams")

    jones_matches = []
    for k in knots:
        jc = k.get("jones_coeffs", [])
        if len(jc) < 4:
            continue
        abs_jc = [abs(c) for c in jc[:8] if isinstance(c, (int, float))]
        if len(abs_jc) < 4 or all(c == 0 for c in abs_jc):
            continue
        window = tuple(abs_jc[:4])
        if window in oeis_4gram_index:
            for sid, offset in oeis_4gram_index[window]:
                jones_matches.append({
                    "knot": k["name"], "oeis_id": sid,
                    "name": names.get(sid, "")[:60],
                    "jones_window": list(window), "oeis_offset": offset,
                })

    seen_oeis = set()
    unique_jones = []
    for m in jones_matches:
        if m["oeis_id"] not in seen_oeis:
            seen_oeis.add(m["oeis_id"])
            unique_jones.append(m)
    print(f"    Jones coefficient matches: {len(jones_matches)} raw, {len(unique_jones)} unique OEIS")

    # Phase 4: Alexander coefficient matching (hash-based)
    print("\n[6] Phase 4: Alexander coefficient matching...")
    oeis_3gram_index = defaultdict(list)
    for sid, terms in oeis.items():
        if len(terms) < 3:
            continue
        seen_grams = set()
        for j in range(min(len(terms) - 2, 50)):
            gram = tuple(terms[j:j+3])
            if gram not in seen_grams:
                seen_grams.add(gram)
                oeis_3gram_index[gram].append((sid, j))
    print(f"    Built 3-gram index: {len(oeis_3gram_index)} unique 3-grams")

    alex_matches = []
    for k in knots:
        ac = k.get("alex_coeffs", [])
        if len(ac) < 3:
            continue
        abs_ac = [abs(c) for c in ac[:6] if isinstance(c, (int, float))]
        if len(abs_ac) < 3 or all(c == 0 for c in abs_ac):
            continue
        window = tuple(abs_ac[:3])
        if window in oeis_3gram_index:
            for sid, offset in oeis_3gram_index[window]:
                alex_matches.append({
                    "knot": k["name"], "oeis_id": sid,
                    "name": names.get(sid, "")[:60],
                })

    seen_oeis2 = set()
    unique_alex = []
    for m in alex_matches:
        if m["oeis_id"] not in seen_oeis2:
            seen_oeis2.add(m["oeis_id"])
            unique_alex.append(m)
    print(f"    Alexander matches: {len(alex_matches)} raw, {len(unique_alex)} unique OEIS")

    elapsed = time.time() - t0
    all_bridge_oeis = set(m["oeis_id"] for m in det_matches)
    all_bridge_oeis |= set(o["oeis_id"] for o in overlap_scores[:50])
    all_bridge_oeis |= seen_oeis | seen_oeis2

    output = {
        "challenge": "ALL-067", "title": "Knot Bridge Expansion",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_knots": len(knots), "n_oeis": len(oeis),
        "determinant_matches": det_matches[:20],
        "determinant_overlap_top": overlap_scores[:30],
        "jones_matches": unique_jones[:30],
        "alexander_matches": unique_alex[:30],
        "bridge_graph": {
            "total_unique_oeis_bridged": len(all_bridge_oeis),
            "via_determinant_subseq": len(det_matches),
            "via_det_value_overlap": len([o for o in overlap_scores if o["overlap_count"] >= 5]),
            "via_jones_coeffs": len(unique_jones),
            "via_alexander_coeffs": len(unique_alex),
        },
        "assessment": None,
    }

    if len(all_bridge_oeis) > 100:
        output["assessment"] = f"WIDE BRIDGE: {len(all_bridge_oeis)} unique OEIS sequences connected to knot invariants — bridge is broad, not narrow"
    elif len(all_bridge_oeis) > 20:
        output["assessment"] = f"MODERATE BRIDGE: {len(all_bridge_oeis)} OEIS connections. Multiple channels (det, Jones, Alexander)"
    else:
        output["assessment"] = f"NARROW BRIDGE: only {len(all_bridge_oeis)} OEIS connections — torus knot bridge does not generalize"

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
