"""TAPE -- the WTP-05 stateful developmental organism (PREREG_WTP05 s3).

Three stores:
  WORKING STATE  z: S slots x W floats per episode (S <= 8, W = 8, so <= 64 floats). Reset to 0 at every
                 episode start. Slots persist across steps unless a WRITE node overwrites them.
  LONG-TERM MEM  parameter tensors of CONST / LIN / BILIN nodes. BILIN is dense W x W or rank-1 (u v^T).
                 Fixed in life unless the node is plastic and plasticity is ON.
  PROGRAM GRAPH  a typed DAG of nodes evaluated in list order at every step, plus a library of MODULES
                 (pure sub-graphs with 1-2 input ports) invoked by CALL nodes.

All values are (K, W) arrays: K episodes run in parallel (vectorised). Ops:
  OBS            current observation
  READ s         slot s of the working state (value at the start of the step)
  IN i           (modules only) input port i
  CONST v        parameter vector v (W)
  CH a i         channel i of a, broadcast to all W
  ADD a b, MUL a b, SIGN a (x >= 0 -> +1 else -1)
  SEL g a b      elementwise where(g >= 0, a, b)            (gate / select / branch)
  LIN a M        a @ M.T                                     (factor lookup / memory read)
  DOT a b        sum(a * b) broadcast                         (contraction)
  BILIN a b M    a^T M b broadcast                            (tensor contraction)
  PERM a p       a[:, p]                                      (small mode permutation)
  WRITE a s      sink: next z[s] = a
  ACT a          sink: action = sign(a[:, 0])
  CALL m a b     output of module m on ports (a, b)

Lifetime (one evaluation): L blocks of K episodes. With plasticity ON, every plastic parameter theta is used
as theta + sigma * eps_k in episode k (antithetic pairs), and after the block
  theta = clip(theta + eta * sum_k z(r_k) eps_k / (K sigma), -1, 1),
where z(r) is the block-standardised episode reward. Updates happen only BETWEEN blocks, so an episode can
never carry history in its parameters. The working state is the only within-episode memory.
"""
import copy
import hashlib
import json

import numpy as np

W = 8
S_MAX = 8
N_MAX = 32          # main-graph nodes
M_MAX = 4           # modules
MOD_MAX = 10        # nodes per module
OPS = ("OBS", "READ", "CONST", "CH", "ADD", "MUL", "SIGN", "SEL", "LIN", "DOT", "BILIN", "PERM", "WRITE", "ACT", "CALL")
ARITY = dict(OBS=0, READ=0, IN=0, CONST=0, CH=1, ADD=2, MUL=2, SIGN=1, SEL=3, LIN=1, DOT=2, BILIN=2, PERM=1, WRITE=1,
             ACT=1, CALL=2)
PARAM_OPS = ("CONST", "LIN", "BILIN")
SINKS = ("WRITE", "ACT")
PLASTIC_BOUND = 1.0  # lifetime-plastic parameters are clipped to [-1, 1] after every update (bounded synapses)


# ------------------------------------------------------------------ genome helpers

def node(op, *inputs, **kw):
    return dict(op=op, inp=list(inputs), **kw)


def genome(nodes, S=4, modules=None, eta=0.0, sigma=0.0):
    return dict(S=int(S), nodes=nodes, modules=modules or [], eta=float(eta), sigma=float(sigma))


def ghash(g):
    def enc(x):
        if isinstance(x, np.ndarray):
            return np.round(x, 6).tolist()
        raise TypeError
    return hashlib.sha256(json.dumps(g, sort_keys=True, default=enc).encode()).hexdigest()[:16]


def n_nodes(g):
    return len(g["nodes"]) + sum(len(m["nodes"]) for m in g["modules"])


def n_params(g):
    tot = 0
    for nd in g["nodes"] + [x for m in g["modules"] for x in m["nodes"]]:
        for k in ("v", "M", "u", "w"):
            if k in nd:
                tot += np.asarray(nd[k]).size
    return tot


