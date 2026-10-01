"""W4 simulation core (shared by pilot.py and world.py). No treatment code here."""
import math
from collections import deque
import numpy as np

N_MODELS, N_STATES, N_INPUTS = 64, 6, 2
START, FORBIDDEN, GOAL = 0, 4, 5
EPISODES, MAX_STEPS = 1000, 30
SEEDS = list(range(10))
INF = 10 ** 9
PARAMS = dict(N_MODELS=N_MODELS, N_STATES=N_STATES, N_INPUTS=N_INPUTS, START=START,
              FORBIDDEN=FORBIDDEN, GOAL=GOAL, EPISODES=EPISODES, MAX_STEPS=MAX_STEPS)


def make_family(seed):
    return np.random.default_rng([seed, 1]).integers(0, N_STATES, size=(N_MODELS, N_STATES, N_INPUTS))


def true_indices(seed):
    return np.random.default_rng([seed, 2]).integers(0, N_MODELS, size=EPISODES)


def robust_values(T, V):
    """AND-OR fixed point over consistent set V using only safe actions."""
    sub = T[V]  # k x S x A
    safe = ~np.any(sub == FORBIDDEN, axis=0)  # S x A
    val = np.full(N_STATES, INF)
    val[GOAL] = 0
    for _ in range(N_STATES + 1):
        new = val.copy()
        for s in range(N_STATES):
            if s == GOAL:
                continue
            best = INF
            for a in range(N_INPUTS):
                if safe[s, a]:
                    w = val[sub[:, s, a]].max()
                    if w < INF:
                        best = min(best, 1 + w)
            new[s] = best
        if np.array_equal(new, val):
            break
        val = new
    return val, safe


def robust_action(T, V, s):
    """Limit-seeking skeleton. Returns (action or None, trigger_reason or None, allowed)."""
    val, safe = robust_values(T, V)
    sa = [a for a in range(N_INPUTS) if safe[s, a]]
    if not sa:
        return None, "none_safe", list(range(N_INPUTS))
    if val[s] >= INF:
        return None, "none_progress", sa
    sub = T[V]
    best, arg = INF, None
    for a in sa:
        w = val[sub[:, s, a]].max()
        if w < INF and 1 + w < best:
            best, arg = 1 + w, a
    return arg, None, sa


def bfs_first_action(table, s, avoid_forbidden):
    """table: S x A. First action of a shortest path s->GOAL, or None."""
    if s == GOAL:
        return None
    prev = {s: None}
    q = deque([s])
    while q:
        u = q.popleft()
        if u == GOAL:
            break
        for a in range(N_INPUTS):
            v = int(table[u, a])
            if avoid_forbidden and v == FORBIDDEN:
                continue
            if v not in prev:
                prev[v] = (u, a)
                q.append(v)
    if GOAL not in prev:
        return None
    node = GOAL
    while prev[node][0] != s:
        node = prev[node][0]
    return prev[node][1]


def plan_with_model(table, s):
    a = bfs_first_action(table, s, True)
    if a is None:
        a = bfs_first_action(table, s, False)
    if a is None:
        ok = [x for x in range(N_INPUTS) if table[s, x] != FORBIDDEN]
        a = ok[0] if ok else 0
    return a


def run_episode(T, true_m, policy, rng=None):
    V = np.arange(N_MODELS)
    s = START
    forb = 0
    steps = MAX_STEPS
    probes = 0
    probe_bits = 0.0
    probe_true_safe = 0
    trig_none_safe = 0
    for t in range(MAX_STEPS):
        a, is_probe, reason = policy(T, V, s, true_m, rng)
        s2 = int(T[true_m, s, a])
        before = len(V)
        V = V[T[V, s, a] == s2]
        if is_probe and before > 1:  # repair (attempt 2): singleton-set triggers are not probes
            probes += 1
            probe_bits += math.log2(before) - math.log2(len(V))
            probe_true_safe += int(s2 != FORBIDDEN)
            trig_none_safe += int(reason == "none_safe")
        if s2 == FORBIDDEN:
            forb += 1
        s = s2
        if s == GOAL:
            steps = t + 1
            break
    return dict(forbidden=forb, steps=steps, reached=int(s == GOAL), probes=probes,
                probe_bits=probe_bits, probe_true_safe=probe_true_safe,
                trig_none_safe=trig_none_safe, final_log2V=math.log2(len(V)))


# ---- phase-1 policies: CE reference, null twin, positive control ----

def policy_ce(T, V, s, true_m, rng):
    return plan_with_model(T[V.min()], s), False, None


def policy_null_twin(T, V, s, true_m, rng):
    a, reason, allowed = robust_action(T, V, s)
    if reason is None:
        return a, False, None
    return int(allowed[rng.integers(len(allowed))]), True, reason


def policy_positive(T, V, s, true_m, rng):
    a, reason, allowed = robust_action(T, V, s)
    tt = T[true_m]
    if reason is None:
        return plan_with_model(tt, s), False, None
    k = len(V)

    def key(x):
        s2 = int(tt[s, x])
        cell = int(np.sum(T[V, s, x] == s2))
        bits = math.log2(k) - math.log2(cell)
        prog = s2 == GOAL or bfs_first_action(tt, s2, True) is not None
        return (s2 != FORBIDDEN, bits, prog, -x)
    return max(allowed, key=key), True, reason


def run_arm(seed, policy, rng_stream=None):
    T = make_family(seed)
    idx = true_indices(seed)
    rng = np.random.default_rng([seed, rng_stream]) if rng_stream is not None else None
    return [run_episode(T, int(m), policy, rng) for m in idx]
