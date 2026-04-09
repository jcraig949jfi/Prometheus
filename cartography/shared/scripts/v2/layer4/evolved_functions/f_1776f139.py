def search_gap_ratio_v1_840(values_a, values_b):
    """Compare consecutive-difference distributions."""
    import numpy as np
    from scipy import stats
    def gaps(v):
        s = np.sort(np.array(v, dtype=float))
        d = np.diff(s)
        if len(d) == 0:
            return np.array([])
        mean_d = np.mean(d)
        if mean_d > 0:
            return d / mean_d
        return d
    ga, gb = gaps(values_a), gaps(values_b)
    if len(ga) < 5 or len(gb) < 5:
        return {"statistic": 0.0, "p_value": 1.0, "description": "insufficient data"}
    d, p = stats.ks_2samp(ga, gb)
    return {"statistic": float(d), "p_value": float(p), "description": f"Gap-ratio KS D={d:.4f}"}