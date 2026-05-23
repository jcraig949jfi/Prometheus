"""baseline_matrix.py — per-elite ablation matrix.

For each top elite in the checkpoint, evaluate:
  A) original 2-primitive composition (sanity)
  B) first primitive only (n0)
  C) second primitive only (n1)
  D) wiring randomized (input_mapping values shuffled within valid sources)
  E) primitives swapped/reversed (n0 ↔ n1)

If the original (A) does not beat the better of (B) and (C) by ≥0.05 accuracy,
the 'composition' is not pulling its weight — the recipe is single-primitive
performance with decorative scaffold.

Usage:
    python baseline_matrix.py [checkpoint_path] [n_elites=5]
"""
import sys
import copy
import random
import pickle
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from compiler import compile_organism
from sandbox import evaluate_organism_on_tasks
from task_manager import TaskManager
from fitness import compute_ncd_baseline


# Standard fallback router_logic that scores candidates against n0's output
_SIMPLE_ROUTER = """\
n0_out = outputs.get('n0')
n0_str = str(n0_out) if n0_out is not None else ''
scores = []
for cand in candidates:
    cs = str(cand)
    if n0_str and (n0_str in cs or cs in n0_str):
        scores.append(1.0)
    elif n0_str and any(c == n0_str for c in cs.split()):
        scores.append(0.5)
    else:
        scores.append(0.0)
return scores
"""


def _clone(org):
    return copy.deepcopy(org)


def variant_first_only(org):
    """Keep only n0; route_logic falls back to a simple string-match scorer."""
    v = _clone(org)
    if len(v.primitive_sequence) < 2:
        return None
    v.primitive_sequence = v.primitive_sequence[:1]
    v.router_logic = _SIMPLE_ROUTER
    v.genome_id = f"{v.genome_id[:8]}_first"
    return v


def variant_second_only(org):
    """Keep only the second primitive but relabel as n0; rewire its inputs to prompt/candidates."""
    v = _clone(org)
    if len(v.primitive_sequence) < 2:
        return None
    second = v.primitive_sequence[1]
    # relabel as n0
    second.node_id = "n0"
    # rewire — any inputs that referenced n0.output now reference 'prompt'
    new_mapping = {}
    for k, val in second.input_mapping.items():
        if isinstance(val, str) and val.startswith("n"):
            new_mapping[k] = "prompt"
        else:
            new_mapping[k] = val
    second.input_mapping = new_mapping
    v.primitive_sequence = [second]
    v.router_logic = _SIMPLE_ROUTER
    v.genome_id = f"{v.genome_id[:8]}_second"
    return v


def variant_wiring_randomized(org, rng):
    """Shuffle input_mapping values among valid sources for each non-n0 node."""
    v = _clone(org)
    if len(v.primitive_sequence) < 2:
        return None
    valid_sources = ["prompt", "candidates"]
    for i, pc in enumerate(v.primitive_sequence):
        if i == 0:
            continue
        # build list of valid sources for this node: prompt/candidates + earlier nodes' outputs
        sources = list(valid_sources)
        for j in range(i):
            sources.append(f"n{j}.output")
        new_mapping = {}
        for k in pc.input_mapping.keys():
            new_mapping[k] = rng.choice(sources)
        pc.input_mapping = new_mapping
    v.genome_id = f"{v.genome_id[:8]}_rwire"
    return v


def variant_reversed(org):
    """Swap n0 ↔ n1 if the organism has exactly 2 primitives."""
    v = _clone(org)
    if len(v.primitive_sequence) != 2:
        return None
    a, b = v.primitive_sequence
    # Relabel
    a.node_id, b.node_id = "n1", "n0"
    # Inputs that referenced n0.output now must reference (the new n0's output, which is the former b)
    # The simpler interpretation: swap the two nodes positions in the list
    # The downstream router_logic likely still references n0/n1 as positions
    v.primitive_sequence = [b, a]
    # Clear any n-references in their input_mapping that no longer make sense
    for pc in v.primitive_sequence:
        nm = {}
        for k, val in pc.input_mapping.items():
            if isinstance(val, str) and val.startswith("n"):
                # the swap inverts indices; just point at prompt to keep it safe
                nm[k] = "prompt"
            else:
                nm[k] = val
        pc.input_mapping = nm
    v.genome_id = f"{v.genome_id[:8]}_rev"
    return v


def _accuracy_on(source_code, tasks):
    """Return raw accuracy fraction over the task set."""
    if source_code is None:
        return 0.0
    try:
        results = evaluate_organism_on_tasks(source_code, tasks, timeout=0.5)
    except Exception as e:
        return 0.0
    if not results:
        return 0.0
    correct = sum(1 for r in results if r.get("correct"))
    return correct / max(len(results), 1)


def evaluate_variant(label, org, tasks, ncd_baseline):
    if org is None:
        return {"label": label, "skipped": True}
    cr = compile_organism(org)
    if not cr.success:
        return {"label": label, "compile_failed": True, "acc": 0.0, "margin": -ncd_baseline.get("accuracy", 0.0)}
    acc = _accuracy_on(cr.source_code, tasks)
    margin = acc - ncd_baseline.get("accuracy", 0.0)
    return {
        "label": label,
        "compile_failed": False,
        "acc": round(acc, 3),
        "margin": round(margin, 3),
        "genome_id": org.genome_id[:14],
        "primitives": " -> ".join(pc.primitive_name for pc in org.primitive_sequence),
    }


