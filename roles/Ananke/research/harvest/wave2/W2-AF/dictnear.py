"""DICT-near control. W2-M's DICT cues only sensor 0, and envs.build picks sensor 0 FIRST, i.e. at env distance
exactly d (or the farthest reachable <= d); later sensors fall back to nearer sites when distance-d sites run
out. So DICT is the single-sensor transport of the FARTHEST sensor, not the best single sensor. DICT-near cues
only the sensor nearest the actuator (ties: lowest index), same plant, same held worlds.
Scored for every task-1 row whose selected member passes lo99 > .55, and for W2-M's 8 PLANT-SOLVED NULL rows
(their member as recorded). Reports int - DICT_near paired CI; also per-world sensor distance profiles."""
import json, sys
import af_common as c
import numpy as np
import torch
import w2m_plants as wp
from task1_maj import genome
from prometheus.ananke import envs
from prometheus.ananke.physics import Physics

def near_abl(ph):
    D = envs.dist_matrix(ph)
    def f(ep, sl):
        si = ep.schedule.sense_idx.numpy(); ri = ep.schedule.read_idx.numpy()[:, 0]
        for b in range(sl.start, sl.stop):
            dd = D[ri[b], si[b]]
            j = int(np.argmin(dd))
            keep = np.zeros(si.shape[1], bool); keep[j] = True
            ep.schedule.sense_val[:, b, torch.as_tensor(~keep)] = 0
    return f

def prof(ph, env, held):
    ep = envs.build(ph, env, held); D = envs.dist_matrix(ph)
    si = ep.schedule.sense_idx.numpy(); ri = ep.schedule.read_idx.numpy()[:, 0]
    d = np.array([D[ri[b], si[b]] for b in range(0, len(held), 2)])
    return {"d_sensor0_mean": float(d[:, 0].mean()), "d_min_mean": float(d.min(1).mean()),
            "frac_sensor0_is_nearest": float(np.mean(d[:, 0] == d.min(1)))}

if __name__ == "__main__":
    R = {r["cell_id"]: r for r in c.hc.rows()}
    todo = []
    for l in open(c.OUT / "task1_rows.jsonl"):
        o = json.loads(l); s = o["sel_af"]; h = o["held"][s]
        if h["lo99"] > 0.55: todo.append((o["cell"], s, "task1"))
    for x in json.load(open(c.HERE.parent / "W2-M/out/classification.json")):
        if x["set"] == "null" and x["class"].startswith("PLANT-SOLVED"):
            cid = [k for k in R if k.startswith(x["cell"]) and R[k]["env"]["family"] == "MAJ"][0]
            todo.append((cid, x["member"], "w2m"))
    fn = c.OUT / "dictnear.jsonl"
    fin = {json.loads(l)["cell"] for l in open(fn)} if fn.exists() else set()
    ck = c.Clock()
    for cid, mem, src in todo:
        if cid in fin: continue
        r = R[cid]; ph = Physics.from_dict(r["physics"]).validate(); env = envs.EnvSpec(**r["env"])
        held = c.held_seeds(r); g = genome(mem, ph)[1]
        e, d0, dn = c.batch_eval(ph, env, [(g, held, False), (g, held, True), (g, held, near_abl(ph))])
        o = {"cell": cid, "src": src, "member": mem, "acc": e["acc"], "lo99": e["lo99"], "DICT0": d0["acc"],
             "DICT_near": dn["acc"], "DICT_near_lo99": dn["lo99"], "DICT_near_hi99": dn["hi99"],
             "int_minus_dict0": c.pair_diff(e, d0), "int_minus_dict_near": c.pair_diff(e, dn), **prof(ph, env, held)}
        with open(fn, "a") as f: f.write(json.dumps(o) + "\n")
        print(cid[:8], src, mem, "acc %.3f lo %.3f D0 %.3f Dn %.3f  i-Dn lo %.3f  d0 %.2f dmin %.2f" % (
            e["acc"], e["lo99"], d0["acc"], dn["acc"], o["int_minus_dict_near"][1], o["d_sensor0_mean"], o["d_min_mean"]), flush=True)
    print(ck.done())
