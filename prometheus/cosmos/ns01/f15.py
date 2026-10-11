"""NS-01 failure-15 discriminating test (prereg roles/Cosmos/campaigns/NS-01_2026-10-11/PREREG_F15_RELATIONAL.md).

    python -m prometheus.cosmos.supervise launch <rundir> --stall 900 -- \
        python -m prometheus.cosmos.ns01.f15 run <campaign_dir> <rundir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task

KS = (1, 4, 16)


class RelationalWitness(System):
    """W-REL: the cue exists only as the relation B - A (mod 4) across M share pairs, each share uniform at all times."""

    def __init__(self, task: Task, M: int = 32):
        self.t, self.M = task, M

    def init(self, E):
        return {"A": np.zeros((E, self.M)), "B": np.zeros((E, self.M)), "t": np.zeros(E, dtype=np.int64)}

    def noise(self, n, rng):
        return {"key": rng.integers(0, 4, (n, self.M)).astype(float), "r": rng.integers(0, 4, (n, self.M)).astype(float)}

    def step(self, st, o, nz):
        o = np.asarray(o)
        first = (st["t"] == 0)[:, None]
        c = np.clip(o, 0, 3).astype(float)[:, None]
        A = np.where(first, nz["key"], np.mod(st["A"] + nz["r"], 4))
        B = np.where(first, np.mod(c + nz["key"], 4), np.mod(st["B"] + nz["r"], 4))
        return {"A": A, "B": B, "t": st["t"] + 1}

    def readout_features(self, st):
        rel = np.mod(st["B"] - st["A"], 4).astype(int)
        return np.stack([(rel == v).mean(1) for v in range(4)], 1)

    def full_state(self, st):
        return np.hstack([st["A"], st["B"], st["t"][:, None].astype(float)])


def _onehot_cols(Ftr, Fte):
    out_tr, out_te = [], []
    for j in range(Ftr.shape[1]):
        a, b = np.rint(Ftr[:, j]).astype(int), np.rint(Fte[:, j]).astype(int)
        lo, hi = a.min(), a.max()
        if hi - lo > 12:
            return None, None                                  # not categorical: T1 n/a
        a, b = np.clip(a, lo, hi) - lo, np.clip(b, lo, hi) - lo
        out_tr.append(np.eye(hi - lo + 1)[a]), out_te.append(np.eye(hi - lo + 1)[b])
    return np.hstack(out_tr), np.hstack(out_te)


def _intervene(st, kind, rng):
    st = {k: v.copy() for k, v in st.items()}
    E, M = st["A"].shape
    r = rng.integers(0, 4, (E, M)).astype(float)
    if kind == "GAUGE":
        st["A"], st["B"] = np.mod(st["A"] + r, 4), np.mod(st["B"] + r, 4)
    else:
        st["B"] = np.mod(st["B"] + r, 4)
    return st


def measure(make, has_shares: bool, seed: int = 0) -> dict:
    from prometheus.cosmos.c4.cert_b import RF_WIDTH, _Ridge
    from prometheus.cosmos.ns01.signature import V, _episodes, excess
    rng = np.random.default_rng([0xF15, seed])
    out = {}

    def run(sys_, obs, iv=None):
        st = sys_.init(obs.shape[0])
        for t in range(obs.shape[1]):
            st = sys_.step(st, obs[:, t], sys_.noise(obs.shape[0], rng))
            if iv and t == 1:
                st = _intervene(st, iv, rng)
        return np.asarray(sys_.readout_features(st), float), np.asarray(sys_.full_state(st), float)

    def fe(Xtr, ytr, Xte, yte, rf):
        m = _Ridge(V, rf=RF_WIDTH if rf else 0, seed=1).fit(Xtr, ytr)
        return excess(float((m.predict(Xte) == yte).mean())), m

    for k in KS:
        t = Task(V, k)
        s = make(t)
        ctr, otr = _episodes(k, 2000, rng)
        cte, ote = _episodes(k, 2000, rng)
        Rtr, Ftr = run(s, otr)
        Rte, Fte = run(s, ote)
        rf, mR = fe(Rtr, ctr, Rte, cte, True)
        row = {"rf": rf, "full_rf": fe(Ftr, ctr, Fte, cte, True)[0], "full_lin": fe(Ftr, ctr, Fte, cte, False)[0]}
        Otr, Ote = _onehot_cols(Ftr, Fte)
        row["full_onehot"] = None if Otr is None else fe(Otr, ctr, Ote, cte, True)[0]
        if has_shares and k >= 1:
            for iv in ("GAUGE", "DESYNC"):
                Rx, _ = run(make(t), ote, iv)
                row[iv] = excess(float((mR.predict(Rx) == cte).mean()))
        out[k] = row
    return out


def _make(camp, name):
    if name == "W-REL":
        return lambda t: RelationalWitness(t)
    from prometheus.cosmos.ns01.evaluate import load_llm
    return load_llm((Path(camp) / "proposals" / name[0] / f"{int(name[1:]):02d}.py").read_text())


def one(j):
    return {"key": j["key"], "m": measure(_make(j["camp"], j["key"]), j["key"] in ("B08", "W-REL"))}


def classify(m: dict) -> str:
    ks = list(m)
    g = lambda x: float(np.mean([m[k]["rf"] - m[k][x] for k in ks])) if all(m[k][x] is not None for k in ks) else None
    gl, go = g("full_lin"), g("full_onehot")
    if gl is not None and gl <= .10:
        return "DECODER_CLASS_ARTIFACT"
    if go is not None and go <= .10:
        return "REPRESENTATION_DEPENDENT"
    gauge_ok = all(("GAUGE" not in m[k]) or (m[k]["GAUGE"] >= .9 * m[k]["rf"] and m[k]["DESYNC"] < .10) for k in ks)
    if gl is not None and gl >= .20 and (go is None or go >= .20) and gauge_ok:
        return "RELATIONAL"
    return "UNRESOLVED"


def run_all(camp, rundir):
    from prometheus.cosmos import supervise as SV
    jobs = [{"key": n, "camp": str(camp)} for n in ("B08", "W-REL", "B01", "B05")]
    return SV.run_jobs(one, jobs, rundir, key="key", out="f15.jsonl", workers=2, max_failures=0)


if __name__ == "__main__":
    a = sys.argv
    if a[1] == "run":
        run_all(a[2], a[3])
    elif a[1] == "analyse":
        rows = [json.loads(x) for x in Path(a[2], "f15.jsonl").read_text().splitlines() if x.strip()]
        print(json.dumps({r["key"]: {"class": classify({int(k): v for k, v in r["m"].items()}), "m": r["m"]} for r in rows},
                         indent=1))
