"""Joint-carrier probes on 4781b0a1 (PLAN.md, committed first). CPU, 2 threads."""
import json
import pathlib
import sys

import numpy as np
import torch

REPO = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
from prometheus.ananke import assays, c1b, c1b_run, envs, lens  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402

torch.set_num_threads(2)
DEV = "cpu"
OUT = pathlib.Path(__file__).parent
SEEDS = assays.world_seeds(0x5E7, 64)
r = [x for x in c1b_run.d_wave_cells() if x["extra"]["source_cell"].startswith("4781b0a1")][0]
PH, ENV = Physics.from_dict(r["physics"]), envs.EnvSpec(**r["env"])
G = np.asarray(r["extra"]["genome"], dtype=np.int64)
TK = c1b.ticks(ENV)
TRIALS = range(ENV.trials)


def at(off):
    return [t0 + off for t0 in TK["t0"]] if off >= 0 else [t0 + off for t0 in TK["t0"] if t0 + off >= 0]


def sw(names, sub=None):
    return lambda w: lens.swap(w, names, sub=sub)


def erase(parts):
    def f(w):
        for p in parts:
            if p == "S":
                w.S.zero_()
            elif p == "Kp":
                w.Kp.zero_()
            elif p == "inbox":
                w.Acc_sum.zero_(); w.Acc_cnt.zero_()
            elif p == "w":
                w.w.fill_(16)
            elif p == "flush":
                w.Msum.zero_(); w.Mcnt.zero_()
    return f


def run(fn, ticks):
    tr = lens.run(PH, G, ENV, SEEDS, hooks={t: fn for t in ticks}, device=DEV)
    return lens.trial_acc(tr, TRIALS)


if __name__ == "__main__":
    base = lens.run(PH, G, ENV, SEEDS, device=DEV)
    nrm = lens.trial_acc(base, TRIALS)
    res = {"normal": lens.ci(nrm)}
    swaps = {"S": sw(["S"]), "Kp": sw(["Kp"]), "inbox": sw(["Acc_sum", "Acc_cnt"]), "w": sw(["w"]),
             "pay0": sw(["Msum"], 0), "pay1": sw(["Msum"], 1), "counts": sw(["Mcnt"]),
             "channel": sw(lens.FLIGHT_ARRAYS), "site": sw(lens.SITE_ARRAYS),
             "joint": lambda w: (lens.swap(w, lens.FLIGHT_ARRAYS), lens.swap(w, lens.SITE_ARRAYS))}
    erases = {"S": erase(["S"]), "Kp": erase(["Kp"]), "inbox": erase(["inbox"]), "w": erase(["w"]),
              "flush": erase(["flush"]), "S+flush": erase(["S", "flush"]), "Kp+flush": erase(["Kp", "flush"]),
              "allsite": erase(["S", "Kp", "inbox", "w"]), "allsite+flush": erase(["S", "Kp", "inbox", "w", "flush"])}
    for off in (1, 8, 15):
        for n, f in swaps.items():
            p = run(f, at(off))
            res[f"swap t0+{off} {n}"] = (lens.ci(p), lens.swap_verdict(nrm, p))
        for n, f in erases.items():
            p = run(f, at(off))
            m, lo, hi = lens.ci(p - nrm)
            res[f"erase t0+{off} {n}"] = (lens.ci(p), {"diff": m, "diff_lo99": lo, "diff_hi99": hi})
        print("done", off, flush=True)
    p = run(swaps["joint"], at(-1))
    res["J4 joint swap t0-1"] = (lens.ci(p), lens.swap_verdict(nrm, p))
    # J3 decoders at t0+8
    feats = []

    def rec(w, t):
        if t in at(8):
            a = w.read_idx[:, 0]
            bi = torch.arange(w.B)
            feats.append({
                "S0_a": w.S[bi, a, 0].numpy().astype(float), "S1_a": w.S[bi, a, 1].numpy().astype(float),
                "Kp_a": w.Kp[bi, a].sum(-1).numpy().astype(float),
                "pay0": w.Msum[..., 0].sum((0, 2, 3)).numpy().astype(float),
                "pay1": w.Msum[..., 1].sum((0, 2, 3)).numpy().astype(float),
                "pay1_a": w.Msum[..., 1][:, bi, a, :].sum((0, 2)).numpy().astype(float),
                "S0_all": w.S[..., 0].sum(-1).numpy().astype(float),
            })
    tr = lens.run(PH, G, ENV, SEEDS, recorders={"f": rec}, device=DEV)
    y = tr.ep.y
    B, K = y.shape
    half = (B // 2) // 2 * 2

    def score(X):
        s = np.sign(X - np.median(X[:half]))
        pol = 1 if (s[:half] * y[:half]).mean() >= 0 else -1
        c = np.where(s == 0, 0.5, (pol * s == y).astype(float))[half:]
        return lens.ci(c.mean(1).reshape(-1, 2).mean(-1))
    X = {k: np.stack([f[k] for f in feats], 1) for k in feats[0]}
    dec = {k: score(v) for k, v in X.items()}
    site_keys = ["S0_a", "S1_a", "Kp_a", "S0_all"]
    chan_keys = ["pay0", "pay1", "pay1_a"]
    bs = max(site_keys, key=lambda k: dec[k][0])
    bc = max(chan_keys, key=lambda k: dec[k][0])
    zs = lambda v: (v - v[:half].mean()) / (v[:half].std() + 1e-9)  # noqa: E731
    A, Bc = zs(X[bs]), zs(X[bc])
    best = None
    for th in np.linspace(0, np.pi, 37):
        comb = np.cos(th) * A + np.sin(th) * Bc
        s = np.sign(comb[:half])
        v = (s * y[:half]).mean()
        if best is None or abs(v) > abs(best[1]):
            best = (th, v)
    comb = np.cos(best[0]) * A + np.sin(best[0]) * Bc
    dec[f"joint_linear({bs},{bc})"] = score(comb)
    res["J3 decoders t0+8"] = dec
    (OUT / "out_j_probe.json").write_text(json.dumps(res, indent=1, default=float))
    for k, v in res.items():
        print(k, json.dumps(v, default=lambda x: round(float(x), 3))[:160])
