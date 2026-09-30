"""R-MECH (Bellerophon) executable attack harness for Cosmos C4 DESIGN v0.2 -- PHASE 1 (public material only; no D2).

Everything here is built from the DESIGN TEXT (roles/Cosmos/c4/DESIGN_C4.md s3-s10, S0_TRIVIAL_RULES.md s3) plus the
PUBLIC C3 certificate (prometheus/cosmos/c3/*), which is used UNCHANGED as Certificate A.

Contents
  Reservoir      a continuous planted family (leak a, noise sigma, input gain g, width d): x' = a x + g W_in e(o) + sigma n
  sysid_rel      the S1 "channel reliability" coordinate as the design text specifies it: probe symbols injected through
                 the input channel at t = 0, i.i.d. drive afterwards, a FIXED-CLASS linear decoder (ridge, frozen
                 hyper-parameters) trained on independent episodes, held-out accuracy recorded on the fixed grid H = 1..16.
                 It imports numpy and the System interface only (G1), uses its own RNG namespace (G2), is one vector per
                 WORLD, identical across k (G3), has frozen settings (G4), and uses a whitened, affine-invariant decoder
                 (G5).
  t3_down        T3-DOWN written from S0_TRIVIAL_RULES s3 (exact-zero paired distances at q = k+1).
  b_use          Certificate B-USE written from DESIGN s6 (source-randomized cue, identical query, readout trained on
                 B's own episodes, exact binomial test of held-out V-way accuracy vs 1/V).
    python attack_harness.py <out.jsonl> <part> <parts>
"""
import json, math, sys, time

import numpy as np

from prometheus.cosmos.c3.system import System, rollout, train_readout
from prometheus.cosmos.c3.task import Task, batch, paired_batch, onehot
from prometheus.cosmos.c3.certify import certify

H = tuple(range(1, 17))          # the design's fixed horizon grid


class Reservoir(System):
    def __init__(self, task: Task, a: float, sigma: float, g: float = 1.0, d: int = 8, wseed: int = 0):
        self.t, self.a, self.s, self.g, self.d = task, a, sigma, g, d
        r = np.random.default_rng(wseed)
        self.W = r.standard_normal((task.n_symbols, d)) / math.sqrt(d)
        self.name = "RES(a=%.2f,s=%.2f)" % (a, sigma)

    def init(self, E):
        return {"x": np.zeros((E, self.d)), "cur": np.zeros(E, dtype=np.int64)}

    def noise(self, n, rng):
        return {"n": rng.standard_normal((n, self.d))}

    def step(self, st, o, nz):
        x = self.a * st["x"] + self.g * self.W[o] + self.s * nz["n"]
        return {"x": x, "cur": o.copy()}

    def readout_features(self, st):
        return np.hstack([st["x"], onehot(st["cur"], self.t.n_symbols)])

    def full_state(self, st):
        return np.hstack([st["x"], onehot(st["cur"], self.t.n_symbols)])


# ---------------------------------------------------------------- S1 SYSID reliability coordinate (numpy + System only)
def _ridge_fit_predict(Xtr, ytr, Xte, K, lam=1e-2):
    mu, sd = Xtr.mean(0), Xtr.std(0); sd[sd < 1e-12] = 1.0
    Z, Zt = (Xtr - mu) / sd, (Xte - mu) / sd
    Z = np.hstack([Z, np.ones((len(Z), 1))]); Zt = np.hstack([Zt, np.ones((len(Zt), 1))])
    Y = np.eye(K)[ytr]
    Wt = np.linalg.solve(Z.T @ Z + lam * np.eye(Z.shape[1]), Z.T @ Y)
    return (Zt @ Wt).argmax(1)


