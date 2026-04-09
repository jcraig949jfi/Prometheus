def search_ratio_consecutive(values_a, values_b):
    import numpy as np
    from scipy import stats
    a, b = np.array(values_a, dtype=float), np.array(values_b, dtype=float)
    if len(a) < 3 or len(b) < 3:
        return {"statistic": 0.0, "p_value": 1.0, "description": "insufficient data"}
    ratios_a = a[1:] / a[:-1]
    ratios_b = b[1:] / b[:-1]
    stat, p = stats.ks_2samp(ratios_a, ratios_b)
    return {"statistic": float(stat), "p_value": float(p), "description": f"KS stat={stat:.4f}"}