"""W2-AI: per-trial-index accuracy of both champions on all 64 held worlds (mirror pairs), plus the one-shot-latch
prediction: pair-mean accuracy at trial k = .5 + .5 * P(first lead-negative trial >= k)... computed empirically from
the recorded cue sequence (latch model: a world floods at its first positive cue, then reads a constant sign).
CPU eager, 2 threads."""
import os, sys, json, gzip, pathlib, time
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"; os.environ["OMP_NUM_THREADS"] = "2"
ROOT = pathlib.Path(__file__).resolve().parents[6]; sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import numpy as np, torch
torch.set_num_threads(2); assert not torch.cuda.is_available()
from prometheus.ananke import assays, envs, search
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int
import fwd
out = {}
c0 = time.process_time()
for cid in ("925caa3a48964717", "882525a9d4a3d073"):
    r = fwd.load(cid)
    ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"]); sp = search.SearchSpec(**r["search"])
    g = np.asarray(r["result"]["champion"], dtype=np.int64)
    hs = assays.world_seeds(H_int(r["search_seed"], search.HELD_NS), sp.M_held)
    M = len(hs)
    ws = [hs[m - (m % 2)] for m in range(M)]
    ep = envs.build(ph, env, hs)
    w = fwd.AblWorld(ph, np.repeat(g[None], M, 0), ws, device="cpu", schedule=ep.schedule)
    w.run(env.T(), graph=False)
    tr = w.trace.numpy()
    pt = envs.per_trial(ep, tr)                       # [M, trials]
    s0 = tr[ep.ro_tick, np.arange(M)[:, None], 0]     # readout S0 values
    # latch model: world b "fires" at its first trial with positive target y (cue sign incl. mirror), readout
    # thereafter = sign of the fired state; before firing = sign of the quiescent state. Fit the two signs from data.
    y = ep.y
    fired = np.cumsum(y > 0, 1) > 0
    sf = np.sign(s0[fired]).mean() if fired.any() else 0
    sq = np.sign(s0[~fired]).mean() if (~fired).any() else 0
    latch_pred_correct = np.where(fired, np.sign(sf) == y, np.sign(sq) == y).astype(float)
    agree = float((np.sign(s0) == np.where(fired, np.sign(sf), np.sign(sq))).mean())
    out[cid] = {"acc_by_trial": pt.mean(0).round(4).tolist(), "acc": float(pt.mean()),
                "latch_model_acc": float(latch_pred_correct.mean()),
                "latch_model_acc_by_trial": latch_pred_correct.mean(0).round(4).tolist(),
                "mean_sign_s0_fired": float(sf), "mean_sign_s0_quiescent": float(sq),
                "frac_readouts_matching_latch_model": agree,
                "frac_readouts_zero": float((s0 == 0).mean())}
    print(cid, json.dumps(out[cid]), flush=True)
out["cpu_s"] = round(time.process_time() - c0, 1)
(pathlib.Path(__file__).parent / "out_per_trial.json").write_text(json.dumps(out, indent=1))
