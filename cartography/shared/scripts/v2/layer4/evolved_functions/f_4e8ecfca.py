def search_spearman_v1_215(values_a, values_b):
    """Spearman rank correlation between two value arrays."""
    import numpy as np
    from scipy import stats
    n = min(len(values_a), len(values_b))
    if n < 10:
        return {"statistic": 0.0, "p_value": 1.0, "description": "insufficient data"}
    rho, p = stats.spearmanr(values_a[:n], values_b[:n])
    return {"statistic": float(rho), "p_value": float(p), "description": f"Spearman ρ={rho:.4f}"}