def search_fingerprint(values_a, values_b):
    import numpy as np
    from scipy import stats
    n = min(len(values_a), len(values_b), 500)
    if n < 20:
        return {"statistic": 0.0, "p_value": 1.0, "description": "insufficient data"}
    a, b = np.array(values_a[:n]), np.array(values_b[:n])
    da = np.diff(np.sort(a))
    db = np.diff(np.sort(b))
    stat, p = stats.ks_2samp(da, db)
    return {"statistic": float(stat), "p_value": float(p), "description": f"gap KS stat={stat:.4f}, p={p:.4f}"}