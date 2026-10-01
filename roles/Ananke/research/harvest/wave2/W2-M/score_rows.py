"""Score the MAJ integration plant family at C1 MAJ evolve rows' EXACT physics, eager CPU.
Per row: (1) select ONE in-genome-space member on 32 DEV worlds (namespace H(seed,0x57324D)), a priori menu
INT_CO, INT_1, INT_1A6, INT_1G, INT_2, INT_2A6 (only members that fit prog_len/state_dim/payload_width);
(2) score the selected member on the row's own 64 HELD worlds (C1 HELD_NS) with controls zero_comm and DICT
(only sensor 0 cued: same plant, single-sensor input) and the FIRST (first-arrival) readout plant;
(3) SIGNAL rows: re-evaluate the C1 champion on the same held worlds for a paired plant-champion CI, and the
champion under DICT. (4) multi-hop rows where INT_2 does not fit: INT_2 with genome override, flagged.
usage: python score_rows.py signal|null   (null: menu by placement, 4 members; no FIRST readout, to fit the cap)"""
import sys
import numpy as np
import w2m_common as c, w2m_plants as wp
from prometheus.ananke import envs, assays
from prometheus.ananke.engine import Controls
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int
import json

MENU = {"INT_CO": None, "INT_1": dict(lanes=1), "INT_1A6": dict(lanes=1, reset="age", k=6),
        "INT_1G": dict(lanes=1, gated=True), "INT_2": dict(lanes=2), "INT_2A6": dict(lanes=2, reset="age", k=6)}

def genome(name, ph):
    if name == "INT_CO":
        return ph, wp.int_co(ph), True, 6
    if name == "FIRST":
        ok = ph.prog_len >= 9 and ph.state_dim >= 2
        ph2 = ph if ok else ph.replace(prog_len=max(ph.prog_len, 9), state_dim=max(ph.state_dim, 2))
        return ph2, wp.first(ph2), ok, 9
    return wp.member(ph, **MENU[name])

def pairs_ci(p):
    m, lo, hi = assays.pair_ci(np.asarray(p)); return float(m), float(lo), float(hi)

NULL_MENU = {"one_hop": ("INT_CO", "INT_1", "INT_1A6", "INT_1G"), "multi": ("INT_CO", "INT_1", "INT_2", "INT_2A6")}

