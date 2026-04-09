def search_spearman(values_a, values_b):
    """Spearman rank correlation between two value arrays."""
    import numpy as np
    from scipy import stats
    n = min(len(values_a), len(values_b))
    if n < 10:
        return {"statistic": 0.0, "p_value": 1.0, "description": "insufficient data"}
    r, p = stats.spearmanr(values_a[:n], values_b[:n])
    return {"statistic": float(r), "p_value": float(p), "description": f"Spearman r={r:.4f}"}