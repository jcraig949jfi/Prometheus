#!/usr/bin/env python3
"""Run all v3 tools against the expanded trap battery.

Computes:
- Per-tool accuracy on Tier A (parsing) and Tier B (judgment) traps
- Fallback rate: % of traps where no structural parser fires
- Epistemic honesty: correlation between parser coverage and confidence
- Per-category accuracy heatmap
- Family-level analysis

Output: forge_v3/expanded_battery_report.json + expanded_battery_report.md
"""

import json
import logging
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from test_harness import load_tool_from_file, TRAPS, _run_battery, _ncd_baseline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [BATTERY] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("expanded_battery")

HEPH_ROOT = Path(__file__).resolve().parent.parent
V3_DIR = HEPH_ROOT / "forge_v3"
REPORT_JSON = V3_DIR / "expanded_battery_report.json"
REPORT_MD = V3_DIR / "expanded_battery_report.md"


def load_expanded_battery(seed=42, n_per_category=2):
    """Load the full expanded battery (base + extended)."""
    try:
        from trap_generator_extended import generate_full_battery
        battery = generate_full_battery(n_per_category=n_per_category, seed=seed)
        log.info("Full battery: %d traps from %d categories",
                 len(battery), len(set(t["category"] for t in battery)))
        return battery
    except ImportError:
        log.warning("Extended generators not available, falling back to base")
        from trap_generator import generate_trap_battery
        battery = generate_trap_battery(n_per_category=n_per_category, seed=seed)
        # Add tier tag to base traps
        for t in battery:
            t.setdefault("tier", "A")
        return battery


def evaluate_tool_expanded(tool, battery):
    """Evaluate a single tool on the expanded battery.

    Returns dict with per-tier accuracy, fallback rate, per-category results.
    """
    tier_a_correct = 0
    tier_a_total = 0
    tier_b_correct = 0
    tier_b_total = 0
    category_results = defaultdict(lambda: {"correct": 0, "total": 0})
    fallback_count = 0
    confidence_when_correct = []
    confidence_when_wrong = []
    reasoning_types = Counter()

    for trap in battery:
        prompt = trap["prompt"]
        candidates = trap["candidates"]
        correct = trap["correct"]
        category = trap["category"]
        tier = trap.get("tier", "A")

        try:
            ranked = tool.evaluate(prompt, candidates)
            if not ranked:
                continue

            top = ranked[0]
            is_correct = top["candidate"] == correct
            reasoning = top.get("reasoning", "")

            # Track fallback usage
            if "fallback:ncd" in reasoning.lower() or "ncd" in reasoning.lower():
                fallback_count += 1
                reasoning_types["fallback"] += 1
            elif "execution:" in reasoning.lower():
                reasoning_types["execution"] += 1
            elif "structural:" in reasoning.lower():
                reasoning_types["structural"] += 1
            else:
                reasoning_types["other"] += 1

            # Track per-tier
            if tier == "A":
                tier_a_total += 1
                if is_correct:
                    tier_a_correct += 1
            else:
                tier_b_total += 1
                if is_correct:
                    tier_b_correct += 1

            # Track per-category
            category_results[category]["total"] += 1
            if is_correct:
                category_results[category]["correct"] += 1

            # Track confidence calibration
            try:
                conf = tool.confidence(prompt, correct)
                if is_correct:
                    confidence_when_correct.append(conf)
                else:
                    confidence_when_wrong.append(conf)
            except Exception:
                pass

        except Exception:
            if tier == "A":
                tier_a_total += 1
            else:
                tier_b_total += 1
            category_results[category]["total"] += 1

    total = tier_a_total + tier_b_total
    fallback_rate = fallback_count / total if total > 0 else 1.0

    # Epistemic honesty: are we less confident when falling back?
    avg_conf_correct = float(np.mean(confidence_when_correct)) if confidence_when_correct else 0.0
    avg_conf_wrong = float(np.mean(confidence_when_wrong)) if confidence_when_wrong else 0.0
    epistemic_honesty = avg_conf_correct - avg_conf_wrong  # positive = well calibrated

    return {
        "tier_a_accuracy": tier_a_correct / tier_a_total if tier_a_total > 0 else 0.0,
        "tier_a_total": tier_a_total,
        "tier_b_accuracy": tier_b_correct / tier_b_total if tier_b_total > 0 else 0.0,
        "tier_b_total": tier_b_total,
        "overall_accuracy": (tier_a_correct + tier_b_correct) / total if total > 0 else 0.0,
        "fallback_rate": fallback_rate,
        "epistemic_honesty": epistemic_honesty,
        "avg_confidence_correct": avg_conf_correct,
        "avg_confidence_wrong": avg_conf_wrong,
        "reasoning_types": dict(reasoning_types),
        "category_results": {k: dict(v) for k, v in category_results.items()},
    }


