"""
Failure Mode Mining — Turn Kills into Signals.
================================================
Meta-analysis of the falsification battery's own behavior.
Instead of discarding failed hypotheses, cluster the WAYS they fail.

Sources:
  1. shadow_preload.jsonl — 6240 hypothesis records with per-F-test verdicts
  2. bridge_hunter_results.jsonl — 282K test records with hypothesis types
  3. genocide rounds r2-r7 — structured kill/survive records
  4. shadow_tensor.json — aggregated cell-level statistics

Output: failure_mode_results.json
"""

import json
import math
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]  # F:/Prometheus
CONVERGENCE = ROOT / "cartography" / "convergence" / "data"
V2 = Path(__file__).resolve().parent

# Input files
SHADOW_PRELOAD = CONVERGENCE / "shadow_preload.jsonl"
BRIDGE_HUNTER = CONVERGENCE / "bridge_hunter_results.jsonl"
SHADOW_TENSOR = CONVERGENCE / "shadow_tensor.json"
GENOCIDE_FILES = [CONVERGENCE / f"genocide_r{i}_results.json" for i in range(2, 8)]

# F-test names and families
F_TEST_NAMES = {
    "F1_permutation_null": "F1",
    "F2_subset_stability": "F2",
    "F3_effect_size": "F3",
    "F4_confound_sweep": "F4",
    "F5_alternative_normalization": "F5",
    "F6_base_rate": "F6",
    "F7_dose_response": "F7",
    "F8_direction_consistency": "F8",
    "F9_simpler_explanation": "F9",
    "F10_outlier_sensitivity": "F10",
    "F11_cross_validation": "F11",
    "F12_partial_correlation": "F12",
    "F13_growth_rate_filter": "F13",
    "F14_phase_shift": "F14",
}

# Kill family taxonomy: group F-tests by failure mechanism
KILL_FAMILIES = {
    "statistical_null": ["F1_permutation_null", "F6_base_rate"],
    "effect_size_artifact": ["F3_effect_size", "F12_partial_correlation"],
    "normalization_sensitivity": ["F5_alternative_normalization", "F10_outlier_sensitivity"],
    "replication_failure": ["F2_subset_stability", "F8_direction_consistency", "F11_cross_validation"],
    "confound_or_simpler": ["F4_confound_sweep", "F9_simpler_explanation"],
    "growth_rate_artifact": ["F13_growth_rate_filter"],
    "phase_structure": ["F14_phase_shift"],
}

# Reverse map: F-test -> family
TEST_TO_FAMILY = {}
for family, tests in KILL_FAMILIES.items():
    for t in tests:
        TEST_TO_FAMILY[t] = family


