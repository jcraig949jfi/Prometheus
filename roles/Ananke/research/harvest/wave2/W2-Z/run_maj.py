"""MAJ economy rows: economy-cheap integrators. Member chosen on 16 DEV worlds (namespace W2ZD), then scored on the
row's own 64 HELD worlds with must-fail controls zero_comm and DICT (only sensor 0 cued; W2-M dict_sched)."""
import sys, json
sys.path.insert(0, '.')
import wz_common as wz
np = wz.np
sys.path.insert(0, str(wz.HERE.parent / "W2-M"))
from prometheus.ananke import plants
A = plants.assemble
DEV_NS = 0x57325A44


def dict_sched(ep):
    sv = ep.schedule.sense_val
    sv[:, :, 1:] = 0


MEMBERS = {
    # 3 lines (W2-M INT_LEAK): forgetting left to physics decay
    "LEAK3": [("MULQ", "EMIT", "SENSE", "SENSE", 0), ("MOV", "PAY0", "SENSE", 0, 0), ("ADD", "S0", "S0", "IN0_0", 0)],
    # 4 lines: own leak S0 := S0>>1 + IN (works without physics decay)
    "LEAK4s1": [("MULQ", "EMIT", "SENSE", "SENSE", 0), ("MOV", "PAY0", "SENSE", 0, 0),
                ("SHR", "T0", "S0", 1, 0), ("ADD", "S0", "T0", "IN0_0", 0)],
    "LEAK4s2": [("MULQ", "EMIT", "SENSE", "SENSE", 0), ("MOV", "PAY0", "SENSE", 0, 0),
                ("SHR", "T0", "S0", 2, 0), ("ADD", "S0", "T0", "IN0_0", 0)],
    # 5 lines: S0 := S0 - S0>>2 + IN (gentler own leak)
    "LEAK5": [("MULQ", "EMIT", "SENSE", "SENSE", 0), ("MOV", "PAY0", "SENSE", 0, 0),
              ("SHR", "T0", "S0", 2, 0), ("SUB", "S0", "S0", "T0", 0), ("ADD", "S0", "S0", "IN0_0", 0)],
}


def genome(ph, name):
    b = A(ph, MEMBERS[name])
    return np.broadcast_to(b, (ph.rules, *b.shape)).copy()


rows = sys.argv[1].split(",")
tag = sys.argv[2]
res = {}
clk = wz.Clock()
for c in rows:
    r = wz.row(c); ph, env = wz.cell(r)
    dev = wz.assays.world_seeds(wz.H_int(r["search_seed"], DEV_NS), 16)
    devs = {}
    for nm in MEMBERS:
        if len(MEMBERS[nm]) > ph.prog_len:
            continue
        devs[nm] = wz.hc.evaluate(ph, genome(ph, nm), env, dev)["acc"]
    best = max(devs, key=devs.get)
    held = wz.held(r, 64)
    g = genome(ph, best)
    e = wz.hc.evaluate(ph, g, env, held)
    passed = e["lo99"] > 0.55
    ez = wz.hc.evaluate(ph, g, env, held[:16], ctrl=wz.Controls(zero_comm=True)) if passed else {"acc": None}
    ed = wz.hc.evaluate(ph, g, env, held, sched_fn=dict_sched) if passed else {"acc": None, "hi99": None, "pairs": e["pairs"]}
    eo = {"acc": None, "lo99": None}
    st = wz.run_stats(ph, g, env, held[:4])
    o = {"dev": {k: round(v, 3) for k, v in devs.items()}, "member": best, "lines": len(MEMBERS[best]),
         "acc": e["acc"], "lo99": e["lo99"], "hi99": e["hi99"], "zero_comm": ez["acc"], "DICT": ed["acc"], "DICT_hi99": ed["hi99"],
         "econ_off": eo["acc"], "econ_off_lo99": eo["lo99"],
         "emit_per_awake": st["emitters"] / max(1, st["awake"]),
         "champ_held": r["result"]["held"].get("acc"),
         "pairs_minus_dict": None}
    d = np.array(e["pairs"]) - np.array(ed["pairs"])
    m, lo, hi = wz.assays.pair_ci(d)
    o["plant_minus_DICT"] = [round(float(lo), 3), round(float(hi), 3)]
    res[r["cell_id"]] = o
    print(r["cell_id"][:8], best, "acc %.3f [%.3f]" % (e["acc"], e["lo99"]), "zc", ez["acc"], "DICT", ed["acc"],
          "p-D", o["plant_minus_DICT"], "emit/awake %.3f" % o["emit_per_awake"], "dev", o["dev"], flush=True)
res["_clock"] = clk.done(); print(res["_clock"])
wz.save(f"maj_{tag}.json", res)
