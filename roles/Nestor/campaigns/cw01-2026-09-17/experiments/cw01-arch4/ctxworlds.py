"""CONTEXT WORLDS (cycle 7): hand-built episode families in which the environmental REGIME changes the
correct answer, not the timing or difficulty of producing it. Regime 0 expects the stored value v;
regime 1 expects 15 - v (its 4-bit complement). No phase variable, mode bit, clock or memory operation
is given to the organism: the cue is an ordinary input word in an ordinary tick.

 A  OBSERVABLE   the ask tick carries the regime word: [ASK, tag, r]; PUT precedes it
 B  REMEMBERED   a cue tick [CUE, 1, c] opens the episode, then PUT, then a bare [ASK, tag]; the
                 decision-time observation is identical across regimes
 C  PREDICTIVE   one LIFETIME episode of T trials; the regime holds for `block` trials then flips;
                 each trial's cue is noisy (c = r with probability p, else 1 - r); the organism's
                 state persists across trials according to its own persist policy

Controls: SHUFFLED history (the cue tick comes after the ask), DESTROYED cue (c independent of r),
NOCUE (no cue tick at all). Ceilings of invariant policies are computed on the very episodes used.
Lifetime traces: eval_trace() records every ask (observation, cue, regime, answer, correctness) and
the register/tape state at each ask; interventions clear or overwrite state at chosen ticks.
Computational scope: integer programs on a bounded VM."""
from __future__ import annotations

import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common as CM            # noqa: E402
A = CM.A
from archaeon.wse.worlds import Episode, K_ASK, K_PUT   # noqa: E402
from proteus.foundry.vm import Player, Meter             # noqa: E402
CUE = 8                       # the NOISE word kind: never referenced by any world generator
VMAX = 16


def f_regime(r, v):
    return v if r == 0 else (VMAX - 1 - v)


def _rng(world, seed, index):
    return A.SplitMix64(A.seed_from("nestor.ctx", A.LOOP_SEED, world, seed, index))


def episodes_A(seed, index, n=16):
    rng = _rng("A", seed, index)
    out = []
    for _ in range(n):
        tag, v, r = 1 + rng.randbelow(60000), rng.randbelow(VMAX), rng.randbelow(2)
        out.append(Episode(ticks=[[K_PUT, tag, v], [K_ASK, tag, r]], expected={1: f_regime(r, v)}, intervention_tick=1, meta={"regime": [r], "cue": [r], "v": [v]}))
    return out


def episodes_B(seed, index, n=16, control=None):
    rng = _rng("B", seed, index)
    out = []
    for _ in range(n):
        tag, v, r = 1 + rng.randbelow(60000), rng.randbelow(VMAX), rng.randbelow(2)
        c = r if control != "destroyed" else rng.randbelow(2)
        if control == "shuffled":
            ticks, exp = [[K_PUT, tag, v], [K_ASK, tag], [CUE, 1, c]], {1: f_regime(r, v)}
        elif control == "nocue":
            ticks, exp = [[K_PUT, tag, v], [K_ASK, tag]], {1: f_regime(r, v)}
        else:
            ticks, exp = [[CUE, 1, c], [K_PUT, tag, v], [K_ASK, tag]], {2: f_regime(r, v)}
        out.append(Episode(ticks=ticks, expected=exp, intervention_tick=1, meta={"regime": [r], "cue": [c], "v": [v]}))
    return out


def episodes_C(seed, index, trials=16, block=4, p_cue=0.7, control=None, phase=None):
    rng = _rng("C", seed, index)
    r = rng.randbelow(2)
    off = rng.randbelow(block) if phase is None else phase
    ticks, expected, regimes, cues, vs = [], {}, [], [], []
    for t in range(trials):
        if t > 0 and (t + off) % block == 0:
            r = 1 - r
        c = (r if rng.unit() < p_cue else 1 - r) if control != "destroyed" else rng.randbelow(2)
        tag, v = 1 + rng.randbelow(60000), rng.randbelow(VMAX)
        ticks.append([CUE, 1, c])
        ticks.append([K_PUT, tag, v])
        ticks.append([K_ASK, tag])
        expected[len(ticks) - 1] = f_regime(r, v)
        regimes.append(r); cues.append(c); vs.append(v)
    return [Episode(ticks=ticks, expected=expected, intervention_tick=1, meta={"regime": regimes, "cue": cues, "v": vs, "block": block, "p_cue": p_cue})]


