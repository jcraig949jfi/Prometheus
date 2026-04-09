def search_ratio_consecutive(values_a, values_b):
    import numpy as np
    from scipy import stats
    n = min(len(values_a), len(values_b))
    if n < 10: return {"statistic": 0.0, "p_value": 1.0, "description": "insufficient data"}
    ratios = np.array(values_a[1:n]) / np.array(values_a[:n-1])
    if np.any(ratios <= 0): return {"statistic": 0.0, "p_value": 1.0, "description": "non-positive values"}
    log_ratios = np.log(ratios)
    stat, p = stats.shapiro(log_ratios)
    return {"statistic": float(stat), "p_value": float(p), "description": f"Shapiro-Wilk normality test on log ratios"}