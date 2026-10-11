"""WTP-05 variation operators (PREREG_WTP05 s3.3).

BASELINE (every arm): add node, delete node, rewire an input, perturb a parameter / channel / slot / permutation,
change op (same arity), change the number of working-state slots.
PLASTICITY arm adds: toggle a node's plastic flag, perturb eta / sigma. Without it eta = sigma = 0 always.
PROMOTION arm adds (directive s8):
  DUP      duplicate a node's ancestor cone inline, then reconnect one typed port of the copy
  PROMOTE  reify a node's ancestor cone (<= 2 external inputs, <= MOD_MAX nodes) into a library module and
           replace it by CALL; promotion costs fitness (score.py), it is never automatic
  CALL     insert a call to an existing module with random port connections
  FREEZE   freeze / unfreeze a module (frozen: no mutation, no plasticity, half the definition cost)
"""
import copy

import numpy as np

from .tape import W, S_MAX, N_MAX, M_MAX, MOD_MAX, ARITY, PARAM_OPS, node, genome

NEW_OPS = ("READ", "CONST", "CH", "ADD", "MUL", "SIGN", "SEL", "LIN", "DOT", "BILIN", "PERM", "WRITE")
NEW_W = np.array([2, 2, 3, 2, 2, 1, 3, 1, 1, 1, 0.5, 2], float)
NEW_W /= NEW_W.sum()


def _params(op, rng, S):
    if op == "READ" or op == "WRITE":
        return dict(s=int(rng.integers(S)))
    if op == "CONST":
        return dict(v=np.round(rng.normal(0, 0.7, W), 3))
    if op == "CH":
        return dict(i=int(rng.integers(W)))
    if op == "LIN":
        return dict(M=np.round(rng.normal(0, 1 / np.sqrt(W), (W, W)), 3))
    if op == "BILIN":
        if rng.random() < 0.5:
            return dict(u=np.round(rng.normal(0, 1, W), 3), w=np.round(rng.normal(0, 1, W), 3))
        return dict(M=np.round(rng.normal(0, 1 / np.sqrt(W), (W, W)), 3))
    if op == "PERM":
        return dict(p=rng.permutation(W).tolist())
    return {}


def random_node(op, pos, rng, S, n_modules=0):
    k = ARITY[op]
    inp = [int(rng.integers(pos)) for _ in range(k)]
    nd = node(op, *inp, **_params(op, rng, S))
    if op == "CALL":
        nd["m"] = int(rng.integers(max(1, n_modules)))
    return nd


def random_genome(rng, S=2):
    nodes = [node("OBS"), node("READ", s=0)]
    for _ in range(int(rng.integers(2, 6))):
        op = str(rng.choice(NEW_OPS, p=NEW_W))
        nodes.append(random_node(op, len(nodes), rng, S))
    nodes.append(node("ACT", len(nodes) - 1))
    return genome(nodes, S=S)


def _shift(nodes, pos, delta, start):
    for nd in nodes[start:]:
        nd["inp"] = [j + delta if j >= pos else j for j in nd["inp"]]


def add_node(g, rng, n_modules=0, op=None):
    if len(g["nodes"]) >= N_MAX:
        return False
    pos = int(rng.integers(1, len(g["nodes"]) + 1))
    op = op or str(rng.choice(NEW_OPS, p=NEW_W))
    nd = random_node(op, pos, rng, g["S"], n_modules)
    _shift(g["nodes"], pos, 1, pos)
    g["nodes"].insert(pos, nd)
    later = [i for i in range(pos + 1, len(g["nodes"])) if g["nodes"][i]["inp"]]
    if later and rng.random() < 0.7:
        i = int(rng.choice(later))
        g["nodes"][i]["inp"][int(rng.integers(len(g["nodes"][i]["inp"])))] = pos
    return True


def delete_node(g, rng):
    cand = [i for i in range(1, len(g["nodes"])) if g["nodes"][i]["op"] != "ACT"]
    if not cand:
        return False
    i = int(rng.choice(cand))
    rep = g["nodes"][i]["inp"][0] if g["nodes"][i]["inp"] else 0
    for nd in g["nodes"][i + 1:]:
        nd["inp"] = [rep if j == i else (j - 1 if j > i else j) for j in nd["inp"]]
    del g["nodes"][i]
    return True


