"""Closure runs for blockers 1, 2 and majors 9-15: the author's version-three world two, its control, and my organisms."""
import sys, json, time
sys.dont_write_bytecode = True
sys.path.insert(0, "harness")
from rso_harness import ladder as L
import comp as C

t0 = time.time()
# (a) the author's table, re-run
sv = L.survey_pairs(300)
print("author's survey_pairs(300):")
for name, row in sv.items():
    print("  %-42s ninth %6.2f %-9s control %6.2f %-9s -> %s" % (name, row["ninth_pair"]["mean"], row["ninth_pair"]["answer"],
          row["control"]["mean"], row["control"]["answer"], row["answer"]))
rc = json.load(open("harness/RECEIPT_harness_v0.json"))
key = [k for k in rc if "pair" in k.lower()][0]
same = all(abs(sv[n]["ninth_pair"]["mean"] - rc[key]["survey"][n]["ninth_pair"]["mean"]) < 1e-12 and
           abs(sv[n]["control"]["mean"] - rc[key]["survey"][n]["control"]["mean"]) < 1e-12 for n in sv)
print("  equals the receipt section %r: %s" % (key, same))

# (b) my organisms under the author's run_pairs, both arms
def both(name, make, lives=300):
    a = L.certificate(L.run_pairs(make, lives)); b = L.certificate(L.run_pairs(make, lives, control=True))
    print("  %-70s ninth %6.2f %-9s control %6.2f %-9s -> %s" % (name[:70], a["mean"], a["answer"], b["mean"], b["answer"], L.pair_answer(a, b)))
    sys.stdout.flush()
print("my organisms (comp.py) under the author's run_pairs and its new control:")
for cls in (C.Elim, C.CacheRot, C.CacheXor, C.SameRow, C.SameCol, C.PairCompose, C.TripleBrute, C.Composer,
            C.OneTableOneRelabel, C.Hardwired22):
    both(cls.name, cls)
for m in (2, 3):
    both(C.PartialComposer(m).name, lambda m=m: C.PartialComposer(m))
both(C.CacheAffine.name + " (120 lives)", C.CacheAffine, 120)
print("elapsed %.0f s" % (time.time() - t0))
