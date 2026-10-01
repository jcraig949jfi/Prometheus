"""TASK 1: joint ceilings for every XOR and FLIP evolve row + known-answer + falsification checks.
python task1_xor_flip.py  -> out/task1_xor_flip.json"""
import glob, json
from w2u_ceil import *            # noqa: F401,F403
from w2p_common import Clock, held_seeds
import attain as A

NS = 0x57325555   # "W2UU" fresh-seed namespace
WORLDS = 128
ck = Clock()
R = hc.rows()
H = HERE.parent.parent / "H-PLANT"
W2L = HERE.parent / "W2-L"
lcmap = {o["cell"]: o for o in json.load(open(H / "out/lc_census.json"))["rows"]}
E = [r for r in R if r["kind"] == "evolve" and r["env"]["family"] in ("XOR", "FLIP")]
res = {"ka": {}, "rows": [], "plants": []}

# ---- KA1: async terms OFF reproduces H-PLANT lc_census (SCORE_NS, M=64) exactly, all XOR+FLIP evolve rows
ka1 = []
for r in E:
    ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    c = ceilings(ph, env, assays.world_seeds(hc.SCORE_NS, 64), terms=())
    b = lcmap[r["cell_id"]]["bound"]
    ka1.append({"cell": r["cell_id"][:8], "fam": env.family, "hplant": b, "lc": c["lc"], "joint_off": c["joint"],
                "joint_block_off": c.get("joint_block"),
                "exact": abs(c["lc"] - b) < 1e-12 and abs(c["joint"] - b) < 1e-12
                and (c.get("joint_block") is None or abs(c["joint_block"] - b) < 1e-12)})
res["ka"]["hplant_lc_census_terms_off"] = {"n": len(ka1), "exact": sum(o["exact"] for o in ka1),
                                          "nontrivial(<1)": sum(o["hplant"] < 1 for o in ka1),
                                          "fails": [o for o in ka1 if not o["exact"]]}
print("KA1", res["ka"]["hplant_lc_census_terms_off"]["exact"], "/", len(ka1), flush=True)

# ---- KA2: H-PLANT M=256 lightcone file
ka2 = []
for o in json.load(open(H / "out/lightcone_d64656f2_1b26026f_6f82f9c7_fac4aaa2.json")):
    ph = Physics.from_dict(o["physics"]); env = envs.EnvSpec(**o["env"])
    c = ceilings(ph, env, assays.world_seeds(hc.SCORE_NS, 256), terms=())
    ka2.append((o["cell"][:8], env.family, o["acc_upper_bound"], c["lc"], abs(c["lc"] - o["acc_upper_bound"]) < 1e-12))
res["ka"]["hplant_lightcone_M256"] = ka2
print("KA2", ka2, flush=True)

# ---- KA3: RELAY through my code reproduces W2-P joint (fresh W2-P seeds, 128 worlds)
w2p = {o["cell"]: o for o in json.load(open(HERE.parent / "W2-P/out/task2_timing.json"))["rows"]}
from w2p_common import fresh_seeds as w2p_fresh
rel = [r for r in R if r["kind"] == "evolve" and r["env"]["family"] == "RELAY"]
ka3 = []
for r in rel[::12] + [r for r in rel if r["physics"]["update_mode"] == "async"][:8]:
    ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    c = ceilings(ph, env, w2p_fresh(r, 128))
    q = w2p[r["cell_id"]]
    ka3.append((r["cell_id"][:8], ph.update_mode, q["ceil_joint"], c["joint"], abs(q["ceil_joint"] - c["joint"]) < 1e-9))
res["ka"]["w2p_relay_joint"] = {"n": len(ka3), "exact": sum(x[4] for x in ka3), "rows": ka3}
print("KA3", sum(x[4] for x in ka3), "/", len(ka3), flush=True)

# ---- KA4: closed forms. async p, cl=2, single sensor never late: RELAY cue-only 1-.5(1-p)^2 ...
#      FLIP block-2 async p=.5 at zero transport: P(M)=(.75)^2=.5625 (checked in REPORT by hand)

