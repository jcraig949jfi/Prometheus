"""W2-O step 2-3: re-run each sampled C1 NULL cell's recorded champion on its recorded HELD seeds with
W2-C's guards attached (read-only: guards only wrap/observe), plus feasibility instruments.
Known-answer gate: recorded held acc, lo99, hi99, zero_comm, comm_delta, comm_delta_lo99 must reproduce
exactly; otherwise the cell is STOPPED (no guard/feasibility verdict reported for it).
Usage: python null_audit.py [cell_id ...]   (default: all of out/sample.json). CPU eager (graph=False)."""
import os, sys, json, time, pathlib
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["PTE_MUT_THREADS"] = "2"
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-C"))
from pte_mut import env as _env  # noqa: F401  (CPU-only setup; asserts no CUDA)
from pte_mut.guards import guarded
import gzip
import numpy as np
import torch
assert not torch.cuda.is_available()
torch.set_num_threads(2)
from prometheus.ananke import assays, envs, search, topology, rng
from prometheus.ananke.engine import Controls
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int
from prometheus.ananke.search import TRAIN_NS, FINAL_NS, HELD_NS

ROOT = HERE.parents[5]
ROWS = {}
for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt"):
    r = json.loads(l)
    ROWS[r["cell_id"]] = r


def bfs_all(ph):
    """transport hop distance M[i, j] over the directed out-edge table (engine: rec = nbr[src]); -1 = none."""
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
    """Per-world physical feasibility of the task, independent of the genome:
    reach: needed sensor -> actuator transport paths exist (directed BFS);
    cue:   sensor site awake on >= 1 tick of a non-zero cue window (SENSE is never latched);
    ceiling_info: .5 + .5 * fraction of scored trials whose needed cue(s) are received AND can reach a
                  (upper bound ignoring timing/latency; the light cone is a separate bound)."""
    ep = envs.build(ph, env, seeds)
    B = len(seeds)
    fam = env.family
    M = bfs_all(ph)
    sidx = ep.schedule.sense_idx.numpy()
    ridx = ep.schedule.read_idx.numpy()[:, 0]
    sval = ep.schedule.sense_val.numpy()                     # [T, B, K]
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
    if fam in ("RELAY", "FLIP"):
        info = reach[:, 0, None] & recv[:, 0]               # FLIP: teacher is AT a; cue must reach a
        impossible = ~reach[:, 0]
    elif fam == "XOR":
        info = (reach[:, :, None] & recv).all(1)
        impossible = ~reach.all(1)
    else:  # MAJ
        info = (reach[:, :, None] & recv).any(1)
        impossible = ~reach.any(1)
        partial = (~reach).any(1) & reach.any(1)
    scored = ep.scored
    frac = (info & scored).sum(1) / scored.sum(1)
    ceiling = 0.5 + 0.5 * frac
    awk = aw_all.sum((0, 2)).astype(np.int64)
    eng_awake = world_normal.stats["awake"].cpu().numpy().astype(np.int64)
    hc = hops[:, :1] if fam == "FLIP" else hops            # FLIP column 1 (teacher) sits AT a
    out = {"impossible_worlds": int(impossible.sum()), "M": B,
           "unreachable_sensor_frac": float((~reach).mean()),
           "hops_median": float(np.median(hc[hc >= 0])) if (hc >= 0).any() else None,
           "hops_max": int(hc.max()),
           "cue_recv_frac": [round(float(recv[:, k].mean()), 4) for k in range(K)],
           "worlds_no_cue_ever": int((~recv[:, 0].any(1)).sum()),
           "ceiling_info_mean": float(ceiling.mean()), "ceiling_info_min": float(ceiling.min()),
           "wake_recompute_matches_engine": bool(np.array_equal(awk, eng_awake))}
    if partial is not None:
        out["partial_reach_worlds"] = int(partial.sum())
        out["sensors_reaching_mean"] = float(reach.sum(1).mean())
    return out


