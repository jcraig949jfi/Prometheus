from drv import *
from collections import Counter
rows = meta.qualify()
MINE = ["G1.cell","G1.receipt","G2.preflight","G3.exclusion","G4.entry","G5.neutrality","G6.observer","G6.reset","G6.restart","G7.calibration","G7.report","G8.demand"]
tot_clean = sum(r["clean"] for r in rows.values()); tot_mut = sum(r["mutants"] for r in rows.values())
print("gates", len(rows), "clean", tot_clean, "mutants", tot_mut)
c = Counter(m["verdict"] for r in rows.values() for m in r["mutant_verdicts"])
print("verdicts", dict(c))
esc = meta.known_escapes()
print("escapes", len(esc), Counter(e["gate"] for e in esc))
for gid, r in rows.items():
    print("%-16s status=%s clean=%d mutants=%d fa=%s esc=%s wk=%s" % (gid, r["status"], r["clean"], r["mutants"], r["false_alarms"], r["escapes"], r["wrong_kind"]))
ind = sorted({gid for gid, r in rows.items() for m in r["mutant_verdicts"] if m["verdict"] == INDETERMINATE})
print("gates returning INDETERMINATE:", ind)
print()
for gid in MINE:
    print("=====", gid)
    for m in rows[gid]["mutant_verdicts"]:
        print("  [%s] %s\n       -> %s" % (m["verdict"], m["mutant"], m["reason"]))
