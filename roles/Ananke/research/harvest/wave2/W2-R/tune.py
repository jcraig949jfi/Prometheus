"""Task 2: timing sweep of D/E-wave and top comm-family SIGNAL champions.
One change at a time: lat_base -1,+1,+2 (physics) and env delta -2,-1,+1,+2 (not HOLD: delta inert).
Discovery: 16 mirror pairs (32 fresh worlds), paired against native on the same seeds.
Confirmation: if the best variant gains >= .03, re-run best and native on a disjoint 16-pair set.
CPU budget guard: stop starting new champions when process CPU exceeds BUDGET core-seconds."""
from r_common import *
import dataclasses
import sys
BUDGET = float(sys.argv[1]) if len(sys.argv) > 1 else 950.0
START = int(sys.argv[2]) if len(sys.argv) > 2 else 0
OUTNAME = sys.argv[3] if len(sys.argv) > 3 else "tune.json"
ck = Clock()
R = rows()
sel, seen = [], set()
def add(r, tag):
    h = ghash(genome_of(r)) + str(r["physics"]["topo_seed"]) + str(r["env"])
    if h in seen:
        return False
    seen.add(h); sel.append((tag, r)); return True
for r in R:
    if r["wave"] == "D" and r["kind"] == "adjudicate": add(r, "D-adj")
for r in R:
    if r["wave"] == "E" and r["kind"] == "evolve": add(r, "E-evo")
for r in R:
    if r["wave"] == "D" and r["kind"] == "evolve" and r["labels"]["SIGNAL"]: add(r, "D-evo-SIG")
top = sorted([r for r in R if r["kind"] == "evolve" and r["labels"]["SIGNAL"] and r["env"]["family"] != "HOLD"
              and r["wave"] not in ("D", "E")], key=lambda r: -r["result"]["held"]["acc"])
n = 0
for r in top:
    if n >= 20: break
    n += add(r, "top20")
for r in R:
    if r["wave"] == "D" and r["kind"] == "evolve" and not r["labels"]["SIGNAL"]: add(r, "D-evo-NULL")
def pci(p):
    m, lo, hi = assays.pair_ci(np.asarray(p)); return [round(float(m), 4), round(float(lo), 4), round(float(hi), 4)]
out = []
for j, (tag, r) in enumerate(sel):
    if j < START:
        continue
    if time.process_time() - ck.t0 > BUDGET:
        print("BUDGET STOP at", j, flush=True); break
    ph, env = spec_of(r); G = genome_of(r)
    key = int(r["cell_id"][:8], 16)
    s1 = seeds(H_int(NS, 0x7E1, key), 32)
    s2 = seeds(H_int(NS, 0x7E2, key), 32)
    variants = {f"lat{d:+d}": (ph.replace(lat_base=ph.lat_base + d).validate(), env)
                for d in (-1, 1, 2) if ph.lat_base + d >= 0}
    if env.family != "HOLD":
        for d in (-2, -1, 1, 2):
            if env.delta + d >= 1:
                variants[f"delta{d:+d}"] = (ph, dataclasses.replace(env, delta=env.delta + d))
    pn = pairs(acc_only(ph, G, env, s1))
    rec = {"tag": tag, "cell": r["cell_id"], "parent": r["parent"], "fam": env.family, "noise": ph.noise,
           "lat_base": ph.lat_base, "delta": env.delta, "sync": ph.update_mode, "period": ph.update_period,
           "held": r["result"].get("held", {}).get("acc"), "native": pci(pn), "var": {}}
    for k, (p2, e2) in variants.items():
        pv = pairs(acc_only(p2, G, e2, s1))
        rec["var"][k] = {"acc": round(float(pv.mean()), 4), "gain": pci(pv - pn)}
    best = max(rec["var"], key=lambda k: rec["var"][k]["gain"][0])
    rec["best"] = best; rec["best_gain"] = rec["var"][best]["gain"][0]
    if rec["best_gain"] >= 0.03:
        p2, e2 = variants[best]
        qn = pairs(acc_only(ph, G, env, s2)); qv = pairs(acc_only(p2, G, e2, s2))
        rec["confirm"] = {"native": pci(qn), "best": pci(qv), "gain": pci(qv - qn)}
    rec["cpu_s"] = round(time.process_time() - ck.t0, 1)
    out.append(rec)
    print(j, tag, r["cell_id"][:8], env.family, "nat", rec["native"][0], "best", best, rec["best_gain"],
          "conf", rec.get("confirm", {}).get("gain"), "cpu", rec["cpu_s"], flush=True)
    save(OUTNAME, {"rows": out, "clock": ck.done(), "n_selected": len(sel)})
save(OUTNAME, {"rows": out, "clock": ck.done(), "n_selected": len(sel)})
print(ck.done())
