"""W2-Y task 3: re-score the C1 decay_shift transect levels (RELAY b0/b1 phys; FLIP b0 phys) with P-1's decay-robust
relay_refresh plant (harvest/wave2/P-1/decay_plant.py, imported read-only) on each row's OWN plant seeds
(world_seeds(H_int(search_seed, 0x9147), 32), campaign.py:299) and own physics, prog_len = max(L, 16).
KA: relay_flood at prog_len max(L,12) (exactly campaign.plant_viability) must reproduce the recorded plant acc.
Eager CPU, 2 threads, CUDA hidden (hp_common asserts)."""
import os, sys, pathlib, json, importlib.util
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"; os.environ["HP_THREADS"] = "2"; os.environ["OMP_NUM_THREADS"] = "2"
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-P"))
from w2p_common import np, envs, assays, hc, Physics, H_int, Clock  # noqa
from prometheus.ananke import plants
import torch
assert not torch.cuda.is_available()
spec = importlib.util.spec_from_file_location("p1dp", HERE.parent / "P-1" / "decay_plant.py")
src = (HERE.parent / "P-1" / "decay_plant.py").read_text()
# import only the plant definition (the module body runs an experiment at import): exec the function source
ns = {"plants": plants}
fsrc = src[src.index("def relay_refresh"):src.index("N_PER =")]
exec(fsrc, ns)
relay_refresh = ns["relay_refresh"]
ck = Clock()
fam_want = [("RELAY", 0), ("RELAY", 1), ("FLIP", 0)]
waves = sys.argv[1].split(",") if len(sys.argv) > 1 else ["B"]
out = []
for r in hc.rows():
    if r["wave"] not in waves or r["extra"]["transect"] != "decay_shift" or r["extra"]["track"] != "phys": continue
    if (r["env"]["family"], r["extra"]["base"]) not in fam_want: continue
    ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    seeds = assays.world_seeds(H_int(r["search_seed"], 0x9147), 32)
    o = {"cell": r["cell_id"], "wave": r["wave"], "family": env.family, "base": r["extra"]["base"],
         "li": r["extra"]["level_index"], "decay": ph.decay_shift, "rep": r["extra"].get("rep", 0),
         "recorded_flood": r["result"]["plant"]["acc"]}
    if o["rep"] == 0:
        p12 = ph.replace(prog_len=max(ph.prog_len, 12))
        o["ka_flood12"] = hc.evaluate(p12, plants.plant("relay_flood", p12), env, seeds)["acc"]
        o["ka_match"] = abs(o["ka_flood12"] - o["recorded_flood"]) < 1e-9
    p16 = ph.replace(prog_len=max(ph.prog_len, 16)).validate()
    a = hc.evaluate(p16, hc.bc(p16, relay_refresh(p16)), env, seeds)
    o["refresh"] = a["acc"]; o["refresh_lo99"] = a["lo99"]
    out.append(o); print(o, ck.done(), flush=True)
(HERE / "out" / f"task3_decay_{'_'.join(waves)}.json").write_text(json.dumps({"rows": out, "compute": ck.done()}, indent=1))
print(ck.done())
