"""Forge Tester — evaluates candidate tools against quarantined batteries.

This script has NO ability to modify tools. It reads tool files from
forge/candidates/, evaluates them, and writes verdicts to forge/verdicts/.

It NEVER communicates test content (prompts, candidates, expected answers)
back to the Builder. The verdict contains ONLY:
- Category name + pass/fail + failure type
- Ablation results
- Diversity score
"""
import sys, os, io, json, importlib.util, ast, zlib, argparse, hashlib
from pathlib import Path
from collections import defaultdict
from datetime import datetime

if __name__ == "__main__" and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = Path(__file__).resolve().parent.parent
FORGE = Path(__file__).resolve().parent
QUARANTINE = FORGE / "tester_quarantine"
CANDIDATES = FORGE / "candidates"
VERDICTS = FORGE / "verdicts"

# Add paths for batteries, primitives, and forge package
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "agents" / "hephaestus" / "src"))
sys.path.insert(0, str(QUARANTINE))

from forge.thresholds import THRESHOLDS


def load_battery(tier, n_per_category, seed):
    """Load battery from quarantine. Tester is the ONLY script that does this."""
    if tier == 2:
        from trap_generator_t2 import generate_t2_battery
        return generate_t2_battery(n_per_category=n_per_category, seed=seed)
    elif tier == 3:
        from trap_generator_t3 import generate_t3_battery
        return generate_t3_battery(n_per_category=n_per_category, seed=seed)
    else:
        raise ValueError(f"Unknown tier: {tier}")


def load_tool(tool_path):
    """Load a ReasoningTool from a .py file. Read-only — no modification."""
    path = Path(tool_path)
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.ReasoningTool()


def run_battery(tool, battery):
    """Run a tool against a battery. Returns per-category results.
    
    NEVER returns test content — only category-level pass/fail.
    """
    cat_correct = defaultdict(int)
    cat_total = defaultdict(int)
    cat_failures = defaultdict(list)
    errors = 0

    for trap in battery:
        cat = trap.get("category", "unknown")
        cat_total[cat] += 1
        try:
            ranked = tool.evaluate(trap["prompt"], trap["candidates"])
            top = ranked[0]["candidate"] if ranked else None
            if top == trap["correct"]:
                cat_correct[cat] += 1
            else:
                cat_failures[cat].append("wrong_answer")
        except TimeoutError:
            cat_failures[cat].append("timeout")
            errors += 1
        except Exception:
            cat_failures[cat].append("format_error")
            errors += 1

    results = {}
    for cat in cat_total:
        correct = cat_correct.get(cat, 0)
        total = cat_total[cat]
        passed = correct == total  # Must get ALL right in category
        failure_type = None
        if not passed:
            fails = cat_failures.get(cat, ["wrong_answer"])
            failure_type = max(set(fails), key=fails.count)  # Most common failure
        results[cat] = {"pass": passed, "failure_type": failure_type}

    overall = sum(cat_correct.values()) / sum(cat_total.values()) if cat_total else 0
    return {"overall_score": overall, "per_category": results, "errors": errors}


def run_seed_battery(tool, tier, seeds, n_per_category=2):
    """Run tool against battery across multiple seeds. Returns scores and stability."""
    scores = []
    all_category_results = {}
    for seed in seeds:
        battery = load_battery(tier, n_per_category, seed)
        result = run_battery(tool, battery)
        scores.append(result["overall_score"])
        # Merge category results (pass only if passes on ALL seeds)
        for cat, cat_result in result["per_category"].items():
            if cat not in all_category_results:
                all_category_results[cat] = {"pass": True, "failure_type": None}
            if not cat_result["pass"]:
                all_category_results[cat]["pass"] = False
                all_category_results[cat]["failure_type"] = cat_result["failure_type"]

    seed_stability = max(scores) - min(scores) if scores else 0
    return {
        "seed_scores": scores,
        "seed_stability": seed_stability,
        "overall_score": sum(scores) / len(scores) if scores else 0,
        "per_category": all_category_results,
    }


