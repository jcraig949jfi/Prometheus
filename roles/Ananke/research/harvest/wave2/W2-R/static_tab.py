"""Cross-tab of static readout classes (rule-weighted) by noise x SIGNAL/NULL."""
from r_common import *
from static_cls import classify_genome
import collections
from scipy.stats import fisher_exact
E = [r for r in rows() if r["kind"] == "evolve"]
CL = ("LIN_COMM", "LIN_SENSE", "THRESH", "NONLIN", "NOINPUT")
recs = []
for r in E:
    ph, env = spec_of(r)
    c = classify_genome(ph, genome_of(r))
    w = collections.Counter()
    for p in c["rules"]:
        k = p["cls"]
        if k == "LINEAR":
            k = "LIN_COMM" if "comm" in p["kinds"] else "LIN_SENSE"
        w[k] += 1 / len(c["rules"])
    recs.append({"cell": r["cell_id"], "fam": r["env"]["family"], "noise": r["physics"]["noise"],
                 "SIG": bool(r["labels"]["SIGNAL"]), "w": dict(w), "rules": ph.rules, "setrule": ph.setrule,
                 "held": r["result"]["held"]["acc"]})
save("static_weighted.json", recs)
def table(sel, title):
    print(f"\n{title}")
    print(f"{'noise':>5} {'lab':>4} {'n':>4} " + " ".join(f"{c:>9}" for c in CL) + "   anyLINC  majLINC")
    for nz in (0, 16, 64):
        for lab in ("NULL", "SIG"):
            xs = [x for x in recs if sel(x) and x["noise"] == nz and x["SIG"] == (lab == "SIG")]
            if not xs:
                continue
            tot = {c: sum(x["w"].get(c, 0) for x in xs) / len(xs) for c in CL}
            anyl = sum(x["w"].get("LIN_COMM", 0) > 0 for x in xs)
            majl = sum(x["w"].get("LIN_COMM", 0) >= .5 for x in xs)
            print(f"{nz:5d} {lab:>4} {len(xs):4d} " + " ".join(f"{tot[c]:9.3f}" for c in CL) + f"   {anyl:4d}     {majl:4d}")
COMM = ("RELAY", "XOR", "MAJ", "FLIP")
table(lambda x: x["fam"] in COMM, "COMM families (RELAY/XOR/MAJ/FLIP), mean rule-weight per class")
for f in COMM + ("HOLD",):
    table(lambda x, f=f: x["fam"] == f, f)
# Fisher: NULL comm, majLINC at noise 64 vs noise 0; and NULL vs SIG at noise 0 (RELAY)
def cnt(sel):
    xs = [x for x in recs if sel(x)]
    a = sum(x["w"].get("LIN_COMM", 0) >= .5 for x in xs)
    return a, len(xs) - a
for nzh in (16, 64):
    a = cnt(lambda x: x["fam"] in COMM and not x["SIG"] and x["noise"] == nzh)
    b = cnt(lambda x: x["fam"] in COMM and not x["SIG"] and x["noise"] == 0)
    print(f"\nNULL comm majLINC noise{nzh} {a} vs noise0 {b}: OR, p =", fisher_exact([a, b]))
a = cnt(lambda x: x["fam"] in COMM and not x["SIG"] and x["noise"] > 0)
b = cnt(lambda x: x["fam"] in COMM and x["SIG"])
print("NULL comm noise>0", a, "vs SIG comm (all noise)", b, fisher_exact([a, b]))
a = cnt(lambda x: x["fam"] in COMM and not x["SIG"] and x["noise"] == 0)
print("NULL comm noise0", a, "vs SIG comm (all noise)", b, fisher_exact([a, b]))
