"""TASK 1: W2-M's MAJ plant family at the MAJ NULL evolve cells W2-W left UNDECIDED or never plant-scored
(excluding P_PROVEN). Protocol = W2-M score_rows.py:
 (1) select ONE in-genome-space member on 32 DEV worlds (namespace H(seed,0x57324D)). A priori menu =
     W2-M MENU (INT_CO, INT_1, INT_1A6, INT_1G, INT_2, INT_2A6) PLUS INT_LEAK (W2-M's post-hoc economy member;
     fixed here before any of these rows was seen, so it is a priori for this population). Both selections
     are recorded: sel_w2m (6-member menu) and sel_af (7-member menu).
 (2) score the selected member(s) on the row's own 64 HELD worlds (32 mirror pairs, C1 HELD_NS), with the
     must-fails DICT (only sensor 0 cued, same plant) and zero_comm.
 (3) if no in-space member reaches lo99 > .55: OVERRIDE check = INT_1 (one-hop) / INT_2 (multi-hop) with the
     genome fields raised to fit (prog_len, state_dim, payload_width), still <= 16 lines, held + DICT.
usage: python task1_maj.py START END   (resumable; appends to out/task1_rows.jsonl)"""
import sys, json, csv
import af_common as c
import numpy as np
import w2m_plants as wp
from score_rows import genome as w2m_genome, MENU
from prometheus.ananke import envs
from prometheus.ananke.physics import Physics
from prometheus.ananke.engine import Controls

MENU7 = list(MENU) + ["INT_LEAK"]

def genome(name, ph):
    if name == "INT_LEAK":
        ok = ph.prog_len >= 3
        return ph, wp.int_leak(ph), ok, 3
    return w2m_genome(name, ph)

def population():
    P = list(csv.DictReader(open(c.HERE.parent / "W2-W/null_placement.csv")))
    pop = [p for p in P if p["family"] == "MAJ" and p["final_class"] != "P_PROVEN"
           and (p["final_class"] == "UNDECIDED" or not p["w2m_class"])]
    # priority: never-scored UNDECIDED (69), W2-M-scored UNDECIDED (9), then never-scored inadmissible/other
    key = lambda p: (0 if p["final_class"] == "UNDECIDED" and not p["w2m_class"] else
                     1 if p["final_class"] == "UNDECIDED" else 2, p["cell"])
    return sorted(pop, key=key)

def score(r, prow, lc):
    ph = Physics.from_dict(r["physics"]).validate(); env = envs.EnvSpec(**r["env"])
    dev = c.dev_seeds(r); held = c.held_seeds(r)
    o = {"cell": r["cell_id"], "w2w_class": prow["final_class"], "w2m_scored": bool(prow["w2m_class"]),
         "admissible": prow["admissible"], "marginal": prow["w2t_marginal"], "placement": lc["placement"],
         "lc_bound": lc["lc_bound"], "topology": ph.topology, "update_mode": ph.update_mode,
         "cap": ph.cap, "collision": ph.collision, "economy": ph.economy_on,
         "genome_space": {k: getattr(ph, k) for k in ("prog_len", "state_dim", "payload_width")},
         "champ_held": r["result"]["held"]["acc"], "dev": {}}
    names, jobs = [], []
    for n in MENU7:
        _, g, ok, need = genome(n, ph)
        o["dev"][n] = {"fits": bool(ok), "lines": need}
        if ok:
            names.append(n); jobs.append((g, dev, False))
    res = c.batch_eval(ph, env, jobs)
    for n, e in zip(names, res):
        o["dev"][n]["acc"] = e["acc"]
    fit6 = [n for n in names if n != "INT_LEAK"]
    o["sel_w2m"] = max(fit6, key=lambda k: o["dev"][k]["acc"]) if fit6 else None
    o["sel_af"] = max(names, key=lambda k: o["dev"][k]["acc"])
    sels = [s for s in dict.fromkeys([o["sel_af"], o["sel_w2m"]]) if s]
    hj = []
    for s in sels:
        g = genome(s, ph)[1]; hj += [(g, held, False), (g, held, True)]
    hr = c.batch_eval(ph, env, hj)
    o["held"] = {}
    for i, s in enumerate(sels):
        e, d = hr[2 * i], hr[2 * i + 1]
        o["held"][s] = {"acc": e["acc"], "lo99": e["lo99"], "hi99": e["hi99"], "DICT": d["acc"],
                        "DICT_lo99": d["lo99"], "int_minus_dict": c.pair_diff(e, d)}
    z = c.batch_eval(ph, env, [(genome(o["sel_af"], ph)[1], held, False)], ctrl=Controls(zero_comm=True))[0]
    o["zero_comm_sel_af"] = z["acc"]
    if max(v["lo99"] for v in o["held"].values()) <= 0.55:
        on = "INT_1" if lc["placement"] == "one_hop" else "INT_2"
        ph2, g2, ok2, need = w2m_genome(on, ph)
        if not ok2 and ph2.prog_len <= 16:
            e, d = c.batch_eval(ph2.validate(), env, [(g2, held, False), (g2, held, True)])
            o["override"] = {"member": on, "lines": need, "acc": e["acc"], "lo99": e["lo99"], "DICT": d["acc"],
                             "int_minus_dict": c.pair_diff(e, d),
                             "raised": {k: getattr(ph2, k) for k in ("prog_len", "state_dim", "payload_width")}}
        elif ok2:
            o["override"] = {"member": on, "note": "fits in space; already in the dev menu"}
        else:
            o["override"] = {"member": on, "note": "needs > 16 lines"}
    return o

if __name__ == "__main__":
    a, b = int(sys.argv[1]), int(sys.argv[2])
    pop = population()
    lcs = {x["cell"]: x for x in json.load(open(c.HERE.parent / "W2-M/out/lc_maj.json"))["rows"]}
    R = {r["cell_id"]: r for r in c.hc.rows()}
    fn = c.OUT / "task1_rows.jsonl"
    done = set()
    if fn.exists():
        done = {json.loads(l)["cell"] for l in open(fn)}
    ck = c.Clock()
    for p in pop[a:b]:
        if p["cell"] in done: continue
        o = score(R[p["cell"]], p, lcs[p["cell"]])
        o["cpu_s_cum"] = ck.done()["cpu_s"]
        with open(fn, "a") as f: f.write(json.dumps(o) + "\n")
        best = max(o["held"].items(), key=lambda kv: kv[1]["lo99"])
        print(o["cell"][:8], o["placement"], o["topology"], "sel", o["sel_af"], "/", o["sel_w2m"],
              "held %.3f lo %.3f DICT %.3f dlo %.3f" % (best[1]["acc"], best[1]["lo99"], best[1]["DICT"], best[1]["int_minus_dict"][1]),
              "zc %.3f" % o["zero_comm_sel_af"], ("ovr %s" % {k: v for k, v in o["override"].items() if k in ("acc", "lo99", "note")}) if "override" in o else "",
              flush=True)
    print(ck.done())