def run_cell(cid):
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
        rz = assays.evaluate(ph, champ[None], env, hseeds, ctrl=Controls(zero_comm=True), device="cpu",
                             graph=False)
        alarms = g.check()
        wn = next(w for w, req, _ in g.worlds if req and req[0] == "none")
        wz = next(w for w, req, _ in g.worlds if req and req[0] != "none")
    ph_pair, pz_pair = rh.pair_acc()[0], rz.pair_acc()[0]
    m, lo, hi = assays.pair_ci(ph_pair)
    dm, dlo, dhi = assays.pair_ci(ph_pair - pz_pair)
    rec = r["result"]["held"]
    rep = {"acc": float(m), "lo99": float(lo), "hi99": float(hi), "zero_comm": float(pz_pair.mean()),
           "comm_delta": float(dm), "comm_delta_lo99": float(dlo)}
    gate = {k: [rec[k], rep[k], abs(rec[k] - rep[k]) < 1e-12] for k in rep}
    gate_pass = all(v[2] for v in gate.values())
    res = {"cell": cid, "family": env.family, "gate_pass": gate_pass, "gate": gate}
    if not gate_pass:
        res["STOPPED"] = "known-answer gate failed"
        return res
    tel_dev = max(abs(float(rh.tel[k][0]) - r["result"]["held_tel"][k]) for k in r["result"]["held_tel"])
    sel = set()
    for gen in range(sp.gens):
        sel |= set(assays.world_seeds(H_int(S, TRAIN_NS, gen), sp.M))
    sel |= set(assays.world_seeds(H_int(S, FINAL_NS), sp.M_final))
    g8 = bool(sel & set(hseeds))
    tr = wn.trace.cpu().numpy()[:, :, 0]                     # [T, B] readout S0
    ep = envs.build(ph, env, hseeds)
    s0_ro = tr[ep.ro_tick, np.arange(len(hseeds))[:, None]]
    readout_dead = int((s0_ro == 0).all(1).sum())             # world scores exactly .5 by the 0-rule
    readout_never_written = int((tr == 0).all(0).sum())
    twin_blind = int((tr[:, 0::2] == tr[:, 1::2]).all(0).sum())  # pairs whose readout never diverges
    stn = {k: v.cpu().numpy() for k, v in wn.stats.items()}
    stz = {k: v.cpu().numpy() for k, v in wz.stats.items()}
    feas = feasibility(ph, env, hseeds, wn)
    res.update({
        "alarms": alarms, "tel_max_abs_dev": tel_dev, "G8_direct_overlap": g8,
        "readout_dead_worlds": readout_dead, "readout_never_written_worlds": readout_never_written,
        "twin_blind_pairs": twin_blind, "pairs": len(hseeds) // 2,
        "normal": {"emitters": int(stn["emitters"].sum()), "delivered": int(stn["delivered"].sum()),
                   "worlds_emitting": int((stn["emitters"] > 0).sum()), "nonnop": int(stn["nonnop"].sum())},
        "zero_comm_arm": {"delivered": int(stz["delivered"].sum()), "attempted": int(stz["attempted"].sum())},
        "zc_pairs_all_half": bool((pz_pair == 0.5).all()),
        "acc_equal_normal_vs_zc": bool(np.array_equal(rh.acc, rz.acc)),
        "feasibility": feas,
        "compute": {"cpu_s": round(time.process_time() - t0c, 1), "wall_s": round(time.time() - w0, 1)}})
    return res


if __name__ == "__main__":
    sample = json.load(open(HERE / "out/sample.json"))
    cells = sys.argv[1:] or [s["cell"] for s in sample]
    meta = {s["cell"]: s for s in sample}
    outp = HERE / "out/null_audit.jsonl"
    for cid in cells:
        res = run_cell(cid)
        res["lc_bound"] = meta.get(cid, {}).get("lc_bound")
        res["stratum"] = meta.get(cid, {}).get("stratum")
        print(json.dumps(res, default=str)[:1200], flush=True)
        with open(outp, "a") as f:
            f.write(json.dumps(res, default=str) + "\n")
