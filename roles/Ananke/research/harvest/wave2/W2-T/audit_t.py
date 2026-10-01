"""W2-T step 2: W2-O's admissibility audit over the whole C1 NULL population, in batches.
Guards: W2-O's PATCHED copy (G12 judges only ctrl=='none' Worlds), imported from ../W2-O/pte_mut.
Mode per cell (out/cells.json):
  full=True  -> held normal + zero_comm arms in ONE guarded() context (all guards incl. G0/G6/G7), known-answer on
                acc/lo99/hi99/zero_comm/comm_delta/comm_delta_lo99 + held_tel, then FINAL-seed ranking evaluation
                in a second guarded() context (champ_train_final known-answer + guards).
  full=False -> held NORMAL arm only in guarded() (G1-G5, G9-G12 meaningful; G0/G6/G7 need a control and are not
                evaluated), known-answer on acc/lo99/hi99 + held_tel.
Both: direct G8 (held vs all train+final seeds), engagement (readout-dead worlds, emitting worlds, twin-blind pairs),
per-half per-trial accuracy (G12/TRUNCATED test), feasibility (reach, cue reception, wake recompute == engine).
Usage: python audit_t.py <batch_index> <n_batches> | python audit_t.py cell <cell...>   CPU eager, 2 threads."""
import os, sys, json, time, pathlib, gzip
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
NT = os.environ.get("W2T_THREADS", "1")      # <= 2; 1 avoids OMP spin waste on a saturated host
os.environ["OMP_NUM_THREADS"] = NT
os.environ["PTE_MUT_THREADS"] = NT
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-O"))           # PATCHED pte_mut (G12 control-exempt)
from pte_mut import env as _env  # noqa: F401,E402
from pte_mut.guards import guarded  # noqa: E402
import pte_mut  # noqa: E402
assert "W2-O" in pte_mut.__file__, pte_mut.__file__
import numpy as np  # noqa: E402
import torch  # noqa: E402
assert not torch.cuda.is_available()
torch.set_num_threads(int(NT))
assert int(NT) <= 2
from prometheus.ananke import assays, envs, search, topology, rng  # noqa: E402
from prometheus.ananke.engine import Controls  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402
from prometheus.ananke.rng import H_int  # noqa: E402
from prometheus.ananke.search import TRAIN_NS, FINAL_NS, HELD_NS  # noqa: E402

ROOT = HERE.parents[5]
ROWS = {}
for _l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt"):
    _r = json.loads(_l)
    ROWS[_r["cell_id"]] = _r


def bfs_all(ph):
    N = ph.n_sites
    nbr, _ = topology.build(ph)
    if nbr is None:
        M = np.ones((N, N), dtype=np.int64)
        np.fill_diagonal(M, 0)
        return M
    return np.stack([topology.graph_distances(ph, s) for s in range(N)])


def awake_mask(ph, ws_list, T, sites):
    """[T, B, len(sites)] bool: exact recomputation of engine step 3 (WAKE)."""
    B = len(ws_list)
    if ph.update_mode == "sync":
        a = (np.arange(T) % ph.update_period == 0)[:, None, None]
        return np.broadcast_to(a, (T, B, len(sites))).copy()
    ws = torch.as_tensor(np.asarray(ws_list, dtype=np.int64))
    st = torch.as_tensor(np.asarray(sites, dtype=np.int64))
    p = ph.p16(ph.update_p)
    out = np.zeros((T, B, len(sites)), dtype=bool)
    for t in range(T):
        hw = rng.chain(rng.site_base(ws, rng.WAKE, t, st), 0)
        out[t] = ((hw & 0xFFFF) < p).numpy()
    return out


