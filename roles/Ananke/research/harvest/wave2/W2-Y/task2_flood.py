"""W2-Y task 2: flood ceilings (flood_ceil.py) for the RELAY/MAJ accuracy-verdict transects, plus known-answer checks.
CPU only, 2 threads; no engine runs (numpy MC on envs.build placements)."""
import sys, pathlib, json
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-P"))
from w2p_common import np, envs, assays, hc, Physics, H_int, Clock, held_seeds  # noqa
import task2_timing as T2
import flood_ceil as FC
OUT = HERE / "out"
ck = Clock()
mode = sys.argv[1] if len(sys.argv) > 1 else "all"
res = {}
if mode in ("ka", "all"):
    ka = []
    R0 = [r for r in hc.rows() if r["wave"] == "B" and r["env"]["family"] in ("RELAY", "MAJ")
          and r["physics"]["topology"] != "global" and r["physics"]["update_mode"] == "sync"
          and r["physics"]["dest_mode"] == "all" and r["extra"].get("rep", 0) == 0][::7][:10]
    for r in R0:
        ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
        sd = assays.world_seeds(H_int(r["search_seed"], 0x9147), 8)
        f = FC.ceilings(ph, env, sd, R=2, opts=dict(loss=False, jitter=False, dup=False), envs=envs)
        l = T2.ceilings(ph, env, sd)["lc"]
        ka.append((r["cell_id"][:8], env.family, ph.topology, round(f, 6), round(l, 6), abs(f - l) < 1e-9))
    print("KA1 flood(no loss/jitter/dup) == T2 lc:", sum(x[-1] for x in ka), "/", len(ka), ka, flush=True)
    ph = Physics(topology="global", n_sites=64, update_mode="sync", update_period=1, lat_base=3, lat_hop=0,
                 lat_jitter=0, loss=0.1, dup=0.0, fanout=4, dest_mode="sample").validate()
    rs = np.random.default_rng(1)
    got = FC.flood_P(ph, [0], 5, 0, 4, 2, rs, R=20000)[:, 0].mean()  # emits at h=0,1 arrive 3,4; relays too late
    th = 1 - (1 - 0.9 / 63) ** (4 * 2)
    print("KA2 global one-round closed form:", round(float(got), 4), "vs", round(th, 4), flush=True)
    res["ka1"] = ka; res["ka2"] = [float(got), th]
if mode in ("rows", "all"):
    want = {("RELAY", "delta"), ("RELAY", "decay_shift"), ("RELAY", "economy"), ("MAJ", "topology"), ("MAJ", "economy")}
    out = []
    for r in hc.rows():
        if r["wave"] not in ("B", "B2"): continue
        if (r["env"]["family"], r["extra"]["transect"]) not in want: continue
        # decay/economy levels share every transport dial -> flood ceiling identical across levels; level 0 only
        if r["extra"]["transect"] in ("decay_shift", "economy") and r["extra"]["level_index"] != 0: continue
        if r["env"]["family"] == "MAJ" and (r["extra"]["track"] != "phys" or r["extra"]["base"] != 1): continue
        ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
        o = {"cell": r["cell_id"], "wave": r["wave"], "kind": r["kind"], "family": env.family, "dial": r["extra"]["transect"],
             "base": r["extra"]["base"], "track": r["extra"]["track"], "li": r["extra"]["level_index"]}
        ps = assays.world_seeds(H_int(r["search_seed"], 0x9147), 32)
        o["flood_plant"] = FC.ceilings(ph, env, ps, R=32, seed=int(r["cell_id"][:8], 16), envs=envs)
        if r["kind"] == "evolve":
            o["flood_held"] = FC.ceilings(ph, env, held_seeds(r), R=16, seed=int(r["cell_id"][8:16], 16), envs=envs)
        out.append(o)
        if len(out) % 10 == 0:
            print(len(out), ck.done(), flush=True)
            (OUT / "task2_flood_partial.json").write_text(json.dumps(out))
    res["rows"] = out
res["compute"] = ck.done()
(OUT / f"task2_flood_{mode}.json").write_text(json.dumps(res, indent=1))
print(ck.done())
