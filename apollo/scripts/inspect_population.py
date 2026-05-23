"""inspect_population.py — show what's actually in Apollo's surviving population.

Loads the latest checkpoint, groups organisms by lineage operator,
prints primitive sequences + wiring for each surviving organism.

Usage:
    python inspect_population.py [checkpoint_path]
"""
import sys
import pickle
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def main():
    if len(sys.argv) > 1:
        ckpt_path = sys.argv[1]
    else:
        ckpt_dir = Path(__file__).parent.parent / "run_v2d2b" / "checkpoints"
        # Find latest non-backup checkpoint
        checkpoints = sorted([p for p in ckpt_dir.glob("checkpoint_gen_*.pkl") if "bakeoff" not in p.name])
        if not checkpoints:
            print("No checkpoints found")
            sys.exit(1)
        ckpt_path = str(checkpoints[-1])

    print(f"=== Loading {ckpt_path} ===\n")
    with open(ckpt_path, "rb") as f:
        data = pickle.load(f)
    population = data["population"]
    gen = data["generation"]

    # Group by lineage signature
    by_lineage_tag = defaultdict(list)
    for org in population:
        muts = list(org.lineage.mutations_applied)
        # Find the "real" mutation type (not 'drift' or 'annealed')
        real = [m for m in muts if m not in ('drift', 'annealed')]
        tag = real[0] if real else 'drift_only'
        by_lineage_tag[tag].append(org)

    print(f"Generation: {gen}, population: {len(population)}\n")
    print("--- Population breakdown by primary mutation operator ---")
    for tag, orgs in sorted(by_lineage_tag.items(), key=lambda x: -len(x[1])):
        is_llm = 'llm' in tag
        marker = " *LLM*" if is_llm else ""
        print(f"  {len(orgs):3d} {tag}{marker}")

    print(f"\n--- LLM-derived organism details (operator -> primitive sequence -> wiring) ---\n")
    for tag, orgs in sorted(by_lineage_tag.items()):
        if 'llm' not in tag:
            continue
        print(f"==== {tag} ({len(orgs)} organisms) ====")
        for i, org in enumerate(orgs):
            prim_seq = " -> ".join(pc.primitive_name for pc in org.primitive_sequence)
            wiring = []
            for pc in org.primitive_sequence:
                for k, v in pc.input_mapping.items():
                    if v.startswith("n") or v == "prompt" or v == "candidates":
                        wiring.append(f"{pc.node_id}.{k}<-{v}")
            print(f"  [{i+1}] {org.genome_id[:8]} | {len(org.primitive_sequence)} prims | {prim_seq}")
            print(f"        muts={list(org.lineage.mutations_applied)}")
            if wiring:
                print(f"        wiring: {', '.join(wiring[:6])}{'...' if len(wiring)>6 else ''}")
        print()

    # Primitive frequency in surviving population
    print("--- Primitives used by surviving population (frequency) ---")
    prim_counts = Counter()
    for org in population:
        for pc in org.primitive_sequence:
            prim_counts[pc.primitive_name] += 1
    for p, n in sorted(prim_counts.items(), key=lambda x: -x[1]):
        print(f"  {n:3d}  {p}")

    # Compare LLM-derived vs non-LLM primitive usage
    print("\n--- Primitive bias: LLM-derived vs non-LLM organisms ---")
    llm_orgs = [o for o in population if any('llm_batch' in m for m in o.lineage.mutations_applied)]
    non_llm_orgs = [o for o in population if not any('llm_batch' in m for m in o.lineage.mutations_applied)]
    llm_prims = Counter()
    non_llm_prims = Counter()
    for o in llm_orgs:
        for pc in o.primitive_sequence:
            llm_prims[pc.primitive_name] += 1
    for o in non_llm_orgs:
        for pc in o.primitive_sequence:
            non_llm_prims[pc.primitive_name] += 1
    print(f"  N LLM-derived={len(llm_orgs)}  N non-LLM={len(non_llm_orgs)}")
    all_prims = set(llm_prims) | set(non_llm_prims)
    print(f"  {'primitive':<32} {'LLM%':>6}  {'nonLLM%':>8}")
    for p in sorted(all_prims):
        l_pct = llm_prims[p] / max(len(llm_orgs), 1) * 100
        n_pct = non_llm_prims[p] / max(len(non_llm_orgs), 1) * 100
        if l_pct or n_pct:
            print(f"  {p:<32} {l_pct:5.0f}%  {n_pct:6.0f}%")


if __name__ == "__main__":
    main()
