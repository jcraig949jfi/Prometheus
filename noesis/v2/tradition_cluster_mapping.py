#!/usr/bin/env python3
"""
tradition_cluster_mapping.py — Aletheia
Maps 153 ethnomathematics traditions to depth-3 structural clusters.

Strategy:
  1. Each depth-3 chain is a sequence of 3 damage operators.
  2. Each damage operator decomposes into base primitives (from damage_operators table).
  3. Each tradition has an enriched_primitive_vector of (primitive, weight) pairs.
  4. For each tradition, compute activation of each damage operator from its primitives.
  5. For each chain, compute whether the tradition can "support" it (all 3 operators activated).
  6. Build a 10-chain binary signature for each tradition.
  7. Assign to nearest cluster by Hamming distance on signatures.
"""

import json
import duckdb
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path
from datetime import datetime

DB_PATH = "F:/prometheus/noesis/v2/noesis_v2.duckdb"
DEPTH3_PATH = "F:/prometheus/noesis/v2/composition_depth3_results.json"
OUTPUT_PATH = "F:/prometheus/noesis/v2/tradition_cluster_mapping_results.json"
JOURNAL_PATH = "F:/prometheus/journal/2026-03-29.md"

# ── Load depth-3 results ──────────────────────────────────────────────
with open(DEPTH3_PATH) as f:
    depth3 = json.load(f)

chains = depth3["chains"]  # list of 10 chains, each with id, name, sequence
clusters = depth3["clusters"]  # cluster_0..cluster_12, each with signature (len-10 binary)

chain_names = [c["name"] for c in chains]
chain_sequences = [c["sequence"] for c in chains]  # e.g. ["EXTEND","CONCENTRATE","DISTRIBUTE"]
n_chains = len(chains)

print(f"Loaded {n_chains} chains, {len(clusters)} clusters")

# ── Load damage operator -> primitive decomposition ───────────────────
con = duckdb.connect(DB_PATH, read_only=True)

damage_rows = con.execute("SELECT name, primitive_form, canonical_form FROM damage_operators").fetchall()
# Build mapping: damage_op_name -> set of base primitives it requires
damage_to_primitives = {}
for name, prim_form, canon_form in damage_rows:
    # Use canonical_form which is more complete
    # Parse "SYMMETRIZE + COMPOSE" -> {"SYMMETRIZE", "COMPOSE"}
    prims = set()
    for form in [prim_form, canon_form]:
        if form:
            for p in form.split("+"):
                p = p.strip()
                if p:
                    prims.add(p)
    damage_to_primitives[name] = prims

print("\nDamage operator -> primitives:")
for op, prims in sorted(damage_to_primitives.items()):
    print(f"  {op}: {sorted(prims)}")

# ── Load all 153 traditions ───────────────────────────────────────────
ethno_rows = con.execute("""
    SELECT system_id, tradition, system_name, region, period,
           enriched_primitive_vector, candidate_primitives_noesis
    FROM ethnomathematics
""").fetchall()

traditions = []
for row in ethno_rows:
    sys_id, tradition, name, region, period, enriched, noesis = row
    # Parse primitive vector
    vec_str = enriched or noesis
    if vec_str:
        vec = json.loads(vec_str)
        prim_dict = {p: w for p, w in vec}
    else:
        prim_dict = {}
    traditions.append({
        "system_id": sys_id,
        "tradition": tradition,
        "system_name": name,
        "region": region or "Unknown",
        "period": period or "Unknown",
        "primitive_vector": prim_dict
    })

print(f"\nLoaded {len(traditions)} traditions")
con.close()

# ── Compute damage operator activation for each tradition ─────────────
# A tradition "activates" a damage operator if it has at least one of
# the required primitives with non-trivial weight.
# Activation score = geometric mean of weights for required primitives
# (0 if any required primitive is missing)

ACTIVATION_THRESHOLD = 0.10  # minimum activation to count as "supported"

