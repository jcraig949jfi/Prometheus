def search_spearman(values_a, values_b):
    import numpy as np
    from scipy import stats
    if len(values_a) < 3 or len(values_b) < 3:
        return {"statistic": 0.0, "p_value": 1.0, "description": "insufficient data"}
    rho, p = stats.spearmanr(values_a, values_b)
    return {"statistic": float(rho), "p_value": float(p), "description": f"Spearman rho={rho:.4f}"}