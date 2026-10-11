"""NS-01 Arm D: a symbolic mechanism grammar (non-LLM generator).

A mechanism = (topology, write rule, 1-3 dynamics operators in order, readout), with parameters drawn from a seeded
rng. State: a float array x (E, n) plus, for spatial topologies, an integer head that moves v cells per step. The
current symbol is always appended to readout and full_state (as in every archived system).

DOCUMENTED BIAS (directive s4): the primitives below are Cosmos's choice and inherit the archive's vocabulary
(vectors, rings, grids, graphs, counters; mixing, decay, diffusion, shifts, thresholds). Unfamiliar organisations
reachable here come only from unusual COMBINATIONS (e.g. modular counters with sorting and a moving window).
Absent by construction: particles / variable-size state, learned rules, continuous time, multi-agent interaction.

Feedback (same exclusion engine as Arm C): after a REJECTED signal, every primitive used by the rejected proposal has
its sampling weight halved; ACCEPTED leaves weights unchanged.
"""
from __future__ import annotations

import json
from typing import Dict, List

import numpy as np

from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot

TOPOLOGY = ["vec", "ring", "grid", "graph", "counters"]
WRITE = ["add_embed", "set_at_head", "toggle_mod", "gate_mult"]
DYN = ["linear_mix", "diffuse", "shift", "decay", "tanh", "threshold", "sort", "noise", "swap_pairs", "majority"]
READ = ["all", "window", "summary", "proj"]


class GrammarMechanism(System):
    def __init__(self, task: Task, spec: Dict):
        self.t, self.s = task, spec
        r = np.random.default_rng(spec["pseed"])
        n = spec["n"]
        self.n = n
        self.W = r.standard_normal((task.n_symbols, n)) / np.sqrt(n)
        self.K = r.integers(0, spec.get("m", 5), (task.n_symbols, n))
        self.M = np.linalg.qr(r.standard_normal((n, n)))[0] * spec.get("a", 0.9)
        A = (r.random((n, n)) < 3.0 / n).astype(float)
        np.fill_diagonal(A, 0)
        self.A = A / np.maximum(A.sum(1, keepdims=True), 1)
        self.R = r.standard_normal((n, 8)) / np.sqrt(n)
        self.side = int(round(np.sqrt(n))) if spec["topology"] == "grid" else None

    def init(self, E):
        return {"x": np.zeros((E, self.n)), "h": np.zeros(E, dtype=np.int64), "cur": np.zeros(E, dtype=np.int64)}

    def noise(self, n, rng):
        return {"z": rng.standard_normal((n, self.n)), "u": rng.random(n), "i": rng.integers(0, self.n, (n, 2))}

    def _nb(self, x):
        tp = self.s["topology"]
        if tp == "ring":
            return 0.5 * (np.roll(x, 1, 1) + np.roll(x, -1, 1))
        if tp == "grid":
            g = x.reshape(len(x), self.side, self.side)
            return (0.25 * (np.roll(g, 1, 1) + np.roll(g, -1, 1) + np.roll(g, 1, 2) + np.roll(g, -1, 2))).reshape(len(x), -1)
        if tp == "graph":
            return x @ self.A.T
        return np.repeat(x.mean(1, keepdims=True), x.shape[1], 1)

    def step(self, st, o, nz):
        s, x, h = self.s, st["x"].copy(), st["h"].copy()
        E = len(o)
        w = s["write"]
        if w == "add_embed":
            x = x + s["g"] * self.W[o]
        elif w == "set_at_head":
            x[np.arange(E), h % self.n] = s["g"] * self.W[o, 0] * np.sqrt(self.n)
        elif w == "toggle_mod":
            x = np.mod(x + self.K[o], s.get("m", 5))
        elif w == "gate_mult":
            x = x * (1.0 + s["g"] * self.W[o]) + 0.1 * s["g"] * self.W[o]
        for op in s["dyn"]:
            if op == "linear_mix":
                x = x @ (self.A.T * s.get("a", 0.9) if s["topology"] == "graph" else self.M.T)
            elif op == "diffuse":
                x = (1 - s["D"]) * x + s["D"] * self._nb(x)
            elif op == "shift":
                x = np.roll(x, s["v"], 1)
            elif op == "decay":
                x = x * (1 - s["delta"])
            elif op == "tanh":
                x = np.tanh(s["gain"] * x)
            elif op == "threshold":
                x = (x > s["theta"]).astype(float)
            elif op == "sort":
                x = np.sort(x, 1)
            elif op == "noise":
                x = x + s["sigma"] * nz["z"]
            elif op == "swap_pairs":
                sw = nz["u"] < s["pswap"]
                a, b = nz["i"][:, 0], nz["i"][:, 1]
                xa, xb = x[np.arange(E), a].copy(), x[np.arange(E), b].copy()
                x[np.arange(E)[sw], a[sw]], x[np.arange(E)[sw], b[sw]] = xb[sw], xa[sw]
            elif op == "majority":
                x = np.sign(x + np.roll(x, 1, 1) + np.roll(x, -1, 1))
        if s["topology"] in ("ring", "grid"):
            h = (h + s["hv"] + np.where(nz["u"] < s.get("jit", 0.0), 1, 0)) % self.n
        x = np.clip(x, -1e6, 1e6)
        return {"x": x, "h": h, "cur": np.asarray(o).copy()}

    def readout_features(self, st):
        x, r = st["x"], self.s["read"]
        if r == "window":
            E = len(x)
            idx = (st["h"][:, None] + np.arange(-1, 2)[None]) % self.n
            f = x[np.arange(E)[:, None], idx]
        elif r == "summary":
            xs = np.sort(x, 1)
            f = np.stack([x.sum(1), x.max(1), x.min(1), np.abs(x).mean(1)], 1)
            f = np.hstack([f, xs[:, -3:]])
        elif r == "proj":
            f = x @ self.R
        else:
            f = x
        return np.hstack([f, onehot(st["cur"], self.t.n_symbols)])

    def full_state(self, st):
        return np.hstack([st["x"], onehot(st["h"], self.n), onehot(st["cur"], self.t.n_symbols)])


