"""THESEUS-48: where do solvers fail at V 8 -- storing the cue, or releasing it?

Prereg: roles/Theseus/prereg/2026-10-10_store_release/PREREG.md.

For each selected-task solver, episodes at V 8, k 8 (task seed 0; 400 train / 400 test, the
same draws as task_J) are run with a trace that also records the memory field M
(task_system.run_with_input does not). Ridge one-vs-rest decoders (task_system's form) are fit
on:
  STORE    the state at the step BEFORE the query (t = k): every non-sensor channel X[1:] and
           all memory M, concatenated -- is the cue held anywhere?
  RELEASE  the sensor channel after the query (= task_J readout ch0) -- is it released?
Per solver: J_store, J_release, and the best single store source (one X channel or one M row).

  python -m theseus.synth.probe_store --tag <tag> [--workers 4]
"""

import argparse
import json
import os
from multiprocessing import Pool

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

from . import sel_eval as se  # noqa: E402
from . import substrate as sb  # noqa: E402
from . import task_comp as tcm  # noqa: E402
from . import task_system as ts  # noqa: E402

V, K = 8, 8
SOURCES = [  # (stratum, arm, run, evaldir with selected-task J rows)
    (1, "law", "v0_2t0_2026-10-08", "theseus/runs/comp_task_law_2026-10-08"),
    (1, "nolaw", "v0_2t0nl_2026-10-08", "theseus/runs/comp_task_law_2026-10-08"),
    (2, "law", "v0_2t0_s2_2026-10-08", "theseus/runs/comp_task_s2_law_2026-10-08"),
    (2, "nolaw", "v0_2t0nl_s2_2026-10-08", "theseus/runs/comp_task_s2_law_2026-10-08"),
    (3, "law", "v0_2t0_s3_2026-10-09", "theseus/runs/comp_task_s3_law_2026-10-09"),
    (3, "nolaw", "v0_2t0nl_s3_2026-10-09", "theseus/runs/comp_task_s3_law_2026-10-09"),
    (4, "law", "v0_2t0_s4_2026-10-09", "theseus/runs/comp_task_s4_law_2026-10-09"),
    (4, "nolaw", "v0_2t0nl_s4_2026-10-09", "theseus/runs/comp_task_s4_law_2026-10-09"),
]


def trace_states(g, obs, N=ts.N_CELLS, seed=0):
    """As task_system.run_with_input, returning (X at t=len-2, M at t=len-2, X at t=len-1)."""
    C = g["C"]
    field = sb.Field(g, N)
    X = sb._init(g, C, N, seed)
    M = np.zeros((C, N))
    m0 = X.mean(1).copy()
    H = [X.copy() for _ in range(sb.HIST)]
    pre = None
    for t, x in enumerate(obs):
        if x is not None and x >= 0:
            X[0, :] = 0.0
            X[0, (int(x) * ts.IN_GROOVE) % N] = ts.IN_AMP
        ts._step(g, X, M, H, t, field, N, m0, {})
        H.append(X.copy())
        H.pop(0)
        if t == len(obs) - 2:
            pre = (X.copy(), M.copy())
    return pre[0], pre[1], X.copy()


def _decode(F1, c1, F2, c2):
    F1, F2 = np.tanh(F1), np.tanh(F2)
    mu, sd = F1.mean(0), F1.std(0) + 1e-9
    A = np.hstack([(F1 - mu) / sd, np.ones((len(F1), 1))])
    B = np.hstack([(F2 - mu) / sd, np.ones((len(F2), 1))])
    W = np.linalg.solve(A.T @ A + 1.0 * np.eye(A.shape[1]), A.T @ np.eye(V)[c1])
    return float(((B @ W).argmax(1) == c2).mean())


def job(g):
    from prometheus.cosmos.c3 import task as tk
    t = tk.Task(V=V, k=K)
    rng = np.random.default_rng(0)  # identical draws to task_J(seed=0)
    c1, o1 = tk.batch(t, 400, rng)
    c2, o2 = tk.batch(t, 400, rng)
    S = [[trace_states(g, row) for row in o] for o in (o1, o2)]
    C = g["C"]

    def feats(i, fn):
        return np.array([fn(s) for s in S[i]])
    store = lambda s: np.concatenate([s[0][1:].ravel(), s[1].ravel()])  # noqa: E731
    out = {"J_store": _decode(feats(0, store), c1, feats(1, store), c2),
           "J_release": _decode(feats(0, lambda s: s[2][0]), c1, feats(1, lambda s: s[2][0]), c2)}
    best, best_src = 0.0, None
    for c in range(1, C):
        j = _decode(feats(0, lambda s, c=c: s[0][c]), c1, feats(1, lambda s, c=c: s[0][c]), c2)
        if j > best:
            best, best_src = j, f"X{c}"
    for c in range(C):
        j = _decode(feats(0, lambda s, c=c: s[1][c]), c1, feats(1, lambda s, c=c: s[1][c]), c2)
        if j > best:
            best, best_src = j, f"M{c}"
    out.update({"J_store_best_single": best, "best_source": best_src, "C": C})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    out = f"theseus/runs/{a.tag}"
    os.makedirs(out, exist_ok=True)
    items, meta = [], {}
    for st, arm, run, d in SOURCES:
        g = dict(se.sample(run))
        J = {json.loads(l)["id"]: json.loads(l)["v"] for l in open(f"{d}/J_{run}.jsonl", encoding="utf-8")}
        for i in sorted(J):
            if J[i] >= tcm.SOLVER:
                k = f"{run}:{i}"
                meta[k] = {"stratum": st, "arm": arm, "run": run, "id": i, "J_sel": J[i]}
                items.append((k, g[i]))
    with Pool(a.workers) as pool:
        done = tcm._stage(pool, f"{out}/ROWS.jsonl", items, job)
    with open(f"{out}/TABLE.jsonl", "w", encoding="utf-8") as f:
        for k, _ in items:
            f.write(json.dumps({**meta[k], **done[k]}, separators=(",", ":")) + "\n")
    print(json.dumps({"n": len(items)}))


if __name__ == "__main__":
    main()
