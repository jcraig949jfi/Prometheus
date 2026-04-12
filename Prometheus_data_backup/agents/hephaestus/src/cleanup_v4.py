#!/usr/bin/env python3
"""One-time cleanup + scoring for v4 library.

1. Score ALL v4 tools on 58-category battery (seen + unseen)
2. Investigate the 0% fallback rate
3. Generate all_scores.json for Apollo/Athena seed selection
4. Report epistemic honesty distribution

Usage:
    python cleanup_v4.py
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
from trap_generator_extended import generate_full_battery

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CLEANUP] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("cleanup")

HEPH_ROOT = Path(__file__).resolve().parent.parent
V4_DIR = HEPH_ROOT / "forge_v4"


def investigate_fallback_rate(tool, battery, tool_name=""):
    """Deep investigation of why fallback rate is 0%.

    Check: are reasoning strings actually containing fallback tags?
    Check: are structural parsers firing on everything?
    Check: is it an instrumentation issue?
    """
    fallback_tagged = 0
    structural_tagged = 0
    computation_tagged = 0
    judgment_tagged = 0
    no_tag = 0
    empty_reasoning = 0

    sample_reasonings = []

    for trap in battery[:20]:  # Sample 20
        try:
            ranked = tool.evaluate(trap["prompt"], trap["candidates"])
            if ranked:
                r = ranked[0].get("reasoning", "")
                if not r:
                    empty_reasoning += 1
                elif "fallback" in r.lower():
                    fallback_tagged += 1
                elif "computation" in r.lower() or "comp" in r.lower():
                    computation_tagged += 1
                elif "structural" in r.lower() or "struct" in r.lower():
                    structural_tagged += 1
                elif "judgment" in r.lower():
                    judgment_tagged += 1
                else:
                    no_tag += 1

                if len(sample_reasonings) < 5:
                    sample_reasonings.append({
                        "prompt": trap["prompt"][:60],
                        "category": trap["category"],
                        "reasoning": r[:100],
                    })
        except Exception:
            pass

    total = fallback_tagged + structural_tagged + computation_tagged + judgment_tagged + no_tag + empty_reasoning
    return {
        "fallback_tagged": fallback_tagged,
        "structural_tagged": structural_tagged,
        "computation_tagged": computation_tagged,
        "judgment_tagged": judgment_tagged,
        "no_tag": no_tag,
        "empty_reasoning": empty_reasoning,
        "total_checked": total,
        "samples": sample_reasonings,
    }


def main():
    start = time.time()

    # Load batteries
    seen = generate_full_battery(n_per_category=2, seed=42)
    unseen = generate_full_battery(n_per_category=2, seed=137)
    log.info("Batteries: seen=%d unseen=%d traps, %d categories",
             len(seen), len(unseen), len(set(t["category"] for t in seen)))

    # Get all v4 tools
    tools = sorted(p for p in V4_DIR.glob("*.py") if not p.name.startswith("_"))
    log.info("v4 tools: %d", len(tools))

    # Categorize traps
    tier_a_seen = [t for t in seen if t.get("tier") == "A"]
    tier_b_seen = [t for t in seen if t.get("tier") == "B"]
    categories = sorted(set(t["category"] for t in seen))

    # Score all tools
    results = {}
    fallback_investigation = {}
    honesty_distribution = []

    for i, py in enumerate(tools):
        if (i + 1) % 50 == 0:
            log.info("  Scored %d/%d...", i + 1, len(tools))

        try:
            tool = load_tool_from_file(py)

            # Investigate fallback on first 10 tools
            if i < 10:
                fb_info = investigate_fallback_rate(tool, seen, py.stem)
                fallback_investigation[py.stem] = fb_info

            # Score on seen battery
            s_a_c = s_a_t = s_b_c = s_b_t = 0
            conf_correct = []
            conf_wrong = []
            category_results = {}
            fallback_count = 0

            for trap in seen:
                cat = trap["category"]
                tier = trap.get("tier", "A")
                try:
                    ranked = tool.evaluate(trap["prompt"], trap["candidates"])
                    if ranked:
                        ok = ranked[0]["candidate"] == trap["correct"]
                        reasoning = ranked[0].get("reasoning", "")

                        if "fallback" in reasoning.lower() or "ncd" in reasoning.lower():
                            fallback_count += 1

                        if tier == "A":
                            s_a_t += 1
                            if ok: s_a_c += 1
                        else:
                            s_b_t += 1
                            if ok: s_b_c += 1

                        if cat not in category_results:
                            category_results[cat] = {"correct": 0, "total": 0}
                        category_results[cat]["total"] += 1
                        if ok:
                            category_results[cat]["correct"] += 1

                        try:
                            conf = tool.confidence(trap["prompt"], trap["correct"])
                            if ok:
                                conf_correct.append(conf)
                            else:
                                conf_wrong.append(conf)
                        except Exception:
                            pass
                except Exception:
                    if tier == "A": s_a_t += 1
                    else: s_b_t += 1

            # Score on unseen battery
            u_c = u_t = 0
            u_a_c = u_a_t = u_b_c = u_b_t = 0
            for trap in unseen:
                tier = trap.get("tier", "A")
                try:
                    ranked = tool.evaluate(trap["prompt"], trap["candidates"])
                    if ranked:
                        ok = ranked[0]["candidate"] == trap["correct"]
                        u_t += 1
                        if ok: u_c += 1
                        if tier == "A":
                            u_a_t += 1
                            if ok: u_a_c += 1
                        else:
                            u_b_t += 1
                            if ok: u_b_c += 1
                except Exception:
                    u_t += 1
                    if tier == "A": u_a_t += 1
                    else: u_b_t += 1

            # Compute metrics
            sa = s_a_c / s_a_t if s_a_t else 0
            sb = s_b_c / s_b_t if s_b_t else 0
            so = (s_a_c + s_b_c) / (s_a_t + s_b_t) if (s_a_t + s_b_t) else 0
            ua = u_c / u_t if u_t else 0
            ua_a = u_a_c / u_a_t if u_a_t else 0
            ua_b = u_b_c / u_b_t if u_b_t else 0

            avg_cc = float(np.mean(conf_correct)) if conf_correct else 0.5
            avg_cw = float(np.mean(conf_wrong)) if conf_wrong else 0.5
            honesty = avg_cc - avg_cw
            honesty_distribution.append(honesty)

            fb_rate = fallback_count / (s_a_t + s_b_t) if (s_a_t + s_b_t) else 1

            results[py.stem] = {
                "seen_tier_a": round(sa, 4),
                "seen_tier_b": round(sb, 4),
                "seen_overall": round(so, 4),
                "unseen_tier_a": round(ua_a, 4),
                "unseen_tier_b": round(ua_b, 4),
                "unseen_overall": round(ua, 4),
                "gap": round(so - ua, 4),
                "epistemic_honesty": round(honesty, 4),
                "avg_confidence_correct": round(avg_cc, 4),
                "avg_confidence_wrong": round(avg_cw, 4),
                "fallback_rate": round(fb_rate, 4),
                "category_results": {k: v for k, v in category_results.items()},
            }

        except Exception as e:
            results[py.stem] = {"error": str(e)[:80]}

    elapsed = time.time() - start
    log.info("Scoring complete in %.1f minutes", elapsed / 60)

    # Save all_scores.json
    output = {
        "metadata": {
            "total_tools": len(results),
            "total_categories": len(categories),
            "seen_battery_size": len(seen),
            "unseen_battery_size": len(unseen),
            "seen_seed": 42,
            "unseen_seed": 137,
            "generated_at": __import__("datetime").datetime.now().isoformat(),
        },
        "tools": results,
    }

    scores_path = V4_DIR / "all_scores.json"
    scores_path.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
    log.info("Saved: %s", scores_path)

    # Save fallback investigation
    fb_path = V4_DIR / "fallback_investigation.json"
    fb_path.write_text(json.dumps(fallback_investigation, indent=2), encoding="utf-8")
    log.info("Saved: %s", fb_path)

    # Print summary
    valid = [r for r in results.values() if "error" not in r]
    so_all = [r["seen_overall"] for r in valid]
    ua_all = [r["unseen_overall"] for r in valid]
    sa_all = [r["seen_tier_a"] for r in valid]
    sb_all = [r["seen_tier_b"] for r in valid]
    h_all = [r["epistemic_honesty"] for r in valid]
    fb_all = [r["fallback_rate"] for r in valid]

    print()
    print("=" * 70)
    print("  v4 LIBRARY CLEANUP RESULTS")
    print("=" * 70)
    print(f"  Tools scored:     {len(valid)} ({len(results) - len(valid)} errors)")
    print(f"  Categories:       {len(categories)}")
    print()
    print(f"  Seen Overall:     {np.median(so_all)*100:.1f}% median")
    print(f"  Seen Tier A:      {np.median(sa_all)*100:.1f}% median")
    print(f"  Seen Tier B:      {np.median(sb_all)*100:.1f}% median")
    print(f"  Unseen Overall:   {np.median(ua_all)*100:.1f}% median")
    print(f"  80%+ unseen:      {sum(1 for u in ua_all if u >= 0.8)}/{len(valid)}")
    print()
    print(f"  Epistemic Honesty:")
    print(f"    Median:         {np.median(h_all):.3f}")
    print(f"    Top quartile:   {np.percentile(h_all, 75):.3f}")
    print(f"    >= 0.3:         {sum(1 for h in h_all if h >= 0.3)}/{len(valid)}")
    print(f"    >= 0.5:         {sum(1 for h in h_all if h >= 0.5)}/{len(valid)}")
    print()
    print(f"  Fallback Rate:")
    print(f"    Median:         {np.median(fb_all)*100:.1f}%")
    print(f"    > 0:            {sum(1 for f in fb_all if f > 0)}/{len(valid)}")
    print()
    print("  Fallback Investigation (first 10 tools):")
    for name, info in list(fallback_investigation.items())[:5]:
        print(f"    {name[:45]}:")
        print(f"      tagged: fb={info['fallback_tagged']} struct={info['structural_tagged']} "
              f"comp={info['computation_tagged']} judge={info['judgment_tagged']} "
              f"none={info['no_tag']} empty={info['empty_reasoning']}")
        if info["samples"]:
            s = info["samples"][0]
            print(f"      sample: [{s['category']}] {s['reasoning'][:70]}")

    # Apollo seed selection file
    seeds = []
    for name, r in sorted(results.items(), key=lambda x: x[1].get("unseen_overall", 0), reverse=True):
        if "error" in r:
            continue
        seeds.append({
            "name": name,
            "unseen_overall": r["unseen_overall"],
            "unseen_tier_a": r["unseen_tier_a"],
            "unseen_tier_b": r["unseen_tier_b"],
            "epistemic_honesty": r["epistemic_honesty"],
            "gap": r["gap"],
        })

    seeds_path = V4_DIR / "apollo_seed_candidates.json"
    seeds_path.write_text(json.dumps(seeds, indent=2), encoding="utf-8")
    log.info("Apollo seed candidates: %s (%d tools ranked by unseen accuracy)", seeds_path, len(seeds))

    print()
    print(f"  FILES FOR APOLLO/ATHENA:")
    print(f"    {scores_path}")
    print(f"    {seeds_path}")
    print(f"    {fb_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
