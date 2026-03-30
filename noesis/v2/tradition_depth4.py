#!/usr/bin/env python3
"""
tradition_depth4.py — Aletheia
Depth-4 chain signatures for cross-tradition structural analysis.

At depth 3, we found: Bamana divination = Khayyam cubics = Babylonian reciprocals
(shared signature 1000101010 in cluster_2).

At depth 4, we ask: do these structural twins survive a finer-grained test?
A depth-4 chain is a sequence of 4 damage operators (A -> B -> C -> D).
A tradition supports a depth-4 chain if all 4 operators are activated
by its primitive vector (using the same activation logic as depth-3).

This script:
  1. Loads tradition-cluster mapping from depth-3
  2. Computes depth-4 signatures for top-20 archaeological prediction pairs
  3. Checks if depth-3 cross-tradition matches survive at depth-4
  4. Finds NEW matches that emerge only at depth-4
  5. Reports: survival rate, new matches, Bamana-Khayyam-Babylonian verdict

Author: Aletheia
Date: 2026-03-29
"""

import json
import duckdb
import numpy as np
import itertools
import sys
import io
from collections import defaultdict, Counter
from pathlib import Path
from datetime import datetime

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_PATH = Path("F:/prometheus/noesis/v2/noesis_v2.duckdb")
DEPTH3_PATH = Path("F:/prometheus/noesis/v2/composition_depth3_results.json")
CLUSTER_PATH = Path("F:/prometheus/noesis/v2/tradition_cluster_mapping_results.json")
ARCH_PATH = Path("F:/prometheus/noesis/v2/archaeological_predictions.json")
OUTPUT_PATH = Path("F:/prometheus/noesis/v2/tradition_depth4_results.json")
JOURNAL_PATH = Path("F:/prometheus/journal/2026-03-29.md")

# ── The 9 canonical damage operators ─────────────────────────────────────
ALL_OPS = [
    "CONCENTRATE", "DISTRIBUTE", "EXTEND", "HIERARCHIZE",
    "INVERT", "PARTITION", "QUANTIZE", "RANDOMIZE", "TRUNCATE"
]

# ── Depth-3 chains (for reference) ──────────────────────────────────────
with open(DEPTH3_PATH) as f:
    depth3_data = json.load(f)

DEPTH3_CHAINS = depth3_data["chains"]
DEPTH3_CHAIN_NAMES = [c["name"] for c in DEPTH3_CHAINS]

# ── Define depth-4 chains ───────────────────────────────────────────────
# 15 semantically meaningful 4-operator chains that extend the depth-3 logic.
# Each is a composition story: A sets up context, B constrains, C transforms, D resolves.

