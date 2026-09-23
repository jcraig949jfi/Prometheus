"""P-A11 (serendipity): the e09 chain organism on e07's accumulate-and-report task.

Parent T-X07 (<- T-E09). Delta: e07's task (theta rotated by an attempt-stable Q, noisy
observations, a query index) with lifetimes drawn from disjoint TRAIN and HELD-OUT streams;
organisms are e09's straight-line chains (4 digit args over 20 hex digits of the 5-feature
observation vector [4 obs components scaled to uint16, query index], 3 ops from
add/sub/mul/xor/and/or mod 16), output y = -2 + 4*v/15. Single-op ceiling by exhaustive
search (2400) selected on TRAIN and scored on HELD-OUT; 3-op chains by GA (4 lineages x 150
gens x 128), arithmetic and scrambled op tables. Reference points: floor (output 0) and the
stateless optimum (hand-built linear readout, no memory) on the same held-out lifetimes.
Descriptive.
"""
from __future__ import annotations

import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "loop"))
import looprun as L            # noqa: E402
import seeds as S              # noqa: E402

W7 = L.import_world("cw01-e07", "world_e07")
PID, TID, AID = "P-A11", "T-X07", "cw01-loop1-PA11"
OPS = [lambda a, b: (a + b) & 15, lambda a, b: (a - b) & 15, lambda a, b: (a * b) & 15,
       lambda a, b: a ^ b, lambda a, b: a & b, lambda a, b: a | b]
N_TRAIN, N_HELD, GENS, P = 32, 32, 150, 128


def op_tables(scramble_seed=None):
    g = np.arange(16)
    T = np.stack([f(g[:, None], g[None, :]) for f in OPS]).astype(np.int64)
    if scramble_seed is not None:
        T = np.random.Generator(np.random.PCG64(scramble_seed)).integers(0, 16, size=T.shape)
    return T


def digits_of(stream):
    """(n_life*L, 20) hex digits of [4 obs components in [-4,4] -> uint16, query*4096]."""
    obs = stream["obs"].reshape(-1, stream["obs"].shape[-1])
    q = stream["q"].reshape(-1)
    u = np.clip((obs + 4.0) / 8.0, 0, 1) * 65535
    feats = np.concatenate([u.astype(np.int64), (q * 4096)[:, None]], axis=1)          # (n, 5)
    d = [((feats >> (12 - 4 * j)) & 15) for j in range(4)]                                # per feature 4 digits
    return np.stack(d, axis=2).reshape(feats.shape[0], -1)                               # (n, 20)


def targets_of(stream):
    n, Lh = stream["q"].shape
    tq = stream["theta"][np.arange(n)[:, None], stream["q"]]
    return tq.reshape(-1)


def score_chain(args, ops, T, dg, tq):
    """args (P,4) ops (P,3) -> mean score per organism over all rows."""
    Pn = args.shape[0]
    out = np.zeros(Pn)
    for p in range(Pn):
        x = [dg[:, args[p, i]] for i in range(4)]
        v = T[ops[p, 0], x[0], x[1]]
        v = T[ops[p, 1], v, x[2]]
        v = T[ops[p, 2], v, x[3]]
        y = -2.0 + 4.0 * v / 15.0
        out[p] = np.maximum(0.0, 1.0 - np.abs(y - tq)).mean()
    return out


def score_single(op, a, b, T, dg, tq):
    v = T[op, dg[:, a], dg[:, b]]
    y = -2.0 + 4.0 * v / 15.0
    return np.maximum(0.0, 1.0 - np.abs(y - tq)).mean()


def evolve_chain(T, dg_tr, tq_tr, rng):
    args = rng.integers(0, 20, size=(P, 4))
    ops = rng.integers(0, 6, size=(P, 3))
    for g in range(GENS):
        fit = score_chain(args, ops, T, dg_tr, tq_tr)
        if g == GENS - 1:
            break
        order = np.argsort(-fit, kind="stable")
        el = order[:4]
        cand = rng.integers(0, P, size=(P - 4, 3))
        win = cand[np.arange(P - 4), np.argmax(fit[cand], axis=1)]
        na, no = args[win].copy(), ops[win].copy()
        which = rng.random(P - 4) < 0.5
        io, ia = rng.integers(0, 3, P - 4), rng.integers(0, 4, P - 4)
        vo, va = rng.integers(0, 6, P - 4), rng.integers(0, 20, P - 4)
        for c in range(P - 4):
            if which[c]:
                no[c, io[c]] = vo[c]
            else:
                na[c, ia[c]] = va[c]
        args, ops = np.concatenate([args[el], na]), np.concatenate([ops[el], no])
    b = int(np.argmax(fit))
    return args[b], ops[b], float(fit[b])


