"""THESEUS-31: give Theseus programs an INPUT CHANNEL and a task (Hestia #1897 s4.19).

A genome becomes an organism that is driven by an observation stream. Each step t:
  1. INPUT   channel 0 is a TRANSIENT SENSOR: it is overwritten with a one-hot pulse of
             amplitude IN_AMP at cell site(x) = (x * IN_GROOVE) mod N (zeros elsewhere).
             (An additive input was rejected before any task run: pulses would persist in a
             program that does nothing, so "do nothing" would solve cue recall.)
  2. RULES   the genome's rules run once (exactly substrate.run's per-step semantics).
The task is the shared cue-recall demand of prometheus.cosmos.c3.task (public): cue at t=0,
k distractors, a query at t=k+1; the organism "answers" through a linear readout of its
state at the query, fitted on training episodes and scored on held-out episodes:
  J = held-out accuracy (chance = 1/V).
The readout is a ridge one-vs-rest classifier written here (no Cosmos harness code is used),
so J measures what the program's own state carries about the cue.

This module re-implements the per-step loop of substrate.run with an input hook; it is
checked against substrate.run with no input (identical traces) in theseus/synth/tests.
"""

from __future__ import annotations

import numpy as np

from . import substrate as sb

IN_AMP = 1.0
IN_GROOVE = 5
N_CELLS = 32


def _step(g, X, M, H, t, field, N, m0, lens_cache):
    """One step of substrate.run's inner loop (sequential rules), in place on X/M."""
    for r in g["rules"]:
        op, p, d = r["op"], r["p"], r["dst"]
        S = X
        if op == "diffuse":
            new = S[d] + p[0] * (field.nmean(S[r["src"][0]]) - S[d])
        elif op == "advect":
            new = S[d] + p[1] * (np.roll(S[r["src"][0]], int(p[0])) - S[d])
        elif op == "react":
            prod = np.ones(N)
            for j, s in enumerate(r["src"]):
                prod = prod * (p[1] + p[2 + j] * np.tanh(S[s]))
            new = S[d] + p[0] * np.tanh(prod)
        elif op == "saturate":
            new = p[0] * np.tanh(S[d] / p[0])
        elif op == "conserve":
            new = S[d] - p[0] * (S[d].mean() - m0[d])
        elif op == "decay":
            new = S[d] * (1.0 - p[0])
        elif op == "remember":
            M[d] = (1 - p[0]) * M[d] + p[0] * S[r["src"][0]]
            continue
        elif op == "recall":
            new = S[d] + p[0] * (M[d] - S[d])
        elif op == "threshold":
            new = S[d] + p[1] * np.tanh(8.0 * (S[r["src"][0]] - p[0]))
        elif op == "replicate":
            src = S[r["src"][0]]
            new = S[d] + p[0] * np.maximum(field.nmax(src) - S[d], 0.0)
        elif op == "select":
            q = np.quantile(S[d], 1.0 - p[0])
            new = np.where(S[d] >= q, S[d], S[d] * (1.0 - p[1]))
        elif op == "mirror":
            new = (1 - p[0]) * S[d] + p[0] * S[d][::-1]
        elif op == "coarse":
            new = S[d] + p[1] * (sb._blockmean(S[r["src"][0]], int(p[0])) - S[d])
        elif op == "delay":
            new = S[d] + p[1] * (H[-int(p[0])][r["src"][0]] - S[d])
        elif op == "wrap":
            P = p[0]
            new = np.mod(S[d] + P / 2.0, P) - P / 2.0
        elif op == "rank":
            rk = np.argsort(np.argsort(S[d])) / max(N - 1, 1) * 2.0 - 1.0
            new = (1 - p[0]) * S[d] + p[0] * (S[d].mean() + rk * S[d].std())
        elif op == "drive":
            cell = int(p[2] * N) % N
            new = S[d].copy()
            new[cell] += p[0] * np.sin(2.0 * np.pi * t / p[1])
        elif op == "gate":
            cond = S[r["src"][0]]
            new = S[d] + p[1] * np.where(cond > p[0], S[r["src"][1]] - S[d], 0.0)
        elif op == "inject":
            new = S[d] + p[0] * M[d]
        elif op == "modulate":
            new = S[d] + p[0] * M[d] * S[r["src"][0]]
        elif op == "lensmap":
            new = S[d] + p[0] * (sb._lens_apply(r["lens"], S) - S[d])
        else:  # pragma: no cover
            raise ValueError(op)
        X[d] = new
    if field.bc == "absorb":
        X[:, 0] = 0.0
        X[:, -1] = 0.0
    if not np.all(np.isfinite(X)) or np.abs(X).max() > sb.CLIP:
        X[:] = np.clip(np.nan_to_num(X, nan=0.0, posinf=sb.CLIP, neginf=-sb.CLIP), -sb.CLIP, sb.CLIP)
        return True
    return False


def run_with_input(g, obs, N=N_CELLS, seed=0):
    """Run genome g driven by the integer sequence obs (len T). Returns (trace[T,C,N], blowup)."""
    C = g["C"]
    field = sb.Field(g, N)
    X = sb._init(g, C, N, seed)
    M = np.zeros((C, N))
    m0 = X.mean(1).copy()
    H = [X.copy() for _ in range(sb.HIST)]
    trace = np.empty((len(obs), C, N))
    blow = False
    for t, x in enumerate(obs):
        if x is not None and x >= 0:
            X[0, :] = 0.0
            X[0, (int(x) * IN_GROOVE) % N] = IN_AMP
        blow |= _step(g, X, M, H, t, field, N, m0, {})
        trace[t] = X
        H.append(X.copy())
        H.pop(0)
    return trace, blow


def features(g, obs, N=N_CELLS, seed=0):
    tr, blow = run_with_input(g, obs, N, seed)
    f = tr[-1].ravel()
    return np.tanh(f), blow


def task_J(g, V=4, k=4, n_train=400, n_test=400, seed=0, N=N_CELLS):
    """Held-out cue-recall accuracy of a ridge readout on the program's state at the query."""
    from prometheus.cosmos.c3 import task as tk
    t = tk.Task(V=V, k=k)
    rng = np.random.default_rng(seed)
    c1, o1 = tk.batch(t, n_train, rng)
    c2, o2 = tk.batch(t, n_test, rng)
    F1, F2, blow = [], [], False
    for row in o1:
        f, b = features(g, row, N)
        F1.append(f)
        blow |= b
    for row in o2:
        f, b = features(g, row, N)
        F2.append(f)
        blow |= b
    F1, F2 = np.array(F1), np.array(F2)
    mu, sd = F1.mean(0), F1.std(0) + 1e-9
    A = np.hstack([(F1 - mu) / sd, np.ones((len(F1), 1))])
    B = np.hstack([(F2 - mu) / sd, np.ones((len(F2), 1))])
    W = np.linalg.solve(A.T @ A + 1.0 * np.eye(A.shape[1]), A.T @ np.eye(V)[c1])
    return {"J": float(((B @ W).argmax(1) == c2).mean()), "chance": 1.0 / V, "blowup": bool(blow),
            "V": V, "k": k, "n_train": n_train, "n_test": n_test}
