"""W2-AL: latch prevalence across C1 evolve SIGNAL champions (RELAY, MAJ, then HOLD).

Per row (held seeds world_seeds(H(search_seed, HELD_NS), M_held), mirror pairs share physics seeds, CPU eager):
  - known-answer gate: (acc, lo99, hi99) must equal the recorded held values bit-exactly;
  - accuracy by trial index; late-half (trials >= trials//2) accuracy with the gate's own pair bootstrap CI;
  - one-shot latch model fit: a world reads sign q until its first trial whose cue has polarity p, then sign r
    forever.  Fit p in {+,-} and cue definition in {target y, any sensor column (MAJ)}; q, r by majority sign.
    fit = fraction of readouts whose sign equals the model's prediction (zeros never match);
  - twin assay (assays.twin_assay, hseeds[:16]) at the trials listed in W2AL_TWIN (default "0,2"); trial 2 is
    checked against the recorded twin.
Usage: python prevalence.py FAMILY[,FAMILY...]   (appends to out_rows.jsonl; skips cells already done)
CPU only, torch 1 thread (W2AL_THREADS) set AFTER imports, graph=False."""
import os, sys, json, gzip, pathlib, time
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"; os.environ["OMP_NUM_THREADS"] = "2"
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]; sys.path.insert(0, str(ROOT))
import numpy as np, torch
from prometheus.ananke import assays, envs, search
from prometheus.ananke.engine import World
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int
torch.set_num_threads(int(os.environ.get("W2AL_THREADS", "1"))); assert not torch.cuda.is_available()

OUT = HERE / "out_rows.jsonl"
TWIN_TRIALS = [int(x) for x in os.environ.get("W2AL_TWIN", "0,2").split(",") if x != ""]
BUDGET_S = float(os.environ.get("W2AL_BUDGET_S", "1e9"))
MAXN = int(os.environ.get("W2AL_MAXN", "0"))


def latch_fit(s0, y, sv_sign_any):
    """s0 [M,tr] readouts, y [M,tr] targets, sv_sign_any: dict p -> [M,tr] bool (any sensor column has sign p
    in the trial's cue window).  Returns best model."""
    sg = np.sign(s0)
    best = None
    cands = {}
    for p in (1, -1):
        cands[("y", p)] = (y == p)
        if sv_sign_any is not None:
            cands[("anysensor", p)] = sv_sign_any[p]
    for (cue, p), ev in cands.items():
        fired = np.cumsum(ev, 1) > 0
        q = np.sign(sg[~fired].mean()) if (~fired).any() else 0
        r = np.sign(sg[fired].mean()) if fired.any() else 0
        pred = np.where(fired, r, q)
        fit = float((sg == pred).mean())
        pred_acc = float(np.where(pred == 0, .5, (pred == y)).mean())
        if best is None or fit > best["fit"]:
            best = {"fit": fit, "cue": cue, "p": p, "q": float(q), "r": float(r), "pred_acc": pred_acc,
                    "frac_fired_by_end": float(fired[:, -1].mean())}
    return best


def done_cells():
    if not OUT.exists():
        return set()
    return {json.loads(l)["cell_id"] for l in OUT.read_text().splitlines() if l.strip()}


def main():
    fams = sys.argv[1].split(",")
    rows = [json.loads(l) for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt")]
    todo = [r for r in rows if r["kind"] == "evolve" and r["env"]["family"] in fams
            and r["result"]["held"]["lo99"] > 0.55]
    todo.sort(key=lambda r: (fams.index(r["env"]["family"]), r["cell_id"]))
    have = done_cells()
    c_start = time.process_time()
    ndone = 0
    for r in todo:
        if r["cell_id"] in have:
            continue
        if MAXN and ndone >= MAXN:
            break
        if time.process_time() - c_start > BUDGET_S:
            print("budget stop", flush=True)
            break
        c0, t0 = time.process_time(), time.time()
        ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"]); sp = search.SearchSpec(**r["search"])
        g = np.asarray(r["result"]["champion"], dtype=np.int64)
        hs = assays.world_seeds(H_int(r["search_seed"], search.HELD_NS), sp.M_held)
        M = len(hs)
        ws = [hs[m - (m % 2)] for m in range(M)]
        ep = envs.build(ph, env, hs)
        w = World(ph, np.repeat(g[None], M, 0), ws, device="cpu", schedule=ep.schedule)
        w.run(env.T(), graph=False)
        tr = w.trace.cpu().numpy()
        acc_w = envs.score(ep, tr)
        m, lo, hi = assays.pair_ci(acc_w.reshape(-1, 2).mean(-1))
        h = r["result"]["held"]
        gate = bool(abs(m - h["acc"]) < 1e-12 and abs(lo - h["lo99"]) < 1e-12 and abs(hi - h["hi99"]) < 1e-12)
        pt = envs.per_trial(ep, tr)                                   # [M, trials]
        ntr = env.trials
        late = pt[:, ntr // 2:].mean(1)
        lm, llo, lhi = assays.pair_ci(late.reshape(-1, 2).mean(-1))
        early = pt[:, :ntr // 2].mean(1)
        s0 = tr[ep.ro_tick, np.arange(M)[:, None], 0]
        sv = ep.schedule.sense_val.numpy()                            # [T, M, K]
        Pd = env.period()
        anyp = None
        if sv.shape[2] > 1:
            anyp = {p: np.zeros((M, ntr), bool) for p in (1, -1)}
            for k in range(ntr):
                win = sv[k * Pd:k * Pd + env.cue_len]                 # [cue_len, M, K]
                anyp[1][:, k] = (win > 0).any((0, 2))
                anyp[-1][:, k] = (win < 0).any((0, 2))
        lf = latch_fit(s0, ep.y, anyp)
        lf_y = latch_fit(s0, ep.y, None)
        tw = {}
        for t in TWIN_TRIALS:
            tw[t] = {k: float(v[0]) for k, v in
                     assays.twin_assay(ph, g[None], env, hs[:16], trial=t, device="cpu").items()}
        rec_tw = r["result"]["twin"]
        tw2_exact = (all(abs(tw[2][k] - rec_tw[k]) < 1e-9 for k in rec_tw) if 2 in tw else None)
        rec = {"cell_id": r["cell_id"], "wave": r["wave"], "family": env.family, "topology": ph.topology,
               "radius": ph.radius, "n_sites": ph.n_sites, "env_d": env.d, "trials": ntr,
               "held_acc": h["acc"], "held_lo99": h["lo99"], "gate_exact": gate,
               "recomputed": [float(m), float(lo), float(hi)],
               "acc_by_trial": pt.mean(0).round(4).tolist(),
               "early_acc": float(early.mean()),
               "late_acc": float(lm), "late_lo99": float(llo), "late_hi99": float(lhi),
               "latch": lf, "latch_y_only": lf_y,
               "frac_readouts_zero": float((s0 == 0).mean()),
               "twin_recorded": rec_tw, "twin": {str(k): v for k, v in tw.items()}, "twin2_repro_exact": tw2_exact,
               "cpu_s": round(time.process_time() - c0, 1), "wall_s": round(time.time() - t0, 1)}
        with OUT.open("a") as f:
            f.write(json.dumps(rec) + "\n")
        ndone += 1
        print(r["cell_id"], env.family, f"gate={gate} acc={m:.3f} late={lm:.3f}[{llo:.3f}] fit={lf['fit']:.3f}"
              f" bh={[round(tw[t]['beyond_hop'], 3) for t in tw]} cpu={rec['cpu_s']} wall={rec['wall_s']}",
              flush=True)


if __name__ == "__main__":
    main()
