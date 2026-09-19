"""world.integer_batch.v1 (overnight C92; design U1 / ext.batch.v1): the integer world's semantics over n
environments in lockstep behind ONE object. Registers, charge and survival live in numpy arrays of shape
(n_envs, ...) and the linear transition is one vectorised statement per op; the trace (the reference's exact
JSON text per tick, hashed per env), events and the pending-action queue stay per env in Python because they
ARE the reference's observable contract and must match it byte for byte.

A batch world is a world: with n_envs=1 it satisfies core.world.v1 through reset/observe/step/... so admission
drives it through the ordinary contract and compares its trace with world.integer.v1's (implements=
"world.integer", C70). The executor uses the batch face (reset_batch/observe_batch/step_batch/events_batch/
trace_hashes/summaries) only when budget.batch asks for it, and the receipts must come out equal to the scalar
path's run for run (tests/test_batch.py). Envs finish at different ticks: a finished env is masked, never
stepped again, so its trace is exactly what the scalar world would have produced.
"""
from __future__ import annotations

import hashlib
import json
from typing import Dict, List, Optional

import numpy as np

from prometheus.toolbox.contracts import ActionSpace, EVENT_ID, Event
from prometheus.toolbox.ref.worlds import DEFAULTS, M, XS64, stream

_U = np.uint64


def _xs_next(s: np.ndarray) -> np.ndarray:
    """xorshift64 over a uint64 vector, same constants as XS64 (wraparound is the mask)."""
    with np.errstate(over="ignore"):
        x = s.copy()
        x ^= x << _U(13); x ^= x >> _U(7); x ^= x << _U(17)
    return x


