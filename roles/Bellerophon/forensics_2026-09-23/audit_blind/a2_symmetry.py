import json, collections
W=r"C:\Users\James\z80atlas_campaign_2026-09-19"
runs=[json.loads(l) for l in open(W+r"\runs.jsonl",encoding="utf-8")]
byf=collections.defaultdict(list)
for r in runs: byf[r["family"]].append(r)
vec_of={f:rs[0]["vec"] for f,rs in byf.items()}
by_vec={json.dumps(v,sort_keys=True):f for f,v in vec_of.items()}
def solved(rs): return any((r["summary"].get("solvers_tail") or 0)>=1 for r in rs)
ENDO={"ENDOGENOUS_COPY","ENDOGENOUS_PARTIAL","OVERWRITE","CONSTRUCTIVE","PAIR_EXECUTION"}
# forward / reverse counts, and with seeded inits excluded / only non-intervention runs
def cmp(axis, treat_pred, ctrl_level, filt=lambda r:True):
    fw=rv=both=neither=0
    for f,v in vec_of.items():
        if not treat_pred(v): continue
        g=by_vec.get(json.dumps(dict(v,**{axis:ctrl_level}),sort_keys=True))
        if not g: continue
        a=[r for r in byf[f] if filt(r)]; b=[r for r in byf[g] if filt(r)]
        if not a or not b: continue
        sa,sb=solved(a),solved(b)
        fw+=sa and not sb; rv+=sb and not sa; both+=sa and sb; neither+= (not sa and not sb)
    return dict(forward=fw,reverse=rv,both=both,neither=neither)
print("ENDO vs EXTERNAL (all runs)", cmp("reproduction", lambda v:v["reproduction"] in ENDO, "EXTERNAL"))
print("ENDO vs EXTERNAL (init RANDOM only)", cmp("reproduction", lambda v:v["reproduction"] in ENDO and v["init"]=="RANDOM", "EXTERNAL"))
print("ENDO vs EXTERNAL (no intervention runs)", cmp("reproduction", lambda v:v["reproduction"] in ENDO, "EXTERNAL", lambda r:r["kind"]!="intervention"))
print("INCR vs ATOMIC", cmp("scoring", lambda v:v["scoring"]=="INCREMENTAL","ATOMIC"))
print("RESERVOIR vs ISOLATED", cmp("spatial", lambda v:v["spatial"]=="RESERVOIR","NICHES_ISOLATED"))
# replicate agreement: families with >=2 runs, fraction where runs disagree on solved
dis=tot=0
for f,rs in byf.items():
    rs=[r for r in rs if r["kind"]!="intervention"]
    if len(rs)>=2:
        s=[(r["summary"].get("solvers_tail") or 0)>=1 for r in rs]; tot+=1; dis+= (any(s) and not all(s))
print("families>=2 runs: %d ; replicate disagreement on solved: %d (%.3f)"%(tot,dis,dis/tot))
# intervention runs mixed into families: how many families contain intervention runs AND non-intervention runs
mix=sum(1 for f,rs in byf.items() if any(r["kind"]=="intervention" for r in rs) and any(r["kind"]!="intervention" for r in rs))
print("families mixing intervention (init_tapes) runs with ordinary runs:",mix)