class Grammar:
    def __init__(self, seed: int):
        self.rng = np.random.default_rng([0x6EA7, seed])
        self.w = {c: {p: 1.0 for p in ps} for c, ps in
                  (("topology", TOPOLOGY), ("write", WRITE), ("dyn", DYN), ("read", READ))}

    def _pick(self, cat, k=1):
        ps = list(self.w[cat])
        p = np.array([self.w[cat][x] for x in ps])
        return list(self.rng.choice(ps, size=k, replace=False, p=p / p.sum()))

    def sample(self) -> Dict:
        r = self.rng
        tp = self._pick("topology")[0]
        n = {"vec": 16, "ring": 24, "grid": 36, "graph": 32, "counters": 12}[tp]
        spec = {"topology": tp, "n": n, "write": self._pick("write")[0],
                "dyn": self._pick("dyn", int(r.integers(1, 4))), "read": self._pick("read")[0],
                "pseed": int(r.integers(1, 2 ** 31)), "g": float(r.uniform(0.3, 2.0)), "a": float(r.uniform(0.5, 1.0)),
                "D": float(r.uniform(0.05, 0.5)), "v": int(r.integers(1, 4)), "delta": float(r.uniform(0.01, 0.3)),
                "gain": float(r.uniform(0.5, 3.0)), "theta": float(r.uniform(-0.5, 0.5)),
                "sigma": float(r.uniform(0.01, 0.5)), "pswap": float(r.uniform(0.05, 0.5)),
                "m": int(r.integers(2, 8)), "hv": int(r.integers(0, 3)), "jit": float(r.uniform(0, 0.3))}
        return spec

    def feedback(self, spec: Dict, accepted: bool):
        if accepted:
            return
        for cat, vals in (("topology", [spec["topology"]]), ("write", [spec["write"]]), ("dyn", spec["dyn"]),
                          ("read", [spec["read"]])):
            for v in vals:
                self.w[cat][v] *= 0.5


def make_from_spec(spec: Dict):
    return lambda task: GrammarMechanism(task, spec)


def spec_json(spec: Dict) -> str:
    return json.dumps(spec, sort_keys=True)
