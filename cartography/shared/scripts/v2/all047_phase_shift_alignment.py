"""
ALL-047: Phase-Shift & Oscillation Alignment
==============================================
For the a_p sequences of modular forms, compute the autocorrelation
function as a function of lag in the prime index. Does the autocorrelation
show periodic structure? At what lags do forms become phase-aligned?

Also: cross-correlation between pairs of forms at the same level.
Is there a characteristic oscillation frequency?
"""
import json, time
import numpy as np
import duckdb
from scipy import stats
from pathlib import Path
from collections import defaultdict

V2 = Path(__file__).resolve().parent
DB = V2.parents[3] / "charon" / "data" / "charon.duckdb"
OUT = V2 / "all047_phase_shift_results.json"

def sieve(limit):
    is_p = [True] * (limit + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_p[i]:
            for j in range(i*i, limit+1, i): is_p[j] = False
    return [i for i in range(2, limit+1) if is_p[i]]

def autocorrelation(x, max_lag=15):
    n = len(x)
    x = x - np.mean(x)
    var = np.var(x)
    if var < 1e-12: return np.zeros(max_lag)
    ac = np.correlate(x, x, mode='full')
    ac = ac[n-1:n-1+max_lag] / (var * n)
    return ac

def main():
    t0 = time.time()
    print("=== ALL-047: Phase-Shift & Oscillation Alignment ===\n")

    con = duckdb.connect(str(DB), read_only=True)
    rows = con.execute("""
        SELECT lmfdb_label, level, ap_coeffs FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND char_order = 1
        ORDER BY level LIMIT 5000
    """).fetchall()
    con.close()
    print(f"  {len(rows)} forms loaded")

    ap_primes = sieve(50)
    MAX_LAG = 15

    # 1. Per-form autocorrelation
    print("\n[1] Computing per-form autocorrelation...")
    all_acs = []
    for label, level, ap_json in rows:
        ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
        ap_vals = np.array([x[0] if isinstance(x, list) else x for x in ap[:25]], dtype=float)
        if len(ap_vals) < MAX_LAG + 3: continue
        ac = autocorrelation(ap_vals, MAX_LAG)
        all_acs.append(ac)

    all_acs = np.array(all_acs)
    mean_ac = all_acs.mean(axis=0)
    std_ac = all_acs.std(axis=0)

    print(f"  Mean autocorrelation by lag:")
    for lag in range(MAX_LAG):
        sig = "***" if abs(mean_ac[lag]) > 2 * std_ac[lag] / np.sqrt(len(all_acs)) else ""
        print(f"    lag={lag}: AC={mean_ac[lag]:.4f} ± {std_ac[lag]:.4f} {sig}")

    # Peak lag (excluding lag=0)
    peak_lag = int(np.argmax(np.abs(mean_ac[1:]))) + 1
    peak_ac = float(mean_ac[peak_lag])

    # 2. Cross-correlation at same level
    print("\n[2] Cross-correlation between same-level pairs...")
    by_level = defaultdict(list)
    for label, level, ap_json in rows:
        ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
        ap_vals = [x[0] if isinstance(x, list) else x for x in ap[:25]]
        if len(ap_vals) >= 15:
            by_level[level].append({"label": label, "ap": np.array(ap_vals, dtype=float)})

    cross_corrs = []
    for level, group in by_level.items():
        if len(group) < 2: continue
        for i in range(len(group)):
            for j in range(i+1, len(group)):
                n = min(len(group[i]["ap"]), len(group[j]["ap"]))
                x = group[i]["ap"][:n] - np.mean(group[i]["ap"][:n])
                y = group[j]["ap"][:n] - np.mean(group[j]["ap"][:n])
                sx, sy = np.std(x), np.std(y)
                if sx > 0 and sy > 0:
                    cc = float(np.correlate(x, y)[0] / (n * sx * sy))
                    cross_corrs.append(cc)

    if cross_corrs:
        cc_arr = np.array(cross_corrs)
        print(f"  {len(cross_corrs)} same-level pairs")
        print(f"  Mean cross-correlation: {cc_arr.mean():.4f}")
        print(f"  Std: {cc_arr.std():.4f}")
        print(f"  Fraction |cc| > 0.5: {np.mean(np.abs(cc_arr) > 0.5):.4f}")
        # Compare to null
        null_cc = np.random.randn(len(cross_corrs)) / np.sqrt(15)
        stat, p_val = stats.ks_2samp(cc_arr, null_cc)
        print(f"  KS test vs null: D={stat:.4f}, p={p_val:.4e}")
    else:
        cc_arr = np.array([0])
        p_val = 1.0

    # 3. Spectral analysis: FFT of mean a_p sequence
    print("\n[3] Spectral analysis of mean a_p...")
    all_ap = np.array([[x[0] if isinstance(x, list) else x for x in
                       (json.loads(r[2]) if isinstance(r[2], str) else r[2])[:20]]
                      for r in rows if len(json.loads(r[2]) if isinstance(r[2], str) else r[2]) >= 20],
                     dtype=float)
    mean_ap = all_ap.mean(axis=0)
    fft = np.fft.rfft(mean_ap - mean_ap.mean())
    power = np.abs(fft)**2
    freqs = np.fft.rfftfreq(len(mean_ap))
    dominant_freq = float(freqs[np.argmax(power[1:]) + 1]) if len(power) > 1 else 0

    print(f"  Dominant frequency: {dominant_freq:.4f}")
    print(f"  Power spectrum: {[round(float(p), 1) for p in power[:8]]}")

    elapsed = time.time() - t0
    output = {
        "challenge": "ALL-047", "title": "Phase-Shift & Oscillation Alignment",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_forms": len(rows),
        "autocorrelation": {
            "mean_by_lag": [round(float(v), 6) for v in mean_ac],
            "std_by_lag": [round(float(v), 6) for v in std_ac],
            "peak_lag": peak_lag,
            "peak_value": round(peak_ac, 6),
        },
        "cross_correlation": {
            "n_pairs": len(cross_corrs),
            "mean": round(float(cc_arr.mean()), 6),
            "std": round(float(cc_arr.std()), 6),
            "frac_above_05": round(float(np.mean(np.abs(cc_arr) > 0.5)), 4),
            "ks_pvalue": float(p_val),
        },
        "spectral": {
            "dominant_frequency": round(dominant_freq, 6),
            "power_spectrum": [round(float(p), 2) for p in power[:10]],
        },
        "assessment": None,
    }

    if peak_ac > 0.1:
        output["assessment"] = f"OSCILLATION DETECTED: peak AC={peak_ac:.3f} at lag={peak_lag}. Forms show characteristic periodicity in prime index space"
    elif abs(peak_ac) > 0.05:
        output["assessment"] = f"WEAK OSCILLATION: peak AC={peak_ac:.4f} at lag={peak_lag}. Marginal periodicity"
    else:
        output["assessment"] = f"NO OSCILLATION: all AC < 0.05. a_p sequences are effectively white noise in prime index"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
