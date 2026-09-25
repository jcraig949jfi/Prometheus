"""WTP small world executor (directive s55). One life of a world genome:
build (with preflight legality), run, measure. Deterministic given
(genome, seed); every run returns digests for replay checks.

Controls built into the executor (PREREG_WTP01 s4): shuffle_latents
(field values permuted over cells), reskin (index labels permuted within
every mode), memory transplant (start with a given memory object),
ablations (freeze learning, no marks, no rollouts)."""
import copy
import hashlib
import time

import numpy as np

from .registry import REG
from .organism import make_memory, convert, CONVERTIBLE


class Illegal(Exception):
    pass


# ------------------------------------------------------------------ field

def _std(x):
    s = x.std()
    return (x - x.mean()) / s if s > 1e-12 else x


def base_field(gen, dims, rank, rng):
    D = len(dims)
    if gen == "tt":
        r = [1] + [rank] * (D - 1) + [1]
        t = rng.normal(size=(1, dims[0], r[1]))
        for k in range(1, D):
            t = np.tensordot(t, rng.normal(size=(r[k], dims[k], r[k + 1])), axes=([-1], [0]))
        return t.reshape(dims)
    if gen == "cp":
        out = np.zeros(dims)
        for _ in range(rank):
            t = rng.normal(size=dims[0])
            for n in dims[1:]:
                t = np.multiply.outer(t, rng.normal(size=n))
            out += t
        return out
    if gen == "lowrank":
        s = max(1, D // 2)
        a, b = int(np.prod(dims[:s])), int(np.prod(dims[s:]))
        return (rng.normal(size=(a, rank)) @ rng.normal(size=(rank, b))).reshape(dims)
    if gen == "pairwise":  # graphical-model-like: sum of 2-mode interaction tables
        out = np.zeros(dims)
        for _ in range(max(1, rank)):
            i, j = rng.choice(D, 2, replace=False)
            W = rng.normal(size=(dims[i], dims[j]))
            sh = [1] * D
            sh[i], sh[j] = dims[i], dims[j]
            out = out + (W if i < j else W.T).reshape(sh)
        return out
    if gen == "sparse":
        out = np.zeros(int(np.prod(dims)))
        idx = rng.choice(out.size, size=max(2, out.size // 50), replace=False)
        out[idx] = rng.normal(0, 5, size=len(idx))
        return out.reshape(dims)
    if gen == "spectral":
        C = rng.normal(size=[min(n, 3) for n in dims])
        out = C
        for m, n in enumerate(dims):
            B = np.array([[np.cos(np.pi * f * (i + 0.5) / n) for i in range(n)] for f in range(C.shape[m])])
            out = np.moveaxis(np.tensordot(np.moveaxis(out, m, -1), B, axes=([-1], [0])), -1, m)
        return out
    if gen == "sum":
        g1, g2 = rng.choice(["tt", "cp", "lowrank", "pairwise", "spectral", "random"], 2, replace=False)
        return _std(base_field(g1, dims, rank, rng)) + _std(base_field(g2, dims, rank, rng))
    return rng.normal(size=dims)


def build_field(sub, rng):
    x = base_field(sub["gen"], sub["dims"], sub["rank"], rng)
    for a in sub["chain"]:
        x = REG[a["op"]].fn(x, a["p"], rng)
        if not np.all(np.isfinite(x)) or x.size < 16 or x.size > 4096 or x.ndim < 2:
            raise Illegal(f"field after {a['op']}: shape {x.shape}, finite={np.all(np.isfinite(x))}")
    x = _std(np.real(x))
    if x.std() < 1e-6:
        raise Illegal("constant field")
    r = x
    for a in sub.get("reward_chain", []):
        r = REG[a["op"]].fn(r, a["p"], rng)
    if r.shape != x.shape or not np.all(np.isfinite(r)):
        r = x
    return x, _std(np.real(r))


# ------------------------------------------------------------------ graph

def build_graph(geo, dims, x, rng):
    cells = int(np.prod(dims))
    kind = geo["kind"]
    k = max(1, geo["k"])
    if kind == "tensor_index":
        N = cells
        node_cell = np.arange(N)
        addr = np.array(np.unravel_index(np.arange(N), dims)).T
        strides = np.array([int(np.prod(dims[m + 1:])) for m in range(len(dims))])
        adj = []
        for v in range(N):
            nb = [v + (val - addr[v, m]) * strides[m] for m in range(len(dims)) for val in range(dims[m]) if val != addr[v, m]]
            adj.append(set(int(u) for u in rng.choice(nb, size=min(k, len(nb)), replace=False)))
    else:
        N = int(min(geo["n_nodes"], cells))
        if geo["map"] == "sorted":
            node_cell = np.argsort(x.reshape(-1))[np.linspace(0, cells - 1, N).astype(int)]
        elif geo["map"] == "blocked":
            node_cell = np.linspace(0, cells - 1, N).astype(int)
        else:
            node_cell = rng.choice(cells, size=N, replace=False)
        adj = [set() for _ in range(N)]

        def und(a, b):
            if a != b:
                adj[a].add(int(b))
                adj[b].add(int(a))
        if kind in ("ring", "small_world", "wormholes"):
            for v in range(N):
                for j in range(1, k // 2 + 1):
                    und(v, (v + j) % N)
            if kind == "small_world":
                for v in range(N):
                    if rng.random() < geo["p"]:
                        und(v, int(rng.integers(N)))
            if kind == "wormholes":
                for _ in range(k):
                    und(int(rng.integers(N)), int(rng.integers(N)))
        elif kind == "torus":
            w = int(np.sqrt(N))
            for v in range(w * w):
                i, j = divmod(v, w)
                und(v, ((i + 1) % w) * w + j)
                und(v, i * w + (j + 1) % w)
        elif kind == "scale_free":
            m = max(1, k // 2)
            deg = np.ones(N)
            for v in range(1, N):
                targets = rng.choice(v, size=min(m, v), replace=False, p=deg[:v] / deg[:v].sum())
                for u in targets:
                    und(v, int(u))
                    deg[u] += 1
                    deg[v] += 1
        elif kind == "random_geometric":
            P = rng.random((N, 2))
            r = np.sqrt(k / (np.pi * N))
            d = ((P[:, None] - P[None]) ** 2).sum(-1)
            for a, b in zip(*np.nonzero(np.triu(d < r * r, 1))):
                und(int(a), int(b))
        elif kind == "erdos":
            for _ in range(N * k // 2):
                und(int(rng.integers(N)), int(rng.integers(N)))
        elif kind == "modular":
            B = max(2, k)
            blk = rng.integers(B, size=N)
            for _ in range(N * 3):
                a, b = rng.integers(N, size=2)
                if blk[a] == blk[b] or rng.random() < geo["p"] * 0.2:
                    und(int(a), int(b))
        elif kind == "tree":
            for v in range(1, N):
                und(v, (v - 1) // max(2, k))
        elif kind == "dag":
            for v in range(N - 1):
                for u in rng.integers(v + 1, N, size=min(k, N - v - 1)):
                    adj[v].add(int(u))
        elif kind == "spectral_roads":  # a singular vector becomes a road network (s8)
            M = x.reshape(x.shape[0], -1)
            U, s, Vt = np.linalg.svd(M, full_matrices=False)
            emb = U[:, 0][np.unravel_index(node_cell, x.shape)[0]] + 1e-3 * rng.normal(size=N)
            order = np.argsort(emb)
            for i in range(N):
                for j in range(1, k // 2 + 1):
                    if i + j < N:
                        und(int(order[i]), int(order[i + j]))
        # directionality
        for v in range(N):
            for u in list(adj[v]):
                if u > v and v in adj[u] and rng.random() < geo["directed"]:
                    if rng.random() < 0.5:
                        adj[v].discard(u)
                    else:
                        adj[u].discard(v)
    for v in range(N):
        if not adj[v]:
            adj[v].add(int(rng.integers(N)))
    return adj, node_cell


def reachable(adj, start):
    seen, stack = {start}, [start]
    while stack:
        v = stack.pop()
        for u in adj[v]:
            if u not in seen:
                seen.add(u)
                stack.append(u)
    return len(seen)


# ------------------------------------------------------------------ run

def _digest(*arrays):
    h = hashlib.sha256()
    for a in arrays:
        h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()[:16]


def _nlmse(pred, y):
    mse = float(np.mean((np.nan_to_num(pred, nan=0.0, posinf=1e6, neginf=-1e6) - y) ** 2))
    return float(-np.log10(max(mse / (y.var() + 1e-12), 1e-12)))


class Org:
    def __init__(self, i, mem, energy, node):
        self.i, self.mem, self.energy, self.node = i, mem, energy, node
        self.alive = True
        self.gain = self.cost = 0.0
        self.flops = 0
        self.buf, self.queue = [], []
        self.visited = set()
        self.marks = {}
        self.probes = self.rollouts = self.conversions = self.writes = 0
        self.harvest_t = []


def run_world(g, seed, *, shuffle_latents=False, reskin=False, transplant=None, freeze=False,
              no_marks=False, no_rollouts=False, record=False, return_memory=False):
    t0 = time.time()
    rng = np.random.default_rng(seed)
    try:
        x, rew = build_field(g["substrate"], rng)
    except Illegal as ex:
        return dict(status="ILLEGAL", reason=str(ex))
    except Exception as ex:
        return dict(status="ILLEGAL", reason=f"{type(ex).__name__}: {ex}")
    dims = list(x.shape)
    if shuffle_latents:
        p = rng.permutation(x.size)
        x, rew = x.reshape(-1)[p].reshape(dims), rew.reshape(-1)[p].reshape(dims)
    if reskin:
        for m in range(len(dims)):
            perm = rng.permutation(dims[m])
            x, rew = np.take(x, perm, axis=m), np.take(rew, perm, axis=m)
    try:
        adj, node_cell = build_graph(g["geometry"], dims, x, rng)
    except Exception as ex:
        return dict(status="ILLEGAL", reason=f"graph: {type(ex).__name__}: {ex}")
    N = len(adj)
    if reachable(adj, 0) < 0.3 * N and reachable(adj, N // 2) < 0.3 * N:
        return dict(status="ILLEGAL", reason="graph mostly unreachable")
    addr = np.array(np.unravel_index(np.arange(x.size), dims)).T
    ir = g["irreversibility"]
    hazard_edges = set()
    for v in range(N):
        for u in adj[v]:
            if rng.random() < ir["hazard_frac"]:
                hazard_edges.add((v, u))
            if rng.random() < ir["oneway"] * 0.5 and v in adj[u] and len(adj[u]) > 1:
                adj[u].discard(v)
    mg = g["memory"]
    B = g["boundary"]
    R, L, C, S = g["resource"], g["learning"], g["credit"], g["search"]
    orgs = []
    try:
        for i in range(B["n_org"]):
            mem = copy.deepcopy(transplant) if (transplant is not None and i == 0) else make_memory(mg["substrate"], dims, mg["cap"], rng)
            orgs.append(Org(i, mem, R["energy0"], int(rng.integers(N))))
    except ValueError as ex:
        return dict(status="ILLEGAL", reason=f"memory: {ex}")
    birth = copy.deepcopy(orgs[0].mem)
    battery = rng.choice(x.size, size=min(128, x.size), replace=False)
    init_digest = _digest(x, np.array(sorted((v, u) for v in range(N) for u in adj[v])))
    shared_marks = {}
    last_harv = np.full(N, -10 ** 9)
    T = g["time"]["lifetime"]
    ck = max(1, T // g["time"]["checkpoints"])
    trace = []
    ev_hash = hashlib.sha256()
    events = [] if record else None
    tr, ob = g["transition"], g["observation"]
    reach0 = reachable(adj, orgs[0].node)
    diverged = False

    def predict(o, cells_idx):
        p = o.mem.predict(addr[cells_idx])
        p = np.nan_to_num(p, nan=0.0, posinf=1e6, neginf=-1e6)
        if B["marks"] != "none" and not no_marks:
            store = shared_marks if B["marks"] == "shared" else o.marks
            for j, c in enumerate(cells_idx):
                if int(c) in store:
                    val, tw = store[int(c)]
                    p[j] = val * (1 - B["mark_decay"]) ** max(0, tt - tw)
        return p

    def observe(o, v):
        c = int(node_cell[v])
        if ob["kind"] == "probe_only":
            return np.zeros(0, int), np.zeros(0)
        a = addr[c]
        if ob["kind"] == "cell":
            cells = np.array([c])
        else:
            m = ob["mode"] % len(dims)
            fib = np.repeat(a[None], dims[m], 0)
            fib[:, m] = np.arange(dims[m])
            cells = np.ravel_multi_index(fib.T, dims)
            if ob["kind"] == "masked":
                cells = rng.choice(cells, size=min(ob["k"], len(cells)), replace=False)
        vals = x.reshape(-1)[cells].copy()
        if ob["kind"] == "marginal":
            vals = np.full(1, vals.mean())
            cells = np.array([c])
        for at in ob["chain"]:
            vals = np.asarray(REG[at["op"]].fn(vals, at["p"], rng), float)
            if vals.shape[0] != len(cells):
                vals = np.resize(vals, len(cells))
        sd = ob["noise_sd"]
        if sd > 0:
            z = {"normal": rng.normal(size=len(vals)), "laplace": rng.laplace(size=len(vals)),
                 "cauchy_clip": np.clip(rng.standard_cauchy(size=len(vals)), -10, 10)}[ob["noise_dist"]]
            vals = vals + sd * z
        return cells, vals

    def learn(o, cells, vals):
        nonlocal diverged
        if freeze or len(cells) == 0:
            return
        y = vals.copy()
        if C["noise"] > 0:
            y = y + rng.normal(0, C["noise"], len(y))
        if C["sign_flip"] > 0:
            y = np.where(rng.random(len(y)) < C["sign_flip"], -y, y)
        if C["radius"] > 0:
            extra_c, extra_y = [], []
            for c, v in zip(cells, y):
                for u in list(adj[int(np.nonzero(node_cell == c)[0][0])])[:C["radius"]] if (node_cell == c).any() else []:
                    extra_c.append(int(node_cell[u]))
                    extra_y.append(v)
            if extra_c:
                cells, y = np.concatenate([cells, extra_c]).astype(int), np.concatenate([y, extra_y])
        o.queue.append((tt + C["delay"], cells, y))
        ready = [q for q in o.queue if q[0] <= tt]
        o.queue = [q for q in o.queue if q[0] > tt]
        for _, cc, yy in ready:
            if L["rule"] == "batch_replay":
                o.buf.extend(zip(cc, yy))
                if len(o.buf) >= L["batch"]:
                    bc = np.array([b[0] for b in o.buf])
                    by = np.array([b[1] for b in o.buf])
                    for _ in range(L["sweeps"]):
                        o.flops += o.mem.learn(addr[bc], by, "nlms", L["lr"])
                    o.buf = []
            else:
                o.flops += o.mem.learn(addr[cc], yy, L["rule"], L["lr"])
                o.buf = (o.buf + list(zip(cc, yy)))[-64:]
            o.mem.quantize(mg["bits"])
            o.cost += R["p_write"] * len(yy)
        ps = o.mem.params()
        if ps and not all(np.all(np.isfinite(a)) for a in ps):
            diverged = True
            for a in ps:
                a[~np.isfinite(a)] = 0.0

    tt = 0
    for tt in range(T):
        # world transition laws
        if tr["drift"] > 0 and tt > 0 and tt % tr["drift_period"] == 0:
            try:
                x2, r2 = build_field(g["substrate"], rng)
                if x2.shape == x.shape:
                    d = tr["drift"]
                    x = np.sqrt(1 - d) * x + np.sqrt(d) * x2
                    rew = np.sqrt(1 - d) * rew + np.sqrt(d) * r2
            except Illegal:
                pass
        if tr["basis_change_period"] and tt > 0 and tt % tr["basis_change_period"] == 0:
            m = int(rng.integers(len(dims)))
            perm = rng.permutation(dims[m])
            x, rew = np.take(x, perm, axis=m), np.take(rew, perm, axis=m)
        if tr["rewire_period"] and tt > 0 and tt % tr["rewire_period"] == 0:
            for v in range(N):
                if rng.random() < tr["rewire_frac"] and adj[v]:
                    adj[v].discard(next(iter(adj[v])))
                    adj[v].add(int(rng.integers(N)))
        if tr["catastrophe_rate"] > 0 and rng.random() < tr["catastrophe_rate"]:
            m = int(rng.integers(len(dims)))
            sl = [slice(None)] * len(dims)
            sl[m] = int(rng.integers(dims[m]))
            x[tuple(sl)] = 0.0
            rew[tuple(sl)] = 0.0
        for o in orgs:
            if not o.alive:
                continue
            v = o.node
            o.visited.add(v)
            cells, vals = observe(o, v)
            learn(o, cells, vals)
            if B["marks"] != "none" and not no_marks and len(cells):
                store = shared_marks if B["marks"] == "shared" else o.marks
                store[int(cells[0])] = (float(vals[0]), tt)
                o.writes += 1
                o.cost += R["p_write"]
            c = int(node_cell[v])
            if tt - last_harv[v] >= R["regrow"]:
                h = R["gain"] * max(0.0, float(rew.reshape(-1)[c]) - R["theta"])
                o.gain += h
                last_harv[v] = tt
                o.harvest_t.append((tt, h))
            if R["query_every"] and tt % R["query_every"] == 0:
                qc = int(rng.integers(x.size))
                if abs(predict(o, np.array([qc]))[0] - x.reshape(-1)[qc]) < R["tol"]:
                    o.gain += R["query_reward"]
                o.cost += R["p_read"]
            nbrs = sorted(adj[v])
            pol = S["policy"]
            if pol == "rollout" and no_rollouts:
                pol = "greedy"
            if pol == "random":
                nxt = int(rng.choice(nbrs))
            else:
                if pol == "probe_greedy":
                    pc = node_cell[nbrs]
                    pv = x.reshape(-1)[pc] + ob["noise_sd"] * rng.normal(size=len(pc))
                    learn(o, pc, pv)
                    o.probes += len(pc)
                    o.cost += R["p_probe"] * len(pc)
                    score = pv
                elif pol == "rollout":
                    r_before = o.rollouts

                    def val(node, depth):
                        o.rollouts += 1
                        base = max(0.0, float(predict(o, np.array([node_cell[node]]))[0]) - R["theta"])
                        if depth <= 1:
                            return base
                        kids = sorted(adj[node])[:4]
                        return base + 0.9 * max(val(u, depth - 1) for u in kids)
                    score = np.array([val(u, S["depth"]) for u in nbrs])
                    o.cost += R["p_rollout"] * (o.rollouts - r_before) * 1e-2
                else:
                    score = predict(o, node_cell[nbrs]) - R["theta"]
                    o.cost += R["p_read"] * len(nbrs)
                if pol == "novelty":
                    score = score + 10.0 * np.array([u not in o.visited for u in nbrs])
                if pol == "softmax":
                    z = np.clip(score / max(S["temp"], 1e-3), -50, 50)
                    pz = np.exp(z - z.max())
                    nxt = int(rng.choice(nbrs, p=pz / pz.sum()))
                elif pol == "eps_greedy" and rng.random() < S["eps"]:
                    nxt = int(rng.choice(nbrs))
                else:
                    nxt = int(nbrs[int(np.argmax(np.asarray(score) + 1e-9 * rng.random(len(nbrs))))])
            if (v, nxt) in hazard_edges:
                o.mem.hazard(ir["hazard"], rng)
            if ir["door_close"] > 0 and rng.random() < ir["door_close"] and len(adj[v]) > 1:
                adj[v].discard(nxt)
            o.cost += R["p_move"] * 0.1
            o.node = nxt
            o.cost += R["metabolism"]
            ev = (tt, o.i, v, nxt, round(o.gain - o.cost, 6))
            ev_hash.update(repr(ev).encode())
            if record:
                events.append(ev)
            fl = o.flops
            o.flops = 0
            o.cost += R["p_compute"] * fl
            o.total_flops = getattr(o, "total_flops", 0) + fl
            if R["energy0"] + o.gain - o.cost <= 0:
                o.alive = False
        # checkpoint
        if tt % ck == 0 or tt == T - 1:
            o0 = orgs[0]
            # representation fluidity: try a costed conversion (s14)
            if mg["fluid"] and tt > 0 and len(o0.buf) >= 16 and o0.alive:
                kind = str(rng.choice([k for k in CONVERTIBLE if k != o0.mem.kind]))
                try:
                    sample = rng.choice(x.size, size=64, replace=False)
                    new, fl = convert(o0.mem, kind, dims, mg["cap"], rng, addr[sample], None)
                    bc = np.array([b[0] for b in o0.buf])
                    by = np.array([b[1] for b in o0.buf])
                    new.learn(addr[bc], by, "nlms", 0.5)
                    if np.mean((new.predict(addr[bc]) - by) ** 2) < np.mean((o0.mem.predict(addr[bc]) - by) ** 2):
                        o0.mem = new
                        o0.conversions += 1
                    o0.cost += R["p_compute"] * fl
                except ValueError:
                    pass
            if mg["forget"] != "none":
                for o in orgs:
                    o.mem.forget(mg["forget"], mg["forget_rate"], rng)
            nl = _nlmse(orgs[0].mem.predict(addr[battery]), x.reshape(-1)[battery])
            trace.append(dict(t=tt, nlmse=nl, rank=orgs[0].mem.eff_rank(), kind=orgs[0].mem.kind,
                              U=R["energy0"] + orgs[0].gain - orgs[0].cost, alive=orgs[0].alive))
        if not any(o.alive for o in orgs):
            break
    o0 = orgs[0]
    yb = x.reshape(-1)[battery]
    nl_end = _nlmse(o0.mem.predict(addr[battery]), yb)
    nl_birth = _nlmse(birth.predict(addr[battery]), yb)
    nl_marks = _nlmse(predict(o0, battery), yb)
    ht = o0.harvest_t
    half = (tt + 1) / 2
    h1 = sum(h for t_, h in ht if t_ < half) / max(half, 1)
    h2 = sum(h for t_, h in ht if t_ >= half) / max(tt + 1 - half, 1)
    nf = o0.mem.n_floats()
    tf = max(getattr(o0, "total_flops", 0), 1)
    CG = nl_end - nl_birth
    out = dict(
        status="OK", steps=tt + 1, U=o0.gain - o0.cost, alive=o0.alive, CG=CG, CG_marks=nl_marks - nl_birth,
        nlmse_end=nl_end, nlmse_birth=nl_birth, E2C=CG / np.log10(10 + (tt + 1) * tf * max(nf, 1)),
        compression=CG / max(nf, 1) * 100, reach=h2 / (h1 + 1e-6) if h1 > 0 else (10.0 if h2 > 0 else 1.0),
        option=reachable(adj, o0.node) / max(reach0, 1), n_floats=nf, flops=tf, probes=o0.probes, rollouts=o0.rollouts,
        conversions=o0.conversions, mark_writes=sum(o.writes for o in orgs), diverged=diverged,
        pop_U=float(np.mean([o.gain - o.cost for o in orgs])), final_kind=o0.mem.kind, dims=dims, n_nodes=N,
        init_digest=init_digest, event_digest=ev_hash.hexdigest()[:16],
        final_digest=_digest(x, *[np.asarray(a) for a in o0.mem.params()]) if o0.mem.params() else _digest(x),
        trace=trace, secs=round(time.time() - t0, 3))
    if record:
        out["events"] = events
    if return_memory:
        out["_memory"] = o0.mem
    return out
