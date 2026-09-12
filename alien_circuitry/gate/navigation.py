"""Frozen policies and target-directed search for the U-A3 gate.

Policies rank candidate successors by a key tuple (smaller is better). Tier 0 = target reached / proven safe,
tier 1 = unknown (ranked by frozen local features: lower length bound, then higher out-degree, then action order),
tier 2 = proven dead.  No policy sees D, Reach or trap labels.

  B0  random legal action (seeded)
  B1  length heuristic: shorter successor first, then action order
  B2  frozen local features, zero lookahead (tier by immediate target / provably-dead rules)
  LAh exact bounded lookahead of depth h (1..5) on top of B2

Two searchers:
  greedy_walk  commit to the best-ranked action, never backtrack; a taken trap is a catastrophic choice
  guided_dfs   depth-first search with children ordered by the policy, backtracking, expansion budget
Costs: states expanded and transitions examined, both "cached" (per-problem memo shared by search and lookahead)
and "uncached" (every lookahead call counted in full).
"""
from __future__ import annotations
import random
import numpy as np
from .observation import Observer


class Cost:
    __slots__ = ("exp_c", "exm_c", "exp_u", "exm_u", "memo")

    def __init__(self):
        self.exp_c = self.exm_c = self.exp_u = self.exm_u = 0
        self.memo = set()

    def expand(self, obs: Observer, v: int):
        deg = obs.fi[v + 1] - obs.fi[v]
        self.exp_u += 1; self.exm_u += deg
        if v not in self.memo:
            self.memo.add(v); self.exp_c += 1; self.exm_c += deg

    def add_lookahead(self, r):
        _, _, eu, xu, en, xn = r
        self.exp_u += eu; self.exm_u += xu; self.exp_c += en; self.exm_c += xn


def make_policy(name: str, obs: Observer, seed: int = 0):
    rng = random.Random(seed)
    # every key starts with a tier: 0 target/proven safe, 1 unknown, 2 proven dead.  B0/B1 never prove anything.
    if name == "B0":
        return lambda s, t, idx, cost: (1, rng.random(), 0, idx)
    if name == "B1":
        return lambda s, t, idx, cost: (1, int(obs.LEN[s]), 0, idx)
    def b2_key(s, t, idx):
        if s == t:
            return (0, 0, 0, idx)
        if obs.provably_dead(s, t):
            return (2, 0, 0, idx)
        return (1, obs.len_bound(s, t), -int(obs.outdeg[s]), idx)
    if name == "B2":
        return lambda s, t, idx, cost: b2_key(s, t, idx)
    if name.startswith("LA"):
        h = int(name[2:])
        def key(s, t, idx, cost):
            if s == t:
                return (0, 0, 0, idx)
            if obs.provably_dead(s, t):
                return (2, 0, 0, idx)
            r = obs.lookahead(s, t, h, cost.memo)
            cost.add_lookahead(r)
            if r[0] == "SAFE":
                return (0, r[1], 0, idx)
            if r[0] == "TRAP":
                return (2, 0, 0, idx)
            return (1, obs.len_bound(s, t), -int(obs.outdeg[s]), idx)
        return key
    raise ValueError(name)


def greedy_walk(obs: Observer, policy, s0: int, t: int, Dcol: np.ndarray, max_steps: int = 64) -> dict:
    cost = Cost(); s = s0; steps = 0; catastrophic = False; first_trap_step = -1
    fi, fx = obs.fi, obs.fx
    while s != t and steps < max_steps:
        cost.expand(obs, s)
        succ = fx[fi[s]:fi[s + 1]]
        if not succ:
            break
        keys = [(policy(u, t, i, cost), u) for i, u in enumerate(succ)]
        k, u = min(keys)
        if k[0] == 2 and all(kk[0] == 2 for kk, _ in keys):
            break  # every option proven dead: stop
        if Dcol[s] >= 0 and Dcol[u] < 0 and not catastrophic:
            catastrophic = True; first_trap_step = steps
        s = u; steps += 1
    solved = s == t
    d0 = int(Dcol[s0])
    return {"solved": solved, "steps": steps, "path_len": steps if solved else -1, "excess": (steps - d0) if solved else -1,
            "catastrophic": catastrophic, "first_trap_step": first_trap_step,
            "exp_c": cost.exp_c, "exm_c": cost.exm_c, "exp_u": cost.exp_u, "exm_u": cost.exm_u}


def guided_dfs(obs: Observer, policy, s0: int, t: int, Dcol: np.ndarray, budget: int = 20000) -> dict:
    cost = Cost(); fi, fx = obs.fi, obs.fx
    visited = {s0}; trap_transitions = 0; pops = 0
    # stack entries: (state, ordered children list, next index)
    def children(s):
        cost.expand(obs, s)
        succ = fx[fi[s]:fi[s + 1]]
        keys = sorted(((policy(u, t, i, cost), u) for i, u in enumerate(succ)))
        return [u for _, u in keys]
    if s0 == t:
        return {"solved": True, "path_len": 0, "excess": 0, "trap_transitions": 0, "pops": 0, "exp_c": 0, "exm_c": 0, "exp_u": 0, "exm_u": 0}
    stack = [(s0, children(s0), 0)]
    d0 = int(Dcol[s0])
    while stack:
        s, ch, i = stack[-1]
        if i >= len(ch):
            stack.pop(); continue
        stack[-1] = (s, ch, i + 1)
        u = ch[i]
        if u in visited:
            continue
        visited.add(u); pops += 1
        if Dcol[s] >= 0 and Dcol[u] < 0:
            trap_transitions += 1
        if u == t:
            plen = len(stack)
            return {"solved": True, "path_len": plen, "excess": plen - d0, "trap_transitions": trap_transitions, "pops": pops,
                    "exp_c": cost.exp_c, "exm_c": cost.exm_c, "exp_u": cost.exp_u, "exm_u": cost.exm_u}
        if cost.exp_c > budget:
            break
        stack.append((u, children(u), 0))
    return {"solved": False, "path_len": -1, "excess": -1, "trap_transitions": trap_transitions, "pops": pops,
            "exp_c": cost.exp_c, "exm_c": cost.exm_c, "exp_u": cost.exp_u, "exm_u": cost.exm_u}
