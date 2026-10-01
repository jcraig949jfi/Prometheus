"""A6: host Monte Carlo of W-V's pivot contrast D_piv under stylized readouts.
Rectified count threshold: readout + iff sum of arrivals from +-signed sensors >= k.
Signed lossy majority: readout = sign(sum_j v_j n_j). Arrival counts n_j ~ Poisson(lam)
shared by mirror partners (common physics draws). Follow/eligibility/pivot exactly as
W-V ana.follow_table/stratum (world-A votes; pivotal = 3 agreeing votes and j agrees)."""
import json, numpy as np
rng = np.random.default_rng(0xA6)
def sim(kind, k=1, lam=1.0, n=200000, p=0.3, ties="zero"):
    y = np.where(rng.random(n) < .5, 1, -1)
    v = y[:, None] * np.where(rng.random((n, 5)) < p, -1, 1)          # world A signs
    cnt = rng.poisson(lam, (n, 5))
    def readout(sig):     # sig: [n,5] signs as seen by the emitting sensors
        if kind == "rect":
            tot = (cnt * (sig > 0)).sum(1); return np.where(tot >= k, 1, -1)
        tot = (cnt * sig).sum(1); return np.sign(tot)
    def readout_mix(sig, j, sig_other):
        s = sig.copy(); s[:, j] = sig_other[:, j]; return readout(s)
    A, B = readout(v), readout(-v)
    elig = (A == y) & (B == -y)
    fs, piv = [], []
    agree = v == y[:, None]; nag = agree.sum(1)
    for j in range(5):
        Aj = readout_mix(v, j, -v); Bj = readout_mix(-v, j, v)
        f = (((Aj == B) & (Aj != 0)).astype(float) + ((Bj == A) & (Bj != 0))) / 2
        fs.append(f); piv.append((nag == 3) & agree[:, j])
    fs = np.stack(fs, 1); piv = np.stack(piv, 1); e = elig[:, None]
    fp = fs[e & piv].mean(); fn = fs[e & ~piv].mean()
    acc = ((A == y).astype(float) * .5 + (B == -y) * .5).mean()
    return {"acc": round(float(acc), 3), "single_mean": round(float(fs[elig].mean()), 3),
            "f_piv": round(float(fp), 3), "f_non": round(float(fn), 3), "D_piv": round(float(fp - fn), 3)}
out = {}
for lam in (0.5, 1.0, 2.0, 4.0):
    for k in (1, 2, 3, 4):
        out[f"rect lam{lam} k{k}"] = sim("rect", k, lam)
    out[f"signed-majority lam{lam}"] = sim("signed", lam=lam)
for kk, vv in out.items(): print(kk, vv)
json.dump(out, open("out/a6_piv_model.json", "w"), indent=1)