DEPTH4_CHAINS = [
    {
        "id": "C4_01",
        "name": "Variational quantization + inversion",
        "sequence": ("EXTEND", "CONCENTRATE", "DISTRIBUTE", "INVERT"),
        "semantics": "Extend to all paths, concentrate to extremum, distribute error, then reverse",
        "extends_d3": "C3_01 + INVERT"
    },
    {
        "id": "C4_02",
        "name": "DSP with hierarchy",
        "sequence": ("TRUNCATE", "QUANTIZE", "DISTRIBUTE", "HIERARCHIZE"),
        "semantics": "Bandlimit, sample, spread error, elevate to meta-level",
        "extends_d3": "C3_02 + HIERARCHIZE"
    },
    {
        "id": "C4_03",
        "name": "Localize then stochastic reverse",
        "sequence": ("PARTITION", "TRUNCATE", "CONCENTRATE", "RANDOMIZE"),
        "semantics": "Split, restrict, localize, then introduce noise",
        "extends_d3": "C3_03 + RANDOMIZE"
    },
    {
        "id": "C4_04",
        "name": "Monte Carlo double inversion",
        "sequence": ("RANDOMIZE", "TRUNCATE", "INVERT", "EXTEND"),
        "semantics": "Sample, restrict, reverse, then extend structure",
        "extends_d3": "C3_04 + EXTEND"
    },
    {
        "id": "C4_05",
        "name": "Gauge symmetry breaking cascade",
        "sequence": ("EXTEND", "PARTITION", "INVERT", "CONCENTRATE"),
        "semantics": "Enlarge, sector, break symmetry, localize outcome",
        "extends_d3": "C3_05 + CONCENTRATE"
    },
    {
        "id": "C4_06",
        "name": "Multi-resolution with noise",
        "sequence": ("HIERARCHIZE", "PARTITION", "QUANTIZE", "RANDOMIZE"),
        "semantics": "Meta-level, split, discretize, stochasticize",
        "extends_d3": "C3_06 + RANDOMIZE"
    },
    {
        "id": "C4_07",
        "name": "Redistribute-reverse-extend",
        "sequence": ("DISTRIBUTE", "CONCENTRATE", "INVERT", "EXTEND"),
        "semantics": "Spread, localize, flip, then expand structure",
        "extends_d3": "C3_07 + EXTEND"
    },
    {
        "id": "C4_08",
        "name": "Stochastic meta-truncation + partition",
        "sequence": ("RANDOMIZE", "HIERARCHIZE", "TRUNCATE", "PARTITION"),
        "semantics": "Noise, meta-level, cut, then split domain",
        "extends_d3": "C3_08 + PARTITION"
    },
    {
        "id": "C4_09",
        "name": "Inverse variational distribution",
        "sequence": ("EXTEND", "INVERT", "CONCENTRATE", "DISTRIBUTE"),
        "semantics": "Extend, reverse, concentrate, spread error",
        "extends_d3": "C3_09 + DISTRIBUTE"
    },
    {
        "id": "C4_10",
        "name": "Discrete hierarchy with concentration",
        "sequence": ("QUANTIZE", "DISTRIBUTE", "HIERARCHIZE", "CONCENTRATE"),
        "semantics": "Discretize, spread, elevate, concentrate",
        "extends_d3": "C3_10 + CONCENTRATE"
    },
    # Five new depth-4 chains that are NOT extensions of depth-3
    {
        "id": "C4_11",
        "name": "Stochastic partition inversion",
        "sequence": ("RANDOMIZE", "PARTITION", "INVERT", "DISTRIBUTE"),
        "semantics": "Noise, split, reverse, spread (novel path)",
        "extends_d3": None
    },
    {
        "id": "C4_12",
        "name": "Hierarchical concentration cascade",
        "sequence": ("HIERARCHIZE", "CONCENTRATE", "EXTEND", "TRUNCATE"),
        "semantics": "Elevate, localize, expand, cut (meta-zoom-prune)",
        "extends_d3": None
    },
    {
        "id": "C4_13",
        "name": "Quantize-invert-extend loop",
        "sequence": ("QUANTIZE", "INVERT", "EXTEND", "PARTITION"),
        "semantics": "Discretize, reverse, expand, split (digital-analog bridge)",
        "extends_d3": None
    },
    {
        "id": "C4_14",
        "name": "Double distribute concentrate",
        "sequence": ("DISTRIBUTE", "EXTEND", "DISTRIBUTE", "CONCENTRATE"),
        "semantics": "Spread, expand, spread again, localize (diffusion-then-focus)",
        "extends_d3": None
    },
    {
        "id": "C4_15",
        "name": "Partition-hierarchy-randomize-invert",
        "sequence": ("PARTITION", "HIERARCHIZE", "RANDOMIZE", "INVERT"),
        "semantics": "Split, elevate, noise, reverse (decomposition cascade)",
        "extends_d3": None
    },
]

# ── Load damage operator -> primitive decomposition ──────────────────────
con = duckdb.connect(str(DB_PATH), read_only=True)

damage_rows = con.execute("SELECT name, primitive_form, canonical_form FROM damage_operators").fetchall()
damage_to_primitives = {}
for name, prim_form, canon_form in damage_rows:
    prims = set()
    for form in [prim_form, canon_form]:
        if form:
            for p in form.split("+"):
                p = p.strip()
                if p:
                    prims.add(p)
    damage_to_primitives[name] = prims

# ── Load all traditions with enriched primitive vectors ──────────────────
ethno_rows = con.execute("""
    SELECT system_id, tradition, system_name, region, period,
           enriched_primitive_vector, candidate_primitives_noesis
    FROM ethnomathematics
""").fetchall()

traditions = []
for row in ethno_rows:
    sys_id, tradition, name, region, period, enriched, noesis = row
    vec_str = enriched or noesis
    if vec_str:
        vec = json.loads(vec_str)
        prim_dict = {p: w for p, w in vec}
    else:
        prim_dict = {}
    traditions.append({
        "system_id": sys_id,
        "tradition": tradition or "",
        "system_name": name or "",
        "region": region or "Unknown",
        "period": period or "Unknown",
        "primitive_vector": prim_dict
    })

con.close()