def main():
    start = time.time()
    log.info("Loading expanded battery...")

    # Evolution battery (for scoring)
    battery = load_expanded_battery(seed=42, n_per_category=2)
    # Held-out battery (for validation)
    held_out = load_expanded_battery(seed=137, n_per_category=2)

    categories = sorted(set(t["category"] for t in battery))
    tier_a_cats = sorted(set(t["category"] for t in battery if t.get("tier") == "A"))
    tier_b_cats = sorted(set(t["category"] for t in battery if t.get("tier") == "B"))
    log.info("Categories: %d total (%d Tier A, %d Tier B)",
             len(categories), len(tier_a_cats), len(tier_b_cats))

    # Get all v3 tools (exclude utility files)
    tools = sorted(p for p in V3_DIR.glob("*.py") if not p.name.startswith("_"))
    log.info("Tools to evaluate: %d", len(tools))

    # NCD baseline
    ncd_tool = type("NCD", (), {
        "evaluate": lambda self, p, c: sorted(
            [{"candidate": x, "score": 1.0 - len(
                __import__("zlib").compress((p + x).encode())) / max(
                len(__import__("zlib").compress(p.encode())),
                len(__import__("zlib").compress(x.encode())), 1),
              "reasoning": "fallback:ncd"} for x in c],
            key=lambda r: r["score"], reverse=True),
        "confidence": lambda self, p, a: 0.5,
    })()
    ncd_results = evaluate_tool_expanded(ncd_tool, battery)
    log.info("NCD baseline: Tier A=%.0f%% Tier B=%.0f%% Overall=%.0f%%",
             ncd_results["tier_a_accuracy"] * 100,
             ncd_results["tier_b_accuracy"] * 100,
             ncd_results["overall_accuracy"] * 100)

    # Evaluate all tools
    results = {}
    for i, py in enumerate(tools):
        if (i + 1) % 25 == 0:
            log.info("  Evaluated %d/%d tools...", i + 1, len(tools))
        try:
            tool = load_tool_from_file(py)

            # Score on evolution battery
            ev = evaluate_tool_expanded(tool, battery)

            # Score on held-out battery
            ho = evaluate_tool_expanded(tool, held_out)

            results[py.stem] = {
                "evolution": ev,
                "held_out": {
                    "tier_a_accuracy": ho["tier_a_accuracy"],
                    "tier_b_accuracy": ho["tier_b_accuracy"],
                    "overall_accuracy": ho["overall_accuracy"],
                },
                "gap": ev["overall_accuracy"] - ho["overall_accuracy"],
            }
        except Exception as e:
            results[py.stem] = {"error": str(e)}

    elapsed = time.time() - start
    log.info("Evaluation complete in %.1f minutes", elapsed / 60)

    # Compute aggregate stats
    ev_tier_a = [r["evolution"]["tier_a_accuracy"] for r in results.values() if "evolution" in r]
    ev_tier_b = [r["evolution"]["tier_b_accuracy"] for r in results.values() if "evolution" in r]
    ev_overall = [r["evolution"]["overall_accuracy"] for r in results.values() if "evolution" in r]
    ev_fallback = [r["evolution"]["fallback_rate"] for r in results.values() if "evolution" in r]
    ev_honesty = [r["evolution"]["epistemic_honesty"] for r in results.values() if "evolution" in r]
    ho_overall = [r["held_out"]["overall_accuracy"] for r in results.values() if "held_out" in r]
    gaps = [r["gap"] for r in results.values() if "gap" in r]

    report = {
        "total_tools": len(results),
        "total_categories": len(categories),
        "tier_a_categories": len(tier_a_cats),
        "tier_b_categories": len(tier_b_cats),
        "traps_per_battery": len(battery),
        "ncd_baseline": ncd_results,
        "tier_a_median_acc": round(float(np.median(ev_tier_a)) * 100, 1) if ev_tier_a else 0,
        "tier_b_median_acc": round(float(np.median(ev_tier_b)) * 100, 1) if ev_tier_b else 0,
        "overall_median_acc": round(float(np.median(ev_overall)) * 100, 1) if ev_overall else 0,
        "held_out_median_acc": round(float(np.median(ho_overall)) * 100, 1) if ho_overall else 0,
        "median_fallback_rate": round(float(np.median(ev_fallback)) * 100, 1) if ev_fallback else 0,
        "median_epistemic_honesty": round(float(np.median(ev_honesty)), 3) if ev_honesty else 0,
        "median_gap": round(float(np.median(gaps)) * 100, 1) if gaps else 0,
        "tools_80_plus_overall": sum(1 for a in ev_overall if a >= 0.8),
        "tools_overfit": sum(1 for g in gaps if g > 0.5),
        "elapsed_minutes": round(elapsed / 60, 1),
        "per_tool_results": results,
    }

    # Save JSON
    REPORT_JSON.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    log.info("Report saved: %s", REPORT_JSON)

    # Build markdown report
    md = [
        "# Expanded Battery Report",
        "",
        f"*{len(battery)} traps across {len(categories)} categories "
        f"({len(tier_a_cats)} Tier A, {len(tier_b_cats)} Tier B)*",
        f"*{len(results)} tools evaluated in {elapsed/60:.1f} minutes*",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Tier A median accuracy | {report['tier_a_median_acc']}% |",
        f"| Tier B median accuracy | {report['tier_b_median_acc']}% |",
        f"| Overall median accuracy | {report['overall_median_acc']}% |",
        f"| Held-out median accuracy | {report['held_out_median_acc']}% |",
        f"| Median fallback rate | {report['median_fallback_rate']}% |",
        f"| Median epistemic honesty | {report['median_epistemic_honesty']} |",
        f"| Median seen-unseen gap | {report['median_gap']}% |",
        f"| Tools 80%+ overall | {report['tools_80_plus_overall']} |",
        f"| Tools overfit (gap>50%) | {report['tools_overfit']} |",
        "",
        "## Top 20 by Held-Out Accuracy",
        "",
        f"| Tool | Tier A | Tier B | Overall | Held-Out | Fallback | Honesty |",
        f"|------|--------|--------|---------|----------|----------|---------|",
    ]

    sorted_tools = sorted(
        [(name, r) for name, r in results.items() if "held_out" in r],
        key=lambda x: x[1]["held_out"]["overall_accuracy"],
        reverse=True
    )

    for name, r in sorted_tools[:20]:
        ev = r["evolution"]
        ho = r["held_out"]
        md.append(
            f"| {name[:50]} | {ev['tier_a_accuracy']*100:.0f}% | "
            f"{ev['tier_b_accuracy']*100:.0f}% | {ev['overall_accuracy']*100:.0f}% | "
            f"{ho['overall_accuracy']*100:.0f}% | {ev['fallback_rate']*100:.0f}% | "
            f"{ev['epistemic_honesty']:.2f} |"
        )

    # Per-category accuracy (aggregated across all tools)
    md += ["", "## Per-Category Accuracy (median across all tools)", ""]
    cat_medians = {}
    for cat in categories:
        cat_accs = []
        for r in results.values():
            if "evolution" not in r:
                continue
            cr = r["evolution"]["category_results"].get(cat, {})
            if cr.get("total", 0) > 0:
                cat_accs.append(cr["correct"] / cr["total"])
        if cat_accs:
            cat_medians[cat] = float(np.median(cat_accs))

    md.append(f"| Category | Median Acc | Tier |")
    md.append(f"|----------|-----------|------|")
    for cat, med in sorted(cat_medians.items(), key=lambda x: -x[1]):
        tier = "A" if cat in [t["category"] for t in battery if t.get("tier") == "A"] else "B"
        md.append(f"| {cat} | {med*100:.0f}% | {tier} |")

    REPORT_MD.write_text("\n".join(md), encoding="utf-8")
    log.info("Markdown report saved: %s", REPORT_MD)

    # Print summary
    print()
    print("=" * 70)
    print("  EXPANDED BATTERY RESULTS")
    print("=" * 70)
    print(f"  Tools:       {report['total_tools']}")
    print(f"  Categories:  {report['total_categories']} ({report['tier_a_categories']} Tier A, {report['tier_b_categories']} Tier B)")
    print(f"  Tier A acc:  {report['tier_a_median_acc']}% median")
    print(f"  Tier B acc:  {report['tier_b_median_acc']}% median")
    print(f"  Overall:     {report['overall_median_acc']}% median")
    print(f"  Held-out:    {report['held_out_median_acc']}% median")
    print(f"  Fallback:    {report['median_fallback_rate']}% median")
    print(f"  Honesty:     {report['median_epistemic_honesty']}")
    print(f"  80%+ tools:  {report['tools_80_plus_overall']}")
    print(f"  Overfit:     {report['tools_overfit']}")
    print(f"  Time:        {report['elapsed_minutes']} min")
    print("=" * 70)


if __name__ == "__main__":
    main()
