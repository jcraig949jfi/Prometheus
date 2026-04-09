def search_pearson_v6_40(values_a, values_b):
    """Pearson correlation between two value arrays."""
    import numpy as np
    from scipy import stats
    n = min(len(values_a), len(values_b))
    if n < 10:
        return {"statistic": 0.0, "p_value": 1.0, "description": "insufficient data"}
    r, p = stats.pearsonr(values_a[:n], values_b[:n])
    return {"statistic": float(r), "p_value": float(p), "description": f"Pearson r={r:.4f}"}