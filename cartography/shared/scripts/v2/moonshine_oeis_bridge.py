"""
Moonshine OEIS Cross-Reference + Formula Scan
===============================================
Connects moonshine-related mathematics to the Prometheus cartography:

1. Identifies all moonshine-adjacent OEIS sequences (McKay-Thompson, mock theta,
   Eisenstein, j-function, umbral)
2. Extracts their coefficient patterns and cross-references with other OEIS sequences
3. Searches for structural bridges: sequences sharing coefficient subsequences
   with moonshine sequences
4. Connects to the formula corpus (OpenWebMath) for mock theta identities

Usage:
    python moonshine_oeis_bridge.py
"""

import json
import time
import re
from collections import defaultdict, Counter
from pathlib import Path
from math import gcd


# ─────────────────────────────────────────────────────────────────────────────
# Known moonshine-related OEIS sequences
# ─────────────────────────────────────────────────────────────────────────────

MOONSHINE_CORE = {
    # Monster moonshine (Monstrous)
    "A000521": {"name": "Klein j-function coefficients", "type": "monstrous", "group": "Monster"},
    "A007191": {"name": "McKay-Thompson T_2 for Monster", "type": "monstrous", "group": "Monster"},
    "A014708": {"name": "McKay-Thompson T_3 for Monster", "type": "monstrous", "group": "Monster"},
    "A007246": {"name": "McKay-Thompson T_5 for Monster", "type": "monstrous", "group": "Monster"},
    "A007267": {"name": "j-function expansion (1728*j)", "type": "monstrous", "group": "Monster"},

    # Modular forms / Eisenstein
    "A000594": {"name": "Ramanujan tau (Delta, weight 12)", "type": "modular", "weight": 12},
    "A006352": {"name": "Eisenstein E_2 coefficients", "type": "modular", "weight": 2},
    "A004009": {"name": "Eisenstein E_4 coefficients", "type": "modular", "weight": 4},
    "A013973": {"name": "Eisenstein E_6 coefficients", "type": "modular", "weight": 6},
    "A008410": {"name": "Eisenstein E_8 coefficients", "type": "modular", "weight": 8},
    "A013974": {"name": "Eisenstein E_10 coefficients", "type": "modular", "weight": 10},
    "A029829": {"name": "Eisenstein E_12 coefficients", "type": "modular", "weight": 12},

    # Mock theta / Umbral moonshine
    "A045488": {"name": "Ramanujan mock theta f(q)", "type": "mock_theta", "order": 3},
    "A001488": {"name": "Ramanujan mock theta 2nd order", "type": "mock_theta", "order": 2},
    "A053250": {"name": "Umbral moonshine M24", "type": "umbral", "group": "M24"},
    "A000118": {"name": "Representations as sum of 4 squares", "type": "theta", "formula": "theta_3^4"},
    "A008443": {"name": "Representations as sum of 8 triangular numbers", "type": "theta"},
    "A000122": {"name": "Jacobi theta_3 coefficients", "type": "theta"},

    # Lattice theta functions
    "A004011": {"name": "D_4 lattice theta", "type": "lattice_theta", "lattice": "D4"},
    "A008408": {"name": "E_8 lattice theta", "type": "lattice_theta", "lattice": "E8"},
    "A004027": {"name": "Leech lattice theta", "type": "lattice_theta", "lattice": "Leech"},
}

# Sequences to search for as bridge candidates
BRIDGE_KEYWORDS = [
    "moonshine", "mock theta", "mock modular", "niemeier", "monster group",
    "mckay-thompson", "mathieu", "leech lattice", "theta function",
    "modular form", "eisenstein series", "eta function", "dedekind eta",
    "partition function", "ramanujan", "j-function", "j-invariant",
    "weight 12", "cusp form", "siegel modular", "jacobi form",
]