def plastic_keys(g, frozen_modules=True):
    """-> [(where, idx, key)] where where = -1 for main graph else module index."""
    out = []
    for i, nd in enumerate(g["nodes"]):
        if nd.get("plastic") and nd["op"] in PARAM_OPS:
            out += [(-1, i, k) for k in ("v", "M", "u", "w") if k in nd]
    for mi, m in enumerate(g["modules"]):
        if frozen_modules and m.get("frozen"):
            continue
        for i, nd in enumerate(m["nodes"]):
            if nd.get("plastic") and nd["op"] in PARAM_OPS:
                out += [(mi, i, k) for k in ("v", "M", "u", "w") if k in nd]
    return out


# ------------------------------------------------------------------ interpreter

def _bilin_mat(nd, P):
    if "M" in nd:
        return P.get("M", nd["M"])
    u, w = P.get("u", nd["u"]), P.get("w", nd["w"])
    if u.ndim == 1:
        return np.outer(u, w)
    return u[:, :, None] * w[:, None, :]


def _eval_graph(nodes, vals_in, obs, z, modules, pmap, mod_pmaps, K, depth=0):
    """Evaluate one graph for one step. vals_in: port values for modules. Returns (vals, writes, act)."""
    vals = [None] * len(nodes)
    writes, act = {}, None
    for i, nd in enumerate(nodes):
        op = nd["op"]
        a = [vals[j] for j in nd["inp"]]
        P = pmap.get(i, {})
        if op == "OBS":
            v = obs
        elif op == "READ":
            v = z[:, nd["s"]] if nd["s"] < z.shape[1] else np.zeros((K, W))
        elif op == "IN":
            v = vals_in[nd["port"]]
        elif op == "CONST":
            c = P.get("v", nd["v"])
            v = np.broadcast_to(c, (K, W))
        elif op == "CH":
            v = np.broadcast_to(a[0][:, nd["i"]:nd["i"] + 1], (K, W))
        elif op == "ADD":
            v = a[0] + a[1]
        elif op == "MUL":
            v = a[0] * a[1]
        elif op == "SIGN":
            v = np.where(a[0] >= 0, 1.0, -1.0)
        elif op == "SEL":
            v = np.where(a[0] >= 0, a[1], a[2])
        elif op == "LIN":
            M = P.get("M", nd["M"])
            v = a[0] @ M.T if M.ndim == 2 else np.einsum("kj,kij->ki", a[0], M)
        elif op == "DOT":
            v = np.broadcast_to((a[0] * a[1]).sum(1, keepdims=True), (K, W))
        elif op == "BILIN":
            M = _bilin_mat(nd, P)
            s = np.einsum("ki,ij,kj->k", a[0], M, a[1]) if M.ndim == 2 else np.einsum("ki,kij,kj->k", a[0], M, a[1])
            v = np.broadcast_to(s[:, None], (K, W))
        elif op == "PERM":
            v = a[0][:, nd["p"]]
        elif op == "WRITE":
            v = np.clip(np.nan_to_num(a[0]), -1e3, 1e3)        # state is bounded: clip at the write
            writes[nd["s"]] = v
        elif op == "ACT":
            act = np.nan_to_num(a[0][:, 0])
            v = a[0]
        elif op == "CALL":
            m = nd["m"]
            if depth > 2 or m >= len(modules):
                v = np.zeros((K, W))
            else:
                mv, _, _ = _eval_graph(modules[m]["nodes"], a, obs, z, modules, mod_pmaps.get(m, {}), mod_pmaps, K, depth + 1)
                v = mv[modules[m]["out"]]
        else:
            raise ValueError(op)
        vals[i] = v
    return vals, writes, act


def run_block(g, obs, rng=None, eps_scale=None, pmap=None, mod_pmaps=None, record=None, ws_reset=False):
    """Run K episodes (obs: K x T x W). Returns actions (K x T). `record` (dict) receives the working state at
    each step if given (z_before: K x T x S x W)."""
    K, T, _ = obs.shape
    S = g["S"]
    z = np.zeros((K, S, W))
    acts = np.zeros((K, T))
    pmap = pmap or {}
    mod_pmaps = mod_pmaps or {}
    if record is not None:
        record["z"] = np.zeros((K, T, S, W))
    with np.errstate(all="ignore"):
        return _run(g, obs, K, T, S, z, acts, pmap, mod_pmaps, record, ws_reset)


