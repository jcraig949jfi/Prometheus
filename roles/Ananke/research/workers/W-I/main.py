"""W-I main: reader-axis trajectories + twin physical profiles for the frozen set."""
import gzip, json, pathlib, sys, time
HERE = pathlib.Path(__file__).parent
REPO = HERE.resolve().parents[4]
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(HERE))
import numpy as np, torch
from prometheus.ananke import assays, c1b_run, lens
import traj

PANEL = "62a7fff9 35c721fd 72dd71d8 bbef66a1 e2afff1c e9196cae cd5b6fd6 31cd2a8a 4316f167 a02aa099 bf82cb29 dcd404a9 ed16c553 2dccdaa5 8c37f32e c16d5231 e06701a5 78f3b0ec 4ab2ba01 4781b0a1".split()
SPAN = "85ca202e ab089e45 7b7b025e 13127335 00c5d3b6 1c0a1bc7 65d840a8 0187372b 0a23398f 613162a3 63d17a90 369f5a5b 42716814".split()
import os
DEV = os.environ.get("WI_DEV", "cpu")
CHUNK = int(os.environ.get("WI_CHUNK", "16"))
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)


def full_ids():
    ids = {}
    with gzip.open(REPO / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt") as f:
        for l in f:
            r = json.loads(l)
            if r["kind"] == "evolve":
                ids[r["cell_id"][:8]] = r["cell_id"]
    return ids


def one(cid, seeds):
    ph, env, g, row = c1b_run.load(cid)
    Pd = env.period()
    ro_off = (env.cue_len + env.gap) if env.family == "HOLD" else env.delta
    offs = list(range(-1, ro_off))
    names = traj.arm_names(ph)
    arms = [("normal", None, 0)] + [(f"{n}@{o}", traj.ARMS[n], o) for o in offs for n in names]
    t = time.time()
    ep, pt, trs = traj.run_arms(ph, g, env, seeds, arms, chunk=CHUNK, device=DEV)
    trials = range(1, env.trials)
    nrm = traj.pair_acc(pt["normal"], ep, trials)
    res = {"cell": cid, "wave": row["wave"], "family": env.family, "phys_digest": ph.digest(),
           "physics": ph.to_dict(), "env": env.to_dict(), "arms": names, "ro_off": ro_off,
           "cue_len": env.cue_len, "normal": lens.ci(nrm), "offsets": {}}
    sc = ep.scored.copy(); sc[:, 0] = False
    base_ok = (pt["normal"] == 1.0) & sc
    for o in offs:
        d = {}
        for n in names:
            lab = f"{n}@{o}"
            p = traj.pair_acc(pt[lab], ep, trials)
            d[n] = {"acc": lens.ci(p), "verdict": lens.swap_verdict(nrm, p),
                    "arm_identical": bool(np.array_equal(trs[lab], trs["normal"]))}
        xs = (pt[f"site_all@{o}"] < 1.0)[base_ok].astype(float)
        yc = (pt[f"channel_all@{o}"] < 1.0)[base_ok].astype(float)
        phi = float(np.corrcoef(xs, yc)[0, 1]) if xs.std() > 0 and yc.std() > 0 else None
        d["phi"] = phi
        res["offsets"][o] = d
    res["reader_s"] = time.time() - t
    t = time.time()
    res["twin"] = traj.twin_profile(ph, g, env, 0x5EE ^ 0x7, device=DEV)
    res["twin_s"] = time.time() - t
    return res


if __name__ == "__main__":
    torch.set_num_threads(2)
    ids = full_ids()
    seeds = assays.world_seeds(0x5EE, 64)
    todo = [ids[c] for c in PANEL + SPAN]
    for cid in todo:
        f = OUT / f"traj_{cid[:8]}.json"
        lk = OUT / f"traj_{cid[:8]}.lock"
        if f.exists():
            continue
        try:
            os.close(os.open(lk, os.O_CREAT | os.O_EXCL))
        except FileExistsError:
            continue
        r = one(cid, seeds)
        f.write_text(json.dumps(r, default=float))
        lk.unlink()
        print(cid[:8], r["family"], "normal", [round(x, 3) for x in r["normal"]],
              "reader_s", round(r["reader_s"], 1), "twin_s", round(r["twin_s"], 1), flush=True)
