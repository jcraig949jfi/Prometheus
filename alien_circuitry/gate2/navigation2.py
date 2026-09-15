"""Navigation policies for the survivor gate (monoid universes).

  B0  random legal action
  B1  rank heuristic: prefer successors whose rank is closest to the target rank without falling below it
  B2  frozen local features: tier 0 target, tier 2 provably dead (rank below target), else rank distance then action order
  LAh B2 plus emulated exact lookahead of depth h (SAFE -> tier 0 with distance, TRAP -> tier 2); cost charged per call
  KA  kernel-aware reference (uses the withheld invariant as a tier-2 rule; NOT a baseline; residual-blind otherwise)
Searchers: greedy commit walk and guided DFS with backtracking and an expansion budget.
"""
from __future__ import annotations
import random
import numpy as np
from ..universe.monoid import kernel_compatible


class Cost:
    __slots__ = ("exp", "exm", "look_exp", "look_exm", "calls")

    def __init__(self):
        self.exp = self.exm = 0; self.look_exp = self.look_exm = 0.0; self.calls = 0


def make_policy(name: str, obs, U: dict, ball_cost: dict | None, seed: int = 0):
    rng = random.Random(seed); rank = obs.rank; targets = U["targets"]
    if name == "B0":
        return lambda s, j, idx, cost: (1, rng.random(), idx)
    if name == "B1":
        def k1(s, j, idx, cost):
            t = targets[j]; r = int(rank[s]) - int(rank[t])
            return (1, (r if r >= 0 else 100 - r), idx)
        return k1
    def b2(s, j, idx):
        t = targets[j]
        if s == t: return (0, 0, idx)
        if obs.provably_dead(s, t): return (2, 0, idx)
        return (1, int(rank[s]) - int(rank[t]), idx)
    if name == "B2":
        return lambda s, j, idx, cost: b2(s, j, idx)
    if name.startswith("LA"):
        h = int(name[2:]); bc = ball_cost[str(h)]
        def kl(s, j, idx, cost):
            t = targets[j]
            if s == t: return (0, 0, idx)
            if obs.provably_dead(s, t): return (2, 0, idx)
            v = obs.verdict(s, j, h); cost.calls += 1; cost.look_exp += bc["mean_states_expanded"]; cost.look_exm += bc["mean_transitions_examined"]
            if v == "SAFE": return (0, int(obs._D[s, j]), idx)
            if v == "TRAP": return (2, 0, idx)
            return (1, int(rank[s]) - int(rank[t]), idx)
        return kl
    if name == "KA":
        kmask = U["kmask"]
        def kk(s, j, idx, cost):
            t = targets[j]
            if s == t: return (0, 0, idx)
            if obs.provably_dead(s, t) or (kmask[s] & ~kmask[t]) != 0: return (2, 0, idx)
            return (1, int(rank[s]) - int(rank[t]), idx)
        return kk
    raise ValueError(name)


def greedy_walk(obs, policy, s0: int, j: int, Dcol: np.ndarray, max_steps: int = 64) -> dict:
    cost = Cost(); s = s0; steps = 0; catastrophic = False; t = obs.targets[j]; fi, fx = obs.fi, obs.fx
    while s != t and steps < max_steps:
        succ = fx[fi[s]:fi[s + 1]]; cost.exp += 1; cost.exm += len(succ)
        if not succ: break
        keys = [(policy(u, j, i, cost), u) for i, u in enumerate(succ)]
        k, u = min(keys)
        if k[0] == 2 and all(kk[0] == 2 for kk, _ in keys): break
        if Dcol[s] >= 0 and Dcol[u] < 0: catastrophic = True
        s = u; steps += 1
    solved = s == t; d0 = int(Dcol[s0])
    return {"solved": solved, "path_len": steps if solved else -1, "excess": (steps - d0) if solved else -1, "catastrophic": catastrophic,
            "exp": cost.exp, "exm": cost.exm, "look_exp": cost.look_exp, "look_exm": cost.look_exm, "calls": cost.calls}


def guided_dfs(obs, policy, s0: int, j: int, Dcol: np.ndarray, budget: int = 40000) -> dict:
    cost = Cost(); t = obs.targets[j]; fi, fx = obs.fi, obs.fx; visited = {s0}; traps_taken = 0
    def children(s):
        succ = fx[fi[s]:fi[s + 1]]; cost.exp += 1; cost.exm += len(succ)
        # tier-2 children carry a SOUND proof of death (rank below target, exhausted lookahead, or the kernel
        # invariant for KA); pruning them is valid and is what any searcher holding the proof would do
        return [u for k, u in sorted(((policy(u, j, i, cost), u) for i, u in enumerate(succ))) if k[0] != 2]
    if s0 == t:
        return {"solved": True, "path_len": 0, "excess": 0, "trap_transitions": 0, "exp": 0, "exm": 0, "look_exp": 0.0, "look_exm": 0.0, "calls": 0}
    stack = [(s0, children(s0), 0)]; d0 = int(Dcol[s0])
    while stack:
        s, ch, i = stack[-1]
        if i >= len(ch): stack.pop(); continue
        stack[-1] = (s, ch, i + 1); u = ch[i]
        if u in visited: continue
        visited.add(u)
        if Dcol[s] >= 0 and Dcol[u] < 0: traps_taken += 1
        if u == t:
            return {"solved": True, "path_len": len(stack), "excess": len(stack) - d0, "trap_transitions": traps_taken, "exp": cost.exp, "exm": cost.exm,
                    "look_exp": cost.look_exp, "look_exm": cost.look_exm, "calls": cost.calls}
        if cost.exp > budget: break
        stack.append((u, children(u), 0))
    return {"solved": False, "path_len": -1, "excess": -1, "trap_transitions": traps_taken, "exp": cost.exp, "exm": cost.exm,
            "look_exp": cost.look_exp, "look_exm": cost.look_exm, "calls": cost.calls}
