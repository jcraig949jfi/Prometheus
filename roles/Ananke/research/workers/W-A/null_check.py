"""Post-hoc (labelled): discriminating power of the frozen rules. Null
predictor = the champion's measured BASE curve, unchanged."""
import json
import numpy as np
import conditions as C
from evaluate import interval, iv_holds

eng = json.loads((C.HERE / "out/engine.json").read_text())
G = C.GAPS
m = lambda k: {g: eng[k][str(g)][0] for g in G}
tests = [k for k in eng if not k.startswith(("base:", "canon"))]
good = 0
for k in tests:
    c = k.split(":")[1]
    b, x = m(f"base:{c}"), m(k)
    mae = np.mean([abs(b[g] - x[g]) for g in G])
    ok = mae <= 0.07 and iv_holds(interval(x), interval(b))
    good += ok
print(f"null (base curve) passes {good}/{len(tests)}")
same = [k for k in eng if k.startswith("pr0:")]
print("pr0 curves identical to canon:uniform:",
      {k: all(eng[k][str(g)] == eng["canon:uniform"][str(g)] for g in G) for k in same})
print("canon:specimen identical to base:4ab2ba01:",
      all(eng["canon:specimen"][str(g)] == eng["base:4ab2ba01"][str(g)] for g in G))
