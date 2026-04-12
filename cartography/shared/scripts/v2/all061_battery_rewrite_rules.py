"""
ALL-061: Battery Failure-Mode Rewrite Rules
=============================================
Analyse the battery sweep to find failure patterns:
1. Which hypotheses fail consistently? (fragile vs robust)
2. Do failures cluster by domain (EC, MF, G2)?
3. Can we extract "rewrite rules": IF hypothesis has property X → THEN it fails test Y?
4. What is the false-positive rate of the battery?
"""
import json, time
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

V2 = Path(__file__).resolve().parent
BATTERY = V2.parents[3] / "cartography" / "convergence" / "data" / "battery_sweep_v2.jsonl"
BRIDGES = V2.parents[3] / "cartography" / "convergence" / "data" / "bridges.jsonl"
OUT = V2 / "all061_battery_rewrite_results.json"

def main():
    t0 = time.time()
    print("=== ALL-061: Battery Failure-Mode Rewrite Rules ===\n")

    # Load battery results
    print("[1] Loading battery sweep...")
    records = []
    with open(BATTERY) as f:
        for line in f:
            if line.strip():
                try: records.append(json.loads(line))
                except: pass
    print(f"  {len(records)} records")
    sample = records[0] if records else {}
    print(f"  Fields: {list(sample.keys())}")

    # Identify verdict field
    verdict_field = None
    for k in ["verdict", "status", "result", "pass", "outcome"]:
        if k in sample:
            verdict_field = k; break

    # Identify domain/category field
    domain_field = None
    for k in ["domain", "category", "type", "source", "dataset"]:
        if k in sample:
            domain_field = k; break

    # Identify hypothesis text
    hyp_field = None
    for k in ["hypothesis", "description", "text", "label", "name"]:
        if k in sample:
            hyp_field = k; break

    print(f"  verdict_field: {verdict_field}")
    print(f"  domain_field: {domain_field}")
    print(f"  hyp_field: {hyp_field}")

    # Verdict distribution
    if verdict_field:
        verdicts = Counter(r.get(verdict_field) for r in records)
        print(f"\n  Verdict distribution:")
        for v, cnt in verdicts.most_common():
            print(f"    {v}: {cnt} ({cnt/len(records):.1%})")

    # Domain distribution
    if domain_field:
        domains = Counter(r.get(domain_field) for r in records)
        print(f"\n  Domain distribution:")
        for d, cnt in domains.most_common():
            print(f"    {d}: {cnt}")

    # Failure analysis: verdicts by domain
    if verdict_field and domain_field:
        print(f"\n  Failure rate by domain:")
        domain_verdicts = defaultdict(Counter)
        for r in records:
            d = r.get(domain_field, "unknown")
            v = r.get(verdict_field, "unknown")
            domain_verdicts[d][v] += 1

        domain_failure = {}
        for d, vc in sorted(domain_verdicts.items()):
            total = sum(vc.values())
            fail_count = vc.get("FAIL", 0) + vc.get("fail", 0) + vc.get("rejected", 0) + vc.get("falsified", 0)
            fail_rate = fail_count / total if total > 0 else 0
            domain_failure[d] = {
                "total": total,
                "fail": fail_count,
                "fail_rate": round(fail_rate, 4),
                "verdicts": dict(vc),
            }
            print(f"    {d}: {fail_count}/{total} = {fail_rate:.1%}")

    # Numeric field analysis for rewrite rules
    print(f"\n  Numeric field statistics:")
    numeric_fields = {}
    for k, v in sample.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            vals = [r.get(k) for r in records if isinstance(r.get(k), (int, float))]
            if vals:
                arr = np.array(vals)
                numeric_fields[k] = {
                    "mean": round(float(arr.mean()), 4),
                    "std": round(float(arr.std()), 4),
                    "min": round(float(arr.min()), 4),
                    "max": round(float(arr.max()), 4),
                }
                print(f"    {k}: mean={arr.mean():.4f}, std={arr.std():.4f}")

    # Rewrite rule extraction: find fields that predict verdict
    rules = []
    if verdict_field:
        pass_vals = set(v for v, _ in verdicts.most_common(1))
        for k in numeric_fields:
            vals = [(r.get(k), r.get(verdict_field)) for r in records
                    if isinstance(r.get(k), (int, float)) and r.get(verdict_field)]
            if not vals: continue
            pass_v = [v for v, vd in vals if vd in pass_vals]
            fail_v = [v for v, vd in vals if vd not in pass_vals]
            if pass_v and fail_v:
                from scipy import stats as sp_stats
                stat, p_val = sp_stats.mannwhitneyu(pass_v, fail_v, alternative='two-sided')
                if p_val < 0.05:
                    rules.append({
                        "field": k,
                        "pass_mean": round(float(np.mean(pass_v)), 4),
                        "fail_mean": round(float(np.mean(fail_v)), 4),
                        "mwu_pvalue": float(p_val),
                        "rule": f"IF {k} {'>' if np.mean(pass_v) > np.mean(fail_v) else '<'} "
                                f"{(np.mean(pass_v)+np.mean(fail_v))/2:.2f} THEN likely PASS",
                    })

    print(f"\n  Rewrite rules extracted: {len(rules)}")
    for rule in rules:
        print(f"    {rule['rule']} (p={rule['mwu_pvalue']:.4e})")

    # Load bridges for concept enrichment
    print("\n[2] Loading bridges for concept analysis...")
    bridges = []
    with open(BRIDGES) as f:
        for line in f:
            if line.strip():
                try: bridges.append(json.loads(line))
                except: pass
    print(f"  {len(bridges)} bridge concepts")

    # Top bridges by specificity
    top_bridges = sorted(bridges, key=lambda b: -b.get("specificity", 0))[:10]
    print(f"\n  Top bridges by specificity:")
    for b in top_bridges:
        print(f"    {b.get('concept', b.get('name', '?'))}: "
              f"spec={b.get('specificity', 0):.4f}, datasets={b.get('n_datasets', 0)}")

    elapsed = time.time() - t0
    output = {
        "challenge": "ALL-061", "title": "Battery Failure-Mode Rewrite Rules",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_records": len(records),
        "verdict_distribution": dict(verdicts) if verdict_field else {},
        "domain_failure_rates": domain_failure if verdict_field and domain_field else {},
        "numeric_fields": numeric_fields,
        "rewrite_rules": rules,
        "n_bridges": len(bridges),
        "top_bridges": [{"concept": b.get("concept", ""), "specificity": b.get("specificity", 0)}
                       for b in top_bridges],
        "assessment": None,
    }

    if rules:
        output["assessment"] = f"RULES FOUND: {len(rules)} rewrite rules. Top: {rules[0]['rule']}"
    elif verdict_field:
        output["assessment"] = f"NO RULES: verdict distribution {dict(verdicts)} but no numeric predictors of failure"
    else:
        output["assessment"] = f"NO VERDICT FIELD: battery uses {list(sample.keys())} — cannot extract failure patterns"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
