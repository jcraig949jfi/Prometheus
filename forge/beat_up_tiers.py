"""Beat-up script: stress test all T2 and T3 forged tools against their batteries.

Runs each tool against its own tier battery, plus cross-tier batteries.
Reports per-tool, per-category accuracy with detailed failure analysis.
"""
import sys, os, importlib.util, zlib, traceback, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
FORGE = ROOT / "forge"

# Add paths
sys.path.insert(0, str(ROOT / "agents" / "hephaestus" / "src"))
sys.path.insert(0, str(FORGE / "v2" / "hephaestus_t2" / "src"))
sys.path.insert(0, str(FORGE / "v2" / "hephaestus_t2" / "forge"))
sys.path.insert(0, str(FORGE / "v3" / "hephaestus_t3" / "src"))
sys.path.insert(0, str(FORGE / "v3" / "hephaestus_t3" / "forge"))

# ── Load batteries ──────────────────────────────────────────────────────
from trap_generator_t2 import generate_t2_battery, T2_CATEGORIES
from trap_generator_t3 import generate_t3_battery, T3_CATEGORIES

T2_BATTERY = generate_t2_battery(n_per_category=2, seed=42)
T3_BATTERY = generate_t3_battery(n_per_category=5, seed=42)
print(f"T2 battery: {len(T2_BATTERY)} traps across {len(T2_CATEGORIES)} categories")
print(f"T3 battery: {len(T3_BATTERY)} traps across {len(T3_CATEGORIES)} categories")

# T1 static battery (from test harness)
from test_harness import TRAPS as T1_BATTERY
print(f"T1 battery: {len(T1_BATTERY)} static traps")

# ── Load tools ──────────────────────────────────────────────────────────
def load_tool(path):
    """Load a ReasoningTool from a .py file, handling import side effects."""
    path = Path(path)
    name = path.stem
    # Add parent dir to sys.path so relative imports work
    parent = str(path.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod.ReasoningTool()

T2_TOOLS = {}
T3_TOOLS = {}
t2_dir = FORGE / "v2" / "hephaestus_t2" / "forge"
t3_dir = FORGE / "v3" / "hephaestus_t3" / "forge"

for f in sorted(t2_dir.glob("t2_*.py")):
    try:
        T2_TOOLS[f.stem] = load_tool(f)
        print(f"  Loaded T2: {f.stem}")
    except Exception as e:
        print(f"  FAILED T2: {f.stem} — {e}")

for f in sorted(t3_dir.glob("t3_*.py")):
    try:
        T3_TOOLS[f.stem] = load_tool(f)
        print(f"  Loaded T3: {f.stem}")
    except Exception as e:
        print(f"  FAILED T3: {f.stem} — {e}")

# ── NCD baseline ────────────────────────────────────────────────────────
class NCDBaseline:
    def evaluate(self, prompt, candidates):
        out = []
        for c in candidates:
            ca = len(zlib.compress(prompt.encode()))
            cb = len(zlib.compress(c.encode()))
            cab = len(zlib.compress((prompt + " " + c).encode()))
            d = (cab - min(ca, cb)) / max(ca, cb) if max(ca, cb) > 0 else 1.0
            out.append({"candidate": c, "score": 1.0 / (1.0 + d)})
        return sorted(out, key=lambda x: x["score"], reverse=True)

NCD = NCDBaseline()

# ── Run battery ─────────────────────────────────────────────────────────
def run_battery(tool, battery, label=""):
    """Run a tool against a battery. Return per-category results."""
    cat_correct = defaultdict(int)
    cat_total = defaultdict(int)
    failures = []
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
                failures.append({"cat": cat, "prompt": trap["prompt"][:80],
                                 "expected": trap["correct"][:60] if isinstance(trap["correct"], str) else str(trap["correct"]),
                                 "got": (top[:60] if isinstance(top, str) else str(top)) if top else "None"})
        except Exception as e:
            errors += 1
            failures.append({"cat": cat, "prompt": trap["prompt"][:80], "error": str(e)[:60]})

    total_correct = sum(cat_correct.values())
    total = sum(cat_total.values())
    acc = total_correct / total if total > 0 else 0
    return {"accuracy": acc, "correct": total_correct, "total": total,
            "errors": errors, "cat_correct": dict(cat_correct),
            "cat_total": dict(cat_total), "failures": failures}

def print_results(tool_name, result, battery_name):
    print(f"\n{'='*70}")
    print(f"  {tool_name} vs {battery_name}")
    print(f"  Overall: {result['correct']}/{result['total']} = {result['accuracy']:.1%}"
          f"  (errors: {result['errors']})")
    print(f"  Per-category:")
    for cat in sorted(result['cat_total'].keys()):
        c = result['cat_correct'].get(cat, 0)
        t = result['cat_total'][cat]
        bar = '█' * c + '░' * (t - c)
        print(f"    {cat:40s} {c}/{t} {bar}")
    if result['failures'][:3]:
        print(f"  Sample failures:")
        for f in result['failures'][:3]:
            if 'error' in f:
                print(f"    [{f['cat']}] ERROR: {f['error']}")
            else:
                print(f"    [{f['cat']}] expected={f['expected']}")
                print(f"              got     ={f['got']}")

# ── Main ────────────────────────────────────────────────────────────────
print("\n" + "━"*70)
print("  NCD BASELINE")
print("━"*70)
for bname, battery in [("T2", T2_BATTERY), ("T3", T3_BATTERY), ("T1", T1_BATTERY)]:
    r = run_battery(NCD, battery)
    print(f"  NCD vs {bname}: {r['correct']}/{r['total']} = {r['accuracy']:.1%}")

print("\n" + "━"*70)
print("  T2 TOOLS vs T2 BATTERY")
print("━"*70)
for name, tool in T2_TOOLS.items():
    r = run_battery(tool, T2_BATTERY)
    print_results(name, r, "T2 Battery")

print("\n" + "━"*70)
print("  T3 TOOLS vs T3 BATTERY")
print("━"*70)
for name, tool in T3_TOOLS.items():
    r = run_battery(tool, T3_BATTERY)
    print_results(name, r, "T3 Battery")

print("\n" + "━"*70)
print("  CROSS-TIER: T2 TOOLS vs T1 BATTERY")
print("━"*70)
for name, tool in T2_TOOLS.items():
    r = run_battery(tool, T1_BATTERY)
    print_results(name, r, "T1 Battery")

print("\n" + "━"*70)
print("  CROSS-TIER: T3 TOOLS vs T1 BATTERY")
print("━"*70)
for name, tool in T3_TOOLS.items():
    r = run_battery(tool, T1_BATTERY)
    print_results(name, r, "T1 Battery")

print("\n" + "━"*70)
print("  CROSS-TIER: T2 TOOLS vs T3 BATTERY")
print("━"*70)
for name, tool in T2_TOOLS.items():
    r = run_battery(tool, T3_BATTERY)
    print(f"  {name}: {r['correct']}/{r['total']} = {r['accuracy']:.1%}")

print("\n" + "━"*70)
print("  CROSS-TIER: T3 TOOLS vs T2 BATTERY")
print("━"*70)
for name, tool in T3_TOOLS.items():
    r = run_battery(tool, T2_BATTERY)
    print(f"  {name}: {r['correct']}/{r['total']} = {r['accuracy']:.1%}")

print("\n\nDONE.")