def run_ablation(tool_path, tier, seed=42, n_per_category=2):
    """Remove each primitive/amino acid one at a time and re-run battery.

    Returns ablation table: {primitive_name: {"delta": float, "load_bearing": bool}}
    """
    # Parse the tool's source to find imported primitives/amino acids
    source = Path(tool_path).read_text(encoding='utf-8')
    tree = ast.parse(source)

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imports.append({
                    "module": node.module or "",
                    "name": alias.name,
                    "asname": alias.asname or alias.name,
                })

    # Get baseline score
    tool = load_tool(tool_path)
    battery = load_battery(tier, n_per_category, seed)
    baseline = run_battery(tool, battery)
    baseline_score = baseline["overall_score"]

    # For each imported function, create a modified version with it stubbed out
    ablation = {}
    for imp in imports:
        # Skip non-primitive imports
        if imp["module"] and ("forge_primitives" in imp["module"] or "amino_acids" in imp["module"]):
            name = imp["name"]
            try:
                # Create modified source with the function replaced by a no-op
                modified = _stub_function(source, name, imp["asname"])
                mod_tool = _load_from_string(modified, Path(tool_path).stem + f"_ablate_{name}")
                result = run_battery(mod_tool, battery)
                delta = baseline_score - result["overall_score"]
                ablation[name] = {
                    "delta": round(delta, 4),
                    "load_bearing": abs(delta) >= THRESHOLDS[f"t{tier}"]["min_ablation_impact"],
                }
            except Exception as e:
                ablation[name] = {"delta": None, "error": str(e)[:100], "load_bearing": False}

    return ablation, baseline_score


def _stub_function(source, func_name, alias):
    """Replace a function import with a stub that returns a neutral value."""
    # Replace the function call with a lambda that returns None
    stub_line = f"\ndef {alias}(*args, **kwargs): return None  # ABLATION STUB\n"
    # Comment out the import of this specific function
    lines = source.split('\n')
    modified = []
    for line in lines:
        stripped = line.strip()
        if f"import" in stripped and func_name in stripped:
            # Comment out this import line and add stub
            modified.append(f"# ABLATED: {line}")
            modified.append(stub_line)
        else:
            modified.append(line)
    return '\n'.join(modified)


def _load_from_string(source_code, module_name):
    """Load a ReasoningTool from a string of Python source code."""
    import types
    mod = types.ModuleType(module_name)
    exec(compile(source_code, f"<ablation:{module_name}>", "exec"), mod.__dict__)
    return mod.ReasoningTool()


def compute_callgraph(tool_path):
    """Extract the set of primitive/amino acid calls from a tool's source."""
    source = Path(tool_path).read_text(encoding='utf-8')
    tree = ast.parse(source)
    calls = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and ("forge_primitives" in node.module or "amino_acids" in node.module):
                for alias in node.names:
                    calls.add(alias.name)
    return calls


def compute_diversity(tool_path, existing_tool_paths):
    """Compute pairwise call-graph overlap with all existing tools.

    Returns dict with max_overlap, most_similar_tool, passes_check.
    """
    new_calls = compute_callgraph(tool_path)
    if not new_calls:
        return {"max_overlap": 1.0, "most_similar_tool": None, "passes_diversity_check": False}

    max_overlap = 0.0
    most_similar = None
    for existing_path in existing_tool_paths:
        existing_calls = compute_callgraph(existing_path)
        if not existing_calls:
            continue
        intersection = new_calls & existing_calls
        union = new_calls | existing_calls
        overlap = len(intersection) / len(union) if union else 0
        if overlap > max_overlap:
            max_overlap = overlap
            most_similar = Path(existing_path).stem

    threshold = THRESHOLDS["max_callgraph_overlap"]
    return {
        "max_overlap": round(max_overlap, 4),
        "most_similar_tool": most_similar,
        "passes_diversity_check": max_overlap <= threshold,
    }


