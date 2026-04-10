#!/usr/bin/env python3
"""
Cross-correlate residue-class starvation with Hecke congruence pairs.

Question: Are the 156 non-CM starved forms (ell>=5) overrepresented
among congruence pair nodes?

If starvation (small Galois image) forces congruences, we expect enrichment.
If independent, overlap should match hypergeometric expectation.
"""

import json
import os
from collections import defaultdict
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))

# ── 1. Load starvation data ──────────────────────────────────────────
with open(os.path.join(HERE, "residue_starvation_results.json")) as f:
    starv_data = json.load(f)

total_forms = starv_data["metadata"]["total_scanned"]  # 17314

# Filter: non-CM, starvation at ell >= 5
starved_forms = []
for form in starv_data["starved_forms"]:
    if form["is_cm"]:
        continue
    large_primes = {int(p) for p in form["starvation"].keys() if int(p) >= 5}
    if large_primes:
        starved_forms.append(form)

starved_labels = {f["label"] for f in starved_forms}
print(f"Non-CM starved forms (ell>=5): {len(starved_labels)}")

# Build starvation-prime map: label -> set of primes where starved
starved_primes_map = {}
for form in starved_forms:
    primes = {int(p) for p in form["starvation"].keys() if int(p) >= 5}
    starved_primes_map[form["label"]] = primes

# ── 2. Load congruence data ──────────────────────────────────────────
with open(os.path.join(HERE, "congruence_graph.json")) as f:
    cong_data = json.load(f)

# Collect congruence nodes per ell
cong_nodes_by_ell = {}  # ell -> set of form labels
cong_pairs_by_ell = {}  # ell -> list of (form_a, form_b)

for ell_str, block in cong_data.items():
    ell = int(ell_str)
    if ell < 5:
        continue
    nodes = set()
    pairs = []
    for c in block["congruences"]:
        nodes.add(c["form_a"])
        nodes.add(c["form_b"])
        pairs.append((c["form_a"], c["form_b"]))
    cong_nodes_by_ell[ell] = nodes
    cong_pairs_by_ell[ell] = pairs

all_cong_nodes = set()
for nodes in cong_nodes_by_ell.values():
    all_cong_nodes |= nodes

print(f"Congruence nodes (ell>=5): {len(all_cong_nodes)}")
for ell in sorted(cong_nodes_by_ell):
    print(f"  mod-{ell}: {len(cong_nodes_by_ell[ell])} nodes, "
          f"{len(cong_pairs_by_ell[ell])} pairs")

# ── 3. Compute overlap ──────────────────────────────────────────────
overlap = starved_labels & all_cong_nodes
print(f"\nOverlap (starved AND congruence node): {len(overlap)}")

# ── 4. Null expectation (hypergeometric) ─────────────────────────────
# Drawing len(starved_labels) balls from total_forms,
# where len(all_cong_nodes) are "successes"
n_starved = len(starved_labels)
n_cong = len(all_cong_nodes)
expected_overlap = n_starved * n_cong / total_forms

print(f"\nNull expectation: {expected_overlap:.2f}")
print(f"  (hypergeometric: {n_starved} starved, {n_cong} cong nodes, {total_forms} total)")

# Hypergeometric test: P(X >= observed)
# scipy hypergeom: M=population, n=success states, N=draws
observed = len(overlap)
pval = stats.hypergeom.sf(observed - 1, total_forms, n_cong, n_starved)
enrichment = observed / expected_overlap if expected_overlap > 0 else float('inf')

print(f"Enrichment ratio: {enrichment:.2f}x")
print(f"p-value (hypergeometric, one-sided): {pval:.4e}")

# ── 5. Prime-by-prime breakdown ──────────────────────────────────────
print("\n=== Prime-by-prime breakdown ===")

prime_breakdown = {}
for ell in sorted(cong_nodes_by_ell):
    ell_overlap = starved_labels & cong_nodes_by_ell[ell]
    n_ell_cong = len(cong_nodes_by_ell[ell])
    exp_ell = n_starved * n_ell_cong / total_forms
    enrich_ell = len(ell_overlap) / exp_ell if exp_ell > 0 else float('inf')
    pval_ell = stats.hypergeom.sf(len(ell_overlap) - 1, total_forms,
                                   n_ell_cong, n_starved)
    print(f"  mod-{ell}: overlap={len(ell_overlap)}, expected={exp_ell:.2f}, "
          f"enrichment={enrich_ell:.2f}x, p={pval_ell:.4e}")
    prime_breakdown[str(ell)] = {
        "congruence_nodes": n_ell_cong,
        "overlap": len(ell_overlap),
        "expected": round(exp_ell, 4),
        "enrichment": round(enrich_ell, 4),
        "p_value": float(pval_ell),
        "overlap_labels": sorted(ell_overlap)
    }

