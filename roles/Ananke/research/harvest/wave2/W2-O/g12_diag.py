"""W2-O: is a G12_STATE_LIVE alarm on a recorded NULL a broken experiment (schedule/readout/IO stops in
the 2nd half) or a champion property (latch/saturation/energy death)? Also a guard NEGATIVE-CONTROL panel:
the same guards on recorded SIGNAL cells (a guard that fires equally on SIGNALs does not mark brokenness).
Usage: python g12_diag.py diag <cell...> | python g12_diag.py signal <cell...>"""
import os, sys, json, pathlib
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["PTE_MUT_THREADS"] = "2"
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import null_audit as NA  # noqa: E402  (CPU guard set up there)
import numpy as np  # noqa: E402
from prometheus.ananke import assays, envs, search  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402
from prometheus.ananke.rng import H_int  # noqa: E402
from prometheus.ananke.search import HELD_NS  # noqa: E402
from pte_mut.guards import guarded  # noqa: E402


def diag(cid):
    r = NA.ROWS[cid]
    ph = Physics.from_dict(r["physics"]).validate()
    env = envs.EnvSpec(**r["env"])
    sp = search.SearchSpec(**r["search"])
    champ = np.asarray(r["result"]["champion"])
    hs = assays.world_seeds(H_int(r["search_seed"], HELD_NS), sp.M_held)
    with guarded() as g:
        res = assays.evaluate(ph, champ[None], env, hs, device="cpu", graph=False)
        al = g.check()
        w = g.worlds[0][0]
    ep = envs.build(ph, env, hs)
    T = env.T()
    h = T // 2
    tr = w.trace.cpu().numpy()[:T, :, 0]
    sv = ep.schedule.sense_val.numpy()
    ch = np.diff(tr, axis=0) != 0
    last_change = np.array([np.flatnonzero(ch[:, b]).max() + 1 if ch[:, b].any() else -1 for b in range(tr.shape[1])])
    pt = envs.per_trial(ep, w.trace.cpu().numpy())
    ntr = pt.shape[1]
    sc = ep.scored
    acc1 = float((pt[:, :ntr // 2] * sc[:, :ntr // 2]).sum() / sc[:, :ntr // 2].sum())
    acc2 = float((pt[:, ntr // 2:] * sc[:, ntr // 2:]).sum() / sc[:, ntr // 2:].sum())
    et = w.tel["emit_trace"].cpu().numpy()[:T]
    s0_end = tr[-1]
    out = {"cell": cid, "family": env.family, "alarms": al, "held_acc": float(res.mean()[0]), "T": T,
           "sched_nonzero_ticks_1st_2nd": [int((sv[:h] != 0).any((1, 2)).sum()), int((sv[h:] != 0).any((1, 2)).sum())],
           "readout_change_frac_1st_2nd": [float(ch[:h - 1].any(0).mean()), float(ch[h - 1:].any(0).mean())],
           "last_change_tick_median": float(np.median(last_change)),
           "per_trial_acc_1st_2nd": [acc1, acc2],
           "emit_1st_2nd": [int(et[:h].sum()), int(et[h:].sum())],
           "energy_final_frac": float(w.E.float().mean().item() / max(ph.e_max, 1)),
           "s0_end_abs_median": float(np.median(np.abs(s0_end))), "s0_end_abs_max": int(np.abs(s0_end).max()),
           "s0_end_sign_balance": float(np.mean(np.sign(s0_end))),
           "economy": r["levels"].get("economy"), "c_op": ph.c_op, "e_max": ph.e_max}
    return out


def signal(cid):
    r = NA.ROWS[cid]
    res = NA.run_cell(cid)
    res["recorded_signal"] = bool(r["labels"].get("SIGNAL"))
    return res


if __name__ == "__main__":
    mode, cells = sys.argv[1], sys.argv[2:]
    fn = {"diag": diag, "signal": signal}[mode]
    with open(HERE / f"out/g12_{mode}.jsonl", "a") as f:
        for c in cells:
            o = fn(c)
            print(json.dumps(o, default=str)[:1500], flush=True)
            f.write(json.dumps(o, default=str) + "\n")
