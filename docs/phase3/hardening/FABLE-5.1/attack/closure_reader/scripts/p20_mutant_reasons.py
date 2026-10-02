"""Every registered mutant with its verdict and reason, to check that it is rejected for the reason its name says."""
from drv import *

rows = meta.qualify()
n = 0
for gid, r in rows.items():
    print("== %s  status %s  sound %d  mutants %d" % (gid, r["status"], r["clean"], r["mutants"]))
    for m in r["mutant_verdicts"]:
        n += 1
        print("   %-13s %-78s | %s" % (m["verdict"], m["mutant"][:78], m["reason"][:200]))
print("mutants:", n)
print()
for e in meta.known_escapes():
    print("ESCAPE %-15s %-5s %s" % (e["gate"], e["verdict"], e["fault"]))
    if "shown" in e:
        print("        shown:", e["shown"])
