"""W2-AJ TASK 1: dynamic emitter census by site class over the 69 C1 RELAY+MAJ SIGNAL evolve champions.

Pre-stated (before running): SR-01 predicts that NO never-sensing site (not a sensor, not the actuator)
emits a twin-discordant (cue-bearing) packet in any champion, and that never-sensing non-zero-payload
emissions are ~0 for single-rule champions.

Hook: World._emit is wrapped READ-ONLY (records want/pay, then calls the original unchanged); restored
in a finally block. Held worlds = the champion's own held seeds (search.HELD_NS), first 32 = 16 mirror
pairs, mirror twins share physics seeds (assays.evaluate convention). CPU eager, 2 threads.

Classes per world: sensor = schedule.sense_idx[b]; actuator = read_idx[b]; never = all other sites.
Counts:
  emit      : awake & o_emit>0 (packet attempted)
  emit_nz   : emit with any payload component != 0 (emitter-side payload, before channel noise)
  disc      : per mirror pair, per site and tick, (want, payload*want) differs between the twins:
              the site's emission carries cue information (twins differ only in cue sign)
  sdiff     : per pair, site-ticks whose state S differs between twins (information REACHED the site)
Usage: python aj_census.py [cid8 ...]   (default: all 69)
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
from prometheus.ananke import engine  # noqa: E402
from prometheus.ananke.engine import World  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402
from prometheus.ananke.rng import H_int  # noqa: E402

ROWS = ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz"


def bfs_from(nbr, srcs):
    N = nbr.shape[0]
    d = np.full(N, 10 ** 6, dtype=np.int64)
    fr = list(srcs)
    for s in fr:
        d[s] = 0
    k = 0
    while fr:
        k += 1
        nx = []
        for u in fr:
            for v in nbr[u]:
                if d[v] > k:
                    d[v] = k
                    nx.append(int(v))
        fr = nx
    return d


def champions():
    R = [json.loads(l) for l in gzip.open(ROWS, "rt")]
    return [r for r in R if r["kind"] == "evolve" and r["env"]["family"] in ("RELAY", "MAJ")
            and r["result"]["held"]["lo99"] > 0.55]


def census(r, npairs=16):
    ph = Physics.from_dict(r["physics"]).validate()
    env = envs.EnvSpec(**r["env"])
    g0 = np.asarray(r["result"]["champion"], dtype=np.int64).reshape(ph.rules, ph.prog_len, 5)
    seeds = assays.world_seeds(H_int(r["search_seed"], search.HELD_NS), 64)[:2 * npairs]
    M = len(seeds)
    ws = [seeds[m - (m % 2)] for m in range(M)]
    ep = envs.build(ph, env, seeds)
    N = ph.n_sites
    si = ep.schedule.sense_idx.numpy()
    ra = ep.schedule.read_idx.numpy()[:, 0]
    cls = np.full((M, N), 2, dtype=np.int64)          # 0 sensor, 1 actuator, 2 never
    for b in range(M):
        cls[b, si[b]] = 0
        cls[b, ra[b]] = 1                             # actuator overrides if it also senses (none expected)
    overlap = int(sum(ra[b] in set(si[b].tolist()) for b in range(M)))
    acc_n = {"emit": torch.zeros(M, N, dtype=torch.int64), "emit_nz": torch.zeros(M, N, dtype=torch.int64)}
    disc = torch.zeros(M // 2, N, dtype=torch.int64)
    sdiff = torch.zeros(M // 2, N, dtype=torch.int64)
    orig = World._emit

    def hook(self, want, chan, pay):
        nz = want & (pay != 0).any(-1)
        acc_n["emit"] += want.to(torch.int64)
        acc_n["emit_nz"] += nz.to(torch.int64)
        wv = want.view(M // 2, 2, N)
        pv = (pay * want[..., None].to(pay.dtype)).view(M // 2, 2, N, -1)
        disc.add_(((wv[:, 0] != wv[:, 1]) | (pv[:, 0] != pv[:, 1]).any(-1)).to(torch.int64))
        Sv = self.S.view(M // 2, 2, N, -1)
        sdiff.add_((Sv[:, 0] != Sv[:, 1]).any(-1).to(torch.int64))
        return orig(self, want, chan, pay)

    World._emit = hook
    try:
        w = World(ph, np.repeat(g0[None], M, 0), ws, device="cpu", schedule=ep.schedule)
        w.run(env.T(), graph=False)
    finally:
        World._emit = orig
    assert World._emit is orig
    acc = envs.score(ep, w.trace.cpu().numpy())
    pairs = acc.reshape(M // 2, 2).mean(-1)
    em = acc_n["emit"].numpy()
    enz = acc_n["emit_nz"].numpy()
    dsc = disc.numpy()
    sdf = sdiff.numpy()
    cl_pair = cls[0::2]                                  # twins share placement
    nbr, _ = topology.build(ph)
    out = {"cell": r["cell_id"][:8], "family": env.family, "wave": r["wave"], "topology": ph.topology,
           "N": N, "radius": ph.radius, "rules": ph.rules, "setrule": bool(ph.setrule), "d": env.d,
           "held_acc_rec": r["result"]["held"]["acc"], "held_lo99_rec": r["result"]["held"]["lo99"],
           "acc16": round(float(pairs.mean()), 4), "act_sensor_overlap": overlap}
    names = ("sensor", "actuator", "never")
    for c, nm in enumerate(names):
        mk = cls == c
        mp = cl_pair == c
        out[f"{nm}_sites"] = int(mk.sum())
        out[f"{nm}_emit"] = int(em[mk].sum())
        out[f"{nm}_emit_nz"] = int(enz[mk].sum())
        out[f"{nm}_disc"] = int(dsc[mp].sum())
        out[f"{nm}_sdiff"] = int(sdf[mp].sum())
        out[f"{nm}_sites_emit_nz"] = int(((enz > 0) & mk).sum())
        out[f"{nm}_sites_disc"] = int(((dsc > 0) & mp).sum())
        out[f"{nm}_sites_sdiff"] = int(((sdf > 0) & mp).sum())
    # hop distance (sensor -> site, signal direction) of never-sensing sites that emit nz / discordantly
    hn, hd, hs = [], [], []
    for p in range(M // 2):
        b = 2 * p
        if nbr is None:
            dist = np.ones(N, dtype=np.int64)
            dist[si[b]] = 0
        else:
            dist = bfs_from(nbr, si[b])
        nev = cls[b] == 2
        hn += dist[nev & ((enz[b] + enz[b + 1]) > 0)].tolist()
        hd += dist[nev & (dsc[p] > 0)].tolist()
        hs += dist[nev & (sdf[p] > 0)].tolist()
    def hist(h):
        v, c = np.unique(h, return_counts=True) if h else ([], [])
        return {str(int(a)): int(b) for a, b in zip(v, c)}
    out["never_nz_hops"] = hist(hn)
    out["never_disc_hops"] = hist(hd)
    out["never_sdiff_hops"] = hist(hs)
    return out


if __name__ == "__main__":
    t0 = time.process_time()
    ch = champions()
    assert len(ch) == 69, len(ch)
    want = sys.argv[1:]
    sel = [r for r in ch if not want or r["cell_id"][:8] in want]
    outp = HERE / ("census.jsonl" if not want else "census_partial.jsonl")
    with open(outp, "a" if want else "w") as f:
        for r in sel:
            t1 = time.process_time()
            o = census(r)
            o["cpu_s"] = round(time.process_time() - t1, 1)
            f.write(json.dumps(o) + "\n")
            f.flush()
            print(o["cell"], o["family"], o["topology"], o["rules"], "acc16", o["acc16"],
                  "never: emit", o["never_emit"], "nz", o["never_emit_nz"], "disc", o["never_disc"],
                  "sdiff", o["never_sdiff"], "| sensor nz", o["sensor_emit_nz"], "disc", o["sensor_disc"],
                  "| act nz", o["actuator_emit_nz"], "cpu", o["cpu_s"], flush=True)
    print("total cpu_s", round(time.process_time() - t0, 1))
