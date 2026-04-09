def search_spectral(values_a, values_b):
    import numpy as np
    from scipy import stats
    n = min(len(values_a), len(values_b), 256)
    if n < 32:
        return {"statistic": 0, "p_value": 1.0, "description": "insufficient data"}
    t = np.arange(n)
    a, b = np.array(values_a[:n]), np.array(values_b[:n])
    freqs = np.linspace(0.1, 0.5, 100)
    from scipy.signal import lombscargle
    pa = lombscargle(t, a - a.mean(), freqs, normalize=True)
    pb = lombscargle(t, b - b.mean(), freqs, normalize=True)
    corr = stats.pearsonr(pa, pb)[0]
    p_val = max(0.0, 1 - abs(corr))
    return {"statistic": corr, "p_value": p_val, "description": f"periodogram corr={corr:.4f}"}