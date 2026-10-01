"""W2-AI: do the two C1 multi-hop RELAY SIGNAL champions FORWARD?

Usage: python fwd.py <cell_id_prefix> <mode>
  mode = gate   : full 64 held worlds, known-answer gate vs recorded (acc, lo99, hi99) + per-world hop table
  mode = ablate : first 32 held worlds (16 mirror pairs), emission-ablation conditions + twin divergence

Ablation hook: World._emit is wrapped so that want := want & ~mask[B, N]. A silenced site still runs its
program, still receives, still pays nothing extra (economy off in both cells); it only cannot put packets into
flight. Mirror twins share the mask. CPU eager only (graph=False), 2 threads.
"""
import os
import sys
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "2"
import gzip
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


class AblWorld(World):
    emit_mask = None   # [B, N] bool, True = silenced

    def _emit(self, want, chan, pay):
        if self.emit_mask is not None:
            want = want & ~self.emit_mask
        return super()._emit(want, chan, pay)


def load(prefix):
    for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt"):
        r = json.loads(l)
        if r["cell_id"].startswith(prefix):
            return r
    raise KeyError(prefix)


def run(ph, genome, env, seeds, mask=None):
    """hp_common.evaluate semantics (mirror pairs share physics seeds) + per-tick twin divergence."""
    M = len(seeds)
    ws = [seeds[m - (m % 2)] for m in range(M)]
    ep = envs.build(ph, env, seeds)
    g = np.repeat(genome[None], M, axis=0)
    w = AblWorld(ph, g, ws, device="cpu", schedule=ep.schedule)
    if mask is not None:
        w.emit_mask = torch.as_tensor(mask, dtype=torch.bool)
    T = env.T()
    first_div = np.full((M // 2, ph.n_sites), -1, dtype=np.int64)   # first tick a site's S differs between twins
    for t in range(T):
        w.step()
        d = (w.S[0::2] != w.S[1::2]).any(-1).numpy()
        new = d & (first_div < 0)
        first_div[new] = t
    acc = envs.score(ep, w.trace.numpy())
    return acc, ep, first_div


def hop_table(ph, ep):
    M = ep.schedule.sense_idx.shape[0]
    D = {}
    rows = []
    for b in range(M):
        s = int(ep.schedule.sense_idx[b, 0])
        a = int(ep.schedule.read_idx[b, 0])
        if s not in D:
            D[s] = topology.graph_distances(ph, s)
        rows.append((s, a, int(D[s][a])))
    return rows


def path_sets(ph, s, a):
    """shortest-path intermediates; sensor out-neighbours (a vertex cut unless a is one of them)."""
    ds = topology.graph_distances(ph, s)
    N = ph.n_sites
    # distance v -> a over the directed table: BFS from every v is costly; use reverse BFS
    nbr, _ = topology.build(ph)
    rev = [[] for _ in range(N)]
    for u in range(N):
        for v in nbr[u]:
            rev[int(v)].append(u)
    da = np.full(N, -1)
    da[a] = 0
    fr = [a]
    while fr:
        nx = []
        for v in fr:
            for u in rev[v]:
                if da[u] < 0:
                    da[u] = da[v] + 1
                    nx.append(u)
        fr = nx
    h = ds[a]
    onpath = [v for v in range(N) if v not in (s, a) and ds[v] >= 0 and da[v] >= 0 and ds[v] + da[v] == h]
    outn = sorted(set(int(v) for v in nbr[s]) - {s, a})
    return onpath, outn, ds, da


def main():
    prefix, mode = sys.argv[1], sys.argv[2]
    r = load(prefix)
    cid = r["cell_id"]
    ph = Physics.from_dict(r["physics"])
    env = envs.EnvSpec(**r["env"])
    sp = search.SearchSpec(**r["search"])
    g = np.asarray(r["result"]["champion"], dtype=np.int64)
    hseeds = assays.world_seeds(H_int(r["search_seed"], search.HELD_NS), sp.M_held)
    t0, c0 = time.time(), time.process_time()
    out = {"cell": cid, "topology": ph.topology, "radius": ph.radius, "env_d": env.d, "mode": mode,
           "recorded_held": r["result"]["held"]}
    if mode == "gate":
        acc, ep, fd = run(ph, g, env, hseeds)
        pairs = acc.reshape(-1, 2).mean(-1)
        m, lo, hi = assays.pair_ci(pairs)
        h = r["result"]["held"]
        out["recomputed"] = {"acc": float(m), "lo99": float(lo), "hi99": float(hi)}
        out["gate_exact"] = bool(abs(m - h["acc"]) < 1e-12 and abs(lo - h["lo99"]) < 1e-12
                                 and abs(hi - h["hi99"]) < 1e-12)
        ht = hop_table(ph, ep)
        out["hops_per_world"] = [x[2] for x in ht]
        out["env_dist_per_world"] = [int(envs.dist_matrix(ph)[s, a]) for s, a, _ in ht]
        out["acc_per_world"] = acc.tolist()
        hops = np.array([x[2] for x in ht])
        out["acc_by_hops"] = {int(k): {"n_worlds": int((hops == k).sum()), "acc": float(acc[hops == k].mean())}
                              for k in np.unique(hops)}
        out["acc_first32"] = float(acc[:32].mean())
        out["actuator_ever_diverges_frac"] = float(
            (fd[np.arange(len(ht) // 2), [ht[2 * p][1] for p in range(len(ht) // 2)]] >= 0).mean())
    else:
        seeds = hseeds[:int(os.environ.get("W2AI_M", "32"))]
        ep = envs.build(ph, env, seeds)
        ht = hop_table(ph, ep)
        M, N = len(seeds), ph.n_sites
        rng = np.random.default_rng(H_int(0x5741, int(cid[:8], 16)) % (2 ** 32))
        conds = {"none": np.zeros((M, N), bool), "path": np.zeros((M, N), bool), "cut_outn": np.zeros((M, N), bool),
                 "all_but_s_a": np.ones((M, N), bool), "ctrl_rand_path": np.zeros((M, N), bool),
                 "ctrl_rand_outn": np.zeros((M, N), bool), "ctrl_near_offpath": np.zeros((M, N), bool)}
        info = []
        for b, (s, a, hop) in enumerate(ht):
            onpath, outn, ds, da = path_sets(ph, s, a)
            conds["path"][b, onpath] = True
            conds["cut_outn"][b, outn] = True
            conds["all_but_s_a"][b, [s, a]] = False
            role = set(onpath) | set(outn) | {s, a}
            # off-path pool: not s, a, not shortest-path intermediates, not sensor out-neighbours,
            # and not on any path of length <= hop + 1 (ds + da <= hop + 1)
            pool = [v for v in range(N) if v not in role and not (ds[v] >= 0 and da[v] >= 0 and ds[v] + da[v] <= hop + 1)]
            # twins share the mask: draw on the lead world, copy to its twin
            if b % 2 == 0:
                rp = rng.choice(pool, size=len(onpath), replace=False)
                ro = rng.choice(pool, size=len(outn), replace=False)
                # near control: off-path sites closest to the sensor (sensor-side, wrong direction)
                near = sorted(pool, key=lambda v: (ds[v] if ds[v] >= 0 else 10 ** 6, v))[:len(onpath)]
            conds["ctrl_rand_path"][b, rp] = True
            conds["ctrl_rand_outn"][b, ro] = True
            conds["ctrl_near_offpath"][b, near] = True
            info.append({"s": s, "a": a, "hop": hop, "n_path": len(onpath), "n_outn": len(outn),
                         "a_in_outn": a in set(int(v) for v in topology.build(ph)[0][s])})
        out["worlds"] = info
        only = os.environ.get("W2AI_CONDS")
        res = {}
        for name, mask in conds.items():
            if only and name not in only.split(","):
                continue
            tt = time.time()
            acc, _, fd = run(ph, g, env, seeds, mask)
            pairs = acc.reshape(-1, 2).mean(-1)
            m, lo, hi = assays.pair_ci(pairs)
            a_idx = [ht[2 * p][1] for p in range(M // 2)]
            act_div = fd[np.arange(M // 2), a_idx]
            res[name] = {"acc": float(m), "lo99": float(lo), "hi99": float(hi),
                         "pairs_ne_half": int((np.abs(pairs - 0.5) > 1e-12).sum()),
                         "actuator_diverges_pairs": int((act_div >= 0).sum()),
                         "actuator_first_div_tick": act_div.tolist(),
                         "n_silenced_mean": float(mask.sum(1).mean()), "wall_s": round(time.time() - tt, 1)}
            print(name, json.dumps({k: v for k, v in res[name].items() if k != "actuator_first_div_tick"}), flush=True)
        out["conditions"] = res
        # diff-trace style: first divergence tick at sensor / path / actuator in the unablated run (trial 1 cue t=0)
    out["cpu_s"] = round(time.process_time() - c0, 1)
    out["wall_s"] = round(time.time() - t0, 1)
    fn = HERE / f"out_{cid[:8]}_{mode}.json"
    fn.write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k not in ("acc_per_world", "hops_per_world", "env_dist_per_world",
                                                                 "worlds", "conditions")}), flush=True)


if __name__ == "__main__":
    main()
