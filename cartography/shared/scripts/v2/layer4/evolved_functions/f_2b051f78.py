def search_spearman(values_a, values_b):
    import numpy as np
    from scipy import stats
    a, b = np.array(values_a, dtype=float), np.array(values_b, dtype=float)
    if len(a) < 5 or len(b) < 5:
        return {"statistic": 0.0, "p_value": 1.0, "description": "insufficient data"}
    rho, p = stats.spearmanr(a, b)
    return {"statistic": float(rho), "p_value": float(p), "description": f"Spearman rho={rho:.4f}"}