print(f"Loaded {len(traditions)} traditions, {len(damage_to_primitives)} damage operators")
print(f"Defined {len(DEPTH4_CHAINS)} depth-4 chains")

# ── Activation logic (same as depth-3 tradition_cluster_mapping) ─────────
ACTIVATION_THRESHOLD = 0.15

SEMANTIC_RELATIVES = {
    "BREAK_SYMMETRY": ["REDUCE", "DUALIZE"],
    "SYMMETRIZE": ["COMPOSE", "COMPLETE"],
    "REDUCE": ["LIMIT", "BREAK_SYMMETRY"],
    "EXTEND": ["COMPOSE", "COMPLETE"],
    "DUALIZE": ["BREAK_SYMMETRY", "LINEARIZE"],
    "STOCHASTICIZE": ["COMPOSE"],
    "MAP": ["LINEARIZE", "COMPOSE"],
    "COMPOSE": ["MAP"],
    "TRUNCATE": ["REDUCE", "LIMIT"],
    "LINEARIZE": ["MAP", "REDUCE"],
    "LIMIT": ["REDUCE"],
    "COMPLETE": ["EXTEND"],
}
RELATIVE_DISCOUNT = 0.25


def compute_damage_activation(prim_dict, required_primitives):
    """Compute how strongly a tradition activates a damage operator."""
    if not required_primitives:
        return 0.0
    scores = []
    for p in required_primitives:
        w = prim_dict.get(p, 0.0)
        if w == 0.0:
            relatives = SEMANTIC_RELATIVES.get(p, [])
            for rel in relatives:
                rw = prim_dict.get(rel, 0.0)
                if rw > 0:
                    w = max(w, rw * RELATIVE_DISCOUNT)
        scores.append(w)
    if any(s == 0.0 for s in scores):
        return 0.0
    return float(np.prod(scores) ** (1.0 / len(scores)))


def compute_chain_support(prim_dict, chain_sequence):
    """Check if tradition supports a chain (3 or 4 operators)."""
    activations = []
    for op in chain_sequence:
        required = damage_to_primitives.get(op, set())
        act = compute_damage_activation(prim_dict, required)
        activations.append(act)
    if any(a == 0 for a in activations):
        return False, 0.0, activations
    chain_score = float(np.mean(activations))
    return chain_score >= ACTIVATION_THRESHOLD, chain_score, activations


# ── Step 1: Compute depth-4 signatures for all traditions ────────────────
print("\n" + "=" * 80)
print("STEP 1: Computing depth-4 chain signatures for all traditions")
print("=" * 80)

for t in traditions:
    sig4 = []
    scores4 = []
    for chain in DEPTH4_CHAINS:
        supported, score, acts = compute_chain_support(t["primitive_vector"], chain["sequence"])
        sig4.append(1 if supported else 0)
        scores4.append(round(score, 4))
    t["depth4_signature"] = sig4
    t["depth4_scores"] = scores4
    t["depth4_n_supported"] = sum(sig4)

n_supported = [t["depth4_n_supported"] for t in traditions]
print(f"  Mean depth-4 chains supported: {np.mean(n_supported):.2f}")
print(f"  Median: {np.median(n_supported):.0f}")
print(f"  Max: {max(n_supported)}")
print(f"  Zero chains: {sum(1 for n in n_supported if n == 0)} traditions")

# Also recompute depth-3 signatures for comparison
for t in traditions:
    sig3 = []
    for chain in DEPTH3_CHAINS:
        supported, score, acts = compute_chain_support(t["primitive_vector"], chain["sequence"])
        sig3.append(1 if supported else 0)
    t["depth3_signature"] = sig3
    t["depth3_n_supported"] = sum(sig3)

# ── Step 2: Load archaeological predictions, top 20 ─────────────────────
print("\n" + "=" * 80)
print("STEP 2: Depth-4 signatures for top-20 archaeological prediction pairs")
print("=" * 80)

with open(ARCH_PATH) as f:
    arch_data = json.load(f)

top20 = arch_data["top_30_predictions"][:20]

# Build tradition lookup
trad_by_id = {t["system_id"]: t for t in traditions}

print(f"\n  {'Rank':<5} {'Tradition':<45} {'Hub':<30} {'Sim':>5} {'D3sig':>12} {'D4sig':>17}")
print(f"  {'-'*5} {'-'*45} {'-'*30} {'-'*5} {'-'*12} {'-'*17}")