def score(r, lc, light=False):
    ph = Physics.from_dict(r["physics"]).validate(); env = envs.EnvSpec(**r["env"])
    dev = assays.world_seeds(H_int(r["search_seed"], 0x57324D), 32)
    held = c.held_seeds(r, 64)
    out = {"cell": r["cell_id"], "wave": r["wave"], "SIGNAL": r["labels"]["SIGNAL"],
           "champ_held": r["result"]["held"]["acc"], "champ_lo99": r["result"]["held"]["lo99"],
           "placement": lc["placement"], "lc_bound": lc["lc_bound"], "m_hist": lc["m_hist"],
           "genome_space": {k: ph.to_dict()[k] for k in ("prog_len", "state_dim", "payload_width", "channels")},
           "dev": {}}
    menu = MENU if not light else NULL_MENU["one_hop" if lc["placement"] == "one_hop" else "multi"]
    for name in menu:
        ph2, g, ok, n = genome(name, ph)
        if not ok:
            out["dev"][name] = {"fits": False, "lines": n}; continue
        e = c.hc.evaluate(ph2, g, env, dev)
        out["dev"][name] = {"fits": True, "lines": n, "acc": e["acc"]}
    best = max((k for k, v in out["dev"].items() if v["fits"]), key=lambda k: out["dev"][k]["acc"])
    out["selected"] = best
    ph2, g, ok, n = genome(best, ph)
    e = c.hc.evaluate(ph2, g, env, held)
    ez = c.hc.evaluate(ph2, g, env, held, ctrl=Controls(zero_comm=True))
    ed = c.hc.evaluate(ph2, g, env, held, sched_fn=wp.dict_sched)
    out["held"] = {"acc": e["acc"], "lo99": e["lo99"], "hi99": e["hi99"], "pairs": e["pairs"]}
    out["zero_comm"] = {"acc": ez["acc"], "lo99": ez["lo99"], "hi99": ez["hi99"]}
    out["DICT"] = {"acc": ed["acc"], "lo99": ed["lo99"], "hi99": ed["hi99"]}
    out["int_minus_dict"] = pairs_ci(np.array(e["pairs"]) - np.array(ed["pairs"]))
    if not light:
        phf, gf, okf, _ = genome("FIRST", ph)
        ef = c.hc.evaluate(phf, gf, env, held)
        out["FIRST"] = {"acc": ef["acc"], "lo99": ef["lo99"], "hi99": ef["hi99"], "in_space": okf}
    if lc["placement"] != "one_hop" and not genome("INT_2", ph)[2]:
        pho, go, _, n2 = genome("INT_2", ph)
        eo = c.hc.evaluate(pho, go, env, held)
        out["INT_2_override"] = {"acc": eo["acc"], "lo99": eo["lo99"], "hi99": eo["hi99"],
                                 "override": {k: pho.to_dict()[k] for k in ("prog_len", "state_dim", "payload_width")}}
    if r["labels"]["SIGNAL"]:
        champ = np.asarray(r["result"]["champion"])[None][0]
        ec = c.hc.evaluate(ph, champ, env, held)
        ecd = c.hc.evaluate(ph, champ, env, held, sched_fn=wp.dict_sched)
        out["champ_cpu"] = {"acc": ec["acc"], "lo99": ec["lo99"], "matches_record": abs(ec["acc"] - r["result"]["held"]["acc"]) < 1e-9}
        out["champ_DICT"] = {"acc": ecd["acc"], "lo99": ecd["lo99"], "hi99": ecd["hi99"]}
        out["plant_minus_champ"] = pairs_ci(np.array(e["pairs"]) - np.array(ec["pairs"]))
        out["dictplant_minus_champ"] = pairs_ci(np.array(ed["pairs"]) - np.array(ec["pairs"]))
    return out

if __name__ == "__main__":
    which = sys.argv[1]
    lcs = {o["cell"]: o for o in json.load(open(c.OUT / "lc_maj.json"))["rows"]}
    rows = c.maj_rows()
    if which == "signal":
        sel = [r for r in rows if r["labels"]["SIGNAL"]]
    else:
        g = np.random.default_rng(0x57324D)
        nulls = [r for r in rows if not r["labels"]["SIGNAL"]]
        one = [r for r in nulls if lcs[r["cell_id"]]["placement"] == "one_hop"]
        mul = [r for r in nulls if lcs[r["cell_id"]]["placement"] != "one_hop"]
        sel = [one[i] for i in sorted(g.choice(len(one), 15, replace=False))] + \
              [mul[i] for i in sorted(g.choice(len(mul), 15, replace=False))]
    ck = c.Clock(); res = []
    for r in sel:
        o = score(r, lcs[r["cell_id"]], light=(which != "signal")); res.append(o)
        print(o["cell"][:8], o["placement"], "lc %.3f" % o["lc_bound"], "sel", o["selected"],
              "held %.3f lo %.3f" % (o["held"]["acc"], o["held"]["lo99"]), "zc %.3f" % o["zero_comm"]["acc"],
              "DICT %.3f" % o["DICT"]["acc"], ("FIRST %.3f" % o["FIRST"]["acc"]) if "FIRST" in o else "",
              "champ %.3f/%.3f" % (o["champ_held"], o["champ_lo99"]),
              ("ovr %.3f" % o["INT_2_override"]["acc"]) if "INT_2_override" in o else "",
              ("p-c [%.3f,%.3f]" % o["plant_minus_champ"][1:]) if "plant_minus_champ" in o else "", flush=True)
        c.save(f"score_{which}.json", {"rows": res, "compute": ck.done()})
    print(ck.done())