def main():
    if len(sys.argv) > 1:
        ckpt_path = sys.argv[1]
    else:
        ckpt_dir = Path(__file__).parent.parent / "run_v2d2b" / "checkpoints"
        checkpoints = sorted([p for p in ckpt_dir.glob("checkpoint_gen_*.pkl") if "bakeoff" not in p.name])
        ckpt_path = str(checkpoints[-1]) if checkpoints else None
    if not ckpt_path:
        print("No checkpoint")
        sys.exit(1)

    n_elites = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    print(f"=== Baseline matrix on {ckpt_path}, top {n_elites} elites ===\n")

    with open(ckpt_path, "rb") as f:
        data = pickle.load(f)
    population = data["population"]
    generation = data["generation"]
    print(f"Loaded {len(population)} organisms at gen {generation}")

    # Need an evolution-task set + NCD baseline
    project_root = Path(__file__).parent.parent.parent.resolve()
    apollo_dir = Path(__file__).parent.parent.resolve()
    trap_gen_path = str(project_root / "agents" / "hephaestus" / "src" / "trap_generator.py")
    tm = TaskManager(
        trap_gen_path=trap_gen_path,
        n_reference=50, n_evolution=100, n_held_out=50,
        rotation_count=10, rotation_interval=50,
    )
    evolution_tasks = tm.get_evolution_tasks()
    print(f"Loaded {len(evolution_tasks)} evolution tasks")

    print("Computing NCD baseline...")
    ncd_baseline = compute_ncd_baseline(evolution_tasks)
    print(f"NCD baseline accuracy: {ncd_baseline['accuracy']:.1%}")

    # Pick elites — first 5 organisms with primitive_count >= 2 are most representative
    elites = []
    for org in population:
        if len(org.primitive_sequence) >= 2:
            elites.append(org)
        if len(elites) >= n_elites:
            break

    print(f"\nEvaluating {len(elites)} elites × 5 variants each ({len(elites)*5} evaluations)\n")

    rng = random.Random(20260522)
    table = []

    for i, elite in enumerate(elites):
        prim_chain = " -> ".join(pc.primitive_name for pc in elite.primitive_sequence)
        muts = list(elite.lineage.mutations_applied)
        print(f"=== Elite {i+1}: {elite.genome_id[:8]} | {prim_chain}")
        print(f"   muts={muts}")

        variants = [
            ("A_original", _clone(elite)),
            ("B_first_only", variant_first_only(elite)),
            ("C_second_only", variant_second_only(elite)),
            ("D_wire_random", variant_wiring_randomized(elite, rng)),
            ("E_reversed", variant_reversed(elite)),
        ]

        row = {"elite": elite.genome_id[:8], "muts": muts, "primitives": prim_chain}
        for label, v in variants:
            res = evaluate_variant(label, v, evolution_tasks, ncd_baseline)
            row[label] = res
            if res.get("skipped"):
                print(f"   {label:14s}: SKIP")
            elif res.get("compile_failed"):
                print(f"   {label:14s}: COMPILE FAILED  (margin={res.get('margin',0):+.3f})")
            else:
                print(f"   {label:14s}: acc={res['acc']:.3f}  margin={res['margin']:+.3f}  | {res['primitives'][:80]}")
        table.append(row)
        print()

    # Aggregate verdict
    print("=" * 80)
    print("VERDICT — composition lift over best single-primitive baseline")
    print("=" * 80)
    real_compositions = 0
    decorative = 0
    for row in table:
        orig = row["A_original"]
        b = row.get("B_first_only", {})
        c = row.get("C_second_only", {})
        d = row.get("D_wire_random", {})
        e = row.get("E_reversed", {})
        # Best single-primitive baseline
        single_accs = []
        if not b.get("compile_failed") and not b.get("skipped"):
            single_accs.append(b.get("acc", 0))
        if not c.get("compile_failed") and not c.get("skipped"):
            single_accs.append(c.get("acc", 0))
        best_single = max(single_accs) if single_accs else 0.0
        orig_acc = orig.get("acc", 0)
        lift = orig_acc - best_single
        verdict = "REAL_COMPOSITION" if lift >= 0.05 else "DECORATIVE"
        if verdict == "REAL_COMPOSITION":
            real_compositions += 1
        else:
            decorative += 1
        print(f"  {row['elite']}  {row['primitives'][:50]:50s}  "
              f"orig={orig_acc:.3f}  best_single={best_single:.3f}  "
              f"lift={lift:+.3f}  random_wiring={d.get('acc',0):.3f}  reversed={e.get('acc',0):.3f}  "
              f"[{verdict}]")
    print()
    print(f"Real-composition elites: {real_compositions}/{len(table)}")
    print(f"Decorative elites:       {decorative}/{len(table)}")
    if real_compositions == 0:
        print("\nCONCLUSION: Composition is NOT pulling its weight. The 2-primitive recipe")
        print("            appears to be single-primitive performance with decorative scaffold.")
        print("            This corroborates the reviewer's Goodhart hypothesis.")
    elif real_compositions >= len(table) * 0.6:
        print("\nCONCLUSION: Most elites show real compositional lift. Recipe is genuine.")
    else:
        print("\nCONCLUSION: Mixed — some elites compose, others are decorative. Worth a closer look.")


if __name__ == "__main__":
    main()
