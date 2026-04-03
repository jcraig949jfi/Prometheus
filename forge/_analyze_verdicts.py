"""Analyze G2 verdicts — scores, ablation, and what's working."""
import json
from pathlib import Path

verdicts_dir = Path("forge/verdicts")
results = []
for f in sorted(verdicts_dir.glob("t2_*.json")):
    v = json.loads(f.read_text())
    results.append(v)

print(f"{'Tool':<30s} {'Score':>6s} {'Stability':>10s} {'Verdict':<20s}")
print("-" * 70)
for v in sorted(results, key=lambda x: x.get("overall_score", 0), reverse=True):
    tid = v["tool_id"]
    score = v.get("overall_score", 0)
    stab = v.get("seed_stability", 0)
    verdict = v.get("verdict", "?")
    print(f"{tid:<30s} {score:>5.1%} {stab:>9.3f}  {verdict}")

# Ablation analysis for top tools
print("\n\nAblation for tools scoring > 30%:")
for v in results:
    if v.get("overall_score", 0) > 0.30:
        print(f"\n  {v['tool_id']} ({v['overall_score']:.1%}):")
        abl = v.get("ablation", {})
        if not abl:
            print("    No ablation data")
            continue
        total_delta = sum(abs(d.get("delta", 0)) for d in abl.values() if d.get("delta") is not None)
        for prim, data in sorted(abl.items(), key=lambda x: abs(x[1].get("delta", 0)), reverse=True):
            delta = data.get("delta", 0)
            lb = data.get("load_bearing", False)
            share = abs(delta) / total_delta if total_delta > 0 else 0
            err = data.get("error", "")
            if err:
                print(f"    {prim:30s} ERROR: {err[:60]}")
            else:
                marker = " <<<" if lb else ""
                print(f"    {prim:30s} delta={delta:+.4f}  share={share:.0%}{marker}")
