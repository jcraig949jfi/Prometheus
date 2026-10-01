"""W2-AJ TASK 2: 4781b0a1 sensor-to-sensor edge cut + DICT-k curve. Predictions in PLAN.md (written first).

Each mirror pair runs as its own B=2 World with a per-pair neighbour table installed by temporarily
overriding prometheus.ananke.topology.build (the only call site is World.__init__), restored in a
finally block. Env placement is native (envs.dist_matrix untouched). CPU eager, 2 threads.
Usage: python aj_edgecut.py [cut|dictk|all]
"""
import os
import sys
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "2"
import contextlib
import gzip
import itertools
import json
import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parents[6]
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402
import torch  # noqa: E402
torch.set_num_threads(2)
assert not torch.cuda.is_available()
from prometheus.ananke import assays, envs, search, topology  # noqa: E402
from prometheus.ananke.engine import World  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402
from prometheus.ananke.rng import H_int  # noqa: E402

ROWS = ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz"
NS = 0x57324A41  # "W2JA" control-edge RNG namespace
r = [x for x in (json.loads(l) for l in gzip.open(ROWS, "rt"))
     if x["cell_id"].startswith("4781b0a1") and x["kind"] == "evolve"][0]
ph = Physics.from_dict(r["physics"]).validate()
env = envs.EnvSpec(**r["env"])
g0 = np.asarray(r["result"]["champion"], dtype=np.int64).reshape(ph.rules, ph.prog_len, 5)
N, RAD = ph.n_sites, ph.radius
assert ph.topology == "ring"
seeds = assays.world_seeds(H_int(r["search_seed"], search.HELD_NS), 64)[:32]
M = len(seeds)
EP = envs.build(ph, env, seeds)
SI = EP.schedule.sense_idx.numpy()
RA = EP.schedule.read_idx.numpy()[:, 0]
NBR0, DIST0 = topology.build(ph)


def ringd(a, b):
    x = abs(int(a) - int(b)) % N
    return min(x, N - x)


@contextlib.contextmanager
def table(nbr):
    ob = topology.build
    topology.build = lambda p: (nbr, DIST0.copy())
    try:
        yield
    finally:
        topology.build = ob
    assert topology.build is ob


