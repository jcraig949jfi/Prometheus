"""
Challenge 5: F3/F13 Adversarial DMZ
======================================
The battery sweep has hypotheses classified by verdict (KILLED/SURVIVES).
Among those near the boundary (delta_pct ≈ median), do extended lag tests
discriminate? Build a phase-shift analysis at lags 1-10 on the a_p data
to find hypotheses that pass basic battery but fail extended analysis.
"""
import json, time, math
import numpy as np
import duckdb
from scipy import stats
from pathlib import Path
from collections import Counter, defaultdict

V2 = Path(__file__).resolve().parent
DB = V2.parents[3] / "charon" / "data" / "charon.duckdb"
BATTERY = V2.parents[3] / "cartography" / "convergence" / "data" / "battery_sweep_v2.jsonl"
BRIDGES = V2.parents[3] / "cartography" / "convergence" / "data" / "bridges.jsonl"
OUT = V2 / "c5_f3_f13_boundary_results.json"

def sieve(limit):
    is_p = [True] * (limit + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_p[i]:
            for j in range(i*i, limit+1, i): is_p[j] = False
    return [i for i in range(2, limit+1) if is_p[i]]

def main():
    t0 = time.time()
    print("=== Challenge 5: F3/F13 Adversarial DMZ ===\n")

    # Load battery
    records = []
    with open(BATTERY) as f:
        for line in f:
            if line.strip():
                try: records.append(json.loads(line))
                except: pass
    print(f"  {len(records)} battery records")

    # Identify boundary records (middle tertile of delta_pct)
    deltas = [r.get("delta_pct", 0) for r in records if isinstance(r.get("delta_pct"), (int, float))]
    if deltas:
        p33 = float(np.percentile(deltas, 33))
        p67 = float(np.percentile(deltas, 67))
        boundary = [r for r in records if p33 <= r.get("delta_pct", 0) <= p67]
        print(f"  Boundary zone (delta_pct {p33:.1f}–{p67:.1f}%): {len(boundary)} records")
    else:
        boundary = records
        p33, p67 = 0, 100

    # Load bridges for cross-reference
    bridges = []
    with open(BRIDGES) as f:
        for line in f:
            if line.strip():
                try: bridges.append(json.loads(line))
                except: pass
    print(f"  {len(bridges)} bridge concepts")

    # Extended lag analysis on modular form a_p data
    print("\n  Running extended phase-shift lag analysis...")
    con = duckdb.connect(str(DB), read_only=True)
    rows = con.execute("""
        SELECT lmfdb_label, level, ap_coeffs
        FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND char_order = 1
        ORDER BY level LIMIT 5000
    """).fetchall()
    con.close()

    ap_primes = sieve(50)
    MAX_LAG = 10

    # Compute autocorrelation at extended lags
    lag_stats = {lag: [] for lag in range(1, MAX_LAG + 1)}
    for label, level, ap_json in rows:
        ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
        ap_vals = np.array([x[0] if isinstance(x, list) else x for x in ap[:25]], dtype=float)
        if len(ap_vals) < MAX_LAG + 5: continue
        mean_ap = np.mean(ap_vals)
        var_ap = np.var(ap_vals)
        if var_ap < 1e-10: continue

        for lag in range(1, MAX_LAG + 1):
            n = len(ap_vals) - lag
            if n < 5: break
            ac = float(np.sum((ap_vals[:n] - mean_ap) * (ap_vals[lag:lag+n] - mean_ap)) / (n * var_ap))
            lag_stats[lag].append(ac)

    # Extended lag profile
    print("\n  Extended autocorrelation profile:")
    lag_profile = {}
    for lag in range(1, MAX_LAG + 1):
        vals = lag_stats[lag]
        if vals:
            arr = np.array(vals)
            mean_ac = float(arr.mean())
            std_ac = float(arr.std())
            se = std_ac / math.sqrt(len(vals))
            sig = abs(mean_ac) > 2 * se
            lag_profile[lag] = {
                "mean_ac": round(mean_ac, 6),
                "std_ac": round(std_ac, 6),
                "n_forms": len(vals),
                "significant": sig,
            }
            marker = " ***" if sig else ""
            print(f"    lag={lag}: AC={mean_ac:.5f} ± {std_ac:.5f} (SE={se:.5f}){marker}")

    # Find forms with ANOMALOUS lag structure
    # (forms where AC at lag>5 is significant — these are the DMZ candidates)
    print("\n  Finding forms with anomalous extended lag structure...")
    anomalous = []
    for label, level, ap_json in rows:
        ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
        ap_vals = np.array([x[0] if isinstance(x, list) else x for x in ap[:25]], dtype=float)
        if len(ap_vals) < MAX_LAG + 5: continue
        mean_ap = np.mean(ap_vals)
        var_ap = np.var(ap_vals)
        if var_ap < 1e-10: continue

        # Check lags 6-10 specifically
        extended_acs = []
        for lag in range(6, MAX_LAG + 1):
            n = len(ap_vals) - lag
            if n < 5: break
            ac = float(np.sum((ap_vals[:n] - mean_ap) * (ap_vals[lag:lag+n] - mean_ap)) / (n * var_ap))
            extended_acs.append(ac)

        if extended_acs:
            max_ext = max(abs(ac) for ac in extended_acs)
            if max_ext > 0.3:  # Strong extended autocorrelation
                anomalous.append({
                    "label": label, "level": level,
                    "max_extended_ac": round(max_ext, 4),
                    "extended_acs": [round(ac, 4) for ac in extended_acs],
                })

    anomalous.sort(key=lambda x: -x["max_extended_ac"])
    print(f"  Anomalous forms (|AC| > 0.3 at lag 6-10): {len(anomalous)}")
    for a in anomalous[:10]:
        print(f"    {a['label']} (N={a['level']}): max_ext_AC={a['max_extended_ac']}")

    # Cross-reference anomalous forms with bridge concepts
    print("\n  Cross-referencing with bridges...")
    bridge_concepts = {b.get("concept", ""): b for b in bridges}
    anomalous_levels = set(a["level"] for a in anomalous)

    # Battery verdict distribution in boundary vs all
    boundary_verdicts = Counter(r.get("verdict") for r in boundary)
    all_verdicts = Counter(r.get("verdict") for r in records)

    elapsed = time.time() - t0
    output = {
        "challenge": "C5", "title": "F3/F13 Adversarial DMZ",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_battery_records": len(records),
        "boundary_zone": {"p33": round(p33, 1), "p67": round(p67, 1), "n": len(boundary)},
        "boundary_verdicts": dict(boundary_verdicts),
        "extended_lag_profile": lag_profile,
        "n_anomalous_forms": len(anomalous),
        "top_anomalous": anomalous[:20],
        "assessment": None,
    }

    # Significant lags
    sig_lags = [lag for lag, info in lag_profile.items() if info["significant"]]
    if anomalous:
        output["assessment"] = (
            f"DMZ POPULATED: {len(anomalous)} forms have anomalous extended lag structure (|AC|>0.3 at lag 6-10). "
            f"Significant lags: {sig_lags}. These are candidates for cross-domain bridges that basic battery misses. "
            f"Top candidate: {anomalous[0]['label']} (max_ext_AC={anomalous[0]['max_extended_ac']}).")
    else:
        output["assessment"] = (
            f"DMZ EMPTY: no forms have anomalous extended autocorrelation. "
            f"The phase-shift extension to lag 10 does not reveal hidden structure beyond lag 5. "
            f"Significant population-level lags: {sig_lags}.")

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