def sysid_rel(sys_: System, V: int, n_in: int, E: int = 1500, seed: int = 777):
    """REL[h] = held-out accuracy of recovering a probe symbol p (drawn from 0..V-1, injected at t = 0) from the readout
    view after h further steps of i.i.d. drive (uniform over the non-probe input symbols V..n_in-1). World property: no k."""
    rng = np.random.default_rng(("SYSID", seed).__hash__() & 0xFFFFFFFF)
    rel = {}
    Tm = max(H) + 1
    for part in ("train", "test"):
        p = rng.integers(0, V, E)
        obs = np.empty((E, Tm), dtype=np.int64); obs[:, 0] = p
        obs[:, 1:] = rng.integers(V, n_in, (E, Tm - 1))
        st = sys_.init(E); feats = {}
        for t in range(Tm):
            st = sys_.step(st, obs[:, t], sys_.noise(E, rng))
            if t in H:
                feats[t] = sys_.readout_features(st)
        if part == "train":
            tr = (p, feats)
        else:
            te = (p, feats)
    for h in H:
        pred = _ridge_fit_predict(tr[1][h], tr[0], te[1][h], V)
        rel[h] = float((pred == te[0]).mean())
    return rel


# ---------------------------------------------------------------- T3-DOWN from S0_TRIVIAL_RULES s3 text
def t3_down(sys_: System, task: Task, n_pairs: int = 500, seed: int = 4242):
    rng = np.random.default_rng(seed)
    cues, obs = paired_batch(task, n_pairs, rng)
    r = rollout(sys_, obs, np.random.default_rng(seed + 1), paired=True)
    S = sys_.full_state(r["final"]); R = r["features"]
    ds = np.abs(S[0::2] - S[1::2]).sum(1).max(); dr = np.abs(R[0::2] - R[1::2]).sum(1).max()
    return "NONE" if ds == 0 else ("PASSIVE" if dr == 0 else "FUNCTIONAL")


# ---------------------------------------------------------------- Certificate B-USE from DESIGN s6 text
def b_use(sys_: System, task: Task, E_train: int = 2000, E_test: int = 3000, seed: int = 99, alpha: float = 0.01):
    rng = np.random.default_rng(("B", seed).__hash__() & 0xFFFFFFFF)
    pol = train_readout(sys_, task, E_train, rng, batch)          # B trains its own readout on its own episodes
    cues, obs = batch(Task(task.V, task.k, 0.0), E_test, rng)      # source-randomized cue; query identical (h = 0)
    r = rollout(sys_, obs, rng)
    acc = float((pol.predict(r["features"]) == cues).mean())
    n, k = E_test, int(round(acc * E_test))
    p0 = 1.0 / task.V
    from scipy.stats import binom                                   # exact one-sided binomial tail P(X >= k)
    pval = float(binom.sf(k - 1, n, p0))
    return {"acc": acc, "p": pval, "functional": bool(pval < alpha)}


GRID = [(a, s) for a in (0.3, 0.6, 0.8, 0.9, 0.95) for s in (0.05, 0.3, 0.8, 1.5)]
KS = (2, 4, 8)
V = 4


def one(a, s):
    tk0 = Task(V, 2)
    sysw = Reservoir(tk0, a, s)
    rel = sysid_rel(sysw, V, tk0.n_symbols)                          # ONE vector per world (k-free)
    rows = []
    for k in KS:
        tk = Task(V, k)
        sk = Reservoir(tk, a, s)                                     # same world, k-variant
        t0 = time.time()
        A = certify(sk, tk, seed=11)
        rows.append({"a": a, "sigma": s, "k": k, "A_class": A["class"], "A_P2_effect": A["P2"]["effect"],
                     "A_P1_D": A["P1"]["D_bits"], "T3": t3_down(sk, tk), "B": b_use(sk, tk),
                     "REL": rel, "REL_at_q": rel[k + 1], "sec": round(time.time() - t0, 1)})
    return rows


if __name__ == "__main__":
    out, part, parts = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    with open(out, "a", encoding="utf-8") as fh:
        for i, (a, s) in enumerate(GRID):
            if i % parts == part:
                for r in one(a, s):
                    fh.write(json.dumps(r) + "\n"); fh.flush()
