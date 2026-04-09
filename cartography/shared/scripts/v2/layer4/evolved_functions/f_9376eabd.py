def search_qq(values_a, values_b):
    import numpy as np
    from scipy import stats
    a, b = np.array(values_a, dtype=float), np.array(values_b, dtype=float)
    if len(a) < 5 or len(b) < 5:
        return {"statistic": 0.0, "p_value": 1.0, "description": "insufficient data"}
    quantiles = np.linspace(0.01, 0.99, 99)
    q_a, q_b = np.quantile(a, quantiles), np.quantile(b, quantiles)
    stat = np.mean(np.abs(q_a - q_b))
    p = 1.0
    return {"statistic": float(stat), "p_value": float(p), "description": f"QQ div={stat:.4f}"}