class IntegerWorldBatch:
    kind = "world.integer_batch.v1"
    capabilities = frozenset({"core.world.v1", "ext.events.v1", "ext.snapshot.v1", "ext.legal_actions.v1", "ext.multiplayer.v1",
                              "ext.intervention.world_params.v1", "ext.cost.v1", "ext.replay.bit.v1", "ext.world.lifetime_state.v1", "ext.batch.v1"})
    replay_class = "BIT"
    ACT_MUL = 97

    def __init__(self, n_envs: int = 1, **params):
        unknown = sorted(set(params) - set(DEFAULTS))
        if unknown:
            raise ValueError("%s: unknown params %s" % (self.kind, unknown))
        if not isinstance(n_envs, int) or n_envs < 1:
            raise ValueError("%s: n_envs must be a positive int" % self.kind)
        self.p = dict(DEFAULTS, **params); self.n_players = self.p["n_players"]; self.n_envs = n_envs
        s = stream("structure", self.p["world_seed"]); R = self.p["n_regs"]
        self.ops = [(s.below(R), s.below(7) + 1, s.below(R), s.below(7) + 1, s.below(R), s.below(M)) for _ in range(self.p["n_ops"])]
        self.targets = [s.below(R) for _ in range(self.p["act_width"])]
        self.yreg = s.below(R); self.ylo = s.below(M); self.yhi = (self.ylo + self.p["yield_width"]) % M
        self.obs_regs = list(range(min(self.p["obs_regs"], R)))
        self.regs = None; self.ev: List[List[Event]] = [[] for _ in range(n_envs)]; self.steps = np.zeros(n_envs, dtype=np.int64)
        self._prev = None

    def manifest(self) -> dict:
        return {"kind": self.kind, "params": self.p, "implements": "world.integer", "n_envs": self.n_envs}

    # ------------------------------------------------------------ batch face (ext.batch.v1)
    def reset_batch(self, seeds: List[int], keep: bool = False) -> None:
        if len(seeds) != self.n_envs:
            raise ValueError("%s: %d seeds for %d envs" % (self.kind, len(seeds), self.n_envs))
        p = self.p; n = self.n_envs; R = p["n_regs"]
        if keep and self.regs is not None:
            regs = self.regs.copy(); stoch = self.stoch.copy()
            pending = [[(q[0] - int(self.t[i]), q[1], q[2], q[3]) for q in self.pending[i]] for i in range(n)]
        else:
            regs = np.zeros((n, R), dtype=np.int64); stoch = np.zeros(n, dtype=_U); pending = [[] for _ in range(n)]
            for i, seed in enumerate(seeds):
                s = stream("init", p["world_seed"], seed)
                regs[i] = [s.below(M) for _ in range(R)]
                stoch[i] = _U(stream("stoch", p["world_seed"], seed).s)
        self.regs = regs; self.stoch = stoch; self.pending = pending
        self.charge = np.full((n, self.n_players), p["start_charge"], dtype=np.int64)
        self.alive = np.ones((n, self.n_players), dtype=bool)
        self.t = np.zeros(n, dtype=np.int64); self.active = np.ones(n, dtype=bool); self.seeds = list(seeds)
        self.h = [hashlib.sha256() for _ in range(n)]; self.ev = [[] for _ in range(n)]

    def observe_batch(self, pid: int) -> List[List[int]]:
        obs = self.regs[:, self.obs_regs].tolist(); ch = self.charge[:, pid].tolist()
        return [o + [min(15, max(0, c) // 8)] for o, c in zip(obs, ch)]

    def legal_actions(self, pid: int) -> ActionSpace:
        return ActionSpace(self.p["act_width"], self.p["act_range"])

    def step_batch(self, actions: List[Dict[int, List[int]]]) -> List[bool]:
        """actions[i] is env i's {pid: action}; None ABANDONS env i (the executor lost its players: it is never stepped
        again and its trace stays where it was). Finished envs are skipped whatever is passed for them."""
        p = self.p; n = self.n_envs; act = self.active
        if len(actions) != n:
            raise ValueError("%s: %d action dicts for %d envs" % (self.kind, len(actions), n))
        for i in range(n):
            if actions[i] is None:
                act[i] = False
        W, AR, AC, AD = p["act_width"], p["act_range"], p["act_cost"], p["action_delay"]
        # phase 1: intake, per env (events and the pending queue are the reference's exact sequence)
        for i in np.flatnonzero(act):
            t = int(self.t[i]); ev = self.ev[i]; ch = self.charge[i]; al = self.alive[i]; pend = self.pending[i]
            for pid in range(self.n_players):
                if not al[pid]:
                    continue
                a = list(actions[i].get(pid, []))[:W]
                a = [x % AR for x in a] + [0] * (W - len(a))
                mag = sum(a); cost = mag * AC
                if cost > ch[pid]:
                    mag, cost = 0, 0
                if cost:
                    ch[pid] -= cost; ev.append((t, EVENT_ID["RESOURCE_CHANGE"], pid, 0, -cost))
                ev.append((t, EVENT_ID["ACTION"], pid, 0, mag))
                if mag:
                    for k, x in enumerate(a):
                        if x:
                            pend.append((t + AD, pid, self.targets[k], x * self.ACT_MUL))
            landing = sorted((q for q in pend if q[0] == t), key=lambda q: (q[1], q[2]))
            self.pending[i] = [q for q in pend if q[0] > t]
            for _, pid, tgt, amt in landing:
                self.regs[i, tgt] = (self.regs[i, tgt] + amt) % M; ev.append((t, EVENT_ID["STATE_WRITE"], pid, tgt, amt))
        # phase 2: transition, vectorised over the active envs
        if not p["_cheat_skip_dynamics"]:
            idx = np.flatnonzero(act); regs = self.regs
            if p["regime_period"]:
                flip = ((self.t[idx] // p["regime_period"]) % 2 == 1)
            else:
                flip = np.zeros(len(idx), dtype=bool)
            for dst, a, s1, b, s2, c in self.ops:
                aa = np.where(flip, (M - a) % M, a)
                regs[idx, dst] = (aa * regs[idx, s1] + b * regs[idx, s2] + c) % M
            if p["stoch_rate"]:
                st = self.stoch[idx]
                x1 = _xs_next(st); kick = (x1 % _U(p["stoch_rate"])) == 0
                x2 = _xs_next(x1); x3 = _xs_next(x2)
                # the reference writes regs[xs.below(n_regs)] = xs.below(M): Python evaluates the RIGHT side first, so the
                # VALUE comes from draw 2 and the register index from draw 3 -- the contract is the reference's behaviour
                val = (x2 % _U(M)).astype(np.int64); which = (x3 % _U(p["n_regs"])).astype(np.int64)
                new = np.where(kick, x3, x1)
                for j, i in enumerate(idx):
                    if kick[j]:
                        regs[i, which[j]] = val[j]
                self.stoch[idx] = new
        # phase 3: economy, per env (settlement order and events are the contract)
        done = [not bool(a) for a in act]
        for i in np.flatnonzero(act):
            t = int(self.t[i]); ev = self.ev[i]; ch = self.charge[i]; al = self.alive[i]
            v = int(self.regs[i, self.yreg]); lo, hi = self.ylo, self.yhi
            win = (lo <= v < hi) if lo < hi else (v >= lo or v < hi)
            winners = [q for q in range(self.n_players) if al[q]] if win else []
            for pid in range(self.n_players):
                if not al[pid]:
                    continue
                ch[pid] -= p["step_cost"]
                if pid in winners:
                    g = p["yield_amt"] // len(winners); ch[pid] += g; ev.append((t, EVENT_ID["YIELD"], pid, self.yreg, g))
                    if len(winners) > 1:
                        ev.append((t, EVENT_ID["CONTACT"], pid, len(winners), g))
                if ch[pid] <= 0:
                    al[pid] = False; ev.append((t, EVENT_ID["ABSORBED"], pid, 0, int(ch[pid])))
            self.h[i].update(json.dumps([t, self.regs[i].tolist(), ch.tolist(), al.tolist()]).encode())
            self.t[i] = t + 1; self.steps[i] += 1
            fin = (t + 1 >= p["horizon"]) or (self.n_players > 0 and not al.any())
            if fin:
                self.active[i] = False
            done[i] = fin
        return done

    def events_batch(self) -> List[List[Event]]:
        out, self.ev = self.ev, [[] for _ in range(self.n_envs)]
        return out

    def trace_hashes(self) -> List[str]:
        return [h.hexdigest() for h in self.h]

    def summaries(self) -> List[dict]:
        return [{"ticks": int(self.t[i]), "charge": self.charge[i].tolist(), "alive": self.alive[i].tolist()} for i in range(self.n_envs)]

    def accounting_batch(self) -> List[Dict[str, int]]:
        return [{"world_steps": int(s)} for s in self.steps]

    # ------------------------------------------------------------ scalar face (core.world.v1): env 0 of an n_envs=1 world
    def _one(self):
        if self.n_envs != 1:
            raise ValueError("%s: the scalar face needs n_envs=1 (this world has %d)" % (self.kind, self.n_envs))

    def reset(self, seed: int, keep: bool = False) -> None:
        self._one(); self.reset_batch([seed], keep=keep)

    def observe(self, pid: int) -> List[int]:
        return self.observe_batch(pid)[0]

    def step(self, actions: Dict[int, List[int]]) -> bool:
        self._one()
        return self.step_batch([actions])[0]

    def trace_hash(self) -> str:
        return self.trace_hashes()[0]

    def events(self) -> List[Event]:
        return self.events_batch()[0]

    def accounting(self) -> Dict[str, int]:
        return {"world_steps": int(self.steps.sum())}

    def summary(self) -> dict:
        return self.summaries()[0]

    def snapshot(self) -> bytes:
        self._one()
        st = {"t": int(self.t[0]), "regs": self.regs[0].tolist(), "charge": self.charge[0].tolist(), "alive": self.alive[0].tolist(),
              "pending": [list(q) for q in self.pending[0]], "stoch": int(self.stoch[0]), "seed": self.seeds[0], "active": bool(self.active[0])}
        return json.dumps({"st": st, "h": self.h[0].hexdigest(), "steps": int(self.steps[0])}, sort_keys=True).encode()

    def restore(self, snapshot: bytes) -> None:
        self._one(); d = json.loads(snapshot.decode()); st = d["st"]
        self.t[0] = st["t"]; self.regs[0] = st["regs"]; self.charge[0] = st["charge"]; self.alive[0] = st["alive"]
        self.pending[0] = [tuple(q) for q in st["pending"]]; self.stoch[0] = _U(st["stoch"]); self.active[0] = st["active"]
        self.h[0] = hashlib.sha256(("restored:" + d["h"]).encode()); self.ev[0] = []
