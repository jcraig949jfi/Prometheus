def search_tail_overlap_v1(values_a, values_b):
    import numpy as np
    from scipy import stats
    a, b = np.array(values_a), np.array(values_b)
    q_high = np.percentile(np.concatenate([a, b]), 90)
    tail_a = a[a >= q_high]
    tail_b = b[b >= q_high]
    if len(tail_a) < 5 or len(tail_b) < 5:
        return {"statistic": 0.0, "p_value": 1.0, "description": "insufficient tail data"}
    d, p = stats.ks_2samp(tail_a, tail_b)
    return {"statistic": float(d), "p_value": float(p), "description": f"Tail KS D={d:.4f}"}