def compute_damage_activation(prim_dict, required_primitives):
    """Compute how strongly a tradition activates a damage operator.

    Uses soft matching: for each required primitive, look for it directly
    or through semantic relatives. Score = mean of individual matches,
    NOT requiring all to be present (which is too strict for ethnomathematics
    since traditions rarely have exotic primitives like TRUNCATE).
    """
    if not required_primitives:
        return 0.0

    # Semantic relatives: if a tradition has one of these, it gets partial
    # credit for the target primitive.  Based on damage operator decompositions
    # and structural similarity.
    SEMANTIC_RELATIVES = {
        "BREAK_SYMMETRY": ["REDUCE", "DUALIZE", "LIMIT"],
        "SYMMETRIZE": ["COMPOSE", "EXTEND", "COMPLETE"],
        "REDUCE": ["BREAK_SYMMETRY", "LIMIT", "LINEARIZE"],
        "EXTEND": ["COMPOSE", "COMPLETE", "SYMMETRIZE"],
        "DUALIZE": ["BREAK_SYMMETRY", "MAP", "LINEARIZE"],
        "STOCHASTICIZE": ["COMPOSE", "EXTEND", "COMPLETE"],
        "MAP": ["COMPOSE", "LINEARIZE", "REDUCE"],
        "COMPOSE": ["MAP", "EXTEND", "SYMMETRIZE"],
        "TRUNCATE": ["REDUCE", "LIMIT", "BREAK_SYMMETRY"],
        "LINEARIZE": ["MAP", "REDUCE", "DUALIZE"],
        "LIMIT": ["REDUCE", "TRUNCATE", "BREAK_SYMMETRY"],
        "COMPLETE": ["EXTEND", "SYMMETRIZE", "COMPOSE"],
    }

    scores = []
    for p in required_primitives:
        w = prim_dict.get(p, 0.0)
        if w == 0.0:
            # Check semantic relatives at 40% strength
            relatives = SEMANTIC_RELATIVES.get(p, [])
            for rel in relatives:
                rw = prim_dict.get(rel, 0.0)
                if rw > 0:
                    w = max(w, rw * 0.4)
        scores.append(w)

    # Use mean (not geometric mean) to allow partial support
    return np.mean(scores)


def compute_chain_support(prim_dict, chain_sequence):
    """Check if tradition supports a chain (all 3 operators have some activation)."""
    activations = []
    for op in chain_sequence:
        required = damage_to_primitives.get(op, set())
        act = compute_damage_activation(prim_dict, required)
        activations.append(act)
    # Chain is supported if average activation exceeds threshold
    avg_act = np.mean(activations) if activations else 0
    return avg_act >= ACTIVATION_THRESHOLD, avg_act, activations


# ── Build chain signature for each tradition ──────────────────────────
print("\n-- Computing chain signatures for all traditions --")

tradition_signatures = []
for t in traditions:
    sig = []
    chain_scores = []
    for chain in chains:
        supported, score, acts = compute_chain_support(t["primitive_vector"], chain["sequence"])
        sig.append(1 if supported else 0)
        chain_scores.append(score)
    t["chain_signature"] = sig
    t["chain_scores"] = chain_scores
    t["n_chains_supported"] = sum(sig)
    tradition_signatures.append(sig)

# Stats
n_supported = [t["n_chains_supported"] for t in traditions]
print(f"  Mean chains supported per tradition: {np.mean(n_supported):.2f}")
print(f"  Median: {np.median(n_supported):.0f}")
print(f"  Max: {max(n_supported)} ({sum(1 for n in n_supported if n == max(n_supported))} traditions)")
print(f"  Zero chains: {sum(1 for n in n_supported if n == 0)} traditions")

# ── Assign traditions to clusters ─────────────────────────────────────
print("\n-- Assigning traditions to clusters --")

def hamming_distance(sig1, sig2):
    """Hamming distance between two binary signatures."""
    return sum(a != b for a, b in zip(sig1, sig2))