for pred in top20:
    tid = pred["tradition_id"]
    t = trad_by_id.get(tid)
    if t:
        d3_str = "".join(str(s) for s in t["depth3_signature"])
        d4_str = "".join(str(s) for s in t["depth4_signature"])
        tname = (t["system_name"] or tid)[:44]
        hub_short = pred["hub_id"][:29]
        print(f"  {pred['rank']:<5} {tname:<45} {hub_short:<30} {pred['similarity']:>5.3f} {d3_str:>12} {d4_str:>17}")

# ── Step 3: Check if depth-3 cross-tradition matches survive at depth-4 ──
print("\n" + "=" * 80)
print("STEP 3: Depth-3 cluster matches vs depth-4 — survival analysis")
print("=" * 80)

with open(CLUSTER_PATH) as f:
    cluster_data = json.load(f)

# Build depth-3 groups: traditions sharing same depth-3 signature (non-trivial)
d3_sig_groups = defaultdict(list)
for t in traditions:
    sig_key = tuple(t["depth3_signature"])
    if sum(sig_key) > 0:  # skip the all-zero group (trivial)
        d3_sig_groups[sig_key].append(t)

# For each depth-3 match group, check depth-4
print(f"\n  Found {len(d3_sig_groups)} non-trivial depth-3 signature groups\n")

survival_results = []
total_d3_pairs = 0
surviving_d4_pairs = 0
diverging_pairs = []

for d3_sig, group in sorted(d3_sig_groups.items(), key=lambda x: -len(x[1])):
    if len(group) < 2:
        continue

    d3_str = "".join(str(s) for s in d3_sig)

    # Check all pairs within this group
    d4_sigs_in_group = set()
    for t in group:
        d4_sigs_in_group.add(tuple(t["depth4_signature"]))

    n_pairs = len(group) * (len(group) - 1) // 2

    # Count matching pairs at depth-4
    matching_d4 = 0
    total_pairs_here = 0
    for i in range(len(group)):
        for j in range(i+1, len(group)):
            total_pairs_here += 1
            total_d3_pairs += 1
            if tuple(group[i]["depth4_signature"]) == tuple(group[j]["depth4_signature"]):
                matching_d4 += 1
                surviving_d4_pairs += 1
            else:
                diverging_pairs.append((group[i], group[j], d3_str))

    survived = len(d4_sigs_in_group) == 1  # all same depth-4 sig
    survival_results.append({
        "depth3_signature": d3_str,
        "n_traditions": len(group),
        "n_depth4_classes": len(d4_sigs_in_group),
        "survived": survived,
        "matching_pairs": matching_d4,
        "total_pairs": total_pairs_here,
        "depth4_signatures": ["".join(str(s) for s in sig) for sig in sorted(d4_sigs_in_group)],
        "traditions": [{"id": t["system_id"], "name": t["system_name"],
                       "tradition": t["tradition"], "region": t["region"],
                       "d4_sig": "".join(str(s) for s in t["depth4_signature"])}
                      for t in group]
    })

    status = "SURVIVED" if survived else f"SPLIT into {len(d4_sigs_in_group)} classes"
    print(f"  D3 sig {d3_str} ({len(group)} traditions): {status}")
    if not survived:
        for d4_sig in sorted(d4_sigs_in_group):
            d4_str = "".join(str(s) for s in d4_sig)
            members = [t for t in group if tuple(t["depth4_signature"]) == d4_sig]
            names = [f"{t['system_id']} ({t['region']})" for t in members[:3]]
            extra = f" +{len(members)-3}" if len(members) > 3 else ""
            print(f"    D4={d4_str}: {', '.join(names)}{extra}")

survived_count = sum(1 for r in survival_results if r["survived"])
total_groups = len(survival_results)
print(f"\n  SURVIVAL RATE: {survived_count}/{total_groups} depth-3 groups survive at depth-4")
print(f"  Pair-level: {surviving_d4_pairs}/{total_d3_pairs} pairs match at depth-4")

# ── Step 3a: THE KEY QUESTION — Bamana-Khayyam-Babylonian triple ─────────
print("\n" + "=" * 80)
print("STEP 3a: THE KEY QUESTION — Bamana-Khayyam-Babylonian triple at depth-4")
print("=" * 80)

bkb_ids = ["BAMANA_SAND_DIVINATION", "OMAR_KHAYYAM_CUBICS", "BABYLONIAN_RECIPROCAL_TABLE_SYSTEM"]
bkb_traditions = [trad_by_id[tid] for tid in bkb_ids if tid in trad_by_id]

