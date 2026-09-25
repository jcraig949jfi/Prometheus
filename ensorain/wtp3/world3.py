"""WTP-03 executor = Declared physics change vs WTP-02: the query market is graded (see the query block).

WTP-02 executor (frozen copy) + three hooks: `tap` (records the exact
samples organism 0 learns from, the world's final field and org 0's seen set), `field_hook`
(maps every built field, birth and drift, to a surrogate) and exposure counters.

WTP-02 executor (PREREG_WTP02 s1, s3). Reuses WTP-01's field generators,
geometries, registry and memory substrates; replaces randomness,
measurement and degeneracy handling.

Randomness (R3): named SeedSequence streams. Everything environmental is
PRE-DRAWN per step from world_dyn / noise, so two lives with the same seed
see the same environment whatever the organism does (door closures depend
on the path, but their dice are pre-drawn per step too).

Measurement (R1): V0 = field variance at birth, fixed. AC = -log10(MSE/V0)
clipped to [-3, 6]. CG = AC(org) - AC(zero predictor); CGu = the same on
battery cells the organism never observed."""
import collections
import copy
import hashlib
import time

import numpy as np

from ensorain.wtp.registry import REG
from ensorain.wtp.world import build_field, build_graph, reachable, Illegal
from ensorain.wtp.organism import make_memory, convert, CONVERTIBLE

STREAMS = ("world_gen", "world_dyn", "noise", "policy", "learner", "mutation", "transplant", "controls")
BANDS = (0.01, 0.03, 0.10, 0.25)
MAXOBS = 64


def streams(seed):
    kids = np.random.SeedSequence(int(seed)).spawn(len(STREAMS))
    return {n: np.random.default_rng(k) for n, k in zip(STREAMS, kids)}, \
        {n: [int(seed)] + list(k.spawn_key) for n, k in zip(STREAMS, kids)}


def AC(pred, y, V0):
    mse = float(np.mean((np.nan_to_num(pred, nan=0.0, posinf=1e6, neginf=-1e6) - y) ** 2))
    return float(np.clip(-np.log10(max(mse / V0, 1e-12)), -3, 6))


def _digest(*arrays):
    h = hashlib.sha256()
    for a in arrays:
        h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()[:16]


def build(g, S, twin=None, reskin=False):
    """World construction from world_gen (+ controls for the shuffle permutation)."""
    x, rew = build_field(g["substrate"], S["world_gen"])
    dims = list(x.shape)
    if twin == "shuffled":
        p = S["controls"].permutation(x.size)
        x, rew = x.reshape(-1)[p].reshape(dims), rew.reshape(-1)[p].reshape(dims)
    if reskin:
        rr = np.random.default_rng(S["controls"].integers(2 ** 31))
        for m in range(len(dims)):
            perm = rr.permutation(dims[m])
            x, rew = np.take(x, perm, axis=m), np.take(rew, perm, axis=m)
    adj, node_cell = build_graph(g["geometry"], dims, x, S["world_gen"])
    ir, wd, N = g["irreversibility"], S["world_gen"], len(adj)
    hazard_edges = set()
    for v in range(N):
        for u in list(adj[v]):
            if wd.random() < ir["hazard_frac"]:
                hazard_edges.add((v, u))
            if wd.random() < ir["oneway"] * 0.5 and v in adj[u] and len(adj[u]) > 1:
                adj[u].discard(v)
    return x, rew, dims, adj, node_cell, hazard_edges


def mem_cap(g, cells):
    return max(1, int(g["memory"]["band"] * cells))


class Org:
    def __init__(self, i, mem, node):
        self.i, self.mem, self.node = i, mem, node
        self.alive = True
        self.gain = self.cost = 0.0
        self.flops = self.total_flops = 0
        self.buf, self.queue = [], []
        self.visited, self.seen = set(), set()
        self.marks = collections.OrderedDict()
        self.probes = self.rollouts = self.conversions = self.writes = self.updates = self.consolidations = 0
        self.step_gain, self.step_flops = [], []


