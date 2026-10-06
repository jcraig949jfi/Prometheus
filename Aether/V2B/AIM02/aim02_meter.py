"""AIM02 richness instrument: non-AIM site-field trajectories only.

Input: a recording `seq` of shape (W+1, M): the byte value of M site-field
columns (fields opcode, arg1, payload ONLY -- never arg0, never energy) at
every tick of a late window of W ticks (row 0 = window start). Backend xp is
numpy or cupy; results are host Python numbers.

Per column (site-field), over the window:
  n_ch    number of change events (value differs from previous tick)
  U       distinct values held (including the value at window start)
  upc     (U - 1) / n_ch            distinct values entered per change
  tpc     distinct (prev, new) transitions / n_ch
  n16     share of change events whose new value was NOT held in the previous 16 ticks
  n64     same with a 64-tick memory
  dr1/dr2 discovery rate in the first / second half of the window:
          (# values first held in that half) / (# changes in that half)
  returns gaps between consecutive holdings of the same value (> 1 tick),
          pooled per activity bin (return-time distribution)

ACTIVITY CONDITIONING: columns with n_ch >= 2 are binned by n_ch into
log2 bins [2,4) [4,8) [8,16) [16,32) [32,64) [64,128) [128,256) [256,inf).
Every richness statistic is reported per bin, so a comparison can weight the
comparator's bin values by the treatment's bin mix (compare_conds), and
"more changes -> more unique states" cannot become the result.
"""

import numpy as np

BIN_EDGES = [2, 4, 8, 16, 32, 64, 128, 256, 1 << 30]
METRICS = ("upc", "tpc", "n16", "n64", "dr2", "dr_ratio")


def _host(x):
    return np.asarray(getattr(x, "get", lambda: x)())


def analyze(xp, seq):
    """seq: (W+1, M) uint8 array (xp). Returns per-bin stats dict (host)."""
    W1, M = seq.shape
    W = W1 - 1
    s = seq.astype(xp.int32)
    ch = s[1:] != s[:-1]                                   # (W, M)
    n_ch = ch.sum(axis=0)
    keep = n_ch >= 2
    idx = xp.nonzero(keep)[0]
    out = {"W": int(W), "M": int(M), "columns_changing": int(keep.sum()),
           "columns_ge1": int((n_ch >= 1).sum()), "bins": []}
    if idx.size == 0:
        return out
    s = s[:, idx]
    ch = ch[:, idx]
    n_ch = n_ch[idx]
    Mc = s.shape[1]
    # novelty at memory L: new value at t+1 not equal to any value held in [t+1-L, t]
    newv = s[1:]
    nov = {}
    for L in (16, 64):
        seen = xp.zeros((W, Mc), dtype=bool)
        for lag in range(1, L + 1):
            # value held at time (t+1-lag) for event row t (t = 0..W-1); clamp to window start
            src = xp.concatenate([xp.repeat(s[:1], max(0, lag - 1), axis=0), s[: W1 - lag]], axis=0)[:W] \
                if lag > 1 else s[:W]
            seen |= (newv == src)
        nov[L] = ((ch & ~seen).sum(axis=0) / xp.maximum(n_ch, 1)).astype(xp.float64)
    # distinct values and first-seen times via (value, time) keys
    T = xp.arange(W1, dtype=xp.int32)[:, None]
    key = xp.sort(s * 4096 + T, axis=0)                    # W1 <= 4096 required
    val = key // 4096
    tim = key % 4096
    newgrp = xp.concatenate([xp.ones((1, Mc), dtype=bool), val[1:] != val[:-1]], axis=0)
    U = newgrp.sum(axis=0)
    first_t = xp.where(newgrp, tim, -1)
    half = W // 2
    disc1 = ((first_t > 0) & (first_t <= half)).sum(axis=0)
    disc2 = (first_t > half).sum(axis=0)
    ch1 = ch[:half].sum(axis=0)
    ch2 = ch[half:].sum(axis=0)
    # return gaps: consecutive occurrences of the same value with a gap > 1
    gap = tim[1:] - tim[:-1]
    same = val[1:] == val[:-1]
    ret = same & (gap > 1)
    # transitions
    prev = s[:-1]
    tk = xp.where(ch, prev * 256 + newv, -1)
    tks = xp.sort(tk, axis=0)
    tnew = xp.concatenate([tks[:1] >= 0, (tks[1:] != tks[:-1]) & (tks[1:] >= 0)], axis=0)
    ntr = tnew.sum(axis=0)
    nc = n_ch.astype(xp.float64)
    per = {
        "n_ch": _host(n_ch),
        "upc": _host((U - 1) / nc),
        "tpc": _host(ntr / nc),
        "n16": _host(nov[16]),
        "n64": _host(nov[64]),
        "dr1": _host(xp.where(ch1 > 0, disc1 / xp.maximum(ch1, 1), xp.nan)),
        "dr2": _host(xp.where(ch2 > 0, disc2 / xp.maximum(ch2, 1), xp.nan)),
        "U": _host(U),
    }
    per["dr_ratio"] = np.where(per["dr1"] > 0, per["dr2"] / np.where(per["dr1"] > 0, per["dr1"], 1), np.nan)
    gaps_h = _host(gap)
    ret_h = _host(ret)
    col_bin = np.digitize(per["n_ch"], BIN_EDGES) - 1
    for b in range(len(BIN_EDGES) - 1):
        m = col_bin == b
        nb = int(m.sum())
        row = {"bin": b, "lo": BIN_EDGES[b], "hi": BIN_EDGES[b + 1], "columns": nb}
        if nb:
            for k in ("n_ch", "upc", "tpc", "n16", "n64", "dr1", "dr2", "dr_ratio", "U"):
                v = per[k][m]
                v = v[~np.isnan(v)] if v.dtype.kind == "f" else v
                row[k + "_mean"] = float(v.mean()) if v.size else None
                row[k + "_median"] = float(np.median(v)) if v.size else None
            g = gaps_h[:, m][ret_h[:, m]]
            row["returns"] = int(g.size)
            row["return_q"] = [float(np.quantile(g, q)) for q in (0.1, 0.5, 0.9)] if g.size else None
            row["return_mean"] = float(g.mean()) if g.size else None
        out["bins"].append(row)
    # global distributions (descriptive)
    out["hist_n_ch_log2"] = np.bincount(col_bin, minlength=len(BIN_EDGES) - 1).tolist()
    out["U_hist"] = np.bincount(np.minimum(per["U"], 64), minlength=65).tolist()
    return out