def load_shadow_preload():
    """Load detailed hypothesis records with per-F-test battery results."""
    if not SHADOW_PRELOAD.exists():
        return []
    records = []
    with open(SHADOW_PRELOAD, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except Exception:
                continue
    return records


def load_bridge_hunter():
    """Load bridge hunter results (kills only, with hypothesis types)."""
    if not BRIDGE_HUNTER.exists():
        return []
    records = []
    with open(BRIDGE_HUNTER, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
                records.append(r)
            except Exception:
                continue
    return records


def load_genocide_results():
    """Load genocide round results."""
    all_tests = []
    for gf in GENOCIDE_FILES:
        if not gf.exists():
            continue
        try:
            data = json.loads(gf.read_text(encoding="utf-8"))
        except Exception:
            continue
        tests = data.get("tests", [])
        for t in tests:
            t["_source"] = gf.name
        all_tests.extend(tests)
    return all_tests


def load_shadow_tensor():
    """Load aggregated shadow tensor."""
    if not SHADOW_TENSOR.exists():
        return {}
    return json.loads(SHADOW_TENSOR.read_text(encoding="utf-8"))


def analyze_kill_distribution(preload_records):
    """Analyze which F-tests kill the most hypotheses."""
    kill_counts = Counter()
    total_kills = 0
    total_records = len(preload_records)

    for r in preload_records:
        if r.get("verdict") == "KILLED":
            total_kills += 1
            for kt in r.get("kill_tests", []):
                kill_counts[kt] += 1

    # Compute kill rate per test
    kill_dist = {}
    for test_name, count in kill_counts.most_common():
        short = F_TEST_NAMES.get(test_name, test_name)
        kill_dist[test_name] = {
            "short_name": short,
            "kill_count": count,
            "pct_of_all_kills": round(100 * count / total_kills, 2) if total_kills else 0,
            "pct_of_all_records": round(100 * count / total_records, 2) if total_records else 0,
        }

    return {
        "total_records": total_records,
        "total_kills": total_kills,
        "total_survives": total_records - total_kills,
        "kill_rate": round(total_kills / total_records, 4) if total_records else 0,
        "per_test": kill_dist,
    }


def analyze_pair_distribution(preload_records):
    """Analyze which dataset pairs produce the most kills."""
    pair_kills = Counter()
    pair_total = Counter()
    pair_survives = Counter()

    for r in preload_records:
        pair = r.get("pair", "unknown")
        pair_total[pair] += 1
        if r.get("verdict") == "KILLED":
            pair_kills[pair] += 1
        elif r.get("verdict") == "SURVIVES":
            pair_survives[pair] += 1

    pair_dist = {}
    for pair in pair_total:
        kills = pair_kills[pair]
        total = pair_total[pair]
        survives = pair_survives[pair]
        pair_dist[pair] = {
            "total": total,
            "kills": kills,
            "survives": survives,
            "kill_rate": round(kills / total, 4) if total else 0,
        }

    # Sort by kill count
    pair_dist = dict(sorted(pair_dist.items(), key=lambda x: -x[1]["kills"]))
    return pair_dist


def analyze_failure_patterns(preload_records):
    """Analyze whether kills are clean (1 test) or multi-test."""
    killed = [r for r in preload_records if r.get("verdict") == "KILLED"]

    n_kill_tests = Counter()
    for r in killed:
        n = len(r.get("kill_tests", []))
        n_kill_tests[n] += 1

    # Compute distribution
    pattern_dist = {
        "clean_kill_1_test": n_kill_tests.get(1, 0),
        "double_kill_2_tests": n_kill_tests.get(2, 0),
        "triple_kill_3_tests": n_kill_tests.get(3, 0),
        "multi_kill_4plus": sum(v for k, v in n_kill_tests.items() if k >= 4),
        "total_killed": len(killed),
    }

    # Average kill tests per kill
    all_kill_counts = [len(r.get("kill_tests", [])) for r in killed]
    if all_kill_counts:
        pattern_dist["mean_kill_tests"] = round(statistics.mean(all_kill_counts), 2)
        pattern_dist["median_kill_tests"] = statistics.median(all_kill_counts)

    # Kill test co-occurrence matrix
    cooccurrence = Counter()
    for r in killed:
        kt = sorted(r.get("kill_tests", []))
        for i in range(len(kt)):
            for j in range(i + 1, len(kt)):
                cooccurrence[(kt[i], kt[j])] += 1

    top_cooccurrences = []
    for (t1, t2), count in cooccurrence.most_common(15):
        top_cooccurrences.append({
            "test_1": F_TEST_NAMES.get(t1, t1),
            "test_2": F_TEST_NAMES.get(t2, t2),
            "test_1_full": t1,
            "test_2_full": t2,
            "co_kill_count": count,
        })

    pattern_dist["top_co_occurrences"] = top_cooccurrences
    return pattern_dist


def analyze_near_misses(preload_records):
    """Find hypotheses that nearly survived the battery."""
    killed = [r for r in preload_records if r.get("verdict") == "KILLED"]

    # Near-miss: passed >= 6 tests and failed <= 2
    near_misses = []
    for r in killed:
        passed = r.get("passed", 0)
        failed = r.get("failed", 0)
        skipped = r.get("skipped", 0)
        kill_tests = r.get("kill_tests", [])

        if passed >= 6 and failed <= 2:
            # Extract test-level p-values from the tests array
            test_details = {}
            for t in r.get("tests", []):
                tname = t.get("test", "")
                test_details[tname] = {
                    "verdict": t.get("verdict", ""),
                    "p_value": t.get("p_value"),
                    "z_score": t.get("z_score"),
                    "cohens_d": t.get("cohens_d"),
                }

            near_misses.append({
                "pair": r.get("pair", ""),
                "claim": r.get("claim", "")[:200],
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "kill_tests": kill_tests,
                "kill_families": list(set(TEST_TO_FAMILY.get(kt, "unknown") for kt in kill_tests)),
            })

    # Sort by most tests passed (closest to surviving)
    near_misses.sort(key=lambda x: (-x["passed"], x["failed"]))

    # Analyze what kills near-misses
    near_miss_killers = Counter()
    near_miss_families = Counter()
    for nm in near_misses:
        for kt in nm["kill_tests"]:
            near_miss_killers[kt] += 1
            fam = TEST_TO_FAMILY.get(kt, "unknown")
            near_miss_families[fam] += 1

    # Find the "almost real" (passed 7+ with only 1 fail)
    almost_real = [nm for nm in near_misses if nm["passed"] >= 7 and nm["failed"] == 1]

    return {
        "total_near_misses": len(near_misses),
        "almost_real_count": len(almost_real),
        "near_miss_killers": {
            F_TEST_NAMES.get(k, k): v for k, v in near_miss_killers.most_common()
        },
        "near_miss_families": dict(near_miss_families.most_common()),
        "top_near_misses": near_misses[:20],
        "almost_real": almost_real[:10],
    }


def analyze_kill_families(preload_records):
    """Classify all kills into family taxonomy."""
    killed = [r for r in preload_records if r.get("verdict") == "KILLED"]

    family_kills = defaultdict(int)
    family_records = defaultdict(list)

    for r in killed:
        # Determine primary kill family (the family of the first kill test)
        kill_tests = r.get("kill_tests", [])
        families_hit = set()
        for kt in kill_tests:
            fam = TEST_TO_FAMILY.get(kt, "unknown")
            families_hit.add(fam)
            family_kills[fam] += 1

        # Primary family = the one with the lowest-numbered test
        primary = "unknown"
        for kt in kill_tests:
            fam = TEST_TO_FAMILY.get(kt, "unknown")
            if fam != "unknown":
                primary = fam
                break
        family_records[primary].append(r)

    # Compute family statistics
    family_stats = {}
    for fam in KILL_FAMILIES:
        records = family_records.get(fam, [])
        n = len(records)

        # How many near-misses in this family?
        near_miss_in_family = sum(
            1 for r in records
            if r.get("passed", 0) >= 6 and r.get("failed", 0) <= 2
        )

        # Average passed tests before death
        avg_passed = 0
        if records:
            avg_passed = round(statistics.mean(r.get("passed", 0) for r in records), 2)

        family_stats[fam] = {
            "total_kills_involving": family_kills[fam],
            "primary_kills": n,
            "near_misses": near_miss_in_family,
            "avg_passed_before_death": avg_passed,
            "member_tests": [F_TEST_NAMES.get(t, t) for t in KILL_FAMILIES[fam]],
        }

    # Sort by total kills
    family_stats = dict(sorted(family_stats.items(), key=lambda x: -x[1]["total_kills_involving"]))
    return family_stats


def analyze_bridge_hunter_kills(hunter_records):
    """Analyze kill patterns from bridge hunter (hypothesis type distribution)."""
    type_kills = Counter()
    type_total = Counter()
    pair_type_kills = Counter()

    for r in hunter_records:
        h = r.get("hypothesis", {})
        tr = r.get("test_result", {})
        htype = h.get("type", "unknown")
        verdict = tr.get("verdict", "")
        type_total[htype] += 1

        if verdict == "FAIL":
            type_kills[htype] += 1
            d1 = h.get("d1", "")
            d2 = h.get("d2", "")
            if d1 and d2:
                pair_type_kills[f"{'--'.join(sorted([d1, d2]))}:{htype}"] += 1

    type_stats = {}
    for htype in type_total:
        total = type_total[htype]
        kills = type_kills.get(htype, 0)
        type_stats[htype] = {
            "total": total,
            "kills": kills,
            "kill_rate": round(kills / total, 4) if total else 0,
        }

    return {
        "by_type": dict(sorted(type_stats.items(), key=lambda x: -x[1]["kills"])),
        "top_pair_type_kills": [
            {"pair_type": k, "kills": v}
            for k, v in pair_type_kills.most_common(20)
        ],
    }


def analyze_genocide_patterns(genocide_records):
    """Analyze genocide round patterns."""
    kills = [t for t in genocide_records if "KILL" in t.get("tag", "").upper() or "KILL" in t.get("verdict", "").upper()]
    survives = [t for t in genocide_records if "SURVIV" in t.get("tag", "").upper() or "SURVIV" in t.get("verdict", "").upper()]

    # Categorize kill reasons
    kill_reasons = Counter()
    for k in kills:
        detail = k.get("detail", "")
        if "irrational" in detail.lower():
            kill_reasons["type_mismatch_irrational"] += 1
        elif "tautolog" in detail.lower() or "trivial" in detail.lower():
            kill_reasons["tautological"] += 1
        elif "data" in detail.lower() and ("limitation" in detail.lower() or "not parsed" in detail.lower()):
            kill_reasons["data_limitation"] += 1
        elif "insufficient" in detail.lower():
            kill_reasons["insufficient_data"] += 1
        elif "base rate" in detail.lower():
            kill_reasons["base_rate"] += 1
        else:
            kill_reasons["other"] += 1

    return {
        "total_tested": len(genocide_records),
        "kills": len(kills),
        "survives": len(survives),
        "kill_reasons": dict(kill_reasons.most_common()),
    }


def analyze_shadow_tensor_cells(shadow):
    """Analyze cell-level patterns from the shadow tensor."""
    cells = shadow.get("cells", {})
    meta = shadow.get("meta", {})

    # Find cells with highest kill rates
    high_kill_cells = []
    low_kill_cells = []
    for pk, cell in cells.items():
        n = cell.get("n_tested", 0)
        if n < 5:
            continue
        kr = cell.get("kill_rate", 0)
        if kr is None:
            continue
        entry = {
            "pair": pk,
            "n_tested": n,
            "n_killed": cell.get("n_killed", 0),
            "n_passed": cell.get("n_passed", 0),
            "kill_rate": kr,
            "anomaly_score": cell.get("anomaly_score", 0),
            "near_miss_count": cell.get("near_miss_count", 0),
            "best_p": cell.get("best_p", 1.0),
        }
        if kr > 0.5:
            high_kill_cells.append(entry)
        elif kr < 0.2 and n >= 10:
            low_kill_cells.append(entry)

    high_kill_cells.sort(key=lambda x: -x["kill_rate"])
    low_kill_cells.sort(key=lambda x: x["kill_rate"])

    return {
        "total_cells": meta.get("n_cells", 0),
        "explored_cells": meta.get("n_explored", 0),
        "total_tests": meta.get("total_tests", 0),
        "total_kills": meta.get("total_kills", 0),
        "total_passes": meta.get("total_passes", 0),
        "high_kill_rate_cells": high_kill_cells[:15],
        "low_kill_rate_cells": low_kill_cells[:10],
    }


def compute_recommendations(kill_dist, near_miss_analysis, family_stats):
    """Recommend new tests based on failure pattern analysis."""
    recommendations = []

    # Check which families have the most near-misses
    nm_families = near_miss_analysis.get("near_miss_families", {})
    if nm_families:
        top_nm_family = max(nm_families, key=nm_families.get)
        recommendations.append({
            "priority": 1,
            "recommendation": f"Strengthen '{top_nm_family}' tests - this family has the most near-misses ({nm_families[top_nm_family]})",
            "rationale": "Near-misses that slip through this family are the most likely false positives in our survivors",
        })

    # Check for tests that never kill
    per_test = kill_dist.get("per_test", {})
    all_tests = set(F_TEST_NAMES.keys())
    active_tests = set(per_test.keys())
    dormant = all_tests - active_tests
    if dormant:
        recommendations.append({
            "priority": 2,
            "recommendation": f"Investigate dormant tests: {[F_TEST_NAMES[t] for t in dormant]}",
            "rationale": "These tests never killed anything - either they're too lenient or never triggered",
        })

    # Check co-occurrence patterns - if F3 and F11 always co-kill, one might be redundant
    # But more importantly, independent kills are more valuable
    nm_killers = near_miss_analysis.get("near_miss_killers", {})
    if nm_killers:
        top_killer = max(nm_killers, key=nm_killers.get)
        recommendations.append({
            "priority": 3,
            "recommendation": f"The {top_killer} test is the primary near-miss killer - consider a stricter variant",
            "rationale": f"It kills {nm_killers[top_killer]} near-misses that passed most other tests",
        })

    # Check for prime confound
    per_test_data = kill_dist.get("per_test", {})
    f1_kills = per_test_data.get("F1_permutation_null", {}).get("kill_count", 0)
    f3_kills = per_test_data.get("F3_effect_size", {}).get("kill_count", 0)
    if f3_kills > f1_kills * 5:
        recommendations.append({
            "priority": 4,
            "recommendation": "Add F15: Prime detrending test",
            "rationale": f"F3 kills {f3_kills} vs F1 kills {f1_kills} - many hypotheses have real permutation signal but tiny effect size. A prime-detrending test would catch the 96%+ of cross-dataset structure that is just primes.",
        })

    # Transformation test for near-misses
    almost_real = near_miss_analysis.get("almost_real_count", 0)
    if almost_real > 0:
        recommendations.append({
            "priority": 5,
            "recommendation": f"Add transformation-based tests (Layer 3) for {almost_real} 'almost real' hypotheses",
            "rationale": "These passed 7+ tests but failed on 1. A transformation/embedding test could distinguish real-but-hard-to-see structure from artifacts.",
        })

    recommendations.sort(key=lambda x: x["priority"])
    return recommendations


def run_full_analysis():
    """Run the complete failure mode mining pipeline."""
    print("=" * 70)
    print("  FAILURE MODE MINING - Turn Kills into Signals")
    print("  Meta-analysis of the falsification battery")
    print("=" * 70)
    t0 = time.time()

    # Load data
    print("\n  Loading data sources...")
    preload = load_shadow_preload()
    print(f"    Shadow preload: {len(preload)} hypothesis records")

    hunter = load_bridge_hunter()
    print(f"    Bridge hunter: {len(hunter)} records")

    genocide = load_genocide_results()
    print(f"    Genocide rounds: {len(genocide)} records")

    shadow = load_shadow_tensor()
    print(f"    Shadow tensor: {shadow.get('meta', {}).get('n_cells', 0)} cells")

    # 1. Kill distribution by test
    print("\n  [1/7] Kill distribution by F-test...")
    kill_dist = analyze_kill_distribution(preload)
    print(f"    {kill_dist['total_kills']} kills across {kill_dist['total_records']} records")

    # 2. Kill distribution by pair
    print("  [2/7] Kill distribution by dataset pair...")
    pair_dist = analyze_pair_distribution(preload)
    top_pair = max(pair_dist, key=lambda k: pair_dist[k]["kills"]) if pair_dist else "none"
    print(f"    Top killer pair: {top_pair}")

    # 3. Failure patterns (clean vs multi-kill)
    print("  [3/7] Failure patterns...")
    failure_patterns = analyze_failure_patterns(preload)
    print(f"    Mean kill tests per death: {failure_patterns.get('mean_kill_tests', 0)}")

    # 4. Near-misses
    print("  [4/7] Near-miss analysis...")
    near_misses = analyze_near_misses(preload)
    print(f"    Near-misses (passed>=6): {near_misses['total_near_misses']}")
    print(f"    Almost real (passed>=7, failed=1): {near_misses['almost_real_count']}")

    # 5. Kill family taxonomy
    print("  [5/7] Kill family taxonomy...")
    family_stats = analyze_kill_families(preload)
    for fam, stats in family_stats.items():
        print(f"    {fam}: {stats['total_kills_involving']} kills, {stats['near_misses']} near-misses")

    # 6. Bridge hunter type analysis
    print("  [6/7] Bridge hunter kill types...")
    hunter_analysis = analyze_bridge_hunter_kills(hunter)
    for htype, stats in hunter_analysis["by_type"].items():
        print(f"    {htype}: {stats['kills']}/{stats['total']} killed ({stats['kill_rate']*100:.1f}%)")

    # 7. Shadow tensor cell analysis
    print("  [7/7] Shadow tensor cell analysis...")
    cell_analysis = analyze_shadow_tensor_cells(shadow)

    # Genocide patterns
    print("\n  Genocide round analysis...")
    genocide_analysis = analyze_genocide_patterns(genocide)
    print(f"    Kills: {genocide_analysis['kills']}, Survives: {genocide_analysis['survives']}")

    # Recommendations
    print("\n  Computing recommendations...")
    recommendations = compute_recommendations(kill_dist, near_misses, family_stats)

    elapsed = time.time() - t0

    # Build final results
    results = {
        "meta": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "elapsed_seconds": round(elapsed, 2),
            "sources": {
                "shadow_preload": len(preload),
                "bridge_hunter": len(hunter),
                "genocide_rounds": len(genocide),
                "shadow_tensor_cells": cell_analysis["total_cells"],
            },
        },
        "kill_distribution_by_test": kill_dist,
        "kill_distribution_by_pair": pair_dist,
        "failure_patterns": failure_patterns,
        "near_miss_analysis": near_misses,
        "kill_family_taxonomy": family_stats,
        "bridge_hunter_types": hunter_analysis,
        "genocide_patterns": genocide_analysis,
        "shadow_tensor_cells": cell_analysis,
        "recommendations": recommendations,
    }

    # Print summary
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"\n  Total hypothesis records analyzed: {len(preload) + len(hunter) + len(genocide)}")
    print(f"  Total kills (shadow preload): {kill_dist['total_kills']}")
    print(f"  Kill rate: {kill_dist['kill_rate']*100:.1f}%")

    print(f"\n  TOP KILLER F-TESTS:")
    for test_name, data in list(kill_dist["per_test"].items())[:5]:
        short = data["short_name"]
        print(f"    {short} ({test_name}): {data['kill_count']} kills ({data['pct_of_all_kills']:.1f}%)")

    print(f"\n  KILL FAMILY TAXONOMY:")
    for fam, stats in family_stats.items():
        print(f"    {fam}: {stats['total_kills_involving']} kills, "
              f"{stats['near_misses']} near-misses, "
              f"avg {stats['avg_passed_before_death']:.1f} tests passed before death")

    print(f"\n  NEAR-MISSES:")
    print(f"    Total near-misses (passed>=6, failed<=2): {near_misses['total_near_misses']}")
    print(f"    Almost real (passed>=7, failed=1): {near_misses['almost_real_count']}")
    print(f"    Primary near-miss killer: {list(near_misses['near_miss_killers'].keys())[:3]}")

    print(f"\n  FAILURE PATTERNS:")
    print(f"    Clean kills (1 test): {failure_patterns['clean_kill_1_test']}")
    print(f"    Double kills (2 tests): {failure_patterns['double_kill_2_tests']}")
    print(f"    Triple kills (3 tests): {failure_patterns['triple_kill_3_tests']}")
    print(f"    Multi kills (4+ tests): {failure_patterns['multi_kill_4plus']}")

    print(f"\n  RECOMMENDATIONS:")
    for rec in recommendations:
        print(f"    [{rec['priority']}] {rec['recommendation']}")
        print(f"        {rec['rationale']}")

    # Save
    out_path = V2 / "failure_mode_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n  Results saved to {out_path}")
    print(f"  Elapsed: {elapsed:.1f}s")
    return results


if __name__ == "__main__":
    run_full_analysis()