# ---- main table
thr = {}
for i, r in enumerate(E):
    ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    seeds = assays.world_seeds(H_int(NS, int(r["cell_id"][:8], 16)), WORLDS)
    c = ceilings(ph, env, seeds)
    ch = ceilings(ph, env, held_seeds(r))
    K = c["n_trials"] // (WORLDS // 2)
    P = r["search"]["M_held"] // 2
    if (P, K) not in thr:
        thr[(P, K)] = A.min_true_to_cross(0.55, P, K, "lo_gt", 0.5)
    held = r["result"]["held"]
    o = {"cell": r["cell_id"], "wave": r["wave"], "family": env.family, "topology": ph.topology,
         "update_mode": ph.update_mode, "update_period": ph.update_period, "update_p": ph.update_p,
         "d": env.d, "delta": env.delta, "block": env.block, "lat_base": ph.lat_base, "lat_hop": ph.lat_hop,
         "held_acc": held["acc"], "held_lo99": held["lo99"], "SIGNAL": bool(r["labels"]["SIGNAL"]),
         "K_scored": K, "signal_attainable": thr[(P, K)], "hplant_lc": lcmap[r["cell_id"]]["bound"],
         "ceil": c, "ceil_heldset": ch}
    res["rows"].append(o)
    if i % 40 == 0:
        print(i, len(E), ck.done(), flush=True)

# ---- falsification: plants must not exceed their ceilings
def plant_row(label, ph, env, seeds, acc, lo99, src):
    c = ceilings(ph, env, seeds)
    key = "joint_block" if env.family == "FLIP" else "joint"
    res["plants"].append({"label": label, "src": src, "family": env.family, "mode": ph.update_mode,
                          "acc": acc, "lo99": lo99, "ceil": c,
                          "violates(lo99>ceil_strict)": lo99 > c["joint"] + 1e-9,
                          "exceeds_block_ceiling(lo99>)": lo99 > c[key] + 1e-9})

for f in ["xor_score.json", "xor_score_cell_4eeca9f10c514f08.json", "xor_score_cell_literal_aa2b8d6805a15ec6.json"]:
    o = json.load(open(H / "out" / f))
    plant_row("H-PLANT " + f, Physics.from_dict(o["physics"]), envs.EnvSpec(**o["env"]),
              assays.world_seeds(hc.SCORE_NS, 256), o["normal"]["acc"], o["normal"]["lo99"], f)
for f in ["flip_score.json", "mh_score.json"]:
    for lab, o in json.load(open(H / "out" / f))["results"].items():
        plant_row("H-PLANT " + lab, Physics.from_dict(o["physics"]), envs.EnvSpec(**o["env"]),
                  assays.world_seeds(hc.SCORE_NS, 256), o["normal"]["acc"], o["normal"]["lo99"], f)
# W2-L: every FLIP program reading >= .55 (base M64, refresh M32, thin/full M64), on the seeds it used
seen = set()
for pat, M in [("t1_base_M64_*of4.json", 64), ("t1_refresh_M32_*of4.json", 32)] + \
              [(pathlib.Path(p).name, None) for p in glob.glob(str(W2L / "out/t4_full_*.json"))]:
    for fn in glob.glob(str(W2L / "out" / pat)):
        for o in json.load(open(fn))["rows"]:
            if o["acc"] < 0.55:
                continue
            r = hc.row(o["cell"])
            ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
            MM = M or o["M"]
            plant_row(f"W2-L {o.get('variant')} {o['cell'][:8]}", ph, env, held_seeds(r)[:MM],
                      o["acc"], o["lo99"], pathlib.Path(fn).name)
lat = json.load(open(W2L / "out/t5_relay_latch_d9cc.json"))
res["w2l_latch_raw"] = str(lat)[:400]
res["compute"] = ck.done()
save("task1_xor_flip.json", res)
print("plants:", [(p["label"], round(p["acc"], 3), round(p["lo99"], 3), round(p["ceil"]["joint"], 3),
                   round(p["ceil"].get("joint_block", p["ceil"]["joint"]), 3)) for p in res["plants"]])
print(ck.done())
