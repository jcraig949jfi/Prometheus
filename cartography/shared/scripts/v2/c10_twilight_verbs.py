"""
Challenge 10: Mine the Twilight Realm for Verb Artifacts
==========================================================
Profile the battery hypotheses by their killing test.
Which specific test banishes the most objects to the twilight realm?
Is there a syntactic pattern to what kills?
"""
import json, time
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

V2 = Path(__file__).resolve().parent
BATTERY = V2.parents[3] / "cartography" / "convergence" / "data" / "battery_sweep_v2.jsonl"
OUT = V2 / "c10_twilight_verbs_results.json"

def main():
    t0 = time.time()
    print("=== C10: Mine the Twilight Realm ===\n")

    records = []
    with open(BATTERY) as f:
        for line in f:
            if line.strip():
                try: records.append(json.loads(line))
                except: pass
    print(f"  {len(records)} battery records")

    # Classify: SURVIVES, KILLED, and degree of killing
    survives = [r for r in records if r.get("verdict") == "SURVIVES"]
    killed = [r for r in records if r.get("verdict") == "KILLED"]
    print(f"  SURVIVES: {len(survives)}, KILLED: {len(killed)}")

    # For killed records: which tests killed them?
    kill_test_dist = Counter()
    n_kill_tests = Counter()
    for r in killed:
        kt = r.get("kill_tests", [])
        n_kill_tests[len(kt)] += 1
        for test in kt:
            kill_test_dist[test] += 1

    print(f"\n  Kill test distribution:")
    for test, cnt in kill_test_dist.most_common():
        print(f"    {test}: {cnt} ({cnt/len(killed):.0%} of killed)")

    print(f"\n  Number of killing tests per record:")
    for n, cnt in sorted(n_kill_tests.items()):
        print(f"    {n} tests: {cnt} records")

    # TWILIGHT REALM: killed by exactly 1 test
    twilight = [r for r in killed if len(r.get("kill_tests", [])) == 1]
    print(f"\n  Twilight realm (killed by exactly 1 test): {len(twilight)}")

    # Which single test most often banishes?
    twilight_killers = Counter()
    for r in twilight:
        kt = r.get("kill_tests", [])
        if kt: twilight_killers[kt[0]] += 1
    print(f"  Twilight killers:")
    for test, cnt in twilight_killers.most_common():
        print(f"    {test}: {cnt} ({cnt/len(twilight):.0%})")

    # Profile twilight by source/layer
    twilight_sources = Counter(r.get("source", "?") for r in twilight)
    twilight_layers = Counter(r.get("layer", "?") for r in twilight)
    print(f"\n  Twilight by source: {dict(twilight_sources)}")
    print(f"  Twilight by layer: {dict(twilight_layers)}")

    # Deep shadow: killed by ALL tests
    deep_shadow = [r for r in killed if len(r.get("kill_tests", [])) >= 4]
    shadow_sources = Counter(r.get("source", "?") for r in deep_shadow)
    print(f"\n  Deep shadow (killed by ≥4 tests): {len(deep_shadow)}")
    print(f"  Shadow sources: {dict(shadow_sources)}")

    # Delta_pct distribution: twilight vs shadow vs survives
    tw_deltas = [r.get("delta_pct", 0) for r in twilight if isinstance(r.get("delta_pct"), (int, float))]
    sh_deltas = [r.get("delta_pct", 0) for r in deep_shadow if isinstance(r.get("delta_pct"), (int, float))]
    sv_deltas = [r.get("delta_pct", 0) for r in survives if isinstance(r.get("delta_pct"), (int, float))]

    print(f"\n  Delta_pct by realm:")
    if tw_deltas: print(f"    Twilight: mean={np.mean(tw_deltas):.1f}, std={np.std(tw_deltas):.1f}")
    if sh_deltas: print(f"    Shadow: mean={np.mean(sh_deltas):.1f}, std={np.std(sh_deltas):.1f}")
    if sv_deltas: print(f"    Survives: mean={np.mean(sv_deltas):.1f}, std={np.std(sv_deltas):.1f}")

    # Statistical test: is twilight delta_pct different from survives?
    from scipy import stats
    if tw_deltas and sv_deltas:
        stat, p_val = stats.mannwhitneyu(tw_deltas, sv_deltas, alternative='two-sided')
        print(f"\n  MWU twilight vs survives: U={stat:.0f}, p={p_val:.4e}")
    else:
        p_val = 1.0

    # Verb-like analysis of kill tests
    # Classify tests by what they measure
    test_types = {
        "F1_permutation_null": "statistical_null",
        "F6_base_rate": "baseline",
        "F9_simpler_explanation": "parsimony",
        "F11_cross_validation": "robustness",
        "F3_effect_size": "magnitude",
        "F13_growth_rate": "dynamics",
        "F14_phase_shift": "oscillation",
    }

    # Which TYPE of test kills most in twilight?
    type_kills = Counter()
    for r in twilight:
        kt = r.get("kill_tests", [])
        if kt:
            test = kt[0]
            test_type = test_types.get(test, "unknown")
            type_kills[test_type] += 1

    print(f"\n  Kill types in twilight:")
    for t, cnt in type_kills.most_common():
        print(f"    {t}: {cnt}")

    # Specific OEIS IDs in twilight (if available)
    twilight_ids = [r.get("seq_id", "?") for r in twilight]
    print(f"\n  Sample twilight IDs: {twilight_ids[:20]}")

    elapsed = time.time() - t0
    output = {
        "challenge": "C10", "title": "Twilight Realm Verb Profiling",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_records": len(records),
        "n_survives": len(survives), "n_killed": len(killed),
        "n_twilight": len(twilight), "n_deep_shadow": len(deep_shadow),
        "kill_test_distribution": dict(kill_test_dist),
        "twilight_killers": dict(twilight_killers),
        "twilight_by_source": dict(twilight_sources),
        "deep_shadow_by_source": dict(shadow_sources),
        "delta_pct": {
            "twilight_mean": round(float(np.mean(tw_deltas)), 1) if tw_deltas else None,
            "shadow_mean": round(float(np.mean(sh_deltas)), 1) if sh_deltas else None,
            "survives_mean": round(float(np.mean(sv_deltas)), 1) if sv_deltas else None,
            "mwu_pvalue": float(p_val),
        },
        "kill_type_distribution": dict(type_kills),
        "assessment": None,
    }

    top_killer = twilight_killers.most_common(1)[0] if twilight_killers else ("none", 0)
    top_type = type_kills.most_common(1)[0] if type_kills else ("none", 0)
    output["assessment"] = (
        f"TWILIGHT MAPPED: {len(twilight)} hypotheses killed by exactly 1 test. "
        f"Top banisher: {top_killer[0]} ({top_killer[1]} victims, {top_killer[1]/max(len(twilight),1):.0%}). "
        f"Type: {top_type[0]}. "
        f"Twilight delta_pct={np.mean(tw_deltas):.1f} vs survives={np.mean(sv_deltas):.1f} "
        f"(MWU p={p_val:.3e})."
    ) if tw_deltas and sv_deltas else "NO TWILIGHT DATA"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
