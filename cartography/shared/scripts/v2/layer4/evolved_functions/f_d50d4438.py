def search_power_spectrum(values_a, values_b):
    """Compare power spectrum similarity using FFT magnitudes."""
    import numpy as np
    from scipy import stats
    
    n = min(len(values_a), len(values_b))
    if n < 10:
        return {"statistic": 0.0, "p_value": 1.0, "description": "insufficient data"}
    
    # Compute FFT magnitudes (power spectrum)
    fft_a = np.abs(np.fft.rfft(values_a[:n]))
    fft_b = np.abs(np.fft.rfft(values_b[:n]))
    
    # Ensure same length for comparison
    min_len = min(len(fft_a), len(fft_b))
    fft_a = fft_a[:min_len]
    fft_b = fft_b[:min_len]
    
    # Use Pearson correlation on power spectra
    r, p = stats.pearsonr(fft_a, fft_b)
    
    return {"statistic": float(r), "p_value": float(p), "description": f"Power spectrum correlation r={r:.4f}"}