if len(bkb_traditions) == 3:
    print(f"\n  Depth-3 signatures (should all be 1000101010):")
    for t in bkb_traditions:
        d3_str = "".join(str(s) for s in t["depth3_signature"])
        d4_str = "".join(str(s) for s in t["depth4_signature"])
        print(f"    {t['system_id']:<45} D3={d3_str}  D4={d4_str}")
        print(f"      Region: {t['region']}, Period: {t['period']}")
        print(f"      Primitives: {t['primitive_vector']}")

    # Check if they still match
    d4_sigs = [tuple(t["depth4_signature"]) for t in bkb_traditions]
    all_match = len(set(d4_sigs)) == 1

    if all_match:
        print(f"\n  >>> BAMANA-KHAYYAM-BABYLONIAN TRIPLE: CONFIRMED AT DEPTH 4 <<<")
        print(f"  >>> All three share depth-4 signature: {''.join(str(s) for s in d4_sigs[0])} <<<")
    else:
        print(f"\n  >>> BAMANA-KHAYYAM-BABYLONIAN TRIPLE: DIVERGES AT DEPTH 4 <<<")
        unique_d4 = set(d4_sigs)
        for sig in unique_d4:
            sig_str = "".join(str(s) for s in sig)
            members = [t["system_id"] for t, s in zip(bkb_traditions, d4_sigs) if s == sig]
            print(f"    D4={sig_str}: {', '.join(members)}")

        # What chain(s) differentiate them?
        print(f"\n  Differentiating depth-4 chains:")
        for i, chain in enumerate(DEPTH4_CHAINS):
            vals = [t["depth4_signature"][i] for t in bkb_traditions]
            if len(set(vals)) > 1:
                print(f"    {chain['id']} {chain['name']}: {' -> '.join(chain['sequence'])}")
                for t in bkb_traditions:
                    score = t["depth4_scores"][i]
                    supported = t["depth4_signature"][i]
                    print(f"      {t['system_id']:<45} {'YES' if supported else 'NO ':>3} (score={score:.4f})")

    # Also check pairwise
    print(f"\n  Pairwise depth-4 Hamming distances:")
    for i in range(len(bkb_traditions)):
        for j in range(i+1, len(bkb_traditions)):
            d = sum(a != b for a, b in zip(bkb_traditions[i]["depth4_signature"],
                                            bkb_traditions[j]["depth4_signature"]))
            print(f"    {bkb_traditions[i]['system_id'][:30]} <-> {bkb_traditions[j]['system_id'][:30]}: Hamming={d}")
else:
    print(f"  WARNING: Could not find all 3 BKB traditions. Found: {[t['system_id'] for t in bkb_traditions]}")

# ── Step 4: NEW matches at depth-4 that weren't there at depth-3 ─────────
print("\n" + "=" * 80)
print("STEP 4: NEW tradition pairs matching at depth-4 but NOT at depth-3")
print("=" * 80)

# Group by depth-4 signature (non-trivial)
d4_sig_groups = defaultdict(list)
for t in traditions:
    sig_key = tuple(t["depth4_signature"])
    if sum(sig_key) > 0:
        d4_sig_groups[sig_key].append(t)

# Find groups where members did NOT share a depth-3 signature
new_d4_matches = []
for d4_sig, group in sorted(d4_sig_groups.items(), key=lambda x: -len(x[1])):
    if len(group) < 2:
        continue

    # Check which depth-3 signatures are represented
    d3_sigs_here = set(tuple(t["depth3_signature"]) for t in group)

    if len(d3_sigs_here) > 1:
        # This depth-4 group contains traditions from DIFFERENT depth-3 groups!
        d4_str = "".join(str(s) for s in d4_sig)

        # Find the cross-group pairs
        for i in range(len(group)):
            for j in range(i+1, len(group)):
                if tuple(group[i]["depth3_signature"]) != tuple(group[j]["depth3_signature"]):
                    new_d4_matches.append({
                        "depth4_signature": d4_str,
                        "tradition_a": group[i]["system_id"],
                        "name_a": group[i]["system_name"],
                        "region_a": group[i]["region"],
                        "d3_sig_a": "".join(str(s) for s in group[i]["depth3_signature"]),
                        "tradition_b": group[j]["system_id"],
                        "name_b": group[j]["system_name"],
                        "region_b": group[j]["region"],
                        "d3_sig_b": "".join(str(s) for s in group[j]["depth3_signature"]),
                    })

