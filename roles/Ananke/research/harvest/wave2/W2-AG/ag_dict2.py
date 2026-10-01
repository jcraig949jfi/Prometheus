"""W2-AG decisive check (written before running): 4781b0a1 hypothesis 'reverberating agreement loop'.
A latched sensor forwards PAY1 = max(IN0_1, SENSE), so after its 2-tick cue its payload is non-zero only if it hears
another positive sensor. Prediction: with only TWO sensors cued, a mutually adjacent pair (ring distance <= radius)
gives accuracy > .5; a non-adjacent pair gives EXACTLY .500 per mirror pair (like DICT). 32 held worlds (16 pairs)."""
import os, sys, json, time
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "H-PLANT"))
import torch; torch.set_num_threads(2); assert not torch.cuda.is_available()
import numpy as np
import hp_common
from prometheus.ananke import assays, envs, search
from prometheus.ananke.engine import World
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int
t0 = time.process_time()
r = [x for x in hp_common.rows() if x["cell_id"].startswith("4781b0a1") and x["kind"] == "evolve"][0]
ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"]); g0 = np.asarray(r["result"]["champion"])
N, R = r["physics"]["n_sites"], r["physics"]["radius"]
seeds = assays.world_seeds(H_int(r["search_seed"], search.HELD_NS), 64)[:32]
M = len(seeds); ws = [seeds[m - (m % 2)] for m in range(M)]
def ringd(a, b): x = abs(int(a) - int(b)) % N; return min(x, N - x)
def run(keep_fn):
    ep = envs.build(ph, env, seeds)
    si = np.asarray(ep.schedule.sense_idx)  # [B, K] site index per sensor
    sv = ep.schedule.sense_val
    info = []
    for b in range(M):
        keep = keep_fn(si[b] if si.ndim == 2 else si)
        info.append(keep)
        for k in range(sv.shape[2]):
            if keep is None or k not in keep:
                sv[:, b, k] = 0
    w = World(ph, np.repeat(g0[None], M, 0), ws, device="cpu", schedule=ep.schedule)
    w.run(env.T(), graph=False)
    acc = envs.score(ep, w.trace.cpu().numpy())
    pairs = acc.reshape(M // 2, 2).mean(-1)
    valid = np.array([info[2 * p] is not None for p in range(M // 2)])
    m, lo, hi = assays.pair_ci(pairs[valid]) if valid.sum() > 2 else (float("nan"),) * 3
    return {"n_pairs": int(valid.sum()), "acc": float(m), "lo99": float(lo), "hi99": float(hi),
            "pair_sd": float(pairs[valid].std()), "pairs": pairs[valid].round(4).tolist()}
def pick(adj):
    def f(s):
        K = len(s)
        for i in range(K):
            for j in range(i + 1, K):
                if (ringd(s[i], s[j]) <= R) == adj and ringd(s[i], s[j]) > 0:
                    return (i, j)
        return None
    return f
ep0 = envs.build(ph, env, seeds); si0 = np.asarray(ep0.schedule.sense_idx)
out = {"sense_idx_shape": list(si0.shape), "example_sensors_w0": si0[0].tolist() if si0.ndim == 2 else si0.tolist(),
       "read_idx_w0": np.asarray(ep0.schedule.read_idx).ravel()[:2].tolist()}
out["all5"] = run(lambda s: tuple(range(len(s))))
out["pair_adjacent"] = run(pick(True))
out["pair_nonadjacent"] = run(pick(False))
out["single_0"] = run(lambda s: (0,))
out["cpu_s"] = round(time.process_time() - t0, 1)
json.dump(out, open(os.path.join(os.path.dirname(__file__), "dict2_4781.json"), "w"), indent=1)
for k, v in out.items():
    print(k, v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk != "pairs"})