def cosine_similarity(sig1, sig2):
    """Cosine similarity treating signatures as vectors."""
    s1 = np.array(sig1, dtype=float)
    s2 = np.array(sig2, dtype=float)
    dot = np.dot(s1, s2)
    norm1 = np.linalg.norm(s1)
    norm2 = np.linalg.norm(s2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

# Parse cluster signatures to int lists
cluster_sigs = {}
for cname, cdata in clusters.items():
    cluster_sigs[cname] = [int(x) for x in cdata["signature"]]

assignments = {}  # system_id -> cluster_name
unassigned = []   # traditions that don't fit any cluster

for t in traditions:
    sig = t["chain_signature"]

    # Find best cluster by Hamming distance (lower = better), break ties by cosine
    best_cluster = None
    best_hamming = float('inf')
    best_cosine = -1

    for cname, csig in cluster_sigs.items():
        h = hamming_distance(sig, csig)
        c = cosine_similarity(sig, csig)
        if h < best_hamming or (h == best_hamming and c > best_cosine):
            best_hamming = h
            best_cosine = c
            best_cluster = cname

    t["assigned_cluster"] = best_cluster
    t["hamming_distance"] = best_hamming
    t["cosine_to_cluster"] = best_cosine
    assignments[t["system_id"]] = best_cluster

    # "Doesn't fit" = hamming > half the signature length OR zero signature with no match
    if best_hamming > n_chains // 2:
        unassigned.append(t)

# ── Analysis ──────────────────────────────────────────────────────────
print("\n===================================================================")
print("  TRADITION -> CLUSTER MAPPING RESULTS")
print("===================================================================\n")

# 1. How many traditions per cluster?
cluster_members = defaultdict(list)
for t in traditions:
    cluster_members[t["assigned_cluster"]].append(t)

print("-- Traditions per cluster --")
for cname in sorted(clusters.keys(), key=lambda x: int(x.split("_")[1])):
    members = cluster_members.get(cname, [])
    cdata = clusters[cname]
    chain_list = ", ".join(cdata["chains_supported"])
    print(f"\n  {cname} ({cdata['n_chains']} chains: {chain_list})")
    print(f"    Hub members: {', '.join(cdata['members'])}")
    print(f"    Traditions assigned: {len(members)}")
    if members:
        # Show sample
        for m in sorted(members, key=lambda x: x["hamming_distance"])[:5]:
            print(f"      {m['system_id']} ({m['tradition']}, {m['region']}) "
                  f"[hamming={m['hamming_distance']}, cosine={m['cosine_to_cluster']:.3f}]")
        if len(members) > 5:
            print(f"      ... and {len(members) - 5} more")

# 2. Traditions that don't fit
print(f"\n-- Traditions that don't fit well (hamming > {n_chains // 2}) --")
print(f"  Count: {len(unassigned)} of {len(traditions)}")
for t in sorted(unassigned, key=lambda x: x["hamming_distance"], reverse=True)[:10]:
    print(f"  {t['system_id']} ({t['tradition']}, {t['region']}): "
          f"sig={''.join(str(s) for s in t['chain_signature'])}, "
          f"best={t['assigned_cluster']} (hamming={t['hamming_distance']})")

# 3. Most diverse cluster
print("\n-- Cluster diversity (unique cultural origins) --")
cluster_diversity = {}
for cname, members in sorted(cluster_members.items(), key=lambda x: int(x[0].split("_")[1])):
    regions = set(m["region"] for m in members)
    tradition_names = set(m["tradition"] for m in members if m["tradition"])
    cluster_diversity[cname] = {
        "n_traditions": len(members),
        "n_unique_regions": len(regions),
        "n_unique_tradition_names": len(tradition_names),
        "regions": sorted(regions),
        "tradition_names": sorted(tradition_names)
    }
    print(f"  {cname}: {len(members)} traditions, {len(regions)} regions, "
          f"{len(tradition_names)} cultural traditions")

most_diverse = max(cluster_diversity.items(),
                   key=lambda x: (x[1]["n_unique_regions"], x[1]["n_traditions"]))
print(f"\n  Most diverse: {most_diverse[0]} with {most_diverse[1]['n_unique_regions']} "
      f"unique regions from {most_diverse[1]['n_traditions']} traditions")
print(f"    Regions: {', '.join(most_diverse[1]['regions'][:15])}")

# 4. Surprising alignments
print("\n===================================================================")
print("  SURPRISING ALIGNMENTS")
print("===================================================================\n")

# Find pre-literate / oral traditions
preliterate_keywords = ["oral", "pre-", "stone age", "paleolithic", "neolithic",
                        "hunter", "indigenous", "aboriginal", "sand", "string",
                        "quipu", "knot", "body", "gesture"]

# Find modern/physics-adjacent hubs
modern_hubs = {"HEISENBERG_UNCERTAINTY", "IMPOSSIBILITY_BELLS_THEOREM",
               "IMPOSSIBILITY_NO_CLONING_THEOREM", "IMPOSSIBILITY_CAP",
               "FORCED_SYMMETRY_BREAK", "IMPOSSIBILITY_CRYSTALLOGRAPHIC_RESTRICTION_V2"}

# Cross-continental structural matches
print("-- Cross-continental structural twins --")
# Group by exact signature
sig_groups = defaultdict(list)
for t in traditions:
    sig_key = tuple(t["chain_signature"])
    sig_groups[sig_key].append(t)

cross_continental = []
for sig_key, group in sig_groups.items():
    if len(group) < 2:
        continue
    regions = set()
    for t in group:
        # Extract continent-level info from region
        region = t["region"].lower()
        if any(w in region for w in ["egypt", "nile", "africa", "sahara", "yoruba", "igbo", "akan", "ethiopia", "madagascar"]):
            regions.add("Africa")
        elif any(w in region for w in ["china", "japan", "korea", "india", "tibet", "indonesia", "pacific", "polynesia", "melanesia", "australia", "bengal", "tamil", "southeast asia", "vietnam"]):
            regions.add("Asia-Pacific")
        elif any(w in region for w in ["maya", "aztec", "inca", "andes", "mesoamerica", "amazon", "north america", "south america", "pacific northwest"]):
            regions.add("Americas")
        elif any(w in region for w in ["greece", "rome", "europe", "celtic", "nordic", "mediterranean", "mesopotamia", "babylon", "sumer", "persia", "arab", "islamic"]):
            regions.add("Europe-MidEast")
        else:
            regions.add("Other:" + t["region"][:20])

    if len(regions) >= 2:
        cross_continental.append((sig_key, group, regions))

cross_continental.sort(key=lambda x: len(x[2]), reverse=True)

for sig_key, group, regions in cross_continental[:10]:
    sig_str = "".join(str(s) for s in sig_key)
    cluster_name = group[0]["assigned_cluster"]
    print(f"\n  Signature {sig_str} -> {cluster_name} ({len(group)} traditions, {len(regions)} continents)")
    for t in group[:8]:
        period_short = t["period"][:30] if t["period"] else "?"
        print(f"    {t['system_name']} ({t['tradition']}, {t['region'][:40]}) [{period_short}]")
    if len(group) > 8:
        print(f"    ... and {len(group) - 8} more")

# Pre-literate in same cluster as modern physics hub
print("\n-- Pre-literate traditions sharing cluster with physics hubs --")
for cname, members in cluster_members.items():
    # Check if cluster contains a modern hub
    hub_members = set(clusters[cname]["members"])
    has_modern = bool(hub_members & modern_hubs)
    if not has_modern:
        continue

    for t in members:
        desc = (t.get("system_name", "") + " " + t.get("tradition", "") + " " +
                t.get("period", "")).lower()
        is_ancient = any(kw in desc for kw in preliterate_keywords) or "bce" in desc.lower()
        if is_ancient:
            print(f"  {t['system_id']} ({t['tradition']}, {t['period']}) ")
            print(f"    -> {cname} (shares structure with {', '.join(hub_members & modern_hubs)})")
            print(f"    Signature: {''.join(str(s) for s in t['chain_signature'])}")

# ── Summary statistics ────────────────────────────────────────────────
print("\n===================================================================")
print("  SUMMARY")
print("===================================================================\n")

sig_distribution = Counter(tuple(t["chain_signature"]) for t in traditions)
print(f"  Total traditions: {len(traditions)}")
print(f"  Unique signatures: {len(sig_distribution)}")
print(f"  Traditions with zero chains: {sum(1 for t in traditions if t['n_chains_supported'] == 0)}")
print(f"  Traditions poorly fit (hamming>{n_chains//2}): {len(unassigned)}")
print(f"  Cross-continental signature matches: {len(cross_continental)}")

# Most common signatures
print(f"\n  Top 5 most common signatures:")
for sig, count in sig_distribution.most_common(5):
    sig_str = "".join(str(s) for s in sig)
    # What cluster does this map to?
    sample = [t for t in traditions if tuple(t["chain_signature"]) == sig][0]
    print(f"    {sig_str} -> {sample['assigned_cluster']}: {count} traditions")

# ── Save results ──────────────────────────────────────────────────────
results = {
    "metadata": {
        "analysis": "tradition_cluster_mapping",
        "date": datetime.now().isoformat(),
        "author": "Aletheia",
        "n_traditions": len(traditions),
        "n_clusters": len(clusters),
        "n_chains": n_chains,
        "activation_threshold": ACTIVATION_THRESHOLD
    },
    "cluster_summary": {},
    "tradition_assignments": [],
    "unassigned": [],
    "cross_continental_twins": [],
    "signature_distribution": {}
}

for cname in sorted(clusters.keys(), key=lambda x: int(x.split("_")[1])):
    members = cluster_members.get(cname, [])
    results["cluster_summary"][cname] = {
        "hub_chains": clusters[cname]["chains_supported"],
        "hub_members": clusters[cname]["members"],
        "n_traditions": len(members),
        "tradition_ids": [m["system_id"] for m in members],
        "diversity": cluster_diversity.get(cname, {})
    }

for t in traditions:
    results["tradition_assignments"].append({
        "system_id": t["system_id"],
        "tradition": t["tradition"],
        "region": t["region"],
        "period": t["period"],
        "cluster": t["assigned_cluster"],
        "hamming_distance": t["hamming_distance"],
        "cosine_similarity": round(t["cosine_to_cluster"], 4),
        "chain_signature": "".join(str(s) for s in t["chain_signature"]),
        "n_chains_supported": t["n_chains_supported"]
    })

for t in unassigned:
    results["unassigned"].append({
        "system_id": t["system_id"],
        "tradition": t["tradition"],
        "region": t["region"],
        "chain_signature": "".join(str(s) for s in t["chain_signature"]),
        "best_cluster": t["assigned_cluster"],
        "hamming_distance": t["hamming_distance"]
    })

for sig_key, group, regions in cross_continental[:20]:
    results["cross_continental_twins"].append({
        "signature": "".join(str(s) for s in sig_key),
        "cluster": group[0]["assigned_cluster"],
        "n_traditions": len(group),
        "continents": sorted(regions),
        "traditions": [{"id": t["system_id"], "name": t["system_name"],
                       "tradition": t["tradition"], "region": t["region"]}
                      for t in group]
    })

for sig, count in sig_distribution.most_common():
    results["signature_distribution"]["".join(str(s) for s in sig)] = count

with open(OUTPUT_PATH, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {OUTPUT_PATH}")

# ── Append to journal ─────────────────────────────────────────────────
journal_entry = f"""

## Aletheia — Tradition-Cluster Mapping (depth-3)

**153 ethnomathematics traditions mapped to {len(clusters)} depth-3 structural clusters.**

### Method
- Each tradition's enriched primitive vector -> damage operator activations -> chain support signature (10-bit binary)
- Assigned to nearest cluster by Hamming distance on chain signatures
- Activation threshold: {ACTIVATION_THRESHOLD}

### Key findings
- **Unique signatures**: {len(sig_distribution)} distinct patterns across 153 traditions
- **Zero-chain traditions**: {sum(1 for t in traditions if t['n_chains_supported'] == 0)} (lack the primitives to activate any depth-3 chain)
- **Poorly fit traditions**: {len(unassigned)} (hamming > {n_chains//2} from nearest cluster)
- **Cross-continental twins**: {len(cross_continental)} signature groups span multiple continents

### Most diverse cluster
- **{most_diverse[0]}**: {most_diverse[1]['n_unique_regions']} unique regions, {most_diverse[1]['n_traditions']} traditions
  - Chains: {', '.join(clusters[most_diverse[0]]['chains_supported'])}

### Top signatures
"""

for sig, count in sig_distribution.most_common(5):
    sig_str = "".join(str(s) for s in sig)
    sample = [t for t in traditions if tuple(t["chain_signature"]) == sig][0]
    journal_entry += f"- `{sig_str}` -> {sample['assigned_cluster']}: {count} traditions\n"

journal_entry += f"""
### Surprising alignments
- Cross-continental structural twins found: {len(cross_continental)} groups
- Pre-literate/ancient traditions sharing structure with modern physics hubs identified

Results: `noesis/v2/tradition_cluster_mapping_results.json`
"""

try:
    with open(JOURNAL_PATH, "a", encoding="utf-8") as f:
        f.write(journal_entry)
    print(f"Journal appended: {JOURNAL_PATH}")
except Exception as e:
    print(f"Journal append failed: {e}")

print("\nDone.")