def rewire(g, rng):
    cand = [i for i, nd in enumerate(g["nodes"]) if nd["inp"]]
    if not cand:
        return False
    i = int(rng.choice(cand))
    g["nodes"][i]["inp"][int(rng.integers(len(g["nodes"][i]["inp"])))] = int(rng.integers(i))
    return True


def perturb(nodes, rng, S, n_modules=0):
    cand = [i for i, nd in enumerate(nodes) if nd["op"] in PARAM_OPS + ("CH", "READ", "WRITE", "PERM", "CALL")]
    if not cand:
        return False
    nd = nodes[int(rng.choice(cand))]
    op = nd["op"]
    if op in ("READ", "WRITE"):
        nd["s"] = int(rng.integers(S))
    elif op == "CH":
        nd["i"] = int(rng.integers(W))
    elif op == "PERM":
        a, b = rng.choice(W, 2, replace=False)
        p = list(nd["p"])
        p[a], p[b] = p[b], p[a]
        nd["p"] = p
    elif op == "CALL":
        nd["m"] = int(rng.integers(max(1, n_modules)))
    else:
        keys = [k for k in ("v", "M", "u", "w") if k in nd]
        k = str(rng.choice(keys))
        x = np.array(nd[k], float)
        if rng.random() < 0.5:
            idx = tuple(int(rng.integers(d)) for d in x.shape)
            x[idx] += rng.normal(0, 0.5)
        else:
            x = x + rng.normal(0, 0.15, x.shape)
        if rng.random() < 0.1:                       # occasional snap to {-1, 0, 1}
            x = np.round(x)
        nd[k] = np.round(x, 3)
    return True


def change_op(g, rng):
    cand = [i for i in range(1, len(g["nodes"])) if g["nodes"][i]["op"] not in ("ACT",)]
    if not cand:
        return False
    i = int(rng.choice(cand))
    old = g["nodes"][i]
    same = [o for o in NEW_OPS if ARITY[o] == ARITY[old["op"]] and o != old["op"]]
    if not same:
        return False
    op = str(rng.choice(same))
    nd = node(op, *old["inp"], **_params(op, rng, g["S"]))
    g["nodes"][i] = nd
    return True


def change_S(g, rng):
    g["S"] = int(np.clip(g["S"] + (1 if rng.random() < 0.5 else -1), 1, S_MAX))
    return True


# ------------------------------------------------------------------ plasticity arm

def plastic_toggle(g, rng):
    cand = [nd for nd in g["nodes"] if nd["op"] in PARAM_OPS]
    cand += [nd for m in g["modules"] if not m.get("frozen") for nd in m["nodes"] if nd["op"] in PARAM_OPS]
    if not cand:
        return False
    nd = cand[int(rng.integers(len(cand)))]
    nd["plastic"] = not nd.get("plastic", False)
    return True


def plastic_rates(g, rng):
    g["eta"] = float(np.clip((g["eta"] or 0.3) * np.exp(rng.normal(0, 0.4)), 0.01, 5.0))
    g["sigma"] = float(np.clip((g["sigma"] or 0.3) * np.exp(rng.normal(0, 0.4)), 0.02, 2.0))
    return True


# ------------------------------------------------------------------ promotion arm

def _cone(nodes, x, depth):
    """Ancestors of x within depth (excluding OBS / READ, which stay outside as ports)."""
    cone, frontier = {x}, {x}
    for _ in range(depth):
        nxt = set()
        for i in frontier:
            for j in nodes[i]["inp"]:
                if nodes[j]["op"] not in ("OBS", "READ", "CALL") and j not in cone:
                    nxt.add(j)
        cone |= nxt
        frontier = nxt
    return sorted(cone)


def _pure(nodes, idx):
    return all(nodes[i]["op"] not in ("OBS", "READ", "WRITE", "ACT", "CALL") for i in idx)