def run_pair(p, nbr, keep=None):
    """Run mirror pair p (worlds 2p, 2p+1) with neighbour table nbr; keep = sensor slots cued (None=all).
    Returns (pair accuracy, emissions by the dump site, per-world readout trace)."""
    b0 = 2 * p
    sub = [seeds[b0], seeds[b0 + 1]]
    ep = envs.build(ph, env, sub)
    assert (ep.schedule.sense_idx.numpy() == SI[b0:b0 + 2]).all()
    if keep is not None:
        for k in range(ep.schedule.sense_val.shape[2]):
            if k not in keep:
                ep.schedule.sense_val[:, :, k] = 0
    dump = (int(RA[b0]) + N // 2) % N
    dump_emit = torch.zeros((), dtype=torch.int64)
    orig = World._emit

    def hook(self, want, chan, pay):
        nonlocal dump_emit
        dump_emit = dump_emit + want[:, dump].sum()
        return orig(self, want, chan, pay)

    World._emit = hook
    try:
        with table(nbr):
            w = World(ph, np.repeat(g0[None], 2, 0), [sub[0], sub[0]], device="cpu", schedule=ep.schedule)
        w.run(env.T(), graph=False)
    finally:
        World._emit = orig
    acc = envs.score(ep, w.trace.cpu().numpy())
    return float(acc.mean()), int(dump_emit)


def summarize(name, accs, extra):
    a = np.asarray(accs)
    m, lo, hi = assays.pair_ci(a)
    o = {"cond": name, "acc": round(float(m), 4), "lo99": round(float(lo), 4), "hi99": round(float(hi), 4),
         "pair_sd": round(float(a.std()), 4), "pairs": a.round(4).tolist()}
    o.update(extra)
    print({k: v for k, v in o.items() if k != "pairs"}, flush=True)
    return o


def edges(p):
    b0 = 2 * p
    S = set(SI[b0].tolist())
    a = int(RA[b0])
    ss, sn, nn = [], [], []
    for u in range(N):
        for j in range(NBR0.shape[1]):
            v = int(NBR0[u, j])
            if u in S and v in S:
                ss.append((u, j))
            elif u in S and v not in S and v != a:
                sn.append((u, j))
            elif u not in S and u != a and v not in S and v != a and ringd(u, a) <= 6 and ringd(v, a) <= 6:
                nn.append((u, j))
    return ss, sn, nn


def cut_table(p, es):
    nbr = NBR0.copy()
    dump = (int(RA[2 * p]) + N // 2) % N
    for u, j in es:
        nbr[u, j] = dump
    return nbr


def do_cut():
    out = []
    res = {k: [] for k in ("unpatched_ref", "identity", "CUT_SS", "CTRL_SN", "CTRL_NN")}
    info = {"n_ss": [], "n_sn_pool": [], "n_nn_pool": [], "dump_emit": {k: 0 for k in res}}
    for p in range(M // 2):
        ss, sn, nn = edges(p)
        g = np.random.default_rng(H_int(NS, p))
        k = len(ss)
        info["n_ss"].append(k)
        info["n_sn_pool"].append(len(sn))
        info["n_nn_pool"].append(len(nn))
        csn = [sn[i] for i in g.choice(len(sn), size=k, replace=False)]
        cnn = [nn[i] for i in g.choice(len(nn), size=k, replace=False)]
        for name, nbr in (("identity", NBR0.copy()), ("CUT_SS", cut_table(p, ss)),
                          ("CTRL_SN", cut_table(p, csn)), ("CTRL_NN", cut_table(p, cnn))):
            a, de = run_pair(p, nbr)
            res[name].append(a)
            info["dump_emit"][name] += de
    # unpatched reference: the full 32-world batch through the native path (= TASK 1 acc16)
    w = World(ph, np.repeat(g0[None], M, 0), [seeds[m - (m % 2)] for m in range(M)], device="cpu",
              schedule=envs.build(ph, env, seeds).schedule)
    w.run(env.T(), graph=False)
    acc = envs.score(EP, w.trace.cpu().numpy()).reshape(M // 2, 2).mean(-1)
    res["unpatched_ref"] = acc.tolist()
    info["identity_equals_unpatched_per_pair"] = bool(np.allclose(res["identity"], res["unpatched_ref"]))
    for name in res:
        out.append(summarize(name, res[name], {"dump_emit": info["dump_emit"].get(name)}))
    info["dump_emit"].pop("unpatched_ref")
    return {"conditions": out, "info": info,
            "example_pair0": {"sensors": SI[0].tolist(), "actuator": int(RA[0]), "ss_edges": edges(0)[0]}}


def adj_pairs(sens, sub):
    return sum(ringd(sens[i], sens[j]) <= RAD for i, j in itertools.combinations(sub, 2))


def do_dictk():
    out = []
    for kk in range(1, 6):
        for mode in ("ADJ", "SPREAD"):
            if kk in (1, 5) and mode == "SPREAD":
                continue
            accs, npairs = [], []
            for p in range(M // 2):
                sens = SI[2 * p].tolist()
                subs = list(itertools.combinations(range(5), kk))
                sc = [adj_pairs(sens, s) for s in subs]
                best = max(sc) if mode == "ADJ" else min(sc)
                sub = subs[sc.index(best)]
                npairs.append(best)
                a, _ = run_pair(p, NBR0.copy(), keep=sub)
                accs.append(a)
            out.append(summarize(f"k{kk}_{mode}", accs, {"k": kk, "mode": mode,
                                                          "adj_pairs_per_pair": npairs}))
    return out


if __name__ == "__main__":
    t0 = time.process_time()
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    res = {}
    if what in ("cut", "all"):
        res["cut"] = do_cut()
    if what in ("dictk", "all"):
        res["dictk"] = do_dictk()
    res["cpu_s"] = round(time.process_time() - t0, 1)
    json.dump(res, open(HERE / f"edgecut_{what}.json", "w"), indent=1)
    print("cpu_s", res["cpu_s"])