# ── 6. For overlapping forms: starvation prime vs congruence prime ───
print("\n=== Starvation prime vs congruence prime ===")
same_prime_count = 0
diff_prime_count = 0
same_prime_forms = []
diff_prime_forms = []

for label in sorted(overlap):
    starv_ps = starved_primes_map[label]
    cong_ps = set()
    for ell, nodes in cong_nodes_by_ell.items():
        if label in nodes:
            cong_ps.add(ell)
    shared = starv_ps & cong_ps
    if shared:
        same_prime_count += 1
        same_prime_forms.append({
            "label": label,
            "starvation_primes": sorted(starv_ps),
            "congruence_primes": sorted(cong_ps),
            "shared_primes": sorted(shared),
            "type": "SAME_PRIME"
        })
        print(f"  SAME: {label}  starved@{sorted(starv_ps)}  cong@{sorted(cong_ps)}  shared={sorted(shared)}")
    else:
        diff_prime_count += 1
        diff_prime_forms.append({
            "label": label,
            "starvation_primes": sorted(starv_ps),
            "congruence_primes": sorted(cong_ps),
            "shared_primes": [],
            "type": "DIFFERENT_PRIMES"
        })
        print(f"  DIFF: {label}  starved@{sorted(starv_ps)}  cong@{sorted(cong_ps)}")

print(f"\nSame-prime (single phenomenon): {same_prime_count}")
print(f"Different-prime (independent):  {diff_prime_count}")

# ── 7. Level 637 special investigation ───────────────────────────────
print("\n=== Level 637 investigation ===")
level_637_starved = [f for f in starved_forms if f["level"] == 637]
level_637_cong = []
for ell, pairs in cong_pairs_by_ell.items():
    for a, b in pairs:
        if "637." in a or "637." in b:
            level_637_cong.append({"form_a": a, "form_b": b, "ell": ell})

print(f"  Starved forms at level 637: {len(level_637_starved)}")
for f in level_637_starved:
    print(f"    {f['label']}  starved@{sorted(int(p) for p in f['starvation'].keys())}")
    for p, info in f["starvation"].items():
        if int(p) >= 5:
            print(f"      ell={p}: classes_hit={info['classes_hit']}/{int(p)}, "
                  f"missing={info.get('missing', [])}")

print(f"  Congruence pairs at level 637: {len(level_637_cong)}")
for c in level_637_cong:
    print(f"    {c['form_a']} <-> {c['form_b']}  mod-{c['ell']}")

level_637_labels_starved = {f["label"] for f in level_637_starved
                            if any(int(p) >= 5 for p in f["starvation"])}
level_637_cong_labels = set()
for c in level_637_cong:
    level_637_cong_labels.add(c["form_a"])
    level_637_cong_labels.add(c["form_b"])

level_637_both = level_637_labels_starved & level_637_cong_labels
print(f"  Forms both starved(ell>=5) AND in congruences: {sorted(level_637_both)}")

# ── 8. Save results ─────────────────────────────────────────────────
results = {
    "metadata": {
        "total_forms": total_forms,
        "n_starved_non_cm_ell_ge5": n_starved,
        "n_congruence_nodes_ell_ge5": n_cong,
        "congruence_ells_checked": sorted(cong_nodes_by_ell.keys())
    },
    "global": {
        "overlap_count": observed,
        "expected_overlap": round(expected_overlap, 4),
        "enrichment_ratio": round(enrichment, 4),
        "p_value_hypergeometric": float(pval),
        "overlap_labels": sorted(overlap)
    },
    "per_ell": prime_breakdown,
    "prime_alignment": {
        "same_prime_count": same_prime_count,
        "different_prime_count": diff_prime_count,
        "same_prime_forms": same_prime_forms,
        "different_prime_forms": diff_prime_forms
    },
    "level_637": {
        "starved_forms": [f["label"] for f in level_637_starved],
        "starved_primes": {
            f["label"]: sorted(int(p) for p in f["starvation"].keys())
            for f in level_637_starved
        },
        "congruence_pairs": level_637_cong,
        "forms_both": sorted(level_637_both)
    }
}

out_path = os.path.join(HERE, "starved_congruence_results.json")
with open(out_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {out_path}")