def feasibility(ph, env, seeds, world_normal):
    """W2-O feasibility() plus a HOLD branch (sensor == actuator, no transport)."""
    ep = envs.build(ph, env, seeds)
    B = len(seeds)
    fam = env.family
    M = bfs_all(ph)
    sidx = ep.schedule.sense_idx.numpy()
    ridx = ep.schedule.read_idx.numpy()[:, 0]
    sval = ep.schedule.sense_val.numpy()
    T = sval.shape[0]
    K = sidx.shape[1]
    ws = [seeds[b - (b % 2)] for b in range(B)]
    aw_all = awake_mask(ph, ws, T, list(range(ph.n_sites)))
    Pd = env.period()
    tr = env.trials
    reach = np.zeros((B, K), dtype=bool)
    hops = np.full((B, K), -1)
    recv = np.zeros((B, K, tr), dtype=bool)
    for b in range(B):
        for k in range(K):
            s = sidx[b, k]
            a = ridx[b]
            h = M[s, a]
            hops[b, k] = h
            reach[b, k] = h >= 0
            for i in range(tr):
                t0 = i * Pd + (env.delta + 1 if (fam == "FLIP" and k == 1) else 0)
                ts = np.arange(t0, min(t0 + env.cue_len, T))
                live = ts[sval[ts, b, k] != 0]
                recv[b, k, i] = bool(aw_all[live, b, s].any())
    partial = None
    if fam in ("RELAY", "FLIP", "HOLD"):
        info = reach[:, 0, None] & recv[:, 0]
        impossible = ~reach[:, 0]
    elif fam == "XOR":
        info = (reach[:, :, None] & recv).all(1)
        impossible = ~reach.all(1)
    else:
        info = (reach[:, :, None] & recv).any(1)
        impossible = ~reach.any(1)
        partial = (~reach).any(1) & reach.any(1)
    scored = ep.scored
    frac = (info & scored).sum(1) / scored.sum(1)
    ceiling = 0.5 + 0.5 * frac
    awk = aw_all.sum((0, 2)).astype(np.int64)
    eng_awake = world_normal.stats["awake"].cpu().numpy().astype(np.int64)
    hc = hops[:, :1] if fam == "FLIP" else hops
    out = {"impossible_worlds": int(impossible.sum()), "M": B,
           "hops_median": float(np.median(hc[hc >= 0])) if (hc >= 0).any() else None,
           "hops_max": int(hc.max()),
           "cue_recv_frac": [round(float(recv[:, k].mean()), 4) for k in range(K)],
           "ceiling_info_mean": float(ceiling.mean()), "ceiling_info_min": float(ceiling.min()),
           "wake_recompute_matches_engine": bool(np.array_equal(awk, eng_awake))}
    if partial is not None:
        out["partial_reach_worlds"] = int(partial.sum())
    return out


