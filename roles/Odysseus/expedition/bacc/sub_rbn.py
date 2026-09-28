"""bacc substrate S3: random Boolean networks (N=10, K=2, synchronous). Behaviour = attractor set.

    python3 sub_rbn.py [--smoke]      -> rbn_result.json
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bacc  # noqa: E402

N = 10
S = 1 << N
TARGET = 0b1011001110


def successor_table(g):
    nxt = [0] * S
    for x in range(S):
        y = 0
        for i, (a, b, t) in enumerate(g):
            if (t >> ((((x >> a) & 1) << 1) | ((x >> b) & 1))) & 1:
                y |= 1 << i
        nxt[x] = y
    return nxt


def attractors(g):
    nxt = successor_table(g)
    color = [0] * S            # 0 unseen, >0 id of the pass that visited it
    atts = []
    for x0 in range(S):
        if color[x0]:
            continue
        path = []
        x = x0
        while not color[x]:
            color[x] = x0 + 1
            path.append(x)
            x = nxt[x]
        if color[x] == x0 + 1:                 # closed a new cycle within this pass
            cyc = path[path.index(x):]
            k = cyc.index(min(cyc))
            atts.append(tuple(cyc[k:] + cyc[:k]))
    return frozenset(atts)


def evaluate(g):
    A = attractors(g)
    best = max(N - bin(s ^ TARGET).count("1") for a in A for s in a)
    return A, best / N


def evaluate_coarse(g):
    """POST-HOC sensitivity (not preregistered): behaviour = multiset of attractor lengths only."""
    A, s = evaluate(g)
    return tuple(sorted(len(a) for a in A)), s


def lendist(a, b):
    from collections import Counter
    ca, cb = Counter(a), Counter(b)
    return sum(((ca - cb) + (cb - ca)).values())


def mutate(g, rng, j):
    i = rng.randrange(N)
    a, b, t = g[i]
    if rng.random() < 0.5:
        t ^= 1 << rng.randrange(4)
    else:
        if rng.random() < 0.5:
            v = rng.randrange(N - 1); a = v if v < a else v + 1
        else:
            v = rng.randrange(N - 1); b = v if v < b else v + 1
    return g[:i] + ((a, b, t),) + g[i + 1:]


def sample(rng):
    return tuple((rng.randrange(N), rng.randrange(N), rng.randrange(16)) for _ in range(N))


def gkey(g):
    return g


def neutral(s, s0):
    return abs(s - s0) < 1e-12


def improving(s, s0):
    return s > s0 + 1e-12


def symdiff(a, b):
    return len(a ^ b)


SPEC = bacc.Spec("rbn_n10k2", mutate, evaluate, gkey, neutral, improving, sample, symdiff)
COARSE = bacc.Spec("rbn_n10k2", mutate, evaluate_coarse, gkey, neutral, improving, sample, lendist)


def parents(k=8):
    out = []
    i = 0
    while len(out) < k:
        g = sample(bacc.rng_for("rbn.parent", i))
        _, s = evaluate(g)
        if 0.5 - 1e-9 <= s <= 0.8 + 1e-9:
            out.append(("rbn%d" % i, g))
        i += 1
    return out


def main():
    smoke = "--smoke" in sys.argv
    coarse = "--coarse" in sys.argv
    spec = COARSE if coarse else SPEC
    W, D, m, NN = (1, 3, 8, 50) if smoke else (2, 20, 32, 2000)
    ps = parents(2 if smoke else 8)
    t0 = time.time()
    walkers, null = bacc.run_all(spec, ps, W, D, m, procs=4, null_n=NN)
    t_run = time.time() - t0
    per, summ = bacc.analyse(spec, walkers, null, D)
    for pid, g in ps:
        A, s0 = evaluate(g)
        per[pid]["parent_n_attractors"] = len(A)
        per[pid]["parent_attractor_lengths"] = sorted(len(a) for a in A)
    nm = bacc.null_metrics(null)
    nm["score_hist"] = {str(k / N): sum(1 for r in null if abs(r["s"] - k / N) < 1e-9) for k in range(N + 1)}
    nm["mean_n_attractors"] = sum(len(r["b"]) for r in null) / len(null)
    out = {"substrate": "RBN N=10 K=2 synchronous; behaviour = attractor set; task = best attractor-state match to target",
           "EXPLORATORY": True, "coarse_posthoc": coarse, "design": {"W": W, "D": D, "m": m, "null_n": NN, "parents": [p for p, _ in ps],
                                             "parent_s0": {p: evaluate(g)[1] for p, g in ps}},
           "wall_s": round(time.time() - t0, 1), "walk_wall_s": round(t_run, 1),
           "summary": summ, "null": nm, "per_parent": per}
    with open(os.path.join(HERE, "rbn%s_result%s.json" % ("_coarse" if coarse else "", "_smoke" if smoke else "")), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True, default=str)
    print(json.dumps({k: summ[k] for k in ("median_B_over_G", "median_DOM", "BEHAVIOURAL_POVERTY",
                                            "pooled_neutral_genotypes", "pooled_neutral_behaviours")}), out["wall_s"])


if __name__ == "__main__":
    main()