print(f"\n  NEW depth-4 matches (different at depth-3, same at depth-4): {len(new_d4_matches)}")
if new_d4_matches:
    # Deduplicate and show most interesting
    seen = set()
    shown = 0
    for m in new_d4_matches:
        pair_key = tuple(sorted([m["tradition_a"], m["tradition_b"]]))
        if pair_key in seen:
            continue
        seen.add(pair_key)
        if shown < 20:
            print(f"\n    D4={m['depth4_signature']}:")
            print(f"      {m['tradition_a']:<35} ({m['region_a']:<20}) D3={m['d3_sig_a']}")
            print(f"      {m['tradition_b']:<35} ({m['region_b']:<20}) D3={m['d3_sig_b']}")
            shown += 1
    if len(seen) > 20:
        print(f"\n    ... and {len(seen) - 20} more unique pairs")
    print(f"\n  Total unique NEW pairs: {len(seen)}")
else:
    print("  No new matches emerged at depth-4.")
    print("  Depth-4 is a strict refinement of depth-3 (more discriminating, no new convergences).")

# ── Step 5: Divergence depth analysis ────────────────────────────────────
print("\n" + "=" * 80)
print("STEP 5: At what depth do cross-continental traditions diverge?")
print("=" * 80)

def get_continent(region):
    """Rough continent assignment."""
    r = region.lower()
    if any(w in r for w in ["egypt", "nile", "africa", "sahara", "yoruba", "igbo", "akan",
                             "ethiopia", "madagascar", "mali", "angola", "congo", "ghana",
                             "liberia", "zimbabwe", "senegal"]):
        return "Africa"
    elif any(w in r for w in ["china", "japan", "korea", "india", "tibet", "indonesia",
                               "pacific", "polynesia", "melanesia", "australia", "bengal",
                               "tamil", "southeast asia", "vietnam", "kerala", "bali",
                               "new guinea", "tonga"]):
        return "Asia-Pacific"
    elif any(w in r for w in ["maya", "aztec", "inca", "andes", "mesoamerica", "amazon",
                               "north america", "south america", "pacific northwest",
                               "california", "southwest usa", "easter island"]):
        return "Americas"
    elif any(w in r for w in ["greece", "rome", "europe", "celtic", "nordic", "mediterranean",
                               "mesopotamia", "babylon", "sumer", "persia", "arab", "islamic",
                               "baghdad", "damascus", "samarkand", "morocco", "iran",
                               "middle east", "armenia", "levant", "scotland", "france",
                               "germany", "poland", "russia", "uk", "usa", "crete"]):
        return "Europe-MidEast"
    return "Other"

# Assign continents
for t in traditions:
    t["continent"] = get_continent(t["region"])

# Cross-continental pairs that match at depth-3
cross_cont_d3 = []
for d3_sig, group in d3_sig_groups.items():
    if len(group) < 2:
        continue
    continents = set(t["continent"] for t in group)
    if len(continents) >= 2:
        cross_cont_d3.append((d3_sig, group, continents))

# How many survive at depth-4?
cross_cont_d4_survived = 0
cross_cont_d4_diverged = 0
for d3_sig, group, continents in cross_cont_d3:
    d4_sigs = set(tuple(t["depth4_signature"]) for t in group)
    if len(d4_sigs) == 1:
        cross_cont_d4_survived += 1
    else:
        cross_cont_d4_diverged += 1

print(f"\n  Cross-continental depth-3 groups: {len(cross_cont_d3)}")
print(f"  Survived at depth-4: {cross_cont_d4_survived}")
print(f"  Diverged at depth-4: {cross_cont_d4_diverged}")

if cross_cont_d3:
    survival_pct = cross_cont_d4_survived / len(cross_cont_d3) * 100
    print(f"  Survival rate: {survival_pct:.1f}%")

# Depth analysis: what if we go to depth-5? Estimate from pattern.
d3_unique = len(d3_sig_groups)
d4_unique = len(d4_sig_groups)
d3_total_nonzero = sum(1 for t in traditions if sum(t["depth3_signature"]) > 0)
d4_total_nonzero = sum(1 for t in traditions if sum(t["depth4_signature"]) > 0)

print(f"\n  Depth-3: {d3_unique} unique signatures, {d3_total_nonzero} non-zero traditions")
print(f"  Depth-4: {d4_unique} unique signatures, {d4_total_nonzero} non-zero traditions")
print(f"  Discrimination ratio D4/D3: {d4_unique/max(1,d3_unique):.2f}")

