"""Must-fail: KA-AND (max_plant) with an INCOMPLETE component list (Msum omitted),
full cube, no identity assumption. Expect identity < .99 and NO decisive set;
positive control: the complete list on the same slice finds {S, Msum}."""
import json
import numpy as np, torch
import common
import tt, ana, run_ka
torch.set_num_threads(2)
res = {}
ph, g = run_ka.fixture("max")
for label, drop in (("complete", ()), ("drop_Msum", ("Msum",))):
    comps = {k: v for k, v in tt.coarse_components(ph).items() if k not in drop}
    names = list(comps)
    subs = tt.all_subsets(len(names))
    r, ep = tt.run_table(ph, g, run_ka.HOLD, run_ka.SEEDS, 3, [5], comps, subs)
    yA, yB = ep.y[0::2, 3], ep.y[1::2, 3]
    ident = ana.identity_rate(r[5], subs)
    dd, el = ana.direct_decisive(r[5], subs, yA, yB)
    dd = [d for d, e in zip(dd, el) if e]
    found = [None if d is None else [[names[i] for i in s] for s in d] for d in dd]
    n_none = sum(d is None for d in found)
    top = {}
    for d in found:
        top[str(d)] = top.get(str(d), 0) + 1
    res[label] = {"names": names, "identity": ident, "eligible": len(found), "no_decisive": n_none, "decisive_sets": top}
    print(label, names, "identity", round(ident, 3), "eligible", len(found), "NO-DECISIVE", n_none, top, flush=True)
json.dump(res, open(common.HERE / "out/ka_mustfail.json", "w"), indent=1)