def dup(g, rng):
    cand = [i for i, nd in enumerate(g["nodes"]) if nd["op"] not in ("OBS", "READ", "WRITE", "ACT")]
    if not cand or len(g["nodes"]) >= N_MAX - 2:
        return False
    x = int(rng.choice(cand))
    cone = _cone(g["nodes"], x, int(rng.integers(1, 4)))
    if len(g["nodes"]) + len(cone) > N_MAX:
        return False
    base = len(g["nodes"]) - 1 if g["nodes"][-1]["op"] == "ACT" else len(g["nodes"])
    remap = {}
    new = []
    for k, i in enumerate(cone):
        nd = copy.deepcopy(g["nodes"][i])
        nd["inp"] = [remap.get(j, j) for j in nd["inp"]]
        remap[i] = base + k
        new.append(nd)
    ext = [(k, p) for k, nd in enumerate(new) for p, j in enumerate(nd["inp"]) if j < base and j not in remap.values()]
    if ext:                                           # reconnect one typed port of the copy
        k, p = ext[int(rng.integers(len(ext)))]
        new[k]["inp"][p] = int(rng.integers(base))
    _shift(g["nodes"], base, len(new), base)
    g["nodes"][base:base] = new
    return True


def promote(g, rng):
    if len(g["modules"]) >= M_MAX:
        return False
    cand = [i for i, nd in enumerate(g["nodes"]) if nd["op"] not in ("OBS", "READ", "WRITE", "ACT", "CALL")]
    if not cand:
        return False
    x = int(rng.choice(cand))
    for depth in (3, 2, 1, 0):
        cone = _cone(g["nodes"], x, depth)
        if len(cone) > MOD_MAX - 2 or not _pure(g["nodes"], cone):
            continue
        ext = sorted({j for i in cone for j in g["nodes"][i]["inp"] if j not in cone})
        if 1 <= len(ext) <= 2:
            break
    else:
        return False
    mnodes = [node("IN", port=p) for p in range(len(ext))]
    remap = {j: p for p, j in enumerate(ext)}
    for i in cone:
        nd = copy.deepcopy(g["nodes"][i])
        nd["inp"] = [remap[j] for j in nd["inp"]]
        remap[i] = len(mnodes)
        mnodes.append(nd)
    g["modules"].append(dict(nodes=mnodes, out=remap[x], frozen=False, n_in=len(ext)))
    call = node("CALL", ext[0], ext[-1], m=len(g["modules"]) - 1)
    g["nodes"][x] = call
    # garbage-collect cone nodes no longer referenced
    for i in sorted(set(cone) - {x}, reverse=True):
        if not any(i in nd["inp"] for k, nd in enumerate(g["nodes"]) if k != i):
            for nd in g["nodes"][i + 1:]:
                nd["inp"] = [j - 1 if j > i else j for j in nd["inp"]]
            del g["nodes"][i]
    return True


def call_insert(g, rng):
    if not g["modules"]:
        return False
    return add_node(g, rng, n_modules=len(g["modules"]), op="CALL")


def freeze(g, rng):
    if not g["modules"]:
        return False
    m = g["modules"][int(rng.integers(len(g["modules"])))]
    m["frozen"] = not m.get("frozen", False)
    return True


def module_perturb(g, rng):
    live = [m for m in g["modules"] if not m.get("frozen")]
    if not live:
        return False
    m = live[int(rng.integers(len(live)))]
    return perturb(m["nodes"], rng, g["S"])


def mutate(g, rng, promotion=False, plasticity=False):
    g = copy.deepcopy(g)
    ops = [(add_node, 3), (delete_node, 2), (rewire, 3), (lambda g, r: perturb(g["nodes"], r, g["S"], len(g["modules"])), 4),
           (change_op, 1), (change_S, 0.5)]
    if plasticity:
        ops += [(plastic_toggle, 1), (plastic_rates, 1)]
    if promotion:
        ops += [(dup, 1), (promote, 1), (call_insert, 1.5), (freeze, 0.3), (module_perturb, 1)]
    fs, ws = zip(*ops)
    ws = np.array(ws, float) / sum(ws)
    n = 1 + int(rng.poisson(0.7))
    applied = []
    for _ in range(n):
        k = int(rng.choice(len(fs), p=ws))
        if fs[k](g, rng):
            applied.append(getattr(fs[k], "__name__", "perturb"))
    if not plasticity:
        g["eta"] = g["sigma"] = 0.0
    if not promotion and g["modules"]:
        raise AssertionError("modules without the promotion arm")
    return g, applied