def main():
    t0 = time.time()
    cfg = L.load_cfg("cw01-e07", AID)
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "claim_type": "serendipity-descriptive",
                         "delta": "e09 chain organism on e07's task with disjoint train/held-out lifetimes; single-op ceiling vs 3-op chains vs scrambled ops",
                         "unchanged": "chain representation, op tables, GA form from the e09 probe; e07 task and scoring",
                         "attacks": "was e09's boundary the substrate (w13 does not generalise) or the idea (composition does not help)?",
                         "n_train_lifetimes": N_TRAIN, "n_held_lifetimes": N_HELD, "gens": GENS, "pop": P,
                         "reference": "floor = output 0; stateless optimum = hand-built readout y = (Q^T o)_q on held-out",
                         "decision": "descriptive: chains materially above the single-op ceiling on HELD-OUT is recorded as material"})
    Q = W7.attempt_Q(cfg, AID, "loop")
    tr = W7.task_stream(cfg, AID, "loop", "train", 0, N_TRAIN, Q)
    he = W7.task_stream(cfg, AID, "loop", "held", 0, N_HELD, Q)
    dg_tr, tq_tr, dg_he, tq_he = digits_of(tr), targets_of(tr), digits_of(he), targets_of(he)
    floor = float(np.maximum(0.0, 1.0 - np.abs(tq_he)).mean())
    o_he = he["obs"].reshape(-1, 4)
    q_he = he["q"].reshape(-1)
    y_stateless = (o_he @ Q)[np.arange(len(q_he)), q_he]
    stateless = float(np.maximum(0.0, 1.0 - np.abs(np.clip(y_stateless, -4, 4) - tq_he)).mean())
    T = op_tables()
    combos = [(o, a, b) for o in range(6) for a in range(20) for b in range(20)]
    tr_s = np.array([score_single(o, a, b, T, dg_tr, tq_tr) for o, a, b in combos])
    best = int(np.argmax(tr_s))
    ceiling_held = score_single(*combos[best], T, dg_he, tq_he)
    top64 = np.argsort(-tr_s)[:64]
    held_top = np.array([score_single(*combos[i], T, dg_he, tq_he) for i in top64])
    print("floor %.4f stateless %.4f | single-op train max %.4f -> held %.4f (max over top64 %.4f)"
          % (floor, stateless, tr_s.max(), ceiling_held, held_top.max()), flush=True)
    chains = {}
    for label, Tc in (("arith", T), ("scrambled", op_tables(S.seed(AID, "scramble")))):
        chains[label] = []
        for j in range(4):
            a, o, f = evolve_chain(Tc, dg_tr, tq_tr, S.rng(AID, label, j))
            h = float(score_chain(a[None], o[None], Tc, dg_he, tq_he)[0])
            chains[label].append({"lineage": j, "train": f, "held": h, "ops": o.tolist(), "args": a.tolist()})
            print("   chain %-9s L%d  train %.4f  held %.4f  ops %s args %s" % (label, j, f, h, o.tolist(), a.tolist()), flush=True)
    best_chain_held = max(c["held"] for c in chains["arith"])
    material = bool(best_chain_held > ceiling_held + 0.02 and best_chain_held > floor + 0.02)
    res = {"perturbation_id": PID, "parent": TID, "floor_held": floor, "stateless_optimum_held": stateless,
           "single_op": {"n": len(combos), "train_max": float(tr_s.max()), "ceiling_held_by_train": float(ceiling_held),
                         "held_max_over_top64": float(held_top.max()), "best": combos[best]},
           "chains": chains, "material": material,
           "reading": ("3-op chains exceed the single-op ceiling on held-out lifetimes" if material else
                       "chains do not materially exceed the single-op ceiling on held-out lifetimes"),
           "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, res, ph)
    L.append_evidence(TID, PID, "chain organism on e07 task: single-op ceiling %.3f, best arith chain %.3f, best scrambled %.3f, stateless optimum %.3f, floor %.3f"
                      % (ceiling_held, best_chain_held, max(c["held"] for c in chains["scrambled"]), stateless, floor), material, detail=res["single_op"])
    L.append_evidence("T-E09", PID, "composition probe on a generalising task: %s" % res["reading"], material,
                      state="TEMPORAL_STASIS" if not material else "ACTIVE",
                      state_reason="chain form still cannot compose on a second task; the boundary is the representation, not w13" if not material else "composition helps on a generalising task; the boundary was w13")
    print("DONE %s (%.0f s)" % (res["reading"], time.time() - t0))


if __name__ == "__main__":
    main()