def run_cell(cid, full):
    t0c, w0 = time.process_time(), time.time()
    r = ROWS[cid]
    ph = Physics.from_dict(r["physics"]).validate()
    env = envs.EnvSpec(**r["env"])
    sp = search.SearchSpec(**r["search"])
    S = r["search_seed"]
    champ = np.asarray(r["result"]["champion"])
    hseeds = assays.world_seeds(H_int(S, HELD_NS), sp.M_held)
    with guarded() as g:
        g.champion = champ
        rh = assays.evaluate(ph, champ[None], env, hseeds, device="cpu", graph=False)
        if full:
            rz = assays.evaluate(ph, champ[None], env, hseeds, ctrl=Controls(zero_comm=True), device="cpu",
                                 graph=False)
        alarms = sorted(g.check())
        wn = next(w for w, req, _ in g.worlds if req and req[0] == "none")
        wz = next(w for w, req, _ in g.worlds if req and req[0] != "none") if full else None
    ph_pair = rh.pair_acc()[0]
    m, lo, hi = assays.pair_ci(ph_pair)
    rec = r["result"]["held"]
    rep = {"acc": float(m), "lo99": float(lo), "hi99": float(hi)}
    if full:
        pz_pair = rz.pair_acc()[0]
        dm, dlo, dhi = assays.pair_ci(ph_pair - pz_pair)
        rep.update({"zero_comm": float(pz_pair.mean()), "comm_delta": float(dm), "comm_delta_lo99": float(dlo)})
    gate = {k: [rec[k], rep[k], abs(rec[k] - rep[k]) < 1e-12] for k in rep}
    devs = {k: abs(float(rh.tel[k][0]) - r["result"]["held_tel"][k]) for k in r["result"]["held_tel"]}
    tel_key = max(devs, key=devs.get)
    tel_dev = devs[tel_key]
    gate_pass = all(v[2] for v in gate.values()) and tel_dev < 1e-6   # float32 telemetry: ulp-level slack
    res = {"cell": cid, "family": env.family, "full": full, "gate_pass": gate_pass, "gate": gate,
           "tel_max_abs_dev": tel_dev, "tel_worst_key": tel_key, "alarms_held": alarms}
    sel = set()
    for gen in range(sp.gens):
        sel |= set(assays.world_seeds(H_int(S, TRAIN_NS, gen), sp.M))
    sel |= set(assays.world_seeds(H_int(S, FINAL_NS), sp.M_final))
    res["G8_direct_overlap"] = bool(sel & set(hseeds))
    trf = wn.trace.cpu().numpy()
    tr = trf[:, :, 0]
    ep = envs.build(ph, env, hseeds)
    s0_ro = tr[ep.ro_tick, np.arange(len(hseeds))[:, None]]
    pt = envs.per_trial(ep, trf)
    ntr = pt.shape[1]
    sc = ep.scored
    h1 = (pt[:, :ntr // 2] * sc[:, :ntr // 2]).sum(1) / sc[:, :ntr // 2].sum(1)
    h2 = (pt[:, ntr // 2:] * sc[:, ntr // 2:]).sum(1) / sc[:, ntr // 2:].sum(1)
    p1 = h1.reshape(-1, 2).mean(1)
    p2 = h2.reshape(-1, 2).mean(1)
    _, lo1, _ = assays.pair_ci(p1)
    _, lo2, _ = assays.pair_ci(p2)
    stn = {k: v.cpu().numpy() for k, v in wn.stats.items()}
    res.update({
        "readout_dead_worlds": int((s0_ro == 0).all(1).sum()),
        "readout_never_written_worlds": int((tr == 0).all(0).sum()),
        "twin_blind_pairs": int((tr[:, 0::2] == tr[:, 1::2]).all(0).sum()), "pairs": len(hseeds) // 2,
        "worlds_emitting": int((stn["emitters"] > 0).sum()), "delivered": int(stn["delivered"].sum()),
        "half_acc": [float(p1.mean()), float(p2.mean())], "half_lo99": [float(lo1), float(lo2)],
        "feasibility": feasibility(ph, env, hseeds, wn)})
    if full:
        stz = {k: v.cpu().numpy() for k, v in wz.stats.items()}
        res["zero_comm_arm"] = {"delivered": int(stz["delivered"].sum()), "attempted": int(stz["attempted"].sum())}
        fs = assays.world_seeds(H_int(S, FINAL_NS), sp.M_final)
        with guarded() as g2:
            g2.champion = champ
            rf = assays.evaluate(ph, champ[None], env, fs, device="cpu", graph=False)
            res["alarms_final"] = sorted(g2.check())
        v = float(rf.mean()[0])
        res["final_gate"] = [r["result"]["champ_train_final"], v, abs(v - r["result"]["champ_train_final"]) < 1e-12]
    res["compute"] = {"cpu_s": round(time.process_time() - t0c, 1), "wall_s": round(time.time() - w0, 1)}
    return res


if __name__ == "__main__":
    cells = json.load(open(HERE / "out/cells.json"))
    if sys.argv[1] == "cell":
        todo = [c for c in cells if c["cell"] in sys.argv[2:]]
        tag = "adhoc"
    else:
        bi, nb = int(sys.argv[1]), int(sys.argv[2])
        todo = cells[bi::nb]
        tag = f"b{bi:02d}of{nb}"
    outp = HERE / f"out/audit_{tag}.jsonl"
    done = set()
    if outp.exists():
        done = {json.loads(x)["cell"] for x in open(outp)}
    deadline = time.time() + float(os.environ.get("W2T_WALL", "540"))
    for c in todo:
        if c["cell"] in done:
            continue
        if time.time() > deadline:
            print("DEADLINE; resume later", flush=True)
            break
        res = run_cell(c["cell"], c["full"])
        print(json.dumps({k: res[k] for k in ("cell", "family", "full", "gate_pass", "alarms_held",
                                              "readout_dead_worlds", "compute")}), flush=True)
        with open(outp, "a") as f:
            f.write(json.dumps(res, default=str) + "\n")