def _live(nodes, roots):
    live, stack = set(), list(roots)
    while stack:
        i = stack.pop()
        if i in live:
            continue
        live.add(i)
        stack.extend(nodes[i]["inp"])
    return live


def _compile(nodes, modules, pmap, mod_pmaps, K, depth=0, out=None):
    """-> list of (i, fn, inputs) for live nodes only; fn(args, obs, z, ports) -> value; plus sink lists."""
    roots = [i for i, nd in enumerate(nodes) if nd["op"] in ("WRITE", "ACT")] if out is None else [out]
    live = _live(nodes, roots)
    prog, writes, act = [], [], None
    for i, nd in enumerate(nodes):
        if i not in live:
            continue
        op, P = nd["op"], pmap.get(i, {})
        if op == "OBS":
            fn = lambda a, obs, z, ports: obs
        elif op == "READ":
            s_ = nd["s"]
            fn = (lambda a, obs, z, ports, s_=s_: z[:, s_]) if s_ < S_MAX else (lambda a, obs, z, ports: np.zeros((K, W)))
            fn = (lambda a, obs, z, ports, s_=s_: z[:, s_] if s_ < z.shape[1] else np.zeros((K, W)))
        elif op == "IN":
            p_ = nd["port"]
            fn = lambda a, obs, z, ports, p_=p_: ports[p_]
        elif op == "CONST":
            c = np.broadcast_to(P.get("v", nd["v"]), (K, W))
            fn = lambda a, obs, z, ports, c=c: c
        elif op == "CH":
            ch = nd["i"]
            fn = lambda a, obs, z, ports, ch=ch: np.broadcast_to(a[0][:, ch:ch + 1], (K, W))
        elif op == "ADD":
            fn = lambda a, obs, z, ports: a[0] + a[1]
        elif op == "MUL":
            fn = lambda a, obs, z, ports: a[0] * a[1]
        elif op == "SIGN":
            fn = lambda a, obs, z, ports: np.where(a[0] >= 0, 1.0, -1.0)
        elif op == "SEL":
            fn = lambda a, obs, z, ports: np.where(a[0] >= 0, a[1], a[2])
        elif op == "LIN":
            M = P.get("M", nd["M"])
            fn = (lambda a, obs, z, ports, Mt=M.T: a[0] @ Mt) if M.ndim == 2 else \
                (lambda a, obs, z, ports, M=M: np.einsum("kj,kij->ki", a[0], M))
        elif op == "DOT":
            fn = lambda a, obs, z, ports: np.broadcast_to((a[0] * a[1]).sum(1, keepdims=True), (K, W))
        elif op == "BILIN":
            M = _bilin_mat(nd, P)
            if M.ndim == 2:
                fn = lambda a, obs, z, ports, M=M: np.broadcast_to(((a[0] @ M) * a[1]).sum(1, keepdims=True), (K, W))
            else:
                fn = lambda a, obs, z, ports, M=M: np.broadcast_to(np.einsum("ki,kij,kj->k", a[0], M, a[1])[:, None], (K, W))
        elif op == "PERM":
            pp = np.asarray(nd["p"])
            fn = lambda a, obs, z, ports, pp=pp: a[0][:, pp]
        elif op == "WRITE":
            fn = lambda a, obs, z, ports: np.clip(np.nan_to_num(a[0]), -1e3, 1e3)
            writes.append((i, nd["s"]))
        elif op == "ACT":
            fn = lambda a, obs, z, ports: a[0]
            act = i
        elif op == "CALL":
            m = nd["m"]
            if depth > 2 or m >= len(modules):
                zero = np.zeros((K, W))
                fn = lambda a, obs, z, ports, zero=zero: zero
            else:
                mod = modules[m]
                sub, _, _ = _compile(mod["nodes"], modules, mod_pmaps.get(m, {}), mod_pmaps, K, depth + 1, out=mod["out"])
                fn = lambda a, obs, z, ports, sub=sub, o=mod["out"]: _exec(sub, obs, z, a)[o]
        else:
            raise ValueError(op)
        prog.append((i, fn, nd["inp"]))
    return prog, writes, act


