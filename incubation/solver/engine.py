"""engine.py — deterministic search engines over an action alphabet.

An Action is a (possibly one-step) executable word of primitive IDs:

    reified=True    the action occupies ONE composition slot: depth cost 1, one search
                    node (the endpoint), one candidate test. Execs still cost the full
                    word length — reification never discounts execution.
    reified=False   flat inline block: each step is its own search node, candidate test,
                    and unit of depth. This is the "handed the composition but not
                    reified" control semantics.

A runtime failure inside an action (world dynamics rejecting a step) aborts the action,
records failure evidence, and creates no node for the failed step. Guards are executable
predicates evaluated BEFORE attempting an action; probe executions they perform are
counted honestly through the boundary.

Cost metrics per solve: nodes (states generated), cands (candidate/goal tests — equal to
nodes by construction in these engines), execs (primitive executions, from the boundary),
guard_skips, failures per action. Everything is deterministic: fixed action order, no
randomness, no wall-clock dependence.
"""
from __future__ import annotations

NODE_BUDGET = 12_000_000
EVIDENCE_CAP = 2000


class Action:
    __slots__ = ("aid", "word", "reified", "guard")

    def __init__(self, aid, word, reified=True, guard=None):
        self.aid = aid
        self.word = tuple(word)
        self.reified = reified
        self.guard = guard

    @property
    def depth_cost(self):
        return 1 if self.reified else len(self.word)


class Evidence:
    """Solver-side execution experience for one action: states it was attempted from.
    Balanced caps keep memory bounded; collection order is deterministic."""

    def __init__(self):
        self.fail = []          # (state_tuple, fail_step)
        self.ok = []            # state_tuple

    def record(self, state, fail_step):
        if fail_step is None:
            if len(self.ok) < EVIDENCE_CAP:
                self.ok.append(state)
        else:
            if len(self.fail) < EVIDENCE_CAP:
                self.fail.append((state, fail_step))


def _solution(path):
    return tuple(pid for word in path for pid in word)


def iddfs(bnd, actions, dmax=12, collect=None):
    """Iterative-deepening tree search. collect: optional {aid: Evidence}."""
    counters = {"nodes": 0, "cands": 0, "guard_skips": 0,
                "failures": {a.aid: 0 for a in actions},
                "attempts_ok": {a.aid: 0 for a in actions}}
    if bnd.is_goal(bnd.start):
        return {"solved": True, "sol": (), "found_at": 0, "uses": {},
                **counters, "execs": bnd.execs}

    def attempt(action, state):
        """Run an action from state. Returns (end_state|None, steps_completed)."""
        v = state
        for i, pid in enumerate(action.word):
            v = bnd.apply(pid, v)
            if v is None:
                return None, i
        return v, len(action.word)

    path = []

    def rec(state, budget):
        for action in actions:
            if action.depth_cost > budget:
                continue
            if action.guard is not None and action.guard(bnd, state):
                counters["guard_skips"] += 1
                continue
            if action.reified:
                ns, done = attempt(action, state)
                if collect is not None and action.aid in collect:
                    collect[action.aid].record(bnd.read(state),
                                               None if ns is not None else done)
                if ns is None:
                    counters["failures"][action.aid] += 1
                    continue
                counters["attempts_ok"][action.aid] += 1
                counters["nodes"] += 1
                counters["cands"] += 1
                if counters["nodes"] > NODE_BUDGET:
                    raise MemoryError
                path.append(action.word)
                if bnd.is_goal(ns) or rec(ns, budget - 1):
                    return True
                path.pop()
            else:
                # flat inline block: step-by-step nodes, abort on failure
                v = state
                pushed = 0
                failed = False
                for i, pid in enumerate(action.word):
                    nv = bnd.apply(pid, v)
                    if nv is None:
                        counters["failures"][action.aid] += 1
                        failed = True
                        break
                    counters["nodes"] += 1
                    counters["cands"] += 1
                    if counters["nodes"] > NODE_BUDGET:
                        raise MemoryError
                    path.append((pid,))
                    pushed += 1
                    v = nv
                    if bnd.is_goal(v):
                        return True
                if not failed:
                    counters["attempts_ok"][action.aid] += 1
                    if rec(v, budget - action.depth_cost):
                        return True
                for _ in range(pushed):
                    path.pop()
        return False

    for cap in range(1, dmax + 1):
        try:
            if rec(bnd.start, cap):
                sol = _solution(path)
                uses = {}
                # attribute uses per action id from the path structure
                # (reconstructed by replaying path segments against action words)
                return {"solved": True, "sol": sol, "found_at": cap,
                        "uses": _uses_from_path(path, actions),
                        **counters, "execs": bnd.execs}
        except MemoryError:
            return {"solved": False, "sol": None, "found_at": None, "uses": {},
                    **counters, "execs": bnd.execs, "budget_exhausted": True}
    return {"solved": False, "sol": None, "found_at": None, "uses": {},
            **counters, "execs": bnd.execs}


def _uses_from_path(path, actions):
    by_word = {}
    for a in actions:
        by_word.setdefault(a.word, a.aid)
    uses = {}
    for word in path:
        aid = by_word.get(word)
        if aid is None:                       # single primitive pushed by a flat block
            aid = by_word.get(word, word[0] if len(word) == 1 else str(word))
        uses[aid] = uses.get(aid, 0) + 1
    return uses


def bfs(bnd, actions, dmax=12):
    """Breadth-first graph search with duplicate-state elimination (arm P1:
    strongest primitive-only unrestricted composition search)."""
    counters = {"nodes": 0, "cands": 0, "guard_skips": 0,
                "failures": {a.aid: 0 for a in actions},
                "attempts_ok": {a.aid: 0 for a in actions}}
    if bnd.is_goal(bnd.start):
        return {"solved": True, "sol": (), "found_at": 0, "uses": {},
                **counters, "execs": bnd.execs}
    seen = {bnd.start: None}
    frontier = [bnd.start]
    for depth in range(1, dmax + 1):
        nxt = []
        for state in frontier:
            for action in actions:
                v = state
                ok = True
                for pid in action.word:
                    v = bnd.apply(pid, v)
                    if v is None:
                        counters["failures"][action.aid] += 1
                        ok = False
                        break
                if not ok or v in seen:
                    continue
                seen[v] = (state, action.aid, action.word)
                counters["nodes"] += 1
                counters["cands"] += 1
                if counters["nodes"] > NODE_BUDGET:
                    return {"solved": False, "sol": None, "found_at": None,
                            "uses": {}, **counters, "execs": bnd.execs,
                            "budget_exhausted": True}
                if bnd.is_goal(v):
                    sol, uses, cur = [], {}, v
                    while seen[cur] is not None:
                        prev, aid, word = seen[cur]
                        sol[:0] = word
                        uses[aid] = uses.get(aid, 0) + 1
                        cur = prev
                    return {"solved": True, "sol": tuple(sol), "found_at": depth,
                            "uses": uses, **counters, "execs": bnd.execs}
                nxt.append(v)
        frontier = nxt
    return {"solved": False, "sol": None, "found_at": None, "uses": {},
            **counters, "execs": bnd.execs}
