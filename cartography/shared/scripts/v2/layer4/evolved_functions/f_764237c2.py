def search_ks(values_a, values_b):
    """Kolmogorov-Smirnov test: are distributions different?"""
    import numpy as np
    from scipy import stats
    a, b = np.array(values_a, dtype=float), np.array(values_b, dtype=float)
    if len(a) < 5 or len(b) < 5:
        return {"statistic": 0.0, "p_value": 1.0, "description": "insufficient data"}
    d, p = stats.ks_2samp(a, b)
    return {"statistic": float(d), "p_value": float(p), "description": f"KS D={d:.4f}"}