def compare_conds(treat_bins, comp_bins, min_cols=30):
    """Activity-matched comparison. For each metric, weight bins by the TREATMENT's column counts,
    over bins where both sides have >= min_cols columns. Returns {metric: (treat, comp, ratio, diff)},
    plus the return-time median (pooled-bin weighted) and the share of treatment columns covered."""
    tb = {r["bin"]: r for r in treat_bins}
    cb = {r["bin"]: r for r in comp_bins}
    usable = [b for b in tb if tb[b]["columns"] >= min_cols and b in cb and cb[b]["columns"] >= min_cols]
    tot = sum(tb[b]["columns"] for b in tb)
    res = {"bins_used": usable,
           "coverage": (sum(tb[b]["columns"] for b in usable) / tot) if tot else 0.0}
    for k in ("upc", "tpc", "n16", "n64", "dr2", "dr_ratio"):
        num_t = num_c = wsum = 0.0
        for b in usable:
            vt, vc = tb[b].get(k + "_mean"), cb[b].get(k + "_mean")
            if vt is None or vc is None:
                continue
            w = tb[b]["columns"]
            num_t += w * vt
            num_c += w * vc
            wsum += w
        if wsum:
            t, c = num_t / wsum, num_c / wsum
            res[k] = {"treat": t, "comp": c, "ratio": (t / c) if c else None, "diff": t - c}
    num_t = num_c = wsum = 0.0
    for b in usable:
        if tb[b].get("return_q") and cb[b].get("return_q"):
            w = tb[b]["columns"]
            num_t += w * tb[b]["return_q"][1]
            num_c += w * cb[b]["return_q"][1]
            wsum += w
    if wsum:
        t, c = num_t / wsum, num_c / wsum
        res["return_median"] = {"treat": t, "comp": c, "ratio": (t / c) if c else None, "diff": t - c}
    return res
