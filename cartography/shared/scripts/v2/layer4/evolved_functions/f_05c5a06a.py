def search_mutual_info(values_a, values_b):
    """Binned mutual information between two arrays."""
    import numpy as np
    n = min(len(values_a), len(values_b))
    if n < 20:
        return {"statistic": 0.0, "p_value": 1.0, "description": "insufficient data"}
    a, b = np.array(values_a[:n], dtype=float), np.array(values_b[:n], dtype=float)
    n_bins = max(5, int(np.sqrt(n)))
    hist_ab, _, _ = np.histogram2d(a, b, bins=n_bins)
    pxy = hist_ab / hist_ab.sum()
    px = pxy.sum(axis=1)
    py = pxy.sum(axis=0)
    mi = 0.0
    for i in range(n_bins):
        for j in range(n_bins):
            if pxy[i, j] > 0 and px[i] > 0 and py[j] > 0:
                mi += pxy[i, j] * np.log(pxy[i, j] / (px[i] * py[j]))
    # Null: random pairing MI
    rng = np.random.RandomState(42)
    null_mis = []
    for _ in range(200):
        b_shuf = rng.permutation(b)
        h, _, _ = np.histogram2d(a, b_shuf, bins=n_bins)
        p_s = h / h.sum()
        px_s = p_s.sum(axis=1)
        py_s = p_s.sum(axis=0)
        mi_s = 0.0
        for ii in range(n_bins):
            for jj in range(n_bins):
                if p_s[ii, jj] > 0 and px_s[ii] > 0 and py_s[jj] > 0:
                    mi_s += p_s[ii, jj] * np.log(p_s[ii, jj] / (px_s[ii] * py_s[jj]))
        null_mis.append(mi_s)
    null_mean = np.mean(null_mis)
    null_std = np.std(null_mis) + 1e-12
    z = (mi - null_mean) / null_std
    from scipy import stats
    p_value = float(2 * (1 - stats.norm.cdf(abs(z))))
    return {"statistic": float(mi), "p_value": p_value, "description": f"MI={mi:.4f}, z={z:.2f}"}