def _exec(prog, obs, z, ports):
    vals = {}
    for i, fn, inp in prog:
        vals[i] = fn([vals[j] for j in inp], obs, z, ports)
    return vals


def _run(g, obs, K, T, S, z, acts, pmap, mod_pmaps, record, ws_reset):
    prog, writes, act = _compile(g["nodes"], g["modules"], pmap, mod_pmaps, K)
    for t in range(T):
        if ws_reset:
            z = np.zeros((K, S, W))
        if record is not None:
            record["z"][:, t] = z
        vals = _exec(prog, obs[:, t], z, None)
        if writes:
            z = z.copy()
            for i, s in writes:
                if s < S:
                    z[:, s] = vals[i]
        if act is not None:
            a = np.nan_to_num(vals[act][:, 0])
            acts[:, t] = np.where(a >= 0, 1.0, -1.0)
        else:
            acts[:, t] = 1.0
    return acts


def _param(g, where, i, k):
    nodes = g["nodes"] if where < 0 else g["modules"][where]["nodes"]
    return nodes[i][k]


def _set_param(g, where, i, k, val):
    nodes = g["nodes"] if where < 0 else g["modules"][where]["nodes"]
    nodes[i][k] = val


def lifetime(g, world, rng, plasticity=True, L=None, K=None, history_shuffle=False, ws_reset=False,
             record_last=False):
    """One lifetime of organism g in world. Returns a dict of per-role accuracy/reward and per-block stats.
    The genome is not modified; learned parameters are returned in out['learned'] (copy of g)."""
    L = L or world.L
    K = K or world.K
    g = copy.deepcopy(g)
    keys = plastic_keys(g) if (plasticity and g.get("eta", 0) > 0 and g.get("sigma", 0) > 0) else []
    roles = {}
    blocks = []
    tot_r, tot_w = 0.0, 0.0
    rec = None
    for b in range(L):
        ep = world.block(K, rng, b)
        pmap, mod_pmaps, eps = {}, {}, []
        if keys:
            half = K // 2
            for (where, i, k) in keys:
                th = np.asarray(_param(g, where, i, k), float)
                e = rng.standard_normal((half,) + th.shape)
                e = np.concatenate([e, -e], 0)
                eps.append(e)
                pv = th[None] + g["sigma"] * e
                if where < 0:
                    pmap.setdefault(i, {})[k] = pv
                else:
                    mod_pmaps.setdefault(where, {}).setdefault(i, {})[k] = pv
        record = {} if (record_last and b == L - 1) else None
        acts = run_block(g, ep["obs"], pmap=pmap, mod_pmaps=mod_pmaps, record=record, ws_reset=ws_reset)
        if record is not None:
            rec = dict(z=record["z"], ep=ep, acts=acts)
        correct = (acts == ep["tgt"]) & (ep["tgt"] != 0)
        r_ep = (ep["wt"] * correct).sum(1)
        tot_r += float(r_ep.sum())
        tot_w += float(ep["wt"].sum())
        for role in np.unique(ep["role"]):
            if role == 0:
                continue
            m = ep["role"] == role
            c = roles.setdefault(int(role), [0, 0])
            c[0] += int(correct[m].sum())
            c[1] += int(m.sum())
        blocks.append(dict(r=float(r_ep.mean()),
                           acc={int(rl): float(correct[ep["role"] == rl].mean()) for rl in np.unique(ep["role"]) if rl != 0}))
        if keys:
            sig = r_ep.std()
            rr = r_ep if not history_shuffle else rng.permutation(r_ep)
            zr = (rr - rr.mean()) / sig if sig > 1e-9 else np.zeros(K)
            for (where, i, k), e in zip(keys, eps):
                th = np.asarray(_param(g, where, i, k), float)
                grad = np.tensordot(zr, e, axes=(0, 0)) / (K * g["sigma"])
                _set_param(g, where, i, k, np.clip(th + g["eta"] * grad, -PLASTIC_BOUND, PLASTIC_BOUND))
    out = dict(R=tot_r / max(tot_w, 1e-9), roles={k: v[0] / max(1, v[1]) for k, v in roles.items()},
               role_n={k: v[1] for k, v in roles.items()}, blocks=blocks, learned=g)
    if rec is not None:
        out["record"] = rec
    return out
