import sys, pathlib, json, collections
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "harness"))
from rso_harness import meta, audits, claims
from rso_harness.verdict import *
rows = meta.qualify()
tot_clean = sum(r["clean"] for r in rows.values()); tot_mut = sum(r["mutants"] for r in rows.values())
print("gates", len(rows), "clean", tot_clean, "mutants", tot_mut)
vc = collections.Counter(m["verdict"] for r in rows.values() for m in r["mutant_verdicts"])
print("verdicts", dict(vc))
ind_gates = sorted({g for g, r in rows.items() for m in r["mutant_verdicts"] if m["verdict"] == INDETERMINATE})
print("gates returning INDETERMINATE:", ind_gates)
esc = meta.known_escapes()
print("known escapes", len(esc), "distinct gates", len({e["gate"] for e in esc}), [e["gate"] for e in esc])
for g, r in rows.items():
    print("==", g, r["status"], "clean", r["clean"], "mutants", r["mutants"], "| false", r["false_alarms"], "esc", r["escapes"], "wrong", r["wrong_kind"])
    if g.startswith(("G9", "G10", "G11", "G12")):
        for m in r["mutant_verdicts"]:
            print("     %-13s %s\n         reason: %s" % (m["verdict"], m["mutant"], m["reason"][:300]))