def load_oeis_sequences(data_dir):
    """Load OEIS sequence terms from stripped file."""
    seqs = {}
    stripped_path = data_dir / "stripped_new.txt"
    with open(stripped_path, 'r', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or not line.startswith('A'):
                continue
            parts = line.split(',')
            seq_id = parts[0].strip().split()[0]  # "A000521 " -> "A000521"
            terms = []
            for t in parts[1:]:
                t = t.strip()
                if t:
                    try:
                        terms.append(int(t))
                    except:
                        pass
            if terms:
                seqs[seq_id] = terms
    return seqs


def load_oeis_names(data_dir):
    """Load OEIS sequence names."""
    names_path = data_dir / "oeis_names.json"
    try:
        with open(names_path, 'r', encoding='utf-8', errors='ignore') as f:
            return json.load(f)
    except:
        return {}


def load_oeis_crossrefs(data_dir):
    """Load OEIS cross-references."""
    xref_path = data_dir / "oeis_crossrefs.jsonl"
    xrefs = defaultdict(set)
    try:
        with open(xref_path, 'r', errors='ignore') as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    src = rec.get("source", "")
                    tgt = rec.get("target", "")
                    if src and tgt:
                        xrefs[src].add(tgt)
                        xrefs[tgt].add(src)
                except:
                    pass
    except:
        pass
    return xrefs


def subsequence_match(needle, haystack, min_len=5):
    """Check if needle appears as a contiguous subsequence of haystack."""
    if len(needle) < min_len:
        return False
    n = len(needle)
    for i in range(len(haystack) - n + 1):
        if haystack[i:i+n] == needle[:n]:
            return True
    return False


def fingerprint_sequence(terms, length=8):
    """Create a hashable fingerprint from first `length` nonzero terms."""
    nonzero = [t for t in terms if t != 0]
    if len(nonzero) < length:
        return None
    return tuple(nonzero[:length])


def main():
    data_dir = Path(__file__).resolve().parents[3] / "oeis" / "data"

    print("MOONSHINE OEIS CROSS-REFERENCE")
    print("=" * 72)
    print()

    # ─── Load OEIS data ───
    t0 = time.time()
    print("Loading OEIS sequences...")
    seqs = load_oeis_sequences(data_dir)
    print(f"  Loaded {len(seqs)} sequences in {time.time()-t0:.1f}s")

    print("Loading OEIS names...")
    names = load_oeis_names(data_dir)
    print(f"  Loaded {len(names)} names")

    print("Loading cross-references...")
    xrefs = load_oeis_crossrefs(data_dir)
    print(f"  Loaded xrefs for {len(xrefs)} sequences")
    print()

    # ─── Part 1: Identify moonshine core sequences ───
    print("=" * 72)
    print("PART 1: MOONSHINE CORE SEQUENCES")
    print("=" * 72)
    print()

    found_core = {}
    for seq_id, meta in MOONSHINE_CORE.items():
        if seq_id in seqs:
            terms = seqs[seq_id]
            found_core[seq_id] = terms
            print(f"  {seq_id}: {len(terms):>3} terms  {meta['name']}")
            print(f"    First 8: {terms[:8]}")
        else:
            print(f"  {seq_id}: MISSING  {meta['name']}")

    print(f"\nFound {len(found_core)}/{len(MOONSHINE_CORE)} core sequences")
    print()

    # ─── Part 2: Cross-reference network ───
    print("=" * 72)
    print("PART 2: MOONSHINE CROSS-REFERENCE NETWORK")
    print("=" * 72)
    print()

    # Build the moonshine neighborhood: sequences cross-referenced by core sequences
    neighborhood = defaultdict(set)  # seq_id -> set of core sequences that reference it
    for core_id in found_core:
        refs = xrefs.get(core_id, set())
        for ref in refs:
            if ref in seqs:
                neighborhood[ref].add(core_id)

    # Sort by number of connections to core
    ranked = sorted(neighborhood.items(), key=lambda x: -len(x[1]))
    print(f"Sequences in moonshine neighborhood (cross-referenced by core): {len(ranked)}")
    print()

    # Show top connections
    print("Top 30 most-connected to moonshine core:")
    for seq_id, cores in ranked[:30]:
        name = names.get(seq_id, "?")[:60]
        core_list = ", ".join(sorted(cores)[:5])
        print(f"  {seq_id}: {len(cores)} links  {name}")
        print(f"    Connected to: {core_list}")

    print()

    # ─── Part 3: Coefficient subsequence matching ───
    print("=" * 72)
    print("PART 3: COEFFICIENT SUBSEQUENCE BRIDGES")
    print("=" * 72)
    print()
    print("Searching for non-moonshine sequences that share coefficient")
    print("subsequences with moonshine core sequences...")
    print()

    # For each core sequence, find other sequences sharing a 6-term subsequence
    bridges = []
    core_ids = set(found_core.keys())

    for core_id, core_terms in found_core.items():
        if len(core_terms) < 6:
            continue

        # Create all 6-term windows from the core sequence
        windows = set()
        for i in range(len(core_terms) - 5):
            w = tuple(core_terms[i:i+6])
            if all(t == 0 for t in w):
                continue
            windows.add(w)

        # Search all sequences for these windows
        matches = []
        for seq_id, terms in seqs.items():
            if seq_id in core_ids:
                continue
            if len(terms) < 6:
                continue
            for i in range(len(terms) - 5):
                w = tuple(terms[i:i+6])
                if w in windows:
                    matches.append({
                        "core": core_id,
                        "match": seq_id,
                        "window": list(w),
                        "core_offset": core_terms.index(w[0]),
                        "match_offset": i,
                    })
                    break  # One match per sequence is enough

        if matches:
            meta = MOONSHINE_CORE[core_id]
            print(f"{core_id} ({meta['name']}): {len(matches)} bridges")
            for m in matches[:5]:
                name = names.get(m["match"], "?")[:50]
                print(f"  -> {m['match']}: {name}")
                print(f"     window: {m['window']} at offset {m['core_offset']}")
            if len(matches) > 5:
                print(f"  ... and {len(matches) - 5} more")
            bridges.extend(matches)

    print(f"\nTotal coefficient bridges found: {len(bridges)}")
    print()

    # ─── Part 4: Keyword search for moonshine-adjacent sequences ───
    print("=" * 72)
    print("PART 4: KEYWORD SEARCH FOR MOONSHINE-ADJACENT SEQUENCES")
    print("=" * 72)
    print()

    keyword_hits = defaultdict(list)
    for seq_id, name in names.items():
        nl = name.lower()
        for kw in BRIDGE_KEYWORDS:
            if kw in nl:
                keyword_hits[kw].append((seq_id, name))

    total_unique = set()
    for kw in sorted(keyword_hits.keys(), key=lambda k: -len(keyword_hits[k])):
        hits = keyword_hits[kw]
        unique_ids = set(h[0] for h in hits)
        total_unique.update(unique_ids)
        in_our_data = sum(1 for h in hits if h[0] in seqs)
        print(f"  \"{kw}\": {len(hits)} sequences ({in_our_data} with terms)")

    print(f"\nTotal unique moonshine-adjacent sequences: {len(total_unique)}")

    # How many of these are NOT in the core set?
    novel = total_unique - core_ids
    in_neighborhood = novel & set(neighborhood.keys())
    print(f"Novel (not core): {len(novel)}")
    print(f"Novel + in neighborhood: {len(in_neighborhood)}")
    print()

    # ─── Part 5: Structural summary ───
    print("=" * 72)
    print("STRUCTURAL SUMMARY")
    print("=" * 72)
    print()

    # Count by type
    type_counts = Counter()
    for meta in MOONSHINE_CORE.values():
        type_counts[meta.get("type", "unknown")] += 1

    print("Core sequence types:")
    for t, c in type_counts.most_common():
        print(f"  {t}: {c}")

    # Cross-domain bridges (sequences connected to moonshine but in different domains)
    print(f"\nMoonshine network:")
    print(f"  Core sequences: {len(found_core)}")
    print(f"  1-hop neighborhood: {len(neighborhood)}")
    print(f"  Coefficient bridges: {len(bridges)}")
    print(f"  Keyword-adjacent: {len(total_unique)}")

    # ─── Save results ───
    out = {
        "core_sequences": {k: {"terms": len(v), "meta": MOONSHINE_CORE[k]}
                           for k, v in found_core.items()},
        "neighborhood_size": len(neighborhood),
        "top_connections": [{
            "seq_id": sid,
            "n_core_links": len(cores),
            "name": names.get(sid, ""),
            "cores": list(cores),
        } for sid, cores in ranked[:50]],
        "coefficient_bridges": bridges[:100],
        "keyword_counts": {kw: len(hits) for kw, hits in keyword_hits.items()},
        "total_adjacent": len(total_unique),
    }

    out_path = Path(__file__).parent / "moonshine_oeis_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