def make(world, seed, index, control=None, **kw):
    if world == "A":
        return episodes_A(seed, index, **kw)
    if world == "B":
        return episodes_B(seed, index, control=control, **kw)
    if world == "C":
        return episodes_C(seed, index, control=control, **kw)
    raise ValueError(world)


# ---------------------------------------------------------------- ceilings of invariant policies (on the very episodes)
def ceilings(eps, world):
    """Accuracy of policies that do NOT depend on lifetime context, on these episodes:
    ignore_cue_best   : best fixed transform of v (identity or complement) - the invariant policy
    cue_follow        : answer f(c, v) with the cue available at decision time (A: yes; B: no cue at
                        decision time -> same as ignore; C: the current trial's noisy cue)
    oracle            : f(r, v) - perfect regime knowledge
    tracker (C only)  : Bayes tracker over the regime with the true block length and cue reliability."""
    R = [r for e in eps for r in e.meta["regime"]]
    Cc = [c for e in eps for c in e.meta["cue"]]
    n = len(R)
    ignore = max(np.mean([r == 0 for r in R]), np.mean([r == 1 for r in R]))
    if world == "A":
        cue = 1.0
    elif world == "B":
        cue = ignore
    else:
        cue = float(np.mean([c == r for c, r in zip(Cc, R)]))
    out = {"n_asks": n, "ignore_cue_best": float(ignore), "cue_follow": float(cue), "oracle": 1.0}
    if world == "C":
        e = eps[0]
        block, p = e.meta["block"], e.meta["p_cue"]
        # forward filter over (regime, position-in-block) with known block length and p
        states = [(r, k) for r in (0, 1) for k in range(block)]
        prior = np.ones(len(states)) / len(states)
        correct = 0
        for t, (c, r) in enumerate(zip(Cc, R)):
            like = np.array([p if c == s[0] else 1 - p for s in states])
            post = prior * like
            post /= post.sum()
            pr1 = sum(post[i] for i, s in enumerate(states) if s[0] == 1)
            correct += int((1 if pr1 > 0.5 else 0) == r)
            nxt = np.zeros(len(states))
            for i, (rr, k) in enumerate(states):
                if k + 1 < block:
                    nxt[states.index((rr, k + 1))] += post[i]
                else:
                    nxt[states.index((1 - rr, 0))] += post[i]
            prior = nxt
        out["tracker"] = correct / n
    return out


# ---------------------------------------------------------------- lifetime traces and state interventions
def eval_trace(m, eps, clear_at=None, cue_override=None, snapshots=True):
    """Like evaluate(), with a per-ask trace and optional interventions.
    clear_at:     set of (episode index, tick index) before which registers and tape are cleared
    cue_override: dict (episode index, tick index) -> cue value written into the cue tick's word 2"""
    player = Player(m)
    trace, correct, asks, answered = [], 0, 0, 0
    for ei, ep in enumerate(eps):
        st = player.fresh_state()
        rng = A.SplitMix64(A.seed_from("wse.vmrng", 0, ei))
        ask_i = 0
        for ti, words in enumerate(ep.ticks):
            if clear_at and (ei, ti) in clear_at:
                st["tape"] = list(player.genome) + [0] * (player.tape_words - player.genome_len)
                st["regs"] = [0] * player.n_regs
            w = list(words)
            if cue_override and (ei, ti) in cue_override and w and w[0] == CUE:
                w[2] = cue_override[(ei, ti)]
            player.begin_tick(st)
            outs, _ = player.run_tick(st, [w], 1, rng, meter=Meter())
            if ti in ep.expected:
                a = outs[0][0] if outs[0] else None
                ok = int(a is not None and a == ep.expected[ti])
                asks += 1
                answered += int(a is not None)
                correct += ok
                rec = {"ep": ei, "tick": ti, "ask_i": ask_i, "answer": a, "expected": ep.expected[ti], "correct": ok,
                       "regime": ep.meta["regime"][ask_i], "cue": ep.meta["cue"][ask_i], "v": ep.meta["v"][ask_i]}
                if snapshots:
                    rec["regs"] = list(st["regs"])
                    rec["tape_nonzero"] = int(sum(1 for x in st["tape"][player.genome_len:] if x != 0))
                trace.append(rec)
                ask_i += 1
    return {"reward": correct / max(1, asks), "answered": answered / max(1, asks), "trace": trace}


def reward(m, eps):
    return A.evaluate(m, eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
