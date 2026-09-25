"""cw01-e09 RECONCILE PROBE (not qualification, no production seeds, nothing frozen).

The only composition form the substrate already owns is the representation ecology's
'program' kind (primordial/brain/c3_ecology.py:20-27, 56, 133-136): a straight-line chain
    (((x_a o1 x_b) o2 x_c) o3 x_d) mod 16,   ops = add sub mul xor and or on hex digits,
fit there by exhaustive search on a static regression target, never used as a world policy.
This probe asks the one question that decides whether e09 can be built on it at all:

  in w13, does a 3-op chain over observation digits reach capability MATERIALLY above the
  best single op (the primitive ceiling), and does evolution find such chains?

Organism: args [4] digit indices in [0, 4D), ops [3] in [0, 6); action magnitude = value % 8.
Single-op ceiling: exhaustive over 6 x 20 x 20 (op, a, b), value = op(x_a, x_b) % 8.
Pilot: 4 lineages x 150 generations x 128, mutation = one op id or one arg per child.
Scrambled preview: the same, with each op replaced by a seeded random 16x16 table.
Selection on train seeds; every ceiling/pilot number reported on held64 (30000..30063).
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent


def _bootstrap_lib():
    for cand in [HERE] + list(HERE.parents):
        if (cand / "lib" / "repopath.py").exists():
            sys.path.insert(0, str(cand / "lib"))
            return cand / "lib"
    raise RuntimeError("cannot locate lib/repopath.py walking up from %s" % HERE)


_bootstrap_lib()
sys.path.insert(0, str(HERE.parent / "cw01-e08"))
import seeds as S              # noqa: E402
import world_e08 as W8         # noqa: E402  (Spec, seeds, floors; world through the sanctioned constructor)
from primordial.brain.tt_policy import digits          # noqa: E402
from primordial.soup.b1.np_world import NpEncounter    # noqa: E402

OPS = [lambda a, b: (a + b) & 15, lambda a, b: (a - b) & 15, lambda a, b: (a * b) & 15,
       lambda a, b: a ^ b, lambda a, b: a & b, lambda a, b: a | b]          # c3_ecology.py:56


def op_tables(scramble_seed=None):
    """[6, 16, 16] lookup tables; scrambled = seeded random tables of the same shape/cost."""
    g = np.arange(16)
    T = np.stack([f(g[:, None], g[None, :]) for f in OPS]).astype(np.int64)
    if scramble_seed is not None:
        rng = np.random.Generator(np.random.PCG64(scramble_seed))
        T = rng.integers(0, 16, size=T.shape)
    return T


def forward(args, ops, T, obs, grow):
    """args [P,4], ops [P,3] -> action magnitude [n] for obs rows [n, D] of genome grow[n]."""
    dg = digits(obs.astype(np.uint16)).astype(np.int64)         # (n, 4D)
    a = args[grow]                                              # (n,4)
    o = ops[grow]                                               # (n,3)
    rows = np.arange(len(obs))
    x = [dg[rows, a[:, i]] for i in range(4)]
    v = T[o[:, 0], x[0], x[1]]
    v = T[o[:, 1], v, x[2]]
    v = T[o[:, 2], v, x[3]]
    return v % 8


def forward_single(op, a, b, T, obs, grow):
    dg = digits(obs.astype(np.uint16)).astype(np.int64)
    rows = np.arange(len(obs))
    return T[op[grow], dg[rows, a[grow]], dg[rows, b[grow]]] % 8


def rollout(spec, seeds, P, act_fn):
    k, S_, D = len(seeds), spec.S, spec.D
    n = P * k
    w = NpEncounter(spec.mech, spec.wid, with_obs=True)
    obs = w.reset(np.tile(np.asarray(seeds, np.int64), P))
    genv = np.repeat(np.arange(P), k)
    grow = np.repeat(genv, S_)
    for t in range(spec.T):
        mag = act_fn(obs.reshape(n * S_, D), grow).reshape(n, S_)
        a = np.repeat(mag[:, :, None], spec.W, axis=2).astype(np.int32)
        obs, _, done = w.step(a)
        if done.all():
            break
    return np.clip(w.charge, 0, None).sum(1).reshape(P, k).sum(1).astype(np.int64)


def evolve_chain(spec, T, rng, d4, gens=150, P=128, log_every=25):
    tr, he = W8.train_seeds(None) if False else None, None    # placeholder to keep names local
    train = np.arange(9100, 9108)
    args = rng.integers(0, d4, size=(P, 4))
    ops = rng.integers(0, 6, size=(P, 3))
    hist = []
    for g in range(gens):
        fit = rollout(spec, train, P, lambda o, gr: forward(args, ops, T, o, gr))
        if g % log_every == 0 or g == gens - 1:
            hist.append((g, int(fit.max()), float(fit.mean())))
        if g == gens - 1:
            break
        order = np.argsort(-fit, kind="stable")
        el = order[:4]
        cand = rng.integers(0, P, size=(P - 4, 3))
        win = cand[np.arange(P - 4), np.argmax(fit[cand], axis=1)]
        na, no = args[win].copy(), ops[win].copy()
        which = rng.random(P - 4) < 0.5
        i_op = rng.integers(0, 3, size=P - 4)
        i_ar = rng.integers(0, 4, size=P - 4)
        new_op = rng.integers(0, 6, size=P - 4)
        new_ar = rng.integers(0, d4, size=P - 4)
        for c in range(P - 4):
            if which[c]:
                no[c, i_op[c]] = new_op[c]
            else:
                na[c, i_ar[c]] = new_ar[c]
        args = np.concatenate([args[el], na]); ops = np.concatenate([ops[el], no])
    best = int(np.argmax(fit))
    return {"args": args[best].tolist(), "ops": ops[best].tolist(), "train_fit": int(fit[best]), "hist": hist}


def main():
    t0 = time.time()
    cfg8 = json.loads((HERE.parent / "cw01-e08" / "WORLD.json").read_text(encoding="utf-8"))
    spec = W8.world_spec(cfg8)
    train, held = np.arange(9100, 9108), np.arange(30000, 30064)
    d4 = spec.d
    T = op_tables()
    rep = {"world": spec.wid, "T": spec.T, "D": spec.D, "digits": d4}
    fl = W8.trivial_floors(spec, held)
    rep["held64_floor_abstain"] = fl["per_seed"]["abstain"]
    print("w13 D=%d digits=%d | held64 abstain floor %.1f | competence floor 166.47" % (spec.D, d4, fl["per_seed"]["abstain"]))

    # ---- single-op ceiling: exhaustive ------------------------------------------------
    combos = np.array([(o, a, b) for o in range(6) for a in range(d4) for b in range(d4)])
    P = len(combos)
    op_, a_, b_ = combos[:, 0], combos[:, 1], combos[:, 2]
    fit_tr = rollout(spec, train, P, lambda o, gr: forward_single(op_, a_, b_, T, o, gr))
    top = np.argsort(-fit_tr, kind="stable")[:64]
    fit_he = rollout(spec, held, 64, lambda o, gr: forward_single(op_[top], a_[top], b_[top], T, o, gr)) / len(held)
    i_best = int(np.argmax(fit_tr))
    rep["single_op"] = {"n": int(P), "train_max": int(fit_tr.max()), "train_abstain": 1272,
                        "best_by_train": {"op": int(op_[i_best]), "a": int(a_[i_best]), "b": int(b_[i_best]),
                                          "held64": float(fit_he[0])},
                        "held64_max_over_top64": float(fit_he.max()),
                        "n_top64_above_competence": int((fit_he > 166.47).sum())}
    print("single-op: train max %d (abstain 1272) | best-by-train held64 %.1f | max held64 over top64 %.1f | competent %d/64"
          % (fit_tr.max(), fit_he[0], fit_he.max(), (fit_he > 166.47).sum()))

    # ---- 3-op chain pilots ---------------------------------------------------------------
    for label, Tc in (("chain_arith", T), ("chain_scrambled", op_tables(scramble_seed=S.seed("cw01-e09-probe", "scramble")))):
        runs = []
        for j in range(4):
            rng = S.rng("cw01-e09-probe", label, j)
            r = evolve_chain(spec, Tc, rng, d4)
            args = np.array([r["args"]]); ops = np.array([r["ops"]])
            h = rollout(spec, held, 1, lambda o, gr: forward(args, ops, Tc, o, gr))[0] / len(held)
            r["held64"] = float(h)
            runs.append(r)
            print("   %s lineage %d: train %d  held64 %.1f  ops %s args %s  traj %s"
                  % (label, j, r["train_fit"], h, r["ops"], r["args"], [(g, m) for g, m, _ in r["hist"]][::2]))
        rep[label] = runs
    rep["_elapsed_s"] = round(time.time() - t0, 1)
    (HERE / "PROBE_E09.json").write_text(json.dumps(rep, indent=1, ensure_ascii=True), encoding="utf-8")
    print("PROBE_E09.json written (%.0f s)" % (time.time() - t0))


if __name__ == "__main__":
    main()
