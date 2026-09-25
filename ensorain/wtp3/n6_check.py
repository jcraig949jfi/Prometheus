"""Post-data adjudication (declared in the WTP-03 report): N6 = the best batch completion of ANY class,
tuned in hindsight (rank 1-4 x ridge .01/.1/1, low-rank ALS and CP-ALS, 20 iterations), on the same
stream and test set as each promoted specimen. Writes runs/wtp03/n6_check.json."""
import json
import os

import numpy as np

from .collider import experience, holdout, test_sets, collide, _addr
from .world3 import mem_cap, AC

OUT = os.path.join(os.path.dirname(__file__), "..", "runs", "wtp03")


def als_lr(dims, A, y, r, lam, rng, iters=20):
    D = len(dims)
    best = None
    for s in range(1, D):
        I = np.ravel_multi_index(A[:, :s].T, dims[:s])
        J = np.ravel_multi_index(A[:, s:].T, dims[s:])
        U = rng.normal(0, 0.3, (int(np.prod(dims[:s])), r))
        V = rng.normal(0, 0.3, (int(np.prod(dims[s:])), r))
        for _ in range(iters):
            for M, N, P, Q in ((U, V, I, J), (V, U, J, I)):
                for i in np.unique(P):
                    sel = P == i
                    B = N[Q[sel]]
                    M[i] = np.linalg.solve(B.T @ B + lam * np.eye(r), B.T @ y[sel])
        yield (lambda AA, U=U, V=V, s=s: (U[np.ravel_multi_index(AA[:, :s].T, dims[:s])] * V[np.ravel_multi_index(AA[:, s:].T, dims[s:])]).sum(1))


def als_cp(dims, A, y, r, lam, rng, iters=20):
    D = len(dims)
    F = [rng.normal(0, 0.5, (d, r)) for d in dims]
    for _ in range(iters):
        for m in range(D):
            P = np.ones((len(y), r))
            for j in range(D):
                if j != m:
                    P *= F[j][A[:, j]]
            for v in np.unique(A[:, m]):
                sel = A[:, m] == v
                B = P[sel]
                F[m][v] = np.linalg.solve(B.T @ B + lam * np.eye(r), B.T @ y[sel])

    def pred(AA):
        P = np.ones((len(AA), r))
        for j in range(D):
            P *= F[j][AA[:, j]]
        return P.sum(1)
    return pred


def n6(stream, T):
    dims, x, V0 = stream["dims"], stream["x"].reshape(-1), stream["V0"]
    A, y = _addr(dims, stream["c"]), stream["y"]
    TA = _addr(dims, T)
    best = (-9, None)
    rng = np.random.default_rng(0)
    for r in (1, 2, 3, 4):
        for lam in (0.01, 0.1, 1.0):
            for f in als_lr(dims, A, y, r, lam, rng):
                v = AC(f(TA), x[T], V0)
                best = max(best, (v, f"lowrank r{r} l{lam}"), key=lambda z: z[0])
            v = AC(als_cp(dims, A, y, r, lam, rng)(TA), x[T], V0)
            best = max(best, (v, f"cp r{r} l{lam}"), key=lambda z: z[0])
    return best


def main():
    S = json.load(open(os.path.join(OUT, "summary.json")))
    A = {a["h"]: a for a in json.load(open(os.path.join(OUT, "waveA.json")))["admitted"]}
    out = []
    for s in [s for s in S["specimens"] if s["full_chain"]]:
        a = A[s["h"]]
        g, f = a["g"], s["flag"]
        st, _ = experience(g, a["seed"])
        cap = mem_cap(g, st["x"].size)
        c = collide(st, cap, a["seed"])
        if f["set"] == "recomb":
            stR, blk, _ = holdout(st, np.random.default_rng(a["seed"] + 29))
            stream, T = stR, blk
        else:
            stream, T = st, test_sets(st, np.random.default_rng(a["seed"] + 17))["interp"]
        spec_ac = c["subs"][f["substrate"]]["AC"][f["set"]]
        v, which = n6(stream, T)
        out.append(dict(q=s["q"], substrate=f["substrate"], set=f["set"], specimen_AC=spec_ac, N6_AC=v, N6=which,
                        specimen_minus_N6=spec_ac - v))
        print(s["q"], f["substrate"], f["set"], "specimen AC", round(spec_ac, 3), "N6", round(v, 3), which, "diff", round(spec_ac - v, 3), flush=True)
    json.dump(out, open(os.path.join(OUT, "n6_check.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