def evaluate_tool(tool_path, tier, existing_tool_paths=None, seeds=None):
    """Full evaluation pipeline for a single tool.

    Returns a verdict dict suitable for writing to forge/verdicts/.
    """
    if seeds is None:
        seeds = [42, 0, 1, 99, 9999]
    if existing_tool_paths is None:
        existing_tool_paths = []

    tool_id = Path(tool_path).stem
    tier_key = f"t{tier}"
    thresholds = THRESHOLDS[tier_key]

    # 1. Seed battery
    print(f"  Evaluating {tool_id} across {len(seeds)} seeds...")
    tool = load_tool(tool_path)
    seed_result = run_seed_battery(tool, tier, seeds)

    # 2. Ablation
    print(f"  Running ablation...")
    ablation, baseline_score = run_ablation(tool_path, tier)

    # Check ablation budget share
    deltas = [abs(v["delta"]) for v in ablation.values() if v.get("delta") is not None]
    total_delta = sum(deltas) if deltas else 1
    ablation_ok = True
    promising = []
    for name, result in ablation.items():
        if result.get("delta") is not None:
            budget_share = abs(result["delta"]) / total_delta if total_delta > 0 else 0
            result["budget_share"] = round(budget_share, 4)
            if budget_share > thresholds["max_ablation_budget_share"]:
                ablation_ok = False
                promising.append(name)

    # 3. Diversity
    print(f"  Computing diversity...")
    diversity = compute_diversity(tool_path, existing_tool_paths)

    # 4. Determine verdict
    passes_battery = seed_result["overall_score"] >= thresholds["pass_threshold"]
    passes_seed = seed_result["seed_stability"] <= thresholds["max_seed_drop"]
    passes_ablation = ablation_ok
    passes_diversity = diversity["passes_diversity_check"]

    if passes_battery and passes_seed and passes_ablation and passes_diversity:
        verdict = "PASS"
    elif passes_battery and passes_seed and not passes_ablation:
        verdict = "FAIL_ABLATION"
    elif passes_battery and not passes_seed:
        verdict = "FAIL_SEED_STABILITY"
    elif not passes_battery:
        verdict = "FAIL_BATTERY"
    else:
        verdict = "FAIL_DIVERSITY"

    result = {
        "tool_id": tool_id,
        "tier": tier,
        "timestamp": datetime.now().isoformat(),
        "overall_score": seed_result["overall_score"],
        "seed_scores": seed_result["seed_scores"],
        "seed_stability": seed_result["seed_stability"],
        "per_category": seed_result["per_category"],
        "ablation": ablation,
        "diversity": diversity,
        "verdict": verdict,
        "promising_primitives": promising,
    }

    # Write verdict (NEVER contains test content)
    verdict_path = VERDICTS / f"{tool_id}_verdict.json"
    VERDICTS.mkdir(parents=True, exist_ok=True)
    with open(verdict_path, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print(f"  Verdict: {verdict} (score={seed_result['overall_score']:.1%}, "
          f"stability={seed_result['seed_stability']:.3f})")

    return result


def run_null_baselines(tier, seeds=None, n_per_category=2):
    """Run null baselines (Law 5). Returns baseline scores."""
    if seeds is None:
        seeds = [42]

    battery = load_battery(tier, n_per_category, seeds[0])
    print(f"\n  Null baselines for T{tier} ({len(battery)} traps):")

    # Baseline 1: NCD
    ncd_correct = 0
    for trap in battery:
        prompt = trap["prompt"]
        scores = []
        for c in trap["candidates"]:
            ca = len(zlib.compress(prompt.encode()))
            cb = len(zlib.compress(c.encode()))
            cab = len(zlib.compress((prompt + " " + c).encode()))
            d = (cab - min(ca, cb)) / max(ca, cb) if max(ca, cb) > 0 else 1.0
            scores.append((c, 1.0 / (1.0 + d)))
        scores.sort(key=lambda x: x[1], reverse=True)
        if scores[0][0] == trap["correct"]:
            ncd_correct += 1
    ncd_score = ncd_correct / len(battery) if battery else 0
    print(f"    NCD baseline: {ncd_correct}/{len(battery)} = {ncd_score:.1%}")

    # Baseline 2: Random chance (4 candidates)
    random_score = 1.0 / 4.0  # 25% for 4-way multiple choice
    print(f"    Random chance: {random_score:.1%}")

    return {
        "tier": tier,
        "ncd_score": ncd_score,
        "random_chance": random_score,
        "battery_size": len(battery),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Forge Tester")
    parser.add_argument("--tool", type=str, help="Path to tool .py file to evaluate")
    parser.add_argument("--tier", type=int, required=True, help="Tier (2 or 3)")
    parser.add_argument("--baselines", action="store_true", help="Run null baselines only")
    parser.add_argument("--existing", nargs="*", default=[], help="Existing tool paths for diversity")
    args = parser.parse_args()

    if args.baselines:
        result = run_null_baselines(args.tier)
        out_path = FORGE / "null_baselines.json"
        existing = {}
        if out_path.exists():
            existing = json.loads(out_path.read_text())
        existing[f"t{args.tier}"] = result
        out_path.write_text(json.dumps(existing, indent=2))
        print(f"  Written to {out_path}")
    elif args.tool:
        evaluate_tool(args.tool, args.tier, args.existing)
    else:
        print("Specify --tool PATH or --baselines")