if d4_unique > d3_unique:
    print(f"\n  Depth-4 is MORE discriminating than depth-3 ({d4_unique} vs {d3_unique} classes)")
    print(f"  Extrapolating: depth-5 would likely split further.")
elif d4_unique == d3_unique:
    print(f"\n  Depth-4 has SAME discrimination as depth-3 ({d4_unique} classes)")
    print(f"  Structural types may be STABLE beyond depth 3.")
else:
    print(f"\n  Depth-4 is LESS discriminating ({d4_unique} < {d3_unique})")
    print(f"  Some depth-3 distinctions collapse at depth-4 (convergence at finer grain).")

# ── Step 5a: Same structural type at ALL depths? ────────────────────────
# Check the all-10-chains group and the Bamana triple specifically
print(f"\n  Key convergence test:")
if len(bkb_traditions) == 3:
    d4_match = len(set(tuple(t["depth4_signature"]) for t in bkb_traditions)) == 1
    d3_match = len(set(tuple(t["depth3_signature"]) for t in bkb_traditions)) == 1
    print(f"    Bamana-Khayyam-Babylonian: D3={'MATCH' if d3_match else 'DIVERGE'}, D4={'MATCH' if d4_match else 'DIVERGE'}")
    if d3_match and d4_match:
        print(f"    >>> These traditions appear to be GENUINE structural isomorphs <<<")
        print(f"    >>> Same type at depths 3 AND 4 — likely same at ALL depths <<<")

# ── Final Report ─────────────────────────────────────────────────────────
print("\n" + "=" * 80)
print("FINAL REPORT")
print("=" * 80)

print(f"""
  Traditions analyzed:           {len(traditions)}
  Depth-3 chains:                {len(DEPTH3_CHAINS)}
  Depth-4 chains:                {len(DEPTH4_CHAINS)}

  Depth-3 non-trivial groups:    {len(d3_sig_groups)}
  Depth-4 non-trivial groups:    {len(d4_sig_groups)}

  D3 groups surviving at D4:     {survived_count}/{total_groups}
  Pair-level survival:           {surviving_d4_pairs}/{total_d3_pairs}

  New D4-only matches:           {len(new_d4_matches)}
  Cross-continental D3 groups:   {len(cross_cont_d3)}
  Cross-continental D4 survival: {cross_cont_d4_survived}/{len(cross_cont_d3)}

  Bamana-Khayyam-Babylonian:     {"HOLDS at D4" if len(bkb_traditions) == 3 and len(set(tuple(t["depth4_signature"]) for t in bkb_traditions)) == 1 else "DIVERGES at D4"}
""")