def run_life(g, seed, *, twin=None, transplant=None, freeze=False, reskin=False, no_marks=False,
             lifetime=None, excursions=True, record=False, return_memory=False, intervene=None,
             tap=None, field_hook=None):
    """twin: None | 'shuffled' | 'frozen' | 'random'. intervene: dict of named ablations applied
    mid-construction (e.g. {'ablate_half': True, 'reset_memory': True})."""
    t0 = time.time()
    S, seeds = streams(seed)
    intervene = intervene or {}
    try:
        x, rew, dims, adj, node_cell, hazard_edges = build(g, S, twin, reskin)
        if field_hook is not None:
            x, rew = field_hook(x, rew)
    except Illegal as ex:
        return dict(status="ILLEGAL", reason=str(ex), stream_seeds=seeds)
    except Exception as ex:
        return dict(status="ILLEGAL", reason=f"{type(ex).__name__}: {ex}", stream_seeds=seeds)
    N = len(adj)
    cells = x.size
    V0 = float(x.var())
    addr = np.array(np.unravel_index(np.arange(cells), dims)).T
    ir, mg, B = g["irreversibility"], g["memory"], g["boundary"]
    R, L, C, SR = g["resource"], g["learning"], g["credit"], g["search"]
    tr, ob = g["transition"], g["observation"]
    T = int(lifetime or g["time"]["lifetime"])
    cap = mem_cap(g, cells)
    mark_cap = cap
    substrate = "none" if twin in ("random", "oracle") else mg["substrate"]
    policy = "random" if twin == "random" else SR["policy"]
    freeze = freeze or twin == "frozen"
    use_marks = B["marks"] != "none" and not no_marks and twin != "random"
    orgs = []
    try:
        for i in range(B["n_org"]):
            if transplant is not None and i == 0:
                mem = copy.deepcopy(transplant)
            else:
                mem = make_memory(substrate, dims, cap, S["learner"])
            orgs.append(Org(i, mem, 0 if i == 0 else int(S["world_gen"].integers(N))))
    except ValueError as ex:
        return dict(status="ILLEGAL", reason=f"memory: {ex}", stream_seeds=seeds)
    if intervene.get("reset_memory"):
        orgs[0].mem = make_memory(substrate, dims, cap, S["transplant"])
    if intervene.get("ablate_half"):
        for a in orgs[0].mem.params():
            a[S["transplant"].random(a.shape) < 0.5] = 0.0
    birth = copy.deepcopy(orgs[0].mem)
    battery = S["controls"].choice(cells, size=min(256, cells), replace=False)
    # pre-drawn environment
    nz = S["noise"]
    obs_noise = nz.standard_normal((T, MAXOBS))
    obs_lap = nz.laplace(size=(T, MAXOBS))
    obs_cau = np.clip(nz.standard_cauchy((T, MAXOBS)), -10, 10)
    probe_noise = nz.standard_normal((T, 32))
    door_u = nz.random((T, 4))
    query_cell = nz.integers(cells, size=T)
    wdyn = S["world_dyn"]
    drift_fields = {}
    if tr["drift"] > 0:
        for t in range(tr["drift_period"], T, tr["drift_period"]):
            try:
                drift_fields[t] = build_field(g["substrate"], wdyn)
                if field_hook is not None and drift_fields[t][0].shape == x.shape:
                    drift_fields[t] = field_hook(*drift_fields[t])
            except Illegal:
                pass
    basis = {t: (int(wdyn.integers(len(dims))), None) for t in range(tr["basis_change_period"], T, tr["basis_change_period"])} \
        if tr["basis_change_period"] else {}
    basis = {t: (m, wdyn.permutation(dims[m])) for t, (m, _) in basis.items()}
    rewire = {t: (wdyn.random(N), wdyn.integers(N, size=N)) for t in range(tr["rewire_period"], T, tr["rewire_period"])} \
        if tr["rewire_period"] else {}
    cat_u = wdyn.random(T)
    cat_m = wdyn.integers(len(dims), size=T)
    cat_i = wdyn.random(T)
    shared_marks = collections.OrderedDict()
    last_harv = np.full(N, -10 ** 9)
    ck = max(1, T // 20)
    trace = []
    ev_hash = hashlib.sha256()
    events = [] if record else None
    pol_rng = S["policy"]
    ln_rng = S["learner"]
    status = "OK"
    degenerate_reason = None
    reach_full = reachable(adj, 0)
    init_digest = _digest(np.asarray(battery), np.array(sorted((v, u) for v in range(N) for u in adj[v])))  # at birth

    def mark_store(o):
        return shared_marks if B["marks"] == "shared" else o.marks

    def predict(o, cidx):
        if twin == "oracle" and o.i == 0:
            return x.reshape(-1)[np.asarray(cidx, int)].astype(float)
        p = np.nan_to_num(o.mem.predict(addr[cidx]), nan=0.0, posinf=1e6, neginf=-1e6)
        if use_marks:
            st = mark_store(o)
            for j, c in enumerate(cidx):
                c = int(c)
                if c in st:
                    val, tw = st[c]
                    p[j] = val * (1 - B["mark_decay"]) ** max(0, tt - tw)
        return p

    def observe(v):
        c = int(node_cell[v])
        if ob["kind"] == "probe_only":
            return np.zeros(0, int), np.zeros(0)
        a = addr[c]
        if ob["kind"] == "cell":
            cc = np.array([c])
        else:
            m = ob["mode"] % len(dims)
            fib = np.repeat(a[None], dims[m], 0)
            fib[:, m] = np.arange(dims[m])
            cc = np.ravel_multi_index(fib.T, dims)
            if ob["kind"] == "masked":
                k = min(ob["k"], len(cc))
                cc = cc[np.argsort(obs_noise[tt, :len(cc)])[:k]]
        vals = x.reshape(-1)[cc].copy()
        if ob["kind"] == "marginal":
            vals = np.full(1, vals.mean())
            cc = np.array([c])
        for at in ob["chain"]:
            vals = np.asarray(REG[at["op"]].fn(vals, at["p"], np.random.default_rng(tt)), float)
            if vals.shape[0] != len(cc):
                vals = np.resize(vals, len(cc))
        if ob["noise_sd"] > 0:
            n = len(vals)
            z = {"normal": obs_noise, "laplace": obs_lap, "cauchy_clip": obs_cau}[ob["noise_dist"]][tt, :n]
            vals = vals + ob["noise_sd"] * z
        return cc[:MAXOBS], vals[:MAXOBS]

    def learn(o, cc, vals):
        if freeze or len(cc) == 0:
            return
        y = vals.copy()
        if C["noise"] > 0:
            y = y + C["noise"] * probe_noise[tt, :len(y)] if len(y) <= 32 else y
        if C["sign_flip"] > 0:
            y = np.where(door_u[tt, 0] < C["sign_flip"], -y, y)
        if C["radius"] > 0:
            ex_c, ex_y = [], []
            for c, v in zip(cc, y):
                w = np.nonzero(node_cell == c)[0]
                if len(w):
                    for u in sorted(adj[int(w[0])])[:C["radius"]]:
                        ex_c.append(int(node_cell[u]))
                        ex_y.append(v)
            if ex_c:
                cc, y = np.concatenate([cc, ex_c]).astype(int), np.concatenate([y, ex_y])
        o.queue.append((tt + C["delay"], cc, y))
        ready = [q for q in o.queue if q[0] <= tt]
        o.queue = [q for q in o.queue if q[0] > tt]
        for _, c2, y2 in ready:
            o.updates += len(y2)
            if tap is not None and o.i == 0:
                tap["t"].append(np.full(len(c2), tt))
                tap["c"].append(np.asarray(c2, int))
                tap["y"].append(np.asarray(y2, float))
            if L["rule"] == "batch_replay":
                o.buf.extend(zip(c2, y2))
                if len(o.buf) >= L["batch"]:
                    bc = np.array([b[0] for b in o.buf])
                    by = np.array([b[1] for b in o.buf])
                    for _ in range(L["sweeps"]):
                        o.flops += o.mem.learn(addr[bc], by, "nlms", L["lr"])
                    o.buf = []
            else:
                o.flops += o.mem.learn(addr[c2], y2, L["rule"], L["lr"])
                cons = L.get("consolidate")
                if cons:  # WTP-03 replay consolidation (PREREG_WTP03 s6): every `every` updates, `sweeps` passes over the last `window` samples
                    o.rbuf = (getattr(o, "rbuf", []) + list(zip(c2, y2)))[-cons["window"]:]
                    o.since = getattr(o, "since", 0) + len(y2)
                    if o.since >= cons["every"]:
                        o.since = 0
                        bc = np.array([b[0] for b in o.rbuf])
                        by = np.array([b[1] for b in o.rbuf])
                        for _ in range(cons["sweeps"]):
                            o.flops += o.mem.learn(addr[bc], by, L["rule"], L["lr"])
                        o.consolidations += 1
                o.buf = (o.buf + list(zip(c2, y2)))[-64:]
            o.mem.quantize(mg["bits"])
            o.cost += R["p_write"] * len(y2)
        for a in o.mem.params():
            if not np.all(np.isfinite(a)):
                a[~np.isfinite(a)] = 0.0

    def battery_state(o):
        yb = x.reshape(-1)[battery]
        pb = predict(o, battery)
        unseen = np.array([c not in o.seen for c in battery])
        ac, ac0 = AC(pb, yb, V0), AC(np.zeros_like(yb), yb, V0)
        if unseen.sum() >= 16:
            acu, acu0 = AC(pb[unseen], yb[unseen], V0), AC(np.zeros(unseen.sum()), yb[unseen], V0)
        else:
            acu = acu0 = float("nan")
        return ac, ac0, acu, acu0, int(unseen.sum())

    tt = 0
    for tt in range(T):
        if tt in drift_fields:
            x2, r2 = drift_fields[tt]
            if x2.shape == x.shape:
                d = tr["drift"]
                x = np.sqrt(1 - d) * x + np.sqrt(d) * x2
                rew = np.sqrt(1 - d) * rew + np.sqrt(d) * r2
        if tt in basis:
            m, perm = basis[tt]
            x, rew = np.take(x, perm, axis=m), np.take(rew, perm, axis=m)
        if tt in rewire:
            u, tgt = rewire[tt]
            for v in range(N):
                if u[v] < tr["rewire_frac"] and adj[v]:
                    adj[v].discard(min(adj[v]))
                    adj[v].add(int(tgt[v]))
        if tr["catastrophe_rate"] > 0 and cat_u[tt] < tr["catastrophe_rate"]:
            m = int(cat_m[tt])
            sl = [slice(None)] * len(dims)
            sl[m] = int(cat_i[tt] * dims[m])
            x = x.copy()
            rew = rew.copy()
            x[tuple(sl)] = 0.0
            rew[tuple(sl)] = 0.0
        if float(x.var()) < 0.05 * V0:  # per-step collapse check (R2): never score a collapsed world
            status, degenerate_reason = "DEGENERATE", "variance"
            break
        for o in orgs:
            if not o.alive:
                continue
            v = o.node
            o.visited.add(v)
            cc, vals = observe(v)
            o.seen.update(int(c) for c in cc)
            learn(o, cc, vals)
            g0 = o.gain
            if use_marks and len(cc):
                st = mark_store(o)
                st[int(cc[0])] = (float(vals[0]), tt)
                st.move_to_end(int(cc[0]))
                while len(st) > mark_cap:
                    st.popitem(last=False)
                o.writes += 1
                o.cost += R["p_write"]
            c = int(node_cell[v])
            if tt - last_harv[v] >= R["regrow"]:
                o.gain += R["gain"] * max(0.0, float(rew.reshape(-1)[c]) - R["theta"])
                last_harv[v] = tt
            if R["query_every"] and tt % R["query_every"] == 0:
                qc = int(query_cell[tt])
                # WTP-03 GRADED PREDICTION MARKET (PREREG_WTP03 s5): pays query_reward x (1 - err^2/V0),
                # loss capped at -3 x query_reward. The field mean (best constant) earns ~0 on average,
                # a learner earns in proportion to its R^2 on (mostly unseen) query cells, the oracle earns in full.
                err2 = min(abs(float(predict(o, np.array([qc]))[0] - x.reshape(-1)[qc])), 1e6) ** 2
                o.gain += R["query_reward"] * (1.0 - min(err2 / V0, 4.0))
                o.cost += R["p_read"]
            nbrs = sorted(adj[v])
            if policy == "random":
                nxt = int(nbrs[int(pol_rng.integers(len(nbrs)))])
            else:
                if policy == "probe_greedy":
                    pc = node_cell[nbrs][:32]
                    pv = x.reshape(-1)[pc] + ob["noise_sd"] * probe_noise[tt, :len(pc)]
                    o.seen.update(int(q) for q in pc)
                    learn(o, pc, pv)
                    o.probes += len(pc)
                    o.cost += R["p_probe"] * len(pc)
                    score = np.resize(pv, len(nbrs))
                elif policy == "rollout":
                    r0 = o.rollouts

                    def val(node, depth):
                        o.rollouts += 1
                        base = max(0.0, float(predict(o, np.array([node_cell[node]]))[0]) - R["theta"])
                        if depth <= 1:
                            return base
                        return base + 0.9 * max(val(u, depth - 1) for u in sorted(adj[node])[:4])
                    score = np.array([val(u, SR["depth"]) for u in nbrs])
                    o.cost += R["p_rollout"] * (o.rollouts - r0) * 1e-2
                    o.flops += (o.rollouts - r0) * max(1, o.mem.n_floats())
                else:
                    score = predict(o, node_cell[nbrs]) - R["theta"]
                    o.cost += R["p_read"] * len(nbrs)
                    o.flops += len(nbrs) * max(1, o.mem.n_floats())
                if policy == "novelty":
                    score = score + 10.0 * np.array([u not in o.visited for u in nbrs])
                if policy == "softmax":
                    z = np.clip(score / max(SR["temp"], 1e-3), -50, 50)
                    pz = np.exp(z - z.max())
                    nxt = int(pol_rng.choice(nbrs, p=pz / pz.sum()))
                elif policy == "eps_greedy" and pol_rng.random() < SR["eps"]:
                    nxt = int(nbrs[int(pol_rng.integers(len(nbrs)))])
                else:
                    nxt = int(nbrs[int(np.argmax(np.asarray(score) + 1e-9 * pol_rng.random(len(nbrs))))])
            if (v, nxt) in hazard_edges:
                o.mem.hazard(ir["hazard"], ln_rng)
            if ir["door_close"] > 0 and door_u[tt, 1] < ir["door_close"] and len(adj[v]) > 1:
                adj[v].discard(nxt)
            o.cost += R["p_move"] * 0.1 + R["metabolism"] + R["p_compute"] * o.flops
            o.total_flops += o.flops
            o.step_gain.append(o.gain - g0)
            o.step_flops.append(o.flops)
            o.flops = 0
            o.node = nxt
            ev = (tt, o.i, v, nxt)
            ev_hash.update(repr(ev).encode())
            if record:
                events.append(ev)
            if R["energy0"] + o.gain - o.cost <= 0:
                o.alive = False
        if tt % ck == 0 or tt == T - 1:
            o0 = orgs[0]
            if mg["fluid"] and tt > 0 and len(o0.buf) >= 16 and o0.alive and not freeze:
                kind = str(ln_rng.choice([k for k in CONVERTIBLE if k != o0.mem.kind]))
                try:
                    sample = ln_rng.choice(cells, size=min(64, cells), replace=False)
                    new, fl = convert(o0.mem, kind, dims, cap, ln_rng, addr[sample], None)
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
                    o.mem.forget(mg["forget"], mg["forget_rate"], ln_rng)
            ac, ac0, acu, acu0, nun = battery_state(o0)
            ps = o0.mem.params()
            spars = float(np.mean([np.mean(np.abs(a) < 1e-6) for a in ps])) if ps else None
            var_ratio = float(x.var() / V0)
            reach = reachable(adj, o0.node) / N
            rewarding = float(np.mean(rew > R["theta"]))
            trace.append(dict(t=tt, AC=ac, AC0=ac0, ACu=acu, ACu0=acu0, n_unseen=nun, rank=o0.mem.eff_rank(),
                              kind=o0.mem.kind, sparsity=spars, var_ratio=var_ratio, reach=reach, rewarding=rewarding,
                              U=o0.gain - o0.cost, alive=o0.alive))
            if var_ratio < 0.05 or reach < 0.05 or rewarding == 0.0:
                status = "DEGENERATE"
                degenerate_reason = "variance" if var_ratio < 0.05 else ("topology" if reach < 0.05 else "resources")
                break
        if not any(o.alive for o in orgs):
            break
    o0 = orgs[0]
    if status == "OK":  # final degeneracy check on the end state
        if float(x.var()) < 0.05 * V0:
            status, degenerate_reason = "DEGENERATE", "variance"
        elif float(np.mean(rew > R["theta"])) == 0.0:
            status, degenerate_reason = "DEGENERATE", "resources"
    ac, ac0, acu, acu0, nun = battery_state(o0)
    sg, sf = np.array(o0.step_gain), np.array(o0.step_flops, float)
    n3 = max(1, len(sg) // 3)
    eff_first = (sg[:n3].sum() + 1e-3) / (sf[:n3].sum() + 1.0)
    eff_last = (sg[-n3:].sum() + 1e-3) / (sf[-n3:].sum() + 1.0)
    out = dict(status=status, degenerate_reason=degenerate_reason, steps=tt + 1, alive=o0.alive, U=o0.gain - o0.cost,
               AC=ac, AC0=ac0, CG=ac - ac0, ACu=acu, ACu0=acu0, CGu=(acu - acu0) if nun >= 16 else float("nan"),
               n_unseen=nun, n_seen=len(o0.seen), cells=cells, cap=cap, n_floats=o0.mem.n_floats(),
               band=mg["band"], CA=float(eff_last / eff_first), flops=o0.total_flops, probes=o0.probes,
               rollouts=o0.rollouts, conversions=o0.conversions, mark_writes=sum(o.writes for o in orgs),
               final_kind=o0.mem.kind, dims=dims, n_nodes=N, V0=V0, trace=trace, stream_seeds=seeds,
               init_digest=init_digest,
               event_digest=ev_hash.hexdigest()[:16], secs=None)
    # reachability gain (s3): matched 40-step excursions, trained vs birth memory, frozen world
    if excursions and status == "OK":
        top = rew.reshape(-1) >= np.quantile(rew, 0.9)

        def excursion(mem):
            o = Org(99, mem, o0.node)
            node, hit = o0.node, set()
            ex_rng = np.random.default_rng(int(S["controls"].integers(2 ** 31)) if False else 12345)
            for _ in range(40):
                nb = sorted(adj[node])
                p = np.nan_to_num(mem.predict(addr[node_cell[nb]]), nan=0.0)
                node = int(nb[int(np.argmax(p + 1e-9 * ex_rng.random(len(nb))))])
                if top[node_cell[node]]:
                    hit.add(node)
            return len(hit)
        out["RG"] = (excursion(o0.mem) - excursion(birth)) / 40.0
    else:
        out["RG"] = float("nan")
    out["secs"] = round(time.time() - t0, 3)
    out["updates"] = o0.updates
    out["consolidations"] = o0.consolidations
    out["life_frac"] = (tt + 1) / T
    if tap is not None:
        tap["x_final"] = x.copy()
        tap["x_birth_var"] = V0
        tap["seen"] = np.array(sorted(o0.seen), int)
        tap["dims"] = dims
        tap["T"] = T
    if record:
        out["events"] = events
    if return_memory:
        out["_memory"] = o0.mem
    return out
