"""W-V known-answer checks (PLAN s4) on out/raw_pmaj, raw_pdict. python ka.py -> out/ka.json"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ana

INF_OFFS = (2, 4, 6)
res = {}
pm = ana.summarize("pmaj")
pd = ana.summarize("pdict")
pm_perm = ana.summarize("pmaj", permute_votes=True)


def strata(out, offs, labs=("q0", "q1")):
    return {k: t for k, t in out["strata"].items() if t.get("o") in offs and t.get("lab") in labs}


def informative(st):
    return {k: t for k, t in st.items() if t["class"][0] not in ("UNDEFINED", "NOT-INFORMATIVE")}


# KA-MAJ
s = informative(strata(pm, INF_OFFS))
res["KA-MAJ"] = {"classes": {k: t["class"] for k, t in s.items()},
                 "pass": bool(s) and all(t["class"][0] == "MAJORITY" for t in s.values()),
                 "verdict": ana.verdict(pm, offsets=INF_OFFS)[0]}
# KA-DICT
s = informative(strata(pd, INF_OFFS))
res["KA-DICT"] = {"classes": {k: t["class"] for k, t in s.items()},
                  "pass": bool(s) and all(t["class"] == ["DICTATOR", [4]] for t in s.values()),
                  "verdict": ana.verdict(pd, offsets=INF_OFFS)[0]}
# MF1: PDICT non-carrying sensors show no effect
s = strata(pd, INF_OFFS)
mf1 = {k: [t[f"s{j}"]["hi"] for j in range(4)] for k, t in s.items() if t["n"] >= ana.MIN_ELIGIBLE}
res["MF1"] = {"s0-s3 ci_hi": mf1, "pass": bool(mf1) and all(max(v) <= 0.05 for v in mf1.values())}
# MF2: PDICT never reads MAJORITY anywhere
res["MF2"] = {"pass": all(t["class"][0] != "MAJORITY" for t in pd["strata"].values())}
# MF3: PMAJ with permuted pivot labels must not read MAJORITY (D point < .5)
s = informative(strata(pm_perm, INF_OFFS))
res["MF3"] = {"D": {k: t["piv"]["D"] for k, t in s.items()}, "classes": {k: t["class"] for k, t in s.items()},
              "pass": bool(s) and all(t["class"][0] != "MAJORITY" and t["piv"]["D"] < 0.5 for t in s.values())}
# MF4: o12 not informative in both plants
mf4 = {f"{nm}:{k}": t["class"][0] for nm, out in (("pmaj", pm), ("pdict", pd))
       for k, t in strata(out, (12,), ("q0", "q1", "pooled")).items()}
res["MF4"] = {"classes": mf4, "pass": all(c in ("NOT-INFORMATIVE", "UNDEFINED") for c in mf4.values())}
res["ALL_PASS"] = all(v["pass"] for v in res.values() if isinstance(v, dict) and "pass" in v)
(HERE / "out" / "ka.json").write_text(json.dumps(res, indent=1, default=float))
print(json.dumps(res, indent=1, default=float))
