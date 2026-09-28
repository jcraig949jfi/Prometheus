"""W4 probe (forensic, analytic, 1 core, seconds): would the trace-settable improver
rule P15 'entry finals := finals observed in the donor's solved OBSERVE families' transfer
to the donor's own TRANSFER families in the A19/C2 supply?  Reads frozen A19 artifacts
only; runs no search.  Output: w4_probe_finals.json"""
import json, random, sys, collections
from pathlib import Path
ENG = Path(__file__).resolve().parents[3] / "engine"
sys.path.insert(0, str(ENG))
import basis_v4 as G

rng = random.Random("W4/FINALS/v1")
TRIPLES = [(rng.randint(-30, 30), rng.randint(-9, 9) or 1, rng.randint(-9, 9) or 2)
           for _ in range(300)]

def fvec(final):
    out = []
    for acc, first, last in TRIPLES:
        env = {"acc": acc, "first": first, "last": last, "v": 0}
        try:
            r = eval(G._code(final), G._G, env)
        except Exception:
            r = None
        out.append(r)
    return tuple(out)

cls = {f: fvec(f) for f in G.FINAL_SPACE}
nclasses = len(set(cls.values()))
roles = json.load(open(ENG / "A19_C2" / "A18_ROLES_2026-09-28.json"))
donors = [json.loads(l) for l in open(ENG / "A19_C2" / "A18_DONORS_2026-09-28.jsonl")]
res = {"n_finals": len(G.FINAL_SPACE), "n_extensional_final_classes": nclasses, "rows": []}
agg = collections.Counter()
for d in donors:
    fams = {f["name"]: f for f in roles[d["catalog"].replace("CON", "CON/")]["families"]}
    obs = [fams[n] for n in d["observed_families"] if n in fams]
    tr = [f for f in fams.values() if f["role"] == "TRANSFER"]
    of = {f["final"] for f in obs}
    ofc = {cls[x] for x in of}
    va = [f for f in fams.values() if f["role"] == "VALIDATE"]
    agg["va"] += len(va); agg["va_ext"] += sum(cls[f["final"]] in ofc for f in va)
    exact = sum(f["final"] in of for f in tr)
    ext = sum(cls[f["final"]] in ofc for f in tr)
    kept = sum(1 for f in G.FINAL_SPACE if cls[f] in ofc)
    res["rows"].append({"arm": d["arm"], "catalog": d["catalog"], "n_obs_solved": len(obs),
                        "n_transfer": len(tr), "transfer_final_in_observed_exact": exact,
                        "transfer_final_in_observed_extensional": ext,
                        "entry_finals_kept_ext_closure": kept})
    agg["tr"] += len(tr); agg["exact"] += exact; agg["ext"] += ext
    agg["donors"] += 1; agg["kept"] += kept; agg["obs0"] += (len(obs) == 0)
res["aggregate"] = dict(agg)
res["aggregate"]["frac_transfer_final_covered_ext"] = round(agg["ext"] / agg["tr"], 3)
res["aggregate"]["frac_validate_final_covered_ext"] = round(agg["va_ext"] / agg["va"], 3)
res["aggregate"]["largest_final_class_sizes"] = sorted(collections.Counter(cls.values()).values(), reverse=True)[:6]
res["aggregate"]["mean_entry_finals_kept"] = round(agg["kept"] / agg["donors"], 1)
json.dump(res, open(Path(__file__).with_name("w4_probe_finals.json"), "w"), indent=1)
print(json.dumps(res["aggregate"]), "classes", nclasses)
