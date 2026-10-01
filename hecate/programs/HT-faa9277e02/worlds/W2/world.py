"""HT-faa9277e02 / W2 world. See IMPLEMENTATION_NOTES.md. Writes rows.jsonl."""
import json, os, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "rows.jsonl")

NCELL, LAM, SIGMA, K = 100, 20.0, 0.3, 8
N_TRAIN, N_TEST = 20000, 50000
TS = [1, 2, 4, 8, 16, 32]
SEEDS = list(range(10))
S_COMP = 0.3            # winner-take-most competition width (= spec noise sigma)
ETA0, ETA1 = 0.05, 0.001
ROOT = 20260929

PARAMS = dict(ncell=NCELL, lam=LAM, sigma=SIGMA, K=K, n_train=N_TRAIN, n_test=N_TEST,
              Ts=TS, s_comp=S_COMP, eta0=ETA0, eta1=ETA1, root_seed=ROOT,
              noise="lognormal c*exp(sigma*xi)", input="(log c1_bar, log c2_bar)")


def rng(seed, T, stream):
    return np.random.default_rng(np.random.SeedSequence([ROOT, seed, T, stream]))


def clean(x):
    x = np.asarray(x, float)
    return np.stack([-x / LAM, -(NCELL - x) / LAM], axis=-1)  # log c1, log c2


def sample(r, n, T):
    x = r.integers(0, NCELL, n)
    lc = clean(x)                                   # (n,2)
    noisy = np.exp(lc[:, None, :] + SIGMA * r.standard_normal((n, T, 2)))
    u = np.log(noisy.mean(axis=1))
    return x, u


def mi_bits(x, r, nx=NCELL, nr=K):
    N = len(x)
    J = np.zeros((nx, nr)); np.add.at(J, (x, r), 1)
    def H(c):
        c = c[c > 0]; p = c / N
        hp = -(p * np.log2(p)).sum()
        return hp, hp + (len(c) - 1) / (2 * N * np.log(2))
    hx, hxm = H(J.sum(1)); hr, hrm = H(J.sum(0)); hj, hjm = H(J.ravel())
    return dict(mm=hxm + hrm - hjm, plugin=hx + hr - hj,
                occupied_r=int((J.sum(0) > 0).sum()), occupied_joint=int((J > 0).sum()))


def nearest(u, W):
    return np.argmin(((u[:, None, :] - W[None]) ** 2).sum(-1), axis=1)


def train_hebb(u, r):
    W = u[r.choice(len(u), K, replace=False)].copy()
    n = len(u)
    etas = ETA0 * (ETA1 / ETA0) ** (np.arange(n) / (n - 1))
    for t in range(n):
        d2 = ((u[t] - W) ** 2).sum(1)
        a = -d2 / (2 * S_COMP ** 2); a -= a.max()
        y = np.exp(a); y /= y.sum()
        W += etas[t] * y[:, None] * (u[t][None] - y[:, None] * W)
    return W


def control_readout(u):
    z = u[:, 1] - u[:, 0]
    lo = clean(0)[1] - clean(0)[0]; hi = clean(NCELL - 1)[1] - clean(NCELL - 1)[0]
    b = np.floor((z - lo) / (hi - lo) * K).astype(int)
    return np.clip(b, 0, K - 1), float(lo), float(hi)


def pc_readout(u, T):
    s2 = np.log(1 + (np.exp(SIGMA ** 2) - 1) / T)
    lc = clean(np.arange(NCELL))                    # clean log means
    mu = lc + SIGMA ** 2 / 2 - s2 / 2               # FW: preserve mean
    ll = -((u[:, None, :] - mu[None]) ** 2).sum(-1) / (2 * s2)   # (n,100)
    ll -= ll.max(1, keepdims=True)
    post = np.exp(ll); post /= post.sum(1, keepdims=True)
    cls = (np.arange(NCELL) * K) // NCELL
    mass = np.zeros((len(u), K))
    for k in range(K):
        mass[:, k] = post[:, cls == k].sum(1)
    return mass.argmax(1)


def slope(bits_by_T):
    xs = np.log2([1, 2, 4, 8]); ys = [bits_by_T[str(t)] for t in [1, 2, 4, 8]]
    return float(np.polyfit(xs, ys, 1)[0])


def main():
    t0c, t0w = time.process_time(), time.time()
    if os.path.exists(ROWS):
        os.remove(ROWS)
    f = open(ROWS, "a", encoding="utf-8")
    for seed in SEEDS:
        res = {a: {"bits": {}, "plugin": {}, "occupied_r": {}, "extra": {}} for a in
               ["TREATMENT", "CONTROL", "NULL_TWIN", "POSITIVE_CONTROL"]}
        for T in TS:
            _, utr = sample(rng(seed, T, 0), N_TRAIN, T)
            xte, ute = sample(rng(seed, T, 1), N_TEST, T)
            W = train_hebb(utr, rng(seed, T, 2))
            rh = nearest(ute, W)
            rc, lo, hi = control_readout(ute)
            xc = rng(seed, T, 3).uniform(0, NCELL - 1, K)
            Wn = clean(xc)
            rn = nearest(ute, Wn)
            rp = pc_readout(ute, T)
            for arm, r, ex in [("TREATMENT", rh, {"W": W.round(4).tolist()}),
                               ("CONTROL", rc, {"z_lo": lo, "z_hi": hi}),
                               ("NULL_TWIN", rn, {"centres_x": np.sort(xc).round(3).tolist()}),
                               ("POSITIVE_CONTROL", rp, {"noise_model": "exact T=1; Fenton-Wilkinson T>1"})]:
                m = mi_bits(xte, r)
                res[arm]["bits"][str(T)] = m["mm"]
                res[arm]["plugin"][str(T)] = m["plugin"]
                res[arm]["occupied_r"][str(T)] = m["occupied_r"]
                res[arm]["extra"][str(T)] = ex
        for arm, d in res.items():
            row = dict(arm=arm, seed=seed, params=PARAMS, bits_mm=d["bits"], bits_plugin=d["plugin"],
                       occupied_r=d["occupied_r"], slope_T_le_8=slope(d["bits"]), extra=d["extra"])
            f.write(json.dumps(row) + "\n"); f.flush()
        pc1 = res["POSITIVE_CONTROL"]["bits"]["1"]
        nt1 = res["NULL_TWIN"]["bits"]["1"]
        base = max(0.9 * pc1, nt1 + 0.6)
        cb = {str(T): base + 0.5 * np.log2(T) for T in TS}
        row = dict(arm="CHEAT", seed=seed, params=PARAMS, bits_mm=cb, bits_plugin=cb,
                   occupied_r=None, slope_T_le_8=slope(cb),
                   extra={"injection": "repair1: bits(T)=max(0.9*PC(T=1), NULL_TWIN(T=1)+0.6)+0.5*log2(T), written directly"})
        f.write(json.dumps(row) + "\n"); f.flush()
        print("seed", seed, "done", round(time.process_time() - t0c, 1), flush=True)
    f.close()
    meta = dict(cpu_seconds=time.process_time() - t0c, wall_seconds=time.time() - t0w)
    with open(os.path.join(HERE, "run_meta.json"), "w") as g:
        json.dump(meta, g)
    print(meta)


if __name__ == "__main__":
    main()
