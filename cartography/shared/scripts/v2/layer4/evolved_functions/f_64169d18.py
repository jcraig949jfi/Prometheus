def search_qq(values_a, values_b):
    import numpy as np
    from scipy import stats
    a, b = np.array(values_a, dtype=float), np.array(values_b, dtype=float)
    if len(a) < 5 or len(b) < 5:
        return {"statistic": 0.0, "p_value": 1.0, "description": "insufficient data"}
    q = np.linspace(0.01, 0.99, 99)
    qa, qb = np.quantile(a, q), np.quantile(b, q)
    stat = np.mean(np.abs(qa - qb))
    p = 1.0
    return {"statistic": float(stat), "p_value": float(p), "description": f"QQ div={stat:.4f}"}