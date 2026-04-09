def search_wavelet(values_a, values_b):
    import numpy as np
    from scipy import stats
    n = min(len(values_a), len(values_b), 512)
    if n < 32:
        return {"statistic": 0, "p_value": 1.0, "description": "insufficient data"}
    a, b = np.array(values_a[:n]), np.array(values_b[:n])
    coeffs_a = np.convolve(a, [1, -1], mode='valid')
    coeffs_b = np.convolve(b, [1, -1], mode='valid')
    stat, p_val = stats.ks_2samp(coeffs_a, coeffs_b)
    return {"statistic": stat, "p_value": p_val, "description": f"KS={stat:.4f}"}