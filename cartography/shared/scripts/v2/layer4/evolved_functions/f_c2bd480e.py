def search_power_spectrum(values_a, values_b):
    import numpy as np
    from scipy import stats
    n = min(len(values_a), len(values_b))
    if n < 10:
        return {"statistic": 0.0, "p_value": 1.0, "description": "insufficient data"}
    fft_a = np.abs(np.fft.rfft(values_a[:n]))
    fft_b = np.abs(np.fft.rfft(values_b[:n]))
    m = min(len(fft_a), len(fft_b))
    r, p = stats.pearsonr(fft_a[:m], fft_b[:m])
    return {"statistic": float(r), "p_value": float(p), "description": f"Power spectrum r={r:.4f}"}