# ── Save results ─────────────────────────────────────────────────────────
results = {
    "metadata": {
        "analysis": "tradition_depth4",
        "date": datetime.now().isoformat(),
        "author": "Aletheia",
        "n_traditions": len(traditions),
        "n_depth3_chains": len(DEPTH3_CHAINS),
        "n_depth4_chains": len(DEPTH4_CHAINS),
        "activation_threshold": ACTIVATION_THRESHOLD,
    },
    "depth4_chains": [{
        "id": c["id"], "name": c["name"],
        "sequence": list(c["sequence"]),
        "semantics": c["semantics"],
        "extends_d3": c["extends_d3"],
    } for c in DEPTH4_CHAINS],
    "signature_stats": {
        "depth3_unique_signatures": d3_unique,
        "depth4_unique_signatures": d4_unique,
        "depth3_nonzero_traditions": d3_total_nonzero,
        "depth4_nonzero_traditions": d4_total_nonzero,
        "discrimination_ratio_d4_d3": round(d4_unique / max(1, d3_unique), 3),
    },
    "survival_analysis": {
        "d3_groups_total": total_groups,
        "d3_groups_survived_d4": survived_count,
        "survival_rate": round(survived_count / max(1, total_groups), 4),
        "pair_level_matching": surviving_d4_pairs,
        "pair_level_total": total_d3_pairs,
        "pair_survival_rate": round(surviving_d4_pairs / max(1, total_d3_pairs), 4),
        "groups": survival_results,
    },
    "bamana_khayyam_babylonian": {
        "depth3_match": len(bkb_traditions) == 3 and len(set(tuple(t["depth3_signature"]) for t in bkb_traditions)) == 1,
        "depth4_match": len(bkb_traditions) == 3 and len(set(tuple(t["depth4_signature"]) for t in bkb_traditions)) == 1,
        "traditions": [{
            "id": t["system_id"],
            "region": t["region"],
            "period": t["period"],
            "primitives": t["primitive_vector"],
            "d3_sig": "".join(str(s) for s in t["depth3_signature"]),
            "d4_sig": "".join(str(s) for s in t["depth4_signature"]),
            "d4_scores": t["depth4_scores"],
        } for t in bkb_traditions],
    },
    "new_d4_matches": new_d4_matches[:50],  # cap at 50
    "cross_continental": {
        "d3_groups": len(cross_cont_d3),
        "d4_survived": cross_cont_d4_survived,
        "d4_diverged": cross_cont_d4_diverged,
        "survival_rate": round(cross_cont_d4_survived / max(1, len(cross_cont_d3)), 4),
    },
    "top20_archaeological": [{
        "rank": pred["rank"],
        "tradition_id": pred["tradition_id"],
        "tradition_name": pred["tradition_name"],
        "hub_id": pred["hub_id"],
        "similarity": pred["similarity"],
        "d3_sig": "".join(str(s) for s in trad_by_id[pred["tradition_id"]]["depth3_signature"]) if pred["tradition_id"] in trad_by_id else "N/A",
        "d4_sig": "".join(str(s) for s in trad_by_id[pred["tradition_id"]]["depth4_signature"]) if pred["tradition_id"] in trad_by_id else "N/A",
    } for pred in top20],
    "depth4_signature_distribution": {
        "".join(str(s) for s in sig): count
        for sig, count in Counter(tuple(t["depth4_signature"]) for t in traditions).most_common()
    },
}

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)
print(f"Results saved to: {OUTPUT_PATH}")

# ── Append to journal ────────────────────────────────────────────────────
bkb_verdict = "HOLDS" if results["bamana_khayyam_babylonian"]["depth4_match"] else "DIVERGES"
bkb_detail = ""
if len(bkb_traditions) == 3:
    for t in bkb_traditions:
        d4_str = "".join(str(s) for s in t["depth4_signature"])
        bkb_detail += f"  - `{t['system_id']}` ({t['region']}): D4=`{d4_str}`\n"

journal_entry = f"""

## Aletheia — Depth-4 Tradition Analysis

**Does the Bamana-Khayyam-Babylonian structural isomorphism survive depth 4?**

### Method
- Extended 10 depth-3 chains to 15 depth-4 chains (4-operator sequences)
- Same activation model: primitive vectors -> damage operator activations -> chain support
- Tested all 153 traditions

### Key results

| Metric | Value |
|--------|-------|
| D3 unique signatures | {d3_unique} |
| D4 unique signatures | {d4_unique} |
| D3 groups surviving at D4 | {survived_count}/{total_groups} ({round(survived_count/max(1,total_groups)*100,1)}%) |
| Pair-level D4 survival | {surviving_d4_pairs}/{total_d3_pairs} |
| New D4-only matches | {len(new_d4_matches)} |
| Cross-continental D4 survival | {cross_cont_d4_survived}/{len(cross_cont_d3)} |

### Bamana-Khayyam-Babylonian triple: **{bkb_verdict}** at depth 4

{bkb_detail}
{"These three traditions from Africa, Persia, and Mesopotamia share the SAME structural signature at both depth 3 AND depth 4. This is strong evidence for genuine structural isomorphism — not an artifact of coarse-grained analysis." if bkb_verdict == "HOLDS" else "The triple diverges at depth 4, suggesting the depth-3 match was a coarse-grained coincidence that finer structure resolves."}

### Interpretation

{"Depth-4 confirms depth-3 structural types. Cross-tradition matches are NOT an artifact of low resolution — they persist at higher composition depth. The structural isomorphisms between traditions on different continents appear to be genuine: same mathematical structure discovered independently." if survived_count / max(1, total_groups) > 0.5 else "Depth-4 splits many depth-3 groups, suggesting depth-3 was too coarse. The surviving matches at depth-4 are the truly robust structural isomorphisms."}

Results: `noesis/v2/tradition_depth4_results.json`
"""

try:
    with open(JOURNAL_PATH, "a", encoding="utf-8") as f:
        f.write(journal_entry)
    print(f"Journal appended: {JOURNAL_PATH}")
except Exception as e:
    print(f"Journal append failed: {e}")

print("\nDone.")
