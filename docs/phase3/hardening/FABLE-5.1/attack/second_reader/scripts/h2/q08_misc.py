import sys, pathlib, json, collections
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "harness"))
from rso_harness import meta, audits, claims, torture, retain1, rulers, search
from rso_harness.verdict import *
CF = meta.COUNTERFEIT
R = retain1
r2, r3 = meta.run2(), meta.run3()
print("######## G9.arms on every cell of runs 2 and 3 (the documents quote BUILDER of run 2 and STRATEGIST of run 3 only)")
for tag, cells, arms in (("run 2", r2, meta.ARMS2), ("run 3", r3, meta.ARMS3)):
    for c in cells:
        a = audits.audit_arms(cells[c]["replicates"], arms)
        print("   %s %-11s steps said %-4s | G9.arms %-4s %s" % (tag, c, cells[c]["verdict"], a.verdict, a.reason[:150]))
print("######## G9.sham on every cell of runs 2 and 3")
t2, t3 = audits.clause_table(r2, audits.clauses_run2), audits.clause_table(r3, audits.clauses_run3)
for tag, cells, t in (("run 2", r2, t2), ("run 3", r3, t3)):
    for c in cells:
        a = audits.audit_sham(cells[c]["replicates"], t["NESTING.sham_harmless"])
        print("   %s %-11s G9.sham %-12s %s" % (tag, c, a.verdict, a.reason[:110]))
print("######## run 2 clause table: which clauses fail by themselves")
a2 = audits.audit_clauses(r2, audits.clauses_run2)
names = list(a2.detail["table"])
iso = [c for c in names if c not in a2.detail["cannot_fail"] and c not in a2.detail["not_isolated"]]
print("   cannot_fail:", a2.detail["cannot_fail"]); print("   not_isolated:", a2.detail["not_isolated"]); print("   isolated:", iso)
for c in names:
    print("      %-42s %s" % (c, a2.detail["table"][c]))
a3 = audits.audit_clauses(r3, audits.clauses_run3)
iso3 = [c for c in a3.detail["table"] if c not in a3.detail["cannot_fail"] and c not in a3.detail["not_isolated"]]
print("   run 3: cannot_fail", len(a3.detail["cannot_fail"]), "not_isolated", len(a3.detail["not_isolated"]), "isolated", iso3)
print("######## known escapes: is each fault real? (the registry carries 'shown' for three of eleven)")
esc = meta.known_escapes()
for e in esc:
    print("   %-15s verdict %-5s shown: %s" % (e["gate"], e["verdict"], "yes" if "shown" in e else "NO"))
print("   G6.observer: the rare observer on a seed that was not checked ->", torture.observer_equivalence(R.Register, [987654], torture.rare_observer(meta.PAIRS)).verdict)
chem = {"CHEMISTRY": (meta.relabel(R.Register, "CHEMISTRY"), meta.relabel(R.RegisterImpostor, "CHEMISTRY"))}
print("   G4.entry relabelled:", meta.entry("CHEMISTRY", chem).verdict, "| the unrelabelled case:", meta.entry("CHEMISTRY", {"CHEMISTRY": (R.Register, R.RegisterImpostor)}).verdict)
print("   G10.setting 'as appropriate':", audits.audit_setting(dict(meta.SETTING_OK, cost="as appropriate")).verdict)
print("######## counts")
rows = meta.qualify()
own_runs = [(g, m["mutant"]) for g, r in rows.items() for m in r["mutant_verdicts"]
            if any(w in m["mutant"] for w in ("run 1", "run 2", "run 3", "nothing registered has been built"))]
print("   registered 'mutants' that are the author's own runs or rows of the unbuilt list, not planted faults: %d" % len(own_runs))
for g, m in own_runs:
    print("      %-13s %s" % (g, m))
print("   RUNS rows:", len(audits.RUNS), "| verdict rows in the four receipts: run1 organisms", 4, "(5 target verdicts), run2 cells", len(r2), ", run3 cells", len(r3),
      ", keys verdicts", len(json.loads((CF / audits.KEYS).read_text())["verdicts"]))
print("   receipt rows not in RUNS:")
used = {(src[0], src[2]) for _, _, src, _ in audits.RUNS}
g1 = json.loads((CF / audits.G1).read_text())
for k, v in g1["result"]["v01_verdict"].items():
    if (audits.G1, k) not in used: print("      run 1  %-12s %s" % (k, v))
for k in r2:
    if (audits.G2, k) not in used: print("      run 2  %-12s %s" % (k, r2[k]["verdict"]))
for k in r3:
    if (audits.G3, k) not in used: print("      run 3  %-12s %s" % (k, r3[k]["verdict"]))
for k, v in json.loads((CF / audits.KEYS).read_text())["verdicts"].items():
    if (audits.KEYS, k) not in used: print("      keys   %-58s %s" % (k, v))
print("######## first version against current: mutant names carried over")
sys.path.insert(0, str(HERE / "attack" / "first_version"))
for m in [k for k in list(sys.modules) if k.startswith("rso_harness")]:
    del sys.modules[m]
sys.path.remove(str(HERE / "harness"))
from rso_harness import meta as meta1
meta1.COUNTERFEIT = CF
rows1 = meta1.qualify()
old = {(g, m["mutant"]) for g, r in rows1.items() for m in r["mutant_verdicts"]}
new = {(g, m["mutant"]) for g, r in rows.items() for m in r["mutant_verdicts"]}
print("   first version: %d mutants, %d clean; current: %d mutants; names carried over unchanged: %d" % (
    len(old), sum(r["clean"] for r in rows1.values()), len(new), len(old & new)))
