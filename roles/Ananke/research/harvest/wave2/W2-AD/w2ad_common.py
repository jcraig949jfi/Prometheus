"""W2-AD common: CPU only, 2 threads, eager. Import BEFORE torch.
Batched multi-program evaluation: G groups x M worlds in ONE World (each group = (genome, schedule edit)),
every group re-uses the same world seeds, so groups share all physics randomness (common random numbers;
paired plant-vs-ablation differences are exact pairings). Semantics per group == hp_common.evaluate."""
from __future__ import annotations
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["HP_THREADS"] = "2"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
import json, pathlib, sys, time
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
W2 = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "roles/Ananke/research/harvest/H-PLANT"))
for d in ("W2-B", "W2-P", "W2-U", "W2-L", "W2-M", "W2-J"):
    sys.path.insert(0, str(W2 / d))
import numpy as np
import torch
assert not torch.cuda.is_available(), "GPU visible; refusing"
torch.set_num_threads(2)
assert torch.get_num_threads() <= 2
import hp_common as hc  # noqa: E402
from prometheus.ananke import assays, envs, plants  # noqa: E402
from prometheus.ananke.engine import World, Schedule  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402
from prometheus.ananke.rng import H_int  # noqa: E402

OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
NS = 0x57324144  # "W2AD" fresh namespace (plants and ceilings); disjoint from C1 HELD/TRAIN/FINAL keys


def ci(v):
    m, lo, hi = assays.pair_ci(np.asarray(v, float))
    return float(m), float(lo), float(hi)


def multi_eval(ph, env, seeds, groups, inward=False):
    """groups: list of (name, genome [rules,L,5], sched_edit(sense_val_np, ep) or None).
    Returns {name: {"pairs": [P], "acc","lo99","hi99", "chg_pairs","same_pairs" (FLIP)}} and the episode."""
    M = len(seeds); assert M % 2 == 0
    if inward:
        real = envs.dist_matrix
        envs.dist_matrix = lambda ph_: real(ph_).T.copy()
        try:
            ep = envs.build(ph, env, seeds)
        finally:
            envs.dist_matrix = real
    else:
        ep = envs.build(ph, env, seeds)
    G = len(groups)
    ws1 = [seeds[m - (m % 2)] for m in range(M)]
    sv0 = ep.schedule.sense_val.numpy()          # [T, M, K]
    svs, gens = [], []
    for name, g, edit in groups:
        sv = sv0.copy()
        if edit is not None:
            edit(sv, ep)
        svs.append(sv)
        gens.append(np.repeat(np.asarray(g)[None], M, axis=0))
    sch = Schedule(ep.schedule.sense_idx.repeat(G, 1), torch.as_tensor(np.concatenate(svs, 1)),
                   ep.schedule.read_idx.repeat(G, 1))
    w = World(ph, np.concatenate(gens, 0), ws1 * G, device="cpu", schedule=sch)
    w.run(env.T(), graph=False)
    trace = w.trace.cpu().numpy()                # [T, G*M, 1]
    out = {}
    tr = env.trials
    if env.family == "FLIP":
        Pd = env.period()
        x = np.sign(sv0[np.arange(tr) * Pd][:, :, 0]).T
        chg = np.zeros_like(ep.scored); chg[:, 1:] = x[:, 1:] != x[:, :-1]
    for gi, (name, _, _) in enumerate(groups):
        tg = trace[:, gi * M:(gi + 1) * M]
        acc = envs.score(ep, tg)
        pairs = acc.reshape(M // 2, 2).mean(-1)
        o = {"pairs": pairs}
        o["acc"], o["lo99"], o["hi99"] = ci(pairs)
        if env.family == "FLIP":
            corr = envs.per_trial(ep, tg)
            sc = ep.scored
            def pooled(mask):
                num = (corr * mask).reshape(M // 2, 2, tr).sum((1, 2))
                den = mask.reshape(M // 2, 2, tr).sum((1, 2))
                return np.where(den > 0, num / np.maximum(den, 1), np.nan)
            pc, ps = pooled(sc & chg), pooled(sc & ~chg)
            ok = ~(np.isnan(pc) | np.isnan(ps))
            bal = (pc[ok] + ps[ok]) / 2
            o["B"], o["B_lo99"], o["B_hi99"] = ci(bal) if ok.sum() >= 2 else (np.nan, np.nan, np.nan)
            o["chg"] = float(np.nanmean(pc)); o["same"] = float(np.nanmean(ps)); o["B_npairs"] = int(ok.sum())
        out[name] = o
    return out, ep


def paired(a, b):
    return ci(np.asarray(a) - np.asarray(b))


class Clock:
    def __init__(self): self.t0 = time.process_time(); self.w0 = time.time()
    def done(self): return {"cpu_s": round(time.process_time() - self.t0, 2), "wall_s": round(time.time() - self.w0, 2), "threads": 2}


def jdump(path, obj):
    pathlib.Path(path).write_text(json.dumps(obj, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else (float(o) if isinstance(o, (np.floating,)) else str(o))))
